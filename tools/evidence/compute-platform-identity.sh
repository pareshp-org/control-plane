#!/usr/bin/env bash
# Lane 2 - S18 platform-rebuild identity (Section 96.6 L8835; D78 L10172).
# The byte-identical digest is structurally unavailable on a git-push PaaS that
# rebuilds per environment, so the recorded identity stands in for the digest
# throughout the Section 32 chain: pinned commit SHA + lockfile + build config.
#
# usage: compute-platform-identity.sh <repo_root> <commit_sha> <lockfile_paths_csv> <build_config_paths_csv>
# stdout on success: platform-rebuild:v1:<64 hex>
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "USAGE_ERROR compute-platform-identity.sh <repo_root> <commit_sha> <lockfile_paths_csv> <build_config_paths_csv>"
  exit 2
fi
ROOT="$1"; COMMIT="$2"; LOCKS="$3"; CONFS="$4"

[ -d "$ROOT" ] || { echo "PLATFORM_INPUT_MISSING repo_root=$ROOT"; exit 1; }

printf '%s' "$COMMIT" | grep -qE '^[0-9a-f]{40}$' \
  || { echo "COMMIT_SHA_INVALID value=$COMMIT"; exit 1; }

[ -n "$LOCKS" ] || { echo "PLATFORM_LOCKFILE_UNDECLARED"; exit 1; }
[ -n "$CONFS" ] || { echo "PLATFORM_BUILD_CONFIG_UNDECLARED"; exit 1; }

BLOCK="$(mktemp)"
LINES="$(mktemp)"
trap 'rm -f "$BLOCK" "$LINES"' EXIT

emit_lines() { # kind csv
  local kind="$1" csv="$2" p h
  local IFS=','
  for p in $csv; do
    p="$(printf '%s' "$p" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
    [ -n "$p" ] || continue
    case "$p" in
      /*|*..*) echo "PLATFORM_INPUT_PATH_INVALID path=$p"; exit 1 ;;
    esac
    [ -f "$ROOT/$p" ] || { echo "PLATFORM_INPUT_MISSING path=$p"; exit 1; }
    h="$(sha256sum "$ROOT/$p" | cut -d' ' -f1)"
    printf '%s %s=%s\n' "$kind" "$p" "$h" >> "$LINES"
  done
}

: > "$LINES"
emit_lines lockfile "$LOCKS"
emit_lines buildconfig "$CONFS"

[ -s "$LINES" ] || { echo "PLATFORM_INPUT_MISSING reason=no-lines-emitted"; exit 1; }

{
  printf 'commit=%s\n' "$COMMIT"
  LC_ALL=C sort "$LINES"
} > "$BLOCK"

H="$(sha256sum "$BLOCK" | cut -d' ' -f1)"
printf 'platform-rebuild:v1:%s\n' "$H"
exit 0
