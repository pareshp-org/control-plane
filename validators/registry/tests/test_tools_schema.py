"""Tests for schemas/registry/tools.v1.schema.json and R-TOL-01 (L1-606 / L1-938).

L1-606 (master task table, row 46) and L1-938 (L1-02-15, absorbed from the
phase file per FD-095) target the identical deliverable. Implemented once
under the flat FD-096 layout; L1-938's nested schemas/registry/tools/v1/...
path is superseded.

3 valid + 10 invalid = 13 test functions, matching the task's own case table.
Validated directly with `jsonschema` -- FD-094 supersedes the L1-005
fixture-case harness in favour of Option B (validators/registry/cli.py).
"""
import copy
import json
import os

import jsonschema
import yaml

from validators.registry.rules import r_tol_01

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry", "tools.v1.schema.json"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "tools")


def _schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "tools.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors(doc):
    return list(jsonschema.Draft7Validator(_schema()).iter_errors(doc))


def _gsd_doc():
    return _load(os.path.join("valid", "gsd_entry"))


# ---------------------------------------------------------------------------
# valid (3)
# ---------------------------------------------------------------------------

def test_valid_gsd_entry():
    assert _errors(_gsd_doc()) == []


def test_valid_three_entries():
    doc = _load(os.path.join("valid", "three_entries"))
    assert len(doc["tools"]) == 3
    assert _errors(doc) == []


def test_valid_empty():
    assert _errors(_load(os.path.join("valid", "empty"))) == []


# ---------------------------------------------------------------------------
# invalid (10)
# ---------------------------------------------------------------------------

def test_criticality_absent():
    doc = copy.deepcopy(_gsd_doc())
    del doc["tools"][0]["criticality"]
    assert len(_errors(doc)) > 0
    passed, findings = r_tol_01.check_document(doc)
    assert not passed and findings


def test_criticality_unknown_token():
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["criticality"] = "essential"
    assert len(_errors(doc)) > 0
    passed, findings = r_tol_01.check_document(doc)
    assert not passed


def test_criticality_product_vocabulary():
    """The tool register never reuses the Section 6.1 product vocabulary
    (`critical`) -- Section 62.1: "no rule reads one for the other.\""""
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["criticality"] = "critical"
    assert len(_errors(doc)) > 0
    passed, findings = r_tol_01.check_document(doc, source="criticality_product_vocabulary")
    assert not passed
    assert "declares criticality 'critical', which is outside the Section 62.1 enumeration" in findings[0]


def test_missing_owner():
    doc = copy.deepcopy(_gsd_doc())
    del doc["tools"][0]["owner"]
    assert len(_errors(doc)) == 1


def test_missing_exit_condition():
    doc = copy.deepcopy(_gsd_doc())
    del doc["tools"][0]["exit_condition"]
    assert len(_errors(doc)) == 1


def test_missing_current_version():
    doc = copy.deepcopy(_gsd_doc())
    del doc["tools"][0]["current_version"]
    assert len(_errors(doc)) == 1


def test_last_reviewed_not_date():
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["last_reviewed"] = "July 2026"
    assert len(_errors(doc)) == 1


def test_bad_tool_id():
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["id"] = "GSD Core"
    assert len(_errors(doc)) == 1


def test_extra_tool_field():
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["licence"] = "mit"
    assert len(_errors(doc)) == 1


def test_replacement_candidates_not_array():
    doc = copy.deepcopy(_gsd_doc())
    doc["tools"][0]["replacement_candidates"] = "none"
    assert len(_errors(doc)) == 1
