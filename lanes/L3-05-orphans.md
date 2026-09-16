> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3-05 — PHASE 5: ORPHAN AND EXPIRY DETECTION

> **REFERENCE ONLY** — FD-098 (2026-09-09): Task bodies superseded by L3-06-tasks.md. This file is a design-note reference. Do not execute task bodies from this file.

**Lane:** L3 Reconciler & Provisioning (subsystems C and D, spec Section 99.2, lines 9190 and 9191)
**Branch prefix:** `lane/3/*` · **Merge target:** `integration` · **Merge-train position:** 4th (L1 → L4 → L2 → L3 → L5)
**Owned paths used by this phase:** `reconciler/**` only. This phase writes nothing outside `reconciler/`.
**Repository:** `control-plane`

---

## 0. Why this phase is written defensively

Section 99.6 risk 6 (spec line 9282) states: *"Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system"*, mitigated by *"Detect-only first; repair classes enabled one at a time"*.

Section 99.4 item 6 (line 9257) and Section 98.2 Phase 3 (line 9043) both scope reconciliation v0 to **detect and block only**, naming *"expiry revocation, protection drift, and orphan detection"* and explicitly deferring auto-repair.

Therefore, binding for every task in this phase:

> **No module written in this phase performs, or is capable of performing, a write against GitHub or any network endpoint.** Detection produces findings. Expiry produces a *revocation plan* — a data structure. Execution of that plan belongs to the reconciler apply layer (subsystem C), never to code in `reconciler/orphans/**` or `reconciler/expiry/**`. This is enforced by an automated test (task `L3-05-28`), not by discipline.

Second binding rule, from Section 97.2 (line 8860, write-freshness rationale — *a store whose write step fails silently renders every count-shaped derived metric as zero, which is indistinguishable from health*):

> **A detector that cannot read its input never returns "no orphans".** It returns `status: "input_unavailable"` with the missing input named. Silence must never read as health.

---

## 1. Count reconciliation: fourteen vs sixteen

The phase brief says "fourteen orphan types". The spec is the authority and it says **sixteen**:

| Spec location | Exact text |
| --- | --- |
| Line 990 | `**Orphan detection — what the system surfaces** (16 orphan types):` |
| Lines 992–1010 | A sixteen-row table |
| Line 988 | *"Expiry with open gate-relevant work … is the **fourteenth** orphan type below."* |
| Line 9769 (EC-111) | *"The fourteenth orphan type (High)"* |

"Fourteenth" is the **row index** of the temporary-person-expiry type inside a sixteen-row table, not a total. This phase implements **all sixteen rows** with the severities exactly as printed. No orphan type is invented and none is dropped.

---

## 2. FROZEN FACTS — the sixteen orphan types

Transcribed verbatim from spec Section 12.2, lines 992–1010. The `Detection` and `Severity` columns are copied literally; `Orphan type ID` and `Subject format` are this phase's stable identifiers and are frozen here so no executor ever chooses one.

| # | Orphan type ID | Spec "Orphan type" | Spec "Detection" | Spec "Severity" | Subject format | Task |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `ORPH-PRIMARY-OWNER` | Product with no Primary Owner | Assignment registry | **Blocking** | `product:<id>` | `L3-05-05` |
| 2 | `ORPH-CROSS-REVIEWER` | Product with no Cross-Reviewer | Assignment registry | **Blocking** | `product:<id>` | `L3-05-06` |
| 3 | `ORPH-BACKUP-OWNER` | Product with no Backup Owner | Assignment registry | High | `product:<id>` | `L3-05-07` |
| 4 | `ORPH-PRIMARY-RESPONDER` | Product with no Primary Responder | Contract operations block | **Blocking** | `product:<id>` | `L3-05-08` |
| 5 | `ORPH-SHARED-SERVICE` | Shared service with no owner | Service registry | **Blocking** | `service:<id>` | `L3-05-09` |
| 6 | `ORPH-CERTIFICATE` | Certificate with no owner | Asset inventory | High | `asset:<id>` | `L3-05-10` |
| 7 | `ORPH-DOMAIN` | Domain with no owner | Asset inventory | **Blocking** | `asset:<id>` | `L3-05-11` |
| 8 | `ORPH-VENDOR` | Vendor relationship with no owner | Asset inventory | Medium | `asset:<id>` | `L3-05-12` |
| 9 | `ORPH-ASSET` | Operational asset with no owner | Asset inventory | Medium | `asset:<id>` | `L3-05-13` |
| 10 | `ORPH-COMMITMENT` | Customer commitment with no owner | Contract operations block | **Blocking** | `commitment:<product-id>/<customer-ref>` | `L3-05-14` |
| 11 | `ORPH-PLATFORM-MIGRATION` | Platform migration with no owner | Compatibility state | High | `migration:<product-id>` | `L3-05-15` |
| 12 | `ORPH-VERIFICATION` | Verification responsibility unassigned | Assignment registry | High | `product:<id>` | `L3-05-16` |
| 13 | `ORPH-H1-WORK` | In-flight H1 work with no assignee | Board | High | `board-item:<id>` | `L3-05-17` |
| 14 | `ORPH-TEMP-EXPIRY-OPEN-WORK` | Temporary person expired with open gate-relevant work | Assignment registry + open reviews and gate items at expiry | High | `person:<id>` | `L3-05-18` |
| 15 | `ORPH-POLICY` | Policy with no owner | Policy register | **Blocking** | `policy:<id>` | `L3-05-19` |
| 16 | `ORPH-EXCEPTION` | Open exception whose requester or authority has departed | Exception registry | High | `exception:<id>` | `L3-05-20` |

