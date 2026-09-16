#!/usr/bin/env bash
# L4 suite 6 - Ready-queue-miss detector. Section 97.5 lines 8982-8987; Section 29.4.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../../.." && pwd)"
. "$HERE/lib.sh"
RQ="$CP/tools/records/fixtures/rqm"
DET="$CP/tools/records/rqm-detect"
OUT="${L4_TMP:?}/rqm"; rm -rf "$OUT"; mkdir -p "$OUT"

verdict() { python3 "$DET" --input "$1" --json 2>/dev/null | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("verdict","NONE"),d.get("counts_in_sig06","NONE"))'; }

assert_eq "RQ-1" "miss True"          "$(verdict "$RQ/rq-1.yaml")"
assert_eq "RQ-2" "miss True"          "$(verdict "$RQ/rq-2.yaml")"
assert_eq "RQ-3" "no_miss False"      "$(verdict "$RQ/rq-3.yaml")"
assert_eq "RQ-4" "no_miss False"      "$(verdict "$RQ/rq-4.yaml")"
assert_eq "RQ-5" "miss True"          "$(verdict "$RQ/rq-5.yaml")"
assert_eq "RQ-6" "ready_bypass False" "$(verdict "$RQ/rq-6.yaml")"

# Section 29.4 field set, asserted without naming a field.
python3 "$DET" --input "$RQ/rq-1.yaml"            --json > "$OUT/a.json" 2>/dev/null
python3 "$DET" --input "$RQ/rq-1-unanswered.yaml" --json > "$OUT/b.json" 2>/dev/null
d="$(python3 - "$OUT/a.json" "$OUT/b.json" <<'PY'
import sys,json
a=set(json.load(open(sys.argv[1]))["record"].keys())
b=set(json.load(open(sys.argv[2]))["record"].keys())
print(("SUBSET" if b<a else "NOTSUBSET"), len(a-b))
PY
)"
assert_eq "RQ-FIELDSET" "SUBSET 3" "$d"

summary "06-rqm"
