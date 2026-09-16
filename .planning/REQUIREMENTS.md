# Requirements: MultiProduct — Control Plane

**Defined:** 2026-09-16
**Core Value:** Declared state is enforced, drift is visible, orphans are impossible to miss, and every production artifact is traceable.

## v1 Requirements

Requirements for the V1 ("Foundation launch-critical") release. Each maps to exactly one ROADMAP.md phase, which maps 1:1 to a build lane. Source: `intel/requirements.md` (nine V1 declared items, §99.4; six residuals, §98.2 gap) and `intel/constraints.md` (per-lane charter DoD lists), reconciled per the founder-resolved conflicts recorded in PROJECT.md Key Decisions.

### L0 — Integrator Foundation & Contracts

- [ ] **L0-01**: Contract-first foundation is frozen and provable — `contracts/**` frozen by L0 in Phase 0, `make contracts-verify` and `make promote-check` both green, any change to `contracts/**` goes through a Contract Change Request
- [ ] **L0-02**: Lane path ownership is mechanically exclusive — CODEOWNERS + the lane-guard CI check reject any foreign-path PR, and the merge train (L1 → L4 → L2 → L3 → L5) is the only path onto `integration`
- [ ] **L0-03**: The standing `economics.yaml` ledger entry exists with founder-authored content and all required gate answers (residual R-4)
- [ ] **L0-04**: The pre-Phase-1 baseline for the §103 minimum measure set is captured and recorded before Phase 1 begins (residual R-5)
- [ ] **L0-05**: All sixteen B-Day entry criteria (EC-1..16) read green in one command, including GitHub org Team-tier purchase, `GITHUB_TOKEN` provisioning, PFD-006 resolution, the 8 pilot/product names, and the 18 protocol blocking defects

### L1 — Registries, Schemas & Contract Skeleton

- [ ] **L1-01**: Every file under `registries/**` validates against its JSON Schema in `schemas/registry/**`, with effective dating and append-only discipline enforced from the first commit (nine-declared-item 1)
- [ ] **L1-02**: The verification-contract skeleton schema exists, and CI enforces its presence on every workflow that requires it (nine-declared-item 5, schema half)
- [ ] **L1-03**: The exception registry (mandatory expiry), safe-defaults schema hooks, fail-closed classification, and the control-plane/data-plane invariant test all exist and pass (nine-declared-item 8, governance-tier sliver)
- [ ] **L1-04**: People-tier schemas are designed with effective dating and nothing beyond schema shape ships in V1 (nine-declared-item 9, people-tier sliver)
- [ ] **L1-05**: The weekly bootstrap log's staleness detector runs as a CI rule (residual R-6, CI-rule half)

### L2 — Pipeline & Evidence

- [ ] **L2-01**: The digest invariant is enforced in code and fails closed, with one tested rollback and one recorded restore test per pilot product (nine-declared-item 4)
- [ ] **L2-02**: The workflow-identity gate fails closed when approver == deployer, and the actor gate is the first step of every privileged workflow (L2 charter DoD)
- [ ] **L2-03**: Security/licence scanning is delta-gated and an SBOM is emitted beside every production digest, with no required-check context ever resolving `skipped`/`neutral` (L2 charter DoD)

### L3 — Reconciler & Provisioning

- [ ] **L3-01**: The four scaffolding operations (`create-product`, `add-person`, `change-role`, `remove-person`) run end-to-end against the declared-vs-actual comparison set (nine-declared-item 3)
- [ ] **L3-02**: Reconciliation v0 detects and blocks (not yet auto-repairs) drift, classified only as Green/Amber/Red/Blocking (nine-declared-item 6)
- [ ] **L3-03**: The registry-change lane's staged canary apply and authority-delta gate run on every registry-changing PR (residual R-3)

### L4 — Records, Events & Metrics

- [ ] **L4-01**: `records/**` and `events/**` (in `control-plane-records`) and the records repository itself exist, schema-validated, and are live before any dashboard or reconciliation run reads from them (residual R-1)
- [ ] **L4-02**: The event envelope requires all nine envelope fields, rejects any event carrying an unlisted `event_type`, and every tracked event type carries a stable identifier with a `retired` marker and no delete path (L4 charter DoD)
- [ ] **L4-03**: Every store declares its write-freshness interval — with `events/`, `records/deployments/`, and `records/uat/` marked Blocking — and the cross-repository reader fails closed when `control-plane-records` is unreachable (L4 charter DoD)

