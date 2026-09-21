"""Tests for R-INV-01 and R-INV-03 -- the 29-artifact inventory guard
(L1-704, Section 52.6; Section 0.7).

Adapted to call the rule functions directly against fixture-loaded
documents, rather than the L1-005 ``discover()``/``RULE_ID``/
``expect.yaml`` harness or the CLI "OK: N file(s) validated" / "ERROR
<rule> ..." grammar in ``lanes/L1-05-tasks.md`` -- FD-094 (DECIDED,
``contracts/validator-contract.md``) supersedes that harness and grammar
in favour of Option B (``validators/registry/cli.py``, R01-R18, frozen).
``discover()`` was never added to ``validators/registry/rules/__init__.py``
by any prior task (it ships empty); this one does not add it either.
Same adaptation already used by ``test_owners_manifest.py`` (L1-505,
this task's own dependency), ``test_service_schema.py`` (L1-404) and
``test_r_prd_11.py`` (L1-311).

9 test functions, exactly matching the task's own fixture-case table.
``test_live_tree_thirty_vs_twentynine`` asserts the R-INV-01 error fires
and names both numbers; it is not ``xfail``, because -- per the L1-505
blocker -- the error is correct behaviour on the live tree, not a defect
in the rule.
"""
import os

import jsonschema
import yaml
from referencing import Registry, Resource

from validators.registry.rules import r_inv_01, r_inv_03

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "inv")
SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schemas", "registry")


def _case_dir(*parts):
    return os.path.join(FIXTURES_DIR, *parts)


def _load_yaml(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _owners(case_dir):
    return _load_yaml(os.path.join(case_dir, "owners.yaml"))


def _inventory(case_dir):
    return _load_yaml(os.path.join(case_dir, "inventory.yaml"))


def _actual_paths(case_dir):
    """Every file in the fixture case directory except owners.yaml and
    inventory.yaml, expressed the way owners.artifacts[].path spells a
    registries/-relative file."""
    skip = {"owners.yaml", "inventory.yaml"}
    return [
        f"registries/{name}"
        for name in os.listdir(case_dir)
        if name not in skip and os.path.isfile(os.path.join(case_dir, name))
    ]


def _run_both(case_dir):
    owners_doc = _owners(case_dir)
    inventory_doc = _inventory(case_dir)
    actual = _actual_paths(case_dir)
    passed_01, findings_01 = r_inv_01.check_document(owners_doc)
    passed_03, findings_03 = r_inv_03.check_document(owners_doc, inventory_doc, actual)
    return (passed_01, findings_01), (passed_03, findings_03)


# ---- valid cases (3) -------------------------------------------------------


def test_count_matches_no_errors():
    (p01, f01), (p03, f03) = _run_both(_case_dir("valid", "count_matches"))
    assert (p01, f01) == (True, [])
    assert (p03, f03) == (True, [])


def test_tooling_files_exempt_no_errors():
    (p01, f01), (p03, f03) = _run_both(_case_dir("valid", "tooling_files_exempt"))
    assert (p01, f01) == (True, [])
    assert (p03, f03) == (True, [])


def test_no_owners_file_silent():
    case_dir = _case_dir("valid", "no_owners_file_silent")
    assert not os.path.exists(os.path.join(case_dir, "owners.yaml"))
    (p01, f01), (p03, f03) = _run_both(case_dir)
    assert (p01, f01) == (True, [])
    assert (p03, f03) == (True, [])


# ---- R-INV-01 cases (2) -----------------------------------------------------


def test_count_mismatch_fires_r_inv_01():
    case_dir = _case_dir("count_mismatch")
    (p01, f01), (p03, f03) = _run_both(case_dir)
    assert p01 is False
    assert len(f01) == 1
    assert "R-INV-01" in f01[0]
    assert (p03, f03) == (True, [])


def test_live_tree_thirty_vs_twentynine():
    owners_doc = _owners(_case_dir("live_tree_thirty_vs_twentynine"))
    passed, findings = r_inv_01.check_document(owners_doc, source="registries/OWNERS.yaml")
    assert passed is False
    assert len(findings) == 1
    assert "30" in findings[0]
    assert "29" in findings[0]
    assert "R-INV-01" in findings[0]


# ---- R-INV-03 cases (3) -----------------------------------------------------


def test_unlisted_registry_file_fires_r_inv_03():
    case_dir = _case_dir("unlisted_registry_file")
    (p01, f01), (p03, f03) = _run_both(case_dir)
    assert (p01, f01) == (True, [])
    assert p03 is False
    assert len(f03) == 1
    assert "R-INV-03" in f03[0]
    assert "stray.yaml" in f03[0]


def test_listed_but_absent_fires_r_inv_03():
    case_dir = _case_dir("listed_but_absent")
    (p01, f01), (p03, f03) = _run_both(case_dir)
    assert (p01, f01) == (True, [])
    assert p03 is False
    assert len(f03) == 1
    assert "R-INV-03" in f03[0]
    assert "missing.yaml" in f03[0]


def test_two_unlisted_fires_r_inv_03_twice():
    case_dir = _case_dir("two_unlisted")
    (p01, f01), (p03, f03) = _run_both(case_dir)
    assert (p01, f01) == (True, [])
    assert p03 is False
    assert len(f03) == 2
    assert all("R-INV-03" in f for f in f03)


# ---- schema case (1) --------------------------------------------------------


def test_declared_count_zero_is_schema_invalid():
    owners_path = os.path.join(SCHEMAS_DIR, "owners.v1.schema.json")
    import json

    with open(owners_path, encoding="utf-8") as f:
        schema = json.load(f)
    reg = Registry().with_resources([(schema["$id"], Resource.from_contents(schema))])
    validator = jsonschema.Draft202012Validator(schema, registry=reg)
    doc = _owners(_case_dir("declared_count_zero"))
    errors = list(validator.iter_errors(doc))
    assert len(errors) > 0
