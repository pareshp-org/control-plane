"""
Integration test: L1 validator CLI (Option B, FD-094)
Tests that the validator CLI accepts correct input and rejects bad input.
Run: python -m pytest tests/integration/test_validator.py -v
"""
import subprocess
import sys
from pathlib import Path

IMPL_ROOT = Path(__file__).parent.parent.parent

def run_validator(*args):
    cmd = [sys.executable, "-m", "validators.registry.cli"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(IMPL_ROOT))

def test_validator_full_run_passes():
    """Full 18-rule validator (R01-R18) should exit 0 (pass) against the live registry"""
    result = run_validator(
        "--root", "registries/",
        "--as-of", "2026-09-09",
        "--records-root", "records/",
        "--format", "json"
    )
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stderr}"

def test_validator_json_output():
    """Validator should output valid JSON when --format json"""
    import json
    result = run_validator(
        "--root", "registries/",
        "--as-of", "2026-09-09",
        "--format", "json"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "status" in data

def test_validator_missing_root_fails():
    """Validator should exit 2 when required --root is missing"""
    result = run_validator("--as-of", "2026-09-09", "--format", "json")
    # argparse exits 2 on missing required args
    assert result.returncode == 2
