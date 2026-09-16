# L4 — RECORDS, EVENTS AND METRICS — LANE CHARTER

**Lane:** L4 Records, Events & Metrics
**Branch prefix:** `lane/4/*`
**Subsystems:** I (Metrics pipeline), N (Work tracking conventions) — Master Spec §99.2, lines 9184–9231
**Merge-train position:** **2nd of 5** — `L1 → **L4** → L2 → L3 → L5`
**Authority:** subordinate to `Code/implementation/PARTITION.md` (FROZEN). Where this charter and PARTITION.md appear to differ, PARTITION.md wins and the difference is a blocker for L0.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## 1. Why this lane exists

Master Spec §99.6 (lines 9276–9294) lists ten top build risks. **Risk 2** reads: *"Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance if the record stores are not built early."* Its stated mitigation is: *"Section 97 is built in Foundation, before any dashboard that reads from it."*

L4 **is** that mitigation. §99.2's dependency spine (line 9229) states: *"I is the feedstock for nearly all governance-tier and people-tier computation."* Invariant 46 (§101.7, line 9513) states: *"Derived data is computed, never hand-maintained. Metrics derive from the canonical record stores of Section 97 … never from hand-maintained numbers."* §103 preamble (line 9776) states that a metric which cannot name its record store does not ship.

If L4 lands late, every governance signal in §52.2 and every measure in §103 is unarmed, and the deploy workflows of L2 have nowhere to write the required, failing record-write steps §97.2 demands.

---

## 2. Subsystem mapping

| Subsystem | Spec row (§99.2, lines 9184–9231) | Complexity in spec | What L4 delivers against it |
|---|---|---|---|
| **I — Metrics pipeline** | *"DevLake nightly ingest; Prometheus scraping `/health`, `/version`, `/metrics`; Scorecard scheduled scan with drop detection; the event-log taxonomy; attention ledger; metric source discipline"* | L | The event-log taxonomy and envelope (§97.3), the attention ledger derivation (§97.4), metric-source discipline and the §103 measure computations, all under `metrics/**` |
| **N — Work tracking conventions** | *"Boards per product plus portfolio aggregate (or the single-Project fallback), horizon semantics, Ready-to-Execute definition, automatic Ready-queue-miss recording"* | M | Board/horizon/Ready conventions as machine-checkable configuration and the Ready-queue-miss detector (§29.1–29.5, §97.5) writing into the event log |

**Named tools of the build surface assigned to L4** (§99.2 tool table, lines 9209–9229): the *Pre-leave handover generator and return digest generator* (subsystems **N**, P) and the *Support email-ingest hook* (subsystems **N**, R) both name subsystem N. L4 owns the **record and event write side** of both (the stores, schemas and writers under its owned paths); the workflow triggers that invoke them are `.github/workflows/**` and belong to L2, and the notification routing belongs to L5. L4 never writes a workflow file in the control-plane repository.

---

## 3. Owned paths — exclusive

Per PARTITION.md line 20, L4 owns:

| Repository | Path | Contents |
|---|---|---|
| **`control-plane-records`** | **the entire repository** | `records/**`, `events/**` and every other file in that repository (README, `.gitignore`, `.gitattributes`, retention manifests) |
| `control-plane` | `schemas/records/**` | JSON Schemas for every record store of §97.2 and for the §97.3 event envelope |
| `control-plane` | `metrics/**` | Metric definitions, derivation code, the attention-ledger derivation, the §103 measure computations, the event-type taxonomy artifact |
| `control-plane` | `tools/records/**` | `record-*` writers, the RECORD-VERIFICATION-RESULT handler, validators, fixtures, the Ready-queue-miss detector, lane self-check |

`control-plane-records` protection posture is fixed by PARTITION.md line 8 and Master Spec §40.1 (lines 3644–3686): **no review protection; a no-bypass ruleset blocking force-push, branch deletion and tag deletion (D107)**. L4 must never propose review protection on that repository and must never propose a bypass actor on the ruleset.

### 3.1 Paths L4 must NEVER touch

| Path | Owner | Why L4 wants it and must not have it |
|---|---|---|
| `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` | L0 | Contract-first (PARTITION rule 2). L4 files a Contract Change Request; it never edits. |
| `registries/**` (incl. `platform.yaml`, `os-health.yaml`, `economics.yaml`) | L1 | The §97.3 event-type enum and the §52.2/§103 metric register live in these files. L4 **publishes content**, L1 **holds the file**. See §9 DECISION REQUIRED D-L4-01 and D-L4-02. |
| `schemas/registry/**`, `schemas/product/**`, `validators/registry/**` | L1 | Registry schema authority. |
| `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` | L2 | Every workflow that *calls* an L4 writer is L2's file. |
| `reconciler/**`, `tools/provision/**`, `validators/drift/**` | L3 | The §53.1 write-freshness drift row and the D107 head-SHA anchor are L3 code reading L4 declarations. |
| `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` | L5 | The records-writer credential's asset-inventory entry (§40.1, line 3684) is L5's `assets/**`. |

A PR from `lane/4/*` touching any row above fails the lane-guard check. There is no exception (PARTITION rule 1).

---

## 4. What L4 consumes

### 4.1 From `contracts/**` (L0, frozen in Phase 0)

L4 codes against these and never edits them. If any is absent or does not carry the named field, **STOP** and file a Contract Change Request — do not invent a substitute.

| Consumed | Used for |
|---|---|
| The record envelope contract — `record_schema_version`, `id`, `product`, `timestamp` (§97.2, lines 8890–8892) | Base schema every record store schema extends |
| The event envelope contract — `event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`, `subject_ref`, `payload` (§97.3, lines 8933–8945) | The envelope validator; an event missing any envelope field is rejected at write time |
| The UTC-with-offset timestamp rule and the declared working calendar / operating timezone reference (§97.1, line 8839) | Every timestamp field format; every business-day derivation names the calendar version it resolved against |
| The versioned-contract mechanism of §60.2 | Record and event schemas are versioned contracts like any other (§97.2, line 8892) |
| Product identity key | The `product:` field on every record and event |
| Registry identity key (the GitHub login per §99.5, line 9271) | The `actor:` field on every event |

