"""L3-P6-02: repair enablement registry, every class default-off."""

from __future__ import annotations

import pytest

from reconciler.repair.enablement import (
    REPAIR_CLASSES,
    EnablementError,
    enable,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    reset_for_tests()
    yield
    reset_for_tests()


def test_all_five_classes_exist_and_default_off():
    assert set(REPAIR_CLASSES) == {
        "team_sync",
        "codeowners_regen",
        "label_sync",
        "protection_reapply",
        "expiry_revoke",
    }
    assert all(rc.enabled is False for rc in REPAIR_CLASSES.values())


def test_enabling_requires_a_decision_record_id():
    with pytest.raises(EnablementError):
        enable("team_sync", enabled_on="2026-09-15", enabled_by="")


def test_enabling_requires_an_enabled_on_date():
    with pytest.raises(EnablementError):
        enable("team_sync", enabled_on="", enabled_by="FD-200")


def test_enabling_two_classes_in_one_change_raises():
    with pytest.raises(EnablementError):
        enable(["team_sync", "label_sync"], enabled_on="2026-09-15", enabled_by="FD-200")
    assert REPAIR_CLASSES["team_sync"].enabled is False
    assert REPAIR_CLASSES["label_sync"].enabled is False


def test_enabling_one_class_with_all_three_succeeds():
    rc = enable("team_sync", enabled_on="2026-09-15", enabled_by="FD-200")
    assert rc.enabled is True
    assert rc.enabled_on == "2026-09-15"
    assert rc.enabled_by == "FD-200"
    assert REPAIR_CLASSES["team_sync"].enabled is True
    assert REPAIR_CLASSES["codeowners_regen"].enabled is False


def test_enabling_an_unknown_class_raises():
    with pytest.raises(EnablementError):
        enable("no_such_class", enabled_on="2026-09-15", enabled_by="FD-200")
