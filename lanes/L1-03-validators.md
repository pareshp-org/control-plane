# L1 — PHASE 3: THE VALIDATOR SUITE

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 Registries & Contracts (Subsystems **A** — control-plane repository, **B** — schema validation and CI gate engine; Spec §99.2).
**Branch prefix:** `lane/1/*` — this phase uses `lane/1/03-*`.
**Merge position:** L1 merges FIRST in the train (`L1 → L4 → L2 → L3 → L5`, PARTITION.md).
**Paths this phase may write (all owned by L1):**

| Path | Used by this phase for |
|---|---|
| `validators/registry/**` | all rule code, the CLI, fixtures, tests, the rule manifest |
| `schemas/registry/**` | read-only in this phase, except where a task states otherwise |
| `schemas/product/**` | read-only in this phase |
| `registries/**` | read-only in this phase, except T11 and T15 which create the files L0 designates |

**Paths this phase must NEVER touch** (lane-guard CI will fail the PR): `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` (L2); `reconciler/**`, `tools/provision/**`, `validators/drift/**` (L3); `schemas/records/**`, `metrics/**`, `tools/records/**`, anything in `control-plane-records` (L4); `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` (L5); `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (L0).

**Explicitly out of scope for this phase — do not implement, do not stub:**

* "A reviewer set that does not match GitHub Team membership" (§15.5). This compares **declared state against actual GitHub state** and is therefore Subsystem C, lane L3 (`validators/drift/**`). If you find yourself calling the GitHub API, stop: you are in the wrong lane.
* Automatic expiry **revocation** (§54.2, §10.1). Detection of an expired object is this phase (R05, R09). Revoking it is the reconciler, L3.
* Wiring any rule into a GitHub Actions workflow. This phase ships a CLI; **L2 calls it.** See the Integration Contract below.

---

## 0. Integration contract — what this phase hands to the other lanes

L1 Phase 3 publishes exactly one machine surface. Nothing else in the repo may be assumed to be a public entry point.

```
python -m validators.registry.cli --root <control-plane-root> [--as-of YYYY-MM-DD] [--records-root <path>] [--format json|text] [--rule Rxx ...]
```

| Exit code | Meaning | Consumer behaviour |
|---|---|---|
| `0` | No findings. | CI gate passes. |
| `1` | One or more findings emitted. | CI gate **fails the build** (§15.5). |
| `2` | Usage error, unreadable root, missing schema, or an internal exception. | CI gate **fails the build**. Never treat `2` as a pass — §64.2 classifies validation fail-closed. |

Findings are emitted as a JSON array on stdout under `--format json`. The envelope is frozen at T01 and must not change after T01 merges:

```json
[{"rule":"R07","code":"R07.1","severity":"blocking","file":"products/product-1/product.yaml","pointer":"/operations/coverage_window","message":"coverage_window has 120 uncovered minutes; no active rota member accepts sun 02:00-04:00 Asia/Kolkata","spec":"§15.6, §47.9, D112"}]
```

---

## 1. DECISION REQUIRED — L0 must answer before T00 can pass

Four questions in this phase cannot be answered from the specification. They are **not** for the executing developer. L0 answers them by writing `contracts/decisions/L1-03.yaml` (an L0-owned path — PARTITION.md rule 2). T00 reads that file and fails closed if it is absent or incomplete.

| Key | Question | Why the spec does not answer it | Proposed default L0 may stamp |
|---|---|---|---|
| `validator_runtime` | Which language and dependency set do the rules ship in? | §99.5 fixes GitHub, Actions, Grafana, DevLake and Prometheus. It fixes nothing about the validator implementation; §20.2 says only "scripts over the YAML files". | `python==3.12` with `jsonschema==4.23.0` (Draft 2020-12), `PyYAML==6.0.2`, `pytest==8.3.2`, `ruff==0.6.9`. |
| `control_classification_home` | Which control-plane file carries the fail-closed / fail-open classification of every control (§64.2, invariant 80)? | §52.6 freezes the control-plane inventory at thirty artifacts and forbids a new one where an existing file can hold the content. §64.2 names no file. | `registries/policies.yaml`, extended with a required `failure_mode:` field per entry (`fail-closed` \| `fail-open` \| `graded`), since §52.6 already assigns `policies.yaml` the "policy register and lifecycle state" role and gives each entry an owner and review date. |
| `framework_registry_path` | Where does the Performance Framework Registry (§77.1) live in the repo? | §52.6 lists "Performance framework registry" as an artifact with no filename. §77 gives its fields, not its path. | `registries/performance-framework/v*.yaml`, one file per framework version, plus `registries/performance-framework/index.yaml`. |
| `records_snapshot_mode` | How does a control-plane CI run read `records/restore-tests/` to check that a `restore_tested` date is **derived, not declared** (§44.2)? Those records live in the **records repository** (§52.6, D89), which L1 does not own. | The spec asserts the check; it does not state the cross-repository read mechanism. | `optional-path`: the CLI accepts `--records-root`; when it is absent R06 emits `R06.3 severity=info skipped-no-records-root` and checks age only. L2 supplies the path in CI. |

**Executor rule:** if `contracts/decisions/L1-03.yaml` does not exist, or any of the four keys is missing or set to `null`, **do not proceed past T00.** File the blocker in §3 with `component: L0-decision` and stop. Do not choose a default yourself.

---

## 2. Rule inventory — every "fails CI" / "CI rejects" / "blocking" claim this phase implements

Each row is one task. Each task ships one rule module, one fixture family and one test module.

| Rule | Task | Name | Spec source (verbatim locations) | Severity |
|---|---|---|---|---|
| R01 | T02 | Multi-version schema validation & supported-version floor | §60.1 `supported_contract_versions`; §60.2 "Validator supports BOTH v1 and v2"; §60.3 `unsupported` → deployment blocked; §15.5 "A `contract_version` the current platform version does not support"; invariant 73 | blocking |
| R02 | T03 | Assignments name an existing, non-`departed` person | §15.5 "An assignment referencing a person who does not exist or is `departed`"; §99.2 row B; §7.1 "Departure is a state, not a deletion" | blocking |
| R03 | T04 | Declared dependency names an existing shared service | §20.1 "A product cannot declare a dependency on a shared service that does not exist in the registry. CI enforces this"; §15.5; §99.2 row B; invariant 64 | blocking |
| R04 | T05 | Mandatory `end_date` for every non-employee | §7.1 "`end_date` is mandatory for every non-employee. A CI check fails if a contractor, intern, temporary specialist or consultant has a null end date"; §64.1 "Non-employees: `end_date` mandatory" | blocking |
| R05 | T06 | Expired assignment | §15.5 "An assignment whose `end_date` has passed"; §10.1 expiry column; invariant 58 | blocking |
| R06 | T07 | `restore_tested` within the applicable rolling window | §15.4; §44.2 "CI validates that computed date against the product's applicable window"; §44.3 "Stale restore test … Automated, blocks CI"; invariant 4 | blocking |
| R07 | T08 | The 24x7 / extended coverage blocker | §15.6 "This is an onboarding blocker, not a warning"; §47.9 "A missing `coverage_window`, an uncovered hour, an unnamed paging path, or a rota member who is not active fails validation"; §7.3 coverage-check bullet; **D112** (gives the validator its input); invariant 31 | blocking |
| R08 | T09 | `commitments` entry without a recorded `conflict_check` | §21.4 "`conflict_check: passed` or `waived-with-decision` is recorded in the entry; CI fails a commitments entry with neither"; §15.5 | blocking |
| R09 | T10 | Exception without an expiry | §54.2 "Expiry is mandatory. CI rejects any exception without one"; invariant 77 | blocking |
| R10 | T11 | Unclassified control | §64.2 "Every control is explicitly classified. Unclassified controls fail CI"; invariant 80 | blocking |
| R11 | T12 | Capability defined before it is granted | §9.1 "A capability appearing in a `roles.yaml` default, in a `people.yaml` grant, or in any assignment type without a row in this table fails control-plane CI validation"; **D90**; invariant 11 | blocking |
| R12 | T13 | No dangerous capability in a role default | §8 "Control-plane CI rejects a `roles.yaml` default containing any of them"; **D106**; invariant 79 | blocking |
| R13 | T14 | RPO must be satisfiable by the declared backup frequency | §44.1 "CI validation rejects a declaration whose RPO the declared backup frequency cannot meet"; §15.1 `recovery:` block | blocking |
| R14 | T15 | Revision integrity audit | §77.5 "runs as part of CI on the control-plane repository whenever these files change … blocks the change until every removal carries an intentional-change marker referencing a decision record" | blocking |
| R15 | T16 | Illegal `availability` / `access_status` pairing | §7.1 "CI validates the combination and rejects the rest" | blocking |
| R16 | T17 | `detection_expectation` differs from its derived value | §42.2 "CI fails a contract whose declared value differs from the value its `support_model` implies"; §15.1 `# DERIVED` | blocking |
| R17 | T18 | `founder_decision_delegate` naming a formal people decision | §10.1 "A delegation naming one of them fails schema validation (**D108**)"; §14.2; §74.5 | blocking |
| R18 | T19 | `recovery:` block with no `restore-production.yml` | §15.5 "A product with a `recovery:` block and no `restore-production.yml` workflow"; §44.5 "fails contract validation (15.5)" | blocking |

R15–R18 are the completion of the sweep the phase brief asks for: each is an explicit "fails CI" assertion in the spec, each lives in an L1-owned path, and none requires actual-platform state.

---

## 3. Blocker-issue template — file this instead of improvising

Every STOP rule in this document routes here. Copy verbatim, fill the angle-bracket fields, file, then stop working on that task and move to the next task whose dependencies are met.

```bash
set -euo pipefail
cd "$CP"
gh issue create \
  --title "BLOCKER L1-03-<TASK_ID>: <one-line symptom>" \
  --label blocker,lane-1,phase-3 \
  --body "$(cat <<'EOF'
lane: L1
phase: 3
task: <TASK_ID>
component: <L0-decision | L1-phase-1 | L1-phase-2 | schema | fixture | other>
stop_rule_triggered: <quote the STOP rule text from L1-03-validators.md>

what I ran:
```
<the exact command>
```

what I expected:
<the expected output from the task's SELF-VERIFY block>

what I got:
```
<verbatim output, including exit code>
```

what I did NOT do:
- I did not choose a default, invent a schema field, or edit a path outside validators/registry/**, schemas/**, registries/**.
- I did not proceed to dependent tasks.

decision needed from: <L0 | lane L1 phase 2 owner>
EOF
)"
```

---

## 4. Conventions every task obeys

**Repository root.** Every command block assumes:

```bash
set -euo pipefail
export CP="$HOME/work/control-plane"   # the control-plane repository working copy
cd "$CP"
```

If `$CP` does not exist, clone it once — nothing else in this phase clones:

```bash
set -euo pipefail
git clone git@github.com:<org>/control-plane.git "$CP"
cd "$CP"
```

**Branch, commit and PR, run once per task.** Substitute `<TASK_ID>` and `<slug>` from the task heading.

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b "lane/1/03-<slug>"
```

and at the end of the task:

```bash
set -euo pipefail
cd "$CP"
git add validators/registry schemas registries
git status --porcelain            # inspect: nothing outside the three trees above may appear
git commit -m "$(cat <<'EOF'
L1-03-<TASK_ID>: <rule id> <short rule name>

Implements <spec citations> as a blocking control-plane CI rule.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push -u origin "lane/1/03-<slug>"
gh pr create --base integration \
  --title "L1-03-<TASK_ID>: <rule id> <short rule name>" \
  --body "Lane L1, Phase 3. Rule <rule id>. Spec: <citations>. Fixtures: validators/registry/fixtures/<rid>/. Self-verify in L1-03-validators.md."
```

**No task rebases, merges or touches another lane's branch** (PARTITION.md, branch & merge model).

**Determinism.** No rule may call `datetime.now()` directly. Every date-sensitive rule reads `ctx.today`, which the CLI sets from `--as-of` and defaults to the system date only when the flag is absent. Every fixture test passes `--as-of` explicitly. A rule that reads the wall clock is a defect.

**One rule, one module, one fixture family, one test module.**

```
validators/registry/rules/r07_coverage_rota.py         # the rule
validators/registry/fixtures/r07/pass/                 # a full valid control-plane tree
validators/registry/fixtures/r07/fail-<case>/          # baseline + the single delta under test
validators/registry/fixtures/r07/<case>/expected.json  # the exact finding codes expected
validators/registry/tests/test_r07_coverage_rota.py    # runs the CLI over each fixture dir
```

**Rule module contract**, frozen at T01:

```python
RULE_ID: str          # "R07"
SPEC_REFS: list[str]  # ["§15.6", "§47.9", "D112"] — never empty, never invented
SEVERITY: str         # "blocking"
def check(ctx: Context) -> list[Finding]: ...
```

---

## TASK L1-03-00 — Preflight: decisions, toolchain and Phase 1/2 artifacts

**Size:** S **Depends on:** L1 Phase 1 and Phase 2 merged to `integration`; `contracts/decisions/L1-03.yaml` written by L0.
**Creates/edits:** nothing. This task is read-only.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration

# 1. L0 decisions present and complete
test -f contracts/decisions/L1-03.yaml && echo "DECISIONS_FILE_OK" || echo "DECISIONS_FILE_MISSING"
python - <<'EOF'
import sys, pathlib
try:
    import yaml
except ImportError:
    print("PREFLIGHT_FAIL pyyaml-missing"); sys.exit(2)
p = pathlib.Path("contracts/decisions/L1-03.yaml")
if not p.exists():
    print("PREFLIGHT_FAIL decisions-missing"); sys.exit(2)
d = yaml.safe_load(p.read_text()) or {}
required = ["validator_runtime","control_classification_home","framework_registry_path","records_snapshot_mode"]
missing = [k for k in required if d.get(k) in (None, "", "TBD")]
print("PREFLIGHT_FAIL missing-keys=" + ",".join(missing)) if missing else print("PREFLIGHT_OK decisions")
sys.exit(1 if missing else 0)
EOF

# 2. Phase 2 schema artifacts present
ls -1 schemas/registry/ schemas/product/
test -f schemas/registry/capability.enum.schema.json && echo "CAP_ENUM_OK" || echo "CAP_ENUM_MISSING"

# 3. Toolchain
python --version
python -c "import jsonschema, ruamel.yaml, pytest; print('DEPS_OK')"
ruff --version
gh auth status
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | the inline `python - <<EOF` block | prints `PREFLIGHT_OK decisions`, exit code `0` |
| 2 | `test -f schemas/registry/capability.enum.schema.json` | prints `CAP_ENUM_OK` |
| 3 | `ls -1 schemas/product/` | lists at least `product.v1.schema.json` and `product.v2.schema.json` (§60.2 requires both versions to exist side by side) |
| 4 | `python -c "import jsonschema, ruamel.yaml, pytest; print('DEPS_OK')"` | prints `DEPS_OK`, exit code `0` |
| 5 | `python --version` | matches the `validator_runtime` value stamped by L0 |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  test -f contracts/decisions/L1-03.yaml
  test -f schemas/registry/capability.enum.schema.json
  test -f schemas/product/product.v1.schema.json
  test -f schemas/product/product.v2.schema.json
  python -c "import jsonschema, ruamel.yaml, pytest"
  echo T00_PASS
'
```

Correct output: the single line `T00_PASS` and exit code `0`. Any other output means preflight failed.

**STOP rule.** If any of the five criteria fails, do **not** create a branch and do **not** start T01. File the blocker with `component: L0-decision` (criterion 1), `component: L1-phase-2` (criteria 2–3) or `component: other` (criteria 4–5). Do not install missing schema files yourself: `schemas/**` content is Phase 2's deliverable and re-creating it here produces a duplicate that will conflict at merge.

---

## TASK L1-03-01 — The rule harness, the CLI, the baseline fixture and the fixture generator

**Size:** L **Depends on:** T00. **Slug:** `harness`
**Creates:**
`validators/registry/__init__.py`, `validators/registry/model.py`, `validators/registry/context.py`, `validators/registry/loader.py`, `validators/registry/registry.py`, `validators/registry/cli.py`, `validators/registry/rules/__init__.py`, `validators/registry/rules_manifest.yaml`, `validators/registry/tools/make-fixture.sh`, `validators/registry/tests/conftest.py`, `validators/registry/tests/test_harness.py`, `validators/registry/fixtures/_baseline/**`, `validators/registry/pyproject.toml`, `validators/registry/README.md`.

This is the keystone task. Every later task is a thin addition on top of it.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-harness
mkdir -p validators/registry/{rules,tests,tools,fixtures/_baseline}
```

**Step 1 — the data model.** `validators/registry/model.py`:

```bash
set -euo pipefail
cat > validators/registry/model.py <<'EOF'
from dataclasses import dataclass, asdict
from typing import Literal

Severity = Literal["blocking", "warning", "info"]

@dataclass(frozen=True)
class Finding:
    rule: str      # "R07"
    code: str      # "R07.1"
    severity: Severity
    file: str      # repo-relative path
    pointer: str   # RFC 6901 JSON pointer into the document
    message: str
    spec: str      # "§15.6, §47.9, D112"

    def as_dict(self) -> dict:
        return asdict(self)
EOF
```

**Step 2 — the context and loader.** `context.py` exposes `root: Path`, `today: date`, `records_root: Path | None`, and cached parsed documents; `loader.py` reads YAML with `ruamel.yaml` in round-trip-off, safe mode and returns `(doc, path)` pairs for: `registries/people.yaml`, `registries/roles.yaml`, `registries/platform.yaml`, `registries/exceptions.yaml`, every `products/*/product.yaml`, every `shared-services/*/service.yaml`.

```bash
set -euo pipefail
cat > validators/registry/context.py <<'EOF'
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

@dataclass
class Doc:
    path: str          # repo-relative
    data: Any

@dataclass
class Context:
    root: Path
    today: date
    records_root: Path | None = None
    _cache: dict = field(default_factory=dict)

    def load(self, key: str):
        from .loader import load_key
        if key not in self._cache:
            self._cache[key] = load_key(self, key)
        return self._cache[key]
EOF
```

`loader.py` must define exactly these keys and no others: `people`, `roles`, `platform`, `exceptions`, `policies`, `products`, `services`, `framework`. `products` and `services` return `list[Doc]`; the rest return `Doc | None`. A YAML parse error is not a rule finding — it raises and the CLI exits `2` (fail-closed, §64.2).

**Step 3 — the rule registry.** `registry.py` discovers every module in `validators/registry/rules/` whose name matches `r\d\d_.*\.py`, imports it, asserts the module contract (`RULE_ID`, `SPEC_REFS` non-empty, `SEVERITY`, callable `check`), and returns them sorted by `RULE_ID`. A module failing the contract raises — CLI exit `2`.

**Step 4 — the CLI.** `cli.py` implements exactly the Integration Contract in §0: flags `--root` (required), `--as-of` (ISO date), `--records-root`, `--format json|text` (default `text`), `--rule` (repeatable, filters to those rule ids). Exit `0` with zero findings, `1` with one or more, `2` on any exception or usage error. JSON output is `json.dumps(sorted(findings, key=...), indent=None)` sorted by `(file, rule, code, pointer)` so output is byte-stable.

**Step 5 — the rule manifest.** `rules_manifest.yaml` is the machine-checkable inventory; every later task appends its own row and T20 asserts the manifest and the filesystem agree.

```bash
set -euo pipefail
cat > validators/registry/rules_manifest.yaml <<'EOF'
manifest_version: 1
rules: []
EOF
```

**Step 6 — the baseline fixture.** `validators/registry/fixtures/_baseline/` is a complete, **valid** minimal control plane that every rule must pass cleanly. Every failing fixture in every later task is this tree plus exactly one delta.

```bash
set -euo pipefail
mkdir -p validators/registry/fixtures/_baseline/{registries,products/product-1,shared-services/auth-service}

cat > validators/registry/fixtures/_baseline/registries/platform.yaml <<'EOF'
platform_version: 4.0
supported_contract_versions:
  product: [1, 2]
  verification: [1]
  people_registry: [1]
  service: [1]
reusable_workflow_versions:
  current: v4
  supported: [v3, v4]
  deprecated: [v2]
  deprecation_deadline:
    v2: 2026-08-01
    v3: 2026-12-01
canary_set: [product-1]
EOF

cat > validators/registry/fixtures/_baseline/registries/roles.yaml <<'EOF'
registry_version: 1
roles:
  - id: founder
    default_capabilities: [strategy, budget, hiring, customer-commitment]
  - id: team_lead
    default_capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change]
  - id: developer
    default_capabilities: [code-review]
  - id: qa
    default_capabilities: [verification, uat, release-signoff]
  - id: contractor
    default_capabilities: []
EOF

cat > validators/registry/fixtures/_baseline/registries/people.yaml <<'EOF'
registry_version: 1
people:
  - id: dev-a
    display_name: "Example Developer A"
    github_login: exampledev-a
    role: developer
    employment_type: employee
    capabilities: [backend, code-review]
    ai_runtime: claude-code
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: hybrid
      schedule:
        mon: { start: "09:30", end: "18:30" }
        tue: { start: "09:30", end: "18:30" }
        wed: { start: "09:30", end: "18:30" }
        thu: { start: "09:30", end: "18:30" }
        fri: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-03-01
    end_date: null
  - id: dev-b
    display_name: "Example Developer B"
    github_login: exampledev-b
    role: developer
    employment_type: employee
    capabilities: [backend, code-review]
    ai_runtime: claude-code
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: remote
      schedule:
        mon: { start: "09:30", end: "18:30" }
        tue: { start: "09:30", end: "18:30" }
        wed: { start: "09:30", end: "18:30" }
        thu: { start: "09:30", end: "18:30" }
        fri: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-03-01
    end_date: null
rotas: []
EOF

cat > validators/registry/fixtures/_baseline/registries/exceptions.yaml <<'EOF'
registry_version: 1
exceptions: []
EOF

cat > validators/registry/fixtures/_baseline/shared-services/auth-service/service.yaml <<'EOF'
service_version: 1
identity:
  id: auth-service
  repository: org/auth-service
  type: internal-api
assignments:
  - person: dev-b
    type: primary_owner
  - person: dev-a
    type: cross_reviewer
  - person: dev-a
    type: backup_owner
escalation: team_lead
consumers: [product-1]
compatibility:
  versioning: semver
  supported_versions: ["4.x"]
  deprecation_notice_days: 90
  breaking_change_policy: major-version-with-migration-guide
verification:
  automated: required
  consumer_contract_tests: required
  smoke_tests: required
operations:
  primary_responder: dev-b
  backup_responder: dev-a
  incident_severity_inheritance: highest-consumer
EOF

cat > validators/registry/fixtures/_baseline/products/product-1/product.yaml <<'EOF'
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  id: product-1
  display_name: "Alpha"
  lifecycle: active
  launch_status: launched
  created: 2025-01-15
classification:
  class: commercial
  reliability_criticality: high
  domain: core-platform
assignments:
  - person: dev-a
    type: primary_owner
    start_date: 2025-06-01
    end_date: null
  - person: dev-b
    type: cross_reviewer
    start_date: 2025-06-01
    end_date: null
  - person: dev-b
    type: backup_owner
    start_date: 2025-06-01
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-1-api
      role: primary
      deploys: true
  default_branch: main
  gsd_version: v4.0.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: required
  smoke_tests: required
  performance: optional
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.alpha.internal
  production: https://alpha.example.com
deployment:
  build: docker
  artifact_type: container-image
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: redeploy-previous-tag
  progressive_delivery: none
reversibility_default: fully-reversible
infrastructure:
  runtime: Node.js 22
  database: PostgreSQL 16
  cache: Redis 7
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 450
    ceiling: 600
dependencies:
  internal: [auth-service]
  external: [stripe]
  infrastructure: [postgres-provider]
security:
  secrets_location: AWS Secrets Manager
  scorecard_minimum: 7
  production_db_access: via-bastion-only
data:
  classification: customer-data
  retention_days: 2555
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: true
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors: [stripe.com]
observability:
  health_endpoint: /health
  version_endpoint: /version
  metrics: Prometheus /metrics
  telemetry_exposure: private-authenticated
  alert_channel: "#alerts-product-1"
recovery:
  backup_frequency: daily
  point_in_time_recovery:
    enabled: false
    window_minutes: null
  backup_retention_days: 30
  encrypted: true
  storage_location: independent-provider-bucket-eu
  restore_procedure: docs/restore.md
  restore_environment: throwaway-vm
  integrity_check: row-counts-plus-checksum
  restore_tested: 2026-08-14
  rpo_minutes: 1440
  rto_minutes: 240
operations:
  support_model: business-hours
  coverage_window: null
  detection_expectation: next-business-morning
  intake_channel: support@example.com
  triager: primary_owner
  weekend_exception_eligible: true
  critical_incident_response: next-business-day
commitments:
  - sla: "99.5% monthly uptime"
    scope: paying-customers
    conflict_check: waived-with-decision
business:
  criticality: high
  active_customers: 42
  revenue_importance: high
EOF

mkdir -p validators/registry/fixtures/_baseline/products/product-1/.github/workflows
: > validators/registry/fixtures/_baseline/products/product-1/.github/workflows/restore-production.yml
```

> Note on the last two lines: this path is **inside a fixture directory**, not inside the control-plane repo's own `.github/`. Creating `validators/registry/fixtures/**/.github/workflows/restore-production.yml` is in-lane; creating `.github/workflows/anything` at the repo root is **not** and will fail lane-guard. R18 (T19) needs the presence of this file to have something to detect.

**Step 7 — the fixture generator.**

```bash
set -euo pipefail
cat > validators/registry/tools/make-fixture.sh <<'EOF'
#!/usr/bin/env bash
# usage: make-fixture.sh <rule-id-lower> <case-name>
# copies the baseline control plane into fixtures/<rule>/<case>/ and seeds expected.json
set -euo pipefail
RULE="$1"; CASE="$2"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/fixtures/$RULE/$CASE"
if [ -e "$DEST" ]; then echo "FIXTURE_EXISTS $DEST" >&2; exit 3; fi
mkdir -p "$(dirname "$DEST")"
cp -r "$HERE/fixtures/_baseline" "$DEST"
printf '{"as_of":"2026-08-27","expect":[]}\n' > "$DEST/expected.json"
echo "FIXTURE_CREATED $DEST"
EOF
chmod +x validators/registry/tools/make-fixture.sh
```

**Step 8 — the shared test driver.** `tests/conftest.py` exposes a `run_cli(fixture_dir, rule=None)` helper that shells out to `python -m validators.registry.cli --root <fixture_dir> --as-of <expected.json:as_of> --format json`, returns `(exit_code, findings)`, and a `assert_expected(fixture_dir)` helper that asserts `sorted(codes) == sorted(expected["expect"])` **exactly** — no subset matching. `tests/test_harness.py` asserts: the baseline fixture produces zero findings and exit `0`; an unreadable root produces exit `2`; `--rule R99` (unknown) produces exit `2`.

**Commands to finish**

```bash
set -euo pipefail
cd "$CP"
ruff check validators/registry
python -m pytest validators/registry/tests -q
python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json; echo "EXIT=$?"
git add validators/registry
git status --porcelain
git commit -m "$(cat <<'EOF'
L1-03-01: validator harness, CLI, baseline fixture

