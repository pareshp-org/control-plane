# L4-CONCORDANCE — Lane 4 task-id concordance

**Purpose.** Lane 4 carries two peer decompositions of itself under disjoint id namespaces with no
mapping in either direction. This file is that mapping. It is **additive**: it edits no task file,
authors no task body, and invalidates no existing citation to either namespace. Published under
**FD-004** (`_FOUNDER_DECISIONS.md`): *publish a concordance, do not reissue the indexes.*

**Status:** the six lane coherence reviews return BLOCKED on exactly this defect. This file closes
the L4 half of it.

---

## 0. Files measured, as they are on disk today

Measured 2026-09-02. Every count below is checkable against these exact copies.

```
wc -l L4-0*.md   (in C:/D_Drive/PS/MultiProduct/Code/implementation/lanes)
```

| File | `wc -l` | Side | Task ids it carries |
| --- | ---: | --- | --- |
| `L4-06-tasks.md` | **674** | INDEX | 117 ids, in a markdown **table** (§2, lines 253–371). No `###` task heading anywhere — heading-only greps report zero. |
| `L4-00-charter.md` | **797** | BODY | `L4-T001` … `L4-T007` (7) |
| `L4-01-records-repo.md` | **1559** | BODY | `L4-P1-T01` … `L4-P1-T12` (12) |
| `L4-02-record-schemas.md` | **3867** | BODY | `L4-T201` … `L4-T225` (25) |
| `L4-03-write-paths.md` | **2434** | BODY | `L4-T301` … `L4-T316` (16) |
| `L4-04-attention-ledger.md` | **3654** | BODY | `L4-T401` … `L4-T418` (18) |
| `L4-05-pipeline-and-boards.md` | **3699** | BODY | `L4-P5-01`…`04`, `L4-P5-14`…`24` (15) |
| `L4-07-tests-and-runbook.md` | **2212** | BODY | `L4-P7-T01` … `L4-P7-T14` (14) |
| | **18896** | | |

---

## 1. Headline numbers

| Quantity | Count |
| --- | ---: |
| Distinct task ids the **index** promises (`L4-06-tasks.md`) | **117** |
| Distinct task ids with an actual **body** anywhere in the lane | **107** |
| Index ids **confidently mapped** to a body | **103** |
| Index ids with **no body anywhere** — the residue, the true unbuilt work | **14** |
| Distinct bodies consumed by those 103 mappings | 87 |
| Bodies **no index row claims** — orphans, work that will be done but is tracked nowhere | **41** |

The mapping is many-to-one in both directions by construction: one body can discharge several index
rows (`L4-T305` discharges five), and one index row can be discharged by a pair of bodies
(`L4-P2-13` by `L4-T212` + `L4-T213`).

### 1.1 The structural cause of most of the residue

Twenty-one of the thirty-five residue ids (`L4-P3-06` and all twenty of index Phase 7) are the
**metric register**, and they are unbuilt for one reason: **Lane 4 has no metric-register phase
document.** The lane runs `L4-00` … `L4-05` and `L4-07`; the `L4-06` slot is taken by the tasks
file. The lane says so itself, in `L4-04-attention-ledger.md` line 74, in a table of paths this
phase must not write:

| Path | Owner document | Task |
| --- | --- | --- |
| `metrics/register/**`, `metrics/signals/**` | the metric-register phase | — |

The owner column names a document that does not exist and the task column is empty. `L4-T414`
(line 2571) makes the same disclaimer explicitly: it declares the attention ledger's own eleven
outputs and states it *is not* `metrics/register/metric-declarations.yaml`, *"which belongs to the
metric-register phase"*. Meanwhile `L4-P7-T01` (the tests phase entry gate, line 294) requires
`metrics/register/metric-declarations.yaml` and `metrics/register/validate-sources.sh` to be
`PRESENT` with `ABSENT=0` before a single test is written — so Phase 7's absence stops the tests
phase at its own gate. This is a hard dispatch blocker, not a bookkeeping gap.

### 1.2 A namespace collision that will cause misdispatch

`L4-P7-01` … `L4-P7-20` (index: the metric register) and `L4-P7-T01` … `L4-P7-T14`
(body: tests and runbook) differ **by one character** and are entirely different work. An executor
handed "L4-P7-01" cannot tell which is meant. Any dispatch tooling must treat the literal `T` as
significant. No other L4 namespace pair collides.

---

## 2. Mapping table — index id → body

Confidence: **HIGH** = the body's artifact, acceptance criteria and spec anchors match the index
row's; **MED** = the substance is present but the scope or the artifact count differs, noted per row.

### Phase 0 — lane bootstrap (identity: index and body share the namespace)

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-T001 | L4-T001 | L4-00-charter.md | 248 | HIGH | Preflight and lane branch |
| L4-T002 | L4-T002 | L4-00-charter.md | 309 | HIGH | Records repository skeleton |
| L4-T003 | L4-T003 | L4-00-charter.md | 384 | HIGH | Protection requirement declared for L0 |
| L4-T004 | L4-T004 | L4-00-charter.md | 457 | HIGH | Scaffold the three owned control-plane directories |
| L4-T005 | L4-T005 | L4-00-charter.md | 519 | HIGH | Lane path-ownership self-check script |
| L4-T006 | L4-T006 | L4-00-charter.md | 612 | HIGH | Machine-readable spec-coverage manifest |
| L4-T007 | L4-T007 | L4-00-charter.md | 705 | HIGH | Rebase and open the Phase 0 lane PR |

### Phase 1 — the records repository (identity)

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P1-T01 | L4-P1-T01 | L4-01-records-repo.md | 151 | HIGH | Preflight and parameter binding |
| L4-P1-T02 | L4-P1-T02 | L4-01-records-repo.md | 228 | HIGH | Create `control-plane-records` |
| L4-P1-T03 | L4-P1-T03 | L4-01-records-repo.md | 292 | HIGH | Directory-per-item skeleton |
| L4-P1-T04 | L4-P1-T04 | L4-01-records-repo.md | 398 | HIGH | Root documents: README, CONVENTIONS, .gitignore |
| L4-P1-T05 | L4-P1-T05 | L4-01-records-repo.md | 614 | HIGH | Arm the no-bypass branch ruleset |
| L4-P1-T06 | L4-P1-T06 | L4-01-records-repo.md | 701 | HIGH | Arm the no-bypass tag ruleset |
| L4-P1-T07 | L4-P1-T07 | L4-01-records-repo.md | 779 | HIGH | Prove rewriting blocked, appending permitted |
| L4-P1-T08 | L4-P1-T08 | L4-01-records-repo.md | 888 | HIGH | Add `required_signatures` and prove it |
| L4-P1-T09 | L4-P1-T09 | L4-01-records-repo.md | 994 | HIGH | Create the `records-writer` GitHub App |
| L4-P1-T10 | L4-P1-T10 | L4-01-records-repo.md | 1094 | HIGH | Install and scope the App to the records repo alone |
| L4-P1-T11 | L4-P1-T11 | L4-01-records-repo.md | 1219 | HIGH | Prove the App appends here and reaches no registry |
| L4-P1-T12 | L4-P1-T12 | L4-01-records-repo.md | 1328 | HIGH | Store ruleset and credential shape as code |

