"""L3-P4-06: repo-from-template and required-file assertion."""

from __future__ import annotations

import pytest

from tools.provision.repo import (
    MissingRequiredCommand,
    MissingRequiredFile,
    REQUIRED_COMMANDS,
    REQUIRED_FILES,
    plan_repo,
)

FULL_TEMPLATE_FILES = (
    ".env.example",
    "docker-compose.dev.yml",
    "Makefile",
    "seed/",
    "migrations/",
    "verification/",
    "AGENTS.md",
    "product.yaml",
)


def test_full_template_plans_private_with_no_env_or_app_access():
    plan = plan_repo("alpha", FULL_TEMPLATE_FILES, REQUIRED_COMMANDS)
    assert plan.private is True
    assert plan.environment_access is False
    assert plan.third_party_app_access is False
    assert len(plan.files_verified) == 8
    assert len(REQUIRED_FILES) == 8
    assert len(REQUIRED_COMMANDS) == 8


def test_missing_required_file_is_hard_failure():
    files = [f for f in FULL_TEMPLATE_FILES if f != "AGENTS.md"]
    with pytest.raises(MissingRequiredFile):
        plan_repo("alpha", files, REQUIRED_COMMANDS)


def test_missing_required_directory_is_hard_failure():
    files = [f for f in FULL_TEMPLATE_FILES if f != "seed/"]
    with pytest.raises(MissingRequiredFile):
        plan_repo("alpha", files, REQUIRED_COMMANDS)


def test_product_yaml_or_pointer_alternative_satisfies_requirement():
    files = [f for f in FULL_TEMPLATE_FILES if f != "product.yaml"] + [".product-pointer"]
    plan = plan_repo("alpha", files, REQUIRED_COMMANDS)
    assert plan.private is True


def test_missing_both_product_yaml_and_pointer_is_hard_failure():
    files = [f for f in FULL_TEMPLATE_FILES if f != "product.yaml"]
    with pytest.raises(MissingRequiredFile) as excinfo:
        plan_repo("alpha", files, REQUIRED_COMMANDS)
    assert "product.yaml or .product-pointer" in str(excinfo.value)


def test_missing_required_command_is_hard_failure():
    commands = [c for c in REQUIRED_COMMANDS if c != "parity"]
    with pytest.raises(MissingRequiredCommand):
        plan_repo("alpha", FULL_TEMPLATE_FILES, commands)
