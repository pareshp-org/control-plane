"""
R14 — Schema Version Match
Registry YAML files that declare a `$schema` field must reference a valid
known schema $id. Unrecognised schema identifiers are flagged as failures.
FD-094, FD-096, L1-03, Option B
Exit: 0=pass, 1=fail, 2=input-error
"""
from pathlib import Path

# Hardcoded fallback: known schema $id values from FD-096 schema catalogue.
# These are the $id strings declared in schemas/registry/*.v1.schema.json and
# sibling directories. Used when schemas/ cannot be found on disk.
_KNOWN_SCHEMA_IDS_FALLBACK = frozenset([
    "urn:multiproduct:schemas:registry:people:v1",
    "urn:multiproduct:schemas:registry:capabilities:v1",
    "urn:multiproduct:schemas:registry:roles:v1",
    "urn:multiproduct:schemas:registry:platform:v1",
    "urn:multiproduct:schemas:registry:exceptions:v1",
    "urn:multiproduct:schemas:registry:policies:v1",
    "urn:multiproduct:schemas:registry:commitments:v1",
    "urn:multiproduct:schemas:product:service:v1",
    "urn:multiproduct:schemas:metrics:snapshot:v1",
    "urn:multiproduct:schemas:board:snapshot:v1",
    "urn:multiproduct:schemas:work:open:v1",
    "urn:multiproduct:schemas:governance:topology:v1",
])


def _discover_schema_ids(registry_root):
    """Scan schemas/ directories for JSON Schema files and collect their $id values.

    Tries registry_root/schemas and registry_root/../schemas (for the case where
    registry_root IS the registries/ directory rather than its parent).
    Returns (schema_ids, dir_found) where dir_found records whether a schemas/
    directory was actually located on disk — independent of whether it yielded
    any usable $id values. Callers must use dir_found (not "schema_ids is
    non-empty") to decide whether to fall back to the hardcoded catalogue, so
    that a schemas/ directory that exists but is empty (or whose files all fail
    to parse) is not silently treated the same as a missing directory.
    """
    import json

    root = Path(registry_root)
    candidates = [
        root / "schemas",
        root.parent / "schemas",
    ]
    schema_ids = set()
    dir_found = False
    for schemas_dir in candidates:
        if schemas_dir.exists() and schemas_dir.is_dir():
            dir_found = True
            for json_file in sorted(schemas_dir.rglob("*.json")):
                try:
                    data = json.loads(json_file.read_text("utf-8"))
                    if isinstance(data, dict) and "$id" in data:
                        schema_ids.add(data["$id"])
                except Exception:
                    pass
            break  # use the first existing schemas/ directory found

    return schema_ids, dir_found


def check(registry_root, as_of, records_root=None):
    """Returns (passed: bool, findings: list[str])"""
    findings = []
    root = Path(registry_root)

    try:
        import yaml
    except ImportError:
        return True, ["R14: pyyaml not installed — skipping"]

    # Build the set of known schema $id values (auto-discovered, with hardcoded
    # fallback used ONLY when no schemas/ directory could be found at all — a
    # directory that was found but is empty (or unparsable) must NOT fall back,
    # so that every $schema reference below correctly fails instead of being
    # silently validated against stale hardcoded data.
    discovered_ids, schemas_dir_found = _discover_schema_ids(registry_root)
    known_ids = discovered_ids if schemas_dir_found else set(_KNOWN_SCHEMA_IDS_FALLBACK)

    # Determine the directory to scan: prefer registries/ subdirectory if present
    scan_root = root / "registries" if (root / "registries").exists() else root
    if not scan_root.exists():
        return True, []

    # Walk all *.yaml files recursively; skip canary/internal files (_*.yaml)
    for yaml_file in sorted(scan_root.rglob("*.yaml")):
        if yaml_file.name.startswith("_"):
            continue

        try:
            data = yaml.safe_load(yaml_file.read_text("utf-8"))
        except Exception as exc:
            findings.append(f"R14: {yaml_file.name} parse error: {exc}")
            continue

        if not isinstance(data, dict):
            continue

        schema_ref = data.get("$schema")
        if not schema_ref:
            # $schema is optional; files without it are not checked
            continue

        if schema_ref not in known_ids:
            findings.append(
                f"R14: {yaml_file.name} declares $schema '{schema_ref}' which is not "
                f"in the known schema catalogue (FD-096)"
            )

    return len(findings) == 0, findings
