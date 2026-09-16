"""L3-P1-15: restore_tested vs the restore-test records (spec 53.1 final row; §44.2).

A declared `restore_tested` date with no matching passing record for
that product is Blocking - "a declared date with no matching record is
an unevidenced reliability claim, not a scheduling question" (§101
invariants 3 and 4).
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("restore_tested", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    records = actual.restore_test_records()
    compared = 0

    for product_name, product_yaml in declared.products.items():
        declared_date = product_yaml.get("restore_tested")
        if declared_date is None:
            continue
        compared += 1
        matched = any(
            r.get("product") == product_name and r.get("date") == declared_date and r.get("result") == "pass"
            for r in records
        )
        if not matched:
            findings.append(
                Finding(
                    id=f"restore_tested:{product_name}",
                    comparator="restore_tested",
                    scope=product_name,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name} declares restore_tested={declared_date!r} but no "
                        "matching passing restore-test record exists"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, compared
