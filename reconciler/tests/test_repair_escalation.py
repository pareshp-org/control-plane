"""L3-P6-10: repeated failed repair escalates to Level 5."""

from __future__ import annotations

import pytest

from reconciler.model import Level
from reconciler.repair.escalation import RepairEscalation, evaluate


def _attempts(outcomes, repair_class="team_sync", scope="alpha:dev-2"):
    return [{"repair_class": repair_class, "scope": scope, "outcome": o} for o in outcomes]


def test_three_consecutive_failures_escalates():
    with pytest.raises(RepairEscalation) as exc_info:
        evaluate(_attempts(["failure", "failure", "failure"]))
    assert exc_info.value.level == Level.ESCALATE
    assert exc_info.value.consecutive_failures == 3
    assert exc_info.value.repair_class == "team_sync"
    assert exc_info.value.scope == "alpha:dev-2"


def test_two_failures_does_not_escalate():
    result = evaluate(_attempts(["failure", "failure"]))
    assert result == Level.AUTO_REPAIR


def test_a_success_resets_the_trailing_failure_streak():
    # failure, success, failure, failure - only two consecutive at the
    # tail, so no escalation despite four total attempts and three
    # total failures.
    result = evaluate(_attempts(["failure", "success", "failure", "failure"]))
    assert result == Level.AUTO_REPAIR


def test_custom_threshold_is_honoured():
    # threshold=1 escalates on the very first failure.
    with pytest.raises(RepairEscalation):
        evaluate(_attempts(["failure"]), threshold=1)
    # threshold=5 needs five, not three, consecutive failures.
    assert evaluate(_attempts(["failure"] * 4), threshold=5) == Level.AUTO_REPAIR


def test_no_history_never_escalates():
    assert evaluate([]) == Level.AUTO_REPAIR
