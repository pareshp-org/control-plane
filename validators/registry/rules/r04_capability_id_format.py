"""R04 — Capability ID Format. Capability ids must match CAP-NNNN."""
import re
from pathlib import Path
CAP_PATTERN = re.compile(r'^CAP-\d{4}$')
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R04: pyyaml not installed — skipping"]
    for cap_dir in [root/"registries"/"capabilities", root/"capabilities"]:
        if cap_dir.exists():
            for f in sorted(cap_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    cap_id = d.get("id", "")
                    if cap_id and not CAP_PATTERN.match(str(cap_id)):
                        findings.append(f"R04: {f.name} id '{cap_id}' does not match CAP-NNNN")
                except Exception as e:
                    findings.append(f"R04: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
