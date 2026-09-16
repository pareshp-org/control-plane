# 02 — Acceptance Test Mapping

**Owner:** L0 Integrator. **Status:** authoritative for the five-lane build. **Source of truth:** `Research/MultiProduct_MasterSpec_v4.0.md` Section 100 (110 tests, AT-001 → AT-110) and Section 101 (111 invariants).

This file maps every one of the 110 acceptance tests to **(a)** the lane that implements what it exercises, **(b)** the phase at which it can *first* be run, and **(c)** whether it is automatable or needs a human step. It exists because five lanes build in parallel with no shared context: the only thing that can catch a lane which quietly built the wrong thing is a test whose lane ownership and run-phase were fixed *before* the lane started.

---

## 0. The rule this file enforces

> **A check that can only pass is not a check.**

The specification states this in four places and this file carries it into the harness:

| Where the spec says it | Line | The form it takes |
| --- | --- | --- |
| Section 53.1, the seeded-canary rule | 4689 | "A run that reports zero findings, including the canary, is a **FAILED** run, not a clean one" |
| AT-102 | 9364 | A reconciliation run finding nothing "is assumed broken, never assumed clean"; raises SIG-13 |
| Section 31.2 / verification contracts | 2793 | "A verification contract that cannot fail is not a contract" — every `verification/contract.yaml` declares a seeded-defect case; if the seeded defect passes, the run FAILED; raises SIG-18 |
| Section 103.1, plan-checker measure | 9797 | "Watch the reason mix, not the rate. **Zero rejections means the gates are not working**" |
| Section 103.9 governance signals | 9906 | Review rejection rate: "Very low may mean rubber-stamping" |
| Section 61.3 | 5270 | "A canary must be exercised, not merely observed… its silence must not be mistaken for a pass" |
| Section 95.4 | 8711 | The activation checklist "is executed for real — including the negative tests — at each threshold, not assumed" |

Consequences, binding on this protocol:

1. **Every automatable AT in this map has a named negative twin** (Section 6 below). The twin is a specific mutation that MUST make the AT fail. An AT whose twin does not fail is a **broken AT**, not a passing system.
2. **The AT runner itself carries a permanent failing sentinel** (Section 7). A run in which the sentinel passes — i.e. a 100%-green run — is a FAILED run.
3. **A skipped AT is never counted as a pass.** The runner has three outcomes, and `NOT_YET_RUNNABLE` is reported separately and loudly.
4. **A phase completion check may not cite an AT that has never been executed against a real mutation.** Section 101 requires every invariant classified `mechanical` to name a live check or an AT- identifier; an AT that has only ever returned green without its twin ever having been run does not satisfy that.

---

## 1. Column vocabulary

**Phase vocabulary** — from Section 98. Foundation phases are written `F1`–`F7` to avoid collision with People-tier `P1`–`P8`.

| Token | Meaning (Section 98) |
| --- | --- |
| `F1`–`F7` | Foundation tier, 98.2. F1 Foundation, F2 Visibility, F3 Registries & Standards, F4 Environments, F5 Verification, F6 Delivery Pipeline, F7 GSD Activation |
| `EH` | Early hardening, 98.3 — built moving from 2–3 products to the full portfolio |
| `SA` | Scale activation, 98.4 — activated on a named trigger, never on the calendar |
| `G1`–`G8` | Governance tier, 98.5 |
| `P1`–`P8` | People tier, 98.6 |
| `COND` | Conditional activation — the capability stands up only if its Section 39.5 trigger fires |

**Lane** — from the FROZEN `PARTITION.md`. `L1` Registries & Contracts (subsystems A, B) · `L2` Pipeline & Evidence (E, F) · `L3` Reconciler & Provisioning (C, D) · `L4` Records, Events & Metrics (I, N) · `L5` Access, Infra & Ops (K, L, M, Q, R) · `L0` Integrator (`contracts/**`, `CODEOWNERS`, `docs/**`, root, `Makefile`).

Markers on the Lane column:

| Marker | Meaning |
| --- | --- |
| `L5†` | The implementing paths fall inside a lane's owned tree, but the **subsystem is not in that lane's declared subsystem list** in `PARTITION.md`. L0 must confirm the assignment before the lane starts. See Section 2. |
| `‡G` `‡H` `‡O` `‡P` | The subsystem has **no owner at all** in the frozen partition. See Section 2. |

**Automatable**

| Code | Meaning |
| --- | --- |
| `A` | Fully automatable. Runs unattended in CI or on the operations VM. No human in the pass path. |
| `H/A` | Hybrid. The mechanism is automatable; exactly one named human step remains (an approval, a reply, a restore into an independent environment). The human step is named in the Gate column. |
| `H` | Requires a human step or is a drill. Cannot be reduced to CI. Executed on a recorded cadence; the record is the evidence. |

**First full pass** — the earliest phase at which the *entire* pass condition as written can be met.
**First partial** — the earliest phase at which a machine-checkable *subset* runs. `—` means nothing runs earlier than the full pass.

---

## 2. Partition coverage gaps — read this before assigning work

`PARTITION.md` assigns subsystems **A, B, C, D, E, F, I, K, L, M, N, Q, R** to the five lanes. Section 99.2 of the spec defines **eighteen** subsystems, A–R. Five are unaccounted for. This is not a criticism of the partition — the partition covers the Foundation tier, which is what the five lanes build — but the acceptance catalogue does not stop at the Foundation tier, and **73 of the 110 tests exercise something outside it**. L0 must resolve the following before the lanes start, because an unowned subsystem produces an AT that nobody can ever run and nobody notices is unrun.

| Subsystem (99.2) | What it is | Paths it would need | Status in FROZEN partition | Recommended resolution — **L0 decision, not mine** |
| --- | --- | --- | --- | --- |
| `G` Plan-checker and Gate 1 tooling | Automatic plan rejection, Gate 1 routing, computed requirement set | none declared | **UNOWNED** | F7 deliverable. No lane owns it. Assign to L2 (it is CI-shaped) or scope it out of the five-lane build and record the decision. Blocks AT-106; partially blocks AT-003, AT-080. |
| `H` Dashboards and views | Grafana provisioned from JSON in git — every surface of Section 92 | `ops-vm/**` (L5-owned) | Subsystem **not** in L5's declared list; paths are | Confirm `H → L5`. AT-097 and AT-098 are *provisioning-file* assertions (D75) and land squarely in `ops-vm/**`. |
| `J` Background machine layer | Hermes cage, egress override, systemd stop unit, draft-PR-only verification | `infra/**`, `ops-vm/**` (L5-owned) | Subsystem **not** in L5's declared list; paths are. **F3 deliverable** — the cage stands up in Phase 3 | Confirm `J → L5`. AT-108 and AT-109 are unrunnable until this is assigned. Note the go/park benchmark in F3 gates the whole subsystem. |
| `O` Governance registries and jobs | Exception lifecycle with renewal counting, policy stages, pattern detector, tool register, exit checklists | `registries/**` (L1), `ops-vm/**` (L5) | **Split, unowned** | Split explicitly: schemas + registry files → L1; scheduled jobs → L5. Blocks AT-038, AT-040, AT-045, AT-031. |
| `P` People intelligence engine | Capacity, bandwidth, overload detection, evidence bundles, succession | none declared | **UNOWNED** | Entire People tier. Out of five-lane scope. Record as such — do not let a lane silently absorb it. Blocks 40 tests. |

**Acceptance test locations are settled by REG-015:** harness lives at `verification/acceptance/**`. See `contracts/harness/pairs.tsv` for the canonical test-to-task mapping.

---

## 3. Mapping — Section 100.1 Extensibility (AT-001 → AT-016)

