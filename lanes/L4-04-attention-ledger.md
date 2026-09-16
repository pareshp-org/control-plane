# L4 — PHASE 4 — THE ATTENTION LEDGER AND DERIVED METRICS

**Lane:** L4 Records, Events & Metrics (subsystems I, N — Master Spec §99.2, lines 9184–9231)
**Phase:** 4 — the attention ledger, its duration rule, and the metrics derived from it
**Phase branch:** `lane/4/04-attention-ledger` (one branch for the phase, one commit per task, one PR at the end — the convention `lane/4/00-charter-preflight`, `lane/4/02-record-schemas` and `lane/4/03-write-paths` established)
**Task ID range:** `L4-T401` … `L4-T418` (18 tasks)
**Authority:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` is FROZEN and wins over this file. `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L4-00-charter.md` is the lane charter; its §3 owned-path list, §9 decisions and §12 standing rules bind every task here.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines). Every line number below was located with `grep`/`sed` and is cited, not inferred.

---

## 1. The one defect this phase closes

Master Spec §101.7, invariant 46, line 9514:

> **Derived data is computed, never hand-maintained. Metrics derive from the canonical record stores of Section 97 (Records, Events and Data Conventions), never from hand-maintained numbers.**

§97.1, line 8838, states the shipping test that follows from it:

> Metrics derive from these stores, never from hand-maintained numbers, and **every dashboard metric names the record store it derives from.**

And D102, line 10195, names the specific hole this phase fills:

> The derivation functions the measurement layer rests on are specified rather than assumed. **Attention-hour duration had named sources and no duration rule**, and §99.3 listed the matter closed … Each is defined once, with the calibrated-configuration convention and a stated initial value.

Phase 1 built the stores. Phase 2 built the shapes. Phase 3 built the doors. **Phase 4 builds the one instrument that reads through all three** — the attention ledger — and gives it the duration rule D102 says it never had: a named activity session, a named maximum inter-event gap, a named daily cap, a named precedence order, each a calibrated configuration key with a stated initial value.

Three further spec facts make this phase load-bearing:

| Fact | Spec anchor |
|---|---|
| The Human Attention Hour is the common currency of Part VIII — capacity, utilisation, Product Load Unit, forecasting and staffing diagnosis all denominate in it | §67.1, line 5575 |
| §99.2's dependency spine: *"I is the feedstock for nearly all governance-tier and people-tier computation"* | §99.2, line 9209 |
| §99.6 risk 2: *"Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance if the record stores are not built early"* | §99.6, lines 9276–9294 |

---

## 2. Fixed workspace convention (binding for every task in this file)

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
```

Re-export these at the start of **every** task. The Bash tool resets the working directory between calls; always use absolute paths.

**Runtime, fixed — do not substitute.** Every executable this phase ships runs under `python3` from `PATH`, importing only the standard library plus **PyYAML**. It does **not** use the `.l4-venv` of Phase 2, because `metrics/attention/test-derivation.sh` — already written by `L4-07-tests-and-runbook.md` task `L4-P7-T09` — invokes `python3 "$CP/metrics/attention/derive.py"` literally. A `derive.py` that needs a virtualenv fails that suite. No `jsonschema` import appears anywhere in this phase.

**Paths this phase writes — nothing else:**

| Repository | Path | Written by |
|---|---|---|
| `control-plane` | `metrics/attention/**` | L4-T402 … L4-T414 |
| `control-plane` | `tools/records/rqm-contract.yaml` | L4-T416 |
| `control-plane` | `tools/records/rqm-detect` | L4-T417 |

Nothing is written to `control-plane-records` in this phase. Nothing is written under `metrics/register/`, `metrics/signals/` or `metrics/taxonomy/`.

### 2.1 Files this phase MUST NOT write — already claimed by a sibling L4 document

A sibling document already owns each path below. Creating any of them here is a duplicate authorship that conflicts at merge, and is a STOP.

| Path | Owner document | Task |
|---|---|---|
| `metrics/attention/test-derivation.sh` | `L4-07-tests-and-runbook.md` | `L4-P7-T09` |
| `tools/records/fixtures/attention/input/**` | `L4-07-tests-and-runbook.md` | `L4-P7-T09` |
| `tools/records/fixtures/attention/expected/**` | `L4-07-tests-and-runbook.md` | `L4-P7-T09` |
| `tools/records/fixtures/rqm/**` | `L4-07-tests-and-runbook.md` | `L4-P7-T10` |
| `tools/records/test/suite-06-rqm.sh` | `L4-07-tests-and-runbook.md` | `L4-P7-T10` |
| `tools/records/test-rqm-detector.sh` | `L4-07-tests-and-runbook.md` | `L4-P7-T10` |
| `tools/records/rqm-emit`, `board-emit`, `lib/emit.sh` | `L4-03-write-paths.md` | `L4-T305`, `L4-T309` |
| `metrics/taxonomy/event-types.yaml` | `L4-02-record-schemas.md` | `L4-T203` |
| `metrics/register/**`, `metrics/signals/**` | the metric-register phase | — |

This phase's own self-check fixtures therefore live under **`metrics/attention/selfcheck/`**, a path no sibling claims (L4-T412).

### 2.2 Consumers of this phase's output — the contracts that bind it

Two artifacts written by `L4-07-tests-and-runbook.md` already fix the command-line and JSON contract of two executables this phase produces. **Those contracts are input to this phase, not output of it.** They may not be varied.

| Executable | Fixed by | Invocation, literal |
|---|---|---|
| `metrics/attention/derive.py` | `L4-P7-T09`, `L4-P7-T12` | `python3 derive.py --input <f.yaml> [--input …] [--query-product <p>] --json` |
| `tools/records/rqm-detect` | `L4-P7-T10` | `rqm-detect --input <f.yaml> --json` |

The exact output shapes are transcribed in §6 (L4-T411) and §7 (L4-T417) below.

---

## 3. THE ATTENTION LEDGER — normative tables

### 3.1 The eight categories — closed set (§67.2, lines 5579–5591)

§67.2 line 5579, binding: *"Every attention hour carries exactly one of eight categories. The attention ledger and the utilisation composition (Section 70) use this identical taxonomy; **no parallel category set exists anywhere in the operating system**."*

| # | Category | Covers (§67.2 verbatim, line) | Precedence rank |
|---|---|---|---|
| 1 | **Engineering** | Implementation, including directing AI agents (5583) | 4 |
| 2 | **Review** | Gate 2 review and cross-review (5584) | 3 |
| 3 | **Verification** | Verification-contract authoring, UAT, release verification (5585) | 2 |
| 4 | **Planning** | Gate 1, sequencing, Ready-queue preparation, reviewer-matrix upkeep (5586) | 6 |
| 5 | **Architecture** | Architecture-class work, design, decision records (5587) | 5 |
| 6 | **Incident** | Incident response, coordination, postmortem (5588) | 1 |
| 7 | **Operational** | Releases, deployments, environments, support duties, restore tests (5589) | 7 |
| 8 | **Coordination** | Status, handover, clarification, meetings, interrupts (5590) | 8 |

**Two flags, never a ninth category.**

| Flag | Rule | Spec anchor |
|---|---|---|
| `unplanned` | Work that entered H1 without preparation in H2. *"Unplanned is a flag on an entry, never a ninth category; an unplanned incident hour is still an Incident hour"* | §67.2, line 5592 |
| `ritual` | Set on any entry belonging to a ritual in the §57.2 inventory, *"set by the workflow or record that opens that ritual and **never self-reported**"* | §97.4, line 8956; §57.2, line 4960 |

**Founder coordination time is not a category.** §67.2 line 5594: *"It is the sum of Coordination-category hours attributed to the Founder."*

### 3.2 The per-category source map (§97.4 table, lines 8960–8967) — normative

The middle column is the §97.4 wording, verbatim. The right-hand columns are this phase's mechanical resolution of that wording onto artifacts that exist: L4 record stores (§97.2, lines 8845–8862) and tracked-event phrases from the §97.3 list (line 8951). This table is the human-readable face of `metrics/attention/sources.yaml`, built in L4-T403. Where the two differ, the YAML file is authoritative and the difference is a blocker for L0.

| Category | §97.4 "Derived from", verbatim | Record stores | §97.3 tracked-event phrases (line 8951) | Line |
|---|---|---|---|---|
| Engineering | Authored commits and PR activity windows on owned products, including agent-directing sessions | — | `execute started`; `PR opened with agent_authored flag`; `merge` | 8960 |
| Review | PR review sessions: review-requested to review-submitted activity windows, Gate 2 and cross-review | — | `review requested`; `Gate 2 approval with reviewer role` | 8961 |
| Verification | UAT record execution windows, verification-contract commits, CI failure triage sessions, release sign-off events | `records/uat/`; `records/launches/` | `UAT executed with result`; `CI pass or fail per check`; `parity check result`; `launch readiness signed off` | 8962 |
| Planning | Gate 1 activity, planning-board transitions, Ready-queue refill sessions, Horizon 3 board work | `records/estimates/` | `plan approved (Gate 1) with agent_authored flag`; `moved to Ready`; `Ready-queue miss recorded`; `re-plan triggered` | 8963 |
| Architecture | Architecture-class review activity, architecture decision records, cross-product design sessions | `records/decisions/` | `change class assigned`; `platform change proposed` | 8964 |
| Incident | Incident-record participation windows, from response to resolution, plus postmortem authoring | `records/incidents/`; `records/postmortems/` | `incident opened with severity`; `incident resolved`; `postmortem completed` | 8965 |
| Operational | Deployment approvals and executions, restore tests, asset and dependency sweeps, ops-VM maintenance | `records/deployments/`; `records/restore-tests/` | `production approval granted with approver`; `production deployed with digest`; `restore test executed with result`; `credential rotated` | 8966 |
| Coordination | Standups, handovers, demo records and client-facing sessions, status conversations, unplanned interrupts | `records/demos/` | `status request received (Coordination category)`; `plan submitted-to-approver notification sent` | 8967 |

**Binding rule, from §97.1 line 8838.** A category naming neither a record store nor a tracked-event phrase **does not ship**: it is absent from `sources.yaml`, not present-and-flagged. All eight name at least one. `validate-attention-config.sh` (L4-T405) proves it.

**Engineering and Review name no record store by design.** Their §97.4 wording is *commits* and *PR review sessions* — the git and pull-request surface, ingested by DevLake (§99.2 subsystem I, line 9196). Both name tracked-event phrases that `events/` carries, so both ship. The DevLake ingest itself is a separate dependency; see §5, routed item R1.

### 3.3 THE DURATION RULE — what D102 says was missing, defined once

§97.4 line 8969, binding, verbatim:

> A named interval — a review window, an incident window, a Gate 1 window — bounds the *search* for attention; **it is never itself the duration**. Within the interval, the person's attributed events cluster into **activity sessions**: consecutive events separated by no more than the **idle gap** belong to one session, and a wider gap ends it. A session's duration is the span from its first event to its last; a single-event session counts as one granularity unit. Elapsed wall-clock time between an interval's bounds is never an attention hour — a pull request left open overnight is one short session, not fourteen hours of Review.

Seven rules follow. Each is a numbered rule with a name, and every threshold in them is **calibrated configuration with a stated initial value** (D102, line 10195).

| # | Rule | Definition, binding | Spec line |
|---|---|---|---|
| **DR-1** | **Activity session** | The maximal run of a person's attributed events within one window in which every consecutive pair is separated by **no more than** the idle gap. Sessions do not span windows. | 8969 |
| **DR-2** | **Idle gap** — the named maximum inter-event gap, equivalently the idle timeout that ends a session | Calibrated configuration. **Initial value 30 minutes.** A gap *equal to* the idle gap continues the session; a gap *wider than* it ends the session and opens the next. | 8971 |
| **DR-3** | **Session duration** | First event to last event. A single-event session has span zero and is raised to one granularity unit by DR-4. Interval bounds are never a duration. | 8969 |
| **DR-4** | **Granularity** | Calibrated configuration. **Initial value 0.25 hours**, rounded to **nearest**, **never to zero**: `units = round_half_away(span_hours / 0.25)`, and `units < 1` is raised to `1`. | 8972 |
| **DR-5** | **Category precedence** | A session falling inside two windows resolves in this fixed order and **the losing categories receive nothing**: `Incident, Verification, Review, Engineering, Architecture, Planning, Operational, Coordination`. Two windows contain the same session when their event-timestamp signatures are identical. The losing category is recorded with `0.0` hours, not omitted. | 8973 |
| **DR-6** | **Product attribution** | One product touched → that product. Several → split by **event count**. None → `portfolio`. | 8974 |
| **DR-7** | **Daily reconciliation** | Derived hours for a person on a day never exceed that person's scheduled availability for that day (§69.2). Sessions truncate in **reverse precedence order** — `Coordination, Operational, Planning, Architecture, Engineering, Review, Verification, Incident` — until the reconciliation holds, and **each truncation is recorded**. | 8975 |

And the instrument-defect rule, §97.4 line 8976, which is not a duration rule but the failure mode of one:

> A day whose derived hours exceed scheduled availability **before** truncation is an **instrument defect**, not a workload finding. It raises a drift finding against the ledger and never enters a Capacity Profile, a workload state (Section 83) or the Founder view.

### 3.4 The calibrated-configuration register — every threshold, with its initial value

Built as `metrics/attention/calibration.yaml` in L4-T404. **No threshold in this phase is a literal in code**: every one is read from this file, and `validate-attention-config.sh` proves that no numeric literal for a threshold appears in any `metrics/attention/*.py` file.

| Key | Initial value | Kind | Authority |
|---|---|---|---|
| `idle_gap_minutes` | `30` | calibrated | §97.4 line 8971, verbatim |
| `granularity_hours` | `0.25` | calibrated | §97.4 line 8972, verbatim |
| `granularity_rounding` | `nearest` | fixed by spec | §97.4 line 8972, verbatim |
| `granularity_never_zero` | `true` | fixed by spec | §97.4 line 8972, verbatim |
| `precedence_order` | the eight of DR-5 | fixed by spec | §97.4 line 8973, verbatim |
| `daily_cap_source` | `capacity_profile.scheduled_availability` | fixed by spec | §97.4 line 8975; §69.2 line 5720 |
| `day_boundary_timezone` | `person.work_arrangement.timezone` | fixed by spec | §7.3 line 628; §97.1 line 8839 |
| `truncation_order` | `reverse_precedence` | fixed by spec | §97.4 line 8975 |
| `truncation_tiebreak` | `latest_session_first` | **declared by phase 4** | §97.4 line 8975 names the category order and is silent on the order within a category; the declaration is the authority, not an executor choice |
| `rounding_order` | `round_then_split` | **declared by phase 4** | Source: §84.6 (spec L7892). Rounding order: floor for quotients, round-half-up for final totals. Pinned by `L4-07-tests-and-runbook.md` **D-L4-P7-03** default; see §5 |
| `self_report_cadence` | `weekly` | fixed by spec | §97.4 line 8980; §67.3 line 5601 |
| `self_report_unit` | `band` | fixed by spec | §97.4 line 8980 |
| `self_report_per_product_attribution` | `false` | fixed by spec | §97.4 line 8980, *"unattributed to any product"* |
| `self_report_cap_minutes_per_person_per_week` | `5` | fixed by spec | §67.3 line 5603; §97.4 line 8980 |
| `self_report_bands` | seven bands, L4-T404 | **declared by phase 4** | §97.4 line 8980 requires bands and names none; the shape is §29.3's band-label-plus-representative-point convention (line 2665) |
| `calibration_phase` | `G3` | fixed by spec | §97.4 line 8978 |
| `calibration_min_parallel_reporters` | `2` | fixed by spec | §97.4 line 8978, *"at least two people band-report a single week in parallel"* |
| `threshold_review_months` | `12` | calibrated | §84.6 line 7478, *"reviewed every six or twelve months"* — the longer of the two stated values |

### 3.5 Scheduled availability — the daily cap's input, resolved

§97.4 line 8975 caps against *"that person's scheduled availability for that day in the Capacity Profile (Section 69.2)"*. §69.2 line 5720 gives that field exactly one source:

| Capacity Profile field | Source | Type |
|---|---|---|
| Scheduled availability for the period | `work_arrangement` in `people.yaml` — schedule, `fte`, timezone, public-holiday set (§7.3) | Declared |

So the chain is: **§97.4 line 8975 → §69.2 line 5720 → §7.3 (D111, line 10209)**. `work_arrangement` is a real block on the person record (§7 example, lines 568–580), and L1 has already frozen its schema (`L1-00-charter.md` line 281; `L1-05-tasks.md` task `L1-104`). L4 **reads** `registries/people.yaml`; it never writes it (charter §3.1).

**Resolved conflicts — do not re-open.**

| Apparent conflict | Resolution | Authority |
|---|---|---|
| §97.1 line 8839 says the working calendar is *"held in the leave records (Section 6.4)"*; §7.3 puts `work_arrangement` on the person record | Both hold, for different things. §7.3 line 627: *"Leave and schedule are different declarations and neither substitutes for the other."* The **schedule** is `work_arrangement`; the **absence** is the leave record; the **company calendar and public-holiday list per location** are the leave records (§6.4 line 451; §52.6 line 4641). | D111, line 10209 |
| §6.4 line 453 says *"A person record never stores calendar detail"* | D111 is the later governing decision and states the `work_arrangement` block exists precisely because *"no section defined it and no control-plane file held it"*. L1 has implemented it. | D111, line 10209; `L1-02-schemas.md` §`work_arrangement` |

**Resolution order for `scheduled-availability.py` (L4-T406), fixed:**

| # | Condition | Result |
|---|---|---|
| R1 | person absent from `people.yaml` | `SCHEDAVAIL ERROR person-not-in-registry`, exit 3 |
| R2 | person has no `work_arrangement` block | `SCHEDAVAIL ERROR no-work-arrangement`, exit 3 — fail closed, matching L1's `R07.4` |
| R3 | an approved leave record covers the date | `0.0` |
| R4 | the date is in the public-holiday list for the person's `public_holiday_set` | `0.0` |
| R5 | the date's weekday is absent from `work_arrangement.schedule` | `0.0` (§7.3 line 571: *"omit a day to declare it non-working"*) |
| R6 | otherwise | `(end − start)` in hours, in the person's declared IANA timezone, times the `fte_application` factor |
| R7 | any input unparseable or absent | `SCHEDAVAIL ERROR <reason>`, exit 3. **Never a default number.** |

---

## 4. Phase entry conditions

Task **L4-T401** proves every row. If any row fails, no other task in this phase starts.

| # | Condition | Why | Proof |
|---|---|---|---|
| E1 | `control-plane` is a git repository and `metrics/` exists | Charter L4-T004 | `test -d` |
| E2 | `$CP_ROOT/contracts/registry/event-types.v1.yaml` exists | §97.3 line 8959 — the ledger's event sources are typed | `test -f` |
| E3 | `$CP_ROOT/tools/records/rqm-emit` exists and is executable | Phase 3 L4-T309 — the detector emits through it | `test -x` |
| E4 | `python3` is on PATH and can `import yaml` | Every executable this phase ships | exit 0 |
| E5 | `$CP_ROOT/tools/records/lane-selfcheck.sh` exists and is executable | Charter L4-T005 | `test -x` |
| E6 | `$CP_ROOT/metrics/attention/test-derivation.sh` does **not** exist yet | §2.1 — it is `L4-P7-T09`'s file, written after this phase | `test ! -f` |

If E2 or E3 fail, the phase that owns them has not merged. **Do not create them here.** If E6 fails, a later phase has already merged and this phase is out of order. Open the blocker in L4-T401.

---

## 5. DECISION REQUIRED — hand to L0

Four items. **No L4 executor may answer them.** Each blocks only what it names; everything else in the phase proceeds. Charter decisions **D-L4-01**, **D-L4-02**, **D-L4-03**, Phase-3 decisions **D-L4-P3-01/02/03**, and `L4-07-tests-and-runbook.md` decisions **D-L4-P7-01/02/03** are closed — see `_DECISION_SIGNOFF.md`.

**Closed elsewhere:** **D-L4-P7-03** (round-then-split) — decided, see `_DECISION_SIGNOFF.md`. This phase's `calibration.yaml` carries `rounding_order: round_then_split` with `decided: D-L4-P7-03`. Fixtures that distinguish the two orders may now be added.

### DECISION REQUIRED D-L4-P4-01 — does `fte` multiply the declared schedule, or is it already in it?

- **Fact:** §7.3 line 629: *"`fte` is a capacity multiplier, not a status."* §7 line 577, on the same block: `fte: 1.0  # 0 < fte <= 1; part-time is configuration`. §7.3 line 571 declares the per-weekday `schedule` with explicit `start`/`end`. A part-time person can be expressed either way — a short `schedule` with `fte: 1.0`, or a full `schedule` with `fte: 0.5` — and applying both halves a half-day twice.
- **Question:** In computing scheduled availability for one day, is the declared `schedule` span multiplied by `fte`, or is `fte` an aggregate-period multiplier that the per-day figure must not apply?
- **Blocks:** rule **R6** of `scheduled-availability.py` (L4-T406) only. Every attention fixture supplies `scheduled_availability_hours` directly, so no derivation and no test is blocked.
- **L4 default until answered:** `calibration.yaml` declares `fte_application: none` with `decided: D-L4-P4-01`, and `scheduled-availability.py` reads the factor from that key. `none` means the declared `schedule` span is authoritative and `fte` is **not** applied a second time, grounded in line 577's *"part-time is configuration"*.
- **L4 must not:** hard-code either behaviour, write to `registries/people.yaml`, or infer a schedule from activity (§7.2 line 619: leave *"is never inferred from activity"*).

### DECISION REQUIRED D-L4-P4-02 — the Ready-queue-miss event is appended before three of its six fields exist

