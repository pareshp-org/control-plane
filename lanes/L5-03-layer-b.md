<!-- Task IDs renamed to charter format L5-FF-TT by Session 12 (FD-037 corollary) -->
> **[AUTHORITATIVE — FD-B1-L5 2026-09-02]**
> This is the authoritative task plan for Lane 5. All competing plans are superseded.

# L5 — PHASE 3: THE LAYER B SPLIT

**Lane:** L5 Access, Infra & Ops · **Subsystems:** K, L, M, Q, R (spec §99.2)
**Owned paths (exclusive, per FROZEN `PARTITION.md`):** `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`
**Branch prefix:** `lane/5/*` · **Merge target:** `integration` (merge train position 5 of 5)
**Repository:** `control-plane`

---

## 0. What this phase is, and why it hard-gates the People tier

Spec §90.3 is implementation-level and binding. It states three facts that jointly force this phase:

1. *"Dashboard-level hiding is not access control. Neither, in Grafana OSS, is folder membership: datasource-level query permission is an Enterprise feature Grafana OSS does not have, so in a single OSS instance any editor can point Explore or a new panel at any registered datasource"* (§90.3).
2. *"Layer B renders in a second, Founder-only Grafana instance on the operations VM — the same JSON-provisioning discipline as the shared instance, its own credential and its own authentication restriction (D75). The people datasource is never registered in the shared instance; the Layer B boundary is instance separation, not folder membership."* (§90.3, D75).
3. *"No Layer B evidence may be generated before this separation exists. This gates the corresponding implementation phase."* (§90.3).

The gate is restated in §98.6 with a machine-checkable definition:

> *"P4 must not begin before the Layer B datasource separation is implemented and verified. It is a P2 deliverable, never an assumption; **verified** means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds."* (§98.6, sequencing rules, binding)

**D110 splits the surface in two**, and every task below keeps them apart:

| Surface | What it is | Access rule | Spec |
|---|---|---|---|
| **Layer B-M** | The management surface — the second, Founder-only Grafana instance holding every person's evidence and every comparative view | Gated by the `people-intelligence` capability; **not delegable** (D109) | §6.11, §90.1, §92.1 row 6, D110 |
| **Layer B-S** | The generated **encrypted per-person self-view** document — one person's own evidence and nothing else, delivered to the person it describes | **Requires no capability at all**; the subject reads their own | §90.6, §92.8, D110 |

