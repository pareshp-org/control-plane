# Constraints (SPEC intel)

Synthesized from classified SPEC documents: `PARTITION.md`, `docs/reference/MultiProduct_MasterSpec_v4.0.md`, `master/04-phase-map.md`, and the five lane charters (`lanes/L1-00-charter.md` through `lanes/L5-00-charter.md`).

---

## FROZEN PARTITION CONTRACT — v1
- source: PARTITION.md
- type: protocol
- content: Declares itself "Authoritative. Every implementation document must conform. Do not redesign." (manifest `precedence: 1` — the highest-precedence non-MasterSpec document in this ingest set.) Defines the four repositories (`control-plane`, `control-plane-records`, `product-template`, eight live `<product>` repos) and their protection posture; the five build lanes plus L0 with strict, exclusive path ownership enforced by CODEOWNERS + the lane-guard CI check; five non-negotiable anti-conflict rules — (1) one owner per path, no exceptions; (2) contract-first, `contracts/**` frozen by L0 in Phase 0, lanes file a Contract Change Request rather than edit it; (3) no shared mutable file ever, directory-per-item only; (4) no cross-lane imports, a lane consumes another lane's output only through `contracts/**` or a published artifact; (5) additive-only within a lane. Branch & merge model: `main` (protected, releasable) ← `integration` (daily merge target) ← `lane/N/<phase>-<task>` branches; merge train fixed order **L1 → L4 → L2 → L3 → L5**, once per cycle. AI-developer profile: Sonnet-4.6-class, low cost, no repo context, no judgment authority — every task must carry exact file paths, literal copy-pasteable commands, complete acceptance criteria, a self-verify command with unambiguous output, and a STOP rule.

---

## Multi-Product Engineering and Delivery Operating System — Master Specification v4.0
- source: docs/reference/MultiProduct_MasterSpec_v4.0.md
- type: schema
- content: The base specification (10,256 lines; manifest `precedence: 0`, the single highest-authority document in the ingest set) for the full multi-product engineering/delivery operating system. Every other document in this ingest cites it as the ultimate authority. Structure referenced throughout the dependent documents: subsystem catalogue A–R (§99.2, with the dependency spine A→B→C/D, E→F→H/I); the three build tiers Foundation/Governance/People and their phases 1–7 / G1–G8 / P1–P8 (§98); acceptance tests AT-001..AT-110 (§100); invariants 1–111 (§101); health signals `SIG-nn` (§52.2 arming discipline, D77); decision ids D1–D112 (Appendix A); the 29-artifact registry inventory (§52.6); the five secret tiers (§40.1); record/event schemas and the event envelope (§97); reconciliation levels and drift classes (§53); the minimum measure set and baseline capture (§103); the V1 minimal-honest-build definition (§99.4) and its explicit deferrals; bootstrap binding rules (§95).
- note: given the file's size, this synthesis pass extracted its content indirectly, via the citations quoted verbatim by `PARTITION.md`, `master/01-lane-architecture.md`, `master/06-v1-scope.md`, `master/00-MASTER-PLAN.md`, `master/04-phase-map.md`, and the five lane charters, rather than a full independent line-by-line read. Flag for the roadmapper if a direct extraction pass over specific untouched sections is later required.

---

