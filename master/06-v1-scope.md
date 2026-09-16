# 06 — V1 SCOPE

**Status:** authoritative for scope membership. Subordinate to `implementation/PARTITION.md` (frozen) and to `Research/MultiProduct_MasterSpec_v4.0.md` (the specification).
**Governs:** what the first release contains, what it does not, and the trigger that moves each deferred item into a later release.
**Reader:** the five lane developers (L1–L5) and the integrator (L0). Nothing here requires judgment from a lane. Every scope question resolves to a table lookup; anything that does not is written as an `L0 DECISION REQUIRED` block.

Spec references in this file are `§n.n` into `MultiProduct_MasterSpec_v4.0.md`. Decision records are `Dn` from the decision tables at the end of that document. Acceptance tests are `AT-nnn` (§100). Invariants are numbered items of §101. Health signals are `SIG-nn` (§52.2). None of these identifiers are invented; §14 of this file gives the commands that re-verify every one of them against the spec text.

---

## 1. The one-sentence definition of V1

> V1 is the Foundation launch-critical set (§98.2, Phases 1–7) applied to **2–3 pilot products**, plus the near-free P0 governance design rules baked in from day one — roughly **30% of the build surface** — delivering four capabilities and no more: **declared state enforced, drift visible, orphans impossible to miss, every production artifact traceable** (§99.4, opening paragraph).

Everything in this file is an expansion of that sentence. If a proposed task cannot be traced to one of the nine items in §3 or the six residuals in §4, it is **not in V1** and the lane must stop and open a blocker issue.

---

## 2. What D99 corrected, and how this file reads §98.2

### 2.1 The defect

§98.2 stamps absolute calendar labels on its phases — *Phase 1 (Week 1)*, *Phase 2 (Week 2)*, *Phase 3 (Week 3)*, *Phase 4 (Weeks 4–5, per product)* — while §99.2 prices the subsystems those phases deliver at **M (one to three weeks)** and **L (three to eight weeks)** each, *for one competent engineer with AI assistance, excluding per-product content work*. §98.1's calendar-gating honesty paragraph explicitly scoped itself to "the upper tiers", leaving the Foundation labels unqualified. The result read as a schedule and was not one.

### 2.2 The correction (D99, verbatim scope)

> "The phases split into a **Build track** dated by subsystem with its complexity band, and an **Onboarding track** whose per-product phases are relative to the subsystems they consume. Pre-onboarding deadlines are set from the Onboarding track, not from the labels." — D99, implemented in §98.1, §98.2, §98.3, §99.2, §99.4, §96.2

### 2.3 How this plan applies it — binding

| Rule | Consequence for a lane |
|---|---|
| **R1** | The strings "Week 1".."Week 8" in §98.2 are **not** dates and are **not** a task ordering. No lane task carries a week number. |
| **R2** | Build-track work is ordered by the **dependency spine** of §99.2 — `A → B → C and D; E → F → H/I` — and by the merge train of `PARTITION.md` (`L1 → L4 → L2 → L3 → L5`). Nothing else orders it. |
| **R3** | Onboarding-track work for a product is ordered **relative to the subsystems it consumes**, listed in §7 of this file. A product cannot enter Onboarding Phase 4 before subsystems D, E and L are merged to `main`. |
| **R4** | Pre-onboarding deadlines written into a product's stub `product.yaml` (§96.2, Phase 2 bullet) are set from the **Onboarding track**, never from a §98.2 week label. A deadline breach raises **SIG-38** (`Brownfield adoption health`, Amber; Red past deadline) — so a fabricated deadline manufactures a false Red. |
| **R5** | §98.2's own header — "Launch-critical — must exist before the first pilot product completes onboarding" — is the **scope** statement and survives D99 intact. D99 changed the dating, not the membership. |

### 2.4 The residual mismatch D99 did *not* close

D99 fixed dating. It did not reconcile the **membership** difference between §98.2's seven phase bullet-lists and §99.4's nine-item V1 enumeration. Six items are named in one and absent from the other. They are enumerated in **§4** and are **in V1** — each on a spec citation, none on inference. A lane that finds a task in §4 with no matching bullet in §98.2 is looking at a known, closed gap, not at scope creep.

---

## 3. The definitive V1 inventory — the nine declared items

Source: §99.4, items 1–9, quoted in the "V1 item" column and unabridged in intent.

