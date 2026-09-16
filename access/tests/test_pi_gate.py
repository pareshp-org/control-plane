"""access/tests/test_pi_gate.py

Behavioral pytest suite for L5-T14 (spec 90.4, D109, invariant 106,
AT-090, AT-091). Each test invokes the real request-time CLI --
`access/tools/check_people_intelligence_gate.py --request <yaml>` -- against
one of the four fixtures under access/tests/fixtures/, so this suite
genuinely exercises the gate's outcome for a specific request rather than
re-checking the already-committed repo tree (that is what --selftest does,
and it is left untouched: at-091-capability-gate.sh and
at-100-conduct-separation.sh both depend on its exact output).
"""
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI = os.path.join(REPO_ROOT, "access", "tools", "check_people_intelligence_gate.py")
FIXTURES = os.path.join(REPO_ROOT, "access", "tests", "fixtures")


def _run(fixture_name):
    fixture_path = os.path.join(FIXTURES, fixture_name)
    return subprocess.run(
        [sys.executable, CLI, "--request", fixture_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_delegation_grant_fails():
    """Acceptance criterion 1: a fixture assignment granting
    people-intelligence exits 1 (D109, invariant 106, AT-090)."""
    result = _run("pi-request-delegation-grant.yaml")
    assert result.returncode == 1
    assert "PI GATE FAIL" in result.stdout
    assert "not delegable" in result.stdout


def test_own_data_self_view_by_non_holder_passes():
    """Acceptance criterion 2: own-data self-view by a non-holder exits 0
    (AT-090's self-view carve-out)."""
    result = _run("pi-request-self-view.yaml")
    assert result.returncode == 0
    assert "PI GATE FAIL" not in result.stdout


def test_another_persons_data_by_non_holder_fails():
    """Acceptance criterion 3: another person's data requested by a
    non-holder exits 1 (the peer block, Section 90.4)."""
    result = _run("pi-request-peer-block.yaml")
    assert result.returncode == 1
    assert "PI GATE FAIL" in result.stdout


def test_conduct_record_access_by_holder_fails():
    """Acceptance criterion 4: conduct-record access by a holder exits 1
    (holding people-intelligence never grants conduct-record access,
    Section 90.4/88)."""
    result = _run("pi-request-conduct-holder.yaml")
    assert result.returncode == 1
    assert "PI GATE FAIL" in result.stdout
    assert "conduct-record" in result.stdout
