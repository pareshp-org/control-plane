"""L3-P5-07: behavioural-envelope checks."""

from __future__ import annotations

from reconciler.envelope import CONTROLS, EnvelopeConfig, RunContext, check_envelope
from reconciler.model import DriftClass, Level


def _config(**overrides):
    defaults = dict(
        scheduled_triggers=frozenset({"scheduled-6h"}),
        expected_source_host="ops-vm-1",
        scheduled_runs_per_day=4,
    )
    defaults.update(overrides)
    return EnvelopeConfig(**defaults)


def _run(**overrides):
    defaults = dict(
        run_id="R1",
        started_at="2026-09-15T00:00:00Z",
        triggered_by="scheduled-6h",
        source_host="ops-vm-1",
        api_call_count=42,
        runs_today=1,
    )
    defaults.update(overrides)
    return RunContext(**defaults)


def test_exactly_four_controls_are_registered():
    assert len(CONTROLS) == 4
    assert sorted(CONTROLS) == [
        "expected_source_host",
        "per_run_api_call_counts",
        "run_count_ceiling",
        "signed_run_record",
    ]


def test_a_fully_in_envelope_run_produces_no_findings():
    assert check_envelope(_run(), _config()) == []


def test_an_unrecognised_trigger_breaches_signed_run_record():
    findings = check_envelope(_run(triggered_by="ad-hoc-manual"), _config())
    assert len(findings) == 1
    assert findings[0].scope == "signed_run_record"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_run_count_ceiling_is_twice_the_scheduled_runs_per_day_not_a_literal():
    config = _config(scheduled_runs_per_day=4)
    assert config.run_count_ceiling == 8
    config2 = _config(scheduled_runs_per_day=10)
    assert config2.run_count_ceiling == 20


def test_exceeding_the_run_count_ceiling_breaches_that_control_only():
    config = _config(scheduled_runs_per_day=4)  # ceiling = 8
    findings = check_envelope(_run(runs_today=9), config)
    assert len(findings) == 1
    assert findings[0].scope == "run_count_ceiling"


def test_a_run_from_an_unexpected_host_breaches_expected_source_host():
    findings = check_envelope(_run(source_host="attacker-box"), _config())
    assert len(findings) == 1
    assert findings[0].scope == "expected_source_host"
    assert "attacker-box" in findings[0].evidence


def test_an_unpublished_api_call_count_breaches_per_run_api_call_counts():
    findings = check_envelope(_run(api_call_count=None), _config())
    assert len(findings) == 1
    assert findings[0].scope == "per_run_api_call_counts"


def test_multiple_simultaneous_breaches_are_all_reported_not_just_the_first():
    findings = check_envelope(
        _run(triggered_by=None, source_host="attacker-box", api_call_count=None, runs_today=99),
        _config(scheduled_runs_per_day=1),
    )
    assert {f.scope for f in findings} == {
        "signed_run_record",
        "run_count_ceiling",
        "expected_source_host",
        "per_run_api_call_counts",
    }
