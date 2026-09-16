#!/usr/bin/env bash
# ops-vm/layer-b/selfview/generate-selfview.sh
# Usage: generate-selfview.sh <github_login> <session_id>
# Runs on layerb-host, inside the Founder's credentialed session (Section 89.1).
# Plaintext exists only inside the encrypted store and is shredded before exit.
#
# This is the generator's ENVELOPE only (see the DECISION REQUIRED block in
# L5-03-10's task spec, escalation E-P3-01): the per-person view's CONTENT is
# subsystem P's, unassigned in PARTITION v1. This script renders whatever
# /srv/layerb/config/selfview/selfview.sql returns for exactly one subject; it
# composes no content of its own and joins to no other person's rows. Until P
# exists, the psql step below fails and this script stops there - correctly,
# not as a bug in this task.
set -euo pipefail
SUBJECT="${1:?github_login}"
SESSION="${2:?session_id}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
PUB="$MNT/pubkeys/$SUBJECT.asc"
OUTDIR="$MNT/documents/$SUBJECT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# Section 89.1: "the session is the Founder, not a bot."
ACTOR="${LAYERB_SESSION_ACTOR:-}"
[ -n "$ACTOR" ] || { echo "SELFVIEW_NO_SESSION_ACTOR"; exit 2; }
case "$ACTOR" in *"[bot]"*|*-bot|reconciler|provisioning-cli|records-writer)
  echo "MACHINE_IDENTITY_REFUSED"; exit 2 ;; esac

# Section 90.6: no public half, no document.
[ -f "$PUB" ] || { echo "SELFVIEW_NO_PUBKEY $SUBJECT"; exit 3; }

mkdir -p "$OUTDIR"; chmod 700 "$OUTDIR"
PLAIN="$OUTDIR/.$SUBJECT-$STAMP.plain"   # inside the store, never outside it
umask 077

# The per-person view is produced by the people-data store. This script renders
# whatever that view returns for exactly one subject; it composes no content of
# its own and joins to no other person's rows (subsystem P owns the content -
# see the DECISION REQUIRED block of this task).
psql "service=layerb_people" --no-align --tuples-only \
  -v subject="$SUBJECT" -f /srv/layerb/config/selfview/selfview.sql > "$PLAIN"

# Section 92.8: "No peer data, no rankings, no other person's signals."
/srv/layerb/config/selfview/check-no-peer-content.sh "$PLAIN" "$SUBJECT" || {
  shred -u "$PLAIN"; echo "SELFVIEW_PEER_CONTENT_REFUSED"; exit 4; }

ENC="$OUTDIR/$SUBJECT-$STAMP.selfview.asc"
gpg --batch --yes --trust-model always --armor \
    --recipient-file "$PUB" --encrypt --output "$ENC" "$PLAIN"
shred -u "$PLAIN"
chmod 600 "$ENC"

# Section 89.1: "Every generation run is logged in the Layer B access log."
/srv/layerb/config/accesslog/record-access.sh \
  "$ACTOR" "$SUBJECT" layer-b-s-generation generate "$SESSION" >/dev/null

echo "SELFVIEW_GENERATED $SUBJECT $STAMP"
