# Roadmap: MultiProduct — Control Plane

## Overview

The build is organized as six phases mapped 1:1 to the six lanes already defined in the ingested master plan: L0 (Integrator, foundation) and the five AI-developer build lanes L1–L5, sequenced in the fixed merge-train dependency order **L1 → L4 → L2 → L3 → L5**. This is a brownfield roadmap: Phase 0 (contracts, partition, governance) is already tagged `contracts/v1.0.0` and complete, and real implementation already exists in every lane-owned tree with lane task branches merging into `integration`. Each phase below should be planned as *close remaining gaps and verify against the lane's Definition of Done*, not as a from-scratch build. The project's V1 finish line is `make dod-v1` passing across all six phases.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: L0 — Integrator Foundation & Contracts** - Contract-first foundation frozen, lane ownership mechanically exclusive, B-Day entry gate fully green
- [ ] **Phase 2: L1 — Registries, Schemas & Contract Skeleton** - Every registry/schema validated, append-only, effective-dated; governance and people V1 slivers in place
- [ ] **Phase 3: L4 — Records, Events & Metrics** - Append-only records/events store live and schema-validated before any consumer reads from it
- [ ] **Phase 4: L2 — Pipeline & Evidence** - Delivery pipeline enforces the digest invariant and produces an answerable evidence chain
- [ ] **Phase 5: L3 — Reconciler & Provisioning** - Declared vs. actual state continuously compared; scaffolding operations provision products/people
- [ ] **Phase 6: L5 — Access, Infra & Ops** - GitHub org enforcement and founder view are live; governance rules are binding even in bootstrap

## Phase Details

### Phase 1: L0 — Integrator Foundation & Contracts
**Goal**: The founder (L0) can prove the contract-first foundation is frozen, lane ownership is mechanically exclusive, and B-Day's entry gate is fully green before any lane's work is trusted. **Brownfield note**: contract freeze and lane-guard enforcement are already shipped (see PROJECT.md Validated); remaining work here is closing the B-Day live-execution gate, not building foundation infrastructure from scratch.
**Depends on**: Nothing (first phase)
**Requirements**: L0-01, L0-02, L0-03, L0-04, L0-05
**Success Criteria** (what must be TRUE):
  1. `make contracts-verify` and `make promote-check` both print their frozen-OK confirmation for the tagged `contracts/v1.0.0` set
  2. A PR touching a path outside its lane's owned trees is mechanically rejected by CODEOWNERS + the lane-guard CI check, and the merge train (L1 → L4 → L2 → L3 → L5) is the only path onto `integration`
  3. The standing `economics.yaml` ledger entry exists with founder-authored content and all required gate answers
  4. The pre-Phase-1 baseline for the §103 minimum measure set is captured and recorded
  5. All sixteen B-Day entry criteria (EC-1..16) read green in one command, including the currently-open items (GitHub org Team-tier purchase, `GITHUB_TOKEN` provisioning, PFD-006, the 8 pilot/product names, the 18 protocol blocking defects)
**Plans**: TBD

### Phase 2: L1 — Registries, Schemas & Contract Skeleton
**Goal**: Every registry and schema in the control plane is machine-validated, append-only, and effective-dated, and the governance/people V1 slivers exist as schema-only foundations for later lanes. **Brownfield note**: `registries/`, `schemas/`, and `validators/registry/` already exist with tests; remaining work is closing the gap to full lane DoD (DoD-1..11) and verifying it.
**Depends on**: Phase 1
**Requirements**: L1-01, L1-02, L1-03, L1-04, L1-05
**Success Criteria** (what must be TRUE):
  1. Every file under `registries/**` validates against its JSON Schema in `schemas/registry/**`, with effective dating and append-only discipline enforced from the first commit
  2. The verification-contract skeleton schema exists and CI enforces its presence on every relevant workflow
  3. The exception registry (mandatory expiry), safe-defaults schema hooks, fail-closed classification, and the control-plane/data-plane invariant test all exist and pass
  4. The people-tier schemas are designed with effective dating and nothing beyond schema shape ships in V1
  5. The weekly bootstrap log's staleness detector runs as a CI rule
**Plans**: TBD

