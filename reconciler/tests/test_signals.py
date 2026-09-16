"""L3-P1-20: SIG-13 emission on a failed run."""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.runrecord import RunRecord
from reconciler.signals import emit_signals


def _run(status, findings, run_id="R1", finished_at="2026-08-27T00:01:00Z"):
    return RunRecord(
        run_id=run_id,
        started_at="2026-08-27T00:00:00Z",
        finished_at=finished_at,
        status=status,
        findings=findings,
        comparison_counts={},
        canary_found=True,
        external_cause=None,
    )


def _finding(drift_class, first_seen, **overrides):
    defaults = dict(
        id="F1",
        comparator="write_freshness",
        scope="events/",
        drift_class=drift_class,
        level=Level.WARN,
        evidence="e",
        first_seen=first_seen,
    )
    defaults.update(overrides)
    return Finding(**defaults)


def test_failed_run_with_no_overdue_findings_emits_exactly_one_signal():
    run = _run("FAILED", [])
    signals = emit_signals(run)
    assert len(signals) == 1
    assert signals[0]["signal_id"] == "SIG-13"
    assert signals[0]["drift_class"] == "Red"
    assert signals[0]["owner"] == "team_lead"


def test_overdue_red_finding_emits_a_signal_carrying_its_age():
    old_finding = _finding(DriftClass.RED, first_seen="2026-08-20T00:00:00Z")
    run = _run("OK", [old_finding], finished_at="2026-08-27T00:00:00Z")
    signals = emit_signals(run)
    assert len(signals) == 1
    assert "age=" in signals[0]["evidence"]
    assert "F1" in signals[0]["evidence"]


def test_blocking_finding_is_overdue_the_moment_it_outlives_its_own_run():
    # BLOCKING's response time is "immediate" - zero grace.
    old_finding = _finding(
        DriftClass.BLOCKING, first_seen="2026-08-26T23:00:00Z", id="F2"
    )
    run = _run("OK", [old_finding], finished_at="2026-08-27T00:00:00Z")
    signals = emit_signals(run)
    assert len(signals) == 1


def test_freshly_seen_finding_in_its_own_run_is_never_overdue():
    fresh = _finding(DriftClass.BLOCKING, first_seen="2026-08-27T00:00:00Z", id="F3")
    run = _run("OK", [fresh], finished_at="2026-08-27T00:00:00Z")
    assert emit_signals(run) == []


def test_no_notification_call_of_any_kind():
    import inspect

    from reconciler import signals

    source = inspect.getsource(signals)
    for token in ("requests.", "urllib", "smtplib", "webhook"):
        assert token not in source.lower()
