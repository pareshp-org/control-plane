"""R13 — No Empty Registries. WARNING if a non-canary registry dir has no .yaml files."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    reg_root = root / "registries" if (root / "registries").exists() else root
    if not reg_root.exists():
        return True, []

    # Check directory-based registries
    for subdir in sorted(reg_root.iterdir()):
        if not subdir.is_dir():
            continue
        # Registries that are maintained as flat files per FD-096 (e.g. economics.yaml, tools.yaml)
        # do not use directory-per-item storage.
        if (reg_root / f"{subdir.name}.yaml").exists():
            continue
        # Registries/directories that ship empty by specification during bootstrap
        # (Section 77.1 framework, Section 20.1 services)
        if subdir.name in {"framework", "services"}:
            continue
        yamls = [f for f in subdir.glob("*.yaml") if not f.name.startswith("_")]
        if not yamls:
            findings.append(f"R13 WARN: {subdir.name}/ has no non-canary .yaml files")

    # Check flat registries for empty entries
    try:
        import yaml
        for flat_name, key in [
            ("economics.yaml", "automation_ledger"),
            ("policies.yaml", "policies"),
            ("os-health.yaml", "signals"),
        ]:
            flat_file = reg_root / flat_name
            if flat_file.exists():
                try:
                    data = yaml.safe_load(flat_file.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        entries = data.get(key)
                        if entries is None or (isinstance(entries, list) and len(entries) == 0):
                            if flat_name == "economics.yaml" and data.get("operating_system_entry"):
                                continue
                            findings.append(f"R13 WARN: {flat_name} has no entries")
                except Exception:
                    pass
    except ImportError:
        pass

    # R13 is a WARNING — return pass even with findings (findings are informational)
    return True, findings

