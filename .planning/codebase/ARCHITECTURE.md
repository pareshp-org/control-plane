---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
<!-- refreshed: 2026-09-16 -->

# Architecture

**Analysis Date:** 2026-09-16

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLI Entry Points & Orchestration                      │
│  reconciler/cli.py  validators/registry/cli.py  tools/provision/cli.py  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────────┐
│                         Reconciler Layer                                 │
│  `reconciler/` — Drift detection & comparison                            │
│  • Comparators (18+ modules in reconciler/comparators/)                  │
│  • Registry mechanism (reconciler/registry.py)                           │
│  • Model definitions (reconciler/model.py)                               │
│  • State adapters (reconciler/state/)                                    │
└──────────────────────────────┬──────────────────────────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│  Validators     │  │  Provisioning    │  │  Records & Events  │
│  validators/    │  │  tools/provision/│  │  tools/records/    │
│  • Registry     │  │  • GitHub Ops    │  │  • Audit Trail     │
│  • Drift        │  │  • Teams/Repos   │  │  • Metrics         │
│  • Attestation  │  │  • Permissions   │  │  • Event Capture   │
└────────┬────────┘  └────────┬─────────┘  └────────┬───────────┘
         │                    │                     │
└────────┴────────────────────┴─────────────────────┘
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  Access Layer    │     │  Contracts &     │
│  access/         │     │  Data Model      │
│  • Permissions   │     │  contracts/      │
│  • Access Model  │     │  registries/     │
│  • Secrets       │     │  schemas/        │
└──────────────────┘     │  records/        │
                         │  events/         │
                         └──────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **Reconciler CLI** | Phase-1 entry point: list comparators, run comparisons against fixtures/live | `reconciler/cli.py` |
| **Comparators** | Individual drift detectors (branch protection, environments, team membership, etc.) | `reconciler/comparators/*.py` |
| **Registry Validator** | Validate registry schemas against declared contracts | `validators/registry/cli.py` |
| **Drift Validators** | Standalone drift assertions (bypass, codeowners, protection, liveness) | `validators/drift/*.py` |
| **Provisioning CLI** | GitHub operations: create/update teams, repos, permissions, branch protection | `tools/provision/cli.py` |
| **Evidence Tools** | Collect and verify workflow evidence, apply production gates | `tools/evidence/*.py` |
| **Records Tools** | Capture events, manage audit trail, compute metrics | `tools/records/*.py` |
| **Access Layer** | Define permission matrix, team structure, access controls, secrets model | `access/` |
| **Contract Stubs** | Generated protocol buffers and fixtures for testing | `contracts/stubs/` |

## Pattern Overview

**Overall:** Drift Detection & Reconciliation

**Key Characteristics:**

- **Declarative-vs-Actual Comparison** — All comparators follow declare/actual pattern
- **Severity-based Response** — Four drift classes (GREEN, AMBER, RED, BLOCKING) drive action levels
- **Fail-closed on Errors** — Comparator execution failures classified by severity; BLOCKING comparators fail hard
- **Contract-first** — All components consume frozen contracts; no cross-lane imports except through contracts
- **Lane-isolated** — Five build lanes (L1-L5) with strict path ownership, no shared mutable state

## Layers

**Reconciliation Layer:**

- **Purpose:** Detect drift between declared state and actual state
- **Location:** `reconciler/`
- **Contains:** Comparators, state adapters, run orchestration, finding models
- **Depends on:** Contracts (`contracts/`), access model (`access/`), registries (`registries/`)
- **Used by:** CI/CD workflows, Phase-1 verification gates

**Validator Layer:**

- **Purpose:** Validate schemas and audit regulatory compliance
- **Location:** `validators/`
- **Contains:** Registry schema validation, drift assertion rules
- **Depends on:** Contracts, schemas (`schemas/`), records
- **Used by:** CI checks, audit workflows, L1 conformance tests

**Provisioning Layer:**

- **Purpose:** Implement declared state on GitHub (teams, repos, permissions)
- **Location:** `tools/provision/`
- **Contains:** GitHub API operations, checklist generation, plan optimization
- **Depends on:** Access model, registries, contracts
- **Used by:** Phase-0 setup, ongoing reconciliation, drift repair

**Evidence Layer:**

- **Purpose:** Collect and enforce compliance evidence
- **Location:** `tools/evidence/`
- **Contains:** Workflow evidence collection, canary checks, gate enforcement
- **Depends on:** Contracts, records, reconciler output
- **Used by:** CI/CD gates, quality assurance

**Records & Audit Layer:**

- **Purpose:** Maintain audit trail and compliance records
- **Location:** `tools/records/`, `records/`
- **Contains:** Event capture, metric computation, incident tracking
- **Depends on:** Schemas, registries
- **Used by:** Audit workflows, metrics systems, compliance reporting

**Access Control Layer:**

