"""L3-P1-20: SIG-13 emission on a failed run (spec 52.2 SIG-13; 52.4; AT-032; AT-102).

SIG-13 ("Reconciliation job failures, or unresolved findings older
than their class response time" - source Reconciliation, default class
Red, owner Team Lead, P0) fires in two situations:

* the run itself is FAILED (AT-102's zero-findings/missing-canary rule,
  or L3-P1-16's narrowed-comparison rule, or a crashed comparator);
* any individual finding has outlived its own drift class's §53.4
  response time - Red's "2 business days", Blocking's "immediate" (no
  grace period at all: any finding still open past the run in which it
  was first seen is already overdue).

This module only ever returns a list of dicts. It emits; it never
delivers - routing a signal to a human or a channel is Lane 5's
exclusive `notify/**` path (spec 40.1 D89 pattern), and no function
here opens a network connection of any kind to deliver one.

L3-P2-06 extends `emit_signals()` with SIG-05 ("Orphan risk" - source
Reconciliation orphan detection, class Blocking, owner Team Lead;
spec §52.2). It fires once per product carrying at least one orphaned
Primary Owner, Cross-Reviewer, or Primary Responder slot (orphan types
1, 2, 4 - reconciler.orphans.dismissal.SIG05_TRIGGER_INDICES), passed
in via the optional `orphan_findings` argument so every existing
single-argument `emit_signals(run)` call site (SIG-13) is unaffected.
SIG-05 is disjoint from SIG-26/SIG-27 (§52.2's note: "Orphan risk
(SIG-05) is a product-structure condition") - this module never emits
either of those ids, so the two can never be conflated here.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from reconciler.model import DriftClass
from reconciler.runrecord import RunRecord

# §53.4 response times, restricted to the two classes SIG-13's own
# spec text names explicitly (Red, Blocking). Amber's and Green's
# response times are not "overdue" conditions SIG-13 tracks.
_RESPONSE_WINDOW: dict[DriftClass, timedelta] = {
    DriftClass.RED: timedelta(days=2),
    DriftClass.BLOCKING: timedelta(0),
}


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _sig13(evidence: str) -> dict:
    return {
        "signal_id": "SIG-13",
        "drift_class": "Red",
        "owner": "team_lead",
        "evidence": evidence,
    }


def _sig05(product: str, evidence: str) -> dict:
    return {
        "signal_id": "SIG-05",
        "drift_class": "Blocking",
        "owner": "team_lead",
        "evidence": evidence,
        "product": product,
    }


def emit_signals(run: RunRecord, orphan_findings: list | None = None) -> list[dict]:
    signals: list[dict] = []

    if run.status == "FAILED":
        signals.append(_sig13(f"reconciliation run {run.run_id} FAILED"))

    finished_at = _parse(run.finished_at)
    for finding in run.findings:
        window = _RESPONSE_WINDOW.get(finding.drift_class)
        if window is None:
            continue
        age = finished_at - _parse(finding.first_seen)
        if age > window:
            signals.append(
                _sig13(
                    f"finding {finding.id} ({finding.drift_class.value}) has been open "
                    f"for {age}, past its {window} response window (age={age})"
                )
            )

    if orphan_findings:
        from reconciler.orphans.dismissal import sig05_products

        for product in sig05_products(list(orphan_findings)):
            signals.append(_sig05(product, f"{product}: orphaned Primary Owner, Cross-Reviewer or Primary Responder slot"))

    return signals
