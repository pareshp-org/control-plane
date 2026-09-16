#!/usr/bin/env bash
# Lane 2 - SBOM presence beside the artifact digest.
# Section 48.3 (lines 4317-4320): every production artifact build emits an SBOM
# beside the artifact digest, same pipeline step, same storage discipline, same
# immutability. Retrieval is by digest, so the SBOM cannot drift from the
# artifact it describes.
# usage: assert-sbom-beside-digest.sh <image_ref_with_digest> <out_file>
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "USAGE_ERROR assert-sbom-beside-digest.sh <image_ref_with_digest> <out_file>"
  exit 2
fi
REF="$1"; OUT="$2"

printf '%s' "$REF" | grep -qE '@sha256:[0-9a-f]{64}$' \
  || { echo "IDENTITY_FORMAT_INVALID mode=digest value=$REF"; exit 1; }

if ! docker buildx imagetools inspect "$REF" --format '{{ json .SBOM }}' > "$OUT" 2>/dev/null; then
  echo "ARTIFACT_NOT_RESOLVABLE ref=$REF"
  echo "DO_NOT_REBUILD invariant=23 spec=Section-46.2 action=wait-for-the-registry"
  exit 1
fi

CONTENT="$(tr -d ' \t\r\n' < "$OUT")"
case "$CONTENT" in
  ''|'null'|'{}'|'[]')
    echo "SBOM_MISSING ref=$REF"
    exit 1
    ;;
esac

BYTES="$(wc -c < "$OUT" | tr -d ' ')"
echo "SBOM_PRESENT ref=$REF file=$OUT bytes=$BYTES"
exit 0