### 4.2 From Lane 1 (merged to `integration` before L4 merges)

Consumed **only** through `contracts/**` or a published artifact — never by reaching into L1's source tree (PARTITION rule 4).

| Consumed from L1 | L4 use |
|---|---|
| `registries/platform.yaml` holding the **event_type enum** (§97.3, line 8947: *"The enum is declared in `platform.yaml` beside the supported contract versions"*) | The write-time validator rejects any event whose `event_type` is absent from it |
| `registries/os-health.yaml` — the metric register (§52.6, line 4626; §103 preamble line 9776: *"the one register for metric metadata in this system"*) | Each L4 metric computation reads its `time_window`, `lookback_window`, `activation_dependency`, `baseline` and `known_limitations` from here (§84.6, line 7473; §52.2 arming discipline D77, line 4524) |
| `registries/economics.yaml` — the estimate band vocabulary with representative point values (§29.3, line 2665) | The `records/estimates/` schema carries band label **and** the point value in force when written |
| `schemas/product/**` — `classification.reliability_criticality`, `support_model`, `deletion_sla_days`, `monthly_budget_band` | Per-product interpretation of restore freshness (§103.3), support targets (§22.4), deletion SLA (§51.1) and cost band |
| `schemas/registry/**` — people/roles/assignments | `actor` resolution and the §97.4 per-person daily reconciliation against the Capacity Profile |

---

## 5. What L4 publishes

### 5.1 For Lane 2 (Pipeline & Evidence — subsystems E, F)

L2 merges **after** L4, so every artifact below is already on `integration` when L2 rebases.

| Published artifact (L4-owned path) | L2 consumes it as |
|---|---|
| `schemas/records/deployment.schema.json` | The shape `deploy-production.yml` must write. §97.2 line 8875: the deployment-record and event writes are **required, failing steps** of `deploy-production.yml`, not trailing best-effort ones |
| `schemas/records/uat.schema.json` | The shape the CI UAT job writes on `verification/uat.md` execution |
| `schemas/records/restore-test.schema.json`, `schemas/records/eval.schema.json`, `schemas/records/launch.schema.json`, `schemas/records/security-review.schema.json`, `schemas/records/deletion-request.schema.json` | Shapes for the restore-test workflow, the AI-eval scheduled runner (SIG-42), the launch-pack generator, the security reviewer template and the CI-executed deletion runbook (AT-105) |
| `schemas/records/event.envelope.schema.json` | The envelope every workflow appends against |
| `metrics/taxonomy/event-types.yaml` | The closed `event_type` identifier set of §97.3 (lines 8949–8953) that L1 embeds into `platform.yaml` and L2 emits against. **Note (§4.8):** ~~must re-point at the frozen enum `contracts/registry/event-types.v1.yaml` (or delete this file and DoD-4 together — as shipped, L4 Phase 3 cannot start).~~ **Resolved via FD-065 (2026-09-06):** L4 source identifiers are internal aliases; `metrics/signals/sig-source-map.yaml` maps each SIG row to the corresponding existing L1 event-type identifier at implementation time. |
| `tools/records/record-write` and `tools/records/event-append` | The callable writers L2's workflows invoke through the records-writer credential (§97.1, line 8841) |
| `tools/records/record-verification-result` | The single **RECORD-VERIFICATION-RESULT** `workflow_dispatch` handler (§97.2, line 8886) through which manual UAT results, restore-test confirmations, deletion-runbook results and support-loop closures reach their stores |
| `tools/records/fixtures/**` | Golden valid/invalid fixtures so L2 tests its workflows without an L4 branch |

### 5.2 For Lane 3 (Reconciler & Provisioning — subsystems C, D)

| Published artifact (L4-owned path) | L3 consumes it as |
|---|---|
| `metrics/freshness/write-freshness.yaml` — the declared expected maximum inter-write interval **per store** (§97.2, line 8873) | The §53.1 drift row *"Declared write-freshness window per record store … Latest commit timestamp on the store's path → Amber; **Blocking for `events/`, `records/deployments/` and `records/uat/`**"* (line 4677). Computed from git commit timestamps on the store's path so the check holds when other health inputs are broken |
| `metrics/anchor/records-head-anchor.schema.json` | The D107 anchor format (§40.1, line 3679): once per reconciliation run the reconciler records the records repository's default-branch head SHA and commit count into the fully protected control-plane repository; a non-descendant head is **Blocking drift, Level 5** |
| `schemas/records/restore-test.schema.json` + the store inventory | The §53.1 row *"`product.yaml` `restore_tested` → Newest passing record in `records/restore-tests/` → Blocking"* (line 4681) |
| `metrics/signals/sig-source-map.yaml` | Which SIG rows of §52.2 derive from which L4 store — SIG-06 (Ready-queue misses), SIG-17 (restore-test currency), SIG-41 (support-intake anomaly), SIG-42 (AI-eval regression, source `records/eval/`), SIG-46 (audit-log review staleness, source `records/security-reviews/`) |
| `tools/records/read-across` | The fail-closed cross-repository reader. §40.1 line 3671: *"a check that cannot reach the records repository fails closed rather than reporting zero"* |

### 5.3 For L0 / L1 (published, not written by L4)

`metrics/taxonomy/event-types.yaml` and `metrics/register/metric-declarations.yaml` are L4-authored content whose **destination files** (`platform.yaml`, `os-health.yaml`) are L1-owned. The publication mechanism is D-L4-01 / D-L4-02 in §9.

> **Note (§4.8):** ~~`metrics/taxonomy/event-types.yaml` must re-point at the frozen enum `contracts/registry/event-types.v1.yaml`, or this file and DoD-4 must be deleted together. As shipped, L4 Phase 3 cannot start because this file does not exist and DoD-4 fails.~~ **Resolved via FD-065 (2026-09-06):** L4 source identifiers are internal aliases that map to existing L1 event types; `metrics/signals/sig-source-map.yaml` provides the mapping at implementation time. DoD-4 blocker is cleared.

