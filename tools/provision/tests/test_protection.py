"""Tests for L3-P4-03: branch-protection applier from template."""

from __future__ import annotations

from tools.provision.plan import StepKind
from tools.provision.protection import plan_protection

_EXPECTED_ORDER = (
    "require-pull-request",
    "require-approving-review",
    "require-code-owner-review",
    "require-last-push-approval",
    "dismiss-stale-reviews",
    "require-status-checks",
    "require-branches-up-to-date",
    "block-force-push-and-deletions",
    "apply-to-administrators",
    "apply-environment-deploy-policy",
)


def test_ten_steps_in_section_11_3_order():
    plan = plan_protection("gamma", "fixture-a")
    assert tuple(step.id for step in plan.steps) == _EXPECTED_ORDER


def test_contexts_empty_at_creation():
    plan = plan_protection("gamma", "fixture-a")
    assert plan.contexts == []


def test_manual_step_records_owed_contexts():
    plan = plan_protection("gamma", "fixture-a")
    manual_steps = [s for s in plan.steps if s.kind == StepKind.MANUAL]
    assert len(manual_steps) == 1
    assert manual_steps[0].id == "require-status-checks"
    assert "control-plane/blocking-drift" in manual_steps[0].description


def test_nine_write_steps_one_manual_step():
    plan = plan_protection("gamma", "fixture-a")
    assert sum(1 for s in plan.steps if s.kind == StepKind.WRITE) == 9
    assert sum(1 for s in plan.steps if s.kind == StepKind.MANUAL) == 1


def test_no_step_weakens_or_removes_protection():
    plan = plan_protection("gamma", "fixture-a")
    forbidden = ("remove", "disable", "loosen", "widen", "relax", "weaken")
    for step in plan.steps:
        lowered = step.description.lower()
        assert not any(word in lowered for word in forbidden), step.description


def test_step_descriptions_reference_the_named_repo():
    plan = plan_protection("gamma", "fixture-a")
    assert all(step.description.startswith("gamma:") for step in plan.steps)


def test_len_matches_step_count():
    plan = plan_protection("gamma", "fixture-a")
    assert len(plan) == 10 == len(plan.steps)
