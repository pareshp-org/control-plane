# 00 — MASTER IMPLEMENTATION PLAN

**Programme:** MultiProduct Engineering and Delivery Operating System
**Implements:** `Research/MultiProduct_MasterSpec_v4.0.md` (v4.0, 10,256 lines)
**Conforms to:** `Code/implementation/PARTITION.md` (FROZEN v1 — authoritative, never redesigned here)
**Owner:** L0 Integrator (human/lead)
**Status of this file:** the front door. If you read nothing else in this document set, read this.

---

## 0. Authority order

When two documents disagree, the higher line wins. There is no other tie-break.

| Rank | Document | What it settles |
|---|---|---|
| 1 | `Research/MultiProduct_MasterSpec_v4.0.md` | What the system must be and do. Section numbers, AT- ids, invariant numbers, SIG- ids and D- ids are cited from here and nowhere else |
| 2 | `Code/implementation/PARTITION.md` | Who owns which path, branch model, merge train, AI-developer profile |
| 3 | This file (`master/00-MASTER-PLAN.md`) | Scope, tiers, calendar, entry criteria, definition of done, document index |
| 4 | `master/`, `protocol/`, `manual/` documents | Process detail |
| 5 | `lanes/L<N>-<nn>-<slug>.md` | Task-level instructions for one lane |

**Binding rule for every lane developer:** you may not resolve a conflict between two of these documents yourself. Stop, open a blocker issue titled `BLOCKER: authority conflict <doc-A> vs <doc-B>`, and wait for L0. The stop conditions are `manual/03-guardrails-and-stop-rules.md` §4 — an authority conflict is **STOP-01** (ambiguous task spec) or **STOP-08** (anything requiring a judgment call); the blocker template and the filing procedure are §6 of that same file. L0 receives it under the escalation protocol of `lanes/L0-00-charter.md` §7.

---

## 1. What is being built

A **GitOps operating-system distribution for one company** — a software company of roughly nine people operating approximately eight products today and approximately twenty within roughly a year (Section 1, spec line 49).

Spec Section 99.1 states the shape exactly: *the operating system is not an application*. It is an operating model implemented as configuration and glue over commodity tools — GitHub as source of truth and enforcement plane; Grafana, DevLake and Prometheus as the presentation layer; YAML registries in a control-plane repository; scheduled jobs as the backend.

Six deliverable classes, and nothing else:

| # | Deliverable class | Subsystems (Section 99.2) |
|---|---|---|
| 1 | Schema-and-validator suite | A, B |
| 2 | Reconciliation engine | C |
| 3 | Provisioning and scaffolding CLI | D |
| 4 | Reusable CI/CD workflow library | E, F |
| 5 | Metrics and report computation layer | I, N |
| 6 | Dashboard provisioning (JSON in git) | H |

Supporting subsystems: K (AI runtime contract enforcement), L (access-control architecture), M (operations VM), O (governance registries and jobs), Q (asset inventory and deadline watch), R (notification routing). Conditional/deferred subsystems: G (plan-checker), J (background machine layer), P (people intelligence engine).

### 1.1 What is explicitly NOT being built

These are refusals, not deferrals of convenience. A lane developer who finds themselves building one of these has misread a task and must STOP.

| Not built | Authority |
|---|---|
| An installer, tenancy model, or upgrade machinery for third parties | Section 99.6 risk 1 — *"Build the internal distribution for this company only"* |
| A bespoke web application for Layer B people data | Section 99.5 — the Layer B mechanism is a second, Founder-only Grafana instance (D75) |
| A separate identity provider | Section 99.5 — `people.yaml` keys on the GitHub login; GitHub OAuth into Grafana; no separate IdP |
| Any metered-LLM or paid-cloud-LLM dependency in engineering tooling | Invariant 83; invariant 84 |
| A second workflow overlay competing with GSD | Invariant 43 |
| Any code path to an automated formal people action | Invariant 37; AT-071 |
| Any per-person raw-activity drill-down on a general dashboard | Invariant 109; AT-089 |
| Keystroke, screen, webcam or presence surveillance; AI token usage as performance; any single-number productivity score; any leaderboard | Invariants 96, 97, 98, 99; AT-075 |
| A product list hard-coded in any dashboard, workflow or script | AT-001; invariant 52 |
| Background machine layer, until its CPU benchmark passes | Section 99.4 explicitly-deferred; Section 98.2 Phase 3 |
| Shared-service registry, split/merge/transfer, dependency-graph views, versioned-contract migration machinery, domains/topology activation, predictive economics and forecasting, Layer B decision support | Section 99.4, "Explicitly deferred" |

---

## 2. The five-lane model, and why the partition is drawn where it is

Five AI developers (Sonnet-4.6-class, low cost, no repo context, no judgment authority) build simultaneously on five branches, plus one human/lead integrator (L0). The partition in `PARTITION.md` is frozen; this section explains *why* it is drawn there so a lane developer understands the rule they are obeying, and never argues with it.

