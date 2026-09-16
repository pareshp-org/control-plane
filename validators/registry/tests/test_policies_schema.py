"""Tests for schemas/registry/policies.registry.v1.schema.json (L1-603).

Validates fixtures directly with `jsonschema` rather than the L1-005
fixture-case harness (RULE_ID/APPLIES_TO/discover()/expect.yaml) -- FD-094
(DECIDED, PENDING_FOUNDER_DECISIONS.md) supersedes that harness in favour
of Option B (validators/registry/cli.py, R01-R18). This mirrors the
adaptation already made for L1-101 (test_defs_schema.py), L1-104
(test_people_schema.py) and L1-106 (test_platform_schema.py). Fixtures
still live at validators/registry/fixtures/policies/<case>/policies.yaml
as the task specifies.

Two discovered deviations from the task's literal text, both required to
implement it faithfully rather than force wrong arithmetic:

1. Filename: the task's FILES list names the literal path
   `schemas/registry/policies.v1.schema.json` -- that exact filename
   already exists as a different, pre-existing (Phase-0 bootstrap)
   schema with an incompatible shape (`id`/`name`/`enforced_by` --
   Section-52.6-unaware, no stage ladder, no evidence block). It is not
   superseded by any task in this lane and nothing routes its removal
   here. Overwriting it in place would silently delete that schema's
   contract for whatever (if anything) still reads it. Following the
   same non-colliding-filename convention already used for L1-102, 104
   and L1-106, this schema is authored as
   `schemas/registry/policies.registry.v1.schema.json` instead.

2. Arithmetic: the task's own SELF-VERIFY expects `REQ=21`, but its
   "Schema shape" block lists exactly 20 required keys under
   `policies[]` (id, title, owner, purpose, origin, version,
   effective_date, enforcement_stage, min_dwell, pilot_products,
   entered_at_enforce_directly, justification, exception_window_closes,
   supersedes, enforcement_mechanism, evidence, review_date,
   retirement_condition, exceptions_open, status). Likewise the task
   says "4 valid + 12 invalid = 16" but its own invalid-case table lists
   13 rows (bad_id, bad_stage, bad_status, min_dwell_negative,
   min_dwell_missing_pilot, evidence_missing_baseline,
   review_date_not_date, exceptions_open_negative, version_zero,
   missing_retirement_condition, missing_enforcement_mechanism,
   extra_policy_field, extra_top_field) -- 4 + 13 = 17, not 16. Both
   discrepancies are already recorded as mechanical defect M-E in
   lanes/L1-98-DEEP-REVIEW.md ("L1-05-L1-603 REQ=21 vs 20 and 16 vs 17").
   Implemented faithfully to the schema's own itemized field/case lists
   -- REQ=20, 17 tests -- not inventing a field or dropping a case to
   force the doc's stated numbers.

3. Known residual collision (flagged, not silently hidden): creating
   `registries/policies.yaml` (required by this task's own FILES list)
   is discovered, empirically, to make ONE pre-existing check fail:
   `tests/integration/test_registries_schema_independent.py::test_registry_file_conforms_to_schema_independent[policies.yaml]`
   (and identically `scripts/l1/jsonschema-conform.py`). Both of those
   shared, root-level tools map a top-level `registries/<stem>.yaml`
   file to whichever `schemas/**/<stem>.v1.schema.json` is uniquely
   named -- and that uniquely resolves to the pre-existing bootstrap
   `schemas/registry/policies.v1.schema.json` (id/name/enforced_by),
   the same file the sibling `registries/policies/*.yaml` bootstrap
   records legitimately depend on and already pass against. There is
   no filename choice for the new schema that satisfies both: naming it
   `policies.v1.schema.json` would break the passing bootstrap records
   instead, and naming it anything else (done here, for that reason)
   leaves the new envelope file unmapped by that stem heuristic. Fixing
   the root cause requires editing those two shared/root-level mapping
   functions, which are outside this task's own FILES list and outside
   this cluster (L1-601/L1-603 only) -- flagged as a follow-up rather
   than silently worked around or hidden.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "policies")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    policies_path = os.path.join(SCHEMAS_DIR, "policies.registry.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(policies_path, encoding="utf-8") as f:
        policies_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (policies_schema["$id"], Resource.from_contents(policies_schema)),
        ]
    )
    return policies_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "policies.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (4) ---------------------------------------------------

def test_valid_friday_freeze():
    assert _errors_for(os.path.join("valid", "friday_freeze")) == []


def test_valid_observe_stage():
    assert _errors_for(os.path.join("valid", "observe_stage")) == []


def test_valid_withdrawn():
    assert _errors_for(os.path.join("valid", "withdrawn")) == []


def test_valid_empty():
    assert _errors_for(os.path.join("valid", "empty")) == []


# ---- invalid cases (13) -------------------------------------------------

def test_bad_id():
    assert len(_errors_for("bad_id")) > 0


def test_bad_stage():
    assert len(_errors_for("bad_stage")) > 0


def test_bad_status():
    assert len(_errors_for("bad_status")) > 0


def test_min_dwell_negative():
    assert len(_errors_for("min_dwell_negative")) > 0


def test_min_dwell_missing_pilot():
    assert len(_errors_for("min_dwell_missing_pilot")) > 0


def test_evidence_missing_baseline():
    assert len(_errors_for("evidence_missing_baseline")) > 0


def test_review_date_not_date():
    assert len(_errors_for("review_date_not_date")) > 0


def test_exceptions_open_negative():
    assert len(_errors_for("exceptions_open_negative")) > 0


def test_version_zero():
    assert len(_errors_for("version_zero")) > 0


def test_missing_retirement_condition():
    assert len(_errors_for("missing_retirement_condition")) > 0


def test_missing_enforcement_mechanism():
    assert len(_errors_for("missing_enforcement_mechanism")) > 0


def test_extra_policy_field():
    assert len(_errors_for("extra_policy_field")) > 0


def test_extra_top_field():
    assert len(_errors_for("extra_top_field")) > 0
