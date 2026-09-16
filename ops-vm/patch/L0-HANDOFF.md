# Handoff: the tool-register rows for the control-plane stack

Section 51.4 tracks the control-plane patch cadence **through the tool register**
of Section 62.1. The register is `tools.yaml` - a root-level control-plane
registry, and part of **subsystem O (governance registries and jobs)**, which is
**unassigned in PARTITION v1**. Lane L5 owns `ops-vm/**`, `infra/**`,
`assets/**` and `notify/**`, and writes neither.

What L5 has built and where it is:

| Built | Path |
| --- | --- |
| The per-component cadence file the VM reads | `ops-vm/patch/cadence.yaml.example` (empty values; the real file is supplied on the host) |
| The SIG-36 staleness computation | `ops-vm/checks/patch_staleness.py` |
| The post-patch smoke checklist | `ops-vm/patch/smoke-checklist.yaml`, `ops-vm/checks/post-patch-smoke.sh` |
| The singleton patch driver | `ops-vm/patch/patch-driver.sh` |

What L0 must decide and own, and what L5 will not do:

1. Assign subsystem O.
2. Create the `tools.yaml` rows for `grafana-shared`, `grafana-layerb`,
   `prometheus`, `proxy` and `ops-vm-os`, each with the `current_version`,
   `upgrade_policy`, `last_reviewed` and `criticality` fields Section 62.1
   declares. (DevLake is deferred from V1 scope per FD-112/PFD-032 and carries
   no row here; re-adding it is gated on `contracts/v1-scope.yaml`'s
   `devlake.trigger`.)
3. Set the cadence value per component. Section 51.4 requires the Layer B
   Grafana component to carry the tightest cadence in the stack; the staleness
   computation fails closed when it does not, so this is a checked constraint on
   the values, not a preference.
