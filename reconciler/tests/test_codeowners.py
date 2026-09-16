"""L3-P1-05: assignments vs CODEOWNERS comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.codeowners import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_two_findings():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    by_scope = {f.scope: f for f in findings}
    assert set(by_scope) == {"alpha", "beta"}
    assert by_scope["alpha"].id.endswith("machine_identity_present")
    assert by_scope["alpha"].drift_class == DriftClass.BLOCKING
    assert by_scope["alpha"].level == Level.BLOCK
    assert by_scope["beta"].id.endswith("hand_edited")
    assert by_scope["beta"].drift_class == DriftClass.AMBER
    assert by_scope["beta"].level == Level.WARN


def test_machine_identity_suppresses_hand_edited_for_same_repo():
    class FakeActual:
        def codeowners(self, repo):
            return "* @lead-1 @ci-bot[bot]\n"

    fake_declared = type(
        "D",
        (),
        {
            "people": [{"github_login": "lead-1"}],
            "products": {"solo": {"assignments": {"primary_owner": "lead-1"}}},
        },
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].id.endswith("machine_identity_present")


def test_generated_content_matching_actual_produces_no_finding():
    class FakeActual:
        def codeowners(self, repo):
            return "* @lead-1\n"

    fake_declared = type(
        "D",
        (),
        {
            "people": [{"github_login": "lead-1"}],
            "products": {"solo": {"assignments": {"primary_owner": "lead-1"}}},
        },
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
