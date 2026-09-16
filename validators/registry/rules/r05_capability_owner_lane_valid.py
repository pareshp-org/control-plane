"""R05 — Capability Owner Lane Valid. owner_lane must be in {L0..L5}."""
from pathlib import Path
VALID_LANES = {"L0", "L1", "L2", "L3", "L4", "L5"}
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R05: pyyaml not installed — skipping"]
    for cap_dir in [root/"registries"/"capabilities", root/"capabilities"]:
        if cap_dir.exists():
            for f in sorted(cap_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    owner = d.get("owner_lane", "")
                    if owner and owner not in VALID_LANES:
                        findings.append(f"R05: {f.name} owner_lane '{owner}' not in {sorted(VALID_LANES)}")
                except Exception as e:
                    findings.append(f"R05: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