Frozen finding envelope and exit-code contract (0 clean / 1 findings / 2 fail-closed),
rule-module contract, rule manifest and the baseline control-plane fixture every
later rule fixture derives from.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push -u origin lane/1/03-harness
gh pr create --base integration --title "L1-03-01: validator harness, CLI, baseline fixture" --body "Lane L1 Phase 3 keystone. Integration contract per L1-03-validators.md §0."
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json` | stdout exactly `[]`, `EXIT=0` |
| 2 | `python -m validators.registry.cli --root /nonexistent --format json; echo $?` | `2` |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --rule R99; echo $?` | `2` |
| 4 | `python -m pytest validators/registry/tests -q` | ends `3 passed`, exit `0` |
| 5 | `ruff check validators/registry` | prints `All checks passed!`, exit `0` |
| 6 | `bash validators/registry/tools/make-fixture.sh r00 smoke && rm -rf validators/registry/fixtures/r00` | prints a line starting `FIXTURE_CREATED` |
| 7 | `git status --porcelain \| grep -vE '^\?\? ?validators/registry|^A. ?validators/registry' \| wc -l` | `0` — nothing outside `validators/registry/` is staged |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  out=$(python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json)
  test "$out" = "[]"
  python -m validators.registry.cli --root /nonexistent --format json >/dev/null 2>&1; test $? -eq 2
  python -m pytest validators/registry/tests -q >/dev/null
  ruff check validators/registry >/dev/null
  echo T01_PASS
