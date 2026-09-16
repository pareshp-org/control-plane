"""L3-P1-07: workflow template version vs actual comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.workflow_version import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_one_finding_with_platform_compatibility_token():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].scope == "beta/ci.yml"
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN
    assert "platform_compatibility=drifted" in findings[0].evidence


def test_matching_tag_produces_no_finding():
    class FakeActual:
        def workflow_files(self, product):
            return {"ci.yml": {"uses_tag": "workflows/v3"}}

    fake_declared = type(
        "D", (), {"products": {"solo": {"workflow_tag": "workflows/v3"}}}
    )()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
