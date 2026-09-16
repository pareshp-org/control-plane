"""L3-P2-01: the sixteen-type orphan severity map (spec §12.2).

`ORPHAN_TYPES` is the ordered, verbatim transcription of the sixteen-row
table at spec §12.2 - one frozen `OrphanType` per row, in the printed
order. No row here is reworded, merged, renumbered or reordered; a
detector module (ownership.py, assets.py, governance.py) looks up its
own rows by index via `BY_INDEX` rather than re-stating the name or
severity itself, so there is exactly one place in the lane that can get
a transcription wrong.

`GROUPS` partitions the sixteen indices into the three `--group` values
the CLI accepts: `ownership` (1-5), `assets` (6-10), `governance`
(11-16). The partition is exhaustive and non-overlapping by
construction (three contiguous `range()` slices covering 1-16); the
test suite still asserts this explicitly so a future edit that breaks
the partition fails loudly rather than silently dropping a type.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrphanType:
    """One row of the spec §12.2 table."""

    index: int
    name: str
    detection_source: str
    orphan_severity: str


# Transcribed verbatim, row for row, from spec §12.2.
ORPHAN_TYPES: tuple[OrphanType, ...] = (
    OrphanType(1, "Product with no Primary Owner", "Assignment registry", "Blocking"),
    OrphanType(2, "Product with no Cross-Reviewer", "Assignment registry", "Blocking"),
    OrphanType(3, "Product with no Backup Owner", "Assignment registry", "High"),
    OrphanType(4, "Product with no Primary Responder", "Contract operations block", "Blocking"),
    OrphanType(5, "Shared service with no owner", "Service registry", "Blocking"),
    OrphanType(6, "Certificate with no owner", "Asset inventory", "High"),
    OrphanType(7, "Domain with no owner", "Asset inventory", "Blocking"),
    OrphanType(8, "Vendor relationship with no owner", "Asset inventory", "Medium"),
    OrphanType(9, "Operational asset with no owner", "Asset inventory", "Medium"),
    OrphanType(10, "Customer commitment with no owner", "Contract operations block", "Blocking"),
    OrphanType(11, "Platform migration with no owner", "Compatibility state", "High"),
    OrphanType(12, "Verification responsibility unassigned", "Assignment registry", "High"),
    OrphanType(13, "In-flight H1 work with no assignee", "Board", "High"),
    OrphanType(
        14,
        "Temporary person expired with open gate-relevant work",
        "Assignment registry + open reviews and gate items at expiry",
        "High",
    ),
    OrphanType(15, "Policy with no owner", "Policy register", "Blocking"),
    OrphanType(16, "Open exception whose requester or authority has departed", "Exception registry", "High"),
)

BY_INDEX: dict[int, OrphanType] = {t.index: t for t in ORPHAN_TYPES}

# `--group` partition (spec §12.2 groupings used by L3-P2-02..04).
GROUPS: dict[str, tuple[int, ...]] = {
    "ownership": tuple(range(1, 6)),
    "assets": tuple(range(6, 11)),
    "governance": tuple(range(11, 17)),
}

# The seven Blocking-severity rows, spelled out once so a test can
# assert against a literal rather than re-deriving it from ORPHAN_TYPES
# (which would just be testing the code against itself).
BLOCKING_INDICES: frozenset[int] = frozenset({1, 2, 4, 5, 7, 10, 15})
