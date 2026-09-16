# L4-99 — LANE 4 COHERENCE REVIEW

> **SUPERSEDED — 2026-09-02**  
> This review was produced against an earlier copy of the L4 lane files.  
> **Do not act on any finding in this document** without re-deriving it against the current files.

**Reviewer:** L4 coherence reviewer
**Scope reviewed in full:** `L4-00-charter.md`, `L4-01-records-repo.md`, `L4-02-record-schemas.md`, `L4-03-write-paths.md`, `L4-04-attention-ledger.md`, `L4-05-pipeline-and-boards.md`, `L4-06-tasks.md`, `L4-07-tests-and-runbook.md`, plus `PARTITION.md`.
**Spec of record checked against:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## VERDICT

> ## **BLOCKED — DO NOT DISPATCH LANE 4.**
>
> The lane carries **three mutually incompatible task-id namespaces**. Of the 117 tasks in `L4-06-tasks.md` — the file that declares itself *"the complete, ordered work list … Every task is executable from this file alone"* — **98 have no task body in any L4 document**, and **84 tasks that do have bodies appear in no row of that table**. Six charter Definition-of-Done proof commands invoke executables or flags that no task in the lane ever builds. A low-cost executor dispatched today would complete Phase 0, hit an unimplementable acceptance command at task 6 of 117, and stop.
>
> Blocking defects: **D1–D8**. Defects D9–D16 must also be resolved before dispatch because each one produces a STOP under `L4-06-tasks.md` §0.7 on a task that would otherwise pass.

**What is good, and should be preserved through the repair:** `L4-02`, `L4-03`, `L4-04` and `L4-05` are excellent — literal commands, correct spec line numbers, real negative tests, honest DECISION REQUIRED blocks with stated defaults, no path-ownership violations. The damage is almost entirely in the two coordinating documents (`L4-00-charter.md` and `L4-06-tasks.md`), which were written against a different plan than the one the phase files implement.

---

## 1. Path-ownership violations

**None found, with one exception.** Every `cat >`, `mkdir -p`, `printf >` and `git add` in all eight files targets `schemas/records/**`, `metrics/**`, `tools/records/**` or `control-plane-records/**`. Every phase file carries an explicit "paths this phase writes — nothing else" table, and every SELF-VERIFY carries a `FOREIGN=0` line. `registries/**`, `.github/**`, `reconciler/**`, `access/**`, `contracts/**` are correctly declared read-only throughout, with the publish-not-write mechanism routed to L0 as D-L4-01/D-L4-02. This part of the lane is sound.

The single exception is **D14** below (the deliberate seeded canary), which is a destructive-command defect rather than an ownership violation.

---

## 2. Defect list — worst first

### D1 — CRITICAL — `L4-06-tasks.md` and the phase files use incompatible task-id namespaces; 98 of 117 tasks have no body

| Field | Value |
|---|---|
| **File / task id** | `L4-06-tasks.md` §2 (all 117 rows); `L4-02` `L4-T201`–`L4-T225`; `L4-03` `L4-T301`–`L4-T316`; `L4-04` `L4-T401`–`L4-T418`; `L4-05` `L4-P5-14`–`L4-P5-24`; `L4-07` `L4-P7-T01`–`L4-P7-T14` |

**Problem.** Three namespaces exist and only one pair of documents agrees:

| Namespace | Used by | Tasks | Matched by an `L4-06` row? |
|---|---|---|---|
| `L4-T001`–`L4-T007` | charter, `L4-06` | 7 | **yes** |
| `L4-P1-T01`–`L4-P1-T12` | `L4-01`, `L4-06` | 12 | **yes** |
| `L4-T201`–`L4-T225` | `L4-02` | 25 | **no** |
| `L4-T301`–`L4-T316` | `L4-03` | 16 | **no** |
| `L4-T401`–`L4-T418` | `L4-04` | 18 | **no** |
| `L4-P5-14`–`L4-P5-24` | `L4-05` | 11 | **no** (`L4-06` §2 stops at `L4-P5-13`) |
| `L4-P7-T01`–`L4-P7-T14` | `L4-07` | 14 | **no** (`L4-06` §2 has `L4-P7-01`–`L4-P7-20`, a different set) |

`L4-06` §2 rows 20–117 (`L4-P2-01` … `L4-P8-04`, 98 tasks) carry a title, a files-touched column, deps, a size and an acceptance command — and **no command block, no fixture, no expected output beyond the universal dispatcher line**. `L4-06` §3 gives them acceptance *criteria*; nothing gives them *instructions*. `L4-06` line 8 states *"Every task is executable from this file alone"*; for 98 of 117 rows that is false.

Conversely 84 tasks with full, high-quality bodies (`L4-T201`–`L4-T225`, `L4-T301`–`L4-T316`, `L4-T401`–`L4-T418`, `L4-P5-14`–`L4-P5-24`, `L4-P7-T01`–`L4-P7-T14`) appear in no dispatch table, and `L4-05` §2.2 and `L4-04` §2.1 both cite `L4-06` row numbers ("rows 66–69", "rows 70–78") as if the namespaces were one.

**Correction.** L0 must pick **one** namespace and reissue. The cheapest repair that preserves the good work: keep the phase-file namespace (`L4-T2xx`/`L4-T3xx`/`L4-T4xx`) as authoritative, rewrite `L4-06` §2 rows 20–117 to be the index of the *actual* tasks in `L4-02`/`L4-03`/`L4-04`/`L4-05`/`L4-07`, and delete every `L4-06` row for which no body exists (see **D2** — some cannot be re-pointed because nothing builds them). Every `Deps` cell, every `L4-06` §3 acceptance row, every `L4-06` §5 exit gate and every `L4-06` §6 DoD map must be re-derived from that single list.

---

### D2 — CRITICAL — Whole deliverables have acceptance criteria and tests but no task body anywhere in the lane

