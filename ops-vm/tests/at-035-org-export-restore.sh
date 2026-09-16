#!/usr/bin/env bash
# ops-vm/tests/at-035-org-export-restore.sh
# AT-035 - spec 100.3 and 45.3 (D80). Static half proves the export's four
# declared properties; the live half (restore to an independent
# environment, decrypt, wipe) is ASSISTED and is executed by a named human.
#
# Real path (verified on disk): ops-vm/export/run-org-export.sh (L5-04-13),
# not the runbook's draft ops-vm/org-export/export.sh, which no task writes
# (lanes/L5-98-DEEP-REVIEW.md B-05).
set -uo pipefail
. access/tests/lib/assert.sh
EXP=ops-vm/export/run-org-export.sh
if [ ! -x "$EXP" ]; then l5_indeterminate "AT-035/static" "PRE-N missing or not executable: $EXP"; l5_exit; fi
if grep -qiE 'graphql' "$EXP"; then
  l5_pass "AT-035/static-projects-graphql-dump"
else
  l5_fail "AT-035/static-projects-graphql-dump" "the export declares no separate Projects v2 GraphQL dump; spec 45.3 forbids assuming boards are in the migration archive"
fi
if grep -qiE 'object.?lock|append.?only|write.?only' "$EXP"; then
  l5_pass "AT-035/static-write-only-object-locked"
else
  l5_fail "AT-035/static-write-only-object-locked" "the export declares no append-only, write-only credential against object-locked storage (spec 45.3)"
fi
if grep -qiE 'encrypt' "$EXP"; then
  l5_pass "AT-035/static-encrypted"
else
  l5_fail "AT-035/static-encrypted" "the export declares no encryption; spec 45.3 requires a key held outside GitHub"
fi
KEY=assets/inventory/org-export-encryption-key.yaml
TOK=assets/inventory/machine-credential-organisation-export-token.yaml
if [ -f "$KEY" ] && [ -f "$TOK" ]; then
  l5_pass "AT-035/static-inventory-entries"
else
  l5_fail "AT-035/static-inventory-entries" "the export key or its token has no asset entry (spec 45.3, 49.1)"
fi
WIN="$(yq -r '.checks[] | select(.check_id == "AT-035") | .revalidate_after_days' access/tests/coverage.yaml)"
if [ "$WIN" = "90" ]; then
  l5_pass "AT-035/static-90-day-window"
else
  l5_fail "AT-035/static-90-day-window" "the restore-test clock is ${WIN}d; D80 sets a rolling 90-day discipline"
fi
bash access/tests/lib/verify-evidence.sh AT-035
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-035/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-035/live"
else
  l5_fail "AT-035/live" "evidence verification failed"
fi
l5_exit
