#!/usr/bin/env bash
# X3 harness client: dispatches a real reusable workflow at a fixture repository
# in the sandbox organisation and asserts the RUN FAILED with the gate's token.
#
# D-L2-11 (REG-038) is decided (FD-021: option A, one Team-tier sandbox org) but
# no contracts/** file yet publishes the resolved sandbox_org_slug,
# sandbox_dispatch_secret_name or fixture_repo_prefix values. contracts/** keys
# are never invented here. While unresolved this client exits non-zero with
# SANDBOX_ORG_UNRESOLVED. It is a fail-closed stub, never a skipped step (rule S10).
set -uo pipefail

d_resolve_key() {   # d_resolve_key <key>
  grep -rhoE "^[[:space:]]*$1:[[:space:]]*\S+" contracts/ 2>/dev/null | head -1 | awk '{print $2}'
}

d_preflight() {
  local org secret prefix
  org="$(d_resolve_key sandbox_org_slug)"
  secret="$(d_resolve_key sandbox_dispatch_secret_name)"
  prefix="$(d_resolve_key fixture_repo_prefix)"
  if [ -z "$org" ] || [ -z "$secret" ] || [ -z "$prefix" ]; then
    printf 'SANDBOX_ORG_UNRESOLVED (D-L2-11) org=%s secret=%s prefix=%s\n' \
      "${org:-<absent>}" "${secret:-<absent>}" "${prefix:-<absent>}" >&2
    return 1
  fi
  printf '%s %s %s\n' "$org" "$secret" "$prefix"
}

d_dispatch_must_fail() {   # d_dispatch_must_fail <repo-suffix> <workflow> <expected-token>
  local pf; pf="$(d_preflight)" || return 1
  local org prefix; org="$(echo "$pf" | awk '{print $1}')"; prefix="$(echo "$pf" | awk '{print $3}')"
  local repo="$org/${prefix}$1"
  gh workflow run "$2" -R "$repo" --ref main >/dev/null 2>&1 || return 1
  sleep 20
  local concl
  concl="$(gh run list -R "$repo" -w "$2" -L 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null)"
  [ "$concl" = "failure" ] || { printf 'X3-NON-DISCRIMINATING %s %s conclusion=%s\n' "$repo" "$2" "${concl:-none}" >&2; return 1; }
  gh run view -R "$repo" -w "$2" --log 2>/dev/null | grep -q "$3" \
    || { printf 'X3-WRONG-REASON %s expected_token=%s\n' "$repo" "$3" >&2; return 1; }
  return 0
}
