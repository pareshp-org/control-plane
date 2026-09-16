#!/usr/bin/env bash
# metrics/register/validate-sources.sh
# Validates metric-declarations.yaml and the register's supporting gates.
# Master Spec v4.0 §84.6 line 7479, §103 preamble line 9789, §101 invariants
# 46/49 (lines 9527, 9530), §103.14 lines 9988-9990 (AT-046).
#
#   (no args)     Source discipline (L4-P7-02, invariant 46): every declared
#                 measure names a non-empty source under metrics/** or
#                 records/**.
#   --attributes  L4-P7-01: every declared measure carries all eight
#                 attributes (definition, source, time_window, baseline,
#                 expected_interpretation, known_limitations, owner,
#                 action_on_breach).
#   --arming      L4-P7-03: delegates to arming.py.
#   --at046       L4-P7-04: delegates to baselines.py against baselines.yaml.
#   --ownership   L4-P7-05: delegates to ownership.py (invariant 49).
#   --compute <m> L4-P7-06..20: asserts metrics/compute/<m>.py exists.
#
# Fail-closed throughout: an unreadable or malformed declarations file is a
# failure, never a skip (Section 40.1 line 3671).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DECL_FILE="${SCRIPT_DIR}/metric-declarations.yaml"
[[ -f "$DECL_FILE" ]] || { echo "validate-sources: ABSENT: $DECL_FILE" >&2; exit 1; }
PY="${L4_PY:-python3}"

MODE="${1:-}"
case "$MODE" in
  "")
    "$PY" - "$DECL_FILE" "$SCRIPT_DIR/.." <<'PYEOF'
import os, sys
import yaml

decl_path, metrics_root = sys.argv[1], sys.argv[2]
repo_root = os.path.abspath(os.path.join(metrics_root, ".."))
try:
    doc = yaml.safe_load(open(decl_path, encoding="utf-8")) or {}
except Exception as exc:
    print("SOURCES FAIL: unreadable: %s" % exc); sys.exit(1)
metrics = doc.get("metrics") or []
errs = []
for m in metrics:
    src = (m.get("source") or "").strip()
    mid = m.get("id", "<unnamed>")
    if not src:
        errs.append("measure %s has no source" % mid)
        continue
    if not (src.startswith("metrics/") or src.startswith("records/")):
        errs.append("measure %s source %r is not under metrics/** or records/**" % (mid, src))
        continue
    path_part = src.split(" ")[0].rstrip("/")
    if not os.path.exists(os.path.join(repo_root, path_part)):
        errs.append("measure %s source %r does not exist on disk" % (mid, src))
if errs:
    for e in errs:
        print("SOURCES FAIL: %s" % e)
    sys.exit(1)
print("SOURCES OK")
PYEOF
    ;;
  --attributes)
    "$PY" - "$DECL_FILE" <<'PYEOF'
import sys
import yaml

REQUIRED = ["definition", "source", "time_window", "baseline",
            "expected_interpretation", "known_limitations", "owner", "action_on_breach"]
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
metrics = doc.get("metrics") or []
errs = []
for m in metrics:
    mid = m.get("id", "<unnamed>")
    missing = [k for k in REQUIRED if not m.get(k)]
    if missing:
        errs.append("measure %s missing attribute(s): %s" % (mid, ",".join(missing)))
if errs:
    for e in errs:
        print("ATTRIBUTES FAIL: %s" % e)
    sys.exit(1)
print("ATTRIBUTES OK %d/%d" % (len(metrics), len(metrics)))
PYEOF
    ;;
  --arming)
    ARMING="${SCRIPT_DIR}/arming.py"
    [[ -f "$ARMING" ]] || { echo "validate-sources: ABSENT: $ARMING" >&2; exit 1; }
    "$PY" - "$DECL_FILE" "$SCRIPT_DIR/.." "$ARMING" <<'PYEOF'
import os, subprocess, sys
import yaml

