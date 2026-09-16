"""R-POL-03 -- a policy at Enforce naming no exception_window_closes.

Section 55.3: a policy at the Enforce stage must name a close date for
its exception window. `exception_window_closes` is schema-typed
`isoDateOrNull` (schemas/registry/policies.registry.v1.schema.json) --
null is structurally valid but leaves the window permanently open, so
this is a live rule, not a schema constraint.

Standalone, directly-tested rule function -- see r_pol_01.py's module
docstring for why this is not wired into the frozen Option B (FD-094)
R01-R18 dispatch table.

Silent for a policy whose `status` is retired, withdrawn or superseded
(not "in force"; Section 55.3's ladder governs a policy that is).
"""
from __future__ import annotations

from validators.registry.rules.r_pol_01 import INAPPLICABLE_STATUSES

RULE_ID = "R-POL-03"
SPEC = "Section 55.3"
APPLIES_TO = ["policies"]


def check_document(doc, source="policies.yaml"):
    """Check one already-parsed policies.yaml-shaped document.

    Returns (passed, findings) where findings are R-POL-03 message strings.
    """
    findings = []
    if not isinstance(doc, dict):
        return True, []
    for idx, policy in enumerate(doc.get("policies", []) or []):
        if not isinstance(policy, dict):
            continue
        if policy.get("status") in INAPPLICABLE_STATUSES:
            continue
        if policy.get("enforcement_stage") != "enforce":
            continue
        if policy.get("exception_window_closes") is None:
            pid = policy.get("id", "<unknown>")
            findings.append(
                f"R-POL-03 {source}:/policies/{idx}/exception_window_closes "
                f"policy '{pid}' is at Enforce and names no exception_window_closes; "
                f"Section 55.3"
            )
    return len(findings) == 0, findings


def check(registry_root, as_of, records_root=None):
    """Option B-shaped entry point (FD-094 call signature); see
    r_pol_01.check for why this is not wired into RULES.
    """
    from pathlib import Path

    import yaml

    findings = []
    roots = [Path(registry_root)]
    if records_root:
        roots.append(Path(records_root))
    for root in roots:
        for candidate in (root / "registries" / "policies.yaml", root / "policies.yaml"):
            if not candidate.exists():
                continue
            try:
                doc = yaml.safe_load(candidate.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                findings.append(f"R-POL-03 {candidate}: could not parse YAML: {e}")
                continue
            _, doc_findings = check_document(doc, source=str(candidate))
            findings.extend(doc_findings)
    return len(findings) == 0, findings
