#!/usr/bin/env bash
# ops-vm/layer-b/accesslog/record-access.sh
# Usage: record-access.sh <actor> <subject> <surface> <action> <session_id>
# One file per event. Never appends to a shared file.
set -euo pipefail
ACTOR="${1:?actor}"; SUBJECT="${2:?subject}"; SURFACE="${3:?surface}"
ACTION="${4:?action}"; SESSION="${5:?session_id}"
case "$SURFACE" in layer-b-m|layer-b-s-generation|layer-b-s-delivery) ;; *) echo "BAD_SURFACE"; exit 1 ;; esac
case "$ACTOR" in *"[bot]"*|*-bot|reconciler|provisioning-cli|records-writer)
  echo "MACHINE_IDENTITY_REFUSED"; exit 1 ;; esac
DIR="${LAYERB_MNT:-/srv/layerb/encrypted}/accesslog"
mkdir -p "$DIR"; chmod 700 "$DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
ID="$(openssl rand -hex 8)"
cat > "$DIR/$TS-$ID.yaml" <<REC
event_id: "$ID"
actor: "$ACTOR"
subject: "$SUBJECT"
at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
surface: "$SURFACE"
session_id: "$SESSION"
action: "$ACTION"
REC
chmod 600 "$DIR/$TS-$ID.yaml"
echo "ACCESS_RECORDED $ID"