### Phase 2 — record and event schemas (cross-namespace)

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P2-02 | L4-T201 | L4-02-record-schemas.md | 216 | HIGH | Toolchain preflight; pins `jsonschema==4.23.0`, `PyYAML==6.0.2` — the index's `requirements.txt` pinning rule |
| L4-P2-03 | L4-T202 | L4-02-record-schemas.md | 288 | HIGH | UTC-with-offset definition: `$defs.timestamp_utc` + the `NEGTIME` negative that rejects a naive local time |
| L4-P2-04 | L4-T202 | L4-02-record-schemas.md | 288 | HIGH | Record envelope base — index calls it `record.envelope.schema.json`, body writes `record.base.schema.json`; same four required fields, §97.2 line 8890 |
| L4-P2-05 | L4-T204 | L4-02-record-schemas.md | 741 | HIGH | `event.envelope.schema.json`, the nine binding fields, plus the generated `event-type.enum.json` |
| L4-P2-06 | L4-T223 | L4-02-record-schemas.md | 3166 | HIGH | Store inventory — index calls it `store-inventory.yaml`, body writes `store-map.yaml`; 19 rows = the 17 §97.2 stores + `events/` + `bootstrap/` <!-- 19 per FD-059 (bootstrap/ counts as a store) --> |
| L4-P2-07 | L4-T206 | L4-02-record-schemas.md | 1301 | HIGH | `incident.schema.json` |
| L4-P2-08 | L4-T207 | L4-02-record-schemas.md | 1413 | HIGH | `postmortem.schema.json` |
| L4-P2-09 | L4-T208 | L4-02-record-schemas.md | 1536 | HIGH | `uat.schema.json` |
| L4-P2-10 | L4-T209 | L4-02-record-schemas.md | 1632 | HIGH | `estimate.schema.json` — band, point value, `elapsed`, `elapsed_net_blocked` |
| L4-P2-11 | L4-T210 | L4-02-record-schemas.md | 1731 | HIGH | `deployment.schema.json` |
| L4-P2-12 | L4-T211 | L4-02-record-schemas.md | 1841 | HIGH | `restore-test.schema.json` |
| L4-P2-13 | L4-T212 **+** L4-T213 | L4-02-record-schemas.md | 1942, 2047 | HIGH | `decision.schema.json` **and** `decision-pending.schema.json` — the index row names the `pending` sub-store state, so both bodies discharge it |
| L4-P2-14 | L4-T214 | L4-02-record-schemas.md | 2139 | HIGH | `breach.schema.json` |
| L4-P2-15 | L4-T215 | L4-02-record-schemas.md | 2252 | HIGH | `deletion-request.schema.json` (AT-105) |
| L4-P2-16 | L4-T216 | L4-02-record-schemas.md | 2378 | HIGH | `security-review.schema.json` |
| L4-P2-17 | L4-T217 | L4-02-record-schemas.md | 2499 | HIGH | `eval.schema.json` (SIG-42) |
| L4-P2-18 | L4-T218 | L4-02-record-schemas.md | 2622 | HIGH | `launch.schema.json` |
| L4-P2-19 | L4-T219 | L4-02-record-schemas.md | 2743 | HIGH | `demo.schema.json` |
| L4-P2-20 | L4-T220 | L4-02-record-schemas.md | 2835 | HIGH | `support.schema.json` — `detection_source` open set, `received_at` anchor |
| L4-P2-21 | L4-T221 | L4-02-record-schemas.md | 2943 | HIGH | `onboarding.schema.json` |
| L4-P2-22 | L4-T222 | L4-02-record-schemas.md | 3042 | HIGH | `leave.schema.json` — working calendar, operating timezone |
| L4-P2-24 | L4-P7-T12 | L4-07-tests-and-runbook.md | 1666 | **MED** | AT-105 conformance. Body builds `fixtures/negative/at105/` removing each of the four timestamps in turn **plus** an SLA-breach case. Index asks for **six** negatives incl. missing executor / checklist / carve-out; body ships five and only four of the index's six. Substance matches, coverage is short — scope this as a top-up, not new work. |
| L4-P2-25 | L4-T216 | L4-02-record-schemas.md | 2378 | **MED** | Security-review unfixed-finding linkage. The body encodes the rule in the schema (findings require severity + disposition; unfixed requires owner and date); there is **no** separate `asserts/secreview.py` module and no `--at046-secreview` mode. |
| L4-P2-26 | L4-P7-T04 | L4-07-tests-and-runbook.md | 631 | HIGH | Golden valid fixtures, one per store — body: "the writer-generated valid corpus, **all 19 stores**" | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| L4-P2-27 | L4-P7-T06 | L4-07-tests-and-runbook.md | 807 | HIGH | The ten envelope negatives: nine missing-field cases `EN-01`…`EN-09` + `EN-10` free-text `event_type`. Exactly the index's 9+1. (`L4-T224` also prints `--negative 10/10` but proves ten *different*, rule-level cases — see orphans.) |
| L4-P2-29 | L4-T223 | L4-02-record-schemas.md | 3166 | HIGH | Full schema sweep — `validate-schemas.sh --all` over `--coverage/--lint/--fields/--time` + fixture sweep |

