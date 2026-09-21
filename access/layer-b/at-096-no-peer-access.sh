#!/usr/bin/env bash
# access/layer-b/at-096-no-peer-access.sh
# AT-096 - "Employees cannot access each other's data": "Any attempt is denied."
set -euo pipefail
A="${1:?subject_a}"; B="${2:?subject_b}"
FAILS=0
note() { echo "AT-096_FAIL $1"; FAILS=$((FAILS+1)); }

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "AT-096 INDETERMINATE: layerb-host unreachable"; exit 2
fi

# 1. A's document is encrypted to A's key only: B cannot be a recipient.
doc=$(ssh layerb-host "ls -1t /srv/layerb/encrypted/documents/$A/*.selfview.asc | head -1")
kb=$(ssh layerb-host "gpg --with-colons --import-options show-only --import /srv/layerb/encrypted/pubkeys/$B.asc 2>/dev/null | awk -F: '/^pub/{print \$5; exit}'")
ssh layerb-host "gpg --list-only --status-fd 1 --decrypt $doc 2>/dev/null | grep -c '$kb'" \
  | grep -qx 0 || note "$B is a recipient of $A's self-view"

# 2. Document directories are not cross-readable.
perm=$(ssh layerb-host "stat -c %a /srv/layerb/encrypted/documents/$A")
[ "$perm" = "700" ] || note "$A's document directory is mode $perm, expected 700"

# 3. The peer-content refusal actually fires.
r=$(ssh layerb-host "printf 'evidence for %s and %s\n' $A $B > /tmp/at096.plain; \
    /srv/layerb/config/selfview/check-no-peer-content.sh /tmp/at096.plain $A; rm -f /tmp/at096.plain" || true)
printf '%s' "$r" | grep -q "PEER_TOKEN $B" || note "the peer-content check did not refuse a document naming $B"

# 4. Neither subject holds a Layer B-M account by virtue of having a self-view.
u=$(ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" http://127.0.0.1:3001/api/users/lookup?loginOrEmail=$B -o /dev/null -w '%{http_code}'")
[ "$u" = "404" ] || note "$B has a Layer B-M account (lookup returned $u, expected 404)"

if [ "$FAILS" -eq 0 ]; then echo "AT-096_PASS"; else echo "AT-096_FAILED $FAILS"; exit 1; fi
