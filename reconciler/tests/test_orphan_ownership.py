"""L3-P2-02: orphan detectors 1-5 (ownership slots and shared services)."""

from __future__ import annotations

from datetime import date

from reconciler.orphans import load_context
from reconciler.orphans.ownership import detect


def _ctx():
    return load_context("fixture-a", date(2026, 8, 27))


def test_fixture_a_exactly_four_findings_all_on_beta_and_auth_service():
    findings, compared = detect(_ctx())
    assert len(findings) == 4
    by_index = {f.index: f for f in findings}
    assert set(by_index) == {2, 3, 4, 5}
    assert by_index[2].subject == "beta"
    assert by_index[3].subject == "beta"
    assert by_index[4].subject == "beta"
    assert by_index[5].subject == "auth-service"
    assert by_index[2].orphan_severity == "Blocking"
    assert by_index[4].orphan_severity == "Blocking"
    assert by_index[5].orphan_severity == "Blocking"
    assert by_index[3].orphan_severity == "High"


def test_alpha_produces_no_ownership_orphan():
    findings, _ = detect(_ctx())
    assert not any(f.subject == "alpha" for f in findings)


def test_betas_active_primary_owner_produces_no_finding():
    findings, _ = detect(_ctx())
    assert not any(f.index == 1 for f in findings)


def test_compared_is_products_plus_shared_services():
    _, compared = detect(_ctx())
    assert compared == 3


def test_departing_person_is_not_treated_as_an_inactive_holder():
    # qa-1 is availability: departing in fixture-a - active in current
    # mode. This detector must never orphan a slot qa-1 holds; the
    # STOP rule in the task spec forbids collapsing departing into
    # departed/revoked here.
    ctx = _ctx()
    assert ctx.person("qa-1")["availability"] == "departing"
    findings, _ = detect(ctx)
    assert not any(f.subject == "qa-1" for f in findings)
