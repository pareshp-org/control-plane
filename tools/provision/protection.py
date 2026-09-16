"""L3-P4-03: branch-protection applier from template.

Spec basis: Section 11.3's ten-bullet checklist; Section 98.2 Phase 1
("The required-status-check list starts empty per repository"); §64.1.

`plan_protection(repo, template)` plans one step per §11.3 bullet, in
the order printed there:

    1. require a pull request
    2. require at least 1 approving review
    3. require review from Code Owners
    4. require approval of the most recent reviewable push
    5. dismiss stale approvals
    6. require status checks to pass
    7. require branches up to date
    8. block force pushes and deletions on the default branch
    9. apply rules to administrators
    10. apply the environment deployment branch and tag policy

`template` names a fixture (e.g. `"fixture-a"`), loaded the same way
every other Phase-4 planner loads declared state
(`tools/provision/teams.py`'s `registries` argument): through
`reconciler.cli.DeclaredState`, reading
`declared/templates/branch-protection.json`.

Bullet 6 is never emitted as an ordinary write step. Section 98.2
Phase 1 is explicit: *"A required check no workflow emits blocks every
pull request indefinitely; a list that silently stays empty is a gate
that reads armed and is not."* So the `required_status_checks.contexts`
list this plan would apply is **always empty at creation** --
`ProtectionPlan.contexts == []` regardless of what the template
eventually wants -- and bullet 6 is instead a `manual` step recording
the context names the repository still owes, so that debt is never
silently missing from the plan (Section 19.1).

Like every Phase-4 planner (`tools/provision/plan.py`), this module
only ever plans. Nothing here calls the GitHub API, and no step ever
removes or weakens an existing protection setting (safety rule 2) --
each step only ever *adds* a restriction relative to an unprotected
repository; there is no "loosen" or "remove" step in this checklist.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from reconciler.cli import DeclaredState
from tools.provision.plan import Step, StepKind


@dataclass
class ProtectionPlan:
    """The plan `plan_protection` returns.

    `steps` is the ordered ten-bullet plan. `contexts` is the
    `required_status_checks.contexts` list this plan would actually
    apply at creation -- always empty (Section 98.2 Phase 1); the
    context names the template eventually wants live only in bullet
    6's manual-step description, never here.
    """

    steps: list[Step] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.steps)


def plan_protection(repo: str, template: str) -> ProtectionPlan:
    declared = DeclaredState(template)
    tmpl = declared.templates.get("branch-protection", {})
    owed_contexts = list((tmpl.get("required_status_checks") or {}).get("contexts") or [])

    steps = [
        Step(
            "require-pull-request",
            f"{repo}: require a pull request before merging",
            StepKind.WRITE,
        ),
        Step(
            "require-approving-review",
            f"{repo}: require at least 1 approving review",
            StepKind.WRITE,
        ),
        Step(
            "require-code-owner-review",
            f"{repo}: require review from Code Owners",
            StepKind.WRITE,
        ),
        Step(
            "require-last-push-approval",
            f"{repo}: require approval of the most recent reviewable push",
            StepKind.WRITE,
        ),
        Step(
            "dismiss-stale-reviews",
            f"{repo}: dismiss stale approvals on new commits",
            StepKind.WRITE,
        ),
        Step(
            "require-status-checks",
            f"{repo}: require status checks to pass before merging - "
            f"required_status_checks.contexts starts empty (§98.2 Phase 1); "
            f"owed contexts still to populate as each check comes into "
            f"existence: {owed_contexts}",
            StepKind.MANUAL,
        ),
        Step(
            "require-branches-up-to-date",
            f"{repo}: require branches to be up to date before merging",
            StepKind.WRITE,
        ),
        Step(
            "block-force-push-and-deletions",
            f"{repo}: block force pushes and deletions on the default branch",
            StepKind.WRITE,
        ),
        Step(
            "apply-to-administrators",
            f"{repo}: apply rules to administrators",
            StepKind.WRITE,
        ),
        Step(
            "apply-environment-deploy-policy",
            f"{repo}: apply the environment deployment branch and tag policy",
            StepKind.WRITE,
        ),
    ]

    return ProtectionPlan(steps=steps, contexts=[])
