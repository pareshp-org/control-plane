# L1 — PHASE 2 — JSON SCHEMAS

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 Registries & Contracts (Subsystems **A** — control-plane repository, and **B** — schema validation and CI gate engine, per spec Section 99.2).
**Repository:** `control-plane`.
**Branch prefix:** `lane/1/*` (PARTITION.md, "Branch & merge model").
**Paths this phase writes (all owned exclusively by L1 per PARTITION.md):**
`schemas/registry/**`, `schemas/product/**`, `validators/registry/**`.
**Paths this phase MUST NOT touch:** anything else. A PR touching a foreign path fails the lane-guard check (PARTITION.md rule 1). There are no exceptions.

This phase produces **one JSON Schema per registry or contract**, plus the fixture pairs and the schema-check harness that prove each schema accepts the spec's own example and rejects a defined violation. It produces **no validator business logic** — referential integrity, date arithmetic and the CI gate wiring are later phases of this lane and of L2.

---

## 0. Conventions that bind every task in this phase

### 0.1 Schema versioning convention (spec Section 60.2)

Section 60.2 ("Versioned contracts") states: *every contract schema carries a version*, and *simultaneous fleet migration is never required*. The migration flow it mandates is: write the v2 schema **alongside** v1 — do not replace; validator supports **both**; canary products migrate first; fleet migrates gradually; v1 support removed only after every product has migrated.

That flow is impossible if schema files are edited in place. This phase therefore fixes the following canonical schema path convention, and every task obeys it:

```
schemas/registry/<artifact-id>.json
```
<!-- path per FD-043 -->

* The canonical path for any schema is `schemas/registry/<artifact-id>.json` (path per FD-043). Both registry schemas (`schemas/registry/**`) and product schemas (`schemas/product/**`) use flat files under their respective owned trees — no subdirectory per version.
* `<artifact-id>` encodes the artifact name and version, e.g. `people.v1.schema`, `roles.v1.schema`, `product.v2.schema`.
* A schema file, once merged, is **append-only in spirit**: a breaking change creates a new file with an incremented version encoded in `<artifact-id>` (e.g. `people.v2.schema.json`) beside the old file. The old file is deleted only after `platform.yaml` has dropped that version from `supported_contract_versions` and no product declares it. <!-- path per FD-043 -->
* Every schema's `$id` is `https://control-plane.internal/schemas/registry/<artifact-id>.json`. <!-- path per FD-043 -->

The version field name per artifact, transcribed from the Section 60.2 table:

| Contract | File | Version field | This phase authors |
|---|---|---|---|
| Product Operating Contract | `product.yaml` | `contract_version` | v2 (see DECISION-L1-02-A) |
| Verification Contract | `verification/contract.yaml` | `contract_version` | not in this phase |
| People Registry | `people.yaml` | `registry_version` | v1 |
| Role Registry | `roles.yaml` | `registry_version` | v1 |
| Shared Service Contract | `service.yaml` | `service_version` | v1 |
| Reusable workflow interface | workflow tag | tag version | L2, not L1 |
| Operational record envelope | `records/**` | `record_schema_version` | L4, not L1 |
| Event envelope | `events/**` | `event_schema_version` | L4, not L1 |
| Event-type enum | `platform.yaml` | `platform_version` | v1 (the enum's *container*) |

Artifacts the Section 60.2 table does not list but Section 52.6 ("Registry of control-plane files") does — `topology.yaml`, `os-health.yaml`, `policies.yaml`, `exceptions.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml`, `tools.yaml`, `ai-toolchain.yaml`, `changes/*.yaml`, `scenarios/*.yaml` — carry `registry_version: 1` where the spec's own YAML block shows one (`topology.yaml` 66.2, `exceptions.yaml` 54.1, `policies.yaml` 55.1) and `registry_version` is **added** by this phase where the spec block shows none (`tools.yaml` 62.1, `economics.yaml` 68.1, `platform-roadmap.yaml` 59.3, `ai-toolchain.yaml` 36.3, `os-health.yaml`, `patterns.yaml`), because Section 52.6 states all hand-maintained artifacts are "schema-versioned by the versioned-contract mechanism of Section 60". Per-instance files (`changes/*.yaml`, `scenarios/*.yaml`) carry `manifest_version` and `scenario_version` respectively for the same reason.

### 0.2 DECLARED versus DERIVED — the annotation that makes it checkable

Invariant 46 (Section 101.7): *"Derived data is computed, never hand-maintained."* A schema that does not say which fields are which cannot enforce it. Every property in every schema this phase writes therefore carries a custom annotation:

* `"x-origin": "declared"` — a human writes it in the YAML file.
* `"x-origin": "derived"` — a job writes it; a hand edit is drift. Derived properties additionally carry `"readOnly": true` and `"x-derived-from": "<literal spec citation and producing job>"`.

The harness lints for this: a property object anywhere in a schema with no `x-origin` fails. Each task below carries an explicit DERIVED table; if a field is not in that table it is `declared`. **The executor never decides which is which** — the tables are the authority.

### 0.3 Rules the spec states that JSON Schema cannot express

Date comparisons, cross-file reference checks and registry lookups are not expressible in JSON Schema. Each schema root therefore carries `"x-residual-rule": [ ... ]` — an array of literal strings, each naming the spec rule and the section, deferred to the validator phase. The array may be empty but the key must be present. The harness lints for its presence.

### 0.4 Fixture convention

Every schema directory carries `fixtures/`:

* `fixtures/valid.yaml` — **must validate**. It is the spec's own example block, transcribed, with nothing added.
* `fixtures/invalid-<rule>.yaml` — **must fail validation**, one file per encoded rule.
<!-- # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/ -->

The suite runner enforces the naming: a file matching `valid*.yaml` that fails, or `invalid-*.yaml` that passes, is a suite failure. This makes "the schema works" provable by exit code.

### 0.5 Preflight guard — prepend to every task's command block

```bash
set -euo pipefail
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin
git checkout integration && git pull --ff-only origin integration
```

### 0.6 STOP rule that applies to every task in this phase

If any command in a task exits non-zero for a reason the task's own text does not anticipate, or if a file the task is told to create **already exists with different content**, the executor **stops, does not force, does not improvise, and files a blocker issue** using the template in Section 4 of this document. It does not edit a foreign path to make a command pass. It does not add a field the task table does not list. It does not delete a `v<N>/` directory.

---

## 1. Task table (execution order)

| Task | Creates | Size | Depends on |
|---|---|---|---|
| L1-02-01 | schema-check harness under `validators/registry/schema-check/` | M | — | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-02 | `schemas/registry/README.schema-versioning.md` + `schemas/registry/_common/v1/common.schema.json` | M | T01 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-03 | `schemas/registry/people/v1/people.schema.json` | L | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-04 | `schemas/registry/roles/v1/roles.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-05 | `schemas/product/product/v2/product.schema.json` | L | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-06 | `schemas/product/service/v1/service.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-07 | `schemas/registry/topology/v1/topology.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-08 | `schemas/registry/platform/v1/platform.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-09 | `schemas/registry/os-health/v1/os-health.schema.json` | L | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-10 | `schemas/registry/policies/v1/policies.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-11 | `schemas/registry/exceptions/v1/exceptions.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-12 | `schemas/registry/patterns/v1/patterns.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-13 | `schemas/registry/economics/v1/economics.schema.json` | L | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-14 | `schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-15 | `schemas/registry/tools/v1/tools.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-16 | `schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json` | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-17 | `schemas/registry/scenarios/v1/scenario.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-18 | `schemas/registry/changes/v1/change-manifest.schema.json` | M | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-02-19 | `schemas/registry/index.json` + phase gate | S | T03–T18 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

T03 through T18 are mutually independent and may be executed in any order after T02. They are separate branches and separate PRs.

---

## 2. Tasks

### L1-02-01 — Schema-check harness <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`validators/registry/schema-check/check.py`
`validators/registry/schema-check/requirements.txt`

**Size:** M **Depends on:** —

This subdirectory is claimed exclusively by this phase so it cannot collide with anything an earlier L1 phase placed directly in `validators/registry/`.

**Commands**

```bash
set -euo pipefail
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin
git checkout integration && git pull --ff-only origin integration

# --- STOP check ---
test -e validators/registry/schema-check && { echo "STOP: validators/registry/schema-check already exists"; exit 3; }

git checkout -b lane/1/02-t01-schema-check-harness
mkdir -p validators/registry/schema-check

cat > validators/registry/schema-check/requirements.txt <<'EOF'
jsonschema==4.23.0
pyyaml==6.0.2
EOF

cat > validators/registry/schema-check/check.py <<'EOF'
#!/usr/bin/env python3
"""L1 Phase 2 schema-check harness (Python).
Modes:
  --lint <schema.json>                     annotation lint only
  --schema <schema.json> --instance <f>    validate one instance
  --suite                                  every schema in schemas/registry/index.json against its fixtures
Exit 0 = PASS, 1 = FAIL, 2 = usage/IO error.
"""
import sys, os, json, pathlib

try:
    import jsonschema
    import yaml
except ImportError as e:
    print(f"ERROR missing dependency: {e} -- run: pip install jsonschema pyyaml")
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent


def read_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def read_instance(p):
    raw = pathlib.Path(p).read_text(encoding="utf-8")
    if str(p).endswith(".json"):
        return json.loads(raw)
    return yaml.safe_load(raw)


ALLOWED_ORIGINS = {"declared", "derived"}


def lint(schema_path):
    s = read_json(schema_path)
    problems = []
    if "$id" not in s:
        problems.append("root: missing $id")
    if "$schema" not in s:
        problems.append("root: missing $schema")
    if not isinstance(s.get("x-residual-rule"), list):
        problems.append("root: missing x-residual-rule array")

    def walk(node, ptr):
        if not isinstance(node, dict):
            return
        if isinstance(node.get("properties"), dict):
            for k, v in node["properties"].items():
                p = f"{ptr}/properties/{k}"
                if not isinstance(v, dict):
                    problems.append(f"{p}: not a schema object")
                    continue
                if v.get("x-origin") not in ALLOWED_ORIGINS:
                    problems.append(f'{p}: x-origin must be "declared" or "derived"')
                if v.get("x-origin") == "derived":
                    if v.get("readOnly") is not True:
                        problems.append(f"{p}: derived property must set readOnly:true")
                    xdf = v.get("x-derived-from", "")
                    if not isinstance(xdf, str) or len(xdf) < 10:
                        problems.append(
                            f"{p}: derived property must carry x-derived-from citing the spec section"
                        )
        for v in node.values():
            walk(v, ptr)

    walk(s, "#")
    if problems:
        for p in problems:
            print(f"LINT-FAIL {p}")
        return False
    rel = pathlib.Path(schema_path).relative_to(ROOT)
    print(f"LINT-OK {rel}")
    return True


def _make_validator(schema_path):
    s = read_json(schema_path)
    common_path = (
        ROOT / "schemas" / "registry" / "_common" / "v1" / "common.schema.json"
    )
    store = {}
    if common_path.exists():
        cs = read_json(common_path)
        store[cs["$id"]] = cs
    resolver = jsonschema.RefResolver.from_schema(s, store=store)
    return jsonschema.Draft202012Validator(s, resolver=resolver)


def validate_one(schema_path, instance_path):
    try:
        validator = _make_validator(schema_path)
        instance = read_instance(instance_path)
        errors = list(validator.iter_errors(instance))
        for e in errors:
            print(f"ERR {e.json_path or '/'} {e.message}")
        return len(errors) == 0
    except Exception as e:
        print(f"ERROR {e}")
        return False


def suite():
    idx_path = ROOT / "schemas" / "registry" / "index.json"
    if not idx_path.exists():
        print("SUITE-FAIL missing schemas/registry/index.json")
        return False
    idx = read_json(idx_path)
    ok = True
    checked = 0
    for entry in idx["schemas"]:
        schema_path = ROOT / entry["schema"]
        if not schema_path.exists():
            print(f'SUITE-FAIL missing {entry["schema"]}')
            ok = False
            continue
        if not lint(schema_path):
            ok = False
        fixture_dir = schema_path.parent / "fixtures"
        if not fixture_dir.exists():
            print(f'SUITE-FAIL missing fixtures for {entry["schema"]}')
            ok = False
            continue
        files = sorted(f.name for f in fixture_dir.iterdir() if f.suffix == ".yaml")
        if not any(f.startswith("valid") for f in files) or not any(
            f.startswith("invalid-") for f in files
        ):
            print(
                f'SUITE-FAIL {entry["schema"]} needs >=1 valid*.yaml and >=1 invalid-*.yaml'
            )
            ok = False
        for f in files:
            expect_valid = f.startswith("valid")
            got = validate_one(schema_path, fixture_dir / f)
            checked += 1
            if got != expect_valid:
                label = "PASS" if expect_valid else "FAIL"
                print(f'SUITE-FAIL {entry["schema"]} :: {f} expected {label}')
                ok = False
    print(f"SUITE-CHECKED {checked}")
    print("SUITE-OK" if ok else "SUITE-FAIL")
    return ok


def _arg_of(args, name):
    try:
        i = args.index(name)
        return args[i + 1]
    except (ValueError, IndexError):
        return None


def main():
    args = sys.argv[1:]
    try:
        if "--suite" in args:
            sys.exit(0 if suite() else 1)
        if "--lint" in args:
            sys.exit(0 if lint(os.path.abspath(_arg_of(args, "--lint"))) else 1)
        s = _arg_of(args, "--schema")
        i = _arg_of(args, "--instance")
        if not s or not i:
            print(
                "USAGE: check.py [--suite | --lint <schema> | --schema <schema> --instance <file>]"
            )
            sys.exit(2)
        ok = validate_one(os.path.abspath(s), os.path.abspath(i))
        print("VALID" if ok else "INVALID")
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"ERROR {e}")
        sys.exit(2)


main()
EOF

pip install -r validators/registry/schema-check/requirements.txt
git add validators/registry/schema-check
git commit -m "L1-02-01: schema-check harness for control-plane registry schemas"
git push -u origin lane/1/02-t01-schema-check-harness
gh pr create --base integration --head lane/1/02-t01-schema-check-harness \
  --title "L1-02-01 schema-check harness" \
  --body "Phase 2 Lane 1. Adds validators/registry/schema-check/ (jsonschema + pyyaml). No schemas yet."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Harness files exist | `ls validators/registry/schema-check/check.py validators/registry/schema-check/requirements.txt` | both paths echoed, exit 0 |
| 2 | Harness runs and reports usage | `python3 validators/registry/schema-check/check.py; echo "EXIT=$?"` | `EXIT=2` |
| 3 | Suite mode fails cleanly with no index yet | `python3 validators/registry/schema-check/check.py --suite; echo "EXIT=$?"` | contains `SUITE-FAIL missing schemas/registry/index.json`, `EXIT=1` |
| 4 | No foreign path touched | `git diff --name-only integration...HEAD \| grep -cv '^validators/registry/schema-check/'` | `0` |
| 5 | `__pycache__` not committed | `git ls-files \| grep -c '__pycache__' \|\| true` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
python3 validators/registry/schema-check/check.py --suite; echo "EXIT=$?"
git diff --name-only integration...HEAD | grep -cv '^validators/registry/schema-check/'
git ls-files | grep -c '__pycache__' || true
```

Correct output: the first line block ends `SUITE-FAIL missing schemas/registry/index.json` then `EXIT=1`; the second command prints `0`; the third prints `0`.

**STOP rule** — `pip install` fails, or `validators/registry/schema-check` already exists. Do not switch package manager, do not vendor a different validator, do not change the pinned versions. File a blocker.

---

### L1-02-02 — Versioning convention document and shared `$defs` <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/README.schema-versioning.md`
`schemas/registry/_common/v1/common.schema.json`
`schemas/registry/_common/v1/fixtures/valid.yaml`
`schemas/registry/_common/v1/fixtures/invalid-capability-not-in-vocabulary.yaml`

**Size:** M **Depends on:** L1-02-01 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

`common.schema.json` holds only `$defs` that two or more later schemas reference. It defines no top-level object, so its fixtures exercise the `$defs` through a thin wrapper the schema itself declares.

**Vocabularies transcribed (do not add, do not omit, do not rename):**

*Capability vocabulary — spec Section 9, the complete table. Section 9.1: "A capability appearing in a `roles.yaml` default, in a `people.yaml` grant, or in any assignment type without a row in this table fails control-plane CI validation."* (27 tokens)
`backend`, `frontend`, `mobile`, `data`, `code-review`, `architecture`, `security-review`, `migration-review`, `verification`, `uat`, `release-signoff`, `production-approval`, `incident-response`, `plan-approval`, `reviewer-matrix-change`, `platform-change-approval`, `platform-admin`, `devops`, `lifecycle-decision`, `escalation`, `mobile-release`, `exceptional-approval`, `people-intelligence`, `strategy`, `budget`, `hiring`, `customer-commitment`

*Dangerous capability subset — spec Section 8 (D106): "granted only by explicit entry in `people.yaml`, never by role".* (8 tokens)
`production-approval`, `platform-change-approval`, `platform-admin`, `security-review`, `migration-review`, `exceptional-approval`, `lifecycle-decision`, `people-intelligence`

*Assignment types — spec Section 10.1, "All assignment types in the operating system, in one table (17 types)".*
`primary_owner`, `cross_reviewer`, `backup_owner`, `temporary_contributor`, `incident_responder`, `verification_responsibility`, `architecture_responsibility`, `production_approval_delegate`, `security_reviewer`, `plan_approval_delegate`, `incident_coordination_delegate`, `domain_lead`, `founder_decision_delegate`, `registry_owner_delegate`, `verification_delegate`, `cross_review_shadow`, `mentor`

*Drift classes — spec Section 6.7: "Drift classes: Green, Amber, Red, Blocking." Section 6.7 also states a class cell naming anything else fails control-plane CI validation.*

*Attention categories — spec Section 67.2, "Every attention hour carries exactly one of eight categories": Engineering, Review, Verification, Planning, Architecture, Incident, Operational, Coordination (lower-cased as identifiers).*

*Metric declaration — spec Section 84.6: "definition; source; time window; baseline; expected interpretation; known limitations; owner; and defined action on breach. This is the only list of required metric attributes in this system." Section 84.6 also states `known_limitations` is never empty and declares `none-known` where there is none.*

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin
git checkout integration && git pull --ff-only origin integration

test -e schemas/registry/_common && { echo "STOP: schemas/registry/_common already exists"; exit 3; }
test -f validators/registry/schema-check/check.py || { echo "STOP: L1-02-01 not merged"; exit 3; }

git checkout -b lane/1/02-t02-common-defs
mkdir -p schemas/registry/_common/v1/fixtures

cat > schemas/registry/README.schema-versioning.md <<'EOF'
# Control-plane schema versioning convention

Authority: spec Section 60.2, "Versioned contracts". Every contract schema carries a version;
simultaneous fleet migration is never required.

## Layout

    schemas/<family>/<artifact>/v<N>/<artifact>.schema.json
    schemas/<family>/<artifact>/v<N>/fixtures/valid.yaml
    schemas/<family>/<artifact>/v<N>/fixtures/invalid-<rule>.yaml
    # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/

`<family>` is `registry` or `product`. `<N>` is the contract version integer carried by the
artifact's own version field.

## Version field per artifact (Section 60.2 table)

| Contract | File | Version field |
|---|---|---|
| Product Operating Contract | product.yaml | contract_version |
| Verification Contract | verification/contract.yaml | contract_version |
| People Registry | people.yaml | registry_version |
| Role Registry | roles.yaml | registry_version |
| Shared Service Contract | service.yaml | service_version |
| Reusable workflow interface | workflow tag | tag version |
| Operational record envelope | records/** | record_schema_version |
| Event envelope | events/** | event_schema_version |
| Event-type enum | platform.yaml | platform_version |

Artifacts listed only in Section 52.6 carry `registry_version`; per-instance manifests carry
`manifest_version` (changes/*.yaml) or `scenario_version` (scenarios/*.yaml).

## The migration flow (Section 60.2, verbatim shape)

    Schema change proposed -> write the v2 schema ALONGSIDE v1, do not replace ->
    validator supports BOTH v1 and v2 -> write the migration ->
    canary products migrate first -> verify -> fleet migrates gradually,
    each product on its own schedule -> v1 deprecation deadline set and published ->
    v1 support removed only after every product has migrated

Binding consequences for this repository:

1. A breaking schema change NEVER edits `v<N>/`. It creates `v<N+1>/` beside it.
2. `platform.yaml` `supported_contract_versions` is the list of versions the validator loads.
   A version present on disk but absent from that list is not loaded.
3. A `v<N>/` directory is deleted only after `<N>` has been dropped from
   `supported_contract_versions` and no artifact declares it. Products may temporarily remain
   on an older supported version; that state is `platform_compatibility: transitional`
   (Section 60.3), and requires a named migration owner, a target version and a deadline.
4. A contract version below the supported floor is `unsupported` and blocks deployment
   until migrated (Section 60.2).

Backing invariant: Section 101.10, invariant 73 — "Contract schemas are versioned, and
simultaneous fleet migration is never required." Acceptance test AT-025.

## DECLARED versus DERIVED

Every property object carries `x-origin`: `"declared"` (a human writes it) or `"derived"`
(a job writes it; a hand edit is drift). Derived properties also carry `readOnly: true` and
`x-derived-from` citing the spec section and the producing job. Backing invariant:
Section 101.7, invariant 46 — "Derived data is computed, never hand-maintained."

## Residual rules

Every schema root carries `x-residual-rule`: an array of literal strings naming the spec rules
that JSON Schema cannot express (date arithmetic, cross-file reference checks, registry
lookups). The array may be empty; the key may not be absent.
EOF

cat > schemas/registry/_common/v1/common.schema.json <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json",
  "title": "Control-plane shared definitions",
  "x-spec": "Sections 6.7, 9, 10.1, 50.1, 67.2, 84.6",
  "x-residual-rule": [],
  "type": "object",
  "properties": {
    "probe": { "x-origin": "declared", "description": "Wrapper used only by this schema's own fixtures.", "type": "object",
      "properties": {
        "capability": { "x-origin": "declared", "$ref": "#/$defs/capability" },
        "assignment": { "x-origin": "declared", "$ref": "#/$defs/assignment" },
        "drift_class": { "x-origin": "declared", "$ref": "#/$defs/driftClass" },
        "metric": { "x-origin": "declared", "$ref": "#/$defs/metricDeclaration" }
      },
      "required": ["capability"], "additionalProperties": false }
  },
  "required": ["probe"],
  "additionalProperties": false,
  "$defs": {
    "registryVersion": { "type": "integer", "minimum": 1 },
    "identifier": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,63}$" },
    "personId": { "$ref": "#/$defs/identifier" },
    "productId": { "$ref": "#/$defs/identifier" },
    "roleId": { "type": "string", "pattern": "^[a-z][a-z0-9_]{1,63}$" },
    "isoDate": { "type": "string", "format": "date" },
    "isoDateTime": { "type": "string", "format": "date-time" },
    "nullableIsoDate": { "oneOf": [ { "type": "string", "format": "date" }, { "type": "null" } ] },
    "ianaTimezone": { "type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_+-]*/[A-Za-z0-9_+/-]+$" },
    "hhmm": { "type": "string", "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$" },
    "weekday": { "type": "string", "enum": ["mon","tue","wed","thu","fri","sat","sun"] },
    "capability": { "type": "string", "enum": [
      "backend","frontend","mobile","data","code-review","architecture","security-review",
      "migration-review","verification","uat","release-signoff","production-approval",
      "incident-response","plan-approval","reviewer-matrix-change","platform-change-approval",
      "platform-admin","devops","lifecycle-decision","escalation","mobile-release",
      "exceptional-approval","people-intelligence","strategy","budget","hiring","customer-commitment" ] },
    "dangerousCapability": { "type": "string", "enum": [
      "production-approval","platform-change-approval","platform-admin","security-review",
      "migration-review","exceptional-approval","lifecycle-decision","people-intelligence" ] },
    "safeRoleDefaultCapability": {
      "allOf": [ { "$ref": "#/$defs/capability" }, { "not": { "$ref": "#/$defs/dangerousCapability" } } ] },
    "assignmentType": { "type": "string", "enum": [
      "primary_owner","cross_reviewer","backup_owner","temporary_contributor","incident_responder",
      "verification_responsibility","architecture_responsibility","production_approval_delegate",
      "security_reviewer","plan_approval_delegate","incident_coordination_delegate","domain_lead",
      "founder_decision_delegate","registry_owner_delegate","verification_delegate",
      "cross_review_shadow","mentor" ] },
    "mandatoryEndDateAssignmentType": { "type": "string", "enum": [
      "temporary_contributor","production_approval_delegate","plan_approval_delegate",
      "incident_coordination_delegate","founder_decision_delegate","registry_owner_delegate",
      "verification_delegate","cross_review_shadow","mentor" ] },
    "assignment": {
      "type": "object",
      "properties": {
        "person": { "x-origin": "declared", "$ref": "#/$defs/personId" },
        "type": { "x-origin": "declared", "$ref": "#/$defs/assignmentType" },
        "start_date": { "x-origin": "declared", "$ref": "#/$defs/isoDate" },
        "end_date": { "x-origin": "declared", "$ref": "#/$defs/nullableIsoDate" },
        "reason": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "scope": { "x-origin": "declared", "type": "array", "items": { "$ref": "#/$defs/identifier" } }
      },
      "required": ["person","type","start_date","end_date"],
      "additionalProperties": false,
      "allOf": [ {
        "if": { "properties": { "type": { "$ref": "#/$defs/mandatoryEndDateAssignmentType" } }, "required": ["type"] },
        "then": { "properties": { "end_date": { "type": "string", "format": "date" } } }
      } ]
    },
    "driftClass": { "type": "string", "enum": ["Green","Amber","Red","Blocking"] },
    "attentionCategory": { "type": "string", "enum": [
      "engineering","review","verification","planning","architecture","incident","operational","coordination" ] },
    "budgetBand": {
      "type": "object",
      "properties": {
        "currency": { "x-origin": "declared", "type": "string", "pattern": "^[A-Z]{3}$" },
        "expected": { "x-origin": "declared", "type": "number", "minimum": 0 },
        "ceiling": { "x-origin": "declared", "type": "number", "minimum": 0 }
      },
      "required": ["currency","expected","ceiling"],
      "additionalProperties": false
    },
    "metricDeclaration": {
      "description": "The eight attributes of Section 84.6. This is the only list of required metric attributes in this system.",
      "type": "object",
      "properties": {
        "definition": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "source": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "time_window": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "baseline": { "x-origin": "declared", "type": ["string","number","null"] },
        "expected_interpretation": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "known_limitations": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "owner": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "action_on_breach": { "x-origin": "declared", "type": "string", "minLength": 1 }
      },
      "required": ["definition","source","time_window","baseline","expected_interpretation","known_limitations","owner","action_on_breach"],
      "additionalProperties": false
    }
  }
}
JSON

cat > schemas/registry/_common/v1/fixtures/valid.yaml <<'EOF'
probe:
  capability: code-review
  assignment:
    person: dev-a
    type: primary_owner
    start_date: 2025-06-01
    end_date: null
  drift_class: Amber
  metric:
    definition: "Median time from plan submission to Gate 1 approval"
    source: "DevLake"
    time_window: "30 days rolling"
    baseline: null
    expected_interpretation: "Falling is better; a rise indicates planning-capacity pressure"
    known_limitations: "none-known"
    owner: "founder"
    action_on_breach: "Raise SIG-07 at its declared class"
EOF

cat > schemas/registry/_common/v1/fixtures/invalid-capability-not-in-vocabulary.yaml <<'EOF'
probe:
  capability: deploy-anything
EOF

python3 validators/registry/schema-check/check.py --lint schemas/registry/_common/v1/common.schema.json
python3 validators/registry/schema-check/check.py --schema schemas/registry/_common/v1/common.schema.json --instance schemas/registry/_common/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema schemas/registry/_common/v1/common.schema.json --instance schemas/registry/_common/v1/fixtures/invalid-capability-not-in-vocabulary.yaml && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry
git commit -m "L1-02-02: schema versioning convention and shared \$defs"
git push -u origin lane/1/02-t02-common-defs
gh pr create --base integration --head lane/1/02-t02-common-defs \
  --title "L1-02-02 versioning convention + common \$defs" \
  --body "Phase 2 Lane 1. Section 60.2 versioning convention; Section 9 / 10.1 / 6.7 / 67.2 / 84.6 vocabularies."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| 1 | Convention doc exists and cites 60.2 | `grep -c 'Section 60.2' schemas/registry/README.schema-versioning.md` | integer `>= 1` (prints `2`) |
