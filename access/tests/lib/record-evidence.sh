#!/usr/bin/env bash
# access/tests/lib/record-evidence.sh
# Run by a HUMAN only. Writes one evidence file. Never run by the AI executor
# (Section 1.1: "The AI executor writes the test and the card; it never
# writes the evidence").
set -euo pipefail
CHECK_ID="${1:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
RESULT="${2:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
OBSERVED="${3:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
case "$RESULT" in pass|fail) ;; *) echo "STOP: result must be pass or fail"; exit 1;; esac
WHO="$(gh api user --jq .login)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DAY="$(date -u +%Y-%m-%d)"
CLAUSE="$(yq -r ".checks[] | select(.check_id == \"$CHECK_ID\") | .spec_clause" access/tests/coverage.yaml)"
REVAL="$(yq -r ".checks[] | select(.check_id == \"$CHECK_ID\") | .revalidate_after_days" access/tests/coverage.yaml)"
[ -n "$CLAUSE" ] && [ "$CLAUSE" != "null" ] || { echo "STOP: $CHECK_ID is not in access/tests/coverage.yaml"; exit 1; }
OUT="access/tests/evidence/${CHECK_ID}-${DAY}.json"
jq -n --arg c "$CHECK_ID" --arg r "$RESULT" --arg w "$WHO" --arg t "$NOW" \
      --arg o "$OBSERVED" --arg s "$CLAUSE" --argjson d "$REVAL" \
  '{check_id:$c,result:$r,executed_by:$w,executed_at:$t,observed:$o,spec_clause:$s,revalidate_after_days:$d}' > "$OUT"
echo "WROTE $OUT"
