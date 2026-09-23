#!/usr/bin/env python3
"""reconcile_publisher - execute reconciler and publish Prometheus node-exporter metrics.

Spec Section 53.1 & Subsystem M:
Executes reconciler against declared vs actual state, extracts findings by severity
(blocking, amber, green, degrading, warning, advisory) and canary status (canary_found),
and emits atomic Prometheus textfile metrics for node-exporter.

Exit codes per spec 0.5:
  0 = clean (no blocking findings, canary found)
  2 = executed, at least one blocking finding present
  3 = run failed (canary missing, comparison narrowed, or instrument crash)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run reconciler and publish Prometheus metrics text for node-exporter."
    )
    parser.add_argument(
        "--fixture",
        default=os.environ.get("RECONCILER_FIXTURE", "fixture-a"),
        help="Fixture name to reconcile against (default: fixture-a or RECONCILER_FIXTURE)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=os.environ.get("RECONCILER_LIVE", "").lower() in ("1", "true", "yes"),
        help="Reconcile against live GitHub organisation instead of fixture",
    )
    parser.add_argument(
        "--org",
        default=os.environ.get("RECONCILER_ORG", os.environ.get("ORG", None)),
        help="GitHub organisation name when running --live",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        help="Date string YYYY-MM-DD for temporal evaluations",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help="Run only specific comparator id(s)",
    )
    parser.add_argument(
        "--prom-file",
        default=os.environ.get("RECONCILER_PROM_FILE"),
        help="Target Prometheus metric file path (default: $RECONCILER_PROM_DIR/reconciler.prom)",
    )
    parser.add_argument(
        "--prom-dir",
        default=os.environ.get("RECONCILER_PROM_DIR", "/var/lib/prometheus/node-exporter"),
        help="Prometheus textfile collector directory (default: /var/lib/prometheus/node-exporter)",
    )
    parser.add_argument(
        "positional_mode",
        nargs="?",
        default=None,
        help="Positional run mode, e.g. 'full' (ignored for CLI flags compatibility)",
    )
    return parser.parse_args(argv)


def resolve_prom_file(args: argparse.Namespace) -> Path:
    if args.prom_file:
        return Path(args.prom_file)
    return Path(args.prom_dir) / "reconciler.prom"


def run_reconciler_cli(
    args: argparse.Namespace,
    control_plane_root: Path,
) -> tuple[int, dict[str, Any] | None, str, str]:
    """Execute python -m reconciler.cli run with appropriate flags."""
    cli_args = ["run", "--format", "json"]

    if args.live:
        cli_args.append("--live")
        if args.org:
            cli_args.extend(["--org", args.org])
    else:
        cli_args.extend(["--fixture", args.fixture])

    if args.as_of:
        cli_args.extend(["--as-of", args.as_of])

    if args.only:
        for cid in args.only:
            cli_args.extend(["--only", cid])

    cmd = [sys.executable, "-m", "reconciler.cli"] + cli_args

    env = dict(os.environ)
    cp_str = str(control_plane_root)
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{cp_str}{os.pathsep}{existing_pp}" if existing_pp else cp_str

    proc = subprocess.run(
        cmd,
        cwd=control_plane_root,
        env=env,
        capture_output=True,
        text=True,
    )

    record: dict[str, Any] | None = None
    if proc.stdout:
        try:
            record = json.loads(proc.stdout)
        except json.JSONDecodeError:
            # Output was not pure JSON (or was empty)
            pass

    return proc.returncode, record, proc.stdout, proc.stderr


def extract_metrics(
    record: dict[str, Any] | None,
    rc: int,
    existing_prom_file: Path | None = None,
) -> tuple[str, dict[str, int], int]:
    """Extract finding counts by severity, canary detection status, and format Prometheus text."""
    canary_found = 0
    findings: list[dict[str, Any]] = []

    if record is not None:
        canary_found = 1 if record.get("canary_found") else 0
        findings = record.get("findings", [])

    counts = {
        "blocking": 0,
        "amber": 0,
        "green": 0,
        "degrading": 0,
        "warning": 0,
        "advisory": 0,
    }

    for f in findings:
        dc = str(f.get("drift_class") or "").strip().lower()
        sev = str(f.get("severity") or "").strip().lower()
        lvl = f.get("level")

        if dc == "blocking" or sev in ("blocking", "block") or lvl == 4:
            counts["blocking"] += 1
        elif dc == "red" or sev in ("red", "degrading") or lvl == 5:
            counts["degrading"] += 1
        elif dc == "amber" or sev in ("amber", "warning") or lvl in (2, 3):
            counts["amber"] += 1
            counts["warning"] += 1
        elif dc == "green" or sev in ("green", "advisory") or lvl == 1:
            counts["green"] += 1
            counts["advisory"] += 1

    lines = [
        "# HELP reconciler_drift_count Number of active drift findings by severity",
        "# TYPE reconciler_drift_count gauge",
        f'reconciler_drift_count{{severity="blocking"}} {counts["blocking"]}',
        f'reconciler_drift_count{{severity="amber"}} {counts["amber"]}',
        f'reconciler_drift_count{{severity="green"}} {counts["green"]}',
        f'reconciler_drift_count{{severity="degrading"}} {counts["degrading"]}',
        f'reconciler_drift_count{{severity="warning"}} {counts["warning"]}',
        f'reconciler_drift_count{{severity="advisory"}} {counts["advisory"]}',
        "# HELP reconciler_canary_detected Seeded canary detected in reconciliation run",
        "# TYPE reconciler_canary_detected gauge",
        f"reconciler_canary_detected {canary_found}",
    ]

    last_success_ts: int | None = None
    if rc in (0, 2):
        last_success_ts = int(time.time())
    elif existing_prom_file and existing_prom_file.is_file():
        # Preserve previous timestamp if this run failed (canary missing / error)
        try:
            content = existing_prom_file.read_text(encoding="utf-8")
            m = re.search(
                r'ops_vm_job_last_success_timestamp\{job_name="reconcile"\}\s+(\d+)',
                content,
            )
            if m:
                last_success_ts = int(m.group(1))
        except Exception:
            pass

    if last_success_ts is not None:
        lines.extend([
            '# HELP ops_vm_job_last_success_timestamp Unix timestamp of last successful reconciliation run',
            '# TYPE ops_vm_job_last_success_timestamp gauge',
            f'ops_vm_job_last_success_timestamp{{job_name="reconcile"}} {last_success_ts}',
        ])

    return "\n".join(lines) + "\n", counts, canary_found


def write_atomic(target: Path, content: str) -> None:
    """Atomically write Prometheus metrics text to prevent partial reads by node-exporter."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.parent / f"{target.name}.{os.getpid()}.tmp"
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(target)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    script_dir = Path(__file__).resolve().parent
    control_plane_root = script_dir.parent.parent

    prom_path = resolve_prom_file(args)

    rc, record, stdout, stderr = run_reconciler_cli(args, control_plane_root)

    # Print any stderr from reconciler CLI
    if stderr:
        sys.stderr.write(stderr)

    # Generate and write Prometheus metrics
    prom_text, counts, canary_found = extract_metrics(record, rc, prom_path)
    try:
        write_atomic(prom_path, prom_text)
    except Exception as e:
        sys.stderr.write(f"reconcile_publisher: ERROR writing metrics to {prom_path}: {e}\n")
        return 3

    # Summary log to stdout
    total_findings = sum(counts.values())
    status_label = "CLEAN" if rc == 0 else ("BLOCKING_DRIFT" if rc == 2 else "FAILED")
    print(
        f"RECONCILE: status={status_label} exit={rc} canary={canary_found} "
        f"findings={total_findings} (blocking={counts['blocking']} amber={counts['amber']} green={counts['green']}) "
        f"prom={prom_path}"
    )

    # Enforce exit code contract per spec:
    # 0 = clean, 2 = blocking drift present, 3 = run failed (canary missing/error)
    if rc == 0:
        return 0
    elif rc == 2:
        return 2
    else:
        return 3


if __name__ == "__main__":
    sys.exit(main())
