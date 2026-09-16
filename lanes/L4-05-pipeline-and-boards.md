# L4-05 — PHASE 5: INGEST AND WORK TRACKING

**Lane:** L4 — Records, Events and Metrics. Subsystems **I** (Metrics pipeline) and **N** (Work tracking conventions) — Master Spec §99.2, lines 9196 and 9201.
**Phase:** 5 — the ingest half of subsystem I, and the board/horizon/Ready half of subsystem N.
**Branch prefix:** `lane/4/05-*` — one branch per task, `PARTITION.md` line 34.
**Task ids:** `L4-P5-01`…`L4-P5-04` (work tracking, already indexed as rows 66–69 of `L4-06-tasks.md` §2) and `L4-P5-14`…`L4-P5-24` (ingest, added by this file).
**Authority order:** `PARTITION.md` (FROZEN) > `MultiProduct_MasterSpec_v4.0.md` > `L4-00-charter.md` > `L4-06-tasks.md` > this file. Where this file appears to differ from `PARTITION.md`, `PARTITION.md` wins and the difference is a blocker for L0.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines). Every line number below was located with `grep`/`sed` and is cited, not inferred.

---

## 1. Why this phase exists

Two rows of the §99.2 build-surface table, verbatim:

> **I | Metrics pipeline |** *"DevLake nightly ingest; Prometheus scraping `/health`, `/version`, `/metrics`; Scorecard scheduled scan with drop detection; the event-log taxonomy; attention ledger; metric source discipline"* — line 9196
>
> **N | Work tracking conventions |** *"Boards per product plus portfolio aggregate (or the single-Project fallback), horizon semantics, Ready-to-Execute definition, automatic Ready-queue-miss recording"* — line 9201

Phases 3 and 4 built the taxonomy and the writers. Phase 6 builds the attention ledger. **Phase 5 builds the two halves those phases do not touch: what the machine instruments are allowed to feed the metric layer, and what a board column means.**

Three spec obligations are discharged here and nowhere else:

| Obligation | Spec anchor |
|---|---|
| DevLake connector field coverage is an **unverified capability assumption**, *"confirmed before the phase depending on it"*, and is a named dependency of Phase G3 | §30.3 line 2737; §99.3 item 4, line 9243; §98 Phase G3, line 9133 |
| The three runtime endpoints are *"the entire runtime interface the operating system requires of a served product"*, are **not a public surface**, and are scraped over the private path with a per-product scrape credential | §41.2, lines 3719–3728 |
| An item is Ready only on **all ten** criteria, and a banded estimate is captured at Ready confirmation for normal planned work only (D79) | §29.3, lines 2655–2666; D79, line 10162 |

And one rule binds every task in the file — **metric source discipline**, invariant 46 (§101.7, line 9513):

> *"Derived data is computed, never hand-maintained. Metrics derive from the canonical record stores of Section 97 (Records, Events and Data Conventions), never from hand-maintained numbers."*

restated at the §103 preamble (line 9776): *"Every metric derives from the canonical record stores and event log of Section 97 — never from hand-maintained numbers."*

DevLake, Prometheus and Scorecard are **not** §97 record stores. §103.1 and §103.2 nonetheless name DevLake in a column headed *"Source (record store)"* (lines 9782, 9787 and 9794). That is the tension this phase resolves mechanically, in `L4-P5-22`, and it is why the collector declarations are built before the register that reads them.

---

## 2. Scope

### 2.1 Paths this phase writes — nothing else

| Repository | Path | Written by |
|---|---|---|
| `control-plane` | `metrics/boards/**` | `L4-P5-01`…`L4-P5-03` |
| `control-plane` | `metrics/ingest/**` | `L4-P5-14`…`L4-P5-23` |
| `control-plane` | `tools/records/boards/**`, `tools/records/ingest/**` | limb modules |
| `control-plane` | `tools/records/validate-boards.sh`, `tools/records/validate-ingest.sh`, `tools/records/estimate_capture.py` | dispatchers and the D79 capture point |
| `control-plane` | `tools/records/checks/L4-P5-*.sh` | one new file per task, §0.4 |

`metrics/**` and `tools/records/**` are L4-owned by `PARTITION.md` line 20. Nothing in `control-plane-records` is written by this phase.

### 2.2 Explicitly NOT in scope

| Item | Owner | Why, with citation |
|---|---|---|
| The Ready-queue-miss detector — `L4-P5-05`…`L4-P5-13` | L4, elsewhere | Already indexed as rows 70–78 of `L4-06-tasks.md` §2, with acceptance criteria `L4-P5-05`…`L4-P5-13` in its Phase 5 table and charter DoD-8. **This file does not restate them and must not renumber them.** The `metrics/boards/**` files built here are the detector's input. |
| Installing DevLake, Prometheus, Grafana or Scorecard; the compose file; the required database engine | L5 (subsystem M) | §99.2 line 9200 places the operations VM in subsystem M; `PARTITION.md` line 21 gives `ops-vm/**` to L5. `L4-06-tasks.md` §7 already routes *"Grafana dashboards, DevLake ingest configuration, Prometheus scrape configuration"* out of L4. |
| Every Grafana surface that reads these declarations | **no lane** | Subsystem H (§99.2 line 9195) is assigned to no lane in `PARTITION.md` v1. See **DECISION REQUIRED D-L4-P5-03**. |
| `registries/os-health.yaml` (the metric register) and `registries/economics.yaml` (the estimate band vocabulary) | L1 | `PARTITION.md` line 17. L4 **reads** them and **publishes content for** them; it never writes them. Charter `D-L4-02`. |
| The §103 measure computations and the register itself | L4 Phase 7 | `L4-P7-01`…`L4-P7-14`. This phase publishes `metrics/ingest/source-kinds.yaml` as their input. |
| Any `.github/workflows/**` file that schedules a nightly ingest | L2 | `PARTITION.md` line 18. |

### 2.3 The one paragraph that keeps this phase honest

L4 **declares**; L5 **installs**; H **renders**. Every artifact in this phase is a declaration file plus a validator that proves the declaration is internally consistent and spec-conformant. No task in this phase connects to DevLake, scrapes an endpoint, or runs a Scorecard scan from a lane branch. The three tasks that need a live system are marked **ASSISTED** (§3) and produce a request document and an evidence template, never an executed session.

---

## 3. Execution modes — and the ASSISTED rule

| Mode | Who executes | Meaning |
|---|---|---|
| **LANE** | you, the Sonnet-4.6-class executor | Every command in the task is runnable from a lane branch with no credential beyond `gh auth` on `control-plane`. |
| **ASSISTED** | **L0 human lead**, after you prepare | Requires a credential, a console session or a host a low-cost agent must not hold. You produce the request artifact and the evidence template only, then **stop and hand off**. |

This is the same two-mode split `L5-06-tasks.md` §1 uses; the wording is deliberately identical so the two lanes read the same way to the same executor.

**You never execute an ASSISTED task's console steps.** You produce its artifact, commit it, and open the handoff issue. If you find yourself about to type a DevLake admin password, a Prometheus scrape credential, an SSH session into the operations VM, or a GitHub organisation-owner URL — **stop; it is ASSISTED.**

### 3.1 The three ASSISTED tasks of this phase

| Task | What it needs that you must not hold |
|---|---|
| `L4-P5-17` | DevLake admin console or API on the operations VM, plus the connector's configured GitHub token — to enumerate which connector fields actually land (§99.3 item 4, line 9243) |
| `L4-P5-19` | An SSH session on the operations VM and the per-product scrape credential — to prove the three endpoints answer over the private path and are unreachable publicly (§41.2 line 3726; §19.2 line 1892) |
| `L4-P5-21` | A GitHub organisation-owner session — to confirm Scorecard behaviour against **private** repositories and to run the baseline scan (§30.3 line 2737; §98 Phase 2, line 9029) |

**ASSISTED evidence rule.** You never author the evidence file. The human pastes it; your validator reads it. A validator that passes on an evidence file you wrote is not a check (`L4-06-tasks.md` §0.8 rule 9).

---

## 4. Reader contract

You are executing, not designing. Every command is literal and copy-pasteable. Run them in **Git Bash** (POSIX `sh`), not `cmd.exe` or PowerShell. If any step requires you to choose, name, invent or interpret something not written here, **STOP** and file the blocker of §0.5. Do not guess. Do not substitute a similar command. Do not relax a failing acceptance check.

### 0.1 Workspace — export before every task

