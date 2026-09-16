"""Tests for reconciler.closure_audit (L3-P3-06)."""

from __future__ import annotations

from reconciler.closure_audit import ClosedFinding, audit
from reconciler.model import DriftClass, Finding, Level


def _finding(comparator: str, scope: str, first_seen: str, id_suffix: str = "") -> Finding:
    return Finding(
        id=f"{comparator}:{scope}{id_suffix}",
        comparator=comparator,
        scope=scope,
        drift_class=DriftClass.AMBER,
        level=Level.WARN,
        evidence="test",
        first_seen=first_seen,
    )


def test_closure_with_no_evidence_is_reopened_and_tagged():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence=None,
    )
    result = audit([closed], [], recurrence_window_days=14)
    assert len(result.defects) == 1
    assert result.defects[0].reason == "no_remediation_evidence"
    assert result.defects[0].closure_quality_defect is True
    assert result.defects[0].reopened is True


def test_closure_with_evidence_is_not_flagged():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence="PR#412 backfilled the store, verified in RUN-9001",
    )
    result = audit([closed], [], recurrence_window_days=14)
    assert result.defects == []


def test_same_scope_recurrence_within_window_is_reopened_and_tagged():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence="fixed",
    )
    recurrence = _finding("write_freshness", "events/", "2026-08-10T00:00:00Z", id_suffix=":r2")
    result = audit([closed], [recurrence], recurrence_window_days=14)
    reasons = {d.reason for d in result.defects}
    assert "same_scope_recurrence" in reasons
    recurrence_defect = next(d for d in result.defects if d.reason == "same_scope_recurrence")
    assert recurrence_defect.finding.id == recurrence.id
    assert recurrence_defect.closure_quality_defect is True


def test_recurrence_outside_window_is_not_flagged():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence="fixed",
    )
    late = _finding("write_freshness", "events/", "2026-09-15T00:00:00Z", id_suffix=":late")
    result = audit([closed], [late], recurrence_window_days=14)
    assert result.defects == []
    assert result.new_drift_count == 1  # counted as new drift, not a recurrence defect


def test_recurrence_excluded_from_new_drift_count():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence="fixed",
    )
    recurrence = _finding("write_freshness", "events/", "2026-08-10T00:00:00Z", id_suffix=":r2")
    unrelated = _finding("restore_tested", "alpha", "2026-08-11T00:00:00Z")
    result = audit([closed], [recurrence, unrelated], recurrence_window_days=14)
    assert result.new_drift_count == 1  # only `unrelated`; `recurrence` is excluded


def test_recurrence_window_days_is_a_caller_parameter_not_a_literal():
    closed = ClosedFinding(
        finding=_finding("write_freshness", "events/", "2026-08-01T00:00:00Z"),
        closed_at="2026-08-05T00:00:00Z",
        remediation_evidence="fixed",
    )
    borderline = _finding("write_freshness", "events/", "2026-08-10T00:00:00Z", id_suffix=":b")

    narrow = audit([closed], [borderline], recurrence_window_days=1)
    wide = audit([closed], [borderline], recurrence_window_days=30)

    assert narrow.defects == []
    assert narrow.new_drift_count == 1
    assert len(wide.defects) == 1
    assert wide.new_drift_count == 0
