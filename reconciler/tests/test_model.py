"""L3-P0-05: finding model, drift classes, levels."""

import dataclasses

import pytest

from reconciler.model import (
    BLOCKS_WORK,
    RESPONSE_TIME,
    DriftClass,
    Finding,
    Level,
    security_floor,
)


def test_exactly_four_drift_classes():
    assert len(DriftClass) == 4
    assert {m.name for m in DriftClass} == {"GREEN", "AMBER", "RED", "BLOCKING"}


def test_exactly_five_levels():
    assert len(Level) == 5
    assert {m.name for m in Level} == {"DETECT", "WARN", "AUTO_REPAIR", "BLOCK", "ESCALATE"}
    assert [int(Level.DETECT), int(Level.WARN), int(Level.AUTO_REPAIR), int(Level.BLOCK), int(Level.ESCALATE)] == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_response_time_matches_spec_53_4():
    assert RESPONSE_TIME[DriftClass.GREEN] is None
    assert RESPONSE_TIME[DriftClass.AMBER] == "next_planning_cycle_h2"
    assert RESPONSE_TIME[DriftClass.RED] == "2_business_days"
    assert RESPONSE_TIME[DriftClass.BLOCKING] == "immediate"


def test_blocks_work_matches_spec_53_4():
    assert BLOCKS_WORK[DriftClass.GREEN] is False
    assert BLOCKS_WORK[DriftClass.AMBER] is False
    assert BLOCKS_WORK[DriftClass.RED] is False
    assert BLOCKS_WORK[DriftClass.BLOCKING] is True


def test_security_floor():
    assert security_floor(DriftClass.GREEN, True) is DriftClass.RED
    assert security_floor(DriftClass.AMBER, True) is DriftClass.RED
    assert security_floor(DriftClass.BLOCKING, True) is DriftClass.BLOCKING
    assert security_floor(DriftClass.RED, True) is DriftClass.RED
    assert security_floor(DriftClass.GREEN, False) is DriftClass.GREEN


def test_finding_is_frozen():
    finding = Finding(
        id="F1",
        comparator="CMP-01",
        scope="alpha",
        drift_class=DriftClass.GREEN,
        level=Level.DETECT,
        evidence="e",
        first_seen="2026-08-27T00:00:00Z",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        finding.id = "F2"
