#!/usr/bin/env bash
# Every stack component is pinned by digest. Invariant 85.
set -euo pipefail
ENVFILE="${1:-ops-vm/stack/versions.env}"
[ -f "$ENVFILE" ] || { echo "VERSIONS-PINNED: FAIL (no $ENVFILE)"; exit 1; }
bad=0
while IFS='=' read -r k v; do
  case "$k" in
    ''|\#*) continue ;;
    *_DIGEST) case "$v" in sha256:*) ;; *) echo "unpinned: $k"; bad=1 ;; esac ;;
    *_IMAGE)  [ -n "$v" ] || { echo "empty: $k"; bad=1; } ;;
  esac
done < "$ENVFILE"
if [ "$bad" -eq 0 ]; then echo "VERSIONS-PINNED: PASS"; else echo "VERSIONS-PINNED: FAIL"; exit 1; fi
