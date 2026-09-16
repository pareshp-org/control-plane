"""L3-P1-19: fail-closed matrix for Blocking-class checks (spec 64.2; §101 invariant 80).

§64.2: "Reconciliation: fail closed for Blocking-class checks; fail
open with an alert for Green-class checks." This module treats Red the
same as Blocking (both "closed") and Amber the same as Green (both
"open_with_alert") - the spec names only the two extremes, and neither
of the two remaining classes reads as the opposite of its named
neighbour under §53.4's single severity scale.

Every registered comparator must declare its fail-mode class via
reconciler.registry.comparator's `fail_class` kwarg - reconciler.cli's
`list` command enforces that a registered id always has one (§64.2:
"Unclassified controls fail CI").
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level

FAIL_MODE: dict[DriftClass, str] = {
    DriftClass.BLOCKING: "closed",
    DriftClass.RED: "closed",
    DriftClass.AMBER: "open_with_alert",
    DriftClass.GREEN: "open_with_alert",
}


def on_comparator_error(comparator_id: str, drift_class: DriftClass, exc: Exception) -> Finding:
    """Convert a comparator's own execution failure into a Finding.

    Fail-closed (Blocking, Red): the comparator's inability to execute
    is itself a Blocking finding - "detection failure must not silently
    permit drift" (§64.2). Fail-open (Amber, Green): the failure is a
    visible Amber alert naming the comparator and the failure, and the
    run continues rather than escalating to Blocking.

    `first_seen` is left blank here (no `as_of` is passed - only three
    arguments are specified for this function); the caller, which does
    have `as_of` in scope, is responsible for setting it via
    dataclasses.replace() before the finding is reported.
    """
    mode = FAIL_MODE[drift_class]
    finding_class = DriftClass.BLOCKING if mode == "closed" else DriftClass.AMBER
    level = Level.BLOCK if mode == "closed" else Level.WARN

    return Finding(
        id=f"{comparator_id}:execution_failure",
        comparator=comparator_id,
        scope=comparator_id,
        drift_class=finding_class,
        level=level,
        evidence=(
            f"{comparator_id} could not execute ({type(exc).__name__}: {exc}); its "
            f"declared class {drift_class.value} fails {mode!r}"
        ),
        first_seen="",
    )
