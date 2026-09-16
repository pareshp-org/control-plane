"""
Robustness/adverse-conditions integration tests for the validator CLI
(python -m validators.registry.cli).

Covers:
  1. Genuinely malformed registry YAML (bad indentation, unbalanced flow
     braces, stray tabs) — the CLI must report a parse-error finding and
     exit 1, never an uncaught Python traceback.
  2. A completely empty registries/ directory — data-dependent rules
     (R01, R08) must handle it without crashing.
  3. --root pointing to a nonexistent path — the CLI must exit 2 per the
     documented input-error contract (cli.py: "Exit codes: 0=pass, 1=fail,
     2=input-error").
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[2]


def run_rule(rule_id, tmp_root, records_root=None):
    """Run a single rule via the CLI subprocess. Mirrors
    tests/integration/test_rules_extended.py's run_rule() helper."""
    args = [sys.executable, "-m", "validators.registry.cli",
            "--root", str(tmp_root),
            "--as-of", "2026-09-09",
            "--records-root", str(records_root or tmp_root),
            "--format", "json",
            "--rule", rule_id]
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT))
    out = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, out, result.stderr


def run_all(tmp_root, records_root=None, fmt="json"):
    """Run the full rule suite (no --rule) via the CLI subprocess."""
    args = [sys.executable, "-m", "validators.registry.cli",
            "--root", str(tmp_root),
            "--as-of", "2026-09-09",
            "--records-root", str(records_root or tmp_root),
            "--format", fmt]
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT))
    if fmt == "json" and result.stdout.strip():
        out = json.loads(result.stdout)
    else:
        out = {}
    return result.returncode, out, result.stdout, result.stderr


def assert_no_traceback(stderr, stdout=""):
    combined = (stderr or "") + (stdout or "")
    assert "Traceback (most recent call last)" not in combined, (
        f"CLI produced an uncaught Python traceback:\n{combined}"
    )