'
```

Correct output: the single line `T01_PASS`, exit `0`.

**STOP rule.** If the baseline fixture cannot be made to produce `[]` **because a Phase 2 schema rejects a field the spec's own §15.1 example contains**, do not edit the schema and do not edit the spec example out of the fixture. File the blocker with `component: L1-phase-2`, quoting the schema path, the rejected pointer, and the §15.1 line the field comes from.

---

## TASK L1-03-02 — R01 multi-version schema validation and the supported-version floor

**Size:** L **Depends on:** T01. **Slug:** `r01-schema-versions`
**Creates:** `validators/registry/schema_index.py`, `validators/registry/rules/r01_schema_version.py`, `validators/registry/fixtures/r01/**`, `validators/registry/tests/test_r01_schema_version.py`. **Edits:** `validators/registry/rules_manifest.yaml`.

**What the rule does, exactly.** For each document kind in the §60.2 table that this lane owns — `product.yaml`/`contract_version`, `verification/contract.yaml`/`contract_version`, `people.yaml`/`registry_version`, `roles.yaml`/`registry_version`, `service.yaml`/`service_version`:

1. Read the declared version integer. Missing or non-integer → `R01.1`.
2. Resolve `schemas/<family>/<kind>.v<N>.schema.json` via `schema_index.py`. No such schema file → `R01.2` (the validator does not "support BOTH v1 and v2" if a supported version has no schema — §60.2).
3. Validate the document against that exact schema with `jsonschema` Draft 2020-12. Each schema error → one `R01.3` finding, `pointer` = the error's JSON pointer.
4. Compare the declared version against `registries/platform.yaml → supported_contract_versions.<kind>`. Not in the list → `R01.4`, message `"contract_version <N> is unsupported; supported: <list> (§60.3 deployment blocked)"`.
5. A version **present in `supported_contract_versions` but not equal to its maximum** is `transitional` (§60.3) and requires `platform_migration` with a non-null `owner`, `target_contract_version` and `deadline`. Missing any → `R01.5`. A `deadline` earlier than `ctx.today` → `R01.6`.

`R01.4`, `R01.5`, `R01.6` are `blocking`. Nothing here is a warning: §60.3 says deployment blocked and invariant 74 makes the transitional fields mandatory.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r01-schema-versions

for c in pass fail-missing-version fail-no-schema-for-version fail-schema-error fail-unsupported-version fail-transitional-no-owner fail-transitional-past-deadline; do
  bash validators/registry/tools/make-fixture.sh r01 "$c"
done

# fail-missing-version: delete the version field
python - <<'EOF'
import pathlib, re
p = pathlib.Path("validators/registry/fixtures/r01/fail-missing-version/products/product-1/product.yaml")
p.write_text("\n".join(l for l in p.read_text().splitlines() if not l.startswith("contract_version:")) + "\n")
q = pathlib.Path("validators/registry/fixtures/r01/fail-missing-version/expected.json")
q.write_text('{"as_of":"2026-08-27","expect":["R01.1"]}\n')
EOF

# fail-unsupported-version: declare a version the platform does not support
sed -i 's/^contract_version: 2$/contract_version: 9/' \
  validators/registry/fixtures/r01/fail-unsupported-version/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R01.2","R01.4"]}\n' \
  > validators/registry/fixtures/r01/fail-unsupported-version/expected.json

# fail-transitional-no-owner: legal older supported version, no migration block
sed -i 's/^contract_version: 2$/contract_version: 1/' \
  validators/registry/fixtures/r01/fail-transitional-no-owner/products/product-1/product.yaml
sed -i 's/^platform_compatibility: supported$/platform_compatibility: transitional/' \
  validators/registry/fixtures/r01/fail-transitional-no-owner/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R01.5"]}\n' \
  > validators/registry/fixtures/r01/fail-transitional-no-owner/expected.json
```

Fill `fail-no-schema-for-version` by pointing `supported_contract_versions.product` at `[1, 2, 3]` in that fixture's `platform.yaml` while no `product.v3.schema.json` exists (`expect: ["R01.2"]` on the platform file). Fill `fail-schema-error` by setting `identity.lifecycle: retired` (not in the §15.1 enum `active | maintenance | paused | sunset | archived`), `expect: ["R01.3"]`. Fill `fail-transitional-past-deadline` from the previous fixture plus a `platform_migration` block whose `deadline: 2026-01-01` with `as_of` `2026-08-27`, `expect: ["R01.6"]`.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r01_schema_version.py -q` | `7 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r01/pass --as-of 2026-08-27 --format json` | `[]`, exit `0` |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r01/fail-unsupported-version --as-of 2026-08-27 --format json \| python -c "import sys,json;print(sorted({f['code'] for f in json.load(sys.stdin)}))"` | `['R01.2', 'R01.4']` |
| 4 | `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json` | still `[]` — R01 must not regress the baseline |
| 5 | `grep -c 'R01' validators/registry/rules_manifest.yaml` | `1` or more |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r01_schema_version.py -q >/dev/null
  test "$(python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json)" = "[]"
  echo T02_PASS
'
```

**STOP rule.** If `schemas/product/product.v1.schema.json` and `product.v2.schema.json` are not both present, R01 cannot demonstrate §60.2's "Validator supports BOTH v1 and v2". Do **not** author the missing schema — `schemas/product/**` content is Phase 2's deliverable and duplicating it guarantees a merge conflict inside your own lane. File the blocker with `component: L1-phase-2`.

---

## TASK L1-03-03 — R02 assignments name an existing, non-departed person

**Size:** M **Depends on:** T01. **Slug:** `r02-assignment-refs`
**Creates:** `validators/registry/rules/r02_assignment_person_ref.py`, `validators/registry/fixtures/r02/**`, `validators/registry/tests/test_r02_assignment_person_ref.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly.** Build the set of `people[].id` from `registries/people.yaml` and the map `id → availability`. For every `assignments[]` entry in every `products/*/product.yaml` **and** every `shared-services/*/service.yaml`, and for every `topology.yaml` succession designation naming a person:

* `person` not in the id set → `R02.1` — `"assignment references unknown person '<id>' (§15.5)"`.
* `person` present with `availability: departed` → `R02.2` — `"assignment references departed person '<id>'; departure is a state, not a deletion (§7.1) and the assignment must be ended, not the record removed (§15.5)"`.
* `person` present with `access_status: revoked` while the assignment `end_date` is `null` → `R02.3`.
* Duplicate `(person, type)` pairs with overlapping date ranges on one document → `R02.4`.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r02-assignment-refs
for c in pass fail-unknown-person fail-departed-person fail-revoked-open-assignment fail-overlapping-duplicate; do
  bash validators/registry/tools/make-fixture.sh r02 "$c"
done

sed -i 's/^    person: dev-a$/    person: dev-ghost/' \
  validators/registry/fixtures/r02/fail-unknown-person/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R02.1"]}\n' \
  > validators/registry/fixtures/r02/fail-unknown-person/expected.json

python - <<'EOF'
import pathlib
p = pathlib.Path("validators/registry/fixtures/r02/fail-departed-person/registries/people.yaml")
t = p.read_text().replace("    availability: active\n    access_status: provisioned\n",
                          "    availability: departed\n    access_status: revoked\n", 1)
p.write_text(t)
pathlib.Path("validators/registry/fixtures/r02/fail-departed-person/expected.json").write_text(
    '{"as_of":"2026-08-27","expect":["R02.2","R02.2"]}\n')  # primary_owner on product-1 and cross_reviewer on auth-service
EOF
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r02_assignment_person_ref.py -q` | `5 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r02/fail-unknown-person --as-of 2026-08-27 --format json \| python -c "import sys,json;d=json.load(sys.stdin);print(d[0]['code'],d[0]['spec'])"` | `R02.1 §15.5, §99.2` |
| 3 | shared-service coverage: `grep -c "service.yaml" validators/registry/rules/r02_assignment_person_ref.py` | `1` or more — §20.1 gives a shared service "the same four ownership relationships as a product" |
| 4 | baseline unchanged: `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json` | `[]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && python -m pytest validators/registry/tests/test_r02_assignment_person_ref.py -q && echo T03_PASS
```

Correct output: pytest summary line `5 passed` followed by `T03_PASS`.

**STOP rule.** If `registries/topology.yaml` does not exist in `integration`, implement R02 over products and shared services only, add `# topology.yaml absent at T03; succession refs deferred` as a comment in the rule module, and file the blocker with `component: L1-phase-1`. Do not create `topology.yaml` yourself — it is a Phase 1 registry artifact (§52.6).

---

## TASK L1-03-04 — R03 declared dependency names an existing shared service

**Size:** S **Depends on:** T01. **Slug:** `r03-dependency-refs`
**Creates:** `validators/registry/rules/r03_dependency_service_ref.py`, `validators/registry/fixtures/r03/**`, `validators/registry/tests/test_r03_dependency_service_ref.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly.** Build the set of `identity.id` from every `shared-services/*/service.yaml`. For every product:

* an entry in `dependencies.internal[]` absent from that set → `R03.1` — `"product declares a dependency on shared service '<id>' which does not exist in the registry (§20.1)"`.
* the converse edge: a service whose `consumers[]` names a product id with no `products/<id>/product.yaml` → `R03.2`. §20.1 calls `consumers` "authoritative; validated against products", so the check runs both ways.
* a product depending on a service that does **not** list it in `consumers[]` → `R03.3` — the graph of §20.2 is only honest if both declarations agree.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r03-dependency-refs
for c in pass fail-unknown-service fail-unknown-consumer fail-asymmetric-edge; do
  bash validators/registry/tools/make-fixture.sh r03 "$c"
done
sed -i 's/^  internal: \[auth-service\]$/  internal: [auth-service, billing-service]/' \
  validators/registry/fixtures/r03/fail-unknown-service/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R03.1"]}\n' \
  > validators/registry/fixtures/r03/fail-unknown-service/expected.json
sed -i 's/^consumers: \[product-1\]$/consumers: [product-1, product-77]/' \
  validators/registry/fixtures/r03/fail-unknown-consumer/shared-services/auth-service/service.yaml
printf '{"as_of":"2026-08-27","expect":["R03.2"]}\n' \
  > validators/registry/fixtures/r03/fail-unknown-consumer/expected.json
sed -i 's/^consumers: \[product-1\]$/consumers: []/' \
  validators/registry/fixtures/r03/fail-asymmetric-edge/shared-services/auth-service/service.yaml
printf '{"as_of":"2026-08-27","expect":["R03.3"]}\n' \
  > validators/registry/fixtures/r03/fail-asymmetric-edge/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r03_dependency_service_ref.py -q` | `4 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r03/fail-unknown-service --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['code'])"` | `R03.1` |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json` | `[]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && python -m pytest validators/registry/tests/test_r03_dependency_service_ref.py -q && echo T04_PASS
