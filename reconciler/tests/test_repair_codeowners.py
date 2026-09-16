"""L3-P6-04: repair class: CODEOWNERS regeneration."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest

from reconciler.cli import DeclaredState
from reconciler.comparators.codeowners import compare
from reconciler.repair import codeowners_regen
from reconciler.state.fixture_adapter import FixtureState
from tools.provision.codeowners import MachineIdentityInCodeowners, generate


def _fixture_a_findings():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, _ = compare(declared, actual, date(2026, 8, 27))
    return findings, actual


def test_fixture_a_alpha_regeneration_removes_ci_bot_and_matches_generate():
    findings, actual = _fixture_a_findings()
    repairs = codeowners_regen.repair(findings, actual, "fixture-a", enabled=True)
    by_scope = {r.scope: r for r in repairs}
    assert "alpha" in by_scope
    alpha = by_scope["alpha"]
    assert "@ci-bot" not in alpha.after
    assert alpha.after == generate("alpha", "fixture-a")
    assert "ci-bot" in alpha.before  # the pre-repair file really did have it


def test_disabled_class_yields_no_repairs():
    findings, actual = _fixture_a_findings()
    repairs = codeowners_regen.repair(findings, actual, "fixture-a", enabled=False)
    assert repairs == []


def test_unrelated_finding_comparator_is_ignored():
    class FakeActual:
        def codeowners(self, repo):
            raise AssertionError("should never be read for a non-codeowners finding")

    from reconciler.model import DriftClass, Level, Finding

    other = Finding(
        id="team_membership:alpha:dev-2:unassigned",
        comparator="team_membership",
        scope="alpha:dev-2",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="unrelated",
        first_seen="2026-08-27T00:00:00Z",
    )
    repairs = codeowners_regen.repair([other], FakeActual(), "fixture-a", enabled=True)
    assert repairs == []


def test_machine_identity_in_declared_raises_and_produces_no_repair():
    findings, actual = _fixture_a_findings()
    alpha_only = [f for f in findings if f.scope == "alpha"]
    with patch("reconciler.repair.codeowners_regen.generate", side_effect=MachineIdentityInCodeowners("boom")):
        with pytest.raises(MachineIdentityInCodeowners):
            codeowners_regen.repair(alpha_only, actual, "fixture-a", enabled=True)


def test_calls_permitted_before_repairing():
    findings, actual = _fixture_a_findings()
    with patch("reconciler.repair.codeowners_regen.permitted", wraps=codeowners_regen.permitted) as spy:
        repairs = codeowners_regen.repair(findings, actual, "fixture-a", enabled=True)
    assert spy.call_count == len(findings)
    assert repairs  # sanity: the mocked-through call still produced repairs


def test_repair_result_shape_has_required_fields():
    findings, actual = _fixture_a_findings()
    repairs = codeowners_regen.repair(findings, actual, "fixture-a", enabled=True)
    for r in repairs:
        assert r.repair_class == "codeowners_regen"
        assert r.before
        assert r.after
        assert r.permitted_reason
        assert r.compensating_action
