#!/usr/bin/env bash
# Section 45.4: the drill copy is destroyed ON EVIDENCE, never on attestation.
# The record carries the provider's post-drill resource listing for the drill tag
# showing zero resources, and names the explicit deletion of the drill host's
# volume snapshots and provider-side backups, which a filesystem wipe does not
# reach. A drill record filed without this evidence is Blocking drift.
set -euo pipefail
R="${1:?usage: drill-zero-resources.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-ZERO-RESOURCES: FAIL (no $R)"; exit 1; }
g() { awk -F': *' -v k="$1" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"'; }
fail=0
tag=$(g resource_tag);      [ -n "$tag" ] || { echo "resource_tag is empty"; fail=1; }
lst=$(g provider_resource_listing)
[ -n "$lst" ] || { echo "provider_resource_listing is empty - attestation is not evidence"; fail=1; }
[ -z "$lst" ] || [ -f "$lst" ] || { echo "provider_resource_listing does not exist: $lst"; fail=1; }
rem=$(g resources_remaining)
[ "$rem" = "0" ] || { echo "resources_remaining is '$rem', not 0"; fail=1; }
for k in volume_snapshots_deleted provider_side_backups_deleted; do
  v=$(g "$k"); [ -n "$v" ] || { echo "$k is empty - a filesystem wipe does not reach these"; fail=1; }
done
docs=$(g documents_opened)
[ "$docs" = "0" ] || { echo "documents_opened is '$docs', not 0 - the integrity check opens no document"; fail=1; }
if [ "$fail" -eq 0 ]; then echo "DRILL-ZERO-RESOURCES: PASS"; else echo "DRILL-ZERO-RESOURCES: FAIL (Blocking drift)"; exit 4; fi
