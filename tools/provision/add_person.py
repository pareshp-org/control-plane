"""L3-P4-09: the `add-person` orchestrator (spec 12.6, 12.1; §36.4 `ai_restrictions`; AT-002).

Section 12.6, quoted verbatim (see `lanes/L3-04-provisioning.md` line 1641,
carried forward here since L3-06 supersedes L3-04's task *structure*, not
the spec text it quotes): *"`add person` produces: `people.yaml` entry;
organisation invitation; Team membership per assignments; capability
grants; AI runtime assignment honouring per-product `ai_restrictions`;
onboarding checklist issue; and registration in the review network
view."* That is seven named outputs, in this order. Section 12.1 adds one
further, separate act on top of those seven: *"the encryption key for
their self-view document, handed once, in person"* -- a manual step with
no API for it, `self_view_key_exchange`.

**Known contradiction in this task's own text (`lanes/L3-06-tasks.md`,
L3-P4-09), flagged rather than silently resolved:** the task prose calls
the above "seven automated steps ... Plus one manual step" (7 + 1 = 8),
but the task's own Acceptance/SELF-VERIFY block requires the dry-run
summary line to read exactly `PLAN add-person steps=7 writes=0 manual=1`
-- a *total* of 7. Both cannot be true of a plan holding all eight
concepts as separate steps. This module resolves the arithmetic (not the
substance) by folding the two least individually load-bearing outputs --
`onboarding_checklist_issue` and `register_review_network_view`, both
"day one" registration actions that happen together once Team membership
and capability grants have landed -- into one step,
`onboarding_and_review_registration`. Every one of the eight named
concepts is still produced (see that step's description and
`onboarding_checklist()` below, which independently renders the
onboarding-issue content); none is dropped, only two are co-located in
one `Step`. See `notes` in this task's own hand-off record for the same
flag raised to a human integrator.

Like `change_role.py` (L3-P7-01) and `remove_person.py` (L3-P7-02), every
step here is declarative (§101 invariant 55): this operation edits
registry declared state (or, for `org_invitation`, performs the one
direct act Section 12.1 assigns to `add-person` itself rather than to
reconciliation) and leaves any further GitHub-side convergence to
reconciliation. `org_invitation` grants **base Read only** -- the
organisation's default member permission -- and nothing here grants
Write directly: `team_membership_per_assignments` is the only step whose
description names a Write grant, and it is Team-derived (§11.2), never a
direct repository grant.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.provision.plan import Plan, Step, StepKind

# Section 12.6's seven "produces" outputs, with the two final ones folded
# into a single step (see the module docstring's "known contradiction"
# note) -- six automated steps -- plus the one manual step Section 12.1
# adds on top. Total: 7, matching this task's own SELF-VERIFY line.
ADD_PERSON_STEPS: tuple[str, ...] = (
    "people_yaml_entry",
    "org_invitation",
    "team_membership_per_assignments",
    "capability_grants",
    "ai_runtime_assignment",
    "onboarding_and_review_registration",
    "self_view_key_exchange",
)

# The one step of the seven that is StepKind.MANUAL -- Section 12.1: "the
# encryption key for their self-view document, handed once, in person."
# No provider API performs this; it is a tracked manual step, never
# silently missing (Section 19.1's automation-gap sense).
_MANUAL_STEP_ID = "self_view_key_exchange"

_DESCRIPTIONS: dict[str, str] = {
    "people_yaml_entry": "add a people.yaml entry for {login}",
    "org_invitation": (
        "invite {login} into the organisation at the base member permission -- Read only"
    ),
    "team_membership_per_assignments": (
        "add {login} to every GitHub Team implied by their assignments (§11.2) -- "
        "the only step in this plan that grants Write, and it is Team-derived, never a direct repository grant"
    ),
    "capability_grants": (
        "grant {login} exactly the capabilities their assignments declare, explicitly -- "
        "never inherited wholesale (§12.1, §64.1)"
    ),
    "ai_runtime_assignment": (
        "assign {login}'s AI runtime, honouring any ai_restrictions declared on the product(s) "
        "they are assigned to (§36.4) -- checked now, at onboarding, never deferred to a later pass"
    ),
    "onboarding_and_review_registration": (
        "open {login}'s onboarding checklist issue (naming the conduct adviser and the fairness "
        "rules, §12.1) and register {login} in the review network view (cross-review shadow, §12.1)"
    ),
    "self_view_key_exchange": (
        "hand {login} the encryption key for their self-view document, once, in person (§12.1) -- "
        "no API performs this"
    ),
}

# Section 12.7's milestone bands, transcribed verbatim (also quoted at
# `lanes/L3-04-provisioning.md` lines 1717-1725, which this module's
# onboarding_checklist() renders independently of that superseded task's
# own template file).
MILESTONE_BANDS: tuple[tuple[str, str], ...] = (
    ("Local setup working on first product (`make setup`, `make dev`, `make test`)", "Day 1"),
    ("First test executed against a real product", "Day 1-2"),
    ("First cross-review submitted", "Week 1"),
    ("First accepted PR merged", "Week 1-2"),
    ("First Ready item taken independently", "Week 2-3"),
    ("First independent product work as owner or co-owner", "Week 4-8"),
    ("First incident participation", "First quarter"),
)

# No real conduct-adviser identity has been supplied to this lane. Section
# 12.1 requires every joiner to learn "in writing and on day one, who the
# conduct adviser is" -- but this module must not invent a real person's
# name. The onboarding issue names this placeholder until L0 supplies the
# real identity; `onboarding_checklist()` never fabricates one.
CONDUCT_ADVISER_PLACEHOLDER = "PENDING-FOUNDER-INPUT: conduct adviser name and contact (§12.1, §81.8)"


class AiRuntimeRestricted(RuntimeError):
    """`requested_runtime` is named in the product's declared `ai_restrictions` (§36.4)."""