### Phase 3 — taxonomy (cross-namespace)

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P3-01 | L4-T203 | L4-02-record-schemas.md | 507 | HIGH | `metrics/taxonomy/event-types.yaml`, the closed 89-identifier enum (D114-D / REG-021), one id per §97.3 tracked event |
| L4-P3-03 | L4-T203 | L4-02-record-schemas.md | 507 | HIGH | Retire-never-remove and `validate-taxonomy.sh` — the validator is written inside `L4-T203` (line 634); the retirement rule is stated at lines 531 and 538 (`retired: true` stays, never removed) |
| L4-P3-06 | L4-P3-06 | L4-03-metric-register.md | 46 | HIGH | Metric-register bootstrap: `metrics/register/metric-declarations.yaml` skeleton, `metrics/register/validate-sources.sh`, and `metrics/signals/sig-source-map.yaml` (SIG-06/17/41/42/46 source map) |

### Phase 4 — writers and the dispatch handler (cross-namespace)

`L4-T305` is the single emission library and is declared *"the **only** code in the estate that
writes a record file or an event file"*. It enforces UTC-with-offset (§97.1 8839), the record
envelope (§97.2 8890), the closed `event_type` enum (§97.3 8947) and no-silent-overwrite
(invariant 48, 9516), and creates `record-write` / `event-append` as thin front-ends. It therefore
discharges five index rows.

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P4-01 | L4-T305 | L4-03-write-paths.md | 745 | HIGH | Writer library — UTC clock, id minting, path resolution |
| L4-P4-02 | L4-T305 | L4-03-write-paths.md | 745 | HIGH | No-overwrite guard, invariant 48 — enforced in the same library |
| L4-P4-03 | L4-T305 | L4-03-write-paths.md | 745 | HIGH | `record-write`: validate via `lib/validate_instance.py`, then append one record file |
| L4-P4-04 | L4-T305 | L4-03-write-paths.md | 745 | **MED** | Event id and date-partition path convention. The library owns event path resolution, but the body does not restate the `events/<YYYY-MM-DD>/<event_id>.yaml` shape as its own acceptance criterion the way the index row does. |
| L4-P4-05 | L4-T305 | L4-03-write-paths.md | 745 | HIGH | `event-append` — envelope and enum rejection at write time |
| L4-P4-06 | L4-T306 | L4-03-write-paths.md | 990 | HIGH | The RECORD-VERIFICATION-RESULT handler (charter DoD-9) |
| L4-P4-09 | L4-T315 | L4-03-write-paths.md | 2133 | HIGH | Writer negative suite — `validate-human-record.sh` rejects hand-authored files in machine stores, in-place edits (`M`/`R`) and deletions (`D`) |

### Phase 5 — boards and the Ready-queue-miss detector

Index rows `L4-P5-01`…`04` are identity matches in `L4-05`. Rows `L4-P5-05`…`11` — the whole RQM
detector — live in `L4-04-attention-ledger.md`, not in the boards file, as `L4-T416` (the contract,
rules `C1`…`C7`) and `L4-T417` (`rqm-detect`, which reads those rules and never declares its own).

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P5-01 | L4-P5-01 | L4-05-pipeline-and-boards.md | 444 | HIGH | Board conventions — seven columns, Blocked as a flag, Deploy rendered |
| L4-P5-02 | L4-P5-02 | L4-05-pipeline-and-boards.md | 699 | HIGH | Horizon semantics H1/H2/H3 and the `unplanned` rule |
| L4-P5-03 | L4-P5-03 | L4-05-pipeline-and-boards.md | 884 | HIGH | Ready-to-Execute as machine-checkable configuration |
| L4-P5-04 | L4-P5-04 | L4-05-pipeline-and-boards.md | 1100 | HIGH | Estimate capture at Ready confirmation (D79) |
| L4-P5-05 | L4-T416 | L4-04-attention-ledger.md | 3060 | HIGH | RQM contract and the §29.4 field set — `rqm-contract.yaml`, the detector's rule source |
| L4-P5-06 | L4-T417 | L4-04-attention-ledger.md | 3225 | HIGH | Limb 1, pickup without Ready — contract rule `C5` `pickup_without_ready`, `counts_in_sig06: true` |
| L4-P5-07 | L4-T417 | L4-04-attention-ledger.md | 3225 | HIGH | Limb 2, completion with an empty Ready queue — rule `C3`, `counts_in_sig06: true` |
| L4-P5-08 | L4-T416 | L4-04-attention-ledger.md | 3060 | HIGH | Planned-column carve-out — rule `C2` `normal_assignment`, Ready→Planned→In Progress is never a miss |
| L4-P5-09 | L4-T416 | L4-04-attention-ledger.md | 3060 | HIGH | Blocked-resumption carve-out — rule `C1` `resumption`, ordered first so a resumption always wins |
| L4-P5-10 | L4-T416 | L4-04-attention-ledger.md | 3060 | HIGH | `ready_bypass` — rule `C6`, recorded as board hygiene, `counts_in_sig06: false`; asserted by SELF-VERIFY `BYPASS=False` |
| L4-P5-11 | L4-T417 | L4-04-attention-ledger.md | 3225 | HIGH | Cause-prompt fields supplied never inferred — `CAUSE_KEYS`, asserted by SELF-VERIFY `FIELDSET=SUBSET 3` |
| L4-P5-12 | L4-P7-T10 | L4-07-tests-and-runbook.md | 1377 | HIGH | RQM acceptance harness. `L4-04` §2.1 line 74 names `L4-P7-T10` as the owner of `tools/records/test-rqm-detector.sh` and `fixtures/rqm/**` — the index's exact files. Charter DoD-8 is that suite's `RQM OK 6/6`. |

