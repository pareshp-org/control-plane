#!/usr/bin/env bash
# ops-vm/layer-b/manifest/generate-checksum-manifest.sh
# Writes the checksum manifest over the mounted store.
# It hashes bytes. It opens, parses and renders nothing (Section 45.4).
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
OUT="$MNT/CHECKSUMS.sha256"
cd "$MNT"
# Exclude the manifest itself, its count sidecar, AND the ".tmp" name this
# script is about to write to: the shell opens/truncates "$OUT.tmp" for the
# redirect below before the pipeline runs, so an unexcluded ".tmp" pattern
# lets find(1) see (and hash) the manifest's own half-written output -
# caught by running this against a real fixture, not assumed correct.
find . -type f \
  ! -name 'CHECKSUMS.sha256' ! -name 'CHECKSUMS.sha256.count' ! -name 'CHECKSUMS.sha256.tmp' \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum > "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
wc -l < "$OUT" | tr -d ' ' > "$OUT.count"
echo "MANIFEST_WRITTEN $(wc -l < "$OUT" | tr -d ' ') files"
