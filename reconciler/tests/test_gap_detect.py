"""L3-P8-01: gap detector and expiry replay (spec 53.7 bullets 1 and 3)."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.expiry import compare
from reconciler.gap.detect import GapWindow, confirm_clean, detect_gap, replay_expiries
from reconciler.model import DriftClass, Finding, Level
from reconciler.state.fixture_adapter import FixtureState

AS_OF = date(2026, 9, 15)


def _fixture_a_expiry_findings():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, _ = compare(declared, actual, AS_OF)
    return findings


def _canary_finding() -> Finding:
    return Finding(
        id="CANARY-001",
        comparator="display_name",
        scope="canary",
        drift_class=DriftClass.GREEN,
        level=Level.DETECT,
        evidence="seeded canary",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )


def test_gap_window_has_explicit_start_and_end():
    windows = detect_gap({"reconciliation": [date(2026, 8, 1)]}, 1, AS_OF)
    assert len(windows) == 1
    w = windows[0]
    assert w.kind == "reconciliation"
    assert w.start == date(2026, 8, 2)
    assert w.end == AS_OF
    assert w.missed_cycles >= 1


def test_no_gap_when_last_run_is_within_the_expected_interval():
    windows = detect_gap({"reconciliation": [date(2026, 9, 14)]}, 1, AS_OF)
    assert windows == []


def test_a_kind_never_observed_is_still_a_gap_not_a_silent_skip():
    windows = detect_gap({"health-report": []}, 1, AS_OF)
    assert len(windows) == 1
    assert windows[0].kind == "health-report"
    assert windows[0].end == AS_OF


def test_replay_revokes_the_fixture_a_expired_assignment_inside_the_window():
    window = GapWindow(kind="reconciliation", start=date(2026, 1, 1), end=AS_OF, missed_cycles=1)
    findings = _fixture_a_expiry_findings()
    repairs, escalations = replay_expiries(window, assignment_findings=findings)
    assert escalations == []
    assert len(repairs) == 1
    assert repairs[0].scope == "alpha:dev-1"
    assert repairs[0].after == {"team_member": False}


def test_replay_revokes_an_exception_expiring_inside_the_window():
    window = GapWindow(kind="reconciliation", start=date(2026, 3, 1), end=AS_OF, missed_cycles=1)
    exceptions = [{"id": "EXC-200", "requester": "dev-5", "expires": "2026-05-01", "grants": "extra_review_bypass"}]
    repairs, escalations = replay_expiries(window, exceptions=exceptions)
    assert escalations == []
    assert len(repairs) == 1
    assert repairs[0].scope == "dev-5"
    assert repairs[0].after == {"grants": None}


def test_replay_never_skips_an_exception_that_expired_before_the_window_opened():
    # EXC-201 expired long before window.start: bullet 1 draws no floor
    # at the window's start, only a ceiling at window.end.
    window = GapWindow(kind="reconciliation", start=date(2026, 3, 1), end=AS_OF, missed_cycles=1)
    exceptions = [{"id": "EXC-201", "requester": "dev-6", "expires": "2025-01-01", "grants": "extra_review_bypass"}]
    repairs, escalations = replay_expiries(window, exceptions=exceptions)
    assert escalations == []
    assert len(repairs) == 1
    assert repairs[0].scope == "dev-6"


def test_confirm_clean_fails_without_the_seeded_canary_and_passes_with_it():
    assert confirm_clean([]) is False
    assert confirm_clean([_canary_finding()]) is True
    blocking = Finding(
        id="expiry:alpha:dev-1:expired",
        comparator="expiry",
        scope="alpha:dev-1",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="still overdue",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    assert confirm_clean([_canary_finding(), blocking]) is False
