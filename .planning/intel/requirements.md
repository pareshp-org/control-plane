# Requirements (PRD intel)

Synthesized from classified PRD documents: `master/06-v1-scope.md` and `master/00-MASTER-PLAN.md`. Each PRD yields multiple requirement entries.

---

## REQ-v1-scope-definition
- source: master/06-v1-scope.md
- description: The one-sentence definition of V1 — the Foundation launch-critical set (§98.2, Phases 1–7) applied to 2–3 pilot products, plus the near-free P0 governance design rules baked in from day one, roughly 30% of the build surface.
- acceptance: Delivers exactly four capabilities and no more — declared state enforced, drift visible, orphans impossible to miss, every production artifact traceable (§99.4 opening paragraph). Anything not traceable to one of the nine §3 items or six §4 residuals is **not** in V1; a lane that finds such a task must stop and open a blocker issue.
- scope: V1 scope, pilot products, subsystems A–R

---

## REQ-v1-nine-declared-items
- source: master/06-v1-scope.md
- description: The definitive V1 inventory (§99.4 items 1–9), each with an owning lane / lane set.
- acceptance:
  1. Control-plane repository, schemas and CI validation with effective dating and append-only discipline from the start — L1, L4, L0
  2. GitHub enforcement: one organisation, base Read, Teams-derived Write, branch protection with most-recent-push approval, environments, completion checks executed as written — L5, L3, L0
  3. Scaffolding v0 (`create-product`, `add-person`) — L3
  4. Delivery pipeline with the digest invariant, one tested rollback and one recorded restore test per product — L2, L4
  5. Verification-contract skeleton with CI presence enforcement — L1 (schema), L2 (runner)
  6. Reconciliation v0, detect and block only — L3
  7. Founder view v0 from GitHub API and reconciliation output plus Scorecard — L5, L4
  8. From the governance tier: exception registry with mandatory expiry, safe defaults in provisioning templates, fail-closed classification written down, the control-plane/data-plane invariant test — L1, L3, L5, L2
  9. From the people tier: nothing initially except schemas designed with effective dating — L1 (schema shape only)
- scope: subsystems A,B,C,D,E,F,H,I,K,L,M,N,O,Q,R (partial), governance tier sliver, people tier sliver

---

## REQ-v1-six-residuals
- source: master/06-v1-scope.md
- description: Six items named as day-one binding somewhere in the spec that have no corresponding bullet in §98.2's Phase 1–7 list. §98.2's D99 correction did not close this membership gap; these are in V1 regardless and must not be treated as optional.
- acceptance:
  - R-1: `records/` and `events/` stores and the records repository itself, live before any dashboard reads from them — L4
  - R-2: safe defaults, fail-closed classification, the constitution and the untrusted-input rule, API-key-free environments, digest immutability, append-only history, and the explicit production-approval event — binding even in bootstrap — L5 (K,L), L2 (E), L1 (schemas)
  - R-3: the registry-change lane's staged canary apply and authority-delta gate — L3, L1
  - R-4: the operating system's own standing ledger entry in `economics.yaml` — L1 (file), L0 (content)
  - R-5: the pre-Phase-1 baseline capture for the §103 minimum measure set, recorded before Phase 1 begins — L0
  - R-6: the weekly bootstrap log with its staleness detector, and the one-page per-repository transition note — L1 (CI rule), L4 (store), L0 (note)
- scope: records/events store, bootstrap binding rules, registry-change lane, economics ledger, baseline capture, bootstrap log

---

## REQ-v1-l0-decisions
- source: master/06-v1-scope.md
- description: Six L0-only scope questions (§12) that gate specific sets of V1 lane tasks; none may be resolved by a lane.
- acceptance:
  - V1-D1: Is Phase 7 (GSD activation, subsystem G) inside V1? — three options offered (adopt-only / include in-house fallback / out of V1); recommendation (a) adopt-only
  - V1-D2: Which lane owns Founder-view v0 (subsystem H)? — **Closed: FD-002 → L5** (`ops-vm/**`)
  - V1-D3: Is DevLake installed in V1? — **Closed: FD-112/REG-058 → deferred out of V1**
  - V1-D4: Which products are the pilots, and are there two or three? — **Closed: FD-016 → TWO pilots**, ordered by `reliability_criticality` then `business.criticality` then cheapest onboarding
  - V1-D5: Does the operational asset inventory (subsystem Q) ship a V1 sliver? — **Closed (Decision Signoff §2, 2026-09-02): minimal sliver** — machine-credential rows only
  - V1-D6: How many humans hold Write on the control-plane repository during V1? — **Closed: FD-017 → TWO** (the Founder, L0, FD-001; and Nimesh, Team Lead) on `control-plane` and `product-template`
- scope: GSD activation, dashboards ownership, DevLake, pilot product selection, asset inventory scope, bootstrap headcount

---

