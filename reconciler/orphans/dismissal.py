"""L3-P2-06: Blocking orphans are non-dismissible; SIG-05 emission.

Spec §12.2 ("Blocking orphans ... cannot be dismissed without
resolution"); §101 invariant 57; §52.2 SIG-05 (Blocking, owner Team
Lead).

`dismiss()` raises `NonDismissibleOrphan` for any finding whose
`orphan_severity` is `Blocking`, regardless of actor or reason -
invariant 57 leaves no override path, so this function does not even
branch on `actor` before refusing. A non-Blocking finding may be
dismissed, but only with a linked resolution reference; a dismissal
with no resolution is not a dismissal, it is an unrecorded suppression,
which invariant 57's neighbourhood forbids just as firmly.

SIG-05 emission itself lives in `reconciler.signals.emit_signals()` -
this module's `sig05_products()` is the pure predicate that function
calls (spec's own instruction: "Extend emit_signals()"), kept here
because it is the same §12.2 vocabulary this module already owns.
"""

from __future__ import annotations

from dataclasses import dataclass

from reconciler.orphans import OrphanFinding

# The three §12.2 types SIG-05's own row names: a product's Primary
# Owner, Cross-Reviewer, or (via "named responder") Primary Responder
# slot. Type 5 (shared service) and type 3 (Backup Owner, High not
# Blocking) are deliberately excluded - SIG-05's row text is scoped to
# product-structure slots, not every ownership-group orphan.
SIG05_TRIGGER_INDICES: frozenset[int] = frozenset({1, 2, 4})


class NonDismissibleOrphan(Exception):
    """Raised by `dismiss()` for any Blocking-severity orphan finding.

    Invariant 57 admits no exception: not for a different reason, not
    for an actor holding `platform-admin`. There is no bypass
    parameter on this function for a reason - adding one would be the
    bug, not the fix.
    """


@dataclass(frozen=True)
class Dismissal:
    finding: OrphanFinding
    actor: str
    reason: str
    resolution_ref: str


def dismiss(
    finding: OrphanFinding,
    actor: str,
    reason: str,
    *,
    resolution_ref: str | None = None,
) -> Dismissal:
    """Dismiss `finding` on `actor`'s authority, for `reason`.

    Raises `NonDismissibleOrphan` unconditionally when
    `finding.orphan_severity == "Blocking"`. For any other severity,
    raises `ValueError` unless `resolution_ref` is given and non-empty
    - a dismissal is only ever a record of resolution, never a bare
    override.
    """
    if finding.orphan_severity == "Blocking":
        raise NonDismissibleOrphan(
            f"orphan type {finding.index} ({finding.name}) on {finding.subject!r} is "
            f"Blocking and cannot be dismissed without resolution (invariant 57); "
            f"actor={actor!r} reason={reason!r} confer no exception"
        )
    if not resolution_ref:
        raise ValueError(
            f"dismissing a {finding.orphan_severity} orphan requires a linked resolution_ref"
        )
    return Dismissal(finding=finding, actor=actor, reason=reason, resolution_ref=resolution_ref)


def sig05_products(orphan_findings: list[OrphanFinding]) -> list[str]:
    """The distinct product ids (in first-seen order) carrying at least
    one orphaned Primary Owner, Cross-Reviewer or Primary Responder
    slot - i.e. the products SIG-05 fires for."""
    seen: list[str] = []
    for finding in orphan_findings:
        if finding.index in SIG05_TRIGGER_INDICES and finding.subject not in seen:
            seen.append(finding.subject)
    return seen
