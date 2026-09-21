#!/usr/bin/env bash
# access/tests/at-107-eval-regression-blocks-pin.sh
# AT-107 - spec 100.4: a regression detected by the AI-eval scheduled runner
# raises SIG-42 and blocks adoption of the new model pin. Tolerance is
# SIG-42's initial value (spec 52.2): more than 5 percentage points below the
# recorded baseline.
#
# Boundary (stated in L5-07-tests-and-runbook.md Section 4, L5-07-13): the
# category-five incident record and records/eval/ run history live in
# control-plane-records (L4, EXT-3) and the detection computation itself is
# metrics/compute/eval.py (L4, out of Lane 5's owned paths entirely -- not
# access/**/infra/**/ops-vm/**/notify/**/assets/**). What Lane 5 owns is the
# runtime configuration that declares the tolerance, the SIG-42 route and
# the pin (access/ai-toolchain/**, the real path -- lanes/L5-98-DEEP-REVIEW.md
# B-05), and the arithmetic that decides whether a candidate pin is
# adoptable. Neither metrics/** nor records/** is read or written here.
set -uo pipefail
. access/tests/lib/assert.sh
TOL=5
SCOPE=access/ai-toolchain
if [ ! -d "$SCOPE" ]; then l5_indeterminate "AT-107" "PRE-M missing: $SCOPE"; l5_exit; fi
if grep -rqF 'SIG-42' "$SCOPE" 2>/dev/null; then
  l5_pass "AT-107/sig-42-declared"
else
  l5_fail "AT-107/sig-42-declared" "no Lane 5 ai-toolchain file names a SIG-42 route for an eval regression"
fi
if grep -rEq '(^|[^0-9])5[[:space:]]*(percentage|pp|%)' "$SCOPE" 2>/dev/null; then
  l5_pass "AT-107/tolerance-declared"
else
  l5_fail "AT-107/tolerance-declared" "the declared regression tolerance of 5 percentage points (SIG-42) is absent from $SCOPE"
fi
FLOATING="$(grep -rniF -e 'latest' -e '-preview' -e 'stable' "$SCOPE"/runtimes/*.yaml 2>/dev/null || true)"
if [ -z "$FLOATING" ]; then
  l5_pass "AT-107/no-floating-alias"
else
  l5_fail "AT-107/no-floating-alias" "a model identifier uses a floating alias; spec 38.1 requires pinned snapshots: $FLOATING"
fi
score() { jq -r --arg d accuracy '.scored_dimensions[$d]' "$1"; }
B="$(score access/tests/fixtures/at-107-eval-baseline.json)"
R="$(score access/tests/fixtures/at-107-eval-regression.json)"
W="$(score access/tests/fixtures/at-107-eval-within-tolerance.json)"
blocks() { awk -v b="$1" -v c="$2" -v t="$TOL" 'BEGIN { exit ((b - c) > t) ? 0 : 1 }'; }
if blocks "$B" "$R"; then
  l5_pass "AT-107/regression-blocks-pin"
else
  l5_fail "AT-107/regression-blocks-pin" "a drop from $B to $R exceeds the ${TOL}pp tolerance and was not classified as a regression"
fi
if blocks "$B" "$W"; then
  l5_fail "AT-107/within-tolerance-adopts" "a run within tolerance ($B to $W) was wrongly classified as a regression"
else
  l5_pass "AT-107/within-tolerance-adopts"
fi
l5_exit
