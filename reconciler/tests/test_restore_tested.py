"""L3-P1-15: restore_tested vs restore-test records comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.restore_tested import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_only_beta_is_unevidenced():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].scope == "beta"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_matching_passing_record_is_clean():
    class FakeActual:
        def restore_test_records(self):
            return [{"product": "solo", "date": "2026-08-01", "result": "pass"}]

    fake_declared = type(
        "D", (), {"products": {"solo": {"restore_tested": "2026-08-01"}}}
    )()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_matching_date_but_failed_result_is_still_a_finding():
    class FakeActual:
        def restore_test_records(self):
            return [{"product": "solo", "date": "2026-08-01", "result": "fail"}]

    fake_declared = type(
        "D", (), {"products": {"solo": {"restore_tested": "2026-08-01"}}}
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
