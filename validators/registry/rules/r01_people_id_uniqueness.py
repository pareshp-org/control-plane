"""
R01 — People ID Uniqueness
Every person record must have a unique `id` field within the people registry.
FD-094, L1-03, Option B
"""
from pathlib import Path

def check(registry_root, as_of, records_root=None):
    findings = []
    registry_dir = Path(registry_root)

    # Find people registry — try known layouts only. No bare-root fallback:
    # registry_dir always exists (it's the directory being validated), so
    # treating it as a valid "found" candidate made the "not found" branch
    # dead code and let the rule silently scan the wrong directory (a
    # non-recursive glob of the whole registry root), masking real
    # misconfigurations by returning a false clean pass. If neither known
    # layout is found, there is nothing to check — mirrors R02's
    # roles_dir_found convention (and matches this repo's established
    # "missing/empty registry = no data to validate" contract, see
    # tests/integration/test_robustness.py::TestEmptyRegistriesDirectory).
    people_dir = None
    for candidate in [
        registry_dir / "registries" / "people",
        registry_dir / "people",
    ]:
        if candidate.exists():
            people_dir = candidate
            break

    if people_dir is None:
        return True, []

    try:
        import yaml
    except ImportError:
        return True, ["R01: pyyaml not installed — skipping"]

    seen_ids = {}
    for person_file in sorted(people_dir.glob("*.yaml")):
        if person_file.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(person_file.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(f"R01: {person_file.name} — parse error: {e}")
            continue

        if not isinstance(data, dict):
            continue
        person_id = data.get("id")
        if person_id is None:
            continue  # R08 handles missing id
        if person_id in seen_ids:
            findings.append(f"R01: duplicate id '{person_id}' in {person_file.name} and {seen_ids[person_id]}")
        else:
            seen_ids[person_id] = person_file.name

    return len(findings) == 0, findings
