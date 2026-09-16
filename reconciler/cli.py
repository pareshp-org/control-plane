"""reconciler.cli - the Phase-1 CLI: `list` and `run` (spec 53.1, 0.5).

`list` prints every registered comparator id, one per line, sorted, and
exits non-zero if any registered id has no declared fail-mode class
(L3-P1-19; spec 64.2: "Unclassified controls fail CI").

`run` executes comparators against a fixture (or, with --live, a real
GitHub organisation - never exercised by any acceptance command in
lanes/L3-06-tasks.md) and prints the spec-0.5 deterministic summary:

    <STATUS> <id> findings=<int> compared=<int>      (one per comparator)
    CANARY <found|missing|n/a>                         (run-level, last)

Exit codes (spec 0.5): 0 = executed, no Blocking findings. 2 = executed,
at least one Blocking finding. 3 = run FAILED (instrument failure,
canary missing). Any other non-zero is a crash - a STOP, not a status
this module tries to normalise away.

This file grows in place as later Phase-1 tasks land: L3-P1-16 adds the
per-registry comparison-count floor, L3-P1-17 wires the seeded canary
and the zero-findings FAIL rule, L3-P1-19 wires the fail-closed matrix
for a comparator that raises. Each addition is called out at its call
site below rather than silently folded in early.
"""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

import reconciler.comparators as _comparators_pkg
from reconciler.canary import assert_canary
from reconciler.model import DriftClass, Finding
from reconciler.orphans import load_context as _load_orphan_context
from reconciler.orphans import run_group as _run_orphan_group
from reconciler.orphans.prospective import detect as _detect_prospective_orphans
from reconciler.orphans.types import GROUPS as _ORPHAN_GROUPS
from reconciler.registry import COMPARATORS, FAIL_CLASS
from reconciler.runrecord import RunRecord, narrowed_comparators
from reconciler.state.fixture_adapter import FixtureState
from reconciler.state.live_adapter import LiveState

FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def _load_comparators() -> None:
    """Import every module under reconciler/comparators/ so its
    @comparator registration runs. Idempotent - re-importing an
    already-imported module is a cheap no-op for importlib."""
    for info in pkgutil.iter_modules(_comparators_pkg.__path__):
        importlib.import_module(f"reconciler.comparators.{info.name}")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class DeclaredState:
    """The declared/** half of one fixture, loaded once per run.

    Holds exactly the documents the Phase-1 comparator set needs:
    people.yaml, platform.yaml, os-health.yaml, every products/*.yaml,
    and the fixture's canary.yaml (spec: the seeded-canary rule).
    Nothing here is fetched from the network - declared state is always
    local control-plane content (spec 0.4).
    """

    def __init__(self, fixture_name: str, fixtures_root: Path | None = None):
        self.fixture_name = fixture_name
        root = (fixtures_root or FIXTURES_ROOT) / fixture_name
        declared_root = root / "declared"
        self.people: list[dict[str, Any]] = _load_yaml(declared_root / "people.yaml").get("people", [])
        self.platform: dict[str, Any] = _load_yaml(declared_root / "platform.yaml")
        self.os_health: dict[str, Any] = _load_yaml(declared_root / "os-health.yaml")
        self.products: dict[str, dict[str, Any]] = {}
        products_dir = declared_root / "products"
        if products_dir.is_dir():
            for path in sorted(products_dir.glob("*.yaml")):
                self.products[path.stem] = _load_yaml(path)
        canary_path = root / "canary.yaml"
        self.canary: dict[str, Any] | None = (
            _load_yaml(canary_path).get("canary") if canary_path.is_file() else None
        )


