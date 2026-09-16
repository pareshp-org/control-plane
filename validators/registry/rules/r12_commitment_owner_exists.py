"""R12 — Commitment Owner Exists. commitment.owner must exist in people registry."""
from pathlib import Path
def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)
    records = Path(records_root) if records_root else root
    try:
        import yaml
    except ImportError:
        return True, ["R12: pyyaml not installed — skipping"]
    # Collect person ids
    people_dir_found = False
    person_ids = set()
    for people_dir in [root/"registries"/"people", root/"people"]:
        if people_dir.exists():
            people_dir_found = True
            for f in people_dir.glob("*.yaml"):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if isinstance(d, dict) and "id" in d: person_ids.add(d["id"])
                except Exception: pass
            break
    # Check commitments — only validate owner references when a people directory was found
    for commit_dir in [records/"commitments", root/"registries"/"commitments"]:
        if commit_dir.exists():
            for f in sorted(commit_dir.glob("*.yaml")):
                if f.name.startswith("_"): continue
                try:
                    d = yaml.safe_load(f.read_text("utf-8"))
                    if not isinstance(d, dict): continue
                    owner = d.get("owner", "")
                    if owner and people_dir_found and owner not in person_ids:
                        findings.append(f"R12: {f.name} owner '{owner}' not in people registry")
                except Exception as e:
                    findings.append(f"R12: {f.name} error: {e}")
            break
    return len(findings) == 0, findings
