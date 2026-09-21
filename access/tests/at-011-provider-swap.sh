#!/usr/bin/env bash
# access/tests/at-011-provider-swap.sh
# AT-011 - spec 100.1, 35.2, 35.3. The approved runtime list is
# CONFIGURATION: the names live in one place and nowhere else, so a provider
# change touches nothing else.
#
# Real layout (verified on disk): one file per runtime under
# access/ai-toolchain/runtimes/<id>.yaml, validated by
# access/ai-toolchain/validate_toolchain.py -- not the runbook's draft
# single-file access/ai-runtime/approved-runtimes.yaml, which no task writes
# (lanes/L5-98-DEEP-REVIEW.md B-05, same one-file-per-item pattern PARTITION
# rule 3 already established for notify/routing/).
set -uo pipefail
. access/tests/lib/assert.sh
RUNTIMES_DIR=access/ai-toolchain/runtimes
if [ ! -d "$RUNTIMES_DIR" ]; then l5_indeterminate "AT-011" "PRE-M missing: $RUNTIMES_DIR"; l5_exit; fi
IDS="$(yq -r '.runtime_id' "$RUNTIMES_DIR"/*.yaml 2>/dev/null | sort -u)"
MISSING=""
for r in "claude-code" "codex" "antigravity" "cursor" "kilo-code" "hermes-agent"; do
  echo "$IDS" | grep -qxF "$r" || MISSING="$MISSING [$r]"
done
if [ -z "$MISSING" ]; then
  l5_pass "AT-011/list-is-complete"
else
  l5_fail "AT-011/list-is-complete" "approved runtimes missing from the list:$MISSING (spec 35.2)"
fi
if grep -rqF '8e9459c97f707047be5915a5c8b4c503756daa9b' "$RUNTIMES_DIR/hermes-agent.yaml" 2>/dev/null; then
  l5_pass "AT-011/hermes-pinned"
else
  l5_fail "AT-011/hermes-pinned" "Hermes Agent is not pinned at the commit spec 35.2 names (D69)"
fi
# Negative: no runtime name may appear outside the list. A name anywhere
# else is the coupling spec 35.3 calls a defect to be removed.
COUPLED="$(grep -rniE 'claude code|antigravity|kilo code' \
            .github/workflows access/model access/branch-protection access/permission-model \
            access/codeowners infra ops-vm notify 2>/dev/null \
          | grep -v "$RUNTIMES_DIR" || true)"
if [ -z "$COUPLED" ]; then
  l5_pass "AT-011/no-coupling-outside-the-list"
else
  l5_fail "AT-011/no-coupling-outside-the-list" "a runtime name is referenced outside the approved-runtime list: $COUPLED"
fi
l5_exit