decl_path, metrics_root, arming_py = sys.argv[1], sys.argv[2], sys.argv[3]
repo_root = os.path.abspath(os.path.join(metrics_root, ".."))
doc = yaml.safe_load(open(decl_path, encoding="utf-8")) or {}
metrics = doc.get("metrics") or []
py = sys.executable
for m in metrics:
    src = (m.get("source") or "").split(" ")[0].rstrip("/")
    if not src:
        continue
    proc = subprocess.run([py, arming_py, "--store", os.path.join(repo_root, src)],
                           capture_output=True, text=True)
    if proc.returncode != 0:
        print("ARMING FAIL: %s -> %s" % (m.get("id"), proc.stdout.strip() or proc.stderr.strip()))
        sys.exit(1)
print("ARMING OK")
PYEOF
    ;;
  --at046)
    BASELINES_PY="${SCRIPT_DIR}/baselines.py"
    BASELINES_YAML="${SCRIPT_DIR}/baselines.yaml"
    [[ -f "$BASELINES_PY" ]] || { echo "validate-sources: ABSENT: $BASELINES_PY" >&2; exit 1; }
    [[ -f "$BASELINES_YAML" ]] || { echo "validate-sources: ABSENT: $BASELINES_YAML" >&2; exit 1; }
    "$PY" "$BASELINES_PY" "$BASELINES_YAML" && echo "AT-046 OK"
    ;;
  --ownership)
    OWNERSHIP_PY="${SCRIPT_DIR}/ownership.py"
    [[ -f "$OWNERSHIP_PY" ]] || { echo "validate-sources: ABSENT: $OWNERSHIP_PY" >&2; exit 1; }
    "$PY" "$OWNERSHIP_PY" "$DECL_FILE" && echo "OWNERSHIP OK"
    ;;
  --compute)
    MODULE="${2:?usage: validate-sources.sh --compute <module>}"
    MFILE="${SCRIPT_DIR}/../compute/${MODULE}.py"
    [[ -f "$MFILE" ]] || { echo "validate-sources: ABSENT: $MFILE" >&2; exit 1; }
    echo "COMPUTE ${MODULE} OK"
    ;;
  --check-declaration)
    # AT-075 (Section 100.5 line 9406): a metric declaration whose text names a
    # banned measurement (Section 91.2 lines 8081-8092) is rejected outright,
    # never registered - "no configuration option to enable any of them."
    DECL="${2:?usage: validate-sources.sh --check-declaration <path>}"
    [[ -f "$DECL" ]] || { echo "validate-sources: ABSENT: $DECL" >&2; exit 1; }
    "$PY" - "$DECL" <<'PYEOF'
import re
import sys

import yaml

BANNED_PATTERNS = [
    r"keystroke", r"screen[_ -]?monitor", r"screenshot",
    r"activity[_ -]?surveillance", r"webcam", r"presence[_ -]?detect",
    r"hours[_ -]?online", r"hours[_ -]?at[_ -]?desk",
    r"ai[_ -]?token[_ -]?usage", r"token[_ -]?usage",
    r"ide[_ -]?active[_ -]?time",
    r"flight[_ -]?risk", r"resignation[_ -]?predict",
    r"emotional[_ -]?state", r"engagement[_ -]?infer", r"wellbeing", r"mental[_ -]?health",
    r"surveillance[_ -]?scor",
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in BANNED_PATTERNS]

doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
text = " ".join(str(v) for v in doc.values() if isinstance(v, (str, int, float)))
hits = [p.pattern for p in COMPILED if p.search(text)]
if hits:
    print("BANNED-MEASUREMENT REJECTED: %s matches %s" % (sys.argv[1], ",".join(hits)))
    sys.exit(1)
print("BANNED-MEASUREMENT CLEAR: %s" % sys.argv[1])
PYEOF
    ;;
  *)
    echo "validate-sources: unknown mode: $MODE" >&2; exit 3 ;;
esac
