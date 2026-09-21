"""L3-P6-08: repair record emitter."""

from __future__ import annotations

import inspect

import pytest

from reconciler.repair import Repair
from reconciler.repair import records
from reconciler.repair.records import REQUIRED_KEYS, MissingCompensatingAction, emit, emit_all

PERFORMED_AT = "2026-08-27T00:00:00Z"
RUN_ID = "RECON-2026-08-27-001"


def _repair(**overrides) -> Repair:
    fields = {
        "repair_class": "team_sync",
        "finding_id": "team_membership:alpha:dev-2:unassigned",
        "scope": "alpha:dev-2",
        "before": {"team_member": True},
        "after": {"team_member": False},
        "permitted_reason": "dev-2 holds no current assignment on alpha",
        "compensating_action": "re-add dev-2 to the alpha Team if this was removed in error",
    }
    fields.update(overrides)
    return Repair(**fields)


def test_emit_produces_repairrecord_with_all_required_keys():
    record = emit(_repair(), performed_at=PERFORMED_AT, run_id=RUN_ID)
    as_dict = record.to_dict()
    assert set(as_dict) == set(REQUIRED_KEYS)
    assert len(as_dict) == 9


def test_emit_populates_before_and_after_from_the_source_repair():
    source = _repair(before={"team_member": True}, after={"team_member": False})
    record = emit(source, performed_at=PERFORMED_AT, run_id=RUN_ID)
    assert record.before == {"team_member": True}
    assert record.after == {"team_member": False}
    assert record.before is not None
    assert record.after is not None


def test_emit_stamps_performed_at_and_run_id():
    record = emit(_repair(), performed_at=PERFORMED_AT, run_id=RUN_ID)
    assert record.performed_at == PERFORMED_AT
    assert record.run_id == RUN_ID
    # A Repair itself never carries either field.
    assert not hasattr(_repair(), "performed_at")
    assert not hasattr(_repair(), "run_id")


def test_emit_all_produces_exactly_one_record_per_repair():
    repairs = [
        _repair(finding_id="team_membership:alpha:dev-2:unassigned", scope="alpha:dev-2"),
        _repair(finding_id="team_membership:gamma:owner-1:missing", scope="gamma:owner-1"),
        _repair(finding_id="expiry:beta:qa-1:expired", scope="beta:qa-1"),
    ]
    out = emit_all(repairs, performed_at=PERFORMED_AT, run_id=RUN_ID)
    assert len(out) == len(repairs)
    assert [r.finding_id for r in out] == [r.finding_id for r in repairs]


def test_missing_compensating_action_raises_at_emit_time():
    bad = _repair(compensating_action="")
    with pytest.raises(MissingCompensatingAction):
        emit(bad, performed_at=PERFORMED_AT, run_id=RUN_ID)


def test_blank_compensating_action_raises_at_emit_time():
    bad = _repair(compensating_action="   ")
    with pytest.raises(MissingCompensatingAction):
        emit(bad, performed_at=PERFORMED_AT, run_id=RUN_ID)


def test_module_never_writes_to_records_or_events_paths():
    # No filesystem-write capability exists in this module at all -
    # a RepairRecord is handed back in-memory (spec 40.1 D89; AT-110
    # attempt 5: records/** and events/** are never a write target the
    # reconciler credential reaches from this lane).
    assert not hasattr(records, "write")
    source = inspect.getsource(records)
    for banned in ("open(", "write_text(", ".write(", "Path("):
        assert banned not in source, f"{banned!r} found in reconciler/repair/records.py"
