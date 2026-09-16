# Bootstrap Runbook — Multi-Product Engineering OS

**Author:** bendrohit-eng (L0 Integrator)  
**Status:** Pre-Phase 0 (2026-09-09)  
**FD Reference:** FD-014 (dispatch gate), FD-067..081, FD-082..112

## Overview
This runbook covers the bootstrap sequence from Phase 0 (infra creation) through Phase 1 (first product dispatch).

## Pre-Phase 0 Checklist
- [x] All 112 Founder Decisions recorded (FD-001..112)
- [x] 31/32 PFDs resolved (PFD-006 deferred)
- [x] All 6 coherence reviews PASS (L0-L5-99)
- [x] verify_handover.sh: HANDOVER INTACT (re-verified Session 15 final, post T-infix normalization)
- [x] _concordance-check.sh: 5/5 lanes OK (re-verified post FD-082 normalization + FD-095 absorption)
- [x] Schemas created: 12 JSON schemas
- [x] Registries initialized with bootstrap seeds + CAP-0001 sample capability
- [x] Validator CLI: all 18 rules (R01-R18) fully implemented with YAML parsing
- [x] 41 integration tests passing (rule-level pass/fail coverage for every rule)
- [x] CI/CD workflows: 16 workflow files (incl. per-product placeholders P1-P8)
- [x] Git repo initialized, 12 commits
- [x] Local L2 gate-check/push-guard scripts (mirror lane-guard.yml locally)
- [x] run-phase-0.sh verified end-to-end via `--dry-run` (zero credentials required): branch-bootstrap for L0-P0-023 (`main`/`integration` auto-created with an empty initial commit if missing), 89-entry `event_type` enum self-authored (D114-D, no manual Founder population), 23 contract stubs auto-created by `append_register.py` at registration time — no manual steps remain before execution
- [ ] Phase 0 executed (needs GITHUB_TOKEN PAT)
- [ ] 8 product names supplied (for facts.tsv)
- [ ] PFD-006: break-glass second owner decided
- [ ] 18 protocol blocking defects require L0 decision (`protocol/_98-DEEP-REVIEW.md` §4)

## Phase 0: Execute

Set up GitHub repos:
```bash
# Set PAT (never store in files)
$env:GITHUB_TOKEN = "your-pat-here"

# Dry run first
bash run-phase-0.sh --dry-run

# Execute Phase 0
bash run-phase-0.sh
```

Creates:
- `pareshp-org/control-plane` (public)
- `pareshp-org/control-plane-records` (public)
- Branch protection on main
- CODEOWNERS pushed

**Zero manual steps:** three former blockers are now self-handled by the script on every run:
- **L0-P0-023** (the contract freeze — PRs against `main`, merges into `integration`) no longer depends on an earlier task having created either branch: both are bootstrapped with an empty initial commit if missing, right before each is referenced.
- The full **89-entry `event_type` enum** (`C-EVT-ENUM-1` at L0-P0-011, plus its human-readable companion `contracts/event-types.yaml` at L0-P0-025 — all identifiers per D114-D) is self-authored. No Founder population step remains.
- All **23 registered contract stubs** are auto-created by `contracts/ci/append_register.py` as a side effect of registration, so L0-P0-021's `verify_contracts.py` no longer fails on missing stub files.

`--dry-run` completes end-to-end with zero credentials; `GITHUB_TOKEN` is needed only for the real run.

## Phase 0 → Phase 1 Bridge

After Phase 0 completes:

1. **Push implementation to GitHub:**
```bash
cd Code/implementation
git remote add origin https://github.com/pareshp-org/control-plane.git
git push -u origin master
```

2. **Install git hooks locally:**
```bash
make setup
```

3. **Verify all checks pass:**
```bash
make check
```

4. **Upgrade to Team plan (recommended):**
   - Go to https://github.com/organizations/pareshp-org/billing
   - Change REPO_VISIBILITY to "private" in contracts/project-config.sh
   - Make repos private

## Phase 1: First Product Dispatch

Prerequisites:
- Phase 0 complete
- 8 product names in facts.tsv
- PFD-006 decided (break-glass second owner)

Steps:
1. Run `bash scripts/l0/dispatch-check.sh` — must print "DISPATCH GATE: CLEAR"
2. Run `bash scripts/l1/setup-repo-skeleton.sh --mode apply` for each product
3. Run `bash scripts/l3/sync-records.sh --mode apply`
4. Run `bash scripts/metrics/validate-metrics.sh` for baseline

## Runbook Quick Reference

| Task | Command |
|------|---------|
| Concordance check | `make concordance` |
| Verify handover | `make handover` |
| Canary check | `make canary` |
| Validator run | `make validate` |
| Prerequisites check | `bash scripts/provision/check-prerequisites.sh` |
| Dispatch gate | `bash scripts/l0/dispatch-check.sh` |
| Merge check | `bash scripts/l0/merge-check.sh --branch <name>` |
| Orphan detection | `bash scripts/l3/run-orphan-check.sh` |
| Break glass | `bash scripts/break-glass.sh --reason "..." --duration 4h` |
| Topology check | `bash scripts/l5/topology-check.sh` |
| SBOM generation | `bash scripts/security/generate-sbom.sh --product <id> --tag <version>` |

## Key Files
| File | Purpose |
|------|---------|
| `contracts/project-config.sh` | Single source of truth |
| `_FOUNDER_DECISIONS.md` | All 112 FDs |
| `PENDING_FOUNDER_DECISIONS.md` | 32 PFDs (31 resolved, 1 deferred) |
| `run-phase-0.sh` | Phase 0 orchestration |
| `PHASE-0-EXECUTION.md` | Phase 0 run guide |
| `_concordance-check.sh` | 5-lane concordance gate |
| `verify_handover.sh` | Handover integrity check |
| `master/INDEX.md` | Full file inventory (111 files) |
| `registries/topology.yaml` | Governance topology (L5) |
| `facts.tsv` | Product facts table (FD-030) |

## Break Glass Procedure
1. `bash scripts/break-glass.sh --reason "emergency" --duration 4h`
2. Notify L5 owner immediately
3. Record must be reviewed within 24h (AT-022, FD-083)
4. Second owner (PFD-006): TBD before Phase 1 go-live

## Upgrade Path: Free → Team Plan
Currently on GitHub Free plan with public repos.
When ready to go private:
1. Purchase Team plan ($4/user/month) at github.com/organizations/pareshp-org/billing
2. Update `REPO_VISIBILITY="private"` in `contracts/project-config.sh`
3. Run: `gh repo edit pareshp-org/control-plane --visibility private`
4. Run: `gh repo edit pareshp-org/control-plane-records --visibility private`
