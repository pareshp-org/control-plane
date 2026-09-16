"""R17 — Platform ID Uniqueness. All platform ids must be unique."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R17: pyyaml not installed — skipping"]
    seen_ids = {}
    for plat_dir in [root/"registries"/"platform", root/"platform"]:
        if plat_dir.exists():
            for f in sorted(plat_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    plat_id = d.get("id")
                    if plat_id:
                        if plat_id in seen_ids:
                            findings.append(f"R17: duplicate platform id '{plat_id}' in {f.name} and {seen_ids[plat_id]}")
                        else:
                            seen_ids[plat_id] = f.name
                except Exception as e:
                    findings.append(f"R17: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
