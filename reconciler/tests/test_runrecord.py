"""L3-P0-07: run record writer and summary line."""

import pytest
import yaml

from reconciler.runrecord import REQUIRED_KEYS, RefusedWritePath, RunRecord


def _clean_record():
    return RunRecord(
        run_id="R1",
        started_at="2026-08-27T00:00:00Z",
        finished_at="2026-08-27T00:01:00Z",
        status="OK",
        findings=[],
        comparison_counts={"demo": 3},
        canary_found=True,
        external_cause=None,
    )


def test_summary_format_byte_exact():
    r = _clean_record()
    assert r.summary_lines() == ["OK demo findings=0 compared=3", "CANARY found"]


def test_zero_finding_record_still_serialises_with_status(tmp_path):
    r = _clean_record()
    out = r.write(tmp_path / "run-record.yaml")
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["status"] == "OK"
    assert loaded["findings"] == []


def test_write_refuses_records_prefix():
    r = _clean_record()
    with pytest.raises(RefusedWritePath):
        r.write("records/x.yaml")


def test_write_refuses_events_prefix():
    r = _clean_record()
    with pytest.raises(RefusedWritePath):
        r.write("events/x.yaml")


def test_to_dict_keys_match_required_list():
    r = _clean_record()
    assert set(r.to_dict().keys()) == set(REQUIRED_KEYS)