### Phase 6 — the attention ledger (cross-namespace)

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P6-01 | L4-T402 | L4-04-attention-ledger.md | 360 | HIGH | The eight-category taxonomy artifact, and nothing else |
| L4-P6-02 | L4-T403 | L4-04-attention-ledger.md | 496 | HIGH | The per-category derivation source map |
| L4-P6-03 | L4-T407 **+** L4-T404 | L4-04-attention-ledger.md | 1274, 660 | HIGH | Activity-session builder and the idle gap (DR-1/DR-2); the calibrated `idle_gap_minutes: 30` lives in `calibration.yaml` (`L4-T404`) — index calls that file `calibrated.yaml` |
| L4-P6-04 | L4-T407 | L4-04-attention-ledger.md | 1274 | HIGH | Attribution granularity — `granularity_hours: 0.25`, rounded to nearest, never to zero (DR-4) |
| L4-P6-05 | L4-T408 | L4-04-attention-ledger.md | 1474 | HIGH | Category precedence order (DR-5) |
| L4-P6-06 | L4-T409 | L4-04-attention-ledger.md | 1593 | HIGH | Product attribution — one, several, none (DR-6) |
| L4-P6-07 | L4-T410 | L4-04-attention-ledger.md | 1706 | HIGH | Daily reconciliation with recorded truncations (DR-7) |
| L4-P6-08 | L4-T410 | L4-04-attention-ledger.md | 1706 | HIGH | The instrument-defect rule — same body, defined on the pre-truncation total |
| L4-P6-09 | L4-T402 | L4-04-attention-ledger.md | 360 | HIGH | `unplanned` and `ritual` as flags, never a ninth category (§67.2 line 5592) — declared in the taxonomy artifact at line 417 |
| L4-P6-10 | L4-T411 | L4-04-attention-ledger.md | 1847 | HIGH | Banded weekly self-report intake — `lib/selfreport.py`; the band table and cap come through `load_calibration()` (`L4-T404`) |
| L4-P6-11 | L4-T411 | L4-04-attention-ledger.md | 1847 | HIGH | Band apportionment by machine-derived share, with portfolio fallback where no share exists |
| L4-P6-12 | L4-T405 | L4-04-attention-ledger.md | 872 | HIGH | Five-minute collection-cost cap assertion — config check `C6` `five-minute-cap` (line 948); the value `5` is asserted present in `L4-T404` (line 816) |
| L4-P6-13 | L4-T411 | L4-04-attention-ledger.md | 1847 | HIGH | Permanent `self-reported` provenance label, and ritual refusal (a self-report carrying `ritual` is rejected, not cleaned) |
| L4-P6-14 | L4-T413 | L4-04-attention-ledger.md | 2454 | **MED** | Declared limitations of the attention hour. `HANDOFF-P.md` declares them in prose (line 2505: the ledger is a **lower bound**; Architecture and Coordination are systematically under-counted, §97.4 line 8978). The index wants a standalone machine-readable `limitations.yaml`; the substance exists, the artifact shape differs. |
| L4-P6-15 | L4-P7-T09 | L4-07-tests-and-runbook.md | 1108 | HIGH | Attention-ledger acceptance harness. `L4-04` §2.1 line 74 names `L4-P7-T09` as the owner of `metrics/attention/test-derivation.sh` and the attention fixtures — the index's exact files — and forbids `L4-04` from creating them. |

### Phase 7 — metric register (identity: index and body share the namespace)

Note: `L4-P7-01`…`L4-P7-20` are **index** metric-register rows. `L4-P7-T01`…`L4-P7-T14` are the **tests-phase body** ids (`L4-07-tests-and-runbook.md`). The literal `T` is significant — see §1.2.

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P7-01 | L4-P7-01 | L4-03-metric-register.md | 267 | HIGH | `metrics/register/metric-declarations.yaml` — eight §84.6 attributes per §103 measure; charter DoD-13 |
| L4-P7-02 | L4-P7-02 | L4-03-metric-register.md | 351 | HIGH | `metrics/register/validate-sources.sh` — every measure names its record store; a measure that cannot name its store does not ship |
| L4-P7-03 | L4-P7-03 | L4-03-metric-register.md | 389 | HIGH | `metrics/register/arming.py` — empty store renders `unbaselined`, never a miss (D77); charter DoD-14 |
| L4-P7-04 | L4-P7-04 | L4-03-metric-register.md | 429 | HIGH | `metrics/register/baselines.yaml` + `baselines.py` — baseline markers and the §103.14 five-measure minimum (AT-046); charter DoD-15 |
| L4-P7-05 | L4-P7-05 | L4-03-metric-register.md | 471 | HIGH | `metrics/register/ownership.py` — owner-and-response completeness gate (invariant 49) |
| L4-P7-06 | L4-P7-06 | L4-03-metric-register.md | 511 | HIGH | `metrics/compute/deployments.py` — deployment measures from `records/deployments/` |
| L4-P7-07 | L4-P7-07 | L4-03-metric-register.md | 550 | HIGH | `metrics/compute/incidents.py` — incident measures from `records/incidents/` |
| L4-P7-08 | L4-P7-08 | L4-03-metric-register.md | 588 | HIGH | `metrics/compute/restore.py` — restore freshness and failed restore tests |
| L4-P7-09 | L4-P7-09 | L4-03-metric-register.md | 626 | HIGH | `metrics/compute/uat.py` — UAT coverage and pass rate |
| L4-P7-10 | L4-P7-10 | L4-03-metric-register.md | 664 | HIGH | `metrics/compute/support.py` — support load and first-response by severity |
| L4-P7-11 | L4-P7-11 | L4-03-metric-register.md | 702 | HIGH | `metrics/compute/eval.py` — eval measures and regression detection (feeds AT-107 / SIG-42) |
| L4-P7-12 | L4-P7-12 | L4-03-metric-register.md | 740 | HIGH | `metrics/compute/security_reviews.py` — security-review measures: count by severity, unfixed-finding age |
| L4-P7-13 | L4-P7-13 | L4-03-metric-register.md | 778 | HIGH | `metrics/compute/decisions.py` — decision latency, pending-decision queue depth and age |
| L4-P7-14 | L4-P7-14 | L4-03-metric-register.md | 816 | HIGH | `metrics/compute/learning_loop.py` — learning-loop measures (SIG-47) |
| L4-P7-15 | L4-P7-15 | L4-03-metric-register.md | 854 | HIGH | `metrics/compute/estimates.py` — estimate-vs-actual and forecast-calibration inputs |
| L4-P7-16 | L4-P7-16 | L4-03-metric-register.md | 892 | HIGH | `metrics/compute/rqm.py` — Ready-queue-miss 30-day rolling count and trend (SIG-06, invariant 15) |
| L4-P7-17 | L4-P7-17 | L4-03-metric-register.md | 930 | HIGH | `metrics/compute/status_requests.py` — status-request count from the event log |
| L4-P7-18 | L4-P7-18 | L4-03-metric-register.md | 968 | HIGH | `metrics/compute/lifecycle_cadence.py` — onboarding, launch and demo cadence measures |
| L4-P7-19 | L4-P7-19 | L4-03-metric-register.md | 1006 | HIGH | `metrics/compute/weekend_residual.py` — undeclared weekend activations, the residual |
| L4-P7-20 | L4-P7-20 | L4-03-metric-register.md | 1044 | HIGH | `metrics/compute/attention_measures.py` — attention-ledger eleven figures into the §103 register |

### Phase 8 — lane acceptance and handoff