def _parse_as_of(value: str | None) -> date:
    if value is None:
        return datetime.now(timezone.utc).date()
    return date.fromisoformat(value)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cmd_list(args: argparse.Namespace) -> int:
    _load_comparators()
    undeclared = sorted(set(COMPARATORS) - set(FAIL_CLASS))
    if undeclared:
        # L3-P1-19 / spec 64.2: "Unclassified controls fail CI."
        print(f"undeclared fail-mode class for: {', '.join(undeclared)}", file=sys.stderr)
        return 1
    for comparator_id in sorted(COMPARATORS):
        print(comparator_id)
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    _load_comparators()
    as_of = _parse_as_of(args.as_of)

    if args.live:
        actual: Any = LiveState(args.org or "", live=True)
        declared = DeclaredState(args.fixture) if args.fixture else None
    else:
        if not args.fixture:
            print("error: --fixture is required unless --live is given", file=sys.stderr)
            return 1
        declared = DeclaredState(args.fixture)
        actual = FixtureState(args.fixture)

    only = list(args.only) if args.only else None
    if only:
        unknown = [c for c in only if c not in COMPARATORS]
        if unknown:
            print(f"error: unknown comparator id(s): {', '.join(unknown)}", file=sys.stderr)
            return 1
        ids_to_run = only
    else:
        ids_to_run = sorted(COMPARATORS)

    all_findings: list[Finding] = []
    comparison_counts: dict[str, int] = {}
    summary_body: list[str] = []
    any_module_failed = False
    for comparator_id in ids_to_run:
        try:
            findings, compared = COMPARATORS[comparator_id](declared, actual, as_of)
            findings = list(findings)
            module_status = "OK"
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see reconciler.failmode
            # L3-P1-19: a comparator that cannot execute never fails
            # silently - its own declared class decides whether that
            # failure is Blocking (fail closed) or a visible Amber
            # alert (fail open), spec 64.2.
            import dataclasses

            from reconciler.failmode import on_comparator_error

            drift_class = FAIL_CLASS.get(comparator_id, DriftClass.BLOCKING)
            failure_finding = dataclasses.replace(
                on_comparator_error(comparator_id, drift_class, exc),
                first_seen=f"{as_of.isoformat()}T00:00:00Z",
            )
            findings = [failure_finding]
            compared = 0
            module_status = "FAIL"
            any_module_failed = True
        all_findings.extend(findings)
        comparison_counts[comparator_id] = int(compared)
        summary_body.append(f"{module_status} {comparator_id} findings={len(findings)} compared={compared}")

    # `--only` suppresses the canary-missing rule (spec 0.5) once the
    # canary exists. Until L3-P1-17 registers the `display_name`
    # comparator there is no canary concept at all, so every run's line
    # is "missing" regardless of `--only` (spec 0.5's own note on this).
    canary_registered = "display_name" in COMPARATORS
    canary_found = canary_registered and assert_canary(all_findings)

    if only:
        canary_line = "CANARY n/a" if canary_registered else "CANARY missing"
    else:
        canary_line = "CANARY found" if canary_found else "CANARY missing"

    # L3-P1-16: a full run whose actual count for any comparator falls
    # below its expected minimum is FAILED - a silently narrowed
    # comparison is itself visible drift (spec 53.1). `--only` runs are
    # inherently narrowed by design and are exempt (spec 0.5).
    narrowed = [] if only else narrowed_comparators(comparison_counts)

    # L3-P1-17 / AT-102: a full run with no findings at all, or one
    # that is missing the seeded canary, is FAILED - "a reconciler that
    # finds nothing is assumed broken, never assumed clean." Only
    # applies once the canary is registered and only to full runs.
    zero_findings_fail = canary_registered and not only and (not all_findings or not canary_found)

    # `--only` runs never see status FAILED / exit 3 (spec 0.5: "the
    # exit code is 0 or 2 only - never 3. The 3 = FAILED rule applies
    # exclusively to full (non---only) runs"), even if the one
    # comparator it ran crashed - a crash there still surfaces as a
    # Blocking (or Amber) finding via failmode, so it is not silent.
    run_status = "FAILED" if (not only and (narrowed or zero_findings_fail or any_module_failed)) else "OK"

    any_blocking = any(f.drift_class == DriftClass.BLOCKING for f in all_findings)
    exit_code = 3 if run_status == "FAILED" else (2 if any_blocking else 0)

    if args.format == "json":
        record = RunRecord(
            run_id=str(uuid.uuid4()),
            started_at=_now_iso(),
            finished_at=_now_iso(),
            status=run_status,
            findings=all_findings,
            comparison_counts=comparison_counts,
            canary_found=canary_found,
            external_cause=None,
        )
        print(json.dumps(record.to_dict(), indent=2, default=str))

    if args.summary:
        for line in summary_body:
            print(line)
        print(canary_line)

    return exit_code


