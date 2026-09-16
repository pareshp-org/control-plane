"""Tests for schemas/product/product.contract.v2.schema.json -- envelope,
`identity`, `classification` blocks (L1-301).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 fixture-case harness -- FD-094 (DECIDED) supersedes that harness in
favour of Option B (validators/registry/cli.py), the same adaptation
`test_people_schema.py` and `test_platform_schema.py` already document.

Fixture-count note: the task text says "exactly 15 functions" but its own
fixture-case list under `envelope/` names only 14 directories (2 valid + 12
invalid) -- `L1-99-review.md` flags this exact arithmetic mismatch for
L1-301 ("fifteen tests against fourteen listed fixture cases"), and
`L1-05-tasks.md` L1-904 tells the executor not to invent a field or a case
to force a stale count when the discrepancy traces to one of its four
named tasks. This file ships one test per the 14 real fixture cases,
matching `L1-CONCORDANCE.md`'s own count for this task, rather than adding
a 15th test with no fixture behind it.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "product", "envelope")


def _registry():
    defs_path = os.path.join(SCHEMAS_ROOT, "registry", "common", "defs.v1.schema.json")
    product_path = os.path.join(SCHEMAS_ROOT, "product", "product.contract.v2.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(product_path, encoding="utf-8") as f:
        product_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
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


# ---- valid cases (2) ---------------------------------------------------

def test_valid_service_minimal():
    assert _errors_for(os.path.join("valid", "service_minimal")) == []


def test_valid_novel_class():
    """§15.3: classification.class stays an open string -- a value outside
    the six illustrative tokens ("customer-success-pilot") must NOT fail.
    AT-001, invariant 53."""
    assert _errors_for(os.path.join("valid", "novel_class")) == []


# ---- invalid cases (12) -------------------------------------------------

def test_wrong_contract_version():
    assert len(_errors_for("wrong_contract_version")) > 0


def test_missing_conformance_profile():
    assert len(_errors_for("missing_conformance_profile")) > 0


def test_bad_conformance_profile():
    assert len(_errors_for("bad_conformance_profile")) > 0


def test_missing_identity():
    assert len(_errors_for("missing_identity")) > 0


def test_bad_lifecycle():
    assert len(_errors_for("bad_lifecycle")) > 0


def test_bad_launch_status():
    assert len(_errors_for("bad_launch_status")) > 0


def test_missing_reliability_criticality():
    assert len(_errors_for("missing_reliability_criticality")) > 0


def test_criticality_enum_violation():
    assert len(_errors_for("criticality_enum_violation")) > 0


def test_identity_extra_field():
    assert len(_errors_for("identity_extra_field")) > 0


def test_top_level_extra_field():
    assert len(_errors_for("top_level_extra_field")) > 0


def test_created_not_date():
    assert len(_errors_for("created_not_date")) > 0


def test_domain_bad_id():
    assert len(_errors_for("domain_bad_id")) > 0
