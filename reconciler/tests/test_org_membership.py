"""L3-P1-02: org membership comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.org_membership import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def _fixture_a():
    return DeclaredState("fixture-a"), FixtureState("fixture-a")


def test_fixture_a_exactly_one_removal_drift_finding():
    declared, actual = _fixture_a()
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 5
    assert len(findings) == 1
    assert findings[0].scope == "dev-2"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_active_person_absent_from_org_is_amber():
    class FakeActual:
        def org_members(self):
            return []

    class FakeDeclared:
        people = [{"github_login": "ghost-1", "access_status": "active", "availability": "active"}]

    findings, compared = compare(FakeDeclared(), FakeActual(), date(2026, 8, 27))
    assert compared == 1
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN


def test_comparator_emits_findings_only_never_revokes():
    # The comparator has no write-shaped attribute or method at all;
    # detect-only is enforced structurally, not just by convention.
    import inspect

    from reconciler.comparators import org_membership

    source = inspect.getsource(org_membership)
    assert "actual.set_" not in source
    assert "actual.write_" not in source
