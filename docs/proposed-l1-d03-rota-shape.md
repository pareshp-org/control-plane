# RESOLVED — per-product on-call rota shape for `people.yaml` (L1-D03 / REG-042)

> **STATUS: CONFIRMED by the Founder, 2026-09-16 (Option A).** Now being wired into
> `schemas/registry/people.registry.v1.schema.json`, `validators/registry/tests/`, and
> `validators/registry/fixtures/people/**` per this document.

## 1. The decision this answers

**Raised as:** `L1-D03` — `lanes/L1-05-tasks.md`, "DECISION REQUIRED — L1-D03 — Per-product rota
shape in `people.yaml` — **HARD BLOCK**" (§1, ~line 146). Blocks task `L1-311` (the coverage-window
rota rule, §47.9 / AT-047); every other Lane 1 task proceeds without it.

**Registered as:** `REG-042` — `lanes/L0-04-decisions-register.md` (~line 1390), "The per-product
rota shape in `people.yaml` — a hard block."

**What L0 must return** (REG-042's own wording): *"The exact YAML shape with field names for the
per-product rota block, and confirmation of whether `work_arrangement.accepted_coverage_window` is
retained, removed, or becomes a derived value."*

**The conflict driving it:** the person's `work_arrangement.accepted_coverage_window` (already live
in `schemas/registry/people.registry.v1.schema.json`) is a single, person-wide window. §47.9
separately requires that `people.yaml` carry, **per product**, the named rota members, each
member's accepted window, a paging-path identifier, and a funding decision record. Those are two
different shapes, and the spec names fields for the first only — the second needs field names
invented (`paging path`, `funding decision record`) and a decision on precedence between the two
shapes. REG-042 lists three options:

- **A** — per-product rota block on the person, `accepted_coverage_window` retained as the
  person-wide default/ceiling; two shapes, one overriding the other, validator states precedence.
- **B** — per-product rota block only, `accepted_coverage_window` derived from it.
- **C** — the rota lives on `product.yaml`, `people.yaml` carries only the window.

This proposal recommends **Option A** — see §2.

## 2. Recommended shape — Option A

- `work_arrangement.accepted_coverage_window` **is retained** on the person, unchanged, as the
  person-wide ceiling (this is the field already live in the schema and used as the fail-closed
  input elsewhere — nothing about it changes).
- A **new top-level array**, `rotas`, sibling to `people`, carries the per-product data §47.9
  requires. It does not touch `people[]` at all — a rota member is a *reference* to an existing
  `people[].id`, the same pattern `scope.products` already uses in reverse (a person referencing
  product ids).
- **Precedence rule for L1-311 to encode:** a person's entry in a `rotas[].members[]` block is the
  window that counts toward that product's §47.9 coverage-window union check. The person-wide
  `accepted_coverage_window` is the ceiling — a rota member's `accepted_window` must fall within
  their own `accepted_coverage_window`, never outside it. (This containment check is what REG-042's
  own decision note calls out: *"the validator enforces containment."*)

This keeps `people[]` exactly as already schema'd and shipped, adds one new optional array, and
gives §47.9's three unnamed concepts (per-product rota, paging path, funding decision record) fields
of their own — same shape of change L1-D02 already used for the capability vocabulary (extend, do
not replace).

Why not B or C: B would make the person-wide window computed rather than declared, which conflicts
with it being a validated ceiling elsewhere in the schema; C would move rota data out of
`people.yaml`, and §47.9 explicitly puts it there.

## 3. Field-by-field shape

### 3.1 New top-level field

| Field | Type | Required | Notes |
|---|---|---|---|
| `rotas` | array of *rota* | no (optional array; existing files with no on-call product need not add it) | sibling of `people`; same file, `registries/people.yaml` |

### 3.2 `rotas[]` (*rota*)

| Field | Type | Required | Notes |
|---|---|---|---|
| `product` | string, `$ref common#/$defs/stableId` | yes | the product id this rota covers; same id type `scope.products[]` already uses |
| `members` | array of *rota member*, `minItems: 1` | yes | |

### 3.3 `rotas[].members[]` (*rota member*)

| Field | Type | Required | Notes |
|---|---|---|---|
| `person` | string, `$ref common#/$defs/stableId` | yes | must resolve to a `people[].id` (a new residual/referential rule, same family as the existing `role` → `roles.yaml` check) |
| `accepted_window` | object | yes | shape below — the member's accepted coverage window **for this product** |
| `paging_path` | string, `minLength: 1` | yes | names §47.9's "paging-path identifier" — e.g. an alerting-tool routing key. Free string in this proposal; see open question 2 |
| `funding_decision_record` | string, `minLength: 1` | yes | names §47.9's "funding decision record" — the id of the decision that funded this rota seat. Free string in this proposal; see open question 3 |

