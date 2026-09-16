#!/usr/bin/env bash
# capacity-check.sh — L4 capacity profile check (FD-085, FD-090/PFD-019)
# DEPRECATED SHIM: the real FTE/YAML parsing + working-calendar model lives in
# scripts/l4/capacity-model.py (already wired to `make capacity`). This wrapper
# used to be an unfinished stub (TOTAL_FTE hardcoded to 0, no threshold/exit
# logic) that duplicated that script without doing any of its work. It now
# just delegates so there is one real implementation instead of two.
set -euo pipefail

echo "NOTE: capacity-check.sh is deprecated — delegating to scripts/l4/capacity-model.py" >&2
exec python scripts/l4/capacity-model.py --period "$(date +%Y-%m)" --output text "$@"
