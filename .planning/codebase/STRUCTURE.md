---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
# Codebase Structure

**Analysis Date:** 2026-09-16

## Directory Layout

```
control-plane/
├── access/                 # L5 — Access control, permissions, secrets model
│   ├── model/             # Permission matrix, team definitions, safe defaults
│   ├── schemas/           # Access-related YAML schemas
│   ├── secrets/           # Secret boundaries, tier definitions, incident handling
│   ├── tests/             # Access model tests (test_access_model.py, test_pi_gate.py)
│   ├── tools/             # Validation tools (check_arming_order.py, validate_access_config.py)
│   └── invariants/        # Invariant definitions for access controls
├── assets/                 # L5 — Asset tracking and inventory
│   ├── inventory/         # Asset registry
│   ├── deadlines/         # Asset lifecycle deadlines
│   └── watch/             # Asset monitoring
├── bootstrap/              # L0 — Phase-0 setup scripts and scaffolding
├── contracts/              # L0 — Frozen contract definitions (immutable after phase 0)
│   ├── registry/          # Registry contracts (people.registry.v1.json, roles.registry.v1.json)
│   ├── reconciler/        # Reconciler contracts (drift-finding.v1.json, repair-record.v1.json)
│   ├── records/           # Record contracts (event.envelope.v1.json, record.envelope.v1.json)
│   ├── access/            # Access model contracts (permission-model.v1.yaml, protection.template.v1.yaml)
│   ├── provisioning/      # Provisioning contracts (operation.v1.yaml)
│   ├── fixtures/          # Test fixtures (one dir per test scenario)
│   ├── stubs/             # Generated code/protocol buffers from contracts
│   └── register.yaml      # Master contract registry (audit log)
├── decisions/              # L0 — Founder decisions and design records
├── docs/                   # L0 — Documentation and guides
├── e2e/                    # L3-P2 — End-to-end integration tests
├── events/                 # L4 — Event audit trail (one file per event, never merged)
│   └── YYYY-MM-DD/        # Events partitioned by date
├── gate-state/             # L0 — CI gate state and status tracking
├── infra/                  # L5 — Infrastructure configuration (networks, runners, deadman)
│   ├── deadman/           # Deadman switch configuration
│   ├── hosts/             # Host provisioning
│   ├── runners/           # GitHub Actions runner configuration
│   ├── network/           # Network policies
│   └── layer-b/           # Layer B infrastructure
├── lanes/                  # L0-L5 — Lane workflow configurations
├── manual/                 # L0 — Manual operation runbooks
├── master/                 # L0 — Master branch configurations
├── metrics/                # L4 — Metrics computation and reporting
│   ├── attention/         # Alerts and attention-worthy signals
│   ├── boards/            # Metric dashboard definitions
│   ├── compute/           # Metric calculation logic
│   ├── taxonomy/          # Metric naming and categorization
│   └── register/          # Metric registry
├── notify/                 # L5 — Notification system (channels, escalation, routing)
│   ├── channels/          # Notification backends (Slack, email, etc.)
│   ├── routes/            # Routing rules for notifications
│   ├── escalation/        # Escalation policies
│   └── assisted/          # Assisted notification handling
├── ops-vm/                 # L5 — Operations VM configuration and tooling
│   ├── checks/            # Health checks (selfcheck, drill, liveness)
│   ├── layer-b/           # Layer B VM operations
│   ├── provision/         # VM provisioning
│   ├── jobs/              # Scheduled jobs and cron tasks
│   ├── prometheus/        # Prometheus monitoring
│   ├── grafana/           # Grafana dashboards and provisioning
│   ├── slo/               # Service-level objectives
│   ├── renovate/          # Renovate (dependency update) configuration
│   └── tests/             # VM integration tests
├── protocol/               # L0 — Protocol and interface definitions
├── reconciler/             # L3 — Drift reconciliation engine (Phase-1 core)
│   ├── comparators/       # Drift comparator modules (18+ comparators)
│   │   ├── branch_protection.py     # Branch protection drift
│   │   ├── environments.py           # Environment configuration drift
│   │   ├── team_membership.py        # Team membership drift
│   │   ├── codeowners.py            # CODEOWNERS file drift
│   │   ├── cmp_10_lifecycle.py      # Lifecycle policy drift
│   │   └── [13 more...]
│   ├── state/             # State adapters (fixture_adapter.py, live_adapter.py)
│   ├── repair/            # Drift repair utilities
│   ├── gap/               # Gap classification and handling
│   ├── orphans/           # Orphan detection and classification
│   ├── fixtures/          # Test fixtures (one dir per scenario: fixture-a, etc.)
│   ├── tests/             # Comparator unit tests
│   ├── cli.py             # Main entry point: `python -m reconciler list|run`
│   ├── model.py           # Core models (DriftClass, Finding, Level)
│   ├── registry.py        # Comparator registration mechanism
│   ├── runrecord.py       # Run record aggregation and reporting
│   ├── canary.py          # Canary validation
│   └── [support modules]
├── records/                # L4 — Audit trail and record storage (one file per record)
│   ├── people/            # People records
│   ├── products/          # Product records
│   ├── decisions/         # Decision records
│   ├── incidents/         # Incident records
│   ├── deployments/       # Deployment records
│   ├── postmortems/       # Postmortem records
│   ├── security-reviews/  # Security review records
│   └── [other record types]
├── registries/             # L1 — Authoritative reference data (one file per item)
│   ├── people/            # Person records (one YAML per person)
│   ├── roles/             # Role definitions
│   ├── services/          # Service definitions
│   ├── capabilities/      # Capability vocabulary
│   ├── platform/          # Platform record
│   ├── policies/          # Policy records
│   ├── exceptions/        # Exception records (non-conformance)
│   └── framework/         # Framework references
├── schemas/                # L1 — JSON/YAML schema definitions
│   ├── registry/          # Registry schemas (people.v1.json, roles.v1.json, etc.)
│   ├── records/           # Record schemas (event-type.enum.v1.yaml, etc.)
│   ├── product/           # Product definition schemas
│   ├── governance/        # Governance schemas
│   ├── metrics/           # Metrics schemas
│   ├── board/             # Board/kanban schemas
│   └── work/              # Work item schemas
├── scripts/                # L0-L5 — Build and automation scripts
│   ├── l1/                # L1 lane scripts
│   ├── l2/                # L2 lane scripts
│   ├── l3/                # L3 lane scripts
│   ├── l4/                # L4 lane scripts
│   ├── l5/                # L5 lane scripts
│   ├── provision/         # Provisioning scripts
│   ├── security/          # Security-related scripts
│   ├── git-hooks/         # Git hook scripts (pre-commit, commit-msg)
│   ├── metrics/           # Metrics computation scripts
│   ├── phase0-lib/        # Phase-0 provisioning library functions
│   └── [other scripts]
├── templates/              # L2 — Reusable workflow templates
│   └── workflows/         # GitHub Actions workflow templates
├── tests/                  # All tests (integration, unit)
│   ├── integration/       # Integration tests (test_validator.py, test_rules.py, etc.)
│   └── __init__.py
├── tools/                  # L2-L5 — Operational tooling
│   ├── provision/         # L3 — GitHub provisioning toolkit
│   │   ├── cli.py                    # Provisioning CLI entry point
│   │   ├── plan.py                   # Plan generation
│   │   ├── teams.py                  # Team provisioning
│   │   ├── repo.py                   # Repository provisioning
│   │   ├── protection.py             # Branch protection rules
│   │   ├── environments.py           # Environment provisioning
│   │   ├── codeowners.py             # CODEOWNERS generation
│   │   ├── change_role.py            # Role change operations
│   │   └── tests/                    # Provisioning tests
│   ├── evidence/          # L2 — Evidence collection and gates
│   │   ├── [evidence collection modules]
│   │   ├── canary/                   # Canary validation tools
│   │   ├── gates/                    # Gate enforcement
│   │   └── tests/                    # Evidence tests
│   └── records/           # L4 — Record and metrics tools
│       ├── [record capture modules]
│       ├── dispatch/                 # Event dispatching
│       ├── ingest/                   # Record ingestion
│       └── [other record tools]
├── validators/             # L1/L3/All — Validation and compliance checking
│   ├── registry/          # L1 — Registry schema validator
│   │   ├── cli.py                    # `python -m validators.registry.cli --root . ...`
│   │   ├── loader.py                 # Schema and registry loader
│   │   ├── rules/                    # Validation rules
│   │   └── tests/                    # Validator tests
│   └── drift/             # L3 — Drift assertion validators
│       ├── assert_protection.py      # Branch protection assertions
│       ├── assert_codeowners.py      # CODEOWNERS assertions
│       ├── [other drift assertions]
│       └── tests/                    # Drift assertion tests
├── Makefile                # L0 — Build targets (make check, validate, test, etc.)
├── PARTITION.md            # L0 — Authoritative lane/path ownership contract
├── CONTRIBUTING.md         # L0 — Contribution guidelines
├── _FOUNDER_DECISIONS.md   # L0 — Decision log (FD-XXX)
├── _concordance-check.sh   # L0 — 5-lane concordance verification script
├── facts.tsv              # L0 — Fact database
├── pyproject.toml         # L0 — Python project metadata
├── pytest.ini             # L0 — Pytest configuration
└── requirements-dev.txt   # L0 — Development dependencies
```

