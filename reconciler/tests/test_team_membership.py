"""L3-P1-04: product.yaml assignments vs GitHub Team membership comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.team_membership import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_one_finding():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].scope == "alpha:dev-2"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_expired_temporary_assignment_does_not_count_toward_declared_team():
    class FakeActual:
        def team_members(self, product):
            return []

    fake_declared = type(
        "D",
        (),
        {
            "products": {
                "gamma": {
                    "assignments": {},
                    "temporary_assignments": [
                        {"person": "temp-1", "end_date": "2020-01-01"},
                    ],
                }
            }
        },
    )()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_missing_holder_from_team_is_flagged():
    class FakeActual:
        def team_members(self, product):
            return []

    fake_declared = type(
        "D",
        (),
        {"products": {"gamma": {"assignments": {"primary_owner": "owner-1"}}}},
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert "missing from its Team" in findings[0].evidence