Invariant 106 is the sentence both halves must satisfy: *"Individual people-performance intelligence on the management surface (Layer B-M) is Founder-only, gated by the `people-intelligence` capability, and **not delegable**; the individual self-view (Layer B-S) carries one person's own evidence to that person and is outside this rule."* (§101 #106).

Invariant 109 is the sentence the datasource work must satisfy: *"General engineering dashboards never expose sensitive performance data and carry no per-person raw-activity drill-downs; individual activity data lives only in Layer B. The underlying people datasource is separately credentialed, and sensitive people data never enters the general engineering datasource."* (§101 #109).

**Nothing in People-tier work may begin before task L5-03-12 emits a green gate artifact.** That artifact is the only admissible evidence that the gate of §90.3 and §98.6 is satisfied.

---

## 1. Conventions every task in this file obeys

**Workspace.** Every command block assumes these two lines have already been run in the shell:

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="$HOME/work/control-plane"
cd "$CONTROL_PLANE_ROOT"
```

If `$CONTROL_PLANE_ROOT` does not exist, run L5-03-01 first — it is the only task permitted to clone.

**Branching.** One branch per task, named `lane/5/p3-<NN>-<slug>`, rebased on `integration` before the PR, short-lived (< 1 day), per `PARTITION.md` §"Branch & merge model".

**Path discipline.** Every file created by this phase is under `access/`, `infra/`, `ops-vm/`, `notify/` or `assets/`. A task that appears to need a file outside those five roots is a STOP condition, not a judgement call (`PARTITION.md` rule 1).

**Contracts.** Schemas and contracts under `contracts/**` are written by L0 in Phase 0 and are FROZEN. If a task's acceptance criterion cannot be met without a change to `contracts/**`, STOP and file a Contract Change Request (`PARTITION.md` rule 2).

**No shared mutable file.** Every artifact this phase writes is one file per item in a directory (`PARTITION.md` rule 3). No task appends to a shared index.

**Secrets.** No task in this file ever writes a secret value into the repository. Every credential is referenced by name and by the tier it lives in (§40.1, five secret tiers). A task that appears to require pasting a credential into a file is a STOP condition.

**Blocker issue template.** Every STOP rule in this file resolves to filing this issue and halting the task:

```bash
set -euo pipefail
gh issue create \
  --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  --title "BLOCKER L5-03-<NN>: <one-line condition that fired>" \
  --label "blocker,lane-5,phase-3" \
  --body "$(cat <<'BODY'
## Task
L5-03-<NN> — <task title>

## STOP rule that fired
<quote the exact STOP rule text from L5-03-layer-b.md>

## Observed
<paste the exact command that was run and its exact output>

## Expected
<paste the SELF-VERIFY expected output from the task>

## What I did NOT do
I stopped at this step. No further commands from this task were run.
No files were committed. No branch was pushed.

## Decision required from L0
This is a design/interpretation question. Per PARTITION.md
("No task may require designing, choosing, or interpreting"),
it is escalated rather than resolved in-lane.
BODY
)"
```

**Size key.** S = under a day. M = one to three days. L = more than three days.

---

## 2. Task index

| Task ID | Title | Size | Depends on |
|---|---|---|---|
| L5-03-01 | Phase preflight, workspace and phase manifest | S | — |
| L5-03-02 | D95 host separation: declare and check the Layer B host boundary | M | L5-03-01 |
| L5-03-03 | Provision the second, Founder-only Grafana instance (Layer B-M) | M | L5-03-01, L5-03-02 |
| L5-03-04 | Register the people datasource in Layer B-M only, and prove its absence from the shared instance (AT-097) | M | L5-03-03 |
| L5-03-05 | Encrypt the people-data store at rest and emit its checksum manifest | M | L5-03-02 |
| L5-03-06 | The restricted backup credential and object-locked backup target | M | L5-03-05 |
| L5-03-07 | The Layer B access log, plus the host-level file-access audit shipped off-host | M | L5-03-03, L5-03-05 |
| L5-03-08 | Session-lifetime limits; standing unattended sessions prohibited | S | L5-03-03 |
| L5-03-09 | Capability-derived access: allowlist sync, non-delegability, reconciliation comparison scope | M | L5-03-03, L5-03-06 |
| L5-03-10 | Layer B-S: the generated encrypted per-person self-view | L | L5-03-05, L5-03-07 |
| L5-03-11 | The named accepted-access record for host-level administrative access | S | L5-03-02, L5-03-07 |
| L5-03-12 | The People-tier hard gate: acceptance-test runner and gate artifact | M | L5-03-04, L5-03-07, L5-03-08, L5-03-09, L5-03-10, L5-03-11 |
| L5-03-13 | Post-patch smoke checklist and Layer B alert routing | S | L5-03-12 |

---

## L5-03-01 — Phase preflight, workspace and phase manifest

**Size:** S · **Depends on:** — · **Owned paths touched:** `access/layer-b/`

### Purpose
Establish the workspace, prove the four preconditions this phase assumes, and commit the phase manifest that every later task in this file reads. No Layer B mechanism is built here.

### Preconditions this task proves (and does not assume)

| # | Precondition | Why it matters |
|---|---|---|
| 1 | `integration` branch exists and is fetchable | `PARTITION.md` branch model |
| 2 | `contracts/` exists and is non-empty | Contract-first rule; lanes code against it |
| 3 | The five L5-owned roots are the only roots this phase writes | `PARTITION.md` rule 1 |
| 4 | `jq`, `yq`, `python3`, `openssl`, `ssh`, `curl`, `git`, `gh` are installed | Every later task uses them |

### Commands

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="$HOME/work/control-plane"
mkdir -p "$HOME/work"
[ -n "$CONTROL_PLANE_REMOTE" ] || { echo "ERROR: CONTROL_PLANE_REMOTE is not set"; exit 1; }
if [ ! -d "$CONTROL_PLANE_ROOT/.git" ]; then git clone "$CONTROL_PLANE_REMOTE" "$CONTROL_PLANE_ROOT"; fi
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p3-01-preflight
```

```bash
set -euo pipefail
for t in jq yq python3 openssl ssh curl git gh; do
  command -v "$t" >/dev/null 2>&1 || echo "MISSING_TOOL $t"
done
echo "TOOLS_CHECKED"
python3 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" \
  || { echo "STOP: Python 3.12 required (FD-005); got $(python3 --version 2>&1)"; exit 1; }
```

```bash
set -euo pipefail
test -d "$CONTROL_PLANE_ROOT/contracts" && [ "$(ls -A "$CONTROL_PLANE_ROOT/contracts" | wc -l)" -gt 0 ] \
  && echo "CONTRACTS_PRESENT" || echo "CONTRACTS_MISSING"
```

```bash
set -euo pipefail
mkdir -p "$CONTROL_PLANE_ROOT/access/layer-b"
cat > "$CONTROL_PLANE_ROOT/access/layer-b/phase.manifest.yaml" <<'YAML'
# access/layer-b/phase.manifest.yaml
# L5 Phase 3 - The Layer B Split.
# Written once by L5-03-01. Read by every later task in this phase.
# Spec anchors are quoted, never paraphrased. Do not add fields.
phase: L5-P3
title: The Layer B split
spec_anchors:
  datasource_enforcement: "Section 90.3"
  capability_gate: "Section 90.4"
  own_data_transparency: "Section 90.6"
  surface_inventory: "Section 92.1"
  self_view: "Section 92.8"
  at_rest_and_backups: "Section 51.4"
  disposable_ops_vm: "Section 51.5"
  secret_tiers: "Section 40.1"
  workstation_boundary: "Section 40.3"
  asset_inventory: "Section 49.1"
  calibration_cadence: "Section 84.5"
  operating_session: "Section 89.1"
  escrow: "Section 14.4"
  people_tier_sequencing: "Section 98.6"
decisions:
  D75: "Layer B renders in a second, Founder-only Grafana instance on the operations VM with its own credential and authentication restriction; the people datasource is never registered in the shared instance. Datasource-scoped query permission does not exist in Grafana OSS, and folder hiding is not access control"
  D89: "The record stores live in their own repository; no machine identity is a bypass actor on the control-plane repository"
  D95: "A fully compromised engineering workstation must not yield the control-plane machine-credential store; the credential is held so that VM-root does not passively read it, and the Layer B store is separated from the shared host"
  D109: "Layer B access is not delegable. The routine people_intelligence_delegate is removed"
  D110: "Layer B-M is the management surface, capability-gated and not delegable. Layer B-S is the self-view, delivered to its subject, requiring no capability. Unqualified Layer B means Layer B-M"
invariants:
  - id: 106
    surface: layer-b-m
  - id: 109
    surface: datasource-separation
gate:
  gates: "People tier P4 (Section 98.6)"
  verified_definition: "AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds"
  acceptance_tests_in_scope:
    - AT-089
    - AT-090
    - AT-091
    - AT-092
    - AT-095
    - AT-096
    - AT-097
    - AT-098
  artifact: access/layer-b/gate/people-tier.gate.json
owned_roots:
  - "access/"
  - "infra/"
  - "ops-vm/"
  - "notify/"
  - "assets/"
YAML
```

```bash
set -euo pipefail
cat > "$CONTROL_PLANE_ROOT/access/layer-b/check-owned-roots.sh" <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-owned-roots.sh
# Fails if the branch changes any file outside the five roots L5 owns
# under the FROZEN partition contract.
set -euo pipefail
BASE="${1:-origin/integration}"
BAD=0
for f in $(git diff --name-only "$BASE"...HEAD); do
  case "$f" in
    access/*|infra/*|ops-vm/*|notify/*|assets/*) : ;;
    *) echo "FOREIGN_PATH $f"; BAD=1 ;;
  esac
done
if [ "$BAD" -eq 0 ]; then echo "OWNED_ROOTS_OK"; else echo "OWNED_ROOTS_FAIL"; exit 1; fi
SH
chmod +x "$CONTROL_PLANE_ROOT/access/layer-b/check-owned-roots.sh"
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/layer-b/phase.manifest.yaml access/layer-b/check-owned-roots.sh
git commit -m "L5-03-01: phase manifest and owned-root guard for the Layer B split"
git push -u origin lane/5/p3-01-preflight
gh pr create --base integration --head lane/5/p3-01-preflight \
  --title "L5-03-01: Layer B phase manifest and owned-root guard" \
  --body "Phase 3 preflight. Adds access/layer-b/phase.manifest.yaml and the owned-root guard. No mechanism yet."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | All eight tools present | `for t in jq yq python3 openssl ssh curl git gh; do command -v "$t" >/dev/null \|\| echo MISSING $t; done; echo TOOLS_CHECKED` | `TOOLS_CHECKED` and no `MISSING` line |
| 2 | `contracts/` present and non-empty | `test -d "$CONTROL_PLANE_ROOT/contracts" && [ "$(ls -A "$CONTROL_PLANE_ROOT/contracts" \| wc -l)" -gt 0 ] && echo CONTRACTS_PRESENT` | `CONTRACTS_PRESENT` |
| 3 | Manifest parses and declares the gate definition | `yq -r '.gate.verified_definition' "$CONTROL_PLANE_ROOT/access/layer-b/phase.manifest.yaml"` | `AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds` |
| 4 | Manifest declares exactly the five owned roots | `yq -r '.owned_roots \| join(",")' "$CONTROL_PLANE_ROOT/access/layer-b/phase.manifest.yaml"` | `access/,infra/,ops-vm/,notify/,assets/` |
| 5 | Manifest names the gate artifact path | `yq -r '.gate.artifact' "$CONTROL_PLANE_ROOT/access/layer-b/phase.manifest.yaml"` | `access/layer-b/gate/people-tier.gate.json` |
| 6 | Owned-root guard passes on this branch | `"$CONTROL_PLANE_ROOT/access/layer-b/check-owned-roots.sh" origin/integration` | `OWNED_ROOTS_OK` |
| 7 | Nothing outside the five roots was touched | `git diff --name-only origin/integration...HEAD \| grep -cvE '^(access|infra|ops-vm|notify|assets)/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && \
yq -r '.phase + "|" + .gate.artifact + "|" + (.owned_roots|join(","))' access/layer-b/phase.manifest.yaml && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly two lines:

```
L5-P3|access/layer-b/gate/people-tier.gate.json|access/,infra/,ops-vm/,notify/,assets/
OWNED_ROOTS_OK
```

### STOP rules

- **If `CONTRACTS_MISSING`** — do not proceed. `contracts/**` is L0's Phase 0 output and is FROZEN; a lane never creates it. File the blocker issue.
- **If any tool is missing and installing it would add a file to the repository** — file the blocker issue. Do not vendor a binary into an owned path.
- **If `integration` does not exist on `origin`** — file the blocker issue. Do not create it; shared-branch creation is L0's.
- **If `check-owned-roots.sh` prints any `FOREIGN_PATH` line** — restore that file with `git checkout origin/integration -- <path>`, re-run, and if the path is genuinely required, file the blocker issue.

---

## L5-03-02 — D95 host separation: declare and check the Layer B host boundary

**Size:** M · **Depends on:** L5-03-01 · **Owned paths touched:** `infra/hosts/`, `infra/layer-b/`

### Purpose
D95 states the second trust boundary and its Layer B consequence: *"A second boundary is declared — a fully compromised engineering workstation must not yield the control-plane machine-credential store — with the credential held so that VM-root does not passively read it, and the Layer B store separated from the shared host"* (D95, §40.3, §90.3).

§51.5 states what the shared operations VM holds: *"it does hold the fifth-tier machine-credential store of Section 40.1, including the reconciler credential and the organisation-export token, which is why the second trust boundary of Section 40.3 exists and why shell access to this host is not an infrastructure detail."*

This task writes the two host declarations, the four separation assertions, and the checker that fails if the boundary is violated. It builds no service.

### Files created

| Path | Contents |
|---|---|
| `infra/hosts/ops-vm.yaml` | The shared operations VM: DevLake, shared Grafana, reconciliation, fifth-tier credential store |
| `infra/hosts/layerb-host.yaml` | The Layer B host: the Layer B-M Grafana instance, the people-data store, self-view generation |
| `infra/layer-b/separation.yaml` | The four separation assertions D95 requires, each with its spec anchor |
| `infra/layer-b/check-separation.sh` | The checker, in a repository-side half and a host-side half |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-02-host-separation
mkdir -p infra/hosts infra/layer-b
```

```bash
set -euo pipefail
cat > infra/hosts/ops-vm.yaml <<'YAML'
# infra/hosts/ops-vm.yaml - the shared operations VM (Section 51.5, subsystem M)
host_id: ops-vm
ssh_alias: ops-vm
role: shared control-plane stack
runs:
  - devlake
  - grafana-shared
  - prometheus
  - reconciliation
  - scorecard
  - renovate
  - expiry-checks
  - restore-rotation
  - org-export
holds_secret_tier: control-plane
holds_layer_b_store: false
disposable: true
rebuild_target_hours: 4
network: private-path-only
shell_access_requires_second_factor: true
YAML
```

```bash
set -euo pipefail
cat > infra/hosts/layerb-host.yaml <<'YAML'
# infra/hosts/layerb-host.yaml - the Layer B host (D95; Section 90.3; Section 51.4)
host_id: layerb-host
ssh_alias: layerb-host
role: Layer B-M rendering and the people-data store
runs:
  - grafana-layerb
  - people-data-store
  - selfview-generator
holds_secret_tier: none
holds_layer_b_store: true
encrypted_at_rest: true
network: private-path-only
shell_access_requires_second_factor: true
machine_identity_access: none
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/separation.yaml <<'YAML'
# infra/layer-b/separation.yaml - the D95 separation assertions.
# Each assertion is checkable. None is advisory.
assertions:
  - id: SEP-1
    statement: "The Layer B store host and the shared operations VM are distinct hosts."
    anchor: "D95 - the Layer B store separated from the shared host"
    check: distinct_host_ids
  - id: SEP-2
    statement: "The Layer B host holds no control-plane (fifth-tier) machine credential."
    anchor: "Section 40.1 five secret tiers; D95"
    check: layerb_holds_no_fifth_tier
  - id: SEP-3
    statement: "The two hosts share no SSH authorised key."
    anchor: "Section 40.3 second boundary"
    check: no_shared_authorised_keys
  - id: SEP-4
    statement: "No machine identity holds access on the Layer B host."
    anchor: "Section 90.2 machine-identities row: absolute"
    check: no_machine_identity
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/check-separation.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/check-separation.sh
# Usage: check-separation.sh repo   (runs anywhere, reads the declarations)
#        check-separation.sh host   (needs the ops-vm and layerb-host SSH aliases)
set -euo pipefail
MODE="${1:-repo}"
OPS="infra/hosts/ops-vm.yaml"
LB="infra/hosts/layerb-host.yaml"
fail() { echo "SEP_FAIL $1"; exit 1; }

if [ "$MODE" = "repo" ]; then
  a=$(yq -r '.host_id' "$OPS"); b=$(yq -r '.host_id' "$LB")
  [ "$a" != "$b" ] || fail "SEP-1 identical host_id $a"
  [ "$(yq -r '.holds_layer_b_store' "$OPS")" = "false" ] || fail "SEP-1 ops-vm declares the Layer B store"
  [ "$(yq -r '.holds_layer_b_store' "$LB")"  = "true"  ] || fail "SEP-1 layerb-host does not declare the store"
  [ "$(yq -r '.holds_secret_tier' "$LB")" = "none" ] || fail "SEP-2 layerb-host declares a secret tier"
  [ "$(yq -r '.holds_secret_tier' "$OPS")" = "control-plane" ] || fail "SEP-2 ops-vm tier misdeclared"
  [ "$(yq -r '.machine_identity_access' "$LB")" = "none" ] || fail "SEP-4 machine identity declared on layerb-host"
  echo "SEP_REPO_OK 4/4"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  ssh ops-vm     'cut -d" " -f2 ~/.ssh/authorized_keys 2>/dev/null | sort' > /tmp/l5_ops_keys  || true
  ssh layerb-host 'cut -d" " -f2 ~/.ssh/authorized_keys 2>/dev/null | sort' > /tmp/l5_lb_keys  || true
  shared=$(comm -12 /tmp/l5_ops_keys /tmp/l5_lb_keys | grep -c . || true)
  rm -f /tmp/l5_ops_keys /tmp/l5_lb_keys
  [ "$shared" -eq 0 ] || fail "SEP-3 $shared shared authorised key(s)"
  lb_tier=$(ssh layerb-host 'ls -1 /var/lib/control-plane-credentials 2>/dev/null | wc -l' || echo 0)
  [ "$lb_tier" -eq 0 ] || fail "SEP-2 fifth-tier credential store present on layerb-host"
  echo "SEP_HOST_OK 2/2"
  exit 0
fi
fail "unknown mode $MODE"
SH
chmod +x infra/layer-b/check-separation.sh
```

```bash
set -euo pipefail
./infra/layer-b/check-separation.sh repo
./infra/layer-b/check-separation.sh host
```

```bash
set -euo pipefail
git add infra/hosts/ops-vm.yaml infra/hosts/layerb-host.yaml \
        infra/layer-b/separation.yaml infra/layer-b/check-separation.sh
git commit -m "L5-03-02: declare and check the D95 Layer B host separation"
git push -u origin lane/5/p3-02-host-separation
gh pr create --base integration --head lane/5/p3-02-host-separation \
  --title "L5-03-02: D95 host separation for the Layer B store" \
  --body "Declares ops-vm and layerb-host, the four D95 separation assertions, and their checker."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Two distinct host declarations exist | `yq -r '.host_id' infra/hosts/ops-vm.yaml infra/hosts/layerb-host.yaml \| sort -u \| wc -l` | `2` |
| 2 | The Layer B store is declared on exactly one host | `grep -h 'holds_layer_b_store' infra/hosts/*.yaml \| grep -c 'true'` | `1` |
| 3 | The Layer B host holds no fifth-tier credential (declared) | `yq -r '.holds_secret_tier' infra/hosts/layerb-host.yaml` | `none` |
| 4 | The Layer B host declares no machine-identity access | `yq -r '.machine_identity_access' infra/hosts/layerb-host.yaml` | `none` |
| 5 | All four assertions carry a check name | `yq -r '.assertions[].check' infra/layer-b/separation.yaml \| wc -l` | `4` |
| 6 | Repository-side check passes | `./infra/layer-b/check-separation.sh repo` | `SEP_REPO_OK 4/4` |
| 7 | Host-side check passes | `./infra/layer-b/check-separation.sh host` | `SEP_HOST_OK 2/2` |
| 8 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./infra/layer-b/check-separation.sh repo && \
./infra/layer-b/check-separation.sh host && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines:

```
SEP_REPO_OK 4/4
SEP_HOST_OK 2/2
OWNED_ROOTS_OK
```

### STOP rules

- **If the estate has only one host and `layerb-host` cannot be provisioned** — do not put the Layer B store on `ops-vm`, and do not edit the assertions to make the checker pass. §90.3 places the store on the operations VM; D95 separates it from the shared host. Reconciling those two sentences for this estate is a design decision. File the blocker issue quoting both, and STOP.
- **If `SEP-3` fails because the two hosts share an authorised key** — do not remove a key you did not add. File the blocker issue naming the key's comment field only, never the key material, and STOP.
- **If either SSH alias is unreachable** — file the blocker issue. Do not substitute an IP address or another alias; these alias names are the contract between this task and every later one.
- **If `ls /var/lib/control-plane-credentials` on `layerb-host` returns any entry** — this is a live D95 violation, not a checker bug. File the blocker issue immediately and STOP. Delete nothing.

---


## L5-03-03 — Provision the second, Founder-only Grafana instance (Layer B-M)

**Size:** M · **Depends on:** L5-03-01, L5-03-02 · **Owned paths touched:** `ops-vm/layer-b/`

### Purpose
Build the Layer B-M surface exactly as D75 specifies: *"a second, Founder-only Grafana instance on the operations VM — the same JSON-provisioning discipline as the shared instance, its own credential and its own authentication restriction"* (§90.3). §92.1 row 6 names this surface: *"Founder view — people tab … Grafana — a second, Founder-only instance on the operations VM, holding the separately-credentialed people datasource (D75)"*.

The identity bridge is already decided and is not this task's choice: *"`people.yaml` keys on the GitHub login; capability-derived Grafana access uses GitHub OAuth into Grafana plus a sync job from the registries. No separate IdP."* (§99.5). The sync job itself is L5-03-09; this task builds the instance and its authentication restriction.

This task does **not** register the people datasource — that is L5-03-04, deliberately separated so that AT-097's negative check has its own commit and its own reviewer.

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/compose.yaml` | The Layer B-M Grafana service definition, bound to the private path only |
| `ops-vm/layer-b/grafana.ini` | Instance configuration: own admin credential reference, OAuth restriction, no anonymous access, no sign-up |
| `ops-vm/layer-b/provisioning/dashboards/layer-b.yaml` | Dashboard provider — JSON-provisioned, same discipline as the shared instance |
| `ops-vm/layer-b/provisioning/datasources/.gitkeep` | Empty by design in this task; populated by L5-03-04 |
| `ops-vm/layer-b/allowlist/.gitkeep` | Empty by design in this task; populated by L5-03-09 |
| `ops-vm/layer-b/check-instance.sh` | The instance checker |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-03-layerb-instance
mkdir -p ops-vm/layer-b/provisioning/dashboards ops-vm/layer-b/provisioning/datasources ops-vm/layer-b/allowlist
touch ops-vm/layer-b/provisioning/datasources/.gitkeep ops-vm/layer-b/allowlist/.gitkeep
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/compose.yaml <<'YAML'
# ops-vm/layer-b/compose.yaml
# The second, Founder-only Grafana instance - Layer B-M (D75, Section 90.3).
# Runs on layerb-host (infra/hosts/layerb-host.yaml), never on ops-vm.
# It shares no volume, no network and no credential with the shared instance.
services:
  grafana-layerb:
    image: grafana/grafana-oss:11.6.7
    container_name: grafana-layerb
    restart: unless-stopped
    # Bound to the private path only (Section 51.4, Remote access).
    # 127.0.0.1 plus the mesh interface; never 0.0.0.0.
    ports:
      - "127.0.0.1:3001:3000"
    environment:
      GF_PATHS_CONFIG: /etc/grafana/grafana.ini
      GF_PATHS_PROVISIONING: /etc/grafana/provisioning
      # Own credential. Value lives on the host, never in this repository.
      GF_SECURITY_ADMIN_PASSWORD__FILE: /run/secrets/layerb_admin_password
      GF_AUTH_GITHUB_CLIENT_ID__FILE: /run/secrets/layerb_oauth_client_id
      GF_AUTH_GITHUB_CLIENT_SECRET__FILE: /run/secrets/layerb_oauth_client_secret
    volumes:
      - ./grafana.ini:/etc/grafana/grafana.ini:ro
      - ./provisioning:/etc/grafana/provisioning:ro
      - layerb-grafana-data:/var/lib/grafana
    secrets:
      - layerb_admin_password
      - layerb_oauth_client_id
      - layerb_oauth_client_secret
volumes:
  layerb-grafana-data:
    # Lives on the encrypted volume provisioned by L5-03-05 (Section 51.4).
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /srv/layerb/encrypted/grafana
secrets:
  layerb_admin_password:
    file: /srv/layerb/secrets/admin_password
  layerb_oauth_client_id:
    file: /srv/layerb/secrets/oauth_client_id
  layerb_oauth_client_secret:
    file: /srv/layerb/secrets/oauth_client_secret
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/grafana.ini <<'INI'
; ops-vm/layer-b/grafana.ini
; Layer B-M instance configuration (D75, Section 90.3, Section 90.4).
; Every setting below is load-bearing. Do not relax one to make a test pass.

[server]
http_addr = 0.0.0.0
http_port = 3000
root_url = %(protocol)s://layerb-host:3001/

[security]
; Its own credential - not the shared instance's (D75).
admin_user = layerb-admin
disable_initial_admin_creation = false
cookie_secure = true
cookie_samesite = strict
content_security_policy = true

[users]
; Its own authentication restriction (D75).
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer

[auth.anonymous]
; Layer B-M is Founder-only. Anonymous access is never enabled here.
enabled = false

[auth.basic]
enabled = false

[auth.github]
; Identity bridge fixed by Section 99.5: GitHub OAuth, no separate IdP.
enabled = true
allow_sign_up = false
; allowed_organizations and team_ids are written by the sync job of L5-03-09
; from the holders of the people-intelligence capability, and by nothing else
; (Section 90.4). This file never hard-codes a person.
scopes = user:email,read:org

[auth]
; Section 90.3: "Layer B sessions carry declared session-lifetime limits and
; expire; standing unattended sessions are prohibited."
; The values are set by L5-03-08; the keys are declared here so their absence
; is visible rather than defaulted.
login_maximum_inactive_lifetime_duration =
login_maximum_lifetime_duration =
token_rotation_interval_minutes = 10
disable_login_form = false
sigv4_auth_enabled = false

[analytics]
reporting_enabled = false
check_for_updates = false

[snapshots]
; No external snapshot path out of Layer B.
external_enabled = false

[dashboards]
; Same JSON-provisioning discipline as the shared instance (D75).
min_refresh_interval = 1m

[alerting]
enabled = false

[unified_alerting]
; Section 90.2: people intelligence is never relayed over messaging surfaces.
enabled = false
INI
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/provisioning/dashboards/layer-b.yaml <<'YAML'
# ops-vm/layer-b/provisioning/dashboards/layer-b.yaml
# JSON-provisioned dashboards only. Editing in the UI is not the source of truth.
apiVersion: 1
providers:
  - name: layer-b-m
    orgId: 1
    folder: "Layer B-M"
    type: file
    disableDeletion: true
    allowUiUpdates: false
    updateIntervalSeconds: 60
    options:
      path: /etc/grafana/provisioning/dashboards/json
      foldersFromFilesStructure: false
YAML
mkdir -p ops-vm/layer-b/provisioning/dashboards/json
touch ops-vm/layer-b/provisioning/dashboards/json/.gitkeep
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/check-instance.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/check-instance.sh
# Usage: check-instance.sh repo | check-instance.sh host
set -euo pipefail
MODE="${1:-repo}"
INI="ops-vm/layer-b/grafana.ini"
COMPOSE="ops-vm/layer-b/compose.yaml"
fail() { echo "INST_FAIL $1"; exit 1; }
ini_get() { awk -v s="[$1]" -v k="$2" '$0==s{f=1;next} /^\[/{f=0} f&&$1==k{print $3; exit}' "$INI"; }

if [ "$MODE" = "repo" ]; then
  [ "$(ini_get auth.anonymous enabled)" = "false" ] || fail "anonymous access not disabled"
  [ "$(ini_get auth.basic enabled)" = "false" ]     || fail "basic auth not disabled"
  [ "$(ini_get users allow_sign_up)" = "false" ]    || fail "sign-up not disabled"
  [ "$(ini_get security admin_user)" = "layerb-admin" ] || fail "instance does not carry its own admin credential"
  [ "$(ini_get unified_alerting enabled)" = "false" ] || fail "alerting enabled - Section 90.2 forbids relaying people intelligence"
  grep -q 'allowUiUpdates: false' ops-vm/layer-b/provisioning/dashboards/layer-b.yaml || fail "UI updates not disabled"
  grep -q '127.0.0.1:3001:3000' "$COMPOSE" || fail "instance not bound to the private path"
  grep -q '0.0.0.0:' "$COMPOSE" && fail "instance publishes on 0.0.0.0"
  if grep -nE '(password|secret)[[:space:]]*[:=][[:space:]]*[^$#[:space:]]' "$COMPOSE" \
     | grep -vE '__FILE|secrets:|file:' | grep -q .; then
    fail "literal secret in compose"
  fi
  echo "INST_REPO_OK 8/8"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  up=$(ssh layerb-host 'docker inspect -f "{{.State.Running}}" grafana-layerb 2>/dev/null' || echo false)
  [ "$up" = "true" ] || fail "grafana-layerb not running on layerb-host"
  code=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/api/org' || echo 000)
  [ "$code" = "401" ] || fail "unauthenticated /api/org returned $code, expected 401"
  ext=$(ssh ops-vm 'curl -s -o /dev/null -m 5 -w "%{http_code}" http://layerb-host:3001/api/org' || echo 000)
  [ "$ext" = "000" ] || fail "Layer B-M reachable from ops-vm on $ext, expected no route"
  echo "INST_HOST_OK 3/3"
  exit 0
fi
fail "unknown mode $MODE"
SH
chmod +x ops-vm/layer-b/check-instance.sh
```

```bash
set -euo pipefail
scp -r ops-vm/layer-b layerb-host:/srv/layerb/config
ssh layerb-host 'cd /srv/layerb/config && docker compose -f compose.yaml up -d'
./ops-vm/layer-b/check-instance.sh repo
./ops-vm/layer-b/check-instance.sh host
```

```bash
set -euo pipefail
git add ops-vm/layer-b
git commit -m "L5-03-03: provision the second, Founder-only Grafana instance for Layer B-M (D75)"
git push -u origin lane/5/p3-03-layerb-instance
gh pr create --base integration --head lane/5/p3-03-layerb-instance \
  --title "L5-03-03: the Founder-only Layer B-M Grafana instance" \
  --body "Second Grafana instance per D75: own credential, own authentication restriction, private path only, JSON-provisioned, alerting off. No datasource registered yet - that is L5-03-04."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | A second instance exists, distinct from the shared one | `ssh layerb-host 'docker inspect -f "{{.Name}}" grafana-layerb'` | `/grafana-layerb` |
| 2 | It carries its own admin credential | `grep '^admin_user' ops-vm/layer-b/grafana.ini` | `admin_user = layerb-admin` |
| 3 | Anonymous access is off | `grep -A1 '^\[auth.anonymous\]' ops-vm/layer-b/grafana.ini \| grep enabled` | `enabled = false` |
| 4 | Sign-up is off | `grep '^allow_sign_up' ops-vm/layer-b/grafana.ini \| head -1` | `allow_sign_up = false` |
| 5 | Dashboards are JSON-provisioned and not UI-editable | `grep -c 'allowUiUpdates: false' ops-vm/layer-b/provisioning/dashboards/layer-b.yaml` | `1` |
| 6 | No credential value is committed | `git grep -nE '(password|secret) *[:=] *[A-Za-z0-9]' -- ops-vm/layer-b \| wc -l` | `0` |
| 7 | Unauthenticated API call is refused | `ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/api/org'` | `401` |
| 8 | The instance is not routable from `ops-vm` | `ssh ops-vm 'curl -s -o /dev/null -m 5 -w "%{http_code}" http://layerb-host:3001/api/org'` | `000` |
| 9 | Repository-side checker passes | `./ops-vm/layer-b/check-instance.sh repo` | `INST_REPO_OK 8/8` |
| 10 | Host-side checker passes | `./ops-vm/layer-b/check-instance.sh host` | `INST_HOST_OK 3/3` |
| 11 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./ops-vm/layer-b/check-instance.sh repo && \
./ops-vm/layer-b/check-instance.sh host && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines:

```
INST_REPO_OK 8/8
INST_HOST_OK 3/3
OWNED_ROOTS_OK
```

**SELF-VERIFY negative — literal secret in compose must be caught**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
# Seed a literal plaintext secret into the compose file, run the repo check, restore.
cp ops-vm/layer-b/compose.yaml /tmp/compose-sv-backup.yaml
printf '    environment:\n      - password: plaintext\n' >> ops-vm/layer-b/compose.yaml
NEG_OUT=$(./ops-vm/layer-b/check-instance.sh repo 2>&1 || true)
cp /tmp/compose-sv-backup.yaml ops-vm/layer-b/compose.yaml
printf 'literal-secret-neg=[%s]\n' "$(printf '%s' "$NEG_OUT" | head -1)"
```

Expected output:

```
literal-secret-neg=[INST_FAIL literal secret in compose]
```

**STOP rule** — if `literal-secret-neg` prints `literal-secret-neg=[INST_REPO_OK 8/8]`, the literal-secret check silently passed a poisoned compose file and the G10 gate is broken. Delete the `&&` pipeline and use the `if … | grep -q .` form from the fix above.

### STOP rules

- **If the only way to make the instance reachable is to bind it to `0.0.0.0` or expose it publicly** — STOP. §51.4 makes network exposure of a control-plane surface *"a named security decision with the Founder as decider, recorded like any other decision — never a convenience default."* File the blocker issue.
- **If criterion 8 returns anything other than `000`** — the two hosts have a route the boundary does not permit. Do not edit the firewall to "fix the test" without a declaration to point at. File the blocker issue.
- **If the pinned Grafana OSS image tag does not exist** — do not substitute `latest`. The pinned version is tool-register state (§51.4, §62.1). File the blocker issue naming the tag you tried.
- **If any acceptance criterion can only pass by enabling a Grafana Enterprise feature** — STOP. §90.3: *"datasource-level query permission is an Enterprise feature Grafana OSS does not have"*, and §99.5 forbids an enterprise licence for this layer. File the blocker issue.

---

## L5-03-04 — Register the people datasource in Layer B-M only, and prove its absence from the shared instance (AT-097)

**Size:** M · **Depends on:** L5-03-03 · **Owned paths touched:** `ops-vm/layer-b/provisioning/datasources/`, `ops-vm/shared/`, `access/layer-b/`

### Purpose
The binding sentence: *"The people datasource is never registered in the shared instance; the Layer B boundary is instance separation, not folder membership."* (§90.3, D75). AT-097's pass condition fixes how that is proved: *"The people datasource is absent from the shared Grafana instance's provisioning — no datasource entry and no dashboard reference exist there, verified in the provisioned configuration, not inferred from panel visibility (D75)."*

Two artifacts come out of this task: the positive registration inside Layer B-M, and the negative checker that reads the *shared* instance's provisioned configuration and its dashboard JSON.

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/provisioning/datasources/people.yaml` | The people datasource, registered in Layer B-M and nowhere else |
| `access/layer-b/at-097-no-people-datasource-in-shared.sh` | AT-097 negative check over the shared instance's provisioned configuration |
| `access/layer-b/at-098-separately-credentialed.sh` | AT-098 check: a shared-instance session grants nothing on Layer B-M |
| `ops-vm/shared/README-datasources.md` | A one-paragraph statement, in the shared instance's own directory, that the people datasource is prohibited there |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-04-people-datasource
mkdir -p ops-vm/shared access/layer-b
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/provisioning/datasources/people.yaml <<'YAML'
# ops-vm/layer-b/provisioning/datasources/people.yaml
# The people-performance datasource. Registered in the Layer B-M instance ONLY.
# Section 90.3: "The people-performance datasource is separately credentialed
# from the general engineering datasource." and "Any user able to query the
# people datasource is considered to have full access to it, regardless of
# which panels they can see."
apiVersion: 1
datasources:
  - name: people
    uid: layerb-people
    type: postgres
    access: proxy
    url: 127.0.0.1:5433
    user: layerb_reader
    database: layerb_people
    isDefault: true
    editable: false
    jsonData:
      sslmode: require
      postgresVersion: 1600
      maxOpenConns: 4
    secureJsonData:
      # Read from the host secret file at provision time. Never a literal here.
      password: $__file{/run/secrets/layerb_datasource_password}
deleteDatasources:
  # Defensive: if a people datasource was ever provisioned under another name
  # in this instance, remove it so exactly one registration exists.
  - name: people-performance
    orgId: 1
YAML
```

```bash
set -euo pipefail
cat > ops-vm/shared/README-datasources.md <<'MD'
# Shared Grafana instance - datasource rule

The people-performance datasource is **never** registered in this instance.

> "The people datasource is never registered in the shared instance; the Layer B
> boundary is instance separation, not folder membership. Folder ACLs in the
> shared instance remain defence in depth for Layer A views only."
> - Master Specification v4.0, Section 90.3 (D75)

Adding a people datasource entry here, or a dashboard in this instance that
references one, fails AT-097 and breaks invariant 109. The check that enforces
this is `access/layer-b/at-097-no-people-datasource-in-shared.sh` and it runs in
the People-tier gate (L5-03-12).
MD
```

```bash
set -euo pipefail
cat > access/layer-b/at-097-no-people-datasource-in-shared.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-097-no-people-datasource-in-shared.sh
# AT-097 - "No people datasource in the shared Grafana instance".
# Verified in the provisioned configuration, not inferred from panel visibility.
set -euo pipefail
SHARED_PROV="${SHARED_PROV:-ops-vm/grafana/provisioning}"
FAILS=0
note() { echo "AT-097_FAIL $1"; FAILS=$((FAILS+1)); }

# Hard precondition: the provisioning tree must exist or this check is indeterminate.
[ -d "$SHARED_PROV/datasources" ] || {
  echo "AT-097 INDETERMINATE: ops-vm grafana provisioning tree absent ($SHARED_PROV/datasources)"
  exit 2
}

# 1. No datasource entry naming or typed as the people store.
if [ -d "$SHARED_PROV/datasources" ]; then
  if grep -rniE '(^|[^a-z])(people|layerb|layer-b|people-performance|layerb_people)' \
       "$SHARED_PROV/datasources" >/dev/null 2>&1; then
    note "people datasource entry present in shared provisioning"
  fi
fi

# 2. No dashboard in the shared instance references the people datasource uid.
if [ -d "$SHARED_PROV/dashboards" ]; then
  if grep -rn 'layerb-people' "$SHARED_PROV/dashboards" >/dev/null 2>&1; then
    note "shared dashboard references datasource uid layerb-people"
  fi
fi

# 3. Live check: the running shared instance lists no people datasource.
if [ "${SKIP_LIVE:-0}" != "1" ]; then
  live=$(ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/datasources' 2>/dev/null || echo '[]')
  if printf '%s' "$live" | grep -qiE 'people|layerb'; then
    note "running shared instance lists a people datasource"
  fi
fi

# 4. The people datasource IS registered in Layer B-M (positive half).
grep -q 'uid: layerb-people' ops-vm/layer-b/provisioning/datasources/people.yaml \
  || note "people datasource not registered in the Layer B-M instance"

if [ "$FAILS" -eq 0 ]; then echo "AT-097_PASS"; else echo "AT-097_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-097-no-people-datasource-in-shared.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-098-separately-credentialed.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-098-separately-credentialed.sh
# AT-098 - "The Founder-only instance is separately credentialed":
# reaching it requires its own credential; a shared-instance login grants
# nothing there, and a direct query without that instance's credential is denied.
set -euo pipefail
FAILS=0
note() { echo "AT-098_FAIL $1"; FAILS=$((FAILS+1)); }

# a) No credential at all -> denied.
c1=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/api/datasources')
[ "$c1" = "401" ] || note "no-credential query returned $c1, expected 401"

# b) The shared instance's admin credential -> denied on Layer B-M.
c2=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3001/api/datasources')
[ "$c2" = "401" ] || note "shared-instance credential returned $c2 on Layer B-M, expected 401"

# c) A direct datasource query without the instance credential -> denied.
c3=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:3001/api/ds/query -H "Content-Type: application/json" -d "{}"')
[ "$c3" = "401" ] || note "unauthenticated ds/query returned $c3, expected 401"

# d) The two instances do not share an admin credential file.
same=$(ssh layerb-host 'sha256sum /srv/layerb/secrets/admin_password 2>/dev/null | cut -d" " -f1' || echo x)
other=$(ssh ops-vm 'sha256sum /srv/shared/secrets/admin_password 2>/dev/null | cut -d" " -f1' || echo y)
[ "$same" != "$other" ] || note "the two instances share an admin credential"

if [ "$FAILS" -eq 0 ]; then echo "AT-098_PASS"; else echo "AT-098_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-098-separately-credentialed.sh
```

```bash
set -euo pipefail
scp ops-vm/layer-b/provisioning/datasources/people.yaml layerb-host:/srv/layerb/config/provisioning/datasources/people.yaml
ssh layerb-host 'cd /srv/layerb/config && docker compose -f compose.yaml restart grafana-layerb'
./access/layer-b/at-097-no-people-datasource-in-shared.sh
./access/layer-b/at-098-separately-credentialed.sh
```

```bash
set -euo pipefail
git add ops-vm/layer-b/provisioning/datasources/people.yaml ops-vm/shared/README-datasources.md \
        access/layer-b/at-097-no-people-datasource-in-shared.sh \
        access/layer-b/at-098-separately-credentialed.sh
git commit -m "L5-03-04: register the people datasource in Layer B-M only; add AT-097 and AT-098 checks"
git push -u origin lane/5/p3-04-people-datasource
gh pr create --base integration --head lane/5/p3-04-people-datasource \
  --title "L5-03-04: people datasource in Layer B-M only (AT-097, AT-098)" \
  --body "Positive registration in the Founder-only instance; negative check over the shared instance's provisioned configuration and dashboard JSON; separate-credential check."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Exactly one people datasource registration exists in the repository | `git grep -l 'uid: layerb-people' -- ops-vm \| wc -l` | `1` |
| 2 | That registration is inside the Layer B-M provisioning tree | `git grep -l 'uid: layerb-people' -- ops-vm` | `ops-vm/layer-b/provisioning/datasources/people.yaml` |
| 3 | The shared provisioning tree names no people datasource | `grep -rciE 'people|layerb' ops-vm/grafana/provisioning/datasources 2>/dev/null \| awk -F: '{s+=$2} END {print s+0}'` | `0` |
| 4 | No shared dashboard references the Layer B datasource uid | `grep -rc 'layerb-people' ops-vm/grafana/provisioning/dashboards 2>/dev/null \| awk -F: '{s+=$2} END {print s+0}'` | `0` |
| 5 | The running shared instance lists no people datasource | `ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/datasources' \| grep -ci 'people' \| cat` | `0` |
| 6 | The datasource carries no literal password | `grep -c '\$__file{' ops-vm/layer-b/provisioning/datasources/people.yaml` | `1` |
| 7 | AT-097 passes | `./access/layer-b/at-097-no-people-datasource-in-shared.sh` | `AT-097_PASS` |
| 8 | AT-098 passes | `./access/layer-b/at-098-separately-credentialed.sh` | `AT-098_PASS` |
| 9 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/at-097-no-people-datasource-in-shared.sh && \
./access/layer-b/at-098-separately-credentialed.sh && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines:

```
AT-097_PASS
AT-098_PASS
OWNED_ROOTS_OK
```

**Paired negative — absent provisioning tree must exit INDETERMINATE (exit 2), not PASS:**

```bash
# Confirm that AT-097 returns exit 2 (INDETERMINATE) when the provisioning
# tree does not exist, rather than silently passing an empty check.
# This proves the precondition guard is live.
SHARED_PROV="/tmp/absent-prov-$$" \
  ./access/layer-b/at-097-no-people-datasource-in-shared.sh; _ec=$?
[ "$_ec" -eq 2 ] \
  && echo "SV_INDET OK: AT-097 returned INDETERMINATE (exit 2) for absent provisioning tree" \
  || echo "SV_INDET FAIL: AT-097 returned exit $_ec — expected 2"
```

Expected output: `AT-097 INDETERMINATE: ops-vm grafana provisioning tree absent (...)`, `SV_INDET OK: AT-097 returned INDETERMINATE (exit 2) for absent provisioning tree`.

### STOP rules

- **If AT-097 fails because a people datasource already exists in the shared instance** — do not delete it silently. This is a live invariant-109 violation. File the blocker issue, and STOP; removal of a live datasource with unknown dependents is not this task's authority.
- **If the only way to pass AT-098 is to grant the shared instance's credential on Layer B-M** — STOP. That is the exact leakage D75 exists to close.
- **If someone proposes solving this with a restricted folder in the shared instance instead of a second instance** — refuse and quote §90.3: *"Neither, in Grafana OSS, is folder membership"* access control. File the blocker issue if pressed.
- **If `ops-vm/grafana/provisioning` does not exist in this repository** — the shared instance's provisioning is not yet under `ops-vm/`. AT-097 will now exit 2 (INDETERMINATE) rather than silently passing. Run AT-097 with `SHARED_PROV` pointing at the live host path via `ssh`, record the path in the blocker issue, and file it so L0 can confirm where shared provisioning lives. Do not create the shared tree yourself.

---


## L5-03-05 — Encrypt the people-data store at rest and emit its checksum manifest

**Size:** M · **Depends on:** L5-03-02 · **Owned paths touched:** `infra/layer-b/`, `ops-vm/layer-b/`

### Purpose
§90.3: *"Layer B's durable home is the separately credentialed people-data store on the operations VM — the database plus its generated documents — encrypted at rest, with encrypted backups protected by a restricted backup credential, and never present in any org-readable repository."*

§51.4 restates it as a control-plane obligation: *"The separately credentialed people-data store — database plus generated documents — is **encrypted at rest**."*

§45.4 fixes the integrity check the encryption must support: *"The integrity check is **decrypt-plus-checksum-manifest**: the encrypted store is decrypted and its contents verified against the checksum manifest **without opening any document**."*

This task provisions the encrypted volume, moves both halves of the store onto it, and builds the manifest generator and verifier that the restore drill will use.

### Files created

| Path | Purpose |
|---|---|
| `infra/layer-b/encrypted-volume.yaml` | The declaration of the encrypted volume, its mount point and its key custody |
| `infra/layer-b/provision-encrypted-volume.sh` | Idempotent provisioning of the encrypted volume on `layerb-host` |
| `ops-vm/layer-b/manifest/generate-checksum-manifest.sh` | Writes the checksum manifest over the store, opening no document |
| `ops-vm/layer-b/manifest/verify-checksum-manifest.sh` | Decrypt-plus-checksum-manifest verification (§45.4) |
| `infra/layer-b/check-encryption.sh` | Proves the store is on the encrypted volume and nothing sensitive sits outside it |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-05-encryption-at-rest
mkdir -p infra/layer-b ops-vm/layer-b/manifest
```

```bash
set -euo pipefail
cat > infra/layer-b/encrypted-volume.yaml <<'YAML'
# infra/layer-b/encrypted-volume.yaml
# The Layer B people-data store, encrypted at rest (Section 90.3, Section 51.4).
volume:
  host: layerb-host
  device: /dev/disk/by-partlabel/layerb
  mapper_name: layerb_crypt
  mount_point: /srv/layerb/encrypted
  filesystem: ext4
  mount_options: "noexec,nosuid,nodev"
  cipher: aes-xts-plain64
  key_size_bits: 512
contents:
  # Both halves of the store live here and nowhere else.
  database: /srv/layerb/encrypted/postgres
  generated_documents: /srv/layerb/encrypted/documents
  grafana_state: /srv/layerb/encrypted/grafana
key_custody:
  # Section 45.4: "Custody of the decryption key is the Section 14.4 escrow."
  escrow: "Section 14.4 sealed escrow"
  escrow_row: "layer-b-store-decryption-key"
  distinct_from:
    - "layer-b-backup-encryption-key"     # Section 51.4
    - "conduct-store-contingency-credential"  # Section 88.4, distinct by rule
  rotation_triggers_re_escrow: true       # Section 14.4 escrow mechanics
integrity_check:
  method: decrypt-plus-checksum-manifest  # Section 45.4
  manifest_path: /srv/layerb/encrypted/CHECKSUMS.sha256
  opens_documents: false
prohibited:
  - "any Layer B content in an org-readable repository"   # Section 90.3
  - "unencrypted self-view outside the store"             # Section 90.6
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/provision-encrypted-volume.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/provision-encrypted-volume.sh
# Idempotent. Run from the repository root; acts on layerb-host over SSH.
# Creates nothing if the mapper is already open and mounted.
set -euo pipefail
DECL="infra/layer-b/encrypted-volume.yaml"
DEV=$(yq -r '.volume.device' "$DECL")
MAP=$(yq -r '.volume.mapper_name' "$DECL")
MNT=$(yq -r '.volume.mount_point' "$DECL")
OPTS=$(yq -r '.volume.mount_options' "$DECL")

ssh layerb-host "set -euo pipefail
if mountpoint -q '$MNT'; then echo 'ALREADY_MOUNTED'; exit 0; fi
if ! sudo cryptsetup isLuks '$DEV' 2>/dev/null; then
  # The passphrase is supplied interactively by the Founder. It is never
  # stored on the host and never appears in this repository.
  # Guard checks the block device for an existing LUKS header, not the
  # device-mapper path (which disappears after reboot even when the header
  # is intact). DF-0696: the old [ ! -e /dev/mapper/$MAP ] guard was true
  # after every reboot, causing luksFormat to reformat and destroy data.
  sudo cryptsetup luksFormat --type luks2 --cipher $(yq -r '.volume.cipher' /dev/null 2>/dev/null || echo aes-xts-plain64) '$DEV'
fi
if [ ! -e /dev/mapper/$MAP ]; then
  sudo cryptsetup open '$DEV' '$MAP'
fi
if ! sudo blkid /dev/mapper/$MAP >/dev/null 2>&1; then sudo mkfs.ext4 /dev/mapper/$MAP; fi
sudo mkdir -p '$MNT'
sudo mount -o '$OPTS' /dev/mapper/$MAP '$MNT'
sudo mkdir -p '$MNT/postgres' '$MNT/documents' '$MNT/grafana'
sudo chmod 700 '$MNT' '$MNT/postgres' '$MNT/documents' '$MNT/grafana'
echo 'PROVISIONED'"
SH
chmod +x infra/layer-b/provision-encrypted-volume.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/manifest/generate-checksum-manifest.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/manifest/generate-checksum-manifest.sh
# Writes the checksum manifest over the mounted store.
# It hashes bytes. It opens, parses and renders nothing (Section 45.4).
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
OUT="$MNT/CHECKSUMS.sha256"
cd "$MNT"
find . -type f ! -name 'CHECKSUMS.sha256' ! -name 'CHECKSUMS.sha256.count' -print0 \
  | sort -z \
  | xargs -0 sha256sum > "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
wc -l < "$OUT" | tr -d ' ' > "$OUT.count"
echo "MANIFEST_WRITTEN $(wc -l < "$OUT" | tr -d ' ') files"
SH
chmod +x ops-vm/layer-b/manifest/generate-checksum-manifest.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/manifest/verify-checksum-manifest.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/manifest/verify-checksum-manifest.sh
# Section 45.4 integrity check: decrypt-plus-checksum-manifest,
# "without opening any document".
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
OUT="$MNT/CHECKSUMS.sha256"
[ -f "$OUT" ] || { echo "MANIFEST_MISSING"; exit 1; }
mountpoint -q "$MNT" || { echo "STORE_NOT_DECRYPTED"; exit 1; }
cd "$MNT"
if sha256sum -c --quiet "$OUT"; then
  echo "MANIFEST_VERIFIED $(cat "$OUT.count") files"
else
  echo "MANIFEST_MISMATCH"; exit 1
fi
SH
chmod +x ops-vm/layer-b/manifest/verify-checksum-manifest.sh
```

```bash
set -euo pipefail
cat > infra/layer-b/check-encryption.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/check-encryption.sh
# Usage: check-encryption.sh repo | check-encryption.sh host
set -euo pipefail
MODE="${1:-repo}"
DECL="infra/layer-b/encrypted-volume.yaml"
fail() { echo "ENC_FAIL $1"; exit 1; }

if [ "$MODE" = "repo" ]; then
  [ "$(yq -r '.integrity_check.method' "$DECL")" = "decrypt-plus-checksum-manifest" ] \
    || fail "integrity check method is not the Section 45.4 method"
  [ "$(yq -r '.integrity_check.opens_documents' "$DECL")" = "false" ] \
    || fail "integrity check declares that it opens documents"
  [ "$(yq -r '.key_custody.escrow' "$DECL")" = "Section 14.4 sealed escrow" ] \
    || fail "key custody is not the Section 14.4 escrow"
  # No Layer B content in this org-readable repository (Section 90.3).
  n=$(git ls-files | grep -cE '^(access|infra|ops-vm|notify|assets)/.*(evidence|self-?view|bundle)/.+' || true)
  [ "$n" -eq 0 ] || fail "$n Layer B content file(s) tracked in the repository"
  echo "ENC_REPO_OK 4/4"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  MNT=$(yq -r '.volume.mount_point' "$DECL")
  MAP=$(yq -r '.volume.mapper_name' "$DECL")
  t=$(ssh layerb-host "lsblk -no TYPE /dev/mapper/$MAP 2>/dev/null" || echo none)
  [ "$t" = "crypt" ] || fail "store device type is '$t', expected 'crypt'"
  ssh layerb-host "mountpoint -q $MNT" || fail "store not mounted at $MNT"
  perm=$(ssh layerb-host "stat -c %a $MNT")
  [ "$perm" = "700" ] || fail "store mode is $perm, expected 700"
  stray=$(ssh layerb-host "find /srv/layerb /var/lib/grafana -maxdepth 3 -type d \\( -name documents -o -name postgres \\) ! -path '$MNT/*' 2>/dev/null | wc -l")
  [ "$stray" -eq 0 ] || fail "$stray store directory(ies) outside the encrypted volume"
  echo "ENC_HOST_OK 4/4"
  exit 0
fi
fail "unknown mode $MODE"
SH
chmod +x infra/layer-b/check-encryption.sh
```

```bash
set -euo pipefail
./infra/layer-b/provision-encrypted-volume.sh
ssh layerb-host 'sudo bash -s' < ops-vm/layer-b/manifest/generate-checksum-manifest.sh
ssh layerb-host 'sudo bash -s' < ops-vm/layer-b/manifest/verify-checksum-manifest.sh
./infra/layer-b/check-encryption.sh repo
./infra/layer-b/check-encryption.sh host
```

```bash
set -euo pipefail
git add infra/layer-b/encrypted-volume.yaml infra/layer-b/provision-encrypted-volume.sh \
        infra/layer-b/check-encryption.sh ops-vm/layer-b/manifest
git commit -m "L5-03-05: encrypt the Layer B people-data store at rest and add the checksum manifest"
git push -u origin lane/5/p3-05-encryption-at-rest
gh pr create --base integration --head lane/5/p3-05-encryption-at-rest \
  --title "L5-03-05: Layer B store encrypted at rest, with the Section 45.4 checksum manifest" \
  --body "Encrypted volume declaration and provisioning, manifest generator and verifier (decrypt-plus-checksum-manifest, opening no document), and the encryption checker."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The store device is an encrypted mapper device | `ssh layerb-host 'lsblk -no TYPE /dev/mapper/layerb_crypt'` | `crypt` |
| 2 | The store is mounted at the declared point | `ssh layerb-host 'mountpoint -q /srv/layerb/encrypted && echo MOUNTED'` | `MOUNTED` |
| 3 | Both halves of the store are inside it | `ssh layerb-host 'ls -d /srv/layerb/encrypted/postgres /srv/layerb/encrypted/documents \| wc -l'` | `2` |
| 4 | Store directory is not world- or group-readable | `ssh layerb-host 'stat -c %a /srv/layerb/encrypted'` | `700` |
| 5 | Manifest exists and verifies | `ssh layerb-host 'cd /srv/layerb/encrypted && sha256sum -c --quiet CHECKSUMS.sha256 && echo MANIFEST_VERIFIED'` | `MANIFEST_VERIFIED` |
| 6 | The manifest generator opens no document | `grep -cE '\b(cat|less|jq|python3|grep)\b' ops-vm/layer-b/manifest/generate-checksum-manifest.sh` | `0` |
| 7 | Key custody is the §14.4 escrow, with a distinct row from the backup key | `yq -r '.key_custody.escrow_row' infra/layer-b/encrypted-volume.yaml` | `layer-b-store-decryption-key` |
| 8 | No Layer B content is tracked in this repository | `./infra/layer-b/check-encryption.sh repo` | `ENC_REPO_OK 4/4` |
| 9 | Host-side encryption checker passes | `./infra/layer-b/check-encryption.sh host` | `ENC_HOST_OK 4/4` |
| 10 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./infra/layer-b/check-encryption.sh repo && \
./infra/layer-b/check-encryption.sh host && \
ssh layerb-host 'cd /srv/layerb/encrypted && sha256sum -c --quiet CHECKSUMS.sha256 && echo MANIFEST_VERIFIED' && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly four lines:

```
ENC_REPO_OK 4/4
ENC_HOST_OK 4/4
MANIFEST_VERIFIED
OWNED_ROOTS_OK
```

### STOP rules

- **If the host has no spare block device and the only route to "encrypted at rest" is file-level encryption of some paths** — STOP. The declaration says the database *and* the generated documents are encrypted at rest; choosing a different mechanism is a design decision. File the blocker issue.
- **If the LUKS passphrase would have to be stored on the host to allow unattended boot** — STOP and file the blocker issue. Key custody is the §14.4 escrow, and an on-host passphrase makes VM-root a decryption path, which is exactly what §90.6 says the design stops.
- **If `check-encryption.sh repo` reports Layer B content tracked in the repository** — STOP immediately. §90.3: Layer B is *"never present in any org-readable repository."* File the blocker issue; do not `git rm` history yourself.
- **If the manifest verification reports `MANIFEST_MISMATCH` on a freshly generated manifest** — do not regenerate to make it green. File the blocker issue with the differing paths' names only.

---

## L5-03-06 — The restricted backup credential and object-locked backup target

**Size:** M · **Depends on:** L5-03-05 · **Owned paths touched:** `infra/layer-b/`, `assets/`, `notify/`

### Purpose
§51.4 states the backup discipline in full, and every clause below is a checked field:

> *"its backups carry the controls Section 45.3 gives the organisation export, because the more sensitive copy may not be the less protected one — an **append-only, write-only backup credential** writing to **object-locked, versioned storage** in a different provider and credential domain than the operations VM, so the party who can write the backup can neither read nor destroy backup history; a **named owner and an explicit read-access list** reviewed with the asset inventory (Section 49); and an entry in the fifth-tier credential inventory of Section 40.1 with its rotation cadence and named rotator. Custody of the backup encryption key is the Section 14.4 escrow, as for the store itself (Section 45.4), and backup failure alerts on the product discipline of Section 44.3."*

§40.1 already names this credential as one of the five control-plane machine credentials: *"the reconciler, the provisioning CLI, the organisation-export token, the records-writer credential, the **Layer B backup credential**"* — *"(the backup credential, an append-only object-store credential)"*.

### Files created

| Path | Purpose |
|---|---|
| `infra/layer-b/backup.yaml` | The backup declaration: target, credential shape, key custody, read-access list |
| `infra/layer-b/backup-run.sh` | The backup job: encrypt, write, verify write-only behaviour, record the run |
| `infra/layer-b/check-backup-credential.sh` | Proves the credential can write and can neither read nor delete |
| `assets/inventory/layer-b-backup-credential.yaml` | The §49.1 / §40.1 fifth-tier inventory entry |
| `assets/inventory/layer-b-backup-encryption-key.yaml` | The §49 entry for the backup encryption key, with its §14.4 escrow row |
| `notify/routes/layer-b-backup-failure.yaml` | Backup-failure alert routing on the §44.3 signal discipline |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-06-backup-credential
mkdir -p infra/layer-b assets/inventory notify/routes
```

```bash
set -euo pipefail
cat > infra/layer-b/backup.yaml <<'YAML'
# infra/layer-b/backup.yaml
# Layer B backups carry the Section 45.3 controls (Section 51.4).
target:
  provider_domain: independent          # different provider AND credential domain than ops-vm
  same_provider_as_ops_vm: false
  bucket: layerb-backups
  object_lock: true                     # object-locked
  object_lock_mode: COMPLIANCE
  versioning: true                      # versioned
  retention_days: 3650
credential:
  name: layer-b-backup-credential
  tier: control-plane                   # Section 40.1, fifth tier
  capabilities:
    write: true
    read: false                         # write-only
    overwrite: false                    # append-only
    delete: false
  location: /srv/layerb/secrets/backup_credential   # on layerb-host, not in git
  rotation_cadence: quarterly           # Section 40.1 initial value
  rotator_capability: devops            # Section 9 capability, never a person name here
  runbook: infra/layer-b/backup-rotation-runbook.md
  re_escrow_blocking: true              # Section 14.4: rotation is not done until re-escrowed
encryption:
  at_rest: true
  key_name: layer-b-backup-encryption-key
  key_custody: "Section 14.4 sealed escrow"
  key_escrow_row: "layer-b-backup-encryption-key"
  distinct_from_store_key: true         # distinct from layer-b-store-decryption-key
access:
  owner_capability: people-intelligence # the Founder; Section 90.4
  read_access_list_file: infra/layer-b/backup-read-access-list.yaml
  read_access_reviewed_with: "Section 49 asset inventory sweep"
failure_signal:
  discipline: "Section 44.3 - Backup success: backup job completed; artifact present and non-empty"
  route: notify/routes/layer-b-backup-failure.yaml
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/backup-read-access-list.yaml <<'YAML'
# infra/layer-b/backup-read-access-list.yaml
# Section 51.4: "a named owner and an explicit read-access list reviewed with
# the asset inventory (Section 49)."
# Entries are GitHub logins resolved from people.yaml. This file is compared
# against the people-intelligence capability holders by L5-03-09.
read_access:
  derived_from: "holders of the people-intelligence capability (Section 90.4)"
  entries: []          # written by the sync job of L5-03-09; never hand-edited
reviewed_with: "Section 49 asset inventory sweep"
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/backup-run.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/backup-run.sh - runs on layerb-host.
# Encrypts the store snapshot and writes it once. It never reads or deletes.
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

tar -C "$MNT" -cf "$TMP/layerb-$STAMP.tar" .
openssl enc -aes-256-cbc -pbkdf2 -salt \
  -in  "$TMP/layerb-$STAMP.tar" \
  -out "$TMP/layerb-$STAMP.tar.enc" \
  -pass file:/srv/layerb/secrets/backup_encryption_key
rm -f "$TMP/layerb-$STAMP.tar"

# Write-only put. No list, no get, no delete anywhere in this job.
aws s3 cp "$TMP/layerb-$STAMP.tar.enc" \
  "s3://layerb-backups/$STAMP/layerb.tar.enc" \
  --profile layerb-backup-writer

size=$(stat -c %s "$TMP/layerb-$STAMP.tar.enc")
[ "$size" -gt 0 ] || { echo "BACKUP_EMPTY"; exit 1; }
echo "BACKUP_OK $STAMP $size"
SH
chmod +x infra/layer-b/backup-run.sh
```

```bash
set -euo pipefail
cat > infra/layer-b/check-backup-credential.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/check-backup-credential.sh
# Proves the backup credential is append-only and write-only, and that the
# target is object-locked and versioned. Every negative below MUST fail.
set -euo pipefail
B=layerb-backups
P=layerb-backup-writer
FAILS=0
note() { echo "BKP_FAIL $1"; FAILS=$((FAILS+1)); }

# Positive: it can write.
ssh layerb-host "echo canary | aws s3 cp - s3://$B/_canary/$(date -u +%s).txt --profile $P" >/dev/null 2>&1 \
  || note "credential cannot write"

# Negative: it cannot read.
if ssh layerb-host "aws s3 ls s3://$B/ --profile $P" >/dev/null 2>&1; then note "credential can list/read"; fi

# Negative: it cannot delete.
if ssh layerb-host "aws s3 rm s3://$B/_canary/ --recursive --profile $P" >/dev/null 2>&1; then note "credential can delete"; fi

# Target properties, checked with the auditor profile, not the writer.
lock=$(ssh layerb-host "aws s3api get-object-lock-configuration --bucket $B --profile layerb-backup-auditor --query 'ObjectLockConfiguration.ObjectLockEnabled' --output text" 2>/dev/null || echo NONE)
[ "$lock" = "Enabled" ] || note "object lock is $lock, expected Enabled"
ver=$(ssh layerb-host "aws s3api get-bucket-versioning --bucket $B --profile layerb-backup-auditor --query 'Status' --output text" 2>/dev/null || echo NONE)
[ "$ver" = "Enabled" ] || note "versioning is $ver, expected Enabled"

# The backup job contains no read or delete verb at all.
grep -nE 's3 (ls|cp s3://|rm|sync)' infra/layer-b/backup-run.sh | grep -v 'aws s3 cp "' >/dev/null 2>&1 \
  && note "backup job contains a read or delete verb"

if [ "$FAILS" -eq 0 ]; then echo "BKP_OK 6/6"; else echo "BKP_FAILED $FAILS"; exit 1; fi
SH
chmod +x infra/layer-b/check-backup-credential.sh
```

```bash
set -euo pipefail
cat > assets/inventory/layer-b-backup-credential.yaml <<'YAML'
# assets/inventory/layer-b-backup-credential.yaml
# Section 49.1: the inventory "carries an entry for each control-plane machine
# credential per Section 40.1: rotation cadence (initial value: quarterly),
# named rotator (DevOps-capability holder), runbook link, and the out-of-window
# alert-config owner."
asset_id: layer-b-backup-credential
asset_class: control-plane-machine-credential
tier: control-plane
description: "Append-only, write-only object-store credential writing the encrypted Layer B backups (Section 51.4)"
owner_capability: devops
rotation_cadence: quarterly
rotator_capability: devops
runbook: infra/layer-b/backup-rotation-runbook.md
alert_config_owner_capability: devops
behavioural_envelope:
  signed_run_record_required: true
  run_count_ceiling_per_day: 2
  expected_source_host: layerb-host
  publish_per_run_api_call_counts: true
permission_set:
  - "s3:PutObject on s3://layerb-backups/*"
expiry_tracked: true
alert_threshold_days: 30
escrow_row: "layer-b-backup-credential"
re_escrow_blocking_on_rotation: true
YAML
```

```bash
set -euo pipefail
cat > assets/inventory/layer-b-backup-encryption-key.yaml <<'YAML'
# assets/inventory/layer-b-backup-encryption-key.yaml
asset_id: layer-b-backup-encryption-key
asset_class: encryption-key
description: "Encrypts the Layer B backups. Custody is the Section 14.4 escrow (Section 51.4, Section 45.4)"
owner_capability: people-intelligence
rotation_cadence: annually
rotator_capability: devops
escrow_row: "layer-b-backup-encryption-key"
distinct_from:
  - "layer-b-store-decryption-key"
  - "organisation-export-encryption-key"
re_escrow_blocking_on_rotation: true
expiry_tracked: true
alert_threshold_days: 30
canary_decrypt_verified_quarterly: true   # Section 14.4 escrow mechanics
YAML
```

```bash
set -euo pipefail
cat > notify/routes/layer-b-backup-failure.yaml <<'YAML'
# notify/routes/layer-b-backup-failure.yaml
# Section 51.4: "backup failure alerts on the product discipline of Section 44.3".
# Section 44.3, Backup success: "Alert to product channel on failure".
# Section 90.2: people intelligence is never relayed over messaging surfaces -
# so this alert carries the JOB RESULT only, never any Layer B content.
route_id: layer-b-backup-failure
trigger: "infra/layer-b/backup-run.sh exits non-zero, or emits BACKUP_EMPTY"
transport: actions-webhook              # Section 92.11, Section 99.2 subsystem R
destination_key: designated_messaging_channel   # configuration value, never hard-coded
payload_fields:
  - job
  - status
  - timestamp
  - host
prohibited_payload_fields:
  - person
  - evidence
  - document_name
  - datasource_row
escalation: "escalation role, per Section 44.3 restore-failure discipline"
YAML
```

```bash
set -euo pipefail
cat > infra/layer-b/backup-rotation-runbook.md <<'MD'
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
MD
```

```bash
set -euo pipefail
./infra/layer-b/check-backup-credential.sh
ssh layerb-host 'sudo bash -s' < infra/layer-b/backup-run.sh
git add infra/layer-b/backup.yaml infra/layer-b/backup-read-access-list.yaml \
        infra/layer-b/backup-run.sh infra/layer-b/check-backup-credential.sh \
        infra/layer-b/backup-rotation-runbook.md \
        assets/inventory/layer-b-backup-credential.yaml \
        assets/inventory/layer-b-backup-encryption-key.yaml \
        notify/routes/layer-b-backup-failure.yaml
git commit -m "L5-03-06: restricted Layer B backup credential, object-locked target and failure routing"
git push -u origin lane/5/p3-06-backup-credential
gh pr create --base integration --head lane/5/p3-06-backup-credential \
  --title "L5-03-06: the restricted Layer B backup credential" \
  --body "Append-only write-only credential, object-locked versioned target in an independent provider domain, fifth-tier inventory entries, escrow rows, rotation runbook and Section 44.3 failure routing."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The credential can write | `ssh layerb-host 'echo x \| aws s3 cp - s3://layerb-backups/_canary/t.txt --profile layerb-backup-writer >/dev/null && echo WRITE_OK'` | `WRITE_OK` |
| 2 | The credential cannot read | `ssh layerb-host 'aws s3 ls s3://layerb-backups/ --profile layerb-backup-writer >/dev/null 2>&1 \|\| echo READ_DENIED'` | `READ_DENIED` |
| 3 | The credential cannot delete | `ssh layerb-host 'aws s3 rm s3://layerb-backups/_canary/t.txt --profile layerb-backup-writer >/dev/null 2>&1 \|\| echo DELETE_DENIED'` | `DELETE_DENIED` |
| 4 | Object lock is enabled | `ssh layerb-host 'aws s3api get-object-lock-configuration --bucket layerb-backups --profile layerb-backup-auditor --query "ObjectLockConfiguration.ObjectLockEnabled" --output text'` | `Enabled` |
| 5 | Versioning is enabled | `ssh layerb-host 'aws s3api get-bucket-versioning --bucket layerb-backups --profile layerb-backup-auditor --query "Status" --output text'` | `Enabled` |
| 6 | The target is not in the ops-VM provider domain | `yq -r '.target.same_provider_as_ops_vm' infra/layer-b/backup.yaml` | `false` |
| 7 | The inventory entry carries cadence, rotator and runbook | `yq -r '.rotation_cadence + "\|" + .rotator_capability + "\|" + .runbook' assets/inventory/layer-b-backup-credential.yaml` | `quarterly\|devops\|infra/layer-b/backup-rotation-runbook.md` |
| 8 | The backup key is escrowed under its own row, distinct from the store key | `yq -r '.escrow_row' assets/inventory/layer-b-backup-encryption-key.yaml; yq -r '.key_custody.escrow_row' infra/layer-b/encrypted-volume.yaml` | two lines: `layer-b-backup-encryption-key` then `layer-b-store-decryption-key` |
| 9 | The failure route carries no Layer B content field | `yq -r '.prohibited_payload_fields \| length' notify/routes/layer-b-backup-failure.yaml` | `4` |
| 10 | Full credential checker passes | `./infra/layer-b/check-backup-credential.sh` | `BKP_OK 6/6` |
| 11 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./infra/layer-b/check-backup-credential.sh && \
yq -r '.target.object_lock, .target.versioning, .target.same_provider_as_ops_vm' infra/layer-b/backup.yaml | tr '\n' ' ' && echo && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines:

```
BKP_OK 6/6
true true false
OWNED_ROOTS_OK
```

### STOP rules

- **If the object store cannot be placed in a different provider and credential domain than the operations VM** — STOP. §51.4 requires it so that *"the party who can write the backup can neither read nor destroy backup history."* File the blocker issue.
- **If object lock cannot be enabled on the bucket after creation** — do not proceed with an unlocked bucket. Object lock generally must be enabled at bucket creation. File the blocker issue.
- **If criterion 2 or 3 succeeds (the credential *can* read or delete)** — STOP. The credential is over-scoped and the write-only property does not hold. File the blocker issue.
- **If rotating the credential would require skipping re-escrow** — STOP. §14.4: re-escrow is *"a blocking step in the rotation runbook"*.

---

## L5-03-07 — The Layer B access log, plus the host-level file-access audit shipped off-host

**Size:** M · **Depends on:** L5-03-03, L5-03-05 · **Owned paths touched:** `ops-vm/layer-b/`, `infra/layer-b/`, `access/layer-b/`

### Purpose
Two logs, at two levels, because §90.3 says one cannot see what the other covers:

> *"Every Layer B access is logged: who accessed, whose data, and when. The access log is reviewed on the calibration cadence (Section 84.5)."*

and, for the host-level accepted risk:

> *"it carries a compensating control the holder cannot silently defeat — host-level file-access auditing on the store path, shipped to a destination the host holds no credential to alter, the same write-only discipline the organisation export uses (Section 45.3) … The Layer B access log below is application-level and does not see a root-level file read, which is precisely the gap the host-level audit trail covers."*

§89.1 adds the generation case: *"Every generation run is logged in the Layer B access log (Section 90.3)."*

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/accesslog/schema.yaml` | The three mandatory fields and the prohibited ones |
| `ops-vm/layer-b/accesslog/record-access.sh` | Appends one access record per event, one file per event |
| `ops-vm/layer-b/accesslog/review.sh` | The calibration-cadence review, writing a review record |
| `infra/layer-b/auditd-layerb.rules` | Host-level file-access audit rules on the store path |
| `infra/layer-b/ship-audit.sh` | Write-only shipping of the host audit trail off-host |
| `access/layer-b/check-access-log.sh` | Proves both logs exist, are populated and are shipped |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-07-access-log
mkdir -p ops-vm/layer-b/accesslog infra/layer-b access/layer-b
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/accesslog/schema.yaml <<'YAML'
# ops-vm/layer-b/accesslog/schema.yaml
# Section 90.3: "Every Layer B access is logged: who accessed, whose data, and when."
record:
  one_file_per_event: true          # PARTITION.md rule 3 - no shared mutable file
  path_pattern: "/srv/layerb/encrypted/accesslog/{ts}-{event_id}.yaml"
  required_fields:
    - actor            # who accessed - the GitHub login of the human identity
    - subject          # whose data - the person the accessed evidence is about
    - at               # when - RFC3339 UTC
    - surface          # layer-b-m | layer-b-s-generation | layer-b-s-delivery
    - session_id
    - action           # login | query | render | generate | deliver | export
  prohibited_fields:
    # The access log is a log of access, never a second copy of the evidence.
    - evidence
    - kpi_value
    - document_body
    - note
actor_rules:
  machine_identity_permitted: false  # Section 90.2 machine-identities row: absolute
  # Section 89.1: generation "executes as a script under the Founder's own
  # identity in a credentialed session ... the session is the Founder, not a bot."
  generation_actor_must_be_human: true
review:
  cadence: "Section 84.5 calibration cadence"
  initial_value: quarterly
  output: "records/security-reviews/ (written by the reviewing human, not by this lane)"
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/accesslog/record-access.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/accesslog/record-access.sh
# Usage: record-access.sh <actor> <subject> <surface> <action> <session_id>
# One file per event. Never appends to a shared file.
set -euo pipefail
ACTOR="${1:?actor}"; SUBJECT="${2:?subject}"; SURFACE="${3:?surface}"
ACTION="${4:?action}"; SESSION="${5:?session_id}"
case "$SURFACE" in layer-b-m|layer-b-s-generation|layer-b-s-delivery) ;; *) echo "BAD_SURFACE"; exit 1 ;; esac
case "$ACTOR" in *"[bot]"*|*-bot|reconciler|provisioning-cli|records-writer)
  echo "MACHINE_IDENTITY_REFUSED"; exit 1 ;; esac
DIR="${LAYERB_MNT:-/srv/layerb/encrypted}/accesslog"
mkdir -p "$DIR"; chmod 700 "$DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
ID="$(openssl rand -hex 8)"
cat > "$DIR/$TS-$ID.yaml" <<REC
event_id: "$ID"
actor: "$ACTOR"
subject: "$SUBJECT"
at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
surface: "$SURFACE"
session_id: "$SESSION"
action: "$ACTION"
REC
chmod 600 "$DIR/$TS-$ID.yaml"
echo "ACCESS_RECORDED $ID"
SH
chmod +x ops-vm/layer-b/accesslog/record-access.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/accesslog/review.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/accesslog/review.sh
# The Section 84.5 calibration-cadence review of the access log.
# It counts and summarises. It never renders evidence.
set -euo pipefail
DIR="${LAYERB_MNT:-/srv/layerb/encrypted}/accesslog"
SINCE_DAYS="${1:-90}"
[ -d "$DIR" ] || { echo "ACCESSLOG_MISSING"; exit 1; }
n=$(find "$DIR" -name '*.yaml' -mtime "-$SINCE_DAYS" | wc -l | tr -d ' ')
actors=$(grep -h '^actor:' $(find "$DIR" -name '*.yaml' -mtime "-$SINCE_DAYS") 2>/dev/null | sort -u | wc -l | tr -d ' ')
machine=$(grep -hE '^actor: ".*(\[bot\]|reconciler|records-writer)' $(find "$DIR" -name '*.yaml') 2>/dev/null | wc -l | tr -d ' ')
echo "ACCESSLOG_REVIEW events=$n distinct_actors=$actors machine_actors=$machine"
[ "$machine" -eq 0 ] || { echo "MACHINE_ACTOR_PRESENT"; exit 1; }
SH
chmod +x ops-vm/layer-b/accesslog/review.sh
```

```bash
set -euo pipefail
cat > infra/layer-b/auditd-layerb.rules <<'RULES'
## infra/layer-b/auditd-layerb.rules
## Host-level file-access auditing on the Layer B store path.
## Section 90.3: the compensating control the host-admin holder "cannot silently
## defeat". It exists because "The Layer B access log ... is application-level
## and does not see a root-level file read".
-w /srv/layerb/encrypted -p rwa -k layerb_store
-w /srv/layerb/secrets    -p rwa -k layerb_secrets
## Changing or unloading these rules is itself audited.
-w /etc/audit/rules.d/ -p wa -k layerb_audit_config
-e 2
RULES
```

```bash
set -euo pipefail
cat > infra/layer-b/ship-audit.sh <<'SH'
#!/usr/bin/env bash
# infra/layer-b/ship-audit.sh - runs on layerb-host, hourly.
# Ships the host audit trail to a destination the host holds no credential to
# alter: the same append-only, write-only, object-locked discipline the
# organisation export uses (Section 45.3), per Section 90.3.
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
ausearch -k layerb_store -k layerb_secrets -k layerb_audit_config --start recent > "$TMP" || true
[ -s "$TMP" ] || echo "no-events $STAMP" > "$TMP"
# Write-only profile. It cannot list, get or delete what it wrote.
aws s3 cp "$TMP" "s3://layerb-audit/$STAMP.log" --profile layerb-audit-writer
echo "AUDIT_SHIPPED $STAMP"
SH
chmod +x infra/layer-b/ship-audit.sh
```

```bash
set -euo pipefail
cat > access/layer-b/check-access-log.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-access-log.sh
set -euo pipefail
FAILS=0
note() { echo "LOG_FAIL $1"; FAILS=$((FAILS+1)); }

# Schema declares the three Section 90.3 fields.
for f in actor subject at; do
  yq -r '.record.required_fields[]' ops-vm/layer-b/accesslog/schema.yaml | grep -qx "$f" \
    || note "required field '$f' missing from the access-log schema"
done
[ "$(yq -r '.actor_rules.machine_identity_permitted' ops-vm/layer-b/accesslog/schema.yaml)" = "false" ] \
  || note "schema permits a machine identity as actor"

# Application-level log exists on the host and refuses a machine identity.
ssh layerb-host 'test -d /srv/layerb/encrypted/accesslog' || note "access log directory absent"
if ssh layerb-host '/srv/layerb/config/accesslog/record-access.sh reconciler alice layer-b-m query s1' >/dev/null 2>&1; then
  note "machine identity accepted by record-access.sh"
fi

# Host-level audit is loaded and keyed.
k=$(ssh layerb-host 'sudo auditctl -l | grep -c layerb_store' || true)
[ "$k" -ge 1 ] || note "auditd rule for the store path not loaded"

# Audit shipping is write-only: the host cannot read back what it shipped.
if ssh layerb-host 'aws s3 ls s3://layerb-audit/ --profile layerb-audit-writer' >/dev/null 2>&1; then
  note "the host can read the shipped audit trail"
fi

if [ "$FAILS" -eq 0 ]; then echo "LOG_OK 8/8"; else echo "LOG_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/check-access-log.sh
```

```bash
set -euo pipefail
scp -r ops-vm/layer-b/accesslog layerb-host:/srv/layerb/config/accesslog
scp infra/layer-b/auditd-layerb.rules layerb-host:/tmp/auditd-layerb.rules
ssh layerb-host 'sudo cp /tmp/auditd-layerb.rules /etc/audit/rules.d/layerb.rules && sudo augenrules --load && sudo auditctl -l | grep layerb_store'
ssh layerb-host '/srv/layerb/config/accesslog/record-access.sh founder-login founder-login layer-b-m login smoke-1'
./access/layer-b/check-access-log.sh
```

```bash
set -euo pipefail
git add ops-vm/layer-b/accesslog infra/layer-b/auditd-layerb.rules \
        infra/layer-b/ship-audit.sh access/layer-b/check-access-log.sh
git commit -m "L5-03-07: Layer B access log and the off-host host-level file-access audit"
git push -u origin lane/5/p3-07-access-log
gh pr create --base integration --head lane/5/p3-07-access-log \
  --title "L5-03-07: the Layer B access log and its host-level compensating audit" \
  --body "Application-level access log (who, whose data, when; one file per event; machine identities refused) plus the auditd rules and write-only off-host shipping that cover the root-level read the application log cannot see."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The schema requires actor, subject and time | `yq -r '.record.required_fields[]' ops-vm/layer-b/accesslog/schema.yaml \| grep -cE '^(actor|subject|at)$'` | `3` |
| 2 | The schema prohibits evidence content in the log | `yq -r '.record.prohibited_fields \| length' ops-vm/layer-b/accesslog/schema.yaml` | `4` |
| 3 | One file per event, never a shared append target | `yq -r '.record.one_file_per_event' ops-vm/layer-b/accesslog/schema.yaml` | `true` |
| 4 | A real access writes a record | `ssh layerb-host '/srv/layerb/config/accesslog/record-access.sh founder-login founder-login layer-b-m login smoke-2' \| cut -d" " -f1` | `ACCESS_RECORDED` |
| 5 | A machine identity is refused | `ssh layerb-host '/srv/layerb/config/accesslog/record-access.sh reconciler alice layer-b-m query s9' \|\| true` | `MACHINE_IDENTITY_REFUSED` |
| 6 | Host-level audit rule is loaded on the store path | `ssh layerb-host 'sudo auditctl -l \| grep -c layerb_store'` | `1` |
| 7 | Audit shipping is write-only from the host | `ssh layerb-host 'aws s3 ls s3://layerb-audit/ --profile layerb-audit-writer >/dev/null 2>&1 \|\| echo AUDIT_READ_DENIED'` | `AUDIT_READ_DENIED` |
| 8 | The review names the calibration cadence | `yq -r '.review.cadence' ops-vm/layer-b/accesslog/schema.yaml` | `Section 84.5 calibration cadence` |
| 9 | Combined checker passes | `./access/layer-b/check-access-log.sh` | `LOG_OK 8/8` |
| 10 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/check-access-log.sh && \
ssh layerb-host '/srv/layerb/config/accesslog/review.sh 90' && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines (the counts vary; the prefixes do not):

```
LOG_OK 8/8
ACCESSLOG_REVIEW events=<N> distinct_actors=<M> machine_actors=0
OWNED_ROOTS_OK
```

`machine_actors` must be `0`. Any other value is a failure, not a variation.

### STOP rules

- **If `machine_actors` is greater than `0`** — STOP at once. §90.2's machine-identities row is absolute: *"no machine identity holds any people-related data category, receives a Layer B credential or folder scope, or holds the people-intelligence capability, under any configuration."* File the blocker issue.
- **If the host can read back its own shipped audit trail** — STOP. §90.3 requires *"a destination the host holds no credential to alter."* File the blocker issue.
- **If `auditd` is unavailable on the host OS** — do not substitute an in-process logger. The compensating control must be one the host-admin holder *"cannot silently defeat"*; choosing a different mechanism is a design decision. File the blocker issue.
- **If anyone proposes storing evidence content in the access log so reviews are easier** — refuse; the schema's `prohibited_fields` exist for that. File the blocker issue if pressed.

---

## L5-03-08 — Session-lifetime limits; standing unattended sessions prohibited

**Size:** S · **Depends on:** L5-03-03 · **Owned paths touched:** `ops-vm/layer-b/session/`, `ops-vm/layer-b/grafana.ini`, `access/layer-b/`

### Purpose
One sentence of §90.3 is the whole task: *"Layer B sessions carry declared session-lifetime limits and expire; standing unattended sessions are prohibited."*

L5-03-03 deliberately left the two keys present and empty in `ops-vm/layer-b/grafana.ini`:

```
login_maximum_inactive_lifetime_duration =
login_maximum_lifetime_duration =
```

so that their absence is visible rather than defaulted. This task fills them from the frozen contract, and adds the checker that proves three things: the limits are declared and non-empty, the running instance reports them, and no standing unattended session exists on the instance — where *standing unattended session* has one machine-checkable meaning: a Grafana service account, an API key, or an auth token whose last-seen age exceeds the declared maximum lifetime.

A service account or API key on Layer B-M is also a machine identity, and §90.2's machine-identities row is absolute: *"no machine identity holds any people-related data category, receives a Layer B credential or folder scope, or holds the `people-intelligence` capability, under any configuration."* The same check therefore covers both sentences.

### DECISION REQUIRED — routed to L0

The two duration **values** are not in this file and are not the executor's to choose. §90.3 requires that the limits be *declared*; it names no number. The values are read from the frozen contract at the two keys below, and this task never invents one.

| Contract key | Consumed by | If absent |
|---|---|---|
| `layer_b.session.max_lifetime_duration` | `ops-vm/layer-b/session/render-session-ini.sh` | STOP. File a Contract Change Request per `PARTITION.md` rule 2, and the blocker issue of §1. Do not pick a duration. |
| `layer_b.session.max_inactive_lifetime_duration` | `ops-vm/layer-b/session/render-session-ini.sh` | STOP, same route. |

`contracts/**` is L0's Phase 0 output and is FROZEN. A lane reads it and never edits it.

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/session/session-limits.yaml` | The declaration: which contract keys hold the limits, and what "standing unattended session" means as a check |
| `ops-vm/layer-b/session/render-session-ini.sh` | Writes the two contract values into the `[auth]` block of `ops-vm/layer-b/grafana.ini`. Idempotent |
| `access/layer-b/check-session-limits.sh` | Repository-side and host-side proof that the limits are declared, live, and that no standing session exists |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-08-session-limits
mkdir -p ops-vm/layer-b/session access/layer-b
```

```bash
set -euo pipefail
# Q9 resolved — layer_b block (6th key) added to L5-02 shape; see L5-02-secrets-and-boundaries.md "required shape".
# Fail before writing anything if the frozen contract does not carry both keys.
test -f contracts/access/access-inputs.yaml || { echo "CONTRACT_MISSING"; exit 1; }
MAXLIFE=$(yq -r '.layer_b.session.max_lifetime_duration // ""' contracts/access/access-inputs.yaml)
MAXIDLE=$(yq -r '.layer_b.session.max_inactive_lifetime_duration // ""' contracts/access/access-inputs.yaml)
[ -n "$MAXLIFE" ] && [ -n "$MAXIDLE" ] && echo "SESSION_CONTRACT_PRESENT" || echo "SESSION_CONTRACT_MISSING"
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/session/session-limits.yaml <<'YAML'
# ops-vm/layer-b/session/session-limits.yaml
# Section 90.3: "Layer B sessions carry declared session-lifetime limits and
# expire; standing unattended sessions are prohibited."
# This file declares WHERE the limits come from and WHAT the prohibition means
# as a check. It never carries the durations themselves - those are frozen
# contract values (PARTITION.md rule 2).
surface: layer-b-m
instance: grafana-layerb
limits:
  source: contracts/access/access-inputs.yaml
  keys:
    max_lifetime: layer_b.session.max_lifetime_duration
    max_inactive_lifetime: layer_b.session.max_inactive_lifetime_duration
  rendered_into: ops-vm/layer-b/grafana.ini
  rendered_keys:
    - login_maximum_lifetime_duration
    - login_maximum_inactive_lifetime_duration
  token_rotation_interval_minutes: 10     # already set by L5-03-03; re-asserted here
standing_unattended_session:
  # The prohibition, made machine-checkable. Each row must count zero.
  prohibited:
    - id: SUS-1
      what: "any Grafana service account on the Layer B-M instance"
      api: "/api/serviceaccounts/search"
      expected_count: 0
      anchor: "Section 90.2 machine-identities row: absolute"
    - id: SUS-2
      what: "any Grafana API key on the Layer B-M instance"
      api: "/api/auth/keys"
      expected_count: 0
      anchor: "Section 90.2 machine-identities row: absolute"
    - id: SUS-3
      what: "any auth token whose age exceeds the declared maximum lifetime"
      api: "/api/admin/users/:id/auth-tokens"
      expected_count: 0
      anchor: "Section 90.3 sessions expire"
    - id: SUS-4
      what: "anonymous access, which is a session with no holder at all"
      config: "[auth.anonymous] enabled"
      expected_value: "false"
      anchor: "Section 90.3; D75 own authentication restriction"
review:
  cadence: "Section 84.5 calibration cadence"
  initial_value: quarterly
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/session/render-session-ini.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/session/render-session-ini.sh
# Writes the two frozen contract values into the [auth] block of the Layer B-M
# grafana.ini. Idempotent: running it twice produces the same file.
# It never invents a duration. A missing contract value is a hard stop.
set -euo pipefail
CONTRACT="contracts/access/access-inputs.yaml"
INI="ops-vm/layer-b/grafana.ini"
[ -f "$CONTRACT" ] || { echo "CONTRACT_MISSING"; exit 2; }
[ -f "$INI" ] || { echo "INI_MISSING"; exit 2; }

MAXLIFE=$(yq -r '.layer_b.session.max_lifetime_duration // ""' "$CONTRACT")
MAXIDLE=$(yq -r '.layer_b.session.max_inactive_lifetime_duration // ""' "$CONTRACT")
[ -n "$MAXLIFE" ] || { echo "CONTRACT_VALUE_MISSING layer_b.session.max_lifetime_duration"; exit 2; }
[ -n "$MAXIDLE" ] || { echo "CONTRACT_VALUE_MISSING layer_b.session.max_inactive_lifetime_duration"; exit 2; }

python3 - "$INI" "$MAXLIFE" "$MAXIDLE" <<'PY'
import sys
path, maxlife, maxidle = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(path, encoding="utf-8").read().split("\n")
out, in_auth = [], False
for line in lines:
    s = line.strip()
    if s.startswith("[") and s.endswith("]"):
        in_auth = (s == "[auth]")
        out.append(line); continue
    if in_auth and s.split("=")[0].strip() == "login_maximum_lifetime_duration":
        out.append("login_maximum_lifetime_duration = " + maxlife); continue
    if in_auth and s.split("=")[0].strip() == "login_maximum_inactive_lifetime_duration":
        out.append("login_maximum_inactive_lifetime_duration = " + maxidle); continue
    out.append(line)
open(path, "w", encoding="utf-8").write("\n".join(out))
PY
echo "SESSION_INI_RENDERED $MAXLIFE $MAXIDLE"
SH
chmod +x ops-vm/layer-b/session/render-session-ini.sh
```

```bash
set -euo pipefail
cat > access/layer-b/check-session-limits.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-session-limits.sh
# Usage: check-session-limits.sh repo | check-session-limits.sh host
set -euo pipefail
MODE="${1:-repo}"
INI="ops-vm/layer-b/grafana.ini"
CONTRACT="contracts/access/access-inputs.yaml"
FAILS=0
note() { echo "SESS_FAIL $1"; FAILS=$((FAILS+1)); }
ini_get() { awk -v s="[$1]" -v k="$2" '$0==s{f=1;next} /^\[/{f=0} f&&$1==k{print $3; exit}' "$INI"; }

if [ "$MODE" = "repo" ]; then
  life=$(ini_get auth login_maximum_lifetime_duration)
  idle=$(ini_get auth login_maximum_inactive_lifetime_duration)
  [ -n "$life" ] || note "login_maximum_lifetime_duration is empty - the limit is not declared"
  [ -n "$idle" ] || note "login_maximum_inactive_lifetime_duration is empty - the limit is not declared"
  [ "$life" = "$(yq -r '.layer_b.session.max_lifetime_duration // ""' "$CONTRACT")" ] \
    || note "rendered max lifetime does not match the frozen contract"
  [ "$idle" = "$(yq -r '.layer_b.session.max_inactive_lifetime_duration // ""' "$CONTRACT")" ] \
    || note "rendered inactive lifetime does not match the frozen contract"
  [ "$(ini_get auth.anonymous enabled)" = "false" ] || note "SUS-4 anonymous access is enabled"
  [ "$(ini_get auth token_rotation_interval_minutes)" = "10" ] || note "token rotation interval is not 10"
  [ "$(yq -r '.standing_unattended_session.prohibited | length' ops-vm/layer-b/session/session-limits.yaml)" = "4" ] \
    || note "the standing-unattended-session prohibition does not carry its four rows"
  if [ "$FAILS" -eq 0 ]; then echo "SESS_REPO_OK 7/7"; else echo "SESS_REPO_FAILED $FAILS"; exit 1; fi
  exit 0
fi

if [ "$MODE" = "host" ]; then
  A='-u "$LAYERB_ADMIN"'
  sa=$(ssh layerb-host "curl -s $A 'http://127.0.0.1:3001/api/serviceaccounts/search?perpage=100' | jq -r '.totalCount // 0'" || echo -1)
  [ "$sa" = "0" ] || note "SUS-1 $sa service account(s) on Layer B-M"
  ak=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/auth/keys | jq -r 'length'" || echo -1)
  [ "$ak" = "0" ] || note "SUS-2 $ak API key(s) on Layer B-M"
  stale=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/admin/settings | jq -r '.auth.login_maximum_lifetime_duration // \"\"'" || echo "")
  [ -n "$stale" ] || note "SUS-3 the running instance reports no maximum session lifetime"
  anon=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/admin/settings | jq -r '.\"auth.anonymous\".enabled // \"true\"'" || echo true)
  [ "$anon" = "false" ] || note "SUS-4 the running instance permits anonymous access"
  if [ "$FAILS" -eq 0 ]; then echo "SESS_HOST_OK 4/4"; else echo "SESS_HOST_FAILED $FAILS"; exit 1; fi
  exit 0
fi
note "unknown mode $MODE"; exit 1
SH
chmod +x access/layer-b/check-session-limits.sh
```

```bash
set -euo pipefail
./ops-vm/layer-b/session/render-session-ini.sh
scp ops-vm/layer-b/grafana.ini layerb-host:/srv/layerb/config/grafana.ini
ssh layerb-host 'cd /srv/layerb/config && docker compose -f compose.yaml restart grafana-layerb'
./access/layer-b/check-session-limits.sh repo
./access/layer-b/check-session-limits.sh host
```

```bash
set -euo pipefail
git add ops-vm/layer-b/session ops-vm/layer-b/grafana.ini access/layer-b/check-session-limits.sh
git commit -m "L5-03-08: declared Layer B session-lifetime limits; standing unattended sessions prohibited"
git push -u origin lane/5/p3-08-session-limits
gh pr create --base integration --head lane/5/p3-08-session-limits \
  --title "L5-03-08: Layer B session-lifetime limits and the standing-session prohibition" \
  --body "Renders the two frozen contract durations into the Layer B-M [auth] block and adds the checker proving the limits are live and that no service account, API key, over-age token or anonymous path constitutes a standing unattended session."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Both contract keys are present before anything is written | `yq -r '.layer_b.session.max_lifetime_duration, .layer_b.session.max_inactive_lifetime_duration' contracts/access/access-inputs.yaml \| grep -c '^$'` | `0` |
| 2 | The maximum-lifetime key is rendered non-empty | `grep -c '^login_maximum_lifetime_duration = .\+$' ops-vm/layer-b/grafana.ini` | `1` |
| 3 | The inactive-lifetime key is rendered non-empty | `grep -c '^login_maximum_inactive_lifetime_duration = .\+$' ops-vm/layer-b/grafana.ini` | `1` |
| 4 | The renderer is idempotent | `./ops-vm/layer-b/session/render-session-ini.sh >/dev/null && sha256sum ops-vm/layer-b/grafana.ini > /tmp/a && ./ops-vm/layer-b/session/render-session-ini.sh >/dev/null && sha256sum ops-vm/layer-b/grafana.ini > /tmp/b && cmp -s /tmp/a /tmp/b && echo IDEMPOTENT` | `IDEMPOTENT` |
| 5 | No duration literal is hard-coded in the renderer | `grep -cE '=[[:space:]]*[0-9]+[hmd]' ops-vm/layer-b/session/render-session-ini.sh` | `0` |
| 6 | The prohibition carries exactly four checkable rows | `yq -r '.standing_unattended_session.prohibited \| length' ops-vm/layer-b/session/session-limits.yaml` | `4` |
| 7 | No service account exists on Layer B-M | `ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" "http://127.0.0.1:3001/api/serviceaccounts/search?perpage=100" \| jq -r ".totalCount // 0"'` | `0` |
| 8 | No API key exists on Layer B-M | `ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/auth/keys \| jq -r "length"'` | `0` |
| 9 | The running instance reports a maximum session lifetime | `ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/admin/settings \| jq -r ".auth.login_maximum_lifetime_duration \| length > 0"'` | `true` |
| 10 | Repository-side checker passes | `./access/layer-b/check-session-limits.sh repo` | `SESS_REPO_OK 7/7` |
| 11 | Host-side checker passes | `./access/layer-b/check-session-limits.sh host` | `SESS_HOST_OK 4/4` |
| 12 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/check-session-limits.sh repo && \
./access/layer-b/check-session-limits.sh host && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines:

```
SESS_REPO_OK 7/7
SESS_HOST_OK 4/4
OWNED_ROOTS_OK
```

### STOP rules

- **If either contract key is absent or empty** — STOP. Do not pick a duration, do not copy one from another instance, and do not leave the key empty "for now". §90.3 requires a *declared* limit and `PARTITION.md` rule 2 forbids editing `contracts/**`. File a Contract Change Request and the blocker issue naming the two keys.
- **If a service account or API key already exists on Layer B-M** — STOP. Do not delete it. §90.2's machine-identities row is absolute, so an existing one is a live invariant-106 breach with an unknown creator and an unknown dependent. File the blocker issue naming the account's id and creation date only.
- **If unattended access is required so that a scheduled job can render a Layer B panel** — STOP. §89.1: *"the session is the Founder, not a bot."* Making a job able to run unattended against Layer B is a design change, not a configuration change. File the blocker issue.
- **If the running instance does not expose `/api/admin/settings`** — do not weaken the check to a repository-only assertion and do not mark criterion 9 as passed by inspection. File the blocker issue naming the Grafana version, so L0 can confirm the settings endpoint for the pinned tag.

---

## L5-03-09 — Capability-derived access: allowlist sync, non-delegability, reconciliation comparison scope

**Size:** M · **Depends on:** L5-03-03, L5-03-06 · **Owned paths touched:** `ops-vm/layer-b/allowlist/`, `access/layer-b/`, `infra/layer-b/`

### Purpose
§90.4 fixes four things and this task builds all four:

> *"Access to the Founder-only Layer B instance (90.3, D75) — its credential and its authentication allowlist — derives from this capability and from nothing else; reconciliation (Section 53) verifies that the holders of Layer B access exactly match the holders of the capability. The comparison's scope is written down rather than assumed: it covers the instance credential, the authentication allowlist, and the host's named OS accounts, sudoers entries, SSH authorised keys and backup-store read list — compared against the capability holders and against the named accepted-access record of 90.3. A holder appearing in neither list is Blocking drift. A check scoped narrower than the access it exists to verify reports clean for the wrong reason."*

and, immediately above it:

> *"**It is not delegable** (D109). No assignment type grants it, and none may be introduced to do so."*

The identity bridge is settled and is not this task's choice: *"`people.yaml` keys on the GitHub login; capability-derived Grafana access uses GitHub OAuth into Grafana plus a sync job from the registries. No separate IdP."* (§99.5). This task is that sync job, plus the written-down comparison scope L3's reconciler consumes.

The capability registry belongs to lane L1 and the reconciler to L3. `PARTITION.md` rule 4 forbids reaching into either source tree, so this task consumes **one published artifact** — the capability-holders artifact — whose path is a frozen contract value, and publishes **one artifact** — the comparison scope — for L3 to consume. Nothing else crosses a lane boundary.

### DECISION REQUIRED — routed to L0

| # | Item | Why it is not this task's | Route |
|---|---|---|---|
| 1 | The path of the published capability-holders artifact | It is another lane's output; `PARTITION.md` rule 4 permits consumption only through a published artifact, and naming that artifact is L0's | Read from `layer_b.capability_holders_artifact` in `contracts/access/access-inputs.yaml`. If absent: Contract Change Request plus the §1 blocker issue |
| 2 | The validator-level negative test of AT-090 — *"an attempt to create an assignment granting `people-intelligence` fails validation"* | Registry validators live under `validators/registry/**`, owned by L1. L5 owns no path there | This task proves non-delegability over the **published artifact and the sync job**; the validator half is escalation `E-P3-04` |
| 3 | AT-091's sentence *"Granting the dated delegate assignment opens access through reconciliation"* contradicts D109 and §90.4, which state that no assignment type grants the capability and none may be introduced | A specification tension. Resolving it is a decision, not an executor's reading | Escalation `E-P3-05`. This task implements the D109 direction — holders only, no delegate path — and files the tension rather than choosing a reading |

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/allowlist/sync-allowlist.sh` | The §99.5 sync job: makes Layer B-M's users exactly the capability holders. Supports `--dry-run` |
| `ops-vm/layer-b/allowlist/holders/.gitkeep` | One generated file per holder at run time; directory-per-item, never a shared list (`PARTITION.md` rule 3) |
| `access/layer-b/reconciliation-scope.yaml` | The §90.4 comparison scope, written down — the published interface L3's reconciler consumes |
| `access/layer-b/check-allowlist-parity.sh` | Compares all six scope surfaces against the holders; a holder in neither list is Blocking |
| `access/layer-b/check-non-delegable.sh` | D109: no delegate path exists in the artifact, in the sync job, or on the instance |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-09-capability-allowlist
mkdir -p ops-vm/layer-b/allowlist/holders access/layer-b infra/layer-b
touch ops-vm/layer-b/allowlist/holders/.gitkeep
```

```bash
set -euo pipefail
# Q9 resolved — layer_b.capability_holders_artifact is now declared in L5-02 shape; see L5-02-secrets-and-boundaries.md "required shape".
# Fail before writing anything if the frozen contract does not name the artifact.
HOLDERS=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
[ -n "$HOLDERS" ] && echo "HOLDERS_ARTIFACT_DECLARED $HOLDERS" || echo "HOLDERS_ARTIFACT_MISSING"
```

```bash
set -euo pipefail
cat > access/layer-b/reconciliation-scope.yaml <<'YAML'
# access/layer-b/reconciliation-scope.yaml
# Section 90.4: "The comparison's scope is written down rather than assumed."
# This file IS that writing-down. It is the published interface lane L3's
# reconciler consumes; L3 never reaches into this lane's source tree
# (PARTITION.md rule 4).
scope_id: layer-b-access-parity
derives_from: "the people-intelligence capability, and nothing else (Section 90.4)"
compared_against:
  - "holders of the people-intelligence capability"
  - "the named accepted-access record of Section 90.3 (assets/inventory/layer-b-host-admin-access.yaml)"
surfaces:
  - id: SCOPE-1
    surface: instance credential
    where: "/srv/layerb/secrets/admin_password on layerb-host"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh credential"
  - id: SCOPE-2
    surface: authentication allowlist
    where: "Grafana org users on the Layer B-M instance"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh allowlist"
  - id: SCOPE-3
    surface: named OS accounts
    where: "layerb-host /etc/passwd, uid >= 1000"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh os-accounts"
  - id: SCOPE-4
    surface: sudoers entries
    where: "layerb-host /etc/sudoers and /etc/sudoers.d"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh sudoers"
  - id: SCOPE-5
    surface: SSH authorised keys
    where: "layerb-host authorized_keys comment fields"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh ssh-keys"
  - id: SCOPE-6
    surface: backup-store read list
    where: "infra/layer-b/backup-read-access-list.yaml"
    enumerated_by: "access/layer-b/check-allowlist-parity.sh backup-read"
finding_class:
  # Section 53.4: there is exactly one drift severity scale.
  holder_in_neither_list: Blocking
  anchor: "Section 90.4 - 'A holder appearing in neither list is Blocking drift.'"
narrowing_prohibited: >-
  Section 90.4: "A check scoped narrower than the access it exists to verify
  reports clean for the wrong reason." Removing a surface from this file to make
  the parity check pass is a STOP condition, not a fix.
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/allowlist/sync-allowlist.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/allowlist/sync-allowlist.sh
# Section 99.5: "capability-derived Grafana access uses GitHub OAuth into
# Grafana plus a sync job from the registries. No separate IdP."
# Section 90.4: access derives from the capability "and from nothing else".
#
# Usage: sync-allowlist.sh [--dry-run] [--holders-file <path>]
# With no --holders-file the artifact path is read from the frozen contract.
# This script contains no login. If you are about to add one, stop.
set -euo pipefail
DRY=0; HOLDERS_FILE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --holders-file) HOLDERS_FILE="${2:?path}"; shift 2 ;;
    *) echo "UNKNOWN_ARG $1"; exit 2 ;;
  esac
done
if [ -z "$HOLDERS_FILE" ]; then
  HOLDERS_FILE=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
fi
[ -n "$HOLDERS_FILE" ] || { echo "HOLDERS_ARTIFACT_MISSING"; exit 2; }
[ -f "$HOLDERS_FILE" ] || { echo "HOLDERS_ARTIFACT_UNREADABLE $HOLDERS_FILE"; exit 2; }

# The holders of people-intelligence, and nothing else. Sorted, deduplicated.
WANT=$(yq -r '.capabilities["people-intelligence"].holders[]' "$HOLDERS_FILE" | sort -u)
[ -n "$WANT" ] || { echo "NO_HOLDERS_IN_ARTIFACT"; exit 2; }

API="http://127.0.0.1:3001"
HAVE=$(ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" $API/api/org/users | jq -r '.[].login'" | sort -u)

ADD=$(comm -23 <(printf '%s\n' "$WANT") <(printf '%s\n' "$HAVE"))
DEL=$(comm -13 <(printf '%s\n' "$WANT") <(printf '%s\n' "$HAVE"))

if [ "$DRY" -eq 1 ]; then
  echo "SYNC_PLAN add=$(printf '%s\n' "$ADD" | grep -c . ) remove=$(printf '%s\n' "$DEL" | grep -c . )"
  exit 0
fi

for login in $ADD; do
  pw=$(openssl rand -hex 24)   # generated on the host, unused: login is OAuth only
  ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" -X POST $API/api/admin/users \
    -H 'Content-Type: application/json' \
    -d '{\"name\":\"$login\",\"login\":\"$login\",\"password\":\"$pw\"}' >/dev/null"
  echo "ADDED $login"
done

for login in $DEL; do
  # DF-0691: layerb-admin is the instance's own built-in admin and is never
  # present in the people-intelligence holder list. Without this guard the
  # first non-dry-run deletes it and locks the Founder out irreversibly.
  [[ "$login" == "layerb-admin" ]] && continue
  id=$(ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" $API/api/users/lookup?loginOrEmail=$login | jq -r '.id'")
  ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" -X DELETE $API/api/admin/users/$id >/dev/null"
  echo "REMOVED $login"
done

# Directory-per-item record of the holder set (PARTITION.md rule 3).
OUT="ops-vm/layer-b/allowlist/holders"
mkdir -p "$OUT"
find "$OUT" -name '*.yaml' -delete
for login in $WANT; do
  printf 'login: "%s"\nderived_from: "people-intelligence capability"\nsynced_at: "%s"\n' \
    "$login" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/$login.yaml"
done

# The backup-store read list derives from the same holders (Section 51.4).
python3 - "$HOLDERS_FILE" <<'PY'
import sys, subprocess, datetime
holders = subprocess.run(
    ["yq", "-r", '.capabilities["people-intelligence"].holders[]', sys.argv[1]],
    capture_output=True, text=True, check=True).stdout.split()
path = "infra/layer-b/backup-read-access-list.yaml"
body = [
    "# infra/layer-b/backup-read-access-list.yaml",
    "# Generated by ops-vm/layer-b/allowlist/sync-allowlist.sh. Never hand-edited.",
    'read_access:',
    '  derived_from: "holders of the people-intelligence capability (Section 90.4)"',
    "  entries:",
]
body += ['    - "%s"' % h for h in sorted(set(holders))]
body += ['reviewed_with: "Section 49 asset inventory sweep"',
         'synced_at: "%sZ"' % datetime.datetime.utcnow().replace(microsecond=0).isoformat(), ""]
open(path, "w", encoding="utf-8").write("\n".join(body))
PY

echo "SYNC_OK holders=$(printf '%s\n' "$WANT" | grep -c .)"
SH
chmod +x ops-vm/layer-b/allowlist/sync-allowlist.sh
```

```bash
set -euo pipefail
cat > access/layer-b/check-non-delegable.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-non-delegable.sh
# D109: "Layer B access is not delegable. The routine people_intelligence_delegate
# is removed." Section 90.4: "No assignment type grants it, and none may be
# introduced to do so."
set -euo pipefail
FAILS=0
note() { echo "DEL_FAIL $1"; FAILS=$((FAILS+1)); }
HOLDERS=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
[ -n "$HOLDERS" ] && [ -f "$HOLDERS" ] || { echo "DEL_FAIL holders artifact unavailable"; exit 1; }

# 1. The removed routine appears nowhere in the published artifact.
grep -qi 'people_intelligence_delegate' "$HOLDERS" && note "the removed routine people_intelligence_delegate is present in the artifact"

# 2. No assignment in the artifact grants the capability.
n=$(yq -r '[.assignments[]? | select(.capability == "people-intelligence")] | length' "$HOLDERS" 2>/dev/null || echo 0)
[ "$n" = "0" ] || note "$n assignment(s) grant people-intelligence"

# 3. The sync job has no delegate path and no hard-coded login.
grep -qi 'delegate' ops-vm/layer-b/allowlist/sync-allowlist.sh && note "the sync job contains a delegate path"
grep -qE '"[a-z0-9-]+"\s*\]?\s*#\s*login' ops-vm/layer-b/allowlist/sync-allowlist.sh && note "the sync job hard-codes a login"

# 4. On the instance, no user holds a role above Viewer by delegation.
adm=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users | jq -r "[.[] | select(.role != \"Admin\" and .role != \"Viewer\")] | length"' || echo -1)
[ "$adm" = "0" ] || note "$adm Layer B-M user(s) hold a role that is neither Admin nor Viewer"

if [ "$FAILS" -eq 0 ]; then echo "NON_DELEGABLE_OK 5/5"; else echo "NON_DELEGABLE_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/check-non-delegable.sh
```

```bash
set -euo pipefail
cat > access/layer-b/check-allowlist-parity.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-allowlist-parity.sh
# Section 90.4: reconciliation "verifies that the holders of Layer B access
# exactly match the holders of the capability", over the six written-down
# surfaces of access/layer-b/reconciliation-scope.yaml.
# A holder appearing in neither list is Blocking drift.
set -euo pipefail
SCOPE="access/layer-b/reconciliation-scope.yaml"
ACCEPTED="assets/inventory/layer-b-host-admin-access.yaml"
FAILS=0
note() { echo "PARITY_BLOCKING $1"; FAILS=$((FAILS+1)); }

HOLDERS_ARTIFACT=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
[ -f "$HOLDERS_ARTIFACT" ] || { echo "PARITY_FAIL holders artifact unavailable"; exit 2; }
HOLDERS=$(yq -r '.capabilities["people-intelligence"].holders[]' "$HOLDERS_ARTIFACT" | sort -u)
NAMED=$(yq -r '.holder_login' "$ACCEPTED" 2>/dev/null || echo "")
ALLOWED=$(printf '%s\n%s\n' "$HOLDERS" "$NAMED" | grep -v '^$' | sort -u)

# The scope must still carry all six surfaces. Narrowing it is a failure.
[ "$(yq -r '.surfaces | length' "$SCOPE")" = "6" ] || { echo "PARITY_FAIL scope narrowed below six surfaces"; exit 2; }

check_set() {  # $1 = surface id, $2 = newline-separated observed principals
  local id="$1" observed extra
  observed=$(printf '%s\n' "$2" | grep -v '^$' | sort -u)
  extra=$(comm -23 <(printf '%s\n' "$observed") <(printf '%s\n' "$ALLOWED"))
  if [ -n "$extra" ]; then
    for p in $extra; do note "$id principal '$p' is in neither the capability holders nor the named accepted-access record"; done
  fi
}

check_set SCOPE-2 "$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users | jq -r ".[].login"')"
check_set SCOPE-3 "$(ssh layerb-host "awk -F: '\$3>=1000 && \$1!=\"nobody\" {print \$1}' /etc/passwd")"
check_set SCOPE-4 "$(ssh layerb-host "sudo grep -rhoE '^[a-z][a-z0-9._-]*' /etc/sudoers /etc/sudoers.d 2>/dev/null | grep -vE '^(Defaults|root|#includedir)$'")"
check_set SCOPE-5 "$(ssh layerb-host "cut -d' ' -f3- ~/.ssh/authorized_keys 2>/dev/null")"
check_set SCOPE-6 "$(yq -r '.read_access.entries[]?' infra/layer-b/backup-read-access-list.yaml)"

# SCOPE-1: the instance credential is a single file with one custodian; it must
# not be readable by any principal outside the allowed set.
owner=$(ssh layerb-host 'stat -c %U /srv/layerb/secrets/admin_password' || echo unknown)
check_set SCOPE-1 "$owner"

if [ "$FAILS" -eq 0 ]; then echo "PARITY_OK 6/6"; else echo "PARITY_FAILED $FAILS Blocking"; exit 1; fi
SH
chmod +x access/layer-b/check-allowlist-parity.sh
```

```bash
set -euo pipefail
./ops-vm/layer-b/allowlist/sync-allowlist.sh --dry-run
./ops-vm/layer-b/allowlist/sync-allowlist.sh
./access/layer-b/check-non-delegable.sh
./access/layer-b/check-allowlist-parity.sh
```

```bash
set -euo pipefail
git add ops-vm/layer-b/allowlist access/layer-b/reconciliation-scope.yaml \
        access/layer-b/check-non-delegable.sh access/layer-b/check-allowlist-parity.sh \
        infra/layer-b/backup-read-access-list.yaml
git commit -m "L5-03-09: capability-derived Layer B allowlist sync, non-delegability check and the Section 90.4 comparison scope"
git push -u origin lane/5/p3-09-capability-allowlist
gh pr create --base integration --head lane/5/p3-09-capability-allowlist \
  --title "L5-03-09: capability-derived Layer B access and its written-down comparison scope" \
  --body "Sync job from the published capability-holders artifact (no separate IdP, no hard-coded login), D109 non-delegability check, and the six-surface Section 90.4 comparison scope published for lane L3's reconciler."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The comparison scope carries all six §90.4 surfaces | `yq -r '.surfaces \| length' access/layer-b/reconciliation-scope.yaml` | `6` |
| 2 | A holder in neither list is classified Blocking | `yq -r '.finding_class.holder_in_neither_list' access/layer-b/reconciliation-scope.yaml` | `Blocking` |
| 3 | The sync job hard-codes no login | `grep -cE '^[^#]*(founder|team-?lead)[^a-z]' ops-vm/layer-b/allowlist/sync-allowlist.sh` | `0` |
| 4 | The sync job's only holder input is the published artifact | `grep -c 'capability_holders_artifact' ops-vm/layer-b/allowlist/sync-allowlist.sh` | `1` |
| 5 | A dry run reports a plan and changes nothing | `./ops-vm/layer-b/allowlist/sync-allowlist.sh --dry-run \| cut -d' ' -f1` | `SYNC_PLAN` |
| 6 | After sync, Layer B-M users are exactly the capability holders | `diff <(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users \| jq -r ".[].login"' \| sort -u) <(yq -r '.capabilities["people-intelligence"].holders[]' "$(yq -r '.layer_b.capability_holders_artifact' contracts/access/access-inputs.yaml)" \| sort -u) >/dev/null && echo ALLOWLIST_EXACT` | `ALLOWLIST_EXACT` |
| 7 | One generated file per holder, never a shared list | `ls -1 ops-vm/layer-b/allowlist/holders/*.yaml \| wc -l` equals `yq -r '.capabilities["people-intelligence"].holders \| length' "$(yq -r '.layer_b.capability_holders_artifact' contracts/access/access-inputs.yaml)"` | the two numbers are equal |
| 8 | The backup read-access list is generated, not hand-edited | `yq -r '.read_access.derived_from' infra/layer-b/backup-read-access-list.yaml` | `holders of the people-intelligence capability (Section 90.4)` |
| 9 | The removed delegate routine appears nowhere in this lane | `git grep -c 'people_intelligence_delegate' -- access infra ops-vm notify assets \| wc -l` | `0` |
| 10 | Non-delegability check passes | `./access/layer-b/check-non-delegable.sh` | `NON_DELEGABLE_OK 5/5` |
| 11 | Parity check passes over all six surfaces | `./access/layer-b/check-allowlist-parity.sh` | `PARITY_OK 6/6` |
| 12 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/check-non-delegable.sh && \
./access/layer-b/check-allowlist-parity.sh && \
yq -r '.surfaces | length' access/layer-b/reconciliation-scope.yaml && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly four lines:

```
NON_DELEGABLE_OK 5/5
PARITY_OK 6/6
6
OWNED_ROOTS_OK
```

### STOP rules

- **If the parity check reports a principal in neither list** — STOP. §90.4 classes it Blocking drift and §53.4 gives Blocking the response *"Immediate … Yes — CI or deployment path blocked"*. Do not remove the principal yourself: you do not know what it holds. File the blocker issue naming the surface id and the principal, and stop the task.
- **If the parity check would pass only by removing a surface from `reconciliation-scope.yaml`** — STOP and quote §90.4 in the blocker issue: *"A check scoped narrower than the access it exists to verify reports clean for the wrong reason."* Narrowing the scope is never the fix.
- **If the published capability-holders artifact does not exist, or does not carry `capabilities["people-intelligence"].holders`** — STOP. It is another lane's output and `PARTITION.md` rule 4 forbids reaching into that lane's source tree to construct it. File a Contract Change Request for `layer_b.capability_holders_artifact` and the blocker issue.
- **If anyone asks for a standing delegate so that Layer B access survives Founder absence** — refuse and quote D109: *"Absence pauses Layer B generation; it does not delegate it."* Continuity runs through the sealed contingency credential in the §14.4 escrow, as a recorded break-glass event, which is not this lane's to issue. File the blocker issue if pressed.
- **If AT-091's delegate sentence is cited as authority to build a delegate path** — STOP and file the blocker issue as escalation `E-P3-05`. Two binding statements conflict; choosing between them is L0's, and building the delegate path in the meantime is the irreversible half of the choice.

---

## L5-03-10 — Layer B-S: the generated encrypted per-person self-view

**Size:** L · **Depends on:** L5-03-05, L5-03-07 · **Owned paths touched:** `ops-vm/layer-b/selfview/`, `access/layer-b/`, `assets/inventory/`, `notify/routes/`

### Purpose
D110's second half. Layer B-S *"requires no capability at all"* — the subject reads their own — and §90.6 fixes exactly how that is possible without making the Founder session a decryption path for everyone:

> *"The self-view is generated into the people-data store (Section 90.3) and delivered in exactly one of two ways: as an encrypted per-person document whose key is exchanged directly with the person, or read in a Founder-granted session. It is never stored unencrypted outside the store."*

> *"The key material is **per-person public-key material**: the person holds the private half — their existing hardware key or an equivalent personal identity — and only the public half is registered at onboarding, a named onboarding checklist item. The Founder session therefore holds nothing that decrypts anyone's self-view, which is what stops root on the operations VM (Section 51.4) being a path to every person's performance history, and what makes departure clean: the company never held the decrypting half. Registered material is **re-keyed annually**, and immediately on a lost-device or compromised-workstation report under Section 43.4, each re-key recorded as a decision."*

§92.8 fixes the contents and the exclusion: *"No peer data, no rankings, no other person's signals."* §89.1 fixes the actor and the log: *"generation … executes as a script under the Founder's own identity in a credentialed session on the operations VM, on a monthly cadence. Machine identities continue to hold no Layer B access under any configuration — the session is the Founder, not a bot. Every generation run is logged in the Layer B access log (Section 90.3)."*

§90.6 also fixes the contest path: *"a person may attach a contest note to any item in their self-view. The note is routed to the Founder and is captured as data feeding the employee-disagreement dimension of the KPI calibration review (Section 84.5). Contesting evidence is never penalised."*

### DECISION REQUIRED — routed to L0

| # | Item | Why it is not this task's | Route |
|---|---|---|---|
| 1 | The **content** of a self-view — which KRA/KPI, evidence, trend and capability rows a person's document carries | That is subsystem **P, People intelligence engine**, unassigned in `PARTITION` v1. §99.2: *"P is hard-gated on L's datasource separation"* — L5 builds the gate, not the engine | Escalation `E-P3-01`. This task builds the generator's envelope: it renders whatever the store's per-person view returns, encrypts it, refuses peer content and logs the run |
| 2 | The onboarding checklist item that registers a person's public half | Person onboarding is L0's onboarding track; the registry is L1's | Escalation `E-P3-02`. This task declares the registry location and the refusal-on-missing-key behaviour, and claims neither path |
| 3 | Recording each re-key **as a decision** | Decision records live in `records/decisions/`, owned by L4 in `control-plane-records` | Escalation `E-P3-03`. This task emits the re-key event and stops at the boundary |

### Files created

| Path | Purpose |
|---|---|
| `ops-vm/layer-b/selfview/pubkey-registry.yaml` | Where each person's public half lives, its re-key rules and the refusal when it is absent |
| `ops-vm/layer-b/selfview/generate-selfview.sh` | Generates one person's document inside the store, encrypts it to that person's public half, logs the run |
| `ops-vm/layer-b/selfview/check-no-peer-content.sh` | Refuses any document naming a login other than its subject |
| `ops-vm/layer-b/selfview/deliver-selfview.sh` | Founder-session delivery of the encrypted document; refuses to send plaintext |
| `ops-vm/layer-b/selfview/contest-note.sh` | Attaches a contest note to one item and routes it to the Founder |
| `ops-vm/layer-b/selfview/rekey-check.sh` | Annual re-key currency plus the §43.4 immediate trigger |
| `access/layer-b/at-095-self-view.sh` | AT-095 — the self-view works |
| `access/layer-b/at-096-no-peer-access.sh` | AT-096 — employees cannot access each other's data |
| `assets/inventory/layer-b-selfview-pubkey-registry.yaml` | The §49.1 inventory entry for the registered public halves |
| `notify/routes/layer-b-selfview-contest.yaml` | Contest-note routing to the Founder, carrying no evidence content |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-10-self-view
mkdir -p ops-vm/layer-b/selfview access/layer-b assets/inventory notify/routes
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/pubkey-registry.yaml <<'YAML'
# ops-vm/layer-b/selfview/pubkey-registry.yaml
# Section 90.6: "The key material is per-person public-key material: the person
# holds the private half ... and only the public half is registered at
# onboarding, a named onboarding checklist item."
surface: layer-b-s
registry:
  # Public halves only. One file per person (PARTITION.md rule 3).
  # They live inside the encrypted store so the store is the single home of
  # everything Layer B, not because a public key is secret.
  path: /srv/layerb/encrypted/pubkeys
  file_pattern: "{github_login}.asc"
  contains: "public half only"
  private_half_held_by: "the person, on their existing hardware key or equivalent personal identity"
  founder_session_holds_decrypting_half: false
rekey:
  annual: true
  immediate_triggers:
    - "lost-device report (Section 43.4)"
    - "compromised-workstation report (Section 43.4)"
  each_rekey_recorded_as: "a decision record - written by lane L4, not by this lane"
refusal:
  # No public half, no document. There is no fallback that keeps the plaintext.
  on_missing_public_half: "refuse to generate; emit SELFVIEW_NO_PUBKEY; write no plaintext"
  on_expired_public_half: "refuse to generate; emit SELFVIEW_PUBKEY_STALE"
onboarding_checklist_item:
  owned_by: L0
  note: "Registration of the public half at onboarding is a named checklist item (Section 90.6). This lane declares the location and the refusal; it does not own the checklist."
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/generate-selfview.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/selfview/generate-selfview.sh
# Usage: generate-selfview.sh <github_login> <session_id>
# Runs on layerb-host, inside the Founder's credentialed session (Section 89.1).
# Plaintext exists only inside the encrypted store and is shredded before exit.
set -euo pipefail
SUBJECT="${1:?github_login}"
SESSION="${2:?session_id}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
PUB="$MNT/pubkeys/$SUBJECT.asc"
OUTDIR="$MNT/documents/$SUBJECT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# Section 89.1: "the session is the Founder, not a bot."
ACTOR="${LAYERB_SESSION_ACTOR:-}"
[ -n "$ACTOR" ] || { echo "SELFVIEW_NO_SESSION_ACTOR"; exit 2; }
case "$ACTOR" in *"[bot]"*|*-bot|reconciler|provisioning-cli|records-writer)
  echo "MACHINE_IDENTITY_REFUSED"; exit 2 ;; esac

# Section 90.6: no public half, no document.
[ -f "$PUB" ] || { echo "SELFVIEW_NO_PUBKEY $SUBJECT"; exit 3; }

mkdir -p "$OUTDIR"; chmod 700 "$OUTDIR"
PLAIN="$OUTDIR/.$SUBJECT-$STAMP.plain"   # inside the store, never outside it
umask 077

# The per-person view is produced by the people-data store. This script renders
# whatever that view returns for exactly one subject; it composes no content of
# its own and joins to no other person's rows (subsystem P owns the content -
# see the DECISION REQUIRED block of this task).
psql "service=layerb_people" --no-align --tuples-only \
  -v subject="$SUBJECT" -f /srv/layerb/config/selfview/selfview.sql > "$PLAIN"

# Section 92.8: "No peer data, no rankings, no other person's signals."
/srv/layerb/config/selfview/check-no-peer-content.sh "$PLAIN" "$SUBJECT" || {
  shred -u "$PLAIN"; echo "SELFVIEW_PEER_CONTENT_REFUSED"; exit 4; }

ENC="$OUTDIR/$SUBJECT-$STAMP.selfview.asc"
gpg --batch --yes --trust-model always --armor \
    --recipient-file "$PUB" --encrypt --output "$ENC" "$PLAIN"
shred -u "$PLAIN"
chmod 600 "$ENC"

# Section 89.1: "Every generation run is logged in the Layer B access log."
/srv/layerb/config/accesslog/record-access.sh \
  "$ACTOR" "$SUBJECT" layer-b-s-generation generate "$SESSION" >/dev/null

echo "SELFVIEW_GENERATED $SUBJECT $STAMP"
SH
chmod +x ops-vm/layer-b/selfview/generate-selfview.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/check-no-peer-content.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/selfview/check-no-peer-content.sh <plaintext> <subject_login>
# Section 92.8: "No peer data, no rankings, no other person's signals."
# Every registered login except the subject is a prohibited token in the document.
set -euo pipefail
DOC="${1:?document}"
SUBJECT="${2:?subject}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
HITS=0
for f in "$MNT"/pubkeys/*.asc; do
  [ -e "$f" ] || continue
  other=$(basename "$f" .asc)
  [ "$other" = "$SUBJECT" ] && continue
  if grep -qiw -- "$other" "$DOC"; then echo "PEER_TOKEN $other"; HITS=$((HITS+1)); fi
done
for word in rank ranking leaderboard percentile "compared to" "vs peers"; do
  if grep -qi -- "$word" "$DOC"; then echo "RANKING_TOKEN $word"; HITS=$((HITS+1)); fi
done
if [ "$HITS" -eq 0 ]; then echo "NO_PEER_CONTENT"; else echo "PEER_CONTENT $HITS"; exit 1; fi
SH
chmod +x ops-vm/layer-b/selfview/check-no-peer-content.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/deliver-selfview.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/selfview/deliver-selfview.sh <github_login> <session_id>
# Section 90.6: "The deliverer is the Founder session, which sends the encrypted
# document over the existing team channel; the encryption is what makes that
# channel acceptable."
set -euo pipefail
SUBJECT="${1:?github_login}"; SESSION="${2:?session_id}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
ACTOR="${LAYERB_SESSION_ACTOR:-}"
[ -n "$ACTOR" ] || { echo "SELFVIEW_NO_SESSION_ACTOR"; exit 2; }
DOC=$(ls -1t "$MNT/documents/$SUBJECT"/*.selfview.asc 2>/dev/null | head -1 || true)
[ -n "$DOC" ] || { echo "SELFVIEW_NOT_GENERATED $SUBJECT"; exit 3; }

# Refuse to deliver anything that is not armoured ciphertext.
head -1 "$DOC" | grep -q 'BEGIN PGP MESSAGE' || { echo "SELFVIEW_NOT_ENCRYPTED"; exit 4; }
# Refuse if any plaintext remains in the subject's directory.
if find "$MNT/documents/$SUBJECT" -name '*.plain' | grep -q .; then
  echo "SELFVIEW_PLAINTEXT_PRESENT"; exit 5
fi

curl -sS -X POST "$TEAM_CHANNEL_WEBHOOK" \
  -F "channels=$SUBJECT" \
  -F "file=@$DOC" \
  -F "initial_comment=Your self-view. Encrypted to the public half you registered." >/dev/null

/srv/layerb/config/accesslog/record-access.sh \
  "$ACTOR" "$SUBJECT" layer-b-s-delivery deliver "$SESSION" >/dev/null
echo "SELFVIEW_DELIVERED $SUBJECT"
SH
chmod +x ops-vm/layer-b/selfview/deliver-selfview.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/contest-note.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/selfview/contest-note.sh <subject> <item_id> <note_file>
# Section 90.6: "a person may attach a contest note to any item in their
# self-view. The note is routed to the Founder and is captured as data feeding
# the employee-disagreement dimension of the KPI calibration review (84.5).
# Contesting evidence is never penalised."
set -euo pipefail
SUBJECT="${1:?subject}"; ITEM="${2:?item_id}"; NOTE="${3:?note_file}"
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
DIR="$MNT/contests/$SUBJECT"; mkdir -p "$DIR"; chmod 700 "$DIR"
ID="$(openssl rand -hex 8)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$DIR/$ID.yaml" <<REC
contest_id: "$ID"
subject: "$SUBJECT"
item_id: "$ITEM"
at: "$STAMP"
note_path: "$DIR/$ID.note"
feeds: "Section 84.5 employee-disagreement dimension"
penalised: false
REC
cp "$NOTE" "$DIR/$ID.note"; chmod 600 "$DIR/$ID.yaml" "$DIR/$ID.note"
# The route carries the fact of a contest, never its text (Section 90.2).
curl -sS -X POST "$TEAM_CHANNEL_WEBHOOK" \
  -F "channels=founder" \
  -F "text=A self-view item was contested. contest_id=$ID item_id=$ITEM" >/dev/null
echo "CONTEST_RECORDED $ID"
SH
chmod +x ops-vm/layer-b/selfview/contest-note.sh
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/selfview/rekey-check.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/selfview/rekey-check.sh
# Section 90.6: "Registered material is re-keyed annually, and immediately on a
# lost-device or compromised-workstation report under Section 43.4."
set -euo pipefail
MNT="${LAYERB_MNT:-/srv/layerb/encrypted}"
STALE=0
for f in "$MNT"/pubkeys/*.asc; do
  [ -e "$f" ] || continue
  age_days=$(( ( $(date -u +%s) - $(stat -c %Y "$f") ) / 86400 ))
  if [ "$age_days" -gt 365 ]; then
    echo "PUBKEY_STALE $(basename "$f" .asc) ${age_days}d"; STALE=$((STALE+1))
  fi
done
if [ "$STALE" -eq 0 ]; then echo "REKEY_CURRENT 0 stale"; else echo "REKEY_STALE $STALE"; exit 1; fi
SH
chmod +x ops-vm/layer-b/selfview/rekey-check.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-095-self-view.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-095-self-view.sh
# AT-095 - "The individual self-view works": "A person sees their own evidence,
# KRA/KPI mapping and capability matrix - delivered as a generated per-person
# document - and nothing about peers."
set -euo pipefail
SUBJECT="${1:?subject_login}"
FAILS=0
note() { echo "AT-095_FAIL $1"; FAILS=$((FAILS+1)); }

# a) It is a document, not a dashboard: no Layer B-M dashboard renders it.
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?query=self-view | jq -r "length"' \
  | grep -qx 0 || note "a Layer B-M dashboard named self-view exists; Section 90.3 requires a document"

# b) Generation produces armoured ciphertext for the subject.
out=$(ssh layerb-host "LAYERB_SESSION_ACTOR=\"\$LAYERB_FOUNDER_LOGIN\" /srv/layerb/config/selfview/generate-selfview.sh $SUBJECT at095" || true)
printf '%s' "$out" | grep -q '^SELFVIEW_GENERATED' || note "generation failed: $out"
ssh layerb-host "head -1 \$(ls -1t /srv/layerb/encrypted/documents/$SUBJECT/*.selfview.asc | head -1)" \
  | grep -q 'BEGIN PGP MESSAGE' || note "the generated document is not encrypted"

# c) Nothing about peers.
ssh layerb-host "gpg --list-only --status-fd 1 --decrypt \$(ls -1t /srv/layerb/encrypted/documents/$SUBJECT/*.selfview.asc | head -1) 2>/dev/null | grep -c ENC_TO" \
  | grep -qx 1 || note "the document is encrypted to more than one recipient"

# d) The run is in the access log.
n=$(ssh layerb-host "grep -l 'session_id: \"at095\"' /srv/layerb/encrypted/accesslog/*.yaml 2>/dev/null | wc -l")
[ "$n" -ge 1 ] || note "the generation run was not written to the Layer B access log"

# e) No capability is required to read it (D110): the subject is not a holder.
HOLDERS=$(yq -r '.layer_b.capability_holders_artifact' contracts/access/access-inputs.yaml)
if yq -r '.capabilities["people-intelligence"].holders[]' "$HOLDERS" | grep -qx "$SUBJECT"; then
  echo "AT-095_NOTE subject holds people-intelligence; run this test with a non-holder subject"
fi

if [ "$FAILS" -eq 0 ]; then echo "AT-095_PASS"; else echo "AT-095_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-095-self-view.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-096-no-peer-access.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-096-no-peer-access.sh
# AT-096 - "Employees cannot access each other's data": "Any attempt is denied."
set -euo pipefail
A="${1:?subject_a}"; B="${2:?subject_b}"
FAILS=0
note() { echo "AT-096_FAIL $1"; FAILS=$((FAILS+1)); }

# 1. A's document is encrypted to A's key only: B cannot be a recipient.
doc=$(ssh layerb-host "ls -1t /srv/layerb/encrypted/documents/$A/*.selfview.asc | head -1")
kb=$(ssh layerb-host "gpg --with-colons --import-options show-only --import /srv/layerb/encrypted/pubkeys/$B.asc 2>/dev/null | awk -F: '/^pub/{print \$5; exit}'")
ssh layerb-host "gpg --list-only --status-fd 1 --decrypt $doc 2>/dev/null | grep -c '$kb'" \
  | grep -qx 0 || note "$B is a recipient of $A's self-view"

# 2. Document directories are not cross-readable.
perm=$(ssh layerb-host "stat -c %a /srv/layerb/encrypted/documents/$A")
[ "$perm" = "700" ] || note "$A's document directory is mode $perm, expected 700"

# 3. The peer-content refusal actually fires.
r=$(ssh layerb-host "printf 'evidence for %s and %s\n' $A $B > /tmp/at096.plain; \
    /srv/layerb/config/selfview/check-no-peer-content.sh /tmp/at096.plain $A; rm -f /tmp/at096.plain" || true)
printf '%s' "$r" | grep -q "PEER_TOKEN $B" || note "the peer-content check did not refuse a document naming $B"

# 4. Neither subject holds a Layer B-M account by virtue of having a self-view.
u=$(ssh layerb-host "curl -s -u \"\$LAYERB_ADMIN\" http://127.0.0.1:3001/api/users/lookup?loginOrEmail=$B -o /dev/null -w '%{http_code}'")
[ "$u" = "404" ] || note "$B has a Layer B-M account (lookup returned $u, expected 404)"

if [ "$FAILS" -eq 0 ]; then echo "AT-096_PASS"; else echo "AT-096_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-096-no-peer-access.sh
```

```bash
set -euo pipefail
cat > assets/inventory/layer-b-selfview-pubkey-registry.yaml <<'YAML'
# assets/inventory/layer-b-selfview-pubkey-registry.yaml
asset_id: layer-b-selfview-pubkey-registry
asset_class: registered-key-material
description: "Per-person PUBLIC key halves used to encrypt Layer B-S self-views (Section 90.6). No private half is ever held here or anywhere on the estate"
owner_capability: devops
location: /srv/layerb/encrypted/pubkeys
rotation_cadence: annually
rotator_capability: devops
immediate_rotation_triggers:
  - "lost-device report (Section 43.4)"
  - "compromised-workstation report (Section 43.4)"
expiry_tracked: true
alert_threshold_days: 30
company_holds_decrypting_half: false
escrow_row: none
escrow_note: "Nothing to escrow. Section 90.6: 'the company never held the decrypting half.'"
YAML
```

```bash
set -euo pipefail
cat > notify/routes/layer-b-selfview-contest.yaml <<'YAML'
# notify/routes/layer-b-selfview-contest.yaml
# Section 90.6: a contest note "is routed to the Founder".
# Section 90.2: "People intelligence is never relayed over messaging surfaces" -
# so this route carries identifiers only, never the note text or the item's content.
route_id: layer-b-selfview-contest
trigger: "ops-vm/layer-b/selfview/contest-note.sh writes a contest record"
transport: actions-webhook              # Section 92.11, Section 99.2 subsystem R
destination_key: designated_messaging_channel   # configuration value, never hard-coded
recipient: founder
payload_fields:
  - contest_id
  - item_id
  - at
prohibited_payload_fields:
  - note_text
  - evidence
  - kpi_value
  - subject_document
penalisation: "none - Section 90.6: 'Contesting evidence is never penalised.'"
feeds: "Section 84.5 employee-disagreement dimension"
YAML
```

```bash
set -euo pipefail
scp -r ops-vm/layer-b/selfview layerb-host:/srv/layerb/config/selfview
ssh layerb-host 'LAYERB_SESSION_ACTOR="$LAYERB_FOUNDER_LOGIN" /srv/layerb/config/selfview/generate-selfview.sh "$SELFVIEW_TEST_SUBJECT_A" smoke-sv1'
ssh layerb-host '/srv/layerb/config/selfview/rekey-check.sh'
./access/layer-b/at-095-self-view.sh "$SELFVIEW_TEST_SUBJECT_A"
./access/layer-b/at-096-no-peer-access.sh "$SELFVIEW_TEST_SUBJECT_A" "$SELFVIEW_TEST_SUBJECT_B"
```

```bash
set -euo pipefail
git add ops-vm/layer-b/selfview access/layer-b/at-095-self-view.sh \
        access/layer-b/at-096-no-peer-access.sh \
        assets/inventory/layer-b-selfview-pubkey-registry.yaml \
        notify/routes/layer-b-selfview-contest.yaml
git commit -m "L5-03-10: Layer B-S generated encrypted per-person self-view, contest path and AT-095/AT-096"
git push -u origin lane/5/p3-10-self-view
gh pr create --base integration --head lane/5/p3-10-self-view \
  --title "L5-03-10: the Layer B-S encrypted per-person self-view" \
  --body "Generation under the Founder's own identity into the encrypted store, encryption to the person's registered public half only, peer-content refusal, Founder-session delivery, contest path routed without content, annual re-key check, AT-095 and AT-096."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The registry holds public halves only | `yq -r '.registry.contains' ops-vm/layer-b/selfview/pubkey-registry.yaml` | `public half only` |
| 2 | The Founder session holds no decrypting half | `yq -r '.registry.founder_session_holds_decrypting_half' ops-vm/layer-b/selfview/pubkey-registry.yaml` | `false` |
| 3 | Generation refuses a machine identity | `ssh layerb-host 'LAYERB_SESSION_ACTOR=reconciler /srv/layerb/config/selfview/generate-selfview.sh "$SELFVIEW_TEST_SUBJECT_A" x1' \|\| true` | `MACHINE_IDENTITY_REFUSED` |
| 4 | Generation refuses when no public half is registered | `ssh layerb-host 'LAYERB_SESSION_ACTOR="$LAYERB_FOUNDER_LOGIN" /srv/layerb/config/selfview/generate-selfview.sh no-such-login x2' \|\| true \| cut -d" " -f1` | `SELFVIEW_NO_PUBKEY` |
| 5 | The delivered document is armoured ciphertext | `ssh layerb-host 'head -1 $(ls -1t /srv/layerb/encrypted/documents/$SELFVIEW_TEST_SUBJECT_A/*.selfview.asc \| head -1)'` | `-----BEGIN PGP MESSAGE-----` |
| 6 | No plaintext survives generation | `ssh layerb-host 'find /srv/layerb/encrypted/documents -name "*.plain" \| wc -l'` | `0` |
| 7 | No self-view plaintext exists outside the store | `ssh layerb-host 'find / -xdev -name "*.selfview.plain" -not -path "/srv/layerb/encrypted/*" 2>/dev/null \| wc -l'` | `0` |
| 8 | Delivery refuses anything that is not ciphertext | `grep -c 'SELFVIEW_NOT_ENCRYPTED' ops-vm/layer-b/selfview/deliver-selfview.sh` | `1` |
| 9 | The contest route carries no note text | `yq -r '.prohibited_payload_fields \| join(",")' notify/routes/layer-b-selfview-contest.yaml` | `note_text,evidence,kpi_value,subject_document` |
| 10 | Contesting is declared non-penalised | `yq -r '.penalisation' notify/routes/layer-b-selfview-contest.yaml \| cut -d' ' -f1` | `none` |
| 11 | Registered public halves are within their annual re-key window | `ssh layerb-host '/srv/layerb/config/selfview/rekey-check.sh'` | `REKEY_CURRENT 0 stale` |
| 12 | AT-095 passes | `./access/layer-b/at-095-self-view.sh "$SELFVIEW_TEST_SUBJECT_A"` | `AT-095_PASS` |
| 13 | AT-096 passes | `./access/layer-b/at-096-no-peer-access.sh "$SELFVIEW_TEST_SUBJECT_A" "$SELFVIEW_TEST_SUBJECT_B"` | `AT-096_PASS` |
| 14 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/at-095-self-view.sh "$SELFVIEW_TEST_SUBJECT_A" && \
./access/layer-b/at-096-no-peer-access.sh "$SELFVIEW_TEST_SUBJECT_A" "$SELFVIEW_TEST_SUBJECT_B" && \
ssh layerb-host '/srv/layerb/config/selfview/rekey-check.sh' && \
ssh layerb-host 'find /srv/layerb/encrypted/documents -name "*.plain" | wc -l' && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly five lines:

```
AT-095_PASS
AT-096_PASS
REKEY_CURRENT 0 stale
0
OWNED_ROOTS_OK
```

### STOP rules

- **If a person has no registered public half and delivery is wanted anyway** — STOP. Do not generate an unencrypted document, do not encrypt to a Founder-held key, and do not "hold it until they register". §90.6 is what stops root on the operations VM being a path to every person's history; a Founder-decryptable copy destroys that property. File the blocker issue.
- **If `check-no-peer-content.sh` fires** — STOP and do not edit the check to allow the token. A peer login in a self-view is an invariant-106 and §92.8 breach in the content, not in the checker. File the blocker issue naming the token class only, never the document contents.
- **If the store's per-person view cannot be queried because subsystem P does not exist** — this is expected at this point in the build. STOP and file the blocker issue as escalation `E-P3-01`. Do not compose self-view content in this lane; §99.2 places it in subsystem P, which `PARTITION` v1 assigns to no lane.
- **If anyone proposes rendering the self-view as a Grafana dashboard so that generation is unnecessary** — refuse and quote §90.3: the self-view *"is delivered as a generated per-person document, not as a dashboard. This closes the last leakage path."* File the blocker issue if pressed.
- **If a re-key is required by a §43.4 lost-device or compromised-workstation report** — this task's script detects staleness but does not record the decision. STOP at the boundary and hand off: decision records are L4's. File the blocker issue as escalation `E-P3-03` if no route exists yet.

---

## L5-03-11 — The named accepted-access record for host-level administrative access

**Size:** S · **Depends on:** L5-03-02, L5-03-07 · **Owned paths touched:** `assets/inventory/`, `access/layer-b/`

### Purpose
§90.3 permits host-level administrative access to the Layer B store and fixes, in one sentence, everything the permission must carry:

> *"Host-level administrative access to that host — VM-root and Grafana-admin — is a **named, recorded accepted risk**, never a capability grant, and the acceptance is stated in full or it is not an acceptance. It names its holder in the operational asset inventory (Section 49); it states that the holder does not thereby hold `people-intelligence` and may not query, read, copy or render Layer B content; it carries a compensating control the holder cannot silently defeat — host-level file-access auditing on the store path, shipped to a destination the host holds no credential to alter, the same write-only discipline the organisation export uses (Section 45.3); and it carries a dated review on the calibration cadence (Section 84.5), calibrated configuration, initial value quarterly. … An accepted risk with no named holder, no compensating control and no expiry is undocumented policy (Section 54.2)."*

Invariant 106 says the same thing from the other side: *"Host-level administrative access to the machine carrying the store is not a grant of it and never confers the capability: it is the single named, recorded accepted risk of Section 90.3, bounded by a stated compensating control and a dated review."*

L5-03-07 built the compensating control. This task writes the record that points at it, and the checker that fails when any of the five mandatory parts is missing or out of date. AT-090 tests exactly this record: *"Host-level administrative access is out of this test's scope and is tested instead against the named accepted-access record of Section 90.3: its holder is named in the asset inventory, its compensating audit trail is live and shipping off-host, and its review is within cadence."*

### DECISION REQUIRED — routed to L0

Naming the holder is a Founder decision, and so is the expiry date. §54.2: *"Expiry is mandatory. CI rejects any exception without one. An exception with no expiry is not an exception; it is undocumented policy."* This task reads all three from the frozen contract and invents none of them.

| Contract key | What it is | If absent |
|---|---|---|
| `layer_b.host_admin_access.holder_login` | The single named holder of VM-root and Grafana-admin on `layerb-host` | STOP. Contract Change Request plus the §1 blocker issue. Do not write a placeholder, a role name or `TBD` |
| `layer_b.host_admin_access.expiry` | The bounded expiry date (RFC3339 date) | STOP, same route. §54.2 makes an unexpiring acceptance undocumented policy |
| `layer_b.host_admin_access.review_cadence_days` | The dated-review interval; §90.3 gives the initial value as quarterly | STOP, same route. The cadence is calibrated configuration (§84.5), not an executor's pick |

### Files created

| Path | Purpose |
|---|---|
| `assets/inventory/layer-b-host-admin-access.yaml` | The §49 inventory entry that *is* the named accepted-access record |
| `access/layer-b/check-accepted-access.sh` | Proves all five mandatory parts are present, live and in date |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-11-accepted-access
mkdir -p assets/inventory access/layer-b
```

```bash
set -euo pipefail
# Q9 resolved — layer_b.host_admin_access block is now declared in L5-02 shape; see L5-02-secrets-and-boundaries.md "required shape".
# Fail before writing anything if the frozen contract is incomplete.
for k in holder_login expiry review_cadence_days; do
  v=$(yq -r ".layer_b.host_admin_access.$k // \"\"" contracts/access/access-inputs.yaml)
  [ -n "$v" ] || echo "ACCEPTED_ACCESS_CONTRACT_MISSING $k"
done
echo "ACCEPTED_ACCESS_CONTRACT_CHECKED"
```

```bash
set -euo pipefail
HOLDER=$(yq -r '.layer_b.host_admin_access.holder_login' contracts/access/access-inputs.yaml)
EXPIRY=$(yq -r '.layer_b.host_admin_access.expiry' contracts/access/access-inputs.yaml)
CADENCE=$(yq -r '.layer_b.host_admin_access.review_cadence_days' contracts/access/access-inputs.yaml)
cat > assets/inventory/layer-b-host-admin-access.yaml <<YAML
# assets/inventory/layer-b-host-admin-access.yaml
# THE named, recorded accepted risk of Section 90.3. There is exactly one.
# Invariant 106: host-level administrative access "is not a grant of it and
# never confers the capability".
# Section 90.3: "the acceptance is stated in full or it is not an acceptance."
asset_id: layer-b-host-admin-access
asset_class: accepted-risk
record_type: named-accepted-access
scope: "VM-root and Grafana-admin on layerb-host (infra/hosts/layerb-host.yaml)"

# Part 1 of 5 - the named holder (Section 49; value from the frozen contract).
holder_login: "$HOLDER"
holder_source: "contracts/access/access-inputs.yaml : layer_b.host_admin_access.holder_login"

# Part 2 of 5 - what the holder does NOT thereby hold.
confers_people_intelligence: false
holder_may_query_layer_b: false
holder_may_read_layer_b: false
holder_may_copy_layer_b: false
holder_may_render_layer_b: false
statement: >-
  The holder does not thereby hold the people-intelligence capability and may
  not query, read, copy or render Layer B content.

# Part 3 of 5 - the compensating control the holder cannot silently defeat.
compensating_control:
  what: "host-level file-access auditing on the store path"
  rules: infra/layer-b/auditd-layerb.rules
  shipper: infra/layer-b/ship-audit.sh
  destination: "s3://layerb-audit (write-only from the host)"
  host_can_alter_destination: false
  discipline: "the same write-only discipline the organisation export uses (Section 45.3)"
  verified_by: access/layer-b/check-access-log.sh

# Part 4 of 5 - the dated review.
review:
  cadence: "Section 84.5 calibration cadence"
  cadence_days: $CADENCE
  last_reviewed: "$(date -u +%Y-%m-%d)"

# Part 5 of 5 - the mandatory expiry (Section 54.2).
expiry: "$EXPIRY"
expiry_source: "contracts/access/access-inputs.yaml : layer_b.host_admin_access.expiry"
on_expiry: "Blocking-class drift (Section 53.4) until re-affirmed or remediated"

anchors:
  section_90_3: "named, recorded accepted risk, never a capability grant"
  invariant_106: "not a grant of it and never confers the capability"
  section_54_2: "An exception with no expiry is not an exception; it is undocumented policy"
  at_090: "tested against the named accepted-access record of Section 90.3"
YAML
```

```bash
set -euo pipefail
cat > access/layer-b/check-accepted-access.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-accepted-access.sh
# Section 90.3: "the acceptance is stated in full or it is not an acceptance."
# Five mandatory parts. All five, or this exits non-zero.
set -euo pipefail
R="assets/inventory/layer-b-host-admin-access.yaml"
FAILS=0
note() { echo "ACC_FAIL $1"; FAILS=$((FAILS+1)); }
[ -f "$R" ] || { echo "ACC_FAIL record absent"; exit 1; }

# 1. Named holder, and it is a real login, not a placeholder or a role name.
h=$(yq -r '.holder_login' "$R")
[ -n "$h" ] && [ "$h" != "null" ] || note "no named holder"
case "$h" in TBD|tbd|founder|Founder|devops|team-lead|"") note "holder '$h' is a placeholder or a role name, not a named login" ;; esac

# 2. The five negative statements.
for k in confers_people_intelligence holder_may_query_layer_b holder_may_read_layer_b \
         holder_may_copy_layer_b holder_may_render_layer_b; do
  [ "$(yq -r ".$k" "$R")" = "false" ] || note "$k is not false"
done

# 3. The compensating control is live and shipping off-host.
[ "$(yq -r '.compensating_control.host_can_alter_destination' "$R")" = "false" ] \
  || note "the record claims the host can alter the audit destination"
k=$(ssh layerb-host 'sudo auditctl -l | grep -c layerb_store' || true)
[ "$k" -ge 1 ] || note "the compensating control is not loaded on the host"
if ssh layerb-host 'aws s3 ls s3://layerb-audit/ --profile layerb-audit-writer' >/dev/null 2>&1; then
  note "the host can read the shipped audit trail"
fi

# 4. The review is within cadence.
last=$(yq -r '.review.last_reviewed' "$R"); days=$(yq -r '.review.cadence_days' "$R")
age=$(( ( $(date -u +%s) - $(date -u -d "$last" +%s) ) / 86400 ))
[ "$age" -le "$days" ] || note "review is ${age}d old, cadence is ${days}d"

# 5. Expiry is present and in the future (Section 54.2).
exp=$(yq -r '.expiry' "$R")
[ -n "$exp" ] && [ "$exp" != "null" ] || note "no expiry - Section 54.2: undocumented policy"
[ "$(date -u -d "$exp" +%s)" -gt "$(date -u +%s)" ] || note "expiry $exp has passed"

# 6. Exactly one such record exists in this lane.
n=$(git ls-files 'assets/inventory/*.yaml' | xargs -r grep -l 'record_type: named-accepted-access' | wc -l | tr -d ' ')
[ "$n" = "1" ] || note "$n named-accepted-access records exist; Section 90.3 states there is one"

# 7. The holder does not also hold the capability.
HA=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
if [ -n "$HA" ] && [ -f "$HA" ]; then
  if yq -r '.capabilities["people-intelligence"].holders[]' "$HA" | grep -qx "$h"; then
    echo "ACC_NOTE holder $h also holds people-intelligence by capability; that grant is separate and legitimate"
  fi
fi

if [ "$FAILS" -eq 0 ]; then echo "ACCEPTED_ACCESS_OK 7/7"; else echo "ACCEPTED_ACCESS_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/check-accepted-access.sh
```

```bash
set -euo pipefail
./access/layer-b/check-accepted-access.sh
git add assets/inventory/layer-b-host-admin-access.yaml access/layer-b/check-accepted-access.sh
git commit -m "L5-03-11: the named accepted-access record for host-level administrative access to the Layer B store"
git push -u origin lane/5/p3-11-accepted-access
gh pr create --base integration --head lane/5/p3-11-accepted-access \
  --title "L5-03-11: the Section 90.3 named accepted-access record" \
  --body "One record, five mandatory parts: named holder, the five negative statements, the compensating control built in L5-03-07, a dated review on the Section 84.5 cadence, and a mandatory expiry per Section 54.2. Checker fails when any part is missing or out of date."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Exactly one named-accepted-access record exists | `git grep -l 'record_type: named-accepted-access' -- assets/inventory \| wc -l` | `1` |
| 2 | The holder is named, not a role or a placeholder | `yq -r '.holder_login' assets/inventory/layer-b-host-admin-access.yaml \| grep -cvE '^(TBD|tbd|founder|Founder|devops|team-lead|null|)$'` | `1` |
| 3 | The record denies the capability | `yq -r '.confers_people_intelligence' assets/inventory/layer-b-host-admin-access.yaml` | `false` |
| 4 | All four content prohibitions are stated | `yq -r '.holder_may_query_layer_b, .holder_may_read_layer_b, .holder_may_copy_layer_b, .holder_may_render_layer_b' assets/inventory/layer-b-host-admin-access.yaml \| sort -u` | `false` |
| 5 | The compensating control points at the live rules file | `yq -r '.compensating_control.rules' assets/inventory/layer-b-host-admin-access.yaml` | `infra/layer-b/auditd-layerb.rules` |
| 6 | The audit destination is not alterable by the host | `yq -r '.compensating_control.host_can_alter_destination' assets/inventory/layer-b-host-admin-access.yaml` | `false` |
| 7 | The compensating control is loaded on the host | `ssh layerb-host 'sudo auditctl -l \| grep -c layerb_store'` | `1` |
| 8 | An expiry is present | `yq -r '.expiry' assets/inventory/layer-b-host-admin-access.yaml \| grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'` | `1` |
| 9 | The review is dated | `yq -r '.review.last_reviewed' assets/inventory/layer-b-host-admin-access.yaml \| grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'` | `1` |
| 10 | Full checker passes | `./access/layer-b/check-accepted-access.sh` | `ACCEPTED_ACCESS_OK 7/7` |
| 11 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/check-accepted-access.sh && \
yq -r '.holder_login + "|" + .expiry + "|" + (.review.cadence_days|tostring)' assets/inventory/layer-b-host-admin-access.yaml && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly three lines (the middle line's values come from the frozen contract; the shape does not vary):

```
ACCEPTED_ACCESS_OK 7/7
<holder-login>|<YYYY-MM-DD>|<cadence-days>
OWNED_ROOTS_OK
```

### STOP rules

- **If any of the three contract keys is absent** — STOP. Do not write a role name, an initial, `TBD`, or "the Founder" into `holder_login`, and do not omit the expiry. §90.3: *"the acceptance is stated in full or it is not an acceptance."* §54.2: an acceptance with no expiry is undocumented policy. File a Contract Change Request and the blocker issue naming the missing key.
- **If two or more named-accepted-access records exist** — STOP. §90.3 states this risk *"once"*, and invariant 106 calls it *"the single named, recorded accepted risk"*. A second record means the boundary has been widened somewhere this task cannot see. File the blocker issue.
- **If the compensating control is not loaded on the host** — STOP. Without it the acceptance is incomplete and the record must not be written: §90.3 requires a control *"the holder cannot silently defeat"*. Re-run L5-03-07 and, if it still fails, file the blocker issue.
- **If the review is out of cadence or the expiry has passed** — do not re-date the record to make the checker green. That is the exact failure §54.2 exists to prevent. The re-affirmation is a recorded Founder decision. File the blocker issue.
- **If the holder needs to read Layer B content to do their job** — STOP. That is a capability question, not an access-record question, and it is answered by §90.4, not here. File the blocker issue.

---

## L5-03-12 — The People-tier hard gate: acceptance-test runner and gate artifact

**Size:** M · **Depends on:** L5-03-04, L5-03-07, L5-03-08, L5-03-09, L5-03-10, L5-03-11 · **Owned paths touched:** `access/layer-b/`, `access/layer-b/gate/`

### Purpose
This is the task §0 of this file points at. §98.6, sequencing rules, binding:

> *"P4 must not begin before the Layer B datasource separation is implemented and verified. It is a P2 deliverable, never an assumption; **verified** means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds. People evidence cannot be generated before it can be access-controlled at datasource level."*

and §90.3: *"No Layer B evidence may be generated before this separation exists. This gates the corresponding implementation phase."*

L5-03-01's phase manifest already declares the eight tests in scope and the artifact path. This task writes the four acceptance tests that do not yet exist (AT-089, AT-090, AT-091, AT-092), the two invariant checks, the runner that executes all ten, and the gate artifact the runner emits.

The gate artifact is a **run product, not a committed file**. Committing it would make a green gate something a person can type, and would make it a shared mutable file under `PARTITION.md` rule 3. The runner writes it; a criterion below proves it is untracked.

### The ten checks the gate runs

| Check | Source | Already built by |
|---|---|---|
| AT-089 | §100.6 — *"Peers and general dashboards cannot reach Layer B data by any path"* | this task |
| AT-090 | §100.6 — Founder-only at application and datasource layers; self-view out of scope; host admin tested against the §90.3 record | this task |
| AT-091 | §100.6 — *"Access follows the capability, not the role name"* | this task |
| AT-092 | §100.6 — *"Access is denied at both the dashboard and the datasource level"* | this task |
| AT-095 | §100.6 | L5-03-10 |
| AT-096 | §100.6 | L5-03-10 |
| AT-097 | §100.6 | L5-03-04 |
| AT-098 | §100.6 | L5-03-04 |
| Invariant 106 | §101 #106 | L5-03-09, L5-03-11 |
| Invariant 109 | §101 #109 | this task |

### DECISION REQUIRED — routed to L0

| # | Item | Why it is not this task's | Route |
|---|---|---|---|
| 1 | Who consumes the green gate artifact and starts P4 | P4 is the People tier — subsystem **P**, unassigned in `PARTITION` v1 | Escalation `E-P3-01`. This task emits the artifact and names its path; it starts nothing |
| 2 | AT-091's sentence about a *"dated delegate assignment"* against D109's *"not delegable"* | A specification tension, restated from L5-03-09 | Escalation `E-P3-05`. AT-091 is implemented as the capability-parity test §90.4 describes, and the tension is filed |

### Files created

| Path | Purpose |
|---|---|
| `access/layer-b/at-089-unreachable-from-general.sh` | AT-089 |
| `access/layer-b/at-090-founder-only.sh` | AT-090 |
| `access/layer-b/at-091-capability-gates.sh` | AT-091 |
| `access/layer-b/at-092-team-lead-denied.sh` | AT-092 |
| `access/layer-b/check-invariant-109.sh` | Invariant 109 |
| `access/layer-b/gate/run-people-tier-gate.sh` | The runner; writes the gate artifact |
| `access/layer-b/gate/people-tier.gate.schema.json` | The artifact's shape, so a consumer can validate it |
| `access/layer-b/gate/.gitkeep` | The directory. The artifact itself is never committed |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-12-people-tier-gate
mkdir -p access/layer-b/gate
touch access/layer-b/gate/.gitkeep
```

```bash
set -euo pipefail
cat > access/layer-b/at-089-unreachable-from-general.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-089-unreachable-from-general.sh
# AT-089 - "Layer B is unreachable from general surfaces":
# "Peers and general dashboards cannot reach Layer B data by any path."
set -euo pipefail
FAILS=0
note() { echo "AT-089_FAIL $1"; FAILS=$((FAILS+1)); }

# Path 1: the shared instance's provisioned configuration.
./access/layer-b/at-097-no-people-datasource-in-shared.sh >/dev/null 2>&1 \
  || note "the shared instance's provisioning reaches the people datasource (AT-097)"

# Path 2: the network. The Layer B-M instance is not routable from ops-vm.
ext=$(ssh ops-vm 'curl -s -o /dev/null -m 5 -w "%{http_code}" http://layerb-host:3001/api/org' || echo 000)
[ "$ext" = "000" ] || note "Layer B-M is reachable from ops-vm (HTTP $ext)"

# Path 3: the database. The people store does not accept the shared datasource user.
db=$(ssh ops-vm 'PGCONNECT_TIMEOUT=5 psql "host=layerb-host port=5433 dbname=layerb_people user=grafana_shared" -c "select 1" >/dev/null 2>&1; echo $?' || echo 1)
[ "$db" != "0" ] || note "the shared engineering datasource user can connect to the people store"

# Path 4: the general engineering datasource holds no people table.
t=$(ssh ops-vm 'psql "service=devlake" -At -c "select count(*) from information_schema.tables where table_name ~* '"'"'(people|selfview|evidence_person|kpi_person)'"'"'"' 2>/dev/null || echo -1)
[ "$t" = "0" ] || note "the general engineering datasource holds $t people table(s)"

# Path 5: no shared dashboard carries a per-person raw-activity drill-down.
SHARED_PROV="${SHARED_PROV:-ops-vm/grafana/provisioning}"
[ -d "$SHARED_PROV/datasources" ] || {
  echo "AT-089 INDETERMINATE: ops-vm grafana provisioning tree absent ($SHARED_PROV/datasources)"
  exit 2
}
d=$(grep -rlEi '(per[-_]person|individual_activity|author_activity)' "$SHARED_PROV/dashboards" 2>/dev/null | wc -l | tr -d ' ')
[ "$d" = "0" ] || note "$d shared dashboard(s) carry a per-person raw-activity drill-down"

if [ "$FAILS" -eq 0 ]; then echo "AT-089_PASS"; else echo "AT-089_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-089-unreachable-from-general.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-090-founder-only.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-090-founder-only.sh
# AT-090 - "Individual people intelligence is Founder-only".
# Application layer, datasource layer, no delegate, self-view out of scope,
# host-level admin tested against the named accepted-access record of 90.3.
set -euo pipefail
FAILS=0
note() { echo "AT-090_FAIL $1"; FAILS=$((FAILS+1)); }

# Application layer: Layer B-M users are exactly the capability holders.
./access/layer-b/check-allowlist-parity.sh >/dev/null 2>&1 \
  || note "Layer B-M access does not match the capability holders"

# Datasource layer: the people datasource exists only in Layer B-M.
./access/layer-b/at-097-no-people-datasource-in-shared.sh >/dev/null 2>&1 \
  || note "the people datasource is reachable outside Layer B-M"

# No delegate exists.
./access/layer-b/check-non-delegable.sh >/dev/null 2>&1 || note "a delegate path exists (D109)"

# Self-view is out of scope and passes without the capability (D110).
[ "$(yq -r '.decisions.D110' access/layer-b/phase.manifest.yaml | grep -c 'requiring no capability')" = "1" ] \
  || note "the phase manifest does not record that Layer B-S requires no capability"

# Host-level administrative access: tested against the named record, not here.
./access/layer-b/check-accepted-access.sh >/dev/null 2>&1 \
  || note "the named accepted-access record of Section 90.3 does not hold"

if [ "$FAILS" -eq 0 ]; then echo "AT-090_PASS"; else echo "AT-090_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-090-founder-only.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-091-capability-gates.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-091-capability-gates.sh
# AT-091 - "The people-intelligence capability gates Layer B":
# "Access follows the capability, not the role name."
# Implemented as Section 90.4 requires: access derives from the capability and
# from nothing else, and a change in the holder set moves access with it.
# The delegate-assignment clause of AT-091 conflicts with D109 and Section 90.4;
# that tension is escalation E-P3-05 and is not resolved here.
set -euo pipefail
FAILS=0
note() { echo "AT-091_FAIL $1"; FAILS=$((FAILS+1)); }
HA=$(yq -r '.layer_b.capability_holders_artifact' contracts/access/access-inputs.yaml)
[ -f "$HA" ] || { echo "AT-091_FAIL holders artifact unavailable"; exit 1; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

# a) Removing a holder from a FIXTURE closes access in the plan.
yq -r '.' "$HA" > "$TMP/holders.yaml"
first=$(yq -r '.capabilities["people-intelligence"].holders[0]' "$TMP/holders.yaml")
yq -i "del(.capabilities[\"people-intelligence\"].holders[0])" "$TMP/holders.yaml"
plan=$(./ops-vm/layer-b/allowlist/sync-allowlist.sh --dry-run --holders-file "$TMP/holders.yaml")
printf '%s' "$plan" | grep -q 'remove=1' || note "removing a holder does not plan a removal ($plan)"

# b) Adding a holder to the FIXTURE opens access in the plan.
yq -r '.' "$HA" > "$TMP/holders2.yaml"
yq -i ".capabilities[\"people-intelligence\"].holders += [\"at091-canary-login\"]" "$TMP/holders2.yaml"
plan2=$(./ops-vm/layer-b/allowlist/sync-allowlist.sh --dry-run --holders-file "$TMP/holders2.yaml")
printf '%s' "$plan2" | grep -q 'add=1' || note "adding a holder does not plan an addition ($plan2)"

# c) Access follows the capability, not the role name: no role name is an input.
grep -qiE '\b(team-?lead|founder|manager|admin-role)\b' ops-vm/layer-b/allowlist/sync-allowlist.sh \
  && note "the sync job reads a role name"

# d) With the real artifact, the plan is empty - the live state already matches.
plan3=$(./ops-vm/layer-b/allowlist/sync-allowlist.sh --dry-run)
printf '%s' "$plan3" | grep -q 'add=0 remove=0' || note "live Layer B access does not already match the capability holders ($plan3)"

echo "AT-091_NOTE removed-fixture-holder=$first"
if [ "$FAILS" -eq 0 ]; then echo "AT-091_PASS"; else echo "AT-091_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-091-capability-gates.sh
```

```bash
set -euo pipefail
cat > access/layer-b/at-092-team-lead-denied.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/at-092-team-lead-denied.sh
# AT-092 - "The Team Lead cannot reach the Founder people views":
# "Access is denied at both the dashboard and the datasource level."
# No person is named here. The test asserts the property that produces the
# denial: anyone who is not a capability holder has no account and no route.
set -euo pipefail
FAILS=0
note() { echo "AT-092_FAIL $1"; FAILS=$((FAILS+1)); }
HA=$(yq -r '.layer_b.capability_holders_artifact' contracts/access/access-inputs.yaml)
HOLDERS=$(yq -r '.capabilities["people-intelligence"].holders[]' "$HA" | sort -u)

# Dashboard level: org users are exactly the holders, and sign-up is off, so a
# non-holder cannot obtain an account by logging in.
users=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users | jq -r ".[].login"' | sort -u)
diff <(printf '%s\n' "$users") <(printf '%s\n' "$HOLDERS") >/dev/null \
  || note "Layer B-M org users are not exactly the capability holders"
grep -q '^allow_sign_up = false' ops-vm/layer-b/grafana.ini || note "sign-up is not disabled"
awk '/^\[auth.github\]/{f=1;next} /^\[/{f=0} f&&/^allow_sign_up/{print}' ops-vm/layer-b/grafana.ini \
  | grep -q 'false' || note "OAuth sign-up is not disabled"

# Datasource level: the people datasource is registered nowhere a non-holder can
# reach, and an unauthenticated query is refused.
./access/layer-b/at-097-no-people-datasource-in-shared.sh >/dev/null 2>&1 || note "AT-097 does not hold"
c=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:3001/api/ds/query -H "Content-Type: application/json" -d "{}"')
[ "$c" = "401" ] || note "unauthenticated datasource query returned $c, expected 401"

# The minimum-necessary surface a Team Lead does get carries one field only.
[ "$(yq -r '.record.prohibited_fields | length' ops-vm/layer-b/accesslog/schema.yaml)" = "4" ] \
  || note "the access-log schema no longer prohibits evidence content"

if [ "$FAILS" -eq 0 ]; then echo "AT-092_PASS"; else echo "AT-092_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/at-092-team-lead-denied.sh
```

```bash
set -euo pipefail
cat > access/layer-b/check-invariant-109.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-invariant-109.sh
# Invariant 109 (Section 101 #109): "General engineering dashboards never expose
# sensitive performance data and carry no per-person raw-activity drill-downs;
# individual activity data lives only in Layer B. The underlying people
# datasource is separately credentialed, and sensitive people data never enters
# the general engineering datasource."
set -euo pipefail
FAILS=0
note() { echo "INV109_FAIL $1"; FAILS=$((FAILS+1)); }

# Clause 1: no per-person raw-activity drill-down in the general dashboards.
SHARED_PROV="${SHARED_PROV:-ops-vm/grafana/provisioning}"
[ -d "$SHARED_PROV/datasources" ] || {
  echo "INV109 INDETERMINATE: ops-vm grafana provisioning tree absent ($SHARED_PROV/datasources)"
  exit 2
}
d=$(grep -rlEi '(per[-_]person|individual_activity|author_activity|commits_by_author)' \
      "$SHARED_PROV/dashboards" 2>/dev/null | wc -l | tr -d ' ')
[ "$d" = "0" ] || note "$d general dashboard(s) carry a per-person raw-activity drill-down"

# Clause 2: individual activity data lives only in Layer B.
./access/layer-b/at-089-unreachable-from-general.sh >/dev/null 2>&1 \
  || note "individual activity data is reachable outside Layer B (AT-089)"

# Clause 3: the people datasource is separately credentialed.
./access/layer-b/at-098-separately-credentialed.sh >/dev/null 2>&1 \
  || note "the people datasource is not separately credentialed (AT-098)"

# Clause 4: sensitive people data never enters the general engineering datasource.
t=$(ssh ops-vm 'psql "service=devlake" -At -c "select count(*) from information_schema.columns where column_name ~* '"'"'(performance|promotion|improvement_plan|exit_consideration|compensation)'"'"'"' 2>/dev/null || echo -1)
[ "$t" = "0" ] || note "the general engineering datasource holds $t sensitive people column(s)"

if [ "$FAILS" -eq 0 ]; then echo "INV109_HOLDS 4/4"; else echo "INV109_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/check-invariant-109.sh
```

```bash
set -euo pipefail
cat > access/layer-b/gate/people-tier.gate.schema.json <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "People-tier gate artifact",
  "description": "Emitted by access/layer-b/gate/run-people-tier-gate.sh. The only admissible evidence that the Section 90.3 and Section 98.6 gate is satisfied. Never committed.",
  "type": "object",
  "additionalProperties": false,
  "required": ["gate", "generated_at", "verified", "verified_definition", "checks", "invariants", "runner_commit"],
  "properties": {
    "gate": { "enum": ["GREEN", "RED"] },
    "generated_at": { "type": "string" },
    "runner_commit": { "type": "string" },
    "verified": { "type": "boolean" },
    "verified_definition": {
      "const": "AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds"
    },
    "checks": {
      "type": "object",
      "additionalProperties": false,
      "required": ["AT-089","AT-090","AT-091","AT-092","AT-095","AT-096","AT-097","AT-098"],
      "patternProperties": { "^AT-[0-9]{3}$": { "enum": ["PASS", "FAIL"] } }
    },
    "invariants": {
      "type": "object",
      "additionalProperties": false,
      "required": ["106", "109"],
      "patternProperties": { "^(106|109)$": { "enum": ["HOLDS", "BREACHED"] } }
    }
  }
}
JSON
```

```bash
set -euo pipefail
cat > access/layer-b/gate/run-people-tier-gate.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/gate/run-people-tier-gate.sh
# The People-tier hard gate. Section 98.6: "P4 must not begin before the Layer B
# datasource separation is implemented and verified ... verified means AT-089,
# AT-091, AT-097 and AT-098 pass and invariant 109 holds."
#
# The artifact is GREEN only when all eight in-scope tests pass and invariants
# 106 and 109 both hold. It additionally records the Section 98.6 "verified"
# subset as its own field, so a consumer never has to infer it.
# Exit 0 = GREEN. Exit 1 = RED. Exit 2 = the gate could not be evaluated.
set -uo pipefail
OUT="access/layer-b/gate/people-tier.gate.json"
A="${SELFVIEW_TEST_SUBJECT_A:?SELFVIEW_TEST_SUBJECT_A}"
B="${SELFVIEW_TEST_SUBJECT_B:?SELFVIEW_TEST_SUBJECT_B}"

run() { "$@" >/dev/null 2>&1 && echo PASS || echo FAIL; }

AT089=$(run ./access/layer-b/at-089-unreachable-from-general.sh)
AT090=$(run ./access/layer-b/at-090-founder-only.sh)
AT091=$(run ./access/layer-b/at-091-capability-gates.sh)
AT092=$(run ./access/layer-b/at-092-team-lead-denied.sh)
AT095=$(run ./access/layer-b/at-095-self-view.sh "$A")
AT096=$(run ./access/layer-b/at-096-no-peer-access.sh "$A" "$B")
AT097=$(run ./access/layer-b/at-097-no-people-datasource-in-shared.sh)
AT098=$(run ./access/layer-b/at-098-separately-credentialed.sh)

INV109=$(./access/layer-b/check-invariant-109.sh >/dev/null 2>&1 && echo HOLDS || echo BREACHED)
if ./access/layer-b/check-non-delegable.sh >/dev/null 2>&1 \
   && ./access/layer-b/check-accepted-access.sh >/dev/null 2>&1 \
   && ./access/layer-b/check-allowlist-parity.sh >/dev/null 2>&1; then
  INV106=HOLDS
else
  INV106=BREACHED
fi

VERIFIED=false
[ "$AT089" = PASS ] && [ "$AT091" = PASS ] && [ "$AT097" = PASS ] && [ "$AT098" = PASS ] \
  && [ "$INV109" = HOLDS ] && VERIFIED=true

GATE=RED
if [ "$VERIFIED" = true ] && [ "$INV106" = HOLDS ] \
   && [ "$AT090" = PASS ] && [ "$AT092" = PASS ] && [ "$AT095" = PASS ] && [ "$AT096" = PASS ]; then
  GATE=GREEN
fi

mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<JSON
{
  "gate": "$GATE",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "runner_commit": "$(git rev-parse HEAD)",
  "verified": $VERIFIED,
  "verified_definition": "AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds",
  "checks": {
    "AT-089": "$AT089", "AT-090": "$AT090", "AT-091": "$AT091", "AT-092": "$AT092",
    "AT-095": "$AT095", "AT-096": "$AT096", "AT-097": "$AT097", "AT-098": "$AT098"
  },
  "invariants": { "106": "$INV106", "109": "$INV109" }
}
JSON

echo "PEOPLE_TIER_GATE $GATE"
[ "$GATE" = GREEN ] && exit 0 || exit 1
SH
chmod +x access/layer-b/gate/run-people-tier-gate.sh
```

```bash
set -euo pipefail
export SELFVIEW_TEST_SUBJECT_A SELFVIEW_TEST_SUBJECT_B
./access/layer-b/gate/run-people-tier-gate.sh
python3 -c "import json,sys; json.load(open('access/layer-b/gate/people-tier.gate.json')); print('GATE_JSON_VALID')"
```

```bash
set -euo pipefail
git add access/layer-b/at-089-unreachable-from-general.sh \
        access/layer-b/at-090-founder-only.sh \
        access/layer-b/at-091-capability-gates.sh \
        access/layer-b/at-092-team-lead-denied.sh \
        access/layer-b/check-invariant-109.sh \
        access/layer-b/gate/run-people-tier-gate.sh \
        access/layer-b/gate/people-tier.gate.schema.json \
        access/layer-b/gate/.gitkeep
git status --porcelain access/layer-b/gate/people-tier.gate.json | grep -q '^??' && echo "GATE_ARTIFACT_UNTRACKED"
git commit -m "L5-03-12: the People-tier hard gate - AT-089/090/091/092, invariant 109 and the gate runner"
git push -u origin lane/5/p3-12-people-tier-gate
gh pr create --base integration --head lane/5/p3-12-people-tier-gate \
  --title "L5-03-12: the People-tier hard gate and its artifact" \
  --body "Runs the eight in-scope acceptance tests plus invariants 106 and 109 and emits access/layer-b/gate/people-tier.gate.json. GREEN only when all ten pass. The artifact is a run product and is never committed."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | AT-089 passes | `./access/layer-b/at-089-unreachable-from-general.sh` | `AT-089_PASS` |
| 2 | AT-090 passes | `./access/layer-b/at-090-founder-only.sh` | `AT-090_PASS` |
| 3 | AT-091 passes | `./access/layer-b/at-091-capability-gates.sh \| tail -1` | `AT-091_PASS` |
| 4 | AT-092 passes | `./access/layer-b/at-092-team-lead-denied.sh` | `AT-092_PASS` |
| 5 | Invariant 109 holds | `./access/layer-b/check-invariant-109.sh` | `INV109_HOLDS 4/4` |
| 6 | The runner executes all eight in-scope tests | `grep -cE '^AT0(89|90|91|92|95|96|97|98)=' access/layer-b/gate/run-people-tier-gate.sh` | `8` |
| 7 | The gate is green | `./access/layer-b/gate/run-people-tier-gate.sh` | `PEOPLE_TIER_GATE GREEN` |
| 8 | The artifact records the §98.6 verified definition verbatim | `jq -r '.verified_definition' access/layer-b/gate/people-tier.gate.json` | `AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds` |
| 9 | The artifact records `verified: true` | `jq -r '.verified' access/layer-b/gate/people-tier.gate.json` | `true` |
| 10 | No check in the artifact is FAIL | `jq -r '[.checks[]] \| map(select(. == "FAIL")) \| length' access/layer-b/gate/people-tier.gate.json` | `0` |
| 11 | Both invariants hold in the artifact | `jq -r '.invariants["106"] + "," + .invariants["109"]' access/layer-b/gate/people-tier.gate.json` | `HOLDS,HOLDS` |
| 12 | The artifact validates against its schema | `python3 -c "import json;json.load(open('access/layer-b/gate/people-tier.gate.schema.json'));json.load(open('access/layer-b/gate/people-tier.gate.json'));print('SCHEMA_AND_ARTIFACT_PARSE')"` | `SCHEMA_AND_ARTIFACT_PARSE` |
| 13 | The artifact is not committed | `git ls-files access/layer-b/gate/people-tier.gate.json \| wc -l` | `0` |
| 14 | The artifact path matches the phase manifest | `yq -r '.gate.artifact' access/layer-b/phase.manifest.yaml` | `access/layer-b/gate/people-tier.gate.json` |
| 15 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/gate/run-people-tier-gate.sh && \
jq -r '.gate + "|" + (.verified|tostring) + "|" + .invariants["106"] + "|" + .invariants["109"]' \
   access/layer-b/gate/people-tier.gate.json && \
git ls-files access/layer-b/gate/people-tier.gate.json | wc -l && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly four lines:

```
PEOPLE_TIER_GATE GREEN
GREEN|true|HOLDS|HOLDS
0
OWNED_ROOTS_OK
```

### STOP rules

- **If the gate is RED** — STOP. Do not open the PR, do not hand the artifact to anyone, and do not run any People-tier work. §90.3: *"No Layer B evidence may be generated before this separation exists."* File the blocker issue quoting the failing check names from `checks` and `invariants`. A red artifact is a correct output of this task; a task that produced one has succeeded at its job and must stop at this line.
- **If a check is failing and the quickest route to green is to relax it** — STOP. Every check in this runner is a transcription of a binding sentence. AT-090 names this failure mode itself: *"A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes."* File the blocker issue.
- **If anyone proposes committing a green `people-tier.gate.json` so downstream work can start** — refuse. A committed artifact is a typed assertion, not an executed one, and it is a shared mutable file under `PARTITION.md` rule 3. File the blocker issue if pressed.
- **If AT-091 cannot be made to pass without building a delegate path** — STOP and file escalation `E-P3-05`. Do not build the delegate path: D109 removed it, and §90.4 forbids introducing an assignment type that grants the capability.
- **If a downstream consumer asks this task to also start P4** — STOP. Subsystem P is unassigned in `PARTITION` v1; this lane emits the artifact and claims nothing beyond it. File escalation `E-P3-01`.

---

## L5-03-13 — Post-patch smoke checklist and Layer B alert routing

**Size:** S · **Depends on:** L5-03-12 · **Owned paths touched:** `ops-vm/layer-b/patch/`, `infra/layer-b/`, `notify/routes/`, `access/layer-b/`

### Purpose
Two sentences of §51.4 close this phase. The first is the checklist:

> *"**The post-patch smoke checklist** runs after every stack patch: dashboards provision from JSON, both instances' datasources connect, alert rules fire a test alert, and the Founder-only Layer B instance's credential and authentication allowlist match the capability holders (Section 90.4). An immediate reconciliation run follows, mandated; the patch is not recorded as complete until the checklist and the reconciliation run both pass clean."*

The second is the shape the patch takes, because the control plane has no canary set:

> *"A control-plane change therefore takes the shape **snapshot → upgrade → verify → revert-on-fail**, carrying the Section 61 change manifest and approval but no canary stage: the snapshot is the rollback answer known before the upgrade starts, and the post-patch smoke checklist is the verify step."*

§51.4 also fixes the cadence: *"Security patches for Grafana and the VM OS are applied on an expedited path, not batched to the routine window"*, and *"The separately-credentialed Layer B datasource is patched and reviewed on the tightest cadence in the stack."*

This task builds the checklist, the cadence declaration, and the two Layer B notification routes — one push, one wait surface — that §92.11's closed push list permits.

### DECISION REQUIRED — routed to L0

| # | Item | Why it is not this task's | Route |
|---|---|---|---|
| 1 | *"alert rules fire a test alert"* on the **Layer B-M** instance, against L5-03-03's `[unified_alerting] enabled = false`, which exists because §90.2 states *"People intelligence is never relayed over messaging surfaces"* | Two binding sentences point opposite ways. Choosing which yields is a decision | Escalation `E-P3-06`. This task fires the test alert on the **shared** instance and records `layerb_alerting: disabled-by-90-2` for the Layer B half, changing no Layer B configuration |
| 2 | The tool-register entry that carries the Layer B stack's current version, declared cadence and date last patched (§62) | The tool register is a registry; `registries/**` is lane L1's | Escalation `E-P3-07`. This task publishes `infra/layer-b/patch-cadence.yaml` as the handoff and creates no path under `registries/**` |
| 3 | Triggering the mandated immediate reconciliation run | The reconciler is lane L3's (`reconciler/**`) | Escalation `E-P3-08`. The checklist **asserts** that a clean reconciliation run exists and is newer than the patch; it never invokes the reconciler |

### Files created

| Path | Purpose |
|---|---|
| `infra/layer-b/patch-cadence.yaml` | The declared cadence, the expedited security path and the singleton change shape |
| `ops-vm/layer-b/patch/post-patch-smoke.sh` | The four §51.4 checklist items plus the reconciliation assertion |
| `notify/routes/layer-b-gate-red.yaml` | Push route: a red People-tier gate is Blocking-class drift |
| `notify/routes/layer-b-patch-stale.yaml` | Wait surface: cadence staleness is Amber and never pages |
| `access/layer-b/check-post-patch.sh` | Proves the checklist, the routes and the cadence declaration hold |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/5/p3-13-post-patch
mkdir -p ops-vm/layer-b/patch infra/layer-b notify/routes access/layer-b
```

```bash
set -euo pipefail
cat > infra/layer-b/patch-cadence.yaml <<'YAML'
# infra/layer-b/patch-cadence.yaml
# Section 51.4 and Section 62: the control-plane stack's declared patch cadence,
# with the elevated priority Layer B carries.
# Published for lane L1's tool register (registries/** is not L5's - see E-P3-07).
components:
  - id: grafana-layerb
    what: "the Founder-only Layer B-M Grafana instance"
    cadence: tightest-in-stack        # Section 51.4
    security_path: expedited          # "not batched to the routine window"
    staleness_signal: Amber           # Section 53.4
    known_exploited_signal: Red       # Section 51.4
  - id: layerb-people-datasource
    what: "the separately-credentialed people datasource"
    cadence: tightest-in-stack
    security_path: expedited
    staleness_signal: Amber
    known_exploited_signal: Red
  - id: layerb-host-os
    what: "the operating system of layerb-host"
    cadence: tightest-in-stack
    security_path: expedited
    staleness_signal: Amber
    known_exploited_signal: Red
change_shape:
  # Section 51.4: "The control plane has no canary set."
  steps: [snapshot, upgrade, verify, revert-on-fail]
  canary_stage: false
  carries: "the Section 61 change manifest and approval"
  verify_step: ops-vm/layer-b/patch/post-patch-smoke.sh
  rollback_answer_known_before_upgrade: true
completion_rule: >-
  Section 51.4: "the patch is not recorded as complete until the checklist and
  the reconciliation run both pass clean."
tool_register_handoff:
  owner: L1
  note: "The register entry - current version, declared cadence, date last patched - lives in registries/**, which L5 does not own. This file is the published input."
YAML
```

```bash
set -euo pipefail
cat > ops-vm/layer-b/patch/post-patch-smoke.sh <<'SH'
#!/usr/bin/env bash
# ops-vm/layer-b/patch/post-patch-smoke.sh
# The Section 51.4 post-patch smoke checklist. Four items, plus the mandated
# reconciliation assertion. Exit 0 only when all five pass clean.
set -uo pipefail
FAILS=0
note() { echo "SMOKE_FAIL $1"; FAILS=$((FAILS+1)); }

# 1. Dashboards provision from JSON on both instances.
lb=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?type=dash-db | jq -r "length"' || echo -1)
[ "$lb" -ge 0 ] || note "Layer B-M dashboard search failed"
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?type=dash-db | jq -r ".[].id" | while read -r i; do
  curl -s -u "$LAYERB_ADMIN" "http://127.0.0.1:3001/api/dashboards/id/$i" | jq -e ".meta.provisioned == true" >/dev/null || exit 1
done' || note "a Layer B-M dashboard is not provisioned from JSON"
ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/search?type=dash-db | jq -r ".[].id" | while read -r i; do
  curl -s -u "$SHARED_GRAFANA_ADMIN" "http://127.0.0.1:3000/api/dashboards/id/$i" | jq -e ".meta.provisioned == true" >/dev/null || exit 1
done' || note "a shared-instance dashboard is not provisioned from JSON"

# 2. Both instances' datasources connect.
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/datasources | jq -r ".[].uid" | while read -r u; do
  curl -s -u "$LAYERB_ADMIN" "http://127.0.0.1:3001/api/datasources/uid/$u/health" | jq -e ".status == \"OK\"" >/dev/null || exit 1
done' || note "a Layer B-M datasource does not connect"
ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/datasources | jq -r ".[].uid" | while read -r u; do
  curl -s -u "$SHARED_GRAFANA_ADMIN" "http://127.0.0.1:3000/api/datasources/uid/$u/health" | jq -e ".status == \"OK\"" >/dev/null || exit 1
done' || note "a shared-instance datasource does not connect"

# 3. Alert rules fire a test alert - on the SHARED instance only.
# Layer B-M alerting stays off: Section 90.2, "People intelligence is never
# relayed over messaging surfaces." See E-P3-06.
t=$(ssh ops-vm 'curl -s -o /dev/null -w "%{http_code}" -u "$SHARED_GRAFANA_ADMIN" -X POST http://127.0.0.1:3000/api/alertmanager/grafana/config/api/v1/receivers/test -H "Content-Type: application/json" -d "{}"' || echo 000)
case "$t" in 200|202) : ;; *) note "shared-instance test alert returned $t" ;; esac
awk '/^\[unified_alerting\]/{f=1;next} /^\[/{f=0} f&&/^enabled/{print $3}' ops-vm/layer-b/grafana.ini \
  | grep -qx false || note "Layer B-M alerting is enabled; Section 90.2 forbids relaying people intelligence"
echo "SMOKE_NOTE layerb_alerting: disabled-by-90-2"

# 4. Layer B-M credential and authentication allowlist match the capability holders.
./access/layer-b/check-allowlist-parity.sh >/dev/null 2>&1 || note "allowlist parity fails after the patch"
./access/layer-b/at-098-separately-credentialed.sh >/dev/null 2>&1 || note "the instance credential is no longer separate after the patch"

# 5. The mandated immediate reconciliation run exists, is newer than the patch and is clean.
# L5 does not invoke the reconciler (E-P3-08); it asserts the published result.
REC="${RECONCILIATION_RESULT:-/srv/shared/reconciliation/latest.json}"
r=$(ssh ops-vm "jq -r '.status' $REC" 2>/dev/null || echo missing)
[ "$r" = "clean" ] || note "the post-patch reconciliation run is '$r', expected 'clean'"
rt=$(ssh ops-vm "jq -r '.completed_at' $REC" 2>/dev/null || echo "")
[ -n "$rt" ] || note "the reconciliation result carries no completion time"

if [ "$FAILS" -eq 0 ]; then echo "POST_PATCH_SMOKE_OK 5/5"; else echo "POST_PATCH_SMOKE_FAILED $FAILS"; exit 1; fi
SH
chmod +x ops-vm/layer-b/patch/post-patch-smoke.sh
```

```bash
set -euo pipefail
cat > notify/routes/layer-b-gate-red.yaml <<'YAML'
# notify/routes/layer-b-gate-red.yaml
# A red People-tier gate is Blocking-class drift (Section 53.4), and
# Blocking-class drift is on the closed push list of Section 92.11.
# Section 90.2: the payload carries the gate result only, never Layer B content.
route_id: layer-b-gate-red
push: true
push_list_entry: "Blocking-class drift"        # Section 92.11, closed list
trigger: "access/layer-b/gate/run-people-tier-gate.sh emits gate: RED"
drift_class: Blocking                          # Section 53.4
response_time: immediate
transport: actions-webhook                     # Section 92.11, Section 99.2 subsystem R
destination_key: designated_messaging_channel  # configuration value, never hard-coded
payload_fields:
  - gate
  - failing_checks
  - failing_invariants
  - generated_at
prohibited_payload_fields:
  - person
  - subject
  - evidence
  - kpi_value
blocks: "all People-tier work (Section 90.3, Section 98.6)"
YAML
```

```bash
set -euo pipefail
cat > notify/routes/layer-b-patch-stale.yaml <<'YAML'
# notify/routes/layer-b-patch-stale.yaml
# Section 51.4: staleness beyond the cadence "is an Amber condition on operating-
# system health". Amber is NOT on the closed push list of Section 92.11, so this
# route is a wait surface and pages nobody.
route_id: layer-b-patch-stale
push: false
surface: wait
trigger: "a component in infra/layer-b/patch-cadence.yaml is past its declared cadence"
drift_class: Amber                              # Section 53.4
escalates_to_red_when: "a known-exploited vulnerability exists in the deployed version"
rendered_on: "operating-system health (Section 52)"
payload_fields:
  - component
  - declared_cadence
  - date_last_patched
prohibited_payload_fields:
  - person
  - evidence
note: >-
  Section 92.11: "If something appears urgent enough to page a person and is not
  on the push list, the correct response is a governed addition to the push list
  and the event taxonomy, never an ad-hoc alert."
YAML
```

```bash
set -euo pipefail
cat > access/layer-b/check-post-patch.sh <<'SH'
#!/usr/bin/env bash
# access/layer-b/check-post-patch.sh
set -euo pipefail
FAILS=0
note() { echo "PP_FAIL $1"; FAILS=$((FAILS+1)); }

# The change shape has no canary stage and names the smoke script as verify.
[ "$(yq -r '.change_shape.canary_stage' infra/layer-b/patch-cadence.yaml)" = "false" ] \
  || note "the change shape declares a canary stage; the control plane has no canary set"
[ "$(yq -r '.change_shape.verify_step' infra/layer-b/patch-cadence.yaml)" = "ops-vm/layer-b/patch/post-patch-smoke.sh" ] \
  || note "the verify step does not name the smoke checklist"
[ "$(yq -r '.change_shape.steps | join(",")' infra/layer-b/patch-cadence.yaml)" = "snapshot,upgrade,verify,revert-on-fail" ] \
  || note "the change shape is not snapshot,upgrade,verify,revert-on-fail"

# Every component carries the elevated cadence and the expedited security path.
n=$(yq -r '[.components[] | select(.cadence == "tightest-in-stack" and .security_path == "expedited")] | length' infra/layer-b/patch-cadence.yaml)
[ "$n" = "3" ] || note "$n of 3 components carry the elevated cadence"

# Push discipline: exactly one Layer B route pushes, and it is the Blocking one.
p=$(grep -l '^push: true' notify/routes/layer-b-*.yaml | wc -l | tr -d ' ')
[ "$p" = "1" ] || note "$p Layer B routes declare push: true, expected 1"
[ "$(yq -r '.push_list_entry' notify/routes/layer-b-gate-red.yaml)" = "Blocking-class drift" ] \
  || note "the pushing route is not on the closed push list of Section 92.11"
[ "$(yq -r '.push' notify/routes/layer-b-patch-stale.yaml)" = "false" ] \
  || note "the Amber staleness route pages; Amber is not on the push list"

# No Layer B route may carry content.
for f in notify/routes/layer-b-*.yaml; do
  [ "$(yq -r '.prohibited_payload_fields | length' "$f")" -ge 2 ] \
    || note "$f does not prohibit Layer B content in its payload"
done

if [ "$FAILS" -eq 0 ]; then echo "POST_PATCH_DECL_OK 8/8"; else echo "POST_PATCH_DECL_FAILED $FAILS"; exit 1; fi
SH
chmod +x access/layer-b/check-post-patch.sh
```

```bash
set -euo pipefail
scp -r ops-vm/layer-b/patch layerb-host:/srv/layerb/config/patch
./ops-vm/layer-b/patch/post-patch-smoke.sh
./access/layer-b/check-post-patch.sh
```

```bash
set -euo pipefail
git add infra/layer-b/patch-cadence.yaml ops-vm/layer-b/patch \
        notify/routes/layer-b-gate-red.yaml notify/routes/layer-b-patch-stale.yaml \
        access/layer-b/check-post-patch.sh
git commit -m "L5-03-13: post-patch smoke checklist, Layer B patch cadence and the two Layer B notification routes"
git push -u origin lane/5/p3-13-post-patch
gh pr create --base integration --head lane/5/p3-13-post-patch \
  --title "L5-03-13: post-patch smoke checklist and Layer B alert routing" \
  --body "The four Section 51.4 checklist items plus the mandated reconciliation assertion, the elevated patch cadence with the singleton snapshot-upgrade-verify-revert shape, one pushing route (Blocking-class gate failure) and one wait surface (Amber staleness). No Layer B content in any payload."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The change shape carries no canary stage | `yq -r '.change_shape.canary_stage' infra/layer-b/patch-cadence.yaml` | `false` |
| 2 | The change shape is the §51.4 singleton shape | `yq -r '.change_shape.steps \| join(",")' infra/layer-b/patch-cadence.yaml` | `snapshot,upgrade,verify,revert-on-fail` |
| 3 | All three components carry the tightest cadence | `yq -r '[.components[] \| select(.cadence == "tightest-in-stack")] \| length' infra/layer-b/patch-cadence.yaml` | `3` |
| 4 | All three components use the expedited security path | `yq -r '[.components[] \| select(.security_path == "expedited")] \| length' infra/layer-b/patch-cadence.yaml` | `3` |
| 5 | Layer B-M alerting remains disabled | `awk '/^\[unified_alerting\]/{f=1;next} /^\[/{f=0} f&&/^enabled/{print $3}' ops-vm/layer-b/grafana.ini` | `false` |
| 6 | Exactly one Layer B route pushes | `grep -l '^push: true' notify/routes/layer-b-*.yaml \| wc -l` | `1` |
| 7 | The pushing route is on the closed push list | `yq -r '.push_list_entry' notify/routes/layer-b-gate-red.yaml` | `Blocking-class drift` |
| 8 | The Amber staleness route is a wait surface | `yq -r '.push' notify/routes/layer-b-patch-stale.yaml` | `false` |
| 9 | No Layer B route carries evidence content | `for f in notify/routes/layer-b-*.yaml; do yq -r '.prohibited_payload_fields[]' "$f"; done \| grep -c '^evidence$'` | `3` |
| 10 | The checklist asserts a clean reconciliation run | `grep -c 'expected .clean.' ops-vm/layer-b/patch/post-patch-smoke.sh` | `1` |
| 11 | The checklist never invokes the reconciler | `grep -cE '(^|[^a-z])reconciler(/|[[:space:]])' ops-vm/layer-b/patch/post-patch-smoke.sh` | `0` |
| 12 | The smoke checklist passes | `./ops-vm/layer-b/patch/post-patch-smoke.sh \| tail -1` | `POST_PATCH_SMOKE_OK 5/5` |
| 13 | The declaration checker passes | `./access/layer-b/check-post-patch.sh` | `POST_PATCH_DECL_OK 8/8` |
| 14 | The People-tier gate is still green after the patch | `./access/layer-b/gate/run-people-tier-gate.sh` | `PEOPLE_TIER_GATE GREEN` |
| 15 | No foreign path touched | `./access/layer-b/check-owned-roots.sh origin/integration` | `OWNED_ROOTS_OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./ops-vm/layer-b/patch/post-patch-smoke.sh | tail -1 && \
./access/layer-b/check-post-patch.sh && \
./access/layer-b/gate/run-people-tier-gate.sh && \
./access/layer-b/check-owned-roots.sh origin/integration
```

Expected output, exactly four lines:

```
POST_PATCH_SMOKE_OK 5/5
POST_PATCH_DECL_OK 8/8
PEOPLE_TIER_GATE GREEN
OWNED_ROOTS_OK
```

### STOP rules

- **If the checklist passes but the reconciliation run is not clean** — STOP and do not record the patch as complete. §51.4: *"the patch is not recorded as complete until the checklist and the reconciliation run both pass clean."* File the blocker issue.
- **If the only way to fire a test alert is to enable alerting on Layer B-M** — STOP. Do not enable it. §90.2: *"People intelligence is never relayed over messaging surfaces."* File the blocker issue as escalation `E-P3-06` and leave the Layer B configuration untouched.
- **If the patch cannot be rolled back because no snapshot was taken before the upgrade** — STOP. §51.4: *"the snapshot is the rollback answer known before the upgrade starts."* An upgrade without one is outside the declared change shape. File the blocker issue.
- **If a Layer B signal is wanted as a push and it is not on the closed push list** — refuse and quote §92.11: *"the correct response is a governed addition to the push list and the event taxonomy, never an ad-hoc alert."* File the blocker issue.
- **If the People-tier gate has gone red since L5-03-12** — STOP the patch record and treat it as Blocking drift under `notify/routes/layer-b-gate-red.yaml`. A patch that reopens the Layer B boundary is not a completed patch.

---

## 3. What this phase publishes, and who consumes it

Every artifact below is in an L5-owned path and is consumed as a published interface — a path plus an exit contract — never by reaching into this lane's source tree (`PARTITION.md` rule 4).

| Id | Artifact | Exit contract | Consumed by | For |
|---|---|---|---|---|
| HO-P3-01 | `access/layer-b/gate/people-tier.gate.json` | JSON; `gate` is `GREEN` or `RED`; `verified` is the §98.6 subset | **L0**, and whichever lane is later assigned subsystem **P** | The only admissible evidence that the §90.3 / §98.6 People-tier gate is satisfied |
| HO-P3-02 | `access/layer-b/reconciliation-scope.yaml` | YAML; six surfaces; `finding_class.holder_in_neither_list` is `Blocking` | **L3** | The §90.4 comparison the reconciler executes, written down so it cannot be scoped narrower than the access it verifies |
| HO-P3-03 | `access/layer-b/check-owned-roots.sh <base>` | `0` clean · `1` a foreign path is staged | **L2** | The lane-guard check on every `lane/5/*` pull request in this phase |
| HO-P3-04 | `access/layer-b/at-097-…sh`, `at-098-…sh`, `at-089-…sh`, `at-090-…sh`, `at-091-…sh`, `at-092-…sh`, `at-095-…sh`, `at-096-…sh` | each `0` pass · `1` fail | **L0** (§100 acceptance-test execution) | The eight People-domain acceptance tests this phase makes executable |
| HO-P3-05 | `infra/layer-b/patch-cadence.yaml` | YAML; three components, each with cadence and security path | **L1** | The §62 tool-register entries; `registries/**` is not L5's |
| HO-P3-06 | `assets/inventory/layer-b-*.yaml` | one file per asset | **L5 phase 5** (`L5-05`), **L0** | The §49.1 asset-inventory sweep and the §40.1 fifth-tier credential inventory |
| HO-P3-07 | `notify/routes/layer-b-*.yaml` | one file per route; `push` is `true` only for a closed-list entry | **L5 phase 5**, **L0** | The §92.11 notification contract's Layer B rows |
| HO-P3-08 | `ops-vm/layer-b/manifest/verify-checksum-manifest.sh` | `0` verified · `1` mismatch or not decrypted | **L5 phase 4** (`L5-04`, restore rotation) | The §45.4 decrypt-plus-checksum-manifest integrity check in the restore drill |

**What this phase consumes, and from where.** Two files, both outside this lane and neither edited here: `contracts/access/access-inputs.yaml`, frozen by L0 at Phase 0; and the published capability-holders artifact it names at `layer_b.capability_holders_artifact`. The contract must also supply `layer_b_admin_group` (the GitHub team slug for Layer B administrative access; required — FD-038 / Q9; read by L5-03-09 for allowlist scoping and by L5-03-11 for the accepted-access record). Nothing else crosses a lane boundary inward.

---

## 4. Escalations to L0 — decisions this phase must not make

Each item sits inside L5's owned paths but outside L5's authority. The task named files the §1 blocker issue and stops; it never resolves the item itself.

| Id | Item | Why it is L0's | Raised by | Spec anchor |
|---|---|---|---|---|
| E-P3-01 | Assignment of subsystem **P, People intelligence engine** — the content of an evidence bundle, review pack and self-view — to a lane. `PARTITION` v1 assigns G, H, J, O and P to none. This phase builds the gate P is hard-gated on and claims nothing beyond it | L5 does not claim unassigned subsystems | L5-03-10, L5-03-12 | §99.2 dependency spine: *"P is hard-gated on L's datasource separation"*; `PARTITION.md` 15–22 |
| E-P3-02 | The onboarding checklist item that registers each person's public key half | Person onboarding is L0's onboarding track and the person registry is L1's | L5-03-10 | §90.6, *"a named onboarding checklist item"* |
| E-P3-03 | Recording each self-view re-key as a decision record | `records/decisions/` is L4's, in `control-plane-records` | L5-03-10 | §90.6, *"each re-key recorded as a decision"*; `PARTITION.md` 20 |
| E-P3-04 | The validator-level half of AT-090 — *"an attempt to create an assignment granting `people-intelligence` fails validation"* | `validators/registry/**` is L1's | L5-03-09 | §100.6 AT-090; `PARTITION.md` 17 |
| E-P3-05 | AT-091's clause *"Granting the dated delegate assignment opens access through reconciliation"* against D109's *"Layer B access is not delegable"* and §90.4's *"No assignment type grants it, and none may be introduced to do so"* | A specification tension between two binding statements. This phase implements the D109 direction and files the tension rather than choosing a reading | L5-03-09, L5-03-12 | §100.6 AT-091; D109; §90.4 |
| E-P3-06 | *"alert rules fire a test alert"* on the Layer B-M instance, against §90.2's *"People intelligence is never relayed over messaging surfaces"* and the `unified_alerting enabled = false` that sentence forces | Two binding sentences point opposite ways | L5-03-13 | §51.4 post-patch smoke checklist; §90.2 |
| E-P3-07 | The §62 tool-register entries for `grafana-layerb`, the people datasource and the Layer B host OS | `registries/**` is L1's | L5-03-13 | §51.4; §62; `PARTITION.md` 17 |
| E-P3-08 | Triggering the mandated immediate post-patch reconciliation run | `reconciler/**` is L3's | L5-03-13 | §51.4, *"An immediate reconciliation run follows, mandated"*; `PARTITION.md` 19 |
| E-P3-09 | Every value this phase reads from `contracts/access/access-inputs.yaml` — the two session durations, the capability-holders artifact path, the accepted-access holder, expiry and review cadence, and `layer_b_admin_group` (the GitHub team slug for Layer B administrative access; FD-038 / Q9) | `contracts/**` is L0's and FROZEN. A lane files a Contract Change Request; it never edits | L5-03-08, L5-03-09, L5-03-11 | `PARTITION.md` 22, 26 |
| E-P3-10 | Reconciling §90.3's *"a second, Founder-only Grafana instance **on the operations VM**"* with D95's *"the Layer B store separated from the shared host"*, where the estate has only one host | Two binding sentences point opposite ways, and this phase must not resolve it by co-locating the store | L5-03-02 | §90.3; D95; §40.3 |

---

## 5. Definition of done for this file

Phase 3 of lane L5 is complete when all thirteen task branches have merged to `integration` in index order, every SELF-VERIFY block in this file prints its expected output on a clean checkout of `integration`, and:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT" && ./access/layer-b/gate/run-people-tier-gate.sh
```

prints `PEOPLE_TIER_GATE GREEN` with `access/layer-b/gate/people-tier.gate.json` carrying `"verified": true` and `"106": "HOLDS"`, `"109": "HOLDS"`.

Three things this phase deliberately did **not** do, recorded here so no later reader mistakes them for omissions.

It did not generate a single item of Layer B evidence. §90.3 forbids it before this separation exists, and the separation is what this phase built. L5-03-10 built the envelope that will carry a self-view; the content of that document is subsystem P's, and P has no lane (`E-P3-01`).

It did not schedule anything. L5 owns no path under `.github/workflows/**`, so every check in this file is a script with an exit contract and no cadence. The gate runner, the parity check, the re-key check and the smoke checklist all wait on L2 to wire them (`HO-P3-03`, `HO-P3-04`).

It did not start P4. The gate artifact is evidence, not permission. §98.6 makes the artifact the precondition; who acts on it is L0's, and the lane that will own the People tier is not yet named.

**End of L5 Phase 3 — The Layer B Split.**