| Lane | Branch prefix | Subsystems | Exclusive paths |
|---|---|---|---|
| **L1** Registries & Contracts | `lane/1/*` | A, B | `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` |
| **L2** Pipeline & Evidence | `lane/2/*` | E, F | `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` |
| **L3** Reconciler & Provisioning | `lane/3/*` | C, D | `reconciler/**`, `tools/provision/**`, `validators/drift/**` |
| **L4** Records, Events & Metrics | `lane/4/*` | I, N | all of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` |
| **L5** Access, Infra & Ops | `lane/5/*` | K, L, M, Q, R | `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` |
| **L0** Integrator | `main`, `integration` | — | `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` |

### 2.1 Why the cut lines fall here

The partition is not a division of labour by topic. It is a division by **merge-conflict surface**, then by **dependency direction**.

1. **The cut follows the dependency spine of Section 99.2**, which reads: A (registries) → B (validation) → C (reconciliation) and D (provisioning); E (workflows) → F (evidence chain) → H/I (views and metrics). L1 holds A+B because B is meaningless without A in the same tree. L3 holds C+D because C's declared-state input is D's output surface. L2 holds E+F because F reads exactly what E emits.
2. **`control-plane-records` is a whole repository given to one lane.** Section 97.1 puts records and events behind the records-writer credential (D89), and D107 blocks force-push and deletion there with a no-bypass ruleset. Two lanes writing one append-only store with an anchored head SHA is the one shape D107 exists to make detectable. L4 owns it entirely.
3. **`contracts/**` belongs to nobody but L0 and is frozen before B-Day.** Rule 2 of the partition. Every cross-lane fact — schema shapes, event envelope, workflow inputs, drift-finding format — is expressed there, so no lane ever reads another lane's source tree. That is why rule 4 (no cross-lane imports) is enforceable at all.
4. **No shared mutable file, ever** (rule 3): directory-per-item, one file per event, per record, per schema. This is why parallel merges cannot conflict, and it is the same property Section 97.3 demands of the event log — *"one file per event, never a concurrent append to a shared period file, so parallel workflow runs never contend"*. The build model and the runtime model share a rule.
5. **L5 is independent at build time and integrates last**, because access, infra, ops-VM, notification and asset inventory are configuration surfaces nothing else compiles against.

### 2.2 The merge train

Fixed order, once per cycle: **L1 → L4 → L2 → L3 → L5**, into `integration`; `integration` → `main` when the full gate passes. That order is the dependency order of §2.1: schemas and record schemas first (everything validates against them), then workflows, then the reconciler that consumes both, then access/infra.

A lane NEVER merges another lane's branch and NEVER rebases another lane's branch. The model is `master/02-branch-merge-model.md`; the cycle as a procedure is `protocol/06-integration-cycle.md`; the literal commands L0 runs slot by slot are `lanes/L0-03-merge-train.md`.

### 2.3 Subsystems the frozen partition does not assign

Honesty first: the five lanes cover the Foundation/V1 surface. Five subsystems have **no owning lane** in the frozen partition. Three of them are derivable from existing path ownership without amending anything; two are not.

**Derivable — no decision needed, stated here so no lane invents a home for them:**

| Subsystem | Where its Foundation-scope pieces land | Derivation |
|---|---|---|
| **O** Governance registries and jobs | `exceptions.yaml`, `policies.yaml` → `registries/**` (L1); their validators → `validators/registry/**` (L1); automatic expiry revocation → `reconciler/**` (L3); scheduled job hosting → `ops-vm/**` (L5) | Section 99.2 lists O as depending on A and C; the artefacts are registries and reconciliation rows, both already owned |
| **J** Background machine layer | cage configuration files, egress override, systemd stop unit → `infra/**` and `ops-vm/**` (L5) | Section 99.2 names them host artefacts; Section 96.6 makes the Hermes hosts estate machines. **Nothing here is built until the Phase 3 CPU benchmark passes** (Section 98.2) |
| **P** People intelligence engine | out of scope for these five lanes entirely | Section 99.4 item 9: from the people tier, nothing initially. Section 98.6 hard-gates P4 on the Layer B datasource separation, itself a P2 deliverable |

> ### L0 DECISION REQUIRED — D-PLAN-01: owner of Subsystem H (dashboards and views)
> Grafana dashboards are provisioned from JSON in git (Section 99.5). No path in `PARTITION.md` names a dashboard directory. Section 99.4 item 7 puts **Founder view v0** inside V1, so this cannot wait.
> **Option A** — L4 owns it under `metrics/**` (dashboards are the read surface of the metrics layer; keeps computation and presentation in one lane).
> **Option B** — L5 owns it under `ops-vm/**` (Grafana runs on the ops VM; keeps all VM-resident configuration in one lane; matches the Section 99.5 statement that dashboards are provisioned configuration on that host).
> **Option C** — L0 owns it under `docs/**`-adjacent root path and hand-maintains it. **Rejected on sight by invariant 46** (derived data is computed, never hand-maintained) — listed only so it is visibly rejected.
> **Constraint on the decision:** whichever lane is chosen, the Layer B split of Section 99.5 and D75 means the **Founder-only instance's provisioning must live in a path the chosen lane owns and AT-097 must be executable against it** — AT-097 verifies the people datasource is absent from the shared instance's provisioned configuration, *not inferred from panel visibility*.
> **L0 records the choice in the decision register built by `lanes/L0-04-decisions-register.md` — the row is `REG-001`, and D-PLAN-01 is one of its sixteen source ids across thirteen concordance rows (that file's §5 concordance). The row lives in `docs/decisions/register.tsv`, the open statement in `docs/decisions/open/REG-001.md`, the closure in `docs/decisions/closed/REG-001.yaml`. This happens before B-Day. Until `REG-001` reads `closed`, no lane creates a dashboard directory.**

> ### L0 DECISION REQUIRED — D-PLAN-02: Subsystem G (plan-checker and Gate 1 tooling)
> Section 99.3 item 3 lists plan-checker internals as **design-open**: *verify every assumed capability against the exact pinned GSD release before configuring it; budget building the checker in-house if verification fails.* Section 99.6 risk 4 rates it a volatility risk. Section 99.2 prices it "L if built in-house" (3–8 weeks). It has no owning lane.
> **Option A** — pinned GSD release verifies: G is configuration only; L0 owns it under root files; no lane builds anything; Onboarding Phase 7 proceeds.
> **Option B** — verification fails: G is an in-house build of L complexity. It needs a lane and a path, which requires an L0 amendment to the frozen partition — the only amendment this plan contemplates.
> **Option C** — verification fails and G is parked: Phase 7 (GSD Activation) is recorded as `declined` per Section 98.1 ("Declined is a state, not an absence"), with gate answers, forgone capabilities and a review date. Planning artifacts remain plain markdown and YAML regardless (Section 99.6 risk 4 mitigation), so this loses tooling, not truth.
> **The capability-verification run against the pinned release is an entry-criterion task (§5, EC-9). L0 records the outcome and the option taken before Onboarding Phase 7 is scheduled for any product.**

---

## 3. The three build tiers, mapped to lanes

Section 98.1: one roadmap, three tiers. **Foundation (Phases 1–7)** builds the delivery operating system and onboards the portfolio. **Governance (G1–G8)** instruments the operating system itself. **People (P1–P8)** builds capacity and management intelligence on top of governance data.

| Tier | Spec phases | Lanes engaged | Priority mix | Gate to enter the tier |
|---|---|---|---|---|
| **Foundation** | 1–7 (Section 98.2) | L1, L2, L3, L4, L5 — all five, full engagement | launch-critical | Entry criteria of §5 all green |
| **Governance** | G1–G8 (Section 98.5) | L1 (registries, invariant classification), L3 (reconciliation Levels 1–4), L4 (health computation, attention ledger), L5 (ops VM jobs); H per D-PLAN-01 | G1 P0, G2 P0/P1, G3 P1/P2, G4 P1, G5 P2, G6 P2/P3, G7 P1-build/P3-activate, G8 P1/P2 | Foundation DoD (§6.2) green **and** each phase independently passes the Section 59 platform investment gate |
| **People** | P1–P8 (Section 98.6) | Subsystem P has **no lane** — requires an L0 partition amendment (§2.3) | P1–P4 priority P1, P5–P7 P2, P8 P3 | G3 attention ledger live; **and** for P4, the Layer B datasource separation verified — *verified* means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds (Section 98.6) |

### 3.1 The two binding sequencing rules the whole plan obeys

1. **P0-before-P2, binding** (Section 98.1): no P2 or P3 capability may be started while a P0 capability is unbuilt. A phase recorded `declined` releases the lock; an `unbuilt` P0 holds it exactly as written.
2. **Calendar-gating honesty** (Section 98.1): the critical path of the upper tiers is elapsed operation time, not engineering effort. Pattern detection needs realistically two quarters of incident and exception history (G4); capacity forecasting at least two quarters of attention data (G5); framework evolution at least two full review periods of evidence (P8). No build acceleration compresses this, and no predictive layer is built before its data exists.

### 3.2 Tier-level phase gate

Each Governance and People phase passes the same gate any platform investment passes (Section 59; Section 98.1). The seven investment-gate answers per phase are authored into the standing ledger entry in `economics.yaml` **before the phase is committed** — Phase 1 authors the block for Phases 1–7 (Section 98.2; D104). A phase that cannot justify itself is not built, and is recorded `declined`, not silently skipped.

---

## 4. The honest calendar

> **This section is Section 98 as amended by D99.** D99, verbatim on the point: *"§98.2 stamped absolute weeks on phases whose deliverables §99.2 prices three to ten times higher... The phases split into a Build track dated by subsystem with its complexity band, and an Onboarding track whose per-product phases are relative to the subsystems they consume. Pre-onboarding deadlines are set from the Onboarding track, not from the labels."* (Appendix A, D99; scope §98.1, §98.2, §98.3, §99.2, §99.4, §96.2.)
>
> **Consequence, stated plainly so no lane developer is misled:** the strings "Week 1", "Week 2", "Week 3", "Weeks 4–5", "Weeks 5–7", "Week 7", "Week 8" in Section 98.2 are **configuration-elapsed labels**. They are not build estimates and no task in this plan is scheduled against them.

Three tracks run at once. Only Track M is dated in absolute working days. Track B is dated in **build-elapsed weeks from B-Day**, banded by subsystem complexity. Track O is dated **relative to named Track B milestones**.

Complexity bands are Section 99.2's: **S** under a week, **M** one to three weeks, **L** three to eight weeks, **XL** multi-month — for one competent engineer with AI assistance, excluding per-product content work.

### 4.1 Track M — manual and configuration (L0 and named humans; absolute days)

No AI developer executes anything in this track. There is no single human-only-operations file; the prohibition is enforced in three places that do exist. `manual/03-guardrails-and-stop-rules.md` §2 states the standing prohibitions `P-1`…`P-8` an AI developer may never cross, and §4 the eight STOP conditions. `lanes/L0-00-charter.md`, `lanes/L0-01-phase-0-contracts.md`, `lanes/L0-02-lane-guard.md`, `lanes/L0-03-merge-train.md`, `lanes/L0-04-decisions-register.md`, `lanes/L0-05-integration-gate.md` and `lanes/L0-06-bootstrap-mode.md` each declare **Executor: the human lead — not an AI developer** in their header, and every command in them is run by a person. `lanes/L0-07-onboarding-track.md` is the one L0 file an AI developer does execute, and it marks each privileged step **HUMAN STEP**, where the executor's obligation is to record and verify the evidence and never to perform the step.

| ID | Work | Spec | Duration | Runs |
|---|---|---|---|---|
| M-1 | Consolidate all products into one company-owned GitHub organisation; move any repository on a personal account (S9) | 98.2 Phase 1; 96.6 S9 | 2–5 working days | before B-Day |
| M-2 | Organisation base permission Read; Teams grant Write **from an interim assignment set**, created **before** branch protection is armed (D101) | 98.2 Phase 1; 95.2 | 1 day | before M-3 |
| M-3 | Branch protection on every repository, **required-status-check list starts empty per repository** and is populated as each check comes into existence | 98.2 Phase 1 | 1 day | after M-2 |
| M-4 | Second organisation Owner, or escrowed break-glass Owner credential with a named escrow custodian | 98.2 Phase 1 completion check | 1 day | before B-Day |
| M-5 | Organisation-enforced 2FA verified active; hardware keys or passkeys for Founder, org Owners, platform-admin holders | 98.2 Phase 1 completion check | 1 day | before B-Day |
| M-6 | S10 and S19 sweeps on every live repository — committed secrets rotated (rotation, not rewriting, is the control); committed customer data inventoried, notified where required, removed from the working tree | 96.6 S10, S19; invariant 111 | 3–10 working days | before B-Day; blocks AI access to the repository until passed |
| M-7 | **The universal floor** — nine items × every live product = **72 tracked obligations at eight products**, one checklist row per item per product, each with a named executor and a date | 96.6 | **several weeks**, sequenced by `classification.reliability_criticality` per 96.5 | parallel with Track B, **never inside Phase 1's label** |
| M-8 | One-page per-repository transition note for each existing team; names the human to ask when a merge blocks, with a same-day response commitment for two weeks after branch protection lands | 95.4 | 1 day/repo | with M-3 |
| M-9 | Weekly bootstrap log entry, three-field template under `records/bootstrap-log/`; **Blocking drift when the newest entry is older than 7 days** (calibrated) | 95.4 | minutes/week | every week of the programme |

### 4.2 Track B — build, dated by subsystem (build-elapsed weeks from B-Day)

B-Day = the first lane commit, which is only legal once every entry criterion in §5 is green.

| Milestone | Contents | Subsystems (band) | Lane | Starts at | Band |
|---|---|---|---|---|---|
| **B0** | Entry checklist green; `contracts/**` authored and FROZEN; lane-guard CI check live; five lane branches created | — | L0 | — | 3–5 working days (config-elapsed) |
| **B1** | Every registry and product-contract schema present; multi-version validators, referential integrity, date rules, the 24x7-without-rota and commitments-conflict blockers, exception-without-expiry rejection, unclassified-control rejection — all green in control-plane CI | A (M) + B (M) | L1 | B0 | **2–6 weeks** |
| **B2** | Reusable workflow library v1, consumable by pinned tag: `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue`; digest invariant enforced in code; parity job; delta-gated scanning; SBOM emission; Friday-freeze time gate | E (L) | L2 | B1 | **3–8 weeks** |
| **B3** | Provisioning v0: `create-product` and `add-person` generating repository, Teams, CODEOWNERS, branch protection and registry entries with **zero hand-editing** | D (L) | L3 | B1 | **3–8 weeks** |
| **B4** | Reconciliation v0 — **detect and block only**: Teams versus registries, expiry revocation, protection drift, orphan detection at blocking severity. Auto-repair is NOT built here | C (L, v0 slice) | L3 | B3 | **3–8 weeks** |
| **B5** | Metrics pipeline and work-tracking conventions: DevLake nightly ingest; Prometheus scraping `/health`, `/version`, `/metrics`; Scorecard scheduled scan with drop detection; event-log taxonomy with the D103 envelope; boards per product plus portfolio aggregate (or the single-Project fallback) | I (L) + N (M) | L4 | B1 | **4–11 weeks** |
| **B6** | Access model (org base Read plus Teams-derived Write; branch and environment protection; five secret tiers; fail-closed classification; the Layer B split per D75); AI runtime contract enforcement; operations VM; asset inventory and deadline watch; notification routing | L (M–L) + K (M) + M (M) + Q (S–M) + R (S) | L5 | B0 | **4–18 weeks** |
| **B7** | Evidence chain store and query: eleven-question answerability for any production artifact; `/version` digest-match monitoring at 100%; `verify-digest-chain` sweep; append-only history with effective dating | F (M) | L2 | B2 | **1–3 weeks** |

**Critical path:** B1 → B3 → B4 = **8 to 22 build-elapsed weeks**. L5's chain (B6) runs 4–18 weeks in parallel from B0 and is the only serious contender for the path. Every other lane finishes inside that window.

**Reconciling this with Section 99.2's own total.** Section 99.2 prices the *full* surface at 10–14 engineer-months at single-implementer pace, excluding per-product onboarding content and excluding the calendar time the upper tiers need for data accumulation. Section 99.4 sizes V1 at *roughly 30% of the build surface*. Five lanes running in parallel do not divide by five, because B1 → B3 → B4 is serial by construction: **8–22 build-elapsed weeks is the honest band for Track B, and it replaces "Weeks 1–3" as the Foundation build date.** L0 publishes the chosen point in the band, with its reasoning, as a row in the decision register built by `lanes/L0-04-decisions-register.md` — raised here as **D-PLAN-03**, carried in `docs/decisions/register.tsv` with its statement in `docs/decisions/open/` and its closure in `docs/decisions/closed/`; §6 of that file is the procedure for admitting an id the register does not yet carry. No lane treats an unpublished point estimate as real.

**Where the Section 98.2 labels map, for readers coming from the spec:**

| Section 98.2 label | Track | Real dating |
|---|---|---|
| Phase 1 — "Week 1" | Track M, items M-1 … M-8 | configuration-elapsed, ~1 week of human work; the universal floor (M-7) is **several weeks and runs beside it, never inside it** (96.6) |
| Phase 2 — "Week 2" | Track B, part of B5 and B6 | build-elapsed; DevLake + Grafana are subsystems M and I, bands M and L |
| Phase 3 — "Week 3" | Track B, B1 → B3 → B4 | build-elapsed **8–22 weeks**. This is the single largest correction D99 makes |
| Phases 4–7 — "Weeks 4–8, per product" | Track O | relative to B2/B3/B7 and to the product's own predecessor phase |

### 4.3 Track O — onboarding, per product, relative

Per Section 96.5: realistic pace is **3–4 weeks per product** for anything not already deploying through CI/CD; the first product takes longer; subsequent products inherit the pattern and the scaffolding. Sequencing rule: highest `classification.reliability_criticality` first; within equal criticality, by `business.criticality`, then by expected onboarding cost, cheapest first. At eight products this is roughly two quarters (Section 96.1).

| Onboarding phase | Consumes | Earliest start (relative) | Duration |
|---|---|---|---|
| **Intake gap assessment** (precedes everything) | `templates/intake-gap-assessment.md` | any time after B0 | 0.5–2 days/product |
| **O-4 Environments** (spec Phase 4) | E (B2), D (B3), secret tiers (B6) | `max(B2, B3, B6)` + 0 | 1–2 weeks |
| **O-5 Verification** (spec Phase 5) | B (B1); the product's O-4 | O-4 complete | AI drafts, then **QA-takeover SLA: two weeks** from the drafted suite landing (96.6) |
| **O-6 Delivery Pipeline** (spec Phase 6) | E (B2), F (B7) | `max(O-5, B7)` | ~1 week |
| **O-7 GSD Activation** (spec Phase 7) | G — **see D-PLAN-02** | O-6 complete, and D-PLAN-02 resolved | days |

**Out-of-order exception, mandatory:** a product in starting state **S3 (CD only — auto-deploy with no meaningful tests)** takes O-5 *before* O-6, out of normal order (96.6, S3). S3 is named in the spec as the most dangerous state; its interim CD gating happens in Track M, not here.

**D99's operative consequence:** *pre-onboarding deadlines are set from the Onboarding track, not from the labels.* Every `deadline` field in a product's pre-onboarding block (Section 96.2) is derived from that product's position in the Track O sequence and the Track B milestones it consumes — never from "Weeks 4–5". A deadline set from a label is a deadline that will breach, and a breached deadline is Red under Section 96.4.

### 4.4 Governance and People tiers — no calendar

Neither tier gets a date in this plan, and that is deliberate.

| Tier phase | Its clock | Earliest possible start |
|---|---|---|
| G1 | reconciliation, DevLake and Grafana operational | after B4 and B5 |
| G2 | G1 | after G1 |
| G3 | G1–G2; DevLake field coverage confirmed (Section 99.3 item 4) | after G2 |
| G4 | **realistically two quarters of G1 data** | G1 + ~2 quarters |
| G5 | **at least two quarters of G3 attention data** | G3 + ~2 quarters |
| G6 | G5 | after G5 |
| G7, G8 | build-gated, not data-gated | after G2 |
| P1 | G3 attention ledger | after G3 |
| P2 | Framework v1 source (Section 78); subsystem L | after P1 |
| P4 | P2–P3 **and** Layer B separation verified (AT-089, AT-091, AT-097, AT-098 pass; invariant 109 holds) | hard gate, no exception |
| P8 | **at least two full review periods of P4 evidence** | P4 + 2 review periods |

Effort, for budgeting only (Section 98.7): G1–G2 roughly 2–4 weeks of effort spread across a quarter, one person part-time; G3–G5 roughly 1–2 weeks per phase; G6–G8 and the People tier one person opportunistically. **No dedicated platform team, no dedicated data engineer, and no new headcount is justified by the governance or people tiers themselves. If either tier appears to require a hire, the scope is wrong** (Section 98.7).

---

## 5. Entry criteria — what must be true before B-Day

Every criterion is a command with an unambiguous output. **If any one fails, B-Day does not happen.** No lane branch is created, no lane developer is started. This checklist is executed by L0 as part of Phase 0: the gate that records its result is `L0-P0` in `master/05-entry-exit-criteria.md` §2, and the task list that produces the artefacts each criterion reads is `lanes/L0-01-phase-0-contracts.md` §4 (task index in its §7). `EC-` ids are this file's own id space and are cited from here; `master/05-entry-exit-criteria.md` names its own gate ids (`UEG-1`…`UEG-5`, `UXG-1`…`UXG-4`, `L0P0-E1`…) and the two spaces are not interchangeable.

Set these once:

```bash
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP="$ORG/control-plane"
export CPR="$ORG/control-plane-records"
```

**EC-1 — GitHub plan tier is Team or higher.** D73 settles this: branch protection on private repositories requires the Team plan, non-negotiable and verified. Environment required reviewers are Enterprise-only and are NOT depended on.

```bash
gh api "/orgs/$ORG" --jq '.plan.name'
# PASS: prints "team", "business", or "enterprise". FAIL: prints "free".
```

**EC-2 — The three repositories exist.**

```bash
for r in control-plane control-plane-records product-template; do
  gh api "/repos/$ORG/$r" --jq '.full_name' || echo "MISSING: $r"
done
# PASS: three full_name lines, no MISSING line.
```

**EC-3 — `control-plane` carries full branch protection and NO machine bypass actor (D89).**

```bash
gh api "/repos/$CP/rulesets" --jq '.[].id' | while read -r id; do
  gh api "/repos/$CP/rulesets/$id" --jq '[.rules[]?.type] | (contains(["required_status_checks"]) and contains(["pull_request"]) and contains(["required_signatures"]))'
done | grep -qx true && echo PASS || echo FAIL
# PASS: at least one single ruleset's own rules contain all three types. Checked per ruleset, not flattened
# across every ruleset the repo has, so a second, unrelated ruleset (e.g. tag protection) cannot supply a
# required type on the branch-protection ruleset's behalf.
gh api "/repos/$CP/rulesets" --jq '.[].id' | while read -r id; do
  gh api "/repos/$CP/rulesets/$id" --jq 'if has("bypass_actors") then .bypass_actors[] else empty end'
done | jq -s 'length'
# PASS: prints 0. Any non-zero is a machine bypass actor and violates D89.
```

**EC-4 — `control-plane-records` has the D107 no-bypass ruleset: force-push and deletion blocked, fast-forward commits permitted, no review protection.**

```bash
gh api "/repos/$CPR/rulesets" --jq '[.[] | select(.enforcement=="active") | .rules[].type]'
# PASS: contains "non_fast_forward" and "deletion". MUST NOT contain "pull_request".
```

**EC-5 — Environment protection rules and Projects aggregation verify.** Section 98.2 Phase 1: *verify plan-tier dependencies*. Section 99.6 risk 5: an unavailable protection feature reproduces the silent-gate failure; fallbacks are recorded as accepted risks, never assumed.

```bash
gh api "/repos/$CP/environments" --jq '.environments[].name'
gh api graphql -f query='query($o:String!){organization(login:$o){projectsV2(first:5){nodes{title}}}}' -f o="$ORG"
# PASS: both return without error. FAIL on either: record the fallback as a dated accepted risk in exceptions.yaml before proceeding (Section 99.5 — the single org-level Project with a product field is the default fallback).
```

**EC-6 — No API key anywhere, on any machine, including shell profiles and repository `.env` files.** Invariant 84; Section 95.3 binds this from day one.

```bash
env | grep -i api_key ; echo "exit=$?"
grep -RIl --exclude-dir=.git -iE 'api[_-]?key' ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
# PASS: no matching env lines (exit=1 from grep) and no file list printed.
```

**EC-7 — Pre-Phase-1 baselines captured.** Section 103.14: *baselines are captured before Phase 1 of Section 98 begins*. One-time **banded self-estimates** — bands, not minutes — labelled as estimates in the record and never mixed with ledger-derived data. Minimum set: Founder coordination time per week; Team Lead coordination hours per week; engineering hours per product per month; developer disruption hours per month; the Founder operating-load ceiling that SIG-43 breaches against. Every other Section 103.13 measure carries a recorded baseline estimate or an explicit `unbaselined` marker. Verified by **AT-046**.

```bash
test -f records/baselines/pre-phase-1.yaml && \
  grep -c 'provenance: estimate' records/baselines/pre-phase-1.yaml
# PASS: file exists and the count is >= 5.
```

**EC-8 — Bootstrap exceptions authored, and the minimal validator has teeth.** Section 95.2: Phase 1 ships a minimal `exceptions.yaml` schema validator in control-plane CI — expiry present, owner present, deactivation trigger present — *so bootstrap exceptions have mechanical teeth from week one*. Bootstrap Mode is scoped **per repository, never per company**; product repositories whose existing teams hold Write never enter bootstrap.

```bash
make validate-exceptions
# PASS: exit 0 on the real file.
make validate-exceptions FIXTURE=tests/fixtures/exceptions/malformed-no-expiry.yaml
# PASS: exit != 0. An exception without an expiry MUST be rejected (invariant 77).
```

**EC-9 — Plan-checker capability verification run against the pinned GSD release.** Section 99.3 item 3; Section 99.6 risk 4. Outcome feeds **D-PLAN-02**. This is a verification run, not a build.

```bash
# L0 executes the capability matrix against the pinned tag and records the result:
test -f records/decisions/plan-checker-capability-verification.yaml
# PASS: the record exists and names the pinned tag, each assumed capability, and verified|unavailable per capability.
```

**EC-10 — DevLake's required database engine and version confirmed for the pinned release.** Section 99.5: *it determines the compose file and the control-plane backup procedure.* Recorded before L5 touches `infra/**`.

```bash
test -f records/decisions/devlake-substrate.yaml
# PASS: the record names engine, version and the compose file it implies.
```

**EC-11 — The standing operating-system ledger entry exists in `economics.yaml`.** D104 moves it to Phase 1 as a hand-authored stub so the investment gate can gate the phases it is supposed to gate. Seven investment-gate answers for Phases 1–7 (Sections 57.2, 59.2), the predicted saving, and a dated scoring commitment.

```bash
yq '.entries[] | select(.id=="operating-system") | .gate_answers | length' registries/economics.yaml
# PASS: prints 7.
```

**EC-12 — `contracts/**` is authored and FROZEN.** Partition rule 2. This is the single largest determinant of whether five parallel lanes can merge without conflict.

```bash
test -d contracts && git log -1 --format=%H -- contracts/ && \
  gh api "/repos/$CP/rulesets" --jq '[.[] | select(.rules[].type=="pull_request") | .conditions.ref_name.include[]?]'
# PASS: contracts/ exists, has a commit, and CODEOWNERS assigns it to L0 alone.
grep -E '^/contracts/' CODEOWNERS
# PASS: exactly one line, owner is the L0 identity, no lane identity present.
```

**EC-13 (Phase 1) — The lane-guard CI check is live and fails a foreign-path PR.** Partition rule 1: a lane PR touching a foreign path FAILS the lane-guard check, no exceptions. Without this the entire anti-conflict model is an intention. *Phase 0 keeps required_status_checks empty (lane-guard not yet deployed); the live guard is a Phase 1 precondition.*

```bash
make lane-guard LANE=1 FILES="schemas/registry/people.schema.json"   # PASS: exit 0
make lane-guard LANE=1 FILES="reconciler/main.py"                    # PASS: exit != 0
make lane-guard LANE=1 FILES="contracts/drift-finding.schema.json"   # PASS: exit != 0
```

**EC-14 — CODEOWNERS contains human identities only, and the negative test is executed.** Section 98.2 Phase 1 completion check: *an approval from a machine account does not satisfy branch protection — CODEOWNERS is generated to contain human identities only, and the check is executed negatively.*

```bash
make codeowners-human-only
# PASS: exit 0, and the run prints the negative-test result: a machine-account approval did NOT satisfy protection.
```

**EC-15 — Five lane branches created off `integration`, one per lane, and `integration` exists off `main`.**

```bash
git ls-remote --heads "https://github.com/$CP.git" | grep -E 'refs/heads/(main|integration)$'
# PASS: both lines present.
```

**EC-16 — All Phase 0-gated decisions closed.** `lanes/L0-04-decisions-register.md` §3 lists every `REG-` entry that is Ph0-gated. Each must carry a dated closure record in `docs/decisions/closed/` before B-Day. This gate is `make decisions-gate` and is chained into `make promote-check` via `L0-04-07`; it is stated here so that the entry-criteria checklist is complete and so cross-referencing documents (`master/05` §2, `protocol/11` §1) can cite it by id.

```bash
make decisions-gate
# PASS: prints zero open Ph0-gated entries, e.g. "decisions-gate: 0 open Ph0 entries".
# FAIL: any non-zero count. Do not mark B-Day; resolve the open entry under its REG- id.
```

---

## 6. Definition of done

Three DoD levels. Each is a command set, not a judgment. **Nothing is done because someone says it is done** — Section 96.6's rule generalises to the whole programme: *the gap assessment is honest or it is useless... the completion checks are executed as written, never assumed.*

L0 owns the `Makefile` (partition), so these targets are normative and L0 authors them at B0.

### 6.1 V1 done — the minimal honest V1

Section 99.4 defines V1 as the Foundation launch-critical set for **2–3 pilot products**, plus the near-free P0 governance design rules, *roughly 30% of the build surface*, delivering *declared state enforced, drift visible, orphans impossible to miss, every production artifact traceable*.

All nine Section 99.4 items, each with its check:

| # | Section 99.4 item | Check |
|---|---|---|
| 1 | Control-plane repository, schemas and CI validation, with effective dating and append-only discipline from the start | `make validate` exits 0; `make check-append-only` exits 0 |
| 2 | GitHub enforcement: one organisation, base Read, Teams-derived Write, branch protection with most-recent-push approval, environments — **completion checks executed as written** | `make phase1-completion-check` exits 0 and prints each Section 98.2 negative test with its result |
| 3 | Scaffolding v0 (`create-product`, `add-person`) | `make at AT=AT-001` and `make at AT=AT-002` exit 0 |
| 4 | Delivery pipeline with the digest invariant, one tested rollback and one recorded restore test per pilot product | `make at AT=AT-103` exits 0; `make evidence-chain PRODUCT=<p>` answers all eleven questions |
| 5 | Verification-contract skeleton with CI presence enforcement | `make validate` rejects a fixture product with no verification contract (invariant 1) |
| 6 | Reconciliation v0, detect and block only; stricter-only rule enforced in code and tested | `make at AT=AT-102` and `make at AT=AT-033` and `make at AT=AT-110` exit 0 |
| 7 | Founder view v0 from GitHub API, reconciliation output and Scorecard | `make founder-view-v0` renders with zero hand-maintained numbers (invariant 46) |
| 8 | Exception registry with mandatory expiry; safe defaults in provisioning templates; fail-closed classification written down; the control-plane/data-plane invariant test | `make at AT=AT-036`, `AT-037`, `AT-039` exit 0; `make at AT=AT-029` exits 0 (invariants 75, 76) |
| 9 | People-tier schemas designed with effective dating, nothing else | `make validate` passes on people schemas; **no** Layer B artefact exists yet |

```bash
make dod-v1
# PASS: exit 0, and the run prints one PASS line per row above with the AT- id it executed.
```

**V1 also holds, from day one, everything Section 95.3 declares binding even in bootstrap:** digest immutability (invariant 22), verification contracts (invariant 1), secrets tiers and the API-key-free environment (invariants 25, 84), append-only history and effective dating (invariant 47), the constitution and the untrusted-input rule (invariant 20), safe defaults and fail-closed classification (invariants 79, 80), the explicit production-approval event (invariant 12), and the registry-change lane's staged apply and authority-delta gate.

### 6.2 Foundation tier done

Every Section 98.2 completion check executed as written, for every live product, plus the whole-portfolio conditions:

```bash
make dod-foundation
```

passes only when all of the following hold:

| Condition | Authority |
|---|---|
| Every live product is fully onboarded — Phases 4–7 complete — **or** carries a pre-onboarding block with a named deadline that has not been breached | 96.2, 96.4 |
| The portfolio adoption ratio reaches 100% by the last named deadline | 96.4 |
| Every universal-floor row (72 at eight products) is closed with a named executor and a date, or carries a dated accepted risk mirrored into the exception registry | 96.6 |
| Zero Blocking drift open | 98.5 G1 exit; 53 |
| Every reconciliation run finds the seeded canary; a zero-finding run is a **failed** run raising SIG-13 | AT-102 |
| The eleven-item evidence chain is answerable for one real deployment per product | 98.2 Phase 6; F |
| One deliberate rollback succeeded in staging, per product | 98.2 Phase 6 |
| One restore test recorded per product, entering the rolling 90-day rotation; a `restore_tested` date older than the window fails CI | 98.2 Phase 6; invariant 4 |
| Every bootstrap exception is either closed against its activation checklist with cited weekly-log entries, or is live with an unexpired date | 95.2, 95.4; AT-039 |
| The Foundation-scope acceptance-test set passes (§6.4) | 100 |
| No dashboard, workflow or script contains a product list | AT-001; invariant 52 |

### 6.3 Programme done

Section 100 preamble is the definition, verbatim in substance: *the operating system is complete only if every test in this section passes by configuration, onboarding and record-keeping alone — with no redesign of the architecture.*

```bash
make dod-programme
```

passes only when:

1. **All 110 acceptance tests pass.** The catalogue is AT-001 to AT-100 plus AT-101–AT-103 (Platform), AT-104–AT-107 (Governance) and AT-108–AT-110 (Access), across six domains: Extensibility, Lifecycle, Platform, Governance, People, Access.
2. **All 111 invariants carry a checkable enforcement classification.** Section 101 preamble: each is exactly one of **mechanical** (naming the CI check, branch-protection rule, reconciliation row or AT- identifier that enforces it), **policy** (naming the `policies.yaml` entry carrying owner, review date and enforcement mechanism), or **review-held** (naming the standing review that reads it and the role that chairs it). The classification is authored at **Phase G2**.

```bash
make invariant-classification
# PASS: exit 0. Control-plane CI FAILS when an invariant classified "mechanical" names no live
# check or AT- identifier, when one classified "policy" names no live policies.yaml entry,
# or when any invariant carries no classification at all.
```

3. **No architecture rewrite was required to pass any test.** Section 100 preamble: *if any test requires rewriting the architecture, the architecture is not sufficiently extensible and the defect is in this specification, not in the situation.* A test that could only be made to pass by redesign is escalated to L0 as a specification defect, never worked around in a lane.
4. **Every Governance and People phase is either built and passing its exit criteria, or recorded `declined`** with gate answers, forgone capabilities and a review date (Section 98.1). `declined` is a valid programme-done state. `unbuilt` is not.
5. **The quarterly operating-system review has run end to end from the generated review pack and retired at least one policy, one metric or one automation, or explicitly recorded why nothing warranted retirement** (Section 98.5 G8 exit; AT-045). *A review that only adds is a failed review.*

### 6.4 Which acceptance tests gate which tier

Section 100 preamble: *each test is verified at the implementation phase where the capability it exercises activates.* The Foundation gate set is therefore a subset, and the rest are not failures — they are not yet armed.

| Gate | Acceptance tests |
|---|---|
| **V1** | AT-001, AT-002, AT-029, AT-033, AT-036, AT-037, AT-039, AT-046, AT-102, AT-110 |
| **Foundation** | the V1 set, plus AT-009, AT-010, AT-030, AT-031, AT-034, AT-035, AT-038, AT-047, AT-049, AT-051, AT-103 |
| **Governance** | AT-032, AT-040 … AT-045, AT-048, AT-050, AT-104 … AT-107, AT-101, and the Platform set AT-023 … AT-028 as each capability activates |
| **People** | AT-052 … AT-088, and the Access set AT-089 … AT-100, AT-108, AT-109. **AT-089, AT-091, AT-097 and AT-098 plus invariant 109 are the hard gate on P4** (Section 98.6) |

```bash
make at-suite TIER=v1
make at-suite TIER=foundation
make at-suite TIER=governance
make at-suite TIER=people
# Each prints one line per AT- id: "<id> PASS" | "<id> FAIL" | "<id> UNARMED <phase-that-arms-it>".
# A tier gate passes only when its own rows are all PASS. UNARMED rows outside the tier are not failures.
```

`UNARMED` is the Section 52.2 arming discipline applied to the test suite, and it is why D100 exists: **phase exit criteria name only what that phase can deliver.** A gate that demands a later phase's output is a cycle no amount of effort breaks.

---

## 7. How to read this document set

**Ninety-two documents:** `PARTITION.md` at the root of `Code/implementation/`, plus ninety-one markdown files across four directories — `master/` (11), `protocol/` (13), `manual/` (13), `lanes/` (54). This section is the **authoritative index**: if a document in this set exists at a path not listed here, it is not part of the plan until L0 adds a row. Paths are relative to `Code/implementation/`.

Several files in the tree are **not** plan documents and no task reads them; this section names the ones seen so far, not a closed set — a file not indexed in §7.2 stays out of scope by that omission alone: `_STATUS.txt` (generation-progress counter for the authoring run), `_DAMAGE.md` and `_INTEGRITY.md` (repair-run bookkeeping), `lanes/l1all.tmp` (an authoring scratch file), `protocol/00-dispatch-model.md` and `protocol/README.md` (front matter, not rows in the §7.2 protocol index), `protocol/_98-DEEP-REVIEW.md` and `manual/_98-DEEP-REVIEW.md` (the same underscore-prefixed bookkeeping convention as `_DAMAGE.md`/`_INTEGRITY.md`), and in `lanes/`: `L0-CONCORDANCE.md`, `L1-CONCORDANCE.md`, `L1-98-DEEP-REVIEW.md`, `L2-CONCORDANCE.md`, `L2-98-DEEP-REVIEW.md`, `L3-CONCORDANCE.md`, `L4-CONCORDANCE.md`, `L4-98-DEEP-REVIEW.md`, `L4-04-metric-register.md` (self-labeled "SUPERSEDED DRAFT" in its own header), `L5-CONCORDANCE.md`, `L5-98-DEEP-REVIEW.md`, `_ALIASES.tsv` and `lane-paths.tsv`. Ignore all of these.

Nobody reads all ninety-two. §7.1 is the order for each reader; §7.2 is the complete list.

### 7.1 Read in this order

**Every reader, always, first — and it is short.**

| Order | Path | What it is | Owner |
|---|---|---|---|
| 1 | `PARTITION.md` | The FROZEN lane partition. Repositories, path ownership, the five anti-conflict rules, branch and merge model, AI-developer profile | L0 |
| 2 | `master/00-MASTER-PLAN.md` | **This file.** Scope, five-lane rationale, three tiers, the honest calendar, entry criteria, definition of done, this index | L0 |

**Then, if you are an AI developer executing one lane task** — and nothing outside this list; `manual/09-cost-and-context-discipline.md` binds how much you read.

| Order | Path | What it is | Read |
|---|---|---|---|
| 3 | `manual/00-README-FOR-AI-DEVELOPERS.md` | Which lane you are, what you own, the five rules that outrank everything, how a day works | In full. Two minutes |
| 4 | `manual/03-guardrails-and-stop-rules.md` | Prohibitions `P-1`…`P-8`, the eight STOP conditions `STOP-01`…`STOP-08`, the blocker template and how to file it. **Overrides your task card** | In full |
| 5 | `manual/04-anti-hallucination.md` | Every gate that stops you inventing a path, an identifier, a command flag or a passing test | In full |
| 6 | `manual/02-task-execution-protocol.md` | The twelve-step loop you run once per task, start to finish | In full — this is your loop |
| 7 | `manual/05-git-workflow.md` | Every git command you will run, in order, with expected output — including §14, the forbidden commands | In full |
| 8 | `master/09-glossary-and-conventions.md` | §2 identifiers, §4 branch naming, §5 commit format, §6 PR format, §7 blocker and CCR templates | Those sections |
| 9 | `lanes/L<N>-00-charter.md` | Your lane's charter: mandate, owned paths, consumption and publication contracts, STOP rules | In full |
| 10 | `lanes/L<N>-<nn>-<slug>.md` | **Your phase file, and only yours.** The task bodies you execute | Your phase only |
| 11 | `master/05-entry-exit-criteria.md` | §0, plus your lane's section — the entry conditions and the exit command for your phase | Those sections |
| 12 | `manual/06-pr-and-review.md`, `manual/10-quality-bar.md` | What a finished task looks like, before you open the PR | Before the PR |
| 13 | `manual/08-failure-playbook.md` | What to do when something has gone wrong, without deciding anything | Only when it has |

**Never read** another lane's charter, phase file, or source tree. Reading another lane's pack to "understand the interface" is PARTITION rule 4 violated in the reader — consume `contracts/**` or a published artifact.

**Then, if you are L0** — you are the only reader who reads the whole set. Order: `PARTITION.md` → this file → `master/01-lane-architecture.md` → `master/06-v1-scope.md` → `master/04-phase-map.md` → `master/02-branch-merge-model.md` → `master/03-conflict-prevention.md` → `lanes/L0-01-phase-0-contracts.md` (execute it) → `master/05-entry-exit-criteria.md` §0 and §2 → `protocol/00`, `protocol/05`, `protocol/06` → `master/08-progress-tracking.md` → `master/07-risk-register.md` → `lanes/L0-00-charter.md` (keep it open) → `protocol/07-rollback.md`. Everything else on demand. Before B-Day, also work `master/INDEX.md` §7 OPEN ITEMS to a resolution or a dated deferral.

### 7.2 The full index

**Master (`master/`)** — programme-level, L0-owned. Eleven files.

| Path | Contents |
|---|---|
| `master/00-MASTER-PLAN.md` | This file. Authority order; what is built and what is refused; the five-lane rationale; the three tiers; the honest calendar as Tracks M/B/O; entry criteria `EC-1`…`EC-15`; three definition-of-done levels; this index; the ten standing rules |
| `master/01-lane-architecture.md` | Why each lane boundary sits where it does. The 26-row path-ownership manifest; `CODEOWNERS` text; the lane-guard reference implementation; the eighteen cross-lane contract surfaces `C1`–`C18` L0 must freeze, with producer and consumers; a full owns/consumes/publishes/must-not-break specification per lane; the boundary-reason register `B1`–`B18`. **This is the contract-surface inventory** |
| `master/02-branch-merge-model.md` | Git topology and branch lifetimes; naming; who may merge what; the merge train and the daily cycle; the lane-developer command reference `O-0`…`O-12`; rebase discipline; behind-lane recovery; conflict authority; the literal ruleset JSON for `CP-1`, `CP-2`, `CP-3`, `REC-1`, `REC-2`; negative tests `N-1`…`N-8` |
| `master/03-conflict-prevention.md` | The mechanical guarantee that five branches cannot collide. `.github/lane-ownership.map`; the complete `lane-guard.yml` workflow (rules `R1`–`R5`); the local pre-push mirror; the append-only and generated-artifact maps; **the Contract Change Request procedure and issue form (§4)**; the additive-only ladder; a worked example that reproduces a conflict and then prevents it |
| `master/04-phase-map.md` | One timeline. The two clocks — Build track `BT-0`…`BT-4`, Onboarding track `OT-P4`…`OT-P7`; the phase grid by lane; the critical path; the sync points `S0`–`S4` and what "clean" means as commands; calendar-gated items nothing compresses; what is genuinely concurrent versus what only looks concurrent |
| `master/05-entry-exit-criteria.md` | The largest master file. Per lane phase: entry conditions, exit criteria, and the exact command that proves exit, each printing `PASS <id>` or `FAIL <id>`. Universal entry gate `UEG-1`…`UEG-5` and universal exit gate `UXG-1`…`UXG-4`; L0's `L0-P0` and the per-cycle `G-INT`; spec-phase gates `G-F1`…`G-F7`, `G-G1`, `G-G2`; then `L1-P1`…`L5-P5`; the AT coverage map for all 110 tests |
| `master/06-v1-scope.md` | What the first release contains and what it does not. The nine §99.4 V1 items and the six residuals `R-1`…`R-6`; the build track by subsystem and complexity band; the V1 invariant floor and acceptance-test set; the deferred register with the trigger that un-defers each item; `contracts/v1-scope.yaml` and the one-command scope lookup; the V1 exit gate |
| `master/07-risk-register.md` | Risks to *building* the system, not to running it. Register A (`BR-01`…`BR-13`, the spec's own §99.6 risks, scored); Register B (`AX-01`…`AX-17`, the risks that exist only because five agents build at once — silent divergence, hallucinated paths, fabricated citations, lane-guard evasion, unowned surfaces); detection commands `A1`…`A11` and `B1`…`B17`; the lane STOP-rule block |
| `master/08-progress-tracking.md` | How L0 knows where the programme is, given that **a lane never reports status — status is derived from git**. The task ledger under `docs/plan/`; the nine derived status values; the daily integration report `R1`–`R9`; the five burn-downs and their spec-derived denominators; the blocked-task procedure; STOP-AND-REPLAN signals; the instrument's own seeded canary |
| `master/09-glossary-and-conventions.md` | The house style, mechanised, so five agents produce code that reads as one author's. Vocabulary; identifier spaces and how to verify one before writing it; the task-id scheme; branch naming; commit format and its `commit-msg` hook; PR format; **the blocker and CCR templates (§7)**; repository layout; file naming; YAML and JSON Schema conventions |
| `master/INDEX.md` | The navigational map of the whole set, with per-audience reading orders and — in §7 — every contradiction (`C-1`…`C-26`), dangling reference (`R-1`…`R-12`) and gap (`G-1`…`G-11`) found by a full cross-read. It settles nothing; it lists what L0 must settle |

**Protocol (`protocol/`)** — how the five lanes coexist and how the work is proven. L0-owned; every lane reads the ones its tasks invoke. Thirteen files.

| Path | Contents |
|---|---|
| `protocol/00-test-strategy.md` | The verification pyramid `T0`–`T4` for a five-lane parallel build: what is tested, where it runs, when, who owns it, what it blocks, and the exit-code contract. The one idea it enforces: *a check that can only pass is not a check.* Read before any other protocol file |
| `protocol/01-contract-tests.md` | The tests that catch two lanes diverging on a shared concept — the mechanical backstop behind PARTITION rule 2. Governs `contracts/**`, `contracts/fixtures/**` and `contracts/harness/**`, none of which a lane may edit |
| `protocol/02-acceptance-mapping.md` | Every one of the 110 acceptance tests `AT-001`…`AT-110` mapped to the lane that implements what it exercises, the phase at which it can *first* run, and whether it is automatable or needs a human step. **This is the acceptance-test reference for `make at AT=<id>` and `make at-suite TIER=<t>`, and for the `UNARMED` arming discipline of §6.4** |
| `protocol/03-invariant-tests.md` | The enforcement test suite for Section 101: how each of the 111 invariants is proven enforceable, with executable fixtures, and how the mechanical / policy / review-held classification is itself made checkable |
| `protocol/04-negative-tests.md` | The negative-test catalogue. Every test performs a forbidden action and asserts the system refused. A gate verified only positively reads armed and is not; this file is the executed proof for every such gate |
| `protocol/05-merge-gate.md` | The two gates and nothing else merges anywhere: **GATE A** (`LG-01`…`LG-12`) for a lane PR into `integration`, **GATE B** (`IG-01`…`IG-12`) for `integration` into `main` |
| `protocol/06-integration-cycle.md` | The merge train as a procedure: cycle open, slot by slot in the order L1 → L4 → L2 → L3 → L5, promotion, cycle close |
| `protocol/07-rollback.md` | Recovery of the *build* — lane branches, `integration`, `main`, in both repositories. Not production rollback. A lane executes only §R3 (its own branch) and §R5.3 (re-landing its own reverted work); it never reverts `integration` |
| `protocol/08-smoke-and-e2e.md` | End-to-end verification that the five lanes built the *same* system, run at every `integration` → `main` promotion and once as the V1 exit gate |
| `protocol/09-fixtures.md` | Fixtures and test data: where they live, who authors them, how a lane consumes another lane's fixtures without touching its source tree, and the `FG-1`…`FG-5` meta-gates |
| `protocol/10-ci-pipeline.md` | The CI pipeline **for the build itself** — the workflows that run on `lane/N/*`, on `integration` and on `main` during the five-lane build. Deliberately distinct from the reusable workflow library L2 ships as a product; conflating the two is the most expensive documentation error available |
| `protocol/11-definition-of-done.md` | Done at every level, as commands: per task, per phase, per lane, per tier. The protocol-side counterpart to §6 of this file |
| `protocol/99-WALKTHROUGH.md` | Diagnostic, not normative. Walks protocol `00`–`11` end to end on paper — once for a task that goes right, three times for tasks that go wrong — and records where the walk falls through. Routes what it finds to L0; picks no winners |

**Manual (`manual/`)** — the AI developer's operating manual. This is what a lane agent is actually given. Thirteen files — `00`–`11`, plus the `99` hardening review.

| Path | Contents |
|---|---|
| `manual/00-README-FOR-AI-DEVELOPERS.md` | **Read first, before any action.** Two minutes: which lane you are, what you own, the five rules that matter more than everything else, how a day works |
| `manual/01-lane-system-prompts.md` | Five complete, verbatim copy-pasteable system prompts, one per lane. Production artefacts, not examples — the literal text an agent is started with |
| `manual/02-task-execution-protocol.md` | One task end to end: the twelve-step loop, run once per task, in order, without skipping. Preconditions, branch, implement, self-verify, scope-check, commit, PR, handoff |
| `manual/03-guardrails-and-stop-rules.md` | The standing prohibitions `P-1`…`P-8`; the ownership guard to run before every commit; the eight stop conditions `STOP-01`…`STOP-08`; the blocker issue template, its required evidence per stop code, and how to file it; the stop procedure. **Overrides your task card wherever they disagree** |
| `manual/04-anti-hallucination.md` | Every rule that stops an agent inventing a path, an identifier, a command flag or a passing test. Gates, not advice |
| `manual/05-git-workflow.md` | Every git command you will ever run, in the order you run them, with the output you should see — plus §14, the forbidden commands. If a command you are about to type is not on that page, stop |
| `manual/06-pr-and-review.md` | PR construction and the review protocol; the four distinct events of §27; what a machine may never do in review |
| `manual/07-worked-example.md` | One real Lane 1 task — authoring the `people.yaml` registry schema — executed from hand-off to merge with nothing elided. Every command literal, every file shown in full, every **CAPTURED** output actually produced. Pattern-match against it instead of interpreting |
| `manual/08-failure-playbook.md` | What to do when something goes wrong, without deciding anything. The three laws, then a branch per failure mode |
| `manual/09-cost-and-context-discipline.md` | What you may read, how much, and when to stop reading. You do not explore, survey, or read the specification to get oriented; an insufficient task card is a stop, not a licence to read more |
| `manual/10-quality-bar.md` | What "done" means: a state proven with commands whose output you pasted. No `TODO`, no skeleton, no deferred content — and no quietly shrinking a five-part criterion into a one-part deliverable |
| `manual/11-onboarding-a-new-agent.md` | Handover as a procedure: an incoming agent taking over a running lane, an outgoing agent standing down, L0 running the swap, and every proposal to add a sixth agent |
| `manual/99-HARDENING.md` | Adversarial hardening review of `manual/00`…`manual/11` and `PARTITION.md`, read against a literal-minded low-cost agent: findings `A1`–`A20` on the five lane system prompts, `B1`–`B15` cross-file contradictions, `C1`–`C13` broken or exploitable commands, an end-to-end red-team walkthrough, `M1`–`M18` missing controls, and the fix sequence. **A findings document, not normative** — no lane executes it; L0 applies the tightened wording, and until it does the file it names still governs |

**Lanes (`lanes/`)** — the task packs. Fifty-four files, nine per lane, on one fixed shape: `-00` is the charter, `-01`…`-07` are phase and task content, `-99` is the coherence review. **A lane developer opens the nine files of its own lane and no others** — and within those, its charter plus its current phase file.

*Lane summary and Track B milestones:*

| Lane | Files | Subsystems | Track B milestones it delivers |
|---|---|---|---|
| **L0** Integrator (human lead) | `lanes/L0-00` … `L0-07`, `L0-99` | — | B0, and the merge train and integration gate throughout |
| **L1** Registries & Contracts | `lanes/L1-00` … `L1-07`, `L1-99` | A, B | B1 |
| **L2** Pipeline & Evidence | `lanes/L2-00` … `L2-07`, `L2-99` | E, F | B2, B7 |
| **L3** Reconciler & Provisioning | `lanes/L3-00` … `L3-07`, `L3-99` | C, D | B3, B4 |
| **L4** Records, Events & Metrics | `lanes/L4-00` … `L4-07`, `L4-99` | I, N | B5 |
| **L5** Access, Infra & Ops | `lanes/L5-00` … `L5-07`, `L5-99` | K, L, M, Q, R | B6 |

**L0 — Integrator.** Executor is the human lead for every file except `L0-07`; no AI developer runs `L0-00` through `L0-06`.

| Path | Contents |
|---|---|
| `lanes/L0-00-charter.md` | The integrator's standing charter: what L0 owns, the authority boundary, the seven §99.3 design-open items reserved to L0, the L0-only decision register, the decisions lanes are **forbidden** to make, the escalation protocol (§7), the cadence, the merge train in five lines, and L0's own tasks |
| `lanes/L0-01-phase-0-contracts.md` | **Phase 0: authoring and freezing `contracts/**` before any lane starts.** The contract register, every Phase 0 task, the stub-and-fixture guarantee, what "frozen" means exactly, the task index and dependency graph, and **the Contract Change Request procedure (§8)**. Nothing else in the programme starts until this file completes |
| `lanes/L0-02-lane-guard.md` | The production lane-guard: the ownership map, the CI check, generated `CODEOWNERS` with human identities only, and what a foreign-path PR failure looks like. The charter stands up the first cut; this file is the version that ships |
| `lanes/L0-03-merge-train.md` | The merge train as an operational procedure — the charter's five lines turned into literal commands, failure branches and records, slot by slot |
| `lanes/L0-04-decisions-register.md` | **The single decision register for the whole set.** Sixty entries `REG-001`…`REG-060`; the concordance mapping 188 source ids across every file (including `D-PLAN-01`, `D-PLAN-02`) to their `REG-nnn`; how a lane looks one up in three commands (§4.1); what a lane may never do with it (§4.3); the file format (§7). On disk: `docs/decisions/register.tsv`, `concordance.tsv`, `open/REG-nnn.md`, `closed/REG-nnn.yaml` |
| `lanes/L0-05-integration-gate.md` | The `integration` → `main` gate built: what `protocol/05-merge-gate.md` §4 (`IG-01`…`IG-12`) and `protocol/00-test-strategy.md` §5 (T3) specify, made executable |
| `lanes/L0-06-bootstrap-mode.md` | Bootstrap Mode operation, executed by the human lead acting as Founder: opening and closing every bootstrap exception with expiry, owner and deactivation trigger; the §95.4 activation checklist; the weekly log |
| `lanes/L0-07-onboarding-track.md` | **The per-product Track O runbook**, and the one L0 file an AI developer executes (privileged steps are marked **HUMAN STEP** — record and verify the evidence, never perform the step). The relative clock made mechanical; the DevOps serialiser; **the universal floor — nine items × every live product, 72 obligations (§5)**; the S1–S19 intake taxonomy and the path from each (§6); the intake gap assessment (§7); the QA-takeover SLA (§8); the interim rule (§9); the per-product sequencing plan for eight products (§10) |
| `lanes/L0-99-review.md` | Coherence review of the eight L0 files (19,450 lines, 103 tasks) against `PARTITION.md` and the spec |

**L1 — Registries & Contracts** (A, B). Owns `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`. Merges **first**.

| Path | Contents |
|---|---|
| `lanes/L1-00-charter.md` | Lane mandate, owned paths, subsystem and spec coverage, consumption and publication contracts, merge-train obligations, lane DoD, STOP rules |
| `lanes/L1-01-repo-skeleton.md` | Phase 1: the `control-plane` repository skeleton, with effective dating and append-only discipline from the first commit — retrofitting history is impossible by definition |
| `lanes/L1-02-schemas.md` | Phase 2: the JSON Schema suite for every registry and product contract |
| `lanes/L1-03-validators.md` | Phase 3: the validator suite — multi-version validation, referential integrity, date rules, and the blocking rejections (24×7 without rota, commitments conflict, exception without expiry, unclassified control) |
| `lanes/L1-04-ci-gate-engine.md` | Phase 4: the CI gate engine, the `gate-rule.v1` schema, and the seeded canary under `registries/canary/**` |
| `lanes/L1-05-tasks.md` | The complete ordered atomic task list for Lane 1. Work it top to bottom; every task is executable without opening another document |
| `lanes/L1-06-tests.md` | Lane 1 test strategy — every test file lands under `validators/registry/tests/**` |
| `lanes/L1-07-runbook.md` | The Lane 1 daily runbook. A script, not advice: every branch point ends in a command or in a STOP |
| `lanes/L1-99-review.md` | Coherence review of the eight L1 files (12,213 lines) against `PARTITION.md` and the spec |

**L2 — Pipeline & Evidence** (E, F). Owns `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`. Merges third.

| Path | Contents |
|---|---|
| `lanes/L2-00-charter.md` | Lane mandate, owned paths, subsystem and spec coverage, consumption and publication contracts, merge-train obligations, STOP rules `S1`–`S5`, the blocker template, and the task-id ranges reserved per subsystem |
| `lanes/L2-01-reusable-workflows.md` | Phase 1: the reusable workflow library v1, consumable by pinned tag — `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue` |
| `lanes/L2-02-digest-invariant.md` | Phase 2: the digest invariant and the artifact chain, enforced in code |
| `lanes/L2-03-production-gates.md` | Phase 3: production approval and isolation — the explicit approval event, environment protection, the Friday-freeze time gate |
| `lanes/L2-04-evidence-chain.md` | Phase 4: subsystem F, the evidence chain store and query — eleven-question answerability for any production artifact, `/version` digest-match monitoring, the `verify-digest-chain` sweep, append-only history with effective dating |
| `lanes/L2-05-tasks.md` | The complete ordered atomic task list for Lane 2 — 76 tasks, each executable without opening another document |
| `lanes/L2-06-tests.md` | Lane 2 test strategy; everything it creates lands under `tools/evidence/**` and `.github/workflows/**` |
| `lanes/L2-07-runbook.md` | The Lane 2 daily runbook. Every branch point ends in a command or in a STOP |
| `lanes/L2-99-review.md` | Coherence review of the eight L2 files (19,918 lines) against `PARTITION.md` and the spec |

**L3 — Reconciler & Provisioning** (C, D). Owns `reconciler/**`, `tools/provision/**`, `validators/drift/**`. Merges fourth.

| Path | Contents |
|---|---|
| `lanes/L3-00-charter.md` | Lane mandate, owned paths, subsystem and spec coverage, publication contracts, merge-train obligations, STOP rules |
| `lanes/L3-01-diff-engine.md` | Phase 1: the read-only declared-versus-actual diff engine — every row of §53.1, per-registry comparison counts, run-integrity rules, and the schema validator that proves a run record well-formed |
| `lanes/L3-02-levels-and-repair.md` | Phase 2: the five response levels and auto-repair. Phase 1 must be merged before any task here starts |
| `lanes/L3-03-canary-and-integrity.md` | Phase 3: instrument integrity — the seeded canary, and the rule that a zero-finding run is a **failed** run. No task in this phase enables a new repair class; every new path is a detector, a recorder, or a gate that fails closed |
| `lanes/L3-04-provisioning.md` | Phase 4: subsystem D — `create-product` and `add-person` generating repository, Teams, `CODEOWNERS`, branch protection and registry entries with zero hand-editing |
| `lanes/L3-05-orphans.md` | Phase 5: orphan and expiry detection. Writes nothing outside `reconciler/` |
| `lanes/L3-06-tasks.md` | The complete ordered atomic task list for Lane 3, under the standing rule that auto-repair is the most dangerous code in the system |
| `lanes/L3-07-tests-and-runbook.md` | Lane 3 test harness, fixture organisation, every test case, the phase-gated live-organisation procedure, and the Lane 3 daily runbook |
| `lanes/L3-99-review.md` | Coherence review of the eight L3 files against `PARTITION.md` and the spec, with the per-file task census |

**L4 — Records, Events & Metrics** (I, N). Owns **all of `control-plane-records`**, plus `schemas/records/**`, `metrics/**`, `tools/records/**`. Merges second.

| Path | Contents |
|---|---|
| `lanes/L4-00-charter.md` | Lane mandate, the two-repository owned-path list, subsystem and spec coverage, consumption and publication contracts, merge-train obligations, lane decisions and standing rules |
| `lanes/L4-01-records-repo.md` | Phase 1: standing up `control-plane-records` — the directory-per-item convention, the D107 no-bypass ruleset, commit signing, and the `records-writer` GitHub App (D89) |
| `lanes/L4-02-record-schemas.md` | Phase 2: the record and event schemas, including the D103 event envelope (`L4-T201`…`L4-T225`) |
| `lanes/L4-03-write-paths.md` | Phase 3: how records actually get written — the write paths, one file per record, never a concurrent append to a shared period file |
| `lanes/L4-04-attention-ledger.md` | Phase 4: the attention ledger, its duration rule, and the metrics derived from it (`L4-T401`…`L4-T418`) |
| `lanes/L4-05-pipeline-and-boards.md` | Phase 5: the ingest half of subsystem I (DevLake, Prometheus, Scorecard) and the board / horizon / Ready half of subsystem N |
| `lanes/L4-06-tasks.md` | The complete ordered atomic task list for Lane 4, executable from that file alone |
| `lanes/L4-07-tests-and-runbook.md` | Lane 4 test strategy — fixture corpora, round-trip, negative, derivation and acceptance proofs — plus the daily runbook for a lane that works across two repositories. Every L4 artifact is an instrument, and this phase makes each one prove it can fail |
| `lanes/L4-99-review.md` | Coherence review of the eight L4 files against `PARTITION.md` and the spec |

**L5 — Access, Infra & Ops** (K, L, M, Q, R). Owns `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`. Merges last.

| Path | Contents |
|---|---|
| `lanes/L5-00-charter.md` | Lane mandate, path ownership, subsystem mapping, spec coverage map, consumption and publication contracts, merge-train obligations, the lane DoD, and the task-authoring contract binding every other `L5-*` file |
| `lanes/L5-01-org-and-access.md` | Phase 1: the GitHub organisation and access model — org base Read, Teams-derived Write, branch and environment protection, the deployment branch and tag policy, the §95.2 bootstrap arming pattern. Writes `access/**` only |
| `lanes/L5-02-secrets-and-boundaries.md` | Phase 2: the five secret tiers and the trust boundaries. Fourteen mechanical tasks; every value that would need judgement is read from a frozen L0 input file |
| `lanes/L5-03-layer-b.md` | Phase 3: the Layer B split — the second, Founder-only Grafana instance per §99.5 and D75, and the provisioning that makes AT-097 executable against it |
| `lanes/L5-04-ops-vm.md` | Phase 4: the operations VM and the estate. Where output must land in a foreign path, the task ends in a handoff issue, never an edit |
| `lanes/L5-05-assets-ai-notify.md` | Phase 5: subsystem Q (asset inventory and deadline watch), subsystem K (AI runtime contract enforcement) and subsystem R (notification routing) |
| `lanes/L5-06-tasks.md` | The complete ordered atomic task list for Lane 5. Work it top to bottom; do not skip a task whose dependencies are unmet |
| `lanes/L5-07-tests-and-runbook.md` | Lane 5 test strategy and daily runbook, including the **ASSISTED** and **HUMAN-GATED** markings for steps a named human executes |
| `lanes/L5-99-review.md` | Coherence review of the eight L5 files (17,000 lines) against `PARTITION.md` and the spec |

**If L0 adds a lane file**, it matches the glob `lanes/L<N>-<nn>-<slug>.md` and gets a row in the lane table above before its first task is issued.

### 7.3 The one-paragraph version, for someone who reads only this

A nine-person company running eight products is building a GitOps operating system for itself: YAML registries in a control-plane repository, validators that gate CI, a reconciler that diffs declared state against GitHub and blocks drift, a provisioning CLI that creates a product with zero hand-editing, a reusable workflow library consumed by pinned tag, a metrics layer, and Grafana dashboards provisioned from JSON in git. Five AI developers build it in parallel on five branches whose paths never overlap, merging in a fixed dependency order through one human integrator. The build takes **8 to 22 build-elapsed weeks** on its critical path — not the three weeks the spec's phase labels suggest, because D99 corrected those labels into a build track dated by subsystem complexity and an onboarding track dated relative to it. Onboarding the eight live products then runs three to four weeks each, highest-reliability-criticality first, roughly two quarters. Governance instrumentation follows, and cannot be rushed: pattern detection needs two quarters of history, forecasting two quarters of attention data. It is done when all 110 acceptance tests pass by configuration alone, all 111 invariants carry a live enforcement classification, and no test required redesigning the architecture to pass.

---

## 8. Standing rules for every lane developer

These override any instinct, on every task, in every lane.

1. **Never edit a path your lane does not own.** One owner per path; the lane-guard check fails you; there are no exceptions.
2. **Never edit `contracts/**`.** File a Contract Change Request — the procedure and issue form are `master/03-conflict-prevention.md` §4; what L0 does with it is `lanes/L0-01-phase-0-contracts.md` §8; the template you fill in is `master/09-glossary-and-conventions.md` §7.
3. **Never append to a shared index, list, or registry-of-everything.** Directory-per-item only: one file per event, per record, per schema.
4. **Never reach into another lane's source tree.** Consume `contracts/**` or a published artifact.
5. **Prefer a new file over editing an existing one**, and only inside your owned paths.
6. **Never invent a spec section number, an AT- id, an invariant number, a SIG- id or a D- id.** If a task cites one you cannot find in the spec, that is a STOP.
7. **Never make a design decision.** Section 99.3 lists seven design-open matters — the attention classifier and constraint-diagnosis algorithm; the `make parity` declaration format; plan-checker internals; DevLake field coverage; machine sources for context checks; KPI instrumentation projects; calibration methods. Every one belongs to L0. If your task requires you to choose, you have the wrong task: STOP and open a blocker.
8. **Never relax a control.** Auto-repair may only move the system toward the declared, stricter state (invariant 81; AT-033). A reconciler presented with a stricter-than-declared production control raises it for human review and does not relax it.
9. **A reconciliation run that finds nothing is assumed broken, never assumed clean** (AT-102). Build the seeded canary before you build the finding.
10. **Every task you finish must be provable by one command whose output is unambiguous.** If you cannot state that command, the task is not finished.

---

## 9. Open L0 decisions carried by this file

| ID | Decision | Blocks | Latest resolution point |
|---|---|---|---|
| D-PLAN-01 | Owning lane and path for Subsystem H (dashboards and views), including the Layer B Founder-only instance's provisioning | Founder view v0 (Section 99.4 item 7); AT-097 executability | **before B-Day** |
| D-PLAN-02 | Subsystem G (plan-checker): configuration-only, in-house build with a partition amendment, or Phase 7 recorded `declined` | Onboarding phase O-7 for every product | before O-7 is scheduled for the first product; the verification run itself is EC-9, before B-Day |
| D-PLAN-03 | The published point estimate inside the 8–22 build-elapsed-week Track B band, with its reasoning | Pre-onboarding deadlines (Section 96.2), which D99 requires be set from the Onboarding track | **before B-Day**, and re-published after each merge-train cycle |
| D-PLAN-04 | Partition amendment assigning Subsystem P (people intelligence engine) a lane and paths | People tier P1 onward | before the People tier starts; **not before** — Section 99.4 item 9 defers it in sequence, never unscheduled |

**Where these are recorded.** The single decision register for the whole set is built by `lanes/L0-04-decisions-register.md`. Its §3 is the register itself, its §5 the concordance that resolves every source id — including the `D-PLAN-nn` ids above — to a `REG-nnn` entry, and its §7 the file format. On disk: `docs/decisions/register.tsv` (one row per decision), `docs/decisions/concordance.tsv` (source id → `REG-nnn`), `docs/decisions/open/REG-nnn.md` (the open statement), `docs/decisions/closed/REG-nnn.yaml` (the dated closure). All four are L0-owned under `docs/**`.

| ID raised here | Register entry | Where to read it |
|---|---|---|
| D-PLAN-01 | **REG-001** — *"Subsystems G H J O and P are assigned to no lane"* | `docs/decisions/open/REG-001.md`; concordance row in `lanes/L0-04-decisions-register.md` §5 |
| D-PLAN-02 | **REG-001** (same entry; G is one of its five subsystems, and option C there is this file's option C) | as above |
| D-PLAN-03 | not yet carried by the register — admitted under `lanes/L0-04-decisions-register.md` §6, then read at its allocated `REG-nnn` | `docs/decisions/register.tsv` |
| D-PLAN-04 | **REG-001** (subsystem P is named in that row) | `docs/decisions/open/REG-001.md` |

**How a lane looks one up**, in three commands, is `lanes/L0-04-decisions-register.md` §4.1: resolve the source id against `docs/decisions/concordance.tsv`, read `docs/decisions/open/REG-nnn.md`, then confirm the `state` field in `docs/decisions/register.tsv`. If `state` reads `open`, the decision is not made and **the task STOPs**. If it reads `closed`, the row's `record` field names the decision record carrying the answer — read that record, not the register. A lane never edits anything under `docs/decisions/**` (§4.3 of that file). An unresolved decision is never resolved by a lane.
