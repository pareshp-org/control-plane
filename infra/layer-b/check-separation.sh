#!/usr/bin/env bash
# infra/layer-b/check-separation.sh
# Usage: check-separation.sh repo   (runs anywhere, reads the declarations)
#        check-separation.sh host   (needs the ops-vm and layerb-host SSH aliases)
set -euo pipefail
MODE="${1:-repo}"
OPS="infra/hosts/ops-vm.yaml"
LB="infra/hosts/layerb-host.yaml"
fail() { echo "SEP_FAIL $1"; exit 1; }

if [ "$MODE" = "repo" ]; then
  a=$(yq -r '.host_id' "$OPS"); b=$(yq -r '.host_id' "$LB")
  [ "$a" != "$b" ] || fail "SEP-1 identical host_id $a"
  [ "$(yq -r '.holds_layer_b_store' "$OPS")" = "false" ] || fail "SEP-1 ops-vm declares the Layer B store"
  [ "$(yq -r '.holds_layer_b_store' "$LB")"  = "true"  ] || fail "SEP-1 layerb-host does not declare the store"
  [ "$(yq -r '.holds_secret_tier' "$LB")" = "none" ] || fail "SEP-2 layerb-host declares a secret tier"
  [ "$(yq -r '.holds_secret_tier' "$OPS")" = "control-plane" ] || fail "SEP-2 ops-vm tier misdeclared"
  [ "$(yq -r '.machine_identity_access' "$LB")" = "none" ] || fail "SEP-4 machine identity declared on layerb-host"
  echo "SEP_REPO_OK 4/4"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  # Both SSH aliases must actually be reachable before their absence of a
  # shared key can mean anything. An unreachable alias must not read as an
  # empty (therefore "disjoint") key list - that would report SEP_HOST_OK on
  # an estate that was never checked at all.
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ops-vm true 2>/dev/null; then
    echo "SEP_HOST_INDETERMINATE ops-vm unreachable"; exit 2
  fi
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
    echo "SEP_HOST_INDETERMINATE layerb-host unreachable"; exit 2
  fi
  ssh ops-vm     'cut -d" " -f2 ~/.ssh/authorized_keys 2>/dev/null | sort' > /tmp/l5_ops_keys
  ssh layerb-host 'cut -d" " -f2 ~/.ssh/authorized_keys 2>/dev/null | sort' > /tmp/l5_lb_keys
  shared=$(comm -12 /tmp/l5_ops_keys /tmp/l5_lb_keys | grep -c . || true)
  rm -f /tmp/l5_ops_keys /tmp/l5_lb_keys
  [ "$shared" -eq 0 ] || fail "SEP-3 $shared shared authorised key(s)"
  lb_tier=$(ssh layerb-host 'ls -1 /var/lib/control-plane-credentials 2>/dev/null | wc -l')
  [ "$lb_tier" -eq 0 ] || fail "SEP-2 fifth-tier credential store present on layerb-host"
  echo "SEP_HOST_OK 2/2"
  exit 0
fi
fail "unknown mode $MODE"
