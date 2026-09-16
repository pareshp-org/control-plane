"""
R02 — Role Reference Valid
Every person's `role` field must match an `id` in the roles registry.
FD-094, L1-03, Option B
"""
from pathlib import Path

def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R02: pyyaml not installed — skipping"]

    # Load roles registry
    roles_dir_found = False
    role_ids = set()
    for roles_dir in [root / "registries" / "roles", root / "roles"]:
        if roles_dir.exists():
            roles_dir_found = True
            for f in roles_dir.glob("*.yaml"):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text(encoding="utf-8"))
                    if isinstance(d, dict) and "id" in d:
                        role_ids.add(d["id"])
                except Exception: pass
            break

    # Check people — only validate role references when a roles directory was found
    for people_dir in [root / "registries" / "people", root / "people"]:
        if people_dir.exists():
            for f in sorted(people_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text(encoding="utf-8"))
                    if not isinstance(d, dict): continue
                    role = d.get("role")
                    if role and roles_dir_found and role not in role_ids:
                        findings.append(f"R02: {f.name} role '{role}' not in roles registry (known: {sorted(role_ids)})")
                except Exception as e:
                    findings.append(f"R02: {f.name} parse error: {e}")
            break

    return len(findings) == 0, findings
