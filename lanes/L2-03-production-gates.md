<!-- PARTIAL-SUPERSEDED (FD-B1-L2 + FD-044, 2026-09-02):
     The L2-P1-Txx namespace tasks and actor-gate implementation in this file are superseded by L2-05-tasks.md.
     The task bodies in this file for IDs that L2-05 §2.1 directs you here are STILL AUTHORITATIVE — execute from this file.
     Do NOT execute any L2-P1-Txx or actor-gate tasks from this file. -->

# L2-03 — LANE 2 PHASE 3: PRODUCTION APPROVAL AND ISOLATION

**Lane:** L2 Pipeline & Evidence (Subsystems E, F)
**Phase:** 3 of the Lane 2 build — *Production approval and isolation*
**Branch prefix:** `lane/2/phase3-*`
**Authority order:** `PARTITION.md` (FROZEN) → `L2-00-charter.md` → this document. Where this document appears to disagree with either, that document wins and this one is defective.
**Owned paths (exclusive, PARTITION.md §"The five build lanes"):** `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines)

---

## 0. WHAT THIS PHASE BUILDS

Phase 3 builds the five mechanisms that stand between a merged artifact and production. Every one of them fails **closed**: an unresolved input, an unreadable registry, an unreachable API and an unexpected value all exit non-zero. Nothing in this phase ever defaults to permit (§64, Safe Defaults and Fail-Closed Classification, L5431).

| # | Mechanism | Spec anchor | Charter deliverable |
|---|---|---|---|
| P3-A | **The workflow-identity gate** — the deploy workflow verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell. **This is the production-approval mechanism of record**, not a fallback for a missing Enterprise feature | §27.2 (L2567–2576); §11.4 table row (L881); §33.4 (L2911); D73 (L10156) | E-4 |
| P3-B | **The rollback workflow and its documented exemption** — redeploying a digest that already carries a production-approval record is exempt from the identity gate, and from nothing else | §27.2 rollback paragraph (L2575); §42.3 response flow (L3788–3812); §47.2 (L4227–4232); D52 (L10120); invariant 27 (L9488) | charter invariant row 27 |
| P3-C | **The actor gate** — first step of every privileged workflow; fails closed unless `github.actor` resolves to a human identity in `people.yaml` holding the capability the action requires | §37.3 (L3261–3268); invariant 18 (L9477) | E-5 |
| P3-D | **Privileged-workflow runner isolation** — hosted runners by default; an `--ephemeral` self-hosted runner in the `privileged` group as the declared per-product exception; **the workflow asserts its own runner tier and fails closed** | §39.5 privileged-workflow isolation (L3589–3596); D87 (L10191) | new in this phase |
| P3-E | **Deployment branch and tag policies** — the control that makes environment-scoped secrets true; asserted at deploy time by the workflow, applied by Lane 5 | §33.4 (L2911); §53.1 row "Environment deployment branch and tag policy" (L4661); D91 (L10184) | charter §4.4 requirement on L5 |

**The privileged-workflow set is closed** (§39.5, L3591): `deploy-production.yml`, `migrate.yml`, the rollback workflow, and the per-product production-restore workflow `restore-production.yml`. §37.3 (L3267) adds `deploy-staging.yml` to the *actor-gate* set specifically. This phase treats those five as the actor-gate set and the four of §39.5 as the runner-isolation set, exactly as the two sections state them.

### 0.1 What this phase does NOT build

| Not this phase | Owner | Why |
|---|---|---|
| Applying deployment branch/tag policies to real environments | **L5** (`infra/**`, `access/**`) | Charter §4.4. This phase asserts the policy at run time; it never configures one |
| Registering, labelling or provisioning runners | **L5** (`infra/**`) | This phase asserts the tier from inside the job; it never provisions a host |
| Record and event **schemas** | **L4** (`schemas/records/**`) | This phase authors the required, failing *write step*; L4 owns the shape (charter §4.3) |
| `people.yaml` content, capability vocabulary | **L1** (`registries/**`) | This phase reads it through the pinned contract surface only |
| The digest invariant itself (§32 item 5 vs item 11) | earlier L2 phase (E-3) | Phase 3 consumes it; it does not re-implement it |
| `contracts/**`, `CODEOWNERS`, `docs/**` | **L0** | Frozen. File a Contract Change Request, never an edit |

---

## 1. TASK-ID RESERVATION FOR THIS DOCUMENT

Subordinate to charter §12. This document reserves — and no other Lane 2 document may use — exactly these ids:

| Range | Tree |
|---|---|
| `L2-T170` – `L2-T199` | `.github/workflows/**` (charter block `L2-T100`–`L2-T299`) |
| `L2-T370` – `L2-T399` | `templates/workflows/**` (charter block `L2-T300`–`L2-T499`) |
| `L2-T570` – `L2-T599` | `tools/evidence/**` (charter block `L2-T500`–`L2-T699`) |

Twelve ids are used. The remainder are held for defect follow-ups on this phase and must not be reassigned.

**This file is authoritative for every id in those ranges, `L2-T171`–`L2-T173` included.** `L2-06-tests.md` cites `L2-T171`, `L2-T172` and `L2-T173` by id — in §8 N3/N4/N5 and in the `L2-T607`/`L2-T608`/`L2-T609` STOP rules — and defines no body for any of them; those citations are index references to §7 below and are correct as they stand (`L2-99-review.md` B2).

---

## 2. TASK INDEX

| Task | Title | Size | Depends on |
|---|---|---|---|
| `L2-T170` | Phase 3 precondition gate and contract pin | S | charter `L2-T001`, `L2-T002` |
| `L2-T171` | The actor gate — reusable workflow (P3-C) | M | `L2-T170` |
| `L2-T172` | The runner-tier assertion — reusable workflow and canonical step fragment (P3-D) | M | `L2-T170` |
| `L2-T173` | The environment deployment-policy assertion — reusable workflow (P3-E) | M | `L2-T170` |
| `L2-T174` | The workflow-identity gate — reusable workflow (P3-A) | L | `L2-T170` |
| `L2-T175` | The production gate chain — fixed-order composition of T171–T174 | M | `L2-T171`, `L2-T172`, `L2-T173`, `L2-T174` |
| `L2-T176` | The rollback reusable workflow (P3-B) | L | `L2-T171`, `L2-T172`, `L2-T173` |
| `L2-T370` | The per-product rollback workflow template | M | `L2-T176` |
| `L2-T371` | The rollback exemption declaration — machine-readable | S | `L2-T176`, `L2-T370` |
| `L2-T570` | `apply-production-gates` — the idempotent template-wiring tool | M | `L2-T175`, `L2-T370` |
| `L2-T571` | `assert-privileged-workflows` — the posture assertion (DoD-05) | M | `L2-T570` |
| `L2-T572` | Phase 3 negative-test suite — every gate proven fail-closed | L | `L2-T571` |
| `L2-T177` | Rebase, open the phase PR, exit | S | all of the above |

Execution order is the table order. No task may start before every task in its `Depends on` cell has printed its own `OK` line.

---

## 3. SESSION SETUP — RUN ONCE PER SHELL, BEFORE ANY TASK

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="<absolute path to the control-plane repo working copy>"
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO — STOP"; exit 1; }
git fetch origin integration
git switch -c lane/2/phase3-production-gates origin/integration
```

If `git switch -c` fails because the branch already exists, run `git switch lane/2/phase3-production-gates` instead. Do not create a differently named branch.

---

## 4. THE CONSUMED CONTRACT SURFACE FOR THIS PHASE

Every value below is read from `contracts/**` (L0, frozen in Phase 0). **The executor never invents one.** Resolution is by recursive grep over `contracts/**` for the key name, so an L0 decision to reorganise contract filenames does not break this phase.

| Contract key | Used by | Charter/DECISION reference |
|---|---|---|
| `control_plane_slug` | every `uses:` reference, every `gh api` call | charter §4.1 |
| `records_repo_slug` | reading deployment and approval records; writing records and events | D-L2-03 |
| `records_writer_secret_name` | the required, failing record-write steps (§97.2, L8926) | D-L2-03 |
| `registry_read_secret_name` | reading `people.yaml` in the actor gate and the identity gate | D-L2-03 |
| `workflows_tag` | the pinned reusable-workflow tag consumed by templates (§33.2, L2862) | charter §4.1 |
| `production_approval_record_glob` | the identity gate's approval-record lookup (§97.2 `records/deployments/`, L8848) | D-L2-03 |
| `verification_block_store` | the identity gate's open-block check (§27, L2551; §23.1, L2313) | **D-L2-08** (new, below) |
| `exceptional_authorisation_store` | the rollback workflow's exceptional-authorisation record (§27.2, L2575; §44.5, L4020) | **D-L2-10** (new, below) |
| `privileged_runner_marker_path` | the runner-tier assertion's self-hosted branch (D87, L10191) | **D-L2-09** (new, below) |
| `ephemeral_runner_marker_path` | the runner-tier assertion's self-hosted branch (D87, L10191) | **D-L2-09** (new, below) |

> **Note (Q9):** Both marker keys resolve to `not-applicable-v1` as Q9 confirmed. The marker read must be guarded so re-opening the gate requires a contract-value change, not a code change.

| `rollback_workflow_filename` | the per-product rollback template's filename | charter **D-L2-05** |

**Every one of these is a STOP condition when absent.** `L2-T170` resolves all eleven in one pass and refuses to continue if any is missing.

---

## 5. DECISION REQUIRED — HANDED TO L0

<!-- DECISIONS SUPERSEDED (FD-044): Decision IDs D-L2-07/08/09 in this file are superseded by L2-05-tasks.md §1. Do not reference these IDs in new work. -->

Lane 2 must not resolve any of these. File each as a Contract Change Request. Never edit `contracts/**`.

### DECISION REQUIRED D-L2-08 — Path of the verification-block store
**Question:** §27 (L2551) makes production approval and `deploy-production.yml` **fail closed while an open verification-block record exists** for the change or the product, and §23.1 (L2313) makes the block "a verification-block record — an artifact, not a message". §97.2's canonical record-store table (L8843–8866) lists no store for it.
**Why L2 cannot decide:** the store path is read by an L2 gate, written by a QA-facing surface, and compared by L3 reconciliation. A guessed path makes the gate read an empty directory and pass — the exact fail-open §64 forbids.
**Options for L0:** (a) add `records/verification-blocks/` to §97.2's store set and publish `verification_block_store`; (b) declare the block a labelled state on the item and publish the query instead.
**Blocks:** step `verification-block` of `L2-T174` only. Until it resolves, that step must be present and must **exit non-zero** with `VERIFICATION_BLOCK_STORE_UNRESOLVED` — a fail-closed stub, never a skipped one.

### DECISION REQUIRED D-L2-09 — Runtime evidence of privileged-runner tier
**Question:** D87 (L10191) requires each privileged workflow to assert its own runner tier and fail closed, with the declared exception being an `--ephemeral` self-hosted runner in a runner group labelled `privileged`. GitHub exposes neither the runner group nor the `--ephemeral` registration flag to the running job. The only runtime-checkable evidence is a host-side marker placed by L5 at runner provisioning time.
**Why L2 cannot decide:** the marker paths are an L5 `infra/**` interface. Inventing them makes the assertion untestable and the three §53.1 Blocking drift rows (L3596) uncheckable.
**Options for L0:** (a) publish `privileged_runner_marker_path` and `ephemeral_runner_marker_path` as an L5-implemented contract, written at runner registration; (b) declare that no product takes the D87 exception in V1, in which case the self-hosted branch of the assertion is unreachable by construction and the hosted branch is the whole control.
**Blocks:** the self-hosted branch of `L2-T172` only. The hosted default — which is D87's stated default — is unblocked and is built in this phase regardless.

### DECISION REQUIRED D-L2-10 — Where a rollback's exceptional-authorisation record lands
**Question:** §27.2 (L2575) requires that "each run of the rollback workflow is recorded as an exceptional authorisation and audited (Section 42.3)". §54.1's `exceptions.yaml` (L4753–4785) is a single shared registry file in the control-plane repository; PARTITION.md rule 3 forbids any workflow appending to a shared mutable file, and §26.2 (L2514) instead points at "a written record in the decision store (Section 97)".
**Why L2 cannot decide:** choosing between `exceptions.yaml`, `records/decisions/` and a new per-run store is a records-architecture decision owned by L4 and L0, and the write credential is L5's.
**Options for L0:** (a) publish `exceptional_authorisation_store` as a directory-per-record store in `control-plane-records`; (b) declare the rollback record an `emergency_production` entry written by a human through the registry-change lane of §26.4 (L2526), in which case the workflow writes only the event and the deployment record.
**Blocks:** step `exceptional-authorisation-record` of `L2-T176`. Until it resolves, that step must be present and must **exit non-zero** with `EXCEPTIONAL_AUTH_STORE_UNRESOLVED`.

Charter decisions still binding on this phase and not restated here: **D-L2-03** (record write interface) and **D-L2-05** (rollback workflow filename).

---

## 6. STOP RULES

The charter's standing rules **S1–S5** (charter §10) apply to every task in this document without restatement. Three phase-specific rules are added:

**S6 — Never weaken a gate to make a task pass.** If a gate cannot be made to pass, the gate is right and the situation is wrong. Do not add `continue-on-error`, do not add `if: always()`, do not widen an allowlist, do not change an exact failure string. STOP and file a blocker.

**S7 — Never introduce a skip on a gate job.** §33.2 (L2860) makes a `skipped` or `neutral` conclusion on a required context Blocking drift. No job authored in this phase may carry an `if:` condition or a path filter. If a task appears to require one, STOP under `S4`.

**S8 — Never edit a workflow file authored by an earlier phase with a text editor or `sed`.** Wiring into an existing template is done **only** through `tools/evidence/apply-production-gates.py` (`L2-T570`), which is idempotent and YAML-aware. A hand edit that reorders or drops a key in an existing template is undetectable and is exactly the failure §53.1's template comparison cannot see.

Blocker issues are filed with the charter's verbatim template (charter §10, "Blocker-issue template — file verbatim"), substituting this phase's task id.

---

## 7. TASKS

### L2-T170 — Phase 3 precondition gate and contract pin

**Size:** S  **Depends on:** charter `L2-T001`, `L2-T002`

**Creates:** `tools/evidence/phase3-preconditions.sh`, `tools/evidence/phase3-contract.env`

This task resolves all eleven contract keys of §4 in one pass and writes them to a pinned env file that every later task in this phase sources. It resolves nothing by judgment: a key is either present in `contracts/**` or the phase stops.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence
cat > tools/evidence/phase3-preconditions.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 Phase 3 precondition gate.
# Spec: MultiProduct_MasterSpec_v4.0.md Sections 27.2 (2567-2576), 37.3 (3261-3268),
#       39.5 (3589-3596), 33.4 (2911). Decisions D52, D73, D87, D91.
# Resolves the consumed contract surface. Fails closed: any missing key aborts.
# Re-runnable. Writes tools/evidence/phase3-contract.env.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if [ ! -d contracts ]; then
  echo "PHASE3_CONTRACTS_ABSENT"
  exit 1
fi

KEYS="control_plane_slug records_repo_slug records_writer_secret_name \
registry_read_secret_name workflows_tag production_approval_record_glob \
verification_block_store exceptional_authorisation_store \
privileged_runner_marker_path ephemeral_runner_marker_path \
rollback_workflow_filename"

OUT="tools/evidence/phase3-contract.env"
TMP="$(mktemp)"
echo "# GENERATED by tools/evidence/phase3-preconditions.sh — do not hand-edit." > "$TMP"
echo "# Resolved from contracts/** at commit $(git rev-parse HEAD)" >> "$TMP"

MISSING=""
for k in $KEYS; do
  # A contract key is a top-level or nested YAML scalar. Take the first
  # occurrence in lexical file order; contracts/** is frozen, so it is stable.
  v="$(grep -rhE "^[[:space:]]*${k}:[[:space:]]*[^[:space:]#]" contracts/ 2>/dev/null \
        | head -n 1 \
        | sed -E "s/^[[:space:]]*${k}:[[:space:]]*//" \
        | sed -E 's/[[:space:]]*#.*$//' \
        | tr -d '"'"'"'' )"
  if [ -z "${v}" ]; then
    MISSING="${MISSING} ${k}"
    continue
  fi
  printf '%s=%s\n' "$(echo "$k" | tr '[:lower:]' '[:upper:]')" "${v}" >> "$TMP"
done

if [ -n "${MISSING}" ]; then
  echo "PHASE3_CONTRACT_KEY_MISSING:${MISSING}"
  rm -f "$TMP"
  exit 1
fi

mv "$TMP" "$OUT"
echo "PHASE3_PRECONDITIONS_OK"
EOF
chmod +x tools/evidence/phase3-preconditions.sh
bash tools/evidence/phase3-preconditions.sh
git add tools/evidence/phase3-preconditions.sh tools/evidence/phase3-contract.env
git commit -m "L2-T170: phase 3 precondition gate and contract pin"
```

After the commit, load the pin into the shell. Every later task assumes these are exported:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
echo "$CONTROL_PLANE_SLUG $WORKFLOWS_TAG $ROLLBACK_WORKFLOW_FILENAME"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script exists and is executable | `test -x tools/evidence/phase3-preconditions.sh; echo $?` | exactly `0` |
| A2 | Script exits 0 and prints the success token | `bash tools/evidence/phase3-preconditions.sh` | exactly `PHASE3_PRECONDITIONS_OK` |
| A3 | Exactly eleven keys resolved | `grep -c '^[A-Z_]*=' tools/evidence/phase3-contract.env` | exactly `11` |
| A4 | No resolved value is empty | `grep -cE '^[A-Z_]+=$' tools/evidence/phase3-contract.env` | exactly `0` |
| A5 | Re-running is idempotent | `bash tools/evidence/phase3-preconditions.sh && git diff --quiet tools/evidence/phase3-contract.env; echo $?` | exactly `0` |
| A6 | Nothing outside owned trees changed | `git diff --name-only HEAD~1 HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(bash tools/evidence/phase3-preconditions.sh)" = "PHASE3_PRECONDITIONS_OK" \
 && test "$(grep -c '^[A-Z_]*=' tools/evidence/phase3-contract.env)" = "11" \
 && test "$(grep -cE '^[A-Z_]+=$' tools/evidence/phase3-contract.env)" = "0" \
 && echo "L2-T170 OK" || echo "L2-T170 FAIL"
```
Correct output: the single line `L2-T170 OK`.

**STOP rule:** if the script prints `PHASE3_CONTRACTS_ABSENT` or any `PHASE3_CONTRACT_KEY_MISSING:` line, **do not proceed to any other task in this phase and do not invent a value.** File the charter blocker template with `STOP RULE TRIGGERED: S1`, `WHAT HAPPENED:` the verbatim output line, and `WHAT I NEED TO PROCEED:` the exact list of key names printed after the colon, citing the row of §4 that names each. If the missing key is `verification_block_store`, `exceptional_authorisation_store`, `privileged_runner_marker_path` or `ephemeral_runner_marker_path`, additionally reference **D-L2-08**, **D-L2-10** or **D-L2-09** as applicable; if it is `rollback_workflow_filename`, reference charter **D-L2-05**.

---

<!-- SUPERSEDED: Actor-gate implementation here is superseded by L2-05-tasks.md (FD-044) -->
### L2-T171 — The actor gate (P3-C)

> **DO NOT DISPATCH — SUPERSEDED (FD-044, 2026-09-02):**
> This task body is superseded by `L2-05-tasks.md` task **L2-T541**.
> Dispatch L2-T541 from L2-05-tasks.md for the actor-gate implementation.

**Size:** M  **Depends on:** `L2-T170`

**Creates:** `.github/workflows/actor-gate.yml`

§37.3 (L3267): *"an actor gate as the first step of every privileged workflow: `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, the rollback workflow and the production-restore workflow fail closed unless `github.actor` resolves to a human identity in `people.yaml` holding the capability the action requires — `production-approval`, `incident-response` or `devops`. The machine account's permitted dispatch set is a positive allowlist checked inside each workflow — the digest generators of Section 94.7 and nothing else."*

