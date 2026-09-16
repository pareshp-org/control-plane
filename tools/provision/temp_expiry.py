"""L3-P7-05: temporary-person expiry treated as an exit (spec 12.2, 12.4; AT-008).

§12.2: "Temporary-person expiry is an exit. Expiry of a temporary
specialist or contractor triggers the same exit record and orphan scan
as `remove person`." `on_expiry()` invokes the **same** eleven-step
`build_remove_person_plan()` from L3-P7-02 - not a reduced variant, not
a re-derived copy of its step list. §12.2 additionally names orphan
type 14 ("Temporary person expired with open gate-relevant work") as
"the fourteenth orphan type"; `raise_type_14_if_applicable()` is the
one place that finding gets built.

AT-008: "reconciliation revokes on the end date without human action."
`on_expiry()` is a pure function of (`person`, `as_of`, optional
`ctx`) - nothing it does waits on, or can be blocked by, a human
decision. Every step in the plan it returns is `StepKind.WRITE`
(declarative, per invariant 55), exactly as build_remove_person_plan()
already guarantees; this module adds no manual step of its own.
"""

from __future__ import annotations

from datetime import date

from reconciler.orphans import OrphanContext, OrphanFinding
from reconciler.orphans.types import BY_INDEX
from tools.provision.plan import Plan
from tools.provision.remove_person import build_remove_person_plan

# §12.2: "the fourteenth orphan type."
ORPHAN_TYPE_14 = BY_INDEX[14]
assert ORPHAN_TYPE_14.index == 14
assert ORPHAN_TYPE_14.name == "Temporary person expired with open gate-relevant work"


def _as_date(value: date | str) -> date:
    return date.fromisoformat(value) if isinstance(value, str) else value


def _holds_open_gate_work(ctx: OrphanContext, person: str) -> list[dict]:
    """Open board reviews/gate items still assigned to `person` (spec
    12.2's detection source for type 14: "open reviews and gate items
    at expiry")."""
    return [item for item in ctx.open_gate_items if item.get("assignee") == person]


def raise_type_14_if_applicable(ctx: OrphanContext, person: str, as_of: date) -> OrphanFinding | None:
    """Return the type-14 orphan finding when `person` holds open
    gate-relevant work at `as_of`; None when they hold none."""
    open_items = _holds_open_gate_work(ctx, person)
    if not open_items:
        return None
    items_desc = ", ".join(sorted(item.get("id", "<unnamed>") for item in open_items))
    return OrphanFinding(
        index=ORPHAN_TYPE_14.index,
        name=ORPHAN_TYPE_14.name,
        orphan_severity=ORPHAN_TYPE_14.orphan_severity,
        subject=person,
        detail=f"{person}: open gate-relevant work at expiry ({as_of.isoformat()}): {items_desc}",
        orphans_on=as_of.isoformat(),
    )


def on_expiry(person: str, as_of: date | str, ctx: OrphanContext | None = None) -> Plan:
    """The temporary-person expiry plan - identical to remove-person's.

    `as_of` is accepted (and normalised) because expiry is dated - the
    end date the reconciliation loop is comparing against - even though
    the eleven-step plan itself carries no date. When `ctx` is given
    and `person` holds open gate-relevant work at `as_of`, the type-14
    orphan is available via `raise_type_14_if_applicable()` (call it
    separately - `on_expiry()` returns the Plan alone, matching
    remove-person's own return shape exactly, per the "same plan, not a
    reduced variant" rule).

    No human action gates this: `as_of` is read, not asked for, and
    every one of the eleven steps executes without a manual step in
    between (AT-008).
    """
    _as_date(as_of)  # validate the date is well-formed; expiry is not optimistic about a bad end_date
    return build_remove_person_plan(person)
