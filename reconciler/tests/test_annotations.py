"""L3-P1-18: run annotations: external-cause, acknowledged_by/at, clean-run record."""

from __future__ import annotations

import pytest

from reconciler.annotations import (
    AlreadyAcknowledged,
    acknowledge,
    annotate_external_cause,
    needs_reexecution,
    record_clean,
)
from reconciler.canary import CANARY_ID
from reconciler.model import DriftClass, Finding, Level
from reconciler.runrecord import RunRecord


def _finding(drift_class, **overrides):
    defaults = dict(
        id="F1",
        comparator="write_freshness",
        scope="events/",
        drift_class=drift_class,
        level=Level.WARN,
        evidence="e",
        first_seen="2026-08-27T00:00:00Z",
    )
    defaults.update(overrides)
    return Finding(**defaults)


def _run(findings):
    return RunRecord(
        run_id="R1",
        started_at="2026-08-27T00:00:00Z",
        finished_at="2026-08-27T00:01:00Z",
        status="OK",
        findings=findings,
        comparison_counts={"write_freshness": 3},
        canary_found=True,
        external_cause=None,
    )


def test_external_cause_names_the_outage_and_marks_for_reexecution():
    red_finding = _finding(DriftClass.RED)
    run = _run([red_finding])
    assert needs_reexecution(run) is False

    annotated = annotate_external_cause(run, "outage-2026-08-27-pagerduty-123")
    assert annotated.external_cause == "outage-2026-08-27-pagerduty-123"
    assert needs_reexecution(annotated) is True
    assert annotated.findings[0].external_cause == "outage-2026-08-27-pagerduty-123"


def test_external_cause_never_suppresses_blocking_findings():
    blocking_finding = _finding(DriftClass.BLOCKING)
    run = _run([blocking_finding])
    annotated = annotate_external_cause(run, "outage-1")
    assert annotated.findings[0].external_cause is None


def test_acknowledge_sets_by_and_at():
    finding = _finding(DriftClass.AMBER)
    acked = acknowledge(finding, by="lead-1", at="2026-08-27T12:00:00Z")
    assert acked.acknowledged_by == "lead-1"
    assert acked.acknowledged_at == "2026-08-27T12:00:00Z"
    assert finding.acknowledged_by is None  # original untouched


def test_second_acknowledge_raises_rather_than_overwrites():
    finding = _finding(DriftClass.AMBER)
    acked = acknowledge(finding, by="lead-1", at="2026-08-27T12:00:00Z")
    with pytest.raises(AlreadyAcknowledged):
        acknowledge(acked, by="dev-1", at="2026-08-27T13:00:00Z")


def test_clean_run_still_produces_a_full_record():
    canary_only = _finding(DriftClass.GREEN, id=CANARY_ID, comparator="display_name")
    run = _run([canary_only])
    recorded = record_clean(run)
    assert recorded.status == "OK"
    assert recorded.to_dict()["findings"] != []
    assert recorded.to_dict()["run_id"] == "R1"


def test_record_clean_rejects_a_run_with_real_findings():
    run = _run([_finding(DriftClass.BLOCKING)])
    with pytest.raises(ValueError):
        record_clean(run)