- **Fact:** §97.5 line 8984: the board automation *"appends a Ready-queue-miss event with who, which date, and which product, **and opens a one-line cause prompt** for the Team Lead"*. §97.5 line 8986: the event *"carries the full Section 29.4 field set … the last three supplied by the cause prompt, never inferred."* Phase 3's `tools/records/rqm-emit` (task `L4-T309`) **refuses a verdict document missing any of the eight keys**, `queue_empty_reason`, `team_lead_blocked` and `priority_changed_recently` included. An event cannot be appended at detection time and also carry fields that do not exist yet.
- **Question:** Does the event wait for the cause prompt to be answered, or is it appended immediately and completed by a follow-up record (§97.2 line 8890: *"corrections are follow-up records"*)? If the second, which store carries the follow-up?
- **Blocks:** the `--emit` path of `rqm-detect` (L4-T417) only. Classification, the `--json` verdict and the whole of `L4-P7-T10`'s suite are unaffected — that suite never calls `--emit`.
- **L4 default until answered:** `rqm-detect --emit` writes the `rqm-emit` verdict document **only** when `cause_prompt_answered` is true. When it is false it prints `RQM-DETECT PENDING-CAUSE <case>` on stdout, exits `0`, writes no verdict file and appends no event. It never fabricates a cause, a `team_lead_blocked` or a `priority_changed_recently`.
- **L4 must not:** modify `tools/records/rqm-emit` (Phase 3's file), relax its eight-key requirement, or infer any of the three cause fields.

### DECISION REQUIRED D-L4-P4-03 — which leave record carries the company working calendar

- **Fact:** §6.4 line 451 and §52.6 line 4641 both place the company working calendar — operating timezone, standard working days, core-hours window and *"the public-holiday list per location"* — in the leave records. There are now two calendars: (1) the company working calendar in the leave records, and (2) per-person `work_arrangement` schedule. `work_arrangement.public_holiday_set` is a reference to the company calendar, not a second independent list. `L4-02-record-schemas.md` gives `leave.schema.json` those fields plus a calendar **version** (`L4-06-tasks.md` row `L4-P2-22`). Neither the spec nor Phase 2 states **which** record in `records/leave/` is the current calendar, or how a reader selects it.
- **Question:** By what rule does a reader select the calendar-carrying leave record — a fixed filename, the highest calendar `version`, the latest effective date, or another rule L0 names?
- **Blocks:** rule **R4** of `scheduled-availability.py` (L4-T406) only, and only in production wiring. No fixture and no test is blocked.
- **L4 default until answered:** `scheduled-availability.py` takes the calendar document as a **required explicit argument** `--calendar <path>`. It never searches `records/leave/`, never picks a record by resemblance, and exits `3` with `SCHEDAVAIL ERROR no-calendar` when the argument is absent.
- **L4 must not:** invent a filename convention under `records/leave/`, or fall back to a hard-coded holiday list.

### DECISION REQUIRED D-L4-P4-04 — the Capacity Profile has no lane

- **Fact:** §97.4 line 8975 caps derived hours against *"that person's scheduled availability for that day **in the Capacity Profile** (Section 69.2)"*, and line 8976 says an instrument-defect day *"never enters a Capacity Profile, a workload state (Section 83) or the Founder view"*. The Capacity Profile, workload states and the whole people-intelligence surface are §99.2 subsystem **P** (line 9203), which **PARTITION.md v1 assigns to no lane** — the known partition gap already escalated by other authors, alongside G, H, J and O. L4 does not claim it.
- **Question:** Which lane owns subsystem P, and therefore owns the consumer that must honour `capacity_profile_eligible`, `workload_state_eligible` and `founder_view_eligible`?
- **Blocks:** nothing in this phase. This phase **emits** the three eligibility flags and the recorded truncations; it builds no Capacity Profile, no workload state and no Founder view.
- **L4 default until answered:** `derive.py` emits `capacity_profile_eligible`, `workload_state_eligible` and `founder_view_eligible` as declared output fields, and `metrics/attention/HANDOFF-P.md` (L4-T413) names them for whoever receives subsystem P. **L4 writes no file under any path subsystem P would own.**
- **L4 must not:** claim subsystem P, build a Capacity Profile, or render a Founder view.

**Routed dependencies — stated, not claimed.**

| # | Item | Needed for | Owner |
|---|---|---|---|
| R1 | DevLake ingest of commit and PR activity (§99.2 subsystem I, line 9196; run on the operations VM, subsystem M, line 9200) | The Engineering and Review windows of §3.2 in production. Not needed for any fixture. | Ops VM is L5 (`ops-vm/**`, PARTITION.md line 21). The ingest contract is an L0 routing question. |
| R2 | The `event_type` identifier for each tracked-event phrase in §3.2 | `sources.yaml` validation | `metrics/taxonomy/event-types.yaml`, Phase 2 task `L4-T203`. This phase **looks identifiers up**; it never declares one (charter §12 rule 3). |
| R3 | Drift finding for an instrument-defect day (§97.4 line 8976) | The defect must reach an operator | `validators/drift/**` is L3 (PARTITION.md line 19). L4 emits the flag; L3 raises the finding. |

---

## 6. Tasks

Eighteen tasks, **L4-T401** through **L4-T418**. Each is mechanical. None requires designing, choosing or interpreting.

---

### L4-T401 — Phase-4 preflight and phase branch

**Size:** S
**Depends on:** none (phase entry)

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" checkout -B lane/4/04-attention-ledger origin/integration
git -C "$CP_ROOT" status --porcelain
test -d "$CP_ROOT/metrics" && echo "E1=yes" || echo "E1=no"
test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo "E2=yes" || echo "E2=no"
test -x "$CP_ROOT/tools/records/rqm-emit" && echo "E3=yes" || echo "E3=no"
python3 -c "import yaml" 2>/dev/null && echo "E4=yes" || echo "E4=no"
test -x "$CP_ROOT/tools/records/lane-selfcheck.sh" && echo "E5=yes" || echo "E5=no"
test ! -f "$CP_ROOT/metrics/attention/test-derivation.sh" && echo "E6=yes" || echo "E6=no"
mkdir -p "$CP_ROOT/metrics/attention/lib" "$CP_ROOT/metrics/attention/selfcheck/input" \
         "$CP_ROOT/metrics/attention/selfcheck/expected"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Phase branch created off `origin/integration` | `git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD` | `lane/4/04-attention-ledger` |
| 2 | Working tree clean before any write | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 3 | Event taxonomy present (E2) | `test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo YES` | `YES` |
| 4 | Phase-3 emitter present (E3) | `test -x "$CP_ROOT/tools/records/rqm-emit" && echo YES` | `YES` |
| 5 | `python3` + PyYAML usable (E4) | `python3 -c "import yaml"; echo $?` | `0` |
| 6 | The tests phase has not merged ahead of this one (E6) | `test ! -f "$CP_ROOT/metrics/attention/test-derivation.sh" && echo YES` | `YES` |
| 7 | Three working directories created | `ls -d "$CP_ROOT"/metrics/attention/lib "$CP_ROOT"/metrics/attention/selfcheck/input "$CP_ROOT"/metrics/attention/selfcheck/expected \| wc -l` | `3` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
echo "BRANCH=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l | tr -d ' ')"
echo "TAXONOMY=$(test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo yes || echo no)"
echo "RQMEMIT=$(test -x "$CP_ROOT/tools/records/rqm-emit" && echo yes || echo no)"
echo "PYYAML=$(python3 -c 'import yaml' 2>/dev/null && echo yes || echo no)"
echo "TESTPHASE=$(test ! -f "$CP_ROOT/metrics/attention/test-derivation.sh" && echo absent || echo present)"
echo "DIRS=$(ls -d "$CP_ROOT"/metrics/attention/lib "$CP_ROOT"/metrics/attention/selfcheck/input "$CP_ROOT"/metrics/attention/selfcheck/expected 2>/dev/null | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
BRANCH=lane/4/04-attention-ledger
DIRTY=0
TAXONOMY=yes
RQMEMIT=yes
PYYAML=yes
TESTPHASE=absent
DIRS=3
```

**STOP rule** — if any value differs from the expected block above: **do not create the missing artifact yourself.** `TAXONOMY=no` or `RQMEMIT=no` means an earlier L4 phase has not merged to `integration`; creating them here duplicates another phase's authorship and will conflict at merge. `TESTPHASE=present` means `L4-07-tests-and-runbook.md` merged before this phase and the merge train ran out of order — stop, because this phase would then be writing against a suite it was supposed to precede. `PYYAML=no` is a runner-image matter for L0. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T401 Phase 4 entry condition failed"
lane: L4
phase: 4
task_id: L4-T401
blocked_by: "<taxonomy absent | rqm-emit absent | pyyaml absent | tests phase merged first | tree dirty>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "BRANCH=lane/4/04-attention-ledger / DIRTY=0 / TAXONOMY=yes / RQMEMIT=yes / PYYAML=yes / TESTPHASE=absent / DIRS=3"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8954-8981; Section 97.5 lines 8982-8987; L4-00-charter.md section 7 DoD-6, DoD-7, DoD-8; L4-03-write-paths.md task L4-T309"
needs: "L0"
action_taken: "nothing created, nothing pushed"
```

---

### L4-T402 — The eight-category taxonomy artifact

**Size:** M
**Depends on:** L4-T401

Transcribe §3.1 of this file into `metrics/attention/taxonomy.yaml`. Copy the block below **verbatim**. Do not add a category, do not omit one, do not reorder `precedence`, do not change a `spec_line`.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/taxonomy.yaml" <<'TAX_EOF'
# metrics/attention/taxonomy.yaml
# The single eight-category attention taxonomy. Master Spec v4.0 Section 67.2, lines 5577-5594.
# Section 67.2 line 5579, binding: "Every attention hour carries exactly one of eight categories.
# The attention ledger and the utilisation composition (Section 70) use this identical taxonomy;
# no parallel category set exists anywhere in the operating system."
# Section 67.1 line 5573: one hour, attributed to a product or to the portfolio, in exactly one category.
taxonomy_version: 1
category_count: 8
categories:
  - name: Engineering
    covers: "Implementation, including directing AI agents"
    precedence: 4
    spec_line: 5583
  - name: Review
    covers: "Gate 2 review and cross-review"
    precedence: 3
    spec_line: 5584
  - name: Verification
    covers: "Verification-contract authoring, UAT, release verification"
    precedence: 2
    spec_line: 5585
  - name: Planning
    covers: "Gate 1, sequencing, Ready-queue preparation, reviewer-matrix upkeep"
    precedence: 6
    spec_line: 5586
  - name: Architecture
    covers: "Architecture-class work, design, decision records"
    precedence: 5
    spec_line: 5587
  - name: Incident
    covers: "Incident response, coordination, postmortem"
    precedence: 1
    spec_line: 5588
  - name: Operational
    covers: "Releases, deployments, environments, support duties, restore tests"
    precedence: 7
    spec_line: 5589
  - name: Coordination
    covers: "Status, handover, clarification, meetings, interrupts"
    precedence: 8
    spec_line: 5590
# Section 67.2 line 5592 and Section 97.4 line 8956: flags on an entry, never a ninth category.
flags:
  - name: unplanned
    rule: "Work that entered the committed horizon H1 without preparation in H2. An unplanned incident hour is still an Incident hour."
    self_reportable: true
    spec_line: 5592
  - name: ritual
    rule: "The entry belongs to a ritual in the Section 57.2 inventory. Set by the workflow or record that opens that ritual."
    self_reportable: false
    spec_line: 8956
# Section 67.2 line 5594: not a category.
derived_aggregates:
  - name: founder_coordination_time
    definition: "The sum of Coordination-category hours attributed to the Founder."
    is_category: false
    spec_line: 5594
# Section 91.2 lines 8083-8092 and Section 67.3 line 5605: what this taxonomy is never used for.
prohibited_uses:
  - "individual performance evidence"
  - "per-person drill-downs on general dashboards"
  - "hours online or hours at desk as a performance measure"
  - "IDE active time as a performance measure"
  - "AI token usage as a performance measure"
prohibited_uses_spec_lines: [5605, 8087, 8088, 8089]
TAX_EOF
git -C "$CP_ROOT" add metrics/attention/taxonomy.yaml
git -C "$CP_ROOT" commit -m "L4-T402: the eight-category attention taxonomy (Section 67.2)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file parses as YAML | `python3 -c "import yaml;yaml.safe_load(open(r'$CP_ROOT/metrics/attention/taxonomy.yaml'))"; echo $?` | `0` |
| 2 | Exactly eight categories | `python3 -c "import yaml;print(len(yaml.safe_load(open(r'$CP_ROOT/metrics/attention/taxonomy.yaml'))['categories']))"` | `8` |
| 3 | The eight precedence ranks are `1..8` with no repeat | see SELF-VERIFY `RANKS` | `12345678` |
| 4 | Exactly two flags, and `ritual` is not self-reportable | see SELF-VERIFY `RITUAL` | `flags=2 ritual_self_reportable=False` |
| 5 | Category names match §67.2 exactly | see SELF-VERIFY `NAMES` | `Architecture,Coordination,Engineering,Incident,Operational,Planning,Review,Verification` |
| 6 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - "$CP_ROOT/metrics/attention/taxonomy.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
c = d["categories"]
print("COUNT=%d" % len(c))
print("RANKS=%s" % "".join(str(x) for x in sorted(r["precedence"] for r in c)))
print("NAMES=%s" % ",".join(sorted(r["name"] for r in c)))
f = d["flags"]
rit = [x for x in f if x["name"] == "ritual"][0]
print("RITUAL=flags=%d ritual_self_reportable=%s" % (len(f), rit["self_reportable"]))
PY
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
COUNT=8
RANKS=12345678
NAMES=Architecture,Coordination,Engineering,Incident,Operational,Planning,Review,Verification
RITUAL=flags=2 ritual_self_reportable=False
FOREIGN=0
```

**STOP rule** — if `COUNT` is not `8`, or `RANKS` is not `12345678`, or a name differs from the eight of §67.2: you have edited the transcription. Restore the block verbatim. A ninth category, or a flag promoted to a category, contradicts §67.2 line 5579 (*"no parallel category set exists anywhere in the operating system"*) and §67.1 line 5573 (*"exactly one category"*). Do not add a category to make a later task pass. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T402 attention taxonomy does not match Section 67.2"
lane: L4
phase: 4
task_id: L4-T402
blocked_by: "<category count wrong | precedence rank duplicated | category name differs | flag promoted to category>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "COUNT=8 / RANKS=12345678 / NAMES=Architecture,Coordination,Engineering,Incident,Operational,Planning,Review,Verification / RITUAL=flags=2 ritual_self_reportable=False"
spec_ref: "Master Spec v4.0 Section 67.2 lines 5577-5594; Section 67.1 line 5573; Section 97.4 lines 8956, 8973"
needs: "L0"
action_taken: "nothing beyond metrics/attention/taxonomy.yaml"
```

---

### L4-T403 — The per-category source map

**Size:** M
**Depends on:** L4-T402

Transcribe §3.2 of this file into `metrics/attention/sources.yaml`. The `derived_from` string of every row is the §97.4 table cell **verbatim**. Copy the block below exactly.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/sources.yaml" <<'SRC_EOF'
# metrics/attention/sources.yaml
# Per-category derivation sources. Master Spec v4.0 Section 97.4 table, lines 8958-8967.
# Section 97.1 line 8838, binding: "every dashboard metric names the record store it derives from".
# A category naming neither a record store nor a tracked-event phrase DOES NOT SHIP:
# it is absent from this file, not present-and-flagged.
# derived_from is the Section 97.4 cell verbatim. record_stores are Section 97.2 store paths
# (lines 8845-8862). event_phrases are quoted from the Section 97.3 tracked-events list (line 8951);
# the event_type identifier for each is looked up in metrics/taxonomy/event-types.yaml and is
# NEVER declared here (L4-00-charter.md section 12 rule 3).
sources_version: 1
event_type_register: metrics/taxonomy/event-types.yaml
categories:
  - category: Engineering
    derived_from: "Authored commits and PR activity windows on owned products, including agent-directing sessions"
    record_stores: []
    event_phrases:
      - "execute started"
      - "PR opened with agent_authored flag"
      - "merge"
    external_ingest: devlake
    spec_line: 8960
  - category: Review
    derived_from: "PR review sessions: review-requested to review-submitted activity windows, Gate 2 and cross-review"
    record_stores: []
    event_phrases:
      - "review requested"
      - "Gate 2 approval with reviewer role"
    external_ingest: devlake
    spec_line: 8961
  - category: Verification
    derived_from: "UAT record execution windows, verification-contract commits, CI failure triage sessions, release sign-off events"
    record_stores: ["records/uat/", "records/launches/"]
    event_phrases:
      - "UAT executed with result"
      - "CI pass or fail per check"
      - "parity check result"
      - "launch readiness signed off"
    external_ingest: null
    spec_line: 8962
  - category: Planning
    derived_from: "Gate 1 activity, planning-board transitions, Ready-queue refill sessions, Horizon 3 board work"
    record_stores: ["records/estimates/"]
    event_phrases:
      - "plan approved (Gate 1) with agent_authored flag"
      - "moved to Ready"
      - "Ready-queue miss recorded"
      - "re-plan triggered"
    external_ingest: null
    spec_line: 8963
  - category: Architecture
    derived_from: "Architecture-class review activity, architecture decision records, cross-product design sessions"
    record_stores: ["records/decisions/"]
    event_phrases:
      - "change class assigned"
      - "platform change proposed"
    external_ingest: null
    spec_line: 8964
  - category: Incident
    derived_from: "Incident-record participation windows, from response to resolution, plus postmortem authoring"
    record_stores: ["records/incidents/", "records/postmortems/"]
    event_phrases:
      - "incident opened with severity"
      - "incident resolved"
      - "postmortem completed"
    external_ingest: null
    spec_line: 8965
  - category: Operational
    derived_from: "Deployment approvals and executions, restore tests, asset and dependency sweeps, ops-VM maintenance"
    record_stores: ["records/deployments/", "records/restore-tests/"]
    event_phrases:
      - "production approval granted with approver"
      - "production deployed with digest"
      - "restore test executed with result"
      - "credential rotated"
    external_ingest: null
    spec_line: 8966
  - category: Coordination
    derived_from: "Standups, handovers, demo records and client-facing sessions, status conversations, unplanned interrupts"
    record_stores: ["records/demos/"]
    event_phrases:
      - "status request received (Coordination category)"
      - "plan submitted-to-approver notification sent"
    external_ingest: null
    spec_line: 8967
# Section 99.2 line 9196 places DevLake ingest inside subsystem I; the operations VM that runs it is
# subsystem M and PARTITION.md line 21 gives ops-vm/** to L5. L4 declares the dependency and builds
# no ingest. See L4-04-attention-ledger.md section 5, routed item R1.
external_ingest_dependencies:
  devlake:
    supplies: "commit and pull-request activity windows for the Engineering and Review categories"
    owner_note: "Subsystem I ingest running on the operations VM (Section 99.2 lines 9196, 9200). ops-vm/** is L5 (PARTITION.md line 21). Routed to L0."
    blocks: "production Engineering and Review windows only; no fixture and no test depends on it"
SRC_EOF
git -C "$CP_ROOT" add metrics/attention/sources.yaml
git -C "$CP_ROOT" commit -m "L4-T403: per-category attention source map (Section 97.4 lines 8958-8967)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file parses as YAML | `python3 -c "import yaml;yaml.safe_load(open(r'$CP_ROOT/metrics/attention/sources.yaml'))"; echo $?` | `0` |
| 2 | Exactly eight source rows | see SELF-VERIFY `COUNT` | `8` |
| 3 | Its category set equals the taxonomy's category set | see SELF-VERIFY `MATCH` | `SAME` |
| 4 | Every category names a store or an event phrase | see SELF-VERIFY `SOURCELESS` | `0` |
| 5 | No `event_type` identifier is declared in this file | `grep -c "event_type:" "$CP_ROOT/metrics/attention/sources.yaml"` | `0` |
| 6 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - "$CP_ROOT/metrics/attention/sources.yaml" "$CP_ROOT/metrics/attention/taxonomy.yaml" <<'PY'
import sys, yaml
s = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
t = yaml.safe_load(open(sys.argv[2], encoding="utf-8"))
rows = s["categories"]
print("COUNT=%d" % len(rows))
a = sorted(r["category"] for r in rows)
b = sorted(r["name"] for r in t["categories"])
print("MATCH=%s" % ("SAME" if a == b else "DIFFERENT"))
print("SOURCELESS=%d" % sum(1 for r in rows if not r["record_stores"] and not r["event_phrases"]))
PY
echo "NOIDENT=$(grep -c 'event_type:' "$CP_ROOT/metrics/attention/sources.yaml")"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
COUNT=8
MATCH=SAME
SOURCELESS=0
NOIDENT=0
FOREIGN=0
```

**STOP rule** — if `SOURCELESS` is not `0`, a category has been left with no derivation source and §97.1 line 8838 forbids shipping it. **Do not invent a source to clear the count** and do not delete the category — the taxonomy is closed at eight (§67.2 line 5579), so a sourceless category is a spec question, not an edit. If `NOIDENT` is not `0`, an `event_type` identifier has been declared here; identifiers are governed additions to `metrics/taxonomy/event-types.yaml` (§97.3 line 8947) and Phase 2 owns that file. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T403 attention source map incomplete or declares an identifier"
lane: L4
phase: 4
task_id: L4-T403
blocked_by: "<category with no store and no event phrase | category set differs from taxonomy | event_type identifier declared here>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "COUNT=8 / MATCH=SAME / SOURCELESS=0 / NOIDENT=0 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8958-8967; Section 97.1 line 8838; Section 97.3 line 8947; Section 67.2 line 5579"
needs: "L0"
action_taken: "nothing beyond metrics/attention/sources.yaml"
```

---

### L4-T404 — The calibrated-configuration register

**Size:** M
**Depends on:** L4-T401

Every threshold this phase uses, each with a stated initial value, as D102 (line 10195) requires. **No later task may write a threshold as a literal in code.**

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/calibration.yaml" <<'CAL_EOF'
# metrics/attention/calibration.yaml
# Every threshold the attention ledger uses, with a stated initial value.
# D102 (line 10195): "Each is defined once, with the calibrated-configuration convention and a
# stated initial value." Section 84.6 line 7478: "Thresholds are reviewed every six or twelve
# months and refitted against observed data. No first threshold is assumed correct."
# kind: calibrated  = a hypothesis carrying an initial value, refitted at the review cadence
# kind: spec-fixed  = quoted from the spec; changing it is a spec change, not a calibration
# kind: phase4-declared = the spec is silent; this file is the authority, not an executor choice
calibration_version: 1
review_months: 12
review_spec_line: 7478

idle_gap_minutes:
  value: 30
  kind: calibrated
  spec_line: 8971
  quote: "The idle gap is calibrated configuration with an initial value of 30 minutes."
  rule: "A gap equal to the idle gap continues the session; a gap wider than it ends the session."

granularity_hours:
  value: 0.25
  kind: calibrated
  spec_line: 8972
  quote: "Attribution granularity is calibrated configuration with an initial value of 0.25 hours, rounded to nearest, never to zero."

granularity_rounding:
  value: nearest
  kind: spec-fixed
  spec_line: 8972
  tie_rule: away_from_zero

granularity_never_zero:
  value: true
  kind: spec-fixed
  spec_line: 8972
  rule: "A computed unit count below 1 is raised to 1. A single-event session counts as one granularity unit (line 8969)."

precedence_order:
  value: [Incident, Verification, Review, Engineering, Architecture, Planning, Operational, Coordination]
  kind: spec-fixed
  spec_line: 8973
  quote: "a session falling inside two windows resolves in this fixed order and the losing categories receive nothing"
  loser_rule: "The losing category is recorded with 0.0 hours for the same products, never omitted."
  identity_rule: "Two windows contain the same session when their event-timestamp signatures are identical."

truncation_order:
  value: reverse_precedence
  kind: spec-fixed
  spec_line: 8975
  expanded: [Coordination, Operational, Planning, Architecture, Engineering, Review, Verification, Incident]

truncation_tiebreak:
  value: latest_session_first
  kind: phase4-declared
  spec_line: 8975
  note: "Section 97.4 line 8975 fixes the category order and is silent on the order within one category. This declaration is the authority; it is not an executor choice."

rounding_order:
  value: round_then_split
  kind: phase4-declared
  decided: D-L4-P7-03
  spec_lines: [8972, 8974]
  note: "Decided: round-then-split. See _DECISION_SIGNOFF.md and L4-07-tests-and-runbook.md D-L4-P7-03."

daily_cap_source:
  value: capacity_profile.scheduled_availability
  kind: spec-fixed
  spec_lines: [8975, 5720]
  resolution_chain: "Section 97.4 line 8975 -> Section 69.2 line 5720 -> Section 7.3 work_arrangement (D111, line 10209)"

day_boundary_timezone:
  value: person.work_arrangement.timezone
  kind: spec-fixed
  spec_lines: [628, 8839]
  quote: "Every time-bounded obligation resolves against the person's timezone where it concerns a person"
  rule: "IANA identifier, never a UTC offset (Section 7.3 line 628). Never the runner's local time (Section 97.1 line 8839)."

fte_application:
  value: none
  kind: phase4-declared
  decided: D-L4-P4-01
  spec_lines: [577, 629]
  note: "none means the declared work_arrangement.schedule span is authoritative and fte is not applied a second time, per Section 7 line 577 'part-time is configuration'. Blocks rule R6 of scheduled-availability.py only."

self_report_cadence:
  value: weekly
  kind: spec-fixed
  spec_lines: [5601, 8980]

self_report_unit:
  value: band
  kind: spec-fixed
  spec_line: 8980
  quote: "bands, not minutes; weekly, not daily; one band per category, unattributed to any product"

self_report_per_product_attribution:
  value: false
  kind: spec-fixed
  spec_line: 8980
  rule: "Per-product attribution is never asked of the person. The week's band is apportioned by machine-derived activity share."

self_report_cap_minutes_per_person_per_week:
  value: 5
  kind: spec-fixed
  spec_lines: [5603, 8980]
  quote: "The five-minute cap is binding"
  breach_rule: "A collection design costing more than this fails the check. It is a collection design to be simplified, not a person to be chased."

self_report_bands:
  kind: phase4-declared
  spec_line: 8980
  shape_source: "Section 29.3 line 2665 - band label plus the representative point value in force when written"
  note: "Section 97.4 line 8980 requires bands and names none. These are initial values, refitted at the G3 calibration. The shape is borrowed from Section 29.3; the values are not."
  value:
    - {label: none,     representative_hours: 0.0}
    - {label: under-1h, representative_hours: 0.5}
    - {label: 1-2h,     representative_hours: 1.5}
    - {label: 2-4h,     representative_hours: 3.0}
    - {label: 4-8h,     representative_hours: 6.0}
    - {label: 8-16h,    representative_hours: 12.0}
    - {label: over-16h, representative_hours: 20.0}

calibration_phase:
  value: G3
  kind: spec-fixed
  spec_line: 8978

calibration_min_parallel_reporters:
  value: 2
  kind: spec-fixed
  spec_line: 8978
  quote: "at least two people band-report a single week in parallel with the derivation, and the divergence is recorded as the metric's stated error bar"
CAL_EOF
git -C "$CP_ROOT" add metrics/attention/calibration.yaml
git -C "$CP_ROOT" commit -m "L4-T404: calibrated configuration register with stated initial values (D102)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file parses as YAML | `python3 -c "import yaml;yaml.safe_load(open(r'$CP_ROOT/metrics/attention/calibration.yaml'))"; echo $?` | `0` |
| 2 | The two spec-quoted initial values are exact | see SELF-VERIFY `INITIAL` | `idle=30 gran=0.25` |
| 3 | The precedence order is the §97.4 line 8973 order | see SELF-VERIFY `PREC` | `Incident,Verification,Review,Engineering,Architecture,Planning,Operational,Coordination` |
| 4 | The truncation order is the exact reverse | see SELF-VERIFY `TRUNC` | `EXACT-REVERSE` |
| 5 | Every key carries a `kind` and a spec line | see SELF-VERIFY `UNSOURCED` | `0` |
| 6 | The five-minute cap is present and equals `5` | see SELF-VERIFY `CAP` | `5` |
| 7 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - "$CP_ROOT/metrics/attention/calibration.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print("INITIAL=idle=%s gran=%s" % (d["idle_gap_minutes"]["value"], d["granularity_hours"]["value"]))
p = d["precedence_order"]["value"]
print("PREC=%s" % ",".join(p))
print("TRUNC=%s" % ("EXACT-REVERSE" if d["truncation_order"]["expanded"] == list(reversed(p)) else "NOT-REVERSE"))
bad = 0
for k, v in d.items():
    if not isinstance(v, dict):
        continue
    if "kind" not in v:
        bad += 1
    if "spec_line" not in v and "spec_lines" not in v:
        bad += 1
print("UNSOURCED=%d" % bad)
print("CAP=%s" % d["self_report_cap_minutes_per_person_per_week"]["value"])
PY
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
INITIAL=idle=30 gran=0.25
PREC=Incident,Verification,Review,Engineering,Architecture,Planning,Operational,Coordination
TRUNC=EXACT-REVERSE
UNSOURCED=0
CAP=5
FOREIGN=0
```

**STOP rule** — if `INITIAL` is not `idle=30 gran=0.25`, the two values §97.4 lines 8971–8972 state verbatim have been changed; restore them. If `PREC` differs by one position, DR-5 no longer matches line 8973 and every derivation result becomes wrong in a way no later test can localise. **Never retune a threshold to make a later task pass** — a threshold refit is a §84.6 line 7478 calibration review, evidenced and dated, never an edit during a build. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T404 calibrated configuration does not match the spec's stated values"
lane: L4
phase: 4
task_id: L4-T404
blocked_by: "<idle gap changed | granularity changed | precedence order changed | truncation order not the reverse | key without kind or spec line>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "INITIAL=idle=30 gran=0.25 / PREC=Incident,Verification,Review,Engineering,Architecture,Planning,Operational,Coordination / TRUNC=EXACT-REVERSE / UNSOURCED=0 / CAP=5"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8971-8975; Section 84.6 lines 7473-7478; D102 line 10195"
needs: "L0"
action_taken: "nothing beyond metrics/attention/calibration.yaml"
```

---

### L4-T405 — Config validator, with its negative test

**Size:** M
**Depends on:** L4-T402, L4-T403, L4-T404

Charter §12 rule 10: *"A check that cannot fail is not a check."* This validator ships with a seeded canary that proves it rejects.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/validate-attention-config.sh" <<'VAC_EOF'
#!/usr/bin/env bash
# metrics/attention/validate-attention-config.sh
# Proves taxonomy.yaml, sources.yaml and calibration.yaml agree with each other and with the spec.
# Output contract: one final line. ATTNCFG OK <counters> exit 0 / ATTNCFG FAIL <counters> exit 1 /
# ATTNCFG ERROR <reason> exit 3 (could not execute - never a pass).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
for f in taxonomy.yaml sources.yaml calibration.yaml; do
  [ -f "$HERE/$f" ] || { echo "ATTNCFG ERROR missing-$f"; exit 3; }
done
if [ "${1:-}" = "--selftest" ]; then
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  cp "$HERE/taxonomy.yaml" "$HERE/sources.yaml" "$HERE/calibration.yaml" "$T/"
  cp "$HERE/validate-attention-config.sh" "$T/"
  python3 - "$T/taxonomy.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
d["categories"].append({"name": "Meetings", "covers": "seeded canary", "precedence": 9, "spec_line": 0})
yaml.safe_dump(d, open(sys.argv[1], "w", encoding="utf-8"), sort_keys=False)
PY
  if sh "$T/validate-attention-config.sh" >/dev/null 2>&1; then
    echo "ATTNCFG FAIL selftest-canary-accepted"; exit 1
  fi
  echo "ATTNCFG OK selftest 1/1"; exit 0
fi
python3 - "$HERE" <<'PY' || exit $?
import os, sys, yaml
h = sys.argv[1]
tax = yaml.safe_load(open(os.path.join(h, "taxonomy.yaml"), encoding="utf-8"))
src = yaml.safe_load(open(os.path.join(h, "sources.yaml"), encoding="utf-8"))
cal = yaml.safe_load(open(os.path.join(h, "calibration.yaml"), encoding="utf-8"))
fails = []
cats = tax["categories"]
# C1 Section 67.2 line 5579 - exactly eight, exactly one rank each.
if len(cats) != 8:
    fails.append("category-count:%d" % len(cats))
if sorted(c["precedence"] for c in cats) != list(range(1, 9)):
    fails.append("precedence-not-1-8")
# C2 Section 97.4 line 8973 - the precedence order is the calibration order.
by_rank = [c["name"] for c in sorted(cats, key=lambda c: c["precedence"])]
if by_rank != cal["precedence_order"]["value"]:
    fails.append("precedence-order-mismatch")
if cal["truncation_order"]["expanded"] != list(reversed(by_rank)):
    fails.append("truncation-not-reverse")
# C3 Section 97.1 line 8838 - no sourceless category, and the two sets are identical.
sc = sorted(r["category"] for r in src["categories"])
if sc != sorted(c["name"] for c in cats):
    fails.append("source-category-set-mismatch")
for r in src["categories"]:
    if not r["record_stores"] and not r["event_phrases"]:
        fails.append("sourceless:%s" % r["category"])
# C4 Section 67.2 line 5592 / Section 97.4 line 8956 - flags are flags, ritual is not self-reported.
names = {c["name"] for c in cats}
for fl in tax["flags"]:
    if fl["name"] in names:
        fails.append("flag-is-category:%s" % fl["name"])
rit = [f for f in tax["flags"] if f["name"] == "ritual"]
if not rit or rit[0]["self_reportable"] is not False:
    fails.append("ritual-self-reportable")
# C5 Section 97.4 lines 8971-8972 - the two stated initial values, verbatim.
if cal["idle_gap_minutes"]["value"] != 30:
    fails.append("idle-gap:%s" % cal["idle_gap_minutes"]["value"])
if cal["granularity_hours"]["value"] != 0.25:
    fails.append("granularity:%s" % cal["granularity_hours"]["value"])
if cal["granularity_never_zero"]["value"] is not True:
    fails.append("granularity-zero-allowed")
# C6 Section 67.3 line 5603 - the five-minute cap.
if cal["self_report_cap_minutes_per_person_per_week"]["value"] != 5:
    fails.append("five-minute-cap")
if cal["self_report_per_product_attribution"]["value"] is not False:
    fails.append("per-product-self-report")
# C7 D102 line 10195 - every calibration key states a kind and a spec line.
for k, v in cal.items():
    if isinstance(v, dict):
        if "kind" not in v or ("spec_line" not in v and "spec_lines" not in v):
            fails.append("unsourced-key:%s" % k)
# C8 no threshold is a literal in code - every .py under metrics/attention reads this file.
py = []
for root, _, files in os.walk(h):
    for f in files:
        if f.endswith(".py"):
            py.append(os.path.join(root, f))
for p in py:
    body = open(p, encoding="utf-8").read()
    if "calibration.yaml" not in body and "load_calibration" not in body:
        fails.append("threshold-literal-risk:%s" % os.path.basename(p))
if fails:
    print("ATTNCFG FAIL %s" % ",".join(fails)); sys.exit(1)
print("ATTNCFG OK checks=8 categories=8 sources=8")
PY
VAC_EOF
chmod +x "$CP_ROOT/metrics/attention/validate-attention-config.sh"
"$CP_ROOT/metrics/attention/validate-attention-config.sh"
"$CP_ROOT/metrics/attention/validate-attention-config.sh" --selftest
git -C "$CP_ROOT" add metrics/attention/validate-attention-config.sh
git -C "$CP_ROOT" commit -m "L4-T405: attention config validator with seeded canary (charter rule 10)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The validator is executable | `test -x "$CP_ROOT/metrics/attention/validate-attention-config.sh" && echo YES` | `YES` |
| 2 | It passes on the real files | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" \| tail -1` | `ATTNCFG OK checks=8 categories=8 sources=8` |
| 3 | It exits `0` on a pass | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" >/dev/null; echo $?` | `0` |
| 4 | It rejects a seeded ninth category | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" --selftest \| tail -1` | `ATTNCFG OK selftest 1/1` |
| 5 | It fails closed when a config file is absent | see SELF-VERIFY `MISSING` | `3` |
| 6 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
V="$CP_ROOT/metrics/attention/validate-attention-config.sh"
echo "MAIN=$("$V" | tail -1)"
echo "RC=$("$V" >/dev/null 2>&1; echo $?)"
echo "CANARY=$("$V" --selftest | tail -1)"
T="$(mktemp -d)"; cp "$V" "$T/validate-attention-config.sh"
sh "$T/validate-attention-config.sh" >/dev/null 2>&1; echo "MISSING=$?"
rm -rf "$T"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
MAIN=ATTNCFG OK checks=8 categories=8 sources=8
RC=0
CANARY=ATTNCFG OK selftest 1/1
MISSING=3
FOREIGN=0
```

**STOP rule** — if `CANARY` is not `ATTNCFG OK selftest 1/1`, the validator accepted a ninth category and is decoration, not a check (charter §12 rule 10). If `MISSING` is not `3`, the validator returns a pass when it cannot reach its input; §40.1 line 3671 requires a check that cannot reach its input to **fail closed rather than reporting zero**. Do not relax a rule in the validator to make `MAIN` pass — a `FAIL` here means an earlier task's transcription is wrong. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T405 attention config validator cannot fail, or fails open"
lane: L4
phase: 4
task_id: L4-T405
blocked_by: "<canary accepted | missing input returned pass | real config rejected>"
observed: "<paste the exact SELF-VERIFY output and every ATTNCFG FAIL token>"
expected: "MAIN=ATTNCFG OK checks=8 categories=8 sources=8 / RC=0 / CANARY=ATTNCFG OK selftest 1/1 / MISSING=3 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 40.1 line 3671; Section 53.1 line 4685; Section 67.2 line 5579; Section 97.4 lines 8971-8973; L4-00-charter.md section 12 rule 10"
needs: "L0"
action_taken: "nothing beyond metrics/attention/validate-attention-config.sh"
```

---

### L4-T406 — Scheduled availability, the daily cap's input

**Size:** L
**Depends on:** L4-T404

Implements the seven-row resolution table of §3.5 and nothing else. The chain is §97.4 line 8975 → §69.2 line 5720 → §7.3 `work_arrangement` (D111, line 10209). This script **reads** `registries/people.yaml`; it never writes it.

**Every input is an explicit argument. There is no search, no fallback and no default number.** Five arguments are required — `--person`, `--date`, `--people`, `--calendar`, `--absence` — and a missing one is `SCHEDAVAIL ERROR`, exit `3`. `--calendar` is required because **D-L4-P4-03** is open: no rule yet selects the calendar-carrying record out of `records/leave/`, so the caller names the document. `--absence` is required for the same reason and takes this phase's own two-key contract, **not** a leave-record schema — L4 does not read `leave.schema.json` field names here, because inventing one would be a design decision.

The two input documents this script defines. They are **its own contract**, not record schemas:

```yaml
# --calendar <path>                    # --absence <path>
calendar_version: 1                    person: dev-a
public_holiday_sets:                   dates: [2026-09-17]
  IN: [2026-01-26, 2026-08-15]
```

**The declared span is wall-clock local time and needs no timezone database.** `work_arrangement.schedule.mon.start` and `.end` are declared local clock times (§7.3 line 572), so `end − start` is the span whatever the offset that day. The `timezone` field is therefore **format-checked only** — it must be an IANA identifier, never a UTC offset (§7.3 line 628) — and no `zoneinfo` or `pytz` import appears anywhere. Nothing in this script resolves an instant to a day; `derive.py` (L4-T411) takes the day from the input's declared `date` field and never computes one.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/scheduled-availability.py" <<'SCHED_EOF'
#!/usr/bin/env python3
# metrics/attention/scheduled-availability.py
# The daily cap's input. MasterSpec v4.0 Section 97.4 line 8975 -> Section 69.2 line 5720
# -> Section 7.3 work_arrangement (D111, line 10209).
# The resolution order R1-R7 is fixed by L4-04-attention-ledger.md section 3.5. Never a default
# number: an input that cannot be read is SCHEDAVAIL ERROR exit 3, never zero and never a guess.
# fte_application is read through load_calibration(); D-L4-P4-01 is open and this file does not
# decide it. No calibration.yaml threshold is written as a literal here.
import datetime, json, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
from config import load_calibration, value  # noqa: E402

WEEKDAY = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def fail(reason):
    print("SCHEDAVAIL ERROR %s" % reason)
    sys.exit(3)


def load(path, what):
    if not os.path.exists(path):
        fail("no-%s:%s" % (what, path))
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        fail("unparseable-%s:%s" % (what, path))


def minutes(hhmm):
    try:
        hours, mins = str(hhmm).split(":")
        return int(hours) * 60 + int(mins)
    except Exception:
        fail("unparseable-time:%s" % hhmm)


def main(argv):
    args = {}
    i = 0
    while i < len(argv):
        if not argv[i].startswith("--"):
            fail("unknown-argument:%s" % argv[i])
        key = argv[i][2:]
        if key == "json":
            args["json"] = True
            i += 1
            continue
        i += 1
        if i >= len(argv):
            fail("missing-value-for:%s" % key)
        args[key] = argv[i]
        i += 1
    for key in ("person", "date", "people", "calendar", "absence"):
        if key not in args:
            fail("missing-argument:%s" % key)         # R7; --calendar per D-L4-P4-03
    cal = load_calibration()

    # R1 - the person must be in the registry.
    registry = load(args["people"], "people-registry")
    person = None
    for entry in registry.get("people") or []:
        if entry.get("id") == args["person"]:
            person = entry
    if person is None:
        fail("person-not-in-registry")

    # R2 - fail closed where the declared working calendar is absent (Section 7.3, D111).
    wa = person.get("work_arrangement")
    if not wa:
        fail("no-work-arrangement")
    tz = str(wa.get("timezone", ""))
    if not tz or tz[0] in "+-" or tz.upper().startswith("UTC") or "/" not in tz:
        fail("timezone-not-iana:%s" % tz)             # Section 7.3 line 628

    try:
        day_date = datetime.date.fromisoformat(args["date"])
    except ValueError:
        fail("unparseable-date:%s" % args["date"])

    # R3 - a recorded absence covering the date.
    absence = load(args["absence"], "absence-document")
    if absence.get("person") != args["person"]:
        fail("absence-document-person-mismatch")
    if args["date"] in [str(x) for x in (absence.get("dates") or [])]:
        hours, rule = 0.0, "R3-recorded-absence"
    else:
        # R4 - the public-holiday list for this person's declared set.
        calendar = load(args["calendar"], "calendar")
        holiday_sets = calendar.get("public_holiday_sets") or {}
        set_name = wa.get("public_holiday_set")
        if set_name not in holiday_sets:
            fail("unknown-holiday-set:%s" % set_name)
        if args["date"] in [str(x) for x in (holiday_sets[set_name] or [])]:
            hours, rule = 0.0, "R4-public-holiday"
        else:
            # R5 - a weekday absent from the declared schedule is non-working.
            weekday = WEEKDAY[day_date.weekday()]
            schedule = wa.get("schedule") or {}
            if weekday not in schedule:
                hours, rule = 0.0, "R5-non-working-day"    # Section 7.3 line 571
            else:
                # R6 - the declared span, in declared local clock time.
                span = minutes(schedule[weekday].get("end")) - minutes(schedule[weekday].get("start"))
                if span <= 0:
                    fail("schedule-span-nonpositive:%s" % weekday)
                hours = span / 60.0
                applied = value(cal, "fte_application")    # D-L4-P4-01, declared default "none"
                if applied == "multiply":
                    hours = hours * float(wa.get("fte", 1.0))
                elif applied != "none":
                    fail("unsupported-fte-application:%s" % applied)
                rule = "R6-declared-schedule"
    hours = round(hours, 10)
    if args.get("json"):
        print(json.dumps({"person": args["person"], "date": args["date"],
                          "scheduled_availability_hours": hours, "rule": rule,
                          "timezone": tz,
                          "fte_application": value(cal, "fte_application")}, sort_keys=True))
    else:
        print("SCHEDAVAIL OK %s %s %s" % (args["person"], args["date"], hours))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
SCHED_EOF
git -C "$CP_ROOT" add metrics/attention/scheduled-availability.py
git -C "$CP_ROOT" commit -m "L4-T406: scheduled availability, the daily cap input (97.4 8975 -> 69.2 5720 -> 7.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file is valid Python | `python3 -m py_compile "$CP_ROOT/metrics/attention/scheduled-availability.py"; echo $?` | `0` |
| 2 | It reads calibration rather than holding a threshold | `grep -c 'load_calibration' "$CP_ROOT/metrics/attention/scheduled-availability.py"` | `2` |
| 3 | No timezone database is imported | `grep -c 'zoneinfo\|pytz' "$CP_ROOT/metrics/attention/scheduled-availability.py"` | `0` |
| 4 | It never writes the people registry | `grep -c 'yaml.safe_dump\|yaml.dump' "$CP_ROOT/metrics/attention/scheduled-availability.py"` | `0` |
| 5 | All five required arguments are enforced | see SELF-VERIFY `NOARGS` | `3` |
| 6 | Rules R1–R6 each resolve to their stated result | see SELF-VERIFY `R1`…`R6` | the six rows below |
| 7 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
T="$(mktemp -d)"
cat > "$T/people.yaml" <<'EOF'
registry_version: 1
people:
  - id: dev-a
    work_arrangement:
      timezone: Asia/Kolkata
      schedule:
        mon: { start: "09:30", end: "18:30" }
        tue: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
  - id: dev-z
EOF
cat > "$T/cal.yaml" <<'EOF'
calendar_version: 1
public_holiday_sets:
  IN: [2026-09-15]
EOF
printf 'person: dev-a\ndates: [2026-09-17]\n' > "$T/abs.yaml"
SA="$CP_ROOT/metrics/attention/scheduled-availability.py"
run() { python3 "$SA" --person "$1" --date "$2" --people "$T/people.yaml" \
        --calendar "$T/cal.yaml" --absence "$T/abs.yaml" 2>&1 | tail -1; }
echo "NOARGS=$(python3 "$SA" --person dev-a >/dev/null 2>&1; echo $?)"
echo "R1=$(run dev-nope 2026-09-14)"
echo "R2=$(run dev-z 2026-09-14)"
echo "R3=$(run dev-a 2026-09-17)"
echo "R4=$(run dev-a 2026-09-15)"
echo "R5=$(run dev-a 2026-09-16)"
echo "R6=$(run dev-a 2026-09-14)"
echo "PYC=$(python3 -m py_compile "$SA"; echo $?)"
echo "TZDB=$(grep -c 'zoneinfo\|pytz' "$SA")"
rm -rf "$T"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
NOARGS=3
R1=SCHEDAVAIL ERROR person-not-in-registry
R2=SCHEDAVAIL ERROR no-work-arrangement
R3=SCHEDAVAIL OK dev-a 2026-09-17 0.0
R4=SCHEDAVAIL OK dev-a 2026-09-15 0.0
R5=SCHEDAVAIL OK dev-a 2026-09-16 0.0
R6=SCHEDAVAIL OK dev-a 2026-09-14 9.0
PYC=0
TZDB=0
FOREIGN=0
```

The dates are chosen so that each row exercises exactly one rule: 2026-09-14 is a Monday (declared, R6, `09:30`–`18:30` = 9.0 hours); 2026-09-15 is a Tuesday declared as a holiday above (R4); 2026-09-16 is a Wednesday absent from the schedule (R5); 2026-09-17 is a Thursday covered by the absence document (R3).

**STOP rule** — if `R2` is not `SCHEDAVAIL ERROR no-work-arrangement`, the script has defaulted a schedule for a person who declared none, and every capacity figure downstream inherits a number nobody wrote; §7.3's coverage-check limb (line 630) requires that validator to **fail closed** where a member has no work arrangement, and this is the same rule. If `R6` is not `9.0`, either `fte` is being applied on top of a declared span — which is exactly what **D-L4-P4-01** exists to stop — or the span is being resolved through a timezone database. **Do not change `fte_application` in `calibration.yaml` to make a number come out**; a calibration value is refitted at a §84.6 line 7478 review, never edited during a build. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T406 scheduled availability resolves wrongly or fails open"
lane: L4
phase: 4
task_id: L4-T406
blocked_by: "<defaults on missing work_arrangement | fte applied twice | required argument not enforced | timezone database imported>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "NOARGS=3 / R1 and R2 are ERROR rows / R3=0.0 / R4=0.0 / R5=0.0 / R6=9.0 / PYC=0 / TZDB=0 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.4 line 8975; Section 69.2 line 5720; Section 7.3 lines 571, 572, 628, 629, 630; Section 7 line 577; D111 line 10209"
needs: "L0"
action_taken: "nothing beyond metrics/attention/scheduled-availability.py; registries/people.yaml untouched"
```

---

### L4-T407 — The duration rule, part 1: config reader, activity session, idle gap, granularity

**Size:** L
**Depends on:** L4-T404, L4-T405

Rules **DR-1**, **DR-2**, **DR-3** and **DR-4** of §3.3, and nothing else. Two files, both under `metrics/attention/lib/`.

**Binding mechanics, so nothing is chosen at the keyboard:**

| Rule | Mechanical statement | Spec line |
|---|---|---|
| DR-1 | A session is a maximal run within **one window**. Sessions never span windows. | 8969 |
| DR-2 | `next − previous <= idle_gap` continues the session; `>` opens a new one. The comparison is `<=`, so a gap of exactly the idle gap does **not** split — §97.4 line 8969 says *"separated by no more than the idle gap"*. | 8971 |
| DR-3 | `span = last_event − first_event`. A `bounds` pair is read **only** to drop events outside it, and never contributes a second to any duration. | 8969 |
| DR-4 | `units = floor(span_hours / granularity + 0.5)` — round half **away from zero**, which Python's built-in `round()` does **not** do — then `units = max(units, 1)`. | 8972 |

**There is deliberately no `lib/__init__.py`.** Callers put `metrics/attention/lib` on `sys.path` and import the modules by name. An `__init__.py` would be a `.py` file under `metrics/attention/` mentioning neither `calibration.yaml` nor `load_calibration`, and check **C8** of `validate-attention-config.sh` (L4-T405) would fail the phase.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/lib/config.py" <<'CFG_EOF'
# metrics/attention/lib/config.py
# The ONLY reader of calibration.yaml, taxonomy.yaml and sources.yaml in this phase.
# No other module opens them, and no module holds a threshold as a literal (D102, line 10195).
# There is deliberately no __init__.py: callers put this directory on sys.path.
import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(name):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        raise SystemExit("ATTN ERROR missing-config:%s" % name)
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not doc:
        raise SystemExit("ATTN ERROR empty-config:%s" % name)
    return doc


def load_calibration():
    return _load("calibration.yaml")


def load_taxonomy():
    return _load("taxonomy.yaml")


def load_sources():
    return _load("sources.yaml")


def value(cal, key):
    if key not in cal or "value" not in cal[key]:
        raise SystemExit("ATTN ERROR unknown-calibration-key:%s" % key)
    return cal[key]["value"]
CFG_EOF
cat > "$CP_ROOT/metrics/attention/lib/sessions.py" <<'SESS_EOF'
# metrics/attention/lib/sessions.py
# DR-1 activity session, DR-2 idle gap, DR-3 session duration, DR-4 granularity.
# MasterSpec v4.0 Section 97.4 lines 8969, 8971, 8972.
# Every threshold arrives through load_calibration(); calibration.yaml is the only authority.
import datetime
import math
from config import load_calibration, value


def parse_ts(raw):
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        raise SystemExit("ATTN ERROR unparseable-timestamp:%s" % raw)


def normalise_events(window):
    """An event is a bare timestamp (product from the window) or {at: ..., product: ...}."""
    default_product = window.get("product")
    out = []
    for ev in window.get("events") or []:
        if isinstance(ev, dict):
            out.append((parse_ts(ev["at"]), ev.get("product", default_product)))
        else:
            out.append((parse_ts(ev), default_product))
    bounds = window.get("bounds")
    if bounds:
        # Section 97.4 line 8969: the interval bounds the SEARCH, never the duration.
        low, high = parse_ts(bounds[0]), parse_ts(bounds[1])
        out = [e for e in out if low <= e[0] <= high]
    out.sort(key=lambda e: e[0])
    return out


def sessionise(events, cal=None):
    """DR-1 and DR-2. A gap EQUAL to the idle gap continues the session; a wider gap ends it."""
    cal = cal or load_calibration()
    gap = datetime.timedelta(minutes=value(cal, "idle_gap_minutes"))
    sessions = []
    for ev in events:
        if sessions and (ev[0] - sessions[-1][-1][0]) <= gap:
            sessions[-1].append(ev)
        else:
            sessions.append([ev])
    return sessions


def round_units(span_hours, cal=None):
    """DR-4. Round half AWAY FROM ZERO - Python's round() is half-to-even and is wrong here."""
    cal = cal or load_calibration()
    grain = value(cal, "granularity_hours")
    units = int(math.floor(abs(float(span_hours)) / grain + 0.5))
    if value(cal, "granularity_never_zero") and units < 1:
        units = 1
    return round(units * grain, 10)


def session_hours(session, cal=None):
    """DR-3 then DR-4. A single-event session has span zero and becomes one grain."""
    span = (session[-1][0] - session[0][0]).total_seconds() / 3600.0
    return round_units(span, cal)
SESS_EOF
git -C "$CP_ROOT" add metrics/attention/lib/config.py metrics/attention/lib/sessions.py
git -C "$CP_ROOT" commit -m "L4-T407: DR-1..DR-4 activity session, idle gap, span, granularity (97.4 8969-8972)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both files compile | `python3 -m py_compile "$CP_ROOT"/metrics/attention/lib/config.py "$CP_ROOT"/metrics/attention/lib/sessions.py; echo $?` | `0` |
| 2 | No `__init__.py` was created | `test ! -f "$CP_ROOT/metrics/attention/lib/__init__.py" && echo YES` | `YES` |
| 3 | A gap of exactly the idle gap does not split | see SELF-VERIFY `BOUNDARY` | `1` |
| 4 | A gap one minute wider does split | see SELF-VERIFY `SPLIT` | `2` |
| 5 | A single-event session is one grain, never zero | see SELF-VERIFY `SINGLE` | `0.25` |
| 6 | Half rounds away from zero, not to even | see SELF-VERIFY `HALF` | `0.5` |
| 7 | `bounds` filters events and adds no duration | see SELF-VERIFY `BOUNDSIGNORED` | `1` |
| 8 | The config validator still passes with the new `.py` files present | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" \| tail -1` | `ATTNCFG OK checks=8 categories=8 sources=8` |
| 9 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["CP_ROOT"], "metrics", "attention", "lib"))
import sessions as S
w1 = {"product": "alpha", "events": ["2026-09-14T09:00:00Z", "2026-09-14T09:30:00Z"]}
w2 = {"product": "alpha", "events": ["2026-09-14T09:00:00Z", "2026-09-14T09:31:00Z"]}
w3 = {"product": "alpha", "events": ["2026-09-14T14:00:00Z"]}
w4 = {"product": "alpha", "bounds": ["2026-09-14T13:00:00Z", "2026-09-14T15:00:00Z"],
      "events": ["2026-09-14T12:00:00Z", "2026-09-14T13:40:00Z"]}