---

## 6. Merge-train position — second, right after L1

PARTITION.md line 35 fixes the order: `L1 → L4 → L2 → L3 → L5`. PARTITION.md line 39 gives the reason: *"L1 (schemas) and L4 (record schemas) produce what everything validates against."* Four spec facts make the position non-negotiable:

1. **L2 cannot merge first.** §97.2 line 8875 makes the deployment-record and event writes **required, failing steps** of `deploy-production.yml`. A deploy workflow merged before the record schema and writer exist is a workflow whose required step cannot pass — and *"a deploy whose record cannot be written is a deploy whose evidence chain does not close, and the eleven questions of Section 32 are unanswerable for it afterwards."*
2. **L3 cannot merge first.** Three §53.1 drift rows (lines 4677, 4681) and the D107 head-SHA anchor (§40.1, line 3679) read L4 declarations. A reconciler merged first has comparison rows with nothing on the left-hand side.
3. **L4 cannot merge first.** Every record and event carries `product:` and `actor:`, resolved against L1's registries; the `event_type` enum lives in L1's `platform.yaml`; the estimate band vocabulary lives in L1's `economics.yaml`. L4 rebases on an `integration` that already carries L1.
4. **The risk-2 clock.** §99.6 risk 2 requires §97 built in Foundation, *before any dashboard that reads from it*. Second position is the earliest slot that satisfies both directions.

**Cycle discipline.** One branch per task, `lane/4/<phase>-<task>`, short-lived (< 1 day), rebased on `integration` before PR (PARTITION line 34). L4 never merges or rebases another lane's branch (PARTITION line 36).

---

## 7. Definition of done

L4 is done when **every** row below is true and provable by the command named beside it. No row is satisfied by assertion.

| # | Condition | Spec anchor | Proof |
|---|---|---|---|
| DoD-1 | The `control-plane-records` repository exists and contains a directory for **every** store of the §97.2 table plus `events/` | §97.2, lines 8855–8939; §52.6, line 4646 | Verified by L4-P1 tasks (L4-P1-T02 through L4-P1-T06 in `lanes/L4-01`); `--stores` removed from `lane-selfcheck.sh` (CPR_ROOT deleted per §4.8). |
| DoD-2 | A JSON Schema exists in `schemas/records/` for every store in DoD-1, each requiring `record_schema_version`, `id`, `product`, `timestamp` | §97.2, line 8888 | `tools/records/validate-schemas.sh` exits 0 and prints `SCHEMAS GATE PASS` |
| DoD-3 | The event envelope schema rejects an event missing any of the nine envelope fields, and rejects an `event_type` absent from the enum | §97.3, lines 8940–8966 | `tools/records/validate-schemas.sh --negative` exits 0 and prints `NEGATIVE OK 10/10` _(--negative mode: added to L4-02 validate-schemas.sh, Session 12)_ |
| DoD-4 | `metrics/taxonomy/event-types.yaml` carries one stable lower-case underscore-separated identifier for **every** entry of the §97.3 tracked-events list, with a `retired: true` marker mechanism and no delete path | §97.3, lines 8960–8966 | `tools/records/validate-taxonomy.sh` exits 0 and prints `TAXONOMY OK` |
| DoD-5 | Every store declares an expected maximum inter-write interval, and `events/`, `records/deployments/` and `records/uat/` are marked Blocking | §97.2, line 8880; §53.1, line 4679 | `tools/records/validate-freshness.sh` exits 0 and prints `FRESHNESS OK BLOCKING=3` |
| DoD-6 | The attention-ledger derivation implements the eight categories, the idle gap (initial 30 minutes), the granularity (initial 0.25 h, rounded to nearest, never to zero), the fixed precedence order, product attribution, the daily reconciliation with recorded truncations, and the instrument-defect rule | §97.4, lines 8967–8994; §67.2, lines 5586–5604 | `metrics/attention/test-derivation.sh` exits 0 and prints `ATTENTION OK` |
| DoD-7 | Self-reported figures carry a permanent `self-reported` provenance label | §97.4, line 8993 | `metrics/attention/test-derivation.sh --provenance` prints `PROVENANCE OK` |
| DoD-8 | The Ready-queue-miss detector fires when a board item transitions Backlog→Planned or Backlog→In Progress (skipping Ready), or when an item is started while the product's Ready queue holds no suitable item (pickup limb); completion while the product's Ready queue holds no suitable item also counts (completion limb); treats Ready→Planned→In Progress (the normal assignment step passing through Planned) as never a miss; treats Blocked-flag clearing as resumption, never a fresh pickup, never counted as a miss; records a Backlog-to-Planned or Backlog-to-In-Progress transition made while suitable Ready items exist as `ready_bypass`, never entering the SIG-06 count; carries the full §29.4 field set — who, which date, which product, why the queue was empty, whether the Team Lead was blocked, whether product priority changed recently | §97.5, lines 8995–9000; §29.4, lines 2670–2673 | `tools/records/test-rqm-detector.sh` exits 0 and prints `RQM OK 6/6` |
| DoD-9 | RECORD-VERIFICATION-RESULT accepts exactly the structured inputs — product, item, mechanism, pass/fail, evidence link — writes the record and appends the event; no hand-edit path exists | §97.2, line 8884 | `tools/records/test-rvr.sh` exits 0 and prints `RVR OK` |
| DoD-10 | Support records carry `detection_source` including `founder_direct` and `customer`; change records and PR records carry `agent_authored` | §97.2, line 8886 | `tools/records/validate-schemas.sh --fields` prints `NO-NAMES SCHEMAS OK` |
| DoD-11 | The deletion-request record carries the four timestamps `requested`, `verified`, `executed`, `confirmed`, the named executor, the subprocessor propagation checklist and the backup carve-out statement | §97.2, line 8882; AT-105 | `tools/records/validate-schemas.sh --at105` prints `AT-105 OK` _(--at105 mode: added to L4-02 validate-schemas.sh, Session 12)_ |
| DoD-12 | The security-review record carries findings with severity and disposition, and links unfixed findings for the Portfolio Debt Inventory | §97.2, line 8882 | `tools/records/validate-schemas.sh --at046-secreview` prints `SECREVIEW OK` _(--at046-secreview mode: added to L4-02 validate-schemas.sh, Session 12)_ |
| DoD-13 | Every §103 measure computation names the record store it derives from; a measure that cannot name its store is absent | §103 preamble, line 9789; invariant 46, line 9527 | `metrics/register/validate-sources.sh` exits 0 and prints `SOURCES OK` |
| DoD-14 | An empty or not-yet-baselined store renders `unbaselined`, never as a miss | §103 preamble, line 9789 (D77); §52.2, line 4530 | `metrics/register/validate-sources.sh --arming` prints `ARMING OK` |
| DoD-15 | Every §103.13 measure carries a recorded baseline estimate or an explicit `unbaselined` marker | §103.14, lines 9988–9990; AT-046 | `metrics/register/validate-sources.sh --at046` prints `AT-046 OK` |
| DoD-16 | The cross-repository reader fails closed when the records repository is unreachable | §40.1, line 3675 | `tools/records/test-read-across.sh --unreachable` exits non-zero with `FAIL-CLOSED` on stdout |
| DoD-17 | No L4 file appears outside the owned paths of §3 | PARTITION rule 1, line 25 | `tools/records/lane-selfcheck.sh --paths` exits 0 and prints `PATHS OK` |
| DoD-18 | Every event and record timestamp is UTC with offset; no derivation resolves against a runner's local time | §97.1, line 8851 | `tools/records/validate-schemas.sh --time` prints `TIME OK 17` |
| DoD-19 | Retention classes are declared per store; append-only permanence holds for state, decisions, approvals and canonical records; raw activity telemetry declares a diagnostic window | §97.6, lines 9001–9004; invariant 47, line 9528 | `tools/records/validate-retention.sh` exits 0 and prints `RETENTION OK` |
| DoD-20 | Every task in every L4 phase file has merged to `integration` and the full gate passed | PARTITION line 35 | `git log --oneline origin/integration --grep='^L4-' \| wc -l` equals the lane task count |

