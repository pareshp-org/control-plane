"""L3-P1-09: assignment end_date vs current Team membership comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.expiry import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_one_finding_and_no_revocation():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 1
    assert len(findings) == 1
    assert findings[0].scope == "alpha:dev-1"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK
    assert "repair_class=expiry_revoke" in findings[0].evidence
    # detect only - no team-membership mutation method exists to call
    assert not hasattr(actual, "remove_team_member")


def test_expiring_within_14_days_and_still_active_is_amber():
    class FakeActual:
        def team_members(self, product):
            return ["temp-1"]

    fake_declared = type(
        "D",
        (),
        {
            "products": {
                "gamma": {
                    "temporary_assignments": [
                        {"person": "temp-1", "type": "temporary_contributor", "end_date": "2026-09-05"}
                    ]
                }
            }
        },
    )()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert compared == 1
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN


def test_expired_but_already_removed_from_team_is_clean():
    class FakeActual:
        def team_members(self, product):
            return []

    fake_declared = type(
        "D",
        (),
        {
            "products": {
                "gamma": {
                    "temporary_assignments": [
                        {"person": "temp-1", "type": "temporary_contributor", "end_date": "2020-01-01"}
                    ]
                }
            }
        },
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