Severity tally, asserted by test in `L3-05-21`: **Blocking = 7** (#1, 2, 4, 5, 7, 10, 15) · **High = 7** (#3, 6, 11, 12, 13, 14, 16) · **Medium = 2** (#8, 9).

The only permitted severity strings are the three literals `Blocking`, `High`, `Medium`. They are the Section 12.2 vocabulary and are **not** the four-value drift scale of Section 6.7 (line 474: Green, Amber, Red, Blocking). Do not map between them. The single mapping this phase implements is the one the spec states outright: Section 53.2 line 4697 places *"orphaned product"* under **Level 4 — Block**, so a `Blocking` orphan blocks (exit code 2). `High` and `Medium` orphans are reported only; any further response-level mapping is out of scope for this phase per Section 99.4 item 6 ("orphan detection at blocking severity").

---

## 3. FROZEN FACTS — the other rules this phase implements

| Rule | Spec anchor | Exact text (abridged) |
| --- | --- | --- |
| Prospective detection at `departing` | Section 12.2, line 985 | *"Orphan detection runs immediately when `availability` becomes `departing`, in prospective mode against the declared `end_date`: it emits the transfer worklist — every responsibility that would orphan on that date"* |
| Blocking orphans cannot be dismissed | Section 12.2, line 1011 | *"Blocking orphans appear on the Founder View's product attention dimension as Action Required and cannot be dismissed without resolution"* |
| Same, as invariant | Section 101.8, invariant **57**, line 9528 | *"Departures trigger orphan detection, and blocking orphans cannot be dismissed unresolved."* |
| Same, as acceptance test | **AT-017**, line 9326 | *"orphan detection surfaces every unowned responsibility; blocking orphans cannot be dismissed unresolved"* |
| Temporary assignments expire without humans | Section 101.8, invariant **58**, line 9529 | *"Temporary assignments carry a mandatory end date and expire without human action."* |
| Automatic expiry revocation | Section 12.4, line 1052 (`Expiry` row) | *"Reconciliation revokes access on the date. No human action required"* |
| Same, as acceptance tests | **AT-008** (9312), **AT-018** (9327), **AT-036** (9358), **AT-037** (9359) | AT-037: *"An exception that cannot be auto-revoked becomes Blocking drift on its expiry date"* |
| Exception auto-revocation scope | Section 54.2, line 4789 | *"Temporary access, temporary assignments and platform compatibility waivers are revoked or reverted by reconciliation at expiry, not by memory. Where automatic revocation is not possible, the exception becomes Blocking-class drift on its expiry date."* |
| **14-day** delegation expiry warning | Section 10.1, line 787 | *"Every delegation-type assignment receives a 14-day advance expiry warning in the daily expiry check, exactly as expiring assets do (Section 49)."* |
| **T-minus-7** temporary-person warning | Section 12.4, line 1057 | *"Reconciliation emits a T-minus-7-day expiry warning to the sponsor, listing the person's open pull requests and open reviews, so expiry never strands in-flight work."* |
| Same, per edge case | **EC-111**, line 9769 | *"Orphan detection warns the assignment's sponsor at T-minus-7 days"* |
| Reconciliation cadence | Section 94.7, line 8556 | *"Reconciliation | Nightly and on registry change | Drift, expiry, orphan detection"* |
| Suspension does **not** orphan | Section 88 note, line 7769 | *"Ownership and coverage effects of a suspension … are handled by the normal succession and delegation mechanisms of Sections 13 and 17, **without those surfaces disclosing the reason**"* |
| Departure is a state, not a deletion | Section 7.1, line 609 | *"A departed person's record is retained with `availability: departed` and `access_status: revoked`"* |
| Health signal fed | **SIG-05**, line 4534 | *"Orphan risk | Any product with no active Primary Owner, no active Cross-Reviewer, or no named responder | Registries | Blocking | Team Lead"* |
| Events emitted (payloads only) | Section 97.3, line 8952 | `orphan detected` · `orphan resolved` · `delegation expiry warning issued` · `temporary-person expiry warning issued` |
| Event **writing** is not this lane | Section 97.1, line 8840 (D89) | *"Workflow-written records and events land in the records repository through the records-writer machine credential … scoped to that repository alone and reaches no registry at all"* |

**Event boundary.** This phase produces event *payload files* on local disk. It never writes to the records repository. `control-plane-records` is owned exclusively by L4 (PARTITION.md line 20) and the write path is the records-writer credential from a workflow (L2). Any task tempted to write an event is out of bounds.

---

## 4. Registry field facts (so no executor guesses a field name)

Copied from the spec so detection queries are literal.

| Source | Path convention | Fields this phase reads | Spec anchor |
| --- | --- | --- | --- |
| People registry | `people.yaml` | `people[].id`, `.employment_type`, `.availability` (`active｜on_leave｜departing｜departed`), `.access_status` (`pending｜provisioned｜suspended｜revoked`), `.start_date`, `.end_date`, `.sponsor`, `.scope` | Section 7, lines 552–600 |
| Product contract | `products/<id>/product.yaml` | `identity.id`, `platform_compatibility`, `assignments[].person/.type/.start_date/.end_date`, `operations.primary_responder`, `operations.backup_responder`, `operations.triager`, `commitments[].customer`, `platform_migration.owner/.deadline/.target_contract_version` | Section 15.1 lines 1292–1535; Section 60.3 lines 5195–5202 |
| Shared service | `shared-services/<id>/service.yaml` | `identity.id`, `assignments[].person/.type` | Section 20.1, lines 2035–2072 |
| Policy register | `policies.yaml` | `policies[].id`, `.owner`, `.status` | Section 55.1, lines 4836–4870 |
| Exception registry | `exceptions.yaml` | `exceptions[].id`, `.type`, `.requester`, `.authority`, `.expiry`, `.closure` | Section 54.1, lines 4753–4788 |
| Asset inventory | **see `DR-L3-05-A`** — Closed. Producer: L5 | entry id, owner, type, expiry | Section 49.1, lines 4340–4353; Section 52.6 registry row |
| Board (H1 items) | **see `DR-L3-05-C`** — Closed. Producer: L4 | item id, assignee, column/flag | Section 29.1–29.2, lines 2625–2650 |
| Open gate-relevant work | **see `DR-L3-05-D`** — Closed. Producer: L4 | open reviews / verification items / approvals by holder | Section 12.2 line 988; EC-111 line 9769 |

Assignment type tokens used by this phase, all from the seventeen-row table at Section 10.1 lines 767–786: `primary_owner`, `cross_reviewer`, `backup_owner`, `verification_responsibility`, `incident_responder`, `temporary_contributor`, `security_reviewer`, `production_approval_delegate`, `plan_approval_delegate`, `incident_coordination_delegate`, `founder_decision_delegate`, `registry_owner_delegate`, `verification_delegate`, `cross_review_shadow`, `mentor`, `architecture_responsibility`, `domain_lead`.

---

## 5. DECISION REQUIRED — five items for L0

Each blocks named tasks. **An executor reaching a blocked task with no answer recorded STOPS and opens the blocker issue.** L0 answers on the blocker issue; the executor pastes the literal answer into `reconciler/orphans/decisions.py` (task `L3-05-02` creates that file with every constant set to `None` and a module-level docstring naming the five decisions).

> ### DECISION REQUIRED — `DR-L3-05-A` — Operational asset inventory location and type vocabulary
> **Blocks:** `L3-05-10`, `L3-05-11`, `L3-05-12`, `L3-05-13` (orphan types 6, 7, 8, 9).
> **Why it cannot be decided in-lane:** Section 49.1 (lines 4340–4353) and the Section 52.6 control-plane file registry both name the artifact *"Operational asset inventory"* and state that *"Each entry carries an expiry date, a named owner, and an alert threshold of at least 30 days"* — but neither states a **filename**, a **schema**, or a **type vocabulary**. Orphan types 6–9 require distinguishing a certificate from a domain from a vendor relationship from any other operational asset, and that distinction has no spec-given field.
> **L0 must supply, verbatim:** (a) the path of the asset inventory file(s) relative to the control-plane repository root; (b) the YAML key holding the list of entries; (c) the key holding each entry's stable id; (d) the key holding each entry's owner (a `people.yaml` id); (e) the key holding each entry's type, and the exact literal value(s) that mean *certificate*, *domain*, *vendor relationship*, and the rule for *everything else*.
> **Constants to fill:** `ASSET_INVENTORY_PATHS`, `ASSET_ENTRIES_KEY`, `ASSET_ID_KEY`, `ASSET_OWNER_KEY`, `ASSET_TYPE_KEY`, `ASSET_TYPE_CERTIFICATE`, `ASSET_TYPE_DOMAIN`, `ASSET_TYPE_VENDOR` in `reconciler/orphans/decisions.py`.
> **Note for L0:** the asset inventory is data owned by lane L5 (`assets/**`, PARTITION.md line 21). L3 reads it by path; L3 must not import L5 source (PARTITION.md rule 4).

> ### DECISION REQUIRED — `DR-L3-05-B` — Which assignment types are "delegation-type"
> **Blocks:** `L3-05-26` (the 14-day warning).
> **Why it cannot be decided in-lane:** Section 10.1 line 787 requires *"Every delegation-type assignment receives a 14-day advance expiry warning"* but the seventeen-row table above it never labels a row "delegation-type". Candidate rows carry three different expiry phrasings — *"Yes, mandatory `end_date`"*, *"Yes, on `end_date`"*, *"Yes, if dated"*, *"Optional; reviewed quarterly"* — and choosing among them is interpretation.
> **L0 must supply, verbatim:** the exact list of `assignments[].type` tokens (drawn from the Section 10.1 table) that receive the 14-day warning.
> **Constant to fill:** `DELEGATION_WARNING_TYPES` in `reconciler/orphans/decisions.py`.

> ### DECISION REQUIRED — `DR-L3-05-C` — Board snapshot source and shape for H1 items
> **Blocks:** `L3-05-17` (orphan type 13).
> **Why it cannot be decided in-lane:** Section 12.2's Detection column for this row is *"Board"*. Boards live in the designated work-management system (Section 29.1, line 2625), not in a control-plane YAML file, and Section 99.5 leaves the board shape as *"the single org-level Project with a product field is the default; per-product Projects with aggregation are the upgrade"*. There is no spec-given file for the reconciler to read.
> **L0 must supply, verbatim:** (a) the path of the board snapshot file the reconciler reads, relative to the control-plane repository root, and its format (`json` or `yaml`); (b) the key holding the item list; (c) the keys holding item id, assignee, column and Blocked flag; (d) the exact literal column values that constitute H1 per Section 29.2 line 2645 (*"Planned, In Progress, In Review, Verify — plus the Deploy pipeline stage and any item carrying the Blocked flag"*); (e) confirmation of which lane produces the snapshot.
> **Constants to fill:** `BOARD_SNAPSHOT_PATH`, `BOARD_SNAPSHOT_FORMAT`, `BOARD_ITEMS_KEY`, `BOARD_ITEM_ID_KEY`, `BOARD_ASSIGNEE_KEY`, `BOARD_COLUMN_KEY`, `BOARD_BLOCKED_KEY`, `BOARD_H1_COLUMNS` in `reconciler/orphans/decisions.py`.

> ### DECISION REQUIRED — `DR-L3-05-D` — "Open gate-relevant work" input surface
> **Blocks:** `L3-05-18` (orphan type 14), `L3-05-27` (T-minus-7 warning payload).
> **Why it cannot be decided in-lane:** Section 12.2 line 988 defines the condition as *"an unfinished security review, an open review or verification item that a gate is waiting on"*; EC-111 (line 9769) as *"a review, verification judgment or approval they hold is still open"*; Section 12.4 line 1057 requires the warning to list *"the person's open pull requests and open reviews"*. All of these live on the live GitHub surface, and this phase is forbidden from making network calls (§0). A snapshot file is required and the spec names none.
> **L0 must supply, verbatim:** (a) the path and format of the open-gate-item snapshot the reconciler reads; (b) the key holding the item list; (c) the keys holding item id, holder (a `people.yaml` id), kind, and product; (d) the exact literal `kind` values that count as gate-relevant; (e) confirmation of which lane produces the snapshot.
> **Constants to fill:** `OPEN_WORK_SNAPSHOT_PATH`, `OPEN_WORK_SNAPSHOT_FORMAT`, `OPEN_WORK_ITEMS_KEY`, `OPEN_WORK_ID_KEY`, `OPEN_WORK_HOLDER_KEY`, `OPEN_WORK_KIND_KEY`, `OPEN_WORK_PRODUCT_KEY`, `OPEN_WORK_GATE_RELEVANT_KINDS` in `reconciler/orphans/decisions.py`.

> ### DECISION REQUIRED — `DR-L3-05-E` — How a customer commitment's owner resolves
> **Blocks:** `L3-05-14` (orphan type 10).
> **Why it cannot be decided in-lane:** Section 12.2 gives the Detection source as *"Contract operations block"*, but the commitments schema (Section 21.1, lines 2123–2148, and Section 15.1, lines 1512–1535) contains **no `owner:` field** on a commitments entry. The operations block (Section 15.1, lines 1481–1495) contains `triager`, `primary_responder`, `backup_responder` and `intake_channel`, and Section 21.4's last row mentions *"a named backup communicator recorded in the entry"* for one specific case only. Selecting which field carries commitment ownership is interpretation.
> **L0 must supply, verbatim:** the ordered resolution rule — which `operations` key (or which commitments-entry key) names the responsible person for a commitments entry, and what the fallback is when it is absent.
> **Constants to fill:** `COMMITMENT_OWNER_RESOLUTION` (an ordered tuple of dotted key paths) in `reconciler/orphans/decisions.py`.

---

## 6. Conventions binding on every task

### 6.1 Toolchain (fixed — do not choose)

Python 3.12, `PyYAML==6.0.2`, `pytest==8.3.3`. No other third-party dependency may be added by this phase. Standard library only, plus those two.

### 6.2 Working directory

Every fenced command runs from the **root of the `control-plane` checkout**. Establish it once per session:

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
pwd
```

If `$CONTROL_PLANE` is unset, set it to the absolute path of your `control-plane` checkout before starting. Every path in this document is relative to that root.

### 6.3 Standard git block (identical in every task; `<slug>` and `<Tnn>` differ)

```bash
set -euo pipefail
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/05-<slug>
```

…work…

```bash
set -euo pipefail
git add reconciler
git status --porcelain
git commit -m "L3-05-<Tnn>: <task title>"
git push -u origin lane/3/05-<slug>
gh pr create --base integration --head lane/3/05-<slug> \
  --title "L3-05-<Tnn> <task title>" \
  --body "Lane L3, Phase 5 (orphan and expiry detection). Task L3-05-<Tnn>. Spec: Section 12.2 (lines 948-1011)."
```

### 6.4 Lane-guard self-check (run before every `git push`, in every task)

```bash
set -euo pipefail
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
```

Expected output: `LANE-GUARD OK`. Any other output is a STOP condition — see §6.6.

### 6.5 Full test command (used by every SELF-VERIFY)

```bash
set -euo pipefail
python -m pytest reconciler/tests -q
```

### 6.6 Blocker-issue template (used by every STOP rule)

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L3-05-<Tnn>: <one-line symptom>" \
  --label "blocker,lane-3,phase-5" \
  --body "$(cat <<'EOF'
TASK: L3-05-<Tnn>
LANE: L3 (Reconciler & Provisioning)
PHASE: 5 - Orphan and expiry detection
BRANCH: lane/3/05-<slug>

STOP TRIGGER (verbatim, from the task's STOP rule):
<paste the trigger sentence>

COMMAND RUN:
<paste the exact command>

OBSERVED OUTPUT:
<paste output, unedited>

EXPECTED OUTPUT (from the task's SELF-VERIFY block):
<paste expected>

DECISION REQUIRED ID (if any): <DR-L3-05-A|B|C|D|E|none>

WHAT I DID NOT DO: I did not guess, did not change any path outside reconciler/,
did not modify contracts/, and did not push.
EOF
)"
```

After opening the issue: `git stash` any uncommitted work, leave the branch in place, and stop. Do not continue to the next task.

### 6.7 Frozen output vocabulary

These literals appear in golden fixture files and must match byte-for-byte.

| Concept | Frozen value |
| --- | --- |
| Severity strings | `Blocking`, `High`, `Medium` |
| Detector status | `ok`, `input_unavailable` |
| Run modes | `current`, `prospective` |
| Date format everywhere | ISO 8601 date, `YYYY-MM-DD` |
| CLI exit code — clean | `0` |
| CLI exit code — at least one `Blocking` finding in `current` mode | `2` (Section 53.2 Level 4 — Block, line 4697) |
| CLI exit code — at least one detector `input_unavailable` | `3` |
| CLI exit code — internal error | `1` |
| Exit-code precedence when several apply | `1` > `3` > `2` > `0` |

### 6.8 Holder predicate (defined once, in `L3-05-02`; used by fourteen detectors)

`holder_state(person_id, ctx, as_of, mode) -> "held" | "vacant"`, evaluated in this exact order:

1. `person_id` is `None`, empty, or absent from `people.yaml` → `vacant`.
2. `availability == "departed"` → `vacant`.
3. `access_status == "revoked"` → `vacant`.
4. `mode == "prospective"` **and** `availability == "departing"` **and** `end_date` is not null **and** `end_date <= as_of` → `vacant`.
5. `mode == "prospective"` **and** `end_date` is not null **and** `end_date <= as_of` → `vacant`.
6. `access_status == "suspended"` → **`held`** — a suspension must not surface as an orphan, per line 7769.
7. `availability == "on_leave"` → `held`.
8. Otherwise → `held`.

`assignment_in_force(a, as_of) -> bool`: `(a.start_date is None or a.start_date <= as_of) and (a.end_date is None or a.end_date >= as_of)`.

`active_holders(assignments, type_token, ctx, as_of, mode) -> list[str]`: the `person` of every assignment where `a.type == type_token`, `assignment_in_force(a, as_of)`, and `holder_state(a.person, ...) == "held"`.

**No lifecycle filter.** Section 12.2 attaches no `identity.lifecycle` qualifier to any orphan row, so no detector filters by lifecycle. Do not add one.

**Referential integrity is not this phase's job.** An assignment naming a person absent from `people.yaml` is an L1 registry-validator failure (Section 99.2 subsystem B, line 9188). Here it merely evaluates to `vacant`.

---

## 7. Task table

| Task ID | Title | Size | Depends on | DR block |
| --- | --- | --- | --- | --- |
| `L3-05-01` | Preflight: environment, toolchain and phase preconditions | S | — | — |
| `L3-05-02` | Finding model, severity enum, detector registry, decisions module | M | `T01` | — |
| `L3-05-03` | Control-plane loader with input-availability guard | M | `T02` | — |
| `L3-05-04` | Fixture harness and golden-case layout | M | `T03` | — |
| `L3-05-05` | Detector 1 — `ORPH-PRIMARY-OWNER` (Blocking) | S | `T04` | — |
| `L3-05-06` | Detector 2 — `ORPH-CROSS-REVIEWER` (Blocking) | S | `T04` | — |
| `L3-05-07` | Detector 3 — `ORPH-BACKUP-OWNER` (High) | S | `T04` | — |
| `L3-05-08` | Detector 4 — `ORPH-PRIMARY-RESPONDER` (Blocking) | S | `T04` | — |
| `L3-05-09` | Detector 5 — `ORPH-SHARED-SERVICE` (Blocking) | S | `T04` | — |
| `L3-05-10` | Detector 6 — `ORPH-CERTIFICATE` (High) | S | `T04` | `DR-A` |
| `L3-05-11` | Detector 7 — `ORPH-DOMAIN` (Blocking) | S | `T10` | `DR-A` |
| `L3-05-12` | Detector 8 — `ORPH-VENDOR` (Medium) | S | `T10` | `DR-A` |
| `L3-05-13` | Detector 9 — `ORPH-ASSET` (Medium) | S | `T10` | `DR-A` |
| `L3-05-14` | Detector 10 — `ORPH-COMMITMENT` (Blocking) | S | `T04` | `DR-E` |
| `L3-05-15` | Detector 11 — `ORPH-PLATFORM-MIGRATION` (High) | S | `T04` | — |
| `L3-05-16` | Detector 12 — `ORPH-VERIFICATION` (High) | S | `T04` | — |
| `L3-05-17` | Detector 13 — `ORPH-H1-WORK` (High) | M | `T04` | `DR-C` |
| `L3-05-18` | Detector 14 — `ORPH-TEMP-EXPIRY-OPEN-WORK` (High) | M | `T04` | `DR-D` |
| `L3-05-19` | Detector 15 — `ORPH-POLICY` (Blocking) | S | `T04` | — |
| `L3-05-20` | Detector 16 — `ORPH-EXCEPTION` (High) | S | `T04` | — |
| `L3-05-21` | Registry completeness and severity-conformance test | S | `T05`–`T20` | — |
| `L3-05-22` | Prospective mode and the departing-person transfer worklist | M | `T21` | — |
| `L3-05-23` | Orphan report and event payload emitter | M | `T21` | — |
| `L3-05-24` | Blocking-orphan dismissal guard | M | `T23` | — |
| `L3-05-25` | Expiry scan → revocation plan (no execution) | M | `T03`, `T21` | — |
| `L3-05-26` | 14-day delegation expiry warning | M | `T25` | `DR-B` |
| `L3-05-27` | T-minus-7 temporary-person expiry warning to sponsor | M | `T25`, `T18` | `DR-D` |
| `L3-05-28` | No-network / no-write safety test | S | `T27` | — |
| `L3-05-29` | CLI, exit codes and machine-readable output | M | `T22`, `T23`, `T24`, `T25`, `T26`, `T27` | — |
| `L3-05-30` | Phase acceptance suite — AT-017 end to end | L | `T28`, `T29` | — |

---

## 8. Tasks

---

### `L3-05-01` — Preflight: environment, toolchain and phase preconditions

**Size:** S · **Depends on:** — · **Files created:** `reconciler/PHASE5-PREFLIGHT.md`

**Steps**

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/05-preflight
python --version
python -c "import sys; assert sys.version_info[:2] == (3, 11), sys.version; print('PYTHON OK')"
python -c "import yaml; print('PYYAML', yaml.__version__)"
python -c "import pytest; print('PYTEST', pytest.__version__)"
test -d reconciler && echo "RECONCILER DIR PRESENT" || echo "RECONCILER DIR MISSING"
ls reconciler
git remote -v | head -2
```

```bash
set -euo pipefail
mkdir -p reconciler/orphans reconciler/expiry reconciler/tests
cat > reconciler/PHASE5-PREFLIGHT.md <<'EOF'
# L3 Phase 5 preflight record

Phase: L3-05 orphan and expiry detection.
Spec authority: MultiProduct Master Specification v4.0, Section 12.2 (lines 948-1011),
Section 10.1 (line 787), Section 12.4 (lines 1046-1060), Section 54.2 (line 4789),
Section 53.2 (line 4697), invariants 57 and 58 (lines 9528-9529), AT-017 (line 9326).

Binding constraints recorded at preflight:
- No module under reconciler/orphans/** or reconciler/expiry/** performs a network
  call or a GitHub write. Detection and expiry produce data only (Section 99.6 risk 6).
- A detector that cannot read an input returns status "input_unavailable", never an
  empty finding list (Section 97.2 write-freshness rationale).
- Severity vocabulary is exactly: Blocking, High, Medium (Section 12.2 table).
- This phase writes only under reconciler/ (PARTITION.md line 19).

Toolchain: Python 3.11, PyYAML 6.0.2, pytest 8.3.3. No other dependency.
EOF
touch reconciler/orphans/__init__.py reconciler/expiry/__init__.py reconciler/tests/__init__.py
```

```bash
set -euo pipefail
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
git add reconciler
git commit -m "L3-05-01: phase 5 preflight record and package skeleton"
git push -u origin lane/3/05-preflight
gh pr create --base integration --head lane/3/05-preflight \
  --title "L3-05-01 Phase 5 preflight" \
  --body "Lane L3, Phase 5 (orphan and expiry detection). Task L3-05-01. Spec: Section 12.2 (lines 948-1011)."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous expected output |
| 1 | Python is exactly 3.11 | `python -c "import sys; assert sys.version_info[:2]==(3,11); print('PYTHON OK')"` | `PYTHON OK` |
| 2 | PyYAML importable | `python -c "import yaml; print('PYYAML', yaml.__version__)"` | line starts `PYYAML 6.` |
| 3 | pytest importable | `python -c "import pytest; print('PYTEST', pytest.__version__)"` | line starts `PYTEST 8.` |
| 4 | Three packages exist | `ls reconciler/orphans/__init__.py reconciler/expiry/__init__.py reconciler/tests/__init__.py \| wc -l` | `3` |
| 5 | Preflight record committed | `git show --stat --oneline HEAD \| grep -c PHASE5-PREFLIGHT` | `1` |
| 6 | No foreign path touched | lane-guard block in §6.4 | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python -c "import sys,yaml,pytest;print('PY',sys.version_info[0],sys.version_info[1]);print('YAML',yaml.__version__);print('PYTEST',pytest.__version__)"
ls reconciler/orphans/__init__.py reconciler/expiry/__init__.py reconciler/tests/__init__.py | wc -l
git diff --name-only integration...HEAD | grep -cv -E '^reconciler/'
```

Expected output, exactly:

```
PY 3 11
YAML 6.0.2
PYTEST 8.3.3
3
0
```

(The final `0` is `grep -c` finding no foreign paths; `grep` exits 1 there, which is expected.)

**STOP rule**
STOP and open a blocker if any of: Python is not 3.11; PyYAML or pytest is absent or a different major version; `reconciler/` already contains a non-Python implementation (e.g. `*.go`, `*.ts`, `Cargo.toml`) indicating an earlier L3 phase fixed a different toolchain; the lane-guard reports `LANE-GUARD FAIL`. **Do not install, upgrade, or downgrade anything, and do not translate this phase into another language.** Use the §6.6 template with `<one-line symptom>` = `toolchain mismatch in reconciler/`.

---

### `L3-05-02` — Finding model, severity enum, detector registry, decisions module

**Size:** M · **Depends on:** `L3-05-01`
**Files created:** `reconciler/orphans/model.py`, `reconciler/orphans/people.py`, `reconciler/orphans/decisions.py`, `reconciler/orphans/registry.py`, `reconciler/tests/orphans/__init__.py`, `reconciler/tests/orphans/test_model.py`

**What to build (no design choices remain — everything is specified)**

`reconciler/orphans/model.py`:

- `SEVERITIES = ("Blocking", "High", "Medium")` — module constant, frozen tuple, exactly these three strings in this order.
- `@dataclass(frozen=True) class OrphanFinding` with fields, in this order: `orphan_type: str`, `severity: str`, `subject: str`, `detail: str`, `source: str`, `as_of: str`, `mode: str`.
  - `__post_init__` raises `ValueError` if `severity not in SEVERITIES`, or if `mode not in ("current", "prospective")`, or if `as_of` does not match `^\d{4}-\d{2}-\d{2}$`.
- `@dataclass(frozen=True) class DetectorResult` with fields, in this order: `orphan_type: str`, `status: str`, `findings: tuple[OrphanFinding, ...]`, `missing_inputs: tuple[str, ...]`.
  - `__post_init__` raises `ValueError` if `status not in ("ok", "input_unavailable")`; if `status == "input_unavailable"` and `missing_inputs` is empty; if `status == "ok"` and `missing_inputs` is non-empty.
- `def finding_key(f: OrphanFinding) -> tuple[str, str]: return (f.orphan_type, f.subject)` — the stable identity of a finding, used by the dismissal guard and by report diffing.
- `def sort_findings(findings) -> list[OrphanFinding]` — sorts by `(SEVERITIES.index(severity), orphan_type, subject)`. All emitted output is sorted with this so golden files are stable.

`reconciler/orphans/people.py`: `holder_state`, `assignment_in_force`, `active_holders` — implemented exactly as the eight-step and two-rule definitions in §6.8. Dates are compared as `datetime.date`; a YAML value already parsed as `date` is used directly, a string is parsed with `date.fromisoformat`, `None` stays `None`.

`reconciler/orphans/decisions.py`: every constant named in the five DECISION REQUIRED blocks, each assigned `None`, above a module docstring that reproduces the five DR ids, what each blocks, and the instruction *"Values are supplied by L0 on the blocker issue and pasted here verbatim. Do not invent a value."* `# FROM REG-039: replace None with the approved literal values.`

`reconciler/orphans/registry.py`:

- `DETECTORS: dict[str, "Detector"]` — an empty dict at this task; each detector task appends exactly one entry.
- `def register(module) -> None` — validates that the module exposes `ORPHAN_TYPE: str`, `SEVERITY: str`, `SOURCE: str`, `detect(ctx) -> DetectorResult`; raises `ValueError` on a duplicate `ORPHAN_TYPE`; raises `ValueError` if `SEVERITY not in SEVERITIES`.
- `def run_all(ctx) -> list[DetectorResult]` — runs every registered detector in sorted `ORPHAN_TYPE` order and returns the results. If a detector raises, `run_all` re-raises after wrapping the message with the `ORPHAN_TYPE`; it never swallows an exception into an empty result.

`reconciler/tests/orphans/test_model.py` — at minimum these six tests: severity tuple is exactly the three literals in order; a bad severity raises; a bad mode raises; a bad `as_of` raises; `input_unavailable` with empty `missing_inputs` raises; `ok` with non-empty `missing_inputs` raises.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/05-model
mkdir -p reconciler/tests/orphans
touch reconciler/tests/orphans/__init__.py
# create the five files described above
python -m pytest reconciler/tests/orphans/test_model.py -q
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
git add reconciler
git commit -m "L3-05-02: orphan finding model, holder predicate, detector registry, decisions module"
git push -u origin lane/3/05-model
gh pr create --base integration --head lane/3/05-model \
  --title "L3-05-02 Orphan finding model and detector registry" \
  --body "Lane L3, Phase 5 (orphan and expiry detection). Task L3-05-02. Spec: Section 12.2 (lines 948-1011)."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Severity vocabulary is exactly the three spec literals | `python -c "from reconciler.orphans.model import SEVERITIES;print(SEVERITIES)"` | `('Blocking', 'High', 'Medium')` |
| 2 | Registry starts empty | `python -c "from reconciler.orphans.registry import DETECTORS;print(len(DETECTORS))"` | `0` |
| 3 | All twenty-four decision constants exist and are `None` | `python -c "import reconciler.orphans.decisions as d;n=[k for k in dir(d) if k.isupper()];print(len(n), all(getattr(d,k) is None for k in n))"` | `24 True` |
| 4 | Suspension is `held` | `python -c "from reconciler.orphans.people import holder_state; print(holder_state('p',{'p':{'availability':'active','access_status':'suspended'}},None,'current'))"` | `held` |
| 5 | Departed is `vacant` | same helper with `availability='departed'` | `vacant` |
| 6 | Model tests pass | `python -m pytest reconciler/tests/orphans/test_model.py -q \| tail -1` | contains `6 passed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from reconciler.orphans.model import SEVERITIES, OrphanFinding, DetectorResult
from reconciler.orphans.registry import DETECTORS
import reconciler.orphans.decisions as d
print("SEVERITIES", SEVERITIES)
print("DETECTORS", len(DETECTORS))
names=[k for k in dir(d) if k.isupper()]
print("DECISIONS", len(names), all(getattr(d,k) is None for k in names))
try:
    OrphanFinding("X","Critical","s","d","src","2026-08-27","current"); print("SEV-GUARD FAIL")
except ValueError: print("SEV-GUARD OK")
try:
    DetectorResult("X","input_unavailable",(),()); print("INPUT-GUARD FAIL")
except ValueError: print("INPUT-GUARD OK")
EOF
```

Expected output, exactly:

```
SEVERITIES ('Blocking', 'High', 'Medium')
DETECTORS 0
DECISIONS 24 True
SEV-GUARD OK
INPUT-GUARD OK
```

**STOP rule**
STOP if the decision-constant count is not 24, or if any guard prints `FAIL`. **Do not relax a guard to make a test pass, and do not fill any decision constant with a guessed value.** §6.6 template, symptom `model guards not enforcing`.

---

### `L3-05-03` — Control-plane loader with input-availability guard

**Size:** M · **Depends on:** `L3-05-02`
**Files created:** `reconciler/orphans/loader.py`, `reconciler/tests/orphans/test_loader.py`

**What to build**

`load_control_plane(root: Path, as_of: date, mode: str) -> ControlPlane` where `ControlPlane` is a frozen dataclass exposing:

| Attribute | Loaded from | On file missing |
| --- | --- | --- |
| `people: dict[str, dict]` | `<root>/people.yaml`, keyed by `people[].id` | record `"people.yaml"` in `missing` |
| `products: dict[str, dict]` | every `<root>/products/*/product.yaml`, keyed by `identity.id` | record `"products/*/product.yaml"` in `missing` if the directory is absent |
| `services: dict[str, dict]` | every `<root>/shared-services/*/service.yaml`, keyed by `identity.id` | record `"shared-services/*/service.yaml"` in `missing` |
| `policies: list[dict]` | `<root>/policies.yaml` → `policies` | record `"policies.yaml"` |
| `exceptions: list[dict]` | `<root>/exceptions.yaml` → `exceptions` | record `"exceptions.yaml"` |
| `assets: list[dict]` | paths from `decisions.ASSET_INVENTORY_PATHS` | record each path; if the constant is `None`, record `"DR-L3-05-A unanswered"` |
| `board_items: list[dict]` | `decisions.BOARD_SNAPSHOT_PATH` | record the path; if the constant is `None`, record `"DR-L3-05-C unanswered"` |
| `open_work: list[dict]` | `decisions.OPEN_WORK_SNAPSHOT_PATH` | record the path; if the constant is `None`, record `"DR-L3-05-D unanswered"` |
| `missing: tuple[str, ...]` | accumulated as above | — |
| `as_of: date`, `mode: str` | passed in | — |

Rules, all mandatory:

- A missing file is recorded in `missing` and the corresponding collection is left **empty**. The loader never raises for a missing file.
- A file that exists but fails to parse **raises** `ControlPlaneParseError` naming the path. A corrupt registry is not the same as an absent one and must not read as health.
- An empty-but-present file (`null` document) parses to an empty collection and is **not** recorded as missing.
- Helper `ctx.require(*keys) -> tuple[str, ...]` returns the subset of `keys` present in `missing`; a detector uses it to decide between `ok` and `input_unavailable`.
- The loader performs **no** network access and **no** writes.

`reconciler/tests/orphans/test_loader.py`: at minimum — a complete fixture loads with `missing == ()`; a fixture with no `policies.yaml` records exactly `("policies.yaml",)`; a fixture with a malformed `people.yaml` raises `ControlPlaneParseError` containing the path; an empty `exceptions.yaml` gives `exceptions == []` and does **not** appear in `missing`.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/05-loader
mkdir -p reconciler/tests/fixtures/orphans
# create loader.py and test_loader.py, plus the four small loader fixtures under
# reconciler/tests/fixtures/loader/{complete,no-policies,malformed-people,empty-exceptions}/
python -m pytest reconciler/tests/orphans/test_loader.py -q
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
git add reconciler
git commit -m "L3-05-03: control-plane loader with input-availability guard"
git push -u origin lane/3/05-loader
gh pr create --base integration --head lane/3/05-loader \
  --title "L3-05-03 Control-plane loader" \
  --body "Lane L3, Phase 5 (orphan and expiry detection). Task L3-05-03. Spec: Section 97.2 (write-freshness rationale, line 8860)."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Complete fixture reports nothing missing | `python -c "from pathlib import Path;from datetime import date;from reconciler.orphans.loader import load_control_plane as L;print(L(Path('reconciler/tests/fixtures/loader/complete'),date(2026,8,27),'current').missing)"` | `()` |
| 2 | Missing file is named, not silently empty | same against `no-policies` | `('policies.yaml',)` |
| 3 | Malformed file raises | `python -c "...load 'malformed-people'..."` | traceback ending `ControlPlaneParseError` and the path |
| 4 | Empty file is not "missing" | same against `empty-exceptions`, print `(ctx.exceptions, ctx.missing)` | `([], ())` |
| 5 | Loader tests pass | `python -m pytest reconciler/tests/orphans/test_loader.py -q \| tail -1` | contains `4 passed` |
| 6 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane, ControlPlaneParseError
B=Path('reconciler/tests/fixtures/loader')
print("COMPLETE", load_control_plane(B/'complete', date(2026,8,27),'current').missing)
print("NOPOL", load_control_plane(B/'no-policies', date(2026,8,27),'current').missing)
c=load_control_plane(B/'empty-exceptions', date(2026,8,27),'current')
print("EMPTY", c.exceptions, c.missing)
try:
    load_control_plane(B/'malformed-people', date(2026,8,27),'current'); print("PARSE-GUARD FAIL")
except ControlPlaneParseError as e: print("PARSE-GUARD OK")
EOF
```

Expected output, exactly:

```
COMPLETE ()
NOPOL ('policies.yaml',)
EMPTY [] ()
PARSE-GUARD OK
```

**STOP rule**
STOP if a malformed registry loads without raising, or if a missing file produces `missing == ()`. **Both failures make silence look like health, which §0 forbids; do not "fix" them by widening the try/except.** §6.6 template, symptom `loader treats missing or corrupt input as clean`.

---

### `L3-05-04` — Fixture harness and golden-case layout

**Size:** M · **Depends on:** `L3-05-03`
**Files created:** `reconciler/tests/support/__init__.py`, `reconciler/tests/support/harness.py`, `reconciler/tests/fixtures/orphans/README.md`, `reconciler/tests/fixtures/orphans/_BASE/**`

**Frozen fixture case layout** (every detector task creates cases in exactly this shape):

```
reconciler/tests/fixtures/orphans/<CASE-ID>/
    case.json          # {"as_of":"YYYY-MM-DD","mode":"current"|"prospective"}
    people.yaml
    policies.yaml
    exceptions.yaml
    products/<product-id>/product.yaml     (zero or more)
    shared-services/<service-id>/service.yaml (zero or more)
    expected.json
```

Frozen `expected.json` shape:

```json
{
  "as_of": "2026-08-27",
  "mode": "current",
  "input_unavailable": [],
  "findings": [
    {
      "orphan_type": "ORPH-PRIMARY-OWNER",
      "severity": "Blocking",
      "subject": "product:product-1",
      "detail": "no in-force primary_owner assignment held by an active person",
      "source": "Assignment registry"
    }
  ]
}
```

`harness.py` exposes:

- `run_case(case_id: str) -> dict` — loads `case.json`, loads the control plane from the case directory, runs **only the detector under test** when `orphan_type` is passed, or `run_all` when it is not, and returns the JSON-shaped dict above with findings passed through `sort_findings`.
- `assert_case(case_id: str, orphan_type: str | None = None) -> None` — compares `run_case(...)` to `expected.json` with `assertEqual`-style equality on the whole dict, and on mismatch prints a unified diff of `json.dumps(..., indent=2, sort_keys=True)` for both sides.
- `_BASE` is a minimal clean control plane — one person `dev-a` (`availability: active`, `access_status: provisioned`), one product `product-1` fully owned, one shared service `svc-1` fully owned, an empty `policies.yaml` (`policies: []`) and an empty `exceptions.yaml` (`exceptions: []`). Detector cases are created by copying `_BASE` and changing exactly one thing.
- `copy_base(case_id: str) -> Path` — a helper used by fixture-authoring scripts, not by tests.

`README.md` in the fixtures directory states, in prose: every detector owns exactly two cases, `<ORPHAN-TYPE>-ORPHAN` and `<ORPHAN-TYPE>-CLEAN`; the `-CLEAN` case must produce zero findings **for that detector**; golden files are authored by hand and never regenerated from the implementation output.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/05-harness
mkdir -p reconciler/tests/support reconciler/tests/fixtures/orphans/_BASE/products/product-1 \
         reconciler/tests/fixtures/orphans/_BASE/shared-services/svc-1
touch reconciler/tests/support/__init__.py
# author harness.py, README.md and the _BASE fixture files
python -c "from reconciler.tests.support.harness import run_case; print(run_case('_BASE'))"
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
git add reconciler
git commit -m "L3-05-04: golden fixture harness and _BASE clean control plane"
git push -u origin lane/3/05-harness
gh pr create --base integration --head lane/3/05-harness \
  --title "L3-05-04 Fixture harness" \
  --body "Lane L3, Phase 5 (orphan and expiry detection). Task L3-05-04."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | `_BASE` loads with nothing missing except the three DR-blocked inputs | see SELF-VERIFY | `('DR-L3-05-A unanswered', 'DR-L3-05-C unanswered', 'DR-L3-05-D unanswered')` |
| 2 | `_BASE` yields zero findings with zero detectors registered | `python -c "from reconciler.tests.support.harness import run_case;print(run_case('_BASE')['findings'])"` | `[]` |
| 3 | `assert_case` fails loudly on a deliberate mismatch | temporarily edit `_BASE/expected.json` to add a bogus finding, run `assert_case('_BASE')` | non-zero exit and a printed diff; **revert the edit afterwards** |
| 4 | Fixture README present | `test -f reconciler/tests/fixtures/orphans/README.md && echo README OK` | `README OK` |
| 5 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.tests.support.harness import run_case
ctx = load_control_plane(Path('reconciler/tests/fixtures/orphans/_BASE'), date(2026,8,27), 'current')
print("MISSING", tuple(sorted(ctx.missing)))
r = run_case('_BASE')
print("FINDINGS", r['findings'])
print("MODE", r['mode'], "AS_OF", r['as_of'])
EOF
```

Expected output, exactly:

```
MISSING ('DR-L3-05-A unanswered', 'DR-L3-05-C unanswered', 'DR-L3-05-D unanswered')
FINDINGS []
MODE current AS_OF 2026-08-27
```

**STOP rule**
STOP if `_BASE` produces any finding, or if `assert_case` passes against a deliberately wrong `expected.json`. **A harness that cannot fail proves nothing.** §6.6 template, symptom `fixture harness does not detect a golden mismatch`.

---

### Detector tasks `L3-05-05` … `L3-05-20` — common shape

Every detector task below follows this identical shape. Read it once; each task then states only what differs.

**Files per detector task**

```
reconciler/orphans/detectors/<snake_case_id>.py
reconciler/tests/orphans/test_<snake_case_id>.py
reconciler/tests/fixtures/orphans/<ORPHAN-TYPE>-ORPHAN/**
reconciler/tests/fixtures/orphans/<ORPHAN-TYPE>-CLEAN/**
```

(The first detector task also creates `reconciler/orphans/detectors/__init__.py`.)

**Module contract, identical for all sixteen**

```python
ORPHAN_TYPE = "<the frozen id from §2>"
SEVERITY    = "<the frozen severity from §2 — Blocking | High | Medium>"
SOURCE      = "<the spec Detection column, verbatim>"

def detect(ctx) -> DetectorResult:
    missing = ctx.require(*REQUIRED_INPUTS)
    if missing:
        return DetectorResult(ORPHAN_TYPE, "input_unavailable", (), missing)
    findings = [...]
    return DetectorResult(ORPHAN_TYPE, "ok", tuple(sort_findings(findings)), ())
```

The module ends with `registry.register(sys.modules[__name__])` executed on import, and `reconciler/orphans/detectors/__init__.py` imports every detector module so that importing the package populates `DETECTORS`.

**Test contract, identical for all sixteen**

```python
from reconciler.tests.support.harness import assert_case

def test_orphan_case():
    assert_case("<ORPHAN-TYPE>-ORPHAN", orphan_type="<ORPHAN-TYPE>")

def test_clean_case():
    assert_case("<ORPHAN-TYPE>-CLEAN", orphan_type="<ORPHAN-TYPE>")
```

**Commands, identical for all sixteen** (substitute `<Tnn>`, `<slug>`, `<ORPHAN-TYPE>`, `<snake_case_id>`)

```bash
set -euo pipefail
cd "$CONTROL_PLANE"
git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/05-<slug>
mkdir -p reconciler/orphans/detectors
cp -r reconciler/tests/fixtures/orphans/_BASE reconciler/tests/fixtures/orphans/<ORPHAN-TYPE>-ORPHAN
cp -r reconciler/tests/fixtures/orphans/_BASE reconciler/tests/fixtures/orphans/<ORPHAN-TYPE>-CLEAN
# apply the single documented mutation to the -ORPHAN case; hand-author both expected.json files
python -m pytest reconciler/tests/orphans/test_<snake_case_id>.py -q
python -m pytest reconciler/tests -q
git diff --name-only integration...HEAD | grep -v -E '^reconciler/' | tee /tmp/foreign.txt
test ! -s /tmp/foreign.txt && echo "LANE-GUARD OK" || echo "LANE-GUARD FAIL"
git add reconciler
git commit -m "L3-05-<Tnn>: detector <ORPHAN-TYPE> (<SEVERITY>)"
git push -u origin lane/3/05-<slug>
gh pr create --base integration --head lane/3/05-<slug> \
  --title "L3-05-<Tnn> Detector <ORPHAN-TYPE>" \
  --body "Lane L3, Phase 5. Task L3-05-<Tnn>. Orphan type from Section 12.2 table (lines 992-1010)."
```

**Acceptance criteria, identical for all sixteen**

| # | Criterion | Proving command | Expected output |
| 1 | Constants match §2 byte-for-byte | `python -c "import reconciler.orphans.detectors.<snake_case_id> as m;print(m.ORPHAN_TYPE, '|', m.SEVERITY, '|', m.SOURCE)"` | the task's stated line |
| 2 | Detector is registered exactly once | `python -c "import reconciler.orphans.detectors as d;from reconciler.orphans.registry import DETECTORS;print('<ORPHAN-TYPE>' in DETECTORS)"` | `True` |
| 3 | `-ORPHAN` case matches its golden file | `python -m pytest reconciler/tests/orphans/test_<snake_case_id>.py::test_orphan_case -q \| tail -1` | contains `1 passed` |
| 4 | `-CLEAN` case yields zero findings | `python -m pytest reconciler/tests/orphans/test_<snake_case_id>.py::test_clean_case -q \| tail -1` | contains `1 passed` |
| 5 | Missing input yields `input_unavailable`, never empty-ok | the task's SELF-VERIFY | `input_unavailable` and a non-empty `missing_inputs` |
| 6 | Whole suite still green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed` and **not** `failed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**STOP rule, identical for all sixteen**
STOP and open a blocker (§6.6) if any of: the severity you would need to write differs from §2; the `-CLEAN` case produces a finding; the detector returns `ok` with an empty finding list while an input it reads is in `ctx.missing`; the task is DR-blocked and the relevant constant in `reconciler/orphans/decisions.py` is still `None`. **Never edit §2's severity, never guess a decision constant, never change `_BASE`.** Symptom line: `<ORPHAN-TYPE> cannot be implemented as specified`.

---

### `L3-05-05` — Detector 1: `ORPH-PRIMARY-OWNER` (Blocking)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d01-primary-owner` · **Module:** `reconciler/orphans/detectors/orph_primary_owner.py`

**Constants** — `ORPHAN_TYPE = "ORPH-PRIMARY-OWNER"` · `SEVERITY = "Blocking"` · `SOURCE = "Assignment registry"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (spec Section 12.2 line 993; SIG-05 line 4534: *"Any product with no active Primary Owner"*)

> For every product `p` in `ctx.products`:
> emit a finding when `active_holders(p["assignments"], "primary_owner", ctx, as_of, mode)` is empty.

**Frozen finding fields**
`subject = f"product:{p['identity']['id']}"` · `detail = "no in-force primary_owner assignment held by an active person"`

**Fixture mutations**

| Case | Mutation from `_BASE` |
| --- | --- |
| `ORPH-PRIMARY-OWNER-ORPHAN` | In `products/product-1/product.yaml`, set the `primary_owner` assignment's `person` to `dev-x`, and add `dev-x` to `people.yaml` with `availability: departed`, `access_status: revoked`. Expect one finding. |
| `ORPH-PRIMARY-OWNER-CLEAN` | Unchanged `_BASE`, plus a second assignment `{person: dev-a, type: primary_owner, start_date: 2020-01-01, end_date: null}` is **not** added — the base owner suffices. Expect zero findings. |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
import reconciler.orphans.detectors as _
from reconciler.orphans.detectors.orph_primary_owner import ORPHAN_TYPE, SEVERITY, SOURCE, detect
from reconciler.tests.support.harness import run_case, load_ctx
print(ORPHAN_TYPE, "|", SEVERITY, "|", SOURCE)
r = run_case("ORPH-PRIMARY-OWNER-ORPHAN", orphan_type=ORPHAN_TYPE)
print("N", len(r["findings"]), r["findings"][0]["subject"], r["findings"][0]["severity"])
print("CLEAN", len(run_case("ORPH-PRIMARY-OWNER-CLEAN", orphan_type=ORPHAN_TYPE)["findings"]))
ctx = load_ctx("ORPH-PRIMARY-OWNER-ORPHAN"); object.__setattr__(ctx, "missing", ("people.yaml",))
res = detect(ctx); print("GUARD", res.status, res.missing_inputs, len(res.findings))
EOF
```

Expected output, exactly:

```
ORPH-PRIMARY-OWNER | Blocking | Assignment registry
N 1 product:product-1 Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-06` — Detector 2: `ORPH-CROSS-REVIEWER` (Blocking)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d02-cross-reviewer` · **Module:** `orph_cross_reviewer.py`

**Constants** — `ORPHAN_TYPE = "ORPH-CROSS-REVIEWER"` · `SEVERITY = "Blocking"` · `SOURCE = "Assignment registry"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 994; SIG-05 line 4534 *"no active Cross-Reviewer"*)

> For every product `p`: emit when `active_holders(p["assignments"], "cross_reviewer", ctx, as_of, mode)` is empty.

**Frozen finding fields** — `subject = f"product:{id}"` · `detail = "no in-force cross_reviewer assignment held by an active person"`

**Fixture mutations** — `-ORPHAN`: delete the `cross_reviewer` assignment from `products/product-1/product.yaml`. `-CLEAN`: unchanged `_BASE`.

**SELF-VERIFY** — as `L3-05-05`, substituting the module and type. Expected output, exactly:

```
ORPH-CROSS-REVIEWER | Blocking | Assignment registry
N 1 product:product-1 Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-07` — Detector 3: `ORPH-BACKUP-OWNER` (High)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d03-backup-owner` · **Module:** `orph_backup_owner.py`

**Constants** — `ORPHAN_TYPE = "ORPH-BACKUP-OWNER"` · `SEVERITY = "High"` · `SOURCE = "Assignment registry"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 995)

> For every product `p`: emit when `active_holders(p["assignments"], "backup_owner", ctx, as_of, mode)` is empty.

**Frozen finding fields** — `subject = f"product:{id}"` · `detail = "no in-force backup_owner assignment held by an active person"`

**Fixture mutations** — `-ORPHAN`: set the `backup_owner` assignment's `end_date` to `2026-01-01` (expired relative to the case `as_of` of `2026-08-27`). `-CLEAN`: unchanged `_BASE`.

**Note for the executor:** severity here is `High`, **not** `Blocking` — Section 12.2 line 995 prints `High`. Do not "harmonise" it with the two rows above. Section 95.4 (line 8682) separately records that Backup-Owner coverage runs under a bootstrap exception until headcount thresholds are reached; that is an L5/L0 concern and changes nothing in this detector.

**SELF-VERIFY** expected output, exactly:

```
ORPH-BACKUP-OWNER | High | Assignment registry
N 1 product:product-1 High
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-08` — Detector 4: `ORPH-PRIMARY-RESPONDER` (Blocking)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d04-primary-responder` · **Module:** `orph_primary_responder.py`

**Constants** — `ORPHAN_TYPE = "ORPH-PRIMARY-RESPONDER"` · `SEVERITY = "Blocking"` · `SOURCE = "Contract operations block"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 996 — Detection column is *"Contract operations block"*; the field is `operations.primary_responder`, Section 15.1 line 1491; SIG-05 line 4534 *"no named responder"*)

> For every product `p`, let `r = p.get("operations", {}).get("primary_responder")`.
> Emit when `r` is `None` or empty, **or** when `holder_state(r, ctx, as_of, mode) == "vacant"`.

Section 15.1 marks `primary_responder` as DERIVED from the `incident_responder` assignments *"which are authoritative; validated by reconciliation"*. Validating derived-versus-authoritative is drift detection, not orphan detection, and is not this task. Read the operations block, exactly as the Detection column says.

**Frozen finding fields** — `subject = f"product:{id}"` · `detail = "operations.primary_responder is unset or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: set `operations.primary_responder: null` in `products/product-1/product.yaml`. `-CLEAN`: unchanged `_BASE`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-PRIMARY-RESPONDER | Blocking | Contract operations block
N 1 product:product-1 Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-09` — Detector 5: `ORPH-SHARED-SERVICE` (Blocking)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d05-shared-service` · **Module:** `orph_shared_service.py`

**Constants** — `ORPHAN_TYPE = "ORPH-SHARED-SERVICE"` · `SEVERITY = "Blocking"` · `SOURCE = "Service registry"` · `REQUIRED_INPUTS = ("people.yaml", "shared-services/*/service.yaml")`

**Detection query** (Section 12.2 line 997; service schema Section 20.1 lines 2044–2052)

> For every service `s` in `ctx.services`: emit when `active_holders(s["assignments"], "primary_owner", ctx, as_of, mode)` is empty.

Section 20.1 line 2074 states *"A shared service has the same four ownership relationships as a product"*, but Section 12.2 provides exactly **one** shared-service orphan row — *"Shared service with no owner"* — so this detector checks `primary_owner` only. Do not add cross-reviewer or backup-owner rows for services; inventing orphan types is forbidden.

**Frozen finding fields** — `subject = f"service:{s['identity']['id']}"` · `detail = "no in-force primary_owner assignment held by an active person"`

**Fixture mutations** — `-ORPHAN`: in `shared-services/svc-1/service.yaml`, change the `primary_owner` assignment's `person` to `dev-x` (the departed person added in `T05`'s people fixture; add the same `dev-x` record here). `-CLEAN`: unchanged `_BASE`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-SHARED-SERVICE | Blocking | Service registry
N 1 service:svc-1 Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-10` — Detector 6: `ORPH-CERTIFICATE` (High) — **DR-L3-05-A blocked**

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d06-certificate` · **Module:** `orph_certificate.py`
**Also creates:** `reconciler/orphans/assets.py` (the shared asset-inventory reader used by `T10`–`T13`).

