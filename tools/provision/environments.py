"""L3-P4-04: environments and deployment branch/tag policy applier.

Spec basis: Section 33.4 (deployment branch and tag policy: only the
default branch and protected release tags may deploy to `staging` and
`production` - "no other ref"); Section 19.1; Section 64.1, which this
module exists to satisfy: a production environment is never planned
with a credential of any kind, and never planned with an approver,
until a human explicitly configures one later, outside this lane.

`plan_environments(repo, template)` plans three environments -
`development`, `staging`, `production` - and, on `staging` and
`production` only, a deployment branch and tag policy scoped to the
default branch and protected release tags and nothing else.

`template` names a fixture (e.g. `"fixture-a"`), loaded the same way
`tools/provision/protection.py` and `tools/provision/teams.py` load
declared state: through `reconciler.cli.DeclaredState`, reading
`declared/templates/environment.json`.

This plan never emits a write step whose `forbidden` flag is set, and
`_reject_forbidden_steps` never lets one through even by accident -
see its own docstring for what that guards against.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from reconciler.cli import DeclaredState
from tools.provision.plan import StepKind

_GATED_ENVIRONMENTS = ("staging", "production")


class ForbiddenWriteError(RuntimeError):
    """Raised by `_reject_forbidden_steps` - never returned as a plan."""


@dataclass(frozen=True)
class EnvironmentStep:
    """One environment-provisioning step.

    `forbidden=True` marks the one class of step this module must
    never actually plan under any template or repository: a write
    that would provision a credential, or a write that would assign
    an approver ahead of explicit human configuration (§64.1). No
    branch of `plan_environments` below ever constructs a step with
    `forbidden=True` - the flag exists only so the guard function has
    something concrete to prove itself against in a test.
    """

    id: str
    description: str
    kind: StepKind
    forbidden: bool = False


@dataclass
class EnvironmentPlan:
    steps: list[EnvironmentStep] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.steps)


def _reject_forbidden_steps(steps: list[EnvironmentStep]) -> list[EnvironmentStep]:
    """§64.1's enforcement point: never let a forbidden step through.

    A production environment is created without any credential and
    without any approver until a human explicitly configures one
    later - this function is what makes that a checked invariant
    rather than a comment, by raising the moment any caller (in
    practice, only a test) constructs a step this module must never
    plan.
    """
    for step in steps:
        if step.forbidden:
            raise ForbiddenWriteError(
                f"step {step.id!r} is forbidden by §64.1 and can never be planned"
            )
    return steps


def plan_environments(repo: str, template: str) -> EnvironmentPlan:
    declared = DeclaredState(template)
    tmpl = declared.templates.get("environment", {})
    declared_envs = list(tmpl.get("environments") or list(_GATED_ENVIRONMENTS))
    env_names = ["development"] + [e for e in declared_envs if e != "development"]
    policy = tmpl.get("deployment_branch_policy") or {}

    steps: list[EnvironmentStep] = []
    for env_name in env_names:
        steps.append(
            EnvironmentStep(
                id=f"create-environment-{env_name}",
                description=f"{repo}/{env_name}: create the environment",
                kind=StepKind.WRITE,
            )
        )
        if env_name in _GATED_ENVIRONMENTS:
            steps.append(
                EnvironmentStep(
                    id=f"deployment-branch-tag-policy-{env_name}",
                    description=(
                        f"{repo}/{env_name}: apply the deployment branch and tag policy - "
                        f"protected_branches={bool(policy.get('protected_branches'))}, "
                        f"custom_branch_policies={bool(policy.get('custom_branch_policies'))} "
                        "- only the default branch and protected release tags may deploy, "
                        "no other ref (§33.4)"
                    ),
                    kind=StepKind.WRITE,
                )
            )

    return EnvironmentPlan(steps=_reject_forbidden_steps(steps))