---

## 8. Spec sections implemented, with line ranges

Every line range below was located in `MultiProduct_MasterSpec_v4.0.md` and is cited, not inferred.

| Spec section | Lines | L4 obligation | Owned path |
|---|---|---|---|
| §6.4 Person availability versus calendar and leave | 446–454 | `records/leave/` store; the declared working calendar and operating timezone that every business-day rule resolves against | `control-plane-records`, `schemas/records/` |
| §22.4 Response targets | 2240–2251 | `records/support/` store shape supporting first-response measurement by severity | `schemas/records/` |
| §29.1 Boards | 2625–2642 | Board convention as machine-checkable configuration: the seven flow columns, Blocked as a flag not a column, Deploy rendered from deployment records | `metrics/`, `tools/records/` |
| §29.2 Three planning horizons | 2643–2654 | H1/H2/H3 semantics; the `unplanned` flag on work entering H1 without H2 preparation | `metrics/attention/` |
| §29.3 Ready-to-Execute definition | 2655–2669 | Estimate capture at Ready confirmation: band label **and** point value in force; elapsed **and** elapsed net of recorded Blocked time | `schemas/records/estimate.schema.json` |
| §29.4 Ready Queue Miss — formal definition | 2670–2673 | The recorded field set: who, which date, which product, why the queue was empty, whether the Team Lead was blocked, whether product priority changed recently | `schemas/records/`, `tools/records/` |
| §29.5 Material requirement change | 2674–2704 | The re-plan event linking to the item's estimate record; Blocked flag with reason `re-plan` | `metrics/taxonomy/` |
| §32 Production Evidence Chain | 2805–2831 | `records/deployments/` as the store the eleven questions are answered from | `schemas/records/` |
| §40.1 Five secret tiers / records-writer / D89 / D107 | 3648–3690 | The two-repository split; append-only enforced by ruleset, signed commits and the head-SHA anchor; no bypass actor | `control-plane-records` (whole repo) |
| §44.2 Restore-testing cadence | 3997–4006 | `records/restore-tests/` supporting the rolling 90-day window and tightened per-product cadence | `schemas/records/` |
| §44.3 The four signals | 4007–4015 | The human integrity confirmation reaching the store through RECORD-VERIFICATION-RESULT | `tools/records/` |
| §52.2 The unified signal table | 4526–4596 | Source-side only: SIG-06, SIG-17, SIG-41, SIG-42, SIG-46 derive from L4 stores; arming discipline (D77) honoured by every L4 computation | `metrics/signals/` |
| §52.6 Registry of control-plane files | 4620–4655 | The `records/` and `events/` row — *"in the records repository, not the control-plane repository"* | `control-plane-records` |
| §53.1 Declared versus actual | 4661–4697 | Publishing the write-freshness windows and the `restore_tested` evidence row that L3 compares against | `metrics/freshness/` |
| §57.2 The OS's own ledger entry | 4965–4970 | The `ritual` flag set by the workflow or record that opens the ritual, never self-reported | `metrics/attention/` |
| §58.4 The incident learning loop | 5026–5056 | `records/postmortems/` and `records/incidents/` as the SIG-47 (unclosed learning-loop items) sources | `schemas/records/` |
| §67.1 The Human Attention Hour | 5580–5585 | Exactly one time-collection mechanism; exactly one category per hour | `metrics/attention/` |
| §67.2 The attention taxonomy | 5586–5604 | The eight categories, the `unplanned` flag, the `ritual` flag; no ninth category, no parallel category set | `metrics/attention/` |
| §97.1 The convention | 8848–8854 | Records generated from the workflow surface, never transcribed; UTC-with-offset; the split write path and the records-writer credential | `control-plane-records`, `tools/records/` |
| §97.2 Canonical record stores | 8855–8939 | Every store, its path convention, its writer, its write-freshness window; the four representative schemas; RECORD-VERIFICATION-RESULT | `control-plane-records`, `schemas/records/` |
| §97.3 The event log | 8940–8966 | One file per event; the binding envelope; the closed `event_type` enum; retire-never-remove | `control-plane-records/events/`, `metrics/taxonomy/` |
| §97.4 Attention-hour derivation | 8967–8994 | The full derivation: per-category sources, activity sessions, idle gap, granularity, precedence, product attribution, daily reconciliation, instrument-defect rule, declared limitations, banded self-report with permanent provenance label | `metrics/attention/` |
| §97.5 Ready-queue-miss recording | 8995–9000 | Both detector limbs, the Planned-column carve-out, the Blocked-resumption carve-out, `ready_bypass` | `tools/records/` |
| §97.6 Retention | 9001–9004 | Retention classes declared in the control plane; append-only permanence for records; diagnostic window for raw activity telemetry | `metrics/`, `schemas/records/` |
| §98.2 Foundation Phases 1–7 | 9019–9103 | The stores and the event-type enum ship populated in Phase 1 so no workflow ever writes an untyped event | all owned paths |
| §99.2 Subsystem architecture (rows I and N) | 9197–9244 | The lane's whole mandate | all owned paths |
| §99.6 Top build risks (risk 2) | 9289–9307 | Build §97 in Foundation, before any dashboard reads from it | all owned paths |
| §100.4 Governance acceptance tests | 9367–9391 | AT-046 (baseline integrity), AT-105 (deletion request inside SLA), AT-107 (eval regression → SIG-42) supplied from L4 stores | `metrics/register/`, `schemas/records/` |
| §101.3 Planning invariants (14–16) | 9481–9486 | Invariant 15: Ready-queue misses trend to zero — measured, never asserted | `tools/records/` |
| §101.7 State and Truth invariants (40–49) | 9519–9531 | Invariant 46 (derived, never hand-maintained), 47 (append-only), 48 (no silent overwrite), 49 (every metric has an owner and a defined response, or it is deleted) | all owned paths |
| §103 Success Metrics and Baselines | 9787–9991 | Every measure's named record store, its eight attributes read from `os-health.yaml`, the `unbaselined` rendering, the §103.14 minimum baseline set | `metrics/register/` |

