"""L3-P7-05: temporary-person expiry treated as an exit (spec 12.2, 12.4; AT-008)."""

from __future__ import annotations

from datetime import date

from reconciler.orphans import OrphanContext
from tools.provision.plan import StepKind
from tools.provision.remove_person import REMOVE_PERSON_STEPS, build_remove_person_plan
from tools.provision.temp_expiry import on_expiry, raise_type_14_if_applicable


def _ctx(open_gate_items=()) -> OrphanContext:
    return OrphanContext(
        fixture_name="test",
        as_of=date(2026, 8, 27),
        people=[{"github_login": "qa-1", "availability": "departing", "end_date": "2026-08-27"}],
        products={},
        shared_services=[],
        assets=[],
        board_items=[],
        open_gate_items=list(open_gate_items),
        migrations=[],
        policies=[],
        exceptions=[],
    )


def test_expiry_produces_the_identical_eleven_step_plan_as_remove_person():
    expiry_plan = on_expiry("qa-1", "2026-08-27")
    remove_plan = build_remove_person_plan("qa-1")
    assert [s.id for s in expiry_plan.steps] == [s.id for s in remove_plan.steps]
    assert [s.id for s in expiry_plan.steps] == list(REMOVE_PERSON_STEPS)
    assert len(expiry_plan.steps) == 11


def test_expiry_accepts_a_date_object_too():
    plan = on_expiry("qa-1", date(2026, 8, 27))
    assert len(plan.steps) == 11


def test_orphan_type_14_raised_when_open_gate_work_is_held_at_expiry():
    ctx = _ctx(open_gate_items=[{"id": "GATE-7", "assignee": "qa-1"}])
    finding = raise_type_14_if_applicable(ctx, "qa-1", date(2026, 8, 27))
    assert finding is not None
    assert finding.index == 14
    assert finding.name == "Temporary person expired with open gate-relevant work"
    assert finding.subject == "qa-1"


def test_no_type_14_when_no_open_gate_work_is_held():
    ctx = _ctx(open_gate_items=[{"id": "GATE-7", "assignee": "someone-else"}])
    assert raise_type_14_if_applicable(ctx, "qa-1", date(2026, 8, 27)) is None


def test_no_type_14_when_there_is_no_open_gate_work_at_all():
    ctx = _ctx(open_gate_items=[])
    assert raise_type_14_if_applicable(ctx, "qa-1", date(2026, 8, 27)) is None


def test_expiry_plan_requires_no_human_action_to_execute():
    # AT-008: reconciliation revokes on the end date without human
    # action - no step in the plan is a manual (human-carried) step.
    plan = on_expiry("qa-1", "2026-08-27")
    assert plan.count(StepKind.MANUAL) == 0
    assert plan.summary_line("remove-person") == "PLAN remove-person steps=11 writes=0 manual=0"
