# MultiProduct — Control Plane

## What This Is

A multi-product engineering and delivery operating system for a founder-run portfolio of products: a `control-plane` repository (plus a paired `control-plane-records` repo) that owns schema-validated registries, GitHub access enforcement, CI/CD pipelines with a provable evidence chain, drift reconciliation between declared and actual state, and append-only records/events/metrics — built by five AI-developer build lanes (L1–L5) under a human Integrator (L0, the Founder personally). This is a **brownfield** continuation: Phase 0 (contracts, partition, governance) is tagged `contracts/v1.0.0` and complete, and multiple lane branches are already merged into `integration`.

## Core Value

Declared state is enforced, drift is visible, orphans are impossible to miss, and every production artifact is traceable — if any one of those four fails, nothing else in this system matters.

**Developer-facing success metric:** V1 is done when `make dod-v1` passes — all nine spec §99.4 items pass their named checks, plus everything §95.3 declares binding even in bootstrap (digest immutability, verification contracts, secret tiers, API-key-free environments, append-only history, the constitution/untrusted-input rule, safe defaults/fail-closed classification, the explicit production-approval event, the registry-change lane's staged apply and authority-delta gate). *(source: `master/00-MASTER-PLAN.md` §6.1, `intel/requirements.md` REQ-master-plan-definition-of-done — this is the given metric, not a substitute.)*

## Requirements

### Validated

<!-- Shipped and confirmed, per the ingested docs. -->

- ✓ Contract-first foundation frozen — `contracts/**` frozen at tag `contracts/v1.0.0` (hash `07232bd3...`), 24 contracts each with a 7-key header/register row/stub/fixtures; `make contracts-verify` and `make promote-check` both prove it — Phase 0
- ✓ Lane path ownership mechanically exclusive — CODEOWNERS + the lane-guard CI check reject foreign-path PRs; merge-train order **L1 → L4 → L2 → L3 → L5** rehearsed on empty lane branches — Phase 0
- ✓ Decision governance closed for bootstrap — all 112 Founder Decisions recorded (FD-001..112), 31/32 PFDs resolved (only PFD-006 open), all 6 lane coherence reviews PASS, `verify_handover.sh` reports HANDOVER INTACT — Phase 0
- ✓ Real implementation exists across all five lane-owned trees (`access/`, `reconciler/`, `validators/`, `tools/provision/`, `tools/evidence/`, `tools/records/`, `metrics/`, `registries/`, `schemas/`, `records/`, `events/`) with accompanying unit/integration tests — confirmed via repository structure mapping
- ✓ Multiple lane task branches merged into `integration` through the adversarially-verified merge-train process (`lane/1/*`, `lane/2/*`, `lane/3/*`, `lane/4/*`, `lane/5/*`) — confirmed via `git log`

### Active

<!-- Current scope. Building toward make dod-v1. -->

- [ ] All nine §99.4 V1 declared items pass their named checks, across all five lanes
- [ ] The six binding day-one residuals (R-1..R-6) fully closed
- [ ] B-Day entry criteria EC-1..16 all green — explicitly open today: GitHub org Team-tier purchase, `GITHUB_TOKEN` provisioning for live execution, 8 pilot/product names for `facts.tsv`, PFD-006 (L5 break-glass second owner), 18 protocol blocking defects (`protocol/_98-DEEP-REVIEW.md` §4)
- [ ] L5 asset-inventory readiness gate passes — currently `FAIL (27 errors)`, three inventory entries written under the wrong field set (finding B-13)
- [ ] L4 task-body concordance gap closed — 107/117 bodies present at last measurement against the `L4-06-tasks.md` index
- [ ] Known tech debt from codebase concerns resolved or explicitly deferred: empty policy registry (blocked on Phase G2), orphan-dismissal audit trail not persisted, repair operations lack live-GitHub end-to-end tests

### Out of Scope

<!-- Explicit boundaries. Full list and reasons in REQUIREMENTS.md. -->

- Installer/tenancy/upgrade machinery for third parties, a bespoke web app for Layer B people data, a separate identity provider, and any metered/paid-cloud-LLM dependency in engineering tooling — explicit refusals (§99.6 risk 1, §99.5/D75, invariants 83/84)
- Surveillance-flavored people metrics (keystroke/screen/webcam/presence tracking, AI-token-as-performance, single-number productivity scores, leaderboards) and per-person raw-activity drill-down on general dashboards — explicit refusals (invariants 96-99/109, AT-075/AT-089)
- DevLake installation — closed V1-D3, deferred out of V1
- Subsystem P's broader scope (the attention classifier, the general people-intelligence engine) — remains L0-only/non-delegable per FD-002, deferred from V1 outright per §99.4 item 9
- Subsystem J (background machine layer / Hermes Agent) — deferred until its Phase-3 CPU benchmark passes

## Context

**Six-lane build model.** The build is organized as five AI-developer build lanes (L1 Registries & Contracts, L2 Pipeline & Evidence, L3 Reconciler & Provisioning, L4 Records/Events/Metrics, L5 Access/Infra/Ops) plus L0, the human Integrator — the Founder personally, not the Team Lead (FD-001). Lane executors are treated as a Sonnet-4.6-class AI-developer profile: low cost, no repo context, no judgment authority — every task must carry exact file paths, literal copy-pasteable commands, complete acceptance criteria, a self-verify command, and a STOP rule (`PARTITION.md`). This ROADMAP's phase structure maps 1:1 to those six lanes, in the fixed merge-train dependency order **L1 → L4 → L2 → L3 → L5**, with L0 as the foundation phase.

**Why subsystems G and J don't map to a lane.** Subsystem G (plan-checker / Gate-1 approval flow) is implemented by GSD (`open-gsd/gsd-core`) — this planning setup itself — on an adopt-only basis, reserved to L0 directly. Subsystem J (the background machine layer) is implemented by Hermes Agent, also reserved to L0 directly, and is gated on an unrun Phase-3 CPU benchmark decision. Neither has a build-lane owner; L5's own charter explicitly disclaims any part of subsystems G, H, J, O, or P (`infra/READINESS.md`). Both are tracked as founder-owned, cross-cutting concerns rather than roadmap phases.

**Brownfield status.** This is not a from-scratch initialization. Real code exists in every lane-owned tree (see Validated above), and lane task branches are already merging into `integration`. Each roadmap phase below should be planned as *close remaining gaps and verify against the lane's DoD*, not as a from-scratch build — see each phase's Goal note.

**Ingest conflict handling.** Two warnings surfaced during ingest synthesis (see `.planning/INGEST-CONFLICTS.md`) were resolved by the founder and are recorded in Key Decisions below rather than left open: the REG-001/REG-002 subject mismatch, and the FD-093/FD-002 subsystem-P ownership conflict.

## Constraints

- **Runtime**: Python 3.12 — per decision D-EE-1 in `master/05-entry-exit-criteria.md`. This specific file was excluded from the ingest manifest as procedural reference, so this is recorded here as a founder-supplied fact rather than an ingest-derived one.
- **Contract-first**: `contracts/**` is frozen by L0 in Phase 0; a lane needing a change files a Contract Change Request (`docs/contract-change-request.md`) and stops — it never edits the contract directly (`PARTITION.md` rule 2).
- **Path ownership**: one owner per path with no exceptions, no shared mutable file (directory-per-item only), no cross-lane imports (a lane consumes another lane's output only through `contracts/**` or a published artifact), additive-only within a lane (`PARTITION.md` rules 1, 3, 4, 5).
- **Branch/merge model**: `main` (protected, releasable) ← `integration` (daily merge target) ← `lane/N/<phase>-<task>` branches; merge train fixed order **L1 → L4 → L2 → L3 → L5**, once per cycle.
- **No API keys anywhere on any machine** (EC-6); no metered-LLM or paid-cloud-LLM dependency in engineering tooling (invariants 83, 84).
- **Drift-class vocabulary is fixed**: Green, Amber, Red, Blocking — no other severity vocabulary anywhere (L3 charter, contract C9).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| REG-001/REG-002 subject definitions | `_FOUNDER_DECISIONS.md` wins over `decisions/open-decisions.yaml` on conflicting ADR content. REG-001 = "Subsystems G, H, J, O and P" (resolved by FD-002); REG-002 = "the lane-guard circularity" (resolved by FD-003) | ✓ Good — founder-resolved; `open-decisions.yaml`'s conflicting REG- labels are stale/superseded |
| Subsystem P ownership (FD-093 vs FD-002) | FD-093 is a narrow amendment, not a full supersession: the Capacity-Profile output slice moves to L4 (reclassified as a metrics/subsystem-N aggregate); the attention classifier and the broader people-intelligence engine remain L0-only and non-delegable per FD-002's original forced ruling | ✓ Good — founder-resolved, recorded here so it doesn't need re-litigating |
| Lane architecture vs `PARTITION.md` precedence | `master/01-lane-architecture.md` explicitly subordinates itself to `PARTITION.md`; no actual content conflict found where they overlap | ✓ Good |
| Merge-train order | Fixed **L1 → L4 → L2 → L3 → L5**, once per cycle; L5 goes last deliberately because it arms the enforcement boundary over work that already exists elsewhere | ✓ Good — drives this ROADMAP's phase dependency order |
| Subsystem G (plan-checker / Gate-1) → GSD | Adopt-only, L0-owned, no build-lane owner (V1-D1 recommendation, founder-confirmed for this planning setup) | — Pending B-Day GSD capability-verification run (EC-9) |
| Subsystem J (background machine layer) → Hermes Agent | Deferred, gated on an unrun Phase-3 CPU benchmark decision; L0-owned, no build-lane owner | — Pending (benchmark not yet run) |
| Two pilot products (FD-016) | Ordered by `reliability_criticality`, then `business.criticality`, then cheapest onboarding | ✓ Good |
| Founder-view v0 ownership (V1-D2) | Closed → L5 (`ops-vm/**`) | ✓ Good |
| DevLake in V1 (V1-D3) | Closed → deferred out of V1 | ✓ Good |
| Asset inventory V1 sliver (V1-D5) | Closed → minimal sliver, machine-credential rows only | ✓ Good |
| Control-plane Write headcount (V1-D6) | Closed → TWO (Founder/L0 per FD-001, and Nimesh, Team Lead) | ✓ Good |

---
*Last updated: 2026-09-16 after initial ingest-driven project initialization*