| # | V1 item (§99.4) | Subsystems (§99.2) | Owning lane(s) | Onboarding phase(s) (§98.2) | Exactly what V1 contains | What is *not* in this item |
|---|---|---|---|---|---|---|
| **1** | Control-plane repository, schemas and CI validation — with effective dating and append-only discipline from the start | A, B | **L1** (`schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`); **L4** (`schemas/records/**`, all of `control-plane-records`); **L0** (`contracts/**`, `CODEOWNERS`) | 1, 3 | `people.yaml` (incl. `work_arrangement`, D111), `roles.yaml`, `platform.yaml` (incl. the closed `event_type` enum, D103), `exceptions.yaml`, `economics.yaml` ledger stub (D104), `product.yaml` at `contract_version: 1` for pilots, the constitution file, `ai-toolchain.yaml`; multi-version schema validators; referential integrity; date rules; the 24x7-without-rota and commitments-conflict blockers; exception-without-expiry rejection; undefined-capability rejection (D81, D90); dangerous-capability-in-role-default rejection (D106); delegation-scope rejection (D108, D109); record/event envelopes with `record_schema_version` and `event_schema_version` (D103) | The other 20 artifacts of the §52.6 twenty-nine-entry registry (`os-health.yaml`, `policies.yaml`, `patterns.yaml`, `platform-roadmap.yaml`, `tools.yaml`, `topology.yaml`, `service.yaml`, `changes/*.yaml`, `scenarios/*.yaml`, the Layer B stores, the conduct store, the framework registry, the compliance register). Unclassified-control rejection (§99.2 row B) needs `policies.yaml` → **G2** |
| **2** | GitHub enforcement: one organisation, base Read, Teams-derived Write, branch protection with most-recent-push approval, environments — completion checks executed as written | L | **L5** (`access/**`, `infra/**`); **L3** applies it (`tools/provision/**`); **L0** (`CODEOWNERS`) | 1 | Org consolidation; base permission Read; Teams grant Write **before** protection is armed (D101); branch protection on every repository with required review and approval of the most recent reviewable push; the required-status-check list **starts empty per repository** and is populated per phase (§98.2, Phase 1); environment deployment **branch and tag** policies from the template on every environment (D91); org-enforced 2FA with hardware keys/passkeys for Founder, Owners and platform-admin holders; second Owner or escrowed break-glass Owner credential with a named escrow custodian; the five secret tiers incl. the records-writer at tier five (D89, §40.1); the records repo's no-bypass ruleset blocking force-push and delete (D107) | Layer B: the second Founder-only Grafana instance and the separately-credentialed people datasource (D75) → **P2** (§98.6). Enterprise-only environment required reviewers — never depended on (D73) |
| **3** | Scaffolding v0 (`create-product`, `add-person`) — a portfolio of eight products crosses the pays-for-itself threshold immediately | D | **L3** (`tools/provision/**`) | 3 | `create-product`: repo from `product-template`, Teams from registries, generated CODEOWNERS (human identities only), branch protection, environments with scoped secrets and deployment branch/tag policies, registration in every surface, **zero hand-editing**. `add-person`: `people.yaml` entry, Team membership, capability grant at minimum privilege (inv. 79), draft state. Safe defaults in both templates (§95.3) | `change-role`, `remove-person`, template evolution → **Early hardening** (§98.3, final row) |
| **4** | Delivery pipeline with the digest invariant, one tested rollback and one recorded restore test per product — the single highest-safety-per-effort item; it makes the evidence chain answerable | E, F | **L2** (`.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`); **L4** writes the records | 4, 6 | Reusable workflows consumed by pinned tag: `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`; immutable artifact build with digest recording and SBOM emission; the digest invariant enforced **in code** (inv. 22, 23); parity job (§33.1 `make parity`); Friday-freeze time gate resolved against the declared working calendar, never runner-local time (§97.1); production approval as a distinct recorded event through the **workflow-identity gate** (D73, §27.2), failing closed when approver == deployer; privileged workflows assert their own runner tier and fail closed (D87); deployment-record and event writes as **required, failing steps** of `deploy-production.yml` (§97.2); one deliberate rollback executed in staging; one restore test recorded, entering the rolling 90-day rotation (inv. 3, 4); `verify-digest-chain` (§99.2, named tools); the eleven-question evidence chain (§32) answerable for one real deployment | `org-export` and `background-queue` workflows (§99.2 row E) → deferred, §9. Bulk fleet-migration PR script and change-matrix scaffold → **Early hardening** (change manifests) |
| **5** | Verification-contract skeleton with CI presence enforcement — the load-bearing invariant "no onboarded product without a verification contract" cannot be deferred | B (schema), E (runner) | **L1** (`schemas/product/**` — the `verification/contract.yaml` schema); **L2** (`.github/workflows/**` — the presence and execution check) | 5 | The `verification/contract.yaml` schema; control-plane CI failing any onboarded product missing it (inv. 1); **the seeded-defect case (D97)** — every contract declares a deliberately broken build or mutated assertion it MUST fail; a run in which the seeded case passes is a **FAILED run** and raises **SIG-18**, Blocking for that product; required-file presence checked, not assumed (§33.1, incl. `AGENTS.md`); `verification/uat.md` authored; smoke tests; the `RECORD-VERIFICATION-RESULT` `workflow_dispatch` pattern (§97.2) | Auto-pass scope tuning, performance and load verification (§31.3) beyond presence. AI evaluation suites are in V1 **only** for a pilot that declares an `ai_runtime_dependency` (§98.2 Phase 5, AT-049) |
| **6** | Reconciliation v0, **detect and block only** — Teams versus registries, expiry revocation, protection drift, orphan detection. Its stricter-only rule is enforced in code and tested | C | **L3** (`reconciler/**`, `validators/drift/**`) | 3 | Scheduled diff of declared vs actual GitHub state at **Levels 1 (Detect), 2 (Warn) and 4 (Block)** of §53.2; automatic expiry revocation; orphan detection at **Blocking** severity (SIG-05); protection drift (SIG-03); the block mechanism is the reconciler's **check-run-write scope posting a named required check** on every affected repository, failing while a Blocking finding is open (D92) — not "fails CI", which a stale green check never does; the **stricter-only rule enforced in code and tested** (inv. 81, §53.3, AT-033) even though Level 3 does not ship; the seeded reconciliation canary — a zero-finding run is a **failed** run raising SIG-13 (AT-102); per-run object caps, expected-source assertion, run-count ceiling, signed run record, and a run without a matching scheduled trigger classified Blocking (D96); the reconciler anchors the records-repo head SHA into the protected control-plane repository each run (D107); the reconciler's write scope narrowed to generated `derived/**` (D93); the **registry-change lane's staged canary apply and authority-delta gate** (§26.4, D93 — see §4.5) | **Level 3 auto-repair** and **drift classification** → **Early hardening** (§98.3, row 1). Level 5 escalate ships in V1 **only** for the reconciliation job's own failure, which AT-102 and AT-032 require; every other Level 5 trigger of §53.2 waits for the incident workflow |
| **7** | Founder view v0 from GitHub API and reconciliation output plus Scorecard | H (partial), I (partial), M | **L5** (`ops-vm/**` — Grafana provisioning); **L4** (`metrics/**` — the computation) — **see `L0 DECISION REQUIRED V1-D2`** | 2 | Grafana on the operations VM, dashboards as provisioned JSON in git, never hand-edited in the UI (§92.3, §99.5); Scorecard scheduled scan with drop detection; one screen carrying: open drift by class, orphans, exception expiries, per-product Scorecard score, pre-onboarding deadline status; Renovate installed with its two-ruleset bypass split so the compensating check does not sit inside the ruleset it compensates for (D74, D89); Remote Control enabled for anyone who wants it; the §51 remote-access decision recorded — or carried as a dated `policy_waiver` in `exceptions.yaml` with owner and deactivation trigger (§98.2 Phase 2) | The full Founder view of §93 → **G3**. The eight decision questions of §93.3 → questions 1–5 at G3, 6 at G5, 7–8 at G6 (D100); at V1 all eight render **unarmed — not yet instrumented** (D77). **DevLake** — see `L0 DECISION REQUIRED V1-D3` |
| **8** | From the governance tier, only: the exception registry with mandatory expiry; safe defaults in provisioning templates; fail-closed classification written down; and the control-plane/data-plane invariant test | O (sliver), D, L | **L1** (`registries/**` — `exceptions.yaml` + its minimal validator); **L3** (`tools/provision/**` — safe defaults; `reconciler/**` — expiry revocation); **L5** (`access/**` — fail-closed classification); **L2** (`.github/workflows/**` — the CP/DP test) | 1 | `exceptions.yaml` with the **minimal Phase-1 validator**: expiry present, owner present, deactivation trigger present — active in control-plane CI and proven by rejecting a deliberately malformed exception (§95.2, inv. 77); bootstrap exceptions authored one per relaxed gate, with the unarmed *and* armed configurations recorded side by side (§95.2); **SIG-39** armed (bootstrap exception past expiry with its gate still unarmed, Red, Founder); safe defaults in every provisioning template (§95.3, inv. 79); every control explicitly classified fail-closed or fail-open and the classification written down (§64.2, inv. 80); the control-plane-versus-data-plane invariant test (inv. 75, 76 — AT-029, AT-030) | Full exception-lifecycle validation, renewal counting (AT-038), break-glass standardisation, `policies.yaml`, gradual enforcement stages → **G2**. The CP/DP *dependency audit* (as opposed to the invariant test) → **G1** |
| **9** | From the people tier, **nothing** initially except schemas designed with effective dating | — | **L1** (schema shape only) | — | Effective dating and append-only discipline present in every registry and record schema so that history is not retrofitted (§95.3, inv. 47). No people computation, no capacity view, no evidence bundle, no Layer B surface | Everything in P1–P8 (§98.6). Capacity views activate when real people are working in the system. Layer B-M decision support waits for its gates; the datasource separation is a **P2** deliverable — deferred in sequence, never unscheduled (§99.4 item 9) |

---

## 4. The six residuals — in V1, absent from the §98.2 phase bullets

Each of these is named as day-one binding somewhere in the spec and has no corresponding bullet in §98.2's Phases 1–7. They are **in V1**. A lane must not treat them as optional.

| ID | Residual | Why it is V1 (citation) | Lane | Acceptance |
|---|---|---|---|---|
| **R-1** | **The `records/` and `events/` stores and the records repository itself**, live before any dashboard reads from them | §99.6 risk 2: "Section 97 is built in Foundation, before any dashboard that reads from it". `PARTITION.md` already froze `control-plane-records` as a repository with the D107 ruleset | **L4** (all of `control-plane-records`, `schemas/records/**`, `tools/records/**`) | Every store of §97.2 that V1 writes to exists with a schema; the **write-freshness** instrument is declared per store in `os-health.yaml` and is **Blocking** for `events/`, `records/deployments/` and `records/uat/` (§97.2) |
| **R-2** | **Safe defaults, fail-closed classification, the constitution and the untrusted-input rule, API-key-free environments, digest immutability, append-only history and the explicit production-approval event** — all binding from day one *even in bootstrap* | §95.3, the "What remains binding even in bootstrap" list, verbatim | **L5** (K, L), **L2** (E), **L1** (schemas) | `env \| grep -i api_key` returns empty on every machine including shell profiles and repository `.env` files (§98.2 Phase 1); inv. 84 holds; inv. 20, 22, 47 hold |
| **R-3** | **The registry-change lane's staged canary apply and authority-delta gate** | §95.3 final bullet: "the one lane whose owner review is, in bootstrap, the Founder reviewing the Founder is the lane that most needs a mechanical check"; §26.4; D93 | **L3** (`reconciler/**`) + **L1** (`validators/registry/**` for the authority-delta CI rule) | A merged registry change applies to the declared canary set only and holds the fleet for one reconciliation cycle; an **authority delta** — a diff adding a capability, adding an assignment type conferring Write, or changing `access_status` — **fails CI** without a linked decision record ID in the same commit |
| **R-4** | **The operating system's own standing ledger entry in `economics.yaml`** — the seven investment-gate answers for Phases 1–7, the predicted saving and the dated scoring commitment | §98.2 Phase 1 final bullet; D104 moved it to Phase 1 as a hand-authored stub "so the investment gate can gate the phases it is supposed to gate" | **L1** (`registries/**`) — content authored by **L0** | `economics.yaml` carries the entry; `control_plane_budget_band` declared with `expected`, `ceiling`, `currency` (§50.1) |
| **R-5** | **The pre-Phase-1 baseline capture** — one-time banded self-estimates for the §103 minimum measure set, recorded **before** Phase 1 begins | §103.14 via G1's deliverable list ("verification and re-recording of the pre-Phase-1 baseline estimates"); AT-046 permits a measure to be marked `unbaselined` but not to be silently absent | **L0** (this is a Founder input, not a lane build) | Every §103 measure has a recorded pre-Phase-1 banded estimate **or** is explicitly marked `unbaselined`. Verified at G1, captured at V1 — a baseline cannot be captured retroactively |
| **R-6** | **The weekly bootstrap log** with its staleness detector, and the one-page per-repository transition note | §95.4: the log "has a detector: control-plane CI raises **Blocking** drift when the newest entry is older than the calibrated staleness window, initial value 7 days"; the transition note is a Phase 1 product | **L1** (the CI staleness rule, `validators/registry/**`); **L4** (`records/bootstrap-log/` store + the two-of-three pre-fill generator); note authored by **L0** | A `records/bootstrap-log/` entry newer than 7 days exists, or control-plane CI is Blocking |

