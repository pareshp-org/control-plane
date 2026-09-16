# L1-00 — LANE 1 CHARTER: Registries and Contracts

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 Registries & Contracts
**Branch prefix:** `lane/1/*`
**Subsystems:** A (Control-plane repository), B (Schema validation and CI gate engine)
**Merge-train position:** FIRST (`L1 → L4 → L2 → L3 → L5`)
**Governing partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — FROZEN. This charter never contradicts it.
**Governing spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines)

> **Reader profile.** Every task in this lane is executed by a low-cost AI developer with no repository context
> and no judgment authority, working alone on one branch. Nothing in any L1 document may require designing,
> choosing, interpreting, or "using judgment". Where a choice is genuinely open, it appears in
> §12 DECISION REQUIRED and is escalated to L0. It is never left to the executor.

---

## 1. Charter statement

L1 builds the **declared-state substrate** of the operating system and the **engine that proves declared state is well-formed**.

Concretely, L1 produces exactly three classes of artifact:

1. **Schemas** — versioned JSON Schema documents for every control-plane registry and every per-product contract.
2. **Registry files** — the authoritative YAML registry instances themselves (`people.yaml`, `roles.yaml`, `platform.yaml`, `topology.yaml`, and the governance registers).
3. **Validators** — the executable checks that fail CI on a malformed, referentially broken, expired, or fail-open declaration.

L1 builds **no** workflow, **no** reconciler, **no** provisioning CLI, **no** dashboard, **no** record store, and **no** access configuration. Those belong to other lanes (§4).

The spec states the dependency this charter exists to serve, in Section 99.2 (lines 9184–9231):

> **Dependency spine:** A (registries) → B (validation) → C (reconciliation) and D (provisioning) …

Everything the other four lanes do is validated against what L1 emits. That is why L1 merges first.

---

## 2. Subsystem mapping to spec Section 99.2

Section 99.2 lives at spec lines **9184–9231**. L1 owns exactly two rows of that table.

| # | Subsystem (verbatim from 99.2) | Cx | Depends on | L1 scope |
|---|---|---|---|---|
| **A** | Control-plane repository — "Versioned YAML registries and contracts: people, roles, assignments, platform, topology, per-product contracts and verification contracts, the governance files (os-health, policies, exceptions, patterns, economics, platform-roadmap, tools), the people-layer entities, and the record stores of Section 97" | M | — | **All of A except the record stores of Section 97**, which PARTITION assigns to L4 (`schemas/records/**`). See §4. |
| **B** | Schema validation and CI gate engine — "Multi-version schema validators, referential integrity (assignments name existing non-departed people; dependencies name existing services), date rules (mandatory end dates for non-employees, restore-tested within window, expired assignments fail), the 24x7-without-rota and commitments-conflict blockers, exception-without-expiry rejection, unclassified-control rejection" | M | A | **All of B.** The validator *code and fixtures* are L1. The CI *workflow file* that invokes them is L2 (`.github/workflows/**`). See §6. |

Section 99.2 also lists named build-surface tools. One is assigned to subsystem B and is therefore L1's:

| Tool (99.2, lines 9184–9231) | Subsystem | L1 verdict |
|---|---|---|
| `check-commitment` CLI — "Checks a proposed customer commitment against the commitments and SLA registry (Section 21) before signature" | B | **L1 builds it**, under `validators/registry/**`. Its rule table is Section 21.4 (spec lines 2166–2184). |
| `record-decision` CLI | A, O | **NOT L1** — it writes `records/decisions/`, which is L4. See §12 DECISION REQUIRED #3. |

---

## 3. Owned paths — exact, exclusive

Copied verbatim from PARTITION.md line 17. These four prefixes are the complete set. L1 writes nothing outside them.

```
schemas/registry/**
schemas/product/**
registries/**
validators/registry/**
```

### 3.1 Normative internal layout

L1 is the sole owner of these prefixes and therefore fixes their internal structure here. Every later L1 document
(`L1-01-*`, `L1-02-*`, …) places files according to this table and nowhere else.

| Path | Holds | Spec anchor |
|---|---|---|
| `schemas/registry/people.v1.schema.json` | People Registry schema, incl. `work_arrangement` | §7 (543–633) |
| `schemas/registry/roles.v1.schema.json` | Role Registry schema | §8 (634–686) |
| `schemas/registry/capabilities.v1.schema.json` | The closed capability vocabulary | §9 (687–724) |
| `schemas/registry/topology.v1.schema.json` | Domains, TL scopes, succession | §13.1 (1133–1155), §66.2 (5508–5541) |
| `schemas/registry/platform.v1.schema.json` | OS version, supported contract versions, canary set, closed `event_type` enum | §60 (5119–5214), §52.6 (4613–4648) |
| `schemas/registry/exceptions.v1.schema.json` | Exception registry incl. break-glass and bootstrap | §54 (4746–4829), §95.2 (8644–8684) |
| `schemas/registry/policies.v1.schema.json` | Policy register and lifecycle state | §55 (4830–4906) |
| `schemas/registry/os-health.v1.schema.json` | Metric register (signal + success-metric declarations) | §52.6 (4613–4648) |
| `schemas/registry/patterns.v1.schema.json` | Confirmed failure patterns | §52.6 (4613–4648) |
| `schemas/registry/economics.v1.schema.json` | Attention weights, load-model weights, automation ledger | §68.1 (5624–5655), §52.6 (4613–4648) |
| `schemas/registry/platform-roadmap.v1.schema.json` | Roadmap, investment gates, change budget | §59.3 (5083–5102) |
| `schemas/registry/tools.v1.schema.json` | Tool register: owner, version, purpose, exit condition | §62.1 (5289–5357) |
| `schemas/registry/framework.v1.schema.json` | Performance framework registry — definitions only, never individual evidence | §77 (6339–6405) |
| `schemas/product/product.v1.schema.json` | Product Operating Contract | §15 (1284–1606) |
| `schemas/product/verification-contract.v1.schema.json` | Verification Contract | §31 (2741–2802) |
| `schemas/product/service.v1.schema.json` | Shared Service Contract | §20 (2027–2112) |
| `registries/*.yaml` | The authoritative registry instances named in §52.6 that L1 owns | §52.6 (4613–4648) |
| `validators/registry/schema/` | Multi-version schema validation driver | §99.2 row B |
| `validators/registry/rules/` | One file per non-schema rule (referential integrity, date rules, blockers) | §15.5 (1564–1582), §99.2 row B |
| `validators/registry/fixtures/valid/` | Golden fixtures that MUST pass | §100 pass conditions |
| `validators/registry/fixtures/invalid/` | Golden fixtures that MUST fail, one per rule | §100 pass conditions |
<!-- # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/ -->
| `validators/registry/bin/` | Executable entrypoints, incl. `check-commitment` | §99.2 tools table |
| `validators/registry/_meta/` | Lane self-guard and spec-anchor files created by §11 | — |

