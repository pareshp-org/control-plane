"""Unit tests for L2-T517: seeded_defect."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = REPO_ROOT / "tools" / "evidence" / "fixtures" / "seeded"


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "tools.evidence.seeded_defect", *args]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_seeded_case_failed_is_healthy():
    result_path = str(FIXTURES_DIR / "case-failed.json")
    res = run_tool("--result", result_path, "--summary")
    assert res.returncode == 0
    assert "OK seeded_defect checked=1 failed=0" in res.stdout


def test_seeded_case_passed_is_unhealthy_inversion():
    result_path = str(FIXTURES_DIR / "case-passed.json")
    res = run_tool("--result", result_path, "--summary")
    assert res.returncode == 2
    assert "FAIL seeded_defect checked=1 failed=1" in res.stdout
    assert "SIG-18" in res.stderr
    assert "PASSED — the contract stopped discriminating" in res.stderr


def test_no_case_errors():
    result_path = str(FIXTURES_DIR / "no-case.json")
    res = run_tool("--result", result_path, "--summary")
    assert res.returncode == 3
    assert "ERROR seeded_defect checked=0 failed=0" in res.stdout
    assert "declares no seeded cases" in res.stderr


def test_missing_file_errors():
    result_path = str(FIXTURES_DIR / "missing.json")
    res = run_tool("--result", result_path, "--summary")
    assert res.returncode == 3
    assert "ERROR seeded_defect checked=0 failed=0" in res.stdout
    assert "result file not found" in res.stderr
