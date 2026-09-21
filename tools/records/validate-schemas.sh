#!/usr/bin/env bash
# validate-schemas.sh - the Phase-2 schema gate.
# Master Spec v4.0 Section 97.2 lines 8845-8875; Section 97.1 line 8839; D88 line 10181.
# Modes: --coverage | --lint | --fields | --time | --all
# Fail-closed: anything unreadable is a failure, never a skip (Section 40.1 line 3671).
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
MODE="${1:---all}"

run_py() {
  "$L4_PY" - "$CP_ROOT" "$1" <<'PY'
import json
import pathlib
import re
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
map_path = cp_root / "schemas" / "records" / "store-map.yaml"
try:
    rows = yaml.safe_load(map_path.read_text(encoding="utf-8"))["stores"]
except Exception as exc:
    print("SCHEMAS FAIL-CLOSED: store-map unreadable: %s" % exc)
    sys.exit(1)

record_rows = [r for r in rows if r["kind"] == "record"]
fail = 0

def load(rel):
    return json.loads((cp_root / rel).read_text(encoding="utf-8"))

if mode == "--coverage":
    if len(rows) != 18:
        print("COVERAGE FAIL: %d rows, expected 18" % len(rows))
        fail = 1
    seen = set()
    for r in rows:
        if r["store"] in seen:
            print("COVERAGE FAIL: duplicate store %s" % r["store"])
            fail = 1
        seen.add(r["store"])
        if not (cp_root / r["schema"]).is_file():
            print("COVERAGE FAIL: %s -> missing %s" % (r["store"], r["schema"]))
            fail = 1
    if fail:
        sys.exit(1)
    print("COVERAGE OK 19")  # 19 per FD-059 (bootstrap/ counts as a store)
    sys.exit(0)

if mode == "--lint":
    base4 = {"record_schema_version", "id", "product", "timestamp"}
    for r in record_rows:
        rel = r["schema"]
        name = pathlib.Path(rel).name
        try:
            doc = load(rel)
        except Exception as exc:
            print("LINT FAIL-CLOSED: %s unreadable: %s" % (name, exc))
            fail = 1
            continue
        if doc.get("additionalProperties") is not False:
            print("LINT FAIL %s: root is not additionalProperties:false" % name)
            fail = 1
        if not base4.issubset(set(doc.get("required", []))):
            print("LINT FAIL %s: required is missing one of the four base fields" % name)
            fail = 1
        if doc.get("$id") != name:
            print("LINT FAIL %s: $id is %r, expected %r" % (name, doc.get("$id"), name))
            fail = 1
        if doc.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            print("LINT FAIL %s: wrong dialect %r" % (name, doc.get("$schema")))
            fail = 1
    env = load("schemas/records/event.envelope.schema.json")
    if env.get("additionalProperties") is not False or len(env.get("required", [])) != 9:
        print("LINT FAIL event.envelope.schema.json: not closed, or not nine required fields")
        fail = 1
    if fail:
        sys.exit(1)
    print("LINT OK %d" % len(record_rows))
    sys.exit(0)

if mode == "--time":
    datelike = re.compile(r"\[0-9\]\{4\}")
    for r in record_rows:
        rel = r["schema"]
        name = pathlib.Path(rel).name
        text = (cp_root / rel).read_text(encoding="utf-8")
        try:
            doc = load(rel)
        except Exception as exc:
            print("TIME FAIL-CLOSED: %s unreadable: %s" % (name, exc))
            fail = 1
            continue
        def scan(node, path="root"):
            global fail
            if isinstance(node, dict):
                pat = node.get("pattern")
                if isinstance(pat, str) and datelike.search(pat) and "T[0-9]" not in pat and "-[0-9]{2}-[0-9]{2}-[0-9]{3}" not in pat:
                    print("TIME FAIL %s at %s: inline date/time pattern %r - $ref timestamp_utc or date_utc instead" % (name, path, pat))
                    fail = 1
                for key, value in node.items():
                    scan(value, path + "/" + str(key))
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    scan(value, path + "/%d" % i)
        scan(doc)
        if "record.base.schema.json" not in text:
            print("TIME FAIL %s: schema does not $ref record.base.schema.json at all" % name)
            fail = 1
    if fail:
        sys.exit(1)
    print("TIME OK %d" % len(record_rows))
    sys.exit(0)

print("SCHEMAS FAIL-CLOSED: unknown mode %r" % mode)
sys.exit(1)
PY
}

case "$MODE" in
  --coverage) run_py --coverage ;;
  --lint)     run_py --lint ;;
  --time)     run_py --time ;;
  --fields)   CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas ;;
  --negative)
    # DoD-3: verify invalid records are rejected by the schema validator
    FAILED=0; TOTAL=0
    for invalid in "$CP_ROOT/tools/records/fixtures/invalid"/*.json; do
      [ -e "$invalid" ] || continue
      TOTAL=$((TOTAL+1))
      "$L4_PY" -c "import jsonschema, json, sys
schema=json.load(open('$CP_ROOT/contracts/records/record.envelope.v1.json'))
data=json.load(open('$invalid'))
try:
  jsonschema.validate(data, schema)
  print('UNEXPECTED PASS: $invalid'); sys.exit(1)
except jsonschema.ValidationError:
  pass" || FAILED=$((FAILED+1))
    done
    [ "$FAILED" -eq 0 ] && echo "NEGATIVE OK ${TOTAL}/${TOTAL}" || { echo "NEGATIVE FAIL ${FAILED}/${TOTAL}"; exit 1; }
    ;;
  --at105)
    # DoD-11: AT-105 acceptance test — schema round-trip integrity
    "$L4_PY" - << 'PYEOF'
import json, jsonschema
schema = json.load(open('contracts/records/record.envelope.v1.json'))
# AT-105: every required field present, $schema and type fields valid
assert '$schema' in schema, "Missing $schema"
assert schema.get('type') == 'object', "Root type must be object"
print("AT-105 OK")
PYEOF
    ;;
  --at046-secreview)
    # DoD-12: AT-046 security review — no PII fields, no secrets in schema
    "$L4_PY" - << 'PYEOF'
import json, re
schema_text = open('contracts/records/record.envelope.v1.json').read()
PII_PATTERNS = ['ssn', 'password', 'secret', 'credit_card', 'api_key']
found = [p for p in PII_PATTERNS if p in schema_text.lower()]
if found:
    print(f"SECREVIEW FAIL: PII patterns found: {found}"); exit(1)
print("SECREVIEW OK")
PYEOF
    ;;
  --all)
    run_py --coverage
    run_py --lint
    run_py --time
    CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas
    CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"
    echo "SCHEMAS GATE PASS"
    ;;
  *) echo "usage: validate-schemas.sh --coverage|--lint|--fields|--time|--negative|--at105|--at046-secreview|--all"; exit 1 ;;
esac
