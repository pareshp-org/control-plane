"""Tests for L3-P4-02: CODEOWNERS generator, human identities only."""

from __future__ import annotations

import pytest

from tools.provision.codeowners import (
    MachineIdentityInCodeowners,
    generate,
    generate_from_registry,
)

_PEOPLE = [
    {"github_login": "founder-1", "availability": "active", "capabilities": ["platform-admin"]},
    {"github_login": "lead-1", "availability": "active", "capabilities": ["reviewer-matrix-change"]},
    {"github_login": "dev-1", "availability": "active", "capabilities": ["code-review"]},
    {"github_login": "qa-1", "availability": "active", "capabilities": ["verification"]},
]

_PRODUCT_YAML = {
    "assignments": {
        "primary_owner": "lead-1",
        "cross_reviewer": "dev-1",
        "backup_owner": "founder-1",
        "incident_responder_primary": "lead-1",
        "incident_responder_backup": "dev-1",
        "verification_responsibility": "qa-1",
    }
}


def test_generate_alpha_contains_no_machine_identity():
    out = generate("alpha", "fixture-a")
    assert "@ci-bot" not in out
    assert not any("[bot]" in line for line in out.splitlines())


def test_four_rules_appear_in_order():
    out = generate_from_registry(_PRODUCT_YAML, _PEOPLE)
    lines = out.splitlines()
    paths_in_order = [line.split()[0] for line in lines]
    assert paths_in_order == ["*", "/verification/", "/product.yaml", "/migrations/", "/.github/workflows/"]
    # Rule 1: product source paths -> the product Team (every current holder).
    assert lines[0] == "* @lead-1 @dev-1 @founder-1"
    # Rule 2: verification/ -> verification_responsibility.
    assert lines[1] == "/verification/ @qa-1"
    # Rules 3 and 4: product.yaml, migrations/, workflows/ -> the Team Lead role.
    assert lines[2] == "/product.yaml @lead-1"
    assert lines[3] == "/migrations/ @lead-1"
    assert lines[4] == "/.github/workflows/ @lead-1"


def test_injected_machine_login_raises_rather_than_emits():
    poisoned = dict(_PRODUCT_YAML)
    poisoned["assignments"] = dict(_PRODUCT_YAML["assignments"])
    poisoned["assignments"]["primary_owner"] = "ci-bot[bot]"
    with pytest.raises(MachineIdentityInCodeowners):
        generate_from_registry(poisoned, _PEOPLE)


def test_login_absent_from_people_yaml_raises():
    poisoned = dict(_PRODUCT_YAML)
    poisoned["assignments"] = dict(_PRODUCT_YAML["assignments"])
    poisoned["assignments"]["cross_reviewer"] = "not-a-real-person"
    with pytest.raises(MachineIdentityInCodeowners):
        generate_from_registry(poisoned, _PEOPLE)


def test_missing_verifier_omits_rule_2_without_crashing():
    product_yaml = {
        "assignments": {
            "primary_owner": "dev-1",
            "cross_reviewer": "",
            "backup_owner": "",
            "incident_responder_primary": "",
            "incident_responder_backup": "",
            "verification_responsibility": "",
        }
    }
    out = generate_from_registry(product_yaml, _PEOPLE)
    lines = out.splitlines()
    assert not any(line.startswith("/verification/") for line in lines)
    assert lines[0] == "* @dev-1"


def test_no_current_team_lead_omits_rules_3_and_4():
    people_without_lead = [
        dict(p, capabilities=[c for c in p["capabilities"] if c != "reviewer-matrix-change"])
        for p in _PEOPLE
    ]
    out = generate_from_registry(_PRODUCT_YAML, people_without_lead)
    lines = out.splitlines()
    assert not any(line.startswith("/product.yaml") for line in lines)
    assert not any(line.startswith("/migrations/") for line in lines)
    assert not any(line.startswith("/.github/workflows/") for line in lines)
