"""L3-P8-01: gap detector and expiry replay (spec 53.7 bullets 1 and 3; spec 46.1).

Section 53.7, transcribed: "The control loop can fail in two
directions. It can go dark - a reconciliation gap, an export gap, or a
health-report gap." Bullet 1, verbatim: "Replay expiries that should
have fired during the gap - assignment end_dates, temporary access,
exception expiries - and revoke or revert anything now overdue." Bullet
3, verbatim: "Then re-run all standing checks and confirm clean
results, including the seeded canary."

`detect_gap()` answers "did the loop go dark, and for how long" for one
or more named cycle kinds - reconciliation, export, health-report -
from a run-history of past completions. A kind with no recorded run at
all is never read as clean (the same posture reconciler.canary takes
toward zero findings, AT-102): it is reported as a gap of unknown
depth, not silently skipped.

`replay_expiries()` is bullet 1. It does not duplicate the revocation
logic reconciler.repair.expiry_revoke already carries (spec 26.4: one
write path, not a second one invented for the gap) - it calls straight
through to `revoke_expired_assignments()` / `revoke_expired_exceptions()`
and adds exactly one thing: nothing is filtered by the window's start.
An expiry the loop missed on the first day of a ten-day gap is exactly
as overdue as one it missed on the last day, and bullet 1 says "revoke
or revert anything now overdue" with no floor on how far back overdue
may reach.

Task note on signatures: the task text names this function
`replay_expiries(window)`. A single-argument function cannot itself
know which assignments or exceptions are declared, so the declared
side - `assignment_findings`, `exceptions` - is threaded through as
explicit parameters instead of being read from a global or a fixture
path baked into this module. `window` still governs the call: its
`end` is the "as of" boundary every revocation decision is measured
against, exactly as a normal cycle would use `as_of` (spec 26.4 - one
write path).

`confirm_clean()` is bullet 3's re-run confirmation: the gap procedure
is not allowed to declare itself closed on a re-run that quietly
checked nothing. It fails whenever the seeded canary
(reconciler.canary.assert_canary, L3-P1-17) is absent, and whenever a
Blocking finding survived the replay.
"""

from __future__ import annotations

import dataclasses
from datetime import date, timedelta
from typing import Any, Mapping, Sequence

from reconciler.canary import assert_canary
from reconciler.model import DriftClass, Finding
from reconciler.repair import Repair
from reconciler.repair.expiry_revoke import revoke_expired_assignments, revoke_expired_exceptions

# Section 53.7's three named-dark directions. `export` has no cadence
# fixed by this lane's spec anchors (that is a stated, routed gap, not
# invented here) - callers that have one supply it through
# `expected_interval`; callers that don't simply omit "export" from
# `run_history`.
CYCLE_KINDS = ("reconciliation", "export", "health-report")


class GapDetectionError(RuntimeError):
    """Raised when `run_history` names a kind `detect_gap()` has no
    expected interval for. Never guessed at; the caller must supply one."""


@dataclasses.dataclass(frozen=True)
class GapWindow:
    """One missed-cycle window for one loop kind (spec 53.7).

    `start` is the moment the kind was next due and was not observed;
    `end` is `as_of`, the moment the gap was noticed. `missed_cycles`
    counts how many expected intervals fit inside that span, rounded up
    - a gap window is never reported as "one cycle late" when it is
    several.
    """

    kind: str
    start: date
    end: date
    missed_cycles: int

    def contains(self, when: date) -> bool:
        return self.start <= when <= self.end


def detect_gap(
    run_history: Mapping[str, Sequence[date]],
    expected_interval: Mapping[str, int] | int,
    as_of: date,
) -> list[GapWindow]:
    """Return one `GapWindow` per kind in `run_history` whose most recent
    completion is more than its expected interval old as of `as_of` -
    the loop went dark for that kind (spec 53.7).

    `expected_interval` is either a single integer number of days applied
    to every kind present in `run_history`, or a mapping of kind -> days
    for a per-kind cadence (spec 51.2's reconciliation/export/health-report
    figures differ). A kind in `run_history` with no matching interval
    raises `GapDetectionError` rather than silently assuming one.

    A kind whose history is empty - never observed - is reported as a
    one-cycle-deep gap window opening at `as_of` itself: the true start
    of its dark period is unknown, but "no run has ever completed" is
    never read as "clean" (AT-102's posture, applied here to the loop's
    own history rather than to a run's findings).
    """
    if isinstance(expected_interval, int):
        intervals: dict[str, int] = {kind: expected_interval for kind in run_history}
    else:
        intervals = dict(expected_interval)

    windows: list[GapWindow] = []
    for kind, history in run_history.items():
        interval_days = intervals.get(kind)
        if interval_days is None:
            raise GapDetectionError(
                f"detect_gap: no expected_interval declared for kind={kind!r}; "
                "supply one rather than assuming a cadence"
            )
        if not history:
            windows.append(GapWindow(kind=kind, start=as_of, end=as_of, missed_cycles=1))
            continue

        last_run = max(history)
        due = last_run + timedelta(days=interval_days)
        if due >= as_of:
            continue  # still inside the expected cadence: no gap

        days_late = (as_of - due).days
        missed_cycles = max(1, -(-days_late // interval_days))  # ceil division, at least 1
        windows.append(GapWindow(kind=kind, start=due, end=as_of, missed_cycles=missed_cycles))

    return windows


def replay_expiries(
    window: GapWindow,
    assignment_findings: Sequence[Finding] = (),
    exceptions: Sequence[Mapping[str, Any]] = (),
) -> tuple[list[Repair], list[Finding]]:
    """Bullet 1: replay every expiry that should have fired inside
    `window` and revoke or revert anything now overdue.

    `assignment_findings` is the Phase-1 `expiry` comparator's output
    (covers both "assignment end_dates" and "temporary access" - the
    only delegation-shaped structure product.yaml exposes carries both
    under one row, per reconciler.comparators.expiry's own docstring).
    `exceptions` is every declared exception entry. Both are passed
    straight through to `reconciler.repair.expiry_revoke`'s existing,
    tested revocation logic - unchanged, because spec 26.4 names one
    write path and the gap procedure does not invent a second one.

    `window.end` is the "as of" boundary for the exception check, not
    `window.start`: an exception that expired long before the gap even
    opened is exactly as overdue as one that expired the day the gap
    was noticed, and bullet 1 draws no floor at the window's start.
    """
    repairs = list(revoke_expired_assignments(assignment_findings, enabled=True))
    exception_repairs, escalations = revoke_expired_exceptions(exceptions, window.end, enabled=True)
    repairs.extend(exception_repairs)
    return repairs, escalations


def confirm_clean(findings: Sequence[Finding]) -> bool:
    """Bullet 3: "re-run all standing checks and confirm clean results,
    including the seeded canary."

    Returns `False` when the seeded canary (L3-P1-17, AT-102) is absent
    from `findings` - the same zero-findings-is-broken rule a normal run
    applies, applied here so the gap procedure cannot mistake a blinded
    re-run instrument for a closed gap - and `False` when any Blocking
    finding survived the replay. Returns `True` only when both checks
    pass.
    """
    if not assert_canary(list(findings)):
        return False
    return not any(f.drift_class == DriftClass.BLOCKING for f in findings)
