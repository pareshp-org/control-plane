"""L3-P5-07: behavioural-envelope checks (spec 40.1 "The behavioural
envelope" — all four controls; §40.3).

§40.1 explains why a scheduled time window alone is not the boundary:
"an alert that cannot fire is a gate that appears to be working and is
not" — a compromised credential run inside the scheduled hour, on the
scheduled host, would sail past a window-only check. The envelope is
therefore four independent controls, and only these four:

* ``signed_run_record`` — every run names its scheduled trigger; a run
  whose named trigger matches none of the schedule's own recorded
  triggers is out of envelope.
* ``run_count_ceiling`` — calibrated configuration, not a literal:
  initial value twice the scheduled run count per day
  (`EnvelopeConfig.run_count_ceiling`), recalibrated automatically
  whenever `scheduled_runs_per_day` changes because it is a derived
  property, never a value someone has to remember to update by hand.
* ``expected_source_host`` — a run from any other host is out of
  envelope.
* ``per_run_api_call_counts`` — published on every run (including a
  fully clean one) so that read-side abuse shows up as a volume
  anomaly to whatever watches that series; a run that fails to publish
  its own count defeats that mechanism just as surely as a run that
  publishes an anomalous one, so an unpublished count is itself a
  breach of this control.

A run outside the envelope on any of the four is Blocking drift
(§40.1) — `check_envelope()` runs every registered control and returns
every breach it finds, never stopping at the first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from reconciler.model import DriftClass, Finding, Level

ControlFn = Callable[["RunContext", "EnvelopeConfig"], "Finding | None"]

# control name -> its check(run, config) function. Populated purely by
# the four @_control registrations below — exactly four, per this
# module's own docstring ("only these four").
CONTROLS: dict[str, ControlFn] = {}


def _control(name: str) -> Callable[[ControlFn], ControlFn]:
    def register(fn: ControlFn) -> ControlFn:
        if name in CONTROLS:
            raise ValueError(f"envelope control {name!r} is already registered")
        CONTROLS[name] = fn
        return fn

    return register


@dataclass(frozen=True)
class RunContext:
    """What one reconciliation run reports about itself for envelope
    purposes — deliberately separate from reconciler.runrecord.RunRecord,
    which this module does not touch: the envelope is a pre-run/at-run
    admission check, not part of the comparator run's own output shape.
    """

    run_id: str
    started_at: str
    triggered_by: str | None
    source_host: str
    api_call_count: int | None
    runs_today: int  # this run's ordinal among today's runs, this run included


@dataclass(frozen=True)
class EnvelopeConfig:
    """Calibrated configuration for the envelope, not literals scattered
    through the controls below."""

    scheduled_triggers: frozenset[str]
    expected_source_host: str
    scheduled_runs_per_day: int

    @property
    def run_count_ceiling(self) -> int:
        # spec 40.1: "calibrated configuration, initial value twice the
        # scheduled run count per day, recalibrated whenever the
        # schedule changes" — a derived property recalculates itself
        # the instant scheduled_runs_per_day does, rather than a
        # ceiling someone has to remember to bump by hand.
        return 2 * self.scheduled_runs_per_day


def _breach(control: str, run: RunContext, evidence: str) -> Finding:
    return Finding(
        id=f"envelope:{control}:{run.run_id}",
        comparator="behavioural_envelope",
        scope=control,
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence=evidence,
        first_seen=run.started_at,
    )


@_control("signed_run_record")
def _check_signed_run_record(run: RunContext, config: EnvelopeConfig) -> Finding | None:
    if run.triggered_by is None or run.triggered_by not in config.scheduled_triggers:
        return _breach(
            "signed_run_record",
            run,
            f"run {run.run_id} names trigger {run.triggered_by!r}, which matches no "
            f"scheduled trigger record ({sorted(config.scheduled_triggers)}) — a run with "
            "no matching trigger record is out of envelope (spec 40.1)",
        )
    return None


@_control("run_count_ceiling")
def _check_run_count_ceiling(run: RunContext, config: EnvelopeConfig) -> Finding | None:
    ceiling = config.run_count_ceiling
    if run.runs_today > ceiling:
        return _breach(
            "run_count_ceiling",
            run,
            f"run {run.run_id} is the {run.runs_today}th run today, over the ceiling of "
            f"{ceiling} (twice the {config.scheduled_runs_per_day} scheduled runs/day) — "
            "spec 40.1",
        )
    return None


@_control("expected_source_host")
def _check_expected_source_host(run: RunContext, config: EnvelopeConfig) -> Finding | None:
    if run.source_host != config.expected_source_host:
        return _breach(
            "expected_source_host",
            run,
            f"run {run.run_id} ran from host {run.source_host!r}, expected "
            f"{config.expected_source_host!r} — a run from any other host is out of "
            "envelope (spec 40.1)",
        )
    return None


@_control("per_run_api_call_counts")
def _check_per_run_api_call_counts(run: RunContext, config: EnvelopeConfig) -> Finding | None:
    if run.api_call_count is None:
        return _breach(
            "per_run_api_call_counts",
            run,
            f"run {run.run_id} published no per-run API call count — this control exists "
            "so read-side abuse surfaces as a volume anomaly (spec 40.1); a run that "
            "publishes nothing defeats that just as surely as one that publishes an "
            "anomalous count",
        )
    if run.api_call_count < 0:
        return _breach(
            "per_run_api_call_counts",
            run,
            f"run {run.run_id} published a negative API call count ({run.api_call_count})",
        )
    return None


def check_envelope(run: RunContext, config: EnvelopeConfig) -> list[Finding]:
    """Run every registered control against `run`, in name-sorted
    order, and return every breach found — never short-circuiting on
    the first one, since §40.1 treats all four as independent."""
    findings: list[Finding] = []
    for name in sorted(CONTROLS):
        finding = CONTROLS[name](run, config)
        if finding is not None:
            findings.append(finding)
    return findings
