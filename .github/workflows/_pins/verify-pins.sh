#!/usr/bin/env bash
# FAILS if any workflow in .github/workflows/*.yml references a third-party
# action by anything other than a full 40-character commit SHA, or if any
# __PIN_ token survives, or if any reusable-workflow reference into this
# repository uses a branch instead of the workflows/vN tag.
# Spec Section 33.2 ("no tags, no floating branches, no exceptions"),
# Section 33.3 ("Consumption is by pinned tag, never by branch"), Section 48.1.
# This is a fail-closed acceptance gate: it makes no exception for
# pre-existing files. If the live library is not yet pinned, this script
# is supposed to say so and exit non-zero — that is the correct behaviour,
# not a bug.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

shopt -s nullglob
files=(.github/workflows/*.yml)
shopt -u nullglob

fail=0

if [ "${#files[@]}" -gt 0 ]; then

if grep -RIn '__PIN_[A-Z_]*__' "${files[@]}" 2>/dev/null; then
  echo "FAIL: unsubstituted pin token"; fail=1
fi

while IFS= read -r line; do
  [ -z "$line" ] && continue
  ref="${line##*@}"
  case "$line" in
    "./"*|"docker://"*) : ;; # same-repo relative call, or a raw docker image — not a pinned third-party action
    *"/.github/workflows/"*) # cross-repo reusable workflow reference
      case "$ref" in
        workflows/v[0-9]*) : ;;
        *) echo "FAIL: reusable workflow not consumed by workflows/vN tag: $line"; fail=1 ;;
      esac ;;
    *)
      if ! printf '%s' "$ref" | grep -Eq '^[0-9a-f]{40}$'; then
        echo "FAIL: third-party action not pinned to a 40-hex SHA: $line"; fail=1
      fi ;;
  esac
done < <(grep -RhoE '^[[:space:]]*(-[[:space:]]*)?uses:[[:space:]]*[^[:space:]#]+' "${files[@]}" 2>/dev/null | sed -E 's/^[[:space:]]*(-[[:space:]]*)?uses:[[:space:]]*//')

if grep -RIn 'permissions:[[:space:]]*write-all' "${files[@]}" 2>/dev/null; then
  echo "FAIL: permissions: write-all is prohibited (Section 33.2)"; fail=1
fi

fi

if [ "$fail" -eq 0 ]; then echo "PINS OK"; fi
exit "$fail"