**Step 0 — decision gate.** Run:

```bash
set -euo pipefail
python -c "import reconciler.orphans.decisions as d; print('ASSET-DR', d.ASSET_INVENTORY_PATHS is not None)"
```

If this prints `ASSET-DR False`, **STOP immediately** and open the blocker issue with `DECISION REQUIRED ID: DR-L3-05-A`. Do not create the file, do not invent a path, do not proceed to `T11`–`T13`.

**Constants** — `ORPHAN_TYPE = "ORPH-CERTIFICATE"` · `SEVERITY = "High"` · `SOURCE = "Asset inventory"` · `REQUIRED_INPUTS = ("DR-L3-05-A unanswered",) + tuple(decisions.ASSET_INVENTORY_PATHS)`

**Shared reader** `reconciler/orphans/assets.py`:
`iter_assets(ctx) -> Iterator[dict]` yields each entry from `ctx.assets`; `asset_id(e)`, `asset_owner(e)`, `asset_type(e)` read via the `decisions.ASSET_*_KEY` constants.

**Detection query** (Section 12.2 line 998; Section 49.1 line 4346: *"Each entry carries an expiry date, a named owner…"*; line 4353: *"A departing person who owned a certificate or a domain leaves an orphaned asset"*)

> For every asset entry `e` where `asset_type(e) == decisions.ASSET_TYPE_CERTIFICATE`:
> emit when `asset_owner(e)` is `None`/empty, **or** `holder_state(asset_owner(e), ctx, as_of, mode) == "vacant"`.

