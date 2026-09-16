"""L3-P3-06: closure-quality audit sampler (spec 53.6: "Closure
quality is auditable. Every closed drift finding records what changed
and links its evidence. A sample of closed findings is audited at the
quarterly review; a finding closed without evidence of remediation, or
a finding that recurs in the same scope shortly after closure, is
reopened and counted as a closure-quality defect, not as new drift.
Fast-closing findings to keep counts pretty therefore fails the audit
rather than passing the budget.")

Two independent checks, both producing a ClosureQualityDefect that
reopens the implicated finding rather than letting it stand as either
a clean closure or (for the recurrence case) fresh drift:

  A. A ClosedFinding with no `remediation_evidence` link.
  B. An open Finding whose `(comparator, scope)` matches a closed
     finding's, and whose `first_seen` falls within
     `recurrence_window_days` after that closure - a same-scope
     recurrence "shortly after closure" (spec 53.6). Such a finding is
     excluded from `new_drift_count` so it is not double-counted.

`recurrence_window_days` is always a caller-supplied parameter, never
a literal in this module: spec 53.6 makes tolerances themselves
calibration-reviewed, so the window is exactly the kind of value this
module must never hard-code.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime

from reconciler.model import Finding


@dataclasses.dataclass(frozen=True)
class ClosedFinding:
    """A previously-open Finding, as closed. `remediation_evidence` is
    the link spec 53.6 requires ("records what changed and links its
    evidence"); its absence is itself an audit defect."""

    finding: Finding
    closed_at: str  # ISO-8601, e.g. "2026-08-27T00:00:00Z"
    remediation_evidence: str | None = None


@dataclasses.dataclass(frozen=True)
class ClosureQualityDefect:
    finding: Finding
    reason: str  # "no_remediation_evidence" | "same_scope_recurrence"
    reopened: bool = True
    closure_quality_defect: bool = True


@dataclasses.dataclass(frozen=True)
class AuditResult:
    defects: list[ClosureQualityDefect]
    # Open findings implicated in a recurrence defect are excluded
    # here - they are counted as a closure-quality defect, not as new
    # drift (spec 53.6).
    new_drift_count: int


def _parse(iso_ts: str) -> datetime:
    return datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))


def audit(
    closed_findings: list[ClosedFinding],
    open_findings: list[Finding],
    recurrence_window_days: float,
) -> AuditResult:
    defects: list[ClosureQualityDefect] = []
    recurred_open_ids: set[str] = set()

    # Check A: evidence-less closures.
    for closed in closed_findings:
        if not closed.remediation_evidence:
            defects.append(
                ClosureQualityDefect(finding=closed.finding, reason="no_remediation_evidence")
            )

    # Check B: same-scope recurrence shortly after closure.
    for closed in closed_findings:
        closed_at = _parse(closed.closed_at)
        for open_finding in open_findings:
            if open_finding.id in recurred_open_ids:
                continue
            if (
                open_finding.comparator != closed.finding.comparator
                or open_finding.scope != closed.finding.scope
            ):
                continue
            elapsed_days = (_parse(open_finding.first_seen) - closed_at).total_seconds() / 86400.0
            if 0 <= elapsed_days <= recurrence_window_days:
                defects.append(
                    ClosureQualityDefect(finding=open_finding, reason="same_scope_recurrence")
                )
                recurred_open_ids.add(open_finding.id)

    new_drift_count = sum(1 for f in open_findings if f.id not in recurred_open_ids)

    return AuditResult(defects=defects, new_drift_count=new_drift_count)
