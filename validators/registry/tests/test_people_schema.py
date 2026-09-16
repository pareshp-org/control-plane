"""Tests for schemas/registry/people.registry.v1.schema.json (L1-104).

Adapted to validate fixtures directly with `jsonschema` rather than
the L1-005 fixture-case harness (RULE_ID/APPLIES_TO/discover()/
expect.yaml) -- FD-094 (DECIDED) supersedes that harness in favour of
Option B (validators/registry/cli.py). Fixtures still live at
validators/registry/fixtures/people/<case>/people.yaml as the task
specifies.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "people")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    people_path = os.path.join(SCHEMAS_DIR, "people.registry.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(people_path, encoding="utf-8") as f:
        people_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (people_schema["$id"], Resource.from_contents(people_schema)),
        ]
    )
    return people_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "people.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (4) -------------------------------------------------

def test_valid_employee_full():
    assert _errors_for(os.path.join("valid", "employee_full")) == []


def test_valid_specialist_scoped():
    assert _errors_for(os.path.join("valid", "specialist_scoped")) == []


def test_valid_departed():
    assert _errors_for(os.path.join("valid", "departed")) == []


def test_valid_no_work_arrangement():
    assert _errors_for(os.path.join("valid", "no_work_arrangement")) == []


# ---- invalid cases (18) -----------------------------------------------

def test_missing_version():
    assert len(_errors_for("missing_version")) > 0


def test_missing_id():
    assert len(_errors_for("missing_id")) > 0


def test_bad_github_login():
    assert len(_errors_for("bad_github_login")) > 0


def test_unknown_capability():
    assert len(_errors_for("unknown_capability")) > 0


def test_bad_employment_type():
    assert len(_errors_for("bad_employment_type")) > 0


def test_bad_availability():
    assert len(_errors_for("bad_availability")) > 0


def test_bad_access_status():
    assert len(_errors_for("bad_access_status")) > 0


def test_utc_offset_timezone():
    assert len(_errors_for("utc_offset_timezone")) > 0


def test_fte_zero():
    assert len(_errors_for("fte_zero")) > 0


def test_fte_above_one():
    assert len(_errors_for("fte_above_one")) > 0


def test_bad_hhmm():
    assert len(_errors_for("bad_hhmm")) > 0


def test_schedule_unknown_day():
    assert len(_errors_for("schedule_unknown_day")) > 0


def test_schedule_extra_field():
    assert len(_errors_for("schedule_extra_field")) > 0


def test_extra_top_field():
    assert len(_errors_for("extra_top_field")) > 0


def test_extra_person_field():
    assert len(_errors_for("extra_person_field")) > 0


def test_end_date_not_date():
    assert len(_errors_for("end_date_not_date")) > 0


def test_capabilities_not_array():
    assert len(_errors_for("capabilities_not_array")) > 0


def test_scope_extra_field():
    assert len(_errors_for("scope_extra_field")) > 0
