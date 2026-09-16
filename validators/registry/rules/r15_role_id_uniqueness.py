"""R15 — Role ID Uniqueness. All role ids must be unique."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R15: pyyaml not installed — skipping"]
    seen_ids = {}
    for roles_dir in [root/"registries"/"roles", root/"roles"]:
        if roles_dir.exists():
            for f in sorted(roles_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    role_id = d.get("id")
                    if role_id:
                        if role_id in seen_ids:
                            findings.append(f"R15: duplicate role id '{role_id}' in {f.name} and {seen_ids[role_id]}")
                        else:
                            seen_ids[role_id] = f.name
                except Exception as e:
                    findings.append(f"R15: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
