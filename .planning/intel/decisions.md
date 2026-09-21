# Decisions (ADR intel)

Synthesized from classified ADR documents in `.planning/intel/classifications/`. One entry per classified document. Where a document is itself a registry of many individual decisions, the registry's own key entries are surfaced inside its decision statement rather than exploded into separate top-level entries, since the classifier treated the whole document as one ADR unit.

---

## ADR: 01 — Lane Architecture
- source: master/01-lane-architecture.md
- status: locked (declared "normative for the build"; classification `locked: true`, manifest `precedence: 5`)
- decision: Defines the five build lanes (L1–L5) plus the L0 integrator, their subsystems (A–R, Section 99.2), exclusive path ownership (§2 manifest), the CODEOWNERS layout (§3), the lane-guard check (§4), the eighteen contract surfaces C1–C18 L0 must freeze before any lane starts (§5), full per-lane specifications (§6.1–6.6), cross-lane interaction rules restated as executable commands (§7), the boundary-reason register B1–B18 (§8), and the merge-train order **L1 → L4 → L2 → L3 → L5**. The document explicitly subordinates itself to `PARTITION.md`: *"Precedence rule, binding. Where this file and `PARTITION.md` appear to disagree, `PARTITION.md` wins and this file is wrong."*
- scope: lane architecture, path ownership, subsystems A-R, build lanes L1-L5, merge train, CODEOWNERS, contract surfaces, inter-lane dependencies
- open items (all later resolved by FD-002 per `_FOUNDER_DECISIONS.md`): LA-01 (five subsystems G,H,J,O,P have no lane), LA-02 (lane-guard/Renovate-guard/independent-verifier ownership — `.github/workflows/**` is L2's, but the guard constrains L2), LA-03 (twelve unowned surfaces of §2.1), LA-04 (`os-health.yaml` sits in an L1 path but is a metrics artifact), LA-05 (closed `event_type` enum lives in `platform.yaml`, L1's file, but is authored by L4)
- note: see `INGEST-CONFLICTS.md` INFO-1 — this ADR is outranked by the SPEC `PARTITION.md` (manifest precedence 1 < 5) per its own stated subordination; not a real conflict, but the precedence direction is non-default (ADR outranked by SPEC) and is recorded for transparency.

---

## ADR: Decision Registry (open-decisions.yaml)
- source: decisions/open-decisions.yaml
- status: proposed (registry; individual rows carry their own `RESOLVED`/`OPEN` status)
- decision: Multi-lane decision registry tracking decisions with ids `D-*`, `REG-*` and `PFD-*`. Resolved entries include: `D-L4-01` (event-type enum — remap L4 metrics to existing L1 event types, no new registry entries, resolved by FD-065); `D-L4-02` (metric-register publication — L4-scoped, L1 carries stable references only, resolved by FD-066); `D-L2-07`/`D-L2-08`/`D-L2-09` (REG-020/REG-033 compliance and their intersection, resolved by FD-053/FD-054); dispatch-gate `Q1`–`Q11` (resolved by FD-071..081); the L2/L3 branch-model and namespace PFDs (`PFD-010`..`PFD-015`, resolved by FD-084..089); the L4 scheduling PFDs (`PFD-016`..`PFD-019`, resolved by FD-090..093); and PFD-001 through PFD-032 generally (resolved by FD-082, FD-083, FD-094..112). One entry remains **OPEN**: `PFD-006` — L5 break-glass second owner, deferred by the Founder, no FD yet.
- scope: architectural decisions, event-type enum, metric registry, compliance (REG-020, REG-033), layer ownership, dispatch gates (Q1-Q11), L2 integration, L3 bootstrap, L4 scheduling, L5 executor, branch protection, Git conventions, bootstrap exception, registry location
- CONFLICT: this file's `REG-001` (titled "canonical event-type ownership", resolved_by FD-002) and `REG-002` (titled "cross-layer metric reference protocol", resolved_by FD-003) do not match the subjects `_FOUNDER_DECISIONS.md` assigns to the same ids (`FD-002 = REG-001 · Subsystems G, H, J, O and P`; `FD-003 = REG-002 · The lane-guard circularity`). See `INGEST-CONFLICTS.md` WARNING-1.

---

## ADR: L0-04 — The Decision Register
- source: lanes/L0-04-decisions-register.md
- status: proposed (procedural meta-ADR; document itself records prompts and option sets — it does not close decisions. No explicit "Status: Accepted" field.)
- decision: Establishes L0's single canonical decision register with a stable `REG-` id space, replacing more than twenty incompatible open-decision id schemes found across 57 plan documents (`D-PLAN-nn`, `LA-nn`, `D-REQ-n`, `DECISION n`, `D-EE-n`, `V1-Dn`, `DEC-nn`, `L1-Dnn`, `DR-L1-06-x`, `D-L2-nn`, `D-L3-nn`, `DR-L3-05-x`, `D-L4-Pn-nn`, `L0-IG-Dn`, etc.). States that `REG-001` (the subsystem G/H/J/O/P partition gap) and `REG-002` (the lane-guard circularity) outrank every other entry and are both `P0`. §5 is a concordance mapping every source id in every plan file to its `REG-` id. Binding rule for lane executors: cite the `REG-` id in any blocker, never only the lane-local source id.
- scope: decision register, REG id space, decision states, priority bands, L0 authority, decision resolution