> **FD-078 (2026-09-08):** This table is the canonical authority for AT→owner-lane assignment.
> 16 rows previously disputed with `protocol/00` are resolved: protocol/02 prevails in all cases.
> L3 owns all authority_delta ATs (owns `validators/drift/**`).

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-001 | `create-product` scaffold; every surface enumerates from the registry; no product list anywhere | L3 (D) | L1 (A,B), L4 (I), L5† (H) | `G3` | `F3` | `A` | Scaffold + registry enumeration + the repo-wide "no hard-coded product list" grep run at F3. Full pass needs **economics** picking the product up — `economics.yaml` product entries land at **G3** (attention and portfolio economics) |
| AT-002 | `add-person`; role assignment, capability grant, new-person lifecycle; capacity profile, ramp curve, Insufficient Evidence initialise | L3 (D) | L1, L5 (L) | `P2` | `F3` | `A` | Registry + reconciled access half runs at F3. **Gate: P1** for capacity profile and ramp curve, **P2** for the Insufficient Evidence state (framework registry) |
| AT-003 | Acting Team Lead pre-designated, dormant capability activates by configuration; Gate 1 and escalation continue | L1 (A) | L3 (C), L5 (L), ‡G | `EH` | `F3` | `H/A` | Acting Team Lead designation is an **Early hardening** deliverable (98.3). Human step: a real Gate 1 approval must resolve to the acting holder — subsystem `G` is **unowned**, see Section 2 |
| AT-004 | Permanent Team Lead change; role and assignment change only, no workflow redesign; new acting designated at once | L3 (D) | L1 | `EH` | `F3` | `A` | `change-role` is an Early hardening deliverable (98.3, "the remaining provisioning operations"). F3 partial: the assignment-registry edit alone |
| AT-005 | QA engineer becomes Team Lead; effective date, recalculated capabilities, segmented performance period, no retroactive evaluation | L1 (A) | L3 (D), ‡P | `P2` | `EH` | `A` | Role/capability half at EH with `change-role`. **Gate: P2** — the Performance Framework Registry and effective dating. Segmentation semantics are the same machinery AT-078 tests |
| AT-006 | Two QA members join; QA role capacity scales; no single-QA assumption exists anywhere | L1 (A) | ‡P | `P1` | `F3` | `A` | The "no single-QA assumption exists **anywhere**" clause is a static repo-wide assertion runnable from **F3** and worth running from F3, every merge. Capacity scaling itself is **P1** |
| AT-007 | A new role is introduced; role profile plus performance-framework mapping; no architecture change | L1 (A) | ‡P | `P2` | `F3` | `A` | `roles.yaml` entry + derived Teams at F3. **Gate: P2** for the framework mapping half |
| AT-008 | Temporary specialist/contractor: scoped, dated, capability-limited; reconciliation revokes on the end date with no human action | L3 (C) | L1 (B), L5 (L) | `SA` | `F3` | `A` | Mechanism ships early — mandatory end dates for non-employees is a **subsystem B** validator (99.2) and expiry revocation is in **reconciliation v0, F3**. `SA` only because 98.4 activates the contractor model on "first contractor". **Run the mechanism at F3 with a synthetic contractor; do not wait for a real one** |
| AT-009 | New technology stack conforms to the operating interface for its conformance profile — eight commands, three endpoints, verification contract | L2 (E) | L1 (product schema) | `F5` | `F4` | `A` | F4 gives the eight commands and `make parity`; the verification contract lands at **F5**. Whole test is a conformance runner against a deliberately foreign stack |
| AT-010 | One product, three repositories: Product and Repository are separate; one contract, one owner set, one dashboard entry; protection on all repos | L1 (A) | L3 (D), L2 (E) | `F4` | `F3` | `A` | Schema separation + provisioning at F3; CI and protection applied across all three repos verified at **F4** |
| AT-011 | AI provider changes; approved runtime list is configuration; GSD, verification, GitHub, CI, production, ownership, review routing all unchanged | L5 (K) | L1 | `F3` | `F1` | `A` | F1 authors `platform.yaml` and the approved-runtime list; F3 makes it enforced configuration. The "unchanged" clause is a `git diff --stat` assertion over the declared surfaces |
| AT-012 | Team doubles; capacity, allocation and health models scale without redesign | ‡P | L1 | `P1` | `F3` | `A` | F3 partial: doubling `people.yaml` must produce no schema, workflow or dashboard edit. **Gate: P1** for the capacity and allocation models themselves |
| AT-013 | Product count doubles; capacity model and staffing forecast scale through the product registry alone | ‡P | L1, L4 | `G5` | `F3` | `A` | F3 partial: registry-only scaling, zero workflow edits. **Gate: G5** — the capacity forecast job, itself gated on two quarters of G3 attention data (calendar gate, 98.1) |
| AT-014 | Performance framework replaced completely; capacity, health, evidence pipeline, dashboards, decision support unaffected | ‡P | L1 | `P8` | `P2` | `A` | **Gate: P2** for a first framework version to replace, **P8** for framework evolution. P8 additionally gated on "two full review periods of P4 evidence" — a calendar gate no build acceleration compresses (98.1) |
| AT-015 | A KPI is removed; historical periods preserved with the old KPI, future periods use the new configuration | ‡P | L4 (records) | `P8` | `P2` | `A` | **Gate: P8**. The immutable-history rules this leans on are a **G1** deliverable |
| AT-016 | Second Team Lead and product domains; only `topology.yaml` changes; zero contract, workflow or dashboard edits; escalation resolves through topology | L1 (A) | ‡O | `G7` | — | `A` | **Gate: G7** — `topology.yaml` with dormant domains. 98.5 requires the test pass "with domains both dormant and simulated active, with zero product contract edits" — the zero-edit clause is a `git diff` assertion and is the falsifiable half |

---

## 4. Mapping — Section 100.2 Lifecycle (AT-017 → AT-022)

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-017 | A person leaves: exit lifecycle, revocation, orphan detection at blocking severity, blocking orphans undismissable, succession, evidence archived, history retained | L3 (C,D) | L1, L4, ‡P | `P7` | `F3` | `H/A` | **F3 gives the load-bearing half**: reconciliation v0 ships expiry revocation *and* orphan detection at blocking severity (98.2 F3). `remove-person` is **EH**. **Gate: P7** for succession readiness and **P4** for the performance-evidence archive. Human step: the departure decision itself |
| AT-018 | A temporary assignment expires; reconciliation removes it with no human action; access revoked, capacity recalculated | L3 (C) | L1, ‡P | `F3` | — | `A` | Runs at F3 against reconciliation v0. The capacity-recalculation clause is **P1**; run the revocation half from F3 and record the capacity clause as gated |
| AT-019 | A product splits; two contracts emerge; original resolves to successor or sunset, never ambiguous; historical evidence preserved under the original identity | L1 (A) | L4 (records), L2 | `SA` | — | `H/A` | **Gate: SA** — 98.4 activates split/merge on "first split or merge". Human step: the split decision and the successor-vs-sunset call. The *ambiguity* clause is automatable and is the falsifiable half: a contract resolving to neither must fail validation |
| AT-020 | Products merge; verification contracts merged, never dropped; both histories queryable under original identities | L1 (A) | L2 (E,F), L4 | `SA` | — | `H/A` | **Gate: SA**. Invariant 5 ("Verification contracts are merged, never dropped, when products merge") is the mechanical half and is CI-checkable the moment two contracts exist |
| AT-021 | Permanent ownership change under `reviewer-matrix-change`; recorded as a decision; Founder-view notification generated automatically; **no** Founder approval step exists | L1 (A) | L4 (records/decisions), L5 (R) | `F3` | — | `H/A` | Runs at F3: assignment registries are populated and the `record-decision` CLI exists (99.2 named tools). Human step: the Team Lead executes it. The "no Founder approval step exists or is required" clause is a **negative assertion over the workflow set** and is fully automatable |
| AT-022 | Founder continuity: standing delegation activates; second Owner or escrowed break-glass credential **verified usable**; account inventory current; Layer B contingency access functions | L5 (L,Q) | L1 | `F1` | — | `H` | F1's completion check already requires "a second organisation Owner or an escrowed break-glass Owner credential… with a named escrow custodian". Section 39 is explicit: **"Verified by periodic drill, not assumed."** An inventory match is not a functional test — the escrowed credential must authenticate and each escrowed key must decrypt a canary blob. Layer B contingency clause is gated on **P2** |

---