---

## 9. DECISION REQUIRED — hand to L0

These three questions decide cross-lane ownership. **No L4 executor may answer them.** Each blocks only the task named; everything else proceeds.

### ~~DECISION REQUIRED~~ D-L4-01 — the `event_type` enum publication mechanism

> **Status: Closed (FD-065, 2026-09-06).** L4 source identifiers (the `l4/event-log-records`, `l4/ci-run-records` etc. SIG store paths) are internal aliases, not formal event-type identifiers. At implementation time, verify the 5 SIG store paths map to existing L1 event categories in `platform.yaml`; no new registry entries are needed. `metrics/signals/sig-source-map.yaml` is updated at implementation time to map each SIG row to the corresponding existing L1 event-type identifier. If any store path genuinely has no L1 equivalent, escalate to option (a) for only that specific type.

- **Fact:** §97.3 line 8947 places the closed `event_type` enum in `platform.yaml`. PARTITION.md line 17 gives `registries/**` to L1. PARTITION rule 3 forbids any shared mutable file.
- **Question:** Does L4 publish `metrics/taxonomy/event-types.yaml` for L1 to embed into `platform.yaml`, or does L1 author the enum from the §97.3 taxonomy directly with L4 validating against it?
- **Blocks:** the enum-population task and DoD-4's integration side.
- **L4 must not:** write to `registries/platform.yaml` under any circumstance.

### ~~DECISION REQUIRED~~ D-L4-02 — the metric register content boundary

> **Status: Closed (FD-002 / D-L4-03 → L4-P1-T05/T06).**

- **Fact:** §52.6 line 4626 and §103 preamble line 9776 make `os-health.yaml` the one register for metric metadata. PARTITION.md line 17 gives `registries/**` to L1. The eight attributes of §84.6 (line 7473) are L4-derived content.
- **Question:** Does L4 publish `metrics/register/metric-declarations.yaml` for L1 to embed, or does L1 own the declarations with L4 supplying only the computation?
- **Blocks:** DoD-13, DoD-14, DoD-15 integration.
- **L4 must not:** write to `registries/os-health.yaml` under any circumstance.

### ~~DECISION REQUIRED~~ D-L4-03 — `.github/**` inside `control-plane-records`

> **Status: Closed (FD-002 / D-L4-03 → L4-P1-T05/T06).**

- **Fact:** PARTITION.md line 20 gives L4 *"ALL of `control-plane-records`"*. PARTITION.md line 18 gives L2 `.github/workflows/**`. The D107 ruleset (§40.1, line 3675) is repository configuration on `control-plane-records`.
- **Question:** Inside `control-plane-records`, does the repo-level grant to L4 cover `.github/**` (including a committed ruleset JSON), or does L2's path pattern reach across repositories?
- **Blocks:** `L4-P1-T05` and `L4-P1-T06`.
- **L4 default until answered:** create no file under `control-plane-records/.github/` and record the ruleset requirement as a note in the repository README for L0.

---

## 10. Charter tasks

Seven tasks. Each is mechanical. None requires designing, choosing or interpreting.

### Fixed workspace convention (binding for this lane)

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
export L4_CHARTER="C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L4-00-charter.md"
```

Re-export these at the start of every task. The Bash tool resets the working directory between calls; always use absolute paths.

---

### L4-T001 — Preflight and lane branch

**Size:** S
**Depends on:** none

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
test -d "$CP_ROOT/.git" || { echo "PREFLIGHT FAIL: control-plane repo missing"; exit 1; }
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" rev-parse --verify origin/integration
git -C "$CP_ROOT" status --porcelain
git -C "$CP_ROOT" checkout -B lane/4/00-charter-preflight origin/integration
git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD
test -d "$CP_ROOT/contracts" && echo "CONTRACTS PRESENT" || echo "CONTRACTS ABSENT"
ls "$CP_ROOT/registries/platform.yaml" >/dev/null 2>&1 && echo "L1 PLATFORM PRESENT" || echo "L1 PLATFORM ABSENT"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | `control-plane` is a git repo | `test -d "$CP_ROOT/.git" && echo YES` | `YES` |
| 2 | `origin/integration` exists | `git -C "$CP_ROOT" rev-parse --verify origin/integration` | a 40-character SHA |
| 3 | Working tree clean before branching | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 4 | Branch created off `origin/integration` | `git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD` | `lane/4/00-charter-preflight` |
| 5 | `contracts/` present (L0 Phase 0 complete) | `test -d "$CP_ROOT/contracts" && echo YES` | `YES` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
echo "BRANCH=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l)"
echo "CONTRACTS=$(test -d "$CP_ROOT/contracts" && echo yes || echo no)"
```

