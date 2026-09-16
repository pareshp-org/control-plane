"""Tests for schemas/registry/owners.v1.schema.json and the live
registries/OWNERS.yaml manifest (L1-505).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 discover()/RULE_ID/expect.yaml harness or the CLI "OK: N file(s)
validated" grammar in lanes/L1-05-tasks.md -- FD-094 (DECIDED)
supersedes that harness and grammar in favour of Option B
(validators/registry/cli.py, R01-R18), which this schema/manifest-only
task does not touch. Same adaptation already used by L1-102/L1-104/
L1-106.

The live registries/OWNERS.yaml ships thirty artifact entries against
`declared_count: 29` -- the honest transcription of Section 52.6's
"twenty-nine entries" sentence against a table body that actually names
thirty artifacts on twenty-nine lines. This is a deliberate,
correct-and-expected discrepancy (see the L1-505 unconditional STOP),
not a schema error: `declared_count` and `len(artifacts)` are
independent integers at the schema level, and nothing here makes them
agree.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas", "registry")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "owners")
REGISTRIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "registries")


def _registry():
    owners_path = os.path.join(SCHEMAS_DIR, "owners.v1.schema.json")
    with open(owners_path, encoding="utf-8") as f:
        owners_schema = json.load(f)
    reg = Registry().with_resources(
        [(owners_schema["$id"], Resource.from_contents(owners_schema))]
    )
    return owners_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "owners.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (2) ----------------------------------------------------


def test_valid_live_manifest():
    assert _errors_for(os.path.join("valid", "live_manifest")) == []


def test_valid_minimal():
    assert _errors_for(os.path.join("valid", "minimal")) == []


# ---- invalid cases (6) ---------------------------------------------------


def test_bad_owner_token():
    assert len(_errors_for("bad_owner_token")) > 0


def test_bad_repository_token():
    assert len(_errors_for("bad_repository_token")) > 0


def test_missing_purpose():
    assert len(_errors_for("missing_purpose")) > 0


def test_path_empty():
    assert len(_errors_for("path_empty")) > 0


def test_extra_artifact_field():
    assert len(_errors_for("extra_artifact_field")) > 0


def test_artifacts_empty():
    assert len(_errors_for("artifacts_empty")) > 0


# ---- live-manifest assertions (mirror the task's own ACCEPTANCE #3-#5) --


def _load_owners_yaml():
    with open(os.path.join(REGISTRIES_DIR, "OWNERS.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_live_manifest_artifacts_count_is_thirty():
    doc = _load_owners_yaml()
    assert len(doc["artifacts"]) == 30


def test_live_manifest_declared_count_is_twenty_nine():
    doc = _load_owners_yaml()
    assert doc["declared_count"] == 29


def test_live_manifest_per_entry_owner_count_is_two():
    doc = _load_owners_yaml()
    assert sum(1 for a in doc["artifacts"] if a["per_entry_owner"]) == 2


def test_live_manifest_off_repository_count_is_two():
    doc = _load_owners_yaml()
    assert sum(1 for a in doc["artifacts"] if a["repository"] == "off-repository") == 2


def test_live_manifest_validates_against_schema():
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    assert list(validator.iter_errors(_load_owners_yaml())) == []
