#!/usr/bin/env bash
# Section 45.3 negative test: the credential that writes the export cannot read,
# overwrite or delete what previous runs wrote. A credential that can read or
# delete FAILS this check.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/export/storage.env
set -a; . ops-vm/export/storage.env; set +a
export AWS_ACCESS_KEY_ID="$EXPORT_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$EXPORT_SECRET_ACCESS_KEY"
probe="org-export/_credential-probe-$(date -u +%s)"
fail=0
aws --endpoint-url "$EXPORT_ENDPOINT" s3api put-object \
    --bucket "$EXPORT_BUCKET" --key "$probe" --body /dev/null >/dev/null \
  || { echo "write DENIED - the credential cannot write"; fail=1; }
if aws --endpoint-url "$EXPORT_ENDPOINT" s3api get-object \
      --bucket "$EXPORT_BUCKET" --key "$probe" /dev/null >/dev/null 2>&1; then
  echo "read ALLOWED - credential is not write-only"; fail=1
else echo "read denied OK"; fi
if aws --endpoint-url "$EXPORT_ENDPOINT" s3api delete-object \
      --bucket "$EXPORT_BUCKET" --key "$probe" >/dev/null 2>&1; then
  echo "delete ALLOWED - credential is not append-only"; fail=1
else echo "delete denied OK"; fi
if [ "$fail" -eq 0 ]; then echo "EXPORT-CREDENTIAL: PASS"; else echo "EXPORT-CREDENTIAL: FAIL"; exit 1; fi
