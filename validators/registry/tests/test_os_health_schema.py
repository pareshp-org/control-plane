"""Tests for schemas/registry/os-health.v1.schema.json (L1-605 / L1-932).

L1-605 (master task table, row 45) and L1-932 (L1-02-09, absorbed from the
L1-02-schemas.md phase file per FD-095) both target the identical
deliverable -- the os-health.yaml schema with the eight Section 84.6
attributes plus activation_dependency and lookback_window (D77). FD-096
fixes the flat schemas/registry/<name>.v1.schema.json layout, which is what
is authored here; L1-932's nested schemas/registry/os-health/v1/... layout
predates that decision and is not used.

Validated directly with `jsonschema` (self-contained schema, no external
$ref) rather than the L1-005 fixture-case harness -- FD-094 (DECIDED)
supersedes that harness in favour of Option B (validators/registry/cli.py),
the same adaptation test_platform_schema.py documents for L1-106.
"""
import copy
import json
import os

import jsonschema
import yaml

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry", "os-health.v1.schema.json"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "os-health")


def _schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _valid_doc():
    path = os.path.join(FIXTURES_DIR, "valid", "three_signals", "os-health.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors(doc):
    return list(jsonschema.Draft7Validator(_schema()).iter_errors(doc))


def _load_negative(case):
    path = os.path.join(FIXTURES_DIR, case, "os-health.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# valid fixture
# ---------------------------------------------------------------------------

def test_valid_three_signals():
    assert _errors(_valid_doc()) == []


# ---------------------------------------------------------------------------
# the three shipped negative fixtures
# ---------------------------------------------------------------------------

def test_negative_signal_class_not_in_scale():
    doc = _load_negative("invalid-signal-class-not-in-scale")
    assert doc["signals"][0]["states"][0]["class"] == "Orange"
    assert len(_errors(doc)) > 0


def test_negative_signal_missing_known_limitations():
    doc = _load_negative("invalid-signal-missing-known-limitations")
    assert doc["signals"][0]["known_limitations"] == ""
    assert len(_errors(doc)) > 0


def test_negative_signal_missing_activation_dependency():
    doc = _load_negative("invalid-signal-missing-activation-dependency")
    assert "activation_dependency" not in doc["signals"][0]
    assert len(_errors(doc)) > 0


# ---------------------------------------------------------------------------
# top-level and drift_class_tolerances
# ---------------------------------------------------------------------------

def test_missing_registry_version():
    doc = copy.deepcopy(_valid_doc())
    del doc["registry_version"]
    assert len(_errors(doc)) > 0


def test_registry_version_not_integer():
    doc = copy.deepcopy(_valid_doc())
    doc["registry_version"] = "1"
    assert len(_errors(doc)) > 0


def test_registry_version_below_minimum():
    doc = copy.deepcopy(_valid_doc())
    doc["registry_version"] = 0
    assert len(_errors(doc)) > 0


def test_missing_drift_class_tolerances():
    doc = copy.deepcopy(_valid_doc())
    del doc["drift_class_tolerances"]
    assert len(_errors(doc)) > 0


def test_drift_tolerances_wrong_green_const():
    doc = copy.deepcopy(_valid_doc())
    doc["drift_class_tolerances"]["green"] = "capped"
    assert len(_errors(doc)) > 0


def test_drift_tolerances_wrong_blocking_const():
    doc = copy.deepcopy(_valid_doc())
    doc["drift_class_tolerances"]["blocking"] = "budgeted"
    assert len(_errors(doc)) > 0


def test_drift_tolerances_negative_amber():
    doc = copy.deepcopy(_valid_doc())
    doc["drift_class_tolerances"]["amber_per_product"] = -1
    assert len(_errors(doc)) > 0


def test_top_level_extra_field_rejected():
    doc = copy.deepcopy(_valid_doc())
    doc["notes"] = "not permitted"
    assert len(_errors(doc)) > 0


# ---------------------------------------------------------------------------
# signal-level attributes
# ---------------------------------------------------------------------------

def test_signal_id_bad_pattern():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["id"] = "SIGNAL-5"
    assert len(_errors(doc)) > 0


def test_signal_name_empty():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["name"] = ""
    assert len(_errors(doc)) > 0


def test_signal_priority_invalid_enum():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["priority"] = "P3"
    assert len(_errors(doc)) > 0


def test_signal_states_empty_array():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["states"] = []
    assert len(_errors(doc)) > 0


def test_signal_states_bad_state_token():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["states"][0]["state"] = "alert"
    assert len(_errors(doc)) > 0


def test_signal_missing_lookback_window():
    doc = copy.deepcopy(_valid_doc())
    del doc["signals"][0]["lookback_window"]
    assert len(_errors(doc)) > 0


def test_signal_missing_definition():
    doc = copy.deepcopy(_valid_doc())
    del doc["signals"][0]["definition"]
    assert len(_errors(doc)) > 0


def test_signal_baseline_wrong_type():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["baseline"] = {"nested": "object"}
    assert len(_errors(doc)) > 0


def test_signal_extra_field_rejected():
    doc = copy.deepcopy(_valid_doc())
    doc["signals"][0]["severity"] = "sev1"
    assert len(_errors(doc)) > 0
