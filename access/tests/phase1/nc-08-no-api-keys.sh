#!/usr/bin/env bash
# access/tests/phase1/nc-08-no-api-keys.sh
# NC-08 - spec 98.2 Phase 1 ("no API key present anywhere"); Section 40.2 and
# Section 36.6 (env | grep -i api_key must return empty; shell profiles and
# repository .env files checked at onboarding and re-checked quarterly);
# invariant 84.
# Negative check: nothing on this machine may present an API key.
# Scope: process environment, shell profiles, every .env under the working copy.
set -uo pipefail
. access/tests/lib/assert.sh

ENVHITS="$(env | grep -i 'api_key' || true)"
if [ -z "$ENVHITS" ]; then
  l5_pass "NC-08/env"
else
  l5_fail "NC-08/env" "environment presents: $(echo "$ENVHITS" | cut -d= -f1 | tr '\n' ' ')"
fi

PHITS=0
for p in .bashrc .bash_profile .profile .zshrc .zprofile .config/fish/config.fish; do
  f="$HOME/$p"
  [ -f "$f" ] || continue
  if grep -Eiq 'api[_-]?key' "$f"; then
    l5_fail "NC-08/profile" "$f references an api key"
    PHITS=1
  fi
done
[ "$PHITS" -eq 0 ] && l5_pass "NC-08/profiles"

EHITS=0
# testdata/ and fixtures/ are excluded: this lane and access/secrets/checks
# both ship deliberately "dirty" .env fixtures (e.g.
# access/secrets/testdata/no-api-keys/dirty/repo/.env) so that OTHER checkers
# can prove they refuse a planted key. Sweeping those in here would make NC-08
# permanently FAIL for a reason unrelated to any real credential on this
# machine, and the STOP rule below would then block the lane on a fixture.
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if grep -Eiq 'api[_-]?key' "$f"; then
    l5_fail "NC-08/dotenv" "$f references an api key"
    EHITS=1
  fi
done < <(find . -name '.env' -o -name '.env.*' 2>/dev/null \
          | grep -v '/node_modules/' \
          | grep -Ev '/(testdata|fixtures)/')
[ "$EHITS" -eq 0 ] && l5_pass "NC-08/dotenv"

# Positive control. Spec 36.6: every Hermes instance points at the estate's own
# local inference endpoint and model.api_key carries a self-minted control-plane
# token, never a vendor API key. Spec 35.2: the only approved provider value is
# custom. The Hermes worker config is subsystem J (infra/hermes/**), unassigned
# in PARTITION v1 as of this writing (lanes/L5-98-DEEP-REVIEW.md B-14) and built
# by no task in the tree yet. This positive control activates the moment that
# file exists; until then it contributes neither a pass nor a failure, per this
# task's own SELF-VERIFY (which must read SUITE OK on a clean machine today).
HERMES_CFG=""
for cand in infra/hermes/background-worker.yaml infra/hermes/worker.yaml; do
  [ -f "$cand" ] && { HERMES_CFG="$cand"; break; }
done
if [ -n "$HERMES_CFG" ]; then
  PROV="$(yq -r '.model.provider // ""' "$HERMES_CFG")"
  if [ "$PROV" = "custom" ]; then
    l5_pass "NC-08/hermes-provider"
  else
    l5_fail "NC-08/hermes-provider" "model.provider is '$PROV'; spec 35.2 requires custom"
  fi
  BASE="$(yq -r '.model.base_url // ""' "$HERMES_CFG")"
  case "$BASE" in
    http://*|https://*) l5_pass "NC-08/hermes-base-url" ;;
    *) l5_fail "NC-08/hermes-base-url" "model.base_url is not set to the LAN endpoint" ;;
  esac
fi
l5_exit
