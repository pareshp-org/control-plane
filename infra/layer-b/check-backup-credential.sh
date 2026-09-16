#!/usr/bin/env bash
# infra/layer-b/check-backup-credential.sh
# Proves the backup credential is append-only and write-only, and that the
# target is object-locked and versioned. Every negative below MUST fail.
set -euo pipefail
B=layerb-backups
P=layerb-backup-writer
FAILS=0
note() { echo "BKP_FAIL $1"; FAILS=$((FAILS+1)); }

# The backup job's own source is checked first: it needs no host at all, and
# gating it behind a live-host probe would mean this repository-side defect
# could never be caught in an environment with no layerb-host yet.
if grep -nE 's3 (ls|cp s3://|rm|sync)' infra/layer-b/backup-run.sh | grep -v 'aws s3 cp "' >/dev/null 2>&1; then
  note "backup job contains a read or delete verb"
fi

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "BKP_INDETERMINATE layerb-host unreachable ($FAILS static finding(s) above)"
  [ "$FAILS" -eq 0 ] && exit 2 || exit 1
fi

# Positive: it can write.
ssh layerb-host "echo canary | aws s3 cp - s3://$B/_canary/$(date -u +%s).txt --profile $P" >/dev/null 2>&1 \
  || note "credential cannot write"

# Negative: it cannot read.
if ssh layerb-host "aws s3 ls s3://$B/ --profile $P" >/dev/null 2>&1; then note "credential can list/read"; fi

# Negative: it cannot delete.
if ssh layerb-host "aws s3 rm s3://$B/_canary/ --recursive --profile $P" >/dev/null 2>&1; then note "credential can delete"; fi

# Target properties, checked with the auditor profile, not the writer.
lock=$(ssh layerb-host "aws s3api get-object-lock-configuration --bucket $B --profile layerb-backup-auditor --query 'ObjectLockConfiguration.ObjectLockEnabled' --output text" 2>/dev/null || echo NONE)
[ "$lock" = "Enabled" ] || note "object lock is $lock, expected Enabled"
ver=$(ssh layerb-host "aws s3api get-bucket-versioning --bucket $B --profile layerb-backup-auditor --query 'Status' --output text" 2>/dev/null || echo NONE)
[ "$ver" = "Enabled" ] || note "versioning is $ver, expected Enabled"

if [ "$FAILS" -eq 0 ]; then echo "BKP_OK 6/6"; else echo "BKP_FAILED $FAILS"; exit 1; fi