```

**STOP rule.** If the repository contains no `shared-services/` directory at all, do **not** skip the rule and do **not** create a placeholder service. Implement it against an empty service set (every internal dependency then correctly fails `R03.1`) and note in the PR body that the fleet declares no shared services yet. Only file a blocker if `dependencies.internal` is absent from `schemas/product/product.v2.schema.json`, with `component: L1-phase-2`.

---

## TASK L1-03-05 — R04 mandatory `end_date` for every non-employee

**Size:** S **Depends on:** T01. **Slug:** `r04-nonemployee-end-date`
**Creates:** `validators/registry/rules/r04_nonemployee_end_date.py`, `validators/registry/fixtures/r04/**`, `validators/registry/tests/test_r04_nonemployee_end_date.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly.** The non-employee set is the §7.1 list verbatim: `contractor`, `intern`, `temporary_specialist`, `consultant`. Employment types are open-ended (§7.1), so the rule is written as **"anything that is not `employee` is a non-employee"** — that is the fail-closed reading required by §64.1, and it means a newly added employment type is covered without a code change.

* `employment_type != "employee"` and `end_date` is null/absent → `R04.1` — `"non-employee '<id>' has no end_date (§7.1, §64.1)"`.
* `employment_type != "employee"` and no `scope:` block → `R04.2` — §64.1 "Non-employees: `end_date` mandatory, scope mandatory".
* `end_date` present and earlier than `start_date` → `R04.3`.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r04-nonemployee-end-date
for c in pass fail-null-end-date fail-missing-scope fail-inverted-dates fail-novel-employment-type; do
  bash validators/registry/tools/make-fixture.sh r04 "$c"
done
for c in pass fail-null-end-date fail-missing-scope fail-inverted-dates fail-novel-employment-type; do
cat >> "validators/registry/fixtures/r04/$c/registries/people.yaml" <<'EOF'
  - id: sec-1
    display_name: "Example Security Specialist"
    github_login: examplesec-1
    role: specialist
    employment_type: temporary_specialist
    capabilities: [security-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2026-04-01
    end_date: 2026-06-30
    scope:
      products: [product-1]
      repositories_only: true
EOF
done
sed -i 's/^    end_date: 2026-06-30$/    end_date: null/' \
  validators/registry/fixtures/r04/fail-null-end-date/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R04.1"]}\n' \
  > validators/registry/fixtures/r04/fail-null-end-date/expected.json
sed -i 's/^    employment_type: temporary_specialist$/    employment_type: fractional_cto/' \
  validators/registry/fixtures/r04/fail-novel-employment-type/registries/people.yaml
sed -i 's/^    end_date: 2026-06-30$/    end_date: null/' \
  validators/registry/fixtures/r04/fail-novel-employment-type/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R04.1"]}\n' \
  > validators/registry/fixtures/r04/fail-novel-employment-type/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r04_nonemployee_end_date.py -q` | `5 passed` |
| 2 | the `fail-novel-employment-type` fixture passes | proves the open-ended reading of §7.1; a rule hard-coding the four names fails this test |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r04/pass --as-of 2026-08-27 --format json` | `[]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && python -m pytest validators/registry/tests/test_r04_nonemployee_end_date.py -q && echo T05_PASS
```

**STOP rule.** If `schemas/registry/people.v1.schema.json` declares `employment_type` as a closed `enum`, the schema contradicts §7.1's "Employment types are open-ended" and `fail-novel-employment-type` will be rejected by R01 before R04 sees it. Do not edit the schema. File the blocker with `component: L1-phase-2`, quoting §7.1's first bullet.

---

## TASK L1-03-06 — R05 expired assignment

**Size:** S **Depends on:** T01. **Slug:** `r05-expired-assignment`
**Creates:** `validators/registry/rules/r05_expired_assignment.py`, `validators/registry/fixtures/r05/**`, `validators/registry/tests/test_r05_expired_assignment.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly.**

* Any assignment on any product or shared service whose `end_date` is strictly earlier than `ctx.today` → `R05.1` — `"assignment <type> for '<person>' expired on <date> (§15.5)"`.
* Any assignment whose `type` is in the §10.1 **mandatory-`end_date`** set and whose `end_date` is null → `R05.2`. That set, taken verbatim from the "Expires cleanly" column reading "Yes, mandatory `end_date`": `plan_approval_delegate`, `incident_coordination_delegate`, `founder_decision_delegate`, `registry_owner_delegate`, `verification_delegate`, `cross_review_shadow`, `mentor`. The types reading "Yes, on `end_date`" — `temporary_contributor`, `production_approval_delegate` — also require one, by invariant 58 ("Temporary assignments carry a mandatory end date"), and are in the set.
* Any assignment whose `end_date` is between `ctx.today` and `ctx.today + 14 days` → `R05.3`, severity `warning`. §10.1: "Every delegation-type assignment receives a 14-day advance expiry warning". This is the one non-blocking finding in the suite; it must not change the exit code on its own, and `test_r05` asserts exactly that.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r05-expired-assignment
for c in pass fail-expired fail-delegate-no-end-date warn-expiring-in-10-days; do
  bash validators/registry/tools/make-fixture.sh r05 "$c"
done
python - <<'EOF'
import pathlib
base = pathlib.Path("validators/registry/fixtures/r05")
add = """  - person: dev-b
    type: temporary_contributor
    start_date: 2026-05-01
    end_date: {end}
    reason: "fixture"
"""
for case, end, expect in [
    ("fail-expired", "2026-06-15", ["R05.1"]),
    ("warn-expiring-in-10-days", "2026-09-05", ["R05.3"]),
    ("fail-delegate-no-end-date", "null", ["R05.2"]),
]:
    p = base / case / "products/product-1/product.yaml"
    t = p.read_text().replace("escalation: team_lead\n", add.format(end=end) + "escalation: team_lead\n", 1)
    p.write_text(t)
    (base / case / "expected.json").write_text('{"as_of":"2026-08-27","expect":%s}\n' % expect.__repr__().replace("'", '"'))
EOF
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r05_expired_assignment.py -q` | `4 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r05/warn-expiring-in-10-days --as-of 2026-08-27 --format json >/dev/null; echo $?` | `1` — a warning is still a finding; the harness's exit rule is "any finding → 1". Record this explicitly in the PR body so L2 knows the gate fails on the 14-day warning too, as §10.1 intends ("warned, never silent") |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r05/warn-expiring-in-10-days --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['severity'])"` | `warning` |
| 4 | date determinism: run criterion 3 again with `--as-of 2026-10-01` | `[]` semantics change to `R05.1`; the rule reads `ctx.today`, never the wall clock |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r05_expired_assignment.py -q >/dev/null
  test "$(python -m validators.registry.cli --root validators/registry/fixtures/r05/warn-expiring-in-10-days --as-of 2026-10-01 --format json | python -c "import sys,json;print(json.load(sys.stdin)[0][\"code\"])")" = "R05.1"
  echo T06_PASS
'
```

**STOP rule.** If you cannot make criterion 4 pass without importing `datetime.date.today()` inside the rule module, you have mis-wired `ctx.today`. Fix the wiring in `context.py` — do not add a second clock. If `context.py` cannot carry it because T01 froze the signature differently, file the blocker with `component: other` and quote the frozen signature.

---

## TASK L1-03-07 — R06 `restore_tested` within the applicable rolling window

**Size:** M **Depends on:** T01, T00 (`records_snapshot_mode`). **Slug:** `r06-restore-window`
**Creates:** `validators/registry/rules/r06_restore_window.py`, `validators/registry/fixtures/r06/**`, `validators/registry/tests/test_r06_restore_window.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly.** The window is derived, never declared:

| `classification.reliability_criticality` | Applicable window |
|---|---|
| `critical` | 30 days (§44.2: "a `critical` product is restore-tested within every rolling 30-day window") |
| `high`, `medium`, `low` | 90 days (§15.4, §44.2: "The 90-day window is the floor for all products") |

* `recovery` present, `restore_tested` absent or null → `R06.1`.
* `ctx.today - restore_tested > window` → `R06.2` — `"restore_tested <date> is <N> days old; product window is <W> days (§15.4, §44.2, invariant 4)"`.
* `--records-root` supplied and the newest **passing** record in `<records-root>/records/restore-tests/` for this product carries a date **later than or different from** the declared `restore_tested` → `R06.4` — `"restore_tested is derived, not declared (§44.2); declared <d1>, newest passing record <d2>"`. A hand-edited date is drift, not evidence.
* `--records-root` **not** supplied → emit `R06.3` severity `info`, message `"derived-date check skipped: no --records-root (see contracts/decisions/L1-03.yaml records_snapshot_mode)"`. `info` findings are reported but, uniquely, do **not** affect the exit code; T01's `cli.py` computes the exit code over `severity in {"blocking","warning"}` only. If T01 did not implement that, add it in this task and update `test_harness.py`.
* `recovery: not-applicable` → the rule checks that a `reason` is declared (§44.1 "may declare `recovery: not-applicable` with a declared reason, CI-validated") → `R06.5` when absent, and otherwise skips the date checks.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r06-restore-window
for c in pass fail-stale-90 fail-stale-30-critical fail-missing-date fail-not-applicable-no-reason info-no-records-root fail-declared-not-derived; do
  bash validators/registry/tools/make-fixture.sh r06 "$c"
done
sed -i 's/^  restore_tested: 2026-08-14$/  restore_tested: 2026-04-01/' \
  validators/registry/fixtures/r06/fail-stale-90/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R06.2"]}\n' \
  > validators/registry/fixtures/r06/fail-stale-90/expected.json
sed -i 's/^  reliability_criticality: high$/  reliability_criticality: critical/' \
  validators/registry/fixtures/r06/fail-stale-30-critical/products/product-1/product.yaml
sed -i 's/^  restore_tested: 2026-08-14$/  restore_tested: 2026-07-01/' \
  validators/registry/fixtures/r06/fail-stale-30-critical/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R06.2"]}\n' \
  > validators/registry/fixtures/r06/fail-stale-30-critical/expected.json
mkdir -p validators/registry/fixtures/r06/fail-declared-not-derived/_records/records/restore-tests
cat > validators/registry/fixtures/r06/fail-declared-not-derived/_records/records/restore-tests/2026-07-02-product-1.yaml <<'EOF'
record_schema_version: 1
product: product-1
tested_on: 2026-07-02
result: passed
integrity_check: row-counts-plus-checksum
EOF
printf '{"as_of":"2026-08-27","records_root":"_records","expect":["R06.4"]}\n' \
  > validators/registry/fixtures/r06/fail-declared-not-derived/expected.json
```

`tests/conftest.py` must be extended in this task to pass `--records-root <fixture>/<records_root>` when `expected.json` carries the key.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r06_restore_window.py -q` | `7 passed` |
| 2 | 30-day tightening: the `fail-stale-30-critical` fixture (76 days old) fails, while the identical tree with `reliability_criticality: high` passes | `R06.2` then `[]` — proves the tighten-only rule of §15.4 |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r06/info-no-records-root --as-of 2026-08-27 --format json >/dev/null; echo $?` | `0` — an `info` finding alone never fails the gate |
| 4 | `python -m validators.registry.cli --root validators/registry/fixtures/r06/info-no-records-root --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['code'])"` | `R06.3` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r06_restore_window.py -q >/dev/null
  python -m validators.registry.cli --root validators/registry/fixtures/r06/info-no-records-root --as-of 2026-08-27 --format json >/dev/null
  echo T07_PASS
'
```

**STOP rule.** If `contracts/decisions/L1-03.yaml → records_snapshot_mode` is anything other than `optional-path`, the `--records-root` design above does not apply. Do not invent an alternative cross-repository read (a git submodule, an API call, a vendored copy). File the blocker with `component: L0-decision`, quoting the stamped value and §52.6's statement that `records/**` lives in the records repository (D89).

---

## TASK L1-03-08 — R07 the 24x7 / extended coverage blocker

**Size:** L **Depends on:** T01. **Slug:** `r07-coverage-rota`
**Creates:** `validators/registry/rules/r07_coverage_rota.py`, `validators/registry/coverage.py`, `validators/registry/fixtures/r07/**`, `validators/registry/tests/test_r07_coverage_rota.py`. **Edits:** `rules_manifest.yaml`.

This is the §15.6 onboarding blocker. **D112** is what makes it implementable: it gives the validator its input on the person side — `people.yaml → people[].work_arrangement.accepted_coverage_window` (§7.3) — and `people.yaml → rotas[]` carries, per product, "the named rota members, each member's accepted window, the paging-path identifier and the funding decision record" (§52.6 people.yaml row; §47.9).

**Window shapes the rule reads** (§15.1 `coverage_window` "days, hours and timezone"; §7.3 `accepted_coverage_window`):

```yaml
coverage_window:
  days: [mon, tue, wed, thu, fri, sat, sun]
  start: "00:00"
  end: "24:00"
  timezone: Asia/Kolkata
```

**Algorithm, deterministic.** Expand each window over one canonical UTC week anchored on the Monday of the ISO week containing `ctx.today`, resolving each declared IANA timezone with `zoneinfo` so DST is applied rather than assumed away (§7.3: "Timezone is an IANA identifier, never a UTC offset, because offsets move twice a year"). Represent each window as a set of UTC minute intervals. The rota's coverage is the **union** of the accepted windows of rota members whose `availability` is `active`. The product's requirement is the expanded `coverage_window`. Any non-empty `requirement − coverage` is an uncovered segment.

**Findings, each a verbatim clause of §47.9 or §7.3:**

| Code | Condition | Spec |
|---|---|---|
| `R07.1` | `support_model` in `{extended, 24x7}` and `coverage_window` is null or absent | §15.5, §47.9 "A missing `coverage_window` … fails validation" |
| `R07.2` | no `rotas[]` entry for this product | §15.6 "cannot be onboarded unless a funded response rota exists"; invariant 31 |
| `R07.3` | a rota member id is not in `people.yaml` | §47.9 "CI validates coverage against declared data, never against a claim" |
| `R07.4` | a rota member has no `work_arrangement` block, **fail closed** | §7.3, D112 |
| `R07.5` | a rota member's `accepted_coverage_window` is null, **fail closed** | §7.3, D112 |
| `R07.6` | a rota member's `availability` is not `active` | §47.9 "or a rota member who is not active fails validation" |
| `R07.7` | uncovered minutes remain after the union; message names the uncovered segment in the product's declared timezone | §47.9 "an uncovered hour … fails validation"; D112 |
| `R07.8` | `rotas[].paging_path` is absent or empty | §47.9 "an unnamed paging path … fails validation" |
| `R07.9` | `rotas[].funding_decision_record` is absent | §47.9 "the funding decision record"; §15.6 "funded response rota" |
| `R07.10` | `support_model: business-hours` but `coverage_window` is non-null | §15.1 "null for business-hours" |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r07-coverage-rota
for c in pass-24x7-fully-covered fail-24x7-no-window fail-24x7-no-rota fail-uncovered-hour fail-member-no-work-arrangement fail-member-null-accepted-window fail-member-not-active fail-no-paging-path fail-no-funding-record fail-business-hours-with-window; do
  bash validators/registry/tools/make-fixture.sh r07 "$c"
done

# the passing 24x7 fixture: two members whose accepted windows tile the week
python - <<'PY'
import pathlib
d = pathlib.Path("validators/registry/fixtures/r07/pass-24x7-fully-covered")
p = d/"products/product-1/product.yaml"
t = p.read_text()
t = t.replace("  support_model: business-hours\n", "  support_model: 24x7\n")
t = t.replace("  detection_expectation: next-business-morning\n", "  detection_expectation: continuous\n")
t = t.replace("  coverage_window: null\n",
"""  coverage_window:
    days: [mon, tue, wed, thu, fri, sat, sun]
    start: "00:00"
    end: "24:00"
    timezone: Asia/Kolkata
""")
p.write_text(t)

q = d/"registries/people.yaml"
t = q.read_text()
t = t.replace("      accepted_coverage_window: null\n",
"""      accepted_coverage_window:
        days: [mon, tue, wed, thu, fri, sat, sun]
        start: "00:00"
        end: "12:00"
        timezone: Asia/Kolkata
""", 1)
t = t.replace("      accepted_coverage_window: null\n",
"""      accepted_coverage_window:
        days: [mon, tue, wed, thu, fri, sat, sun]
        start: "12:00"
        end: "24:00"
        timezone: Asia/Kolkata
""", 1)
t = t.replace("rotas: []\n",
"""rotas:
  - product: product-1
    paging_path: pager-primary-p1
    funding_decision_record: records/decisions/2026-03-04-fund-p1-rota.yaml
    members: [dev-a, dev-b]
""")
q.write_text(t)
(d/"expected.json").write_text('{"as_of":"2026-08-27","expect":[]}\n')
PY

# the uncovered-hour fixture: same tree, second member's window starts an hour late
cp -r validators/registry/fixtures/r07/pass-24x7-fully-covered/. validators/registry/fixtures/r07/fail-uncovered-hour/
sed -i '0,/        start: "12:00"/s//        start: "13:00"/' \
  validators/registry/fixtures/r07/fail-uncovered-hour/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R07.7"]}\n' \
  > validators/registry/fixtures/r07/fail-uncovered-hour/expected.json
```

Build the remaining eight fixtures the same way: copy `pass-24x7-fully-covered`, apply exactly one delta, write `expected.json` with the single code from the table above.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r07_coverage_rota.py -q` | `10 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r07/fail-uncovered-hour --as-of 2026-08-27 --format json \| python -c "import sys,json;f=json.load(sys.stdin)[0];print(f['code'], '60' in f['message'] or 'uncovered' in f['message'])"` | `R07.7 True` — the message must name the uncovered span, not merely say "not covered" |
| 3 | fail-closed proof: `python -m validators.registry.cli --root validators/registry/fixtures/r07/fail-member-null-accepted-window --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['code'])"` | `R07.5` — not `[]`. D112: "fails closed where a member has no work arrangement, no accepted window" |
| 4 | DST proof: a fixture with `timezone: Europe/Dublin` on the product and `timezone: Asia/Kolkata` on the members produces the same verdict whether `--as-of` falls in January or July | identical `expect` sets; a rule using fixed UTC offsets fails this |
| 5 | `grep -c "zoneinfo" validators/registry/coverage.py` | `1` or more |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r07_coverage_rota.py -q >/dev/null
  test "$(python -m validators.registry.cli --root validators/registry/fixtures/r07/fail-member-null-accepted-window --as-of 2026-08-27 --format json | python -c "import sys,json;print(json.load(sys.stdin)[0][\"code\"])")" = "R07.5"
  test "$(python -m validators.registry.cli --root validators/registry/fixtures/r07/pass-24x7-fully-covered --as-of 2026-08-27 --format json)" = "[]"
  echo T08_PASS
'
```

**STOP rule.** If `schemas/registry/people.v1.schema.json` has no `rotas` property, or `schemas/product/product.v2.schema.json` has no `operations.coverage_window` object with `days`, `start`, `end`, `timezone`, R07 has nothing to read and D112's whole point is unmet. **Do not add the properties to the schemas from this task** — `schemas/**` is Phase 2's deliverable and a second author guarantees a merge conflict inside L1. File the blocker with `component: L1-phase-2`, quoting §52.6's `people.yaml` row ("per-product rota membership for funded coverage — each member's accepted window, the paging-path identifier and the funding decision record") and D112 in full.

---

## TASK L1-03-09 — R08 commitments entry without a recorded `conflict_check`

**Size:** S **Depends on:** T01. **Slug:** `r08-conflict-check`
**Creates:** `validators/registry/rules/r08_conflict_check.py`, `validators/registry/fixtures/r08/**`, `validators/registry/tests/test_r08_conflict_check.py`. **Edits:** `rules_manifest.yaml`.

**Scope discipline.** This task implements the **presence** rule only: §21.4's closing sentence — "`conflict_check: passed` or `waived-with-decision` is recorded in the entry; CI fails a commitments entry with neither" — and §15.5's matching bullet. It does **not** implement the eight-row conflict table of §21.4; that table is the `check-commitment` CLI, a separate named build-surface tool (§99.2 tools table, subsystem B) and a separate task in a later phase. Do not start building it here.

* `commitments[]` entry with `conflict_check` absent, null, or any value outside `{passed, waived-with-decision}` → `R08.1`.
* `conflict_check: waived-with-decision` with no `waiver_decision_record` field pointing at a record path → `R08.2`. §21.4: "explicitly waived by a Founder decision record" — a waiver naming no record is the same defect as no waiver.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r08-conflict-check
for c in pass-passed pass-waived fail-absent fail-null fail-bad-token fail-waived-no-record; do
  bash validators/registry/tools/make-fixture.sh r08 "$c"
done
sed -i 's/^    conflict_check: waived-with-decision$/    conflict_check: passed/' \
  validators/registry/fixtures/r08/pass-passed/products/product-1/product.yaml
sed -i '/^    conflict_check: waived-with-decision$/d' \
  validators/registry/fixtures/r08/fail-absent/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R08.1"]}\n' \
  > validators/registry/fixtures/r08/fail-absent/expected.json
sed -i 's/^    conflict_check: waived-with-decision$/    conflict_check: pending/' \
  validators/registry/fixtures/r08/fail-bad-token/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R08.1"]}\n' \
  > validators/registry/fixtures/r08/fail-bad-token/expected.json
printf '{"as_of":"2026-08-27","expect":["R08.2"]}\n' \
  > validators/registry/fixtures/r08/fail-waived-no-record/expected.json
cat >> validators/registry/fixtures/r08/pass-waived/products/product-1/product.yaml <<'EOF'
    waiver_decision_record: records/decisions/2026-02-11-p1-sla-waiver.yaml
EOF
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r08_conflict_check.py -q` | `6 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r08/fail-bad-token --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['code'])"` | `R08.1` |
| 3 | scope discipline: `grep -ci "rto_minutes\|downtime budget\|undetected window" validators/registry/rules/r08_conflict_check.py` | `0` — the eight-row table is not implemented here |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r08_conflict_check.py -q >/dev/null
  test "$(grep -ci "downtime budget" validators/registry/rules/r08_conflict_check.py)" = "0"
  echo T09_PASS
'
```

**STOP rule.** If `waiver_decision_record` is not in `schemas/product/product.v2.schema.json`, implement `R08.2` as a check for **any** key on the entry whose name ends `_decision_record`, note the deviation in the PR body, and file the blocker with `component: L1-phase-2` quoting §21.4 ("explicitly waived by a Founder decision record"). Do not add the field to the schema yourself.

---

## TASK L1-03-10 — R09 exception without an expiry

**Size:** S **Depends on:** T01. **Slug:** `r09-exception-expiry`
**Creates:** `validators/registry/rules/r09_exception_expiry.py`, `validators/registry/fixtures/r09/**`, `validators/registry/tests/test_r09_exception_expiry.py`. **Edits:** `rules_manifest.yaml`.

**What the rule does, exactly**, over `registries/exceptions.yaml`:

* `expiry` absent or null → `R09.1` — `"exception <id> has no expiry; an exception with no expiry is not an exception, it is undocumented policy (§54.2, invariant 77)"`.
* `expiry` earlier than `start` → `R09.2`.
* `type` in `{bootstrap, founder_standing_delegation_activation}` and `deactivation_trigger` null or absent → `R09.3`. §54.2: "`deactivation_trigger` … mandatory for types that close on an event", and §54.2 names exactly these two as the declared-non-discretionary types.
* `compensating_control` absent → `R09.4`. §54.2: "Every exception names a compensating control … If the honest answer is 'none', that must be written, because it changes the class." The literal string `none` satisfies the rule; an absent field does not.
* `compensating_control` present and not the literal `none`, with `compensating_control_record` or `compensating_control_cadence` absent → `R09.5`. §54.2: "the record names the store its execution lands in and the cadence it runs on".
* `authority` naming a person id absent from `people.yaml` → `R09.6` (§54.1 comment: "must hold the mapped capability" — the reference must at minimum resolve; the capability mapping of §54.3 is not implemented here).

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r09-exception-expiry
for c in pass fail-no-expiry fail-inverted-dates fail-bootstrap-no-trigger fail-no-compensating-control fail-control-without-record fail-unknown-authority; do
  bash validators/registry/tools/make-fixture.sh r09 "$c"
done
for c in pass fail-no-expiry fail-inverted-dates fail-bootstrap-no-trigger fail-no-compensating-control fail-control-without-record fail-unknown-authority; do
python - "$c" <<'PY'
import pathlib, sys
c = sys.argv[1]
p = pathlib.Path(f"validators/registry/fixtures/r09/{c}/registries/exceptions.yaml")
p.write_text("""registry_version: 1
exceptions:
  - id: EXC-2026-041
    type: platform_compatibility
    reason: "fixture exception"
    requester: dev-b
    authority: dev-a
    affected:
      products: [product-1]
      repositories: [org/product-1-api]
    scope: "Remain on workflows@v3 for CI only"
    start: 2026-05-02
    expiry: 2026-12-30
    compensating_control: "Weekly manual dependency scan"
    compensating_control_record: records/security-reviews/
    compensating_control_cadence: weekly
    owner: dev-a
    review_date: 2026-06-01
    renewals: 0
    became_permanent: false
    closure: null
    deactivation_trigger: null
""")
PY
done
sed -i 's/^    expiry: 2026-12-30$/    expiry: null/' \
  validators/registry/fixtures/r09/fail-no-expiry/registries/exceptions.yaml
printf '{"as_of":"2026-08-27","expect":["R09.1"]}\n' \
  > validators/registry/fixtures/r09/fail-no-expiry/expected.json
sed -i 's/^    type: platform_compatibility$/    type: bootstrap/' \
  validators/registry/fixtures/r09/fail-bootstrap-no-trigger/registries/exceptions.yaml
printf '{"as_of":"2026-08-27","expect":["R09.3"]}\n' \
  > validators/registry/fixtures/r09/fail-bootstrap-no-trigger/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r09_exception_expiry.py -q` | `7 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r09/fail-no-expiry --as-of 2026-08-27 --format json \| python -c "import sys,json;f=json.load(sys.stdin)[0];print(f['code'],f['spec'])"` | `R09.1 §54.2, invariant 77` |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r09/pass --as-of 2026-08-27 --format json` | `[]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && python -m pytest validators/registry/tests/test_r09_exception_expiry.py -q && echo T10_PASS
```

**STOP rule.** Do **not** implement renewal counting or same-scope matching (§54.2 "Same scope, new ID, still a renewal"). That is scope matching over closed exceptions across two quarters — Subsystem O governance jobs and the reconciler's same-scope nomination, not a control-plane schema rule. If you find yourself writing a similarity function, stop and re-read this paragraph.

---

## TASK L1-03-11 — R10 unclassified control

**Size:** M **Depends on:** T00 (`control_classification_home`), T01. **Slug:** `r10-control-classification`
**Creates:** `validators/registry/rules/r10_control_classification.py`, `validators/registry/fixtures/r10/**`, `validators/registry/tests/test_r10_control_classification.py`, and — only if L0 stamped the proposed default — `registries/policies.yaml` seeded with the thirteen control rows of the §64.2 table. **Edits:** `rules_manifest.yaml`.

**Read `contracts/decisions/L1-03.yaml → control_classification_home` first.** Everything below assumes the stamped value is `registries/policies.yaml` with a `failure_mode:` field. If the stamped value is anything else, use that path and that field name instead; the rule logic is unchanged.

**The thirteen controls of §64.2, transcribed verbatim** — the seed file must contain exactly these ids and these `failure_mode` values, and no others invented:

| id | `failure_mode` |
|---|---|
| `authentication-and-authorisation` | `fail-closed` |
| `branch-protection-and-required-reviews` | `fail-closed` |
| `production-deployment-approval` | `fail-closed` |
| `rollback-across-migration-boundary` | `fail-closed` |
| `verification-and-required-status-checks` | `fail-closed` |
| `secret-access` | `fail-closed` |
| `reconciliation` | `graded` |
| `product-runtime-monitoring` | `fail-open` |
| `dashboards-and-health-reports` | `fail-open` |
| `planning-metadata-and-boards` | `graded` |
| `background-machine-layer` | `fail-open` |
| `ai-runtimes` | `fail-open` |

`graded` exists because §64.2's reconciliation row reads "Fail closed for Blocking-class checks; fail open with an alert for Green-class checks" and the boards row reads "Degrade" — neither is a single token. A `graded` row must additionally declare `graded_detail:` (free text, transcribed from the table's Behaviour column) or it is unclassified.

**Findings:**

| Code | Condition | Spec |
|---|---|---|
| `R10.1` | a control entry with no `failure_mode` | §64.2 "Every control is explicitly classified. Unclassified controls fail CI"; invariant 80 |
| `R10.2` | `failure_mode` outside `{fail-closed, fail-open, graded}` | §64.2 |
| `R10.3` | `failure_mode: graded` with no `graded_detail` | §64.2 reconciliation and boards rows |
| `R10.4` | one of the twelve §64.2 control ids is absent from the register | §64.2 is the complete table; a missing row is an unclassified control by omission |
| `R10.5` | an entry with no `owner` | §52.6 `policies.yaml` row: "each policy names its own owner" |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r10-control-classification
python -c "import yaml,sys;d=yaml.safe_load(open('contracts/decisions/L1-03.yaml'));print(d['control_classification_home'])"
for c in pass fail-missing-failure-mode fail-bad-token fail-graded-no-detail fail-missing-control-row fail-no-owner; do
  bash validators/registry/tools/make-fixture.sh r10 "$c"
done
```

Seed each fixture's `registries/policies.yaml` with the twelve rows above, then apply one delta per fixture. Then seed the **real** register at the stamped path with the same twelve rows and a `review_date` per row.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r10_control_classification.py -q` | `6 passed` |
| 2 | `python -c "import yaml;d=yaml.safe_load(open('registries/policies.yaml'));print(len([e for e in d['policies'] if 'failure_mode' in e]))"` | `12` |
| 3 | `python -m validators.registry.cli --root . --rule R10 --as-of 2026-08-27 --format json` run at the repo root | `[]`, exit `0` — the real register classifies every control |
| 4 | no invented controls: `python -c "import yaml;ids={e['id'] for e in yaml.safe_load(open('registries/policies.yaml'))['policies'] if 'failure_mode' in e};print(sorted(ids))"` | exactly the twelve ids in the table above |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r10_control_classification.py -q >/dev/null
  test "$(python -m validators.registry.cli --root . --rule R10 --as-of 2026-08-27 --format json)" = "[]"
  echo T11_PASS
'
```

**STOP rule.** If `control_classification_home` is unset, or is set to a path outside `registries/**`, stop. A path outside `registries/**` is outside L1's ownership and writing it fails lane-guard. File the blocker with `component: L0-decision`, quoting §52.6's thirty-artifact ceiling and §64.2's "Unclassified controls fail CI".

---

## TASK L1-03-12 — R11 capability defined before it is granted

**Size:** M **Depends on:** T01. **Slug:** `r11-capability-defined`
**Creates:** `validators/registry/rules/r11_capability_defined.py`, `validators/registry/fixtures/r11/**`, `validators/registry/tests/test_r11_capability_defined.py`. **Edits:** `rules_manifest.yaml`.

**Source of the vocabulary.** §9's table "is the complete capability vocabulary" (§9.1). The machine copy of it is `schemas/registry/capability.enum.schema.json`, authored in Phase 2 — the vocabulary belongs in the schema layer, not in a new registry artifact, because §52.6 caps the control-plane inventory at twenty-nine and forbids a new artifact where an existing layer can hold the content. **Do not create `registries/capabilities.yaml`.**

**Findings:**

| Code | Condition | Spec |
|---|---|---|
| `R11.1` | a `people[].capabilities[]` entry absent from the enum | §9.1 "A capability appearing in … a `people.yaml` grant … without a row in this table fails control-plane CI validation" |
| `R11.2` | a `roles[].default_capabilities[]` entry absent from the enum | §9.1 "in a `roles.yaml` default" |
| `R11.3` | an assignment type in any contract absent from the seventeen types of §10.1 | §9.1 "or in any assignment type" |
| `R11.4` | the enum file omits any of the capabilities §9's table defines — checked against the frozen list in the rule module's `SPEC_VOCABULARY` constant | **D90**: "swept to completion … the CI rule added under D81 now has nothing left to reject" |

`SPEC_VOCABULARY` is transcribed from §9's table verbatim and must contain exactly: `backend`, `frontend`, `mobile`, `data`, `code-review`, `architecture`, `security-review`, `migration-review`, `verification`, `uat`, `release-signoff`, `production-approval`, `incident-response`, `plan-approval`, `reviewer-matrix-change`, `platform-change-approval`, `platform-admin`, `devops`, `lifecycle-decision`, `escalation`, `mobile-release`, `exceptional-approval`, `people-intelligence`, `strategy`, `budget`, `hiring`, `customer-commitment`. Twenty-seven entries. `devops` is present because D90 added it — its absence was exactly the defect D90 closed.

The seventeen assignment types of §10.1, verbatim: `primary_owner`, `cross_reviewer`, `backup_owner`, `temporary_contributor`, `incident_responder`, `verification_responsibility`, `architecture_responsibility`, `production_approval_delegate`, `security_reviewer`, `plan_approval_delegate`, `incident_coordination_delegate`, `domain_lead`, `founder_decision_delegate`, `registry_owner_delegate`, `verification_delegate`, `cross_review_shadow`, `mentor`.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r11-capability-defined
for c in pass fail-undefined-people-grant fail-undefined-role-default fail-unknown-assignment-type fail-enum-drift; do
  bash validators/registry/tools/make-fixture.sh r11 "$c"
done
sed -i 's/^    capabilities: \[backend, code-review\]$/    capabilities: [backend, code-review, deploy-anything]/' \
  validators/registry/fixtures/r11/fail-undefined-people-grant/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R11.1"]}\n' \
  > validators/registry/fixtures/r11/fail-undefined-people-grant/expected.json
sed -i 's/^    default_capabilities: \[code-review\]$/    default_capabilities: [code-review, ship-it]/' \
  validators/registry/fixtures/r11/fail-undefined-role-default/registries/roles.yaml
printf '{"as_of":"2026-08-27","expect":["R11.2"]}\n' \
  > validators/registry/fixtures/r11/fail-undefined-role-default/expected.json
sed -i 's/^    type: cross_reviewer$/    type: shadow_owner/' \
  validators/registry/fixtures/r11/fail-unknown-assignment-type/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R11.3"]}\n' \
  > validators/registry/fixtures/r11/fail-unknown-assignment-type/expected.json
```

For `fail-enum-drift`, copy `schemas/registry/capability.enum.schema.json` into the fixture with `devops` removed; `expect: ["R11.4"]`. The rule must therefore read the enum from `<root>/schemas/registry/capability.enum.schema.json` when present in the fixture root, falling back to the repo's own copy.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r11_capability_defined.py -q` | `5 passed` |
| 2 | `python -c "import re,pathlib;s=pathlib.Path('validators/registry/rules/r11_capability_defined.py').read_text();import ast;print(len([m for m in re.findall(r'\"[a-z-]+\"', s)]) > 0)"` then count `SPEC_VOCABULARY` | `27` entries |
| 3 | D90 proof: `python -m validators.registry.cli --root validators/registry/fixtures/r11/fail-enum-drift --rule R11 --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['code'])"` | `R11.4` |
| 4 | `grep -r "registries/capabilities.yaml" validators/registry \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r11_capability_defined.py -q >/dev/null
  test "$(python -c "from validators.registry.rules import r11_capability_defined as m; print(len(m.SPEC_VOCABULARY))")" = "27"
  echo T12_PASS
'
```

**STOP rule.** If `schemas/registry/capability.enum.schema.json` is absent, do not transcribe §9's table into a new schema file yourself — Phase 2 owns `schemas/**` and a duplicate enum is exactly the "second source of truth" §5 forbids. File the blocker with `component: L1-phase-2`, quoting §9.1 and D90.

---

## TASK L1-03-13 — R12 no dangerous capability in a role default

**Size:** S **Depends on:** T12 (shares the vocabulary constant). **Slug:** `r12-dangerous-role-default`
**Creates:** `validators/registry/rules/r12_dangerous_role_default.py`, `validators/registry/fixtures/r12/**`, `validators/registry/tests/test_r12_dangerous_role_default.py`. **Edits:** `rules_manifest.yaml`.

**The dangerous set, transcribed verbatim from §8 (D106)** — exactly these eight, no more, no fewer: `production-approval`, `platform-change-approval`, `platform-admin`, `security-review`, `migration-review`, `exceptional-approval`, `lifecycle-decision`, `people-intelligence`.

| Code | Condition | Spec |
|---|---|---|
| `R12.1` | any `roles[].default_capabilities[]` entry in the dangerous set | §8 "Control-plane CI rejects a `roles.yaml` default containing any of them"; D106; invariant 79 |
| `R12.2` | the `founder` role default containing `people-intelligence` | §9.1 "`people-intelligence` is held by the Founder and is not delegable (D109)" — held by the person, granted in `people.yaml`, never inherited from the role default. §8's rule admits no exception for `founder`, and D106 says the dangerous set is "granted only by explicit entry in `people.yaml`, never by role". Emitted as a distinct code because the §8 role table's `founder` row itself lists it, and the reviewer needs the contradiction named rather than buried in a generic finding |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r12-dangerous-role-default
for c in pass fail-team-lead-production-approval fail-founder-people-intelligence fail-multiple; do
  bash validators/registry/tools/make-fixture.sh r12 "$c"
done
sed -i 's/^    default_capabilities: \[architecture, plan-approval, escalation, reviewer-matrix-change\]$/    default_capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change, production-approval]/' \
  validators/registry/fixtures/r12/fail-team-lead-production-approval/registries/roles.yaml
printf '{"as_of":"2026-08-27","expect":["R12.1"]}\n' \
  > validators/registry/fixtures/r12/fail-team-lead-production-approval/expected.json
sed -i 's/^    default_capabilities: \[strategy, budget, hiring, customer-commitment\]$/    default_capabilities: [strategy, budget, hiring, customer-commitment, people-intelligence]/' \
  validators/registry/fixtures/r12/fail-founder-people-intelligence/registries/roles.yaml
printf '{"as_of":"2026-08-27","expect":["R12.2"]}\n' \
  > validators/registry/fixtures/r12/fail-founder-people-intelligence/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r12_dangerous_role_default.py -q` | `4 passed` |
| 2 | `python -c "from validators.registry.rules import r12_dangerous_role_default as m; print(len(m.DANGEROUS)); print(sorted(m.DANGEROUS))"` | `8` and the eight names above, sorted |
| 3 | `python -m validators.registry.cli --root . --rule R12 --as-of 2026-08-27 --format json` at the repo root | `[]` — the live `registries/roles.yaml` must already comply |
| 4 | `python -c "from validators.registry.rules import r12_dangerous_role_default as m; from validators.registry.rules import r11_capability_defined as v; print(m.DANGEROUS <= set(v.SPEC_VOCABULARY))"` | `True` — every dangerous name is a defined capability |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r12_dangerous_role_default.py -q >/dev/null
  test "$(python -c "from validators.registry.rules import r12_dangerous_role_default as m;print(len(m.DANGEROUS))")" = "8"
  test "$(python -m validators.registry.cli --root . --rule R12 --as-of 2026-08-27 --format json)" = "[]"
  echo T13_PASS
'
```

**STOP rule.** If criterion 3 fails — the live `registries/roles.yaml` contains a dangerous capability in a role default — do **not** edit `roles.yaml` in this task to make your own rule pass. That is a registry content change, it belongs in its own PR with the Founder as owner (§52.6), and silently fixing it hides the finding the rule exists to surface. Ship the rule, then file the blocker with `component: L1-phase-1`, quoting D106 and the offending role id.

---

## TASK L1-03-14 — R13 RPO must be satisfiable by the declared backup frequency

**Size:** S **Depends on:** T01. **Slug:** `r13-rpo-backup-frequency`
**Creates:** `validators/registry/rules/r13_rpo_backup_frequency.py`, `validators/registry/fixtures/r13/**`, `validators/registry/tests/test_r13_rpo_backup_frequency.py`. **Edits:** `rules_manifest.yaml`.

**The mapping, transcribed verbatim from §44.1** — the closed set and its minutes:

| `backup_frequency` | minutes |
|---|---|
| `continuous` | `0` |
| `hourly` | `60` |
| `six-hourly` | `360` |
| `daily` | `1440` |
| `weekly` | `10080` |

§44.1: "the check is arithmetic rather than judgment: `rpo_minutes` must be at least the minutes value of the declared `backup_frequency` … unless `point_in_time_recovery.enabled` is true, in which case `rpo_minutes` must be at least the declared `window_minutes`."

| Code | Condition |
|---|---|
| `R13.1` | `backup_frequency` outside the closed set → "a frequency outside the closed set is a malformed contract" (§44.1) |
| `R13.2` | PITR disabled and `rpo_minutes < map[backup_frequency]` |
| `R13.3` | PITR enabled and `window_minutes` null → the escape hatch is a declared field, not an absence |
| `R13.4` | PITR enabled and `rpo_minutes < window_minutes` |
| `R13.5` | `rpo_minutes` or `rto_minutes` absent, or declared in any unit other than minutes (a non-integer value) → §44.1 "RPO and RTO are declared in minutes only — one unit, no ambiguity" |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r13-rpo-backup-frequency
for c in pass pass-pitr fail-bad-frequency fail-rpo-below-frequency fail-pitr-null-window fail-rpo-below-pitr-window fail-non-integer-rpo; do
  bash validators/registry/tools/make-fixture.sh r13 "$c"
done
sed -i 's/^  backup_frequency: daily$/  backup_frequency: nightly/' \
  validators/registry/fixtures/r13/fail-bad-frequency/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R13.1"]}\n' \
  > validators/registry/fixtures/r13/fail-bad-frequency/expected.json
sed -i 's/^  rpo_minutes: 1440$/  rpo_minutes: 60/' \
  validators/registry/fixtures/r13/fail-rpo-below-frequency/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R13.2"]}\n' \
  > validators/registry/fixtures/r13/fail-rpo-below-frequency/expected.json
python - <<'PY'
import pathlib
for case, deltas, expect in [
  ("pass-pitr", [("    enabled: false", "    enabled: true"),
                 ("    window_minutes: null", "    window_minutes: 15"),
                 ("  rpo_minutes: 1440", "  rpo_minutes: 15")], []),
  ("fail-pitr-null-window", [("    enabled: false", "    enabled: true")], ["R13.3"]),
  ("fail-rpo-below-pitr-window", [("    enabled: false", "    enabled: true"),
                                  ("    window_minutes: null", "    window_minutes: 60"),
                                  ("  rpo_minutes: 1440", "  rpo_minutes: 15")], ["R13.4"]),
  ("fail-non-integer-rpo", [("  rpo_minutes: 1440", '  rpo_minutes: "24h"')], ["R13.5"]),
]:
    p = pathlib.Path(f"validators/registry/fixtures/r13/{case}/products/product-1/product.yaml")
    t = p.read_text()
    for a, b in deltas:
        t = t.replace(a, b)
    p.write_text(t)
    pathlib.Path(f"validators/registry/fixtures/r13/{case}/expected.json").write_text(
        '{"as_of":"2026-08-27","expect":%s}\n' % str(expect).replace("'", '"'))
PY
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r13_rpo_backup_frequency.py -q` | `7 passed` |
| 2 | `python -c "from validators.registry.rules import r13_rpo_backup_frequency as m; print(m.FREQUENCY_MINUTES)"` | `{'continuous': 0, 'hourly': 60, 'six-hourly': 360, 'daily': 1440, 'weekly': 10080}` |
| 3 | spec example is valid: the baseline fixture (`daily`, `rpo_minutes: 1440`) produces `[]` | `[]` — §44.1: "The example is internally possible by construction" |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r13_rpo_backup_frequency.py -q >/dev/null
  test "$(python -c "from validators.registry.rules import r13_rpo_backup_frequency as m;print(m.FREQUENCY_MINUTES[\"six-hourly\"])")" = "360"
  echo T14_PASS
'
```

**STOP rule.** If a live product declares a `backup_frequency` outside the five tokens, the rule is right and the contract is wrong. Do not widen the mapping to accommodate it. Ship the rule, file the blocker with `component: L1-phase-1` naming the product and the token, and quote §44.1's "the mapping above is the whole vocabulary".

---

## TASK L1-03-15 — R14 the revision integrity audit

**Size:** L **Depends on:** T00 (`framework_registry_path`), T01. **Slug:** `r14-revision-integrity`
**Creates:** `validators/registry/rules/r14_revision_integrity.py`, `validators/registry/diffgen.py`, `validators/registry/fixtures/r14/**`, `validators/registry/tests/test_r14_revision_integrity.py`. **Edits:** `rules_manifest.yaml`.

§77.5 states the split precisely, and this task implements **only the machine half**: "CI generates the diff of removed or changed protected entities … and blocks the change until every removal carries an intentional-change marker referencing a decision record. Semantic judgments … are a human review step performed on that flagged diff; **CI flags, it does not adjudicate**."

**Protected entities, transcribed verbatim from §77.5:** people, roles, KRAs, KPIs, weights, targets, stretch targets, rating-scale details, acceptance tests, invariants and access rules.

**Where the rule reads each one:**

| Protected entity | Source |
|---|---|
| people | `registries/people.yaml → people[].id` |
| roles | `registries/roles.yaml → roles[].id` |
| KRAs, KPIs, weights, targets, stretch targets, rating-scale details | the framework registry at the stamped `framework_registry_path` |
| acceptance tests | the `AT-###` identifiers declared in the control plane |
| invariants | the invariant numbers declared in the control plane |
| access rules | the entries at the stamped `control_classification_home` |

**How the diff is computed.** The rule is a **two-revision** rule, the only one in the suite. It takes `--base <git-ref>` (default `origin/integration`), reads each protected source at that ref via `git show <ref>:<path>`, reads the working-tree version, and computes the removed and changed key sets. `git` is invoked read-only; the rule never writes to the index or the working tree.

| Code | Condition | Spec |
|---|---|---|
| `R14.1` | a protected entity present at `--base` and absent in the working tree, with no matching entry in `intentional_changes[]` | §77.5 "blocks the change until every removal carries an intentional-change marker referencing a decision record" |
| `R14.2` | an `intentional_changes[]` marker whose `decision_record` field is absent, or points at a path with no `records/decisions/` prefix | §77.5 "referencing a decision record" |
| `R14.3` | a protected entity changed (weight, target, stretch target, rating-scale band) with no marker | §77.5 "removed **or changed** protected entities" |
| `R14.4` | a retired person, role, KRA or KPI removed outright rather than moved to inactive configuration with a `retirement_date` | §77.5 "its history moves to inactive configuration with a retirement date and remains queryable for the periods it governed"; §63; invariant 47 |
| `R14.5` | severity `info`, always emitted when `R14.1`/`R14.3` fire: `"human review required for semantic judgments (founder authority weakened? team lead authority widened?) — CI flags, it does not adjudicate (§77.5)"` | §77.5 |

The `intentional_changes[]` block lives beside the framework registry index and takes the shape:

```yaml
intentional_changes:
  - entity_kind: kpi          # person | role | kra | kpi | weight | target | stretch_target | rating_scale | acceptance_test | invariant | access_rule
    entity_key: "v1/qa/escaped-defect-rate"
    change: removed           # removed | changed
    decision_record: records/decisions/2026-08-02-framework-v2-activation.yaml
    retirement_date: 2026-08-01
```

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r14-revision-integrity
python -c "import yaml;print(yaml.safe_load(open('contracts/decisions/L1-03.yaml'))['framework_registry_path'])"
for c in pass-no-change pass-removal-with-marker fail-removal-no-marker fail-marker-no-decision-record fail-weight-changed-no-marker fail-hard-delete-not-retired; do
  bash validators/registry/tools/make-fixture.sh r14 "$c"
done
```

Because R14 is two-revision, its fixtures are **pairs**: each fixture dir gains a `_base/` subdirectory holding the prior state, and `tests/conftest.py` is extended in this task with a `run_cli_two_rev(fixture_dir)` helper that passes `--base-dir <fixture>/_base` (a directory alternative to `--base <git-ref>`, so tests need no git history). The rule must support both flags; `--base` and `--base-dir` are mutually exclusive and supplying both is exit `2`.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r14_revision_integrity.py -q` | `6 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r14/fail-removal-no-marker --base-dir validators/registry/fixtures/r14/fail-removal-no-marker/_base --as-of 2026-08-27 --format json \| python -c "import sys,json;print(sorted({f['code'] for f in json.load(sys.stdin)}))"` | `['R14.1', 'R14.5']` |
| 3 | CI-flags-not-adjudicates: `grep -ci "weakened\|widened" validators/registry/rules/r14_revision_integrity.py` matches only the `R14.5` message string, and no branch decides it | the rule contains no code path that classifies an authority change; assert by `python -c "from validators.registry.rules import r14_revision_integrity as m; print('adjudicate' not in dir(m))"` → `True` |
| 4 | `python -m validators.registry.cli --root . --rule R14 --base-dir . --as-of 2026-08-27 --format json; echo $?` | `2` — `--base-dir` equal to `--root` is a usage error, not a silent pass |
| 5 | read-only git: `grep -cE "git (add|commit|checkout|reset|clean)" validators/registry/rules/r14_revision_integrity.py validators/registry/diffgen.py` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r14_revision_integrity.py -q >/dev/null
  test "$(grep -cE "git (add|commit|checkout|reset|clean)" validators/registry/diffgen.py)" = "0"
  echo T15_PASS
'
```

**STOP rule.** If the framework registry does not exist at the stamped `framework_registry_path`, implement R14 over people, roles, access rules, acceptance tests and invariants only; emit `R14.6` severity `info` naming the absent framework source; and file the blocker with `component: L1-phase-1`. Do **not** author a framework registry from §78's snapshot — §78.1 is the *current configuration snapshot*, its content is Founder-owned (§52.6, §77.4: "The system never activates a framework change on its own authority"), and transcribing it here is exactly the authority overreach §77.4 forbids.

---

## TASK L1-03-16 — R15 illegal `availability` / `access_status` pairing

**Size:** S **Depends on:** T01. **Slug:** `r15-availability-pairing`
**Creates:** `validators/registry/rules/r15_availability_pairing.py`, `validators/registry/fixtures/r15/**`, `validators/registry/tests/test_r15_availability_pairing.py`. **Edits:** `rules_manifest.yaml`.

§7.1: "`availability` and `access_status` are two enums on one record, and not every pairing is legal. CI validates the combination and rejects the rest." The three legality clauses, verbatim:

1. `departed` implies `revoked`.
2. `revoked` implies `departed` **or** a non-employee past `end_date`.
3. `suspended` is valid only with `active` or `on_leave`.

| Code | Condition |
|---|---|
| `R15.1` | `availability: departed` with `access_status != revoked` |
| `R15.2` | `access_status: revoked` with `availability != departed` and not (`employment_type != employee` and `end_date < ctx.today`) |
| `R15.3` | `access_status: suspended` with `availability` not in `{active, on_leave}` |
| `R15.4` | `access_status: suspended` with no `review_by` date → §7.1 "Every suspension carries a mandatory **review-by date**" |
| `R15.5` | severity `warning`, `access_status: suspended` with `review_by` earlier than `ctx.today` → §7.1 "an unreviewed suspension past that date is Red drift". The drift **classification** is the reconciler's (L3); the date arithmetic is here |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r15-availability-pairing
for c in pass fail-departed-not-revoked fail-revoked-not-departed pass-revoked-nonemployee-past-end fail-suspended-with-departed fail-suspended-no-review-by warn-suspension-overdue; do
  bash validators/registry/tools/make-fixture.sh r15 "$c"
done
sed -i '0,/    availability: active/s//    availability: departed/' \
  validators/registry/fixtures/r15/fail-departed-not-revoked/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R15.1"]}\n' \
  > validators/registry/fixtures/r15/fail-departed-not-revoked/expected.json
sed -i '0,/    access_status: provisioned/s//    access_status: revoked/' \
  validators/registry/fixtures/r15/fail-revoked-not-departed/registries/people.yaml
printf '{"as_of":"2026-08-27","expect":["R15.2"]}\n' \
  > validators/registry/fixtures/r15/fail-revoked-not-departed/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r15_availability_pairing.py -q` | `7 passed` |
| 2 | `pass-revoked-nonemployee-past-end` (a `temporary_specialist` with `end_date: 2026-06-30`, `as_of 2026-08-27`, `revoked` + `active`) | `[]` — clause 2's second branch, which a naive implementation gets wrong |
| 3 | `python -m validators.registry.cli --root . --rule R15 --as-of 2026-08-27 --format json` at the repo root | `[]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r15_availability_pairing.py -q >/dev/null
  test "$(python -m validators.registry.cli --root validators/registry/fixtures/r15/pass-revoked-nonemployee-past-end --as-of 2026-08-27 --format json)" = "[]"
  echo T16_PASS
'
```

**STOP rule.** If `review_by` is not a property of the person record in `schemas/registry/people.v1.schema.json`, implement `R15.1`–`R15.3` and emit `R15.4` only when the key is present-but-null; then file the blocker with `component: L1-phase-2`, quoting §7.1's "Every suspension carries a mandatory review-by date". Do not add the property to the schema.

---

## TASK L1-03-17 — R16 `detection_expectation` differs from its derived value

**Size:** S **Depends on:** T01. **Slug:** `r16-detection-expectation`
**Creates:** `validators/registry/rules/r16_detection_expectation.py`, `validators/registry/fixtures/r16/**`, `validators/registry/tests/test_r16_detection_expectation.py`. **Edits:** `rules_manifest.yaml`.

**The mapping, transcribed verbatim from §42.2's table:**

| `support_model` | derived `detection_expectation` |
|---|---|
| `business-hours` | `next-business-morning` |
| `extended` | `rostered-window` |
| `24x7` | `continuous` |

§42.2: "`detection_expectation` is **derived, not authored**: this table is the mapping, its three tokens are the closed value set, and CI fails a contract whose declared value differs from the value its `support_model` implies."

| Code | Condition |
|---|---|
| `R16.1` | declared value differs from the derived value |
| `R16.2` | declared value outside the three-token closed set |
| `R16.3` | `support_model` outside `{business-hours, extended, 24x7}` (§15.1 closed set, §47.9 table) |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r16-detection-expectation
for c in pass fail-mismatch fail-unknown-token fail-unknown-support-model; do
  bash validators/registry/tools/make-fixture.sh r16 "$c"
done
sed -i 's/^  detection_expectation: next-business-morning$/  detection_expectation: continuous/' \
  validators/registry/fixtures/r16/fail-mismatch/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R16.1"]}\n' \
  > validators/registry/fixtures/r16/fail-mismatch/expected.json
sed -i 's/^  detection_expectation: next-business-morning$/  detection_expectation: best-effort/' \
  validators/registry/fixtures/r16/fail-unknown-token/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R16.2"]}\n' \
  > validators/registry/fixtures/r16/fail-unknown-token/expected.json
sed -i 's/^  support_model: business-hours$/  support_model: office-hours/' \
  validators/registry/fixtures/r16/fail-unknown-support-model/products/product-1/product.yaml
printf '{"as_of":"2026-08-27","expect":["R16.3"]}\n' \
  > validators/registry/fixtures/r16/fail-unknown-support-model/expected.json
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r16_detection_expectation.py -q` | `4 passed` |
| 2 | `python -c "from validators.registry.rules import r16_detection_expectation as m; print(m.DERIVED)"` | `{'business-hours': 'next-business-morning', 'extended': 'rostered-window', '24x7': 'continuous'}` |
| 3 | `fail-mismatch` message names both values | message contains `declared 'continuous'` and `derived 'next-business-morning'` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r16_detection_expectation.py -q >/dev/null
  test "$(python -c "from validators.registry.rules import r16_detection_expectation as m;print(m.DERIVED[\"24x7\"])")" = "continuous"
  echo T17_PASS
'
```

**STOP rule.** Do not implement the "worst-case undetected window" computation described in the same §42.2 paragraph. That number is consumed by §21.4's uptime-SLA feasibility row and belongs to the `check-commitment` tool, not to this rule. If you are computing intervals across the working calendar, you are in the wrong task.

---

## TASK L1-03-18 — R17 `founder_decision_delegate` naming a formal people decision

**Size:** S **Depends on:** T01. **Slug:** `r17-delegate-scope`
**Creates:** `validators/registry/rules/r17_delegate_scope.py`, `validators/registry/fixtures/r17/**`, `validators/registry/tests/test_r17_delegate_scope.py`. **Edits:** `rules_manifest.yaml`.

§10.1, `founder_decision_delegate` row: "**The delegable scope excludes every formal people decision** (Section 74.5) — recognition, promotion, role change affecting employment responsibility or status, hiring, formal warning, improvement plan, exit consideration, compensation and permanent headcount. A delegation naming one of them fails schema validation (**D108**)."

**The excluded set, transcribed verbatim, ten entries:** `recognition`, `promotion`, `role-change-affecting-employment-responsibility-or-status`, `hiring`, `formal-warning`, `improvement-plan`, `exit-consideration`, `compensation`, `permanent-headcount`. That is nine tokens; the tenth phrase in the sentence — "every formal people decision" — is the category, not a token, and the rule must **not** invent a tenth id.

| Code | Condition | Spec |
|---|---|---|
| `R17.1` | a `founder_decision_delegate` assignment whose `scope[]` contains any excluded token | §10.1, §14.2, §74.5, D108 |
| `R17.2` | a `founder_decision_delegate` assignment with `end_date: null` | §10.1 "Yes, mandatory `end_date`"; §10.3 "dated, scoped, reasoned, visible" |
| `R17.3` | a `founder_decision_delegate` assignment with no `scope` or no `reason` | §10.3 "Every delegation records: the capability delegated, the scope …, the duration, and the reason" |
| `R17.4` | any assignment type granting `people-intelligence` in its scope | §9.1 "`people-intelligence` … is not delegable (D109)"; §10.3 "Layer B access is not delegable by any assignment type (D109)" |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r17-delegate-scope
for c in pass fail-scope-promotion fail-no-end-date fail-no-reason fail-people-intelligence; do
  bash validators/registry/tools/make-fixture.sh r17 "$c"
done
python - <<'PY'
import pathlib
tmpl = """  - person: dev-b
    type: founder_decision_delegate
    start_date: 2026-08-01
    end_date: {end}
    scope: {scope}
    reason: {reason}
"""
cases = {
 "pass":                     dict(end="2026-09-30", scope="[budget, customer-commitment]", reason='"Founder travel"', expect=[]),
 "fail-scope-promotion":     dict(end="2026-09-30", scope="[budget, promotion]",           reason='"Founder travel"', expect=["R17.1"]),
 "fail-no-end-date":         dict(end="null",       scope="[budget]",                      reason='"Founder travel"', expect=["R17.2"]),
 "fail-no-reason":           dict(end="2026-09-30", scope="[budget]",                      reason="null",            expect=["R17.3"]),
 "fail-people-intelligence": dict(end="2026-09-30", scope="[people-intelligence]",         reason='"Founder travel"', expect=["R17.4"]),
}
for c, v in cases.items():
    p = pathlib.Path(f"validators/registry/fixtures/r17/{c}/products/product-1/product.yaml")
    t = p.read_text().replace("escalation: team_lead\n",
        tmpl.format(end=v["end"], scope=v["scope"], reason=v["reason"]) + "escalation: team_lead\n", 1)
    p.write_text(t)
    pathlib.Path(f"validators/registry/fixtures/r17/{c}/expected.json").write_text(
        '{"as_of":"2026-08-27","expect":%s}\n' % str(v["expect"]).replace("'", '"'))
PY
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r17_delegate_scope.py -q` | `5 passed` |
| 2 | `python -c "from validators.registry.rules import r17_delegate_scope as m; print(len(m.EXCLUDED_SCOPES))"` | `9` |
| 3 | `python -m validators.registry.cli --root validators/registry/fixtures/r17/fail-people-intelligence --rule R17 --as-of 2026-08-27 --format json \| python -c "import sys,json;print(json.load(sys.stdin)[0]['spec'])"` | contains `D109` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r17_delegate_scope.py -q >/dev/null
  test "$(python -c "from validators.registry.rules import r17_delegate_scope as m;print(len(m.EXCLUDED_SCOPES))")" = "9"
  echo T18_PASS
'
```

**STOP rule.** Do not extend the excluded set with anything §74.5 does not list, and do not soften it with a "unless a Founder decision record exists" branch. §10.1 says such a delegation "fails schema validation" with no escape hatch, and invariants 36 and 38 make it binding. If a live registry contains one, file the blocker with `component: L1-phase-1` rather than widening the rule.

---

## TASK L1-03-19 — R18 `recovery:` block with no `restore-production.yml`

**Size:** S **Depends on:** T01. **Slug:** `r18-restore-production-workflow`
**Creates:** `validators/registry/rules/r18_restore_production_workflow.py`, `validators/registry/fixtures/r18/**`, `validators/registry/tests/test_r18_restore_production_workflow.py`. **Edits:** `rules_manifest.yaml`.

§15.5: "A product with a `recovery:` block and no `restore-production.yml` workflow (Section 44.5)." §44.5: "A product with a `recovery:` block and no `restore-production.yml` fails contract validation (15.5)."

**Where the rule looks.** For product `<id>`, the workflow is expected at `products/<id>/.github/workflows/restore-production.yml` inside the control-plane fixture tree, and — in the live repo — at the path the product contract's `code.repositories[].name` implies. Because the live product repositories are **not** in the control-plane repository, the live check reads the declaration, not the remote file: the rule requires `recovery.restore_production_workflow` to name a path, and separately checks that path's existence **only when the path resolves inside `--root`**. Confirming the file exists in the product's own repository is actual-state work and belongs to L3's reconciler.

| Code | Condition |
|---|---|
| `R18.1` | `recovery:` present (and not `not-applicable`) with no `restore_production_workflow` declaration |
| `R18.2` | `restore_production_workflow` declared with a basename other than `restore-production.yml` — §44.5 names the file, and "generated from the template at product creation like every other required workflow" means the name is fixed, not chosen |
| `R18.3` | `restore_production_workflow` resolves inside `--root` and the file does not exist |

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-r18-restore-production-workflow
for c in pass fail-no-declaration fail-wrong-filename fail-declared-file-missing pass-recovery-not-applicable; do
  bash validators/registry/tools/make-fixture.sh r18 "$c"
done
for c in pass fail-wrong-filename fail-declared-file-missing; do
  printf '  restore_production_workflow: .github/workflows/restore-production.yml\n' \
    >> "validators/registry/fixtures/r18/$c/products/product-1/product.yaml"
done
sed -i 's|restore-production.yml$|restore-prod.yml|' \
  validators/registry/fixtures/r18/fail-wrong-filename/products/product-1/product.yaml
rm validators/registry/fixtures/r18/fail-declared-file-missing/products/product-1/.github/workflows/restore-production.yml
printf '{"as_of":"2026-08-27","expect":["R18.1"]}\n' > validators/registry/fixtures/r18/fail-no-declaration/expected.json
printf '{"as_of":"2026-08-27","expect":["R18.2"]}\n' > validators/registry/fixtures/r18/fail-wrong-filename/expected.json
printf '{"as_of":"2026-08-27","expect":["R18.3"]}\n' > validators/registry/fixtures/r18/fail-declared-file-missing/expected.json
```

For `pass-recovery-not-applicable`, replace the whole `recovery:` block with `recovery: not-applicable` plus `recovery_not_applicable_reason: "stateless static site"` and set `conformance_profile: static-site` (§44.1: "a `static-site` may declare `not-applicable`"; §15.7). `expect: []`.

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests/test_r18_restore_production_workflow.py -q` | `5 passed` |
| 2 | `python -m validators.registry.cli --root validators/registry/fixtures/r18/pass-recovery-not-applicable --rule R18 --as-of 2026-08-27 --format json` | `[]` |
| 3 | lane boundary: `grep -cE "requests|urllib|gh api|github.com" validators/registry/rules/r18_restore_production_workflow.py` | `0` — no remote lookup; that is L3 |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests/test_r18_restore_production_workflow.py -q >/dev/null
  test "$(grep -cE "requests|urllib|gh api" validators/registry/rules/r18_restore_production_workflow.py)" = "0"
  echo T19_PASS
'
```

**STOP rule.** If `recovery.restore_production_workflow` is not a property in `schemas/product/product.v2.schema.json`, R18 has nothing to read and §44.5's blocking claim is unenforceable from the control plane. File the blocker with `component: L1-phase-2`, quoting §44.5's sentence in full. Do not fall back to probing product repositories over the network — that crosses into L3.

---

## TASK L1-03-20 — Suite closure: manifest coverage, exit-code contract, citation lint

**Size:** M **Depends on:** T02–T19 all merged to `integration`. **Slug:** `suite-closure`
**Creates:** `validators/registry/tests/test_suite_closure.py`, `validators/registry/tests/test_exit_contract.py`, `validators/registry/tools/lint_citations.py`, `validators/registry/README.md` (rewrite). **Edits:** `validators/registry/rules_manifest.yaml` (final form).

**What this task proves.** That the suite is complete, closed and honest — and that L2 can wire it without reading any of the rule code.

`rules_manifest.yaml` final shape, one row per rule, eighteen rows:

```yaml
manifest_version: 1
rules:
  - id: R01
    module: rules/r01_schema_version.py
    name: "Multi-version schema validation and supported-version floor"
    severity: blocking
    spec_refs: ["§60.1", "§60.2", "§60.3", "§15.5", "invariant 73"]
    codes: [R01.1, R01.2, R01.3, R01.4, R01.5, R01.6]
    fixtures: fixtures/r01
  # ... R02 … R18
```

**`test_suite_closure.py` asserts, each an exact equality:**

1. The set of `id` values in the manifest equals the set of `RULE_ID` values discovered on disk equals `{R01 … R18}` — eighteen ids, no gaps, no extras.
2. Every manifest row's `module` file exists and every module's `SPEC_REFS` equals the row's `spec_refs`.
3. Every `codes[]` entry is emitted by at least one fixture in `fixtures/<rid>/*/expected.json` — a declared finding code with no fixture is an untested rule.
4. Every fixture directory has an `expected.json`, and every `expected.json` `expect` set is exactly reproduced by running the CLI over that fixture.
5. Every rule has at least one `pass*` fixture and at least one `fail*` fixture.

**`test_exit_contract.py` asserts the §0 table, which is L2's entire interface:**

| Input | Expected |
|---|---|
| baseline fixture | exit `0`, stdout `[]` |
| any `fail-*` fixture | exit `1` |
| `r06/info-no-records-root` | exit `0` with a non-empty `info` finding |
| `--root` pointing at a file, not a directory | exit `2` |
| a fixture containing malformed YAML | exit `2` — fail closed (§64.2) |
| `--rule R99` | exit `2` |

**`lint_citations.py`** greps every `SPEC_REFS` entry and every `spec` field emitted by every fixture, and asserts each is one of: `§<n>` / `§<n>.<n>` with `n` in the real section range `1–104`; `D<n>` with `n` in `1–112`; or `invariant <n>` with `n` in `1–111` (§101: "The catalogue contains **111 invariants**"). Any citation outside those ranges fails the lint. This is the mechanical guard against an invented section, D id or invariant number.

**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/03-suite-closure
python validators/registry/tools/lint_citations.py --root validators/registry; echo "LINT_EXIT=$?"
python -m pytest validators/registry/tests -q
python -m validators.registry.cli --root . --as-of 2026-08-27 --format text; echo "LIVE_EXIT=$?"
ruff check validators/registry
```

