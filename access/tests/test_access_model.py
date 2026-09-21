"""access/tests/test_access_model.py

Schema/structural test suite for L5-T12 (access-model validator, spec 11,
40, 64, 90). For each of the seven stems declared in
access/schema/access-model.schema.json: one positive test asserting the
shipped file validates via `access/tools/validate_access_model.py`, and one
negative test that copies the file to a temp path, deletes one required
top-level key, and asserts the validator exits 1. 14 tests total.
"""
import json
import os
import subprocess
import sys

import pytest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI = os.path.join(REPO_ROOT, "access", "tools", "validate_access_model.py")
SCHEMA_PATH = os.path.join(REPO_ROOT, "access", "schema", "access-model.schema.json")

# Mirrors access/tools/validate_access_model.py's STEM_FILES. Kept as a
# separate literal (rather than imported) so this suite exercises the CLI
# exactly as a caller would, the same way access/tests/test_machine_identity.py
# and access/tests/test_pi_gate.py exercise their CLIs by subprocess.
STEM_FILES = {
    "github-permissions": os.path.join("access", "model", "permission-semantics.yaml"),
    "permission-model": os.path.join("access", "model", "teams.yaml"),
    "branch-protection": os.path.join("access", "branch-protection", "branch-protection.yaml"),
    "secret-tiers": os.path.join("access", "published", "secret-tiers.v1.json"),
    "permission-matrix": os.path.join("access", "model", "permission-matrix.yaml"),
    "fail-closed": os.path.join("access", "fail-closed", "classification-register.yaml"),
    "safe-defaults": os.path.join("access", "model", "safe-defaults.yaml"),
}

STEM_ORDER = tuple(STEM_FILES)


def _run(*args):
    return subprocess.run(
        [sys.executable, CLI] + list(args),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _load(path):
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".json"):
            return json.load(handle)
        return yaml.safe_load(handle)


def _dump(doc, path):
    with open(path, "w", encoding="utf-8") as handle:
        if path.endswith(".json"):
            json.dump(doc, handle)
        else:
            yaml.safe_dump(doc, handle)


def _required_keys(stem):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as handle:
        schema_document = json.load(handle)
    return schema_document[stem]["required"]


@pytest.mark.parametrize("stem", STEM_ORDER)
def test_shipped_file_validates(stem):
    """Positive case: the committed file for this stem validates cleanly."""
    result = _run("--only", stem)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ACCESS MODEL OK: 1 file(s)" in result.stdout


@pytest.mark.parametrize("stem", STEM_ORDER)
def test_missing_required_key_fails(stem, tmp_path):
    """Negative case: copy the committed file to a temp path, delete one
    required top-level key, and assert the validator exits 1.

    Also covers acceptance criterion 4 (a missing model file causes exit 1,
    fail-closed per spec 64.2 row 1) for this stem, proven here rather than
    asserted in prose: pointing --path at a file that does not exist at all
    must exit 1 with the same failure format.
    """
    real_path = os.path.join(REPO_ROOT, STEM_FILES[stem])
    doc = _load(real_path)

    victim_key = _required_keys(stem)[0]
    assert victim_key in doc, "expected required key %r in %s" % (victim_key, real_path)
    del doc[victim_key]

    suffix = ".json" if real_path.endswith(".json") else ".yaml"
    mutated_path = tmp_path / ("mutated-%s%s" % (stem, suffix))
    _dump(doc, str(mutated_path))

    result = _run("--only", stem, "--path", str(mutated_path))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "ACCESS MODEL FAIL" in result.stdout

    missing_path = tmp_path / ("does-not-exist-%s%s" % (stem, suffix))
    missing_result = _run("--only", stem, "--path", str(missing_path))
    assert missing_result.returncode == 1, missing_result.stdout + missing_result.stderr
    assert "ACCESS MODEL FAIL" in missing_result.stdout
    assert "file not found" in missing_result.stdout
