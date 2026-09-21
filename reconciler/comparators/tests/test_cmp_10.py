"""L3-P0-CMP10: lifecycle vs Renovate, monitoring and CI configuration."""

from __future__ import annotations

from datetime import date

from reconciler.comparators.cmp_10_lifecycle import compare, load_table
from reconciler.model import DriftClass, Level

_CONFORMANT_WORKFLOWS = {"renovate.yml": {}, "ci.yml": {}}
_ALIVE_CHECK_RUNS = {"ci": {"conclusion": "success"}}


class _FakeActual:
    def __init__(self, workflows=None, check_runs=None):
        self._workflows = _CONFORMANT_WORKFLOWS if workflows is None else workflows
        self._check_runs = _ALIVE_CHECK_RUNS if check_runs is None else check_runs

    def workflow_files(self, repo):
        return dict(self._workflows)

    def check_runs(self, repo):
        return dict(self._check_runs)


def _declared(lifecycle="active", alert_channel="#alerts-alpha"):
    product = {"lifecycle": lifecycle}
    if alert_channel is not None:
        product["observability"] = {"alert_channel": alert_channel}

    class _FakeDeclared:
        products = {"alpha": product}

    return _FakeDeclared()


def test_the_table_covers_every_section_18_1_lifecycle_state():
    table = load_table()
    assert table["states"] == ["active", "maintenance", "paused", "sunset", "archived"]
    for check in table["checks"]:
        assert set(check["expected_by_state"]) == set(table["states"]), check["id"]


def test_the_archive_flag_and_workflow_checks_are_the_only_unsafe_ones():
    unsafe = {c["id"] for c in load_table()["checks"] if not c["safe"]}
    assert unsafe == {"repository-archived-flag", "ci-workflow-present"}


def test_a_conformant_active_product_produces_no_finding():
    findings, compared = compare(_declared(), _FakeActual(), date(2026, 9, 16))
    assert findings == []
    assert compared == 1


def test_a_missing_renovate_schedule_proposes_a_repair_and_never_applies_it():
    actual = _FakeActual(workflows={"ci.yml": {}})
    findings, _ = compare(_declared(), actual, date(2026, 9, 16))
    assert len(findings) == 1
    finding = findings[0]
    assert finding.level == Level.AUTO_REPAIR
    assert finding.drift_class == DriftClass.AMBER
    assert "renovate-schedule-present" in finding.evidence
    assert "'applied': False" in finding.evidence


def test_a_missing_ci_workflow_alerts_and_proposes_nothing():
    actual = _FakeActual(workflows={"renovate.yml": {}})
    findings, _ = compare(_declared(), actual, date(2026, 9, 16))
    assert len(findings) == 1
    finding = findings[0]
    assert finding.level == Level.WARN
    assert finding.drift_class == DriftClass.AMBER
    assert "ci-workflow-present" in finding.evidence
    assert "applied" not in finding.evidence


def test_an_archived_product_with_a_still_present_ci_workflow_alerts_only():
    actual = _FakeActual(workflows={"ci.yml": {}}, check_runs={})
    findings, _ = compare(_declared(lifecycle="archived", alert_channel=None), actual, date(2026, 9, 16))
    assert len(findings) == 1
    finding = findings[0]
    assert finding.level == Level.WARN
    assert "ci-workflow-present" in finding.evidence
