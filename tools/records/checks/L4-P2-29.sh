#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P2-29 -- full schema sweep over every store.
# Master Spec v4.0 Section 97.2 lines 8845-8875; Section 97.1 line 8839; D88 line 10181.
# Concordance body: L4-T223 in L4-02-record-schemas.md ("store-map.yaml and
# validate-schemas.sh"). Acceptance command per L4-06-tasks.md row 48:
# `bash tools/records/validate-schemas.sh` (default mode --all). DoD-2: "Every
# schema named in store-inventory.yaml plus both envelopes plus the timestamp
# definition load and validate. No store lacks a schema; no schema lacks a store."
CP_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
export CP_ROOT="$CP_DIR"
export L4_PY="${L4_PY:-python}"

VS="$CP_DIR/tools/records/validate-schemas.sh"
MAP="$CP_DIR/schemas/records/store-map.yaml"
NAMES="$CP_DIR/tools/records/validate-no-names.sh"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }
[[ -f "$MAP" ]] || { echo "ABSENT: $MAP" >&2; exit 1; }
[[ -f "$NAMES" ]] || { echo "ABSENT: $NAMES" >&2; exit 1; }

# Positive: the whole gate passes in one command, over the real store-map and
# the real schema files -- this is the acceptance command verbatim.
OUT="$(bash "$VS" 2>&1)" || { echo "$OUT" >&2; echo "validate-schemas.sh (--all) failed" >&2; exit 1; }
echo "$OUT" | tail -n1 | grep -qx "SCHEMAS GATE PASS" \
  || { echo "$OUT" >&2; echo "last line was not SCHEMAS GATE PASS" >&2; exit 1; }

# Assertion: no store lacks a schema, no schema lacks a store -- coverage mode
# reports the fixed row count on its own OK line.
bash "$VS" --coverage | grep -Eq '^COVERAGE OK [0-9]+$' \
  || { echo "validate-schemas.sh --coverage did not report COVERAGE OK" >&2; exit 1; }

# Assertion: the store-map itself still carries exactly eighteen rows (the
# seventeen record stores of Section 2.2 plus the shared events/ envelope --
# store-map_version 1; see L4-T223 note on the nineteen-vs-eighteen count).
ROWS=$(grep -c '{ store:' "$MAP")
[ "$ROWS" -eq 18 ] || { echo "expected 18 store-map rows, got $ROWS" >&2; exit 1; }

# Negative fixture (neg_fixture): a schema declaring a denied property name
# (D88 limb B) must be rejected by --fields. Sandbox a copy of the real store
# schemas with the bad_fixture injected, so the real validate-no-names.sh
# logic runs against real bytes rather than being merely asserted.
BAD_FIXTURE="$CP_DIR/tools/records/fixtures/invalid/denied-property.schema.json"
[[ -f "$BAD_FIXTURE" ]] || { echo "ABSENT: $BAD_FIXTURE" >&2; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/schemas/records" "$TMP/tools/records"
cp "$CP_DIR"/schemas/records/*.schema.json "$TMP/schemas/records/"
cp "$CP_DIR/tools/records/denied-property-names.txt" "$TMP/tools/records/"
cp "$NAMES" "$TMP/tools/records/validate-no-names.sh"
cp "$BAD_FIXTURE" "$TMP/schemas/records/zz-neg-fixture.schema.json"
if CP_ROOT="$TMP" L4_PY="$L4_PY" bash "$TMP/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; then
  echo "neg-fixture: expected D88 rejection did not occur" >&2
  exit 1
fi

echo "CHECK L4-P2-29 PASS"
