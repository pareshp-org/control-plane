#!/usr/bin/env bash
# ===========================================================================
# THE DIGEST INVARIANT
# MultiProduct_MasterSpec_v4.0.md Section 32 (lines 2803-2828):
#   "the digest deployed to production must be byte-identical to the one
#    verified in staging. CI rejects any production deployment where the
#    requested digest differs from the digest that passed staging verification."
# Section 33.4 (lines 2887-2912) restates it as a P0 pipeline property.
# Invariant 22 (line 9483): the production artifact is the same digest
#   verified in staging. Never rebuilt.
# Section 96.6 row S18 (L8835) / D78 (L10172): for a platform-rebuild
#   product the recorded identity stands in for the digest here.
# Record shape: Section 97.2 (L8907).
#
# usage: assert-staging-verified-identity.sh <records_dir> <product> <identity_mode> <requested_identity>
#   exit 0 -> DIGEST_INVARIANT_OK
#   exit 1 -> any refusal; the first token of stdout is the verdict string
#   exit 2 -> usage error
# There is no third outcome and no "assume ok" branch.
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"
. "$HERE/lib/record-read.sh"

if [ "$#" -ne 4 ]; then
  echo "USAGE_ERROR assert-staging-verified-identity.sh <records_dir> <product> <identity_mode> <requested_identity>"
  exit 2
fi
RECORDS_DIR="$1"; PRODUCT="$2"; MODE="$3"; REQ="$4"

VERDICT="$(identity_guard "$MODE" "$REQ")" || { echo "$VERDICT"; exit 1; }

STORE="$RECORDS_DIR/records/deployments"
if [ ! -d "$STORE" ]; then
  echo "RECORDS_STORE_ABSENT path=$STORE"
  exit 1
fi

MATCH=""
CANDIDATES=""
SEEN=0

while IFS= read -r f; do
  [ -n "$f" ] || continue
  record_filename_ok "$f" || { echo "RECORD_FILENAME_INVALID file=$f"; exit 1; }
  p="$(record_key "$f" product)" || { echo "RECORD_UNPARSEABLE file=$f key=product"; exit 1; }
  [ "$p" = "$PRODUCT" ] || continue
  SEEN=$((SEEN + 1))
  sv="$(record_key "$f" staging_verified)" || { echo "RECORD_UNPARSEABLE file=$f key=staging_verified"; exit 1; }
  sr="$(record_key "$f" smoke_result)"     || { echo "RECORD_UNPARSEABLE file=$f key=smoke_result"; exit 1; }
  id="$(record_key "$f" digest)"           || { echo "RECORD_UNPARSEABLE file=$f key=digest"; exit 1; }
  [ "$sv" = "true" ] || continue
  [ "$sr" = "pass" ] || continue
  CANDIDATES="$CANDIDATES $id"
  if [ "$id" = "$REQ" ]; then
    MATCH="$f"
  fi
done < <(find "$STORE" -type f -name '*.yaml' | LC_ALL=C sort)

if [ -n "$MATCH" ]; then
  echo "DIGEST_INVARIANT_OK product=$PRODUCT mode=$MODE identity=$REQ record=$MATCH"
  exit 0
fi

if [ -z "$CANDIDATES" ]; then
  echo "NO_STAGING_VERIFIED_RECORD product=$PRODUCT requested=$REQ records_for_product=$SEEN"
  exit 1
fi

echo "DIGEST_INVARIANT_VIOLATION product=$PRODUCT requested=$REQ staging_verified=[$CANDIDATES ]"
exit 1
