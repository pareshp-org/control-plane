#!/usr/bin/env bash
# tools/records/validate-human-record.sh
# The human review lane guard for control-plane-records.
# Master Spec v4.0 Section 97.2 line 8871 (nobody edits a record file by hand to report a
# result), line 8890 (never edits in place; corrections are follow-up records),
# invariant 47 line 9515 (append-only), invariant 48 line 9516 (no silent overwrite).
# Usage: validate-human-record.sh [<base-ref>]   default base-ref: origin/HEAD
set -u
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
BASE="${1:-origin/HEAD}"
DIFF="$(git -C "$CPR_ROOT" diff --name-status "$BASE"...HEAD)"
if [ -z "$DIFF" ]; then echo "HUMAN-RECORD OK 0 files"; exit 0; fi
# DF-0614 fix: `python3 - <<'PY'` makes the heredoc win on fd 0, so python3 reads the script
# from the heredoc but sys.stdin.read() inside the script returns empty — the piped DIFF is
# discarded. Fix: write the checker to a temp file and pipe DIFF into a named python3 call.
_VHR_PY="$(mktemp --suffix=.py)"
cat > "$_VHR_PY" <<'PY'
import sys, yaml
reg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
hand = {r["path"].rstrip("/") for r in reg["stores"] if r["hand_authored"]}
machine = {r["path"].rstrip("/") for r in reg["stores"] if not r["hand_authored"]}
errs, n = [], 0
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    parts = line.split("\t")
    status, path = parts[0][0], parts[-1]
    n += 1
    if not (path.startswith("records/") or path.startswith("events/")):
        continue
    if status in ("M", "R"):
        errs.append("in-place-edit %s (Section 97.2 line 8890: corrections are follow-up records)" % path)
        continue
    if status == "D":
        errs.append("deletion %s (invariant 47 line 9515: history is append-only)" % path)
        continue
    if status == "A":
        owner = None
        for d in sorted(hand | machine, key=len, reverse=True):
            if path.startswith(d + "/"):
                owner = d
                break
        if owner is None:
            errs.append("unknown-store %s" % path)
        elif owner in machine:
            errs.append("hand-authored-in-machine-store %s (Section 97.2 line 8871)" % path)
if errs:
    for e in errs:
        print("HUMAN-RECORD FAIL " + e)
    sys.exit(1)
print("HUMAN-RECORD OK %d files" % n)
PY
printf '%s\n' "$DIFF" | python3 "$_VHR_PY" "$CP_ROOT/tools/records/write-paths.yaml"
_VHR_RC=$?
rm -f "$_VHR_PY"
exit "$_VHR_RC"
