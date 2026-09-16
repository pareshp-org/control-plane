#!/usr/bin/env bash
# infra/layer-b/check-encryption.sh
# Usage: check-encryption.sh repo | check-encryption.sh host
set -euo pipefail
MODE="${1:-repo}"
DECL="infra/layer-b/encrypted-volume.yaml"
fail() { echo "ENC_FAIL $1"; exit 1; }

if [ "$MODE" = "repo" ]; then
  [ "$(yq -r '.integrity_check.method' "$DECL")" = "decrypt-plus-checksum-manifest" ] \
    || fail "integrity check method is not the Section 45.4 method"
  [ "$(yq -r '.integrity_check.opens_documents' "$DECL")" = "false" ] \
    || fail "integrity check declares that it opens documents"
  [ "$(yq -r '.key_custody.escrow' "$DECL")" = "Section 14.4 sealed escrow" ] \
    || fail "key custody is not the Section 14.4 escrow"
  # No Layer B content in this org-readable repository (Section 90.3).
  # A path merely living under a directory named evidence/selfview/bundle is
  # not itself Layer B content - L5-03-07, L5-03-10 and others are REQUIRED
  # by their own task specs to ship tooling at exactly such paths
  # (ops-vm/layer-b/selfview/generate-selfview.sh and its siblings; a
  # .gitkeep placeholder in access/tests/evidence/). This check exists to
  # catch an actual generated document or data file accidentally committed,
  # so it excludes known source/config/placeholder extensions rather than
  # flagging every file whose directory happens to share a name with the
  # runtime store. Confirmed against a fixture: the tooling in
  # ops-vm/layer-b/selfview/ used to trip this check the moment L5-03-10 was
  # implemented, which cannot have been the intent.
  n=$(git ls-files | grep -E '^(access|infra|ops-vm|notify|assets)/' \
      | grep -viE '\.(sh|yaml|yml|md|py|json|gitkeep)$' \
      | grep -cE '(evidence|self-?view|bundle)' || true)
  [ "$n" -eq 0 ] || fail "$n Layer B content file(s) tracked in the repository"
  echo "ENC_REPO_OK 4/4"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
    echo "ENC_HOST_INDETERMINATE layerb-host unreachable"; exit 2
  fi
  MNT=$(yq -r '.volume.mount_point' "$DECL")
  MAP=$(yq -r '.volume.mapper_name' "$DECL")
  t=$(ssh layerb-host "lsblk -no TYPE /dev/mapper/$MAP 2>/dev/null" || echo none)
  [ "$t" = "crypt" ] || fail "store device type is '$t', expected 'crypt'"
  ssh layerb-host "mountpoint -q $MNT" || fail "store not mounted at $MNT"
  perm=$(ssh layerb-host "stat -c %a $MNT")
  [ "$perm" = "700" ] || fail "store mode is $perm, expected 700"
  stray=$(ssh layerb-host "find /srv/layerb /var/lib/grafana -maxdepth 3 -type d \\( -name documents -o -name postgres \\) ! -path '$MNT/*' 2>/dev/null | wc -l")
  [ "$stray" -eq 0 ] || fail "$stray store directory(ies) outside the encrypted volume"
  echo "ENC_HOST_OK 4/4"
  exit 0
fi
fail "unknown mode $MODE"