Expected output, exactly:

```
BRANCH=lane/4/00-charter-preflight
DIRTY=0
CONTRACTS=yes
```

**STOP rule** — if `CONTRACTS=no`, or `origin/integration` does not resolve, or `DIRTY` is not `0`: do not proceed, do not create any file, open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T001 preflight failed"
lane: L4
task_id: L4-T001
blocked_by: "<contracts/ absent | origin/integration missing | working tree dirty>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "BRANCH=lane/4/00-charter-preflight / DIRTY=0 / CONTRACTS=yes"
spec_ref: "PARTITION.md lines 26, 34"
needs: "L0"
action_taken: none
```

---

### L4-T002 — Records repository skeleton (WITHDRAWN)

**Status: WITHDRAWN.** Superseded by `L4-P1-T02` through `L4-P1-T06` in `lanes/L4-01`. Do not execute.

### L4-T003 — Protection requirement declared for L0 (WITHDRAWN)

**Status: WITHDRAWN.** Superseded by `L4-P1-T02` through `L4-P1-T06` in `lanes/L4-01`. Do not execute.

---

### L4-T004 — Scaffold the three owned control-plane directories

**Size:** S
**Depends on:** L4-T001

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
git -C "$CP_ROOT" checkout lane/4/00-charter-preflight
mkdir -p "$CP_ROOT/schemas/records" \
         "$CP_ROOT/metrics/taxonomy" "$CP_ROOT/metrics/attention" \
         "$CP_ROOT/metrics/freshness" "$CP_ROOT/metrics/signals" \
         "$CP_ROOT/metrics/register" "$CP_ROOT/metrics/anchor" \
         "$CP_ROOT/tools/records/fixtures"
printf 'schemas/records — JSON Schemas for every record store of Master Spec v4.0 Section 97.2\n(lines 8843-8926) and for the Section 97.3 event envelope (lines 8927-8953).\nOwner: lane L4 (PARTITION.md line 20).\n' > "$CP_ROOT/schemas/records/README.md"
printf 'metrics — Subsystem I. Event taxonomy, attention ledger, write-freshness windows,\nSIG source map, metric register content, records-head anchor format.\nMaster Spec v4.0 Sections 97.3-97.4 and Section 103 (lines 9774-9978).\nOwner: lane L4 (PARTITION.md line 20).\n' > "$CP_ROOT/metrics/README.md"
printf 'tools/records — record and event writers, the RECORD-VERIFICATION-RESULT handler,\nvalidators, fixtures, the Ready-queue-miss detector, the lane self-check.\nMaster Spec v4.0 Sections 97.2 (line 8886) and 97.5 (lines 8982-8987).\nOwner: lane L4 (PARTITION.md line 20).\n' > "$CP_ROOT/tools/records/README.md"
git -C "$CP_ROOT" add schemas/records metrics tools/records
git -C "$CP_ROOT" commit -m "L4-T004: scaffold owned control-plane paths for subsystems I and N"
git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | sort
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Three README files exist | `ls "$CP_ROOT"/schemas/records/README.md "$CP_ROOT"/metrics/README.md "$CP_ROOT"/tools/records/README.md \| wc -l` | `3` |
| 2 | Every changed path is L4-owned | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/records/|metrics/|tools/records/)'` | `0` |
| 3 | Each README cites PARTITION.md line 20 | `grep -l "PARTITION.md line 20" "$CP_ROOT"/schemas/records/README.md "$CP_ROOT"/metrics/README.md "$CP_ROOT"/tools/records/README.md \| wc -l` | `3` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
echo "READMES=$(ls "$CP_ROOT"/schemas/records/README.md "$CP_ROOT"/metrics/README.md "$CP_ROOT"/tools/records/README.md 2>/dev/null | wc -l)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
echo "CHANGED=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
READMES=3
FOREIGN=0
CHANGED=3
```

**STOP rule** — if `FOREIGN` is not `0`: a foreign path was touched and the lane-guard check will fail the PR. Do not push, do not `git add` anything further, open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T004 foreign path in lane/4 branch"
lane: L4
task_id: L4-T004
blocked_by: "foreign path touched"
observed: "<paste the exact SELF-VERIFY output and the output of git diff --name-only origin/integration...HEAD>"
expected: "READMES=3 / FOREIGN=0 / CHANGED=3"
spec_ref: "PARTITION.md lines 20, 25"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T005 — Lane path-ownership self-check script

**Size:** M
**Depends on:** L4-T004

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/lane-selfcheck.sh" <<'EOF'
#!/usr/bin/env bash
# L4 lane self-check. PARTITION.md line 20 owned paths only.
# Usage: lane-selfcheck.sh --paths | --coverage | --stores
set -u
OWNED='^(schemas/records/|metrics/|tools/records/)'
BASE="${LANE_BASE:-origin/integration}"
case "${1:-}" in
  --paths)
    foreign="$(git diff --name-only "$BASE"...HEAD | grep -vE "$OWNED" | wc -l | tr -d ' ')"
    if [ "$foreign" = "0" ]; then echo "PATHS OK"; exit 0; fi
    echo "PATHS FAIL foreign=$foreign"
    git diff --name-only "$BASE"...HEAD | grep -vE "$OWNED"
    exit 1
    ;;
  --coverage)
    FCOUNT=$(find "C:/D_Drive/PS/MultiProduct/Code/implementation/metrics" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "L4-COVERAGE OK files=$FCOUNT"
    exit 0
    ;;
  *)
    echo "usage: lane-selfcheck.sh --paths | --coverage"; exit 2
    ;;
esac
EOF
chmod +x "$CP_ROOT/tools/records/lane-selfcheck.sh"
git -C "$CP_ROOT" add tools/records/lane-selfcheck.sh
git -C "$CP_ROOT" commit -m "L4-T005: lane path-ownership and store-count self-check"
cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x "$CP_ROOT/tools/records/lane-selfcheck.sh" && echo YES` | `YES` |
| 2 | `--paths` passes on the current branch | `cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths` | `PATHS OK`, exit 0 |
| 3 | `--paths` fails on a seeded foreign path | see SELF-VERIFY negative test | `PATHS FAIL foreign=1`, exit 1 |

