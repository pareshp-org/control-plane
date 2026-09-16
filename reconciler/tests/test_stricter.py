"""L3-P6-01: the stricter-only predicate's proof suite (spec 53.3;
invariant 81; AT-033). Twelve cases: declared-stricter and
declared-looser for each of a branch-protection dict, a plain boolean
flag, a numeric threshold and a required-contexts list, the equal
(no-repair) case, and the three category-based absolute refusals."""

from __future__ import annotations

from reconciler.model import Level
from reconciler.repair.stricter import classify_level, permitted


def test_branch_protection_dict_declared_stricter_is_permitted():
    declared = {"require_code_owner_reviews": True}
    actual = {"require_code_owner_reviews": False}
    ok, reason = permitted(declared, actual, "branch_protection")
    assert ok is True
    assert reason == ""


def test_branch_protection_dict_declared_looser_is_refused_and_warns():
    declared = {"require_code_owner_reviews": False}
    actual = {"require_code_owner_reviews": True}
    ok, reason = permitted(declared, actual, "branch_protection")
    assert ok is False
    assert "AT-033" in reason
    assert classify_level(declared, actual, "branch_protection") == Level.WARN


def test_equal_declared_and_actual_is_no_repair():
    ok, reason = permitted({"x": 1}, {"x": 1}, "branch_protection")
    assert ok is False
    assert "nothing to repair" in reason
    assert classify_level({"x": 1}, {"x": 1}, "branch_protection") == Level.DETECT


def test_absolute_refusal_production_runtime_config():
    ok, reason = permitted("v2", "v1", "production_runtime_config")
    assert ok is False
    assert "production_runtime_config" in reason


def test_absolute_refusal_data():
    ok, reason = permitted({"row": 2}, {"row": 1}, "data")
    assert ok is False
    assert "data" in reason


def test_absolute_refusal_secret():
    ok, reason = permitted({"x": 1}, {"x": 0}, "secret")
    assert ok is False
    assert "secret" in reason


def test_boolean_flag_declared_true_actual_false_is_permitted():
    ok, _ = permitted(True, False, "boolean_flag")
    assert ok is True


def test_boolean_flag_declared_false_actual_true_is_refused():
    ok, reason = permitted(False, True, "boolean_flag")
    assert ok is False
    assert "AT-033" in reason


def test_numeric_threshold_declared_higher_is_permitted():
    ok, _ = permitted(2, 1, "numeric_threshold")
    assert ok is True


def test_numeric_threshold_declared_lower_is_refused():
    ok, reason = permitted(1, 2, "numeric_threshold")
    assert ok is False
    assert "AT-033" in reason


def test_context_list_declared_superset_is_permitted():
    ok, _ = permitted(["a", "b"], ["a"], "context_list")
    assert ok is True


def test_context_list_declared_subset_is_refused():
    ok, reason = permitted(["a"], ["a", "b"], "context_list")
    assert ok is False
    assert "AT-033" in reason
