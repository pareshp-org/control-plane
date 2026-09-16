# Architecture: Multi-Product Engineering OS

## System Overview
An internal engineering OS for a ~9-person software company running ~20 products.
Single person (Founder/L0 Integrator) holds all 5 lane seats during bootstrap.

## 5-Lane Architecture

```
┌─────────────────────────────────────────────────────────┐
│  L0  │  Integrator  │  Merge authority, dispatch gate   │
├─────────────────────────────────────────────────────────┤
│  L1  │  Schema Contracts  │  Validator, schemas, regs   │
├─────────────────────────────────────────────────────────┤
│  L2  │  CI/CD  │  Branch guard, pipelines, releases     │
├─────────────────────────────────────────────────────────┤
│  L3  │  Record Store  │  Provisioning, records           │
├─────────────────────────────────────────────────────────┤
│  L4  │  Metrics  │  Scorecards, capacity, planning       │
├─────────────────────────────────────────────────────────┤
│  L5  │  Access/Governance  │  Policies, audit, gate      │
└─────────────────────────────────────────────────────────┘
```

## Key Decisions (Selected)
| FD | Decision |
|----|----------|
| FD-067 | L0 integrator: bendrohit-eng |
| FD-082 | Task ID format: L<N>-<FF>-<NN> (no T-infix) |
| FD-086 | Actor gate: bendrohit-eng only in bootstrap |
| FD-094 | Validator CLI: Option B (python -m validators.registry.cli) |
| FD-096 | Schema layout: flat (schemas/registry/<name>.v1.schema.json) |
| FD-100 | Registry layout: dir-per-item (registries/<type>/<id>.yaml) |
| FD-102 | Branch protection: PRs required for main |
| FD-106 | Registry canary: registries/people/_canary.yaml |
| FD-108 | Orphan detection: 5 surfaces |
| FD-112 | DevLake: deferred from V1 scope |

## Data Flow
```
Registries (L1) → Records (L3) → Metrics (L4)
     ↓                  ↓              ↓
  Schemas            Board/Work     Scorecards
     ↓                  ↓              ↓
  Validator          Orphan Det.    Capacity
     ↓                  ↓              ↓
  CI Gate (L2)       L5 Audit       FTE Model
```

## Repository Structure
```
implementation/
├── contracts/          # Single source of truth configs
├── lanes/             # 66 plan files (L0-L5)
├── schemas/           # JSON schemas (12 files)
├── registries/        # Runtime registries (YAML, dir-per-item)
├── records/           # Runtime records (board, work, metrics)
├── validators/        # L1 validator CLI (Option B, R01-R18)
├── scripts/           # Operational scripts (l0/, l1/, l5/, metrics/, provision/)
├── .github/workflows/ # CI/CD (16 workflow files)
├── tests/             # Integration tests
├── ops-vm/            # Ops VM stack (DevLake deferred)
└── docs/              # Architecture and asset docs
```

## Phase 0 Status
- run-phase-0.sh: READY
- Repos: pareshp-org/control-plane, pareshp-org/control-plane-records (public)
- See PHASE-0-EXECUTION.md
