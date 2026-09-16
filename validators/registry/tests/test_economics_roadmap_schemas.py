"""Tests for economics.v1.schema.json and platform-roadmap.v1.schema.json (L1-607).

L1-607 (master task table, row 47) is implemented here under the flat
FD-096 layout. L1-936 and L1-937 (L1-02-13/14, absorbed per FD-095)
specify materially richer, incompatible field shapes for the same two
files (load_model/factors/ritual_inventory for economics.yaml;
initiatives[]/horizon/status for platform-roadmap.yaml) -- the two
designs cannot both be authored onto the same schema files. L1-607's
simpler shape, with its own complete 19-case acceptance table, is
implemented as the real deliverable.

4 valid + 15 invalid = 19 test functions, matching the task's own case
table. Validated directly with `jsonschema` -- FD-094 supersedes the
L1-005 fixture-case harness in favour of Option B.
"""
import copy
import json
import os

import jsonschema
import yaml

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "econ")


def _schema(name):
    with open(os.path.join(SCHEMAS_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def _load(case, filename):
    path = os.path.join(FIXTURES_DIR, "valid", case, filename)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _eco_errors(doc):
    return list(jsonschema.Draft7Validator(_schema("economics.v1.schema.json")).iter_errors(doc))


def _rm_errors(doc):
    return list(jsonschema.Draft7Validator(_schema("platform-roadmap.v1.schema.json")).iter_errors(doc))


def _economics_minimal():
    return _load("economics_minimal", "economics.yaml")


def _economics_with_os_entry():
    return _load("economics_with_os_entry", "economics.yaml")


def _roadmap_minimal():
    return _load("roadmap_minimal", "platform-roadmap.yaml")


def _roadmap_with_gate():
    return _load("roadmap_with_gate", "platform-roadmap.yaml")


# ---------------------------------------------------------------------------
# valid (4)
# ---------------------------------------------------------------------------

def test_valid_economics_minimal():
    assert _eco_errors(_economics_minimal()) == []


def test_valid_economics_with_os_entry():
    doc = _economics_with_os_entry()
    assert len(doc["operating_system_entry"]["investment_gate_answers"]) == 7
    assert _eco_errors(doc) == []


def test_valid_roadmap_minimal():
    assert _rm_errors(_roadmap_minimal()) == []


def test_valid_roadmap_with_gate():
    doc = _roadmap_with_gate()
    assert len(doc["investment_gates"][0]["answers"]) == 7
    assert _rm_errors(doc) == []


# ---------------------------------------------------------------------------
# invalid -- economics (9)
# ---------------------------------------------------------------------------

def test_eco_missing_budget_band():
    doc = copy.deepcopy(_economics_minimal())
    del doc["control_plane_budget_band"]
    assert len(_eco_errors(doc)) == 1


def test_eco_band_bad_currency():
    doc = copy.deepcopy(_economics_minimal())
    doc["control_plane_budget_band"]["currency"] = "Rupees"
    assert len(_eco_errors(doc)) == 1


def test_eco_band_negative():
    doc = copy.deepcopy(_economics_minimal())
    doc["control_plane_budget_band"]["ceiling"] = -1
    assert len(_eco_errors(doc)) == 1


def test_eco_ledger_bad_verdict():
    doc = copy.deepcopy(_economics_with_os_entry())
    doc["automation_ledger"][0]["verdict"] = "pending"
    assert len(_eco_errors(doc)) == 1


def test_eco_ledger_negative_cost():
    doc = copy.deepcopy(_economics_with_os_entry())
    doc["automation_ledger"][0]["build_cost_hours"] = -4
    assert len(_eco_errors(doc)) == 1


def test_eco_scored_without_adoption_store():
    """57.1's honesty rule: an entry whose adoption field cannot name a
    store must be recorded unbaselined, not scored keep/improve/etc."""
    doc = copy.deepcopy(_economics_with_os_entry())
    doc["automation_ledger"][0]["adoption"]["source_store"] = None
    doc["automation_ledger"][0]["verdict"] = "keep"
    assert len(_eco_errors(doc)) == 1


def test_eco_os_entry_six_answers():
    doc = copy.deepcopy(_economics_with_os_entry())
    doc["operating_system_entry"]["investment_gate_answers"].pop()
    assert len(_eco_errors(doc)) == 1


def test_eco_os_entry_question_out_of_range():
    doc = copy.deepcopy(_economics_with_os_entry())
    doc["operating_system_entry"]["investment_gate_answers"][0]["question"] = 8
    assert len(_eco_errors(doc)) == 1


def test_eco_extra_top_field():
    doc = copy.deepcopy(_economics_minimal())
    doc["notes"] = "x"
    assert len(_eco_errors(doc)) == 1


# ---------------------------------------------------------------------------
# invalid -- platform-roadmap (6)
# ---------------------------------------------------------------------------

def test_rm_missing_change_budget():
    doc = copy.deepcopy(_roadmap_minimal())
    del doc["change_budget"]
    assert len(_rm_errors(doc)) == 1


def test_rm_bad_period():
    doc = copy.deepcopy(_roadmap_minimal())
    doc["change_budget"]["period"] = "week"
    assert len(_rm_errors(doc)) == 1


def test_rm_negative_max():
    doc = copy.deepcopy(_roadmap_minimal())
    doc["change_budget"]["max_fleet_migrations"] = -1
    assert len(_rm_errors(doc)) == 1


def test_rm_gate_six_answers():
    doc = copy.deepcopy(_roadmap_with_gate())
    doc["investment_gates"][0]["answers"].pop()
    assert len(_rm_errors(doc)) == 1


def test_rm_roadmaps_missing_platform():
    doc = copy.deepcopy(_roadmap_minimal())
    del doc["roadmaps"]["platform"]
    assert len(_rm_errors(doc)) == 1


def test_rm_extra_top_field():
    doc = copy.deepcopy(_roadmap_minimal())
    doc["notes"] = "x"
    assert len(_rm_errors(doc)) == 1
