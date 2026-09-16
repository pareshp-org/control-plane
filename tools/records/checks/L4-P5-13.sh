#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P5-13 - Material requirement change: re-plan event linked to the estimate
# record. Master Spec 29.5 lines 2699-2701.
CP_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$CP_DIR"
export CP_ROOT="$CP_DIR"
export CPR_ROOT="$CP_DIR"
PY="${L4_PY:-python3}"
DEF="$CP_DIR/metrics/boards/replan-definition.yaml"
MOD="$CP_DIR/tools/records/replan.py"

[[ -f "$DEF" ]] || { echo "ABSENT: $DEF" >&2; exit 1; }
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }

# Positive: the literal acceptance command of L4-06-tasks.md row 78.
bash tools/records/validate-boards.sh --replan | grep -qx "BOARDS OK replan=1 triggers=5 threshold=0.5" \
  || { echo "validate-boards.sh --replan did not print the expected summary line" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Positive, real: a mandatory trigger fires against a real, existing estimate record.
# The re-plan event links to it, and the item carries the Blocked flag with reason
# re-plan while execution is stopped (line 2701 - the acceptance criterion itself).
cat > "$TMP/case-replan.yaml" <<YAML
item: work-item/4388
product: solvox
estimate_record: tools/records/fixtures/valid/estimate.yaml
impact_scope_widens: true
YAML
OUT="$("$PY" "$MOD" --input "$TMP/case-replan.yaml")"
echo "$OUT" | grep -q '"event_type": "replan_triggered"' \
  || { echo "re-plan event_type missing or wrong" >&2; echo "$OUT" >&2; exit 1; }
echo "$OUT" | grep -q '"estimate_record": "tools/records/fixtures/valid/estimate.yaml"' \
  || { echo "re-plan event does not link to the estimate record" >&2; echo "$OUT" >&2; exit 1; }
echo "$OUT" | grep -q '"reason": "re-plan"' \
  || { echo "Blocked flag reason is not re-plan" >&2; echo "$OUT" >&2; exit 1; }
echo "$OUT" | grep -q '"set": true' \
  || { echo "Blocked flag is not set while execution is stopped" >&2; echo "$OUT" >&2; exit 1; }
echo "$OUT" | grep -q '"execution": "stopped"' \
  || { echo "execution is not recorded as stopped" >&2; echo "$OUT" >&2; exit 1; }

# Below-threshold case: no line-2699 trigger fires -> update in place, no Blocked flag,
# no re-plan event. Proves the module does not treat every requirement change as re-plan.
cat > "$TMP/case-inplace.yaml" <<YAML
item: work-item/4388
product: solvox
estimate_record: tools/records/fixtures/valid/estimate.yaml
impact_scope_widens: false
YAML
OUT2="$("$PY" "$MOD" --input "$TMP/case-inplace.yaml")"
echo "$OUT2" | grep -q '"verdict": "update_in_place"' \
  || { echo "a change with no fired trigger was not updated in place" >&2; echo "$OUT2" >&2; exit 1; }
echo "$OUT2" | grep -q '"set": false' \
  || { echo "Blocked flag set on a non-re-plan change" >&2; echo "$OUT2" >&2; exit 1; }

# Negative fixture (neg): a re-plan whose estimate_record does not exist on disk must be
# refused, never fabricated. This is the one L4-06-tasks.md section 0.8 rule 9 requires:
# a check that cannot fail is not a check.
cat > "$TMP/bad_fixture-no-estimate.yaml" <<YAML
item: work-item/9999
product: solvox
estimate_record: tools/records/fixtures/valid/does-not-exist.yaml
impact_scope_widens: true
YAML
if OUT3="$("$PY" "$MOD" --input "$TMP/bad_fixture-no-estimate.yaml" 2>&1)"; then
  echo "neg-fixture: expected rejection did not occur" >&2
  echo "$OUT3" >&2
  exit 1
fi
echo "$OUT3" | grep -q "REPLAN FAIL estimate-record-not-found" \
  || { echo "neg-fixture: rejection did not name the missing estimate record" >&2; echo "$OUT3" >&2; exit 1; }

echo "CHECK L4-P5-13 PASS"
