"""Tests for reconciler.checkrun (L3-P3-02)."""

from __future__ import annotations

import pytest

from reconciler.checkrun import CHECK_NAME, InvalidCheckName, publish
from reconciler.model import DriftClass, Finding, Level


def _finding(drift_class: DriftClass, scope: str = "beta") -> Finding:
    return Finding(
        id=f"x:{scope}",
        comparator="x",
        scope=scope,
        drift_class=drift_class,
        level=Level.BLOCK if drift_class == DriftClass.BLOCKING else Level.WARN,
        evidence="test",
        first_seen="2026-08-27T00:00:00Z",
    )


def test_dry_run_is_the_default_and_makes_no_client_call():
    result = publish("beta", [])
    assert result.dry_run is True
    assert result.published is False


def test_invalid_name_raises_before_anything_else():
    with pytest.raises(InvalidCheckName):
        publish("beta", [], name="some-other-check")


def test_one_blocking_finding_yields_failure_conclusion():
    result = publish("beta", [_finding(DriftClass.BLOCKING)])
    assert result.conclusion == "failure"
    assert result.name == CHECK_NAME


def test_no_findings_yields_success_conclusion():
    result = publish("beta", [])
    assert result.conclusion == "success"


def test_non_blocking_findings_do_not_trigger_failure():
    findings = [_finding(DriftClass.RED), _finding(DriftClass.AMBER), _finding(DriftClass.GREEN)]
    result = publish("beta", findings)
    assert result.conclusion == "success"


class _FakeClient:
    def __init__(self):
        self.calls = []

    def create_check_run(self, *, repo, name, conclusion):
        self.calls.append((repo, name, conclusion))


def test_live_path_requires_explicit_dry_run_false_and_calls_client():
    client = _FakeClient()
    result = publish("beta", [_finding(DriftClass.BLOCKING)], dry_run=False, client=client)
    assert result.published is True
    assert client.calls == [("beta", CHECK_NAME, "failure")]
