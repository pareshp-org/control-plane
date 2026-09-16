#!/usr/bin/env bash
# metrics/attention/validate-store-naming.sh
# The shipping test of Section 97.1 line 8838: "A metric that cannot name its store does not ship."
# Output contract: one final line. STORENAME OK <counters> exit 0 / STORENAME FAIL <reasons> exit 1
# / STORENAME ERROR <reason> exit 3 (could not execute - never a pass).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
[ -f "$HERE/derived-metrics.yaml" ] || { echo "STORENAME ERROR missing-derived-metrics"; exit 3; }
[ -f "$HERE/taxonomy.yaml" ]        || { echo "STORENAME ERROR missing-taxonomy"; exit 3; }
[ -f "$HERE/derive.py" ]            || { echo "STORENAME ERROR missing-derive"; exit 3; }

if [ "${1:-}" = "--selftest" ]; then
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  mkdir -p "$T/metrics/attention" "$T/metrics/taxonomy"
  cp "$HERE"/derived-metrics.yaml "$HERE"/taxonomy.yaml "$HERE"/derive.py \
     "$HERE"/scheduled-availability.py "$HERE"/validate-store-naming.sh "$T/metrics/attention/"
  cp "$CP/metrics/taxonomy/event-types.yaml" "$T/metrics/taxonomy/"
  python3 - "$T/metrics/attention/derived-metrics.yaml" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
# Seeded canary: one metric loses the store it must name (Section 97.1 line 8838).
doc["metrics"]["attention_hours_by_category"]["record_stores"] = []
yaml.safe_dump(doc, open(sys.argv[1], "w", encoding="utf-8"), sort_keys=False)
PY
  if sh "$T/metrics/attention/validate-store-naming.sh" >/dev/null 2>&1; then
    echo "STORENAME FAIL selftest-storeless-accepted"; exit 1
  fi
  echo "STORENAME OK selftest 1/1"; exit 0
fi

python3 - "$HERE" "$CP" <<'PY' || exit $?
import os, sys, yaml
here, cp = sys.argv[1], sys.argv[2]
doc = yaml.safe_load(open(os.path.join(here, "derived-metrics.yaml"), encoding="utf-8"))
tax = yaml.safe_load(open(os.path.join(here, "taxonomy.yaml"), encoding="utf-8"))
metrics = doc.get("metrics") or {}
fails = []

# The two executables and the Phase-2 event register are matched by TEXT, never parsed:
# their shapes belong to other tasks and this check must not couple to them.
blob = ""
for name in ("derive.py", "scheduled-availability.py"):
    path = os.path.join(here, name)
    if os.path.exists(path):
        blob += open(path, encoding="utf-8").read()
evt_path = os.path.join(cp, "metrics", "taxonomy", "event-types.yaml")
evt = open(evt_path, encoding="utf-8").read() if os.path.exists(evt_path) else ""
flags = {f["name"] for f in (tax.get("flags") or [])}

REQUIRED = ["definition", "source", "time_window", "baseline",
            "expected_interpretation", "known_limitations", "owner", "action_on_breach"]

stored = 0
for mid, row in metrics.items():
    # S1 Section 84.6 line 7471 - the eight attributes, none empty.
    for attr in REQUIRED:
        if not row.get(attr):
            fails.append("missing-attribute:%s.%s" % (mid, attr))
    # S2 Section 97.1 line 8838 - name the store, or do not ship.
    if not row.get("record_stores"):
        fails.append("storeless:%s" % mid)
    else:
        stored += 1
    # S3 Section 84.6 line 7473 - known_limitations is never empty.
    if str(row.get("known_limitations", "")).strip() in ("", "none"):
        fails.append("empty-limitations:%s" % mid)
    # S4 Section 103.14 line 9975 / D77 line 10160 - a value, or the explicit marker.
    if row.get("baseline") in (None, ""):
        fails.append("no-baseline-and-no-marker:%s" % mid)
    # S6 the figure must actually be emitted.
    src = row.get("source") or {}
    if len(src) != 1:
        fails.append("source-not-exactly-one-provenance:%s" % mid)
    elif "output_key" in src:
        if ('"%s"' % src["output_key"]) not in blob:
            fails.append("output-key-not-emitted:%s:%s" % (mid, src["output_key"]))
    elif "taxonomy_flag" in src:
        if src["taxonomy_flag"] not in flags:
            fails.append("flag-not-in-taxonomy:%s:%s" % (mid, src["taxonomy_flag"]))
    elif "event_type" in src:
        if src["event_type"] not in evt:
            fails.append("event-type-not-in-register:%s:%s" % (mid, src["event_type"]))
    else:
        fails.append("unknown-provenance:%s" % mid)

# S5 - one register per thing. No id here may also live in the Section 103 register.
reg = os.path.join(cp, "metrics", "register", "metric-declarations.yaml")
if os.path.exists(reg):
    other = yaml.safe_load(open(reg, encoding="utf-8")) or {}
    for mid in metrics:
        if mid in other:
            fails.append("duplicate-of-metric-register:%s" % mid)

if not metrics:
    print("STORENAME FAIL empty-register"); sys.exit(1)
if fails:
    print("STORENAME FAIL %s" % ",".join(fails)); sys.exit(1)
print("STORENAME OK metrics=%d stored=%d checks=6" % (len(metrics), stored))
PY
