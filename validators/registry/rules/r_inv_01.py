"""R-INV-01 -- the owner manifest's artifact count must match its own
declared count (Section 52.6: "This table is the complete inventory --
twenty-nine entries").

Standalone, directly-tested rule function -- see the module docstring of
``r_svc_01.py`` (and, for the OWNERS.yaml-specific precedent,
``validators/registry/tests/test_owners_manifest.py``) for why this is
not wired into the frozen Option B (FD-094, ``contracts/validator-contract.md``)
``R01``..``R18`` dispatch table in ``validators/registry/rules/registry.py``.
That contract freezes the rule catalogue as R01-R18 flat files and the
CLI's own ``--format json`` grammar; this task's ACCEPTANCE/SELF-VERIFY
text in ``lanes/L1-05-tasks.md`` (the ``OK: N file(s) validated`` /
``ERROR <rule> ...`` lines, and ``from validators.registry.rules import
discover``) predates that decision and is superseded by it, exactly as
already documented for R-SVC-01..03, R-PAT-01, R-TOL-01 and R-PRD-11/27/28.
``discover()`` was never added to ``validators/registry/rules/__init__.py``
(it ships empty) by any of those tasks either -- this task does not add
it, for the same reason.

Call signature matches the Option B convention (FD-094) for the parts of
it that still apply: ``check(registry_root, as_of, records_root=None) ->
(passed: bool, findings: list[str])``. Not registered in ``registry.py``'s
``RULES`` list (frozen R01-R18); importable directly for testing and for
later CLI ``--rule`` wiring, the same deferral ``r_pat_01.py`` and
``r_tol_01.py`` document.

KNOWN RED on the live tree: ``registries/OWNERS.yaml`` ships thirty
artifact entries against ``declared_count: 29`` (see the L1-505 blocker,
and ``test_owners_manifest.py``'s identical note). This module reports
that discrepancy; it does not silence it.
"""
from __future__ import annotations

from pathlib import Path

import yaml

RULE_ID = "R-INV-01"
SPEC = "Section 52.6"
APPLIES_TO = ["owners"]


def check_document(owners_doc, source="registries/OWNERS.yaml"):
    """Check one already-parsed OWNERS.yaml-shaped document.

    Returns ``(passed, findings)``. Silent (no findings) when
    ``owners_doc`` is ``None`` -- mirrors R-SVC-01's "absent from
    ctx.docs" convention: this rule has nothing to compare against.
    """
    if not isinstance(owners_doc, dict):
        return True, []
    artifacts = owners_doc.get("artifacts") or []
    declared = owners_doc.get("declared_count")
    n = len(artifacts)
    if declared is None or n == declared:
        return True, []
    finding = (
        f"R-INV-01 {source}:/artifacts the owner manifest lists {n} "
        f"control-plane artifacts; declared_count is {declared}; Section 52.6"
    )
    return False, [finding]


def check(registry_root, as_of, records_root=None):
    """Option B entry point: load ``registries/OWNERS.yaml`` under
    ``registry_root`` and check it. Silent (no findings) if the file is
    absent -- "owners absent from ctx.docs"."""
    root = Path(registry_root)
    path = root / "registries" / "OWNERS.yaml"
    if not path.exists():
        return True, []
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    source = "registries/OWNERS.yaml"
    return check_document(doc, source=source)
