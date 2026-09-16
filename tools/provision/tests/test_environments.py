"""Tests for L3-P4-04: environments and deployment branch/tag policy applier."""

from __future__ import annotations

import pytest

from tools.provision.environments import (
    EnvironmentStep,
    ForbiddenWriteError,
    _reject_forbidden_steps,
    plan_environments,
)
from tools.provision.plan import StepKind


def test_three_environments_planned():
    plan = plan_environments("gamma", "fixture-a")
    create_ids = {s.id for s in plan.steps if s.id.startswith("create-environment-")}
    assert create_ids == {
        "create-environment-development",
        "create-environment-staging",
        "create-environment-production",
    }


def test_staging_and_production_carry_deployment_branch_tag_policy():
    plan = plan_environments("gamma", "fixture-a")
    policy_ids = {s.id for s in plan.steps if s.id.startswith("deployment-branch-tag-policy-")}
    assert policy_ids == {
        "deployment-branch-tag-policy-staging",
        "deployment-branch-tag-policy-production",
    }


def test_development_carries_no_policy_step():
    plan = plan_environments("gamma", "fixture-a")
    assert "deployment-branch-tag-policy-development" not in {s.id for s in plan.steps}


def test_no_step_is_ever_forbidden():
    plan = plan_environments("gamma", "fixture-a")
    assert all(step.forbidden is False for step in plan.steps)


def test_policy_step_reflects_the_template_values():
    plan = plan_environments("gamma", "fixture-a")
    staging = next(s for s in plan.steps if s.id == "deployment-branch-tag-policy-staging")
    assert "protected_branches=True" in staging.description
    assert "custom_branch_policies=False" in staging.description


def test_a_forbidden_step_raises():
    forbidden_step = EnvironmentStep(
        id="assign-approver",
        description="gamma/production: assign an approver ahead of time",
        kind=StepKind.WRITE,
        forbidden=True,
    )
    with pytest.raises(ForbiddenWriteError):
        _reject_forbidden_steps([forbidden_step])
