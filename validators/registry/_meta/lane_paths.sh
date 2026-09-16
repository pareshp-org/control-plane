#!/usr/bin/env bash
# Lane 1 self-guard. Fails if the working tree or the branch diff touches a foreign path.
# PARTITION.md rule 1: "One owner per path. A lane PR touching a foreign path FAILS."
# Owned prefixes are copied verbatim from PARTITION.md line 17 and are not editable here.
set -euo pipefail
ALLOW='^(schemas/registry/|schemas/product/|registries/|validators/registry/)'
BASE="${1:-integration}"

changed="$( { git diff --name-only "$BASE"...HEAD 2>/dev/null || true;
              git status --porcelain | awk '{print $2}'; } | sort -u )"

bad="$(printf '%s\n' "$changed" | grep -v -E "$ALLOW" | grep -v '^$' || true)"

if [ -n "$bad" ]; then
  echo "LANE-GUARD-FAIL: foreign paths touched by lane/1:"
  printf '%s\n' "$bad"
  exit 1
fi
echo "LANE-GUARD-PASS"
exit 0
