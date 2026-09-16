"""L3-P3-03: check-run identity assertion (spec 40.1: "A check run
published under that name by any identity other than the reconciler
is Blocking drift.")

For each declared product repository, read `check_runs(repo)`. If the
`control-plane/blocking-drift` check exists there and its
`published_by` is not the declared reconciler identity, that is
Blocking-class drift, in its own right - a way for a non-reconciler
identity to move the one gate spec 40.1 authorises the reconciler
credential to hold.
"""

from __future__ import annotations

from reconciler.checkrun import CHECK_NAME
from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

# The identity every control-plane/blocking-drift check run must be
# published under - the reconciler's own machine credential (spec
# 40.1). Any other name on this specific check is itself Blocking
# drift, regardless of what conclusion it carries.
RECONCILER_IDENTITY = "reconciler"


@comparator("checkrun_identity", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    compared = 0

    for product_name in declared.products:
        compared += 1
        check = actual.check_runs(product_name).get(CHECK_NAME)
        if check is None:
            continue
        published_by = check.get("published_by")
        if published_by != RECONCILER_IDENTITY:
            findings.append(
                Finding(
                    id=f"checkrun_identity:{product_name}",
                    comparator="checkrun_identity",
                    scope=product_name,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name}'s {CHECK_NAME!r} check run was published by "
                        f"{published_by!r}, not {RECONCILER_IDENTITY!r} - a check run "
                        "under that name from any other identity is Blocking drift"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, compared
