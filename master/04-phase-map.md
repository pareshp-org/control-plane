# 04 — THE PHASE MAP

**Scope of this file.** One timeline for the whole build. Every phase, every lane, one grid. What genuinely runs in parallel, what only looks like it does, where the merge train must be clean before anything else moves, and which items no amount of parallelism compresses.

**Authority.** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` is frozen and is never contradicted here. Spec authority: `MultiProduct_MasterSpec_v4.0.md` §98 (as amended by D99, D100, D101), §99.2 dependency spine, §99.4 minimal honest V1, §96.5/§96.6 onboarding pacing, §95 bootstrap, §100 acceptance tests, §101 invariants.

**Reader.** L0 (human/lead integrator) sequences from this file. The five lane developers read it only to know which phase they are in, what gates them, and when to stop and wait. Lane developers never merge, never rebase another lane, never move a sync point.

---

## 1. The two clocks — read this before reading the grid (D99)

D99 is binding and it changes how §98.2 must be read:

> *"§98.2 stamped absolute weeks on phases whose deliverables §99.2 prices three to ten times higher... The phases split into a Build track dated by subsystem with its complexity band, and an Onboarding track whose per-product phases are relative to the subsystems they consume. Pre-onboarding deadlines are set from the Onboarding track, not from the labels."* (D99, §98.1/§98.2/§99.2)

So:

| Track | What it is | How it is dated | Who runs it |
|---|---|---|---|
| **Build track** — `BT-0` … `BT-4` | Building the subsystems of §99.2 | By subsystem complexity band (§99.2: S <1wk, M 1–3wks, L 3–8wks, XL multi-month, for **one** competent engineer with AI assistance) | The five lanes in parallel + L0 |
| **Onboarding track** — `OT-P4` … `OT-P7` | Bringing each of the eight live products to the §96.6 target standard | Relative to the Build-track phase that delivers the subsystem it consumes; 3–4 weeks per product (§96.5), sequenced highest `classification.reliability_criticality` first | L0 + product teams + QA. **Not a lane deliverable.** |
| **Floor** — `OT-FLOOR` | The §96.6 universal floor: nine items × every live product | Its own declared duration in the roadmap, never inside Phase 1's week (§96.6) | L0 + named per-product executors (§95.4) |
| **Governance tier** — `G1`…`G8` | Instrumentation over the running Foundation (§98.5) | Calendar-gated on accumulated operating data; **one person, part-time** (§98.7) | Not a lane. Post-Foundation. |
| **People tier** — `P1`…`P8` | Capacity and management intelligence (§98.6) | Gated on G3 attention data and on the Layer B datasource separation | Not a lane. Post-G3. |

`BT-n` and `OT-Pn` are **labels of this plan**, not spec phase numbers. The spec's Phase 1–7 numbering is preserved in the "Spec phase" column of every table below. No spec phase number is invented anywhere in this file.

**Week labels in §98.2 ("Week 1", "Weeks 4–5") are configuration elapsed, not build elapsed.** They describe how long the *configuration action* takes once the subsystem exists. They are not budgets for building the subsystem. Never quote a §98.2 week label as a build deadline.

---

## 2. The master phase grid

Lane columns are the frozen lanes of PARTITION.md. `—` means the lane has no deliverable in that phase and must not open a branch for it. `idle` means the lane is deliberately blocked and must wait.

| Phase | Spec phase | L0 (`main`/`integration`) | L1 · A,B | L2 · E,F | L3 · C,D | L4 · I,N | L5 · K,L,M,Q,R | Ends at |
|---|---|---|---|---|---|---|---|---|
| **BT-0** Contract freeze | none (PARTITION rule 2) | `contracts/**` authored + FROZEN; CODEOWNERS; lane-guard check; `Makefile`; generated stubs + fixtures; pre-Phase-1 baselines recorded (§103.14) | idle | idle | idle | idle | idle | **S0** |
| **BT-1** Foundation & registry core | §98.2 Phase 1; §98.2 Phase 2 portfolio items | Org consolidation; Teams grant Write **then** branch protection (D101); required-check list starts empty; bootstrap exceptions (§95.2); `economics.yaml` OS ledger entry; per-repo transition notes (§95.4) | **A**: `people.yaml`, `roles.yaml`, `platform.yaml` schemas. **B**: minimal `exceptions.yaml` validator — expiry / owner / deactivation trigger (§95.2, Phase 1 deliverable) | **E**: `ci` reusable workflow only — the first required status check must exist before any check can be added to protection | **D**: `create-product` / `add-person` skeleton against frozen contracts + fixtures. **Unverified.** | **N**: board conventions, Ready-to-Execute definition, Ready-queue-miss detector (§97.5). Record + event store layout, event envelope, record schema version (D103) | **M**: ops VM, DevLake + Grafana + Prometheus (§98.2 Phase 2). **R**: notification routing. **K**: `env | grep -i api_key` check (§98.2 Phase 1) | **S1** |
| **BT-2** Validation, provisioning v0, reconciliation v0 | §98.2 Phase 3 | Hermes background-layer benchmark go/park decision (§98.2 Phase 3); `tools.yaml` registration before first use (D69); constitution file | **A/B complete**: `product.yaml` @ `contract_version: 1`; referential integrity; date rules; 24x7-without-rota blocker; commitments-conflict blocker; unclassified-control rejection; `check-commitment` CLI | **E**: `build` workflow + immutable artifact + digest recording; parity job | **D complete**: `create-product`, `add-person` with zero hand-editing. **C v0**: detect-and-block only — Teams vs registries, expiry revocation, protection drift, orphan detection at blocking severity (§99.4 item 6) | **I** feedstock: event-log taxonomy emission; `record-decision` CLI; Scorecard scan wiring | **L**: access model, five secret tiers, fail-closed classification. **Q**: asset inventory + deadline watch. **K**: approved-runtime / approved-extension lists | **S2** |
| **BT-3** Pipeline, evidence chain, metrics | §98.2 Phases 4–6 (platform half only) | Adds each new check context to branch protection at S3; production-approval gate + workflow-identity gate (§27.2) armed or its bootstrap exception recorded | Verification-contract schema; `restore_tested` date rule (invariant 4) | **E complete**: `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue`; digest invariant enforced **in code**; SBOM; delta-gated security/licence scan; Friday-freeze time gate. **F**: eleven-question answerability; `verify-digest-chain` | **C** Levels 1–2 (Detect / Warn); AT-102 seeded canary; AT-110 bounded-credential test executed for real | **I complete**: DevLake nightly ingest; Prometheus scraping `/health`, `/version`, `/metrics`; Scorecard drop detection; attention-ledger schema (§97.4) | Environments with scoped secrets; restore-rotation scheduler (with L2); org-export mechanism per metadata class (D80) | **S3** |
| **BT-4** Views & governance registries | §99.4 item 7 (Founder view v0); §98.5 G1–G2 build surface | Resolved: FD-002 — plan-checker (subsystem G) is owned by L0. Subsystems **H** (dashboards), **O** (governance registries & jobs), **G** (plan-checker), **J** (background layer), **P** (people intelligence) assigned per FD-002. | — | — | — | — | — | **S4** |

### Onboarding track — runs against a *finished* Build track, per product

| Phase | Spec phase | Gated on | Per-product cost | Serialised by |
|---|---|---|---|---|
| `OT-FLOOR` | §96.6 universal floor | Nothing. Starts at BT-0, before any lane work lands | 9 items × 8 products = **72 tracked obligations**, each with a named executor and a date | L0 attention; criticality order (§96.5) |
| `OT-INTAKE` | §96.6 intake gap assessment | `templates/intake-gap-assessment.md` existing | 1 recorded assessment per product, written by a human assessor (D72) | L0 |
| `OT-P4` Environments | §98.2 Phase 4 | **S3** (L2's `build` + parity job; L5's environments + scoped secrets) | Weeks 4–5 *of that product's own onboarding*, not of the calendar | Product team |
| `OT-P5` Verification | §98.2 Phase 5 | `OT-P4` for that product | Weeks 5–7 *of that product's own onboarding* | **QA — the hard serialiser.** QA-takeover SLA: two weeks from AI-drafted suite landing (§96.6) |
| `OT-P6` Delivery pipeline | §98.2 Phase 6 | **S3** (L2's `deploy-*`, `restore-test`; F's evidence chain) | Week 7 *of that product's own onboarding* | Product team + one deliberate rollback + one restore test |
| `OT-P7` GSD activation | §98.2 Phase 7 | `OT-P6` for that product | Week 8 *of that product's own onboarding* | Plan-checker availability — DECISION 1 resolved (FD-002); plan-checker (subsystem G) owned by L0 |

---

## 3. The critical path

### 3.1 The spine, from §99.2

> **Dependency spine:** A (registries) → B (validation) → C (reconciliation) and D (provisioning); E (workflows) → F (evidence chain) → H/I (views and metrics); I is the feedstock for nearly all governance-tier and people-tier computation; P is hard-gated on L's datasource separation. (§99.2)

Plus the per-subsystem `Depends on` column of §99.2: `C` depends on **A, B and D**. `D` depends on A, B. `F` depends on E. `I` depends on A, E. `H` depends on I, F, C. `P` depends on I, L, A.

### 3.2 The longest chain

```
BT-0 (contract freeze, L0 solo)
  → A  (L1, band M)
  → B  (L1, band M)
  → D  (L3, band L)          ← D depends on A and B
  → C  (L3, band L)          ← C depends on A, B and D
  → auto-repair Level 3      ← calendar-gated, §98.3
```

Summed at §99.2's own bands (M = 1–3 weeks, L = 3–8 weeks, single implementer):

| Segment | Band sum | Weeks |
|---|---|---|
| A + B (lane L1) | M + M | 2 – 6 |
| D + C (lane L3) | L + L | 6 – 16 |
| **Critical path total, excluding BT-0** | | **8 – 22 weeks** |

**Five parallel developers do not compress this.** The chain is serial across exactly two lanes, and half of it (D → C) is serial *inside one lane*. Adding lanes adds nothing to a chain; it only overlaps the work that is not on the chain.

### 3.3 Lane load, for comparison

| Lane | Subsystems | Band sum | Weeks (single implementer) | On the critical path? |
|---|---|---|---|---|
| L1 | A (M) + B (M) | M+M | 2 – 6 | **Yes — the head of it** |
| L2 | E (L) + F (M) | L+M | 4 – 11 | No — but F is serial behind E inside the lane |
| L3 | C (L) + D (L) | L+L | 6 – 16 | **Yes — the tail of it, and the longest single lane** |
| L4 | I (L) + N (M) | L+M | 4 – 11 | No — but I is gated on E |
| L5 | K (M) + L (M–L) + M (M) + Q (S–M) + R (S) | — | 6 – 18 | No — integrates last (PARTITION) |

§99.2's own total for the **full** surface is 10–14 engineer-months at single-implementer pace, excluding per-product onboarding content and excluding upper-tier calendar accumulation. The five-lane build addresses the V1 subset of §99.4 (≈30% of the build surface), not that total.

### 3.4 Wall-clock, honestly stated

Wall-clock for the parallel build ≈ **T_L0 (Phase 0 solo, unparallelised — FD-011) + max(critical path, longest off-path lane)** and never less than BT-0 plus the critical path. L0's Phase 0 is not concurrent with any lane work and must be added, not overlapped:

```
BT-0 (L0, unparallelisable)  +  8–22 weeks (A→B→D→C)  +  OT-* per product
```

L5's 6–18 weeks fits inside that window and is why PARTITION merges L5 last. L2's 4–11 weeks fits too, which is why L2 can absorb the evidence-chain work without extending the schedule.

---

## 4. Synchronisation points — the merge train must be clean

A sync point is a hard stop. **No lane opens a branch for the next phase until L0 declares the sync point passed.** The merge train order is frozen by PARTITION: **L1 → L4 → L2 → L3 → L5**, once per cycle.

### 4.1 What "clean" means — executable definition

L0 runs this at every sync point. Every line has one unambiguous expected output.

```bash
set -euo pipefail
# L0 sets these once, at BT-0, and never again
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"  # FD-068: value lives in contracts/project-config.sh
check_org
export CP="$ORG/control-plane"

git fetch origin --prune
git checkout integration
git reset --hard origin/integration

# 1. No lane PR is still open against integration.  Expected output: 0
gh pr list --repo "$CP" --base integration --state open --json number --jq 'length'

# 2. The last CI run on integration succeeded.  Expected output: success
gh run list --repo "$CP" --branch integration --limit 1 --json conclusion --jq '.[0].conclusion'

# 3. integration is a fast-forward of main.  Expected output: FF-OK
git merge-base --is-ancestor origin/main origin/integration && echo FF-OK || echo NOT-FF

# 4. No lane branch is left unmerged.  Expected output: NO UNMERGED LANES
git branch -r --no-merged origin/integration | grep -E 'origin/lane/[1-5]/' && echo "UNMERGED LANE - STOP" || echo "NO UNMERGED LANES"

# 5. Every required status check named in protection was actually reported by the last run.
gh api "repos/$CP/branches/main/protection" --jq '.required_status_checks.contexts[]' | sort > /tmp/required.txt
gh api "repos/$CP/commits/integration/check-runs" --jq '.check_runs[].name' | sort -u > /tmp/reported.txt
comm -23 /tmp/required.txt /tmp/reported.txt      # Expected output: (empty)
```

**Line 5 is not optional.** §98.2 Phase 1: *"A required check no workflow emits blocks every pull request indefinitely; a list that silently stays empty is a gate that reads armed and is not."* At each sync point L0 adds the contexts that phase created, and executes line 5 to prove they report.

### 4.2 Lane-guard self-check — every lane runs this before opening a PR

One command per lane. Any output other than `PATHS OK` is a **STOP**: do not open the PR, open a blocker issue.

```bash
set -euo pipefail
# Run from the lane branch, after rebasing on integration.
git fetch origin
git rebase origin/integration
git diff --name-only origin/integration...HEAD > /tmp/changed.txt
```

| Lane | Verification command (paste verbatim, substituting nothing) |
|---|---|
| L1 | `grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' /tmp/changed.txt && echo "FOREIGN PATH - STOP" || echo "PATHS OK"` |
| L2 | `grep -vE '^(\.github/workflows/|templates/workflows/|tools/evidence/)' /tmp/changed.txt && echo "FOREIGN PATH - STOP" || echo "PATHS OK"` |
| L3 | `grep -vE '^(reconciler/|tools/provision/|validators/drift/)' /tmp/changed.txt && echo "FOREIGN PATH - STOP" || echo "PATHS OK"` |
| L4 (control-plane) | `grep -vE '^(schemas/records/|metrics/|tools/records/)' /tmp/changed.txt && echo "FOREIGN PATH - STOP" || echo "PATHS OK"` |
| L4 (control-plane-records) | whole repository is L4's — no path filter, but `records/**` and `events/**` are **directory-per-item, one file per item**, never a shared mutable index (PARTITION rule 3) |
| L5 | `grep -vE '^(access/|infra/|ops-vm/|notify/|assets/)' /tmp/changed.txt && echo "FOREIGN PATH - STOP" || echo "PATHS OK"` |

### 4.3 The sync points

| Sync | Closes | Cannot pass until | Executed negatively (must fail) |
|---|---|---|---|
| **S0** | BT-0 | `contracts/**` tagged and frozen; CODEOWNERS live; lane-guard check installed; generated stubs and fixtures published | A PR touching a foreign path **fails** the lane-guard check (PARTITION rule 1). Prove it with a throwaway PR |
| **S1** | BT-1 | §98.2 Phase 1 completion check passes in full — quoted in §5 below. Teams granting Write existed **before** branch protection was armed (D101) | No direct human push to any default branch on `control-plane` succeeds; an approval from a Read-only account does **not** satisfy protection; an approval from a machine account does **not** satisfy it; a workflow pushed to a non-default branch declaring `environment: production` obtains no environment secret; a deliberately malformed `exceptions.yaml` entry is rejected (§98.2 Phase 1) |
| **S2** | BT-2 | §98.2 Phase 3 completion check: *"contracts validate; registries, contracts and Team membership agree, machine-verified"* | Reconciliation v0 finds the AT-102 seeded canary. A run reporting zero findings is a **failed** run and raises SIG-13 |
| **S3** | BT-3 | §98.2 Phase 6 completion check on the pilot product(s): a deliberate rollback succeeded in staging; restore test recorded; the eleven-item evidence chain answerable for one real deployment | AT-110 executed for real from the reconciler's own credential — all six attempts fail, and the credential still completes a normal reconciliation run. AT-103 and the production-approval workflow-identity test (deploy fails closed when approver == deploying actor) |
| **S4** | BT-4 | Resolved: FD-002 — plan-checker (subsystem G) is owned by L0. Subsystem assignments complete per FD-002. | — |

### 4.4 Sync-point STOP rules (binding on lane developers)

1. If your lane-guard command prints `FOREIGN PATH - STOP` — do not open the PR. Open a blocker issue naming the file and the owning lane. Never edit a foreign path, not even to fix an obvious bug.
2. If you need a change to `contracts/**` — you file a **Contract Change Request** to L0 (PARTITION rule 2). You never edit `contracts/**`. Stop work on the affected task until L0 answers.
3. If your acceptance criterion cannot be evaluated because another lane's output does not exist yet — that is a **sync-point dependency, not a blocker**. Record it, finish everything else in the task, and stop. Do not stub another lane's output into your own tree (PARTITION rule 4).
4. If the sync point has not been declared passed by L0 — do not start the next phase, even if your lane's work in that phase is obviously independent.

---

## 5. Calendar-gated items — the ones parallelism cannot compress

§98.1, binding:

> *"the critical path of the upper tiers is elapsed operation time, not engineering effort. Pattern detection needs realistically two quarters of incident and exception history; capacity forecasting needs at least two quarters of attention data; framework evolution needs at least two full review periods of evidence. No amount of build acceleration compresses this, and no predictive layer is built before its data exists."* (§98.1)

| Item | Spec | Clock starts when | Minimum elapsed | Proof the clock started |
|---|---|---|---|---|
| **Pre-Phase-1 baselines** | §103.14, AT-046 | Before BT-1 begins | Must be **complete before** BT-1, not during | Every §103 minimum-set measure has a recorded one-time banded self-estimate labelled as an estimate; anything without one is explicitly marked `unbaselined` |
| **Universal floor** (`OT-FLOOR`) | §96.6 | BT-0 | *"several weeks"* — spec gives no number. **DECISION 3** | 72 checklist rows (9 items × 8 products), each with named executor and date; a floor declared done on paper is the exact failure §96.4 exists to catch |
| **Reconciliation auto-repair, Level 3** | §98.3 | S2 (detect-and-block live) | *"waits until detection has run clean for weeks"* — weeks of clean runs, not weeks of work | Consecutive reconciliation runs with zero unresolved findings **and** the AT-102 canary found on every one |
| **Drift classification** | §98.3 | S2 | Needs *"several products"* before drift is a real risk | Number of onboarded products in the registry |
| **Restore-test rotation** | §98.2 Phase 6; invariant 4 | First recorded restore test per product | Every product restore-tested within any rolling **90-day** window | `restore_tested` date in each product contract; an older date fails CI |
| **Organisation export restore test** | §98.3, AT-035, D80 | First export run (scheduled at §98.2 Phase 2) | *"within the first quarter"* | Recorded restore of the export to an independent environment, each data class through its own mechanism |
| **Asset inventory / vendor deadline watch** | §98.3 | BT-2 (Q built) | Needed *"before the first certificate expiry, roughly month 3"* | Earliest expiry date in `assets` inventory |
| **QA takeover per product** | §96.6 | AI-drafted suite lands for that product | **2 weeks** SLA, per product, and QA is one person | Breach is a QA-capacity signal at the weekly review, never a personal one |
| **G4 — failure-pattern learning** | §98.5 G4 | G1 live and emitting | *"realistically two quarters of G1 data"* | G1 health-report history length |
| **G5 — load model & predictive capacity** | §98.5 G5 | G3 attention ledger live | *"at least two quarters of G3 attention data"* | Attention-ledger record count and span |
| **G6 — scenario modelling** | §98.5 G6 | G5 exit | G5 forecast accuracy scored first | Forecast retrospective scoring records |
| **P8 — framework evolution** | §98.6 sequencing rules | P4 evidence bundles generating | *"at least two full review periods of P4 evidence"* | Count of completed review periods |
| **G8 — first quarterly OS review** | §98.5 G8 | Phase 1 (the review runs each quarter on whatever data existed) | One quarter | Generated review pack |
| **Bootstrap exception expiries** | §95.2, SIG-39, AT-039 | Each exception's `start` | Its own `expiry`; unclosed past expiry escalates **Red** | `exceptions.yaml`; every entry has expiry, owner, deactivation trigger or CI rejects it (invariant 77) |

**Distinct category — trigger-gated, never calendar-gated.** §98.4 items activate *on their trigger, never on the calendar*: shared service registry (first genuine shared service), dependency graph views (~10 products or first shared service), split/merge processes (first split or merge), contractor model (first contractor), platform compatibility migration (first contract schema change), data and privacy extension (first regulated-data requirement), transfer process (first transfer), second review cluster (~12 people), domain activation (second Team Lead exists). **Do not put these on the timeline at all.** Putting a trigger-gated item on a date is how it gets built before it is needed.

---

## 6. What is genuinely concurrent, and what only looks it

This section exists because a grid with five columns reads as five-way parallelism, and it is not.

### 6.1 Genuinely concurrent

| Concurrent pair | Why it really is | Cost of the concurrency |
|---|---|---|
| L1 (A, B) ‖ L5 (M, R, Q) | §99.2: M depends on nothing; R depends on nothing; Q depends on A only for owner references, which the frozen contracts supply | None. L5's ops VM and notification routing share no path and no artifact with L1 |
| L1 (A, B) ‖ L4 (N) | §99.2: N depends on nothing. Boards, horizon semantics and Ready-queue-miss detection are independent of every schema | None |
| L2 (E) ‖ L1 (A, B) | §99.2: E depends on A. E consumes A's *shape*, which the frozen `contracts/**` provides at S0 | L2's workflows cannot be validated against real registries until S1 |
| L5 (all) ‖ everything | PARTITION: *"L5 (access/infra) is independent at build time, integrates last."* L5 authors declarations and enforcement configuration in its own paths | L5's **end-to-end** verification is not independent — the access model is applied by L3's provisioning (`D`). This is precisely why L5 merges last in the train |
| OT-P4/P5/P6 across different products | Different repositories, different teams | Bounded by QA — see 6.2 |

### 6.2 Only *appears* concurrent — state this out loud to anyone who asks why the schedule is not shorter

| Apparent parallelism | The truth | Consequence |
|---|---|---|
| **L3 building C and D while L1 builds A and B** | L3 can *write code* against frozen contracts and fixtures. It cannot *verify* anything: §99.2 gives `D → {A, B}` and `C → {A, B, D}`. L3's acceptance criteria are unevaluable until S1 lands real schemas and validators | L3 code is written concurrently; L3 phases **complete** serially, after L1. Do not report L3 as "done" before S1 |
| **L3's two subsystems, C and D** | Serial *inside one lane*: C depends on D (§99.2). One developer, two subsystems, strict order | L3 is the longest lane (6–16 weeks) and carries the tail of the critical path. Splitting it across lanes is not available — PARTITION is frozen |
| **L2's E and F** | Serial inside one lane: F depends on E (§99.2). The evidence chain has nothing to chain until the workflows emit artifacts | L2's 4–11 weeks is a sequence, not two parallel halves |
| **L4's metrics pipeline (I)** | `I` depends on **A and E** (§99.2). Schemas and event envelopes can be authored at BT-1; ingest and scraping cannot be exercised until L2 emits at BT-3 | L4 delivers in two separated pieces, at S1 and S3, not one continuous stream |
| **Dashboards (H)** | `H` depends on **I, F and C** — three different lanes. It is the most dependency-dense subsystem in §99.2, and no lane owns it (DECISION 1) | H cannot start before S3 under any assignment |
| **Eight products onboarding "in parallel"** | §98.2 Phases 5–7 pass through **one QA person**, with a two-week QA-takeover SLA per product (§96.6). §99.6 names QA *"the most acute single-person dependency in the model"* | Onboarding wall-clock ≈ 8 × (QA takeover) staggered against 3–4 weeks per product, **not** 3–4 weeks total. Sequence by `reliability_criticality` (§96.5) so that the products where an ungoverned incident hurts most spend the least time in pre-onboarding mode |
| **The universal floor "alongside Phase 1"** | §96.6 is explicit: the floor *"carries its own duration in the roadmap rather than riding inside Phase 1's week"*, and it is *"nine items across every live product... at eight products seventy-two tracked obligations"* | It runs alongside BT-0/BT-1 on the calendar but consumes L0 and per-product-team attention, not lane attention. It is not free and it is not a week |
| **The G tier "in parallel with Foundation"** | §98.7: G1–G2 is *"one person, part-time... roughly 2–4 weeks of effort spread across a quarter"*; G3–G5 *"1–2 weeks per phase"*. And §98.1's platform investment gate (§59) applies to each G phase individually | The G tier is one contended person, sequential, calendar-gated. It is not a sixth lane and must never be drawn as one |
| **The P tier** | §98.6: P4 *"must not begin before the Layer B datasource separation is implemented and verified"*, where verified means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds. §99.2: *"P is hard-gated on L's datasource separation"* | P4 has a hard mechanical gate, not a soft dependency. No evidence bundle is generated for anyone whose framework mapping still carries an outstanding marker (§98.6) |
| **BT-0** | L0 alone. Five lanes idle by construction (PARTITION rule 2: `contracts/**` is written by L0 in Phase 0 and FROZEN) | This is the single most expensive serialisation in the plan. Shortening BT-0 by rushing the contracts costs far more later — every Contract Change Request stalls a lane |

### 6.3 Two sequencing rules that override the grid

1. **P0-before-P2, binding (§98.1):** *"no P2 or P3 capability may be started while a P0 capability is unbuilt."* The P0 phases are G1 and G2 (§98.5); G3 is P1/P2, G5 and G6 are P2/P3. A phase that fails its own investment gate is recorded as **`declined`** — a recorded decision with gate answers, forgone capabilities and a review date — and `declined` is distinct from `unbuilt`. **A declined P0 releases the lock; an unbuilt P0 holds it** (§98.1).
2. **Exit criteria are scoped to their own deliverables (D100).** No phase's exit may require another phase's output. G3 exits on questions 1–5 of §93.3; question 6 renders as **unarmed — not yet instrumented** under the §52.2 arming discipline (D77) until G5 arrives; questions 7 and 8 render unarmed until G6 arrives; and G3 does not wait on any of them. Apply the same rule to every sync point in this file: if a criterion needs a later phase, it is not a criterion — it is an arming dependency.

---

## 7. Per-phase entry and exit — quoted from the spec, not paraphrased

### BT-0 → S0

Entry: nothing. This is the start.

Exit, all of which L0 executes:

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP_DIR="$HOME/src/control-plane"
export CP="$ORG/control-plane"

# contracts frozen and tagged
git -C "$CP_DIR" tag --list 'contracts/v1.0.0'               # expected: contracts/v1.0.0
LAST_CONTRACTS_COMMIT="$(git -C "$CP_DIR" log --format=%H -1 contracts/)"
git -C "$CP_DIR" merge-base --is-ancestor "$LAST_CONTRACTS_COMMIT" contracts/v1.0.0 && echo "AT-OR-BEFORE-TAG" || echo "AFTER TAG - STOP"
gh api "repos/$CP/rulesets" --jq '.[]|select(.name=="contract-tag")|.bypass_actors|length'  # expected: 0

# CODEOWNERS resolves to human identities only (§98.2 Phase 1 completion check)
gh api "repos/$CP/contents/CODEOWNERS" --jq '.content' | base64 -d | grep -E '\[bot\]|-app$' && echo "MACHINE IDENTITY - STOP" || echo "HUMANS ONLY"

# pre-Phase-1 baselines recorded (§103.14, AT-046)
ls "$CP_DIR/records/baselines/" | wc -l                            # expected: one file per §103 minimum-set measure
```

Plus the negative test: open a throwaway PR from `lane/1/s0-guard-test` touching `.github/workflows/ci.yml` (an L2 path). It **must fail** the lane-guard check. Close it.

### BT-1 → S1

Exit is §98.2's Phase 1 completion check, executed as written — not summarised. Its checkable clauses:

- no direct human push to any default branch succeeds on `control-plane`; the reconciler credential's declared repair scope (§26.4) is the **only** machine write path admitted; the records-writer holds **no** credential on this repository at all (§40.1, D89);
- an approval from a Read-only account does **not** satisfy branch protection; a Write-holding Cross-Reviewer approval does;
- an approval from a machine account does **not** satisfy branch protection — checked **negatively**;
- organisation-enforced 2FA active, hardware keys or passkeys for the Founder, organisation Owners and platform-admin holders;
- no API key present anywhere: `env | grep -i api_key` empty on every machine, shell profiles and repository `.env` files included;
- the minimal `exceptions.yaml` validator rejects a deliberately malformed exception;
- **Teams granting Write exist before branch protection is armed** (D101), so no window opens in which no approval can satisfy the gate;
- a workflow pushed to a non-default branch declaring `environment: production` obtains no environment secret — checked negatively;
- a second organisation Owner or an escrowed break-glass Owner credential exists with a named escrow custodian;
- the organisation export's first run is scheduled in §98.2 Phase 2, or its absence is a dated accepted risk (D80).

D101's arming order inside BT-1 is not negotiable and is the one ordering error that silently breaks the whole week:

```
1. Derive Teams from the interim assignment set   →  Teams grant Write
2. Arm branch protection (required review, most-recent-push approval)
3. Required-status-check list starts EMPTY, per repository
4. Each later phase adds its own contexts and proves they report (§4.1 line 5)
```

Phase 3 later replaces the interim assignment set with the registry-derived one (§98.2 Phase 1, D101). Use the §95.2 bootstrap arming pattern — configured but not yet binding, with the armed configuration recorded beside the unarmed one — rather than inventing a second approach (D101).

### BT-2 → S2

Exit, §98.2 Phase 3 completion check, verbatim: *"contracts validate; registries, contracts and Team membership agree, machine-verified."*

Plus AT-102, which is a run-level property and must be wired at S2, not later: every reconciliation run must find the deliberately seeded canary drift; a run reporting zero findings — canary included — is a **failed** run, raises SIG-13, and triggers the gap procedure.

### BT-3 → S3

Exit, §98.2 Phase 6 completion check: a deliberate rollback succeeded in staging; restore test recorded; the eleven-item evidence chain answerable for one real deployment; and the production-approval test verifies the workflow-identity gate — the approval actor is recorded and the deploy fails closed when the approver equals the deploying actor, **never** environment required reviewers, which on private repositories are Enterprise-only (D73).

Plus AT-110 executed for real *at the phase that builds the reconciler*, per AT-110's own text, and re-executed at every credential rotation.

### BT-4 → S4

Resolved: FD-002 — plan-checker (subsystem G) is owned by L0.

---

## 8. L0 DECISIONS REQUIRED

Five decisions block or bound this map. Each is a genuine gap — an unassigned subsystem, an unowned path, or a spec range rather than a spec value. None may be resolved by a lane developer.

### DECISION 1 — Five subsystems have no owning lane — **Resolved: FD-002**

**The gap.** PARTITION.md assigns subsystems A,B → L1; E,F → L2; C,D → L3; I,N → L4; K,L,M,Q,R → L5. §99.2 defines eighteen lettered subsystems A–R. **G, H, J, O and P are assigned to no lane and their source paths appear in no lane's OWNS column.**

| Subsystem | §99.2 | Band | Depends on | §99.4 V1 status |
|---|---|---|---|---|
| G — Plan-checker and Gate 1 tooling | design-open internals (§99.3 item 3) | L *if built in-house* | — | Needed at §98.2 Phase 7; risk 4 in §99.6 |
| H — Dashboards and views | Grafana provisioned from JSON in git | L | I, F, C | Founder view v0 is §99.4 item 7 |
| J — Background machine layer | conditional on the CPU benchmark | L + hardware | D, E | **Explicitly deferred** (§99.4) |
| O — Governance registries and jobs | exception lifecycle, policies, patterns, tool register | M | A, C | Partly V1: §99.4 item 8 — exception registry with mandatory expiry, safe defaults, fail-closed classification |
| P — People intelligence engine | capacity, bundles, succession | L–XL | I, L, A | **Explicitly deferred** (§99.4 item 9) |

**Why L0 must decide.** PARTITION rule 1 is *"One owner per path. No path appears in two lanes."* Assigning H to a lane creates a new owned path root; doing it inside a lane, or letting two lanes both touch `dashboards/`, breaks the frozen contract and reintroduces merge conflict.

**Options.**
- **(a) Leave G, H, J, O, P entirely to L0**, post-Foundation, sequential. Consistent with §98.7 (*"one person, part-time"* for the G tier) and with §99.4 deferring J and P outright. Cost: BT-4 is not a parallel phase at all; the Founder view v0 of §99.4 item 7 slips behind S3.
- **(b) Assign only the V1-necessary slices** — H's Founder-view-v0 dashboards and O's exception registry — to existing lanes with new, non-overlapping path roots (for example `dashboards/**` to L4 alongside `metrics/**`, and the governance registry files to L1 alongside `registries/**`), and leave G, J, P with L0. Cost: one amendment to the frozen partition, which must be made once, explicitly, and versioned — not drifted into.
- **(c) Open a sixth lane.** Contradicts the five-lane execution model this plan is written for. Not recommended, listed for completeness.

**Until this is decided, BT-4 does not start and no lane opens a branch touching dashboards, `policies.yaml`, `patterns.yaml`, `os-health.yaml` or `tools.yaml`.**

### DECISION 2 — Unowned paths for named control-plane artifacts — **Resolved: REG-008**

**The gap.** These artifacts are named by the spec and fall outside every lane's OWNS list in PARTITION.md:

| Artifact | Spec | Candidate owner |
|---|---|---|
| `templates/intake-gap-assessment.md` | §96.6 (*"the named template artifact in the control plane"*) | L0 (`docs/**`-adjacent) or L2 (owns `templates/workflows/**` only) |
| `exceptions.yaml` | §95.2, §98.2 Phase 1, invariant 77 | L1 owns `registries/**`; is `exceptions.yaml` a registry? |
| `policies.yaml`, `os-health.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml`, `tools.yaml` | §99.2 subsystem A ("the governance files") | Same question |
| Grafana dashboard JSON | §99.5 (*"dashboards as provisioned JSON"*) | See DECISION 1 |

**Why it blocks.** The minimal `exceptions.yaml` **validator** is an unambiguous L1 deliverable (it is `validators/registry/**`). The **file itself** has no declared owner, and BT-1 cannot complete without it (§98.2 Phase 1 names it explicitly). L0 decides once, records the assignment in a versioned amendment to PARTITION.md, and updates CODEOWNERS in the same commit.

### DECISION 3 — The universal floor's duration and per-product sequence — **Resolved: Q5**

**The gap.** §96.6 states the floor *"carries its own duration in the roadmap"* and that *"costed honestly against the portfolio's starting states it is several weeks."* It gives no number, deliberately — the number depends on the eight products' actual starting states, which only the intake gap assessments reveal.

**What L0 must produce, before BT-1:** the 72-row checklist (9 items × 8 products) with a named executor and a date per row, sequenced by `classification.reliability_criticality` (§96.5), each lower-criticality product still outstanding on a floor item carrying a dated accepted risk mirrored into the exception registry.

**Why it cannot wait.** Two floor items are hard AI-safety gates that block work on the product entirely: S10 (secrets committed — *"No AI-assisted session opens the repository until the S10 check passes"*) and S19 (customer data committed — same rule, and invariant 111). A product failing either is unavailable to any AI-assisted work, including onboarding, until it passes.

### DECISION 4 — Pilot product count and identity for V1 — **Resolved: Q6**

**The gap.** §99.4: *"V1 is the Foundation launch-critical set for 2–3 pilot products."* Two or three is a range; which products is unstated and must follow §96.5's criticality ordering.

**What L0 must produce, before S2:** the named pilot set (2 or 3 products), recorded as a decision with the sequence and deadlines, reviewed at the quarterly operating-system review (§96.5). S3's exit criteria are evaluated against this set and no other.

### DECISION 5 — Calendar anchors that no spec line supplies — **Resolved: Q1**

**The gap.** Three values that everything in this file is relative to, and that the spec does not and cannot fix:

| Anchor | Why the spec cannot supply it |
|---|---|
| BT-0 duration (contract freeze) | `contracts/**` is a PARTITION artifact, not a §99.2 subsystem; it carries no complexity band. It is also the one phase with **zero** parallelism, so its length is added directly to wall-clock |
| The GitHub organisation login (`$ORG`) | Environment-specific. Every command in this file substitutes it |
| Start date for the Build track | Bootstrap exception `start`/`expiry` dates (§95.2), the 90-day restore rotation, and the "roughly month 3" asset-inventory gate are all measured from it |

**Recommendation, for L0 to accept or replace:** set BT-0 at a fixed, short, explicitly-timeboxed duration and treat any overrun as a signal that a contract is being designed rather than transcribed — §99.3 states every registry and contract schema is *"direct transcription to JSON Schema"*, so BT-0 is transcription work, not design work. The design-open items of §99.3 (attention classifier, `make parity` declaration format, plan-checker internals, DevLake field coverage, machine sources for context checks, KPI instrumentation projects, calibration methods) are **not** in `contracts/**` and must not extend BT-0.

---

## 9. One-page summary for L0

```
BT-0  L0 alone. Contracts frozen. Lanes idle. ── S0 ──┐
BT-1  L1 A,B  │ L2 E-skeleton │ L3 D-shell  │ L4 N   │ L5 M,R,K  ── S1 ──┐
BT-2  L1 A,B✔ │ L2 E-build    │ L3 D✔,C-v0  │ L4 I-a │ L5 L,Q,K  ── S2 ──┐
BT-3  L1 v-ct │ L2 E✔,F       │ L3 C L1-L2  │ L4 I✔  │ L5 env    ── S3 ──┐
BT-4  RESOLVED (FD-002) — plan-checker (subsystem G) is owned by L0
──────────────────────────────────────────────────────────────────────────
CRITICAL PATH:  BT-0 → A(M) → B(M) → D(L) → C(L)  =  8–22 weeks
MERGE TRAIN:    L1 → L4 → L2 → L3 → L5, once per cycle, integration→main on full gate
LONGEST LANE:   L3 (6–16 wks). L5 (6–18 wks) is broad but off the critical path.
QA is the onboarding-track constraint, not lane count (§99.6).
G and P tiers are one contended person, calendar-gated (§98.7). Not lanes.
§98.4 items are TRIGGER-gated. Never put them on the timeline.
```

**The single most common way this plan fails:** a lane reports a phase "done" because its code is written, while its acceptance criteria are unevaluable until a sync point lands another lane's output. Written code is not a completed phase. A phase completes at its sync point, on the executed completion check, or it has not completed.
