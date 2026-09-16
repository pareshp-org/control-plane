# L4-06 — Lane 4 Atomic Task List

**Lane 4 — Records, Events & Metrics.** Subsystems **I** (Metrics pipeline) and **N** (Work tracking conventions), Master Spec §99.2 lines 9184–9231.
**Branch prefix:** `lane/4/*` · **Merge-train position:** 2nd of 5 (L1 → **L4** → L2 → L3 → L5), `PARTITION.md` line 35.
**Owned paths (exclusive), `PARTITION.md` line 20:** ALL of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` in `control-plane`.
**Authority order:** `PARTITION.md` (FROZEN) > `MultiProduct_MasterSpec_v4.0.md` > `L4-00-charter.md` > this file. Where this file appears to differ from `PARTITION.md`, `PARTITION.md` wins and the difference is a blocker for L0.

This file is the complete, ordered work list for Lane 4. Work it **top to bottom**. Every task is executable from this file alone. Do not skip, do not reorder, do not batch.

> §99.6 risk 2 (line 9280): *"Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance if the record stores are not built early."* Mitigation: *"Section 97 is built in Foundation, before any dashboard that reads from it."* §99.2 dependency spine (line 9229): *"I is the feedstock for nearly all governance-tier and people-tier computation."* Every rule in §0 below exists because of those two sentences.

---

## 0. Standing protocol — read once, apply to every task

### 0.1 Workspace — export before every task

The shell resets between calls. Re-export these at the start of every task. Always use absolute paths.

```bash
set -euo pipefail
export ORG="${ORG:?ERROR: ORG env var must be set to the GitHub org name}"
export RECORDS_REPO="control-plane-records"
export RECORDS_SLUG="${ORG}/${RECORDS_REPO}"
export CP_REPO="control-plane"
export CP_SLUG="${ORG}/${CP_REPO}"
export WORK="$HOME/src"
export RECORDS_DIR="${WORK}/${RECORDS_REPO}"
export CP_DIR="${WORK}/${CP_REPO}"
export SECRETS_DIR="$HOME/.l4-secrets"        # never inside any git working tree
mkdir -p "$WORK" "$SECRETS_DIR" && chmod 700 "$SECRETS_DIR"
echo "ORG=$ORG RECORDS_SLUG=$RECORDS_SLUG CP_SLUG=$CP_SLUG"
```

### 0.2 Path ownership (hard)

In `control-plane` you may create or edit files **only** under these three roots:

```
schemas/records/**
metrics/**
tools/records/**
```

In `control-plane-records` you own **every** path (`PARTITION.md` line 20), subject to D-L4-TL-6.

You may **read** anything. You may **never write** to `contracts/**`, `CODEOWNERS`, `docs/**`, `Makefile`, any root file, `registries/**`, `schemas/registry/**`, `schemas/product/**`, `validators/registry/**`, `validators/drift/**`, `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`, `reconciler/**`, `tools/provision/**`, `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`. A pull request touching a foreign path fails the lane-guard check and is rejected (`PARTITION.md` rule 1, line 25).

**Namespace-package rule.** Do **not** create `tools/__init__.py` or `schemas/__init__.py`. `tools/` and `schemas/` are shared parents owned by other lanes. `tools.records` imports as a PEP 420 implicit namespace package. Creating either `__init__.py` is a foreign-path write and will be rejected.

**No shared mutable file, ever** (`PARTITION.md` rule 3, line 27; §97.3 line 8929). One file per record, one file per event, one file per schema, one file per event-type payload declaration, one file per task check. No task in this file appends to an index, list, or registry-of-everything.

### 0.3 Git protocol — every task in `control-plane`, no exceptions

Start of every task:

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/<task-slug>
```

End of every task, after its acceptance command passes:

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add <the exact files named in the task row>
git commit -m "<TASK-ID>: <task title>"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/<task-slug>
gh pr create --base integration \
  --title "<TASK-ID>: <task title>" \
  --body "Lane 4. Task <TASK-ID>. Acceptance command in L4-06-tasks.md passed."
```

One branch per task, short-lived (< 1 day), rebased on `integration` before PR (`PARTITION.md` line 34). **Never merge or rebase another lane's branch** (`PARTITION.md` line 36).

### 0.4 Git protocol — every task in `control-plane-records` (Phase 1 only)

`control-plane-records` carries **no review protection** by design (`PARTITION.md` line 8; §40.1 line 3665). Phase 1 tasks therefore commit to its default branch directly and **open no pull request**. They are still bound by the no-bypass ruleset: appends are fast-forward commits and succeed; force-push, branch deletion and tag deletion are rejected (§40.1, D107, line 3673).

```bash
set -euo pipefail
cd "$RECORDS_DIR"
git pull --ff-only origin main
git add <the exact files named in the task row>
git commit -S -m "<TASK-ID>: <task title>"
git push origin main
```

**Never propose review protection on `control-plane-records`. Never propose a bypass actor on either of its rulesets.** Both are fixed by `PARTITION.md` line 8 and §40.1 (D107, D89).

### 0.5 Deterministic output contract — used by every acceptance command in this file

Every executable this lane ships prints its result as exactly one final line on stdout and sets its exit code from the table below. Nothing else is printed to stdout on a pass.

```
<NAME> OK <counters>        exit 0    the assertion held
<NAME> FAIL <counters>      exit 1    the module executed and the assertion did not hold
<NAME> ERROR <reason>       exit 3    the module could not execute (missing input, unreachable store)
```

Exit `3` is never a pass and never a clean run. A check that cannot reach its input **fails closed** (§40.1 line 3671: *"a check that cannot reach the records repository fails closed rather than reporting zero"*). Any exit code other than 0, 1 or 3 is a crash and is a STOP.

### 0.6 The per-task check dispatcher — the universal SELF-VERIFY

Task `L4-P2-01` builds `tools/records/check.sh`, a fixed dispatcher that runs `tools/records/checks/<TASK-ID>.sh` and prints one line. **Every task from `L4-P2-01` onward contributes exactly one new file `tools/records/checks/<TASK-ID>.sh`** — a new file, never an edit to a shared one.

`tools/records/check.sh`, verbatim, written once in `L4-P2-01`:

```bash
#!/usr/bin/env bash
set -eu
# check.sh — dispatch a per-task check file.
# Normal:  check.sh <TASK-ID>           runs checks/<TASK-ID>.sh
# Audit:   check.sh --audit <TASK-ID>   validates minimum check-file requirements
#                                        before running; the phase-exit gate uses this mode.
AUDIT=0
if [ "${1:-}" = "--audit" ]; then AUDIT=1; shift; fi
T="${1:?usage: check.sh [--audit] <TASK-ID>}"
D="$(cd "$(dirname "$0")" && pwd)"
F="$D/checks/${T}.sh"
if [ ! -f "$F" ]; then echo "CHECK ${T} ERROR no-check-file"; exit 3; fi
if [ "$AUDIT" -eq 1 ]; then
  LINES="$(wc -l < "$F")"
  if [ "$LINES" -lt 10 ]; then
    echo "CHECK ${T} ERROR audit-too-short lines=${LINES} min=10"; exit 3
  fi
  if ! grep -qE '(grep[[:space:]]|\[[[:space:]].*[=!]|[[:space:]]-eq[[:space:]]|[[:space:]]-ne[[:space:]])' "$F"; then
    echo "CHECK ${T} ERROR audit-no-assertion"; exit 3
  fi
  if ! grep -qiE '(negative|fixture.*fail|bad_fixture|neg_fixture|# neg)' "$F"; then
    echo "CHECK ${T} ERROR audit-no-negative-fixture"; exit 3
  fi
fi
if bash "$F" >/dev/null 2>&1; then echo "CHECK ${T} PASS"; exit 0; fi
echo "CHECK ${T} FAIL"; exit 1
```

**Minimum check-file requirements (enforced by `--audit` mode; phase-exit gate runs `--audit`):**

1. **Length** — at least 10 lines. A stub `exit 0` or near-empty file is rejected.
2. **Assertion** — must contain at least one `grep`, `[ ... = ... ]`, or integer comparison (`-eq`, `-ne`). A file with no testable assertion cannot prove anything.
3. **Negative fixture** — must reference a fixture path or variable that is expected to cause failure (identified by the keywords `negative`, `fixture.*fail`, `bad_fixture`, `neg_fixture`, or a `# neg` comment). This proves the check can detect a bad state, not only a good one.

These requirements apply to every file under `tools/records/checks/` from `L4-P2-01` onward.

**Universal SELF-VERIFY block — applies to every task with id `L4-P2-01` or later.** Run it after the task's acceptance command passes and before you commit:

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh <TASK-ID>; echo "exit=$?"
```

**Expected output, exactly two lines, nothing else:**

```
CHECK <TASK-ID> PASS
exit=0
```

Any other output — `FAIL`, `ERROR`, a different exit, extra lines — is a STOP. Phases 0 and 1 predate the dispatcher; their SELF-VERIFY commands and expected outputs are given individually in §4.

### 0.7 STOP rule and blocker-issue template

**Standing STOP rule.** Stop, commit nothing, and file the blocker below if: the task's stated STOP condition occurs; any command errors in a way the task does not describe; a file you must edit is outside §0.2; the universal SELF-VERIFY prints anything other than the two expected lines; a spec fact you need is not written in this file; or the task would require you to design, choose or interpret anything. Do not guess, do not substitute, do not work around, do not proceed to the next task.

```bash
set -euo pipefail
BLOCKER_FILE="${WORK}/BLOCKER-${TASK_ID}.yaml"
cat > "$BLOCKER_FILE" <<'EOF'
type: blocker
blocked_task: <TASK-ID>
lane: 4
branch: lane/4/<task-slug>
repo: <control-plane | control-plane-records>
stop_condition_hit: <quote the STOP line from L4-06-tasks.md verbatim>
command_run: |
  <the exact command, copy-pasted>
observed_output: |
  <paste verbatim, do not summarise, do not redact anything except credentials>
expected_output: |
  <paste the SELF-VERIFY expected block verbatim>
files_touched_so_far: <exact paths, or "none">
state_left_behind: <branch pushed? commit made? platform object created? or "none">
what_i_did_NOT_do: <the remaining steps of the task>
decision_required_from: L0
EOF
echo "Blocker written to: $BLOCKER_FILE"
echo "BLOCKER-UNFILED"
```

Then take the next **unblocked** task in the table, or idle. Never work around a blocker.

### 0.8 The nine standing rules of this lane (from `L4-00-charter.md` §12)

1. Write only the owned paths of §0.2. Run `bash tools/records/lane-selfcheck.sh --paths` before every commit and every push.
2. Never edit `contracts/**`. A needed contract change is a Contract Change Request to L0 (`PARTITION.md` rule 2).
3. Never append to a shared file. Directory-per-item only.
4. Never reach into another lane's source tree. Consume through `contracts/**` or a published artifact only (`PARTITION.md` rule 4).
5. Prefer a new file to editing an existing one; edit only inside owned paths (`PARTITION.md` rule 5).
6. Never merge or rebase another lane's branch.
7. **Records are never edited in place.** Corrections are follow-up records (§97.2 line 8890). This binds fixtures and examples too.
8. **Every timestamp is UTC with its offset** (§97.1 line 8839). No derivation resolves against a runner's local time.
9. **A check that cannot fail is not a check.** Every validator ships with a negative test (§53.1 seeded-canary rule, line 4685).

---

## 1. DECISION REQUIRED — L0 must answer these

No L4 executor may answer any of these. Each blocks only the tasks named; everything else proceeds.

### D-L4-TL-1 — implementation language, runtime and dependency pinning

**Question.** What language, runtime version and dependency-pinning mechanism do `metrics/**` and `tools/records/**` use?
**Why L0.** §99.5 (lines 9264–9275) fixes the git host, CI, dashboard stack, records format and identity bridge. It does not fix the implementation language of subsystems I and N. Choosing one is architecture.
**Constraint from spec.** §99.1 line 9182: the build is *"a schema-and-validator suite … a metrics and report computation layer"* — scripts and CLIs, never an application. §101 invariant 85 requires third-party dependencies pinned.
**This file is written assuming L0 ratifies:** Python 3.12; dependencies pinned by exact `==` in `tools/records/requirements.txt`; no lockfile generator; every acceptance surface is a `bash` wrapper under `tools/records/` or `metrics/` so the charter's DoD commands hold regardless of engine language.
**Blocks:** `L4-P2-02` and every task after it.
**If L0 ratifies anything else:** STOP at `L4-P2-02`, file the blocker, and this whole file needs reissuing by L0.

### D-L4-TL-2 — decision-id collision across the L4 document set

**Fact.** `L4-00-charter.md` §9 uses `D-L4-01`/`D-L4-02`/`D-L4-03` for the event-type enum publication mechanism, the metric register content boundary and `.github/**` inside `control-plane-records`. `L4-01-records-repo.md` §"DECISION REQUIRED" uses the **same three ids** for the GitHub organisation login, the commit-signing mechanism and records-writer key custody. Six distinct decisions carry three ids.
**Question.** Renumber which set, to what.
**Why L0.** Document-set numbering is L0's; a lane renumbering another lane's document is a foreign-path write.
**Blocks:** nothing. This file uses the `D-L4-TL-*` namespace throughout to avoid inheriting the collision. Cite decisions by their document plus id until L0 renumbers.

### D-L4-TL-3 — Phase 0 / Phase 1 overlap on the records-repository skeleton

**Fact.** `L4-00-charter.md` §11 defines `L4-T002` *"Records repository skeleton"* and `L4-T003` *"Protection requirement declared for L0"*. `L4-01-records-repo.md` §0.3 defines `L4-P1-T02` (create the repository), `L4-P1-T03` (directory-per-item skeleton), `L4-P1-T04` (root documents) and `L4-P1-T05`/`L4-P1-T06` (the two rulesets). These overlap in scope and would create the same platform objects twice.
**Question.** Which document is authoritative for creating `control-plane-records` and its rulesets, and what becomes of the other's rows?
**Why L0.** Deleting or superseding a task defined in another lane document is a judgment call about document authority.
**Blocks:** `L4-T002`, `L4-T003`. Everything else proceeds; `L4-T004` onward do not depend on them.
**Executor default until answered:** run `L4-T001` and `L4-T004`–`L4-T007`, then stop and wait. Do not create `control-plane-records` twice.
**Status: Closed.** See `_DECISION_SIGNOFF.md`. `L4-01-records-repo.md` is authoritative; `L4-T002` is withdrawn (superseded by `L4-P1-T02`).

### D-L4-TL-4 — `SIG-43` is assigned to two different signals in §52.2

**Fact.** Master Spec line 4571 ends with a `SIG-43` row *"Unclosed learning-loop items"* sourced from `records/postmortems/` plus `records/incidents/`. Line 4572 opens a second `SIG-43` row, *"Founder operating load"*, sourced from the attention ledger. Line 4593–4594 lists `SIG-43` once, as Founder operating load; line 4611 discusses `SIG-43` as Founder operating load; line 10197 (D104) states SIG-43 to SIG-46 were added covering Founder operating load, OS net value, change-budget breach and audit-log review staleness.
**Question.** Which signal keeps `SIG-43`, and what id does the other take?
**Why L0.** `metrics/signals/sig-source-map.yaml` maps one id to one source store; it cannot carry one id twice, and inventing a replacement id is prohibited.
**Blocks:** `L4-P3-06` (the SIG source map) and `L4-P7-14` (learning-loop measures). Both are unblocked the moment L0 records an id.
**Decided.** The learning-loop signal takes `SIG-47`. Map the Founder-operating-load signal to `SIG-43` (the reading three other spec locations agree on), and emit the learning-loop row with `signal_id: SIG-47`. See `_DECISION_SIGNOFF.md`.

### D-L4-TL-5 — the GitHub organisation login, and the `contracts/**` filenames L4 consumes

**Question, part A.** The organisation login that `ORG` in §0.1 binds to.
**Question, part B.** The exact frozen paths under `contracts/**` for the five artifacts Lane 4 codes against. Lane 4 never edits them (`PARTITION.md` rule 2).

| Role | What Lane 4 does with it | Spec anchor |
| --- | --- | --- |
| Record envelope — `record_schema_version`, `id`, `product`, `timestamp` | The base every store schema extends | §97.2 line 8890 |
| Event envelope — the nine fields of the §97.3 example | The envelope validator; a missing field is rejected at write time | §97.3 lines 8931–8945 |
| UTC-with-offset timestamp format, and the declared working calendar / operating timezone reference | Every timestamp field; every business-day derivation names the calendar version it resolved against | §97.1 line 8839; §6.4 lines 446–454 |
| Versioned-contract mechanism | Record and event schemas are versioned contracts like any other | §60.2; §97.2 line 8892 |
| Product identity key and registry identity key (the GitHub login, §99.5 line 9271) | The `product:` and `actor:` fields | §97.3 lines 8938–8941 |

**Why L0.** `contracts/**` is L0-owned and frozen in Phase 0. A lane guessing a filename produces a lane that compiles against nothing.
**Discovery aid for L0:** `ls -1 "$CP_DIR"/contracts/`
**Blocks:** `L4-T001` (part A) and `L4-P2-04` (part B). Everything before `L4-P2-04` is fixture-backed and proceeds.

### D-L4-TL-6 — `.github/**` inside `control-plane-records` (restated from `L4-00-charter.md` §9)

**Fact.** `PARTITION.md` line 20 gives L4 *"ALL of `control-plane-records`"*. `PARTITION.md` line 18 gives L2 `.github/workflows/**`.
**Question.** Inside `control-plane-records`, does the repo-level grant cover `.github/**`, or does L2's path pattern reach across repositories?
**Blocks:** `L4-T003` only.
**Executor default until answered:** create no file under `control-plane-records/.github/`. Record the ruleset requirement in `control-plane-records/PROTECTION-REQUEST.md` for L0.

### Already open, not restated here

`L4-00-charter.md` §9 `D-L4-01` (how `metrics/taxonomy/event-types.yaml` reaches `registries/platform.yaml`) blocks the integration side of `L4-P3-01`/`L4-P3-03`. `L4-00-charter.md` §9 `D-L4-02` (how `metrics/register/metric-declarations.yaml` reaches `registries/os-health.yaml`) blocks the integration side of `L4-P7-01`–`L4-P7-04`. `L4-01-records-repo.md` `D-L4-02` (commit-signing mechanism) blocks `L4-P1-T08`. In every case the **L4-owned artifact is still built** on schedule; only the embedding into an L1 file waits. **L4 never writes to `registries/**` under any circumstance.**

---

## Section 2 — CONCORDANCE INDEX (FD-031/FD-048/FD-049)

Canonical tasks are defined in the phase files listed below. This index is a read-only cross-reference. Executors work from the phase files directly. The superseded master table that follows this section uses a conflicting task-id namespace and must not be used for execution.

| Phase File | Task ID | Title | Phase |
| --- | --- | --- | --- |
| L4-01-records-repo.md | L4-P1-T01 | Preflight and parameter binding | 1 |
| L4-01-records-repo.md | L4-P1-T02 | Create the `control-plane-records` repository | 1 |
| L4-01-records-repo.md | L4-P1-T03 | Build the directory-per-item skeleton | 1 |
| L4-01-records-repo.md | L4-P1-T04 | Root documents: `README.md`, `CONVENTIONS.md`, `.gitignore` | 1 |
| L4-01-records-repo.md | L4-P1-T05 | Arm the no-bypass branch ruleset (force-push + deletion) | 1 |
| L4-01-records-repo.md | L4-P1-T06 | Arm the no-bypass tag ruleset (tag deletion) | 1 |
| L4-01-records-repo.md | L4-P1-T07 | Prove: rewriting blocked, appending permitted | 1 |
| L4-01-records-repo.md | L4-P1-T08 | Add `required_signatures` and prove it | 1 |
| L4-01-records-repo.md | L4-P1-T09 | Create the `records-writer` GitHub App | 1 |
| L4-01-records-repo.md | L4-P1-T10 | Install and scope the App to `control-plane-records` alone | 1 |
| L4-01-records-repo.md | L4-P1-T11 | Prove the App appends here and reaches no registry | 1 |
| L4-01-records-repo.md | L4-P1-T12 | Store ruleset and credential shape as code in `tools/records/` | 1 |
| L4-02-record-schemas.md | L4-T201 | Phase branch and toolchain preflight | 2 |
| L4-02-record-schemas.md | L4-T202 | `record.base.schema.json`, the shared `$defs`, and the validator library | 2 |
| L4-02-record-schemas.md | L4-T203 | `metrics/taxonomy/event-types.yaml`, the closed 89-identifier enum (D114-D / REG-021) | 2 |
| L4-02-record-schemas.md | L4-T204 | `event.envelope.schema.json` and the generated `event-type.enum.json` | 2 |
| L4-02-record-schemas.md | L4-T205 | D88 no-names enforcement: the property-name lint and the value scanner | 2 |
| L4-02-record-schemas.md | L4-T206 | `incident.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T207 | `postmortem.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T208 | `uat.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T209 | `estimate.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T210 | `deployment.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T211 | `restore-test.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T212 | `decision.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T213 | `decision-pending.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T214 | `breach.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T215 | `deletion-request.schema.json` (AT-105) | 2 |
| L4-02-record-schemas.md | L4-T216 | `security-review.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T217 | `eval.schema.json` (SIG-42) | 2 |
| L4-02-record-schemas.md | L4-T218 | `launch.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T219 | `demo.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T220 | `support.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T221 | `onboarding.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T222 | `leave.schema.json` | 2 |
| L4-02-record-schemas.md | L4-T223 | `store-map.yaml` and `validate-schemas.sh` (coverage, lint, `--fields`, `--time`) | 2 |
| L4-02-record-schemas.md | L4-T224 | The ten rule-level negative fixtures, `--negative` 10/10 | 2 |
| L4-02-record-schemas.md | L4-T225 | Rebase and open the phase PR to `integration` | 2 |
| L4-03-write-paths.md | L4-T301 | Phase-3 preflight and phase branch | 3 |
| L4-03-write-paths.md | L4-T302 | The write-path register | 3 |
| L4-03-write-paths.md | L4-T303 | Write-path register validator, with its negative test | 3 |
| L4-03-write-paths.md | L4-T304 | The RECORD-VERIFICATION-RESULT input contract | 3 |
| L4-03-write-paths.md | L4-T305 | The emission library `tools/records/lib/emit.sh` | 3 |
| L4-03-write-paths.md | L4-T306 | The RECORD-VERIFICATION-RESULT handler | 3 |
| L4-03-write-paths.md | L4-T307 | RVR test harness (charter DoD-9) | 3 |
| L4-03-write-paths.md | L4-T308 | The board-event emission contract | 3 |
| L4-03-write-paths.md | L4-T309 | The board emitter and the Ready-queue-miss emitter | 3 |
| L4-03-write-paths.md | L4-T310 | Taxonomy conformance check for both emission contracts | 3 |
| L4-03-write-paths.md | L4-T311 | The deploy required-step contract | 3 |
| L4-03-write-paths.md | L4-T312 | The deploy emitter | 3 |
| L4-03-write-paths.md | L4-T313 | The deploy emitter failure test | 3 |
| L4-03-write-paths.md | L4-T314 | The human review lane, declared | 3 |
| L4-03-write-paths.md | L4-T315 | The no-hand-edit guard | 3 |
| L4-03-write-paths.md | L4-T316 | Phase-3 coverage proof, rebase and lane PR | 3 |
| L4-03-metric-register.md | L4-P3-06 | SIG source map and metrics/register bootstrap | 3 |
| L4-03-metric-register.md | L4-P7-01 | Metric declarations — the eight attributes per measure | 7 |
| L4-03-metric-register.md | L4-P7-02 | Source discipline — every measure names its record store | 7 |
| L4-03-metric-register.md | L4-P7-03 | Arming discipline — empty store renders `unbaselined`, never a miss | 7 |
| L4-03-metric-register.md | L4-P7-04 | Baseline markers and the §103.14 minimum baseline set | 7 |
| L4-03-metric-register.md | L4-P7-05 | Owner-and-response completeness gate (invariant 49) | 7 |
| L4-03-metric-register.md | L4-P7-06 | Deployment measures | 7 |
| L4-03-metric-register.md | L4-P7-07 | Incident measures | 7 |
| L4-03-metric-register.md | L4-P7-08 | Restore measures — freshness and failed tests | 7 |
| L4-03-metric-register.md | L4-P7-09 | UAT coverage and pass rate | 7 |
| L4-03-metric-register.md | L4-P7-10 | Support measures — load and first-response by severity | 7 |
| L4-03-metric-register.md | L4-P7-11 | Eval measures and regression detection | 7 |
| L4-03-metric-register.md | L4-P7-12 | Security-review measures — count by severity, unfixed-finding age | 7 |
| L4-03-metric-register.md | L4-P7-13 | Decision latency and pending-decision queue depth and age | 7 |
| L4-03-metric-register.md | L4-P7-14 | Learning-loop measures (SIG-47) | 7 |
| L4-03-metric-register.md | L4-P7-15 | Estimate-vs-actual and forecast-calibration inputs | 7 |
| L4-03-metric-register.md | L4-P7-16 | Ready-queue-miss measure — 30-day rolling count and trend | 7 |
| L4-03-metric-register.md | L4-P7-17 | Status-request count from the event log | 7 |
| L4-03-metric-register.md | L4-P7-18 | Onboarding, launch and demo cadence measures | 7 |
| L4-03-metric-register.md | L4-P7-19 | Undeclared weekend activations — the residual | 7 |
| L4-03-metric-register.md | L4-P7-20 | Attention-ledger measures | 7 |
| L4-04-attention-ledger.md | L4-T401 | Phase-4 preflight and phase branch | 4 |
| L4-04-attention-ledger.md | L4-T402 | The eight-category taxonomy artifact | 4 |
| L4-04-attention-ledger.md | L4-T403 | The per-category source map | 4 |
| L4-04-attention-ledger.md | L4-T404 | The calibrated-configuration register | 4 |
| L4-04-attention-ledger.md | L4-T405 | Config validator, with its negative test | 4 |
| L4-04-attention-ledger.md | L4-T406 | Scheduled availability, the daily cap's input | 4 |
| L4-04-attention-ledger.md | L4-T407 | The duration rule, part 1: config reader, activity session, idle gap, granularity | 4 |
| L4-04-attention-ledger.md | L4-T408 | The duration rule, part 2: category precedence (DR-5) | 4 |
| L4-04-attention-ledger.md | L4-T409 | The duration rule, part 3: product attribution (DR-6) | 4 |
| L4-04-attention-ledger.md | L4-T410 | The duration rule, part 4: daily reconciliation and the instrument defect (DR-7) | 4 |
| L4-04-attention-ledger.md | L4-T411 | `derive.py`, the attention ledger | 4 |
| L4-04-attention-ledger.md | L4-T412 | This phase's own proof: `metrics/attention/selfcheck/` | 4 |
| L4-04-attention-ledger.md | L4-T413 | `HANDOFF-P.md`: what this phase emits for the lane that does not exist | 4 |
| L4-04-attention-ledger.md | L4-T414 | Every metric names its store, or it does not ship | 4 |
| L4-04-attention-ledger.md | L4-T415 | Attention-ledger gate: every check in order, and the phase checkpoint | 4 |
| L4-04-attention-ledger.md | L4-T416 | The Ready-queue-miss contract | 4 |
| L4-04-attention-ledger.md | L4-T417 | `rqm-detect`, the Ready-queue-miss detector | 4 |
| L4-04-attention-ledger.md | L4-T418 | Phase-4 coverage proof, rebase and lane PR | 4 |
<!-- LEGACY DRAFT ROWS (2026-09-06): L4-04-metric-register.md used slot-04 numbering before
     Session 13 created the canonical L4-03-metric-register.md with the correct task IDs
     (L4-P3-06, L4-P7-01..L4-P7-20).  These M01..M15 rows are ORPHANED — they have no
     corresponding Phase-7 index entry and are superseded by the 21 rows above.
     The canonical file is L4-03-metric-register.md. -->
| ~~L4-04-metric-register.md~~ | ~~L4-04-M01~~ | ~~Metric Attribute Schema~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M02~~ | ~~Write-Freshness Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M03~~ | ~~Freshness Validator~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M04~~ | ~~Head-SHA Anchor Schema~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M05~~ | ~~Signal Source Map~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M06~~ | ~~Engineering and Delivery Metric Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M07~~ | ~~Reliability and Business Metric Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M08~~ | ~~Platform, Team Lead, Founder, and Review Network Metric Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M09~~ | ~~Knowledge, Bottleneck, Portfolio, and OS Success Metric Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M10~~ | ~~Source Validator Base Pass~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M11~~ | ~~Arming-Discipline Validator~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M12~~ | ~~Baseline Integrity Validator~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M13~~ | ~~Retention Class Declarations~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M14~~ | ~~Retention Validator~~ | LEGACY |
| ~~L4-04-metric-register.md~~ | ~~L4-04-M15~~ | ~~Metric-Declarations Publication Interface~~ | LEGACY |
| L4-05-pipeline-and-boards.md | L4-P5-01 | Board conventions: seven columns, Blocked as a flag, Deploy rendered | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-02 | Horizon semantics H1/H2/H3 and the `unplanned` rule | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-03 | Ready-to-Execute definition as machine-checkable configuration | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-04 | Estimate capture at Ready confirmation (D79) | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-14 | Ingest entry gate, `metrics/ingest/` skeleton and the `INGEST` dispatcher | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-15 | `collectors.yaml`: the three named collectors and their cadences | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-16 | DevLake nightly ingest declaration and the §99.3 coverage gate | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-17 | (ASSISTED) DevLake connector field-coverage confirmation | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-18 | Prometheus scrape declaration: the three §41.2 endpoints | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-19 | (ASSISTED) private-path scrape reachability evidence | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-20 | Scorecard scheduled scan and drop detection | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-21 | (ASSISTED) Scorecard private-repository behaviour and baseline scan | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-22 | Metric source discipline: the `source_kind` rule and its validator | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-23 | Ingest freshness and the three arming strings | 5 |
| L4-05-pipeline-and-boards.md | L4-P5-24 | Phase sweep, rebase, PR | 5 |

---

> **OLD SECTION 2 — SUPERSEDED — kept for reference only — do not use these task IDs**

## 2. Master task table — all 117 tasks in execution order

Work top to bottom. `Deps` are task ids that must be **merged to `integration`** first (Phase 1 rows: pushed to `control-plane-records` `main` first). Paths in the `Files touched` column are repo-relative: Phase 1 rows are relative to `control-plane-records`, every other row is relative to `control-plane`. Every task from `L4-P2-01` onward also writes its own `tools/records/checks/<TASK-ID>.sh`; that file is implied on every such row and is not repeated in the column.

**Sizes:** **S** under half a day · **M** half a day to two days · **L** two to five days.

| # | ID | Ph | Title | Files touched | Deps | Sz | Acceptance command |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | L4-T001 | 0 | Preflight and lane branch | none (branch only) | D-L4-TL-5A | S | `gh api "/orgs/${ORG}" --jq .login` |
| 2 | L4-T002 **WITHDRAWN** | 0 | Records repository skeleton | `control-plane-records` (whole repo) | L4-T001, D-L4-TL-3 | M | *(superseded by `L4-P1-T02`)* |
| 3 | L4-T003 | 0 | Protection requirement declared for L0 | `PROTECTION-REQUEST.md` (records repo) | L4-T002, D-L4-TL-6 | S | `gh api "/repos/${RECORDS_SLUG}/contents/PROTECTION-REQUEST.md" --jq .name` |
| 4 | L4-T004 | 0 | Scaffold the three owned control-plane directories | `schemas/records/.gitkeep`, `metrics/.gitkeep`, `tools/records/.gitkeep` | L4-T001 | S | `ls -1d schemas/records metrics tools/records | wc -l` |
| 5 | L4-T005 | 0 | Lane path-ownership self-check script | `tools/records/lane-selfcheck.sh` | L4-T004 | M | `bash tools/records/lane-selfcheck.sh --paths` |
| 6 | L4-T006 | 0 | Machine-readable spec-coverage manifest | `metrics/register/l4-spec-coverage.csv` | L4-T004 | M | `bash tools/records/lane-selfcheck.sh --coverage` |
| 7 | L4-T007 | 0 | Rebase and open the Phase 0 lane PR | none (git only) | L4-T004, L4-T005, L4-T006 | S | `gh pr view --json state --jq .state` |
| 8 | L4-P1-T01 | 1 | Preflight and parameter binding | none (read-only) | L4-T001 | S | `gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq .role` |
| 9 | L4-P1-T02 | 1 | Create the `control-plane-records` repository | the repository `${RECORDS_SLUG}` | L4-P1-T01 | S | `gh api "/repos/${RECORDS_SLUG}" --jq .private` |
| 10 | L4-P1-T03 | 1 | Build the directory-per-item skeleton | `records/**/.gitkeep`, `events/.gitkeep`, `bootstrap/.gitkeep` | L4-P1-T02 | M | `gh api "/repos/${RECORDS_SLUG}/git/trees/main?recursive=1" --jq '[.tree[]\|select(.path\|endswith(".gitkeep"))]\|length'` |
| 11 | L4-P1-T04 | 1 | Root documents: `README.md`, `CONVENTIONS.md`, `.gitignore` | `README.md`, `CONVENTIONS.md`, `.gitignore` | L4-P1-T03 | M | `gh api "/repos/${RECORDS_SLUG}/contents/CONVENTIONS.md" --jq .name` |
| 12 | L4-P1-T05 | 1 | Arm the no-bypass **branch** ruleset (force-push + deletion) | ruleset on `${RECORDS_SLUG}` | L4-P1-T04 | M | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq -c '[.rules[].type]\|sort'` |
| 13 | L4-P1-T06 | 1 | Arm the no-bypass **tag** ruleset (tag deletion) | ruleset on `${RECORDS_SLUG}` | L4-P1-T02 | S | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq -c '[.rules[].type]\|sort'` |
| 14 | L4-P1-T07 | 1 | Prove rewriting blocked, appending permitted | one commit under `bootstrap/` | L4-P1-T05, L4-P1-T06 | M | `git push --force origin HEAD:main; echo "push_exit=$?"` |
| 15 | L4-P1-T08 | 1 | Add `required_signatures` and prove it | the branch ruleset; one API commit under `bootstrap/` | L4-P1-T07 | M | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified` |
| 16 | L4-P1-T09 | 1 | Create the `records-writer` GitHub App | GitHub App in `${ORG}`; `${SECRETS_DIR}/records-writer.pem` | L4-P1-T02 | M | `gh api "/apps/${APP_SLUG}" --jq -c .permissions` |
| 17 | L4-P1-T10 | 1 | Install and scope the App to `control-plane-records` alone | App installation; `tools/records/rw-token.sh` (uncommitted) | L4-P1-T09 | M | `gh api "/orgs/${ORG}/installations" --jq '.installations[]\|select(.app_slug=="'"${APP_SLUG}"'")\|.repository_selection'` |
| 18 | L4-P1-T11 | 1 | Prove the App appends here and reaches no registry | two commits under `bootstrap/`, written by the App | L4-P1-T10, L4-P1-T08 | M | `curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${RW_TOKEN}" "https://api.github.com/repos/${CP_SLUG}/contents/README.md"` |
| 19 | L4-P1-T12 | 1 | Store ruleset and credential shape as code | `tools/records/rulesets/*.json`, `tools/records/rw-token.sh`, `tools/records/CREDENTIAL.md` | L4-P1-T05, L4-P1-T06, L4-P1-T08, L4-P1-T10 | M | `bash tools/records/lane-selfcheck.sh --paths` |
| 20 | L4-P2-01 | 2 | Check dispatcher and the deterministic output contract | `tools/records/check.sh`, `tools/records/CONTRACT.md` | L4-T005 | S | `bash tools/records/check.sh L4-P2-01` |
| 21 | L4-P2-02 | 2 | Schema toolchain, pinned deps, `validate-schemas.sh` skeleton | `tools/records/requirements.txt`, `tools/records/validate-schemas.sh`, `tools/records/lib/schemaload.py` | L4-P2-01, D-L4-TL-1 | M | `bash tools/records/validate-schemas.sh --selftest` |
| 22 | L4-P2-03 | 2 | UTC-with-offset timestamp definition and its negative cases | `schemas/records/defs/timestamp.schema.json` | L4-P2-02 | S | `bash tools/records/validate-schemas.sh --time` |
| 23 | L4-P2-04 | 2 | Record envelope base schema | `schemas/records/record.envelope.schema.json` | L4-P2-03, D-L4-TL-5B | M | `bash tools/records/validate-schemas.sh --only record.envelope` |
| 24 | L4-P2-05 | 2 | Event envelope schema — the nine binding fields | `schemas/records/event.envelope.schema.json` | L4-P2-03, D-L4-TL-5B | M | `bash tools/records/validate-schemas.sh --only event.envelope` |
| 25 | L4-P2-06 | 2 | Store inventory manifest — the 17 record store paths | `schemas/records/store-inventory.yaml` | L4-P2-04 | M | `bash tools/records/lane-selfcheck.sh --stores` |
| 26 | L4-P2-07 | 2 | `incident` record schema | `schemas/records/incident.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only incident` |
| 27 | L4-P2-08 | 2 | `postmortem` record schema | `schemas/records/postmortem.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only postmortem` |
| 28 | L4-P2-09 | 2 | `uat` record schema | `schemas/records/uat.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only uat` |
| 29 | L4-P2-10 | 2 | `estimate` record schema — band, point value, elapsed, elapsed-net-Blocked | `schemas/records/estimate.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only estimate` |
| 30 | L4-P2-11 | 2 | `deployment` record schema | `schemas/records/deployment.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only deployment` |
| 31 | L4-P2-12 | 2 | `restore-test` record schema — `integrity_check` and named verifier | `schemas/records/restore-test.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only restore-test` |
| 32 | L4-P2-13 | 2 | `decision` record schema, with the `pending` sub-store state | `schemas/records/decision.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only decision` |
| 33 | L4-P2-14 | 2 | `breach` record schema — notification deadline | `schemas/records/breach.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only breach` |
| 34 | L4-P2-15 | 2 | `deletion-request` record schema — four timestamps, executor, subprocessor checklist, carve-out | `schemas/records/deletion-request.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only deletion-request` |
| 35 | L4-P2-16 | 2 | `security-review` record schema — findings, severity, disposition | `schemas/records/security-review.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only security-review` |
| 36 | L4-P2-17 | 2 | `eval` record schema — scored dimensions, baseline, tolerance | `schemas/records/eval.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only eval` |
| 37 | L4-P2-18 | 2 | `launch` record schema | `schemas/records/launch.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only launch` |
| 38 | L4-P2-19 | 2 | `demo` record schema | `schemas/records/demo.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only demo` |
| 39 | L4-P2-20 | 2 | `support` record schema — `detection_source`, received-timestamp anchor | `schemas/records/support.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only support` |
| 40 | L4-P2-21 | 2 | `onboarding` record schema | `schemas/records/onboarding.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only onboarding` |
| 41 | L4-P2-22 | 2 | `leave` record schema — working calendar and operating timezone | `schemas/records/leave.schema.json` | L4-P2-06 | M | `bash tools/records/validate-schemas.sh --only leave` |
| 42 | L4-P2-23 | 2 | Shared flag definitions: `agent_authored`, `detection_source`, `pre_onboarding` | `schemas/records/defs/flags.schema.json` | L4-P2-07, L4-P2-20 | S | `bash tools/records/validate-schemas.sh --fields` |
| 43 | L4-P2-24 | 2 | AT-105 conformance assertion on `deletion-request` | `tools/records/asserts/at105.py` | L4-P2-15 | S | `bash tools/records/validate-schemas.sh --at105` |
| 44 | L4-P2-25 | 2 | Security-review conformance assertion (unfixed-finding linkage) | `tools/records/asserts/secreview.py` | L4-P2-16 | S | `bash tools/records/validate-schemas.sh --at046-secreview` |
| 45 | L4-P2-26 | 2 | Golden valid fixtures — one file per store | `tools/records/fixtures/valid/**` | L4-P2-22 | M | `bash tools/records/validate-schemas.sh --fixtures valid` |
| 46 | L4-P2-27 | 2 | Negative fixture suite — 10 envelope rejections | `tools/records/fixtures/invalid/**` | L4-P2-05, L4-P2-26 | M | `bash tools/records/validate-schemas.sh --negative` |
| 47 | L4-P2-28 | 2 | Record and event schema version register (§60.2) | `schemas/records/versions.yaml`, `schemas/records/VERSIONS.md` | L4-P2-27 | S | `bash tools/records/validate-schemas.sh --versions` |
| 48 | L4-P2-29 | 2 | Full schema sweep over every store | `tools/records/checks/L4-P2-29.sh` only | L4-P2-03…L4-P2-28 | S | `bash tools/records/validate-schemas.sh` |
| 49 | L4-P3-01 | 3 | `event-types.yaml` — one identifier per §97.3 tracked event | `metrics/taxonomy/event-types.yaml` | L4-P2-29 | L | `bash tools/records/validate-taxonomy.sh --ids` |
| 50 | L4-P3-02 | 3 | Per-type payload declarations, one file per type | `metrics/taxonomy/payloads/<event_type>.yaml` | L4-P3-01 | L | `bash tools/records/validate-taxonomy.sh --payloads` |
| 51 | L4-P3-03 | 3 | Retire-never-remove mechanism and `validate-taxonomy.sh` | `tools/records/validate-taxonomy.sh`, `metrics/taxonomy/RETIREMENT.md` | L4-P3-02 | M | `bash tools/records/validate-taxonomy.sh` |
| 52 | L4-P3-04 | 3 | Write-freshness windows per store, 3 Blocking | `metrics/freshness/write-freshness.yaml`, `tools/records/validate-freshness.sh` | L4-P2-06 | M | `bash tools/records/validate-freshness.sh` |
| 53 | L4-P3-05 | 3 | Records head-SHA anchor schema (D107) | `metrics/anchor/records-head-anchor.schema.json` | L4-P2-05 | M | `bash tools/records/validate-schemas.sh --only records-head-anchor` |
| 54 | L4-P3-06 | 3 | SIG source map — which signal derives from which L4 store | `metrics/signals/sig-source-map.yaml` | L4-P2-29, D-L4-TL-4 | M | `bash tools/records/validate-taxonomy.sh --signals` |
| 55 | L4-P3-07 | 3 | Retention classes per store (§97.6) | `metrics/retention/retention-classes.yaml`, `tools/records/validate-retention.sh` | L4-P2-06 | M | `bash tools/records/validate-retention.sh` |
| 56 | L4-P4-01 | 4 | Writer library: UTC clock, id minting, path resolution | `tools/records/lib/writer.py` | L4-P3-03, L4-P3-04 | M | `bash tools/records/test-writers.sh --lib` |
| 57 | L4-P4-02 | 4 | No-overwrite guard (invariant 48) | `tools/records/lib/nooverwrite.py` | L4-P4-01 | M | `bash tools/records/test-writers.sh --nooverwrite` |
| 58 | L4-P4-03 | 4 | `record-write` — validate, then append one record file | `tools/records/record-write`, `tools/records/record_write.py` | L4-P4-02 | M | `bash tools/records/test-writers.sh --record-write` |
| 59 | L4-P4-04 | 4 | Event id and date-partition path convention | `tools/records/lib/eventpath.py` | L4-P4-01 | S | `bash tools/records/test-writers.sh --eventpath` |
| 60 | L4-P4-05 | 4 | `event-append` — envelope and enum rejection at write time | `tools/records/event-append`, `tools/records/event_append.py` | L4-P4-04, L4-P3-03 | M | `bash tools/records/test-writers.sh --event-append` |
| 61 | L4-P4-06 | 4 | `record-verification-result` — the RECORD-VERIFICATION-RESULT handler | `tools/records/record-verification-result`, `tools/records/rvr.py`, `tools/records/test-rvr.sh` | L4-P4-03, L4-P4-05 | L | `bash tools/records/test-rvr.sh` |
| 62 | L4-P4-07 | 4 | `record-decision` CLI — pending, then decided | `tools/records/record-decision`, `tools/records/record_decision.py` | L4-P4-03, L4-P2-13 | M | `bash tools/records/test-writers.sh --record-decision` |
| 63 | L4-P4-08 | 4 | `read-across` — fail-closed cross-repository reader | `tools/records/read-across`, `tools/records/read_across.py`, `tools/records/test-read-across.sh` | L4-P4-01 | M | `bash tools/records/test-read-across.sh --unreachable` |
| 64 | L4-P4-09 | 4 | Writer negative suite — no hand-edit path, no in-place edit | `tools/records/fixtures/writer-negative/**`, `tools/records/test-writers.sh` | L4-P4-06, L4-P4-07 | M | `bash tools/records/test-writers.sh --negative` |
| 65 | L4-P4-10 | 4 | Records-writer token adapter for every writer | `tools/records/lib/rwtoken.py` | L4-P4-01, L4-P1-T12 | S | `bash tools/records/test-writers.sh --token-adapter` |
| 66 | L4-P5-01 | 5 | Board conventions — seven columns, Blocked as a flag, Deploy rendered | `metrics/boards/board-conventions.yaml` | L4-P3-01 | M | `bash tools/records/validate-boards.sh --columns` |
| 67 | L4-P5-02 | 5 | Horizon semantics H1/H2/H3 and the `unplanned` rule | `metrics/boards/horizons.yaml` | L4-P5-01 | S | `bash tools/records/validate-boards.sh --horizons` |
| 68 | L4-P5-03 | 5 | Ready-to-Execute definition as machine-checkable configuration | `metrics/boards/ready-definition.yaml`, `tools/records/validate-boards.sh` | L4-P5-01 | M | `bash tools/records/validate-boards.sh --ready` |
| 69 | L4-P5-04 | 5 | Estimate capture at Ready confirmation | `tools/records/estimate_capture.py` | L4-P5-03, L4-P2-10 | M | `bash tools/records/validate-boards.sh --estimate-capture` |
| 70 | L4-P5-05 | 5 | RQM detector skeleton and the §29.4 field set | `tools/records/rqm/detect.py`, `tools/records/rqm/fields.yaml` | L4-P5-03, L4-P4-05 | M | `bash tools/records/test-rqm-detector.sh --fields` |
| 71 | L4-P5-06 | 5 | RQM limb 1 — pickup of an item that never passed Ready | `tools/records/rqm/limb_pickup.py` | L4-P5-05 | M | `bash tools/records/test-rqm-detector.sh --limb pickup` |
| 72 | L4-P5-07 | 5 | RQM limb 2 — completion with an empty Ready queue | `tools/records/rqm/limb_completion.py` | L4-P5-05 | M | `bash tools/records/test-rqm-detector.sh --limb completion` |
| 73 | L4-P5-08 | 5 | Planned-column carve-out — Ready→Planned→In Progress is never a miss | `tools/records/rqm/carveout_planned.py` | L4-P5-06 | S | `bash tools/records/test-rqm-detector.sh --carveout planned` |
| 74 | L4-P5-09 | 5 | Blocked-resumption carve-out — clearing the flag is not a fresh pickup | `tools/records/rqm/carveout_blocked.py` | L4-P5-06 | S | `bash tools/records/test-rqm-detector.sh --carveout blocked` |
| 75 | L4-P5-10 | 5 | `ready_bypass` — recorded, and excluded from the SIG-06 count | `tools/records/rqm/bypass.py` | L4-P5-06, L4-P3-06 | M | `bash tools/records/test-rqm-detector.sh --bypass` |
| 76 | L4-P5-11 | 5 | Cause-prompt fields — supplied, never inferred | `tools/records/rqm/cause_prompt.py` | L4-P5-05 | M | `bash tools/records/test-rqm-detector.sh --cause` |
| 77 | L4-P5-12 | 5 | RQM detector acceptance harness | `tools/records/test-rqm-detector.sh`, `tools/records/fixtures/rqm/**` | L4-P5-06…L4-P5-11 | M | `bash tools/records/test-rqm-detector.sh` |
| 78 | L4-P5-13 | 5 | Material requirement change — re-plan event linked to the estimate record | `tools/records/rqm/replan.py` | L4-P5-04, L4-P3-01 | M | `bash tools/records/validate-boards.sh --replan` |
| 79 | L4-P6-01 | 6 | The eight attention categories, and nothing else | `metrics/attention/categories.yaml` | L4-P3-01 | M | `bash metrics/attention/test-derivation.sh --categories` |
| 80 | L4-P6-02 | 6 | Per-category derivation source map | `metrics/attention/sources.yaml` | L4-P6-01 | M | `bash metrics/attention/test-derivation.sh --sources` |
| 81 | L4-P6-03 | 6 | Activity-session builder and the idle gap | `metrics/attention/sessions.py`, `metrics/attention/calibrated.yaml` | L4-P6-02 | L | `bash metrics/attention/test-derivation.sh --sessions` |
| 82 | L4-P6-04 | 6 | Attribution granularity — 0.25 h, nearest, never zero | `metrics/attention/granularity.py` | L4-P6-03 | M | `bash metrics/attention/test-derivation.sh --granularity` |
| 83 | L4-P6-05 | 6 | Category precedence order | `metrics/attention/precedence.py` | L4-P6-03 | M | `bash metrics/attention/test-derivation.sh --precedence` |
| 84 | L4-P6-06 | 6 | Product attribution — one, several, none | `metrics/attention/attribution.py` | L4-P6-03 | M | `bash metrics/attention/test-derivation.sh --attribution` |
| 85 | L4-P6-07 | 6 | Daily reconciliation with recorded truncations | `metrics/attention/reconcile.py` | L4-P6-05, L4-P6-06 | L | `bash metrics/attention/test-derivation.sh --reconcile` |
| 86 | L4-P6-08 | 6 | The instrument-defect rule | `metrics/attention/instrument_defect.py` | L4-P6-07 | M | `bash metrics/attention/test-derivation.sh --instrument-defect` |
| 87 | L4-P6-09 | 6 | `unplanned` and `ritual` flags — flags, never a ninth category | `metrics/attention/flags.py` | L4-P6-01, L4-P5-02 | M | `bash metrics/attention/test-derivation.sh --flags` |
| 88 | L4-P6-10 | 6 | Banded weekly self-report intake | `metrics/attention/selfreport.py`, `metrics/attention/bands.yaml` | L4-P6-01 | M | `bash metrics/attention/test-derivation.sh --selfreport` |
| 89 | L4-P6-11 | 6 | Band apportionment by machine-derived share | `metrics/attention/apportion.py` | L4-P6-10, L4-P6-06 | M | `bash metrics/attention/test-derivation.sh --apportion` |
| 90 | L4-P6-12 | 6 | Five-minute collection-cost cap assertion | `metrics/attention/collection_cost.py` | L4-P6-10 | S | `bash metrics/attention/test-derivation.sh --cost-cap` |
| 91 | L4-P6-13 | 6 | Permanent `self-reported` provenance label | `metrics/attention/provenance.py` | L4-P6-11 | M | `bash metrics/attention/test-derivation.sh --provenance` |
| 92 | L4-P6-14 | 6 | Declared limitations of the attention hour | `metrics/attention/limitations.yaml` | L4-P6-13 | S | `bash metrics/attention/test-derivation.sh --limitations` |
| 93 | L4-P6-15 | 6 | Attention-ledger acceptance harness | `metrics/attention/test-derivation.sh`, `metrics/attention/fixtures/**` | L4-P6-01…L4-P6-14 | M | `bash metrics/attention/test-derivation.sh` |
| 94 | L4-P7-01 | 7 | Metric declarations — the eight attributes per measure | `metrics/register/metric-declarations.yaml` | L4-P3-06 | L | `bash metrics/register/validate-sources.sh --attributes` |
| 95 | L4-P7-02 | 7 | Source discipline — every measure names its record store | `metrics/register/validate-sources.sh` | L4-P7-01 | M | `bash metrics/register/validate-sources.sh` |
| 96 | L4-P7-03 | 7 | Arming discipline — empty store renders `unbaselined`, never a miss | `metrics/register/arming.py` | L4-P7-02 | M | `bash metrics/register/validate-sources.sh --arming` |
| 97 | L4-P7-04 | 7 | Baseline markers and the §103.14 minimum baseline set | `metrics/register/baselines.yaml`, `metrics/register/baselines.py` | L4-P7-03 | M | `bash metrics/register/validate-sources.sh --at046` |
| 98 | L4-P7-05 | 7 | Owner-and-response completeness gate (invariant 49) | `metrics/register/ownership.py` | L4-P7-01 | M | `bash metrics/register/validate-sources.sh --ownership` |
| 99 | L4-P7-06 | 7 | Deployment measures | `metrics/compute/deployments.py` | L4-P2-11, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute deployments` |
| 100 | L4-P7-07 | 7 | Incident measures | `metrics/compute/incidents.py` | L4-P2-07, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute incidents` |
| 101 | L4-P7-08 | 7 | Restore measures — freshness and failed tests | `metrics/compute/restore.py` | L4-P2-12, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute restore` |
| 102 | L4-P7-09 | 7 | UAT coverage and pass rate | `metrics/compute/uat.py` | L4-P2-09, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute uat` |
| 103 | L4-P7-10 | 7 | Support measures — load and first-response by severity | `metrics/compute/support.py` | L4-P2-20, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute support` |
| 104 | L4-P7-11 | 7 | Eval measures and regression detection | `metrics/compute/eval.py` | L4-P2-17, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute eval` |
| 105 | L4-P7-12 | 7 | Security-review measures — count by severity, unfixed-finding age | `metrics/compute/security_reviews.py` | L4-P2-16, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute security_reviews` |
| 106 | L4-P7-13 | 7 | Decision latency and pending-decision queue depth and age | `metrics/compute/decisions.py` | L4-P2-13, L4-P4-07 | M | `bash metrics/register/validate-sources.sh --compute decisions` |
| 107 | L4-P7-14 | 7 | Learning-loop measures | `metrics/compute/learning_loop.py` | L4-P2-08, L4-P2-07, D-L4-TL-4 | M | `bash metrics/register/validate-sources.sh --compute learning_loop` |
| 108 | L4-P7-15 | 7 | Estimate-vs-actual and forecast-calibration inputs | `metrics/compute/estimates.py` | L4-P2-10, L4-P5-04 | M | `bash metrics/register/validate-sources.sh --compute estimates` |
| 109 | L4-P7-16 | 7 | Ready-queue-miss measure — 30-day rolling count and trend | `metrics/compute/rqm.py` | L4-P5-12, L4-P3-06 | M | `bash metrics/register/validate-sources.sh --compute rqm` |
| 110 | L4-P7-17 | 7 | Status-request count from the event log | `metrics/compute/status_requests.py` | L4-P3-01, L4-P6-01 | S | `bash metrics/register/validate-sources.sh --compute status_requests` |
| 111 | L4-P7-18 | 7 | Onboarding, launch and demo cadence measures | `metrics/compute/lifecycle_cadence.py` | L4-P2-18, L4-P2-19, L4-P2-21 | M | `bash metrics/register/validate-sources.sh --compute lifecycle_cadence` |
| 112 | L4-P7-19 | 7 | Undeclared weekend activations — the residual | `metrics/compute/weekend_residual.py` | L4-P3-01, L4-P2-22 | M | `bash metrics/register/validate-sources.sh --compute weekend_residual` |
| 113 | L4-P7-20 | 7 | Attention-ledger measures | `metrics/compute/attention_measures.py` | L4-P6-15, L4-P7-02 | M | `bash metrics/register/validate-sources.sh --compute attention_measures` |
| 114 | L4-P8-01 | 8 | Write-freshness proved end to end from git commit timestamps | `tools/records/test-freshness-e2e.sh` | L4-P3-04, L4-P4-05 | M | `bash tools/records/test-freshness-e2e.sh` |
| 115 | L4-P8-02 | 8 | DoD matrix runner — all 20 charter rows in one command | `tools/records/run-dod-matrix.sh` | every task above | M | `bash tools/records/run-dod-matrix.sh` |
| 116 | L4-P8-03 | 8 | Lane handoff manifest | `metrics/HANDOFF.md` | L4-P8-02 | S | `bash tools/records/run-dod-matrix.sh --handoff` |
| 117 | L4-P8-04 | 8 | Final rebase and lane PR to `integration` | none (git only) | L4-P8-03 | S | `gh pr view --json state --jq .state` |

---

## 3. Acceptance criteria — what each task's command must prove

Each row below is the complete acceptance criterion for its task. Every criterion is provable by the task's acceptance command in §2, whose expected output is in §4. A criterion is met or it is not; there is nothing to interpret. **Spec anchors are line numbers in `MultiProduct_MasterSpec_v4.0.md`.**

### Phase 0 — lane bootstrap

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-T001 | `ORG` is bound to a real organisation login; you hold `admin` on it; `gh`, `git`, `jq`, `openssl`, `curl` all respond to `--version`; branch `lane/4/p0-preflight` exists. | `PARTITION.md` line 34 |
| L4-T002 | **WITHDRAWN** — superseded by `L4-P1-T02`. | §40.1 lines 3668–3671 |
| L4-T003 | `PROTECTION-REQUEST.md` exists at the records-repo root and states: no review protection; a no-bypass ruleset blocking force-push, branch deletion and tag deletion; **zero bypass actors**. **Blocked by D-L4-TL-6.** | §40.1 line 3677 (D107); `PARTITION.md` line 8 |
| L4-T004 | The three owned roots exist in `control-plane` and contain nothing but `.gitkeep`. | `PARTITION.md` line 20 |
| L4-T005 | `lane-selfcheck.sh --paths` exits 0 on a clean tree and exits 1 when a file is staged outside the three owned roots (the negative case is part of the task). | `PARTITION.md` rule 1, line 25 |
| L4-T006 | Every spec section in `L4-00-charter.md` §8 appears as one CSV row carrying section, line range, obligation and owned path. No row is blank; no row cites a section that does not exist at that line. | `L4-00-charter.md` §8 |
| L4-T007 | A PR from `lane/4/p0-*` to `integration` is open and the lane-guard check is green. | `PARTITION.md` lines 33–35 |

### Phase 1 — the records repository

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P1-T01 | Organisation reachable; caller role is `admin`; `control-plane` has an `integration` branch. | `PARTITION.md` line 33 |
| L4-P1-T02 | Repository `control-plane-records` exists, is private, and has **no** branch-protection object on `main`. | §40.1 line 3671 |
| L4-P1-T03 | Exactly **19** `.gitkeep` files exist: the 17 record store paths of §97.2, plus `events/`, plus `bootstrap/`. | §97.2 lines 8857–8875; §97.3 line 8942 |
| L4-P1-T04 | `README.md`, `CONVENTIONS.md` and `.gitignore` exist at the root. `CONVENTIONS.md` states directory-per-item, never-edit-in-place, UTC-with-offset, the envelope, the split write path, signed commits and retention. `.gitignore` excludes every credential form. | §97.1 lines 8850–8853; §97.2 line 8888 |
| L4-P1-T05 | The branch ruleset on `main` carries exactly the rule types `deletion` and `non_fast_forward`, with **zero** bypass actors. | §40.1 line 3677 |
| L4-P1-T06 | The tag ruleset carries exactly `deletion` and `non_fast_forward`, with **zero** bypass actors. | §40.1 line 3677 |
| L4-P1-T07 | A fast-forward append to `main` succeeds. A force push to `main` is rejected. A delete of `main` is rejected. All three are executed, not asserted. | §40.1 line 3677 |
| L4-P1-T08 | The branch ruleset additionally carries `required_signatures`; the head commit on `main` reports `verification.verified == true`; an unsigned local commit is rejected. **Blocked by `L4-01-records-repo.md` D-L4-02.** | §40.1 line 3680 |
| L4-P1-T09 | The `records-writer` App exists with permissions **exactly** `{"contents":"write","metadata":"read"}`. The private key is outside every git working tree, mode 700 directory. | §40.1 line 3671; D89 line 3664 |
| L4-P1-T10 | Installation `repository_selection` is `selected`; the installation reaches exactly **1** repository. | §40.1 line 3671 |
| L4-P1-T11 | The App appends a record-shaped file and an event-shaped file under a date partition. The App **cannot read** `control-plane` (HTTP 404), **cannot write** it, and **cannot approve** anything. All five attempts are executed. | §40.1 lines 3664, 3671; §97.1 line 8853 |
| L4-P1-T12 | Both ruleset JSONs and the credential shape are committed under `tools/records/`; `rw-token.sh` is present and executable; nothing outside `tools/records/` is staged. | `PARTITION.md` line 20 |

### Phase 2 — record and event schemas

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P2-01 | `check.sh` is byte-identical to §0.6. Running it on a task id with no check file prints `CHECK <id> ERROR no-check-file` and exits 3. `CONTRACT.md` transcribes §0.5. | §0.5 of this file |
| L4-P2-02 | `requirements.txt` pins every dependency with `==`. `validate-schemas.sh --selftest` proves the loader rejects a syntactically invalid schema. **Blocked by D-L4-TL-1.** | §101 invariant 85; §99.1 line 9195 |
| L4-P2-03 | The timestamp definition accepts UTC-with-offset and rejects: a naive local time, a date-only value, an offset-free `Z`-less string, and a value carrying a non-UTC offset without an explicit offset field. Four negative cases, all executed. | §97.1 line 8851 |
| L4-P2-04 | The record envelope **requires** `record_schema_version`, `id`, `product`, `timestamp`. An absent `record_schema_version` reads as version 1. Records never edit in place — the schema forbids a `supersedes_in_place` style field and the check asserts its absence. **Blocked by D-L4-TL-5B.** | §97.2 lines 8888–8890 |
| L4-P2-05 | The event envelope **requires** all nine fields: `event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`, `subject_ref`, `payload`. An event missing any one is rejected. `event_type` is constrained to an identifier pattern, never free text. **Blocked by D-L4-TL-5B.** | §97.3 lines 8944–8960 |
| L4-P2-06 | `store-inventory.yaml` lists exactly the 17 record store paths of the §97.2 table: `records/incidents/`, `records/postmortems/`, `records/uat/`, `records/estimates/`, `records/deployments/`, `records/restore-tests/`, `records/decisions/`, `records/decisions/pending/`, `records/breaches/`, `records/deletion-requests/`, `records/security-reviews/`, `records/eval/`, `records/launches/`, `records/demos/`, `records/support/`, `records/onboarding/`, `records/leave/`. Each row names its writer and what it generates, transcribed from the table. | §97.2 lines 8857–8875 |
| L4-P2-07 | `incident.schema.json` extends the record envelope and requires `severity`, `detected`, `detection_source` (enum exactly `alert`, `customer`, `internal`, `support_intake`), `responded`, `resolved`, `customer_impact`, `resolution`, `postmortem`, `pre_onboarding`. | §97.2 lines 8894–8905 |
| L4-P2-08 | `postmortem.schema.json` carries generated learning-loop items each with an open/closed state and a link to a regression-test item where the incident was a production bug. | §58.4 lines 5026–5056; §52.2 line 4577 |
| L4-P2-09 | `uat.schema.json` carries the executed result, the `verification/uat.md` reference, and whether the result arrived by CI or by the RECORD-VERIFICATION-RESULT dispatch. | §97.2 lines 8861, 8884 |
| L4-P2-10 | `estimate.schema.json` requires the band **label** and the representative **point value in force when written**, plus `elapsed` **and** `elapsed_net_blocked`, as two distinct fields. | §29.3 line 2669; §97.2 line 8862 |
| L4-P2-11 | `deployment.schema.json` requires `id`, `product`, `digest`, `approved_by`, `approval_event`, `staging_verified`, `uat_record`, `smoke_result`, `rollback_of`. | §97.2 lines 8907–8917 |
| L4-P2-12 | `restore-test.schema.json` carries the test result, the recorded `integrity_check` result and the named verifier, and the source (workflow or RECORD-VERIFICATION-RESULT confirmation). | §44.3 lines 4007–4015; §53.1 line 4680 |
| L4-P2-13 | `decision.schema.json` requires `id`, `decider`, `prompt_received`, `decided`, `subject`, `options_considered`, `evidence`, `review_date`, and a `state` of `pending` or `decided`. | §97.2 lines 8919–8925 |
| L4-P2-14 | `breach.schema.json` carries the classification event and the notification deadline against which compliance is measured. | §97.2 line 8867 |
| L4-P2-15 | `deletion-request.schema.json` requires all four timestamps `requested`, `verified`, `executed`, `confirmed`; the **named executor**; the **subprocessor propagation checklist** (each subprocessor with its own deletion confirmation); and the **backup carve-out policy statement**. | §97.2 line 8882; AT-105 line 9388 |
| L4-P2-16 | `security-review.schema.json` carries findings, each with `severity` and `disposition`; any finding with disposition `unfixed` requires an owner and a date for the Portfolio Debt Inventory link. | §97.2 line 8882 |
| L4-P2-17 | `eval.schema.json` carries per-dimension scores, each dimension's recorded baseline, and the declared tolerance the regression is measured against. | §38.3 line 3433; §52.2 line 4577 |
| L4-P2-18 | `launch.schema.json` carries the launch-readiness evidence references assembled at sign-off. | §97.2 line 8871 |
| L4-P2-19 | `demo.schema.json` requires `id`, `product`, `customer`, `given_by`, `duration_minutes`, `outcome`. | §97.2 lines 8927–8933 (the `records/demos/…yaml` example) |
| L4-P2-20 | `support.schema.json` requires `detection_source` whose enum **includes** `founder_direct` and `customer` alongside the intake channels, and a `received_at` field distinct from the ingest timestamp, so the first-response clock anchors to the message's received timestamp. | §97.2 line 8888; §103.4 (D80 note); AT-104 line 9387 |
| L4-P2-21 | `onboarding.schema.json` carries the phase completed, whether it was machine- or human-written, and the first-accepted-PR reference where the phase produces one. | §97.2 line 8874 |
| L4-P2-22 | `leave.schema.json` carries the declared working calendar and operating timezone that every business-day rule resolves against, and the calendar **version**. | §6.4 lines 446–454; §97.1 line 8851 |
| L4-P2-23 | `agent_authored` is a required boolean on change records and PR records. `detection_source` is defined once and referenced, never redeclared per store. | §97.2 line 8886 |
| L4-P2-24 | A deletion-request record missing any one of the four timestamps, the executor, the checklist, or the carve-out statement is rejected. Six negative cases. | AT-105 line 9388 |
| L4-P2-25 | A security-review record carrying an `unfixed` finding with no owner or no date is rejected. | §97.2 line 8882 |
| L4-P2-26 | Exactly one valid golden fixture exists per store in `store-inventory.yaml`, and every one validates. | §0.8 rule 3 |
| L4-P2-27 | Exactly **10** invalid event fixtures exist: one per missing envelope field (9) plus one carrying an `event_type` absent from the enum (1). All 10 are rejected. | §97.3 lines 8944–8960 |
| L4-P2-28 | Every schema file appears in `versions.yaml` with its version; `VERSIONS.md` states that record and event schemas are versioned contracts under §60.2 and that a retired version is marked, never removed. | §97.2 line 8888; §60.2 |
| L4-P2-29 | Every schema named in `store-inventory.yaml` plus both envelopes plus the timestamp definition load and validate. No store lacks a schema; no schema lacks a store. | `L4-00-charter.md` DoD-2 |

### Phase 3 — taxonomy, freshness, signals, anchor, retention

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P3-01 | Every entry in the §97.3 tracked-events list (lines 8962–8966) has exactly one identifier: lower-case, underscore-separated, matching `^[a-z][a-z0-9_]*$`. No identifier appears twice. No entry is unmapped. The file states that an identifier is never renamed once shipped. | §97.3 lines 8960–8966 |
| L4-P3-02 | Every identifier in `event-types.yaml` has exactly one payload declaration file under `metrics/taxonomy/payloads/`, named for the identifier. No orphan payload file; no identifier without one. Directory-per-item — the payloads are never one shared file. | §97.3 line 8958; `PARTITION.md` rule 3 |
| L4-P3-03 | Marking an identifier `retired: true` is accepted; removing an identifier that previously shipped is rejected. `validate-taxonomy.sh` proves both. | §97.3 line 8961 |
| L4-P3-04 | Every store in `store-inventory.yaml` declares an expected maximum inter-write interval. Exactly **3** are marked Blocking: `events/`, `records/deployments/`, `records/uat/`. Every other store is Amber past its interval. The value is computed from git commit timestamps on the store's path, not from any other health input. | §97.2 line 8880; §53.1 line 4679 |
| L4-P3-05 | The anchor schema requires the records repository default-branch head SHA and the commit count, and states that a head not descending from the last anchored SHA is Blocking drift, Level 5. L4 writes the schema only; the reconciler that writes anchors is L3's. | §40.1 line 3681; §53.2 |
| L4-P3-06 | Each of SIG-06, SIG-17, SIG-41, SIG-42, SIG-43, SIG-46, SIG-47 maps to exactly one L4 store. The learning-loop row is emitted with `signal_id: SIG-47` (D-L4-TL-4 decided). No signal id is mapped twice. | §52.2 lines 4541, 4552, 4576, 4577, 4581 |
| L4-P3-07 | Every store declares a retention class. Canonical records — state, decisions, approvals — declare append-only permanence with effective dating. Raw activity telemetry declares a diagnostic window after which it may be aggregated or discarded. No store is unclassified. | §97.6 lines 9001–9004; §101 invariants 47–48, lines 9527–9529 |

### Phase 4 — writers and the dispatch handler

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P4-01 | The clock emits UTC with offset only; a call that would emit a runner-local time raises. Ids are minted to the store's declared pattern. | §97.1 line 8839 |
| L4-P4-02 | Writing to a path that already exists is refused with exit 1 and no file is modified. Executed against a real existing file, not mocked. | §101 invariant 48, line 9529 |
| L4-P4-03 | `record-write` validates against the store's schema **before** writing, writes exactly one new file, and refuses to modify an existing one. A schema-invalid record is refused with exit 1 and nothing is written. | §97.2 lines 8890–8892 |
| L4-P4-04 | Event paths are `events/<YYYY-MM-DD>/<event_id>.yaml` — one file per event, never a concurrent append to a shared period file. Two events on the same date produce two files. | §97.3 line 8929 |
| L4-P4-05 | `event-append` rejects an event missing any envelope field and rejects an `event_type` absent from `event-types.yaml`, both **at write time**, before any file is created. | §97.3 lines 8931–8947 |
| L4-P4-06 | The handler accepts exactly the structured inputs **product, item, mechanism, pass-or-fail, evidence link**; writes the corresponding record; appends the event; and exposes no path that edits a record file by hand. A call with a missing input is refused. | §97.2 line 8886 |
| L4-P4-07 | Opening a decision prompt writes to `records/decisions/pending/`; deciding writes a new file to `records/decisions/` and marks the pending record superseded by a follow-up record, never by editing it. | §97.2 lines 8865–8866; §99.2 tool table line 9230 |
| L4-P4-08 | With the records repository reachable the reader returns records. With it unreachable the reader exits non-zero and prints `FAIL-CLOSED`; it **never** returns zero rows as a success. | §40.1 line 3671 |
| L4-P4-09 | Four negatives all executed: hand-edit of an existing record is refused; an in-place correction is refused; an unvalidated record is refused; an untyped event is refused. | §0.8 rules 3 and 7 |
| L4-P4-10 | Every writer obtains its credential through `rw-token.sh` and never through a literal token. A writer invoked with no token available exits 3, not 0. | §97.1 line 8841; §40.1 line 3665 |

### Phase 5 — work tracking conventions and the Ready-queue-miss detector

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P5-01 | The declared flow is exactly `Backlog → Ready → Planned → In Progress → In Review → Verify → Done`. **Blocked** is declared a flag on any in-flight column, never a column. **Deploy** is declared rendered from deployment records, never hand-moved. | §29.1 lines 2625–2631 |
| L4-P5-02 | H1 contains the in-flight columns plus the Deploy stage plus any Blocked item and is **Committed**; H2 is **Prepared**; H3 is **Candidate**. An item entering H1 without H2 preparation carries `unplanned`. | §29.2 lines 2643–2654 |
| L4-P5-03 | The Ready definition carries all ten criteria of §29.3: clear requirement; product identified; priority; intended person; verification path; dependencies understood; architecture decisions resolved; impact scope proposed; acceptance criteria; enough context to begin. An item missing any one is not Ready. | §29.3 lines 2655–2669 |
| L4-P5-04 | Estimate capture fires at the Ready **confirmation** transition and nowhere else; it records band label and point value in force; spikes, incidents and debt-remediation items are exempt and produce no estimate record. | §29.3 line 2667 |
| L4-P5-05 | Every emitted RQM event carries the full §29.4 field set: who, which date, which product, why the queue was empty, whether the Team Lead was blocked, whether product priority changed recently. | §29.4 lines 2670–2673 |
| L4-P5-06 | A board transition from Backlog directly to Planned or In Progress, **or** an item started while the product's Ready queue is empty, emits a Ready-queue-miss event. | §97.5 line 8997 |
| L4-P5-07 | A completion transition where the product's Ready queue holds no suitable item for that person emits a Ready-queue-miss event, with no pickup involved. | §97.5 line 8999 |
| L4-P5-08 | `Ready → Planned → In Progress` emits nothing. Passing through Planned is never a miss. | §97.5 line 8997 |
| L4-P5-09 | Clearing the Blocked flag and resuming an item emits nothing. It is a resumption, never a fresh pickup. | §97.5 line 8997 |
| L4-P5-10 | A Backlog-to-Planned or Backlog-to-In-Progress transition made **while suitable Ready items exist** is recorded with reason `ready_bypass` and is **excluded** from the SIG-06 count. Both limbs proved: the record exists, and the SIG-06 count does not move. | §97.5 line 8999; §52.2 line 4541 |
| L4-P5-11 | The last three §29.4 fields are populated from the cause prompt only. A run with no cause prompt leaves them absent — never inferred, never defaulted. | §97.5 line 8999 |
| L4-P5-12 | Six cases pass: limb 1, limb 2, Planned carve-out, Blocked carve-out, `ready_bypass`, full field set. | `L4-00-charter.md` DoD-8 |
| L4-P5-13 | The re-plan event links to the item's estimate record, and the item carries the Blocked flag with reason `re-plan` while execution is stopped. | §29.5 lines 2699–2701 |

### Phase 6 — the attention ledger

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P6-01 | Exactly eight categories: Engineering, Review, Verification, Planning, Architecture, Incident, Operational, Coordination. A ninth is rejected. Exactly one category per hour. | §67.2 lines 5586–5604; §67.1 line 5580 |
| L4-P6-02 | Each of the eight categories names its derived-from source, transcribed from the §97.4 table. No category is sourceless. | §97.4 lines 8967–8994 |
| L4-P6-03 | Consecutive events separated by no more than the idle gap form one session; a wider gap ends it. Session duration is first-event to last-event. A single-event session counts as one granularity unit. **Elapsed wall-clock between interval bounds is never an attention hour.** The idle gap is declared calibrated configuration with initial value **30 minutes**. | §97.4 lines 8970–8972 |
| L4-P6-04 | Granularity is calibrated configuration with initial value **0.25 hours**, rounded to **nearest**, and **never to zero**. A session shorter than half a unit still yields one unit, not zero. | §97.4 line 8973 |
| L4-P6-05 | A session inside two windows resolves in exactly this order, losing categories receiving nothing: Incident, Verification, Review, Engineering, Architecture, Planning, Operational, Coordination. | §97.4 line 8974 |
| L4-P6-06 | One product touched → attributes there. Several → splits **by event count**. None → attributes to the portfolio. | §97.4 line 8975 |
| L4-P6-07 | Derived hours for a person on a day never exceed that person's scheduled availability for that day. Sessions truncate in **reverse precedence order** until the reconciliation holds, and **each truncation is recorded**. | §97.4 line 8976 |
| L4-P6-08 | A day exceeding scheduled availability **before** truncation raises a drift finding against the ledger and enters **no** Capacity Profile, **no** workload state and **not** the Founder view. It is an instrument defect, never a workload finding. | §97.4 line 8977 |
| L4-P6-09 | `unplanned` and `ritual` are flags on an entry, never categories. A ritual review hour is still a Review hour. The `ritual` flag is set by the workflow or record that opens the ritual and is never self-reported. | §67.2 line 5592; §57.2 lines 4965–4970 |
| L4-P6-10 | Self-report intake accepts **one band per category, weekly, unattributed to any product**. It never accepts minutes, never accepts a daily entry, and never asks for per-product attribution. | §97.4 line 8980 |
| L4-P6-11 | The week's band is apportioned across that person's products in proportion to their machine-derived activity shares for the same week, and to the portfolio where no share exists. | §97.4 line 8980 |
| L4-P6-12 | The declared collection cost per person per week is asserted at or under **5 minutes**. A design exceeding it fails the check rather than being accepted. | §67.3 line 5605; §97.4 line 8980 |
| L4-P6-13 | Any figure including self-reported hours carries a `self-reported` provenance label, and the label is **permanent** — no code path removes it, and the check proves removal is impossible by asserting the label survives aggregation, apportionment and rendering. | §97.4 line 8980 |
| L4-P6-14 | The limitations file states: the attention hour is a **lower bound**; Architecture and Coordination are systematically under-counted; the idle gap and granularity are hypotheses until calibrated; calibration runs once at Phase G3 with at least two people band-reporting one week in parallel; the divergence is the stated error bar. | §97.4 line 8981 |
| L4-P6-15 | Every criterion L4-P6-01 through L4-P6-14 passes in one run. | `L4-00-charter.md` DoD-6, DoD-7 |

### Phase 7 — the metric register and the §103 computations

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P7-01 | Every declared measure carries all **eight** attributes: definition; source; time window; baseline; expected interpretation; known limitations; owner; defined action on breach. A measure carrying seven is rejected. | §84.6 line 7479; §103 preamble line 9789 |
| L4-P7-02 | Every measure names the record store it derives from. A measure that cannot name its store is **absent from the register**, not present-and-flagged. | §103 preamble line 9789; §101 invariant 46, line 9527 |
| L4-P7-03 | An empty or not-yet-baselined store renders the measure `unbaselined`. It never renders as a miss, never as zero, and an unarmed measure cannot fail. | §103 preamble line 9789 (D77); §52.2 line 4530 |
| L4-P7-04 | Every §103.13 measure carries either a recorded baseline estimate or an explicit `unbaselined` marker. The five-member minimum baseline set is present and each member is labelled a banded pre-Phase-1 estimate, never mixed with ledger-derived data. | §103.14 lines 9988–9990; AT-046 line 9381 |
| L4-P7-05 | Every measure has an owner and a defined response, or it is absent from the register. | §101 invariant 49, line 9530 |
| L4-P7-06 | Deployment frequency, deployment failure rate, rollback rate and merged-but-not-deployed all name `records/deployments/` (the last also naming merge events) and compute from it, never from a hand-maintained number. | §103.2 lines 9791–9798; §32 lines 2803–2829 |
| L4-P7-07 | MTTR, incident frequency by severity, and detection-to-response latency all name `records/incidents/`. Detection-to-response is interpreted against each product's declared `support_model`. | §103.3 lines 9805–9809 |
| L4-P7-08 | Restore freshness computes against the rolling 90-day floor and the tightened cadence the product's `classification.reliability_criticality` requires. Failed restore tests target zero and name `records/restore-tests/`. | §44.2 lines 3993–4002; §103.3 lines 9810–9811 |
| L4-P7-09 | UAT coverage and pass rate name `records/uat/`. | §97.2 line 8848 |
| L4-P7-10 | Support load names `records/support/`. First-response time by severity anchors the clock to the message's **received timestamp**, never to the ingest event. | §103.4 line 9825; §22.4 lines 2238–2249; AT-104 line 9387 |
| L4-P7-11 | Eval pass rates name `records/eval/`. A scored dimension falling more than its declared tolerance below its recorded baseline is a regression and raises SIG-42. A night's regressions on one product coalesce into **one** triage, never one per dimension. | §52.2 line 4571; §38.3 lines 3433–3434; AT-107 line 9390 |
| L4-P7-12 | Finding count by severity and unfixed-finding age name `records/security-reviews/`. Unfixed findings age visibly rather than silently. | §97.2 lines 8858, 8884; §52.2 line 4575 |
| L4-P7-13 | Decision latency names `records/decisions/`. Pending-decision queue depth and age name `records/decisions/pending/`. | §97.2 lines 8865–8866; §103.13 line 9972 |
| L4-P7-14 | An open postmortem older than 30 days with unclosed generated items, or a closed production-bug incident with no linked regression-test item, is counted. Emitted under `signal_id: SIG-47` (D-L4-TL-4 decided; unblocked). | §52.2 line 4571; §58.4 lines 5017–5047 |
| L4-P7-15 | Estimation accuracy uses **elapsed net of recorded Blocked time**; forecast calibration uses **raw elapsed**. Both figures come from the record and the two are never confused. | §29.3 line 2667; §97.2 line 8850 |
| L4-P7-16 | The Ready-queue-miss measure is a 30-day rolling count and trend, excludes `ready_bypass` events, and is declared a Team Lead capacity signal, never an individual signal. | §52.2 line 4541; §29.4 line 2670; §101 invariant 15, line 9484 |
| L4-P7-17 | Status requests are counted from Coordination-category status-request events in the event log, weekly, derived and never hand-counted. | §103.13 line 9969 |
| L4-P7-18 | Onboarding time to first accepted PR names `records/onboarding/`. Launch cadence names `records/launches/`. Demo cadence names `records/demos/`. | §97.2 lines 8871–8874 |
| L4-P7-19 | The measure is the **residual**: out-of-hours state-changing events in the event log, measured against each person's declared working calendar, **minus** the activations recorded in the exception registry. It reports at team level and never names a person. | §103.3 line 9812 |
| L4-P7-20 | Founder coordination time, Team Lead coordination hours, engineering hours per product per month, QA verification hours and Founder total OS ritual hours all name the attention ledger and carry the `self-reported` label wherever a self-reported component is included. | §103.13 lines 9962–9982 |

### Phase 8 — lane acceptance and handoff

| ID | Acceptance criteria | Spec anchor |
| --- | --- | --- |
| L4-P8-01 | Freshness is computed from real git commit timestamps on a real store path, proved for one Amber store and one Blocking store, and proved to still compute when every other health input is removed. | §97.2 line 8873 |
| L4-P8-02 | All **20** DoD rows of `L4-00-charter.md` §7 are executed in one run and all pass. Any row that cannot execute exits 3, never 0. | `L4-00-charter.md` §7 |
| L4-P8-03 | `HANDOFF.md` names, per consumer lane, the exact artifact paths L2, L3, L1 and L0 consume, with no artifact left unnamed. | `L4-00-charter.md` §5 |
| L4-P8-04 | The final lane PR to `integration` is open, the lane-guard check is green, and no file outside the three owned roots appears in the diff. | `PARTITION.md` rule 1, line 25 |

---

## 4. SELF-VERIFY — expected output

### 4.1 Universal rule, tasks `L4-P2-01` and later

Every task from `L4-P2-01` onward is self-verified by §0.6. Run with `--audit` first to prove the check file meets minimum requirements, then run normally:

```bash
set -euo pipefail
cd "$CP_DIR" && bash tools/records/check.sh --audit <TASK-ID>; echo "audit=$?"
cd "$CP_DIR" && bash tools/records/check.sh <TASK-ID>; echo "exit=$?"
```

```
CHECK <TASK-ID> PASS
exit=0
```

Substitute the task's own id. Two lines, nothing else. Anything else is a STOP under §0.7.

### 4.2 Named summary lines — the charter DoD surfaces

These acceptance commands print a named summary line instead of, and in addition to, the dispatcher line. Both must be seen.

| Command | Expected stdout, exactly | Exit |
| --- | --- | --- |
| `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` | 0 |
| `bash tools/records/lane-selfcheck.sh --stores` | `STORES OK 17/17` | 0 |
| `bash tools/records/validate-schemas.sh` | `SCHEMAS OK` | 0 |
| `bash tools/records/validate-schemas.sh --negative` | `NEGATIVE OK 10/10` | 0 |
| `bash tools/records/validate-schemas.sh --fields` | `FIELDS OK` | 0 |
| `bash tools/records/validate-schemas.sh --time` | `TIME OK` | 0 |
| `bash tools/records/validate-schemas.sh --at105` | `AT-105 OK` | 0 |
| `bash tools/records/validate-schemas.sh --at046-secreview` | `SECREVIEW OK` | 0 |
| `bash tools/records/validate-taxonomy.sh` | `TAXONOMY OK` | 0 |
| `bash tools/records/validate-freshness.sh` | `FRESHNESS OK BLOCKING=3` | 0 |
| `bash tools/records/validate-retention.sh` | `RETENTION OK` | 0 |
| `bash tools/records/test-rvr.sh` | `RVR OK` | 0 |
| `bash tools/records/test-rqm-detector.sh` | `RQM OK 6/6` | 0 |
| `bash tools/records/test-read-across.sh --unreachable` | `FAIL-CLOSED` | non-zero |
| `bash metrics/attention/test-derivation.sh` | `ATTENTION OK` | 0 |
| `bash metrics/attention/test-derivation.sh --provenance` | `PROVENANCE OK` | 0 |
| `bash metrics/register/validate-sources.sh` | `SOURCES OK` | 0 |
| `bash metrics/register/validate-sources.sh --arming` | `ARMING OK` | 0 |
| `bash metrics/register/validate-sources.sh --at046` | `AT-046 OK` | 0 |

`test-read-across.sh --unreachable` is the one command in this lane whose **pass is a non-zero exit**. That is the fail-closed property of §40.1 line 3671 and is correct. A zero exit there is a STOP.

### 4.3 Phases 0 and 1 — per-task SELF-VERIFY

These predate the dispatcher. Run the command; the output must match the Expected column exactly.

| ID | SELF-VERIFY command | Expected stdout, exactly |
| --- | --- | --- |
| L4-T001 | `gh api "/orgs/${ORG}" --jq .login` | the value of `$ORG` |
| L4-T002 | `gh api "/repos/${RECORDS_SLUG}" --jq .private` | `true` |
| L4-T003 | `gh api "/repos/${RECORDS_SLUG}/contents/PROTECTION-REQUEST.md" --jq .name` | `PROTECTION-REQUEST.md` |
| L4-T004 | `ls -1d schemas/records metrics tools/records \| wc -l` | `3` |
| L4-T005 | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |
| L4-T006 | `bash tools/records/lane-selfcheck.sh --coverage` | `COVERAGE OK` |
| L4-T007 | `gh pr view --json state --jq .state` | `OPEN` |
| L4-P1-T01 | `gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq .role` | `admin` |
| L4-P1-T02 | `gh api "/repos/${RECORDS_SLUG}/branches/main/protection" >/dev/null 2>&1 && echo yes \|\| echo no` | `no` |
| L4-P1-T03 | `gh api "/repos/${RECORDS_SLUG}/git/trees/main?recursive=1" --jq '[.tree[]\|select(.path\|endswith(".gitkeep"))]\|length'` | `19` |
| L4-P1-T04 | `gh api "/repos/${RECORDS_SLUG}/contents/CONVENTIONS.md" --jq .name` | `CONVENTIONS.md` |
| L4-P1-T05 | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq -c '[.rules[].type]\|sort'` | `["deletion","non_fast_forward"]` |
| L4-P1-T06 | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq -c '[.rules[].type]\|sort'` | `["deletion","non_fast_forward"]` |
| L4-P1-T07 | `git push --force origin HEAD:main >/dev/null 2>&1 && echo ALLOWED \|\| echo REJECTED` | `REJECTED` |
| L4-P1-T08 | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified` | `true` |
| L4-P1-T09 | `gh api "/apps/${APP_SLUG}" --jq -c .permissions` | `{"contents":"write","metadata":"read"}` |
| L4-P1-T10 | `curl -sS -H "Authorization: Bearer ${RW_TOKEN}" -H 'Accept: application/vnd.github+json' https://api.github.com/installation/repositories \| jq -r '.total_count'` | `1` |
| L4-P1-T11 | `curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${RW_TOKEN}" -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/${CP_SLUG}/contents/README.md"` | `404` |
| L4-P1-T12 | `bash tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |

---

## 5. Phase exit gates

A phase is not finished until its gate passes. Do not start the next phase until it does. A gate failure is a STOP under §0.7 with `<TASK-ID>` set to `EXIT-GATE-P<n>`.

| Gate | Command | Expected final line |
| --- | --- | --- |
| P0 | `bash tools/records/lane-selfcheck.sh --paths && bash tools/records/lane-selfcheck.sh --coverage` | `COVERAGE OK` |
| P1 | the twelve-check exit gate transcribed in `L4-01-records-repo.md` §"Phase exit gate" | `L4 PHASE 1 EXIT GATE: PASS` |
| P2 | `bash tools/records/validate-schemas.sh && bash tools/records/validate-schemas.sh --negative && bash tools/records/lane-selfcheck.sh --stores` | `STORES OK 17/17` |
| P3 | `bash tools/records/validate-taxonomy.sh && bash tools/records/validate-freshness.sh && bash tools/records/validate-retention.sh` | `RETENTION OK` |
| P4 | `bash tools/records/test-writers.sh && bash tools/records/test-rvr.sh && bash tools/records/test-read-across.sh --unreachable \|\| true` | `FAIL-CLOSED` |
| P5 | `bash tools/records/validate-boards.sh && bash tools/records/test-rqm-detector.sh` | `RQM OK 6/6` |
| P6 | `bash metrics/attention/test-derivation.sh && bash metrics/attention/test-derivation.sh --provenance` | `PROVENANCE OK` |
| P7 | `bash metrics/register/validate-sources.sh && bash metrics/register/validate-sources.sh --arming && bash metrics/register/validate-sources.sh --at046` | `AT-046 OK` |
| P8 | `bash tools/records/run-dod-matrix.sh` | `DOD OK 20/20` |

---

## 6. Charter Definition-of-Done → task map

Every row of `L4-00-charter.md` §7 is discharged by the tasks named. No DoD row is unowned.

| DoD | Discharged by |
| --- | --- |
| DoD-1 stores exist | L4-P1-T03, L4-P2-06 |
| DoD-2 a schema per store | L4-P2-04, L4-P2-07…L4-P2-22, L4-P2-29 |
| DoD-3 envelope negatives | L4-P2-05, L4-P2-27 |
| DoD-4 event-type taxonomy | L4-P3-01, L4-P3-02, L4-P3-03 |
| DoD-5 write freshness, 3 Blocking | L4-P3-04 |
| DoD-6 attention derivation | L4-P6-01…L4-P6-09, L4-P6-15 |
| DoD-7 self-reported provenance | L4-P6-10…L4-P6-13 |
| DoD-8 Ready-queue-miss detector | L4-P5-05…L4-P5-12 |
| DoD-9 RECORD-VERIFICATION-RESULT | L4-P4-06 |
| DoD-10 `detection_source`, `agent_authored` | L4-P2-20, L4-P2-23 |
| DoD-11 deletion-request AT-105 | L4-P2-15, L4-P2-24 |
| DoD-12 security-review findings | L4-P2-16, L4-P2-25 |
| DoD-13 every measure names its store | L4-P7-01, L4-P7-02 |
| DoD-14 `unbaselined`, never a miss | L4-P7-03 |
| DoD-15 baseline or explicit marker | L4-P7-04 |
| DoD-16 read-across fails closed | L4-P4-08 |
| DoD-17 no file outside owned paths | L4-T005, run before every commit; L4-P8-04 |
| DoD-18 UTC with offset | L4-P2-03, L4-P4-01 |
| DoD-19 retention classes | L4-P3-07 |
| DoD-20 everything merged to `integration` | L4-P8-04 |

---

## 7. What Lane 4 does not build — do not attempt any of these

| Not built here | Owner | Why |
| --- | --- | --- |
| The workflows that **call** L4 writers, including the required failing record-write steps of `deploy-production.yml` | L2 | `.github/workflows/**` is L2's path (`PARTITION.md` line 18); §97.2 line 8875 |
| The reconciler that writes the head-SHA anchor and compares write-freshness windows | L3 | `reconciler/**`, `validators/drift/**` are L3's paths; §40.1 line 3679; §53.1 line 4677 |
| The `event_type` enum **inside** `registries/platform.yaml`, and metric metadata **inside** `registries/os-health.yaml` | L1 | `registries/**` is L1's path (`PARTITION.md` line 17); §97.3 line 8947; §52.6 line 4626 |
| The records-writer credential's operational-asset-inventory entry and ops-VM custody | L5 | `assets/**`, `ops-vm/**` are L5's paths; §40.1 line 3684 |
| Grafana dashboards, DevLake ingest configuration, Prometheus scrape configuration | L5 / H | §99.6 risk 2 — records first, dashboards after |
| Any change to `contracts/**` | L0 | Contract-first, `PARTITION.md` rule 2, line 26 |

---

**End of L4-06.** Work the §2 table top to bottom. Verify with §4. Gate with §5. Stop with §0.7.