| Field | Value |
|---|---|
| **File / task id** | `L4-06-tasks.md` `L4-P3-04`, `L4-P3-05`, `L4-P3-06`, `L4-P3-07`, `L4-P7-01`–`L4-P7-20`, `L4-P2-06`, `L4-P2-28`, `L4-P8-01`–`L4-P8-04`; charter DoD-5, DoD-13, DoD-14, DoD-15, DoD-19 |

**Problem.** These artifacts are named as required by the charter, indexed by `L4-06`, and **tested by `L4-07`** — but no document contains a task that creates them. Grep across all eight L4 files, matching only charter/`L4-06`/`L4-07` (requirement and test), never a phase file (construction):

| Artifact | Required by | Built by |
|---|---|---|
| `metrics/freshness/write-freshness.yaml` | DoD-5, `L4-P3-04`, `L4-07` `L4-P7-T11` | **nothing** |
| `metrics/anchor/records-head-anchor.schema.json` | charter §5.2, `L4-P3-05` | **nothing** |
| `metrics/signals/sig-source-map.yaml` | charter §5.2, `L4-P3-06` | **nothing** |
| `metrics/retention/retention-classes.yaml` | DoD-19, `L4-P3-07` | **nothing** |
| `metrics/register/metric-declarations.yaml` | DoD-13, `L4-P7-01` | **nothing** |
| `metrics/compute/**` (15 modules) | DoD-13, `L4-P7-06`–`L4-P7-20` | **nothing** |
| `metrics/register/validate-sources.sh`, `arming.py`, `baselines.yaml`, `ownership.py` | DoD-13/14/15, `L4-P7-02`–`L4-P7-05` | **nothing** |
| `schemas/records/store-inventory.yaml` | `L4-P2-06`, `--stores` | **nothing** (`L4-02` builds `store-map.yaml` instead — see **D21**) |
| `schemas/records/versions.yaml`, `VERSIONS.md` | `L4-P2-28` | **nothing** |
| `tools/records/run-dod-matrix.sh`, `test-freshness-e2e.sh`, `metrics/HANDOFF.md` | `L4-P8-01`–`L4-P8-03` | **nothing** |

`L4-04` §2.1 routes `metrics/register/**` and `metrics/signals/**` to *"the metric-register phase"* with an em-dash where the task id should be. **There is no metric-register phase document.** The lane's file set is `L4-00` … `L4-07` and none of them is it.

Consequence: charter **DoD-5, DoD-13, DoD-14, DoD-15 and DoD-19 are undischargeable**, and `L4-07` `L4-P7-T11` is a test suite pointed at files that will never exist.

**Correction.** L0 must author the missing phase document (a metric-register / freshness / retention / signals phase, ~30 tasks, the largest single gap) before dispatch, or explicitly descope those DoD rows and the `L4-07` suites that test them. This is not an executor-repairable gap.

---

### D3 — CRITICAL — Six charter DoD proof commands invoke executables or flags that no task builds

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` §7 DoD-2, DoD-3, DoD-4, DoD-10, DoD-11, DoD-12, DoD-18; `L4-06-tasks.md` §4.2 |

**Problem.** The charter's §7 and `L4-06` §4.2 both state *"Expected stdout, exactly"*. Against what `L4-02` `L4-T223` actually ships:

| Required command | Required output | What exists |
|---|---|---|
| `bash tools/records/validate-schemas.sh` | `SCHEMAS OK`, exit 0 | `L4-02` line 3357: bare invocation hits `*) echo "usage: …"; exit 1`. **No `SCHEMAS OK` string exists in the shipped script.** Also `${CP_ROOT:?}` and `${L4_PY:?}` are required env vars the DoD command does not set — it dies on unbound variable first |
| `… --negative` → `NEGATIVE OK 10/10` | | `L4-02` ships `tools/records/test-negative.sh --negative` printing `NEGATIVE 10/10`. Different script, different string |
| `… --fields` → `FIELDS OK` | | `--fields` delegates to `validate-no-names.sh --schemas`, printing `NO-NAMES SCHEMAS OK <n>` |
| `… --time` → `TIME OK` | | ships `TIME OK 17` |
| `… --at105` → `AT-105 OK` | | **mode not implemented** |
| `… --at046-secreview` → `SECREVIEW OK` | | **mode not implemented** |
| `bash tools/records/validate-taxonomy.sh` → `TAXONOMY OK` | | `L4-02` `L4-T203` ships `TAXONOMY OK 86` |

`L4-06` §2 additionally invokes `validate-schemas.sh --selftest`, `--only <name>` (×17), `--fixtures valid`, `--versions` — **none implemented**. `L4-02` implements exactly `--coverage`, `--lint`, `--time`, `--fields`, `--all`.

**Correction.** Freeze the output grammar once (`L4-07` §0.6 already attempts this and is the right home for it), then make the charter §7 table, `L4-06` §4.2, `L4-06` §5 exit gates, and the `L4-02` script agree — string for string, mode for mode. Every `L4-06` §2 acceptance command must name a mode that some task implements.

---

### D4 — CRITICAL — `lane-selfcheck.sh --coverage` is required twice and implemented nowhere

| Field | Value |
|---|---|
| **File / task id** | `L4-06-tasks.md` §2 row 6 (`L4-T006`), §4.3, §5 gate P0; `L4-00-charter.md` `L4-T005` |

**Problem.** `L4-06` makes `bash tools/records/lane-selfcheck.sh --coverage` the acceptance command for `L4-T006`, its SELF-VERIFY (expected `COVERAGE OK`), and **the entire Phase 0 exit gate**. The script is written verbatim exactly once, in charter `L4-T005` (lines 526–552), with `case "${1:-}" in --paths) … --stores) … *) echo "usage: lane-selfcheck.sh --paths | --stores"; exit 2`. `--coverage` falls to the usage branch: **exit 2, no `COVERAGE OK`**. The only `--coverage` in the lane is on a different script (`validate-schemas.sh`, `L4-02` `L4-T223`), which does not exist yet at Phase 0 and prints `COVERAGE OK 19`, not `COVERAGE OK`.

Charter `L4-T006` uses a completely different self-verify (`ROWS=31 / BADRANGE=0 / OVERFLOW=0 / FOREIGNPATH=0`), so the two documents disagree about how the same task is proved.

**Correction.** Add a `--coverage` mode to `lane-selfcheck.sh` in charter `L4-T005` that validates `metrics/register/l4-spec-coverage.csv` and prints `COVERAGE OK` (or repoint `L4-06` §2/§4.3/§5-P0 at the charter's `ROWS=31` self-verify). Whichever is chosen, the P0 exit gate must name a command that exists at the end of Phase 0.

---

### D5 — CRITICAL — The store-count check is hard-coded to 18 while Phase 1 builds 19

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` `L4-T002` / `L4-T005`; `L4-01-records-repo.md` `L4-P1-T03`; `L4-06-tasks.md` `L4-P1-T03`, `L4-P2-06`, gate P2; `L4-03-write-paths.md` `L4-T301` E1 |

