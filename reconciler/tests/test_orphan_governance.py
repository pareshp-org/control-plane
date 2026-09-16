"""L3-P2-04: orphan detectors 11-16 (migration, verification, H1,
temporary expiry, policy, exception)."""

from __future__ import annotations

from datetime import date

from reconciler.orphans import load_context
from reconciler.orphans.governance import detect


def _ctx(as_of=date(2026, 8, 27)):
    return load_context("fixture-a", as_of)


def test_fixture_a_exactly_five_findings():
    findings, compared = detect(_ctx())
    assert len(findings) == 5
    by_index = {f.index: f for f in findings}
    assert set(by_index) == {12, 13, 14, 15, 16}
    assert by_index[12].subject == "beta"
    assert by_index[13].subject == "WI-101"
    assert by_index[14].subject == "dev-1"
    assert by_index[15].subject == "POL-001"
    assert by_index[16].subject == "EXC-001"


def test_migration_with_an_active_owner_produces_no_finding():
    findings, _ = detect(_ctx())
    assert not any(f.index == 11 for f in findings)


def test_h1_item_with_an_active_assignee_produces_no_finding():
    findings, _ = detect(_ctx())
    assert not any(f.subject == "WI-102" for f in findings)


def test_compared_is_the_fixed_six_types():
    _, compared = detect(_ctx())
    assert compared == 6


def test_temp_expiry_is_not_yet_orphaned_before_end_date():
    # dev-1's temporary_contributor assignment on alpha ends 2026-01-31.
    # As-of a date before that, it has not expired and type 14 must not fire.
    findings, _ = detect(_ctx(as_of=date(2026, 1, 1)))
    assert not any(f.index == 14 for f in findings)
