#!/usr/bin/env bash
# escalate-digest-mismatch.sh - turn sweep findings into the Blocking-drift
# event that Section 92.11 (line 8276) requires before anything may page anyone.
#
# Spec: Section 41.2 line 3729 ("any mismatch is a P0 investigation");
# Section 53.2 line 4697 (Level 4, Block); Section 92.11 line 8276 (the closed
# push list); Section 97.3 lines 8931-8944 (the event envelope).
#
# Chooses no severity. Writes no incident record. Names no channel.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"
# This script's own runtime contract fixes every refusal here as an input
# error, exit 2 — distinct from common.sh's generic exit 1 default and from
# this script's own exit 3 (findings present). Redefined locally after
# sourcing, same as L2-T508's build-deployment-record.sh.
ev_die() { printf '%s %s: %s\n' "$EV_FAIL_PREFIX" "$1" "$2" >&2; exit 2; }
ev_require_cmd python3

FINDINGS=""; TYPES=""; EVENT_ID=""; ACTOR=""; RUN_URL=""; OUT_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --findings)    FINDINGS="${2:-}"; shift 2 ;;
    --event-types) TYPES="${2:-}";    shift 2 ;;
    --event-id)    EVENT_ID="${2:-}"; shift 2 ;;
    --actor)       ACTOR="${2:-}";    shift 2 ;;
    --run-url)     RUN_URL="${2:-}";  shift 2 ;;
    --out-dir)     OUT_DIR="${2:-}";  shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
for pair in FINDINGS:--findings TYPES:--event-types EVENT_ID:--event-id \
            ACTOR:--actor RUN_URL:--run-url OUT_DIR:--out-dir; do
  var="${pair%%:*}"; flag="${pair##*:}"
  [ -n "${!var}" ] || ev_die "BAD_ARG" "$flag is required"
done
ev_require_file "$FINDINGS" "FINDINGS_ABSENT"
ev_require_file "$TYPES" "EVENT_TYPES_ABSENT"
printf '%s' "$EVENT_ID" | grep -qE '^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$' \
  || ev_die "ID_MALFORMED" "event id must match EVT-YYYY-MM-DD-NNNNNN: $EVENT_ID"

python3 "$HERE/lib/build-drift-event.py" \
  --findings "$FINDINGS" --event-types "$TYPES" --event-id "$EVENT_ID" \
  --actor "$ACTOR" --run-url "$RUN_URL" --now "$(ev_now_utc)" --out-dir "$OUT_DIR"
