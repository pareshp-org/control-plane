#!/usr/bin/env bash
# ops-vm/layer-b/selfview/rekey-check.sh
# Section 90.6: "Registered material is re-keyed annually, and immediately on a
# lost-device or compromised-workstation report under Section 43.4."
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
STALE=0
for f in "$MNT"/pubkeys/*.asc; do
  [ -e "$f" ] || continue
  age_days=$(( ( $(date -u +%s) - $(stat -c %Y "$f") ) / 86400 ))
  if [ "$age_days" -gt 365 ]; then
    echo "PUBKEY_STALE $(basename "$f" .asc) ${age_days}d"; STALE=$((STALE+1))
  fi
done
if [ "$STALE" -eq 0 ]; then echo "REKEY_CURRENT 0 stale"; else echo "REKEY_STALE $STALE"; exit 1; fi
