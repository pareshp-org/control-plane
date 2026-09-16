"""
Independent cross-validation of registries/**/*.yaml against schemas/registry/*.json
(and schemas/governance/topology.v1.schema.json for the root-level topology.yaml).

This is a *second, independent* conformance check alongside
scripts/l1/jsonschema-conform.py. It deliberately does NOT import or reuse
anything from that script, and it deliberately does NOT delegate the actual
schema-conformance decision to the `jsonschema` library's validator either
(even though that package is available and is what jsonschema-conform.py
uses). Instead this file hand-rolls its own small Draft-07-subset validator
(`validate_instance`) directly in the test module, so a bug shared between
the production script and the `jsonschema` package's Draft7Validator would
not produce a false-positive "PASS" here.

Two things are checked:

1. Schema conformance — every non-underscore registries/**/*.yaml file,
   independently mapped to its schema file, validated by the inline
   validator (test_registry_file_conforms_to_schema_independent).

2. Id uniqueness — a second, independent-of-the-R-rule-validators regression
   guard confirming every registry file's top-level `id` is unique within
   its own registry type (directory). R01/R15/R17 already do this for
   people/roles/platform specifically, by importing shared rule modules
   through the CLI; this check is a from-scratch re-implementation that
   additionally covers capabilities/exceptions/policies, which have no
   dedicated R-rule for id uniqueness today.

Files whose name starts with "_" (e.g. registries/*/_canary.yaml) are
excluded, matching the established convention in jsonschema-conform.py and
in R01/R15/R17: they are drift-detection sentinels, not registry records.

A handful of self-tests near the bottom prove the inline validator and the
duplicate-id detector actually catch violations (using synthetic
schemas/instances), so this file cannot pass vacuously.
"""
import datetime
import json
import re
from pathlib import Path

import pytest
import yaml

IMPL_ROOT = Path(__file__).resolve().parents[2]
REGISTRIES_DIR = IMPL_ROOT / "registries"
SCHEMAS_DIR = IMPL_ROOT / "schemas"

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Inline Draft-07-subset JSON Schema validator (independent of `jsonschema`)
# ---------------------------------------------------------------------------

