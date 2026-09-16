#!/usr/bin/env bash
# D88: a record carrying a display name MUST fail validation.
# Spec: D88 (line 10181); Section 91.8 line 8171. See DECISION REQUIRED D-L4-P7-01.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../../.." && pwd)"
. "$HERE/lib.sh"
D88="$CP/tools/records/fixtures/negative/d88"
V="$CP/tools/records/fixtures/valid/verbatim"
GATE="$CP/tools/records/lib/validate_instance.py"

# Tested directly against each store's real schema (schema validation IS the
# D88 enforcement mechanism - every person field below is typed person_ref,
# pattern ^[a-z0-9][a-z0-9-]{1,38}$, which "Priya Raman" cannot match). The
# task's own literal script calls record-write/event-append with
# --validate-only/--from-file, a mode neither script implements (record-write
# takes only positional <store> <id> <body-file>; it self-flags this as
# NEEDS_FIX, same FD-039 CLI-shape gap already found in L4-P7-T06).
assert_rejects "D88-01" python3 "$GATE" record "$CP/schemas/records/deployment.schema.json" "$D88/D88-01-approved_by.yaml"
assert_rejects "D88-02" python3 "$GATE" record "$CP/schemas/records/decision.schema.json" "$D88/D88-02-decider.yaml"
assert_rejects "D88-03" python3 "$GATE" record "$CP/schemas/records/demo.schema.json" "$D88/D88-03-given_by.yaml"
assert_rejects "D88-04" python3 "$GATE" record "$CP/schemas/records/deletion-request.schema.json" "$D88/D88-04-executor.yaml"
assert_rejects "D88-05" python3 "$GATE" event "$CP/schemas/records/event.envelope.schema.json" "$D88/D88-05-actor.yaml"

# Matching positives. Without these the negatives prove only that the validator is broken.
assert_exit "D88-P1" 0 python3 "$GATE" record "$CP/schemas/records/deployment.schema.json" "$V/deployment.yaml"
assert_exit "D88-P2" 0 python3 "$GATE" record "$CP/schemas/records/decision.schema.json" "$V/decision.yaml"
assert_exit "D88-P3" 0 python3 "$GATE" record "$CP/schemas/records/demo.schema.json" "$V/demo.yaml"
assert_exit "D88-P4" 0 python3 "$GATE" record "$CP/schemas/records/deletion-request.schema.json" "$CP/tools/records/fixtures/valid/deletion-request.yaml"
assert_exit "D88-P5" 0 python3 "$GATE" event "$CP/schemas/records/event.envelope.schema.json" "$V/event.yaml"

# No display name anywhere in the valid corpora.
leak="$(grep -rEl '^(approved_by|decider|given_by|actor|executor): +[A-Z][a-z]+ +[A-Z]' \
        "$CP/tools/records/fixtures/valid" | wc -l | tr -d ' ')"
assert_eq "D88-CORPUS-CLEAN" "0" "$leak"

summary "03-d88"