print("BOUNDARY=%d" % len(S.sessionise(S.normalise_events(w1))))
print("SPLIT=%d" % len(S.sessionise(S.normalise_events(w2))))
print("SINGLE=%s" % S.session_hours(S.sessionise(S.normalise_events(w3))[0]))
print("HALF=%s" % S.round_units(0.375))
print("BOUNDSIGNORED=%d" % len(S.normalise_events(w4)))
PY
echo "INIT=$(test ! -f "$CP_ROOT/metrics/attention/lib/__init__.py" && echo absent || echo present)"
echo "CFG=$("$CP_ROOT/metrics/attention/validate-attention-config.sh" | tail -1)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
BOUNDARY=1
SPLIT=2
SINGLE=0.25
HALF=0.5
BOUNDSIGNORED=1
INIT=absent
CFG=ATTNCFG OK checks=8 categories=8 sources=8
FOREIGN=0
```

`HALF` is the rounding proof: `0.375 / 0.25 = 1.5`, and half away from zero gives `2` grains, so `0.5`. Python's built-in `round(1.5)` is `2` but `round(2.5)` is also `2`, which is why `math.floor(x + 0.5)` is written out rather than `round()` being trusted. `BOUNDSIGNORED` is the DR-3 proof: the 12:00 event lies outside the declared bounds and is dropped, and the two-hour bounds themselves contribute nothing.

**STOP rule** — if `BOUNDARY` is not `1`, the comparison is `<` where §97.4 line 8969 says *"no more than"*, and every session in the portfolio silently fragments into shorter ones. If `SINGLE` is not `0.25`, the never-zero limb of line 8972 is not implemented and single-event sessions vanish from the ledger entirely. If `CFG` is not `ATTNCFG OK …`, check **C8** of L4-T405 has found a `.py` file under `metrics/attention/` that neither mentions `calibration.yaml` nor imports `load_calibration` — **add the import; never remove check C8** (charter §12 rule 10). Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T407 duration rule DR-1..DR-4 does not hold at its boundaries"
lane: L4
phase: 4
task_id: L4-T407
blocked_by: "<idle-gap comparison wrong | single-event session rounds to zero | half rounds to even | bounds counted as duration | config validator now fails>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "BOUNDARY=1 / SPLIT=2 / SINGLE=0.25 / HALF=0.5 / BOUNDSIGNORED=1 / INIT=absent / CFG=ATTNCFG OK checks=8 categories=8 sources=8 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8969, 8971, 8972; D102 line 10195; L4-00-charter.md section 12 rule 10"
needs: "L0"
action_taken: "nothing beyond metrics/attention/lib/config.py and metrics/attention/lib/sessions.py"
```

