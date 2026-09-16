#!/usr/bin/env bash
# Section 36.6: Repomix pre-flight secret stripping on the GSD packaging path.
# Fails closed. Never packages when either precondition is unmet.
# Usage: repomix_preflight.sh <repo-path> <secretlint-coverage-record>
set -u
if [ "$#" -ne 2 ]; then
  echo "USAGE: repomix_preflight.sh <repo-path> <secretlint-coverage-record>"
  exit 2
fi
REPO="$1"; COVERAGE="$2"
if ! command -v repomix >/dev/null 2>&1; then
  echo "REPOMIX-PREFLIGHT: BLOCKED (repomix is not installed)"
  exit 3
fi
if [ ! -f "$COVERAGE" ]; then
  echo "REPOMIX-PREFLIGHT: BLOCKED (no recorded Secretlint coverage at $COVERAGE)"
  exit 3
fi
echo "REPOMIX-PREFLIGHT: PASS"
echo "PACKAGE-COMMAND: repomix --secret-filtering-enabled $REPO"
exit 0
