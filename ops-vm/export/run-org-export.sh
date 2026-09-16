#!/usr/bin/env bash
# Scheduled organisation export (Section 45.3). Encrypt locally with a key held
# outside GitHub, then write with an append-only, write-only credential to
# object-locked, versioned storage in a different provider and credential domain.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/export/storage.env
set -a; . ops-vm/export/storage.env; set +a
require_env GITHUB_ORG EXPORT_PROVIDER EXPORT_ENDPOINT EXPORT_BUCKET EXPORT_OBJECT_LOCK \
            EXPORT_VERSIONING EXPORT_RETENTION_DAYS EXPORT_ACCESS_KEY_ID \
            EXPORT_SECRET_ACCESS_KEY EXPORT_ENCRYPTION_RECIPIENTS_FILE \
            EXPORT_ENCRYPTION_KEY_ESCROW EXPORT_ENCRYPTION_KEY_ASSET_ID \
            EXPORT_OWNER

[ "$EXPORT_OBJECT_LOCK" = "on" ] || fail_closed "object lock must be on (Section 45.3)"
[ "$EXPORT_VERSIONING" = "on" ] || fail_closed "versioning must be on (Section 45.3)"
require_file "$EXPORT_ENCRYPTION_RECIPIENTS_FILE"

ops-vm/checks/export-credential.sh || fail_closed "export credential is not append-only/write-only"

stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT

# Repositories, issues, pull requests and review records: migrations REST API.
# The repository list is generated from the registry at run time, never listed
# in this repository (invariant 52).
repos=$(list-repositories --from-registry)
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to export an empty set"
python3 -c 'import json,sys;print(json.dumps({"repositories":sys.argv[1].split(),"lock_repositories":False}))' \
  "$repos" > "$work/repos.json"
gh api --method POST "/orgs/$GITHUB_ORG/migrations" --input "$work/repos.json" > "$work/migration.json"
mig=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["id"])' "$work/migration.json")
gh api "/orgs/$GITHUB_ORG/migrations/$mig/archive" > "$work/migration-$stamp.tar.gz"

# Projects v2 boards: NOT in migration archives; separate GraphQL dump (D80).
gh api graphql -F org="$GITHUB_ORG" -f query="$(cat ops-vm/export/projects.graphql)" \
  > "$work/projects-$stamp.json"

# Audit log: Enterprise-only API; excluded on the Team plan and named as excluded.
cp ops-vm/export/EXCLUSIONS.md "$work/EXCLUSIONS.md"

sha256sum "$work"/* > "$work/manifest-$stamp.sha256"
ops-vm/checks/export-no-secret-values.sh "$work" || fail_closed "a secret value reached the export staging area (Section 45.1)"

age --encrypt --recipients-file "$EXPORT_ENCRYPTION_RECIPIENTS_FILE" \
    --output "$work/org-export-$stamp.age" \
    <(tar -C "$work" -cf - "migration-$stamp.tar.gz" "projects-$stamp.json" "manifest-$stamp.sha256" "EXCLUSIONS.md")

WRITE_TOKEN="$EXPORT_SECRET_ACCESS_KEY" ops-vm/export/put.sh "$work/org-export-$stamp.age"

now=$(date -u +%s)
printf 'ops_vm_job_last_success_timestamp{job_name="org-export"} %s\n' "$now" \
  > /var/lib/ops-vm/metrics/org-export-freshness.prom
record_run org-export ok "owner=$EXPORT_OWNER key_asset=$EXPORT_ENCRYPTION_KEY_ASSET_ID"
