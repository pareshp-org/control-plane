#!/usr/bin/env bash
# Section 46.6: the runner site, power and network dependency is declared beside
# each host, so a CI execution estate outage has a cause on the record rather
# than a discovery during one.
set -euo pipefail
DIR="${1:-assets/inventory}"
[ -d "$DIR" ] || { echo "RUNNER-DEPENDENCIES: FAIL-CLOSED (no inventory directory: $DIR)"; exit 1; }
found=0; bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  grep -q '^asset_class: ci_runner$' "$f" || continue
  found=$((found + 1))
  for k in site power network patch_cadence owner cost_band; do
    grep -qE "^${k}: *[^ ]" "$f" || { echo "missing $k: $f"; bad=1; }
  done
done
if [ "$bad" -eq 0 ]; then echo "RUNNER-DEPENDENCIES: PASS ($found ci_runner entries)"; else echo "RUNNER-DEPENDENCIES: FAIL"; exit 1; fi