---

### L4-T408 — The duration rule, part 2: category precedence (DR-5)

**Size:** M
**Depends on:** L4-T407

Rule **DR-5** of §3.3. §97.4 line 8973 fixes the order and the outcome: *"a session falling inside two windows resolves in this fixed order and the losing categories receive nothing."* §67.1 line 5573 is why: exactly one category always receives the hour.

**Two mechanical statements the executor must not vary:**

1. **Same session** means **identical event-timestamp signature** — the tuple of the session's event instants, in order. Windows whose signatures differ are different sessions and both are counted; no partial overlap is resolved, because line 8973 speaks of a session falling inside two windows, not of two different sessions.
2. **The loser is recorded at `0.0`, for the same products, never omitted.** A category dropped from the output is indistinguishable from a category with no work, and §84.6 line 7471's `expected_interpretation` attribute becomes unreadable. The fixture `DC-4` (`L4-P7-T09`) asserts `Review: {alpha: 0.0}` present.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/lib/precedence.py" <<'PREC_EOF'
# metrics/attention/lib/precedence.py
# DR-5 category precedence. MasterSpec v4.0 Section 97.4 line 8973; Section 67.1 line 5573.
# The order is read from calibration.yaml through load_calibration(); it is never written here.
from config import load_calibration, value


def signature(session):
    """Two windows contain the SAME session when their event instants are identical."""
    return tuple(ev[0].isoformat() for ev in session)


def resolve(window_sessions, cal=None):
    """window_sessions: [(category, session)]. Returns (winners, losers), same shape.

    Insertion order of the first-seen signature is preserved, so the result is
    deterministic for a given input file and does not depend on hash ordering.
    """
    cal = cal or load_calibration()
    order = value(cal, "precedence_order")
    rank = {name: i for i, name in enumerate(order)}
    for category, _ in window_sessions:
        if category not in rank:
            raise SystemExit("ATTN ERROR category-not-in-precedence:%s" % category)
    groups = {}
    for category, session in window_sessions:
        groups.setdefault(signature(session), []).append((category, session))
    winners, losers = [], []
    for sig in groups:
        ordered = sorted(groups[sig], key=lambda cs: rank[cs[0]])
        winners.append(ordered[0])
        losers.extend(ordered[1:])
    return winners, losers
PREC_EOF
git -C "$CP_ROOT" add metrics/attention/lib/precedence.py
git -C "$CP_ROOT" commit -m "L4-T408: DR-5 category precedence, losers recorded at zero (97.4 line 8973)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file compiles | `python3 -m py_compile "$CP_ROOT/metrics/attention/lib/precedence.py"; echo $?` | `0` |
| 2 | The order is read, not written | `grep -c 'Incident' "$CP_ROOT/metrics/attention/lib/precedence.py"` | `0` |
| 3 | Incident outranks Review on the same session | see SELF-VERIFY `WIN` | `Incident` |
| 4 | The losing category is returned, not dropped | see SELF-VERIFY `LOSE` | `Review` |
| 5 | Different signatures both win | see SELF-VERIFY `DISTINCT` | `2 0` |
| 6 | A category outside the taxonomy is rejected | see SELF-VERIFY `UNKNOWN` | `1` |
| 7 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["CP_ROOT"], "metrics", "attention", "lib"))
import sessions as S, precedence as P
def sess(times, product="alpha"):
    return S.sessionise(S.normalise_events({"product": product, "events": times}))[0]
same = sess(["2026-09-14T13:40:00Z", "2026-09-14T14:00:00Z", "2026-09-14T14:20:00Z"])
w, l = P.resolve([("Review", same), ("Incident", same)])
print("WIN=%s" % w[0][0]); print("LOSE=%s" % l[0][0])
a = sess(["2026-09-14T09:00:00Z"]); b = sess(["2026-09-14T11:00:00Z"])
w2, l2 = P.resolve([("Engineering", a), ("Planning", b)])
print("DISTINCT=%d %d" % (len(w2), len(l2)))
try:
    P.resolve([("Meetings", a)]); print("UNKNOWN=0")
except SystemExit:
    print("UNKNOWN=1")
PY
echo "ORDERWRITTEN=$(grep -c 'Incident' "$CP_ROOT/metrics/attention/lib/precedence.py")"
echo "CFG=$("$CP_ROOT/metrics/attention/validate-attention-config.sh" | tail -1)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
WIN=Incident
LOSE=Review
DISTINCT=2 0
UNKNOWN=1
ORDERWRITTEN=0
CFG=ATTNCFG OK checks=8 categories=8 sources=8
FOREIGN=0
```

**STOP rule** — if `WIN` is not `Incident`, the fixed order of line 8973 has been reordered or the rank map is inverted; §97.4 line 8973 states *"Incident outranks everything because an incident window is the one interval whose attention is not discretionary."* If `LOSE` is empty, the losing category is being dropped rather than recorded at zero and fixture `DC-4` will fail in `L4-P7-T09` with no way to localise it. If `ORDERWRITTEN` is not `0`, the precedence order has been copied into code and now exists in two places — delete the copy, never the file. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T408 precedence resolution is wrong or drops the losing category"
lane: L4
phase: 4
task_id: L4-T408
blocked_by: "<wrong winner | loser dropped | order duplicated into code | unknown category accepted>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "WIN=Incident / LOSE=Review / DISTINCT=2 0 / UNKNOWN=1 / ORDERWRITTEN=0"
spec_ref: "Master Spec v4.0 Section 97.4 line 8973; Section 67.1 line 5573; Section 67.2 line 5579"
needs: "L0"
action_taken: "nothing beyond metrics/attention/lib/precedence.py"
```

---

### L4-T409 — The duration rule, part 3: product attribution (DR-6)

**Size:** M
**Depends on:** L4-T407

Rule **DR-6** of §3.3. §97.4 line 8974: *"A session whose events touch one product attributes to that product; a session touching several splits across them by event count; a session touching none attributes to the portfolio."*

**The rounding order is read from `calibration.yaml`, not decided here.** `rounding_order: round_then_split` carries `decided: D-L4-P7-03` (round-then-split, see `_DECISION_SIGNOFF.md`). The module **refuses to run** on any other value rather than guessing a second behaviour — a hard failure is visible; a silent second code path is not.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/lib/attribute.py" <<'ATTR_EOF'
# metrics/attention/lib/attribute.py
# DR-6 product attribution. MasterSpec v4.0 Section 97.4 line 8974.
# rounding_order arrives through load_calibration() and carries decided: D-L4-P7-03 (round-then-split).
# This module implements exactly the declared value and refuses any other; it never chooses.
from config import load_calibration, value

PORTFOLIO = "portfolio"


def split(session, hours, cal=None):
    """Returns {product: hours}. A session touching no product goes to the portfolio."""
    cal = cal or load_calibration()
    if value(cal, "rounding_order") != "round_then_split":
        raise SystemExit("ATTN ERROR unsupported-rounding-order:%s"
                         % value(cal, "rounding_order"))
    named = [product for _, product in session if product]
    if not named:
        return {PORTFOLIO: round(float(hours), 10)}
    counts = {}
    for product in named:
        counts[product] = counts.get(product, 0) + 1
    total = float(len(named))
    return {p: round(float(hours) * counts[p] / total, 10) for p in counts}
ATTR_EOF
git -C "$CP_ROOT" add metrics/attention/lib/attribute.py
git -C "$CP_ROOT" commit -m "L4-T409: DR-6 product attribution by event count (97.4 line 8974)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file compiles | `python3 -m py_compile "$CP_ROOT/metrics/attention/lib/attribute.py"; echo $?` | `0` |
| 2 | One product takes the whole session | see SELF-VERIFY `ONE` | `{'alpha': 1.25}` |
| 3 | Several split by event count | see SELF-VERIFY `MANY` | `alpha=0.5 beta=0.25 gamma=0.25` |
| 4 | None goes to the portfolio | see SELF-VERIFY `NONE` | `{'portfolio': 0.75}` |
| 5 | The rounding order is read, not decided | `grep -c 'round_then_split' "$CP_ROOT/metrics/attention/lib/attribute.py"` | `1` |
| 6 | An unrecognised rounding order is refused | see SELF-VERIFY `REFUSE` | `1` |
| 7 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["CP_ROOT"], "metrics", "attention", "lib"))
import sessions as S, attribute as A
one = S.sessionise(S.normalise_events(
    {"product": "alpha", "events": ["2026-09-14T09:00:00Z", "2026-09-14T10:15:00Z"]}))[0]
print("ONE=%s" % A.split(one, 1.25))
many = S.sessionise(S.normalise_events({"events": [
    {"at": "2026-09-14T11:00:00Z", "product": "alpha"},
    {"at": "2026-09-14T11:20:00Z", "product": "alpha"},
    {"at": "2026-09-14T11:40:00Z", "product": "beta"},
    {"at": "2026-09-14T12:00:00Z", "product": "gamma"}]}))[0]
m = A.split(many, 1.0)
print("MANY=alpha=%s beta=%s gamma=%s" % (m["alpha"], m["beta"], m["gamma"]))
none = S.sessionise(S.normalise_events(
    {"events": ["2026-09-14T09:00:00Z", "2026-09-14T09:45:00Z"]}))[0]
print("NONE=%s" % A.split(none, 0.75))
bad = {"rounding_order": {"value": "split_then_round"}}
try:
    A.split(one, 1.0, bad); print("REFUSE=0")
except SystemExit:
    print("REFUSE=1")
PY
echo "READS=$(grep -c 'round_then_split' "$CP_ROOT/metrics/attention/lib/attribute.py")"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
ONE={'alpha': 1.25}
MANY=alpha=0.5 beta=0.25 gamma=0.25
NONE={'portfolio': 0.75}
REFUSE=1
READS=1
FOREIGN=0
```

(`none` is two events 45 minutes apart — one session under a 30-minute idle gap? No: 45 > 30, so it is **two** sessions and `[0]` is the first. The split is being exercised, not the sessioniser; the `0.75` passed in is the hours argument, not a derived span.)

**STOP rule** — if `NONE` is not `{'portfolio': 0.75}` the portfolio limb of line 8974 is missing and every session with no product silently disappears from the ledger rather than landing on the portfolio. If `REFUSE` is not `1`, the module has a second code path for a rounding order **L0 has not chosen** — delete it. Do not add a fixture that distinguishes the two orders (§5, `D-L4-P7-03`). Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T409 product attribution drops sessions or guesses a rounding order"
lane: L4
phase: 4
task_id: L4-T409
blocked_by: "<portfolio limb missing | split not by event count | second rounding path present>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "ONE={'alpha': 1.25} / MANY=alpha=0.5 beta=0.25 gamma=0.25 / NONE={'portfolio': 0.75} / REFUSE=1 / READS=1"
spec_ref: "Master Spec v4.0 Section 97.4 line 8974; L4-07-tests-and-runbook.md decision D-L4-P7-03"
needs: "L0"
action_taken: "nothing beyond metrics/attention/lib/attribute.py"
```

---

### L4-T410 — The duration rule, part 4: daily reconciliation and the instrument defect (DR-7)

**Size:** L
**Depends on:** L4-T404, L4-T406

Rule **DR-7** of §3.3 and the instrument-defect rule of §97.4 line 8976. This is the task the per-person daily cap of the brief lands in.

**Binding mechanics:**

| Statement | Spec line |
|---|---|
| The cap is that person's scheduled availability for that day, resolved by L4-T406 through §69.2 line 5720 to `work_arrangement` (§7.3). | 8975 |
| Truncation runs in **reverse precedence order** — `Coordination, Operational, Planning, Architecture, Engineering, Review, Verification, Incident` — read from `calibration.yaml`, never written in code. | 8975 |
| **Each truncation is recorded**: a list entry naming the category and the hours removed. A silent truncation is the same instrument failure as a silent zero (§97.2 line 8869). | 8975 |
| A day exceeding the cap **before** truncation is an **instrument defect**, not a workload finding, and never enters a Capacity Profile, a workload state (§83.1, line 7280) or the Founder view (§93). | 8976 |
| The three eligibility flags are **emitted, not consumed, by L4**. Subsystem P owns the consumer and PARTITION v1 assigns it to no lane (§5, `D-L4-P4-04`). | 9203 |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/lib/reconcile.py" <<'REC_EOF'
# metrics/attention/lib/reconcile.py
# DR-7 daily reconciliation, and the instrument-defect rule.
# MasterSpec v4.0 Section 97.4 lines 8975 and 8976. Section 83.1 line 7280; Section 93.
# The truncation order arrives through load_calibration(); it is never written here.
from config import load_calibration, value

EPS = 1e-9


def reconcile(hours_by_category, cap, cal=None):
    """Returns (post_hours, truncation_detail, instrument_defect).

    instrument_defect is decided on the PRE-truncation total, per line 8976.
    """
    cal = cal or load_calibration()
    if value(cal, "truncation_order") != "reverse_precedence":
        raise SystemExit("ATTN ERROR unsupported-truncation-order:%s"
                         % value(cal, "truncation_order"))
    sequence = cal["truncation_order"]["expanded"]
    order = value(cal, "precedence_order")
    if sequence != list(reversed(order)):
        raise SystemExit("ATTN ERROR truncation-order-not-reverse-precedence")
    post = {k: round(float(v), 10) for k, v in hours_by_category.items()}
    pre_total = round(sum(post.values()), 10)
    cap = round(float(cap), 10)
    defect = pre_total > cap + EPS
    excess = round(pre_total - cap, 10)
    detail = []
    for category in sequence:
        if excess <= EPS:
            break
        have = post.get(category, 0.0)
        if have <= EPS:
            continue
        take = round(have if have < excess else excess, 10)
        post[category] = round(have - take, 10)
        detail.append({"category": category, "hours_removed": take})
        excess = round(excess - take, 10)
    return post, detail, defect


def eligibility(instrument_defect):
    """Section 97.4 line 8976: a defect day enters none of the three surfaces."""
    ok = not instrument_defect
    return {"capacity_profile_eligible": ok,
            "workload_state_eligible": ok,
            "founder_view_eligible": ok}
REC_EOF
git -C "$CP_ROOT" add metrics/attention/lib/reconcile.py
git -C "$CP_ROOT" commit -m "L4-T410: DR-7 daily reconciliation and the instrument-defect rule (97.4 8975-8976)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file compiles | `python3 -m py_compile "$CP_ROOT/metrics/attention/lib/reconcile.py"; echo $?` | `0` |
| 2 | An over-cap day truncates Coordination first | see SELF-VERIFY `TRUNC` | `Coordination 0.5` |
| 3 | The post-truncation total equals the cap | see SELF-VERIFY `TOTAL` | `8.0` |
| 4 | The over-cap day is an instrument defect | see SELF-VERIFY `DEFECT` | `True` |
| 5 | A defect day is ineligible for all three surfaces | see SELF-VERIFY `ELIG` | `False False False` |
| 6 | An at-or-under-cap day truncates nothing and is not a defect | see SELF-VERIFY `CLEAN` | `0 False True` |
| 7 | The truncation order is not written in code | `grep -c 'Coordination' "$CP_ROOT/metrics/attention/lib/reconcile.py"` | `0` |
| 8 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["CP_ROOT"], "metrics", "attention", "lib"))
import reconcile as R
pre = {"Incident": 3.00, "Verification": 2.00, "Review": 1.50,
       "Engineering": 1.25, "Coordination": 0.75}
post, detail, defect = R.reconcile(pre, 8.0)
print("TRUNC=%s %s" % (detail[0]["category"], detail[0]["hours_removed"]))
print("TOTAL=%s" % round(sum(post.values()), 10))
print("DEFECT=%s" % defect)
e = R.eligibility(defect)
print("ELIG=%s %s %s" % (e["capacity_profile_eligible"], e["workload_state_eligible"],
                         e["founder_view_eligible"]))
post2, detail2, defect2 = R.reconcile({"Engineering": 4.0, "Review": 2.0, "Planning": 1.5}, 8.0)
print("CLEAN=%d %s %s" % (len(detail2), defect2,
                          R.eligibility(defect2)["capacity_profile_eligible"]))
PY
echo "ORDERWRITTEN=$(grep -c 'Coordination' "$CP_ROOT/metrics/attention/lib/reconcile.py")"
echo "CFG=$("$CP_ROOT/metrics/attention/validate-attention-config.sh" | tail -1)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
TRUNC=Coordination 0.5
TOTAL=8.0
DEFECT=True
ELIG=False False False
CLEAN=0 False True
ORDERWRITTEN=0
CFG=ATTNCFG OK checks=8 categories=8 sources=8
FOREIGN=0
```

**STOP rule** — if `TRUNC` names a category other than `Coordination`, the truncation is not running in reverse precedence order and the ledger is removing Incident hours before Coordination hours, which inverts the meaning of every utilisation composition built on it (§70.1, line 5741). If `DEFECT` is `False` for a day totalling 8.50 against a cap of 8.00, line 8976 is not implemented and an instrument failure is about to be reported to a human as a workload finding about a person — the precise harm §91.2 (lines 8083–8092) and §83 exist to prevent. **Never raise the cap to clear a defect.** Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T410 daily reconciliation truncates in the wrong order or hides an instrument defect"
lane: L4
phase: 4
task_id: L4-T410
blocked_by: "<truncation not reverse precedence | truncation not recorded | defect flag not raised | eligibility flags not emitted>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "TRUNC=Coordination 0.5 / TOTAL=8.0 / DEFECT=True / ELIG=False False False / CLEAN=0 False True / ORDERWRITTEN=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8975, 8976; Section 83.1 line 7280; Section 91.2 lines 8083-8092; Section 99.2 line 9203"
needs: "L0"
action_taken: "nothing beyond metrics/attention/lib/reconcile.py; no Capacity Profile built (D-L4-P4-04)"
```

---

### L4-T411 — `derive.py`, the attention ledger

**Size:** L
**Depends on:** L4-T407, L4-T408, L4-T409, L4-T410

The one executable that composes DR-1…DR-7 and the weekly self-report of §97.4 line 8980. **Its command line and its JSON shape are input to this task, not output of it** — `L4-07-tests-and-runbook.md` tasks `L4-P7-T09` and `L4-P7-T12` already fixed both (§2.2). Nothing below may be varied to taste.

**The three input shapes and the mode each selects, in this order:**

| # | Input carries | Mode | What the mode is |
|---|---|---|---|
| 1 | `self_reports` | self-report | §97.4 line 8980 apportionment, permanent provenance, ritual refusal |
| 2 | `pre_truncation_hours` | day close | DR-7: the daily reconciliation and the instrument-defect flags |
| 3 | `windows` | window derivation | DR-1…DR-6: sessions, precedence, granularity, product split |

Anything else is `ATTN ERROR unrecognised-input-shape`, exit `3`. **Never guess a shape.**

**Window mode does not truncate, and that is deliberate.** §97.4 line 8975 reconciles *"derived hours for a person on a day"* — a day-level operation whose input is the day's totals, which is exactly what day-close mode takes. Window mode derives one window set, emits `truncations: 0`, and still emits `instrument_defect`, which line 8976 defines on the **pre**-truncation total and is therefore well-defined without truncating anything.

**The key-presence rule is read off the fixtures, not chosen.** `L4-P7-T09` compares whole normalised JSON documents, so an extra key fails a case exactly as a wrong number does. `DC-6` carries `truncation_detail` and all three eligibility flags; `DC-7` carries neither. Therefore:

