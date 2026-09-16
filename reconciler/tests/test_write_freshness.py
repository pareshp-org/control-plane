"""L3-P1-14: record-store write freshness comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.write_freshness import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_only_deployments_is_stale_and_blocking():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 3
    assert len(findings) == 1
    assert findings[0].scope == "records/deployments/"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_non_blocking_store_past_window_is_amber():
    class FakeActual:
        def store_last_write(self):
            return {"registries/": "2026-08-01T00:00:00Z"}

    fake_declared = type(
        "D", (), {"os_health": {"write_freshness_max_hours": {"registries/": 24}}}
    )()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert compared == 1
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN


def test_same_day_write_is_never_stale():
    class FakeActual:
        def store_last_write(self):
            return {"events/": "2026-08-27T23:59:00Z"}

    fake_declared = type(
        "D", (), {"os_health": {"write_freshness_max_hours": {"events/": 1}}}
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
