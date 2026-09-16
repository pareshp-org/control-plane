#!/usr/bin/env bash
# metrics/attention/validate-attention-config.sh
# Proves taxonomy.yaml, sources.yaml and calibration.yaml agree with each other and with the spec.
# Output contract: one final line. ATTNCFG OK <counters> exit 0 / ATTNCFG FAIL <counters> exit 1 /
# ATTNCFG ERROR <reason> exit 3 (could not execute - never a pass).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
for f in taxonomy.yaml sources.yaml calibration.yaml; do
  [ -f "$HERE/$f" ] || { echo "ATTNCFG ERROR missing-$f"; exit 3; }
done
if [ "${1:-}" = "--selftest" ]; then
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  cp "$HERE/taxonomy.yaml" "$HERE/sources.yaml" "$HERE/calibration.yaml" "$T/"
  cp "$HERE/validate-attention-config.sh" "$T/"
  python3 - "$T/taxonomy.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
d["categories"].append({"name": "Meetings", "covers": "seeded canary", "precedence": 9, "spec_line": 0})
yaml.safe_dump(d, open(sys.argv[1], "w", encoding="utf-8"), sort_keys=False)
PY
  if sh "$T/validate-attention-config.sh" >/dev/null 2>&1; then
    echo "ATTNCFG FAIL selftest-canary-accepted"; exit 1
  fi
  echo "ATTNCFG OK selftest 1/1"; exit 0
fi
python3 - "$HERE" <<'PY' || exit $?
import os, sys, yaml
h = sys.argv[1]
tax = yaml.safe_load(open(os.path.join(h, "taxonomy.yaml"), encoding="utf-8"))
src = yaml.safe_load(open(os.path.join(h, "sources.yaml"), encoding="utf-8"))
cal = yaml.safe_load(open(os.path.join(h, "calibration.yaml"), encoding="utf-8"))
fails = []
cats = tax["categories"]
# C1 Section 67.2 line 5579 - exactly eight, exactly one rank each.
if len(cats) != 8:
    fails.append("category-count:%d" % len(cats))
if sorted(c["precedence"] for c in cats) != list(range(1, 9)):
    fails.append("precedence-not-1-8")
# C2 Section 97.4 line 8973 - the precedence order is the calibration order.
by_rank = [c["name"] for c in sorted(cats, key=lambda c: c["precedence"])]
if by_rank != cal["precedence_order"]["value"]:
    fails.append("precedence-order-mismatch")
if cal["truncation_order"]["expanded"] != list(reversed(by_rank)):
    fails.append("truncation-not-reverse")
# C3 Section 97.1 line 8838 - no sourceless category, and the two sets are identical.
sc = sorted(r["category"] for r in src["categories"])
if sc != sorted(c["name"] for c in cats):
    fails.append("source-category-set-mismatch")
for r in src["categories"]:
    if not r["record_stores"] and not r["event_phrases"]:
        fails.append("sourceless:%s" % r["category"])
# C4 Section 67.2 line 5592 / Section 97.4 line 8956 - flags are flags, ritual is not self-reported.
names = {c["name"] for c in cats}
for fl in tax["flags"]:
    if fl["name"] in names:
        fails.append("flag-is-category:%s" % fl["name"])
rit = [f for f in tax["flags"] if f["name"] == "ritual"]
if not rit or rit[0]["self_reportable"] is not False:
    fails.append("ritual-self-reportable")
# C5 Section 97.4 lines 8971-8972 - the two stated initial values, verbatim.
if cal["idle_gap_minutes"]["value"] != 30:
    fails.append("idle-gap:%s" % cal["idle_gap_minutes"]["value"])
if cal["granularity_hours"]["value"] != 0.25:
    fails.append("granularity:%s" % cal["granularity_hours"]["value"])
if cal["granularity_never_zero"]["value"] is not True:
    fails.append("granularity-zero-allowed")
# C6 Section 67.3 line 5603 - the five-minute cap.
if cal["self_report_cap_minutes_per_person_per_week"]["value"] != 5:
    fails.append("five-minute-cap")
if cal["self_report_per_product_attribution"]["value"] is not False:
    fails.append("per-product-self-report")
# C7 D102 line 10195 - every calibration key states a kind and a spec line.
for k, v in cal.items():
    if isinstance(v, dict):
        if "kind" not in v or ("spec_line" not in v and "spec_lines" not in v):
            fails.append("unsourced-key:%s" % k)
# C8 no threshold is a literal in code - every .py under metrics/attention reads this file.
py = []
for root, _, files in os.walk(h):
    for f in files:
        if f.endswith(".py"):
            py.append(os.path.join(root, f))
for p in py:
    body = open(p, encoding="utf-8").read()
    if "calibration.yaml" not in body and "load_calibration" not in body:
        fails.append("threshold-literal-risk:%s" % os.path.basename(p))
if fails:
    print("ATTNCFG FAIL %s" % ",".join(fails)); sys.exit(1)
print("ATTNCFG OK checks=8 categories=8 sources=8")
PY
