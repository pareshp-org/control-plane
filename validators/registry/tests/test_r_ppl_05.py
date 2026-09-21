"""Tests for R-PPL-05, R-PPL-09, R-PPL-10, R-PPL-11, R-PPL-12 (L1-207,
Section 7.3, D111).

Exercised by calling ``validators.registry.rules.r_ppl_05`` directly
against a parsed ``people.yaml`` fixture, rather than through
``validators/registry/cli.py`` -- see the module docstring of
``r_ppl_05.py`` and, for precedent, ``test_service_schema.py`` /
``test_r_prd_11.py``'s own notes that FD-094 (DECIDED) supersedes the
CLI grammar and ``echo "EXIT=$?"`` acceptance commands written into
``lanes/L1-05-tasks.md``.

13 test functions: 5 valid, 8 invalid, matching the task's own fixture-case
list exactly.
"""
import os

import yaml

from validators.registry.rules import r_ppl_05

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "ppl05")


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "people.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _findings(case):
    return r_ppl_05.check(_load(case))


# ---------------------------------------------------------------------------
# valid (5)
# ---------------------------------------------------------------------------


def test_valid_full_week():
    case = os.path.join("valid", "full_week")
    assert _findings(case) == []


def test_valid_part_time_three_days():
    case = os.path.join("valid", "part_time_three_days")
    assert _findings(case) == []


def test_valid_departed_no_arrangement():
    # departed with no work_arrangement never fires R-PPL-12 -- it applies
    # to active people only.
    case = os.path.join("valid", "departed_no_arrangement")
    assert _findings(case) == []


def test_valid_fte_point_six_valid():
    # Section 7.3: "fte is a capacity multiplier, not a status" -- fte=0.6
    # alone must not trigger any rule here.
    case = os.path.join("valid", "fte_point_six_valid")
    assert _findings(case) == []


def test_valid_weekend_only_schedule():
    # Section 7.3: "omit a day to declare it non-working" -- a schedule
    # naming only sat/sun is a complete, valid working calendar.
    case = os.path.join("valid", "weekend_only_schedule")
    assert _findings(case) == []


# ---------------------------------------------------------------------------
# invalid (8)
# ---------------------------------------------------------------------------


def test_utc_offset_triggers_r_ppl_05():
    findings = _findings("utc_offset")
    assert len(findings) == 1
    assert "R-PPL-05" in findings[0]
    assert "+05:30" in findings[0]
    assert "is not an IANA identifier" in findings[0]
    assert "Section 7.3 forbids UTC offsets" in findings[0]


def test_no_slash_timezone_triggers_r_ppl_05():
    findings = _findings("no_slash_timezone")
    assert len(findings) == 1
    assert "R-PPL-05" in findings[0]
    assert "PST" in findings[0]
    assert "is not an IANA identifier" in findings[0]


def test_end_before_start_triggers_r_ppl_09():
    findings = _findings("end_before_start")
    assert len(findings) == 1
    assert "R-PPL-09" in findings[0]
    assert "'mon'" in findings[0]
    assert "ends at or before it starts" in findings[0]


def test_end_equals_start_triggers_r_ppl_09():
    findings = _findings("end_equals_start")
    assert len(findings) == 1
    assert "R-PPL-09" in findings[0]
    assert "'mon'" in findings[0]
    assert "ends at or before it starts" in findings[0]


def test_empty_schedule_triggers_r_ppl_10():
    findings = _findings("empty_schedule")
    assert len(findings) == 1
    assert "R-PPL-10" in findings[0]
    assert "declares no working days" in findings[0]
    assert "Section 7.3 requires a working calendar" in findings[0]


def test_coverage_window_without_schedule_triggers_r_ppl_11_only():
    # R-PPL-10's generic "no working days" condition also holds here, but
    # R-PPL-11 reports the more specific problem instead -- never both.
    findings = _findings("coverage_window_without_schedule")
    assert len(findings) == 1
    assert "R-PPL-11" in findings[0]
    assert "R-PPL-10" not in findings[0]
    assert "no working calendar to resolve it against" in findings[0]


def test_active_without_arrangement_triggers_r_ppl_12():
    findings = _findings("active_without_arrangement")
    assert len(findings) == 1
    assert "R-PPL-12" in findings[0]
    assert "has no work_arrangement" in findings[0]
    assert "Section 47.9 fails closed without it" in findings[0]


def test_two_bad_days_triggers_r_ppl_09_twice():
    findings = _findings("two_bad_days")
    assert len(findings) == 2
    assert all("R-PPL-09" in f for f in findings)
    assert any("'mon'" in f for f in findings)
    assert any("'tue'" in f for f in findings)
    assert not any("'wed'" in f for f in findings)
