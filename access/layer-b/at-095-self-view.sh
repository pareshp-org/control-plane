#!/usr/bin/env bash
# access/layer-b/at-095-self-view.sh
# AT-095 - "The individual self-view works": "A person sees their own evidence,
# KRA/KPI mapping and capability matrix - delivered as a generated per-person
# document - and nothing about peers."
set -euo pipefail
SUBJECT="${1:?subject_login}"
FAILS=0
note() { echo "AT-095_FAIL $1"; FAILS=$((FAILS+1)); }

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "AT-095 INDETERMINATE: layerb-host unreachable"; exit 2
fi

# a) It is a document, not a dashboard: no Layer B-M dashboard renders it.
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?query=self-view | jq -r "length"' \
  | grep -qx 0 || note "a Layer B-M dashboard named self-view exists; Section 90.3 requires a document"

# b) Generation produces armoured ciphertext for the subject.
out=$(ssh layerb-host "LAYERB_SESSION_ACTOR=\"\$LAYERB_FOUNDER_LOGIN\" /srv/layerb/config/selfview/generate-selfview.sh $SUBJECT at095" || true)
printf '%s' "$out" | grep -q '^SELFVIEW_GENERATED' || note "generation failed: $out"
ssh layerb-host "head -1 \$(ls -1t /srv/layerb/encrypted/documents/$SUBJECT/*.selfview.asc | head -1)" \
  | grep -q 'BEGIN PGP MESSAGE' || note "the generated document is not encrypted"

# c) Nothing about peers.
ssh layerb-host "gpg --list-only --status-fd 1 --decrypt \$(ls -1t /srv/layerb/encrypted/documents/$SUBJECT/*.selfview.asc | head -1) 2>/dev/null | grep -c ENC_TO" \
  | grep -qx 1 || note "the document is encrypted to more than one recipient"

# d) The run is in the access log.
n=$(ssh layerb-host "grep -l 'session_id: \"at095\"' /srv/layerb/encrypted/accesslog/*.yaml 2>/dev/null | wc -l")
[ "$n" -ge 1 ] || note "the generation run was not written to the Layer B access log"

# e) No capability is required to read it (D110): the subject is not a holder.
# Informational only - this is not an AT-095 pass/fail clause, and the
# capability-holders artifact (contracts/access/access-inputs.yaml,
# layer_b.capability_holders_artifact) is a FROZEN contract L0 owns
# (PARTITION.md rule 2) that has not been authored yet (see L5-98-DEEP-REVIEW.md
# B-09). The original draft read it unconditionally under `set -e`, so AT-095
# would abort here with no useful message the moment this cross-lane
# dependency is missing, rather than skipping an advisory check. Guarded so a
# missing contract cannot crash the test whose four lettered clauses above are
# what §98.6 actually gates on.
if [ -f contracts/access/access-inputs.yaml ]; then
  HOLDERS=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
  if [ -n "$HOLDERS" ] && [ -f "$HOLDERS" ] \
     && yq -r '.capabilities["people-intelligence"].holders[]' "$HOLDERS" 2>/dev/null | grep -qx "$SUBJECT"; then
    echo "AT-095_NOTE subject holds people-intelligence; run this test with a non-holder subject"
  fi
else
  echo "AT-095_NOTE contracts/access/access-inputs.yaml not yet authored by L0 (B-09); skipping the capability-holder cross-check"
fi

if [ "$FAILS" -eq 0 ]; then echo "AT-095_PASS"; else echo "AT-095_FAILED $FAILS"; exit 1; fi
