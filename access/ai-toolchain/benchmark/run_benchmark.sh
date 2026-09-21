#!/usr/bin/env bash
# Section 35.5 model-regression benchmark wrapper. Fails closed.
# It validates, refuses, and dispatches. It never records an adoption
# decision: "The runner executes; humans record the results and make the
# adoption decision" (Section 35.5).
# Usage: run_benchmark.sh <manifest.yaml>
set -u
if [ "$#" -ne 1 ]; then
  echo "USAGE: run_benchmark.sh <manifest.yaml>"
  exit 2
fi
MANIFEST="$1"
if [ ! -f "$MANIFEST" ]; then
  echo "BENCHMARK-RUN: BLOCKED (manifest $MANIFEST does not exist)"
  exit 3
fi
keys="$(env | sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p' \
        | grep -i 'api_key' | sort | tr '\n' ' ')"
if [ -n "${keys% }" ]; then
  echo "BENCHMARK-RUN: BLOCKED (vendor API key variables present: ${keys% })"
  echo "REASON: Section 36.6 — no vendor API keys exist anywhere in the estate"
  exit 3
fi
if ! python3 access/ai-toolchain/benchmark/validate_benchmark.py "$MANIFEST" \
     >/dev/null 2>&1; then
  echo "BENCHMARK-RUN: BLOCKED (manifest failed Section 35.5 validation)"
  exit 3
fi
if ! command -v hermes-batch-runner >/dev/null 2>&1; then
  echo "BENCHMARK-RUN: BLOCKED (hermes batch runner not present on this host)"
  exit 3
fi
echo "BENCHMARK-RUN: DISPATCHED $MANIFEST"
echo "WRITES-TO-RECORDS: none — SIG-42 and records/eval/ belong to the"
echo "WRITES-TO-RECORDS: Section 38.3 AI-eval scheduled runner, not to this"
exit 0
