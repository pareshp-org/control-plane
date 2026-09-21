"""R-POL-01 -- a policy entered directly at Enforce with no justification.

Section 55.3: a policy that skips the Observe/Warn/Pilot ladder and enters
directly at Enforce must name a justification. Invariant 78 permits the
skip only for a critical security control, and the label is auditable --
so a direct entry with a null or empty justification is a finding.

Standalone, directly-tested rule function -- see the module docstring of
r_svc_01.py (validators/registry/rules/r_svc_01.py, L1-404) for why this
is not wired into the frozen Option B (FD-094) R01-R18 dispatch table:
extending that frozen catalogue to a new numbered slot is not this task's
call to make. This mirrors the same adaptation already made for L1-404
(r_svc_01/02/03), L1-606 (r_tol_01) and L1-5xx (r_pat_01) -- FD-094
(DECIDED) supersedes the L1-005 discover()/RULE_ID/APPLIES_TO harness and
the "OK: N file(s) validated" / "ERROR <rule>" CLI grammar that this
task's own SELF-VERIFY block assumes. L1-604's test_policy_rules.py
exercises this function directly against the fixtures in
validators/registry/fixtures/pol/, exactly as test_service_schema.py and
test_tools_schema.py already do for their own rules.

A policy whose `status` is retired, withdrawn or superseded is not "in
force" (Section 55.3's ladder governs a policy that is in force), so this
rule -- like R-POL-02, R-POL-03 and R-POL-04 -- is silent for those.
"""
from __future__ import annotations

RULE_ID = "R-POL-01"
SPEC = "Section 55.3"
APPLIES_TO = ["policies"]

INAPPLICABLE_STATUSES = {"retired", "withdrawn", "superseded"}


def check_document(doc, source="policies.yaml"):
    """Check one already-parsed policies.yaml-shaped document.

    Returns (passed, findings) where findings are R-POL-01 message strings,
    following the same (passed, findings) convention as r_pat_01.check_document
    and r_tol_01.check_document.
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
        if policy.get("entered_at_enforce_directly") is not True:
            continue
        justification = policy.get("justification")
        if justification is None or justification == "":
            pid = policy.get("id", "<unknown>")
            findings.append(
                f"R-POL-01 {source}:/policies/{idx}/justification "
                f"policy '{pid}' entered directly at Enforce with no justification; "
                f"invariant 78 permits the skip only for a critical security control, "
                f"and the label is auditable"
            )
    return len(findings) == 0, findings


def check(registry_root, as_of, records_root=None):
    """Option B-shaped entry point (FD-094 call signature) for a future CLI
    wiring decision -- not registered in RULES (that list is R01-R18
    sequential and frozen; not this task's file to edit). Scans every
    policies.yaml under registry_root and records_root.
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
                findings.append(f"R-POL-01 {candidate}: could not parse YAML: {e}")
                continue
            _, doc_findings = check_document(doc, source=str(candidate))
            findings.extend(doc_findings)
    return len(findings) == 0, findings
