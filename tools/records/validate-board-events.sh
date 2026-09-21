#!/usr/bin/env bash
# tools/records/validate-board-events.sh
# Every armed event_type in the Phase 3 emission contracts must already exist in the
# Section 97.3 taxonomy artifact. Master Spec v4.0 Section 97.3 line 8947.
# THIS SCRIPT NEVER WRITES THE TAXONOMY.
set -u
: "${CP_ROOT:?CP_ROOT not set}"
TAX="$CP_ROOT/metrics/taxonomy/event-types.yaml"
if [ ! -f "$TAX" ]; then echo "TAXONOMY-CONFORMANCE FAIL taxonomy-absent $TAX"; exit 1; fi
# The identifier-membership check runs entirely inside python (never captures a
# multi-line python stdout into a bash variable for a `for` loop). On a native
# Windows python3, stdout in text mode translates every internal "\n" to
# "\r\n"; bash command substitution strips only the FINAL trailing newline, so
# every line except the last keeps a stray \r glued to the end of its word
# when captured and iterated with `for t in $TYPES`. That \r then sits inside
# the grep pattern and never matches the LF-only taxonomy file, so every
# identifier except the alphabetically-last one falsely reports absent - a
# real, found-while-running defect, not a content problem in either emission
# contract. Doing the whole check in one python process sidesteps the bash
# round-trip instead of trying to out-guess line-ending translation in shell.
python3 - "$CP_ROOT" "$TAX" <<'PY'
import os, sys, yaml

cp, tax_path = sys.argv[1], sys.argv[2]
taxonomy = yaml.safe_load(open(tax_path, encoding="utf-8"))
known = {row["id"] for row in taxonomy["event_types"]}

types = []
r = yaml.safe_load(open(os.path.join(cp, "tools", "records", "dispatch", "rvr-inputs.yaml"), encoding="utf-8"))
types += [m["event_type"] for m in r["mechanisms"] if m["armed"]]
b = yaml.safe_load(open(os.path.join(cp, "tools", "records", "dispatch", "board-events.yaml"), encoding="utf-8"))
types += [t["event_type"] for t in b["transitions"] if t["event_type"] != "unarmed"]
types += ["ready_queue_miss_recorded"]
types = sorted(set(types))

missing = [t for t in types if t not in known]
for t in missing:
    print("TAXONOMY-CONFORMANCE FAIL absent-from-taxonomy %s" % t)
if missing:
    print("TAXONOMY-CONFORMANCE FAIL %d/%d absent" % (len(missing), len(types)))
    sys.exit(1)
print("TAXONOMY-CONFORMANCE OK %d/%d" % (len(types), len(types)))
PY
