"""
R07 — Exception Expiry Future
All active exceptions in registries/exceptions/ must have `expires` date > as_of.
FD-094, L1-03, Option B
"""
from pathlib import Path
from datetime import date

def check(registry_root, as_of, records_root=None):
    findings = []
    root = Path(registry_root)

    exceptions_dir = None
    for candidate in [
        root / "registries" / "exceptions",
        root / "exceptions",
    ]:
        if candidate.exists():
            exceptions_dir = candidate
            break

    if exceptions_dir is None:
        return True, []

    try:
        import yaml
        from datetime import datetime
        try:
            as_of_date = date.fromisoformat(as_of)
        except Exception:
            return False, [f"R07: invalid --as-of date: {as_of}"]
    except ImportError:
        return True, ["R07: pyyaml not installed — skipping"]

    for exc_file in sorted(exceptions_dir.glob("*.yaml")):
        if exc_file.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(exc_file.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(f"R07: {exc_file.name} — parse error: {e}")
            continue

        if not isinstance(data, dict):
            continue
        status = data.get("status", "active")
        if status != "active":
            continue  # only check active exceptions
        expires = data.get("expires")
        if expires is None:
            findings.append(f"R07: {exc_file.name} — missing 'expires' field")
            continue
        try:
            expires_date = date.fromisoformat(str(expires)[:10])
            if expires_date <= as_of_date:
                findings.append(f"R07: {exc_file.name} — expires {expires} is not in the future (as-of: {as_of})")
        except Exception as e:
            findings.append(f"R07: {exc_file.name} — invalid expires date: {expires}")

    return len(findings) == 0, findings