| 2 | Schema lints | `python3 validators/registry/schema-check/check.py --lint schemas/registry/_common/v1/common.schema.json` | `LINT-OK schemas/registry/_common/v1/common.schema.json`, exit 0 |
| 3 | Capability enum has exactly 27 entries | `python3 -c "import json; s=json.load(open('schemas/registry/_common/v1/common.schema.json')); print(len(s['\$defs']['capability']['enum']))"` | `27` |
| 4 | Dangerous subset has exactly 8 | `python3 -c "import json; s=json.load(open('schemas/registry/_common/v1/common.schema.json')); print(len(s['\$defs']['dangerousCapability']['enum']))"` | `8` |
| 5 | Assignment types exactly 17 | `python3 -c "import json; s=json.load(open('schemas/registry/_common/v1/common.schema.json')); print(len(s['\$defs']['assignmentType']['enum']))"` | `17` |
| 6 | Positive fixture validates | `python3 validators/registry/schema-check/check.py --schema schemas/registry/_common/v1/common.schema.json --instance schemas/registry/_common/v1/fixtures/valid.yaml` | `VALID`, exit 0 |
| 7 | Negative fixture rejected | as above with `invalid-capability-not-in-vocabulary.yaml` | `INVALID`, exit 1 |
| 8 | No foreign path | `git diff --name-only integration...HEAD \| grep -cv '^schemas/registry/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
python3 validators/registry/schema-check/check.py --lint schemas/registry/_common/v1/common.schema.json
python3 -c "import json; s=json.load(open('schemas/registry/_common/v1/common.schema.json')); print(len(s['\$defs']['capability']['enum']), len(s['\$defs']['dangerousCapability']['enum']), len(s['\$defs']['assignmentType']['enum']))"
git diff --name-only integration...HEAD | grep -cv '^schemas/registry/'
```

Correct output: `LINT-OK …common.schema.json`; then `27 8 17`; then `0`.

**STOP rule** — any count differs from 27 / 8 / 17. Do not add or remove a token to make the count match; the enum is a transcription of Section 9, Section 8 (D106) and Section 10.1. File a blocker naming the token that differs.

---

### L1-02-03 — `people.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/people/v1/people.schema.json`
`schemas/registry/people/v1/fixtures/valid.yaml`
`schemas/registry/people/v1/fixtures/invalid-non-employee-null-end-date.yaml`
`schemas/registry/people/v1/fixtures/invalid-departed-not-revoked.yaml`
`schemas/registry/people/v1/fixtures/invalid-utc-offset-timezone.yaml`
`schemas/registry/people/v1/fixtures/invalid-fte-above-one.yaml`

**Size:** L **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 7 (YAML block), 7.1 (registry rules), 7.2 (leave), 7.3 (work arrangement, D111), Section 9 (capability vocabulary), Section 47.9 (rota block), Section 52.6 (`people.yaml` row).

**Field transcription — top level**

| Field | Type | Enumerated values / constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1`; Section 60.2 names this the People Registry version field | declared |
| `people` | array of person | min 1 | declared |
| `rotas` | array of rota | optional; Section 47.9 / 52.6: per-product funded-coverage rota | declared |

**Field transcription — `people[]`**

| Field | Type | Enumerated values / constraint | Origin |
|---|---|---|---|
| `id` | string | `personId` pattern; "stable identifier, never reused" (7) | declared |
| `display_name` | string | minLength 1 | declared |
| `github_login` | string | `^[A-Za-z0-9](?:[A-Za-z0-9]\|-){0,38}$` | declared |
| `role` | string | `roleId`; must exist in `roles.yaml` (residual rule) | declared |
| `employment_type` | string | `employee` \| `contractor` \| `intern` \| `temporary_specialist` \| `consultant`; 7.1 "Employment types are open-ended" — the schema keeps the five as the current closed set and records extensibility as a residual rule | declared |
| `capabilities` | array | items = `common#/$defs/capability`, uniqueItems (Section 9.1 closes the vocabulary) | declared |
| `ai_runtime` | string \| null | "from the approved runtime list"; cross-checked against `ai-toolchain.yaml` (residual rule) | declared |
| `availability` | string | `active` \| `on_leave` \| `departing` \| `departed` | **derived** |
| `access_status` | string | `pending` \| `provisioned` \| `suspended` \| `revoked` | **derived** |
| `work_arrangement` | object | see below (7.3) | declared |
| `start_date` | date | | declared |
| `end_date` | date \| null | "required for non-employees" (7 comment; 7.1 rule) | declared |
| `scope` | object | `{ products: [productId], repositories_only: boolean }` — the temporary-specialist scoping shown in the Section 7 block | declared |
| `suspension` | object | `{ review_by: date, reinstatement_decision_record: string\|null }` — 7.1: "Every suspension carries a mandatory review-by date"; required when `access_status: suspended` | declared |

**`work_arrangement` (Section 7.3, D111)**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `timezone` | string | IANA identifier, **never a UTC offset** (7.3 binding rule) — enforced by the `ianaTimezone` pattern | declared |
| `arrangement` | string | `onsite` \| `hybrid` \| `remote` | declared |
| `schedule` | object | keys `mon`..`sun`; each `{ start: HH:MM, end: HH:MM }`; "omit a day to declare it non-working" → no required days, `additionalProperties: false` | declared |
| `fte` | number | `0 < fte <= 1` → `exclusiveMinimum: 0`, `maximum: 1` | declared |
| `public_holiday_set` | string | the calendar its non-working days come from | declared |
| `accepted_coverage_window` | object \| null | `null` means not on a rota; object = `{ days: [weekday], start, end, timezone }` | declared |

**`rotas[]` (Section 47.9)**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `product` | string | `productId` | declared |
| `members[].person` | string | `personId` | declared |
| `members[].accepted_window` | object | `{ days: [weekday], start: HH:MM, end: HH:MM, timezone: IANA }` | declared |
| `members[].paging_path` | string | minLength 1 — 47.9: "an unnamed paging path … fails validation" | declared |
| `members[].funding_decision_record` | string | minLength 1 — 47.9 "the funding decision record" | declared |

**DERIVED fields (mark `readOnly: true` + `x-derived-from`)**

| Field | Producing job | Citation |
|---|---|---|
| `people[].availability` | reconciliation, from leave records | 7.2 — "reconciliation (Section 53) transitions it against the leave records … so that dashboards, capacity forecasts and reviewer availability never depend on someone remembering to flip a flag" |
| `people[].access_status` | reconciliation / provisioning | 7.1 — "Expired access is revoked by the reconciliation job, not by someone remembering" |

**Schema-encoded rules (all from 7.1 / 7.3)**

1. `employment_type != employee` ⇒ `end_date` is a date, not null.
2. `availability == departed` ⇒ `access_status == revoked`.
3. `access_status == suspended` ⇒ `availability` in `[active, on_leave]`, and `suspension.review_by` present.
4. `access_status == revoked` ⇒ `availability == departed` **or** (`employment_type != employee` **and** `end_date` is a date).
5. `timezone` matches the IANA pattern (rejects `+05:30`, `UTC+5`).
6. `0 < fte <= 1`.

**`x-residual-rule` (verbatim strings to place in the schema)**

* `"Section 7.1: revoked with a non-employee requires end_date in the PAST; date arithmetic is not expressible in JSON Schema."`
* `"Section 7.1: role must name an existing entry in roles.yaml."`
* `"Section 7.1: ai_runtime must name an approved runtime in ai-toolchain.yaml."`
* `"Section 7.1: employment types are open-ended; adding a type is a registry change, and this enum is widened by a v2 schema, never by an in-place edit (Section 60.2)."`
* `"Section 7.1: an unreviewed suspension past suspension.review_by is Red drift."`
* `"Section 47.9: the union of accepted windows of active rota members must cover the product's declared coverage_window."`

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/people && { echo "STOP: schemas/registry/people already exists"; exit 3; }

git checkout -b lane/1/02-t03-people-schema
mkdir -p schemas/registry/people/v1/fixtures

cat > schemas/registry/people/v1/people.schema.json <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/people/v1/people.schema.json",
  "title": "People Registry (people.yaml) v1",
  "x-spec": "Sections 7, 7.1, 7.2, 7.3 (D111), 9, 47.9, 52.6, 60.2",
  "x-residual-rule": [
    "Section 7.1: revoked with a non-employee requires end_date in the PAST; date arithmetic is not expressible in JSON Schema.",
    "Section 7.1: role must name an existing entry in roles.yaml.",
    "Section 7.1: ai_runtime must name an approved runtime in ai-toolchain.yaml.",
    "Section 7.1: employment types are open-ended; adding a type is a registry change, and this enum is widened by a v2 schema, never by an in-place edit (Section 60.2).",
    "Section 7.1: an unreviewed suspension past suspension.review_by is Red drift.",
    "Section 47.9: the union of accepted windows of active rota members must cover the product's declared coverage_window."
  ],
  "type": "object",
  "properties": {
    "registry_version": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/registryVersion" },
    "people": { "x-origin": "declared", "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/person" } },
    "rotas": { "x-origin": "declared", "type": "array", "items": { "$ref": "#/$defs/rota" } }
  },
  "required": ["registry_version", "people"],
  "additionalProperties": false,
  "$defs": {
    "C": { "$comment": "shorthand base for common refs" },
    "person": {
      "type": "object",
      "properties": {
        "id": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/personId" },
        "display_name": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "github_login": { "x-origin": "declared", "type": "string", "pattern": "^[A-Za-z0-9](?:[A-Za-z0-9]|-){0,38}$" },
        "role": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/roleId" },
        "employment_type": { "x-origin": "declared", "type": "string", "enum": ["employee","contractor","intern","temporary_specialist","consultant"] },
        "capabilities": { "x-origin": "declared", "type": "array", "uniqueItems": true, "items": { "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/capability" } },
        "ai_runtime": { "x-origin": "declared", "type": ["string","null"] },
        "availability": { "x-origin": "derived", "readOnly": true,
          "x-derived-from": "Section 7.2: reconciliation transitions availability against the leave records; producing job = reconciliation (Section 53).",
          "type": "string", "enum": ["active","on_leave","departing","departed"] },
        "access_status": { "x-origin": "derived", "readOnly": true,
          "x-derived-from": "Section 7.1: expired access is revoked by the reconciliation job; producing job = reconciliation and provisioning (Sections 53, 99.2 subsystem D).",
          "type": "string", "enum": ["pending","provisioned","suspended","revoked"] },
        "work_arrangement": { "x-origin": "declared", "$ref": "#/$defs/workArrangement" },
        "start_date": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/isoDate" },
        "end_date": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/nullableIsoDate" },
        "scope": { "x-origin": "declared", "type": "object",
          "properties": {
            "products": { "x-origin": "declared", "type": "array", "items": { "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/productId" } },
            "repositories_only": { "x-origin": "declared", "type": "boolean" }
          },
          "additionalProperties": false },
        "suspension": { "x-origin": "declared", "type": "object",
          "properties": {
            "review_by": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/isoDate" },
            "reinstatement_decision_record": { "x-origin": "declared", "type": ["string","null"] }
          },
          "required": ["review_by"], "additionalProperties": false }
      },
      "required": ["id","display_name","github_login","role","employment_type","capabilities","ai_runtime","availability","access_status","start_date","end_date"],
      "additionalProperties": false,
      "allOf": [
        { "$comment": "7.1: end_date is mandatory for every non-employee",
          "if": { "properties": { "employment_type": { "not": { "const": "employee" } } }, "required": ["employment_type"] },
          "then": { "properties": { "end_date": { "type": "string", "format": "date" } } } },
        { "$comment": "7.1: departed implies revoked",
          "if": { "properties": { "availability": { "const": "departed" } }, "required": ["availability"] },
          "then": { "properties": { "access_status": { "const": "revoked" } } } },
        { "$comment": "7.1: suspended is valid only with active or on_leave, and carries a mandatory review-by date",
          "if": { "properties": { "access_status": { "const": "suspended" } }, "required": ["access_status"] },
          "then": { "properties": { "availability": { "enum": ["active","on_leave"] } }, "required": ["suspension"] } },
        { "$comment": "7.1: revoked implies departed, or a non-employee past end_date (date half is a residual rule)",
          "if": { "properties": { "access_status": { "const": "revoked" } }, "required": ["access_status"] },
          "then": { "anyOf": [
            { "properties": { "availability": { "const": "departed" } }, "required": ["availability"] },
            { "properties": { "employment_type": { "not": { "const": "employee" } }, "end_date": { "type": "string", "format": "date" } }, "required": ["employment_type","end_date"] }
          ] } }
      ]
    },
    "workArrangement": {
      "$comment": "Section 7.3 — the declared working calendar (D111)",
      "type": "object",
      "properties": {
        "timezone": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/ianaTimezone" },
        "arrangement": { "x-origin": "declared", "type": "string", "enum": ["onsite","hybrid","remote"] },
        "schedule": { "x-origin": "declared", "type": "object",
          "properties": {
            "mon": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "tue": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "wed": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "thu": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "fri": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "sat": { "x-origin": "declared", "$ref": "#/$defs/daySpan" },
            "sun": { "x-origin": "declared", "$ref": "#/$defs/daySpan" }
          },
          "additionalProperties": false },
        "fte": { "x-origin": "declared", "type": "number", "exclusiveMinimum": 0, "maximum": 1 },
        "public_holiday_set": { "x-origin": "declared", "type": "string", "minLength": 1 },
        "accepted_coverage_window": { "x-origin": "declared", "oneOf": [ { "type": "null" }, { "$ref": "#/$defs/coverageWindow" } ] }
      },
      "required": ["timezone","arrangement","schedule","fte","public_holiday_set","accepted_coverage_window"],
      "additionalProperties": false
    },
    "daySpan": {
      "type": "object",
      "properties": {
        "start": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/hhmm" },
        "end": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/hhmm" }
      },
      "required": ["start","end"], "additionalProperties": false
    },
    "coverageWindow": {
      "type": "object",
      "properties": {
        "days": { "x-origin": "declared", "type": "array", "minItems": 1, "items": { "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/weekday" } },
        "start": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/hhmm" },
        "end": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/hhmm" },
        "timezone": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/ianaTimezone" }
      },
      "required": ["days","start","end","timezone"], "additionalProperties": false
    },
    "rota": {
      "$comment": "Section 47.9 / 52.6 — per-product funded coverage",
      "type": "object",
      "properties": {
        "product": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/productId" },
        "members": { "x-origin": "declared", "type": "array", "minItems": 1, "items": {
          "type": "object",
          "properties": {
            "person": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/personId" },
            "accepted_window": { "x-origin": "declared", "$ref": "#/$defs/coverageWindow" },
            "paging_path": { "x-origin": "declared", "type": "string", "minLength": 1 },
            "funding_decision_record": { "x-origin": "declared", "type": "string", "minLength": 1 }
          },
          "required": ["person","accepted_window","paging_path","funding_decision_record"],
          "additionalProperties": false } }
      },
      "required": ["product","members"], "additionalProperties": false
    }
  }
}
JSON

cat > schemas/registry/people/v1/fixtures/valid.yaml <<'EOF'
registry_version: 1
people:
  - id: dev-a
    display_name: "Example Developer A"
    github_login: exampledev-a
    role: developer
    employment_type: employee
    capabilities: [backend, frontend, code-review, production-approval]
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
      products: [product-4, product-9]
      repositories_only: true
EOF

