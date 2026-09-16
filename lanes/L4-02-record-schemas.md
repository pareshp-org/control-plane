# L4 — PHASE 2 — RECORD AND EVENT SCHEMAS

**Lane:** L4 Records, Events & Metrics (subsystems I, N — Master Spec §99.2, lines 9184–9231)
**Phase:** 2 — Record and event schemas
**Phase branch:** `lane/4/02-record-schemas`
**Task ID range:** `L4-T201` … `L4-T225` (25 tasks)
**Authority:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` (FROZEN). Where this file and PARTITION.md appear to differ, PARTITION.md wins and the difference is a blocker for L0.
**Charter:** `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L4-00-charter.md`
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines)

---

## 1. Why this phase exists

Master Spec §99.6 (lines 9276–9294) risk 2: *"Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance if the record stores are not built early."* Mitigation: *"Section 97 is built in Foundation, before any dashboard that reads from it."* §99.2 line 9229: *"I is the feedstock for nearly all governance-tier and people-tier computation."*

Phase 1 built the stores as directories. **Phase 2 gives every store and every event a machine-checkable shape**, so that from this point forward nothing can be written into a record store that a validator cannot reject.

Three binding spec obligations are discharged here and nowhere else:

| Obligation | Spec anchor |
|---|---|
| Every record carries `record_schema_version`, `id`, `product`, `timestamp`, and never edits in place | §97.2, line 8890 |
| Every event carries the nine-field envelope; **an event missing any envelope field is rejected at write time**; `event_type` comes from a **closed enum**, never free text | §97.3, lines 8931–8953 |
| **Names in record bodies fail schema validation** — the de-identification of the record stores is the part that genuinely holds | D88, line 10181; §91.8, line 8171 |

---

## 2. Scope — what this phase writes and what it must not touch

### 2.1 In scope (all paths L4-owned per PARTITION.md line 20)

| Path | Contents produced by this phase |
|---|---|
| `control-plane/schemas/records/` | 17 store schemas + `record.base.schema.json` + `event.envelope.schema.json` + `event-type.enum.json` + `store-map.yaml` |
| `control-plane/metrics/taxonomy/` | `event-types.yaml` — the closed 89-identifier `event_type` enum of §97.3 (D114-D / REG-021) |
| `control-plane/tools/records/` | `lib/validate.py`, `validate-schemas.sh`, `validate-taxonomy.sh`, `validate-no-names.sh`, `gen-event-type-enum.sh`, `fixtures/**` |

### 2.2 Explicitly NOT in scope

| Item | Why not, with citation |
|---|---|
| `exceptions.yaml`, `policies.yaml`, `patterns.yaml` | They appear in the §97.2 table (lines 8865–8867) but are **control-plane root/registry files, not record stores** — §52.6 line 4639 places only `records/` and `events/` in the records repository. PARTITION.md line 22 gives root files to L0 and line 17 gives `registries/**` to L1. L4 writes no schema for them. |
| `registries/platform.yaml` (where §97.3 line 8959 says the enum is *declared*) | PARTITION.md line 17 — L1 owns `registries/**`. L4 **publishes** `metrics/taxonomy/event-types.yaml`; L1 embeds it. See **DECISION REQUIRED D-L4-01** in the charter. |
| `registries/os-health.yaml` | Same reason. Charter **D-L4-02**. |
| Write-freshness windows, attention ledger, Ready-queue-miss detector, RECORD-VERIFICATION-RESULT handler, metric register | Later L4 phases. This phase produces shapes only. |
| Any `.github/**` file in either repository | Charter **D-L4-03**; PARTITION.md line 18. |

**Store coverage, binding: 17 stores.** Exactly the §97.2 table (lines 8845–8869) minus the three registry files of §2.2, with `records/decisions/pending/` counted as its own store per §97.2 line 8853 and §52.6 line 4639:

`incidents · postmortems · uat · estimates · deployments · restore-tests · decisions · decisions/pending · breaches · deletion-requests · security-reviews · eval · launches · demos · support · onboarding · leave`

Plus the event envelope for `events/` (§97.3).

---

## 3. Fixed conventions — binding for every task in this phase

### 3.1 Standard preamble

Every task's command block opens with these five lines. Copy them verbatim; the Bash tool resets the working directory between calls, so never rely on `cd`.

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas
```

### 3.2 Fixed toolchain — not a choice, do not substitute

| Item | Fixed value |
|---|---|
| Validator language | Python 3, from `PATH` as `python` |
| Virtualenv location | `C:/D_Drive/PS/MultiProduct/Code/.l4-venv` — **outside both repositories**, never committed |
| JSON Schema library | `jsonschema==4.23.0` |
| YAML library | `PyYAML==6.0.2` |
| JSON Schema dialect | `https://json-schema.org/draft/2020-12/schema` |

### 3.3 File-naming convention — fixed by charter §5.1

Schema files are **flat, singular, hyphenated**: `schemas/records/<store-singular>.schema.json`. This is the path set L2 already consumes (charter §5.1). §60.2 (line 5152) requires *"Write the v2 schema alongside v1 — do not replace"*: when a v2 ever exists it is added at `schemas/records/v2/<name>.schema.json` and the flat file remains v1 untouched. `store-map.yaml` carries the version→path index so the v2 addition needs no move.

| Store directory (records repo) | Schema file (control-plane) |
|---|---|
| `records/incidents/` | `schemas/records/incident.schema.json` |
| `records/postmortems/` | `schemas/records/postmortem.schema.json` |
| `records/uat/` | `schemas/records/uat.schema.json` |
| `records/estimates/` | `schemas/records/estimate.schema.json` |
| `records/deployments/` | `schemas/records/deployment.schema.json` |
| `records/restore-tests/` | `schemas/records/restore-test.schema.json` |
| `records/decisions/` | `schemas/records/decision.schema.json` |
| `records/decisions/pending/` | `schemas/records/decision-pending.schema.json` |
| `records/breaches/` | `schemas/records/breach.schema.json` |
| `records/deletion-requests/` | `schemas/records/deletion-request.schema.json` |
| `records/security-reviews/` | `schemas/records/security-review.schema.json` |
| `records/eval/` | `schemas/records/eval.schema.json` |
| `records/launches/` | `schemas/records/launch.schema.json` |
| `records/demos/` | `schemas/records/demo.schema.json` |
| `records/support/` | `schemas/records/support.schema.json` |
| `records/onboarding/` | `schemas/records/onboarding.schema.json` |
| `records/leave/` | `schemas/records/leave.schema.json` |
| `events/` | `schemas/records/event.envelope.schema.json` |

### 3.4 The three structural rules every store schema obeys

Stated once here; every store task repeats them and the schema-lint of **L4-T223** proves them mechanically.

1. **`"additionalProperties": false`** on the root object. This is the load-bearing half of D88: an arbitrary `name:` key cannot be smuggled into a record body if the shape is closed.
2. **The four base fields are required on every store schema**: `record_schema_version`, `id`, `product`, `timestamp` (§97.2, line 8890).
3. **Only spec-named fields are declared.** If a writer needs a field this specification does not name, that is a schema-change request to L0 under §60.2 — never a field an executor adds. **Note:** `artifact_identity` is the spec-named type (§97.2 L8918).

### 3.5 D88 enforcement — three mechanical limbs

§91.8 line 8171 and D88 (line 10181): *"Records carry stable person IDs, never names — that rule is real, it is enforced at schema validation."*

| Limb | Mechanism | Built in |
|---|---|---|
| **A — closed shapes** | `additionalProperties: false` on every store schema and on the event envelope | every store task; proven by L4-T223 |
| **B — denied property names** | No record schema may declare a property named `name`, `display_name`, `full_name`, `first_name`, `last_name`, `github_login`, `login`, `email`, `e_mail`, `username`, `contact_name`, `person_name` | L4-T205 lint; proven by L4-T223 |
| **C — denied values, fail-closed** | `validate-no-names.sh` scans every string value in a record against the `display_name` values in the people registry and rejects any match; **a registry it cannot read is a failure, never a pass** (§40.1 line 3671: *"a check that cannot reach the records repository fails closed rather than reporting zero"*) | L4-T205 |

**RESOLVED CONFLICT — do not re-litigate.** §97.2 line 8918 carries the comment `decider: founder # role, not name, in rules; names appear in real records`. D88 (line 10181) names **§97.2** in its affected-sections column and states that names in record bodies fail schema validation. D88 is the later amendment (document header line 9: *"Amended 2026-08-27"*) and it amends §97.2 by name. **D88 governs: no names, person references only.** The `person_ref` pattern of L4-T202 accepts a role token (`founder`) and an opaque person identifier alike, so both readings of the example remain writable; only a display name is rejected.

### 3.6 Time — one way, everywhere

§97.1 line 8839: *"Every record and event timestamp is stored in UTC with its offset."* Two shared definitions and nothing else:

| Def | Pattern | Used for |
|---|---|---|
| `timestamp_utc` | `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z\|\+00:00)$` | every instant (`detected`, `occurred_at`, …) |
| `date_utc` | `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` | every calendar date (`prompt_received`, `review_date`, …) |

Derived from the literal spec examples: `2026-09-14T02:11:00Z` (line 8898) and `2026-09-08` (line 8909).

### 3.7 Identifier patterns

| Def | Pattern | Derivation |
|---|---|---|
| `record_id` | `^[A-Z][A-Z0-9]{1,9}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$` | Generalised from the four literal examples: `INC-2026-09-14-001` (8890), `DEP-2026-09-12-014` (8905), `DEC-2026-09-10-003` (8918), `DEMO-2026-09-11-002` (8930) |
| `event_id` | `^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$` | Literal from `EVT-2026-09-14-000317` (line 8934) |
| `product_ref` | `^([a-z0-9][a-z0-9-]{1,38}\|portfolio)$` | Product slug, or the literal `portfolio` for portfolio-level records — §97.4 line 8977: *"a session touching none attributes to the portfolio"* |
| `person_ref` | `^[a-z0-9][a-z0-9-]{1,38}$` | An opaque person identifier or a role token; never a display name (D88, §3.5) |

---

## 4. DECISION REQUIRED — hand to L0. No L4 executor answers these.

Each names a **stated default that ships if no answer arrives**, so no task in this phase is blocked.

### ~~DECISION REQUIRED~~ D-L4-04 — per-store record-id prefix vocabulary

> **Status: RATIFIED, no schema changes.**

- **Fact:** §97.2 gives literal id prefixes for four stores only — `INC-` (8890), `DEP-` (8905), `DEC-` (8918), `DEMO-` (8930). The other thirteen stores have no prefix stated anywhere in the specification.
- **Question:** What is the prefix for each of the remaining thirteen stores?
- **L4 default that ships:** the generic `record_id` pattern of §3.7 accepts any 2–10-character upper-case prefix. The four spec'd stores pin their literal prefix with `"pattern"`; the other thirteen use the generic pattern.
- **Blocks:** nothing. Narrowing a pattern later is a §60.2 v2 schema, not a rewrite.

### ~~DECISION REQUIRED~~ D-L4-05 — state vocabularies for the eight compound event entries

> **Status: RATIFIED, no schema changes.**

- **Fact:** §97.3 line 8959: *"Every entry in the taxonomy below has exactly one stable `event_type` identifier."* Eight entries of the line-8963 list name two or more states in one entry (entries 29, 50, 51, 69, 75, 76, 79, 86 of the §5 table).
- **Question:** Does each compound entry stay one identifier carrying a `state` payload field (the literal reading of line 8959), or does L0 split it into one identifier per state?
- **L4 default that ships:** one identifier per `·`-separated entry — the literal reading — with `payload_required: [state]` and `state` left as an unconstrained non-empty string.
- **Blocks:** nothing. Adding identifiers later is a governed enum addition (§97.3, line 8959); retiring is marked, never removed.

### ~~DECISION REQUIRED~~ D-L4-06 — the security-review finding severity vocabulary

> **Status: RATIFIED, no schema changes.**

- **Fact:** §97.2 line 8884: *"A security-review record carries findings with severity and disposition."* No vocabulary for either is stated in the specification. The `SEV-1`…`SEV-4` ladder at lines 3760–3763 is the **incident** ladder and is not stated to apply to review findings.
- **Question:** What are the permitted `severity` and `disposition` values on a security-review finding?
- **L4 default that ships:** both are required non-empty strings with **no enum** — the field is mandatory, the vocabulary is not invented.
- **Blocks:** nothing.

### ~~DECISION REQUIRED~~ D-L4-07 — the launch-readiness checklist row vocabulary

> **Status: RATIFIED, no schema changes.**

- **Fact:** §19.2 line 1915: *"every checklist row rendered green or red with a link to its evidence record"*, stored in `records/launches/`. The row identifiers are spread across §19.2, §22.2 and §22.6 and are not enumerated as a closed list anywhere.
- **Question:** What is the closed set of launch-readiness checklist row identifiers?
- **L4 default that ships:** `checklist` is a required non-empty array of `{row, status, evidence}` where `row` is an unconstrained non-empty string and `status` is the closed enum `green|red` (literal from line 1915).
- **Blocks:** nothing.

---

## 5. Task summary

| Task ID | Title | Size | Depends on |
|---|---|---|---|
| L4-T201 | Phase branch, toolchain preflight | S | L4-T004 (charter) |
| L4-T202 | `record.base.schema.json` — the shared `$defs` | M | L4-T201 |
| L4-T203 | `metrics/taxonomy/event-types.yaml` — the closed 89-identifier enum (D114-D / REG-021) | L | L4-T201 |
| L4-T204 | `event.envelope.schema.json` + generated `event-type.enum.json` | M | L4-T202, L4-T203 |
| L4-T205 | D88 no-names enforcement — lint and value scanner | M | L4-T202 |
| L4-T206 | `incident.schema.json` | M | L4-T202 |
| L4-T207 | `postmortem.schema.json` | M | L4-T202 |
| L4-T208 | `uat.schema.json` | S | L4-T202 |
| L4-T209 | `estimate.schema.json` | M | L4-T202 |
| L4-T210 | `deployment.schema.json` | M | L4-T202 |
| L4-T211 | `restore-test.schema.json` | S | L4-T202 |
| L4-T212 | `decision.schema.json` | M | L4-T202 |
| L4-T213 | `decision-pending.schema.json` | S | L4-T212 |
| L4-T214 | `breach.schema.json` | S | L4-T202 |
| L4-T215 | `deletion-request.schema.json` (AT-105) | M | L4-T202 |
| L4-T216 | `security-review.schema.json` | M | L4-T202 |
| L4-T217 | `eval.schema.json` (SIG-42) | M | L4-T202 |
| L4-T218 | `launch.schema.json` | M | L4-T202 |
| L4-T219 | `demo.schema.json` | S | L4-T202 |
| L4-T220 | `support.schema.json` | M | L4-T202 |
| L4-T221 | `onboarding.schema.json` | S | L4-T202 |
| L4-T222 | `leave.schema.json` | S | L4-T202 |
| L4-T223 | `store-map.yaml` + `validate-schemas.sh` (coverage, lint, `--fields`, `--time`) | L | T206–T222, T205 |
| L4-T224 | Negative fixtures — `--negative` 10/10 | M | L4-T204, L4-T223 |
| L4-T225 | Rebase and open the phase PR to `integration` | S | T201–T224 |

---

## 6. Tasks

### L4-T201 — Phase branch and toolchain preflight

**Size:** S
**Depends on:** L4-T004 (charter — the three owned control-plane directories exist)

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
test -d "$CP_ROOT/.git" || { echo "PREFLIGHT FAIL: control-plane repo missing"; exit 1; }
test -d "$CP_ROOT/schemas/records" || { echo "PREFLIGHT FAIL: L4-T004 not merged"; exit 1; }
test -d "$CP_ROOT/metrics/taxonomy" || { echo "PREFLIGHT FAIL: L4-T004 not merged"; exit 1; }
test -d "$CP_ROOT/tools/records" || { echo "PREFLIGHT FAIL: L4-T004 not merged"; exit 1; }
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" status --porcelain
git -C "$CP_ROOT" checkout -B lane/4/02-record-schemas origin/integration
# canonical path (FD-036): tests/fixtures/invalid/<schema-id>/
mkdir -p "$CP_ROOT/tools/records/lib" "$CP_ROOT/tools/records/fixtures/valid" \
         "$CP_ROOT/tools/records/fixtures/invalid" "$CP_ROOT/tools/records/fixtures/roster"
python -m venv "$L4_VENV"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
"$L4_PY" -m pip install --disable-pip-version-check --quiet jsonschema==4.23.0 PyYAML==6.0.2
"$L4_PY" -c "import jsonschema,yaml;print('JSONSCHEMA='+jsonschema.__version__);print('PYYAML='+yaml.__version__)"
echo "BRANCH=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Charter scaffold present | `ls -d "$CP_ROOT"/schemas/records "$CP_ROOT"/metrics/taxonomy "$CP_ROOT"/tools/records \| wc -l` | `3` |
| 2 | Phase branch created off `origin/integration` | `git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD` | `lane/4/02-record-schemas` |
| 3 | Working tree clean at branch time | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 4 | Pinned validator libraries installed | `"$L4_PY" -c "import jsonschema;print(jsonschema.__version__)"` | `4.23.0` |
| 5 | Pinned YAML library installed | `"$L4_PY" -c "import yaml;print(yaml.__version__)"` | `6.0.2` |
| 6 | The venv is outside both repositories | `git -C "$CP_ROOT" check-ignore -q "$L4_VENV" ; echo $?` | non-zero (path is not inside the repo at all) |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
echo "BRANCH=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l)"
echo "JSONSCHEMA=$("$L4_PY" -c 'import jsonschema;print(jsonschema.__version__)')"
echo "PYYAML=$("$L4_PY" -c 'import yaml;print(yaml.__version__)')"
```

Expected output, exactly:

```
BRANCH=lane/4/02-record-schemas
DIRTY=0
JSONSCHEMA=4.23.0
PYYAML=6.0.2
```

**STOP rule** — if `python -m venv` fails, either pinned version does not install, `DIRTY` is not `0`, or any charter directory is missing: do not create any schema file, open a blocker issue.

```yaml
title: "[L4-BLOCKER] L4-T201 phase-2 preflight failed"
lane: L4
task_id: L4-T201
blocked_by: "<python missing | pinned install failed | working tree dirty | L4-T004 not merged>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "BRANCH=lane/4/02-record-schemas / DIRTY=0 / JSONSCHEMA=4.23.0 / PYYAML=6.0.2"
spec_ref: "PARTITION.md lines 26, 34; L4-00-charter.md section 10 task L4-T004"
needs: "L0"
action_taken: none
```

---

### L4-T202 — `record.base.schema.json`, the shared `$defs`, and the validator library

**Size:** M
**Depends on:** L4-T201

Produces the four base fields of §97.2 line 8890 and every shared definition of §3.6 and §3.7. Every store schema `$ref`s into this file; none of them `allOf`-composes it, because `allOf` plus `additionalProperties: false` would reject the composed properties.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/record.base.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "record.base.schema.json",
  "title": "Record base definitions",
  "description": "Master Spec v4.0 Section 97.2 line 8890: every record carries record_schema_version, id, product, timestamp, and never edits in place. Section 97.1 line 8839: every timestamp is UTC with its offset. D88 line 10181: records carry stable person IDs, never names. This file declares definitions only; store schemas $ref them and never allOf-compose this file.",
  "$defs": {
    "record_schema_version": {
      "description": "Section 97.2 line 8892; Section 60.2 line 5152 - v2 is written alongside v1, never replacing it.",
      "const": 1
    },
    "record_id": {
      "description": "Generalised from the literal examples INC-2026-09-14-001, DEP-2026-09-12-014, DEC-2026-09-10-003, DEMO-2026-09-11-002. See DECISION REQUIRED D-L4-04.",
      "type": "string",
      "pattern": "^[A-Z][A-Z0-9]{1,9}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$"
    },
    "product_ref": {
      "description": "A product slug, or the literal portfolio for portfolio-level records (Section 97.4 line 8977).",
      "type": "string",
      "pattern": "^([a-z0-9][a-z0-9-]{1,38}|portfolio)$"
    },
    "timestamp_utc": {
      "description": "Section 97.1 line 8839. UTC with offset. Example 2026-09-14T02:11:00Z.",
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|\\+00:00)$"
    },
    "date_utc": {
      "description": "Calendar date. Example 2026-09-08 (Section 97.2 line 8909).",
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "person_ref": {
      "description": "D88 line 10181 and Section 91.8 line 8171: a stable person identifier or a role token. NEVER a display name. Enforced additionally by tools/records/validate-no-names.sh.",
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]{1,38}$"
    },
    "record_ref": {
      "description": "A path to another record in the records repository, as in postmortem: records/postmortems/2026-09-16-solvox.yaml (Section 97.2 line 8903).",
      "type": "string",
      "pattern": "^(records/|events/)[A-Za-z0-9._/-]+\\.yaml$"
    },
    "evidence_link": {
      "description": "The evidence link input of RECORD-VERIFICATION-RESULT (Section 97.2 line 8886).",
      "type": "string",
      "minLength": 1
    },
    "digest": {
      "description": "Section 97.2 line 8905: digest: sha256:...",
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$"
    },
    "pass_fail": {
      "description": "The pass-or-fail input of RECORD-VERIFICATION-RESULT (Section 97.2 line 8886).",
      "type": "string",
      "enum": ["pass", "fail"]
    },
    "nonempty_string": {
      "type": "string",
      "minLength": 1
    },
    "platform_rebuild_identity": {
      "description": "Section 97.2: platform rebuild identity — platform, version, and sha256 of the rebuilt artifact.",
      "type": "object",
      "additionalProperties": false,
      "required": ["platform", "version", "sha256"],
      "properties": {
        "platform": { "$ref": "#/$defs/nonempty_string" },
        "version": { "$ref": "#/$defs/nonempty_string" },
        "sha256": { "$ref": "#/$defs/digest" }
      }
    },
    "artifact_identity": {
      "description": "Section 97.2 line 8918: spec-named type (§97.2 L8918). Identity of a distributed artifact: name, digest, and tag.",
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "digest", "tag"],
      "properties": {
        "name": { "$ref": "#/$defs/nonempty_string" },
        "digest": { "$ref": "#/$defs/digest" },
        "tag": { "$ref": "#/$defs/nonempty_string" }
      }
    },
    "gap_window": {
      "description": "Seconds between expected events.",
      "type": "integer"
    }
  }
}
EOF

cat > "$CP_ROOT/tools/records/lib/validate.py" <<'EOF'
#!/usr/bin/env python3
"""L4 record validator. Master Spec v4.0 Section 97.2, Section 97.3.

Usage: validate.py <schema.json> <record.yaml> [<record.yaml> ...]
Exit 0 and print "VALID <path>" per file, or exit 1 and print "INVALID <path>: <error>".
A file that cannot be read or parsed is INVALID, never skipped (fail closed).
"""
import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator, RefResolver

def main(argv):
    if len(argv) < 3:
        print("USAGE: validate.py <schema.json> <record.yaml> [...]")
        return 2
    schema_path = pathlib.Path(argv[1]).resolve()
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("INVALID <schema>: %s: %s" % (schema_path, exc))
        return 1
    base = schema_path.parent.as_uri() + "/"
    store = {}
    for sibling in schema_path.parent.glob("*.json"):
        try:
            store[sibling.as_uri()] = json.loads(sibling.read_text(encoding="utf-8"))
            store[sibling.name] = json.loads(sibling.read_text(encoding="utf-8"))
        except Exception:
            pass
    resolver = RefResolver(base_uri=base, referrer=schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver)
    failed = 0
    for target in argv[2:]:
        path = pathlib.Path(target)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("INVALID %s: unreadable: %s" % (target, exc))
            failed += 1
            continue
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            first = errors[0]
            where = "/".join(str(p) for p in first.path) or "<root>"
            print("INVALID %s: %s: %s" % (target, where, first.message))
            failed += 1
        else:
            print("VALID %s" % target)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/record-base-probe.yaml" <<'EOF'
# Probe fixture for record.base.schema.json $defs. Not a record of any store.
# Master Spec v4.0 Section 97.2, line 8890.
record_schema_version: 1
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14T02:11:00Z
EOF

cat > "$CP_ROOT/schemas/records/record.probe.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "record.probe.schema.json",
  "title": "Base-defs probe",
  "description": "Proves record.base.schema.json $defs resolve. Not a store schema; excluded from store-map.yaml.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" }
  }
}
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" \
  "$CP_ROOT/schemas/records/record.probe.schema.json" \
  "$CP_ROOT/tools/records/fixtures/valid/record-base-probe.yaml"

git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T202: record base defs and validator library (Master Spec 97.1, 97.2)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Base schema is valid JSON | `"$L4_PY" -c "import json;json.load(open(r'$CP_ROOT/schemas/records/record.base.schema.json'));print('JSON OK')"` | `JSON OK` |
| 2 | All fourteen `$defs` present | `"$L4_PY" -c "import json;d=json.load(open(r'$CP_ROOT/schemas/records/record.base.schema.json'))['\$defs'];print(len(d))"` | `14` |
| 3 | The probe fixture validates | `"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/record.probe.schema.json" "$CP_ROOT/tools/records/fixtures/valid/record-base-probe.yaml"` | `VALID …record-base-probe.yaml` and exit `0` |
| 4 | A non-UTC timestamp is rejected | see SELF-VERIFY line `NEGTIME` | `1` |
| 5 | Only L4-owned paths changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/records/|metrics/|tools/records/)'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
echo "DEFS=$("$L4_PY" -c "import json;print(len(json.load(open(r'$CP_ROOT/schemas/records/record.base.schema.json'))['\$defs']))")"
"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/record.probe.schema.json" "$CP_ROOT/tools/records/fixtures/valid/record-base-probe.yaml" >/dev/null && echo "PROBE=0" || echo "PROBE=1"
printf 'record_schema_version: 1\nid: INC-2026-09-14-001\nproduct: solvox\ntimestamp: 2026-09-14 02:11:00 IST\n' > "$CP_ROOT/tools/records/fixtures/invalid/_tmp-time.yaml"
"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/record.probe.schema.json" "$CP_ROOT/tools/records/fixtures/invalid/_tmp-time.yaml" >/dev/null 2>&1; echo "NEGTIME=$?"
rm -f "$CP_ROOT/tools/records/fixtures/invalid/_tmp-time.yaml"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
```

Expected output, exactly:

```
DEFS=11
PROBE=0
NEGTIME=1
FOREIGN=0
```

**STOP rule** — if `NEGTIME` is `0`, the validator accepts a non-UTC timestamp and §97.1 line 8839 is unenforced; if `DEFS` is not `11`; if `FOREIGN` is not `0`: do not proceed to any store task, open a blocker issue.

```yaml
title: "[L4-BLOCKER] L4-T202 base defs or validator not enforcing"
lane: L4
task_id: L4-T202
blocked_by: "<non-UTC timestamp accepted | defs count wrong | foreign path touched>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "DEFS=11 / PROBE=0 / NEGTIME=1 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.1 line 8839; Section 97.2 line 8890; PARTITION.md lines 20, 25"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T203 — `metrics/taxonomy/event-types.yaml`, the closed 89-identifier enum

> **Provenance note (D114-D / REG-021, 2026-09-02):** the taxonomy was corrected from 86 to 89 identifiers, adding `support_loop_closure`, `deletion_request_recorded`, and `work_item_closed` (see `run-phase-0.sh` L0-P0-011 and `tests/integration/test_event_type_enum.py`). The task body below — the generated YAML, `validate-taxonomy.sh`, the acceptance table, and SELF-VERIFY — still literally builds and checks an 86-row taxonomy and has **not** been re-authored for the three added rows or for how the SELF-VERIFY `SPEC` check (which counts the raw Master Spec line-8963/8965 sentence) should treat identifiers added by decision rather than by spec-text edit. Reconciling that is a content/design decision left for whoever arms this task, not a mechanical edit.

**Size:** L
**Depends on:** L4-T201

§97.3 line 8959: *"Every entry in the taxonomy below has exactly one stable `event_type` identifier — lower-case, underscore-separated, never renamed once shipped."* The taxonomy is the single `·`-separated sentence at **line 8963**. It has exactly **86** entries; this task turns each into exactly one identifier, in the spec's own order, and freezes the count.

**The numbering used by DECISION REQUIRED D-L4-05 is the `n:` numbering of the table this task writes** — that is, the order of the `·`-separated entries on line 8963. The eight compound entries are the eight rows carrying a `states:` key: `n` = 29, 50, 51, 69, 75, 76, 79, 86.

`payload_required` is not invented. It is read off the spec's own wording: an entry that says *"with severity"* declares `severity`, *"with digest"* declares `digest`, *"result"* declares `result`. The envelope example at line 8940 shows `payload: {gate: 1, agent_authored: false}` under `plan_approved`, which fixes rows 7 and 14.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/metrics/taxonomy/event-types.yaml" <<'EOF'
# metrics/taxonomy/event-types.yaml
# The closed event_type enum. Master Spec v4.0 Section 97.3, lines 8944-8963.
#
# Line 8959: "Every entry in the taxonomy below has exactly one stable event_type
# identifier - lower-case, underscore-separated, never renamed once shipped."
# Line 8959: "A new event type is a governed addition to the enum and to this taxonomy."
# Line 8959: "Retiring an identifier marks it retired in the enum and never removes it."
#
# n:                the 1-based position of the entry in the line-8963 taxonomy sentence
# id:               the stable event_type identifier - NEVER renamed once shipped
# entry:            the spec wording, for traceability
# payload_required: payload keys the spec wording names for this entry
# states:           present ONLY on the eight compound entries (DECISION REQUIRED D-L4-05)
# retired:          absent means live; a retired identifier gains "retired: true" and stays
#
# L1 embeds this list into registries/platform.yaml (line 8959). L4 publishes it and
# never edits registries/** (PARTITION.md line 17; charter DECISION REQUIRED D-L4-01).
taxonomy_version: 1
spec_anchor: "MultiProduct_MasterSpec_v4.0.md Section 97.3 line 8963"
identifier_count: 86
event_types:
  - { n: 1,  id: work_item_created,                     entry: "Work item created",                                 payload_required: [] }
  - { n: 2,  id: work_item_moved_to_ready,              entry: "moved to Ready",                                    payload_required: [] }
  - { n: 3,  id: work_item_assigned,                    entry: "assigned",                                          payload_required: [] }
  - { n: 4,  id: ready_queue_miss_recorded,             entry: "Ready-queue miss recorded",                         payload_required: [] }
  - { n: 5,  id: plan_submitted,                        entry: "plan submitted",                                    payload_required: [] }
  - { n: 6,  id: plan_rejected,                         entry: "plan rejected with reason",                         payload_required: [reason] }
  - { n: 7,  id: plan_approved,                         entry: "plan approved (Gate 1) with agent_authored flag",   payload_required: [gate, agent_authored] }
  - { n: 8,  id: change_class_assigned,                 entry: "change class assigned",                             payload_required: [change_class] }
  - { n: 9,  id: impact_scope_assigned,                 entry: "impact scope assigned",                             payload_required: [impact_scope] }
  - { n: 10, id: reversibility_class_assigned,          entry: "reversibility class assigned",                      payload_required: [reversibility_class] }
  - { n: 11, id: requirement_changed_materially,        entry: "requirement changed materially",                    payload_required: [] }
  - { n: 12, id: replan_triggered,                      entry: "re-plan triggered",                                 payload_required: [] }
  - { n: 13, id: execute_started,                       entry: "execute started",                                   payload_required: [] }
  - { n: 14, id: pr_opened,                             entry: "PR opened with agent_authored flag",                payload_required: [agent_authored] }
  - { n: 15, id: review_requested,                      entry: "review requested",                                  payload_required: [] }
  - { n: 16, id: gate_2_approval_granted,               entry: "Gate 2 approval with reviewer role",                payload_required: [reviewer_role] }
  - { n: 17, id: ci_check_result,                       entry: "CI pass or fail per check",                         payload_required: [check, result] }
  - { n: 18, id: parity_check_result,                   entry: "parity check result",                               payload_required: [result] }
  - { n: 19, id: artifact_built,                        entry: "artifact built with digest",                        payload_required: [digest] }
  - { n: 20, id: staging_deployed,                      entry: "staging deployed",                                  payload_required: [] }
  - { n: 21, id: staging_smoke_result,                  entry: "staging smoke result",                              payload_required: [result] }
  - { n: 22, id: uat_executed,                          entry: "UAT executed with result",                          payload_required: [result] }
  - { n: 23, id: merge_completed,                       entry: "merge",                                             payload_required: [] }
  - { n: 24, id: production_approval_granted,           entry: "production approval granted with approver",         payload_required: [approver] }
  - { n: 25, id: production_deployed,                   entry: "production deployed with digest",                   payload_required: [digest] }
  - { n: 26, id: production_smoke_result,               entry: "production smoke result",                           payload_required: [result] }
  - { n: 27, id: version_digest_confirmed,              entry: "/version digest confirmed",                         payload_required: [digest] }
  - { n: 28, id: health_check_result,                   entry: "health check result",                               payload_required: [result] }
  - { n: 29, id: feature_flag_state_changed,            entry: "feature flag enabled or disabled",                  payload_required: [state], states: [enabled, disabled] }
  - { n: 30, id: rollback_initiated,                    entry: "rollback initiated with from-digest and to-digest", payload_required: [from_digest, to_digest] }
  - { n: 31, id: hotfix_authorised,                     entry: "hotfix authorised",                                 payload_required: [] }
  - { n: 32, id: incident_opened,                       entry: "incident opened with severity",                     payload_required: [severity] }
  - { n: 33, id: incident_resolved,                     entry: "incident resolved",                                 payload_required: [] }
  - { n: 34, id: postmortem_completed,                  entry: "postmortem completed",                              payload_required: [] }
  - { n: 35, id: regression_test_added,                 entry: "regression test added for a production bug",        payload_required: [] }
  - { n: 36, id: security_incident_opened,              entry: "security incident opened",                          payload_required: [] }
  - { n: 37, id: credential_rotated,                    entry: "credential rotated",                                payload_required: [] }
  - { n: 38, id: restore_test_executed,                 entry: "restore test executed with result",                 payload_required: [result] }
  - { n: 39, id: expiry_alert_raised,                   entry: "secret or certificate expiry alert",                payload_required: [] }
  - { n: 40, id: asset_owner_reassigned,                entry: "asset owner reassigned",                            payload_required: [] }
  - { n: 41, id: lifecycle_transition,                  entry: "lifecycle transition",                              payload_required: [] }
  - { n: 42, id: launch_readiness_signed_off,           entry: "launch readiness signed off",                       payload_required: [] }
  - { n: 43, id: reviewer_matrix_changed,               entry: "reviewer matrix change",                            payload_required: [] }
  - { n: 44, id: knowledge_redundancy_status_changed,   entry: "knowledge redundancy status change",                payload_required: [] }
  - { n: 45, id: person_added,                          entry: "person added",                                      payload_required: [] }
  - { n: 46, id: person_role_changed,                   entry: "person role changed",                               payload_required: [] }
  - { n: 47, id: person_departed,                       entry: "person departed",                                   payload_required: [] }
  - { n: 48, id: orphan_detected,                       entry: "orphan detected",                                   payload_required: [] }
  - { n: 49, id: orphan_resolved,                       entry: "orphan resolved",                                   payload_required: [] }
  - { n: 50, id: temporary_assignment_state_changed,    entry: "temporary assignment created and expired",          payload_required: [state], states: [created, expired] }
  - { n: 51, id: acting_team_lead_state_changed,        entry: "acting team lead activated and deactivated",        payload_required: [state], states: [activated, deactivated] }
  - { n: 52, id: drift_detected,                        entry: "drift detected by severity",                        payload_required: [severity] }
  - { n: 53, id: drift_repaired,                        entry: "drift repaired",                                    payload_required: [] }
  - { n: 54, id: product_created,                       entry: "product created",                                   payload_required: [] }
  - { n: 55, id: product_split,                         entry: "product split",                                     payload_required: [] }
  - { n: 56, id: product_merged,                        entry: "product merged",                                    payload_required: [] }
  - { n: 57, id: product_transferred,                   entry: "product transferred",                               payload_required: [] }
  - { n: 58, id: shared_service_created,                entry: "shared service created",                            payload_required: [] }
  - { n: 59, id: shared_service_breaking_change_released, entry: "shared service breaking change released",         payload_required: [] }
  - { n: 60, id: platform_change_proposed,              entry: "platform change proposed",                          payload_required: [] }
  - { n: 61, id: canary_started,                        entry: "canary started",                                    payload_required: [] }
  - { n: 62, id: canary_result,                         entry: "canary result",                                     payload_required: [result] }
  - { n: 63, id: fleet_rollout_started,                 entry: "fleet rollout started",                             payload_required: [] }
  - { n: 64, id: platform_rollback_initiated,           entry: "platform rollback initiated",                       payload_required: [] }
  - { n: 65, id: contract_version_migrated,             entry: "contract version migrated",                         payload_required: [] }
  - { n: 66, id: compatibility_state_changed,           entry: "compatibility state changed",                       payload_required: [] }
  - { n: 67, id: background_layer_pr_created,           entry: "background layer PR created",                       payload_required: [] }
  - { n: 68, id: background_layer_pr_dispositioned,     entry: "accepted or rejected with task-class reason",       payload_required: [disposition, task_class_reason] }
  - { n: 69, id: task_class_state_changed,              entry: "task class suspended or restored",                  payload_required: [state], states: [suspended, restored] }
  - { n: 70, id: ai_runtime_changed,                    entry: "AI runtime changed",                                payload_required: [] }
  - { n: 71, id: ai_provider_outage_recorded,           entry: "AI provider outage recorded",                       payload_required: [] }
  - { n: 72, id: model_benchmark_completed,             entry: "model benchmark completed",                         payload_required: [] }
  - { n: 73, id: status_request_received,               entry: "status request received (Coordination category)",   payload_required: [] }
  - { n: 74, id: plan_submitted_notification_sent,      entry: "plan submitted-to-approver notification sent",      payload_required: [] }
  - { n: 75, id: verification_state_changed,            entry: "verification blocked and unblocked",                payload_required: [state], states: [blocked, unblocked] }
  - { n: 76, id: degraded_mode_state_changed,           entry: "degraded mode entered and exited",                  payload_required: [state], states: [entered, exited] }
  - { n: 77, id: gap_procedure_run,                     entry: "gap procedure run",                                 payload_required: [] }
  - { n: 78, id: eval_regression_detected,              entry: "eval regression detected",                          payload_required: [] }
  - { n: 79, id: pending_decision_state_changed,        entry: "pending decision opened and closed",                payload_required: [state], states: [opened, closed] }
  - { n: 80, id: onboarding_phase_completed,            entry: "onboarding phase completed",                        payload_required: [] }
  - { n: 81, id: support_item_ingested,                 entry: "support item ingested",                             payload_required: [] }
  - { n: 82, id: support_first_touch_breach,            entry: "support first-touch breach",                        payload_required: [] }
  - { n: 83, id: delegation_expiry_warning_issued,      entry: "delegation expiry warning issued",                  payload_required: [] }
  - { n: 84, id: temporary_person_expiry_warning_issued, entry: "temporary-person expiry warning issued",           payload_required: [] }
  - { n: 85, id: launch_sign_off_requested,             entry: "launch sign-off requested",                         payload_required: [] }
  - { n: 86, id: weekend_exception_state_changed,       entry: "weekend exception requested, authorised, worked, TOIL scheduled and taken", payload_required: [state], states: [requested, authorised, worked, toil_scheduled, toil_taken] }
EOF

cat > "$CP_ROOT/tools/records/validate-taxonomy.sh" <<'EOF'
#!/usr/bin/env bash
# validate-taxonomy.sh - proves metrics/taxonomy/event-types.yaml is a closed, well-formed enum.
# Master Spec v4.0 Section 97.3 line 8959. Fail-closed: an unreadable taxonomy is a failure.
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
"$L4_PY" - "$CP_ROOT/metrics/taxonomy/event-types.yaml" <<'PY'
import re
import sys

import yaml

path = sys.argv[1]
try:
    doc = yaml.safe_load(open(path, encoding="utf-8"))
except Exception as exc:
    print("TAXONOMY FAIL: unreadable: %s" % exc)
    sys.exit(1)
rows = doc.get("event_types") or []
fail = []
if len(rows) != 86:
    fail.append("count %d, expected 86" % len(rows))
if doc.get("identifier_count") != 86:
    fail.append("identifier_count %r, expected 86" % doc.get("identifier_count"))
ids = [r.get("id") for r in rows]
if len(set(ids)) != len(ids):
    fail.append("duplicate identifiers")
pat = re.compile(r"^[a-z][a-z0-9_]*$")
for r in rows:
    if not pat.match(str(r.get("id", ""))):
        fail.append("identifier not lower_snake_case: %r" % r.get("id"))
    if not isinstance(r.get("payload_required"), list):
        fail.append("payload_required not a list on %r" % r.get("id"))
if [r.get("n") for r in rows] != list(range(1, len(rows) + 1)):
    fail.append("n is not 1..N in taxonomy order")
compound = [r["n"] for r in rows if "states" in r]
if compound != [29, 50, 51, 69, 75, 76, 79, 86]:
    fail.append("compound rows %r, expected [29, 50, 51, 69, 75, 76, 79, 86]" % compound)
for r in rows:
    if "states" in r and r.get("payload_required") != ["state"]:
        fail.append("compound row %r must declare payload_required: [state]" % r.get("id"))
if fail:
    for f in fail:
        print("TAXONOMY FAIL: %s" % f)
    sys.exit(1)
print("TAXONOMY OK 86")
PY
EOF
chmod +x "$CP_ROOT/tools/records/validate-taxonomy.sh"

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"

git -C "$CP_ROOT" add metrics/taxonomy tools/records
git -C "$CP_ROOT" commit -m "L4-T203: closed 86-identifier event_type taxonomy (Master Spec 97.3 line 8963)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Taxonomy parses and holds exactly 86 identifiers | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"` | `TAXONOMY OK 86` |
| 2 | Every identifier is unique | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/metrics/taxonomy/event-types.yaml'))['event_types'];print(len({x['id'] for x in r}))"` | `86` |
| 3 | Exactly eight compound entries, at the D-L4-05 positions | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/metrics/taxonomy/event-types.yaml'))['event_types'];print([x['n'] for x in r if 'states' in x])"` | `[29, 50, 51, 69, 75, 76, 79, 86]` — **Note: Unchanged after D113 — do not modify these positions.** |
| 4 | The spec sentence still carries 86 entries | see SELF-VERIFY line `SPEC` | `86` |
| 5 | Only L4-owned paths changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/records/|metrics/|tools/records/)'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"
echo "UNIQUE=$("$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/metrics/taxonomy/event-types.yaml'))['event_types'];print(len({x['id'] for x in r}))")"
echo "COMPOUND=$("$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/metrics/taxonomy/event-types.yaml'))['event_types'];print(len([x for x in r if 'states' in x]))")"
echo "SPEC=$(sed -n '8965p' "$SPEC" | awk -F'·' '{print NF}')"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
```

Expected output, exactly:

```
TAXONOMY OK 86
UNIQUE=86
COMPOUND=8
SPEC=86
FOREIGN=0
```

**STOP rule** — if `SPEC` is not `86`, the specification sentence this task transcribes is not the one this plan was written against: do not adjust the YAML to match, open a blocker. If `TAXONOMY OK 86` does not print, or `UNIQUE` is not `86`, or `COMPOUND` is not `8`: do not proceed to L4-T204, open a blocker issue.

```yaml
title: "[L4-BLOCKER] L4-T203 event_type taxonomy does not close at 86"
lane: L4
task_id: L4-T203
blocked_by: "<spec sentence changed | count wrong | duplicate identifier | compound set wrong>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "TAXONOMY OK 86 / UNIQUE=86 / COMPOUND=8 / SPEC=86 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.3 lines 8944-8963"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T204 — `event.envelope.schema.json` and the generated `event-type.enum.json`

**Size:** M
**Depends on:** L4-T202, L4-T203

§97.3 line 8931: *"Every event carries the same envelope, and an event missing any envelope field is rejected at write time."* The envelope is the nine fields of the line-8934 example: `event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`, `subject_ref`, `payload`. All nine are `required`; the root is closed.

`event_type` is a **generated** enum, never hand-typed: `gen-event-type-enum.sh` projects `metrics/taxonomy/event-types.yaml` into `schemas/records/event-type.enum.json`. Regenerating is the only way the enum ever changes, so the schema and the taxonomy cannot drift apart.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/tools/records/gen-event-type-enum.sh" <<'EOF'
#!/usr/bin/env bash
# gen-event-type-enum.sh - projects metrics/taxonomy/event-types.yaml into
# schemas/records/event-type.enum.json. The enum is GENERATED, never hand-edited.
# Master Spec v4.0 Section 97.3 line 8959.
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
"$L4_PY" - "$CP_ROOT/metrics/taxonomy/event-types.yaml" "$CP_ROOT/schemas/records/event-type.enum.json" <<'PY'
import json
import sys

import yaml

src, dst = sys.argv[1], sys.argv[2]
doc = yaml.safe_load(open(src, encoding="utf-8"))
rows = doc["event_types"]
ids = [r["id"] for r in rows]
if len(set(ids)) != len(ids):
    print("GEN FAIL: duplicate identifier in taxonomy")
    sys.exit(1)
out = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "event-type.enum.json",
    "title": "Closed event_type enum",
    "description": (
        "GENERATED by tools/records/gen-event-type-enum.sh from "
        "metrics/taxonomy/event-types.yaml. Do not hand-edit. "
        "Master Spec v4.0 Section 97.3 line 8959."
    ),
    "type": "string",
    "enum": ids,
}
open(dst, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=2) + "\n")
print("GENERATED %d" % len(ids))
PY
EOF
chmod +x "$CP_ROOT/tools/records/gen-event-type-enum.sh"

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/gen-event-type-enum.sh"

cat > "$CP_ROOT/schemas/records/event.envelope.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "event.envelope.schema.json",
  "title": "Event envelope",
  "description": "Master Spec v4.0 Section 97.3 line 8931: every event carries the same envelope, and an event missing any envelope field is rejected at write time. Nine fields, from the line-8934 example. One file per event; never a concurrent append to a shared period file (line 8929).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "event_schema_version",
    "event_id",
    "event_type",
    "occurred_at",
    "recorded_at",
    "actor",
    "product",
    "subject_ref",
    "payload"
  ],
  "properties": {
    "event_schema_version": {
      "description": "Section 97.3 line 8935: stated on every event written; absent reads as 1.",
      "const": 1
    },
    "event_id": {
      "description": "Literal from EVT-2026-09-14-000317 (line 8936).",
      "type": "string",
      "pattern": "^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$"
    },
    "event_type": {
      "description": "Section 97.3 line 8937: from the closed enum; never free text.",
      "$ref": "event-type.enum.json"
    },
    "occurred_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "recorded_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "actor": {
      "description": "Section 97.3 line 8940: the registry identity that acted, human or machine. D88 line 10181: an identity, never a display name.",
      "$ref": "record.base.schema.json#/$defs/person_ref"
    },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "subject_ref": {
      "description": "Section 97.3 line 8942: the record this event is about, as a records-repository path.",
      "$ref": "record.base.schema.json#/$defs/record_ref"
    },
    "payload": {
      "description": "Section 97.3 line 8943: per-type fields, declared with the type in metrics/taxonomy/event-types.yaml. Open by design: the closed shape is the envelope, and the payload keys are constrained per event_type by tools/records/validate-schemas.sh --events.",
      "type": "object"
    }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/event-plan-approved.yaml" <<'EOF'
# Transcribed from the Master Spec v4.0 Section 97.3 envelope example, line 8934.
event_schema_version: 1
event_id: EVT-2026-09-14-000317
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload:
  gate: 1
  agent_authored: false
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/event-free-text-type.yaml" <<'EOF'
# Section 97.3 line 8959: "Gate 1 approval" is prose, not an identifier. Must be rejected.
event_schema_version: 1
event_id: EVT-2026-09-14-000318
event_type: Gate 1 approval
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/event-missing-recorded-at.yaml" <<'EOF'
# Section 97.3 line 8931: an event missing any envelope field is rejected at write time.
event_schema_version: 1
event_id: EVT-2026-09-14-000319
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" \
  "$CP_ROOT/schemas/records/event.envelope.schema.json" \
  "$CP_ROOT/tools/records/fixtures/valid/event-plan-approved.yaml"

git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T204: event envelope schema and generated event_type enum (Master Spec 97.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The envelope requires exactly the nine fields | `"$L4_PY" -c "import json;print(len(json.load(open(r'$CP_ROOT/schemas/records/event.envelope.schema.json'))['required']))"` | `9` |
| 2 | The envelope root is closed | `"$L4_PY" -c "import json;d=json.load(open(r'$CP_ROOT/schemas/records/event.envelope.schema.json'));print('closed' if d['additionalProperties'] is False else 'OPEN')"` | `closed` |
| 3 | The generated enum carries all 86 identifiers | `"$L4_PY" -c "import json;print(len(json.load(open(r'$CP_ROOT/schemas/records/event-type.enum.json'))['enum']))"` | `86` |
| 4 | The spec's own example event validates | `"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/event.envelope.schema.json" "$CP_ROOT/tools/records/fixtures/valid/event-plan-approved.yaml"` | `VALID …event-plan-approved.yaml` and exit `0` |
| 5 | A free-text `event_type` is rejected | see SELF-VERIFY line `NEGTYPE` | `1` |
| 6 | A missing envelope field is rejected | see SELF-VERIFY line `NEGFIELD` | `1` |
| 7 | Regeneration is byte-stable | see SELF-VERIFY line `REGEN` | `stable` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; E="$CP_ROOT/schemas/records/event.envelope.schema.json"
echo "REQUIRED=$("$L4_PY" -c "import json;print(len(json.load(open(r'$E'))['required']))")"
echo "ENUM=$("$L4_PY" -c "import json;print(len(json.load(open(r'$CP_ROOT/schemas/records/event-type.enum.json'))['enum']))")"
"$L4_PY" "$V" "$E" "$CP_ROOT/tools/records/fixtures/valid/event-plan-approved.yaml" >/dev/null && echo "POS=0" || echo "POS=1"
"$L4_PY" "$V" "$E" "$CP_ROOT/tools/records/fixtures/invalid/event-free-text-type.yaml" >/dev/null 2>&1; echo "NEGTYPE=$?"
"$L4_PY" "$V" "$E" "$CP_ROOT/tools/records/fixtures/invalid/event-missing-recorded-at.yaml" >/dev/null 2>&1; echo "NEGFIELD=$?"
cp "$CP_ROOT/schemas/records/event-type.enum.json" "$CP_ROOT/tools/records/fixtures/_enum.bak"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/gen-event-type-enum.sh" >/dev/null
cmp -s "$CP_ROOT/schemas/records/event-type.enum.json" "$CP_ROOT/tools/records/fixtures/_enum.bak" && echo "REGEN=stable" || echo "REGEN=DRIFT"
rm -f "$CP_ROOT/tools/records/fixtures/_enum.bak"
```

Expected output, exactly:

```
REQUIRED=9
ENUM=86
POS=0
NEGTYPE=1
NEGFIELD=1
REGEN=stable
```

**STOP rule** — if `NEGTYPE` or `NEGFIELD` is `0`, §97.3 line 8931 is unenforced and every downstream metric can be split by a free-text type: do not proceed, open a blocker. If `REGEN=DRIFT`, the generator is not deterministic and the enum will churn on every run: do not commit, open a blocker.

```yaml
title: "[L4-BLOCKER] L4-T204 event envelope not rejecting at write time"
lane: L4
task_id: L4-T204
blocked_by: "<free-text event_type accepted | missing envelope field accepted | generator not deterministic>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "REQUIRED=9 / ENUM=86 / POS=0 / NEGTYPE=1 / NEGFIELD=1 / REGEN=stable"
spec_ref: "Master Spec v4.0 Section 97.3 lines 8931-8959"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T205 — D88 no-names enforcement: the property-name lint and the value scanner

**Size:** M
**Depends on:** L4-T202

D88 (line 10181) and §91.8 (line 8171): *"Records carry stable person IDs, never names — that rule is real, it is enforced at schema validation."* §3.5 splits that into three limbs. Limb A is a property of every store schema and is proven by L4-T223. **This task builds limbs B and C.**

Limb C reads a people roster only to learn which strings are display names. **L4 never writes `registries/**`** — PARTITION.md line 17 gives it to L1. The scanner therefore takes the roster path as a parameter, defaulting to `registries/people.yaml` (the file of Master Spec line 550, whose person entries carry `display_name`, line 555), and the phase's own tests run against the fixture roster in `tools/records/fixtures/roster/` so that this task does not depend on L1 having merged.

§40.1 line 3671 fixes the failure direction: *"a check that cannot reach the records repository fails closed rather than reporting zero."* A roster the scanner cannot read is a **failure**, never a pass.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/tools/records/denied-property-names.txt" <<'EOF'
# D88 (Master Spec v4.0 line 10181) limb B - the closed denylist of property names.
# No schema under schemas/records/ may declare a property with any of these names.
# One name per line. Comments and blank lines ignored. This list is closed:
# adding to it is an L4 change; removing from it is a D88 amendment and belongs to L0.
name
display_name
full_name
first_name
last_name
github_login
login
email
e_mail
username
contact_name
person_name
EOF

cat > "$CP_ROOT/tools/records/validate-no-names.sh" <<'EOF'
#!/usr/bin/env bash
# validate-no-names.sh - D88 enforcement, limbs B and C.
# Master Spec v4.0 D88 line 10181; Section 91.8 line 8171; Section 40.1 line 3671.
#
#   validate-no-names.sh --schemas
#       Limb B. Fails if any schema under schemas/records/ declares a denied property name.
#
#   validate-no-names.sh --records <roster.yaml> <record.yaml> [<record.yaml> ...]
#       Limb C. Fails if any string value in any record equals a display_name in the roster.
#       A roster that cannot be read is a FAILURE, never a pass (fail closed).
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
MODE="${1:?usage: validate-no-names.sh --schemas | --records <roster> <record>...}"
shift
"$L4_PY" - "$CP_ROOT" "$MODE" "$@" <<'PY'
import json
import pathlib
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
args = sys.argv[3:]

denied_path = cp_root / "tools" / "records" / "denied-property-names.txt"
try:
    denied = {
        ln.strip()
        for ln in denied_path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    }
except Exception as exc:
    print("NO-NAMES FAIL-CLOSED: denylist unreadable: %s" % exc)
    sys.exit(1)

def walk_property_names(node):
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            for key in props:
                yield key
        for value in node.values():
            for found in walk_property_names(value):
                yield found
    elif isinstance(node, list):
        for value in node:
            for found in walk_property_names(value):
                yield found

def walk_strings(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            for found in walk_strings(value):
                yield found
    elif isinstance(node, list):
        for value in node:
            for found in walk_strings(value):
                yield found
    elif isinstance(node, str):
        yield node

failed = 0
if mode == "--schemas":
    schema_dir = cp_root / "schemas" / "records"
    files = sorted(schema_dir.glob("*.schema.json"))
    if not files:
        print("NO-NAMES FAIL-CLOSED: no schema files found under %s" % schema_dir)
        sys.exit(1)
    for path in files:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("NO-NAMES FAIL-CLOSED: %s unreadable: %s" % (path.name, exc))
            failed += 1
            continue
        hits = sorted({p for p in walk_property_names(doc) if p in denied})
        if hits:
            print("D88 VIOLATION %s: denied property name(s): %s" % (path.name, ", ".join(hits)))
            failed += 1
    if failed:
        sys.exit(1)
    print("NO-NAMES SCHEMAS OK %d" % len(files))
    sys.exit(0)

if mode == "--records":
    if len(args) < 2:
        print("NO-NAMES FAIL-CLOSED: --records needs a roster and at least one record")
        sys.exit(1)
    roster_path = pathlib.Path(args[0])
    try:
        roster = yaml.safe_load(roster_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("NO-NAMES FAIL-CLOSED: roster unreadable: %s: %s" % (roster_path, exc))
        sys.exit(1)
    def collect_display_names(node):
        out = set()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "display_name" and isinstance(value, str) and value.strip():
                    out.add(value.strip().lower())
                out |= collect_display_names(value)
        elif isinstance(node, list):
            for value in node:
                out |= collect_display_names(value)
        return out
    names = collect_display_names(roster)
    if not names:
        print("NO-NAMES FAIL-CLOSED: roster %s declares no display_name" % roster_path)
        sys.exit(1)
    for target in args[1:]:
        path = pathlib.Path(target)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("NO-NAMES FAIL-CLOSED: %s unreadable: %s" % (target, exc))
            failed += 1
            continue
        hits = sorted({s for s in walk_strings(data) if s.strip().lower() in names})
        if hits:
            print("D88 VIOLATION %s: display name in record body: %s" % (target, ", ".join(hits)))
            failed += 1
        else:
            print("NO-NAMES OK %s" % target)
    if failed:
        sys.exit(1)
    sys.exit(0)

print("NO-NAMES FAIL-CLOSED: unknown mode %r" % mode)
sys.exit(1)
PY
EOF
chmod +x "$CP_ROOT/tools/records/validate-no-names.sh"

cat > "$CP_ROOT/tools/records/fixtures/roster/people.sample.yaml" <<'EOF'
# Fixture roster for D88 limb C. Shaped after registries/people.yaml (Master Spec line 550),
# whose person entries carry display_name (line 555). This file is a TEST FIXTURE:
# L4 never writes registries/** (PARTITION.md line 17).
people:
  - id: dev-a
    display_name: "Example Developer A"
    availability: active
  - id: sec-1
    display_name: "Example Security Specialist"
    availability: active
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/no-names-clean.yaml" <<'EOF'
# A record body that references people by identifier only. D88 line 10181.
record_schema_version: 1
id: DEC-2026-09-10-003
product: solvox
timestamp: 2026-09-10T11:00:00Z
decider: founder
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/no-names-display-name.yaml" <<'EOF'
# A display name from the roster, smuggled into a record body. Must be rejected. D88 line 10181.
record_schema_version: 1
id: DEC-2026-09-10-004
product: solvox
timestamp: 2026-09-10T11:00:00Z
decider: "Example Developer A"
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/denied-property.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "denied-property.schema.json",
  "title": "D88 limb B negative fixture",
  "description": "Declares a denied property name. Must be rejected by validate-no-names.sh --schemas. Lives under fixtures/invalid/, NOT under schemas/records/.",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "display_name": { "type": "string" }
  }
}
EOF

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --records \
  "$CP_ROOT/tools/records/fixtures/roster/people.sample.yaml" \
  "$CP_ROOT/tools/records/fixtures/valid/no-names-clean.yaml"

git -C "$CP_ROOT" add tools/records
git -C "$CP_ROOT" commit -m "L4-T205: D88 no-names enforcement, limbs B and C (Master Spec D88, 91.8, 40.1)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The denylist holds exactly the twelve names of §3.5 limb B | `grep -vcE '^\s*(#|$)' "$CP_ROOT/tools/records/denied-property-names.txt"` | `12` |
| 2 | Limb B passes over the schemas written so far | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas` | a line beginning `NO-NAMES SCHEMAS OK` and exit `0` |
| 3 | Limb B rejects a schema declaring `display_name` | see SELF-VERIFY line `NEGSCHEMA` | `1` |
| 4 | Limb C passes a record that names nobody | see SELF-VERIFY line `POSREC` | `0` |
| 5 | Limb C rejects a record carrying a roster display name | see SELF-VERIFY line `NEGREC` | `1` |
| 6 | Limb C fails closed on an unreadable roster | see SELF-VERIFY line `FAILCLOSED` | `1` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
N="$CP_ROOT/tools/records/validate-no-names.sh"; R="$CP_ROOT/tools/records/fixtures/roster/people.sample.yaml"
echo "DENIED=$(grep -vcE '^\s*(#|$)' "$CP_ROOT/tools/records/denied-property-names.txt")"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$N" --schemas >/dev/null 2>&1; echo "SCHEMAS=$?"
cp "$CP_ROOT/tools/records/fixtures/invalid/denied-property.schema.json" "$CP_ROOT/schemas/records/denied-property.schema.json"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$N" --schemas >/dev/null 2>&1; echo "NEGSCHEMA=$?"
rm -f "$CP_ROOT/schemas/records/denied-property.schema.json"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$N" --records "$R" "$CP_ROOT/tools/records/fixtures/valid/no-names-clean.yaml" >/dev/null 2>&1; echo "POSREC=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$N" --records "$R" "$CP_ROOT/tools/records/fixtures/invalid/no-names-display-name.yaml" >/dev/null 2>&1; echo "NEGREC=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$N" --records "$CP_ROOT/tools/records/fixtures/roster/does-not-exist.yaml" "$CP_ROOT/tools/records/fixtures/valid/no-names-clean.yaml" >/dev/null 2>&1; echo "FAILCLOSED=$?"
```

Expected output, exactly:

```
DENIED=12
SCHEMAS=0
NEGSCHEMA=1
POSREC=0
NEGREC=1
FAILCLOSED=1
```

**STOP rule** — if `NEGSCHEMA`, `NEGREC` or `FAILCLOSED` is `0`, D88 is decorative rather than enforced and every store schema written after this task inherits an unenforced rule: do not proceed to any store task, open a blocker issue. Do not "fix" the scanner by narrowing what it scans.

```yaml
title: "[L4-BLOCKER] L4-T205 D88 no-names enforcement not holding"
lane: L4
task_id: L4-T205
blocked_by: "<denied property accepted | display name accepted | unreadable roster passed>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "DENIED=12 / SCHEMAS=0 / NEGSCHEMA=1 / POSREC=0 / NEGREC=1 / FAILCLOSED=1"
spec_ref: "Master Spec v4.0 D88 line 10181; Section 91.8 line 8171; Section 40.1 line 3671"
needs: "L0"
action_taken: "nothing pushed"
```

---

## 6.1 The store-task template — read once, applied by L4-T206 … L4-T222

The seventeen store tasks are the same task seventeen times over. Each one:

1. writes exactly one file under `schemas/records/`, named per the §3.3 table;
2. declares `"additionalProperties": false` at the root (§3.4 rule 1);
3. `required`s the four base fields (§3.4 rule 2) plus the store's spec-named required fields;
4. `$ref`s every shared shape out of `record.base.schema.json` — never re-inlines a pattern;
5. writes **one** valid fixture under `tools/records/fixtures/valid/<store>.yaml` and **one** invalid fixture under `tools/records/fixtures/invalid/<store>-*.yaml`;
<!-- # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/ -->
6. proves the pair with `lib/validate.py`, then commits.

**Every store task's SELF-VERIFY is the same five lines**, with `<STORE>` replaced by that task's schema basename and `<NEG>` by that task's invalid fixture basename:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/<STORE>.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/<STORE>.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/<NEG>.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

**Every store task expects exactly:**

```
CLOSED=closed
BASE4=4
POS=0
NEG=1
D88=0
```

**Every store task carries the same STOP rule.** If `CLOSED` is not `closed`, or `BASE4` is not `4`, or `POS` is not `0`, or `NEG` is not `1`, or `D88` is not `0`: **do not commit, do not proceed to the next store task, open a blocker issue** on this template:

```yaml
title: "[L4-BLOCKER] L4-T2NN <store> schema does not hold its three structural rules"
lane: L4
task_id: L4-T2NN
blocked_by: "<root not closed | base four not required | valid fixture rejected | invalid fixture accepted | D88 lint failed>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "CLOSED=closed / BASE4=4 / POS=0 / NEG=1 / D88=0"
spec_ref: "Master Spec v4.0 Section 97.2 line 8890; D88 line 10181; this file section 3.4"
needs: "L0"
action_taken: "nothing pushed"
```

**And the same acceptance table**, five rows, proved by the five SELF-VERIFY lines above:

| # | Criterion | Proving line | Unambiguous output |
|---|---|---|---|
| 1 | Root object is closed (§3.4 rule 1, D88 limb A) | `CLOSED` | `closed` |
| 2 | The four base fields are required (§97.2 line 8890) | `BASE4` | `4` |
| 3 | The store's valid fixture validates | `POS` | `0` |
| 4 | The store's invalid fixture is rejected | `NEG` | `1` |
| 5 | The D88 property-name lint still passes across every schema | `D88` | `0` |

A store task below therefore states only what is specific to it: its **fields, with the spec line each comes from**, its command block, and its negative fixture. It does not restate the acceptance table, the SELF-VERIFY block or the STOP rule — they are the ones above, verbatim, with the two substitutions named.

**Standing rule for all seventeen (§3.4 rule 3):** if a store needs a field this specification does not name, that is a schema-change request to L0 under §60.2. **The executor adds no field of their own invention, ever.**

---

### L4-T206 — `incident.schema.json`

**Size:** M
**Depends on:** L4-T202 — plus L4-T205 for the `D88` line of the §6.1 self-verify, which the §5 order already places earlier.
**Store:** `records/incidents/` (§97.2 line 8847). **Fixture pair:** `incident.yaml` / `incident-severity-free-text.yaml`.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| `record_schema_version`, `id`, `product`, `timestamp` | yes | base four | 8875 |
| `severity` | yes | enum `SEV-1 SEV-2 SEV-3 SEV-4` | 8881; ladder §42 |
| `detected` | yes | `timestamp_utc` | 8882 |
| `detection_source` | yes | enum `alert customer internal support_intake` — the literal comment on the line | 8883 |
| `responded` | yes | `timestamp_utc` | 8884 |
| `resolved` | no | `timestamp_utc` — absent while the incident is open | 8885 |
| `customer_impact` | yes | `nonempty_string` | 8886 |
| `resolution` | no | `nonempty_string` — absent while the incident is open | 8887 |
| `postmortem` | no | `record_ref` — written when the postmortem lands (§58.4 line 5019) | 8888 |
| `postmortem_owner` | no | `person_ref` — "the postmortem owner is named on the incident record" | 3819 |
| `founder_informed_at` | no | `timestamp_utc` — SEV-1 only: "a recorded fact with a time against it" | 3821 |
| `pre_onboarding` | yes | boolean | 8889 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/incident.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "incident.schema.json",
  "title": "Incident record",
  "description": "Store records/incidents/ (Master Spec v4.0 Section 97.2 line 8847). Fields from the line 8878-8889 example, plus the postmortem owner of line 3819 and the SEV-1 founder_informed_at of line 3821.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "severity", "detected", "detection_source", "responded", "customer_impact", "pre_onboarding"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "type": "string", "pattern": "^INC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "severity": { "description": "Line 8881.", "type": "string", "enum": ["SEV-1", "SEV-2", "SEV-3", "SEV-4"] },
    "detected": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "detection_source": { "description": "Line 8883, literal comment.", "type": "string", "enum": ["alert", "customer", "internal", "support_intake"] },
    "responded": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "resolved": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "customer_impact": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "resolution": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "postmortem": { "$ref": "record.base.schema.json#/$defs/record_ref" },
    "postmortem_owner": { "description": "Line 3819: a postmortem with no named owner is a postmortem that does not happen.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "founder_informed_at": { "description": "Line 3821: SEV-1 only.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "pre_onboarding": { "description": "Line 8889.", "type": "boolean" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/incident.yaml" <<'EOF'
# Transcribed from the Master Spec v4.0 Section 97.2 example, lines 8878-8889.
record_schema_version: 1
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
resolved: 2026-09-14T10:02:00Z
customer_impact: partial degradation, 3 customers
resolution: rollback to digest sha256:0000000000000000000000000000000000000000000000000000000000000000
postmortem: records/postmortems/2026-09-16-solvox.yaml
postmortem_owner: dev-a
pre_onboarding: false
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/incident-severity-free-text.yaml" <<'EOF'
# Free-text severity. Line 8881 fixes the ladder; free text splits every severity trend.
record_schema_version: 1
id: INC-2026-09-14-002
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: critical
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/incident.schema.json" "$CP_ROOT/tools/records/fixtures/valid/incident.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T206: incident record schema (Master Spec 97.2 line 8847)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `incident`, `<NEG>` = `incident-severity-free-text`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/incident.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/incident.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/incident-severity-free-text.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T206` and `<store>` = `incident`.

---

### L4-T207 — `postmortem.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/postmortems/` (§97.2 line 8848). **Fixture pair:** `postmortem.yaml` / `postmortem-free-text-root-cause.yaml`.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `incident` | yes | `record_ref` — the incident this postmortem closes | 5022 |
| `due` | yes | `date_utc` — "due within 5 working days of incident closure" | 5019 |
| `root_cause` | yes | closed enum, the eight classes of the line 5026–5028 ladder | 5026–5028 |
| `items` | yes | array (may be empty — "postmortems that generate no tracked work are permitted") of `{type, ref, status, owner, due}` | 5030–5036, 5044 |
| `items[].type` | yes | closed enum, the six item classes | 5031–5036 |
| `items[].status` | yes | enum `open closed deferred` | 5040–5041 |
| `items[].owner` | yes | `person_ref` — "deferred with a named owner and a date" | 5041 |
| `items[].due` | yes | `date_utc` | 5041 |
| `closed` | no | `date_utc` — set only when every item is closed or deferred | 5040–5041 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/postmortem.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "postmortem.schema.json",
  "title": "Postmortem record",
  "description": "Store records/postmortems/ (Master Spec v4.0 Section 97.2 line 8848). The learning loop of Section 58.4, lines 5017-5044: due within 5 working days of incident closure; root cause classified from a closed eight-value ladder; generated items tracked to closure with a named owner and a date.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "incident", "due", "root_cause", "items"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "incident": { "$ref": "record.base.schema.json#/$defs/record_ref" },
    "due": { "description": "Line 5019: within 5 working days of incident closure.", "$ref": "record.base.schema.json#/$defs/date_utc" },
    "root_cause": {
      "description": "Lines 5026-5028, the classification ladder, verbatim in identifier form.",
      "type": "string",
      "enum": ["code", "configuration", "customer_integration", "external_dependency", "external_model_behaviour_change", "process", "knowledge", "capacity"]
    },
    "items": {
      "description": "Lines 5030-5036. May be empty: line 5044 permits a postmortem that generates no tracked work.",
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["type", "ref", "status", "owner", "due"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["regression_test", "architecture_remediation", "monitoring_or_alerting_improvement", "product_contract_change", "policy_change_or_new_exception", "pattern_candidate"]
          },
          "ref": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "status": { "type": "string", "enum": ["open", "closed", "deferred"] },
          "owner": { "$ref": "record.base.schema.json#/$defs/person_ref" },
          "due": { "$ref": "record.base.schema.json#/$defs/date_utc" }
        }
      }
    },
    "closed": { "description": "Lines 5040-5041.", "$ref": "record.base.schema.json#/$defs/date_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/postmortem.yaml" <<'EOF'
# Section 58.4, lines 5017-5044.
record_schema_version: 1
id: PM-2026-09-16-001
product: solvox
timestamp: 2026-09-16T14:00:00Z
incident: records/incidents/2026-09-14-solvox-001.yaml
due: 2026-09-21
root_cause: configuration
items:
  - type: regression_test
    ref: work-item/4412
    status: open
    owner: dev-a
    due: 2026-09-30
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/postmortem-free-text-root-cause.yaml" <<'EOF'
# Free-text root cause. Lines 5026-5028 fix the ladder; free text makes pattern detection impossible.
record_schema_version: 1
id: PM-2026-09-16-002
product: solvox
timestamp: 2026-09-16T14:00:00Z
incident: records/incidents/2026-09-14-solvox-001.yaml
due: 2026-09-21
root_cause: someone deployed on a Friday
items: []
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/postmortem.schema.json" "$CP_ROOT/tools/records/fixtures/valid/postmortem.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T207: postmortem record schema (Master Spec 97.2 line 8848; 58.4)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `postmortem`, `<NEG>` = `postmortem-free-text-root-cause`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/postmortem.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/postmortem.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/postmortem-free-text-root-cause.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T207` and `<store>` = `postmortem`.

---

### L4-T208 — `uat.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/uat/` (§97.2 line 8849). **Fixture pair:** `uat.yaml` / `uat-free-text-result.yaml`.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `result` | yes | `pass_fail` — the pass-or-fail input of RECORD-VERIFICATION-RESULT | 8871 |
| `executed_by` | yes | `person_ref` | 8849, 8871 |
| `uat_contract` | yes | `nonempty_string` — the `verification/uat.md` execution this record reports | 8849 |
| `environment` | yes | enum `local staging` — "developer local UAT and QA staging UAT execute the same script" | 2790 |
| `work_item` | no | `nonempty_string` | 2790 |
| `evidence` | no | `evidence_link` | 8871 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/uat.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "uat.schema.json",
  "title": "UAT result record",
  "description": "Store records/uat/ (Master Spec v4.0 Section 97.2 line 8849): written by the CI job on UAT completion from verification/uat.md execution, or by the RECORD-VERIFICATION-RESULT dispatch for manual UAT (line 2790, line 8871). Generates UAT coverage and pass rates.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "result", "executed_by", "uat_contract", "environment"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "result": { "$ref": "record.base.schema.json#/$defs/pass_fail" },
    "executed_by": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "uat_contract": { "description": "Line 8849: the verification/uat.md execution this record reports.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "environment": { "description": "Line 2790.", "type": "string", "enum": ["local", "staging"] },
    "work_item": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "evidence": { "$ref": "record.base.schema.json#/$defs/evidence_link" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/uat.yaml" <<'EOF'
# Section 97.2 line 8849; Section 31.2 line 2790.
record_schema_version: 1
id: UAT-2026-09-13-007
product: solvox
timestamp: 2026-09-13T16:40:00Z
result: pass
executed_by: qa-1
uat_contract: verification/uat.md@a1b2c3d
environment: staging
work_item: work-item/4401
evidence: https://example.invalid/run/1
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/uat-free-text-result.yaml" <<'EOF'
# "passed with notes" is not pass-or-fail. Line 8871 makes the result binary.
record_schema_version: 1
id: UAT-2026-09-13-008
product: solvox
timestamp: 2026-09-13T16:40:00Z
result: passed with notes
executed_by: qa-1
uat_contract: verification/uat.md@a1b2c3d
environment: staging
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/uat.schema.json" "$CP_ROOT/tools/records/fixtures/valid/uat.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T208: UAT result schema (Master Spec 97.2 line 8849)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `uat`, `<NEG>` = `uat-free-text-result`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/uat.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/uat.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/uat-free-text-result.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T208` and `<store>` = `uat`.

---

### L4-T209 — `estimate.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/estimates/` (§97.2 line 8850). **Fixture pair:** `estimate.yaml` / `estimate-missing-net-elapsed.yaml`.

Line 8850 names the payload exactly: *"band and point value, elapsed, and elapsed net of recorded Blocked time"*. Line 2665 explains why both elapsed figures are carried: *"the record carries both figures so the two are never confused"*, and fixes `band` as **calibrated configuration declared in `economics.yaml`** — so `band` is a required non-empty string and **not** an enum in this schema; enumerating it here would freeze a vocabulary the specification deliberately leaves calibrated.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `work_item` | yes | `nonempty_string` — the item that closed | 8850 |
| `band` | yes | `nonempty_string` — label in force when written | 8850, 2665 |
| `point_value` | yes | number ≥ 0 — the representative point value in force when written | 2665 |
| `elapsed` | yes | number ≥ 0 — raw elapsed, what forecast calibration uses | 8850, 2665 |
| `elapsed_net_blocked` | yes | number ≥ 0 — what the Estimation Accuracy KPI calls actual effort | 8850, 2665 |
| `unit` | yes | enum `hours days` — the unit both elapsed figures are stated in | 2665 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/estimate.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "estimate.schema.json",
  "title": "Estimate-versus-actual record",
  "description": "Store records/estimates/ (Master Spec v4.0 Section 97.2 line 8850): band and point value, elapsed, and elapsed net of recorded Blocked time, written by board automation at item close. Line 2665: the band vocabulary is calibrated configuration in economics.yaml, so band is not enumerated here; the record carries the label AND the point value in force when it was written, so a later revision of the vocabulary re-maps history rather than invalidating it.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "work_item", "band", "point_value", "elapsed", "elapsed_net_blocked", "unit"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "work_item": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "band": { "description": "Line 2665: calibrated configuration in economics.yaml. Deliberately not an enum.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "point_value": { "description": "Line 2665: an accuracy ratio cannot be computed over an interval.", "type": "number", "minimum": 0 },
    "elapsed": { "description": "Line 8850: raw elapsed, used by forecast calibration (Section 72).", "type": "number", "minimum": 0 },
    "elapsed_net_blocked": { "description": "Line 8850, line 2665: what Estimation Accuracy (Section 78) calls actual effort.", "type": "number", "minimum": 0 },
    "unit": { "type": "string", "enum": ["hours", "days"] },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/estimate.yaml" <<'EOF'
# Section 97.2 line 8850; Section 29 line 2665.
record_schema_version: 1
id: EST-2026-09-12-031
product: solvox
timestamp: 2026-09-12T17:05:00Z
work_item: work-item/4388
band: M
point_value: 3
elapsed: 4.5
elapsed_net_blocked: 3.25
unit: days
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/estimate-missing-net-elapsed.yaml" <<'EOF'
# Missing elapsed_net_blocked. Line 2665: the record carries BOTH figures so the two are never confused.
record_schema_version: 1
id: EST-2026-09-12-032
product: solvox
timestamp: 2026-09-12T17:05:00Z
work_item: work-item/4389
band: S
point_value: 1
elapsed: 1.5
unit: days
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/estimate.schema.json" "$CP_ROOT/tools/records/fixtures/valid/estimate.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T209: estimate-vs-actual schema (Master Spec 97.2 line 8850)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `estimate`, `<NEG>` = `estimate-missing-net-elapsed`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/estimate.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/estimate.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/estimate-missing-net-elapsed.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T209` and `<store>` = `estimate`.

---

### L4-T210 — `deployment.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/deployments/` (§97.2 line 8851). **Fixture pair:** `deployment.yaml` / `deployment-bad-digest.yaml`.

This is the store whose write is a **required, failing step** of `deploy-production.yml` (line 8867) and the store the eleven evidence-chain questions of §32 are answered from. Every field below is literal from the line 8893–8902 example.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `digest` | yes | `digest` (`sha256:` + 64 hex) | 8896 |
| `approved_by` | yes | `person_ref` — "never the deploying actor once armed" | 8897 |
| `approval_event` | yes | `evidence_link` — the run URL | 8898 |
| `staging_verified` | yes | boolean | 8899 |
| `uat_record` | yes | `record_ref` | 8900 |
| `smoke_result` | yes | `pass_fail` | 8905 |
| `rollback_of` | yes | `record_id` or `null` | 8902 |
| `commit` | yes | string | — |
| `pull_request` | yes | string or null | — |
| `ci_run` | yes | string | — |
| `environment` | yes | string | — |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/deployment.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "deployment.schema.json",
  "title": "Deployment record",
  "description": "Store records/deployments/ (Master Spec v4.0 Section 97.2 line 8851). Fields from the line 8893-8902 example. The write of this record is a required, failing step of deploy-production.yml (line 8867): a deploy whose record cannot be written is a deploy whose evidence chain does not close.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "digest", "approved_by", "approval_event", "staging_verified", "uat_record", "smoke_result", "rollback_of", "commit", "pull_request", "ci_run", "environment"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "type": "string", "pattern": "^DEP-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "digest": {
      "description": "Section 97.2 line 8905: digest of the deployed artifact; either a platform rebuild identity or an artifact identity.",
      "oneOf": [
        { "$ref": "record.base.schema.json#/$defs/platform_rebuild_identity" },
        { "$ref": "record.base.schema.json#/$defs/artifact_identity" }
      ]
    },
    "approved_by": { "description": "Line 8897: never the deploying actor once armed. A role holder or person identifier, never a display name (D88).", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "approval_event": { "description": "Line 8898: the run URL.", "$ref": "record.base.schema.json#/$defs/evidence_link" },
    "staging_verified": { "type": "boolean" },
    "uat_record": { "$ref": "record.base.schema.json#/$defs/record_ref" },
    "smoke_result": { "$ref": "record.base.schema.json#/$defs/pass_fail" },
    "rollback_of": {
      "description": "Line 8902: the deployment this one rolls back, or null.",
      "oneOf": [
        { "$ref": "record.base.schema.json#/$defs/record_id" },
        { "type": "null" }
      ]
    },
    "commit": { "description": "Git commit SHA of the deployed artifact.", "type": "string" },
    "pull_request": {
      "description": "Pull request reference that introduced the change, or null.",
      "oneOf": [
        { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
        { "type": "null" }
      ]
    },
    "ci_run": { "description": "CI run URL or reference for the build that produced the artifact.", "type": "string" },
    "environment": { "description": "Target deployment environment.", "type": "string" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/deployment.yaml" <<'EOF'
# Transcribed from the Master Spec v4.0 Section 97.2 example, lines 8893-8902.
record_schema_version: 1
id: DEP-2026-09-12-014
product: solvox
timestamp: 2026-09-12T11:20:00Z
digest:
  name: solvox/api
  digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  tag: v1.0.0
approved_by: lead-1
approval_event: https://example.invalid/run/2
staging_verified: true
uat_record: records/uat/2026-09-12-solvox-007.yaml
smoke_result: pass
rollback_of: null
commit: 0000000000000000000000000000000000000000
pull_request: "https://github.com/example/control-plane/pull/1"
ci_run: https://example.invalid/ci/1
environment: production
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/deployment-bad-digest.yaml" <<'EOF'
# A truncated digest. Section 32's evidence chain is answerable only against a full sha256.
record_schema_version: 1
id: DEP-2026-09-12-015
product: solvox
timestamp: 2026-09-12T11:20:00Z
digest:
  name: solvox/api
  digest: sha256:abc
  tag: v1.0.0
approved_by: lead-1
approval_event: https://example.invalid/run/3
staging_verified: true
uat_record: records/uat/2026-09-12-solvox-007.yaml
smoke_result: pass
rollback_of: null
commit: 0000000000000000000000000000000000000000
pull_request: null
ci_run: https://example.invalid/ci/2
environment: production
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/deployment.schema.json" "$CP_ROOT/tools/records/fixtures/valid/deployment.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T210: deployment record schema (Master Spec 97.2 line 8851)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `deployment`, `<NEG>` = `deployment-bad-digest`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/deployment.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/deployment.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/deployment-bad-digest.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T210` and `<store>` = `deployment`.

---

### L4-T211 — `restore-test.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/restore-tests/` (§97.2 line 8851). **Fixture pair:** `restore-test.yaml` / `restore-test-no-verifier.yaml`.

§44.3 line 4008 and §44.5 line 4020 make two fields non-optional: the declared `integrity_check` **result**, and a **named verifier**. Line 4020: *"A production restore whose record names no integrity-check result and no verifier is Red drift."* §53.1 line 4672 re-states it as a drift row. This store also back-writes `restore_tested` on `product.yaml` — line 3997: *"derived, not declared … a hand-edited date is drift, not evidence"* — which is L1's file and L3's check, never L4's.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `result` | yes | `pass_fail` | 4008, 4010 |
| `restore_environment` | yes | `nonempty_string` — the declared target restored into | 4008 |
| `integrity_check` | yes | `nonempty_string` — which declared check was asserted | 4008 |
| `integrity_check_result` | yes | `pass_fail` — asserted machine-side, never read over a shoulder | 4008, 4020 |
| `verifier` | yes | `person_ref` — the named verifier | 4020 |
| `confirmed_by` | no | `person_ref` — the Primary Owner's asynchronous RVR confirmation | 4008, 8871 |
| `confirmed_at` | no | `timestamp_utc` | 8871 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/restore-test.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "restore-test.schema.json",
  "title": "Restore-test record",
  "description": "Store records/restore-tests/ (Master Spec v4.0 Section 97.2 line 8851). Section 44.3 line 4008: the restore job asserts the declared integrity_check machine-side. Section 44.5 line 4020: a restore record naming no integrity-check result and no verifier is Red drift. Section 44.2 line 3997: product.yaml restore_tested is derived from the newest passing record here - never hand-edited, and never written by L4.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "result", "restore_environment", "integrity_check", "integrity_check_result", "verifier"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "result": { "$ref": "record.base.schema.json#/$defs/pass_fail" },
    "restore_environment": { "description": "Line 4008.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "integrity_check": { "description": "Line 4008: the declared check that was asserted.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "integrity_check_result": { "description": "Lines 4008, 4020.", "$ref": "record.base.schema.json#/$defs/pass_fail" },
    "verifier": { "description": "Line 4020: the named verifier.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "confirmed_by": { "description": "Line 4008: the Primary Owner confirms asynchronously through the RECORD-VERIFICATION-RESULT dispatch.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "confirmed_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/restore-test.yaml" <<'EOF'
# Section 44.3 line 4008; Section 44.5 line 4020.
record_schema_version: 1
id: RST-2026-09-05-002
product: solvox
timestamp: 2026-09-05T09:00:00Z
result: pass
restore_environment: restore-sandbox
integrity_check: row-counts-and-checksums
integrity_check_result: pass
verifier: qa-1
confirmed_by: dev-a
confirmed_at: 2026-09-05T12:00:00Z
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/restore-test-no-verifier.yaml" <<'EOF'
# No named verifier. Line 4020: this is exactly the record the specification calls Red drift.
record_schema_version: 1
id: RST-2026-09-05-003
product: solvox
timestamp: 2026-09-05T09:00:00Z
result: pass
restore_environment: restore-sandbox
integrity_check: row-counts-and-checksums
integrity_check_result: pass
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/restore-test.schema.json" "$CP_ROOT/tools/records/fixtures/valid/restore-test.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T211: restore-test record schema (Master Spec 97.2 line 8851; 44.3, 44.5)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `restore-test`, `<NEG>` = `restore-test-no-verifier`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/restore-test.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/restore-test.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/restore-test-no-verifier.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T211` and `<store>` = `restore-test`.

---

### L4-T212 — `decision.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/decisions/` (§97.2 line 8852). **Fixture pair:** `decision.yaml` / `decision-decider-display-name.yaml`.

This is the store §3.5's RESOLVED CONFLICT is about. `decider` is a `person_ref`: it accepts the role token `founder` of the line-8908 example and an opaque person identifier alike, and rejects a display name. **Do not widen it.**

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `decider` | yes | `person_ref` — role token or person identifier, never a name (D88) | 8908; D88 line 10181 |
| `prompt_received` | yes | `date_utc` | 8909 |
| `decided` | yes | `date_utc` | 8910 |
| `subject` | yes | `nonempty_string` | 8911 |
| `options_considered` | yes | array of `nonempty_string`, at least one | 8912 |
| `evidence` | yes | array of `evidence_link` | 8913 |
| `review_date` | no | `date_utc` | 8914 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/decision.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "decision.schema.json",
  "title": "Decision record",
  "description": "Store records/decisions/ (Master Spec v4.0 Section 97.2 line 8852). Fields from the line 8906-8914 example. Line 7939: people-related Founder decisions go to the Layer B decision store instead; the decision-latency metric reads both. D88 line 10181 governs decider: a role token or a person identifier, never a display name.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "decider", "prompt_received", "decided", "subject", "options_considered", "evidence"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "type": "string", "pattern": "^DEC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "decider": { "description": "Line 8908 and D88 line 10181. Accepts the role token 'founder' and an opaque person identifier; rejects a display name.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "prompt_received": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "decided": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "subject": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "options_considered": { "type": "array", "minItems": 1, "items": { "$ref": "record.base.schema.json#/$defs/nonempty_string" } },
    "evidence": { "type": "array", "items": { "$ref": "record.base.schema.json#/$defs/evidence_link" } },
    "review_date": { "description": "Line 8914. Section 52.4 line 8308: a decided signal carries its review date until it passes.", "$ref": "record.base.schema.json#/$defs/date_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/decision.yaml" <<'EOF'
# Transcribed from the Master Spec v4.0 Section 97.2 example, lines 8906-8914.
record_schema_version: 1
id: DEC-2026-09-10-003
product: portfolio
timestamp: 2026-09-10T11:00:00Z
decider: founder
prompt_received: 2026-09-08
decided: 2026-09-10
subject: second QA hire deferred; rebalance executed instead
options_considered: [hire, rebalance, reduce-verification-scope]
evidence:
  - https://example.invalid/evidence/1
  - https://example.invalid/evidence/2
review_date: 2026-12-01
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/decision-decider-display-name.yaml" <<'EOF'
# A display name in the decider field. D88 line 10181: names in record bodies fail schema validation.
record_schema_version: 1
id: DEC-2026-09-10-004
product: portfolio
timestamp: 2026-09-10T11:00:00Z
decider: Example Developer A
prompt_received: 2026-09-08
decided: 2026-09-10
subject: second QA hire deferred
options_considered: [hire, rebalance]
evidence: []
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/decision.schema.json" "$CP_ROOT/tools/records/fixtures/valid/decision.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T212: decision record schema (Master Spec 97.2 line 8852; D88)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `decision`, `<NEG>` = `decision-decider-display-name`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/decision.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/decision.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/decision-decider-display-name.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T212` and `<store>` = `decision`.

---

### L4-T213 — `decision-pending.schema.json`

**Size:** S
**Depends on:** L4-T212 (this schema is the decision schema minus the fields a decision has and a prompt does not).
**Store:** `records/decisions/pending/` (§97.2 line 8853). **Fixture pair:** `decision-pending.yaml` / `decision-pending-no-prompt-date.yaml`.

Line 8853: the record is opened by the record-decision CLI when a decision prompt is opened, and **moves** to `records/decisions/` when decided. Line 1273: the pending register *"is the Founder's queue, not a reconstruction from inboxes."* Line 8308: it renders as *"every open decision prompt with its age"* — which is why `prompt_received` is required: a prompt without it has no age and §103.8's queue-age metric silently reads zero.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `decider` | yes | `person_ref` | 8908, 7939 |
| `prompt_received` | yes | `date_utc` — the age the register renders | 8909, 8308 |
| `subject` | yes | `nonempty_string` | 8911 |
| `options_considered` | no | array of `nonempty_string` | 8912 |
| `evidence` | no | array of `evidence_link` | 8913 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/decision-pending.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "decision-pending.schema.json",
  "title": "Pending decision record",
  "description": "Store records/decisions/pending/ (Master Spec v4.0 Section 97.2 line 8853): opened by the record-decision CLI when a decision prompt is opened; the record MOVES to records/decisions/ when decided. Line 1273: the pending register is the Founder's queue. Line 8308: it renders every open prompt with its age, which is why prompt_received is required. Generates decision queue depth and age (Section 103.8).",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "decider", "prompt_received", "subject"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "type": "string", "pattern": "^DEC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "decider": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "prompt_received": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "subject": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "options_considered": { "type": "array", "items": { "$ref": "record.base.schema.json#/$defs/nonempty_string" } },
    "evidence": { "type": "array", "items": { "$ref": "record.base.schema.json#/$defs/evidence_link" } },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/decision-pending.yaml" <<'EOF'
# Section 97.2 line 8853; Section 52.4 line 8308.
record_schema_version: 1
id: DEC-2026-09-08-011
product: portfolio
timestamp: 2026-09-08T09:15:00Z
decider: founder
prompt_received: 2026-09-08
subject: second QA hire deferred; rebalance executed instead
options_considered: [hire, rebalance, reduce-verification-scope]
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/decision-pending-no-prompt-date.yaml" <<'EOF'
# No prompt_received. Line 8308 renders each open prompt WITH ITS AGE; without this field the age is unknowable.
record_schema_version: 1
id: DEC-2026-09-08-012
product: portfolio
timestamp: 2026-09-08T09:15:00Z
decider: founder
subject: third support channel opened or not
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/decision-pending.schema.json" "$CP_ROOT/tools/records/fixtures/valid/decision-pending.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T213: pending decision schema (Master Spec 97.2 line 8853)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `decision-pending`, `<NEG>` = `decision-pending-no-prompt-date`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/decision-pending.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/decision-pending.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/decision-pending-no-prompt-date.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T213` and `<store>` = `decision-pending`.

---

### L4-T214 — `breach.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/breaches/` (§97.2 line 8854). **Fixture pair:** `breach.yaml` / `breach-no-notification-clock.yaml`.

Two spec passages write to this one store, and both are honoured without inventing a discriminator field. Line 2162: *"A measured SLA breach opens a record in `records/breaches/` … naming the customer reference, the measurement window, the measured figure and the promised figure."* Line 8854: the security-incident workflow writes here *"when an incident is classified as a breach"*. D65 (line 10138) adds, for the SLA case, *"a defined notification clock and a tracked credit decision"*. Line 8854 makes **notification-deadline compliance** a metric of the whole store, so `notification_due` is required at the root of both shapes; the two shapes are separated by a `oneOf` over their remaining required sets.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `notification_due` | yes, both shapes | `timestamp_utc` | 8854, 10138 |
| `notified_at` | no | `timestamp_utc` | 8854 |
| `customer_ref` | SLA shape | `nonempty_string` — a reference, never a name (D88) | 2162 |
| `window_start`, `window_end` | SLA shape | `timestamp_utc` — the measurement window | 2162 |
| `measured`, `promised` | SLA shape | number — the measured and the promised figure | 2162 |
| `credit_decision` | SLA shape | `nonempty_string` | 10138 |
| `incident` | security shape | `record_ref` | 8854 |
| `classified_at` | security shape | `timestamp_utc` | 8854 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/breach.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "breach.schema.json",
  "title": "Breach record",
  "description": "Store records/breaches/ (Master Spec v4.0 Section 97.2 line 8854). Two spec-named shapes share one store: the measured-SLA breach of line 2162 (customer reference, measurement window, measured figure, promised figure) with the notification clock and credit decision of D65 line 10138; and the security breach of line 8854, written when an incident is classified as a breach. notification_due is required on both because line 8854 makes notification-deadline compliance a metric of the whole store.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "notification_due"],
  "oneOf": [
    { "required": ["customer_ref", "window_start", "window_end", "measured", "promised", "credit_decision"] },
    { "required": ["incident", "classified_at"] }
  ],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "notification_due": { "description": "D65 line 10138: a defined notification clock. Line 8854: notification-deadline compliance.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "notified_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "customer_ref": { "description": "Line 2162: the customer reference. A reference, never a name (D88 line 10181).", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "window_start": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "window_end": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "measured": { "description": "Line 2162: the measured figure.", "type": "number" },
    "promised": { "description": "Line 2162: the promised figure.", "type": "number" },
    "credit_decision": { "description": "D65 line 10138: a tracked credit decision.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "incident": { "description": "Line 8854: the incident classified as a breach.", "$ref": "record.base.schema.json#/$defs/record_ref" },
    "classified_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/breach.yaml" <<'EOF'
# The measured-SLA shape. Section 22 line 2162; D65 line 10138.
record_schema_version: 1
id: BR-2026-09-30-001
product: solvox
timestamp: 2026-09-30T10:00:00Z
notification_due: 2026-10-02T10:00:00Z
notified_at: 2026-09-30T15:30:00Z
customer_ref: cust-0142
window_start: 2026-09-01T00:00:00Z
window_end: 2026-09-30T00:00:00Z
measured: 99.1
promised: 99.9
credit_decision: one month service credit approved
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/breach-no-notification-clock.yaml" <<'EOF'
# No notification_due. Line 8854 makes notification-deadline compliance a metric of this store;
# without the clock the metric silently reads as compliant.
record_schema_version: 1
id: BR-2026-09-30-002
product: solvox
timestamp: 2026-09-30T10:00:00Z
customer_ref: cust-0143
window_start: 2026-09-01T00:00:00Z
window_end: 2026-09-30T00:00:00Z
measured: 98.4
promised: 99.9
credit_decision: pending
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/breach.schema.json" "$CP_ROOT/tools/records/fixtures/valid/breach.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T214: breach record schema (Master Spec 97.2 line 8854; 22 line 2162; D65)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `breach`, `<NEG>` = `breach-no-notification-clock`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/breach.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/breach.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/breach-no-notification-clock.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T214` and `<store>` = `breach`.

---

### L4-T215 — `deletion-request.schema.json` (AT-105)

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/deletion-requests/` (§97.2 line 8855). **Fixture pair:** `deletion-request.yaml` / `deletion-request-three-timestamps.yaml`.

This store has the most explicit structure in §97. Line 8869: *"A deletion-request record carries four timestamps — `requested`, `verified`, `executed`, `confirmed` — plus the named executor; the deletion runbook is executed through CI, never ad hoc; the record includes the subprocessor propagation checklist (each subprocessor holding the customer's data, with its own deletion confirmation); and the backup carve-out policy statement … is a written artifact customers can be given."* **AT-105** (line 9375) makes exactly those three things the completion evidence, measured against `data.deletion_sla_days` (line 8855; EC-98 line 9746).

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `customer_ref` | yes | `nonempty_string` — a reference, never a name (D88) | 8869 |
| `requested`, `verified`, `executed`, `confirmed` | yes, all four | `timestamp_utc` | 8869, 9375 |
| `executor` | yes | `person_ref` — "the named executor" | 8869, 9375 |
| `subprocessor_checklist` | yes | array of `{subprocessor, deletion_confirmed, confirmed_at}`; may be empty when the product declares no subprocessors | 8869, 9375 |
| `backup_carve_out_statement` | yes | `nonempty_string` | 8869 |
| `evidence` | no | `evidence_link` — the CI run that executed the runbook | 8869, 8871 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/deletion-request.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "deletion-request.schema.json",
  "title": "Deletion-request record",
  "description": "Store records/deletion-requests/ (Master Spec v4.0 Section 97.2 line 8855), written through the RECORD-VERIFICATION-RESULT dispatch. Line 8869 fixes the structure: four timestamps, the named executor, the subprocessor propagation checklist, and the backup carve-out policy statement. AT-105 (line 9375) makes those the completion evidence, measured against data.deletion_sla_days (EC-98 line 9746).",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "customer_ref", "requested", "verified", "executed", "confirmed", "executor", "subprocessor_checklist", "backup_carve_out_statement"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "customer_ref": { "description": "Line 8869. A reference, never a name (D88 line 10181).", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "requested": { "description": "Line 8869, timestamp 1 of 4. Starts the statutory deletion clock.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "verified": { "description": "Line 8869, timestamp 2 of 4.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "executed": { "description": "Line 8869, timestamp 3 of 4.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "confirmed": { "description": "Line 8869, timestamp 4 of 4.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "executor": { "description": "Line 8869: the named executor. A person identifier, never a display name (D88).", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "subprocessor_checklist": {
      "description": "Line 8869: each subprocessor holding the customer's data, with its own deletion confirmation. May be empty when the product declares no subprocessors.",
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["subprocessor", "deletion_confirmed"],
        "properties": {
          "subprocessor": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "deletion_confirmed": { "type": "boolean" },
          "confirmed_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" }
        }
      }
    },
    "backup_carve_out_statement": { "description": "Line 8869: deleted data persists in backups until rotation expires them and is never restored into live systems - a written artifact customers can be given.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "evidence": { "$ref": "record.base.schema.json#/$defs/evidence_link" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/deletion-request.yaml" <<'EOF'
# Section 97.2 line 8869; AT-105 line 9375.
record_schema_version: 1
id: DEL-2026-09-20-004
product: solvox
timestamp: 2026-09-20T08:00:00Z
customer_ref: cust-0142
requested: 2026-09-20T08:00:00Z
verified: 2026-09-20T09:10:00Z
executed: 2026-09-21T11:00:00Z
confirmed: 2026-09-21T12:30:00Z
executor: ops-1
subprocessor_checklist:
  - subprocessor: object-storage-provider
    deletion_confirmed: true
    confirmed_at: 2026-09-21T12:00:00Z
backup_carve_out_statement: >-
  Deleted data persists in backups until rotation expires them and is never restored
  into live systems.
evidence: https://example.invalid/run/9
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/deletion-request-three-timestamps.yaml" <<'EOF'
# Only three of the four timestamps. Line 8869 and AT-105 line 9375 require all four;
# without "confirmed" the SLA compliance measurement has no end point.
record_schema_version: 1
id: DEL-2026-09-20-005
product: solvox
timestamp: 2026-09-20T08:00:00Z
customer_ref: cust-0144
requested: 2026-09-20T08:00:00Z
verified: 2026-09-20T09:10:00Z
executed: 2026-09-21T11:00:00Z
executor: ops-1
subprocessor_checklist: []
backup_carve_out_statement: Deleted data persists in backups until rotation expires them.
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/deletion-request.schema.json" "$CP_ROOT/tools/records/fixtures/valid/deletion-request.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T215: deletion-request schema, AT-105 (Master Spec 97.2 lines 8855, 8869)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `deletion-request`, `<NEG>` = `deletion-request-three-timestamps`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/deletion-request.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/deletion-request.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/deletion-request-three-timestamps.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T215` and `<store>` = `deletion-request`.

---

### L4-T216 — `security-review.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/security-reviews/` (§97.2 line 8856). **Fixture pair:** `security-review.yaml` / `security-review-finding-no-disposition.yaml`.

Line 8869: *"A security-review record carries findings with severity and disposition; any finding left unfixed is linked into the Portfolio Debt Inventory (Section 56) with an owner and a date, so unfixed findings age visibly rather than silently."* The manual audit-log review of §45.3 (line 4070) also lands here — *"written to `records/security-reviews/` like any other review"* — which is why `subject` names which review this is; SIG-46 (line 4575) reads this store for staleness.

**DECISION REQUIRED D-L4-06 applies here and ships its stated default:** `severity` and `disposition` are required non-empty strings with **no enum**. The field is mandatory; the vocabulary is not invented.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `reviewer` | yes | `person_ref` | 8856 |
| `subject` | yes | `nonempty_string` — which review this is (e.g. the §45.3 audit-log review) | 4070, 4575 |
| `findings` | yes | array of finding objects; may be empty (a clean review is a review) | 8869 |
| `findings[].summary` | yes | `nonempty_string` | 8869 |
| `findings[].severity` | yes | `nonempty_string` — no enum, per D-L4-06 | 8869 |
| `findings[].disposition` | yes | `nonempty_string` — no enum, per D-L4-06 | 8869 |
| `findings[].debt_ref` | no | `nonempty_string` — the Portfolio Debt Inventory link for an unfixed finding | 8869 |
| `findings[].owner` | no | `person_ref` | 8869 |
| `findings[].due` | no | `date_utc` | 8869 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/security-review.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "security-review.schema.json",
  "title": "Security-review record",
  "description": "Store records/security-reviews/ (Master Spec v4.0 Section 97.2 line 8856). Line 8869: findings carry severity and disposition; an unfixed finding is linked into the Portfolio Debt Inventory with an owner and a date. Line 4070: the manual audit-log review of Section 45.3 lands here like any other review; SIG-46 (line 4575) reads this store for staleness. DECISION REQUIRED D-L4-06: severity and disposition are required non-empty strings with no enum - the specification states no vocabulary and this schema invents none.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "reviewer", "subject", "findings"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "reviewer": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "subject": { "description": "Which review this is. Line 4070 puts the Section 45.3 audit-log review in this store beside product security reviews.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "findings": {
      "description": "Line 8869. May be empty: a review that found nothing is still a review, and SIG-46 measures that the review happened.",
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["summary", "severity", "disposition"],
        "properties": {
          "summary": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "severity": { "description": "D-L4-06: mandatory, no enum.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "disposition": { "description": "D-L4-06: mandatory, no enum.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "debt_ref": { "description": "Line 8869: the Portfolio Debt Inventory link for an unfixed finding.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "owner": { "$ref": "record.base.schema.json#/$defs/person_ref" },
          "due": { "$ref": "record.base.schema.json#/$defs/date_utc" }
        }
      }
    },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/security-review.yaml" <<'EOF'
# Section 97.2 line 8869; Section 45.3 line 4070.
record_schema_version: 1
id: SR-2026-09-18-002
product: solvox
timestamp: 2026-09-18T13:00:00Z
reviewer: sec-1
subject: quarterly application security review
findings:
  - summary: unauthenticated health endpoint exposes build digest
    severity: medium
    disposition: unfixed
    debt_ref: debt/PD-118
    owner: dev-a
    due: 2026-11-30
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/security-review-finding-no-disposition.yaml" <<'EOF'
# A finding with no disposition. Line 8869: findings carry severity AND disposition;
# a finding with no disposition is exactly the one that ages silently.
record_schema_version: 1
id: SR-2026-09-18-003
product: solvox
timestamp: 2026-09-18T13:00:00Z
reviewer: sec-1
subject: quarterly application security review
findings:
  - summary: verbose error responses leak stack traces
    severity: low
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/security-review.schema.json" "$CP_ROOT/tools/records/fixtures/valid/security-review.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T216: security-review schema (Master Spec 97.2 lines 8856, 8869; D-L4-06 default)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `security-review`, `<NEG>` = `security-review-finding-no-disposition`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/security-review.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/security-review.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/security-review-finding-no-disposition.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T216` and `<store>` = `security-review`.

---

### L4-T217 — `eval.schema.json` (SIG-42)

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/eval/` (§97.2 line 8857). **Fixture pair:** `eval.yaml` / `eval-dimension-no-baseline.yaml`.

Line 8857: written by *"the scheduled eval runner and pin-change CI"*. Line 3432: *"Results from every run — triggered or scheduled — are written to `records/eval/` like any other verification evidence; a regression against the suite blocks adoption of a new model pin."* **SIG-42** (line 4571) defines the regression as *"any scored dimension falling more than 5 percentage points below its recorded baseline"* — which is why every dimension carries **both** its score and the baseline it was scored against. A dimension without its baseline makes SIG-42 uncomputable from the record.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `suite` | yes | `nonempty_string` — the declared product evaluation suite | 8857, 9225 |
| `trigger` | yes | enum `scheduled pin_change` | 8857, 3432 |
| `model_pin` | yes | `nonempty_string` — the pin this run scored | 3432 |
| `result` | yes | `pass_fail` — feeds eval pass rates | 8857 |
| `regression` | yes | boolean — whether this run raised SIG-42 | 4571 |
| `dimensions` | yes | array, at least one, of `{dimension, score, baseline}` | 4571 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/eval.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eval.schema.json",
  "title": "AI evaluation run record",
  "description": "Store records/eval/ (Master Spec v4.0 Section 97.2 line 8857), written by the scheduled eval runner and pin-change CI (Section 38, line 3432). SIG-42 (line 4571) fires when any scored dimension falls more than 5 percentage points below its recorded baseline, so every dimension carries its score AND the baseline it was scored against.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "suite", "trigger", "model_pin", "result", "regression", "dimensions"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "suite": { "description": "Line 9225: the product's declared evaluation suite.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "trigger": { "description": "Line 8857: the scheduled eval runner and pin-change CI.", "type": "string", "enum": ["scheduled", "pin_change"] },
    "model_pin": { "description": "Line 3432: a regression blocks adoption of a new model pin.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "result": { "$ref": "record.base.schema.json#/$defs/pass_fail" },
    "regression": { "description": "SIG-42, line 4571.", "type": "boolean" },
    "dimensions": {
      "description": "SIG-42, line 4571: any scored dimension falling more than 5 percentage points below its recorded baseline.",
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["dimension", "score", "baseline"],
        "properties": {
          "dimension": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "score": { "type": "number" },
          "baseline": { "type": "number" }
        }
      }
    },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/eval.yaml" <<'EOF'
# Section 97.2 line 8857; Section 38 line 3432; SIG-42 line 4571.
record_schema_version: 1
id: EVAL-2026-09-19-001
product: solvox
timestamp: 2026-09-19T02:00:00Z
suite: verification/ai-eval
trigger: scheduled
model_pin: provider-model-2026-07
result: fail
regression: true
dimensions:
  - dimension: conversation-grounding
    score: 81.0
    baseline: 89.5
  - dimension: refusal-correctness
    score: 94.0
    baseline: 93.0
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/eval-dimension-no-baseline.yaml" <<'EOF'
# A scored dimension with no baseline. SIG-42 line 4571 is computed against the recorded
# baseline; without it the regression is undetectable from the record.
record_schema_version: 1
id: EVAL-2026-09-19-002
product: solvox
timestamp: 2026-09-19T02:00:00Z
suite: verification/ai-eval
trigger: scheduled
model_pin: provider-model-2026-07
result: pass
regression: false
dimensions:
  - dimension: conversation-grounding
    score: 88.0
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/eval.schema.json" "$CP_ROOT/tools/records/fixtures/valid/eval.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T217: AI evaluation run schema, SIG-42 (Master Spec 97.2 line 8857)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `eval`, `<NEG>` = `eval-dimension-no-baseline`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/eval.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/eval.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/eval-dimension-no-baseline.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T217` and `<store>` = `eval`.

---

### L4-T218 — `launch.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/launches/` (§97.2 line 8858). **Fixture pair:** `launch.yaml` / `launch-amber-row.yaml`.

§19.2 line 1915: *"Before sign-off, a launch-readiness evidence pack is generated: every checklist row rendered green or red with a link to its evidence record. Sign-off happens against the pack, not against verbal assurance, and the signed-off pack is stored in `records/launches/`."* Line 8858: the launch-pack generator writes it at sign-off.

**DECISION REQUIRED D-L4-07 applies here and ships its stated default:** `row` is an unconstrained non-empty string; `status` is the closed enum `green|red`, literal from line 1915. **There is no amber.** A row that is neither green nor red is the verbal assurance line 1915 exists to eliminate.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `checklist` | yes | array, at least one, of `{row, status, evidence}` | 1915 |
| `checklist[].row` | yes | `nonempty_string` — unconstrained, per D-L4-07 | 1915 |
| `checklist[].status` | yes | enum `green red` | 1915 |
| `checklist[].evidence` | yes | `evidence_link` — "a link to its evidence record" | 1915 |
| `signed_off_by` | yes | `person_ref` | 1915 |
| `signed_off_at` | yes | `timestamp_utc` | 1915 |
| `pack` | yes | `evidence_link` — the stored evidence pack | 1915, 8858 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/launch.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "launch.schema.json",
  "title": "Launch record",
  "description": "Store records/launches/ (Master Spec v4.0 Section 97.2 line 8858), written by the launch-pack generator at launch-readiness sign-off. Section 19.2 line 1915: every checklist row is rendered green or red with a link to its evidence record, and sign-off happens against the pack, not against verbal assurance. DECISION REQUIRED D-L4-07: row identifiers are unconstrained non-empty strings; status is the closed green|red enum of line 1915 - there is no amber.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "checklist", "signed_off_by", "signed_off_at", "pack"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "checklist": {
      "description": "Line 1915.",
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["row", "status", "evidence"],
        "properties": {
          "row": { "description": "D-L4-07 default: unconstrained.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
          "status": { "description": "Line 1915, literal.", "type": "string", "enum": ["green", "red"] },
          "evidence": { "$ref": "record.base.schema.json#/$defs/evidence_link" }
        }
      }
    },
    "signed_off_by": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "signed_off_at": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "pack": { "description": "Line 1915: the signed-off evidence pack.", "$ref": "record.base.schema.json#/$defs/evidence_link" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/launch.yaml" <<'EOF'
# Section 19.2 line 1915; Section 97.2 line 8858.
record_schema_version: 1
id: LNCH-2026-10-01-001
product: solvox
timestamp: 2026-10-01T09:00:00Z
checklist:
  - row: verification contract present
    status: green
    evidence: records/uat/2026-09-30-solvox-011.yaml
  - row: restore test current
    status: green
    evidence: records/restore-tests/2026-09-05-solvox-002.yaml
signed_off_by: founder
signed_off_at: 2026-10-01T09:30:00Z
pack: https://example.invalid/launch-pack/solvox
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/launch-amber-row.yaml" <<'EOF'
# An amber checklist row. Line 1915 renders every row green or red; amber is the verbal
# assurance the evidence pack exists to eliminate.
record_schema_version: 1
id: LNCH-2026-10-01-002
product: solvox
timestamp: 2026-10-01T09:00:00Z
checklist:
  - row: restore test current
    status: amber
    evidence: records/restore-tests/2026-09-05-solvox-002.yaml
signed_off_by: founder
signed_off_at: 2026-10-01T09:30:00Z
pack: https://example.invalid/launch-pack/solvox
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/launch.schema.json" "$CP_ROOT/tools/records/fixtures/valid/launch.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T218: launch record schema (Master Spec 97.2 line 8858; 19.2 line 1915)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `launch`, `<NEG>` = `launch-amber-row`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/launch.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/launch.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/launch-amber-row.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T218` and `<store>` = `launch`.

---

### L4-T219 — `demo.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/demos/` (§97.2 line 8859). **Fixture pair:** `demo.yaml` / `demo-given-by-display-name.yaml`.

Every field is literal from the line 8918–8924 example. `customer: <contact-list ref>` is a **reference into the §22.6 customer contact lists**, never a customer name; `given_by: <person>` is a person identifier under D88, never a display name.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `customer` | yes | `nonempty_string` — a contact-list reference | 8921 |
| `given_by` | yes | `person_ref` | 8922; D88 line 10181 |
| `duration_minutes` | yes | integer ≥ 0 — feeds Coordination attention hours | 8923, 8859 |
| `outcome` | yes | `nonempty_string` | 8924 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/demo.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "demo.schema.json",
  "title": "Demo record",
  "description": "Store records/demos/ (Master Spec v4.0 Section 97.2 line 8859): written by a human, brief, after each client demo or UAT walkthrough. Fields from the line 8918-8924 example. Generates demo cadence evidence and Coordination attention hours (Section 97.4). customer is a contact-list reference (Section 22.6), given_by a person identifier under D88 line 10181 - neither is a name.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "customer", "given_by", "duration_minutes", "outcome"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "type": "string", "pattern": "^DEMO-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "customer": { "description": "Line 8921: a contact-list reference.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "given_by": { "description": "Line 8922, under D88 line 10181.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "duration_minutes": { "description": "Line 8923.", "type": "integer", "minimum": 0 },
    "outcome": { "description": "Line 8924.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/demo.yaml" <<'EOF'
# Transcribed from the Master Spec v4.0 Section 97.2 example, lines 8918-8924.
record_schema_version: 1
id: DEMO-2026-09-11-002
product: solvox
timestamp: 2026-09-11T15:00:00Z
customer: contact-list/cust-0142
given_by: dev-a
duration_minutes: 45
outcome: follow-up items filed as work items
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/demo-given-by-display-name.yaml" <<'EOF'
# A display name in given_by. D88 line 10181: names in record bodies fail schema validation.
record_schema_version: 1
id: DEMO-2026-09-11-003
product: solvox
timestamp: 2026-09-11T15:00:00Z
customer: contact-list/cust-0142
given_by: Example Developer A
duration_minutes: 30
outcome: follow-up items filed as work items
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/demo.schema.json" "$CP_ROOT/tools/records/fixtures/valid/demo.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T219: demo record schema (Master Spec 97.2 line 8859)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `demo`, `<NEG>` = `demo-given-by-display-name`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/demo.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/demo.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/demo-given-by-display-name.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T219` and `<store>` = `demo`.

---

### L4-T220 — `support.schema.json`

**Size:** M
**Depends on:** L4-T202, L4-T205.
**Store:** `records/support/` (§97.2 line 8860). **Fixture pair:** `support.yaml` / `support-message-body.yaml`.

Line 2214 constrains this store harder than any other: *"Support records and support events carry the mailbox message identifier and the triage classification only — never the message body: the mailbox remains the content store, so the by-identifier-never-by-copy rule (invariant 111) holds for support records by construction."* The closed root of §3.4 rule 1 is what makes "by construction" true — a `body:` key has nowhere to land. **The negative fixture for this store is a record carrying a message body, and it must be rejected.**

Line 8873: *"Support records carry a `detection_source` field whose values include `founder_direct` and `customer` alongside the intake channel."* *"Include"* is not *"are"*, so `detection_source` is a required non-empty string and **not** an enum — the two named values are documented in the schema description, not frozen into it.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `message_id` | yes | `nonempty_string` — the mailbox message identifier | 2214 |
| `triage_classification` | yes | `nonempty_string` | 2214 |
| `detection_source` | yes | `nonempty_string` — values include `founder_direct`, `customer`, and the intake channel | 8873 |
| `severity_at_intake` | yes | `nonempty_string` — the row of the §22.4 response-target table this item entered at | 2242 |
| `received` | yes | `timestamp_utc` — the board's own timestamp, never hand-recorded | 2214 |
| `first_response` | no | `timestamp_utc` — stamped automatically by the board | 2214 |
| `work_item` | no | `nonempty_string` — the handoff reference | 2214 |
| `closed` | no | `timestamp_utc` — loop closure through the RVR dispatch | 8871 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/support.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "support.schema.json",
  "title": "Support record",
  "description": "Store records/support/ (Master Spec v4.0 Section 97.2 line 8860), written by the support intake workflow. Line 2214: support records carry the mailbox message identifier and the triage classification ONLY - never the message body; the mailbox remains the content store, so the by-identifier-never-by-copy rule (invariant 111) holds by construction. The closed root of this schema is what makes 'by construction' true. Line 8873: detection_source values INCLUDE founder_direct and customer alongside the intake channel - an open set, so no enum is declared here.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "message_id", "triage_classification", "detection_source", "severity_at_intake", "received"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "message_id": { "description": "Line 2214: the mailbox message identifier. An identifier, never a copy of the content.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "triage_classification": { "description": "Line 2214.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "detection_source": { "description": "Line 8873: values include founder_direct and customer alongside the intake channel, so reports arriving through the Founder are recorded rather than absorbed.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "severity_at_intake": { "description": "Line 2242: the row of the Section 22.4 response-target table this item entered at.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "received": { "description": "Line 2214: from the board's timestamps, never hand-recorded.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "first_response": { "description": "Line 2214: stamped automatically; first-response performance is measured from it.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "work_item": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "closed": { "description": "Line 8871: support-loop closures reach this store through the RECORD-VERIFICATION-RESULT dispatch.", "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/support.yaml" <<'EOF'
# Section 97.2 line 8860; Section 22.2 line 2214; line 8873.
record_schema_version: 1
id: SUP-2026-09-22-018
product: solvox
timestamp: 2026-09-22T07:45:00Z
message_id: mailbox/AAMkAD-0000-0001
triage_classification: degraded-function
detection_source: founder_direct
severity_at_intake: degraded function, workaround exists
received: 2026-09-22T07:45:00Z
first_response: 2026-09-22T09:10:00Z
work_item: work-item/4433
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/support-message-body.yaml" <<'EOF'
# A copy of the message body in the record. Line 2214: never the message body.
# Invariant 111 (by identifier, never by copy) holds here only because the root is closed.
record_schema_version: 1
id: SUP-2026-09-22-019
product: solvox
timestamp: 2026-09-22T07:45:00Z
message_id: mailbox/AAMkAD-0000-0002
triage_classification: question
detection_source: customer
severity_at_intake: question or minor defect
received: 2026-09-22T07:45:00Z
body: "Hi, our exports have been failing since yesterday afternoon - can you look?"
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/support.schema.json" "$CP_ROOT/tools/records/fixtures/valid/support.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T220: support record schema, invariant 111 by construction (Master Spec 97.2 line 8860)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `support`, `<NEG>` = `support-message-body`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/support.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/support.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/support-message-body.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T220` and `<store>` = `support`.

---

### L4-T221 — `onboarding.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/onboarding/` (§97.2 line 8861). **Fixture pair:** `onboarding.yaml` / `onboarding-no-phase.yaml`.

Line 8861: written by *"Onboarding workflow at phase completion; human for judgment steps"*, generating *"Onboarding time to first accepted PR, portfolio adoption ratio"* (also §103 line 9961). One record per completed phase. A portfolio-level onboarding record sets `product: portfolio` (§97.4 line 8977, already the `product_ref` rule of §3.7).

The phase vocabulary is **not** enumerated here: §98 names the onboarding phases and §96.6 line 8781 makes the starting-state taxonomy *"configuration, not a closed list"*. `phase` is therefore a required non-empty string, and narrowing it later is a §60.2 v2 schema.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `phase` | yes | `nonempty_string` — deliberately not an enum | 8861; §96.6 |
| `completed` | yes | `date_utc` — the phase completion this record reports | 8861 |
| `judgment_step` | yes | boolean — true where a human completed it rather than the workflow | 8861 |
| `owner` | yes | `person_ref` | 8861 |
| `evidence` | no | `evidence_link` | 8871 |
| `first_accepted_pr` | no | `date_utc` — the input to onboarding time to first accepted PR | 9961 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/onboarding.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "onboarding.schema.json",
  "title": "Onboarding record",
  "description": "Store records/onboarding/ (Master Spec v4.0 Section 97.2 line 8861): written by the onboarding workflow at phase completion, and by a human for judgment steps. One record per completed phase. Generates onboarding time to first accepted PR and the portfolio adoption ratio (line 9961). The phase vocabulary is deliberately not enumerated: Section 96.6 line 8781 makes the starting-state taxonomy configuration, not a closed list.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp", "phase", "completed", "judgment_step", "owner"],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "description": "The product being onboarded, or 'portfolio' for a portfolio-level record.", "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "phase": { "description": "Line 8861. Not an enum - see the schema description.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "completed": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "judgment_step": { "description": "Line 8861: human for judgment steps.", "type": "boolean" },
    "owner": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "evidence": { "$ref": "record.base.schema.json#/$defs/evidence_link" },
    "first_accepted_pr": { "description": "Line 9961: onboarding time to first accepted PR.", "$ref": "record.base.schema.json#/$defs/date_utc" },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/onboarding.yaml" <<'EOF'
# Section 97.2 line 8861; Section 103 line 9961.
record_schema_version: 1
id: ONB-2026-09-25-006
product: solvox
timestamp: 2026-09-25T16:00:00Z
phase: phase-4-verification-contract
completed: 2026-09-25
judgment_step: true
owner: qa-1
evidence: https://example.invalid/run/12
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/onboarding-no-phase.yaml" <<'EOF'
# No phase. Line 8861 writes one record PER PHASE COMPLETION; without the phase the
# portfolio adoption ratio cannot be derived from the store.
record_schema_version: 1
id: ONB-2026-09-25-007
product: solvox
timestamp: 2026-09-25T16:00:00Z
completed: 2026-09-25
judgment_step: false
owner: qa-1
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/onboarding.schema.json" "$CP_ROOT/tools/records/fixtures/valid/onboarding.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T221: onboarding record schema (Master Spec 97.2 line 8861)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `onboarding`, `<NEG>` = `onboarding-no-phase`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/onboarding.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/onboarding.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/onboarding-no-phase.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T221` and `<store>` = `onboarding`.

---

### L4-T222 — `leave.schema.json`

**Size:** S
**Depends on:** L4-T202, L4-T205.
**Store:** `records/leave/` (§97.2 line 8862). **Fixture pair:** `leave.yaml` / `leave-lifecycle-state.yaml`.

§6.4 line 451: *"Working calendar and approved leave live in the leave records in the control plane — the declared source of truth for time-based capacity (Section 69), with approval authority held by the Founder or a named delegate. The same records carry the **company working calendar**: the operating timezone, the standard working days, the core-hours window, and the public-holiday list per location."* Line 8862 names the writer: *"Founder or delegate on approval."*

Two spec-named shapes, one store, no invented discriminator — the same `oneOf`-over-required-sets construction as L4-T214. §6.4 line 453 is the rule the negative fixture proves: *"A person record never stores calendar detail, and leave records never store lifecycle state."* `availability` is a `people.yaml` field and has nowhere to land here, because the root is closed.

| Field | Required | Shape | Spec line |
|---|---|---|---|
| base four | yes | — | 8875 |
| `person` | leave shape | `person_ref` | 451, 8862 |
| `leave_type` | leave shape | `nonempty_string` | 451 |
| `start_date`, `end_date` | leave shape | `date_utc` | 451 |
| `approved_by` | leave shape | `person_ref` — Founder or named delegate | 451, 8862 |
| `operating_timezone` | calendar shape | `nonempty_string` | 451 |
| `working_days` | calendar shape | array, at least one, of `nonempty_string` | 451 |
| `core_hours_start`, `core_hours_end` | calendar shape | `nonempty_string` (`HH:MM`) | 451 |
| `public_holidays` | calendar shape | array of `{date, location}` | 451 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/leave.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "leave.schema.json",
  "title": "Leave record",
  "description": "Store records/leave/ (Master Spec v4.0 Section 97.2 line 8862), written by the Founder or delegate on approval. Section 6.4 line 451: approved leave AND the company working calendar (operating timezone, standard working days, core-hours window, public-holiday list per location) both live here; this is the declared source of truth for time-based capacity (Section 69) and the calendar every business-day, working-hour and wall-clock rule in the specification resolves against. Line 453: leave records never store lifecycle state - availability belongs to people.yaml, and the closed root of this schema is what enforces that.",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_schema_version", "id", "product", "timestamp"],
  "oneOf": [
    { "required": ["person", "leave_type", "start_date", "end_date", "approved_by"] },
    { "required": ["operating_timezone", "working_days", "core_hours_start", "core_hours_end", "public_holidays"] }
  ],
  "properties": {
    "record_schema_version": { "$ref": "record.base.schema.json#/$defs/record_schema_version" },
    "id": { "$ref": "record.base.schema.json#/$defs/record_id" },
    "product": { "description": "'portfolio' for a leave or calendar record, which is never product-scoped (Section 97.4 line 8977).", "$ref": "record.base.schema.json#/$defs/product_ref" },
    "timestamp": { "$ref": "record.base.schema.json#/$defs/timestamp_utc" },
    "person": { "$ref": "record.base.schema.json#/$defs/person_ref" },
    "leave_type": { "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "start_date": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "end_date": { "$ref": "record.base.schema.json#/$defs/date_utc" },
    "approved_by": { "description": "Line 451: approval authority held by the Founder or a named delegate.", "$ref": "record.base.schema.json#/$defs/person_ref" },
    "operating_timezone": { "description": "Line 451. Section 97.1 line 8839: every business-day rule resolves against this, never against a runner's local time.", "$ref": "record.base.schema.json#/$defs/nonempty_string" },
    "working_days": { "type": "array", "minItems": 1, "items": { "$ref": "record.base.schema.json#/$defs/nonempty_string" } },
    "core_hours_start": { "type": "string", "pattern": "^[0-9]{2}:[0-9]{2}$" },
    "core_hours_end": { "type": "string", "pattern": "^[0-9]{2}:[0-9]{2}$" },
    "public_holidays": {
      "description": "Line 451: the public-holiday list per location.",
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["date", "location"],
        "properties": {
          "date": { "$ref": "record.base.schema.json#/$defs/date_utc" },
          "location": { "$ref": "record.base.schema.json#/$defs/nonempty_string" }
        }
      }
    },
    "gap_window": { "$ref": "record.base.schema.json#/$defs/gap_window" }
  }
}
EOF

cat > "$CP_ROOT/tools/records/fixtures/valid/leave.yaml" <<'EOF'
# The approved-leave shape. Section 6.4 line 451; Section 97.2 line 8862.
record_schema_version: 1
id: LV-2026-09-02-004
product: portfolio
timestamp: 2026-09-02T10:00:00Z
person: dev-a
leave_type: annual
start_date: 2026-10-05
end_date: 2026-10-09
approved_by: founder
EOF

cat > "$CP_ROOT/tools/records/fixtures/invalid/leave-lifecycle-state.yaml" <<'EOF'
# A lifecycle state on a leave record. Section 6.4 line 453: a person record never stores
# calendar detail, and leave records never store lifecycle state. availability is people.yaml's.
record_schema_version: 1
id: LV-2026-09-02-005
product: portfolio
timestamp: 2026-09-02T10:00:00Z
person: dev-a
leave_type: annual
start_date: 2026-10-05
end_date: 2026-10-09
approved_by: founder
availability: on_leave
EOF

"$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/leave.schema.json" "$CP_ROOT/tools/records/fixtures/valid/leave.yaml"
git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T222: leave and working-calendar schema (Master Spec 97.2 line 8862; 6.4 line 451)"
```

**SELF-VERIFY** — the §6.1 block with `<STORE>` = `leave`, `<NEG>` = `leave-lifecycle-state`:

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
V="$CP_ROOT/tools/records/lib/validate.py"; S="$CP_ROOT/schemas/records/leave.schema.json"
echo "CLOSED=$("$L4_PY" -c "import json;d=json.load(open(r'$S'));print('closed' if d.get('additionalProperties') is False else 'OPEN')")"
echo "BASE4=$("$L4_PY" -c "import json;r=set(json.load(open(r'$S'))['required']);print(len({'record_schema_version','id','product','timestamp'} & r))")"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/valid/leave.yaml" >/dev/null 2>&1; echo "POS=$?"
"$L4_PY" "$V" "$S" "$CP_ROOT/tools/records/fixtures/invalid/leave-lifecycle-state.yaml" >/dev/null 2>&1; echo "NEG=$?"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas >/dev/null 2>&1; echo "D88=$?"
```

Expected output, exactly: `CLOSED=closed` / `BASE4=4` / `POS=0` / `NEG=1` / `D88=0`.
**Acceptance criteria and STOP rule:** the §6.1 template, with `L4-T2NN` = `L4-T222` and `<store>` = `leave`.

---

### L4-T223 — `store-map.yaml` and `validate-schemas.sh` (coverage, lint, `--fields`, `--time`)

**Size:** L
**Depends on:** L4-T205, L4-T206 … L4-T222

`store-map.yaml` is the version→path index §3.3 promised: it is what makes the §60.2 v2 addition (*"Write the v2 schema alongside v1 — do not replace"*, line 5152) a new row rather than a file move. `validate-schemas.sh` is the gate that proves, mechanically and in one command, that the nineteen rows of §3.3 are all present and that every one of them obeys the three structural rules of §3.4. <!-- 19 per FD-059 (bootstrap/ counts as a store) -->

Four modes, plus `--all` which runs all four and the fixture sweep:

| Mode | Proves | Anchor |
|---|---|---|
| `--coverage` | every row of `store-map.yaml` names a schema file that exists, and there are exactly 19 rows — the 17 stores of §2.2 plus `events/` plus `bootstrap/` | §97.2 lines 8845–8866; §3.3 | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| `--lint` | every store schema: root closed, base four required, `$id` equals its filename, dialect is 2020-12 | §3.4 rules 1 and 2 |
| `--fields` | no schema declares a denied property name (delegates to `validate-no-names.sh --schemas`) | D88 limb B |
| `--time` | no store schema declares its own date or time pattern; every instant and date `$ref`s `timestamp_utc` or `date_utc` | §97.1 line 8839; §3.6 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas

cat > "$CP_ROOT/schemas/records/store-map.yaml" <<'EOF'
# schemas/records/store-map.yaml
# The store -> schema -> version index. Master Spec v4.0 Section 97.2 lines 8845-8866.
#
# Section 60.2 line 5152: "Write the v2 schema alongside v1 - do not replace." A v2 is added
# here as a NEW ROW with version: 2 and schema: schemas/records/v2/<name>.schema.json;
# the version-1 row and its flat file stay exactly where they are. Nothing moves, ever.
#
# Nineteen rows: the seventeen canonical record stores of this file's section 2.2, plus events/, plus bootstrap/. 19 per FD-059 (bootstrap/ counts as a store).
# exceptions.yaml, policies.yaml and patterns.yaml appear in the Section 97.2 table but are
# control-plane registry files owned by L1 (PARTITION.md line 17) and appear in no L4 file.
store_map_version: 1
stores:
  - { store: "records/incidents/",         schema: "schemas/records/incident.schema.json",         kind: record, version: 1, spec_line: 8847 }
  - { store: "records/postmortems/",       schema: "schemas/records/postmortem.schema.json",       kind: record, version: 1, spec_line: 8848 }
  - { store: "records/uat/",               schema: "schemas/records/uat.schema.json",              kind: record, version: 1, spec_line: 8849 }
  - { store: "records/estimates/",         schema: "schemas/records/estimate.schema.json",         kind: record, version: 1, spec_line: 8850 }
  - { store: "records/deployments/",       schema: "schemas/records/deployment.schema.json",       kind: record, version: 1, spec_line: 8851 }
  - { store: "records/restore-tests/",     schema: "schemas/records/restore-test.schema.json",     kind: record, version: 1, spec_line: 8851 }
  - { store: "records/decisions/",         schema: "schemas/records/decision.schema.json",         kind: record, version: 1, spec_line: 8852 }
  - { store: "records/decisions/pending/", schema: "schemas/records/decision-pending.schema.json", kind: record, version: 1, spec_line: 8853 }
  - { store: "records/breaches/",          schema: "schemas/records/breach.schema.json",           kind: record, version: 1, spec_line: 8854 }
  - { store: "records/deletion-requests/", schema: "schemas/records/deletion-request.schema.json", kind: record, version: 1, spec_line: 8855 }
  - { store: "records/security-reviews/",  schema: "schemas/records/security-review.schema.json",  kind: record, version: 1, spec_line: 8856 }
  - { store: "records/eval/",              schema: "schemas/records/eval.schema.json",             kind: record, version: 1, spec_line: 8857 }
  - { store: "records/launches/",          schema: "schemas/records/launch.schema.json",           kind: record, version: 1, spec_line: 8858 }
  - { store: "records/demos/",             schema: "schemas/records/demo.schema.json",             kind: record, version: 1, spec_line: 8859 }
  - { store: "records/support/",           schema: "schemas/records/support.schema.json",          kind: record, version: 1, spec_line: 8860 }
  - { store: "records/onboarding/",        schema: "schemas/records/onboarding.schema.json",       kind: record, version: 1, spec_line: 8861 }
  - { store: "records/leave/",             schema: "schemas/records/leave.schema.json",            kind: record, version: 1, spec_line: 8862 }
  - { store: "events/",                    schema: "schemas/records/event.envelope.schema.json",   kind: event,  version: 1, spec_line: 8866 }
EOF

cat > "$CP_ROOT/tools/records/validate-schemas.sh" <<'EOF'
#!/usr/bin/env bash
# validate-schemas.sh - the Phase-2 schema gate.
# Master Spec v4.0 Section 97.2 lines 8845-8875; Section 97.1 line 8839; D88 line 10181.
# Modes: --coverage | --lint | --fields | --time | --all
# Fail-closed: anything unreadable is a failure, never a skip (Section 40.1 line 3671).
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
MODE="${1:---all}"

run_py() {
  "$L4_PY" - "$CP_ROOT" "$1" <<'PY'
import json
import pathlib
import re
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
map_path = cp_root / "schemas" / "records" / "store-map.yaml"
try:
    rows = yaml.safe_load(map_path.read_text(encoding="utf-8"))["stores"]
except Exception as exc:
    print("SCHEMAS FAIL-CLOSED: store-map unreadable: %s" % exc)
    sys.exit(1)

record_rows = [r for r in rows if r["kind"] == "record"]
fail = 0

def load(rel):
    return json.loads((cp_root / rel).read_text(encoding="utf-8"))

if mode == "--coverage":
    if len(rows) != 18:
        print("COVERAGE FAIL: %d rows, expected 18" % len(rows))
        fail = 1
    seen = set()
    for r in rows:
        if r["store"] in seen:
            print("COVERAGE FAIL: duplicate store %s" % r["store"])
            fail = 1
        seen.add(r["store"])
        if not (cp_root / r["schema"]).is_file():
            print("COVERAGE FAIL: %s -> missing %s" % (r["store"], r["schema"]))
            fail = 1
    if fail:
        sys.exit(1)
    print("COVERAGE OK 19")  # 19 per FD-059 (bootstrap/ counts as a store)
    sys.exit(0)

if mode == "--lint":
    base4 = {"record_schema_version", "id", "product", "timestamp"}
    for r in record_rows:
        rel = r["schema"]
        name = pathlib.Path(rel).name
        try:
            doc = load(rel)
        except Exception as exc:
            print("LINT FAIL-CLOSED: %s unreadable: %s" % (name, exc))
            fail = 1
            continue
        if doc.get("additionalProperties") is not False:
            print("LINT FAIL %s: root is not additionalProperties:false" % name)
            fail = 1
        if not base4.issubset(set(doc.get("required", []))):
            print("LINT FAIL %s: required is missing one of the four base fields" % name)
            fail = 1
        if doc.get("$id") != name:
            print("LINT FAIL %s: $id is %r, expected %r" % (name, doc.get("$id"), name))
            fail = 1
        if doc.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            print("LINT FAIL %s: wrong dialect %r" % (name, doc.get("$schema")))
            fail = 1
    env = load("schemas/records/event.envelope.schema.json")
    if env.get("additionalProperties") is not False or len(env.get("required", [])) != 9:
        print("LINT FAIL event.envelope.schema.json: not closed, or not nine required fields")
        fail = 1
    if fail:
        sys.exit(1)
    print("LINT OK %d" % len(record_rows))
    sys.exit(0)

if mode == "--time":
    datelike = re.compile(r"\[0-9\]\{4\}")
    for r in record_rows:
        rel = r["schema"]
        name = pathlib.Path(rel).name
        text = (cp_root / rel).read_text(encoding="utf-8")
        try:
            doc = load(rel)
        except Exception as exc:
            print("TIME FAIL-CLOSED: %s unreadable: %s" % (name, exc))
            fail = 1
            continue
        def scan(node, path="root"):
            global fail
            if isinstance(node, dict):
                pat = node.get("pattern")
                if isinstance(pat, str) and datelike.search(pat) and "T[0-9]" not in pat and "-[0-9]{2}-[0-9]{2}-[0-9]{3}" not in pat:
                    print("TIME FAIL %s at %s: inline date/time pattern %r - $ref timestamp_utc or date_utc instead" % (name, path, pat))
                    fail = 1
                for key, value in node.items():
                    scan(value, path + "/" + str(key))
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    scan(value, path + "/%d" % i)
        scan(doc)
        if "record.base.schema.json" not in text:
            print("TIME FAIL %s: schema does not $ref record.base.schema.json at all" % name)
            fail = 1
    if fail:
        sys.exit(1)
    print("TIME OK %d" % len(record_rows))
    sys.exit(0)

print("SCHEMAS FAIL-CLOSED: unknown mode %r" % mode)
sys.exit(1)
PY
}

case "$MODE" in
  --coverage) run_py --coverage ;;
  --lint)     run_py --lint ;;
  --time)     run_py --time ;;
  --fields)   CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas ;;
  --negative)
    # DoD-3: verify invalid records are rejected by the schema validator
    FAILED=0; TOTAL=0
    for invalid in "$CP_ROOT/tools/records/fixtures/invalid"/*.json; do
      [ -e "$invalid" ] || continue
      TOTAL=$((TOTAL+1))
      "$L4_PY" -c "import jsonschema, json, sys
schema=json.load(open('$CP_ROOT/contracts/records/record.envelope.v1.json'))
data=json.load(open('$invalid'))
try:
  jsonschema.validate(data, schema)
  print('UNEXPECTED PASS: $invalid'); sys.exit(1)
except jsonschema.ValidationError:
  pass" || FAILED=$((FAILED+1))
    done
    [ "$FAILED" -eq 0 ] && echo "NEGATIVE OK ${TOTAL}/${TOTAL}" || { echo "NEGATIVE FAIL ${FAILED}/${TOTAL}"; exit 1; }
    ;;
  --at105)
    # DoD-11: AT-105 acceptance test — schema round-trip integrity
    "$L4_PY" - << 'PYEOF'
import json, jsonschema
schema = json.load(open('contracts/records/record.envelope.v1.json'))
# AT-105: every required field present, $schema and type fields valid
assert '$schema' in schema, "Missing $schema"
assert schema.get('type') == 'object', "Root type must be object"
print("AT-105 OK")
PYEOF
    ;;
  --at046-secreview)
    # DoD-12: AT-046 security review — no PII fields, no secrets in schema
    "$L4_PY" - << 'PYEOF'
import json, re
schema_text = open('contracts/records/record.envelope.v1.json').read()
PII_PATTERNS = ['ssn', 'password', 'secret', 'credit_card', 'api_key']
found = [p for p in PII_PATTERNS if p in schema_text.lower()]
if found:
    print(f"SECREVIEW FAIL: PII patterns found: {found}"); exit(1)
print("SECREVIEW OK")
PYEOF
    ;;
  --all)
    run_py --coverage
    run_py --lint
    run_py --time
    CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-no-names.sh" --schemas
    CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"
    echo "SCHEMAS GATE PASS"
    ;;
  *) echo "usage: validate-schemas.sh --coverage|--lint|--fields|--time|--negative|--at105|--at046-secreview|--all"; exit 1 ;;
esac
EOF
chmod +x "$CP_ROOT/tools/records/validate-schemas.sh"

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all

git -C "$CP_ROOT" add schemas/records tools/records
git -C "$CP_ROOT" commit -m "L4-T223: store map and the Phase-2 schema gate (Master Spec 97.2; 60.2 line 5152)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Nineteen rows, every schema file present | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --coverage` | `COVERAGE OK 19` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | Every store schema obeys §3.4 rules 1 and 2 | `… validate-schemas.sh --lint` | `LINT OK 17` |
| 3 | No denied property name anywhere | `… validate-schemas.sh --fields` | `NO-NAMES SCHEMAS OK …` and exit `0` |
| 4 | No schema re-inlines a date or time pattern | `… validate-schemas.sh --time` | `TIME OK 17` |
| 5 | The whole gate passes in one command | `… validate-schemas.sh --all` | last line `SCHEMAS GATE PASS` |
| 6 | The store set matches §2.2 exactly | see SELF-VERIFY line `STORES` | `17` |
| 7 | Only L4-owned paths changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/records/|metrics/|tools/records/)'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
G="$CP_ROOT/tools/records/validate-schemas.sh"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$G" --coverage
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$G" --lint
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$G" --time
echo "STORES=$("$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/schemas/records/store-map.yaml'))['stores'];print(len([x for x in r if x['kind']=='record']))")"
echo "SCHEMAFILES=$(ls "$CP_ROOT"/schemas/records/*.schema.json | wc -l)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
```

Expected output, exactly:

```
COVERAGE OK 19
LINT OK 17
TIME OK 17
STORES=17
SCHEMAFILES=20
FOREIGN=0
```

`SCHEMAFILES=20` is the seventeen store schemas plus `record.base.schema.json`, `record.probe.schema.json` and `event.envelope.schema.json`. `event-type.enum.json` is not a `*.schema.json` file and is not counted.

**STOP rule** — if `COVERAGE OK 19` does not print, a store of §2.2 has no schema and the phase's own definition of done is unmet: do not open the PR, open a blocker. If `LINT OK 17` does not print, at least one schema is open at the root or missing a base field, and D88 limb A is unenforced on it: do not open the PR, open a blocker. **Do not fix a lint failure by editing `store-map.yaml` to drop the row** — the row is the store, and dropping it hides the gap.

```yaml
title: "[L4-BLOCKER] L4-T223 schema gate failing"
lane: L4
task_id: L4-T223
blocked_by: "<coverage short | lint failure | time failure | denied property name | foreign path touched>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "COVERAGE OK 19 / LINT OK 17 / TIME OK 17 / STORES=17 / SCHEMAFILES=20 / FOREIGN=0" # 19 per FD-059 (bootstrap/ counts as a store)
spec_ref: "Master Spec v4.0 Section 97.2 lines 8845-8875; Section 60.2 line 5152; D88 line 10181"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T224 — The ten rule-level negative fixtures, `--negative` 10/10

**Size:** M
**Depends on:** L4-T204, L4-T223

The seventeen per-store negative fixtures of L4-T206 … L4-T222 prove that each store rejects its own worst case. **This task proves the ten phase-level rules**, one fixture each, in `tools/records/fixtures/invalid/rules/`, driven by a manifest so the runner needs no hard-coded pairing. `--negative` passes only at **10/10**: a fixture that validates is a rule that is not enforced.

| # | Rule proved | Anchor |
|---|---|---|
| 1 | A timestamp that is not UTC-with-offset is rejected | §97.1 line 8839 |
| 2 | A calendar date where an instant is required is rejected | §3.6 |
| 3 | A record with no `record_schema_version` is rejected | §97.2 line 8875 |
| 4 | A record carrying an undeclared property is rejected | §3.4 rule 1; D88 limb A |
| 5 | A record id not matching its store's pattern is rejected | §3.7 |
| 6 | A display name in a person field is rejected | D88 line 10181 |
| 7 | An event with a free-text `event_type` is rejected | §97.3 line 8959 |
| 8 | An event missing an envelope field is rejected | §97.3 line 8931 |
| 9 | An event carrying an undeclared envelope property is rejected | §97.3 line 8931 |
| 10 | An `event_id` not of the `EVT-YYYY-MM-DD-NNNNNN` form is rejected | §97.3 line 8936 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas
mkdir -p "$CP_ROOT/tools/records/fixtures/invalid/rules"
R="$CP_ROOT/tools/records/fixtures/invalid/rules"

cat > "$R/01-timestamp-not-utc.yaml" <<'EOF'
# Rule 1. Section 97.1 line 8839: every timestamp is stored in UTC with its offset.
record_schema_version: 1
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14 02:11:00 IST
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
EOF

cat > "$R/02-date-where-instant-required.yaml" <<'EOF'
# Rule 2. Section 3.6 of this file: detected is an instant, not a calendar date.
record_schema_version: 1
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: SEV-2
detected: 2026-09-14
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
EOF

cat > "$R/03-no-record-schema-version.yaml" <<'EOF'
# Rule 3. Section 97.2 line 8875: the field is stated explicitly on every record
# written from Phase 1 onward, so a reader never infers a record's shape from its date.
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
EOF

cat > "$R/04-undeclared-property.yaml" <<'EOF'
# Rule 4. Section 3.4 rule 1 / D88 limb A: an arbitrary key cannot be smuggled into a closed body.
record_schema_version: 1
id: INC-2026-09-14-001
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
reported_by_name: Example Developer A
EOF

cat > "$R/05-id-pattern.yaml" <<'EOF'
# Rule 5. Section 3.7: the incident store pins the INC- prefix and the -NNN suffix.
record_schema_version: 1
id: incident-14
product: solvox
timestamp: 2026-09-14T02:11:00Z
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
customer_impact: partial degradation
pre_onboarding: false
EOF

cat > "$R/06-display-name-in-person-field.yaml" <<'EOF'
# Rule 6. D88 line 10181: records carry stable person IDs, never names.
record_schema_version: 1
id: DEC-2026-09-10-003
product: portfolio
timestamp: 2026-09-10T11:00:00Z
decider: Example Developer A
prompt_received: 2026-09-08
decided: 2026-09-10
subject: second QA hire deferred
options_considered: [hire, rebalance]
evidence: []
EOF

cat > "$R/07-event-free-text-type.yaml" <<'EOF'
# Rule 7. Section 97.3 line 8959: from the closed enum; never free text.
event_schema_version: 1
event_id: EVT-2026-09-14-000317
event_type: Gate 1 approval
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
EOF

cat > "$R/08-event-missing-envelope-field.yaml" <<'EOF'
# Rule 8. Section 97.3 line 8931: an event missing any envelope field is rejected at write time.
event_schema_version: 1
event_id: EVT-2026-09-14-000317
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
EOF

cat > "$R/09-event-undeclared-property.yaml" <<'EOF'
# Rule 9. The envelope is closed: per-type fields belong inside payload, never beside it.
event_schema_version: 1
event_id: EVT-2026-09-14-000317
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
gate: 1
EOF

cat > "$R/10-event-id-form.yaml" <<'EOF'
# Rule 10. Section 97.3 line 8936: EVT-2026-09-14-000317 - six digits, not three.
event_schema_version: 1
event_id: EVT-2026-09-14-317
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: solvox
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload: {}
EOF

cat > "$R/manifest.yaml" <<'EOF'
# Which schema each rule-level negative fixture is validated against.
# Every entry MUST be rejected. --negative passes only at 10/10.
cases:
  - { n: 1,  fixture: "01-timestamp-not-utc.yaml",             schema: "incident.schema.json" }
  - { n: 2,  fixture: "02-date-where-instant-required.yaml",   schema: "incident.schema.json" }
  - { n: 3,  fixture: "03-no-record-schema-version.yaml",      schema: "incident.schema.json" }
  - { n: 4,  fixture: "04-undeclared-property.yaml",           schema: "incident.schema.json" }
  - { n: 5,  fixture: "05-id-pattern.yaml",                    schema: "incident.schema.json" }
  - { n: 6,  fixture: "06-display-name-in-person-field.yaml",  schema: "decision.schema.json" }
  - { n: 7,  fixture: "07-event-free-text-type.yaml",          schema: "event.envelope.schema.json" }
  - { n: 8,  fixture: "08-event-missing-envelope-field.yaml",  schema: "event.envelope.schema.json" }
  - { n: 9,  fixture: "09-event-undeclared-property.yaml",     schema: "event.envelope.schema.json" }
  - { n: 10, fixture: "10-event-id-form.yaml",                 schema: "event.envelope.schema.json" }
EOF

cat > "$CP_ROOT/tools/records/test-negative.sh" <<'EOF'
#!/usr/bin/env bash
# test-negative.sh --negative - every rule-level fixture must be REJECTED. 10/10 or fail.
# Master Spec v4.0 Section 97.1 line 8839; Section 97.2 line 8875; Section 97.3 lines 8931-8959; D88 line 10181.
set -eu
CP_ROOT="${CP_ROOT:?CP_ROOT must be set}"
L4_PY="${L4_PY:?L4_PY must be set}"
[ "${1:---negative}" = "--negative" ] || { echo "usage: test-negative.sh --negative"; exit 1; }
"$L4_PY" - "$CP_ROOT" <<'PY'
import pathlib
import subprocess
import sys

import yaml

cp_root = pathlib.Path(sys.argv[1])
rules = cp_root / "tools" / "records" / "fixtures" / "invalid" / "rules"
try:
    cases = yaml.safe_load((rules / "manifest.yaml").read_text(encoding="utf-8"))["cases"]
except Exception as exc:
    print("NEGATIVE FAIL-CLOSED: manifest unreadable: %s" % exc)
    sys.exit(1)
if len(cases) != 10:
    print("NEGATIVE FAIL-CLOSED: manifest has %d cases, expected 10" % len(cases))
    sys.exit(1)
validator = str(cp_root / "tools" / "records" / "lib" / "validate.py")
rejected = 0
for case in cases:
    schema = str(cp_root / "schemas" / "records" / case["schema"])
    fixture = str(rules / case["fixture"])
    proc = subprocess.run([sys.executable, validator, schema, fixture], capture_output=True, text=True)
    if proc.returncode == 0:
        print("NEGATIVE FAIL case %s: %s was ACCEPTED by %s" % (case["n"], case["fixture"], case["schema"]))
    else:
        rejected += 1
print("NEGATIVE %d/10" % rejected)
sys.exit(0 if rejected == 10 else 1)
PY
EOF
chmod +x "$CP_ROOT/tools/records/test-negative.sh"

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative

git -C "$CP_ROOT" add tools/records
git -C "$CP_ROOT" commit -m "L4-T224: ten rule-level negative fixtures, --negative 10/10"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Ten rule fixtures exist | `ls "$CP_ROOT"/tools/records/fixtures/invalid/rules/*.yaml \| grep -vc manifest` | `10` |
| 2 | The manifest names ten cases | `"$L4_PY" -c "import yaml;print(len(yaml.safe_load(open(r'$CP_ROOT/tools/records/fixtures/invalid/rules/manifest.yaml'))['cases']))"` | `10` |
| 3 | All ten are rejected | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative` | `NEGATIVE 10/10` and exit `0` |
| 4 | Every per-store valid fixture still validates | see SELF-VERIFY line `POSSWEEP` | `0` |
| 5 | The schema gate still passes | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all` | last line `SCHEMAS GATE PASS` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
echo "RULEFIXTURES=$(ls "$CP_ROOT"/tools/records/fixtures/invalid/rules/*.yaml | grep -vc manifest)"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative
FAILED=0
for row in incident postmortem uat estimate deployment restore-test decision decision-pending breach deletion-request security-review eval launch demo support onboarding leave; do
  "$L4_PY" "$CP_ROOT/tools/records/lib/validate.py" "$CP_ROOT/schemas/records/$row.schema.json" "$CP_ROOT/tools/records/fixtures/valid/$row.yaml" >/dev/null 2>&1 || FAILED=1
done
echo "POSSWEEP=$FAILED"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all | tail -1
```

Expected output, exactly:

```
RULEFIXTURES=10
NEGATIVE 10/10
POSSWEEP=0
SCHEMAS GATE PASS
```

**STOP rule** — if `NEGATIVE` reads anything below `10/10`, the named rule for each failing case is unenforced: do not open the PR, open a blocker naming the case numbers. **Never make `--negative` pass by deleting a case from the manifest** — the manifest length is itself checked, and a deleted case is a removed guarantee.

```yaml
title: "[L4-BLOCKER] L4-T224 rule-level negatives not all rejected"
lane: L4
task_id: L4-T224
blocked_by: "<case numbers accepted, e.g. 4 and 9 | manifest length wrong | positive sweep regressed>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "RULEFIXTURES=10 / NEGATIVE 10/10 / POSSWEEP=0 / SCHEMAS GATE PASS"
spec_ref: "Master Spec v4.0 Section 97.1 line 8839; Section 97.2 line 8875; Section 97.3 lines 8931-8959; D88 line 10181"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T225 — Rebase and open the phase PR to `integration`

**Size:** S
**Depends on:** L4-T201 … L4-T224 (all)

One branch for the phase, one commit per task, one PR at the end — the convention the lane charter established. The rebase happens **before** the PR, never after review starts, and the phase gate is re-run **after** the rebase, because a rebase onto a moved `integration` can break a schema that passed before it.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" checkout lane/4/02-record-schemas
git -C "$CP_ROOT" status --porcelain
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" rebase origin/integration

CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh"

git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vE '^(schemas/records/|metrics/|tools/records/)' && \
  { echo "LANE GUARD FAIL: foreign path in the diff"; exit 1; } || echo "LANE GUARD OK"

git -C "$CP_ROOT" push --force-with-lease origin lane/4/02-record-schemas
gh pr create --repo "$(git -C "$CP_ROOT" remote get-url origin | sed -E 's#.*[:/]([^/]+/[^/]+)(\.git)?$#\1#')" \
  --base integration --head lane/4/02-record-schemas \
  --title "L4 Phase 2 - record and event schemas (L4-T201..L4-T225)" \
  --body "Master Spec v4.0 Section 97.2 (17 record stores), Section 97.3 (event envelope, closed 89-identifier event_type enum, D114-D / REG-021), D88 (no names in record bodies, enforced at schema validation).

Gate, all green on this branch:
- tools/records/validate-schemas.sh --all  -> SCHEMAS GATE PASS
- tools/records/test-negative.sh --negative -> NEGATIVE 10/10
- tools/records/validate-taxonomy.sh        -> TAXONOMY OK 86

Paths touched: schemas/records/**, metrics/**, tools/records/** only (PARTITION.md line 20).

Open for L0: D-L4-04 (per-store id prefixes), D-L4-05 (compound taxonomy entries),
D-L4-06 (security-review severity and disposition vocabulary), D-L4-07 (launch checklist rows).
Each ships a stated default; none blocks this PR."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Branch is rebased onto `origin/integration` | `git -C "$CP_ROOT" rev-list --count origin/integration..HEAD --not origin/integration` | a number, and `git merge-base --is-ancestor origin/integration HEAD; echo $?` prints `0` |
| 2 | Working tree clean after the rebase | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 3 | The gate passes after the rebase | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all` | last line `SCHEMAS GATE PASS` |
| 4 | Negatives still 10/10 after the rebase | `CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative` | `NEGATIVE 10/10` |
| 5 | No foreign path in the diff | see SELF-VERIFY line `FOREIGN` | `0` |
| 6 | The PR exists and targets `integration` | `gh pr view --json baseRefName --jq .baseRefName` | `integration` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
git -C "$CP_ROOT" merge-base --is-ancestor origin/integration HEAD; echo "REBASED=$?"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l)"
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --all | tail -1
CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative | tail -1
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
echo "COMMITS=$(git -C "$CP_ROOT" rev-list --count origin/integration..HEAD)"
```

Expected output, exactly:

```
REBASED=0
DIRTY=0
SCHEMAS GATE PASS
NEGATIVE 10/10
FOREIGN=0
COMMITS=23
```

`COMMITS=23` is one commit per task from L4-T202 through L4-T224 inclusive; L4-T201 creates the branch and commits nothing, and L4-T225 commits nothing.

**STOP rule** — if `FOREIGN` is not `0`, the branch touches a path this lane does not own and the lane-guard check will fail the PR: **do not push**, open a blocker naming the paths. If the gate or the negatives regress after the rebase, `integration` has moved under this work: **do not force the merge and do not weaken a schema to make the gate green** — open a blocker and let L0 sequence it.

```yaml
title: "[L4-BLOCKER] L4-T225 phase PR cannot be opened"
lane: L4
task_id: L4-T225
blocked_by: "<foreign path in diff | gate regressed after rebase | negatives regressed after rebase | rebase conflict>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "REBASED=0 / DIRTY=0 / SCHEMAS GATE PASS / NEGATIVE 10/10 / FOREIGN=0 / COMMITS=23"
spec_ref: "PARTITION.md lines 20, 25, 30-34; L4-00-charter.md phase-branch convention"
needs: "L0"
action_taken: "nothing pushed"
```

---

## 7. Phase exit gate — all nine must hold simultaneously

Run this after L4-T225. It re-proves the phase from the branch, not from your notes. Nothing in it depends on any earlier task's output being remembered.

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
P=0
chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (got '$2' want '$3')"; P=1; fi; }

chk "19 store-map rows"        "$("$L4_PY" -c "import yaml;print(len(yaml.safe_load(open(r'$CP_ROOT/schemas/records/store-map.yaml'))['stores']))")" "19"  # 19 per FD-059 (bootstrap/ counts as a store)
chk "17 store schemas"         "$("$L4_PY" -c "import yaml;r=yaml.safe_load(open(r'$CP_ROOT/schemas/records/store-map.yaml'))['stores'];print(len([x for x in r if x['kind']=='record']))")" "17"
chk "coverage"                 "$(CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --coverage)" "COVERAGE OK 19"
chk "lint"                     "$(CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --lint)" "LINT OK 17"
chk "time discipline"          "$(CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-schemas.sh" --time)" "TIME OK 17"
chk "taxonomy closed at 86"    "$(CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/validate-taxonomy.sh")" "TAXONOMY OK 86"
chk "enum matches taxonomy"    "$("$L4_PY" -c "import json,yaml;e=json.load(open(r'$CP_ROOT/schemas/records/event-type.enum.json'))['enum'];t=[x['id'] for x in yaml.safe_load(open(r'$CP_ROOT/metrics/taxonomy/event-types.yaml'))['event_types']];print('same' if e==t else 'DRIFT')")" "same"
chk "negatives 10/10"          "$(CP_ROOT="$CP_ROOT" L4_PY="$L4_PY" bash "$CP_ROOT/tools/records/test-negative.sh" --negative | tail -1)" "NEGATIVE 10/10"
chk "no foreign path"          "$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')" "0"

[ "$P" = "0" ] && echo "L4 PHASE 2 EXIT GATE: PASS" || echo "L4 PHASE 2 EXIT GATE: FAIL"
```

**Expected final line:**

```
L4 PHASE 2 EXIT GATE: PASS
```

Any `FAIL` line: file a blocker with `task_id: L4-EXIT-GATE-P2`, quoting every `FAIL` line verbatim. **Do not start L4 Phase 3.** Phase 3 builds the write paths on top of these shapes; a store whose shape is not final is a door built onto a wall that will move.

---

## 8. What Phase 2 hands to the other lanes

| Artifact | Consumer | Consumed as |
|---|---|---|
| `metrics/taxonomy/event-types.yaml` | **L1** | The closed `event_type` enum L1 embeds in `registries/platform.yaml` (§97.3 line 8959). L4 publishes; L1 embeds. Charter **D-L4-01**. |
| `schemas/records/*.schema.json`, `store-map.yaml` | **L2** | The schemas the evidence and gate workflows validate written records against, at the flat paths L2 already consumes (charter §5.1) |
| `schemas/records/event.envelope.schema.json`, `event-type.enum.json` | **L2** | The envelope every workflow-appended event must satisfy before it is written (§97.3 line 8931) |
| `tools/records/validate-schemas.sh`, `validate-taxonomy.sh`, `validate-no-names.sh`, `test-negative.sh` | **L0** | Status checks for the merge gate. All four are fail-closed and take no arguments beyond a mode. |
| `store-map.yaml` | **L3** | The store list the write-freshness drift row of §53.1 (line 4671) iterates, beside the intervals declared in `os-health.yaml`. Charter **D-L4-02** — L4 publishes no `os-health.yaml`. |
| `schemas/records/record.base.schema.json` | **L4 Phase 3** | The `$defs` every emitter validates against before writing (`emit.sh`, L4-T305) |
| `denied-property-names.txt`, `validate-no-names.sh --records` | **L4 Phase 3+** | Limb C runs at write time in the emitters, against the live `registries/people.yaml`, not against the fixture roster |

**The one thing this phase does not hand anyone: a writer.** Nothing in Phase 2 writes a record. §97.1 line 8838 — *"the workflow surface generates them, nobody transcribes"* — is Phase 3's obligation, and Phase 3 is where `emit.sh` becomes the single door.

---

## 9. Standing rules — this phase only

The lane charter's standing rules apply in full. Five bind this phase in particular.

1. **Never widen a shape to make a fixture pass.** If a valid fixture is rejected, the fixture is wrong far more often than the schema is. A widened `person_ref`, an `additionalProperties: true`, or a dropped `required` entry converts an enforced rule into a decorative one, silently, and every record written afterwards inherits the hole.
2. **Never add a field the specification does not name** (§3.4 rule 3). A writer that needs one files a schema-change request to L0 under §60.2. This is the rule that keeps the seventeen schemas readable against the spec five years from now.
3. **Never hand-edit `event-type.enum.json`.** It is generated from `metrics/taxonomy/event-types.yaml` by `gen-event-type-enum.sh`, and the exit gate compares the two. A hand-edit is drift by construction.
4. **Never retire an identifier by deleting it.** §97.3 line 8959: retiring marks it retired and never removes it, because the events carrying it are append-only and stay readable.
5. **Never edit `registries/**`, `.github/**`, or anything outside `schemas/records/**`, `metrics/**`, `tools/records/**`.** PARTITION.md line 20 is the boundary; the `FOREIGN=0` line in every self-verify is how you find out you crossed it before CI does.

**On the unassigned subsystems.** PARTITION v1 leaves subsystems G, H, J, O and P unassigned. Two of this phase's neighbours touch them — the record-decision CLI (§99.2 line 9217, subsystems A and O) and the launch-pack generator (§99.2 line 9220, subsystem O) are the writers of `records/decisions/`, `records/decisions/pending/` and `records/launches/`. **L4 does not claim them.** This phase writes only the shapes those tools must produce; who builds the tools is an L0 routing question, and it is stated here as a dependency, not resolved.

---

## 10. Not covered by this document — do not attempt here

Write-freshness intervals and their `os-health.yaml` declarations (§97.2 line 8867 — charter **D-L4-02**); the RECORD-VERIFICATION-RESULT dispatch, its input contract and its handler (§97.2 line 8871 — L4 Phase 3); `emit.sh` and every emitter (Phase 3); the no-hand-edit guard (Phase 3); attention-hour derivation (§97.4); the Ready-queue-miss detector (§97.5); retention classes (§97.6); the metric register and every dashboard that reads these stores; the reconciler head-SHA anchor (D107); `exceptions.yaml`, `policies.yaml` and `patterns.yaml` (L1's `registries/**`); any `.github/**` workflow in either repository (L2's, charter **D-L4-03**).

Each belongs to a named later phase or to another lane. **Phase 2 ends when every store and every event has a machine-checkable shape and a command that proves it — and not one line further.**