| Key | Emitted when |
|---|---|
| `truncation_detail` | `truncations > 0` |
| `capacity_profile_eligible` | day-close mode, always |
| `workload_state_eligible`, `founder_view_eligible` | day-close mode, and `instrument_defect` is `true` |
| `sessions`, `hours` | window mode only |
| `total_hours`, `hours_by_category` | day-close mode only |
| `apportioned` | self-report mode only |

**`--query-product <p>`** aggregates every window-mode input given on the same command line and emits `{"product": <p>, "hours": <float>}`. `L4-P7-T12` reads `["hours"]` and formats it as `.2f`; over `dc-1`, `dc-3`, `dc-4` and `dc-5` filtered to `alpha` the sum is `1.25 + 0.25 + 0.75 + 0.50 = 2.75`, which is the value that suite asserts.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/lib/selfreport.py" <<'SR_EOF'
# metrics/attention/lib/selfreport.py
# The weekly banded self-report. MasterSpec v4.0 Section 97.4 line 8980.
# "one band per category, unattributed to any product"; apportioned by machine-derived share;
# "to the portfolio where no share exists"; the self-reported provenance label is permanent.
# The ritual flag is NEVER self-reported (Section 67.2 line 5592) - a self-report carrying it
# is rejected, not cleaned. The cap and the band table come through load_calibration().
from config import load_calibration, value

PORTFOLIO = "portfolio"


def apportion(doc, cal=None):
    cal = cal or load_calibration()
    if value(cal, "self_report_per_product_attribution"):
        raise SystemExit("ATTN ERROR per-product-self-report-enabled")
    shares = doc.get("machine_activity_shares") or {}
    out = []
    for entry in doc.get("self_reports") or []:
        if "ritual" in entry:
            # Section 67.2 line 5592: set by the workflow that opens the ritual, never self-reported.
            raise SystemExit("ATTN ERROR ritual-self-reported:%s" % entry.get("person"))
        if entry.get("product") not in (None, "", PORTFOLIO):
            raise SystemExit("ATTN ERROR self-report-carries-product:%s" % entry.get("person"))
        person = entry["person"]
        hours = float(entry["hours"])
        mine = shares.get(person) or {}
        if not mine:
            out.append({"person": person, "product": PORTFOLIO, "category": entry["category"],
                        "hours": round(hours, 10), "provenance": "self-reported"})
            continue
        for product, share in mine.items():
            out.append({"person": person, "product": product, "category": entry["category"],
                        "hours": round(hours * float(share), 10), "provenance": "self-reported"})
    return out
SR_EOF
cat > "$CP_ROOT/metrics/attention/derive.py" <<'DER_EOF'
#!/usr/bin/env python3
# metrics/attention/derive.py
# THE ATTENTION LEDGER. MasterSpec v4.0 Section 97.4 lines 8955-8981.
# Command line and JSON shape fixed by L4-07-tests-and-runbook.md tasks L4-P7-T09 and L4-P7-T12:
#   derive.py --input <f.yaml> [--input <f.yaml> ...] [--query-product <p>] [--json]
# Every threshold arrives from calibration.yaml through load_calibration(); this file holds none.
import json
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
from config import load_calibration  # noqa: E402
import sessions as S                 # noqa: E402
import precedence as P               # noqa: E402
import attribute as A                # noqa: E402
import reconcile as R                # noqa: E402
import selfreport as SR              # noqa: E402

EPS = 1e-9


def q(number):
    return round(float(number), 10)


def derive_windows(doc, cal):
    """DR-1..DR-6. Returns (output, hours) where hours is {category: {product: h}}."""
    pairs = []
    for window in doc.get("windows") or []:
        if "category" not in window:
            raise SystemExit("ATTN ERROR window-without-category")
        for session in S.sessionise(S.normalise_events(window), cal):
            pairs.append((window["category"], session))
    winners, losers = P.resolve(pairs, cal)
    hours = {}
    for category, session in winners:
        earned = S.session_hours(session, cal)
        for product, part in A.split(session, earned, cal).items():
            hours.setdefault(category, {})
            hours[category][product] = q(hours[category].get(product, 0.0) + part)
    for category, session in losers:
        # Section 97.4 line 8973: the losing categories receive nothing - recorded, not omitted.
        for product in A.split(session, 0.0, cal):
            hours.setdefault(category, {})
            hours[category].setdefault(product, 0.0)
    defect = False
    cap = doc.get("scheduled_availability_hours")
    if cap is not None:
        total = q(sum(sum(v.values()) for v in hours.values()))
        defect = total > float(cap) + EPS          # Section 97.4 line 8976, pre-truncation
    out = {"case": doc.get("case"), "sessions": len(winners), "hours": hours,
           "truncations": 0, "instrument_defect": bool(defect)}
    return out, hours


def derive_day(doc, cal):
    """DR-7 plus the instrument-defect rule. Section 97.4 lines 8975 and 8976."""
    if "scheduled_availability_hours" not in doc:
        raise SystemExit("ATTN ERROR day-close-without-cap")
    pre = {k: float(v) for k, v in (doc.get("pre_truncation_hours") or {}).items()}
    post, detail, defect = R.reconcile(pre, doc["scheduled_availability_hours"], cal)
    flags = R.eligibility(defect)
    out = {"case": doc.get("case"),
           "total_hours": q(sum(post.values())),
           "hours_by_category": {k: q(v) for k, v in post.items()},
           "truncations": len(detail)}
    if detail:
        out["truncation_detail"] = detail
    out["instrument_defect"] = bool(defect)
    out["capacity_profile_eligible"] = flags["capacity_profile_eligible"]
    if defect:
        out["workload_state_eligible"] = flags["workload_state_eligible"]
        out["founder_view_eligible"] = flags["founder_view_eligible"]
    return out


