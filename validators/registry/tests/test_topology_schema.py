"""Tests for schemas/registry/topology.v1.schema.json (L1-501).

Section 66.2's escalation rule is prose that a *rule* implements (L1-503),
not this schema, so there is no `escalation_resolution` block; Section
66.4's founder scope split names no fields and no carrier file ("No
structure is built early"), so there is no `founder_scope_split` block
either. `succession.team_lead.acting` is nullable: Section 13.1
pre-designates the Acting Team Lead, but the designation itself is a
Founder decision (Section 52.6 owner row), not a schema default.

Each fixture directory under validators/registry/fixtures/topology/
also carries an `expect.yaml` (today / expect_exit / expect_errors),
transcribed per the task's own COMMANDS block. Validated here directly
with `jsonschema` against the fixtures' `topology.yaml` documents,
resolving the common/defs.v1.schema.json $refs via a Registry -- the
same Option B adaptation (FD-094, DECIDED, supersedes the L1-005
fixture-case harness) already used by test_platform_schema.py (L1-106),
test_framework_schema.py (L1-801) and test_os_health_schema.py (L1-605).

14 test functions: 4 valid + 10 invalid, matching the task's own case
table exactly (Case column, "Verdict" 0 errors / 1 error).
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
SCHEMA_PATH = os.path.join(SCHEMAS_DIR, "topology.v1.schema.json")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "topology")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        topology_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (topology_schema["$id"], Resource.from_contents(topology_schema)),
        ]
    )
    return topology_schema, reg


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "topology.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors(doc):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    return list(validator.iter_errors(doc))


# ---------------------------------------------------------------------------
# valid (4)
# ---------------------------------------------------------------------------

def test_valid_dormant_minimal():
    doc = _load(os.path.join("valid", "dormant_minimal"))
    assert doc["domains_active"] is False
    assert doc["succession"]["team_lead"]["acting"] is None
    assert _errors(doc) == []


def test_valid_dormant_with_acting():
    doc = _load(os.path.join("valid", "dormant_with_acting"))
    assert doc["succession"]["team_lead"]["acting"] == "dev-a"
    assert _errors(doc) == []


def test_valid_domains_declared_dormant():
    doc = _load(os.path.join("valid", "domains_declared_dormant"))
    assert len(doc["domains"]) == 2
    assert all(d["lead"] is None for d in doc["domains"])
    assert _errors(doc) == []


def test_valid_triggers_declared():
    doc = _load(os.path.join("valid", "triggers_declared"))
    assert len(doc["activation_triggers"]) == 3
    assert _errors(doc) == []


# ---------------------------------------------------------------------------
# invalid (10)
# ---------------------------------------------------------------------------

def test_missing_registry_version():
    doc = _load("missing_registry_version")
    assert "registry_version" not in doc
    assert len(_errors(doc)) == 1


def test_domains_active_not_bool():
    doc = _load("domains_active_not_bool")
    assert doc["domains_active"] == "false"
    assert len(_errors(doc)) == 1


def test_missing_succession():
    doc = _load("missing_succession")
    assert "succession" not in doc
    assert len(_errors(doc)) == 1


def test_acting_bad_id():
    doc = _load("acting_bad_id")
    assert doc["succession"]["team_lead"]["acting"] == "Dev A"
    assert len(_errors(doc)) == 1


def test_domain_bad_id():
    doc = _load("domain_bad_id")
    assert doc["domains"][0]["id"] == "Commerce Domain"
    assert len(_errors(doc)) == 1


def test_domain_products_not_unique():
    doc = _load("domain_products_not_unique")
    assert doc["domains"][0]["products"] == ["product-1", "product-1"]
    assert len(_errors(doc)) == 1


def test_domain_lead_bad_id():
    doc = _load("domain_lead_bad_id")
    assert doc["domains"][0]["lead"] == "Nimesh"
    assert len(_errors(doc)) == 1


def test_extra_top_field():
    doc = _load("extra_top_field")
    assert doc["owner"] == "founder"
    assert len(_errors(doc)) == 1


def test_extra_domain_field():
    doc = _load("extra_domain_field")
    assert doc["domains"][0]["budget"] == 0
    assert len(_errors(doc)) == 1


def test_triggers_not_array():
    doc = _load("triggers_not_array")
    assert doc["activation_triggers"] == "product count > 15"
    assert len(_errors(doc)) == 1
