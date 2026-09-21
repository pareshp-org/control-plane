#!/usr/bin/env bash
# Published to lane L2 as the object-lock write primitive of the org-export
# workflow. Contract, exactly as L2 declared it:
#   one argument: a local file
#   writes to object-locked, versioned storage using WRITE_TOKEN
#   exits non-zero on failure
# Section 45.3: the credential that writes cannot read, overwrite or delete what
# previous runs wrote, and object lock means the event that compromises the
# exporter cannot destroy the history.
set -euo pipefail
SRC="${1:?usage: put.sh <local-file>}"
[ -f "$SRC" ] || { echo "EXPORT-PUT: FAIL (no such file: $SRC)"; exit 1; }
[ -n "${WRITE_TOKEN:-}" ] || { echo "EXPORT-PUT: FAIL-CLOSED (WRITE_TOKEN is empty)"; exit 1; }
: "${EXPORT_ENDPOINT:?EXPORT_ENDPOINT is required}"
: "${EXPORT_BUCKET:?EXPORT_BUCKET is required}"
: "${EXPORT_RETENTION_DAYS:?EXPORT_RETENTION_DAYS is required}"
key="org-export/$(date -u +%Y%m%dT%H%M%SZ)-$(basename "$SRC")"
AWS_ACCESS_KEY_ID="${EXPORT_ACCESS_KEY_ID:-}" \
AWS_SECRET_ACCESS_KEY="$WRITE_TOKEN" \
aws --endpoint-url "$EXPORT_ENDPOINT" s3api put-object \
    --bucket "$EXPORT_BUCKET" --key "$key" --body "$SRC" \
    --object-lock-mode COMPLIANCE \
    --object-lock-retain-until-date "$(date -u -d "+$EXPORT_RETENTION_DAYS days" +%Y-%m-%dT%H:%M:%SZ)" \
  || { echo "EXPORT-PUT: FAIL (write refused)"; exit 1; }
echo "EXPORT-PUT: OK $key"
