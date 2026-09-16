"""R13 — No Empty Registries. WARNING if a non-canary registry dir has no .yaml files."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    reg_root = root / "registries" if (root / "registries").exists() else root
    if not reg_root.exists():
        return True, []
    for subdir in sorted(reg_root.iterdir()):
        if not subdir.is_dir(): continue
        yamls = [f for f in subdir.glob("*.yaml") if not f.name.startswith("_")]
        if not yamls:
            findings.append(f"R13 WARN: {subdir.name}/ has no non-canary .yaml files")
    # R13 is a WARNING — return pass even with findings (findings are informational)
    return True, findings
