# Handoff: the three D87 Blocking reconciliation rows

Section 39.5 states that *"Reconciliation carries three Blocking rows for this
posture (Section 53.1)."* The reconciler is **lane L3's** (`reconciler/**`), and
the privileged workflows are **lane L2's** (`.github/workflows/**`). Lane L5
owns neither and edits neither (PARTITION rules 1 and 4).

L5 has built the three checks as standalone executables, each proven against a
fixture, each exiting **4** on a Blocking finding:

| Row | Statement | Executable |
| --- | --- | --- |
| D87-ROW-1 | A self-hosted runner in the `privileged` group registered non-ephemerally | `infra/runners/d87/check-ephemeral-registration.sh` |
| D87-ROW-2 | A privileged workflow resolving to a shared-pool label | `infra/runners/d87/check-privileged-workflow-tier.sh` |
| D87-ROW-3 | A branch-push-triggered workflow admitted to the `privileged` group | `infra/runners/d87/check-no-branch-push-in-privileged.sh` |

Each takes one tab-separated listing produced read-only from the platform; the
input shapes are documented in the head comment of each script.

**For L3:** wire the three as Blocking reconciliation rows in Section 53.1's
declared-versus-actual table. The closed privileged-workflow set lives in
`infra/runners/d87/separation.yaml`; read it, do not restate it.

**For L2:** Section 39.5 additionally requires the separation to be *"asserted in
the workflow, not only in configuration"* - each privileged workflow fails closed
unless the runner it resolved to carries the `privileged` label or is hosted.
That assertion belongs inside the workflow files and is not built here.