def _cmd_orphans(args: argparse.Namespace) -> int:
    """`orphans` - the L3-P2 sixteen-type orphan detector (spec §12.2).

    Independent of `run`/`list`: it reads fixture-a's declared/**
    orphan-relevant documents (reconciler.orphans.load_context), never
    a comparator, and never --live (no task in this cluster wires it).

    Exit codes: a normal (non-prospective) invocation follows the
    general spec 0.5 rule - 2 if any Blocking-severity orphan is
    present, 0 otherwise. `--prospective` always exits 0 (L3-P2-05: a
    transfer worklist describing a future state never blocks).
    """
    as_of = _parse_as_of(args.as_of)
    ctx = _load_orphan_context(args.fixture, as_of)

    if args.prospective:
        findings, compared = _detect_prospective_orphans(ctx)
        label = "orphans.prospective"
        exit_code = 0
    else:
        if not args.group:
            print("error: --group is required unless --prospective is given", file=sys.stderr)
            return 1
        findings, compared = _run_orphan_group(args.group, ctx)
        label = f"orphans.{args.group}"
        any_blocking = any(f.orphan_severity == "Blocking" for f in findings)
        exit_code = 2 if any_blocking else 0

    if args.summary:
        print(f"OK {label} findings={len(findings)} compared={compared}")

    return exit_code


def _cmd_repair_classes(args: argparse.Namespace) -> int:
    # L3-P6-02: the Phase 6 repair enablement registry, printed sorted
    # by class id so the output is deterministic regardless of dict
    # insertion order.
    from reconciler.repair.enablement import REPAIR_CLASSES

    enabled_count = 0
    for class_id in sorted(REPAIR_CLASSES):
        repair_class = REPAIR_CLASSES[class_id]
        print(f"CLASS {class_id} enabled={'true' if repair_class.enabled else 'false'}")
        if repair_class.enabled:
            enabled_count += 1
    print(f"REPAIR_CLASSES total={len(REPAIR_CLASSES)} enabled={enabled_count}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m reconciler.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="print every registered comparator id, sorted")
    p_list.set_defaults(func=_cmd_list)

    p_run = sub.add_parser("run", help="execute comparators against a fixture or --live org")
    p_run.add_argument("--fixture", default=None)
    p_run.add_argument("--only", action="append", default=None)
    p_run.add_argument("--as-of", dest="as_of", default=None)
    p_run.add_argument("--summary", action="store_true")
    p_run.add_argument("--format", choices=["json"], default=None)
    p_run.add_argument("--live", action="store_true")
    p_run.add_argument("--org", default=None)
    p_run.set_defaults(func=_cmd_run)

    p_orphans = sub.add_parser("orphans", help="run the sixteen-type orphan detectors against a fixture (spec §12.2)")
    p_orphans.add_argument("--fixture", required=True)
    p_orphans.add_argument("--group", choices=sorted(_ORPHAN_GROUPS), default=None)
    p_orphans.add_argument("--as-of", dest="as_of", default=None)
    p_orphans.add_argument("--prospective", action="store_true")
    p_orphans.add_argument("--summary", action="store_true")
    p_orphans.set_defaults(func=_cmd_orphans)

    p_repair_classes = sub.add_parser(
        "repair-classes", help="print the Phase 6 repair-class enablement registry (spec 99.6 risk 6)"
    )
    p_repair_classes.add_argument("--summary", action="store_true")
    p_repair_classes.set_defaults(func=_cmd_repair_classes)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