When the asset inventory carries no entries of this type, emit `UNARMED`, never `0 findings`. (D77 requires UNARMED status for untriggered scans.)

**Frozen finding fields** — `subject = f"asset:{asset_id(e)}"` · `detail = "certificate has no owner or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: add an asset-inventory file at `decisions.ASSET_INVENTORY_PATHS[0]` inside the case directory with one certificate entry owned by `dev-x` (departed) and one owned by `dev-a`. `-CLEAN`: same file, both entries owned by `dev-a`.

**SELF-VERIFY** expected output, exactly (`N 1` = only the `dev-x` certificate):

```
ORPH-CERTIFICATE | High | Asset inventory
N 1 High
CLEAN 0
GUARD input_unavailable 0
```

---

### `L3-05-11` — Detector 7: `ORPH-DOMAIN` (Blocking) — **DR-L3-05-A blocked**

**Size:** S · **Depends on:** `L3-05-10` · **Slug:** `d07-domain` · **Module:** `orph_domain.py`

**Constants** — `ORPHAN_TYPE = "ORPH-DOMAIN"` · `SEVERITY = "Blocking"` · `SOURCE = "Asset inventory"` · same `REQUIRED_INPUTS` as `T10`.

**Detection query** (Section 12.2 line 999)

> Identical to `T10` with `decisions.ASSET_TYPE_DOMAIN`.

When the asset inventory carries no entries of this type, emit `UNARMED`, never `0 findings`. (D77 requires UNARMED status for untriggered scans.)

Note the severity difference from `T10`: a certificate is `High`, a domain is `Blocking`, printed on adjacent rows of the same table (lines 998, 999). Copy them; do not reconcile them.

**Frozen finding fields** — `subject = f"asset:{asset_id(e)}"` · `detail = "domain has no owner or names a person who is not active"`

**Fixture mutations** — as `T10`, with domain-typed entries.

**SELF-VERIFY** expected output, exactly:

```
ORPH-DOMAIN | Blocking | Asset inventory
N 1 Blocking
CLEAN 0
GUARD input_unavailable 0
```

---

### `L3-05-12` — Detector 8: `ORPH-VENDOR` (Medium) — **DR-L3-05-A blocked**

**Size:** S · **Depends on:** `L3-05-10` · **Slug:** `d08-vendor` · **Module:** `orph_vendor.py`

**Constants** — `ORPHAN_TYPE = "ORPH-VENDOR"` · `SEVERITY = "Medium"` · `SOURCE = "Asset inventory"` · same `REQUIRED_INPUTS` as `T10`.

**Detection query** (Section 12.2 line 1000; Section 49.2 line 4364: external-deadline entries each have *"a named owner (defaulting to the affected product's Primary Owner)"*)

> Identical to `T10` with `decisions.ASSET_TYPE_VENDOR`.

When the asset inventory carries no entries of this type, emit `UNARMED`, never `0 findings`. (D77 requires UNARMED status for untriggered scans.)

The "defaults to the affected product's Primary Owner" phrasing of Section 49.2 describes how an owner is **chosen when the entry is created**, not a runtime fallback the reconciler applies. This detector applies **no** fallback: an entry with no owner key is orphaned. If `DR-L3-05-A`'s answer states a runtime fallback, implement exactly what it states and nothing more.

**Frozen finding fields** — `subject = f"asset:{asset_id(e)}"` · `detail = "vendor relationship has no owner or names a person who is not active"`

**SELF-VERIFY** expected output, exactly:

```
ORPH-VENDOR | Medium | Asset inventory
N 1 Medium
CLEAN 0
GUARD input_unavailable 0
```

---

### `L3-05-13` — Detector 9: `ORPH-ASSET` (Medium) — **DR-L3-05-A blocked**

**Size:** S · **Depends on:** `L3-05-10` · **Slug:** `d09-asset` · **Module:** `orph_asset.py`

**Constants** — `ORPHAN_TYPE = "ORPH-ASSET"` · `SEVERITY = "Medium"` · `SOURCE = "Asset inventory"` · same `REQUIRED_INPUTS` as `T10`.

**Detection query** (Section 12.2 line 1001; Section 51-adjacent line 4177: *"Orphan detection covers asset owners, not only product owners"*)

> For every asset entry `e` whose `asset_type(e)` is **not** one of `ASSET_TYPE_CERTIFICATE`, `ASSET_TYPE_DOMAIN`, `ASSET_TYPE_VENDOR`:
> emit when the owner is absent or `vacant`.

This is the residual row and must not double-count: an entry counted by `T10`, `T11` or `T12` is never counted here. The registry-completeness test in `T21` asserts the four asset detectors partition the inventory.

**Frozen finding fields** — `subject = f"asset:{asset_id(e)}"` · `detail = "operational asset has no owner or names a person who is not active"`

**SELF-VERIFY** expected output, exactly:

```
ORPH-ASSET | Medium | Asset inventory
N 1 Medium
CLEAN 0
GUARD input_unavailable 0
PARTITION OK
```

(the last line is a check that the four asset detectors' subject sets are pairwise disjoint on the `-ORPHAN` fixture)

---

### `L3-05-14` — Detector 10: `ORPH-COMMITMENT` (Blocking) — **DR-L3-05-E blocked**

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d10-commitment` · **Module:** `orph_commitment.py`

**Step 0 — decision gate.**

```bash
set -euo pipefail
python -c "import reconciler.orphans.decisions as d; print('COMMIT-DR', d.COMMITMENT_OWNER_RESOLUTION is not None)"
```

If `COMMIT-DR False`, STOP and open the blocker with `DECISION REQUIRED ID: DR-L3-05-E`.