| Index id | Body id | Body file | Line | Conf | What the task does |
| --- | --- | --- | ---: | --- | --- |
| L4-P8-04 | L4-P7-T14 | L4-07-tests-and-runbook.md | 1929 | HIGH | Rebase, lane self-check, open the final PR to `integration` |

---

## 3. Residue — index ids with no body anywhere (14)

**This is the true unbuilt work of Lane 4.** Each row states what the index promises, so it can be
scoped. Nothing here is authored in this file.

### 3.1 Phase 2 residue (3)

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| L4-P2-01 | `tools/records/check.sh` (the universal per-task check dispatcher, byte-identical to `L4-06` §0.6) and `tools/records/CONTRACT.md` (transcribing the §0.5 OK/FAIL/ERROR exit contract). **Every index task from `L4-P2-01` onward is required to contribute `tools/records/checks/<TASK-ID>.sh`.** | No body creates `check.sh`. `L4-00-charter.md` `L4-T005` creates `lane-selfcheck.sh`, a different script (path ownership). `L4-P5-14` line 1345 *runs* `bash tools/records/check.sh ZZZ` as entry condition E2, i.e. treats it as a prerequisite built elsewhere. `CONTRACT.md` appears only in `L4-06-tasks.md`. **This is load-bearing: the entire index-side SELF-VERIFY convention rests on a dispatcher no body builds.** |
| L4-P2-23 | `schemas/records/defs/flags.schema.json` — `agent_authored` a required boolean on change records and PR records; `detection_source` **defined once and referenced, never redeclared per store**. Charter DoD-10. | The bodies do the opposite by design. `record.base.schema.json` has eleven `$defs` (`person_ref`, `record_ref`, `evidence_link`, `digest`, `pass_fail`, `nonempty_string`, `record_schema_version`, `record_id`, `product_ref`, `timestamp_utc`, `date_utc`) — no flags. `detection_source` is redeclared per store: an enum in `incident` (`L4-T206`, line 1344) and an open `nonempty_string` in `support` (`L4-T220`, line 2850), each with its own justification. No change-record or PR-record schema exists in the lane at all, so `agent_authored` has no record to be required on — it exists only as an event payload key in `L4-T203`. `validate-schemas.sh --fields` exists but proves the D88 no-names lint, a different assertion under the same flag name. **A design conflict, not just a gap: L0 must rule.** |
| L4-P2-28 | `schemas/records/versions.yaml` + `schemas/records/VERSIONS.md` — every schema file listed with its version; a statement that record and event schemas are §60.2 versioned contracts and that a retired version is marked, never removed. | Neither filename appears in any body. Partial substance only: `store-map.yaml` (`L4-T223`) carries a `version:` column per row and documents the §60.2 "write v2 alongside v1, never replace" rule as a new-row convention. There is no version register document and no retired-version marking rule for schemas. Mapped at LOW and therefore **not counted as mapped**. |

### 3.2 Phase 3 residue (4) — the taxonomy and store-policy tail

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| L4-P3-02 | `metrics/taxonomy/payloads/<event_type>.yaml` — one payload declaration **file per event type**, directory-per-item, no shared file. Every one of the 89 identifiers (D114-D / REG-021) has exactly one; no orphan file, no identifier without one. Charter DoD-4. | No body creates a `payloads/` directory; the string appears in no phase file. `L4-T203` declares `payload_required: [...]` **inline as a column of `event-types.yaml`** — which is exactly the single shared file `PARTITION.md` rule 3 and the index row forbid. Substance partly present, structure explicitly contrary. |
| L4-P3-04 | `metrics/freshness/write-freshness.yaml` + `tools/records/validate-freshness.sh` — an expected maximum inter-write interval per store; exactly **3** Blocking (`events/`, `records/deployments/`, `records/uat/`); every other store Amber past its interval; computed from git commit timestamps on the store path. Charter DoD-5. | No builder. Every occurrence is a forward reference: `L4-P7-T01`'s entry gate requires `validate-freshness.sh` PRESENT, `L4-P7-T11` tests it, `L4-T316`/`L4-T225` name it in coverage proofs. Nothing writes either file. (`L4-P5-23` writes `metrics/ingest/freshness.yaml` — collector ingest freshness, a different artifact for a different subsystem.) |
| L4-P3-05 | `metrics/anchor/records-head-anchor.schema.json` — the records-repo default-branch head SHA and commit count; a head not descending from the last anchored SHA is Blocking drift, Level 5 (D107). L4 writes the schema only; L3 writes the anchors. | Appears once in the whole lane, in `L4-00-charter.md` line 112 (a scope statement). No body. This is the L4 side of a cross-lane contract with L3 — its absence breaks L3's reconciler input. |
| ~~L4-P3-06~~ | ~~`metrics/signals/sig-source-map.yaml`~~ | **(Closed Session 13 — body in L4-03-metric-register.md line 46; mapped in §2 Phase 3.)** |
| L4-P3-07 | `metrics/retention/retention-classes.yaml` + `tools/records/validate-retention.sh` — a retention class per store; canonical records append-only permanent with effective dating; raw activity telemetry a diagnostic window; no store unclassified. Charter DoD-19. | No builder. **`L4-P5-23` line 3304 states it outright:** *"the class file is `metrics/retention/retention-classes.yaml`, built by `L4-P3-07` (entry condition E8). This task asserts that file is reachable and declares **no** class of its own."* A phase body names an index id as the builder of a file no body builds. |

### 3.3 Phase 4 residue (3)

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| L4-P4-07 | `tools/records/record-decision` + `record_decision.py` — the decision CLI writing `pending` then `decided`, against `decision.schema.json` and `decision-pending.schema.json`. | No builder. `L4-T314` (line 2016) and `L4-T302` mention the record-decision CLI in the write-path register as a write path that must exist; `L4-T213` builds the `decision-pending` **schema** only. The CLI itself is written nowhere. Note the schemas (`L4-T212`, `L4-T213`) *are* built, so this is a thin, well-specified gap. |
| L4-P4-08 | `tools/records/read-across` + `read_across.py` + `test-read-across.sh` — the **fail-closed** cross-repository reader: a check that cannot reach the records repository fails closed rather than reporting zero (§40.1 line 3671). Charter DoD-16. | The **test** exists and the **subject** does not. `L4-P7-T11` (line 1548) builds `test-read-across.sh` and `L4-P7-T01`'s entry gate requires `tools/records/read-across` PRESENT. No body creates `read-across`. This is one of the two instrument traps that produce false zeros — it is exactly the fail-closed guarantee, unbuilt. |
| L4-P4-10 | `tools/records/lib/rwtoken.py` — a records-writer token adapter **for every writer**, so each writer mints an installation token rather than carrying a credential. | No builder. `L4-P1-T12` writes `tools/records/rw-token.sh` (the credential *shape* as code, phase-1 provisioning) — a different artifact at a different layer. No writer-library adapter exists; `L4-T305`'s emission library does not acquire a token. |

