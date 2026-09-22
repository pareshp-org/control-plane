"""Unit tests for L2-T546: verification_contract_check."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = REPO_ROOT / "tools" / "evidence" / "fixtures" / "vc"


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "tools.evidence.verification_contract_check", *args]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_complete_contract_passes():
    contract = str(FIXTURES_DIR / "complete.yaml")
    res = run_tool("--contract", contract, "--criticality", "critical", "--summary")
    assert res.returncode == 0
    assert "OK verification_contract_check checked=4 failed=0" in res.stdout


def test_no_perf_critical_fails_on_critical():
    contract = str(FIXTURES_DIR / "no-perf-critical.yaml")
    res = run_tool("--contract", contract, "--criticality", "critical", "--summary")
    assert res.returncode == 2
    assert "FAIL verification_contract_check checked=4 failed=1" in res.stdout
    assert "no performance_mechanism is declared" in res.stderr


def test_no_perf_critical_passes_on_low():
    contract = str(FIXTURES_DIR / "no-perf-critical.yaml")
    res = run_tool("--contract", contract, "--criticality", "low", "--summary")
    assert res.returncode == 0
    assert "OK verification_contract_check checked=4 failed=0" in res.stdout


def test_no_coverage_fails():
    contract = str(FIXTURES_DIR / "no-coverage.yaml")
    res = run_tool("--contract", contract, "--criticality", "low", "--summary")
    assert res.returncode == 2
    assert "FAIL verification_contract_check checked=4 failed=1" in res.stdout
    assert "no coverage_map declared" in res.stderr


def test_no_seeded_fails():
    contract = str(FIXTURES_DIR / "no-seeded.yaml")
    res = run_tool("--contract", contract, "--criticality", "low", "--summary")
    assert res.returncode == 2
    assert "FAIL verification_contract_check checked=4 failed=1" in res.stdout
    assert "no seeded_defect_cases or seeded_defect_case declared" in res.stderr


def test_missing_contract_errors():
    contract = str(FIXTURES_DIR / "nonexistent.yaml")
    res = run_tool("--contract", contract, "--criticality", "low", "--summary")
    assert res.returncode == 3
    assert "ERROR verification_contract_check checked=0 failed=0" in res.stdout
    assert "contract file not found" in res.stderr
