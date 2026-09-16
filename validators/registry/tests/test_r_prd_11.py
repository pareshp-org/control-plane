"""Tests for R-PRD-11, R-PRD-27, R-PRD-28 (L1-311, §47.9, AT-047).

Exercised by calling ``validators.registry.rules.r_prd_11`` directly
against parsed ``product.yaml`` / ``people.yaml`` fixture pairs, rather
than through ``validators/registry/cli.py`` -- see the module docstring
of ``r_prd_11.py`` and, for precedent, ``test_service_schema.py``'s own
note that FD-094 supersedes the CLI grammar and ``echo "AT047_EXIT=$?"``
acceptance command written into ``lanes/L1-05-tasks.md``.

10 test functions: 3 valid, 7 invalid, matching the task's own fixture-case
table exactly.
"""
import os

import yaml

from validators.registry.rules import r_prd_11

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "product", "rota")


def _load(case, filename):
    path = os.path.join(FIXTURES_DIR, case, filename)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _product(case):
    return _load(case, "product.yaml")


def _people(case):
    return _load(case, "people.yaml")


def _findings(case):
    return r_prd_11.check(_product(case), _people(case))


# ---------------------------------------------------------------------------
# valid (3)
# ---------------------------------------------------------------------------


def test_valid_extended_fully_covered():
    case = os.path.join("valid", "extended_fully_covered")
    assert _findings(case) == []


def test_valid_24x7_three_shifts():
    case = os.path.join("valid", "24x7_three_shifts")
    assert _findings(case) == []


def test_valid_business_hours_no_rota():
    case = os.path.join("valid", "business_hours_no_rota")
    # business-hours is not in {extended, 24x7} -- the rule does not
    # apply at all, regardless of the (empty) rota.
    assert _findings(case) == []


# ---------------------------------------------------------------------------
# invalid (7)
# ---------------------------------------------------------------------------


def test_extended_gap_one_hour_triggers_r_prd_11():
    case = os.path.join("invalid", "extended_gap_one_hour")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-11" in findings[0]
    assert "not fully covered" in findings[0]
    assert "Section 47.9 fails closed" in findings[0]


def test_24x7_empty_rota_triggers_r_prd_28_only():
    case = os.path.join("invalid", "24x7_empty_rota")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-28" in findings[0]
    assert "24x7 support cannot be onboarded without a funded rota" in findings[0]
    assert "Section 15.6 onboarding blocker, invariant 31" in findings[0]


def test_member_no_work_arrangement_triggers_r_prd_27():
    case = os.path.join("invalid", "member_no_work_arrangement")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-27" in findings[0]
    assert "rota-a" in findings[0]
    assert "no work_arrangement" in findings[0]
    assert "fails closed where a member has no work arrangement" in findings[0]


def test_member_window_too_narrow_triggers_r_prd_11():
    case = os.path.join("invalid", "member_window_too_narrow")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-11" in findings[0]
    assert "not fully covered" in findings[0]


def test_member_departed_triggers_r_prd_11():
    case = os.path.join("invalid", "member_departed")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-11" in findings[0]


def test_member_on_leave_counted_triggers_r_prd_11():
    # Section 47.9 counts only availability: active -- an on_leave member
    # must NOT be counted toward the union, even though their window is
    # otherwise valid.
    case = os.path.join("invalid", "member_on_leave_counted")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-11" in findings[0]


def test_timezone_mismatch_uncovered_triggers_r_prd_11():
    # The member's accepted_window uses the product's coverage_window's
    # clock digits but a different IANA timezone -- correct §7.3 window
    # arithmetic (resolved in the product's declared timezone) must not
    # be fooled into treating this as covered.
    case = os.path.join("invalid", "timezone_mismatch_uncovered")
    findings = _findings(case)
    assert len(findings) == 1
    assert "R-PRD-11" in findings[0]
    assert "not fully covered" in findings[0]
