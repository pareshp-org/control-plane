"""R06 — Platform Type Valid. type must be in {service, library, tool, infra}."""
from pathlib import Path
VALID_TYPES = {"service", "library", "tool", "infra"}
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R06: pyyaml not installed — skipping"]
    for plat_dir in [root/"registries"/"platform", root/"platform"]:
        if plat_dir.exists():
            for f in sorted(plat_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    ptype = d.get("type", "")
                    if ptype and ptype not in VALID_TYPES:
                        findings.append(f"R06: {f.name} type '{ptype}' not in {sorted(VALID_TYPES)}")
                except Exception as e:
                    findings.append(f"R06: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