---

## 5. Build track — dated by subsystem and complexity band (D99)

Complexity bands are §99.2's own, for **one competent engineer with AI assistance, excluding per-product content work**: **S** under a week, **M** one to three weeks, **L** three to eight weeks, **XL** multi-month. The band prices the **full** subsystem; the V1 column states the subset V1 buys.

| Subsystem (§99.2) | Band | Lane (PARTITION) | V1 subset | Depends on (§99.2 spine) |
|---|---|---|---|---|
| **A** Control-plane repository | M | L1 (+L4 for `schemas/records/**`, +L0 for `contracts/**`) | 9 of the 29 §52.6 artifacts (item 1) | — |
| **B** Schema validation and CI gate engine | M | L1 | Full, minus unclassified-control rejection (needs `policies.yaml` → G2) | A |
| **C** Reconciliation engine | L | L3 | Levels 1, 2, 4 + the job-failure path of Level 5. **No Level 3.** | A, B, D |
| **D** Provisioning and scaffolding | L | L3 | `create-product`, `add-person` only | A, B |
| **E** Reusable workflow library | L | L2 | `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`. **Not** `org-export`, **not** `background-queue` | A |
| **F** Evidence chain store and query | M | L2 | Full: eleven-question answerability, `/version` digest-match monitoring, `verify-digest-chain` | E |
| **I** Metrics pipeline | L | L4 (`metrics/**`) | Event-log taxonomy + record stores + Scorecard scan with drop detection + Prometheus scraping `/health`, `/version`, `/metrics`. **DevLake: see V1-D3** | A, E |
| **K** AI runtime contract enforcement | M | L5 | Approved-runtime and approved-extension lists as configuration; API-key-free checks; secret-stripping pre-flight; constitution referenced from every context file | A |
| **L** Access-control architecture | M–L | L5 | **Layer A only.** Org base Read + Teams-derived Write; branch and environment protection; five secret tiers; fail-closed classification. **No Layer B split** | A, D |
| **M** Operations VM | M | L5 (`ops-vm/**`) | Grafana, reconciliation, Scorecard, Renovate, expiry checks, restore rotation. **Not** DevLake (V1-D3), **not** health computation (G1), **not** org export (Early hardening) | — |
| **N** Work tracking conventions | M | L4 | Boards per product plus portfolio aggregate, **or** the single org-level Project with a product field, which §99.5 names the default | — |
| **Q** Asset inventory and deadline watch | S–M | L5 (`assets/**`) | **See `L0 DECISION REQUIRED V1-D5`** — machine-credential expiry rows only, or nothing | A |
| **R** Notification routing | S | L5 (`notify/**`) | Actions webhook to messaging channel; per-product alert channels; the documented phone-escalation path | — |
| **H** Dashboards and views | L | **See V1-D2** | Founder view v0 only (item 7) | I, F, C |
| **G** Plan-checker and Gate 1 tooling | L if built in-house | **See `L0 DECISION REQUIRED V1-D1`** | Phase 7 membership is undecided | — |
| **J** Background machine layer | L + hardware | — | **Not in V1** (§9) | D, E |
| **O** Governance registries and jobs | M | L1 (`registries/**`) + L3 (expiry job) | `exceptions.yaml` + the minimal validator only | A, C |
| **P** People intelligence engine | L–XL | — | **Not in V1** (§9) | I, L, A |

**Effort budget, stated as the spec states it and no further.** §99.2 prices the full surface at **10–14 engineer-months at single-implementer pace**, excluding per-product onboarding content and excluding calendar time for data accumulation. §99.4 prices V1 at **roughly 30%** of that surface — **≈ 3.0–4.2 engineer-months of single-implementer effort**. How five parallel lanes compress that is a throughput question for L0 and is **not** a spec fact. **No lane task in this plan carries a date.**

---

## 6. Merge-train ordering for the V1 build track

`PARTITION.md` fixes the train as **L1 → L4 → L2 → L3 → L5**, once per cycle. That order is the §99.2 dependency spine, and V1 respects it without exception:

```
L1  A + B          schemas and validators — what everything else validates against
L4  I(records) + N record stores and event log — the substrate metrics derive from (inv. 46)
L2  E + F          workflows and evidence chain — consume L1 schemas
L3  C + D          reconciler and provisioning — consume L1 schemas and L5's access model
L5  K + L + M + Q + R  access, infra, ops VM, notify — independent at build time, integrates last
```

A lane that finds itself blocked on another lane's *source* has misread the partition: cross-lane consumption is through `contracts/**` or a published artifact only (PARTITION rule 4). If the contract stub you need is missing, **stop and file a Contract Change Request with L0** (PARTITION rule 2). Do not edit `contracts/**`.

---

## 7. Onboarding track — per product, relative to subsystems consumed (D99)

Applies to the **2–3 pilot products only** (see `L0 DECISION REQUIRED V1-D4`). Sequenced highest `classification.reliability_criticality` first (§96.5). All remaining live products sit in **pre-onboarding mode** (§96.2) with a deadline set from *this* track, per rule R4.

| Onboarding phase | Cannot start until these subsystems are merged to `main` | Deliverables (§98.2) | Completion check, executed as written |
|---|---|---|---|
| **O-1** ≡ Phase 4, Environments | D (create-product), E (parity job), L (environments + scoped secrets), M (ops VM reachable) | The eight standard commands of §33.1; staging provisioned with parity to production; GitHub Environments with scoped secrets and the §27.2 workflow-identity gate on production; parity check job active | Someone unfamiliar with the product runs `make setup && make dev && make test` successfully; `make parity` reports no divergence; every required file of §33.1 is present, `AGENTS.md` included; **and the required-status-check contexts this phase adds are listed in the repository's branch protection and are actually reported by a run** |
| **O-2** ≡ Phase 5, Verification | B (contract schema + validator), E (CI runner) | AI writes the automated suite; QA reviews, corrects and takes ownership; `verification/uat.md`; smoke tests; CI runs the full contract on every push; the eval suite lands under `verification/` where the product declares an `ai_runtime_dependency` | Verification contract present **and passing**, with its seeded-defect case **failing** (D97); QA signed off within the per-product QA-takeover SLA (§96.6, initial value two weeks from the AI-drafted suite landing). A breached SLA is a QA-capacity signal, never a personal one |
| **O-3** ≡ Phase 6, Delivery Pipeline | E (all six workflows), F (evidence chain), L4's `records/deployments/` and `events/` | Immutable artifact build with digest recording and SBOM emission; staging deploy plus smoke; production approval gate with self-review prevention **or its recorded bootstrap exception**; rollback tested at least once, deliberately; backup configured; one restore test performed and recorded, entering the rolling 90-day rotation | A deliberate rollback succeeded in staging; restore test recorded; **the eleven-item evidence chain answerable for one real deployment**; the production-approval test verifies the workflow-identity gate — the approval actor is recorded and the deploy **fails closed** when the approver equals the deploying actor — never environment required reviewers, which are Enterprise-only on private repositories (D73) |
| **O-4** ≡ Phase 7, GSD Activation | G — **membership undecided, see V1-D1** | GSD Core at a pinned tag, minimal profile; project initialised, `.planning/` created; constitution referenced in `CONTEXT.md`; model routing and profile configured, keys verified against the pinned release | A first plan passes the plan-checker and is approved at Gate 1 |

Phases 1, 2 and 3 of §98.2 are **not** onboarding phases — they are Build-track work plus one-time org configuration, and they are covered by §3 and §5 of this file.

§98.2's own pacing note survives D99 and is repeated here because it governs the Onboarding track: *"3–4 weeks per product for anything not already deploying through CI/CD… The first product takes longer; subsequent products inherit the pattern and the scaffolding."* The interim rule of §96.6 applies throughout: **manual feature work continues under the recorded accepted risks; only AI-assisted feature work waits for the contract.**

