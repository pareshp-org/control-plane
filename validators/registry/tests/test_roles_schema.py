"""Tests for schemas/registry/roles.registry.v1.schema.json (L1-102).

Adapted to validate fixtures directly with `jsonschema` rather than
the L1-005 fixture-case harness (RULE_ID/APPLIES_TO/discover()/
expect.yaml) -- FD-094 (DECIDED) supersedes that harness in favour of
Option B (validators/registry/cli.py). Fixtures still live at
validators/registry/fixtures/roles/<case>/roles.yaml as the task
specifies; each of the ten test functions below encodes the expected
pass/fail directly instead of reading it back out of an expect.yaml.
"""
import json
import os

import jsonschema
import pytest
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "roles")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    roles_path = os.path.join(SCHEMAS_DIR, "roles.registry.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(roles_path, encoding="utf-8") as f:
        roles_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (roles_schema["$id"], Resource.from_contents(roles_schema)),
        ]
    )
    return roles_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "roles.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


def test_valid_minimal():
    assert _errors_for(os.path.join("valid", "minimal")) == []


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DISCOVERED SPEC CONTRADICTION (not in the original audit): L1-101's "
        "stableId pattern '^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$' forbids "
        "underscores, but 5 of Section 8's own 11 role ids are snake_case "
        "(team_lead, acting_team_lead, mobile_developer, senior_developer, "
        "foundational_developer). L1-102 says role id : $ref stableId, so "
        "the mandated 'valid/full' fixture (all eleven spec roles) cannot "
        "pass schema validation as both tasks are literally specified. "
        "Not resolved here -- resolving it is an L1-101/L1-103 spec-fidelity "
        "call, not a roles-schema-authoring call."
    ),
)
def test_valid_full():
    doc = _load_fixture(os.path.join("valid", "full"))
    assert len(doc["roles"]) == 11
    assert _errors_for(os.path.join("valid", "full")) == []


def test_missing_version():
    assert len(_errors_for("missing_version")) > 0


def test_unknown_capability():
    assert len(_errors_for("unknown_capability")) > 0


def test_extra_field():
    assert len(_errors_for("extra_field")) > 0


def test_names_a_person():
    # Section 76.3: a Role Profile never names a person. Caught the same
    # way as any other extra field -- additionalProperties: false.
    assert len(_errors_for("names_a_person")) > 0


def test_empty_roles():
    assert len(_errors_for("empty_roles")) > 0


def test_bad_id_format():
    assert len(_errors_for("bad_id_format")) > 0


def test_duplicate_id():
    # JSON Schema has no cross-item uniqueness constraint for roles[].id.
    # Per L1-102's own text, id-uniqueness is a rule concern (R-CAP-02's
    # sibling checks at L1-202, itself superseded -- see L1-202 SKIPPED),
    # not a schema concern -- so this fixture is schema-VALID even though
    # it is semantically a duplicate-id registry.
    assert _errors_for("duplicate_id") == []


def test_capability_not_array():
    assert len(_errors_for("capability_not_array")) > 0
