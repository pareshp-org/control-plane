> **[SUPERSEDED — FD-B1-L2 2026-09-02]**
> This file has been superseded by L2-05-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L2-05-tasks.md

# L2-00 — LANE 2 CHARTER: PIPELINE AND EVIDENCE

**Lane:** L2 Pipeline & Evidence
**Subsystems:** E (Reusable workflow library), F (Evidence chain store and query)
**Branch prefix:** `lane/2/*`
**Merge-train position:** 3rd of 5 — `L1 → L4 → **L2** → L3 → L5`
**Authority:** subordinate to `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` (FROZEN). Where this charter and PARTITION.md appear to disagree, PARTITION.md wins and this charter is defective.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## 1. SCOPE

Lane 2 builds **the enforcement plane**. Every other lane produces declarations, records or configuration; Lane 2 produces the machinery that refuses to let a declaration be violated. When a product cannot deploy an unapproved digest, that refusal is a Lane 2 artifact. When the eleven evidence questions of Section 32 are answerable, the answer is assembled by a Lane 2 tool.

### 1.1 In scope

| # | Deliverable | Spec anchor |
|---|---|---|
| E-1 | The reusable workflow library in the control-plane repository, versioned by tag, consumed by pinned tag: `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue` | §99.2 row E (L9192); §33.2 (L2854–2869) |
| E-2 | The per-product workflow templates generated at product creation: `ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml`, conditionally `background-queue.yml` | §33.2 required-workflows paragraph (L2854–2869); §44.5 (L4016–4021) |
| E-3 | The digest invariant enforced **in code** — production deploy rejects any digest differing from the digest staging verified | §32 (L2803–2828); §33.4 (L2887–2912); invariant 22 (L9483) |
| E-4 | The workflow-identity gate on `deploy-production` — approving identity ≠ deploying identity, fail-closed | §27.2 (L2567–2576); D73 (L10156) |
| E-5 | The actor gate as **first step** of every privileged workflow (`deploy-staging`, `deploy-production`, `migrate`, rollback, production-restore) | §37.3 (L3261–3268); invariant 18 (L9477) |
| E-6 | Parity job; delta-gated security scanning; delta-gated licence scanning; slopsquat legitimacy check at execute time; SBOM emission beside the digest | §33.1–33.2 (L2831–2869); §48.1–48.3 (L4300–4320) |
| E-7 | Friday-freeze / core-hours time gate, resolved against the declared operating timezone, never runner local time | §34.2 (L2930–2935); §97.1 time rule (L8836–8842) |
| E-8 | The `renovate-path-guard` required status check (ruleset-B position, no bypass actor): fails on out-of-manifest diff **or** on any commit authored/committed by a non-Renovate identity | §33.2 Renovate paragraph (L2854–2869); D74 (L10157); D89 (L10182) |
| E-9 | The required-status-check name registry — the authoritative list of context names this lane emits, every one produced by a job carrying **no `if:` and no path filter** | §33.2 path-filter paragraph (L2854–2869); §98.2 Phase 1 completion check (L9024) |
| E-10 | Control-plane scheduled workflows: organisation-export job, restore-rotation scheduler, the `verify-digest-chain` scheduled sweep | §45.3 (L4064–4077); §44.2 (L3993–4002); §99.2 named tools (L9214–9231) |
| E-11 | Verification-contract presence check and the seeded-defect execution job (a run in which the seeded case **passes** is a FAILED run) | §31.2 (L2787–2794); SIG-18 (L4520–4587) |
| F-1 | `tools/evidence/` — the evidence-chain assembler answering the eleven questions of §32 for any production artifact | §32 (L2803–2828) |
| F-2 | `verify-digest-chain` — the digest-vs-approval sweep; scheduled, and runnable on demand as the outage-recovery gate that **gates resumption of production deploys** | §99.2 named tools (L9214); §46.1 recovery step 3 (L4090–4131) |
| F-3 | `/version` digest-match monitoring at 100%; any mismatch is a P0 investigation | §41.2 (L3717–3729); §32 item 11 (L2803–2828) |
| F-4 | Append-only history with effective dating in the evidence surface; conformance-profile substitution so a `client-app`, `library`, `batch`, `customer-hosted` or `static-site` product closes the chain on its declared equivalent evidence | §99.2 row F (L9193); §15.7 (L1587–1606) |

### 1.2 Explicitly OUT of scope for Lane 2

Naming these prevents the most likely lane collision.

| Not L2 | Owner | Why |
|---|---|---|
| `product.yaml` / registry JSON Schemas and their validators | L1 | `schemas/**`, `validators/registry/**` |
| Record and event schemas; `control-plane-records` content | L4 | L2 workflows *write* records at runtime; the schema is L4's |
| Reconciler, drift validators, `create-product` / `add-person` CLI | L3 | `reconciler/**`, `tools/provision/**`, `validators/drift/**` |
| Branch protection, rulesets, the `workflows/*` tag ruleset, environment configuration, secret tiering, runner hosts | L5 | `access/**`, `infra/**` |
| `contracts/**`, `CODEOWNERS`, `Makefile`, `docs/**`, root files | L0 | Frozen contract surface |
| Grafana/DevLake/Prometheus provisioning (subsystems H, I) | L4/L5 | `metrics/**` is L4 |
| Bulk fleet-migration PR script, change-matrix scaffold, blast-radius `affected:` generator | **unassigned** | See DECISION REQUIRED D-L2-01 |

---

## 2. OWNED PATHS — EXCLUSIVE

Lane 2 writes to exactly these three trees and nothing else. A Lane 2 pull request touching any other path fails the lane-guard check with no exception (PARTITION.md rule 1).

```
.github/workflows/**      # the reusable workflow library + control-plane CI + scheduled jobs
templates/workflows/**    # per-product workflow templates consumed by create-product
tools/evidence/**         # evidence-chain assembly, query, verify-digest-chain
```

**Consequence worth stating once:** because `.github/workflows/**` is L2's exclusively, the **lane-guard CI check itself is a Lane 2 file**. Lane 2 authors it from PARTITION.md's ownership table verbatim (task `L2-T004`). Lane 2 does not author `CODEOWNERS` — that is L0's.

**Additive-only discipline (PARTITION.md rule 5):** prefer a new workflow file over editing an existing one. Editing is permitted only inside the three trees above.

---

## 3. SUBSYSTEM MAPPING

| Subsystem | Spec row | Complexity (spec) | Depends on (spec) | Lane mapping |
|---|---|---|---|---|
| **E — Reusable workflow library** | §99.2 (L9192) | L (3–8 weeks) | A | `.github/workflows/**` + `templates/workflows/**` |
| **F — Evidence chain store and query** | §99.2 (L9193) | M (1–3 weeks) | E | `tools/evidence/**` |

Spec dependency spine (§99.2, L9226): `E (workflows) → F (evidence chain) → H/I (views and metrics)`. F is therefore internal to this lane and must not be started before E-3 (the digest invariant) exists, because F's central assertion is that item 5 and item 11 of §32 match.

Subsystem I (metrics) and H (dashboards) are **downstream consumers** of L2 output and belong to L4/L5. L2 publishes; it does not present.

---

## 4. WHAT LANE 2 CONSUMES

Per PARTITION.md rule 4, Lane 2 reaches into no other lane's source tree. It consumes exactly two ways: through `contracts/**`, or through a published artifact.

### 4.1 From `contracts/**` (L0, frozen in Phase 0)

| Consumed | Used by | If absent |
|---|---|---|
| Product-contract field names and the `conformance_profile` enumeration | E-2 templates, F-4 profile substitution | STOP — file blocker, cite §15.7 (L1587–1606) |
| Capability names `production-approval`, `incident-response`, `devops`, `migration-review`, `mobile-release` | E-4, E-5 gates | STOP — cite §37.3 (L3261–3268), §27.2 (L2567–2576) |
| The invocation contract for L1's validators (entrypoint + exit-code semantics) | E-6 `contract validation` and `registry and assignment validation` jobs | STOP — see DECISION REQUIRED D-L2-02 |
| The record/event write interface: records-writer secret name, target repository, record schema paths | E-1 deploy/restore/UAT record writes | STOP — see DECISION REQUIRED D-L2-03 |
| The `make parity` environment-schema declaration format | E-6 parity job | STOP — see REG-060 item 2 (spec marks this **design-open**, §99.3 item 2, L9232–9247) |
| Environment names `development`, `staging`, `production`, and environment-scoped secret names | E-1, E-2 | STOP — cite §33.4 (L2887–2912) |

### 4.2 From Lane 1 (schemas and validators) — as published artifacts

