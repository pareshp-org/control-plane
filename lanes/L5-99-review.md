> **SUPERSEDED — 2026-09-02**  
> This review was produced against an earlier copy of the L5 lane files (17,000 lines).  
> The current files total 32,160 lines. All four BLOCKING findings (D-01, D-02, D-04, D-14) have  
> been verified false at triage. **Do not act on any finding in this document** without  
> re-deriving it against the current files. See `review-harvest/_DISPATCH_GATE.md` §3.

---

# L5-99 — LANE 5 COHERENCE REVIEW (FRESH — 2026-09-02)

**Reviewed:** L5-00-charter.md, L5-01-org-and-access.md, L5-02-secrets-and-boundaries.md,  
L5-03-layer-b.md, L5-04-ops-vm.md, L5-05-assets-ai-notify.md, L5-06-tasks.md  
**Not in scope but exists:** L5-07-tests-and-runbook.md (additional tasks and tool deps; requires separate review pass)  
**Review date:** 2026-09-02  
**Total corpus size:** ~32,000 lines

---

## VERDICT

# BLOCKED

**Root cause:** L5-06-tasks.md was authored as a self-contained replacement task system but was never reconciled with L5-01 through L5-05. The Founder must designate exactly one task system as authoritative before any executor can start Phase 0 work.

---

## BLOCKING findings

### B-01 — Two parallel, mutually contradictory task systems
L5-06-tasks.md ("LANE 5 ATOMIC TASK LIST", tasks L5-T01..L5-T59) and the five phase files (L5-01 through L5-05) both specify complete, self-contained implementations of the same subsystems, to different paths, with different toolchains, under incompatible task-id schemes. They cannot both be executed without collisions.

- L5-06 creates: `access/model/`, `access/ai-runtime/`, `access/layerb/`, `access/tests/`
- L5-01 creates: `access/org/`, `access/permissions/`, `access/teams/`, `access/codeowners/`

**Decision needed from L0:** Designate exactly one task system as authoritative. Retire the other.

### B-02 — Six different task-id formats; cross-file dependencies cannot close

| File | Format | Example |
|---|---|---|
| L5-00-charter.md | `L5-<FF>-<TT>` (mandate) | `L5-00-01` |
| L5-01-org-and-access.md | `L5-01-T<TT>` | `L5-01-04` |
| L5-02-secrets-and-boundaries.md | `L5-P2-T<TT>` | `L5-P2-T03` |
| L5-03-layer-b.md | `L5-P3-<NN>` | `L5-P3-07` |
| L5-04-ops-vm.md | `L5-04-T<TT>` | `L5-04-14` |
| L5-05-assets-ai-notify.md | `L5-05-[Q/K/R]<NN>` | `L5-05-Q02` |
| L5-06-tasks.md | `L5-T<TT>` (flat) | `L5-T30` |

**Decision needed:** Standardize on one format, or explicitly declare L5-06 as the only valid namespace.

### B-03 — Charter DoD is unprovable: `l5-validate.sh` implements only 1 of 16 modes
DoD-01 through DoD-16 all invoke `bash infra/tools/l5-validate.sh --<mode>`. Only `--layout` is implemented; the other 15 modes return exit 2 with `L5 VALIDATE UNIMPLEMENTED-MODE`. L5-06 builds a different toolchain (`lane_tree_check.sh`, `validate_handoff.py`, `pytest`) that never extends this script.

**Decision needed:** Either assign tasks to implement each validator mode, or redesign the DoD proof commands to match the toolchain the authoritative task system actually builds.

### B-04 — Charter's fixed `access/` layout contradicted by both task systems
Charter §2.1 specifies subdirectories: `model/`, `branch-protection/`, `secrets/`, `layer-b/`, `fail-closed/`, `ai-runtime/`, `published/`. L5-01 creates a completely different set; L5-06 partially overlaps but diverges on key names (`layerb/` vs `layer-b/`). The DoD-01 layout check would fail on either system.

**Decision needed:** Revise §2.1 to match the authoritative task system, or revise the task system to match §2.1.

---

## HIGH findings

### H-01 — Python 3.12 not enforced (FD-005 violation)
FD-005 mandates Python 3.12 with exact `==` pins. L5-01 accepts Python 3.9+; L5-02 accepts Python 3.10+; L5-03 through L5-06 have no interpreter version assertion. **[Fix dispatched: separate agent adding 3.12 checks to all phase files.]**

### H-02 — `yq` required but undeclared in any pinned toolchain
L5-03 §1 and L5-07 both require `yq` in their preflight checks. `yq` is not listed in any `requirements.txt`, not in the charter's prerequisites, and has no prescribed installation step.
**Fix:** Add `yq` to charter §1.1 tool-prerequisite list with a version pin and install instruction.

### H-03 — Four env-var names for the control-plane root
`$CONTROL_PLANE_ROOT` (L5-00 charter), `$CP_ROOT` (L5-01, L5-02, L5-04), `$CP` (L5-03, L5-05), `$CONTROL_PLANE` (L5-07). DoD commands use `$CONTROL_PLANE_ROOT`; phase files use their own. Cross-file DoD verification fails. **[Fix dispatched: separate agent standardizing to `$CONTROL_PLANE_ROOT`.]**

### H-04 — Open escalations E-05 and E-08 gate executable tasks
E-05 RESOLVED (FD-062): L5_ROUTING_CHANNEL env var, default engineering-alerts — L5-T41 routing integration test unblocked for DoD-10. E-08 (private-path deferral) gates L5-04-02 (a prereq for T03..T17) with no waiver-shape fallback.
**E-08 DEFERRED (FD-063):** L5-04-02 is marked BLOCKED-PENDING-E-08; private-path value is set at Phase 1 deployment configuration. E-08 is no longer an open decision requiring Founder input before Phase 1.

---

## LOW findings

- **L-01** — Size scale contradictions across files (charter §11.2 vs L5-02/04/06 definitions; T16/T17 marked L but exceed charter's L-task maximum)
- **L-02** — Six non-identical blocker templates across all phase files
- **L-03** — L5-01 §0.6 commit trailer `Lane: L5` not in charter §11.3 mandatory template
- **L-04** — L5-07-tests-and-runbook.md exists but was not fully reviewed; contains additional tasks, uses `$CONTROL_PLANE`, requires `yq`, and may carry further issues

---

## What the Founder must decide to unblock L5

1. **Which task system is authoritative** — L5-06 alone, or L5-01..L5-05 together? (Resolves B-01, B-02, B-03, B-04 cascades)
2. **Fix the access/ directory layout** — charter §2.1 vs the authoritative task system
3. **Resolve E-08** escalation (for H-04) — E-05 RESOLVED (FD-062)