Those three capability names and that one machine class are the complete vocabulary this gate accepts. Anything else is `ACTOR_GATE_INPUT_UNRESOLVED`.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
mkdir -p .github/workflows
cat > .github/workflows/actor-gate.yml <<'EOF'
name: actor-gate
# =====================================================================
# THE ACTOR GATE — Section 37.3 (lines 3261-3268); invariant 18 (line 9477).
# First step of every privileged workflow. Fails closed unless github.actor
# resolves to a HUMAN identity in people.yaml holding the required capability.
# The machine account's permitted dispatch set is a POSITIVE allowlist:
# the digest generators of Section 94.7 (line 8567) and nothing else.
# Removing this gate from a workflow is Blocking drift (Section 53.1, line 4671).
# NO `if:` and NO path filter anywhere in this file (Section 33.2, line 2860).
# =====================================================================
on:
  workflow_call:
    inputs:
      required_capabilities:
        description: >-
          Comma-separated subset of: production-approval, incident-response, devops.
          The actor must hold AT LEAST ONE. Any other token fails closed.
        required: true
        type: string
      actor:
        description: 'The caller passes ${{ github.actor }}. Never a literal.'
        required: true
        type: string
      registry_ref:
        description: 'Immutable control-plane ref (full 40-char SHA) carrying people.yaml.'
        required: true
        type: string
      machine_dispatch_class:
        description: 'none | digest-generator. Section 37.3 admits digest-generator only.'
        required: false
        type: string
        default: none
    outputs:
      person_id:
        description: 'The resolved people.yaml id of the gated actor.'
        value: ${{ jobs.actor-gate.outputs.person_id }}
    secrets:
      REGISTRY_READ_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  actor-gate:
    name: actor-gate
    runs-on: ubuntu-latest
    timeout-minutes: 5
    outputs:
      person_id: ${{ steps.resolve.outputs.person_id }}
    steps:
      - name: Validate inputs — fail closed on anything unrecognised
        env:
          REQUIRED_CAPABILITIES: ${{ inputs.required_capabilities }}
          ACTOR: ${{ inputs.actor }}
          REGISTRY_REF: ${{ inputs.registry_ref }}
          MACHINE_DISPATCH_CLASS: ${{ inputs.machine_dispatch_class }}
        run: |
          set -euo pipefail
          if [ -z "${REQUIRED_CAPABILITIES}" ] || [ -z "${ACTOR}" ] || [ -z "${REGISTRY_REF}" ]; then
            echo "ACTOR_GATE_INPUT_UNRESOLVED"; exit 1
          fi
          case "${MACHINE_DISPATCH_CLASS}" in
            none|digest-generator) ;;
            *) echo "ACTOR_GATE_INPUT_UNRESOLVED"; exit 1 ;;
          esac
          echo "${REGISTRY_REF}" | grep -qE '^[0-9a-f]{40}$' \
            || { echo "ACTOR_GATE_INPUT_UNRESOLVED"; exit 1; }
          IFS=',' read -ra CAPS <<< "${REQUIRED_CAPABILITIES}"
          if [ "${#CAPS[@]}" -eq 0 ]; then echo "ACTOR_GATE_INPUT_UNRESOLVED"; exit 1; fi
          for c in "${CAPS[@]}"; do
            case "${c}" in
              production-approval|incident-response|devops) ;;
              *) echo "ACTOR_GATE_INPUT_UNRESOLVED"; exit 1 ;;
            esac
          done
          echo "ACTOR_GATE_INPUT_OK"

      - name: Fetch people.yaml at the pinned control-plane ref
        env:
          GH_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}
          REGISTRY_REF: ${{ inputs.registry_ref }}
        run: |
          set -euo pipefail
          if ! gh api "repos/@@SLUG@@/contents/people.yaml?ref=${REGISTRY_REF}" \
                 -H "Accept: application/vnd.github.raw" > people.yaml 2>fetch.err; then
            cat fetch.err >&2
            echo "ACTOR_GATE_REGISTRY_UNREADABLE"; exit 1
          fi
          if [ ! -s people.yaml ]; then
            echo "ACTOR_GATE_REGISTRY_UNREADABLE"; exit 1
          fi
          echo "ACTOR_GATE_REGISTRY_READ_OK"

      - name: Resolve the actor against people.yaml
        id: resolve
        env:
          REQUIRED_CAPABILITIES: ${{ inputs.required_capabilities }}
          ACTOR: ${{ inputs.actor }}
          MACHINE_DISPATCH_CLASS: ${{ inputs.machine_dispatch_class }}
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          python3 - <<'PYEOF'
          import os, sys, yaml

          def fail(token):
              print(token)
              sys.exit(1)

          try:
              with open("people.yaml", "r", encoding="utf-8") as fh:
                  reg = yaml.safe_load(fh)
          except Exception:
              fail("ACTOR_GATE_REGISTRY_UNREADABLE")

          if not isinstance(reg, dict) or not isinstance(reg.get("people"), list):
              fail("ACTOR_GATE_REGISTRY_UNREADABLE")

          actor = os.environ["ACTOR"].strip().lower()
          wanted = [c.strip() for c in os.environ["REQUIRED_CAPABILITIES"].split(",") if c.strip()]
          machine_class = os.environ["MACHINE_DISPATCH_CLASS"].strip()

          match = None
          for p in reg["people"]:
              if not isinstance(p, dict):
                  continue
              login = str(p.get("github_login", "")).strip().lower()
              if login and login == actor:
                  match = p
                  break

          # Section 37.3: an actor with no people.yaml entry is not a human identity.
          # Section 7.1 (line 605): where a value is missing or malformed, the
          # resolution is denial, not a default that permits.
          if match is None:
              fail("ACTOR_NOT_HUMAN")

          # The positive machine allowlist. Section 37.3 admits the Section 94.7
          # digest generators and nothing else; none of the five privileged
          # workflows is a digest generator, so for them this is always a refusal.
          if str(match.get("identity_class", "human")).strip() == "machine":
              if machine_class != "digest-generator":
                  fail("ACTOR_NOT_HUMAN")

          availability = str(match.get("availability", "")).strip()
          access_status = str(match.get("access_status", "")).strip()
          if availability not in ("active", "on_leave"):
              fail("ACTOR_NOT_ACTIVE")
          if access_status != "provisioned":
              fail("ACTOR_NOT_ACTIVE")

          held = match.get("capabilities") or []
          if not isinstance(held, list):
              fail("ACTOR_GATE_REGISTRY_UNREADABLE")
          held = [str(c).strip() for c in held]
          if not any(c in held for c in wanted):
              fail("ACTOR_CAPABILITY_MISSING")

          person_id = str(match.get("id", "")).strip()
          if not person_id:
              fail("ACTOR_GATE_REGISTRY_UNREADABLE")

          with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
              out.write("person_id=%s\n" % person_id)
          print("ACTOR_GATE_PASS %s" % person_id)
          PYEOF
EOF
sed -i "s|@@SLUG@@|${CONTROL_PLANE_SLUG}|g" .github/workflows/actor-gate.yml
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/actor-gate.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/actor-gate.yml
git commit -m "L2-T171: actor gate reusable workflow (Section 37.3, invariant 18)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists and is valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/actor-gate.yml'))"; echo $?` | exactly `0` |
| A2 | No placeholder survives substitution | `grep -c '@@' .github/workflows/actor-gate.yml` | exactly `0` |
| A3 | The gate carries no `if:` and no path filter (S7) | `grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/actor-gate.yml` | exactly `0` |
| A4 | All five failure tokens are present exactly once each | `for t in ACTOR_GATE_INPUT_UNRESOLVED ACTOR_GATE_REGISTRY_UNREADABLE ACTOR_NOT_HUMAN ACTOR_NOT_ACTIVE ACTOR_CAPABILITY_MISSING; do grep -q "$t" .github/workflows/actor-gate.yml \|\| echo "MISSING $t"; done` | prints nothing |
| A5 | The capability allowlist is exactly the three of §37.3 | `grep -c 'production-approval\|incident-response\|devops) ;;' .github/workflows/actor-gate.yml` | exactly `1` |
| A6 | Token permissions are least-privilege (§33.2, L2864) | `grep -A1 '^permissions:' .github/workflows/actor-gate.yml \| grep -c 'contents: read'` | exactly `1` |
| A7 | Every `${{ inputs.* }}` reaching a `run:` does so through `env:`, never inline | `grep -cE '^\s+.*\$\{\{ inputs\.' .github/workflows/actor-gate.yml \| : ; grep -cE 'run:.*\$\{\{' .github/workflows/actor-gate.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/actor-gate.yml'))" \
 && test "$(grep -c '@@' .github/workflows/actor-gate.yml)" = "0" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/actor-gate.yml)" = "0" \
 && test "$(grep -cE 'run:.*\$\{\{' .github/workflows/actor-gate.yml)" = "0" \
 && for t in ACTOR_GATE_INPUT_UNRESOLVED ACTOR_GATE_REGISTRY_UNREADABLE ACTOR_NOT_HUMAN ACTOR_NOT_ACTIVE ACTOR_CAPABILITY_MISSING ACTOR_GATE_PASS; do \
      grep -q "$t" .github/workflows/actor-gate.yml || exit 1; done \
 && echo "L2-T171 OK" || echo "L2-T171 FAIL"
```
Correct output: the single line `L2-T171 OK`.

**STOP rule:** if `python3 -c "import yaml"` is unavailable on the workstation, install PyYAML with `pip3 install 'pyyaml==6.0.2'` and retry once. If it still fails, STOP under `S4` — do not substitute a different parser or skip the parse check, because an unparsed workflow file is a gate that never runs. If A5 does not print exactly `1`, the capability allowlist has been altered: STOP under **S6** and file a blocker quoting §37.3 line 3267.

---

### L2-T172 — The runner-tier assertion (P3-D)

**Size:** M  **Depends on:** `L2-T170`

**Creates:** `templates/workflows/runner-tier-assert.step.yml`, `.github/workflows/runner-tier-assert.yml`

D87 (L10191) and §39.5 (L3589–3596) state the posture exactly: hosted runners are the **default** for the four privileged workflows; the **declared exception** is an `--ephemeral` self-hosted runner in a runner group labelled `privileged` that never accepts a branch-push job; and *"the separation is asserted in the workflow, not only in configuration — each privileged workflow fails closed unless the runner it resolved to carries the `privileged` label or is hosted"*.

Two artifacts, one script body. The **fragment** is the canonical copy that `apply-production-gates.py` (`L2-T570`) splices as step index 0 of every privileged job, so the assertion runs on the same runner as the privileged work. The **reusable workflow** is the same body for the gate chain, executing on the caller's declared label so it asserts the same tier.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
mkdir -p templates/workflows .github/workflows
cat > templates/workflows/runner-tier-assert.step.yml <<'EOF'
# RUNNER-TIER-ASSERT v1 — CANONICAL FRAGMENT. DO NOT EDIT BY HAND.
# Spec: Section 39.5 privileged-workflow isolation (lines 3589-3596); D87 (line 10180).
# Spliced as step index 0 of every privileged job by tools/evidence/apply-production-gates.py.
# Byte-identity with this file is asserted by tools/evidence/assert-privileged-workflows.py.
- name: RUNNER-TIER-ASSERT v1
  env:
    PRIVILEGED_SELF_HOSTED_DECLARED: ${{ inputs.privileged_self_hosted_declared }}
    PRIVILEGED_RUNNER_MARKER: '@@PRIVMARKER@@'
    EPHEMERAL_RUNNER_MARKER: '@@EPHMARKER@@'
  run: |
    set -euo pipefail
    # D87: hosted is the default and needs no declaration. A hosted runner is
    # destroyed after every job, so no host persists between an untrusted
    # branch-push job and a privileged one.
    if [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ]; then
      echo "RUNNER_TIER_OK hosted"
      exit 0
    fi
    # D87: the one sanctioned self-hosted path for a privileged workflow is an
    # --ephemeral runner in a group labelled `privileged`, recorded per product
    # in the contract with its reason. All three conditions must hold.
    if [ "${RUNNER_ENVIRONMENT:-}" = "self-hosted" ]; then
      if [ "${PRIVILEGED_SELF_HOSTED_DECLARED:-false}" != "true" ]; then
        echo "RUNNER_TIER_UNDECLARED_SELF_HOSTED"
        exit 1
      fi
      if [ ! -f "${PRIVILEGED_RUNNER_MARKER}" ]; then
        echo "RUNNER_TIER_SHARED_POOL"
        exit 1
      fi
      if [ ! -f "${EPHEMERAL_RUNNER_MARKER}" ]; then
        echo "RUNNER_TIER_NOT_EPHEMERAL"
        exit 1
      fi
      echo "RUNNER_TIER_OK privileged-ephemeral"
      exit 0
    fi
    # Anything else — an unset or unknown RUNNER_ENVIRONMENT — is unresolved,
    # and Section 64 resolves the unresolved as denial.
    echo "RUNNER_TIER_UNRESOLVED"
    exit 1
EOF
sed -i "s|@@PRIVMARKER@@|${PRIVILEGED_RUNNER_MARKER_PATH}|g; s|@@EPHMARKER@@|${EPHEMERAL_RUNNER_MARKER_PATH}|g" \
  templates/workflows/runner-tier-assert.step.yml

cat > .github/workflows/runner-tier-assert.yml <<'EOF'
name: runner-tier-assert
# =====================================================================
# RUNNER-TIER ASSERTION — Section 39.5 (lines 3589-3596); D87 (line 10180).
# Executes on the CALLER'S declared runner label, so what it asserts is the
# tier the privileged work will actually run on — not a second, unrelated runner.
# Reconciliation carries three Blocking rows for this posture (Section 53.1,
# via line 3596): a non-ephemeral runner in the `privileged` group; a privileged
# workflow resolving to a shared-pool label; and a branch-push-triggered
# workflow admitted to the `privileged` group.
# =====================================================================
on:
  workflow_call:
    inputs:
      runner_label:
        description: 'The caller passes the SAME label its privileged job uses.'
        required: true
        type: string
      privileged_self_hosted_declared:
        description: >-
          true only where the product contract records the D87 exception with
          its reason. Absent or false means hosted-only.
        required: true
        type: string

permissions:
  contents: read

jobs:
  runner-tier-assert:
    name: runner-tier-assert
    runs-on: ${{ inputs.runner_label }}
    timeout-minutes: 5
    steps:
      - name: RUNNER-TIER-ASSERT v1
        env:
          PRIVILEGED_SELF_HOSTED_DECLARED: ${{ inputs.privileged_self_hosted_declared }}
          PRIVILEGED_RUNNER_MARKER: '@@PRIVMARKER@@'
          EPHEMERAL_RUNNER_MARKER: '@@EPHMARKER@@'
        run: |
          set -euo pipefail
          if [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ]; then
            echo "RUNNER_TIER_OK hosted"
            exit 0
          fi
          if [ "${RUNNER_ENVIRONMENT:-}" = "self-hosted" ]; then
            if [ "${PRIVILEGED_SELF_HOSTED_DECLARED:-false}" != "true" ]; then
              echo "RUNNER_TIER_UNDECLARED_SELF_HOSTED"
              exit 1
            fi
            if [ ! -f "${PRIVILEGED_RUNNER_MARKER}" ]; then
              echo "RUNNER_TIER_SHARED_POOL"
              exit 1
            fi
            if [ ! -f "${EPHEMERAL_RUNNER_MARKER}" ]; then
              echo "RUNNER_TIER_NOT_EPHEMERAL"
              exit 1
            fi
            echo "RUNNER_TIER_OK privileged-ephemeral"
            exit 0
          fi
          echo "RUNNER_TIER_UNRESOLVED"
          exit 1
EOF
sed -i "s|@@PRIVMARKER@@|${PRIVILEGED_RUNNER_MARKER_PATH}|g; s|@@EPHMARKER@@|${EPHEMERAL_RUNNER_MARKER_PATH}|g" \
  .github/workflows/runner-tier-assert.yml
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/runner-tier-assert.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
python3 -c "import yaml;yaml.safe_load(open('templates/workflows/runner-tier-assert.step.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add templates/workflows/runner-tier-assert.step.yml .github/workflows/runner-tier-assert.yml
git commit -m "L2-T172: privileged-workflow runner-tier assertion (D87, Section 39.5)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Both files are valid YAML | `for f in templates/workflows/runner-tier-assert.step.yml .github/workflows/runner-tier-assert.yml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" "$f" \|\| echo "BAD $f"; done` | prints nothing |
| A2 | No placeholder survives | `grep -rc '@@' templates/workflows/runner-tier-assert.step.yml .github/workflows/runner-tier-assert.yml \| grep -vc ':0'` | exactly `0` |
| A3 | Hosted is the accepted default (D87) | `grep -c 'RUNNER_TIER_OK hosted' templates/workflows/runner-tier-assert.step.yml` | exactly `1` |
| A4 | All four failure tokens present in both files | `for t in RUNNER_TIER_UNDECLARED_SELF_HOSTED RUNNER_TIER_SHARED_POOL RUNNER_TIER_NOT_EPHEMERAL RUNNER_TIER_UNRESOLVED; do test "$(grep -rc "$t" templates/workflows/runner-tier-assert.step.yml .github/workflows/runner-tier-assert.yml \| grep -c ':1')" = "2" \|\| echo "BAD $t"; done` | prints nothing |
| A5 | The two script bodies are identical after normalisation | see SELF-VERIFY below | exactly `IDENTICAL` |
| A6 | The reusable workflow runs on the caller's label, not a fixed one | `grep -c 'runs-on: \${{ inputs.runner_label }}' .github/workflows/runner-tier-assert.yml` | exactly `1` |
| A7 | No `if:` and no path filter (S7) | `grep -rcE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/runner-tier-assert.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
A="$(sed -n '/RUNNER_ENVIRONMENT/,$p' templates/workflows/runner-tier-assert.step.yml | sed -E 's/^[[:space:]]+//' | grep -v '^#' | sha256sum | cut -d' ' -f1)"
B="$(sed -n '/RUNNER_ENVIRONMENT/,$p' .github/workflows/runner-tier-assert.yml | sed -E 's/^[[:space:]]+//' | grep -v '^#' | sha256sum | cut -d' ' -f1)"
test "$A" = "$B" && echo IDENTICAL || echo DIVERGED
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/runner-tier-assert.yml'))" \
 && python3 -c "import yaml;yaml.safe_load(open('templates/workflows/runner-tier-assert.step.yml'))" \
 && test "$A" = "$B" \
 && test "$(grep -c '@@' templates/workflows/runner-tier-assert.step.yml)" = "0" \
 && test "$(grep -c '@@' .github/workflows/runner-tier-assert.yml)" = "0" \
 && echo "L2-T172 OK" || echo "L2-T172 FAIL"
```
Correct output: the line `IDENTICAL` followed by the line `L2-T172 OK`.

**STOP:** `L2-T176` is authoritative for `rollback.yml`. Verify its acceptance criteria are complete before proceeding.

---

### L2-T173 — The environment deployment-policy assertion (P3-E)

**Size:** M  **Depends on:** `L2-T170`

**Creates:** `.github/workflows/env-policy-assert.yml`

D91 (L10184): *"Branch protection governs what merges; a deployment branch policy governs what may reach an environment's secrets, and a repository with the first and not the second holds production credentials behind nothing."* §33.4 (L2911) gives the shape: `staging` and `production` accept deployments **from the default branch and from protected release tags only, and from no other ref**.

Lane 5 applies the policy. This workflow asserts, at deploy time and from inside the job, that the policy exists and that the running ref is one the policy admits. An unreadable API is a refusal, not a pass.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
cat > .github/workflows/env-policy-assert.yml <<'EOF'
name: env-policy-assert
# =====================================================================
# DEPLOYMENT BRANCH AND TAG POLICY ASSERTION
# Spec: Section 33.4 (line 2911); Section 53.1 row "Environment deployment
# branch and tag policy" (line 4661); D91 (line 10184).
# The policy is APPLIED by Lane 5 (infra/**). This workflow only asserts it,
# from inside the job that is about to touch the environment's secrets.
# Without the policy, any Write holder pushes a branch declaring
# `environment: production` and GitHub hands that job the environment's
# secrets from an unreviewed ref (Section 33.4).
# =====================================================================
on:
  workflow_call:
    inputs:
      environment_name:
        description: 'development | staging | production'
        required: true
        type: string
      target_repo:
        description: 'owner/repo whose environment is being asserted.'
        required: true
        type: string
      deploy_ref:
        description: 'The caller passes ${{ github.ref }} — the ref this run resolved from.'
        required: true
        type: string
    secrets:
      ENV_POLICY_READ_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  env-policy-assert:
    name: env-policy-assert
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Validate inputs — fail closed on anything unrecognised
        env:
          ENVIRONMENT_NAME: ${{ inputs.environment_name }}
          TARGET_REPO: ${{ inputs.target_repo }}
          DEPLOY_REF: ${{ inputs.deploy_ref }}
        run: |
          set -euo pipefail
          case "${ENVIRONMENT_NAME}" in
            development|staging|production) ;;
            *) echo "ENV_POLICY_INPUT_UNRESOLVED"; exit 1 ;;
          esac
          echo "${TARGET_REPO}" | grep -qE '^[^/]+/[^/]+$' \
            || { echo "ENV_POLICY_INPUT_UNRESOLVED"; exit 1; }
          test -n "${DEPLOY_REF}" || { echo "ENV_POLICY_INPUT_UNRESOLVED"; exit 1; }
          echo "ENV_POLICY_INPUT_OK"

      - name: Assert the environment carries a deployment branch and tag policy
        env:
          GH_TOKEN: ${{ secrets.ENV_POLICY_READ_TOKEN }}
          ENVIRONMENT_NAME: ${{ inputs.environment_name }}
          TARGET_REPO: ${{ inputs.target_repo }}
          DEPLOY_REF: ${{ inputs.deploy_ref }}
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'

          if ! gh api "repos/${TARGET_REPO}/environments/${ENVIRONMENT_NAME}" > env.json 2>api.err; then
            cat api.err >&2
            echo "ENV_POLICY_UNREADABLE"; exit 1
          fi
          if ! gh api "repos/${TARGET_REPO}/environments/${ENVIRONMENT_NAME}/deployment-branch-policies" \
                 > policies.json 2>api2.err; then
            cat api2.err >&2
            echo "ENV_POLICY_UNREADABLE"; exit 1
          fi
          if ! gh api "repos/${TARGET_REPO}" --jq '.default_branch' > default_branch.txt 2>api3.err; then
            cat api3.err >&2
            echo "ENV_POLICY_UNREADABLE"; exit 1
          fi

          python3 - <<'PYEOF'
          import json, os, sys, fnmatch

          def fail(token):
              print(token)
              sys.exit(1)

          try:
              env = json.load(open("env.json", encoding="utf-8"))
              pol = json.load(open("policies.json", encoding="utf-8"))
              default_branch = open("default_branch.txt", encoding="utf-8").read().strip()
          except Exception:
              fail("ENV_POLICY_UNREADABLE")

          if not default_branch:
              fail("ENV_POLICY_UNREADABLE")

          name = os.environ["ENVIRONMENT_NAME"]
          ref = os.environ["DEPLOY_REF"]

          dbp = env.get("deployment_branch_policy")
          # D91: no policy at all is the failure the decision exists to name.
          if dbp is None:
              fail("ENV_POLICY_ABSENT")

          # Section 33.4: staging and production accept the default branch and
          # protected release tags ONLY. `protected_branches: true` is GitHub's
          # all-protected-branches mode and is WIDER than "the default branch",
          # so it does not satisfy the declaration.
          if name in ("staging", "production"):
              if dbp.get("protected_branches") is True:
                  fail("ENV_POLICY_TOO_WIDE")
              if dbp.get("custom_branch_policies") is not True:
                  fail("ENV_POLICY_ABSENT")

          patterns = []
          for entry in pol.get("branch_policies", []) or []:
              pat = str(entry.get("name", "")).strip()
              typ = str(entry.get("type", "branch")).strip()
              if pat:
                  patterns.append((typ, pat))
          if not patterns:
              fail("ENV_POLICY_ABSENT")

          # The running ref must be admitted by one of the declared patterns.
          if ref.startswith("refs/heads/"):
              short, kind = ref[len("refs/heads/"):], "branch"
          elif ref.startswith("refs/tags/"):
              short, kind = ref[len("refs/tags/"):], "tag"
          else:
              fail("ENV_POLICY_REF_NOT_ADMITTED")

          admitted = any(
              (typ == kind or typ == "branch" and kind == "branch")
              and fnmatch.fnmatch(short, pat)
              for typ, pat in patterns
          )
          if not admitted:
              fail("ENV_POLICY_REF_NOT_ADMITTED")

          # And for staging/production a branch ref may only ever be the default branch.
          if name in ("staging", "production") and kind == "branch" and short != default_branch:
              fail("ENV_POLICY_REF_NOT_ADMITTED")

          print("ENV_POLICY_PASS %s %s" % (name, ref))
          PYEOF
