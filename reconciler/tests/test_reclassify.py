"""Tests for reconciler.reclassify (L3-P3-05)."""

from __future__ import annotations

import pytest

from reconciler.model import DriftClass, Finding, Level
from reconciler.reclassify import (
    EXCEPTION_APPROVAL_CAPABILITY,
    ReclassificationRefused,
    reclassify,
)

RED_FINDING = Finding(
    id="write_freshness:events/",
    comparator="write_freshness",
    scope="events/",
    drift_class=DriftClass.RED,
    level=Level.WARN,
    evidence="test",
    first_seen="2026-08-27T00:00:00Z",
)

FOUNDER = {"github_login": "founder-1", "capabilities": [EXCEPTION_APPROVAL_CAPABILITY]}
LEAD = {"github_login": "lead-1", "capabilities": ["escalation", "code-review"]}


def test_downward_without_decision_id_raises():
    with pytest.raises(ReclassificationRefused):
        reclassify(RED_FINDING, DriftClass.AMBER, FOUNDER, decision_record_id=None)


def test_downward_with_id_but_no_authority_raises():
    with pytest.raises(ReclassificationRefused):
        reclassify(RED_FINDING, DriftClass.AMBER, LEAD, decision_record_id="DEC-001")


def test_downward_with_id_and_authority_succeeds_and_records():
    new_finding, record = reclassify(RED_FINDING, DriftClass.AMBER, FOUNDER, decision_record_id="DEC-001")
    assert new_finding.drift_class == DriftClass.AMBER
    assert record.direction == "downward"
    assert record.decision_record_id == "DEC-001"
    assert record.actor == "founder-1"
    assert record.from_class == DriftClass.RED
    assert record.to_class == DriftClass.AMBER


def test_upward_always_succeeds_and_records_without_id_or_authority():
    new_finding, record = reclassify(RED_FINDING, DriftClass.BLOCKING, LEAD, decision_record_id=None)
    assert new_finding.drift_class == DriftClass.BLOCKING
    assert record.direction == "upward"
    assert record.decision_record_id is None


def test_same_class_is_not_downward_and_needs_no_authority():
    new_finding, record = reclassify(RED_FINDING, DriftClass.RED, LEAD, decision_record_id=None)
    assert new_finding.drift_class == DriftClass.RED
    assert record.direction == "upward"
