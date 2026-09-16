#!/usr/bin/env bash
# ops-vm/layer-b/selfview/deliver-selfview.sh <github_login> <session_id>
# Section 90.6: "The deliverer is the Founder session, which sends the encrypted
# document over the existing team channel; the encryption is what makes that
# channel acceptable."
set -euo pipefail
SUBJECT="${1:?github_login}"; SESSION="${2:?session_id}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
ACTOR="${LAYERB_SESSION_ACTOR:-}"
[ -n "$ACTOR" ] || { echo "SELFVIEW_NO_SESSION_ACTOR"; exit 2; }
DOC=$(ls -1t "$MNT/documents/$SUBJECT"/*.selfview.asc 2>/dev/null | head -1 || true)
[ -n "$DOC" ] || { echo "SELFVIEW_NOT_GENERATED $SUBJECT"; exit 3; }

# Refuse to deliver anything that is not armoured ciphertext.
head -1 "$DOC" | grep -q 'BEGIN PGP MESSAGE' || { echo "SELFVIEW_NOT_ENCRYPTED"; exit 4; }
# Refuse if any plaintext remains in the subject's directory.
if find "$MNT/documents/$SUBJECT" -name '*.plain' | grep -q .; then
  echo "SELFVIEW_PLAINTEXT_PRESENT"; exit 5
fi

curl -sS -X POST "$TEAM_CHANNEL_WEBHOOK" \
  -F "channels=$SUBJECT" \
  -F "file=@$DOC" \
  -F "initial_comment=Your self-view. Encrypted to the public half you registered." >/dev/null

/srv/layerb/config/accesslog/record-access.sh \
  "$ACTOR" "$SUBJECT" layer-b-s-delivery deliver "$SESSION" >/dev/null
echo "SELFVIEW_DELIVERED $SUBJECT"