**Problem.** Two skeletons are specified:

- Charter `L4-T002` creates 17 record stores + `events/` = **18 `.gitkeep`**, and `lane-selfcheck.sh --stores` hard-codes `if [ "$n" = "18" ]` (charter line 544).
- `L4-01` `L4-P1-T03` creates the same 17 + `events/` + **`bootstrap/`** = **19 `.gitkeep`**, and its SELF-VERIFY, its STOP rule and the Phase-1 exit gate (`L4-01` line 1523) all assert `19`. `L4-06` `L4-P1-T03` agrees: `19`.

If Phase 1 runs as `L4-01` specifies, `lane-selfcheck.sh --stores` returns `STORES FAIL count=19 expected=18`, exit 1. That single failure breaks:

- charter **DoD-1** (`STORES OK 17/17`),
- `L4-06` §2 acceptance for `L4-P2-06`,
- `L4-06` §5 **exit gate P2**,
- `L4-03` `L4-T301` entry condition **E1** (`= 18`) and its SELF-VERIFY line `STORES=18`,
- `L4-07` §1.2 and its `L4-P7-T14` and phase exit gate.

The string `STORES OK 17/17` printed when the count is 18 is itself confusing and should be fixed at the same time.

**Correction.** L0 decides whether `bootstrap/` is part of the skeleton (it is a Phase-1 write-path proof tree, not a §97.2 store, so the cleanest answer is: keep it, exclude it from the store count). Then make the counter count *stores*, not `.gitkeep` files, and set every assertion in all five documents to the same number with the same expected string.

---

### D6 — CRITICAL — Charter DoD-8 states the opposite of §97.5 on the Ready-queue-miss detector

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` §7 DoD-8 |

**Problem.** DoD-8 requires the detector to *"treat Backlog→Planned→In Progress as normal"*. Master Spec §97.5, **line 8984**, verbatim:

> *"when a person picks up a work item that has not passed through Ready — **a board transition from Backlog directly to Planned or In Progress**, or an item started while the product's Ready queue is empty — the board automation appends a Ready-queue-miss event … **The Planned column is the normal assignment step (Ready → Planned → In Progress)** and passing through it is never a miss."*

The carve-out is `Ready → Planned → In Progress`. `Backlog → Planned` is the **miss**, not the normal path. `L4-06` `L4-P5-06` and `L4-P5-08` state it correctly; `L4-04` `L4-T416` states it correctly. The charter — the document `L4-06` §6 maps every task back to — states it backwards.

Because the charter's §7 is the lane's Definition of Done, an executor building to DoD-8 builds a detector that misses the single most common real case, and SIG-06 renders zero forever — precisely the §99.6 risk-2 failure mode this lane exists to prevent.

**Correction.** Rewrite charter DoD-8 to: *"treats `Ready → Planned → In Progress` as normal; treats a transition from Backlog directly to Planned or In Progress as a miss unless suitable Ready items existed, in which case it is recorded `ready_bypass` outside the SIG-06 count."*

---

### D7 — CRITICAL — Systematically wrong spec line citations in the charter and `L4-06`

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` §7 (DoD-6, 9, 10, 11, 12), §8, §1; `L4-06-tasks.md` §3 (≈20 rows), §1 |

**Problem.** Every §97.2-internal citation in the charter and `L4-06` is shifted by roughly +14 to +17 lines. Verified line by line against the spec:

