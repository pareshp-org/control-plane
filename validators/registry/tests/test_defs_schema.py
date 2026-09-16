"""Tests for schemas/registry/common/defs.v1.schema.json (L1-101).

Adapted to validate directly against the schema with `jsonschema`
rather than the L1-005 fixture-case harness (RULE_ID/APPLIES_TO/
discover()) -- FD-094 (DECIDED) supersedes that harness in favour of
the Option B CLI design (validators/registry/cli.py). The $defs
content itself is dispatch-agnostic, so it is tested directly.
"""
import json
import os

import jsonschema
import pytest

DEFS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "schemas", "registry", "common", "defs.v1.schema.json",
)


def _load():
    with open(DEFS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _validator_for(def_name):
    schema = _load()
    ref_schema = {"$ref": f"#/$defs/{def_name}", "$defs": schema["$defs"]}
    return jsonschema.Draft202012Validator(ref_schema)


def _accepts(def_name, value):
    v = _validator_for(def_name)
    errors = list(v.iter_errors(value))
    return len(errors) == 0


def test_iso_date():
    assert _accepts("isoDate", "2026-09-15")
    assert not _accepts("isoDate", "2026-9-15")


def test_iso_date_or_null():
    assert _accepts("isoDateOrNull", "2026-09-15")
    assert _accepts("isoDateOrNull", None)
    assert not _accepts("isoDateOrNull", "not-a-date")


def test_stable_id():
    assert _accepts("stableId", "bendrohit-eng")
    assert not _accepts("stableId", "Bad_ID!")


def test_github_login():
    assert _accepts("githubLogin", "octocat-99")
    assert not _accepts("githubLogin", "-leading-hyphen")


def test_iana_timezone():
    assert _accepts("ianaTimezone", "Asia/Kolkata")
    assert not _accepts("ianaTimezone", "IST")


def test_hhmm():
    assert _accepts("hhmm", "09:30")
    assert not _accepts("hhmm", "24:00")


def test_capability():
    schema = _load()
    enum = schema["$defs"]["capability"]["enum"]
    assert len(enum) == 27
    assert _accepts("capability", "backend")
    assert not _accepts("capability", "not-a-capability")


def test_dangerous_capability():
    schema = _load()
    dangerous = schema["$defs"]["dangerousCapability"]["enum"]
    capability = schema["$defs"]["capability"]["enum"]
    assert len(dangerous) == 8
    assert set(dangerous).issubset(set(capability))
    assert _accepts("dangerousCapability", "platform-admin")
    assert not _accepts("dangerousCapability", "backend")


def test_assignment_type():
    schema = _load()
    enum = schema["$defs"]["assignmentType"]["enum"]
    assert len(enum) == 17
    assert _accepts("assignmentType", "primary_owner")
    assert not _accepts("assignmentType", "not-an-assignment-type")


def test_drift_class():
    assert _accepts("driftClass", "amber")
    assert not _accepts("driftClass", "yellow")


def test_employment_type():
    assert _accepts("employmentType", "contractor")
    assert not _accepts("employmentType", "freelancer")


def test_availability():
    assert _accepts("availability", "on_leave")
    assert not _accepts("availability", "vacationing")


def test_access_status():
    assert _accepts("accessStatus", "provisioned")
    assert not _accepts("accessStatus", "granted")


def test_decision_record_id():
    assert _accepts("decisionRecordId", "DEC-2026-001")
    assert not _accepts("decisionRecordId", "DECISION-1")
