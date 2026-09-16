"""
R08 — People Required Fields
Every person record must have: id, name, role, lane_assignments
FD-094, L1-03, Option B
Exit: 0=pass, 1=fail, 2=input-error
"""
from pathlib import Path

REQUIRED = ["id", "name", "role", "lane_assignments"]

def check(registry_root, as_of, records_root=None):
    """Returns (passed: bool, findings: list[str])"""
    findings = []
    root = Path(registry_root)

    # Find people registry — try known layouts only. No bare-root fallback:
    # root always exists (it's the directory being validated), so treating
    # it as a valid "found" candidate made the "not found" branch dead code
    # and let the rule silently scan the wrong directory (a non-recursive
    # glob of the whole registry root), masking real misconfigurations by
    # returning a false clean pass. If neither known layout is found, there
    # is nothing to check — mirrors R02's roles_dir_found convention (and
    # matches this repo's established "missing/empty registry = no data to
    # validate" contract, see
    # tests/integration/test_robustness.py::TestEmptyRegistriesDirectory).
    registry_dir = None
    for candidate in [root / "registries" / "people", root / "people"]:
        if candidate.exists():
            registry_dir = candidate
            break

    if registry_dir is None:
        return True, []

    try:
        import yaml
    except ImportError:
        return True, ["R08: pyyaml not installed — skipping (install: pip install pyyaml)"]

    person_files = list(registry_dir.glob("*.yaml")) + list(registry_dir.glob("*.yml"))
    person_files = [f for f in person_files if not f.name.startswith("_")]

    if not person_files:
        return True, []  # empty registry is OK (R13 handles emptiness warning)

    for person_file in person_files:
        try:
            data = yaml.safe_load(person_file.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(f"R08: {person_file.name} — YAML parse error: {e}")
            continue

        if not isinstance(data, dict):
            findings.append(f"R08: {person_file.name} — not a mapping")
            continue

        for field in REQUIRED:
            if field not in data:
                findings.append(f"R08: {person_file.name} — missing required field '{field}'")

    passed = len(findings) == 0
    return passed, findings
