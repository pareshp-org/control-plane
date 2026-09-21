#!/usr/bin/env bash
# assets/tests/at-017-asset-owner-orphan.sh
# AT-017 (asset-owner leg) - spec 100.2 and 49.1: "Asset owners participate in
# orphan detection." An asset left unowned by a departure must SURFACE; an
# owned one must not. The check runs against a copy of the inventory in a
# temporary root; it never writes a fixture into assets/inventory/.
set -uo pipefail
. access/tests/lib/assert.sh
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-017" "python3 not on PATH"; l5_exit; }
if [ ! -f assets/validate_assets.py ]; then l5_indeterminate "AT-017" "assets/validate_assets.py absent"; l5_exit; fi
if [ ! -d assets/inventory ]; then l5_indeterminate "AT-017" "PRE-K missing: assets/inventory"; l5_exit; fi
BASE="$(python3 assets/validate_assets.py 2>&1 | tail -n 1)"
case "$BASE" in
  "ASSET-VALIDATE: PASS"*) l5_pass "AT-017/inventory-baseline-clean" ;;
  *) l5_indeterminate "AT-017" "the live inventory is not clean before the test: $BASE"; l5_exit ;;
esac
TMP="$(mktemp -d)"
mkdir -p "$TMP/assets"
cp -r assets/. "$TMP/assets/"
cp assets/tests/fixtures/asset-owner-departed.yaml "$TMP/assets/inventory/at-017-orphan-fixture.yaml"
l5_refuses "AT-017/orphan-surfaces" "an asset whose owner departed and was not reassigned" \
  bash -c 'cd "$1" && python3 assets/validate_assets.py' _ "$TMP"
rm -f "$TMP/assets/inventory/at-017-orphan-fixture.yaml"
OWNER="$(python3 assets/resolve_holder.py capability:devops 2>/dev/null | sed 's/^RESOLVE: //')"
case "${OWNER:-NONE}" in
  ''|NONE|AMBIGUOUS) l5_indeterminate "AT-017/positive-control" "resolve_holder.py returned '${OWNER:-empty}'; do not invent an owner"; l5_exit ;;
esac
sed "s/__OWNER__/$OWNER/" assets/tests/fixtures/asset-owner-active.yaml > "$TMP/assets/inventory/at-017-owned-fixture.yaml"
l5_permits "AT-017/owned-asset-passes" "an identical asset with a resolving owner" \
  bash -c 'cd "$1" && python3 assets/validate_assets.py' _ "$TMP"
rm -rf "$TMP"
l5_exit
