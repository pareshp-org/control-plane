"""L3-P2-05: prospective orphan mode on `availability: departing`."""

from __future__ import annotations

from datetime import date

from reconciler.orphans import load_context
from reconciler.orphans.prospective import detect


def _ctx():
    return load_context("fixture-a", date(2026, 8, 27))


def test_fixture_a_exactly_two_prospective_findings():
    findings, compared = detect(_ctx())
    assert len(findings) == 2
    by_index = {f.index: f for f in findings}
    assert set(by_index) == {6, 12}
    assert by_index[6].subject == "cert-1"
    assert by_index[12].subject == "alpha"
    assert all(f.prospective is True for f in findings)
    assert all(f.orphans_on == "2026-09-30" for f in findings)


def test_compared_is_number_of_people_rows():
    _, compared = detect(_ctx())
    assert compared == 5


def test_prospective_finding_never_duplicates_an_already_current_orphan():
    # beta's own current-mode ownership orphans (types 2, 3, 4) have
    # nothing to do with qa-1's departure and must never appear here.
    findings, _ = detect(_ctx())
    assert not any(f.subject == "beta" for f in findings)
