#!/usr/bin/env bash
# ops-vm/tests/at-097-shared-no-people-ds.sh
# AT-097 - spec 100.6 / 90.3 (D75). Verified in the PROVISIONED CONFIGURATION:
# no datasource entry and no dashboard reference to the people datasource may
# exist in the shared instance.
#
# Real paths (verified on disk): the shared instance provisions from
# ops-vm/grafana/provisioning; the Founder-only Layer B-M instance from
# ops-vm/layer-b/provisioning. The runbook's draft paths --
# ops-vm/grafana/shared/provisioning and ops-vm/grafana/founder/provisioning
# -- are written by no task in the tree (lanes/L5-98-DEEP-REVIEW.md B-05).
# This is the same finding access/layer-b/at-097-no-people-datasource-in-shared.sh
# (built by L5-04-04) already independently records; that script's default
# $SHARED_PROV is ops-vm/grafana/provisioning too. This test integrates the
# same acceptance property into the Lane 5 coverage/evidence harness rather
# than duplicating its live-instance leg.
set -uo pipefail
. access/tests/lib/assert.sh
SHARED=ops-vm/grafana
FOUNDER=ops-vm/layer-b
if [ ! -d "$SHARED/provisioning/datasources" ]; then l5_indeterminate "AT-097" "PRE-E missing"; l5_exit; fi
if [ ! -d "$FOUNDER/provisioning/datasources" ]; then l5_indeterminate "AT-097" "PRE-F missing"; l5_exit; fi
TOKENS="$(grep -rhoE '(uid|name):[[:space:]]*[A-Za-z0-9_-]+' "$FOUNDER/provisioning/datasources" | awk '{print $2}' | sort -u)"
if [ -z "$TOKENS" ]; then l5_indeterminate "AT-097" "founder instance declares no datasource to look for"; l5_exit; fi
# Match only an actual YAML uid:/name: mapping line, with comment lines
# stripped first -- a bare substring grep would also match a documentation
# comment that explicitly RECORDS the datasource's absence (e.g.
# ops-vm/grafana/provisioning/datasources/layer-a.yaml's own header, "The
# people datasource is NEVER registered here"), producing exactly the false
# positive spec doctrine (Section 3.1) warns against: a check scoped wider
# than the property it verifies reports FAIL for the wrong reason.
noncomment_lines() { find "$1" -type f 2>/dev/null -exec grep -vE '^[[:space:]]*#' {} +; }
HIT=0
SHARED_LIVE="$(noncomment_lines "$SHARED")"
for tok in $TOKENS; do
  MATCH="$(printf '%s\n' "$SHARED_LIVE" | grep -E "(uid|name):[[:space:]]*${tok}([^A-Za-z0-9_-]|$)" || true)"
  if [ -n "$MATCH" ]; then
    l5_fail "AT-097" "shared instance provisioning registers the people datasource token '$tok': $MATCH"
    HIT=1
  fi
done
[ "$HIT" -eq 0 ] && l5_pass "AT-097/no-people-datasource-in-shared"
NAMING="$(noncomment_lines "$SHARED/provisioning" | grep -iE 'people|layer[_-]?b' || true)"
if [ -n "$NAMING" ]; then
  l5_fail "AT-097/naming" "a non-comment line in shared provisioning mentions people or Layer B: $NAMING"
else
  l5_pass "AT-097/naming"
fi
l5_exit
