"""L3-P2-03: orphan detectors 6-10 (assets and customer commitments)."""

from __future__ import annotations

from datetime import date

from reconciler.orphans import load_context
from reconciler.orphans.assets import detect


def _ctx():
    return load_context("fixture-a", date(2026, 8, 27))


def test_fixture_a_exactly_three_findings():
    findings, compared = detect(_ctx())
    assert len(findings) == 3
    by_index = {f.index: f for f in findings}
    assert set(by_index) == {7, 8, 10}
    assert by_index[7].subject == "domain-1"
    assert by_index[7].orphan_severity == "Blocking"
    assert by_index[8].subject == "vendor-1"
    assert by_index[8].orphan_severity == "Medium"
    assert by_index[10].subject == "COM-alpha-001"
    assert by_index[10].orphan_severity == "Blocking"


def test_certificate_owned_by_a_departing_person_is_not_a_finding():
    # cert-1's owner qa-1 is availability: departing - still active.
    findings, _ = detect(_ctx())
    assert not any(f.subject == "cert-1" for f in findings)


def test_operational_asset_with_an_active_owner_is_not_a_finding():
    findings, _ = detect(_ctx())
    assert not any(f.subject == "opasset-1" for f in findings)


def test_compared_is_asset_rows_plus_commitment_rows():
    _, compared = detect(_ctx())
    assert compared == 5