### L5 — Access, Infra & Ops

- [ ] **L5-01**: GitHub org enforcement — base Read, Teams-derived Write, branch protection with most-recent-push approval, environments, and completion checks executed as written — is live and verifiable (nine-declared-item 2)
- [ ] **L5-02**: Founder view v0 (GitHub API + reconciliation output + Scorecard) is live and readable by the founder (nine-declared-item 7)
- [ ] **L5-03**: Safe defaults, fail-closed classification, the constitution/untrusted-input rule, API-key-free environments, digest immutability, append-only history, and the explicit production-approval event are all binding, even in bootstrap (residual R-2)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Conditional / Deferred Subsystems

- **META-01**: Subsystem G (plan-checker / Gate-1 approval flow) — implemented by GSD, adopt-only, L0-owned, no build-lane owner
- **META-02**: Subsystem J (background machine layer) — implemented by Hermes Agent, deferred until its Phase-3 CPU benchmark passes; L0-owned, no build-lane owner
- **META-03**: Subsystem P's broader scope — the attention classifier and the general people-intelligence engine — remains L0-only/non-delegable per FD-002, deferred from V1 outright per §99.4 item 9
- **META-04**: DevLake installation — closed V1-D3, deferred out of V1

### Foundation-tier and Programme-tier gates (post-V1)

- **GATE-01**: `make dod-foundation` — every live product onboarded, 100% portfolio adoption ratio, zero Blocking drift, one rollback + one restore test per product, all bootstrap exceptions closed or live-unexpired
- **GATE-02**: `make dod-programme` — all 110 acceptance tests pass, all 111 invariants carry a checkable enforcement classification, every Governance/People phase built-and-passing or recorded `declined`, quarterly OS review has run end to end

## Out of Scope

Explicitly excluded per `master/00-MASTER-PLAN.md` §1.1 ("a lane developer who finds itself building one of these has misread a task and must STOP") and the explicitly-deferred list.

| Feature | Reason |
|---------|--------|
| Installer/tenancy/upgrade machinery for third parties | Explicit refusal — §99.6 risk 1 |
| Bespoke web application for Layer B people data | Explicit refusal — §99.5, D75 |
| Separate identity provider | Explicit refusal — §99.5 |
| Metered-LLM or paid-cloud-LLM dependency in engineering tooling | Explicit refusal — invariants 83, 84 |
| Second workflow overlay competing with GSD | Explicit refusal — invariant 43 |
| Automated formal people action | Explicit refusal — invariant 37, AT-071 |
| Per-person raw-activity drill-down on a general dashboard | Explicit refusal — invariant 109, AT-089 |
| Keystroke/screen/webcam/presence surveillance, AI-token-as-performance, single-number productivity score, leaderboards | Explicit refusal — invariants 96-99, AT-075 |
| Hard-coded product list in any dashboard/workflow/script | Explicit refusal — AT-001, invariant 52 |
| Background machine layer (subsystem J / Hermes) before its CPU benchmark passes | Explicit refusal until the gate passes |
| Shared-service registry, split/merge/transfer, dependency-graph views, versioned-contract migration machinery, domains/topology activation, predictive economics/forecasting, Layer B decision support | Explicitly deferred (post-V1) |
| DevLake installation | Closed V1-D3 → deferred out of V1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| L0-01 | Phase 1 | Complete |
| L0-02 | Phase 1 | Complete |
| L0-03 | Phase 1 | Complete |
| L0-04 | Phase 1 | In Progress |
| L0-05 | Phase 1 | Blocked |
| L1-01 | Phase 2 | In Progress |
| L1-02 | Phase 2 | In Progress |
| L1-03 | Phase 2 | In Progress |
| L1-04 | Phase 2 | In Progress |
| L1-05 | Phase 2 | In Progress |
| L4-01 | Phase 3 | In Progress |
| L4-02 | Phase 3 | In Progress |
| L4-03 | Phase 3 | In Progress |
| L2-01 | Phase 4 | In Progress |
| L2-02 | Phase 4 | In Progress |
| L2-03 | Phase 4 | In Progress |
| L3-01 | Phase 5 | In Progress |
| L3-02 | Phase 5 | In Progress |
| L3-03 | Phase 5 | In Progress |
| L5-01 | Phase 6 | In Progress |
| L5-02 | Phase 6 | In Progress |
| L5-03 | Phase 6 | In Progress |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-16*
*Last updated: 2026-09-16 after initial ingest-driven project initialization*
