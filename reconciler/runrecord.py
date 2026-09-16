"""Run record writer and summary line (spec 53.1, 0.5, 40.1 D89).

"Every reconciliation run writes its result, and a clean run is
recorded as clean." A RunRecord is what a Phase 1+ CLI run produces:
one row per comparator's compared-row count, the findings it raised,
whether the seeded canary was found, and whether the run itself
succeeded.

write() refuses to serialise into records/** or events/** — those
trees belong to Lane 4 (D89; AT-110's negative attempt 5), and the
reconciler credential must never be given a path that reaches them.

to_dict()'s key set is intended to match the ``run_record`` contract
published under contracts/schemas/ once L3-P0-03 resolves L3-D2's five
concrete schema paths; that task is blocked (the paths were never
recorded, only the directory layout was), so this module defines its
own explicit, documented shape rather than importing a contract that
does not yet exist on disk.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

from reconciler.model import Finding

### L3-P1-16 - per-registry comparison counts (spec 53.1: "Every run
### additionally records its per-registry comparison counts ... so that
### a silently narrowed comparison is itself visible drift").
###
### FD-061 sets the eventual target at 19 comparison entries, with
### L3-01 as the authoritative decomposition. Sixteen of those entries
### have a settled id and a settled minimum today: the fourteen named
### directly by L3-P1-02..P1-15 (including branch_protection=2 and
### environments=4, whose own comparator modules are built by
### L3-P1-06/L3-P1-08 - not this cluster's tasks), plus display_name=1
### (L3-P1-17) and checkrun_identity=2 (L3-P3-03, Phase 3). The
### remaining three entries are explicitly unresolved: L3-99-review.md
### finding B6 records that L3-01's and L3-06's decompositions of
### spec 53.1 were never reconciled into one authoritative manifest, so
### three comparator identities (and their minimums) have no name to
### transcribe yet, only a placeholder in the task file's own comment.
### Inventing three ids or values here would be exactly the ad hoc
### class/config decision spec 53.4 reserves for L0 - so this table
### holds the sixteen that are actually specified, and
### narrowed_comparators() below only ever evaluates a comparator id
### against this table once that id is both registered *and* present
### in a run's comparison_counts - an unbuilt comparator (any of
### branch_protection, environments, checkrun_identity, or the three
### unresolved ids) is absent from every run today and is therefore
### never treated as "narrowed"; it is simply not yet built.
EXPECTED_MINIMUM_COUNTS: dict[str, int] = {
    "org_membership": 5,
    "capability_authority": 5,
    "team_membership": 2,
    "codeowners": 2,
    "branch_protection": 2,
    "workflow_version": 2,
    "environments": 4,
    "expiry": 1,
    "workflow_tag_sha": 1,
    "renovate_bypass": 2,
    "machine_authorship": 2,
    "infra_attestation": 2,
    "write_freshness": 3,
    "restore_tested": 2,
    "display_name": 1,
    "checkrun_identity": 2,
}


def narrowed_comparators(comparison_counts: dict[str, int]) -> list[str]:
    """Every comparator id present in `comparison_counts` whose actual
    count fell below its EXPECTED_MINIMUM_COUNTS floor - a silently
    narrowed comparison is itself visible drift (spec 53.1). A
    comparator id with no entry in comparison_counts at all (because it
    is not yet built, or a --only run did not select it) is not
    evaluated here - see the module-level note above this table."""
    return sorted(
        cid
        for cid, minimum in EXPECTED_MINIMUM_COUNTS.items()
        if cid in comparison_counts and comparison_counts[cid] < minimum
    )


REQUIRED_KEYS = (
    "run_id",
    "started_at",
    "finished_at",
    "status",
    "findings",
    "comparison_counts",
    "canary_found",
    "external_cause",
)

_REFUSED_PREFIXES = ("records/", "events/")


class RefusedWritePath(PermissionError):
    """Raised by RunRecord.write() for any path under records/ or events/."""


def _finding_to_dict(finding: Finding) -> dict:
    d = dataclasses.asdict(finding)
    d["drift_class"] = finding.drift_class.value
    d["level"] = int(finding.level)
    return d


@dataclass
class RunRecord:
    run_id: str
    started_at: str
    finished_at: str
    status: str  # "OK" | "FAILED"
    findings: list[Finding] = field(default_factory=list)
    comparison_counts: dict[str, int] = field(default_factory=dict)
    canary_found: bool = False
    external_cause: str | None = None

    def __post_init__(self):
        if self.status not in ("OK", "FAILED"):
            raise ValueError(f"status must be 'OK' or 'FAILED', got {self.status!r}")

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "findings": [_finding_to_dict(f) for f in self.findings],
            "comparison_counts": dict(self.comparison_counts),
            "canary_found": self.canary_found,
            "external_cause": self.external_cause,
        }

    def summary_lines(self) -> list[str]:
        """The spec 0.5 deterministic summary: one line per comparator key
        in comparison_counts, in insertion order, then the CANARY line."""
        lines = []
        for key, compared in self.comparison_counts.items():
            findings_for_key = sum(1 for f in self.findings if f.comparator == key)
            lines.append(f"{self.status} {key} findings={findings_for_key} compared={compared}")
        lines.append("CANARY found" if self.canary_found else "CANARY missing")
        return lines

    def write(self, path: str | Path) -> Path:
        posix = PurePosixPath(str(path).replace("\\", "/"))
        for prefix in _REFUSED_PREFIXES:
            if str(posix).startswith(prefix):
                raise RefusedWritePath(
                    f"refusing to write the run record into {prefix!r} "
                    "(records/** and events/** belong to Lane 4 - spec 40.1 D89)"
                )
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(self.to_dict(), sort_keys=False), encoding="utf-8")
        return out
