#!/usr/bin/env bash
# ops-vm/layer-b/selfview/contest-note.sh <subject> <item_id> <note_file>
# Section 90.6: "a person may attach a contest note to any item in their
# self-view. The note is routed to the Founder and is captured as data feeding
# the employee-disagreement dimension of the KPI calibration review (84.5).
# Contesting evidence is never penalised."
set -euo pipefail
SUBJECT="${1:?subject}"; ITEM="${2:?item_id}"; NOTE="${3:?note_file}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
DIR="$MNT/contests/$SUBJECT"; mkdir -p "$DIR"; chmod 700 "$DIR"
ID="$(openssl rand -hex 8)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$DIR/$ID.yaml" <<REC
contest_id: "$ID"
subject: "$SUBJECT"
item_id: "$ITEM"
at: "$STAMP"
note_path: "$DIR/$ID.note"
feeds: "Section 84.5 employee-disagreement dimension"
penalised: false
REC
cp "$NOTE" "$DIR/$ID.note"; chmod 600 "$DIR/$ID.yaml" "$DIR/$ID.note"
# The route carries the fact of a contest, never its text (Section 90.2).
curl -sS -X POST "$TEAM_CHANNEL_WEBHOOK" \
  -F "channels=founder" \
  -F "text=A self-view item was contested. contest_id=$ID item_id=$ITEM" >/dev/null
echo "CONTEST_RECORDED $ID"
