#!/usr/bin/env bash
# access/tests/check-coverage.sh
# Fails when a manifest row names a missing test file, or when a Lane 5 test
# file is named by no manifest row. Fail-closed in both directions.
#
# The manifest's test_file list is read from yq exactly once, into a file,
# and matched in-memory from there. Re-invoking `yq ... | grep -qxF "$f"`
# once per candidate file (the previous form) starts one yq process per
# candidate and lets `grep -q` close the pipe as soon as it matches; on this
# platform's yq that intermittently surfaces as
# "Error: write /dev/stdout: The pipe is being closed." on stderr together
# with a spurious "is in no manifest row" FAIL that does not reproduce on
# the next run -- a flaky false FAIL, which is worse than a slow true one.
set -uo pipefail
RC=0
MANIFEST_LIST="$(mktemp)"
trap 'rm -f "$MANIFEST_LIST"' EXIT
yq -r '.checks[].test_file' access/tests/coverage.yaml | sort -u > "$MANIFEST_LIST"

while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || { echo "FAIL coverage :: manifest names missing test file $f"; RC=1; }
done < "$MANIFEST_LIST"

while IFS= read -r f; do
  case "$f" in */lib/*|*/lane5.sh|*/check-coverage.sh) continue;; esac
  grep -qxF "$f" "$MANIFEST_LIST" \
    || { echo "FAIL coverage :: test file $f is in no manifest row"; RC=1; }
done < <(find access/tests infra/tests ops-vm/tests notify/tests assets/tests -name '*.sh' 2>/dev/null | sort)
if [ "$RC" -eq 0 ]; then echo "COVERAGE OK"; else echo "COVERAGE FAIL"; fi
exit "$RC"