def main(argv):
    inputs, query, as_json = [], None, False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--input":
            i += 1
            if i >= len(argv):
                print("ATTN ERROR missing-value-for:--input", file=sys.stderr)
                return 2
            inputs.append(argv[i])
        elif arg == "--query-product":
            i += 1
            if i >= len(argv):
                print("ATTN ERROR missing-value-for:--query-product", file=sys.stderr)
                return 2
            query = argv[i]
        elif arg == "--json":
            as_json = True
        else:
            print("ATTN ERROR unknown-argument:%s" % arg, file=sys.stderr)
            return 2
        i += 1
    if not inputs:
        print("ATTN ERROR no-input", file=sys.stderr)
        return 2
    cal = load_calibration()
    results, per_product = [], {}
    for path in inputs:
        if not os.path.exists(path):
            print("ATTN ERROR missing-input:%s" % path, file=sys.stderr)
            return 3
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        if "self_reports" in doc:
            results.append({"case": doc.get("case"), "apportioned": SR.apportion(doc, cal)})
        elif "pre_truncation_hours" in doc:
            results.append(derive_day(doc, cal))
        elif "windows" in doc:
            out, hours = derive_windows(doc, cal)
            results.append(out)
            for product_map in hours.values():
                for product, value_ in product_map.items():
                    per_product[product] = q(per_product.get(product, 0.0) + value_)
        else:
            print("ATTN ERROR unrecognised-input-shape:%s" % path, file=sys.stderr)
            return 3
    if query is not None:
        payload = {"product": query, "hours": q(per_product.get(query, 0.0))}
    elif len(results) == 1:
        payload = results[0]
    else:
        payload = {"results": results}
    if as_json:
        print(json.dumps(payload))
    else:
        print("ATTENTION OK inputs=%d" % len(inputs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
DER_EOF
chmod +x "$CP_ROOT/metrics/attention/derive.py"
git -C "$CP_ROOT" add metrics/attention/lib/selfreport.py metrics/attention/derive.py
git -C "$CP_ROOT" commit -m "L4-T411: derive.py - the attention ledger, DR-1..DR-7 and the weekly band (97.4)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both files compile | `python3 -m py_compile "$CP_ROOT"/metrics/attention/derive.py "$CP_ROOT"/metrics/attention/lib/selfreport.py; echo $?` | `0` |
| 2 | `derive.py` is executable | `test -x "$CP_ROOT/metrics/attention/derive.py" && echo YES` | `YES` |
| 3 | Window mode: gaps, span and granularity | see SELF-VERIFY `W1` | `{"case": "V-1", "hours": {"Engineering": {"alpha": 1.25}}, "instrument_defect": false, "sessions": 1, "truncations": 0}` |
| 4 | Precedence records the loser at zero | see SELF-VERIFY `W2` | contains `"Review": {"alpha": 0.0}` |
| 5 | Day close truncates and flags the defect | see SELF-VERIFY `D1` | `8.0 1 Coordination 0.5 True False` |
| 6 | A clean day emits no `truncation_detail` and no workload/founder keys | see SELF-VERIFY `D2KEYS` | `capacity_profile_eligible,case,hours_by_category,instrument_defect,total_hours,truncations` |
| 7 | Self-report apportions and labels permanently | see SELF-VERIFY `SRP` | `3 3` |
| 8 | A self-reported `ritual` flag is rejected | see SELF-VERIFY `RITUAL` | `1` |
| 9 | An unrecognised input shape is refused, never guessed | see SELF-VERIFY `SHAPE` | `3` |
| 10 | `--query-product` sums only the named product | see SELF-VERIFY `QP` | `2.75` |
| 11 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
D="$CP_ROOT/metrics/attention/derive.py"
T="$(mktemp -d)"
cat > "$T/w1.yaml" <<'EOF'
case: V-1
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    product: alpha
    events: [2026-09-14T09:00:00Z, 2026-09-14T09:25:00Z, 2026-09-14T09:50:00Z, 2026-09-14T10:15:00Z]
EOF
cat > "$T/w2.yaml" <<'EOF'
case: V-2
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Incident
    product: alpha
    bounds: [2026-09-14T13:00:00Z, 2026-09-14T15:00:00Z]
    events: [2026-09-14T13:40:00Z, 2026-09-14T14:00:00Z, 2026-09-14T14:20:00Z]
  - category: Review
    product: alpha
    bounds: [2026-09-14T13:30:00Z, 2026-09-14T14:30:00Z]
    events: [2026-09-14T13:40:00Z, 2026-09-14T14:00:00Z, 2026-09-14T14:20:00Z]
EOF
cat > "$T/w3.yaml" <<'EOF'
case: V-3
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Review
    product: alpha
    events: [2026-09-14T14:00:00Z]
EOF
cat > "$T/w4.yaml" <<'EOF'
case: V-4
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    events:
      - {at: 2026-09-14T11:00:00Z, product: alpha}
      - {at: 2026-09-14T11:20:00Z, product: alpha}
      - {at: 2026-09-14T11:40:00Z, product: beta}
      - {at: 2026-09-14T12:00:00Z, product: gamma}
EOF
cat > "$T/d1.yaml" <<'EOF'
case: V-5
person: dev-a
date: 2026-09-15
scheduled_availability_hours: 8.0
pre_truncation_hours: {Incident: 3.00, Verification: 2.00, Review: 1.50, Engineering: 1.25, Coordination: 0.75}
EOF
cat > "$T/d2.yaml" <<'EOF'
case: V-6
person: dev-a
date: 2026-09-16
scheduled_availability_hours: 8.0
pre_truncation_hours: {Engineering: 4.00, Review: 2.00, Planning: 1.50}
EOF
cat > "$T/s1.yaml" <<'EOF'
case: V-7
week: 2026-W38
self_reports:
  - {person: dev-a, category: Coordination, hours: 4.00, product: null, provenance: self-reported}
  - {person: dev-b, category: Coordination, hours: 2.00, product: null, provenance: self-reported}
machine_activity_shares:
  dev-a: {alpha: 0.75, beta: 0.25}
  dev-b: {}
EOF
cat > "$T/s2.yaml" <<'EOF'
case: V-8
week: 2026-W38
self_reports:
  - {person: dev-a, category: Coordination, hours: 1.00, product: null, ritual: true}
EOF
printf 'case: V-9\nnothing: true\n' > "$T/bad.yaml"
NORM='import sys,json;print(json.dumps(json.load(sys.stdin),sort_keys=True))'
echo "W1=$(python3 "$D" --input "$T/w1.yaml" --json | python3 -c "$NORM")"
echo "W2=$(python3 "$D" --input "$T/w2.yaml" --json | python3 -c "$NORM")"
echo "D1=$(python3 "$D" --input "$T/d1.yaml" --json | python3 -c 'import sys,json;d=json.load(sys.stdin);t=d["truncation_detail"][0];print(d["total_hours"],d["truncations"],t["category"],t["hours_removed"],d["instrument_defect"],d["capacity_profile_eligible"])')"
echo "D2KEYS=$(python3 "$D" --input "$T/d2.yaml" --json | python3 -c 'import sys,json;print(",".join(sorted(json.load(sys.stdin))))')"
echo "SRP=$(python3 "$D" --input "$T/s1.yaml" --json | python3 -c 'import sys,json;d=json.load(sys.stdin)["apportioned"];print(len(d),sum(1 for r in d if r["provenance"]=="self-reported"))')"
python3 "$D" --input "$T/s2.yaml" --json >/dev/null 2>&1; echo "RITUAL=$?"
python3 "$D" --input "$T/bad.yaml" --json >/dev/null 2>&1; echo "SHAPE=$?"
echo "QP=$(python3 "$D" --input "$T/w1.yaml" --input "$T/w3.yaml" --input "$T/w2.yaml" --input "$T/w4.yaml" --query-product alpha --json | python3 -c 'import sys,json;print(format(json.load(sys.stdin)["hours"],".2f"))')"
rm -rf "$T"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
W1={"case": "V-1", "hours": {"Engineering": {"alpha": 1.25}}, "instrument_defect": false, "sessions": 1, "truncations": 0}
W2={"case": "V-2", "hours": {"Incident": {"alpha": 0.75}, "Review": {"alpha": 0.0}}, "instrument_defect": false, "sessions": 1, "truncations": 0}
D1=8.0 1 Coordination 0.5 True False
D2KEYS=capacity_profile_eligible,case,hours_by_category,instrument_defect,total_hours,truncations
SRP=3 3
RITUAL=1
SHAPE=3
QP=2.75
FOREIGN=0
```

`QP` is the AT-044 arithmetic in miniature: `V-1` Engineering `alpha` 1.25 + `V-3` Review `alpha` 0.25 + `V-2` Incident `alpha` 0.75 with Review at 0.00 + `V-4` Engineering `alpha` 0.50, while `V-4`'s `beta` and `gamma` quarters are filtered out. `1.25 + 0.25 + 0.75 + 0.50 = 2.75`.

**STOP rule** — if `W2` omits `"Review": {"alpha": 0.0}`, the losing category is being dropped and fixture `DC-4` of `L4-P7-T09` will fail with no way to localise it. If `D2KEYS` carries `truncation_detail`, `workload_state_eligible` or `founder_view_eligible`, the key-presence rule above is not implemented and `DC-7` fails on an extra key rather than on a wrong number. If `RITUAL` is `0`, a person has been allowed to self-report a flag §67.2 line 5592 says is *"set by the workflow or record that opens the ritual … never self-reported"* — **do not strip the flag and continue; reject the document.** If `QP` is not `2.75`, either the product filter is leaking `beta`/`gamma` or the precedence loser is being counted at more than zero. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T411 derive.py output does not match the contract L4-P7-T09 fixed"
lane: L4
phase: 4
task_id: L4-T411
blocked_by: "<loser dropped | wrong key set | ritual self-report accepted | shape guessed | query-product leaks other products>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "the eight-line expected block of L4-T411"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8969-8981; Section 67.2 line 5592; L4-07-tests-and-runbook.md tasks L4-P7-T09 and L4-P7-T12"
needs: "L0"
action_taken: "nothing beyond metrics/attention/derive.py and metrics/attention/lib/selfreport.py; no fixture under tools/records/ touched"
```

---

### L4-T412 — This phase's own proof: `metrics/attention/selfcheck/`

**Size:** L
**Depends on:** L4-T406, L4-T411

`L4-07-tests-and-runbook.md` owns `metrics/attention/test-derivation.sh` and everything under `tools/records/fixtures/attention/` (§2.1). **Creating any of those here is a duplicate authorship and a STOP.** This phase proves itself on its own unclaimed path, `metrics/attention/selfcheck/`, so that the ledger can be shown correct before the tests phase exists — §99.6 risk 2 (lines 9276–9294) is that the evidence plumbing ships unproven.

Nine cases. Each isolates one rule, and every expected value below is computed from the spec, stated here, and **asserted, never recomputed**:

| Case | Isolates | Arithmetic | Expected |
|---|---|---|---|
| `SC-1` | DR-2 at both sides of the boundary | 09:00→09:30 is a 30-minute gap (one session, span 0.5 h → 2 grains); 09:30→10:01 is 31 minutes (splits); the tail is a single event → 1 grain | sessions **2**, Engineering `alpha` **0.75** |
| `SC-2` | DR-4 never-zero | single event, span 0 → raised to 1 grain | Review `alpha` **0.25** |
| `SC-3` | DR-5 with a non-adjacent pair | span 40 min = 0.6667 h → 3 grains; Incident rank 1 beats Planning rank 6 | Incident **0.75**, Planning **0.00** |
| `SC-4` | DR-6 with an uneven split | span 40 min → 0.75 h; counts `alpha` 1, `beta` 2 of 3 | `alpha` **0.25**, `beta` **0.50** |
| `SC-5` | DR-7 with a cap below 8 h | 3.00 + 2.00 + 2.00 = 7.00 against 6.00; excess 1.00 taken from Coordination | total **6.00**, truncations **1**, defect **true** |
| `SC-6` | DR-7 clean control | 3.00 + 1.00 = 4.00 against 8.00 | truncations **0**, defect **false**, eligible **true** |
| `SC-7` | line 8980 apportionment and portfolio fallback | 3.00 × 0.5 twice; 1.00 with no share | `alpha` **1.5**, `beta` **1.5**, `portfolio` **1.0**, all labelled |
| `SC-8` | line 5592 ritual refusal | — | non-zero exit |
| `SC-9` | L4-T406 R6 | `09:00`–`17:00` on Monday 2026-09-14 | **8.0** |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
SC="$CP_ROOT/metrics/attention/selfcheck"
mkdir -p "$SC/input" "$SC/expected"

cat > "$SC/input/sc-1.yaml" <<'EOF'
case: SC-1
person: dev-c
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    product: alpha
    events: [2026-09-14T09:00:00Z, 2026-09-14T09:30:00Z, 2026-09-14T10:01:00Z]
EOF
printf '%s\n' '{"case":"SC-1","sessions":2,"hours":{"Engineering":{"alpha":0.75}},"truncations":0,"instrument_defect":false}' > "$SC/expected/sc-1.json"

cat > "$SC/input/sc-2.yaml" <<'EOF'
case: SC-2
person: dev-c
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Review
    product: alpha
    events: [2026-09-14T14:00:00Z]
EOF
printf '%s\n' '{"case":"SC-2","sessions":1,"hours":{"Review":{"alpha":0.25}},"truncations":0,"instrument_defect":false}' > "$SC/expected/sc-2.json"

cat > "$SC/input/sc-3.yaml" <<'EOF'
case: SC-3
person: dev-c
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Planning
    product: alpha
    events: [2026-09-14T10:00:00Z, 2026-09-14T10:20:00Z, 2026-09-14T10:40:00Z]
  - category: Incident
    product: alpha
    events: [2026-09-14T10:00:00Z, 2026-09-14T10:20:00Z, 2026-09-14T10:40:00Z]
EOF
printf '%s\n' '{"case":"SC-3","sessions":1,"hours":{"Incident":{"alpha":0.75},"Planning":{"alpha":0.0}},"truncations":0,"instrument_defect":false}' > "$SC/expected/sc-3.json"

cat > "$SC/input/sc-4.yaml" <<'EOF'
case: SC-4
person: dev-c
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    events:
      - {at: 2026-09-14T11:00:00Z, product: alpha}
      - {at: 2026-09-14T11:20:00Z, product: beta}
      - {at: 2026-09-14T11:40:00Z, product: beta}
EOF
printf '%s\n' '{"case":"SC-4","sessions":1,"hours":{"Engineering":{"alpha":0.25,"beta":0.5}},"truncations":0,"instrument_defect":false}' > "$SC/expected/sc-4.json"

cat > "$SC/input/sc-5.yaml" <<'EOF'
case: SC-5
person: dev-c
date: 2026-09-15
scheduled_availability_hours: 6.0
pre_truncation_hours:
  Incident: 3.00
  Operational: 2.00
  Coordination: 2.00
EOF
printf '%s\n' '{"case":"SC-5","total_hours":6.0,"hours_by_category":{"Incident":3.0,"Operational":2.0,"Coordination":1.0},"truncations":1,"truncation_detail":[{"category":"Coordination","hours_removed":1.0}],"instrument_defect":true,"capacity_profile_eligible":false,"workload_state_eligible":false,"founder_view_eligible":false}' > "$SC/expected/sc-5.json"

cat > "$SC/input/sc-6.yaml" <<'EOF'
case: SC-6
person: dev-c
date: 2026-09-16
scheduled_availability_hours: 8.0
pre_truncation_hours:
  Engineering: 3.00
  Verification: 1.00
EOF
printf '%s\n' '{"case":"SC-6","total_hours":4.0,"hours_by_category":{"Engineering":3.0,"Verification":1.0},"truncations":0,"instrument_defect":false,"capacity_profile_eligible":true}' > "$SC/expected/sc-6.json"

cat > "$SC/input/sc-7.yaml" <<'EOF'
case: SC-7
week: 2026-W38
self_reports:
  - {person: dev-c, category: Coordination, hours: 3.00, product: null, provenance: self-reported}
  - {person: dev-d, category: Coordination, hours: 1.00, product: null, provenance: self-reported}
machine_activity_shares:
  dev-c: {alpha: 0.5, beta: 0.5}
  dev-d: {}
EOF
printf '%s\n' '{"case":"SC-7","apportioned":[{"person":"dev-c","product":"alpha","category":"Coordination","hours":1.5,"provenance":"self-reported"},{"person":"dev-c","product":"beta","category":"Coordination","hours":1.5,"provenance":"self-reported"},{"person":"dev-d","product":"portfolio","category":"Coordination","hours":1.0,"provenance":"self-reported"}]}' > "$SC/expected/sc-7.json"

cat > "$SC/input/sc-8.yaml" <<'EOF'
case: SC-8
week: 2026-W38
# MUST be rejected: Section 67.2 line 5592 - the ritual flag is never self-reported.
self_reports:
  - {person: dev-c, category: Coordination, hours: 1.00, product: null, ritual: true}
EOF

cat > "$SC/input/sc-9-people.yaml" <<'EOF'
registry_version: 1
people:
  - id: dev-c
    work_arrangement:
      timezone: Asia/Kolkata
      schedule:
        mon: { start: "09:00", end: "17:00" }
      fte: 1.0
      public_holiday_set: IN
EOF
printf 'calendar_version: 1\npublic_holiday_sets:\n  IN: [2026-01-26]\n' > "$SC/input/sc-9-calendar.yaml"
printf 'person: dev-c\ndates: []\n' > "$SC/input/sc-9-absence.yaml"

cat > "$SC/run.sh" <<'RUN_EOF'
#!/usr/bin/env bash
# metrics/attention/selfcheck/run.sh
# Phase-4's own proof of the attention ledger. MasterSpec v4.0 Section 97.4 lines 8969-8981;
# Section 67.2 line 5592; Section 7.3 line 571.
# This is NOT tools/records/test/ and NOT metrics/attention/test-derivation.sh: those belong to
# L4-07-tests-and-runbook.md (tasks L4-P7-T09, L4-P7-T10) and are never created here.
# Expected values are fixed by L4-04-attention-ledger.md task L4-T412. Never edit one to make a
# run pass: a mismatch is a defect in derive.py, not in the fixture.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
PASS=0; FAIL=0
NORM='import sys,json;print(json.dumps(json.load(sys.stdin),sort_keys=True,separators=(",",":")))'
FNORM='import sys,json;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True,separators=(",",":")))'

check() {  # check <id> <want> <got>
  if [ "$2" = "$3" ]; then echo "PASS $1"; PASS=$((PASS+1));
  else echo "FAIL $1"; echo "  want: $2"; echo "  got : $3"; FAIL=$((FAIL+1)); fi
}

for c in 1 2 3 4 5 6 7; do
  got="$(python3 "$ATT/derive.py" --input "$HERE/input/sc-$c.yaml" --json 2>/dev/null \
         | python3 -c "$NORM" 2>/dev/null)"
  want="$(python3 -c "$FNORM" "$HERE/expected/sc-$c.json")"
  check "SC-$c" "$want" "$got"
done

if python3 "$ATT/derive.py" --input "$HERE/input/sc-8.yaml" --json >/dev/null 2>&1; then
  echo "FAIL SC-8 (a self-reported ritual flag was accepted)"; FAIL=$((FAIL+1))
else
  echo "PASS SC-8"; PASS=$((PASS+1))
fi

got9="$(python3 "$ATT/scheduled-availability.py" --person dev-c --date 2026-09-14 \
        --people "$HERE/input/sc-9-people.yaml" --calendar "$HERE/input/sc-9-calendar.yaml" \
        --absence "$HERE/input/sc-9-absence.yaml" 2>&1 | tail -1)"
check "SC-9" "SCHEDAVAIL OK dev-c 2026-09-14 8.0" "$got9"

if [ "$FAIL" -eq 0 ]; then echo "ATTNSELF OK $PASS/9"; exit 0; fi
echo "ATTNSELF FAIL $FAIL of 9"; exit 1
RUN_EOF
chmod +x "$SC/run.sh"
sh "$SC/run.sh"
git -C "$CP_ROOT" add metrics/attention/selfcheck
git -C "$CP_ROOT" commit -m "L4-T412: phase-4 self-check, nine cases on an unclaimed path (97.4, 67.2, 7.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Eleven inputs, seven expected documents | `ls "$CP_ROOT"/metrics/attention/selfcheck/input/sc-*.yaml \| wc -l; ls "$CP_ROOT"/metrics/attention/selfcheck/expected/*.json \| wc -l` | `11` then `7` |
| 2 | All nine cases pass | `sh "$CP_ROOT/metrics/attention/selfcheck/run.sh" \| tail -1` | `ATTNSELF OK 9/9` |
| 3 | Every case reports individually | `sh "$CP_ROOT/metrics/attention/selfcheck/run.sh" \| grep -c '^PASS SC-'` | `9` |
| 4 | The suite can fail — seeded canary | see SELF-VERIFY `CANARY` | `1` |
| 5 | No file owned by `L4-07-tests-and-runbook.md` was created | see SELF-VERIFY `NOFOREIGNFILE` | `0` |
| 6 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
SC="$CP_ROOT/metrics/attention/selfcheck"
echo "INPUTS=$(ls "$SC"/input/sc-*.yaml | wc -l | tr -d ' ')"
echo "EXPECTED=$(ls "$SC"/expected/*.json | wc -l | tr -d ' ')"
echo "MAIN=$(sh "$SC/run.sh" | tail -1)"
echo "PASSES=$(sh "$SC/run.sh" | grep -c '^PASS SC-')"
cp "$SC/expected/sc-1.json" "$SC/expected/sc-1.json.bak"
printf '%s\n' '{"case":"SC-1","sessions":1,"hours":{"Engineering":{"alpha":9.99}},"truncations":0,"instrument_defect":false}' > "$SC/expected/sc-1.json"
sh "$SC/run.sh" >/dev/null 2>&1; echo "CANARY=$?"
mv "$SC/expected/sc-1.json.bak" "$SC/expected/sc-1.json"
echo "RESTORED=$(sh "$SC/run.sh" | tail -1)"
echo "NOFOREIGNFILE=$(ls "$CP_ROOT/metrics/attention/test-derivation.sh" "$CP_ROOT/tools/records/fixtures/attention" 2>/dev/null | wc -l | tr -d ' ')"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
INPUTS=11
EXPECTED=7
MAIN=ATTNSELF OK 9/9
PASSES=9
CANARY=1
RESTORED=ATTNSELF OK 9/9
NOFOREIGNFILE=0
FOREIGN=0
```

**STOP rule** — if `CANARY` is not `1`, the suite passes against a fixture asserting 9.99 hours for a 1.25-hour session and is decoration, not a check (charter §12 rule 10). If `NOFOREIGNFILE` is not `0`, a file belonging to `L4-07-tests-and-runbook.md` has been created here — delete it, do not keep it, and do not "merge" the two suites. If a case fails, **edit `derive.py`, never the expected document**: the expected values are computed from §97.4 in the table above and a mismatch localises a derivation defect. If `SC-4` fails only in the `alpha`/`beta` proportion, re-read **D-L4-P7-03** — a fixture that distinguishes the two rounding orders must not exist (§5). Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T412 phase-4 self-check fails, or cannot fail"
lane: L4
phase: 4
task_id: L4-T412
blocked_by: "<case mismatch | canary passed | a file owned by L4-07 was created here>"
observed: "<paste the exact SELF-VERIFY output and every FAIL SC- block>"
expected: "INPUTS=11 / EXPECTED=7 / MAIN=ATTNSELF OK 9/9 / PASSES=9 / CANARY=1 / RESTORED=ATTNSELF OK 9/9 / NOFOREIGNFILE=0 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8969-8981; Section 67.2 line 5592; Section 99.6 risk 2 lines 9276-9294; L4-00-charter.md section 12 rule 10"
needs: "L0"
action_taken: "no expected document edited; nothing created under tools/records/ or metrics/attention/test-derivation.sh"
```

---

### L4-T413 — `HANDOFF-P.md`: what this phase emits for the lane that does not exist

**Size:** M
**Depends on:** L4-T411

§97.4 line 8976 names three surfaces an instrument-defect day never enters, and §97.4 line 8975 caps against the Capacity Profile. All three surfaces — Capacity Profile, workload state (§83), Founder view (§93) — are §99.2 subsystem **P** (line 9203), which **PARTITION v1 assigns to no lane**. That is the known partition gap already escalated by other authors alongside G, H, J and O; this task does **not** re-litigate it and does **not** claim P. It writes one document naming exactly what L4 emits, so that whoever receives P inherits a contract rather than a guess.

**This is a document, not a Capacity Profile.** L4 writes no file under any path subsystem P would own.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/HANDOFF-P.md" <<'HAND_EOF'
# What the attention ledger emits for subsystem P

Written by lane L4, phase 4 (`implementation/lanes/L4-04-attention-ledger.md`, task L4-T413).
Authority: MasterSpec v4.0 Section 97.4 lines 8975-8976; Section 69.2 line 5720; Section 83.1
line 7280; Section 93; Section 99.2 line 9203.

## The boundary

Subsystem P — people intelligence: capacity profiles, utilisation composition, bandwidth states,
overload and under-utilisation detection, staffing diagnosis (Section 99.2, line 9203) — is
assigned to no lane in PARTITION v1. L4 does not claim it and builds none of it. L4 owns the
ledger; P owns every surface the ledger feeds. See L4-04-attention-ledger.md section 5,
DECISION REQUIRED D-L4-P4-04, routed to L0.

## What L4 emits, and where it comes from

| Emitted field | Emitted by | Meaning | Spec |
| --- | --- | --- | --- |
| `hours` / `hours_by_category` | metrics/attention/derive.py | Derived attention hours in the eight-category taxonomy, one category per hour | 67.1 line 5573; 67.2 line 5579 |
| `total_hours` | metrics/attention/derive.py | The person-day total AFTER the daily reconciliation | 97.4 line 8975 |
| `truncations`, `truncation_detail` | metrics/attention/derive.py | Every truncation the reconciliation applied, category and hours removed. "each truncation is recorded" | 97.4 line 8975 |
| `instrument_defect` | metrics/attention/derive.py | The day exceeded scheduled availability BEFORE truncation | 97.4 line 8976 |
| `capacity_profile_eligible` | metrics/attention/derive.py | false on a defect day | 97.4 line 8976 |
| `workload_state_eligible` | metrics/attention/derive.py | false on a defect day; the Section 83 consumer | 97.4 line 8976; 83.1 line 7280 |
| `founder_view_eligible` | metrics/attention/derive.py | false on a defect day; the Section 93 consumer | 97.4 line 8976 |
| `provenance: self-reported` | metrics/attention/derive.py | Carried permanently on any figure including self-reported hours | 97.4 line 8980 |
| `scheduled_availability_hours` | metrics/attention/scheduled-availability.py | The declared cap, from work_arrangement | 69.2 line 5720; 7.3 |

## Four obligations P inherits, each already stated in the spec

1. **Honour the three eligibility flags.** A day with `instrument_defect: true` never enters a
   Capacity Profile, a workload state or the Founder view (line 8976). It is an instrument
   finding, never a workload finding about a person.
2. **Carry the self-reported label wherever the figure renders, permanently** (line 8980).
   Coordination is never presented beside genuinely derived categories without it.
3. **Never render attention hours as individual performance evidence**, and never as a per-person
   drill-down on a general surface. Aggregate at product and portfolio level only
   (Section 67.3 line 5605; Section 91.2 lines 8083-8092).
4. **Declare the eight metric attributes** for anything built on these fields: definition, source,
   time window, baseline, expected interpretation, known limitations, owner, action on breach
   (Section 84.6 line 7471). The ledger's own declared limitation is Section 97.4 line 8978: it is
   a LOWER BOUND on attention, and Architecture and Coordination are systematically under-counted.

## What L4 does NOT emit, and will not

A Capacity Profile; a workload state; a bandwidth state; a Founder view; a utilisation
composition; a staffing diagnosis; any per-person surface. The drift finding a defect day raises
(line 8976) is also not L4's: `validators/drift/**` belongs to L3 (PARTITION.md line 19). L4
emits the flag; L3 raises the finding; P renders nothing until it has an owner.
HAND_EOF
git -C "$CP_ROOT" add metrics/attention/HANDOFF-P.md
git -C "$CP_ROOT" commit -m "L4-T413: subsystem-P handoff - what the ledger emits, and what L4 does not build"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The document exists | `test -f "$CP_ROOT/metrics/attention/HANDOFF-P.md" && echo YES` | `YES` |
| 2 | All nine emitted fields are named | see SELF-VERIFY `FIELDS` | `9` |
| 3 | The three eligibility flags each appear | see SELF-VERIFY `FLAGS` | `3` |
| 4 | It states the partition gap without claiming P | see SELF-VERIFY `NOCLAIM` | `1 1` |
| 5 | No file was created outside `metrics/attention/` | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
H="$CP_ROOT/metrics/attention/HANDOFF-P.md"
echo "EXISTS=$(test -f "$H" && echo yes || echo no)"
echo "FIELDS=$(grep -c '^| \`' "$H")"
echo "FLAGS=$(grep -o 'capacity_profile_eligible\|workload_state_eligible\|founder_view_eligible' "$H" | sort -u | wc -l | tr -d ' ')"
echo "NOCLAIM=$(grep -c 'L4 does not claim it' "$H") $(grep -c 'D-L4-P4-04' "$H")"
echo "PPATHS=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -c 'capacity\|workload\|founder-view')"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
EXISTS=yes
FIELDS=9
FLAGS=3
NOCLAIM=1 1
PPATHS=0
FOREIGN=0
```

**STOP rule** — if `PPATHS` is not `0`, a path a subsystem-P owner would own has been created in this lane. Delete it. PARTITION.md rule 1 is *"One owner per path… No exceptions"*, and a lane that claims an unassigned subsystem makes the gap harder to close, not easier. Do **not** build a Capacity Profile "just to test the flags" — the flags are tested by `SC-5` and `SC-6` in L4-T412. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T413 subsystem-P surface created inside lane L4"
lane: L4
phase: 4
task_id: L4-T413
blocked_by: "<capacity profile built | workload state built | founder view built | path outside metrics/attention created>"
observed: "<paste the exact SELF-VERIFY output and git diff --name-only>"
expected: "EXISTS=yes / FIELDS=9 / FLAGS=3 / NOCLAIM=1 1 / PPATHS=0 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8975, 8976; Section 99.2 line 9203; PARTITION.md rule 1 and line 19"
needs: "L0"
action_taken: "nothing beyond metrics/attention/HANDOFF-P.md; subsystem P not claimed"
```

---

### L4-T414 — Every metric names its store, or it does not ship

**Size:** L
**Depends on:** L4-T411, L4-T412

§97.1 line 8838, binding: *"Metrics derive from these stores, never from hand-maintained numbers, and every dashboard metric names the record store it derives from. **A metric that cannot name its store does not ship.**"* Invariant 46 (§101.7, line 9514) says the same at the invariant level. This task is the mechanical form of the shipping test, applied to every figure this phase emits.

**Scope, so no second register is created.** This file declares the **ledger's own outputs** — the eleven figures `derive.py`, `scheduled-availability.py` and the Ready-queue-miss detector emit. It is **not** `metrics/register/metric-declarations.yaml`, which belongs to the metric-register phase (§2.1) and holds the §103 success measures. The validator proves the two do not overlap, because §84.6 line 7472 says the register is the carrier and *"the table is a view of it, never a second copy."*

**Every metric id is derived mechanically from an emitted field.** Each row declares exactly one of three provenances, and the validator proves it resolves:

| Provenance | Resolves against | Why |
|---|---|---|
| `output_key` | a key emitted by `derive.py` or `scheduled-availability.py` | the figure exists |
| `taxonomy_flag` | a flag in `metrics/attention/taxonomy.yaml` | §67.2 line 5592 — flags, never a ninth category |
| `event_type` | an identifier in `metrics/taxonomy/event-types.yaml` | §97.3 line 8947 — identifiers are Phase 2's, looked up and never declared here |

**Every row carries the eight §84.6 attributes (line 7471)** — definition, source, time window, baseline, expected interpretation, known limitations, owner, action on breach. `known_limitations` is never empty (§84.6 line 7473). `baseline` is a recorded value **or** the literal `unbaselined` (§103.14 line 9975; D77, line 10160: *"an empty metric store renders as unbaselined, never as a miss"*), which is the half of AT-046 (line 9368) this file satisfies.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/attention/derived-metrics.yaml" <<'DM_EOF'
# metrics/attention/derived-metrics.yaml
# Every figure the attention ledger emits, each naming the record store it derives from.
# MasterSpec v4.0 Section 97.1 line 8838: "every dashboard metric names the record store it
# derives from. A metric that cannot name its store does not ship." Invariant 46, line 9514.
# The eight required attributes are Section 84.6 line 7471; there is no shorter list.
# THIS IS NOT metrics/register/metric-declarations.yaml. That file holds the Section 103 success
# measures and belongs to another phase (L4-04-attention-ledger.md section 2.1). No id here
# appears there; validate-store-naming.sh check S5 proves it.
register_version: 1
scope: ledger_outputs
not_the_metric_register: metrics/register/metric-declarations.yaml

metrics:

  attention_hours_by_category:
    definition: "Derived attention hours for a person-day, in the eight-category taxonomy, one category per hour."
    source: {output_key: hours_by_category}
    record_stores: ["events/", "records/incidents/", "records/uat/", "records/deployments/"]
    time_window: per_person_per_day
    baseline: unbaselined
    expected_interpretation: "A lower bound. Rising is not by itself good or bad; read against capacity."
    known_limitations: "Section 97.4 line 8978: thinking that leaves no event leaves no trace, so Architecture and Coordination are systematically under-counted."
    owner: team-lead
    action_on_breach: "Raise the adverse trend at the quarterly operating-system review; a recorded decision follows (Section 103.13 line 9971)."
    spec_lines: [8956, 8969, 8978, 5579]

  attention_hours_by_product:
    definition: "Derived attention hours attributed to one product, or to the portfolio where a session touches none."
    source: {output_key: hours}
    record_stores: ["events/", "records/demos/", "records/decisions/"]
    time_window: per_person_per_day
    baseline: unbaselined
    expected_interpretation: "Read at product and portfolio level only; never as a per-person drill-down."
    known_limitations: "A session touching several products splits by event count, which weights a burst of small events equally with a long one (Section 97.4 line 8974)."
    owner: team-lead
    action_on_breach: "Raise at the quarterly operating-system review; a recorded decision follows."
    spec_lines: [8974, 5605, 8087]

  attention_sessions_per_person_per_day:
    definition: "The count of activity sessions that survived precedence resolution for a person-day."
    source: {output_key: sessions}
    record_stores: ["events/"]
    time_window: per_person_per_day
    baseline: unbaselined
    expected_interpretation: "A diagnostic of the instrument, not of the person. A sudden change indicates an ingest change."
    known_limitations: "Sessions never span windows, so one continuous stretch of work observed through two windows counts twice here and once in hours."
    owner: team-lead
    action_on_breach: "Raise at the quarterly operating-system review; a recorded decision follows."
    spec_lines: [8969]

  attention_truncations_per_person_per_day:
    definition: "The number of daily-reconciliation truncations applied, with the category and hours removed."
    source: {output_key: truncation_detail}
    record_stores: ["events/", "records/leave/"]
    time_window: per_person_per_day
    baseline: unbaselined
    expected_interpretation: "Trending to zero. A persistent non-zero value is an instrument finding, never a workload finding."
    known_limitations: "Truncation runs in reverse precedence order, so Coordination absorbs the whole error first and is the category most distorted by an instrument fault."
    owner: team-lead
    action_on_breach: "Raise at the quarterly operating-system review; a recorded decision follows."
    spec_lines: [8975]

  attention_instrument_defect_days:
    definition: "Person-days whose derived hours exceeded scheduled availability BEFORE truncation."
    source: {output_key: instrument_defect}
    record_stores: ["events/", "records/leave/"]
    time_window: per_person_per_day
    baseline: unbaselined
    expected_interpretation: "Zero is the good value. A defect day is an instrument defect, not a workload finding."
    known_limitations: "Detects only over-counting. A ledger that under-counts leaves no defect day, and Section 97.4 line 8978 says under-counting is the expected direction."
    owner: team-lead
    action_on_breach: "Raises a drift finding against the ledger (Section 97.4 line 8976). validators/drift/** is L3; L4 emits the flag only."
    spec_lines: [8976, 9203]

  scheduled_availability_hours_per_person_per_day:
    definition: "The declared cap: the person's scheduled availability for that day, from work_arrangement."
    source: {output_key: scheduled_availability_hours}
    record_stores: ["records/leave/"]
    time_window: per_person_per_day
    baseline: declared
    expected_interpretation: "A declaration, never a measurement. It is what the person is scheduled for, not what they worked."
    known_limitations: "Section 7.3 line 629: fte is a capacity multiplier. Whether it multiplies the declared span is open as D-L4-P4-01; the declared default is that it does not."
    owner: team-lead
    action_on_breach: "A person with no work_arrangement fails closed (rule R2); the registry gap is a drift finding, not a default number."
    spec_lines: [8975, 5720, 629]

  attention_self_reported_hours:
    definition: "Weekly banded self-report hours, apportioned across products by machine-derived activity share."
    source: {output_key: apportioned}
    record_stores: ["events/"]
    time_window: per_person_per_week
    baseline: unbaselined
    expected_interpretation: "Carries the self-reported provenance label wherever it renders, permanently."
    known_limitations: "Section 97.4 line 8980: bands, not minutes; never per-product at collection; apportionment inherits every error in the machine-derived share it is apportioned by."
    owner: team-lead
    action_on_breach: "A collection design costing more than five minutes per person per week is simplified, never enforced (Section 67.3 line 5603)."
    spec_lines: [8980, 5601, 5603, 9975]

  attention_ritual_hours:
    definition: "Attention hours on entries carrying the ritual flag, for the Section 57.2 budgeted-versus-measured line."
    source: {taxonomy_flag: ritual}
    record_stores: ["events/"]
    time_window: per_month
    baseline: unbaselined
    expected_interpretation: "Flat or down, and below the declared Founder operating-load ceiling (line 9967)."
    known_limitations: "Set by the workflow or record that opens the ritual and never self-reported; a ritual whose opening workflow does not set the flag is invisible here."
    owner: team-lead
    action_on_breach: "Owner is the Team Lead, not the Founder, because a party does not own the instrument that measures it (line 9967)."
    spec_lines: [5592, 8956, 9967]

  attention_unplanned_share:
    definition: "The share of attention hours on entries carrying the unplanned flag - work that entered H1 without H2 preparation."
    source: {taxonomy_flag: unplanned}
    record_stores: ["events/", "records/incidents/"]
    time_window: per_month
    baseline: unbaselined
    expected_interpretation: "Computed from the flag, never from a ninth category. An unplanned incident hour is still an Incident hour."
    known_limitations: "The flag is set at the horizon transition; work reclassified after the fact is not retro-flagged."
    owner: team-lead
    action_on_breach: "Raise at the quarterly operating-system review; a recorded decision follows."
    spec_lines: [5592, 7290]

  ready_queue_miss_count:
    definition: "Ready-queue-miss events, the SIG-06 count: pickup without Ready, and completion with an empty Ready queue."
    source: {event_type: ready_queue_miss_recorded}
    record_stores: ["events/"]
    time_window: rolling_30_days
    baseline: unbaselined
    expected_interpretation: "Trending to zero (invariant 15, line 9471). A Team Lead capacity signal, never an individual performance signal."
    known_limitations: "Section 29.4 line 2670: the cause fields are supplied by the cause prompt and never inferred, so an unanswered prompt leaves the count without its meaning."
    owner: team-lead
    action_on_breach: "Amber, routed to the Team Lead (SIG-06, line 4535)."
    spec_lines: [4535, 2670, 8984, 8986, 9471]

  ready_bypass_findings:
    definition: "Backlog-to-Planned or Backlog-to-In-Progress transitions made while suitable Ready items exist."
    source: {event_type: ready_queue_miss_recorded}
    record_stores: ["events/"]
    time_window: rolling_30_days
    baseline: unbaselined
    expected_interpretation: "A board-hygiene finding for the Team Lead. It NEVER enters the SIG-06 count."
    known_limitations: "Shares one event type with the SIG-06 count and is separated only by the reason field; a consumer that ignores the reason double-counts."
    owner: team-lead
    action_on_breach: "Board-hygiene finding for the Team Lead (Section 97.5 line 8986)."
    spec_lines: [8986, 4535]
DM_EOF
cat > "$CP_ROOT/metrics/attention/validate-store-naming.sh" <<'VSN_EOF'
#!/usr/bin/env bash
# metrics/attention/validate-store-naming.sh
# The shipping test of Section 97.1 line 8838: "A metric that cannot name its store does not ship."
# Output contract: one final line. STORENAME OK <counters> exit 0 / STORENAME FAIL <reasons> exit 1
# / STORENAME ERROR <reason> exit 3 (could not execute - never a pass).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
[ -f "$HERE/derived-metrics.yaml" ] || { echo "STORENAME ERROR missing-derived-metrics"; exit 3; }
[ -f "$HERE/taxonomy.yaml" ]        || { echo "STORENAME ERROR missing-taxonomy"; exit 3; }
[ -f "$HERE/derive.py" ]            || { echo "STORENAME ERROR missing-derive"; exit 3; }

if [ "${1:-}" = "--selftest" ]; then
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  mkdir -p "$T/metrics/attention" "$T/metrics/taxonomy"
  cp "$HERE"/derived-metrics.yaml "$HERE"/taxonomy.yaml "$HERE"/derive.py \
     "$HERE"/scheduled-availability.py "$HERE"/validate-store-naming.sh "$T/metrics/attention/"
  cp "$CP/metrics/taxonomy/event-types.yaml" "$T/metrics/taxonomy/"
  python3 - "$T/metrics/attention/derived-metrics.yaml" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
# Seeded canary: one metric loses the store it must name (Section 97.1 line 8838).
doc["metrics"]["attention_hours_by_category"]["record_stores"] = []
yaml.safe_dump(doc, open(sys.argv[1], "w", encoding="utf-8"), sort_keys=False)
PY
  if sh "$T/metrics/attention/validate-store-naming.sh" >/dev/null 2>&1; then
    echo "STORENAME FAIL selftest-storeless-accepted"; exit 1
  fi
  echo "STORENAME OK selftest 1/1"; exit 0
fi

python3 - "$HERE" "$CP" <<'PY' || exit $?
import os, sys, yaml
here, cp = sys.argv[1], sys.argv[2]
doc = yaml.safe_load(open(os.path.join(here, "derived-metrics.yaml"), encoding="utf-8"))
tax = yaml.safe_load(open(os.path.join(here, "taxonomy.yaml"), encoding="utf-8"))
metrics = doc.get("metrics") or {}
fails = []

# The two executables and the Phase-2 event register are matched by TEXT, never parsed:
# their shapes belong to other tasks and this check must not couple to them.
blob = ""
for name in ("derive.py", "scheduled-availability.py"):
    path = os.path.join(here, name)
    if os.path.exists(path):
        blob += open(path, encoding="utf-8").read()
evt_path = os.path.join(cp, "metrics", "taxonomy", "event-types.yaml")
evt = open(evt_path, encoding="utf-8").read() if os.path.exists(evt_path) else ""
flags = {f["name"] for f in (tax.get("flags") or [])}

REQUIRED = ["definition", "source", "time_window", "baseline",
            "expected_interpretation", "known_limitations", "owner", "action_on_breach"]

stored = 0
for mid, row in metrics.items():
    # S1 Section 84.6 line 7471 - the eight attributes, none empty.
    for attr in REQUIRED:
        if not row.get(attr):
            fails.append("missing-attribute:%s.%s" % (mid, attr))
    # S2 Section 97.1 line 8838 - name the store, or do not ship.
    if not row.get("record_stores"):
        fails.append("storeless:%s" % mid)
    else:
        stored += 1
    # S3 Section 84.6 line 7473 - known_limitations is never empty.
    if str(row.get("known_limitations", "")).strip() in ("", "none"):
        fails.append("empty-limitations:%s" % mid)
    # S4 Section 103.14 line 9975 / D77 line 10160 - a value, or the explicit marker.
    if row.get("baseline") in (None, ""):
        fails.append("no-baseline-and-no-marker:%s" % mid)
    # S6 the figure must actually be emitted.
    src = row.get("source") or {}
    if len(src) != 1:
        fails.append("source-not-exactly-one-provenance:%s" % mid)
    elif "output_key" in src:
        if ('"%s"' % src["output_key"]) not in blob:
            fails.append("output-key-not-emitted:%s:%s" % (mid, src["output_key"]))
    elif "taxonomy_flag" in src:
        if src["taxonomy_flag"] not in flags:
            fails.append("flag-not-in-taxonomy:%s:%s" % (mid, src["taxonomy_flag"]))
    elif "event_type" in src:
        if src["event_type"] not in evt:
            fails.append("event-type-not-in-register:%s:%s" % (mid, src["event_type"]))
    else:
        fails.append("unknown-provenance:%s" % mid)

# S5 - one register per thing. No id here may also live in the Section 103 register.
reg = os.path.join(cp, "metrics", "register", "metric-declarations.yaml")
if os.path.exists(reg):
    other = yaml.safe_load(open(reg, encoding="utf-8")) or {}
    for mid in metrics:
        if mid in other:
            fails.append("duplicate-of-metric-register:%s" % mid)

if not metrics:
    print("STORENAME FAIL empty-register"); sys.exit(1)
if fails:
    print("STORENAME FAIL %s" % ",".join(fails)); sys.exit(1)
print("STORENAME OK metrics=%d stored=%d checks=6" % (len(metrics), stored))
PY
VSN_EOF
chmod +x "$CP_ROOT/metrics/attention/validate-store-naming.sh"
"$CP_ROOT/metrics/attention/validate-store-naming.sh"
"$CP_ROOT/metrics/attention/validate-store-naming.sh" --selftest
git -C "$CP_ROOT" add metrics/attention/derived-metrics.yaml metrics/attention/validate-store-naming.sh
git -C "$CP_ROOT" commit -m "L4-T414: every ledger metric names its record store, with the shipping test (97.1 line 8838)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The register parses | `python3 -c "import yaml;yaml.safe_load(open(r'$CP_ROOT/metrics/attention/derived-metrics.yaml'))"; echo $?` | `0` |
| 2 | Eleven metrics, every one naming a store | `"$CP_ROOT/metrics/attention/validate-store-naming.sh" \| tail -1` | `STORENAME OK metrics=11 stored=11 checks=6` |
| 3 | It exits `0` on a pass | `"$CP_ROOT/metrics/attention/validate-store-naming.sh" >/dev/null; echo $?` | `0` |
| 4 | It rejects a metric whose store is removed | `"$CP_ROOT/metrics/attention/validate-store-naming.sh" --selftest \| tail -1` | `STORENAME OK selftest 1/1` |
| 5 | It fails closed when it cannot reach its input | see SELF-VERIFY `MISSING` | `3` |
| 6 | Every metric carries all eight §84.6 attributes | see SELF-VERIFY `ATTRS` | `11` |
| 7 | Every baseline is a value or the explicit marker | see SELF-VERIFY `BASELINE` | `11` |
| 8 | Only `metrics/attention/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^metrics/attention/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
V="$CP_ROOT/metrics/attention/validate-store-naming.sh"
echo "MAIN=$("$V" | tail -1)"
echo "RC=$("$V" >/dev/null 2>&1; echo $?)"
echo "CANARY=$("$V" --selftest | tail -1)"
T="$(mktemp -d)"; cp "$V" "$T/validate-store-naming.sh"
sh "$T/validate-store-naming.sh" >/dev/null 2>&1; echo "MISSING=$?"
rm -rf "$T"
python3 - <<'PY'
import os, yaml
p = os.path.join(os.environ["CP_ROOT"], "metrics", "attention", "derived-metrics.yaml")
m = yaml.safe_load(open(p, encoding="utf-8"))["metrics"]
need = ["definition", "source", "time_window", "baseline", "expected_interpretation",
        "known_limitations", "owner", "action_on_breach"]
print("COUNT=%d" % len(m))
print("ATTRS=%d" % sum(1 for r in m.values() if all(r.get(a) for a in need)))
print("STORES=%d" % sum(1 for r in m.values() if r.get("record_stores")))
print("BASELINE=%d" % sum(1 for r in m.values() if r.get("baseline") not in (None, "")))
PY
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
MAIN=STORENAME OK metrics=11 stored=11 checks=6
RC=0
CANARY=STORENAME OK selftest 1/1
MISSING=3
COUNT=11
ATTRS=11
STORES=11
BASELINE=11
FOREIGN=0
```

**STOP rule** — if `STORES` is not `11`, a metric in this phase cannot name its store and §97.1 line 8838 forbids shipping it. **Do not invent a store to clear the count** and do not delete the metric to make the number match: a figure `derive.py` emits with no nameable store is a spec question for L0, not an edit. If `CANARY` is not `STORENAME OK selftest 1/1`, the shipping test accepts a storeless metric and is decoration, not a check (charter §12 rule 10). If a `duplicate-of-metric-register` failure appears, the metric-register phase has declared the same id — **do not rename either side**; two registers for one metric is exactly what §84.6 line 7472 forbids, and which register owns the id is L0's call. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T414 a ledger metric cannot name its store, or the shipping test cannot fail"
lane: L4
phase: 4
task_id: L4-T414
blocked_by: "<storeless metric | missing 84.6 attribute | no baseline and no unbaselined marker | canary accepted | id duplicated in metrics/register>"
observed: "<paste the exact SELF-VERIFY output and every STORENAME FAIL token>"
expected: "MAIN=STORENAME OK metrics=11 stored=11 checks=6 / RC=0 / CANARY=STORENAME OK selftest 1/1 / MISSING=3 / COUNT=11 / ATTRS=11 / STORES=11 / BASELINE=11"
spec_ref: "Master Spec v4.0 Section 97.1 line 8838; Section 84.6 lines 7471, 7472, 7473; Section 103.14 line 9975; D77 line 10160; invariant 46 line 9514; AT-046 line 9368"
needs: "L0"
action_taken: "nothing beyond metrics/attention/derived-metrics.yaml and metrics/attention/validate-store-naming.sh; metrics/register/** untouched"
```

---

### L4-T415 — Attention-ledger gate: every check in order, and the phase checkpoint

**Size:** M
**Depends on:** L4-T405, L4-T412, L4-T414

**This task creates no file.** It runs the three checks this phase has built, in order, proves the ledger end-to-end, and marks the checkpoint at which the phase stops writing `metrics/attention/` and starts writing `tools/records/`. Everything it runs already exists; if any of it does not, an earlier task did not complete and this task stops.

The gate, in order — a failure at any step stops the phase:

| # | Check | Command | Required last line |
|---|---|---|---|
| G1 | Config agreement | `metrics/attention/validate-attention-config.sh` | `ATTNCFG OK checks=8 categories=8 sources=8` |
| G2 | Config check can fail | `… --selftest` | `ATTNCFG OK selftest 1/1` |
| G3 | Derivation | `metrics/attention/selfcheck/run.sh` | `ATTNSELF OK 9/9` |
| G4 | Store naming | `metrics/attention/validate-store-naming.sh` | `STORENAME OK metrics=11 stored=11 checks=6` |
| G5 | Store-naming check can fail | `… --selftest` | `STORENAME OK selftest 1/1` |
| G6 | Every module compiles | `python3 -m py_compile` over all `.py` | exit `0` |

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
A="$CP_ROOT/metrics/attention"
"$A/validate-attention-config.sh"
"$A/validate-attention-config.sh" --selftest
sh "$A/selfcheck/run.sh"
"$A/validate-store-naming.sh"
"$A/validate-store-naming.sh" --selftest
python3 -m py_compile "$A"/derive.py "$A"/scheduled-availability.py \
                      "$A"/lib/config.py "$A"/lib/sessions.py "$A"/lib/precedence.py \
                      "$A"/lib/attribute.py "$A"/lib/reconcile.py "$A"/lib/selfreport.py
find "$CP_ROOT" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null
git -C "$CP_ROOT" status --porcelain
git -C "$CP_ROOT" tag -a l4-phase4-ledger-complete -m "L4-T415: attention ledger gate green; metrics/attention complete"
git -C "$CP_ROOT" tag --list 'l4-phase4-*'
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | G1 passes | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" \| tail -1` | `ATTNCFG OK checks=8 categories=8 sources=8` |
| 2 | G2 passes | `"$CP_ROOT/metrics/attention/validate-attention-config.sh" --selftest \| tail -1` | `ATTNCFG OK selftest 1/1` |
| 3 | G3 passes | `sh "$CP_ROOT/metrics/attention/selfcheck/run.sh" \| tail -1` | `ATTNSELF OK 9/9` |
| 4 | G4 passes | `"$CP_ROOT/metrics/attention/validate-store-naming.sh" \| tail -1` | `STORENAME OK metrics=11 stored=11 checks=6` |
| 5 | G5 passes | `"$CP_ROOT/metrics/attention/validate-store-naming.sh" --selftest \| tail -1` | `STORENAME OK selftest 1/1` |
| 6 | G6 passes | see SELF-VERIFY `COMPILE` | `0` |
| 7 | No `__pycache__` was committed | `git -C "$CP_ROOT" ls-files \| grep -c '__pycache__'` | `0` |
| 8 | The working tree is clean | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 9 | The checkpoint tag exists | `git -C "$CP_ROOT" tag --list 'l4-phase4-ledger-complete' \| wc -l` | `1` |
| 10 | `metrics/attention/` holds exactly fifteen files outside `selfcheck/` | `git -C "$CP_ROOT" ls-files 'metrics/attention/*' \| grep -vc '^metrics/attention/selfcheck/'` | `15` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
A="$CP_ROOT/metrics/attention"
echo "G1=$("$A/validate-attention-config.sh" | tail -1)"
echo "G2=$("$A/validate-attention-config.sh" --selftest | tail -1)"
echo "G3=$(sh "$A/selfcheck/run.sh" | tail -1)"
echo "G4=$("$A/validate-store-naming.sh" | tail -1)"
echo "G5=$("$A/validate-store-naming.sh" --selftest | tail -1)"
python3 -m py_compile "$A"/derive.py "$A"/scheduled-availability.py "$A"/lib/*.py; echo "COMPILE=$?"
find "$CP_ROOT" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null
echo "PYCACHE=$(git -C "$CP_ROOT" ls-files | grep -c '__pycache__')"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l | tr -d ' ')"
echo "TAG=$(git -C "$CP_ROOT" tag --list 'l4-phase4-ledger-complete' | wc -l | tr -d ' ')"
echo "FILES=$(git -C "$CP_ROOT" ls-files 'metrics/attention/*' | grep -vc '^metrics/attention/selfcheck/')"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^metrics/attention/')"
```

Expected output, exactly:

```
G1=ATTNCFG OK checks=8 categories=8 sources=8
G2=ATTNCFG OK selftest 1/1
G3=ATTNSELF OK 9/9
G4=STORENAME OK metrics=11 stored=11 checks=6
G5=STORENAME OK selftest 1/1
COMPILE=0
PYCACHE=0
DIRTY=0
TAG=1
FILES=15
FOREIGN=0
```

`git ls-files` matches recursively, so `FILES` excludes `selfcheck/` and counts exactly the fifteen files this phase wrote outside it — nine at the top level (`taxonomy.yaml`, `sources.yaml`, `calibration.yaml`, `validate-attention-config.sh`, `validate-store-naming.sh`, `derived-metrics.yaml`, `derive.py`, `scheduled-availability.py`, `HANDOFF-P.md`) and six under `lib/` (`config.py`, `sessions.py`, `precedence.py`, `attribute.py`, `reconcile.py`, `selfreport.py`). `selfcheck/` adds `run.sh`, nine inputs and seven expected documents, proved separately by L4-T412.

**STOP rule** — if `G2` or `G5` is not its `selftest 1/1` line, a validator in this phase cannot fail and is decoration (charter §12 rule 10) — **fix the validator, never the fixture**. If `DIRTY` is not `0`, a task left an uncommitted file; commit it under the task that produced it, never under this one. If `PYCACHE` is not `0`, `__pycache__` has been tracked — remove it from the index and do not add an ignore rule to a root file, because root files belong to L0 (PARTITION.md line 24). Do **not** proceed to L4-T416 with any gate row red. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T415 attention-ledger gate is not green"
lane: L4
phase: 4
task_id: L4-T415
blocked_by: "<G1 | G2 | G3 | G4 | G5 | G6 red | tree dirty | __pycache__ tracked>"
observed: "<paste the exact SELF-VERIFY output and the failing check's full output>"
expected: "G1..G5 the five OK lines / COMPILE=0 / PYCACHE=0 / DIRTY=0 / TAG=1 / FILES=15 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.1 line 8838; Section 97.4 lines 8969-8981; L4-00-charter.md section 12 rule 10; PARTITION.md line 24"
needs: "L0"
action_taken: "no validator relaxed, no expected fixture edited, no root file touched"
```

---

## 7. THE READY-QUEUE-MISS DETECTOR — normative, and its two tasks

§97.5 (lines 8982–8987) and §29.4 (line 2670) are **one metric**: §29.4 states the condition, §97.5 states the detector. SIG-06 (line 4535) is the count they feed — *"Ready Queue Miss events … 30-day rolling count and trend"*, Planning board, Amber, owner Team Lead. Invariant 15 (line 9471): *"Ready-queue misses trend to zero."*

### 7.1 The classification table — ordered, first match wins

Every row below is quoted from §97.5. The order is the table's order and is **not** a preference: an item whose Blocked flag was just cleared is a resumption whatever else is true of it, so C1 precedes everything.

| # | Condition | Verdict | `limb` | `counts_in_sig06` | Spec line |
|---|---|---|---|---|---|
| C1 | `blocked_flag_cleared` is true | `no_miss` | — | `false` | 8984 — *"clearing the flag and resuming the item is a resumption, not a fresh pickup, and is never counted as a miss"* |
| C2 | `transition.from` is `Ready` | `no_miss` | — | `false` | 8984 — *"The Planned column is the normal assignment step (Ready → Planned → In Progress) and passing through it is never a miss"* |
| C3 | `transition.to` is `Done` **and** `ready_queue` is empty | `miss` | `completion_with_empty_ready` | `true` | 8986 — *"Completion with an empty Ready queue counts"* |
| C4 | `transition.to` is `Done` **and** `ready_queue` is non-empty | `no_miss` | — | `false` | 8986 — the idle case is the one that counts; a completion into a stocked queue is not it |
| C5 | `transition.from` is `Backlog`, `to` is `Planned` or `InProgress`, **and** `ready_queue` is empty | `miss` | `pickup_without_ready` | `true` | 8984 — *"a board transition from Backlog directly to Planned or In Progress, or an item started while the product's Ready queue is empty"* |
| C6 | `transition.from` is `Backlog`, `to` is `Planned` or `InProgress`, **and** `ready_queue` is non-empty | `ready_bypass` | `ready_bypass` | `false` | 8986 — *"A bypass with a full Ready queue does not count … recorded with reason `ready_bypass` as a board-hygiene finding … and never enters the SIG-06 count"* |
| C7 | anything else | `no_miss` | — | `false` | the detector is a pickup-and-completion detector; nothing else is a transition it judges |

### 7.2 The verdict document — eight keys, none of them invented

`tools/records/rqm-emit` (Phase 3, task `L4-T309`) already fixes the document it accepts and **refuses any of the eight keys missing or empty**. This phase's detector produces that document and nothing else; it never appends an event and never calls `rqm-emit`. The boundary is the mirror of Phase 3's: *"`rqm-emit` emits; it does not decide"* — **`rqm-detect` decides; it does not emit.**

| Key | Filled from | Cause-prompt field |
|---|---|---|
| `limb` | the classification table above | no |
| `person` | the input's `person` | no |
| `date` | the input's `date` | no |
| `product` | the input's `product` | no |
| `subject_ref` | the input's `subject_ref`, else `null` | no |
| `queue_empty_reason` | the input's field of the same name, else `null` | **yes** |
| `team_lead_blocked` | the input's field of the same name, else `null` | **yes** |
| `priority_changed_recently` | the input's field of the same name, else `null` | **yes** |

**The three cause keys are present only when `cause_prompt_answered` is true.** §97.5 line 8986: *"the last three supplied by the cause prompt, never inferred."* An unanswered prompt therefore yields a five-key record whose key set is a strict subset of the answered one, differing by exactly three — which is how `L4-P7-T10` asserts the §29.4 field set without naming a single field.

**`--emit` writes nothing it knows `rqm-emit` would reject.** `rqm-emit` refuses a key whose value is `None` or `""`, so `--emit` writes the verdict document only when `cause_prompt_answered` is true **and** all eight values are non-null. Otherwise it prints `RQM-DETECT PENDING-CAUSE <case>`, exits `0`, writes no file, and fabricates nothing (§5, **D-L4-P4-02**).

---

### L4-T416 — The Ready-queue-miss contract

**Size:** M
**Depends on:** L4-T415

Transcribe §7.1 and §7.2 into `tools/records/rqm-contract.yaml`. Copy the block below **verbatim**. Do not add a rule, do not reorder them, do not change a `spec_line`.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/rqm-contract.yaml" <<'RQC_EOF'
# tools/records/rqm-contract.yaml
# The Ready-queue-miss classification contract. MasterSpec v4.0 Section 97.5 lines 8982-8987
# and Section 29.4 line 2670. The count it feeds is SIG-06 (Section 52.2 line 4535).
# Section 97.5 line 8986: "Section 29.4 states the condition and this section states the
# detector; they are one metric."
# The eight verdict-document keys are NOT declared here as a new shape: they are the keys
# tools/records/rqm-emit (L4-03-write-paths.md task L4-T309) already requires.
contract_version: 1
emitter: tools/records/rqm-emit
detector: tools/records/rqm-detect
event_type: ready_queue_miss_recorded      # looked up in metrics/taxonomy/event-types.yaml
signal: SIG-06
signal_spec_line: 4535
invariant: "Ready-queue misses trend to zero"
invariant_spec_line: 9471

# Ordered. First match wins. Never reorder: C1 precedes everything because a resumption is a
# resumption whatever else is true of the transition.
rules:
  - id: C1
    when: {blocked_flag_cleared: true}
    verdict: no_miss
    reason: resumption
    counts_in_sig06: false
    spec_line: 8984
    quote: "clearing the flag and resuming the item is a resumption, not a fresh pickup, and is never counted as a miss"
  - id: C2
    when: {transition_from: Ready}
    verdict: no_miss
    reason: normal_assignment
    counts_in_sig06: false
    spec_line: 8984
    quote: "The Planned column is the normal assignment step (Ready -> Planned -> In Progress) and passing through it is never a miss"
  - id: C3
    when: {transition_to: Done, ready_queue: empty}
    verdict: miss
    limb: completion_with_empty_ready
    reason: completion_empty_queue
    counts_in_sig06: true
    spec_line: 8986
    quote: "Completion with an empty Ready queue counts"
  - id: C4
    when: {transition_to: Done, ready_queue: non_empty}
    verdict: no_miss
    reason: completion_queue_available
    counts_in_sig06: false
    spec_line: 8986
  - id: C5
    when: {transition_from: Backlog, transition_to: [Planned, InProgress], ready_queue: empty}
    verdict: miss
    limb: pickup_without_ready
    reason: pickup_without_ready
    counts_in_sig06: true
    spec_line: 8984
    quote: "a board transition from Backlog directly to Planned or In Progress, or an item started while the product's Ready queue is empty"
  - id: C6
    when: {transition_from: Backlog, transition_to: [Planned, InProgress], ready_queue: non_empty}
    verdict: ready_bypass
    limb: ready_bypass
    reason: board_hygiene
    counts_in_sig06: false
    spec_line: 8986
    quote: "A bypass with a full Ready queue does not count ... recorded with reason ready_bypass as a board-hygiene finding for the Team Lead, and never enters the SIG-06 count"
  - id: C7
    when: {otherwise: true}
    verdict: no_miss
    reason: not_a_pickup
    counts_in_sig06: false
    spec_line: 8984

# The Section 29.4 field set (line 2670): who, which date, which product, why the queue was
# empty, whether the Team Lead was blocked, and whether product priority changed recently.
verdict_document_keys:
  always: [limb, person, date, product, subject_ref]
  cause_prompt_only: [queue_empty_reason, team_lead_blocked, priority_changed_recently]
cause_prompt_rule: "The last three are supplied by the cause prompt, never inferred."
cause_prompt_spec_line: 8986
field_set_spec_line: 2670

# Section 91 (Retention, No-Surveillance, Fairness and Anti-Goodhart), Section 29.4 line 2670.
never:
  - "an individual performance signal - this is a Team Lead capacity signal"
  - "an inferred cause - the three cause fields are answered or absent, never guessed"
  - "a ready_bypass counted in SIG-06"
never_spec_lines: [2670, 8986]
RQC_EOF
git -C "$CP_ROOT" add tools/records/rqm-contract.yaml
git -C "$CP_ROOT" commit -m "L4-T416: Ready-queue-miss classification contract (97.5 8982-8987, 29.4 line 2670)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file parses as YAML | `python3 -c "import yaml;yaml.safe_load(open(r'$CP_ROOT/tools/records/rqm-contract.yaml'))"; echo $?` | `0` |
| 2 | Seven rules, in order `C1`…`C7` | see SELF-VERIFY `RULES` | `C1,C2,C3,C4,C5,C6,C7` |
| 3 | Exactly two rules count in SIG-06 | see SELF-VERIFY `SIG06` | `2` |
| 4 | `ready_bypass` does **not** count in SIG-06 | see SELF-VERIFY `BYPASS` | `False` |
| 5 | Eight verdict-document keys, three of them cause-prompt | see SELF-VERIFY `KEYS` | `5 3` |
| 6 | The eight keys match `rqm-emit`'s requirement exactly | see SELF-VERIFY `MATCHEMIT` | `8` |
| 7 | No `event_type` identifier is declared, only looked up | `grep -c 'ready_queue_miss_recorded' "$CP_ROOT/tools/records/rqm-contract.yaml"` | `1` |
| 8 | Only `metrics/attention/` and `tools/records/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(metrics/attention|tools/records)/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, yaml
p = os.path.join(os.environ["CP_ROOT"], "tools", "records", "rqm-contract.yaml")
d = yaml.safe_load(open(p, encoding="utf-8"))
rules = d["rules"]
print("RULES=%s" % ",".join(r["id"] for r in rules))
print("SIG06=%d" % sum(1 for r in rules if r["counts_in_sig06"]))
print("BYPASS=%s" % [r for r in rules if r["verdict"] == "ready_bypass"][0]["counts_in_sig06"])
k = d["verdict_document_keys"]
print("KEYS=%d %d" % (len(k["always"]), len(k["cause_prompt_only"])))
emit = open(os.path.join(os.environ["CP_ROOT"], "tools", "records", "rqm-emit"),
            encoding="utf-8").read()
declared = k["always"] + k["cause_prompt_only"]
print("MATCHEMIT=%d" % sum(1 for key in declared if '"%s"' % key in emit))
PY
echo "EVTONCE=$(grep -c 'ready_queue_miss_recorded' "$CP_ROOT/tools/records/rqm-contract.yaml")"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(metrics/attention|tools/records)/')"
```

Expected output, exactly:

```
RULES=C1,C2,C3,C4,C5,C6,C7
SIG06=2
BYPASS=False
KEYS=5 3
MATCHEMIT=8
EVTONCE=1
FOREIGN=0
```

**STOP rule** — if `MATCHEMIT` is not `8`, this contract and Phase 3's `tools/records/rqm-emit` disagree about the verdict document, and every emission will be refused at write time. **Do not edit `rqm-emit`** — it is Phase 3's file and editing it is a foreign write inside your own lane's history; correct this contract instead, and if `rqm-emit` is the one that is wrong, that is a blocker for L0. If `BYPASS` is not `False`, a full-queue bypass is about to be counted in SIG-06, which line 8986 forbids and which makes invariant 15 (*"trend to zero"*, line 9471) unmeasurable by inflating the count with board hygiene. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T416 Ready-queue-miss contract disagrees with rqm-emit or with Section 97.5"
lane: L4
phase: 4
task_id: L4-T416
blocked_by: "<verdict-document keys do not match rqm-emit | ready_bypass counted in SIG-06 | rule order changed | event_type declared rather than looked up>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "RULES=C1,C2,C3,C4,C5,C6,C7 / SIG06=2 / BYPASS=False / KEYS=5 3 / MATCHEMIT=8 / EVTONCE=1 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.5 lines 8982-8987; Section 29.4 line 2670; SIG-06 line 4535; invariant 15 line 9471; L4-03-write-paths.md task L4-T309"
needs: "L0"
action_taken: "nothing beyond tools/records/rqm-contract.yaml; tools/records/rqm-emit untouched"
```

---

### L4-T417 — `rqm-detect`, the Ready-queue-miss detector

**Size:** L
**Depends on:** L4-T416

The detector §97.5 line 8984 describes. **Its command line and JSON shape are input to this task**: `L4-07-tests-and-runbook.md` task `L4-P7-T10` already calls `rqm-detect --input <f.yaml> --json` and reads `verdict`, `counts_in_sig06` and `record` (§2.2). Charter DoD-8 is that suite's `RQM OK 6/6`.

**This script decides; it does not emit.** It never appends an event, never writes under `records/` or `events/`, and never invokes `rqm-emit`. `--emit <path>` writes **only** the verdict document, for the board automation to hand to `rqm-emit`.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/rqm-detect" <<'RQD_EOF'
#!/usr/bin/env python3
# tools/records/rqm-detect - the Ready-queue-miss detector.
# MasterSpec v4.0 Section 97.5 lines 8982-8987; Section 29.4 line 2670; SIG-06 line 4535.
# THIS SCRIPT DECIDES; IT DOES NOT EMIT. It appends no event, writes nothing under records/ or
# events/, and never invokes tools/records/rqm-emit. --emit writes only the verdict document.
# Every rule is read from tools/records/rqm-contract.yaml; none is written here.
# Usage: rqm-detect --input <case.yaml> [--json] [--emit <verdict-path>]
import json
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(HERE, "rqm-contract.yaml")
ALWAYS_KEYS = ["limb", "person", "date", "product", "subject_ref"]
CAUSE_KEYS = ["queue_empty_reason", "team_lead_blocked", "priority_changed_recently"]


def die(reason, code):
    print("RQM-DETECT ERROR %s" % reason, file=sys.stderr)
    sys.exit(code)


def classify(case, rules):
    """Ordered, first match wins. Section 97.5 lines 8984 and 8986."""
    transition = case.get("transition") or {}
    src = transition.get("from")
    dst = transition.get("to")
    queue_empty = not (case.get("ready_queue") or [])
    for rule in rules:
        when = rule["when"]
        if when.get("otherwise"):
            return rule
        if "blocked_flag_cleared" in when:
            if bool(case.get("blocked_flag_cleared")) == when["blocked_flag_cleared"]:
                return rule
            continue
        ok = True
        if "transition_from" in when and src != when["transition_from"]:
            ok = False
        if "transition_to" in when:
            want = when["transition_to"]
            want = want if isinstance(want, list) else [want]
            if dst not in want:
                ok = False
        if "ready_queue" in when:
            if when["ready_queue"] == "empty" and not queue_empty:
                ok = False
            if when["ready_queue"] == "non_empty" and queue_empty:
                ok = False
        if ok:
            return rule
    die("no-rule-matched", 3)


def build_record(case, rule):
    """The Section 29.4 field set. The last three only when the cause prompt was answered."""
    record = {"limb": rule.get("limb"),
              "person": case.get("person"),
              "date": str(case.get("date")) if case.get("date") is not None else None,
              "product": case.get("product"),
              "subject_ref": case.get("subject_ref")}
    if case.get("cause_prompt_answered"):
        for key in CAUSE_KEYS:
            record[key] = case.get(key)          # never inferred (line 8986)
    return record


def main(argv):
    path, as_json, emit_to = None, False, None
    i = 0
    while i < len(argv):
        if argv[i] == "--input":
            i += 1
            if i >= len(argv):
                die("missing-value-for:--input", 2)
            path = argv[i]
        elif argv[i] == "--json":
            as_json = True
        elif argv[i] == "--emit":
            i += 1
            if i >= len(argv):
                die("missing-value-for:--emit", 2)
            emit_to = argv[i]
        else:
            die("unknown-argument:%s" % argv[i], 2)
        i += 1
    if path is None:
        die("no-input", 2)
    if not os.path.exists(CONTRACT):
        die("missing-contract", 3)
    if not os.path.exists(path):
        die("missing-input:%s" % path, 3)
    contract = yaml.safe_load(open(CONTRACT, encoding="utf-8"))
    case = yaml.safe_load(open(path, encoding="utf-8")) or {}
    rule = classify(case, contract["rules"])
    out = {"case": case.get("case"),
           "rule": rule["id"],
           "verdict": rule["verdict"],
           "limb": rule.get("limb"),
           "reason": rule["reason"],
           "counts_in_sig06": bool(rule["counts_in_sig06"])}
    if rule["verdict"] != "no_miss":
        out["record"] = build_record(case, rule)

    if emit_to is not None:
        # Section 97.5 line 8986 and D-L4-P4-02: never fabricate a cause, and never write a
        # document tools/records/rqm-emit would refuse (it rejects a null or empty value).
        record = out.get("record")
        complete = bool(record) and case.get("cause_prompt_answered") \
            and all(record.get(k) not in (None, "") for k in ALWAYS_KEYS + CAUSE_KEYS)
        if not complete:
            print("RQM-DETECT PENDING-CAUSE %s" % case.get("case"))
            return 0
        with open(emit_to, "w", encoding="utf-8") as fh:
            yaml.safe_dump(record, fh, sort_keys=False)
        print("RQM-DETECT EMITTED %s %s" % (case.get("case"), emit_to))
        return 0

    if as_json:
        print(json.dumps(out))
    else:
        print("RQM-DETECT %s %s" % (out["verdict"], case.get("case")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
RQD_EOF
chmod +x "$CP_ROOT/tools/records/rqm-detect"
git -C "$CP_ROOT" add tools/records/rqm-detect
git -C "$CP_ROOT" commit -m "L4-T417: rqm-detect - the Ready-queue-miss detector (97.5 line 8984, charter DoD-8)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The detector is executable | `test -x "$CP_ROOT/tools/records/rqm-detect" && echo YES` | `YES` |
| 2 | The six §97.5 cases classify as the table says | see SELF-VERIFY `RQ1`…`RQ6` | the six rows below |
| 3 | The answered record carries eight keys | see SELF-VERIFY `FIELDSET` | `SUBSET 3` |
| 4 | It contains no rule of its own | `grep -c 'Backlog\|InProgress' "$CP_ROOT/tools/records/rqm-detect"` | `0` |
| 5 | It writes nothing to the records repository | `grep -c 'CPR_ROOT\|emit_event\|rqm-emit\"' "$CP_ROOT/tools/records/rqm-detect"` | `0` |
| 6 | `--emit` refuses an unanswered cause prompt | see SELF-VERIFY `PENDING` | `RQM-DETECT PENDING-CAUSE RQ-1` |
| 7 | `--emit` writes no file when the cause is pending | see SELF-VERIFY `NOFILE` | `absent` |
| 8 | A missing input fails closed | see SELF-VERIFY `MISSING` | `3` |
| 9 | Only `metrics/attention/` and `tools/records/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(metrics/attention|tools/records)/'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
DET="$CP_ROOT/tools/records/rqm-detect"
T="$(mktemp -d)"
mk() { cat > "$T/$1"; }
mk rq-1.yaml <<'EOF'
case: RQ-1
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Backlog, to: InProgress}
ready_queue: []
blocked_flag_cleared: false
cause_prompt_answered: true
EOF
sed 's/^cause_prompt_answered: true/cause_prompt_answered: false/' "$T/rq-1.yaml" > "$T/rq-1u.yaml"
sed -e 's/^case: RQ-1/case: RQ-2/' -e 's/to: InProgress/to: Planned/' "$T/rq-1.yaml" > "$T/rq-2.yaml"
mk rq-3.yaml <<'EOF'
case: RQ-3
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Ready, to: Planned, then: InProgress}
ready_queue: [WI-101, WI-102]
blocked_flag_cleared: false
cause_prompt_answered: false
EOF
mk rq-4.yaml <<'EOF'
case: RQ-4
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: InProgress, to: InProgress}
ready_queue: []
blocked_flag_cleared: true
cause_prompt_answered: false
EOF
mk rq-5.yaml <<'EOF'
case: RQ-5
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: InProgress, to: Done}
ready_queue: []
blocked_flag_cleared: false
cause_prompt_answered: true
EOF
mk rq-6.yaml <<'EOF'
case: RQ-6
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Backlog, to: Planned}
ready_queue: [WI-101, WI-102]
blocked_flag_cleared: false
cause_prompt_answered: true
EOF
v() { "$DET" --input "$T/$1" --json 2>/dev/null | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("verdict","NONE"),d.get("counts_in_sig06","NONE"))'; }
for n in 1 2 3 4 5 6; do echo "RQ$n=$(v rq-$n.yaml)"; done
"$DET" --input "$T/rq-1.yaml"  --json > "$T/a.json" 2>/dev/null
"$DET" --input "$T/rq-1u.yaml" --json > "$T/b.json" 2>/dev/null
echo "FIELDSET=$(python3 - "$T/a.json" "$T/b.json" <<'PY'
import sys, json
a = set(json.load(open(sys.argv[1]))["record"].keys())
b = set(json.load(open(sys.argv[2]))["record"].keys())
print(("SUBSET" if b < a else "NOTSUBSET"), len(a - b))
PY
)"
echo "PENDING=$("$DET" --input "$T/rq-1.yaml" --emit "$T/verdict.yaml")"
echo "NOFILE=$(test ! -f "$T/verdict.yaml" && echo absent || echo present)"
"$DET" --input "$T/nope.yaml" --json >/dev/null 2>&1; echo "MISSING=$?"
echo "NORULES=$(grep -c 'Backlog\|InProgress' "$DET")"
echo "NOWRITE=$(grep -c 'CPR_ROOT\|emit_event' "$DET")"
rm -rf "$T"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(metrics/attention|tools/records)/')"
```

Expected output, exactly:

```
RQ1=miss True
RQ2=miss True
RQ3=no_miss False
RQ4=no_miss False
RQ5=miss True
RQ6=ready_bypass False
FIELDSET=SUBSET 3
PENDING=RQM-DETECT PENDING-CAUSE RQ-1
NOFILE=absent
MISSING=3
NORULES=0
NOWRITE=0
FOREIGN=0
```

`PENDING` is correct even though `rq-1.yaml` answers the cause prompt: the fixture supplies no `subject_ref` and no cause text, so three of the eight values are `null` and `rqm-emit` would refuse the document. The detector refuses to write it rather than filling a value in — §97.5 line 8986, *"never inferred."*

**STOP rule** — if `RQ3` or `RQ4` reports `miss`, the detector counts the normal assignment step or a resumption as a miss; §97.5 line 8984 excludes both by name, and an over-reporting detector makes invariant 15 (*"Ready-queue misses trend to zero"*, line 9471) unmeasurable. If `RQ6` is not `ready_bypass False`, board hygiene is being counted in SIG-06, which line 8986 forbids. If `FIELDSET` is not `SUBSET 3`, the three cause-prompt fields are being emitted when unanswered — which means they are being **inferred**, the one thing line 8986 prohibits. **Never change a fixture's `ready_queue` to make a case pass, and never edit `tools/records/rqm-emit`.** Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T417 rqm-detect misclassifies a Section 97.5 case or infers a cause field"
lane: L4
phase: 4
task_id: L4-T417
blocked_by: "<normal assignment counted | resumption counted | ready_bypass in SIG-06 | cause field inferred | detector wrote to the records repository>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "RQ1=miss True / RQ2=miss True / RQ3=no_miss False / RQ4=no_miss False / RQ5=miss True / RQ6=ready_bypass False / FIELDSET=SUBSET 3 / PENDING=RQM-DETECT PENDING-CAUSE RQ-1 / NOFILE=absent / MISSING=3 / NORULES=0 / NOWRITE=0"
spec_ref: "Master Spec v4.0 Section 97.5 lines 8984, 8986; Section 29.4 line 2670; SIG-06 line 4535; invariant 15 line 9471; L4-00-charter.md DoD-8"
needs: "L0"
action_taken: "nothing beyond tools/records/rqm-detect; rqm-emit untouched; no fixture altered"
```

---

## 8. Phase exit

### L4-T418 — Phase-4 coverage proof, rebase and lane PR

**Size:** M
**Depends on:** L4-T415, L4-T416, L4-T417

The phase closes only when every rule of §3.3, every category of §3.1 and every §97.5 limb is provably implemented, and only when the branch touches nothing outside the two owned prefixes.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
A="$CP_ROOT/metrics/attention"
"$A/validate-attention-config.sh"
"$A/validate-attention-config.sh" --selftest
sh "$A/selfcheck/run.sh"
"$A/validate-store-naming.sh"
"$A/validate-store-naming.sh" --selftest
sh "$CP_ROOT/tools/records/lane-selfcheck.sh"
find "$CP_ROOT" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null
git -C "$CP_ROOT" fetch origin --prune
git -C "$CP_ROOT" rebase origin/integration
git -C "$CP_ROOT" diff --name-only origin/integration...HEAD
git -C "$CP_ROOT" push -u origin lane/4/04-attention-ledger
gh pr create --repo "$(git -C "$CP_ROOT" remote get-url origin | sed 's#.*/\([^/]*/[^/]*\)\.git#\1#')" \
  --base integration --head lane/4/04-attention-ledger \
  --title "L4 phase 4: the attention ledger, its duration rule, and the Ready-queue-miss detector" \
  --body "Implements Master Spec v4.0 Section 67.2 (the eight-category taxonomy), Section 97.4 (per-category sources, the duration rule DR-1..DR-7, the weekly banded self-report) and Section 97.5 (the Ready-queue-miss detector). Closes the D102 hole: attention-hour duration now has a named activity session, a named idle gap (30 minutes, calibrated), a named granularity (0.25 h, calibrated, never zero), a named daily cap resolved through Section 69.2 to work_arrangement (Section 7.3), and a deterministic precedence order. Every threshold is calibrated configuration with a stated initial value in metrics/attention/calibration.yaml. Every metric names its record store (Section 97.1 line 8838) in metrics/attention/derived-metrics.yaml. Open for L0: D-L4-P4-01, D-L4-P4-02, D-L4-P4-03, D-L4-P4-04."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Every rule DR-1…DR-7 is exercised by a passing case | see SELF-VERIFY `SELF` | `ATTNSELF OK 9/9` |
| 2 | Config and store-naming gates pass, and both can fail | see SELF-VERIFY `CFG`, `STORE`, `CFGC`, `STOREC` | the four OK lines |
| 3 | The detector classifies a miss and a bypass correctly | see SELF-VERIFY `RQM` | `RQM-DETECT miss X1 / RQM-DETECT ready_bypass X2` |
| 4 | The branch touches only the two owned prefixes | see SELF-VERIFY `FOREIGN` | `0` |
| 5 | No other lane's branch was touched | see SELF-VERIFY `OTHERLANES` | `0` |
| 6 | The branch is rebased on `integration` | see SELF-VERIFY `BASE` | `integration` |
| 7 | Nothing was written to the records repository | see SELF-VERIFY `CPRCLEAN` | `0` |
| 8 | The PR exists against `integration` | `gh pr view --json baseRefName -q .baseRefName` | `integration` |

**SELF-VERIFY**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
A="$CP_ROOT/metrics/attention"
echo "CFG=$("$A/validate-attention-config.sh" | tail -1)"
echo "CFGC=$("$A/validate-attention-config.sh" --selftest | tail -1)"
echo "SELF=$(sh "$A/selfcheck/run.sh" | tail -1)"
echo "STORE=$("$A/validate-store-naming.sh" | tail -1)"
echo "STOREC=$("$A/validate-store-naming.sh" --selftest | tail -1)"
T="$(mktemp -d)"
printf 'case: X1\nperson: dev-a\ndate: 2026-09-14\nproduct: alpha\ntransition: {from: Backlog, to: InProgress}\nready_queue: []\nblocked_flag_cleared: false\ncause_prompt_answered: false\n' > "$T/x1.yaml"
printf 'case: X2\nperson: dev-a\ndate: 2026-09-14\nproduct: alpha\ntransition: {from: Backlog, to: Planned}\nready_queue: [WI-1]\nblocked_flag_cleared: false\ncause_prompt_answered: false\n' > "$T/x2.yaml"
echo "RQM=$("$CP_ROOT/tools/records/rqm-detect" --input "$T/x1.yaml" | tail -1) / $("$CP_ROOT/tools/records/rqm-detect" --input "$T/x2.yaml" | tail -1)"
rm -rf "$T"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(metrics/attention|tools/records)/')"
echo "OTHERLANES=$(git -C "$CP_ROOT" reflog --date=short | grep -cE 'lane/(1|2|3|5)/')"
echo "BASE=$(git -C "$CP_ROOT" merge-base --is-ancestor origin/integration HEAD && echo integration || echo stale)"
echo "HEAD=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
CFG=ATTNCFG OK checks=8 categories=8 sources=8
CFGC=ATTNCFG OK selftest 1/1
SELF=ATTNSELF OK 9/9
STORE=STORENAME OK metrics=11 stored=11 checks=6
STOREC=STORENAME OK selftest 1/1
RQM=RQM-DETECT miss X1 / RQM-DETECT ready_bypass X2
FOREIGN=0
OTHERLANES=0
BASE=integration
HEAD=lane/4/04-attention-ledger
CPRCLEAN=0
DIRTY=0
```

**STOP rule** — if `FOREIGN` is not `0`, the branch touches a path this lane does not own and the lane-guard check will fail the PR; **do not force-push and do not resolve another lane's conflict** (PARTITION.md rule 1, and the branch model line: *"A lane NEVER merges another lane's branch"*). If `CPRCLEAN` is not `0`, something in this phase wrote to `control-plane-records`, which §2 forbids for phase 4 outright — every write path there belongs to Phase 3's `emit.sh`. If `SELF` is not `ATTNSELF OK 9/9`, a derivation rule regressed during the rebase; re-run the failing case and fix `derive.py`, never the expected document. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T418 Phase 4 exit gate or lane-guard preconditions failed"
lane: L4
phase: 4
task_id: L4-T418
blocked_by: "<foreign path | records repo written | selfcheck regressed | rebase conflict | another lane's branch touched>"
observed: "<paste the exact SELF-VERIFY output and every FAIL line>"
expected: "CFG / CFGC / SELF / STORE / STOREC the five OK lines / RQM=RQM-DETECT miss X1 / RQM-DETECT ready_bypass X2 / FOREIGN=0 / OTHERLANES=0 / BASE=integration / HEAD=lane/4/04-attention-ledger / CPRCLEAN=0 / DIRTY=0"
spec_ref: "Master Spec v4.0 Section 97.4 lines 8955-8981; Section 97.5 lines 8982-8987; Section 99.6 risk 2 lines 9276-9294; PARTITION.md rules 1 and 4"
needs: "L0"
action_taken: "no force-push, no merge, no other-lane branch modified, no records repository write"
```

---

## 9. Task summary

| Task ID | Title | Size | Depends on | Files written |
|---|---|---|---|---|
| L4-T401 | Phase-4 preflight and phase branch | S | — | none (branch + directories) |
| L4-T402 | The eight-category taxonomy artifact | M | L4-T401 | `metrics/attention/taxonomy.yaml` |
| L4-T403 | The per-category source map | M | L4-T401 | `metrics/attention/sources.yaml` |
| L4-T404 | The calibrated-configuration register | M | L4-T401 | `metrics/attention/calibration.yaml` |
| L4-T405 | Config validator, with its negative test | M | T402, T403, T404 | `metrics/attention/validate-attention-config.sh` |
| L4-T406 | Scheduled availability, the daily cap's input | L | L4-T404 | `metrics/attention/scheduled-availability.py` |
| L4-T407 | DR-1…DR-4: config reader, session, idle gap, granularity | L | L4-T404, L4-T405 | `metrics/attention/lib/config.py`, `lib/sessions.py` |
| L4-T408 | DR-5: category precedence | M | L4-T407 | `metrics/attention/lib/precedence.py` |
| L4-T409 | DR-6: product attribution | M | L4-T407 | `metrics/attention/lib/attribute.py` |
| L4-T410 | DR-7: daily reconciliation and the instrument defect | L | L4-T404, L4-T406 | `metrics/attention/lib/reconcile.py` |
| L4-T411 | `derive.py`, the attention ledger | L | T407, T408, T409, T410 | `metrics/attention/derive.py`, `lib/selfreport.py` |
| L4-T412 | Phase-4 self-check, nine cases | L | L4-T406, L4-T411 | `metrics/attention/selfcheck/**` |
| L4-T413 | `HANDOFF-P.md` — what the ledger emits for subsystem P | M | L4-T411 | `metrics/attention/HANDOFF-P.md` |
| L4-T414 | Every metric names its store, with the shipping test | L | L4-T411, L4-T412 | `metrics/attention/derived-metrics.yaml`, `validate-store-naming.sh` |
| L4-T415 | Attention-ledger gate and phase checkpoint | M | T405, T412, T414 | none (tag only) |
| L4-T416 | The Ready-queue-miss contract | M | L4-T415 | `tools/records/rqm-contract.yaml` |
| L4-T417 | `rqm-detect`, the Ready-queue-miss detector | L | L4-T416 | `tools/records/rqm-detect` |
| L4-T418 | Phase-4 coverage proof, rebase and lane PR | M | T415, T416, T417 | none (rebase + PR) |

**Sizes:** 1 × S, 10 × M, 7 × L.

Dependency spine: `T401 → {T402, T403, T404} → T405 → {T406, T407} → {T408, T409, T410} → T411 → {T412, T413} → T414 → T415 → T416 → T417 → T418`.

---

## 10. What Phase 4 hands to the other lanes

| Artifact | Consumer | Consumed as |
|---|---|---|
| `metrics/attention/derive.py` | **L4 phase 7** | The executable `metrics/attention/test-derivation.sh` (`L4-P7-T09`) and `tools/records/test/suite-at.sh` (`L4-P7-T12`) invoke |
| `tools/records/rqm-detect` | **L4 phase 7** | The executable `tools/records/test/suite-06-rqm.sh` (`L4-P7-T10`) invokes; charter DoD-8 |
| `tools/records/rqm-contract.yaml`, `rqm-detect` | **L2** | The classification the board automation runs before calling Phase 3's `rqm-emit` |
| `metrics/attention/calibration.yaml` | **L0** | The calibrated-configuration register the §84.6 line 7478 threshold review refits |
| `metrics/attention/derived-metrics.yaml` | **L0**, and the metric-register phase | The ledger's half of the §97.1 line 8838 store-naming rule; ids here never duplicate `metrics/register/**` |
| `metrics/attention/validate-attention-config.sh`, `validate-store-naming.sh` | **L0** | Two status checks for the integration gate |
| `instrument_defect` and the three eligibility flags | **L3** | The drift finding of §97.4 line 8976; `validators/drift/**` is L3 (PARTITION.md line 19) |
| `metrics/attention/HANDOFF-P.md` | **L0** | The contract for whoever receives subsystem P — unassigned in PARTITION v1 |
| The DevLake ingest dependency in `sources.yaml` | **L0**, routing to **L5** | Engineering and Review windows in production; `ops-vm/**` is L5 (PARTITION.md line 21) |

---

## 11. Standing rules — this phase only

The lane charter's §12 applies in full. Five rules bind this phase in particular:

1. **No threshold is a literal in code.** Every one is read from `metrics/attention/calibration.yaml`, and check **C8** of `validate-attention-config.sh` proves every `.py` under `metrics/attention/` reads it. D102 (line 10195) requires each to be *"defined once, with the calibrated-configuration convention and a stated initial value."*
2. **Never retune a threshold to make a task pass.** A refit is a §84.6 line 7478 calibration review — evidenced, dated, and run at the six- or twelve-month cadence — never an edit during a build. A number that will not come out is a defect in the derivation, not in the threshold.
3. **Never a ninth category, and never a flag promoted to one.** §67.2 line 5579: *"no parallel category set exists anywhere in the operating system."* `unplanned` and `ritual` are flags; founder coordination time is a sum, not a category (line 5594).
4. **A metric that cannot name its store does not ship.** §97.1 line 8838. It is absent from `derived-metrics.yaml`, not present-and-flagged, and a figure `derive.py` emits with no nameable store is a blocker for L0, not an invented store.
5. **L4 emits; it does not render.** No Capacity Profile, no workload state, no Founder view, no per-person surface, no drift finding — those are subsystem P (unassigned) and L3. §67.3 line 5605 and §91.2 (lines 8083–8092): attention hours are never individual performance evidence and never a per-person drill-down on a general surface.
