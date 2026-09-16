# 01 — Lane Architecture

**Status:** normative for the build. Subordinate to `implementation/PARTITION.md`, which is FROZEN.
**Governs:** the five build lanes plus L0, their subsystems, their exclusive path ownership, their contract consumption, their publications, their inter-lane dependencies, and the reason each boundary sits where it does.
**Spec under implementation:** `Research/MultiProduct_MasterSpec_v4.0.md` (10,256 lines). Subsystem letters A–R are Section 99.2. Phases are Section 98. Acceptance tests AT-001..AT-110 are Section 100. Invariants 1–111 are Section 101.

**Reader:** a Sonnet-4.6-class AI developer with no repo context and no judgment authority, plus one human/lead integrator (L0). Nothing in this file asks a lane to decide anything. Every open matter is routed to an explicit `L0 DECISION REQUIRED` block.

**Precedence rule, binding.** Where this file and `PARTITION.md` appear to disagree, `PARTITION.md` wins and this file is wrong. File a Contract Change Request against this file; do not act on the discrepancy.

---

## 1. The lane map on one page

| Lane | Branch prefix | Subsystems (Section 99.2) | Repo(s) touched | Merge-train position |
|---|---|---|---|---|
| **L0 Integrator** (human/lead) | `main`, `integration` | — (owns `contracts/**`, arbitrates all five) | control-plane, control-plane-records, product-template | Owns the train |
| **L1 Registries & Contracts** | `lane/1/*` | A, B | control-plane | 1st |
| **L4 Records, Events & Metrics** | `lane/4/*` | I, N | control-plane-records (all), control-plane (subset) | 2nd |
| **L2 Pipeline & Evidence** | `lane/2/*` | E, F | control-plane | 3rd |
| **L3 Reconciler & Provisioning** | `lane/3/*` | C, D | control-plane | 4th |
| **L5 Access, Infra & Ops** | `lane/5/*` | K, L, M, Q, R | control-plane | 5th |

Subsystems **G, H, J, O, P are not assigned to any lane by `PARTITION.md`.** This is not an oversight to be quietly patched by a lane — see §9, `L0 DECISION REQUIRED — LA-01`.

### 1.1 Subsystem dependency graph, verbatim from Section 99.2

| Subsystem | Depends on (Section 99.2 column) | Lane |
|---|---|---|
| A Control-plane repository | — | L1 |
| B Schema validation and CI gate engine | A | L1 |
| C Reconciliation engine | A, B, D | L3 |
| D Provisioning and scaffolding | A, B | L3 |
| E Reusable workflow library | A | L2 |
| F Evidence chain store and query | E | L2 |
| G Plan-checker and Gate 1 tooling | — | **unassigned** |
| H Dashboards and views | I, F, C | **unassigned** |
| I Metrics pipeline | A, E | L4 |
| J Background machine layer (conditional) | D, E | **unassigned** |
| K AI runtime contract enforcement | A | L5 |
| L Access-control architecture | A, D | L5 |
| M Operations VM | — | L5 |
| N Work tracking conventions | — | L4 |
| O Governance registries and jobs | A, C | **unassigned** |
| P People intelligence engine | I, L, A | **unassigned** |
| Q Asset inventory and deadline watch | A | L5 |
| R Notification routing | — | L5 |

Section 99.2's dependency spine, quoted: A (registries) → B (validation) → C (reconciliation) and D (provisioning); E (workflows) → F (evidence chain) → H/I (views and metrics); I is the feedstock for **nearly all** governance-tier and people-tier computation; P is hard-gated on L's datasource separation.

### 1.2 Why the merge train is L1 → L4 → L2 → L3 → L5 and not the subsystem graph

The subsystem graph says `I` (L4) depends on `E` (L2), yet L4 merges *before* L2. This is deliberate and must not be "corrected".

- **L4 merges second because it publishes the shapes L2 writes into.** L2's `deploy-production.yml` has a required, failing step that writes a deployment record and an event (Section 97.2). It cannot write a record until the record schema and the event envelope exist. L4's *schemas* precede L2's *writers*. L4's *metrics computation* (the part that genuinely depends on E) reads records that already exist and is therefore insensitive to merge order.
- **L3 merges fourth even though it depends on L5's access model, because it consumes that model through `contracts/**`, never through `access/**`.** This is anti-conflict rule 4 in `PARTITION.md`. If L3 ever imports from L5's tree, the ordering collapses and the two lanes deadlock.
- **L5 merges last because it is independent at build time.** Nothing L1–L4 builds reads L5 source. L5 arms the enforcement boundary over work that already exists, which is the correct order for an enforcement boundary — arming a gate before there is anything to gate is precisely the Phase 1 failure Section 98.2 warns about ("a team that experiences its merges mysteriously breaking").

---

## 2. Path-ownership manifest

This is the transcribable table. One owner per path; no path appears twice. Repo column: `CP` = `control-plane`, `CPR` = `control-plane-records`.

