"""L3-P3-05: reclassification gate (spec 53.5: "Reclassifying a
finding downward requires the same authority as approving an
exception for it, and is recorded as a decision. There is no informal
path from Red to Amber.")

Drift-class reclassification names no exception `type` of its own in
the Section 54.3 authority mapping, so it resolves through that
mapping's own fallback for a Founder-owned, out-of-normal-flow
decision with no more specific type: the `exceptional-approval`
capability (spec 9: "Authorise an action outside the normal flow, per
the exceptional-authorisation list of Section 26.3 and the
exception-authority mapping of Section 54.3"; spec 54.3's own
`policy_waiver` row uses the identical fallback - "the policy's
declared owner capability, or `exceptional-approval` for Founder-owned
policies" - and a drift class is exactly such a Founder-owned policy,
spec 53.6). Downward reclassification of a finding is precisely that
kind of action: it overrides what the instrument itself computed.

Every call that does not raise returns both the reclassified Finding
and a ReclassificationRecord - there is no code path here that
changes a class without producing an audit entry (spec 53.5: "is
recorded as a decision").
"""

from __future__ import annotations

import dataclasses
from typing import Any, Mapping, Union

from reconciler.model import DriftClass, Finding

# spec 9 / 54.3: the Founder-class capability authorising an
# out-of-normal-flow decision with no more specific exception type -
# the authority spec 53.5 requires for a downward reclassification.
EXCEPTION_APPROVAL_CAPABILITY = "exceptional-approval"

# Ordering of the spec 53.4 scale, least to most severe. "Downward"
# means strictly decreasing under this order.
_ORDER: dict[DriftClass, int] = {
    DriftClass.GREEN: 0,
    DriftClass.AMBER: 1,
    DriftClass.RED: 2,
    DriftClass.BLOCKING: 3,
}

Actor = Union[Mapping[str, Any], str]


class ReclassificationRefused(PermissionError):
    """Raised when a downward reclassification lacks a decision record
    or the actor's authority. Spec 53.5: "There is no informal path
    from Red to Amber" - and none for any other downward move either.
    """


@dataclasses.dataclass(frozen=True)
class ReclassificationRecord:
    finding_id: str
    from_class: DriftClass
    to_class: DriftClass
    actor: str
    decision_record_id: str | None
    direction: str  # "upward" | "downward"


def _actor_login(actor: Actor) -> str:
    if isinstance(actor, str):
        return actor
    return str(actor.get("github_login", actor))


def _actor_capabilities(actor: Actor) -> set[str]:
    if isinstance(actor, str):
        return set()
    return set(actor.get("capabilities") or [])


def reclassify(
    finding: Finding,
    to_class: DriftClass,
    actor: Actor,
    decision_record_id: str | None = None,
) -> tuple[Finding, ReclassificationRecord]:
    """Reclassify `finding` to `to_class`. Returns (new Finding,
    ReclassificationRecord) on success.

    Downward moves (to a lower-severity class) raise
    ReclassificationRefused unless BOTH:
      * `decision_record_id` is a non-empty string, and
      * `actor` holds EXCEPTION_APPROVAL_CAPABILITY.

    Upward moves (to an equal-or-higher-severity class) are always
    permitted and are recorded exactly like a downward one - spec
    53.5 gates the direction that loosens a control, not the
    audit trail itself.
    """
    if not isinstance(to_class, DriftClass):
        raise TypeError(f"to_class must be a DriftClass, got {to_class!r}")

    is_downward = _ORDER[to_class] < _ORDER[finding.drift_class]
    direction = "downward" if is_downward else "upward"

    if is_downward:
        if not decision_record_id:
            raise ReclassificationRefused(
                f"downward reclassification of {finding.id!r} "
                f"({finding.drift_class.value} -> {to_class.value}) requires a "
                "non-empty decision_record_id (spec 53.5: 'no informal path')"
            )
        if EXCEPTION_APPROVAL_CAPABILITY not in _actor_capabilities(actor):
            raise ReclassificationRefused(
                f"{_actor_login(actor)!r} lacks {EXCEPTION_APPROVAL_CAPABILITY!r}; "
                f"downward reclassification of {finding.id!r} requires the same "
                "authority as approving an exception for it (spec 53.5)"
            )

    record = ReclassificationRecord(
        finding_id=finding.id,
        from_class=finding.drift_class,
        to_class=to_class,
        actor=_actor_login(actor),
        decision_record_id=decision_record_id,
        direction=direction,
    )
    return dataclasses.replace(finding, drift_class=to_class), record
