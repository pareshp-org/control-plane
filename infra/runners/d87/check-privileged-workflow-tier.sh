#!/usr/bin/env bash
# D87 Blocking row 2: a privileged workflow resolving to a shared-pool label.
# Input is a resolution listing in the form
#   <workflow-file>\t<resolved runs-on label>
# The closed privileged set comes from separation.yaml; it is never widened here.
set -euo pipefail
L="${1:?usage: check-privileged-workflow-tier.sh <resolution.tsv>}"
S="${2:-infra/runners/d87/separation.yaml}"
[ -f "$L" ] || { echo "D87-ROW-2: FAIL-CLOSED (no resolution listing: $L)"; exit 4; }
[ -f "$S" ] || { echo "D87-ROW-2: FAIL-CLOSED (no separation.yaml)"; exit 4; }
priv=$(awk '/^privileged_workflows:/{f=1;next} /^[a-z_]+:/{f=0} f && /^ *- /{gsub(/^ *- /,"");print}' "$S")
bad=0
while IFS=$'\t' read -r wf label; do
  [ -n "${wf:-}" ] || continue
  echo "$priv" | grep -qxF "$wf" || continue
  case "$label" in
    ubuntu-*|windows-*|macos-*|privileged) ;;
    *) echo "privileged workflow $wf resolved to shared-pool label: $label"; bad=1 ;;
  esac
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-2: PASS"; else echo "D87-ROW-2: BLOCKING"; exit 4; fi
