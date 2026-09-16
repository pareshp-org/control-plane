"""R-INV-03 -- a file under ``registries/`` absent from the owner manifest
and from the tooling exemption list (Section 52.6).

Standalone, directly-tested rule function -- see ``r_inv_01.py``'s module
docstring for why this is not wired into the frozen Option B (FD-094)
``R01``..``R18`` dispatch table, and why the literal CLI-grammar /
``discover()`` lines of this task's SELF-VERIFY block in
``lanes/L1-05-tasks.md`` are superseded by that decision.

``R-INV-02`` is not allocated here -- it belongs to L1-902's invariant-
classification rule; that id is deliberately left free.

Reconciliation is two-directional, matching the task's own fixture table
(``unlisted_registry_file`` and ``two_unlisted`` exercise one direction;
``listed_but_absent`` exercises the other):

1. Every real file under ``registries/`` must match either an
   ``owners.artifacts[].path`` entry (literal or glob) or an
   ``inventory.tooling_exempt`` glob.
2. Every *literal* (non-glob) ``registries/``-scoped
   ``owners.artifacts[].path`` entry must name a file that actually
   exists. Glob entries (e.g. ``registries/services/*/service.yaml``)
   and non-``registries/`` entries (e.g. ``product.yaml``, ``records/``,
   prose rows like ``"Constitution file"``) are not files this module can
   resolve against this repository's ``registries/`` tree, so they are
   not checked here.

``registries/OWNERS.yaml`` and ``registries/INVENTORY.yaml`` themselves
are the manifest and this rule's own configuration -- they are never
compared against direction 1, the same way a mirror does not reflect
itself. (``tooling_exempt`` exists for everything else that plays the
same "describes the inventory, is not inventoried" role -- see the
``valid/tooling_files_exempt`` fixture.)

Both directions are silent (no findings) when ``owners_doc`` is absent
-- "owners absent from ctx.docs" (matching R-INV-01 and R-SVC-01).
"""
from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

RULE_ID = "R-INV-03"
SPEC = "Section 52.6"
APPLIES_TO = ["owners", "inventory"]

_SELF_FILES = {"registries/OWNERS.yaml", "registries/INVENTORY.yaml"}


def _message(path):
    return (
        f"R-INV-03 registries/{path} is a control-plane artifact absent from "
        f"the owner manifest; Section 52.6 requires a new artifact to state "
        f"which existing file cannot hold it"
    )


def _absent_message(path):
    return (
        f"R-INV-03 registries/{path} is a control-plane artifact absent from "
        f"the owner manifest; Section 52.6 requires a new artifact to state "
        f"which existing file cannot hold it (listed in registries/OWNERS.yaml, "
        f"but no such file exists)"
    )


def _matches_any(path, patterns):
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def check_document(owners_doc, inventory_doc, actual_paths, source="registries"):
    """Check one already-parsed ``(owners.yaml, inventory.yaml)`` pair
    against ``actual_paths``, the set of file paths actually present
    under ``registries/`` (each already in the ``registries/<rest>``
    form used by ``owners.artifacts[].path``, and excluding
    ``registries/OWNERS.yaml`` / ``registries/INVENTORY.yaml``
    themselves).

    Returns ``(passed, findings)``.
    """
    if not isinstance(owners_doc, dict):
        return True, []

    artifact_paths = [
        a.get("path")
        for a in (owners_doc.get("artifacts") or [])
        if isinstance(a, dict) and a.get("path")
    ]
    exempt = list((inventory_doc or {}).get("tooling_exempt") or [])
    actual = sorted(set(actual_paths) - _SELF_FILES)

    findings = []

    # Direction 1: every real registries/ file must be covered by the
    # manifest (literal or glob) or by the tooling exemption list.
    for path in actual:
        if _matches_any(path, artifact_paths) or _matches_any(path, exempt):
            continue
        findings.append(_message(path[len("registries/"):] if path.startswith("registries/") else path))

    # Direction 2: a literal (non-glob) registries/-scoped manifest entry
    # must name a file that exists.
    actual_set = set(actual)
    for artifact_path in artifact_paths:
        if not artifact_path.startswith("registries/"):
            continue
        if "*" in artifact_path or "?" in artifact_path:
            continue
        if artifact_path in _SELF_FILES:
            continue
        if artifact_path not in actual_set:
            findings.append(
                _absent_message(
                    artifact_path[len("registries/"):]
                    if artifact_path.startswith("registries/")
                    else artifact_path
                )
            )

    return len(findings) == 0, findings


def _scan_top_level(registries_dir: Path):
    """List regular files directly inside ``registries/`` (not
    recursive). Section 0.7 exempts schemas, validators and fixtures
    from the inventory; the per-entry content directories this repo
    keeps alongside the top-level registry files (``registries/people/``,
    ``registries/policies/``, etc.) are a separate, per-entry storage
    concern this rule does not resolve -- the manifest's own granularity
    (Section 52.6) is one artifact per top-level file/glob, not per
    entry."""
    if not registries_dir.is_dir():
        return []
    return [
        f"registries/{p.name}"
        for p in sorted(registries_dir.iterdir())
        if p.is_file()
    ]


def check(registry_root, as_of, records_root=None):
    """Option B entry point: load ``registries/OWNERS.yaml`` and
    ``registries/INVENTORY.yaml`` under ``registry_root`` and reconcile
    them against the top-level files actually present in
    ``registries/``. Silent (no findings) if ``OWNERS.yaml`` is absent.
    """
    root = Path(registry_root)
    owners_path = root / "registries" / "OWNERS.yaml"
    if not owners_path.exists():
        return True, []

    owners_doc = yaml.safe_load(owners_path.read_text(encoding="utf-8"))

    inventory_path = root / "registries" / "INVENTORY.yaml"
    inventory_doc = None
    if inventory_path.exists():
        inventory_doc = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))

    actual_paths = _scan_top_level(root / "registries")
    return check_document(owners_doc, inventory_doc, actual_paths)
