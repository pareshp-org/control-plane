"""Tests for schemas/registry/framework.v1.schema.json (L1-801).

registries/framework/ is directory-per-item (Section 77.1's retirement_date
means versions accumulate; PARTITION rule 3 forbids a single shared-index
file) -- it ships empty (.gitkeep only). Population of a live
registries/framework/<v>.yaml is the Founder's, under the Section 77.4
change authority, and is explicitly out of scope for this task.

5 valid + 15 invalid = 20 test functions, matching the task's own case
table. Validated directly with `jsonschema` -- FD-094 supersedes the
L1-005 fixture-case harness in favour of Option B.
"""
import copy
import json
import os

import jsonschema
import yaml

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry", "framework.v1.schema.json"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "framework", "valid")


def _schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "framework.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors(doc):
    return list(jsonschema.Draft7Validator(_schema()).iter_errors(doc))


def _three_kpis():
    return _load("v1_three_kpis")


# ---------------------------------------------------------------------------
# valid (5)
# ---------------------------------------------------------------------------

def test_valid_v1_three_kpis():
    assert _errors(_three_kpis()) == []


def test_valid_v1_ten_kpis():
    doc = _load("v1_ten_kpis")
    assert len(doc["kpis"]) == 10
    assert doc["multi_framework_transition"] is True
    assert _errors(doc) == []


def test_valid_custom_no_kras():
    doc = _load("custom_no_kras")
    assert doc["kras"] == []
    assert all(kpi["kra_id"] is None for kpi in doc["kpis"])
    assert _errors(doc) == []


def test_valid_review_cadence_not_defined():
    doc = _load("review_cadence_not_defined")
    assert doc["review_cadence"] == "Not defined"
    assert _errors(doc) == []


def test_valid_retired_with_date():
    doc = _load("retired_with_date")
    assert doc["status"] == "retired"
    assert doc["retirement_date"] == "2026-06-30"
    assert _errors(doc) == []


# ---------------------------------------------------------------------------
# invalid (15)
# ---------------------------------------------------------------------------

def test_bad_framework_version():
    doc = copy.deepcopy(_three_kpis())
    doc["framework_version"] = "1.0"
    assert len(_errors(doc)) == 1


def test_bad_status():
    doc = copy.deepcopy(_three_kpis())
    doc["status"] = "superseded"
    assert len(_errors(doc)) == 1


def test_missing_effective_date():
    doc = copy.deepcopy(_three_kpis())
    del doc["effective_date"]
    assert len(_errors(doc)) == 1


def test_affected_roles_empty():
    doc = copy.deepcopy(_three_kpis())
    doc["affected_roles"] = []
    assert len(_errors(doc)) == 1


def test_affected_roles_bad_id():
    doc = copy.deepcopy(_three_kpis())
    doc["affected_roles"] = ["Senior Developer"]
    assert len(_errors(doc)) == 1


def test_kra_weight_above_100():
    doc = copy.deepcopy(_three_kpis())
    doc["kras"][0]["weight"] = 140
    assert len(_errors(doc)) == 1


def test_kpi_weight_negative():
    doc = copy.deepcopy(_three_kpis())
    doc["kpis"][0]["weight"] = -5
    assert len(_errors(doc)) == 1


def test_kpi_missing_target():
    doc = copy.deepcopy(_three_kpis())
    del doc["kpis"][0]["target"]
    assert len(_errors(doc)) == 1


def test_kpi_missing_time_window():
    doc = copy.deepcopy(_three_kpis())
    del doc["kpis"][0]["time_window"]
    assert len(_errors(doc)) == 1


def test_kpi_missing_known_limitations():
    doc = copy.deepcopy(_three_kpis())
    del doc["kpis"][0]["known_limitations"]
    assert len(_errors(doc)) == 1


def test_kpi_known_limitations_empty():
    doc = copy.deepcopy(_three_kpis())
    doc["kpis"][0]["known_limitations"] = ""
    assert len(_errors(doc)) == 1


def test_rating_scale_verbatim_false():
    doc = copy.deepcopy(_three_kpis())
    doc["rating_scale"]["verbatim"] = False
    assert len(_errors(doc)) == 1


def test_rating_scale_no_bands():
    doc = copy.deepcopy(_three_kpis())
    doc["rating_scale"]["bands"] = []
    assert len(_errors(doc)) == 1


def test_review_cadence_empty():
    doc = copy.deepcopy(_three_kpis())
    doc["review_cadence"] = ""
    assert len(_errors(doc)) == 1


def test_extra_top_field():
    doc = copy.deepcopy(_three_kpis())
    doc["owner"] = "founder"
    assert len(_errors(doc)) == 1
