"""L3-P1-16: per-registry comparison counts on the run record.

FD-061 sets the eventual comparison-set target at 19 entries with
L3-01 authoritative, but three of those ids remain genuinely
unresolved (L3-99-review.md finding B6: L3-01's and L3-06's
decompositions of spec 53.1 were never reconciled into one manifest).
This cluster does not invent the missing three - EXPECTED_MINIMUM_COUNTS
holds the sixteen that are actually named and valued today, and this
suite tests the mechanism (the floor table and the narrowing check)
rather than asserting a "19" this build cannot yet produce. See the
runrecord.py module comment above EXPECTED_MINIMUM_COUNTS for the full
accounting of which ids are outstanding and why.
"""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState, main
from reconciler.runrecord import EXPECTED_MINIMUM_COUNTS, narrowed_comparators
from reconciler.state.fixture_adapter import FixtureState


def test_expected_minimum_counts_matches_the_spec_table_exactly():
    # Asserted by test, not left as a comment (L3-P1-16 acceptance #3).
    assert EXPECTED_MINIMUM_COUNTS == {
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


def test_lowering_one_comparators_count_flips_it_to_narrowed():
    healthy = {cid: minimum for cid, minimum in EXPECTED_MINIMUM_COUNTS.items()}
    assert narrowed_comparators(healthy) == []

    narrowed_input = dict(healthy)
    narrowed_input["org_membership"] = healthy["org_membership"] - 1
    assert narrowed_comparators(narrowed_input) == ["org_membership"]


def test_full_fixture_a_run_narrows_nothing_among_its_registered_comparators():
    # Every comparator this cluster has actually registered meets its
    # floor on fixture-a; branch_protection/environments/display_name/
    # checkrun_identity and the three unresolved ids are simply absent
    # from comparison_counts (not yet built) and are therefore not
    # evaluated - see narrowed_comparators' own docstring.
    from reconciler.cli import _load_comparators
    from reconciler.registry import COMPARATORS
    from reconciler.state.fixture_adapter import FixtureState as _FS

    _load_comparators()
    declared = DeclaredState("fixture-a")
    actual = _FS("fixture-a")
    as_of = date(2026, 8, 27)
    comparison_counts = {cid: fn(declared, actual, as_of)[1] for cid, fn in COMPARATORS.items()}
    assert narrowed_comparators(comparison_counts) == []
    assert len(comparison_counts) == len(COMPARATORS)
