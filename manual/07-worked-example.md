# 07 — Worked Example: One Lane 1 Task, End to End

This file exists so you can **pattern-match instead of interpret**.

It is one real task — authoring the JSON Schema for the `people.yaml` registry —
executed from the moment the task is handed to you until the moment the PR is open
and ready for L0 to merge.
Nothing is elided. Every command is literal and copy-pasteable. Every file is shown
in full. Every output shown under a **CAPTURED** banner was produced by actually
running the command; nothing in those blocks is invented.

When you are given a Lane 1 schema task, **do what this file does, in this order.**
If your task differs from this one, the *shape* still holds: preflight, read, write,
self-verify, scope-check, commit, PR, report. Merging is L0's, never yours.

---

## 0. Provenance of the outputs in this file

| Banner | Meaning |
|---|---|
| **CAPTURED** | The command was executed and this is its verbatim output, including exit code. |
| **REMOTE** | The command touches GitHub. The command line is exact; the output block shows the shape `gh`/`git` returns. Your run will differ in SHAs, URLs and PR numbers. |

Toolchain the CAPTURED blocks were produced with — if your versions differ, say so in
your report rather than adapting silently:

```
node     v22.19.0
npm      10.9.3
git      2.49.0
ajv-cli  5.0.0   (ajv 8.20.0)
js-yaml  4.1.0
```

---

## 1. The task spec, exactly as it was issued

This is the whole prompt. It is reproduced verbatim so you can see what a
well-formed task looks like. **If a task you receive is missing any numbered
section below, stop and use the blocker template in
`manual/03-guardrails-and-stop-rules.md` §6 — do not fill the gap yourself.**

````text
TASK ID:      L1-F3-04
LANE:         L1 Registries & Contracts
REPO:         control-plane
BRANCH:       lane/1/f3-04-people-registry-schema   (branch from `integration`, never from `main`)
DEPENDS ON:   L1-F3-01 (lane bootstrap) — already merged to `integration`

1. GOAL
   Author the JSON Schema that structurally validates the control-plane people
   registry file `people.yaml`, described in MasterSpec v4.0 Section 7.

2. FILES YOU CREATE (exactly these 12; create no others, edit no others)
   schemas/registry/people.schema.json
   validators/registry/verify-people.sh
   validators/registry/fixtures/people/valid/001-spec-section-7-example.yaml
   validators/registry/fixtures/people/invalid/001-contractor-with-null-end-date.yaml
   validators/registry/fixtures/people/invalid/002-departed-but-not-revoked.yaml
   validators/registry/fixtures/people/invalid/003-revoked-employee-still-active.yaml
   validators/registry/fixtures/people/invalid/004-suspended-while-departing.yaml
   validators/registry/fixtures/people/invalid/005-timezone-is-utc-offset.yaml
   validators/registry/fixtures/people/invalid/006-fte-above-one.yaml
   validators/registry/fixtures/people/invalid/007-unknown-top-level-property.yaml
   validators/registry/fixtures/people/invalid/008-empty-people-list.yaml
   validators/registry/fixtures/people/invalid/009-wrong-registry-version.yaml

3. FILES THAT ALREADY EXIST — READ THEM, DO NOT EDIT THEM
   validators/registry/run-suite.sh    the lane suite; it auto-discovers verify-*.sh
   validators/registry/yaml2json.js    the mandated YAML loader (see §6 below)
   package.json                        already declares ajv-cli and js-yaml

4. PRE-DECIDED BY L0 — COPY THESE LITERALLY, DO NOT CHOOSE
   4.1  Dialect:  "$schema": "http://json-schema.org/draft-07/schema#"
        Draft-07 is ajv-cli's default, so no --spec flag can be forgotten.
   4.2  Identifier: "$id": "urn:multiproduct:schema:registry:people:1"
        A urn, not an https URL, so no validator ever attempts a network fetch.
   4.3  Dates are validated by regex pattern, NOT by "format": "date".
        Rationale: "format" requires the ajv-formats plugin and a -c flag that
        is easy to omit; an omitted -c makes format checks silently no-op.
   4.4  additionalProperties: false at EVERY object level.
   4.5  `availability` and `access_status` ARE closed enums.
        `role` and `employment_type` are NOT enums. Section 7.1 states employment
        types are open-ended; Section 8 states roles are configuration. Constrain
        them to a slug pattern only.
   4.6  `accepted_coverage_window` has the shape {days, start, end, timezone},
        matching operations.coverage_window in Section 15.1, because Section 47.9
        compares the two windows against each other.

5. CROSS-FIELD RULES TO ENCODE (Section 7.1). Encode exactly these four.
   R1  end_date is mandatory (non-null) for every person whose employment_type
       is not the literal string "employee".
   R2  availability: departed  =>  access_status: revoked
   R3  access_status: revoked  =>  availability: departed OR employment_type
       is not "employee".
   R4  access_status: suspended  =>  availability is active or on_leave.

6. EXPLICITLY OUT OF SCOPE — DO NOT IMPLEMENT, DO NOT "FIX"
   These are real requirements that JSON Schema cannot express. They belong to
   task L1-P2-T007 (the registry validator). If you notice them, that is expected;
   noticing them is not permission to build them.
   - uniqueness of `id` across the people array
   - `role` must exist in roles.yaml; `ai_runtime` must be on the Section 35 list
   - the "past end_date" half of R3, which needs today's date
   - schedule start < end
   - anything under schemas/product/, registries/, or any path outside
     schemas/registry/ and validators/registry/

7. KNOWN TRAP — HANDLE IT THE MANDATED WAY
   YAML's default type resolution turns an unquoted 2025-03-01 into a timestamp,
   not a string, so every "type": "string" date check fails against a file that
   is actually correct. Do NOT loosen the schema to accept objects. Convert YAML
   with the committed loader, which uses js-yaml's JSON_SCHEMA:
       node validators/registry/yaml2json.js <file.yaml>
   verify-people.sh must call it. It is already written; just use it.

8. ACCEPTANCE CRITERIA (all four, or the task is not done)
   A. npx ajv compile -s schemas/registry/people.schema.json
      prints "is valid" and exits 0.
   B. bash validators/registry/verify-people.sh
      prints "RESULT: PASS" and exits 0.
   C. bash validators/registry/run-suite.sh
      prints "LANE 1 SUITE: PASS" and exits 0.
   D. Every one of the 12 files in §2 exists and is staged; nothing else is.

