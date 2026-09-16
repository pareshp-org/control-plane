"""Integration tests for individual validator rules R01-R18."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[2]


def run_rule(rule_id, tmp_root):
    """Run validator CLI for a single rule against tmp_root."""
    result = subprocess.run(
        [sys.executable, "-m", "validators.registry.cli",
         "--root", str(tmp_root),
         "--as-of", "2026-09-09",
         "--records-root", str(tmp_root),
         "--format", "json",
         "--rule", rule_id],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return result.returncode, json.loads(result.stdout) if result.stdout.strip() else {}


def make_people_dir(base, entries):
    p = base / "registries" / "people"
    p.mkdir(parents=True, exist_ok=True)
    (p / "_canary.yaml").write_text("_canary: __CANARY__\n")
    for name, data in entries.items():
        (p / f"{name}.yaml").write_text(yaml.dump(data))
    return p


def make_roles_dir(base, entries):
    p = base / "registries" / "roles"
    p.mkdir(parents=True, exist_ok=True)
    for name, data in entries.items():
        (p / f"{name}.yaml").write_text(yaml.dump(data))
    return p


def make_capabilities_dir(base, entries):
    p = base / "registries" / "capabilities"
    p.mkdir(parents=True, exist_ok=True)
    for name, data in entries.items():
        (p / f"{name}.yaml").write_text(yaml.dump(data))
    return p


class TestR01PeopleIdUniqueness:
    def test_pass_unique_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"]},
                "bob": {"id": "bob", "name": "Bob", "role": "lane-owner", "lane_assignments": ["L1"]},
            })
            code, out = run_rule("R01", base)
            assert code == 0
            assert out["status"] == "PASS"

    def test_fail_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"]},
                "alice2": {"id": "alice", "name": "Alice Clone", "role": "founder-integrator", "lane_assignments": ["L0"]},
            })
            code, out = run_rule("R01", base)
            assert code == 1
            assert any("R01" in f for f in out.get("findings", []))


class TestR03LaneAssignmentValid:
    def test_pass_valid_lanes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0", "L1"]},
            })
            code, out = run_rule("R03", base)
            assert code == 0

    def test_fail_invalid_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0", "L99"]},
            })
            code, out = run_rule("R03", base)
            assert code == 1
            assert any("L99" in f for f in out.get("findings", []))


class TestR04CapabilityIdFormat:
    def test_pass_valid_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_capabilities_dir(base, {
                "CAP-0001": {"id": "CAP-0001", "name": "test-cap", "owner_lane": "L0"},
            })
            code, out = run_rule("R04", base)
            assert code == 0

    def test_fail_invalid_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_capabilities_dir(base, {
                "bad-cap": {"id": "BAD-001", "name": "bad-cap", "owner_lane": "L0"},
            })
            code, out = run_rule("R04", base)
            assert code == 1
            assert any("R04" in f for f in out.get("findings", []))


class TestR08PeopleRequiredFields:
    def test_pass_all_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"]},
            })
            code, out = run_rule("R08", base)
            assert code == 0

    def test_fail_missing_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "role": "founder-integrator", "lane_assignments": ["L0"]},
            })
            code, out = run_rule("R08", base)
            assert code == 1
            assert any("name" in f.lower() for f in out.get("findings", []))


class TestR11CanaryIntact:
    def test_pass_canary_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            canary_dir = base / "registries" / "people"
            canary_dir.mkdir(parents=True)
            (canary_dir / "_canary.yaml").write_text("_canary: __CANARY__\n")
            code, out = run_rule("R11", base)
            assert code == 0

    def test_fail_canary_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries" / "people").mkdir(parents=True)
            code, out = run_rule("R11", base)
            assert code == 1

    def test_fail_canary_corrupted(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            canary_dir = base / "registries" / "people"
            canary_dir.mkdir(parents=True)
            (canary_dir / "_canary.yaml").write_text("_canary: WRONG_VALUE\n")
            code, out = run_rule("R11", base)
            assert code == 1


class TestR16FteRangeValid:
    def test_pass_valid_fte(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"], "fte": 1.0},
            })
            code, out = run_rule("R16", base)
            assert code == 0

    def test_fail_fte_above_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"], "fte": 1.5},
            })
            code, out = run_rule("R16", base)
            assert code == 1
            assert any("R16" in f for f in out.get("findings", []))

    def test_fail_fte_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_people_dir(base, {
                "alice": {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"], "fte": -0.1},
            })
            code, out = run_rule("R16", base)
            assert code == 1
