"""L3-P4-07: the `create-product` orchestrator (spec §19.1; §12.6; AT-001)."""

from __future__ import annotations

import re
from pathlib import Path

from tools.provision.create_product import (
    CREATE_PRODUCT_MANUAL_STEPS,
    CREATE_PRODUCT_STEPS,
    build_create_product_plan,
    registered_product_ids,
)
from tools.provision.plan import StepKind


def test_plan_has_exactly_thirteen_automated_steps_in_spec_order():
    plan = build_create_product_plan("gamma", "fixture-a")
    assert [s.id for s in plan.steps] == list(CREATE_PRODUCT_STEPS)
    assert len(plan.steps) == 13


def test_every_automated_step_is_write_kind():
    plan = build_create_product_plan("gamma", "fixture-a")
    assert all(s.kind == StepKind.WRITE for s in plan.steps)


def test_plan_has_exactly_two_manual_steps_in_spec_order():
    plan = build_create_product_plan("gamma", "fixture-a")
    assert [s.id for s in plan.manual_steps] == list(CREATE_PRODUCT_MANUAL_STEPS)
    assert len(plan.manual_steps) == 2
    assert all(s.kind == StepKind.MANUAL for s in plan.manual_steps)


def test_dry_run_summary_line_matches_spec_exactly():
    plan = build_create_product_plan("gamma", "fixture-a")
    assert plan.summary_line("create-product") == "PLAN create-product steps=13 writes=0 manual=2"


def test_manual_steps_never_inflate_the_steps_count():
    # The two manual steps live in `.manual_steps`, never in `.steps` -
    # otherwise `steps=` would read 15, not 13, on a dry run.
    plan = build_create_product_plan("gamma", "fixture-a")
    manual_ids = {s.id for s in plan.manual_steps}
    step_ids = {s.id for s in plan.steps}
    assert manual_ids.isdisjoint(step_ids)


def test_no_product_name_is_hard_coded_in_this_module():
    # Acceptance check, verbatim: `grep -rn "alpha\\|beta"
    # tools/provision/create_product.py` returns nothing.
    source = Path(__file__).resolve().parent.parent / "create_product.py"
    text = source.read_text(encoding="utf-8")
    assert not re.search(r"alpha|beta", text)


def test_registered_product_ids_reads_the_registry_not_a_literal_list():
    # fixture-a declares exactly alpha and beta under declared/products/ -
    # this module learns that by reading the fixture, never by carrying
    # its own copy of the names.
    assert registered_product_ids("fixture-a") == ("alpha", "beta")


def test_registration_steps_reflect_the_registry_count():
    plan = build_create_product_plan("gamma", "fixture-a")
    for step_id in (
        "register_portfolio_board",
        "register_grafana_scorecard_devlake",
        "register_dependency_graph",
    ):
        step = next(s for s in plan.steps if s.id == step_id)
        assert "2 product(s) registered today" in step.description
        assert "gamma would make 3" in step.description


def test_product_yaml_step_names_the_current_contract_version():
    plan = build_create_product_plan("gamma", "fixture-a")
    step = next(s for s in plan.steps if s.id == "product_yaml")
    assert "contract_version=2" in step.description


def test_steps_are_named_for_the_product_being_created():
    plan = build_create_product_plan("gamma", "fixture-a")
    for step in plan.steps:
        assert step.description.startswith("gamma:")
    for step in plan.manual_steps:
        assert step.description.startswith("gamma:")
