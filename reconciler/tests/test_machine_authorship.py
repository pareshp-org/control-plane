"""L3-P1-12: machine workflow-file change and bypass-branch authorship comparator."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.machine_authorship import compare
from reconciler.model import DriftClass, Level
from reconciler.state.fixture_adapter import FixtureState


def test_fixture_a_exactly_two_findings_both_blocking():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = compare(declared, actual, date(2026, 8, 27))
    assert compared == 2
    assert len(findings) == 2
    assert all(f.drift_class == DriftClass.BLOCKING for f in findings)
    assert all(f.level == Level.BLOCK for f in findings)
    scopes = {f.scope for f in findings}
    assert scopes == {"alpha/ci.yml", "renovate/dep-1"}


def test_human_pushed_workflow_file_is_never_flagged_and_never_counted():
    class FakeActual:
        def workflow_files(self, product):
            return {"ci.yml": {"pusher_is_machine": False, "last_pusher": "human-1"}}

        def bypass_branches(self):
            return []

    fake_declared = type("D", (), {"products": {"solo": {}}})()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 0


def test_bypass_branch_with_only_declared_actor_commits_is_clean_but_compared():
    class FakeActual:
        def workflow_files(self, product):
            return {}

        def bypass_branches(self):
            return [{"branch": "b1", "declared_bypass_actor": "renovate[bot]", "commit_authors": ["renovate[bot]"]}]

    fake_declared = type("D", (), {"products": {}})()
    findings, compared = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert findings == []
    assert compared == 1


def test_authorship_offense_is_never_downgraded_to_a_warning():
    # §33.2: "The authorship half is not optional." A lockfile-only
    # diff by a non-declared author must still be Blocking.
    class FakeActual:
        def workflow_files(self, product):
            return {}

        def bypass_branches(self):
            return [{"branch": "b1", "declared_bypass_actor": "renovate[bot]", "commit_authors": ["renovate[bot]", "dev-9"]}]

    fake_declared = type("D", (), {"products": {}})()
    findings, _ = compare(fake_declared, FakeActual(), date(2026, 8, 27))
    assert len(findings) == 1
    assert findings[0].drift_class == DriftClass.BLOCKING