**Versioning rule, binding on every L1 file.** Section 60.2 (spec lines 5152–5214) requires: *"Write the v2 schema alongside v1 — do not replace"* and *"Validator supports BOTH v1 and v2."* No L1 task may ever delete or overwrite a `*.v1.schema.json` once merged. New versions are new files. This is also PARTITION rule 5 (additive-only).

---

## 4. Explicitly NOT owned — do not touch

A PR from `lane/1/*` touching any path below **FAILS the lane-guard check** (PARTITION rule 1). No exceptions, no "just this once".

| Foreign path | Owner | Why L1 might wrongly reach for it |
|---|---|---|
| `contracts/**` | **L0** | Frozen in Phase 0. L1 codes *against* it. A needed change is a Contract Change Request, never an edit (PARTITION rule 2). |
| `schemas/records/**` | **L4** | Section 99.2 row A names "the record stores of Section 97" — PARTITION splits them to L4. §97 (8834–8991) is L4's, not L1's. |
| `.github/workflows/**` | **L2** | L1 writes validator code; L2 writes the workflow that runs it. |
| `templates/workflows/**`, `tools/evidence/**` | L2 | — |
| `reconciler/**`, `tools/provision/**`, `validators/drift/**` | **L3** | `validators/drift/**` is a different prefix from `validators/registry/**`. Read the prefix. |
| `metrics/**`, `tools/records/**`, all of `control-plane-records` | L4 | — |
| `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` | L5 | Section 49 (4334–4369) asset inventory is L5's `assets/**`. |
| `CODEOWNERS`, `docs/**`, `Makefile`, root files | **L0** | — |

---

## 5. What L1 consumes from `contracts/**`

PARTITION line 26: *"`contracts/**` is written by L0 in Phase 0 and FROZEN. Lanes code against it and against generated stubs/fixtures."*

L1 requires exactly these five facts to be present in `contracts/**` before it can build. Each is asserted mechanically by task **L1-00-01**. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

| # | Fact L1 consumes | Used by | If absent |
|---|---|---|---|
| C1 | The validator invocation contract: the command line, exit-code semantics and machine-readable output shape L2's CI workflow uses to call L1's validators | `validators/registry/bin/**` | STOP — file CCR (§13) |
| C2 | The repository layout contract: confirmation that the four L1 prefixes of §3 are the real on-disk prefixes in `control-plane` | every L1 task | STOP — file CCR |
| C3 | The schema-version contract: the naming and discovery convention for `*.vN.schema.json`, so L2/L3/L4 resolve a version the same way L1 emits it | all schemas | STOP — file CCR |
| C4 | The fixture contract: where L3/L4 read L1's golden fixtures from, so no lane reaches into another lane's source tree (PARTITION rule 4) | `validators/registry/fixtures/**` | STOP — file CCR |
| C5 | The blocker-issue contract: the issue label/template L0 reads | §13 | STOP — file CCR |

L1 consumes nothing else from any lane. L1 **never** imports from `reconciler/**`, `metrics/**`, `access/**`, or `.github/**`.

---

## 6. What L1 publishes for the other lanes

Everything below is consumed **only** through `contracts/**` or as a merged artifact on `integration` — never by reaching into `validators/registry/` source (PARTITION rule 4).

| Published artifact | Consumer lane | Spec anchor for the coupling |
|---|---|---|
| ~~The complete capability vocabulary (`schemas/registry/capabilities.v1.schema.json`)~~ — **NOT PUBLISHED — REG-043 row b: this file does not exist. Remove any task step or acceptance criterion that asserts its presence.** Section 9's table is the *closed* set; the vocabulary is enforced via the validator rule, not a published schema file. | L3 (permission derivation), L5 (access model) | §9.1 (717–724); D81; D90 |
| `product.v1.schema.json` + valid/invalid fixtures | L2 (CI gate), L3 (provisioning templates) | §15 (1284–1606) |
| `verification-contract.v1.schema.json` | L2 (CI presence enforcement) | §31 (2741–2802); invariant 1 |
| The closed `event_type` enum, declared **inside `registries/platform.yaml`** | **L4** (event envelope) | §52.6 (4613–4648): "`platform.yaml` … the closed `event_type` enum of the Section 97.3 event taxonomy"; D103 |
| Supported-contract-version floor and canary-set membership in `registries/platform.yaml` | L3 (reconciler staging), L2 (rollout) | §60.2 (5152–5214); §60.3 (5193–5214); D93 |
| Validator entrypoints with defined exit codes | **L2** (wires them into `.github/workflows/**`) | §99.2 row B |
| `registries/exceptions.yaml` + its schema (expiry, owner, deactivation trigger mandatory) | L3 (expiry revocation), L5 (bootstrap gates) | §54 (4746–4829); invariant 77 |
| `registries/people.yaml` incl. `work_arrangement.accepted_coverage_window` | L3, L5 | §7.3 (621–633); D111; D112 |

---

## 7. Merge-train position and why L1 is first

PARTITION line 35: **`L1 → L4 → L2 → L3 → L5`**, once per cycle, into `integration`.

PARTITION lines 39–41 give the reason, and the spec corroborates it twice:

- PARTITION line 39: *"L1 (schemas) and L4 (record schemas) produce what everything validates against."*
- Spec §99.2 (9184–9231), dependency spine: *"A (registries) → B (validation) → C (reconciliation) and D (provisioning)"* — B depends on A; C and D depend on A and B.
- Spec §99.2 table, "Depends on" column: **A depends on nothing.** It is the only subsystem in L1's scope with no upstream. B depends only on A. Both are inside L1, so L1 is internally closed and can merge with zero inbound dependencies.
- Spec §98.2 Phase 1 (8992–9090) puts *"Create the control-plane repository; author `people.yaml`, `roles.yaml`, `platform.yaml`"* in Week 1, and Phase 3 *"Registries and Standards (Week 3)"* before Phase 4 environments and Phase 6 pipeline.