### 3.4 Phase 5 residue (1)

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| L4-P5-13 | `tools/records/rqm/replan.py` — material requirement change: a re-plan event linked to the estimate record it invalidates. | No builder. `re-plan triggered` exists only as event-type entry text in `L4-T203`'s enum (`L4-04` lines 126, 552 quote it). Nothing links a re-plan event to an estimate record. |

### 3.5 Phase 7 residue (0) — metric register [ALL CLOSED Session 13]

**Closed Session 13.** `L4-03-metric-register.md` was created with all 20 task bodies
(`L4-P7-01`…`L4-P7-20`). All 20 rows are now mapped in §2 Phase 7. The structural gap described
in §1.1 is filled; `L4-P7-T01`'s entry-gate precondition (`metric-declarations.yaml` and
`validate-sources.sh` PRESENT) can now be satisfied.

21 items closed in this section and §3.2 (Closed Session 13 — body in L4-03-metric-register.md).

### 3.6 Phase 8 residue (3)

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| L4-P8-01 | `tools/records/test-freshness-e2e.sh` — write-freshness proved end to end from real git commit timestamps. | No builder; depends on `L4-P3-04`, itself residue. |
| L4-P8-02 | `tools/records/run-dod-matrix.sh` — the **20 charter DoD rows in one command**. | No builder. The lane has four per-phase coverage proofs (`L4-T225`, `L4-T316`, `L4-T418`, `L4-P5-24`) and one tests-phase runner (`L4-P7-T14`), but no single 20-row DoD matrix. This is the lane's own acceptance gate, unbuilt. |
| L4-P8-03 | `metrics/HANDOFF.md` — the **lane** handoff manifest. | No builder. `L4-T413` writes `HANDOFF-P.md`, scoped in its own heading to *"what **this phase** emits"* (the attention ledger only). A phase handoff is not the lane handoff; mapping it would overstate coverage. |

---

## 4. Orphans — bodies no index row claims (41)

These are executable, fully-specified tasks that **will be done and are tracked in no index**. They
are not waste: several are prerequisites the index silently assumes. They are invisible to any
plan, schedule or progress count built from `L4-06-tasks.md`.

### 4.1 `L4-02-record-schemas.md` (3)

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| L4-T205 | L4-02-record-schemas.md | 954 | D88 no-names enforcement: the property-name lint and the value scanner. Every store schema (`L4-T206`…`L4-T222`) declares a dependency on it and `validate-schemas.sh --fields` delegates to it. A hard prerequisite the index never lists. |
| L4-T224 | L4-02-record-schemas.md | 3424 | Ten **rule-level** negative fixtures in `fixtures/invalid/rules/`, `--negative 10/10`: non-UTC timestamp, date-where-instant, missing `record_schema_version`, undeclared property, bad record id, D88 display name, free-text `event_type`, missing envelope field, undeclared envelope property, malformed `event_id`. **Near-duplicate of `L4-P7-T06`** — both produce a `10/10` result claimed for charter DoD-3, over two different sets of ten. L0 should rule on which is authoritative before both are built. |
| L4-T225 | L4-02-record-schemas.md | 3703 | Rebase and open the Phase-2 PR to `integration`. |

### 4.2 `L4-03-write-paths.md` (13) — the write-path register and emitters

The index's Phase 4 covers the writer *library* and the RVR handler; it covers none of the
write-path **register**, the board/deploy **emitters**, or the human review lane.

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| L4-T301 | L4-03-write-paths.md | 143 | Phase-3 preflight and phase branch |
| L4-T302 | L4-03-write-paths.md | 217 | The write-path register — every store's writer, hand-authored flag and event pairing |
| L4-T303 | L4-03-write-paths.md | 500 | Write-path register validator, with its negative test |
| L4-T304 | L4-03-write-paths.md | 618 | The RECORD-VERIFICATION-RESULT **input contract** (`L4-P4-06` maps only to the handler, `L4-T306`) |
| L4-T307 | L4-03-write-paths.md | 1128 | RVR test harness (charter DoD-9) |
| L4-T308 | L4-03-write-paths.md | 1225 | The board-event emission contract |
| L4-T309 | L4-03-write-paths.md | 1356 | The board emitter and the Ready-queue-miss emitter (`rqm-emit`) — `L4-T416` binds its verdict-document keys and forbids editing it |
| L4-T310 | L4-03-write-paths.md | 1513 | Taxonomy conformance check for both emission contracts |
| L4-T311 | L4-03-write-paths.md | 1608 | The deploy required-step contract |
| L4-T312 | L4-03-write-paths.md | 1741 | The deploy emitter |
| L4-T313 | L4-03-write-paths.md | 1867 | The deploy emitter failure test |
| L4-T314 | L4-03-write-paths.md | 1974 | The human review lane, declared |
| L4-T316 | L4-03-write-paths.md | 2264 | Phase-3 coverage proof, rebase and lane PR |

### 4.3 `L4-04-attention-ledger.md` (6)

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| L4-T401 | L4-04-attention-ledger.md | 285 | Phase-4 preflight and phase branch |
| L4-T406 | L4-04-attention-ledger.md | 1032 | Scheduled availability — the daily cap's input (`scheduled-availability.py`); DR-7 cannot reconcile without it |
| L4-T412 | L4-04-attention-ledger.md | 2211 | The phase's own proof, `metrics/attention/selfcheck/`, nine cases `SC-1`…`SC-9` on a path no sibling claims — deliberately distinct from `L4-P7-T09` |
| L4-T414 | L4-04-attention-ledger.md | 2571 | Every ledger metric names its store, or it does not ship — the ledger's eleven outputs with all eight §84.6 attributes |
| L4-T415 | L4-04-attention-ledger.md | 2917 | Attention-ledger gate `G1`…`G6` and the phase checkpoint |
| L4-T418 | L4-04-attention-ledger.md | 3503 | Phase-4 coverage proof, rebase and lane PR |

### 4.4 `L4-05-pipeline-and-boards.md` (11) — the entire ingest pipeline

