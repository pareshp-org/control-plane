"""
R11 — Canary Intact
registries/people/_canary.yaml must exist and contain the __CANARY__ sentinel.
FD-094, FD-106/PFD-026, L1-03, Option B
Exit: 0=pass, 1=fail, 2=input-error
"""
from pathlib import Path

SENTINEL = "__CANARY__"
CANARY_PATH = "people/_canary.yaml"  # relative to registry_root


def check(registry_root, as_of, records_root=None):
    """Returns (passed: bool, findings: list[str])"""
    root = Path(registry_root)

    # Try several paths where _canary.yaml might live
    candidates = [
        root / "registries" / "people" / "_canary.yaml",
        root / "people" / "_canary.yaml",
        root / "_canary.yaml",
    ]

    canary_file = None
    for candidate in candidates:
        if candidate.exists():
            canary_file = candidate
            break

    if canary_file is None:
        return False, [f"R11: _canary.yaml not found in {registry_root} (checked {len(candidates)} paths)"]

    content = canary_file.read_text(encoding="utf-8")
    if SENTINEL not in content:
        return False, [f"R11: {canary_file} exists but sentinel '{SENTINEL}' is missing — possible drift"]

    return True, []
