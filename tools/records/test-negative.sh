#!/usr/bin/env bash
# test-negative.sh --negative - every rule-level fixture must be REJECTED. 10/10 or fail.
# Master Spec v4.0 Section 97.1 line 8839; Section 97.2 line 8875; Section 97.3 lines 8931-8959; D88 line 10181.
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
[ "${1:---negative}" = "--negative" ] || { echo "usage: test-negative.sh --negative"; exit 1; }
"$L4_PY" - "$CP_ROOT" <<'PY'
import pathlib
import subprocess
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
rules = cp_root / "tools" / "records" / "fixtures" / "invalid" / "rules"
try:
    cases = yaml.safe_load((rules / "manifest.yaml").read_text(encoding="utf-8"))["cases"]
except Exception as exc:
    print("NEGATIVE FAIL-CLOSED: manifest unreadable: %s" % exc)
    sys.exit(1)
if len(cases) != 10:
    print("NEGATIVE FAIL-CLOSED: manifest has %d cases, expected 10" % len(cases))
    sys.exit(1)
validator = str(cp_root / "tools" / "records" / "lib" / "validate.py")
rejected = 0
for case in cases:
    schema = str(cp_root / "schemas" / "records" / case["schema"])
    fixture = str(rules / case["fixture"])
    proc = subprocess.run([sys.executable, validator, schema, fixture], capture_output=True, text=True)
    if proc.returncode == 0:
        print("NEGATIVE FAIL case %s: %s was ACCEPTED by %s" % (case["n"], case["fixture"], case["schema"]))
    else:
        rejected += 1
print("NEGATIVE %d/10" % rejected)
sys.exit(0 if rejected == 10 else 1)
PY
