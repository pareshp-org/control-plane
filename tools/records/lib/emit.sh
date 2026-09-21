#!/usr/bin/env bash
# tools/records/lib/emit.sh — the single record/event emission primitive of lane L4.
# Master Spec v4.0: 97.1 line 8839, 97.2 lines 8867/8871/8890, 97.3 lines 8929-8947,
# invariant 48 line 9516. Source this file; do not execute it.
# Optional: EMIT_SCHEMA=<file in schemas/records/>, EMIT_OCCURRED_AT=<UTC with offset>.
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
EMIT_TAXONOMY="$CP_ROOT/metrics/taxonomy/event-types.yaml"
EMIT_VALIDATOR="$CP_ROOT/tools/records/lib/validate_instance.py"

emit_now() { date -u +%Y-%m-%dT%H:%M:%S+00:00; }
emit_day() { date -u +%Y-%m-%d; }

emit_schema_path() {
  if [ -n "${EMIT_SCHEMA:-}" ]; then echo "$CP_ROOT/schemas/records/$EMIT_SCHEMA"; else echo "-"; fi
}

# emit_type_known <event_type> -- shape-independent token search of the taxonomy artifact.
emit_type_known() {
  if [ ! -f "$EMIT_TAXONOMY" ]; then
    echo "EMIT FAIL taxonomy-absent $EMIT_TAXONOMY" >&2; return 1
  fi
  if grep -qE "(^|[^A-Za-z0-9_])$1([^A-Za-z0-9_]|\$)" "$EMIT_TAXONOMY"; then return 0; fi
  echo "EMIT FAIL unknown-event-type $1" >&2; return 1
}

# emit_record <store> <id> <body-file>   -> prints the written path
emit_record() {
  emit_store="$1"; emit_id="$2"; emit_body="$3"
  emit_dir="$CPR_ROOT/records/$emit_store"
  if [ ! -d "$emit_dir" ]; then echo "EMIT FAIL no-store $emit_store" >&2; return 1; fi
  emit_out="$emit_dir/$emit_id.yaml"
  if [ -e "$emit_out" ]; then echo "EMIT FAIL overwrite-refused $emit_out" >&2; return 1; fi
  if ! python3 "$EMIT_VALIDATOR" record "$(emit_schema_path)" "$emit_body" >&2; then
    echo "EMIT FAIL invalid-record $emit_body" >&2; return 1
  fi
  cp "$emit_body" "$emit_out" || return 1
  echo "$emit_out"
}

# emit_event <event_type> <actor> <product> <subject_ref> <payload-file|-> -> prints the path
emit_event() {
  emit_et="$1"; emit_actor="$2"; emit_product="$3"; emit_subject="$4"; emit_payload="$5"
  emit_type_known "$emit_et" || return 1
  emit_d="$(emit_day)"; emit_edir="$CPR_ROOT/events/$emit_d"
  mkdir -p "$emit_edir"
  emit_seq="$(printf '%06d' "$(( $(find "$emit_edir" -maxdepth 1 -name 'EVT-*.yaml' | wc -l) + 1 ))")"
  emit_eid="EVT-$emit_d-$emit_seq"; emit_eout="$emit_edir/$emit_eid.yaml"
  if [ -e "$emit_eout" ]; then echo "EMIT FAIL overwrite-refused $emit_eout" >&2; return 1; fi
  {
    printf 'event_schema_version: 1\n'
    printf 'event_id: %s\n' "$emit_eid"
    printf 'event_type: %s\n' "$emit_et"
    printf 'occurred_at: %s\n' "${EMIT_OCCURRED_AT:-$(emit_now)}"
    printf 'recorded_at: %s\n' "$(emit_now)"
    printf 'actor: %s\n' "$emit_actor"
    printf 'product: %s\n' "$emit_product"
    printf 'subject_ref: %s\n' "$emit_subject"
    printf 'payload:\n'
    if [ "$emit_payload" = "-" ]; then printf '  {}\n'; else sed 's/^/  /' "$emit_payload"; fi
  } > "$emit_eout"
  if ! EMIT_SCHEMA="event.envelope.schema.json" python3 "$EMIT_VALIDATOR" event \
        "$CP_ROOT/schemas/records/event.envelope.schema.json" "$emit_eout" >&2; then
    rm -f "$emit_eout"; echo "EMIT FAIL invalid-event $emit_eid" >&2; return 1
  fi
  echo "$emit_eout"
}

emit_commit() { git -C "$CPR_ROOT" add -A && git -C "$CPR_ROOT" commit -q -m "$1"; }

# emit_pair <store> <id> <body-file> <event_type> <actor> <product> <payload-file|->
# Section 97.2 line 8871: writes the record AND appends the event. Never one without the other.
emit_pair() {
  emit_p_store="$1"; emit_p_id="$2"; emit_p_body="$3"; emit_p_et="$4"
  emit_p_actor="$5"; emit_p_product="$6"; emit_p_payload="$7"
  emit_p_rec="$(emit_record "$emit_p_store" "$emit_p_id" "$emit_p_body")" || return 1
  emit_p_ev="$(emit_event "$emit_p_et" "$emit_p_actor" "$emit_p_product" \
                "records/$emit_p_store/$emit_p_id.yaml" "$emit_p_payload")" || {
    rm -f "$emit_p_rec"
    echo "EMIT FAIL pair-rolled-back $emit_p_id" >&2; return 1; }
  emit_commit "records: $emit_p_id ($emit_p_store) + $(basename "$emit_p_ev" .yaml) [$emit_p_et]" || return 1
  echo "RECORD=$emit_p_rec"
  echo "EVENT=$emit_p_ev"
}
