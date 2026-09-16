"""L3-P6-06: repair class: expired assignment and expired access
removal (AT-008, AT-018, AT-036, AT-037)."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from reconciler.cli import DeclaredState
from reconciler.comparators.expiry import compare
from reconciler.model import DriftClass, Level
from reconciler.repair import expiry_revoke
from reconciler.state.fixture_adapter import FixtureState

AS_OF = date(2026, 9, 15)


def _fixture_a_expiry_findings():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, _ = compare(declared, actual, AS_OF)
    return findings


def test_fixture_a_expired_assignment_revoked_when_enabled():
    findings = _fixture_a_expiry_findings()
    repairs = expiry_revoke.revoke_expired_assignments(findings, enabled=True)
    assert len(repairs) == 1
    assert repairs[0].scope == "alpha:dev-1"
    assert repairs[0].after == {"team_member": False}
    assert repairs[0].repair_class == "expiry_revoke"


def test_disabled_class_yields_no_repairs_and_finding_stands():
    findings = _fixture_a_expiry_findings()
    repairs = expiry_revoke.revoke_expired_assignments(findings, enabled=False)
    assert repairs == []
    # AT-018's "no human action" guarantee never silently downgrades
    # the underlying finding - re-running the comparator still raises
    # it, unchanged, while the class stays off (spec 10.2).
    still_findings = _fixture_a_expiry_findings()
    assert len(still_findings) == 1
    assert still_findings[0].drift_class == DriftClass.BLOCKING
    assert still_findings[0].level == Level.BLOCK


def test_amber_expiring_soon_finding_is_not_touched_by_repair():
    class FakeActual:
        def team_members(self, product):
            return ["temp-1"]

    fake_declared = type(
        "D",
        (),
        {
            "products": {
                "gamma": {
                    "temporary_assignments": [
                        {"person": "temp-1", "type": "temporary_contributor", "end_date": "2026-09-20"}
                    ]
                }
            }
        },
    )()
    findings, _ = compare(fake_declared, FakeActual(), AS_OF)
    assert findings[0].drift_class == DriftClass.AMBER
    repairs = expiry_revoke.revoke_expired_assignments(findings, enabled=True)
    assert repairs == []


def test_exception_past_expiry_with_grants_is_revoked():
    exceptions = [{"id": "EXC-100", "requester": "dev-9", "expires": "2026-01-01", "grants": "extra_review_bypass"}]
    repairs, escalations = expiry_revoke.revoke_expired_exceptions(exceptions, AS_OF, enabled=True)
    assert escalations == []
    assert len(repairs) == 1
    assert repairs[0].scope == "dev-9"
    assert repairs[0].after == {"grants": None}


def test_exception_past_expiry_without_grants_escalates_to_blocking():
    exceptions = [{"id": "EXC-101", "requester": "dev-9", "expires": "2026-01-01"}]
    repairs, escalations = expiry_revoke.revoke_expired_exceptions(exceptions, AS_OF, enabled=True)
    assert repairs == []
    assert len(escalations) == 1
    assert escalations[0].drift_class == DriftClass.BLOCKING
    assert escalations[0].level == Level.BLOCK
    assert "AT-037" in escalations[0].evidence


def test_exception_not_yet_expired_is_untouched():
    exceptions = [{"id": "EXC-001", "requester": "dev-2", "expires": "2026-12-01"}]
    repairs, escalations = expiry_revoke.revoke_expired_exceptions(exceptions, AS_OF, enabled=True)
    assert repairs == []
    assert escalations == []


def test_every_repair_calls_permitted():
    findings = _fixture_a_expiry_findings()
    with patch("reconciler.repair.expiry_revoke.permitted", wraps=expiry_revoke.permitted) as spy:
        repairs = expiry_revoke.revoke_expired_assignments(findings, enabled=True)
    assert spy.call_count == len(findings)
    assert repairs


def test_temporary_assignment_never_becomes_permanent_through_inaction():
    # Disabling the class must never be mistaken for the assignment
    # becoming permanent (spec 10.2): the comparator keeps raising the
    # same Blocking finding for as long as the class stays off, run
    # after run, rather than the drift quietly clearing itself.
    findings_run_1 = _fixture_a_expiry_findings()
    expiry_revoke.revoke_expired_assignments(findings_run_1, enabled=False)
    findings_run_2 = _fixture_a_expiry_findings()
    assert findings_run_1 == findings_run_2
    assert findings_run_2[0].drift_class == DriftClass.BLOCKING
