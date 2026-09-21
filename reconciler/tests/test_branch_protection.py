"""L3-P1-06: branch-protection template vs actual comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.branch_protection import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState

_TEMPLATE = {
    "required_pull_request_reviews": {
        "required_approving_review_count": 1,
        "require_code_owner_reviews": True,
        "require_last_push_approval": True,
        "dismiss_stale_reviews": True,
    },
    "required_status_checks": {"strict": True, "contexts": ["control-plane/blocking-drift"]},
    "allow_force_pushes": False,
    "allow_deletions": False,
    "enforce_admins": True,
}


def _fake_declared(products, template=_TEMPLATE):
    return type(
        "D",
        (),
        {"products": products, "templates": {"branch-protection": template}},
    )()


def test_fixture_a_exactly_one_finding_beta_weakened():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    finding = findings[0]
    assert finding.scope == "beta"
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.level == Level.BLOCK
    assert "require_code_owner_reviews" in finding.evidence


def test_matching_protection_produces_no_finding():
    class FakeActual:
        def branch_protection(self, repo):
            return dict(_TEMPLATE)

    declared = _fake_declared({"solo": {}})
    findings, compared = compare(declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_weakened_required_approving_review_count_is_blocking():
    class FakeActual:
        def branch_protection(self, repo):
            weak = dict(_TEMPLATE)
            weak["required_pull_request_reviews"] = dict(weak["required_pull_request_reviews"])
            weak["required_pull_request_reviews"]["required_approving_review_count"] = 0
            return weak

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.BLOCKING


def test_disappearing_required_context_is_blocking():
    class FakeActual:
        def branch_protection(self, repo):
            weak = dict(_TEMPLATE)
            weak["required_status_checks"] = {"strict": True, "contexts": []}
            return weak

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.BLOCKING
    assert "contexts" in findings[0].evidence


def test_stricter_than_declared_yields_amber_never_repaired():
    """AT-033: actual stricter than declared raises Level 2, never a repair."""

    class FakeActual:
        def branch_protection(self, repo):
            stricter = dict(_TEMPLATE)
            stricter["required_pull_request_reviews"] = dict(stricter["required_pull_request_reviews"])
            stricter["required_pull_request_reviews"]["required_approving_review_count"] = 2
            return stricter

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN
    assert findings[0].id.endswith("stricter_than_declared")


def test_extra_required_context_is_stricter_amber():
    class FakeActual:
        def branch_protection(self, repo):
            stricter = dict(_TEMPLATE)
            stricter["required_status_checks"] = {
                "strict": True,
                "contexts": ["control-plane/blocking-drift", "extra-check"],
            }
            return stricter

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER


def test_allow_force_pushes_turned_on_is_weakened():
    class FakeActual:
        def branch_protection(self, repo):
            weak = dict(_TEMPLATE)
            weak["allow_force_pushes"] = True
            return weak

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.BLOCKING
