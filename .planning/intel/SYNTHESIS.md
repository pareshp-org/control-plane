# Synthesis Summary

Entry point for `gsd-roadmapper`. Produced by `gsd-doc-synthesizer` in `new` mode from `.planning/intel/classifications/*.json` (27 files) and their source documents.

## Doc counts by type

| Type | Count | Documents |
|---|---:|---|
| ADR | 6 | `master/01-lane-architecture.md`, `decisions/open-decisions.yaml`, `lanes/L0-04-decisions-register.md`, `docs/decisions-summary.md`, `PENDING_FOUNDER_DECISIONS.md`, `_FOUNDER_DECISIONS.md` |
| SPEC | 8 | `PARTITION.md`, `docs/reference/MultiProduct_MasterSpec_v4.0.md`, `master/04-phase-map.md`, `lanes/L1-00-charter.md`, `lanes/L2-00-charter.md`, `lanes/L3-00-charter.md`, `lanes/L4-00-charter.md`, `lanes/L5-00-charter.md` |
| PRD | 2 | `master/06-v1-scope.md`, `master/00-MASTER-PLAN.md` |
| DOC | 11 | `docs/bootstrap-runbook.md`, `infra/READINESS.md`, `docs/phase-0-complete.md`, `docs/architecture.md`, `lanes/L0-00-charter.md`, `lanes/L0-CONCORDANCE.md`, `lanes/L1-CONCORDANCE.md`, `lanes/L2-CONCORDANCE.md`, `lanes/L3-CONCORDANCE.md`, `lanes/L4-CONCORDANCE.md`, `lanes/L5-CONCORDANCE.md` |
| **Total** | **27** | |

## Decisions locked

1 document classified `locked: true`: `master/01-lane-architecture.md` (which itself declares subordination to `PARTITION.md` on any disagreement — see `INGEST-CONFLICTS.md` INFO-1). All other ADR-type documents are `locked: false`, though `_FOUNDER_DECISIONS.md` declares itself self-authoritative over "a plan document" wherever the two disagree.

## Requirements extracted

7 requirement entries in `intel/requirements.md`: `REQ-v1-scope-definition`, `REQ-v1-nine-declared-items`, `REQ-v1-six-residuals`, `REQ-v1-l0-decisions`, `REQ-master-plan-deliverable-classes`, `REQ-master-plan-not-built`, `REQ-master-plan-entry-criteria`, `REQ-master-plan-definition-of-done`.

## Constraints extracted

8 constraint entries in `intel/constraints.md`, type breakdown: 2 `protocol` (`PARTITION.md`, `master/04-phase-map.md`), 1 `schema` (the Master Spec v4.0), 5 `nfr` (the L1–L5 lane charters).

## Context topics

5 topics in `intel/context.md`, drawing from all 11 DOC sources: Phase 0 / Bootstrap, Lane 5 Integration Readiness, Architecture Overview (informal), Task-ID Concordances (L0–L5), L0 Integrator Charter (operational).

## Conflicts

**0 blockers, 2 warnings (competing/contradictory decision content), 3 info (auto-resolved by precedence).**

- WARNING 1: `REG-001`/`REG-002` are defined with different subjects in `decisions/open-decisions.yaml` versus `_FOUNDER_DECISIONS.md` (tied ADR precedence — cannot auto-resolve).
- WARNING 2: `_FOUNDER_DECISIONS.md`'s FD-093 (subsystem P → L4) contradicts its own earlier FD-002 (subsystem P → L0, forced, non-delegable), with no stated supersession.
- INFO 1–3: precedence-resolved, non-blocking simplifications/subordinations (`01-lane-architecture.md` deferring to `PARTITION.md`; `docs/architecture.md`'s stale canary-location and lane-label claims deferring to the ADR register and SPEC/ADR sources respectively).

See `.planning/INGEST-CONFLICTS.md` for full detail.

## Files produced

- `.planning/intel/decisions.md` — 6 ADR entries
- `.planning/intel/requirements.md` — 8 PRD entries (7 requirements + inline sub-items)
- `.planning/intel/constraints.md` — 8 SPEC entries
- `.planning/intel/context.md` — 5 topic-keyed DOC entries
- `.planning/INGEST-CONFLICTS.md` — conflict detection report (0 blockers / 2 warnings / 3 info)

## Status

**STATUS: AWAITING USER — 2 competing/contradictory decisions need resolution before routing** (see Warnings above). No hard blockers; safe to continue drafting downstream artifacts in parallel with resolving the two warnings, but the roadmapper should not silently pick a side on subsystem-P ownership (FD-002 vs FD-093) or on the REG-001/REG-002 subject mismatch.