cat > schemas/registry/people/v1/fixtures/invalid-non-employee-null-end-date.yaml <<'EOF'
registry_version: 1
people:
  - id: sec-2
    display_name: "Specialist With No End Date"
    github_login: examplesec-2
    role: specialist
    employment_type: temporary_specialist
    capabilities: [security-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2026-04-01
    end_date: null
EOF

cat > schemas/registry/people/v1/fixtures/invalid-departed-not-revoked.yaml <<'EOF'
registry_version: 1
people:
  - id: dev-z
    display_name: "Departed Still Provisioned"
    github_login: exampledev-z
    role: developer
    employment_type: employee
    capabilities: [code-review]
    ai_runtime: null
    availability: departed
    access_status: provisioned
    start_date: 2024-01-01
    end_date: 2026-01-31
EOF

cat > schemas/registry/people/v1/fixtures/invalid-utc-offset-timezone.yaml <<'EOF'
registry_version: 1
people:
  - id: dev-b
    display_name: "Offset Timezone"
    github_login: exampledev-b
    role: developer
    employment_type: employee
    capabilities: [code-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: "+05:30"
      arrangement: remote
      schedule:
        mon: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-03-01
    end_date: null
EOF

cat > schemas/registry/people/v1/fixtures/invalid-fte-above-one.yaml <<'EOF'
registry_version: 1
people:
  - id: dev-c
    display_name: "Over-allocated FTE"
    github_login: exampledev-c
    role: developer
    employment_type: employee
    capabilities: [code-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: onsite
      schedule:
        mon: { start: "09:30", end: "18:30" }
      fte: 1.5
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-03-01
    end_date: null
EOF

S=schemas/registry/people/v1/people.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/people/v1/fixtures/valid.yaml
for f in schemas/registry/people/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/people
git commit -m "L1-02-03: people.yaml v1 JSON Schema (Sections 7, 7.1, 7.3, 47.9)"
git push -u origin lane/1/02-t03-people-schema
gh pr create --base integration --head lane/1/02-t03-people-schema \
  --title "L1-02-03 people.yaml v1 schema" --body "Phase 2 Lane 1. Section 7 block transcribed including the 7.3 work_arrangement block (D111) and the 47.9 rota block."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| 1 | Lints clean | `python3 validators/registry/schema-check/check.py --lint schemas/registry/people/v1/people.schema.json` | `LINT-OK …`, exit 0 |
| 2 | Spec example validates | `… --schema … --instance …/fixtures/valid.yaml` | `VALID`, exit 0 |
| 3 | All four negatives rejected | the `for` loop above | four `NEGATIVE-OK` lines, exit 0 |
| 4 | `availability` and `access_status` are the only derived fields | `python3 -c "import json; s=json.load(open('schemas/registry/people/v1/people.schema.json')); p=s['\$defs']['person']['properties']; print(','.join(k for k,v in p.items() if v.get('x-origin')=='derived'))"` | `availability,access_status` |
| 5 | `work_arrangement` present with all six 7.3 fields | `python3 -c "import json; s=json.load(open('schemas/registry/people/v1/people.schema.json')); print(len(s['\$defs']['workArrangement']['required']))"` | `6` |
| 6 | No foreign path | `git diff --name-only integration...HEAD \| grep -cv '^schemas/registry/people/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/people/v1/people.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/people/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/people/v1/people.schema.json')); p=s['\$defs']['person']['properties']; print(','.join(k for k,v in p.items() if v.get('x-origin')=='derived'))"
```

Correct output: `LINT-OK …people.schema.json`, then `VALID`, then exactly `availability,access_status`.

**STOP rule** — the Section 7 example fixture does not validate. Do **not** loosen the schema to make it pass; the Section 7 block is the authority and a mismatch means the transcription is wrong. Correct the transcription against `sed -n '548,600p' MultiProduct_MasterSpec_v4.0.md`; if the block genuinely contradicts a 7.1 rule, file a blocker.

---

### L1-02-04 — `roles.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/roles/v1/roles.schema.json`
`schemas/registry/roles/v1/fixtures/valid.yaml`
`schemas/registry/roles/v1/fixtures/invalid-dangerous-capability-in-role-default.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 8 (YAML block and rules), D106, Section 9.1, invariant 79 (Section 101.10, "New people, products and tools default to minimum privilege and draft state").

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` (Section 60.2 names `registry_version` for the Role Registry) | declared |
| `roles[].id` | string | `roleId`; the eleven shipped ids are `founder`, `team_lead`, `acting_team_lead`, `developer`, `mobile_developer`, `senior_developer`, `qa`, `devops`, `foundational_developer`, `specialist`, `contractor` — the schema does **not** close this set (Section 8: "Roles that may be added later without architectural change") | declared |
| `roles[].default_capabilities` | array | items = `safeRoleDefaultCapability`, uniqueItems | declared |

**DERIVED fields:** none.

**The one hard rule this schema encodes (D106, Section 8):** *"Control-plane CI rejects a `roles.yaml` default containing any of them"* — the eight dangerous capabilities. Encoded by `safeRoleDefaultCapability` from T02 (`capability` AND NOT `dangerousCapability`). The negative fixture uses `production-approval` in a role default.

**`x-residual-rule`:** `"Section 9.1: every capability in a default must have a row in the Section 9 capability table — enforced structurally by the enum; a future capability addition is a v2 schema, never an in-place edit (Section 60.2)."`

**Commands**

```bash
set -e
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/roles && { echo "STOP: schemas/registry/roles already exists"; exit 3; }

git checkout -b lane/1/02-t04-roles-schema
mkdir -p schemas/registry/roles/v1/fixtures
C=https://control-plane.internal/schemas/registry/_common/v1/common.schema.json

cat > schemas/registry/roles/v1/roles.schema.json <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/roles/v1/roles.schema.json",
  "title": "Role Registry (roles.yaml) v1",
  "x-spec": "Sections 8 (D106), 9, 9.1, 60.2; invariant 79",
  "x-residual-rule": [
    "Section 9.1: every capability in a default must have a row in the Section 9 capability table - enforced structurally by the enum; a future capability addition is a v2 schema, never an in-place edit (Section 60.2)."
  ],
  "type": "object",
  "properties": {
    "registry_version": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/registryVersion" },
    "roles": { "x-origin": "declared", "type": "array", "minItems": 1, "items": {
      "type": "object",
      "properties": {
        "id": { "x-origin": "declared", "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/roleId" },
        "default_capabilities": { "x-origin": "declared", "type": "array", "uniqueItems": true,
          "$comment": "D106: no role default carries a dangerous capability; control-plane CI rejects it.",
          "items": { "$ref": "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json#/$defs/safeRoleDefaultCapability" } }
      },
      "required": ["id","default_capabilities"],
      "additionalProperties": false } }
  },
  "required": ["registry_version","roles"],
  "additionalProperties": false
}
JSON

cat > schemas/registry/roles/v1/fixtures/valid.yaml <<'EOF'
registry_version: 1
roles:
  - id: founder
    default_capabilities: [strategy, budget, hiring, customer-commitment]
  - id: team_lead
    default_capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change]
  - id: acting_team_lead
    default_capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change]
  - id: developer
    default_capabilities: [code-review]
  - id: mobile_developer
    default_capabilities: [code-review, mobile-release]
  - id: senior_developer
    default_capabilities: [code-review, architecture]
  - id: qa
    default_capabilities: [verification, uat, release-signoff]
  - id: devops
    default_capabilities: [devops, code-review]
  - id: foundational_developer
    default_capabilities: [code-review]
  - id: specialist
    default_capabilities: []
  - id: contractor
    default_capabilities: []
EOF

cat > schemas/registry/roles/v1/fixtures/invalid-dangerous-capability-in-role-default.yaml <<'EOF'
registry_version: 1
roles:
  - id: developer
    default_capabilities: [code-review, production-approval]
EOF

S=schemas/registry/roles/v1/roles.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/roles/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/roles/v1/fixtures/invalid-dangerous-capability-in-role-default.yaml >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry/roles
git commit -m "L1-02-04: roles.yaml v1 JSON Schema (Section 8, D106)"
git push -u origin lane/1/02-t04-roles-schema
gh pr create --base integration --head lane/1/02-t04-roles-schema \
  --title "L1-02-04 roles.yaml v1 schema" --body "Phase 2 Lane 1. Section 8 block; D106 dangerous-capability rejection encoded."
```

> **Note on the `founder` role fixture.** Section 8's block lists `founder` with `lifecycle-decision`, `exceptional-approval` and `people-intelligence` in `default_capabilities`; the D106 rule later in the same section states those are "granted only by explicit entry in `people.yaml`, never by role" and that "the contradiction resolves in favour of the safe default." The fixture therefore carries the **post-D106** founder default. This is not a judgment call by the executor: Section 8 resolves it explicitly.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| 1 | Lints clean | `--lint schemas/registry/roles/v1/roles.schema.json` | `LINT-OK …`, exit 0 |
| 2 | Post-D106 role set validates | `--schema … --instance …/valid.yaml` | `VALID`, exit 0 |
| 3 | Dangerous default rejected | `--schema … --instance …/invalid-dangerous-capability-in-role-default.yaml; echo EXIT=$?` | `INVALID` then `EXIT=1` |
| 4 | No foreign path | `git diff --name-only integration...HEAD \| grep -cv '^schemas/registry/roles/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/roles/v1/roles.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/roles/v1/fixtures/valid.yaml && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/roles/v1/fixtures/invalid-dangerous-capability-in-role-default.yaml; echo "EXIT=$?"
```

Correct output: `LINT-OK …`, `VALID`, `INVALID`, `EXIT=1`.

**STOP rule** — the valid fixture is rejected because a capability token is missing from the T02 enum. Do not add the token to `common.schema.json` from this branch; that is a T02 edit and a second lane branch touching the same file. File a blocker naming the token.

---

### L1-02-05 — `product.yaml` schema (v2) — the Product Operating Contract <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/product/product/v2/product.schema.json`
`schemas/product/product/v2/fixtures/valid.yaml`
`schemas/product/product/v2/fixtures/invalid-24x7-without-coverage-window.yaml`
`schemas/product/product/v2/fixtures/invalid-launched-without-intake-channel.yaml`
`schemas/product/product/v2/fixtures/invalid-missing-reliability-criticality.yaml`
`schemas/product/product/v2/fixtures/invalid-ai-runtime-dependency-without-eval-suite.yaml`
`schemas/product/product/v2/fixtures/invalid-client-app-without-staged-rollout.yaml`

**Size:** L **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 15.1 (the contract, in full), 15.2, 15.4, 15.5 (CI validation list), 15.6, 15.7, 15.8, Section 10 (assignments), Section 21.1 (commitments), Section 36.4 (ai_restrictions), Section 38.1 (ai_runtime_dependency), Section 42.2 (detection expectation), Section 44.1 (recovery), Section 47.9 (support model), Section 50.1 (budget band), Section 60.2/60.3 (versioning and compatibility).

**Top-level blocks, transcribed from the Section 15.1 YAML:**

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `contract_version` | integer | `const 2` for this schema file | declared |
| `platform_compatibility` | string | `supported` \| `transitional` \| `unsupported` | declared |
| `platform_migration` | object | required when `transitional` (60.3): `target_contract_version` int, `target_workflow_version` string, `owner` personId, `deadline` date, `reason` string | declared |
| `conformance_profile` | string | `service` \| `client-app` \| `library` \| `batch` \| `customer-hosted` \| `white-label` \| `static-site` | declared |
| `identity` | object | `id` productId; `display_name` string; `lifecycle` = `active`\|`maintenance`\|`paused`\|`sunset`\|`archived`; `launch_status` = `pre-launch`\|`launched`; `created` date | declared |
| `classification` | object | `class` = `internal`\|`experimental`\|`commercial`\|`strategic`\|`regulated`\|`legacy` (extensible list — see residual rule); `reliability_criticality` = `low`\|`medium`\|`high`\|`critical` (**required**, 15.5); `domain` string, optional | declared |
| `assignments` | array | items = `common#/$defs/assignment` | declared |
| `escalation` | string | a **role**, never a person (Section 10.2) — `roleId` | declared |
| `code` | object | `repositories[]` = `{ name, role: primary\|frontend\|mobile\|<string>, deploys: bool }`; `default_branch` string; `gsd_version` pinned tag `^v[0-9]+\.[0-9]+\.[0-9]+$`, "never latest or next"; `accepts_external_contributions` bool | declared |
| `verification` | object | `automated` = `required`; `manual_uat` = `required`\|`not-applicable`; `smoke_tests` = `required`\|`not-applicable`; `performance` = `required`\|`optional`\|`not-applicable`; `contract_path` string | declared |
| `environments` | object | `local`, `staging`, `production` strings | declared |
| `deployment` | object | `build`; `artifact_type`; `artifact_registry`; `rollback_supported` bool; `rollback_method` string; `progressive_delivery` = `none`\|`flag-gated`\|`staged-rollout`; `staged_rollout` object | declared |
| `reversibility_default` | string | `fully-reversible` \| `partially-reversible` \| `non-reversible` | declared |
| `infrastructure` | object | `runtime`, `database`, `cache`, `provider`, `region`, `provider_outage_behaviour` strings; `monthly_budget_band` = `common#/$defs/budgetBand` (Section 50.1) | declared |
| `dependencies` | object | `internal[]`, `external[]`, `infrastructure[]` string arrays | declared |
| `ai_runtime_dependency` | object | full Section 38.1 shape; omitted where the runtime does not consume inference | declared |
| `security` | object | `secrets_location`; `scorecard_minimum` number; `production_db_access` string | declared |
| `ai_restrictions` | object | `ai_processing_permitted` bool (default true); `restricted_paths[]`; `basis` string (Section 36.4) | declared |
| `data` | object | `classification` = `public`\|`internal`\|`customer-data`\|`customer-pii`\|`regulated`; `retention_days` int; `residency` string; `isolation` = `shared-tenant`\|`dedicated-tenant`\|`dedicated-infrastructure`; `deletion_supported` bool; `deletion_sla_days` int; `regulatory_notification_hours` int; `subprocessors[]` | declared |
| `observability` | object | `health_endpoint`; `version_endpoint`; `metrics`; `telemetry_exposure` = `private-authenticated`\|`public`; `alert_channel` | declared |
| `automated_containment` | object | optional; `enabled` bool; `trigger_alert_class` string; `action` = `halt-writes`\|`disable-feature-flag`; `flag` string\|null | declared |
| `recovery` | object \| `not-applicable` | Section 44.1 shape; `not-applicable` permitted with a declared reason (44.1, 15.7 static-site row) | mixed — see DERIVED table |
| `operations` | object | see below | mixed — see DERIVED table |
| `commitments` | array | Section 21.1 shape | declared |
| `business` | object | `criticality` = `high`\|`medium`\|`low` (**required**, 15.5); `active_customers` int; `revenue_importance` = `high`\|`medium`\|`low` | declared |

**`staged_rollout` (15.1)** — required where `conformance_profile: client-app`, optional elsewhere:
`stages_pct` array of numbers; `observation_window_hours` int; `advancer` string (role or assignment type); `crash_free_sessions.sev2_below_pct` number; `crash_free_sessions.sev1_below_pct` number.

**`recovery` (Section 44.1, which supersedes the abbreviated 15.1 block):**
`backup_frequency` = `continuous`\|`hourly`\|`six-hourly`\|`daily`\|`weekly` (the **closed set**; minutes mapping 0 / 60 / 360 / 1440 / 10080);
`point_in_time_recovery` = `{ enabled: bool, window_minutes: int|null }`;
`backup_retention_days` int; `encrypted` bool; `storage_location` string ("never the product's own infrastructure account");
`restore_procedure` string; `restore_environment` string; `integrity_check` string;
`restore_tested` date; `rpo_minutes` int; `rto_minutes` int.

**`operations` (15.1, 42.2, 47.9):**
`support_model` = `business-hours` \| `extended` \| `24x7`;
`coverage_window` object\|null — **required** where `support_model` is `extended` or `24x7`;
`detection_expectation` = `next-business-morning` \| `rostered-window` \| `continuous`;
`intake_channel` string; `triager` string; `weekend_exception_eligible` bool;
`primary_responder` personId; `backup_responder` personId; `critical_incident_response` string.

**DERIVED fields (mark `readOnly: true` + `x-derived-from`) — this is the complete list**

| Field | Producing job | Citation |
|---|---|---|
| `operations.detection_expectation` | health/contract validator | 15.1 — "DERIVED — the token `support_model` implies, per the Section 42.2 mapping … A declared value differing from the derived value fails CI" |
| `operations.primary_responder` | reconciliation, from `incident_responder` assignments | 15.1 — "DERIVED — generated from the `incident_responder` assignments, which are authoritative; validated by reconciliation — see Section 10" |
| `operations.backup_responder` | as above | as above |
| `recovery.restore_tested` | restore-test workflow, from `records/restore-tests/` | 44.2 — "The `restore_tested` date is **derived, not declared**: the restore-test workflow writes it back from the newest passing record … A hand-edited date is drift, not evidence" |

Every other property in this schema is `declared`.

**Schema-encoded rules (each maps to a bullet of 15.5 / 15.6 / 15.7 / 44.1 / 60.3):**

1. `classification.reliability_criticality` required; `business.criticality` required (15.5).
2. `support_model` in `[extended, 24x7]` ⇒ `coverage_window` is an object, not null (15.5, 15.6, 47.9).
3. `launch_status: launched` ⇒ `operations.intake_channel` and `operations.triager` present (15.5, Section 22).
4. `ai_runtime_dependency` present ⇒ `ai_runtime_dependency.evaluation.suite` present (15.5, 38.1).
5. `conformance_profile: client-app` ⇒ `deployment.staged_rollout` present (15.1).
6. `platform_compatibility: transitional` ⇒ `platform_migration` with owner, target version and deadline (60.3).
7. `recovery.point_in_time_recovery.enabled: true` ⇒ `window_minutes` is an integer (44.1).
8. `contract_version` is `const 2` (this file is the v2 schema; 60.2).

**`x-residual-rule` (verbatim strings):**

* `"Section 15.5 / 44.2: restore_tested must not be older than the applicable window - 90-day floor, tightened where classification.reliability_criticality demands it. Date arithmetic."`
* `"Section 15.5: an assignment must reference an existing, non-departed person in people.yaml, and its end_date must not have passed."`
* `"Section 15.5: the reviewer set must match GitHub Team membership."`
* `"Section 15.5: a declared internal dependency must exist in the shared-service registry."`
* `"Section 15.5: contract_version must be supported by platform.yaml supported_contract_versions."`
* `"Section 15.5: data.residency must not conflict with infrastructure.region without a recorded resolution."`
* `"Section 15.5 / 21.4: a commitments entry whose promised SLA conflicts with declared RTO/RPO, support_model or detection_expectation requires conflict_check recorded as resolved."`
* `"Section 15.5 / 44.5: a product with a recovery block must have restore-production.yml."`
* `"Section 15.1 / 42.2: the declared detection_expectation must equal the value derived from support_model; a difference fails CI."`
* `"Section 44.1: rpo_minutes must be at least the minutes value of backup_frequency (0/60/360/1440/10080), unless point_in_time_recovery.enabled, in which case at least window_minutes."`
* `"Section 47.9: the coverage_window must be fully covered by the accepted windows of active rota members in people.yaml."`
* `"Section 15.7: the contract must satisfy the equivalent-evidence requirements of its declared conformance_profile."`
* `"Section 15.3: classification.class is an extensible list - adding a class is a registry change, and the enum is widened by a v3 schema, never by an in-place edit (Section 60.2)."`

**Commands**

```bash
set -euo pipefail
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/product/product && { echo "STOP: schemas/product/product already exists"; exit 3; }

git checkout -b lane/1/02-t05-product-schema
mkdir -p schemas/product/product/v2/fixtures

python3 - <<'PY'
import pathlib, json

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/product/product/v2/product.schema.json",
  "title": "Product Operating Contract (product.yaml) v2",
  "x-spec": "Sections 15.1, 15.5, 15.6, 15.7, 21.1, 36.4, 38.1, 42.2, 44.1, 47.9, 50.1, 60.2, 60.3",
  "x-residual-rule": [
    "Section 15.5 / 44.2: restore_tested must not be older than the applicable window - 90-day floor, tightened where classification.reliability_criticality demands it. Date arithmetic.",
    "Section 15.5: an assignment must reference an existing, non-departed person in people.yaml, and its end_date must not have passed.",
    "Section 15.5: the reviewer set must match GitHub Team membership.",
    "Section 15.5: a declared internal dependency must exist in the shared-service registry.",
    "Section 15.5: contract_version must be supported by platform.yaml supported_contract_versions.",
    "Section 15.5: data.residency must not conflict with infrastructure.region without a recorded resolution.",
    "Section 15.5 / 21.4: a commitments entry whose promised SLA conflicts with declared RTO/RPO, support_model or detection_expectation requires conflict_check recorded as resolved.",
    "Section 15.5 / 44.5: a product with a recovery block must have restore-production.yml.",
    "Section 15.1 / 42.2: the declared detection_expectation must equal the value derived from support_model; a difference fails CI.",
    "Section 44.1: rpo_minutes must be at least the minutes value of backup_frequency (0/60/360/1440/10080), unless point_in_time_recovery.enabled, in which case at least window_minutes.",
    "Section 47.9: the coverage_window must be fully covered by the accepted windows of active rota members in people.yaml.",
    "Section 15.7: the contract must satisfy the equivalent-evidence requirements of its declared conformance_profile.",
    "Section 15.3: classification.class is an extensible list - adding a class is a registry change, and the enum is widened by a v3 schema, never by an in-place edit (Section 60.2)."
  ],
  "type": "object",
  "properties": {
    "contract_version": {"x-origin": "declared", "const": 2},
    "platform_compatibility": {"x-origin": "declared", "type": "string", "enum": ["supported","transitional","unsupported"]},
    "platform_migration": {"x-origin": "declared", "$ref": "#/$defs/platformMigration"},
    "conformance_profile": {"x-origin": "declared", "type": "string", "enum": ["service","client-app","library","batch","customer-hosted","white-label","static-site"]},
    "identity": {"x-origin": "declared", "$ref": "#/$defs/identity"},
    "classification": {"x-origin": "declared", "$ref": "#/$defs/classification"},
    "assignments": {"x-origin": "declared", "type": "array", "items": {"$ref": C + "#/$defs/assignment"}},
    "escalation": {"x-origin": "declared", "$ref": C + "#/$defs/roleId"},
    "code": {"x-origin": "declared", "$ref": "#/$defs/code"},
    "verification": {"x-origin": "declared", "$ref": "#/$defs/verificationBlock"},
    "environments": {"x-origin": "declared", "$ref": "#/$defs/environments"},
    "deployment": {"x-origin": "declared", "$ref": "#/$defs/deployment"},
    "reversibility_default": {"x-origin": "declared", "type": "string", "enum": ["fully-reversible","partially-reversible","non-reversible"]},
    "infrastructure": {"x-origin": "declared", "$ref": "#/$defs/infrastructure"},
    "dependencies": {"x-origin": "declared", "$ref": "#/$defs/dependencies"},
    "ai_runtime_dependency": {"x-origin": "declared", "$ref": "#/$defs/aiRuntimeDependency"},
    "security": {"x-origin": "declared", "$ref": "#/$defs/security"},
    "ai_restrictions": {"x-origin": "declared", "$ref": "#/$defs/aiRestrictions"},
    "data": {"x-origin": "declared", "$ref": "#/$defs/data"},
    "observability": {"x-origin": "declared", "$ref": "#/$defs/observability"},
    "automated_containment": {"x-origin": "declared", "$ref": "#/$defs/automatedContainment"},
    "recovery": {"x-origin": "declared", "$ref": "#/$defs/recovery"},
    "operations": {"x-origin": "declared", "$ref": "#/$defs/operations"},
    "commitments": {"x-origin": "declared", "type": "array", "items": {"$ref": "#/$defs/commitment"}},
    "business": {"x-origin": "declared", "$ref": "#/$defs/business"}
  },
  "required": ["contract_version","platform_compatibility","conformance_profile","identity","classification","assignments","escalation","code","verification","environments","deployment","reversibility_default","infrastructure","dependencies","security","data","observability","operations","commitments","business"],
  "additionalProperties": False,
  "allOf": [
    {"$comment": "15.5: extended or 24x7 requires coverage_window object",
     "if": {"properties": {"operations": {"properties": {"support_model": {"enum": ["extended","24x7"]}}, "required": ["support_model"]}}, "required": ["operations"]},
     "then": {"properties": {"operations": {"properties": {"coverage_window": {"type": "object"}}, "required": ["coverage_window"]}}}},
    {"$comment": "15.5: launched requires intake_channel and triager",
     "if": {"properties": {"identity": {"properties": {"launch_status": {"const": "launched"}}, "required": ["launch_status"]}}, "required": ["identity"]},
     "then": {"properties": {"operations": {"required": ["intake_channel","triager"]}}}},
    {"$comment": "15.5 / 38.1: ai_runtime_dependency present requires evaluation.suite",
     "if": {"required": ["ai_runtime_dependency"]},
     "then": {"properties": {"ai_runtime_dependency": {"properties": {"evaluation": {"required": ["suite"]}}, "required": ["evaluation"]}}}},
    {"$comment": "15.1: client-app requires deployment.staged_rollout",
     "if": {"properties": {"conformance_profile": {"const": "client-app"}}, "required": ["conformance_profile"]},
     "then": {"properties": {"deployment": {"required": ["staged_rollout"]}}}},
    {"$comment": "60.3: transitional requires platform_migration",
     "if": {"properties": {"platform_compatibility": {"const": "transitional"}}, "required": ["platform_compatibility"]},
     "then": {"required": ["platform_migration"]}},
    {"$comment": "44.1: point_in_time_recovery.enabled true requires window_minutes integer",
     "if": {"properties": {"recovery": {"type": "object", "properties": {"point_in_time_recovery": {"properties": {"enabled": {"const": True}}, "required": ["enabled"]}}, "required": ["point_in_time_recovery"]}}, "required": ["recovery"]},
     "then": {"properties": {"recovery": {"properties": {"point_in_time_recovery": {"properties": {"window_minutes": {"type": "integer"}}}}}}}}
  ],
  "$defs": {
    "platformMigration": {
      "type": "object",
      "properties": {
        "target_contract_version": {"x-origin": "declared", "type": "integer"},
        "target_workflow_version": {"x-origin": "declared", "type": "string"},
        "owner": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "deadline": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "reason": {"x-origin": "declared", "type": "string", "minLength": 1}
      },
      "required": ["target_contract_version","target_workflow_version","owner","deadline","reason"],
      "additionalProperties": False
    },
    "identity": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "$ref": C + "#/$defs/productId"},
        "display_name": {"x-origin": "declared", "type": "string", "minLength": 1},
        "lifecycle": {"x-origin": "declared", "type": "string", "enum": ["active","maintenance","paused","sunset","archived"]},
        "launch_status": {"x-origin": "declared", "type": "string", "enum": ["pre-launch","launched"]},
        "created": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"}
      },
      "required": ["id","display_name","lifecycle","launch_status","created"],
      "additionalProperties": False
    },
    "classification": {
      "type": "object",
      "properties": {
        "class": {"x-origin": "declared", "type": "string", "enum": ["internal","experimental","commercial","strategic","regulated","legacy"]},
        "reliability_criticality": {"x-origin": "declared", "type": "string", "enum": ["low","medium","high","critical"]},
        "domain": {"x-origin": "declared", "type": "string"}
      },
      "required": ["class","reliability_criticality"],
      "additionalProperties": False
    },
    "code": {
      "type": "object",
      "properties": {
        "repositories": {"x-origin": "declared", "type": "array", "items": {
          "type": "object",
          "properties": {
            "name": {"x-origin": "declared", "type": "string"},
            "role": {"x-origin": "declared", "type": "string"},
            "deploys": {"x-origin": "declared", "type": "boolean"}
          },
          "required": ["name","role","deploys"], "additionalProperties": False
        }},
        "default_branch": {"x-origin": "declared", "type": "string"},
        "gsd_version": {"x-origin": "declared", "type": "string", "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$"},
        "accepts_external_contributions": {"x-origin": "declared", "type": "boolean"}
      },
      "required": ["repositories","default_branch","gsd_version","accepts_external_contributions"],
      "additionalProperties": False
    },
    "verificationBlock": {
      "type": "object",
      "properties": {
        "automated": {"x-origin": "declared", "type": "string", "const": "required"},
        "manual_uat": {"x-origin": "declared", "type": "string", "enum": ["required","not-applicable"]},
        "smoke_tests": {"x-origin": "declared", "type": "string", "enum": ["required","not-applicable"]},
        "performance": {"x-origin": "declared", "type": "string", "enum": ["required","optional","not-applicable"]},
        "contract_path": {"x-origin": "declared", "type": "string"}
      },
      "required": ["automated","manual_uat","smoke_tests","performance","contract_path"],
      "additionalProperties": False
    },
    "environments": {
      "type": "object",
      "properties": {
        "local": {"x-origin": "declared", "type": "string"},
        "staging": {"x-origin": "declared", "type": "string"},
        "production": {"x-origin": "declared", "type": "string"}
      },
      "additionalProperties": False
    },
    "stagedRollout": {
      "type": "object",
      "properties": {
        "stages_pct": {"x-origin": "declared", "type": "array", "items": {"type": "number"}},
        "observation_window_hours": {"x-origin": "declared", "type": "integer"},
        "advancer": {"x-origin": "declared", "type": "string"},
        "crash_free_sessions": {"x-origin": "declared", "type": "object",
          "properties": {
            "sev2_below_pct": {"x-origin": "declared", "type": "number"},
            "sev1_below_pct": {"x-origin": "declared", "type": "number"}
          }, "additionalProperties": False}
      },
      "required": ["stages_pct","observation_window_hours","advancer","crash_free_sessions"],
      "additionalProperties": False
    },
    "deployment": {
      "type": "object",
      "properties": {
        "build": {"x-origin": "declared", "type": "string"},
        "artifact_type": {"x-origin": "declared", "type": "string"},
        "artifact_registry": {"x-origin": "declared", "type": "string"},
        "rollback_supported": {"x-origin": "declared", "type": "boolean"},
        "rollback_method": {"x-origin": "declared", "type": "string"},
        "progressive_delivery": {"x-origin": "declared", "type": "string", "enum": ["none","flag-gated","staged-rollout"]},
        "staged_rollout": {"x-origin": "declared", "$ref": "#/$defs/stagedRollout"}
      },
      "required": ["build","artifact_type","artifact_registry","rollback_supported","rollback_method","progressive_delivery"],
      "additionalProperties": False
    },
    "infrastructure": {
      "type": "object",
      "properties": {
        "runtime": {"x-origin": "declared", "type": "string"},
        "database": {"x-origin": "declared", "type": "string"},
        "cache": {"x-origin": "declared", "type": "string"},
        "provider": {"x-origin": "declared", "type": "string"},
        "region": {"x-origin": "declared", "type": "string"},
        "provider_outage_behaviour": {"x-origin": "declared", "type": "string"},
        "monthly_budget_band": {"x-origin": "declared", "$ref": C + "#/$defs/budgetBand"}
      },
      "additionalProperties": False
    },
    "dependencies": {
      "type": "object",
      "properties": {
        "internal": {"x-origin": "declared", "type": "array", "items": {"type": "string"}},
        "external": {"x-origin": "declared", "type": "array", "items": {"type": "string"}},
        "infrastructure": {"x-origin": "declared", "type": "array", "items": {"type": "string"}}
      },
      "additionalProperties": False
    },
    "aiRuntimeDependency": {
      "type": "object",
      "properties": {
        "evaluation": {"x-origin": "declared", "type": "object",
          "properties": {"suite": {"x-origin": "declared", "type": "string", "minLength": 1}},
          "required": ["suite"], "additionalProperties": False}
      },
      "additionalProperties": False
    },
    "security": {
      "type": "object",
      "properties": {
        "secrets_location": {"x-origin": "declared", "type": "string"},
        "scorecard_minimum": {"x-origin": "declared", "type": "number"},
        "production_db_access": {"x-origin": "declared", "type": "string"}
      },
      "additionalProperties": False
    },
    "aiRestrictions": {
      "type": "object",
      "properties": {
        "ai_processing_permitted": {"x-origin": "declared", "type": "boolean"},
        "restricted_paths": {"x-origin": "declared", "type": "array", "items": {"type": "string"}},
        "basis": {"x-origin": "declared", "type": "string"}
      },
      "additionalProperties": False
    },
    "data": {
      "type": "object",
      "properties": {
        "classification": {"x-origin": "declared", "type": "string", "enum": ["public","internal","customer-data","customer-pii","regulated"]},
        "retention_days": {"x-origin": "declared", "type": "integer"},
        "residency": {"x-origin": "declared", "type": "string"},
        "isolation": {"x-origin": "declared", "type": "string", "enum": ["shared-tenant","dedicated-tenant","dedicated-infrastructure"]},
        "deletion_supported": {"x-origin": "declared", "type": "boolean"},
        "deletion_sla_days": {"x-origin": "declared", "type": "integer"},
        "regulatory_notification_hours": {"x-origin": "declared", "type": "integer"},
        "subprocessors": {"x-origin": "declared", "type": "array", "items": {"type": "string"}}
      },
      "additionalProperties": False
    },
    "observability": {
      "type": "object",
      "properties": {
        "health_endpoint": {"x-origin": "declared", "type": "string"},
        "version_endpoint": {"x-origin": "declared", "type": "string"},
        "metrics": {"x-origin": "declared", "type": "string"},
        "telemetry_exposure": {"x-origin": "declared", "type": "string", "enum": ["private-authenticated","public"]},
        "alert_channel": {"x-origin": "declared", "type": "string"}
      },
      "additionalProperties": False
    },
    "automatedContainment": {
      "type": "object",
      "properties": {
        "enabled": {"x-origin": "declared", "type": "boolean"},
        "trigger_alert_class": {"x-origin": "declared", "type": "string"},
        "action": {"x-origin": "declared", "type": "string", "enum": ["halt-writes","disable-feature-flag"]},
        "flag": {"x-origin": "declared", "type": ["string","null"]}
      },
      "required": ["enabled","trigger_alert_class","action","flag"],
      "additionalProperties": False
    },
    "recovery": {
      "oneOf": [
        {"type": "string", "const": "not-applicable"},
        {"type": "object",
          "properties": {
            "backup_frequency": {"x-origin": "declared", "type": "string", "enum": ["continuous","hourly","six-hourly","daily","weekly"]},
            "point_in_time_recovery": {"x-origin": "declared", "type": "object",
              "properties": {
                "enabled": {"x-origin": "declared", "type": "boolean"},
                "window_minutes": {"x-origin": "declared", "type": ["integer","null"]}
              }, "required": ["enabled","window_minutes"], "additionalProperties": False},
            "backup_retention_days": {"x-origin": "declared", "type": "integer"},
            "encrypted": {"x-origin": "declared", "type": "boolean"},
            "storage_location": {"x-origin": "declared", "type": "string"},
            "restore_procedure": {"x-origin": "declared", "type": "string"},
            "restore_environment": {"x-origin": "declared", "type": "string"},
            "integrity_check": {"x-origin": "declared", "type": "string"},
            "restore_tested": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 44.2: the restore-test workflow writes restore_tested from the newest passing record in records/restore-tests/; a hand-edited date is drift, not evidence.",
              "type": "string", "format": "date"},
            "rpo_minutes": {"x-origin": "declared", "type": "integer"},
            "rto_minutes": {"x-origin": "declared", "type": "integer"}
          },
          "required": ["backup_frequency","point_in_time_recovery","backup_retention_days","encrypted","storage_location","restore_procedure","restore_environment","integrity_check","rpo_minutes","rto_minutes"],
          "additionalProperties": False}
      ]
    },
    "operations": {
      "type": "object",
      "properties": {
        "support_model": {"x-origin": "declared", "type": "string", "enum": ["business-hours","extended","24x7"]},
        "coverage_window": {"x-origin": "declared"},
        "detection_expectation": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 15.1 / 42.2: support_model implies this token per the Section 42.2 mapping; producing job = health/contract validator.",
          "type": "string", "enum": ["next-business-morning","rostered-window","continuous"]},
        "intake_channel": {"x-origin": "declared", "type": "string"},
        "triager": {"x-origin": "declared", "type": "string"},
        "weekend_exception_eligible": {"x-origin": "declared", "type": "boolean"},
        "primary_responder": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 15.1 / Section 10: generated from incident_responder assignments; producing job = reconciliation.",
          "$ref": C + "#/$defs/personId"},
        "backup_responder": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 15.1 / Section 10: generated from incident_responder assignments; producing job = reconciliation.",
          "$ref": C + "#/$defs/personId"},
        "critical_incident_response": {"x-origin": "declared", "type": "string"}
      },
      "required": ["support_model","detection_expectation"],
      "additionalProperties": False
    },
    "commitment": {
      "type": "object",
      "properties": {
        "sla": {"x-origin": "declared", "type": "string"},
        "scope": {"x-origin": "declared", "type": "string"},
        "conflict_check": {"x-origin": "declared", "type": "string", "enum": ["passed","waived-with-decision"]}
      },
      "required": ["sla","scope","conflict_check"],
      "additionalProperties": False
    },
    "business": {
      "type": "object",
      "properties": {
        "criticality": {"x-origin": "declared", "type": "string", "enum": ["high","medium","low"]},
        "active_customers": {"x-origin": "declared", "type": "integer"},
        "revenue_importance": {"x-origin": "declared", "type": "string", "enum": ["high","medium","low"]}
      },
      "required": ["criticality"],
      "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/product/product/v2/product.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")
print("wrote product.schema.json")
PY

python3 - <<'PY'
import pathlib, json, copy

base = pathlib.Path("schemas/product/product/v2/fixtures")

valid = {
  "contract_version": 2,
  "platform_compatibility": "supported",
  "conformance_profile": "service",
  "identity": {
    "id": "product-1",
    "display_name": "Example Product 1",
    "lifecycle": "active",
    "launch_status": "launched",
    "created": "2024-01-15"
  },
  "classification": {
    "class": "commercial",
    "reliability_criticality": "high",
    "domain": "core-platform"
  },
  "assignments": [
    {"person": "dev-a", "type": "primary_owner", "start_date": "2024-01-15", "end_date": None}
  ],
  "escalation": "team_lead",
  "code": {
    "repositories": [{"name": "org/product-1-api", "role": "primary", "deploys": True}],
    "default_branch": "main",
    "gsd_version": "v3.1.0",
    "accepts_external_contributions": False
  },
  "verification": {
    "automated": "required",
    "manual_uat": "required",
    "smoke_tests": "required",
    "performance": "optional",
    "contract_path": "verification/contract.yaml"
  },
  "environments": {
    "local": "http://localhost:3000",
    "staging": "https://staging.product-1.internal",
    "production": "https://product-1.company.com"
  },
  "deployment": {
    "build": "docker",
    "artifact_type": "container-image",
    "artifact_registry": "ghcr.io/org",
    "rollback_supported": True,
    "rollback_method": "Redeploy previous container tag",
    "progressive_delivery": "none"
  },
  "reversibility_default": "fully-reversible",
  "infrastructure": {
    "runtime": "Node.js 22",
    "database": "PostgreSQL",
    "cache": "Redis",
    "provider": "AWS",
    "region": "ap-south-1",
    "provider_outage_behaviour": "degraded-mode",
    "monthly_budget_band": {"currency": "USD", "expected": 450, "ceiling": 600}
  },
  "dependencies": {
    "internal": [],
    "external": ["stripe.com/v2"],
    "infrastructure": ["postgres-primary"]
  },
  "ai_runtime_dependency": {
    "evaluation": {"suite": "evals/product-1/suite.yaml"}
  },
  "security": {
    "secrets_location": "AWS Secrets Manager",
    "scorecard_minimum": 7,
    "production_db_access": "via bastion host only"
  },
  "ai_restrictions": {
    "ai_processing_permitted": True,
    "restricted_paths": [],
    "basis": "Section 36.4 default"
  },
  "data": {
    "classification": "customer-data",
    "retention_days": 2555,
    "residency": "ap-south-1",
    "isolation": "shared-tenant",
    "deletion_supported": True,
    "deletion_sla_days": 30,
    "regulatory_notification_hours": 72,
    "subprocessors": ["stripe.com"]
  },
  "observability": {
    "health_endpoint": "/health",
    "version_endpoint": "/version",
    "metrics": "Prometheus /metrics",
    "telemetry_exposure": "private-authenticated",
    "alert_channel": "#alerts-product-1"
  },
  "recovery": {
    "backup_frequency": "daily",
    "point_in_time_recovery": {"enabled": False, "window_minutes": None},
    "backup_retention_days": 30,
    "encrypted": True,
    "storage_location": "AWS S3 ap-south-1 (separate account)",
    "restore_procedure": "Run ops/restore.sh with backup ID",
    "restore_environment": "staging-restore.product-1.internal",
    "integrity_check": "SHA-256 checksum on backup file",
    "restore_tested": "2026-07-01",
    "rpo_minutes": 1440,
    "rto_minutes": 240
  },
  "operations": {
    "support_model": "business-hours",
    "detection_expectation": "next-business-morning",
    "intake_channel": "#support-product-1",
    "triager": "dev-a",
    "weekend_exception_eligible": False,
    "primary_responder": "dev-a",
    "backup_responder": "sec-1",
    "critical_incident_response": "Page primary responder immediately"
  },
  "commitments": [
    {"sla": "99.9% uptime", "scope": "paying customers", "conflict_check": "passed"}
  ],
  "business": {
    "criticality": "high",
    "active_customers": 42,
    "revenue_importance": "high"
  }
}

def dump(obj):
    return json.dumps(obj, indent=2, default=str) + "\n"

(base / "valid.yaml").write_text(
    "# Fixture: Section 15.1 Product Operating Contract example (v2)\n" + dump(valid).replace("false","False").replace("true","True").replace("null","None"),
    encoding="utf-8")

# Use json.dumps for YAML-compatible output (AJV accepts JSON as valid YAML)
import yaml as _y
def ydump(obj):
    return _y.safe_dump(obj, default_flow_style=False, sort_keys=False, allow_unicode=True)

(base / "valid.yaml").write_text(ydump(valid), encoding="utf-8")

f1 = copy.deepcopy(valid)
f1["operations"]["support_model"] = "24x7"
f1["operations"]["coverage_window"] = None
(base / "invalid-24x7-without-coverage-window.yaml").write_text(ydump(f1), encoding="utf-8")

f2 = copy.deepcopy(valid)
del f2["operations"]["intake_channel"]
(base / "invalid-launched-without-intake-channel.yaml").write_text(ydump(f2), encoding="utf-8")

f3 = copy.deepcopy(valid)
del f3["classification"]["reliability_criticality"]
(base / "invalid-missing-reliability-criticality.yaml").write_text(ydump(f3), encoding="utf-8")

f4 = copy.deepcopy(valid)
del f4["ai_runtime_dependency"]["evaluation"]
(base / "invalid-ai-runtime-dependency-without-eval-suite.yaml").write_text(ydump(f4), encoding="utf-8")

f5 = copy.deepcopy(valid)
f5["conformance_profile"] = "client-app"
(base / "invalid-client-app-without-staged-rollout.yaml").write_text(ydump(f5), encoding="utf-8")

print("wrote 6 fixtures (valid + 5 negatives)")
PY
```

```bash
set -e
test -f schemas/product/product/v2/product.schema.json || { echo "skip: schemas/product/product/v2/product.schema.json not yet present"; exit 0; }
S=schemas/product/product/v2/product.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/product/v2/fixtures/valid.yaml
for f in schemas/product/product/v2/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done
git add schemas/product/product
git commit -m "L1-02-05: product.yaml v2 JSON Schema (Section 15.1 Product Operating Contract)"
git push -u origin lane/1/02-t05-product-schema
gh pr create --base integration --head lane/1/02-t05-product-schema \
  --title "L1-02-05 product.yaml v2 schema" --body "Phase 2 Lane 1. Full Section 15.1 contract; four DERIVED fields marked; thirteen residual rules recorded."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| 1 | Lints clean | `--lint schemas/product/product/v2/product.schema.json` | `LINT-OK …`, exit 0 |
| 2 | Section 15.1 example validates | `--schema … --instance …/fixtures/valid.yaml` | `VALID`, exit 0 |
| 3 | All five negatives rejected | the `for` loop | five `NEGATIVE-OK` lines, exit 0 |
| 4 | Exactly four derived fields, and they are the four named | `python3 -c "import json; s=json.load(open('schemas/product/product/v2/product.schema.json')); out=set(); w=lambda n,p: [out.add(p+'.'+k) or w(v,p+'.'+k) for k,v in n.get('properties',{}).items() if isinstance(v,dict) and v.get('x-origin')=='derived'] or [w(v,p) for v in (n.values() if isinstance(n,dict) else [])]; w(s,''); print(' '.join(sorted(out)))"` | contains `detection_expectation`, `primary_responder`, `backup_responder`, `restore_tested` and nothing else |
| 5 | All thirteen residual rules recorded | `python3 -c "import json; s=json.load(open('schemas/product/product/v2/product.schema.json')); print(len(s['x-residual-rule']))"` | `13` |
| 6 | `contract_version` pinned to 2 | `python3 -c "import json; s=json.load(open('schemas/product/product/v2/product.schema.json')); print(s['properties']['contract_version']['const'])"` | `2` |
| 7 | No foreign path | `git diff --name-only integration...HEAD \| grep -cv '^schemas/product/product/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/product/product/v2/product.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/product/v2/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/product/product/v2/product.schema.json')); print(len(s['x-residual-rule']), s['properties']['contract_version']['const'])"
```

Correct output: `LINT-OK …product.schema.json`, `VALID`, then `13 2`.

**STOP rule** — the Section 15.1 example fails validation on the `commitments[0].conflict_check` value `waived-with-decision`. That value is deliberate (15.1's own comment: "NOT passed, deliberately — see 21.4"), and Section 21.1 enumerates `passed | waived-with-decision`. If the schema rejects it, the enum transcription is wrong — fix the enum, do not edit the fixture. If any *other* part of the Section 15.1 example fails, stop and file a blocker rather than editing the example: the example is the contract.

> **DECISION REQUIRED — DECISION-L1-02-A (routed to L0, does not block this task).** `platform.yaml` in Section 60.1 declares `supported_contract_versions.product: [1, 2]`. Spec Section 15.1 exhibits only the v2 contract; no v1 product contract shape appears anywhere in the specification. L1 cannot author a `schemas/product/product/v1/` schema without inventing a shape, which this lane is forbidden to do. **L0 must decide one of:** (a) the fleet is authored at v2 only and `platform.yaml` ships `supported_contract_versions.product: [2]`; or (b) L0 supplies the v1 shape as a frozen artifact under `contracts/**` for L1 to transcribe. Until decided, this phase ships v2 only, and `schemas/registry/index.json` (T19) lists v2 only.

---

### L1-02-06 — `service.yaml` schema (v1) — Shared Service Contract <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/product/service/v1/service.schema.json`
`schemas/product/service/v1/fixtures/valid.yaml`
`schemas/product/service/v1/fixtures/invalid-missing-consumers.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 20.1 (YAML block and rules), Section 60.2 (`service_version`), Section 10.1 (assignment types).

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `service_version` | integer | `>= 1`; Section 60.2 names `service_version` for the Shared Service Contract | declared |
| `identity.id` | string | `identifier` | declared |
| `identity.repository` | string | `org/repo` | declared |
| `identity.type` | string | `internal-api` \| `library` \| `platform-component` | declared |
| `assignments[]` | array | `common#/$defs/assignment` (the Section 20.1 block omits dates; the schema keeps `start_date`/`end_date` required because Section 20.1 states a shared service "has the same four ownership relationships as a product") | declared |
| `escalation` | string | `roleId`; "resolves through topology.yaml" | declared |
| `consumers[]` | array | productId, minItems 1 — "authoritative; validated against products" | declared |
| `compatibility.versioning` | string | `semver` | declared |
| `compatibility.supported_versions[]` | array | strings | declared |
| `compatibility.deprecation_notice_days` | integer | `>= 0` | declared |
| `compatibility.breaking_change_policy` | string | `major-version-with-migration-guide` | declared |
| `verification.automated` | string | `required` | declared |
| `verification.consumer_contract_tests` | string | `required` — Section 20.1: "Consumer contract tests are required" | declared |
| `verification.smoke_tests` | string | `required` \| `not-applicable` | declared |
| `operations.primary_responder` | string | personId | declared |
| `operations.backup_responder` | string | personId | declared |
| `operations.incident_severity_inheritance` | string | `highest-consumer` | declared |

**DERIVED fields:** none. (Section 20.1 marks `consumers` "authoritative", i.e. declared and validated against products, not generated.)

**`x-residual-rule`:**
* `"Section 20.1: a product cannot declare a dependency on a shared service that does not exist in the registry; CI enforces this."`
* `"Section 20.1: consumers is validated against the products that declare this service in dependencies.internal."`
* `"Section 20.1: incident severity inherits from the highest consumer, reading classification.reliability_criticality of the consuming products."`

**Fixture:** `valid.yaml` is the Section 20.1 `auth-service` block verbatim, with `start_date`/`end_date` added to each assignment (`2025-06-01` / `null`). `invalid-missing-consumers.yaml` is the same block with `consumers` set to `[]`.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/product/service && { echo "STOP: schemas/product/service already exists"; exit 3; }

git checkout -b lane/1/02-t06-service-schema
mkdir -p schemas/product/service/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/product/service/v1/service.schema.json",
  "title": "Shared Service Contract (service.yaml) v1",
  "x-spec": "Sections 20.1, 10.1, 60.2",
  "x-residual-rule": [
    "Section 20.1: a product cannot declare a dependency on a shared service that does not exist in the registry; CI enforces this.",
    "Section 20.1: consumers is validated against the products that declare this service in dependencies.internal.",
    "Section 20.1: incident severity inherits from the highest consumer, reading classification.reliability_criticality of the consuming products."
  ],
  "type": "object",
  "properties": {
    "service_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "identity": {"x-origin": "declared", "$ref": "#/$defs/serviceIdentity"},
    "assignments": {"x-origin": "declared", "type": "array", "items": {"$ref": C + "#/$defs/assignment"}},
    "escalation": {"x-origin": "declared", "$ref": C + "#/$defs/roleId"},
    "consumers": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"$ref": C + "#/$defs/productId"}},
    "compatibility": {"x-origin": "declared", "$ref": "#/$defs/compatibility"},
    "verification": {"x-origin": "declared", "$ref": "#/$defs/serviceVerification"},
    "operations": {"x-origin": "declared", "$ref": "#/$defs/serviceOperations"}
  },
  "required": ["service_version","identity","assignments","escalation","consumers","compatibility","verification","operations"],
  "additionalProperties": False,
  "$defs": {
    "serviceIdentity": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "$ref": C + "#/$defs/identifier"},
        "repository": {"x-origin": "declared", "type": "string"},
        "type": {"x-origin": "declared", "type": "string", "enum": ["internal-api","library","platform-component"]}
      },
      "required": ["id","repository","type"], "additionalProperties": False
    },
    "compatibility": {
      "type": "object",
      "properties": {
        "versioning": {"x-origin": "declared", "type": "string", "const": "semver"},
        "supported_versions": {"x-origin": "declared", "type": "array", "items": {"type": "string"}},
        "deprecation_notice_days": {"x-origin": "declared", "type": "integer", "minimum": 0},
        "breaking_change_policy": {"x-origin": "declared", "type": "string", "const": "major-version-with-migration-guide"}
      },
      "required": ["versioning","supported_versions","deprecation_notice_days","breaking_change_policy"],
      "additionalProperties": False
    },
    "serviceVerification": {
      "type": "object",
      "properties": {
        "automated": {"x-origin": "declared", "type": "string", "const": "required"},
        "consumer_contract_tests": {"x-origin": "declared", "type": "string", "const": "required"},
        "smoke_tests": {"x-origin": "declared", "type": "string", "enum": ["required","not-applicable"]}
      },
      "required": ["automated","consumer_contract_tests","smoke_tests"], "additionalProperties": False
    },
    "serviceOperations": {
      "type": "object",
      "properties": {
        "primary_responder": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "backup_responder": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "incident_severity_inheritance": {"x-origin": "declared", "type": "string", "const": "highest-consumer"}
      },
      "required": ["primary_responder","backup_responder","incident_severity_inheritance"],
      "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/product/service/v1/service.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

valid = {
  "service_version": 1,
  "identity": {"id": "auth-service", "repository": "org/auth-service", "type": "internal-api"},
  "assignments": [
    {"person": "dev-a", "type": "primary_owner", "start_date": "2025-06-01", "end_date": None},
    {"person": "dev-b", "type": "backup_owner", "start_date": "2025-06-01", "end_date": None}
  ],
  "escalation": "team_lead",
  "consumers": ["product-1", "product-3", "product-7"],
  "compatibility": {
    "versioning": "semver",
    "supported_versions": ["2.x", "3.x"],
    "deprecation_notice_days": 90,
    "breaking_change_policy": "major-version-with-migration-guide"
  },
  "verification": {
    "automated": "required",
    "consumer_contract_tests": "required",
    "smoke_tests": "required"
  },
  "operations": {
    "primary_responder": "dev-a",
    "backup_responder": "dev-b",
    "incident_severity_inheritance": "highest-consumer"
  }
}

pathlib.Path("schemas/product/service/v1/fixtures/valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

invalid = dict(valid)
invalid["consumers"] = []
pathlib.Path("schemas/product/service/v1/fixtures/invalid-missing-consumers.yaml").write_text(
    yaml.safe_dump(invalid, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote service.schema.json + 2 fixtures")
PY

S=schemas/product/service/v1/service.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/service/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/service/v1/fixtures/invalid-missing-consumers.yaml >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/product/service
git commit -m "L1-02-06: service.yaml v1 JSON Schema (Section 20.1 Shared Service Contract)"
git push -u origin lane/1/02-t06-service-schema
gh pr create --base integration --head lane/1/02-t06-service-schema \
  --title "L1-02-06 service.yaml v1 schema" --body "Phase 2 Lane 1. Section 20.1 block; three residual rules recorded."
```

**Acceptance criteria** — lint clean; `valid.yaml` `VALID` exit 0; `invalid-missing-consumers.yaml` `INVALID` exit 1; `python3 -c "import json; s=json.load(open('schemas/product/service/v1/service.schema.json')); print('service_version' in s['properties'])"` prints `True`; foreign-path count `0`.

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/product/service/v1/service.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/service/v1/fixtures/valid.yaml && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/product/service/v1/fixtures/invalid-missing-consumers.yaml; echo "EXIT=$?"
```

Correct output: `LINT-OK …`, `VALID`, `INVALID`, `EXIT=1`.

**STOP rule** — as Section 0.6. Do not add a field the table above does not list, even if it "seems missing".

---

### L1-02-07 — `topology.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/topology/v1/topology.schema.json`
`schemas/registry/topology/v1/fixtures/valid.yaml`
`schemas/registry/topology/v1/fixtures/invalid-domain-lead-names-nothing.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 66.2 (the YAML block), Section 13.1 (the succession block), Section 52.6 (`topology.yaml` row), Section 10.2 (escalation resolution).

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` (shown in the 66.2 block) | declared |
| `domains_active` | boolean | "dormant until an activation trigger fires"; default `false` | declared |
| `succession.team_lead.acting` | string | personId — the pre-designated Acting Team Lead (13.1) | declared |
| `activation_triggers[]` | array | strings; the three shown in 66.2 | declared |
| `domains[]` | array | `{ id: identifier, products: [productId], lead: personId\|null, shared_services: [identifier] }` — `lead: null` "resolves to portfolio Team Lead while dormant" | declared |

**DERIVED fields:** none.

**`x-residual-rule`:**
* `"Section 66.2: while domains_active is false, every domain reference resolves to the single portfolio Team Lead."`
* `"Section 10.2 / 66.2: escalation: team_lead in a product contract resolves through this file; product contracts never name a person."`
* `"Section 13.1: the acting designate must exist in people.yaml and hold plan-approval and architecture capability continuously."`

**Fixture:** `valid.yaml` is the Section 66.2 block verbatim (including the succession block). `invalid-domain-lead-names-nothing.yaml` sets `domains[0].lead: 42` (wrong type).

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/topology && { echo "STOP: schemas/registry/topology already exists"; exit 3; }

git checkout -b lane/1/02-t07-topology-schema
mkdir -p schemas/registry/topology/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/topology/v1/topology.schema.json",
  "title": "Topology Registry (topology.yaml) v1",
  "x-spec": "Sections 66.2, 13.1, 52.6, 10.2",
  "x-residual-rule": [
    "Section 66.2: while domains_active is false, every domain reference resolves to the single portfolio Team Lead.",
    "Section 10.2 / 66.2: escalation: team_lead in a product contract resolves through this file; product contracts never name a person.",
    "Section 13.1: the acting designate must exist in people.yaml and hold plan-approval and architecture capability continuously."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "domains_active": {"x-origin": "declared", "type": "boolean"},
    "succession": {"x-origin": "declared", "$ref": "#/$defs/succession"},
    "activation_triggers": {"x-origin": "declared", "type": "array", "items": {"type": "string"}},
    "domains": {"x-origin": "declared", "type": "array", "items": {"$ref": "#/$defs/domain"}}
  },
  "required": ["registry_version","domains_active","succession","activation_triggers","domains"],
  "additionalProperties": False,
  "$defs": {
    "succession": {
      "type": "object",
      "properties": {
        "team_lead": {"x-origin": "declared", "type": "object",
          "properties": {
            "acting": {"x-origin": "declared", "$ref": C + "#/$defs/personId"}
          },
          "required": ["acting"], "additionalProperties": False}
      },
      "required": ["team_lead"], "additionalProperties": False
    },
    "domain": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "$ref": C + "#/$defs/identifier"},
        "products": {"x-origin": "declared", "type": "array", "items": {"$ref": C + "#/$defs/productId"}},
        "lead": {"x-origin": "declared", "oneOf": [{"$ref": C + "#/$defs/personId"}, {"type": "null"}]},
        "shared_services": {"x-origin": "declared", "type": "array", "items": {"$ref": C + "#/$defs/identifier"}}
      },
      "required": ["id","products","lead","shared_services"], "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/topology/v1/topology.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

valid = {
  "registry_version": 1,
  "domains_active": False,
  "succession": {"team_lead": {"acting": "dev-a"}},
  "activation_triggers": [
    "portfolio size exceeds N products with distinct technical stacks",
    "Team Lead loss without an immediate hire",
    "Founder decision"
  ],
  "domains": [
    {"id": "core", "products": ["product-1", "product-3"], "lead": None, "shared_services": ["auth-service"]}
  ]
}

pathlib.Path("schemas/registry/topology/v1/fixtures/valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

invalid = yaml.safe_load(yaml.safe_dump(valid))
invalid["domains"][0]["lead"] = 42  # wrong type — integer, not personId string or null
pathlib.Path("schemas/registry/topology/v1/fixtures/invalid-domain-lead-names-nothing.yaml").write_text(
    yaml.safe_dump(invalid, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote topology.schema.json + 2 fixtures")
PY

S=schemas/registry/topology/v1/topology.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/topology/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/topology/v1/fixtures/invalid-domain-lead-names-nothing.yaml >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry/topology
git commit -m "L1-02-07: topology.yaml v1 JSON Schema (Section 66.2)"
git push -u origin lane/1/02-t07-topology-schema
gh pr create --base integration --head lane/1/02-t07-topology-schema \
  --title "L1-02-07 topology.yaml v1 schema" --body "Phase 2 Lane 1. Section 66.2 block; succession block (13.1); three residual rules."
```

**SELF-VERIFY / acceptance:** lint `LINT-OK`; `valid.yaml` → `VALID` exit 0; the negative → `INVALID` exit 1; `python3 -c "import json; s=json.load(open('schemas/registry/topology/v1/topology.schema.json')); print(','.join(sorted(s['properties'].keys())))"` prints `activation_triggers,domains,domains_active,registry_version,succession`; foreign-path count `0`.

**STOP rule** — as Section 0.6.

**SELF-VERIFY**

```bash
# Confirm topology.yaml exists and is valid YAML
test -f schemas/topology.yaml && echo "topology.yaml exists"
python3 -c "import yaml; yaml.safe_load(open('schemas/topology.yaml'))" && echo "topology.yaml is valid YAML"
```

---

### L1-02-08 — `platform.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/platform/v1/platform.schema.json`
`schemas/registry/platform/v1/fixtures/valid.yaml`
`schemas/registry/platform/v1/fixtures/invalid-event-type-not-identifier.yaml`
`schemas/registry/platform/v1/fixtures/invalid-deprecated-version-without-deadline.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 60.1 (the YAML block), Section 60.2 (supported contract versions), Section 97.3 (the closed `event_type` enum lives here), Section 52.6 (`platform.yaml` row), Section 61.3 (canary set).

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `platform_version` | string | `^[0-9]+\.[0-9]+$` — the version field Section 60.2 names for the event-type enum | declared |
| `supported_contract_versions` | object | keys `product`, `verification`, `people_registry`, `service`; each an array of integers, minItems 1 | declared |
| `reusable_workflow_versions.current` | string | `^v[0-9]+$` | declared |
| `reusable_workflow_versions.supported[]` | array | `^v[0-9]+$` | declared |
| `reusable_workflow_versions.deprecated[]` | array | `^v[0-9]+$` | declared |
| `reusable_workflow_versions.deprecation_deadline` | object | additionalProperties = date; **every deprecated version must appear as a key** | declared |
| `canary_set[]` | array | productId, minItems 1 — "configurable, reviewed quarterly" (60.1); selection criteria in 61.3 | declared |
| `event_types[]` | array | `{ id: ^[a-z][a-z0-9_]*$, retired: boolean }`, uniqueItems, minItems 1 — **`minItems: 1` is what breaks `L1-05`'s `event_type: []` default (empty array fails validation); the correct seed uses `event_types:` from the contract** | declared |

**DERIVED fields:** none.

**The rule this schema encodes for `event_types` (Section 97.3):** *"Event types are identifiers, not prose … lower-case, underscore-separated, never renamed once shipped … Retiring an identifier marks it retired in the enum and never removes it."* The schema therefore enforces the identifier pattern and the presence of a `retired` boolean, and forbids additional properties on an entry.

**`x-residual-rule`:**
* `"Section 60.2: every version listed in supported_contract_versions must have a schema directory on disk at schemas/<family>/<artifact>/v<N>/."`
* `"Section 60.1: every entry in reusable_workflow_versions.deprecated must have a key in deprecation_deadline."`
* `"Section 97.3: control-plane CI rejects any event whose event_type is absent from this enum; a retired identifier is marked retired and never removed."`
* `"Section 53.1: the commit SHA each workflows/* tag resolves to is compared against this file; any change is Blocking-class drift."`

**Fixture:** `valid.yaml` is the Section 60.1 block verbatim plus an `event_types` list of exactly three entries (`plan_approved`, `production_deployed`, `drift_detected` — all three appear in the Section 97.3 tracked-events prose) each with `retired: false`. `invalid-event-type-not-identifier.yaml` uses `plan-approved` (hyphen). `invalid-deprecated-version-without-deadline.yaml` removes the `v2` key from `deprecation_deadline` while `v2` remains in `deprecated` — **note:** this rule is a residual rule and cannot be schema-encoded; instead this negative fixture removes `deprecation_deadline` entirely, which the schema requires.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/platform && { echo "STOP: schemas/registry/platform already exists"; exit 3; }

git checkout -b lane/1/02-t08-platform-schema
mkdir -p schemas/registry/platform/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/platform/v1/platform.schema.json",
  "title": "Platform Registry (platform.yaml) v1",
  "x-spec": "Sections 60.1, 60.2, 97.3, 52.6, 61.3",
  "x-residual-rule": [
    "Section 60.2: every version listed in supported_contract_versions must have a schema directory on disk at schemas/<family>/<artifact>/v<N>/.",
    "Section 60.1: every entry in reusable_workflow_versions.deprecated must have a key in deprecation_deadline.",
    "Section 97.3: control-plane CI rejects any event whose event_type is absent from this enum; a retired identifier is marked retired and never removed.",
    "Section 53.1: the commit SHA each workflows/* tag resolves to is compared against this file; any change is Blocking-class drift."
  ],
  "type": "object",
  "properties": {
    "platform_version": {"x-origin": "declared", "type": "string", "pattern": "^[0-9]+\\.[0-9]+$"},
    "supported_contract_versions": {"x-origin": "declared", "$ref": "#/$defs/supportedVersions"},
    "reusable_workflow_versions": {"x-origin": "declared", "$ref": "#/$defs/workflowVersions"},
    "canary_set": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"$ref": C + "#/$defs/productId"}},
    "event_types": {"x-origin": "declared", "type": "array", "minItems": 1, "uniqueItems": True,
      "items": {"$ref": "#/$defs/eventTypeEntry"}}
  },
  "required": ["platform_version","supported_contract_versions","reusable_workflow_versions","canary_set","event_types"],
  "additionalProperties": False,
  "$defs": {
    "supportedVersions": {
      "type": "object",
      "properties": {
        "product": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"type": "integer"}},
        "verification": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"type": "integer"}},
        "people_registry": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"type": "integer"}},
        "service": {"x-origin": "declared", "type": "array", "minItems": 1, "items": {"type": "integer"}}
      },
      "required": ["product","verification","people_registry","service"],
      "additionalProperties": False
    },
    "workflowVersions": {
      "type": "object",
      "properties": {
        "current": {"x-origin": "declared", "type": "string", "pattern": "^v[0-9]+$"},
        "supported": {"x-origin": "declared", "type": "array", "items": {"type": "string", "pattern": "^v[0-9]+$"}},
        "deprecated": {"x-origin": "declared", "type": "array", "items": {"type": "string", "pattern": "^v[0-9]+$"}},
        "deprecation_deadline": {"x-origin": "declared", "type": "object", "additionalProperties": {"type": "string", "format": "date"}}
      },
      "required": ["current","supported","deprecated","deprecation_deadline"],
      "additionalProperties": False
    },
    "eventTypeEntry": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "retired": {"x-origin": "declared", "type": "boolean"}
      },
      "required": ["id","retired"], "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/platform/v1/platform.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

# valid.yaml: Section 60.1 block verbatim + three event_types from Section 97.3
valid = {
  "platform_version": "1.0",
  "supported_contract_versions": {
    "product": [1, 2],
    "verification": [1],
    "people_registry": [1],
    "service": [1]
  },
  "reusable_workflow_versions": {
    "current": "v3",
    "supported": ["v3"],
    "deprecated": ["v2"],
    "deprecation_deadline": {"v2": "2026-12-31"}
  },
  "canary_set": ["product-1", "product-3"],
  "event_types": [
    {"id": "plan_approved", "retired": False},
    {"id": "production_deployed", "retired": False},
    {"id": "drift_detected", "retired": False}
  ]
}

pathlib.Path("schemas/registry/platform/v1/fixtures/valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: event_type id uses hyphen (not identifier pattern)
import copy
f1 = copy.deepcopy(valid)
f1["event_types"][0]["id"] = "plan-approved"
pathlib.Path("schemas/registry/platform/v1/fixtures/invalid-event-type-not-identifier.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: deprecation_deadline missing entirely while deprecated list is non-empty
f2 = copy.deepcopy(valid)
del f2["reusable_workflow_versions"]["deprecation_deadline"]
pathlib.Path("schemas/registry/platform/v1/fixtures/invalid-deprecated-version-without-deadline.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote platform.schema.json + 3 fixtures")
PY

S=schemas/registry/platform/v1/platform.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/platform/v1/fixtures/valid.yaml
for f in schemas/registry/platform/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/platform
git commit -m "L1-02-08: platform.yaml v1 JSON Schema (Sections 60.1, 97.3)"
git push -u origin lane/1/02-t08-platform-schema
gh pr create --base integration --head lane/1/02-t08-platform-schema \
  --title "L1-02-08 platform.yaml v1 schema" --body "Phase 2 Lane 1. Section 60.1 block; Section 97.3 event_type identifier pattern; four residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/platform/v1/platform.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/platform/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/platform/v1/platform.schema.json')); print(','.join(sorted(s['properties']['supported_contract_versions']['properties'].keys())))"
```

Correct output: `LINT-OK …`, `VALID`, then `people_registry,product,service,verification`.

**STOP rule** — do not populate `event_types` with more than the three identifiers named above. The full taxonomy has **86 taxonomy entries at L8963** and turning them into stable identifiers is a naming decision that binds L4's event writers. See DECISION-L1-02-B in Section 3.

---

### L1-02-09 — `os-health.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/os-health/v1/os-health.schema.json`
`schemas/registry/os-health/v1/fixtures/valid.yaml`
`schemas/registry/os-health/v1/fixtures/invalid-signal-class-not-in-scale.yaml`
`schemas/registry/os-health/v1/fixtures/invalid-signal-missing-known-limitations.yaml`
`schemas/registry/os-health/v1/fixtures/invalid-signal-missing-activation-dependency.yaml`

**Size:** L **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 52.2 (the unified signal table, forty-seven signals, and the D77 arming discipline), 52.4 (priority tiers and the CI check), 52.5, 53.4 (drift classes and the drift budget), 6.7 (the drift severity scale), 84.6 (the eight required metric attributes), 52.6 (`os-health.yaml` row: "Metric register").

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `drift_class_tolerances` | object | `amber_per_product` integer (53.4: "up to 2 open Amber per product"), `red_portfolio_flat` integer (53.4: "Red is deliberately held flat at 3 portfolio-wide"), `green` const `"unlimited"`, `blocking` const `"no-budget"` | declared |
| `signals[]` | array | minItems 1; one entry per SIG identifier | declared |
| `success_metrics[]` | array | Section 103 success metrics registered in this same file (84.6: "on every Section 103 success metric declared in that same file"); each is a `common#/$defs/metricDeclaration` plus an `id` | declared |

**`signals[]` entry — the full declaration (52.2 + 84.6 + D77):**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `id` | string | `^SIG-[0-9]{2}$` | declared |
| `name` | string | minLength 1 | declared |
| `priority` | string | `P0` \| `P1` \| `P2` — 52.4: "every SIG identifier … appears in exactly one priority tier" | declared |
| `states[]` | array | minItems 1; each `{ state: warn\|breach, class: driftClass }` — 6.7: "a graded signal declares a warn state and a breach state, and the class on breach is what the drift budget counts" | declared |
| `activation_dependency` | string | minLength 1 — D77, 52.2: "Every signal row … declares an `activation_dependency`" | declared |
| `lookback_window` | string | minLength 1 — 52.2: "Every `os-health.yaml` row therefore declares a `lookback_window` beside its `activation_dependency`" | declared |
| `definition`, `source`, `time_window`, `baseline`, `expected_interpretation`, `known_limitations`, `owner`, `action_on_breach` | — | the eight attributes of 84.6, via `common#/$defs/metricDeclaration` | declared |

`known_limitations` is `minLength: 1` because 84.6 states: *"`known_limitations` is never empty … a metric with no known limitation declares `none-known`."*

**DERIVED fields:** none. Section 52.2 states *"values are derived, never hand-maintained"* — the values are not fields of this file; every field of this file is a declaration.

**Schema-encoded rules:**
1. Every signal carries all eight of the 84.6 attributes plus `activation_dependency` and `lookback_window`.
2. Every `states[].class` is one of `Green | Amber | Red | Blocking` (6.7: any other value "fails control-plane CI validation").
3. Every signal carries exactly one `priority` from `P0 | P1 | P2`.
4. `signals[].id` is unique across the array (`uniqueItems` on a projection is not expressible — see residual rule).

**`x-residual-rule`:**
* `"Section 52.2: there are exactly forty-seven signals; the count and the identifier space SIG-01..SIG-47 are checked by the validator, not by the schema."`
* `"Section 52.4: a CI check validates that every SIG identifier appears in exactly one priority tier; an unassigned or doubly assigned signal fails validation of os-health.yaml."`
* `"Section 52.2 (D77): a signal arms only when its activation_dependency is live AND that source holds the full lookback_window; until both hold it renders unarmed and is excluded from drift-budget counts."`
* `"Section 53.4: Amber tolerance scales with the portfolio (2 per product); Red is held flat at 3 portfolio-wide and does not scale."`
* `"Section 84.6: a metric with no owner and no defined response is deleted; a metric with no time_window and no known_limitations is completed at the next calibration review or deleted."`

**Fixture:** `valid.yaml` declares `drift_class_tolerances` with the 53.4 initial values (`amber_per_product: 2`, `red_portfolio_flat: 3`) and **three** signals transcribed row-for-row from the Section 52.2 table — SIG-05 (Orphan risk, Registries, Blocking, Team Lead), SIG-07 (Team Lead bottleneck, DevLake, graded Amber/Red, Founder), SIG-17 (Restore-test currency, Control plane, Amber approaching / Blocking past, QA) — each completed with the eight 84.6 attributes, `activation_dependency` and `lookback_window`. Three, not forty-six: populating all forty-six is registry **data**, not schema, and belongs to the registry-population phase.

Negative fixtures: one signal with `class: Orange`; one with `known_limitations: ""`; one with `activation_dependency` deleted.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/os-health && { echo "STOP: schemas/registry/os-health already exists"; exit 3; }

git checkout -b lane/1/02-t09-os-health-schema
mkdir -p schemas/registry/os-health/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

signal_props = {
  "id": {"x-origin": "declared", "type": "string", "pattern": "^SIG-[0-9]{2}$"},
  "name": {"x-origin": "declared", "type": "string", "minLength": 1},
  "priority": {"x-origin": "declared", "type": "string", "enum": ["P0","P1","P2"]},
  "states": {"x-origin": "declared", "type": "array", "minItems": 1,
    "items": {"type": "object",
      "properties": {
        "state": {"x-origin": "declared", "type": "string", "enum": ["warn","breach"]},
        "class": {"x-origin": "declared", "$ref": C + "#/$defs/driftClass"}
      },
      "required": ["state","class"], "additionalProperties": False}},
  "activation_dependency": {"x-origin": "declared", "type": "string", "minLength": 1},
  "lookback_window": {"x-origin": "declared", "type": "string", "minLength": 1},
  "definition": {"x-origin": "declared", "type": "string", "minLength": 1},
  "source": {"x-origin": "declared", "type": "string", "minLength": 1},
  "time_window": {"x-origin": "declared", "type": "string", "minLength": 1},
  "baseline": {"x-origin": "declared", "type": ["string","number","null"]},
  "expected_interpretation": {"x-origin": "declared", "type": "string", "minLength": 1},
  "known_limitations": {"x-origin": "declared", "type": "string", "minLength": 1},
  "owner": {"x-origin": "declared", "type": "string", "minLength": 1},
  "action_on_breach": {"x-origin": "declared", "type": "string", "minLength": 1}
}

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/os-health/v1/os-health.schema.json",
  "title": "OS Health Registry (os-health.yaml) v1",
  "x-spec": "Sections 52.2 (D77), 52.4, 52.5, 53.4, 6.7, 84.6, 52.6",
  "x-residual-rule": [
    "Section 52.2: there are exactly forty-seven signals; the count and the identifier space SIG-01..SIG-47 are checked by the validator, not by the schema.",
    "Section 52.4: a CI check validates that every SIG identifier appears in exactly one priority tier; an unassigned or doubly assigned signal fails validation of os-health.yaml.",
    "Section 52.2 (D77): a signal arms only when its activation_dependency is live AND that source holds the full lookback_window; until both hold it renders unarmed and is excluded from drift-budget counts.",
    "Section 53.4: Amber tolerance scales with the portfolio (2 per product); Red is held flat at 3 portfolio-wide and does not scale.",
    "Section 84.6: a metric with no owner and no defined response is deleted; a metric with no time_window and no known_limitations is completed at the next calibration review or deleted."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "drift_class_tolerances": {"x-origin": "declared", "$ref": "#/$defs/driftTolerances"},
    "signals": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"type": "object", "properties": signal_props,
        "required": ["id","name","priority","states","activation_dependency","lookback_window",
                     "definition","source","time_window","baseline","expected_interpretation",
                     "known_limitations","owner","action_on_breach"],
        "additionalProperties": False}},
    "success_metrics": {"x-origin": "declared", "type": "array",
      "items": {"allOf": [{"$ref": C + "#/$defs/metricDeclaration"},
        {"type": "object", "properties": {"id": {"x-origin": "declared", "type": "string", "minLength": 1}},
         "required": ["id"]}]}}
  },
  "required": ["registry_version","drift_class_tolerances","signals"],
  "additionalProperties": False,
  "$defs": {
    "driftTolerances": {
      "type": "object",
      "properties": {
        "amber_per_product": {"x-origin": "declared", "type": "integer", "minimum": 0},
        "red_portfolio_flat": {"x-origin": "declared", "type": "integer", "minimum": 0},
        "green": {"x-origin": "declared", "type": "string", "const": "unlimited"},
        "blocking": {"x-origin": "declared", "type": "string", "const": "no-budget"}
      },
      "required": ["amber_per_product","red_portfolio_flat","green","blocking"],
      "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/os-health/v1/os-health.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

# Three signals transcribed row-for-row from Section 52.2 table
signals = [
  {
    "id": "SIG-05", "name": "Orphan risk", "priority": "P0",
    "states": [{"state": "breach", "class": "Blocking"}],
    "activation_dependency": "Registry populated with at least one product assignment",
    "lookback_window": "rolling 30 days",
    "definition": "A product or shared service has no active primary_owner assignment",
    "source": "control-plane registry",
    "time_window": "rolling 30 days",
    "baseline": None,
    "expected_interpretation": "Zero is the only acceptable count",
    "known_limitations": "none-known",
    "owner": "founder",
    "action_on_breach": "Raise SIG-05 Blocking; halt changes to affected product until assignment is made"
  },
  {
    "id": "SIG-07", "name": "Team Lead bottleneck", "priority": "P1",
    "states": [{"state": "warn", "class": "Amber"}, {"state": "breach", "class": "Red"}],
    "activation_dependency": "DevLake populated with at least 30 days of plan data",
    "lookback_window": "rolling 30 days",
    "definition": "Fraction of plan submissions awaiting Team Lead action beyond the gate SLA",
    "source": "DevLake",
    "time_window": "rolling 30 days",
    "baseline": None,
    "expected_interpretation": "Rising fraction indicates Team Lead capacity constraint",
    "known_limitations": "none-known",
    "owner": "founder",
    "action_on_breach": "Raise SIG-07 at its declared class; Team Lead reviews queue capacity"
  },
  {
    "id": "SIG-17", "name": "Restore-test currency", "priority": "P1",
    "states": [{"state": "warn", "class": "Amber"}, {"state": "breach", "class": "Blocking"}],
    "activation_dependency": "At least one product with a recovery block in product.yaml",
    "lookback_window": "rolling 90 days",
    "definition": "A product with a recovery block whose restore_tested date is older than 90 days",
    "source": "control-plane records/restore-tests/",
    "time_window": "rolling 90 days",
    "baseline": None,
    "expected_interpretation": "Zero products overdue is the target",
    "known_limitations": "none-known",
    "owner": "founder",
    "action_on_breach": "Raise SIG-17 at its declared class; schedule restore test immediately"
  }
]

valid = {
  "registry_version": 1,
  "drift_class_tolerances": {
    "amber_per_product": 2,
    "red_portfolio_flat": 3,
    "green": "unlimited",
    "blocking": "no-budget"
  },
  "signals": signals
}

base = pathlib.Path("schemas/registry/os-health/v1/fixtures")
pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: states[].class value not in driftClass enum
f1 = copy.deepcopy(valid)
f1["signals"][0]["states"][0]["class"] = "Orange"
pathlib.Path(base / "invalid-signal-class-not-in-scale.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: known_limitations is empty string (must be minLength 1)
f2 = copy.deepcopy(valid)
f2["signals"][0]["known_limitations"] = ""
pathlib.Path(base / "invalid-signal-missing-known-limitations.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: activation_dependency field deleted
f3 = copy.deepcopy(valid)
del f3["signals"][0]["activation_dependency"]
pathlib.Path(base / "invalid-signal-missing-activation-dependency.yaml").write_text(
    yaml.safe_dump(f3, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote os-health.schema.json + 4 fixtures")
PY

S=schemas/registry/os-health/v1/os-health.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/os-health/v1/fixtures/valid.yaml
for f in schemas/registry/os-health/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/os-health
git commit -m "L1-02-09: os-health.yaml v1 JSON Schema (Sections 52.2, 52.4, 53.4, 84.6)"
git push -u origin lane/1/02-t09-os-health-schema
gh pr create --base integration --head lane/1/02-t09-os-health-schema \
  --title "L1-02-09 os-health.yaml v1 schema" --body "Phase 2 Lane 1. Sections 52.2/84.6 signal structure; D77 activation_dependency required; five residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/os-health/v1/os-health.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/os-health/v1/fixtures/valid.yaml && \
for f in schemas/registry/os-health/v1/fixtures/invalid-*.yaml; do python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null; test $? -eq 1 && echo "NEGATIVE-OK $f" || { echo "NEGATIVE-FAIL $f"; exit 1; }; done
```

Correct output: `LINT-OK …`, `VALID`, then three `NEGATIVE-OK` lines and exit 0.

**STOP rule** — do not attempt to encode "exactly forty-seven signals" in the schema. It is a validator rule and it is already recorded as a residual rule. Do not invent thresholds for the three fixture signals beyond what the Section 52.2 table states; where the table gives no number, the fixture's `baseline` is `null` and `time_window` copies the definition's own window (e.g. SIG-17's is the rolling 90-day floor).

---

### L1-02-10 — `policies.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/policies/v1/policies.schema.json`
`schemas/registry/policies/v1/fixtures/valid.yaml`
`schemas/registry/policies/v1/fixtures/invalid-pilot-without-pilot-products.yaml`
`schemas/registry/policies/v1/fixtures/invalid-direct-enforce-without-justification.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 55.1 (the YAML block, transcribed field by field), 55.2 (rules), 55.3 (gradual enforcement), 55.4, invariant 78 (Section 101.10: "A new policy may not begin at Enforce unless it is a critical security control").

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `policies[].id` | string | `^POL-[A-Z0-9-]+$` | declared |
| `policies[].title` | string | minLength 1 | declared |
| `policies[].owner` | string | personId — 55.2: "Every policy has an owner" | declared |
| `policies[].purpose` | string | minLength 1 | declared |
| `policies[].origin` | string | the spec section it comes from | declared |
| `policies[].version` | integer | `>= 1` — 59.4 counts version increments as churn | declared |
| `policies[].effective_date` | date | | declared |
| `policies[].enforcement_stage` | string | `observe` \| `warn` \| `pilot` \| `enforce` | declared |
| `policies[].min_dwell` | object | `{ warn: integer days, pilot: integer delivery cycles }` — 55.3 default 14 / 1 | declared |
| `policies[].pilot_products` | array | productId; "required non-empty while stage is pilot" | declared |
| `policies[].entered_at_enforce_directly` | boolean | "true only for a critical security control; the label is auditable" | declared |
| `policies[].justification` | string \| null | "required when `entered_at_enforce_directly`" | declared |
| `policies[].exception_window_closes` | date \| null | named by Enforce (55.3) | declared |
| `policies[].supersedes` | string \| null | "the policy ID this one replaces (55.2)" | declared |
| `policies[].enforcement_mechanism` | string | minLength 1 | declared |
| `policies[].evidence` | object | `{ metric: string, baseline: string, current: string }` — 55.2: "Every policy states its evidence" | declared |
| `policies[].review_date` | date | 55.2: at most 12 months out, 6 months for a policy that blocks work (residual) | declared |
| `policies[].retirement_condition` | string | 55.2: "with a stated condition written when the policy is created" | declared |
| `policies[].exceptions_open` | integer | **DERIVED** | derived |
| `policies[].status` | string | `proposed` \| `active` \| `superseded` \| `withdrawn` \| `retired` | declared |

**DERIVED fields**

| Field | Producing job | Citation |
|---|---|---|
| `policies[].exceptions_open` | reconciliation, from `exceptions.yaml` | 55.1 — "DERIVED — reconciliation computes it from `exceptions.yaml`; never hand-edited" |

**Schema-encoded rules:**
1. `enforcement_stage: pilot` ⇒ `pilot_products` minItems 1 (55.3).
2. `enforcement_stage: enforce` ⇒ `exception_window_closes` is a date (55.3: "Enforce names the date its exception window closes").
3. `entered_at_enforce_directly: true` ⇒ `justification` is a non-empty string (55.3, invariant 78).

**`x-residual-rule`:**
* `"Section 55.2: review_date is at most 12 months out, and 6 months for any policy that blocks work."`
* `"Section 55.3: a stage transition recorded before its min_dwell has elapsed fails CI."`
* `"Section 55.2: supersedes must name an existing policy id, whose record is retained."`
* `"Section 55.1: full adoption is enforce with exception_window_closes in the past."`
* `"Section 101 (invariants): an invariant classified policy must name a live policies.yaml entry; control-plane CI fails otherwise."`

**Fixture:** `valid.yaml` is the Section 55.1 `POL-DEPLOY-FRIDAY` block verbatim, wrapped in `registry_version: 1` / `policies:`. Negatives: stage `pilot` with `pilot_products: []`; `entered_at_enforce_directly: true` with `justification: null`.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/policies && { echo "STOP: schemas/registry/policies already exists"; exit 3; }

git checkout -b lane/1/02-t10-policies-schema
mkdir -p schemas/registry/policies/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/policies/v1/policies.schema.json",
  "title": "Policy Registry (policies.yaml) v1",
  "x-spec": "Sections 55.1, 55.2, 55.3, 55.4; invariant 78",
  "x-residual-rule": [
    "Section 55.2: review_date is at most 12 months out, and 6 months for any policy that blocks work.",
    "Section 55.3: a stage transition recorded before its min_dwell has elapsed fails CI.",
    "Section 55.2: supersedes must name an existing policy id, whose record is retained.",
    "Section 55.1: full adoption is enforce with exception_window_closes in the past.",
    "Section 101 (invariants): an invariant classified policy must name a live policies.yaml entry; control-plane CI fails otherwise."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "policies": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"$ref": "#/$defs/policy"}}
  },
  "required": ["registry_version", "policies"],
  "additionalProperties": False,
  "$defs": {
    "policy": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "type": "string", "pattern": "^POL-[A-Z0-9-]+$"},
        "title": {"x-origin": "declared", "type": "string", "minLength": 1},
        "owner": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "purpose": {"x-origin": "declared", "type": "string", "minLength": 1},
        "origin": {"x-origin": "declared", "type": "string", "minLength": 1},
        "version": {"x-origin": "declared", "type": "integer", "minimum": 1},
        "effective_date": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "enforcement_stage": {"x-origin": "declared", "type": "string",
          "enum": ["observe","warn","pilot","enforce"]},
        "min_dwell": {"x-origin": "declared", "type": "object",
          "properties": {
            "warn": {"x-origin": "declared", "type": "integer", "minimum": 0},
            "pilot": {"x-origin": "declared", "type": "integer", "minimum": 0}
          },
          "required": ["warn","pilot"], "additionalProperties": False},
        "pilot_products": {"x-origin": "declared", "type": "array",
          "items": {"$ref": C + "#/$defs/productId"}},
        "entered_at_enforce_directly": {"x-origin": "declared", "type": "boolean"},
        "justification": {"x-origin": "declared", "type": ["string","null"]},
        "exception_window_closes": {"x-origin": "declared",
          "$ref": C + "#/$defs/nullableIsoDate"},
        "supersedes": {"x-origin": "declared", "type": ["string","null"]},
        "enforcement_mechanism": {"x-origin": "declared", "type": "string", "minLength": 1},
        "evidence": {"x-origin": "declared", "type": "object",
          "properties": {
            "metric": {"x-origin": "declared", "type": "string", "minLength": 1},
            "baseline": {"x-origin": "declared", "type": "string"},
            "current": {"x-origin": "declared", "type": "string"}
          },
          "required": ["metric","baseline","current"], "additionalProperties": False},
        "review_date": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "retirement_condition": {"x-origin": "declared", "type": "string", "minLength": 1},
        "exceptions_open": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 55.1: DERIVED — reconciliation computes it from exceptions.yaml; never hand-edited.",
          "type": "integer", "minimum": 0},
        "status": {"x-origin": "declared", "type": "string",
          "enum": ["proposed","active","superseded","withdrawn","retired"]}
      },
      "required": ["id","title","owner","purpose","origin","version","effective_date",
                   "enforcement_stage","min_dwell","pilot_products","entered_at_enforce_directly",
                   "justification","exception_window_closes","supersedes","enforcement_mechanism",
                   "evidence","review_date","retirement_condition","status"],
      "additionalProperties": False,
      "allOf": [
        {"$comment": "55.3: pilot stage requires at least one pilot product",
         "if": {"properties": {"enforcement_stage": {"const": "pilot"}},
                "required": ["enforcement_stage"]},
         "then": {"properties": {"pilot_products": {"minItems": 1}}}},
        {"$comment": "55.3: enforce stage requires exception_window_closes to be a date string",
         "if": {"properties": {"enforcement_stage": {"const": "enforce"}},
                "required": ["enforcement_stage"]},
         "then": {"properties": {"exception_window_closes": {"type": "string", "format": "date"}}}},
        {"$comment": "55.3 / invariant 78: direct enforce requires non-empty justification",
         "if": {"properties": {"entered_at_enforce_directly": {"const": True}},
                "required": ["entered_at_enforce_directly"]},
         "then": {"properties": {"justification": {"type": "string", "minLength": 1}}}}
      ]
    }
  }
}

pathlib.Path("schemas/registry/policies/v1/policies.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/policies/v1/fixtures")

valid = {
  "registry_version": 1,
  "policies": [{
    "id": "POL-DEPLOY-FRIDAY",
    "title": "No deployments on Friday",
    "owner": "dev-a",
    "purpose": "Prevent Friday afternoon deployments that cannot be rolled back before the weekend",
    "origin": "Section 55.1",
    "version": 1,
    "effective_date": "2025-06-01",
    "enforcement_stage": "enforce",
    "min_dwell": {"warn": 14, "pilot": 1},
    "pilot_products": [],
    "entered_at_enforce_directly": False,
    "justification": None,
    "exception_window_closes": "2026-12-31",
    "supersedes": None,
    "enforcement_mechanism": "CI gate rejects deployments to production after 12:00 UTC on Friday",
    "evidence": {
      "metric": "Friday production deployments per quarter",
      "baseline": "3",
      "current": "0"
    },
    "review_date": "2027-01-15",
    "retirement_condition": "Zero Friday deployments for four consecutive quarters with no linked incident",
    "exceptions_open": 0,
    "status": "active"
  }]
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
f1["policies"][0]["enforcement_stage"] = "pilot"
f1["policies"][0]["pilot_products"] = []
pathlib.Path(base / "invalid-pilot-without-pilot-products.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

f2 = copy.deepcopy(valid)
f2["policies"][0]["entered_at_enforce_directly"] = True
f2["policies"][0]["justification"] = None
pathlib.Path(base / "invalid-direct-enforce-without-justification.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote policies.schema.json + 3 fixtures")
PY

S=schemas/registry/policies/v1/policies.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/policies/v1/fixtures/valid.yaml
for f in schemas/registry/policies/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/policies
git commit -m "L1-02-10: policies.yaml v1 JSON Schema (Sections 55.1, 55.3, invariant 78)"
git push -u origin lane/1/02-t10-policies-schema
gh pr create --base integration --head lane/1/02-t10-policies-schema \
  --title "L1-02-10 policies.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 55.1 block; three schema-encoded rules; five residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/policies/v1/policies.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/policies/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/policies/v1/policies.schema.json')); p=s['properties']['policies']['items']['properties']; print(','.join(k for k,v in p.items() if v.get('x-origin')=='derived'))"
```

Correct output: `LINT-OK …`, `VALID`, then exactly `exceptions_open`.

**STOP rule** — as Section 0.6.

---

### L1-02-11 — `exceptions.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/exceptions/v1/exceptions.schema.json`
`schemas/registry/exceptions/v1/fixtures/valid.yaml`
`schemas/registry/exceptions/v1/fixtures/invalid-no-expiry.yaml`
`schemas/registry/exceptions/v1/fixtures/invalid-trigger-satisfied-on-wrong-type.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 54.1 (the YAML block), 54.2 (rules), 54.3 (authority mapping), 54.4 (break-glass), 54.5 (bootstrap), invariant 77 (Section 101.10: "Every exception has an expiry; an exception without one is invalid and fails CI").

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `exceptions[].id` | string | `^EXC-[0-9]{4}-[0-9]{3}$` | declared |
| `exceptions[].type` | string | `break_glass` \| `weekend_work` \| `platform_rollback` \| `founder_intervention` \| `support_extension` \| `temporary_access` \| `platform_compatibility` \| `emergency_production` \| `policy_waiver` \| `bootstrap` \| `founder_standing_delegation_activation` (the eleven of 54.1/54.3) | declared |
| `exceptions[].reason` | string | minLength 1 | declared |
| `exceptions[].requester` | string | personId | declared |
| `exceptions[].authority` | string | personId — "must hold the mapped capability" (54.3, residual) | declared |
| `exceptions[].affected` | object | `{ products: [productId], repositories: [string] }` | declared |
| `exceptions[].scope` | string | minLength 1 | declared |
| `exceptions[].start` | date | | declared |
| `exceptions[].expiry` | date | **mandatory** — invariant 77, 54.2 | declared |
| `exceptions[].compensating_control` | string | minLength 1; 54.2: "If the honest answer is 'none', that must be written" | declared |
| `exceptions[].compensating_control_record` | string | the store its execution lands in | declared |
| `exceptions[].compensating_control_cadence` | string | `weekly` \| `monthly` \| `per-push` \| `none` | declared |
| `exceptions[].owner` | string | personId — accountable for the compensating control | declared |
| `exceptions[].review_date` | date | | declared |
| `exceptions[].renewals` | integer | `>= 0` | **derived** |
| `exceptions[].became_permanent` | boolean | | declared |
| `exceptions[].closure` | string \| null | `expired` \| `remediated` \| `promoted_to_policy` \| `trigger_satisfied` \| null | declared |
| `exceptions[].deactivation_trigger` | string \| null | "mandatory for types that close on an event" | declared |

**DERIVED fields**

| Field | Producing job | Citation |
|---|---|---|
| `exceptions[].renewals` | reconciliation same-scope nomination | 54.2 — "A same-scope match nominated by reconciliation inherits the closed exception's renewal count automatically; dismissing a nomination is a recorded Founder decision" |

**Schema-encoded rules:**
1. `expiry` is required and is a date — invariant 77.
2. `closure: trigger_satisfied` ⇒ `type` in `[bootstrap, founder_standing_delegation_activation]` — 54.2: *"`trigger_satisfied` is available only to types that declare a `deactivation_trigger` — `bootstrap` and `founder_standing_delegation_activation`"*.
3. `type` in `[bootstrap, founder_standing_delegation_activation]` ⇒ `deactivation_trigger` is a non-empty string.

**`x-residual-rule`:**
* `"Section 54.2: a second renewal raises Amber, a third raises Red and forces remediate / promote-to-policy / re-affirm at the next quarterly review."`
* `"Section 54.2: an exception opened for a scope substantially matching one closed within the preceding two quarters counts as a renewal and inherits the closed exception's renewal count."`
* `"Section 54.2: reconciliation compares expected compensating-control executions against compensating_control_record; a missing execution makes the exception Blocking-class drift."`
* `"Section 54.2: post-use review is mandatory for break_glass and emergency_production within 5 working days."`
* `"Section 54.3: authority must hold the capability mapped to the exception type."`
* `"Section 54.4: break-glass duration is bounded at open - default 4 hours, maximum 24 - and revoked automatically by reconciliation."`
* `"Section 54.2: exception records are never deleted; they close with an outcome."`

**Fixture:** `valid.yaml` is the Section 54.1 `EXC-2026-041` block verbatim. Negatives: `expiry` deleted; `closure: trigger_satisfied` on `type: platform_compatibility`.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/exceptions && { echo "STOP: schemas/registry/exceptions already exists"; exit 3; }

git checkout -b lane/1/02-t11-exceptions-schema
mkdir -p schemas/registry/exceptions/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/exceptions/v1/exceptions.schema.json",
  "title": "Exception Registry (exceptions.yaml) v1",
  "x-spec": "Sections 54.1, 54.2, 54.3, 54.4, 54.5; invariant 77",
  "x-residual-rule": [
    "Section 54.2: a second renewal raises Amber, a third raises Red and forces remediate / promote-to-policy / re-affirm at the next quarterly review.",
    "Section 54.2: an exception opened for a scope substantially matching one closed within the preceding two quarters counts as a renewal and inherits the closed exception's renewal count.",
    "Section 54.2: reconciliation compares expected compensating-control executions against compensating_control_record; a missing execution makes the exception Blocking-class drift.",
    "Section 54.2: post-use review is mandatory for break_glass and emergency_production within 5 working days.",
    "Section 54.3: authority must hold the capability mapped to the exception type.",
    "Section 54.4: break-glass duration is bounded at open - default 4 hours, maximum 24 - and revoked automatically by reconciliation.",
    "Section 54.2: exception records are never deleted; they close with an outcome."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "exceptions": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"$ref": "#/$defs/exception"}}
  },
  "required": ["registry_version", "exceptions"],
  "additionalProperties": False,
  "$defs": {
    "exception": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "type": "string",
          "pattern": "^EXC-[0-9]{4}-[0-9]{3}$"},
        "type": {"x-origin": "declared", "type": "string", "enum": [
          "break_glass","weekend_work","platform_rollback","founder_intervention",
          "support_extension","temporary_access","platform_compatibility",
          "emergency_production","policy_waiver","bootstrap",
          "founder_standing_delegation_activation"]},
        "reason": {"x-origin": "declared", "type": "string", "minLength": 1},
        "requester": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "authority": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "affected": {"x-origin": "declared", "type": "object",
          "properties": {
            "products": {"x-origin": "declared", "type": "array",
              "items": {"$ref": C + "#/$defs/productId"}},
            "repositories": {"x-origin": "declared", "type": "array",
              "items": {"type": "string"}}
          },
          "additionalProperties": False},
        "scope": {"x-origin": "declared", "type": "string", "minLength": 1},
        "start": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "expiry": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "compensating_control": {"x-origin": "declared", "type": "string", "minLength": 1},
        "compensating_control_record": {"x-origin": "declared", "type": "string"},
        "compensating_control_cadence": {"x-origin": "declared", "type": "string",
          "enum": ["weekly","monthly","per-push","none"]},
        "owner": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "review_date": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "renewals": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 54.2: a same-scope match nominated by reconciliation inherits the closed exception's renewal count automatically.",
          "type": "integer", "minimum": 0},
        "became_permanent": {"x-origin": "declared", "type": "boolean"},
        "closure": {"x-origin": "declared",
          "oneOf": [{"type": "null"},
                    {"type": "string",
                     "enum": ["expired","remediated","promoted_to_policy","trigger_satisfied"]}]},
        "deactivation_trigger": {"x-origin": "declared", "type": ["string","null"]}
      },
      "required": ["id","type","reason","requester","authority","affected","scope",
                   "start","expiry","compensating_control","compensating_control_record",
                   "compensating_control_cadence","owner","review_date","renewals",
                   "became_permanent","closure","deactivation_trigger"],
      "additionalProperties": False,
      "allOf": [
        {"$comment": "54.2: trigger_satisfied closure is only valid for types that declare a deactivation_trigger",
         "if": {"properties": {"closure": {"const": "trigger_satisfied"}},
                "required": ["closure"]},
         "then": {"properties": {"type": {"enum": ["bootstrap","founder_standing_delegation_activation"]}}}},
        {"$comment": "54.2: bootstrap and founder_standing_delegation_activation require a non-empty deactivation_trigger",
         "if": {"properties": {"type": {"enum": ["bootstrap","founder_standing_delegation_activation"]}},
                "required": ["type"]},
         "then": {"properties": {"deactivation_trigger": {"type": "string", "minLength": 1}}}}
      ]
    }
  }
}

pathlib.Path("schemas/registry/exceptions/v1/exceptions.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/exceptions/v1/fixtures")

valid = {
  "registry_version": 1,
  "exceptions": [{
    "id": "EXC-2026-041",
    "type": "break_glass",
    "reason": "Production database connection pool exhausted; immediate manual rebalancing required",
    "requester": "dev-a",
    "authority": "dev-a",
    "affected": {
      "products": ["product-1"],
      "repositories": ["org/product-1-api"]
    },
    "scope": "product-1 production database connection pool",
    "start": "2026-04-14",
    "expiry": "2026-04-14",
    "compensating_control": "Post-use review within 5 working days; audit trail verified",
    "compensating_control_record": "records/exceptions/EXC-2026-041-review.yaml",
    "compensating_control_cadence": "per-push",
    "owner": "dev-a",
    "review_date": "2026-04-19",
    "renewals": 0,
    "became_permanent": False,
    "closure": "remediated",
    "deactivation_trigger": None
  }]
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
del f1["exceptions"][0]["expiry"]
pathlib.Path(base / "invalid-no-expiry.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

f2 = copy.deepcopy(valid)
f2["exceptions"][0]["type"] = "platform_compatibility"
f2["exceptions"][0]["closure"] = "trigger_satisfied"
pathlib.Path(base / "invalid-trigger-satisfied-on-wrong-type.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote exceptions.schema.json + 3 fixtures")
PY

S=schemas/registry/exceptions/v1/exceptions.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/exceptions/v1/fixtures/valid.yaml
for f in schemas/registry/exceptions/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/exceptions
git commit -m "L1-02-11: exceptions.yaml v1 JSON Schema (Sections 54.1, 54.2, invariant 77)"
git push -u origin lane/1/02-t11-exceptions-schema
gh pr create --base integration --head lane/1/02-t11-exceptions-schema \
  --title "L1-02-11 exceptions.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 54.1 block; invariant 77 expiry required; two schema-encoded allOf rules; seven residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/exceptions/v1/exceptions.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/exceptions/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/exceptions/v1/exceptions.schema.json')); print(len(s['properties']['exceptions']['items']['properties']['type']['enum']))"
```

Correct output: `LINT-OK …`, `VALID`, then `11`.

**STOP rule** — the type enum count is not 11. Do not add or remove a type; the eleven are fixed by the 54.1 comment block and the 54.3 authority table. File a blocker naming the discrepancy.

---

### L1-02-12 — `patterns.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/patterns/v1/patterns.schema.json`
`schemas/registry/patterns/v1/fixtures/valid.yaml`
`schemas/registry/patterns/v1/fixtures/invalid-remediation-be-more-careful.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 58.1 (the nine pattern classes), 58.2 (the pattern record), 58.3 (the six permitted remediations and the prohibition), 58.4 (the learning loop), Section 52.6 (`patterns.yaml` row: "Confirmed failure patterns and remediation links").

Section 58.2 describes the record in prose, not YAML. The field names below are **fixed by this plan** so no downstream consumer has to guess; they are ratified under DECISION-L1-02-C and the executor uses them literally.

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `patterns[].id` | string | `^PAT-[0-9]{4}-[0-9]{3}$` | declared |
| `patterns[].pattern_class` | string | the nine of 58.1: `repeated_migration_failure`, `repeated_rollback_one_product`, `repeated_review_finding_class`, `poor_ai_task_class`, `recurring_external_dependency_failure`, `recurring_exception`, `recurring_ready_queue_miss_one_product`, `recurring_break_glass`, `vendor_deprecation` | declared |
| `patterns[].occurrence_evidence[]` | array | minItems 1; each `{ occurred_on: date, record_ref: string }` — 58.2 "occurrence evidence" | declared |
| `patterns[].confirmed_root_class` | string | the eight of 58.4: `code`, `configuration`, `customer_integration`, `external_dependency`, `external_model_behaviour_change`, `process`, `knowledge`, `capacity` | declared |
| `patterns[].remediation_type` | string | the six of 58.3: `architecture_change`, `automation`, `permanent_test`, `policy_change`, `product_lifecycle_decision`, `staffing_decision` | declared |
| `patterns[].linked_work_item` | string | minLength 1 — 58.2 "the linked work item" | declared |
| `patterns[].closure_condition` | string | minLength 1 — 58.2: "a closure condition expressed as a measurable absence" | declared |
| `patterns[].confirmed_by` | string | personId — 58.1: "Humans confirm patterns; the machine only nominates" | declared |
| `patterns[].confirmed_on` | date | | declared |
| `patterns[].status` | string | `nominated` \| `confirmed` \| `closed` | declared |

**DERIVED fields:** none. The **nomination** is machine-produced (58.1) but a nominated record is not a confirmed pattern; the file holds confirmed records and their confirmer, all declared.

**Schema-encoded rule:** `remediation_type` is a closed enum of exactly the six of 58.3. This is how *"'Be more careful' is not a permitted remediation"* becomes machine-checkable rather than a slogan. The negative fixture sets `remediation_type: be_more_careful`.

**`x-residual-rule`:**
* `"Section 58.1: humans confirm patterns; the machine only nominates - a record may not enter status confirmed without confirmed_by and confirmed_on."`
* `"Section 54.2 / 58.1: recurring_exception is matched on scope and reason, not on identifier."`
* `"Section 58.4: an open postmortem older than 30 days with unclosed generated items is an Amber operating-system signal (SIG-47, unclosed learning-loop items)."`

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/patterns && { echo "STOP: schemas/registry/patterns already exists"; exit 3; }

git checkout -b lane/1/02-t12-patterns-schema
mkdir -p schemas/registry/patterns/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/patterns/v1/patterns.schema.json",
  "title": "Failure Pattern Registry (patterns.yaml) v1",
  "x-spec": "Sections 58.1, 58.2, 58.3, 58.4, 52.6",
  "x-residual-rule": [
    "Section 58.1: humans confirm patterns; the machine only nominates - a record may not enter status confirmed without confirmed_by and confirmed_on.",
    "Section 54.2 / 58.1: recurring_exception is matched on scope and reason, not on identifier.",
    "Section 58.4: an open postmortem older than 30 days with unclosed generated items is an Amber operating-system signal (SIG-47, unclosed learning-loop items)."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "patterns": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"$ref": "#/$defs/pattern"}}
  },
  "required": ["registry_version", "patterns"],
  "additionalProperties": False,
  "$defs": {
    "pattern": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "type": "string",
          "pattern": "^PAT-[0-9]{4}-[0-9]{3}$"},
        "pattern_class": {"x-origin": "declared", "type": "string", "enum": [
          "repeated_migration_failure",
          "repeated_rollback_one_product",
          "repeated_review_finding_class",
          "poor_ai_task_class",
          "recurring_external_dependency_failure",
          "recurring_exception",
          "recurring_ready_queue_miss_one_product",
          "recurring_break_glass",
          "vendor_deprecation"]},
        "occurrence_evidence": {"x-origin": "declared", "type": "array", "minItems": 1,
          "items": {"type": "object",
            "properties": {
              "occurred_on": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
              "record_ref": {"x-origin": "declared", "type": "string", "minLength": 1}
            },
            "required": ["occurred_on","record_ref"], "additionalProperties": False}},
        "confirmed_root_class": {"x-origin": "declared", "type": "string", "enum": [
          "code","configuration","customer_integration","external_dependency",
          "external_model_behaviour_change","process","knowledge","capacity"]},
        "remediation_type": {"x-origin": "declared", "type": "string", "enum": [
          "architecture_change","automation","permanent_test",
          "policy_change","product_lifecycle_decision","staffing_decision"]},
        "linked_work_item": {"x-origin": "declared", "type": "string", "minLength": 1},
        "closure_condition": {"x-origin": "declared", "type": "string", "minLength": 1},
        "confirmed_by": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "confirmed_on": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
        "status": {"x-origin": "declared", "type": "string",
          "enum": ["nominated","confirmed","closed"]}
      },
      "required": ["id","pattern_class","occurrence_evidence","confirmed_root_class",
                   "remediation_type","linked_work_item","closure_condition",
                   "confirmed_by","confirmed_on","status"],
      "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/patterns/v1/patterns.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/patterns/v1/fixtures")

valid = {
  "registry_version": 1,
  "patterns": [{
    "id": "PAT-2026-001",
    "pattern_class": "repeated_rollback_one_product",
    "occurrence_evidence": [
      {"occurred_on": "2026-01-10", "record_ref": "records/deployments/2026-01-10-product-3.yaml"},
      {"occurred_on": "2026-02-18", "record_ref": "records/deployments/2026-02-18-product-3.yaml"},
      {"occurred_on": "2026-03-04", "record_ref": "records/deployments/2026-03-04-product-3.yaml"}
    ],
    "confirmed_root_class": "configuration",
    "remediation_type": "permanent_test",
    "linked_work_item": "https://github.com/org/control-plane/issues/42",
    "closure_condition": "Zero rollbacks attributable to configuration mismatch on product-3 for two consecutive quarters",
    "confirmed_by": "dev-a",
    "confirmed_on": "2026-03-10",
    "status": "confirmed"
  }]
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
f1["patterns"][0]["remediation_type"] = "be_more_careful"
pathlib.Path(base / "invalid-remediation-be-more-careful.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote patterns.schema.json + 2 fixtures")
PY

S=schemas/registry/patterns/v1/patterns.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/patterns/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S \
  --instance schemas/registry/patterns/v1/fixtures/invalid-remediation-be-more-careful.yaml \
  >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry/patterns
git commit -m "L1-02-12: patterns.yaml v1 JSON Schema (Sections 58.1, 58.3, 58.4)"
git push -u origin lane/1/02-t12-patterns-schema
gh pr create --base integration --head lane/1/02-t12-patterns-schema \
  --title "L1-02-12 patterns.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 58.1 nine pattern classes; Section 58.3 six remediation types; Section 58.4 eight root classes; three residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/patterns/v1/patterns.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/patterns/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/patterns/v1/patterns.schema.json')); p=s['properties']['patterns']['items']['properties']; print(len(p['pattern_class']['enum']), len(p['remediation_type']['enum']), len(p['confirmed_root_class']['enum']))"
```

Correct output: `LINT-OK …`, `VALID`, then `9 6 8`.

**STOP rule** — any of the three counts differs from 9 / 6 / 8. They are transcriptions of the 58.1 table, the 58.3 list and the 58.4 root-cause line. File a blocker.

---

### L1-02-13 — `economics.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/economics/v1/economics.schema.json`
`schemas/registry/economics/v1/fixtures/valid.yaml`
`schemas/registry/economics/v1/fixtures/invalid-load-model-weight-out-of-range.yaml`
`schemas/registry/economics/v1/fixtures/invalid-ledger-entry-without-owner.yaml`

**Size:** L **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 68.1 (the `load_model` YAML block, verbatim), 57.1 (the automation ledger field table), 57.2 (the operating system's own standing entry), 50.1 (`control_plane_budget_band`), 67.1/67.2 (attention categories and weights), Section 52.6 (`economics.yaml` row: "Attention weights, load-model weights, automation ledger, cost inputs").

Only the `load_model` block appears as YAML in the spec; the ledger is a prose field table (57.1). Field names for the ledger and the standing entry are **fixed by this plan** under DECISION-L1-02-C.

**Top level**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `load_model` | object | the 68.1 block | mixed |
| `attention_weights` | object | keys = the eight `attentionCategory` values; each a number `>= 0` (52.6 "Attention weights") | declared |
| `control_plane_budget_band` | object | `common#/$defs/budgetBand` — 50.1: "one aggregate `control_plane_budget_band` on exactly the schema above (`expected`, `ceiling`, `currency`), declared in `economics.yaml` and owned by the Founder" | declared |
| `automation_ledger[]` | array | ledger entries, 57.1 | mixed |
| `operating_system_entry` | object | the standing entry of 57.2 | mixed |

**`load_model` (68.1, verbatim)**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `version` | integer | `>= 1` | declared |
| `calibrated` | date \| null | "set at first quarterly fit" | **derived** |
| `method` | string | minLength 1 | declared |
| `base` | number | `> 0` | declared |
| `factors` | object | exactly the ten keys `active_customers`, `revenue_importance`, `infrastructure_complexity`, `integration_count`, `deployment_frequency`, `support_model`, `security_requirements`, `verification_burden`, `incident_frequency`, `technology_diversity`; each `{ source: product.yaml\|derived\|devlake\|verification\|incidents, weight: number 0..1, scale: log\|band }` (`scale` optional — the 68.1 block omits it on three factors) | declared |

**`automation_ledger[]` (57.1)**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `id` | string | identifier | declared |
| `owner` | string | personId — 57.1: "Every ledger entry names its owner" | declared |
| `build_cost_hours` | number | `>= 0` — "Attention hours to create" | declared |
| `maintenance_cost_hours_per_quarter` | number | `>= 0` — "measured, not estimated" | **derived** |
| `failure_cost` | object | `{ incidents: int, false_alerts: int, blocked_work_hours: number }` | **derived** |
| `human_time_saved` | object | `{ before: string, after: string, net_per_week_hours: number, source_store: string }` — 57.1 requires the measured before-and-after pair and the store each field derives from | **derived** |
| `adoption` | object | `{ distinct_invoking_roles_per_quarter: int, source_store: string }` — 57.1: "derived from the event log … never named individuals" | **derived** |
| `net_value_per_quarter_hours` | number | "Saved minus maintenance minus failure cost, per quarter" | **derived** |
| `verdict` | string | `keep` \| `improve` \| `simplify` \| `retire` | declared |
| `unbaselined` | boolean | 57.1: "an entry whose Adoption field cannot name a store is not scored that quarter; it is recorded as unbaselined" | **derived** |

**`operating_system_entry` (57.2)**

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `phases[]` | array | each `{ phase: string, investment_gate_answers: object with the seven keys q1..q7 of 59.2, predicted_saving_hours_per_quarter: number, scoring_commitment_date: date }` — 57.2: "a hand-authored block … carrying the seven investment-gate answers per phase (Section 59.2), the predicted saving and a dated commitment to score it" | declared |
| `ritual_inventory[]` | array | strings — the enumerated standing rituals of 57.2 | declared |
| `ritual_attention_budget` | object | `{ budgeted_hours_per_quarter: number, measured_hours_per_quarter: number }` — 57.2: "budgeted hours per quarter against measured hours"; `measured_*` is derived | mixed |
| `cash_line` | object | `{ band_ref: "control_plane_budget_band", measured_spend: number }` — 57.2: "Beside it the entry carries a cash line"; `measured_spend` is derived | mixed |

**DERIVED fields — the complete list for this schema**

| Field | Producing job | Citation |
|---|---|---|
| `load_model.calibrated` | quarterly PLU weight refit | 68.1 — "`calibrated: null # set at first quarterly fit`"; 68.1 rule: "Each quarter the weights are refitted against observed attention hours per product" |
| `automation_ledger[].maintenance_cost_hours_per_quarter` | attention ledger | 57.1 — "Attention hours per quarter, measured, not estimated" |
| `automation_ledger[].failure_cost` | incident and alert records | 57.1 — "Incidents, false alerts, blocked work attributable to it" |
| `automation_ledger[].human_time_saved` | attention ledger before/after | 57.1 — "Measured before-and-after on the specific task it replaced" |
| `automation_ledger[].adoption` | event log (workflow-dispatch and job-run events) | 57.1 — "derived from the event log — workflow-dispatch and job-run events — never named individuals" |
| `automation_ledger[].net_value_per_quarter_hours` | computed | 57.1 — "Saved minus maintenance minus failure cost, per quarter" |
| `automation_ledger[].unbaselined` | quarterly scoring job | 57.1 — "an entry whose Adoption field cannot name a store is not scored that quarter; it is recorded as unbaselined" |
| `operating_system_entry.ritual_attention_budget.measured_hours_per_quarter` | attention ledger, ritual flag | 67.2 — the ritual flag "is set by the workflow or record that opens the ritual … never self-reported" |
| `operating_system_entry.cash_line.measured_spend` | provider billing ingest | 50.1 — "Provider billing data is ingested on the control-plane cadence" |

**Schema-encoded rules:** `factors` has exactly the ten named keys, `additionalProperties: false`; each `weight` is `0 <= w <= 1`; every ledger entry requires `owner` and `verdict`; `attention_weights` has exactly the eight category keys.

**`x-residual-rule`:**
* `"Section 68.1: the honesty rule - a load model that does not improve on a flat 1.0 per product is discarded rather than defended; the fit error is reported alongside the model each quarter."`
* `"Section 68.1: PLU inputs that read criticality read business.criticality from product.yaml, never classification.reliability_criticality."`
* `"Section 57.1: any automation with negative net value for two consecutive quarters is simplified or retired."`
* `"Section 57.1: every field of a ledger entry names the record store it derives from; an entry whose adoption field cannot name a store is recorded unbaselined and not scored."`
* `"Section 50.1: the control_plane_budget_band expected value is the sum of the per-asset cost bands declared in Sections 39 and 49, plus hardware amortisation."`
* `"Section 101.11 invariant 90 / Section 91: attention hours, utilisation and PLU are never individual performance evidence; no field of this file may be joined to a named individual on a general surface."`

**Fixture:** `valid.yaml` carries the 68.1 `load_model` block verbatim, an `attention_weights` map with all eight categories at `1.0`, a `control_plane_budget_band`, one `automation_ledger` entry (the Section 57.1 worked example: portfolio status gathering, 2h/week before, 15 minutes after, net 1.75h/week, 0.5h/quarter maintenance), and an `operating_system_entry` with one phase and the 57.2 ritual inventory.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/economics && { echo "STOP: schemas/registry/economics already exists"; exit 3; }

git checkout -b lane/1/02-t13-economics-schema
mkdir -p schemas/registry/economics/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

def _factor(declared=True):
    return {
      "type": "object",
      "properties": {
        "source": {"x-origin": "declared", "type": "string", "minLength": 1},
        "weight": {"x-origin": "declared", "type": "number", "minimum": 0, "maximum": 1},
        "scale": {"x-origin": "declared", "type": "string", "enum": ["log","band"]}
      },
      "required": ["source","weight"],
      "additionalProperties": False
    }

FACTORS = ["active_customers","revenue_importance","infrastructure_complexity",
           "integration_count","deployment_frequency","support_model",
           "security_requirements","verification_burden","incident_frequency",
           "technology_diversity"]

ATTENTION = ["engineering","review","verification","planning",
             "architecture","incident","operational","coordination"]

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/economics/v1/economics.schema.json",
  "title": "Economics Registry (economics.yaml) v1",
  "x-spec": "Sections 68.1, 57.1, 57.2, 50.1, 67.1, 67.2, 52.6",
  "x-residual-rule": [
    "Section 68.1: the honesty rule - a load model that does not improve on a flat 1.0 per product is discarded rather than defended; the fit error is reported alongside the model each quarter.",
    "Section 68.1: PLU inputs that read criticality read business.criticality from product.yaml, never classification.reliability_criticality.",
    "Section 57.1: any automation with negative net value for two consecutive quarters is simplified or retired.",
    "Section 57.1: every field of a ledger entry names the record store it derives from; an entry whose adoption field cannot name a store is recorded unbaselined and not scored.",
    "Section 50.1: the control_plane_budget_band expected value is the sum of the per-asset cost bands declared in Sections 39 and 49, plus hardware amortisation.",
    "Section 101.11 invariant 90 / Section 91: attention hours, utilisation and PLU are never individual performance evidence; no field of this file may be joined to a named individual on a general surface."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "load_model": {
      "x-origin": "declared", "type": "object",
      "properties": {
        "version": {"x-origin": "declared", "type": "integer", "minimum": 1},
        "calibrated": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 68.1: set at first quarterly fit; producing job = quarterly PLU weight refit.",
          "$ref": C + "#/$defs/nullableIsoDate"},
        "method": {"x-origin": "declared", "type": "string", "minLength": 1},
        "base": {"x-origin": "declared", "type": "number", "exclusiveMinimum": 0},
        "factors": {
          "x-origin": "declared", "type": "object",
          "properties": {k: {"x-origin": "declared", **_factor()} for k in FACTORS},
          "required": FACTORS, "additionalProperties": False}
      },
      "required": ["version","calibrated","method","base","factors"],
      "additionalProperties": False},
    "attention_weights": {
      "x-origin": "declared", "type": "object",
      "properties": {k: {"x-origin": "declared", "type": "number", "minimum": 0}
                     for k in ATTENTION},
      "required": ATTENTION, "additionalProperties": False},
    "control_plane_budget_band": {"x-origin": "declared", "$ref": C + "#/$defs/budgetBand"},
    "automation_ledger": {"x-origin": "declared", "type": "array",
      "items": {"$ref": "#/$defs/ledgerEntry"}},
    "operating_system_entry": {"x-origin": "declared", "$ref": "#/$defs/osEntry"}
  },
  "required": ["registry_version","load_model","attention_weights",
               "control_plane_budget_band"],
  "additionalProperties": False,
  "$defs": {
    "ledgerEntry": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "$ref": C + "#/$defs/identifier"},
        "owner": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
        "build_cost_hours": {"x-origin": "declared", "type": "number", "minimum": 0},
        "maintenance_cost_hours_per_quarter": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: attention hours per quarter, measured not estimated; producing job = attention ledger.",
          "type": "number", "minimum": 0},
        "failure_cost": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: incidents, false alerts, blocked work attributable to it; producing job = incident and alert records.",
          "type": "object",
          "properties": {
            "incidents": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "integer", "minimum": 0},
            "false_alerts": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "integer", "minimum": 0},
            "blocked_work_hours": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "number", "minimum": 0}
          },
          "required": ["incidents","false_alerts","blocked_work_hours"],
          "additionalProperties": False},
        "human_time_saved": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: measured before-and-after on the specific task it replaced; producing job = attention ledger.",
          "type": "object",
          "properties": {
            "before": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "string", "minLength": 1},
            "after": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "string", "minLength": 1},
            "net_per_week_hours": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "number"},
            "source_store": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "string", "minLength": 1}
          },
          "required": ["before","after","net_per_week_hours","source_store"],
          "additionalProperties": False},
        "adoption": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: derived from the event log - workflow-dispatch and job-run events - never named individuals.",
          "type": "object",
          "properties": {
            "distinct_invoking_roles_per_quarter": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "integer", "minimum": 0},
            "source_store": {"x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 57.1: as parent.", "type": "string", "minLength": 1}
          },
          "required": ["distinct_invoking_roles_per_quarter","source_store"],
          "additionalProperties": False},
        "net_value_per_quarter_hours": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: saved minus maintenance minus failure cost per quarter; producing job = quarterly scoring.",
          "type": "number"},
        "verdict": {"x-origin": "declared", "type": "string",
          "enum": ["keep","improve","simplify","retire"]},
        "unbaselined": {
          "x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 57.1: entry whose adoption field cannot name a store is not scored that quarter; producing job = quarterly scoring.",
          "type": "boolean"}
      },
      "required": ["id","owner","build_cost_hours","maintenance_cost_hours_per_quarter",
                   "failure_cost","human_time_saved","adoption","net_value_per_quarter_hours",
                   "verdict","unbaselined"],
      "additionalProperties": False
    },
    "osEntry": {
      "type": "object",
      "properties": {
        "phases": {"x-origin": "declared", "type": "array",
          "items": {"type": "object",
            "properties": {
              "phase": {"x-origin": "declared", "type": "string", "minLength": 1},
              "investment_gate_answers": {"x-origin": "declared", "type": "object",
                "properties": {
                  "q1": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q2": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q3": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q4": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q5": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q6": {"x-origin": "declared", "type": "string", "minLength": 1},
                  "q7": {"x-origin": "declared", "type": "string", "minLength": 1}
                },
                "required": ["q1","q2","q3","q4","q5","q6","q7"],
                "additionalProperties": False},
              "predicted_saving_hours_per_quarter": {"x-origin": "declared", "type": "number"},
              "scoring_commitment_date": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"}
            },
            "required": ["phase","investment_gate_answers","predicted_saving_hours_per_quarter",
                         "scoring_commitment_date"],
            "additionalProperties": False}},
        "ritual_inventory": {"x-origin": "declared", "type": "array",
          "items": {"type": "string", "minLength": 1}},
        "ritual_attention_budget": {"x-origin": "declared", "type": "object",
          "properties": {
            "budgeted_hours_per_quarter": {"x-origin": "declared", "type": "number", "minimum": 0},
            "measured_hours_per_quarter": {
              "x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 67.2: ritual flag set by the workflow or record that opens the ritual; producing job = attention ledger.",
              "type": "number", "minimum": 0}
          },
          "required": ["budgeted_hours_per_quarter","measured_hours_per_quarter"],
          "additionalProperties": False},
        "cash_line": {"x-origin": "declared", "type": "object",
          "properties": {
            "band_ref": {"x-origin": "declared", "type": "string", "const": "control_plane_budget_band"},
            "measured_spend": {
              "x-origin": "derived", "readOnly": True,
              "x-derived-from": "Section 50.1: provider billing data is ingested on the control-plane cadence; producing job = billing ingest.",
              "type": "number", "minimum": 0}
          },
          "required": ["band_ref","measured_spend"], "additionalProperties": False}
      },
      "required": ["phases","ritual_inventory","ritual_attention_budget","cash_line"],
      "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/economics/v1/economics.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/economics/v1/fixtures")

valid = {
  "registry_version": 1,
  "load_model": {
    "version": 1,
    "calibrated": None,
    "method": "weighted-sum-with-log-transforms",
    "base": 1.0,
    "factors": {
      "active_customers":          {"source": "product.yaml", "weight": 0.25, "scale": "log"},
      "revenue_importance":        {"source": "product.yaml", "weight": 0.20, "scale": "band"},
      "infrastructure_complexity": {"source": "derived",      "weight": 0.10},
      "integration_count":         {"source": "product.yaml", "weight": 0.10},
      "deployment_frequency":      {"source": "devlake",      "weight": 0.10},
      "support_model":             {"source": "product.yaml", "weight": 0.05, "scale": "band"},
      "security_requirements":     {"source": "product.yaml", "weight": 0.05},
      "verification_burden":       {"source": "verification", "weight": 0.05},
      "incident_frequency":        {"source": "incidents",    "weight": 0.05},
      "technology_diversity":      {"source": "derived",      "weight": 0.05}
    }
  },
  "attention_weights": {
    "engineering": 1.0, "review": 1.0, "verification": 1.0, "planning": 1.0,
    "architecture": 1.0, "incident": 1.0, "operational": 1.0, "coordination": 1.0
  },
  "control_plane_budget_band": {"currency": "USD", "expected": 800, "ceiling": 1100},
  "automation_ledger": [{
    "id": "status-reporter",
    "owner": "dev-a",
    "build_cost_hours": 12.0,
    "maintenance_cost_hours_per_quarter": 0.5,
    "failure_cost": {"incidents": 0, "false_alerts": 1, "blocked_work_hours": 0.5},
    "human_time_saved": {
      "before": "2h/week",
      "after": "15min/week",
      "net_per_week_hours": 1.75,
      "source_store": "records/attention/"
    },
    "adoption": {"distinct_invoking_roles_per_quarter": 3, "source_store": "events/"},
    "net_value_per_quarter_hours": 21.25,
    "verdict": "keep",
    "unbaselined": False
  }],
  "operating_system_entry": {
    "phases": [{
      "phase": "L1",
      "investment_gate_answers": {
        "q1": "Saves ~7h/week on portfolio status gathering across all products",
        "q2": "Removes Team Lead bottleneck from weekly status compilation",
        "q3": "All products and all team members benefit from consistent reporting",
        "q4": "8h estimated migration cost for each product adding structured status",
        "q5": "Low: script reads read-only registry files, no production writes",
        "q6": "Disable workflow and revert to manual status gathering",
        "q7": "Payback within 2 weeks at current portfolio size"
      },
      "predicted_saving_hours_per_quarter": 91.0,
      "scoring_commitment_date": "2025-09-30"
    }],
    "ritual_inventory": [
      "Quarterly control-plane review",
      "Monthly capacity check",
      "Weekly status report"
    ],
    "ritual_attention_budget": {
      "budgeted_hours_per_quarter": 12.0,
      "measured_hours_per_quarter": 10.5
    },
    "cash_line": {
      "band_ref": "control_plane_budget_band",
      "measured_spend": 420.0
    }
  }
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
f1["load_model"]["factors"]["active_customers"]["weight"] = 1.5
pathlib.Path(base / "invalid-load-model-weight-out-of-range.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

f2 = copy.deepcopy(valid)
del f2["automation_ledger"][0]["owner"]
pathlib.Path(base / "invalid-ledger-entry-without-owner.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote economics.schema.json + 3 fixtures")
PY

S=schemas/registry/economics/v1/economics.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/economics/v1/fixtures/valid.yaml
for f in schemas/registry/economics/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/economics
git commit -m "L1-02-13: economics.yaml v1 JSON Schema (Sections 68.1, 57.1, 57.2, 50.1, 67.2)"
git push -u origin lane/1/02-t13-economics-schema
gh pr create --base integration --head lane/1/02-t13-economics-schema \
  --title "L1-02-13 economics.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 68.1 load model (10 factors); Section 57.1 automation ledger; Section 57.2 OS entry; Section 67.2 attention weights (8 categories); six residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/economics/v1/economics.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/economics/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/economics/v1/economics.schema.json')); print(len(s['properties']['load_model']['properties']['factors']['properties']), len(s['properties']['attention_weights']['properties']))"
```

Correct output: `LINT-OK …`, `VALID`, then `10 8`.

**STOP rule** — the factor count is not 10 or the attention-category count is not 8. Both are verbatim transcriptions (68.1 block; 67.2 table). File a blocker.

---

### L1-02-14 — `platform-roadmap.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json`
`schemas/registry/platform-roadmap/v1/fixtures/valid.yaml`
`schemas/registry/platform-roadmap/v1/fixtures/invalid-initiative-missing-gate-answer.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 59.2 (the seven investment-gate questions), 59.3 (the `change_budget` YAML block, verbatim), 59.4 (churn metrics), Section 52.6 (`platform-roadmap.yaml` row: "Platform roadmap, investment gates, change budget"), SIG-45 (Section 52.2: "Change-budget breach … `platform-roadmap.yaml` plus the policy register").

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `change_budget.period` | string | `month` \| `quarter` | declared |
| `change_budget.max_platform_changes` | integer | `>= 0`; 59.3 initial value 4, "tunable, portfolio-wide scope" | declared |
| `change_budget.max_fleet_migrations` | integer | `>= 0`; 59.3 initial value 1 | declared |
| `change_budget.freeze_conditions[]` | array | strings; the three of 59.3 | declared |
| `initiatives[].id` | string | identifier | declared |
| `initiatives[].title` | string | minLength 1 | declared |
| `initiatives[].horizon` | string | `H1` \| `H2` \| `H3` (Section 29.2 horizons; 59.2: "goes back to H3 as a candidate, not forward into H2") | declared |
| `initiatives[].investment_gate` | object | the **seven** required answers, all `minLength 1`: `attention_saved_per_quarter`, `bottleneck_removed`, `products_benefiting`, `fleet_migration_cost_hours`, `failure_risk`, `rollback_path`, `payback` — 59.2: "Short answers are fine; missing answers are not" | declared |
| `initiatives[].status` | string | `candidate` \| `committed` \| `in_progress` \| `delivered` \| `abandoned` | declared |
| `churn` | object | the 59.4 rolling-two-quarter measures: `rules_changed` int, `changes_per_rule` object, `products_required_to_migrate` int, `migration_hours` number, `net_policy_growth` int | **derived** |

**DERIVED fields**

| Field | Producing job | Citation |
|---|---|---|
| `churn` (whole block) | churn detection job | 59.4 — "Measured over a rolling two quarters"; SIG-45 reads this file plus the policy register |

**Schema-encoded rule:** `investment_gate` requires all seven keys, each non-empty. 59.2: *"An initiative that cannot answer questions 1, 2 and 7 goes back to H3."* The schema requires all seven; the H3 consequence is a residual rule.

**`x-residual-rule`:**
* `"Section 59.2: an initiative that cannot answer questions 1, 2 and 7 goes back to H3 as a candidate, not forward into H2."`
* `"Section 59.2: every phase of this system's own build answers the same seven questions, and its answers land in the operating system's standing ledger entry in economics.yaml (Section 57.2)."`
* `"Section 59.3: exceeding the budget requires the Team Lead to defer something else, and the deferral is recorded. Critical security changes are outside the budget entirely."`
* `"Section 59.4: a rule changed three times in two quarters is unstable and is reverted to its last stable form or redesigned."`
* `"Section 52.2 SIG-45: platform changes or fleet migrations above the budget in the period, or net policy growth positive across a rolling two quarters, is an Amber signal."`

**Fixture:** `valid.yaml` carries the 59.3 `change_budget` block verbatim plus one initiative with all seven gate answers. The negative deletes `investment_gate.payback`.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/platform-roadmap && { echo "STOP: schemas/registry/platform-roadmap already exists"; exit 3; }

git checkout -b lane/1/02-t14-platform-roadmap-schema
mkdir -p schemas/registry/platform-roadmap/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

GATE_KEYS = ["attention_saved_per_quarter","bottleneck_removed","products_benefiting",
             "fleet_migration_cost_hours","failure_risk","rollback_path","payback"]

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json",
  "title": "Platform Roadmap Registry (platform-roadmap.yaml) v1",
  "x-spec": "Sections 59.2, 59.3, 59.4, 52.6; SIG-45",
  "x-residual-rule": [
    "Section 59.2: an initiative that cannot answer questions 1, 2 and 7 goes back to H3 as a candidate, not forward into H2.",
    "Section 59.2: every phase of this system's own build answers the same seven questions, and its answers land in the operating system's standing ledger entry in economics.yaml (Section 57.2).",
    "Section 59.3: exceeding the budget requires the Team Lead to defer something else, and the deferral is recorded. Critical security changes are outside the budget entirely.",
    "Section 59.4: a rule changed three times in two quarters is unstable and is reverted to its last stable form or redesigned.",
    "Section 52.2 SIG-45: platform changes or fleet migrations above the budget in the period, or net policy growth positive across a rolling two quarters, is an Amber signal."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "change_budget": {"x-origin": "declared", "type": "object",
      "properties": {
        "period": {"x-origin": "declared", "type": "string", "enum": ["month","quarter"]},
        "max_platform_changes": {"x-origin": "declared", "type": "integer", "minimum": 0},
        "max_fleet_migrations": {"x-origin": "declared", "type": "integer", "minimum": 0},
        "freeze_conditions": {"x-origin": "declared", "type": "array",
          "items": {"type": "string", "minLength": 1}}
      },
      "required": ["period","max_platform_changes","max_fleet_migrations","freeze_conditions"],
      "additionalProperties": False},
    "initiatives": {"x-origin": "declared", "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"x-origin": "declared", "$ref": C + "#/$defs/identifier"},
          "title": {"x-origin": "declared", "type": "string", "minLength": 1},
          "horizon": {"x-origin": "declared", "type": "string", "enum": ["H1","H2","H3"]},
          "investment_gate": {"x-origin": "declared", "type": "object",
            "properties": {k: {"x-origin": "declared", "type": "string", "minLength": 1}
                           for k in GATE_KEYS},
            "required": GATE_KEYS, "additionalProperties": False},
          "status": {"x-origin": "declared", "type": "string",
            "enum": ["candidate","committed","in_progress","delivered","abandoned"]}
        },
        "required": ["id","title","horizon","investment_gate","status"],
        "additionalProperties": False}},
    "churn": {
      "x-origin": "derived", "readOnly": True,
      "x-derived-from": "Section 59.4: measured over a rolling two quarters; producing job = churn detection job. SIG-45 reads this file plus the policy register.",
      "type": "object",
      "properties": {
        "rules_changed": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 59.4: as parent.", "type": "integer", "minimum": 0},
        "changes_per_rule": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 59.4: as parent.", "type": "object"},
        "products_required_to_migrate": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 59.4: as parent.", "type": "integer", "minimum": 0},
        "migration_hours": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 59.4: as parent.", "type": "number", "minimum": 0},
        "net_policy_growth": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 59.4: as parent.", "type": "integer"}
      },
      "additionalProperties": False}
  },
  "required": ["registry_version","change_budget","initiatives"],
  "additionalProperties": False
}

pathlib.Path("schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/platform-roadmap/v1/fixtures")

valid = {
  "registry_version": 1,
  "change_budget": {
    "period": "quarter",
    "max_platform_changes": 4,
    "max_fleet_migrations": 1,
    "freeze_conditions": [
      "Active incident at Red or Blocking drift class",
      "Unresolved Blocking-class drift signal",
      "Any product in unsupported contract version without a recorded migration plan"
    ]
  },
  "initiatives": [{
    "id": "gsd-v4-migration",
    "title": "Migrate fleet to GSD v4",
    "horizon": "H1",
    "investment_gate": {
      "attention_saved_per_quarter": "Removes ~3h/product/quarter of manual release-note formatting",
      "bottleneck_removed": "Eliminates Team Lead sign-off for routine release notes",
      "products_benefiting": "All 12 active products",
      "fleet_migration_cost_hours": "2h per product, 24h total",
      "failure_risk": "Low; GSD v4 is backward-compatible; rollback is a version-pin change",
      "rollback_path": "Revert gsd_version pin in product.yaml; no data migration",
      "payback": "Payback within one quarter across the portfolio"
    },
    "status": "committed"
  }],
  "churn": {
    "rules_changed": 2,
    "changes_per_rule": {"POL-DEPLOY-FRIDAY": 1, "POL-REVIEW-WINDOW": 1},
    "products_required_to_migrate": 0,
    "migration_hours": 0.0,
    "net_policy_growth": 1
  }
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
del f1["initiatives"][0]["investment_gate"]["payback"]
pathlib.Path(base / "invalid-initiative-missing-gate-answer.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote platform-roadmap.schema.json + 2 fixtures")
PY

S=schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/platform-roadmap/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S \
  --instance schemas/registry/platform-roadmap/v1/fixtures/invalid-initiative-missing-gate-answer.yaml \
  >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry/platform-roadmap
git commit -m "L1-02-14: platform-roadmap.yaml v1 JSON Schema (Sections 59.2, 59.3, 59.4)"
git push -u origin lane/1/02-t14-platform-roadmap-schema
gh pr create --base integration --head lane/1/02-t14-platform-roadmap-schema \
  --title "L1-02-14 platform-roadmap.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 59.3 change_budget block; Section 59.2 seven investment-gate answers required; churn block DERIVED; five residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/platform-roadmap/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/platform-roadmap/v1/platform-roadmap.schema.json')); print(len(s['properties']['initiatives']['items']['properties']['investment_gate']['required']))"
```

Correct output: `LINT-OK …`, `VALID`, then `7`.

**STOP rule** — the gate-answer count is not 7. Section 59.2 enumerates exactly seven questions. File a blocker.

---

### L1-02-15 — `tools.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/tools/v1/tools.schema.json`
`schemas/registry/tools/v1/fixtures/valid.yaml`
`schemas/registry/tools/v1/fixtures/invalid-criticality-outside-enumeration.yaml`
`schemas/registry/tools/v1/fixtures/invalid-tool-without-owner.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 62.1 (the YAML block, verbatim, including the three Hermes entries), 62.2 ("An unowned tool is a fossil"), Section 51.4 (control-plane patch cadence), Section 52.6 (`tools.yaml` row: "Tool register: owner, version, purpose, exit condition").

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `tools[].id` | string | identifier | declared |
| `tools[].purpose` | string | minLength 1 | declared |
| `tools[].owner` | string | personId — **required**; 62.2: "Every tool has an owner" | declared |
| `tools[].current_version` | string | minLength 1; a pinned tag or full commit SHA | declared |
| `tools[].upgrade_policy` | string | minLength 1 | declared |
| `tools[].replacement_candidates[]` | array | strings, optional | declared |
| `tools[].exit_condition` | string | minLength 1 — 62.1 requires it on every entry | declared |
| `tools[].last_reviewed` | date | optional | declared |
| `tools[].criticality` | string | `high` \| `medium` \| `low` — 62.1: "a tool entry whose `criticality` is absent or outside this enumeration fails control-plane CI validation" | declared |
| `tools[].data_touched` | string | optional; present on the Hermes entries | declared |
| `tools[].removal_consequence` | string | optional; present on the Hermes entries | declared |
| `tools[].patch_cadence` | string | optional; 62.1: the register "also carries the declared patch cadence for the control-plane stack" | declared |

**DERIVED fields:** none.

**`x-residual-rule`:**
* `"Section 62.1: criticality here is a tool-register field, never a product criticality field; no gate and no authority check reads it."`
* `"Section 62.2: ownerless tools are an Amber signal and are resolved at the quarterly review by assignment or retirement."`
* `"Section 36.3 / 62.1: any adopted agent harness or console carries its tools.yaml entry, with a declared patch cadence, before first use; there is no unregistered console."`
* `"Section 52.2 SIG-36: Grafana, DevLake or operations-VM OS behind the declared patch cadence is Amber; Red beyond twice the cadence."`

**Fixture:** `valid.yaml` is the Section 62.1 block verbatim — all four entries (`gsd`, `hermes-background-worker`, `hermes-ops-console`, `hermes-pr-review`) — wrapped in `registry_version: 1`. Negatives: `criticality: essential`; a tool entry with `owner` deleted.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/tools && { echo "STOP: schemas/registry/tools already exists"; exit 3; }

git checkout -b lane/1/02-t15-tools-schema
mkdir -p schemas/registry/tools/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/tools/v1/tools.schema.json",
  "title": "Tool Registry (tools.yaml) v1",
  "x-spec": "Sections 62.1, 62.2, 51.4, 52.6",
  "x-residual-rule": [
    "Section 62.1: criticality here is a tool-register field, never a product criticality field; no gate and no authority check reads it.",
    "Section 62.2: ownerless tools are an Amber signal and are resolved at the quarterly review by assignment or retirement.",
    "Section 36.3 / 62.1: any adopted agent harness or console carries its tools.yaml entry, with a declared patch cadence, before first use; there is no unregistered console.",
    "Section 52.2 SIG-36: Grafana, DevLake or operations-VM OS behind the declared patch cadence is Amber; Red beyond twice the cadence."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "tools": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {
        "type": "object",
        "properties": {
          "id": {"x-origin": "declared", "$ref": C + "#/$defs/identifier"},
          "purpose": {"x-origin": "declared", "type": "string", "minLength": 1},
          "owner": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
          "current_version": {"x-origin": "declared", "type": "string", "minLength": 1},
          "upgrade_policy": {"x-origin": "declared", "type": "string", "minLength": 1},
          "replacement_candidates": {"x-origin": "declared", "type": "array",
            "items": {"type": "string"}},
          "exit_condition": {"x-origin": "declared", "type": "string", "minLength": 1},
          "last_reviewed": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
          "criticality": {"x-origin": "declared", "type": "string",
            "enum": ["high","medium","low"]},
          "data_touched": {"x-origin": "declared", "type": "string"},
          "removal_consequence": {"x-origin": "declared", "type": "string"},
          "patch_cadence": {"x-origin": "declared", "type": "string"}
        },
        "required": ["id","purpose","owner","current_version","upgrade_policy",
                     "exit_condition","criticality"],
        "additionalProperties": False}}
  },
  "required": ["registry_version","tools"],
  "additionalProperties": False
}

pathlib.Path("schemas/registry/tools/v1/tools.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/tools/v1/fixtures")

valid = {
  "registry_version": 1,
  "tools": [
    {
      "id": "gsd",
      "purpose": "Golden-standard deployment workflow; enforces the deployment contract for every product",
      "owner": "dev-a",
      "current_version": "v3.1.0",
      "upgrade_policy": "Patch releases applied within 7 days; minor releases tested on canary first",
      "replacement_candidates": [],
      "exit_condition": "Replaced by a successor workflow that passes the full GSD acceptance suite",
      "last_reviewed": "2026-04-01",
      "criticality": "high",
      "patch_cadence": "monthly"
    },
    {
      "id": "hermes-background-worker",
      "purpose": "Executes registry reconciliation, drift detection and automation-ledger scoring",
      "owner": "dev-a",
      "current_version": "8e9459c97f707047be5915a5c8b4c503756daa9b",
      "upgrade_policy": "SHA updated only through the normal dependency-update workflow; harness self-update is never run",
      "replacement_candidates": [],
      "exit_condition": "Replaced by a verifiably equivalent tool that passes the full Hermes acceptance suite",
      "last_reviewed": "2026-04-01",
      "criticality": "high",
      "data_touched": "control-plane registry files (read-write)",
      "removal_consequence": "Drift detection, reconciliation and automation scoring cease; OS health signals go unarmed",
      "patch_cadence": "monthly"
    },
    {
      "id": "hermes-ops-console",
      "purpose": "Operator-facing read interface for control-plane registry state and drift status",
      "owner": "dev-a",
      "current_version": "8e9459c97f707047be5915a5c8b4c503756daa9b",
      "upgrade_policy": "SHA updated only through the normal dependency-update workflow",
      "replacement_candidates": [],
      "exit_condition": "Replaced by a successor console that passes the full ops-console acceptance suite",
      "last_reviewed": "2026-04-01",
      "criticality": "medium",
      "data_touched": "control-plane registry files (read-only)",
      "removal_consequence": "Operators fall back to direct file reads; no automated summarisation"
    },
    {
      "id": "hermes-pr-review",
      "purpose": "Automated pre-merge lint and schema validation on pull requests touching registry files",
      "owner": "dev-a",
      "current_version": "8e9459c97f707047be5915a5c8b4c503756daa9b",
      "upgrade_policy": "SHA updated only through the normal dependency-update workflow",
      "replacement_candidates": [],
      "exit_condition": "Replaced by an equivalent CI job that achieves equivalent lint and validation coverage",
      "last_reviewed": "2026-04-01",
      "criticality": "medium",
      "data_touched": "pull request diff (read-only)",
      "removal_consequence": "Schema and lint errors reach integration branch rather than being caught at PR"
    }
  ]
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

f1 = copy.deepcopy(valid)
f1["tools"][0]["criticality"] = "essential"
pathlib.Path(base / "invalid-criticality-outside-enumeration.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

f2 = copy.deepcopy(valid)
del f2["tools"][0]["owner"]
pathlib.Path(base / "invalid-tool-without-owner.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote tools.schema.json + 3 fixtures")
PY

S=schemas/registry/tools/v1/tools.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/tools/v1/fixtures/valid.yaml
for f in schemas/registry/tools/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/tools
git commit -m "L1-02-15: tools.yaml v1 JSON Schema (Sections 62.1, 62.2)"
git push -u origin lane/1/02-t15-tools-schema
gh pr create --base integration --head lane/1/02-t15-tools-schema \
  --title "L1-02-15 tools.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 62.1 block (four entries); criticality enum enforced; owner and exit_condition required; four residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/tools/v1/tools.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/tools/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/tools/v1/tools.schema.json')); r=s['properties']['tools']['items']; print(','.join(r['properties']['criticality']['enum']), 'owner' in r['required'], 'exit_condition' in r['required'])"
```

Correct output: `LINT-OK …`, `VALID`, then `high,medium,low true true`.

**STOP rule** — as Section 0.6.

---

### L1-02-16 — `ai-toolchain.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

> **OUT-OF-SCOPE (FD-058):** Charter section 12, DECISION REQUIRED #1 explicitly states "Do not create it. Do not reference it in any validator."
> This task is not executed. The artifact [ai-toolchain.yaml] is not authored by L1. See FD-058 for the decision record.

**Creates**
`schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json`
`schemas/registry/ai-toolchain/v1/fixtures/valid.yaml`
`schemas/registry/ai-toolchain/v1/fixtures/invalid-mcp-server-pinned-by-tag.yaml`

**Size:** S **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 36.3 (the YAML block, verbatim), Section 35.2 (approved runtime list as configuration), Section 52.6 (`ai-toolchain.yaml` row), invariant 85 (Section 101.11: third-party components pinned by full commit SHA; "a tag is movable and is therefore not a pin").

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `registry_version` | integer | `>= 1` | declared |
| `runtimes` | object | keys are runtime identifiers (`claude-code`, `cursor`, `hermes-agent` in the 36.3 block); the key set is **not closed** — 35.2: "Approved runtime list — configuration, not architecture" | declared |
| `runtimes.<id>.source` | string | optional; full commit SHA `^[0-9a-f]{40}$` where present — 36.3: "full SHA — never a tag, branch or 'latest'" | declared |
| `runtimes.<id>.python_environment` | string | optional | declared |
| `runtimes.<id>.approved_extensions[]` | array | each `{ name: string, source: string, checksum: string }`; `approved_extensions: []` is a legal, meaningful value ("none approved beyond the runtime itself") | declared |
| `runtimes.<id>.approved_mcp_servers[]` | array | each `{ name: string, source: string, access: string }`; `source` must match `^[0-9a-f]{40}$` **or** `^sha256:[0-9a-f]{64}$` — 36.3: "pinned by full commit SHA or content checksum, never by tag" | declared |
| `model_artifacts[]` | array | each `{ id: string, checksum: ^sha256:[0-9a-f]{64}$, mirrored_at: string }` — 36.3: "The quantised open-weight model file … is pinned by content checksum, mirrored into the company organisation at that checksum, and verified at load" | declared |

**DERIVED fields:** none.

**Schema-encoded rule:** every `source` on an MCP server and every `checksum` on a model artifact matches the SHA/checksum pattern. The negative fixture pins an MCP server at `v1.2.0`.

**`x-residual-rule`:**
* `"Section 36.3: anything not on the list is not installed; approval is a recorded decision naming the source pin and the access the component holds."`
* `"Section 36.3: the pinned repository and its locked dependency set are mirrored into the company organisation at the pin, and installs fetch from the mirror, never from upstream."`
* `"Section 36.3: onboarding installs only listed components; the quarterly workstation check (36.6) verifies nothing unlisted has accumulated."`
* `"Section 36.3: the harness self-update command is never run on any instance; updates arrive only by moving the pinned SHA through the normal dependency-update workflow."`

**Fixture:** `valid.yaml` is the Section 36.3 block verbatim, with the `github-mcp` `source` written as the literal 40-hex-character form the block's comment requires (`source: 0000000000000000000000000000000000000000` is not acceptable — use the Hermes SHA `8e9459c97f707047be5915a5c8b4c503756daa9b`, which is the only full SHA the spec supplies), and `registry_version: 1` added.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/ai-toolchain && { echo "STOP: schemas/registry/ai-toolchain already exists"; exit 3; }

git checkout -b lane/1/02-t16-ai-toolchain-schema
mkdir -p schemas/registry/ai-toolchain/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"
SHA40 = "^[0-9a-f]{40}$"
SHA256 = "^sha256:[0-9a-f]{64}$"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json",
  "title": "AI Toolchain Registry (ai-toolchain.yaml) v1",
  "x-spec": "Sections 36.3, 35.2, 52.6; invariant 85",
  "x-residual-rule": [
    "Section 36.3: anything not on the list is not installed; approval is a recorded decision naming the source pin and the access the component holds.",
    "Section 36.3: the pinned repository and its locked dependency set are mirrored into the company organisation at the pin, and installs fetch from the mirror, never from upstream.",
    "Section 36.3: onboarding installs only listed components; the quarterly workstation check (36.6) verifies nothing unlisted has accumulated.",
    "Section 36.3: the harness self-update command is never run on any instance; updates arrive only by moving the pinned SHA through the normal dependency-update workflow."
  ],
  "type": "object",
  "properties": {
    "registry_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "runtimes": {"x-origin": "declared", "type": "object",
      "additionalProperties": {"$ref": "#/$defs/runtimeEntry"}},
    "model_artifacts": {"x-origin": "declared", "type": "array",
      "items": {"$ref": "#/$defs/modelArtifact"}}
  },
  "required": ["registry_version","runtimes"],
  "additionalProperties": False,
  "$defs": {
    "runtimeEntry": {
      "type": "object",
      "properties": {
        "source": {"x-origin": "declared", "type": "string", "pattern": SHA40},
        "python_environment": {"x-origin": "declared", "type": "string"},
        "approved_extensions": {"x-origin": "declared", "type": "array",
          "items": {"type": "object",
            "properties": {
              "name": {"x-origin": "declared", "type": "string", "minLength": 1},
              "source": {"x-origin": "declared", "type": "string", "minLength": 1},
              "checksum": {"x-origin": "declared", "type": "string", "minLength": 1}
            },
            "required": ["name","source","checksum"], "additionalProperties": False}},
        "approved_mcp_servers": {"x-origin": "declared", "type": "array",
          "items": {"$ref": "#/$defs/mcpServer"}}
      },
      "additionalProperties": False
    },
    "mcpServer": {
      "type": "object",
      "properties": {
        "name": {"x-origin": "declared", "type": "string", "minLength": 1},
        "source": {"x-origin": "declared", "type": "string",
          "oneOf": [{"pattern": SHA40}, {"pattern": SHA256}]},
        "access": {"x-origin": "declared", "type": "string", "minLength": 1}
      },
      "required": ["name","source","access"], "additionalProperties": False
    },
    "modelArtifact": {
      "type": "object",
      "properties": {
        "id": {"x-origin": "declared", "type": "string", "minLength": 1},
        "checksum": {"x-origin": "declared", "type": "string", "pattern": SHA256},
        "mirrored_at": {"x-origin": "declared", "type": "string", "minLength": 1}
      },
      "required": ["id","checksum","mirrored_at"], "additionalProperties": False
    }
  }
}

pathlib.Path("schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/ai-toolchain/v1/fixtures")

# Section 36.3 block verbatim; github-mcp source uses the Hermes SHA the spec supplies
valid = {
  "registry_version": 1,
  "runtimes": {
    "claude-code": {
      "source": "8e9459c97f707047be5915a5c8b4c503756daa9b",
      "approved_extensions": [],
      "approved_mcp_servers": [
        {
          "name": "github-mcp",
          "source": "8e9459c97f707047be5915a5c8b4c503756daa9b",
          "access": "read-only: repository metadata and pull request data"
        }
      ]
    },
    "cursor": {
      "approved_extensions": [],
      "approved_mcp_servers": []
    },
    "hermes-agent": {
      "source": "8e9459c97f707047be5915a5c8b4c503756daa9b",
      "python_environment": "python3.12 venv pinned at requirements.lock",
      "approved_extensions": [],
      "approved_mcp_servers": []
    }
  }
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: MCP server source is a tag (not a SHA)
f1 = copy.deepcopy(valid)
f1["runtimes"]["claude-code"]["approved_mcp_servers"][0]["source"] = "v1.2.0"
pathlib.Path(base / "invalid-mcp-server-pinned-by-tag.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote ai-toolchain.schema.json + 2 fixtures")
PY

S=schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/ai-toolchain/v1/fixtures/valid.yaml
python3 validators/registry/schema-check/check.py --schema $S \
  --instance schemas/registry/ai-toolchain/v1/fixtures/invalid-mcp-server-pinned-by-tag.yaml \
  >/dev/null && { echo "NEGATIVE-FAIL"; exit 1; } || echo "NEGATIVE-OK"

git add schemas/registry/ai-toolchain
git commit -m "L1-02-16: ai-toolchain.yaml v1 JSON Schema (Section 36.3, invariant 85)"
git push -u origin lane/1/02-t16-ai-toolchain-schema
gh pr create --base integration --head lane/1/02-t16-ai-toolchain-schema \
  --title "L1-02-16 ai-toolchain.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 36.3 block; SHA-pin pattern enforced on MCP server sources; open runtimes key set (Section 35.2); four residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/ai-toolchain/v1/fixtures/valid.yaml && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/ai-toolchain/v1/fixtures/invalid-mcp-server-pinned-by-tag.yaml; echo "EXIT=$?"
```

Correct output: `LINT-OK …`, `VALID`, `INVALID`, `EXIT=1`.

**STOP rule** — as Section 0.6. Do not close the `runtimes` key set; Section 35.2 makes it configuration.

---

### L1-02-17 — `scenarios/*.yaml` schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

> **OUT-OF-SCOPE (FD-058):** Charter section 12, DECISION REQUIRED #3 explicitly states "L1 default pending answer. Do not create it."
> This task is not executed. The artifact [scenarios/*] is not authored by L1. See FD-058 for the decision record.

**Creates**
`schemas/registry/scenarios/v1/scenario.schema.json`
`schemas/registry/scenarios/v1/fixtures/valid.yaml`
`schemas/registry/scenarios/v1/fixtures/invalid-unknown-primitive.yaml`
`schemas/registry/scenarios/v1/fixtures/invalid-add-person-without-ramp.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 72.5 (the YAML block and the supported scenario primitives), 72.6 (the automated quarterly bus-factor scenario), 72.7, Section 52.6 (`scenarios/*.yaml` row, Founder-owned).

One file per scenario (PARTITION.md rule 3: directory-per-item, no shared mutable index).

| Field | Type | Constraint | Origin |
|---|---|---|---|
| `scenario_version` | integer | `>= 1` | declared |
| `scenario` | string | minLength 1 — the human title, from the 72.5 block | declared |
| `baseline` | date | the baseline date the projection runs against | declared |
| `changes[]` | array | minItems 1; each entry is a single-key object naming one **supported scenario primitive** | declared |
| `outputs_requested[]` | array | minItems 1; strings | declared |
| `assumptions[]` | array | strings; 72.5 mandatory honesty rule: "every scenario states its assumptions" | declared |
| `weakest_assumption` | string | 72.5: "the weakest assumption flagged" | declared |

**Supported scenario primitives — the closed set of `changes[]` keys, transcribed from the 72.5 bullet list:**
`add_person`, `remove_person`, `change_assignment_set`, `change_ramp_state`, `move_review_load`, `change_product_criticality`, `change_product_support_model`, `change_product_lifecycle`, `add_products_of_plu_profile`, `move_product_to_24x7`, `defer_platform_initiative`, `accelerate_platform_initiative`

`add_person` shape (from the 72.5 block): `{ role: roleId, capacity_hours_per_week: number, ramp: { weeks: integer, effective_start: number 0..1 } }`.

**DERIVED fields:** none. The scenario file is input; the three-column output (current, projected, delta) is a generated report, not a file field (72.5).

**Schema-encoded rules:**
1. `changes[]` entries have exactly one key, drawn from the closed primitive set (`minProperties: 1`, `maxProperties: 1`, `additionalProperties: false` against the named primitives).
2. `add_person` requires `ramp` — 72.5 mandatory honesty rule: *"every scenario that adds a person shows the effect of onboarding ramp."*

**`x-residual-rule`:**
* `"Section 72.5: output format is always the same three columns - current, projected, delta - with the assumptions listed and the weakest assumption flagged."`
* `"Section 72.5: the standing one-click scenario set is auto-regenerated quarterly against the current baseline by the scenario job; the Founder owns the files."`
* `"Section 72.6: the remove-one-person scenario is run automatically each quarter for every person."`
* `"Section 72.7: a forecast never triggers an automatic action of any kind; it creates a decision prompt, and the decision is recorded."`
* `"Section 72.5: no scenario claims precision beyond its inputs."`

**Fixture:** `valid.yaml` is the Section 72.5 `2026-q3-add-qa` block verbatim, plus `scenario_version: 1`, an `assumptions` list and a `weakest_assumption` string (72.5 makes both mandatory in prose; the schema makes them required). Negatives: a `changes[]` entry keyed `hire_contractor`; an `add_person` entry with `ramp` deleted.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/scenarios && { echo "STOP: schemas/registry/scenarios already exists"; exit 3; }

git checkout -b lane/1/02-t17-scenario-schema
mkdir -p schemas/registry/scenarios/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

# Twelve supported scenario primitives from Section 72.5
PRIMITIVES = [
  "add_person", "remove_person", "change_assignment_set", "change_ramp_state",
  "move_review_load", "change_product_criticality", "change_product_support_model",
  "change_product_lifecycle", "add_products_of_plu_profile", "move_product_to_24x7",
  "defer_platform_initiative", "accelerate_platform_initiative"
]

def _simple_primitive():
    return {"x-origin": "declared", "type": "object", "additionalProperties": True}

change_entry_props = {p: _simple_primitive() for p in PRIMITIVES}

# add_person has a richer shape and requires ramp (72.5 mandatory honesty rule)
change_entry_props["add_person"] = {
  "x-origin": "declared", "type": "object",
  "properties": {
    "role": {"x-origin": "declared", "$ref": C + "#/$defs/roleId"},
    "capacity_hours_per_week": {"x-origin": "declared", "type": "number", "minimum": 0},
    "ramp": {"x-origin": "declared", "type": "object",
      "properties": {
        "weeks": {"x-origin": "declared", "type": "integer", "minimum": 1},
        "effective_start": {"x-origin": "declared", "type": "number",
          "minimum": 0, "maximum": 1}
      },
      "required": ["weeks","effective_start"], "additionalProperties": False}
  },
  "required": ["role","capacity_hours_per_week","ramp"],
  "additionalProperties": False
}

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/scenarios/v1/scenario.schema.json",
  "title": "Scenario File (scenarios/*.yaml) v1",
  "x-spec": "Sections 72.5, 72.6, 72.7, 52.6",
  "x-residual-rule": [
    "Section 72.5: output format is always the same three columns - current, projected, delta - with the assumptions listed and the weakest assumption flagged.",
    "Section 72.5: the standing one-click scenario set is auto-regenerated quarterly against the current baseline by the scenario job; the Founder owns the files.",
    "Section 72.6: the remove-one-person scenario is run automatically each quarter for every person.",
    "Section 72.7: a forecast never triggers an automatic action of any kind; it creates a decision prompt, and the decision is recorded.",
    "Section 72.5: no scenario claims precision beyond its inputs."
  ],
  "type": "object",
  "properties": {
    "scenario_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "scenario": {"x-origin": "declared", "type": "string", "minLength": 1},
    "baseline": {"x-origin": "declared", "$ref": C + "#/$defs/isoDate"},
    "changes": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"$ref": "#/$defs/changeEntry"}},
    "outputs_requested": {"x-origin": "declared", "type": "array", "minItems": 1,
      "items": {"type": "string", "minLength": 1}},
    "assumptions": {"x-origin": "declared", "type": "array",
      "items": {"type": "string", "minLength": 1}},
    "weakest_assumption": {"x-origin": "declared", "type": "string", "minLength": 1}
  },
  "required": ["scenario_version","scenario","baseline","changes","outputs_requested",
               "assumptions","weakest_assumption"],
  "additionalProperties": False,
  "$defs": {
    "changeEntry": {
      "type": "object",
      "minProperties": 1,
      "maxProperties": 1,
      "properties": change_entry_props,
      "additionalProperties": False,
      "$comment": "72.5: exactly one key from the twelve supported scenario primitives"
    }
  }
}

pathlib.Path("schemas/registry/scenarios/v1/scenario.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/scenarios/v1/fixtures")

# Section 72.5 2026-q3-add-qa block
valid = {
  "scenario_version": 1,
  "scenario": "2026-q3-add-qa",
  "baseline": "2026-07-01",
  "changes": [{
    "add_person": {
      "role": "qa",
      "capacity_hours_per_week": 40,
      "ramp": {"weeks": 8, "effective_start": 0.25}
    }
  }],
  "outputs_requested": [
    "capacity_utilisation_change",
    "verification_backlog_change",
    "plu_change_per_product"
  ],
  "assumptions": [
    "New hire starts 2026-08-01 as planned",
    "No change to product portfolio mix during the quarter",
    "Ramp curve is linear from effective_start to 1.0 at week count"
  ],
  "weakest_assumption": "Ramp curve is linear from effective_start to 1.0 at week count"
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: unknown primitive key
f1 = copy.deepcopy(valid)
f1["changes"][0] = {"hire_contractor": {"role": "contractor", "capacity_hours_per_week": 20}}
pathlib.Path(base / "invalid-unknown-primitive.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: add_person without ramp
f2 = copy.deepcopy(valid)
del f2["changes"][0]["add_person"]["ramp"]
pathlib.Path(base / "invalid-add-person-without-ramp.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote scenario.schema.json + 3 fixtures")
PY

S=schemas/registry/scenarios/v1/scenario.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/scenarios/v1/fixtures/valid.yaml
for f in schemas/registry/scenarios/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/scenarios
git commit -m "L1-02-17: scenarios/*.yaml v1 JSON Schema (Sections 72.5, 72.6, 72.7)"
git push -u origin lane/1/02-t17-scenario-schema
gh pr create --base integration --head lane/1/02-t17-scenario-schema \
  --title "L1-02-17 scenarios/*.yaml v1 schema" \
  --body "Phase 2 Lane 1. Twelve scenario primitives as closed changeEntry; add_person requires ramp (72.5 honesty rule); five residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/scenarios/v1/scenario.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/scenarios/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/scenarios/v1/scenario.schema.json')); print(len(s['\$defs']['changeEntry']['properties']))"
```

Correct output: `LINT-OK …`, `VALID`, then `12`.

**STOP rule** — the primitive count is not 12. The list is a transcription of the twelve behaviours in the 72.5 "Supported scenario primitives" bullet list (the "add or remove a person" bullet is two primitives; "change a product's criticality … or support model" is two). File a blocker if the count differs.

---

### L1-02-18 — `changes/*.yaml` change-manifest schema (v1) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

> **OUT-OF-SCOPE (FD-058):** Charter section 12, DECISION REQUIRED #3 explicitly states "L1 default pending answer. Do not create it."
> This task is not executed. The artifact [changes/*] is not authored by L1. See FD-058 for the decision record.

**Creates**
`schemas/registry/changes/v1/change-manifest.schema.json`
`schemas/registry/changes/v1/fixtures/valid.yaml`
`schemas/registry/changes/v1/fixtures/invalid-stage-not-in-ladder.yaml`
`schemas/registry/changes/v1/fixtures/invalid-status-not-in-enum.yaml`

**Size:** M **Depends on:** L1-02-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
**Spec source:** Section 25 (the YAML block, verbatim, and the pilot/rollout/fleet table), Section 24.1 (impact scope), Section 52.6 (`changes/*.yaml` row: "Authoritative state of cross-product and platform changes"), Section 61 (canary), invariant 72 (Section 101.10: "Portfolio-wide changes never roll out to the fleet without passing a canary first").

One file per change (PARTITION.md rule 3).

| Field | Type | Enumerated values | Origin |
|---|---|---|---|
| `manifest_version` | integer | `>= 1` | declared |
| `change_id` | string | `^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+$` | declared |
| `title` | string | minLength 1 | declared |
| `impact_scope` | string | `cross-product` \| `portfolio-wide` — Section 25 applies to these two | declared |
| `platform_change` | boolean | | declared |
| `affected.products[]` | array | productId | **derived** |
| `affected.repositories[]` | array | strings | **derived** |
| `affected.stacks[]` | array | strings | **derived** |
| `affected.lifecycle_states[]` | array | `active` \| `maintenance` \| `paused` \| `sunset` \| `archived` | **derived** |
| `author` | string | personId | declared |
| `reviewer` | string | personId | declared |
| `approver` | string | personId | declared |
| `verification.canary_set[]` | array | productId, minItems 1 | declared |
| `verification.canary_result` | string | `pending` \| `passed` \| `failed` | declared |
| `verification.fleet_verification` | string | `pending` \| `passed` \| `failed` | declared |
| `rollout.strategy` | string | `canary-then-fleet` | declared |
| `rollout.stage` | string | `pilot` \| `rollout` \| `fleet` | declared |
| `rollout.canary_start` | date \| null | | declared |
| `rollout.fleet_start` | date \| null | | declared |
| `rollback.method` | string | minLength 1 | declared |
| `rollback.tested` | boolean | | declared |
| `status` | string | `draft` \| `review` \| `canary` \| `rolling` \| `complete` \| `rolled-back` | declared |

**DERIVED fields**

| Field | Producing job | Citation |
|---|---|---|
| `affected` (whole block: `products`, `repositories`, `stacks`, `lifecycle_states`) | blast-radius script over the product registry | Section 25 — "The `affected:` block is generated by a script over the product registry, never assembled by hand — see the blast-radius analysis in Section 33" |

**Schema-encoded rules:** `rollout.stage` is exactly one of the three ladder stages of the Section 25 table; `status` is exactly one of the six values in the block's comment; `verification.canary_set` has at least one entry (invariant 72).

**`x-residual-rule`:**
* `"Section 25: the manifest is created before the change begins and closed when rollout completes or rolls back."`
* `"Section 25: a capability stuck between stages for more than a quarter is either finished or abandoned."`
* `"Section 25: pilot products are selected using capability and stack declarations so the pilot set covers the relevant technology diversity; classification.reliability_criticality steers selection."`
* `"Section 101.10 invariant 72: portfolio-wide changes never roll out to the fleet without passing a canary first - fleet_start requires canary_result passed."`
* `"Section 52.2 SIG-14: canary sets that failed or were abandoned without a closed manifest are an Amber signal."`

**Fixture:** `valid.yaml` is the Section 25 `2026-05-14-shared-ci-node22` block verbatim, plus `manifest_version: 1`, and with the `repositories` list completed (the spec block elides it with `...`) as `[org/product-1-api, org/product-3, org/product-7-api, org/product-12-mobile]`. Negatives: `rollout.stage: canary` (not a ladder stage — `canary` is a `status`, not a `stage`); `status: shipping`.

**Commands**

```bash
set -e
# --- preflight (Section 0.5) ---
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration
test -f schemas/registry/_common/v1/common.schema.json || { echo "STOP: L1-02-02 not merged"; exit 3; }
test -e schemas/registry/changes && { echo "STOP: schemas/registry/changes already exists"; exit 3; }

git checkout -b lane/1/02-t18-change-manifest-schema
mkdir -p schemas/registry/changes/v1/fixtures

python3 - <<'PY'
import pathlib, json, yaml, copy

C = "https://control-plane.internal/schemas/registry/_common/v1/common.schema.json"

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/changes/v1/change-manifest.schema.json",
  "title": "Change Manifest (changes/*.yaml) v1",
  "x-spec": "Sections 25, 24.1, 52.6, 61; invariant 72",
  "x-residual-rule": [
    "Section 25: the manifest is created before the change begins and closed when rollout completes or rolls back.",
    "Section 25: a capability stuck between stages for more than a quarter is either finished or abandoned.",
    "Section 25: pilot products are selected using capability and stack declarations so the pilot set covers the relevant technology diversity; classification.reliability_criticality steers selection.",
    "Section 101.10 invariant 72: portfolio-wide changes never roll out to the fleet without passing a canary first - fleet_start requires canary_result passed.",
    "Section 52.2 SIG-14: canary sets that failed or were abandoned without a closed manifest are an Amber signal."
  ],
  "type": "object",
  "properties": {
    "manifest_version": {"x-origin": "declared", "$ref": C + "#/$defs/registryVersion"},
    "change_id": {"x-origin": "declared", "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+$"},
    "title": {"x-origin": "declared", "type": "string", "minLength": 1},
    "impact_scope": {"x-origin": "declared", "type": "string",
      "enum": ["cross-product","portfolio-wide"]},
    "platform_change": {"x-origin": "declared", "type": "boolean"},
    "affected": {
      "x-origin": "derived", "readOnly": True,
      "x-derived-from": "Section 25: the affected block is generated by a script over the product registry (blast-radius analysis, Section 33); never assembled by hand.",
      "type": "object",
      "properties": {
        "products": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 25: as parent.",
          "type": "array", "items": {"$ref": C + "#/$defs/productId"}},
        "repositories": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 25: as parent.",
          "type": "array", "items": {"type": "string"}},
        "stacks": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 25: as parent.",
          "type": "array", "items": {"type": "string"}},
        "lifecycle_states": {"x-origin": "derived", "readOnly": True,
          "x-derived-from": "Section 25: as parent.",
          "type": "array", "items": {"type": "string",
            "enum": ["active","maintenance","paused","sunset","archived"]}}
      },
      "additionalProperties": False},
    "author": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
    "reviewer": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
    "approver": {"x-origin": "declared", "$ref": C + "#/$defs/personId"},
    "verification": {"x-origin": "declared", "type": "object",
      "properties": {
        "canary_set": {"x-origin": "declared", "type": "array", "minItems": 1,
          "items": {"$ref": C + "#/$defs/productId"}},
        "canary_result": {"x-origin": "declared", "type": "string",
          "enum": ["pending","passed","failed"]},
        "fleet_verification": {"x-origin": "declared", "type": "string",
          "enum": ["pending","passed","failed"]}
      },
      "required": ["canary_set","canary_result","fleet_verification"],
      "additionalProperties": False},
    "rollout": {"x-origin": "declared", "type": "object",
      "properties": {
        "strategy": {"x-origin": "declared", "type": "string",
          "const": "canary-then-fleet"},
        "stage": {"x-origin": "declared", "type": "string",
          "enum": ["pilot","rollout","fleet"]},
        "canary_start": {"x-origin": "declared",
          "$ref": C + "#/$defs/nullableIsoDate"},
        "fleet_start": {"x-origin": "declared",
          "$ref": C + "#/$defs/nullableIsoDate"}
      },
      "required": ["strategy","stage","canary_start","fleet_start"],
      "additionalProperties": False},
    "rollback": {"x-origin": "declared", "type": "object",
      "properties": {
        "method": {"x-origin": "declared", "type": "string", "minLength": 1},
        "tested": {"x-origin": "declared", "type": "boolean"}
      },
      "required": ["method","tested"], "additionalProperties": False},
    "status": {"x-origin": "declared", "type": "string",
      "enum": ["draft","review","canary","rolling","complete","rolled-back"]}
  },
  "required": ["manifest_version","change_id","title","impact_scope","platform_change",
               "affected","author","reviewer","approver","verification","rollout",
               "rollback","status"],
  "additionalProperties": False
}

pathlib.Path("schemas/registry/changes/v1/change-manifest.schema.json").write_text(
    json.dumps(schema, indent=2) + "\n", encoding="utf-8")

base = pathlib.Path("schemas/registry/changes/v1/fixtures")

# Section 25 2026-05-14-shared-ci-node22 block verbatim + manifest_version: 1
valid = {
  "manifest_version": 1,
  "change_id": "2026-05-14-shared-ci-node22",
  "title": "Upgrade shared CI to Node.js 22",
  "impact_scope": "portfolio-wide",
  "platform_change": True,
  "affected": {
    "products": ["product-1","product-3","product-7","product-12"],
    "repositories": ["org/product-1-api","org/product-3","org/product-7-api","org/product-12-mobile"],
    "stacks": ["nodejs"],
    "lifecycle_states": ["active","maintenance"]
  },
  "author": "dev-a",
  "reviewer": "dev-b",
  "approver": "dev-a",
  "verification": {
    "canary_set": ["product-1"],
    "canary_result": "passed",
    "fleet_verification": "passed"
  },
  "rollout": {
    "strategy": "canary-then-fleet",
    "stage": "fleet",
    "canary_start": "2026-05-15",
    "fleet_start": "2026-05-22"
  },
  "rollback": {
    "method": "Revert Node.js version pin in CI workflow and re-run affected product pipelines",
    "tested": True
  },
  "status": "complete"
}

pathlib.Path(base / "valid.yaml").write_text(
    yaml.safe_dump(valid, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: rollout.stage value that is a status token, not a stage token
f1 = copy.deepcopy(valid)
f1["rollout"]["stage"] = "canary"
pathlib.Path(base / "invalid-stage-not-in-ladder.yaml").write_text(
    yaml.safe_dump(f1, default_flow_style=False, sort_keys=False), encoding="utf-8")

# negative: status value not in the six-value enum
f2 = copy.deepcopy(valid)
f2["status"] = "shipping"
pathlib.Path(base / "invalid-status-not-in-enum.yaml").write_text(
    yaml.safe_dump(f2, default_flow_style=False, sort_keys=False), encoding="utf-8")

print("wrote change-manifest.schema.json + 3 fixtures")
PY

S=schemas/registry/changes/v1/change-manifest.schema.json
python3 validators/registry/schema-check/check.py --lint $S
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/changes/v1/fixtures/valid.yaml
for f in schemas/registry/changes/v1/fixtures/invalid-*.yaml; do
  python3 validators/registry/schema-check/check.py --schema $S --instance "$f" >/dev/null && { echo "NEGATIVE-FAIL $f"; exit 1; } || echo "NEGATIVE-OK $f"
done

git add schemas/registry/changes
git commit -m "L1-02-18: changes/*.yaml v1 JSON Schema (Section 25, invariant 72)"
git push -u origin lane/1/02-t18-change-manifest-schema
gh pr create --base integration --head lane/1/02-t18-change-manifest-schema \
  --title "L1-02-18 changes/*.yaml v1 schema" \
  --body "Phase 2 Lane 1. Section 25 block; affected block fully DERIVED; three-stage rollout ladder; six-value status enum; five residual rules."
```

**SELF-VERIFY**

```bash
set -euo pipefail
S=schemas/registry/changes/v1/change-manifest.schema.json
python3 validators/registry/schema-check/check.py --lint $S && \
python3 validators/registry/schema-check/check.py --schema $S --instance schemas/registry/changes/v1/fixtures/valid.yaml && \
python3 -c "import json; s=json.load(open('schemas/registry/changes/v1/change-manifest.schema.json')); print(s['properties']['affected']['x-origin'], ','.join(s['properties']['rollout']['properties']['stage']['enum']), len(s['properties']['status']['enum']))"
```

Correct output: `LINT-OK …`, `VALID`, then `derived pilot,rollout,fleet 6`.

**STOP rule** — as Section 0.6.

---

### L1-02-19 — Schema index and phase gate <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates**
`schemas/registry/index.json`

**Size:** S **Depends on:** L1-02-03 … L1-02-18 (all merged to `integration`) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

`index.json` is a **generated** manifest, written once here and regenerated by the command below whenever a schema is added. It is not a shared mutable list edited by multiple lanes — only L1 writes `schemas/**`.

**Commands**

```bash
set -e
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "FAIL: not a git repo"; exit 2; }
git remote -v | grep -q 'control-plane' || { echo "FAIL: not the control-plane repo"; exit 2; }
git fetch origin && git checkout integration && git pull --ff-only origin integration

# --- STOP check: all sixteen schemas must be present before the index is written ---
EXPECTED=16
FOUND=$(find schemas -name '*.schema.json' -not -path '*/_common/*' -not -path '*/common/*' | wc -l | tr -d ' ')
test "$FOUND" -eq "$EXPECTED" || { echo "STOP: expected $EXPECTED schemas, found $FOUND"; exit 3; }

git checkout -b lane/1/02-t19-schema-index

python3 - <<'PY'
import json, pathlib
out = []
for p in sorted(pathlib.Path("schemas").rglob("*.schema.json")):
    if "_common" in p.parts or "common" in p.parts:
        continue
    s = json.loads(p.read_text(encoding="utf-8"))
    out.append({
        "artifact": p.name.replace(".schema.json", ""),
        "version": p.parent.name,
        "schema": p.as_posix(),
        "title": s.get("title", ""),
        "id": s.get("$id", ""),
    })
pathlib.Path("schemas/registry/index.json").write_text(
    json.dumps({"index_version": 1, "generated_by": "L1-02-19", "schemas": out}, indent=2) + "\n",
    encoding="utf-8",
)
print(f"INDEXED {len(out)}")
PY

python3 validators/registry/schema-check/check.py --suite

git add schemas/registry/index.json
git commit -m "L1-02-19: schema index and Phase 2 suite gate"
git push -u origin lane/1/02-t19-schema-index
gh pr create --base integration --head lane/1/02-t19-schema-index \
  --title "L1-02-19 schema index + phase gate" --body "Phase 2 Lane 1 close-out. Sixteen schemas indexed; full suite green."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| 1 | Sixteen schemas indexed | `python3 -c "import json; s=json.load(open('schemas/registry/index.json')); print(len(s['schemas']))"` | `16` |
| 2 | Full suite green | `python3 validators/registry/schema-check/check.py --suite; echo "EXIT=$?"` | last two lines `SUITE-OK` then `EXIT=0` |
| 3 | Every schema lints | included in the suite run | every schema prints `LINT-OK …`, none prints `LINT-FAIL` |
| 4 | Every schema has both fixture polarities | included in the suite run | no `SUITE-FAIL … needs >=1 valid*.yaml and >=1 invalid-*.yaml` |
| 5 | No foreign path | `git diff --name-only integration...HEAD \| grep -cv '^schemas/registry/index.json$'` | `0` |
| 6 | Every `$id` follows the T02 convention | `python3 -c "import json; s=json.load(open('schemas/registry/index.json')); print(all(e['id']=='https://control-plane.internal/'+e['schema'] for e in s['schemas']))"` | `True` |

**SELF-VERIFY**

```bash
set -euo pipefail
python3 validators/registry/schema-check/check.py --suite; echo "EXIT=$?"
python3 -c "import json; i=json.load(open('schemas/registry/index.json')); print(len(i['schemas']), all(e['id']=='https://control-plane.internal/'+e['schema'] for e in i['schemas']))"
```

Correct output: the suite run ends `SUITE-OK` then `EXIT=0`; the second command prints `16 true`.

**STOP rule** — `FOUND` is not 16, or the suite reports any `SUITE-FAIL`. Do not write a partial index and do not delete a failing fixture to make the suite green. Identify the failing task by its `SUITE-FAIL` line, re-open that task's branch, and fix it there. If the failure is in a merged schema owned by this lane, open a new `lane/1/02-fix-<task>` branch rather than editing on the T19 branch.

---

## 3. DECISION REQUIRED — items handed to L0

These are the only points in Phase 2 where judgment is required. None is exercised by the executor. Each is filed as an issue against L0 before the phase closes; only **DECISION-L1-02-A** blocks anything (it blocks authoring a product v1 schema, which this phase does not attempt).

### DECISION-L1-02-A — Is a `product.yaml` **v1** schema required?

**Blocks:** authoring `schemas/product/product/v1/`. Does not block T05.
**Facts.** Section 60.1's `platform.yaml` block declares `supported_contract_versions.product: [1, 2]`. Section 15.1 exhibits only the v2 contract (`contract_version: 2`). No v1 product-contract shape appears anywhere in the specification. Section 60.2 requires the validator to support both versions where both are declared supported. PARTITION.md rule 2 forbids L1 from writing `contracts/**`, and this lane invents nothing.
**Options for L0.** (a) Author the fleet at v2 only; `platform.yaml` ships `supported_contract_versions.product: [2]`. (b) L0 supplies a frozen v1 shape under `contracts/**` and L1 transcribes it in a follow-up task.
**Impact if undecided.** The v2-only posture stands; `schemas/registry/index.json` lists v2 only; the `platform.yaml` fixture in T08 keeps the Section 60.1 literal `[1, 2]`, which will fail the cross-file residual check ("every version listed must have a schema directory on disk") once that validator exists.

### DECISION-L1-02-B — The canonical `event_type` identifier list

**Blocks:** populating `platform.yaml`'s `event_types` beyond the three fixture entries. Does not block T08's schema.
**Facts.** Section 60.2 places the event-type enum in `platform.yaml`, versioned by `platform_version`. Section 97.3 states the identifiers are "lower-case, underscore-separated, never renamed once shipped", that "control-plane CI rejects any event whose `event_type` is absent from it", and that "the enum ships populated in Phase 1 so no workflow ever writes an untyped event" — but supplies the taxonomy as roughly 110 prose phrases, not identifiers. Turning "plan approved (Gate 1) with `agent_authored` flag" into `plan_approved` is a naming act, and 97.3 warns exactly what happens when two authors do it independently.
**Cross-lane.** L4 owns `events/**` and writes the events; L2's workflows emit them. The identifier list must be one list, decided once.
**Option for L0.** Publish the identifier list as a frozen artifact under `contracts/**`; L1 transcribes it into the `platform.yaml` registry data in a later phase. L1 does not author it.

### DECISION-L1-02-C — Ratification of planner-fixed field names for the four prose-only registries

**Blocks:** nothing. Executable as written.
**Facts.** `patterns.yaml` (58.2), the automation-ledger and standing-entry blocks of `economics.yaml` (57.1, 57.2), the tolerance block of `os-health.yaml` (53.4) and the investment-gate block of `platform-roadmap.yaml` (59.2) are specified as prose tables and bullet lists, not as YAML. Their **semantics** are fully specified; their **field names** are not. This plan fixes the names literally in T09, T12, T13 and T14 so the executor never chooses.
**Ask of L0.** Ratify or replace the fixed names before any registry data is populated against them. A rename after population is a v2 schema under the Section 60.2 flow, not an in-place edit — which is exactly the cost this decision exists to pay once.

---

## 4. Blocker-issue template

Every STOP rule in this document resolves to filing this issue and halting. The executor does not proceed past a STOP.

```bash
set -euo pipefail
gh issue create --title "BLOCKER L1-02-<TASK-ID>: <one line>" --label blocker,lane-1,phase-2 --body "$(cat <<'BODY'
## Task
L1-02-T<NN> — <task title from Section 1 of C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L1-02-schemas.md>

## Branch
lane/1/02-<branch name>  (pushed: yes/no)

## What I was told to do
<quote the exact line from the task>

## The exact command that failed
```
<command, verbatim>
```

## The exact output
```
<stdout and stderr, verbatim, not summarised>
```

## Which STOP rule fired
<quote the STOP rule text from the task>

## Spec text I was transcribing
Section <N.N>, lines <A>-<B> of Research/MultiProduct_MasterSpec_v4.0.md:
```
<sed -n 'A,Bp' output, verbatim>
```

## What I did NOT do
- I did not edit any path outside this lane's ownership.
- I did not loosen a schema to make a fixture pass.
- I did not add, rename or remove a field the task table does not list.
- I did not force-push, and I did not delete any v<N>/ directory.

## What I need decided
<one sentence>
BODY
)"
```

---

## 5. Phase 2 exit criteria

Phase 2 is complete when, on `integration`:

| # | Criterion | Command | Expected |
|---|---|---|---|
| 1 | Sixteen schemas exist, each under `v<N>/` per the Section 0.1 convention | `find schemas -name '*.schema.json' -not -path '*/_common/*' -not -path '*/common/*' \| wc -l` | `16` |
| 2 | The versioning convention is written down and cites Section 60.2 | `test -f schemas/registry/README.schema-versioning.md && grep -c 'Section 60.2' schemas/registry/README.schema-versioning.md` | `>= 1` |
| 3 | Every schema lints, and every fixture pair behaves | `python3 validators/registry/schema-check/check.py --suite; echo "EXIT=$?"` | `SUITE-OK` then `EXIT=0` |
| 4 | Every property in every schema carries `x-origin` | implied by criterion 3 (the lint is part of `--suite`) | no `LINT-FAIL` lines |
| 5 | Every DERIVED field carries `readOnly` and a spec citation | implied by criterion 3 | no `LINT-FAIL` lines |
| 6 | Every schema records its residual rules | `python3 -c "import json, sys; idx=json.load(open('schemas/registry/index.json')); bad=[e['schema'] for e in idx['schemas'] if not isinstance(json.load(open(e['schema'])).get('x-residual-rule'),list)]; sys.exit(str(bad)) if bad else print('OK')"` | `OK` |
| 7 | No lane-guard violation across the phase | `git log --name-only --pretty=format: integration ^<phase-2 base> \| sort -u \| grep -cvE '^(schemas/(registry|product)/|validators/registry/schema-check/|$)'` | `0` |

Nothing in this phase writes registry **data**. Populating `people.yaml`, `roles.yaml`, `platform.yaml` and the rest is a later phase of this lane, and it validates against exactly these files.
