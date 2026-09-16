"""L3-P1-13: declared infrastructure boundary vs attestation window comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.infra_attestation import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_only_beta_is_stale():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].scope == "beta"
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert findings[0].level == Level.BLOCK


def test_no_provider_side_call_is_ever_made():
    import inspect

    from reconciler.comparators import infra_attestation

    source = inspect.getsource(infra_attestation)
    assert "actual." not in source


def test_product_within_window_is_clean():
    fake_declared = type(
        "D",
        (),
        {
            "platform": {"attestation_window_days": 30},
            "products": {
                "solo": {"infrastructure": {"attestation_date": "2026-08-10"}},
            },
        },
    )()
    findings, compared = compare(fake_declared, None, date(2026, 8, 27))
    assert findings == []
    assert compared == 1