## 5. Mapping — Section 100.3 Platform (AT-023 → AT-035, AT-101 → AT-103)

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-023 | GSD version change; canary set verifies first; products run different pinned versions via `platform_compatibility` | L2 (E) | L1 (`platform.yaml`) | `EH` | `F7` | `A` | F7 installs GSD at a pinned tag. **Gate: EH** — "Platform change process and canary set… needs enough products for a canary to be meaningful" (98.3). Per 61.5 the canary must be *exercised*: a `workflow_dispatch` run of `ci.yml` and `build.yml` plus a staging deploy, recorded on the manifest |
| AT-024 | A shared CI workflow breaks; impact analysis, canary catches it, rollback reverts the workflow tag; pinned consumers unaffected | L2 (E) | L1 | `EH` | — | `A` | **This test is intrinsically a negative test** — you break the workflow on purpose. It is the cheapest high-value AT in the catalogue and should run on every workflow-library release |
| AT-025 | A platform contract schema changes; both versions supported; canary migrates first; deprecation deadline published; no simultaneous fleet migration | L1 (A,B) | L2 | `EH` | — | `A` | **Gate: EH** — "Versioned contracts (`contract_version` enforcement)… needs a reason to change a schema" (98.3) |
| AT-026 | A platform change progresses pilot → rollout → fleet with per-stage verification and a working, tested rollback | L2 (E) | L1 | `EH` | — | `A` | The falsifiable clause is *tested* rollback. An untested rollback is the platform-tier analogue of an untested backup (invariant 3) |
| AT-027 | A new platform policy propagates from `policies.yaml` and the reusable workflows without hand-editing twenty product files | L1 (A) | L2 (E), ‡O | `G2` | — | `A` | **Gate: G2** — `policies.yaml` is populated at G2 (98.5). Falsifiable clause: the propagation must show **zero per-product file edits** in the diff |
| AT-028 | GitHub unavailable for hours: Degraded Engineering Mode; products keep serving; local work continues; state reconciled on recovery, never assumed | L5 (M) | L2, L0 (docs) | `F6` | — | `H` | Drill. Requires a simulated outage and human participation. F6 is the earliest honest point — a pipeline must exist to degrade. The "reconciled on recovery, never assumed" clause maps to Section 46.1's outage-recovery gate (its six-step "ON RECOVERY" list, line 4121), mirrored by 53.7's gap procedure, which re-runs reconciliation **including the seeded canary** (53.7, line 4750) |
| AT-029 | Entire control plane unreachable; all products keep serving; a production rollback still executable via the documented manual path | L2 (E) | L5, L0 (docs) | `F6` | — | `H` | Drill. Human executes the manual rollback. F6 completion check already requires "a deliberate rollback succeeded in staging" — AT-029 is that rollback executed **with the control plane switched off** |
| AT-030 | A control-plane tool is disabled; product workflows continue; `.planning/`, verification contracts and product contracts remain readable and usable without it | L5 (K,Q) | L2, L1 | `F7` | `F5` | `A` | F5 partial: contracts readable without tooling. Full pass at F7 once `.planning/` exists |
| AT-031 | A named external tool is removed; boards, records and metrics continue from the OS's own stores; the integration's declared exit condition executes cleanly | L5 (Q) | L4 (N), ‡O | `G8` | — | `A` | **Gate: G8** — the tool register and retirement path (98.5). Note the carve-out: the git host is **exempt** per Section 62.5; do not let a lane widen this test to the substrate |
| AT-032 | Self-observability: the OS detects and reports a failure in its own reconciliation, health job or dashboard freshness | L5† (H,M) | L3 (C), L4 (I) | `G1` | `F3` | `A` | **Gate: G1** — `os-health.yaml` and the health computation job. F3 partial: reconciliation's own absence for a cycle is detectable the moment reconciliation is scheduled. The independent control verifier (53.1, line 4691) makes "its own absence for one cycle is Level 5" the falsifiable clause |
| AT-033 | No auto-loosening: reconciliation presented with a **stricter**-than-declared production control raises it for human review and does not relax it | L3 (C) | L5 (L) | `EH` | — | `A` | **Gate: EH** — auto-repair Level 3 is Early hardening (98.3); detect-only reconciliation at F3 cannot loosen anything, so running this at F3 proves nothing. **This is the single most important negative test in the reconciler**: the auto-repair path is described in 98.3 as "the riskiest code in the system" |
| AT-034 | Governance layerability: the delivery core runs with the removable governance artifacts removed; reconciliation engine and exception registry are **core-resident and never removed** | L0 | all lanes | `F7` | `F5` | `A` | Run at F7 and **re-run at the completion of every G phase** — this is the test that stops the governance tier from silently becoming load-bearing. The removable set is enumerated: `os-health.yaml`, `policies.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml`, the scenario calculator, the maturity-assessment and forecast jobs |
| AT-035 | The scheduled organisation export restores to an independent environment, each data class through its own recorded mechanism; Projects boards via GraphQL dump | L2 (E) | L5 (M) | `EH` | `F2` | `H/A` | Export job is **EH** (98.3, "Organisation export job… needed before the first restore test, within the first quarter"); F1's completion check requires the first run be *scheduled* in F2 or the absence recorded as a dated accepted risk (D80). Human step: standing up the independent environment. Restore recorded on the rolling 90-day discipline |
| AT-101 | Three simultaneous SEV-1s; three Primary Responders lead independently; escalation coordinates rather than repairs; Founder informed not dispatching; a doubled responder reassigns to Backup and it is recorded as a **capacity incident** | L1 (A) | L5 (R), L4 (records) | `F6` | `F3` | `H` | Drill with three humans. F3 partial and fully automatable: the responder registry must **fail validation** if any person is Primary Responder on two products without a distinct Backup — that static check is what makes the drill survivable |
| AT-102 | **The seeded reconciliation canary.** Every run must find the planted drift; a run reporting zero findings is a FAILED run, raises SIG-13, triggers the gap procedure | L3 (C) | L1 | `F3` | — | `A` | Runs from **F3**, the moment reconciliation v0 exists, and on **every run forever after**. Per 53.1 each run also records per-registry comparison counts so a silently narrowed comparison is itself visible drift. This is the keystone AT of the whole catalogue and the model for Section 6 below |
| AT-103 | Production restore without hand-held credentials: `restore-production.yml` generated from the template, executes end to end, no credential handed to or typed by a human; run, authorisation and result recorded | L2 (E) | L5 (L, secret tiers), L4 (records) | `F6` | — | `H/A` | F6 configures backup and performs one recorded restore test. Human step: the **exceptional-authorisation** approval. Falsifiable clause: the workflow must fail closed if the scoped run identity is absent — and a human typing a credential must be structurally impossible, not merely discouraged |

---

## 6. Mapping — Section 100.4 Governance (AT-036 → AT-051, AT-104 → AT-107)

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-036 | A temporary access exception expires; reconciliation revokes it with no human action | L3 (C) | L1 (B), ‡O | `F3` | `F1` | `A` | F1 already requires the minimal `exceptions.yaml` validator (expiry, owner, deactivation trigger) active in control-plane CI, **rejecting a deliberately malformed exception** — the negative test is written into the phase gate. Full revocation at F3 |
| AT-037 | A failed exception becomes **Blocking** drift on its expiry date and appears on the Founder view | L3 (C) | L5† (H), ‡O | `G3` | `F3` | `A` | Blocking-drift half runs at F3. **Gate: G3** — "the full Founder view (Section 93)" is a G3 deliverable |
| AT-038 | A same-scope exception reopened counts as a **renewal**; a fresh ID does not reset the count | ‡O | L1, L3 | `G2` | — | `A` | **Gate: G2** — "exception lifecycle with auto-expiry and renewal counting" (98.5). Subsystem `O` is **unowned** — see Section 2. The falsifiable clause is precise and easy: close and reopen the same scope under a new ID; if the counter reads 1, the test failed |
| AT-039 | A bootstrap exception carries an expiry and an activation checklist; when the headcount trigger is met or the expiry passes, the gate arms or the exception surfaces as Blocking drift — it cannot lapse silently | L1 (A) | L3 (C), ‡O | `F3` | `F1` | `A` | F1 records bootstrap exceptions for every gate headcount cannot satisfy (98.2). F3 gives the drift detector. 95.4 supplies the arming thresholds and their negative tests verbatim — reuse them, do not re-derive them |
| AT-040 | Pattern to work: a third occurrence of a failure class produces a pattern candidate and a tracked remediation item with a closure condition | ‡O | L4 (I) | `G4` | — | `A` | **Gate: G4**, itself gated on "realistically two quarters of G1 data" (98.5). Calendar gate — cannot be compressed. Seed three synthetic occurrences to prove the detector fires; a detector that has never fired is unproven |
| AT-041 | The Founder view presents **ranked attention with decisions required, and no activity feed** | L5† (H) | L4 (I) | `G3` | — | `A` | **Gate: G3**. The "no activity feed" clause is a structural assertion over the provisioned dashboard JSON and is the falsifiable half |
| AT-042 | A future bottleneck is projected with a horizon ≥ 4 weeks before it materialises, and the projection is **retrospectively scored** | ‡P | L4 (I) | `G5` | — | `A` | **Gate: G5**, gated on ≥ two quarters of G3 attention data (98.5). Retrospective scoring is what makes this falsifiable — an unscored forecast cannot be wrong, and G5's exit criterion is "forecast accuracy scored and reported honestly" |
| AT-043 | QA sees projected verification demand for the next 6 weeks by product | ‡P | L4 (I) | `G5` | — | `A` | **Gate: G5** — the verification demand forecast for QA. Same two-quarter calendar gate |
| AT-044 | A lifecycle decision is evidenced with **actual attention-hour data**, not impression | L4 (I) | ‡O | `G3` | — | `A` | **Gate: G3** — the attention ledger with the Section 97.4 derivation rules. Falsifiable clause: a decision record citing no ledger rows must not validate as evidenced |
| AT-045 | Bureaucracy check: the quarterly review retires at least one policy, metric or automation — **or explicitly records why nothing warranted retirement** | ‡O | L0 | `G8` | — | `H` | **Gate: G8**, plus one elapsed quarter. 98.5 states it flatly: "A review that only adds is a failed review." Human judgment; the record is the evidence |
| AT-046 | Every Section 103 success measure has a recorded pre-Phase-1 baseline, or is explicitly marked **unbaselined** | L4 (I) | L0 | `G1` | `F1` | `A` | The banded self-estimates are captured **before F1** (103.14); G1 verifies and re-records them against early instrumented data. Machine check: iterate the Section 103 measure set, assert `baseline` or `unbaselined` present on every row. "A measurement programme with no baseline can prove nothing" (98.5) |
| AT-047 | Detection-to-response latency recorded per incident; a product whose declared `coverage_window` is not fully covered by active rota members' accepted windows **fails contract validation** | L1 (B) | L4 (I) | `G3` | `F3` | `A` | **The contract-validation half is F3 and fully automatable** — subsystem B's "24x7-without-rota blocker" (99.2). Latency measurement is **G3** and needs real incidents. Do not let the lane ship only the measurement half |
| AT-048 | A customer report enters the per-product intake channel, is triaged into the Section 41 defect taxonomy, and produces a support-to-engineering handoff record; first response measured against Section 22 severity targets | L4 (N) | L5 (R) | `EH` | — | `H/A` | **Gate: EH** — "Support intake and triage per product… needed as soon as customers can report defects" (98.3). Human step: the triage judgment. Ingest, clock and handoff record are automatable |
| AT-049 | A product declaring `ai_runtime_dependency` without an evaluation suite under `verification/` **fails CI**; a pinned-model change cannot merge without the suite passing | L1 (B) | L2 (E), L5 (K) | `F5` | — | `A` | **Gate: F5** — "Where the product declares an AI runtime dependency, the evaluation suite lands under `verification/` here" (98.2). Written as a negative test already; implement it as one |
| AT-050 | Spend outside `infrastructure.monthly_budget_band` raises a **Red** health signal and can be classified as a cost incident with a named owner | L4 (I) | L1, L5† (H) | `G1` | `F3` | `A` | Budget band lands in every contract at F3 (98.2). **Gate: G1** for the health signal itself. Falsifiable clause: inject a synthetic spend figure outside the band and require Red |
| AT-051 | A not-yet-onboarded product carries a minimal ruleset, accepted-risk record and named deadline; a breached deadline surfaces as drift; adoption-health signals make partial adoption visible | L1 (A) | L3 (C) | `F2` | — | `A` | **Gate: F2** — pre-onboarding blocks written for every live product not yet in the pipeline (98.2). Falsifiable clause: back-date a deadline; drift must appear. Adoption-health signals are G1-shaped but the deadline breach is not |
| AT-104 | An inbound support email becomes a structured support-board record with the first-response clock anchored to the **message's received timestamp** (D80); the record closes only when the **customer loop** is closed | L4 (N) | L5 (R) | `EH` | — | `H/A` | Support email-ingest hook (99.2 named tools, subsystems N,R). Human step: the reply to the customer. Falsifiable clause and the whole point of the test: **a fix shipped with no reply must not close the record** — assert closure is refused |
| AT-105 | A customer deletion request executes through the deletion runbook via CI with completion evidence — four timestamps, named executor, subprocessor propagation checklist — inside `deletion_sla_days` | L2 (E) | L4 (records), L1 | `SA` | — | `H/A` | **Gate: SA** — "Data and privacy extension: first regulated-data customer requirement" (98.4). Human step: the named executor and the subprocessor checklist. Evidence completeness is automatable: a record missing any of the four timestamps must fail validation |
| AT-106 | A Gate 1 submission notifies its resolved approver as a **push** event; a breached turnaround auto-raises Blocked routed to the escalation role — a capacity signal, never a personal one; re-request to an active `plan_approval_delegate` or Acting Team Lead is a recorded routing event | ‡G | L5 (R), L1 | `F7` | — | `H/A` | **Gate: F7** — Gate 1 goes live ("a first plan passes the plan-checker and is approved at Gate 1"). **Subsystem `G` is unowned — see Section 2.** Human step: the approval itself. Notification, breach detection and routing are automatable |
| AT-107 | A regression detected by the AI-eval scheduled runner creates the category-five incident, raises **SIG-42**, and blocks adoption of the new model pin until the suite passes or a recorded exception accepts the change | L5 (K) | L2 (E), L4 (`records/eval/`) | `F5` | — | `A` | AI-eval scheduled runner is a named tool under subsystem K (99.2). Evaluation suites land at F5. Falsifiable clause: **plant a regression in a fixture suite; if adoption is not blocked, the runner is broken** |

