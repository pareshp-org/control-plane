#!/usr/bin/env bash
# The Phase 1 access completion check (spec Section 98.2), offline.
# Runs every access/** checker in dependency order, then the eight offline
# assertions. No credentials, no organisation, no network.
set -eu
cd "$(git rev-parse --show-toplevel)"

python access/tools/validate_access_config.py         > /dev/null
python access/tools/check_permission_semantics.py     > /dev/null
python access/tools/check_team_derivation.py          > /dev/null
python access/tools/check_no_enterprise_dependency.py > /dev/null
python access/tools/check_arming_order.py             > /dev/null
bash   access/codeowners/test_generate_codeowners.sh  > /dev/null

# The arming gate must REJECT the forbidden order. A gate that accepts it is
# decoration, and the whole check is worthless (D101).
if python access/tools/check_arming_order.py \
     --config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1; then
  echo "PHASE1-ACCESS-CHECK: FAIL - the arming gate accepted a forbidden order" >&2
  exit 1
fi

python access/checks/phase1_assertions.py
