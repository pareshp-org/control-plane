"""L3-P1-03: capability vs team-implied authority comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.capability_authority import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_one_amber_finding():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 5
    assert len(findings) == 1
    assert findings[0].scope == "dev-2"
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN


def test_person_with_authority_capability_is_clean():
    class FakeActual:
        def team_members(self, product):
            return ["reviewer-1"]

    class FakeDeclared:
        people = [{"github_login": "reviewer-1", "capabilities": ["code-review"]}]
        products = {"alpha": {}}

    findings, compared = compare(FakeDeclared(), FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_person_not_on_any_team_is_never_flagged():
    class FakeActual:
        def team_members(self, product):
            return []

    class FakeDeclared:
        people = [{"github_login": "outsider-1", "capabilities": []}]
        products = {"alpha": {}}

    findings, _ = compare(FakeDeclared(), FakeActual(), date(2026, 8, 27))
    assert findings == []
