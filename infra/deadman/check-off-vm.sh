#!/usr/bin/env bash
# D94: outside the VM, outside GitHub, outside the product providers.
# Each leg's declared provider is compared against the operations VM's provider,
# against github, and against every infrastructure.provider the product registry
# declares. The registry is read as DATA, read-only.
set -euo pipefail
WD="${1:?usage: check-off-vm.sh <watchdog.yaml> <ops-vm-provider> <product-registry.yaml>}"
OPSP="${2:?}"
REG="${3:?}"
[ -f "$WD" ] || { echo "DEADMAN-OFF-VM: FAIL (no $WD)"; exit 1; }
[ -f "$REG" ] || { echo "DEADMAN-OFF-VM: FAIL-CLOSED (product registry unreadable: $REG)"; exit 1; }
prov=$(awk -F': *' '/^provider:/{print $2}' "$WD" | tr -d '"' | head -1)
[ -n "$prov" ] || { echo "DEADMAN-OFF-VM: FAIL (watchdog declares no provider)"; exit 1; }
grep -q '^runs_off_operations_vm: true$' "$WD" \
  || { echo "DEADMAN-OFF-VM: FAIL (runs_off_operations_vm is not true)"; exit 1; }
fail=0
[ "$prov" != "$OPSP" ] || { echo "provider equals the operations VM provider: $prov"; fail=1; }
[ "$prov" != "github" ] || { echo "provider is github"; fail=1; }
if python3 -c '
import sys, yaml
reg = yaml.safe_load(open(sys.argv[1])) or {}
prov = sys.argv[2]
names = {(p.get("infrastructure") or {}).get("provider") for p in reg.get("products", [])}
sys.exit(0 if prov in names else 1)' "$REG" "$prov"; then
  echo "provider is a product infrastructure provider: $prov"; fail=1
fi
if [ "$fail" -eq 0 ]; then echo "DEADMAN-OFF-VM: PASS"; else echo "DEADMAN-OFF-VM: FAIL"; exit 1; fi
