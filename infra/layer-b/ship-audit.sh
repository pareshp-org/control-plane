#!/usr/bin/env bash
# infra/layer-b/ship-audit.sh - runs on layerb-host, hourly.
# Ships the host audit trail to a destination the host holds no credential to
# alter: the same append-only, write-only, object-locked discipline the
# organisation export uses (Section 45.3), per Section 90.3.
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT

# ausearch accepts one -k per invocation; repeating the flag on one command
# line only keeps the last occurrence, so a single
# `ausearch -k a -k b -k c` silently ships only key c's events and defeats
# the compensating control while looking correct. Query each key separately
# and concatenate.
ANY_FAILED=0
: > "$TMP"
for key in layerb_store layerb_secrets layerb_audit_config; do
  if OUT=$(ausearch -k "$key" --start recent 2>/tmp/ship-audit.$$.err); then
    printf '%s\n' "$OUT" >> "$TMP"
  else
    # ausearch exits non-zero both when it finds nothing for the key (fine,
    # not a failure) and on a real error such as denied access to the audit
    # log (not fine). Distinguish by checking stderr rather than blanket
    # `|| true`, which would hide the second case.
    if grep -qi 'no matches\|<no matches>' /tmp/ship-audit.$$.err 2>/dev/null; then
      : # no events for this key since the last ship - expected, not a failure
    else
      echo "AUDIT_QUERY_FAILED key=$key: $(cat /tmp/ship-audit.$$.err)" >&2
      ANY_FAILED=1
    fi
  fi
  rm -f /tmp/ship-audit.$$.err
done
[ "$ANY_FAILED" -eq 0 ] || { echo "AUDIT_SHIP_ABORTED query failure, see stderr"; exit 1; }

[ -s "$TMP" ] || echo "no-events $STAMP" > "$TMP"
# Write-only profile. It cannot list, get or delete what it wrote.
aws s3 cp "$TMP" "s3://layerb-audit/$STAMP.log" --profile layerb-audit-writer
echo "AUDIT_SHIPPED $STAMP"
