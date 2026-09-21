"""R-POL-04 -- a policy's current stage entered before its declared
min_dwell elapsed.

Section 55.3: a policy must dwell at Warn and Pilot for at least its
declared `min_dwell` before advancing (or before being validated as of
a given day while still in that stage). `min_dwell.warn` is declared in
days (Section 55.1); `min_dwell.pilot` is declared in **delivery
cycles**, not days, per the same section's comment "days at Warn;
delivery cycles at Pilot". A delivery cycle's length in days is not
declared anywhere in the specification. This rule therefore reads
`min_dwell.pilot` as a count of days -- the practical default until
L0 resolves the unit -- and says so in its own message, rather than
inventing a delivery-cycle-length constant. See the L1-604 task's own
conditional STOP (`BLOCKER L1 L1-604: min_dwell.pilot is declared in
delivery cycles...`) for the two candidate resolutions this ships
without choosing between.

`observe` and `enforce` have no declared `min_dwell` entry and never
fire this rule -- only `warn` and `pilot` do.

Standalone, directly-tested rule function -- see r_pol_01.py's module
docstring for why this is not wired into the frozen Option B (FD-094)
R01-R18 dispatch table.

Silent for a policy whose `status` is retired, withdrawn or superseded
(not "in force"; Section 55.3's ladder governs a policy that is).
"""
from __future__ import annotations

import datetime

from validators.registry.rules.r_pol_01 import INAPPLICABLE_STATUSES

RULE_ID = "R-POL-04"
SPEC = "Section 55.3"
APPLIES_TO = ["policies"]

_DWELL_STAGES = ("warn", "pilot")


def _as_date(value) -> datetime.date:
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value))


def check_document(doc, today, source="policies.yaml"):
    """Check one already-parsed policies.yaml-shaped document as of
    ``today`` (a ``datetime.date`` or an ISO-8601 date string).

    Returns (passed, findings) where findings are R-POL-04 message strings.
    """
    findings = []
    if not isinstance(doc, dict):
        return True, []
    today_date = _as_date(today)
    for idx, policy in enumerate(doc.get("policies", []) or []):
        if not isinstance(policy, dict):
            continue
        if policy.get("status") in INAPPLICABLE_STATUSES:
            continue
        stage = policy.get("enforcement_stage")
        if stage not in _DWELL_STAGES:
            continue
        min_dwell = policy.get("min_dwell") or {}
        declared = min_dwell.get(stage)
        if declared is None:
            continue
        effective_date = policy.get("effective_date")
        if effective_date is None:
            continue
        elapsed = (today_date - _as_date(effective_date)).days
        if elapsed < declared:
            pid = policy.get("id", "<unknown>")
            findings.append(
                f"R-POL-04 {source}:/policies/{idx}/effective_date "
                f"policy '{pid}' is at '{stage}' {elapsed} days after its effective_date; "
                f"its declared min_dwell for that stage is {declared} days; Section 55.3"
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
                findings.append(f"R-POL-04 {candidate}: could not parse YAML: {e}")
                continue
            _, doc_findings = check_document(doc, as_of, source=str(candidate))
            findings.extend(doc_findings)
    return len(findings) == 0, findings