**Constants** — `ORPHAN_TYPE = "ORPH-COMMITMENT"` · `SEVERITY = "Blocking"` · `SOURCE = "Contract operations block"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 1002; commitments schema Section 21.1 lines 2123–2148)

> For every product `p` and every entry `c` in `p.get("commitments", [])`:
> resolve the owner by walking `decisions.COMMITMENT_OWNER_RESOLUTION` in order — each element is a dotted key path evaluated first against `c`, then against `p` — and taking the first non-empty value.
> Emit when no element resolves to a value, **or** when `holder_state(resolved, ctx, as_of, mode) == "vacant"`.

**Frozen finding fields** — `subject = f"commitment:{p['identity']['id']}/{c['customer']}"` · `detail = "customer commitment has no owner or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: add a `commitments:` block to `products/product-1/product.yaml` with one entry `customer: customer-ref-017`, and make whatever key `COMMITMENT_OWNER_RESOLUTION` names resolve to `dev-x` (departed). `-CLEAN`: same entry resolving to `dev-a`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-COMMITMENT | Blocking | Contract operations block
N 1 commitment:product-1/customer-ref-017 Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-15` — Detector 11: `ORPH-PLATFORM-MIGRATION` (High)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d11-platform-migration` · **Module:** `orph_platform_migration.py`

**Constants** — `ORPHAN_TYPE = "ORPH-PLATFORM-MIGRATION"` · `SEVERITY = "High"` · `SOURCE = "Compatibility state"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 1003; Section 60.3 lines 5195–5211: *"`transitional` … **Requires a named migration owner, a target version and a deadline**"* and *"A transitional product without an owner or past its deadline appears on the Founder's product-attention dimension as Action Required"*; invariant **74**, line 9551)

> For every product `p` where `p.get("platform_compatibility") == "transitional"`, let `o = p.get("platform_migration", {}).get("owner")`.
> Emit when `o` is `None`/empty, **or** `holder_state(o, ctx, as_of, mode) == "vacant"`.

Deadline-passed is a separate condition feeding SIG-10 (line 4539) and is **not** an orphan; do not detect it here.

**Frozen finding fields** — `subject = f"migration:{p['identity']['id']}"` · `detail = "transitional product has no migration owner or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: set `platform_compatibility: transitional` on `product-1` and add `platform_migration: {target_contract_version: 2, owner: dev-x, deadline: 2026-12-01}`. `-CLEAN`: same but `owner: dev-a`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-PLATFORM-MIGRATION | High | Compatibility state
N 1 migration:product-1 High
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-16` — Detector 12: `ORPH-VERIFICATION` (High)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d12-verification` · **Module:** `orph_verification.py`

**Constants** — `ORPHAN_TYPE = "ORPH-VERIFICATION"` · `SEVERITY = "High"` · `SOURCE = "Assignment registry"` · `REQUIRED_INPUTS = ("people.yaml", "products/*/product.yaml")`

**Detection query** (Section 12.2 line 1004; assignment type `verification_responsibility`, Section 10.1 line 773 — *"Owns this product's verification contract"*)

> For every product `p`: emit when `active_holders(p["assignments"], "verification_responsibility", ctx, as_of, mode)` is empty.

A `verification_delegate` assignment (Section 10.1, line 783) is dated, scoped and does **not** satisfy this row — the row names the responsibility, not a delegate of it. Do not count delegates.

**Frozen finding fields** — `subject = f"product:{id}"` · `detail = "no in-force verification_responsibility assignment held by an active person"`

