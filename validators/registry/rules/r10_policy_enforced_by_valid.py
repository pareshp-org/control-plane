"""R10 — Policy enforced_by valid. Must be a valid lane or person id."""
from pathlib import Path
VALID_LANES = {"L0", "L1", "L2", "L3", "L4", "L5"}
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R10: pyyaml not installed — skipping"]
    # Collect known person ids
    people_dir_found = False
    person_ids = set()
    for people_dir in [root/"registries"/"people", root/"people"]:
        if people_dir.exists():
            people_dir_found = True
            for f in people_dir.glob("*.yaml"):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if isinstance(d, dict) and "id" in d: person_ids.add(d["id"])
                except Exception: pass
            break
    valid_refs = VALID_LANES | person_ids
    # Check policies — gate on whether the people directory was found (not on
    # whether the collected set of ids is non-empty), so a present-but-empty
    # people registry still causes person-only references to fail instead of
    # silently passing. Lane references remain checkable regardless, since
    # VALID_LANES is always populated.
    for pol_dir in [root/"registries"/"policies", root/"policies"]:
        if pol_dir.exists():
            for f in sorted(pol_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    enforced_by = d.get("enforced_by", "")
                    if not enforced_by:
                        continue
                    if enforced_by in VALID_LANES:
                        continue
                    if not people_dir_found or enforced_by not in person_ids:
                        findings.append(f"R10: {f.name} enforced_by '{enforced_by}' not a valid lane or person (known: {sorted(valid_refs)[:5]}...)")
                except Exception as e:
                    findings.append(f"R10: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