9. SELF-VERIFY COMMAND (run it; paste its real output into your report)
   bash validators/registry/verify-people.sh; echo "EXIT=$?"
   Unambiguous success is the literal line "RESULT: PASS" together with EXIT=0.
   Any other output, including a pass count of 0, is failure.

10. STOP RULES — if any of these is true, do NOT proceed. Open a blocker issue
    using the template in manual/03-guardrails-and-stop-rules.md §6 and stop.
    S1  Any file in §3 is missing from the repo.
    S2  Section 7 of the spec disagrees with §4 or §5 of this task.
    S3  A rule in §5 cannot be expressed without inventing a field name that is
        not in Section 7.
    S4  Making a fixture pass would require changing a file in §3.
    S5  Your self-verify passes only because a fixture directory is empty.
    S6  You believe a §6 item must be implemented for the task to be correct.
````

---

## 2. Step 0 — Preflight: prove the repo is what the task says it is

Run this **before writing anything**. Its whole purpose is to defeat the failure
mode of inventing a plausible path.

```bash
set -euo pipefail
cd /path/to/control-plane

# 1. Where am I, and is the tree clean?
git rev-parse --show-toplevel
git status --short
git rev-parse --abbrev-ref HEAD

# 2. Do the files the task promised actually exist? (STOP RULE S1)
ls -l validators/registry/run-suite.sh
ls -l validators/registry/yaml2json.js
ls -l package.json

# 3. Are the tools installed?
node --version
npx --no-install ajv compile -s /dev/null 2>&1 | head -1   # expect an error, not "not found"

# 4. Create the branch from integration — never from main
git fetch origin
git checkout -B lane/1/f3-04-people-registry-schema origin/integration
```

If step 2 errors with `No such file or directory`, **stop.** That is S1. Do not
create the missing file yourself; it belongs to a different task and another agent
may already own it.

---

## 3. Step 1 — Read the two inputs, in this order

```bash
# The frozen partition — tells you which paths you may touch.
sed -n '12,30p' implementation/PARTITION.md

# The specification section this schema transcribes.
sed -n '543,640p' Research/MultiProduct_MasterSpec_v4.0.md
```

Lane 1 owns exactly these four path globs. Memorise them; every later step checks
against them:

```
schemas/registry/**
schemas/product/**
registries/**
validators/registry/**
```

---

## 4. Step 2 — Write the schema

