"""Extended integration tests for validator rules R02, R05-R07, R09-R10, R12-R15, R17-R18."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
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


class TestR02RoleReferenceValid:
    def test_pass_role_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/roles/founder.yaml", {"id": "founder-integrator"})
            write_yaml(base / "registries/people/alice.yaml",
                       {"id": "alice", "name": "Alice", "role": "founder-integrator", "lane_assignments": ["L0"]})
            (base / "registries/people/_canary.yaml").write_text("_canary: __CANARY__\n")
            code, out = run_rule("R02", base)
            assert code == 0

    def test_fail_role_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries/roles").mkdir(parents=True)
            write_yaml(base / "registries/people/alice.yaml",
                       {"id": "alice", "name": "Alice", "role": "nonexistent-role", "lane_assignments": ["L0"]})
            (base / "registries/people/_canary.yaml").write_text("_canary: __CANARY__\n")
            code, out = run_rule("R02", base)
            assert code == 1
            assert any("nonexistent-role" in f for f in out.get("findings", []))


class TestR05CapabilityOwnerLaneValid:
    def test_pass_valid_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/capabilities/CAP-0001.yaml",
                       {"id": "CAP-0001", "name": "test", "owner_lane": "L1"})
            code, out = run_rule("R05", base)
            assert code == 0

    def test_fail_invalid_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/capabilities/CAP-0001.yaml",
                       {"id": "CAP-0001", "name": "test", "owner_lane": "L99"})
            code, out = run_rule("R05", base)
            assert code == 1
            assert any("L99" in f for f in out.get("findings", []))


class TestR06PlatformTypeValid:
    def test_pass_valid_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/platform/cp.yaml",
                       {"id": "cp", "name": "control-plane", "type": "service"})
            code, out = run_rule("R06", base)
            assert code == 0

    def test_fail_invalid_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/platform/cp.yaml",
                       {"id": "cp", "name": "control-plane", "type": "unknown-type"})
            code, out = run_rule("R06", base)
            assert code == 1
            assert any("unknown-type" in f for f in out.get("findings", []))


class TestR07ExceptionExpiryFuture:
    def test_pass_future_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/exceptions/exc-001.yaml",
                       {"id": "exc-001", "status": "active", "expires": "2030-01-01", "granted_by": "bendrohit-eng"})
            code, out = run_rule("R07", base)
            assert code == 0

    def test_fail_past_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/exceptions/exc-001.yaml",
                       {"id": "exc-001", "status": "active", "expires": "2020-01-01", "granted_by": "bendrohit-eng"})
            code, out = run_rule("R07", base)
            assert code == 1
            assert any("R07" in f for f in out.get("findings", []))


class TestR09NoDuplicateCapabilities:
    def test_pass_unique_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/capabilities/CAP-0001.yaml",
                       {"id": "CAP-0001", "name": "alpha"})
            write_yaml(base / "registries/capabilities/CAP-0002.yaml",
                       {"id": "CAP-0002", "name": "beta"})
            code, out = run_rule("R09", base)
            assert code == 0

    def test_fail_duplicate_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/capabilities/CAP-0001.yaml",
                       {"id": "CAP-0001", "name": "alpha"})
            write_yaml(base / "registries/capabilities/CAP-0002.yaml",
                       {"id": "CAP-0002", "name": "alpha"})
            code, out = run_rule("R09", base)
            assert code == 1
            assert any("alpha" in f for f in out.get("findings", []))


class TestR10PolicyEnforcedByValid:
    def test_pass_valid_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/policies/pol-001.yaml",
                       {"id": "POL-001", "enforced_by": "L0"})
            code, out = run_rule("R10", base)
            assert code == 0

    def test_pass_valid_person(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries/people").mkdir(parents=True, exist_ok=True)
            (base / "registries/people/_canary.yaml").write_text("_canary: __CANARY__\n")
            write_yaml(base / "registries/people/alice.yaml",
                       {"id": "alice", "name": "Alice", "role": "founder", "lane_assignments": ["L0"]})
            write_yaml(base / "registries/policies/pol-001.yaml",
                       {"id": "POL-001", "enforced_by": "alice"})
            code, out = run_rule("R10", base)
            assert code == 0


class TestR12CommitmentOwnerExists:
    def test_pass_owner_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries/people").mkdir(parents=True, exist_ok=True)
            (base / "registries/people/_canary.yaml").write_text("_canary: __CANARY__\n")
            write_yaml(base / "registries/people/alice.yaml",
                       {"id": "alice", "name": "Alice", "role": "founder", "lane_assignments": ["L0"]})
            write_yaml(base / "commitments/com-001.yaml",
                       {"id": "com-001", "owner": "alice"})
            code, out = run_rule("R12", base)
            assert code == 0

    def test_fail_owner_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries/people").mkdir(parents=True, exist_ok=True)
            (base / "registries/people/_canary.yaml").write_text("_canary: __CANARY__\n")
            write_yaml(base / "registries/people/alice.yaml",
                       {"id": "alice", "name": "Alice", "role": "founder", "lane_assignments": ["L0"]})
            write_yaml(base / "commitments/com-001.yaml",
                       {"id": "com-001", "owner": "ghost-person"})
            code, out = run_rule("R12", base)
            assert code == 1
            assert any("ghost-person" in f for f in out.get("findings", []))


class TestR13NoEmptyRegistries:
    def test_warn_but_pass_on_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries/empty-dir").mkdir(parents=True)
            code, out = run_rule("R13", base)
            # R13 always returns pass (warnings only)
            assert code == 0
            assert any("R13 WARN" in f for f in out.get("findings", []))


class TestR15RoleIdUniqueness:
    def test_pass_unique_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/roles/role-a.yaml", {"id": "role-a", "name": "Role A"})
            write_yaml(base / "registries/roles/role-b.yaml", {"id": "role-b", "name": "Role B"})
            code, out = run_rule("R15", base)
            assert code == 0

    def test_fail_duplicate_role_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/roles/role-a.yaml", {"id": "role-dup", "name": "Role A"})
            write_yaml(base / "registries/roles/role-b.yaml", {"id": "role-dup", "name": "Role B"})
            code, out = run_rule("R15", base)
            assert code == 1
            assert any("role-dup" in f for f in out.get("findings", []))


class TestR17PlatformIdUniqueness:
    def test_pass_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/platform/p1.yaml", {"id": "plat-1"})
            write_yaml(base / "registries/platform/p2.yaml", {"id": "plat-2"})
            code, out = run_rule("R17", base)
            assert code == 0

    def test_fail_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/platform/p1.yaml", {"id": "plat-dup"})
            write_yaml(base / "registries/platform/p2.yaml", {"id": "plat-dup"})
            code, out = run_rule("R17", base)
            assert code == 1
            assert any("plat-dup" in f for f in out.get("findings", []))


class TestR18ExceptionGrantedByAuthorized:
    def test_pass_authorized_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/exceptions/exc-001.yaml",
                       {"id": "exc-001", "granted_by": "bendrohit-eng"})
            code, out = run_rule("R18", base)
            assert code == 0

    def test_fail_unauthorized_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "registries/exceptions/exc-001.yaml",
                       {"id": "exc-001", "granted_by": "unknown-actor"})
            code, out = run_rule("R18", base)
            assert code == 1
            assert any("unknown-actor" in f for f in out.get("findings", []))
