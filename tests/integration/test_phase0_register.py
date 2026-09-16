"""
Integration tests for the phase-0 contract register append helper.

Exercises scripts/phase0-lib/append_register.py -- a manually-synced mirror
of the run-phase-0.sh heredoc for task L0-P0-002 (see the header comment in
that file) -- against a scratch repo layout in tmp_path, without touching the
real contracts/ tree or invoking run-phase-0.sh itself.
"""
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

IMPL_ROOT = Path(__file__).parent.parent.parent
APPEND_REGISTER = IMPL_ROOT / "scripts" / "phase0-lib" / "append_register.py"


@pytest.fixture
def repo(tmp_path):
    """A scratch repo root with an initialised, empty contracts/register.yaml
    -- mirrors what L0-P0-002 does before append_register.py is ever called."""
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "register.yaml").write_text(
        yaml.dump({"contracts": []}, default_flow_style=False, sort_keys=False)
    )
    return tmp_path


def run_append(repo, *args):
    return subprocess.run(
        [sys.executable, str(APPEND_REGISTER), *args],
        capture_output=True, text=True, cwd=str(repo),
    )


def load_register(repo):
    return yaml.safe_load((repo / "contracts" / "register.yaml").read_text())


def test_append_register_script_exists():
    assert APPEND_REGISTER.exists(), f"mirror script missing: {APPEND_REGISTER}"


def test_registering_a_contract_creates_its_stub_file(repo):
    result = run_append(
        repo, "C-TEST-1", "contracts/foo.yaml", "1", "L1", "L1", "L2,L3", "stubs/c-test-1.yaml"
    )
    assert result.returncode == 0, result.stderr
    assert "appended: C-TEST-1" in result.stdout

    stub_path = repo / "contracts" / "stubs" / "c-test-1.yaml"
    assert stub_path.exists()
    stub_text = stub_path.read_text()
    assert "contract_id: C-TEST-1" in stub_text
    assert "registered_path: contracts/foo.yaml" in stub_text
    assert "stub: true" in stub_text

    data = load_register(repo)
    ids = [r["id"] for r in data["contracts"]]
    assert ids == ["C-TEST-1"]
    row = data["contracts"][0]
    assert row["consuming_lanes"] == ["L2", "L3"]
    assert row["version"] == 1
    assert row["stub"] == "stubs/c-test-1.yaml"


def test_reregistering_is_idempotent_and_skips(repo):
    first = run_append(
        repo, "C-TEST-2", "contracts/bar.yaml", "1", "L1", "L1", "L2", "stubs/c-test-2.yaml"
    )
    assert first.returncode == 0, first.stderr

    # Re-register the same id with different (would-be) values -- the
    # existing row must not change, and the call must be a no-op skip.
    second = run_append(
        repo, "C-TEST-2", "contracts/bar-v2.yaml", "9", "L9", "L9", "L9", "stubs/other.yaml"
    )
    assert second.returncode == 0, second.stderr
    assert "skip: C-TEST-2 already in register" in second.stdout

    data = load_register(repo)
    ids = [r["id"] for r in data["contracts"]]
    assert ids.count("C-TEST-2") == 1
    row = data["contracts"][0]
    assert row["path"] == "contracts/bar.yaml"
    assert row["version"] == 1

    # No stub was created for the (skipped) second call's stub path.
    assert not (repo / "contracts" / "stubs" / "other.yaml").exists()


def test_empty_stub_argument_is_a_noop(repo):
    result = run_append(
        repo, "C-TEST-3", "contracts/baz.yaml", "1", "L1", "L1", "L2", ""
    )
    assert result.returncode == 0, result.stderr
    assert "appended: C-TEST-3" in result.stdout

    data = load_register(repo)
    row = data["contracts"][0]
    assert row["id"] == "C-TEST-3"
    assert row["stub"] == ""

    # An empty stub must never trigger the file-creation branch -- not even
    # an empty stubs/ directory should appear.
    assert not (repo / "contracts" / "stubs").exists()


def test_existing_real_file_at_stub_path_is_never_overwritten(repo):
    stub_dir = repo / "contracts" / "stubs"
    stub_dir.mkdir(parents=True)
    real_stub = stub_dir / "c-test-4.yaml"
    real_content = "# real, hand-authored contract content\nkey: value\n"
    real_stub.write_text(real_content)

    result = run_append(
        repo, "C-TEST-4", "contracts/qux.yaml", "1", "L1", "L1", "L2", "stubs/c-test-4.yaml"
    )
    assert result.returncode == 0, result.stderr
    assert "appended: C-TEST-4" in result.stdout

    # The real file's content must be untouched -- the script only writes
    # the placeholder stub when the path does not already exist.
    assert real_stub.read_text() == real_content

    data = load_register(repo)
    row = data["contracts"][0]
    assert row["id"] == "C-TEST-4"
    assert row["stub"] == "stubs/c-test-4.yaml"
