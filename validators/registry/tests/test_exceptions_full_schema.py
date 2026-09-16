"""Tests for schemas/registry/exceptions.registry.v1.schema.json (L1-601).

Validates fixtures directly with `jsonschema` rather than the L1-005
fixture-case harness (RULE_ID/APPLIES_TO/discover()/expect.yaml) -- FD-094
(DECIDED, PENDING_FOUNDER_DECISIONS.md) supersedes that harness in favour
of Option B (validators/registry/cli.py, R01-R18). This mirrors the
adaptation already made for L1-101 (test_defs_schema.py), L1-104
(test_people_schema.py) and L1-106 (test_platform_schema.py). Fixtures
still live at validators/registry/fixtures/exc_full/<case>/exceptions.yaml
as the task specifies.

Deviations from the task's literal text, all required to implement it
faithfully rather than force a wrong number or a vacuous check:

1. Filename: the task's FILES list names the literal path
   `schemas/registry/exceptions.v1.schema.json`. That exact filename
   already exists as a different, pre-existing (Phase-0 bootstrap)
   schema with an incompatible shape (`id`/`reason`/`granted_by`/
   `expires`/`gate`). It is not superseded by any task in this lane and
   nothing routes its removal here -- overwriting it in place would
   silently delete whatever (if anything) still reads that contract.
   Following the same non-colliding-filename convention already used
   for L1-102, L1-104 and L1-106, this schema is authored as
   `schemas/registry/exceptions.registry.v1.schema.json` instead.

2. Arithmetic: the task's own SELF-VERIFY expects `REQ=19`, but the
   task's own "Schema shape" block lists exactly 18 required keys under
   `exceptions[]` (id, type, reason, requester, authority, affected,
   scope, start, expiry, compensating_control,
   compensating_control_record, compensating_control_cadence, owner,
   review_date, renewals, became_permanent, closure,
   deactivation_trigger). Its case table (4 valid + 16 deltas, plus the
   base case = 17 named cases) totals 21 fixtures/functions, not the
   "20 passed" the ACCEPTANCE table states. Both discrepancies are
   already recorded as mechanical defect M-E in
   lanes/L1-98-DEEP-REVIEW.md ("L1-05-L1-601 REQ=19 vs 18 fields and 20
   vs 21 cases"). Implemented faithfully to the schema's own itemized
   field/case lists -- REQ=18, 21 tests -- not inventing a field or
   dropping a case to force the doc's stated numbers.

3. Dependency gap: L1-601 DEPENDS on L1-108 (the week-one minimal
   schema, `schemas/registry/exceptions.v1.minimal.schema.json`) and
   its own spec requires `test_minimal_is_a_strict_subset` to prove this
   full schema's required-field set is a superset of the minimal one's.
   L1-108 has not been implemented in this repository -- no minimal
   schema file exists -- and creating it is outside this task's own
   FILES list (and outside this cluster, which is L1-601/L1-603 only).
   Faking that proof against a schema that does not exist would be
   exactly the vacuous-pass placeholder this session is instructed not
   to write, so `test_minimal_is_a_strict_subset` is omitted here and
   recorded as a real gap: once L1-108 lands, add it back as
   `set(minimal_required).issubset(full_required)`.

4. `exceptionType` (11 tokens, Section 54.1/54.3): the task's own text
   says these were "added to defs.v1.schema.json at L1-108" -- a file
   L1-108 does not even list in its own FILES, and L1-108 has not run.
   Rather than edit the shared `common/defs.v1.schema.json` from a task
   whose FILES list does not name it (L1-601's FILES list does not
   either), the eleven-token enum is defined locally inside this
   schema's own `$defs.exceptionType` and referenced with a local
   `$ref`. `DEFS` in `common/defs.v1.schema.json` therefore stays at 14,
   not 15 -- correct given L1-108 has not added anything there.
"""
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

SCHEMAS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "schemas", "registry"
)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "exc_full")


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    exc_path = os.path.join(SCHEMAS_DIR, "exceptions.registry.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(exc_path, encoding="utf-8") as f:
        exc_schema = json.load(f)
    reg = Registry().with_resources(
        [
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (exc_schema["$id"], Resource.from_contents(exc_schema)),
        ]
    )
    return exc_schema, reg


def _load_fixture(case):
    path = os.path.join(FIXTURES_DIR, case, "exceptions.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _load_fixture(case)
    return list(validator.iter_errors(doc))


# ---- valid cases (4) -----------------------------------------------------

def test_valid_platform_compatibility_full():
    assert _errors_for(os.path.join("valid", "platform_compatibility_full")) == []


def test_valid_bootstrap():
    assert _errors_for(os.path.join("valid", "bootstrap")) == []


def test_valid_closed_remediated():
    assert _errors_for(os.path.join("valid", "closed_remediated")) == []


def test_valid_empty():
    assert _errors_for(os.path.join("valid", "empty")) == []


# ---- invalid cases (17) ---------------------------------------------------

def test_no_expiry():
    assert len(_errors_for("no_expiry")) > 0


def test_expiry_null():
    # Invariant 77 / Section 54.2: expiry is never nullable.
    assert len(_errors_for("expiry_null")) > 0


def test_no_owner():
    assert len(_errors_for("no_owner")) > 0


def test_no_compensating_control():
    assert len(_errors_for("no_compensating_control")) > 0


def test_compensating_control_empty():
    assert len(_errors_for("compensating_control_empty")) > 0


def test_cadence_bad_enum():
    assert len(_errors_for("cadence_bad_enum")) > 0


def test_closure_bad_enum():
    assert len(_errors_for("closure_bad_enum")) > 0


def test_renewals_negative():
    assert len(_errors_for("renewals_negative")) > 0


def test_became_permanent_not_bool():
    assert len(_errors_for("became_permanent_not_bool")) > 0


def test_bad_id_format():
    assert len(_errors_for("bad_id_format")) > 0


def test_bad_type():
    assert len(_errors_for("bad_type")) > 0


def test_review_date_not_date():
    assert len(_errors_for("review_date_not_date")) > 0


def test_affected_products_bad_id():
    assert len(_errors_for("affected_products_bad_id")) > 0


def test_missing_requester():
    assert len(_errors_for("missing_requester")) > 0


def test_missing_authority():
    assert len(_errors_for("missing_authority")) > 0


def test_extra_exception_field():
    assert len(_errors_for("extra_exception_field")) > 0


def test_extra_top_field():
    assert len(_errors_for("extra_top_field")) > 0