The shell resets between calls. Re-export these at the start of **every** task. Always use absolute paths.

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP_REPO="control-plane"
export CP_SLUG="${ORG}/${CP_REPO}"
export WORK="$HOME/l4work"
export CP_DIR="${WORK}/${CP_REPO}"
export L4_VENV="C:/D_Drive/PS/MultiProduct/Code/.l4-venv"
L4_PY="$L4_VENV/Scripts/python.exe"; [ -x "$L4_PY" ] || L4_PY="$L4_VENV/bin/python"
export L4_PY
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
echo "CP_DIR=$CP_DIR L4_PY=$L4_PY"
```

`$L4_VENV` is the virtualenv fixed by `L4-02-record-schemas.md` §3.2 — **outside both repositories, never committed**. `$WORK`/`$CP_DIR` are fixed by `L4-06-tasks.md` §0.1. Both conventions already exist in this lane; this file adopts them and creates no third one.

If `ORG` prints as the literal placeholder, **STOP** — `D-L4-TL-5` has not been answered.

### 0.2 Path ownership (hard)

In `control-plane` you may create or edit files **only** under `schemas/records/**`, `metrics/**`, `tools/records/**`. You may read anything. A pull request touching a foreign path fails the lane-guard check (`PARTITION.md` rule 1, line 25). Run `bash tools/records/lane-selfcheck.sh --paths` before every commit and every push.

**Namespace-package rule** (`L4-06-tasks.md` §0.2): do **not** create `tools/__init__.py` or `schemas/__init__.py`. Every limb module in this phase is invoked **by file path** (`"$L4_PY" tools/records/boards/columns.py`), never by import, so no package file is ever needed.

**No shared mutable file, ever** (`PARTITION.md` rule 3). One file per collector, one file per board concept, one file per task check. No task appends to an index.

### 0.3 Deterministic output contract

Inherited verbatim from `L4-06-tasks.md` §0.5. Every executable this phase ships prints exactly one final line on stdout and sets its exit code from this table:

```
<NAME> OK <counters>        exit 0    the assertion held
<NAME> FAIL <counters>      exit 1    the module executed and the assertion did not hold
<NAME> ERROR <reason>       exit 3    the module could not execute (missing input, unreachable source)
```

Exit `3` is never a pass. A check that cannot reach its input **fails closed** (§40.1 line 3671). Any exit code other than 0, 1 or 3 is a crash and is a STOP.

`<NAME>` is `BOARDS` for `validate-boards.sh` and `INGEST` for `validate-ingest.sh`. Those two strings are frozen; changing either breaks the phase sweep of §10.

### 0.4 The universal SELF-VERIFY

`tools/records/check.sh` is the fixed dispatcher built in `L4-P2-01` (`L4-06-tasks.md` §0.6). **Every task in this file contributes exactly one new file `tools/records/checks/<TASK-ID>.sh`** — a new file, never an edit to a shared one. After the task's acceptance command passes and before you commit:

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh <TASK-ID>; echo "exit=$?"
```

**Expected output, exactly two lines, nothing else:**

```
CHECK <TASK-ID> PASS
exit=0
```

Any other output — `FAIL`, `ERROR`, a different exit, extra lines — is a STOP.

### 0.5 STOP rule and blocker template

**Standing STOP rule.** Stop, commit nothing, and file the blocker below if: the task's stated STOP condition occurs; any command errors in a way the task does not describe; a file you must edit is outside §0.2; the universal SELF-VERIFY prints anything other than the two expected lines; a spec fact you need is not written in this file; or the task would require you to design, choose or interpret anything. Do not guess, do not substitute, do not work around, do not proceed to the next task.

```bash
set -euo pipefail
gh issue create --repo "${CP_SLUG}" --title "BLOCKER <TASK-ID>: <one-line symptom>" --label blocker,lane-4 --body "$(cat <<'EOF'
blocked_task: <TASK-ID>
lane: 4
phase: 5
branch: lane/4/05-<task-slug>
repo: control-plane
stop_condition_hit: <quote the STOP line from L4-05-pipeline-and-boards.md verbatim>
command_run: |
  <the exact command, copy-pasted>
observed_output: |
  <paste verbatim, do not summarise, do not redact anything except credentials>
expected_output: |
  <paste the SELF-VERIFY expected block verbatim>
files_touched_so_far: <exact paths, or "none">
state_left_behind: <branch pushed? commit made? or "none">
what_i_did_NOT_do: <the remaining steps of the task>
decision_required_from: L0
EOF
)"
```

Then take the next **unblocked** task, or idle. Never work around a blocker.

### 0.6 The standing git wrapper — every task, no exceptions

Open every task with:

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-<task-slug>
```

Close every task, after its acceptance command **and** its SELF-VERIFY pass:

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add <the exact files named in the task's Writes line>
git commit -m "<TASK-ID>: <task title>"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-<task-slug>
gh pr create --base integration \
  --title "<TASK-ID>: <task title>" \
  --body "Lane 4, Phase 5. Task <TASK-ID>. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

Each task below repeats these blocks with the slug and file list already filled in. Copy them as written. **Never merge or rebase another lane's branch** (`PARTITION.md` line 36).

### 0.7 Task index

| Task id | Title | Mode | Size | Depends on |
|---|---|---|---|---|
| `L4-P5-01` | Board conventions — seven columns, Blocked as a flag, Deploy rendered | LANE | M | `L4-P3-01` |
| `L4-P5-02` | Horizon semantics H1/H2/H3 and the `unplanned` rule | LANE | S | `L4-P5-01` |
| `L4-P5-03` | Ready-to-Execute definition as machine-checkable configuration | LANE | M | `L4-P5-01` |
| `L4-P5-04` | Estimate capture at Ready confirmation (D79) | LANE | M | `L4-P5-03`, `L4-P2-10` |
| `L4-P5-14` | Ingest entry gate, `metrics/ingest/` skeleton and the `INGEST` dispatcher | LANE | S | `L4-P5-03`, `L4-P3-06` |
| `L4-P5-15` | `collectors.yaml` — the three named collectors and their cadences | LANE | M | `L4-P5-14` |
| `L4-P5-16` | DevLake nightly ingest declaration and the §99.3 coverage gate | LANE | M | `L4-P5-15` |
| `L4-P5-17` | **ASSISTED** — DevLake connector field-coverage confirmation | ASSISTED | M | `L4-P5-16` |
| `L4-P5-18` | Prometheus scrape declaration — the three §41.2 endpoints | LANE | M | `L4-P5-15` |
| `L4-P5-19` | **ASSISTED** — private-path scrape reachability evidence | ASSISTED | S | `L4-P5-18` |
| `L4-P5-20` | Scorecard scheduled scan and drop detection | LANE | M | `L4-P5-15` |
| `L4-P5-21` | **ASSISTED** — Scorecard private-repository behaviour and baseline scan | ASSISTED | S | `L4-P5-20` |
| `L4-P5-22` | Metric source discipline — the `source_kind` rule and its validator | LANE | M | `L4-P5-16`, `L4-P5-18`, `L4-P5-20` |
| `L4-P5-23` | Ingest freshness and the three arming strings | LANE | M | `L4-P5-22` |
| `L4-P5-24` | Phase sweep, rebase, PR | LANE | S | all of the above |

Sizes: **S** under 1 hour, **M** 1–4 hours, **L** over 4 hours. No task spans a day.

**Ids `L4-P5-05`…`L4-P5-13` are deliberately absent from this file.** They are the Ready-queue-miss detector, indexed as rows 70–78 of `L4-06-tasks.md` §2. Do not create them here and do not renumber this file to close the gap.

---

## 5. Phase entry conditions

`L4-P5-01` proves rows E1–E5; `L4-P5-14` proves rows E6–E8. If any row fails, no task depending on it starts. **Do not create another phase's artifact to make a row pass.**

| # | Condition | Owner | Verify command | Required by |
|---|---|---|---|---|
| E1 | `$CP_DIR` is a git checkout of `control-plane` with an `integration` branch | L0 / L1 | `git -C "$CP_DIR" rev-parse --verify origin/integration` | every task |
| E2 | `tools/records/check.sh` exists and prints `CHECK X ERROR no-check-file` for an unknown id | `L4-P2-01` | `bash tools/records/check.sh ZZZ; echo "exit=$?"` | every task |
| E3 | `tools/records/lane-selfcheck.sh` exists and is executable | charter `L4-T005` | `test -x tools/records/lane-selfcheck.sh` | every task |
| E4 | `$L4_PY` runs and can `import yaml` | `L4-P2-02` | `"$L4_PY" -c "import yaml,sys;print(sys.version.split()[0])"` | every task |
| E5 | `metrics/taxonomy/event-types.yaml` exists | `L4-P3-01` | `test -f metrics/taxonomy/event-types.yaml` | `L4-P5-01` |
| E6 | `metrics/signals/sig-source-map.yaml` exists | `L4-P3-06` | `test -f metrics/signals/sig-source-map.yaml` | `L4-P5-14` |
| E7 | `schemas/records/estimate.schema.json` exists and requires both `elapsed` and `elapsed_net_blocked` | `L4-P2-10` | `"$L4_PY" -c "import json;d=json.load(open('schemas/records/estimate.schema.json'));r=set(d['required']);print('OK' if {'elapsed','elapsed_net_blocked'}<=r else 'MISSING')"` | `L4-P5-04` |
| E8 | `metrics/retention/retention-classes.yaml` exists | `L4-P3-07` | `test -f metrics/retention/retention-classes.yaml` | `L4-P5-23` |

If E5, E6, E7 or E8 fail, the phase that owns them has not merged to `integration`. **Do not create them here.** File the blocker naming the condition id.

---

## 6. DECISION REQUIRED — hand to L0. No L4 executor answers these.

Five questions. Each names a **stated default that ships if no answer arrives**, so no task in this phase is blocked on an answer. The `D-L4-P5-*` namespace is used to avoid the id collision recorded as `D-L4-TL-2`.

### DECISION REQUIRED D-L4-P5-01 — Scorecard scan results name no §97 record store

- **Fact.** §101.7 invariant 46 (line 9513) and the §103 preamble (line 9776) require every metric to derive from a canonical §97 record store. `grep -n "records/" MultiProduct_MasterSpec_v4.0.md` over the §97.2 store table (lines 8845–8869) returns **no** Scorecard store, and §52.2 (lines 4530–4576) carries **no** `SIG-` row whose source is Scorecard. Yet §92.3 line 8300 requires a Scorecard drop to arrive *"either as a decision prompt … or as an owned line on the Reliability dimension"*, and §19.2 line 1896 makes *"Scorecard at or above the declared minimum; no unresolved high findings"* a launch-readiness row.
- **Question.** Does a `records/scorecard/` store get added by a §97.2 table amendment, or does the Scorecard drop route to an existing store (and which), or does it remain a collector-only surface exempt from invariant 46?
- **L4 default that ships:** `metrics/ingest/scorecard.yaml` declares `source_kind: collector` and `source_store: PENDING-D-L4-P5-01`. `L4-P5-22`'s validator asserts the placeholder is **present**, not that it is resolved. The drop-detection measure therefore renders `unarmed — not yet instrumented` under D77 (§52.2 line 4524) and **cannot render as a miss**.
- **L4 must not:** create a `records/scorecard/` directory, add a store to `schemas/records/`, or route a Scorecard result into an existing store by resemblance.
- **Blocks:** nothing. Binding a store later is a `metrics/ingest/scorecard.yaml` field edit, not a rewrite.

### DECISION REQUIRED D-L4-P5-02 — "drop" has no declared magnitude

- **Fact.** §92.3 line 8300 says *"A Scorecard score drop"* and §17.3 line 1771 says *"Expect a Scorecard drop to remediate"*. Neither states how large a decrease is a drop, nor over what window. `security.scorecard_minimum` (§15.1, initial value `7.0`) is a **floor**, which is a different condition from a decrease.
- **Question.** What magnitude and window define a reportable drop, and does crossing `scorecard_minimum` route differently from a decrease above it?
- **L4 default that ships:** two separately named conditions, both literal readings of the two cited lines — `decrease`: any strictly negative delta against the previous recorded scan for that product; `below_minimum`: the new score is below that product's declared `security.scorecard_minimum`. Both are declared; `metrics/ingest/scorecard.yaml` records `routing_threshold: any_decrease` (D-L4-P5-02 decided).
- **Blocks:** nothing.

### DECISION REQUIRED D-L4-P5-03 — subsystem H, and the installation side of subsystem M, have no lane

- **Fact.** `PARTITION.md` §"The five build lanes" (lines 15–22) assigns subsystems A, B, C, D, E, F, I, K, L, M, N, Q, R. **G, H, J, O and P are assigned to no lane.** Subsystem **H** (§99.2 line 9195) is *"Dashboards and views | Grafana provisioned from JSON in git: every surface of Section 92"*, and its declared dependency list is `I, F, C` — it consumes exactly what this phase publishes. Separately, `PARTITION.md` line 21 gives `ops-vm/**` to L5, so the **installation** of DevLake, Prometheus and Scorecard is L5's, while their **declarations** are L4's.
- **Question.** Which lane owns subsystem H, and what is the handoff mechanism from `metrics/ingest/**` (L4) to the Grafana JSON (H) and to the collector configuration on the operations VM (L5)?
- **L4 default that ships:** this phase publishes declarations only, and `metrics/ingest/README.md` names the consumers as *"L5 for installation (`ops-vm/**`), subsystem H for rendering — H unassigned in PARTITION v1"*. L4 opens no Grafana file and no `ops-vm/**` file.
- **L4 must not:** claim subsystem H, write a dashboard JSON, or write anything under `ops-vm/**`.
- **Blocks:** nothing in this phase. It blocks anyone who expects a chart at the end of it.

### DECISION REQUIRED D-L4-P5-04 — the designated work-management system, and which board mode is selected

- **Fact.** §29.1 line 2625 says boards live *"in the designated work-management system"*. §29.1 line 2635 states the implementation dependency verbatim: *"confirm aggregation and filtering capability at the plan tier in use before Phase 1 of implementation … If aggregation is unavailable, the fallback is a single organisation-level project containing all items with a product field, and per-product filtered views — one board, many views, rather than many boards plus a manual roll-up."* That confirmation is a console action against a live plan tier; no executor can perform it from a lane branch.
- **Question.** Which system, which plan tier, and — after the confirmation — is `selected_mode` `aggregated` or `single_project_fallback`?
- **L4 default that ships:** `metrics/boards/board-conventions.yaml` declares **both** modes in full, sets `selected_mode: single_project_fallback` (D-L4-P5-04 decided) and `aggregation_confirmed: false`. `validate-boards.sh --columns` asserts both modes are declared and the mode is answered. Nothing downstream in this phase branches on the mode.
- **L4 must not:** pick a mode, name a vendor, or create a board.
- **Blocks:** nothing in this phase.

### DECISION REQUIRED D-L4-P5-05 — how an item is marked spike, incident or debt-remediation for the estimate exemption

- **Fact.** §29.3 line 2667 (D79): *"Normal planned work records an estimate band … spikes, incidents and debt-remediation items are exempt."* The three exempt classes are named in prose. No field on any board item, in any registry schema, or in §97.2 carries them: `grep -n "debt-remediation" MultiProduct_MasterSpec_v4.0.md` returns line 2665 and nothing else.
- **Question.** What field on a board item carries the item class, and what is its closed vocabulary?
- **L4 default that ships:** `metrics/boards/ready-definition.yaml` declares `estimate_exempt_classes: [spike, incident, debt-remediation]` — the three literal §29.3 words — and `tools/records/estimate_capture.py` **requires** the caller to pass `--item-class`. It **never infers the class**, and a call with no `--item-class` exits `3` (`ERROR missing-item-class`), never `0`.
- **L4 must not:** infer the class from a title, a label, a linked incident record, or a column.
- **Blocks:** nothing. The caller is board automation, which is subsystem N's write path and reaches `estimate_capture.py` through the `machine-board` class of `L4-03-write-paths.md` §3.1.

---

## 7. Normative tables — transcribed, not summarised

Every task below writes one of these tables into a file. Where a task's YAML and a table here differ, **the table is authoritative and the difference is a blocker for L0.**

### 7.1 The flow — §29.1, line 2628, exactly seven columns in this order

```
Backlog → Ready → Planned → In Progress → In Review → Verify → Done
```

*"Backlog and Ready are not the same thing. This distinction is load-bearing."* — line 2631.

### 7.2 The two states that are not columns — §29.1, line 2632

| State | Kind | Applies to | Rule |
|---|---|---|---|
| **Blocked** | flag | Planned, In Progress, In Review, Verify — *"any in-flight column"* | Flagged items surface in the by-blocked-state view. **Never a column.** |
| **Deploy** | post-merge pipeline stage | — | *"rendered on the board from deployment records (Section 32) so that an item's position between merge and shipped is visible; nobody moves a card into it by hand."* |

### 7.3 Board topology — §29.1, lines 2633–2635

| Item | Value |
|---|---|
| Product board | One per product. **Execution truth.** |
| Portfolio board | One aggregate view across all products, *"derived from product boards wherever the projects platform supports aggregation"*. **An aggregated planning and capacity view, not execution truth.** *"Nobody maintains duplicate cards by hand."* |
| Portfolio views (line 2634, ten, verbatim) | current work · ready work · future work · by owner · by reviewer · by product · by priority · by blocked state · by lifecycle status · by impact scope |
| Fallback if aggregation is unavailable (line 2635) | *"a single organisation-level project containing all items with a product field, and per-product filtered views — one board, many views, rather than many boards plus a manual roll-up"* |
| Queue of record (line 2639, D70) | The boards of §29.1 only. The background worker harness's internal dispatch queue *"is never a work surface, never rendered or exposed as a board, and never execution truth."* |

### 7.4 The three horizons — §29.2, lines 2645–2649

| Horizon | Contains | Status | Owner |
|---|---|---|---|
| **H1 — Current** | The in-flight flow columns — Planned, In Progress, In Review, Verify — plus the Deploy pipeline stage and any item carrying the Blocked flag | **Committed** | Developers |
| **H2 — Ready Next** | Prepared work that can start immediately when capacity opens | **Prepared**, not committed | Team Lead |
| **H3 — Future** | Major features, technical debt, migrations, architecture evolution, customer requests, security work, integrations, platform upgrades, lifecycle decisions | **Candidate**, intentionally flexible | Team Lead |

Line 2649: *"Work that enters H1 without H2 preparation carries the `unplanned` flag in the attention taxonomy (Section 67)."* Line 2651: *"The Founder does not rearrange individual developer tasks"*; routine Founder priority changes are recorded as a decision record referenced by the affected H2 and H3 items.

### 7.5 The ten Ready criteria — §29.3, line 2655, verbatim and in order

| # | Criterion |
|---|---|
| 1 | a clear requirement |
| 2 | the product identified |
| 3 | a priority |
| 4 | an intended person |
| 5 | a verification path |
| 6 | dependencies understood |
| 7 | required architecture decisions resolved |
| 8 | impact scope proposed |
| 9 | acceptance criteria |
| 10 | enough context to begin GSD discussion immediately |

*"An item is Ready **only when** it has"* all ten. Missing one is not Ready.

The pipeline of line 2658–2659: `Idea → Defined → Verification understood → Architecture resolved → Ready → Assigned → Executed`.

Four further §29.3 rules, all declared in `ready-definition.yaml`:

| Rule | Line |
|---|---|
| Two Ready items per developer is the **normal planning target, not an absolute invariant**; a large architecture item legitimately occupying someone for weeks with nothing queued is correct behaviour, not a planning miss | 2662 |
| The hard requirement is that **Ready-queue misses trend to zero**; do not fragment tasks artificially to satisfy a numeric queue count | 2663 |
| **Ready-draft delegation** — Primary Owners may draft Ready candidates for their own products; the Team Lead's confirmation is the Ready transition. Authorship is delegated; Ready authority is retained | 2664 |
| Item selection among equal-priority Ready items is the developer's own choice | 2666 |

### 7.6 Estimate capture — §29.3 line 2665 (D79, line 10162)

| Element | Value |
|---|---|
| Capture point | **Ready confirmation.** The single capture point feeding the estimates store and the estimation-accuracy KPIs. |
| Applies to | Normal planned work only |
| Exempt | spikes, incidents, debt-remediation items |
| Form | **Banded**, matching the collection philosophy, **never hours-precise** |
| Vocabulary home | *"calibrated configuration declared in `economics.yaml`"* — **L1's file** (`PARTITION.md` line 17). L4 reads it; L4 never writes it. |
| Initial calibration (line 2665) | `XS` half a day · `S` one day · `M` three days · `L` five days · `XL` ten days and a prompt to split the item |
| Recorded on the record | the band **label** *and* the point value **in force when it was written**, *"so a later revision of the vocabulary re-maps the history rather than invalidating it"* |
| Actual effort | **elapsed net of recorded Blocked time** for the §78 Estimation Accuracy KPI; **raw elapsed** for forecast calibration; *"the record carries both figures so the two are never confused"* |

### 7.7 The three collectors of subsystem I — §99.2 line 9196

| Collector | Cadence, with anchor | What it produces |
|---|---|---|
| **DevLake** | Nightly. §94.2 clock: ingestion **04:00**, *"DevLake refresh complete"* **06:00** (lines 8409, 8411) | PR cycle time, cross-review turnaround, lead time merge-to-production (§103.1, §103.2); SIG-04, SIG-07, SIG-08 and — with registries — SIG-40 (§52.2 lines 4533, 4536, 4537, 4569) |
| **Prometheus** | Scrapes the three §41.2 endpoints. **Interval is set in the operations-VM Prometheus configuration (subsystem M, L5 `ops-vm/**`) and is not declared by L4** — §38.4 line 3476 refers to *"a scrape interval"* and names no value | Liveness and dependency health, deployed digest, product metrics including AI token and spend counters |
| **Scorecard** | Nightly. §94.2 clock: *"Scorecard full scan"* **02:00** (line 8406); §84.4 tool cadence table: *"Scorecard \| Nightly \| Risk score per product \| Free"* (line 8561) | Risk score per product (§85.2 line 8395) |

### 7.8 The three required endpoints — §41.2, lines 3723–3725, verbatim

| Endpoint | Provides |
|---|---|
| `GET /health` | Liveness plus dependency health, distinguishing internal from external failure |
| `GET /version` | Deployed artifact digest and build metadata |
| `GET /metrics` | Prometheus format |

Binding conditions, all from §41.2:

| Condition | Line |
|---|---|
| Required of every product whose declared `conformance_profile` exposes the service interface — *"the `service` default, and `white-label` per deployment"*. A product declaring `client-app`, `library`, `batch`, `customer-hosted` or `static-site` *"meets the equivalent evidence of Section 15.7 instead, and is never failed for lacking an endpoint its shape cannot serve"* | 3719 |
| *"The three endpoints are not a public surface."* Each product declares `observability.telemetry_exposure`; **the estate's declared posture is `private-authenticated`** — reachable only over the private path from the operations VM, with a **per-product scrape credential**. `public` is a recorded Founder decision, never a framework default | 3726 |
| *"The private path is a scrape path only — it carries the operations VM no production credential, no deploy key and no environment access"* | 3726 |
| *"`/version` closes the production evidence chain … the digest it reports must equal the approved digest, and any mismatch is a P0 investigation"* | 3728 |
| Every AI-consuming product exports cumulative tokens and estimated spend per provider key through `/metrics`, and Prometheus alerts at `cost.metrics_alert_fraction` — **initial calibrated value 0.8** | 3476 |
| Launch readiness: *"`observability.telemetry_exposure` declared, and `/metrics` verified unreachable from the public internet unless a recorded Founder decision declares it `public`"* | 1892 |

### 7.9 The DevLake field-coverage caveat — §99.3 item 4, line 9243, verbatim

> **DevLake field coverage** — several metrics (routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread measures) require bespoke computation beyond DevLake's models; **confirm coverage before Phase G3**.

Reinforced twice more:

- §30.3 line 2737: *"Other tools carry unverified capability assumptions, each confirmed before the phase depending on it: … **DevLake's connector field coverage and required database engine** …"*
- §98 Phase G3, line 9133: *"Dependencies: G1–G2; **DevLake field coverage confirmed.**"*

**The rule this phase makes mechanical:** a measure declaring `source_kind: collector` and `collector: devlake` may not arm until `metrics/ingest/devlake-coverage.yaml` records a confirmation for the field it needs. Until then it renders `unarmed — not yet instrumented` under D77 (§52.2 line 4524) — **never as a miss, never as zero**.

### 7.10 The three arming strings — frozen vocabulary

Only these three strings may appear in an `arming_state` field anywhere in `metrics/ingest/**`. They are transcribed from §52.2 line 4524 and §51.2 line 4459; no fourth string is invented.

| String | Meaning | Anchor |
|---|---|---|
| `unarmed — not yet instrumented` | The declared source is not live | §52.2, line 4524 |
| `unarmed — insufficient history` | The source is live but does not yet hold the full `lookback_window` | §52.2, line 4524 |
| `armed — source stale` | The source is live and holds the window, but its ingest is past its freshness bound | §51.2, line 4459 |

Line 4459, verbatim, is the only stated freshness SLO for any collector in this phase: *"DevLake ingest freshness \| Ingest completes at least daily \| Age of the newest ingested row \| Amber; the signals sourced from DevLake render as **armed — source stale** (Section 52.2) rather than as within tolerance"*.

---

## 8. Tasks — subsystem N, work tracking conventions

These four are rows 66–69 of `L4-06-tasks.md` §2. Their ids, file paths, sizes, dependencies and acceptance commands are taken from that index unchanged.

**RESOLVED ORDERING — do not re-litigate.** `L4-06-tasks.md` row 68 lists `tools/records/validate-boards.sh` among `L4-P5-03`'s files, while rows 66 and 67 already verify with `validate-boards.sh --columns` and `--horizons`. The dispatcher is therefore **created** in `L4-P5-01` and **extended** by later limbs. Editing a file inside an owned path is permitted (`PARTITION.md` rule 5); creating it twice is not. Every limb is its own file under `tools/records/boards/`, so rule 3 holds.

---

### TASK `L4-P5-01` — Board conventions: seven columns, Blocked as a flag, Deploy rendered

**Mode** LANE · **Size** M · **Depends on** `L4-P3-01` · **Spec** §29.1 lines 2623–2639; D70
**Writes** `metrics/boards/board-conventions.yaml`, `tools/records/validate-boards.sh`, `tools/records/boards/columns.py`, `tools/records/checks/L4-P5-01.sh`

§7.1, §7.2 and §7.3 become one file. Line 2631 is why the check counts columns rather than trusting a set: *"Backlog and Ready are not the same thing. This distinction is load-bearing."* A configuration that collapses them, or that promotes Blocked to a column, is the erosion the check exists to catch.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-board-conventions

mkdir -p metrics/boards tools/records/boards tools/records/checks

cat > metrics/boards/board-conventions.yaml <<'EOF'
# Board conventions - Master Spec section 29.1, lines 2623-2639.
# Transcribed, not summarised. See L4-05-pipeline-and-boards.md sections 7.1-7.3.
schema: metrics/boards/board-conventions.v1
spec_anchor: "MultiProduct_MasterSpec_v4.0.md 29.1 lines 2623-2639"

flow_columns:            # line 2628, in order, exactly seven
  - Backlog
  - Ready
  - Planned
  - In Progress
  - In Review
  - Verify
  - Done

backlog_and_ready_are_distinct: true          # line 2631, load-bearing

in_flight_columns:       # line 2632, "any in-flight column"
  - Planned
  - In Progress
  - In Review
  - Verify

non_column_states:       # line 2632
  Blocked:
    kind: flag
    is_column: false
    applies_to: [Planned, In Progress, In Review, Verify]
    surfaced_in_view: by blocked state
  Deploy:
    kind: post-merge-pipeline-stage
    is_column: false
    rendered_from: records/deployments/
    rendered_from_spec_section: "32"
    hand_moved: false

board_topology:          # line 2633
  product_board:
    cardinality: one-per-product
    role: execution-truth
  portfolio_board:
    cardinality: one
    role: aggregated-planning-and-capacity-view
    derived_from: product_boards
    hand_maintained_duplicate_cards: false
    views:               # line 2634, ten, verbatim and in order
      - current work
      - ready work
      - future work
      - by owner
      - by reviewer
      - by product
      - by priority
      - by blocked state
      - by lifecycle status
      - by impact scope

aggregation_modes:       # line 2635
  aggregated:
    description: "portfolio board derived from product boards by platform aggregation"
    requires: "aggregation and filtering capability confirmed at the plan tier in use"
  single_project_fallback:
    description: "a single organisation-level project containing all items with a product field, and per-product filtered views"
    shape: "one board, many views, rather than many boards plus a manual roll-up"
    requires: "none"
selected_mode: single_project_fallback        # L4-05 section 6, D-L4-P5-04 — decided
aggregation_confirmed: false
confirmation_deadline: "before Phase 1 of implementation (line 2635)"

queue_of_record:         # line 2639, D70
  is: "the boards of section 29.1"
  excluded:
    - id: background-worker-harness-internal-dispatch-queue
      spec_section: "37"
      never_a_work_surface: true
      never_rendered_as_a_board: true
      never_execution_truth: true
EOF

cat > tools/records/boards/columns.py <<'PYEOF'
#!/usr/bin/env python3
"""BOARDS --columns limb. Master Spec 29.1 lines 2623-2639."""
import sys, yaml

FLOW = ["Backlog", "Ready", "Planned", "In Progress", "In Review", "Verify", "Done"]
INFLIGHT = ["Planned", "In Progress", "In Review", "Verify"]
VIEWS = ["current work", "ready work", "future work", "by owner", "by reviewer",
         "by product", "by priority", "by blocked state", "by lifecycle status",
         "by impact scope"]


def fail(msg):
    print("BOARDS FAIL columns %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/board-conventions.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR board-conventions-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("flow_columns") != FLOW:
        fail("flow-columns-not-the-seven-of-line-2628")
    if d.get("backlog_and_ready_are_distinct") is not True:
        fail("backlog-ready-collapsed")
    if d.get("in_flight_columns") != INFLIGHT:
        fail("in-flight-set-wrong")
    ns = d.get("non_column_states") or {}
    if set(ns) != {"Blocked", "Deploy"}:
        fail("non-column-states-not-exactly-Blocked-and-Deploy")
    b = ns["Blocked"]
    if b.get("kind") != "flag" or b.get("is_column") is not False:
        fail("Blocked-is-not-a-flag")
    if b.get("applies_to") != INFLIGHT:
        fail("Blocked-applies-to-wrong-columns")
    if b.get("surfaced_in_view") != "by blocked state":
        fail("Blocked-view-missing")
    dep = ns["Deploy"]
    if dep.get("is_column") is not False or dep.get("hand_moved") is not False:
        fail("Deploy-hand-moved-or-column")
    if dep.get("rendered_from") != "records/deployments/":
        fail("Deploy-not-rendered-from-deployment-records")
    for c in FLOW:
        if c in ns:
            fail("column-also-declared-a-non-column-state")
    t = d.get("board_topology") or {}
    pb, pf = t.get("product_board") or {}, t.get("portfolio_board") or {}
    if pb.get("cardinality") != "one-per-product" or pb.get("role") != "execution-truth":
        fail("product-board-not-execution-truth")
    if pf.get("role") != "aggregated-planning-and-capacity-view":
        fail("portfolio-board-claims-execution-truth")
    if pf.get("hand_maintained_duplicate_cards") is not False:
        fail("duplicate-cards-permitted")
    if pf.get("views") != VIEWS:
        fail("portfolio-views-not-the-ten-of-line-2634")
    if sorted(d.get("aggregation_modes") or {}) != ["aggregated", "single_project_fallback"]:
        fail("both-aggregation-modes-not-declared")
    if not d.get("selected_mode") or d.get("selected_mode").startswith("PENDING"):
        fail("selected-mode-not-answered")
    if d.get("aggregation_confirmed") is not False:
        fail("aggregation-claimed-confirmed-without-evidence")
    ex = (d.get("queue_of_record") or {}).get("excluded") or []
    if not any(e.get("id") == "background-worker-harness-internal-dispatch-queue"
               and e.get("never_execution_truth") is True for e in ex):
        fail("D70-carve-out-missing")
    print("BOARDS OK columns=7 inflight=4 nonstate=2 views=10 modes=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

cat > tools/records/validate-boards.sh <<'SHEOF'
#!/usr/bin/env bash
# BOARDS dispatcher. Lane 4, Phase 5. Output contract: L4-06-tasks.md section 0.5.
set -eu
cd "$(dirname "$0")/../.."
PY="${L4_PY:-python}"
case "${1:-}" in
  --columns)  exec "$PY" tools/records/boards/columns.py ;;
  --horizons) exec "$PY" tools/records/boards/horizons.py ;;
  --ready)    exec "$PY" tools/records/boards/ready.py ;;
  --estimate-capture) exec "$PY" tools/records/estimate_capture.py --selftest ;;
  "")
    for f in tools/records/boards/columns.py tools/records/boards/horizons.py tools/records/boards/ready.py; do
      [ -f "$f" ] || { echo "BOARDS ERROR missing-limb"; exit 3; }
      "$PY" "$f" >/dev/null || { echo "BOARDS FAIL limb"; exit 1; }
    done
    if [ -f tools/records/estimate_capture.py ]; then
      "$PY" tools/records/estimate_capture.py --selftest >/dev/null || { echo "BOARDS FAIL limb"; exit 1; }
    fi
    echo "BOARDS OK"
    ;;
  *) echo "BOARDS ERROR unknown-limb"; exit 3 ;;
esac
SHEOF
chmod +x tools/records/validate-boards.sh

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-boards.sh --columns | grep -qx "BOARDS OK columns=7 inflight=4 nonstate=2 views=10 modes=2"' \
  > tools/records/checks/L4-P5-01.sh

bash tools/records/validate-boards.sh --columns
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-boards.sh --columns` | `BOARDS OK columns=7 inflight=4 nonstate=2 views=10 modes=2` |
| 2 | Exactly seven flow columns, in §29.1 order | `"$L4_PY" -c "import yaml;print('/'.join(yaml.safe_load(open('metrics/boards/board-conventions.yaml'))['flow_columns']))"` | `Backlog/Ready/Planned/In Progress/In Review/Verify/Done` |
| 3 | Blocked is a flag, not a column | `"$L4_PY" -c "import yaml;b=yaml.safe_load(open('metrics/boards/board-conventions.yaml'))['non_column_states']['Blocked'];print(b['kind'],b['is_column'])"` | `flag False` |
| 4 | Deploy is rendered, never hand-moved | `"$L4_PY" -c "import yaml;x=yaml.safe_load(open('metrics/boards/board-conventions.yaml'))['non_column_states']['Deploy'];print(x['rendered_from'],x['hand_moved'])"` | `records/deployments/ False` |
| 5 | Ten portfolio views | `"$L4_PY" -c "import yaml;print(len(yaml.safe_load(open('metrics/boards/board-conventions.yaml'))['board_topology']['portfolio_board']['views']))"` | `10` |
| 6 | Both modes declared; mode selected | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/boards/board-conventions.yaml'));print(len(d['aggregation_modes']),d['selected_mode'])"` | `2 single_project_fallback` |
| 7 | The check **can fail** (§0.8 rule 9) | `cp metrics/boards/board-conventions.yaml /tmp/bc.bak && "$L4_PY" -c "import yaml;p='metrics/boards/board-conventions.yaml';d=yaml.safe_load(open(p));d['flow_columns'].remove('Ready');yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-boards.sh --columns; echo "exit=$?"; cp /tmp/bc.bak metrics/boards/board-conventions.yaml` | `BOARDS FAIL columns flow-columns-not-the-seven-of-line-2628` then `exit=1` |
| 8 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-01; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-01 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-02` if:

- Criterion 7 does not print `BOARDS FAIL` — a check that cannot fail is not a check (`L4-06-tasks.md` §0.8 rule 9). Blocker.
- `lane-selfcheck.sh --paths` reports anything but `PATHS OK`. Blocker.
- `metrics/boards/board-conventions.yaml` already exists on `integration` → a prior partial run. Do **not** overwrite it and do **not** delete it. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/boards/board-conventions.yaml tools/records/validate-boards.sh tools/records/boards/columns.py tools/records/checks/L4-P5-01.sh
git commit -m "L4-P5-01: Board conventions - seven columns, Blocked as a flag, Deploy rendered"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-board-conventions
gh pr create --base integration --title "L4-P5-01: Board conventions" \
  --body "Lane 4, Phase 5. Task L4-P5-01. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-02` — Horizon semantics H1/H2/H3 and the `unplanned` rule

**Mode** LANE · **Size** S · **Depends on** `L4-P5-01` · **Spec** §29.2 lines 2641–2651; §67.2 line 5592
**Writes** `metrics/boards/horizons.yaml`, `tools/records/boards/horizons.py`, `tools/records/checks/L4-P5-02.sh`

§7.4 becomes one file. The H1 membership rule is the load-bearing part: H1 is *"the in-flight flow columns … **plus the Deploy pipeline stage and any item carrying the Blocked flag**"* (line 2645). A Blocked item is still committed; dropping it out of H1 is how committed work becomes invisible.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-horizons

cat > metrics/boards/horizons.yaml <<'EOF'
# Three planning horizons - Master Spec section 29.2, lines 2641-2651.
schema: metrics/boards/horizons.v1
spec_anchor: "MultiProduct_MasterSpec_v4.0.md 29.2 lines 2641-2651"

horizons:
  H1:
    name: Current
    status: Committed
    owner: Developers
    contains_columns: [Planned, In Progress, In Review, Verify]
    contains_pipeline_stage: Deploy
    contains_blocked_flagged_items: true       # line 2645, load-bearing
  H2:
    name: Ready Next
    status: Prepared
    committed: false                            # line 2646, "Prepared, not committed"
    owner: Team Lead
    contains: "Prepared work that can start immediately when capacity opens"
  H3:
    name: Future
    status: Candidate
    owner: Team Lead
    intentionally_flexible: true
    is_a_commitment: false                      # line 2649, "H3 is not a commitment"
    contains:                                   # line 2647, verbatim, nine
      - major features
      - technical debt
      - migrations
      - architecture evolution
      - customer requests
      - security work
      - integrations
      - platform upgrades
      - lifecycle decisions

unplanned_rule:                                 # line 2649
  condition: "an item enters H1 without H2 preparation"
  effect: "the item carries the `unplanned` flag in the attention taxonomy"
  taxonomy_section: "67"
  is_a_flag: true                               # 67.2 line 5592 - a flag, never a category
  is_a_category: false

founder_rule:                                   # line 2651
  operates_at: [H3, portfolio]
  rearranges_individual_developer_tasks: false
  exceptional_override_permitted: true
  priority_change_recording: "a decision record referenced by the affected H2 and H3 items"
  translation_of_override_into_sequencing: Team Lead
EOF

cat > tools/records/boards/horizons.py <<'PYEOF'
#!/usr/bin/env python3
"""BOARDS --horizons limb. Master Spec 29.2 lines 2641-2651."""
import sys, yaml

H1COLS = ["Planned", "In Progress", "In Review", "Verify"]
H3 = ["major features", "technical debt", "migrations", "architecture evolution",
      "customer requests", "security work", "integrations", "platform upgrades",
      "lifecycle decisions"]


def fail(msg):
    print("BOARDS FAIL horizons %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/horizons.yaml", encoding="utf-8"))
        b = yaml.safe_load(open("metrics/boards/board-conventions.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR horizons-input-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    h = d.get("horizons") or {}
    if sorted(h) != ["H1", "H2", "H3"]:
        fail("not-exactly-three-horizons")
    if h["H1"].get("status") != "Committed" or h["H1"].get("owner") != "Developers":
        fail("H1-not-committed-to-developers")
    if h["H1"].get("contains_columns") != H1COLS:
        fail("H1-columns-not-the-in-flight-four")
    if h["H1"].get("contains_columns") != b.get("in_flight_columns"):
        fail("H1-columns-disagree-with-board-conventions")
    if h["H1"].get("contains_pipeline_stage") != "Deploy":
        fail("H1-omits-Deploy")
    if h["H1"].get("contains_blocked_flagged_items") is not True:
        fail("H1-omits-blocked-items")
    if h["H2"].get("status") != "Prepared" or h["H2"].get("committed") is not False:
        fail("H2-not-prepared-uncommitted")
    if h["H2"].get("owner") != "Team Lead" or h["H3"].get("owner") != "Team Lead":
        fail("H2-or-H3-not-owned-by-Team-Lead")
    if h["H3"].get("status") != "Candidate" or h["H3"].get("is_a_commitment") is not False:
        fail("H3-treated-as-a-commitment")
    if h["H3"].get("contains") != H3:
        fail("H3-content-list-not-the-nine-of-line-2647")
    u = d.get("unplanned_rule") or {}
    if u.get("is_a_flag") is not True or u.get("is_a_category") is not False:
        fail("unplanned-declared-as-a-category")
    if "without H2 preparation" not in (u.get("condition") or ""):
        fail("unplanned-condition-not-H2-preparation")
    f = d.get("founder_rule") or {}
    if f.get("rearranges_individual_developer_tasks") is not False:
        fail("founder-rearranges-developer-tasks")
    if "decision record" not in (f.get("priority_change_recording") or ""):
        fail("founder-priority-change-not-recorded-as-a-decision-record")
    print("BOARDS OK horizons=3 h1cols=4 h3items=9")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-boards.sh --horizons | grep -qx "BOARDS OK horizons=3 h1cols=4 h3items=9"' \
  > tools/records/checks/L4-P5-02.sh

bash tools/records/validate-boards.sh --horizons
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-boards.sh --horizons` | `BOARDS OK horizons=3 h1cols=4 h3items=9` |
| 2 | H1 is Committed, owned by Developers | `"$L4_PY" -c "import yaml;h=yaml.safe_load(open('metrics/boards/horizons.yaml'))['horizons']['H1'];print(h['status'],h['owner'])"` | `Committed Developers` |
| 3 | H1 carries Deploy **and** Blocked-flagged items | `"$L4_PY" -c "import yaml;h=yaml.safe_load(open('metrics/boards/horizons.yaml'))['horizons']['H1'];print(h['contains_pipeline_stage'],h['contains_blocked_flagged_items'])"` | `Deploy True` |
| 4 | H2 is Prepared and **not** committed | `"$L4_PY" -c "import yaml;h=yaml.safe_load(open('metrics/boards/horizons.yaml'))['horizons']['H2'];print(h['status'],h['committed'])"` | `Prepared False` |
| 5 | H3 is Candidate and not a commitment | `"$L4_PY" -c "import yaml;h=yaml.safe_load(open('metrics/boards/horizons.yaml'))['horizons']['H3'];print(h['status'],h['is_a_commitment'])"` | `Candidate False` |
| 6 | `unplanned` is a flag, never a category | `"$L4_PY" -c "import yaml;u=yaml.safe_load(open('metrics/boards/horizons.yaml'))['unplanned_rule'];print(u['is_a_flag'],u['is_a_category'])"` | `True False` |
| 7 | The check **can fail** | `cp metrics/boards/horizons.yaml /tmp/hz.bak && "$L4_PY" -c "import yaml;p='metrics/boards/horizons.yaml';d=yaml.safe_load(open(p));d['horizons']['H1']['contains_blocked_flagged_items']=False;yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-boards.sh --horizons; echo "exit=$?"; cp /tmp/hz.bak metrics/boards/horizons.yaml` | `BOARDS FAIL horizons H1-omits-blocked-items` then `exit=1` |
| 8 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-02; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-02 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-03` if:

- The limb prints `BOARDS ERROR horizons-input-unreadable:*` → `L4-P5-01` has not merged and its file is absent. Do **not** recreate it. Blocker.
- The limb prints `BOARDS FAIL horizons H1-columns-disagree-with-board-conventions` → the two files disagree. Do **not** edit either to force agreement; one of them contradicts §7.2/§7.4. Blocker.
- Criterion 7 does not print `BOARDS FAIL`. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/boards/horizons.yaml tools/records/boards/horizons.py tools/records/checks/L4-P5-02.sh
git commit -m "L4-P5-02: Horizon semantics H1/H2/H3 and the unplanned rule"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-horizons
gh pr create --base integration --title "L4-P5-02: Horizon semantics" \
  --body "Lane 4, Phase 5. Task L4-P5-02. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-03` — Ready-to-Execute definition as machine-checkable configuration

**Mode** LANE · **Size** M · **Depends on** `L4-P5-01` · **Spec** §29.3 lines 2653–2666
**Writes** `metrics/boards/ready-definition.yaml`, `tools/records/boards/ready.py`, `tools/records/checks/L4-P5-03.sh`

§7.5 becomes one file. Line 2655 says an item is Ready *"only when it has"* the ten. The check asserts the conjunction is `all`, because "nine of ten and it is nearly Ready" is exactly the erosion that would make the Ready-queue-miss detector of `L4-P5-05`…`L4-P5-13` meaningless.

Two rules must **not** become numeric gates: the two-items-per-developer target (line 2662) is declared `is_absolute_invariant: false`, and line 2663 forbids artificial fragmentation to satisfy a queue count.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-ready-definition

cat > metrics/boards/ready-definition.yaml <<'EOF'
# Ready-to-Execute - Master Spec section 29.3, lines 2653-2666.
schema: metrics/boards/ready-definition.v1
spec_anchor: "MultiProduct_MasterSpec_v4.0.md 29.3 lines 2653-2666"

conjunction: all          # line 2655, "only when it has" - all ten, never a majority

criteria:                 # line 2655, verbatim and in order
  - id: clear_requirement
    text: "a clear requirement"
  - id: product_identified
    text: "the product identified"
  - id: priority
    text: "a priority"
  - id: intended_person
    text: "an intended person"
  - id: verification_path
    text: "a verification path"
  - id: dependencies_understood
    text: "dependencies understood"
  - id: architecture_decisions_resolved
    text: "required architecture decisions resolved"
  - id: impact_scope_proposed
    text: "impact scope proposed"
  - id: acceptance_criteria
    text: "acceptance criteria"
  - id: enough_context_to_begin
    text: "enough context to begin GSD discussion immediately"

pipeline:                 # lines 2658-2659
  - Idea
  - Defined
  - Verification understood
  - Architecture resolved
  - Ready
  - Assigned
  - Executed

planning_target:          # line 2662
  ready_items_per_developer: 2
  is_absolute_invariant: false
  note: "a large architecture item legitimately occupying someone for weeks with nothing queued behind it is correct behaviour, not a planning miss"

hard_requirement:         # line 2663
  statement: "Ready-queue misses trend to zero"
  artificial_fragmentation_permitted: false

ready_draft_delegation:   # line 2664
  drafting_permitted_by: Primary Owner
  drafting_scope: "their own products"
  ready_transition_authority: Team Lead
  authority_delegated: false

item_selection:           # line 2666
  among_equal_priority_ready_items: "the developer's own choice"

estimate_capture:         # line 2665 (D79) - the capture point, consumed by L4-P5-04
  capture_point: ready_confirmation
  applies_to: normal_planned_work
  estimate_exempt_classes:            # D-L4-P5-05 - the three literal words of line 2665
    - spike
    - incident
    - debt-remediation
  item_class_inferred: false          # never inferred from title, label or column
  band_vocabulary_home: registries/economics.yaml
  band_vocabulary_owner_lane: L1
  hours_precise: false
EOF

cat > tools/records/boards/ready.py <<'PYEOF'
#!/usr/bin/env python3
"""BOARDS --ready limb. Master Spec 29.3 lines 2653-2666."""
import sys, yaml

IDS = ["clear_requirement", "product_identified", "priority", "intended_person",
       "verification_path", "dependencies_understood",
       "architecture_decisions_resolved", "impact_scope_proposed",
       "acceptance_criteria", "enough_context_to_begin"]
PIPE = ["Idea", "Defined", "Verification understood", "Architecture resolved",
        "Ready", "Assigned", "Executed"]
EXEMPT = ["spike", "incident", "debt-remediation"]


def fail(msg):
    print("BOARDS FAIL ready %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/ready-definition.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR ready-definition-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("conjunction") != "all":
        fail("conjunction-not-all")
    c = d.get("criteria") or []
    if [x.get("id") for x in c] != IDS:
        fail("criteria-not-the-ten-of-line-2655")
    for x in c:
        if not (x.get("text") or "").strip():
            fail("criterion-has-no-text")
    if d.get("pipeline") != PIPE:
        fail("pipeline-not-the-seven-of-lines-2658-2659")
    pt = d.get("planning_target") or {}
    if pt.get("ready_items_per_developer") != 2:
        fail("planning-target-not-two")
    if pt.get("is_absolute_invariant") is not False:
        fail("planning-target-declared-an-invariant")
    hr = d.get("hard_requirement") or {}
    if "trend to zero" not in (hr.get("statement") or ""):
        fail("hard-requirement-not-trend-to-zero")
    if hr.get("artificial_fragmentation_permitted") is not False:
        fail("artificial-fragmentation-permitted")
    rd = d.get("ready_draft_delegation") or {}
    if rd.get("drafting_permitted_by") != "Primary Owner":
        fail("ready-draft-delegation-wrong-drafter")
    if rd.get("ready_transition_authority") != "Team Lead":
        fail("ready-authority-not-retained-by-Team-Lead")
    if rd.get("authority_delegated") is not False:
        fail("ready-authority-delegated")
    ec = d.get("estimate_capture") or {}
    if ec.get("capture_point") != "ready_confirmation":
        fail("estimate-capture-point-not-ready-confirmation")
    if ec.get("applies_to") != "normal_planned_work":
        fail("estimate-capture-not-limited-to-normal-planned-work")
    if ec.get("estimate_exempt_classes") != EXEMPT:
        fail("exempt-classes-not-the-three-of-line-2665")
    if ec.get("item_class_inferred") is not False:
        fail("item-class-inference-permitted")
    if ec.get("band_vocabulary_home") != "registries/economics.yaml":
        fail("band-vocabulary-not-in-economics-yaml")
    if ec.get("hours_precise") is not False:
        fail("hours-precise-estimates-permitted")
    print("BOARDS OK ready=10 pipeline=7 exempt=3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-boards.sh --ready | grep -qx "BOARDS OK ready=10 pipeline=7 exempt=3"' \
  > tools/records/checks/L4-P5-03.sh

bash tools/records/validate-boards.sh --ready
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-boards.sh --ready` | `BOARDS OK ready=10 pipeline=7 exempt=3` |
| 2 | Exactly ten criteria | `"$L4_PY" -c "import yaml;print(len(yaml.safe_load(open('metrics/boards/ready-definition.yaml'))['criteria']))"` | `10` |
| 3 | The conjunction is `all`, not a threshold | `"$L4_PY" -c "import yaml;print(yaml.safe_load(open('metrics/boards/ready-definition.yaml'))['conjunction'])"` | `all` |
| 4 | The two-item target is not an invariant | `"$L4_PY" -c "import yaml;p=yaml.safe_load(open('metrics/boards/ready-definition.yaml'))['planning_target'];print(p['ready_items_per_developer'],p['is_absolute_invariant'])"` | `2 False` |
| 5 | Ready authority is retained by the Team Lead | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open('metrics/boards/ready-definition.yaml'))['ready_draft_delegation'];print(r['ready_transition_authority'],r['authority_delegated'])"` | `Team Lead False` |
| 6 | The three exempt classes are the literal §29.3 words | `"$L4_PY" -c "import yaml;print(','.join(yaml.safe_load(open('metrics/boards/ready-definition.yaml'))['estimate_capture']['estimate_exempt_classes']))"` | `spike,incident,debt-remediation` |
| 7 | The check **can fail** | `cp metrics/boards/ready-definition.yaml /tmp/rd.bak && "$L4_PY" -c "import yaml;p='metrics/boards/ready-definition.yaml';d=yaml.safe_load(open(p));d['criteria'].pop();yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-boards.sh --ready; echo "exit=$?"; cp /tmp/rd.bak metrics/boards/ready-definition.yaml` | `BOARDS FAIL ready criteria-not-the-ten-of-line-2655` then `exit=1` |
| 8 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-03; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-03 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-04` if:

- `tools/records/validate-boards.sh` is absent → `L4-P5-01` has not merged. Do **not** create a second dispatcher. Blocker.
- Any step asks you to add, merge, split or reword a Ready criterion → the ten are transcribed from line 2655 and are not yours to edit. Blocker.
- Criterion 7 does not print `BOARDS FAIL`. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/boards/ready-definition.yaml tools/records/boards/ready.py tools/records/checks/L4-P5-03.sh
git commit -m "L4-P5-03: Ready-to-Execute definition as machine-checkable configuration"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-ready-definition
gh pr create --base integration --title "L4-P5-03: Ready-to-Execute definition" \
  --body "Lane 4, Phase 5. Task L4-P5-03. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-04` — Estimate capture at Ready confirmation (D79)

**Mode** LANE · **Size** M · **Depends on** `L4-P5-03`, `L4-P2-10` · **Spec** §29.3 line 2665; D79 line 10162; §97.2 line 8850
**Writes** `tools/records/estimate_capture.py`, `tools/records/fixtures/estimate-capture/*.json`, `tools/records/checks/L4-P5-04.sh`

§7.6 becomes one callable. Four rules make this task non-negotiable:

1. **One capture point.** Line 2665: *"This is the single capture point feeding the estimates store and the estimation-accuracy KPIs (D79)."* Firing anywhere but the Ready-confirmation transition is a defect, not a convenience.
2. **The vocabulary is L1's.** *"The band vocabulary is calibrated configuration declared in `economics.yaml`"* — `PARTITION.md` line 17 gives `registries/**` to L1. This module **reads** that file and **fails closed** if it cannot (§40.1 line 3671). It never writes it and never embeds a fallback vocabulary.
3. **Label and point value together.** The record carries *"the band label and the point value in force when it was written, so a later revision of the vocabulary re-maps the history rather than invalidating it."*
4. **Two elapsed figures, never one.** *"The quantity the Estimation Accuracy KPI (Section 78) calls actual effort is elapsed net of recorded Blocked time; raw elapsed is what forecast calibration uses, and the record carries both figures so the two are never confused."* `L4-P2-10` already made `elapsed` and `elapsed_net_blocked` two required, distinct fields on `estimate.schema.json`; this module never emits one without the other's key present.

The exemption is `D-L4-P5-05`: `--item-class` is **required** and never inferred.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-estimate-capture

mkdir -p tools/records/fixtures/estimate-capture

cat > tools/records/estimate_capture.py <<'PYEOF'
#!/usr/bin/env python3
"""Estimate capture at Ready confirmation. Master Spec 29.3 line 2665; D79 line 10162.

Single capture point. Reads the band vocabulary from registries/economics.yaml
(L1-owned, read-only here). Fails closed when it cannot be read.
Never infers the item class; --item-class is required.
"""
import argparse, json, sys, yaml

READY_DEF = "metrics/boards/ready-definition.yaml"
ECONOMICS = "registries/economics.yaml"
CAPTURE_TRANSITION = "ready_confirmation"


def err(reason):
    print("ESTIMATE ERROR %s" % reason)
    sys.exit(3)


def fail(reason):
    print("ESTIMATE FAIL %s" % reason)
    sys.exit(1)


def load_ready():
    try:
        return yaml.safe_load(open(READY_DEF, encoding="utf-8"))["estimate_capture"]
    except Exception:
        err("ready-definition-unreadable")


def load_bands():
    """Band vocabulary lives in registries/economics.yaml - L1's file. Fail closed."""
    try:
        e = yaml.safe_load(open(ECONOMICS, encoding="utf-8"))
    except Exception:
        err("economics-unreachable")
    bands = (e or {}).get("estimate_bands")
    if not bands:
        err("economics-declares-no-estimate-bands")
    out = {}
    for b in bands:
        label, pv = b.get("label"), b.get("point_value_days")
        if not label or pv is None:
            err("band-without-label-or-point-value")
        out[label] = pv
    return out, (e or {}).get("estimate_bands_version")


def capture(args):
    cfg = load_ready()
    if args.transition != CAPTURE_TRANSITION:
        fail("not-the-capture-point:%s" % args.transition)
    if args.item_class is None:
        err("missing-item-class")
    exempt = cfg["estimate_exempt_classes"]
    if args.item_class in exempt:
        print(json.dumps({"captured": False, "reason": "exempt", "item_class": args.item_class}))
        print("ESTIMATE OK exempt=%s" % args.item_class)
        return 0
    if args.item_class != "normal_planned_work":
        err("unknown-item-class:%s" % args.item_class)
    if args.band is None:
        err("missing-band")
    bands, version = load_bands()
    if args.band not in bands:
        fail("band-not-in-economics-vocabulary:%s" % args.band)
    rec = {
        "band": args.band,
        "point_value_days": bands[args.band],
        "band_vocabulary_version": version,
        "captured_at_transition": CAPTURE_TRANSITION,
        "item": args.item,
        "product": args.product,
        "elapsed": None,
        "elapsed_net_blocked": None,
    }
    print(json.dumps(rec, sort_keys=True))
    print("ESTIMATE OK band=%s point=%s" % (args.band, bands[args.band]))
    return 0


def selftest():
    cfg = load_ready()
    if cfg.get("capture_point") != CAPTURE_TRANSITION:
        fail("capture-point-drifted")
    if cfg.get("item_class_inferred") is not False:
        fail("class-inference-permitted")
    if cfg.get("band_vocabulary_home") != ECONOMICS:
        fail("vocabulary-home-drifted")
    if cfg.get("hours_precise") is not False:
        fail("hours-precise-permitted")
    if len(cfg.get("estimate_exempt_classes") or []) != 3:
        fail("exempt-classes-not-three")
    print("BOARDS OK estimate-capture=1 exempt=3")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--transition")
    p.add_argument("--item-class", dest="item_class")
    p.add_argument("--band")
    p.add_argument("--item")
    p.add_argument("--product")
    a = p.parse_args()
    return selftest() if a.selftest else capture(a)


if __name__ == "__main__":
    sys.exit(main())
PYEOF

cat > tools/records/fixtures/estimate-capture/README.md <<'EOF'
Negative cases proved by tools/records/checks/L4-P5-04.sh, all executed, never mocked:
1. wrong transition            -> ESTIMATE FAIL not-the-capture-point:in_progress   exit 1
2. no --item-class             -> ESTIMATE ERROR missing-item-class                 exit 3
3. exempt class                -> ESTIMATE OK exempt=incident, captured False       exit 0
4. economics.yaml unreachable  -> ESTIMATE ERROR economics-unreachable              exit 3
EOF

cat > tools/records/checks/L4-P5-04.sh <<'SHEOF'
#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
PY="${L4_PY:-python}"
bash tools/records/validate-boards.sh --estimate-capture | grep -qx "BOARDS OK estimate-capture=1 exempt=3"
"$PY" tools/records/estimate_capture.py --transition in_progress --item-class normal_planned_work --band M 2>&1 \
  | grep -q "ESTIMATE FAIL not-the-capture-point:in_progress"
"$PY" tools/records/estimate_capture.py --transition ready_confirmation --band M 2>&1 \
  | grep -q "ESTIMATE ERROR missing-item-class"
"$PY" tools/records/estimate_capture.py --transition ready_confirmation --item-class incident 2>&1 \
  | grep -q "ESTIMATE OK exempt=incident"
SHEOF

bash tools/records/validate-boards.sh --estimate-capture
bash tools/records/checks/L4-P5-04.sh && echo "NEGATIVES OK 3/3"
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The self-test passes with the frozen counters | `bash tools/records/validate-boards.sh --estimate-capture` | `BOARDS OK estimate-capture=1 exempt=3` |
| 2 | Capture fires at Ready confirmation and nowhere else | `"$L4_PY" tools/records/estimate_capture.py --transition in_progress --item-class normal_planned_work --band M; echo "exit=$?"` | `ESTIMATE FAIL not-the-capture-point:in_progress` then `exit=1` |
| 3 | The item class is required, never inferred (`D-L4-P5-05`) | `"$L4_PY" tools/records/estimate_capture.py --transition ready_confirmation --band M; echo "exit=$?"` | `ESTIMATE ERROR missing-item-class` then `exit=3` |
| 4 | An exempt class captures nothing | `"$L4_PY" tools/records/estimate_capture.py --transition ready_confirmation --item-class incident \| tail -1` | `ESTIMATE OK exempt=incident` |
| 5 | The vocabulary is read from L1's file and fails closed | `"$L4_PY" -c "import re,io;s=open('tools/records/estimate_capture.py').read();print('registries/economics.yaml' in s, 'economics-unreachable' in s)"` | `True True` |
| 6 | No fallback vocabulary is embedded | `grep -c "XS\|XL" tools/records/estimate_capture.py` | `0` |
| 7 | The emitted record carries band label **and** point value **and** both elapsed keys | `"$L4_PY" -c "import ast,sys;s=open('tools/records/estimate_capture.py').read();print(all(k in s for k in ['\"band\"','point_value_days','\"elapsed\"','elapsed_net_blocked','band_vocabulary_version']))"` | `True` |
| 8 | All three negatives execute | `bash tools/records/checks/L4-P5-04.sh && echo "NEGATIVES OK 3/3"` | `NEGATIVES OK 3/3` |
| 9 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-04; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-04 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-14` if:

- `registries/economics.yaml` is absent or declares no `estimate_bands` → L1 has not published the vocabulary. The module printing `ESTIMATE ERROR economics-unreachable` is **correct behaviour**; criterion 1 still passes because the self-test does not read it. **Do not create `registries/economics.yaml`** — it is L1's path (`PARTITION.md` line 17) and writing it fails the lane guard. File the blocker naming `registries/economics.yaml`, and record in it the §29.3 initial calibration L1 must carry: `XS` half a day, `S` one day, `M` three days, `L` five days, `XL` ten days and a prompt to split the item.
- Criterion 6 returns anything but `0` → a band vocabulary has been embedded here. That is a second source of truth for calibrated configuration. Blocker.
- Criterion 3 exits `0` instead of `3` → class inference has crept in. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add tools/records/estimate_capture.py tools/records/fixtures/estimate-capture/README.md tools/records/checks/L4-P5-04.sh
git commit -m "L4-P5-04: Estimate capture at Ready confirmation (D79)"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-estimate-capture
gh pr create --base integration --title "L4-P5-04: Estimate capture at Ready confirmation" \
  --body "Lane 4, Phase 5. Task L4-P5-04. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

## 9. Tasks — subsystem I, ingest

Ids resume at `L4-P5-14`. `L4-P5-05`…`L4-P5-13` are the Ready-queue-miss detector, indexed as rows 70–78 of `L4-06-tasks.md` §2, and are not in this file.

**The standing rule for this half.** Every task writes a **declaration** plus a validator. None of them connects to a running system. Where evidence from a running system is needed, an **ASSISTED** task produces the request document and the evidence template, and the human lead returns the evidence file.

---

### TASK `L4-P5-14` — Ingest entry gate, `metrics/ingest/` skeleton and the `INGEST` dispatcher

**Mode** LANE · **Size** S · **Depends on** `L4-P5-03`, `L4-P3-06` · **Spec** §99.2 line 9196; §99.6 risk 2 line 9281
**Writes** `metrics/ingest/README.md`, `tools/records/validate-ingest.sh`, `tools/records/ingest/.gitkeep`, `tools/records/checks/L4-P5-14.sh`

This task proves entry conditions E1–E8 of §5 and stands up the dispatcher every later ingest task extends. It writes no collector declaration.

`metrics/ingest/README.md` names the downstream consumers so that no later reader assumes L4 renders anything. Subsystem H is unassigned (`D-L4-P5-03`); saying so in the file is the honest state, not a placeholder.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-ingest-gate

echo "--- entry conditions, all eight ---"
git -C "$CP_DIR" rev-parse --verify origin/integration >/dev/null && echo "E1 ok"
bash tools/records/check.sh ZZZ; echo "E2 exit=$?"
test -x tools/records/lane-selfcheck.sh && echo "E3 ok"
"$L4_PY" -c "import yaml,sys;print('E4 ok', sys.version.split()[0])"
test -f metrics/taxonomy/event-types.yaml && echo "E5 ok"
test -f metrics/signals/sig-source-map.yaml && echo "E6 ok"
"$L4_PY" -c "import json;r=set(json.load(open('schemas/records/estimate.schema.json'))['required']);print('E7 ok' if {'elapsed','elapsed_net_blocked'}<=r else 'E7 MISSING')"
test -f metrics/retention/retention-classes.yaml && echo "E8 ok"

mkdir -p metrics/ingest tools/records/ingest
: > tools/records/ingest/.gitkeep

cat > metrics/ingest/README.md <<'EOF'
# metrics/ingest - collector declarations (Lane 4, subsystem I)

Master Spec section 99.2 line 9196 assigns to subsystem I:
"DevLake nightly ingest; Prometheus scraping /health, /version, /metrics;
Scorecard scheduled scan with drop detection; the event-log taxonomy;
attention ledger; metric source discipline".

## What lives here

One file per collector. Declarations only - what each collector is allowed to
source, at what cadence, under what confirmation state, and how a metric reading
from it must be armed. No file here installs, configures or contacts anything.

## Who consumes it, and who does not

| Consumer | What it takes | Owner |
| --- | --- | --- |
| Operations VM install and collector configuration | cadence, targets, credentials shape | L5, ops-vm/** (subsystem M, spec line 9200) |
| Grafana surfaces of Section 92 | the armed set and the source kinds | subsystem H - UNASSIGNED in PARTITION v1, see D-L4-P5-03 |
| The metric register and the Section 103 computations | source-kinds.yaml, devlake-coverage.yaml | Lane 4 Phase 7, L4-P7-01 and L4-P7-02 |
| The reconciler drift rows | nothing in this directory | L3 |

L4 declares. L5 installs. H renders. Lane 4 opens no Grafana file and no
ops-vm/** file (PARTITION.md rule 1, line 25).

## The rule that binds every file here

Invariant 46 (spec line 9513): "Derived data is computed, never hand-maintained.
Metrics derive from the canonical record stores of Section 97, never from
hand-maintained numbers." DevLake, Prometheus and Scorecard are not Section 97
record stores. source-kinds.yaml (L4-P5-22) states what that means mechanically.
EOF

cat > tools/records/validate-ingest.sh <<'SHEOF'
#!/usr/bin/env bash
# INGEST dispatcher. Lane 4, Phase 5. Output contract: L4-06-tasks.md section 0.5.
set -eu
cd "$(dirname "$0")/../.."
PY="${L4_PY:-python}"
run() { [ -f "$1" ] || { echo "INGEST ERROR missing-limb"; exit 3; }; exec "$PY" "$1"; }
case "${1:-}" in
  --collectors)   run tools/records/ingest/collectors.py ;;
  --devlake)      run tools/records/ingest/devlake.py ;;
  --prometheus)   run tools/records/ingest/prometheus.py ;;
  --scorecard)    run tools/records/ingest/scorecard.py ;;
  --source-kinds) run tools/records/ingest/source_kind.py ;;
  --freshness)    run tools/records/ingest/freshness.py ;;
  "")
    n=0
    for f in collectors devlake prometheus scorecard source_kind freshness; do
      p="tools/records/ingest/${f}.py"
      [ -f "$p" ] || { echo "INGEST ERROR missing-limb"; exit 3; }
      "$PY" "$p" >/dev/null || { echo "INGEST FAIL limb"; exit 1; }
      n=$((n+1))
    done
    echo "INGEST OK limbs=${n}"
    ;;
  *) echo "INGEST ERROR unknown-limb"; exit 3 ;;
esac
SHEOF
chmod +x tools/records/validate-ingest.sh

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'test -f metrics/ingest/README.md' \
  'test -x tools/records/validate-ingest.sh' \
  'bash tools/records/validate-ingest.sh --collectors 2>&1 | grep -q "INGEST ERROR missing-limb"' \
  > tools/records/checks/L4-P5-14.sh

bash tools/records/validate-ingest.sh --collectors; echo "exit=$?"
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | All eight entry conditions hold | the eight-line block above, run as one paste | `E1 ok` `E2 exit=3` `E3 ok` `E4 ok 3.12.x` `E5 ok` `E6 ok` `E7 ok` `E8 ok` |
| 2 | The dispatcher exists and is executable | `test -x tools/records/validate-ingest.sh && echo OK` | `OK` |
| 3 | The dispatcher **fails closed** on a missing limb | `bash tools/records/validate-ingest.sh --collectors; echo "exit=$?"` | `INGEST ERROR missing-limb` then `exit=3` |
| 4 | An unknown limb is an error, never a pass | `bash tools/records/validate-ingest.sh --nonsense; echo "exit=$?"` | `INGEST ERROR unknown-limb` then `exit=3` |
| 5 | The README names H as unassigned | `grep -c "UNASSIGNED in PARTITION v1" metrics/ingest/README.md` | `1` |
| 6 | The README names no vendor install step | `grep -ci "docker\|compose\|apt-get\|helm" metrics/ingest/README.md` | `0` |
| 7 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-14; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-14 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-15` if:

- Any of E1–E8 fails. Each names the phase that owns it in §5. **Do not create another phase's artifact.** Blocker naming the condition id.
- Criterion 3 exits `0` instead of `3` → the dispatcher reports a missing limb as a pass. That is the fail-open shape §40.1 line 3671 forbids. Blocker.
- `metrics/ingest/` already exists on `integration` → a prior partial run. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/README.md tools/records/validate-ingest.sh tools/records/ingest/.gitkeep tools/records/checks/L4-P5-14.sh
git commit -m "L4-P5-14: Ingest entry gate, metrics/ingest skeleton and the INGEST dispatcher"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-ingest-gate
gh pr create --base integration --title "L4-P5-14: Ingest entry gate and dispatcher" \
  --body "Lane 4, Phase 5. Task L4-P5-14. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-15` — `collectors.yaml`: the three named collectors and their cadences

**Mode** LANE · **Size** M · **Depends on** `L4-P5-14` · **Spec** §99.2 line 9196; §94.2 lines 8406–8411; §84.4 line 8561; §85.2 line 8395
**Writes** `metrics/ingest/collectors.yaml`, `tools/records/ingest/collectors.py`, `tools/records/checks/L4-P5-15.sh`

§7.7 becomes one file. The collector set is **closed at three** because line 9196 names three. A fourth entry is a spec change, not a configuration change.

The Prometheus row deliberately declares **no scrape interval**. §38.4 line 3476 says a runaway becomes visible *"within a scrape interval"* and names no value; the interval belongs to the operations-VM Prometheus configuration, which is `ops-vm/**` and L5's (`PARTITION.md` line 21). Declaring a number here would invent one.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-collectors

cat > metrics/ingest/collectors.yaml <<'EOF'
# The three collectors of subsystem I - Master Spec section 99.2 line 9196.
# Closed set. A fourth collector is a spec change, not a configuration change.
schema: metrics/ingest/collectors.v1
spec_anchor: "MultiProduct_MasterSpec_v4.0.md 99.2 line 9196"
closed_set: true

collectors:
  devlake:
    produces: "engineering flow metrics from the organisation's git and review activity"
    cadence: nightly
    cadence_anchor: "94.2 line 8409 ingestion 04:00; line 8411 refresh complete 06:00"
    window_start_utc: "04:00"
    window_complete_utc: "06:00"
    declaration_file: metrics/ingest/devlake.yaml
    installed_by_lane: L5
    installed_at_path: "ops-vm/**"
    coverage_confirmation_required: true      # 99.3 item 4, line 9243
  prometheus:
    produces: "liveness, dependency health, deployed digest and product metrics"
    cadence: scrape
    cadence_anchor: "41.2 lines 3719-3728; 38.4 line 3476 refers to 'a scrape interval' and names no value"
    scrape_interval_declared_by_l4: false     # the interval lives in the ops-VM configuration
    scrape_interval_owner_lane: L5
    declaration_file: metrics/ingest/prometheus.yaml
    installed_by_lane: L5
    installed_at_path: "ops-vm/**"
    coverage_confirmation_required: false
  scorecard:
    produces: "risk score per product"
    produces_anchor: "85.2 line 8395; 84.4 line 8561"
    cadence: nightly
    cadence_anchor: "94.2 line 8406 full scan 02:00; 84.4 line 8561 nightly"
    window_start_utc: "02:00"
    declaration_file: metrics/ingest/scorecard.yaml
    installed_by_lane: L5
    installed_at_path: "ops-vm/**"
    coverage_confirmation_required: false

# Every collector is a read-side instrument. None of them is a Section 97 record
# store, and none of them is a source of truth. See source-kinds.yaml (L4-P5-22).
not_a_record_store: [devlake, prometheus, scorecard]

# Subsystem M installs them; subsystem H renders from them; L4 declares them.
declaring_lane: L4
installing_subsystem: M
rendering_subsystem: H
rendering_subsystem_lane: UNASSIGNED-D-L4-P5-03
EOF

cat > tools/records/ingest/collectors.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --collectors limb. Master Spec 99.2 line 9196."""
import sys, yaml

NAMES = ["devlake", "prometheus", "scorecard"]


def fail(msg):
    print("INGEST FAIL collectors %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/ingest/collectors.yaml", encoding="utf-8"))
    except Exception as e:
        print("INGEST ERROR collectors-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("closed_set") is not True:
        fail("collector-set-not-closed")
    c = d.get("collectors") or {}
    if sorted(c) != NAMES:
        fail("collectors-not-the-three-of-line-9196")
    if c["devlake"].get("cadence") != "nightly" or c["scorecard"].get("cadence") != "nightly":
        fail("nightly-cadence-missing")
    if c["devlake"].get("window_start_utc") != "04:00":
        fail("devlake-window-not-0400")
    if c["devlake"].get("window_complete_utc") != "06:00":
        fail("devlake-refresh-not-0600")
    if c["scorecard"].get("window_start_utc") != "02:00":
        fail("scorecard-scan-not-0200")
    if c["devlake"].get("coverage_confirmation_required") is not True:
        fail("devlake-coverage-confirmation-not-required")
    p = c["prometheus"]
    if p.get("scrape_interval_declared_by_l4") is not False:
        fail("l4-declares-a-scrape-interval-it-must-not-invent")
    if p.get("scrape_interval_owner_lane") != "L5":
        fail("scrape-interval-owner-not-L5")
    for n in NAMES:
        if c[n].get("installed_by_lane") != "L5" or c[n].get("installed_at_path") != "ops-vm/**":
            fail("collector-installation-not-routed-to-L5")
        if not (c[n].get("declaration_file") or "").startswith("metrics/ingest/"):
            fail("declaration-file-outside-metrics-ingest")
    if sorted(d.get("not_a_record_store") or []) != NAMES:
        fail("collectors-claimed-as-record-stores")
    if d.get("rendering_subsystem") != "H":
        fail("rendering-subsystem-not-H")
    if d.get("rendering_subsystem_lane") != "UNASSIGNED-D-L4-P5-03":
        fail("H-claimed-by-a-lane-without-L0")
    print("INGEST OK collectors=3 nightly=2 scrape=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --collectors | grep -qx "INGEST OK collectors=3 nightly=2 scrape=1"' \
  > tools/records/checks/L4-P5-15.sh

bash tools/records/validate-ingest.sh --collectors
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --collectors` | `INGEST OK collectors=3 nightly=2 scrape=1` |
| 2 | Exactly the three collectors of line 9196 | `"$L4_PY" -c "import yaml;print(','.join(sorted(yaml.safe_load(open('metrics/ingest/collectors.yaml'))['collectors'])))"` | `devlake,prometheus,scorecard` |
| 3 | DevLake window is 04:00→06:00 | `"$L4_PY" -c "import yaml;c=yaml.safe_load(open('metrics/ingest/collectors.yaml'))['collectors']['devlake'];print(c['window_start_utc'],c['window_complete_utc'])"` | `04:00 06:00` |
| 4 | Scorecard full scan is 02:00, nightly | `"$L4_PY" -c "import yaml;c=yaml.safe_load(open('metrics/ingest/collectors.yaml'))['collectors']['scorecard'];print(c['window_start_utc'],c['cadence'])"` | `02:00 nightly` |
| 5 | L4 declares **no** scrape interval | `grep -ci "scrape_interval_seconds\|interval: *[0-9]" metrics/ingest/collectors.yaml` | `0` |
| 6 | No collector is claimed as a record store | `"$L4_PY" -c "import yaml;print(len(yaml.safe_load(open('metrics/ingest/collectors.yaml'))['not_a_record_store']))"` | `3` |
| 7 | Subsystem H is not claimed | `"$L4_PY" -c "import yaml;print(yaml.safe_load(open('metrics/ingest/collectors.yaml'))['rendering_subsystem_lane'])"` | `UNASSIGNED-D-L4-P5-03` |
| 8 | The check **can fail** | `cp metrics/ingest/collectors.yaml /tmp/co.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/collectors.yaml';d=yaml.safe_load(open(p));d['collectors']['prometheus']['scrape_interval_declared_by_l4']=True;yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --collectors; echo "exit=$?"; cp /tmp/co.bak metrics/ingest/collectors.yaml` | `INGEST FAIL collectors l4-declares-a-scrape-interval-it-must-not-invent` then `exit=1` |
| 9 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-15; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-15 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-16` if:

- Any step would add a fourth collector. Line 9196 names three. A fourth is a spec change. Blocker.
- Any step asks you for a scrape interval, a database engine, a port or a hostname → all four are `ops-vm/**` and L5's. Blocker.
- Criterion 8 does not print `INGEST FAIL`. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/collectors.yaml tools/records/ingest/collectors.py tools/records/checks/L4-P5-15.sh
git commit -m "L4-P5-15: collectors.yaml - the three named collectors and their cadences"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-collectors
gh pr create --base integration --title "L4-P5-15: Collector declarations" \
  --body "Lane 4, Phase 5. Task L4-P5-15. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-16` — DevLake nightly ingest declaration and the §99.3 coverage gate

**Mode** LANE · **Size** M · **Depends on** `L4-P5-15` · **Spec** §99.2 line 9196; §99.3 item 4 line 9243; §30.3 line 2737; §98 Phase G3 line 9133; §94.2 lines 8409, 8411; §52.2 line 4524
**Writes** `metrics/ingest/devlake.yaml`, `metrics/ingest/devlake-coverage.yaml`, `tools/records/ingest/devlake.py`, `tools/records/checks/L4-P5-16.sh`

This is the task the ingest half exists for. §99.3 item 4 (§7.9) says DevLake field coverage is **design-open** and must be *"confirm[ed] … before Phase G3"*. §30.3 line 2737 repeats it as an *"unverified capability assumption"*. §98 Phase G3 line 9133 lists *"DevLake field coverage confirmed"* as a dependency of that phase.

An unconfirmed assumption is only a caveat if something reads it. This task makes it mechanical: **`devlake-coverage.yaml` is the gate.** Every row is `unconfirmed` until a human returns evidence, and a consumer of an unconfirmed row renders `unarmed — not yet instrumented` under D77 (§52.2 line 4524) — never as a miss, never as zero.

**The consumer census is thirteen, and it is not a judgment call.** A DevLake consumer is a metric or signal row whose Source cell names DevLake. Those rows are at spec lines 4533, 4536, 4537, 4569, 7048, 7052, 7053, 9782, 9787, 9794, 9811, 9954 and 9963. Criterion 3 below proves each of those lines really does contain the string `DevLake`, so no line number in the file is inferred.

**The three bespoke computations are the three named in item 4, verbatim** — *"routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread measures"*. They carry `covered_by_devlake_models: false` because line 9243 says they *"require bespoke computation beyond DevLake's models"*. That is a transcription, not an assessment.

**You do not confirm coverage in this task.** Confirmation needs the DevLake console; that is `L4-P5-17`, and it is ASSISTED.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-devlake

cat > metrics/ingest/devlake.yaml <<'EOF'
# DevLake nightly ingest - Master Spec section 99.2 line 9196.
# Declaration only. The operations VM that runs DevLake is subsystem M (line 9200)
# and PARTITION.md line 21 gives ops-vm/** to L5. L4 opens no ops-vm file.
schema: metrics/ingest/devlake.v1
collector: devlake
source_kind: collector                 # never a Section 97 record store - see source-kinds.yaml
cadence: nightly
window_start_utc: "04:00"              # 94.2 line 8409 "DevLake ingestion"
window_complete_utc: "06:00"           # 94.2 line 8411 "DevLake refresh complete"

# The required database engine is an unverified capability assumption (30.3 line 2737)
# and an operations-VM concern. L4 names no engine and no version.
database_engine_declared_by_l4: false
database_engine_owner_lane: L5
database_engine_spec_anchor: "30.3 line 2737 - DevLake's connector field coverage and required database engine"

# Every metric or signal row in the spec whose Source cell names DevLake.
# kind: measure = a Section 79 or Section 103 metric row. kind: signal = a Section 52.2 SIG row.
consumers:
  - id: C01
    name: "SIG-04 Review concentration"
    kind: signal
    spec_line: 4533
  - id: C02
    name: "SIG-07 Team Lead bottleneck"
    kind: signal
    spec_line: 4536
  - id: C03
    name: "SIG-08 QA bottleneck"
    kind: signal
    spec_line: 4537
  - id: C04
    name: "SIG-40 Cross-review participation"
    kind: signal
    spec_line: 4569
    source_cell: "DevLake plus registries"
  - id: C05
    name: "Review distribution spread"
    kind: measure
    spec_line: 7048
  - id: C06
    name: "Verification demand vs capacity"
    kind: measure
    spec_line: 7052
    source_cell: "DevLake, verification contracts"
  - id: C07
    name: "Gate 1 latency"
    kind: measure
    spec_line: 7053
  - id: C08
    name: "PR cycle time per product, median and 90th percentile"
    kind: measure
    spec_line: 9782
  - id: C09
    name: "Cross-review turnaround, median and 90th percentile"
    kind: measure
    spec_line: 9787
  - id: C10
    name: "Lead time, merge to production"
    kind: measure
    spec_line: 9794
  - id: C11
    name: "Undeclared weekend activations per quarter"
    kind: measure
    spec_line: 9811
    source_cell: "event log (Section 97.3) and DevLake activity"
  - id: C12
    name: "Review hours per product per month"
    kind: measure
    spec_line: 9954
  - id: C13
    name: "Ownership transfer time to first verified change"
    kind: measure
    spec_line: 9963
    source_cell: "Registries plus DevLake"

# The three computations Section 99.3 item 4 (line 9243) names as beyond DevLake's
# models. Quoted, not paraphrased. Each still needs a coverage answer, because the
# bespoke computation reads DevLake rows even where DevLake does not compute it.
bespoke_computations:
  - id: B1
    quoted: "routine reviews absorbed cross-checked against the routing table"
    spec_line: 9243
    covered_by_devlake_models: false
    measure_row_spec_line: 9870
  - id: B2
    quoted: "reviewer familiarity"
    spec_line: 9243
    covered_by_devlake_models: false
    other_spec_anchor: none-in-spec
  - id: B3
    quoted: "reviewer-spread measures"
    spec_line: 9243
    covered_by_devlake_models: false
    measure_row_spec_line: 4533

coverage_file: metrics/ingest/devlake-coverage.yaml
installed_by_lane: L5
installed_at_path: "ops-vm/**"
EOF

cat > metrics/ingest/devlake-coverage.yaml <<'EOF'
# The Section 99.3 item 4 coverage gate, line 9243:
# "DevLake field coverage - several metrics (routine reviews absorbed cross-checked
#  against the routing table, reviewer familiarity, reviewer-spread measures) require
#  bespoke computation beyond DevLake's models; confirm coverage before Phase G3."
#
# Reinforced at 30.3 line 2737 (unverified capability assumption) and at
# 98 Phase G3 line 9133 ("Dependencies: G1-G2; DevLake field coverage confirmed").
#
# NO ROW IN THIS FILE IS CONFIRMED BY LANE 4. Confirmation requires the DevLake
# console on the operations VM and is task L4-P5-17, mode ASSISTED. A row moves off
# "unconfirmed" only when the human lead returns the evidence file named below.
schema: metrics/ingest/devlake-coverage.v1
gate_phase: G3
gate_spec_line: 9133
caveat_spec_line: 9243
assumption_spec_line: 2737
confirmed: false
evidence_file: metrics/ingest/evidence/devlake-coverage-evidence.yaml
evidence_template: metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml
evidence_authored_by_lane_4: false

# D77, section 52.2 line 4524. Frozen string - see L4-05-pipeline-and-boards.md 7.10.
arming_state_while_unconfirmed: "unarmed — not yet instrumented"
never_renders_as: [miss, zero, amber, missing-data]

# One row per consumer of devlake.yaml, plus one per bespoke computation.
# state is exactly one of: unconfirmed | confirmed | unavailable
rows:
  - {ref: C01, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C02, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C03, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C04, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C05, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C06, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C07, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C08, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C09, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C10, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C11, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C12, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: C13, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: B1, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: B2, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
  - {ref: B3, state: unconfirmed, confirmed_by: "", confirmed_at: ""}
EOF

cat > tools/records/ingest/devlake.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --devlake limb. Master Spec 99.2 line 9196; 99.3 item 4 line 9243."""
import os
import sys
import yaml

CONSUMER_LINES = [4533, 4536, 4537, 4569, 7048, 7052, 7053,
                  9782, 9787, 9794, 9811, 9954, 9963]
STATES = {"unconfirmed", "confirmed", "unavailable"}
UNARMED = "unarmed — not yet instrumented"   # 52.2 line 4524, frozen vocabulary


def fail(msg):
    print("INGEST FAIL devlake %s" % msg)
    sys.exit(1)


def load(path):
    try:
        return yaml.safe_load(open(path, encoding="utf-8"))
    except Exception as e:
        print("INGEST ERROR devlake-unreadable:%s:%s"
              % (os.path.basename(path), type(e).__name__))
        sys.exit(3)


def main():
    d = load("metrics/ingest/devlake.yaml")
    cov = load("metrics/ingest/devlake-coverage.yaml")
    col = load("metrics/ingest/collectors.yaml")["collectors"]["devlake"]

    if d.get("source_kind") != "collector":
        fail("devlake-claimed-as-record-store")
    if d.get("cadence") != col.get("cadence"):
        fail("cadence-diverges-from-collectors-yaml")
    if d.get("window_start_utc") != col.get("window_start_utc"):
        fail("window-start-diverges-from-collectors-yaml")
    if d.get("window_complete_utc") != col.get("window_complete_utc"):
        fail("window-complete-diverges-from-collectors-yaml")
    if d.get("database_engine_declared_by_l4") is not False:
        fail("l4-declares-a-database-engine-it-must-not-invent")
    if d.get("database_engine_owner_lane") != "L5":
        fail("database-engine-owner-not-L5")

    cons = d.get("consumers") or []
    if sorted(c.get("spec_line") for c in cons) != CONSUMER_LINES:
        fail("consumer-census-not-the-thirteen-devlake-source-rows")
    if len({c.get("id") for c in cons}) != 13:
        fail("duplicate-consumer-id")
    for c in cons:
        if c.get("kind") not in ("measure", "signal"):
            fail("consumer-kind-not-measure-or-signal:%s" % c.get("id"))

    bes = d.get("bespoke_computations") or []
    if len(bes) != 3:
        fail("bespoke-computations-not-three-of-line-9243")
    for b in bes:
        if b.get("spec_line") != 9243:
            fail("bespoke-not-anchored-at-9243:%s" % b.get("id"))
        if b.get("covered_by_devlake_models") is not False:
            fail("bespoke-claimed-covered:%s" % b.get("id"))

    if cov.get("gate_phase") != "G3" or cov.get("gate_spec_line") != 9133:
        fail("coverage-gate-not-G3-line-9133")
    if cov.get("arming_state_while_unconfirmed") != UNARMED:
        fail("unconfirmed-arming-string-not-frozen-vocabulary")
    if cov.get("evidence_authored_by_lane_4") is not False:
        fail("lane-4-claims-authorship-of-assisted-evidence")

    rows = cov.get("rows") or []
    want = sorted([c["id"] for c in cons] + [b["id"] for b in bes])
    if sorted(r.get("ref") for r in rows) != want:
        fail("coverage-rows-do-not-cover-every-consumer-and-bespoke")

    ev = cov.get("evidence_file")
    ev_present = bool(ev) and os.path.isfile(ev)
    n_conf = 0
    for r in rows:
        st = r.get("state")
        if st not in STATES:
            fail("bad-state:%s:%s" % (r.get("ref"), st))
        if st != "unconfirmed":
            n_conf += 1
            if not ev_present:
                fail("confirmed-without-evidence:%s" % r.get("ref"))
            if not r.get("confirmed_by") or not r.get("confirmed_at"):
                fail("confirmed-without-attribution:%s" % r.get("ref"))
    if cov.get("confirmed") is not (n_conf == len(rows)):
        fail("coverage-flag-inconsistent-with-rows")
    if ev_present:
        evd = load(ev) or {}
        if evd.get("authored_by") in (None, "", "lane-4", "L4"):
            fail("lane-authored-evidence-is-not-evidence")

    print("INGEST OK devlake consumers=13 bespoke=3 coverage_rows=16 gate=G3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --devlake | grep -qx "INGEST OK devlake consumers=13 bespoke=3 coverage_rows=16 gate=G3"' \
  > tools/records/checks/L4-P5-16.sh

bash tools/records/validate-ingest.sh --devlake
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --devlake` | `INGEST OK devlake consumers=13 bespoke=3 coverage_rows=16 gate=G3` |
| 2 | Thirteen consumers, three bespoke, sixteen coverage rows | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/devlake.yaml'));c=yaml.safe_load(open('metrics/ingest/devlake-coverage.yaml'));print(len(d['consumers']),len(d['bespoke_computations']),len(c['rows']))"` | `13 3 16` |
| 3 | **No line number is inferred** — every cited spec line really contains `DevLake` | `for n in 4533 4536 4537 4569 7048 7052 7053 9782 9787 9794 9811 9954 9963 9243; do sed -n "${n}p" "$SPEC" \| grep -q DevLake \|\| echo "BAD $n"; done; echo SPECLINES-OK` | `SPECLINES-OK`, with no `BAD` line before it |
| 4 | Every coverage row is `unconfirmed` | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open('metrics/ingest/devlake-coverage.yaml'))['rows'];print(sorted({x['state'] for x in r}))"` | `['unconfirmed']` |
| 5 | The gate is G3 and the coverage flag is false | `"$L4_PY" -c "import yaml;c=yaml.safe_load(open('metrics/ingest/devlake-coverage.yaml'));print(c['gate_phase'],c['confirmed'])"` | `G3 False` |
| 6 | L4 declares **no** database engine | `grep -ci "postgres\|mysql\|mariadb\|sqlite\|clickhouse" metrics/ingest/devlake.yaml` | `0` |
| 7 | The unconfirmed arming string is the frozen §7.10 string, em dash included — checked by code point so no em dash need be typed | `"$L4_PY" -c "import yaml;s=yaml.safe_load(open('metrics/ingest/devlake-coverage.yaml'))['arming_state_while_unconfirmed'];print(len(s),ord(s[8])==8212,s.endswith('not yet instrumented'))"` | `30 True True` |
| 8 | The check **can fail** — a row confirmed with no evidence is rejected | `cp metrics/ingest/devlake-coverage.yaml /tmp/dc.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/devlake-coverage.yaml';d=yaml.safe_load(open(p));d['rows'][0]['state']='confirmed';yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --devlake; echo "exit=$?"; cp /tmp/dc.bak metrics/ingest/devlake-coverage.yaml` | `INGEST FAIL devlake confirmed-without-evidence:C01` then `exit=1` |
| 9 | The check **fails closed** when its input is gone | `mv metrics/ingest/devlake-coverage.yaml /tmp/dc2.bak; bash tools/records/validate-ingest.sh --devlake; echo "exit=$?"; mv /tmp/dc2.bak metrics/ingest/devlake-coverage.yaml` | `INGEST ERROR devlake-unreadable:devlake-coverage.yaml:FileNotFoundError` then `exit=3` |
| 10 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-16; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-16 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-17` if:

- Criterion 3 prints any `BAD <n>` line → a spec line number in this file does not name DevLake. **Do not "fix" it by editing the number.** Blocker, quoting the `BAD` line.
- Criterion 8 exits `0` → the gate accepts a confirmation with no evidence, and the §99.3 caveat is decoration (`L4-06-tasks.md` §0.8 rule 9). Blocker.
- Criterion 9 exits `0` or `1` instead of `3` → the limb reports a pass it cannot support (§40.1 line 3671). Blocker.
- Any step appears to require opening DevLake, running a connector, or reading a token. That is `L4-P5-17` and it is **ASSISTED**. Blocker.
- You are tempted to set a row to `confirmed` because it "obviously" works. **Never.** Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/devlake.yaml metrics/ingest/devlake-coverage.yaml tools/records/ingest/devlake.py tools/records/checks/L4-P5-16.sh
git commit -m "L4-P5-16: DevLake nightly ingest declaration and the section 99.3 coverage gate"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-devlake
gh pr create --base integration --title "L4-P5-16: DevLake declaration and coverage gate" \
  --body "Lane 4, Phase 5. Task L4-P5-16. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-17` — **ASSISTED** — DevLake connector field-coverage confirmation

**Mode ASSISTED** · **Size** M · **Depends on** `L4-P5-16` · **Spec** §99.3 item 4 line 9243; §30.3 line 2737; §98 Phase G3 line 9133
**Writes** `metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md`, `metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml`, `tools/records/checks/L4-P5-17.sh`
**Does NOT write** `metrics/ingest/evidence/devlake-coverage-evidence.yaml` — that file is authored by the human lead and by nobody else.

> **ASSISTED — read this before typing anything.** Confirming connector field coverage requires the DevLake console or API on the operations VM and the connector's configured GitHub token (§3.1; §30.3 line 2737). You must not hold either. **You produce the request document and the evidence template, open the handoff issue, and stop.** You do not open DevLake. You do not run a connector. You do not paste a credential anywhere, including into a blocker issue. If you find yourself about to, that is the STOP rule firing.

The evidence rule of §3.1 applies in full: **a validator that passes on an evidence file you wrote is not a check.** `L4-P5-16`'s limb already refuses an evidence file whose `authored_by` is `lane-4` or empty. This task keeps that true by shipping a template in which every answer field is `PENDING-HUMAN`.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-devlake-coverage-request

mkdir -p metrics/ingest/requests metrics/ingest/evidence

cat > metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md <<'EOF'
# ASSISTED request L4-P5-17 - DevLake connector field coverage

Requested of: the L0 human lead, or a delegate holding operations-VM access.
Requested by: Lane 4, Phase 5, task L4-P5-17. Prepared by the lane executor, who holds
no DevLake credential and ran nothing against DevLake.

## Why this request exists

Master Spec section 99.3 item 4, line 9243, verbatim:

  "DevLake field coverage - several metrics (routine reviews absorbed cross-checked
   against the routing table, reviewer familiarity, reviewer-spread measures) require
   bespoke computation beyond DevLake's models; confirm coverage before Phase G3."

Section 30.3 line 2737 lists "DevLake's connector field coverage and required database
engine" among the unverified capability assumptions, "each confirmed before the phase
depending on it". Section 98 Phase G3, line 9133, lists "DevLake field coverage
confirmed" as a dependency of Phase G3.

Until this request is answered, all sixteen rows of metrics/ingest/devlake-coverage.yaml
stay "unconfirmed" and every consumer renders "unarmed - not yet instrumented"
(D77, section 52.2 line 4524). Nothing breaks. Nothing lies either.

## What is being asked

For each of the sixteen rows below, answer exactly one of:

  confirmed   - DevLake, as configured on this estate, supplies what this row needs
  unavailable - it does not, and a bespoke computation or another source is required

Do not answer "partial". A row that is partly covered is "unavailable" for this gate:
the gate exists to stop a metric arming on data that is not fully there.

## The sixteen rows

Thirteen consumers - every spec row whose Source cell names DevLake:

| ref | consumer | spec line |
| --- | --- | --- |
| C01 | SIG-04 Review concentration | 4533 |
| C02 | SIG-07 Team Lead bottleneck | 4536 |
| C03 | SIG-08 QA bottleneck | 4537 |
| C04 | SIG-40 Cross-review participation | 4569 |
| C05 | Review distribution spread | 7048 |
| C06 | Verification demand vs capacity | 7052 |
| C07 | Gate 1 latency | 7053 |
| C08 | PR cycle time per product | 9782 |
| C09 | Cross-review turnaround | 9787 |
| C10 | Lead time, merge to production | 9794 |
| C11 | Undeclared weekend activations per quarter | 9811 |
| C12 | Review hours per product per month | 9954 |
| C13 | Ownership transfer time to first verified change | 9963 |

Three bespoke computations - quoted from line 9243:

| ref | quoted | spec line |
| --- | --- | --- |
| B1 | routine reviews absorbed cross-checked against the routing table | 9243 |
| B2 | reviewer familiarity | 9243 |
| B3 | reviewer-spread measures | 9243 |

## How to answer

Copy metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml to
metrics/ingest/evidence/devlake-coverage-evidence.yaml, fill every PENDING-HUMAN field,
and commit it. Then set the matching rows in metrics/ingest/devlake-coverage.yaml to the
answered state with confirmed_by and confirmed_at populated, and set the top-level
"confirmed" flag to true only when every row is answered. The validator
(tools/records/ingest/devlake.py) refuses any other combination.

## What the lane executor did NOT do

- did not open the DevLake console or call its API
- did not read, hold or transcribe any credential
- did not author metrics/ingest/evidence/devlake-coverage-evidence.yaml
- did not set any row of devlake-coverage.yaml to anything but "unconfirmed"

## Also unanswered, and deliberately not asked here

The required database engine (section 30.3 line 2737) is an operations-VM concern:
PARTITION.md line 21 gives ops-vm/** to L5. It is not part of this request.
EOF

cat > metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml <<'EOF'
# TEMPLATE - copy to devlake-coverage-evidence.yaml and fill in. Do not edit in place.
# Authored by the human lead who ran the console session. NEVER by lane 4:
# tools/records/ingest/devlake.py rejects an evidence file whose authored_by is
# "lane-4", "L4" or empty (L4-05-pipeline-and-boards.md section 3.1).
# This file must never carry a credential of any kind, nor a host address.
schema: metrics/ingest/devlake-coverage-evidence.v1
request: metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md
authored_by: PENDING-HUMAN            # the person who ran the session, not a lane id
authored_at: PENDING-HUMAN            # UTC with offset (L4-06-tasks.md section 0.8 rule 8)
devlake_version: PENDING-HUMAN
connector: PENDING-HUMAN
session_note: PENDING-HUMAN           # what was inspected, in one or two sentences
credentials_present: false

rows:
  - {ref: C01, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C02, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C03, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C04, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C05, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C06, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C07, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C08, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C09, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C10, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C11, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C12, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: C13, state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: B1,  state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: B2,  state: PENDING-HUMAN, note: PENDING-HUMAN}
  - {ref: B3,  state: PENDING-HUMAN, note: PENDING-HUMAN}
EOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'test -f metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md' \
  'test -f metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml' \
  '[ "$(grep -c PENDING-HUMAN metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml || true)" = "21" ]' \
  '[ "$(grep -c "state: confirmed" metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml || true)" = "0" ]' \
  'bash tools/records/validate-ingest.sh --devlake | grep -q "INGEST OK devlake"' \
  > tools/records/checks/L4-P5-17.sh

bash tools/records/check.sh L4-P5-17; echo "exit=$?"
```

Then open the handoff issue. This is the last command of the task:

```bash
set -euo pipefail
gh issue create --repo "${CP_SLUG}" --title "ASSISTED L4-P5-17: DevLake connector field-coverage confirmation" --label assisted,lane-4 --body "$(cat <<'EOF'
assisted_task: L4-P5-17
lane: 4
phase: 5
mode: ASSISTED
branch: lane/4/05-devlake-coverage-request
repo: control-plane
needs_from_human: DevLake console or API on the operations VM, plus the connector's configured GitHub token
why_a_lane_executor_cannot_do_it: the credential must not be held by a lane executor (L4-05-pipeline-and-boards.md section 3)
request_document: metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md
evidence_template: metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml
evidence_file_to_create: metrics/ingest/evidence/devlake-coverage-evidence.yaml
rows_awaiting_answer: 16
spec_anchor: "99.3 item 4 line 9243; 30.3 line 2737; 98 Phase G3 line 9133"
blocks: "Phase G3 (spec line 9133). Blocks nothing inside lane 4 phase 5."
state_until_answered: "all sixteen rows unconfirmed; every consumer renders unarmed - not yet instrumented (D77, line 4524)"
what_the_executor_did: "wrote the request document, the evidence template and the task check; opened this issue; stopped"
what_the_executor_did_NOT_do: "did not open DevLake, did not run a connector, did not hold or transcribe a credential, did not author the evidence file"
EOF
)"
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The request document exists | `test -f metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md && echo OK` | `OK` |
| 2 | The template is a template, not an answer — 21 lines still awaiting a human | `grep -c "PENDING-HUMAN" metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml` | `21` |
| 3 | The lane confirmed nothing (`grep -c` exiting `1` on no match is normal; the printed `0` is the criterion) | `grep -c "state: confirmed" metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml` | `0` |
| 4 | The real evidence file was **not** created by the lane | `test -f metrics/ingest/evidence/devlake-coverage-evidence.yaml && echo CREATED \|\| echo NOT-CREATED` | `NOT-CREATED` |
| 5 | Coverage rows are still all unconfirmed | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open('metrics/ingest/devlake-coverage.yaml'))['rows'];print(sorted({x['state'] for x in r}))"` | `['unconfirmed']` |
| 6 | The template carries no credential field | `grep -ci "token\|password\|secret\|api_key\|connection_string" metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml` | `0` |
| 7 | The DevLake limb still passes | `bash tools/records/validate-ingest.sh --devlake` | `INGEST OK devlake consumers=13 bespoke=3 coverage_rows=16 gate=G3` |
| 8 | The handoff issue is open | `gh issue list --repo "${CP_SLUG}" --label assisted --search "L4-P5-17" --json number \| grep -c number` | `1` |
| 9 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-17; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-17 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-18` if:

- Any step would have you open the DevLake console, call its API, or read a credential. **That is the ASSISTED boundary of §3.** Blocker.
- Criterion 4 prints `CREATED` → the lane authored the evidence file. Delete it, commit nothing, and file the blocker.
- Criterion 2 prints anything other than `21` → the template has been partly filled. A partly-filled template is an answer, and the lane does not answer. Blocker.
- `gh issue create` fails → the handoff never reached a human, so the task is not done even though its files exist. Blocker.

**Once the handoff issue is open, this task is complete for you.** Do not wait for the answer; the coverage gate blocks Phase G3, not this phase. Take `L4-P5-18`.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/requests/L4-P5-17-devlake-coverage-request.md metrics/ingest/evidence/devlake-coverage-evidence.TEMPLATE.yaml tools/records/checks/L4-P5-17.sh
git commit -m "L4-P5-17: ASSISTED handoff - DevLake coverage request and evidence template"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-devlake-coverage-request
gh pr create --base integration --title "L4-P5-17: ASSISTED - DevLake coverage request and template" \
  --body "Lane 4, Phase 5. Task L4-P5-17, mode ASSISTED. Request and template only; no console session, no evidence authored by the lane. Handoff issue opened."
```

---

### TASK `L4-P5-18` — Prometheus scrape declaration: the three §41.2 endpoints

**Mode** LANE · **Size** M · **Depends on** `L4-P5-15` · **Spec** §41.2 lines 3719, 3723–3725, 3726, 3728; §38.4 line 3476; §19.2 line 1892; §103.2 line 9798
**Writes** `metrics/ingest/prometheus.yaml`, `tools/records/ingest/prometheus.py`, `tools/records/checks/L4-P5-18.sh`

§7.8 becomes one file. Five things about this task are easy to get wrong, so they are stated before the commands:

1. **Three endpoints, not four, and the `Provides` strings are transcribed character-for-character** from spec lines 3723–3725. They are *"the entire runtime interface the operating system requires of a served product"* (line 3719).
2. **The endpoints are not a public surface** (line 3726). The estate's declared posture is `private-authenticated`, with a **per-product scrape credential**, and `public` is *"a recorded Founder decision, never a default inherited from a framework."* A file that declares `public` here is wrong, not configurable.
3. **The private path is a scrape path only** — line 3726: *"it carries the operations VM no production credential, no deploy key and no environment access."* The declaration says so explicitly, so a later reader cannot quietly widen it.
4. **No interval, no host, no port, no URL.** The Prometheus configuration lives on the operations VM, which is `ops-vm/**` and L5's (`PARTITION.md` line 21). Criterion 6 fails the task if a URL or a port appears anywhere in the file.
5. **Export the `/version` digest observation to a named records-repo path per REG-034.**

A product declaring a profile that cannot serve an endpoint *"meets the equivalent evidence of Section 15.7 instead, and is never failed for lacking an endpoint its shape cannot serve"* (line 3719). That exemption is declared here, not inferred later.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-prometheus

cat > metrics/ingest/prometheus.yaml <<'EOF'
# Prometheus scraping of the three required endpoints - Master Spec 99.2 line 9196,
# defined at section 41.2. Declaration only: no interval, no host, no port, no URL.
# The Prometheus configuration itself is ops-vm/** and belongs to L5 (PARTITION.md line 21).
schema: metrics/ingest/prometheus.v1
collector: prometheus
source_kind: collector                 # never a Section 97 record store
scrape_interval_declared_by_l4: false  # 38.4 line 3476 says "a scrape interval" and names no value
scrape_interval_owner_lane: L5

# Transcribed from the table at spec lines 3721-3725. Provides strings are verbatim.
endpoints:
  - path: /health
    provides: "Liveness plus dependency health, distinguishing internal from external failure"
    spec_line: 3723
  - path: /version
    provides: "Deployed artifact digest and build metadata"
    spec_line: 3724
  - path: /metrics
    provides: "Prometheus format"
    spec_line: 3725

# Line 3719: required of the profiles that expose the service interface.
required_for_conformance_profiles: [service, white-label]
white_label_note: "per deployment (line 3719)"
exempt_conformance_profiles: [batch, client-app, customer-hosted, library, static-site]
exempt_equivalent_evidence_section: "15.7"
never_failed_for_lacking_an_endpoint_its_shape_cannot_serve: true
profiles_spec_line: 3719

# Line 3726. The estate posture. "public" is a recorded Founder decision, never a default.
telemetry_exposure_field: observability.telemetry_exposure
telemetry_exposure_posture: private-authenticated
public_requires_recorded_founder_decision: true
public_is_a_framework_default: false
per_product_scrape_credential: true
exposure_spec_line: 3726

# Line 3726: the private path is a scrape path only.
private_path_carries_none_of: [deploy_key, environment_access, production_credential]
private_path_spec_line: 3726

# Line 3728, and the Section 103.2 row at line 9798.
version_digest_must_equal_approved_digest: true
version_digest_mismatch_severity: P0
version_spec_line: 3728
version_metric_row_spec_line: 9798

# Line 3476. The counters are exported BY the product; the alert rule is configured
# on the operations VM by L5. L4 declares neither a rule nor a threshold of its own.
ai_counters_exported_via: /metrics
ai_counters_content: "cumulative tokens and estimated spend per provider key for the current billing month"
alert_fraction_key: cost.metrics_alert_fraction
alert_fraction_initial_value_in_spec: 0.8
alert_rule_owner_lane: L5
l4_declares_alert_rule: false
ai_counters_spec_line: 3476

# Line 1892, launch readiness. The proof is an ASSISTED evidence file, never a lane run.
launch_readiness_row_spec_line: 1892
public_unreachability_evidence_file: metrics/ingest/evidence/scrape-reachability-evidence.yaml
evidence_authored_by_lane_4: false

installed_by_lane: L5
installed_at_path: "ops-vm/**"
EOF

cat > tools/records/ingest/prometheus.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --prometheus limb. Master Spec 41.2 lines 3719-3728."""
import re
import sys
import yaml

PATH = "metrics/ingest/prometheus.yaml"
ENDPOINTS = [
    ("/health", "Liveness plus dependency health, distinguishing internal from external failure", 3723),
    ("/version", "Deployed artifact digest and build metadata", 3724),
    ("/metrics", "Prometheus format", 3725),
]
EXEMPT = ["batch", "client-app", "customer-hosted", "library", "static-site"]
CARRIES_NONE = ["deploy_key", "environment_access", "production_credential"]
FORBIDDEN = re.compile(r"https?://|:9090|:9100|hostname|ip_address|scrape_interval_seconds")


def fail(msg):
    print("INGEST FAIL prometheus %s" % msg)
    sys.exit(1)


def main():
    try:
        raw = open(PATH, encoding="utf-8").read()
        d = yaml.safe_load(raw)
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml", encoding="utf-8"))
    except Exception as e:
        print("INGEST ERROR prometheus-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    if FORBIDDEN.search(raw):
        fail("host-port-url-or-interval-declared-by-l4")
    if d.get("source_kind") != "collector":
        fail("prometheus-claimed-as-record-store")

    eps = d.get("endpoints") or []
    if [(e.get("path"), e.get("provides"), e.get("spec_line")) for e in eps] != ENDPOINTS:
        fail("endpoints-not-the-three-of-lines-3723-3725")

    if d.get("required_for_conformance_profiles") != ["service", "white-label"]:
        fail("required-profiles-not-service-and-white-label")
    if sorted(d.get("exempt_conformance_profiles") or []) != EXEMPT:
        fail("exempt-profiles-not-the-five-of-line-3719")
    if d.get("exempt_equivalent_evidence_section") != "15.7":
        fail("exempt-evidence-section-not-15-7")
    if d.get("never_failed_for_lacking_an_endpoint_its_shape_cannot_serve") is not True:
        fail("shape-exemption-not-declared")

    if d.get("telemetry_exposure_posture") != "private-authenticated":
        fail("posture-not-private-authenticated")
    if d.get("public_requires_recorded_founder_decision") is not True:
        fail("public-without-a-recorded-founder-decision")
    if d.get("public_is_a_framework_default") is not False:
        fail("public-declared-as-a-framework-default")
    if d.get("per_product_scrape_credential") is not True:
        fail("per-product-scrape-credential-not-declared")
    if sorted(d.get("private_path_carries_none_of") or []) != CARRIES_NONE:
        fail("private-path-scope-widened-beyond-line-3726")

    if d.get("version_digest_must_equal_approved_digest") is not True:
        fail("version-digest-equality-not-declared")
    if d.get("version_digest_mismatch_severity") != "P0":
        fail("digest-mismatch-not-p0")

    if d.get("ai_counters_exported_via") != "/metrics":
        fail("ai-counters-not-on-metrics-endpoint")
    if d.get("alert_fraction_key") != "cost.metrics_alert_fraction":
        fail("alert-fraction-key-renamed")
    if d.get("alert_fraction_initial_value_in_spec") != 0.8:
        fail("alert-fraction-initial-value-not-0-8")
    if d.get("l4_declares_alert_rule") is not False:
        fail("l4-declares-an-alert-rule-that-is-l5s")

    if d.get("scrape_interval_declared_by_l4") is not False:
        fail("l4-declares-a-scrape-interval-it-must-not-invent")
    p = col["collectors"]["prometheus"]
    if p.get("scrape_interval_declared_by_l4") is not False:
        fail("collectors-yaml-and-prometheus-yaml-disagree-on-the-interval-owner")
    if d.get("evidence_authored_by_lane_4") is not False:
        fail("lane-4-claims-authorship-of-assisted-evidence")

    print("INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --prometheus | grep -qx "INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated"' \
  > tools/records/checks/L4-P5-18.sh

bash tools/records/validate-ingest.sh --prometheus
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --prometheus` | `INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated` |
| 2 | Exactly the three endpoints, in spec order | `"$L4_PY" -c "import yaml;print(','.join(e['path'] for e in yaml.safe_load(open('metrics/ingest/prometheus.yaml'))['endpoints']))"` | `/health,/version,/metrics` |
| 3 | The `Provides` strings are the spec's, character-for-character | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/prometheus.yaml'));import io;bad=[e['path'] for e in d['endpoints'] if e['provides'] not in io.open('$SPEC',encoding='utf-8').read()];print(bad or 'ALL-VERBATIM')"` | `ALL-VERBATIM` |
| 4 | The declared posture is private-authenticated | `"$L4_PY" -c "import yaml;print(yaml.safe_load(open('metrics/ingest/prometheus.yaml'))['telemetry_exposure_posture'])"` | `private-authenticated` |
| 5 | The private path is declared to carry none of the three | `"$L4_PY" -c "import yaml;print(sorted(yaml.safe_load(open('metrics/ingest/prometheus.yaml'))['private_path_carries_none_of']))"` | `['deploy_key', 'environment_access', 'production_credential']` |
| 6 | No URL, host, port or interval anywhere in the file | `grep -ci "http\|:9090\|hostname\|ip_address\|scrape_interval_seconds" metrics/ingest/prometheus.yaml` | `0` |
| 7 | Five exempt profiles, and the §15.7 equivalent evidence named | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/prometheus.yaml'));print(len(d['exempt_conformance_profiles']),d['exempt_equivalent_evidence_section'])"` | `5 15.7` |
| 8 | The check **can fail** — `public` is rejected | `cp metrics/ingest/prometheus.yaml /tmp/pr.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/prometheus.yaml';d=yaml.safe_load(open(p));d['telemetry_exposure_posture']='public';yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --prometheus; echo "exit=$?"; cp /tmp/pr.bak metrics/ingest/prometheus.yaml` | `INGEST FAIL prometheus posture-not-private-authenticated` then `exit=1` |
| 9 | The check **fails closed** when its input is gone | `mv metrics/ingest/prometheus.yaml /tmp/pr2.bak; bash tools/records/validate-ingest.sh --prometheus; echo "exit=$?"; mv /tmp/pr2.bak metrics/ingest/prometheus.yaml` | `INGEST ERROR prometheus-unreadable:FileNotFoundError` then `exit=3` |
| 10 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-18; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-18 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-19` if:

- Criterion 3 prints anything but `ALL-VERBATIM` → a `provides` string was paraphrased. Retype it from §7.8; do not adjust the criterion. Blocker if it still fails.
- Any step asks you for a scrape interval, a hostname, a port, a URL or an alert rule → every one of those is `ops-vm/**` and L5's. Blocker.
- Criterion 8 exits `0` → the file would accept `public` silently, which line 3726 forbids. Blocker.
- A product name or a product count is needed anywhere in this task. It is not: this file is estate-wide and per-product facts belong to the ASSISTED evidence of `L4-P5-19`. Blocker if you think otherwise.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/prometheus.yaml tools/records/ingest/prometheus.py tools/records/checks/L4-P5-18.sh
git commit -m "L4-P5-18: Prometheus scrape declaration - the three section 41.2 endpoints"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-prometheus
gh pr create --base integration --title "L4-P5-18: Prometheus scrape declaration" \
  --body "Lane 4, Phase 5. Task L4-P5-18. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-19` — **ASSISTED** — private-path scrape reachability evidence

**Mode ASSISTED** · **Size** S · **Depends on** `L4-P5-18` · **Spec** §41.2 line 3726; §19.2 line 1892
**Writes** `metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md`, `metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml`, `tools/records/checks/L4-P5-19.sh`
**Does NOT write** `metrics/ingest/evidence/scrape-reachability-evidence.yaml`.

> **ASSISTED — read this before typing anything.** §19.2 line 1892 makes launch readiness require *"`/metrics` verified unreachable from the public internet unless a recorded Founder decision declares it `public`"*. Verifying that needs a session on the operations VM and the per-product scrape credential (§41.2 line 3726). You must not hold either. **You produce the request document and the evidence template, open the handoff issue, and stop.** You do not `curl` a product endpoint — not from the private path, and above all not from the public internet.

The template records a **host role**, never a hostname or an address, and carries `credentials_present: false` for the same reason `L4-P5-18` forbids a URL in its declaration.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-scrape-reachability-request

mkdir -p metrics/ingest/requests metrics/ingest/evidence

cat > metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md <<'EOF'
# ASSISTED request L4-P5-19 - private-path scrape reachability

Requested of: the L0 human lead, or a delegate holding operations-VM access and the
per-product scrape credential.
Requested by: Lane 4, Phase 5, task L4-P5-19. Prepared by the lane executor, who holds
no scrape credential and issued no request to any product endpoint.

## Why this request exists

Master Spec section 41.2 line 3726: "The three endpoints are not a public surface. ...
the estate's declared posture is private-authenticated: the endpoints are reachable only
over the private path from the operations VM, with a per-product scrape credential ...
public remains available and is a recorded Founder decision, never a default inherited
from a framework."

Section 19.2 line 1892 makes it a launch-readiness row: "observability.telemetry_exposure
declared, and /metrics verified unreachable from the public internet unless a recorded
Founder decision declares it public (Section 41.2)."

metrics/ingest/prometheus.yaml declares the posture. It cannot prove it. This request is
the proof, and only a human with operations-VM access can produce it.

## What is being asked, per product

For every product whose declared conformance_profile is "service" or "white-label"
(spec line 3719) - and for no other product, because line 3719 says a product with a
different shape "is never failed for lacking an endpoint its shape cannot serve":

1. GET /health answers over the private path from the operations VM, with the
   per-product scrape credential
2. GET /version answers over the private path, same conditions
3. GET /metrics answers over the private path, same conditions
4. GET /metrics is NOT reachable from the public internet - unless a recorded Founder
   decision declares this product's telemetry_exposure "public", in which case name the
   decision record instead of asserting unreachability
5. observability.telemetry_exposure is declared for the product (line 1892)

Answer each with: yes | no | founder-decision-public

## How to answer

Copy metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml to
metrics/ingest/evidence/scrape-reachability-evidence.yaml, duplicate the product block
once per in-scope product, and fill every PENDING-HUMAN field. Commit it.

## What must NOT go in the evidence file

No hostname, no IP address, no URL, no port, no credential, no token. Record the host
ROLE ("operations VM") and the outcome. The private path "carries the operations VM no
production credential, no deploy key and no environment access" (line 3726), and the
evidence of that path must not become the place those things get written down.

## What the lane executor did NOT do

- did not issue any request to any product endpoint, private or public
- did not hold or transcribe a scrape credential
- did not author metrics/ingest/evidence/scrape-reachability-evidence.yaml
EOF

cat > metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml <<'EOF'
# TEMPLATE - copy to scrape-reachability-evidence.yaml and fill in. Do not edit in place.
# Authored by the human who ran the session. NEVER by lane 4.
# No hostname, IP address, URL, port or credential in this file - see the request document.
# Duplicate the block under "products" once per in-scope product (conformance_profile
# service or white-label, spec line 3719). Answer each field: yes | no | founder-decision-public
schema: metrics/ingest/scrape-reachability-evidence.v1
request: metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md
authored_by: PENDING-HUMAN
authored_at: PENDING-HUMAN
observed_from_host_role: PENDING-HUMAN
credentials_present: false

products:
  - product: PENDING-HUMAN
    health_answers_over_private_path: PENDING-HUMAN
    version_answers_over_private_path: PENDING-HUMAN
    metrics_answers_over_private_path: PENDING-HUMAN
    metrics_unreachable_from_public_internet: PENDING-HUMAN
    telemetry_exposure_declared: PENDING-HUMAN
    founder_decision_record: PENDING-HUMAN
EOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'test -f metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md' \
  'test -f metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml' \
  '[ "$(grep -c PENDING-HUMAN metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml || true)" = "10" ]' \
  '[ "$(grep -ci "http\|[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*" metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml || true)" = "0" ]' \
  'bash tools/records/validate-ingest.sh --prometheus | grep -q "INGEST OK prometheus"' \
  > tools/records/checks/L4-P5-19.sh

bash tools/records/check.sh L4-P5-19; echo "exit=$?"
```

Then open the handoff issue. This is the last command of the task:

```bash
set -euo pipefail
gh issue create --repo "${CP_SLUG}" --title "ASSISTED L4-P5-19: private-path scrape reachability evidence" --label assisted,lane-4 --body "$(cat <<'EOF'
assisted_task: L4-P5-19
lane: 4
phase: 5
mode: ASSISTED
branch: lane/4/05-scrape-reachability-request
repo: control-plane
needs_from_human: a session on the operations VM and the per-product scrape credential
why_a_lane_executor_cannot_do_it: the credential must not be held by a lane executor, and no lane may probe a product endpoint from the public internet
request_document: metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md
evidence_template: metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml
evidence_file_to_create: metrics/ingest/evidence/scrape-reachability-evidence.yaml
scope: "every product whose conformance_profile is service or white-label (spec line 3719); no other product"
spec_anchor: "41.2 line 3726; 19.2 line 1892"
blocks: "the launch-readiness row at line 1892 for each product. Blocks nothing inside lane 4 phase 5."
must_not_contain: "hostname, IP address, URL, port, credential"
what_the_executor_did: "wrote the request document, the evidence template and the task check; opened this issue; stopped"
what_the_executor_did_NOT_do: "issued no request to any endpoint, held no credential, authored no evidence file"
EOF
)"
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The request document exists | `test -f metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md && echo OK` | `OK` |
| 2 | The template is unfilled — ten fields awaiting a human | `grep -c "PENDING-HUMAN" metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml` | `10` |
| 3 | No address, URL or host in the template | `grep -ci "http\|[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*" metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml` | `0` |
| 4 | The real evidence file was **not** created by the lane | `test -f metrics/ingest/evidence/scrape-reachability-evidence.yaml && echo CREATED \|\| echo NOT-CREATED` | `NOT-CREATED` |
| 5 | The template asks the four §41.2/§19.2 questions plus the exposure declaration | `grep -c "_over_private_path\|_unreachable_from_public_internet\|telemetry_exposure_declared" metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml` | `5` |
| 6 | The Prometheus limb still passes | `bash tools/records/validate-ingest.sh --prometheus` | `INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated` |
| 7 | The handoff issue is open | `gh issue list --repo "${CP_SLUG}" --label assisted --search "L4-P5-19" --json number \| grep -c number` | `1` |
| 8 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-19; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-19 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-20` if:

- Any step would have you `curl`, `wget` or otherwise request a product endpoint. **Probing a product endpoint from the public internet is never a lane action.** Blocker.
- You are asked for the product list, a hostname or a scrape credential. None of those belongs in this task. Blocker.
- Criterion 4 prints `CREATED`. Delete the file, commit nothing, file the blocker.
- `gh issue create` fails. Blocker — the handoff did not reach a human.

**Once the handoff issue is open, this task is complete for you.** Take `L4-P5-20`.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/requests/L4-P5-19-scrape-reachability-request.md metrics/ingest/evidence/scrape-reachability-evidence.TEMPLATE.yaml tools/records/checks/L4-P5-19.sh
git commit -m "L4-P5-19: ASSISTED handoff - private-path scrape reachability request and template"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-scrape-reachability-request
gh pr create --base integration --title "L4-P5-19: ASSISTED - scrape reachability request and template" \
  --body "Lane 4, Phase 5. Task L4-P5-19, mode ASSISTED. Request and template only; no endpoint was contacted by the lane."
```

---

### TASK `L4-P5-20` — Scorecard scheduled scan and drop detection

**Mode** LANE · **Size** M · **Depends on** `L4-P5-15` · **Spec** §99.2 line 9196; §94.2 line 8406; §84.4 line 8561; §85.2 line 8395; §92.3 line 8300; §94.6 line 8537; §15.1; §19.2 line 1896; §17.3 line 1771; §30.3 line 2737
**Writes** `metrics/ingest/scorecard.yaml`, `tools/records/ingest/scorecard.py`, `tools/records/checks/L4-P5-20.sh`

Line 9196 asks for *"Scorecard scheduled scan **with drop detection**"*. The scan half is fully specified — nightly, 02:00 (§94.2 line 8406; §84.4 line 8561), producing *"Risk score per product"* (§85.2 line 8395). **The drop half is not**, and this task does not invent it:

- §92.3 line 8300 states the **routing**: *"A Scorecard score drop never sends the Founder to browse raw scores: it arrives either as a decision prompt (where a Founder decision is genuinely required) or as an owned line on the Reliability dimension, naming the product, the drop and the owner already acting on it."* §94.6 line 8537 places it in the Monday 09:45 slot on the same terms. Both are transcribed.
- The **magnitude** of a drop: D-L4-P5-02 decided `any_decrease` (any strictly negative delta). Two conditions are declared, `decrease` and `below_minimum`, and the routing threshold is `any_decrease`.
- The **record store** a Scorecard result lands in is nowhere stated — see **DECISION REQUIRED D-L4-P5-01**. `source_store` is written as `PENDING-D-L4-P5-01`.

`security.scorecard_minimum` is a **product-contract field** (§15.1, initial value `7.0`) owned by L1. This file names the key and never a value. And because Scorecard behaviour against private repositories is an unverified capability assumption (§30.3 line 2737, confirmed in `L4-P5-21`), the whole collector ships `unarmed — not yet instrumented`.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-scorecard

cat > metrics/ingest/scorecard.yaml <<'EOF'
# Scorecard scheduled scan with drop detection - Master Spec 99.2 line 9196.
# The scan is specified; the drop magnitude is not. See DECISION REQUIRED
# D-L4-P5-01 and D-L4-P5-02 in L4-05-pipeline-and-boards.md section 6.
schema: metrics/ingest/scorecard.v1
collector: scorecard
cadence: nightly
window_start_utc: "02:00"              # 94.2 line 8406 "Scorecard full scan"
cadence_anchor_2: "84.4 line 8561 - Scorecard | Nightly | Risk score per product | Free"
produces: "Risk score per product"     # 85.2 line 8395
produces_spec_line: 8395

# Metric source discipline. Invariant 46 line 9513: metrics derive from the canonical
# record stores of Section 97. No Section 97.2 store carries a Scorecard result, and no
# Section 52.2 signal row names Scorecard as its Source. D-L4-P5-01 is open.
source_kind: collector
source_store: PENDING-D-L4-P5-01
is_source_of_truth: false

# Drop detection. Two separately named conditions, each a literal reading of a cited
# line. Neither carries a magnitude: the spec states none.
drop_conditions:
  - name: decrease
    definition: "any strictly negative delta in the product's score against the previous recorded scan for that product"
    spec_line: 8300
  - name: below_minimum
    definition: "the new score is below that product's declared security.scorecard_minimum"
    spec_line: 1896
routing_threshold: any_decrease

# Routing, 92.3 line 8300, reinforced at 94.6 line 8537. Transcribed, not designed.
routing:
  never: browse_raw_scores
  arrives_as: [decision_prompt, owned_line_on_reliability_dimension]
  line_names: [product, drop, owner_already_acting]
  spec_line: 8300
  rhythm_slot_spec_line: 8537

# The floor is a product-contract field owned by L1 (PARTITION.md line 17).
# L4 names the key. L4 never writes a value, here or anywhere.
floor_key: security.scorecard_minimum
floor_example_spec_line: 1424
floor_value_declared_by_l4: false
floor_owner: "product contract, schemas/product/** (L1)"
launch_readiness_row_spec_line: 1896
lifecycle_expectation_spec_line: 1771

# 30.3 line 2737: "Scorecard behaviour against private repositories" is an unverified
# capability assumption. Confirmation is task L4-P5-21, mode ASSISTED.
private_repo_behaviour_confirmed: false
private_repo_assumption_spec_line: 2737
baseline_scan_phase: "98 Phase 2, line 9029 - Scorecard baseline scan across all products"
evidence_file: metrics/ingest/evidence/scorecard-behaviour-evidence.yaml
evidence_authored_by_lane_4: false

# D77, 52.2 line 4524. Frozen string - L4-05-pipeline-and-boards.md 7.10.
arming_state: "unarmed — not yet instrumented"
never_renders_as: [miss, zero, amber, missing-data]

installed_by_lane: L5
installed_at_path: "ops-vm/**"
EOF

cat > tools/records/ingest/scorecard.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --scorecard limb. Master Spec 99.2 line 9196; 92.3 line 8300."""
import sys
import yaml

PATH = "metrics/ingest/scorecard.yaml"
CONDITIONS = ["below_minimum", "decrease"]
ARRIVES = ["decision_prompt", "owned_line_on_reliability_dimension"]
UNARMED = "unarmed — not yet instrumented"   # 52.2 line 4524


def fail(msg):
    print("INGEST FAIL scorecard %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open(PATH, encoding="utf-8"))
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml",
                                  encoding="utf-8"))["collectors"]["scorecard"]
    except Exception as e:
        print("INGEST ERROR scorecard-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    if d.get("cadence") != col.get("cadence"):
        fail("cadence-diverges-from-collectors-yaml")
    if d.get("window_start_utc") != col.get("window_start_utc"):
        fail("scan-window-diverges-from-collectors-yaml")
    if d.get("produces") != "Risk score per product":
        fail("produces-not-the-line-8395-string")

    if d.get("source_kind") != "collector":
        fail("scorecard-claimed-as-record-store")
    if d.get("is_source_of_truth") is not False:
        fail("collector-claimed-as-source-of-truth")
    if d.get("source_store") != "PENDING-D-L4-P5-01":
        fail("source-store-bound-without-L0")

    cond = d.get("drop_conditions") or []
    if sorted(c.get("name") for c in cond) != CONDITIONS:
        fail("drop-conditions-not-decrease-and-below-minimum")
    for c in cond:
        if not c.get("definition") or not c.get("spec_line"):
            fail("drop-condition-without-definition-or-anchor:%s" % c.get("name"))
    if not d.get("routing_threshold") or d.get("routing_threshold").startswith("PENDING"):
        fail("routing-threshold-not-answered")

    r = d.get("routing") or {}
    if r.get("never") != "browse_raw_scores":
        fail("raw-score-browsing-not-forbidden")
    if sorted(r.get("arrives_as") or []) != ARRIVES:
        fail("routing-not-the-two-forms-of-line-8300")
    if sorted(r.get("line_names") or []) != ["drop", "owner_already_acting", "product"]:
        fail("owned-line-does-not-name-product-drop-and-owner")

    if d.get("floor_key") != "security.scorecard_minimum":
        fail("floor-key-renamed")
    if d.get("floor_value_declared_by_l4") is not False:
        fail("l4-declares-a-scorecard-minimum-that-is-l1s")

    if d.get("private_repo_behaviour_confirmed") is not False:
        fail("private-repo-behaviour-confirmed-without-assisted-evidence")
    if d.get("evidence_authored_by_lane_4") is not False:
        fail("lane-4-claims-authorship-of-assisted-evidence")
    if d.get("arming_state") != UNARMED:
        fail("arming-string-not-frozen-vocabulary")

    print("INGEST OK scorecard conditions=2 pending=2 arming=unarmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --scorecard | grep -qx "INGEST OK scorecard conditions=2 pending=2 arming=unarmed"' \
  > tools/records/checks/L4-P5-20.sh

bash tools/records/validate-ingest.sh --scorecard
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --scorecard` | `INGEST OK scorecard conditions=2 pending=2 arming=unarmed` |
| 2 | Nightly at 02:00, producing the §85.2 string | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/scorecard.yaml'));print(d['cadence'],d['window_start_utc'],d['produces'])"` | `nightly 02:00 Risk score per product` |
| 3 | Exactly the two drop conditions | `"$L4_PY" -c "import yaml;print(sorted(c['name'] for c in yaml.safe_load(open('metrics/ingest/scorecard.yaml'))['drop_conditions']))"` | `['below_minimum', 'decrease']` |
| 4 | Source store placeholder; routing threshold answered | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/scorecard.yaml'));print(d['source_store'],d['routing_threshold'])"` | `PENDING-D-L4-P5-01 any_decrease` |
| 5 | Raw-score browsing is forbidden; both arrival forms declared | `"$L4_PY" -c "import yaml;r=yaml.safe_load(open('metrics/ingest/scorecard.yaml'))['routing'];print(r['never'],len(r['arrives_as']))"` | `browse_raw_scores 2` |
| 6 | L4 declares **no** score, minimum or threshold number | `grep -c "^[a-z_]*\(minimum\|score\|threshold\): *[0-9]" metrics/ingest/scorecard.yaml` | `0` |
| 7 | The collector is unarmed, by the frozen string (code-point check) | `"$L4_PY" -c "import yaml;s=yaml.safe_load(open('metrics/ingest/scorecard.yaml'))['arming_state'];print(len(s),ord(s[8])==8212,s.endswith('not yet instrumented'))"` | `30 True True` |
| 8 | The check **can fail** — one condition removed is rejected | `cp metrics/ingest/scorecard.yaml /tmp/sc.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/scorecard.yaml';d=yaml.safe_load(open(p));d['drop_conditions']=[d['drop_conditions'][0]];yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --scorecard; echo "exit=$?"; cp /tmp/sc.bak metrics/ingest/scorecard.yaml` | `INGEST FAIL scorecard drop-conditions-not-decrease-and-below-minimum` then `exit=1` |
| 9 | The check **fails closed** when its input is gone | `mv metrics/ingest/scorecard.yaml /tmp/sc2.bak; bash tools/records/validate-ingest.sh --scorecard; echo "exit=$?"; mv /tmp/sc2.bak metrics/ingest/scorecard.yaml` | `INGEST ERROR scorecard-unreadable:FileNotFoundError` then `exit=3` |
| 10 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-20; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-20 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-21` if:

- Any step would have you choose a drop magnitude, a window, or a routing threshold. **That is D-L4-P5-02 and it belongs to L0.** Blocker.
- Any step would have you bind `source_store` to a `records/` path. **That is D-L4-P5-01 and it belongs to L0.** Do not route a Scorecard result into an existing store because it resembles one. Blocker.
- Any step would have you write a number for `security.scorecard_minimum`. That field is L1's (`PARTITION.md` line 17). Blocker.
- Criterion 8 exits `0`. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/scorecard.yaml tools/records/ingest/scorecard.py tools/records/checks/L4-P5-20.sh
git commit -m "L4-P5-20: Scorecard scheduled scan and drop detection"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-scorecard
gh pr create --base integration --title "L4-P5-20: Scorecard scan and drop detection" \
  --body "Lane 4, Phase 5. Task L4-P5-20. Acceptance command in L4-05-pipeline-and-boards.md passed. Two L0 decisions remain open as declared placeholders."
```

---

### TASK `L4-P5-21` — **ASSISTED** — Scorecard private-repository behaviour and baseline scan

**Mode ASSISTED** · **Size** S · **Depends on** `L4-P5-20` · **Spec** §30.3 line 2737; §98 Phase 2 line 9029; §98 completion check line 9035
**Writes** `metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md`, `metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml`, `tools/records/checks/L4-P5-21.sh`
**Does NOT write** `metrics/ingest/evidence/scorecard-behaviour-evidence.yaml`.

> **ASSISTED — read this before typing anything.** §30.3 line 2737 lists *"Scorecard behaviour against private repositories"* as an unverified capability assumption. Confirming it, and running the Phase 2 baseline scan across all products (§98 line 9029), needs a GitHub organisation-owner session. You must not hold one. **You produce the request document and the evidence template, open the handoff issue, and stop.**

Until the evidence returns, `metrics/ingest/scorecard.yaml` keeps `private_repo_behaviour_confirmed: false` and the collector stays `unarmed — not yet instrumented`. The completion check of §98 Phase 2 (line 9035) — *"every product visible in Grafana with a Scorecard score"* — is not this lane's to close: Grafana is subsystem H, unassigned (**D-L4-P5-03**).

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-scorecard-behaviour-request

mkdir -p metrics/ingest/requests metrics/ingest/evidence

cat > metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md <<'EOF'
# ASSISTED request L4-P5-21 - Scorecard behaviour against private repositories

Requested of: the L0 human lead, or a delegate holding a GitHub organisation-owner session.
Requested by: Lane 4, Phase 5, task L4-P5-21. Prepared by the lane executor, who holds no
organisation-owner session and ran no scan.

## Why this request exists

Master Spec section 30.3 line 2737 lists, among the unverified capability assumptions
"each confirmed before the phase depending on it": "Scorecard behaviour against private
repositories".

Section 98 Phase 2, line 9029: "Scorecard baseline scan across all products".

Every repository in this estate is private. If Scorecard does not produce a usable score
against a private repository, then the launch-readiness row at section 19.2 line 1896
("Scorecard at or above the declared minimum; no unresolved high findings"), the risk
score of section 85.2 line 8395, and the drop detection of section 92.3 line 8300 all
have no source - and metrics/ingest/scorecard.yaml must stay unarmed rather than render
a zero that reads like a healthy score.

## What is being asked

1. Does Scorecard run against a private repository in this organisation, and does it
   return a score? yes | no | partial-with-note
2. Which checks, if any, are unavailable or degraded against a private repository?
3. Was the Phase 2 baseline scan run across all products (spec line 9029)?
4. On what date, and against how many products? (count only - no product list is needed
   in this file)
5. If the answer to 1 is no or partial: what is the recorded fallback, and is it an
   accepted risk with a named holder and a review date?

## How to answer

Copy metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml to
metrics/ingest/evidence/scorecard-behaviour-evidence.yaml, fill every PENDING-HUMAN
field, and commit it. Then, and only then, set private_repo_behaviour_confirmed in
metrics/ingest/scorecard.yaml and move arming_state off "unarmed - not yet instrumented".

## What the lane executor did NOT do

- did not open a GitHub organisation-owner session
- did not run a Scorecard scan against any repository
- did not author metrics/ingest/evidence/scorecard-behaviour-evidence.yaml
- did not change private_repo_behaviour_confirmed or arming_state

## Not asked here, deliberately

"Every product visible in Grafana with a Scorecard score" (the Phase 2 completion check,
line 9035) is a subsystem H surface. Subsystem H is unassigned in PARTITION v1
(D-L4-P5-03). Lane 4 opens no Grafana file.
EOF

cat > metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml <<'EOF'
# TEMPLATE - copy to scorecard-behaviour-evidence.yaml and fill in. Do not edit in place.
# Authored by the human who ran the session. NEVER by lane 4:
# tools/records/ingest/scorecard.py keeps the collector unarmed until this file exists
# and private_repo_behaviour_confirmed is set by a human.
# No credential, token or organisation-owner detail in this file.
schema: metrics/ingest/scorecard-behaviour-evidence.v1
request: metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md
authored_by: PENDING-HUMAN
authored_at: PENDING-HUMAN
runs_against_private_repository: PENDING-HUMAN     # yes | no | partial-with-note
degraded_or_unavailable_checks: PENDING-HUMAN
baseline_scan_run: PENDING-HUMAN                   # spec line 9029
baseline_scan_date: PENDING-HUMAN
baseline_scan_product_count: PENDING-HUMAN
fallback_if_unsupported: PENDING-HUMAN
accepted_risk_holder: PENDING-HUMAN
accepted_risk_review_date: PENDING-HUMAN
credentials_present: false
EOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'test -f metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md' \
  'test -f metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml' \
  '[ "$(grep -c PENDING-HUMAN metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml || true)" = "10" ]' \
  'bash tools/records/validate-ingest.sh --scorecard | grep -q "arming=unarmed"' \
  > tools/records/checks/L4-P5-21.sh

bash tools/records/check.sh L4-P5-21; echo "exit=$?"
```

Then open the handoff issue. This is the last command of the task:

```bash
set -euo pipefail
gh issue create --repo "${CP_SLUG}" --title "ASSISTED L4-P5-21: Scorecard private-repository behaviour and baseline scan" --label assisted,lane-4 --body "$(cat <<'EOF'
assisted_task: L4-P5-21
lane: 4
phase: 5
mode: ASSISTED
branch: lane/4/05-scorecard-behaviour-request
repo: control-plane
needs_from_human: a GitHub organisation-owner session
why_a_lane_executor_cannot_do_it: an organisation-owner session must not be held by a lane executor
request_document: metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md
evidence_template: metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml
evidence_file_to_create: metrics/ingest/evidence/scorecard-behaviour-evidence.yaml
spec_anchor: "30.3 line 2737; 98 Phase 2 line 9029; 98 completion check line 9035"
blocks: "arming of the Scorecard collector. Blocks nothing inside lane 4 phase 5."
state_until_answered: "private_repo_behaviour_confirmed false; collector renders unarmed - not yet instrumented (D77, line 4524)"
also_open: "D-L4-P5-01 (no Section 97 record store for a Scorecard result) and D-L4-P5-02 (no declared drop magnitude) - both for L0, both unaffected by this evidence"
what_the_executor_did: "wrote the request document, the evidence template and the task check; opened this issue; stopped"
what_the_executor_did_NOT_do: "ran no scan, held no organisation session, authored no evidence file, changed no arming state"
EOF
)"
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The request document exists | `test -f metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md && echo OK` | `OK` |
| 2 | The template is unfilled — ten fields awaiting a human | `grep -c "PENDING-HUMAN" metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml` | `10` |
| 3 | The real evidence file was **not** created by the lane | `test -f metrics/ingest/evidence/scorecard-behaviour-evidence.yaml && echo CREATED \|\| echo NOT-CREATED` | `NOT-CREATED` |
| 4 | The collector is still unconfirmed and unarmed | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/scorecard.yaml'));print(d['private_repo_behaviour_confirmed'],d['arming_state'].startswith('unarmed'))"` | `False True` |
| 5 | The Scorecard limb still passes | `bash tools/records/validate-ingest.sh --scorecard` | `INGEST OK scorecard conditions=2 pending=2 arming=unarmed` |
| 6 | No Grafana file was touched (subsystem H is unassigned) | `git diff --name-only origin/integration...HEAD \| grep -ci "grafana\|dashboard"` | `0` |
| 7 | The handoff issue is open | `gh issue list --repo "${CP_SLUG}" --label assisted --search "L4-P5-21" --json number \| grep -c number` | `1` |
| 8 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-21; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-21 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-22` if:

- Any step would have you open a GitHub organisation-owner session or run a Scorecard scan. Blocker.
- Any step would have you set `private_repo_behaviour_confirmed` to `true`, or move `arming_state` off the unarmed string. **Only the returned evidence moves it, and only a human writes that evidence.** Blocker.
- Criterion 6 prints anything but `0` → a Grafana or dashboard file was touched. Subsystem H is unassigned (**D-L4-P5-03**) and is not yours. Revert it. Blocker.
- `gh issue create` fails. Blocker.

**Once the handoff issue is open, this task is complete for you.** Take `L4-P5-22`.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/requests/L4-P5-21-scorecard-behaviour-request.md metrics/ingest/evidence/scorecard-behaviour-evidence.TEMPLATE.yaml tools/records/checks/L4-P5-21.sh
git commit -m "L4-P5-21: ASSISTED handoff - Scorecard private-repository behaviour request and template"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-scorecard-behaviour-request
gh pr create --base integration --title "L4-P5-21: ASSISTED - Scorecard behaviour request and template" \
  --body "Lane 4, Phase 5. Task L4-P5-21, mode ASSISTED. Request and template only; no scan was run by the lane."
```

---

### TASK `L4-P5-22` — Metric source discipline: the `source_kind` rule and its validator

**Mode** LANE · **Size** M · **Depends on** `L4-P5-16`, `L4-P5-18`, `L4-P5-20` · **Spec** §101.7 invariant 46 line 9513; §103 preamble line 9776; §52.2 line 4522; §1 line 395; §97.2 table lines 8845–8869
**Writes** `metrics/ingest/source-kinds.yaml`, `tools/records/ingest/source_kind.py`, `tools/records/checks/L4-P5-22.sh`

This is the last clause of the §99.2 subsystem I row — *"metric source discipline"* — and it is the one that keeps the other three honest.

Invariant 46, line 9513, verbatim: *"Derived data is computed, never hand-maintained. Metrics derive from the canonical record stores of Section 97 (Records, Events and Data Conventions), never from hand-maintained numbers."* The §103 preamble, line 9776, restates it; §52.2 line 4522 says of the signal table *"values are derived, never hand-maintained"*; line 395 says *"Derived metrics are never edited by hand."*

**The tension, and its mechanical resolution.** DevLake, Prometheus and Scorecard are collectors. None is a §97.2 canonical record store — that table (lines 8845–8869) lists none of them. Yet §103.1 and §103.2 name DevLake under a column headed *"Source (record store)"* at lines 9782, 9787 and 9794. Rather than argue with the spec, this file **types every source**: `record_store` is the only kind that may be a source of truth; `collector` never is; and any measure whose only source is a collector is declared as such, in writing, where the register of Phase 7 will read it.

The second half is the anti-hand-maintenance rule made checkable: **no file under `metrics/ingest/**` may carry a metric value.** A declaration file with a `count:` or a `score:` in it has become a hand-maintained number, which is exactly what invariant 46 forbids. The validator walks every YAML file in the tree, at every depth, and fails on the forbidden key set.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-source-kinds

cat > metrics/ingest/source-kinds.yaml <<'EOF'
# Metric source discipline - the last clause of the subsystem I row, spec line 9196.
#
# Invariant 46, line 9513: "Derived data is computed, never hand-maintained. Metrics
# derive from the canonical record stores of Section 97 (Records, Events and Data
# Conventions), never from hand-maintained numbers."
# Section 103 preamble, line 9776, restates it. Section 52.2 line 4522: "values are
# derived, never hand-maintained". Line 395: "Derived metrics are never edited by hand."
schema: metrics/ingest/source-kinds.v1
rule_spec_lines: [395, 4522, 9513, 9776]

# Closed pair. A third kind is a spec change, not a configuration change.
kinds:
  record_store:
    definition: "a canonical Section 97.2 record store (table at lines 8845-8869)"
    may_be_a_source_of_truth: true
    path_shape: "records/** in control-plane-records, or a named control-plane register"
  collector:
    definition: "a read-side instrument that reads systems of record it does not own"
    may_be_a_source_of_truth: false
    path_shape: "declared under metrics/ingest/**; installed under ops-vm/** by L5"
closed_set: true

# One entry per collector declared in collectors.yaml. No collector is a record store.
sources:
  devlake:
    kind: collector
    is_source_of_truth: false
    may_be_sole_source_of_a_metric: false
    declaration_file: metrics/ingest/devlake.yaml
    named_as_source_in_spec_at: [4533, 4536, 4537, 4569, 7048, 7052, 7053, 9782, 9787, 9794, 9811, 9954, 9963]
    tension_note: "Sections 103.1 and 103.2 head that column 'Source (record store)' while naming DevLake. DevLake is typed here as a collector; the measures it feeds carry source_kind collector in the Phase 7 register."
    backing_record_store: none-declared-in-spec
  prometheus:
    kind: collector
    is_source_of_truth: false
    may_be_sole_source_of_a_metric: false
    declaration_file: metrics/ingest/prometheus.yaml
    named_as_source_in_spec_at: []
    backing_record_store: none-declared-in-spec
    note: "The Section 103.2 digest row at line 9798 sources '/version versus approval record' - the approval record is the record store, the endpoint is the reading."
  scorecard:
    kind: collector
    is_source_of_truth: false
    may_be_sole_source_of_a_metric: false
    declaration_file: metrics/ingest/scorecard.yaml
    named_as_source_in_spec_at: []
    backing_record_store: PENDING-D-L4-P5-01

# Invariant 46 made mechanical. No file under metrics/ingest/** may carry a metric
# value: a declaration that carries a number has become a hand-maintained number.
# These keys are forbidden at any depth in any YAML file in this directory tree.
forbidden_value_keys: [count, current_value, last_value, latest_value, median, p90, score]

consumed_by:
  - "metrics/register/** - Lane 4 Phase 7, L4-P7-01 and L4-P7-02"
  - "subsystem H rendering - UNASSIGNED in PARTITION v1, see D-L4-P5-03"
EOF

cat > tools/records/ingest/source_kind.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --source-kinds limb. Invariant 46, Master Spec line 9513."""
import os
import sys
import yaml

PATH = "metrics/ingest/source-kinds.yaml"
ROOT = "metrics/ingest"
KINDS = ["collector", "record_store"]


def fail(msg):
    print("INGEST FAIL source-kinds %s" % msg)
    sys.exit(1)


def walk_keys(node, forbidden, hits, where):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in forbidden:
                hits.append("%s:%s" % (where, k))
            walk_keys(v, forbidden, hits, where)
    elif isinstance(node, list):
        for v in node:
            walk_keys(v, forbidden, hits, where)


def main():
    try:
        d = yaml.safe_load(open(PATH, encoding="utf-8"))
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml",
                                  encoding="utf-8"))["collectors"]
    except Exception as e:
        print("INGEST ERROR source-kinds-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    if sorted(d.get("kinds") or {}) != KINDS:
        fail("kinds-not-the-closed-pair")
    if d.get("closed_set") is not True:
        fail("kind-set-not-closed")
    if d["kinds"]["record_store"].get("may_be_a_source_of_truth") is not True:
        fail("record-store-not-a-source-of-truth")
    if d["kinds"]["collector"].get("may_be_a_source_of_truth") is not False:
        fail("collector-declared-a-source-of-truth")
    for line in (9513, 9776):
        if line not in (d.get("rule_spec_lines") or []):
            fail("invariant-46-anchor-missing:%d" % line)

    src = d.get("sources") or {}
    if sorted(src) != sorted(col):
        fail("sources-do-not-match-collectors-yaml")
    for name, s in src.items():
        if s.get("kind") != "collector":
            fail("collector-typed-as-record-store:%s" % name)
        if s.get("is_source_of_truth") is not False:
            fail("collector-claimed-as-source-of-truth:%s" % name)
        if s.get("may_be_sole_source_of_a_metric") is not False:
            fail("collector-claimed-as-sole-source:%s" % name)
        f = s.get("declaration_file") or ""
        if not os.path.isfile(f):
            print("INGEST ERROR source-kinds-declaration-missing:%s" % name)
            sys.exit(3)

    forbidden = set(d.get("forbidden_value_keys") or [])
    if not forbidden:
        fail("forbidden-value-key-set-empty")
    hits = []
    for fn in sorted(os.listdir(ROOT)):
        if not fn.endswith(".yaml"):
            continue
        try:
            doc = yaml.safe_load(open(os.path.join(ROOT, fn), encoding="utf-8"))
        except Exception:
            print("INGEST ERROR source-kinds-unparseable:%s" % fn)
            sys.exit(3)
        if fn != os.path.basename(PATH):
            walk_keys(doc, forbidden, hits, fn)
        k = (doc or {}).get("source_kind")
        if k is not None and k not in KINDS:
            fail("unknown-source-kind:%s:%s" % (fn, k))
    if hits:
        fail("hand-maintained-value-key:" + ",".join(sorted(hits)))

    print("INGEST OK source-kinds kinds=2 collectors=3 forbidden=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --source-kinds | grep -qx "INGEST OK source-kinds kinds=2 collectors=3 forbidden=0"' \
  > tools/records/checks/L4-P5-22.sh

bash tools/records/validate-ingest.sh --source-kinds
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --source-kinds` | `INGEST OK source-kinds kinds=2 collectors=3 forbidden=0` |
| 2 | Exactly two kinds, closed | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/source-kinds.yaml'));print(sorted(d['kinds']),d['closed_set'])"` | `['collector', 'record_store'] True` |
| 3 | No collector is a source of truth | `"$L4_PY" -c "import yaml;s=yaml.safe_load(open('metrics/ingest/source-kinds.yaml'))['sources'];print(sorted({v['is_source_of_truth'] for v in s.values()}))"` | `[False]` |
| 4 | The invariant-46 anchors are declared | `"$L4_PY" -c "import yaml;print(yaml.safe_load(open('metrics/ingest/source-kinds.yaml'))['rule_spec_lines'])"` | `[395, 4522, 9513, 9776]` |
| 5 | The DevLake tension is recorded, not hidden | `"$L4_PY" -c "import yaml;print(len(yaml.safe_load(open('metrics/ingest/source-kinds.yaml'))['sources']['devlake']['named_as_source_in_spec_at']))"` | `13` |
| 6 | Invariant 46 is anchored where it is claimed | `sed -n '9513p' "$SPEC" \| grep -c "never from hand-maintained numbers"` | `1` |
| 7 | The check **can fail** — a hand-maintained value key is rejected | `cp metrics/ingest/scorecard.yaml /tmp/sk.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/scorecard.yaml';d=yaml.safe_load(open(p));d['score']=7.0;yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --source-kinds; echo "exit=$?"; cp /tmp/sk.bak metrics/ingest/scorecard.yaml` | `INGEST FAIL source-kinds hand-maintained-value-key:scorecard.yaml:score` then `exit=1` |
| 8 | The check **fails closed** when a declaration it types is gone | `mv metrics/ingest/devlake.yaml /tmp/dl.bak; bash tools/records/validate-ingest.sh --source-kinds; echo "exit=$?"; mv /tmp/dl.bak metrics/ingest/devlake.yaml` | `INGEST ERROR source-kinds-declaration-missing:devlake` then `exit=3` |
| 9 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-22; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-22 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-23` if:

- Any step would have you type a collector as `record_store` so that a metric can arm. **That is the failure invariant 46 exists to prevent.** Blocker.
- Any step would have you create a `records/scorecard/` directory or add a store under `schemas/records/`. That is **D-L4-P5-01**, it belongs to L0, and the store list is `L4-P2`'s. Blocker.
- Criterion 7 exits `0` → the anti-hand-maintenance rule is decoration. Blocker.
- Criterion 8 exits `0` or `1` instead of `3`. Blocker.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/source-kinds.yaml tools/records/ingest/source_kind.py tools/records/checks/L4-P5-22.sh
git commit -m "L4-P5-22: metric source discipline - the source_kind rule and its validator"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-source-kinds
gh pr create --base integration --title "L4-P5-22: Metric source discipline" \
  --body "Lane 4, Phase 5. Task L4-P5-22. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-23` — Ingest freshness and the three arming strings

**Mode** LANE · **Size** M · **Depends on** `L4-P5-22` · **Spec** §51.2 line 4459; §52.2 line 4524; §101.7 invariant 47 line 9514
**Writes** `metrics/ingest/freshness.yaml`, `tools/records/ingest/freshness.py`, `tools/records/checks/L4-P5-23.sh`

Two jobs, and the second is the most valuable check in the phase.

**One.** §51.2 line 4459 states the only collector freshness SLO in the specification: *"DevLake ingest freshness | Ingest completes at least daily | Age of the newest ingested row | Amber; the signals sourced from DevLake render as armed — source stale (Section 52.2) rather than as within tolerance."* That row is transcribed. **Prometheus and Scorecard have no stated freshness SLO**, so this file declares `none-declared-in-spec` for both and L4 invents neither a bound nor a rendering for them. Inventing one would be designing, which §4 forbids.

**Two.** The frozen arming vocabulary of §7.10 is enforced across the whole tree. Only three strings may appear as an arming value anywhere under `metrics/ingest/**`. A fourth string — however sensible it reads — is a new vocabulary, and a new vocabulary is how an instrument quietly starts saying something the specification never authorised. The validator sweeps every YAML file, at every depth, and fails on any string beginning `armed` or `unarmed` that is not one of the three.

**Retention is not declared here.** Invariant 47 (line 9514) says raw activity telemetry retention classes *"are declared in the control plane and owned by the Founder"*, and the class file is `metrics/retention/retention-classes.yaml`, built by `L4-P3-07` (entry condition E8). This task asserts that file is reachable and declares **no** class of its own.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-ingest-freshness

cat > metrics/ingest/freshness.yaml <<'EOF'
# Ingest freshness and the frozen arming vocabulary.
# Section 51.2 line 4459 is the only collector freshness SLO stated anywhere in the
# specification. L4 declares no bound the spec does not state.
schema: metrics/ingest/freshness.v1

collectors:
  devlake:
    freshness_slo: "Ingest completes at least daily"
    measured_by: "Age of the newest ingested row"
    breach_class: Amber
    stale_rendering: "armed — source stale"
    spec_section: "51.2"
    spec_line: 4459
  prometheus:
    freshness_slo: none-declared-in-spec
    l4_declares_no_slo: true
    note: "38.4 line 3476 refers to 'a scrape interval' and names no value; no freshness SLO for Prometheus exists in the specification."
  scorecard:
    freshness_slo: none-declared-in-spec
    l4_declares_no_slo: true
    note: "94.2 line 8406 and 84.4 line 8561 give the scan cadence, not a freshness bound."

# The only three strings that may appear as an arming value anywhere under
# metrics/ingest/**. See L4-05-pipeline-and-boards.md section 7.10.
arming_vocabulary:
  - value: "unarmed — not yet instrumented"
    meaning: "the declared source is not live"
    spec_line: 4524
  - value: "unarmed — insufficient history"
    meaning: "the source is live but does not yet hold the full lookback window"
    spec_line: 4524
  - value: "armed — source stale"
    meaning: "the source is live and holds the window, but its ingest is past its freshness bound"
    spec_line: 4459
closed_vocabulary: true

# Invariant 47, line 9514: retention classes are declared in the control plane and
# owned by the Founder. The class file is L4-P3-07's. Nothing here declares a class.
retention_class_declared_here: false
retention_declaration_file: metrics/retention/retention-classes.yaml
retention_owner: Founder
retention_invariant_spec_line: 9514
EOF

cat > tools/records/ingest/freshness.py <<'PYEOF'
#!/usr/bin/env python3
"""INGEST --freshness limb. Master Spec 51.2 line 4459; 52.2 line 4524."""
import os
import sys
import yaml

PATH = "metrics/ingest/freshness.yaml"
ROOT = "metrics/ingest"
RETENTION = "metrics/retention/retention-classes.yaml"
FROZEN = {
    "unarmed — not yet instrumented",
    "unarmed — insufficient history",
    "armed — source stale",
}


def fail(msg):
    print("INGEST FAIL freshness %s" % msg)
    sys.exit(1)


def strings(node, out):
    if isinstance(node, dict):
        for v in node.values():
            strings(v, out)
    elif isinstance(node, list):
        for v in node:
            strings(v, out)
    elif isinstance(node, str):
        out.append(node)


def main():
    if not os.path.isfile(RETENTION):
        print("INGEST ERROR retention-classes-unreachable")
        sys.exit(3)
    try:
        d = yaml.safe_load(open(PATH, encoding="utf-8"))
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml",
                                  encoding="utf-8"))["collectors"]
    except Exception as e:
        print("INGEST ERROR freshness-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    c = d.get("collectors") or {}
    if sorted(c) != sorted(col):
        fail("freshness-collectors-do-not-match-collectors-yaml")
    dl = c.get("devlake") or {}
    if dl.get("freshness_slo") != "Ingest completes at least daily":
        fail("devlake-slo-not-the-line-4459-string")
    if dl.get("measured_by") != "Age of the newest ingested row":
        fail("devlake-measure-not-the-line-4459-string")
    if dl.get("breach_class") != "Amber":
        fail("devlake-breach-class-not-amber")
    if dl.get("stale_rendering") != "armed — source stale":
        fail("devlake-stale-rendering-not-frozen-vocabulary")
    if dl.get("spec_line") != 4459:
        fail("devlake-slo-anchor-not-4459")
    for name in ("prometheus", "scorecard"):
        if c[name].get("freshness_slo") != "none-declared-in-spec":
            fail("slo-invented-for-a-collector-the-spec-gives-none:%s" % name)
        if c[name].get("l4_declares_no_slo") is not True:
            fail("l4-claims-an-slo-it-must-not-invent:%s" % name)

    vocab = [v.get("value") for v in (d.get("arming_vocabulary") or [])]
    if set(vocab) != FROZEN or len(vocab) != 3:
        fail("arming-vocabulary-not-the-frozen-three")
    if d.get("closed_vocabulary") is not True:
        fail("arming-vocabulary-not-closed")
    if d.get("retention_class_declared_here") is not False:
        fail("retention-class-declared-outside-its-owner-file")

    bad = []
    for fn in sorted(os.listdir(ROOT)):
        if not fn.endswith(".yaml"):
            continue
        try:
            doc = yaml.safe_load(open(os.path.join(ROOT, fn), encoding="utf-8"))
        except Exception:
            print("INGEST ERROR freshness-unparseable:%s" % fn)
            sys.exit(3)
        vals = []
        strings(doc, vals)
        for s in vals:
            t = s.strip()
            if (t.startswith("armed") or t.startswith("unarmed")) and t not in FROZEN:
                bad.append("%s:%s" % (fn, t[:40]))
    if bad:
        fail("arming-string-outside-frozen-vocabulary:" + ",".join(sorted(bad)))

    print("INGEST OK freshness slo=1 none-declared=2 arming_strings=3 violations=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/validate-ingest.sh --freshness | grep -qx "INGEST OK freshness slo=1 none-declared=2 arming_strings=3 violations=0"' \
  > tools/records/checks/L4-P5-23.sh

bash tools/records/validate-ingest.sh --freshness
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The limb passes with the frozen counters | `bash tools/records/validate-ingest.sh --freshness` | `INGEST OK freshness slo=1 none-declared=2 arming_strings=3 violations=0` |
| 2 | The DevLake SLO row is the spec's, word for word | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/freshness.yaml'))['collectors']['devlake'];print(d['freshness_slo'],'/',d['measured_by'],'/',d['breach_class'])"` | `Ingest completes at least daily / Age of the newest ingested row / Amber` |
| 3 | That row really is at line 4459 | `sed -n '4459p' "$SPEC" \| grep -c "DevLake ingest freshness"` | `1` |
| 4 | Two collectors carry no invented SLO | `"$L4_PY" -c "import yaml;c=yaml.safe_load(open('metrics/ingest/freshness.yaml'))['collectors'];print(c['prometheus']['freshness_slo'],c['scorecard']['freshness_slo'])"` | `none-declared-in-spec none-declared-in-spec` |
| 5 | The arming vocabulary is exactly three, and closed | `"$L4_PY" -c "import yaml;d=yaml.safe_load(open('metrics/ingest/freshness.yaml'));print(len(d['arming_vocabulary']),d['closed_vocabulary'])"` | `3 True` |
| 6 | No retention class is declared here | `grep -c "^retention_class_declared_here: false" metrics/ingest/freshness.yaml` | `1` |
| 7 | The check **can fail** — a fourth arming string anywhere is rejected | `cp metrics/ingest/scorecard.yaml /tmp/fr.bak && "$L4_PY" -c "import yaml;p='metrics/ingest/scorecard.yaml';d=yaml.safe_load(open(p));d['arming_state']='armed - probably fine';yaml.safe_dump(d,open(p,'w'))" && bash tools/records/validate-ingest.sh --freshness; echo "exit=$?"; cp /tmp/fr.bak metrics/ingest/scorecard.yaml` | `INGEST FAIL freshness arming-string-outside-frozen-vocabulary:scorecard.yaml:armed - probably fine` then `exit=1` |
| 8 | The check **fails closed** when the retention file is unreachable | `mv metrics/retention/retention-classes.yaml /tmp/rc.bak; bash tools/records/validate-ingest.sh --freshness; echo "exit=$?"; mv /tmp/rc.bak metrics/retention/retention-classes.yaml` | `INGEST ERROR retention-classes-unreachable` then `exit=3` |
| 9 | Nothing outside the owned paths | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-23; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-23 PASS
exit=0
```

#### STOP RULE

Do not proceed to `L4-P5-24` if:

- Any step would have you write a freshness bound for Prometheus or Scorecard. **The specification states none, and this file states that it states none.** Blocker.
- Any step would have you add a fourth arming string, or reword one of the three. The three are transcribed at §7.10. Blocker.
- Criterion 7 exits `0` → a fourth vocabulary passes and the arming discipline is decoration. Blocker.
- Criterion 8 exits `0` or `1` instead of `3` → the limb passes without its cross-file input. Blocker.
- `metrics/retention/retention-classes.yaml` is missing on `integration` → entry condition E8 has not merged. **Do not create it**; it is `L4-P3-07`'s. Blocker naming E8.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/ingest/freshness.yaml tools/records/ingest/freshness.py tools/records/checks/L4-P5-23.sh
git commit -m "L4-P5-23: ingest freshness and the three arming strings"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-ingest-freshness
gh pr create --base integration --title "L4-P5-23: Ingest freshness and arming vocabulary" \
  --body "Lane 4, Phase 5. Task L4-P5-23. Acceptance command in L4-05-pipeline-and-boards.md passed."
```

---

### TASK `L4-P5-24` — Phase sweep, rebase, PR

**Mode** LANE · **Size** S · **Depends on** `L4-P5-01`…`L4-P5-04`, `L4-P5-14`…`L4-P5-23` · **Spec** — none new; this task adds no declaration
**Writes** `tools/records/sweep-phase5.sh`, `tools/records/checks/L4-P5-24.sh`

The sweep runs both dispatchers and every task check this file owns, in one command, and prints one line. It adds no new rule: a sweep that can invent a pass is worse than no sweep.

**This is not the P5 exit gate.** `L4-06-tasks.md` §5 defines gate P5 as `bash tools/records/validate-boards.sh && bash tools/records/test-rqm-detector.sh` with the final line `RQM OK 6/6`. The Ready-queue-miss detector (`L4-P5-05`…`L4-P5-13`) is not in this file, so **this sweep cannot close the phase.** It proves the ingest-and-boards half is whole; gate P5 stays owned by `L4-06-tasks.md`, and it passes only when the detector lands too.

#### Commands

**Commands**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/05-phase-sweep

cat > tools/records/sweep-phase5.sh <<'SHEOF'
#!/usr/bin/env bash
# Phase 5 sweep for the tasks of L4-05-pipeline-and-boards.md.
# NOT the P5 exit gate: that is in L4-06-tasks.md section 5 and additionally
# requires tools/records/test-rqm-detector.sh (L4-P5-05..L4-P5-13).
# Output contract: L4-06-tasks.md section 0.5.
set -u
cd "$(dirname "$0")/../.."
IDS="L4-P5-01 L4-P5-02 L4-P5-03 L4-P5-04 L4-P5-14 L4-P5-15 L4-P5-16 L4-P5-17 L4-P5-18 L4-P5-19 L4-P5-20 L4-P5-21 L4-P5-22 L4-P5-23"
PENDING="PENDING-D-L4-P5-01 UNASSIGNED-D-L4-P5-03"

for f in tools/records/validate-boards.sh tools/records/validate-ingest.sh; do
  [ -x "$f" ] || { echo "PHASE5 ERROR missing-dispatcher"; exit 3; }
done

bash tools/records/validate-boards.sh | grep -q "^BOARDS OK" || { echo "PHASE5 FAIL boards"; exit 1; }
bash tools/records/validate-ingest.sh | grep -qx "INGEST OK limbs=6" || { echo "PHASE5 FAIL ingest"; exit 1; }

n=0
for id in $IDS; do
  [ -f "tools/records/checks/${id}.sh" ] || { echo "PHASE5 ERROR missing-check:${id}"; exit 3; }
  bash tools/records/check.sh "$id" | grep -qx "CHECK ${id} PASS" || { echo "PHASE5 FAIL check:${id}"; exit 1; }
  n=$((n+1))
done

p=0
for tok in $PENDING; do
  grep -rq -- "$tok" metrics/ || { echo "PHASE5 FAIL placeholder-missing:${tok}"; exit 1; }
  p=$((p+1))
done

bash tools/records/lane-selfcheck.sh --paths | grep -q "PATHS OK" || { echo "PHASE5 FAIL paths"; exit 1; }

echo "PHASE5 OK boards=1 ingest=6 checks=${n} pending=${p}"
SHEOF
chmod +x tools/records/sweep-phase5.sh

printf '%s\n' '#!/usr/bin/env bash' 'set -eu' 'cd "$(dirname "$0")/../../.."' \
  'bash tools/records/sweep-phase5.sh | grep -qx "PHASE5 OK boards=1 ingest=6 checks=14 pending=2"' \
  > tools/records/checks/L4-P5-24.sh

bash tools/records/sweep-phase5.sh
```

#### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The sweep passes with the frozen counters | `bash tools/records/sweep-phase5.sh` | `PHASE5 OK boards=1 ingest=6 checks=14 pending=2` |
| 2 | Both dispatchers pass on their own | `bash tools/records/validate-ingest.sh` | `INGEST OK limbs=6` |
| 3 | Every one of the fourteen checks passes | `for id in L4-P5-01 L4-P5-02 L4-P5-03 L4-P5-04 L4-P5-14 L4-P5-15 L4-P5-16 L4-P5-17 L4-P5-18 L4-P5-19 L4-P5-20 L4-P5-21 L4-P5-22 L4-P5-23; do bash tools/records/check.sh $id; done \| grep -c PASS` | `14` |
| 4 | Both remaining placeholders are still unanswered | `for t in PENDING-D-L4-P5-01 UNASSIGNED-D-L4-P5-03; do grep -rq -- "$t" metrics/ && echo "$t"; done \| wc -l \| tr -d ' '` | `2` |
| 5 | The sweep **fails closed** when a check file is missing | `mv tools/records/checks/L4-P5-22.sh /tmp/c22.bak; bash tools/records/sweep-phase5.sh; echo "exit=$?"; mv /tmp/c22.bak tools/records/checks/L4-P5-22.sh` | `PHASE5 ERROR missing-check:L4-P5-22` then `exit=3` |
| 6 | The sweep does **not** claim the phase exit gate | `grep -c "NOT the P5 exit gate" tools/records/sweep-phase5.sh` | `1` |
| 7 | Nothing outside the owned paths, across the whole phase | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |
| 8 | No foreign path was touched by any Phase 5 branch merged so far | `git diff --name-only origin/integration...HEAD \| grep -vc "^metrics/\|^tools/records/"` | `0` |

#### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh L4-P5-24; echo "exit=$?"
```

**Expected output — exactly these two lines:**

```
CHECK L4-P5-24 PASS
exit=0
```

#### STOP RULE

Do not close the phase if:

- Criterion 1 prints `checks=` anything but `14`, or `pending=` anything but `4` → a task did not land, or a placeholder was answered inside the lane. Blocker.
- Criterion 4 prints anything but `4` → an L0 decision was answered by an executor. **Revert it.** Blocker.
- Criterion 5 exits `0` or `1` instead of `3`. Blocker.
- You are about to run `test-rqm-detector.sh` and it does not exist. It is not this file's; the detector is `L4-P5-05`…`L4-P5-13` in `L4-06-tasks.md`. **Do not create it here.** This is not a blocker — it is the expected state; simply stop, and report that gate P5 remains open pending the detector.

#### Close the task

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add tools/records/sweep-phase5.sh tools/records/checks/L4-P5-24.sh
git commit -m "L4-P5-24: phase 5 sweep for the ingest and boards tasks"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/05-phase-sweep
gh pr create --base integration --title "L4-P5-24: Phase 5 sweep (ingest and boards)" \
  --body "Lane 4, Phase 5. Task L4-P5-24. PHASE5 OK boards=1 ingest=6 checks=14 pending=2. This is not the P5 exit gate of L4-06-tasks.md section 5, which additionally requires the Ready-queue-miss detector."
```

---

## 10. Phase sweep, and what it does and does not close

| Question | Answer |
|---|---|
| What closes the tasks in **this file**? | `bash tools/records/sweep-phase5.sh` → `PHASE5 OK boards=1 ingest=6 checks=14 pending=2` (`L4-P5-24`) |
| What closes **Phase 5**? | Gate P5 of `L4-06-tasks.md` §5: `bash tools/records/validate-boards.sh && bash tools/records/test-rqm-detector.sh` → `RQM OK 6/6`. It needs `L4-P5-05`…`L4-P5-13`, which are not in this file. |
| Can this file's sweep substitute for gate P5? | **No.** A sweep that closed a gate it does not cover would be exactly the vacuous-instrument failure of §99.6 risk 2 (line 9281). |
| What must be true before Phase 6 starts? | Gate P5, not this sweep. `L4-P6-09` depends on `L4-P5-02` (`L4-06-tasks.md` row 87), which this file delivers. |

The two frozen dispatcher names of §0.3 are what the sweep greps: `BOARDS` for `validate-boards.sh`, `INGEST` for `validate-ingest.sh`. Renaming either breaks `sweep-phase5.sh` silently, which is why §0.3 froze them.

---

## 11. Placeholder inventory — everything this phase ships unanswered

Four placeholder tokens leave this phase in the tree, plus one behavioural rule. **Every one is an L0 decision from §6.** No executor answers any of them; `L4-P5-24` criterion 4 fails the sweep if one is answered inside the lane.

| Token | File | Decision | What ships until it is answered |
|---|---|---|---|
| `PENDING-D-L4-P5-01` | `metrics/ingest/scorecard.yaml` (`source_store`), `metrics/ingest/source-kinds.yaml` (`backing_record_store`) | D-L4-P5-01 | Scorecard is typed `collector` with no backing store; the drop measure cannot render as a miss |
| ~~`PENDING-D-L4-P5-02`~~ | `metrics/ingest/scorecard.yaml` (`routing_threshold`) | D-L4-P5-02 **decided** | Decided: `routing_threshold: any_decrease`. Token removed from sweep. |
| `UNASSIGNED-D-L4-P5-03` | `metrics/ingest/collectors.yaml` (`rendering_subsystem_lane`), `metrics/ingest/README.md`, `metrics/ingest/source-kinds.yaml` | D-L4-P5-03 | Subsystem H is named as the renderer and as unassigned. L4 opens no Grafana file. |
| ~~`PENDING-D-L4-P5-04`~~ | `metrics/boards/board-conventions.yaml` (`selected_mode`) | D-L4-P5-04 **decided** | Decided: `selected_mode: single_project_fallback`. Token removed from sweep. |
| *(no token — a required argument)* | `tools/records/estimate_capture.py` (`--item-class`) | D-L4-P5-05 | The caller supplies the item class; the module **never infers** it, and a call without it exits `3` |

Three further open items are **not** placeholders in the tree, because they are ASSISTED evidence rather than decisions:

| Awaiting | Task | Held open by |
|---|---|---|
| DevLake connector field coverage — sixteen rows | `L4-P5-17` | §99.3 item 4 line 9243; blocks Phase G3 (line 9133), nothing here |
| Private-path scrape reachability per product | `L4-P5-19` | §19.2 line 1892; blocks the launch-readiness row, nothing here |
| Scorecard behaviour against private repositories | `L4-P5-21` | §30.3 line 2737; holds the Scorecard collector unarmed, nothing here |

---

## 12. Traceability — every clause of the two §99.2 rows to a task

Subsystem **I**, line 9196, clause by clause:

| Clause, verbatim | Task | Artifact |
|---|---|---|
| *"DevLake nightly ingest"* | `L4-P5-15`, `L4-P5-16`, `L4-P5-17` | `collectors.yaml`, `devlake.yaml`, `devlake-coverage.yaml`, the ASSISTED request |
| *"Prometheus scraping `/health`, `/version`, `/metrics`"* | `L4-P5-18`, `L4-P5-19` | `prometheus.yaml`, the reachability request |
| *"Scorecard scheduled scan with drop detection"* | `L4-P5-20`, `L4-P5-21` | `scorecard.yaml`, the behaviour request |
| *"the event-log taxonomy"* | **not this file** — `L4-P3-01` | `metrics/taxonomy/event-types.yaml` (entry condition E5) |
| *"attention ledger"* | **not this file** — Phase 6, `L4-P6-01`…`L4-P6-09` | `metrics/attention/**` |
| *"metric source discipline"* | `L4-P5-22`, `L4-P5-23` | `source-kinds.yaml`, `freshness.yaml` |

Subsystem **N**, line 9201, clause by clause:

| Clause, verbatim | Task | Artifact |
|---|---|---|
| *"Boards per product plus portfolio aggregate (or the single-Project fallback)"* | `L4-P5-01` | `metrics/boards/board-conventions.yaml` — both modes, §29.1 lines 2633–2635 |
| *"horizon semantics"* | `L4-P5-02` | `metrics/boards/horizons.yaml` — H1/H2/H3 and `unplanned`, §29.2 |
| *"Ready-to-Execute definition"* | `L4-P5-03` | `metrics/boards/ready-definition.yaml` — all ten criteria, §29.3 |
| *"automatic Ready-queue-miss recording"* | **not this file** — `L4-P5-05`…`L4-P5-13` | `tools/records/rqm/**`, indexed as rows 70–78 of `L4-06-tasks.md` §2 |
| D79 banded estimate at Ready confirmation (§29.3 line 2665) | `L4-P5-04` | `tools/records/estimate_capture.py` |

---

## 13. Routed out of this file — state the dependency, never claim the path

| Need | Owner | Why this file does not do it |
|---|---|---|
| Any Grafana or dashboard surface that renders these declarations | **Subsystem H — no lane in `PARTITION.md` v1** | Escalated as **D-L4-P5-03**. The known partition gap covers G, H, J, O and P; it is not re-litigated here. L4 opens no Grafana file. |
| Installing DevLake, Prometheus, Grafana or Scorecard; the compose file; the database engine; the scrape interval; the alert rule; hostnames and ports | L5 (`ops-vm/**`) | `PARTITION.md` line 21. Every declaration in this phase names `installed_by_lane: L5` and `installed_at_path: "ops-vm/**"`. |
| `registries/os-health.yaml` (the eight-attribute metric register, §84.6 line 7471) and `registries/economics.yaml` (the estimate band vocabulary) | L1 | `PARTITION.md` line 17. L4 reads them and publishes content **for** them. `L4-P5-04` fails closed rather than creating `economics.yaml`. |
| Any `.github/workflows/**` file that schedules a nightly ingest or a nightly scan | L2 | `PARTITION.md` line 18. |
| A `records/scorecard/` store, or any addition to the §97.2 store table | L0 decision then L4 Phase 2 | **D-L4-P5-01.** `schemas/records/**` is L4's, but the store list is `L4-P2`'s and the question is L0's. |
| The Ready-queue-miss detector | L4, `L4-P5-05`…`L4-P5-13` | Indexed in `L4-06-tasks.md` §2 rows 70–78. This file builds its input and must not renumber it. |
| The §103 measure computations and the metric register | L4 Phase 7 | `L4-P7-01`…`L4-P7-16`. `source-kinds.yaml` and `devlake-coverage.yaml` are their inputs. |
| A contract change of any kind | L0 | `PARTITION.md` rule 2. A lane files a Contract Change Request; it never edits `contracts/**`. |

**End of L4-05.** Fourteen tasks, three of them ASSISTED, four L0 placeholders shipped in the open, and no artifact in this phase that installs, scrapes or renders anything.
