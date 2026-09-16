"""L3-P6-07: repair class: label and board field sync."""

from __future__ import annotations

from unittest.mock import patch

from reconciler.repair import label_sync


def test_diff_and_repair_syncs_a_changed_field():
    repairs = label_sync.diff_and_repair(
        "WI-101",
        {"horizon": "H1", "status": "in_progress"},
        {"horizon": "H2", "status": "in_progress"},
        enabled=True,
    )
    assert len(repairs) == 1
    assert repairs[0].after == {"horizon": "H1"}
    assert repairs[0].before == {"horizon": "H2"}
    assert repairs[0].repair_class == "label_sync"


def test_no_diff_produces_no_repair():
    fields = {"horizon": "H1", "status": "in_progress"}
    repairs = label_sync.diff_and_repair("WI-101", fields, dict(fields), enabled=True)
    assert repairs == []


def test_disabled_yields_no_repairs():
    repairs = label_sync.diff_and_repair(
        "WI-101", {"horizon": "H1"}, {"horizon": "H2"}, enabled=False
    )
    assert repairs == []


def test_touches_no_permission_protection_or_membership_control_kind():
    with patch("reconciler.repair.label_sync.permitted", wraps=label_sync.permitted) as spy:
        label_sync.diff_and_repair("WI-101", {"horizon": "H1"}, {"horizon": "H2"}, enabled=True)
    for call in spy.call_args_list:
        control_kind = call.args[2]
        assert control_kind == "label_and_board_field_set"
        assert control_kind not in {"branch_protection", "team_membership", "secret", "data"}


def test_calls_permitted_and_produces_repair_record_shape():
    items = {
        "WI-101": ({"horizon": "H1", "assignee": "dev-1"}, {"horizon": "H2", "assignee": ""}),
        "WI-102": ({"horizon": "H1"}, {"horizon": "H1"}),
    }
    with patch("reconciler.repair.label_sync.permitted", wraps=label_sync.permitted) as spy:
        repairs = label_sync.repair(items, enabled=True)
    assert spy.called
    by_field = {tuple(r.after.keys())[0]: r for r in repairs}
    assert set(by_field) == {"horizon", "assignee"}
    for r in repairs:
        assert r.permitted_reason
        assert r.compensating_action
