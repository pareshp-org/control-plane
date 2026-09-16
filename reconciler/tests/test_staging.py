"""L3-P7-03: registry-edit canary staging (spec 26.4, 61.5)."""

from __future__ import annotations

import pytest

from reconciler.runrecord import RunRecord
from reconciler.staging import RegistryChange, StagingError, stage

CANARY_SET = frozenset({"alpha", "beta"})


def _run(status: str) -> RunRecord:
    return RunRecord(
        run_id="R1",
        started_at="2026-08-27T00:00:00Z",
        finished_at="2026-08-27T00:01:00Z",
        status=status,
        findings=[],
        comparison_counts={},
        canary_found=(status == "OK"),
        external_cause=None,
    )


def _change(*products: str) -> RegistryChange:
    return RegistryChange(id="chg-1", affected_products=frozenset(products))


def test_first_run_applies_to_canary_set_only():
    change = _change("alpha", "beta", "gamma", "delta")
    wave = stage(change, CANARY_SET, last_canary_run=None)
    assert wave == {"alpha", "beta"}


def test_clean_canary_run_releases_fleet():
    change = _change("alpha", "beta", "gamma", "delta")
    wave = stage(change, CANARY_SET, last_canary_run=_run("OK"))
    assert wave == change.affected_products


def test_failed_canary_run_holds_fleet():
    change = _change("alpha", "beta", "gamma", "delta")
    wave = stage(change, CANARY_SET, last_canary_run=_run("FAILED"))
    assert wave == {"alpha", "beta"}


def test_canary_missing_run_counts_as_failed_and_holds_fleet():
    # A canary-missing run is forced to status "FAILED" upstream
    # (reconciler.cli + L3-P1-17's zero-findings FAIL rule, AT-102).
    # staging.py does not re-derive canary presence - it just reads
    # `.status`, so a FAILED run for any reason holds the fleet.
    change = _change("alpha", "beta", "gamma")
    missing_canary_run = _run("FAILED")
    assert missing_canary_run.canary_found is False
    wave = stage(change, CANARY_SET, last_canary_run=missing_canary_run)
    assert wave == {"alpha", "beta"}


def test_bootstrap_flag_does_not_bypass_the_first_run_hold():
    change = _change("alpha", "beta", "gamma", "delta")
    normal = stage(change, CANARY_SET, last_canary_run=None, bootstrap=False)
    bootstrapped = stage(change, CANARY_SET, last_canary_run=None, bootstrap=True)
    assert normal == bootstrapped == {"alpha", "beta"}


def test_bootstrap_flag_does_not_bypass_the_failed_hold():
    change = _change("alpha", "beta", "gamma", "delta")
    normal = stage(change, CANARY_SET, last_canary_run=_run("FAILED"), bootstrap=False)
    bootstrapped = stage(change, CANARY_SET, last_canary_run=_run("FAILED"), bootstrap=True)
    assert normal == bootstrapped == {"alpha", "beta"}


def test_empty_canary_set_fails_closed():
    change = _change("alpha", "beta")
    with pytest.raises(StagingError):
        stage(change, canary_set=frozenset(), last_canary_run=None)


def test_change_not_touching_any_canary_product_still_gated_by_last_run():
    # The change's own scope never overlaps the declared canary set -
    # wave 1 is legitimately empty, and a clean prior cycle still
    # releases the (canary-less) fleet in full.
    change = _change("gamma", "delta")
    assert stage(change, CANARY_SET, last_canary_run=None) == frozenset()
    assert stage(change, CANARY_SET, last_canary_run=_run("OK")) == {"gamma", "delta"}
