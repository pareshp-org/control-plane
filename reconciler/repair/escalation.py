"""L3-P6-10: repeated failed repair escalates to Level 5 (spec 53.2
Level 5: "repeated failed auto-repair", "a repair class discovered to
have written incorrect state").

`evaluate()` looks at one repair class's own attempt history against
one scope and raises once the trailing run of consecutive failures
reaches `threshold` (spec configuration; initial value 3). Escalation
means creating an incident and notifying the escalation role - this
module emits the escalation object only (the raised exception, whose
`.level` is `Level.ESCALATE`); routing that notification belongs to
Lane 5's `notify/**`, and nothing here calls into it, or into any
network client of any kind.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from reconciler.model import Level

DEFAULT_THRESHOLD = 3


class RepairEscalation(Exception):
    """Raised by evaluate() once a repair class's consecutive-failure
    count against one scope reaches its threshold. `.level` is always
    `Level.ESCALATE` - this is the one place in the Phase 6 package
    that reaches Level 5."""

    def __init__(self, repair_class: str, scope: str, consecutive_failures: int, level: Level):
        self.repair_class = repair_class
        self.scope = scope
        self.consecutive_failures = consecutive_failures
        self.level = level
        super().__init__(
            f"{repair_class} has failed {consecutive_failures} consecutive times against "
            f"{scope!r}; escalating to {level.name} (spec 53.2 Level 5)"
        )


def _consecutive_trailing_failures(attempts: Sequence[Mapping[str, object]]) -> int:
    count = 0
    for attempt in reversed(attempts):
        if attempt.get("outcome") == "failure":
            count += 1
        else:
            break
    return count


def evaluate(repair_history: Sequence[Mapping[str, object]], threshold: int = DEFAULT_THRESHOLD) -> Level:
    """`repair_history` is every attempt so far for one (repair_class,
    scope) pair, in chronological order, each entry shaped at least
    `{"repair_class": str, "scope": str, "outcome": "success"|"failure"}`.

    Raises `RepairEscalation` (`.level` is `Level.ESCALATE`) once the
    trailing run of failures reaches `threshold`; a success anywhere
    in the history resets the count that follows it. Otherwise returns
    `Level.AUTO_REPAIR` - the normal level a repair class runs at,
    un-escalated.
    """
    if threshold < 1:
        raise ValueError(f"threshold must be >= 1, got {threshold}")

    consecutive = _consecutive_trailing_failures(repair_history)
    if consecutive >= threshold:
        last = repair_history[-1]
        raise RepairEscalation(
            str(last.get("repair_class", "unknown")),
            str(last.get("scope", "unknown")),
            consecutive,
            Level.ESCALATE,
        )
    return Level.AUTO_REPAIR
