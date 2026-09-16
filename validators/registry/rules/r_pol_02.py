"""R-POL-02 -- a policy at Pilot naming no pilot_products.

Section 55.3: a policy at the Pilot stage must name the products it is
piloted on. `pilot_products` carries `minItems`-free array shape in the
schema (schemas/registry/policies.registry.v1.schema.json) -- an empty
list is structurally valid but names nothing to pilot against, so this
is a live rule, not a schema constraint (same reasoning L1-201 gives for
R-CAP-01).

Standalone, directly-tested rule function -- see r_pol_01.py's module
docstring for why this is not wired into the frozen Option B (FD-094)
R01-R18 dispatch table.

Silent for a policy whose `status` is retired, withdrawn or superseded
(not "in force"; Section 55.3's ladder governs a policy that is).
"""
from __future__ import annotations

from validators.registry.rules.r_pol_01 import INAPPLICABLE_STATUSES

RULE_ID = "R-POL-02"
SPEC = "Section 55.3"
APPLIES_TO = ["policies"]


def check_document(doc, source="policies.yaml"):
    """Check one already-parsed policies.yaml-shaped document.

    Returns (passed, findings) where findings are R-POL-02 message strings.
    """
    findings = []
    if not isinstance(doc, dict):
        return True, []
    for idx, policy in enumerate(doc.get("policies", []) or []):
        if not isinstance(policy, dict):
            continue
        if policy.get("status") in INAPPLICABLE_STATUSES:
            continue
        if policy.get("enforcement_stage") != "pilot":
            continue
        pilot_products = policy.get("pilot_products") or []
        if len(pilot_products) == 0:
            pid = policy.get("id", "<unknown>")
            findings.append(
                f"R-POL-02 {source}:/policies/{idx}/pilot_products "
                f"policy '{pid}' is at Pilot and names no pilot_products; Section 55.3"
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
                findings.append(f"R-POL-02 {candidate}: could not parse YAML: {e}")
                continue
            _, doc_findings = check_document(doc, source=str(candidate))
            findings.extend(doc_findings)
    return len(findings) == 0, findings