**Operational consequence for the executor:** an L1 branch is rebased on `integration` before its PR (PARTITION line 34), but L1 never waits on another lane's merge. If an L1 task appears to be blocked on L2/L3/L4/L5 output, that is a partition error — **STOP and file a blocker (§13)**; do not work around it by editing a foreign path.

---

## 8. Complete list of spec sections L1 implements

Line ranges are inclusive and were resolved against the frozen spec file. Task **L1-00-04** re-verifies every one of them mechanically. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

| Spec section | Lines | What L1 builds from it |
|---|---|---|
| §4.3 Prohibited hard-coding | 243–257 | Schema rule: no person name, no product name, no product count encoded in any schema `enum` |
| §5 Source of Truth Hierarchy | 321–402 | Precedence order encoded in validator conflict resolution |
| §6.1 The two criticality fields | 407–417 | `business.criticality` and `classification.reliability_criticality` as two distinct required fields (D4) |
| §7 People Registry (incl. 7.1 rules, 7.2 leave, 7.3 work arrangement) | 543–633 | `people.v1.schema.json`; `end_date` mandatory for non-employees; legal `availability`×`access_status` pairings; minimum-authority defaults; `work_arrangement` (D111) |
| §8 Role Registry | 634–686 | `roles.v1.schema.json`; role defaults carry no dangerous capability (D106) |
| §9 Capability Model + 9.1 rules | 687–724 | `capabilities.v1.schema.json` as the closed vocabulary; reject undefined capability anywhere (D81, D90); `people-intelligence` non-delegable |
| §10 Assignment Registry and Delegation | 725–807 | Assignment block in `product.v1.schema.json`; mandatory `end_date` on temporary assignments; `founder_decision_delegate` scope exclusions (D108) |
| §12.4 Contractor and temporary specialist model | 1046–1077 | `end_date` mandatory, CI fails if null |
| §13.1 Acting Team Lead / succession block | 1133–1155 | `topology.v1.schema.json` succession block |
| §15 Product Operating Contract (all of 15.1–15.8) | 1284–1606 | `product.v1.schema.json`; **§15.5 CI validation (1564–1582) is the primary rule list for subsystem B**; conformance profiles (15.7, D50); `launch_status` vs `lifecycle` (15.8) |
| §17.1–17.3 Ownership and the reviewer matrix | 1643–1693 | Four ownership relationships as required contract fields (invariant 7) |
| §18.1–18.2 Lifecycle states and transitions | 1748–1783 | Closed `lifecycle` enum and legal transitions (D103) |
| §20 Shared Services and the dependency graph | 2027–2112 | `service.v1.schema.json`; referential check "dependency names an existing service" |
| §21 Customer Commitments and SLA Registry (incl. 21.4 conflict table 2166–2194) | 2113–2194 | `commitments` block; `conflict_check` required; the `check-commitment` CLI |
| §26.4 The registry-change lane | 2526–2534 | Authority-delta rule: a diff adding a capability, adding a Write-conferring assignment type, or changing `access_status` fails CI without a linked decision-record ID in the same commit (D93) |
| §31 Verification Contract | 2741–2802 | `verification-contract.v1.schema.json` (invariant 1) |
| §38.1 The `ai_runtime_dependency` block | 3373–3414 | Schema block + CI rule (AT-049) |
| §44.1–44.2 Backup declarations and restore cadence | 3963–4002 | `restore_tested` date rule; 90-day floor, tightening only (invariant 4, D5) |
| §52.6 Registry of control-plane files | 4613–4648 | The authoritative inventory of which registry files exist at all (D36) |
| §54 Exception Registry and Break-Glass | 4746–4829 | `exceptions.v1.schema.json`; exception without expiry is invalid and fails CI (invariant 77) |
| §55 Policy Lifecycle and Gradual Enforcement | 4830–4906 | `policies.v1.schema.json`; a new policy may not begin at Enforce unless critical security control (invariant 78) |
| §59.3 Change budget | 5083–5102 | `platform-roadmap.v1.schema.json` |
| §60 Platform Versioning, Versioned Contracts, Compatibility | 5119–5214 | The multi-version schema discipline; `contract_version` / `registry_version` / `service_version` fields; `platform_compatibility` states (SIG-10) |
| §62.1 The tool register | 5289–5357 | `tools.v1.schema.json`: owner, version, purpose, exit condition |
| §64.1–64.2 Safe defaults and fail-closed classification | 5433–5468 | Missing/malformed resolves to denial; **unclassified-control rejection** (invariant 80) |
| §66.2 Domains | 5508–5541 | `topology.v1.schema.json` domains block (AT-016) |
| §68.1 The Product Load Unit | 5624–5655 | `economics.v1.schema.json` load-model weights |
| §76.2–76.4 Person record, Role Profile, prohibited hard-coding | 6253–6300 | People-layer entity schemas with effective dating |
| §77 Performance Framework Registry | 6339–6405 | `framework.v1.schema.json` — definitions only, never individual evidence |
| §91.2 No-surveillance design | 8079–8095 | Banned measurements are **absent from the schema** and rejected if introduced (AT-075) |
| §95.2 Bootstrap exceptions | 8644–8684 | Bootstrap entries validate under `exceptions.v1.schema.json` with mandatory expiry + activation checklist |
| §96.2 Pre-onboarding operating mode | 8720–8760 | The Phase-2 stub `product.yaml`: identity plus the onboarding block only, and the onboarding block removed at onboarding completion |
| §99.2 The subsystem architecture | 9184–9231 | This charter's scope definition |
| §100 Acceptance Tests | 9295–9442 | The AT rows in §9.2 below |
| §101 Non-Negotiable Invariants | 9443–9600 | The invariant rows in §9.1 below |

---

## 9. What L1 is accountable for, by identifier

Never cite an identifier not in these tables. Every one below was read from the spec at the line given.

### 9.1 Invariants L1 enforces mechanically (Section 101, lines 9443–9600)