Lane 2's `ci` reusable workflow invokes L1's registry and contract validators. It invokes them **through the entrypoint declared in `contracts/`**, never by referencing a path under `schemas/**` or `validators/registry/**` in workflow source. If the workflow file contains the literal string `validators/registry/` or `schemas/registry/`, the task is wrong and must be re-done.

Merge-train consequence: **L1 merges to `integration` before L2 in every cycle.** L2 rebases on `integration` after L1's merge, never before.

### 4.3 From Lane 4 (records, events, metrics)

Lane 2 workflows are the **writers** of five record stores (§97.2, L8843–8926):

| Store | Written by which L2 artifact | Spec |
|---|---|---|
| `records/deployments/` | `deploy-staging`, `deploy-production` — a **required, failing step**, never best-effort | §97.2 write-freshness paragraph (L8843–8926) |
| `records/uat/` | the CI job on UAT completion, from `verification/uat.md` | §97.2 (L8843–8926); §31.1 (L2759–2786) |
| `records/restore-tests/` | `restore-test` / `restore-production` workflow, plus the RECORD-VERIFICATION-RESULT dispatch | §44.2–44.3 (L3993–4011); §97.2 (L8843–8926) |
| `records/eval/` | pin-change CI leg of the AI-eval runner | §97.2 (L8843–8926) |
| `events/` | **every** workflow that changes state — one file per event, never a concurrent append | §97.3 (L8927–8953) |

Lane 2 owns the **write step**; Lane 4 owns the **record shape**. L2 never edits `schemas/records/**`. Merge-train consequence: **L4 merges before L2.**

### 4.4 From Lane 5 (access and infra) — required, but not build-blocking

L2 states these requirements and L5 implements them. L2 does **not** configure them.

- The tag ruleset blocking updates and deletions on `workflows/*` with an **empty bypass-actor list** — without it a pinned tag is not a pin (§33.2, L2854–2869).
- Environment deployment branch and tag policies restricting `staging`/`production` to the default branch and protected release tags (§33.4, L2887–2912).
- Ruleset split A/B for the Renovate bypass; L2 emits `renovate-path-guard`, L5 places it in the ruleset that carries **no** bypass actor (§33.2; D89, L10182).
- The records-writer credential and its scope (§40.1, L3644–3686; D89).

---

## 5. WHAT LANE 2 PUBLISHES

| Artifact | Path | Consumed by |
|---|---|---|
| Reusable workflow library at tag `workflows/vN` | `.github/workflows/**` | Every product repository, by pinned tag |
| Per-product workflow templates | `templates/workflows/**` | L3 `create-product` (subsystem D) |
| `templates/workflows/required-checks.yaml` — the authoritative required-status-check context names | `templates/workflows/` | L5 (branch protection), L3 (reconciliation template comparison, §53.1 L4653–4689) |
| `tools/evidence/verify-digest-chain` | `tools/evidence/` | §46.1 recovery gate; scheduled sweep; L4 metrics |
| Evidence-chain query answering §32's eleven questions | `tools/evidence/` | Founder view (L5), Phase 6 completion check (§98.2, L9024) |
| `.github/workflows/lane-guard.yml` | `.github/workflows/` | Every lane's PR |

**Naming authority:** `templates/workflows/required-checks.yaml` is GENERATED FROM `contracts/workflows/required-checks.v1.yaml`. It is not the source of truth. A control in a path its own lane can rewrite is not a control (§53.1). `contracts/workflows/required-checks.v1.yaml` is the frozen contract (L0-owned); `templates/workflows/required-checks.yaml` is the generated output. L5 copies from `contracts/workflows/required-checks.v1.yaml`, not from the generated template.

---

## 6. MERGE-TRAIN POSITION AND BRANCH DISCIPLINE

```
per cycle:   L1 ──▶ L4 ──▶ [ L2 ] ──▶ L3 ──▶ L5 ──▶ integration
                                                        │
                                            full gate green
                                                        ▼
                                                      main
```

Rules, restated from PARTITION.md and binding on every L2 task:

1. One branch per task: `lane/2/<phase>-<task>` — e.g. `lane/2/phase0-charter`. Short-lived (< 1 day).
2. Rebase on `integration` **immediately before** opening the PR, and only after L1 and L4 have merged this cycle.
3. L2 never merges another lane's branch. L2 never rebases another lane's branch.
4. L2 merges to `integration` only. Never to `main`.
5. A rebase conflict outside `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` means someone violated path ownership. **STOP and file a blocker** — do not resolve it.

---

## 7. DEFINITION OF DONE FOR LANE 2

Lane 2 is done when every row below is provable by a command whose output is a exit code or an exact string. No row is satisfied by reading the code.

| # | Criterion | Proof |
|---|---|---|
| DoD-01 | All eight reusable workflows of §99.2 row E exist in `.github/workflows/` | `for w in ci build deploy-staging deploy-production migrate restore-test org-export background-queue; do test -f .github/workflows/$w.yml \|\| echo "MISSING $w"; done` prints nothing |
| DoD-02 | All required per-product workflows of §33.2 exist as templates | same loop over `templates/workflows/` for `ci build deploy-staging deploy-production migrate restore-test restore-production` prints nothing |
| DoD-03 | Digest invariant is enforced in code and fails closed | a negative test dispatching `deploy-production` with a digest ≠ the staging-verified digest exits non-zero and writes **no** deployment record |
| DoD-04 | Workflow-identity gate fails closed when approver == deployer | negative test exits non-zero; job log contains the exact string `APPROVER_EQUALS_DEPLOYER` |
| DoD-05 | Actor gate is the **first** step of all five privileged workflows | `tools/evidence/` check asserts step index 0 of each named workflow is the actor gate; exits 0 |
| DoD-06 | Every context in `required-checks.yaml` is emitted by a job with no `if:` and no path filter | grep-based assertion exits 0; a deliberately added `if:` on one such job makes it exit non-zero |
| DoD-07 | A `skipped` or `neutral` conclusion is impossible on a required context | negative test: a no-work run reports `success` with the literal recorded reason, not `skipped` |
| DoD-08 | Security and licence scanning are delta-gated (new findings only) | seeded legacy finding does not fail; seeded new finding does |
| DoD-09 | SBOM is emitted beside the digest for every production artifact build | artifact listing contains both digest and SBOM; assertion exits 0 |
| DoD-10 | Friday-freeze gate resolves against the declared operating timezone | test with runner TZ set to a timezone where local time is Thursday but declared time is Friday 15:01 → deploy refused |
| DoD-11 | `renovate-path-guard` fails on out-of-manifest diff **and** on foreign-authored commit | two negative tests, both exit non-zero |
| DoD-12 | Verification-contract seeded-defect case runs on every default-branch run; a **passing** seeded case fails the run | negative test exits non-zero and the run raises SIG-18 |
| DoD-13 | `verify-digest-chain` exits non-zero on any digest/approval mismatch and 0 on a clean estate | both directions tested |
| DoD-14 | The eleven questions of §32 are answerable for one real deployment | `tools/evidence` query emits all eleven fields, none empty; exits 0 (Phase 6 completion check, §98.2 L9024) |
| DoD-15 | Deployment-record and event writes are required, failing steps | negative test: record write blocked → deploy job fails |
| DoD-16 | `restore-production.yml` runs end to end with an exceptional-authorisation record and **no** human-typed credential | AT-103 (L9353) executed |
| DoD-17 | A shared workflow change is caught by canary and reverted by tag revert | AT-024 (L9337) executed |
| DoD-18 | Organisation export restores to an independent environment, each data class by its own recorded mechanism | AT-035 (L9345) executed |
| DoD-19 | Production rollback executes via the documented manual path with the control plane unreachable | AT-029 (L9341) executed |
| DoD-20 | No L2 pull request has ever touched a path outside the three owned trees | `lane-guard` green on every L2 PR in the cycle history |

---

## 8. COMPLETE LIST OF SPEC SECTIONS IMPLEMENTED BY LANE 2

Line ranges are inclusive, against `MultiProduct_MasterSpec_v4.0.md` (10,214 lines). Read with `sed -n 'A,Bp'`.

### 8.1 Primary — Lane 2 implements these