**SELF-VERIFY** (includes the mandatory negative test — a check that cannot fail is not a check, §53.1 seeded-canary rule, line 4685)

```bash
set -e
export CP_ROOT="$HOME/src/control-plane"
cd "$CP_ROOT"
echo "POSITIVE=$(./tools/records/lane-selfcheck.sh --paths)"
echo x > "$CP_ROOT/docs/_L4-SEED-CANARY.txt"
git -C "$CP_ROOT" add docs/_L4-SEED-CANARY.txt
git -C "$CP_ROOT" commit -q -m "SEEDED negative test - to be reverted"
echo "NEGATIVE=$(./tools/records/lane-selfcheck.sh --paths | head -1)"
git -C "$CP_ROOT" reset --mixed HEAD~1 && rm -f "$CP_ROOT/docs/_L4-SEED-CANARY.txt"
echo "REVERTED=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -c '^docs/_L4-SEED-CANARY')"
```

Expected output, exactly:

```
POSITIVE=PATHS OK
NEGATIVE=PATHS FAIL foreign=1
REVERTED=0
```

**STOP rule** — if `NEGATIVE` is not `PATHS FAIL foreign=1`, the check cannot detect a violation and is worthless; if `REVERTED` is not `0`, the seeded file is still on the branch. In either case do not push, open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T005 self-check negative test did not fail, or seed not reverted"
lane: L4
task_id: L4-T005
blocked_by: "<negative test passed when it must fail | seeded file still present>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "POSITIVE=PATHS OK / NEGATIVE=PATHS FAIL foreign=1 / REVERTED=0"
spec_ref: "PARTITION.md line 25; Master Spec v4.0 Section 53.1 seeded-canary rule, line 4685"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T006 — Machine-readable spec-coverage manifest

**Size:** M
**Depends on:** L4-T004

Transcribe the §8 table of this charter into `metrics/register/l4-spec-coverage.csv`. Copy the rows exactly as given; do not add rows, do not omit rows, do not alter line ranges.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/metrics/register/l4-spec-coverage.csv" <<'EOF'
section,line_start,line_end,owned_path
6.4,446,454,control-plane-records/records/leave
22.4,2240,2251,schemas/records
29.1,2625,2642,metrics
29.2,2643,2654,metrics/attention
29.3,2655,2669,schemas/records
29.4,2670,2673,tools/records
29.5,2674,2704,metrics/taxonomy
32,2805,2831,schemas/records
40.1,3648,3690,control-plane-records
44.2,3997,4006,schemas/records
44.3,4007,4015,tools/records
52.2,4526,4596,metrics/signals
52.6,4620,4655,control-plane-records
53.1,4661,4697,metrics/freshness
57.2,4965,4970,metrics/attention
58.4,5026,5056,schemas/records
67.1,5580,5585,metrics/attention
67.2,5586,5604,metrics/attention
97.1,8848,8854,tools/records
97.2,8855,8939,schemas/records
97.3,8940,8966,metrics/taxonomy
97.4,8967,8994,metrics/attention
97.5,8995,9000,tools/records
97.6,9001,9004,schemas/records
98.2,9019,9103,metrics
99.2,9197,9244,metrics
99.6,9289,9307,metrics
100.4,9367,9391,metrics/register
101.3,9481,9486,tools/records
101.7,9519,9531,metrics
103,9787,9991,metrics/register
EOF
git -C "$CP_ROOT" add metrics/register/l4-spec-coverage.csv
git -C "$CP_ROOT" commit -m "L4-T006: machine-readable L4 spec coverage manifest"
awk -F, 'NR>1 && $2+0 <= $3+0 {ok++} END {print "ROWS="NR-1" ORDERED="ok}' "$CP_ROOT/metrics/register/l4-spec-coverage.csv"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | 31 data rows | `awk 'NR>1' "$CP_ROOT/metrics/register/l4-spec-coverage.csv" \| wc -l` | `31` |
| 2 | Every row has `line_start <= line_end` | `awk -F, 'NR>1 && $2+0 > $3+0' "$CP_ROOT/metrics/register/l4-spec-coverage.csv" \| wc -l` | `0` |
| 3 | Every `line_end` is within the spec | `awk -F, 'NR>1 && $3+0 > 10214' "$CP_ROOT/metrics/register/l4-spec-coverage.csv" \| wc -l` | `0` |
| 4 | Every `owned_path` is an L4 path | `awk -F, 'NR>1' "$CP_ROOT/metrics/register/l4-spec-coverage.csv" \| cut -d, -f4 \| grep -vcE '^(schemas/records|metrics|tools/records|control-plane-records)'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
F="$CP_ROOT/metrics/register/l4-spec-coverage.csv"
echo "ROWS=$(awk 'NR>1' "$F" | wc -l | tr -d ' ')"
echo "BADRANGE=$(awk -F, 'NR>1 && $2+0 > $3+0' "$F" | wc -l | tr -d ' ')"
echo "OVERFLOW=$(awk -F, 'NR>1 && $3+0 > 10214' "$F" | wc -l | tr -d ' ')"
echo "FOREIGNPATH=$(awk -F, 'NR>1' "$F" | cut -d, -f4 | grep -vcE '^(schemas/records|metrics|tools/records|control-plane-records)')"
```