| # | Invariant (abbreviated) | L1's mechanical enforcement |
|---|---|---|
| 1 | No product completes onboarding without a verification contract | `verification-contract.v1.schema.json` + presence rule |
| 4 | Restore-tested within any rolling 90-day window; criticality tightens, never loosens; a stale `restore_tested` date fails CI | date rule in `validators/registry/rules/` |
| 7 | Every product has Primary Owner, Cross-Reviewer, Backup Owner and Escalation path recorded in the contract | required fields in `product.v1.schema.json` |
| 11 | Authority is evaluated against capability and assignment, never role name alone | capability schema; assignment×capability cross-check |
| 31 | A 24x7 support commitment cannot be accepted without funded response capacity | the 24x7 blocker (§15.6, 1583–1586) |
| 37 | No automatic formal improvement plan / termination / promotion / compensation change / formal warning | no such field exists in any L1 schema; attempted configuration fails validation (AT-071) |
| 50 | People, roles, capabilities and assignments are separate concepts, each dynamic configuration | four separate schemas, no merging |
| 51 | People are never hard-coded into architecture logic | no person identifier in any schema enum |
| 52 | Product count is never hard-coded | no product enum, no fixed-length arrays |
| 58 | Temporary assignments carry a mandatory end date and expire without human action | `end_date` required; expired assignment fails CI |
| 73 | Contract schemas are versioned, and simultaneous fleet migration is never required | §3.1 versioning rule; v1 never deleted |
| 77 | Every exception has an expiry; an exception without one is invalid and **fails CI**; a re-opened same-scope exception counts as a renewal | `exceptions.v1.schema.json` |
| 78 | A new policy may not begin at Enforce unless it is a critical security control | `policies.v1.schema.json` |
| 79 | New people, products and tools default to minimum privilege and draft state | schema defaults (D106) |
| 80 | **Every control is explicitly classified fail-closed or fail-open** | unclassified-control rejection — named in §99.2 row B |
| 96 | No keystroke, screen, webcam or online-presence surveillance | banned measurements absent from schema (AT-075) |
| 98/99 | No single-number productivity score; no employee ranking or leaderboard | no such field in `framework.v1.schema.json` |
| 106 | `people-intelligence` is Founder-only and **not delegable** | assignment granting it fails validation (AT-090) |

### 9.2 Acceptance tests L1 must make passable (Section 100, lines 9295–9442)

| AT | Pass condition L1 supplies |
|---|---|
| AT-001 | "No dashboard, workflow or script contains a product list" — enforced at the schema layer by L1 |
| AT-007 | A new role is introduced: role profile plus framework mapping added; no architecture change |
| AT-008 | Contractor entry is scoped, dated, capability-limited; expiry handled |
| AT-009 | Conformance profile validation (`service` … `static-site`) |
| AT-016 | "Only `topology.yaml` changes" for a second Team Lead and domains |
| AT-025 | A platform contract schema changes — both versions supported simultaneously |
| AT-034 | Governance layerability — the removable governance artifacts named by file: `os-health.yaml`, `policies.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml`; **the exception registry is core-resident and never removed** |
| AT-047 | A declared `coverage_window` not fully covered by active rota members' accepted windows **fails contract validation** (D112) |
| AT-049 | `ai_runtime_dependency` without an evaluation suite under `verification/` fails CI |
| AT-051 | Brownfield pre-onboarding stub validates with identity + onboarding block only |
| AT-071 | "attempted configuration of one fails validation" — no code path to an automated people action |
| AT-075 | "Banned measurements are absent from the schema and rejected if introduced" |
| AT-090 | "an attempt to create an assignment granting `people-intelligence` fails validation" |

### 9.3 Signals fed by L1 data (Section 52.2, lines 4520–4586)

| SIG | Name | L1's contribution |
|---|---|---|
| SIG-05 | Orphan risk | Source column is **Registries** — L1's `product.yaml` ownership fields make it computable |
| SIG-10 | Transitional compatibility backlog | `platform_compatibility` field, §60.3 |
| SIG-20 | Policy currency | `policies.yaml` review dates |
| SIG-22 | Missing framework evidence | `framework.v1.schema.json` instrumentation-status field |
| SIG-39 | Bootstrap exception unclosed | `exceptions.yaml` expiry + deactivation trigger |

### 9.4 Consolidation decisions binding on L1 (Appendix A, lines 10058–10214)

| D | Binding effect on L1 |
|---|---|
| D4 | Two criticality fields, deliberately distinct — both required |
| D5 | 90-day restore floor; tightening only |
| D36 | The registry-of-files table is the complete inventory |
| D50 | Conformance profiles; validation resolves against the declared profile |
| D81 | Every capability defined before granted; CI rejects an undefined capability in a role default, person grant or assignment type |
| D90 | Same rule swept to completion; `devops` capability defined |
| D93 | Registry edits canary first; an **authority delta** fails CI without a linked decision-record ID in the same commit |
| D103 | Records, events and the states they describe carry schemas; closed exception-closure enum; closed product-lifecycle table; `access_status: suspended` gains its exit transition |
| D106 | The dangerous capability set is explicit-grant-only; CI rejects a role default containing any of them |
| D108 | `founder_decision_delegate` scope excludes formal people decisions by name; a delegation naming one fails schema validation |
| D111 | `work_arrangement` block: IANA timezone, per-weekday schedule, FTE, arrangement, public-holiday set |
| D112 | `accepted_coverage_window` on the person record is the input the coverage validator resolves against; fails closed |

---

## 10. Definition of Done for Lane 1

L1 is done when **all eleven** of the following are true. Each is provable by a command; no item is a matter of opinion.

| # | DoD item | Proof |
|---|---|---|
| DoD-1 | Every schema file named in §3.1 exists and is itself a valid JSON Schema document | schema-of-schemas run exits 0 |
| DoD-2 | Every registry file named in §52.6 that L1 owns exists under `registries/` and validates against its schema | validator run exits 0 |
| DoD-3 | Every rule in §15.5 (spec 1564–1582) has exactly one file under `validators/registry/rules/` and at least one invalid fixture that it rejects | rule-to-fixture coverage check exits 0 |
| DoD-4 | Every invariant in §9.1 of this charter has a named check or fixture | invariant coverage check exits 0 |
| DoD-5 | Every AT in §9.2 of this charter has a fixture pair (valid + invalid) | AT coverage check exits 0 |
| DoD-6 | No `*.v1.schema.json` has been deleted or overwritten since first merge (§60.2 discipline) | `git log --diff-filter=D -- schemas/` returns empty |
| DoD-7 | No L1 commit touches a foreign path | `validators/registry/_meta/lane_paths.sh` exits 0 on every commit in the lane |
| DoD-8 | Spec Phase 1 completion check is satisfied for L1's part: *"the minimal `exceptions.yaml` schema validator (expiry, owner, deactivation trigger present) is active in control-plane CI and rejects a deliberately malformed exception"* (spec §98.2, Phase 1 completion check) | the deliberately malformed fixture is rejected with a non-zero exit |
| DoD-9 | Spec Phase 3 completion check is satisfied for L1's part: *"contracts validate"* (spec §98.2, Phase 3 completion check) | `product.yaml` for every product validates at `contract_version: 1` |
| DoD-10 | No banned measurement field exists anywhere in `schemas/**` (AT-075) | banned-term grep over `schemas/` returns no match |
| DoD-11 | Every §12 DECISION REQUIRED item is either resolved by L0 in `contracts/**` or carries an open blocker issue | blocker ledger check |