---

## ADR: Founder Decisions Summary (index)
- source: docs/decisions-summary.md
- status: proposed (index/summary document; confidence: low — lacks Context/Decision/Consequences structure and no explicit Accepted status field)
- decision: Indexes 112 founder decisions (FD-001..112) across 16 sessions; all marked DECIDED. Key clusters cited: Identity & Org (FD-067 `L0_LOGIN=bendrohit-eng`, FD-069 `ORG=pareshp-org` Free plan, FD-050 schema URN prefix); Architecture (FD-082 task-ID format `L<N>-<FF>-<NN>`, FD-094 validator CLI Option B, FD-096 flat schema layout, FD-100 registry dir-per-item); Operations (FD-086 actor gate = bendrohit-eng only, FD-102 branch protection = PRs required, FD-106 canary sentinel, FD-109 bootstrap exception single-owner). One open item: `PFD-006` (break-glass second owner, deferred — decide before Phase 1 go-live); 8 product names still to replace `Product-1..8` in `facts.tsv`.
- scope: founder decisions, architecture, operations, identity, organization, phases, sessions

---

## ADR: Pending Founder Decisions
- source: PENDING_FOUNDER_DECISIONS.md
- status: proposed (decision queue; confidence: medium per classifier — structured as a list of pending decision points, not a single Context/Decision/Consequences record; most rows already carry a `RESOLVED` banner with a citing FD id)
- decision: Catalogues `PFD-001`..`PFD-032`, sourced from `lanes/L1-99-review.md`, `lanes/L2-99-review.md`, `lanes/L3-99-review.md`, and a Session-13 `_DECISION_DOCKET.md` audit. 31 of 32 are RESOLVED (FD-082, FD-083, FD-084..112). The sole remaining OPEN item is `PFD-006` — L5 AT-022 break-glass second owner (who holds escrow credentials if `bendrohit-eng` is unavailable), deferred with no FD.
- scope: L1 validator engine design, L1 dispatch surface, L1 schema file layout, L2 canonical plan, L3 canonical plan, L4 FTE application, L4 ready-queue-miss emit timing, L4 working calendar selection, L4 capacity profile ownership, task-ID grammar, lane reviewer assignment, branch-protection mechanism, record write interface, reconciler identity, seeded canary, security and SBOM scanning, orphan detection surfaces, bootstrap exception path, build start date, board layout configuration

---

## ADR: FOUNDER DECISIONS — the closed register
- source: _FOUNDER_DECISIONS.md
- status: proposed (classification `locked: false`; the document nonetheless declares itself self-authoritative: *"This file is additive and authoritative: where a plan document disagrees with a row here, the row here wins and the document is to be corrected in the next reconciliation sweep."*)
- decision: Register of 112 founder decisions (FD-001..FD-112, plus superseded/re-decided entries such as FD-007-R). Notable entries: **FD-001** — the Founder personally is L0 (not the Team Lead). **FD-002** (`REG-001`) — subsystems G, H, J, O, P assignment: **H → L5** (Grafana/ops-VM), **O-registries → L1**, **O-jobs → L3**, **J → deferred** (CPU-benchmark gated), **G → L0 (Founder, forced, not delegable)**, **P → L0 (Founder, forced, not delegable — §99.3 item 1 attention classifier is design-open and §99.4 item 9 defers P from V1 outright)**. **FD-003** (`REG-002`) — the lane-guard circularity, re-decided as Options A+E after the original Option D proved non-executable under the frozen partition. **FD-016** — two pilot products. **FD-017** — two context-holding humans hold Write at V1 (the Founder and Nimesh, Team Lead). **FD-082** — task-ID grammar `L<N>-<FF>-<NN>`, no T infix. **FD-094/095/096** — L1 validator CLI Option B, L1-05-tasks.md sole dispatch, flat schema layout. **FD-100..112** — registry dir-per-item, git conventions, rulesets-only branch protection, all 16 unowned paths assigned, REST+App-token record writes, GitHub App reconciler identity, `people.yaml/_canary/__CANARY__` seeded canary, Trivy+Syft security tooling, 5 orphan-surface defaults, bootstrap exception path, build-start date 2026-09-08, board/scorecard thresholds, DevLake deferred from V1.
- scope: founder decisions, lane assignments, L0 integrator, contract freeze, implementation toolchain, GitHub organization, JSON Schema, CODEOWNERS, dispatch gate, design-open items, auto-repair, pilots, bootstrap configuration
- CONFLICT: **FD-093** (2026-09-08, resolving `PFD-019`) states *"Option A — L4 owns subsystem P... `PARTITION.md` updated: subsystem P assigned to L4"* — directly contradicting this same document's earlier **FD-002** (2026-09-02), which force-assigns subsystem P to **L0 (the Founder)**, "not delegable to any lane under any option." FD-093 never states it supersedes or amends FD-002. See `INGEST-CONFLICTS.md` WARNING-2.
