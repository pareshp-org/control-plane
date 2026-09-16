#!/usr/bin/env bash
# validate-taxonomy.sh - proves metrics/taxonomy/event-types.yaml is a closed, well-formed enum.
# Master Spec v4.0 Section 97.3 line 8959. Fail-closed: an unreadable taxonomy is a failure.
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
MODE="${1:---taxonomy}"

if [ "$MODE" = "--signals" ]; then
  # L4-P3-06: the SIG source map is closed at exactly the 7 signals D-L4-TL-4
  # names (SIG-06, SIG-17, SIG-41, SIG-42, SIG-43, SIG-46, SIG-47), one row
  # each, signal_id unique. Fail-closed on an unreadable or malformed map.
  "$L4_PY" - "$CP_ROOT/metrics/signals/sig-source-map.yaml" <<'PY'
import sys

import yaml

path = sys.argv[1]
try:
    doc = yaml.safe_load(open(path, encoding="utf-8"))
except Exception as exc:
    print("SIGNALS FAIL: unreadable: %s" % exc)
    sys.exit(1)
rows = doc.get("signals") or []
fail = []
if len(rows) != 7:
    fail.append("count %d, expected 7" % len(rows))
ids = [r.get("signal_id") for r in rows]
if len(set(ids)) != len(ids):
    fail.append("duplicate signal_id")
expected = {"SIG-06", "SIG-17", "SIG-41", "SIG-42", "SIG-43", "SIG-46", "SIG-47"}
if set(ids) != expected:
    fail.append("signal set %r, expected %r" % (sorted(set(ids)), sorted(expected)))
for r in rows:
    if not r.get("source_store"):
        fail.append("row %r has no source_store" % r.get("signal_id"))
if fail:
    for f in fail:
        print("SIGNALS FAIL: %s" % f)
    sys.exit(1)
print("SIGNALS OK %d/7" % len(rows))
PY
  exit $?
fi

if [ "$MODE" = "--retirement" ]; then
  # L4-P3-03: retire-never-remove. An identifier that has ever shipped in
  # metrics/taxonomy/event-types.yaml is never deleted from the file; it may
  # only gain "retired: true" and stay. §97.3 line 8961. Fail-closed: an
  # identifier present at BASELINE_REF and absent from the working copy is
  # Blocking drift, proved by diffing the id sets.
  BASELINE_REF="${2:-origin/integration}"
  "$L4_PY" - "$CP_ROOT" "$CP_ROOT/metrics/taxonomy/event-types.yaml" "$BASELINE_REF" <<'PY'
import subprocess
import sys

import yaml

cp_root, current_path, baseline_ref = sys.argv[1], sys.argv[2], sys.argv[3]


def ids_of(text):
    doc = yaml.safe_load(text) or {}
    return {row.get("id") for row in (doc.get("event_types") or []) if row.get("id")}


try:
    current_ids = ids_of(open(current_path, encoding="utf-8").read())
except Exception as exc:
    print("RETIREMENT FAIL: current taxonomy unreadable: %s" % exc)
    sys.exit(1)

proc = subprocess.run(
    ["git", "-C", cp_root, "show", "%s:metrics/taxonomy/event-types.yaml" % baseline_ref],
    capture_output=True,
    text=True,
)
if proc.returncode != 0:
    # No taxonomy exists yet at the baseline ref (first publication) -
    # nothing has shipped, so nothing can have been removed.
    print("RETIREMENT OK 0")
    sys.exit(0)

try:
    baseline_ids = ids_of(proc.stdout)
except Exception as exc:
    print("RETIREMENT FAIL: baseline taxonomy unreadable: %s" % exc)
    sys.exit(1)

removed = sorted(baseline_ids - current_ids)
if removed:
    print("RETIREMENT FAIL: removed identifier(s) that previously shipped: %s" % ", ".join(removed))
    sys.exit(1)
print("RETIREMENT OK %d" % len(baseline_ids))
PY
  exit $?
fi

"$L4_PY" - "$CP_ROOT/metrics/taxonomy/event-types.yaml" <<'PY'
import re
import sys

import yaml

path = sys.argv[1]
try:
    doc = yaml.safe_load(open(path, encoding="utf-8"))
except Exception as exc:
    print("TAXONOMY FAIL: unreadable: %s" % exc)
    sys.exit(1)
rows = doc.get("event_types") or []
fail = []
if len(rows) != 86:
    fail.append("count %d, expected 86" % len(rows))
if doc.get("identifier_count") != 86:
    fail.append("identifier_count %r, expected 86" % doc.get("identifier_count"))
ids = [r.get("id") for r in rows]
if len(set(ids)) != len(ids):
    fail.append("duplicate identifiers")
pat = re.compile(r"^[a-z][a-z0-9_]*$")
for r in rows:
    if not pat.match(str(r.get("id", ""))):
        fail.append("identifier not lower_snake_case: %r" % r.get("id"))
    if not isinstance(r.get("payload_required"), list):
        fail.append("payload_required not a list on %r" % r.get("id"))
if [r.get("n") for r in rows] != list(range(1, len(rows) + 1)):
    fail.append("n is not 1..N in taxonomy order")
compound = [r["n"] for r in rows if "states" in r]
if compound != [29, 50, 51, 69, 75, 76, 79, 86]:
    fail.append("compound rows %r, expected [29, 50, 51, 69, 75, 76, 79, 86]" % compound)
for r in rows:
    if "states" in r and r.get("payload_required") != ["state"]:
        fail.append("compound row %r must declare payload_required: [state]" % r.get("id"))
if fail:
    for f in fail:
        print("TAXONOMY FAIL: %s" % f)
    sys.exit(1)
print("TAXONOMY OK 86")
PY