**Acceptance criteria**

| # | Provable by | Correct output |
|---|---|---|
| 1 | `python -m pytest validators/registry/tests -q` | exit `0`; the summary line reports at least `100 passed` |
| 2 | `python -c "import yaml;print(len(yaml.safe_load(open('validators/registry/rules_manifest.yaml'))['rules']))"` | `18` |
| 3 | `python -c "import yaml;print(sorted(r['id'] for r in yaml.safe_load(open('validators/registry/rules_manifest.yaml'))['rules']))"` | `['R01', 'R02', ..., 'R18']` with no gap |
| 4 | `python validators/registry/tools/lint_citations.py --root validators/registry; echo $?` | `0` |
| 5 | `python -m validators.registry.cli --root . --as-of 2026-08-27 --format text; echo $?` | `0` on a clean control plane; if non-zero, every finding is a **real** registry defect and is filed as a blocker, not suppressed |
| 6 | `ruff check validators/registry` | `All checks passed!` |
| 7 | `git diff --name-only origin/integration...HEAD \| grep -vE '^validators/registry/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP" && bash -c '
  set -e
  python -m pytest validators/registry/tests -q >/dev/null
  test "$(python -c "import yaml;print(len(yaml.safe_load(open(\"validators/registry/rules_manifest.yaml\"))[\"rules\"]))")" = "18"
  python validators/registry/tools/lint_citations.py --root validators/registry >/dev/null
  ruff check validators/registry >/dev/null
  echo T20_PASS
'
```

