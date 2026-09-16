"""L3-P6-03: repair class: Team membership sync from the registries."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from reconciler.cli import DeclaredState
from reconciler.comparators.team_membership import compare
from reconciler.model import DriftClass, Finding, Level
from reconciler.repair import team_sync
from reconciler.state.fixture_adapter import FixtureState

AS_OF = date(2026, 8, 27)


def _fixture_a_team_findings():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, _ = compare(declared, actual, AS_OF)
    return findings


def test_fixture_a_one_repair_when_enabled():
    findings = _fixture_a_team_findings()
    repairs = team_sync.repair(findings, enabled=True)
    assert len(repairs) == 1
    assert repairs[0].scope == "alpha:dev-2"
    assert repairs[0].after == {"team_member": False}
    assert repairs[0].repair_class == "team_sync"


def test_fixture_a_zero_repairs_when_disabled_and_finding_remains_open():
    findings = _fixture_a_team_findings()
    repairs = team_sync.repair(findings, enabled=False)
    assert repairs == []
    still_findings = _fixture_a_team_findings()
    assert len(still_findings) == 1
    assert still_findings[0].drift_class == DriftClass.BLOCKING


def test_missing_holder_produces_add_repair():
    finding = Finding(
        id="team_membership:gamma:owner-1:missing",
        comparator="team_membership",
        scope="gamma:owner-1",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="owner-1 holds an assignment on gamma but is missing from its Team",
        first_seen="2026-08-27T00:00:00Z",
    )
    repairs = team_sync.repair([finding], enabled=True)
    assert len(repairs) == 1
    assert repairs[0].after == {"team_member": True}
    assert repairs[0].before == {"team_member": False}


def test_unrelated_finding_id_suffix_is_ignored():
    finding = Finding(
        id="team_membership:gamma:owner-1:something_else",
        comparator="team_membership",
        scope="gamma:owner-1",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="n/a",
        first_seen="2026-08-27T00:00:00Z",
    )
    assert team_sync.repair([finding], enabled=True) == []


def test_finding_from_a_different_comparator_is_ignored():
    finding = Finding(
        id="codeowners:alpha:hand_edited",
        comparator="codeowners",
        scope="alpha",
        drift_class=DriftClass.AMBER,
        level=Level.WARN,
        evidence="n/a",
        first_seen="2026-08-27T00:00:00Z",
    )
    assert team_sync.repair([finding], enabled=True) == []


def test_every_repair_calls_permitted():
    findings = _fixture_a_team_findings()
    with patch("reconciler.repair.team_sync.permitted", wraps=team_sync.permitted) as spy:
        repairs = team_sync.repair(findings, enabled=True)
    assert spy.call_count == len(findings)
    assert repairs


def test_repair_result_shape_has_required_fields():
    findings = _fixture_a_team_findings()
    repairs = team_sync.repair(findings, enabled=True)
    for r in repairs:
        assert r.repair_class == "team_sync"
        assert r.before
        assert r.after
        assert r.permitted_reason
        assert r.compensating_action
