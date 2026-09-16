"""
Integration test: registry canary sentinel (FD-106/PFD-026)
Tests that the canary sentinel is intact and detectable.
"""
import subprocess
from pathlib import Path

IMPL_ROOT = Path(__file__).parent.parent.parent
CANARY_FILE = IMPL_ROOT / "registries" / "people" / "_canary.yaml"

def test_canary_file_exists():
    assert CANARY_FILE.exists(), f"Canary file missing: {CANARY_FILE}"

def test_canary_sentinel_present():
    content = CANARY_FILE.read_text()
    assert "__CANARY__" in content, "Canary sentinel __CANARY__ not found"

def test_canary_check_script_passes():
    result = subprocess.run(
        ["bash", "scripts/canary-check.sh", "registries/people/_canary.yaml"],
        capture_output=True, text=True, cwd=str(IMPL_ROOT)
    )
    assert result.returncode == 0, f"canary-check.sh failed: {result.stdout}{result.stderr}"
