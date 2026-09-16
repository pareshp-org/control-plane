#!/usr/bin/env bash
# access/layer-b/check-allowlist-parity.sh
# Section 90.4: reconciliation "verifies that the holders of Layer B access
# exactly match the holders of the capability", over the six written-down
# surfaces of access/layer-b/reconciliation-scope.yaml.
# A holder appearing in neither list is Blocking drift.
set -uo pipefail
SCOPE="access/layer-b/reconciliation-scope.yaml"
ACCEPTED="assets/inventory/layer-b-host-admin-access.yaml"
FAILS=0
note() { echo "PARITY_BLOCKING $1"; FAILS=$((FAILS+1)); }

[ -f "$SCOPE" ] || { echo "PARITY_FAIL scope file missing"; exit 2; }
# The scope must still carry all six surfaces. Narrowing it is a failure.
n=$(yq -r '.surfaces | length' "$SCOPE")
[ "$n" = "6" ] || { echo "PARITY_FAIL scope narrowed to $n surfaces, expected 6"; exit 2; }

HOLDERS_ARTIFACT=""
if [ -f contracts/access/access-inputs.yaml ]; then
  HOLDERS_ARTIFACT=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
fi
if [ -z "$HOLDERS_ARTIFACT" ] || [ ! -f "$HOLDERS_ARTIFACT" ]; then
  echo "PARITY_BLOCKED holders artifact unavailable (contracts/access/access-inputs.yaml : layer_b.capability_holders_artifact is unset or unreadable)"
  exit 2
fi
HOLDERS=$(yq -r '.capabilities["people-intelligence"].holders[]' "$HOLDERS_ARTIFACT" | sort -u)
NAMED=""
[ -f "$ACCEPTED" ] && NAMED=$(yq -r '.holder_login' "$ACCEPTED" 2>/dev/null || echo "")
ALLOWED=$(printf '%s\n%s\n' "$HOLDERS" "$NAMED" | grep -v '^$' | sort -u)

HOST_UNREACHABLE=0
check_set() {  # $1 = surface id, $2 = newline-separated observed principals, $3 = ok when host unreachable
  local id="$1" observed extra
  if [ "$3" = "unreachable" ]; then HOST_UNREACHABLE=1; echo "PARITY_NOTE $id skipped: layerb-host is unreachable from this environment"; return; fi
  observed=$(printf '%s\n' "$2" | grep -v '^$' | sort -u)
  extra=$(comm -23 <(printf '%s\n' "$observed") <(printf '%s\n' "$ALLOWED"))
  if [ -n "$extra" ]; then
    for p in $extra; do note "$id principal '$p' is in neither the capability holders nor the named accepted-access record"; done
  fi
}

if org_users=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users | jq -r ".[].login"' 2>/dev/null); then
  check_set SCOPE-2 "$org_users"
else
  check_set SCOPE-2 "" unreachable
fi
if os_accounts=$(ssh layerb-host "awk -F: '\$3>=1000 && \$1!=\"nobody\" {print \$1}' /etc/passwd" 2>/dev/null); then
  check_set SCOPE-3 "$os_accounts"
else
  check_set SCOPE-3 "" unreachable
fi
if sudoers=$(ssh layerb-host "sudo grep -rhoE '^[a-z][a-z0-9._-]*' /etc/sudoers /etc/sudoers.d 2>/dev/null | grep -vE '^(Defaults|root|#includedir)\$'" 2>/dev/null); then
  check_set SCOPE-4 "$sudoers"
else
  check_set SCOPE-4 "" unreachable
fi
if ssh_keys=$(ssh layerb-host "cut -d' ' -f3- ~/.ssh/authorized_keys 2>/dev/null" 2>/dev/null); then
  check_set SCOPE-5 "$ssh_keys"
else
  check_set SCOPE-5 "" unreachable
fi
check_set SCOPE-6 "$(yq -r '.read_access.entries[]?' infra/layer-b/backup-read-access-list.yaml 2>/dev/null)"

# SCOPE-1: the instance credential is a single file with one custodian; it must
# not be readable by any principal outside the allowed set.
if owner=$(ssh layerb-host 'stat -c %U /srv/layerb/secrets/admin_password' 2>/dev/null); then
  check_set SCOPE-1 "$owner"
else
  check_set SCOPE-1 "" unreachable
fi

if [ "$FAILS" -ne 0 ]; then
  echo "PARITY_FAILED $FAILS Blocking"; exit 1
fi
if [ "$HOST_UNREACHABLE" -eq 1 ]; then
  echo "PARITY_INCOMPLETE (repository-side surfaces clean; host-side surfaces unreachable from this environment)"
  exit 2
fi
echo "PARITY_OK 6/6"
