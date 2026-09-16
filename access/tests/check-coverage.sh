#!/usr/bin/env bash
# access/tests/check-coverage.sh
# Fails when a manifest row names a missing test file, or when a Lane 5 test
# file is named by no manifest row. Fail-closed in both directions.
set -uo pipefail
RC=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || { echo "FAIL coverage :: manifest names missing test file $f"; RC=1; }
done < <(yq -r '.checks[].test_file' access/tests/coverage.yaml | sort -u)
while IFS= read -r f; do
  case "$f" in */lib/*|*/lane5.sh|*/check-coverage.sh) continue;; esac
  yq -r '.checks[].test_file' access/tests/coverage.yaml | grep -qxF "$f" \
    || { echo "FAIL coverage :: test file $f is in no manifest row"; RC=1; }
done < <(find access/tests infra/tests ops-vm/tests notify/tests assets/tests -name '*.sh' 2>/dev/null | sort)
if [ "$RC" -eq 0 ]; then echo "COVERAGE OK"; else echo "COVERAGE FAIL"; fi
exit "$RC"