**L1 is NOT done because the code "looks complete". It is done when the eleven commands above exit 0.**

---

## 11. Charter tasks

These five tasks establish the lane. They are the prerequisite for every later L1 document.
All commands are POSIX `sh`/`bash`. Run them from the **root of the `control-plane` repository working tree**.

### Conventions binding on every L1 task, here and in every later L1 file

| Convention | Value |
|---|---|
| Working directory | root of the `control-plane` repository working tree |
| Branch naming | `lane/1/<phase>-<task>` — e.g. `lane/1/00-charter` |
| Base branch | `integration` |
| Rebase before PR | mandatory (PARTITION line 34) |
| Commit message prefix | `L1: ` |
| Exit-code convention | `0` = pass, non-zero = fail. Never print "OK" on failure. |

---

### L1-00-01 — Verify preconditions and create the lane branch <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** none

**Creates or edits:** no files. Branch only.

**Commands**

```bash
set -e

# 1. Prove we are in a git working tree at its root.
test -d .git || { echo "FAIL: not at the root of a git working tree"; exit 1; }

# 2. Prove L0 Phase 0 has landed: contracts/ exists and is non-empty (PARTITION line 26).
test -d contracts || { echo "FAIL: contracts/ absent - L0 Phase 0 has not landed"; exit 1; }
test -n "$(ls -A contracts)" || { echo "FAIL: contracts/ is empty"; exit 1; }

# 3. Prove the integration branch exists.
git rev-parse --verify integration >/dev/null 2>&1 \
  || { echo "FAIL: branch 'integration' does not exist"; exit 1; }

# 4. Prove no foreign lane prefix already exists that L1 would collide with.
for p in reconciler tools/provision validators/drift metrics access infra ops-vm notify assets; do
  if [ -e "$p" ]; then echo "INFO: foreign path present (expected, do not touch): $p"; fi
done

# 5. Create the lane branch from integration.
git checkout integration
git pull --ff-only
git checkout -b lane/1/00-charter

echo "T01-PASS"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous correct output |
|---|---|---|---|
| A1 | `contracts/` exists and is non-empty | `test -d contracts && test -n "$(ls -A contracts)"; echo $?` | `0` |
| A2 | Current branch is `lane/1/00-charter` | `git rev-parse --abbrev-ref HEAD` | `lane/1/00-charter` |
| A3 | The branch is based on `integration` | `git merge-base --is-ancestor integration HEAD; echo $?` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
git rev-parse --abbrev-ref HEAD && test -d contracts && git merge-base --is-ancestor integration HEAD && echo "T01-VERIFIED"
```

Correct output: the two lines `lane/1/00-charter` then `T01-VERIFIED`.

**STOP rule** — do not proceed to T02 if **any** of:
- `contracts/` is absent or empty (L0 has not landed Phase 0);
- branch `integration` does not exist;
- any of the five facts C1–C5 in §5 cannot be located in `contracts/**`.

File the blocker of §13 with `BLOCKER-KIND: MISSING-CONTRACT` and stop.

---

### L1-00-02 — Create the four owned roots and their README markers <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-00-01 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `schemas/registry/README.md`
- `schemas/product/README.md`
- `registries/README.md`
- `validators/registry/README.md`
- `validators/registry/_meta/.gitkeep`
- `validators/registry/fixtures/valid/.gitkeep`
- `validators/registry/fixtures/invalid/.gitkeep`
  <!-- # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/ -->
- `validators/registry/rules/.gitkeep`
- `validators/registry/schema/.gitkeep`
- `validators/registry/bin/.gitkeep`

**Commands**