| Claim | Cited by charter / `L4-06` | **Actual line** |
|---|---|---|
| Base four (`record_schema_version, id, product, timestamp`), never edits in place, §60.2 versioning | 8890 / 8892 | **8875** |
| RECORD-VERIFICATION-RESULT dispatch | 8886 | **8871** |
| `detection_source` (`founder_direct`, `customer`) and `agent_authored` | 8888 | **8873** |
| Deletion-request four timestamps + security-review findings | 8884 | **8869** |
| Write-freshness window per store, Blocking for 3 stores | 8873 | **8867** |
| Deployment record write is a required, failing step of `deploy-production.yml` | 8875 | **8867** |
| Incident record example | 8894–8905 (`L4-P2-07`) | **8877–8890** (8894–8903 is the *deployment* example) |
| Deployment record example | 8907–8917 (`L4-P2-11`) | **8892–8903** (8905–8915 is the *decision* example) |
| Breach store row | 8856 (`L4-P2-14`) | **8854** (8856 is security-reviews) |
| Launch store row | 8859 (`L4-P2-18`) | **8858** (8859 is demos) |
| Security-reviews store row | 8858 (`L4-P7-12`) | **8856** |
| `records/decisions/pending/` store row | 8854 (`L4-P4-07`) | **8853** |
| Invariant 46 (derived, never hand-maintained) | 9513 | **9514** |
| Invariant 47 (append-only) | 9514 | **9515** |
| Invariant 48 (no silent overwrite) | 9515 | **9516** |
| Invariant 49 (owner and response, or deleted) | 9516 | **9517** |
| §53.1 write-freshness drift row | 4677 | **4671** |
| §53.1 `restore_tested` drift row | 4681 | **4672** |
| §53.1 seeded-canary rule | 4685 | **4680** |
| §40.1 signed-commits bullet (D107) | 3674 | **3676** |
| §40.1 head-SHA anchor bullet (D107) | 3679 | **3677** |
| §84.6 eight metric attributes | 7473 | **7471** (7473 is the *carrier* sentence) |
| §99.2 dependency spine *"I is the feedstock…"* | 9229 | **9209** (9229 is the Draft-PR-only verification tool row) |
| §99.6 risk 2 *"Evidence-plumbing gap"* | 9280 | **9281** (9280 is risk 1, scope drift) |
| §99.5 registry identity key / GitHub login | 9271 | **9269** (9271 is the Boards bullet) |
| §99.2 record-decision CLI tool row | 9214 (`L4-P4-07`) | **9217** (9214 is a table separator) |
| §103.13 decision-latency measures | 9958 (`L4-P7-13`) | **9885** (9958 is incident response time) |
| §103.3 undeclared weekend activations | 9812 (`L4-P7-19`) | **9811** (9812 is drift incidents by severity) |
| §97.4 precedence / attribution / reconciliation / instrument defect | 8974 / 8975 / 8976 / 8977 | **8973 / 8974 / 8975 / 8976** |
| §103.14 minimum baseline set | 9975–9977 | **9975** (9976–9977 are blank and `---`) |

**Also invented / over-stretched:** `L4-06` D-L4-TL-1 cites *"§101 invariant 85 requires third-party dependencies pinned"* to justify pinning Python packages. Invariant 85 (line 9565) is about **GSD Core releases, GitHub Actions SHAs and reusable-workflow tags** and says nothing about language dependencies. The pinning decision may be right; the citation does not support it.

**What is correct, and should be the model:** `L4-02`, `L4-03`, `L4-04` and `L4-05` cite accurately. Sampled and confirmed correct: §97.2 store rows 8847–8866 (`L4-03` §3, all 18 rows), 8871 RVR, 8867 required-failing-steps (`L4-03`), the 86-entry taxonomy at 8952 (I counted the `·`-separated entries: **exactly 86** — `L4-02` `L4-T203` is right), invariant 46 at 9514 (`L4-04`), the §97.4 table at 8960–8967 (`L4-04` §3.2), §67.2 categories 5583–5590, §69.2 line 5720, D102 at 10195, D111 at 10209, §84.6 line 7478, §67.3 lines 5601/5603, AT-046 at 9368, AT-104 at 9374, AT-105 at 9375, AT-107 at 9377, AT-075 at 9406, SIG-06 at 4535, SIG-17 at 4546, SIG-41 at 4570, SIG-42 at 4571, SIG-46 at 4575, D77 arming discipline at 4524, D88 at 10181, D89 at 10182, D107 at 10205, §103 preamble at 9776 (the quoted sentence is genuine and complete), §52.6 rows 4626 and 4639. **No fabricated section, AT id, SIG id, invariant number or D id was found anywhere in the lane** — the failure is line-number drift, not invention.

`L4-06` D-L4-TL-4's report of the **SIG-43 double assignment is correct and verified**: line 4571 ends with a `SIG-43 | Unclosed learning-loop items` row and line 4572 opens a second `SIG-43 | Founder operating load` row; lines 4594, 4611 and 10197 all read it as Founder operating load. That decision is real and must go to L0.

**Correction.** Regenerate every line citation in `L4-00-charter.md` §7/§8 and `L4-06-tasks.md` §3 by grep against the spec, the way `L4-02`/`L4-03`/`L4-04` were. `L4-06` §3 is the file an executor is told to prove its work against; a wrong anchor there sends a low-cost agent to the wrong paragraph and it has no authority to notice.

---

### D8 — CRITICAL — Two incompatible designs ship for the attention ledger and for the Ready-queue-miss detector

| Field | Value |
|---|---|
| **File / task id** | `L4-04` `L4-T402`–`L4-T417` vs `L4-06` `L4-P6-01`–`L4-P6-15` and `L4-P5-05`–`L4-P5-13` |

**Problem.** The same two DoD rows (DoD-6/DoD-7 and DoD-8) are specified twice with different file sets:

| Deliverable | `L4-04` design | `L4-06` design |
|---|---|---|
| Categories | `metrics/attention/taxonomy.yaml` | `metrics/attention/categories.yaml` |
| Config | `metrics/attention/calibration.yaml` (every threshold, no literals in code) | `metrics/attention/calibrated.yaml` (inside `L4-P6-03`) |
| Derivation | `metrics/attention/lib/{config,sessions,precedence,attribute,reconcile,selfreport}.py` + `derive.py` | `metrics/attention/{sessions,granularity,precedence,attribution,reconcile,instrument_defect,flags,selfreport,apportion,collection_cost,provenance}.py` |
| RQM detector | `tools/records/rqm-contract.yaml` + `tools/records/rqm-detect` (`L4-T416`/`L4-T417`) | `tools/records/rqm/{detect,limb_pickup,limb_completion,carveout_planned,carveout_blocked,bypass,cause_prompt}.py` (`L4-P5-05`–`L4-P5-11`) |

Only the `L4-04` set has bodies. `L4-05` §2.2 explicitly refuses to write `L4-P5-05`–`L4-P5-13` (*"This file does not restate them and must not renumber them"*), so those nine tasks have criteria, a DoD row, a `L4-07` test suite — and no instructions in the entire lane.

**Correction.** Delete one design. `L4-04`'s is the one with bodies, with the D102 calibrated-configuration discipline, and with its command-line contract already pinned by `L4-07` `L4-P7-T09`/`L4-P7-T10`. Rewrite `L4-06` Phase 5 rows 70–78 and all of Phase 6 to index `L4-T402`–`L4-T417`.