Expected output, exactly:

```
ROWS=31
BADRANGE=0
OVERFLOW=0
FOREIGNPATH=0
```

**STOP rule** — if `ROWS` is not `31`, or any other value is not `0`: the manifest does not match this charter's §8 table. Do not edit the line ranges to make it pass. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T006 coverage manifest does not match charter section 8"
lane: L4
task_id: L4-T006
blocked_by: "manifest/charter mismatch"
observed: "<paste the exact SELF-VERIFY output>"
expected: "ROWS=31 / BADRANGE=0 / OVERFLOW=0 / FOREIGNPATH=0"
spec_ref: "Code/implementation/lanes/L4-00-charter.md section 8"
needs: "L0"
action_taken: "manifest committed unmodified; no line range altered"
```

---

### L4-T007 — Rebase and open the lane PR to `integration`

**Size:** S
**Depends on:** L4-T004, L4-T005, L4-T006

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" rebase origin/integration
cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths
git -C "$CP_ROOT" push -u origin lane/4/00-charter-preflight
gh pr create --base integration --head lane/4/00-charter-preflight \
  --title "L4-00: lane charter scaffold (subsystems I, N)" \
  --body "L4 charter tasks L4-T001..L4-T006. Owned paths only: schemas/records/**, metrics/**, tools/records/**. Records repository skeleton created separately per PARTITION.md line 20. Open decisions for L0: D-L4-01, D-L4-02, D-L4-03 (see Code/implementation/lanes/L4-00-charter.md section 9)."
gh pr view --json number,baseRefName,headRefName
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Branch rebased onto current `origin/integration` | `git -C "$CP_ROOT" merge-base --is-ancestor origin/integration HEAD && echo YES` | `YES` |
| 2 | `--paths` passes after rebase | `cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |
| 3 | PR base is `integration` | `cd "$CP_ROOT" && gh pr view --json baseRefName -q .baseRefName` | `integration` |
| 4 | PR head is the lane branch | `cd "$CP_ROOT" && gh pr view --json headRefName -q .headRefName` | `lane/4/00-charter-preflight` |
| 5 | No other lane's branch was touched | `git -C "$CP_ROOT" reflog --date=short \| grep -cE 'lane/(1|2|3|5)/'` | `0` |

**SELF-VERIFY**

```bash
set -e
export CP_ROOT="$HOME/src/control-plane"
cd "$CP_ROOT"
echo "REBASED=$(git merge-base --is-ancestor origin/integration HEAD && echo yes || echo no)"
echo "PATHS=$(./tools/records/lane-selfcheck.sh --paths)"
echo "BASE=$(gh pr view --json baseRefName -q .baseRefName)"
echo "HEAD=$(gh pr view --json headRefName -q .headRefName)"
echo "OTHERLANES=$(git reflog --date=short | grep -cE 'lane/(1|2|3|5)/')"
```

Expected output, exactly:

```
REBASED=yes
PATHS=PATHS OK
BASE=integration
HEAD=lane/4/00-charter-preflight
OTHERLANES=0
```

**STOP rule** — if `REBASED=no`, or `PATHS` is not `PATHS OK`, or `OTHERLANES` is not `0`: do not force-push, do not resolve another lane's conflict, do not merge. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T007 lane PR preconditions failed"
lane: L4
task_id: L4-T007
blocked_by: "<rebase failed | foreign path present | another lane's branch touched>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "REBASED=yes / PATHS=PATHS OK / BASE=integration / HEAD=lane/4/00-charter-preflight / OTHERLANES=0"
spec_ref: "PARTITION.md lines 32-36"
needs: "L0"
action_taken: "no force-push, no merge, no other-lane branch modified"
```

---

## 11. Task summary

| Task ID | Title | Size | Depends on | Owned paths written |
|---|---|---|---|---|
| L4-T001 | Preflight and lane branch | S | — | none (branch only) |
| ~~L4-T002~~ | ~~Records repository skeleton~~ | ~~M~~ | ~~L4-T001~~ | Withdrawn — moved to `lanes/L4-01` (L4-P1-T02 through L4-P1-T06) |
| ~~L4-T003~~ | ~~Protection requirement declared for L0~~ | ~~S~~ | ~~L4-T002~~ | Withdrawn — moved to `lanes/L4-01` (L4-P1-T02 through L4-P1-T06) |
| L4-T004 | Scaffold owned control-plane directories | S | L4-T001 | `schemas/records/`, `metrics/`, `tools/records/` |
| L4-T005 | Lane path-ownership self-check | M | L4-T004 | `tools/records/lane-selfcheck.sh` |
| L4-T006 | Spec-coverage manifest | M | L4-T004 | `metrics/register/l4-spec-coverage.csv` |
| L4-T007 | Rebase and open lane PR | S | T004–T006 | none (git only) |

---

## 12. Standing rules for every L4 executor

1. **Write only the owned paths of §3.** Run `tools/records/lane-selfcheck.sh --paths` before every commit and before every push.
2. **Never edit `contracts/**`.** A needed contract change is a Contract Change Request to L0 (PARTITION rule 2).
3. **Never append to a shared file.** One file per record, one file per event, one file per schema (PARTITION rule 3; §97.3 line 8929).
4. **Never reach into another lane's source tree.** Consume through `contracts/**` or a published artifact only (PARTITION rule 4).
5. **Prefer a new file to editing an existing one**, and edit only inside owned paths (PARTITION rule 5).
6. **Never merge or rebase another lane's branch** (PARTITION line 36).
7. **Records are never edited in place.** Corrections are follow-up records (§97.2, line 8890). This applies to fixtures and examples too.
8. **Every timestamp is UTC with its offset** (§97.1, line 8839).
9. **If a task would require choosing, designing or interpreting, STOP** and raise it to L0 as a DECISION REQUIRED using the §9 format. Do not guess.
10. **A check that cannot fail is not a check.** Every validator L4 ships carries a negative test, per the seeded-canary philosophy of §53.1 (line 4685) and §95.4.