---

## 7. Mapping — Section 100.5 People (AT-052 → AT-088)

Every test in this section exercises subsystem **P**, which has **no owner in the frozen partition** (Section 2). Thirty of the thirty-seven cannot run until the People tier. Six have a *static, negative, build-time-checkable* half that must be wired from **F3** and run on every merge — those six (AT-071, AT-074, AT-075, AT-081, AT-083, AT-085 — the same six named in Section 11.5's merge-train gate) are the only People-domain protection the five-lane build actually gets. Five are marked **`STATIC-F3`** below in the First-partial column; AT-075 is the sixth, running a full pass at F3 rather than a partial.

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-052 | Team capacity matches declared calendar, leave, ramp, reserve and operational commitments | ‡P | L4 (I) | `P1` | — | `A` | **Gate: P1**, itself gated on the G3 attention ledger |
| AT-053 | Per-person capacity reflects ramp, leave and operational commitments | ‡P | L4 | `P1` | — | `A` | **Gate: P1** |
| AT-054 | A bandwidth state is emitted **with its composition**, never a single opaque number | ‡P | L4 | `P1` | — | `A` | **Gate: P1**. Falsifiable clause: a bandwidth output with no composition must be rejected by schema |
| AT-055 | Sustained team overload detected multi-signal, multi-window only; a single spike does not trigger; output is a team-level signal, never a set of individual signals | ‡P | L4 | `P3` | — | `A` | **Gate: P3**. Two negative twins required: a single spike must **not** fire, and the emitter must be structurally unable to produce per-person signals here |
| AT-056 | Sustained under-utilisation diagnosed — cause identified **before** any signal is emitted; presented as a planning signal, never underperformance | ‡P | L4 | `P3` | — | `A` | **Gate: P3**. Falsifiable clause: an undiagnosed under-utilisation must emit nothing |
| AT-057 | Team constraint distinguished from person issue — correct variance classification per Section 80 | ‡P | L4 | `P4` | — | `A` | **Gate: P4**, hard-gated on the Layer B separation delivered at P2 (98.6 sequencing rule) |
| AT-058 | Each role evaluated against its own expectations; **no cross-role comparison exists** | ‡P | L1 | `P2` | `F3` | `A` | **Gate: P2**. `STATIC-F3`-adjacent: the absence of any cross-role comparison path is assertable over `roles.yaml` consumers from F3 |
| AT-059 | An evidence bundle is produced with instrumentation status stated per KPI | ‡P | L4 | `P4` | — | `A` | **Gate: P4**; blocked until AT-089, AT-091, AT-097, AT-098 pass and invariant 109 holds (98.6) |
| AT-060 | All Section 80 context checks present and visible in the bundle | ‡P | — | `P4` | — | `A` | **Gate: P4**. Falsifiable clause: a bundle missing any Section 80 check must fail generation, not warn |
| AT-061 | The system **refuses** to emit a person-directed signal from one metric; utilisation alone cannot generate a performance concern | ‡P | — | `P4` | — | `A` | **Gate: P4**. Pure negative test — feed one metric, assert refusal |
| AT-062 | A shared-cause pattern is classified systemic; individual attribution suppressed and the systemic classification shown, **even where an individual metric has worsened** | ‡P | ‡O | `P4` | — | `A` | **Gate: P4**. The "even where worsened" clause is the twin: construct exactly that case |
| AT-063 | Team health issue detected while individual metrics look healthy → team-level alert raised | ‡P | L4 | `P3` | — | `A` | **Gate: P3** |
| AT-064 | Individual concern detected while the team is healthy → individual signal with confidence and context, only when the pattern persists across products or periods | ‡P | L4 | `P4` | — | `A` | **Gate: P4**. Twin: a single-period, single-product pattern must **not** produce a signal |
| AT-065 | Promotion candidate detected: signal with next-level expectations and evidence; **no automatic promotion** | ‡P | — | `P5` | `F3` | `A` | **Gate: P5**. The "no automatic promotion" half is `STATIC-F3` — see AT-071 |
| AT-066 | Coaching signal framed as a performance concern requiring Founder review | ‡P | — | `P5` | — | `A` | **Gate: P5** |
| AT-067 | Staffing candidate: diagnosis names the constraint type; a Hiring Decision Evidence Pack produced when the constraint persists | ‡P | — | `P6` | — | `A` | **Gate: P6** |
| AT-068 | Non-hiring remedies evaluated and recorded **before** any hire recommendation; where reallocation suffices, a rebalance signal is produced instead | ‡P | — | `P6` | — | `A` | **Gate: P6**. Twin: construct a case reallocation solves; a hire recommendation appearing is a failure |
| AT-069 | An overload/under-load pair produces a candidate with capability fit and onboarding cost stated | ‡P | — | `P6` | — | `A` | **Gate: P6** |
| AT-070 | Improvement or exit evidence bundle generated with an explicit human-decision statement | ‡P | — | `P5` | — | `A` | **Gate: P5**. Falsifiable clause: a bundle lacking the human-decision statement must fail generation |
| AT-071 | **No automated people action exists**: no code path to an automated improvement plan, termination, promotion, compensation change or formal warning; attempted configuration fails validation; no workflow permits the Team Lead or automation to finalise a formal personnel action | ‡P | L1, L2, L5 | `P5` | **`STATIC-F3`** | `A` | **This is a standing build-time invariant, not a People-tier test.** Wire it at **F3** as a repository-wide prohibited-symbol check plus a schema negative test, and run it on **every merge in every lane** thereafter. Full pass at P5 only because P5 is where the decision-support surfaces exist to prove absence *within them*. Backs invariant 105 |
| AT-072 | Before the evidence window elapses the answer is **Insufficient Evidence**, and it generates no negative signal | ‡P | — | `P4` | — | `A` | **Gate: P4**. Twin: query inside the window and assert both the state *and* the silence |
| AT-073 | Overrides recorded — decision, reason, evidence, decision-maker, date; evaluated in aggregate without blame; the system continues unchanged | ‡P | L4 (records) | `P5` | — | `A` | **Gate: P5**. Record completeness is schema-checkable the moment the record type exists |
| AT-074 | Every "sustained" threshold is configurable and refittable **without code change** | ‡P | — | `P3` | **`STATIC-F3`** | `A` | `STATIC-F3`: assert no numeric sustained-threshold literal appears outside the configuration files. Full pass at P3 with the calibrated thresholds |
| AT-075 | **No surveillance metrics**: banned measurements absent from the schema and **rejected if introduced** | L1 (B) | L4 (I) | **`F3`** | — | `A` | **Runs in full at F3 and is one of only two People-domain tests the five-lane build can fully pass.** Written as a negative test: introduce a banned field and require rejection. Owned by L1's validators, enforced against L4's metric schemas |
| AT-076 | Hiring scenario comparison shows current state, projected state and delta with assumptions and ramp | ‡P | ‡O | `G6` | — | `A` | **Gate: G6** — the scenario calculator (Section 72), itself gated on G5 |
| AT-077 | Every person and KRA is mapped verbatim, marked outstanding, or marked **Not defined** in the framework version in force | ‡P | L1 | `P2` | — | `A` | **Gate: P2**. 98.6: P2 is completed by reading the framework source directly, never by inferring from summaries |
| AT-078 | Framework version change is non-retroactive; effective date honoured; historical periods stay on their original version; a mid-period change segments the period | ‡P | L4 | `P8` | `P2` | `A` | **Gate: P8**, gated on ≥ two full review periods of P4 evidence (calendar gate, 98.6) |
| AT-079 | A product complexity change updates workload context for all affected people and appears in their evidence | ‡P | L1 | `P4` | `F3` | `A` | Complexity field lands in the contract at F3. **Gate: P4** for the evidence half |
| AT-080 | Team Lead capacity monitored: Gate 1 latency and planning queue tracked; delegation and topology remedies proposed **before** any coaching framing | ‡P | ‡G, L4 | `G5` | `F7` | `A` | Gate 1 latency is measurable from **F7** but requires subsystem `G` (**unowned**). Bottleneck diagnosis chain is **G5**. Twin: assert a coaching framing cannot be emitted before the remedy set is exhausted |
| AT-081 | Capability maturity grants **no** permission — no permission change occurs from a maturity assessment | ‡P | L5 (L) | `P7` | **`STATIC-F3`** | `A` | `STATIC-F3`: assert no code path connects maturity data to the access model. Maturity assessment itself is **G8**; succession/capability is **P7** |
| AT-082 | QA capacity monitored: verification demand vs capacity tracked; automation and rebalance remedies first; **verification depth never traded for throughput** | ‡P | L4 | `G5` | — | `A` | **Gate: G5** (verification demand forecast). Backs invariant 6 |
| AT-083 | Founder capacity remains separate: **no Founder productivity score exists**; Founder-decision latency measured as a system-constraint metric, never a performance metric | L4 (I) | ‡P | `G5` | **`STATIC-F3`** | `A` | `STATIC-F3`: assert no metric keyed to the Founder identity exists in any productivity or performance namespace. Latency-as-constraint half is **G5** (bottleneck diagnosis chain including Founder-decision latency) |
| AT-084 | Rework from machine-drafted work surfaces as a **task-class** quality signal, not an individual penalty | ‡P | L5 (J), L4 | `G6` | — | `A` | **Gate: G6** — background-layer output-value measurement. Twin: assert the signal cannot be keyed to a person |
| AT-085 | Accepted-PR yield and review cost per accepted PR measured; **volume is never counted for any person** | L4 (I) | ‡P | `G6` | **`STATIC-F3`** | `A` | `STATIC-F3`: assert no per-person volume metric exists in any schema — this is a sibling of AT-075 and should share its validator. Measurement half is **G6** (automation ledger) |
| AT-086 | Where raw metrics mislead, **context is displayed instead of a single score** | ‡P | L5† (H) | `P4` | — | `A` | **Gate: P4**. Assertable over the provisioned Layer B dashboard JSON |
| AT-087 | A KPI the system lacks evidence for is marked **Not yet instrumented** or **Requires human input** — no proxy is invented | ‡P | L1 | `P2` | — | `A` | **Gate: P2**. Twin: present an uninstrumented KPI and assert the marker rather than a computed value. This is the Section 52.2 arming discipline applied to people data |
| AT-088 | Source re-read failure is safe: existing verified content preserved; **nothing downgraded to pending** | ‡P | L1 | `P2` | — | `A` | **Gate: P2** — a binding P2 sequencing rule (98.6): "Captured content is preserved verbatim and never downgraded on a failed re-read." Pure negative test: simulate a failed re-read, assert zero downgrades |

---

## 8. Mapping — Section 100.6 Access (AT-089 → AT-100, AT-108 → AT-110)

Twelve of these fifteen are gated on the **Layer B datasource separation**, delivered by subsystem **L** at People-tier phase **P2**. Section 98.6 makes the gate explicit and binding:

> "**P4 must not begin before the Layer B datasource separation is implemented and verified.** It is a P2 deliverable, never an assumption; *verified* means **AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds**."

Those four tests are therefore not merely gated by P2 — they are P2's **exit criteria** and P4's **entry gate**. L0 must treat a green result on those four as a tier-crossing decision, and must require their negative twins before accepting it.

| ID | What it exercises | Lane | Also | First full pass | First partial | Auto | Gate / note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AT-089 | Peers and general dashboards cannot reach Layer B data **by any path** | L5 (L) | L5† (H) | `P2` | — | `A` | **Gate: P2 — Layer B datasource separation.** One of the four P4 entry-gate tests. Backs invariant 109 |
| AT-090 | Individual people intelligence is Founder-only at application **and** datasource layers; no delegate exists; an assignment granting `people-intelligence` **fails validation**; self-view is out of scope | L5 (L) | L1 (B) | `P2` | `F3` | `H/A` | **The validation half is `F3` and automatable** — the assignment validator lives in L1. Datasource half is P2. Human step: the Section 90.3 host-level accepted-access record — its holder named in the asset inventory, its compensating audit trail shipping off-host, its review in cadence. The test text warns against exactly the failure this protocol exists to prevent: "a reinterpreted access-control test is how the boundary erodes." **Do not let a lane widen the scope carve-out** |
| AT-091 | Access follows the **capability**, not the role name; granting the dated delegate assignment opens access through reconciliation; revoking or expiring closes it the same way | L5 (L) | L3 (C), L1 | `P2` | `F3` | `A` | **Gate: P2.** One of the four P4 entry-gate tests. F3 partial: the grant/expire round trip through reconciliation is testable against a stub datasource |
| AT-092 | The Team Lead cannot reach the Founder people views — denied at **both** dashboard and datasource level | L5 (L) | L5† (H) | `P2` | — | `A` | **Gate: P2.** "Both" is the falsifiable word: two independent negative assertions, not one |
| AT-093 | The Team Lead sees operational constraints only — bottlenecks, capacity, allocation visible; promotion, improvement-plan and exit information not | L5 (L) | ‡P | `P4` | `P2` | `A` | **Gate: P4** — the excluded categories must exist before their exclusion is provable. Backs invariant 107 |
| AT-094 | Allocation works fully without Layer B, using the three-state `allocation_state` field | L1 (A) | L5 (L) | `P2` | — | `A` | **Gate: P2** — three-state field handling is an explicit P2 deliverable. Falsifiable clause: run allocation with the Layer B datasource **switched off** and require success |
| AT-095 | The individual self-view: a person sees their own evidence, KRA/KPI mapping and capability matrix as a **generated per-person document**, and nothing about peers | L5 (L) | ‡P | `P2` | — | `A` | **Gate: P2** — the generated per-person self-view document is a P2 deliverable. Backs invariant 108 |
| AT-096 | Employees cannot access each other's data — any attempt denied | L5 (L) | — | `P2` | — | `A` | **Gate: P2.** Pure negative test |
| AT-097 | **No people datasource in the shared Grafana instance** — no datasource entry and no dashboard reference exist there, verified **in the provisioned configuration**, not inferred from panel visibility (D75) | L5† (H,M) | L5 (L) | `P2` | — | `A` | **Gate: P2.** One of the four P4 entry-gate tests. D75 forbids the easy version of this test: a grep over provisioning JSON in git, not a look at a rendered dashboard. Paths land in `ops-vm/**` — confirm the `H → L5` assignment first (Section 2) |
| AT-098 | The Founder-only instance is **separately credentialed** — a shared-instance login grants nothing there; a direct query without that instance's credential is denied (D75) | L5 (L,M) | — | `P2` | — | `A` | **Gate: P2.** One of the four P4 entry-gate tests. Two negative attempts plus one positive: shared login denied, uncredentialed query denied, correct credential succeeds |
| AT-099 | The Founder answers the Section 104 people questions from **one** restricted view | L5 (L) | ‡P | `P4` | — | `A` | **Gate: P4** — the evidence the view renders must exist first |
| AT-100 | Conduct evidence held separately and inaccessible to performance-review pack generation; the complaint path functions when the subject is the Team Lead or the Founder; suspension reuses `access_status: suspended` | L5 (L) | L1 (A) | `P2` | `F3` | `H/A` | `access_status: suspended` is an L1 schema value testable at **F3**. Store separation is **P2**. Human step: exercising the complaint path with the Team Lead and then the Founder as subject — a drill, on a recorded cadence. Backs invariant 110 |
| AT-108 | **The founder ops console is provably read-only**: from its own OS user and credentials, four attempts — control-plane write, `records/` write, board mutation, any Layer B access — all fail; the console then still answers a read query over Layer A data correctly | L5† (J) | L5 (K,L) | `COND` | — | `A` | **Not a phase test — a trigger test.** 98.2 F3 is explicit: the founder ops console is *not* a phase deliverable; it stands up "only if free CI notifications prove insufficient" (Section 39.5), registered in `tools.yaml` before first use. **If the trigger never fires, AT-108 is `NOT_APPLICABLE_BY_DECISION` and must be recorded as such — never left silently unrun.** Subsystem `J` needs the assignment of Section 2. Four negatives plus one positive; "Hermes proposes; the platform disposes" (D69, D71) |
| AT-109 | **The background cage egress wall holds**: from inside the worker container, a non-allowlisted external host and the Layer B store are both refused **at the host egress layer — not by harness configuration** — while GitHub and the LAN inference endpoint succeed; and the systemd wall-clock stop terminates the running process at the window boundary | L5† (J) | L5 (M) | `F3` | — | `A` | **Gate: F3** — the Hermes background worker cage stands up in Phase 3. **Conditional on the CPU benchmark passing**; 98.2 states a parked benchmark parks every local-inference slot. If parked, record `NOT_APPLICABLE_BY_DECISION`. The load-bearing phrase is "not by harness configuration": the test must be run with the harness allowlist **disabled** — otherwise it proves the harness, not the wall |
| AT-110 | **The reconciler credential is provably bounded**: six attempts from the reconciler's own credential — Actions-secret write, environment write, workflow-file change, org-settings change, `records/**` write, any Layer B access — all six fail; the credential then still completes a normal reconciliation run | L3 (C) | L5 (L, secret tiers) | `F3` | — | `A` | **Gate: F3** — executed for real at the phase that builds the reconciler, and **re-executed at every rotation**, on the same gate as 40.1's clean-reconciliation condition. Pairs with **AT-102**: 102 proves the instrument still looks, 110 proves it cannot exceed its reach. Six negatives **plus one positive** — the positive matters, or a fully broken credential passes |

---

## 9. Coverage ledger — what the five-lane build actually proves

This is the section L0 reads. The five lanes build the Foundation tier (Phases 1–7), Early hardening and the Scale-activation mechanisms. That is the whole of their scope, and it is **less than half of what the acceptance catalogue measures**.

### 9.1 By tier

| Reachable at | Tests | Share | Meaning for L0 |
| --- | --- | --- | --- |
| Within the five-lane build — `F1`–`F7`, `EH`, `SA`, `COND` | **37** | 34% | This is everything the parallel build can prove about itself |
| Gated on the Governance tier — `G1`–`G8` | **23** | 21% | Not provable by any lane. Several carry calendar gates measured in quarters |
| Gated on the People tier — `P1`–`P8` | **50** | 45% | Not provable by any lane. Subsystem `P` has **no owner** in the frozen partition |

**37 of 110.** A lane that reports "all my acceptance tests pass" at the end of the build has, at most, said something about a third of the catalogue. Any status report that does not carry this denominator is misleading, and L0 should reject it.

### 9.2 The 37 in-scope tests, by phase and by automatability

| Phase | Tests | `A` | `H/A` | `H` |
| --- | --- | --- | --- | --- |
| `F1` | AT-022 | 0 | 0 | 1 |
| `F2` | AT-051 | 1 | 0 | 0 |
| `F3` | AT-011, AT-018, AT-021, AT-036, AT-039, AT-075, AT-102, AT-109, AT-110 | 8 | 1 | 0 |
| `F4` | AT-010 | 1 | 0 | 0 |
| `F5` | AT-009, AT-049, AT-107 | 3 | 0 | 0 |
| `F6` | AT-028, AT-029, AT-101, AT-103 | 0 | 1 | 3 |
| `F7` | AT-030, AT-034, AT-106 | 2 | 1 | 0 |
| `EH` | AT-003, AT-004, AT-023, AT-024, AT-025, AT-026, AT-033, AT-035, AT-048, AT-104 | 6 | 4 | 0 |
| `SA` | AT-008, AT-019, AT-020, AT-105 | 1 | 3 | 0 |
| `COND` | AT-108 | 1 | 0 | 0 |
| **Total** | **37** | **23** | **10** | **4** |

**23 fully automatable tests are the entire machine-checkable acceptance surface of the five-lane build.** Each one gets a mandatory negative twin in Section 10. Ten more have an automatable core with one named human step; their automatable cores also get twins.

### 9.3 By lane — what each lane is on the hook for

Counted by **primary** lane on tests reachable within the five-lane build.

| Lane | In-scope ATs where this lane is primary | Count |
| --- | --- | --- |
| **L1** Registries & Contracts | AT-010, AT-019, AT-020, AT-025, AT-039, AT-051, AT-075, AT-101*, AT-003 | 9 |
| **L2** Pipeline & Evidence | AT-009, AT-023, AT-024, AT-026, AT-029, AT-035, AT-103, AT-105 | 8 |
| **L3** Reconciler & Provisioning | AT-004, AT-008, AT-017*, AT-018, AT-033, AT-036, AT-102, AT-110 | 7 in-scope (AT-017 full pass is P7) |
| **L4** Records, Events & Metrics | AT-048, AT-104 | 2 |
| **L5** Access, Infra & Ops | AT-011, AT-022, AT-028, AT-030, AT-107, AT-108, AT-109 | 7 |
| **L0** Integrator | AT-034 | 1 |
| **L1** (AT-021 primary, records to L4) | AT-021 | 1 |
| **Unowned** (`‡G`) | AT-106 | 1 |

**L4 is primary on only two in-scope tests.** That is not a small workload — it is a **detection hole**. L4 owns the entire `control-plane-records` repository, `schemas/records/**`, `metrics/**` and `tools/records/**`, and almost nothing in the Foundation-tier acceptance catalogue points at it, because the records and metrics surface is consumed by the Governance tier that is out of scope. L0 must not read "two ATs" as "small risk". Concretely: **L4 could ship a records schema nothing validates against and no acceptance test would notice until G1.**

Mitigation, and L0 must require it: L4's merge gate leans on the **contract-conformance and fixture tests of `contracts/**`** rather than on the acceptance catalogue, plus the `STATIC-F3` checks of AT-071, AT-074, AT-075, AT-081, AT-083 and AT-085, which run against L4's metric schemas and are the only People-domain protection the build has. This is stated in file `03` of this protocol series if one exists; if it does not, it is L0's to write.

### 9.4 The four tests that gate a tier crossing

| Test | Gates | Why it is different |
| --- | --- | --- |
| AT-089 | P2 → P4 | Named verbatim in 98.6 as a P4 entry condition |
| AT-091 | P2 → P4 | Same |
| AT-097 | P2 → P4 | Same; must be verified in the provisioned configuration (D75), not by looking at a dashboard |
| AT-098 | P2 → P4 | Same |

Plus invariant 109 must hold. **P4 generates people evidence; if this gate is crossed on an unverified green, evidence exists that cannot be access-controlled.** L0 requires all four negative twins executed and recorded before accepting the crossing. This is the highest-consequence gate in the catalogue and it is 45% of the way out of the five-lane build's reach — which is exactly why it is written down now.

---

## 10. The negative twin register — every gate must be able to fail

For each automatable AT reachable within the five-lane build, this is the specific mutation that MUST make it fail. A twin is run **at the phase the AT first runs, and again whenever the AT's implementation changes**. Twin results are recorded beside AT results; an AT with no recorded twin result is reported as `UNPROVEN`, not `PASS`.

| Twin | AT | The mutation that must make the AT fail |
| --- | --- | --- |
| `NT-011` | AT-011 | Add a hard-coded runtime name to a workflow or verification script instead of reading the approved-runtime list. AT-011 must fail on the diff assertion |
| `NT-018` | AT-018 | Back-date an assignment's `end_date` and stub the revocation call to no-op. Reconciliation must still report the assignment as live drift — if it reports clean, the revocation was never verified, only invoked |
| `NT-021` | AT-021 | Insert a Founder-approval step into the ownership-change path. AT-021's "no Founder approval step exists or is required" clause must fail |
| `NT-036` | AT-036 | Commit an `exceptions.yaml` entry with no `expiry`. Control-plane CI must reject it — this negative is already written into the F1 completion check ("rejects a deliberately malformed exception"); execute it, do not assume it |
| `NT-039` | AT-039 | Set a bootstrap exception's expiry to yesterday with its gate still stubbed. Blocking drift must appear. Then meet the headcount trigger with the exception open — the gate must arm |
| `NT-071` | AT-071 | Introduce a code path that lets the Team Lead or automation finalise a formal personnel action — an auto-approved improvement plan, termination, promotion, compensation change or formal warning. The repository-wide prohibited-symbol check and the schema negative test must both reject it |
| `NT-074` | AT-074 | Hard-code one "sustained" threshold as a numeric literal in application code instead of reading it from the configuration files. The static check must reject the merge |
| `NT-075` | AT-075 | Add one banned surveillance measurement to a metric schema. The validator must reject the merge. **This twin also covers the AT-085 static half** |
| `NT-081` | AT-081 | Wire a capability-maturity assessment output into the access model so that it changes a permission. The static check must reject the merge — a maturity score must never move a permission |
| `NT-102` | AT-102 | Remove the seeded canary from the comparison set. The run must report FAILED and raise SIG-13 — a clean report here means the instrument stopped looking. **Second twin:** narrow one registry's comparison set by one row; the per-registry comparison counts (53.1) must expose it as visible drift |
| `NT-109` | AT-109 | Disable the host firewall allowlist while leaving the harness allowlist in place. The non-allowlisted connection must **succeed**, proving the earlier pass came from the wall and not from the harness. Restore, re-run, require refusal. **Second twin:** extend a task past the window boundary; the systemd stop must terminate it |
| `NT-110` | AT-110 | Grant the reconciler credential one of the six forbidden scopes. That attempt must now succeed and the AT must FAIL. Revoke, re-run, require all six refusals **and** the positive reconciliation run |
| `NT-010` | AT-010 | Add a second repository to the product without registering it. Branch protection coverage must report the gap; the dashboard must still show one entry |
| `NT-009` | AT-009 | Remove one of the eight commands from the foreign-stack product. The conformance runner must fail on that command specifically, not on a generic error |
| `NT-049` | AT-049 | Declare `ai_runtime_dependency` with no evaluation suite under `verification/`. CI must fail the PR. **Second twin:** change a model pin with a failing suite; the merge must be blocked |
| `NT-107` | AT-107 | Plant a deliberate regression in a fixture evaluation suite. The scheduled runner must raise SIG-42 and block pin adoption. A runner that has never fired is unproven |
| `NT-030` | AT-030 | Remove the control-plane tool from `PATH`. Product workflows must continue and `.planning/` must remain readable — if a workflow silently skips instead of continuing, that is a failure, not a pass |
| `NT-034` | AT-034 | Delete `os-health.yaml`, `policies.yaml`, `patterns.yaml`, `economics.yaml` and `platform-roadmap.yaml`, then build and run the delivery core. It must pass. **Second twin, the important one:** delete the reconciliation engine or the exception registry — the core must **fail**, proving they are genuinely core-resident and not quietly optional |
| `NT-004` | AT-004 | Execute `change-role` and assert that zero workflow files changed in the diff. Then hand-edit a workflow to encode the old lead's identity; the assertion must fail |
| `NT-023` | AT-023 | Point one product at an unpinned workflow ref. The `platform_compatibility` isolation claim must fail — an unpinned consumer is not protected by the canary |
| `NT-024` | AT-024 | Break the shared CI workflow on purpose at the canary tag. The canary must catch it and unmigrated pinned products must remain green. **If the canary set had no activity in the window, per 61.5 the run is not a pass** — the synthetic `workflow_dispatch` exercise must be recorded |
| `NT-025` | AT-025 | Publish a schema change that drops support for the previous `contract_version`. Fleet products on the old version must fail validation, proving the dual-version claim was real |
| `NT-026` | AT-026 | Break the rollback path at the fleet stage. The rollout must be blocked at pilot — an untested rollback must never advance a stage |
| `NT-033` | AT-033 | Present reconciliation with a production control **stricter** than declared. Auto-repair must not touch it and it must be raised for human review. Then present a **looser** control: auto-repair must tighten it. Both directions, or the test proves nothing about direction |
| `NT-008` | AT-008 | Create a synthetic contractor entry with **no** `end_date`. The subsystem-B validator must reject it. Then create one with yesterday's end date and require revocation with no human action |
| `NT-051` | AT-051 | Back-date a pre-onboarding deadline. Drift must appear. Then remove the accepted-risk record; validation must fail |
| `NT-108` | AT-108 | Grant the ops console OS user one write scope. That attempt must succeed and the AT must FAIL. Revoke, re-run, require all four refusals **and** the positive read query |
| `NT-035` | AT-035 | Restore the organisation export to the independent environment with the Projects GraphQL dump **absent**. The restore must be reported incomplete — the D80 clause exists precisely because boards are the class most often assumed present in a migration archive |
| `NT-103` | AT-103 | Remove the workflow's scoped run identity. `restore-production.yml` must fail closed. **Second twin:** attempt the restore with no exceptional-authorisation record; it must refuse |
| `NT-106` | AT-106 | Let a Gate 1 submission breach its turnaround target. The Blocked flag must auto-raise and route to the **escalation role**, not to the author's manager — a capacity signal, never a personal one |
| `NT-048` | AT-048 | Submit an intake item with no defect-taxonomy category. The handoff record must not generate |
| `NT-104` | AT-104 | Ship a fix and attempt to close the support record **without a reply to the customer**. Closure must be refused. **Second twin:** set the first-response clock from the ingest time rather than the message's received timestamp; the D80 assertion must fail |
| `NT-019` | AT-019 | Split a product leaving the original contract resolving to neither a successor nor sunset. Validation must reject the ambiguous state |
| `NT-020` | AT-020 | Merge two products dropping one verification contract. CI must fail on invariant 5 |
| `NT-105` | AT-105 | Write a deletion record missing one of the four timestamps. Validation must reject it. **Second twin:** exceed `deletion_sla_days`; the breach must surface, not age quietly |
| `NT-003` | AT-003 | Mark the Team Lead absent with **no** Acting Team Lead pre-designated. The absence must surface as blocking, not resolve silently to the Founder |

**Twins for the four tier-crossing tests** (out of five-lane scope but specified now so P2 cannot be accepted on a bare green):

| Twin | AT | Mutation |
| --- | --- | --- |
| `NT-089` | AT-089 | Add one Layer B table to the general engineering datasource. Every peer-reachability assertion must fail |
| `NT-091` | AT-091 | Expire the dated delegate assignment and re-run. Access must close through reconciliation, not merely stop being granted |
| `NT-097` | AT-097 | Add a people datasource entry to the shared Grafana provisioning file with **no dashboard referencing it**. AT-097 must still fail — D75 requires the assertion be on the provisioned configuration, so a test that passes here was inferring from panel visibility |
| `NT-098` | AT-098 | Point the Founder-only instance at the shared credential. The uncredentialed-query denial must fail |

---

## 11. The harness

### 11.1 Layout

The harness is **L0-owned** and needs a PARTITION amendment (Section 2). One script per test, one per twin, no shared mutable index — directory-per-item, per the anti-conflict rules.

```
control-plane/
  verification/acceptance/
    AT-011.sh   AT-011.neg.sh
    AT-018.sh   AT-018.neg.sh
    ...
    AT-CANARY.sh          # the permanently failing sentinel
    manifest/
      AT-011.yaml         # id, lane, phase, auto, twin, gate — one file per test
  tools/at/
    run-at.sh
    at-gate.sh
```

Exit-code contract, and it is the whole discipline:

| Code | Meaning | Counted as |
| --- | --- | --- |
| `0` | PASS | pass |
| `1` | FAIL | fail |
| `78` | NOT_YET_RUNNABLE — the phase gate in the manifest is not reached | **reported separately, never a pass** |
| `79` | NOT_APPLICABLE_BY_DECISION — requires a recorded decision id in the manifest | **reported separately, never a pass** |

### 11.2 The sentinel

`AT-CANARY.sh` is a deliberately failing test that must appear as FAILED in every run. Section 53.1's rule applied to the harness itself: a run in which the sentinel passes proves the harness stopped discriminating.

```bash
set -euo pipefail
#!/usr/bin/env bash
# verification/acceptance/AT-CANARY.sh
# Permanently failing sentinel. Section 53.1 seeded-canary rule applied to the AT harness.
# If this returns 0, the harness is broken. Do not "fix" this file.
set -euo pipefail
echo "AT-CANARY: sentinel assertion — this MUST fail"
exit 1
```

### 11.3 The runner

```bash
set -euo pipefail
#!/usr/bin/env bash
# tools/at/run-at.sh <phase-token>   e.g. ./tools/at/run-at.sh F3
set -uo pipefail
PHASE="${1:?usage: run-at.sh <F1|F2|F3|F4|F5|F6|F7|EH|SA|COND>}"
ROOT="$(git rev-parse --show-toplevel)"
pass=0; fail=0; skip=0; na=0; sentinel_ok=0

for t in "$ROOT"/verification/acceptance/AT-*.sh; do
  case "$t" in *.neg.sh) continue;; esac
  id="$(basename "$t" .sh)"
  AT_PHASE="$PHASE" bash "$t"; rc=$?
  case "$rc" in
    0)  if [ "$id" = "AT-CANARY" ]; then
          echo "FATAL: sentinel passed — the harness is not discriminating"; exit 2
        fi
        echo "PASS  $id"; pass=$((pass+1)) ;;
    1)  if [ "$id" = "AT-CANARY" ]; then
          echo "OK    $id (sentinel failed as required)"; sentinel_ok=1
        else
          echo "FAIL  $id"; fail=$((fail+1))
        fi ;;
    78) echo "SKIP  $id  NOT_YET_RUNNABLE at $PHASE"; skip=$((skip+1)) ;;
    79) echo "N/A   $id  NOT_APPLICABLE_BY_DECISION"; na=$((na+1)) ;;
    *)  echo "FAIL  $id  unexpected exit $rc"; fail=$((fail+1)) ;;
  esac
done

if [ "$sentinel_ok" -ne 1 ]; then
  echo "FATAL: sentinel did not run — a run without AT-CANARY is not a run"; exit 2
fi
echo "phase=$PHASE pass=$pass fail=$fail not_yet_runnable=$skip not_applicable=$na sentinel=ok"
[ "$fail" -eq 0 ]
```

### 11.4 Running the twins

A twin run is destructive by design: it mutates, asserts the AT now fails, and reverts. It runs on a scratch branch, never on `integration`.

```bash
#!/usr/bin/env bash
# tools/at/prove-twin.sh <AT-id>
set -euo pipefail
ID="${1:?usage: prove-twin.sh AT-033}"
ROOT="$(git rev-parse --show-toplevel)"
BR="twin/${ID}-$(date +%s)"

git -C "$ROOT" switch -c "$BR"
bash "$ROOT/verification/acceptance/${ID}.sh" \
  || { echo "TWIN UNPROVABLE: pre-mutation run did not pass"; git -C "$ROOT" switch - && git -C "$ROOT" branch -D "$BR"; exit 2; }
bash "$ROOT/verification/acceptance/${ID}.neg.sh"      # applies the mutation

rc=0
bash "$ROOT/verification/acceptance/${ID}.sh" || rc=$?
case $rc in
  0) echo "TWIN FAILED: ${ID} still passes under its negative mutation — the gate cannot fail"
     git -C "$ROOT" switch - && git -C "$ROOT" branch -D "$BR"; exit 1;;
  1) echo "TWIN OK: ${ID} fails under mutation ${ID}.neg.sh";;
  *) echo "TWIN UNPROVABLE: exit $rc"; git -C "$ROOT" switch - && git -C "$ROOT" branch -D "$BR"; exit 2;;
esac

git -C "$ROOT" switch - && git -C "$ROOT" branch -D "$BR"
```

**Paired negative** — an AT that exits 78 (`NOT_YET_RUNNABLE`) or 79 (`NOT_APPLICABLE_BY_DECISION`) after mutation produces `TWIN UNPROVABLE` (exit 2), not `TWIN OK`:

```bash
# Simulate: post-mutation AT exits 78 (NOT_YET_RUNNABLE)
rc=78
case $rc in
  0) echo "TWIN FAILED"; exit 1;;
  1) echo "TWIN OK";;
  *) echo "TWIN UNPROVABLE: exit $rc"; exit 2;;  # ← fires here; exit 2 is returned, not TWIN OK
esac
# Output: "TWIN UNPROVABLE: exit 78"
# Also verified: pre-mutation AT exits 78 → `|| { echo "TWIN UNPROVABLE: pre-mutation run did not pass"; exit 2; }` fires.
```

### 11.5 Where this runs in the merge train

`PARTITION.md` fixes the merge order **L1 → L4 → L2 → L3 → L5** into `integration`, then `integration` → `main` when the full gate passes.

| Point | What runs | Blocking? |
| --- | --- | --- |
| Lane PR → `integration` | `run-at.sh <current-phase>` restricted to ATs whose **primary lane** is this lane, plus every `STATIC-F3` check (AT-071, AT-074, AT-075, AT-081, AT-083, AT-085) regardless of lane | Yes |
| Lane PR touching a path named in any AT manifest's `implements:` list | `prove-twin.sh` for each affected AT | Yes |
| After the full merge train completes a cycle | `run-at.sh <current-phase>` over the **whole** catalogue | Yes |
| `integration` → `main` | Full catalogue plus **every twin for every AT currently reported PASS at this phase** | Yes |
| Phase completion check (Section 98) | Full catalogue, all twins, and the ledger of Section 9 re-emitted with its denominator | Yes |

```bash
# tools/at/at-gate.sh — the integration → main gate
set -euo pipefail
PHASE="$(cat "$(git rev-parse --show-toplevel)/.at-phase")"
bash tools/at/run-at.sh "$PHASE"
for id in $(bash tools/at/run-at.sh "$PHASE" | awk '/^PASS/{print $2}'); do
  bash tools/at/prove-twin.sh "$id"
done
```

**The `STATIC-F3` checks run on every lane's PR, not only their owner's.** AT-071, AT-074, AT-075, AT-081, AT-083 and AT-085 are prohibitions on what may exist anywhere in the repository. A prohibition enforced only in the lane that owns the prohibition is not enforced — any of the five lanes can introduce a banned metric or an automated people action, and four of them would never run the check.

---

## 12. Completeness self-check

This mapping is itself a check, so it must be able to fail. Run these against the spec before trusting any row above. Paths are absolute for this workstation; substitute the repo-relative path in CI.

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
MAP="C:/D_Drive/PS/MultiProduct/Code/implementation/protocol/02-acceptance-mapping.md"

# 1. Section 100 must contain exactly 110 distinct AT ids.
_c1=$(awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' "$SPEC" | grep -oE 'AT-[0-9]{3}' | sort -u | wc -l | tr -d ' ')
[ "$_c1" -eq 110 ] || { echo "FAIL check 1: distinct AT ids in Section 100 = $_c1 (expected 110)"; exit 1; }
echo "PASS check 1: distinct AT ids = $_c1"
unset _c1

# 2. Section 100 must contain exactly 110 table rows beginning with an AT id.
_c2=$(awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' "$SPEC" | grep -cE '^\| AT-[0-9]{3} \|')
[ "$_c2" -eq 110 ] || { echo "FAIL check 2: AT rows in Section 100 = $_c2 (expected 110)"; exit 1; }
echo "PASS check 2: AT rows = $_c2"
unset _c2

# 3. No id may appear as the leading cell of two rows.
_dups=$(awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' "$SPEC" | grep -oE '^\| AT-[0-9]{3}' | sort | uniq -d)
[ -z "$_dups" ] || { echo "FAIL check 3: duplicate leading AT ids in Section 100: $_dups"; exit 1; }
echo "PASS check 3: no duplicate leading AT ids"
unset _dups

# 4. This mapping must cover every id in the spec, and invent none.
# `|| true` keeps a real mismatch (diff exits 1) from tripping `set -e` before the check below runs.
_diff4=$(diff <(awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' "$SPEC" | grep -oE 'AT-[0-9]{3}' | sort -u) \
     <(grep -oE 'AT-[0-9]{3}' "$MAP" | sort -u) || true)
[ -z "$_diff4" ] || { echo "FAIL check 4: mapping/spec AT id mismatch:"; echo "$_diff4"; exit 1; }
echo "PASS check 4: mapping covers exactly the spec's AT ids"
unset _diff4

# 5. Row count and unique-id count must agree (no duplication anomaly in Section 100).
_s100=$(awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' "$SPEC")
_unique=$(printf '%s\n' "$_s100" | grep -oE '^\| AT-[0-9]{3}' | sort -u | wc -l | tr -d ' ')
_cells=$(printf '%s\n' "$_s100" | grep -oE '\| AT-[0-9]{3} \|' | wc -l | tr -d ' ')
[ "$_unique" -eq "$_cells" ] || { echo "FAIL check 5: cells=$_cells unique=$_unique (duplication detected in Section 100)"; exit 1; }
echo "PASS check 5: cells=$_cells unique=$_unique"
unset _s100 _unique _cells

# 6. Every AT in the harness must have a manifest and, if automatable, a twin.
for f in verification/acceptance/AT-*.sh; do
  case "$f" in *.neg.sh|*AT-CANARY.sh) continue;; esac
  id="$(basename "$f" .sh)"
  test -f "verification/acceptance/manifest/${id}.yaml" || { echo "MISSING MANIFEST $id"; exit 1; }
  grep -q '^auto: A' "verification/acceptance/manifest/${id}.yaml" \
    && { test -f "verification/acceptance/${id}.neg.sh" || { echo "MISSING TWIN $id"; exit 1; }; }
done

# 7. The sentinel must exist and must fail.
bash verification/acceptance/AT-CANARY.sh && { echo "FATAL: sentinel passes"; exit 2; }
```

Check 4 is the one that matters. It is the reason no id in this document was written from memory: every AT id above was extracted from the spec and diffed back against it.

---

## 13. STOP rules

These bind every lane. On any of them: **do not proceed; open a blocker issue and stop.** Cite the rule's `STOP-0N` code in the issue title and pass it as part of the `--label` value (repository label convention: `blocker,lane-N,phase-N`, per `lanes/L1-02-schemas.md`) — a blocker issue filed with no code routes to no queue and is indistinguishable from any other blocker.

1. **STOP-01 — A run reports zero failures including the sentinel.** The harness is not discriminating. Do not merge. (Section 53.1, AT-102.)
2. **STOP-02 — An AT is reported PASS with no recorded twin result.** Report it `UNPROVEN`. A gate that has never been shown to fail is not a gate. Do not cite it in a phase completion check.
3. **STOP-03 — An AT returns `78` (NOT_YET_RUNNABLE) and a status report counts it toward a pass rate.** Reject the report. Skipped is not passed.
4. **STOP-04 — An AT returns `79` (NOT_APPLICABLE_BY_DECISION) with no decision id in its manifest.** This is the "parked and forgotten" failure mode. AT-108 and AT-109 are the live candidates — the ops console fires only on its Section 39.5 trigger and the background cage only if the F3 benchmark passes. Either way, a decision record, not silence.
5. **STOP-05 — A lane proposes rewording an AT's pass condition to make it pass.** Stop. AT-090 names this failure in the specification itself: "A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes." A test that cannot pass is a finding about the build, and Section 100's preamble says where the defect then lies.
6. **STOP-06 — P4 is proposed while any of AT-089, AT-091, AT-097, AT-098 is unproven or its twin unrun.** 98.6 makes this binding: people evidence must not be generated before it can be access-controlled at the datasource layer.
7. **STOP-07 — A lane claims an AT outside its primary or contributing lanes in this map.** Two lanes claiming one AT means one of them built something it does not own — precisely the failure this protocol exists to catch. Route to L0.
8. **STOP-08 — A lane reports acceptance coverage without the denominator of Section 9.1.** 37 of 110 is the honest ceiling for the five-lane build. A percentage computed over "the tests I wrote" is not a coverage figure.
9. **STOP-09 — AT-109 is executed with the harness allowlist still enabled.** It then proves the harness, not the wall, and the test text is explicit that the wall must hold "at the host egress layer — not by harness configuration".
10. **STOP-10 — AT-110 or AT-108 is executed without its positive leg.** All-negatives-pass is also what a completely broken credential produces. The positive reconciliation run and the positive read query are load-bearing.
11. **STOP-11 — Subsystem `G`, `H`, `J`, `O` or `P` work appears in a lane PR before L0 has recorded the assignment** of Section 2. An unowned subsystem silently absorbed by a lane is how the partition stops being frozen.
12. **STOP-12 — mandatory `--label` missing.** None of the eleven rules above named a routing code before this edit, so a blocker filed against any of them carried no `--label` value and landed unrouted. Fixed here by giving each rule its own `STOP-0N` code (above); any future STOP rule added to this section must be assigned a code in the same edit that adds it — an unlabelled STOP rule is this same defect recurring.