```bash
set -e
mkdir -p schemas/registry schemas/product registries \
         validators/registry/_meta \
         validators/registry/fixtures/valid \
         validators/registry/fixtures/invalid \
         validators/registry/rules \
         validators/registry/schema \
         validators/registry/bin

for d in validators/registry/_meta validators/registry/fixtures/valid \
         validators/registry/fixtures/invalid validators/registry/rules \
         validators/registry/schema validators/registry/bin; do
  : > "$d/.gitkeep"
done

cat > schemas/registry/README.md <<'EOF'
# schemas/registry — OWNED BY LANE 1 (Registries & Contracts)

Subsystem A of spec Section 99.2 (lines 9184-9231).
JSON Schema documents for the control-plane registries listed in spec Section 52.6 (lines 4613-4648).

RULES
- Additive only. A `*.vN.schema.json` file is NEVER deleted or overwritten once merged
  (spec Section 60.2, lines 5152-5214: "Write the v2 schema alongside v1 - do not replace").
- No person identifier, product identifier or product count appears in any enum
  (spec Section 4.3, lines 243-257; invariants 51 and 52).
- No lane other than L1 writes here.
EOF

cat > schemas/product/README.md <<'EOF'
# schemas/product — OWNED BY LANE 1 (Registries & Contracts)

Per-product contract schemas:
- Product Operating Contract      -> spec Section 15  (lines 1284-1606)
- Verification Contract           -> spec Section 31  (lines 2741-2802)
- Shared Service Contract         -> spec Section 20  (lines 2027-2112)

RULES
- Version fields per spec Section 60.2 (lines 5152-5214):
  product.yaml -> contract_version; verification/contract.yaml -> contract_version;
  service.yaml -> service_version.
- Additive only. No lane other than L1 writes here.
EOF

cat > registries/README.md <<'EOF'
# registries — OWNED BY LANE 1 (Registries & Contracts)

The authoritative control-plane registry instances of spec Section 52.6 (lines 4613-4648).

RULES
- One file per registry. Directory-per-item where a registry holds many entries
  (PARTITION rule 3: no shared mutable index).
- registries/platform.yaml carries the closed `event_type` enum consumed by Lane 4
  (spec Section 52.6; decision D103).
- An authority delta - adding a capability, adding a Write-conferring assignment type,
  or changing access_status - fails CI without a linked decision-record ID in the same
  commit (spec Section 26.4, lines 2526-2534; decision D93).
- No lane other than L1 writes here.
EOF

cat > validators/registry/README.md <<'EOF'
# validators/registry — OWNED BY LANE 1 (Registries & Contracts)

Subsystem B of spec Section 99.2 (lines 9184-9231): multi-version schema validators,
referential integrity, date rules, the 24x7-without-rota and commitments-conflict blockers,
exception-without-expiry rejection, unclassified-control rejection.

LAYOUT
  schema/            multi-version schema validation driver
  rules/             one file per non-schema rule; the rule list is spec Section 15.5 (lines 1564-1582)
  fixtures/valid/    golden fixtures that MUST pass
  fixtures/invalid/  golden fixtures that MUST fail - one per rule
  # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/
  bin/               executable entrypoints, including check-commitment (spec Section 21.4, lines 2166-2184)
  _meta/             lane self-guard and spec-anchor files

EXIT CODES: 0 = pass, non-zero = fail. Never print a success string on failure.

NOT OWNED HERE: validators/drift/** belongs to Lane 3. Read the prefix.
EOF

echo "T02-PASS"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous correct output |
|---|---|---|---|
| A1 | All four README files exist | `ls schemas/registry/README.md schemas/product/README.md registries/README.md validators/registry/README.md >/dev/null 2>&1; echo $?` | `0` |
| A2 | All six validator subdirectories exist | `for d in _meta fixtures/valid fixtures/invalid rules schema bin; do test -d "validators/registry/$d" \|\| exit 1; done; echo $?` | `0` |
| A3 | No file was created outside the four owned prefixes | `git status --porcelain \| awk '{print $2}' \| grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
git status --porcelain | awk '{print $2}' | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' | wc -l
```

Correct output: exactly `0`.

**STOP rule** — do not proceed to T03 if criterion A3 returns anything other than `0`. That means a foreign path was touched, which fails the lane-guard check (PARTITION rule 1). Revert with `git checkout -- .` and file the blocker of §13 with `BLOCKER-KIND: FOREIGN-PATH`.

---

### L1-00-03 — Install the lane self-guard <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-00-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** `validators/registry/_meta/lane_paths.sh`

This script is run by **every** later L1 task before committing. It is the lane's own copy of PARTITION rule 1.

**Commands**

```bash
set -e
cat > validators/registry/_meta/lane_paths.sh <<'EOF'
#!/usr/bin/env bash
# Lane 1 self-guard. Fails if the working tree or the branch diff touches a foreign path.
# PARTITION.md rule 1: "One owner per path. A lane PR touching a foreign path FAILS."
# Owned prefixes are copied verbatim from PARTITION.md line 17 and are not editable here.
set -euo pipefail
ALLOW='^(schemas/registry/|schemas/product/|registries/|validators/registry/)'
BASE="${1:-integration}"

changed="$( { git diff --name-only "$BASE"...HEAD 2>/dev/null || true;
              git status --porcelain | awk '{print $2}'; } | sort -u )"

bad="$(printf '%s\n' "$changed" | grep -v -E "$ALLOW" | grep -v '^$' || true)"

if [ -n "$bad" ]; then
  echo "LANE-GUARD-FAIL: foreign paths touched by lane/1:"
  printf '%s\n' "$bad"
  exit 1
fi
echo "LANE-GUARD-PASS"
exit 0
EOF
chmod +x validators/registry/_meta/lane_paths.sh
./validators/registry/_meta/lane_paths.sh integration
echo "T03-PASS"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous correct output |
|---|---|---|---|
| A1 | The guard exists and is executable | `test -x validators/registry/_meta/lane_paths.sh; echo $?` | `0` |
| A2 | The guard passes on the current clean lane branch | `./validators/registry/_meta/lane_paths.sh integration` | `LANE-GUARD-PASS` |
| A3 | The guard actually catches a foreign path | `touch docs/__probe.tmp && ./validators/registry/_meta/lane_paths.sh integration; echo "exit=$?"; rm -f docs/__probe.tmp` | first line `LANE-GUARD-FAIL: foreign paths touched by lane/1:`, last line `exit=1` |

**SELF-VERIFY**

```bash
set -euo pipefail
./validators/registry/_meta/lane_paths.sh integration && echo "T03-VERIFIED"
```

Correct output: `LANE-GUARD-PASS` then `T03-VERIFIED`.

**STOP rule** — do not proceed if A3 does **not** produce `exit=1`. A guard that fails to catch a deliberately planted foreign path is a broken guard, and every later L1 task depends on it. Delete `docs/__probe.tmp` if it survives, then file the blocker of §13 with `BLOCKER-KIND: GUARD-BROKEN`.

---

### L1-00-04 — Pin and verify the spec anchors used by this lane <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-00-03 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `validators/registry/_meta/spec-anchors.tsv`
- `validators/registry/_meta/check_spec_anchors.sh`

Every later L1 document cites spec sections by line range. If the spec file changes, those citations rot silently.
This task pins them and gives the lane a one-command drift check.

**Commands**