Correct output: the single line `T20_PASS`, exit `0`.

**STOP rule.** If criterion 5 fails against the live control plane, **do not add a suppression file, an allowlist, a `# noqa`-style skip, or an exception entry to make it green.** A finding on the live registry is the suite doing its job; §54.2 requires an expiry-bearing registry exception with a compensating control, and that is a Founder/Team Lead registry decision (§52.6), not a validator change. File the blocker with `component: L1-phase-1`, attach the JSON findings verbatim, and leave the suite failing.

---

## 5. Dependency graph and suggested execution order

```
T00 preflight
 └── T01 harness  ────────────────────────────────────────────────┐
      ├── T02 R01 schema versions                                 │
      ├── T03 R02 assignment person refs                          │
      ├── T04 R03 dependency service refs                         │
      ├── T05 R04 non-employee end_date                           │
      ├── T06 R05 expired assignment                              │
      ├── T07 R06 restore window        (also needs T00 key)      │
      ├── T08 R07 coverage rota                                   │
      ├── T09 R08 conflict_check                                  │
      ├── T10 R09 exception expiry                                │
      ├── T11 R10 control classification (also needs T00 key)     │
      ├── T12 R11 capability defined ──── T13 R12 dangerous role default
      ├── T14 R13 rpo vs backup frequency                         │
      ├── T15 R14 revision integrity     (also needs T00 key)     │
      ├── T16 R15 availability pairing                            │
      ├── T17 R16 detection expectation                           │
      ├── T18 R17 delegate scope                                  │
      └── T19 R18 restore-production workflow                     │
                                                                  │
T20 suite closure ◄───────────────────────────────────────────────┘
```

