#!/usr/bin/env bash
# Appends ONE event file to the records repository. Spec Section 97.3.
# One file per event, never a concurrent append to a shared period file.
# Envelope fields are binding: an event missing any is rejected at write time.
# Args: <event_type> <actor> <product> <subject_ref> <payload-yaml-or-empty>
set -euo pipefail
[ "$#" -ge 4 ] || { echo "FATAL: emit-event.sh needs 4 or 5 args" >&2; exit 1; }
EVENT_TYPE="$1"; ACTOR="$2"; PRODUCT="$3"; SUBJECT_REF="$4"; PAYLOAD="${5:-}"
: "${RECORDS_REPO:?FATAL: RECORDS_REPO unset}"
: "${RECORDS_WRITER_TOKEN:?FATAL: RECORDS_WRITER_TOKEN unset}"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DAY="$(date -u +%Y-%m-%d)"
EID="EVT-${DAY}-$(date -u +%H%M%S)-${RANDOM}"
WORK="$(mktemp -d)"
git -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" \
    clone --depth 1 "https://github.com/${RECORDS_REPO}.git" "$WORK/r" >/dev/null 2>&1
mkdir -p "$WORK/r/events/${DAY}"
{
  echo "event_schema_version: 1"
  echo "event_id: ${EID}"
  echo "event_type: ${EVENT_TYPE}"
  echo "occurred_at: ${NOW}"
  echo "recorded_at: ${NOW}"
  echo "actor: ${ACTOR}"
  echo "product: ${PRODUCT}"
  echo "subject_ref: ${SUBJECT_REF}"
  echo "payload:"
  if [ -n "$PAYLOAD" ]; then printf '%s\n' "$PAYLOAD" | sed 's/^/  /'; else echo "  {}"; fi
} > "$WORK/r/events/${DAY}/${EID}.yaml"
git -C "$WORK/r" add "events/${DAY}/${EID}.yaml"
git -C "$WORK/r" -c user.name="records-writer" -c user.email="records-writer@invalid" \
    -c commit.gpgsign=true commit -S -m "event ${EVENT_TYPE} ${EID}"
git -C "$WORK/r" -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" push origin HEAD
echo "$EID"