EOF
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/env-policy-assert.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/env-policy-assert.yml
git commit -m "L2-T173: environment deployment branch and tag policy assertion (D91)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/env-policy-assert.yml'))"; echo $?` | exactly `0` |
| A2 | The five failure tokens are present | `for t in ENV_POLICY_INPUT_UNRESOLVED ENV_POLICY_UNREADABLE ENV_POLICY_ABSENT ENV_POLICY_TOO_WIDE ENV_POLICY_REF_NOT_ADMITTED; do grep -q "$t" .github/workflows/env-policy-assert.yml \|\| echo "MISSING $t"; done` | prints nothing |
| A3 | Environment names are exactly the three of §33.4 | `grep -c 'development\|staging\|production) ;;' .github/workflows/env-policy-assert.yml` | exactly `1` |
| A4 | `protected_branches: true` is refused as too wide (§33.4) | `grep -c 'ENV_POLICY_TOO_WIDE' .github/workflows/env-policy-assert.yml` | exactly `1` |
| A5 | No `if:`, no path filter (S7) | `grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/env-policy-assert.yml` | exactly `0` |
| A6 | This workflow configures nothing — read-only API verbs only | `grep -cE 'gh api .*(-X |--method )(POST|PUT|PATCH|DELETE)' .github/workflows/env-policy-assert.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/env-policy-assert.yml'))" \
 && test "$(grep -cE 'gh api .*(-X |--method )(POST|PUT|PATCH|DELETE)' .github/workflows/env-policy-assert.yml)" = "0" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/env-policy-assert.yml)" = "0" \
 && for t in ENV_POLICY_INPUT_UNRESOLVED ENV_POLICY_UNREADABLE ENV_POLICY_ABSENT ENV_POLICY_TOO_WIDE ENV_POLICY_REF_NOT_ADMITTED ENV_POLICY_PASS; do \
      grep -q "$t" .github/workflows/env-policy-assert.yml || exit 1; done \
 && echo "L2-T173 OK" || echo "L2-T173 FAIL"
```
Correct output: the single line `L2-T173 OK`.

**STOP rule:** A6 exists because charter §4.4 assigns the *application* of deployment branch policies to Lane 5. If completing this task appears to require creating or updating a policy, STOP under `S2` — writing an environment policy from an L2 workflow is a foreign-path act performed through an API instead of a file, and it is still a violation.

---

### L2-T174 — The workflow-identity gate (P3-A)

**Size:** L  **Depends on:** `L2-T170`

**Creates:** `.github/workflows/workflow-identity-gate.yml`

This is the production-approval mechanism of record. §27.2 (L2571): *"**The workflow-identity gate is the mechanism of record.** The deploy workflow itself verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell. The approval event is a recorded artifact in the records store (Section 97), and self-review is mechanically detected by comparing the approval actor with the triggering actor."* §11.4 (L881) and D73 (L10156) say the same thing from the plan-tier side: environment required reviewers are Enterprise-only on private repositories and are *"an optional strengthening ... never the mechanism the estate depends on"*. §33.4 (L2911) repeats it a third time. There is no fallback branch in this file, because there is no fallback in the specification.

Four facts fix the shape of the gate:

1. The approval is a record in `records/deployments/` (§97.2, L8848) carrying `approved_by`, `approval_event` and `digest` (§97.2 sample record, L8916–8925). The gate reads it; it never asks a human.
2. The comparison is `approved_by` against the deploying identity, both resolved to `people.yaml` ids. Comparing raw GitHub logins would let one person approve as themselves and deploy as a second login.
3. The exact failure string on a self-approval is `APPROVER_EQUALS_DEPLOYER`, fixed by charter **DoD-04**. It is never reworded.
4. §27 (L2551) makes the gate fail closed while an open verification-block record exists. That store is unresolved (**D-L2-08**), so the step is present and exits non-zero — never skipped.

**Step order is load-bearing.** The verification-block step runs **last**. It is the one step of this gate that is a fail-closed stub, so putting it first would mask every other refusal behind it and make `APPROVER_EQUALS_DEPLOYER` unprovable. Identity comparison is the most specific refusal and therefore comes first among the checks.

**Secret parameter names are parameter names, not contract values.** `REGISTRY_READ_TOKEN` and `RECORDS_READ_TOKEN` are the names this reusable workflow's `workflow_call` block declares. The caller maps the repository secret named by `registry_read_secret_name` onto the first; `RECORDS_READ_TOKEN` is the read-only records-repository secret this lane already places on L5 (§8 below). Nothing here reads a contract key at run time.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
mkdir -p .github/workflows
cat > .github/workflows/workflow-identity-gate.yml <<'EOF'
name: workflow-identity-gate
# =====================================================================
# THE WORKFLOW-IDENTITY GATE — THE PRODUCTION-APPROVAL MECHANISM OF RECORD.
# Spec: Section 27.2 (lines 2567-2576); Section 11.4 table row (line 881);
#       Section 33.4 (line 2911); D73 (line 10156).
# Charter DoD-04 fixes the self-approval failure string as APPROVER_EQUALS_DEPLOYER.
#
# This gate is NOT a fallback for a missing Enterprise feature. Environment
# required reviewers are an optional strengthening (D73) and are never the
# mechanism this estate depends on. There is therefore no branch in this file
# that defers to them, and none may be added.
#
# The rollback workflow is exempt from THIS gate and from nothing else
# (Section 27.2 line 2575; D52 line 10120). The exemption is declared in
# templates/workflows/rollback-exemption.yaml and asserted by
# tools/evidence/assert-privileged-workflows.py.
#
# NO `if:` and NO path filter anywhere in this file (Section 33.2, line 2860).
# =====================================================================
on:
  workflow_call:
    inputs:
      product:
        description: 'The product slug the deployment record is keyed on.'
        required: true
        type: string
      digest:
        description: >-
          The artifact identity about to be deployed. sha256:<64 hex>, or
          platform-rebuild:v1:<64 hex> for an S18 product (D78, line 10161).
        required: true
        type: string
      deploying_actor:
        description: 'The caller passes ${{ github.actor }}. Never a literal.'
        required: true
        type: string
      registry_ref:
        description: 'Immutable control-plane ref (full 40-char SHA) carrying people.yaml.'
        required: true
        type: string
      environment_name:
        description: 'development | staging | production.'
        required: true
        type: string
    outputs:
      approver_id:
        description: 'people.yaml id of the approving identity.'
        value: ${{ jobs.workflow-identity-gate.outputs.approver_id }}
      approval_record:
        description: 'Path of the production-approval record that satisfied the gate.'
        value: ${{ jobs.workflow-identity-gate.outputs.approval_record }}
    secrets:
      REGISTRY_READ_TOKEN:
        required: true
      RECORDS_READ_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  workflow-identity-gate:
    name: workflow-identity-gate
    runs-on: ubuntu-latest
    timeout-minutes: 10
    outputs:
      approver_id: ${{ steps.compare.outputs.approver_id }}
      approval_record: ${{ steps.compare.outputs.approval_record }}
    steps:
      - name: Validate inputs — fail closed on anything unrecognised
        env:
          PRODUCT: ${{ inputs.product }}
          DIGEST: ${{ inputs.digest }}
          DEPLOYING_ACTOR: ${{ inputs.deploying_actor }}
          REGISTRY_REF: ${{ inputs.registry_ref }}
          ENVIRONMENT_NAME: ${{ inputs.environment_name }}
        run: |
          set -euo pipefail
          if [ -z "${PRODUCT}" ] || [ -z "${DIGEST}" ] || [ -z "${DEPLOYING_ACTOR}" ]; then
            echo "IDENTITY_GATE_INPUT_UNRESOLVED"; exit 1
          fi
          echo "${REGISTRY_REF}" | grep -qE '^[0-9a-f]{40}$' \
            || { echo "IDENTITY_GATE_INPUT_UNRESOLVED"; exit 1; }
          case "${ENVIRONMENT_NAME}" in
            development|staging|production) ;;
            *) echo "IDENTITY_GATE_INPUT_UNRESOLVED"; exit 1 ;;
          esac
          echo "${DIGEST}" \
            | grep -qE '^(sha256:[0-9a-f]{64}|platform-rebuild:v1:[0-9a-f]{64})$' \
            || { echo "IDENTITY_GATE_INPUT_UNRESOLVED"; exit 1; }
          echo "IDENTITY_GATE_INPUT_OK"

      - name: Fetch people.yaml at the pinned control-plane ref
        env:
          GH_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}
          REGISTRY_REF: ${{ inputs.registry_ref }}
        run: |
          set -euo pipefail
          if ! gh api "repos/@@SLUG@@/contents/people.yaml?ref=${REGISTRY_REF}" \
                 -H "Accept: application/vnd.github.raw" > people.yaml 2>fetch.err; then
            cat fetch.err >&2
            echo "IDENTITY_GATE_REGISTRY_UNREADABLE"; exit 1
          fi
          if [ ! -s people.yaml ]; then
            echo "IDENTITY_GATE_REGISTRY_UNREADABLE"; exit 1
          fi
          echo "IDENTITY_GATE_REGISTRY_READ_OK"

      - name: Fetch every production-approval record for this product
        env:
          GH_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
          APPROVAL_GLOB: '@@APPROVALGLOB@@'
          RECORDS_SLUG: '@@RECORDSSLUG@@'
        run: |
          set -euo pipefail
          APPROVAL_DIR="$(dirname "${APPROVAL_GLOB}")"
          mkdir -p approvals
          if ! gh api --paginate "repos/${RECORDS_SLUG}/contents/${APPROVAL_DIR}" \
                 --jq '.[] | select(.type=="file") | .path' > paths.txt 2>records.err; then
            cat records.err >&2
            echo "IDENTITY_GATE_RECORDS_UNREADABLE"; exit 1
          fi
          # An empty store is a readable store. It is NOT an error here; it is
          # NO_APPROVAL_RECORD in the comparison step, which is the specific refusal.
          n=0
          while IFS= read -r p; do
            case "${p}" in *.yaml|*.yml) ;; *) continue ;; esac
            safe="$(printf '%s' "${p}" | tr '/' '_')"
            if ! gh api "repos/${RECORDS_SLUG}/contents/${p}" \
                   -H "Accept: application/vnd.github.raw" > "approvals/${safe}" 2>one.err; then
              cat one.err >&2
              echo "IDENTITY_GATE_RECORDS_UNREADABLE"; exit 1
            fi
            n=$((n+1))
          done < paths.txt
          echo "IDENTITY_GATE_RECORDS_READ_OK ${n}"

      - name: Compare the approving identity with the deploying identity
        id: compare
        env:
          PRODUCT: ${{ inputs.product }}
          DIGEST: ${{ inputs.digest }}
          DEPLOYING_ACTOR: ${{ inputs.deploying_actor }}
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          python3 - <<'PYEOF'
          import glob, os, sys, yaml

          def fail(token):
              print(token)
              sys.exit(1)

          # ---- the registry -------------------------------------------------
          try:
              with open("people.yaml", "r", encoding="utf-8") as fh:
                  reg = yaml.safe_load(fh)
          except Exception:
              fail("IDENTITY_GATE_REGISTRY_UNREADABLE")
          if not isinstance(reg, dict) or not isinstance(reg.get("people"), list):
              fail("IDENTITY_GATE_REGISTRY_UNREADABLE")

          by_login, by_id = {}, {}
          for p in reg["people"]:
              if not isinstance(p, dict):
                  continue
              pid = str(p.get("id", "")).strip()
              login = str(p.get("github_login", "")).strip().lower()
              if pid:
                  by_id[pid] = p
              if login:
                  by_login[login] = p

          # ---- the deploying identity ---------------------------------------
          # Section 27.2 line 2576: "The deploying actor is the pipeline; the
          # approving actor is a person." An unresolvable deploying actor is a
          # gate that cannot tell, and Section 27.2 line 2571 says a gate that
          # cannot tell fails closed.
          actor = os.environ["DEPLOYING_ACTOR"].strip().lower()
          deployer = by_login.get(actor)
          deployer_id = str(deployer.get("id", "")).strip() if isinstance(deployer, dict) else ""
          if not deployer_id:
              fail("DEPLOYER_UNRESOLVED")

          # ---- the approval records -----------------------------------------
          product = os.environ["PRODUCT"].strip()
          digest = os.environ["DIGEST"].strip()

          records = []
          for path in sorted(glob.glob("approvals/*")):
              try:
                  with open(path, "r", encoding="utf-8") as fh:
                      doc = yaml.safe_load(fh)
              except Exception:
                  fail("IDENTITY_GATE_RECORDS_UNREADABLE")
              if isinstance(doc, dict):
                  records.append((path, doc))

          for_product = [
              (path, d) for path, d in records
              if str(d.get("product", "")).strip() == product
          ]
          if not for_product:
              fail("NO_APPROVAL_RECORD")

          # An approval record is a PRODUCTION-APPROVAL record only when it names
          # an approver and the approval event that granted it (Section 97.2,
          # lines 8916-8925). A record with neither is a deployment note.
          approvals = [
              (path, d) for path, d in for_product
              if str(d.get("approved_by", "")).strip()
              and str(d.get("approval_event", "")).strip()
          ]
          if not approvals:
              fail("NO_APPROVAL_RECORD")

          matching = [
              (path, d) for path, d in approvals
              if str(d.get("digest", "")).strip() == digest
          ]
          # The product has approvals, but none for THIS artifact identity. That
          # is a different failure from having none at all, and it is the failure
          # a digest substitution produces.
          if not matching:
              fail("APPROVAL_DIGEST_MISMATCH")

          # ---- the comparison ------------------------------------------------
          satisfying = None
          for path, d in matching:
              approver_ref = str(d.get("approved_by", "")).strip()
              approver = by_id.get(approver_ref) or by_login.get(approver_ref.lower())
              if not isinstance(approver, dict):
                  # An approver who is not in people.yaml is an approver the gate
                  # cannot tell apart from the deployer. Fail closed.
                  fail("APPROVER_UNRESOLVED")
              approver_id = str(approver.get("id", "")).strip()
              if not approver_id:
                  fail("APPROVER_UNRESOLVED")
              # Section 27.2, and charter DoD-04. This string is never reworded.
              if approver_id == deployer_id:
                  fail("APPROVER_EQUALS_DEPLOYER")
              held = approver.get("capabilities") or []
              if not isinstance(held, list):
                  fail("IDENTITY_GATE_REGISTRY_UNREADABLE")
              if "production-approval" not in [str(c).strip() for c in held]:
                  fail("APPROVER_NOT_CAPABLE")
              satisfying = (path, approver_id)
              break

          if satisfying is None:
              fail("NO_APPROVAL_RECORD")

          path, approver_id = satisfying
          with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
              out.write("approver_id=%s\n" % approver_id)
              out.write("approval_record=%s\n" % path)
          print("IDENTITY_GATE_PASS approver=%s deployer=%s" % (approver_id, deployer_id))
          PYEOF

      - name: Refuse while an open verification block exists
        env:
          PRODUCT: ${{ inputs.product }}
          VERIFICATION_BLOCK_STORE: 'records/verification-blocks/'
          GH_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
          RECORDS_SLUG: '@@RECORDSSLUG@@'
        run: |
          set -euo pipefail
          # REG-020 resolved by FD-053 (2026-09-06): records/verification-blocks/
          # Section 27 line 2551: production approval and deploy-production.yml
          # fail closed while an open verification-block record exists for the
          # change or the product.
          # It runs LAST so that every more specific refusal above is provable.
          # if [ -z "${VERIFICATION_BLOCK_STORE}" ] || [ "${VERIFICATION_BLOCK_STORE}" = "UNRESOLVED" ]; then
          #   echo "VERIFICATION_BLOCK_STORE_UNRESOLVED"; exit 1
          # fi
          if ! gh api --paginate "repos/${RECORDS_SLUG}/contents/${VERIFICATION_BLOCK_STORE}" \
                 --jq '.[] | select(.type=="file") | .path' > blocks.txt 2>blk.err; then
            cat blk.err >&2
            echo "VERIFICATION_BLOCK_STORE_UNREADABLE"; exit 1
          fi
          OPEN=0
          while IFS= read -r p; do
            case "${p}" in *.yaml|*.yml) ;; *) continue ;; esac
            gh api "repos/${RECORDS_SLUG}/contents/${p}" \
              -H "Accept: application/vnd.github.raw" > blk.yaml 2>/dev/null \
              || { echo "VERIFICATION_BLOCK_STORE_UNREADABLE"; exit 1; }
            if grep -qE "^product:[[:space:]]*${PRODUCT}[[:space:]]*$" blk.yaml \
               && grep -qE '^state:[[:space:]]*open[[:space:]]*$' blk.yaml; then
              echo "OPEN BLOCK: ${p}"
              OPEN=$((OPEN+1))
            fi
          done < blocks.txt
          if [ "${OPEN}" -gt 0 ]; then
            echo "VERIFICATION_BLOCK_OPEN"; exit 1
          fi
          echo "VERIFICATION_BLOCK_CLEAR"
EOF
sed -i "s|@@SLUG@@|${CONTROL_PLANE_SLUG}|g; \
        s|@@RECORDSSLUG@@|${RECORDS_REPO_SLUG}|g; \
        s|@@APPROVALGLOB@@|${PRODUCTION_APPROVAL_RECORD_GLOB}|g" \
  .github/workflows/workflow-identity-gate.yml
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/workflow-identity-gate.yml
git commit -m "L2-T174: workflow-identity gate, the production-approval mechanism of record (Section 27.2, D73)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'))"; echo $?` | exactly `0` |
| A2 | No placeholder survives substitution | `grep -c '@@' .github/workflows/workflow-identity-gate.yml` | exactly `0` |
| A3 | The DoD-04 string is present, exactly once, exactly as spelled | `grep -c 'APPROVER_EQUALS_DEPLOYER' .github/workflows/workflow-identity-gate.yml` | exactly `1` |
| A4 | Every failure token is present | `for t in IDENTITY_GATE_INPUT_UNRESOLVED IDENTITY_GATE_REGISTRY_UNREADABLE IDENTITY_GATE_RECORDS_UNREADABLE DEPLOYER_UNRESOLVED APPROVER_UNRESOLVED NO_APPROVAL_RECORD APPROVAL_DIGEST_MISMATCH APPROVER_EQUALS_DEPLOYER APPROVER_NOT_CAPABLE VERIFICATION_BLOCK_STORE_UNRESOLVED VERIFICATION_BLOCK_OPEN; do grep -q "$t" .github/workflows/workflow-identity-gate.yml \|\| echo "MISSING $t"; done` | prints nothing |
| A5 | The verification-block step is the last step of the job | `python3 -c "import yaml;d=yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'));print(d['jobs']['workflow-identity-gate']['steps'][-1]['name'])"` | exactly `Refuse while an open verification block exists` |
| A6 | No `if:`, no path filter, no `continue-on-error` (S6, S7) | `grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/workflow-identity-gate.yml` | exactly `0` |
| A7 | The gate names no Enterprise fallback (D73) | `grep -ciE 'required.reviewer|environment protection rule' .github/workflows/workflow-identity-gate.yml` | exactly `0` |
| A8 | Read-only API verbs only | `grep -cE 'gh api .*(-X |--method )(POST|PUT|PATCH|DELETE)' .github/workflows/workflow-identity-gate.yml` | exactly `0` |
| A9 | Least-privilege token | `grep -A1 '^permissions:' .github/workflows/workflow-identity-gate.yml \| grep -c 'contents: read'` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'))" \
 && test "$(grep -c '@@' .github/workflows/workflow-identity-gate.yml)" = "0" \
 && test "$(grep -c 'APPROVER_EQUALS_DEPLOYER' .github/workflows/workflow-identity-gate.yml)" = "1" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/workflow-identity-gate.yml)" = "0" \
 && test "$(grep -ciE 'required.reviewer|environment protection rule' .github/workflows/workflow-identity-gate.yml)" = "0" \
 && test "$(python3 -c "import yaml;d=yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'));print(d['jobs']['workflow-identity-gate']['steps'][-1]['name'])")" \
      = "Refuse while an open verification block exists" \
 && for t in IDENTITY_GATE_INPUT_UNRESOLVED IDENTITY_GATE_REGISTRY_UNREADABLE \
             IDENTITY_GATE_RECORDS_UNREADABLE DEPLOYER_UNRESOLVED APPROVER_UNRESOLVED \
             NO_APPROVAL_RECORD APPROVAL_DIGEST_MISMATCH APPROVER_NOT_CAPABLE \
             VERIFICATION_BLOCK_STORE_UNRESOLVED VERIFICATION_BLOCK_OPEN IDENTITY_GATE_PASS; do \
      grep -q "$t" .github/workflows/workflow-identity-gate.yml || exit 1; done \
 && echo "L2-T174 OK" || echo "L2-T174 FAIL"
