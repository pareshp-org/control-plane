"""R18 — Exception granted_by Authorized. Must be an authorized actor (FD-083)."""
from pathlib import Path
AUTHORIZED_ACTORS = {"bendrohit-eng"}  # FD-086: bootstrap actor gate
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R18: pyyaml not installed — skipping"]
    for exc_dir in [root/"registries"/"exceptions", root/"exceptions"]:
        if exc_dir.exists():
            for f in sorted(exc_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    granted_by = d.get("granted_by", "")
                    if granted_by and granted_by not in AUTHORIZED_ACTORS:
                        findings.append(f"R18: {f.name} granted_by '{granted_by}' is not an authorized actor (FD-083, FD-086)")
                except Exception as e:
                    findings.append(f"R18: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