## Directory Purposes

**access/:**

- **Purpose:** Access control model, permission matrix, team structure, secrets boundaries
- **Contains:** YAML definitions, Python validation tools, invariant tests
- **Key files:** `access/model/permission-matrix.yaml`, `access/model/teams.yaml`, `access/secrets/envelope/`

**reconciler/:**

- **Purpose:** Core drift detection engine (Phase-1)
- **Contains:** 18+ comparator modules, state adapters, run orchestration
- **Key files:** `reconciler/cli.py` (entry point), `reconciler/model.py` (DriftClass, Finding), `reconciler/registry.py` (registration)

**validators/:**

- **Purpose:** Schema validation and regulatory compliance checking
- **Contains:** Registry schema validator, drift assertion rules
- **Key files:** `validators/registry/cli.py` (L1 validator entry point), `validators/drift/` (assertion rules)

**tools/provision/:**

- **Purpose:** GitHub operations (teams, repos, permissions, branch protection)
- **Contains:** GitHub API integrations, plan generation, verification
- **Key files:** `tools/provision/cli.py` (provisioning entry point), `tools/provision/plan.py` (plan generation)

**tools/evidence/:**

- **Purpose:** Evidence collection and compliance gate enforcement
- **Contains:** Workflow evidence verification, canary checks, production gate rules
- **Key files:** `tools/evidence/gates/` (gate definitions)