**The index has no row for any of this.** Subsystem I's collector half — DevLake, Prometheus,
Scorecard and metric source discipline — is eleven fully-written tasks tracked nowhere. Three are
marked **ASSISTED** (they need a human), which no index row signals.

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| L4-P5-14 | L4-05-pipeline-and-boards.md | 1324 | Ingest entry gate, `metrics/ingest/` skeleton and the `INGEST` dispatcher (its eight entry conditions require four residue artifacts) |
| L4-P5-15 | L4-05-pipeline-and-boards.md | 1475 | `collectors.yaml` — the three named collectors and their cadences |
| L4-P5-16 | L4-05-pipeline-and-boards.md | 1658 | DevLake nightly ingest declaration and the §99.3 coverage gate |
| L4-P5-17 | L4-05-pipeline-and-boards.md | 1994 | **ASSISTED** — DevLake connector field-coverage confirmation |
| L4-P5-18 | L4-05-pipeline-and-boards.md | 2222 | Prometheus scrape declaration: the three §41.2 endpoints |
| L4-P5-19 | L4-05-pipeline-and-boards.md | 2462 | **ASSISTED** — private-path scrape reachability evidence |
| L4-P5-20 | L4-05-pipeline-and-boards.md | 2654 | Scorecard scheduled scan and drop detection |
| L4-P5-21 | L4-05-pipeline-and-boards.md | 2875 | **ASSISTED** — Scorecard private-repository behaviour and baseline scan |
| L4-P5-22 | L4-05-pipeline-and-boards.md | 3058 | Metric source discipline: the `source_kind` rule and its validator (invariant 46 — derived, never hand-maintained) |
| L4-P5-23 | L4-05-pipeline-and-boards.md | 3289 | Ingest freshness and the three frozen §7.10 arming strings |
| L4-P5-24 | L4-05-pipeline-and-boards.md | 3514 | Phase sweep, rebase, PR |

### 4.5 `L4-07-tests-and-runbook.md` (8)

The index's Phase 8 has four rows; the tests phase has fourteen bodies. Six map (§2); eight do not.

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| L4-P7-T01 | L4-07-tests-and-runbook.md | 294 | Entry gate: inventory 26 Phase 1–6 artifacts, `ABSENT=0` required. **Six of the 26 are residue** (`validate-freshness.sh`, `validate-retention.sh`, `read-across`, `ready-queue-miss.schema.json`, `metric-declarations.yaml`, `validate-sources.sh`) — this gate cannot pass today. |
| L4-P7-T02 | L4-07-tests-and-runbook.md | 380 | Test harness skeleton and the runner contract |
| L4-P7-T03 | L4-07-tests-and-runbook.md | 496 | Fixture corpus A: the five verbatim-spec valid fixtures |
| L4-P7-T05 | L4-07-tests-and-runbook.md | 722 | Suite 1: schema round-trip and the absent-version read rule |
| L4-P7-T07 | L4-07-tests-and-runbook.md | 895 | Suite 3: the five D88 display-name negatives and their positives |
| L4-P7-T08 | L4-07-tests-and-runbook.md | 1010 | Suite 4: AT-075 banned-measurement negatives, twenty assertions |
| L4-P7-T11 | L4-07-tests-and-runbook.md | 1545 | Suite 7: store validators, freshness, retention, taxonomy, fail-closed read — tests four residue artifacts |
| L4-P7-T13 | L4-07-tests-and-runbook.md | 1837 | Suite self-canary: prove the suite fails when a check is removed |

---

## 5. What the founder needs to decide

Three items in this concordance are **conflicts**, not gaps, and cannot be closed by writing code:

1. **`L4-P2-23` vs `L4-T206`/`L4-T220`** — the index requires `detection_source` defined once and
   referenced; the bodies deliberately redeclare it per store with written justification (an enum
   for `incident`, an open string for `support`, because §97.2 line 8873 says *"include"* not
   *"are"*). One of the two is wrong.
2. **`L4-P3-02` vs `L4-T203`** — the index requires one payload file per event type
   (directory-per-item, `PARTITION.md` rule 3); the body puts `payload_required` inline as a column
   of the single shared `event-types.yaml`.
3. **`L4-T224` vs `L4-P7-T06`** — two different sets of ten negatives, both claiming charter DoD-3's
   `10/10`. Building both is duplicate authorship at merge.

And one is structural: **Lane 4 needs a metric-register phase document**, or index Phase 7 plus
`L4-P3-06` must be reassigned. Twenty-one of the thirty-five residue ids sit behind that one
decision, and `L4-P7-T01`'s entry gate blocks the tests phase until it is resolved.

---

## 6. Exact commands used — regenerate this

Run from `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes` under Git Bash.