Create `schemas/registry/people.schema.json` with **exactly** this content. This is
the file as committed — 242 lines.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "urn:multiproduct:schema:registry:people:1",
  "title": "People Registry",
  "description": "Structural contract for control-plane people.yaml. MasterSpec v4.0 Section 7. Structure and single-record cross-field rules only; cross-file, cross-record and date-relative rules are enforced by validators/registry/, not here.",
  "type": "object",
  "additionalProperties": false,
  "required": ["registry_version", "people"],
  "properties": {
    "registry_version": {
      "description": "Schema generation of this registry file. Bumped only by L0.",
      "type": "integer",
      "const": 1
    },
    "people": {
      "description": "Every person the operating system knows about, including departed ones (Section 7.1: departure is a state, not a deletion).",
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/person" }
    }
  },
  "definitions": {
    "slug": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64,
      "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"
    },
    "iso_date": {
      "type": "string",
      "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    },
    "clock_time": {
      "type": "string",
      "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
    },
    "day_window": {
      "type": "object",
      "additionalProperties": false,
      "required": ["start", "end"],
      "properties": {
        "start": { "$ref": "#/definitions/clock_time" },
        "end": { "$ref": "#/definitions/clock_time" }
      }
    },
    "weekday_schedule": {
      "description": "Section 7.3: per weekday; omit a day to declare it non-working.",
      "type": "object",
      "additionalProperties": false,
      "minProperties": 1,
      "properties": {
        "mon": { "$ref": "#/definitions/day_window" },
        "tue": { "$ref": "#/definitions/day_window" },
        "wed": { "$ref": "#/definitions/day_window" },
        "thu": { "$ref": "#/definitions/day_window" },
        "fri": { "$ref": "#/definitions/day_window" },
        "sat": { "$ref": "#/definitions/day_window" },
        "sun": { "$ref": "#/definitions/day_window" }
      }
    },
    "iana_timezone": {
      "description": "Section 7.3: an IANA identifier, never a UTC offset. The mandatory Area/Location slash is what rejects '+05:30' and 'UTC+5'.",
      "type": "string",
      "pattern": "^[A-Za-z][A-Za-z0-9_+-]*/[A-Za-z0-9_+-]+(/[A-Za-z0-9_+-]+)?$"
    },
    "coverage_window": {
      "description": "Days, hours and timezone - the Section 15.1 operations.coverage_window shape, matched windows-against-windows per Section 47.9.",
      "type": "object",
      "additionalProperties": false,
      "required": ["days", "start", "end", "timezone"],
      "properties": {
        "days": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": { "enum": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] }
        },
        "start": { "$ref": "#/definitions/clock_time" },
        "end": { "$ref": "#/definitions/clock_time" },
        "timezone": { "$ref": "#/definitions/iana_timezone" }
      }
    },
    "work_arrangement": {
      "description": "Section 7.3, the declared working calendar. Absent for a person with no declared calendar; the Section 15.6 rota validator fails closed on that absence rather than this schema doing so.",
      "type": "object",
      "additionalProperties": false,
      "required": ["timezone", "arrangement", "schedule", "fte", "public_holiday_set", "accepted_coverage_window"],
      "properties": {
        "timezone": { "$ref": "#/definitions/iana_timezone" },
        "arrangement": { "enum": ["onsite", "hybrid", "remote"] },
        "schedule": { "$ref": "#/definitions/weekday_schedule" },
        "fte": {
          "description": "Section 7.3: a capacity multiplier, not a status. 0 < fte <= 1.",
          "type": "number",
          "exclusiveMinimum": 0,
          "maximum": 1
        },
        "public_holiday_set": {
          "type": "string",
          "pattern": "^[A-Z]{2}(-[A-Z0-9]{1,3})?$"
        },
        "accepted_coverage_window": {
          "oneOf": [
            { "$ref": "#/definitions/coverage_window" },
            { "type": "null" }
          ]
        }
      }
    },
    "scope": {
      "description": "Section 7: present only for a person limited to named products.",
      "type": "object",
      "additionalProperties": false,
      "required": ["products"],
      "properties": {
        "products": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": { "$ref": "#/definitions/slug" }
        },
        "repositories_only": { "type": "boolean" }
      }
    },
    "person": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "display_name",
        "github_login",
        "role",
        "employment_type",
        "capabilities",
        "ai_runtime",
        "availability",
        "access_status",
        "start_date",
        "end_date"
      ],
      "properties": {
        "id": {
          "description": "Stable identifier, never reused (Section 7.1). Uniqueness across the array is checked by validators/registry/, not here.",
          "$ref": "#/definitions/slug"
        },
        "display_name": { "type": "string", "minLength": 1, "maxLength": 128 },
        "github_login": {
          "description": "GitHub login rules: alphanumeric plus single internal hyphens, 1-39 characters.",
          "type": "string",
          "pattern": "^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$"
        },
        "role": {
          "description": "Section 8: roles are configuration. Deliberately not an enum. Existence in roles.yaml is checked by validators/registry/, not here.",
          "$ref": "#/definitions/slug"
        },
        "employment_type": {
          "description": "Section 7.1: employment types are open-ended. Deliberately not an enum. Only the literal value 'employee' carries a rule, and that rule is the end_date exemption in R1.",
          "type": "string",
          "minLength": 1,
          "maxLength": 64,
          "pattern": "^[a-z0-9]+(_[a-z0-9]+)*$"
        },
        "capabilities": {
          "description": "Section 7.1: granted individually and explicitly, never inherited from a role default. An empty list is legal and means minimum authority.",
          "type": "array",
          "uniqueItems": true,
          "items": { "$ref": "#/definitions/slug" }
        },
        "ai_runtime": {
          "description": "Section 7.1: a declaration, not a coupling. null means none declared. Membership of the approved runtime list (Section 35) is checked by validators/registry/, not here.",
          "type": ["string", "null"],
          "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"
        },
        "availability": { "enum": ["active", "on_leave", "departing", "departed"] },
        "access_status": { "enum": ["pending", "provisioned", "suspended", "revoked"] },
        "work_arrangement": { "$ref": "#/definitions/work_arrangement" },
        "start_date": { "$ref": "#/definitions/iso_date" },
        "end_date": {
          "oneOf": [
            { "$ref": "#/definitions/iso_date" },
            { "type": "null" }
          ]
        },
        "scope": { "$ref": "#/definitions/scope" }
      },
      "allOf": [
        {
          "title": "R1: end_date is mandatory for every non-employee (Section 7.1).",
          "if": {
            "required": ["employment_type"],
            "properties": { "employment_type": { "not": { "const": "employee" } } }
          },
          "then": {
            "required": ["end_date"],
            "properties": { "end_date": { "$ref": "#/definitions/iso_date" } }
          }
        },
        {
          "title": "R2: departed implies revoked (Section 7.1).",
          "if": {
            "required": ["availability"],
            "properties": { "availability": { "const": "departed" } }
          },
          "then": {
            "required": ["access_status"],
            "properties": { "access_status": { "const": "revoked" } }
          }
        },
        {
          "title": "R3: revoked implies departed, or a non-employee (Section 7.1). The spec's full rule is 'departed or a non-employee past end_date'; the date half needs today's date and is enforced in validators/registry/, not here.",
          "if": {
            "required": ["access_status"],
            "properties": { "access_status": { "const": "revoked" } }
          },
          "then": {
            "anyOf": [
              {
                "required": ["availability"],
                "properties": { "availability": { "const": "departed" } }
              },
              {
                "required": ["employment_type"],
                "properties": { "employment_type": { "not": { "const": "employee" } } }
              }
            ]
          }
        },
        {
          "title": "R4: suspended is valid only with active or on_leave (Section 7.1).",
          "if": {
            "required": ["access_status"],
            "properties": { "access_status": { "const": "suspended" } }
          },
          "then": {
            "required": ["availability"],
            "properties": { "availability": { "enum": ["active", "on_leave"] } }
          }
        }
      ]
    }
  }
}
```

### Two things in that file you must not "clean up"

1. **`role` and `employment_type` are not enums.** They look like they should be —
   Section 7's example block lists four employment types in a comment. That comment
   is illustrative. Section 7.1 says in prose that the list is open-ended. Turning
   the comment into an enum would be exactly the guess this manual exists to prevent.
2. **R3 is weaker than the spec sentence.** The spec says *revoked implies departed
   or a non-employee **past end_date***. JSON Schema has no concept of today.
   The `title` field on R3 records that the missing half is deliberate and where it
   went. Do not delete that note, and do not try to fake the date check.

---

## 5. Step 3 — Write the fixtures

One valid fixture, nine invalid ones, each isolating exactly one violation.

**Why nine invalid fixtures and only one valid one:** a schema that accepts
everything passes a valid-only suite perfectly. The invalid set is the only thing
that proves the schema constrains anything at all.

### `validators/registry/fixtures/people/valid/001-spec-section-7-example.yaml`

```yaml
# VALID. Transcribed from MasterSpec v4.0 Section 7, the people.yaml example block.
# If this fixture ever fails, the schema has diverged from the specification.
registry_version: 1

people:
  - id: dev-a
    display_name: "Example Developer A"
    github_login: exampledev-a
    role: developer
    employment_type: employee
    capabilities:
      - backend
      - frontend
      - code-review
      - production-approval
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
    capabilities:
      - security-review
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2026-04-01
    end_date: 2026-06-30
    scope:
      products: [product-4, product-9]
      repositories_only: true