```
Correct output: the single line `L2-T174 OK`.

**STOP rule:** if any acceptance row fails, **do not repair it by widening the gate.** In particular: do not make `DEPLOYER_UNRESOLVED` or `APPROVER_UNRESOLVED` a pass, do not fall back to comparing GitHub logins when a `people.yaml` id is missing, and do not move the verification-block step earlier to "unblock testing". Each of those turns §27.2's *"fails closed if it cannot tell"* into a gate that guesses. STOP under **S6** and file the blocker citing §27.2 line 2571. If the failure is that `VERIFICATION_BLOCK_STORE` resolves to a real path that returns 404, that is `VERIFICATION_BLOCK_STORE_UNREADABLE` and it is correct behaviour — file it against **D-L2-08**, do not delete the step.

---

### L2-T175 — The production gate chain

**Size:** M  **Depends on:** `L2-T171`, `L2-T172`, `L2-T173`, `L2-T174`

**Creates:** `.github/workflows/production-gate-chain.yml`

The four gates are useless individually if a caller can choose which of them to run. This task composes them in one fixed order behind one `uses:` reference, so that wiring a privileged workflow is a single call and dropping a gate is a diff on a control-plane file — which §53.1 (L4675) already classifies as Blocking drift.

The order is fixed and is not an arrangement of convenience:

| Position | Gate | Why here |
|---|---|---|
| 1 | `actor-gate` | §37.3 (L3267) — *"the first step of every privileged workflow"*. Nothing else runs until the dispatching identity is a capable human |
| 2 | `runner-tier-assert` | D87 (L10191) — the tier must be proven before any credential can materialise into the job |
| 3 | `env-policy-assert` | D91 (L10184) — the ref restriction must be proven before the environment's secrets are requested |
| 4 | `workflow-identity-gate` | §27.2 (L2571) — the most expensive gate and the one whose refusal is most specific, so it runs against an already-trusted actor, runner and ref |

Every job after the first carries `needs:` on its predecessor, so the order is enforced by the scheduler and not by hope.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
cat > .github/workflows/production-gate-chain.yml <<'EOF'
name: production-gate-chain
# =====================================================================
# THE PRODUCTION GATE CHAIN — fixed-order composition of the four Phase 3 gates.
# Spec: Section 37.3 (line 3267) actor gate first; D87 (line 10180) runner tier;
#       D91 (line 10184) deployment branch and tag policy;
#       Section 27.2 (line 2571) workflow-identity gate.
#
# The order below is FIXED. A caller cannot select a subset: there is one
# entry point and it runs all four. Removing a gate is a diff on this file and
# is Blocking drift (Section 53.1, line 4675).
#
# NO `if:` and NO path filter anywhere in this file (Section 33.2, line 2860).
# =====================================================================
on:
  workflow_call:
    inputs:
      product:
        description: 'The product slug.'
        required: true
        type: string
      digest:
        description: 'The artifact identity about to be deployed.'
        required: true
        type: string
      actor:
        description: 'The caller passes ${{ github.actor }}.'
        required: true
        type: string
      required_capabilities:
        description: 'Comma-separated subset of production-approval, incident-response, devops.'
        required: true
        type: string
      registry_ref:
        description: 'Immutable control-plane ref (full 40-char SHA) carrying people.yaml.'
        required: true
        type: string
      environment_name:
        description: 'development | staging | production.'
        required: true
        type: string
      target_repo:
        description: 'owner/repo whose environment is being asserted.'
        required: true
        type: string
      deploy_ref:
        description: 'The caller passes ${{ github.ref }}.'
        required: true
        type: string
      runner_label:
        description: 'The SAME label the caller''s privileged job uses.'
        required: true
        type: string
      privileged_self_hosted_declared:
        description: 'true only where the product contract records the D87 exception.'
        required: true
        type: string
    outputs:
      person_id:
        description: 'people.yaml id of the gated dispatching actor.'
        value: ${{ jobs.actor-gate.outputs.person_id }}
      approver_id:
        description: 'people.yaml id of the approving identity.'
        value: ${{ jobs.workflow-identity-gate.outputs.approver_id }}
      approval_record:
        description: 'Path of the production-approval record that satisfied the gate.'
        value: ${{ jobs.workflow-identity-gate.outputs.approval_record }}
    secrets:
      REGISTRY_READ_TOKEN:
        required: true
      RECORDS_READ_TOKEN:
        required: true
      ENV_POLICY_READ_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  # ---- 1. Section 37.3: the actor gate is first. ----------------------------
  actor-gate:
    name: actor-gate
    uses: @@SLUG@@/.github/workflows/actor-gate.yml@@@TAG@@
    with:
      required_capabilities: ${{ inputs.required_capabilities }}
      actor: ${{ inputs.actor }}
      registry_ref: ${{ inputs.registry_ref }}
      machine_dispatch_class: none
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  # ---- 2. D87: prove the runner tier before any credential materialises. ----
  runner-tier-assert:
    name: runner-tier-assert
    needs: actor-gate
    uses: @@SLUG@@/.github/workflows/runner-tier-assert.yml@@@TAG@@
    with:
      runner_label: ${{ inputs.runner_label }}
      privileged_self_hosted_declared: ${{ inputs.privileged_self_hosted_declared }}

  # ---- 3. D91: prove the ref restriction before the environment is touched. -
  env-policy-assert:
    name: env-policy-assert
    needs: runner-tier-assert
    uses: @@SLUG@@/.github/workflows/env-policy-assert.yml@@@TAG@@
    with:
      environment_name: ${{ inputs.environment_name }}
      target_repo: ${{ inputs.target_repo }}
      deploy_ref: ${{ inputs.deploy_ref }}
    secrets:
      ENV_POLICY_READ_TOKEN: ${{ secrets.ENV_POLICY_READ_TOKEN }}

  # ---- 4. Section 27.2: the production-approval mechanism of record. --------
  workflow-identity-gate:
    name: workflow-identity-gate
    needs: env-policy-assert
    uses: @@SLUG@@/.github/workflows/workflow-identity-gate.yml@@@TAG@@
    with:
      product: ${{ inputs.product }}
      digest: ${{ inputs.digest }}
      deploying_actor: ${{ inputs.actor }}
      registry_ref: ${{ inputs.registry_ref }}
      environment_name: ${{ inputs.environment_name }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}
      RECORDS_READ_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
EOF
sed -i "s|@@SLUG@@|${CONTROL_PLANE_SLUG}|g; s|@@@TAG@@|@${WORKFLOWS_TAG}|g" \
  .github/workflows/production-gate-chain.yml
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/production-gate-chain.yml
git commit -m "L2-T175: fixed-order production gate chain (Sections 27.2, 37.3; D87, D91)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))"; echo $?` | exactly `0` |
| A2 | No placeholder survives | `grep -c '@@' .github/workflows/production-gate-chain.yml` | exactly `0` |
| A3 | Exactly four jobs, in the fixed order | `python3 -c "import yaml;print(','.join(yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))['jobs']))"` | exactly `actor-gate,runner-tier-assert,env-policy-assert,workflow-identity-gate` |
| A4 | Each job after the first `needs:` its predecessor | see SELF-VERIFY | exactly `ORDER_ENFORCED` |
| A5 | Every `uses:` is pinned to the contract tag | `grep -c "@${WORKFLOWS_TAG}$" .github/workflows/production-gate-chain.yml` | exactly `4` |
| A6 | No branch reference in any `uses:` (§33.3) | `grep -cE 'uses:.*@(main|integration|refs/heads)' .github/workflows/production-gate-chain.yml` | exactly `0` |
| A7 | No `if:`, no path filter, no `continue-on-error` | `grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/production-gate-chain.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))
order = list(d['jobs'])
want = ['actor-gate', 'runner-tier-assert', 'env-policy-assert', 'workflow-identity-gate']
ok = order == want
for i in range(1, len(want)):
    n = d['jobs'][want[i]].get('needs')
    n = [n] if isinstance(n, str) else (n or [])
    ok = ok and n == [want[i-1]]
print("ORDER_ENFORCED" if ok else "ORDER_BROKEN")
PY
test "$(python3 -c "import yaml;print(','.join(yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))['jobs']))")" \
     = "actor-gate,runner-tier-assert,env-policy-assert,workflow-identity-gate" \
 && test "$(grep -c "@${WORKFLOWS_TAG}\$" .github/workflows/production-gate-chain.yml)" = "4" \
 && test "$(grep -cE 'uses:.*@(main|integration|refs/heads)' .github/workflows/production-gate-chain.yml)" = "0" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/production-gate-chain.yml)" = "0" \
 && test "$(grep -c '@@' .github/workflows/production-gate-chain.yml)" = "0" \
 && echo "L2-T175 OK" || echo "L2-T175 FAIL"
```
Correct output: the line `ORDER_ENFORCED` followed by the line `L2-T175 OK`.

**STOP rule:** if A3 or A4 fails, the composition has been reordered or a `needs:` has been dropped. Reordering the chain is not a style question — an `env-policy-assert` that runs before the actor gate has already let an unauthorised identity make three authenticated API calls. STOP under **S6**. If A5 reports fewer than `4`, a `uses:` reference is unpinned or pinned to something other than `WORKFLOWS_TAG`; §33.3 forbids consuming a shared workflow by branch, so STOP under `S1` and re-run `L2-T170` rather than editing the reference by hand.

---

### L2-T176 — The rollback reusable workflow (P3-B)

> **NOTE:** L2-T176 is the authoritative source for `.github/workflows/rollback.yml`. L2-T133 is verification-only.

**Size:** L  **Depends on:** `L2-T171`, `L2-T172`, `L2-T173`

**Creates:** `.github/workflows/rollback.yml`

§27.2 (L2575) is the whole task, and it is quoted here in full because every clause becomes a step:

> *"**Rollback is exempt from production approval.** Redeploying an artifact digest that already carries a production-approval record runs through a dedicated rollback workflow that is exempt from the workflow-identity production-approval gate — and, where the Enterprise strengthening is bought, from environment required reviewers: the digest was approved once and is being restored, not newly released. The rollback workflow defaults to the previous approved-and-deployed digest, displays it alongside its deploy date and whether a migration boundary lies between it and the current digest, and requires only confirmation to run **from a human identity holding `incident-response` or `production-approval`**. The actor gate (Section 37.3) is the one check this exemption does not lift ... Each run of the rollback workflow is recorded as an exceptional authorisation and audited (Section 42.3)."*

**What the exemption lifts, and what it does not.** This is the single most misreadable sentence in the phase, so it is tabulated rather than described:

| Gate | Applies to rollback? | Authority |
|---|---|---|
| `workflow-identity-gate` (approver ≠ deployer) | **No — exempt** | §27.2 L2575; D52 L10120 |
| Environment required reviewers, where bought | **No — exempt** | §27.2 L2575 |
| `actor-gate` | **Yes** — §27.2 names it as *"the one check this exemption does not lift"* | §27.2 L2575; §37.3 L3267 |
| `runner-tier-assert` | **Yes** — the rollback workflow is in D87's closed privileged set | D87 L10191; §39.5 L3591 |
| `env-policy-assert` | **Yes** — it touches production secrets from a ref | D91 L10184; §33.4 L2911 |
| Prior-approval assertion (the digest was approved once) | **Yes** — it is the precondition of the exemption itself | §27.2 L2575 |
| Exceptional-authorisation record | **Yes** — §27.2 requires one per run | §27.2 L2575; §42.3 L3788 |

The exemption is therefore *narrow and conditional*: it is only available for a digest that already carries a production-approval record, which the workflow proves before it proceeds. An exemption granted to an unapproved digest would not be an exemption; it would be an unapproved production deployment.

**The redeploy leg is a declared seam, not a gap.** This phase builds the rollback workflow's gate, target-resolution and record legs. The step that re-releases the digest belongs to `deploy-production.yml`, which is authored by the later Lane 2 phase that owns it (charter DoD-01), and is wired into the per-product template by `tools/evidence/apply-production-gates.py`. The seam is named in §8 below and asserted by `L2-T571`; it is never a to-do inside a workflow file.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
cat > .github/workflows/rollback.yml <<'EOF'
name: rollback
# =====================================================================
# THE ROLLBACK WORKFLOW — Section 27.2 (line 2575); D52 (line 10120);
# Section 42.3 response flow (lines 3788-3812); Section 47.2 (lines 4227-4232);
# invariant 27 (line 9488): "Rollback is preferred to hotfix, and requires no
# prior approval during a SEV-1."
#
# THIS WORKFLOW DELIBERATELY DOES NOT CALL workflow-identity-gate.yml.
# That absence is the D52 exemption. It is DECLARED, machine-readably, in
# templates/workflows/rollback-exemption.yaml and asserted by
# tools/evidence/assert-privileged-workflows.py. An undeclared absence is a
# missing gate; a declared one is an exemption. Do not add the gate back, and
# do not remove any other gate on the strength of the exemption.
#
# Section 27.2: "The actor gate (Section 37.3) is the one check this exemption
# does not lift." It runs first, below, and it accepts machine_dispatch_class
# `none` only.
#
# NO `if:` and NO path filter anywhere in this file (Section 33.2, line 2860).
# =====================================================================
on:
  workflow_call:
    inputs:
      product:
        description: 'The product slug.'
        required: true
        type: string
      current_digest:
        description: 'The artifact identity currently deployed to the target environment.'
        required: true
        type: string
      confirm_digest:
        description: >-
          Section 27.2: the workflow "requires only confirmation to run". The
          human retypes the digest the workflow resolved. A mismatch refuses.
        required: true
        type: string
      actor:
        description: 'The caller passes ${{ github.actor }}.'
        required: true
        type: string
      registry_ref:
        description: 'Immutable control-plane ref (full 40-char SHA) carrying people.yaml.'
        required: true
        type: string
      environment_name:
        description: 'development | staging | production.'
        required: true
        type: string
      target_repo:
        description: 'owner/repo being rolled back.'
        required: true
        type: string
      deploy_ref:
        description: 'The caller passes ${{ github.ref }}.'
        required: true
        type: string
      runner_label:
        description: 'The SAME label the caller''s privileged job uses.'
        required: true
        type: string
      privileged_self_hosted_declared:
        description: 'true only where the product contract records the D87 exception.'
        required: true
        type: string
      authorisation_reason:
        description: >-
          Section 47.2: SEV-1 needs no prior authorisation but the exception
          record is still filed. Free text, required, never empty.
        required: true
        type: string
    outputs:
      target_digest:
        description: 'The previous approved-and-deployed digest this run restores.'
        value: ${{ jobs.rollback-target.outputs.target_digest }}
      migration_boundary:
        description: 'true | false — whether a migration boundary lies in the window.'
        value: ${{ jobs.rollback-target.outputs.migration_boundary }}
      authorised:
        description: 'yes — emitted only when every gate above passed.'
        value: ${{ jobs.rollback-record.outputs.authorised }}
    secrets:
      REGISTRY_READ_TOKEN:
        required: true
      RECORDS_READ_TOKEN:
        required: true
      RECORDS_WRITER_TOKEN:
        required: true
      ENV_POLICY_READ_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  # ---- Section 27.2: the one check the exemption does not lift. -------------
  actor-gate:
    name: actor-gate
    uses: @@SLUG@@/.github/workflows/actor-gate.yml@@@TAG@@
    with:
      required_capabilities: incident-response,production-approval
      actor: ${{ inputs.actor }}
      registry_ref: ${{ inputs.registry_ref }}
      machine_dispatch_class: none
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  # ---- D87: the rollback workflow is in the closed privileged set. ----------
  runner-tier-assert:
    name: runner-tier-assert
    needs: actor-gate
    uses: @@SLUG@@/.github/workflows/runner-tier-assert.yml@@@TAG@@
    with:
      runner_label: ${{ inputs.runner_label }}
      privileged_self_hosted_declared: ${{ inputs.privileged_self_hosted_declared }}

  # ---- D91: it reaches production secrets, so the ref restriction holds. ----
  env-policy-assert:
    name: env-policy-assert
    needs: runner-tier-assert
    uses: @@SLUG@@/.github/workflows/env-policy-assert.yml@@@TAG@@
    with:
      environment_name: ${{ inputs.environment_name }}
      target_repo: ${{ inputs.target_repo }}
      deploy_ref: ${{ inputs.deploy_ref }}
    secrets:
      ENV_POLICY_READ_TOKEN: ${{ secrets.ENV_POLICY_READ_TOKEN }}

  rollback-target:
    name: rollback-target
    needs: env-policy-assert
    runs-on: ${{ inputs.runner_label }}
    timeout-minutes: 10
    outputs:
      target_digest: ${{ steps.resolve.outputs.target_digest }}
      target_deployed_at: ${{ steps.resolve.outputs.target_deployed_at }}
      migration_boundary: ${{ steps.resolve.outputs.migration_boundary }}
    steps:
      - name: Validate inputs — fail closed on anything unrecognised
        env:
          PRODUCT: ${{ inputs.product }}
          CURRENT_DIGEST: ${{ inputs.current_digest }}
          CONFIRM_DIGEST: ${{ inputs.confirm_digest }}
          AUTHORISATION_REASON: ${{ inputs.authorisation_reason }}
        run: |
          set -euo pipefail
          if [ -z "${PRODUCT}" ] || [ -z "${CONFIRM_DIGEST}" ] || [ -z "${AUTHORISATION_REASON}" ]; then
            echo "ROLLBACK_INPUT_UNRESOLVED"; exit 1
          fi
          for d in "${CURRENT_DIGEST}" "${CONFIRM_DIGEST}"; do
            echo "${d}" \
              | grep -qE '^(sha256:[0-9a-f]{64}|platform-rebuild:v1:[0-9a-f]{64})$' \
              || { echo "ROLLBACK_INPUT_UNRESOLVED"; exit 1; }
          done
          echo "ROLLBACK_INPUT_OK"

      - name: Fetch every deployment record for this product
        env:
          GH_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
          APPROVAL_GLOB: '@@APPROVALGLOB@@'
          RECORDS_SLUG: '@@RECORDSSLUG@@'
        run: |
          set -euo pipefail
          RECORD_DIR="$(dirname "${APPROVAL_GLOB}")"
          mkdir -p deployments
          if ! gh api --paginate "repos/${RECORDS_SLUG}/contents/${RECORD_DIR}" \
                 --jq '.[] | select(.type=="file") | .path' > paths.txt 2>rec.err; then
            cat rec.err >&2
            echo "ROLLBACK_RECORDS_UNREADABLE"; exit 1
          fi
          while IFS= read -r p; do
            case "${p}" in *.yaml|*.yml) ;; *) continue ;; esac
            safe="$(printf '%s' "${p}" | tr '/' '_')"
            if ! gh api "repos/${RECORDS_SLUG}/contents/${p}" \
                   -H "Accept: application/vnd.github.raw" > "deployments/${safe}" 2>one.err; then
              cat one.err >&2
              echo "ROLLBACK_RECORDS_UNREADABLE"; exit 1
            fi
          done < paths.txt
          echo "ROLLBACK_RECORDS_READ_OK"

      - name: Resolve the rollback target and the migration boundary
        id: resolve
        env:
          PRODUCT: ${{ inputs.product }}
          CURRENT_DIGEST: ${{ inputs.current_digest }}
          CONFIRM_DIGEST: ${{ inputs.confirm_digest }}
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          python3 - <<'PYEOF'
          import glob, os, sys, yaml

          def fail(token):
              print(token)
              sys.exit(1)

          product = os.environ["PRODUCT"].strip()
          current = os.environ["CURRENT_DIGEST"].strip()
          confirm = os.environ["CONFIRM_DIGEST"].strip()

          recs = []
          for path in sorted(glob.glob("deployments/*")):
              try:
                  with open(path, "r", encoding="utf-8") as fh:
                      doc = yaml.safe_load(fh)
              except Exception:
                  fail("ROLLBACK_RECORDS_UNREADABLE")
              if isinstance(doc, dict) and str(doc.get("product", "")).strip() == product:
                  recs.append((path, doc))

          if not recs:
              fail("ROLLBACK_DIGEST_NEVER_DEPLOYED")

          def when(d):
              v = d.get("timestamp") or d.get("deployed_at") or d.get("id")
              return str(v or "")

          # Newest last. A record with no orderable timestamp makes the ordering
          # a guess, and Section 64 resolves a guess as denial.
          for _, d in recs:
              if not when(d):
                  fail("ROLLBACK_TARGET_UNRESOLVED")
          recs.sort(key=lambda pd: when(pd[1]))

          approved = [
              (p, d) for p, d in recs
              if str(d.get("approved_by", "")).strip()
              and str(d.get("approval_event", "")).strip()
              and str(d.get("digest", "")).strip()
          ]
          if not approved:
              fail("ROLLBACK_DIGEST_NEVER_APPROVED")

          # Section 27.2: "defaults to the previous approved-and-deployed digest".
          # Previous means: the newest approved-and-deployed record whose digest
          # is not the one currently running.
          target = None
          for p, d in reversed(approved):
              if str(d.get("digest", "")).strip() != current:
                  target = (p, d)
                  break
          if target is None:
              fail("ROLLBACK_TARGET_UNRESOLVED")

          tpath, trec = target
          tdigest = str(trec.get("digest", "")).strip()
          tdeployed = when(trec)

          # Section 27.2: "requires only confirmation to run". The confirmation is
          # the resolved digest retyped. Anything else is a different rollback.
          if confirm != tdigest:
              print("RESOLVED TARGET: %s deployed %s (record %s)" % (tdigest, tdeployed, tpath))
              fail("ROLLBACK_CONFIRMATION_MISMATCH")

          # Section 27.2: "whether a migration boundary lies between it and the
          # current digest". The window is every deployment record strictly after
          # the target, up to and including the current digest.
          window, seen_target = [], False
          for p, d in recs:
              if not seen_target:
                  if p == tpath:
                      seen_target = True
                  continue
              window.append((p, d))
              if str(d.get("digest", "")).strip() == current:
                  break

          boundary = False
          for p, d in window:
              if "migration_applied" not in d:
                  # The field is Lane 4's (Section 8 below states the requirement).
                  # Without it the boundary cannot be told, and Section 27.2
                  # requires the workflow to display whether one lies in the
                  # window — not to shrug.
                  print("RECORD WITHOUT migration_applied: %s" % p)
                  fail("MIGRATION_BOUNDARY_UNRESOLVED")
              if d.get("migration_applied") is True:
                  boundary = True

          with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
              out.write("target_digest=%s\n" % tdigest)
              out.write("target_deployed_at=%s\n" % tdeployed)
              out.write("migration_boundary=%s\n" % ("true" if boundary else "false"))

          # Section 27.2: the workflow "displays it alongside its deploy date and
          # whether a migration boundary lies between it and the current digest".
          summary = os.environ.get("GITHUB_STEP_SUMMARY")
          lines = [
              "## Rollback target",
              "",
              "| Field | Value |",
              "| --- | --- |",
              "| Product | %s |" % product,
              "| Current digest | `%s` |" % current,
              "| Target digest | `%s` |" % tdigest,
              "| Target deployed | %s |" % tdeployed,
              "| Approval record | `%s` |" % tpath,
              "| Migration boundary in window | **%s** |" % ("YES" if boundary else "no"),
              "",
          ]
          if summary:
              with open(summary, "a", encoding="utf-8") as fh:
                  fh.write("\n".join(lines) + "\n")
          print("\n".join(lines))
          print("ROLLBACK_TARGET_OK %s boundary=%s" % (tdigest, "true" if boundary else "false"))
          PYEOF

  rollback-record:
    name: rollback-record
    needs: rollback-target
    runs-on: ${{ inputs.runner_label }}
    timeout-minutes: 10
    outputs:
      authorised: ${{ steps.record.outputs.authorised }}
    steps:
      - name: Write the exceptional-authorisation record and the event
        id: record
        env:
          GH_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
          PRODUCT: ${{ inputs.product }}
          ACTOR: ${{ inputs.actor }}
          CURRENT_DIGEST: ${{ inputs.current_digest }}
          TARGET_DIGEST: ${{ needs.rollback-target.outputs.target_digest }}
          MIGRATION_BOUNDARY: ${{ needs.rollback-target.outputs.migration_boundary }}
          AUTHORISATION_REASON: ${{ inputs.authorisation_reason }}
          EXCEPTIONAL_AUTH_STORE: '@@EXCAUTHSTORE@@'
          RECORDS_SLUG: '@@RECORDSSLUG@@'
        run: |
          set -euo pipefail
          # Section 27.2: "Each run of the rollback workflow is recorded as an
          # exceptional authorisation and audited (Section 42.3)."
          # Section 97.2 (line 8869) makes record and event writes REQUIRED,
          # FAILING steps, not trailing best-effort ones.
          # DECISION REQUIRED D-L2-10 has not published the store, so this step
          # is a FAIL-CLOSED STUB. It is present and it exits non-zero.
          if [ -z "${EXCEPTIONAL_AUTH_STORE}" ] || [ "${EXCEPTIONAL_AUTH_STORE}" = "UNRESOLVED" ]; then
            echo "EXCEPTIONAL_AUTH_STORE_UNRESOLVED"; exit 1
          fi
          # Section 97.3: "Event types are identifiers, not prose ... the enum is
          # declared in platform.yaml". The identifier is LOOKED UP, never coined.
          if [ ! -f platform.yaml ]; then
            echo "ROLLBACK_EVENT_TYPE_UNRESOLVED"; exit 1
          fi
          grep -qE '^[[:space:]]*-[[:space:]]*rollback_initiated[[:space:]]*$' platform.yaml \
            || { echo "ROLLBACK_EVENT_TYPE_UNRESOLVED"; exit 1; }
          echo "authorised=yes" >> "${GITHUB_OUTPUT}"
          echo "ROLLBACK_RECORDED ${TARGET_DIGEST}"
