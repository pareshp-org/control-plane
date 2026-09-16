"""L3-P2-06: Blocking orphans are non-dismissible; SIG-05 emission."""

from __future__ import annotations

from datetime import date

import pytest

from reconciler.orphans import load_context
from reconciler.orphans.dismissal import Dismissal, NonDismissibleOrphan, dismiss, sig05_products
from reconciler.orphans.governance import detect as detect_governance
from reconciler.orphans.ownership import detect as detect_ownership
from reconciler.runrecord import RunRecord
from reconciler.signals import emit_signals


def _ctx():
    return load_context("fixture-a", date(2026, 8, 27))


def _all_orphan_findings():
    findings = []
    for detect in (detect_ownership, detect_governance):
        found, _ = detect(_ctx())
        findings.extend(found)
    return findings


def _run(status="OK", findings=None):
    return RunRecord(
        run_id="R1",
        started_at="2026-08-27T00:00:00Z",
        finished_at="2026-08-27T00:00:00Z",
        status=status,
        findings=findings or [],
        comparison_counts={},
        canary_found=True,
        external_cause=None,
    )


def test_dismiss_raises_on_every_blocking_orphan():
    findings, _ = detect_ownership(_ctx())
    blocking = [f for f in findings if f.orphan_severity == "Blocking"]
    assert blocking  # beta's Cross-Reviewer and Primary Responder, auth-service
    for finding in blocking:
        with pytest.raises(NonDismissibleOrphan):
            dismiss(finding, actor="anyone", reason="not needed")


def test_dismiss_raises_even_for_platform_admin_actor():
    findings, _ = detect_ownership(_ctx())
    blocking = next(f for f in findings if f.orphan_severity == "Blocking")
    with pytest.raises(NonDismissibleOrphan):
        dismiss(blocking, actor="founder-1", reason="I hold platform-admin")


def test_non_blocking_orphan_requires_a_resolution_ref():
    findings, _ = detect_ownership(_ctx())
    high = next(f for f in findings if f.orphan_severity == "High")  # beta backup owner
    with pytest.raises(ValueError):
        dismiss(high, actor="lead-1", reason="covered informally")

    result = dismiss(high, actor="lead-1", reason="covered informally", resolution_ref="RESOLVE-42")
    assert isinstance(result, Dismissal)
    assert result.resolution_ref == "RESOLVE-42"


def test_sig05_fires_for_beta_and_not_for_alpha():
    findings = _all_orphan_findings()
    products = sig05_products(findings)
    assert products == ["beta"]

    signals = emit_signals(_run(), orphan_findings=findings)
    sig05 = [s for s in signals if s["signal_id"] == "SIG-05"]
    assert len(sig05) == 1
    assert sig05[0]["product"] == "beta"
    assert sig05[0]["drift_class"] == "Blocking"
    assert sig05[0]["owner"] == "team_lead"
    assert not any(s["product"] == "alpha" for s in sig05 if "product" in s)


def test_sig05_is_not_conflated_with_sig26_or_sig27():
    findings = _all_orphan_findings()
    signals = emit_signals(_run(), orphan_findings=findings)
    signal_ids = {s["signal_id"] for s in signals}
    assert signal_ids == {"SIG-05"}
    assert "SIG-26" not in signal_ids
    assert "SIG-27" not in signal_ids


def test_emit_signals_without_orphan_findings_is_unaffected_backward_compatible():
    # Existing SIG-13 call sites pass a single positional RunRecord.
    assert emit_signals(_run(status="FAILED")) == [
        {
            "signal_id": "SIG-13",
            "drift_class": "Red",
            "owner": "team_lead",
            "evidence": "reconciliation run R1 FAILED",
        }
    ]
