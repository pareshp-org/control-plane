#!/usr/bin/env bash
# access/tests/lane5.sh
# Runs every Lane 5 test script in every Lane-5-owned test path.
#
# Fix for a confirmed defect (lanes/L5-98-DEEP-REVIEW.md B-04): the runner
# itself lives at access/tests/*.sh, which the naive `for f in "$d"/*.sh`
# glob over access/tests also matches, so the runner would invoke itself
# forever. It is excluded here by name, alongside check-coverage.sh (a
# manifest check, not a test) and anything under a lib/ directory.
#
# Also distinguishes INCOMPLETE (rc=2 -- an ASSISTED/HUMAN-GATED check
# correctly awaiting human evidence, per Section 1.1's "a missing evidence
# file is not a failure of the test") from FAIL (rc=1 or other non-zero): the
# doctrine that INCOMPLETE is never FAIL only holds if the runner itself
# keeps the two apart.
set -uo pipefail
RC=0
INCOMPLETE=0
for d in access/tests infra/tests ops-vm/tests notify/tests assets/tests; do
  [ -d "$d" ] || continue
  for f in "$d"/*.sh; do
    [ -e "$f" ] || continue
    case "$f" in
      */lane5.sh|*/check-coverage.sh) continue ;;
    esac
    echo "--- $f"
    if bash "$f"; then
      :
    else
      rc=$?
      if [ "$rc" -eq 2 ]; then
        INCOMPLETE=$((INCOMPLETE+1))
      else
        RC=1
      fi
    fi
  done
done
if [ "$RC" -eq 0 ]; then
  if [ "$INCOMPLETE" -eq 0 ]; then
    echo "LANE5 SUITE OK"
  else
    echo "LANE5 SUITE OK (INCOMPLETE=$INCOMPLETE)"
  fi
else
  echo "LANE5 SUITE FAIL"
fi
exit "$RC"