def _json_type_name(value):
    """Map a Python value (as produced by yaml.safe_load / json.load) to its
    JSON Schema type name."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _type_matches(value, expected_type):
    expected = expected_type if isinstance(expected_type, list) else [expected_type]
    actual = _json_type_name(value)
    for t in expected:
        if t == actual:
            return True
        if t == "number" and actual == "integer":
            # JSON Schema: every integer is also a number
            return True
    return False


def _is_valid_date(s):
    if not isinstance(s, str) or not _DATE_RE.match(s):
        return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def validate_instance(instance, schema, path="$"):
    """Hand-rolled, independent validator for the Draft-07 subset actually
    used by schemas/registry/*.json and schemas/governance/topology.v1.schema.json
    (type, required, properties, additionalProperties, pattern, enum,
    format: date, minimum/maximum, items). Returns a list of human-readable
    error strings; empty list means the instance conforms."""
    errors = []

    if "type" in schema:
        if not _type_matches(instance, schema["type"]):
            errors.append(
                f"{path}: expected type {schema['type']!r}, got "
                f"{_json_type_name(instance)!r} (value: {instance!r})"
            )
            # Structural checks below assume the type is right; bail here.
            return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not one of {schema['enum']!r}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(
                f"{path}: value {instance!r} does not match pattern {schema['pattern']!r}"
            )
        if schema.get("format") == "date" and not _is_valid_date(instance):
            errors.append(f"{path}: value {instance!r} is not a valid ISO date (format: date)")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value {instance!r} is below minimum {schema['minimum']!r}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value {instance!r} is above maximum {schema['maximum']!r}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property '{req}'")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property '{key}' is not allowed")

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate_instance(item, schema["items"], f"{path}[{i}]"))

    return errors


# ---------------------------------------------------------------------------
# Independent discovery / schema-mapping (no import from scripts/l1/*)
# ---------------------------------------------------------------------------

def discover_registry_yaml_files():
    """All registries/**/*.yaml files, excluding "_"-prefixed sentinel files."""
    return [
        p for p in sorted(REGISTRIES_DIR.rglob("*.yaml"))
        if not p.name.startswith("_")
    ]


def find_schema_for(yaml_path):
    """Independently map a registries/**/*.yaml file to its schema path.

    - registries/<subdir>/<file>.yaml -> schemas/registry/<subdir>.v1.schema.json
    - registries/<file>.yaml (no subdirectory) -> the unique
      schemas/**/<stem>.v1.schema.json found anywhere under schemas/

    Returns None if no unambiguous mapping exists.
    """
    rel_parts = yaml_path.relative_to(REGISTRIES_DIR).parts

    if len(rel_parts) >= 2:
        subdir = rel_parts[0]
        candidate = SCHEMAS_DIR / "registry" / f"{subdir}.v1.schema.json"
        return candidate if candidate.exists() else None

    stem = yaml_path.stem
    matches = list(SCHEMAS_DIR.rglob(f"{stem}.v1.schema.json"))
    return matches[0] if len(matches) == 1 else None


_YAML_FILES = discover_registry_yaml_files()
_YAML_FILE_IDS = [str(p.relative_to(REGISTRIES_DIR)).replace("\\", "/") for p in _YAML_FILES]


# ---------------------------------------------------------------------------
# Independent id-uniqueness scan (not importing r01/r15/r17)
# ---------------------------------------------------------------------------

def collect_ids_by_registry_type():
    """dict: registry-type directory name -> list of (id, filename) for
    every non-underscore *.yaml file directly in that directory that has a
    top-level `id` field."""
    by_type = {}
    for entry in sorted(REGISTRIES_DIR.iterdir()):
        if not entry.is_dir():
            continue
        pairs = []
        for f in sorted(entry.glob("*.yaml")):
            if f.name.startswith("_"):
                continue
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "id" in data:
                pairs.append((data["id"], f.name))
        by_type[entry.name] = pairs
    return by_type


def find_duplicate_ids(pairs):
    """pairs: iterable of (id, filename). Returns list of
    (duplicate_id, filename, first_seen_filename) for every repeat."""
    seen = {}
    dupes = []
    for id_val, fname in pairs:
        if id_val in seen:
            dupes.append((id_val, fname, seen[id_val]))
        else:
            seen[id_val] = fname
    return dupes


# ===========================================================================
# 1. Schema conformance — every registries/**/*.yaml against its schema
# ===========================================================================

def test_discovery_found_expected_registry_files():
    """Sanity check that discovery is actually finding files (guards against
    this whole test module silently passing vacuously with 0 collected
    files if REGISTRIES_DIR/SCHEMAS_DIR ever move)."""
    assert len(_YAML_FILES) >= 10
    names = {p.name for p in _YAML_FILES}
    assert "topology.yaml" in names
    assert any(p.name.startswith("CAP-") for p in _YAML_FILES)
    # canary sentinels must be excluded
    assert not any(p.name.startswith("_") for p in _YAML_FILES)


@pytest.mark.parametrize("yaml_path", _YAML_FILES, ids=_YAML_FILE_IDS)
def test_registry_file_conforms_to_schema_independent(yaml_path):
    schema_path = find_schema_for(yaml_path)
    assert schema_path is not None, (
        f"no independent schema mapping found for "
        f"{yaml_path.relative_to(IMPL_ROOT)}"
    )

    instance = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    errors = validate_instance(instance, schema)
    assert errors == [], (
        f"{yaml_path.relative_to(IMPL_ROOT)} failed independent validation "
        f"against {schema_path.relative_to(IMPL_ROOT)}:\n" + "\n".join(errors)
    )


# ===========================================================================
# 2. Id uniqueness — independent regression guard, all registry types
# ===========================================================================

def test_ids_unique_within_each_registry_type():
    by_type = collect_ids_by_registry_type()
    # sanity: make sure we actually scanned the directories we expect
    assert set(by_type) >= {
        "capabilities", "exceptions", "people", "platform", "policies", "roles",
    }
    for registry_type, pairs in by_type.items():
        dupes = find_duplicate_ids(pairs)
        assert dupes == [], f"duplicate id(s) in registries/{registry_type}: {dupes}"


def test_topology_domain_ids_unique():
    """topology.yaml has no top-level id (governance topology, not a
    per-record registry) but its `domains` array entries each carry their
    own id — check those independently too, as a forward guard for when
    domains_active flips true and domains get populated (AT-016)."""
    topology_path = REGISTRIES_DIR / "topology.yaml"
    data = yaml.safe_load(topology_path.read_text(encoding="utf-8"))
    domains = data.get("domains", []) if isinstance(data, dict) else []
    pairs = [(d["id"], d.get("id", "?")) for d in domains if isinstance(d, dict) and "id" in d]
    dupes = find_duplicate_ids(pairs)
    assert dupes == [], f"duplicate domain id(s) in registries/topology.yaml: {dupes}"


# ===========================================================================
# 3. Self-tests: prove the inline validator and dupe-detector are not vacuous
# ===========================================================================

def test_validator_accepts_a_valid_instance():
    schema = {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "string", "pattern": "^CAP-[0-9]{4}$"},
            "name": {"type": "string"},
        },
    }
    assert validate_instance({"id": "CAP-0001", "name": "x"}, schema) == []


def test_validator_catches_missing_required_field():
    schema = {"type": "object", "required": ["id", "name"], "properties": {}}
    errors = validate_instance({"id": "X"}, schema)
    assert any("name" in e for e in errors)


def test_validator_catches_type_mismatch():
    schema = {"type": "object", "properties": {"fte": {"type": "number"}}}
    errors = validate_instance({"fte": "not-a-number"}, schema)
    assert errors and "fte" in errors[0]


def test_validator_catches_pattern_violation():
    schema = {"type": "string", "pattern": "^CAP-[0-9]{4}$"}
    assert validate_instance("BAD-ID", schema) != []


def test_validator_catches_enum_violation():
    schema = {"type": "string", "enum": ["active", "deprecated", "planned"]}
    assert validate_instance("bogus-status", schema) != []


def test_validator_catches_bad_date_format():
    schema = {"type": "string", "format": "date"}
    assert validate_instance("09/09/2026", schema) != []
    assert validate_instance("2026-09-09", schema) == []


def test_validator_catches_disallowed_additional_property():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"id": {"type": "string"}},
    }
    errors = validate_instance({"id": "x", "surprise": "y"}, schema)
    assert errors and "surprise" in errors[0]


def test_validator_catches_out_of_range_number():
    schema = {"type": "number", "minimum": 0, "maximum": 1}
    assert validate_instance(1.5, schema) != []
    assert validate_instance(-0.1, schema) != []
    assert validate_instance(0.5, schema) == []


def test_validator_recurses_into_arrays():
    schema = {"type": "array", "items": {"type": "string"}}
    assert validate_instance(["a", "b"], schema) == []
    assert validate_instance(["a", 2], schema) != []


def test_duplicate_id_detection_catches_synthetic_duplicate():
    pairs = [("CAP-0001", "a.yaml"), ("CAP-0002", "b.yaml"), ("CAP-0001", "c.yaml")]
    dupes = find_duplicate_ids(pairs)
    assert len(dupes) == 1
    assert dupes[0][0] == "CAP-0001"
    assert dupes[0][1] == "c.yaml"
    assert dupes[0][2] == "a.yaml"


def test_duplicate_id_detection_passes_when_all_unique():
    pairs = [("CAP-0001", "a.yaml"), ("CAP-0002", "b.yaml")]
    assert find_duplicate_ids(pairs) == []


def test_real_capabilities_schema_rejects_mutated_id(tmp_path):
    """Mutation check against a *real* schema file (not synthetic): take the
    live capabilities schema and a deliberately broken instance, confirm the
    inline validator (the same one used above against real registry files)
    actually flags it. Guards against the inline validator being too
    permissive to ever fail."""
    schema = json.loads(
        (SCHEMAS_DIR / "registry" / "capabilities.v1.schema.json").read_text(encoding="utf-8")
    )
    broken = {"id": "not-a-valid-cap-id", "name": "x", "owner_lane": "L9"}
    errors = validate_instance(broken, schema)
    assert errors, "expected the real capabilities schema to reject a malformed instance"
