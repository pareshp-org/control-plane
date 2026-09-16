#!/usr/bin/env python3
"""
L1 JSON Schema Conformance Check (FD-096)

Validates every registry YAML file under registries/**/*.yaml, plus the
explicit board/work record snapshots, against its mapped JSON Schema
definition using the `jsonschema` package.

Mapping convention (see schemas/registry/*.json and registries/*/README.md):
  registries/<name>/<file>.yaml  -> schemas/registry/<name>.v1.schema.json
      e.g. registries/people/*.yaml        -> schemas/registry/people.v1.schema.json
           registries/capabilities/*.yaml  -> schemas/registry/capabilities.v1.schema.json

  registries/<file>.yaml (directly under registries/, no subdirectory)
      -> resolved by matching <file>'s stem against the unique
         schemas/**/<stem>.v1.schema.json found anywhere under schemas/
      e.g. registries/topology.yaml -> schemas/governance/topology.v1.schema.json

  records/board/snapshot.yaml -> schemas/board/snapshot.v1.schema.json   (explicit)
  records/work/open.yaml      -> schemas/work/open.v1.schema.json       (explicit)

Files whose name starts with "_" (e.g. registries/*/_canary.yaml) are
excluded from discovery — they are drift-detection sentinels, not registry
records, and are not expected to conform to the registry schema.

Usage: python scripts/l1/jsonschema-conform.py
Exit codes: 0 = every discovered file conforms, 1 = one or more files failed
"""
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError

IMPL_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMAS_DIR = IMPL_ROOT / "schemas"
REGISTRIES_DIR = IMPL_ROOT / "registries"
RECORDS_DIR = IMPL_ROOT / "records"

SCHEMA_SUFFIX = ".v1.schema.json"

# Explicit record-file mappings (per task spec), beyond the registries/ walk.
EXPLICIT_TARGETS = [
    (RECORDS_DIR / "board" / "snapshot.yaml", SCHEMAS_DIR / "board" / "snapshot.v1.schema.json"),
    (RECORDS_DIR / "work" / "open.yaml", SCHEMAS_DIR / "work" / "open.v1.schema.json"),
]


def discover_schemas_by_stem():
    """Map schema filename stem (e.g. 'people', 'topology') -> list of
    (category, path) for every schemas/<category>/<stem>.v1.schema.json
    found anywhere under schemas/. Used to resolve registries/*.yaml files
    that live directly under registries/ (no owning subdirectory)."""
    by_stem = {}
    for schema_file in sorted(SCHEMAS_DIR.rglob("*" + SCHEMA_SUFFIX)):
        stem = schema_file.name[: -len(SCHEMA_SUFFIX)]
        category = schema_file.parent.name
        by_stem.setdefault(stem, []).append((category, schema_file))
    return by_stem


def map_registry_file(yaml_path, by_stem):
    """Return the schema Path for a registries/**/*.yaml file, or None with
    a reason string if no unambiguous mapping could be found."""
    rel_parts = yaml_path.relative_to(REGISTRIES_DIR).parts

    if len(rel_parts) >= 2:
        # registries/<subdir>/<file>.yaml -> schemas/registry/<subdir>.v1.schema.json
        subdir = rel_parts[0]
        candidate = SCHEMAS_DIR / "registry" / f"{subdir}{SCHEMA_SUFFIX}"
        if candidate.exists():
            return candidate, None
        return None, f"no schemas/registry/{subdir}{SCHEMA_SUFFIX} for directory '{subdir}'"

    # registries/<file>.yaml directly under registries/ root: resolve by
    # matching the filename stem against the schema catalogue.
    stem = yaml_path.stem
    matches = by_stem.get(stem, [])
    if len(matches) == 1:
        return matches[0][1], None
    if len(matches) > 1:
        cats = ", ".join(f"schemas/{c}/{stem}{SCHEMA_SUFFIX}" for c, _ in matches)
        return None, f"ambiguous schema stem '{stem}' — matches: {cats}"
    return None, f"no schema found with stem '{stem}' anywhere under schemas/"


def discover_registry_targets():
    """Walk registries/**/*.yaml (excluding _-prefixed files) and map each
    to its schema. Returns list of (yaml_path, schema_path_or_None, note)."""
    by_stem = discover_schemas_by_stem()
    targets = []
    for yaml_path in sorted(REGISTRIES_DIR.rglob("*.yaml")):
        if yaml_path.name.startswith("_"):
            continue
        schema_path, note = map_registry_file(yaml_path, by_stem)
        targets.append((yaml_path, schema_path, note))
    return targets


def load_yaml(path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema(path):
    import json
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def relpath(path):
    try:
        return str(path.relative_to(IMPL_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def validate_one(yaml_path, schema_path):
    """Returns (ok: bool, message: str)."""
    try:
        instance = load_yaml(yaml_path)
    except Exception as exc:
        return False, f"YAML parse error: {exc}"

    try:
        schema = load_schema(schema_path)
    except Exception as exc:
        return False, f"schema load error ({relpath(schema_path)}): {exc}"

    try:
        validator = Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)
    except SchemaError as exc:
        return False, f"invalid schema ({relpath(schema_path)}): {exc}"

    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if not errors:
        return True, f"conforms to {relpath(schema_path)}"

    lines = [f"{len(errors)} violation(s) against {relpath(schema_path)}:"]
    for err in errors:
        loc = "/".join(str(p) for p in err.path) or "<root>"
        lines.append(f"    - at {loc}: {err.message}")
    return False, "\n".join(lines)


def main():
    results = []  # (label, ok, message)

    for yaml_path, schema_path, note in discover_registry_targets():
        label = relpath(yaml_path)
        if schema_path is None:
            results.append((label, False, f"no schema mapping found ({note})"))
            continue
        ok, message = validate_one(yaml_path, schema_path)
        results.append((label, ok, message))

    for yaml_path, schema_path in EXPLICIT_TARGETS:
        label = relpath(yaml_path)
        if not yaml_path.exists():
            results.append((label, False, "file not found"))
            continue
        if not schema_path.exists():
            results.append((label, False, f"schema not found: {relpath(schema_path)}"))
            continue
        ok, message = validate_one(yaml_path, schema_path)
        results.append((label, ok, message))

    print("=== L1 JSON Schema Conformance ===")
    fail_count = 0
    pass_count = 0
    for label, ok, message in results:
        status = "PASS" if ok else "FAIL"
        if ok:
            pass_count += 1
            print(f"PASS: {label} — {message}")
        else:
            fail_count += 1
            print(f"FAIL: {label} — {message}")

    print()
    print(f"Conformance check: {pass_count} passed, {fail_count} failed, {len(results)} total")

    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
