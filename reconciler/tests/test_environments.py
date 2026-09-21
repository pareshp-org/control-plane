"""L3-P1-08: environments and deployment branch/tag policy comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.environments import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState

_TEMPLATE = {
    "environments": ["staging", "production"],
    "deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False},
}


def _fake_declared(products, template=_TEMPLATE):
    return type("D", (), {"products": products, "templates": {"environment": template}})()


def test_fixture_a_exactly_one_finding_beta_production_null_policy():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 4
    assert len(findings) == 1
    finding = findings[0]
    assert finding.scope == "beta/production"
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.level == Level.BLOCK
    assert finding.id.endswith("deployment_branch_policy_missing")


def test_matching_environments_produce_no_finding():
    class FakeActual:
        def environments(self, repo):
            return {
                "staging": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}},
                "production": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}},
            }

    declared = _fake_declared({"solo": {}})
    findings, compared = compare(declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 2


def test_missing_environment_is_amber():
    class FakeActual:
        def environments(self, repo):
            return {"staging": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}}}

    declared = _fake_declared({"solo": {}})
    findings, compared = compare(declared, FakeActual(), date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.AMBER
    assert findings[0].level == Level.WARN
    assert findings[0].scope == "solo/production"


def test_null_deployment_branch_policy_is_blocking():
    class FakeActual:
        def environments(self, repo):
            return {
                "staging": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}},
                "production": {"deployment_branch_policy": None},
            }

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.BLOCKING


def test_widened_policy_protected_branches_off_is_blocking():
    class FakeActual:
        def environments(self, repo):
            return {
                "staging": {"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": False}},
                "production": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}},
            }

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].scope == "solo/staging"
    assert findings[0].drift_class == DriftClass.BLOCKING


def test_widened_policy_custom_branch_policies_on_is_blocking():
    class FakeActual:
        def environments(self, repo):
            return {
                "staging": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}},
                "production": {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": True}},
            }

    declared = _fake_declared({"solo": {}})
    findings, _ = compare(declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].scope == "solo/production"
    assert findings[0].drift_class == DriftClass.BLOCKING
