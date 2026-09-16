"""R09 — No Duplicate Capabilities. No two capabilities share the same `name`."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R09: pyyaml not installed — skipping"]
    seen_names = {}
    for cap_dir in [root/"registries"/"capabilities", root/"capabilities"]:
        if cap_dir.exists():
            for f in sorted(cap_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    name = d.get("name", "")
                    if name:
                        if name in seen_names:
                            findings.append(f"R09: duplicate capability name '{name}' in {f.name} and {seen_names[name]}")
                        else:
                            seen_names[name] = f.name
                except Exception as e:
                    findings.append(f"R09: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
