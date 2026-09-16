# Layer B backup credential - rotation runbook

One page, per Section 40.1 ("A one-page rotation runbook lives in the
control-plane repository").

1. A `devops`-capability holder issues a new append-only, write-only object-store
   credential in the independent provider domain. Scope: `s3:PutObject` on
   `s3://layerb-backups/*` and nothing else.
2. Install it at `/srv/layerb/secrets/backup_credential` on `layerb-host`.
3. Run `infra/layer-b/check-backup-credential.sh`. It must print `BKP_OK 6/6`.
4. Run `infra/layer-b/backup-run.sh` once. It must print `BACKUP_OK`.
5. **Re-escrow the replacement** in the Section 14.4 escrow before recording the
   rotation as done. Section 14.4: re-escrow "is a blocking step in the rotation
   runbook (Section 40.1): a rotation is not recordable as done until the
   replacement is escrowed."
6. Run a manual reconciliation run and require it to complete clean. Section 40.1:
   "a credential that rotates but no longer reconciles has not been rotated, it
   has been broken."
7. Revoke the old credential.
