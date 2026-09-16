"""Tests for schemas/registry/service.v1.schema.json plus rules R-SVC-01,
R-SVC-02, R-SVC-03 (L1-404).

Adapted to validate fixtures directly with `jsonschema` and to call the
rule functions directly, rather than the L1-005 discover()/RULE_ID/
APPLIES_TO harness or the CLI "OK: N file(s) validated" / "ERROR <rule>"
grammar in lanes/L1-05-tasks.md -- FD-094 (DECIDED) supersedes that
harness and grammar in favour of Option B
(validators/registry/cli.py, R01-R18). This task's three rule modules
(r_svc_01/02/03.py) are standalone functions, not wired into the R01-R18
dispatch table -- see their module docstrings for why extending that
frozen catalogue is out of scope here. Fixtures still live at
validators/registry/fixtures/service/<case>/service.yaml exactly as the
task specifies, with a sibling product.yaml or people.yaml where a case
exercises a cross-file rule.

`schemas/registry/common/assignments.v1.schema.json` (L1-302) had not
landed when this task's ORDERING NOTE was written; it exists now (a
concurrent commit), so `assignments` here is a real `$ref` to it rather
than a locally duplicated shape.
"""
import datetime
import json
import os

import jsonschema
import yaml
from referencing import Registry, Resource

from validators.registry.rules import r_svc_01, r_svc_02, r_svc_03

SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas", "registry")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "service")

TODAY = datetime.date(2026, 8, 27)


def _registry():
    defs_path = os.path.join(SCHEMAS_DIR, "common", "defs.v1.schema.json")
    assignments_path = os.path.join(SCHEMAS_DIR, "common", "assignments.v1.schema.json")
    service_path = os.path.join(SCHEMAS_DIR, "service.v1.schema.json")
    with open(defs_path, encoding="utf-8") as f:
        defs_schema = json.load(f)
    with open(assignments_path, encoding="utf-8") as f:
        assignments_schema = json.load(f)
    with open(service_path, encoding="utf-8") as f:
        service_schema = json.load(f)
    reg = Registry().with_resources(
        [
            (defs_schema["$id"], Resource.from_contents(defs_schema)),
            ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
            (assignments_schema["$id"], Resource.from_contents(assignments_schema)),
            (service_schema["$id"], Resource.from_contents(service_schema)),
        ]
    )
    return service_schema, reg


def _load(case, filename):
    path = os.path.join(FIXTURES_DIR, case, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _service(case):
    return _load(case, "service.yaml")


def _schema_errors_for(case):
    schema, reg = _registry()
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _service(case)
    return list(validator.iter_errors(doc))


def _known_product_ids(case):
    doc = _load(case, "product.yaml")
    if doc is None:
        return None
    return {doc["identity"]["id"]}


def _known_person_ids(case):
    doc = _load(case, "people.yaml")
    if doc is None:
        return None
    return {p["id"] for p in doc.get("people", [])}


# ---- valid cases (4) ----------------------------------------------------


def test_valid_auth_service_full():
    case = os.path.join("valid", "auth_service_full")
    assert _schema_errors_for(case) == []
    assert r_svc_01.check(_service(case), _known_product_ids(case)) == []
    assert r_svc_02.check(_service(case), TODAY) == []
    assert r_svc_03.check(_service(case), _known_person_ids(case)) == []


def test_valid_no_consumers():
    case = os.path.join("valid", "no_consumers")
    assert _schema_errors_for(case) == []
    assert r_svc_01.check(_service(case), _known_product_ids(case)) == []


def test_valid_library_type():
    case = os.path.join("valid", "library_type")
    assert _schema_errors_for(case) == []


def test_valid_consumer_resolves():
    case = os.path.join("valid", "consumer_resolves")
    assert _schema_errors_for(case) == []
    findings = r_svc_01.check(_service(case), _known_product_ids(case))
    assert findings == []


# ---- schema-only invalid cases (9) --------------------------------------


def test_bad_service_version():
    assert len(_schema_errors_for("bad_service_version")) > 0


def test_identity_repo_no_slash():
    assert len(_schema_errors_for("identity_repo_no_slash")) > 0


def test_identity_bad_type():
    assert len(_schema_errors_for("identity_bad_type")) > 0


def test_consumers_not_unique():
    assert len(_schema_errors_for("consumers_not_unique")) > 0


def test_consumer_contract_tests_optional():
    assert len(_schema_errors_for("consumer_contract_tests_optional")) > 0


def test_severity_inheritance_other():
    assert len(_schema_errors_for("severity_inheritance_other")) > 0


def test_missing_compatibility():
    assert len(_schema_errors_for("missing_compatibility")) > 0


def test_supported_versions_empty():
    assert len(_schema_errors_for("supported_versions_empty")) > 0


def test_extra_top_field():
    assert len(_schema_errors_for("extra_top_field")) > 0


# ---- rule-driven invalid cases (4) ---------------------------------------


def test_consumer_unknown_product():
    case = "consumer_unknown_product"
    assert _schema_errors_for(case) == []
    findings = r_svc_01.check(_service(case), _known_product_ids(case))
    assert len(findings) == 1
    assert "product-99" in findings[0]


def test_escalation_names_person():
    case = "escalation_names_person"
    assert _schema_errors_for(case) == []
    findings = r_svc_03.check(_service(case), _known_person_ids(case))
    assert len(findings) == 1
    assert "dev-b" in findings[0]


def test_no_primary_owner():
    case = "no_primary_owner"
    assert _schema_errors_for(case) == []
    findings = r_svc_02.check(_service(case), TODAY)
    assert len(findings) == 1
    assert "primary_owner" in findings[0]


def test_no_cross_reviewer():
    case = "no_cross_reviewer"
    assert _schema_errors_for(case) == []
    findings = r_svc_02.check(_service(case), TODAY)
    assert len(findings) == 1
    assert "cross_reviewer" in findings[0]


# ---- schema-shape / rule-silence assertions (mirror the task's own -----
# ---- ACCEPTANCE #4/#6 and the "silent when counterpart absent" rule) ---


def test_consumer_contract_tests_is_closed_required():
    with open(os.path.join(SCHEMAS_DIR, "service.v1.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["properties"]["verification"]["properties"]["consumer_contract_tests"]["const"] == "required"


def test_incident_severity_inheritance_is_closed_highest_consumer():
    with open(os.path.join(SCHEMAS_DIR, "service.v1.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    assert (
        schema["properties"]["operations"]["properties"]["incident_severity_inheritance"]["const"]
        == "highest-consumer"
    )


def test_rules_silent_when_counterpart_document_absent():
    case = os.path.join("valid", "auth_service_full")  # no product.yaml/people.yaml sibling
    assert _known_product_ids(case) is None
    assert _known_person_ids(case) is None
    assert r_svc_01.check(_service(case), None) == []
    assert r_svc_03.check(_service(case), None) == []


def test_services_gitkeep_creates_empty_tree():
    services_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "registries", "services"
    )
    assert os.path.isfile(os.path.join(services_dir, ".gitkeep"))
    live = [
        p
        for p in os.listdir(services_dir)
        if p != ".gitkeep"
    ]
    assert live == []
