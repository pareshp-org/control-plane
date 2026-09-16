"""L3-P1-11: Renovate bypass ruleset split comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.renovate_bypass import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_only_the_guard_ruleset_is_flagged():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].scope == "renovate-B"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_pull_request_ruleset_with_bypass_actor_is_never_flagged():
    class FakeActual:
        def rulesets(self):
            return [{"name": "pr-ruleset", "rules": ["pull_request"], "bypass_actors": ["renovate[bot]"]}]

    findings, compared = compare(None, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_guard_ruleset_with_no_bypass_actors_is_clean():
    class FakeActual:
        def rulesets(self):
            return [{"name": "guard", "rules": ["required_status_checks:renovate-path-guard"], "bypass_actors": []}]

    findings, _ = compare(None, FakeActual(), date(2026, 8, 27))
    assert findings == []