| # | Path glob | Repo | Lane | Subsystem | Spec anchor | Why this lane owns it |
|---|---|---|---|---|---|---|
| 1 | `contracts/**` | CP | **L0** | — | `PARTITION.md` rule 2 | The interface every lane codes against. If any lane could edit it, "contract-first" degrades into five private conventions and merges conflict on meaning rather than on text. |
| 2 | `CODEOWNERS` | CP | **L0** | — | Section 11.3 (generated, human identities only) | The file that *defines* ownership cannot be owned by a party it governs. Also: Section 11.3 requires CODEOWNERS be generated from registries and contain no machine identity; L0 arbitrates generator output vs. hand edits. |
| 3 | `docs/**` | CP | **L0** | — | Section 52.6 (`runbooks/`, `docs/control-plane-rebuild.md`) | Cross-lane prose. A lane documenting another lane's surface is a cross-lane import in prose form. |
| 4 | Repository root files (`README.md`, `.gitignore`, `.editorconfig`, `LICENSE`, `CONTRIBUTING.md`, and every other file at depth 0) | CP | **L0** | — | `PARTITION.md` row L0 | Root files are the one place five parallel branches always collide. Reserving depth 0 entirely removes the collision. |
| 5 | `Makefile` | CP | **L0** | — | Section 33.1 (the ten standard commands) | Single shared entry point. Five lanes appending targets to one Makefile is precisely the "shared mutable file" anti-conflict rule 3 forbids. |
| 6 | `schemas/registry/**` | CP | **L1** | A, B | Sections 5.1, 52.6 | The registry schemas (`people`, `roles`, `topology`, `platform`, `policies`, `exceptions`, `patterns`, `economics`, `platform-roadmap`, `tools`, `ai-toolchain`, `os-health`) are the root of the source-of-truth hierarchy. Everything validates against them; nothing they validate may define them. |
| 7 | `schemas/product/**` | CP | **L1** | A, B | Section 15.1 (Product Operating Contract), Section 31.1 (`verification/contract.yaml`), Section 20.1 (`service.yaml`) | The product contract schema is consumed by L2 (CI validation job), L3 (create-product emits a conforming `product.yaml`), L5 (access derives from the assignments block). One author, many consumers. |
| 8 | `registries/**` | CP | **L1** | A | Section 52.6 registry-of-files | The registry *files* themselves. Path ownership here means "owns the file and its schema", not "authors its content" — see §2.2. |
| 9 | `validators/registry/**` | CP | **L1** | B | Section 15.5, Section 26.4 (registry-change lane) | The validator must move in the same commit as the schema it enforces, or a schema change lands with no enforcement for one merge cycle. Co-locating them in one lane makes that impossible. |
| 10 | `.github/workflows/**` | CP | **L2** | E | Section 33.2 ("Reusable workflows live in the control-plane repository"), Section 52.6 row `workflows/` | GitHub only resolves a reusable workflow reference `owner/repo/.github/workflows/x.yml@ref` when the file is physically under `.github/workflows/`. Section 52.6 calls the artifact `workflows/`; `.github/workflows/**` is where that artifact must physically live. Same artifact, platform-mandated location. |
| 11 | `templates/workflows/**` | CP | **L2** | E | Section 33.2 ("All are generated from templates at product creation"), Section 19.1 | The per-repository workflow files (`ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `rollback.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml`, conditionally `background-queue.yml`) that L3's `create-product` stamps into product repos. Authored by the lane that owns what they call. |
| 12 | `tools/evidence/**` | CP | **L2** | F | Section 32 (eleven questions), Section 99.2 named tool `verify-digest-chain` | The evidence chain is assembled from what the pipeline emitted. Only the lane that wrote the emitters can guarantee the eleven questions are answerable. |
| 13 | `reconciler/**` | CP | **L3** | C | Sections 53.1–53.4 | The highest-privilege identity in the system (Section 99.6 risk 6). Isolating it in one lane means its blast radius has one reviewer set and one branch history. |
| 14 | `tools/provision/**` | CP | **L3** | D | Section 19.1, Section 12.1/12.2 | `create-product`, `add-person`, `change-role`, `remove-person`. Provisioning and reconciliation write the same GitHub surface; splitting them across lanes guarantees two divergent models of "declared state". |
| 15 | `validators/drift/**` | CP | **L3** | C | Section 53.1 comparison set | Drift validators are the reconciler's comparison rows expressed as code. They move with the reconciler or the comparison set silently narrows (Section 53.1: a silently narrowed comparison is itself visible drift). |
| 16 | `schemas/records/**` | CP | **L4** | I | Section 97.2, Section 97.3 (event envelope) | Record and event schemas are versioned contracts under Section 60.2. They sit in `control-plane` (not the records repo) because the records repo has no review protection (D107) and a schema must not be writable by the records-writer credential. |
| 17 | `metrics/**` | CP | **L4** | I | Section 97, invariant 46, invariant 49 | "Derived data is computed, never hand-maintained" (invariant 46). Every metric names the record store it derives from (Section 97.1) — the lane that owns the stores owns the derivations. |
| 18 | `tools/records/**` | CP | **L4** | I, N | Section 97.2 `RECORD-VERIFICATION-RESULT`, Section 97.5 (ready-queue-miss detector) | The record writers and the board automation. Co-located with the schemas they satisfy. |
| 19 | `access/**` | CP | **L5** | L | Section 11.2, 11.3, Section 33.4, Section 90 | The enforcement boundary: Teams derivation, branch protection JSON, ruleset JSON, environment deployment-branch/tag policies, five secret tiers, Layer B separation. Consolidated in one lane so that **no lane can weaken the gate that governs its own work**. |
| 20 | `infra/**` | CP | **L5** | L, M | Section 51.4, Section 51.5, Section 40.2 | Provider-side declarations and the `infrastructure:` boundary attestation surface. |
| 21 | `ops-vm/**` | CP | **L5** | M | Section 51.5, Section 45.4 (under-4-hour rebuild) | The disposable VM's entire provisioning. It is rebuilt from this path; splitting it across lanes makes the rebuild untestable. |
| 22 | `notify/**` | CP | **L5** | R | Section 92.11 (the closed push list) | The push list is closed and the destination is a configuration value, never hard-coded. One owner keeps the list closed; five owners reopen it by accretion. |
| 23 | `assets/**` | CP | **L5** | Q | Section 49, Section 40.1 fifth-tier operations | The operational asset inventory, including every fifth-tier machine credential's entry (rotation cadence, rotator, behavioural envelope, expiry). Owners in this file feed orphan detection. |
| 24 | `records/**` | **CPR** | **L4** | I | Sections 97.1, 97.2, 40.1 (D89) | The records repository exists precisely so the records-writer credential reaches no registry. One lane owns the whole repo. |
| 25 | `events/**` | **CPR** | **L4** | I | Section 97.3 | One file per event, never a concurrent append to a shared file — this is what makes parallel workflow runs, and parallel lane merges, conflict-free. |
| 26 | Everything else in `control-plane-records` (root files, `.github/**`) | **CPR** | **L4** | I | `PARTITION.md` row L4 ("ALL of `control-plane-records`") | Stated as ALL. No exception. |

### 2.1 Paths no lane owns

These exist in the spec's inventory (Section 52.6, thirty entries) or in `PARTITION.md`'s repo table but match no glob above. **A lane that finds itself needing one of these has hit a boundary, not a task.** STOP and open a blocker issue; see §9.

| Unowned surface | Spec anchor | Which lane would naturally want it |
|---|---|---|
| `changes/*.yaml` (change manifests) | Section 25, Section 52.6 | L2 (fleet migration), unassigned subsystem O |
| `scenarios/*.yaml` | Section 52.6, Section 72 | unassigned subsystem P/O; deferred per Section 99.4 |
| `templates/**` other than `templates/workflows/**` — record templates, issue templates, `templates/intake-gap-assessment.md` | Section 52.6, Section 96.6 | L4 (record/issue templates), L5 (intake gap assessment) |
| `runbooks/**` (credential-rotation runbook, deletion runbook, manual rollback path) | Sections 40.1, 45.4, 52.6, AT-029, AT-105 | L5 (ops), L3 (rotation), L0 (`docs/**` covers `docs/control-plane-rebuild.md` only) |
| Constitution file | Section 36.1, Section 52.6 | L5 (subsystem K). Covered by L0's "root files" **only if** it sits at depth 0. |
| Provisioned Grafana dashboard JSON | Section 92.3, Section 52.6, subsystem H | unassigned subsystem H |
| Compliance-artifact register (licence-scan results, SBOMs) | Section 48, Section 52.6 | L2 (subsystem E emits SBOMs) |
| Performance framework registry | Section 77, Section 52.6, phase P2 | unassigned subsystem P |
| `.github/ISSUE_TEMPLATE/**`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/dependabot.yml` in `control-plane` | Section 19.1 (CONFIGURE checklist issue), Section 42 (incident issue template) | L2 owns `.github/workflows/**` only — these are outside it |
| `product-template` repository (entire) | `PARTITION.md` Repositories table; Section 19.1 | L3 (`create-product` consumes it) or L2 (workflows) |
| The eight live `<product>` repositories | `PARTITION.md` ("onboarded per-product, not built") | No lane. Onboarding work, not build work. |
| Conduct-records store (sealed conduct records) | Section 52.6, Section 14.4 (escrow credential) | No lane. Owner is Founder, with external-adviser custody; closest to L0's direct-decision-record pattern, but it is not `docs/**` and matches no lane glob. |

### 2.2 Path ownership is not content authorship

This distinction is load-bearing and is violated by default if unstated.

- **L1 owns `registries/**`. The Founder owns `people.yaml`, `roles.yaml`, `topology.yaml`, `economics.yaml` and `scenarios/*.yaml`; the Team Lead owns `platform.yaml`, `os-health.yaml`, `policies.yaml`, `exceptions.yaml`, `patterns.yaml`, `platform-roadmap.yaml`, `tools.yaml` and `ai-toolchain.yaml`** (Section 52.6). L1 builds the schema, the validator, the directory and a *fixture* instance. L1 never authors real registry content. Real content arrives through the registry-change lane of Section 26.4: CI schema validation, plus review by the file's declared owner, plus the linked decision record where required.
- **L4 owns all of `control-plane-records`, but that repository has no review protection** (D107, `PARTITION.md` repo table). CODEOWNERS there is advisory. The enforceable controls on that repo are the no-bypass ruleset blocking force-push and deletion, records-writer commit signing, and the per-run head-SHA anchor written into `control-plane` by the reconciler (Section 40.1, D107). L4 builds those; L3 writes the anchor.
- **A lane owning a path may still not merge without L0.** `integration` → `main` is L0's alone.

---

## 3. CODEOWNERS, transcribable

CODEOWNERS resolves **last matching pattern wins**. Order below is therefore load-bearing: the L0 catch-all is first.

> **Superseded (Section 11.3).** The team-form CODEOWNERS (`@ORG/team-slug`) shown in the block below are superseded by the per-path CODEOWNERS generated by `L0-00-T03` using individual `@LEAD_GITHUB_LOGIN` entries. The team-slug form is preserved here as a structural reference only; the runtime file must contain human GitHub logins, not team slugs.

`control-plane/CODEOWNERS`:

```
# ==========================================================================
# GENERATED-SHAPE FILE — build-time lane ownership.
# Per Section 11.3 the runtime CODEOWNERS is generated from the registries
# and contains HUMAN IDENTITIES ONLY; no machine account ever appears here.
# Enforced negatively by the Phase 1 completion check (Section 98.2) and by
# the independent control verifier (Section 53.1).
# Source of truth for these rows: implementation/PARTITION.md (FROZEN).
# ==========================================================================

# --- L0 catch-all: everything not claimed below belongs to the integrator ---
*                           @ORG/lane-0-integration

# --- L0 explicit ---
/contracts/                 @ORG/lane-0-integration
/CODEOWNERS                 @ORG/lane-0-integration
/docs/                      @ORG/lane-0-integration
/Makefile                   @ORG/lane-0-integration

# --- L1 Registries & Contracts (subsystems A, B) ---
/schemas/registry/          @ORG/lane-1-registries
/schemas/product/           @ORG/lane-1-registries
/registries/                @ORG/lane-1-registries
/validators/registry/       @ORG/lane-1-registries

# --- L2 Pipeline & Evidence (subsystems E, F) ---
/.github/workflows/         @ORG/lane-2-pipeline
/templates/workflows/       @ORG/lane-2-pipeline
/tools/evidence/            @ORG/lane-2-pipeline

# --- L3 Reconciler & Provisioning (subsystems C, D) ---
/reconciler/                @ORG/lane-3-reconciler
/tools/provision/           @ORG/lane-3-reconciler
/validators/drift/          @ORG/lane-3-reconciler

# --- L4 Records, Events & Metrics (subsystems I, N) ---
/schemas/records/           @ORG/lane-4-records
/metrics/                   @ORG/lane-4-records
/tools/records/             @ORG/lane-4-records

# --- L5 Access, Infra & Ops (subsystems K, L, M, Q, R) ---
/access/                    @ORG/lane-5-access
/infra/                     @ORG/lane-5-access
/ops-vm/                    @ORG/lane-5-access
/notify/                    @ORG/lane-5-access
/assets/                    @ORG/lane-5-access
```

`control-plane-records/CODEOWNERS`:

```
# Advisory only. This repository carries NO review protection by design
# (PARTITION.md; Section 40.1, D89; D107). Its enforceable controls are the
# no-bypass ruleset (force-push/deletion blocked), records-writer commit
# signing, and the per-run head-SHA anchor written into control-plane.
*                           @ORG/lane-4-records
```

Substitute the organisation slug literally before committing:

```bash
set -euo pipefail
# from the control-plane repo root, on branch `integration`, run by L0 only
ORG_SLUG="REPLACE-WITH-GITHUB-ORG-SLUG"
sed -i "s|@ORG/|@${ORG_SLUG}/|g" CODEOWNERS
grep -c '@ORG/' CODEOWNERS   # MUST print 0
```

Self-verify the manifest and CODEOWNERS agree (run by L0 at the end of Phase 0; unambiguous output):

```bash
# Every lane glob in CODEOWNERS must appear exactly once.
awk '$1 ~ /^\// {print $1}' CODEOWNERS | sort | uniq -d
# MUST print nothing. Any output is a duplicated path == a two-owner path.
```

```bash
# No machine identity in CODEOWNERS (Section 11.3, Phase 1 completion check).
grep -nEi '\[bot\]|-bot|renovate|github-actions|records-writer|reconciler' CODEOWNERS
# MUST print nothing.
```

---

## 4. The lane-guard check

Anti-conflict rule 1: "A lane PR touching a foreign path FAILS the lane-guard check. No exceptions."

The guard derives the branch prefix from `GITHUB_HEAD_REF` and compares the PR's changed-file set against that lane's globs. Its ownership table is read from `contracts/lane-ownership.yaml` (L0-frozen), **not** from constants inside the workflow file, so that editing the guard's rules requires an L0-owned file.

```bash
#!/usr/bin/env bash
set -euo pipefail
# tools/... — reference implementation of the comparison, for L0 to place.
# Exit 0 = clean. Exit 1 = foreign path touched. No other exit code.
set -euo pipefail
BASE="${1:?base ref}"; HEAD="${2:?head ref}"; LANE="${3:?lane number}"
CHANGED="$(git diff --name-only "origin/${BASE}...${HEAD}")"
ALLOWED="$(yq -r ".lanes.\"L${LANE}\".owns[]" contracts/lane-ownership.yaml)"
VIOLATIONS=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  ok=0
  while IFS= read -r glob; do
    case "$f" in $glob) ok=1; break;; esac
  done <<< "$ALLOWED"
  [ "$ok" -eq 0 ] && VIOLATIONS="${VIOLATIONS}${f}"$'\n'
done <<< "$CHANGED"
if [ -n "$VIOLATIONS" ]; then
  echo "LANE-GUARD FAIL: lane L${LANE} touched foreign paths:"
  echo "$VIOLATIONS"
  exit 1
fi
echo "LANE-GUARD PASS: lane L${LANE}, $(echo "$CHANGED" | grep -c . ) files, 0 foreign."
exit 0
```

Every lane developer runs this locally before opening a PR:

```bash
git fetch origin integration
bash <path-to-lane-guard-script> integration HEAD <N>   # N = your lane number
# Required output: a line beginning "LANE-GUARD PASS". Anything else: STOP.
```

> **L0 DECISION REQUIRED — LA-02: where the lane-guard workflow file lives.**
> The guard must run as a GitHub Actions workflow, which means it must sit under `.github/workflows/`. `PARTITION.md` gives `.github/workflows/**` to **L2**. L2 would therefore own the check that constrains L2 — and, transitively, the `renovate-path-guard` (Section 33.2) and the independent control verifier (Section 53.1), which Section 53.1 requires to run "off the operations VM and under a different credential" from the reconciler.
> Options, all consistent with the frozen partition:
> **(a)** Add a CODEOWNERS override pinning the three specific files `.github/workflows/lane-guard.yml`, `.github/workflows/renovate-path-guard.yml`, `.github/workflows/control-verifier.yml` to `@ORG/lane-0-integration`, leaving the `.github/workflows/**` glob with L2. Path ownership stays L2; *review* ownership on three files moves to L0.
> **(b)** Run all three from a separate repository under L0 with a read-only fine-grained credential, which is the shape Section 53.1 already mandates for the control verifier.
> **(c)** Accept the exposure and rely on the tag ruleset with an empty bypass-actor list (Section 33.2) plus L0 review of every `integration` → `main` merge.
> Recommendation for L0's consideration: (a) for the lane-guard, (b) for the control verifier — because Section 53.1 already states "no control that can be rewritten by the credential it is checking is a control", and the same sentence applies to a lane and its guard.
> **Until L0 decides, no lane creates any of these three files.**

---

## 5. What L0 must freeze in `contracts/` before any lane starts

`contracts/**` is written by L0 in Phase 0 and FROZEN (`PARTITION.md` rule 2). Resolved by FD-013: exact filenames are frozen in PARTITION.md. The **surfaces** below are not optional — each is a place where two lanes touch, and a surface L0 leaves unfrozen becomes a merge conflict or, worse, two divergent implementations that both pass their own tests.

| # | Contract surface | Spec source | Producer lane | Consumer lanes |
|---|---|---|---|---|
| C1 | Event envelope (`event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`, `subject_ref`, `payload`) | Section 97.3 | L4 | L2, L3, L5 |
| C2 | The closed `event_type` enum (declared in `platform.yaml`, migrates as a contract schema does) | Section 97.3, Section 60.2 | L1 holds the file; L4 defines the taxonomy | L2, L3, L4, L5 |
| C3 | Record envelope (`record_schema_version`, `id`, `product`, `timestamp`; never edits in place) and the per-store shapes of the Section 97.2 table | Section 97.2 | L4 | L2, L3 |
| C4 | `RECORD-VERIFICATION-RESULT` `workflow_dispatch` input set (product, item, mechanism, pass/fail, evidence link) | Section 97.2 | L4 | L2 |
| C5 | Registry schema interface: `people.yaml`, `roles.yaml`, `topology.yaml`, `platform.yaml` field sets that other lanes read | Sections 7, 8, 66, 52.6 | L1 | L3, L5 |
| C6 | Product contract interface: the `assignments`, `classification`, `environments`, `recovery`, `infrastructure`, `data`, `commitments`, `ai_runtime_dependency` blocks | Section 15.1 | L1 | L2, L3, L5 |
| C7 | The eight reusable workflows' `inputs:`, `secrets:` and `outputs:` signatures — `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue` | Section 99.2 subsystem E; Section 33.2 | L2 | L3 (generates callers), L5 |
| C8 | The required-status-check **name list**, including `control-plane/blocking-drift` and `renovate-path-guard` | Sections 11.3, 33.2, 53.2 | L2 emits; L3 holds `blocking-drift`; L5 lists them in branch protection | all |
| C9 | Drift class enum — exactly `Green`, `Amber`, `Red`, `Blocking`, and no other severity vocabulary anywhere | Sections 6.7, 53.4 | L3 | L1, L2, L4, L5 |
| C10 | Reconciliation Levels 1–5 semantics and the auto-repair rule (stricter-only) | Sections 53.2, 53.3; invariant 81 | L3 | L5 |
| C11 | The Section 53.1 comparison-set row list (declared-vs-actual pairs and their on-mismatch behaviour) | Section 53.1 | L3 | L1, L5 |
| C12 | The eleven evidence-chain questions and their field sources | Section 32 | L2 | L4 |
| C13 | Five secret tiers and each fifth-tier credential's exact permission set and behavioural envelope | Section 40.1 | L5 | L2, L3, L4 |
| C14 | Permission model: org base Read, Teams-derived Write, the person-class table, Team structure | Section 11.2 | L5 | L3 |
| C15 | Branch-protection and environment-policy template shape | Sections 11.3, 33.4 | L5 | L2, L3 |
| C16 | Conformance profiles, the ten standard commands, the three endpoints (`/health`, `/version`, `/metrics`) | Sections 15.7, 33.1 | L1 (schema) / L2 (checks) | L3, L4 |
| C17 | Layer B separation interface: which datasource, which instance, three-state `allocation_state` | Section 90, D75 | L5 | L4 (must never emit people data into the general datasource — invariant 109) |
| C18 | `contracts/lane-ownership.yaml` — the machine-readable form of §2 above, consumed by the lane-guard | `PARTITION.md` rule 1 | L0 | all (read-only) |

**Contract Change Request, the only path.** A lane needing any of C1–C18 changed opens an issue titled `CCR: <surface> — <one-line reason>`, labels it `contract-change`, and **stops work on the dependent task**. It never edits `contracts/**`, and it never works around the contract locally. L0 answers, amends `contracts/**` on `integration`, and the lane rebases.

---

## 6. Lane specifications

Each subsection states: subsystems, owned paths, consumed contracts, published artifacts, dependency relationships, shape of work, the boundary reasons, the spec-anchored acceptance tests and invariants the lane must not break, and STOP rules.

---

### 6.1 L0 — Integrator (human/lead)

**Subsystems:** none of A–R directly. L0 owns the seams.
**Branches:** `main`, `integration`.
**Owns:** `contracts/**`, `CODEOWNERS`, `docs/**`, all repository root files, `Makefile`. Plus every decision block in this document set.

**Consumes:** nothing from any lane's source tree. L0 reads lane PRs and the merge-train gate output.

**Publishes:**
- `contracts/**` — frozen at end of Phase 0, amended only by CCR.
- `contracts/lane-ownership.yaml` — the machine-readable manifest of §2.
- `CODEOWNERS` — the build-time file of §3, replaced by the generated runtime file at Phase 3 (Section 11.3).
- `docs/control-plane-rebuild.md` — the under-4-hour rebuild runbook (Sections 45.4, 51.5, 52.6).
- `Makefile` — the ten standard commands' control-plane analogue (Section 33.1).
- Every `L0 DECISION REQUIRED` resolution, recorded as a decision record (Section 97.2, `records/decisions/`).

**Dependencies:** L0 blocks all five lanes at Phase 0 and gates all five at every merge.

**Shape of work:**
1. **Phase 0 (before any lane branch exists):** author and freeze C1–C18. Publish `contracts/lane-ownership.yaml`. Land `CODEOWNERS`. Resolve LA-01 and LA-02 below.
2. **Per cycle:** run the merge train L1 → L4 → L2 → L3 → L5. After each lane merges to `integration`, run the full gate. Only when the full gate passes does `integration` merge to `main`.
3. **Continuous:** answer CCRs. A CCR left unanswered blocks a lane; L0 answering "no" with a reason is a valid and fast answer.
4. **Every design-open item of Section 99.3 is L0's** — see §10.

**Boundary reasons:**
- *Why L0 owns `contracts/**` rather than the producing lane.* If L2 owned C7 (workflow signatures), L3's generated callers would break every time L2 refactored, and L3 would have no recourse but to read L2's source — anti-conflict rule 4 violated. Frozen contracts make L2's refactor invisible to L3 until L0 chooses to propagate it.
- *Why L0 owns root files.* Depth 0 is the highest-collision surface in any repository. Reserving it outright is cheaper than merging it five ways.

**Must not break:** invariant 82 (changes to this specification and its enforcing tooling follow the platform-change process: versioned, canaried, reversible); invariant 45 (the source-of-truth hierarchy resolves every conflict); AT-034 (governance layerability — each Section 98 phase adoptable in order with no change to the core).

**STOP rules:**
- If a lane PR requires a contract change, do not merge it. Answer the CCR first.
- If two lanes both claim a path, do not pick one. `PARTITION.md` is frozen; an unclaimed path is an `L0 DECISION REQUIRED`, resolved and recorded, never resolved implicitly by a merge.

---

### 6.2 L1 — Registries & Contracts (subsystems A, B)

**Branch prefix:** `lane/1/*`. **Merge-train position:** 1st.

**Owns:** `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` — all in `control-plane`.

**Subsystem A — Control-plane repository** (Section 99.2, complexity M, depends on nothing): versioned YAML registries and contracts — people, roles, assignments, platform, topology, per-product contracts and verification contracts, the governance files (`os-health`, `policies`, `exceptions`, `patterns`, `economics`, `platform-roadmap`, `tools`), the people-layer entities, and the record stores of Section 97 (the *schemas* for which are L4's — see the boundary note below).

**Subsystem B — Schema validation and CI gate engine** (complexity M, depends on A): multi-version schema validators; referential integrity (assignments name existing non-departed people; dependencies name existing services); date rules (mandatory end dates for non-employees, restore-tested within window, expired assignments fail); the 24x7-without-rota and commitments-conflict blockers; exception-without-expiry rejection; unclassified-control rejection.

**Consumes from `contracts/`:** C18 (lane ownership). L1 is the root of the dependency spine and consumes almost nothing; it *produces* C5, C6 and C16's schema half.

**Publishes:**
- JSON Schema files under `schemas/registry/**` for each of the Section 52.6 registry artifacts.
- JSON Schema files under `schemas/product/**` for `product.yaml` (Section 15.1), `verification/contract.yaml` (Section 31.1) and `service.yaml` (Section 20.1).
- A `validate-registry` CLI under `validators/registry/**` with a stable, machine-parseable exit contract.
- A fixture corpus under `registries/` — valid and deliberately invalid instances — which is how L2, L3, L4 and L5 test against L1 without importing L1's source.

**Dependency relationships:** L1 depends on no lane. L2, L3, L4 and L5 all depend on L1's published schemas *through `contracts/`*, and on L1's fixture corpus for tests. This is why L1 merges first.

**Shape of work:** high-volume, mechanical, additive-only. Roughly one file per registry artifact plus one validator rule per Section 15.5 / Section 26.4 rule. Every task is "write schema X to path P; write fixture pair (valid, invalid); the validator accepts the first and rejects the second with named error E." No task in L1 requires judgment.

**Boundary reasons:**
- *Why `validators/registry/**` is L1 and not L2 (which owns CI).* The validator and the schema must change in the same commit, or one merge cycle exists in which a widened schema has no enforcement. L2 owns the *workflow that invokes* the validator; L1 owns the validator itself. The seam is C8 (the check name), not the code.
- *Why `registries/**` is L1 though the Founder and Team Lead author its content.* Path ownership prevents merge conflicts; content authority is Section 52.6 and the registry-change lane of Section 26.4. Both hold simultaneously. See §2.2.
- *Why the record schemas (`schemas/records/**`) are L4 and not L1, despite subsystem A's description mentioning the record stores.* The records live in a separate repository with a separate credential (Section 40.1, D89). Whoever owns the store owns its schema, or the schema and the writer drift apart across a repository boundary that no single CI run spans.

**Must not break:** invariant 50 (people, roles, capabilities and assignments are separate concepts, each dynamic configuration); invariant 51 (people never hard-coded); invariant 52 (product count never hard-coded); invariant 77 (every exception has an expiry; an exception without one fails CI); invariant 80 (every control explicitly classified fail-closed or fail-open); invariant 61 (the framework in force is not architecture).
**Acceptance tests this lane's output is measured by:** AT-001 (add product 21 — no dashboard, workflow or script contains a product list), AT-002 (add a person), AT-007 (a new role), AT-009 (a new technology stack — conformance profile), AT-016 (second Team Lead: only `topology.yaml` changes), AT-047 (a declared `coverage_window` not covered by rota members' accepted windows fails contract validation), AT-049 (`ai_runtime_dependency` without an evaluation suite fails CI), AT-075 (banned measurements absent from the schema and rejected if introduced), AT-077 (framework fully mapped or explicitly marked).

**STOP rules:**
- If a schema field you are asked to add would require enumerating people or products anywhere, **STOP** — invariants 51 and 52. Open a blocker issue.
- If a validator rule you are asked to write requires reading a file outside `registries/**` or `schemas/**`, **STOP** — that is a cross-lane import. Open a CCR.
- If the spec section you are transcribing leaves the field type or enum genuinely open, **STOP**. Do not choose. Open an issue titled `L0 DECISION REQUIRED: <field> in <schema>` listing the candidate options.

---

### 6.3 L4 — Records, Events & Metrics (subsystems I, N)

**Branch prefix:** `lane/4/*`. **Merge-train position:** 2nd.

**Owns:** ALL of `control-plane-records` (`records/**`, `events/**`, its root files and `.github/**`), plus `schemas/records/**`, `metrics/**` and `tools/records/**` in `control-plane`.

**Subsystem I — Metrics pipeline** (complexity L, depends on A, E): DevLake nightly ingest; Prometheus scraping `/health`, `/version`, `/metrics`; Scorecard scheduled scan with drop detection; the event-log taxonomy; attention ledger; metric source discipline.

**Subsystem N — Work tracking conventions** (complexity M, depends on nothing): boards per product plus portfolio aggregate (or the single-Project fallback of Section 29), horizon semantics, Ready-to-Execute definition, automatic Ready-queue-miss recording.

**Consumes from `contracts/`:** C5, C6 (to know what a `product` field may contain), C12 (the eleven evidence questions, so deployment records carry the fields the chain needs), C13 (the records-writer credential's exact scope), C16 (the three endpoints Prometheus scrapes), C17 (the Layer B boundary it must never cross), C18.

**Publishes:**
- Record schemas for every store in the Section 97.2 table: `records/incidents/`, `records/postmortems/`, `records/uat/`, `records/estimates/`, `records/deployments/`, `records/restore-tests/`, `records/decisions/` (and `records/decisions/pending/`), `records/breaches/`, `records/deletion-requests/`, `records/security-reviews/`, `records/eval/`, `records/launches/`, `records/demos/`, `records/support/`, `records/onboarding/`, `records/leave/`.
- The event envelope schema and the closed `event_type` taxonomy content for C2.
- The `RECORD-VERIFICATION-RESULT` dispatch handler (C4).
- The `record-decision` CLI (Section 99.2 named tools; usable from a phone).
- Write-freshness declarations per store, computed from git commit timestamps on the store's path (Section 97.2).
- Metric definitions under `metrics/**`, each naming the record store it derives from.
- Board automation: the Ready-queue-miss detector of Section 97.5 and the estimate-vs-actual writer.

**Dependency relationships:** depends on L1 (C5, C6). L2 depends on L4 for record and event shapes — this is why L4 precedes L2 in the train. L3 depends on L4 for the head-SHA anchor's target shape. Unassigned subsystems H and P depend on I.

**Shape of work:** schema-heavy and file-heavy, near-perfectly parallel. One directory per store, one schema per store, one fixture pair per store, one freshness declaration per store. Then the derivation jobs, one per metric, each naming its store.

**Boundary reasons:**
- *Why L4 owns the entire records repository rather than sharing it.* D89: a credential described as writing "only `records/**` through a path-scoped bypass" is in fact an unscoped write credential on the repository holding `people.yaml`. The separation is architectural. One lane owning the whole separated repo keeps that property visible in the ownership table itself.
- *Why one file per event, never an append to a shared period file.* Section 97.3 states it for concurrent workflow runs; anti-conflict rule 3 states it for concurrent lane merges. Same mechanism, two reasons. **This is the single rule that makes the whole partition merge-clean, and it must not be optimised away.**
- *Why `schemas/records/**` sits in `control-plane` and not beside the records.* The records repository has no review protection (D107). A schema living there would be writable by the records-writer credential, which would make the schema no longer a contract.
- *Why L4 and not L2 owns the deployment-record schema, though L2's workflow writes it.* Invariant 46: derived data is computed, never hand-maintained, and metrics derive from the canonical stores. The store's shape is a metrics concern; the write is a pipeline concern. Seam = C3.

**Must not break:** invariant 40 (humans write decisions and meaning; machines write measurable state); invariant 46; invariant 47 (append-only for state, decisions, approvals and records; corrections are follow-up records, never in-place edits); invariant 48 (source extraction failure never downgrades existing verified data); invariant 49 (every metric has an owner and a defined response, or it is deleted); invariant 90 (attention hours, utilisation, PLU and output volume are never individual performance evidence); invariant 96 (no keystroke, screen, webcam or online-presence surveillance); invariant 98/99 (no single-number productivity score; no leaderboard); invariant 109 (general engineering dashboards carry no per-person raw-activity drill-downs; sensitive people data never enters the general engineering datasource); invariant 111 (no customer data in repositories — support records reference customer data by identifier, never by copy).
**Acceptance tests:** AT-075, AT-085 (AI output measured by value not volume), AT-087 (a KPI without evidence is marked *Not yet instrumented* or *Requires human input*, never proxied), AT-088 (source re-read failure is safe), AT-104 (a support email becomes a governed record with the first-response clock anchored to the received timestamp, D80), AT-105 (deletion request executes inside its SLA with the four timestamps, named executor and subprocessor propagation checklist in `records/deletion-requests/`), AT-046 (baseline integrity), AT-032 (self-observability includes dashboard freshness).

**STOP rules:**
- If a schema you are asked to write would place a customer's data — name, email body, identifier contents — into a record file, **STOP**. Invariant 111. Records reference by identifier only.
- If a metric you are asked to compute would produce a per-person figure visible on a general surface, **STOP**. Invariants 90, 98, 99, 109. Open a blocker issue.
- If you cannot name the record store a metric derives from, **STOP**. Section 97.1: a metric that cannot name its store does not ship.
- If a record write would be an in-place edit of an existing record file, **STOP**. Invariant 47.

---

### 6.4 L2 — Pipeline & Evidence (subsystems E, F)

**Branch prefix:** `lane/2/*`. **Merge-train position:** 3rd.

**Owns:** `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` — all in `control-plane`.

**Subsystem E — Reusable workflow library** (complexity L, depends on A): `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue` — consumed by pinned tag; the digest invariant enforced in code; parity job; delta-gated security and licence scanning; SBOM emission; Friday-freeze time gate.

**Subsystem F — Evidence chain store and query** (complexity M, depends on E): the eleven-question answerability for any production artifact; `/version` digest-match monitoring at 100%, any mismatch a P0 investigation; append-only history with effective dating.

**Consumes from `contracts/`:** C1, C3, C4 (it writes records and events), C5, C6 (it validates registries and product contracts in CI), C8 (the check names it must emit), C12 (the eleven questions), C13 (which secret tier each job may reach), C15 (which environments and refs its deploys may target), C16 (the ten commands, three endpoints, conformance profiles), C18.

**Publishes:**
- The eight reusable workflows under `.github/workflows/`, released at immutable tags in the `workflows/*` tag namespace.
- The per-repository workflow templates under `templates/workflows/**` that L3's `create-product` stamps out: `ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `rollback.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml` (wherever the product declares a `recovery:` block, Section 44.5), and conditionally `background-queue.yml`.
- `verify-digest-chain` under `tools/evidence/**` — the scheduled sweep comparing every production `/version` digest against its approval record (Section 99.2 named tools; also the outage-recovery gate of Section 46.1).
- The bulk fleet-migration PR script and the blast-radius generator of Section 33.3 (affected products, repositories, stacks, lifecycle states, risk assessment, proposed canary set) — generated by a script over the product registry, never assembled by hand.
- The required status-check contexts named in C8.

**Dependency relationships:** depends on L1 (schemas it validates) and L4 (record/event shapes it writes). L3 depends on L2 for C7 and for the templates it stamps. L5 depends on L2 only through C8 (the check names it lists in branch protection).

**Shape of work:** eight reusable workflows plus nine templates plus the evidence tooling. Each workflow is a discrete, testable unit. Highly parallel, but **not additive-only within a release** — a reusable workflow change is a platform change (Section 33.2) and moves under tag discipline.

**Boundary reasons:**
- *Why `.github/workflows/**` is the reusable library.* Section 52.6 names the artifact `workflows/`; GitHub only resolves `owner/repo/.github/workflows/x.yml@ref` when the file is physically at that path. The location is platform-mandated, not chosen.
- *Why `templates/workflows/**` is L2 and not L3, though L3 stamps them.* The template calls L2's reusable workflow with L2's `inputs:`. Splitting caller and callee across lanes means every signature change is a two-lane change. L3 consumes the template as an opaque artifact.
- *Why the `workflows/*` **tag ruleset** is L5's `access/**` and not L2's.* Section 33.2: a tag is movable and is therefore not a pin unless the ref itself is protected; the ruleset carries an empty bypass-actor list. Moving a tag executes new code in every product's pipeline with no PR, no manifest, no canary and no diff — it defeats the blast-radius apparatus and invariant 72 in one command. **A lane must not own the ruleset protecting its own release artifact.**
- *Why the independent control verifier is not L3's.* Section 53.1: reconciliation regenerates CODEOWNERS and re-applies branch protection and is also the only thing that checks them — "an instrument that can rewrite the wall it inspects". The verifier runs off the operations VM under a different credential. See LA-02.

**Must not break:** invariant 22 (the production artifact is the same digest verified in staging, never rebuilt); invariant 23 (never rebuild to work around registry unavailability); invariant 25 (production secrets environment-scoped, never present locally); invariant 27 (rollback preferred to hotfix, no prior approval during a SEV-1); invariant 71 (platform changes versioned, impact-analysed, canaried, verified, reversible); invariant 72 (portfolio-wide changes never reach the fleet without a canary); invariant 85 (GSD Core pinned to a tag; third-party Actions pinned to full commit SHAs; reusable workflows consumed by pinned tag); invariant 9 (no self-approval, via approval of the most recent reviewable push); invariant 12 (production approval is a separate event from Gate 2 and never self-approved).
**Acceptance tests:** AT-024 (a shared CI workflow breaks — canary catches it, tag rollback reverts, unmigrated products unaffected), AT-025 (contract schema change: both versions supported, no simultaneous fleet migration), AT-026 (pilot → rollout → fleet with per-stage verification and a tested rollback), AT-027 (a new platform policy propagates without hand-editing twenty product files), AT-035 (organisation export restores, each data class through its own recorded mechanism, Projects boards via GraphQL dump, D80), AT-103 (production restore without hand-held credentials: `restore-production.yml` generated from the template, executes end to end with an exceptional-authorisation record and no credential typed by a human), AT-049.

**STOP rules:**
- If a required status-check name would be emitted by a job carrying an `if:` or a path filter, **STOP**. Section 33.2: a skipped job reports a conclusion branch protection counts as satisfied; a `skipped` or `neutral` conclusion on a required context of a merged PR is Blocking drift.
- If a deploy path would rebuild rather than promote a digest, **STOP**. Invariant 22.
- If a workflow needs write permission beyond read, declare it explicitly per permission in the workflow file (Section 33.2). If it needs a secret from a tier above CI, **STOP** — invariant 25, Section 40.1.
- If you are about to move an existing `workflows/*` tag, **STOP**. Publish a new tag. Section 33.2, invariant 72.
- If you are asked to add a bypass actor to any ruleset, **STOP**. Only the split-ruleset Renovate case of Section 33.2 exists, and it is L5's to configure.

---

### 6.5 L3 — Reconciler & Provisioning (subsystems C, D)

**Branch prefix:** `lane/3/*`. **Merge-train position:** 4th.

**Owns:** `reconciler/**`, `tools/provision/**`, `validators/drift/**` — all in `control-plane`.

**Subsystem C — Reconciliation engine** (complexity L, depends on A, B, D): scheduled diff of declared versus actual GitHub state; graded responses at Levels 1–5 (Detect / Warn / Auto-repair / Block / Escalate); automatic expiry revocation; orphan detection at blocking severity; auto-repair only toward stricter declared state.

**Subsystem D — Provisioning and scaffolding** (complexity L, depends on A, B): `create-product`, `add-person`, `change-role`, `remove-person` — repo from template, Teams from registries, generated CODEOWNERS, branch protection, environments with scoped secrets, registration in every surface with zero hand-editing.

**Consumes from `contracts/`:** C5, C6 (declared state), C7 (workflow signatures, to generate callers), C9 (drift classes), C10 (levels and the stricter-only rule), C11 (the comparison-set rows), C13 (its own credential's exact permission set and behavioural envelope), C14 (the permission model it provisions from), C15 (the branch-protection and environment templates it applies), C18.

**Publishes:**
- The reconciliation job and its run record, including per-registry comparison counts (Section 53.1).
- The `control-plane/blocking-drift` check run on product repositories — status only, no content, approving nothing (Section 40.1, "the reconciler's check-run scope").
- The records-repository head-SHA and commit-count anchor written into `control-plane` once per run (Section 40.1, D107).
- The provisioning CLI: `create-product`, `add-person` (Phase 3, Section 98.2), then `change-role`, `remove-person`, template evolution (early hardening, Section 98.3).
- The generated CODEOWNERS for product repositories (human identities only, Section 11.3).
- Drift validators under `validators/drift/**`, one per Section 53.1 comparison row.
- The permanent seeded canary drift record (Section 53.1, AT-102).

**Dependency relationships:** depends on L1 (C5, C6) and, at build time, on **frozen contracts C14 and C15 only** — never on L5's `access/**` source. L5's access model arrives as data through `contracts/`. This is the single most important cross-lane rule in the partition, and it is why L3 can merge before L5.

**Shape of work:** the highest-risk lane and the smallest surface. Section 99.6 risk 6: "the reconciler is the highest-privilege identity in the system", and auto-repair is "the most dangerous code". Section 99.4 item 6 and Section 98.2 Phase 3 both bind: **detect-and-block only in Phase 3; auto-repair (Level 3) is early hardening (Section 98.3), enabled one repair class at a time.**

**Boundary reasons:**
- *Why C and D are one lane.* Section 99.2 lists C as depending on D. Provisioning writes the actual GitHub state; reconciliation compares declared against actual. Two lanes would produce two models of "actual" and the reconciler would flag its own sibling's writes as drift.
- *Why `validators/drift/**` is L3 and `validators/registry/**` is L1.* A registry validator answers "is this file well-formed?" — a schema question, L1. A drift validator answers "does the platform match the file?" — a comparison question, L3. Section 26.4 draws exactly this line: schema validation proves an edit is well-formed; it does not prove it was intended.
- *Why L3 must never write `records/**`.* AT-110 requires that from the reconciler's own credential, a `records/**` write **fails**, along with a GitHub Actions secret write, an environment write, a workflow-file change, an organisation-settings change and any Layer B access — while the credential still completes a normal reconciliation run. The anchor L3 writes goes into `control-plane`, not into the records repo.
- *Why L3 does not own its own verifier.* Section 53.1's independent control verifier runs off the ops VM under a different credential. See LA-02.

**Must not break:** invariant 44 (declared state reconciled; silent drift not permitted); invariant 55 (ownership changes are declarative and take effect through reconciliation); invariant 57 (departures trigger orphan detection; blocking orphans cannot be dismissed unresolved); invariant 58 (temporary assignments carry a mandatory end date and expire without human action); invariant 79 (new people, products and tools default to minimum privilege and draft state); invariant 81 (auto-repair may only move the system toward the declared, stricter state); invariant 87 (every architecture and security policy enforced by the platform wherever the platform can enforce it); invariant 53 (new products are configuration plus onboarding, never platform redesign).
**Acceptance tests:** AT-001, AT-002, AT-008 (contractor: reconciliation revokes on the end date without human action), AT-017 (a person leaves), AT-018 (a temporary assignment expires), AT-033 (no auto-loosening — a stricter-than-declared production control is raised for human review, never relaxed), AT-036 (a temporary access exception expires with no human action), AT-037 (an exception that cannot be auto-revoked becomes Blocking drift on its expiry date), AT-039 (a bootstrap exception cannot lapse silently), AT-102 (the seeded reconciliation canary — a run reporting zero findings is a FAILED run, raises SIG-13, and triggers the gap procedure), AT-110 (the reconciler credential is provably bounded — executed for real, re-executed at every rotation).

**STOP rules:**
- If a repair you are asked to implement could move actual state toward a *looser* control than declared, **STOP**. Invariant 81, Section 53.3, AT-033.
- If you are in Phase 3 and the task asks for Level 3 auto-repair, **STOP**. Section 98.2 Phase 3 and Section 99.4 item 6: detect and block only. Auto-repair is Section 98.3.
- If the reconciler would need write access to a GitHub Actions secret, an environment, a workflow file, organisation settings, `records/**`, or anything in Layer B, **STOP**. AT-110 requires all six to fail.
- If a generated CODEOWNERS would contain any machine identity, **STOP**. Section 11.3; the Phase 1 completion check verifies this negatively.
- If reconciliation reports zero findings including the canary, that is a FAILED run, not a clean one. Raise SIG-13; do not record it clean.

---

### 6.6 L5 — Access, Infra & Ops (subsystems K, L, M, Q, R)

**Branch prefix:** `lane/5/*`. **Merge-train position:** 5th.

**Owns:** `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` — all in `control-plane`.

| Subsystem | Section 99.2 summary | Cx | Depends on | Primary path |
|---|---|---|---|---|
| **K** AI runtime contract enforcement | Approved-runtime and approved-extension lists as configuration; API-key-free checks at onboarding and quarterly; secret-stripping pre-flight; constitution referenced from every context file; model-regression benchmark process | M | A | `access/**` (checks), `assets/**` (registry entries) |
| **L** Access-control architecture | Org base Read plus Teams-derived Write; branch and environment protection as the enforcement boundary; five secret tiers; fail-closed classification; the Layer B split — a second Founder-only Grafana instance carrying the separately-credentialed people datasource (D75), three-state field, generated self-view documents | M–L | A, D | `access/**`, `infra/**` |
| **M** Operations VM | DevLake, Grafana, reconciliation, health computation, Scorecard, Renovate, expiry checks, restore rotation, org export; disposable — rebuild under 4 hours from GitHub, tested quarterly; never in any product's runtime path; patched on the declared cadence of Section 62 | M | — | `ops-vm/**`, `infra/**` |
| **Q** Asset inventory and deadline watch | Certificates, domains, OAuth, signing, vendor contracts and announced vendor deprecations — each with owner, expiry and configurable-lead alert; owners in orphan detection | S–M | A | `assets/**` |
| **R** Notification routing | Actions webhook to messaging channel; per-product alert channels; documented phone-escalation path; Founder and Team Lead out-of-hours channel; no paging apps for developers | S | — | `notify/**` |

**Consumes from `contracts/`:** C5, C6 (the assignments block Teams derive from), C8 (the check names branch protection lists), C9, C10, C11 (so that the enforcement configuration and the reconciler's comparison set agree), C13 (which it also produces the concrete form of), C17 (which it produces), C18.

**Publishes:**
- The Teams derivation and permission model configuration (Section 11.2): org base Read, org-enforced 2FA, the Team-per-product structure, the two org-wide Teams for Team Lead and QA roles.
- The branch-protection template (Section 11.3) and every repository ruleset, including the `workflows/*` tag ruleset with an empty bypass-actor list (Section 33.2) and the split Renovate rulesets A and B (Section 33.2, D89, D74).
- Environment definitions with deployment branch and tag policies (Section 33.4) — `staging` and `production` accept the default branch and protected release tags only.
- The five secret tiers' concrete configuration and each fifth-tier credential's published permission set and behavioural envelope (Section 40.1).
- The `control-plane-records` no-bypass ruleset (force-push, branch deletion, tag deletion blocked) and records-writer commit-signing requirement (D107).
- The ops-VM compose and provisioning under `ops-vm/**`, plus the off-VM detection leg — external uptime check per product and the dead-man's-switch heartbeat (Section 51.5).
- The Layer B split (D75): the second Founder-only Grafana instance with its separately-credentialed people datasource, absent from the shared instance's provisioning.
- The operational asset inventory under `assets/**`, including each machine credential's rotation cadence, named rotator, runbook link, behavioural envelope and expiry date.
- Notification routing under `notify/**`: the Actions webhook into the designated messaging channel as a configuration value, per-product alert channels, the documented phone-escalation path.

**Dependency relationships:** depends on L1 (C5, C6) and, through contracts only, on C8 from L2. L3 depends on L5's *model* via C14/C15, never on L5's source. L5 is independent at build time and integrates last (`PARTITION.md`, dependency order).

**Shape of work:** configuration-as-code, five loosely coupled sub-surfaces, each independently testable. Q and R are S-complexity and can complete early; L is the long pole and is hard-gated by phase P2 (Section 98.6) for its Layer B half.

**Boundary reasons:**
- *Why the enforcement boundary is one lane.* Branch protection, rulesets, environments, Teams and secret tiers are the wall. If each lane configured the part of the wall that gated its own work, every lane would hold the ability to lower its own gate — which is the same failure Section 53.1 names for the reconciler and its own controls.
- *Why L5 owns the ruleset over L2's tags and over L4's repository.* Same reason, applied twice: the protected party never owns its own protection.
- *Why the Layer B separation is instance-level and not panel-level.* Section 99.5 and D75: "panel-hiding is explicitly insufficient — separation is at instance level and tested." AT-097 verifies the absence in the *provisioned configuration*, not inferred from panel visibility.
- *Why `ops-vm/**` is one path under one lane.* Section 51.5: complete loss is a tested under-4-hour rebuild. A rebuild assembled from five lanes' fragments is not testable as one procedure.

**Must not break:** invariant 24 (production database inaccessible from developer machines); invariant 26 (a fully compromised workstation must not yield production access); invariant 75/76 (the control plane observes products and is never in their runtime path; product runtime must not depend on control-plane availability); invariant 79 (minimum privilege and draft state by default); invariant 80 (every control explicitly classified fail-closed or fail-open); invariant 83/84 (fixed-cost tooling; no API keys in developer environments); invariant 86 (AI provider choice replaceable; an outage does not stop engineering); invariant 106 (individual people-performance intelligence on Layer B-M is Founder-only, gated by the `people-intelligence` capability, and **not delegable**); invariant 107 (Team Lead receives only minimum operational people data); invariant 109 (the underlying people datasource is separately credentialed; sensitive people data never enters the general engineering datasource); invariant 18 (the background machine layer cannot merge, approve, deploy, or reach production credentials — enforced by permissions and the actor gate, not by policy).
**Acceptance tests:** AT-011 (AI provider changes — the approved runtime list is configuration), AT-022 (founder continuity: the second organisation Owner or escrowed break-glass credential is verified usable, by periodic drill), AT-028/AT-029 (GitHub unavailable / control plane unreachable — products keep serving; a production rollback still executable via the documented manual path), AT-030, AT-031 (a named external **integration** removed changes nothing; the git host is exempt by the Section 62.5 carve-out), AT-032, AT-089, AT-090, AT-091, AT-092, AT-093, AT-094, AT-096, AT-097 (no people datasource in the shared Grafana instance — verified in the provisioned configuration, D75), AT-098 (the Founder-only instance is separately credentialed, D75), AT-100, AT-108 (the founder ops console is provably read-only: four attempts all fail, then a Layer A read query still answers), AT-109 (the background cage egress wall holds at the **host egress layer**, not by harness configuration, and the systemd wall-clock stop terminates at the window boundary, D69).

**STOP rules:**
- If any configuration would add a bypass actor to a ruleset carrying a compensating status check, **STOP**. Section 33.2, D89: a bypass actor is exempt from every rule in the ruleset it is listed on, so a compensator inside the bypassed ruleset compensates for nothing. The Renovate case is split across two rulesets for exactly this reason; ruleset B carries no bypass actor at all.
- If any configuration would place the people datasource in the shared Grafana instance, or achieve separation by hiding panels, **STOP**. AT-097, AT-098, D75, invariant 109.
- If any configuration would grant a delegate the `people-intelligence` capability, **STOP**. Invariant 106; AT-090 requires that an attempt to create such an assignment **fails validation**.
- If a required-status-check name you are asked to list is not in C8, **STOP**. Section 98.2 Phase 1: "A required check no workflow emits blocks every pull request indefinitely."
- If you are asked to arm branch protection before the Teams granting Write exist, **STOP**. Section 98.2 Phase 1 states the ordering explicitly and Section 95.4 names the result.
- If the ops VM would be placed in any product's runtime path, **STOP**. Invariants 75 and 76; Section 51.3.

---

## 7. Cross-lane interaction rules, restated as commands

These are `PARTITION.md`'s five anti-conflict rules made executable.

**Rule 1 — one owner per path.**
```bash
git fetch origin integration
bash <lane-guard-script> integration HEAD <N>
# Required: a line beginning "LANE-GUARD PASS". Anything else: do not open the PR.
```

**Rule 2 — contract-first.**
```bash
set -euo pipefail
git diff --name-only origin/integration...HEAD | grep '^contracts/' && \
  { echo "STOP: this branch edits contracts/. File a CCR instead."; exit 1; } || \
  echo "OK: no contract edits."
```

**Rule 3 — no shared mutable file.**
```bash
# No lane branch may modify a file another lane also modified this cycle.
git diff --name-only origin/integration...HEAD | sort > /tmp/mine.txt
# L0 runs this across all five lane branches; any intersection is a partition breach.
```

**Rule 4 — no cross-lane imports.** Every lane runs, before every PR:
```bash
# Replace FOREIGN with each path glob your lane does NOT own (from the §2 table).
git grep -nE '(^|[^A-Za-z0-9_/])(reconciler|tools/provision|validators/drift|schemas/records|metrics|tools/records|access|infra|ops-vm|notify|assets|schemas/registry|schemas/product|registries|validators/registry|tools/evidence|templates/workflows)/' -- . \
  | grep -v '^contracts/' | grep -v '^docs/'
# Review every hit. A reference to a path your lane does not own, outside
# contracts/ and docs/, is a cross-lane import. Remove it or file a CCR.
```

**Rule 5 — additive-only within a lane.** Prefer a new file to an edit. Editing is permitted only inside owned paths.

**Rebase discipline.** A lane branch lives less than one day and is rebased on `integration` before its PR:
```bash
git fetch origin
git rebase origin/integration
# A lane NEVER merges and NEVER rebases another lane's branch. (PARTITION.md)
```

---

## 8. Boundary reason register

A boundary whose reason is not stated will be violated. Each row states the boundary, the reason, and what breaks if it is crossed.

| # | Boundary | Reason | What breaks if crossed | Anchor |
|---|---|---|---|---|
| B1 | `contracts/**` is L0's alone | Frozen interfaces let five branches move without seeing each other | Lanes read each other's source; merge conflicts become semantic, not textual | `PARTITION.md` rule 2 |
| B2 | Root files and `Makefile` are L0's | Depth 0 is the highest-collision surface | Five-way conflicts on every cycle | `PARTITION.md` L0 row |
| B3 | Schema and its validator live in one lane (L1) | They must land in one commit | One merge cycle exists where a widened schema is unenforced | Section 15.5, 26.4 |
| B4 | Record schemas (L4) live in `control-plane`, records (L4) in `control-plane-records` | The records-writer credential must not be able to rewrite the schema it satisfies | The schema stops being a contract | Section 40.1, D89; D107 |
| B5 | One file per event and per record, never a shared index | Parallel workflow runs, and parallel lane merges, never contend | Merge conflicts return; the partition stops working | Section 97.3; `PARTITION.md` rule 3 |
| B6 | Reusable workflows sit at `.github/workflows/` | GitHub resolves reusable-workflow refs only from that path | The library is uncallable | Section 33.2; Section 52.6 row `workflows/` |
| B7 | Caller template (`templates/workflows/**`) and callee (`.github/workflows/**`) in the same lane | A signature change would otherwise be a two-lane change | Every workflow refactor blocks two branches | Section 33.2, 19.1 |
| B8 | The `workflows/*` tag ruleset is L5's, not L2's | A movable tag is not a pin; moving one executes new code fleet-wide with no diff | Blast-radius apparatus and invariant 72 defeated in one command | Section 33.2 |
| B9 | Provisioning (D) and reconciliation (C) in one lane | Both write and read the same "actual GitHub state" | Two divergent models of actual state; the reconciler flags its sibling's writes as drift | Section 99.2 (C depends on D) |
| B10 | Registry validators (L1) vs drift validators (L3) | "Well-formed" and "matches the platform" are different questions | Schema validation gets mistaken for intent validation | Section 26.4 |
| B11 | L3 consumes L5's access model through `contracts/`, never `access/**` | Lets L3 merge 4th and L5 merge 5th without deadlock | The merge train deadlocks; both lanes block | `PARTITION.md` rules 4, dependency order |
| B12 | The reconciler may not write `records/**`, secrets, environments, workflow files or org settings | The system's most privileged identity must be bounded by execution, not assertion | AT-110 fails; risk 6 of Section 99.6 materialises | AT-110; Section 40.1 |
| B13 | The independent control verifier runs off the ops VM, under a different credential, not under L3 | An instrument that can rewrite the wall it inspects is not a control | Branch protection and CODEOWNERS become self-attested | Section 53.1 |
| B14 | The enforcement boundary (branch protection, rulesets, environments, Teams, secret tiers) is one lane, L5 | No lane may weaken the gate that governs its own work | Every lane can lower its own gate | Sections 11.2, 11.3, 33.4, 40.1 |
| B15 | Layer B separation is instance-level, provisioned, and tested | Panel-hiding is explicitly insufficient | AT-097/AT-098 fail; invariants 106 and 109 breached | Section 99.5, D75 |
| B16 | Auto-repair is deferred out of Phase 3 into early hardening, one class at a time | It is the riskiest code in the system and needs detection to run clean for weeks first | Risk 6: a write-scope org-admin automation whose bug loosens security or locks everyone out | Sections 98.2 Phase 3, 98.3, 99.4 item 6, 99.6 risk 6 |
| B17 | `records/**` is unprotected against review and absolutely protected against rewriting | A store nobody reviews and anybody can rewrite is a record of nothing | Invariant 47 becomes an assertion | Section 40.1, D107 |
| B18 | Path ownership is not content authorship | Merge safety and editorial authority are different problems with different mechanisms | Lanes author registry content they have no authority over | Section 52.6; Section 26.4 |

---

## 9. Open partition matters — L0 decisions

> ### L0 DECISION REQUIRED — LA-01: five subsystems have no lane.
> `PARTITION.md` assigns 13 of the 18 subsystems of Section 99.2. Unassigned: **G** (plan-checker and Gate 1 tooling), **H** (dashboards and views), **J** (background machine layer, conditional), **O** (governance registries and jobs), **P** (people intelligence engine).
> This is consistent with Section 99.4's minimal honest V1: G is "L if built in-house" and Section 99.6 risk 4 makes its in-house build a *fallback* contingent on verifying capabilities against the pinned GSD release; H is deferred to a Founder view v0 from the GitHub API, reconciliation output and Scorecard; J is parked or activated by the CPU benchmark at Phase 3; O contributes only the exception registry with mandatory expiry to V1; P contributes nothing to V1 and is hard-gated on subsystem L (Sections 98.6 P2, P4).
> The decision L0 must make and record, **before the phase at which each activates**:
> **(a)** Extend an existing lane. Natural fits by dependency: O → L3 (O depends on A and C, and the exception-expiry mechanism is already reconciliation); H → L4 (H depends on I and F, and dashboards are provisioned configuration over metrics); P → L5 (P is hard-gated on L, which L5 owns, and its access boundary is the dominant constraint); J → L5 (the cage, the egress wall and the systemd stop unit are host controls, and AT-109 tests them at the host layer); G → L2 (Gate 1 tooling is CI-adjacent).
> **(b)** Open a sixth lane, `lane/6/*`, with its own path set — which changes the merge train and requires a `PARTITION.md` amendment.
> **(c)** Hold all five with L0 as directly-executed work, consistent with Section 98.7 ("no dedicated platform team") and with the fact that G, H, J, O and P each require judgment the AI-developer profile explicitly excludes.
> Whichever is chosen, the new paths must be added to the §2 manifest, `CODEOWNERS` and `contracts/lane-ownership.yaml` in one commit, and a decision record written to `records/decisions/`.
> **Until L0 decides: no lane creates a plan-checker, a dashboard JSON file, a Hermes cage configuration, a governance job, or any people-intelligence artifact.** A lane asked to do so files a blocker issue naming LA-01.

> ### L0 DECISION REQUIRED — LA-02: the lane-guard, the Renovate path-guard and the independent control verifier.
> Stated in full in §4. In summary: all three must be GitHub Actions workflows, `.github/workflows/**` belongs to L2, and each of the three constrains a party that would then own it. Options (a) CODEOWNERS file-level override to L0, (b) a separate L0 repository with a read-only fine-grained credential, (c) accept and compensate with the empty-bypass tag ruleset plus L0 review of `integration` → `main`.

> ### L0 DECISION REQUIRED — LA-03: the twelve unowned surfaces of §2.1.
> `changes/*.yaml`, `scenarios/*.yaml`, non-workflow `templates/**`, `runbooks/**`, the Constitution file, provisioned dashboard JSON, the compliance-artifact register, the performance framework registry, `.github/` non-workflow files in `control-plane`, the `product-template` repository, the eight live product repositories, and the Conduct-records store.
> Each must be assigned before the first lane task that needs it, or a lane will create it in whatever directory seems reasonable and two lanes will create it twice.
> Note the interaction with LA-01: dashboard JSON belongs to whoever gets H; the framework registry to whoever gets P; `changes/*.yaml` and `scenarios/*.yaml` to whoever gets O.
> Note also that the Constitution file is covered by L0's "root files" **only if** it is placed at repository depth 0. L0 should state its path explicitly.

> ### L0 DECISION REQUIRED — LA-04: `os-health.yaml` sits in an L1 path but is a metrics artifact.
> Section 52.6 places `os-health.yaml` in the control-plane repository as the metric register — "health-signal and Section 103 success-metric declarations: definitions, sources, thresholds, time windows, baselines, drift classes, tolerances, expected interpretations, known limitations, owners, activation dependencies, defined action on breach". By §2 row 8 its path is `registries/**`, which is L1's. Its schema is therefore L1's; its *content* is the Team Lead's (Section 52.6); its *consumers* are L4's metrics and L3's drift classification; and the health computation job that reads it is a Phase G1 deliverable under unassigned subsystem O or H.
> Options: **(a)** leave the file with L1 (schema only) and route the computation job by LA-01; **(b)** carve `registries/os-health.yaml` to L4 as a named exception to row 8 — which breaks "one owner per path" only at file granularity, not glob granularity.
> Recommendation for consideration: (a), because it preserves the glob and Section 52.6 already separates file ownership from schema ownership. Record whichever is chosen.

> ### L0 DECISION REQUIRED — LA-05: the closed `event_type` enum lives in `platform.yaml` (L1) but is authored by L4.
> Section 97.3 is explicit: "The enum is declared in `platform.yaml` beside the supported contract versions, because it migrates exactly as a contract schema does (Section 60.2); control-plane CI rejects any event whose `event_type` is absent from it, and the enum ships populated in Phase 1."
> `platform.yaml` is under `registries/**` (L1). The taxonomy content is L4's domain (Section 97.3's event list). Every workflow that emits an event (L2, L3, L5) depends on it.
> Options: **(a)** L1 owns the file and transcribes L4's taxonomy verbatim from `contracts/` C2 — a one-way copy from the frozen contract, so no lane authors into another lane's file; **(b)** the enum is a separate file under `schemas/records/**` (L4) that `platform.yaml` references, requiring a Section 52.6 amendment (a twenty-ninth-entry change, which Section 52.6 itself governs: "any proposal for a new control-plane artifact must state which existing file cannot hold the content").
> Recommendation for consideration: (a). Under (a), **adding an event type is a CCR against C2, never a direct edit by the emitting lane.**

---

## 10. Design-open items (Section 99.3) — all seven belong to L0

Section 99.3 names seven matters the specification deliberately leaves to the implementer, "each logged as such at build time". **No lane invents any of them.** A lane whose task appears to require one files a blocker issue naming the item number below.

| Section 99.3 item | What is open | Which lane would otherwise invent it | Routing |
|---|---|---|---|
| 1 | The attention classifier and constraint diagnosis algorithm — Healthy/Watch/Action Required with the reason on the same line, and "which constraint binds" | L4 (metrics) | L0. Phase G3 at the earliest. |
| 2 | The `make parity` declaration format — an environment-schema format defined once and reused | L2 (parity job), L1 (schema) | L0 defines the format; then L1 schematises it and L2 consumes it, in that order. |
| 3 | Plan-checker internals — verify every assumed capability against the exact pinned GSD release before configuring it; budget the in-house build if verification fails | unassigned subsystem G | L0, and see LA-01. Section 99.6 risk 4. |
| 4 | DevLake field coverage — routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread measures require bespoke computation; confirm coverage before Phase G3 | L4 | L0 confirms coverage; L4 implements only what L0 confirms. |
| 5 | Machine sources for the fifteen systemic context checks of Section 80 — the computable boundary is drawn by the builder | unassigned subsystem P | L0, and see LA-01. |
| 6 | KPI instrumentation projects — every Section 79 row marked "available after instrumentation" is its own mini-project | P: owned by L0 (FD-002) | L0 scopes each as its own project. |
| 7 | Calibration methods — PLU fit, forecast scoring, sustainable-utilisation bands, the Section 97.4 attention-session parameters, the Section 72.3 confidence table | L4 | L0. Section 99.3 leaves these as quarterly refits with no method prescribed; the *parameters* are calibrated configuration (Section 97.4 gives initial values: idle gap 30 minutes, granularity 0.25 hours) and L4 implements them as configuration, never as constants. |

**The general rule for all seven:** a lane implements the *mechanism* as calibrated configuration with the spec's stated initial value where one exists, and never hard-codes a threshold. AT-074: "Every 'sustained' threshold is configurable and refittable without code change."

---

## 11. Per-lane self-verification, before every PR

Every lane developer runs this block. Every line's required output is stated. Any deviation is a STOP.

```bash
set -euo pipefail
LANE="${LANE:?export LANE=1..5}"
git fetch origin integration

# 1. Rebased on integration (PARTITION.md branch model)
git merge-base --is-ancestor origin/integration HEAD && echo "OK rebased" || \
  { echo "STOP: rebase on origin/integration first"; exit 1; }

# 2. Branch prefix matches the lane
git rev-parse --abbrev-ref HEAD | grep -qE "^lane/${LANE}/" && echo "OK branch prefix" || \
  { echo "STOP: branch must be lane/${LANE}/<phase>-<task>"; exit 1; }

# 3. No contract edits
git diff --name-only origin/integration...HEAD | grep -q '^contracts/' && \
  { echo "STOP: contracts/ is L0-owned. File a CCR."; exit 1; } || echo "OK no contract edits"

# 4. Lane guard
bash <lane-guard-script> integration HEAD "${LANE}"   # must print LANE-GUARD PASS

# 5. Branch age (short-lived, < 1 day)
echo "branch first commit: $(git log --reverse --format=%cI origin/integration..HEAD | head -1)"
# If older than 24h: STOP, split the task and open a blocker issue.
```

**The universal STOP rule for every lane, from `PARTITION.md`:** *"No task may require designing, choosing, or interpreting. If a task needs judgment, it belongs to L0."* If your task requires you to decide anything — a field type, a threshold, a filename not given, a directory not in §2 — do not proceed. Open an issue titled `L0 DECISION REQUIRED: <one line>`, list the options you can see, and stop.