**tools/records/:**

- **Purpose:** Audit trail maintenance and metrics computation
- **Contains:** Event capture, record ingestion, metrics dispatch
- **Key files:** `tools/records/dispatch/` (event dispatching), `tools/records/ingest/` (record capture)

**contracts/:**

- **Purpose:** Frozen interface specifications between components/lanes
- **Contains:** JSON/YAML schemas for all data contracts
- **Key files:** `contracts/register.yaml` (contract audit log), `contracts/fixtures/` (test scenarios)

**registries/:**

- **Purpose:** Authoritative reference data
- **Contains:** One YAML file per item (people, roles, services, capabilities)
- **Key files:** `registries/people/*.yaml`, `registries/roles/*.yaml`, `registries/services/*.yaml`

**schemas/:**

- **Purpose:** Data structure definitions for validation
- **Contains:** JSON schemas for registries, records, products
- **Key files:** `schemas/registry/*.json`, `schemas/records/*.yaml`

**records/:**

- **Purpose:** Audit trail storage (one file per record, never deleted)
- **Contains:** Timestamped records of decisions, incidents, deployments, etc.
- **Key files:** Directory-per-type pattern (e.g., `records/decisions/`, `records/incidents/`)

**events/:**

- **Purpose:** Event audit trail (immutable, append-only)
- **Contains:** One JSON file per event, partitioned by date
- **Key files:** `events/YYYY-MM-DD/*.json` (one file per event, never merged or edited)

