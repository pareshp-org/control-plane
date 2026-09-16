#!/usr/bin/env bash
# L4 suite 5 - attention-hour derivation. MasterSpec v4.0 Section 97.4 lines 8954-8981.
# Expected values are fixed by L4-07-tests-and-runbook.md task L4-P7-T09. Never edit them
# to make a run pass: a mismatch is a defect in metrics/attention/derive.py, not here.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$CP/tools/records/test/lib.sh"
IN="$CP/tools/records/fixtures/attention/input"
EX="$CP/tools/records/fixtures/attention/expected"
NORM='import sys,json;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True,separators=(",",":")))'

if [ "${1:-}" = "--provenance" ]; then
  out="$(python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-8.yaml" --json 2>/dev/null)"
  n="$(printf '%s' "$out" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(sum(1 for r in d["apportioned"] if r.get("provenance")=="self-reported"))')"
  if [ "$n" = "3" ]; then echo "PROVENANCE OK"; exit 0; else echo "PROVENANCE FAIL labelled=$n expected=3"; exit 1; fi
fi

for c in 1 2 3 4 5 6 7 8; do
  id="DC-$c"
  got="$(python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-$c.yaml" --json 2>/dev/null \
        | python3 -c 'import sys,json;print(json.dumps(json.load(sys.stdin),sort_keys=True,separators=(",",":")))')"
  want="$(python3 -c "$NORM" "$EX/dc-$c.json")"
  assert_eq "$id" "$want" "$got"
done
assert_rejects "DC-9" python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-9.yaml" --json

if [ "$L4_FAIL" -eq 0 ]; then echo "ATTENTION OK"; exit 0; else echo "ATTENTION FAIL $L4_FAIL of 9"; exit 1; fi
