"""L3-P6-08: repair record emitter (spec 26.4 "logged as repair
records and visible on the drift view"; spec 53.2 Level 3 "then
record the repair"; spec 53.7).

Turns every Phase 6 class's `Repair` (reconciler/repair/__init__.py)
into exactly one repair record carrying, at minimum, the nine fields
this task's own text names: `repair_class`, `finding_id`, `scope`,
`before`, `after`, `permitted_reason`, `compensating_action`,
`performed_at`, `run_id`. Seven of the nine are copied straight off
the source `Repair`; the remaining two - `performed_at` and `run_id`
- are run-level metadata a `Repair` itself never carries
(reconciler/repair/__init__.py's module docstring explains why: the
caller, not the repair class, has them in scope), so `emit()` below
is where they are added.

`reconciler.contracts_map` (L3-P0-03) is where a module like this one
would normally read `CONTRACTS["repair_record"]` from instead of a
literal key tuple. That task is still blocked - L3-D2 was never
answered, exactly the blocker reconciler/runrecord.py's docstring
already records for the run-record side - so, following that same
module's precedent, `REQUIRED_KEYS` below defines this module's own
explicit, documented shape (the nine fields the task text names)
rather than importing a contract module that does not exist on disk
yet.

`emit()` raises for any repair whose `compensating_action` is missing
or blank (acceptance 2). Section 53.7's repair-class-freeze replay has
nothing to revert against without it, so a record missing one may
never be produced - not logged with a placeholder, not skipped
silently.

Nothing below opens a file, and no path under `records/**` or
`events/**` - the two trees Lane 4 owns and the reconciler credential
must never write to (spec 40.1 D89; AT-110's negative attempt 5) -
ever appears as a write target in this module. A `RepairRecord` is
an in-memory, JSON-shaped value; handing it to the control-plane write
path is a step this lane's build does not take (the task's own text:
"Records are handed to the control-plane write path; this lane does
not write them into records/**").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from reconciler.repair import Repair

# The nine fields this task's own text names as the minimum every
# repair record carries (spec 26.4, 53.2, 53.7, 28.1).
REQUIRED_KEYS: tuple[str, ...] = (
    "repair_class",
    "finding_id",
    "scope",
    "before",
    "after",
    "permitted_reason",
    "compensating_action",
    "performed_at",
    "run_id",
)


class MissingCompensatingAction(ValueError):
    """Raised by emit() when a Repair's compensating_action is missing
    or blank. Spec 53.7 / 28.1: the compensating action is the tested,
    named revert path a repair-class-freeze replays against, so a
    record without one is refused at emit time rather than produced
    with a hole in it."""


@dataclass(frozen=True)
class RepairRecord:
    """One repair, carrying the nine fields REQUIRED_KEYS names.
    Field order matches REQUIRED_KEYS."""

    repair_class: str
    finding_id: str
    scope: str
    before: Any
    after: Any
    permitted_reason: str
    compensating_action: str
    performed_at: str
    run_id: str

    def to_dict(self) -> dict:
        return {key: getattr(self, key) for key in REQUIRED_KEYS}


def emit(repair: Repair, *, performed_at: str, run_id: str) -> RepairRecord:
    """One `Repair` -> one `RepairRecord` (acceptance 1: exactly one
    record per repair, `before` and `after` both populated straight
    off the source repair)."""
    action = repair.compensating_action
    if not action or not action.strip():
        raise MissingCompensatingAction(
            f"repair {repair.finding_id!r} ({repair.repair_class!r}) carries no "
            "compensating_action; refusing to emit a repair record with nothing to "
            "revert against (spec 53.7 / 28.1)"
        )
    if not performed_at:
        raise ValueError("emit() requires a non-empty performed_at timestamp")
    if not run_id:
        raise ValueError("emit() requires a non-empty run_id")

    return RepairRecord(
        repair_class=repair.repair_class,
        finding_id=repair.finding_id,
        scope=repair.scope,
        before=repair.before,
        after=repair.after,
        permitted_reason=repair.permitted_reason,
        compensating_action=action,
        performed_at=performed_at,
        run_id=run_id,
    )


def emit_all(repairs: Sequence[Repair], *, performed_at: str, run_id: str) -> list[RepairRecord]:
    """`emit()` over every repair a run performed, in order - exactly
    one record per repair (acceptance 1). One bad repair (a missing
    compensating_action) fails the whole batch rather than silently
    dropping the offending record - the standing STOP-on-violation
    posture, not a best-effort emit."""
    return [emit(one, performed_at=performed_at, run_id=run_id) for one in repairs]