- **Purpose:** Define and enforce the organization's access model
- **Location:** `access/`
- **Contains:** Permission matrix, team definitions, secrets boundaries, fail-closed rules
- **Depends on:** Registries (people, roles, services)
- **Used by:** Provisioning, reconciliation, access validation

## Data Flow

### Primary Reconciliation Path (Phase-1)

1. **Discovery** — `reconciler/cli.py:list` enumerates all registered comparators (`reconciler/registry.py`) (file: `reconciler/cli.py:55-60`)
2. **Load Declared State** — `DeclaredState` loads fixture YAML: people, platform, products, templates (`reconciler/cli.py:70-102`)
3. **Load Actual State** — `FixtureState` or `LiveState` adapter fetches GitHub state (file: `reconciler/cli.py:200-250`)
4. **Run Comparators** — `reconciler/cli.py:run` invokes each registered comparator with (declared, actual, as_of) (file: `reconciler/cli.py:300+`)
5. **Classify Findings** — Each comparator returns `list[Finding]` with DriftClass; security floor applied if needed (file: `reconciler/model.py:69-78`)
6. **Generate Report** — `RunRecord` aggregates findings; canary validated (file: `reconciler/runrecord.py`)
7. **Exit Code** — 0 (success, no blocking findings), 2 (has blocking findings), 3 (instrument failure) (file: `reconciler/cli.py:100-120`)

### Provisioning & Repair Path (Phase-0 / Ongoing)

1. **Plan Generation** — `tools/provision/cli.py` reads access model and registries
2. **GitHub Sync** — Applies teams, repositories, branch protection, environment rules (file: `tools/provision/cli.py`)
3. **Verification** — Checklists and verify surfaces ensure completeness (file: `tools/provision/verify_surfaces.py`)
4. **Record Update** — Captures operation records for audit trail (file: `tools/records/`)

### Validation Path (L1 Registry Validation)

1. **Load Schemas** — `validators/registry/loader.py` reads schema definitions from `schemas/registry/`
2. **Load Records** — Read registry files from `registries/`
3. **Apply Rules** — `validators/registry/rules/registry.py` validates against schemas
4. **Report Output** — JSON format with pass/fail per registry

**State Management:**

- **Declared state:** Committed YAML/JSON in fixture directories and `declared/` subdirectories
- **Actual state:** Fetched from GitHub API (live mode) or loaded from fixture JSON (test mode)
- **Running state:** In-memory `DeclaredState` and `FixtureState`/`LiveState` objects
- **Output state:** `RunRecord` with findings, comparator counts, canary status

## Key Abstractions

**Comparator:**

- **Purpose:** Single drift comparison rule (e.g., "branch protection template matches actual")
- **Examples:** `reconciler/comparators/branch_protection.py`, `reconciler/comparators/environments.py`
- **Pattern:** Decorated function with signature `(declared, actual, as_of) -> (findings: list[Finding], compared: int)`
- **Registration:** `@comparator(id, fail_class=DriftClass.X)` decorator in `reconciler/registry.py`

**Finding:**

- **Purpose:** One drift detection result produced by a comparator
- **Examples:** `reconciler/model.py:52-66` (dataclass with id, comparator, scope, drift_class, level, evidence)
- **Pattern:** Immutable frozen dataclass; many findings per run aggregated in `RunRecord`

**DriftClass:**

- **Purpose:** Severity classification affecting response level and SLA
- **Values:** GREEN (no action), AMBER (next planning cycle), RED (2 business days), BLOCKING (immediate)
- **Examples:** `reconciler/model.py:16-22`
- **Pattern:** Enum; floored at RED for security/prod drift (file: `reconciler/model.py:69-78`)

**Level (Response Level):**

- **Purpose:** Action to take on drift finding
- **Values:** DETECT (log only), WARN (alert), AUTO_REPAIR (fix if safe), BLOCK (halt), ESCALATE (page)
- **Mapping:** DriftClass → Level via fail-mode matrix in spec 53.2 (reconciler lookup)

**State Adapter:**

- **Purpose:** Abstraction over state source (fixture JSON vs live GitHub API)
- **Examples:** `reconciler/state/fixture_adapter.py`, `reconciler/state/live_adapter.py`
- **Pattern:** Interface with methods to fetch platform, people, products, templates

**Fixture:**

- **Purpose:** Self-contained test scenario with declared and actual state
- **Location:** `reconciler/fixtures/` (one directory per fixture)
- **Structure:** `{declared/, actual.json, canary.yaml}`

**Registry:**

- **Purpose:** Authoritative reference data (people, roles, services, capabilities, etc.)
- **Location:** `registries/*/` directories (one file per item)
- **Schema:** Defined in `schemas/registry/` JSON schemas

**Contract:**

- **Purpose:** Frozen interface specification between components/lanes
- **Location:** `contracts/` (YAML and JSON schemas)
- **Rule:** Never modified after phase 0; lanes implement against it
- **Types:** drift-finding.v1.json, repair-record.v1.json, capability.vocabulary.v1.yaml, etc.