class TestMalformedYaml:
    """A registry YAML file with genuinely malformed syntax must be reported
    as a clean parse-error finding, not crash the process."""

    def _write_malformed(self, base, filename, content):
        people_dir = base / "registries" / "people"
        people_dir.mkdir(parents=True, exist_ok=True)
        (people_dir / "_canary.yaml").write_text("_canary: __CANARY__\n")
        (people_dir / filename).write_text(content, encoding="utf-8")

    def test_bad_indentation_full_run_exits_1_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            # Bad indentation: an unindented mapping key nested under a
            # quoted scalar that was never closed — invalid YAML syntax.
            self._write_malformed(
                base, "bad.yaml",
                'id: alice\n'
                '  name: "unterminated\n'
                '    role: [unbalanced\n',
            )
            code, out, err = 0, {}, ""
            proc_code, out, stdout, stderr = run_all(base, base)
            assert_no_traceback(stderr, stdout)
            assert proc_code == 1, f"expected exit 1, got {proc_code}; stdout={stdout} stderr={stderr}"
            assert out.get("status") == "FAIL"
            findings = out.get("findings", [])
            assert any("parse error" in f.lower() or "error" in f.lower() for f in findings), findings
            # At minimum R01/R08 (which directly scan people/*.yaml) must
            # surface a parse-error finding rather than silently skipping.
            assert any(f.startswith("R01:") and ("parse error" in f) for f in findings), findings
            assert any(f.startswith("R08:") and ("parse error" in f.lower() or "error" in f.lower()) for f in findings), findings

    def test_unbalanced_flow_braces_single_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._write_malformed(
                base, "bad_braces.yaml",
                'id: alice\n'
                'name: {a: 1, b: 2\n'
                'role: founder\n',
            )
            code, out, stderr = run_rule("R08", base)
            assert_no_traceback(stderr)
            assert code == 1, f"expected exit 1, got {code}; out={out} stderr={stderr}"
            findings = out.get("findings", [])
            assert any("parse error" in f.lower() for f in findings), findings

    def test_stray_tab_indentation_single_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            # Tabs are illegal for YAML indentation.
            self._write_malformed(base, "bad_tab.yaml", "id: alice\n\tname: Alice\n")
            code, out, stderr = run_rule("R01", base)
            assert_no_traceback(stderr)
            assert code == 1, f"expected exit 1, got {code}; out={out} stderr={stderr}"
            findings = out.get("findings", [])
            assert any("parse error" in f.lower() for f in findings), findings

    def test_malformed_yaml_across_full_rule_suite_no_crash(self):
        """Run every rule (not just R01/R08) against a malformed file and
        confirm none of them crash with an uncaught exception."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for subdir, fname in [
                ("people", "bad.yaml"),
                ("roles", "bad.yaml"),
                ("capabilities", "bad.yaml"),
                ("platform", "bad.yaml"),
                ("exceptions", "bad.yaml"),
                ("policies", "bad.yaml"),
            ]:
                d = base / "registries" / subdir
                d.mkdir(parents=True, exist_ok=True)
                (d / fname).write_text('a: {unbalanced\n  b: [also unbalanced\n', encoding="utf-8")
            (base / "registries" / "people" / "_canary.yaml").write_text("_canary: __CANARY__\n")
            (base / "commitments").mkdir(parents=True, exist_ok=True)
            (base / "commitments" / "bad.yaml").write_text('a: {unbalanced\n', encoding="utf-8")

            proc_code, out, stdout, stderr = run_all(base, base)
            assert_no_traceback(stderr, stdout)
            # Must be a clean pass/fail exit code (0 or 1), never the
            # top-level exception handler's exit 2.
            assert proc_code in (0, 1), f"expected 0 or 1, got {proc_code}; stdout={stdout} stderr={stderr}"
            assert out.get("status") in ("PASS", "FAIL")


class TestEmptyRegistriesDirectory:
    """A completely empty registries/ directory must not crash rules that
    depend on registry data (R01, R08 in particular)."""

    def test_r01_handles_empty_registries_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries").mkdir(parents=True)
            code, out, stderr = run_rule("R01", base)
            assert_no_traceback(stderr)
            assert code == 0
            assert out.get("status") == "PASS"
            assert out.get("findings", []) == []

    def test_r08_handles_empty_registries_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries").mkdir(parents=True)
            code, out, stderr = run_rule("R08", base)
            assert_no_traceback(stderr)
            assert code == 0
            assert out.get("status") == "PASS"
            assert out.get("findings", []) == []

    def test_r01_handles_missing_registries_dir_entirely(self):
        """No registries/ directory at all (but --root itself exists)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            code, out, stderr = run_rule("R01", base)
            assert_no_traceback(stderr)
            assert code == 0

    def test_r08_handles_missing_registries_dir_entirely(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            code, out, stderr = run_rule("R08", base)
            assert_no_traceback(stderr)
            assert code == 0

    def test_full_run_against_empty_registries_dir_no_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "registries").mkdir(parents=True)
            proc_code, out, stdout, stderr = run_all(base, base)
            assert_no_traceback(stderr, stdout)
            assert proc_code in (0, 1)
            assert out.get("status") in ("PASS", "FAIL")


class TestNonexistentRoot:
    """--root pointing to a path that does not exist on disk must be
    treated as an input error (exit 2), per cli.py's documented contract:
    'Exit codes: 0=pass, 1=fail, 2=input-error'."""

    def test_nonexistent_root_exits_2_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            bogus = base / "does" / "not" / "exist"
            assert not bogus.exists()
            proc_code, out, stdout, stderr = run_all(bogus, bogus, fmt="json")
            assert_no_traceback(stderr, stdout)
            assert proc_code == 2, f"expected exit 2 (input-error), got {proc_code}; stdout={stdout} stderr={stderr}"
            assert out.get("status") == "ERROR"
            assert "error" in out

    def test_nonexistent_root_exits_2_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            bogus = base / "missing"
            proc_code, out, stdout, stderr = run_all(bogus, bogus, fmt="text")
            assert_no_traceback(stderr, stdout)
            assert proc_code == 2, f"expected exit 2 (input-error), got {proc_code}; stdout={stdout} stderr={stderr}"
            assert "ERROR" in stdout

    def test_nonexistent_root_single_rule_also_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            bogus = base / "ghost"
            code, out, stderr = run_rule("R01", bogus)
            assert_no_traceback(stderr)
            assert code == 2, f"expected exit 2 (input-error), got {code}; out={out} stderr={stderr}"

    def test_root_is_a_file_not_a_directory_exits_2(self):
        """--root pointing at an existing file (not a directory) is also
        an input error, not a crash."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            a_file = base / "im_a_file.txt"
            a_file.write_text("not a directory")
            proc_code, out, stdout, stderr = run_all(a_file, a_file, fmt="json")
            assert_no_traceback(stderr, stdout)
            assert proc_code == 2, f"expected exit 2, got {proc_code}; stdout={stdout} stderr={stderr}"