### 3.4 `accepted_window` (member window, per product)

| Field | Type | Required | Notes |
|---|---|---|---|
| `days` | array of weekday token, `minItems: 1`, `uniqueItems: true` | yes | enum `mon`..`sun` — see open question 1 |
| `start` | string, `$ref common#/$defs/hhmm` | yes | same `HH:MM` pattern already used everywhere else (`work_arrangement.schedule`, `accepted_coverage_window`) |
| `end` | string, `$ref common#/$defs/hhmm` | yes | |
| `timezone` | string, `$ref common#/$defs/ianaTimezone` | yes | IANA identifier, same rule as `work_arrangement.timezone` — never a UTC offset |

## 4. Illustrative schema fragment (NOT applied to the live file)

This is how the addition would slot into `schemas/registry/people.registry.v1.schema.json` if the
Founder confirms — added as a new top-level property, alongside the untouched `people` property:

```jsonc
{
  "properties": {
    "registry_version": { "const": 1 },
    "people": { /* … unchanged … */ },

    "rotas": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["product", "members"],
        "properties": {
          "product": { "$ref": "common/defs.v1.schema.json#/$defs/stableId" },
          "members": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["person", "accepted_window", "paging_path", "funding_decision_record"],
              "properties": {
                "person": { "$ref": "common/defs.v1.schema.json#/$defs/stableId" },
                "accepted_window": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": ["days", "start", "end", "timezone"],
                  "properties": {
                    "days": {
                      "type": "array",
                      "minItems": 1,
                      "uniqueItems": true,
                      "items": {
                        "type": "string",
                        "enum": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                      }
                    },
                    "start": { "$ref": "common/defs.v1.schema.json#/$defs/hhmm" },
                    "end": { "$ref": "common/defs.v1.schema.json#/$defs/hhmm" },
                    "timezone": { "$ref": "common/defs.v1.schema.json#/$defs/ianaTimezone" }
                  }
                },
                "paging_path": { "type": "string", "minLength": 1 },
                "funding_decision_record": { "type": "string", "minLength": 1 }
              }
            }
          }
        }
      }
    }
  }
}
```

`registry_version` stays `const: 1` and `required: ["registry_version", "people"]` is unchanged —
`rotas` is additive and optional, so no existing valid `people.yaml` (including every fixture under
`validators/registry/fixtures/people/**`) breaks.

## 5. One worked example (NOT applied to `registries/people.yaml`)

Built on the existing valid fixture style (`validators/registry/fixtures/people/valid/employee_full/people.yaml`),
showing an unchanged person plus the new `rotas` block covering a 24×7 product with two members
whose windows jointly cover the week:

```yaml
registry_version: 1
people:
  - id: alice-dev
    display_name: "Alice Developer"
    github_login: alice-dev
    role: developer
    employment_type: employee
    capabilities: [code-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: "2024-01-15"
    end_date: null
    work_arrangement:
      timezone: "Asia/Kolkata"
      arrangement: hybrid
      schedule:
        mon: {start: "09:00", end: "17:00"}
        tue: {start: "09:00", end: "17:00"}
        wed: {start: "09:00", end: "17:00"}
        thu: {start: "09:00", end: "17:00"}
        fri: {start: "09:00", end: "17:00"}
      fte: 1
      public_holiday_set: "IN-national"
      accepted_coverage_window: {days: 5, start: "09:00", end: "17:00", timezone: "Asia/Kolkata"}
    scope:
      products: [alpha, beta]
      repositories_only: false

  - id: bob-ops
    display_name: "Bob Ops"
    github_login: bob-ops
    role: developer
    employment_type: employee
    capabilities: [incident-response]
    ai_runtime: null
    availability: active
    access_status: provisioned
    start_date: "2023-06-01"
    end_date: null
    work_arrangement:
      timezone: "America/New_York"
      arrangement: remote
      schedule:
        sat: {start: "10:00", end: "18:00"}
        sun: {start: "10:00", end: "18:00"}
      fte: 0.2
      public_holiday_set: "US-national"
      accepted_coverage_window: {days: 2, start: "10:00", end: "18:00", timezone: "America/New_York"}
    scope:
      products: [alpha]
      repositories_only: false

# --- proposed addition ---
rotas:
  - product: alpha
    members:
      - person: alice-dev
        accepted_window:
          days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "17:00"
          timezone: "Asia/Kolkata"
        paging_path: "pagerduty:alpha-primary"
        funding_decision_record: "FD-112"
      - person: bob-ops
        accepted_window:
          days: [sat, sun]
          start: "10:00"
          end: "18:00"
          timezone: "America/New_York"
        paging_path: "pagerduty:alpha-weekend"
        funding_decision_record: "FD-112"
```

