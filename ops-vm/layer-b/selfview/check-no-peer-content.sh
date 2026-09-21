#!/usr/bin/env bash
# ops-vm/layer-b/selfview/check-no-peer-content.sh <plaintext> <subject_login>
# Section 92.8: "No peer data, no rankings, no other person's signals."
# Every registered login except the subject is a prohibited token in the document.
set -euo pipefail
DOC="${1:?document}"
SUBJECT="${2:?subject}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
HITS=0
for f in "$MNT"/pubkeys/*.asc; do
  [ -e "$f" ] || continue
  other=$(basename "$f" .asc)
  [ "$other" = "$SUBJECT" ] && continue
  if grep -qiw -- "$other" "$DOC"; then echo "PEER_TOKEN $other"; HITS=$((HITS+1)); fi
done
for word in rank ranking leaderboard percentile "compared to" "vs peers"; do
  if grep -qi -- "$word" "$DOC"; then echo "RANKING_TOKEN $word"; HITS=$((HITS+1)); fi
done
if [ "$HITS" -eq 0 ]; then echo "NO_PEER_CONTENT"; else echo "PEER_CONTENT $HITS"; exit 1; fi
