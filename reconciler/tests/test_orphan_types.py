"""L3-P2-01: orphan framework and the sixteen-type severity map."""

from __future__ import annotations

from reconciler.orphans.types import BLOCKING_INDICES, GROUPS, ORPHAN_TYPES


def test_exactly_sixteen_entries_indexed_one_through_sixteen_in_order():
    assert len(ORPHAN_TYPES) == 16
    assert [t.index for t in ORPHAN_TYPES] == list(range(1, 17))


def test_exactly_seven_blocking_rows_at_the_named_indices():
    blocking = {t.index for t in ORPHAN_TYPES if t.orphan_severity == "Blocking"}
    assert len(blocking) == 7
    assert blocking == {1, 2, 4, 5, 7, 10, 15}
    assert blocking == BLOCKING_INDICES


def test_groups_partition_one_through_sixteen_with_no_overlap_and_no_gap():
    assert set(GROUPS) == {"ownership", "assets", "governance"}
    all_indices: list[int] = []
    for indices in GROUPS.values():
        all_indices.extend(indices)
    assert sorted(all_indices) == list(range(1, 17))  # no gap
    assert len(all_indices) == len(set(all_indices))  # no overlap
    assert set(GROUPS["ownership"]) == {1, 2, 3, 4, 5}
    assert set(GROUPS["assets"]) == {6, 7, 8, 9, 10}
    assert set(GROUPS["governance"]) == {11, 12, 13, 14, 15, 16}
