"""L3-P5-08: records-repository head SHA anchor."""

from __future__ import annotations

from reconciler.anchor import Anchor, anchor
from reconciler.model import DriftClass, Level


def test_the_first_ever_anchor_call_always_anchors_cleanly():
    new_anchor, finding = anchor("sha-1", 10, None)
    assert new_anchor == Anchor(sha="sha-1", commit_count=10)
    assert finding is None


def test_a_head_that_simply_has_not_moved_anchors_cleanly():
    previous = Anchor(sha="sha-1", commit_count=10)
    new_anchor, finding = anchor("sha-1", 10, previous)
    assert finding is None
    assert new_anchor == previous


def test_a_head_whose_ancestor_set_contains_the_previous_anchor_descends_cleanly():
    previous = Anchor(sha="sha-1", commit_count=10)
    new_anchor, finding = anchor(
        "sha-2",
        12,
        previous,
        ancestor_shas=frozenset({"sha-1", "sha-0"}),
    )
    assert finding is None
    assert new_anchor == Anchor(sha="sha-2", commit_count=12)


def test_a_head_not_descended_from_the_previous_anchor_is_blocking_escalate():
    previous = Anchor(sha="sha-1", commit_count=10)
    new_anchor, finding = anchor(
        "sha-rewritten",
        10,
        previous,
        ancestor_shas=frozenset({"sha-0"}),  # sha-1 is absent
    )
    assert finding is not None
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.level == Level.ESCALATE
    assert "sha-1" in finding.evidence
    assert "sha-rewritten" in finding.evidence
    # The broken chain is still anchored, so the next run has this run's
    # head to compare against rather than looping on the same gap.
    assert new_anchor == Anchor(sha="sha-rewritten", commit_count=10)


def test_a_non_descendant_head_with_no_ancestor_set_supplied_also_escalates():
    previous = Anchor(sha="sha-1", commit_count=10)
    new_anchor, finding = anchor("sha-2", 11, previous)
    assert finding is not None
    assert finding.drift_class == DriftClass.BLOCKING


def test_module_performs_no_write_to_the_records_repository_or_the_drift_events_store():
    import inspect

    import reconciler.anchor as anchor_module

    source = inspect.getsource(anchor_module)
    for banned_prefix in ("records/", "events/"):
        assert banned_prefix not in source
    for banned_call in ("open(", "Path(", ".write_text(", ".write(", "write_bytes"):
        assert banned_call not in source
