"""L3-P7-04: the authority-delta detector (spec 26.4 rule two; FD-025).

Section 26.4's second rule, transcribed: "an authority delta - a diff
that adds a capability, adds an assignment type conferring Write, or
changes `access_status` - fails CI without a linked decision record ID
in the same commit."

Why this exists, in the section's own words: "where a wrong revocation
is caught by orphan risk (SIG-05), a wrong grant has no detector at
all." Reconciliation's orphan machinery (reconciler/orphans/**) already
surfaces an access grant that should have been revoked but was not -
an over-broad *removal* is loud. Nothing upstream of this module
catches the opposite mistake: a registry pull request that silently
*widens* authority. This module is that missing detector, run as a CI
gate on registry diffs before merge - not at reconciliation time, and
not a repair.

FD-025 (2026-09-02) settles this module's ownership: "An authority
delta is a difference between declared state and actual platform
state - that is the definition of drift, and L3 owns validators/drift/
and the reconciler. One lane then owns the whole compare-declared-to-
actual surface." The now-superseded lanes/L3-03-canary-and-integrity.md
routed this work to L1 (`validators/registry/**`); FD-025 supersedes
that routing. This module therefore imports nothing from reconciler/**
(it guards the registry, not the instrument) and nothing from
validators/registry/** either - it is a self-contained CI-time check
over a registry diff, not a reconciliation-time comparator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

# spec 11.2: the assignment types that confer Write.
WRITE_ASSIGNMENT_TYPES = frozenset(
    {"primary_owner", "cross_reviewer", "backup_owner", "temporary_contributor"}
)

_KIND_CAPABILITY_ADDED = "capability_added"
_KIND_WRITE_ASSIGNMENT_ADDED = "write_assignment_added"
_KIND_ACCESS_STATUS_CHANGED = "access_status_changed"


@dataclass(frozen=True)
class RegistryEntry:
    """One registry record's fields relevant to authority (spec 11.2, 26.4).

    `assignments` is a sequence of {"type": ..., "login": ...} mappings.
    Fields irrelevant to authority (display_name and anything else) are
    deliberately not modelled here - a diff touching only those is not
    an authority delta and this module never looks at them.
    """

    capabilities: frozenset[str] = frozenset()
    assignments: tuple[Mapping[str, str], ...] = ()
    access_status: str | None = None


@dataclass(frozen=True)
class RegistryDiff:
    """A registry pull request's before/after state plus the decision
    record IDs findable in the same commit (parsed from the commit
    message, or from a decision-record file changed alongside it -
    this module takes the already-extracted list, not raw commit
    plumbing)."""

    before: RegistryEntry
    after: RegistryEntry
    decision_record_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorityDelta:
    """One authority-widening change §26.4 requires a decision record for."""

    kind: str
    detail: str
    linked: bool  # True iff decision_record_ids was non-empty on the diff

    @property
    def passes(self) -> bool:
        """False fails CI - no linked decision record ID."""
        return self.linked


def _write_assignment_keys(assignments: Sequence[Mapping[str, str]]) -> set[tuple[str, str]]:
    return {
        (a["login"], a["type"])
        for a in assignments
        if a.get("type") in WRITE_ASSIGNMENT_TYPES
    }


def detect(diff: RegistryDiff) -> list[AuthorityDelta]:
    """Return every authority delta in `diff`, recognising exactly the
    three kinds §26.4 names. A diff touching only fields outside those
    three (e.g. display_name) yields an empty list."""

    linked = bool(diff.decision_record_ids)
    deltas: list[AuthorityDelta] = []

    added_capabilities = diff.after.capabilities - diff.before.capabilities
    if added_capabilities:
        deltas.append(
            AuthorityDelta(
                kind=_KIND_CAPABILITY_ADDED,
                detail=f"capability added: {sorted(added_capabilities)}",
                linked=linked,
            )
        )

    before_write = _write_assignment_keys(diff.before.assignments)
    after_write = _write_assignment_keys(diff.after.assignments)
    added_write = after_write - before_write
    if added_write:
        deltas.append(
            AuthorityDelta(
                kind=_KIND_WRITE_ASSIGNMENT_ADDED,
                detail=f"Write-conferring assignment added: {sorted(added_write)}",
                linked=linked,
            )
        )

    if diff.before.access_status != diff.after.access_status:
        deltas.append(
            AuthorityDelta(
                kind=_KIND_ACCESS_STATUS_CHANGED,
                detail=(
                    f"access_status changed: {diff.before.access_status!r} -> "
                    f"{diff.after.access_status!r}"
                ),
                linked=linked,
            )
        )

    return deltas
