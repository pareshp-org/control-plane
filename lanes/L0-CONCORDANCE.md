# L0-CONCORDANCE — Lane 0 task-id concordance

**Lane:** L0 — Integrator / Founder seat (the orchestration layer).
**Decision basis:** FD-004 (publish a concordance; do not reissue the indexes).
**Scope:** mapping and session tracking only. No task body is authored, edited, or moved by this document.

---

## 0. Structural note

Lane 0 is the orchestration lane. Its task bodies live in the protocol documents, the master orchestration scripts, and the cross-lane coordination artifacts rather than in a single monolithic tasks file. The concordance for L0 therefore tracks protocol files, dispatch-gate decisions, and Phase 0 completion status rather than a traditional index-id → body-id mapping.

---

## Session 13 (2026-09-08)

- **protocol/00-dispatch-model.md created** — canonical dispatch model published; establishes the Q1-Q12 question sequence that gates all lane dispatch decisions.
- **FD-071..FD-081 written** — eleven founder decisions answering Q1 through Q12 of the dispatch gate; all dispatch-gate questions fully resolved. FD count: 81 closed.
- **FD-090..093 reserved (PENDING)** — four FD slots reserved for post-Phase-0 decisions; not yet authored.
- **run-phase-0.sh created (1,060 lines)** — top-level Phase 0 orchestration script written; drives the ordered execution sequence across all lanes for Phase 0 dispatch.
- **PENDING_FOUNDER_DECISIONS.md created (19 PFDs)** — collects all remaining L0 choices needed before full lane dispatch can proceed; 19 pending founder decisions catalogued.
- **L1-CONCORDANCE completed (0 orphans)** — L1 concordance fully reconciled; zero orphan task bodies remain.
- **L5 orphan indexing completed (26 bodies)** — all 26 L5 orphan bodies indexed and accounted for.
- **L3 Commands backfill completed (73 blocks)** — 73 command blocks backfilled into L3 concordance.
- **L0-04 register closed (7 REG items)** — 7 REG-line items in the L0-04 register confirmed closed.
- **verify_handover.sh: HANDOVER INTACT — 0 failures, 0 warnings.**
- **Phase 0 status: COMPLETE** — all 26 Phase 0 task bodies present and executable across all lanes; pending GitHub Team tier purchase by Founder before remote execution can proceed.
- **Final-wave completions (2026-09-08):**
  - L0-03-merge-train.md: CHK=NONE→CHK=ABSENT fail-open fix
  - _concordance-check.sh: body_ids() extended for L4-P* headings
  - manual/00 §9: per-lane routing lookup table added
  - L3-CONCORDANCE: 4 rows added (78→82)
  - L4-CONCORDANCE: 21 rows added (82→103 mapped, residue 35→14)
  - L5-CONCORDANCE: 15 unclaimed bodies indexed, 12 covered entries annotated
  - PENDING_FOUNDER_DECISIONS.md: PFD-020..032 added (total 32 PFDs)
  - _DECISION_DOCKET.md audit: 21 RESOLVED, 2 PENDING(PFD), 37 UNTRACKED
  - _RESIDUE.md + _ALIASES.tsv: 21 rows closed, residue 35→14
  - INDEX.md: 91→94 file count updated
  - Commands labels: 185 labels added across L1-00, L1-02, L1-05, L1-06, L5-07, L4-02, L4-03-write-paths, L4-04, L4-05, L4-07
  - L1-05 L1-605 TODO body: reconstructed from L1-02-09
  - verify_handover.sh: HANDOVER INTACT (2026-09-08 final)