**Fixture mutations** — `_BASE` gains a `verification_responsibility` assignment for `dev-a` on `product-1` **as part of this task** (append it to `_BASE`, then re-run the full suite: adding an assignment cannot change any earlier detector's result, and `T21` re-verifies). `-ORPHAN`: remove it. `-CLEAN`: keep it.

**Note:** this is the one task permitted to modify `_BASE`, because `_BASE` must be a *clean* control plane and a clean control plane has a verification owner. Make the `_BASE` edit and the detector in the same commit, and re-run `python -m pytest reconciler/tests -q` before pushing.

**SELF-VERIFY** expected output, exactly:

```
ORPH-VERIFICATION | High | Assignment registry
N 1 product:product-1 High
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
BASE-CLEAN 0
```

(`BASE-CLEAN 0` = `run_case('_BASE')` still yields zero findings across all registered detectors)

---

### `L3-05-17` — Detector 13: `ORPH-H1-WORK` (High) — **DR-L3-05-C blocked**

**Size:** M · **Depends on:** `L3-05-04` · **Slug:** `d13-h1-work` · **Module:** `orph_h1_work.py`

**Step 0 — decision gate.**

```bash
set -euo pipefail
python -c "import reconciler.orphans.decisions as d; print('BOARD-DR', d.BOARD_SNAPSHOT_PATH is not None and d.BOARD_H1_COLUMNS is not None)"
```

If `BOARD-DR False`, STOP and open the blocker with `DECISION REQUIRED ID: DR-L3-05-C`.

**Constants** — `ORPHAN_TYPE = "ORPH-H1-WORK"` · `SEVERITY = "High"` · `SOURCE = "Board"` · `REQUIRED_INPUTS = ("people.yaml", decisions.BOARD_SNAPSHOT_PATH)`

**Detection query** (Section 12.2 line 1005; H1 definition Section 29.2 line 2645: *"The in-flight flow columns — Planned, In Progress, In Review, Verify — plus the Deploy pipeline stage and any item carrying the Blocked flag"*)

> An item `i` from `ctx.board_items` is **in H1** when `i[BOARD_COLUMN_KEY] in BOARD_H1_COLUMNS` **or** `i.get(BOARD_BLOCKED_KEY)` is truthy.
> For every in-H1 item: emit when `i.get(BOARD_ASSIGNEE_KEY)` is `None`/empty, **or** `holder_state(assignee, ctx, as_of, mode) == "vacant"`.

**Frozen finding fields** — `subject = f"board-item:{i[BOARD_ITEM_ID_KEY]}"` · `detail = "in-flight H1 item has no assignee or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: a board snapshot with four items — one H1 unassigned, one H1 assigned to `dev-x` (departed), one H1 assigned to `dev-a`, one non-H1 (`Backlog`) unassigned. Expect exactly **two** findings, sorted by subject. `-CLEAN`: the same four items with all H1 items assigned to `dev-a`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-H1-WORK | High | Board
N 2 High
CLEAN 0
NON-H1 EXCLUDED True
GUARD input_unavailable 0
```

---

### `L3-05-18` — Detector 14: `ORPH-TEMP-EXPIRY-OPEN-WORK` (High) — **DR-L3-05-D blocked**

**Size:** M · **Depends on:** `L3-05-04` · **Slug:** `d14-temp-expiry-open-work` · **Module:** `orph_temp_expiry_open_work.py`

**Step 0 — decision gate.**

```bash
set -euo pipefail
python -c "import reconciler.orphans.decisions as d; print('OPENWORK-DR', d.OPEN_WORK_SNAPSHOT_PATH is not None and d.OPEN_WORK_GATE_RELEVANT_KINDS is not None)"
```

If `OPENWORK-DR False`, STOP and open the blocker with `DECISION REQUIRED ID: DR-L3-05-D`.

**Constants** — `ORPHAN_TYPE = "ORPH-TEMP-EXPIRY-OPEN-WORK"` · `SEVERITY = "High"` · `SOURCE = "Assignment registry + open reviews and gate items at expiry"` · `REQUIRED_INPUTS = ("people.yaml", decisions.OPEN_WORK_SNAPSHOT_PATH)`

**Detection query** (Section 12.2 lines 988 and 1006; EC-111 line 9769)

> `TEMPORARY_EMPLOYMENT_TYPES = ("contractor", "intern", "temporary_specialist", "consultant")` — the four non-employee tokens printed at Section 7 line 558 (`employee | contractor | intern | temporary_specialist | consultant`) minus `employee`. Section 7.1 line 608 binds them together: *"`end_date` is mandatory for every non-employee"*.
> For every person `q` where `q["employment_type"] in TEMPORARY_EMPLOYMENT_TYPES` and `q["end_date"]` is not null and `q["end_date"] <= as_of`:
> let `open_items = [i for i in ctx.open_work if i[OPEN_WORK_HOLDER_KEY] == q["id"] and i[OPEN_WORK_KIND_KEY] in OPEN_WORK_GATE_RELEVANT_KINDS]`.
> Emit when `open_items` is non-empty.

The condition is the person's expiry **plus** open gate-relevant work; expiry alone is `L3-05-25`'s revocation plan, not an orphan.

**Frozen finding fields** — `subject = f"person:{q['id']}"` · `detail = "temporary person expired with open gate-relevant work"`

**Fixture mutations** — `-ORPHAN`: add `sec-1` (`employment_type: temporary_specialist`, `end_date: 2026-06-30`, `sponsor: dev-a`) plus an open-work snapshot containing one gate-relevant item held by `sec-1` and one non-gate-relevant item held by `sec-1`. Case `as_of` is `2026-08-27`. Expect exactly one finding. `-CLEAN`: same `sec-1` but the snapshot holds only the non-gate-relevant item.

**SELF-VERIFY** expected output, exactly:

```
ORPH-TEMP-EXPIRY-OPEN-WORK | High | Assignment registry + open reviews and gate items at expiry
N 1 person:sec-1 High
CLEAN 0
GUARD input_unavailable 0
```

---

### `L3-05-19` — Detector 15: `ORPH-POLICY` (Blocking)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d15-policy` · **Module:** `orph_policy.py`

**Constants** — `ORPHAN_TYPE = "ORPH-POLICY"` · `SEVERITY = "Blocking"` · `SOURCE = "Policy register"` · `REQUIRED_INPUTS = ("people.yaml", "policies.yaml")`

**Detection query** (Section 12.2 line 1008; policy schema Section 55.1 line 4839 `owner:`; Section 55.2 line 4875: *"Every policy has an owner."*)

> For every entry `pol` in `ctx.policies`: emit when `pol.get("owner")` is `None`/empty, **or** `holder_state(pol["owner"], ctx, as_of, mode) == "vacant"`.

**No status filter.** Section 12.2 attaches none, and Section 55.2 states the rule unconditionally. Do not exclude `superseded`, `withdrawn` or `retired` entries.

**Frozen finding fields** — `subject = f"policy:{pol['id']}"` · `detail = "policy has no owner or names a person who is not active"`

**Fixture mutations** — `-ORPHAN`: `policies.yaml` gains `POL-DEPLOY-FRIDAY` with `owner: dev-x` (departed) and `POL-X` with `owner: dev-a`. `-CLEAN`: both owned by `dev-a`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-POLICY | Blocking | Policy register
N 1 policy:POL-DEPLOY-FRIDAY Blocking
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-20` — Detector 16: `ORPH-EXCEPTION` (High)

**Size:** S · **Depends on:** `L3-05-04` · **Slug:** `d16-exception` · **Module:** `orph_exception.py`

**Constants** — `ORPHAN_TYPE = "ORPH-EXCEPTION"` · `SEVERITY = "High"` · `SOURCE = "Exception registry"` · `REQUIRED_INPUTS = ("people.yaml", "exceptions.yaml")`

**Detection query** (Section 12.2 line 1009 — *"Open exception whose requester or authority has departed"*; exception schema Section 54.1 lines 4757–4787, fields `requester`, `authority`, `closure`)

> An exception `e` is **open** when `e.get("closure")` is `None`. (`closure` is the schema's own open/closed field: *"closure: null # expired | remediated | promoted_to_policy | trigger_satisfied"*, line 4786.)
> For every open `e`: emit when `holder_state(e.get("requester"), ...) == "vacant"` **or** `holder_state(e.get("authority"), ...) == "vacant"`.
> Emit **one** finding per exception even when both are vacant; name which in `detail`.

**Frozen finding fields** — `subject = f"exception:{e['id']}"` · `detail` is exactly one of the three literals: `"open exception whose requester is not active"`, `"open exception whose authority is not active"`, `"open exception whose requester and authority are both not active"`.

**Fixture mutations** — `-ORPHAN`: `exceptions.yaml` gains `EXC-2026-041` (`requester: dev-x`, `authority: dev-a`, `closure: null`) and `EXC-2026-042` (`requester: dev-x`, `authority: dev-a`, `closure: expired`). Expect exactly one finding, for `EXC-2026-041`. `-CLEAN`: both entries `requester: dev-a`.

**SELF-VERIFY** expected output, exactly:

```
ORPH-EXCEPTION | High | Exception registry
N 1 exception:EXC-2026-041 High
DETAIL open exception whose requester is not active
CLEAN 0
GUARD input_unavailable ('people.yaml',) 0
```

---

### `L3-05-21` — Registry completeness and severity-conformance test

**Size:** S · **Depends on:** `L3-05-05` … `L3-05-20`
**Files created:** `reconciler/tests/orphans/test_registry_conformance.py`, `reconciler/orphans/SPEC-TABLE.md`

**What to build**

`reconciler/orphans/SPEC-TABLE.md` — the sixteen-row table of §2 above, reproduced verbatim with the line numbers, as the in-repo citation for anyone later tempted to change a severity.

`test_registry_conformance.py` — a single frozen tuple literal `SPEC_TABLE` of sixteen `(orphan_type, severity, source)` triples copied from §2, plus these tests:

1. `test_exactly_sixteen_detectors` — `len(DETECTORS) == 16`.
2. `test_types_match_spec_table` — the set of registered `ORPHAN_TYPE`s equals the set in `SPEC_TABLE`.
3. `test_severities_match_spec_table` — for each row, the registered module's `SEVERITY` equals the table's, compared byte-for-byte.
4. `test_sources_match_spec_table` — same for `SOURCE`.
5. `test_severity_tally` — `Blocking == 7`, `High == 7`, `Medium == 2`.
6. `test_no_severity_outside_vocabulary` — every `SEVERITY` is in `model.SEVERITIES`.
7. `test_base_fixture_is_clean` — `run_case("_BASE")["findings"] == []` with all sixteen registered.
8. `test_asset_detectors_partition` — on the `ORPH-ASSET-ORPHAN` fixture, the subject sets of `ORPH-CERTIFICATE`, `ORPH-DOMAIN`, `ORPH-VENDOR` and `ORPH-ASSET` are pairwise disjoint.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands** — the §6.3 block with slug `registry-conformance`, plus:

```bash
set -euo pipefail
python -m pytest reconciler/tests/orphans/test_registry_conformance.py -q
python -m pytest reconciler/tests -q
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Sixteen detectors registered | `python -c "import reconciler.orphans.detectors as _;from reconciler.orphans.registry import DETECTORS;print(len(DETECTORS))"` | `16` |
| 2 | Severity tally is 7/7/2 | SELF-VERIFY below | `Blocking 7 High 7 Medium 2` |
| 3 | Conformance tests pass | `python -m pytest reconciler/tests/orphans/test_registry_conformance.py -q \| tail -1` | contains `8 passed` |
| 4 | Whole suite green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed`, not `failed` |
| 5 | `SPEC-TABLE.md` committed | `grep -c '^| 16 ' reconciler/orphans/SPEC-TABLE.md` | `1` |
| 6 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
import collections
import reconciler.orphans.detectors as _
from reconciler.orphans.registry import DETECTORS
c = collections.Counter(m.SEVERITY for m in DETECTORS.values())
print("COUNT", len(DETECTORS))
print("Blocking", c["Blocking"], "High", c["High"], "Medium", c["Medium"])
print("SORTED", ",".join(sorted(DETECTORS)))
EOF
```

Expected output, exactly:

```
COUNT 16
Blocking 7 High 7 Medium 2
SORTED ORPH-ASSET,ORPH-BACKUP-OWNER,ORPH-CERTIFICATE,ORPH-COMMITMENT,ORPH-CROSS-REVIEWER,ORPH-DOMAIN,ORPH-EXCEPTION,ORPH-H1-WORK,ORPH-PLATFORM-MIGRATION,ORPH-POLICY,ORPH-PRIMARY-OWNER,ORPH-PRIMARY-RESPONDER,ORPH-SHARED-SERVICE,ORPH-TEMP-EXPIRY-OPEN-WORK,ORPH-VERIFICATION,ORPH-VENDOR
```

**STOP rule**
STOP if the count is not 16 or the tally is not 7/7/2. **Do not fix a tally mismatch by editing `SPEC_TABLE` — the table is the spec; fix the detector.** If you believe the spec table itself is wrong, that is an L0 decision, not an executor edit. §6.6 template, symptom `detector registry does not match Section 12.2 table`.

---

### `L3-05-22` — Prospective mode and the departing-person transfer worklist

**Size:** M · **Depends on:** `L3-05-21`
**Files created:** `reconciler/orphans/prospective.py`, `reconciler/tests/orphans/test_prospective.py`, fixtures `PROSPECTIVE-DEPARTING/**`, `PROSPECTIVE-NO-DEPARTING/**`

**Spec** — Section 12.2 line 985: *"Orphan detection runs immediately when `availability` becomes `departing`, in prospective mode against the declared `end_date`: it emits the transfer worklist — every responsibility that would orphan on that date — so the knowledge-transfer window works from a generated list for the notice period, not from memory."*

**What to build**

- `@dataclass(frozen=True) class TransferWorklist`: `person_id: str`, `end_date: str`, `findings: tuple[OrphanFinding, ...]`.
- `def departing_people(ctx) -> list[dict]` — every person with `availability == "departing"`, sorted by `id`. A departing person with `end_date is None` is **not** skipped: it produces a `TransferWorklist` with `end_date = None` and a single synthetic entry is **not** invented — instead the function raises `MissingEndDateError(person_id)`, because Section 12.2 requires the prospective run to be *"against the declared `end_date`"* and there is nothing to run against. The caller (`T29` CLI) converts that to exit code `1`.
- `def transfer_worklist(root, person, as_of_override=None) -> TransferWorklist` — reloads the control plane with `mode="prospective"` and `as_of = person["end_date"]`, runs all sixteen detectors, and keeps only findings whose subject is affected by that person. "Affected by that person" is computed structurally, with **no** guessing: a finding is kept when re-running the same detector against a copy of the control plane in which that one person is forced to `availability: active, access_status: provisioned` makes the finding disappear. This differential test is the definition; implement it literally.
- `def all_transfer_worklists(root) -> list[TransferWorklist]` — one per departing person, sorted by `person_id`.

**Fixtures**

| Case | Content | Expected |
| --- | --- | --- |
| `PROSPECTIVE-DEPARTING` | `_BASE` plus `dev-a` set to `availability: departing`, `end_date: 2026-09-30`. `dev-a` holds `primary_owner`, `cross_reviewer` is `dev-b` (active), `backup_owner` is `dev-a`, `verification_responsibility` is `dev-a`, `operations.primary_responder: dev-a`, `svc-1` `primary_owner: dev-a`. | A single worklist for `dev-a`, `end_date 2026-09-30`, containing exactly five findings: `ORPH-PRIMARY-OWNER`, `ORPH-BACKUP-OWNER`, `ORPH-PRIMARY-RESPONDER`, `ORPH-VERIFICATION`, `ORPH-SHARED-SERVICE`. |
| `PROSPECTIVE-NO-DEPARTING` | `_BASE` unchanged. | Zero worklists. |

Both cases carry a hand-authored `expected-worklists.json`.

**Additional required test:** running the **current-mode** detectors against `PROSPECTIVE-DEPARTING` at `as_of 2026-08-27` yields **zero** findings — a departing person still holds their responsibilities today. This is the test that proves prospective mode is doing real work.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands** — §6.3 block, slug `prospective`, then:

```bash
set -euo pipefail
python -m pytest reconciler/tests/orphans/test_prospective.py -q
python -m pytest reconciler/tests -q
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Departing person produces a worklist | SELF-VERIFY | `WORKLISTS 1 dev-a 2026-09-30 5` |
| 2 | Current mode is clean on the same fixture | SELF-VERIFY | `CURRENT 0` |
| 3 | Clean control plane produces no worklist | SELF-VERIFY | `NONE 0` |
| 4 | Missing `end_date` raises rather than guessing | SELF-VERIFY | `ENDDATE-GUARD OK` |
| 5 | Test file passes | `python -m pytest reconciler/tests/orphans/test_prospective.py -q \| tail -1` | contains `4 passed` |
| 6 | Whole suite green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed`, not `failed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
import reconciler.orphans.detectors as _
from reconciler.orphans.loader import load_control_plane
from reconciler.orphans.registry import run_all
from reconciler.orphans.prospective import all_transfer_worklists, MissingEndDateError, departing_people
B = Path('reconciler/tests/fixtures/orphans')
wls = all_transfer_worklists(B/'PROSPECTIVE-DEPARTING')
print("WORKLISTS", len(wls), wls[0].person_id, wls[0].end_date, len(wls[0].findings))
print("TYPES", ",".join(sorted(f.orphan_type for f in wls[0].findings)))
ctx = load_control_plane(B/'PROSPECTIVE-DEPARTING', date(2026,8,27), 'current')
print("CURRENT", sum(len(r.findings) for r in run_all(ctx)))
print("NONE", len(all_transfer_worklists(B/'PROSPECTIVE-NO-DEPARTING')))
try:
    all_transfer_worklists(B/'PROSPECTIVE-NO-ENDDATE'); print("ENDDATE-GUARD FAIL")
except MissingEndDateError: print("ENDDATE-GUARD OK")
EOF
```

Expected output, exactly:

```
WORKLISTS 1 dev-a 2026-09-30 5
TYPES ORPH-BACKUP-OWNER,ORPH-PRIMARY-OWNER,ORPH-PRIMARY-RESPONDER,ORPH-SHARED-SERVICE,ORPH-VERIFICATION
CURRENT 0
NONE 0
ENDDATE-GUARD OK
```

(create the tiny third fixture `PROSPECTIVE-NO-ENDDATE` — `_BASE` with `dev-a` `availability: departing`, `end_date: null` — as part of this task)

**STOP rule**
STOP if current mode reports findings for a merely-departing person (that would make every notice period look like a live outage), or if a departing person with a null `end_date` silently produces an empty worklist. **Do not default a missing `end_date` to today, to the run date, or to any other value.** §6.6 template, symptom `prospective mode conflates departing with departed`.

---

### `L3-05-23` — Orphan report and event payload emitter

**Size:** M · **Depends on:** `L3-05-21`
**Files created:** `reconciler/orphans/report.py`, `reconciler/orphans/events.py`, `reconciler/tests/orphans/test_report.py`, `reconciler/tests/orphans/test_events.py`

**What to build**

`report.py`:

- `@dataclass(frozen=True) class OrphanReport`: `as_of: str`, `mode: str`, `findings: tuple[OrphanFinding, ...]`, `input_unavailable: tuple[str, ...]` (each entry formatted `"<ORPHAN-TYPE>: <missing input>"`), `counts: dict[str, int]` (keys exactly `Blocking`, `High`, `Medium`).
- `def build_report(results, as_of, mode) -> OrphanReport` — findings passed through `sort_findings`.
- `def blocking_open(report) -> tuple[OrphanFinding, ...]` — the `Blocking` findings.
- `def to_json(report) -> str` — `json.dumps(..., indent=2, sort_keys=True)`; the only serialisation used anywhere in this phase.
- `def to_text(report) -> str` — one line per finding: `f"{severity}\t{orphan_type}\t{subject}\t{detail}"`, preceded by a header `f"orphan report as_of={as_of} mode={mode} blocking={n} high={n} medium={n}"`, and — when `input_unavailable` is non-empty — a final block headed `INPUT UNAVAILABLE (this report is incomplete):` listing each entry. The incompleteness banner is mandatory; a partial report must never print as if it were whole.

`events.py`:

- `EVENT_TYPES` — a frozen mapping of this phase's four event names, each value copied **verbatim** from the Section 97.3 taxonomy list at line 8952: `"orphan detected"`, `"orphan resolved"`, `"delegation expiry warning issued"`, `"temporary-person expiry warning issued"`.
- `def orphan_detected_payloads(report) -> list[dict]` — one payload per finding: `{"event_type": EVENT_TYPES["orphan_detected"], "event_schema_version": 1, "timestamp": <UTC ISO-8601 with offset>, "subject": ..., "orphan_type": ..., "severity": ..., "detail": ..., "source": ..., "as_of": ..., "mode": ...}`.
- `def orphan_resolved_payloads(previous: OrphanReport, current: OrphanReport) -> list[dict]` — one payload per `finding_key` present in `previous` and absent from `current`.
- `def write_payloads(payloads, out_path: Path) -> None` — writes one JSON object per line to a **local file only**.

**Hard boundary, restated in the module docstring of `events.py`:** these are payload files for a workflow to consume. The records repository and the `events/` store are owned by L4 (PARTITION.md line 20) and written by the records-writer credential from a workflow (Section 97.1 line 8840, D89). `events.py` must not contain a repository path, a credential name, a URL, or a `git` invocation.

**Timestamp rule** — Section 97.1 line 8837: *"Every record and event timestamp is stored in UTC with its offset"*. Use `datetime.now(timezone.utc).isoformat()`. Tests inject a fixed clock; no test asserts on wall-clock time.

**`event_type` token caveat** — Section 52.6 records that the closed `event_type` enum lives in `platform.yaml`, owned by the Team Lead. This phase emits the Section 97.3 phrase verbatim. If control-plane CI later rejects a token, that is a token-vocabulary mismatch: open a blocker (§6.6, symptom `event_type token rejected by platform.yaml enum`) rather than inventing a substitute.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Counts are exact | SELF-VERIFY | `COUNTS {'Blocking': 1, 'High': 0, 'Medium': 0}` |
| 2 | Incomplete report is banner-marked | SELF-VERIFY | `BANNER True` |
| 3 | Four event types, verbatim | `python -c "from reconciler.orphans.events import EVENT_TYPES;print(sorted(EVENT_TYPES.values()))"` | `['delegation expiry warning issued', 'orphan detected', 'orphan resolved', 'temporary-person expiry warning issued']` |
| 4 | `orphan resolved` fires on disappearance | SELF-VERIFY | `RESOLVED 1 ORPH-PRIMARY-OWNER` |
| 5 | No repository/credential/URL string in `events.py` | `grep -c -E 'control-plane-records\|records-writer\|https?://\|subprocess\|git ' reconciler/orphans/events.py` | `0` |
| 6 | Tests pass | `python -m pytest reconciler/tests/orphans/test_report.py reconciler/tests/orphans/test_events.py -q \| tail -1` | contains `passed`, not `failed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
import reconciler.orphans.detectors as _
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.orphans.registry import run_all
from reconciler.orphans.report import build_report, to_text, blocking_open
from reconciler.orphans.events import orphan_resolved_payloads, EVENT_TYPES
B = Path('reconciler/tests/fixtures/orphans')
ctx = load_control_plane(B/'ORPH-PRIMARY-OWNER-ORPHAN', date(2026,8,27), 'current')
rep = build_report([r for r in run_all(ctx) if r.orphan_type=='ORPH-PRIMARY-OWNER'], '2026-08-27','current')
print("COUNTS", rep.counts)
print("BLOCKING", len(blocking_open(rep)))
inc = build_report(run_all(ctx), '2026-08-27','current')
print("BANNER", "INPUT UNAVAILABLE" in to_text(inc))
clean = build_report([], '2026-08-27','current')
res = orphan_resolved_payloads(rep, clean)
print("RESOLVED", len(res), res[0]["orphan_type"])
print("EVENT", res[0]["event_type"] == EVENT_TYPES["orphan_resolved"])
EOF
```

Expected output, exactly:

```
COUNTS {'Blocking': 1, 'High': 0, 'Medium': 0}
BLOCKING 1
BANNER True
RESOLVED 1 ORPH-PRIMARY-OWNER
EVENT True
```

**STOP rule**
STOP if a report containing `input_unavailable` entries renders without the incompleteness banner, or if `events.py` contains any repository path, credential name or network string. **This phase does not write events to any repository.** §6.6 template, symptom `report or event emitter crosses the lane boundary`.

---

### `L3-05-24` — Blocking-orphan dismissal guard

**Size:** M · **Depends on:** `L3-05-23`
**Files created:** `reconciler/orphans/dismissal.py`, `reconciler/tests/orphans/test_dismissal.py`, fixture `reconciler/tests/fixtures/dismissals/*.json`

**Spec** — Section 12.2 line 1011: *"Blocking orphans appear on the Founder View's product attention dimension as Action Required and **cannot be dismissed without resolution**"*. Invariant **57** (line 9528): *"blocking orphans cannot be dismissed unresolved."* **AT-017** (line 9326) tests it.

**Frozen dismissal-file shape** (this phase defines it; it is a lane-local input, not a control-plane registry):

```json
{
  "dismissals": [
    {
      "orphan_type": "ORPH-BACKUP-OWNER",
      "subject": "product:product-1",
      "dismissed_by": "lead-1",
      "dismissed_on": "2026-08-27",
      "reason": "backup owner named in DEC-2026-08-22; registry edit lands Friday"
    }
  ]
}
```

**What to build**

- `def load_dismissals(path) -> list[dict]` — missing file returns `[]`; malformed file raises `DismissalParseError`.
- `def evaluate_dismissals(report, dismissals) -> DismissalOutcome`, where `DismissalOutcome` is a frozen dataclass with `accepted: tuple[dict, ...]`, `rejected: tuple[dict, ...]`, `unknown: tuple[dict, ...]`.
  - A dismissal is **rejected** when its `(orphan_type, subject)` matches a finding in `report` whose `severity == "Blocking"`. This is the invariant. There is no override flag, no force option, no environment variable, and no configuration key that changes it. Do not add one.
  - A dismissal is **accepted** when it matches a finding whose severity is `High` or `Medium`.
  - A dismissal is **unknown** when it matches no finding in the report (the orphan is already resolved, or the dismissal is stale).
- `def dismissal_exit_code(outcome) -> int` — `2` when `rejected` is non-empty, else `0`.
- `def rejection_text(outcome) -> str` — one line per rejection: `f"REJECTED\t{orphan_type}\t{subject}\tBlocking orphans cannot be dismissed unresolved (Section 12.2; invariant 57)"`.

**Required tests** — at minimum: a `Blocking` dismissal is rejected; a `High` dismissal is accepted; a `Medium` dismissal is accepted; a dismissal of a resolved orphan is `unknown`; a missing dismissal file yields `[]` and exit `0`; a dismissal file with an extra key `"force": true` **still rejects** a `Blocking` dismissal (this test exists specifically to prove no override path was added).

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Blocking dismissal rejected | SELF-VERIFY | `BLOCKING rejected` |
| 2 | High dismissal accepted | SELF-VERIFY | `HIGH accepted` |
| 3 | `force` key changes nothing | SELF-VERIFY | `FORCE rejected` |
| 4 | Exit code on rejection is 2 | SELF-VERIFY | `EXIT 2` |
| 5 | No override switch exists anywhere in the module | `grep -c -i -E 'force\|override\|bypass\|ignore_blocking\|--yes' reconciler/orphans/dismissal.py` | `0` |
| 6 | Tests pass | `python -m pytest reconciler/tests/orphans/test_dismissal.py -q \| tail -1` | contains `6 passed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

(criterion 5's grep runs against the module only — the *test* file legitimately contains the word `force`.)

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from reconciler.orphans.model import OrphanFinding
from reconciler.orphans.report import build_report
from reconciler.orphans.dismissal import evaluate_dismissals, dismissal_exit_code
f_block = OrphanFinding("ORPH-PRIMARY-OWNER","Blocking","product:product-1","d","Assignment registry","2026-08-27","current")
f_high  = OrphanFinding("ORPH-BACKUP-OWNER","High","product:product-1","d","Assignment registry","2026-08-27","current")
class R: pass
rep = build_report([], "2026-08-27", "current")
rep = type(rep)(rep.as_of, rep.mode, (f_block, f_high), (), {"Blocking":1,"High":1,"Medium":0})
d_block = {"orphan_type":"ORPH-PRIMARY-OWNER","subject":"product:product-1","dismissed_by":"lead-1","dismissed_on":"2026-08-27","reason":"x"}
d_high  = {"orphan_type":"ORPH-BACKUP-OWNER","subject":"product:product-1","dismissed_by":"lead-1","dismissed_on":"2026-08-27","reason":"x"}
d_force = dict(d_block); d_force["force"] = True
o = evaluate_dismissals(rep, [d_block, d_high, d_force])
print("BLOCKING", "rejected" if d_block in o.rejected else "accepted")
print("HIGH", "accepted" if d_high in o.accepted else "rejected")
print("FORCE", "rejected" if d_force in o.rejected else "accepted")
print("EXIT", dismissal_exit_code(o))
EOF
```

Expected output, exactly:

```
BLOCKING rejected
HIGH accepted
FORCE rejected
EXIT 2
```

**STOP rule**
STOP if any input, flag, key or configuration causes a `Blocking` dismissal to be accepted. **Invariant 57 has no exception clause and this task must not introduce one; if a caller appears to require one, that is an L0 decision.** §6.6 template, symptom `a path exists that dismisses a Blocking orphan`.

---

### `L3-05-25` — Expiry scan → revocation plan (no execution)

**Size:** M · **Depends on:** `L3-05-03`, `L3-05-21`
**Files created:** `reconciler/expiry/plan.py`, `reconciler/expiry/scan.py`, `reconciler/tests/expiry/__init__.py`, `reconciler/tests/expiry/test_scan.py`, fixtures `reconciler/tests/fixtures/expiry/EXPIRY-MIXED/**`, `EXPIRY-CLEAN/**`

**Spec** — Section 12.4 line 1052 (*"Reconciliation revokes access on the date. No human action required"*); invariant **58** (line 9529); Section 10.2 line 792 (*"Temporary assignments … expire and are removed by reconciliation"*); Section 54.2 line 4789 (auto-revocable exception types, and Blocking drift where auto-revocation is impossible); AT-008, AT-018, AT-036, AT-037; Section 53.2 Level 4 line 4697 (*"expired non-employee access still provisioned"* is Blocking-class drift).

**What to build**

`plan.py`:

- `@dataclass(frozen=True) class PlannedAction`: `action: str`, `target: str`, `reason: str`, `effective: str`, `severity_if_unexecuted: str`.
- `ACTIONS` — the frozen closed set of four action tokens this phase may emit: `"revoke_person_access"`, `"remove_assignment"`, `"revert_exception"`, `"flag_blocking_drift"`. `PlannedAction.__post_init__` rejects anything else.
- `@dataclass(frozen=True) class RevocationPlan`: `as_of: str`, `actions: tuple[PlannedAction, ...]`, `missing_inputs: tuple[str, ...]`.
- `def to_json(plan) -> str` — `json.dumps(..., indent=2, sort_keys=True)`.
- **`plan.py` contains no execution function of any kind.** No `apply`, `execute`, `run`, `commit`, or `revoke` that does anything but build data. The module docstring states: *"This module builds a plan. Executing a plan is the reconciler apply layer's job (subsystem C). Adding execution here violates Section 99.6 risk 6 and task L3-05-28 will fail."*

`scan.py` — `def scan_expiries(ctx) -> RevocationPlan`, emitting, in this order:

| Source | Condition | Action | `severity_if_unexecuted` |
| --- | --- | --- | --- |
| `people.yaml` | `end_date` is not null **and** `end_date <= as_of` **and** `access_status != "revoked"` | `revoke_person_access`, target `person:<id>` | `Blocking` (Section 53.2 line 4697: *"expired non-employee access still provisioned"*) |
| every `product.yaml` `assignments[]` | `end_date` is not null **and** `end_date < as_of` | `remove_assignment`, target `assignment:<product-id>/<person>/<type>/<end_date>` | `High` |
| every `service.yaml` `assignments[]` | same | `remove_assignment`, target `assignment:service:<service-id>/<person>/<type>/<end_date>` | `High` |
| `exceptions.yaml` | `closure is None` **and** `expiry <= as_of` **and** `type in AUTO_REVOCABLE_EXCEPTION_TYPES` | `revert_exception`, target `exception:<id>` | `Blocking` |
| `exceptions.yaml` | `closure is None` **and** `expiry <= as_of` **and** `type not in AUTO_REVOCABLE_EXCEPTION_TYPES` | `flag_blocking_drift`, target `exception:<id>` | `Blocking` (AT-037 line 9359) |

`AUTO_REVOCABLE_EXCEPTION_TYPES = ("temporary_access", "platform_compatibility")` — the two type tokens named at Section 54.2 line 4789 (*"Temporary access, temporary assignments and platform compatibility waivers are revoked or reverted by reconciliation at expiry"*) that appear in the Section 54.1 `type` enum (line 4759). *Temporary assignments* are covered by the two `remove_assignment` rows above, not by an exception type.

`reason` strings are frozen: `"non-employee end_date reached; access still provisioned"`, `"assignment end_date passed"`, `"exception expired and its type is auto-revocable"`, `"exception expired and cannot be auto-revoked (Section 54.2)"`.

**Fixtures** — `EXPIRY-MIXED` (`as_of 2026-08-27`) contains: `sec-1` expired `2026-06-30` still `provisioned`; `dev-a` employee, `end_date: null`; one product assignment `temporary_contributor` for `dev-c` ending `2026-06-15`; one open exception `EXC-A` `type: temporary_access` `expiry: 2026-07-01`; one open exception `EXC-B` `type: break_glass` `expiry: 2026-07-01`; one closed exception `EXC-C` `type: temporary_access` `expiry: 2026-01-01` `closure: expired`. Expected: exactly four actions. `EXPIRY-CLEAN`: nothing expired; zero actions. Both carry hand-authored `expected-plan.json`.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Mixed fixture plans exactly four actions | SELF-VERIFY | `ACTIONS 4` |
| 2 | Action tokens are the closed set | SELF-VERIFY | `TOKENS flag_blocking_drift,remove_assignment,revert_exception,revoke_person_access` |
| 3 | Non-auto-revocable expiry becomes Blocking drift, not a revoke | SELF-VERIFY | `EXC-B flag_blocking_drift Blocking` |
| 4 | Closed exception is ignored | SELF-VERIFY | `EXC-C absent` |
| 5 | Clean fixture plans nothing | SELF-VERIFY | `CLEAN 0` |
| 6 | No execution symbol in either module | `grep -c -E 'def (apply\|execute\|commit\|revoke_now)\|requests\|httpx\|urllib\|subprocess\|Github\|github3' reconciler/expiry/plan.py reconciler/expiry/scan.py` | `0` on both files |
| 7 | Tests pass | `python -m pytest reconciler/tests/expiry/test_scan.py -q \| tail -1` | contains `passed`, not `failed` |
| 8 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.expiry.scan import scan_expiries
B = Path('reconciler/tests/fixtures/expiry')
p = scan_expiries(load_control_plane(B/'EXPIRY-MIXED', date(2026,8,27),'current'))
print("ACTIONS", len(p.actions))
print("TOKENS", ",".join(sorted({a.action for a in p.actions})))
b = [a for a in p.actions if a.target=='exception:EXC-B'][0]
print("EXC-B", b.action, b.severity_if_unexecuted)
print("EXC-C", "present" if any(a.target=='exception:EXC-C' for a in p.actions) else "absent")
print("CLEAN", len(scan_expiries(load_control_plane(B/'EXPIRY-CLEAN', date(2026,8,27),'current')).actions))
EOF
```

Expected output, exactly:

```
ACTIONS 4
TOKENS flag_blocking_drift,remove_assignment,revert_exception,revoke_person_access
EXC-B flag_blocking_drift Blocking
EXC-C absent
CLEAN 0
```

**STOP rule**
STOP if you find yourself needing to call GitHub, run `git`, or write anything outside the plan file to make this task pass. **Execution is not in this phase.** Also STOP if an expired exception of a non-auto-revocable type is planned as `revert_exception`: AT-037 requires it to become Blocking drift instead. §6.6 template, symptom `expiry scan attempts execution or mis-classifies a non-revocable exception`.

---

### `L3-05-26` — 14-day delegation expiry warning — **DR-L3-05-B blocked**

**Size:** M · **Depends on:** `L3-05-25`
**Files created:** `reconciler/expiry/warnings.py` (created here, extended by `T27`), `reconciler/tests/expiry/test_delegation_warning.py`, fixtures `DELEGATION-WARN/**`, `DELEGATION-NO-WARN/**`

**Step 0 — decision gate.**

```bash
set -euo pipefail
python -c "import reconciler.orphans.decisions as d; print('DELEG-DR', d.DELEGATION_WARNING_TYPES is not None)"
```

If `DELEG-DR False`, STOP and open the blocker with `DECISION REQUIRED ID: DR-L3-05-B`.

**Spec** — Section 10.1 line 787: *"**Delegation expiry is warned, never silent.** Every delegation-type assignment receives a 14-day advance expiry warning in the daily expiry check, exactly as expiring assets do (Section 49). When an expired delegation bounces an approval, the error surface is a named exception prompt — identifying the expired assignment, its holder and its expiry date — never a silent failure."*

**What to build**

- `WARNING_LEAD_DAYS_DELEGATION = 14` — a module constant with the Section 10.1 line-787 citation in a comment. It is not configurable in this phase.
- `@dataclass(frozen=True) class ExpiryWarning`: `kind: str` (`"delegation"` or `"temporary_person"`), `subject: str`, `holder: str`, `expiry: str`, `days_remaining: int`, `recipient: str`, `detail: str`, `open_items: tuple[str, ...]`.
- `def delegation_warnings(ctx) -> list[ExpiryWarning]`:
  > For every product and service, for every assignment `a` with `a["type"] in decisions.DELEGATION_WARNING_TYPES` and `a.get("end_date")` not null:
  > let `days = (end_date - as_of).days`; emit when `0 <= days <= WARNING_LEAD_DAYS_DELEGATION`.
  > `subject = f"assignment:{scope_id}/{a['person']}/{a['type']}"`, `holder = a["person"]`, `recipient = a["person"]`, `open_items = ()`,
  > `detail = f"delegation {a['type']} on {scope_id} held by {a['person']} expires {end_date} ({days} days)"`.
- The window is inclusive at both ends: `days == 14` warns (the advance warning) and `days == 0` warns (expiry day). `days == 15` does not; `days == -1` does not — an already-expired delegation is `L3-05-25`'s `remove_assignment`, not a warning.
- Warnings are sorted by `(expiry, subject)`.
- `def warning_payloads(warnings) -> list[dict]` — event payloads using `EVENT_TYPES["delegation_expiry_warning_issued"]` (the verbatim Section 97.3 phrase `delegation expiry warning issued`, line 8952). Payload files only; see `T23`'s boundary note.

**Fixtures** — `DELEGATION-WARN` (`as_of 2026-08-27`): four delegation-type assignments with `end_date` of `2026-09-10` (14 days), `2026-08-27` (0 days), `2026-09-11` (15 days) and `2026-08-26` (−1 day). Expect exactly **two** warnings. `DELEGATION-NO-WARN`: the same four assignments but with a non-delegation `type`, expect **zero**.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Lead time is exactly 14 | `python -c "from reconciler.expiry.warnings import WARNING_LEAD_DAYS_DELEGATION as d;print(d)"` | `14` |
| 2 | Boundaries inclusive at 14 and 0, exclusive at 15 and −1 | SELF-VERIFY | `WARN 2 0,14` |
| 3 | Non-delegation types never warn | SELF-VERIFY | `NOWARN 0` |
| 4 | Event token verbatim | SELF-VERIFY | `EVENT delegation expiry warning issued` |
| 5 | Tests pass | `python -m pytest reconciler/tests/expiry/test_delegation_warning.py -q \| tail -1` | contains `passed`, not `failed` |
| 6 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.expiry.warnings import delegation_warnings, warning_payloads, WARNING_LEAD_DAYS_DELEGATION
B = Path('reconciler/tests/fixtures/expiry')
w = delegation_warnings(load_control_plane(B/'DELEGATION-WARN', date(2026,8,27),'current'))
print("LEAD", WARNING_LEAD_DAYS_DELEGATION)
print("WARN", len(w), ",".join(str(x.days_remaining) for x in sorted(w, key=lambda x: x.days_remaining)))
print("NOWARN", len(delegation_warnings(load_control_plane(B/'DELEGATION-NO-WARN', date(2026,8,27),'current'))))
print("EVENT", warning_payloads(w)[0]["event_type"])
EOF
```

Expected output, exactly:

```
LEAD 14
WARN 2 0,14
NOWARN 0
EVENT delegation expiry warning issued
```

**STOP rule**
STOP if `DELEGATION_WARNING_TYPES` is `None`, or if you conclude the correct lead time is not 14. **Section 10.1 line 787 states 14; do not make it configurable, do not read it from a registry, and do not align it with the 30-day asset threshold of Section 49.1 — those are different clocks on different objects.** §6.6 template, symptom `delegation warning window cannot be implemented as 14 days`.

---

### `L3-05-27` — T-minus-7 temporary-person expiry warning to sponsor — **DR-L3-05-D blocked**

**Size:** M · **Depends on:** `L3-05-25`, `L3-05-18`
**Files modified:** `reconciler/expiry/warnings.py` · **Files created:** `reconciler/tests/expiry/test_temp_person_warning.py`, fixtures `TEMP-WARN/**`, `TEMP-NO-SPONSOR/**`

**Spec** — Section 12.4 line 1057: *"Reconciliation emits a T-minus-7-day expiry warning to the sponsor, listing the person's open pull requests and open reviews, so expiry never strands in-flight work."* Section 12.4 sponsor row (line 1055): *"Mandatory `sponsor:` field naming the internal contact"*. EC-111 (line 9769): *"Orphan detection warns the assignment's sponsor at T-minus-7 days"*.

**What to build**

- `WARNING_LEAD_DAYS_TEMPORARY_PERSON = 7` — constant with the line-1057 citation.
- `def temporary_person_warnings(ctx) -> list[ExpiryWarning]`:
  > For every person `q` with `q["employment_type"] in TEMPORARY_EMPLOYMENT_TYPES` (the same four tokens frozen in `T18`) and `q.get("end_date")` not null:
  > let `days = (end_date - as_of).days`; emit when `0 <= days <= 7`.
  > `subject = f"person:{q['id']}"`, `holder = q["id"]`, `recipient = q["sponsor"]`,
  > `open_items = tuple(sorted(i[OPEN_WORK_ID_KEY] for i in ctx.open_work if i[OPEN_WORK_HOLDER_KEY] == q["id"]))` — **all** the person's open items, not only gate-relevant ones, because line 1057 says *"open pull requests and open reviews"*,
  > `detail = f"temporary person {q['id']} expires {end_date} ({days} days); {len(open_items)} open item(s)"`.
- **Missing sponsor:** if `q.get("sponsor")` is absent or empty, emit the warning with `recipient = ""` **and** set `detail` to the frozen literal `f"temporary person {q['id']} expires {end_date} ({days} days); NO SPONSOR RECORDED"`. Never silently drop the warning, and never substitute another recipient — Section 12.4 makes `sponsor` mandatory, so its absence is an L1 registry-validation failure that must remain visible here rather than be papered over.
- `warning_payloads` (from `T26`) handles both kinds; the temporary-person kind uses `EVENT_TYPES["temporary_person_expiry_warning_issued"]` (verbatim `temporary-person expiry warning issued`, line 8952).

**Fixtures** — `TEMP-WARN` (`as_of 2026-08-27`): `sec-1` `temporary_specialist` `end_date 2026-09-03` (7 days) `sponsor: dev-a` with two open items; `sec-2` `contractor` `end_date 2026-09-04` (8 days) — no warning; `dev-a` `employee` `end_date: null` — no warning. Expect exactly **one** warning with two `open_items`. `TEMP-NO-SPONSOR`: `sec-1` as above but `sponsor` absent. Expect one warning with `recipient == ""` and the `NO SPONSOR RECORDED` detail.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Lead time is exactly 7 | `python -c "from reconciler.expiry.warnings import WARNING_LEAD_DAYS_TEMPORARY_PERSON as d;print(d)"` | `7` |
| 2 | Warning goes to the sponsor and lists open items | SELF-VERIFY | `WARN 1 dev-a 2` |
| 3 | Eight days out does not warn | SELF-VERIFY | `WARN 1 dev-a 2` (only `sec-1`) |
| 4 | Missing sponsor is loud, not silent | SELF-VERIFY | `NOSPONSOR 1 '' NO SPONSOR RECORDED` |
| 5 | Event token verbatim | SELF-VERIFY | `EVENT temporary-person expiry warning issued` |
| 6 | Tests pass | `python -m pytest reconciler/tests/expiry/test_temp_person_warning.py -q \| tail -1` | contains `passed`, not `failed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.expiry.warnings import temporary_person_warnings, warning_payloads, WARNING_LEAD_DAYS_TEMPORARY_PERSON
B = Path('reconciler/tests/fixtures/expiry')
print("LEAD", WARNING_LEAD_DAYS_TEMPORARY_PERSON)
w = temporary_person_warnings(load_control_plane(B/'TEMP-WARN', date(2026,8,27),'current'))
print("WARN", len(w), w[0].recipient, len(w[0].open_items))
n = temporary_person_warnings(load_control_plane(B/'TEMP-NO-SPONSOR', date(2026,8,27),'current'))
print("NOSPONSOR", len(n), repr(n[0].recipient), "NO SPONSOR RECORDED" in n[0].detail)
print("EVENT", warning_payloads(w)[0]["event_type"])
EOF
```

Expected output, exactly:

```
LEAD 7
WARN 1 dev-a 2
NOSPONSOR 1 '' True
EVENT temporary-person expiry warning issued
```

**STOP rule**
STOP if a temporary person with no `sponsor` produces no warning, or if you are tempted to route the warning to the Team Lead, the Primary Owner, or anyone the spec does not name. **Line 1057 names the sponsor and nobody else; a missing sponsor is a visible defect, not a routing puzzle.** §6.6 template, symptom `temporary-person warning has no recipient and no defined behaviour`.

---

### `L3-05-28` — No-network / no-write safety test

**Size:** S · **Depends on:** `L3-05-27`
**Files created:** `reconciler/tests/test_no_write_boundary.py`

**Spec** — Section 99.6 risk 6, line 9282 (*"the reconciler is the highest-privilege identity in the system … Detect-only first"*); Section 99.4 item 6, line 9257 (*"detect and block only … auto-repair is the riskiest code in the system"*); Section 98.2 Phase 3, line 9043 (*"Auto-repair is not built here"*).

**What to build** — an AST-based test (not a grep) that walks every `*.py` file under `reconciler/orphans/` and `reconciler/expiry/` and asserts:

1. **No forbidden import**, at module level or inside a function: `requests`, `httpx`, `urllib`, `urllib3`, `http`, `socket`, `ftplib`, `smtplib`, `subprocess`, `github`, `github3`, `pygithub`, `paramiko`, `boto3`.
2. **No `os.system`, `os.popen`, `os.exec*`, `os.spawn*`, or `eval`/`exec` call.**
3. **No `open(..., mode)` where mode contains `w`, `a`, `x` or `+`** — except in the explicitly allow-listed writers `reconciler/orphans/events.py` (`write_payloads`) and `reconciler/expiry/plan.py` (`to_json` returns a string and must not open a file at all — so only `events.py` is allow-listed). The allow-list is a module-level frozen set in the test file with a comment explaining each entry.
4. **No string literal matching `^https?://` or containing `api.github.com`.**
5. Every detector module exposes `detect` and nothing named `apply`, `execute`, `repair`, or `revoke`.

The test reports every violation with file and line number, and fails on the first non-empty violation list.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Boundary test passes on the current tree | `python -m pytest reconciler/tests/test_no_write_boundary.py -q \| tail -1` | contains `5 passed` |
| 2 | The test actually catches a violation | insert `import requests` at the top of `reconciler/orphans/report.py`, re-run | test **fails**, naming `report.py` and the line; **remove the import afterwards** |
| 3 | Allow-list is exactly one entry | `python -c "import reconciler.tests.test_no_write_boundary as t;print(sorted(t.WRITE_ALLOWLIST))"` | `['reconciler/orphans/events.py']` |
| 4 | Whole suite green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed`, not `failed` |
| 5 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python -m pytest reconciler/tests/test_no_write_boundary.py -q | tail -1
python -c "import reconciler.tests.test_no_write_boundary as t;print('ALLOWLIST', sorted(t.WRITE_ALLOWLIST))"
printf '\nimport requests\n' >> reconciler/orphans/report.py
python -m pytest reconciler/tests/test_no_write_boundary.py -q > /tmp/nb.txt 2>&1; echo "EXIT $?"
grep -c "report.py" /tmp/nb.txt
git checkout -- reconciler/orphans/report.py
python -m pytest reconciler/tests/test_no_write_boundary.py -q | tail -1
```

Expected output (the middle `EXIT` must be non-zero and the grep must be at least 1):

```
5 passed in 0.0Xs
ALLOWLIST ['reconciler/orphans/events.py']
EXIT 1
1
5 passed in 0.0Xs
```

**STOP rule**
STOP if the boundary test passes while `import requests` is present in a scanned module — the test is not doing its job and every safety claim in this phase rests on it. **Do not widen `WRITE_ALLOWLIST` to make another module pass; move the write into `events.py` or remove it.** §6.6 template, symptom `no-write boundary test does not detect a network import`.

---

### `L3-05-29` — CLI, exit codes and machine-readable output

**Size:** M · **Depends on:** `L3-05-22`, `L3-05-23`, `L3-05-24`, `L3-05-25`, `L3-05-26`, `L3-05-27`
**Files created:** `reconciler/orphans/cli.py`, `reconciler/tests/test_cli.py`

**Subcommands** (argparse; no third-party CLI library)

| Command | Arguments | Does | Exit codes |
| --- | --- | --- | --- |
| `detect` | `--root PATH` (required), `--as-of YYYY-MM-DD` (default: UTC today), `--format json\|text` (default `text`), `--out PATH` (optional) | Runs all sixteen detectors in `current` mode, prints the report | §6.7 |
| `prospective` | `--root PATH`, `[--person ID]`, `--format`, `--out` | Emits transfer worklists for every departing person, or the named one | §6.7; `1` on `MissingEndDateError` |
| `expiry` | `--root PATH`, `--as-of`, `--format`, `--out` | Prints the revocation plan. **Never executes it.** Exit `2` when any action carries `severity_if_unexecuted == "Blocking"` | §6.7 |
| `warn` | `--root PATH`, `--as-of`, `--format`, `--out` | Prints delegation and temporary-person warnings | `0` always, unless `3` (input unavailable) or `1` (error) |
| `check-dismissals` | `--root PATH`, `--dismissals PATH`, `--as-of` | Runs `detect`, evaluates the dismissal file, prints accepted/rejected/unknown | `2` on any rejection |
| `events` | `--root PATH`, `--as-of`, `--out PATH` (required), `[--previous PATH]` | Writes `orphan detected` payloads, plus `orphan resolved` payloads when `--previous` names an earlier report JSON | §6.7 |

Rules:

- Exit-code precedence is exactly §6.7: `1` > `3` > `2` > `0`.
- Every subcommand prints the incompleteness banner when any input was unavailable, on **stderr** as well as in the report body, so a piped consumer cannot miss it.
- No subcommand accepts `--force`, `--apply`, `--fix`, `--repair`, `--yes` or any equivalent. A test asserts the parser rejects each of those six strings.
- `--out` writes the same bytes it would have printed; it is the only file the CLI creates.

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | Clean fixture exits 0 | `python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/orphans/_BASE --as-of 2026-08-27 >/dev/null 2>&1; echo $?` | `3` if DR inputs still unanswered, `0` once answered — assert the value your tree produces and record it in the PR body |
| 2 | Blocking orphan exits 2 | `python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/orphans/ORPH-PRIMARY-OWNER-ORPHAN --as-of 2026-08-27 --format json >/dev/null 2>&1; echo $?` | `2` |
| 3 | Rejected dismissal exits 2 | `python -m reconciler.orphans.cli check-dismissals --root reconciler/tests/fixtures/orphans/ORPH-PRIMARY-OWNER-ORPHAN --dismissals reconciler/tests/fixtures/dismissals/blocking.json --as-of 2026-08-27 >/dev/null 2>&1; echo $?` | `2` |
| 4 | No mutation flag is accepted | SELF-VERIFY | `FLAGS all-rejected` |
| 5 | JSON output parses | `python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/orphans/ORPH-POLICY-ORPHAN --as-of 2026-08-27 --format json \| python -c "import json,sys;d=json.load(sys.stdin);print(len(d['findings']))"` | `1` |
| 6 | CLI tests pass | `python -m pytest reconciler/tests/test_cli.py -q \| tail -1` | contains `passed`, not `failed` |
| 7 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/orphans/ORPH-PRIMARY-OWNER-ORPHAN --as-of 2026-08-27 --format json > /tmp/rep.json 2>/dev/null; echo "DETECT-EXIT $?"
python -c "import json;d=json.load(open('/tmp/rep.json'));print('FINDINGS',len(d['findings']),d['findings'][0]['orphan_type'],d['findings'][0]['severity'])"
python -m reconciler.orphans.cli check-dismissals --root reconciler/tests/fixtures/orphans/ORPH-PRIMARY-OWNER-ORPHAN --dismissals reconciler/tests/fixtures/dismissals/blocking.json --as-of 2026-08-27 > /tmp/dis.txt 2>&1; echo "DISMISS-EXIT $?"
grep -c "REJECTED" /tmp/dis.txt
bad=0; for f in --force --apply --fix --repair --yes --auto-repair; do python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/orphans/_BASE $f >/dev/null 2>&1 && bad=1; done; test $bad -eq 0 && echo "FLAGS all-rejected" || echo "FLAGS ACCEPTED-SOMETHING"
```

Expected output, exactly:

```
DETECT-EXIT 2
FINDINGS 1 ORPH-PRIMARY-OWNER Blocking
DISMISS-EXIT 2
1
FLAGS all-rejected
```

**STOP rule**
STOP if any of the six mutation flags is accepted by the parser, or if a report containing `Blocking` findings exits `0`. **The reconciler's CLI is the highest-privilege entry point in the system (Section 99.6 risk 6); an accidental `--apply` here is exactly the failure that risk names.** §6.6 template, symptom `CLI exposes a mutation flag or fails to block`.

---

### `L3-05-30` — Phase acceptance suite: AT-017 end to end

**Size:** L · **Depends on:** `L3-05-28`, `L3-05-29`
**Files created:** `reconciler/tests/acceptance/__init__.py`, `reconciler/tests/acceptance/test_at017_person_leaves.py`, fixtures `reconciler/tests/fixtures/acceptance/AT017-*/**`, `reconciler/PHASE5-EXIT.md`

**Spec being tested** — **AT-017** (line 9326): *"A person leaves | Exit lifecycle runs. Reconciliation revokes access; orphan detection surfaces every unowned responsibility; blocking orphans cannot be dismissed unresolved."* Supported by **EC-6** (line 9614), invariants **57** and **58** (lines 9528–9529), and the Section 12.2 flow diagram (lines 950–980).

**The fixture family**

| Fixture | State | Purpose |
| --- | --- | --- |
| `AT017-T0-BEFORE` | `lead-1` active; holds every one of the sixteen orphanable responsibilities across `product-1`, `svc-1`, the asset inventory, `policies.yaml`, `exceptions.yaml`, the board snapshot and the open-work snapshot | Baseline: zero findings |
| `AT017-T1-DEPARTING` | Same, but `lead-1` is `availability: departing`, `end_date: 2026-09-30` | Current mode: zero findings. Prospective mode: a transfer worklist naming every responsibility that would orphan on `2026-09-30` |
| `AT017-T2-DEPARTED` | Same, but `lead-1` is `availability: departed`, `access_status: revoked`, `as_of 2026-10-01` | Current mode: the full orphan set, with the exact severities of §2 |

**Required assertions**

1. `AT017-T0-BEFORE` yields zero findings in `current` mode and zero worklists.
2. `AT017-T1-DEPARTING` yields zero findings in `current` mode — the notice period is not an outage.
3. `AT017-T1-DEPARTING` yields exactly one transfer worklist, for `lead-1`, dated `2026-09-30`, and its finding set equals the finding set of `AT017-T2-DEPARTED` in `current` mode. **This equality is the acceptance test for line 985's "every responsibility that would orphan on that date".**
4. `AT017-T2-DEPARTED` yields findings covering every orphan type the fixture is built to trigger, and each finding's severity equals the §2 table value.
5. Every `Blocking` finding in `AT017-T2-DEPARTED` is rejected by `evaluate_dismissals` (invariant 57), and `dismissal_exit_code` is `2`.
6. `scan_expiries` on `AT017-T2-DEPARTED` plans `revoke_person_access` for `lead-1` if and only if `lead-1` has a non-null `end_date` reached — and the assignment removals for every dated assignment they held (invariant 58).
7. `orphan_detected_payloads` produces one payload per finding, each with `event_type == "orphan detected"`.
8. Re-running detection against a `AT017-T3-RESOLVED` fixture (`lead-1` still departed, every responsibility reassigned to `dev-b`) yields zero findings, and `orphan_resolved_payloads(T2_report, T3_report)` produces one `orphan resolved` payload per previously-open finding.

`reconciler/PHASE5-EXIT.md` records: the number of detectors (16), the severity tally (7/7/2), the AT and invariant ids proved (`AT-017`, `AT-008`, `AT-018`, `AT-036`, `AT-037`, invariants 57 and 58), the five DR ids and whether each was answered, and the full `pytest` summary line at the time of the exit commit.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands** — §6.3 block, slug `at017-acceptance`, then:

```bash
set -euo pipefail
mkdir -p reconciler/tests/acceptance
python -m pytest reconciler/tests/acceptance -q
python -m pytest reconciler/tests -q | tail -1
python -m reconciler.orphans.cli detect --root reconciler/tests/fixtures/acceptance/AT017-T2-DEPARTED --as-of 2026-10-01 --format text
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| 1 | All eight acceptance assertions pass | `python -m pytest reconciler/tests/acceptance -q \| tail -1` | contains `8 passed` |
| 2 | Departing is clean, departed is not | SELF-VERIFY | `T1-CURRENT 0` and `T2-CURRENT` > 0 |
| 3 | Worklist equals the post-departure finding set | SELF-VERIFY | `WORKLIST-EQUALS-T2 True` |
| 4 | Every Blocking finding is undismissable | SELF-VERIFY | `DISMISS rejected=<n> accepted=0` with `<n>` equal to the Blocking count |
| 5 | Resolution clears the report and emits `orphan resolved` | SELF-VERIFY | `T3 0` and `RESOLVED` equal to the T2 finding count |
| 6 | Whole suite green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed`, not `failed` |
| 7 | Exit record committed | `grep -c 'AT-017' reconciler/PHASE5-EXIT.md` | at least `1` |
| 8 | No foreign path | §6.4 block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
python - <<'EOF'
from pathlib import Path
from datetime import date
import reconciler.orphans.detectors as _
from reconciler.orphans.loader import load_control_plane
from reconciler.orphans.registry import run_all
from reconciler.orphans.report import build_report, blocking_open
from reconciler.orphans.prospective import all_transfer_worklists
from reconciler.orphans.dismissal import evaluate_dismissals, dismissal_exit_code
from reconciler.orphans.events import orphan_resolved_payloads
from reconciler.orphans.model import finding_key
B = Path('reconciler/tests/fixtures/acceptance')
def rep(case, d):
    ctx = load_control_plane(B/case, d, 'current')
    return build_report(run_all(ctx), d.isoformat(), 'current')
t1 = rep('AT017-T1-DEPARTING', date(2026,9,1))
t2 = rep('AT017-T2-DEPARTED',  date(2026,10,1))
t3 = rep('AT017-T3-RESOLVED',  date(2026,10,1))
print("T1-CURRENT", len(t1.findings))
print("T2-CURRENT", len(t2.findings))
wl = all_transfer_worklists(B/'AT017-T1-DEPARTING')
print("WORKLIST-EQUALS-T2", {finding_key(f) for f in wl[0].findings} == {finding_key(f) for f in t2.findings})
ds = [{"orphan_type":f.orphan_type,"subject":f.subject,"dismissed_by":"lead-2","dismissed_on":"2026-10-01","reason":"x"} for f in blocking_open(t2)]
o = evaluate_dismissals(t2, ds)
print(f"DISMISS rejected={len(o.rejected)} accepted={len(o.accepted)}")
print("EXIT", dismissal_exit_code(o))
print("T3", len(t3.findings))
print("RESOLVED", len(orphan_resolved_payloads(t2, t3)))
EOF
```

Expected output — `<B>` is the number of `Blocking` findings the fixture triggers and `<N>` the total; both are recorded in `PHASE5-EXIT.md` and must be identical across runs:

```
T1-CURRENT 0
T2-CURRENT <N>
WORKLIST-EQUALS-T2 True
DISMISS rejected=<B> accepted=0
EXIT 2
T3 0
RESOLVED <N>
```

**STOP rule**
STOP if `WORKLIST-EQUALS-T2` is `False` (prospective mode is not producing the transfer worklist line 985 requires), if `accepted` is greater than `0` (invariant 57 is broken), or if `T1-CURRENT` is greater than `0` (a notice period is being reported as a live outage). **Do not adjust the fixture to make the assertion pass — the assertion is the acceptance test.** §6.6 template, symptom `AT-017 end-to-end assertion fails`.

---

## 9. Phase exit criteria

The phase is complete when all of the following are simultaneously true on `integration`:

| # | Exit criterion | Proving command | Expected |
| 1 | Sixteen detectors registered, severities matching Section 12.2 | `python -m pytest reconciler/tests/orphans/test_registry_conformance.py -q \| tail -1` | contains `8 passed` |
| 2 | Every detector has an `-ORPHAN` and a `-CLEAN` golden fixture | `ls -d reconciler/tests/fixtures/orphans/ORPH-*-ORPHAN \| wc -l` and `... -CLEAN \| wc -l` | `16` and `16` |
| 3 | Prospective mode produces the transfer worklist | `python -m pytest reconciler/tests/orphans/test_prospective.py -q \| tail -1` | contains `4 passed` |
| 4 | Blocking orphans cannot be dismissed, by any path | `python -m pytest reconciler/tests/orphans/test_dismissal.py -q \| tail -1` | contains `6 passed` |
| 5 | Expiry produces a plan and never executes | `python -m pytest reconciler/tests/test_no_write_boundary.py reconciler/tests/expiry -q \| tail -1` | contains `passed`, not `failed` |
| 6 | 14-day and 7-day warnings fire on their exact boundaries | `python -m pytest reconciler/tests/expiry/test_delegation_warning.py reconciler/tests/expiry/test_temp_person_warning.py -q \| tail -1` | contains `passed`, not `failed` |
| 7 | AT-017 passes end to end | `python -m pytest reconciler/tests/acceptance -q \| tail -1` | contains `8 passed` |
| 8 | Whole suite green | `python -m pytest reconciler/tests -q \| tail -1` | contains `passed`, not `failed` |
| 9 | Phase touched no foreign path | `git diff --name-only <phase-start-sha>..integration \| grep -cv -E '^reconciler/'` | `0` |
| 10 | All five DECISION REQUIRED items are answered and recorded | `python -c "import reconciler.orphans.decisions as d;n=[k for k in dir(d) if k.isupper()];print(sum(getattr(d,k) is None for k in n))"` | `0` |
| 11 | Exit record present | `grep -c 'AT-017' reconciler/PHASE5-EXIT.md` | at least `1` |

**If criterion 10 is not met, the phase is not complete**, regardless of test results: four detectors (`ORPH-CERTIFICATE`, `ORPH-DOMAIN`, `ORPH-VENDOR`, `ORPH-ASSET`), `ORPH-COMMITMENT`, `ORPH-H1-WORK`, `ORPH-TEMP-EXPIRY-OPEN-WORK` and the 14-day delegation warning are all DR-gated, and a green suite with unanswered decisions means those detectors are returning `input_unavailable` rather than detecting anything. Report that state honestly to L0 — an incomplete phase reported as complete is the exact failure Section 97.2's write-freshness rule exists to prevent.