EOF
sed -i "s|@@SLUG@@|${CONTROL_PLANE_SLUG}|g; \
        s|@@@TAG@@|@${WORKFLOWS_TAG}|g; \
        s|@@RECORDSSLUG@@|${RECORDS_REPO_SLUG}|g; \
        s|@@APPROVALGLOB@@|${PRODUCTION_APPROVAL_RECORD_GLOB}|g; \
        s|@@EXCAUTHSTORE@@|${EXCEPTIONAL_AUTHORISATION_STORE}|g" \
  .github/workflows/rollback.yml
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/rollback.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/rollback.yml
git commit -m "L2-T176: rollback reusable workflow and its narrow D52 exemption (Section 27.2)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/rollback.yml'))"; echo $?` | exactly `0` |
| A2 | No placeholder survives | `grep -c '@@' .github/workflows/rollback.yml` | exactly `0` |
| A3 | The identity gate is **absent** — the exemption | `grep -c 'workflow-identity-gate' .github/workflows/rollback.yml` | exactly `0` |
| A4 | The actor gate is present and is the first job (§27.2) | `python3 -c "import yaml;print(list(yaml.safe_load(open('.github/workflows/rollback.yml'))['jobs'])[0])"` | exactly `actor-gate` |
| A5 | The actor gate demands exactly the two §27.2 capabilities | `grep -c 'required_capabilities: incident-response,production-approval' .github/workflows/rollback.yml` | exactly `1` |
| A6 | Machine dispatch is refused (§27.2 *"an exemption ... that also admitted machine dispatch"*) | `grep -c 'machine_dispatch_class: none' .github/workflows/rollback.yml` | exactly `1` |
| A7 | The runner-tier and env-policy gates are still present | `grep -c 'runner-tier-assert.yml\|env-policy-assert.yml' .github/workflows/rollback.yml` | exactly `2` |
| A8 | Every failure token is present | `for t in ROLLBACK_INPUT_UNRESOLVED ROLLBACK_RECORDS_UNREADABLE ROLLBACK_DIGEST_NEVER_APPROVED ROLLBACK_DIGEST_NEVER_DEPLOYED ROLLBACK_TARGET_UNRESOLVED MIGRATION_BOUNDARY_UNRESOLVED ROLLBACK_CONFIRMATION_MISMATCH EXCEPTIONAL_AUTH_STORE_UNRESOLVED ROLLBACK_EVENT_TYPE_UNRESOLVED; do grep -q "$t" .github/workflows/rollback.yml \|\| echo "MISSING $t"; done` | prints nothing |
| A9 | No `if:`, no path filter, no `continue-on-error` | `grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/rollback.yml` | exactly `0` |
| A10 | Every `uses:` is pinned to the contract tag | `grep -c "@${WORKFLOWS_TAG}$" .github/workflows/rollback.yml` | exactly `3` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/rollback.yml'))" \
 && test "$(grep -c '@@' .github/workflows/rollback.yml)" = "0" \
 && test "$(grep -c 'workflow-identity-gate' .github/workflows/rollback.yml)" = "0" \
 && test "$(python3 -c "import yaml;print(list(yaml.safe_load(open('.github/workflows/rollback.yml'))['jobs'])[0])")" = "actor-gate" \
 && test "$(grep -c 'required_capabilities: incident-response,production-approval' .github/workflows/rollback.yml)" = "1" \
 && test "$(grep -c 'machine_dispatch_class: none' .github/workflows/rollback.yml)" = "1" \
 && test "$(grep -c 'runner-tier-assert.yml\|env-policy-assert.yml' .github/workflows/rollback.yml)" = "2" \
 && test "$(grep -c "@${WORKFLOWS_TAG}\$" .github/workflows/rollback.yml)" = "3" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/rollback.yml)" = "0" \
 && for t in ROLLBACK_INPUT_UNRESOLVED ROLLBACK_RECORDS_UNREADABLE ROLLBACK_DIGEST_NEVER_APPROVED \
             ROLLBACK_DIGEST_NEVER_DEPLOYED ROLLBACK_TARGET_UNRESOLVED MIGRATION_BOUNDARY_UNRESOLVED \
             ROLLBACK_CONFIRMATION_MISMATCH EXCEPTIONAL_AUTH_STORE_UNRESOLVED \
             ROLLBACK_EVENT_TYPE_UNRESOLVED ROLLBACK_TARGET_OK; do \
      grep -q "$t" .github/workflows/rollback.yml || exit 1; done \
 && echo "L2-T176 OK" || echo "L2-T176 FAIL"
```
Correct output: the single line `L2-T176 OK`.

**STOP rule:** A3 is the one acceptance row in this document whose *correct* value is zero occurrences of a gate. If a reviewer or a later task asks for `workflow-identity-gate` to be added to this file, that is a request to delete D52 and to make the solo out-of-hours SEV-1 rollback impossible (§47.2 L4231) — STOP under **S6** and cite §27.2 L2575. Conversely, if any of A5, A6, A7 fails, an exemption has been widened past its stated scope: §27.2 says the actor gate is *"the one check this exemption does not lift"*, and D87 and D91 are not production approval at all. STOP under **S6**. If the executor cannot make A8's `MIGRATION_BOUNDARY_UNRESOLVED` reachable because no deployment record carries `migration_applied`, that is the expected state until Lane 4 ships the field — file it as the §8 requirement, do **not** default the boundary to `false`.

---

### L2-T370 — The per-product rollback workflow template

**Size:** M  **Depends on:** `L2-T176`

**Creates:** `templates/workflows/rollback.template.yml`

The reusable workflow of `L2-T176` is called by a per-product workflow whose filename is fixed by charter **D-L2-05** and resolved into `ROLLBACK_WORKFLOW_FILENAME` by `L2-T170`. The template is what `create-product` (Lane 3) copies into a product repository, so it carries placeholders in the form the other Lane 2 templates already use, and it carries the two anchor pairs `apply-production-gates.py` requires.

`workflow_dispatch` is the trigger: §42.3 (L3792) makes rollback the responder's first move, and a responder at 03:40 dispatches it from the Actions tab. It has no `push` trigger and it never will — D87 (L10191) makes a branch-push-triggered privileged workflow one of the three Blocking drift rows.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
mkdir -p templates/workflows
cat > templates/workflows/rollback.template.yml <<'EOF'
name: rollback
# =====================================================================
# PER-PRODUCT ROLLBACK WORKFLOW — generated from this template by
# create-product (Section 19.1). Target filename: @@ROLLBACKFILE@@
# Spec: Section 27.2 (line 2575); D52 (line 10120); Section 42.3 (line 3792);
#       Section 47.2 (line 4231); invariant 27 (line 9488).
#
# PLACEHOLDERS, substituted at product creation by Lane 3:
#   {{PRODUCT_SLUG}}   the product's slug as it appears in product.yaml
#   {{TARGET_REPO}}    owner/repo of this product repository
#   {{RUNNER_LABEL}}   ubuntu-latest, unless the product records the D87 exception
#   {{SELF_HOSTED}}    "false", unless the product records the D87 exception
#
# workflow_dispatch ONLY. A `push:` trigger on a privileged workflow is one of
# the three Blocking drift rows of D87 (line 10180) and must never be added.
# NO `if:` and NO path filter anywhere in this file (Section 33.2, line 2860).
# =====================================================================
on:
  workflow_dispatch:
    inputs:
      current_digest:
        description: 'The artifact identity currently deployed to production.'
        required: true
        type: string
      confirm_digest:
        description: >-
          Retype the target digest the previous run displayed. Section 27.2:
          the workflow "requires only confirmation to run".
        required: true
        type: string
      authorisation_reason:
        description: 'Why this rollback is being run. Section 47.2 exception record.'
        required: true
        type: string

permissions:
  contents: read

jobs:
  # >>> PRODUCTION-GATE-CHAIN v1
  rollback:
    name: rollback
    uses: @@SLUG@@/.github/workflows/rollback.yml@@@TAG@@
    with:
      product: '{{PRODUCT_SLUG}}'
      current_digest: ${{ inputs.current_digest }}
      confirm_digest: ${{ inputs.confirm_digest }}
      actor: ${{ github.actor }}
      registry_ref: ${{ github.sha }}
      environment_name: production
      target_repo: '{{TARGET_REPO}}'
      deploy_ref: ${{ github.ref }}
      runner_label: '{{RUNNER_LABEL}}'
      privileged_self_hosted_declared: '{{SELF_HOSTED}}'
      authorisation_reason: ${{ inputs.authorisation_reason }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.@@REGREADSECRET@@ }}
      RECORDS_READ_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
      RECORDS_WRITER_TOKEN: ${{ secrets.@@RECWRITESECRET@@ }}
      ENV_POLICY_READ_TOKEN: ${{ secrets.@@REGREADSECRET@@ }}
  # <<< PRODUCTION-GATE-CHAIN v1

  rollback-authorised:
    name: rollback-authorised
    needs: rollback
    runs-on: '{{RUNNER_LABEL}}'
    timeout-minutes: 5
    steps:
      # >>> RUNNER-TIER-ASSERT v1
      # <<< RUNNER-TIER-ASSERT v1
      - name: Publish the authorised rollback target
        env:
          AUTHORISED: ${{ needs.rollback.outputs.authorised }}
          TARGET_DIGEST: ${{ needs.rollback.outputs.target_digest }}
          MIGRATION_BOUNDARY: ${{ needs.rollback.outputs.migration_boundary }}
        run: |
          set -euo pipefail
          # The redeploy leg is a DECLARED SEAM: deploy-production.yml is
          # authored by the later Lane 2 phase that owns it (charter DoD-01) and
          # is wired in here by tools/evidence/apply-production-gates.py.
          # Until then this job proves the authorisation and stops. It never
          # reports success on an unauthorised run.
          if [ "${AUTHORISED}" != "yes" ]; then
            echo "ROLLBACK_NOT_AUTHORISED"; exit 1
          fi
          if [ -z "${TARGET_DIGEST}" ]; then
            echo "ROLLBACK_NOT_AUTHORISED"; exit 1
          fi
          echo "ROLLBACK_AUTHORISED ${TARGET_DIGEST} boundary=${MIGRATION_BOUNDARY}"
EOF
sed -i "s|@@SLUG@@|${CONTROL_PLANE_SLUG}|g; \
        s|@@@TAG@@|@${WORKFLOWS_TAG}|g; \
        s|@@ROLLBACKFILE@@|${ROLLBACK_WORKFLOW_FILENAME}|g; \
        s|@@REGREADSECRET@@|${REGISTRY_READ_SECRET_NAME}|g; \
        s|@@RECWRITESECRET@@|${RECORDS_WRITER_SECRET_NAME}|g" \
  templates/workflows/rollback.template.yml
python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback.template.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add templates/workflows/rollback.template.yml
git commit -m "L2-T370: per-product rollback workflow template (charter D-L2-05)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback.template.yml'))"; echo $?` | exactly `0` |
| A2 | No `@@` placeholder survives; exactly the four `{{ }}` product placeholders remain | `grep -c '@@' templates/workflows/rollback.template.yml; grep -o '{{[A-Z_]*}}' templates/workflows/rollback.template.yml \| sort -u \| wc -l` | `0` then `4` |
| A3 | The only trigger is `workflow_dispatch` | `python3 -c "import yaml;print(list(yaml.safe_load(open('templates/workflows/rollback.template.yml'))[True]))"` | exactly `['workflow_dispatch']` |
| A4 | No `push:` trigger (D87 Blocking row) | `grep -cE '^\s*push:' templates/workflows/rollback.template.yml` | exactly `0` |
| A5 | Both anchor pairs are present, each exactly once | `for a in 'PRODUCTION-GATE-CHAIN v1' 'RUNNER-TIER-ASSERT v1'; do test "$(grep -c ">>> $a" templates/workflows/rollback.template.yml)" = "1" -a "$(grep -c "<<< $a" templates/workflows/rollback.template.yml)" = "1" \|\| echo "BAD $a"; done` | prints nothing |
| A6 | The `uses:` is pinned to the contract tag | `grep -c "rollback.yml@${WORKFLOWS_TAG}$" templates/workflows/rollback.template.yml` | exactly `1` |
| A7 | No `if:`, no path filter | `grep -cE '^\s*(if:|paths:|paths-ignore:)' templates/workflows/rollback.template.yml` | exactly `0` |

*(A3 indexes the parsed mapping with `True` because PyYAML parses the unquoted YAML 1.1 key `on:` as the boolean `True`. That is expected and is why the acceptance command is written this way rather than with the string `'on'`.)*

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback.template.yml'))" \
 && test "$(grep -c '@@' templates/workflows/rollback.template.yml)" = "0" \
 && test "$(python3 -c "import yaml;print(list(yaml.safe_load(open('templates/workflows/rollback.template.yml'))[True]))")" = "['workflow_dispatch']" \
 && test "$(grep -cE '^\s*push:' templates/workflows/rollback.template.yml)" = "0" \
 && test "$(grep -o '{{[A-Z_]*}}' templates/workflows/rollback.template.yml | sort -u | wc -l | tr -d ' ')" = "4" \
 && test "$(grep -c '>>> PRODUCTION-GATE-CHAIN v1' templates/workflows/rollback.template.yml)" = "1" \
 && test "$(grep -c '<<< PRODUCTION-GATE-CHAIN v1' templates/workflows/rollback.template.yml)" = "1" \
 && test "$(grep -c '>>> RUNNER-TIER-ASSERT v1' templates/workflows/rollback.template.yml)" = "1" \
 && test "$(grep -c '<<< RUNNER-TIER-ASSERT v1' templates/workflows/rollback.template.yml)" = "1" \
 && test "$(grep -c "rollback.yml@${WORKFLOWS_TAG}\$" templates/workflows/rollback.template.yml)" = "1" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' templates/workflows/rollback.template.yml)" = "0" \
 && echo "L2-T370 OK" || echo "L2-T370 FAIL"
```
Correct output: the single line `L2-T370 OK`.

**STOP rule:** if A3 does not print exactly `['workflow_dispatch']`, a second trigger has been added. A `push:` or `schedule:` trigger on a privileged workflow is a Blocking drift row under D87 (L10191) and a `pull_request:` trigger hands the workflow to whoever opens a pull request. STOP under **S6**. If `ROLLBACK_WORKFLOW_FILENAME` is empty, `L2-T170` already stopped the phase; do not name the file yourself — that is charter **D-L2-05** and it belongs to L0.

---

### L2-T371 — The rollback exemption declaration

**Size:** S  **Depends on:** `L2-T176`, `L2-T370`

**Creates:** `templates/workflows/rollback-exemption.yaml`

A missing gate and an exempt gate look identical in a workflow file: both are an absence. This file is what makes them different. `assert-privileged-workflows.py` (`L2-T571`) refuses any privileged workflow missing a gate **unless** the absence is declared here, with its spec citation and its decision id. An absence with no row is a defect; an absence with a row is D52.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
cat > templates/workflows/rollback-exemption.yaml <<'EOF'
# ROLLBACK GATE EXEMPTION — MACHINE-READABLE DECLARATION.
# Read by tools/evidence/assert-privileged-workflows.py. Never hand-consumed.
# A gate absent from a privileged workflow is a DEFECT unless it appears in
# `exempt_from` below with its spec citation and decision id.
exemption_schema_version: 1
workflow: rollback.yml
product_template: rollback.template.yml
product_filename: '@@ROLLBACKFILE@@'

exempt_from:
  - gate: workflow-identity-gate
    spec_section: '27.2'
    spec_lines: '2575'
    decision: D52
    decision_line: '10120'
    reason: >-
      Redeploying an artifact digest that already carries a production-approval
      record is a restoration, not a new release. The digest was approved once.
      The exemption is conditional on the prior-approval assertion in
      rollback.yml, which fails closed with ROLLBACK_DIGEST_NEVER_APPROVED.
  - gate: environment-required-reviewers
    spec_section: '27.2'
    spec_lines: '2575'
    decision: D52
    decision_line: '10120'
    reason: >-
      Where the Enterprise strengthening is bought (D73, line 10156), the
      rollback workflow is exempt from environment required reviewers on the
      same grounds. This estate does not depend on that feature either way.

