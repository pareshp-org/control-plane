#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../../.." && pwd)"
. "$HERE/lib.sh"
NEG="$CP/tools/records/fixtures/negative/envelope"
GATE="$CP/tools/records/lib/validate_instance.py"
SCHEMA="$CP/schemas/records/event.envelope.schema.json"

# Every negative fixture must be REJECTED by the real write-time gate
# (tools/records/lib/validate_instance.py, the code emit_event actually calls).
# NOTE: the task's own literal script calls
# "$CP/tools/records/event-append" --from-file <f>, but event-append (built
# for L4-T305/L4-P5's writer) takes ONLY positional
# <event_type> <actor> <product> <subject_ref> [payload-file] and always
# constructs its own envelope from scratch - it has no --from-file/
# --fixture-mode mode to validate an already-built envelope file, so it
# cannot exercise "does a malformed envelope get rejected" at all. The
# script even flags this itself ("NEEDS_FIX ... update to test
# --path/--type/--title (FD-039)"), acknowledging the interface is
# unresolved. Testing against validate_instance.py directly exercises the
# actual rejection mechanism honestly instead of forcing a broken CLI call.
for f in "$NEG"/EN-*.yaml; do
  id="$(basename "$f" .yaml | cut -d- -f1-2)"
  assert_rejects "$id" python3 "$GATE" event "$SCHEMA" "$f"
done

# Local aggregate, in the same "NEGATIVE OK n/n" grammar DoD-3 uses, but for
# THIS suite's own ten envelope fixtures (not to be confused with
# tools/records/test-negative.sh's ten RULE-level fixtures from L4-T224,
# which the task's literal citation of "validate-schemas.sh --negative"
# seems to have meant instead - that script proves a different ten cases).
total=0; rejected=0
for f in "$NEG"/EN-*.yaml; do
  total=$((total+1))
  python3 "$GATE" event "$SCHEMA" "$f" >/dev/null 2>&1 || rejected=$((rejected+1))
done
assert_eq "EN-CHARTER" "NEGATIVE OK $total/$total" "NEGATIVE OK $rejected/$total"

# Positive control: the valid envelope IS accepted, or the negatives prove nothing.
assert_exit "EN-CONTROL" 0 python3 "$GATE" event "$SCHEMA" "$CP/tools/records/fixtures/valid/verbatim/event.yaml"

summary "02-envelope"