| Section | Lines | What L2 builds from it |
|---|---|---|
| §15.5 CI validation | 1564–1582 | The control-plane CI jobs that fail the build on each listed condition, including "a `recovery:` block and no `restore-production.yml`" |
| §25 Change Manifests | 2437–2488 | The manifest-driven canary/fleet workflow legs; `canary_result` and `fleet_verification` written by workflow runs |
| §27.2 No-self-approval mechanics | 2567–2576 | E-4 workflow-identity gate; the dedicated rollback workflow and its exemption boundary |
| §28.2 Progressive delivery | 2593–2620 | Deploy-with-change-disabled path; staged-rollout advance/halt capability check |
| §30.2 Plan-checker hard rejects | 2720–2732 | Only the execute-time half: the slopsquat legitimacy check run in CI against lockfile/manifest diffs |
| §31 Verification Contract | 2741–2802 | E-11 presence check, coverage-map check, seeded-defect execution, performance-mechanism required for high/critical |
| §32 Production Evidence Chain | 2803–2828 | F-1 the eleven questions; the item-5/item-11 invariant; the S18 platform-rebuild equivalence |
| §33.1 Local environment contract | 2831–2853 | Required-file presence check in CI (`.env.example`, `docker-compose.dev.yml`, `Makefile`, seed data, migration dir, `verification/`, `AGENTS.md`, `product.yaml` or pointer) |
| §33.2 Continuous integration | 2854–2869 | The whole CI job set; delta gating; path-filter prohibition; SHA pinning; least-privilege `GITHUB_TOKEN`; `renovate-path-guard`; workflow-file-change drift signal |
| §33.3 Shared workflow blast radius | 2870–2886 | Pinned-tag consumption discipline in templates (the `affected:` generator itself → D-L2-01) |
| §33.4 Artifacts and environments | 2887–2912 | Artifact immutability; the pipeline shape; environment usage in workflows |
| §34.1 Ship is redefined | 2915–2929 | The eight shipped conditions asserted by the deploy workflow; merged vs deployed as separate events |
| §34.2 Friday freeze | 2930–2935 | E-7 time gate, start-by-15:00 **and** observation-window-within-core-hours |
| §34.3 Database migrations | 2936–2944 | `migrate` reusable workflow: CI-only application, ordered/versioned, destructive-migration capability check, pre-migration verified backup |
| §34.4 Seven migration failure cases | 2945–2956 | Cases A–G encoded as the migrate/deploy workflow's branch behaviour and its records |
| §37.3 Prohibited by architecture | 3261–3268 | E-5 actor gate on the five privileged workflows; the machine account's positive dispatch allowlist checked inside each workflow |
| §41.2 The three required endpoints | 3717–3729 | F-3 `/version` digest-match monitoring; scrape-path assumptions for `/health`, `/version`, `/metrics` |
| §44.2 Restore-testing cadence | 3993–4002 | The nightly rotation scheduler workflow; `restore_tested` **derived** and written back from the newest passing record |
| §44.3 The four signals | 4003–4011 | Backup-success and restore-success assertions computed machine-side by the job |
| §44.5 The production-restore workflow | 4016–4021 | `restore-production.yml` template; forensic-snapshot stage first, blocking the restore stage; one workflow, two targets |
| §45.3 The organisation export | 4064–4077 | `org-export` reusable workflow: migrations REST API + separate Projects v2 GraphQL dump; append-only write-only credential usage; encryption; restore-test leg |
| §46.1 Degraded engineering mode | 4090–4131 | `verify-digest-chain` as the recovery-step-3 gate that blocks resumption of production deploys |
| §48.1 Pinning and provenance | 4300–4308 | Full-SHA action pinning enforced in CI; reusable-workflow pinned-tag consumption |
| §48.2 Licence scanning | 4309–4316 | Delta-gated licence scan job; the scanner policy configuration consumed as a control-plane artifact |
| §48.3 SBOM per artifact | 4317–4320 | SBOM emission in the same pipeline step as the digest |
| §61.1–61.5 Platform Change, Canary and Rollback | 5215–5286 | Canary exercise legs (`workflow_dispatch` of `ci.yml` and `build.yml` plus a staging deploy, recorded on the manifest); wave rule; `revert-reusable-workflow-tag` rollback method |
| §99.2 Subsystem architecture — rows E and F, named tools | 9184–9231 | The definition of this lane's surface |
| §100.3 Platform acceptance tests | 9333–9353 | AT-024, AT-029, AT-035, AT-103 executed by L2 |

### 8.2 Secondary — Lane 2 reads these but does not own them

| Section | Lines | Why L2 reads it |
|---|---|---|
| §15.7 Conformance profiles | 1587–1606 | F-4 evidence substitution per profile |
| §19.1 Product creation | 1826–1882 | Templates are consumed here by L3 |
| §23.2 Review routing table | 2315–2338 | Gate-2 identity referenced by the evidence chain (question 3) |
| §26.3 Exceptional authorisation | 2512–2525 | Rollback and production-restore runs are recorded as exceptional authorisations |
| §40.1 Five secret tiers | 3644–3686 | records-writer credential and its scope; L5 implements |
| §52.2 Unified signal table | 4520–4587 | SIG-12, SIG-14, SIG-17, SIG-18, SIG-34, SIG-42 are raised from L2 artifacts |
| §53.1 Declared versus actual | 4653–4689 | L3 compares protection/ruleset JSON against L2's published check-name list |
| §97.1–97.3 Records, events and data conventions | 8836–8953 | The write path and the store shapes L2 workflows write into |
| §98.2 Foundation Phases 1–7 | 9006–9090 | Phase 4/5/6 completion checks are L2's proof obligations |
| §101 Non-negotiable invariants | 9443–9600 | Invariants 18, 22, 23, 27, 28, 71, 72, 85, 87 are enforced by L2 code |

---

## 9. DECISION REQUIRED — HANDED TO L0

Lane 2 must not resolve any of these. Each blocks the tasks named. File as a Contract Change Request; never edit `contracts/**`.

### DECISION REQUIRED D-L2-01 — Home for the fleet-change scripts
**Question:** PARTITION.md assigns no lane the path for three named build-surface tools: the blast-radius `affected:` generator (§33.3, L2870–2886), the bulk fleet-migration PR script (§61.4, L5263–5280; §99.2 named tools, L9214–9231, subsystem "E, O") and the change-matrix scaffold (§99.2, subsystem O).
**Why L2 cannot decide:** creating `tools/fleet/**` would claim a path no lane owns, violating PARTITION.md rule 1.
**Options for L0:** (a) extend L2's ownership to `tools/fleet/**`; (b) assign to L3 under `tools/provision/**`; (c) defer all three to a later phase with a recorded accepted risk.
**Blocks:** every task implementing §33.3 and §61.4.

### DECISION REQUIRED D-L2-02 — L1 validator invocation contract
**Question:** `contracts/` must declare the stable entrypoint and exit-code semantics by which the `ci` reusable workflow invokes L1's contract and registry validators.
**Why L2 cannot decide:** inventing an entrypoint creates a cross-lane import (PARTITION.md rule 4) and breaks on L1's first refactor.
**Blocks:** the `contract-validation` and `registry-validation` jobs (DoD-06 partial).

### DECISION REQUIRED D-L2-03 — Record write interface
**Question:** `contracts/` must declare the records-writer secret name, the target repository, and the record schema paths for `records/deployments/`, `records/uat/`, `records/restore-tests/`, `records/eval/` and `events/`.
**Why L2 cannot decide:** the credential and schemas are L5's and L4's respectively; §97.2 (L8843–8926) makes the deployment-record and event writes **required, failing** steps, so a guessed interface makes every deploy fail.
**Blocks:** DoD-15, DoD-14.

### DECISION REQUIRED REG-060 item 2 — The `make parity` declaration format
**Question:** the environment-schema format that `make parity` and the CI parity job compare against.
**Why L2 cannot decide:** §99.3 (L9232–9247) lists this **explicitly as design-open** — "the `make parity` declaration format ... presumes an environment-schema format to be defined once and reused". Inventing it is a design act, which this lane's executor has no authority to perform.
**Blocks:** E-6 parity job; §98.2 Phase 4 completion check (L9024).

### DECISION REQUIRED D-L2-05 — Filename of the rollback workflow
**Question:** §33.2's required-workflow list (L2854–2869) does not include a rollback workflow, yet §27.2 (L2567–2576) mandates "a dedicated rollback workflow" and §37.3 (L3261–3268) names "the rollback workflow" among the five privileged workflows requiring the actor gate.
**Why L2 cannot decide:** the filename becomes a required-workflow name checked by §15.5 contract validation and by reconciliation's template comparison; choosing it unilaterally desynchronises L1, L3 and L5.
**Blocks:** E-5 (actor gate on the rollback workflow), DoD-05.