```

### `validators/registry/fixtures/people/invalid/001-contractor-with-null-end-date.yaml`

```yaml
# INVALID - R1. Section 7.1: end_date is mandatory for every non-employee.
# Expected error: instancePath /people/0/end_date
registry_version: 1
people:
  - id: con-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: contractor
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/002-departed-but-not-revoked.yaml`

```yaml
# INVALID - R2. Section 7.1: departed implies revoked.
# Expected error: instancePath /people/0/access_status
registry_version: 1
people:
  - id: dep-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: departed
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/003-revoked-employee-still-active.yaml`

```yaml
# INVALID - R3. Section 7.1: revoked implies departed, or a non-employee.
# An employee who is availability: active cannot be access_status: revoked.
# Expected error: instancePath /people/0
registry_version: 1
people:
  - id: rev-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: revoked
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/004-suspended-while-departing.yaml`

```yaml
# INVALID - R4. Section 7.1: suspended is valid only with active or on_leave.
# Expected error: instancePath /people/0/availability
registry_version: 1
people:
  - id: sus-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: departing
    access_status: suspended
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/005-timezone-is-utc-offset.yaml`

```yaml
# INVALID - Section 7.3: timezone is an IANA identifier, never a UTC offset.
# Expected error: instancePath /people/0/work_arrangement/timezone
registry_version: 1
people:
  - id: tz-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: "+05:30"
      arrangement: hybrid
      schedule:
        mon: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/006-fte-above-one.yaml`

```yaml
# INVALID - Section 7.3: 0 < fte <= 1.
# Expected error: instancePath /people/0/work_arrangement/fte
registry_version: 1
people:
  - id: fte-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: remote
      schedule:
        mon: { start: "09:30", end: "18:30" }
      fte: 1.5
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/007-unknown-top-level-property.yaml`

```yaml
# INVALID - additionalProperties: false at the root.
# An invented or misspelled key must be rejected, never silently ignored.
# Expected error: instancePath (root), keyword additionalProperties
registry_version: 1
notes: "this key is not in the schema"
people:
  - id: extra-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
```

### `validators/registry/fixtures/people/invalid/008-empty-people-list.yaml`

```yaml
# INVALID - minItems: 1. An empty registry is a mistake, not a valid state.
# Expected error: instancePath /people, keyword minItems
registry_version: 1
people: []
```

### `validators/registry/fixtures/people/invalid/009-wrong-registry-version.yaml`

```yaml
# INVALID - registry_version is const 1. Only L0 bumps it.
# Expected error: instancePath /registry_version, keyword const
registry_version: 2
people:
  - id: ver-1
    display_name: "Fixture Person"
    github_login: fixture-person
    role: developer
    employment_type: employee
    capabilities: [backend]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
```

---

## 6. Step 4 — Write the self-verify script

Create `validators/registry/verify-people.sh` with exactly this content — 75 lines.

```bash
#!/usr/bin/env bash
# Self-verify for schemas/registry/people.schema.json.
#
# Asserts BOTH directions:
#   every fixture under fixtures/people/valid/   MUST validate
#   every fixture under fixtures/people/invalid/ MUST be rejected
#
# A schema that accepts everything passes a valid-only suite. That is the
# failure this script exists to catch, which is why the invalid set is
# asserted with the same weight as the valid set.
#
# Exit 0 = all assertions held. Any other exit = do not commit.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/../.." && pwd)"
SCHEMA="${ROOT}/schemas/registry/people.schema.json"
FIXTURES="${HERE}/fixtures/people"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

if [ ! -f "${SCHEMA}" ]; then
  echo "FATAL: schema not found at ${SCHEMA}" >&2
  exit 2
fi

pass=0
fail=0

check() {
  # $1 = fixture path, $2 = --valid | --invalid
  local src="$1" mode="$2" name json
  name="$(basename "${src}")"
  json="${WORK}/${name%.yaml}.json"

  if ! node "${HERE}/yaml2json.js" "${src}" > "${json}"; then
    echo "FAIL  ${mode#--}  ${name}  (YAML did not parse)"
    fail=$((fail + 1))
    return
  fi

  if npx --no-install ajv test -s "${SCHEMA}" -d "${json}" "${mode}" > "${WORK}/out.txt" 2>&1; then
    echo "ok    ${mode#--}  ${name}"
    pass=$((pass + 1))
  else
    echo "FAIL  ${mode#--}  ${name}"
    sed 's/^/        /' "${WORK}/out.txt"
    fail=$((fail + 1))
  fi
}

echo "== people.schema.json =="

