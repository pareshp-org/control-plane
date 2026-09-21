#!/usr/bin/env bash
# metrics/attention/selfcheck/run.sh
# Phase-4's own proof of the attention ledger. MasterSpec v4.0 Section 97.4 lines 8969-8981;
# Section 67.2 line 5592; Section 7.3 line 571.
# This is NOT tools/records/test/ and NOT metrics/attention/test-derivation.sh: those belong to
# L4-07-tests-and-runbook.md (tasks L4-P7-T09, L4-P7-T10) and are never created here.
# Expected values are fixed by L4-04-attention-ledger.md task L4-T412. Never edit one to make a
# run pass: a mismatch is a defect in derive.py, not in the fixture.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
PASS=0; FAIL=0
NORM='import sys,json;print(json.dumps(json.load(sys.stdin),sort_keys=True,separators=(",",":")))'
FNORM='import sys,json;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True,separators=(",",":")))'

check() {  # check <id> <want> <got>
  if [ "$2" = "$3" ]; then echo "PASS $1"; PASS=$((PASS+1));
  else echo "FAIL $1"; echo "  want: $2"; echo "  got : $3"; FAIL=$((FAIL+1)); fi
}

for c in 1 2 3 4 5 6 7; do
  got="$(python3 "$ATT/derive.py" --input "$HERE/input/sc-$c.yaml" --json 2>/dev/null \
         | python3 -c "$NORM" 2>/dev/null)"
  want="$(python3 -c "$FNORM" "$HERE/expected/sc-$c.json")"
  check "SC-$c" "$want" "$got"
done

if python3 "$ATT/derive.py" --input "$HERE/input/sc-8.yaml" --json >/dev/null 2>&1; then
  echo "FAIL SC-8 (a self-reported ritual flag was accepted)"; FAIL=$((FAIL+1))
else
  echo "PASS SC-8"; PASS=$((PASS+1))
fi

got9="$(python3 "$ATT/scheduled-availability.py" --person dev-c --date 2026-09-14 \
        --people "$HERE/input/sc-9-people.yaml" --calendar "$HERE/input/sc-9-calendar.yaml" \
        --absence "$HERE/input/sc-9-absence.yaml" 2>&1 | tail -1)"
check "SC-9" "SCHEDAVAIL OK dev-c 2026-09-14 8.0" "$got9"

if [ "$FAIL" -eq 0 ]; then echo "ATTNSELF OK $PASS/9"; exit 0; fi
echo "ATTNSELF FAIL $FAIL of 9"; exit 1
