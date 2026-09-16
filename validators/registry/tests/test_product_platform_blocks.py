"""Tests for the `infrastructure`, `dependencies`, `security`,
`ai_runtime_dependency`, `ai_restrictions`, `data`, `observability`,
`automated_containment` and `business` blocks added to
schemas/product/product.contract.v2.schema.json (L1-304).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 fixture-case harness -- FD-094 (DECIDED) supersedes that harness in
favour of Option B, the same adaptation test_product_envelope.py and
test_product_delivery_blocks.py already document.

Companion change (Deep-Review B24), same as L1-303: this task's schema
edit adds nine more top-level *required* blocks to the same
additionalProperties:false document. Regenerates L1-301's two envelope
fixtures and L1-303's three delivery fixtures in place with the new
blocks filled in (minimal, schema-valid values) so they stay green --
see test_product_envelope.py (14/14) and test_product_delivery_blocks.py
(18/18), unchanged, after this change.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "product", "platform")


def _registry():
    defs_path = os.path.join(SCHEMAS_ROOT, "registry", "common", "defs.v1.schema.json")
    assignments_path = os.path.join(SCHEMAS_ROOT, "registry", "common", "assignments.v1.schema.json")
    product_path = os.path.join(SCHEMAS_ROOT, "product", "product.contract.v2.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(assignments_path, encoding="utf-8") as f:
        assignments_schema = json.load(f)
    with open(product_path, encoding="utf-8") as f:
        product_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (assignments_schema["$id"], Resource.from_contents(assignments_schema)),
            (product_schema["$id"], Resource.from_contents(product_schema)),
        ]
    )
    return product_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "product.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (4) -----------------------------------------------------

def test_valid_service_full():
    assert _errors_for(os.path.join("valid", "service_full")) == []


def test_valid_client_app_null_endpoints():
    """Section 15.7 exempts client-app from the health/version endpoints."""
    assert _errors_for(os.path.join("valid", "client_app_null_endpoints")) == []


def test_valid_no_ai_runtime():
    assert _errors_for(os.path.join("valid", "no_ai_runtime")) == []


def test_valid_data_null():
    assert _errors_for(os.path.join("valid", "data_null")) == []


# ---- invalid cases (17) --------------------------------------------------

def test_missing_budget_band():
    assert len(_errors_for("missing_budget_band")) > 0


def test_budget_bad_currency():
    assert len(_errors_for("budget_bad_currency")) > 0


def test_budget_negative():
    assert len(_errors_for("budget_negative")) > 0


def test_scorecard_above_ten():
    assert len(_errors_for("scorecard_above_ten")) > 0


def test_ai_runtime_no_evaluation():
    """AT-049: ai_runtime_dependency without an evaluation suite fails."""
    assert len(_errors_for("ai_runtime_no_evaluation")) > 0


def test_ai_runtime_empty_providers():
    assert len(_errors_for("ai_runtime_empty_providers")) > 0


def test_data_bad_classification():
    assert len(_errors_for("data_bad_classification")) > 0


def test_data_bad_isolation():
    assert len(_errors_for("data_bad_isolation")) > 0


def test_retention_zero():
    assert len(_errors_for("retention_zero")) > 0


def test_telemetry_bad_enum():
    assert len(_errors_for("telemetry_bad_enum")) > 0


def test_containment_bad_action():
    assert len(_errors_for("containment_bad_action")) > 0


def test_business_missing_criticality():
    """Section 15.5: business.criticality is required."""
    assert len(_errors_for("business_missing_criticality")) > 0


def test_business_bad_criticality():
    assert len(_errors_for("business_bad_criticality")) > 0


def test_dependencies_internal_bad_id():
    assert len(_errors_for("dependencies_internal_bad_id")) > 0


def test_extra_field_in_security():
    assert len(_errors_for("extra_field_in_security")) > 0


def test_missing_ai_restrictions():
    assert len(_errors_for("missing_ai_restrictions")) > 0


def test_subprocessors_not_array():
    assert len(_errors_for("subprocessors_not_array")) > 0