for f in "${FIXTURES}"/valid/*.yaml; do
  check "${f}" --valid
done

for f in "${FIXTURES}"/invalid/*.yaml; do
  check "${f}" --invalid
done

echo "-- ${pass} passed, ${fail} failed --"

if [ "${fail}" -ne 0 ]; then
  echo "RESULT: FAIL"
  exit 1
fi

if [ "${pass}" -lt 2 ]; then
  echo "RESULT: FAIL (fixture directories are empty or unreadable; a suite that"
  echo "        asserts nothing must never report success)"
  exit 1
fi

echo "SELF-VERIFY PASS: L1-F3-04"
```

Three details that are load-bearing, not style:

- **`ajv test ... --valid` / `--invalid`** asserts the *expected* result. Plain
  `ajv validate` only tells you whether a file passed; `test` fails the run when a
  file that should have been rejected was accepted. That is the direction that
  catches an over-permissive schema.
- **The `pass -lt 2` guard.** Without it, a mistyped fixture path makes both `for`
  loops iterate zero times and the script prints `SELF-VERIFY PASS: L1-F3-04`
  having asserted nothing. This is stop rule S5 turned into code.
- **`npx --no-install`** fails loudly if `ajv-cli` is absent instead of silently
  downloading a different version mid-run.

### The files you did *not* write

`validators/registry/yaml2json.js` already exists. It is reproduced here so you can
confirm the copy in the repo matches — **if it differs, stop (S1)**, do not edit it.

```javascript
#!/usr/bin/env node
// Convert one YAML file to JSON on stdout.
//
// Uses js-yaml's JSON_SCHEMA, NOT the default schema. This is load-bearing:
// the default YAML schema resolves an unquoted 2025-03-01 into a JavaScript
// Date object, which then fails every "type": "string" check in the registry
// schemas. JSON_SCHEMA resolves only the types JSON has, so 2025-03-01 stays
// the string "2025-03-01" and the schema validates what the file actually says.
//
// Usage: node validators/registry/yaml2json.js <file.yaml>
'use strict';

const fs = require('fs');
const yaml = require('js-yaml');

const file = process.argv[2];
if (!file) {
  process.stderr.write('usage: node yaml2json.js <file.yaml>\n');
  process.exit(2);
}

let doc;
try {
  doc = yaml.load(fs.readFileSync(file, 'utf8'), { schema: yaml.JSON_SCHEMA });
} catch (err) {
  process.stderr.write('YAML parse error in ' + file + ': ' + err.message + '\n');
  process.exit(2);
}

process.stdout.write(JSON.stringify(doc, null, 2) + '\n');
```

`validators/registry/run-suite.sh` also already exists. Note carefully that it
**discovers** verifiers rather than listing them — which is why adding your
`verify-people.sh` requires editing no shared file at all. That is PARTITION rule 3
("no shared mutable file, ever") in practice.

```bash
#!/usr/bin/env bash
# Lane 1 suite. Created once in L1-F3-01; DO NOT EDIT IT to add a check.
#
# It discovers every validators/registry/verify-*.sh and runs it. A new
# schema task adds its own verify-<name>.sh and is picked up with no edit to
# any shared file -- PARTITION rule 3, no shared mutable file, ever.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

total=0
failed=0
failed_names=""

for script in "${HERE}"/verify-*.sh; do
  [ -e "${script}" ] || continue
  total=$((total + 1))
  name="$(basename "${script}")"
  if bash "${script}"; then
    :
  else
    failed=$((failed + 1))
    failed_names="${failed_names} ${name}"
  fi
  echo
done

echo "===================================="
echo "LANE 1 SUITE: ${total} verifier(s), ${failed} failed"

if [ "${total}" -eq 0 ]; then
  echo "LANE 1 SUITE: FAIL (no verifiers discovered -- an empty suite is not a pass)"
  exit 1
fi

if [ "${failed}" -ne 0 ]; then
  echo "LANE 1 SUITE: FAIL${failed_names}"
  exit 1
fi

echo "LANE-VERIFY PASS: lane 1"
```

---

## 7. Step 5 — Acceptance criterion A: does the schema compile?

```bash
npx --no-install ajv compile -s schemas/registry/people.schema.json; echo "EXIT=$?"
```

**CAPTURED**

```
schema schemas/registry/people.schema.json is valid
EXIT=0
```

This checks the schema is a *well-formed* schema. It says nothing about whether it
validates the right things. That is the next step, and you may not skip it.

---

## 8. Step 6 — Acceptance criterion B: the self-verify run

```bash
bash validators/registry/verify-people.sh; echo "EXIT=$?"
```

**CAPTURED**

```
== people.schema.json ==
ok    valid  001-spec-section-7-example.yaml
ok    invalid  001-contractor-with-null-end-date.yaml
ok    invalid  002-departed-but-not-revoked.yaml
ok    invalid  003-revoked-employee-still-active.yaml
ok    invalid  004-suspended-while-departing.yaml
ok    invalid  005-timezone-is-utc-offset.yaml
ok    invalid  006-fte-above-one.yaml
ok    invalid  007-unknown-top-level-property.yaml
ok    invalid  008-empty-people-list.yaml
ok    invalid  009-wrong-registry-version.yaml
-- 10 passed, 0 failed --
SELF-VERIFY PASS: L1-F3-04
EXIT=0
```

Read that output the way the task spec told you to: the literal string
`SELF-VERIFY PASS: L1-F3-04`, `0 failed`, a pass count of `10` (not `0`), and
`EXIT=0`. **All four, or it did not pass.**

---

## 9. What a real failure looks like, and what you do about it

This is not hypothetical. The block below was produced by deleting rule R4 from the
schema and re-running the identical command — the exact mistake of writing the
schema but forgetting one of the four cross-field rules.

**CAPTURED**

```
== people.schema.json ==
ok    valid  001-spec-section-7-example.yaml
ok    invalid  001-contractor-with-null-end-date.yaml
ok    invalid  002-departed-but-not-revoked.yaml
ok    invalid  003-revoked-employee-still-active.yaml
FAIL  invalid  004-suspended-while-departing.yaml
        C:/Users/.../tmp.eIfg1mDlGw/004-suspended-while-departing.json failed test
ok    invalid  005-timezone-is-utc-offset.yaml
ok    invalid  006-fte-above-one.yaml
ok    invalid  007-unknown-top-level-property.yaml
ok    invalid  008-empty-people-list.yaml
ok    invalid  009-wrong-registry-version.yaml
-- 9 passed, 1 failed --
RESULT: FAIL
EXIT=1
```

(The temp path varies per run; that is expected.)

`FAIL invalid 004` means: *a file that should have been rejected was accepted.*
The fixture is right and the schema is too permissive. The fix is to add the missing
rule to the schema — **never** to delete or weaken the fixture.

To see the underlying error for any one fixture, convert and validate it directly:

```bash
set -euo pipefail
node validators/registry/yaml2json.js \
  validators/registry/fixtures/people/invalid/002-departed-but-not-revoked.yaml > /tmp/f.json
npx ajv validate -s schemas/registry/people.schema.json -d /tmp/f.json
```

**CAPTURED**

```
/tmp/f.json invalid
[
  {
    instancePath: '/people/0/access_status',
    schemaPath: '#/allOf/1/then/properties/access_status/const',
    keyword: 'const',
    params: { allowedValue: 'revoked' },
    message: 'must be equal to constant'
  }
]
```

`schemaPath` tells you which rule fired: `#/allOf/1` is R2, the second entry in the
`allOf` array. Use it to navigate the schema instead of guessing.

### The one decision rule for any failure

| What failed | What it means | What you do |
|---|---|---|
| `FAIL valid <f>` | A legitimate file is being rejected | The schema is too strict. Loosen the schema. |
| `FAIL invalid <f>` | An illegitimate file is being accepted | The schema is too permissive. Add the rule. |
| `(YAML did not parse)` | The fixture is malformed YAML | Fix the fixture's syntax. |
| `FATAL: schema not found` | Wrong working directory | `cd` to the repo root and rerun. |
| `pass count is 0` | Your fixture paths are wrong | Fix paths. Never report this as a pass. |
| Fixing it needs a file from task §3 | Out of your scope | **STOP — S4.** Open a blocker. |

---

## 10. Step 7 — Acceptance criterion C: the lane suite

```bash
bash validators/registry/run-suite.sh; echo "EXIT=$?"
```

**CAPTURED**

```
== people.schema.json ==
ok    valid  001-spec-section-7-example.yaml
ok    invalid  001-contractor-with-null-end-date.yaml
ok    invalid  002-departed-but-not-revoked.yaml
ok    invalid  003-revoked-employee-still-active.yaml
ok    invalid  004-suspended-while-departing.yaml
ok    invalid  005-timezone-is-utc-offset.yaml
ok    invalid  006-fte-above-one.yaml
ok    invalid  007-unknown-top-level-property.yaml
ok    invalid  008-empty-people-list.yaml
ok    invalid  009-wrong-registry-version.yaml
-- 10 passed, 0 failed --

====================================
LANE 1 SUITE: 1 verifier(s), 0 failed
LANE-VERIFY PASS: lane 1
EXIT=0
```

You must run the **whole lane suite**, not just your own verifier. Your schema can
pass in isolation and still break a sibling verifier that shares the loader.

---

## 11. Step 8 — Acceptance criterion D: stage, then prove scope

```bash
git status --short
```

**CAPTURED**

```
?? schemas/
?? validators/registry/fixtures/
?? validators/registry/verify-people.sh
```

Stage exactly the twelve files from the task's §2 — never `git add -A`, which would
sweep in editor droppings, temp files and anything an adjacent problem tempted you
to touch:

```bash
set -euo pipefail
git add \
  schemas/registry/people.schema.json \
  validators/registry/verify-people.sh \
  validators/registry/fixtures

git status --short
```

**CAPTURED**

```
A  schemas/registry/people.schema.json
A  validators/registry/fixtures/people/invalid/001-contractor-with-null-end-date.yaml
A  validators/registry/fixtures/people/invalid/002-departed-but-not-revoked.yaml
A  validators/registry/fixtures/people/invalid/003-revoked-employee-still-active.yaml
A  validators/registry/fixtures/people/invalid/004-suspended-while-departing.yaml
A  validators/registry/fixtures/people/invalid/005-timezone-is-utc-offset.yaml
A  validators/registry/fixtures/people/invalid/006-fte-above-one.yaml
A  validators/registry/fixtures/people/invalid/007-unknown-top-level-property.yaml
A  validators/registry/fixtures/people/invalid/008-empty-people-list.yaml
A  validators/registry/fixtures/people/invalid/009-wrong-registry-version.yaml
A  validators/registry/fixtures/people/valid/001-spec-section-7-example.yaml
A  validators/registry/verify-people.sh
```

Count them: twelve `A` lines, no `M` lines, no untracked leftovers. Now run the
**lane-guard self-check** — the same rule CI enforces, run locally so you find out
before the PR does:

```bash
set -euo pipefail
git diff --cached --name-only \
  | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "SCOPE VIOLATION -- do not commit" \
  || echo "SCOPE OK: every staged path is owned by Lane 1"
```

**CAPTURED**

```
SCOPE OK: every staged path is owned by Lane 1
```

If this prints any path followed by `SCOPE VIOLATION`, unstage that path
(`git restore --staged <path>`) and stop. A lane PR touching a foreign path fails
the lane-guard check with no exceptions (PARTITION rule 1).

---

## 12. Step 9 — Commit

The commit message is not decoration. It is the only place the *deliberate
omissions* are recorded, and the reviewer reads it before the diff.

```bash
set -euo pipefail
git commit -F - <<'MSGEOF'
schema(schemas-registry): add people registry schema v1

Adds schemas/registry/people.schema.json, the structural contract for the
control-plane people registry (MasterSpec v4.0 Section 7), plus its fixture
set and self-verify script. Also passes the full lane suite
(validators/registry/run-suite.sh).

Enforced here:
  - required fields, additionalProperties: false at every level
  - availability and access_status as closed enums
  - role and employment_type deliberately NOT enums (Sections 7.1, 8:
    roles are configuration, employment types are open-ended)
  - R1 end_date mandatory for every non-employee
  - R2 departed implies revoked
  - R3 revoked implies departed or non-employee
  - R4 suspended only with active or on_leave
  - timezone must be an IANA Area/Location identifier, never a UTC offset

Deferred to validators/registry/ (cannot be expressed in JSON Schema):
  - uniqueness of person id across the array
  - role exists in roles.yaml; ai_runtime is on the approved list
  - the "past end_date" half of R3, which needs today's date
  - schedule start < end

Task-Id: L1-F3-04
Lane: L1
Phase: F3
Spec: §7, §7.1, §7.3, §8, §15.1, §47.9
AT: none
Invariant: none
Agent-Authored: true
Self-Verify: bash validators/registry/verify-people.sh
MSGEOF
```

Then confirm what actually landed:

```bash
git show --stat --oneline HEAD
```

**CAPTURED**

```
93e6c94 schema(schemas-registry): add people registry schema v1
 schemas/registry/people.schema.json                | 242 +++++++++++++++++++++
 .../invalid/001-contractor-with-null-end-date.yaml |  15 ++
 .../invalid/002-departed-but-not-revoked.yaml      |  15 ++
 .../invalid/003-revoked-employee-still-active.yaml |  16 ++
 .../invalid/004-suspended-while-departing.yaml     |  15 ++
 .../people/invalid/005-timezone-is-utc-offset.yaml |  23 ++
 .../fixtures/people/invalid/006-fte-above-one.yaml |  23 ++
 .../invalid/007-unknown-top-level-property.yaml    |  17 ++
 .../people/invalid/008-empty-people-list.yaml      |   4 +
 .../people/invalid/009-wrong-registry-version.yaml |  15 ++
 .../people/valid/001-spec-section-7-example.yaml   |  48 ++++
 validators/registry/verify-people.sh               |  75 +++++++
 12 files changed, 508 insertions(+)
```

Twelve files, all additions, zero deletions, zero modifications to existing files.
That shape — pure additions — is what PARTITION rule 5 ("additive-only within a
lane") looks like when it is being followed.

---

## 13. Step 10 — Push and open the PR

**REMOTE**

```bash
git push -u origin lane/1/f3-04-people-registry-schema
```

```
Enumerating objects: 24, done.
Counting objects: 100% (24/24), done.
Delta compression using up to 8 threads
Compressing objects: 100% (18/18), done.
Writing objects: 100% (22/22), 6.41 KiB | 3.20 MiB/s, done.
Total 22 (delta 3), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (3/3), completed with 1 local object.
remote:
remote: Create a pull request for 'lane/1/f3-04-people-registry-schema' on GitHub by visiting:
remote:      https://github.com/<org>/control-plane/pull/new/lane/1/f3-04-people-registry-schema
 * [new branch]      lane/1/f3-04-people-registry-schema -> lane/1/f3-04-people-registry-schema
```

The base is **`integration`**. Never `main`. `main` is protected and only
`integration` merges into it (PARTITION, Branch & merge model).

**REMOTE**

````bash
gh pr create \
  --base integration \
  --head lane/1/f3-04-people-registry-schema \
  --title "[L1] L1-F3-04 add people.yaml JSON Schema" \
  --body-file - <<'PRBODY'
## Task

L1-F3-04 — Lane 1 (Registries & Contracts). Authors the JSON Schema for the
control-plane people registry, `people.yaml`, per MasterSpec v4.0 Section 7.

## What this adds

| Path | Purpose |
|---|---|
| `schemas/registry/people.schema.json` | The structural contract (242 lines) |
| `validators/registry/verify-people.sh` | Self-verify: 1 valid + 9 invalid fixtures |
| `validators/registry/fixtures/people/**` | The 10 fixtures |

Pure additions. No existing file is modified.

## Scope

Every path is inside `schemas/registry/**` and `validators/registry/**`, both
owned exclusively by Lane 1. Local lane-guard check: `SCOPE OK`.

`validators/registry/run-suite.sh` discovers `verify-*.sh` by glob, so this
verifier joins the suite without editing any shared file (PARTITION rule 3).

## Rules encoded

- Required fields; `additionalProperties: false` at every object level
- `availability` / `access_status` as closed enums
- R1 — `end_date` mandatory for every non-employee (§7.1)
- R2 — `departed` ⇒ `revoked` (§7.1)
- R3 — `revoked` ⇒ `departed` or non-employee (§7.1)
- R4 — `suspended` only with `active` or `on_leave` (§7.1)
- `timezone` must be an IANA `Area/Location` identifier, never a UTC offset (§7.3)
- `0 < fte <= 1` (§7.3)

## Deliberately NOT encoded — please review these specifically

Two are anti-patterns the spec forbids:

- **`role` is not an enum.** §8: roles are configuration.
- **`employment_type` is not an enum.** §7.1: employment types are open-ended.
  The four values in the §7 example block are a comment, not a closed set.

Four are beyond what JSON Schema can express. They are assigned to **L1-P2-T007**
(registry validator) and are listed in the commit message:

- uniqueness of `id` across the `people` array
- `role` exists in `roles.yaml`; `ai_runtime` is on the §35 approved list
- the *"past `end_date`"* half of R3, which requires today's date
- `schedule` `start` < `end`

R3 as shipped is therefore **weaker than the spec sentence**, by design. The
`title` field on the R3 subschema records this and names where the rest lives.

## Verification

```
$ npx --no-install ajv compile -s schemas/registry/people.schema.json
schema schemas/registry/people.schema.json is valid

$ bash validators/registry/verify-people.sh
-- 10 passed, 0 failed --
SELF-VERIFY PASS: L1-F3-04

$ bash validators/registry/run-suite.sh
LANE 1 SUITE: 1 verifier(s), 0 failed
LANE-VERIFY PASS: lane 1
```

The invalid fixtures are asserted with `ajv test --invalid`, so an over-permissive
schema fails the suite rather than passing it.

## Refs

MasterSpec v4.0 §7, §7.1, §7.3, §8, §15.1, §47.9
PRBODY
````

---

## 14. Step 11 — Checks, then hand off. Merge is L0's, never yours

`manual/06-pr-and-review.md` §8 states this with no exception: **no agent merges
its own work, no agent merges anyone's work — merges to `integration` and to
`main` are performed by L0 only.** `manual/05-git-workflow.md` §10/§13 states the
same rule ("Machines never merge, approve, or promote"; "you never merge it
yourself"). Do not run `gh pr merge` under any circumstance, including "the
checks are all green and L0 is asleep." The canonical task loop
(`manual/02-task-execution-protocol.md`) has no merge step — it ends at Report,
immediately after the PR is open.

Confirm CI reported, so your report (§15) can say checks are green:

**REMOTE**

```bash
gh pr checks --watch
```

```
All checks were successful
0 failing, 3 successful, 0 pending

NAME          DESCRIPTION  ELAPSED  URL
lane-guard                 12s      https://github.com/.../runs/...
lane-1-suite               41s      https://github.com/.../runs/...
schema-compile             18s      https://github.com/.../runs/...
```

Your task ends here. When L0 merges, `master/02-branch-merge-model.md` §5.2
mandates `gh pr merge $PR --merge --delete-branch` — a merge commit, never
`--squash`, never `--rebase` — because the repository ruleset sets
`allow_squash_merge=false` (decision REG-012). That command, and the branch
delete and cleanup that follow it, are L0's to run, not yours.

Merge-train reminders that are not yours to override:
- You never run `gh pr merge`, on your own branch or anyone else's.
- You never merge, rebase or touch another lane's branch.
- Merges to `integration` and to `main` are L0's move, not yours.

---

## 15. Step 12 — Report back, verbatim template

Fill in every field. Paste **real** output; never paraphrase a result.

```text
TASK:        L1-F3-04
BRANCH:      lane/1/f3-04-people-registry-schema
STATUS:      COMPLETE

FILES CREATED (12):
  schemas/registry/people.schema.json                                     242 lines
  validators/registry/verify-people.sh                                     75 lines
  validators/registry/fixtures/people/valid/001-spec-section-7-example.yaml
  validators/registry/fixtures/people/invalid/001-contractor-with-null-end-date.yaml
  validators/registry/fixtures/people/invalid/002-departed-but-not-revoked.yaml
  validators/registry/fixtures/people/invalid/003-revoked-employee-still-active.yaml
  validators/registry/fixtures/people/invalid/004-suspended-while-departing.yaml
  validators/registry/fixtures/people/invalid/005-timezone-is-utc-offset.yaml
  validators/registry/fixtures/people/invalid/006-fte-above-one.yaml
  validators/registry/fixtures/people/invalid/007-unknown-top-level-property.yaml
  validators/registry/fixtures/people/invalid/008-empty-people-list.yaml
  validators/registry/fixtures/people/invalid/009-wrong-registry-version.yaml

FILES MODIFIED: none
FILES DELETED:  none

ACCEPTANCE CRITERIA:
  A  ajv compile               PASS   "schema ... is valid", exit 0
  B  verify-people.sh          PASS   "10 passed, 0 failed / SELF-VERIFY PASS: L1-F3-04", exit 0
  C  run-suite.sh              PASS   "LANE-VERIFY PASS: lane 1", exit 0
  D  12 files staged, 0 others PASS   lane-guard self-check: SCOPE OK

SELF-VERIFY OUTPUT (verbatim):
  == people.schema.json ==
  ok    valid  001-spec-section-7-example.yaml
  ok    invalid  001-contractor-with-null-end-date.yaml
  ok    invalid  002-departed-but-not-revoked.yaml
  ok    invalid  003-revoked-employee-still-active.yaml
  ok    invalid  004-suspended-while-departing.yaml
  ok    invalid  005-timezone-is-utc-offset.yaml
  ok    invalid  006-fte-above-one.yaml
  ok    invalid  007-unknown-top-level-property.yaml
  ok    invalid  008-empty-people-list.yaml
  ok    invalid  009-wrong-registry-version.yaml
  -- 10 passed, 0 failed --
  SELF-VERIFY PASS: L1-F3-04
  EXIT=0

DEFERRED PER TASK SPEC §6 (not implemented, by instruction):
  - id uniqueness across the array
  - role/ai_runtime cross-file existence checks
  - the "past end_date" half of R3
  - schedule start < end

DEVIATIONS FROM TASK SPEC: none
BLOCKERS OPENED:           none
PR:                        #<n>, open against integration; checks green; merge pending L0
```

If any line above would be untrue, **STATUS is not COMPLETE.** Use `BLOCKED` or
`PARTIAL`, state exactly which acceptance criteria failed, and stop. A partially
finished task reported honestly costs the build an hour; one reported as complete
costs it a day and poisons every task downstream of it.

---

## 16. The blocker issue template

The blocker template, its required evidence per stop code, and the filing
procedure are owned by `manual/03-guardrails-and-stop-rules.md` §6 — not by
this file. It is not duplicated here so the two cannot drift; go there for
the complete field set. What follows is that same procedure with this task's
real values filled in, so the *shape* of a filed blocker is still visible
here.

Use this whenever a STOP rule fires. Open it, then stop working on the task.

**REMOTE**

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER [L1][L1-F3-04] <one line, under 60 chars, no speculation>" \
  --label "blocker" \
  --label "lane-1" \
  --label "stop-0<N>" \
  --body-file - <<'ISSUEBODY'
## Task
L1-F3-04 — add people.yaml JSON Schema
Branch: lane/1/f3-04-people-registry-schema

## Stop rule triggered
S<n> — <quote the stop rule text from the task spec verbatim>

## What I observed
<the exact command run, and its exact output — no paraphrase>

## Why I stopped instead of deciding
<state the specific ambiguity. Name the two or more readings that are both
defensible. Do not recommend one.>

## What I have NOT done
<list every file not written and every acceptance criterion not met>

## State of the branch
<git status --short output>
Committed: <yes/no>. Pushed: <yes/no>.

## What I need from L0
A decision on: <the single question, phrased so the answer is a value or a
path, not an essay>
ISSUEBODY
```

The point of the "Why I stopped" section: it must name a genuine ambiguity. If you
can only write "I was not sure", you were not blocked — you were guessing at whether
to guess. Reread the task spec.

---

## 17. Trap index — where each known failure mode was defended in this run

Every one of these has bitten a cheap agent on a real build. The right-hand column
is the specific step above that stops it.

| Failure mode | Defended by |
|---|---|
| Inventing a plausible file path | §2 preflight `ls -l` on every promised file; stop rule S1 |
| Writing a subtly wrong command and reporting success | §8 four-part success reading: string, count, `0 failed`, `EXIT=0` |
| A verifier that asserts nothing but prints PASS | §6 the `pass -lt 2` guard; §10 the `total -eq 0` guard |
| A schema that accepts everything | §5 nine invalid fixtures asserted with `ajv test --invalid` |
| Silently completing part of the task | §11 count the twelve `A` lines; §15 per-criterion report |
| Drifting outside assigned scope | §11 lane-guard self-check before commit |
| Re-implementing another lane's work | Task §6 names the owning task, L1-P2-T007, explicitly |
| Reporting a test as passing without running it | §15 requires verbatim output including `EXIT=` |
| Guessing at an ambiguity | Task §4 pre-decides every choice; §16 blocker template |
| "Fixing" the schema to satisfy a broken loader | Task §7 mandates `yaml2json.js`; §9 decision table |
| Deleting a fixture to make the suite green | §9: `FAIL invalid` always means fix the schema, never the fixture |
| Editing a shared file to register a new check | §6 `run-suite.sh` discovers by glob; PARTITION rule 3 |
| Opening the PR against `main` | §13 `--base integration`, stated twice |

---

## 18. The one-screen version

```bash
set -euo pipefail
# 0. preflight
cd /path/to/control-plane
ls -l validators/registry/run-suite.sh validators/registry/yaml2json.js package.json
git fetch origin && git checkout -B lane/1/f3-04-people-registry-schema origin/integration

# 1. write the files listed in the task spec §2 — and only those

# 2. verify, all three, in order
npx --no-install ajv compile -s schemas/registry/people.schema.json; echo "EXIT=$?"
bash validators/registry/verify-people.sh;                 echo "EXIT=$?"
bash validators/registry/run-suite.sh;                     echo "EXIT=$?"

# 3. stage exactly the task's files, then prove scope
git add schemas/registry/people.schema.json \
        validators/registry/verify-people.sh \
        validators/registry/fixtures
git status --short
git diff --cached --name-only \
  | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "SCOPE VIOLATION -- do not commit" \
  || echo "SCOPE OK: every staged path is owned by Lane 1"

# 4. commit, push, PR against integration
git commit -F <commit-message-file>
git show --stat --oneline HEAD
git push -u origin lane/1/f3-04-people-registry-schema
gh pr create --base integration --head lane/1/f3-04-people-registry-schema \
             --title "[L1] L1-F3-04 add people.yaml JSON Schema" \
             --body-file <pr-body-file>

# 5. confirm checks; merge is L0's job, not yours -- never run gh pr merge
gh pr checks --watch

# 6. report using the §15 template, with real output pasted in
```

**If any step produces output you did not expect, stop and open a blocker.
An unexpected result is information, not an obstacle to route around.**
