#!/usr/bin/env python3
"""Validate access/secrets/tiers/*.yaml against secret-tier.schema.json.

Section 40.1, lines 3648-3654. Invariant 87: enforced by the platform wherever
the platform can enforce it.

Uses only the standard library plus PyYAML - the two things the phase preflight
proves. It implements the schema subset it needs (required, type, enum, const,
minimum, maximum) rather than importing a schema-validation library, because
adding a dependency is a Contract Change Request, not an edit.

Fail-closed (invariant 80): an unreadable schema, an unreadable tier file or a
missing directory is a FAILURE, never a pass.

Usage:  validate_tiers.py [<tiers-dir>]
Prints one RESULT line last and exits 0 only when every rule holds.
"""
import glob
import json
import os
import sys

import yaml

SCHEMA = os.path.join("access", "secrets", "schemas", "secret-tier.schema.json")
EXPECTED_LOCATIONS = {
    "developer": ".env.local, git-ignored",
    "ci": "GitHub Actions secrets",
    "staging": "GitHub Environment: staging",
    "production": "GitHub Environment: production",
    "control_plane": "Machine-credential store on the hosts that use them",
}
EXPECTED_RANKS = {
    "developer": 1,
    "ci": 2,
    "staging": 3,
    "production": 4,
    "control_plane": 5,
}
TYPES = {
    "object": dict,
    "string": str,
    "integer": int,
    "boolean": bool,
    "array": list,
}


def check_node(value, node, path, errors):
    kind = node.get("type")
    if kind is not None:
        expected = TYPES[kind]
        if expected is int and isinstance(value, bool):
            errors.append("%s: expected integer, got boolean" % path)
            return
        if not isinstance(value, expected):
            errors.append("%s: expected %s, got %s"
                          % (path, kind, type(value).__name__))
            return
    if "const" in node and value != node["const"]:
        errors.append("%s: expected const %r, got %r" % (path, node["const"], value))
    if "enum" in node and value not in node["enum"]:
        errors.append("%s: %r not in enum %r" % (path, value, node["enum"]))
    if "minimum" in node and isinstance(value, int) and value < node["minimum"]:
        errors.append("%s: %r below minimum %r" % (path, value, node["minimum"]))
    if "maximum" in node and isinstance(value, int) and value > node["maximum"]:
        errors.append("%s: %r above maximum %r" % (path, value, node["maximum"]))


def validate_one(doc, schema, path, errors):
    if not isinstance(doc, dict):
        errors.append("%s: document is not a mapping" % path)
        return
    for key in schema.get("required", []):
        if key not in doc:
            errors.append("%s: missing required key %r" % (path, key))
    props = schema.get("properties", {})
    for key, value in doc.items():
        if key in props:
            check_node(value, props[key], "%s:%s" % (path, key), errors)


def main(argv):
    tiers_dir = argv[1] if len(argv) > 1 else os.path.join("access", "secrets", "tiers")
    errors = []
    if not os.path.isfile(SCHEMA):
        print("RESULT FAIL schema-unreadable %s" % SCHEMA)
        return 2
    try:
        with open(SCHEMA, "r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL schema-unparseable %s" % exc)
        return 2
    files = sorted(glob.glob(os.path.join(tiers_dir, "*.yaml")))
    if not files:
        print("RESULT FAIL no-tier-files %s" % tiers_dir)
        return 2
    docs = {}
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
        except Exception as exc:                                # fail closed
            errors.append("%s: unparseable (%s)" % (path, exc))
            continue
        validate_one(doc, schema, path, errors)
        if isinstance(doc, dict) and "tier_id" in doc:
            docs.setdefault(doc["tier_id"], []).append((path, doc))
    for tier_id, entries in sorted(docs.items()):
        if len(entries) > 1:
            errors.append("tier_id %r declared in %d files" % (tier_id, len(entries)))
        path, doc = entries[0]
        if doc.get("rank") != EXPECTED_RANKS.get(tier_id):
            errors.append("%s: rank %r is not the Section 40.1 table position %r"
                          % (path, doc.get("rank"), EXPECTED_RANKS.get(tier_id)))
        if doc.get("location") != EXPECTED_LOCATIONS.get(tier_id):
            errors.append("%s: location is not the Section 40.1 table string" % path)
    for tier_id in sorted(set(EXPECTED_RANKS) - set(docs)):
        errors.append("tier %r has no file" % tier_id)
    for tier_id in sorted(set(docs) - set(EXPECTED_RANKS)):
        errors.append("tier %r is not one of the five tiers of Section 40.1" % tier_id)
    holders = sorted(tid for tid, entries in docs.items()
                     if entries[0][1].get("holds_production_credentials"))
    if holders != ["production"]:
        errors.append("exactly one tier must hold production credentials; got %r"
                      % holders)
    if errors:
        for line in errors:
            print("ERROR %s" % line)
        print("RESULT FAIL %d" % len(errors))
        return 1
    print("RESULT PASS 5")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