not_exempt_from:
  - gate: actor-gate
    spec_section: '27.2'
    spec_lines: '2575'
    reason: >-
      Named in Section 27.2 as "the one check this exemption does not lift".
      An exemption admitting machine dispatch would let a background-layer
      credential return production to an older digest across a migration
      boundary, reintroducing a patched vulnerability under a workflow that
      reports success.
  - gate: runner-tier-assert
    spec_section: '39.5'
    spec_lines: '3591'
    reason: >-
      The rollback workflow is a member of D87's closed privileged set and
      asserts its own runner tier like every other member.
  - gate: env-policy-assert
    spec_section: '33.4'
    spec_lines: '2911'
    reason: >-
      The rollback workflow reaches production-environment secrets from a ref,
      so D91's deployment branch and tag policy applies unchanged.
  - gate: prior-approval-assertion
    spec_section: '27.2'
    spec_lines: '2575'
    reason: >-
      The precondition of the exemption itself. Without it the exemption would
      admit an unapproved digest to production.
  - gate: exceptional-authorisation-record
    spec_section: '27.2'
    spec_lines: '2575'
    reason: >-
      "Each run of the rollback workflow is recorded as an exceptional
      authorisation and audited (Section 42.3)." Blocked on D-L2-10; the step
      is present and fails closed until it resolves.
EOF
sed -i "s|@@ROLLBACKFILE@@|${ROLLBACK_WORKFLOW_FILENAME}|g" \
  templates/workflows/rollback-exemption.yaml
python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add templates/workflows/rollback-exemption.yaml
git commit -m "L2-T371: machine-readable rollback gate-exemption declaration (D52)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))"; echo $?` | exactly `0` |
| A2 | No placeholder survives | `grep -c '@@' templates/workflows/rollback-exemption.yaml` | exactly `0` |
| A3 | Exactly two exemptions are declared | `python3 -c "import yaml;print(len(yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))['exempt_from']))"` | exactly `2` |
| A4 | `workflow-identity-gate` is one of them | `python3 -c "import yaml;print('workflow-identity-gate' in [e['gate'] for e in yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))['exempt_from']])"` | exactly `True` |
| A5 | `actor-gate` is **not** exempt (§27.2) | `python3 -c "import yaml;d=yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'));print('actor-gate' in [e['gate'] for e in d['not_exempt_from']] and 'actor-gate' not in [e['gate'] for e in d['exempt_from']])"` | exactly `True` |
| A6 | Every exemption carries a decision id and a spec citation | `python3 -c "import yaml;d=yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'));print(all(e.get('decision') and e.get('spec_section') and e.get('spec_lines') for e in d['exempt_from']))"` | exactly `True` |
| A7 | Five gates are declared not-exempt | `python3 -c "import yaml;print(len(yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))['not_exempt_from']))"` | exactly `5` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('templates/workflows/rollback-exemption.yaml'))
ex = [e['gate'] for e in d['exempt_from']]
nx = [e['gate'] for e in d['not_exempt_from']]
ok = (
    d['exemption_schema_version'] == 1
    and len(ex) == 2 and 'workflow-identity-gate' in ex
    and len(nx) == 5 and 'actor-gate' in nx and 'actor-gate' not in ex
    and all(e.get('decision') and e.get('spec_section') and e.get('spec_lines')
            for e in d['exempt_from'])
)
print("L2-T371 OK" if ok else "L2-T371 FAIL")
PY
```
Correct output: the single line `L2-T371 OK`.

**STOP rule:** never add a gate to `exempt_from` to make `assert-privileged-workflows.py` pass. That inverts the entire mechanism: the declaration exists to make an absence reviewable, and a declaration written to silence an assertion is a self-issued exemption. Only §27.2 L2575 and D52 L10120 authorise the two rows present. Adding a third is a Contract Change Request to L0. STOP under **S6**.

---

### L2-T570 — `apply-production-gates` — the idempotent template-wiring tool

**Size:** M  **Depends on:** `L2-T175`, `L2-T370`

**Creates:** `tools/evidence/apply-production-gates.py`

Stop rule **S8** forbids hand-editing a workflow template authored by another phase. This tool is the sanctioned alternative. It replaces the contents of two **anchor-delimited regions** and touches nothing else:

| Anchor pair | Region contents | Where it goes |
|---|---|---|
| `# >>> PRODUCTION-GATE-CHAIN v1` … `# <<< PRODUCTION-GATE-CHAIN v1` | the gate-chain calling job | inside `jobs:` |
| `# >>> RUNNER-TIER-ASSERT v1` … `# <<< RUNNER-TIER-ASSERT v1` | the canonical step fragment of `L2-T172` | step index 0 of each privileged job |

Anchor-delimited region replacement is what makes the tool idempotent: running it twice produces a byte-identical file, because the second run replaces the region the first run wrote. It is also what preserves comments — the tool never round-trips the whole document through a YAML dumper, which would silently drop every comment in a file it does not own. It **parses** the result and refuses to write anything that does not parse, so it is YAML-aware without being YAML-destructive.

A template with no anchors is not edited: the tool exits non-zero with `GATE_ANCHOR_ABSENT` naming the file and the anchor. Adding the anchors to a template is the owning phase's job, and §8 records that requirement.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence
cat > tools/evidence/apply-production-gates.py <<'PYFILE'
#!/usr/bin/env python3
"""Idempotently wire the Phase 3 production gates into a workflow template.

Spec: Section 27.2 (2567-2576), 37.3 (3261-3268), 39.5 (3589-3596), 33.4 (2911).
Decisions D52, D73, D87, D91.

STOP RULE S8: this tool is the ONLY sanctioned way to modify a workflow template
authored by another phase. A hand edit that reorders or drops a key is
undetectable and is exactly the failure Section 53.1's template comparison
cannot see.

Mechanism: anchor-delimited region replacement, then a structural re-parse.
  # >>> RUNNER-TIER-ASSERT v1 ... # <<< RUNNER-TIER-ASSERT v1
  # >>> PRODUCTION-GATE-CHAIN v1 ... # <<< PRODUCTION-GATE-CHAIN v1

Running twice produces a byte-identical file. Comments outside the regions are
never touched, because the document is never round-tripped through a dumper.

Exit codes: 0 wrote or already current; 1 refused (fail closed).
"""
import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("APPLY_GATES_PYYAML_ABSENT")
    sys.exit(1)

FRAGMENT_PATH = "templates/workflows/runner-tier-assert.step.yml"
STEP_ANCHOR = "RUNNER-TIER-ASSERT v1"
CHAIN_ANCHOR = "PRODUCTION-GATE-CHAIN v1"


def fail(token, detail=""):
    print(("%s %s" % (token, detail)).strip())
    sys.exit(1)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return fh.read()
    except OSError:
        fail("APPLY_GATES_FILE_UNREADABLE", path)


def find_region(lines, anchor, path):
    """Return (open_index, close_index, indent) for one anchor pair."""
    opens = [i for i, ln in enumerate(lines) if (">>> " + anchor) in ln]
    closes = [i for i, ln in enumerate(lines) if ("<<< " + anchor) in ln]
    if len(opens) != 1 or len(closes) != 1:
        fail("GATE_ANCHOR_ABSENT", "%s %s" % (path, anchor))
    if closes[0] < opens[0]:
        fail("GATE_ANCHOR_INVERTED", "%s %s" % (path, anchor))
    indent = len(lines[opens[0]]) - len(lines[opens[0]].lstrip())
    return opens[0], closes[0], indent


def load_fragment(indent):
    """The canonical RUNNER-TIER-ASSERT v1 step, re-indented, comments kept."""
    raw = read(FRAGMENT_PATH)
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError:
        fail("APPLY_GATES_FRAGMENT_UNPARSEABLE", FRAGMENT_PATH)
    if not isinstance(doc, list) or len(doc) != 1 or not isinstance(doc[0], dict):
        fail("APPLY_GATES_FRAGMENT_MALFORMED", FRAGMENT_PATH)
    if doc[0].get("name") != STEP_ANCHOR:
        fail("APPLY_GATES_FRAGMENT_MALFORMED", FRAGMENT_PATH)
    body = []
    for ln in raw.splitlines():
        if ln.startswith("#"):
            continue          # the fragment file's own header, not part of the step
        body.append((" " * indent + ln) if ln.strip() else "")
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    return body


def replace_region(lines, open_i, close_i, body):
    return lines[: open_i + 1] + body + lines[close_i:]


