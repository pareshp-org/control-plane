"""L3-P1-17: display_name comparator - the seeded canary (Green class, §53.2 Level 1).

Reads the fixture's canary.yaml and reports its deliberately-seeded
display-name mismatch. This comparator's entire purpose is to prove
the reconciler instrument is running at all (AT-102) - it is not a
real declared-vs-actual product-naming check, and every fixture is
expected to seed exactly one such mismatch.
"""

from __future__ import annotations

from reconciler.canary import CANARY_ID
from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("display_name", fail_class=DriftClass.GREEN)
def compare(declared, actual, as_of):
    canary = declared.canary
    if not canary:
        return [], 0

    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    findings: list[Finding] = []
    declared_name = canary.get("declared_display_name")
    actual_name = canary.get("actual_display_name")
    if declared_name != actual_name:
        findings.append(
            Finding(
                id=CANARY_ID,
                comparator="display_name",
                scope=canary.get("product", ""),
                drift_class=DriftClass.GREEN,
                level=Level.DETECT,
                evidence=(
                    f"seeded canary: declared display_name={declared_name!r} vs "
                    f"actual={actual_name!r} - do not fix, this is the instrument check"
                ),
                first_seen=first_seen,
            )
        )

    return findings, 1
