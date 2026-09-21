#!/usr/bin/env bash
# generate-sbom.sh — SBOM generator stub (FD-107/PFD-027)
# Generates a Software Bill of Materials for a product release
# Usage: bash scripts/security/generate-sbom.sh --product <id> --tag <version>
# DECIDED (FD-107, 2026-09-08): Syft, spdx-json output format. This stub
# emits a minimal SPDX 2.3 document so downstream consumers (e.g.
# protocol/08 CP-0603 `check-sbom --require-format spdx-json`) see the
# correct shape. Replace with a real Syft invocation, sha256-pinned per
# PFD-027 Option A, in Phase 1 — pinning is still open pending L0 supplying
# the container digest.
set -euo pipefail

PRODUCT=""
TAG=""
FORMAT="spdx-json"
OUTDIR="records/sbom"

while [[ $# -gt 0 ]]; do
  case $1 in
    --product) PRODUCT="$2"; shift 2;;
    --tag) TAG="$2"; shift 2;;
    --format) FORMAT="$2"; shift 2;;
    --outdir) OUTDIR="$2"; shift 2;;
    *) shift;;
  esac
done

[[ -z "$PRODUCT" || -z "$TAG" ]] && {
  echo "Usage: $0 --product <id> --tag <version> [--format spdx-json] [--outdir <dir>]"
  exit 2
}

if [[ "$FORMAT" != "spdx-json" ]]; then
  echo "NOTE: --format $FORMAT requested, but FD-107 decided spdx-json; emitting spdx-json anyway."
fi

mkdir -p "$OUTDIR"
OUTFILE="$OUTDIR/${PRODUCT}-${TAG}.sbom.json"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== SBOM Generation: $PRODUCT@$TAG (spdx-json, FD-107) ==="

cat > "$OUTFILE" <<EOF
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "$PRODUCT-$TAG",
  "documentNamespace": "https://multiproduct.local/spdx/$PRODUCT/$TAG",
  "creationInfo": {
    "created": "$TIMESTAMP",
    "creators": [
      "Tool: multiproduct-sbom-stub-0.1.0"
    ]
  },
  "packages": []
}
EOF

echo "SBOM written: $OUTFILE"
echo "NOTE: This is a stub SBOM (SPDX 2.3 / spdx-json, no packages enumerated)."
echo "Implement with Syft in L2 Phase 1 per FD-107 (PFD-027); digest pinning still open."
