## Conflict Detection Report

### BLOCKERS (0)

None found.

- LOCKED-vs-LOCKED ADR contradiction check: only one classified document carries `locked: true` (`master/01-lane-architecture.md`); no other locked ADR exists to contradict it.
- Merge mode: N/A — this ingest ran in `new` mode (no existing `.planning/` context to check against).
- UNKNOWN/low-confidence classification check: no document in this ingest set was classified `UNKNOWN`. One document (`docs/decisions-summary.md`) carries `confidence: low` but was cleanly classified `ADR` by the manifest override — it is carried into `decisions.md` with its low-confidence caveat rather than blocked.
- Cross-ref cycle-detection check: a directed graph was built from every classification's `cross_refs`, matched against the 27 classified `source_path` basenames. No cycle was found (max observed chain depth well under the 50-hop cap). Docs with no resolvable in-set cross-refs (e.g. `PARTITION.md`, `decisions/open-decisions.yaml`, `docs/bootstrap-runbook.md`, `infra/READINESS.md`, `docs/phase-0-complete.md`, `docs/architecture.md`) were treated as graph leaves/roots and synthesized normally.

### WARNINGS (2)

[WARNING] REG-001 / REG-002 subject mismatch between decision registries
  Found: `decisions/open-decisions.yaml` labels `REG-001` "canonical event-type ownership" (resolved_by FD-002) and `REG-002` "cross-layer metric reference protocol" (resolved_by FD-003).
  Impact: `_FOUNDER_DECISIONS.md` — the register both `open-decisions.yaml` and `lanes/L0-04-decisions-register.md` point to as the closure source — defines `FD-002` as *"REG-001 · Subsystems G, H, J, O and P"* and `FD-003` as *"REG-002 · The lane-guard circularity."* Both are ADR-type sources carrying the same manifest precedence (2), so precedence cannot pick a winner; a downstream consumer that resolves `REG-001` or `REG-002` from `open-decisions.yaml` will land on a different subject than one that resolves them from `_FOUNDER_DECISIONS.md`.
  → Reconcile the `REG-001`/`REG-002` definitions between `decisions/open-decisions.yaml` and `_FOUNDER_DECISIONS.md` (or retire `open-decisions.yaml`'s conflicting `REG-` labels in favour of the founder-decisions register) before routing any downstream work that cites these ids.

[WARNING] FD-093 contradicts FD-002 on subsystem P ownership
  Found: `_FOUNDER_DECISIONS.md` FD-093 (2026-09-08, resolving `PFD-019`) — *"Option A — L4 owns subsystem P. Capacity planning is a metric aggregate... `PARTITION.md` updated: subsystem P assigned to L4."*
  Impact: The same document's FD-002 (2026-09-02) already force-assigned subsystem P to *"L0 (the Founder)... Forced. §99.3 item 1 (the attention classifier) is design-open. §99.4 item 9 defers P from V1 outright,"* stating explicitly it is "not delegable to any lane under any option." FD-093 never states it supersedes or amends FD-002, and `PENDING_FOUNDER_DECISIONS.md`'s `PFD-019` entry frames the question as though subsystem-P ownership were still fully open, with no reference to FD-002's prior forced ruling. Downstream lane-ownership artifacts (`PARTITION.md`, `lane-paths.tsv`, `CODEOWNERS`) cannot honour both answers simultaneously — one says L0-only/non-delegable, the other says L4.
  → Ask the founder to explicitly reconcile FD-002 and FD-093: does FD-093 narrowly amend FD-002 for the Capacity-Profile output slice only (leaving the rest of subsystem P — the attention classifier, the broader people-intelligence engine — with L0), or does it supersede FD-002 entirely for subsystem P? Record the reconciliation as a new dated decision before assigning subsystem P / Capacity Profile ownership in the roadmap.

### INFO (3)

[INFO] Auto-resolved: SPEC (`PARTITION.md`) > ADR (`master/01-lane-architecture.md`) on lane-architecture precedence
  Note: `master/01-lane-architecture.md` is classified ADR and `locked: true`, but carries manifest `precedence: 5` — lower-ranked than `PARTITION.md`'s SPEC `precedence: 1`. This non-default direction (a SPEC outranking a locked ADR) is intentional: the ADR explicitly states its own subordination — *"Precedence rule, binding. Where this file and `PARTITION.md` appear to disagree, `PARTITION.md` wins and this file is wrong."* No actual content contradiction was found between the two during synthesis; wherever they overlap (path-ownership table, merge-train order, anti-conflict rules), the content agrees. Recorded for transparency because it reverses the ADR > SPEC default.

[INFO] Auto-resolved: ADR register (`_FOUNDER_DECISIONS.md`, FD-106) > DOC (`docs/architecture.md`) on seeded-canary location
  Found: `docs/architecture.md` states *"FD-106 | Registry canary: registries/people/_canary.yaml."*
  Note: `decisions/open-decisions.yaml`, `PENDING_FOUNDER_DECISIONS.md`, and `_FOUNDER_DECISIONS.md` (heading: *"FD-106 — Seeded Canary: people.yaml _canary Field"*) all agree the seeded canary lives at `people.yaml/_canary/__CANARY__`, not a separate `registries/people/_canary.yaml` file. ADR sources (manifest precedence 2–3) outrank the DOC source (precedence 6) under the default ADR > DOC ordering; the ADR value is carried as authoritative in `decisions.md`, and `docs/architecture.md`'s value is treated as a stale simplification in `context.md`.

[INFO] Auto-resolved: SPEC (`PARTITION.md` / `master/01-lane-architecture.md`) > DOC (`docs/architecture.md`) on lane subsystem labels
  Found: `docs/architecture.md`'s informal diagram labels Lane 3 "Record Store" and Lane 4 "Metrics."
  Note: `PARTITION.md` and `master/01-lane-architecture.md` (both higher-precedence SPEC/ADR sources) assign **L3 = Reconciler & Provisioning** (subsystems C, D) and **L4 = Records, Events & Metrics** (subsystems I, N — owning ALL of `control-plane-records`). `docs/architecture.md`'s labels are an informal simplification; the SPEC-tier assignments are carried as authoritative into `constraints.md`.