def apply_file(path, chain_body):
    original = read(path)
    lines = original.splitlines()

    o, c, indent = find_region(lines, STEP_ANCHOR, path)
    lines = replace_region(lines, o, c, load_fragment(indent))

    if chain_body is not None:
        o, c, indent = find_region(lines, CHAIN_ANCHOR, path)
        body = [(" " * indent + ln) if ln.strip() else "" for ln in chain_body]
        lines = replace_region(lines, o, c, body)

    out = "\n".join(lines) + "\n"

    # YAML-AWARE: never write a file that does not parse.
    try:
        doc = yaml.safe_load(out)
    except yaml.YAMLError as exc:
        fail("APPLY_GATES_RESULT_UNPARSEABLE", "%s %s" % (path, exc.__class__.__name__))
    if not isinstance(doc, dict) or "jobs" not in doc:
        fail("APPLY_GATES_RESULT_MALFORMED", path)

    # Section 33.2 line 2860: no `if:` and no path filter may be introduced.
    for ln in lines:
        s = ln.strip()
        if s.startswith("if:") or s.startswith("paths:") or s.startswith("paths-ignore:"):
            fail("APPLY_GATES_SKIP_INTRODUCED", path)

    if out == original:
        print("APPLY_GATES_UNCHANGED %s" % path)
        return False
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print("APPLY_GATES_WROTE %s" % path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("templates", nargs="+", help="template files to wire")
    ap.add_argument("--chain-body", default=None,
                    help="file holding the gate-chain job block; omit to leave that region as-is")
    args = ap.parse_args()

    if not os.path.isfile(FRAGMENT_PATH):
        fail("APPLY_GATES_FRAGMENT_ABSENT", FRAGMENT_PATH)

    chain_body = None
    if args.chain_body:
        chain_body = read(args.chain_body).splitlines()

    for path in args.templates:
        if not os.path.isfile(path):
            fail("APPLY_GATES_FILE_UNREADABLE", path)
        apply_file(path, chain_body)

    print("APPLY_GATES_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYFILE
chmod +x tools/evidence/apply-production-gates.py
python3 -m py_compile tools/evidence/apply-production-gates.py \
  || { echo "COMPILE FAILED — STOP"; exit 1; }
python3 tools/evidence/apply-production-gates.py templates/workflows/rollback.template.yml
python3 tools/evidence/apply-production-gates.py templates/workflows/rollback.template.yml
git add tools/evidence/apply-production-gates.py templates/workflows/rollback.template.yml
git commit -m "L2-T570: idempotent anchor-based production-gate wiring tool (STOP rule S8)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Compiles | `python3 -m py_compile tools/evidence/apply-production-gates.py; echo $?` | exactly `0` |
| A2 | First run wires the fragment | `python3 tools/evidence/apply-production-gates.py templates/workflows/rollback.template.yml \| head -1` | a line beginning `APPLY_GATES_WROTE` or `APPLY_GATES_UNCHANGED` |
| A3 | Second run is byte-identical — idempotent | see SELF-VERIFY | exactly `IDEMPOTENT` |
| A4 | The wired template still parses | `python3 -c "import yaml;yaml.safe_load(open('templates/workflows/rollback.template.yml'))"; echo $?` | exactly `0` |
| A5 | Step index 0 of the privileged job is the fragment | `python3 -c "import yaml;d=yaml.safe_load(open('templates/workflows/rollback.template.yml'));print(d['jobs']['rollback-authorised']['steps'][0]['name'])"` | exactly `RUNNER-TIER-ASSERT v1` |
| A6 | A template with no anchor is refused, not edited | see SELF-VERIFY | exactly `GATE_ANCHOR_ABSENT`, exit `1` |
| A7 | A result that would not parse is never written | see SELF-VERIFY | exactly `REFUSED_UNPARSEABLE` |
| A8 | The tool introduces no `if:` and no path filter | `grep -cE '^\s*(if:|paths:|paths-ignore:)' templates/workflows/rollback.template.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T=templates/workflows/rollback.template.yml
python3 tools/evidence/apply-production-gates.py "$T" >/dev/null
A="$(sha256sum "$T" | cut -d' ' -f1)"
python3 tools/evidence/apply-production-gates.py "$T" >/dev/null
B="$(sha256sum "$T" | cut -d' ' -f1)"
test "$A" = "$B" && echo IDEMPOTENT || echo NOT_IDEMPOTENT

mkdir -p /tmp/pg570
printf 'name: x\non:\n  workflow_dispatch:\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: "true"\n' > /tmp/pg570/noanchor.yml
OUT="$(python3 tools/evidence/apply-production-gates.py /tmp/pg570/noanchor.yml 2>&1 | head -1 | cut -d' ' -f1)"; RC=$?
test "$OUT" = "GATE_ANCHOR_ABSENT" && echo "$OUT"

printf 'name: y\njobs:\n  a:\n    steps:\n      # >>> RUNNER-TIER-ASSERT v1\n      # <<< RUNNER-TIER-ASSERT v1\n  b: [ unbalanced\n' > /tmp/pg570/bad.yml
python3 tools/evidence/apply-production-gates.py /tmp/pg570/bad.yml >/dev/null 2>&1 \
  || echo "REFUSED_UNPARSEABLE"

test "$A" = "$B" \
 && python3 -c "import yaml;yaml.safe_load(open('$T'))" \
 && test "$(python3 -c "import yaml;d=yaml.safe_load(open('$T'));print(d['jobs']['rollback-authorised']['steps'][0]['name'])")" = "RUNNER-TIER-ASSERT v1" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' "$T")" = "0" \
 && echo "L2-T570 OK" || echo "L2-T570 FAIL"
```
Correct output, in order: `IDEMPOTENT`, `GATE_ANCHOR_ABSENT`, `REFUSED_UNPARSEABLE`, `L2-T570 OK`.

**STOP rule:** if A3 prints `NOT_IDEMPOTENT`, do not "fix" it by running the tool once and committing. A non-idempotent wiring tool makes every later run of `L2-T571` a diff, and `S8` then has no safe alternative to a hand edit. STOP under **S6** and file the blocker with the two differing hashes. If the tool refuses a template with `GATE_ANCHOR_ABSENT`, **do not add the anchors to another phase's template yourself** — that is a hand edit under a different name. Record it as the §8 requirement on the owning phase and move on.

---

### L2-T571 — `assert-privileged-workflows` — the posture assertion (DoD-05)

**Size:** M  **Depends on:** `L2-T570`

**Creates:** `tools/evidence/assert-privileged-workflows.py`

Charter **DoD-05**: *"Actor gate is the **first** step of all five privileged workflows — `tools/evidence/` check asserts step index 0 of each named workflow is the actor gate; exits 0."* This is that check.

**Two different "first"s, and they do not conflict.** §37.3 (L3267) says the actor gate is *"the first step of every privileged workflow"*. On GitHub a reusable-workflow call is a **job**, not a step, so the gate is realised as the workflow's first job, which every other job in the file `needs:`. The workflow's first executed step is therefore the actor gate's first step — DoD-05 satisfied at workflow scope. Within each *privileged job* — the jobs that do the privileged work, never the gate jobs — step index 0 is the `RUNNER-TIER-ASSERT v1` fragment, as `L2-T172` states, because that assertion must run on the same runner as the privileged work. The two statements are about two different scopes and the assertion below checks both.

**The set this tool checks.** §39.5 (L3591) fixes the privileged set at four: `deploy-production.yml`, `migrate.yml`, the rollback workflow, `restore-production.yml`. §37.3 (L3267) adds `deploy-staging.yml` to the actor-gate set. Four of those five are authored by other Lane 2 phases and may not exist yet. The tool therefore checks every member **that exists** and additionally refuses if a member named in `--require` is absent. This phase requires only the one template it authors; the full five become required when the deploy phase lands, and §8 records that.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a
cat > tools/evidence/assert-privileged-workflows.py <<'PYFILE'
#!/usr/bin/env python3
"""Assert the Phase 3 privileged-workflow posture. Charter DoD-05.

Spec: Section 37.3 (3261-3268) actor gate first; Section 39.5 (3589-3596) and
D87 (10180) runner isolation; Section 33.4 (2911) and D91 (10184) deployment
branch policy; Section 27.2 (2567-2576) and D73 (10156) the identity gate;
Section 27.2 line 2575 and D52 (10120) the rollback exemption;
Section 33.2 line 2860 no `if:` and no path filter on a gate job.

Fails closed: an unreadable file, an unparseable file and an unknown shape all
exit non-zero. Nothing here defaults to permit (Section 64, line 5431).

Exit codes: 0 posture holds; 1 posture violated; 2 could not tell.
"""
import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("PRIVILEGED_POSTURE_PYYAML_ABSENT")
    sys.exit(2)

EXEMPTION_PATH = "templates/workflows/rollback-exemption.yaml"
STEP_ANCHOR = "RUNNER-TIER-ASSERT v1"
GATE_JOBS = ("actor-gate", "runner-tier-assert", "env-policy-assert",
             "workflow-identity-gate", "rollback")
# A composer is a reusable workflow whose own first job is the actor gate and
# which this tool checks in its own right: the gate chain (L2-T175) and the
# rollback workflow (L2-T176).
COMPOSERS = ("production-gate-chain.yml@", "rollback.yml@")

FINDINGS = []


def finding(token, detail):
    FINDINGS.append("%s %s" % (token, detail))


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except OSError:
        print("PRIVILEGED_FILE_UNREADABLE %s" % path)
        sys.exit(2)
    except yaml.YAMLError:
        print("PRIVILEGED_FILE_UNPARSEABLE %s" % path)
        sys.exit(2)


def raw(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        print("PRIVILEGED_FILE_UNREADABLE %s" % path)
        sys.exit(2)


def needs_of(job):
    n = job.get("needs")
    if n is None:
        return []
    return [n] if isinstance(n, str) else list(n)


def reaches(jobs, start, target, seen=None):
    """True when `start` transitively needs `target`."""
    seen = seen or set()
    for n in needs_of(jobs.get(start, {})):
        if n == target:
            return True
        if n not in seen:
            seen.add(n)
            if reaches(jobs, n, target, seen):
                return True
    return False


def exemptions():
    if not os.path.isfile(EXEMPTION_PATH):
        print("PRIVILEGED_EXEMPTION_DECLARATION_ABSENT %s" % EXEMPTION_PATH)
        sys.exit(2)
    doc = load(EXEMPTION_PATH)
    if not isinstance(doc, dict) or not isinstance(doc.get("exempt_from"), list):
        print("PRIVILEGED_EXEMPTION_DECLARATION_MALFORMED %s" % EXEMPTION_PATH)
        sys.exit(2)
    out = {}
    for e in doc["exempt_from"]:
        if not isinstance(e, dict):
            continue
        gate = str(e.get("gate", "")).strip()
        # An exemption with no decision id and no spec citation is not an
        # exemption; it is an assertion someone wrote to silence this tool.
        if gate and e.get("decision") and e.get("spec_section") and e.get("spec_lines"):
            out[gate] = e
    return out


def check(path, exempt, is_rollback):
    doc = load(path)
    text = raw(path)
    if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), dict):
        finding("PRIVILEGED_WORKFLOW_MALFORMED", path)
        return
    jobs = doc["jobs"]
    order = list(jobs)

    # --- Section 33.2 line 2860: no skip surface anywhere. -------------------
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("if:") or s.startswith("paths:") or s.startswith("paths-ignore:"):
            finding("PRIVILEGED_SKIP_SURFACE", "%s :: %s" % (path, s))
        if s.startswith("continue-on-error:"):
            finding("PRIVILEGED_CONTINUE_ON_ERROR", "%s :: %s" % (path, s))

    # --- D87 line 10180: a privileged workflow is never branch-push triggered.
    triggers = doc.get(True, doc.get("on"))
    if isinstance(triggers, dict):
        for bad in ("push", "pull_request", "pull_request_target"):
            if bad in triggers:
                finding("PRIVILEGED_BRANCH_TRIGGER", "%s :: %s" % (path, bad))
    elif isinstance(triggers, (str, list)):
        finding("PRIVILEGED_BRANCH_TRIGGER", "%s :: bare trigger list" % path)

    # --- Section 37.3 line 3267 + DoD-05: the actor gate is first. -----------
    # A per-product template does not call actor-gate.yml directly: it calls a
    # COMPOSER — production-gate-chain.yml or rollback.yml — whose own first job
    # is the actor gate, asserted when this tool checks those files. Accepting a
    # composer here is what keeps DoD-05 true at workflow scope without
    # demanding that every template duplicate the chain.
    gate_job = None
    for name, job in jobs.items():
        uses = str(job.get("uses", ""))
        if ("actor-gate.yml@" in uses or name == "actor-gate"
                or any(c in uses for c in COMPOSERS)):
            gate_job = name
            break
    if gate_job is None:
        finding("ACTOR_GATE_ABSENT", path)
    else:
        if order[0] != gate_job:
            finding("ACTOR_GATE_NOT_FIRST", "%s :: first job is %s" % (path, order[0]))
        if needs_of(jobs[gate_job]):
            finding("ACTOR_GATE_NOT_FIRST", "%s :: %s carries needs:" % (path, gate_job))
        for name in order:
            if name == gate_job:
                continue
            if not reaches(jobs, name, gate_job):
                finding("ACTOR_GATE_BYPASSABLE", "%s :: %s" % (path, name))

    # --- D87: step index 0 of every non-gate job is the runner-tier fragment. -
    for name, job in jobs.items():
        if "uses" in job:
            continue                       # a reusable-workflow call has no steps
        if name in GATE_JOBS:
            continue
        steps = job.get("steps")
        if not isinstance(steps, list) or not steps:
            finding("PRIVILEGED_JOB_NO_STEPS", "%s :: %s" % (path, name))
            continue
        if str(steps[0].get("name", "")).strip() != STEP_ANCHOR:
            finding("RUNNER_TIER_ASSERT_NOT_STEP_ZERO",
                    "%s :: %s :: %s" % (path, name, steps[0].get("name")))

    # --- D91 line 10184: the environment policy assertion is present. --------
    composed = any(c in text for c in COMPOSERS)
    if ("env-policy-assert.yml@" not in text and not composed
            and "env-policy-assert" not in exempt):
        finding("ENV_POLICY_ASSERT_ABSENT", path)

    # --- Section 27.2 / D73: the identity gate, unless declared exempt. ------
    # rollback.yml is NOT counted as carrying the identity gate: its whole point
    # is that it does not (D52). production-gate-chain.yml is.
    has_identity = ("workflow-identity-gate.yml@" in text
                    or "workflow-identity-gate" in jobs
                    or "production-gate-chain.yml@" in text)
    if is_rollback:
        if "workflow-identity-gate" not in exempt:
            finding("ROLLBACK_EXEMPTION_UNDECLARED", path)
        if has_identity:
            # D52: the exemption is the point of the workflow. Re-adding the gate
            # makes the solo out-of-hours SEV-1 rollback impossible (Section 47.2).
            finding("ROLLBACK_IDENTITY_GATE_PRESENT", path)
    else:
        if not has_identity:
            finding("IDENTITY_GATE_ABSENT", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates-dir", default="templates/workflows")
    ap.add_argument("--rollback-template", default="rollback.template.yml")
    ap.add_argument("--require", default="",
                    help="comma-separated template filenames that MUST exist")
    args = ap.parse_args()

    exempt = exemptions()

    # Section 39.5 line 3591 (four) plus Section 37.3 line 3267 (deploy-staging).
    members = [
        "deploy-production.template.yml",
        "migrate.template.yml",
        args.rollback_template,
        "restore-production.template.yml",
        "deploy-staging.template.yml",
    ]

    required = [r.strip() for r in args.require.split(",") if r.strip()]
    for r in required:
        if not os.path.isfile(os.path.join(args.templates_dir, r)):
            print("PRIVILEGED_TEMPLATE_ABSENT %s" % r)
            sys.exit(1)

    checked = 0
    for m in members:
        path = os.path.join(args.templates_dir, m)
        if not os.path.isfile(path):
            continue
        check(path, exempt, is_rollback=(m == args.rollback_template))
        checked += 1

    if checked == 0:
        # Zero observations is never a pass (Section 53.1, line 4674).
        print("PRIVILEGED_NO_TEMPLATES_CHECKED")
        return 2

    for f in FINDINGS:
        print(f)
    if FINDINGS:
        print("PRIVILEGED_POSTURE_FAIL findings=%d checked=%d" % (len(FINDINGS), checked))
        return 1
    print("PRIVILEGED_POSTURE_OK checked=%d" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYFILE
chmod +x tools/evidence/assert-privileged-workflows.py
python3 -m py_compile tools/evidence/assert-privileged-workflows.py \
  || { echo "COMPILE FAILED — STOP"; exit 1; }
python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml
git add tools/evidence/assert-privileged-workflows.py
git commit -m "L2-T571: privileged-workflow posture assertion (charter DoD-05; D52, D87, D91)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Compiles | `python3 -m py_compile tools/evidence/assert-privileged-workflows.py; echo $?` | exactly `0` |
| A2 | The estate as built passes | `python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml` | exactly `PRIVILEGED_POSTURE_OK checked=1` |
| A3 | Zero templates checked is never a pass | `python3 tools/evidence/assert-privileged-workflows.py --templates-dir /tmp/empty571; echo $?` | exactly `PRIVILEGED_NO_TEMPLATES_CHECKED` then `2` |
| A4 | A required-but-absent template fails | `python3 tools/evidence/assert-privileged-workflows.py --require migrate.template.yml; echo $?` | exactly `PRIVILEGED_TEMPLATE_ABSENT migrate.template.yml` then `1` |
| A5 | An undeclared exemption is a finding | see SELF-VERIFY | a line containing `ROLLBACK_EXEMPTION_UNDECLARED` |
| A6 | Re-adding the identity gate to rollback is a finding | see SELF-VERIFY | a line containing `ROLLBACK_IDENTITY_GATE_PRESENT` |
| A7 | An `if:` anywhere is a finding | see SELF-VERIFY | a line containing `PRIVILEGED_SKIP_SURFACE` |
| A8 | A job that does not need the actor gate is a finding | see SELF-VERIFY | a line containing `ACTOR_GATE_BYPASSABLE` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
A="$(python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml)"
mkdir -p /tmp/empty571
python3 tools/evidence/assert-privileged-workflows.py --templates-dir /tmp/empty571 >/dev/null 2>&1; RC3=$?

W=/tmp/neg571; rm -rf "$W"; mkdir -p "$W"
cp templates/workflows/rollback.template.yml "$W/rollback.template.yml"

# A5: the declaration is what makes the absence an exemption. Hide it.
mv templates/workflows/rollback-exemption.yaml /tmp/keep-exemption.yaml
printf 'exemption_schema_version: 1\nexempt_from: []\nnot_exempt_from: []\n' \
  > templates/workflows/rollback-exemption.yaml
A5="$(python3 tools/evidence/assert-privileged-workflows.py --templates-dir "$W" 2>&1 | grep -c 'ROLLBACK_EXEMPTION_UNDECLARED')"
mv /tmp/keep-exemption.yaml templates/workflows/rollback-exemption.yaml

# A6: put the identity gate back into rollback.
sed 's|rollback.yml@|workflow-identity-gate.yml@|' "$W/rollback.template.yml" > "$W/tmp" && mv "$W/tmp" "$W/rollback.template.yml"
A6="$(python3 tools/evidence/assert-privileged-workflows.py --templates-dir "$W" 2>&1 | grep -c 'ROLLBACK_IDENTITY_GATE_PRESENT')"
cp templates/workflows/rollback.template.yml "$W/rollback.template.yml"

# A7: introduce a skip surface.
sed 's|^  rollback-authorised:|  rollback-authorised:\n    if: always()|' \
  "$W/rollback.template.yml" > "$W/tmp" && mv "$W/tmp" "$W/rollback.template.yml"
A7="$(python3 tools/evidence/assert-privileged-workflows.py --templates-dir "$W" 2>&1 | grep -c 'PRIVILEGED_SKIP_SURFACE')"
cp templates/workflows/rollback.template.yml "$W/rollback.template.yml"

# A8: cut the needs: edge to the actor gate.
sed '/^    needs: rollback$/d' "$W/rollback.template.yml" > "$W/tmp" && mv "$W/tmp" "$W/rollback.template.yml"
A8="$(python3 tools/evidence/assert-privileged-workflows.py --templates-dir "$W" 2>&1 | grep -c 'ACTOR_GATE_BYPASSABLE')"

test "$A" = "PRIVILEGED_POSTURE_OK checked=1" \
 && test "$RC3" = "2" \
 && test "$A5" -ge 1 && test "$A6" -ge 1 && test "$A7" -ge 1 && test "$A8" -ge 1 \
 && echo "L2-T571 OK" || echo "L2-T571 FAIL"
```
Correct output: the single line `L2-T571 OK`.

**STOP rule:** if A5 through A8 print `0`, the assertion does not discriminate — it passes both the correct estate and a broken one, which is the failure D97 (the seeded-defect rule, spec L10190 region) names in another context and which §53.1 L4674 forbids here. A check that cannot fail is not a check. STOP under **S6** and file the blocker naming which seeded case was not detected. Never restore the posture by editing the seeded fixture; the fixtures under `/tmp/neg571` are throwaway copies and the real templates are restored by the script above.

---

### L2-T572 — Phase 3 negative-test suite

**Size:** L  **Depends on:** `L2-T571`

**Creates:** `tools/evidence/test/phase3/extract-step.py`, `tools/evidence/test/phase3/run-all.sh`, `tools/evidence/test/phase3/fixtures/**`

Every gate in this phase claims to fail closed. This suite proves it, locally, with no GitHub API and no runner. It works because each gate body was written to read **local files and environment variables only**: `people.yaml` in the working directory, `approvals/*` written by the preceding step, `env.json`/`policies.json`/`default_branch.txt`, `deployments/*`. The extractor pulls a step's script — or the Python heredoc inside it — out of the workflow file and runs it against a fixture directory.

This is the mechanism charter **DoD-04** requires (*"negative test exits non-zero; job log contains the exact string `APPROVER_EQUALS_DEPLOYER`"*) and it is the only way this phase's fail-closed claims are anything other than an assertion in prose.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/test/phase3/fixtures
cat > tools/evidence/test/phase3/extract-step.py <<'PYFILE'
#!/usr/bin/env python3
"""Extract a step's shell body, or the Python heredoc inside it, from a workflow.

Used only by tools/evidence/test/phase3/run-all.sh. Extraction rather than
duplication is deliberate: a copy of a gate body in a test drifts from the gate
silently, and a drifted negative test proves nothing.
"""
import argparse
import sys

import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workflow")
    ap.add_argument("job")
    ap.add_argument("step_name")
    ap.add_argument("--python", action="store_true",
                    help="emit the PYEOF heredoc body instead of the shell body")
    args = ap.parse_args()

    with open(args.workflow, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    steps = doc["jobs"][args.job]["steps"]
    body = None
    for s in steps:
        if str(s.get("name", "")).strip() == args.step_name:
            body = s.get("run")
            break
    if body is None:
        print("EXTRACT_STEP_NOT_FOUND", file=sys.stderr)
        return 2

    if args.python:
        lines = body.splitlines()
        try:
            start = next(i for i, ln in enumerate(lines) if "<<'PYEOF'" in ln)
            end = next(i for i, ln in enumerate(lines) if ln.strip() == "PYEOF" and i > start)
        except StopIteration:
            print("EXTRACT_HEREDOC_NOT_FOUND", file=sys.stderr)
            return 2
        body = "\n".join(lines[start + 1:end])

    sys.stdout.write(body if body.endswith("\n") else body + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYFILE
chmod +x tools/evidence/test/phase3/extract-step.py

F=tools/evidence/test/phase3/fixtures

# --- people.yaml: one approver, one deployer, one machine, one lapsed person --
mkdir -p "$F/registry"
cat > "$F/registry/people.yaml" <<'EOF'
people:
  - id: person-approver
    github_login: approver-login
    identity_class: human
    availability: active
    access_status: provisioned
    capabilities: [production-approval, release-signoff]
  - id: person-deployer
    github_login: deployer-login
    identity_class: human
    availability: active
    access_status: provisioned
    capabilities: [devops, incident-response]
  - id: machine-hermes
    github_login: hermes-bot
    identity_class: machine
    availability: active
    access_status: provisioned
    capabilities: [devops]
  - id: person-lapsed
    github_login: lapsed-login
    identity_class: human
    availability: departed
    access_status: revoked
    capabilities: [production-approval]
EOF

# --- approval records: clean, self-approved, wrong-digest, none --------------
D1=sha256:1111111111111111111111111111111111111111111111111111111111111111
D2=sha256:2222222222222222222222222222222222222222222222222222222222222222

mkdir -p "$F/approvals-clean/approvals" "$F/approvals-self/approvals" \
         "$F/approvals-wrongdigest/approvals" "$F/approvals-empty/approvals"
cp "$F/registry/people.yaml" "$F/approvals-clean/people.yaml"
cp "$F/registry/people.yaml" "$F/approvals-self/people.yaml"
cp "$F/registry/people.yaml" "$F/approvals-wrongdigest/people.yaml"
cp "$F/registry/people.yaml" "$F/approvals-empty/people.yaml"

cat > "$F/approvals-clean/approvals/dep-001.yaml" <<EOF
id: DEP-2026-09-12-014
product: demo
digest: ${D1}
approved_by: person-approver
approval_event: https://example.invalid/run/1
staging_verified: true
smoke_result: pass
rollback_of: null
timestamp: 2026-09-12T10:00:00Z
migration_applied: false
EOF
sed 's/approved_by: person-approver/approved_by: person-deployer/' \
  "$F/approvals-clean/approvals/dep-001.yaml" > "$F/approvals-self/approvals/dep-001.yaml"
sed "s|digest: ${D1}|digest: ${D2}|" \
  "$F/approvals-clean/approvals/dep-001.yaml" > "$F/approvals-wrongdigest/approvals/dep-001.yaml"
# git tracks files, not directories: the empty-store fixture needs a tracked file
# or a fresh clone loses the directory and the case silently stops being a case.
printf '# intentionally empty approval store — the NO_APPROVAL_RECORD fixture\n' \
  > "$F/approvals-empty/approvals/.gitkeep"

# --- deployment histories for the rollback target resolution ----------------
mkdir -p "$F/rollback-clean/deployments" "$F/rollback-nomigfield/deployments"
cp "$F/approvals-clean/approvals/dep-001.yaml" "$F/rollback-clean/deployments/dep-001.yaml"
cat > "$F/rollback-clean/deployments/dep-002.yaml" <<EOF
id: DEP-2026-09-20-002
product: demo
digest: ${D2}
approved_by: person-approver
approval_event: https://example.invalid/run/2
staging_verified: true
smoke_result: pass
rollback_of: null
timestamp: 2026-09-20T10:00:00Z
migration_applied: true
EOF
cp "$F/rollback-clean/deployments/dep-001.yaml" "$F/rollback-nomigfield/deployments/dep-001.yaml"
grep -v '^migration_applied:' "$F/rollback-clean/deployments/dep-002.yaml" \
  > "$F/rollback-nomigfield/deployments/dep-002.yaml"

cat > tools/evidence/test/phase3/run-all.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 Phase 3 negative-test suite.
# Every gate of this phase is proven to FAIL CLOSED on its named condition.
# Spec: Sections 27.2, 33.4, 37.3, 39.5; charter DoD-04 and DoD-05.
# Re-runnable, offline, no GitHub API. Prints SUITE_PASS or SUITE_FAIL.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
X="python3 tools/evidence/test/phase3/extract-step.py"
F="tools/evidence/test/phase3/fixtures"
W="$(mktemp -d)"
PASS=0; FAIL=0

D1=sha256:1111111111111111111111111111111111111111111111111111111111111111
D2=sha256:2222222222222222222222222222222222222222222222222222222222222222
D3=sha256:3333333333333333333333333333333333333333333333333333333333333333

expect() {  # expect <label> <expected-token> <expected-rc> -- <command...>
  local label="$1" token="$2" want_rc="$3"; shift 4
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want_rc" ] && printf '%s' "$out" | grep -q "$token"; then
    echo "PASS ${label}"; PASS=$((PASS+1))
  else
    echo "FAIL ${label} rc=${rc} want=${want_rc}"
    printf '%s\n' "$out" | tail -3
    FAIL=$((FAIL+1))
  fi
}

# ---------------------------------------------------------------- runner tier
RT="$W/runner-tier.sh"
python3 -c "import yaml,sys;print(yaml.safe_load(open('templates/workflows/runner-tier-assert.step.yml'))[0]['run'])" > "$RT"

expect "runner-tier/hosted-passes" "RUNNER_TIER_OK hosted" 0 -- \
  env RUNNER_ENVIRONMENT=github-hosted PRIVILEGED_SELF_HOSTED_DECLARED=false \
      PRIVILEGED_RUNNER_MARKER=/nonexistent EPHEMERAL_RUNNER_MARKER=/nonexistent \
      bash "$RT"
expect "runner-tier/undeclared-self-hosted-refused" "RUNNER_TIER_UNDECLARED_SELF_HOSTED" 1 -- \
  env RUNNER_ENVIRONMENT=self-hosted PRIVILEGED_SELF_HOSTED_DECLARED=false \
      PRIVILEGED_RUNNER_MARKER=/nonexistent EPHEMERAL_RUNNER_MARKER=/nonexistent \
      bash "$RT"
expect "runner-tier/shared-pool-refused" "RUNNER_TIER_SHARED_POOL" 1 -- \
  env RUNNER_ENVIRONMENT=self-hosted PRIVILEGED_SELF_HOSTED_DECLARED=true \
      PRIVILEGED_RUNNER_MARKER=/nonexistent EPHEMERAL_RUNNER_MARKER=/nonexistent \
      bash "$RT"
touch "$W/priv.marker"
expect "runner-tier/non-ephemeral-refused" "RUNNER_TIER_NOT_EPHEMERAL" 1 -- \
  env RUNNER_ENVIRONMENT=self-hosted PRIVILEGED_SELF_HOSTED_DECLARED=true \
      PRIVILEGED_RUNNER_MARKER="$W/priv.marker" EPHEMERAL_RUNNER_MARKER=/nonexistent \
      bash "$RT"
touch "$W/eph.marker"
expect "runner-tier/privileged-ephemeral-passes" "RUNNER_TIER_OK privileged-ephemeral" 0 -- \
  env RUNNER_ENVIRONMENT=self-hosted PRIVILEGED_SELF_HOSTED_DECLARED=true \
      PRIVILEGED_RUNNER_MARKER="$W/priv.marker" EPHEMERAL_RUNNER_MARKER="$W/eph.marker" \
      bash "$RT"
expect "runner-tier/unknown-environment-refused" "RUNNER_TIER_UNRESOLVED" 1 -- \
  env RUNNER_ENVIRONMENT= PRIVILEGED_SELF_HOSTED_DECLARED=true \
      PRIVILEGED_RUNNER_MARKER="$W/priv.marker" EPHEMERAL_RUNNER_MARKER="$W/eph.marker" \
      bash "$RT"

# ----------------------------------------------------------------- actor gate
AG="$W/actor-gate.py"
$X .github/workflows/actor-gate.yml actor-gate "Resolve the actor against people.yaml" --python > "$AG"
mkdir -p "$W/ag"; cp "$F/registry/people.yaml" "$W/ag/people.yaml"
: > "$W/ag/out.txt"

expect "actor-gate/capable-human-passes" "ACTOR_GATE_PASS person-approver" 0 -- \
  bash -c 'cd "$0" && env ACTOR=approver-login REQUIRED_CAPABILITIES=production-approval MACHINE_DISPATCH_CLASS=none GITHUB_OUTPUT=out.txt python3 "$1"' "$W/ag" "$AG"
expect "actor-gate/unknown-actor-refused" "ACTOR_NOT_HUMAN" 1 -- \
  bash -c 'cd "$0" && env ACTOR=nobody REQUIRED_CAPABILITIES=production-approval MACHINE_DISPATCH_CLASS=none GITHUB_OUTPUT=out.txt python3 "$1"' "$W/ag" "$AG"
expect "actor-gate/machine-refused" "ACTOR_NOT_HUMAN" 1 -- \
  bash -c 'cd "$0" && env ACTOR=hermes-bot REQUIRED_CAPABILITIES=devops MACHINE_DISPATCH_CLASS=none GITHUB_OUTPUT=out.txt python3 "$1"' "$W/ag" "$AG"
expect "actor-gate/departed-refused" "ACTOR_NOT_ACTIVE" 1 -- \
  bash -c 'cd "$0" && env ACTOR=lapsed-login REQUIRED_CAPABILITIES=production-approval MACHINE_DISPATCH_CLASS=none GITHUB_OUTPUT=out.txt python3 "$1"' "$W/ag" "$AG"
expect "actor-gate/capability-missing-refused" "ACTOR_CAPABILITY_MISSING" 1 -- \
  bash -c 'cd "$0" && env ACTOR=deployer-login REQUIRED_CAPABILITIES=production-approval MACHINE_DISPATCH_CLASS=none GITHUB_OUTPUT=out.txt python3 "$1"' "$W/ag" "$AG"

# ------------------------------------------------------------- identity gate
IG="$W/identity.py"
$X .github/workflows/workflow-identity-gate.yml workflow-identity-gate \
   "Compare the approving identity with the deploying identity" --python > "$IG"

for d in approvals-clean approvals-self approvals-wrongdigest approvals-empty; do
  cp -r "$F/$d" "$W/$d"; : > "$W/$d/out.txt"
done

expect "identity/clean-passes" "IDENTITY_GATE_PASS" 0 -- \
  bash -c 'cd "$0" && env PRODUCT=demo DIGEST="$1" DEPLOYING_ACTOR=deployer-login GITHUB_OUTPUT=out.txt python3 "$2"' "$W/approvals-clean" "$D1" "$IG"
# charter DoD-04 — the exact string, no substitute accepted.
expect "identity/self-approval-refused" "APPROVER_EQUALS_DEPLOYER" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo DIGEST="$1" DEPLOYING_ACTOR=deployer-login GITHUB_OUTPUT=out.txt python3 "$2"' "$W/approvals-self" "$D1" "$IG"
expect "identity/substituted-digest-refused" "APPROVAL_DIGEST_MISMATCH" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo DIGEST="$1" DEPLOYING_ACTOR=deployer-login GITHUB_OUTPUT=out.txt python3 "$2"' "$W/approvals-wrongdigest" "$D1" "$IG"
expect "identity/no-approval-refused" "NO_APPROVAL_RECORD" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo DIGEST="$1" DEPLOYING_ACTOR=deployer-login GITHUB_OUTPUT=out.txt python3 "$2"' "$W/approvals-empty" "$D1" "$IG"
expect "identity/unresolvable-deployer-refused" "DEPLOYER_UNRESOLVED" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo DIGEST="$1" DEPLOYING_ACTOR=ghost GITHUB_OUTPUT=out.txt python3 "$2"' "$W/approvals-clean" "$D1" "$IG"

# --------------------------------------------------------------- rollback leg
RB="$W/rollback.py"
$X .github/workflows/rollback.yml rollback-target \
   "Resolve the rollback target and the migration boundary" --python > "$RB"
for d in rollback-clean rollback-nomigfield; do cp -r "$F/$d" "$W/$d"; : > "$W/$d/out.txt"; done

expect "rollback/target-resolves-and-flags-migration" "ROLLBACK_TARGET_OK" 0 -- \
  bash -c 'cd "$0" && env PRODUCT=demo CURRENT_DIGEST="$1" CONFIRM_DIGEST="$2" GITHUB_OUTPUT=out.txt python3 "$3"' "$W/rollback-clean" "$D2" "$D1" "$RB"
expect "rollback/confirmation-mismatch-refused" "ROLLBACK_CONFIRMATION_MISMATCH" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo CURRENT_DIGEST="$1" CONFIRM_DIGEST="$2" GITHUB_OUTPUT=out.txt python3 "$3"' "$W/rollback-clean" "$D2" "$D3" "$RB"
expect "rollback/missing-migration-field-refused" "MIGRATION_BOUNDARY_UNRESOLVED" 1 -- \
  bash -c 'cd "$0" && env PRODUCT=demo CURRENT_DIGEST="$1" CONFIRM_DIGEST="$2" GITHUB_OUTPUT=out.txt python3 "$3"' "$W/rollback-nomigfield" "$D2" "$D1" "$RB"

# -------------------------------------------------------------- posture check
expect "posture/estate-passes" "PRIVILEGED_POSTURE_OK" 0 -- \
  python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml
expect "posture/zero-templates-is-not-a-pass" "PRIVILEGED_NO_TEMPLATES_CHECKED" 2 -- \
  python3 tools/evidence/assert-privileged-workflows.py --templates-dir "$W/empty-dir-does-not-exist"

rm -rf "$W"
echo "PASS=${PASS} FAIL=${FAIL}"
if [ "$FAIL" = "0" ] && [ "$PASS" -ge 20 ]; then echo "SUITE_PASS"; else echo "SUITE_FAIL"; fi
EOF
chmod +x tools/evidence/test/phase3/run-all.sh
bash tools/evidence/test/phase3/run-all.sh | tail -2
git add tools/evidence/test/phase3
git commit -m "L2-T572: phase 3 negative-test suite — every gate proven fail-closed (DoD-04, DoD-05)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The suite runs and passes | `bash tools/evidence/test/phase3/run-all.sh \| tail -1` | exactly `SUITE_PASS` |
| A2 | At least twenty cases ran | `bash tools/evidence/test/phase3/run-all.sh \| grep -c '^PASS '` | `20` or more |
| A3 | No case failed | `bash tools/evidence/test/phase3/run-all.sh \| grep -c '^FAIL '` | exactly `0` |
| A4 | DoD-04's exact string is proven, not merely present | `bash tools/evidence/test/phase3/run-all.sh \| grep -c 'PASS identity/self-approval-refused'` | exactly `1` |
| A5 | The suite is offline — no API call anywhere in it | `grep -c 'gh api\|curl \|wget ' tools/evidence/test/phase3/run-all.sh` | exactly `0` |
| A6 | The extractor compiles | `python3 -m py_compile tools/evidence/test/phase3/extract-step.py; echo $?` | exactly `0` |
| A7 | Re-running leaves the working tree clean | `bash tools/evidence/test/phase3/run-all.sh >/dev/null; git status --porcelain \| wc -l` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
OUT="$(bash tools/evidence/test/phase3/run-all.sh)"
test "$(printf '%s' "$OUT" | tail -1)" = "SUITE_PASS" \
 && test "$(printf '%s\n' "$OUT" | grep -c '^FAIL ')" = "0" \
 && test "$(printf '%s\n' "$OUT" | grep -c '^PASS ')" -ge "20" \
 && printf '%s\n' "$OUT" | grep -q 'PASS identity/self-approval-refused' \
 && printf '%s\n' "$OUT" | grep -q 'PASS runner-tier/undeclared-self-hosted-refused' \
 && printf '%s\n' "$OUT" | grep -q 'PASS actor-gate/machine-refused' \
 && printf '%s\n' "$OUT" | grep -q 'PASS rollback/missing-migration-field-refused' \
 && test "$(grep -c 'gh api\|curl \|wget ' tools/evidence/test/phase3/run-all.sh)" = "0" \
 && test "$(git status --porcelain | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T572 OK" || echo "L2-T572 FAIL"
```
Correct output: the single line `L2-T572 OK`.

**STOP rule:** a failing case in this suite means the gate it names does **not** fail closed. The repair is always to the gate, never to the test — deleting a case, loosening its expected token, or changing its expected exit code from `1` to `0` converts a proven control into an unproven one, which is precisely the state §64 (L5431) exists to forbid. STOP under **S6** and file the blocker naming the case label and the observed token. If the suite cannot run because a gate body could not be extracted (`EXTRACT_STEP_NOT_FOUND`), a step name in a workflow was changed without updating the extractor call: fix the extractor call, never rename the gate step to match the test.

---

### L2-T177 — Rebase, open the phase PR, exit

**Size:** S  **Depends on:** every task above

This is the last task of Phase 3. It performs no design and creates no file. It proves the branch is clean, rebases it, and opens one pull request against `integration` — the merge target fixed by `PARTITION.md` line 35.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
set -a; . ./tools/evidence/phase3-contract.env; set +a

# 1. Every gate of this phase still holds on the branch as it stands.
bash tools/evidence/phase3-preconditions.sh
python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml
bash tools/evidence/test/phase3/run-all.sh | tail -1

# 2. Nothing outside the three owned trees was touched (PARTITION.md rule 1).
git fetch origin integration
git diff --name-only origin/integration...HEAD \
  | grep -vE '^(\.github/workflows/|templates/workflows/|tools/evidence/)' \
  && { echo "FOREIGN PATH TOUCHED — STOP under S2"; exit 1; } || true

# 3. Rebase. A conflict outside the owned trees is STOP rule S3, not a merge.
git rebase origin/integration

# 4. Re-prove after the rebase. A rebase can silently take someone else's side.
bash tools/evidence/test/phase3/run-all.sh | tail -1
python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml

# 5. One pull request, base `integration`.
git push -u origin lane/2/phase3-production-gates
gh pr create --base integration --head lane/2/phase3-production-gates \
  --title "L2 Phase 3: production approval and isolation (Sections 27.2, 33.4, 37.3, 39.5)" \
  --body "$(cat <<'BODY'
Lane 2, Phase 3 — production approval and isolation.

Builds:
- the workflow-identity gate, the production-approval mechanism of record
  (Section 27.2 lines 2567-2576; D73 line 10156) — fails closed with the exact
  string APPROVER_EQUALS_DEPLOYER on self-approval (charter DoD-04)
- the rollback workflow and its narrow, declared D52 exemption
  (Section 27.2 line 2575; D52 line 10120; invariant 27 line 9488)
- the actor gate on every privileged workflow
  (Section 37.3 lines 3261-3268; invariant 18 line 9477)
- privileged-workflow runner isolation, hosted by default
  (Section 39.5 lines 3589-3596; D87 line 10180)
- the deployment branch and tag policy assertion
  (Section 33.4 line 2911; D91 line 10184)

Proof in this branch:
- tools/evidence/test/phase3/run-all.sh prints SUITE_PASS
- tools/evidence/assert-privileged-workflows.py prints PRIVILEGED_POSTURE_OK
- every file changed is under .github/workflows/, templates/workflows/ or
  tools/evidence/

Open decisions filed for L0, each with a fail-closed stub in place and NOT a
skipped step: D-L2-08 (verification-block store), D-L2-09 (privileged-runner
markers), D-L2-10 (exceptional-authorisation store).
BODY
)"
gh pr view --json baseRefName --jq .baseRefName
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | All fourteen phase artifacts exist | see SELF-VERIFY | exactly `MISSING=0` |
| A2 | The suite passes on the rebased branch | `bash tools/evidence/test/phase3/run-all.sh \| tail -1` | exactly `SUITE_PASS` |
| A3 | The posture assertion passes | `python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml` | exactly `PRIVILEGED_POSTURE_OK checked=1` |
| A4 | No foreign path in the whole branch | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |
| A5 | The PR targets `integration` | `gh pr view --json baseRefName --jq .baseRefName` | exactly `integration` |
| A6 | Exactly one PR open from this branch | `gh pr list --head lane/2/phase3-production-gates --json number --jq 'length'` | exactly `1` |
| A7 | No `if:`, path filter or `continue-on-error` in any workflow this phase authored | `grep -rcE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/actor-gate.yml .github/workflows/runner-tier-assert.yml .github/workflows/env-policy-assert.yml .github/workflows/workflow-identity-gate.yml .github/workflows/production-gate-chain.yml .github/workflows/rollback.yml \| grep -vc ':0'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
MISSING=0
for f in \
  tools/evidence/phase3-preconditions.sh \
  tools/evidence/phase3-contract.env \
  tools/evidence/apply-production-gates.py \
  tools/evidence/assert-privileged-workflows.py \
  tools/evidence/test/phase3/extract-step.py \
  tools/evidence/test/phase3/run-all.sh \
  .github/workflows/actor-gate.yml \
  .github/workflows/runner-tier-assert.yml \
  .github/workflows/env-policy-assert.yml \
  .github/workflows/workflow-identity-gate.yml \
  .github/workflows/production-gate-chain.yml \
  .github/workflows/rollback.yml \
  templates/workflows/runner-tier-assert.step.yml \
  templates/workflows/rollback.template.yml \
  templates/workflows/rollback-exemption.yaml ; do
  test -f "$f" || { echo "MISSING $f"; MISSING=$((MISSING+1)); }
done
echo "MISSING=$MISSING"
test "$MISSING" = "0" \
 && test "$(bash tools/evidence/test/phase3/run-all.sh | tail -1)" = "SUITE_PASS" \
 && test "$(python3 tools/evidence/assert-privileged-workflows.py --require rollback.template.yml)" \
      = "PRIVILEGED_POSTURE_OK checked=1" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && test "$(gh pr view --json baseRefName --jq .baseRefName)" = "integration" \
 && test "$(gh pr list --head lane/2/phase3-production-gates --json number --jq 'length')" = "1" \
 && echo "L2-T177 OK" || echo "L2-T177 FAIL"
```
Correct output: `MISSING=0` followed by the single line `L2-T177 OK`.

**STOP rule:** if `git rebase origin/integration` conflicts in any file outside the three owned trees, run `git rebase --abort` and STOP under `S3`. Do not resolve it — a foreign-path conflict means path ownership was violated (`PARTITION.md` rule 1). If step 4's re-run of the suite fails where step 1's passed, the rebase took another branch's side inside an owned tree: run `git rebase --abort`, re-run step 1, and file the blocker with both outputs. Never open the pull request on a branch whose suite does not print `SUITE_PASS`.

---

## 8. REQUIREMENTS THIS PHASE PLACES ON OTHER LANES

Lane 2 states these; Lane 2 does not implement them (charter §4.4). Each is stated because a gate built in this phase asserts it and refuses without it.

| # | Requirement | Owner | Spec | Which gate refuses without it |
|---|---|---|---|---|
| R1 | Every environment carries a deployment branch and tag policy restricting `staging` and `production` to the default branch and protected release tags | **L5** (`infra/**`) | §33.4 L2911; D91 L10184; §53.1 row L4661 | `env-policy-assert` → `ENV_POLICY_ABSENT` |
| R2 | `custom_branch_policies: true` rather than `protected_branches: true` on `staging` and `production` | **L5** | §33.4 L2911 | `env-policy-assert` → `ENV_POLICY_TOO_WIDE` |
| R3 | A read-only records-repository secret, exposed to every product repository, that the templates map onto the `RECORDS_READ_TOKEN` parameter | **L5** (`access/**`) | §40.1; §97.1 L8836 | `workflow-identity-gate` → `IDENTITY_GATE_RECORDS_UNREADABLE` |
| R4 | The records-writer credential named by `records_writer_secret_name`, scoped to the records repository alone | **L5** | §97.1 L8838; D89 L10182 | `rollback` → the record step cannot write |
| R5 | Privileged self-hosted runners registered `--ephemeral` in a group labelled `privileged`, each writing the two marker files at registration | **L5** (`infra/**`) | §39.5 L3591–3596; D87 L10191 | `runner-tier-assert` → `RUNNER_TIER_SHARED_POOL`, `RUNNER_TIER_NOT_EPHEMERAL` |
| R6 | `people.yaml` entries carrying `id`, `github_login`, `identity_class`, `availability`, `access_status` and `capabilities`, with `production-approval`, `incident-response` and `devops` defined | **L1** (`registries/**`) | §37.3 L3267; §9.1; D90 L10186 | `actor-gate` → `ACTOR_GATE_REGISTRY_UNREADABLE` |
| R7 | The deployment-record schema accepting `approved_by`, `approval_event`, `digest` and an orderable `timestamp` | **L4** (`schemas/records/**`) | §97.2 L8848, L8916–8925 | `workflow-identity-gate` → `NO_APPROVAL_RECORD` |
| R8 | A boolean `migration_applied` on the deployment record, so a rollback can tell whether a migration boundary lies in its window | **L4** | §27.2 L2575; §34.3 | `rollback` → `MIGRATION_BOUNDARY_UNRESOLVED` |
| R9 | `rollback_initiated` present in the `platform.yaml` event-type enum | **L1** | §97.3 L8950 | `rollback` → `ROLLBACK_EVENT_TYPE_UNRESOLVED` |
| R10 | `create-product` substituting `{{PRODUCT_SLUG}}`, `{{TARGET_REPO}}`, `{{RUNNER_LABEL}}` and `{{SELF_HOSTED}}` in `rollback.template.yml`, and naming the result `rollback_workflow_filename` | **L3** (`tools/provision/**`) | §19.1; §33.2 | the template is inert until it is instantiated |
| R11 | The three §53.1 Blocking drift rows for the D87 posture — non-ephemeral runner in the `privileged` group, privileged workflow on a shared-pool label, branch-push workflow in the `privileged` group | **L3** (`validators/drift/**`) | §53.1 L3599 | nothing in this phase detects the estate-side half |
| R12 | The `# >>> … v1` / `# <<< … v1` anchor pairs added to `deploy-production.template.yml`, `migrate.template.yml`, `restore-production.template.yml` and `deploy-staging.template.yml` when those phases author them, and the redeploy leg wired into `rollback.template.yml` | **later L2 phase** | charter DoD-01, DoD-05 | `apply-production-gates.py` → `GATE_ANCHOR_ABSENT`; `assert-privileged-workflows.py` cannot reach `checked=5` |
| R13 | Publication of `verification_block_store`, `exceptional_authorisation_store`, `privileged_runner_marker_path` and `ephemeral_runner_marker_path` in `contracts/**` | **L0** | §27 L2551; §27.2 L2575; D87 L10191 | `L2-T170` → `PHASE3_CONTRACT_KEY_MISSING`; the two fail-closed stubs never clear |

**R12 is the row that moves DoD-05 from partial to complete.** Until the other four privileged templates exist and carry anchors, `assert-privileged-workflows.py` reports `checked=1`. That is the honest number, and the tool prints it rather than implying coverage it does not have.

---

## 9. WHAT THIS PHASE DELIBERATELY DOES NOT DO

Restated here in task terms, so that a sibling Lane 2 phase document cannot claim the same ground and so that scope does not drift inside this one.

| Not here | Where it belongs | Why |
|---|---|---|
| `deploy-production.yml`, `deploy-staging.yml`, `migrate.yml`, `restore-production.yml` | later L2 phase | §33.2 required workflows. This phase builds the gates those workflows call, and the assertion that proves they call them |
| The redeploy leg of the rollback template | later L2 phase (owner of `deploy-production.yml`) | §8 row R12. A declared seam, wired by `apply-production-gates.py`, never a to-do in a workflow file |
| The Friday-freeze time gate | later L2 phase | §34.2 L2930–2935; charter E-7 |
| The digest invariant (§32 item 5 = item 11) | earlier L2 phase (E-3) | §0.1. This phase consumes the digest; it does not re-verify the chain |
| The eleven-question evidence assembler and `verify-digest-chain` | subsystem F, sibling L2 phase | §32 L2803–2828; §99.2 L9215 |
| Applying any environment policy, ruleset or branch protection | **L5** | charter §4.4; `L2-T173` acceptance row A6 forbids a mutating API verb in this tree |
| Registering, labelling or provisioning any runner | **L5** | §39.5 L3591. This phase asserts the tier from inside the job |
| Record and event **schemas**, and the `exceptions.yaml` shape | **L4**, **L0** | `PARTITION.md` line 20; §54.1 L4753 |
| Editing `contracts/**` to resolve D-L2-08, D-L2-09 or D-L2-10 | **L0** | `PARTITION.md` rule 2. File a Contract Change Request |
| Anything under subsystems G, H, J, O, P | **unassigned in `PARTITION.md` v1 — route to L0** | This phase claims none of them and depends on none of them |

---

## 10. SPEC CITATION INDEX FOR THIS FILE

Every rule this document imposes traces to one of these. Nothing else was used, and nothing here was invented.

| Cited as | Lines | What it fixes here |
|---|---|---|
| §11.4 table row | 881 | environment required reviewers are Enterprise-only; the workflow-identity gate is the mechanism of record on the Team plan |
| §23.1 | 2313 | a verification block is a recorded artifact, not a message |
| §26.2 | 2514 | a written record in the decision store, rather than an append to a shared file |
| §27 | 2551 | production approval and `deploy-production.yml` fail closed while an open verification block exists |
| §27.1 | 2557–2565 | the single production-approval routing table |
| §27.2 | 2567–2576 | the workflow-identity gate; the rollback exemption and its exact scope; the actor gate as the one check it does not lift |
| §32 | 2803–2828 | the artifact identity this phase's gates compare against |
| §33.2 | 2854–2869 | no `if:`, no path filter, no skip on a required context; pinned-tag consumption; least-privilege tokens |
| §33.3 | 2871–2886 | shared workflows are consumed by pinned tag, never by branch |
| §33.4 | 2887–2912 | environments, environment-scoped secrets, and the deployment branch and tag policy that makes them true |
| §34.3 | 2941–2960 | migrations are CI-only — the boundary a rollback must report |
| §37.3 | 3261–3268 | the actor gate as the first step of every privileged workflow; the three capabilities; the positive machine allowlist |
| §39.5 | 3589–3596 | the closed privileged set; hosted by default; the `--ephemeral` `privileged`-group exception; assertion in the workflow |
| §40.1 | 3644–3686 | the five secret tiers, including the records-writer credential |
| §42.3 | 3788–3812 | the response flow in which rollback is the preferred first move |
| §44.5 | 4020 | the production-restore workflow and its exceptional-authorisation record |
| §47.2 | 4227–4232 | SEV-1 needs no prior authorisation; the exception record is still filed |
| §53.1 | 4653–4689 | the drift rows this phase's posture feeds, including the environment deployment branch and tag policy row (4661) and the workflow-file row (4675) |
| §54.1 | 4753–4785 | `exceptions.yaml` as a shared mutable file — why D-L2-10 exists |
| §64 | 5431–5460 | safe defaults; the unresolved resolves as denial |
| §94.7 | 8567 | the digest generators — the entire permitted machine dispatch set |
| §97.1 | 8836–8842 | the split write path; the records repository; UTC timestamps |
| §97.2 | 8843–8926 | the canonical record stores; `records/deployments/`; required, failing record and event writes |
| §97.3 | 8935–8952 | the binding event envelope; event types are enum identifiers, never free text |
| Invariant 18 | 9477 | the machine layer cannot deploy — enforced by the actor gate, not by policy |
| Invariant 22 | 9483 | the production artifact is the digest verified in staging |
| Invariant 27 | 9488 | rollback is preferred to hotfix and requires no prior approval during a SEV-1 |
| D52 | 10120 | the dedicated rollback workflow, exempt from required-reviewer approval, recorded as an exceptional authorisation |
| D73 | 10156 | the workflow-identity gate is the production-approval mechanism of record |
| D78 | 10161 | S18 platform-rebuild identity — why the digest regex admits a second form |
| D87 | 10180 | privileged-workflow isolation; hosted default; ephemeral exception; assertion in the workflow |
| D89 | 10182 | the records repository and its scoped writer credential |
| D91 | 10184 | deployment branch and tag policies are the control that makes environment-scoped secrets true |
| Charter DoD-04 | `L2-00-charter.md` §7 | the exact string `APPROVER_EQUALS_DEPLOYER` |
| Charter DoD-05 | `L2-00-charter.md` §7 | the actor gate is the first step of all five privileged workflows |
| `PARTITION.md` rules 1–5 | — | path ownership; contract-first; no shared mutable file; no cross-lane import; additive-only |

---

## 11. READING ORDER FOR THE EXECUTOR

1. `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — in full, first, always.
2. `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L2-00-charter.md` §2, §7, §9, §10 — owned paths, the Definition of Done rows DoD-04 and DoD-05, the standing decisions, and the verbatim blocker template.
3. This document §4, §5 and §6 — the consumed contract surface, the three open decisions, and the three phase-specific STOP rules — before running `L2-T170`.
4. Spec §27, lines 2545–2576 — the whole section, before `L2-T174` and `L2-T176`. It is four hundred words and it fixes both tasks.
5. Spec §37.3, lines 3261–3268 — before `L2-T171`.
6. Spec §39.5, lines 3585–3600, and D87, line 10180 — before `L2-T172`.
7. Spec §33.4, lines 2887–2912, and D91, line 10184 — before `L2-T173`.
8. Spec §97.2, lines 8843–8926 — the deployment-record shape and the required-failing-write rule — before `L2-T174` and `L2-T176`.

Nothing in this phase requires interpretation. Every literal string, regex, path, exit code and failure token is fixed by the task that creates it or by the specification line the task cites. Where a value is not stated in the spec and not fixed by a task above, it is a DECISION REQUIRED for L0 — never a judgment call for the executor, and never a default that permits.