## REQ-master-plan-deliverable-classes
- source: master/00-MASTER-PLAN.md
- description: Six deliverable classes constitute the entire build, and nothing else (§1).
- acceptance: (1) schema-and-validator suite — subsystems A,B; (2) reconciliation engine — C; (3) provisioning and scaffolding CLI — D; (4) reusable CI/CD workflow library — E,F; (5) metrics and report computation layer — I,N; (6) dashboard provisioning (JSON in git) — H. Supporting subsystems: K, L, M, O, Q, R. Conditional/deferred subsystems: G, J, P.
- scope: schema-and-validator suite, reconciliation engine, provisioning and scaffolding CLI, CI/CD workflow library, metrics and report computation layer, dashboard provisioning

---

## REQ-master-plan-not-built
- source: master/00-MASTER-PLAN.md
- description: Explicit refusals (§1.1) — a lane developer who finds itself building one of these has misread a task and must STOP. These are refusals, not deferrals of convenience.
- acceptance: no installer/tenancy/upgrade machinery for third parties (Section 99.6 risk 1); no bespoke web application for Layer B people data (§99.5, D75); no separate identity provider (§99.5); no metered-LLM or paid-cloud-LLM dependency in engineering tooling (invariants 83, 84); no second workflow overlay competing with GSD (invariant 43); no automated formal people action (invariant 37, AT-071); no per-person raw-activity drill-down on a general dashboard (invariant 109, AT-089); no keystroke/screen/webcam/presence surveillance, AI-token-as-performance, single-number productivity score, or leaderboard (invariants 96-99, AT-075); no hard-coded product list in any dashboard/workflow/script (AT-001, invariant 52); no background machine layer until its CPU benchmark passes; and the explicitly-deferred list: shared-service registry, split/merge/transfer, dependency-graph views, versioned-contract migration machinery, domains/topology activation, predictive economics/forecasting, Layer B decision support.
- scope: explicit non-goals, deferred capabilities

---

## REQ-master-plan-entry-criteria
- source: master/00-MASTER-PLAN.md
- description: Sixteen entry criteria (§5, `EC-1`..`EC-16`), each an executable command with unambiguous output, that must ALL be green before B-Day (the first lane commit / branch creation). If any one fails, B-Day does not happen.
- acceptance: EC-1 GitHub org plan is Team or higher; EC-2 the three repositories exist; EC-3 `control-plane` carries full branch protection and no machine bypass actor (D89); EC-4 `control-plane-records` has the D107 no-bypass ruleset; EC-5 environment protection rules and Projects aggregation verify; EC-6 no API key anywhere on any machine; EC-7 pre-Phase-1 baselines captured (AT-046); EC-8 bootstrap exceptions authored with a validator that has teeth; EC-9 plan-checker capability verification run against the pinned GSD release; EC-10 DevLake's required database engine/version confirmed; EC-11 the standing `economics.yaml` ledger entry exists with 7 gate answers; EC-12 `contracts/**` authored and FROZEN; EC-13 the lane-guard CI check is live and fails a foreign-path PR; EC-14 CODEOWNERS contains human identities only, negative test executed; EC-15 five lane branches created off `integration`, `integration` exists off `main`; EC-16 all Phase-0-gated `REG-` decisions closed (`make decisions-gate`).
- scope: entry criteria, B-Day gate, branch protection, contract freeze, lane branches

---

## REQ-master-plan-definition-of-done
- source: master/00-MASTER-PLAN.md
- description: Three DoD levels (§6), each a command set rather than a judgment call — "nothing is done because someone says it is done."
- acceptance:
  - 6.1 **V1 done**: all nine §99.4 items pass their named checks (`make dod-v1`), plus everything §95.3 declares binding even in bootstrap (digest immutability, verification contracts, secret tiers, API-key-free environment, append-only history, the constitution/untrusted-input rule, safe defaults/fail-closed classification, the explicit production-approval event, the registry-change lane's staged apply and authority-delta gate).
  - 6.2 **Foundation tier done** (`make dod-foundation`): every live product fully onboarded or carries an unbreached pre-onboarding deadline; 100% portfolio adoption ratio by the last named deadline; every universal-floor row (72 at 8 products) closed or carries a dated accepted risk; zero Blocking drift; seeded canary found on every reconciliation run (AT-102); eleven-item evidence chain answerable per product; one deliberate rollback and one recorded restore test per product; every bootstrap exception closed or live-unexpired; the Foundation-scope AT set passes; no product list hard-coded anywhere (AT-001).
  - 6.3 **Programme done** (`make dod-programme`): all 110 acceptance tests pass; all 111 invariants carry a checkable enforcement classification (mechanical / policy / review-held), authored at Phase G2; no architecture rewrite was required to pass any test; every Governance/People phase is built-and-passing or recorded `declined`; the quarterly OS review has run end to end and retired at least one policy/metric/automation (or explicitly recorded why not).
- scope: definition of done, V1 gate, Foundation gate, programme gate, acceptance test tiering
