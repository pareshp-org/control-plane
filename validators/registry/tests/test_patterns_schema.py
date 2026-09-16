"""Tests for schemas/registry/patterns.v1.schema.json and R-PAT-01 (L1-608 / L1-935).

L1-608 (master task table, row 48) is implemented here under the flat
FD-096 layout. L1-935 (L1-02-12, absorbed per FD-095) specifies a
materially different, richer field shape for the same patterns.yaml file
(pattern_class/occurrence_evidence/confirmed_root_class/confirmed_by
instead of root_class/occurrences/remediation_type) -- the two cannot
both be authored onto one schema file. L1-608's simpler, AT-040-anchored
shape (with its own complete 12-case acceptance table) is implemented as
the real deliverable; L1-935's alternate design is documented here, not
built as a second competing schema.

3 valid + 9 invalid = 12 test functions, matching the task's own case
table. Validated directly with `jsonschema` -- FD-094 supersedes the
L1-005 fixture-case harness in favour of Option B.
"""
import copy
import json
import os

import jsonschema
import yaml

from validators.registry.rules import r_pat_01

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry", "patterns.v1.schema.json"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "patterns")


def _schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "patterns.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors(doc):
    return list(jsonschema.Draft7Validator(_schema()).iter_errors(doc))


def _confirmed_three():
    return _load(os.path.join("valid", "confirmed_three"))


# ---------------------------------------------------------------------------
# valid (3)
# ---------------------------------------------------------------------------

def test_valid_confirmed_three():
    doc = _confirmed_three()
    assert len(doc["patterns"][0]["occurrences"]) == 3
    assert _errors(doc) == []


def test_valid_four_occurrences():
    doc = _load(os.path.join("valid", "four_occurrences"))
    assert len(doc["patterns"][0]["occurrences"]) == 4
    assert _errors(doc) == []


def test_valid_empty():
    assert _errors(_load(os.path.join("valid", "empty"))) == []


# ---------------------------------------------------------------------------
# invalid (9)
# ---------------------------------------------------------------------------

def test_two_occurrences_triggers_r_pat_01():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["occurrences"] = doc["patterns"][0]["occurrences"][:2]
    # schema alone permits 2 (minItems 1) -- this is the rule's job
    assert _errors(doc) == []
    passed, findings = r_pat_01.check_document(doc)
    assert not passed
    assert "records 2 occurrences" in findings[0]
    assert "Section 58.3 confirms a pattern on the third occurrence" in findings[0]


def test_one_occurrence_triggers_r_pat_01():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["occurrences"] = doc["patterns"][0]["occurrences"][:1]
    assert _errors(doc) == []
    passed, findings = r_pat_01.check_document(doc)
    assert not passed
    assert "records 1 occurrences" in findings[0]


def test_be_more_careful_remediation_rejected():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["remediation_type"] = "be_more_careful"
    assert len(_errors(doc)) == 1


def test_remediation_unknown_token_rejected():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["remediation_type"] = "training"
    assert len(_errors(doc)) == 1


def test_bad_pattern_id():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["id"] = "PAT-1"
    assert len(_errors(doc)) == 1


def test_missing_closure_condition():
    doc = copy.deepcopy(_confirmed_three())
    del doc["patterns"][0]["closure_condition"]
    assert len(_errors(doc)) == 1


def test_missing_work_item():
    doc = copy.deepcopy(_confirmed_three())
    del doc["patterns"][0]["work_item"]
    assert len(_errors(doc)) == 1


def test_occurrence_date_not_date():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["occurrences"][0]["date"] = "March"
    assert len(_errors(doc)) == 1


def test_extra_pattern_field_rejected():
    doc = copy.deepcopy(_confirmed_three())
    doc["patterns"][0]["severity"] = "sev1"
    assert len(_errors(doc)) == 1