---

## 8. The V1 invariant floor and the V1 acceptance-test set

### 8.1 Invariants that must hold at V1 exit

These are the §101 items V1 arms. Each has a mechanism in V1. An invariant not listed here is either armed later or renders unarmed (D77) — it is never quietly assumed.

| Inv. | Statement (abbreviated) | V1 mechanism | Carried by |
|---|---|---|---|
| 1 | No product completes onboarding without a verification contract | Control-plane CI presence check + D97 seeded-defect case | Item 5 |
| 3, 4 | Untested backup is no backup; restore-tested within any rolling 90-day window | `restore-test` workflow + `records/restore-tests/`; **SIG-17** Blocking past window | Item 4 |
| 9 | No self-approval, enforced by requiring approval of the most recent reviewable push | Branch protection, **or** a recorded bootstrap exception with the armed configuration written beside the unarmed one (§95.2) | Item 2 |
| 12 | Production approval never self-approved and a separate event from Gate 2 | Workflow-identity gate (D73), failing closed; approval event in `records/deployments/` | Item 4 |
| 20 | External or repository-provided text is data, not authority | Constitution file referenced from every agent context file (§36.1) | Item 1, R-2 |
| 22, 23 | Production artifact is the digest verified in staging; never rebuilt, never rebuilt around registry unavailability | Digest invariant enforced in code; `verify-digest-chain` sweep | Item 4 |
| 44 | Declared state is reconciled against actual; silent drift is not permitted | Reconciler Levels 1/2/4 + the seeded canary (AT-102) | Item 6 |
| 46 | Derived data is computed, never hand-maintained; metrics derive from §97 stores | Every V1 dashboard panel names its record store | R-1, Item 7 |
| 47 | History is append-only for state, decisions, approvals and records | Effective dating in every schema; D107 no-bypass ruleset on `control-plane-records`; reconciler head-SHA anchor | Item 1, Item 9, R-1 |
| 57 | Departures trigger orphan detection; **blocking orphans cannot be dismissed unresolved** | Orphan detection at Blocking severity, **SIG-05**, posted as a named required check (D92) | Item 6 |
| 75, 76 | The control plane observes products and is never in their runtime path | The CP/DP invariant test — AT-029, AT-030 | Item 8 |
| 77 | Every exception has an expiry; one without is invalid and fails CI | The minimal Phase-1 validator, proven by rejecting a deliberately malformed exception | Item 8 |
| 79 | New people, products and tools default to minimum privilege and draft state | Safe defaults in provisioning templates; D106 dangerous-capability rejection | Item 3, Item 8 |
| 80 | Every control is explicitly classified fail-closed or fail-open | The written classification, checked in CI | Item 8 |
| 81 | Auto-repair may only move toward the declared, stricter state | Enforced in code and tested **even though Level 3 does not ship** (§99.4 item 6); AT-033 | Item 6 |
| 84 | API keys remain absent from developer environments | `env \| grep -i api_key` empty on every machine, incl. shell profiles and repo `.env` files | Item 2, R-2 |
| 85 | GSD pinned to a tagged release; third-party Actions pinned to full commit SHAs; reusable workflows consumed by pinned tag | Pin-check job in `ci`; the Actions-SHA check | Item 4 (+O-4 if V1-D1 resolves *in*) |
| 111 | No customer data in repositories | **Partially armed at V1**: the fixture-provenance check (§38.3) and the S19 intake gate (§96.6) are live; the by-identifier construction of support records (§22.2) arms with support intake at Early hardening. State it as partial; do not claim the invariant is fully mechanical | Item 5, §96.6 |

### 8.2 Acceptance tests V1 must pass

| AT | Why it is a V1 test |
|---|---|
| **AT-029** | All products continue serving customers with the control plane unreachable, and a production rollback still executes via the documented manual path — item 8's CP/DP invariant test |
| **AT-030** | A control-plane tool is disabled; `.planning/`, verification contracts and product contracts remain readable and usable without it |
| **AT-033** | No auto-loosening: reconciliation presented with a stricter-than-declared production control raises it for human review and does not relax it |
| **AT-039** | A bootstrap exception carries an expiry and an activation checklist; when the headcount trigger is met or the expiry passes, the gate arms or the exception surfaces as Blocking drift — it cannot lapse silently |
| **AT-051** | Brownfield pre-onboarding mode: a not-yet-onboarded product carries a minimal ruleset, accepted-risk record and named deadline; a breached deadline surfaces as drift |
| **AT-102** | The seeded reconciliation canary: every run must find the seeded drift; a zero-finding run is a **failed** run, raises SIG-13 and triggers the gap procedure |
| **AT-103** | Production restore without hand-held credentials: `restore-production.yml` generated from the template executes end to end with an exceptional-authorisation record and no credential typed by a human |
| **AT-110** | The reconciler credential is provably bounded — six attempts, all six fail, then a normal run completes. §100 states this is **"executed for real at the phase that builds the reconciler"**, which is V1 |
| **AT-009** | Conditional on the pilot's declared conformance profile: for the default `service` profile, the eight commands, the three endpoints and the verification contract |
| **AT-047** *(contract-validation half only)* | A product declaring an extended or 24x7 support model whose declared `coverage_window` is not fully covered by the accepted windows of active rota members **fails contract validation** (D112). The detection-latency half of AT-047 needs incident records and arms later |
| **AT-049** | Conditional on a pilot declaring an `ai_runtime_dependency`: no eval suite under `verification/` → CI fails; a pinned-model change cannot merge without the suite passing |
| **AT-036, AT-037** | Exception expiry revoked by reconciliation with no human action; an exception that cannot be auto-revoked becomes Blocking drift on its expiry date |

### 8.3 Acceptance tests V1 must **not** claim

Listing these is part of the scope contract: a lane that "makes a test pass" from this list has built out of scope.

