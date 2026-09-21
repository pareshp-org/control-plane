#!/usr/bin/env bash
# infra/layer-b/backup-run.sh - runs on layerb-host.
# Encrypts the store snapshot and writes it once. It never reads or deletes.
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

tar -C "$MNT" -cf "$TMP/layerb-$STAMP.tar" .
openssl enc -aes-256-cbc -pbkdf2 -salt \
  -in  "$TMP/layerb-$STAMP.tar" \
  -out "$TMP/layerb-$STAMP.tar.enc" \
  -pass file:/srv/layerb/secrets/backup_encryption_key
rm -f "$TMP/layerb-$STAMP.tar"

# Write-only put. No list, no get, no delete anywhere in this job.
aws s3 cp "$TMP/layerb-$STAMP.tar.enc" \
  "s3://layerb-backups/$STAMP/layerb.tar.enc" \
  --profile layerb-backup-writer

size=$(stat -c %s "$TMP/layerb-$STAMP.tar.enc")
[ "$size" -gt 0 ] || { echo "BACKUP_EMPTY"; exit 1; }
echo "BACKUP_OK $STAMP $size"
