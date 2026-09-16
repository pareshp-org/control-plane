#!/usr/bin/env bash
# ops-vm/layer-b/manifest/verify-checksum-manifest.sh
# Section 45.4 integrity check: decrypt-plus-checksum-manifest,
# "without opening any document".
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
OUT="$MNT/CHECKSUMS.sha256"
[ -f "$OUT" ] || { echo "MANIFEST_MISSING"; exit 1; }
mountpoint -q "$MNT" || { echo "STORE_NOT_DECRYPTED"; exit 1; }
cd "$MNT"
if sha256sum -c --quiet "$OUT"; then
  echo "MANIFEST_VERIFIED $(cat "$OUT.count") files"
else
  echo "MANIFEST_MISMATCH"; exit 1
fi
