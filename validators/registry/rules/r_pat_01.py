"""R-PAT-01 -- a confirmed pattern needs three occurrences (Section 58.3, AT-040).

Section 58.3: a pattern is confirmed on the third occurrence. The schema
carries `occurrences` with `minItems: 1` only -- the third-occurrence
threshold is enforced here, as a rule, so the failure names AT-040 and
Section 58.3 explicitly and the invariant register (L1-902) has a live
check id to point at, the same reasoning L1-201 gives for R-CAP-01.

Call signature matches validators/registry/rules/registry.py's Option B
convention (FD-094): `check(registry_root, as_of, records_root=None) ->
(passed: bool, findings: list[str])`.
"""
from pathlib import Path

import yaml

SPEC = "Section 58.3"
APPLIES_TO = ["patterns"]

_CONFIRMATION_THRESHOLD = 3


def check_document(doc, source="patterns.yaml"):
    """Check one already-parsed patterns.yaml-shaped document."""
    findings = []
    if not isinstance(doc, dict):
        return True, []
    for idx, pattern in enumerate(doc.get("patterns", []) or []):
        if not isinstance(pattern, dict):
            continue
        occurrences = pattern.get("occurrences") or []
        n = len(occurrences)
        if n < _CONFIRMATION_THRESHOLD:
            pat_id = pattern.get("id", "<unknown>")
            findings.append(
                f"R-PAT-01 {source}:/patterns/{idx}/occurrences "
                f"pattern '{pat_id}' records {n} occurrences; "
                f"Section 58.3 confirms a pattern on the third occurrence"
            )
    return len(findings) == 0, findings


def check(registry_root, as_of, records_root=None):
    """Option B entry point: scan every patterns.yaml under registry_root."""
    root = Path(registry_root)
    findings = []
    candidates = [root / "registries" / "patterns.yaml", root / "patterns.yaml"]
    for path in candidates:
        if not path.exists():
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            findings.append(f"R-PAT-01 {path}: could not parse YAML: {e}")
            continue
        _, doc_findings = check_document(doc, source=str(path))
        findings.extend(doc_findings)
    return len(findings) == 0, findings
