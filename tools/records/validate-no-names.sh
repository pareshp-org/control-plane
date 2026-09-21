#!/usr/bin/env bash
# validate-no-names.sh - D88 enforcement, limbs B and C.
# Master Spec v4.0 D88 line 10181; Section 91.8 line 8171; Section 40.1 line 3671.
#
#   validate-no-names.sh --schemas
#       Limb B. Fails if any schema under schemas/records/ declares a denied property name.
#
#   validate-no-names.sh --records <roster.yaml> <record.yaml> [<record.yaml> ...]
#       Limb C. Fails if any string value in any record equals a display_name in the roster.
#       A roster that cannot be read is a FAILURE, never a pass (fail closed).
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
MODE="${1:?usage: validate-no-names.sh --schemas | --records <roster> <record>...}"
shift
"$L4_PY" - "$CP_ROOT" "$MODE" "$@" <<'PY'
import json
import pathlib
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
args = sys.argv[3:]

denied_path = cp_root / "tools" / "records" / "denied-property-names.txt"
try:
    denied = {
        ln.strip()
        for ln in denied_path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    }
except Exception as exc:
    print("NO-NAMES FAIL-CLOSED: denylist unreadable: %s" % exc)
    sys.exit(1)

def walk_property_names(node):
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            for key in props:
                yield key
        for value in node.values():
            for found in walk_property_names(value):
                yield found
    elif isinstance(node, list):
        for value in node:
            for found in walk_property_names(value):
                yield found

def walk_strings(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            for found in walk_strings(value):
                yield found
    elif isinstance(node, list):
        for value in node:
            for found in walk_strings(value):
                yield found
    elif isinstance(node, str):
        yield node

failed = 0
if mode == "--schemas":
    schema_dir = cp_root / "schemas" / "records"
    # record.base.schema.json is the shared $defs LIBRARY (Section 97.1/97.2),
    # not a record body shape - no store ever inlines its $defs, every store
    # $refs them. Its artifact_identity $def legitimately carries a "name"
    # field for a distributed artifact's name (Section 97.2 line 8918, and
    # the standing note at Section 3.4 rule 3 of this phase: "artifact_identity
    # is the spec-named type"). That is a container-artifact name, never a
    # person's name, so it is not a D88 violation - but the generic denylist
    # token "name" cannot tell the two apart by string matching alone.
    # record.probe.schema.json is explicitly "excluded from store-map.yaml"
    # (its own description) - a $defs-resolution probe, not a store schema.
    # Limb B is a store-body lint: scan every actual store/event schema, and
    # exclude only these two non-store files. Do not add further exclusions
    # without a citation - this is the one documented, spec-driven carve-out.
    excluded = {"record.base.schema.json", "record.probe.schema.json"}
    files = sorted(p for p in schema_dir.glob("*.schema.json") if p.name not in excluded)
    if not files:
        print("NO-NAMES FAIL-CLOSED: no schema files found under %s" % schema_dir)
        sys.exit(1)
    for path in files:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("NO-NAMES FAIL-CLOSED: %s unreadable: %s" % (path.name, exc))
            failed += 1
            continue
        hits = sorted({p for p in walk_property_names(doc) if p in denied})
        if hits:
            print("D88 VIOLATION %s: denied property name(s): %s" % (path.name, ", ".join(hits)))
            failed += 1
    if failed:
        sys.exit(1)
    print("NO-NAMES SCHEMAS OK %d" % len(files))
    sys.exit(0)

if mode == "--records":
    if len(args) < 2:
        print("NO-NAMES FAIL-CLOSED: --records needs a roster and at least one record")
        sys.exit(1)
    roster_path = pathlib.Path(args[0])
    try:
        roster = yaml.safe_load(roster_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("NO-NAMES FAIL-CLOSED: roster unreadable: %s: %s" % (roster_path, exc))
        sys.exit(1)
    def collect_display_names(node):
        out = set()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "display_name" and isinstance(value, str) and value.strip():
                    out.add(value.strip().lower())
                out |= collect_display_names(value)
        elif isinstance(node, list):
            for value in node:
                out |= collect_display_names(value)
        return out
    names = collect_display_names(roster)
    if not names:
        print("NO-NAMES FAIL-CLOSED: roster %s declares no display_name" % roster_path)
        sys.exit(1)
    for target in args[1:]:
        path = pathlib.Path(target)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("NO-NAMES FAIL-CLOSED: %s unreadable: %s" % (target, exc))
            failed += 1
            continue
        hits = sorted({s for s in walk_strings(data) if s.strip().lower() in names})
        if hits:
            print("D88 VIOLATION %s: display name in record body: %s" % (target, ", ".join(hits)))
            failed += 1
        else:
            print("NO-NAMES OK %s" % target)
    if failed:
        sys.exit(1)
    sys.exit(0)

print("NO-NAMES FAIL-CLOSED: unknown mode %r" % mode)
sys.exit(1)
PY
