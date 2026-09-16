#!/usr/bin/env bash
# AT-097: no people datasource entry and no dashboard reference exists in the
# shared instance's provisioning - verified in the provisioned configuration,
# never inferred from panel visibility (D75).
set -euo pipefail
hits=$(grep -RniE 'layer-?b|people|person|performance-evidence' \
        ops-vm/grafana/provisioning ops-vm/grafana/dashboards \
        --include='*.yaml' --include='*.yml' --include='*.json' \
        | grep -v 'NEVER registered here' || true)
if [ -n "$hits" ]; then echo "NO-PEOPLE-DATASOURCE-SHARED: FAIL"; echo "$hits"; exit 1; fi
echo "NO-PEOPLE-DATASOURCE-SHARED: PASS"