## 04 — THE PHASE MAP
- source: master/04-phase-map.md
- type: protocol
- content: Splits the build into a **Build track** (`BT-0`…`BT-4`, dated by subsystem complexity band per D99) and an **Onboarding track** (`OT-FLOOR`, `OT-INTAKE`, `OT-P4`…`OT-P7`, dated relative to Build-track milestones, never to §98.2's week labels). Critical path: `BT-0 → A(L1) → B(L1) → D(L3) → C(L3)` = 8–22 build-elapsed weeks; L5's own chain runs 4–18 weeks in parallel from `BT-0` and is the only serious contender. Five hard synchronisation points `S0`…`S4`, each with an executable "clean" definition that L0 runs before declaring the point passed; merge train fixed order **L1 → L4 → L2 → L3 → L5**. Distinguishes genuinely concurrent work from apparent-but-not-real parallelism (e.g., L3 can write code against frozen contracts before L1 lands, but cannot verify anything until S1). Five L0 DECISIONS REQUIRED (`DECISION 1`–`5`) — all recorded as Resolved, via FD-002 (subsystem ownership), REG-008 (unowned-path assignment), and Q1/Q5/Q6 (calendar anchors, universal-floor sequencing, pilot selection).

---

## L1-00 — LANE 1 CHARTER: Registries and Contracts
- source: lanes/L1-00-charter.md
- type: nfr
- content: Owns `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` in `control-plane`. Subsystems A, B. Merge-train position 1st. Definition of Done `DoD-1`..`DoD-11`: every schema file is itself a valid JSON Schema; every owned registry file validates against its schema; every §15.5 validator rule has a file plus an invalid fixture it rejects; every charter invariant/AT has a named check or fixture; no `*.v1.schema.json` ever deleted or overwritten; no L1 commit touches a foreign path; the §98.2 Phase 1 and Phase 3 completion checks are satisfied for L1's part; no banned measurement field exists anywhere in `schemas/**` (AT-075); every §12 DECISION REQUIRED item is resolved in `contracts/**` or carries an open blocker.

---

## L2-00 — LANE 2 CHARTER: PIPELINE AND EVIDENCE
- source: lanes/L2-00-charter.md
- type: nfr
- content: Owns `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` in `control-plane`. Subsystems E, F. Merge-train position 3rd. Definition of Done `DoD-01`..`DoD-20`: all eight reusable workflows exist; all required per-product workflow templates exist; the digest invariant is enforced in code and fails closed; the workflow-identity gate fails closed when approver == deployer; the actor gate is the first step of every privileged workflow; every required-check context is emitted unconditionally (no `if:`, no path filter); a `skipped`/`neutral` conclusion is impossible on a required context; security/licence scanning is delta-gated; SBOM emitted beside every production digest; the Friday-freeze gate resolves against the declared operating timezone; `renovate-path-guard` fails on out-of-manifest and foreign-authored diffs; the verification-contract seeded-defect case must fail on every run; `verify-digest-chain` catches every digest/approval mismatch; the eleven evidence-chain questions are answerable for one real deployment; deployment-record and event writes are required, failing steps; AT-103/AT-024/AT-035/AT-029 executed; zero L2 PRs ever touch a foreign path.

---

## L3-00 — CHARTER: Reconciler & Provisioning
- source: lanes/L3-00-charter.md
- type: nfr
- content: Owns `reconciler/**`, `tools/provision/**`, `validators/drift/**` in `control-plane`. Subsystems C, D. Merge-train position 4th. Fixes the drift-class vocabulary (**Green, Amber, Red, Blocking** — no other severity vocabulary anywhere, per contract C9) and the five reconciliation levels (Detect/Warn/Auto-repair/Block/Escalate). Enumerates the four scaffolding operations (`create-product`, `add-person`, `change-role`, `remove-person`) and the declared-vs-actual comparison set. Records the reconciler credential's tier, scope, and behavioural envelope, and the AT-110 negative test: the reconciler credential must fail all six of a write attempt on a GitHub Actions secret, an environment, a workflow file, org settings, `records/**`, and Layer B — while a normal reconciliation run still completes. Five open decisions handed to L0 (`DR-L3-01`..`05`): the blocking check-run name and registration; which repair class is enabled first and its order; the seeded canary's content and location; the `gap-window` mark's carrier; the independent verifier's write surface.

---

## L4 — RECORDS, EVENTS AND METRICS — LANE CHARTER
- source: lanes/L4-00-charter.md
- type: nfr
- content: Owns ALL of `control-plane-records` (`records/**`, `events/**`, root files, `.github/**`), plus `schemas/records/**`, `metrics/**`, `tools/records/**` in `control-plane`. Subsystems I, N. Merge-train position 2nd (immediately after L1). Definition of Done `DoD-1`..`DoD-20`: every §97.2 store plus `events/` exists with a JSON Schema requiring `record_schema_version`, `id`, `product`, `timestamp`; the event envelope rejects any event missing one of the nine envelope fields or carrying an unlisted `event_type`; the taxonomy carries a stable identifier per tracked event with a `retired` marker and no delete path; every store declares its expected write-freshness interval, with `events/`, `records/deployments/` and `records/uat/` marked Blocking; the attention-ledger derivation implements the eight categories, the 30-minute idle gap, the 0.25h granularity, fixed precedence order, and the instrument-defect rule; self-reported figures carry a permanent `self-reported` provenance label; `RECORD-VERIFICATION-RESULT` accepts only structured inputs with no hand-edit path; the deletion-request schema carries all four required timestamps (AT-105); every §103 measure names the store it derives from, or is absent; an unbaselined store renders `unbaselined`, never a silent miss; the cross-repository reader fails closed when the records repo is unreachable; every timestamp is UTC with offset; retention classes are declared per store.

---

## L5 — ACCESS, INFRA AND OPS — LANE CHARTER
- source: lanes/L5-00-charter.md
- type: nfr
- content: Owns `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` in `control-plane`. Subsystems K, L, M, Q, R. Merge-train position last (5th) — deliberately, because L5 arms the enforcement boundary over work that already exists elsewhere. Definition of Done `DoD-01`..`DoD-16`: all five owned trees plus the fixed internal layout exist; the branch touches no foreign path; the contract gate passes; every §4 spec row has an implementing file citing its spec anchor; no hand-authored aggregate file exists in any owned tree; publication is byte-reproducible from sources; every published artifact validates against its `contracts/**` schema; every control in `access/fail-closed/` is classified exactly `fail-closed` or `fail-open`; every asset entry carries an expiry date, named owner and alert threshold ≥ 30 days; every notify route names a taxonomy id present in L4's published taxonomy and is a subset of the §92.11 closed push list; every approved runtime/extension/MCP server is pinned by full commit SHA or content checksum, never a tag/branch/`latest`; every fifth-tier credential entry carries rotation cadence, named rotator, runbook link, behavioural envelope, and published permission set; no file in any owned tree grants a machine identity any people-related data category; `people-intelligence` appears nowhere as delegable (D109); every VM job declares it is not in any product runtime path.
