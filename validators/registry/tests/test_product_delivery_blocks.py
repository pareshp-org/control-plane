"""Tests for the `code`, `verification`, `environments`, `deployment` and
`reversibility_default` blocks added to
schemas/product/product.contract.v2.schema.json (L1-303).

Adapted to validate fixtures directly with `jsonschema` rather than the
L1-005 fixture-case harness -- FD-094 (DECIDED) supersedes that harness in
favour of Option B, the same adaptation test_product_envelope.py already
documents.

Companion change (Deep-Review B24): this task's schema edit adds new
top-level *required* blocks to the same `additionalProperties: false`
document L1-301 already shipped fixtures for. Left alone, L1-301's two
valid fixtures (`service_minimal`, `novel_class`) would fail retroactively
-- missing the newly-required `code`/`verification`/`environments`/
`deployment`/`assignments`/`escalation`/`reversibility_default` keys --
exactly the fixture-rot B24 describes for L1-301..L1-308. This commit
regenerates those two fixtures in place with the new blocks filled in
(minimal, schema-valid values), rather than leaving them to rot; see
test_product_envelope.py, still 14/14 passing, for the result.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "product", "delivery")


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


# ---- valid cases (3) -----------------------------------------------------

def test_valid_single_repo():
    assert _errors_for(os.path.join("valid", "single_repo")) == []


def test_valid_three_repos():
    """AT-010, invariant 62: one product may declare many repositories."""
    assert _errors_for(os.path.join("valid", "three_repos")) == []


def test_valid_no_staged_rollout():
    assert _errors_for(os.path.join("valid", "no_staged_rollout")) == []


# ---- invalid cases (15) --------------------------------------------------

def test_zero_repositories():
    assert len(_errors_for("zero_repositories")) > 0


def test_repo_name_no_slash():
    assert len(_errors_for("repo_name_no_slash")) > 0


def test_gsd_version_latest():
    assert len(_errors_for("gsd_version_latest")) > 0


def test_gsd_version_next():
    assert len(_errors_for("gsd_version_next")) > 0


def test_gsd_version_unpinned():
    assert len(_errors_for("gsd_version_unpinned")) > 0


def test_missing_default_branch():
    assert len(_errors_for("missing_default_branch")) > 0


def test_verification_bad_enum():
    assert len(_errors_for("verification_bad_enum")) > 0


def test_missing_contract_path():
    assert len(_errors_for("missing_contract_path")) > 0


def test_deployment_bad_progressive():
    assert len(_errors_for("deployment_bad_progressive")) > 0


def test_staged_rollout_extra_field():
    assert len(_errors_for("staged_rollout_extra_field")) > 0


def test_stages_pct_out_of_range():
    assert len(_errors_for("stages_pct_out_of_range")) > 0


def test_crash_free_missing_sev1():
    assert len(_errors_for("crash_free_missing_sev1")) > 0


def test_reversibility_bad_enum():
    assert len(_errors_for("reversibility_bad_enum")) > 0


def test_escalation_missing():
    assert len(_errors_for("escalation_missing")) > 0


def test_assignments_not_array():
    assert len(_errors_for("assignments_not_array")) > 0
