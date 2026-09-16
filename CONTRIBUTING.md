# Contributing to the Multi-Product Engineering OS

## Overview
This is a 5-lane engineering OS for a ~9-person software company managing ~20 products.
See `_FOUNDER_DECISIONS.md` for all architectural decisions (FD-001..112).

## 5-Lane Model
| Lane | Name | Owner | Responsibility |
|------|------|-------|----------------|
| L0 | Integrator | bendrohit-eng | Merge authority, Phase 0/1 dispatch |
| L1 | Schema Contracts | bendrohit-eng (bootstrap) | Validator, schemas, registries |
| L2 | CI/CD | bendrohit-eng (bootstrap) | Pipeline, branch guard, releases |
| L3 | Record Store | bendrohit-eng (bootstrap) | Provisioning, records, snapshots |
| L4 | Metrics | bendrohit-eng (bootstrap) | Scorecards, capacity, planning |
| L5 | Access/Governance | bendrohit-eng (bootstrap) | Policies, audit, break-glass |

## Before Contributing
1. Read `PHASE-0-EXECUTION.md` for Phase 0 status
2. Check `_FOUNDER_DECISIONS.md` for relevant FDs
3. Run `make check` — must pass all 5-lane concordance checks
4. Install git hooks: `make setup`

## Task IDs
Format: `L<N>-<FF>-<NN>` (e.g., `L1-05-001`) — see FD-082 (no T-infix).
File: `lanes/L<N>-<FF>-<filename>.md`

## Validator (L1)
Run: `make validate` (or `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root records/ --format json`)
Rules: R01-R18 — all 18 fully implemented with YAML parsing in `validators/registry/rules/`
Tests: `make test` (41 integration tests covering pass/fail for every rule)

## Pull Requests
- Actor gate: only `bendrohit-eng` can merge in bootstrap mode (FD-086)
- Required: lane-guard CI passes, canary intact, concordance OK
- See `CODEOWNERS` — all paths owned by `@bendrohit-eng` in bootstrap

## Phase 0
Run Phase 0 to create the GitHub repos:
```bash
$env:GITHUB_TOKEN = 'your-pat'
bash run-phase-0.sh --dry-run   # preview
bash run-phase-0.sh              # execute
```
See `PHASE-0-EXECUTION.md` for full instructions.