## Entry Points

**reconciler/cli.py:**

- **Location:** `reconciler/cli.py`
- **Commands:** `python -m reconciler list` | `python -m reconciler run`
- **Triggers:** CI gates (phase-1), manual verification, lane merge validation
- **Responsibilities:** Comparator discovery, state loading, orchestration, exit code generation

**validators/registry/cli.py:**

- **Location:** `validators/registry/cli.py`
- **Commands:** `python -m validators.registry.cli --root . --as-of YYYY-MM-DD --format json`
- **Triggers:** L1 validation gates, schema conformance checks
- **Responsibilities:** Schema loading, rule application, compliance reporting

**tools/provision/cli.py:**

- **Location:** `tools/provision/cli.py`
- **Commands:** `python tools/provision/cli.py plan | apply | verify`
- **Triggers:** Phase-0 bootstrap, ongoing drift repair (conditional)
- **Responsibilities:** GitHub operations, team/repo provisioning, protection rules

**Makefile targets:**

- **check:** Runs concordance (5-lane) + verify_handover
- **validate:** Runs L1 validator on registry
- **test:** Runs pytest on tests/ directory
- **phase0-dry:** Dry-run Phase-0 provisioning

## Architectural Constraints

- **Threading:** Single-threaded event loop per process. Comparators execute sequentially. GitHub API calls blocking.
- **Global state:** `reconciler/registry.py` holds `COMPARATORS` and `FAIL_CLASS` dicts populated at import time. No mutable shared state between lanes.
- **Circular imports:** Avoided by using contract-based composition. Validators consume contracts, not reconciler internals.
- **No cross-lane imports:** Lanes consume each other only through `contracts/` and published artifacts. Direct source imports between lanes forbidden by lane-guard CI check.
- **Contract freeze:** `contracts/**` immutable after phase 0. Lane change requests go through L0 (human review) only.
- **Additive-only within lane:** Lanes prefer new files over modifying existing ones to reduce merge conflicts.

## Anti-Patterns

### Shared Mutable Files

**What happens:** Multiple lanes append to a single shared list or index file (e.g., registry of everything)

**Why it's wrong:** Merge conflicts grow quadratically with lane count. PARTITION.md rule 3 forbids this.

**Do this instead:** Directory-per-item pattern. Each registry entry is one file in `registries/category/item-id.yaml`. Each event is one file in `events/YYYY-MM-DD/event-id.json`. Merges cannot conflict.

### Cross-Lane Source Imports

**What happens:** Lane 3 imports from reconciler internals; Lane 5 imports from Lane 3 directly (not through contracts)

**Why it's wrong:** Creates hidden coupling. Lane guard CI check fails such branches. Breaks the lane independence guarantee.

**Do this instead:** Compose through `contracts/`. If Lane 5 needs Lane 3's output, both lanes implement against the contract schema. Lane 5 reads Lane 3's output files (which conform to the contract), not its source.

### Design Within a Task

**What happens:** A lane task asks "should we use pattern X or Y?" or "which API is better?"

**Why it's wrong:** AI developers (Sonnet-class) are not empowered to judge architecture. Such decisions block the lane. PARTITION.md § "AI developer profile" forbids this.

**Do this instead:** Every task includes exact file paths, exact commands, literal copy-pasteable code, complete acceptance criteria, and a self-verify command. No "design" or "choose" steps in task instructions.

### Silent Errors in Comparators

**What happens:** A comparator catches an exception and returns an empty findings list

**Why it's wrong:** Breaks the "fail-closed" guarantee. Blocking comparators must fail hard on execution error to alert ops.

**Do this instead:** Let the exception propagate. The CLI orchestration wraps it with the comparator's declared fail-class. If fail-class is BLOCKING, the error becomes a Blocking finding.

## Error Handling

**Strategy:** Fail-closed for security-critical comparators, fail-open for advisory ones

**Patterns:**

- **Blocking Comparator Execution Failure:** Propagates as Blocking finding (spec 64.2)
- **AMBER/GREEN Comparator Execution Failure:** Logged as alert, non-blocking
- **Missing Fixture File:** Returns empty findings (no data ≠ drift); canary check will catch if critical
- **Invalid YAML/JSON:** Raises exception, treated per comparator fail-class
- **GitHub API Rate Limit:** Raises exception; caught by fail-closed envelope

## Cross-Cutting Concerns

**Logging:** Plain Python `logging` module; no structured logging framework. Output to stdout/stderr. CI captures and routes to logs.

**Validation:** Schema validation via `jsonschema` (Python). Registry schemas in `schemas/registry/*.json`. Contracts in `contracts/*.v1.json|yaml`. Validations run at load time and test time.

**Authentication:** GitHub Personal Access Token via `GITHUB_TOKEN` env var (never committed). Phase-0 provisioning requires token with `repo`, `admin:org_hook`, `admin:public_key` scopes.

---

*Architecture analysis: 2026-09-16*
