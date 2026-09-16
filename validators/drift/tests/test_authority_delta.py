"""L3-P7-04: the authority-delta detector (spec 26.4 rule two; FD-025)."""

from __future__ import annotations

from validators.drift.authority_delta import (
    WRITE_ASSIGNMENT_TYPES,
    RegistryDiff,
    RegistryEntry,
    detect,
)


def test_capability_added_is_detected():
    diff = RegistryDiff(
        before=RegistryEntry(capabilities=frozenset({"read"})),
        after=RegistryEntry(capabilities=frozenset({"read", "deploy_prod"})),
    )
    deltas = detect(diff)
    assert len(deltas) == 1
    assert deltas[0].kind == "capability_added"
    assert deltas[0].passes is False  # no decision_record_ids on the diff


def test_every_write_conferring_assignment_type_is_detected():
    assert WRITE_ASSIGNMENT_TYPES == {
        "primary_owner",
        "cross_reviewer",
        "backup_owner",
        "temporary_contributor",
    }
    for kind in WRITE_ASSIGNMENT_TYPES:
        diff = RegistryDiff(
            before=RegistryEntry(assignments=()),
            after=RegistryEntry(assignments=({"login": "dev-1", "type": kind},)),
        )
        deltas = detect(diff)
        assert len(deltas) == 1, kind
        assert deltas[0].kind == "write_assignment_added", kind


def test_access_status_changed_is_detected():
    diff = RegistryDiff(
        before=RegistryEntry(access_status="active"),
        after=RegistryEntry(access_status="revoked"),
    )
    deltas = detect(diff)
    assert len(deltas) == 1
    assert deltas[0].kind == "access_status_changed"


def test_display_name_only_change_is_not_a_delta():
    # display_name is deliberately not modelled on RegistryEntry at
    # all - a diff that changes nothing this module tracks yields no
    # delta, by construction.
    diff = RegistryDiff(before=RegistryEntry(), after=RegistryEntry())
    assert detect(diff) == []


def test_non_write_assignment_type_added_is_not_a_delta():
    # "read_reviewer" (or anything outside WRITE_ASSIGNMENT_TYPES)
    # confers no Write, so adding it is not an authority delta.
    diff = RegistryDiff(
        before=RegistryEntry(assignments=()),
        after=RegistryEntry(assignments=({"login": "dev-1", "type": "read_reviewer"},)),
    )
    assert detect(diff) == []


def test_delta_with_a_linked_decision_record_passes():
    diff = RegistryDiff(
        before=RegistryEntry(capabilities=frozenset()),
        after=RegistryEntry(capabilities=frozenset({"deploy_prod"})),
        decision_record_ids=("DR-2026-091",),
    )
    deltas = detect(diff)
    assert len(deltas) == 1
    assert deltas[0].linked is True
    assert deltas[0].passes is True


def test_delta_without_a_linked_decision_record_fails():
    diff = RegistryDiff(
        before=RegistryEntry(capabilities=frozenset()),
        after=RegistryEntry(capabilities=frozenset({"deploy_prod"})),
        decision_record_ids=(),
    )
    deltas = detect(diff)
    assert len(deltas) == 1
    assert deltas[0].linked is False
    assert deltas[0].passes is False
