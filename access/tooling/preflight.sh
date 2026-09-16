#!/usr/bin/env bash
# L5 phase-5 environment preflight. Prints exactly one PREFLIGHT: line.
set -u
fail=0
python3 --version >/dev/null 2>&1 || { echo "MISSING: python3"; fail=1; }
python3 -c "import yaml" >/dev/null 2>&1 || { echo "MISSING: PyYAML"; fail=1; }
if [ "$fail" -ne 0 ]; then
  echo "PREFLIGHT: FAIL"
  exit 1
fi
echo "PREFLIGHT: PASS"
