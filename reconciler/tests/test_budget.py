"""Tests for reconciler.budget (L3-P3-04)."""

from __future__ import annotations

from reconciler.budget import ceilings, evaluate
from reconciler.canary import CANARY_ID
from reconciler.model import DriftClass, Finding, Level


def _finding(comparator: str, drift_class: DriftClass, scope: str = "x", id_: str | None = None) -> Finding:
    return Finding(
        id=id_ or f"{comparator}:{scope}",
        comparator=comparator,
        scope=scope,
        drift_class=drift_class,
        level=Level.WARN,
        evidence="test",
        first_seen="2026-08-27T00:00:00Z",
    )


def test_amber_ceiling_scales_with_product_count():
    assert ceilings(2)["amber"] == 4
    assert ceilings(8)["amber"] == 16
    assert ceilings(20)["amber"] == 40


def test_red_ceiling_is_flat_at_every_product_count():
    assert ceilings(2)["red"] == 3
    assert ceilings(8)["red"] == 3
    assert ceilings(20)["red"] == 3


def test_green_and_blocking_carry_no_ceiling():
    result = ceilings(20)
    assert result["green"] is None
    assert result["blocking"] is None


def test_evaluate_excludes_canary_finding_from_counts():
    canary = _finding("display_name", DriftClass.GREEN, id_=CANARY_ID)
    report = evaluate([canary], product_count=8)
    assert report.open_counts[DriftClass.GREEN.value] == 0


def test_evaluate_excludes_prospective_orphan_findings():
    prospective = _finding("orphan_prospective_ownership", DriftClass.AMBER)
    report = evaluate([prospective], product_count=8)
    assert report.open_counts[DriftClass.AMBER.value] == 0


def test_evaluate_amber_breach_is_attributed_to_the_operating_system():
    findings = [_finding("write_freshness", DriftClass.AMBER, scope=f"p{i}") for i in range(5)]
    report = evaluate(findings, product_count=2, config={"amber_per_product": 2})
    assert report.ceilings["amber"] == 4
    assert report.breaches["amber"] is True
    assert report.amber_breach_scope == "operating_system"
    assert report.amber_breach_scope not in {f.scope for f in findings}


def test_evaluate_no_breach_when_at_or_under_ceiling():
    findings = [_finding("write_freshness", DriftClass.AMBER, scope=f"p{i}") for i in range(4)]
    report = evaluate(findings, product_count=2, config={"amber_per_product": 2})
    assert report.breaches["amber"] is False
    assert report.amber_breach_scope is None
