"""
Dedicated integration tests for the R01/R08 fallback-directory fix.

Bug class: R01 (r01_people_id_uniqueness.py) and R08
(r08_people_required_fields.py) look for the people registry at two known
layouts — `<root>/registries/people` and `<root>/people`. The buggy version
of this code additionally fell back to treating `<root>` itself as a valid
"found" candidate whenever neither known layout existed, because `<root>`
always exists (it's the directory being validated). That made the "not
found" branch dead code and caused the rule to silently perform a
non-recursive glob of the *entire registry root* for `*.yaml` files —
misvalidating whatever stray/unrelated yaml files happened to sit directly
at the root as if they were person records, and producing a spurious wrong
result (bogus duplicate-id or missing-required-field findings, or a false
clean pass) instead of correctly reporting "no people registry found".

This is a different bug class from the R02/R10/R12/R14 short-circuit fix
(which is about early-return short-circuiting elsewhere in the registry
validators, already covered in other dedicated test files this session).

The fix: neither known layout found => return (True, []) immediately,
without ever touching registry_root's own top-level files.

These tests plant a people directory at a WRONG nested path (neither
registries/people nor people) alongside stray top-level yaml files at
registry_root that WOULD have produced spurious findings under the old
bare-root-fallback bug, and assert R01 and R08 both cleanly return
(True, []) — i.e. they never scan registry_root itself.
"""
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


def _plant_wrong_path_people_dir_and_spurious_root_files(base):
    """Shared fixture layout used by the regression tests below.

    - A people directory nested at a WRONG path: base/misc/nested/people/
      (neither base/registries/people nor base/people). Neither R01 nor
      R08 should ever discover or scan this directory (it's simply the
      wrong location) — it exists only to make the scenario realistic
      ("someone misconfigured the layout"), not because the rules do any
      recursive/deep search for it.
    - Two yaml files sitting directly at base/ (the registry root) that
      share the same "id" and are each missing required people fields.
      Under the old bare-root-fallback bug, a non-recursive glob of
      base/*.yaml would have picked these up and misvalidated them as
      person records: R01 would report a spurious duplicate-id finding,
      and R08 would report spurious missing-required-field findings.
    """
    # People registry nested at the WRONG path — must never be found.
    write_yaml(base / "misc" / "nested" / "people" / "real.yaml",
               {"id": "real-person", "name": "Real Person",
                "role": "role-a", "lane_assignments": ["l1"]})

    # Stray files directly at registry_root — must never be scanned.
    write_yaml(base / "dup1.yaml", {"id": "clash", "name": "One"})
    write_yaml(base / "dup2.yaml", {"id": "clash", "name": "Two"})


class TestR01FallbackDirectoryFix:
    def test_wrong_path_people_dir_returns_clean_pass_r01(self):
        # Regression: without the fix, R01 would fall back to scanning
        # registry_root/*.yaml and report a duplicate id "clash" between
        # dup1.yaml and dup2.yaml. With the fix, neither known people
        # layout exists, so R01 must return (True, []) untouched.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _plant_wrong_path_people_dir_and_spurious_root_files(base)

            code, out = run_rule("R01", base)
            assert code == 0
            assert out.get("status") == "PASS"
            assert out.get("findings", []) == []
            # Explicitly assert the spurious result never appears.
            assert not any("clash" in f for f in out.get("findings", []))

    def test_wrong_path_alone_still_clean_pass_r01(self):
        # Sanity control: even with no stray root files at all, a
        # wrong-path people dir alone must be a clean, empty pass.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "misc" / "nested" / "people" / "real.yaml",
                       {"id": "real-person", "name": "Real Person",
                        "role": "role-a", "lane_assignments": ["l1"]})

            code, out = run_rule("R01", base)
            assert code == 0
            assert out.get("findings", []) == []


class TestR08FallbackDirectoryFix:
    def test_wrong_path_people_dir_returns_clean_pass_r08(self):
        # Regression: without the fix, R08 would fall back to scanning
        # registry_root/*.yaml and report missing required fields (role,
        # lane_assignments) for dup1.yaml and dup2.yaml. With the fix,
        # neither known people layout exists, so R08 must return
        # (True, []) untouched.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _plant_wrong_path_people_dir_and_spurious_root_files(base)

            code, out = run_rule("R08", base)
            assert code == 0
            assert out.get("status") == "PASS"
            assert out.get("findings", []) == []
            # Explicitly assert the spurious results never appear.
            assert not any("dup1.yaml" in f or "dup2.yaml" in f
                            for f in out.get("findings", []))

    def test_wrong_path_alone_still_clean_pass_r08(self):
        # Sanity control: even with no stray root files at all, a
        # wrong-path people dir alone must be a clean, empty pass.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_yaml(base / "misc" / "nested" / "people" / "real.yaml",
                       {"id": "real-person", "name": "Real Person",
                        "role": "role-a", "lane_assignments": ["l1"]})

            code, out = run_rule("R08", base)
            assert code == 0
            assert out.get("findings", []) == []


class TestR01R08BothCleanOnWrongPath:
    def test_both_rules_return_true_empty_together(self):
        """The specific regression this fix prevents, exercised for both
        rules against the same on-disk layout in one assertion: a people
        directory nested at a WRONG path must make BOTH R01 and R08
        return (True, []) rather than silently scanning registry_root and
        surfacing a spurious/wrong result from the stray top-level files.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _plant_wrong_path_people_dir_and_spurious_root_files(base)

            code_r01, out_r01 = run_rule("R01", base)
            code_r08, out_r08 = run_rule("R08", base)

            assert (code_r01, out_r01.get("findings", [])) == (0, [])
            assert (code_r08, out_r08.get("findings", [])) == (0, [])
