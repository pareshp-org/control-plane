# Rebuild runbook — what Lane 5 covers and what it hands off

**Lane 5 writes no file under `docs/`.** `docs/control-plane-rebuild.md`
(spec Section 45.4) is an L0-owned file (lanes/L5-98-DEEP-REVIEW.md M-16
already named this trap for an earlier, uncommitted attempt at this
runbook: the charter routes the rebuild runbook to `ops-vm/rebuild/` with
no note that the spec names a `docs/**` file, which is L0's). Lane 5
produces `ops-vm/rebuild/runbook.src.md` (the source steps, machine-checked
by `ops-vm/tools/rebuild_clock.py`) and hands it to L0 to fold into
`docs/control-plane-rebuild.md`.

## What `runbook.src.md` covers

- The disposable compute for `infra/hosts/ops-vm.yaml` only: OS packages,
  the shared stack, every `ops-vm/systemd/*` unit, the ops-VM credential
  store, and the confirmation checks (loopback-only, off-VM liveness,
  post-patch smoke, Grafana provisioning).

## What it does not cover, and who owns it

| Out of scope | Owner | Why |
|---|---|---|
| The Layer B host (`infra/hosts/layerb-host.yaml`) | Lane 5, a separate runbook | D95 requires host separation from the shared stack; a shared rebuild runbook for both hosts would be exactly the collapsed boundary D95 forbids. |
| Restoring registries/records from backup | L3 (reconciler) / L1 (registries) | The rebuild runbook rebuilds compute, not data; restore is a distinct obligation (`ops-vm/checks/restore-rotation-coverage.sh` covers the backup-freshness leg only). |
| VM provisioning itself (R01) | Human, ASSISTED | `ops-vm/assisted/vm-buildout-request.md` — cloud console, payment, private network path. The 4-hour clock in `rebuild_clock.py` starts at R02, once compute exists, per the same boundary Section 45.4 draws between "the VM exists" and "the VM serves." |
| Folding this file into `docs/control-plane-rebuild.md` | L0 | `docs/**` is not a Lane 5 path (PARTITION.md). |