### DECISION REQUIRED D-L2-06 — Lane-guard bootstrap ordering
**Question:** the merge train runs `L1 → L4 → L2 → L3 → L5`, so L1 and L4 merge to `integration` before the lane-guard workflow (an L2 file, task `L2-T004`) exists.
**Why L2 cannot decide:** either L0 ships lane-guard in Phase 0 as an L0-authored exception to path ownership, or the first cycle's L1 and L4 merges run unguarded and are re-checked retroactively.
**Blocks:** DoD-20 for cycle 1 only.

---

## 10. STOP RULES AND THE BLOCKER TEMPLATE

Every Lane 2 task carries a STOP rule. Where a task's own rule does not cover the situation, these standing rules apply:

**S1.** If a required file under `contracts/**` is absent or contains a placeholder, STOP. Do not invent the value.
**S2.** If completing a task requires writing outside `.github/workflows/**`, `templates/workflows/**` or `tools/evidence/**`, STOP.
**S3.** If a rebase on `integration` produces a conflict outside the three owned trees, STOP. Do not resolve it.
**S4.** If a task requires choosing a name, a threshold, a format or an ordering that the spec does not state, STOP and file it as a DECISION REQUIRED for L0.
**S5.** If `git status` shows a modified file you did not intend to modify, STOP before committing.

