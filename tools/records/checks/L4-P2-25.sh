#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P2-25 -- security-review unfixed-finding linkage.
# Master Spec v4.0 Section 97.2 line 8869: an unfixed finding is linked into
# the Portfolio Debt Inventory with an owner and a date. security-review.
# schema.json (L4-T216) leaves owner/due schema-optional because the rule is
# conditional on disposition == "unfixed"; tools/records/asserts/secreview.py
# is that conditional assertion. See lanes/L4-CONCORDANCE.md Phase-2 row
# L4-P2-25 (MED confidence): this module and this check file are exactly the
# residual gap recorded there.
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
SECREVIEW="$CP_DIR/tools/records/asserts/secreview.py"
PY="${L4_PY:-python3}"

[ -f "$SECREVIEW" ] || { echo "ABSENT: $SECREVIEW" >&2; exit 1; }

# Positive: the golden valid fixture (owner + due both present on the unfixed finding).
"$PY" "$SECREVIEW" "$CP_DIR/tools/records/fixtures/valid/security-review.yaml" >/dev/null 2>&1 \
  || { echo "positive fixture unexpectedly rejected" >&2; exit 1; }

# Negative fixture (neg_fixture): an unfixed finding missing owner and due must be rejected.
NEG="$CP_DIR/tools/records/fixtures/invalid/security-review-unfixed-no-owner.yaml"
[ -f "$NEG" ] || { echo "ABSENT: $NEG" >&2; exit 1; }
if OUT="$("$PY" "$SECREVIEW" "$NEG" 2>&1)"; then
  echo "neg_fixture: expected rejection did not occur" >&2
  echo "$OUT" >&2
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "unfixed-no-owner"; then
  echo "neg_fixture: rejection did not name the missing owner" >&2
  echo "$OUT" >&2
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "unfixed-no-due"; then
  echo "neg_fixture: rejection did not name the missing due date" >&2
  echo "$OUT" >&2
  exit 1
fi

echo "CHECK L4-P2-25 PASS"
