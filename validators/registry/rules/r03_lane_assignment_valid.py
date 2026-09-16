"""R03 — Lane Assignment Valid. Each lane_assignment must be in {L0,L1,L2,L3,L4,L5}."""
from pathlib import Path
VALID_LANES = {"L0", "L1", "L2", "L3", "L4", "L5"}
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R03: pyyaml not installed — skipping"]
    for people_dir in [root/"registries"/"people", root/"people"]:
        if people_dir.exists():
            for f in sorted(people_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    lanes = d.get("lane_assignments", [])
                    if not isinstance(lanes, list): lanes = [lanes]
                    for lane in lanes:
                        if lane not in VALID_LANES:
                            findings.append(f"R03: {f.name} invalid lane_assignment '{lane}' (valid: {sorted(VALID_LANES)})")
                except Exception as e:
                    findings.append(f"R03: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
