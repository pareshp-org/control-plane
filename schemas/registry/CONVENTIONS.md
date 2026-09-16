# Registry record conventions — effective dating and append-only

**Status:** binding from the first commit of this repository.
**Owner:** Lane 1 (Registries & Contracts), subsystems A and B of spec Section 99.2.
**Scope:** every file under `registries/**`, and every schema under
`schemas/registry/**` and `schemas/product/**` that validates one.

## 0. Why this file exists before anything else

Spec Section 99.4, item 1 of the minimal honest V1:

> Control-plane repository, schemas and CI validation — with effective dating and
> append-only discipline from the start, because retrofitting history is impossible
> by definition.

Spec Section 63.1 marks immutable history **Priority: P0 — retrofitting history is
impossible by definition**, and invariant 47 (Section 101.7) makes it
non-negotiable:

> History is append-only for state, decisions, approvals and records; records are
> not deleted and state changes are recorded, not overwritten.

## 1. The effective-dating mechanism

Section 63.1 states the mechanism exactly:

> **Mechanism:** state transitions with `start_date` and `end_date` — effective-dating,
> never in-place mutation — plus git history in the control-plane repository as the
> durable record. No separate audit database is introduced.

Therefore:

* **C1 — Dated fields are named `start_date` and `end_date`.** No synonym is
  permitted anywhere in `registries/**`: not `from`/`to`, not `valid_from`,
  not `effective_from`, not `since`. Section 7 uses `start_date` and `end_date`
  on every person record; Section 60.3 uses `deadline` for a migration target,
  which is a different concept and is not an effective-dating field.
* **C2 — `end_date` is always present, and `null` means open-ended.** An absent
  key is a malformed record, not an open interval. Section 7 writes
  `end_date: null` explicitly on an open-ended employee record.
* **C3 — `end_date` is mandatory and non-null for every non-employee.**
  Section 7.1: "`end_date` **is mandatory for every non-employee.** A CI check
  fails if a contractor, intern, temporary specialist or consultant has a null
  end date."
* **C4 — Dates are ISO-8601 calendar dates, `YYYY-MM-DD`.** Timestamps, where a
  registry carries one, are UTC with offset, per Section 97.1: "Every record and
  event timestamp is stored in UTC with its offset."
* **C5 — Business-day and working-hour rules never resolve against a runner's
  local clock.** Section 97.1: they resolve "against the declared working
  calendar and operating timezone held in the leave records (Section 6.4) —
  never against a runner's local time." Timezones in `registries/people.yaml`
  are IANA identifiers, never UTC offsets (Section 7 `work_arrangement.timezone`).

## 2. The append-only rules

Section 63.1 names what is never overwritten destructively:

> ownership, reviewer assignments, platform versions in use, product lifecycle
> state, assignments, approvals, policy text, exception records, classification
> and both criticality fields, domain membership.

Therefore:

* **A1 — Identifiers are stable and are never reused.** Section 63.1: "The system
  refuses to delete departed people and refuses to reuse identifiers." Section 7
  marks the person `id` "stable identifier, never reused". A validator enforces
  this; see `validators/registry/check-append-only.sh`.
* **A2 — A state change closes the old interval and opens a new one.** Set the
  old entry's `end_date`; add a new entry. Never edit a field of a closed
  interval in place.
* **A3 — Departure is a state, not a deletion.** Section 7.1: "A departed
  person's record is retained with `availability: departed` and
  `access_status: revoked` so that historical evidence — who approved what, who
  reviewed what — remains interpretable. Their identifier is never reused."
* **A4 — Corrections are follow-up entries, never in-place rewrites.** Section
  97.2 states this for records — "never edits in place (corrections are
  follow-up records)" — and Section 63.1 generalises the principle to "every
  operating-system record".
* **A5 — Git history is the audit trail.** No separate audit file, no changelog
  registry, no "history" block inside a registry file. Section 63.1 is explicit
  that git plus GitHub's audit log plus the deployment records already carry it.
* **A6 — No shared mutable index.** One entry per item; period and portfolio
  views are derived by aggregation, never by appending to a shared list file.
  Section 97.3 states the rule for events — "written as its own file, one file
  per event, never a concurrent append to a shared period file" — and it is why
  parallel work in this repository never contends for the same file.

## 3. Version fields

Section 60.2 fixes the version field per contract. The three this lane seeds in
Phase 1:

| Contract | File | Version field |
| --- | --- | --- |
| People Registry | `registries/people.yaml` | `registry_version` |
| Role Registry | `registries/roles.yaml` | `registry_version` |
| Event-type enum and platform record | `registries/platform.yaml` | `platform_version` |

* **V1 — A schema change writes v2 alongside v1; it never replaces v1.**
  Section 60.2: "Write the v2 schema alongside v1 — do not replace"; the
  validator supports both; v1 support is removed only after every consumer has
  migrated.
* **V2 — Simultaneous fleet migration is never required** (Section 60.2).

## 4. The telemetry carve-out

Section 63.1 and Section 97.6: append-only permanence applies to state,
decisions, approvals and records. Raw activity telemetry may be aggregated or
discarded after its declared diagnostic window, and retention classes are
declared in the control plane and owned by the Founder. Nothing in
`registries/**` is telemetry, so the carve-out never applies to a file this lane
owns.

## 5. What this file does NOT govern

* `records/**` and `events/**` live in the **`control-plane-records`** repository,
  not here (Section 52.6 row for `records/`/`events/`; Section 40.1, D89). Their
  envelopes carry `record_schema_version` and `event_schema_version`
  (Section 97.2, 97.3) and are owned by Lane 4.
* Layer B stores and the conduct-records store are never in any org-readable
  repository (Section 52.6, Section 90).