def build_add_person_plan(login: str) -> Plan:
    """Build the seven-step add-person plan (spec 12.6, 12.1), in order.

    Six steps are `StepKind.WRITE` (each edits declared registry state, or
    -- `org_invitation` -- performs the one direct act Section 12.1
    assigns to this operation itself); the seventh, `self_view_key_exchange`,
    is `StepKind.MANUAL`. A dry run therefore always reports
    `writes=0 manual=1` (`writes` only ever counts on an applied run, per
    `Plan.summary_line`, and no dry run this module builds is ever
    applied).
    """
    steps = [
        Step(
            step_id,
            _DESCRIPTIONS[step_id].format(login=login),
            StepKind.MANUAL if step_id == _MANUAL_STEP_ID else StepKind.WRITE,
        )
        for step_id in ADD_PERSON_STEPS
    ]
    return Plan(steps=steps)


def resolve_ai_runtime(requested_runtime: str, product_ai_restrictions: list[str] | None) -> str:
    """Return `requested_runtime`, honouring `product_ai_restrictions` (§36.4).

    Raises `AiRuntimeRestricted` if `requested_runtime` is named in the
    product's declared `ai_restrictions` list. This is the function the
    `ai_runtime_assignment` step's description promises is "checked now,
    at onboarding, never deferred": there is no code path in this module
    that assigns an AI runtime without first calling this, and nothing
    here defers the check to a later reconciliation pass.
    """
    restrictions = product_ai_restrictions or []
    if requested_runtime in restrictions:
        raise AiRuntimeRestricted(
            f"AI runtime {requested_runtime!r} is restricted by this product's declared "
            f"ai_restrictions ({restrictions!r}) -- refused at onboarding, not deferred (§36.4)."
        )
    return requested_runtime


@dataclass(frozen=True)
class OnboardingChecklist:
    """The rendered onboarding-checklist issue body, plus the fields it was built from.

    Kept as a dataclass (message + inputs), the same shape
    `change_role.py`'s `OwnershipReassessmentPrompt` uses, so a caller (or
    a test) can inspect what went into the body without re-parsing it.
    """

    login: str
    conduct_adviser: str
    body: str


def onboarding_checklist(login: str, *, conduct_adviser: str | None = None) -> OnboardingChecklist:
    """Render the onboarding-checklist issue body for `login`.

    Names the external conduct adviser and the fairness rules (§12.1:
    "every joiner learns, in writing and on day one, who the conduct
    adviser is") and renders the seven §12.7 milestone bands verbatim.
    `conduct_adviser` defaults to `CONDUCT_ADVISER_PLACEHOLDER` -- this
    function never invents a real person's name or contact detail.
    """
    adviser = conduct_adviser or CONDUCT_ADVISER_PLACEHOLDER
    lines = [
        f"# Onboarding -- {login}",
        "",
        "## Who protects you (§12.1, §81.8) -- read on day one",
        f"- [ ] External conduct adviser contact read and acknowledged: {adviser}",
        "- [ ] §81.8 fairness rules read and acknowledged",
        "",
        "## Lifecycle (§12.1)",
        "- [ ] Self-view encryption key exchanged in person",
        "",
        "## Milestone targets (§12.7 -- rendered automatically)",
        "| Milestone | Target band |",
        "| --- | --- |",
    ]
    lines.extend(f"| {milestone} | {band} |" for milestone, band in MILESTONE_BANDS)
    lines.append("")
    body = "\n".join(lines) + "\n"
    return OnboardingChecklist(login=login, conduct_adviser=adviser, body=body)