**infra/:**

- **Purpose:** Infrastructure configuration
- **Contains:** Network policies, runner configs, deadman switches, layer-b provisioning
- **Key files:** `infra/layer-b/`, `infra/runners/`, `infra/deadman/`

**ops-vm/:**

- **Purpose:** Operations VM configuration, monitoring, scheduled jobs
- **Contains:** Prometheus/Grafana configs, health checks, job definitions
- **Key files:** `ops-vm/prometheus/`, `ops-vm/grafana/`, `ops-vm/jobs/`

**notify/:**

- **Purpose:** Notification system and escalation routing
- **Contains:** Channel definitions, routing rules, escalation policies
- **Key files:** `notify/channels/`, `notify/routes/`, `notify/escalation/`

**scripts/:**

- **Purpose:** Build automation and lane-specific tooling
- **Contains:** Lane scripts (L1-L5), provisioning helpers, metrics computation
- **Key files:** `scripts/l0/`, `scripts/l1/`, etc., `scripts/phase0-lib/`

## Key File Locations

**Entry Points:**

- `reconciler/cli.py` - Phase-1 reconciliation: `python -m reconciler list|run`
- `validators/registry/cli.py` - L1 registry validation: `python -m validators.registry.cli --root . --as-of YYYY-MM-DD`
- `tools/provision/cli.py` - GitHub provisioning: `python tools/provision/cli.py plan|apply|verify`
- `Makefile` - Build targets: `make check|validate|test|phase0-dry`

**Configuration:**

- `.github/workflows/` - GitHub Actions workflow definitions
- `PARTITION.md` - Lane/path ownership contract
- `CONTRIBUTING.md` - Contribution guidelines
- `_FOUNDER_DECISIONS.md` - Design decisions (FD-XXX)

**Core Logic:**

- `reconciler/comparators/*.py` - Individual drift detection rules (18+ modules)
- `access/model/` - Access control definitions
- `tools/provision/*.py` - GitHub operations
- `validators/drift/*.py` - Drift assertion rules

**Testing:**

- `tests/integration/` - Integration tests (test_validator.py, test_rules.py, test_robustness.py)
- `reconciler/fixtures/` - Test fixtures for reconciler
- `reconciler/tests/` - Unit tests for comparators
- `tools/provision/tests/` - Provisioning unit tests

## Naming Conventions

**Files:**

- **Python modules:** `snake_case.py` (e.g., `branch_protection.py`, `test_access_model.py`)
- **YAML registries:** `item-id.yaml` (e.g., `people/alice.yaml`, `roles/admin.yaml`)
- **Event files:** `YYYY-MM-DD/event-id.json` (e.g., `events/2026-09-15/acc-001.json`)
- **Decision records:** `decisions/FD-NNN.md` (FD = Founder Decision)
- **Fixtures:** Directory name matches fixture ID (e.g., `reconciler/fixtures/fixture-a/`)

**Directories:**

- **Plural for collections:** `registries/`, `schemas/`, `records/`, `events/`, `contracts/`
- **Singular for singular:** `reconciler/`, `validators/`, `tools/`
- **Lane directories:** `lane/N/*` in git branches; `scripts/lN/` in trunk
- **Category organization:** `registries/{category}/{item}.yaml`, `records/{type}/{id}.json`

**Functions & Classes:**

- **Python functions:** `snake_case()` (e.g., `load_yaml()`, `compare()`)
- **Python classes:** `PascalCase` (e.g., `DriftClass`, `Finding`, `DeclaredState`)
- **Comparator IDs:** Kebab-case identifiers (e.g., `branch-protection`, `team-membership`)

**Comparator Modules:**

- **Pattern:** One comparator per file; filename hints at domain
- **Examples:** `branch_protection.py` (cmp-branch-protect), `environments.py` (cmp-environments), `team_membership.py` (cmp-team-membership)
- **Registration:** `@comparator(id, fail_class=DriftClass.X)` decorator