```bash
# ---------- 0. the copy being measured ----------
wc -l L4-00-charter.md L4-01-records-repo.md L4-02-record-schemas.md \
      L4-03-write-paths.md L4-04-attention-ledger.md L4-05-pipeline-and-boards.md \
      L4-06-tasks.md L4-07-tests-and-runbook.md

# ---------- 1. INDEX side: 117 ----------
# The ids are TABLE ROWS in section 2 (lines 253-371), column 2. No ### heading exists.
sed -n '253,371p' L4-06-tasks.md \
  | awk -F'|' 'NF>3 {gsub(/ /,"",$3); print $3}' \
  | grep -E '^L4-' | sort -u > /tmp/l4_index.txt
wc -l < /tmp/l4_index.txt                                   # -> 117
sed -E 's/[0-9]+$//' /tmp/l4_index.txt | sort | uniq -c     # -> 7/12/29/7/10/13/15/20/4
# Cross-check: no further index ids in the acceptance-criteria lists (section 3) or the
# charter DoD map (section 6) -- both draw from the same 117.

# ---------- 2. namespace survey: never assume one regex finds them all ----------
grep -ohE 'L4-(P[0-9]+-)?T?[0-9]{2,3}' L4-00-charter.md L4-01-records-repo.md \
     L4-02-record-schemas.md L4-03-write-paths.md L4-04-attention-ledger.md \
     L4-05-pipeline-and-boards.md L4-06-tasks.md L4-07-tests-and-runbook.md \
  | sed -E 's/[0-9]+$/N/' | sort | uniq -c | sort -rn
# -> L4-TN, L4-P5-N, L4-N, L4-P2-N, L4-P7-TN, L4-P1-TN, L4-P7-N, L4-P3-N, L4-P6-N,
#    L4-P4-N, L4-P8-N   (eleven shapes; L4-P7-N and L4-P7-TN differ by one character)

# ---------- 3. BODY side: 107 ----------
# Bodies are headings at depth 2-5, in two dialects: "### L4-T203 --" and "## TASK `L4-P1-T01` --".
# A body carries steps, commands, acceptance criteria and a SELF-VERIFY; a dependency-list
# mention does not. This union pattern covers both dialects and all namespaces:
BODY='^#{2,5} (TASK )?.?L4-(T[0-9]{3}|P[0-9]-T?[0-9]{2})'
for f in L4-00-charter.md L4-01-records-repo.md L4-02-record-schemas.md \
         L4-03-write-paths.md L4-04-attention-ledger.md L4-05-pipeline-and-boards.md \
         L4-06-tasks.md L4-07-tests-and-runbook.md; do
  echo "$f : $(grep -cE "$BODY" "$f")"
done
# -> 7 / 12 / 25 / 16 / 18 / 15 / 0 / 14
grep -hoE "$BODY" L4-0*.md | grep -oE 'L4-[A-Z0-9-]+' | sort -u | wc -l   # -> 107
# Full inventory with file:line:title (the source of every line number in this document):
for f in L4-00-charter.md L4-01-records-repo.md L4-02-record-schemas.md \
         L4-03-write-paths.md L4-04-attention-ledger.md L4-05-pipeline-and-boards.md \
         L4-07-tests-and-runbook.md; do grep -nE "$BODY" "$f" | sed "s|^|$f:|"; done

# ---------- 4. MAPPING evidence: index-promised artifact -> owning body ----------
# 4a. every path the index promises, and which phase files mention it at all
sed -n '253,371p' L4-06-tasks.md \
  | awk -F'|' 'NF>3 {f=$6; gsub(/^ +| +$/,"",f); print f}' | tr ',' '\n' \
  | grep -oE '[a-z0-9_./-]+\.(yaml|py|sh|json|md|txt)' | sort -u > /tmp/idx_paths.txt
while read p; do
  printf '%-52s %s\n' "$p" \
    "$(grep -lF "$(basename "$p")" L4-0[0-57]*.md 2>/dev/null | tr -d '\n' || echo NONE)"
done < /tmp/idx_paths.txt

# 4b. attribute any hit to its ENCLOSING task body (the tool behind every mapping row)
cat > /tmp/owner.sh <<'SH'
#!/bin/bash
cd /c/D_Drive/PS/MultiProduct/Code/implementation/lanes
for f in L4-00-charter.md L4-01-records-repo.md L4-02-record-schemas.md L4-03-write-paths.md \
         L4-04-attention-ledger.md L4-05-pipeline-and-boards.md L4-07-tests-and-runbook.md; do
  grep -nF "$1" "$f" 2>/dev/null | cut -d: -f1 | while read ln; do
    awk -v L="$ln" -v F="$f" \
      'NR<=L && /^#{2,5} (TASK )?.?L4-(T[0-9]{3}|P[0-9]-T?[0-9]{2})/ {h=$0; hl=NR}
       END{print F"  hit@"L"  owner="hl": "h}' "$f"
  done
done
SH
chmod +x /tmp/owner.sh
bash /tmp/owner.sh "retention-classes"       # -> only entry-gate/prereq refs, no builder
bash /tmp/owner.sh "test-derivation.sh"      # -> built by L4-P7-T09  (proves L4-P6-15)
bash /tmp/owner.sh "test-rqm-detector.sh"    # -> built by L4-P7-T10  (proves L4-P5-12)

# 4c. BUILDER test -- distinguishes "creates it" from "mentions it".
#     A body that creates a file uses `cat >`, `mkdir -p`, `touch` or `: >`.
for p in "tools/records/check.sh" at105 secreview payloads freshness.yaml anchor \
         retention sig-source record-decision read-across rwtoken run-dod-matrix; do
  printf '%-24s ' "$p"
  hits=$(grep -hoE "(cat >|mkdir -p|touch|: >)[^\n]{0,120}$p[^\n]{0,40}" \
           L4-00-charter.md L4-01-records-repo.md L4-02-record-schemas.md \
           L4-03-write-paths.md L4-04-attention-ledger.md \
           L4-05-pipeline-and-boards.md L4-07-tests-and-runbook.md 2>/dev/null | head -2)
  echo "${hits:-<no builder>}"
done
# -> every residue artifact prints "<no builder>"

# ---------- 5. the structural finding ----------
sed -n '60,80p' L4-04-attention-ledger.md   # section 2.1: metrics/register/** -> owner
                                            # "the metric-register phase", task column EMPTY
sed -n '2571,2580p' L4-04-attention-ledger.md   # L4-T414 disclaims metric-declarations.yaml
sed -n '3300,3306p' L4-05-pipeline-and-boards.md # "built by L4-P3-07" -- an index id, no body
ls L4-0*.md    # L4-00..L4-05, L4-06-tasks, L4-07 -- there is no metric-register phase file
```

**Reconciliation:** 117 index = 82 mapped + 35 residue. 107 bodies = 66 consumed by those 82
mappings + 41 orphans.

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

### Fixes applied in Session 12

- **D-L4-01 closed** — the defect blocking `L4-01-records-repo.md` dispatch is resolved.
- **DoD-3/11/12 BLOCKED annotations cleared** — the three Definition-of-Done items that were annotated BLOCKED (modes missing) are now unblocked: the relevant modes were added to `L4-02-record-schemas.md`.

### L4-99 re-review (Session 12): **PASS** (pending re-verification against updated `L4-02`)

---

## Session 13 Update (2026-09-08)

- **L4-03-metric-register.md created** — new phase file with 21 task bodies covering the metric-register phase (L4-P3-06 and all 20 Phase 7 index rows); the structural gap identified in §1.1 is now filled.
- **L4-P7-T01 entry gate unblocked** — `metrics/register/metric-declarations.yaml` and `metrics/register/validate-sources.sh` now have owners (L4-03); the Phase 7 PRESENT/ABSENT=0 precondition can be satisfied.
- **DoD-5/13/14/15/19 discharge path exists** — the metric-register tasks provide the artifacts these DoD items require; discharge is now schedulable.
- **D-L4-D8 status under investigation** — a concurrent check is verifying whether the D-L4-D8 decision record is closed or still open; result to be recorded in a follow-on session.