```bash
set -e
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
test -f "$SPEC" || { echo "FAIL: spec not found at $SPEC"; exit 1; }

cat > validators/registry/_meta/spec-anchors.tsv <<'EOF'
# heading_regex	expected_start_line	charter_section_id
^## Section 7\. People Registry	543	7
^## Section 8\. Role Registry	634	8
^## Section 9\. Capability Model	687	9
^## Section 10\. Assignment Registry and Delegation	725	10
^## Section 15\. Product Operating Contract	1284	15
^## Section 20\. Shared Services and the Dependency Graph	2027	20
^## Section 21\. Customer Commitments and SLA Registry	2113	21
^### 26\.4 The registry-change lane	2526	26.4
^## Section 31\. Verification Contract	2741	31
^### 38\.1 The ai_runtime_dependency block	3373	38.1
^### 44\.1 Per-product declarations	3963	44.1
^### 52\.6 Registry of control-plane files	4613	52.6
^## Section 54\. Exception Registry and Break-Glass	4746	54
^## Section 55\. Policy Lifecycle and Gradual Enforcement	4830	55
^## Section 60\. Platform Versioning, Versioned Contracts and Compatibility	5119	60
^### 62\.1 The tool register	5289	62.1
^### 64\.1 Safe defaults	5433	64.1
^### 66\.2 Domains	5508	66.2
^### 68\.1 The Product Load Unit	5624	68.1
^## Section 77\. Performance Framework Registry	6339	77
^### 91\.2 No-surveillance design	8079	91.2
^### 96\.2 Pre-onboarding operating mode	8720	96.2
^### 99\.2 The subsystem architecture	9184	99.2
^## Section 100\. Acceptance Tests	9295	100
^## Section 101\. Non-Negotiable Invariants	9443	101
EOF

cat > validators/registry/_meta/check_spec_anchors.sh <<'EOF'
#!/usr/bin/env bash
# Verifies every spec line-range citation used by Lane 1 still resolves.
# Usage: check_spec_anchors.sh <path-to-MultiProduct_MasterSpec_v4.0.md>
set -euo pipefail
SPEC="${1:?usage: check_spec_anchors.sh <spec-file>}"
TSV="$(dirname "$0")/spec-anchors.tsv"
fail=0
while IFS=$'\t' read -r re want id; do
  case "$re" in \#*|'') continue;; esac
  got="$(grep -n -m1 -E "$re" "$SPEC" | cut -d: -f1)"
  if [ "$got" != "$want" ]; then
    echo "ANCHOR-DRIFT: section $id expected line $want, found '${got:-none}'"
    fail=1
  fi
done < "$TSV"
if [ "$fail" -ne 0 ]; then echo "SPEC-ANCHORS-FAIL"; exit 1; fi
echo "SPEC-ANCHORS-PASS"
exit 0
EOF
chmod +x validators/registry/_meta/check_spec_anchors.sh
./validators/registry/_meta/check_spec_anchors.sh "$SPEC"
echo "T04-PASS"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous correct output |
|---|---|---|---|
| A1 | The anchor file has 25 data rows | `grep -vc '^#' validators/registry/_meta/spec-anchors.tsv` | `25` |
| A2 | Every anchor resolves | `./validators/registry/_meta/check_spec_anchors.sh "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"` | `SPEC-ANCHORS-PASS` |
| A3 | The lane guard still passes | `./validators/registry/_meta/lane_paths.sh integration` | `LANE-GUARD-PASS` |

**SELF-VERIFY**

```bash
set -euo pipefail
./validators/registry/_meta/check_spec_anchors.sh "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md" \
  && ./validators/registry/_meta/lane_paths.sh integration \
  && echo "T04-VERIFIED"
```

Correct output: `SPEC-ANCHORS-PASS`, then `LANE-GUARD-PASS`, then `T04-VERIFIED`.

**STOP rule** — do not proceed if any line prints `ANCHOR-DRIFT`. The spec has moved under this charter, and every
line-range citation in every L1 document is now suspect. **Do not "fix" the numbers.** File the blocker of §13 with
`BLOCKER-KIND: SPEC-DRIFT`, listing every `ANCHOR-DRIFT` line verbatim, and stop.

---

### L1-00-05 — Commit the charter scaffold and open the lane PR <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-00-04 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates or edits:** no new files. Commits T02–T04 output.

**Commands**

```bash
set -e
./validators/registry/_meta/lane_paths.sh integration

git add schemas/registry schemas/product registries validators/registry
git status --porcelain

git commit -m "L1: charter scaffold - owned roots, lane self-guard, spec anchors

