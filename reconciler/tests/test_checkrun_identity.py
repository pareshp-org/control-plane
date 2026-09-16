"""Tests for reconciler.comparators.checkrun_identity (L3-P3-03)."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators import checkrun_identity
from reconciler.model import DriftClass
from reconciler.state.fixture_adapter import FixtureState

AS_OF = date(2026, 8, 27)


def _run():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    return checkrun_identity.compare(declared, actual, AS_OF)


def test_fixture_a_flags_only_alpha():
    findings, compared = _run()
    assert [f.scope for f in findings] == ["alpha"]
    assert findings[0].drift_class == DriftClass.BLOCKING


def test_fixture_a_beta_is_clean():
    findings, _ = _run()
    assert all(f.scope != "beta" for f in findings)


def test_compared_counts_every_declared_product():
    _, compared = _run()
    assert compared == 2


def test_missing_check_run_is_not_flagged():
    class _NoCheckRun(FixtureState):
        def check_runs(self, repo):
            return {}

    declared = DeclaredState("fixture-a")
    actual = _NoCheckRun("fixture-a")
    findings, compared = checkrun_identity.compare(declared, actual, AS_OF)
    assert findings == []
    assert compared == 2


def test_reconciler_identity_matches_checkrun_module_default():
    # spec 40.1's one authorised identity must be a single, shared
    # constant - not re-declared inconsistently between the publisher
    # and this identity-assertion comparator.
    from reconciler.checkrun import CHECK_NAME

    assert checkrun_identity.RECONCILER_IDENTITY == "reconciler"
    assert CHECK_NAME == "control-plane/blocking-drift"
