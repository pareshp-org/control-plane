"""access/tests/test_machine_identity.py

Behavioral pytest suite for L5-T13 (spec 90.2, machine-identities row,
invariant 106). Each test invokes the real request-time CLI --
`access/tools/check_machine_identity_boundary.py --grants <yaml>` -- against
a freshly built grants snapshot, so this suite genuinely exercises the
evaluator's outcome for a specific request rather than re-checking the
already-committed repo tree. One test per machine identity, per the L5-T13
acceptance criteria ("Tests cover all 5 machine identities -- one test
each").
"""
import os
import subprocess
import sys

import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI = os.path.join(REPO_ROOT, "access", "tools", "check_machine_identity_boundary.py")
IDENTITIES = (
    "reconciler",
    "provisioning-cli",
    "ops-console",
    "background-agents",
    "background-machine-layer",
)
POISON_CATEGORY = "Individual utilisation detail"


def _run_with_poisoned_identity(tmp_path, poisoned_identity):
    """Build a grants snapshot where every identity is clean except
    `poisoned_identity`, which holds POISON_CATEGORY, and run the CLI
    against it."""
    grants = {identity: [] for identity in IDENTITIES}
    grants[poisoned_identity] = [POISON_CATEGORY]
    grants_path = tmp_path / ("grants-%s.yaml" % poisoned_identity)
    grants_path.write_text(yaml.safe_dump(grants), encoding="utf-8")
    return subprocess.run(
        [sys.executable, CLI, "--grants", str(grants_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_reconciler_poisoned_grant_is_caught(tmp_path):
    result = _run_with_poisoned_identity(tmp_path, "reconciler")
    assert result.returncode == 1
    assert "MACHINE IDENTITY BOUNDARY FAIL: reconciler" in result.stdout
    assert POISON_CATEGORY in result.stdout


def test_provisioning_cli_poisoned_grant_is_caught(tmp_path):
    result = _run_with_poisoned_identity(tmp_path, "provisioning-cli")
    assert result.returncode == 1
    assert "MACHINE IDENTITY BOUNDARY FAIL: provisioning-cli" in result.stdout
    assert POISON_CATEGORY in result.stdout


def test_ops_console_poisoned_grant_is_caught(tmp_path):
    result = _run_with_poisoned_identity(tmp_path, "ops-console")
    assert result.returncode == 1
    assert "MACHINE IDENTITY BOUNDARY FAIL: ops-console" in result.stdout
    assert POISON_CATEGORY in result.stdout


def test_background_agents_poisoned_grant_is_caught(tmp_path):
    result = _run_with_poisoned_identity(tmp_path, "background-agents")
    assert result.returncode == 1
    assert "MACHINE IDENTITY BOUNDARY FAIL: background-agents" in result.stdout
    assert POISON_CATEGORY in result.stdout


def test_background_machine_layer_poisoned_grant_is_caught(tmp_path):
    result = _run_with_poisoned_identity(tmp_path, "background-machine-layer")
    assert result.returncode == 1
    assert "MACHINE IDENTITY BOUNDARY FAIL: background-machine-layer" in result.stdout
    assert POISON_CATEGORY in result.stdout