---

### D9 — HIGH — `L4-T004` writes README files in the charter and `.gitkeep` files in `L4-06`

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` `L4-T004`; `L4-06-tasks.md` §2 row 4 and §3 |

**Problem.** Charter `L4-T004` writes `schemas/records/README.md`, `metrics/README.md`, `tools/records/README.md`, and its SELF-VERIFY demands `READMES=3 / FOREIGN=0 / CHANGED=3`. `L4-06` row 4 lists `Files touched` as `schemas/records/.gitkeep`, `metrics/.gitkeep`, `tools/records/.gitkeep`, and its §3 acceptance reads *"The three owned roots exist in `control-plane` and contain nothing but `.gitkeep`."* Either instruction fails the other's acceptance check. **Correction:** pick one (READMEs are more useful and already cite `PARTITION.md` line 20, which criterion 3 checks) and make both files say it.

---

### D10 — HIGH — The same files are authored by two different tasks in two different documents

| Field | Value |
|---|---|
| **File / task id** | `tools/records/record-write`, `event-append`, `test-rvr.sh`, `test-rqm-detector.sh`, `metrics/taxonomy/event-types.yaml`, `metrics/attention/sources.yaml` |

**Problem.**

| File | Claimed by | And by |
|---|---|---|
| `tools/records/record-write`, `event-append` | `L4-03` `L4-T305` (as guarded wrappers over `emit.sh`) | `L4-06` `L4-P4-03`, `L4-P4-05` |
| `tools/records/test-rvr.sh` | `L4-03` `L4-T307` | `L4-06` `L4-P4-06` |
| `tools/records/test-rqm-detector.sh` | `L4-07` `L4-P7-T10` | `L4-06` `L4-P5-12` |
| `tools/records/fixtures/rqm/**` | `L4-07` `L4-P7-T10` | `L4-06` `L4-P5-12` |
| `metrics/attention/test-derivation.sh` | `L4-07` `L4-P7-T09` | `L4-06` `L4-P6-15` |
| `metrics/taxonomy/event-types.yaml` | `L4-02` `L4-T203` (Phase 2) | `L4-06` `L4-P3-01` (Phase 3) |
| `metrics/attention/sources.yaml` | `L4-04` `L4-T403` | `L4-06` `L4-P6-02` |

`L4-04` §2.1 correctly anticipates this and forbids re-authoring — but it can only police the documents it names. `L4-06` names none of them and would have a second executor write every one of these a second time.

**Correction.** Once D1 is resolved this mostly dissolves; the residue is the event-types.yaml phase placement (Phase 2 per `L4-02`, Phase 3 per `L4-06` and the charter §5.1). Fix that one explicitly — `L4-02` `L4-T204` generates `event-type.enum.json` from it and cannot wait for Phase 3.

---

### D11 — HIGH — 31 open DECISION REQUIRED items across six namespaces, three of which collide

| Field | Value |
|---|---|
| **File / task id** | charter §9 `D-L4-01/02/03`; `L4-01` §DECISION `D-L4-01/02/03`; `L4-02` §4 `D-L4-04`–`D-L4-07`; `L4-03` §5 `D-L4-P3-01`–`03`; `L4-04` §5 `D-L4-P4-01`–`04`; `L4-05` §6 `D-L4-P5-01`–`05`; `L4-06` §1 `D-L4-TL-1`–`6`; `L4-07` `D-L4-P7-01`–`03` |

**Problem.** `D-L4-01`, `D-L4-02` and `D-L4-03` each name **two entirely different decisions** — the charter's (event-type enum publication / metric register boundary / `.github` inside the records repo) and `L4-01`'s (org login / commit-signing mechanism / key custody). `L4-02` then extends the numbering with `D-L4-04`–`D-L4-07` without saying which of the two series it continues, and `L4-03`/`L4-04`/`L4-07` all reference bare `D-L4-01/02/03` in their prose. `L4-06` D-L4-TL-2 correctly identifies the collision and routes it to L0 — but does not itself resolve it, and then `L4-06` §1 lists only 6 + 3 = 9 of the **31** open decisions, so the L0 decision queue built from `L4-06` will be missing 22 items. SIG-43 is raised three separate times (`D-L4-TL-4`, `D-L4-P7-02`, and by implication in `L4-05`).

**Correction.** L0 renumbers into one namespace, publishes a single lane-wide decision register, and `L4-06` §1 becomes the index of it rather than a partial restatement.

---

### D12 — HIGH — Tasks requiring console sessions, org-owner rights and interactive input are not marked ASSISTED

| Field | Value |
|---|---|
| **File / task id** | `L4-01-records-repo.md` `L4-P1-T02`, `L4-P1-T05`, `L4-P1-T06`, `L4-P1-T08`, `L4-P1-T09`, `L4-P1-T10`, `L4-P1-T11` |

**Problem.** `L4-05` §3 defines a two-mode split (**LANE** / **ASSISTED**) and states it is *"deliberately identical"* to `L5-06-tasks.md`, with the rule: *"If you find yourself about to type … an SSH session … or a GitHub organisation-owner URL — stop; it is ASSISTED."* `L4-01` predates that convention and marks nothing. Yet:

- `L4-P1-T09` is explicitly a **browser console operation** (*"There is no `gh` command that creates an App from nothing"*), requires org-owner rights, requires downloading a private key from a browser, and then runs **`read -r -p "App ID …"`** twice — a blocking interactive prompt that a non-interactive agent cannot answer.
- `L4-P1-T09` also runs `mv "$HOME/Downloads/"records-writer-*.private-key.pem …`, which depends on the executor having a browser and a Downloads directory.
- `L4-P1-T10` is a five-step console click-through in GitHub organisation settings.
- `L4-P1-T02`, `T05`, `T06`, `T08` all require org-admin API rights the lane's own EXT-02 says must be granted by L0.
- `L4-P1-T11` mints and handles a live installation token and asserts on `403` vs `404`.

Per the reviewer's own brief this ASSISTED marking is mandatory for L5; it is equally load-bearing here, because a low-cost agent that cannot complete `L4-P1-T09` will either stall on the `read` prompt or improvise around it, and the STOP rule for improvisation is exactly the credential-exposure incident `L4-P1-T09`'s own STOP rule describes.

**Correction.** Add `L4-05` §3's mode column to `L4-01` §0.3 and `L4-06` §2, mark `L4-P1-T02`, `T05`, `T06`, `T08`, `T09`, `T10`, `T11` **ASSISTED**, and split each into (a) a LANE task that produces the request artifact and the evidence template and (b) the human-executed console session. Replace the two `read -r -p` prompts with L0-supplied environment variables in §0.1, exactly as `ORG` is handled.

---

### D13 — HIGH — Broken command syntax in ~14 acceptance commands

| Field | Value |
|---|---|
| **File / task id** | `L4-06-tasks.md` §2 rows 2, 3, 9, 11, and §4.3 rows `L4-T002`, `L4-T003`, `L4-P1-T01`, `L4-P1-T09`; `L4-00-charter.md` `L4-T007` |

**Problem.**

1. **`gh api … --jq -r <expr>`** — `--jq` takes the jq expression as its value. Written as `--jq -r .private`, the expression becomes the literal string `-r` and `.private` is parsed as a positional argument. Every such command errors rather than printing `true`. Appears in `L4-06` §2 rows 2, 3, 9, 11 and §4.3 rows `L4-T002`, `L4-T003`, `L4-P1-T01`. Correct forms are `--jq .private` or `-q .private`. (`L4-01` gets this right everywhere: `--jq -r '.login'` with the expression quoted is still wrong, but `--jq -r .login` at `L4-01` line 176 has the same bug — worth a sweep of both files.)
2. **`gh pr create --repo-dir "$CP_ROOT"`** and **`gh pr view --repo-dir …`** (charter `L4-T007`, five occurrences) — **`--repo-dir` is not a `gh` flag.** The flag is `--repo <OWNER/REPO>`; a working directory is set by `cd`, not by a flag. `L4-01` `L4-P1-T12` uses the correct `gh pr create --repo "${CP_SLUG}"`.
3. `L4-06` §2 row 4 acceptance is `ls -1 schemas/records metrics tools/records` (prints contents, no assertion) while §4.3 uses `ls -1d … | wc -l` → `3`. Only the second is checkable.

**Correction.** Sweep both files for `--jq -r` and `--repo-dir`; make every acceptance command an assertion with a single unambiguous stdout line.

---

### D14 — HIGH — The charter's seeded-canary self-verify runs `rm -rf` against another lane's directory

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` `L4-T005` SELF-VERIFY, lines 578–584 |

**Problem.** The negative test does:

```bash
mkdir -p "$CP_ROOT/reconciler" && echo x > "$CP_ROOT/reconciler/SEEDED-FOREIGN.txt"
git -C "$CP_ROOT" add reconciler/SEEDED-FOREIGN.txt
git -C "$CP_ROOT" commit -q -m "SEEDED negative test - to be reverted"
…
git -C "$CP_ROOT" reset --hard HEAD~1
rm -rf "$CP_ROOT/reconciler"
```

`reconciler/**` is **L3's exclusive path** (`PARTITION.md` line 19). On merge-train cycle 1 the directory does not yet exist on `integration` and this is harmless. On **every subsequent cycle it does**, and this block: (a) `reset --hard` restores L3's tracked files, then (b) `rm -rf` deletes L3's entire reconciler tree from the working tree, leaving the branch dirty with deletions that the `REVERTED=0` check (which only greps the *committed* diff) will not catch. The following task's `git status --porcelain` cleanliness assertions then fail for a reason the executor has no instruction to diagnose. `git reset --hard` also silently discards any uncommitted work.

The intent — a check that cannot fail is not a check (§53.1 line **4680**, cited by the charter as 4685) — is correct and should be kept.

**Correction.** Seed the canary at a path no lane owns and that is guaranteed absent, e.g. `docs/_L4-SEED-CANARY.txt` (L0's path, still foreign to L4, still trips the `OWNED` regex), and revert with `git restore --staged`/`git rm --cached` + a targeted `rm -f` of the single seeded file — never `rm -rf` a directory and never `reset --hard`.

---

### D15 — HIGH — Two irreconcilable workspace conventions, each declared "binding"

| Field | Value |
|---|---|
| **File / task id** | `L4-00-charter.md` §10 "Fixed workspace convention (binding for this lane)"; `L4-06-tasks.md` §0.1; `L4-02` §3.1; `L4-03` §2; `L4-04` §2; `L4-05` §0.1; `L4-07` §0.1 |

**Problem.** Two root sets are in play:

- `CP_ROOT="$HOME/src/control-plane"`, `CPR_ROOT=".../repos/control-plane-records"` — charter §10 (*"binding for this lane"*), `L4-02`, `L4-03`, `L4-04`.
- `WORK="$HOME/l4work"`, `CP_DIR="$WORK/control-plane"`, `RECORDS_DIR="$WORK/control-plane-records"` — `L4-01` §0.1, `L4-06` §0.1, `L4-05` §0.1.

`L4-07` §0.1 notices and aliases them (`export CP_ROOT="$CP_DIR"`), which is the right instinct but only papers over it inside that one file. An executor running charter `L4-T002` (clones into `C:/D_Drive/.../repos/`) and then `L4-01` `L4-P1-T03` (`rm -rf "${RECORDS_DIR}"; gh repo clone … "${RECORDS_DIR}"` into `$HOME/l4work/`) ends up with **two clones of the records repository** and a `--stores` check pointed at whichever `CPR_ROOT` was exported last.

**Correction.** One convention, declared once, in the charter, adopted verbatim by all seven other files — as `L4-05` §0.1 already does for `$WORK`/`$CP_DIR` and `$L4_VENV`.

---

### D16 — HIGH — Phase numbers mean different things in different files, and two task ids differ by one character

| Field | Value |
|---|---|
| **File / task id** | `L4-03` (Phase 3), `L4-04` (Phase 4), `L4-05` (Phase 5), `L4-07` (Phase 7) vs `L4-06` §2 phase column |

**Problem.**

| Phase number | `L4-06` says | The phase file says |
|---|---|---|
| 2 | record and event schemas | `L4-02`: record and event schemas ✓ |
| 3 | taxonomy, freshness, signals, anchor, retention | `L4-03`: **write paths** (`L4-06`'s Phase 4) |
| 4 | writers and the dispatch handler | `L4-04`: **the attention ledger** (`L4-06`'s Phase 6) |
| 5 | work tracking + RQM detector | `L4-05`: ingest + work tracking (partial overlap) |
| 7 | the metric register and §103 computations | `L4-07`: **test strategy and runbook** (`L4-06`'s Phase 8) |

Consequently the exit gates in `L4-06` §5 (P3 = taxonomy/freshness/retention; P4 = writers) name commands built in documents labelled with different phase numbers, and `L4-01`'s Phase-1 exit gate is the only one both files agree on.

Worse, `L4-07`'s task ids are **`L4-P7-T09`** while `L4-06`'s Phase-7 ids are **`L4-P7-09`** — one character apart, different tasks, different files, both live. `L4-04` §2.2 cites `L4-P7-T09` and `L4-P7-T12` as binding contracts; a reader who resolves those against `L4-06` §2 lands on "Restore measures" and "Security-review measures".

**Correction.** Renumber as part of D1. Never let two live task ids in one lane differ only by an inserted `T`.

---

### D17 — MEDIUM — Charter `L4-T002` acceptance criterion 1 expects `17` from a command that returns `18`

`L4-00-charter.md` `L4-T002`, acceptance row 1: `find "$CPR_ROOT/records" -type d | wc -l` → expected `17`. The loop creates 17 directories under `records/`, and `find` also counts `records/` itself: the command returns **18**. The row's own parenthetical (*"16 under `records/` counting `records/` itself plus `pending/`"*) is a third, also-wrong count. The SELF-VERIFY block uses a different command and is right. **Correction:** delete the criterion or change the expected value to `18`.

### D18 — MEDIUM — `L4-P1-T12` acceptance row 3 says "Four files added" and expects `5`

`L4-01-records-repo.md` `L4-P1-T12`, acceptance row 3. The parenthetical correctly enumerates five files. **Correction:** change the label to "Five files added".

### D19 — MEDIUM — `L4-06` `L4-T006` acceptance requires a CSV column the charter's CSV does not have

`L4-06-tasks.md` §3 `L4-T006`: *"Every spec section … appears as one CSV row carrying section, line range, **obligation** and owned path."* The charter's `l4-spec-coverage.csv` header is `section,line_start,line_end,owned_path` — four columns, no obligation. **Correction:** add the column to the charter heredoc or drop it from the criterion. (Note the CSV also inherits every wrong line range from **D7**, and its `OVERFLOW` check against 10,214 will pass regardless, so the manifest cannot detect its own errors.)

### D20 — MEDIUM — `L4-06` §2 claims to be complete and omits 25 tasks that have bodies

`L4-05` §"Task ids" states it adds `L4-P5-14`…`L4-P5-24` (11 tasks) and `L4-07` §0.3 defines `L4-P7-T01`…`L4-P7-T14` (14 tasks). Neither set appears in the 117-row table `L4-06` line 245 titles *"Master task table — all 117 tasks in execution order"*, nor in the §5 exit gates, nor in the §6 DoD map. **Correction:** fold into D1's renumbering; the header must state the real count.

### D21 — MEDIUM — 17 vs 18 store schemas, and `store-map.yaml` vs `store-inventory.yaml`

`L4-02` §2.1 and §3.3 produce **18** schema files (17 stores incl. a separate `decision-pending.schema.json`, plus the event envelope) indexed by `schemas/records/store-map.yaml` with 19 rows <!-- 19 per FD-059 (bootstrap/ counts as a store) -->. `L4-06` `L4-P2-13` instead folds `pending` into `decision.schema.json` (*"with the `pending` sub-store state"*) and `L4-P2-06` builds `schemas/records/store-inventory.yaml` with 17 rows. `L4-07` `L4-P7-T04` says *"all 19 stores"*. Three counts, two filenames, one deliverable. **Correction:** `L4-02`'s split (a pending record genuinely lacks `decided`, `options_considered` and `evidence`, and its `prompt_received` requirement is load-bearing for §103.8 queue age) is the better design; adopt it and delete `store-inventory.yaml` from `L4-06`.

### D22 — MEDIUM — Output-string collisions that trip `L4-06` §4's "expected stdout, exactly" rule

Beyond D3: `PATHS OK` is emitted both by `lane-selfcheck.sh --paths` (charter) and, as `PATHS OK 19/19`, by `L4-03`'s `validate-write-paths.sh`; `COVERAGE OK` appears as three different strings (`COVERAGE OK`, `COVERAGE OK 19`, `COVERAGE OK 19/19`) across `L4-06`, `L4-02` and `L4-03` <!-- 19 per FD-059 (bootstrap/ counts as a store) -->; `NEGATIVE OK 10/10` (charter, `L4-06`) vs `NEGATIVE 10/10` (`L4-02` exit gate). `L4-07` §0.6 ("Output strings this phase must not change") is the right mechanism and should be promoted to lane-wide scope. **Correction:** one frozen grammar table, owned by the charter, referenced by every other file.

### D23 — LOW — Off-by-one citations inside the otherwise-accurate phase files

`L4-02` cites §97.3 line **8947** for *"Every entry in the taxonomy below has exactly one stable `event_type` identifier"* (actual **8948**); its store-task field tables cite **8875** for the base four (correct) while its own §1 and §3.4 cite **8890** (wrong) — the file disagrees with itself. `L4-04` §3.2 cites the tracked-events list at line **8951** (actual **8952**; 8951 is blank). `L4-05` cites invariant 46 at **9513** (actual **9514**). `L4-03` cites *"a record is never edited in place"* at **8890** (actual **8875**). **Correction:** sweep with grep; these are cheap and each one sends an executor to the wrong paragraph.

### D24 — LOW — `L4-06` `Deps` column mixes task ids, decision ids and ranges

Rows carry `D-L4-TL-5A`, `D-L4-TL-3`, `D-L4-TL-1` (decision ids, not tasks), `L4-P2-03…L4-P2-28` and `L4-P6-01…L4-P6-14` (ranges, not enumerations), and `every task above` (row 115). None of these is machine-resolvable, and a dependency-order checker cannot be written against the column. **Correction:** enumerate task ids only; move decision blockers to a separate `Blocked by` column, as the charter's `L4-T003` already does.

---

## 3. Missing controls

Every task **that has a body** carries both a SELF-VERIFY block and a STOP rule: charter 7/7, `L4-01` 12/12, `L4-02` 25/25 (via the §6.1 template, correctly declared once and referenced), `L4-03` 16/16, `L4-04` 18/18, `L4-05` 15/15, `L4-07` 14/14. The template-once-reference-many pattern in `L4-02` §6.1 and the universal dispatcher in `L4-06` §0.6 are both legitimate and well executed.

**The gap is D2 and D8**: the 98 `L4-06` rows without bodies have no *task-specific* STOP condition and no *task-specific* expected output — only the universal `CHECK <id> PASS / exit=0`, which cannot fire because `tools/records/checks/<TASK-ID>.sh` is written by the missing task itself. For those 98 rows the control structure is circular: the check file that proves the task is created by the task that has no instructions.

---

## 4. Judgment leakage

`L4-02` §4, `L4-03` §5, `L4-04` §5, `L4-05` §6 and `L4-07` §DECISION each state a stated default that ships if no answer arrives, so no executor is left choosing. `L4-02` §3.5's "RESOLVED CONFLICT — do not re-litigate" and `L4-04` §3.5's "Resolved conflicts — do not re-open" are exactly right. Two leaks remain:

- **D12** (console/credential tasks unmarked ASSISTED) — the main one.
- `L4-06` `L4-P2-06`, `L4-P3-04`, `L4-P7-01` and the other 95 body-less rows require the executor to *design* the artifact from an acceptance criterion. `L4-06` §0.7's standing STOP rule (*"the task would require you to design, choose or interpret anything"*) means a compliant executor must file a blocker on all 98 — which is, at least, the correct behaviour.

---

## 5. Executability — the two most complex tasks

**(a) `L4-04` `L4-T411` — `derive.py`, the attention ledger (Size L).** **PASS.** An agent with no context can complete it. Its command line and JSON shape are declared *input* to the task, pinned by `L4-07` `L4-P7-T09`/`L4-P7-T12`; the three input shapes and the mode each selects are tabulated; the key-presence rule is derived from named fixtures rather than chosen; the `--query-product` worked example gives the literal expected value (`1.25 + 0.25 + 0.75 + 0.50 = 2.75`); the full source of `selfreport.py` and `derive.py` is in the heredoc; every threshold comes from `calibration.yaml` and check C8 proves no numeric literal survives in code. This is the standard the rest of the lane should be held to. Its one dependency risk is that `L4-06` never mentions it (D1) and `L4-06`'s competing `L4-P6-*` design would produce a different `derive.py`.

**(b) `L4-06` `L4-P7-01` — "Metric declarations — the eight attributes per measure" (Size L).** **FAIL.** The agent is given a title, a target path (`metrics/register/metric-declarations.yaml`), a dep (`L4-P3-06`, itself body-less), and an acceptance command (`bash metrics/register/validate-sources.sh --attributes`) for a script that no task creates. §3's criterion — *"Every declared measure carries all eight attributes … A measure carrying seven is rejected"* — never says **which measures**, and §103 spans 200 lines and ~60 measures. The executor must decide the measure set, the YAML shape, the attribute vocabulary, the source-store mapping and the validator's design, then write the validator that judges its own output. Under `L4-06` §0.7 the only compliant action is a blocker. The same verdict applies to `L4-P8-02` ("DoD matrix runner", deps: *"every task above"*), whose acceptance command `bash tools/records/run-dod-matrix.sh` must execute all 20 charter DoD rows — six of which (D3) name commands that do not exist and five of which (D2) test artifacts nothing builds.

---

## 6. Minimum repair set before dispatch

1. **D1** — one task-id namespace; `L4-06` §2 rebuilt as an index of tasks that exist.
2. **D2** — author the missing metric-register/freshness/signals/retention phase, or descope DoD-5/13/14/15/19 and the `L4-07` suites that test them.
3. **D3 + D4 + D22** — one frozen output grammar and one validator mode list, agreed by the charter, `L4-02` and `L4-06`.
4. **D5** — settle 18 vs 19 and fix all five documents.
5. **D6** — correct charter DoD-8 against §97.5 line 8984.
6. **D7 + D23** — regenerate every line citation by grep.
7. **D8** — delete the duplicate attention-ledger and RQM designs; keep `L4-04`'s.
8. **D12** — add the ASSISTED mode column and split the seven credential/console tasks.
9. **D9, D10, D11, D13, D14, D15, D16** — each is a small, mechanical fix, but each one STOPs a task that would otherwise pass.

Phase 0 and Phase 1 can be dispatched independently **after** D4, D5, D9, D12, D13, D14 and D15 are fixed — that subset is self-contained and would let the records repository stand up while the rest is repaired. Phases 2 onward cannot be dispatched at all until D1, D2, D3 and D8 are resolved.
