"""Dedicated integration tests for validator rule R14 (Schema Version Match)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]


def run_rule(rule_id, tmp_root, records_root=None):
    args = [sys.executable, "-m", "validators.registry.cli",
            "--root", str(tmp_root),
            "--as-of", "2026-09-09",
            "--records-root", str(records_root or tmp_root),
            "--format", "json",
            "--rule", rule_id]
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT))
    out = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, out


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


class TestR14SchemaVersionMatch:
    def test_pass_known_schema_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_json(base / "schemas/registry/roles.v1.schema.json",
                       {"$id": "urn:multiproduct:schemas:registry:roles:v1"})
            write_yaml(base / "registries/roles/role-a.yaml",
                       {"id": "role-a", "name": "Role A",
                        "$schema": "urn:multiproduct:schemas:registry:roles:v1"})
            code, out = run_rule("R14", base)
            assert code == 0

    def test_fail_unknown_schema_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_json(base / "schemas/registry/roles.v1.schema.json",
                       {"$id": "urn:multiproduct:schemas:registry:roles:v1"})
            write_yaml(base / "registries/roles/role-a.yaml",
                       {"id": "role-a", "name": "Role A",
                        "$schema": "urn:bogus:schema:not-real:v99"})
            code, out = run_rule("R14", base)
            assert code == 1
            assert any("urn:bogus:schema:not-real:v99" in f for f in out.get("findings", []))

    def test_fail_when_schemas_dir_present_but_empty(self):
        # Regression test: a schemas/ directory that EXISTS but contains no
        # discoverable $id values must NOT fall back to the hardcoded
        # catalogue (which would silently validate against stale data).
        # It must cause every $schema reference to fail, matching the
        # already-fixed R02 pattern of separating "directory found" from
        # "collected set is non-empty".
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "schemas").mkdir(parents=True)  # present, but empty
            write_yaml(base / "registries/roles/role-a.yaml",
                       {"id": "role-a", "name": "Role A",
                        # This $id IS in the hardcoded fallback catalogue; if the
                        # empty-but-present schemas/ dir incorrectly fell back to
                        # it, this would wrongly PASS.
                        "$schema": "urn:multiproduct:schemas:registry:roles:v1"})
            code, out = run_rule("R14", base)
            assert code == 1
            assert any("urn:multiproduct:schemas:registry:roles:v1" in f for f in out.get("findings", []))
