"""R16 — FTE Range Valid. Person fte must be in [0.0, 1.0] when present."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    try:
        import yaml
    except ImportError:
        return True, ["R16: pyyaml not installed — skipping"]
    for people_dir in [root/"registries"/"people", root/"people"]:
        if people_dir.exists():
            for f in sorted(people_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    fte = d.get("fte")
                    if fte is not None:
                        try:
                            fte_f = float(fte)
                            if not (0.0 <= fte_f <= 1.0):
                                findings.append(f"R16: {f.name} fte={fte} out of range [0.0, 1.0]")
                        except (TypeError, ValueError):
                            findings.append(f"R16: {f.name} fte='{fte}' is not a number")
                except Exception as e:
                    findings.append(f"R16: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
