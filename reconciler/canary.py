"""L3-P1-17: the seeded canary and the zero-findings FAIL rule (spec 53.1; AT-102; SIG-13; §95.4).

AT-102: "a reconciler that finds nothing is assumed broken, never
assumed clean." The `display_name` comparator (reconciler.comparators.
display_name, Green class) reads fixture-a/canary.yaml and always
reports one seeded, intentionally-mismatched finding at the id
CANARY_ID. assert_canary() is the single place that checks for its
presence; reconciler.cli's full-run path calls it to decide whether a
run's status is OK or FAILED.

The canary finding is deliberately excluded from every drift-budget
count and is never a candidate for repair - both because it is Green
(§53.2 Level 1: detect only, never escalated) and because it exists
purely as an instrument check, not a real declared-vs-actual gap. Any
future drift-budget aggregator must filter on `comparator ==
"display_name"` (or, equivalently, `id == CANARY_ID`) before summing.
"""

from __future__ import annotations

from reconciler.model import Finding

CANARY_ID = "CANARY-001"


def assert_canary(findings: list[Finding]) -> bool:
    """True only when `findings` contains the seeded canary."""
    return any(f.id == CANARY_ID for f in findings)