Subsystems A and B of spec Section 99.2 (lines 9184-9231).
Owned paths per PARTITION.md line 17: schemas/registry/**, schemas/product/**,
registries/**, validators/registry/**.
Adds the lane self-guard (PARTITION rule 1) and the spec-anchor drift check.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"

git fetch origin
git rebase origin/integration
./validators/registry/_meta/lane_paths.sh origin/integration
git push -u origin lane/1/00-charter
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous correct output |
|---|---|---|---|
| A1 | Exactly one commit ahead of `integration` | `git rev-list --count origin/integration..HEAD` | `1` |
| A2 | Every changed file is inside an owned prefix | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` | `0` |
| A3 | The branch is pushed | `git rev-parse --abbrev-ref --symbolic-full-name @{u}` | `origin/lane/1/00-charter` |

**SELF-VERIFY**

```bash
set -euo pipefail
git rev-list --count origin/integration..HEAD \
  && git diff --name-only origin/integration...HEAD \
  && ./validators/registry/_meta/lane_paths.sh origin/integration \
  && echo "T05-VERIFIED"
```

Correct output: `1`, then only paths beginning `schemas/registry/`, `schemas/product/`, `registries/` or
`validators/registry/`, then `LANE-GUARD-PASS`, then `T05-VERIFIED`.

**STOP rule** — do not open the PR, and do not force-push, if:
- A2 returns anything other than `0`;
- the rebase produces a conflict in a file **not** under an owned prefix (that is a partition violation by another lane — PARTITION line 36 forbids L1 from touching another lane's branch);
- `origin/integration` does not exist.

File the blocker of §13 with `BLOCKER-KIND: MERGE-TRAIN` and stop. **Never** resolve a foreign-path conflict; never merge or rebase another lane's branch.

---

## 12. DECISION REQUIRED — escalated to L0

These are genuine gaps between PARTITION.md and spec Section 52.6 / Section 99.2. **No L1 executor may resolve any of them.**
Each blocks the L1 file named in "Blocks". Until L0 answers in `contracts/**`, the L1 executor treats the artifact as **not owned** and does not create it.

---

> ### DECISION REQUIRED #1 — `ai-toolchain.yaml` has no owning path
>
> **Facts.** Spec §52.6 (lines 4613–4648) lists `ai-toolchain.yaml` as a control-plane artifact owned by the Team Lead:
> *"Approved AI runtimes, extensions and MCP-style tool servers, pinned by version (Section 36)."*
> Spec §99.2 (lines 9184–9231) assigns AI runtime contract enforcement to **subsystem K**, and PARTITION line 21 assigns K to **L5**.
> PARTITION grants L5 the prefixes `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` — **none of which is `registries/**`**, which L1 owns exclusively.
> **Question for L0.** Does `ai-toolchain.yaml` and its schema live in L1's `registries/**` + `schemas/registry/**` (L1 authors the schema, L5 authors nothing), or does L0 grant L5 a new prefix?
> **Blocks.** Any L1 file that would create `registries/ai-toolchain.yaml`.
> **L1 default pending answer.** Do not create it. Do not reference it in any validator.
> **FD-058 recorded 2026-09-06 confirms charter wins.** L1-02-16 is OUT-OF-SCOPE per FD-058.

---

> ### DECISION REQUIRED #2 — subsystems G, H, J, O and P are unassigned
>
> **Facts.** Spec §99.2 (lines 9184–9231) defines subsystems A–R. PARTITION lines 17–21 assign A, B (L1); E, F (L2); C, D (L3); I, N (L4); K, L, M, Q, R (L5).
> **G** (plan-checker), **H** (dashboards), **J** (background machine layer), **O** (governance registries and jobs) and **P** (people intelligence engine) are assigned to no lane.
> This matters to L1 because subsystem **O** — *"Exception lifecycle with auto-expiry and renewal counting; policy enforcement stages; pattern detector; learning-loop tracking; change budget and churn counters; exit checklists; tool register"* — reads and writes the governance registers whose **files and schemas** fall inside L1's `registries/**` and `schemas/registry/**`.
> **L1's reading, stated so it can be corrected.** L1 owns the *schemas and the registry files* for `exceptions.yaml`, `policies.yaml`, `patterns.yaml`, `os-health.yaml`, `economics.yaml`, `platform-roadmap.yaml` and `tools.yaml`, because they sit inside owned prefixes and spec §99.2 row A names them explicitly. L1 does **not** own the O-subsystem *jobs* (expiry counter, pattern detector, learning-loop tracker).
> **Question for L0.** Confirm that reading, and name the lane that owns the O jobs.
> **Blocks.** `L1-0N-governance-registries` (schema work may proceed under L1's reading; job work may not).

---

> ### DECISION REQUIRED #3 — `changes/**`, `scenarios/**` and leave records have no owning prefix
>
> **Facts.** Spec §52.6 (lines 4613–4648) lists three further hand-maintained control-plane artifacts:
> `changes/*.yaml` (change manifests, spec §25 lines 2437–2488), `scenarios/*.yaml` (spec §72.5 lines 5932–5969),
> and **Leave records** (*"Source of truth for leave and planned absence, and for the company working calendar"*, spec §7.2 lines 612–620).
> No lane in PARTITION owns `changes/**` or `scenarios/**`. Leave records are a load-bearing input to L1's `people.yaml` `availability` field (spec §7.2) but have no declared home.
> **Question for L0.** Where do these three live, and which lane authors their schemas? If they belong under `registries/**`, they are L1's by path ownership and L1 needs that stated.
> **Blocks.** The `availability` transition rule in `people.v1.schema.json` cannot cite its source until leave records have a home.
> **L1 default pending answer.** Model `availability` as a plain enum with no cross-file reference; add no leave-record validator.
> **FD-058 recorded 2026-09-06 confirms charter wins.** L1-02-17 (scenarios/*.yaml) and L1-02-18 (changes/*.yaml) are OUT-OF-SCOPE per FD-058.

---

> ### DECISION REQUIRED #4 — the CI invocation boundary between L1 and L2
>
> **Facts.** Spec §99.2 (lines 9184–9231) names subsystem B *"Schema validation and CI gate engine"* and assigns it to L1. PARTITION line 18 assigns `.github/workflows/**` to **L2**. So L1 owns the engine and L2 owns the trigger.
> Spec §98.2 Phase 1 completion check requires *"the minimal `exceptions.yaml` schema validator … is **active in control-plane CI** and rejects a deliberately malformed exception"* — an L1 DoD item (DoD-8) that only an L2-owned file can make true.
> **Question for L0.** Confirm that fact **C1** of §5 (the validator invocation contract: command line, exit codes, machine-readable output shape) is present and frozen in `contracts/**`, so L1 and L2 can build to it without either lane editing the other's tree.
> **Blocks.** DoD-8 and DoD-9 cannot be marked done by L1 alone.
> **L1 default pending answer.** Build every validator as a standalone executable with `validators/registry/ci-preflight.sh` as the single L2-facing entry point (the path L1-04 freezes), with documented exit codes. Do not create, edit or propose any file under `.github/`.

---

## 13. Blocker-issue template

When any STOP rule fires, the executor stops immediately and files exactly this issue. It does not improvise a workaround.

```bash
set -euo pipefail
gh issue create \
  --title "L1 BLOCKER: <one-line summary>" \
  --label "blocker,lane-1" \
  --body "$(cat <<'EOF'
BLOCKER-KIND: <MISSING-CONTRACT | FOREIGN-PATH | GUARD-BROKEN | SPEC-DRIFT | MERGE-TRAIN | DECISION-REQUIRED>
LANE: L1 Registries & Contracts (subsystems A, B - spec Section 99.2, lines 9184-9231)
BRANCH: <output of: git rev-parse --abbrev-ref HEAD>
TASK ID: <e.g. L1-00-03>
CHARTER: Code/implementation/lanes/L1-00-charter.md

WHAT I WAS ASKED TO DO
<verbatim task title from the charter>

THE STOP RULE THAT FIRED
<verbatim STOP-rule text from the task>

COMMAND I RAN
```
<verbatim command>
```

OUTPUT I GOT
```
<verbatim output, unedited>
```

OUTPUT THE CHARTER SAYS IS CORRECT
<verbatim "correct output" line from the SELF-VERIFY block>

WHAT I DID NOT DO
- I did not edit any path outside schemas/registry/**, schemas/product/**, registries/**, validators/registry/**.
- I did not edit contracts/**.
- I did not merge, rebase or push any other lane's branch.
- I did not change the charter's line-range citations.
- I made no design choice.

DECISION NEEDED FROM L0
<one sentence: the single question whose answer unblocks this>
EOF
)"
```

If `gh` is unavailable, the executor stops anyway and writes the same body to standard output for the operator to file. It does **not** proceed.

---

## 14. Summary card

| Field | Value |
|---|---|
| Lane | L1 Registries & Contracts |
| Subsystems | A, B (spec §99.2, lines 9184–9231) |
| Owned prefixes | `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` |
| Branch prefix | `lane/1/*` |
| Merge position | 1 of 5 — `L1 → L4 → L2 → L3 → L5` |
| Consumes | `contracts/**` facts C1–C5 only |
| Publishes | Schemas, registry instances, validators, golden fixtures, the closed `event_type` enum, the closed capability vocabulary |
| Charter tasks | L1-00-01 … L1-00-05 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| DoD items | DoD-1 … DoD-11 |
| Open L0 decisions | 4 (§12) |
