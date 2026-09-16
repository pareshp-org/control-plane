"""L3-P5-05: verifier absence for one cycle is Level 5."""

from __future__ import annotations

from reconciler.model import DriftClass, Level

from validators.drift.liveness import check_liveness


def test_gap_of_one_cycle_plus_one_minute_yields_escalate():
    finding = check_liveness(
        last_verifier_result_at="2026-09-15T00:00:00Z",
        as_of="2026-09-15T06:01:00Z",
        cycle_hours=6,
    )
    assert finding is not None
    assert finding.level == Level.ESCALATE
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.scope == "drift_verifier"


def test_gap_inside_one_cycle_yields_no_finding():
    finding = check_liveness(
        last_verifier_result_at="2026-09-15T00:00:00Z",
        as_of="2026-09-15T05:59:00Z",
        cycle_hours=6,
    )
    assert finding is None


def test_gap_exactly_at_the_cycle_boundary_has_not_yet_exceeded_it():
    finding = check_liveness(
        last_verifier_result_at="2026-09-15T00:00:00Z",
        as_of="2026-09-15T06:00:00Z",
        cycle_hours=6,
    )
    assert finding is None


def test_function_is_pure_and_deterministic_for_the_same_inputs():
    args = dict(last_verifier_result_at="2026-09-15T00:00:00Z", as_of="2026-09-16T00:00:00Z", cycle_hours=6)
    first = check_liveness(**args)
    second = check_liveness(**args)
    assert first == second
    assert first.id == "drift_verifier:absent"
    assert first.acknowledged_by is None
    assert first.external_cause is None
