"""Tests for schemas/registry/platform.registry.v1.schema.json (L1-106).

Adapted to validate fixtures directly with `jsonschema` rather than
the L1-005 fixture-case harness -- FD-094 (DECIDED) supersedes that
harness in favour of Option B (validators/registry/cli.py).

Filename note: the task's own FILES list names
`schemas/registry/platform.v1.schema.json` -- the SAME filename as the
pre-existing minimal schema that
tests/integration/test_registries_schema_independent.py already maps
every registries/platform/*.yaml directory record onto (a single
platform-component schema: id/name/type). Overwriting that file with
this envelope shape would break that existing, already-passing
validation. Following the same non-colliding-filename convention
already used for L1-102 (roles.registry.v1.schema.json) and L1-104
(people.registry.v1.schema.json), this schema is authored as
schemas/registry/platform.registry.v1.schema.json instead.

Second discovered discrepancy: the task's SELF-VERIFY says REQ=6, but
its own "Schema shape" block lists only 5 top-level required keys
(platform_version, supported_contract_versions,
reusable_workflow_versions, canary_set, event_type). Implemented
faithfully to the 5 keys the shape table actually shows -- not
inventing a 6th field to force the count -- so REQ=5 here, not 6.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "platform")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    platform_path = os.path.join(SCHEMAS_DIR, "platform.registry.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(platform_path, encoding="utf-8") as f:
        platform_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (platform_schema["$id"], Resource.from_contents(platform_schema)),
        ]
    )
    return platform_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "platform.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


def test_valid_seeded():
    assert _errors_for(os.path.join("valid", "seeded")) == []


def test_valid_empty_cross_lane():
    assert _errors_for(os.path.join("valid", "empty_cross_lane")) == []


def test_bad_platform_version():
    assert len(_errors_for("bad_platform_version")) > 0


def test_missing_supported_contract_versions():
    assert len(_errors_for("missing_supported_contract_versions")) > 0


def test_product_versions_empty():
    assert len(_errors_for("product_versions_empty")) > 0


def test_product_versions_not_int():
    assert len(_errors_for("product_versions_not_int")) > 0


def test_deadline_not_date():
    assert len(_errors_for("deadline_not_date")) > 0


def test_canary_bad_id():
    assert len(_errors_for("canary_bad_id")) > 0


def test_event_type_not_unique():
    assert len(_errors_for("event_type_not_unique")) > 0


def test_extra_top_field():
    assert len(_errors_for("extra_top_field")) > 0


def test_current_not_string_or_null():
    assert len(_errors_for("current_not_string_or_null")) > 0


def test_supported_not_array():
    assert len(_errors_for("supported_not_array")) > 0