T02–T19 are independent of one another apart from T13's dependency on T12, so they may be executed in any order and each is a separate short-lived branch under one day (PARTITION.md branch model). T20 runs only after all of them are on `integration`.

| Task | Size | Blocks |
|---|---|---|
| T00 | S | everything |
| T01 | L | T02–T19 |
| T02 | L | T20 |
| T03 | M | T20 |
| T04 | S | T20 |
| T05 | S | T20 |
| T06 | S | T20 |
| T07 | M | T20 |
| T08 | L | T20 |
| T09 | S | T20 |
| T10 | S | T20 |
| T11 | M | T20 |
| T12 | M | T13, T20 |
| T13 | S | T20 |
| T14 | S | T20 |
| T15 | L | T20 |
| T16 | S | T20 |
| T17 | S | T20 |
| T18 | S | T20 |
| T19 | S | T20 |
| T20 | M | — |

Four L, four M, twelve S, one preflight. Subsystem B is sized **M** ("one to three weeks") in §99.2; this phase is the bulk of it.

## 6. Handover note for L2 (do not act on this — it is a statement of what L2 will find)

After T20 merges, the control-plane repository contains one gate entry point and one machine-readable inventory of what it enforces:

* `python -m validators.registry.cli --root . --as-of $(date -u +%F) --records-root <records-checkout> --format json`
* `validators/registry/rules_manifest.yaml` — eighteen rules, their codes, their severities and their spec citations.

L2 wires that command into `.github/workflows/**`. L1 does not, ever.
