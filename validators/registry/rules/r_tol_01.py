"""R-TOL-01 -- tool criticality must be within the Section 62.1 enumeration.

Section 62.1: "a tool entry whose `criticality` is absent or outside this
enumeration fails control-plane CI validation." The schema's own `enum`
already denies an out-of-scope value structurally; this rule is the live
check that names the failure for CI/report purposes, on the same reasoning
L1-201 gives for R-CAP-01.

Deliberately does NOT reuse Section 6.1's `reliability_criticality` product
vocabulary -- Section 62.1 closes: "The two product criticality fields of
Section 6.1 are a separate vocabulary; no rule reads one for the other."

Call signature matches validators/registry/rules/registry.py's Option B
convention (FD-094): `check(registry_root, as_of, records_root=None) ->
(passed: bool, findings: list[str])`. Not registered in RULES (that list
is R01-R18 sequential; not this task's file to edit) -- exercised directly
by validators/registry/tests/test_tools_schema.py and importable the same
way for CLI --rule wiring later.
"""
from pathlib import Path

import yaml

SPEC = "Section 62.1"
APPLIES_TO = ["tools"]

_ALLOWED = {"high", "medium", "low"}


def check_document(doc, source="tools.yaml"):
    """Check one already-parsed tools.yaml-shaped document.

    Returns (passed, findings) where findings are R-TOL-01 message strings.
    """
    findings = []
    if not isinstance(doc, dict):
        return True, []
    for tool in doc.get("tools", []) or []:
        if not isinstance(tool, dict):
            continue
        tool_id = tool.get("id", "<unknown>")
        criticality = tool.get("criticality")
        if criticality is None or criticality not in _ALLOWED:
            findings.append(
                f"R-TOL-01 {source}: tool '{tool_id}' declares criticality "
                f"'{criticality}', which is outside the Section 62.1 enumeration"
            )
    return len(findings) == 0, findings


def check(registry_root, as_of, records_root=None):
    """Option B entry point: scan every tools.yaml under registry_root."""
    root = Path(registry_root)
    findings = []
    candidates = [root / "registries" / "tools.yaml", root / "tools.yaml"]
    for path in candidates:
        if not path.exists():
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            findings.append(f"R-TOL-01 {path}: could not parse YAML: {e}")
            continue
        _, doc_findings = check_document(doc, source=str(path))
        findings.extend(doc_findings)
    return len(findings) == 0, findings
