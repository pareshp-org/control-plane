"""L3-P1-10: platform.yaml workflow tag to resolved SHA comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.workflow_tag_sha import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_one_finding_no_gradation():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 1
    assert len(findings) == 1
    assert findings[0].scope == "workflows/v3"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_matching_sha_produces_no_finding():
    class FakeActual:
        def resolve_tag(self, tag):
            return "same-sha"

    fake_declared = type(
        "D", (), {"platform": {"workflow_tags": [{"tag": "t", "sha": "same-sha"}]}}
    )()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1
