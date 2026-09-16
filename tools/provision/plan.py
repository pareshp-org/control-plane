"""L3-P4-01: the provisioning plan model (spec Section 7 preamble, §12.6).

Every provisioning operation (`create-product`, `add-person`,
`change-role`, `remove-person`) builds one ``Plan`` of ``Step``s before it
does anything else. A ``Plan`` never performs a mutation itself -- it is
the thing a CLI command prints in ``--dry-run`` mode, and the thing an
``--apply --live`` run walks step by step, recording which steps actually
executed.

The dry-run summary line every Phase-4 operation prints is fixed by
Section 7's preamble:

    PLAN <operation> steps=<int> writes=<int> manual=<int>

``writes`` is the count of mutations *actually performed* -- in
``--dry-run`` (the default, always, per L3-P4-01) it is ``0``. ``manual``
is the count of steps of kind ``manual``: the tracked issues a plan
emits wherever the provider offers no automation (Section 19.1), so a
manual step is never silently missing from the plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StepKind(str, Enum):
    """The three kinds of provisioning step. No fourth kind."""

    WRITE = "write"
    MANUAL = "manual"
    READ = "read"


@dataclass(frozen=True)
class Step:
    """One step of a provisioning plan.

    ``id`` is a short, stable, machine-referenceable token (e.g.
    ``"team-alpha"``); ``description`` is the human-readable summary a
    ``--summary`` run prints; ``kind`` says whether executing this step
    would mutate GitHub state (``write``), only read it (``read``), or
    is a step no API can perform and that a human must carry out
    (``manual``).
    """

    id: str
    description: str
    kind: StepKind

    def __post_init__(self) -> None:
        if not isinstance(self.kind, StepKind):
            try:
                object.__setattr__(self, "kind", StepKind(self.kind))
            except ValueError as exc:
                raise ValueError(
                    f"Step {self.id!r} has kind {self.kind!r}; "
                    f"must be one of {[k.value for k in StepKind]}"
                ) from exc


@dataclass
class Plan:
    """An ordered list of steps for one provisioning operation."""

    steps: list[Step] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.steps)

    def count(self, kind: StepKind) -> int:
        return sum(1 for step in self.steps if step.kind == kind)

    def summary_line(self, operation: str, *, applied: bool = False) -> str:
        """Render the Section 7 dry-run summary line.

        ``applied`` is False for every dry-run (the CLI default and the
        only mode this skeleton ever exercises without ``--apply
        --live``): writes is then always 0, regardless of how many
        write-kind steps the plan holds, because none of them ran.
        """
        writes = self.count(StepKind.WRITE) if applied else 0
        manual = self.count(StepKind.MANUAL)
        return f"PLAN {operation} steps={len(self.steps)} writes={writes} manual={manual}"