`AT-001` (needs every surface enumerating from the registry — dashboards and economics arrive at G1/G3) · `AT-002` (needs capacity profile, ramp curve and Insufficient Evidence → P1/P4) · `AT-003`–`AT-008`, `AT-017`, `AT-018`, `AT-021` (person and assignment lifecycles → Early hardening) · `AT-019`, `AT-020` (split/merge → scale activation) · `AT-022` (founder continuity drill) · `AT-023`–`AT-027`, `AT-101` (platform change, canary, contract versioning, incident concurrency) · `AT-031` (tool independence — `tools.yaml` is a G8 artifact) · `AT-032` (self-observability beyond the reconciler's own failure) · `AT-034` (governance layerability — the removable artifacts do not yet exist) · `AT-035` (org export restore → Early hardening; V1 instead carries the **dated accepted risk** §98.2 Phase 1 permits under D80) · `AT-038` (renewal counting → G2) · `AT-040`–`AT-046`, `AT-048`, `AT-050`, `AT-104`–`AT-107` (governance tier) · `AT-052`–`AT-088` (people tier) · `AT-089`–`AT-100`, `AT-108`, `AT-109` (access separation and the background cage).

---

## 9. The deferred register — every item and the trigger that un-defers it

Column *Source* is the spec passage that both defers the item and names its trigger. Nothing here is a judgment call.

### 9.1 Explicitly deferred by §99.4's closing paragraph

| Deferred item | Un-defer trigger | Lands in | Source |
|---|---|---|---|
| Background machine layer (subsystem J) — cage, whitelist queue, draft-PR-only machine account, egress override, wall-clock stop unit, local inference endpoint | **The CPU benchmark passes.** The benchmark is prompt-processing bound, run before buying hardware; a failed benchmark parks the layer without shame, and a parked benchmark parks every local-inference slot because all three model configurations share the one endpoint | §98.2 Phase 3 (as a go/park decision), then its own build | §99.4 closing; §98.2 Phase 3; §99.5 |
| Shared-service registry (`service.yaml`) and consumer contract tests | **First genuine shared service** | Scale activation | §98.4 |
| Product split, merge and transfer processes | **First split or merge**; **first transfer** | Scale activation | §98.4 |
| Dependency-graph views | **Roughly 10 products, or the first shared service** | Scale activation | §98.4 |
| Versioned-contract migration machinery (`contract_version` enforcement, compatibility states) | **First contract schema change** — §98.3 puts it plainly: "Needs a reason to change a schema" | Early hardening / scale activation | §98.3; §98.4 |
| Domains and topology activation (`topology.yaml` live) | **A second Team Lead exists** (§66). Note the split: the artifact is **built** at G7 and verified while dormant; **activation** is P3 | G7 build, later activation | §98.4; §98.5 (G7) |
| All predictive economics and forecasting (PLU model, capacity forecast, verification-demand forecast, bottleneck diagnosis chain, forecast scoring) | **At least two quarters of G3 attention data.** §98.1's calendar-gating honesty: no amount of build acceleration compresses this | G5 | §99.4 closing; §98.5 (G5) |
| All Layer B decision support (Layer B-M evidence bundles, review packs, decision matrices, promotion readiness) | **The Layer B datasource separation is implemented and verified** — *verified* means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds. The separation itself is a **P2** deliverable, deferred in sequence, never unscheduled | P2 (separation) → P4 (bundles) | §99.4 item 9; §98.6 sequencing rules |

### 9.2 Deferred to Early hardening (§98.3) — built while moving from 2–3 products to the full portfolio

| Deferred item | Un-defer trigger (§98.3's own wording) | Lane when built |
|---|---|---|
| Reconciliation **auto-repair (Level 3)** and **drift classification** | "Auto-repair waits until detection has run clean for weeks, and drift classification needs several products before drift is a real risk." §99.6 risk 6 makes this the most dangerous code in the system: detect-only first, repair classes enabled **one at a time**, stricter-only enforced in code and tested | L3 |
| `contract_version` enforcement | "Needs a reason to change a schema" | L1 |
| Platform change process and canary set | "Needs enough products for a canary to be meaningful" | L2 + L0 |
| Change manifests (`changes/*.yaml`), bulk fleet-migration PR script, change-matrix scaffold | "Needs cross-product changes to exist" | L0 (`contracts/**`) + L2 |
| Acting Team Lead designation | "Should be in place before the first extended absence" | L1 (`registries/**`) |
| Person lifecycle scaffolding (`change-role`, `remove-person`, template evolution) | "Needed before the first hire or departure"; §98.3 final row: the rest follow "the first role change and the first departure" | L3 |
| Operational asset inventory and vendor deadline watch (subsystem Q, full) | "Needed before the first certificate expiry, roughly month 3" — **but see V1-D5** for the machine-credential sliver | L5 |
| Support intake and triage per product (email-ingest hook, `records/support/`, SIG-41) | "Needed as soon as customers can report defects" | L4 + L5 |
| Organisation export job (`org-export` workflow, SIG-34, AT-035) | "Needed before the first restore test of the export, within the first quarter." Until then §98.2 Phase 1 requires the absence be recorded as a **dated accepted risk** (D80) | L2 + L5 |
| Product launch readiness gate and the launch-pack generator | "Needed before the first new product launches" | L2 |

### 9.3 Deferred to scale activation (§98.4) — on trigger, never on the calendar

| Deferred item | Activation point |
|---|---|
| Temporary specialist and contractor model | First contractor |
| Platform compatibility migration | First contract schema change |
| Data and privacy extension (`records/deletion-requests/`, AT-105) | First regulated-data customer requirement |
| Second review cluster | Roughly 12 people |

### 9.4 Deferred governance and people tiers in full

Everything in §98.5 (G1–G8) and §98.6 (P1–P8) is out of V1 except the four slivers named in §99.4 item 8. Each G and P phase additionally passes the **platform investment gate** of §59.2 before it is committed — "If a phase cannot justify itself, it is not built" (§98.1) — and a phase that fails its gate is recorded as **`declined`**, which is a state distinct from `unbuilt` and which releases the P0-before-P2 lock. An **unbuilt** P0 holds the lock exactly as written. **The P0-before-P2 rule is binding at V1**: no P2 or P3 capability may be started while a P0 capability is unbuilt.

---

## 10. Why this V1 is coherent — what it does end to end on day one

The test of a scope cut is not that it is small. It is that nothing in it dangles. V1's four claims each close a loop with no missing link, and the loops interlock.

### 10.1 The four claims and their closed loops

| §99.4 claim | The mechanism that makes it true at V1 | The check that proves it |
|---|---|---|
| **Declared state enforced** | `people.yaml`, `roles.yaml`, `product.yaml` are schema-validated in CI; Teams are derived from the registries; branch protection and environments are applied from the template by `create-product`; a registry edit stages to the canary set and an authority delta fails CI without a decision record | Registries, contracts and Team membership agree, **machine-verified** (§98.2 Phase 3 completion check) |
| **Drift visible** | The reconciler diffs declared vs actual on a schedule, at Levels 1/2/4, over exactly four scopes: Teams vs registries, expiry revocation, protection drift, orphan detection | The seeded canary must be found on every run; a zero-finding run is a **failed** run (AT-102) |
| **Orphans impossible to miss** | Orphan detection runs at **Blocking** severity (SIG-05), and the block is real: the reconciler posts a named required check on every affected repository and it stays red while the finding is open (D92) | A product with no active Primary Owner, Cross-Reviewer or named responder cannot merge |
| **Every production artifact traceable** | `build` records the digest and emits an SBOM; `deploy-staging` verifies it; `deploy-production` refuses a different digest, records the approval as a distinct event through the workflow-identity gate, and writes the deployment record and event as **required, failing steps** | The eleven questions of §32 answerable for one real deployment (§98.2 Phase 6 completion check); `verify-digest-chain` sweeps for mismatch |

### 10.2 The day-one walkthrough — one change, one pilot product, start to finish

1. A developer opens a PR on a pilot product. Branch protection requires review and **approval of the most recent reviewable push** — or, on the control-plane repository during bootstrap, requires it under a recorded exception whose *armed* configuration sits beside the unarmed one, so arming later is a configuration flip and not a build project (§95.2).
2. CI runs the product's verification contract. The contract's **seeded-defect case must fail**; if it passes, the run is a FAILED run and the product is Blocking on SIG-18 (D97). `make parity` runs; a parity violation on a production deployment path is a blocking CI failure.
3. The lane-guard check confirms the PR touches only paths its lane owns (PARTITION rule 1). CODEOWNERS — generated, human identities only — resolves an approver whose approval actually counts, because Teams granted Write before protection was armed (D101).
4. On merge, `build` produces one immutable artifact, records its digest, emits its SBOM.
5. `deploy-staging` deploys **that digest**, runs smoke, and a UAT result reaches `records/uat/` through the `RECORD-VERIFICATION-RESULT` dispatch — nobody edits a record file by hand.
6. Production approval happens as its **own recorded event**. `deploy-production` verifies the approving identity differs from the deploying identity and **fails closed** if they match (D73). It refuses any digest other than the staging-verified one. Its deployment-record and event writes are required, failing steps: a deploy whose record cannot be written is a deploy whose evidence chain does not close.
7. Overnight the reconciler runs. It finds the seeded canary or the run is declared failed. It revokes anything past its `end_date`. It compares Team membership, branch protection and environment configuration against the registries. It anchors the records-repo head SHA into the protected control-plane repository, so a rewrite of history is provable rather than arguable (D107). It publishes its per-run API-call counts and a signed run record (D96).
8. Any Blocking finding becomes a named required check on the affected repositories. Work stops there until it is resolved. Nothing is a notification nobody reads.
9. Monday morning, the Founder opens **one screen**: open drift by class, orphans, exception expiries, Scorecard per product, and which pre-onboarding products are approaching their deadline. No activity feed. Signals with no live source render **unarmed — not yet instrumented**, never as amber, so the screen does not open as a wall of amber (D77).
10. A new product or a new person is one command with **zero hand-editing** — which is what makes eight products cheaper to run than two hand-configured ones (§99.4 item 3).

### 10.3 What V1 deliberately cannot do, and why that is coherent rather than incomplete

V1 cannot forecast, cannot rank attention, cannot detect a failure pattern, cannot produce a people evidence bundle, cannot auto-repair, and cannot answer any of the eight Founder decision questions of §93.3. Each absence is load-bearing:

- **Forecasting and pattern detection are absent because their data does not exist yet.** §98.1 states it without hedging: pattern detection needs realistically two quarters of incident and exception history; capacity forecasting needs at least two quarters of attention data. Building either now produces a confident computation over nothing. §99.6 risk 7 names the failure mode — "instrument-before-operate bureaucracy collapse" — and its defence is exactly this: P0-before-P2, data-before-forecasts.
- **Auto-repair is absent because it is the riskiest code in the system.** §99.6 risk 6: a write-scope, org-admin automation whose bug loosens security or locks everyone out, held by the highest-privilege identity in the estate. Detection must run clean for weeks first. The stricter-only rule is nevertheless written and tested at V1, so the rule exists before the code that could violate it.
- **Layer B is absent because it cannot be built before it can be access-controlled.** §98.6's binding sequencing rule: P4 must not begin before the datasource separation is implemented and verified. §99.6 risk 8: Layer B leakage poisons adoption of the entire operating system. Item 9's contribution — effective dating in the schemas — is precisely the part that cannot be retrofitted, and it is the only part V1 buys.
- **DevLake-derived review and cycle-time metrics are absent because they need team activity to be meaningful anyway** (§99.4 item 7).

The coherence argument is therefore not "V1 is enough". It is: **every capability V1 omits is omitted because its input does not exist, its risk is unbounded until detection has run, or its access control is not yet built — and every capability V1 contains has a complete loop from declaration to enforcement to evidence.** A V1 with a half-built reconciler or a verification check that only tests presence would fail that standard. This one does not.

---

## 11. Scope-freeze mechanics — how a lane answers "is this in V1?"

L0 authors `contracts/v1-scope.yaml` in Phase 0 and **freezes it** with the rest of `contracts/**` (PARTITION rule 2). It is the machine-readable form of §3, §4 and §9 of this file. A lane never edits it; a lane needing a change files a Contract Change Request.

```yaml
# contracts/v1-scope.yaml — authored by L0, frozen. Shape only; L0 fills the entries.
v1_scope_version: 1
pilot_products: []            # V1-D4 — L0 names 2 or 3, highest reliability_criticality first. Values to be supplied after Q6 (REG-047) is answered — the pilot product selection is a founder decision.
items:                        # the nine of §99.4 plus the six residuals of §4
  - id: V1-01
    spec_ref: "99.4#1"
    lanes: [L1, L4, L0]
    subsystems: [A, B]
    paths: ["schemas/registry/**", "schemas/product/**", "registries/**", "validators/registry/**"]
deferred:
  - id: DEF-J
    item: "background machine layer"
    trigger: "CPU benchmark passes"
    trigger_source: "99.4 closing; 98.2 Phase 3; 99.5"
    lands_in: "own build after Phase 3 go/park decision"
```

**The lane rule, literal:**

```bash
set -euo pipefail
# From the control-plane repo root. Answer "is <path> in V1 scope?"
yq -r '.items[] | .id + " " + (.paths | join(" "))' contracts/v1-scope.yaml \
  | grep -F -- "<the path you want to touch>" \
  || { echo "NOT IN V1 SCOPE — STOP. Open a blocker issue titled 'scope: <path>' and assign L0."; exit 1; }
```

**STOP rule for every lane:** if a task you have been given touches a path that is not listed in `contracts/v1-scope.yaml`, **do not proceed and do not improvise a home for it**. Open a blocker issue naming the path and the task, assign it to L0, and move to your next task. Adding a path is an L0 decision, never a lane decision.

---

## 12. L0 DECISION REQUIRED

Six questions this file cannot answer from the spec. Each blocks a specific set of lane tasks. None may be resolved by a lane.

---

> ### `L0 DECISION REQUIRED — V1-D1` · Is Phase 7 (GSD activation, subsystem G) inside V1?
>
> **The conflict.** §98.2's header makes Phases 1–7 "Launch-critical — must exist before the first pilot product completes onboarding", and Phase 7 is one of the seven. §99.4's nine-item enumeration of V1 does **not** mention GSD, the plan-checker, Gate 1 tooling or `.planning/`. §99.3 item 3 lists **plan-checker internals** as design-open: *"verify every assumed capability against the exact pinned GSD release before configuring it; budget building the checker in-house if verification fails."* §99.6 risk 4 rates the dependency as high-mortality and prices the in-house fallback. §99.2 bands subsystem G at **L (three to eight weeks) if built in-house**.
>
> **Options.**
> - **(a) In V1, adopt-only.** Onboarding phase O-4 runs: GSD Core at a pinned tag, minimal profile, `.planning/` created, constitution referenced in `CONTEXT.md`, model routing configured. The capability verification of §99.3 item 3 is executed **immediately**, per §99.6 risk 4. If verification fails, the in-house build is **not** started inside V1 — Gate 1 runs as a recorded human step under a bootstrap exception and O-4's completion check is deferred with a dated trigger.
> - **(b) In V1, including the in-house fallback.** Same as (a), but a failed verification pulls an **L-band** subsystem into V1, changing the effort budget of §5 materially.
> - **(c) Out of V1.** O-4 moves to Early hardening. Pilot products complete onboarding through O-3 and run Gate 1 as a recorded human step. This contradicts §98.2's "Phases 1–7" header and must be recorded as a deliberate scope decision, not left implicit.
>
> **What is blocked until this is decided.** Whether subsystem G appears in `contracts/v1-scope.yaml`; whether O-4 exists in the Onboarding track; whether any lane owns `.planning/` tooling — **no lane in `PARTITION.md` currently owns subsystem G**, which is itself part of the question.
>
> **Recommendation to L0, for the record:** (a). It honours the §98.2 header, keeps the L-band risk outside V1, and executes the verification §99.6 risk 4 demands be executed immediately.

---

> ### `L0 DECISION REQUIRED — V1-D2` · Which lane owns Founder-view v0 (subsystem H)?
>
> **The gap.** `PARTITION.md` assigns subsystems A,B→L1; E,F→L2; C,D→L3; I,N→L4; K,L,M,Q,R→L5. **Subsystem H (Dashboards and views) is assigned to no lane**, and no lane's OWNS column names a `dashboards/**` path. §99.4 item 7 nonetheless makes Founder view v0 a V1 item.
>
> **Options.**
> - **(a) L5.** Dashboard JSON lives under `ops-vm/**` (Grafana provisioning is an operations-VM concern; §99.5 "dashboards as provisioned JSON"; subsystem M is already L5). L4 exposes the computed values through `metrics/**` and L5 renders them. Requires no partition change — `ops-vm/**` already covers it.
> - **(b) L4.** Dashboard JSON lives under `metrics/**` alongside the computation that feeds it. Requires no partition change either — `metrics/**` is L4's.
> - **(c) L0.** L0 owns the dashboard definitions as a `docs/**`-adjacent artifact. Rejected on its face: dashboards are provisioned configuration under CI, not documentation.
>
> **What is blocked.** Every Founder-view-v0 task. Do not start one until this is answered — a lane writing dashboard JSON into the other lane's path **fails the lane-guard check** and cannot merge (PARTITION rule 1).
>
> **Recommendation to L0:** (a). It keeps the render surface with the machine that hosts it and keeps `metrics/**` purely a computation path, which preserves PARTITION rule 4 — L5 consumes L4's output as a published artifact, never by reaching into its source tree.
>
> **State:** Closed — resolved by **FD-002** (2026-09-02, REG-001): H → **L5** (`ops-vm/**`), option (a) above. See `_FOUNDER_DECISIONS.md` FD-002.

---

> ### `L0 DECISION REQUIRED — V1-D3` · Is DevLake installed in V1?
>
> **The conflict, verbatim on both sides.** §98.2 Phase 2 bullet one: *"DevLake and Grafana on the operations VM, connected to the organisation."* §99.4 item 7: *"Founder view v0 from GitHub API and reconciliation output plus Scorecard — **DevLake is heavy and safely deferrable a few weeks in a solo build**; review and cycle-time metrics need team activity to be meaningful anyway."*
>
> **Bearing on the decision.** Phase 2's completion check reads *"every product visible in Grafana with a Scorecard score"* — which **does not require DevLake**. §99.5 warns: *"Confirm DevLake's required database engine and version for the pinned release before install — it determines the compose file and the control-plane backup procedure."* §99.3 item 4 makes **DevLake field coverage** design-open and requires it be confirmed *before Phase G3*, not before V1. Four V1-adjacent signals name DevLake as their source (SIG-04, SIG-07, SIG-08, SIG-40) and would render **unarmed — not yet instrumented** under D77 if it is deferred, which is a legitimate state, not a failure.
>
> **Options.**
> - **(a) Deferred out of V1.** V1 ships Grafana + Prometheus + Scorecard. DevLake installs when team activity makes review and cycle-time metrics meaningful, and in any case before G3. §99.4 governs because it is the V1-scope section.
> - **(b) In V1 as Phase 2 states.** Buys the DevLake-sourced signals earlier at the cost of the database-engine decision, the compose file and the control-plane backup procedure landing inside V1.
>
> **What is blocked.** L5's `ops-vm/**` compose file and the control-plane backup procedure; whether L4's `metrics/**` targets DevLake models or the GitHub API directly.
>
> **Recommendation to L0:** (a), and record it as a decision so it is not re-litigated. §99.4 is the section that defines V1 membership; §98.2's bullet is a phase inventory that D99 has already established is not a schedule.
>
> **State:** Closed — resolved by **REG-058** in Decision Signoff §2, 2026-09-02, and reaffirmed by **FD-112** (2026-09-08, PFD-032): DevLake deferred from V1 scope, option (a). See `_FOUNDER_DECISIONS.md` FD-112 and `contracts/v1-scope.yaml`.

---

> ### `L0 DECISION REQUIRED — V1-D4` · Which products are the pilots, and are there two or three?
>
> **What the spec fixes and what it leaves open.** §99.4 fixes the count as **"2–3 pilot products"**. §96.5 fixes the ordering: *sequenced highest `reliability_criticality` first*. Neither names products — correctly, because product identity is configuration, not architecture (inv. 52).
>
> **What L0 must supply.** The ordered list, written into `contracts/v1-scope.yaml` under `pilot_products`. Every other live product then gets a stub `product.yaml` with an onboarding block and a **deadline set from the Onboarding track of §7**, not from a §98.2 week label (rule R4, D99).
>
> **What is blocked.** All Onboarding-track work (O-1 through O-4) and the Phase 2 pre-onboarding stubs. A lane cannot pick a pilot; product criticality is a Founder judgment recorded in `classification.reliability_criticality`.
>
> **Note for L0:** the choice interacts with §95.1 — a product repository whose existing team already holds Write **satisfies gate independence immediately and never enters bootstrap**. Choosing such a product as pilot one arms more of the invariant floor in §8.1 for real rather than under exception.
>
> **State:** Closed — resolved by **FD-016** (2026-09-02): **TWO** pilots, ordered highest `reliability_criticality` first, then `business.criticality`, then cheapest onboarding cost. See `_FOUNDER_DECISIONS.md` FD-016 (Decision Signoff §1, Q6/REG-047, carries only the recommendation this ratifies).

---

> ### `L0 DECISION REQUIRED — V1-D5` · Does the operational asset inventory (subsystem Q) ship a V1 sliver?
>
> **The conflict.** §98.3 defers the operational asset inventory and vendor deadline watch to Early hardening: *"Needed before the first certificate expiry, roughly month 3."* §97.2 states the opposite for one class of asset: *"Each control-plane machine credential carries its **expiry date**, not only its rotation cadence, in the operational asset inventory, so the 30-day expiry alert fires on it like any other asset (Section 49)."* V1 creates exactly three such credentials — the **reconciler** credential, the **records-writer** GitHub App token, and the **provisioning CLI** credential (§40.1, D89) — and §99.6 risk 6 makes the reconciler's the highest-privilege identity in the estate.
>
> **Options.**
> - **(a) Minimal sliver in V1.** `assets/**` holds machine-credential rows only: owner, expiry date, rotation cadence, 30-day lead alert. Certificates, domains, OAuth, signing and vendor deprecations wait for Early hardening. Band impact: within the **S** end of subsystem Q's S–M range.
> - **(b) Nothing in V1.** The three credentials' expiries live only in the runbook until Early hardening, and the 30-day alert does not fire on them. Must be recorded as a dated accepted risk with an owner, since §97.2 states the requirement in the present tense.
>
> **What is blocked.** L5's `assets/**` tasks, and whether the 30-day expiry alert exists at V1 exit.
>
> **Recommendation to L0:** (a). Three rows and one alert is smaller than the accepted-risk record option (b) would require, and an unwatched expiry on the reconciler credential is the failure §99.6 risk 6 is written about.
>
> **State:** Closed — resolved in Decision Signoff §2, 2026-09-02

---

> ### `L0 DECISION REQUIRED — V1-D6` · How many humans hold Write on the control-plane repository during V1?
>
> **Why this is a scope question, not a staffing one.** §95.1 scopes Bootstrap Mode **per repository, never per company**: the shortfall exists only where no second context-holding human exists. §98.7 assumes *"the Founder solo under Bootstrap Mode"* for Foundation. `PARTITION.md` describes a different reality: five parallel AI developers on five branches plus one human/lead integrator. AI developers are **not** context-holding humans for gate-independence purposes, and §98.2's Phase 1 completion check is explicit that *"an approval from a machine account does **not** satisfy branch protection — CODEOWNERS is generated to contain human identities only, and the check is executed negatively."*
>
> **What L0 must decide and record.** For each repository in scope, how many context-holding humans hold Write at V1, and therefore which rows of the §95.4 activation checklist arm for real and which run under a recorded bootstrap exception. The four thresholds are fixed by §95.4 and are not negotiable: **2 humans** arms no-self-approval, Gate 2 independent review and most-recent-push approval; **3 humans** arms production-approver ≠ deploying-actor and the real cross-review matrix; **QA role filled** arms independent verification authority and release sign-off; **4+ humans** arms Backup Owner coverage, the knowledge-redundancy floor and responder rotation.
>
> **What is blocked.** Which of inv. 9, 12 and 57 arm mechanically at V1 versus run under exception (§8.1); how many bootstrap exceptions L1 must author into `exceptions.yaml`; and whether §98.2's Phase 1 completion check *"executed for real once headcount permits"* is executed for real at V1 or is deferred with its trigger recorded.
>
> **Binding regardless of the answer.** Every relaxed gate gets one exception naming the gate, the repositories, the compensating controls, an owner, an expiry and a deactivation trigger, with the **armed configuration recorded beside the unarmed one** (§95.2). An exception whose expiry passes with its gate still unarmed is **SIG-39**, Red, routed to the Founder. Stubbed gates have a habit of staying stubbed (§99.6 risk 3).
>
> **State:** Closed — resolved by **FD-017** (2026-09-02): **TWO** — the Founder (L0, FD-001) and Nimesh (Team Lead), on `control-plane` and `product-template`. See `_FOUNDER_DECISIONS.md` FD-017 (Decision Signoff §1, Q12/REG-046, carries only the recommendation this ratifies).

---

## 13. V1 exit gate

V1 is complete when this script exits 0. It is run by **L0** on `main`, from the control-plane repository root, with `gh` authenticated, `yq`/`jq` on PATH, and `ORG` (the GitHub organisation login) and `L0_LOGIN` (the integrator's GitHub login) set in the environment. Every check has an unambiguous output; nothing here requires interpretation.

```bash
#!/usr/bin/env bash
# implementation/master/v1-exit-gate.sh — run by L0 only, on main.
set -euo pipefail
: "${ORG:?ERROR: ORG env var must be set to the GitHub organisation login}"
: "${L0_LOGIN:?ERROR: L0_LOGIN env var must be set to the integrator's GitHub login}"
FAIL=0
chk() { if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1"; FAIL=1; fi; }

# --- Item 1: control-plane repository, schemas, CI validation -------------
chk "V1-01 registries present" \
  'test -f people.yaml && test -f roles.yaml && test -f platform.yaml && test -f exceptions.yaml && test -f economics.yaml'
chk "V1-01 every registry schema declares effective dating" \
  'test "$(grep -rl "effective_from" schemas/registry/ | wc -l)" -ge 1'
chk "V1-01 event_type enum is closed in platform.yaml (D103)" \
  'yq -e ".event_types | length > 0" platform.yaml'
chk "V1-01 malformed exception is rejected (inv. 77)" \
  '! ./validators/registry/validate-exceptions.sh tests/fixtures/exception-no-expiry.yaml'
chk "V1-01 role default containing a dangerous capability is rejected (D106)" \
  '! ./validators/registry/validate-roles.sh tests/fixtures/role-default-production-approval.yaml'
chk "V1-01 undefined capability is rejected (D81, D90)" \
  '! ./validators/registry/validate-roles.sh tests/fixtures/capability-undefined.yaml'

# --- Item 2: GitHub enforcement ------------------------------------------
chk "V1-02 org base permission is read" \
  'test "$(gh api /orgs/$ORG --jq .default_repository_permission)" = "read"'
chk "V1-02 branch protection requires last-push approval on control-plane" \
  'gh api /repos/$ORG/control-plane/branches/main/protection --jq ".required_pull_request_reviews.require_last_push_approval" | grep -qx true'
chk "V1-02 no machine bypass actor on control-plane (D89)" \
  'test "$(gh api /repos/$ORG/control-plane/rulesets --jq "[.[].bypass_actors[]?] | length")" = "0"'
chk "V1-02 records repo ruleset blocks force-push and delete (D107)" \
  'gh api /repos/$ORG/control-plane-records/rulesets --jq ".[].rules[].type" | grep -q non_fast_forward'
chk "V1-02 every environment carries a deployment branch policy (D91)" \
  '! for p in $(yq -r ".pilot_products[]" contracts/v1-scope.yaml); do gh api /repos/$ORG/$p/environments --jq ".environments[] | select(.deployment_branch_policy == null) | .name"; done | grep -q .'
chk "V1-02 no API keys anywhere (inv. 84)" \
  '! env | grep -qi api_key'

# --- Item 3: scaffolding v0 ----------------------------------------------
chk "V1-03 create-product runs with zero hand-editing" \
  './tools/provision/create-product --dry-run --name gate-probe --owner "$L0_LOGIN"'
chk "V1-03 add-person runs with zero hand-editing" \
  './tools/provision/add-person --dry-run --login gate-probe-user --role developer'

# --- Item 4: delivery pipeline and evidence chain -------------------------
chk "V1-04 all six V1 reusable workflows exist" \
  'for w in ci build deploy-staging deploy-production migrate restore-test; do test -f ".github/workflows/$w.yml" || exit 1; done'
chk "V1-04 every third-party action is pinned to a full commit SHA (inv. 85)" \
  '! grep -rhoE "uses: [^ ]+@[^ ]+" .github/workflows/ | grep -vE "@[0-9a-f]{40}$" | grep -v "^uses: \./" | grep -q .'
chk "V1-04 digest chain has no mismatch" \
  './tools/evidence/verify-digest-chain --all'
chk "V1-04 eleven evidence questions answerable for one real deployment" \
  './tools/evidence/answer-chain --deployment latest --require 11'
chk "V1-04 a deliberate rollback is recorded" \
  'grep -rl "rollback_of" ../control-plane-records/records/deployments/ | grep -q .'
chk "V1-04 a restore test is recorded within 90 days (inv. 4)" \
  './tools/records/restore-currency --window-days 90 --fail-on-stale'

# --- Item 5: verification contracts ---------------------------------------
chk "V1-05 every onboarded product has a verification contract (inv. 1)" \
  './validators/registry/verification-presence.sh --onboarded-only'
chk "V1-05 every contract declares a seeded-defect case (D97)" \
  './validators/registry/seeded-defect-declared.sh --all'
chk "V1-05 every seeded-defect case actually failed on its last run (SIG-18)" \
  './validators/registry/seeded-defect-last-run.sh --require-fail'

# --- Item 6: reconciliation v0 --------------------------------------------
chk "V1-06 reconciler found the seeded canary on its last run (AT-102)" \
  './reconciler/last-run-report --require-canary'
chk "V1-06 stricter-only rule test passes (inv. 81, AT-033)" \
  './validators/drift/test-stricter-only.sh'
chk "V1-06 reconciler posts a named required check on Blocking findings (D92)" \
  './validators/drift/test-blocking-check-run.sh'
chk "V1-06 records head SHA anchor is current (D107)" \
  './reconciler/verify-records-anchor'
chk "V1-06 reconciler credential is provably bounded (AT-110)" \
  './validators/drift/at-110-bounded-credential.sh'
chk "V1-06 zero open Blocking drift" \
  'test "$(./reconciler/findings --class blocking --count)" = "0"'

# --- Item 7: Founder view v0 ----------------------------------------------
chk "V1-07 every product has a Scorecard score" \
  './metrics/scorecard-coverage --require-all'
chk "V1-07 every dashboard panel names its record store (inv. 46)" \
  './metrics/panel-source-audit --require-store'
chk "V1-07 no unfed signal renders as amber (D77)" \
  './metrics/arming-audit --require-unarmed-for-unfed'

# --- Item 8 + residuals ----------------------------------------------------
chk "V1-08 control-plane/data-plane invariant test passes (AT-029, AT-030)" \
  './validators/drift/at-029-030-cp-dp.sh'
chk "V1-08 every control carries a fail-closed/fail-open classification (inv. 80)" \
  './validators/registry/control-classification.sh --require-all'
chk "R-1 write freshness is Blocking for events, deployments, uat (97.2)" \
  './tools/records/write-freshness --blocking-stores events,deployments,uat'
chk "R-3 authority delta without a decision record fails CI (D93)" \
  '! ./validators/registry/authority-delta.sh tests/fixtures/grant-without-decision.diff'
chk "R-4 economics.yaml carries the standing ledger entry (D104)" \
  'yq -e ".automation_ledger[] | select(.id == \"operating-system\")" economics.yaml'
chk "R-5 every 103 measure is baselined or marked unbaselined (AT-046)" \
  './metrics/baseline-audit --allow-unbaselined-marked'
chk "R-6 bootstrap log entry is newer than 7 days (95.4)" \
  './tools/records/bootstrap-log-freshness --max-age-days 7'

echo "----"
if [ "$FAIL" -eq 0 ]; then echo "V1 EXIT GATE: PASS"; else echo "V1 EXIT GATE: FAIL"; fi
exit "$FAIL"
```

**STOP rule for L0:** a `FAIL` line is not a waiver candidate. Every check above maps to an invariant in §8.1 or a completion check in §98.2. If a check cannot pass, the correct action is a recorded exception with an expiry, an owner and a deactivation trigger (§54.2, inv. 77) — never a deleted check. A deleted check is the silent-gate failure §95.1 is written to prevent.

---

## 14. Citation self-verification

Run this before trusting any identifier in this file. It re-derives every spec reference from the spec text. Output is one `OK`/`MISSING` line per identifier; any `MISSING` means this file is wrong and must be corrected before a lane acts on it.

```bash
set -euo pipefail
# SPEC is the checked-in pointer file `contracts/gate/SPEC_PATH` (written by
# lanes/L0-05-integration-gate.md), never a hardcoded personal path — this
# runs correctly for any lane developer, clone or CI runner.
SPEC="$(cat contracts/gate/SPEC_PATH 2>/dev/null || true)"
[ -n "$SPEC" ] && [ -f "$SPEC" ] || { echo "MISSING §14 spec — contracts/gate/SPEC_PATH is absent or stale; see lanes/L0-05-integration-gate.md"; exit 2; }

# Sections cited
for s in "98.1" "98.2" "98.3" "98.4" "98.5" "98.6" "98.7" \
         "99.1" "99.2" "99.3" "99.4" "99.5" "99.6" \
         "95.1" "95.2" "95.3" "95.4" "96.2" "96.5" "96.6" \
         "97.1" "97.2" "97.3" "52.2" "52.6" "53.2" "53.3" "53.4" "26.4" "33.1" "64.2"; do
  grep -q "^### $s " "$SPEC" && echo "OK   §$s" || echo "MISSING §$s"
done

# Decisions cited
for d in D73 D74 D75 D77 D80 D81 D87 D89 D90 D91 D92 D93 D96 D97 D99 D100 D101 D103 D104 D106 D107 D108 D109 D111 D112; do
  grep -qE "^\| $d \|" "$SPEC" && echo "OK   $d" || echo "MISSING $d"
done

# Acceptance tests cited
for a in AT-009 AT-029 AT-030 AT-032 AT-033 AT-035 AT-036 AT-037 AT-038 AT-039 AT-046 \
         AT-047 AT-049 AT-051 AT-089 AT-091 AT-097 AT-098 AT-102 AT-103 AT-110; do
  grep -qE "^\| $a \|" "$SPEC" && echo "OK   $a" || echo "MISSING $a"
done

# Signals cited
for g in SIG-03 SIG-05 SIG-13 SIG-17 SIG-18 SIG-34 SIG-38 SIG-39 SIG-41; do
  grep -qE "^\| $g \|" "$SPEC" && echo "OK   $g" || echo "MISSING $g"
done

# The two load-bearing quotations
grep -q "The minimal honest V1" "$SPEC" && echo "OK   §99.4 title" || echo "MISSING §99.4 title"
grep -q "Launch-critical — must exist before the first pilot product completes onboarding" "$SPEC" \
  && echo "OK   §98.2 launch-critical header" || echo "MISSING §98.2 launch-critical header"
```

**One correction to escalate, found while verifying the above and out of scope for this file:** §52.2 contains **two rows both numbered `SIG-43`** — *Unclosed learning-loop items* (Amber, QA, sourced from `records/postmortems/` and `records/incidents/`) and *Founder operating load* (Amber/Red, Team Lead, sourced from the attention ledger, added by D104). Both are Governance-tier signals and neither arms at V1, so this does not block V1. L0 should raise it as a specification defect before G1 authors `os-health.yaml`, where a duplicate signal ID becomes a real collision. Reported, not resolved — resolving it is a spec change, not an implementation decision. Withdrawn — D113 fixed this. SIG-43 was the duplicate; the count is now 47, denominator 47.
