#!/usr/bin/env bash
# Section 45.1: the export carries secret REFERENCES - names, scopes and
# locations - never values. Fails the run rather than shipping a value.
set -euo pipefail
DIR="${1:?usage: export-no-secret-values.sh <staging-dir>}"
hits=$(grep -RIlE '(-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,})' "$DIR" || true)
if [ -n "$hits" ]; then echo "EXPORT-NO-SECRET-VALUES: FAIL"; echo "$hits"; exit 1; fi
echo "EXPORT-NO-SECRET-VALUES: PASS"
