"""L3-P1-18: run annotations - external-cause, acknowledged_by/at, clean-run record (spec 53.1).

Three independent operations, none of which mutate their argument in
place - RunRecord and Finding are both plain dataclasses without a
private, hidden write path, so every function here returns a new value
via dataclasses.replace() rather than reaching into an existing record.
"""

from __future__ import annotations

import dataclasses

from reconciler.canary import CANARY_ID
from reconciler.model import DriftClass, Finding
from reconciler.runrecord import RunRecord


class AlreadyAcknowledged(RuntimeError):
    """Raised by acknowledge() when a finding already carries one."""


def annotate_external_cause(run: RunRecord, outage_ref: str) -> RunRecord:
    """Mark `run` as caused by an external outage.

    Names the outage on the run itself (`run.external_cause`), and on
    every Red finding that does not already carry an external_cause
    annotation - suppressing raw Red escalation for this run without
    touching Blocking findings, which are never suppressed by an
    outage (spec 53.4: Blocking's response time is "immediate"
    regardless of cause). `needs_reexecution()` reports this run as
    due for a re-run once the named dependency recovers.
    """
    annotated_findings = [
        dataclasses.replace(finding, external_cause=outage_ref)
        if finding.drift_class == DriftClass.RED and finding.external_cause is None
        else finding
        for finding in run.findings
    ]
    return dataclasses.replace(run, external_cause=outage_ref, findings=annotated_findings)


def needs_reexecution(run: RunRecord) -> bool:
    """True for any run carrying an external_cause annotation - it is
    due for re-execution once the named dependency recovers."""
    return run.external_cause is not None


def acknowledge(finding: Finding, by: str, at: str) -> Finding:
    """Return a copy of `finding` with acknowledged_by/at set.

    Refuses to overwrite an existing acknowledgement: a second
    responder must see the interrupt is already claimed, not silently
    reassign it to themselves.
    """
    if finding.acknowledged_by is not None:
        raise AlreadyAcknowledged(
            f"finding {finding.id!r} is already acknowledged by "
            f"{finding.acknowledged_by!r} at {finding.acknowledged_at!r}"
        )
    return dataclasses.replace(finding, acknowledged_by=by, acknowledged_at=at)


def record_clean(run: RunRecord) -> RunRecord:
    """A clean run - no findings beyond the seeded canary - still
    produces a full run record (spec 53.1: "a clean run is recorded as
    clean"), never an empty file.

    Raises ValueError if `run` actually carries non-canary findings -
    this function documents and enforces the "clean" precondition
    rather than silently relabelling a dirty run as clean.
    """
    non_canary = [f for f in run.findings if f.id != CANARY_ID]
    if non_canary:
        raise ValueError(
            f"record_clean() called on a run with {len(non_canary)} non-canary finding(s)"
        )
    return run
