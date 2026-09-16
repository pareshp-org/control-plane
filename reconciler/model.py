"""There is exactly one drift severity scale, used everywhere. (spec 53.4)

This module is the single definition of drift classes, response levels,
and the Finding record every comparator produces. No other severity
vocabulary exists anywhere in this system: comparators, the run record,
the CLI and the reporting surfaces all import DriftClass and Level from
here rather than defining their own.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


class DriftClass(str, Enum):
    """The four drift severities of spec 53.4. No fifth member."""

    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"
    BLOCKING = "Blocking"


class Level(IntEnum):
    """The five response levels of spec 53.2. No sixth member."""

    DETECT = 1
    WARN = 2
    AUTO_REPAIR = 3
    BLOCK = 4
    ESCALATE = 5


# Transcribed cell for cell from the spec 53.4 table.
RESPONSE_TIME: dict[DriftClass, str | None] = {
    DriftClass.GREEN: None,
    DriftClass.AMBER: "next_planning_cycle_h2",
    DriftClass.RED: "2_business_days",
    DriftClass.BLOCKING: "immediate",
}

# Transcribed cell for cell from the spec 53.4 table.
BLOCKS_WORK: dict[DriftClass, bool] = {
    DriftClass.GREEN: False,
    DriftClass.AMBER: False,
    DriftClass.RED: False,
    DriftClass.BLOCKING: True,
}


@dataclass(frozen=True)
class Finding:
    """One drift finding produced by a comparator's compare()."""

    id: str
    comparator: str
    scope: str
    drift_class: DriftClass
    level: Level
    evidence: str
    first_seen: str
    acknowledged_by: str | None = None
    acknowledged_at: str | None = None
    external_cause: str | None = None
    gap_window: bool = False


def security_floor(drift_class: DriftClass, is_security_or_prod_env: bool) -> DriftClass:
    """Security drift and production environment drift are never
    classified below Red. (spec 53.4)

    Returns RED when ``drift_class`` is GREEN or AMBER and the flag is
    true; otherwise returns ``drift_class`` unchanged.
    """
    if is_security_or_prod_env and drift_class in (DriftClass.GREEN, DriftClass.AMBER):
        return DriftClass.RED
    return drift_class