Each member's `accepted_window` here sits inside (is no wider than) that same person's
`work_arrangement.accepted_coverage_window` — the containment rule §2 describes.

## 6. Open questions flagged for the Founder (not resolved by this proposal)

1. **`days` shape mismatch with the live schema.** The live `accepted_coverage_window.days` field
   (in `schemas/registry/people.registry.v1.schema.json`) is a bare **integer** (a day *count*, e.g.
   `5`), which cannot express *which* days — and §47.9's union-of-windows check (AT-047, task
   `L1-311`) needs to know which days each member covers to compute a union. This proposal uses an
   explicit weekday-token array (`mon`..`sun`) for the new `accepted_window.days` instead, matching
   the day-key convention `work_arrangement.schedule` already uses. If the Founder wants the two
   `days` fields to share one shape, the person-side `accepted_coverage_window.days` would need the
   same change — a second, separate decision, not made here.
2. **`paging_path` — free string or a closed reference?** This proposal leaves it an unconstrained
   `minLength: 1` string (e.g. a PagerDuty/Opsgenie routing key). An alternative is validating it
   against a registered set of paging destinations, if one exists or is planned in `tools.yaml`
   or `platform.yaml`. Not decided here.
3. **`funding_decision_record` — free string or a pattern?** This repo already carries a
   `decisionRecordId` `$def` in `schemas/registry/common/defs.v1.schema.json`
   (pattern `^DEC-\d{4}-\d{3,}$`), but the decision ids actually used throughout this repo's own
   records are `FD-###` / `D###` (e.g. `FD-112`, `D112`), which that pattern does not match. This
   proposal leaves `funding_decision_record` an unconstrained string rather than picking a pattern
   that contradicts the ids already in use — the Founder should say which id scheme (if any) is
   authoritative.

## 7. A cross-reference the Founder should see before ruling

A **different, earlier design pass already exists in this repository** and reaches the same shape:
`lanes/L1-02-schemas.md`, task T03 (~line 657–884), works out a `rotas[]` block on `people.yaml`
with the identical field names used here — `product`, `members[].person`, `members[].accepted_window`,
`members[].paging_path`, `members[].funding_decision_record` — under the same citation, §47.9/§52.6.
Two decision-tracking files already record this as settled:

- `_DECISION_DOCKET.md` (row `REG-042`): *"**A** — retain `work_arrangement.accepted_coverage_window`
  as the person's ceiling; add per-person `rota: [{product, accepted_window, paging_path,
  funding_decision_record}]`… Session 13 — no Founder required."*
- `_DECISION_SIGNOFF.md` (row `REG-042`): *"**A** — person-wide window as ceiling, per-product rota
  block, validator enforces containment… Only field naming was open."*
- `_DECISION_DOCKET.md` §4.5 edit-list note for `L1-02-schemas.md`: *"T03's rota shape is the
  **ratified** answer to REG-042 and stands."*

**This proposal was built independently from `L1-D03`/`REG-042` and the live schema/fixture
conventions, and it converges on the same shape** (Option A; the same three new field names). That
convergence is a useful sanity check, but it is **not** a substitute for the Founder's own sign-off
here: `lanes/L1-05-tasks.md` still shows `L1-D03` as an open **HARD BLOCK** and the live
`schemas/registry/people.registry.v1.schema.json` still has no `rotas` field, so whatever those two
decision-tracking files say, nothing has actually shipped. If the Founder confirms this shape, the
`_DECISION_DOCKET.md` / `_DECISION_SIGNOFF.md` rows and `lanes/L1-05-tasks.md`'s HARD BLOCK banner
should all be updated in the same pass so the register and the task table stop disagreeing with
each other.

## 8. What happens after Founder confirmation (not done by this proposal)

Once confirmed (with or without changes to §6's open questions), wiring this in is:

1. Add the `rotas` property and its `$defs` to `schemas/registry/people.registry.v1.schema.json`.
2. Add `validators/registry/tests/test_people_schema.py` cases for the new block (valid rota,
   missing `paging_path`, missing `funding_decision_record`, member `person` not in `people[]`,
   member window not contained in the person's `accepted_coverage_window`).
3. Add fixtures under `validators/registry/fixtures/people/**` mirroring the existing naming
   convention (e.g. `valid/rota_present`, `rota_member_unknown_person`, `rota_window_not_contained`).
4. Unblock and implement task `L1-311` (`validators/registry/rules/r_prd_11.py`) against this shape.
5. Update `_DECISION_DOCKET.md`, `_DECISION_SIGNOFF.md`, and `lanes/L1-05-tasks.md`'s `L1-D03`
   banner to point at the confirmed version of this document rather than disagreeing with it.

None of these five steps are taken by this proposal.
