"""L3-P4-10: Pre-provisioning (T-minus-one-week) checklist emitter."""

from __future__ import annotations

from datetime import date

from tools.provision.preprovision import (
    ASSET_INVENTORY_ITEM,
    PREPROVISION_ITEMS,
    preprovision_checklist,
)


def test_preprovision_items_are_exactly_six_verbatim():
    assert PREPROVISION_ITEMS == (
        "GitHub account confirmed",
        "hardware ready",
        "email account created",
        "AI-runtime choice asked of the joiner",
        "the runtime seat purchased",
        "an asset-inventory entry recorded for issued hardware",
    )


def test_due_date_is_seven_days_before_start_date():
    checklist = preprovision_checklist("dev-3", "2026-09-21")
    assert checklist.due_date == date(2026, 9, 14)
    checklist_from_date = preprovision_checklist("dev-3", date(2026, 9, 21))
    assert checklist_from_date.due_date == checklist.due_date


def test_render_contains_all_six_items_and_both_dates():
    checklist = preprovision_checklist("dev-3", "2026-09-21")
    body = checklist.render()
    for item in PREPROVISION_ITEMS:
        assert item in body
    assert "2026-09-14" in body
    assert "2026-09-21" in body


def test_asset_inventory_item_names_section_49_and_is_not_written_here():
    checklist = preprovision_checklist("dev-3", "2026-09-21")
    body = checklist.render()
    assert ASSET_INVENTORY_ITEM in body
    assert "Section 49" in body
    assert "not written by this lane" in body
