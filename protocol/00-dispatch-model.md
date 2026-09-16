# 00 — DISPATCH MODEL

# Canonical answers to the dispatch gate questions (FD-014, §5.1 Q1–Q3).
# Authoritative for HOW tasks are delivered, WHAT id grammar is canonical,
# and WHICH execution model applies.
# Conforms to `Code/implementation/PARTITION.md` (FROZEN).

---

## Background

The dispatch gate (`review-harvest/_DISPATCH_GATE.md` §5.1) identified three unresolved
contradictions that block dispatch of any lane:

| Q | Short title | Items blocked |
|---|---|---|
| Q1 | Task delivery format | DF-0046, 0225, 0308, 0325; all 5 lanes at task 1 |
| Q2 | Task-ID grammar + branch grammar | DF-0008, 0010, 0068, 0151, 0161, 0221, 0266–0268, 0315, 0316 |
| Q3 | Execution model | DF-0009; all 5 lanes |

The contradictions arose because `manual/01` §0, `manual/02` §2.1, and `manual/00` §9
gave three incompatible answers to Q1; six live id schemes across 845 task ids gave six
incompatible answers to Q2; and `manual/00` §7 and the lane packs §0 gave incompatible
answers to Q3. The sections below are the Founder's definitive rulings.

---

## Dispatch Model Clarification (FD-071/082/073, 2026-09-08)

The following are the canonical answers to dispatch gate §5.1 Q1–Q3:

### Q1 — Task delivery format
A task is delivered to an agent as a **task card**: the complete body of the task's heading
block from the lane plan file (e.g. `lanes/L1-04-ci-gate-engine.md §L1-04-02`), extracted
verbatim and passed as the agent prompt's context block. The `tasks/<ID>.md` form is a
convenience alias pointing to the same content.

### Q2 — Task-ID grammar and branch grammar (FD-082, extending FD-072)
Canonical task-id: `<LANE>-<FF>-<NN>` where LANE is L0–L5, FF is the two-digit file number,
NN is the two-digit task number within that file. Example: `L1-04-02`.
Canonical branch: `lane/<N>/<descriptive-slug>` where N is 0–5. Example: `lane/1/schema-registry`.
All other schemes (L1-P0-Tnn, L5-01-Tnn, L0-P0-001) are legacy and resolve to this grammar.
As of this note, `manual/00` §9, `manual/02` §2.1, and `lanes/L1-05-tasks.md` still instruct
and use the older two-part `L{lane}-{seq}` form and have not yet been migrated to the
three-part grammar above; this migration is outstanding and remains open under dispatch gate
item `DF-0008` (Q2).

### Q3 — Execution model
One task per agent session. Each session sources `contracts/project-config.sh`, checks out the
lane branch, runs the task body commands, and opens a PR to `integration`. Continuous executor
mode (multiple tasks per session) is not used — task bodies are too interdependent for safe
batching without explicit checkpointing.

---

## Cross-check: L0-00-charter.md vs Q2 (FD-072 note, 2026-09-08)

**Discrepancy resolved.** The charter (`lanes/L0-00-charter.md`) and the lane plan files
previously used a `T`-infix form (`L0-00-T01`) and a `T-` prefix variant (`T-L1-04-01`)
respectively. FD-082 (PFD-008, 2026-09-08) closed this by selecting **Option A —
`L<N>-<FF>-<NN>` (no `T` infix), effective immediately**, confirming and extending FD-072's
ruling, and a normalization pass brought the corpus into conformance.

The current files already conform to the canonical grammar:

- Charter task headings: `L0-00-01`, `L0-00-02`, … `L0-00-09`
- Charter blocker example: `L1-03-07`, `L4-02-03`
- Lane plan files: `L1-04-01`, `L1-04-02`, … `L1-04-09` (no `T-` prefix)

Both match the Q2 canonical grammar `L<N>-<FF>-<NN>` (no `T` infix or prefix). The dispatch
gate item `DF-0008` (Q2) is resolved on this sub-point by FD-082.

Branch grammar is consistent: the charter uses `lane/$n/<slug>` which matches
`lane/<N>/<descriptive-slug>`. No branch grammar discrepancy.