### Phase 3: L4 — Records, Events & Metrics
**Goal**: Every product's operational history is captured in an append-only, schema-validated store before any dashboard or reconciliation run reads from it. **Brownfield note**: `records/`, `events/`, and `metrics/` already exist; the L4 task-body concordance showed a 107/117 gap at last measurement — verify whether that gap is closed before treating this phase as done.
**Depends on**: Phase 2
**Requirements**: L4-01, L4-02, L4-03
**Success Criteria** (what must be TRUE):
  1. `records/**` and `events/**` (in `control-plane-records`) and the records repository itself exist, schema-validated, and are live before any consumer reads from them
  2. The event envelope rejects any event missing an envelope field or carrying an unlisted `event_type`, and every tracked event type carries a stable identifier with a `retired` marker and no delete path
  3. Every store declares its write-freshness interval, with `events/`, `records/deployments/`, and `records/uat/` marked Blocking
  4. The cross-repository reader fails closed when `control-plane-records` is unreachable
**Plans**: TBD

### Phase 4: L2 — Pipeline & Evidence
**Goal**: Every production deployment is delivered through a pipeline that cannot silently skip its own required checks, and every deployment carries a provable, answerable evidence chain. **Brownfield note**: `.github/workflows/`, `templates/workflows/`, and `tools/evidence/` already exist; remaining work is closing the gap to full lane DoD (DoD-01..20) and verifying it.
**Depends on**: Phase 3
**Requirements**: L2-01, L2-02, L2-03
**Success Criteria** (what must be TRUE):
  1. The digest invariant is enforced in code and fails closed, with one tested rollback and one recorded restore test per pilot product
  2. No required-check context can resolve `skipped`/`neutral`, and every privileged workflow's first step is the actor gate; the workflow-identity gate fails closed when approver == deployer
  3. Security/licence scanning is delta-gated, an SBOM is emitted beside every production digest, and the eleven evidence-chain questions are answerable for one real deployment
**Plans**: TBD

### Phase 5: L3 — Reconciler & Provisioning
**Goal**: Declared state and actual GitHub state are continuously compared, drift is classified and (where safe) blocked, and the four scaffolding operations provision new products/people without hand-editing GitHub. **Brownfield note**: `reconciler/` (18+ comparators), `tools/provision/`, and `validators/drift/` already exist with tests; remaining work is closing the gap to full lane DoD and verifying the AT-110 negative test.
**Depends on**: Phase 4
**Requirements**: L3-01, L3-02, L3-03
**Success Criteria** (what must be TRUE):
  1. `create-product`, `add-person`, `change-role`, and `remove-person` scaffolding operations run end-to-end against the declared-vs-actual comparison set
  2. Reconciliation v0 detects and blocks (not yet auto-repairs) drift, classified only as Green/Amber/Red/Blocking
  3. The registry-change lane's staged canary apply and authority-delta gate run on every registry-changing PR
  4. The reconciler credential fails all six AT-110 negative-scope attempts while a normal reconciliation run still completes
**Plans**: TBD

### Phase 6: L5 — Access, Infra & Ops
**Goal**: The organization's access, infrastructure, and operational surfaces enforce the governance rules mechanically, and the founder has a live view into the system's health. **Brownfield note**: `access/`, `infra/`, `ops-vm/`, `notify/`, and `assets/` already exist; the asset-inventory readiness gate currently `FAIL`s (27 errors, finding B-13) — that is the concrete remaining item, not a from-scratch build.
**Depends on**: Phase 5
**Requirements**: L5-01, L5-02, L5-03
**Success Criteria** (what must be TRUE):
  1. GitHub org enforcement — base Read, Teams-derived Write, branch protection with most-recent-push approval, environments, and completion checks executed as written — is live and verifiable
  2. Founder view v0 (GitHub API + reconciliation output + Scorecard) is live and readable by the founder
  3. Safe defaults, fail-closed classification, the constitution/untrusted-input rule, API-key-free environments, digest immutability, append-only history, and the explicit production-approval event are all binding, even in bootstrap
  4. The reconciler credential's AT-110 negative test and the fifth-tier credential rotation/runbook metadata are both verifiably in place
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|-----------------|--------|-----------|
| 1. L0 — Integrator Foundation & Contracts | 0/TBD | Not started | - |
| 2. L1 — Registries, Schemas & Contract Skeleton | 0/TBD | Not started | - |
| 3. L4 — Records, Events & Metrics | 0/TBD | Not started | - |
| 4. L2 — Pipeline & Evidence | 0/TBD | Not started | - |
| 5. L3 — Reconciler & Provisioning | 0/TBD | Not started | - |
| 6. L5 — Access, Infra & Ops | 0/TBD | Not started | - |
