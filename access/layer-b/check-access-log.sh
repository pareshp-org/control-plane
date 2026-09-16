#!/usr/bin/env bash
# access/layer-b/check-access-log.sh
set -euo pipefail
FAILS=0
note() { echo "LOG_FAIL $1"; FAILS=$((FAILS+1)); }

# Schema declares the three Section 90.3 fields. Checked against the repo -
# no host needed for this half.
for f in actor subject at; do
  yq -r '.record.required_fields[]' ops-vm/layer-b/accesslog/schema.yaml | grep -qx "$f" \
    || note "required field '$f' missing from the access-log schema"
done
[ "$(yq -r '.actor_rules.machine_identity_permitted' ops-vm/layer-b/accesslog/schema.yaml)" = "false" ] \
  || note "schema permits a machine identity as actor"

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "LOG_INDETERMINATE layerb-host unreachable ($FAILS repo-side finding(s) above)"
  [ "$FAILS" -eq 0 ] && exit 2 || exit 1
fi

# Application-level log exists on the host and refuses a machine identity.
ssh layerb-host 'test -d /srv/layerb/encrypted/accesslog' || note "access log directory absent"
if ssh layerb-host '/srv/layerb/config/accesslog/record-access.sh reconciler alice layer-b-m query s1' >/dev/null 2>&1; then
  note "machine identity accepted by record-access.sh"
fi

# Host-level audit is loaded and keyed.
k=$(ssh layerb-host 'sudo auditctl -l | grep -c layerb_store' || true)
[ "$k" -ge 1 ] || note "auditd rule for the store path not loaded"

# Audit shipping is write-only: the host cannot read back what it shipped.
if ssh layerb-host 'aws s3 ls s3://layerb-audit/ --profile layerb-audit-writer' >/dev/null 2>&1; then
  note "the host can read the shipped audit trail"
fi

if [ "$FAILS" -eq 0 ]; then echo "LOG_OK 8/8"; else echo "LOG_FAILED $FAILS"; exit 1; fi