### Blocker-issue template — file verbatim

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L2-<TASK-ID>: <one-line condition>" \
  --label "blocker,lane-2" \
  --body "$(cat <<'EOF'
LANE: L2 Pipeline & Evidence
TASK: L2-<TASK-ID>
STOP RULE TRIGGERED: <S1|S2|S3|S4|S5|task-specific>

WHAT I WAS DOING:
<the exact command run>

WHAT HAPPENED:
<exact output, verbatim, including exit code>

WHAT I NEED TO PROCEED:
<the single missing fact, file, or decision>

SPEC CITATION:
MultiProduct_MasterSpec_v4.0.md lines <A>-<B>, Section <N.N>

I HAVE NOT: guessed a value, written outside owned paths, edited contracts/**,
            resolved a foreign-path conflict, or continued past this point.
EOF
)"
```

---

## 11. CHARTER-LEVEL TASKS

These six tasks establish the lane. All later Lane 2 tasks depend on them. Every path below is inside an owned tree.

**Authority — `L2-T001`–`L2-T006` are defined here and nowhere else.** These six ids used to carry a full task body in **both** this section and `L2-05-tasks.md` §3, naming the *same* work under one identifier (`L2-99-review.md`, *Still open — not resolved here*, sixth bullet; `_INTEGRITY.md` finding 4, the last surviving cross-file body collision in the set). That is resolved, and the resolution is binding:

* **This section holds the authoritative body** for all six. Every sibling Lane 2 document already cites them as *charter* tasks — `L2-02-digest-invariant.md` §1 (*"phase 0 (`L2-00-charter.md`, tasks `L2-T001`–`L2-T006`)"*), `L2-03-production-gates.md` §7 (`L2-T170` *Depends on:* charter `L2-T001`, `L2-T002`), `L2-04-evidence-chain.md` §6 (`L2-T500` *Depends on:* `L2-T001` (charter)), `L2-06-tests.md` §9 (`L2-T600` *Depends on:* charter `L2-T001`) and `L2-07-runbook.md` §0 (*"created by charter task `L2-T003`"*). The charter is the only owner the estate is already consistent with.
* **`L2-05-tasks.md` §3 holds an index entry**, one line per id and no body. That file's §2 master-table rows 1–6 remain the execution-order rows; the body they point to is here. Its §2.1 concordance now lists all thirty-two moved or de-duplicated ids in one table.
* **Nothing was deleted.** Every criterion, command, expected output and STOP rule that existed only in `L2-05-tasks.md`'s copy is carried into the block it belongs to below, under a heading beginning **Carried over from `L2-05-tasks.md` §3**. Where the two copies specified *different* artifacts, the difference is recorded there and routed to L0 — never silently merged, never silently dropped.
* **One branch, not six.** These six tasks share the single branch `lane/2/phase0-charter`, opened by `L2-T001` and published by `L2-T006`, whose pull-request body reads *"Tasks L2-T001..L2-T005"*. The per-task branch protocol of `L2-05-tasks.md` §0.3 resumes at that file's task 7, `L2-T530`.

| Id | Authoritative body | Index entry | Content carried over from `L2-05-tasks.md` §3 |
|---|---|---|---|
| `L2-T001` | §11 of this file | `L2-05-tasks.md` §2 row 1, §2.1, §3 | criteria A4–A6 and a second STOP rule (`S2`) |
| `L2-T002` | §11 of this file | `L2-05-tasks.md` §2 row 2, §2.1, §3 | criteria A4–A5, a second STOP rule (`S1`), the lock-format difference |
| `L2-T003` | §11 of this file | `L2-05-tasks.md` §2 row 3, §2.1, §3 | the A3 correction for defect **B5**, its corrected SELF-VERIFY and its blocker |
| `L2-T004` | §11 of this file | `L2-05-tasks.md` §2 row 4, §2.1, §3 | criteria A7–A9, a second STOP rule (`S4`), two recorded implementation differences |
| `L2-T005` | §11 of this file | `L2-05-tasks.md` §2 row 5, §2.1, §3 | criterion A5, and the recorded §0.4 output-contract conflict |
| `L2-T006` | §11 of this file | `L2-05-tasks.md` §2 row 6, §2.1, §3 | criterion A5 with its literal command, a second STOP rule (`S2`) |

Read a block top to bottom, including everything below its first STOP rule. A carried-over criterion is as binding as an original one.

Set once per shell session, before any task:

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="<absolute path to the control-plane repo working copy>"
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO — STOP"; exit 1; }
```

---

### L2-T001 — Create the lane branch and the owned-path skeleton

**Size:** S  **Depends on:** none

**Creates:**
- `C:/…/control-plane/.github/workflows/.gitkeep`
- `C:/…/control-plane/templates/workflows/.gitkeep`
- `C:/…/control-plane/tools/evidence/.gitkeep`

**Commands**

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/phase0-charter
mkdir -p .github/workflows templates/workflows tools/evidence
touch .github/workflows/.gitkeep templates/workflows/.gitkeep tools/evidence/.gitkeep
git add .github/workflows/.gitkeep templates/workflows/.gitkeep tools/evidence/.gitkeep
git commit -m "L2-T001: create lane 2 owned-path skeleton"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | On the lane branch | `git rev-parse --abbrev-ref HEAD` | exactly `lane/2/phase0-charter` |
| A2 | Three directories exist | `test -d .github/workflows && test -d templates/workflows && test -d tools/evidence; echo $?` | exactly `0` |
| A3 | Nothing outside owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(git rev-parse --abbrev-ref HEAD)" = "lane/2/phase0-charter" \
 && test -d .github/workflows && test -d templates/workflows && test -d tools/evidence \
 && test "$(git diff --name-only integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && echo "L2-T001 OK" || echo "L2-T001 FAIL"
```
Correct output: the single line `L2-T001 OK`.

**STOP rule:** if `git checkout integration` fails because the branch does not exist, STOP — the integration branch is L0's to create. File the blocker with STOP RULE `S1`.

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 1 · **Phase** BT-1 · **Size** S · **Deps** none · **Spec** `PARTITION.md` line 18 (the owned-path column of the lane/OWNS table). **Branch** — that file published the slug `t001-skeleton`; under this section's one-branch model the branch is `lane/2/phase0-charter`, opened here and closed once by `L2-T006`, so no §0.3 close block is run per task for tasks 1–6.

**Carried over from `L2-05-tasks.md` §3 — additional acceptance criteria.** A4–A6 were published only in that file's copy of this task. They hold against the artifact the block above builds and are additive to A1–A3.

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A4 | No namespace-package marker (`L2-05-tasks.md` §0.1) | `test ! -e tools/__init__.py; echo $?` | exactly `0` |
| A5 | Exactly three files across the three owned roots | `find .github/workflows templates/workflows tools/evidence -type f \| wc -l \| tr -d ' '` | exactly `3` |
| A6 | Each marker is a zero-byte `.gitkeep` | `find .github/workflows templates/workflows tools/evidence -type f -name .gitkeep -size 0 \| wc -l \| tr -d ' '` | exactly `3` |

**SELF-VERIFY (A4–A6)**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test ! -e tools/__init__.py \
 && test "$(find .github/workflows templates/workflows tools/evidence -type f | wc -l | tr -d ' ')" = "3" \
 && test "$(find .github/workflows templates/workflows tools/evidence -type f -name .gitkeep -size 0 | wc -l | tr -d ' ')" = "3" \
 && echo "L2-T001 A4-A6 OK" || echo "L2-T001 A4-A6 FAIL"
```
Correct output: the single line `L2-T001 A4-A6 OK`.

**STOP rule (second, carried over):** if any of the three owned roots already exists and holds files authored by another lane, do **not** delete or move them. STOP RULE `S2`; blocker title `BLOCKER L2-T001: owned root already populated by a foreign lane`.

---

### L2-T002 — Pin the consumed contract surface

**Size:** S  **Depends on:** L2-T001

**Creates:** `tools/evidence/CONSUMED-CONTRACTS.lock`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test -d contracts || { echo "contracts/ ABSENT — STOP"; exit 1; }
CONTRACTS_SHA="$(git log -1 --format=%H -- contracts)"
test -n "$CONTRACTS_SHA" || { echo "contracts/ HAS NO COMMIT — STOP"; exit 1; }
{
  echo "# Lane 2 consumed contract surface — do not hand-edit."
  echo "contracts_commit: $CONTRACTS_SHA"
  echo "recorded_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "lane: L2"
} > tools/evidence/CONSUMED-CONTRACTS.lock
git add tools/evidence/CONSUMED-CONTRACTS.lock
git commit -m "L2-T002: pin consumed contracts commit"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Lock file exists | `test -f tools/evidence/CONSUMED-CONTRACTS.lock; echo $?` | exactly `0` |
| A2 | Records a 40-char SHA | `grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/CONSUMED-CONTRACTS.lock` | exactly `1` |
| A3 | SHA matches the live tree | `test "$(grep '^contracts_commit: ' tools/evidence/CONSUMED-CONTRACTS.lock \| cut -d' ' -f2)" = "$(git log -1 --format=%H -- contracts)"; echo $?` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
grep -qE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/CONSUMED-CONTRACTS.lock \
 && test "$(grep '^contracts_commit: ' tools/evidence/CONSUMED-CONTRACTS.lock | cut -d' ' -f2)" = "$(git log -1 --format=%H -- contracts)" \
 && echo "L2-T002 OK" || echo "L2-T002 FAIL"
```
Correct output: the single line `L2-T002 OK`.

**STOP rule:** if `contracts/` is absent or has no commit, STOP. `contracts/**` is L0's and is FROZEN in Phase 0 (PARTITION.md rule 2); Lane 2 must never create it. File the blocker with STOP RULE `S1`.

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 2 · **Phase** BT-1 · **Size** S · **Deps** `L2-T001` · **Spec** `PARTITION.md` rules 2 and 4; §4.1 of this charter. **Branch** — superseded slug `t002-contract-pin`; the branch is `lane/2/phase0-charter`.

**Carried over from `L2-05-tasks.md` §3 — additional acceptance criteria.** A4–A5 were published only in that file's copy of this task.

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A4 | The recorded SHA resolves in this repository | `git cat-file -e "$(sed -n 's/^contracts_commit: //p' tools/evidence/CONSUMED-CONTRACTS.lock)"; echo $?` | exactly `0` |
| A5 | Nothing under `contracts/` was modified | `git status --porcelain contracts \| wc -l \| tr -d ' '` | exactly `0` |

**SELF-VERIFY (A4–A5)**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git cat-file -e "$(sed -n 's/^contracts_commit: //p' tools/evidence/CONSUMED-CONTRACTS.lock)" \
 && test "$(git status --porcelain contracts | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T002 A4-A5 OK" || echo "L2-T002 A4-A5 FAIL"
```
Correct output: the single line `L2-T002 A4-A5 OK`.

**Recorded difference — the lock-file format.** `L2-05-tasks.md`'s copy of this task wrote a different lock: a `schema: consumed-contracts/v1` line, the `contracts_commit:` line, and a `paths:` block whose one entry is `contracts/`; it read the SHA with `git rev-list -1 origin/integration -- contracts`. The block above writes `contracts_commit:`, `recorded_at_utc:` and `lane: L2`, and reads the SHA from the checked-out tree with `git log -1 --format=%H -- contracts`. **The block above is authoritative — build exactly that.** Both forms satisfy the acceptance command `grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/CONSUMED-CONTRACTS.lock` → `1` that `L2-05-tasks.md` §2 row 2 uses, so that index row stays correct against this artifact. Do not add a `schema:` or `paths:` key. If a consumer turns out to require one, that is not your call: STOP RULE `S4`, blocker title `BLOCKER L2-T002: a consumer requires keys CONSUMED-CONTRACTS.lock does not carry`.

The superseded form is reproduced here so that no wording is lost. **It is a quotation, not an instruction — do not run it.**

```
# SUPERSEDED — the L2-05-tasks.md form of this artifact. Do not build this.
CONTRACTS_SHA="$(git rev-list -1 origin/integration -- contracts)"
test -n "$CONTRACTS_SHA" || { echo "NO CONTRACTS COMMIT - STOP (rule S1)"; exit 1; }
printf '%s\n' \
  '# Lane 2 consumed contract surface. Read-only. Lane 2 never writes contracts/**.' \
  '# PARTITION.md rules 2 and 4. Regenerated only by a task that says so.' \
  'schema: consumed-contracts/v1' \
  "contracts_commit: ${CONTRACTS_SHA}" \
  'paths:' \
  '  - contracts/' \
  > tools/evidence/CONSUMED-CONTRACTS.lock
```


**STOP rule (second, carried over):** if `contracts/` is absent from `origin/integration`, L0 has not finished Phase 0. STOP RULE `S1`; blocker title `BLOCKER L2-T002: contracts/ absent on integration, Phase 0 not complete`. Do not invent a SHA and do not create `contracts/`.

---

### L2-T003 — Publish the required-status-check name registry

**Size:** S  **Depends on:** L2-T001

**Creates:** `templates/workflows/required-checks.yaml`

**§4.6 correction:** `templates/workflows/required-checks.yaml` is GENERATED FROM `contracts/workflows/required-checks.v1.yaml`. It is not the source of truth. A control in a path its own lane can rewrite is not a control (§53.1). `contracts/workflows/required-checks.v1.yaml` is the frozen contract (L0-owned); `templates/workflows/required-checks.yaml` is the generated output.

Write this file with exactly this content — no additions, no reordering:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/required-checks.yaml <<'EOF'
# Authoritative required-status-check context names emitted by Lane 2.
# Spec: MultiProduct_MasterSpec_v4.0.md Section 33.2 (lines 2854-2869).
# RULE (Section 33.2): every context below is emitted by a job carrying
# NO `if:` and NO path filter. "No work was needed" is an explicit recorded
# success, never a skip. A `skipped` or `neutral` conclusion on any context
# below, on a merged pull request, is Blocking drift (Section 53).
# CONSUMERS: Lane 5 (branch protection), Lane 3 (reconciliation template
# comparison, Section 53.1). Consumers copy from this file and never invent a name.
# Contexts are added phase by phase per Section 98.2 (lines 9006-9090):
# CI checks at Phase 4, the verification contract at Phase 5, pipeline checks at Phase 6.
schema: required-checks/v1
contexts:
  phase_4:
    - unit-tests
    - integration-tests
    - build
    - security-scan
    - licence-scan
    - slopsquat-check
    - contract-validation
    - registry-validation
    - parity-check
  phase_5:
    - verification-contract
    - seeded-defect-case
  phase_6:
    - artifact-digest-recorded
    - sbom-emitted
  always:
    - renovate-path-guard
    - lane-guard
EOF
git add templates/workflows/required-checks.yaml
git commit -m "L2-T003: publish required-status-check name registry"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f templates/workflows/required-checks.yaml; echo $?` | exactly `0` |
| A2 | Declares the schema line | `grep -c '^schema: required-checks/v1$' templates/workflows/required-checks.yaml` | exactly `1` |
| A3 | Exactly 15 context entries | `grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml` | exactly `15` |
| A4 | No duplicate context names | `grep -E '^    - ' templates/workflows/required-checks.yaml \| sort \| uniq -d \| wc -l` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml)" = "15" \
 && test "$(grep -E '^    - ' templates/workflows/required-checks.yaml | sort | uniq -d | wc -l | tr -d ' ')" = "0" \
 && grep -q '^schema: required-checks/v1$' templates/workflows/required-checks.yaml \
 && echo "L2-T003 OK" || echo "L2-T003 FAIL"
```
Correct output: the single line `L2-T003 OK`.

**Note (§4.6):** After the separate CCR commit that adds `digest-invariant-selftest` under a new `control_plane:` group, this count becomes 16 again.

**STOP rule:** do not add, rename or remove a context name. If a later task needs a context that is not listed, STOP and file it under STOP RULE `S4` — the list is a published cross-lane interface (§53.1, L4653–4689).

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 3 · **Phase** BT-1 · **Size** S · **Deps** `L2-T001` · **Spec** §33.2 L2854–2869; §53.1 L4653–4689; §98.2 L9006–9090 (contexts are added phase by phase). **Branch** — superseded slug `t003-required-checks`; the branch is `lane/2/phase0-charter`. `L2-05-tasks.md` instructed its executor to *“transcribe the block below verbatim from `L2-00-charter.md` §11 `L2-T003`”* — that instruction now resolves to the heredoc above, which is the original.



**A3 CORRECTION — read this before you run the SELF-VERIFY above.** The heredoc in this task writes **fifteen** context names: nine under `phase_4`, two under `phase_5`, two under `phase_6`, two under `always`. Criterion A3 and the SELF-VERIFY above both demand `15`, so a byte-correct transcription prints `L2-T003 OK`. That is `L2-99-review.md` defect **B5** — *"Charter `L2-T003` SELF-VERIFY can never print OK"*. **The transcription is right; the arithmetic is wrong.** Do not add a sixteenth name to make the count match, and do not delete a name to make the prose match — the STOP rule above forbids both, and the registry is a published cross-lane interface (§53.1, L4659).

A3 is left standing verbatim above because `L2-05-tasks.md` §0.5 and its index entry for this id both name *"`L2-00-charter.md` §11 criterion A3"* as one of the two places L0 must reconcile. Until L0 answers, **A3-C and the corrected SELF-VERIFY below govern.**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A3-C | Exactly 15 context entries — supersedes A3 | `grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml` | exactly `15` |
| A5-C | Each of the four group keys appears exactly once | `grep -cE '^  (phase_4|phase_5|phase_6|always):$' templates/workflows/required-checks.yaml` | exactly `4` |
| A6-C | `schema: required-checks/v1` appears exactly once | `grep -c '^schema: required-checks/v1$' templates/workflows/required-checks.yaml` | exactly `1` |

**SELF-VERIFY (corrected — run this one, not the one above)**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
echo "CONTEXT_COUNT=$(grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml)"
test "$(grep -E '^    - ' templates/workflows/required-checks.yaml | sort | uniq -d | wc -l | tr -d ' ')" = "0" \
 && grep -q '^schema: required-checks/v1$' templates/workflows/required-checks.yaml \
 && echo "L2-T003 OK" || echo "L2-T003 FAIL"
```

**CORRECT OUTPUT** — both lines, in this order:

```
CONTEXT_COUNT=15
L2-T003 OK
```

**STOP rule (second, carried over) — file this, then continue.** Finish the task, then file the blocker under STOP RULE `S4`, title `BLOCKER L2-T003: required-checks.yaml carries 15 contexts, Section 0.5 and the charter say 15`, naming `L2-05-tasks.md` §0.5 and `L2-00-charter.md` §11 criterion A3 as the two places L0 must reconcile. Every later Lane 2 task counts contexts from the **file**, never from the prose, so the lane is not blocked while L0 answers.

---

### L2-T004 — Author the lane-guard workflow

**Size:** M  **Depends on:** L2-T001

**Creates:** `.github/workflows/lane-guard.yml`

The ownership table below is transcribed verbatim from `PARTITION.md` lines 15–22. Do not alter a single path.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/lane-guard.yml <<'EOF'
name: lane-guard
on:
  pull_request:
    branches: [integration]
permissions:
  contents: read
jobs:
  lane-guard:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Enforce lane path ownership
        shell: bash
        run: |
          set -euo pipefail
          BRANCH="${GITHUB_HEAD_REF}"
          BASE="origin/${GITHUB_BASE_REF}"
          git fetch --no-tags origin "${GITHUB_BASE_REF}"
          FILES="$(git diff --name-only "${BASE}...HEAD")"
          case "${BRANCH}" in
            lane/1/*) ALLOW='^(schemas/registry/|schemas/product/|registries/|validators/registry/)' ;;
            lane/2/*) ALLOW='^(\.github/workflows/|templates/workflows/|tools/evidence/)' ;;
            lane/3/*) ALLOW='^(reconciler/|tools/provision/|validators/drift/)' ;;
            lane/4/*) ALLOW='^(schemas/records/|metrics/|tools/records/)' ;;
            lane/5/*) ALLOW='^(access/|infra/|ops-vm/|notify/|assets/)' ;;
            *) echo "LANE_GUARD_FAIL: branch ${BRANCH} carries no lane prefix"; exit 1 ;;
          esac
          VIOLATIONS="$(printf '%s\n' "${FILES}" | grep -v '^$' | grep -vE "${ALLOW}" || true)"
          if [ -n "${VIOLATIONS}" ]; then
            echo "LANE_GUARD_FAIL: foreign paths touched by ${BRANCH}"
            printf '%s\n' "${VIOLATIONS}"
            exit 1
          fi
          echo "LANE_GUARD_PASS"
EOF
git add .github/workflows/lane-guard.yml
git commit -m "L2-T004: lane-guard path-ownership check"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f .github/workflows/lane-guard.yml; echo $?` | exactly `0` |
| A2 | All five lane prefixes present | `grep -cE '^            lane/[1-5]/\*\)' .github/workflows/lane-guard.yml` | exactly `5` |
| A3 | Action pinned to a full 40-char SHA | `grep -cE 'uses: actions/checkout@[0-9a-f]{40} ' .github/workflows/lane-guard.yml` | exactly `1` |
| A4 | No tag-pinned or branch-pinned action | `grep -cE 'uses: .*@(v[0-9]|main|master)$' .github/workflows/lane-guard.yml` | exactly `0` |
| A5 | Job carries no `if:` and no path filter | `grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/lane-guard.yml` | exactly `0` |
| A6 | Emits an unambiguous verdict string | `grep -c 'LANE_GUARD_PASS' .github/workflows/lane-guard.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -cE '^            lane/[1-5]/\*\)' .github/workflows/lane-guard.yml)" = "5" \
 && test "$(grep -cE 'uses: actions/checkout@[0-9a-f]{40} ' .github/workflows/lane-guard.yml)" = "1" \
 && test "$(grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/lane-guard.yml)" = "0" \
 && echo "L2-T004 OK" || echo "L2-T004 FAIL"
```
Correct output: the single line `L2-T004 OK`.

**STOP rule:** if the `actions/checkout` commit SHA above does not resolve in the target organisation's allowed-actions configuration, STOP — §48.1 (L4300–4308) forbids substituting a tag. File the blocker with STOP RULE `S4`. Do **not** author `CODEOWNERS`; it is L0's (PARTITION.md line 22).

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 4 · **Phase** BT-1 · **Size** M · **Deps** `L2-T001` · **Spec** `PARTITION.md` rule 1 and the lane/OWNS table (lines 16–21); §33.2 L2854–2869 — no `if:`, no path filter, full-SHA pinning, least-privilege token. **Branch** — superseded slug `t004-lane-guard`; the branch is `lane/2/phase0-charter`.

**Carried over from `L2-05-tasks.md` §3 — additional acceptance criteria.** A7 was published only in that file's copy of this task; A8 and A9 make two of its prose criteria — *“the job name is exactly `lane-guard`”* and *“the unknown-prefix arm exits non-zero”* — mechanically checkable against the heredoc above.

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A7 | `permissions:` grants no `write` on any scope | `grep -cE '^[[:space:]]+[a-z-]+: write$' .github/workflows/lane-guard.yml` | exactly `0` |
| A8 | The job is named exactly `lane-guard`, matching the `always:` group of `required-checks.yaml` | `grep -cE '^  lane-guard:$' .github/workflows/lane-guard.yml` | exactly `1` |
| A9 | The unknown-prefix arm exists and exits non-zero | `grep -c 'LANE_GUARD_FAIL: branch ${BRANCH} carries no lane prefix' .github/workflows/lane-guard.yml` | exactly `1` |

**SELF-VERIFY (A7–A9)**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -cE '^[[:space:]]+[a-z-]+: write$' .github/workflows/lane-guard.yml)" = "0" \
 && test "$(grep -cE '^  lane-guard:$' .github/workflows/lane-guard.yml)" = "1" \
 && test "$(grep -c 'LANE_GUARD_FAIL: branch ${BRANCH} carries no lane prefix' .github/workflows/lane-guard.yml)" = "1" \
 && echo "L2-T004 A7-A9 OK" || echo "L2-T004 A7-A9 FAIL"
```
Correct output: the single line `L2-T004 A7-A9 OK`.

**Recorded difference — how the action is pinned.** `L2-05-tasks.md`'s copy of this task referenced `actions/checkout` by the ledger placeholder `PIN:actions/checkout`, to be substituted later by that file's `L2-T531`/`L2-T532` and `tools/evidence/apply_pins.sh`. **The heredoc above is authoritative:** it carries the literal `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`, and a sibling document already depends on that literal — `L2-02-digest-invariant.md` calls it *"the only SHA verified for this estate"*, *"established in `L2-T004`"*, and its workflow-authoring tasks reuse *"the SHA already verified in `L2-T004`"*. A literal full commit SHA is exactly what §48.1 (L4305) and §101 invariant 85 (L9576) require, so it satisfies A3 and A4 and the later `lint_workflow` pinning rule with no substitution step. Consequence for a later task, stated so nobody has to work it out: `L2-05-tasks.md`'s `L2-T532` records the pair `actions/checkout v4.2.2 11bd71901bbe5b1630ceea73d27597364c9af683` in `tools/evidence/action-pins.txt`; it does not rewrite this workflow. **Do not put a `PIN:` placeholder into `.github/workflows/lane-guard.yml`.**

**Recorded difference — the shape of the case arms.** `L2-05-tasks.md`'s copy wrote the five arms as `OWNED='<space-separated prefixes>'` with an unknown-prefix arm echoing `UNKNOWN LANE PREFIX - FAIL CLOSED`. The heredoc above writes them as `ALLOW='^(<alternation>)'` with an unknown-prefix arm echoing `LANE_GUARD_FAIL: branch ${BRANCH} carries no lane prefix`. **The heredoc above is authoritative.** Both forms fail closed on an unrecognised prefix, and both satisfy A2's `grep -cE '^            lane/[1-5]/\*\)' .github/workflows/lane-guard.yml` → `5`, which is also the acceptance command of `L2-05-tasks.md` §2 row 4, so that index row stays correct against this artifact. Do not grep this file for the string `UNKNOWN LANE PREFIX - FAIL CLOSED`; it does not contain it, and the fail-closed behaviour is proved by A6 and by the `exit 1` on the `*)` arm.

The superseded arms are reproduced here so that no wording is lost. **They are a quotation, not an instruction — do not build them.**

```
# SUPERSEDED — the L2-05-tasks.md form of the case arms. Do not build this.
            lane/1/*)  OWNED='schemas/registry/ schemas/product/ registries/ validators/registry/' ;;
            lane/2/*)  OWNED='.github/workflows/ templates/workflows/ tools/evidence/' ;;
            lane/3/*)  OWNED='reconciler/ tools/provision/ validators/drift/' ;;
            lane/4/*)  OWNED='schemas/records/ metrics/ tools/records/' ;;
            lane/5/*)  OWNED='access/ infra/ ops-vm/ notify/ assets/' ;;
            *)         echo "UNKNOWN LANE PREFIX - FAIL CLOSED"; exit 1 ;;
```


**STOP rule (second, carried over):** if implementing the guard appears to need a lane's owned paths from anywhere other than the `PARTITION.md` lane/OWNS table, STOP — that table is frozen and is the only source. STOP RULE `S4`; blocker title `BLOCKER L2-T004: lane-guard needs an owned-path source outside PARTITION.md`.

---

### L2-T005 — Author the merge-train preflight check

**Size:** S  **Depends on:** L2-T002, L2-T003

**Creates:** `tools/evidence/preflight.sh`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/preflight.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 merge-train preflight.
# Merge order (PARTITION.md line 35): L1 -> L4 -> L2 -> L3 -> L5.
# Lane 2 may open its PR only after L1 and L4 outputs are present on integration.
set -euo pipefail
FAIL=0
need_dir() {
  if [ -d "$1" ]; then echo "OK   $1"; else echo "MISS $1"; FAIL=1; fi
}
need_file() {
  if [ -f "$1" ]; then echo "OK   $1"; else echo "MISS $1"; FAIL=1; fi
}
echo "-- L0 contract surface --"
need_dir  "contracts"
need_file "tools/evidence/CONSUMED-CONTRACTS.lock"
echo "-- L1 outputs (merge before L2) --"
need_dir  "schemas/product"
need_dir  "schemas/registry"
need_dir  "validators/registry"
echo "-- L4 outputs (merge before L2) --"
need_dir  "schemas/records"
echo "-- L2 published interfaces --"
need_file "templates/workflows/required-checks.yaml"
need_file ".github/workflows/lane-guard.yml"
if [ "$FAIL" -eq 0 ]; then echo "PREFLIGHT_PASS"; exit 0; fi
echo "PREFLIGHT_FAIL"; exit 1
EOF
chmod +x tools/evidence/preflight.sh
git add tools/evidence/preflight.sh
git commit -m "L2-T005: merge-train preflight check"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists and is executable | `test -x tools/evidence/preflight.sh; echo $?` | exactly `0` |
| A2 | Script parses | `bash -n tools/evidence/preflight.sh; echo $?` | exactly `0` |
| A3 | Checks both L1 and L4 trees | `grep -c 'schemas/registry\|schemas/records' tools/evidence/preflight.sh` | exactly `2` |
| A4 | Emits one of exactly two verdicts | `grep -cE 'PREFLIGHT_(PASS|FAIL)' tools/evidence/preflight.sh` | exactly `2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/preflight.sh \
 && test -x tools/evidence/preflight.sh \
 && test "$(grep -cE 'PREFLIGHT_(PASS|FAIL)' tools/evidence/preflight.sh)" = "2" \
 && echo "L2-T005 OK" || echo "L2-T005 FAIL"
```
Correct output: the single line `L2-T005 OK`.

**STOP rule:** running `tools/evidence/preflight.sh` and getting `PREFLIGHT_FAIL` is **not** a reason to create the missing directory. Those trees belong to L1 and L4. STOP and wait for the merge train, or file a blocker with STOP RULE `S2`.

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 5 · **Phase** BT-1 · **Size** S · **Deps** `L2-T002`, `L2-T003` · **Spec** `PARTITION.md` line 35, the merge train `L1 → L4 → L2 → L3 → L5`. **Branch** — superseded slug `t005-preflight`; the branch is `lane/2/phase0-charter`.

**Carried over from `L2-05-tasks.md` §3 — additional acceptance criterion.** A5 was published only in that file's copy of this task. Run it on a clean working tree.

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A5 | The script writes nothing | `bash tools/evidence/preflight.sh >/dev/null 2>&1; git status --porcelain \| wc -l \| tr -d ' '` | exactly `0` |

**SELF-VERIFY (A5)**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test -z "$(git status --porcelain)" || { echo "TREE NOT CLEAN - RUN A5 LATER"; exit 1; }
bash tools/evidence/preflight.sh >/dev/null 2>&1 || true
test "$(git status --porcelain | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T005 A5 OK" || echo "L2-T005 A5 FAIL"
```
Correct output: the single line `L2-T005 A5 OK`.

**RECORDED CONFLICT — the output contract. Build the script above verbatim; do not "fix" it here.**

`L2-05-tasks.md` §0.4, *Deterministic output contract — binding on every `tools/evidence/**` program*, requires every program under `tools/evidence/` to accept `--summary` and print exactly one line `<STATUS> <tool-id> checked=<int> failed=<int>`, exiting `0` for `OK`, `2` for `FAIL` and `3` for `ERROR`; that file's copy of this task specified the line `OK preflight checked=4 failed=0` over four conditions. Its acceptance criteria read, verbatim: *“`--summary` prints exactly one line matching `^(OK|FAIL|ERROR) preflight checked=[0-9]+ failed=[0-9]+$`”*; *“with all four conditions true the line is `OK preflight checked=4 failed=0` and the exit code is `0`”*; and *“running the script leaves `git status --porcelain` unchanged”*, which is A5 above and is the one of the three that also holds against the script the block above builds. The four conditions it named were: `schemas/registry/` exists (L1), `schemas/records/` exists (L4), `contracts/` exists (L0), and the `contracts_commit` in `CONSUMED-CONTRACTS.lock` is an ancestor of `origin/integration`. The eight the script above checks are a superset of the first three. The script above accepts no flag, checks **eight** conditions, prints `PREFLIGHT_PASS` or `PREFLIGHT_FAIL`, and exits `0` or `1`. The two specifications cannot both be built.

**The script above is authoritative**, because two acceptance criteria outside this task already consume its exact strings: `L2-T006` A1 in this section (`bash tools/evidence/preflight.sh | tail -1` → exactly `PREFLIGHT_PASS`) and the identical command and expected output in `L2-02-digest-invariant.md` criterion A5. Changing the verdict strings or the exit codes turns both red.

Reconciling `preflight.sh` with §0.4 therefore changes a contract two documents already consume, which is L0's call and not an executor's. **Do not add a `--summary` flag, do not renumber the exit codes, and do not reduce the eight checks to four.** File the blocker under STOP RULE `S4`, title `BLOCKER L2-T005: preflight.sh verdict strings and exit codes do not satisfy L2-05-tasks.md §0.4`, naming this block, `L2-05-tasks.md` §0.4, and the two consumers above. Then keep working: nothing downstream is blocked while L0 answers, because every consumer in the estate reads `PREFLIGHT_PASS`.

**STOP rule (third, carried over):** if `schemas/registry/` or `schemas/records/` is absent, the merge train has not reached Lane 2 this cycle. That is not a bug — the script correctly prints `PREFLIGHT_FAIL`. Wait for the cycle, and file a blocker only if the absence persists across two announced cycles, title `BLOCKER L2-T005: merge train has not delivered L1/L4 outputs for two cycles`.

---

### L2-T006 — Rebase and open the lane PR

**Size:** S  **Depends on:** L2-T001, L2-T002, L2-T003, L2-T004, L2-T005

**Creates/edits:** no files. Publishes the branch only.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git rebase origin/integration
bash tools/evidence/preflight.sh
git push -u origin lane/2/phase0-charter
gh pr create \
  --base integration \
  --head lane/2/phase0-charter \
  --title "L2 phase0: lane charter skeleton, required-checks registry, lane-guard, preflight" \
  --body "Lane 2 (Pipeline & Evidence). Tasks L2-T001..L2-T005.
Owned paths only: .github/workflows/**, templates/workflows/**, tools/evidence/**.
Merge-train position 3 of 5 (L1 -> L4 -> L2 -> L3 -> L5)."
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Preflight passes | `bash tools/evidence/preflight.sh \| tail -1` | exactly `PREFLIGHT_PASS` |
| A2 | Branch is a fast-forward of integration | `git merge-base --is-ancestor origin/integration HEAD; echo $?` | exactly `0` |
| A3 | Diff touches owned paths only | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |
| A4 | PR is open against `integration` | `gh pr view --json baseRefName --jq .baseRefName` | exactly `integration` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(bash tools/evidence/preflight.sh | tail -1)" = "PREFLIGHT_PASS" \
 && git merge-base --is-ancestor origin/integration HEAD \
 && test "$(git diff --name-only origin/integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && test "$(gh pr view --json baseRefName --jq .baseRefName)" = "integration" \
 && echo "L2-T006 OK" || echo "L2-T006 FAIL"
```
Correct output: the single line `L2-T006 OK`.

**STOP rule:** if `git rebase origin/integration` reports a conflict in any file outside the three owned trees, abort with `git rebase --abort` and STOP. Do not resolve it — a foreign-path conflict means another lane wrote into L2's territory or L2 wrote into theirs. File the blocker with STOP RULE `S3`.

**Task header fields carried over from `L2-05-tasks.md` §3.** **#** 6 · **Phase** BT-1 · **Size** S · **Deps** `L2-T001`, `L2-T002`, `L2-T003`, `L2-T004`, `L2-T005` · **Spec** `PARTITION.md` branch and merge model, lines 32–36. **Creates** no files — it publishes the branch and opens the pull request. **Branch** — superseded slug `t006-phase0-pr`; the branch is `lane/2/phase0-charter`, and this is the task that runs the §0.3 close block for tasks 1–6.

**Carried over from `L2-05-tasks.md` §3 — additional acceptance criterion and its literal command.** That file's copy opened one branch per task and so checked its five predecessors on `integration` with this loop:

**Commands**

```bash
set -euo pipefail
for T in L2-T001 L2-T002 L2-T003 L2-T004 L2-T005; do
  git log origin/integration --oneline | grep -q "$T" || { echo "UNMERGED $T - STOP"; exit 1; }
done
```

**That loop cannot pass under this charter and must not be run as written.** These six tasks share one branch, `lane/2/phase0-charter`; `L2-T001`–`L2-T005` are commits on it and reach `integration` only when the pull request this task opens is merged. The faithful equivalent, which checks the same five ids against the branch this task is about to publish, is:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
for T in L2-T001 L2-T002 L2-T003 L2-T004 L2-T005; do
  git log origin/integration..HEAD --oneline | grep -q "$T" || { echo "MISSING $T - STOP"; exit 1; }
done
echo "DEPS_PRESENT"
```

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A5 | All five predecessor commits are on this branch and not yet on `integration` | the second block above | exactly `DEPS_PRESENT` |

Run A5 **before** the `git push` in the block above. If it prints `MISSING <id> - STOP`, that task was not committed on this branch: go back and finish it. Do not open the pull request with a predecessor missing.

**STOP rule (second, carried over):** if `lane-guard` is red on Lane 2's own pull request, Lane 2 has written outside its own trees. Do not force-merge and do not edit the guard to make it pass. STOP RULE `S2`; blocker title `BLOCKER L2-T006: lane-guard red on the Lane 2 phase-0 PR`.

---

## 12. TASK-ID RESERVATION

To keep sibling Lane 2 documents from colliding on ids:

| Range | Reserved for |
|---|---|
| `L2-T001`–`L2-T099` | Charter and lane bootstrap (this document) |
| `L2-T100`–`L2-T299` | Subsystem E — reusable workflow library (`.github/workflows/**`) |
| `L2-T300`–`L2-T499` | Subsystem E — per-product templates (`templates/workflows/**`) |
| `L2-T500`–`L2-T699` | Subsystem F — evidence chain (`tools/evidence/**`) |
| `L2-T700`–`L2-T799` | Acceptance-test execution: AT-024, AT-029, AT-035, AT-103 |

---

## 13. INVARIANTS THIS LANE IS ACCOUNTABLE FOR

Cited by number from §101 (L9443–9600). Each must be `mechanical` in classification and must name an L2 check or an AT- identifier.

| Invariant | Text (abridged) | L2 enforcement point |
|---|---|---|
| 18 (L9477) | Background machine layer cannot merge, approve, deploy or reach production credentials — enforced by the actor gate on every privileged workflow | E-5 |
| 22 (L9484) | The production artifact is the same digest verified in staging. Never rebuilt | E-3, DoD-03 |
| 23 (L9485) | Never rebuild an artifact to work around registry unavailability | E-3, §46.2 |
| 27 (L9489) | Rollback is preferred to hotfix and requires no prior approval during a SEV-1 | rollback workflow (blocked on D-L2-05) |
| 28 (L9490) | Non-reversible changes require an explicit recovery strategy and never claim rollback capability | E-6 plan-class checks, §28.1 |
| 71 (L9548) | Platform changes are versioned, impact-analysed, canaried, verified and reversible | §61, DoD-17 |
| 72 (L9549) | Portfolio-wide changes never roll out to the fleet without passing a canary first | pinned-tag consumption, §33.3 |
| 85 (L9565) | GSD pinned to a tagged release; third-party Actions pinned to full commit SHAs; reusable workflows consumed by pinned tag | E-6, L2-T004 A3/A4 |
| 87 (L9567) | Every architecture and security policy is enforced by the platform wherever the platform can enforce it | the whole lane |

---

## 14. SIGNALS RAISED FROM LANE 2 ARTIFACTS

From the unified signal table, §52.2 (L4520–4587). Lane 2 produces the source data; Lane 4 computes and Lane 5 presents.

| Signal | Definition source | L2 artifact that feeds it |
|---|---|---|
| SIG-12 Stale platform versions | Control plane | Pinned GSD / reusable-workflow / action SHAs recorded by CI |
| SIG-14 Failed canary deployments | Change manifests | Canary exercise legs (§61.3) |
| SIG-17 Restore-test currency | Control plane | `records/restore-tests/` written by the restore-test workflow |
| SIG-18 Verification-contract coverage gaps | Verification contracts | The seeded-defect execution job (E-11) |
| SIG-34 Organisation export staleness | Export job telemetry | `org-export` workflow (E-10) |
| SIG-42 AI-eval regression | `records/eval/` | Pin-change CI leg |

---

## 15. READING ORDER FOR THE EXECUTOR

1. `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — in full, first, always.
2. This charter, sections 2, 6, 9, 10 — path ownership, merge train, decisions, STOP rules.
3. Spec §33 (lines 2829–2912) — the single densest section this lane implements.
4. Spec §32 (lines 2803–2828) — the eleven questions, which are the lane's reason to exist.
5. Spec §37.3 (lines 3261–3268) and §27.2 (lines 2567–2576) — the two gates that must fail closed.

Nothing in this lane requires interpretation. Where a value is not stated in the spec or in `contracts/**`, it is a DECISION REQUIRED for L0 — never a judgment call for the executor.
