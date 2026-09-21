#!/usr/bin/env bash
# build-deployment-record.sh - deployment record and event payload builder.
#
# Spec: Section 97.2 (lines 8843-8926) - the record store and its representative
# schema; line 8926 - "the deployment-record and event writes are required,
# failing steps". Section 97.3 (lines 8927-8953) - the binding event envelope.
# Section 97.1 line 8838 - every timestamp in UTC with its offset.
#
# This script BUILDS payloads. It never writes to a store, never names a
# secret and never constructs a path into the records or events trees - those
# are Lane 4's (PARTITION.md line 20) and are reached only through the write
# interface named in the records write-interface contract.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"
# This script's own runtime contract fixes every refusal here as an input
# error, exit 2 (matching evidence-query and verify-digest-chain) — distinct
# from common.sh's generic exit 1 default. Redefined locally after sourcing.
ev_die() { printf '%s %s: %s\n' "$EV_FAIL_PREFIX" "$1" "$2" >&2; exit 2; }
ev_require_cmd python3

MAP=""; TYPES=""; RECORD_ID=""; EVENT_ID=""; PRODUCT=""; ENVIRONMENT=""
DIGEST=""; COMMIT=""; RUN_URL=""; ACTOR=""; APPROVED_BY=""
STAGING_VERIFIED=""; SMOKE_RESULT=""; UAT_RECORD=""; OUT_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --map)              MAP="${2:-}";              shift 2 ;;
    --event-types)      TYPES="${2:-}";            shift 2 ;;
    --record-id)        RECORD_ID="${2:-}";        shift 2 ;;
    --event-id)         EVENT_ID="${2:-}";         shift 2 ;;
    --product)          PRODUCT="${2:-}";          shift 2 ;;
    --environment)      ENVIRONMENT="${2:-}";      shift 2 ;;
    --digest)           DIGEST="${2:-}";           shift 2 ;;
    --commit)           COMMIT="${2:-}";           shift 2 ;;
    --run-url)          RUN_URL="${2:-}";          shift 2 ;;
    --actor)            ACTOR="${2:-}";            shift 2 ;;
    --approved-by)      APPROVED_BY="${2:-}";      shift 2 ;;
    --staging-verified) STAGING_VERIFIED="${2:-}"; shift 2 ;;
    --smoke-result)     SMOKE_RESULT="${2:-}";     shift 2 ;;
    --uat-record)       UAT_RECORD="${2:-}";       shift 2 ;;
    --out-dir)          OUT_DIR="${2:-}";          shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
for pair in MAP:--map TYPES:--event-types RECORD_ID:--record-id EVENT_ID:--event-id \
            PRODUCT:--product ENVIRONMENT:--environment DIGEST:--digest COMMIT:--commit \
            RUN_URL:--run-url ACTOR:--actor OUT_DIR:--out-dir; do
  var="${pair%%:*}"; flag="${pair##*:}"
  [ -n "${!var}" ] || ev_die "BAD_ARG" "$flag is required"
done
ev_require_file "$MAP" "MAP_ABSENT"
ev_require_file "$TYPES" "EVENT_TYPES_ABSENT"

case "$ENVIRONMENT" in
  staging|production) ;;
  *) ev_die "ENVIRONMENT_UNRECOGNISED" "$ENVIRONMENT" ;;
esac

# Section 97.2 line 8896 prints DEP-2026-09-12-014; Section 97.3 line 8933
# prints EVT-2026-09-14-000317. The FORMAT is transcribed; the VALUE is minted
# by the allocator named in the records write-interface contract, never here.
printf '%s' "$RECORD_ID" | grep -qE '^DEP-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$' \
  || ev_die "ID_MALFORMED" "record id must match DEP-YYYY-MM-DD-NNN: $RECORD_ID"
printf '%s' "$EVENT_ID" | grep -qE '^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$' \
  || ev_die "ID_MALFORMED" "event id must match EVT-YYYY-MM-DD-NNNNNN: $EVENT_ID"

mkdir -p "$OUT_DIR"
NOW="$(ev_now_utc)"

python3 "$HERE/lib/build-payloads.py" \
  --map "$MAP" --event-types "$TYPES" \
  --record-id "$RECORD_ID" --event-id "$EVENT_ID" \
  --product "$PRODUCT" --environment "$ENVIRONMENT" --digest "$DIGEST" \
  --commit "$COMMIT" --run-url "$RUN_URL" --actor "$ACTOR" \
  --approved-by "${APPROVED_BY:-none}" \
  --staging-verified "${STAGING_VERIFIED:-false}" \
  --smoke-result "${SMOKE_RESULT:-none}" \
  --uat-record "${UAT_RECORD:-none}" \
  --now "$NOW" --out-dir "$OUT_DIR"

ev_ok "PAYLOADS_BUILT record=$OUT_DIR/record.yaml event=$OUT_DIR/event.yaml"
