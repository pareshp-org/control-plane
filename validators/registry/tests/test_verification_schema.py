"""Tests for schemas/product/verification.contract.v1.schema.json (L1-401).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 fixture-case harness (RULE_ID/APPLIES_TO/discover()/expect.yaml)
-- FD-094 (DECIDED) supersedes that harness in favour of Option B
(validators/registry/cli.py), and the CLI's "OK: N file(s) validated" /
"ERROR <rule> <path>:<pointer> <message>" grammar described in
lanes/L1-05-tasks.md L1-401 was never built against Option B. Fixtures
still live at validators/registry/fixtures/verification/<case>/
verification-contract.yaml exactly as the task specifies, and this file
runs the same 13 cases (3 valid + 10 invalid) the task's own fixture
table lists.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "verification")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "registry", "common", "defs.v1.schema.json")
    contract_path = os.path.join(SCHEMAS_DIR, "product", "verification.contract.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(contract_path, encoding="utf-8") as f:
        contract_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (contract_schema["$id"], Resource.from_contents(contract_schema)),
        ]
    )
    return contract_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "verification-contract.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (3) --------------------------------------------------


def test_valid_service_full():
    assert _errors_for(os.path.join("valid", "service_full")) == []


def test_valid_no_performance():
    assert _errors_for(os.path.join("valid", "no_performance")) == []


def test_valid_with_evaluation_suite():
    assert _errors_for(os.path.join("valid", "with_evaluation_suite")) == []


# ---- invalid cases (10) ------------------------------------------------


def test_missing_seeded_case():
    assert len(_errors_for("missing_seeded_case")) > 0


def test_seeded_case_must_fail_false():
    assert len(_errors_for("seeded_case_must_fail_false")) > 0


def test_seeded_case_bad_id():
    assert len(_errors_for("seeded_case_bad_id")) > 0


def test_bad_contract_version():
    assert len(_errors_for("bad_contract_version")) > 0


def test_coverage_mechanism_unknown():
    assert len(_errors_for("coverage_mechanism_unknown")) > 0


def test_coverage_evidence_missing():
    assert len(_errors_for("coverage_evidence_missing")) > 0


def test_auto_pass_permitted_no_scope():
    assert len(_errors_for("auto_pass_permitted_no_scope")) > 0


def test_performance_profile_empty_criteria():
    assert len(_errors_for("performance_profile_empty_criteria")) > 0


def test_extra_top_field():
    assert len(_errors_for("extra_top_field")) > 0


def test_mechanisms_missing_performance():
    assert len(_errors_for("mechanisms_missing_performance")) > 0


# ---- schema-shape assertions (mirror the task's own ACCEPTANCE #4/#5) --


def test_seeded_defect_case_must_fail_is_closed_true():
    with open(
        os.path.join(SCHEMAS_DIR, "product", "verification.contract.v1.schema.json"),
        encoding="utf-8",
    ) as f:
        schema = json.load(f)
    assert schema["properties"]["seeded_defect_case"]["properties"]["must_fail"]["const"] is True


def test_seven_top_level_required_fields():
    with open(
        os.path.join(SCHEMAS_DIR, "product", "verification.contract.v1.schema.json"),
        encoding="utf-8",
    ) as f:
        schema = json.load(f)
    assert len(schema["required"]) == 7
