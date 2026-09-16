"""Tests for schemas/registry/common/assignments.v1.schema.json -- the
17-type assignment sub-schema shared by product.yaml (Section 10) and the
future service.yaml (Section 20.1), plus the D108 founder_decision_delegate
scope restriction (L1-302).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 fixture-case harness -- FD-094 (DECIDED) supersedes that harness in
favour of Option B, the same adaptation test_people_schema.py and
test_platform_schema.py already document. Each fixture is a single
assignment object (this schema's own top level), not an array, stored as
`assignment.yaml` in its case directory -- there is no prior filename
convention for a sub-schema item fixture to inherit.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry", "common"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "assignments")

def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "defs.v1.schema.json")
    assignments_path = os.path.join(SCHEMAS_DIR, "assignments.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(assignments_path, encoding="utf-8") as f:
        assignments_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (assignments_schema["$id"], Resource.from_contents(assignments_schema)),
        ]
    )
    return assignments_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "assignment.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (17, one per assignment type, Section 10.1) -----------

def test_valid_primary_owner():
    assert _errors_for(os.path.join("valid", "primary_owner")) == []


def test_valid_cross_reviewer():
    assert _errors_for(os.path.join("valid", "cross_reviewer")) == []


def test_valid_backup_owner():
    assert _errors_for(os.path.join("valid", "backup_owner")) == []


def test_valid_temporary_contributor():
    assert _errors_for(os.path.join("valid", "temporary_contributor")) == []


def test_valid_incident_responder():
    assert _errors_for(os.path.join("valid", "incident_responder")) == []


def test_valid_verification_responsibility():
    assert _errors_for(os.path.join("valid", "verification_responsibility")) == []


def test_valid_architecture_responsibility():
    assert _errors_for(os.path.join("valid", "architecture_responsibility")) == []


def test_valid_production_approval_delegate():
    assert _errors_for(os.path.join("valid", "production_approval_delegate")) == []


def test_valid_security_reviewer():
    assert _errors_for(os.path.join("valid", "security_reviewer")) == []


def test_valid_plan_approval_delegate():
    assert _errors_for(os.path.join("valid", "plan_approval_delegate")) == []


def test_valid_incident_coordination_delegate():
    assert _errors_for(os.path.join("valid", "incident_coordination_delegate")) == []


def test_valid_domain_lead():
    assert _errors_for(os.path.join("valid", "domain_lead")) == []


def test_valid_founder_decision_delegate():
    assert _errors_for(os.path.join("valid", "founder_decision_delegate")) == []


def test_valid_registry_owner_delegate():
    assert _errors_for(os.path.join("valid", "registry_owner_delegate")) == []


def test_valid_verification_delegate():
    assert _errors_for(os.path.join("valid", "verification_delegate")) == []


def test_valid_cross_review_shadow():
    assert _errors_for(os.path.join("valid", "cross_review_shadow")) == []


def test_valid_mentor():
    assert _errors_for(os.path.join("valid", "mentor")) == []


# ---- invalid cases (7) ---------------------------------------------------

def test_mentor_null_end_date():
    assert len(_errors_for("mentor_null_end_date")) > 0


def test_plan_delegate_null_end_date():
    assert len(_errors_for("plan_delegate_null_end_date")) > 0


def test_temporary_contributor_null_end_date():
    assert len(_errors_for("temporary_contributor_null_end_date")) > 0


def test_unknown_type():
    assert len(_errors_for("unknown_type")) > 0


def test_assignment_extra_field():
    assert len(_errors_for("assignment_extra_field")) > 0


def test_founder_delegate_names_promotion():
    assert len(_errors_for("founder_delegate_names_promotion")) > 0


def test_founder_delegate_names_compensation():
    assert len(_errors_for("founder_delegate_names_compensation")) > 0
