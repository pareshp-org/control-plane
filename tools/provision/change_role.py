"""L3-P7-01: the `change-role` operation (spec 12.6, 12.3; invariant 56; AT-005).

Composes the plan in exactly the §12.6 order, seven steps: role_update,
capability_recalculation, permission_recalculation,
reviewer_matrix_reassessment, ownership_reassessment_prompt,
incident_responder_reassessment, dashboard_update. Every step is
declarative (§101 invariant 55: "Ownership changes are declarative and
take effect through reconciliation") - this operation edits registry
declared state and leaves the actual GitHub-side mutation to
reconciliation; nothing here calls a provisioning credential directly.

Two hard rules, both from §74 and §101 invariants 36-38:

1. `ownership_reassessment_prompt` posts a request for a human to look
   at `login`'s ownership assignments - it never reassigns anything
   itself. `ownership_reassessment_prompt()` below is the only function
   that builds that request, and it returns an `OwnershipReassessmentPrompt`
   (a message), never a mutated ownership record.
2. AT-071 requires that no code path here ever reach any formal,
   named-in-that-acceptance-test people decision. `_refuse_personnel_action`
   below is the single place this module names any of those five words -
   see its own `_FORBIDDEN_ROLE_TOKENS` tuple for the literal list; every
   other line in this file, including this docstring, deliberately says
   "a formal people decision" instead of repeating them.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.provision.plan import Plan, Step, StepKind

# AT-071 / §74: change-role must refuse to plan any of these. This is
# the one place in this module those five words may appear - the guard
# itself, never a step description or a comment describing what the
# operation does.
_FORBIDDEN_ROLE_TOKENS: tuple[str, ...] = (
    "promotion",
    "termination",
    "compensation",
    "improvement_plan",
    "formal_warning",
)

# §12.6, verbatim order.
CHANGE_ROLE_STEPS: tuple[str, ...] = (
    "role_update",
    "capability_recalculation",
    "permission_recalculation",
    "reviewer_matrix_reassessment",
    "ownership_reassessment_prompt",
    "incident_responder_reassessment",
    "dashboard_update",
)


class ForbiddenPersonnelAction(RuntimeError):
    """`to_role` names a formal people decision - AT-071 refuses this."""


@dataclass(frozen=True)
class OwnershipReassessmentPrompt:
    """A human-facing request, never an automatic reassignment.

    Nothing in this module reads or writes `primary_owner`,
    `cross_reviewer` or `backup_owner` - the fields an actual
    reassignment would touch. This dataclass carries a message only.
    """

    login: str
    to_role: str
    message: str


def _refuse_personnel_action(to_role: str) -> None:
    lowered = to_role.lower()
    hit = next((token for token in _FORBIDDEN_ROLE_TOKENS if token in lowered), None)
    if hit is not None:
        raise ForbiddenPersonnelAction(
            f"change-role refuses to plan a role transition naming {hit!r}: "
            "no code path from this operation reaches a formal people "
            "decision (promotion, compensation, warning, improvement plan "
            "or exit - AT-071)."
        )


def ownership_reassessment_prompt(login: str, to_role: str) -> OwnershipReassessmentPrompt:
    """Build the ownership-reassessment prompt for `login` moving to `to_role`.

    Returns a message asking a human to review whether `login` should
    keep any ownership assignment their new role no longer fits. This
    function performs no reassignment - there is nothing here for it to
    call that would.
    """
    return OwnershipReassessmentPrompt(
        login=login,
        to_role=to_role,
        message=(
            f"{login} is changing role to {to_role!r}: a human should review "
            f"{login}'s current ownership assignments and reassign by hand "
            "if the new role no longer fits one of them. This operation "
            "never reassigns ownership on its own (spec 74; invariant 36-38)."
        ),
    )


def build_change_role_plan(login: str, to_role: str) -> Plan:
    """Build the seven-step change-role plan (spec 12.6), in order.

    Every step is `StepKind.WRITE` - each edits declared registry state
    for reconciliation to apply (invariant 55); none is `MANUAL`
    (Section 19.1's automation-gap sense), so a dry run always prints
    `manual=0`.
    """
    _refuse_personnel_action(to_role)
    prompt = ownership_reassessment_prompt(login, to_role)

    descriptions: dict[str, str] = {
        "role_update": f"update {login}'s declared role to {to_role!r}",
        "capability_recalculation": f"recalculate {login}'s capabilities for role {to_role!r}",
        "permission_recalculation": f"recalculate {login}'s permissions for role {to_role!r}",
        "reviewer_matrix_reassessment": f"reassess the reviewer matrix entries naming {login}",
        "ownership_reassessment_prompt": prompt.message,
        "incident_responder_reassessment": f"reassess incident-responder assignments naming {login}",
        "dashboard_update": f"update dashboards reflecting {login}'s new role {to_role!r}",
    }
    steps = [Step(step_id, descriptions[step_id], StepKind.WRITE) for step_id in CHANGE_ROLE_STEPS]
    return Plan(steps=steps)
