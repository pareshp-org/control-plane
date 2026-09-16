# Operations-VM rebuild runbook (source)

**Spec:** Section 45.4 (the 4-hour clock), Section 51.5 (disposable
operations VM). **Target:** `infra/hosts/ops-vm.yaml`'s
`rebuild_target_hours: 4` -- the single source of truth for the clock; this
file declares no second copy of that number.

**Scope.** This runbook rebuilds `infra/hosts/ops-vm.yaml`'s host from
nothing to serving traffic. It does not rebuild the Layer B host
(`infra/hosts/layerb-host.yaml`, `holds_layer_b_store: true`, its own
separate runbook per D95's host-separation rule) and it does not restore
data -- `ops-vm/checks/restore-rotation-coverage.sh` and the object-locked
backup bucket (`ops-vm/assisted/vm-buildout-request.md` step 6) cover
restore. This runbook assumes the backup target already exists; it rebuilds
the disposable compute, nothing durable.

Every step names the file that performs it and an estimated duration. A step
whose file does not exist is a runbook that cannot execute -- `ops-vm/tools/
rebuild_clock.py --validate` refuses to certify a step against a missing
file, exactly the defect this lane's own deep review (L5-98-DEEP-REVIEW.md
B-21) found in an earlier, uncommitted attempt at this same runbook: timers
referencing undefined variables, and no step installing the unit files it
later tries to enable.

| Step | Action | Performed by | Estimated minutes |
|---|---|---|---|
| R01 | Provision the replacement host, matching `infra/hosts/ops-vm.yaml` | `ops-vm/assisted/vm-buildout-request.md` (ASSISTED -- out of this clock; the clock starts at R02, once compute exists) | 0 |
| R02 | Base OS packages and the docker engine | `ops-vm/lib/common.sh` (`require_file`, environment preamble every later step sources) | 15 |
| R03 | Apply the SSH shell-gate hardening | `infra/network/check-shell-gate.sh` (run to confirm, not to configure -- host imaging is expected to already match; a FAIL here stops the runbook) | 5 |
| R04 | Render and install the pinned component versions | `ops-vm/stack/versions.env.example` -> `ops-vm/stack/versions.env` (operator supplies the real digests; `ops-vm/checks/versions-pinned.sh` verifies) | 10 |
| R05 | Bring up the shared stack (Grafana, Prometheus) | `ops-vm/provision/30-stack-up.sh` | 20 |
| R06 | Confirm the stack answers only on loopback / the private path | `ops-vm/checks/stack-loopback-only.sh` | 5 |
| R07 | Install every systemd unit under `ops-vm/systemd/` into `/etc/systemd/system/` and `systemctl daemon-reload` | `ops-vm/systemd/*.service`, `ops-vm/systemd/*.timer` (install step; this runbook is itself the "no step installs the unit files" fix B-21 named) | 10 |
| R08 | Enable and start `health-report.timer` | `ops-vm/systemd/health-report.timer`, `ops-vm/systemd/health-report.service` | 5 |
| R09 | Enable and start `expiry-check.timer` | `ops-vm/systemd/expiry-check.timer`, `ops-vm/systemd/expiry-check.service` | 5 |
| R10 | Enable and start `restore-rotation.timer` | `ops-vm/systemd/restore-rotation.timer`, `ops-vm/systemd/restore-rotation.service` | 5 |
| R11 | Enable and start `org-export.timer` | `ops-vm/systemd/org-export.timer`, `ops-vm/systemd/org-export.service` | 5 |
| R12 | Enable and start `scorecard.timer` | `ops-vm/systemd/scorecard.timer`, `ops-vm/systemd/scorecard.service` | 5 |
| R13 | Enable and start `renovate.timer` | `ops-vm/systemd/renovate.timer`, `ops-vm/systemd/renovate.service` | 5 |
| R14 | Enable and start `deadman-heartbeat.timer` | `ops-vm/systemd/deadman-heartbeat.timer`, `ops-vm/systemd/deadman-heartbeat.service` | 5 |
| R15 | Re-provision the ops-VM credential store and hardware-key shell gate | `access/secrets/checks/rotation-complete.sh` (the store itself is re-escrowed, not rebuilt from a backup -- Section 40.1 fifth-tier discipline) | 20 |
| R16 | Confirm off-VM liveness reports the host back in | `infra/deadman/check-off-vm.sh` | 5 |
| R17 | Run the post-patch smoke checklist against the rebuilt host | `ops-vm/checks/post-patch-smoke.sh` | 15 |
| R18 | Confirm Grafana provisioning matches git (datasources, dashboards) | `ops-vm/checks/grafana-provisioned.sh` | 10 |

**Total estimated:** 145 minutes (2h 25m) against a 240-minute (4-hour)
target -- `ops-vm/tools/rebuild_clock.py --validate` computes this from the
table above, not from a hand-typed sum, so an edited table is re-checked
automatically.

## L0 handoff

This runbook rebuilds `ops-vm.yaml`'s host only. The Layer B host
(`layerb-host.yaml`) and the durable registries/records repositories are
out of this file's scope; see `ops-vm/rebuild/L0-HANDOFF.md` for exactly
what is and is not covered, and who owns the rest.