## Where to Add New Code

**New Comparator (drift detection rule):**

- **Implementation:** `reconciler/comparators/new_comparator.py`
- **Pattern:** Function with `@comparator(id="cmp-xxx", fail_class=DriftClass.X)` decorator
- **Tests:** `reconciler/tests/test_new_comparator.py`
- **Fixture data:** Add YAML to existing fixture or create new fixture in `reconciler/fixtures/`

**New Validator Rule (schema validation):**

- **Implementation:** `validators/registry/rules/new_rule.py` (or extend existing rule files)
- **Schema:** Add JSON schema to `schemas/registry/new_schema.json` if needed
- **Tests:** `validators/registry/tests/test_new_rule.py`

**New Registry Type (reference data):**

- **Files:** `registries/{category}/{item-id}.yaml` (one file per item)
- **Schema:** Define in `schemas/registry/{category}.v1.json`
- **Validator rule:** Add rule to `validators/registry/rules/` to validate against schema

**New Provisioning Operation:**

- **Implementation:** `tools/provision/new_operation.py`
- **CLI Integration:** Register in `tools/provision/cli.py`
- **Tests:** `tools/provision/tests/test_new_operation.py`

**New Record Type:**

- **Record files:** `records/{type}/{id}.json` (one file per record, timestamped)
- **Schema:** Define in `schemas/records/{type}.v1.json`
- **Capture logic:** Implement in `tools/records/ingest/` or `tools/records/dispatch/`

**New Event Type:**

- **Event files:** `events/YYYY-MM-DD/{event-id}.json` (one file per event, never edited)
- **Event schema:** Define enum in `contracts/records/event-type.enum.v1.yaml`
- **Capture logic:** Add dispatch rule to `tools/records/dispatch/`

**New Access Control Rule:**

- **Implementation:** YAML definition in `access/model/` or `access/invariants/`
- **Validation:** Add check to `access/tools/` (e.g., `check_*.py`)
- **Tests:** Integration test in `access/tests/`

**Utilities & Helpers:**

- **Shared helpers:** `scripts/phase0-lib/` (sourced by shell scripts)
- **Python utilities:** New module file in parent package with clear namespace
- **No standalone utils directory:** Keep utilities close to their consumers to prevent circular imports

## Special Directories

**contracts/fixtures/:**

- **Purpose:** Test scenarios for reconciler
- **Generated:** No, hand-authored
- **Committed:** Yes
- **Structure:** Each fixture is a directory with `declared/` (YAML), `actual.json` (snapshot), `canary.yaml` (seeded canary)
- **Never deleted:** Fixtures are named archives of test scenarios; removal is refactoring not to take lightly

**events/:**

- **Purpose:** Immutable, append-only event audit trail
- **Generated:** Yes (by tools/records dispatch)
- **Committed:** Yes (to control-plane-records repo, not main control-plane)
- **Structure:** One JSON file per event, partitioned by date (YYYY-MM-DD/)
- **Append-only rule:** Events are never edited or deleted. Corrections come as new "correction" or "reversal" events.

**reconciler/fixtures/:**

- **Purpose:** Test scenarios for comparator development
- **Generated:** No, hand-authored
- **Committed:** Yes
- **Structure:** Each fixture = one directory with declared state and actual state JSON
- **Usage:** Referenced by test code; one per unique scenario

**records/:**

- **Purpose:** Persistent audit trail for organizational decisions, incidents, deployments
- **Generated:** Yes (by tools/records ingest)
- **Committed:** Yes
- **Structure:** One JSON file per record, organized by type (people/, decisions/, incidents/, etc.)
- **Retention:** Never deleted; historical record

**gate-state/:**

- **Purpose:** CI gate status tracking and state cache
- **Generated:** Yes (by CI jobs)
- **Committed:** May be (for cache persistence)
- **Structure:** JSON files tracking gate passage, blocking findings, etc.

---

*Structure analysis: 2026-09-16*
