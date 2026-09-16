# L4-07 — PHASE 7: TEST STRATEGY AND DAILY RUNBOOK

**Lane:** L4 — Records, Events and Metrics (Subsystems **I** metrics pipeline, **N** work tracking conventions — MasterSpec §99.2, lines 9184–9231)
**Branch prefix:** `lane/4/*`
**Paths this lane owns exclusively (PARTITION.md line 20, FROZEN):** ALL of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` in the `control-plane` repository.
**This document covers:** the L4 test strategy — fixture corpora, round-trip tests, negative tests, derivation tests, acceptance-test proofs — and the literal daily runbook for a lane that works across **two** repositories.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

**Why a whole phase for tests.** §53.1 line 4680 states the seeded-canary rule: *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking, not that nothing drifted."* Every artifact L4 ships is an instrument. §97.2 line 8867 states why an unexercised instrument is worse than none: *"a workflow whose record-write step fails silently renders every count-shaped derived metric as zero — no ready-queue misses, no anomalies, no regressions — which is indistinguishable from health."* §99.6 risk 2 is the lane's reason to exist and it fails in exactly this shape: dashboards that ship empty look identical to dashboards that ship clean. This phase makes each L4 instrument prove it can fail.

---

## 0. Reader contract

You are executing, not designing. Every command below is literal and copy-pasteable. Run them in **Git Bash** (POSIX `sh`), **not** `cmd.exe` and **not** PowerShell.

If any step requires you to choose, name, invent, or interpret something that is not written here, **STOP** and file a blocker (§0.4). Do not guess. Do not substitute a similar command. Do not "fix" a failing acceptance check by relaxing it, by editing the expected-output file, or by deleting a fixture.

**A failing test in this phase is almost never this phase's bug.** These tests exercise artifacts built in L4 Phases 1–6. When an assertion fails, the correct action is a blocker naming the artifact and the phase that owns it — not a repair. You have no authority to edit `schemas/records/**` or `metrics/**` content in this phase; you may only add files under the paths §0.5 lists.

### 0.1 Environment — set once per shell, before every task

```bash
set -euo pipefail
# ---- L0-supplied parameter (D-L4-01 in L4-01-records-repo.md). ----
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

# ---- Fixed by this document. Do not change. ----
export CP_REPO="control-plane"
export RECORDS_REPO="control-plane-records"
export CP_SLUG="${ORG}/${CP_REPO}"
export RECORDS_SLUG="${ORG}/${RECORDS_REPO}"
export WORK="$HOME/l4work"
export CP_DIR="${WORK}/${CP_REPO}"
export RECORDS_DIR="${WORK}/${RECORDS_REPO}"
export L4_TMP="${WORK}/tmp"            # throwaway sandboxes; never a git working tree of a real repo
export L4_BRANCH="lane/4/07-tests-and-runbook"
mkdir -p "$L4_TMP"

# ---- Aliases for the names used in L4-00-charter.md. Same directories. ----
export CP_ROOT="$CP_DIR"
export CPR_ROOT="$RECORDS_DIR"

echo "ORG=$ORG CP_DIR=$CP_DIR RECORDS_DIR=$RECORDS_DIR L4_TMP=$L4_TMP"
```

If `ORG` prints as the literal placeholder, **STOP** — D-L4-01 has not been answered and nothing in this phase runs.

### 0.2 External preconditions — verify, never create

| Id | Precondition | Owner | Verify command | Required by |
|---|---|---|---|---|
| P7-EXT-01 | `python3` ≥ 3.9 present | you | `python3 --version` | T02 onward |
| P7-EXT-02 | PyYAML importable | you | `python3 -c "import yaml; print('PYYAML OK')"` | T03 onward |
| P7-EXT-03 | `jq` present | you | `jq --version` | T02 onward |
| P7-EXT-04 | `git` and `gh` present | you | `git --version && gh --version` | T01, T13 |
| P7-EXT-05 | `control-plane` cloned at `$CP_DIR` with `origin/integration` resolvable | L0 | `git -C "$CP_DIR" rev-parse --verify origin/integration` | T01 |
| P7-EXT-06 | `control-plane-records` cloned at `$RECORDS_DIR` on `main` | L4 Phase 1 (`L4-P1-T02`) | `git -C "$RECORDS_DIR" rev-parse --abbrev-ref HEAD` → `main` | T01 |
| P7-EXT-07 | `contracts/` present in `control-plane` | L0 Phase 0 | `test -d "$CP_DIR/contracts" && echo YES` | T01 |

If any precondition fails, **STOP** and file a blocker naming the precondition id. Do not create another lane's artifact and do not clone a repository this phase did not create.

### 0.3 Task index

| Task id | Title | Size | Depends on |
|---|---|---|---|
| `L4-P7-T01` | Entry gate — inventory the Phase 1–6 artifacts this phase tests | S | — |
| `L4-P7-T02` | Test harness skeleton and the runner contract | M | `L4-P7-T01` |
| `L4-P7-T03` | Fixture corpus A — the five verbatim-spec valid fixtures | M | `L4-P7-T02` |
| `L4-P7-T04` | Fixture corpus B — the writer-generated valid corpus, all 19 stores | M | `L4-P7-T03` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| `L4-P7-T05` | Suite 1 — schema round-trip and the absent-version read rule | M | `L4-P7-T04` |
| `L4-P7-T06` | Suite 2 — the ten envelope negatives | M | `L4-P7-T03` |
| `L4-P7-T07` | Suite 3 — the five D88 display-name negatives and their positives | M | `L4-P7-T04` |
| `L4-P7-T08` | Suite 4 — AT-075 banned-measurement negatives | M | `L4-P7-T04` |
| `L4-P7-T09` | Suite 5 — attention-hour derivation, nine cases with literal expected hours | L | `L4-P7-T04` |
| `L4-P7-T10` | Suite 6 — Ready-queue-miss detector, six cases | M | `L4-P7-T04` |
| `L4-P7-T11` | Suite 7 — store-level validators, freshness, retention, taxonomy, fail-closed read | M | `L4-P7-T02` |
| `L4-P7-T12` | Acceptance-test proof map — AT-044, AT-046, AT-075, AT-105, AT-107 | L | `L4-P7-T05`–`L4-P7-T11` |
| `L4-P7-T13` | Suite self-canary — prove the suite fails when a check is removed | M | `L4-P7-T12` |
| `L4-P7-T14` | Rebase, lane self-check, open the PR to `integration` | S | `L4-P7-T13` |

Sizes: **S** under 1 hour, **M** 1–4 hours, **L** over 4 hours. Every task is one branch-local unit of work; none spans a day.

### 0.4 Blocker protocol — the STOP rule mechanism

Every STOP rule in this document ends in the same action. File the blocker into the **`control-plane`** repository. **Never** file an issue into `control-plane-records` — it is a record store, not a work surface (§97.1, lines 8836–8842).

```bash
set -euo pipefail
gh issue create \
  --repo "${CP_SLUG}" \
  --title "BLOCKER L4-P7-<TASK-ID>: <one-line symptom>" \
  --label "blocker" --label "lane-4" \
  --body "$(cat <<'EOF'
## Task
L4-P7-<TASK-ID> — <task title from the index in L4-07-tests-and-runbook.md>

## STOP trigger that fired
<quote the exact bullet from the task's STOP RULE>

## Artifact under test and the phase that owns it
<exact file path>  — owned by <L4 phase document filename>

## Command run
<the exact command, verbatim>

## Actual output
<the exact stdout/stderr, verbatim, untruncated>

## Expected output per the task's SELF-VERIFY block
<the expected block, verbatim, from this document>

## State left behind
<what exists now that did not before; what was rolled back; what was not>

## What I did NOT do
I did not edit the artifact under test, relax an assertion, edit an expected-output
file, delete a fixture, choose an alternative approach, or continue to the next task.
EOF
)"
```

After filing: stop work on this lane. Do not start the next task.

### 0.5 The adopt-or-create rule — binding

Other L4 phase documents may already have created some of the files this phase names. **You never overwrite a file that already exists on the branch.** Every creating command in this document is preceded by the same guard:

```bash
set -euo pipefail
# literal guard — copy it exactly, before every file this document creates
l4_guard() { if [ -f "$1" ]; then echo "ADOPT $1"; return 1; else echo "CREATE $1"; return 0; fi; }
```

- `CREATE` → run the task's `cat > …` block as written.
- `ADOPT` → do **not** write the file. Run only the task's SELF-VERIFY block against the existing file. If SELF-VERIFY passes, the task is complete. If it fails, **STOP** and file a blocker with `blocked_by: adopted file does not satisfy this phase's contract`.

This rule exists because L4 phase documents are authored in parallel; it removes every possibility of one phase clobbering another.

### 0.6 Output strings this phase must not change

`L4-00-charter.md` §7 makes these exact strings the proof of nineteen Definition-of-Done rows. Earlier phases emit them. This phase asserts them **verbatim** and never rewrites a script to emit a different string.

| Command | Required last line of stdout | Charter DoD |
|---|---|---|
| `tools/records/lane-selfcheck.sh --paths` | `PATHS OK` | DoD-17 |
| `tools/records/lane-selfcheck.sh --stores` | `STORES OK 17/17` | DoD-1 |
| `tools/records/validate-schemas.sh` | `SCHEMAS OK` | DoD-2 |
| `tools/records/validate-schemas.sh --negative` | `NEGATIVE OK 10/10` | DoD-3 |
| `tools/records/validate-schemas.sh --fields` | `FIELDS OK` | DoD-10 |
| `tools/records/validate-schemas.sh --at105` | `AT-105 OK` | DoD-11 |
| `tools/records/validate-schemas.sh --at046-secreview` | `SECREVIEW OK` | DoD-12 |
| `tools/records/validate-schemas.sh --time` | `TIME OK` | DoD-18 |
| `tools/records/validate-taxonomy.sh` | `TAXONOMY OK` | DoD-4 |
| `tools/records/validate-freshness.sh` | `FRESHNESS OK BLOCKING=3` | DoD-5 |
| `tools/records/validate-retention.sh` | `RETENTION OK` | DoD-19 |
| `tools/records/test-rqm-detector.sh` | `RQM OK 6/6` | DoD-8 |
| `tools/records/test-rvr.sh` | `RVR OK` | DoD-9 |
| `tools/records/test-read-across.sh --unreachable` | contains `FAIL-CLOSED`, exit non-zero | DoD-16 |
| `metrics/attention/test-derivation.sh` | `ATTENTION OK` | DoD-6 |
| `metrics/attention/test-derivation.sh --provenance` | `PROVENANCE OK` | DoD-7 |
| `metrics/register/validate-sources.sh` | `SOURCES OK` | DoD-13 |
| `metrics/register/validate-sources.sh --arming` | `ARMING OK` | DoD-14 |
| `metrics/register/validate-sources.sh --at046` | `AT-046 OK` | DoD-15 |

**Split of build responsibility.** The `validate-*` scripts belong to the phase that builds the artifact they validate — this phase consumes them and never writes them. The `test-*` scripts, `metrics/attention/test-derivation.sh`, every fixture, and the aggregate runner are this phase's deliverables, subject to §0.5.

---

## DECISION REQUIRED — hand to L0 before the named task

No L4 executor may answer these. Each blocks only the assertion named; every other task proceeds.

### D-L4-P7-01 — Does D88 govern the §97.2 decision-record comment?

**The conflict, both sides quoted.**
- **D88** (decision table, line 10192; narrative at §91.8 line 8189): *"Records carry stable person IDs, never names — that rule is real, it is enforced at schema validation, and it is what keeps the record stores de-identified."* D88 also states as a consequence: *"names in record bodies fail schema validation."*
- **§97.2 line 8908**, inside the decision-record example: `decider: founder  # role, not name, in rules; names appear in real records`.

These cannot both be executed. A validator cannot both reject and accept a name in `decider`.

**Question for L0:** Confirm that D88 governs and that §97.2 line 8908's trailing comment is superseded narrative; or state the carve-out — which stores, which fields — in which a name is admitted.

**Default this document executes until answered:** D88 governs. `L4-P7-T07` is written to assert rejection in all five person-valued fields. If L0 rules the other way, `L4-P7-T07` is re-issued by L0; the executor must not adapt it.

**Status: Closed. Option A — D88 governs.** See `_DECISION_SIGNOFF.md`.

**Blocks:** `L4-P7-T07` only.

### D-L4-P7-02 — `SIG-43` carries two different definitions in §52.2

**Fact.** The unified signal table assigns the identifier `SIG-43` twice:
- line 4571 (end of the SIG-42 row): *"SIG-43 | Unclosed learning-loop items | … | `records/postmortems/` plus `records/incidents/` | Amber | QA"*
- line 4572: *"SIG-43 | Founder operating load | … | Attention ledger | Amber; Red on sustained breach … | Team Lead"*

§52.2 line 4594 lists SIG-43 once, as *"Founder operating load"*. §103.14 line 9977 references *"the Founder operating-load ceiling that SIG-43 breaches against"*. `L4-00-charter.md` §8 cites SIG-43 as *unclosed learning-loop items*.

**Question for L0:** Which definition keeps the identifier `SIG-43`, and what identifier does the other take? A one-to-one map is required: `metrics/signals/sig-source-map.yaml` maps one signal id to one record store, and a duplicated id maps one id to two stores.

**Decided.** The SIG-source assertion in `L4-P7-T11` asserts six rows — SIG-06 → Ready-queue-miss events (line 4535), SIG-17 → restore-test currency (line 4546), SIG-41 → support-intake records (line 4570), SIG-42 → `records/eval/` (line 4571), SIG-43 → attention ledger (line 4572, Founder operating load), SIG-47 → `records/postmortems/` plus `records/incidents/` (learning-loop items, per `_DECISION_SIGNOFF.md`). See `_DECISION_SIGNOFF.md`.

**Blocks:** none.

### D-L4-P7-03 — Rounding order for product attribution

**Fact.** §97.4 line 8972 fixes granularity at 0.25 h *"rounded to nearest, never to zero"*. Line 8974 fixes product attribution: *"a session touching several splits across them by event count."* The spec does not state whether the session duration is rounded to the grid **before** it is split across products or **after**.

**Question for L0:** round-then-split, or split-then-round?

**Decided: round-then-split.** Session duration is rounded to the 0.25 h grid first, then split across products by event count. DC-5 (60-minute session 2:1:1) gives 0.50/0.25/0.25 under this order. A many-way-split fixture that distinguishes the two orders may now be added to the suite. See `_DECISION_SIGNOFF.md`.

**Blocks:** nothing.

---

## 1. Test strategy

### 1.1 The five corpora

| Corpus | Path | Contents | Built by |
|---|---|---|---|
| **A — verbatim** | `tools/records/fixtures/valid/verbatim/` | The five records the spec prints literally: incident (§97.2 lines 8877–8890), deployment (8892–8903), decision (8905–8915), demo (8917–8925), event envelope (§97.3 lines 8933–8946), with placeholders resolved and nothing else changed | `L4-P7-T03` |
| **B — generated valid** | `tools/records/fixtures/valid/generated/` | One valid record per store for all 19 stores, produced by `tools/records/record-write` and `tools/records/event-append` — never hand-typed, because §97.1 line 8838 states records are generated from the workflow surface and *"nobody transcribes"* | `L4-P7-T04` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| **C — envelope negatives** | `tools/records/fixtures/negative/envelope/` | Exactly ten: the nine envelope fields removed one at a time, plus one free-text `event_type` | `L4-P7-T06` |
| **D — D88 negatives** | `tools/records/fixtures/negative/d88/` | Five records carrying a human display name in a person-valued field, and the five matching positives carrying a registry identity | `L4-P7-T07` |
| **E — banned-measurement negatives** | `tools/records/fixtures/negative/at075/` | Ten metric declarations, one per banned measurement of §91.2 lines 8083–8092 | `L4-P7-T08` |

Corpora B, C, D, E live in `control-plane` under `tools/records/fixtures/**`. **No fixture is ever committed to `control-plane-records`.** Tests that need a records repository build a throwaway sandbox under `$L4_TMP` (§4.1, rule R6).

### 1.2 The seven suites

| Suite | Id prefix | Proves | Spec anchor |
|---|---|---|---|
| 1 Round-trip | `RT-` | A record parsed and re-serialised is byte-identical after normalisation; an absent `record_schema_version` / `event_schema_version` **reads** as 1 while the **writer** always emits it | §97.2 line 8875; §97.3 line 8935 |
| 2 Envelope negatives | `EN-` | An event missing any envelope field, or carrying a free-text `event_type`, is rejected at write time | §97.3 line 8931, line 8948 |
| 3 D88 negatives | `D88-` | A record carrying a display name fails schema validation | D88, line 10181; §91.8 line 8171 |
| 4 Banned measurements | `BM-` | No banned measurement appears in any L4 schema or metric, and one introduced is rejected | §91.2 lines 8081–8092; AT-075 line 9406 |
| 5 Derivation | `DC-` | Known input windows produce the exact expected hour outputs, including precedence, idle gap, granularity, product attribution, daily reconciliation and the instrument-defect rule | §97.4 lines 8969–8980 |
| 6 Ready-queue miss | `RQ-` | Both detector limbs fire, both carve-outs hold, `ready_bypass` stays outside the count | §97.5 lines 8982–8987; §29.4 |
| 7 Store validators | `SV-` | Freshness, retention, taxonomy, SIG-source map, RVR, and the fail-closed cross-repository read | §97.2 line 8867; §97.6; §40.1 line 3671 |

### 1.3 Layout on disk — all inside `tools/records/` and `metrics/`, all L4-owned

```
control-plane/
  tools/records/
    fixtures/
      valid/verbatim/            corpus A
      valid/generated/           corpus B
      negative/envelope/         corpus C
      negative/d88/              corpus D
      negative/at075/            corpus E
      attention/input/           DC event windows + capacity fixture
      attention/expected/        DC expected hour outputs (JSON)
      rqm/                       RQ board-transition fixtures
    test/
      lib.sh                     assertion helpers, result format
      suite-01-roundtrip.sh
      suite-02-envelope.sh
      suite-03-d88.sh
      suite-04-banned.sh
      suite-06-rqm.sh            (suite 5 lives at metrics/attention/, see below)
      suite-07-validators.sh
      at-map.yaml                acceptance-test proof map
      suite-canary.sh
    run-tests.sh                 the one command
    test-rqm-detector.sh         charter-named entry point, delegates to suite-06
    test-rvr.sh                  charter-named entry point
    test-read-across.sh          charter-named entry point
  metrics/attention/
    test-derivation.sh           charter-named entry point, suite 5
```

### 1.4 The runner contract — one output grammar, no exceptions

Every suite prints one line per case and nothing else on stdout:

```
PASS <case-id> <one-line detail>
FAIL <case-id> expected=<value> actual=<value>
SKIP <case-id> <reason>
```

and terminates with exactly one summary line:

```
SUITE <suite-id> OK <passed>/<total>
SUITE <suite-id> FAIL <failed> of <total>
```

Exit code is `0` only when zero `FAIL` lines were printed. `SKIP` never makes a suite fail, and the only admissible `SKIP` reason is a `DEFERRED-D-L4-P7-0N` decision id from this document.

---

## 2. Tasks

---

### TASK `L4-P7-T01` — Entry gate: inventory the Phase 1–6 artifacts this phase tests

**Size:** S **Depends on:** — **Writes:** `tools/records/test/ENTRY-GATE.txt` (branch only)

This phase tests artifacts it did not build. Prove they exist before writing a single test.

**Commands**

```bash
set -euo pipefail
export ORG="${ORG:?set ORG first}"
export WORK="$HOME/l4work"; export CP_DIR="${WORK}/control-plane"
export RECORDS_DIR="${WORK}/control-plane-records"; export L4_TMP="${WORK}/tmp"
export L4_BRANCH="lane/4/07-tests-and-runbook"
mkdir -p "$L4_TMP"

git -C "$CP_DIR" fetch --all --prune
git -C "$CP_DIR" status --porcelain
git -C "$CP_DIR" checkout -B "$L4_BRANCH" origin/integration
mkdir -p "$CP_DIR/tools/records/test"

: > "$L4_TMP/entry-gate.raw"
for f in \
  tools/records/lane-selfcheck.sh \
  tools/records/validate-schemas.sh \
  tools/records/validate-taxonomy.sh \
  tools/records/validate-freshness.sh \
  tools/records/validate-retention.sh \
  tools/records/record-write \
  tools/records/event-append \
  tools/records/record-verification-result \
  tools/records/read-across \
  schemas/records/event.envelope.schema.json \
  schemas/records/deployment.schema.json \
  schemas/records/uat.schema.json \
  schemas/records/decision.schema.json \
  schemas/records/demo.schema.json \
  schemas/records/incident.schema.json \
  schemas/records/deletion-request.schema.json \
  schemas/records/security-review.schema.json \
  schemas/records/eval.schema.json \
  schemas/records/support.schema.json \
  schemas/records/ready-queue-miss.schema.json \
  metrics/taxonomy/event-types.yaml \
  metrics/freshness/write-freshness.yaml \
  metrics/signals/sig-source-map.yaml \
  metrics/register/metric-declarations.yaml \
  metrics/register/validate-sources.sh \
  metrics/attention/derive.py ; do
  if [ -e "$CP_DIR/$f" ]; then echo "PRESENT $f"; else echo "ABSENT  $f"; fi >> "$L4_TMP/entry-gate.raw"
done
sort "$L4_TMP/entry-gate.raw" > "$CP_DIR/tools/records/test/ENTRY-GATE.txt"
cat "$CP_DIR/tools/records/test/ENTRY-GATE.txt"
grep -c '^ABSENT' "$CP_DIR/tools/records/test/ENTRY-GATE.txt" || true
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Branch created off `origin/integration` | `git -C "$CP_DIR" rev-parse --abbrev-ref HEAD` | `lane/4/07-tests-and-runbook` |
| 2 | The inventory file lists 26 entries | `wc -l < "$CP_DIR/tools/records/test/ENTRY-GATE.txt"` | `26` |
| 3 | Zero artifacts absent | `grep -c '^ABSENT' "$CP_DIR/tools/records/test/ENTRY-GATE.txt"` | `0` |
| 4 | The records repository is on `main` and clean | `git -C "$RECORDS_DIR" rev-parse --abbrev-ref HEAD; git -C "$RECORDS_DIR" status --porcelain \| wc -l` | `main` then `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "BRANCH=$(git -C "$CP_DIR" rev-parse --abbrev-ref HEAD)"
echo "ENTRIES=$(wc -l < "$CP_DIR/tools/records/test/ENTRY-GATE.txt" | tr -d ' ')"
echo "ABSENT=$(grep -c '^ABSENT' "$CP_DIR/tools/records/test/ENTRY-GATE.txt" || true)"
echo "RECBRANCH=$(git -C "$RECORDS_DIR" rev-parse --abbrev-ref HEAD)"
echo "RECDIRTY=$(git -C "$RECORDS_DIR" status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
BRANCH=lane/4/07-tests-and-runbook
ENTRIES=26
ABSENT=0
RECBRANCH=main
RECDIRTY=0
```

**STOP RULE** — if `ABSENT` is not `0`: an artifact this phase tests has not been built. Do not create it, do not stub it, do not skip its suite. File a blocker naming **every** absent path and the phase document that owns it (`schemas/records/**` and `metrics/**` and `tools/records/**` are named in `L4-00-charter.md` §5). If `RECDIRTY` is not `0`, do not commit anything in the records repository — file a blocker instead (§4.7 rule F4).

---

### TASK `L4-P7-T02` — Test harness skeleton and the runner contract

**Size:** M **Depends on:** `L4-P7-T01`
**Writes:** `tools/records/test/lib.sh`, `tools/records/run-tests.sh`

**Commands**

```bash
set -euo pipefail
l4_guard() { if [ -f "$1" ]; then echo "ADOPT $1"; return 1; else echo "CREATE $1"; return 0; fi; }

l4_guard "$CP_DIR/tools/records/test/lib.sh" && cat > "$CP_DIR/tools/records/test/lib.sh" <<'EOF'
#!/usr/bin/env bash
# L4 test assertion library. Output grammar is fixed by L4-07-tests-and-runbook.md section 1.4.
set -u
L4_PASS=0; L4_FAIL=0; L4_SKIP=0

pass() { L4_PASS=$((L4_PASS+1)); echo "PASS $1 $2"; }
fail() { L4_FAIL=$((L4_FAIL+1)); echo "FAIL $1 expected=$2 actual=$3"; }
skip() { L4_SKIP=$((L4_SKIP+1)); echo "SKIP $1 $2"; }

assert_eq() { # id expected actual
  if [ "$2" = "$3" ]; then pass "$1" "eq=$2"; else fail "$1" "$2" "$3"; fi
}
assert_exit() { # id expected_code cmd...
  local id="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1; local got=$?
  if [ "$got" = "$want" ]; then pass "$id" "exit=$got"; else fail "$id" "exit=$want" "exit=$got"; fi
}
assert_rejects() { # id cmd... : passes only when the command exits NON-zero
  local id="$1"; shift
  if "$@" >/dev/null 2>&1; then fail "$id" "non-zero-exit" "exit=0"; else pass "$id" "rejected"; fi
}
assert_last_line() { # id expected_line cmd...
  local id="$1" want="$2"; shift 2
  local got; got="$("$@" 2>/dev/null | tail -1)"
  if [ "$got" = "$want" ]; then pass "$id" "line=$got"; else fail "$id" "$want" "$got"; fi
}
summary() { # suite-id
  if [ "$L4_FAIL" -eq 0 ]; then
    echo "SUITE $1 OK $L4_PASS/$((L4_PASS+L4_FAIL))"; return 0
  else
    echo "SUITE $1 FAIL $L4_FAIL of $((L4_PASS+L4_FAIL))"; return 1
  fi
}
EOF

l4_guard "$CP_DIR/tools/records/run-tests.sh" && cat > "$CP_DIR/tools/records/run-tests.sh" <<'EOF'
#!/usr/bin/env bash
# L4 aggregate test runner. One command, seven suites.
# Usage: run-tests.sh --all | --suite <01|02|03|04|05|06|07>
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
RC=0
run_one() {
  echo "--- $1"
  sh "$2" || RC=1
}
case "${1:---all}" in
  --all)
    run_one "suite-01-roundtrip"  "$HERE/test/suite-01-roundtrip.sh"
    run_one "suite-02-envelope"   "$HERE/test/suite-02-envelope.sh"
    run_one "suite-03-d88"        "$HERE/test/suite-03-d88.sh"
    run_one "suite-04-banned"     "$HERE/test/suite-04-banned.sh"
    run_one "suite-05-derivation" "$CP/metrics/attention/test-derivation.sh"
    run_one "suite-06-rqm"        "$HERE/test/suite-06-rqm.sh"
    run_one "suite-07-validators" "$HERE/test/suite-07-validators.sh"
    ;;
  --suite)
    case "${2:-}" in
      05) run_one "suite-05-derivation" "$CP/metrics/attention/test-derivation.sh" ;;
      01|02|03|04|06|07) run_one "suite-$2" "$HERE/test/suite-$2"*.sh ;;
      *) echo "usage: run-tests.sh --all | --suite <01..07>"; exit 2 ;;
    esac
    ;;
  *) echo "usage: run-tests.sh --all | --suite <01..07>"; exit 2 ;;
esac
if [ "$RC" -eq 0 ]; then echo "L4 SUITE OK"; else echo "L4 SUITE FAIL"; fi
exit "$RC"
EOF

chmod +x "$CP_DIR/tools/records/run-tests.sh" "$CP_DIR/tools/records/test/lib.sh"
git -C "$CP_DIR" add tools/records/test/lib.sh tools/records/run-tests.sh tools/records/test/ENTRY-GATE.txt
git -C "$CP_DIR" commit -m "L4-P7-T02: test harness skeleton, runner contract and entry-gate inventory"
git -C "$CP_DIR" diff --name-only origin/integration...HEAD | sort
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both files exist and are executable | `test -x "$CP_DIR/tools/records/run-tests.sh" && test -x "$CP_DIR/tools/records/test/lib.sh" && echo YES` | `YES` |
| 2 | The library defines all six helpers | `grep -cE '^(pass|fail|skip|assert_eq|assert_exit|assert_rejects|assert_last_line|summary)\(\)' "$CP_DIR/tools/records/test/lib.sh"` | `8` |
| 3 | Runner rejects an unknown argument with exit 2 | `sh "$CP_DIR/tools/records/run-tests.sh" --nonsense; echo $?` | `2` |
| 4 | Only L4-owned paths changed | `git -C "$CP_DIR" diff --name-only origin/integration...HEAD \| grep -vcE '^(schemas/records/|metrics/|tools/records/)'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "EXEC=$(test -x "$CP_DIR/tools/records/run-tests.sh" && test -x "$CP_DIR/tools/records/test/lib.sh" && echo yes || echo no)"
echo "HELPERS=$(grep -cE '^(pass|fail|skip|assert_eq|assert_exit|assert_rejects|assert_last_line|summary)\(\)' "$CP_DIR/tools/records/test/lib.sh")"
sh "$CP_DIR/tools/records/run-tests.sh" --nonsense >/dev/null 2>&1; echo "USAGE_EXIT=$?"
echo "FOREIGN=$(git -C "$CP_DIR" diff --name-only origin/integration...HEAD | grep -vcE '^(schemas/records/|metrics/|tools/records/)')"
```

Expected output, exactly:

```
EXEC=yes
HELPERS=8
USAGE_EXIT=2
FOREIGN=0
```

**STOP RULE** — if `FOREIGN` is not `0`, a foreign path is on the branch and the lane-guard check will fail the PR (PARTITION.md line 25). Do not push. Do not `git add` anything further. File a blocker. If `HELPERS` is not `8` and the files were `ADOPT`ed, file a blocker with `blocked_by: adopted file does not satisfy this phase's contract`.

---

### TASK `L4-P7-T03` — Fixture corpus A: the five verbatim-spec valid fixtures

**Size:** M **Depends on:** `L4-P7-T02`
**Writes:** `tools/records/fixtures/valid/verbatim/*.yaml`

Transcribe the five records the spec prints literally. **The only permitted edits** are: resolving the placeholders `<product>`, `<role-holder>`, `<run url>`, `<contact-list ref>`, `<person>` to the fixed test values below, and adding the `record_schema_version` / `timestamp` fields §97.2 line 8875 requires on every record. Do not add, remove or rename any other field. Do not "improve" a value.

Fixed test values, binding for every fixture in this phase:

| Placeholder | Fixture value | Why this value |
|---|---|---|
| `<product>` | `alpha` | a fixture product id; never a real product |
| person identity | `dev-a`, `dev-b`, `lead-1` | registry identities keyed on the GitHub login (§99.5 line 9268) |
| `<role-holder>` | `lead-1` | a registry identity, never a display name (D88) |
| `<run url>` | `https://example.invalid/run/1` | RFC 2606 reserved TLD; never resolves |
| `<contact-list ref>` | `contacts/CUST-0001` | a reference, not a customer name |

**Commands**

```bash
set -euo pipefail
FX="$CP_DIR/tools/records/fixtures/valid/verbatim"
mkdir -p "$FX"

l4_guard "$FX/incident.yaml" && cat > "$FX/incident.yaml" <<'EOF'
# Corpus A. Verbatim from MasterSpec v4.0 Section 97.2, lines 8877-8890.
# Placeholders resolved per L4-07-tests-and-runbook.md task L4-P7-T03.
record_schema_version: 1
timestamp: 2026-09-14T02:11:00Z
id: INC-2026-09-14-001
product: alpha
severity: SEV-2
detected: 2026-09-14T02:11:00Z
detection_source: alert
responded: 2026-09-14T08:35:00Z
resolved: 2026-09-14T10:02:00Z
customer_impact: partial degradation, 3 customers
resolution: rollback to digest sha256:0000000000000000000000000000000000000000000000000000000000000000
postmortem: records/postmortems/2026-09-16-alpha.yaml
pre_onboarding: false
EOF

l4_guard "$FX/deployment.yaml" && cat > "$FX/deployment.yaml" <<'EOF'
# Corpus A. Verbatim from MasterSpec v4.0 Section 97.2, lines 8892-8903.
record_schema_version: 1
timestamp: 2026-09-12T14:00:00Z
id: DEP-2026-09-12-014
product: alpha
digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
approved_by: lead-1
approval_event: https://example.invalid/run/1
staging_verified: true
uat_record: records/uat/2026-09-12-alpha-001.yaml
smoke_result: pass
rollback_of: null
EOF

l4_guard "$FX/decision.yaml" && cat > "$FX/decision.yaml" <<'EOF'
# Corpus A. Verbatim from MasterSpec v4.0 Section 97.2, lines 8905-8915.
record_schema_version: 1
timestamp: 2026-09-10T09:00:00Z
id: DEC-2026-09-10-003
product: alpha
decider: founder
prompt_received: 2026-09-08
decided: 2026-09-10
subject: second QA hire deferred; rebalance executed instead
options_considered: [hire, rebalance, reduce-verification-scope]
evidence: [https://example.invalid/run/1, https://example.invalid/run/2]
review_date: 2026-12-01
EOF

l4_guard "$FX/demo.yaml" && cat > "$FX/demo.yaml" <<'EOF'
# Corpus A. Verbatim from MasterSpec v4.0 Section 97.2, lines 8917-8925.
record_schema_version: 1
timestamp: 2026-09-11T11:00:00Z
id: DEMO-2026-09-11-002
product: alpha
customer: contacts/CUST-0001
given_by: dev-a
duration_minutes: 45
outcome: follow-up items filed as work items
EOF

l4_guard "$FX/event.yaml" && cat > "$FX/event.yaml" <<'EOF'
# Corpus A. Verbatim from MasterSpec v4.0 Section 97.3, lines 8933-8946.
# The nine envelope fields, in the order the spec prints them.
event_schema_version: 1
event_id: EVT-2026-09-14-000317
event_type: plan_approved
occurred_at: 2026-09-14T09:31:04Z
recorded_at: 2026-09-14T09:31:06Z
actor: lead-1
product: alpha
subject_ref: records/decisions/DEC-2026-09-14-002.yaml
payload:
  gate: 1
  agent_authored: false
EOF

for f in "$FX"/*.yaml; do python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1])); print('PARSES', sys.argv[1])" "$f"; done
git -C "$CP_DIR" add tools/records/fixtures/valid/verbatim
git -C "$CP_DIR" commit -m "L4-P7-T03: corpus A - five verbatim spec fixtures (97.2, 97.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Five fixtures exist | `ls "$FX"/*.yaml \| wc -l` | `5` |
| 2 | All five parse as YAML | `for f in "$FX"/*.yaml; do python3 -c "import sys,yaml;yaml.safe_load(open(sys.argv[1]))" "$f" \|\| exit 1; done; echo OK` | `OK` |
| 3 | The event fixture carries all nine envelope keys | `python3 -c "import yaml;d=yaml.safe_load(open('$FX/event.yaml'));print(len([k for k in ['event_schema_version','event_id','event_type','occurred_at','recorded_at','actor','product','subject_ref','payload'] if k in d]))"` | `9` |
| 4 | No fixture contains a space-separated capitalised person name | `grep -rEc '^(approved_by|decider|given_by|actor|executor): +[A-Z][a-z]+ +[A-Z]' "$FX" \| grep -v ':0$' \| wc -l` | `0` |
| 5 | Every record fixture carries `record_schema_version` | `grep -l '^record_schema_version:' "$FX"/incident.yaml "$FX"/deployment.yaml "$FX"/decision.yaml "$FX"/demo.yaml \| wc -l` | `4` |

**SELF-VERIFY**

```bash
set -euo pipefail
FX="$CP_DIR/tools/records/fixtures/valid/verbatim"
echo "COUNT=$(ls "$FX"/*.yaml | wc -l | tr -d ' ')"
echo "PARSE=$(for f in "$FX"/*.yaml; do python3 -c "import sys,yaml;yaml.safe_load(open(sys.argv[1]))" "$f" || echo BAD; done | grep -c BAD)"
echo "ENVELOPE=$(python3 -c "import yaml;d=yaml.safe_load(open('$FX/event.yaml'));print(len([k for k in ['event_schema_version','event_id','event_type','occurred_at','recorded_at','actor','product','subject_ref','payload'] if k in d]))")"
echo "RSV=$(grep -l '^record_schema_version:' "$FX"/incident.yaml "$FX"/deployment.yaml "$FX"/decision.yaml "$FX"/demo.yaml | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
COUNT=5
PARSE=0
ENVELOPE=9
RSV=4
```

**STOP RULE** — if `ENVELOPE` is not `9`, you altered the envelope while transcribing. Revert the file with `git -C "$CP_DIR" checkout -- tools/records/fixtures/valid/verbatim/event.yaml` and re-transcribe from §97.3 lines 8933–8946. If it is still not `9`, file a blocker. Never add a field the spec does not print, and never rename one to make a validator pass.

---

### TASK `L4-P7-T04` — Fixture corpus B: the writer-generated valid corpus, all 19 stores <!-- 19 per FD-059 (bootstrap/ counts as a store) -->

**Size:** M **Depends on:** `L4-P7-T03`
**Writes:** `tools/records/fixtures/valid/generated/**`, `tools/records/test/generate-corpus.sh`

§97.1 line 8838: *"the surface generates the records; nobody transcribes."* Corpus B is therefore produced by the Phase-2 writers, never typed. This task drives `record-write` and `event-append` into a **sandbox records repository**, then copies the results into the fixture tree.

**Commands**

```bash
set -euo pipefail
l4_guard "$CP_DIR/tools/records/test/generate-corpus.sh" && cat > "$CP_DIR/tools/records/test/generate-corpus.sh" <<'EOF'
#!/usr/bin/env bash
# Generate corpus B by driving the Phase-2 writers into a throwaway sandbox.
# NEVER writes to the real control-plane-records working tree.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
SANDBOX="${L4_TMP:?L4_TMP not set}/records-sandbox"
OUT="$CP/tools/records/fixtures/valid/generated"

rm -rf "$SANDBOX"; mkdir -p "$SANDBOX"; cd "$SANDBOX"
git init -q -b main
for d in records/incidents records/postmortems records/uat records/estimates \
         records/deployments records/restore-tests records/decisions records/decisions/pending \
         records/breaches records/deletion-requests records/security-reviews records/eval \
         records/launches records/demos records/support records/onboarding records/leave events; do
  mkdir -p "$SANDBOX/$d"
done

export RECORDS_ROOT="$SANDBOX"
mkdir -p "$OUT"
for store in incidents postmortems uat estimates deployments restore-tests decisions \
             decisions/pending breaches deletion-requests security-reviews eval \
             launches demos support onboarding leave; do
  "$CP/tools/records/record-write" \
      --store "$store" --product alpha --actor dev-a \
      --timestamp 2026-09-14T09:00:00Z --fixture-mode \
    || { echo "WRITER-FAILED $store" >&2; exit 3; }
done
"$CP/tools/records/event-append" \
    --event-type plan_approved --actor lead-1 --product alpha \
    --occurred-at 2026-09-14T09:31:04Z --recorded-at 2026-09-14T09:31:06Z \
    --subject-ref records/decisions/DEC-2026-09-14-002.yaml --fixture-mode \
  || { echo "APPENDER-FAILED events" >&2; exit 3; }

rm -rf "$OUT"; mkdir -p "$OUT"
( cd "$SANDBOX" && find records events -type f -name '*.yaml' -print0 ) \
  | ( cd "$SANDBOX" && xargs -0 -I{} sh -c 'mkdir -p "'"$OUT"'/$(dirname {})"; cp "{}" "'"$OUT"'/{}"' )
find "$OUT" -type f -name '*.yaml' | wc -l
EOF
chmod +x "$CP_DIR/tools/records/test/generate-corpus.sh"

sh "$CP_DIR/tools/records/test/generate-corpus.sh"
find "$CP_DIR/tools/records/fixtures/valid/generated" -name '*.yaml' | sed "s|$CP_DIR/||" | sort
git -C "$CP_DIR" add tools/records/test/generate-corpus.sh tools/records/fixtures/valid/generated
git -C "$CP_DIR" commit -m "L4-P7-T04: corpus B - writer-generated valid record for all 19 stores" # 19 per FD-059 (bootstrap/ counts as a store)
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 19 generated fixtures — 17 stores of §97.2 plus `events/` plus `bootstrap/` | `find "$CP_DIR/tools/records/fixtures/valid/generated" -name '*.yaml' \| wc -l` | `19` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | Every generated record validates | `cd "$CP_DIR" && ./tools/records/validate-schemas.sh` | last line `SCHEMAS OK`, exit 0 |
| 3 | The sandbox is not a real repository | `git -C "$L4_TMP/records-sandbox" remote -v \| wc -l` | `0` |
| 4 | Nothing was written to the real records repository | `git -C "$RECORDS_DIR" status --porcelain \| wc -l` | `0` |
| 5 | Every generated record states `record_schema_version` explicitly (§97.2 line 8875) | `grep -rLc '^record_schema_version:' "$CP_DIR/tools/records/fixtures/valid/generated/records" \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
G="$CP_DIR/tools/records/fixtures/valid/generated"
echo "FIXTURES=$(find "$G" -name '*.yaml' | wc -l | tr -d ' ')"
echo "SCHEMAS=$(cd "$CP_DIR" && ./tools/records/validate-schemas.sh 2>/dev/null | tail -1)"
echo "SANDBOX_REMOTES=$(git -C "$L4_TMP/records-sandbox" remote -v | wc -l | tr -d ' ')"
echo "RECDIRTY=$(git -C "$RECORDS_DIR" status --porcelain | wc -l | tr -d ' ')"
echo "MISSING_RSV=$(grep -rL '^record_schema_version:' "$G/records" | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
FIXTURES=19
SCHEMAS=SCHEMAS OK
SANDBOX_REMOTES=0
RECDIRTY=0
MISSING_RSV=0
```

**STOP RULE** — if the generator prints `WRITER-FAILED <store>` or `APPENDER-FAILED events`, the Phase-2 writer cannot produce a valid record for that store. **Do not hand-write the fixture.** File a blocker naming the store and `tools/records/record-write`. If `RECDIRTY` is not `0`, you wrote into the real records repository: run `git -C "$RECORDS_DIR" status` , do **not** commit, do **not** `git checkout --` anything you did not create, and file a blocker citing §4.7 rule F4.

---

### TASK `L4-P7-T05` — Suite 1: schema round-trip and the absent-version read rule

**Size:** M **Depends on:** `L4-P7-T04`
**Writes:** `tools/records/test/suite-01-roundtrip.sh`, `tools/records/test/normalise.py`

Two distinct properties, both stated literally by the spec, and they are **not** the same property:

- **Round-trip.** A record parsed and re-serialised carries the identical key set and identical scalar values. §97.2 line 8875: records *"never edit in place (corrections are follow-up records)"* — a reader that silently drops or coerces a field is an in-place edit performed by the parser.
- **Absent-version reads as 1, but the writer always emits it.** §97.2 line 8875: *"An absent `record_schema_version` reads as version 1; the field is stated explicitly on every record written from Phase 1 onward."* §97.3 line 8935: `event_schema_version: 1  # stated on every event written; absent reads as 1`. Meanwhile §97.3 line 8931 makes an event *missing any envelope field* rejected **at write time**. Both hold: **write-time rejects, read-time defaults.** RT-07 and RT-08 assert the read side; EN-01 in suite 2 asserts the write side. Do not "reconcile" them by changing one.

**Commands**

```bash
set -euo pipefail
l4_guard "$CP_DIR/tools/records/test/normalise.py" && cat > "$CP_DIR/tools/records/test/normalise.py" <<'EOF'
import sys, yaml, json
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print(json.dumps(d, sort_keys=True, separators=(",", ":"), default=str))
EOF

l4_guard "$CP_DIR/tools/records/test/suite-01-roundtrip.sh" && cat > "$CP_DIR/tools/records/test/suite-01-roundtrip.sh" <<'EOF'
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
N="$HERE/normalise.py"
TMP="${L4_TMP:?}/rt"; rm -rf "$TMP"; mkdir -p "$TMP"

i=0
for f in "$CP"/tools/records/fixtures/valid/verbatim/*.yaml \
         $(find "$CP/tools/records/fixtures/valid/generated" -name '*.yaml' | sort); do
  i=$((i+1)); id=$(printf 'RT-%02d' "$i")
  a="$(python3 "$N" "$f")"
  python3 -c "import sys,yaml,json; yaml.safe_dump(json.loads(sys.argv[1]), open(sys.argv[2],'w',encoding='utf-8'), sort_keys=True, default_flow_style=False)" "$a" "$TMP/rt.yaml"
  b="$(python3 "$N" "$TMP/rt.yaml")"
  assert_eq "$id" "$a" "$b"
done

# RT read-side default: absent version reads as 1.
sed '/^record_schema_version:/d' "$CP/tools/records/fixtures/valid/verbatim/incident.yaml" > "$TMP/no-rsv.yaml"
got="$(python3 -c "import yaml;d=yaml.safe_load(open('$TMP/no-rsv.yaml'));print(d.get('record_schema_version',1))")"
assert_eq "RT-RSV-DEFAULT" "1" "$got"

sed '/^event_schema_version:/d' "$CP/tools/records/fixtures/valid/verbatim/event.yaml" > "$TMP/no-esv.yaml"
got="$(python3 -c "import yaml;d=yaml.safe_load(open('$TMP/no-esv.yaml'));print(d.get('event_schema_version',1))")"
assert_eq "RT-ESV-DEFAULT" "1" "$got"

# Every generated record states the version explicitly (writer side).
miss="$(grep -rL '^record_schema_version:' "$CP/tools/records/fixtures/valid/generated/records" | wc -l | tr -d ' ')"
assert_eq "RT-WRITER-STATES-RSV" "0" "$miss"

summary "01-roundtrip"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-01-roundtrip.sh"
sh "$CP_DIR/tools/records/test/suite-01-roundtrip.sh"
git -C "$CP_DIR" add tools/records/test/normalise.py tools/records/test/suite-01-roundtrip.sh
git -C "$CP_DIR" commit -m "L4-P7-T05: suite 1 - round-trip and absent-version read rule (97.2, 97.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | 24 round-trip cases run (5 verbatim + 19 generated) | `sh "$CP_DIR/tools/records/test/suite-01-roundtrip.sh" \| grep -c '^PASS RT-[0-9]'` | `24` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | The suite passes with 27 total cases | `sh "$CP_DIR/tools/records/test/suite-01-roundtrip.sh" \| tail -1` | `SUITE 01-roundtrip OK 27/27` |
| 3 | Suite exit code is 0 | `sh "$CP_DIR/tools/records/test/suite-01-roundtrip.sh" >/dev/null; echo $?` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-01-roundtrip.sh"
echo "RTCASES=$(sh "$S" | grep -c '^PASS RT-[0-9]')"
echo "SUMMARY=$(sh "$S" | tail -1)"
sh "$S" >/dev/null 2>&1; echo "EXIT=$?"
```

Expected output, exactly:

```
RTCASES=24
SUMMARY=SUITE 01-roundtrip OK 27/27
EXIT=0
```

**STOP RULE** — if any `RT-nn` case fails, a parser or a writer is losing or coercing a field. **Do not normalise the fixture to make it pass** and do not add a key to the fixture. File a blocker naming the failing fixture path and the artifact under test. If `RT-RSV-DEFAULT` or `RT-ESV-DEFAULT` fails, the read-side default of §97.2 line 8875 / §97.3 line 8935 is not implemented — blocker to the schema phase, not a fix here.

---

### TASK `L4-P7-T06` — Suite 2: the ten envelope negatives

**Size:** M **Depends on:** `L4-P7-T03`
**Writes:** `tools/records/fixtures/negative/envelope/*.yaml`, `tools/records/test/suite-02-envelope.sh`

§97.3 line 8931, binding: *"Every event carries the same envelope, and an event missing any envelope field is rejected at write time."* Line 8948: *"control-plane CI rejects any event whose `event_type` is absent from it."* Nine fields plus the enum is exactly ten cases, which is exactly the count `L4-00-charter.md` DoD-3 requires (`NEGATIVE OK 10/10`).

**EN-01 is the case the task brief names: an event without a version field MUST fail.**

**Commands**

```bash
set -euo pipefail
NEG="$CP_DIR/tools/records/fixtures/negative/envelope"
mkdir -p "$NEG"
SRC="$CP_DIR/tools/records/fixtures/valid/verbatim/event.yaml"

i=0
for field in event_schema_version event_id event_type occurred_at recorded_at actor product subject_ref; do
  i=$((i+1))
  out="$NEG/$(printf 'EN-%02d-missing-%s.yaml' "$i" "$field")"
  l4_guard "$out" && { sed "/^${field}:/d" "$SRC" > "$out"; }
done
l4_guard "$NEG/EN-09-missing-payload.yaml" && \
  python3 -c "import yaml,sys;d=yaml.safe_load(open('$SRC'));d.pop('payload',None);yaml.safe_dump(d,open('$NEG/EN-09-missing-payload.yaml','w'),sort_keys=False)"
l4_guard "$NEG/EN-10-freetext-event-type.yaml" && \
  sed 's/^event_type: .*/event_type: Gate 1 approval/' "$SRC" > "$NEG/EN-10-freetext-event-type.yaml"

l4_guard "$CP_DIR/tools/records/test/suite-02-envelope.sh" && cat > "$CP_DIR/tools/records/test/suite-02-envelope.sh" <<'EOF'
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
NEG="$CP/tools/records/fixtures/negative/envelope"

# Every negative fixture must be REJECTED. A fixture that validates is a failed test.
for f in "$NEG"/EN-*.yaml; do
  id="$(basename "$f" .yaml | cut -d- -f1-2)"
  # NEEDS_FIX: assert_rejects here tests positional args — update to test --path/--type/--title (FD-039)
  assert_rejects "$id" "$CP/tools/records/event-append" --from-file "$f"
done

# The charter-required aggregate string, asserted verbatim (L4-00-charter.md DoD-3).
assert_last_line "EN-CHARTER" "NEGATIVE OK 10/10" sh "$CP/tools/records/validate-schemas.sh" --negative

# Positive control: the valid envelope IS accepted, or the negatives prove nothing.
assert_exit "EN-CONTROL" 0 "$CP/tools/records/event-append" --from-file "$CP/tools/records/fixtures/valid/verbatim/event.yaml" --fixture-mode

summary "02-envelope"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-02-envelope.sh"
sh "$CP_DIR/tools/records/test/suite-02-envelope.sh"
git -C "$CP_DIR" add tools/records/fixtures/negative/envelope tools/records/test/suite-02-envelope.sh
git -C "$CP_DIR" commit -m "L4-P7-T06: suite 2 - ten envelope negatives per 97.3 lines 8931, 8948"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly ten negative fixtures | `ls "$NEG"/EN-*.yaml \| wc -l` | `10` |
| 2 | All ten are rejected by the appender | `sh "$CP_DIR/tools/records/test/suite-02-envelope.sh" \| grep -c '^PASS EN-[01]'` | `10` |
| 3 | The charter string is emitted verbatim | `cd "$CP_DIR" && ./tools/records/validate-schemas.sh --negative \| tail -1` | `NEGATIVE OK 10/10` |
| 4 | The positive control is accepted | `sh "$CP_DIR/tools/records/test/suite-02-envelope.sh" \| grep -c '^PASS EN-CONTROL'` | `1` |
| 5 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-02-envelope.sh" \| tail -1` | `SUITE 02-envelope OK 12/12` |

**SELF-VERIFY**

```bash
set -euo pipefail
NEG="$CP_DIR/tools/records/fixtures/negative/envelope"
S="$CP_DIR/tools/records/test/suite-02-envelope.sh"
echo "FIXTURES=$(ls "$NEG"/EN-*.yaml | wc -l | tr -d ' ')"
echo "REJECTED=$(sh "$S" | grep -c '^PASS EN-[01]')"
echo "CHARTER=$(cd "$CP_DIR" && ./tools/records/validate-schemas.sh --negative 2>/dev/null | tail -1)"
echo "SUMMARY=$(sh "$S" | tail -1)"
sh "$S" >/dev/null 2>&1; echo "EXIT=$?"
```

Expected output, exactly:

```
FIXTURES=10
REJECTED=10
CHARTER=NEGATIVE OK 10/10
SUMMARY=SUITE 02-envelope OK 12/12
EXIT=0
```

**STOP RULE** — if any `EN-nn` prints `FAIL … actual=exit=0`, the writer **accepted** an event missing an envelope field. That is a direct breach of §97.3 line 8931 and it is the exact failure mode §97.2 line 8867 warns of. Do not add the field to the fixture. Do not delete the fixture. File a blocker titled `BLOCKER L4-P7-T06: event-append accepts an event missing <field>` and stop. If `EN-CONTROL` fails, the appender rejects a valid envelope and every negative above is vacuous — file the blocker against the appender, not against the fixtures.

---

### TASK `L4-P7-T07` — Suite 3: the five D88 display-name negatives and their positives

**Size:** M **Depends on:** `L4-P7-T04`
**Blocked by:** **D-L4-P7-01** for its interpretation only; written and executable against the stated default.
**Writes:** `tools/records/fixtures/negative/d88/*.yaml`, `tools/records/test/suite-03-d88.sh`

D88 (line 10181): *"names in record bodies fail schema validation, because the de-identification of the record stores is the part that genuinely holds."* §91.8 line 8171: *"Records carry stable person IDs, never names — that rule is real, it is enforced at schema validation."*

The five person-valued fields the spec names literally, and nothing beyond them:

| Case | Field | Store | Spec line |
|---|---|---|---|
| `D88-01` | `approved_by` | `records/deployments/` | §97.2 line 8897 |
| `D88-02` | `decider` | `records/decisions/` | §97.2 line 8908 |
| `D88-03` | `given_by` | `records/demos/` | §97.2 line 8922 |
| `D88-04` | `executor` | `records/deletion-requests/` | §97.2 line 8869 (*"plus the named executor"*) |
| `D88-05` | `actor` | `events/` | §97.3 line 8940 |

The display name used in every negative is `Priya Raman` — a two-token capitalised human name that is not a registry identity. The matching positive uses `lead-1` or `dev-a`.

**Commands**

```bash
set -euo pipefail
D88="$CP_DIR/tools/records/fixtures/negative/d88"
mkdir -p "$D88"
V="$CP_DIR/tools/records/fixtures/valid/verbatim"
G="$CP_DIR/tools/records/fixtures/valid/generated"

l4_guard "$D88/D88-01-approved_by.yaml" && sed 's/^approved_by: .*/approved_by: Priya Raman/' "$V/deployment.yaml" > "$D88/D88-01-approved_by.yaml"
l4_guard "$D88/D88-02-decider.yaml"     && sed 's/^decider: .*/decider: Priya Raman/'         "$V/decision.yaml"   > "$D88/D88-02-decider.yaml"
l4_guard "$D88/D88-03-given_by.yaml"    && sed 's/^given_by: .*/given_by: Priya Raman/'       "$V/demo.yaml"       > "$D88/D88-03-given_by.yaml"
l4_guard "$D88/D88-05-actor.yaml"       && sed 's/^actor: .*/actor: Priya Raman/'             "$V/event.yaml"      > "$D88/D88-05-actor.yaml"

# D88-04 derives from the generated deletion-request record, because the spec names the
# field ("the named executor") without printing a full example record.
DR="$(find "$G/records/deletion-requests" -name '*.yaml' | head -1)"
l4_guard "$D88/D88-04-executor.yaml" && \
  python3 -c "import yaml,sys;d=yaml.safe_load(open('$DR'));k=[x for x in d if x=='executor'];sys.exit(9) if not k else None;d['executor']='Priya Raman';yaml.safe_dump(d,open('$D88/D88-04-executor.yaml','w'),sort_keys=False)"

l4_guard "$CP_DIR/tools/records/test/suite-03-d88.sh" && cat > "$CP_DIR/tools/records/test/suite-03-d88.sh" <<'EOF'
#!/usr/bin/env bash
# D88: a record carrying a display name MUST fail validation.
# Spec: D88 (line 10181); Section 91.8 line 8171. See DECISION REQUIRED D-L4-P7-01.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
D88="$CP/tools/records/fixtures/negative/d88"
V="$CP/tools/records/fixtures/valid/verbatim"

# NEEDS_FIX: assert_rejects here tests positional args — update to test --path/--type/--title (FD-039)
assert_rejects "D88-01" "$CP/tools/records/record-write" --validate-only --store deployments       --from-file "$D88/D88-01-approved_by.yaml"
assert_rejects "D88-02" "$CP/tools/records/record-write" --validate-only --store decisions         --from-file "$D88/D88-02-decider.yaml"
assert_rejects "D88-03" "$CP/tools/records/record-write" --validate-only --store demos             --from-file "$D88/D88-03-given_by.yaml"
assert_rejects "D88-04" "$CP/tools/records/record-write" --validate-only --store deletion-requests --from-file "$D88/D88-04-executor.yaml"
assert_rejects "D88-05" "$CP/tools/records/event-append" --validate-only --from-file "$D88/D88-05-actor.yaml"

# Matching positives. Without these the negatives prove only that the validator is broken.
assert_exit "D88-P1" 0 "$CP/tools/records/record-write" --validate-only --store deployments --from-file "$V/deployment.yaml"
assert_exit "D88-P2" 0 "$CP/tools/records/record-write" --validate-only --store decisions   --from-file "$V/decision.yaml"
assert_exit "D88-P3" 0 "$CP/tools/records/record-write" --validate-only --store demos       --from-file "$V/demo.yaml"
assert_exit "D88-P4" 0 "$CP/tools/records/record-write" --validate-only --store deletion-requests \
    --from-file "$(find "$CP/tools/records/fixtures/valid/generated/records/deletion-requests" -name '*.yaml' | head -1)"
assert_exit "D88-P5" 0 "$CP/tools/records/event-append" --validate-only --from-file "$V/event.yaml"

# No display name anywhere in the valid corpora.
leak="$(grep -rEl '^(approved_by|decider|given_by|actor|executor): +[A-Z][a-z]+ +[A-Z]' \
        "$CP/tools/records/fixtures/valid" | wc -l | tr -d ' ')"
assert_eq "D88-CORPUS-CLEAN" "0" "$leak"

summary "03-d88"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-03-d88.sh"
sh "$CP_DIR/tools/records/test/suite-03-d88.sh"
git -C "$CP_DIR" add tools/records/fixtures/negative/d88 tools/records/test/suite-03-d88.sh
git -C "$CP_DIR" commit -m "L4-P7-T07: suite 3 - D88 display-name rejection, five negatives and five positives"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Five D88 negative fixtures | `ls "$D88"/D88-0*.yaml \| wc -l` | `5` |
| 2 | All five rejected | `sh "$CP_DIR/tools/records/test/suite-03-d88.sh" \| grep -c '^PASS D88-0'` | `5` |
| 3 | All five positives accepted | `sh "$CP_DIR/tools/records/test/suite-03-d88.sh" \| grep -c '^PASS D88-P'` | `5` |
| 4 | Valid corpora carry no display name | `sh "$CP_DIR/tools/records/test/suite-03-d88.sh" \| grep -c '^PASS D88-CORPUS-CLEAN'` | `1` |
| 5 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-03-d88.sh" \| tail -1` | `SUITE 03-d88 OK 11/11` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-03-d88.sh"
echo "NEGFIX=$(ls "$CP_DIR/tools/records/fixtures/negative/d88"/D88-0*.yaml | wc -l | tr -d ' ')"
echo "REJECTED=$(sh "$S" | grep -c '^PASS D88-0')"
echo "ACCEPTED=$(sh "$S" | grep -c '^PASS D88-P')"
echo "SUMMARY=$(sh "$S" | tail -1)"
sh "$S" >/dev/null 2>&1; echo "EXIT=$?"
```

Expected output, exactly:

```
NEGFIX=5
REJECTED=5
ACCEPTED=5
SUMMARY=SUITE 03-d88 OK 11/11
EXIT=0
```

**STOP RULE** — three distinct triggers, three distinct blockers, and none of them is fixed here:

1. A `D88-0n` case prints `FAIL … actual=exit=0` → the schema **accepts** a display name in a record body. This is a direct breach of D88 and of §91.8 line 8171. File `BLOCKER L4-P7-T07: <field> accepts a display name, D88 not enforced at schema validation`.
2. The `python3` step for `D88-04` exits `9` → the generated deletion-request record has no `executor` key, so §97.2 line 8869's *"named executor"* is not in the schema. File a blocker against `schemas/records/deletion-request.schema.json`.
3. A `D88-Pn` positive is rejected → the validator rejects a registry identity, which would make every negative vacuous. File a blocker against the validator.

Do not edit any schema. Do not weaken the fixture to a single-token name. Do not delete case `D88-02` because §97.2 line 8908's comment appears to permit a name — that conflict is **D-L4-P7-01** and only L0 resolves it.

---

### TASK `L4-P7-T08` — Suite 4: AT-075 banned-measurement negatives

**Size:** M **Depends on:** `L4-P7-T04`
**Writes:** `tools/records/fixtures/negative/at075/*.yaml`, `tools/records/test/suite-04-banned.sh`

**AT-075** (§100.5, line 9406): *"No surveillance metrics | Banned measurements are absent from the schema and rejected if introduced."* The banned list is §91.2, lines 8081–8092, ten bullets, *"with no configuration option to enable any of them"*.

**Commands**

```bash
set -euo pipefail
BM="$CP_DIR/tools/records/fixtures/negative/at075"
mkdir -p "$BM"
i=0
for token in keystroke_logging screen_monitoring activity_surveillance webcam_presence \
             hours_online ai_token_usage ide_active_time flight_risk_prediction \
             emotional_state_inference surveillance_score ; do
  i=$((i+1))
  out="$BM/$(printf 'BM-%02d-%s.yaml' "$i" "$token")"
  l4_guard "$out" && cat > "$out" <<EOF
# AT-075 negative fixture. MasterSpec v4.0 Section 91.2, lines 8081-8092.
# This declaration MUST be rejected by metrics/register/validate-sources.sh.
metric_id: banned_${token}
definition: ${token} measured per person
source: events/
time_window: 7d
baseline: unbaselined
expected_interpretation: higher is worse
known_limitations: none
owner: founder
action_on_breach: review
EOF
done

l4_guard "$CP_DIR/tools/records/test/suite-04-banned.sh" && cat > "$CP_DIR/tools/records/test/suite-04-banned.sh" <<'EOF'
#!/usr/bin/env bash
# AT-075 (line 9406) against the banned list of Section 91.2 (lines 8081-8092).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
BM="$CP/tools/records/fixtures/negative/at075"

# Limb 1 — absent from the schemas and the metrics tree.
i=0
for token in keystroke screen_monitor activity_surveillance webcam \
             hours_online hours_at_desk token_usage ide_active flight_risk surveillance_scor ; do
  i=$((i+1)); id="$(printf 'BM-ABS-%02d' "$i")"
  n="$(grep -rli "$token" "$CP/schemas/records" "$CP/metrics" \
        --exclude-dir=fixtures 2>/dev/null | wc -l | tr -d ' ')"
  assert_eq "$id" "0" "$n"
done

# Limb 2 — rejected if introduced.
i=0
for f in "$BM"/BM-*.yaml; do
  i=$((i+1)); id="$(printf 'BM-REJ-%02d' "$i")"
  assert_rejects "$id" sh "$CP/metrics/register/validate-sources.sh" --check-declaration "$f"
done

summary "04-banned"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-04-banned.sh"
sh "$CP_DIR/tools/records/test/suite-04-banned.sh"
git -C "$CP_DIR" add tools/records/fixtures/negative/at075 tools/records/test/suite-04-banned.sh
git -C "$CP_DIR" commit -m "L4-P7-T08: suite 4 - AT-075 banned-measurement absence and rejection"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Ten banned-metric fixtures | `ls "$BM"/BM-*.yaml \| wc -l` | `10` |
| 2 | Ten absence checks pass | `sh "$CP_DIR/tools/records/test/suite-04-banned.sh" \| grep -c '^PASS BM-ABS'` | `10` |
| 3 | Ten rejection checks pass | `sh "$CP_DIR/tools/records/test/suite-04-banned.sh" \| grep -c '^PASS BM-REJ'` | `10` |
| 4 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-04-banned.sh" \| tail -1` | `SUITE 04-banned OK 20/20` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-04-banned.sh"
echo "FIXTURES=$(ls "$CP_DIR/tools/records/fixtures/negative/at075"/BM-*.yaml | wc -l | tr -d ' ')"
echo "ABSENCE=$(sh "$S" | grep -c '^PASS BM-ABS')"
echo "REJECTION=$(sh "$S" | grep -c '^PASS BM-REJ')"
echo "SUMMARY=$(sh "$S" | tail -1)"
sh "$S" >/dev/null 2>&1; echo "EXIT=$?"
```

Expected output, exactly:

```
FIXTURES=10
ABSENCE=10
REJECTION=10
SUMMARY=SUITE 04-banned OK 20/20
EXIT=0
```

**STOP RULE** — if a `BM-ABS-nn` fails, a banned measurement token appears in an L4 schema or metric. **Do not delete the offending line yourself** — it may be a legitimate word in prose, or it may be a real breach, and telling them apart is judgment. File a blocker quoting the matching file and line and cite §91.2 line 8081 (*"Explicitly banned, with no configuration option to enable any of them"*). If a `BM-REJ-nn` fails, the metric register accepts a banned declaration and AT-075 does not pass — blocker against `metrics/register/validate-sources.sh`.

---

### TASK `L4-P7-T09` — Suite 5: attention-hour derivation, nine cases with literal expected hours

**Size:** L **Depends on:** `L4-P7-T04`
**Writes:** `tools/records/fixtures/attention/input/*.yaml`, `tools/records/fixtures/attention/expected/*.json`, `metrics/attention/test-derivation.sh`

Every expected value below is **computed from the spec and fixed**. You do not compute them; you assert them. The rules applied, each quoted:

- §97.4 line 8971 — *"The **idle gap** is calibrated configuration with an initial value of 30 minutes."* Events separated by **no more than** 30 minutes are one session (line 8969: *"consecutive events separated by no more than the idle gap belong to one session"*); a wider gap ends it.
- §97.4 line 8972 — *"Attribution granularity is calibrated configuration with an initial value of 0.25 hours, rounded to nearest, never to zero."*
- §97.4 line 8969 — *"A session's duration is the span from its first event to its last; a single-event session counts as one granularity unit."* And: *"Elapsed wall-clock time between an interval's bounds is never an attention hour."*
- §97.4 line 8973 — precedence, fixed order: **Incident, Verification, Review, Engineering, Architecture, Planning, Operational, Coordination**; *"the losing categories receive nothing."*
- §97.4 line 8974 — *"a session touching several splits across them by event count; a session touching none attributes to the portfolio."*
- §97.4 line 8975 — truncation *"in reverse precedence order until the reconciliation holds, and each truncation is recorded."*
- §97.4 line 8976 — a day exceeding scheduled availability **before** truncation is an **instrument defect** and *"never enters a Capacity Profile, a workload state (Section 83) or the Founder view."*
- §97.4 line 8980 — the weekly band is *"one band per category, unattributed to any product"*, apportioned *"in proportion to their machine-derived activity shares for the same week, and to the portfolio where no share exists"*, and *"Any figure that includes self-reported hours carries a **self-reported** provenance label wherever it renders, and carries it permanently."*
- §67.2 / §57.2 line 4956 — the `ritual` flag is *"set by the workflow or record that opens that ritual, never self-reported."*

**The nine cases and their expected outputs**

| Case | Input | Rule exercised | Expected output |
|---|---|---|---|
| `DC-1` | `dev-a`, `alpha`, Engineering; events 09:00, 09:25, 09:50, 10:15 (gaps 25/25/25) | one session, span on the grid | Engineering `alpha` **1.25 h**, sessions **1** |
| `DC-2` | `dev-a`, `alpha`, Engineering; events 09:00, 09:20, 10:05, 10:35 (gaps 20/45/30) | 45 > 30 splits; 30 does not | two sessions: 20 min → **0.25**, 30 min → **0.50**; total **0.75 h**, sessions **2** |
| `DC-3` | `dev-a`, `alpha`, Review; one event 14:00 | single-event session, never zero | Review `alpha` **0.25 h**, sessions **1** |
| `DC-4` | `dev-a`, `alpha`; incident window 13:00–15:00 and review window 13:30–14:30; events 13:40, 14:00, 14:20 | precedence, Incident outranks Review | Incident **0.75 h**, Review **0.00 h** |
| `DC-5` | `dev-a`; one session, events 11:00 (`alpha`), 11:20 (`alpha`), 11:40 (`beta`), 12:00 (`gamma`); span 60 min | product attribution by event count | `alpha` **0.50**, `beta` **0.25**, `gamma` **0.25** |
| `DC-6` | `dev-a`, 2026-09-15, scheduled availability **8.00 h**; pre-truncation Incident 3.00, Verification 2.00, Review 1.50, Engineering 1.25, Coordination 0.75 (total **8.50**) | daily reconciliation + instrument defect | post: Incident 3.00, Verification 2.00, Review 1.50, Engineering 1.25, Coordination **0.25**, total **8.00**; truncations **1** (`Coordination`, **0.50**); `instrument_defect` **true**; `capacity_profile_eligible` **false**; `workload_state_eligible` **false**; `founder_view_eligible` **false** |
| `DC-7` | `dev-a`, 2026-09-16, scheduled 8.00 h; Engineering 4.00, Review 2.00, Planning 1.50 (total **7.50**) | clean control | total **7.50**, truncations **0**, `instrument_defect` **false**, `capacity_profile_eligible` **true** |
| `DC-8` | `dev-a`, week 2026-W38, Coordination self-report **4.00 h**, unattributed; machine shares `alpha` 0.75, `beta` 0.25. Plus `dev-b`, Coordination self-report **2.00 h**, no machine share | apportionment + permanent provenance | `dev-a`/`alpha` **3.00**, `dev-a`/`beta` **1.00**, `dev-b`/`portfolio` **2.00**; every one of the three carries `provenance: self-reported` |
| `DC-9` | a self-report entry carrying `ritual: true` | §57.2 line 4956 / §67.2 — never self-reported | the derivation **rejects** it (non-zero exit) |

Coordination in `DC-6` is truncated first because reverse precedence order is Coordination, Operational, Planning, Architecture, Engineering, Review, Verification, Incident, and the excess is 8.50 − 8.00 = 0.50.

**Commands**

```bash
set -euo pipefail
AI="$CP_DIR/tools/records/fixtures/attention/input"
AE="$CP_DIR/tools/records/fixtures/attention/expected"
mkdir -p "$AI" "$AE"

l4_guard "$AI/dc-1.yaml" && cat > "$AI/dc-1.yaml" <<'EOF'
case: DC-1
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    product: alpha
    events: [2026-09-14T09:00:00Z, 2026-09-14T09:25:00Z, 2026-09-14T09:50:00Z, 2026-09-14T10:15:00Z]
EOF
l4_guard "$AE/dc-1.json" && cat > "$AE/dc-1.json" <<'EOF'
{"case":"DC-1","sessions":1,"hours":{"Engineering":{"alpha":1.25}},"truncations":0,"instrument_defect":false}
EOF

l4_guard "$AI/dc-2.yaml" && cat > "$AI/dc-2.yaml" <<'EOF'
case: DC-2
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Engineering
    product: alpha
    events: [2026-09-14T09:00:00Z, 2026-09-14T09:20:00Z, 2026-09-14T10:05:00Z, 2026-09-14T10:35:00Z]
EOF
l4_guard "$AE/dc-2.json" && cat > "$AE/dc-2.json" <<'EOF'
{"case":"DC-2","sessions":2,"hours":{"Engineering":{"alpha":0.75}},"truncations":0,"instrument_defect":false}
EOF

l4_guard "$AI/dc-3.yaml" && cat > "$AI/dc-3.yaml" <<'EOF'
case: DC-3
person: dev-a
date: 2026-09-14
scheduled_availability_hours: 8.0
windows:
  - category: Review
    product: alpha
    events: [2026-09-14T14:00:00Z]
EOF
l4_guard "$AE/dc-3.json" && cat > "$AE/dc-3.json" <<'EOF'
{"case":"DC-3","sessions":1,"hours":{"Review":{"alpha":0.25}},"truncations":0,"instrument_defect":false}
EOF

l4_guard "$AI/dc-4.yaml" && cat > "$AI/dc-4.yaml" <<'EOF'
case: DC-4
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
l4_guard "$AE/dc-4.json" && cat > "$AE/dc-4.json" <<'EOF'
{"case":"DC-4","sessions":1,"hours":{"Incident":{"alpha":0.75},"Review":{"alpha":0.0}},"truncations":0,"instrument_defect":false}
EOF

l4_guard "$AI/dc-5.yaml" && cat > "$AI/dc-5.yaml" <<'EOF'
case: DC-5
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
l4_guard "$AE/dc-5.json" && cat > "$AE/dc-5.json" <<'EOF'
{"case":"DC-5","sessions":1,"hours":{"Engineering":{"alpha":0.5,"beta":0.25,"gamma":0.25}},"truncations":0,"instrument_defect":false}
EOF

l4_guard "$AI/dc-6.yaml" && cat > "$AI/dc-6.yaml" <<'EOF'
case: DC-6
person: dev-a
date: 2026-09-15
scheduled_availability_hours: 8.0
pre_truncation_hours:
  Incident: 3.00
  Verification: 2.00
  Review: 1.50
  Engineering: 1.25
  Coordination: 0.75
EOF
l4_guard "$AE/dc-6.json" && cat > "$AE/dc-6.json" <<'EOF'
{"case":"DC-6","total_hours":8.0,
 "hours_by_category":{"Incident":3.0,"Verification":2.0,"Review":1.5,"Engineering":1.25,"Coordination":0.25},
 "truncations":1,"truncation_detail":[{"category":"Coordination","hours_removed":0.5}],
 "instrument_defect":true,"capacity_profile_eligible":false,
 "workload_state_eligible":false,"founder_view_eligible":false}
EOF

l4_guard "$AI/dc-7.yaml" && cat > "$AI/dc-7.yaml" <<'EOF'
case: DC-7
person: dev-a
date: 2026-09-16
scheduled_availability_hours: 8.0
pre_truncation_hours:
  Engineering: 4.00
  Review: 2.00
  Planning: 1.50
EOF
l4_guard "$AE/dc-7.json" && cat > "$AE/dc-7.json" <<'EOF'
{"case":"DC-7","total_hours":7.5,
 "hours_by_category":{"Engineering":4.0,"Review":2.0,"Planning":1.5},
 "truncations":0,"instrument_defect":false,"capacity_profile_eligible":true}
EOF

l4_guard "$AI/dc-8.yaml" && cat > "$AI/dc-8.yaml" <<'EOF'
case: DC-8
week: 2026-W38
self_reports:
  - person: dev-a
    category: Coordination
    hours: 4.00
    product: null
    provenance: self-reported
  - person: dev-b
    category: Coordination
    hours: 2.00
    product: null
    provenance: self-reported
machine_activity_shares:
  dev-a: {alpha: 0.75, beta: 0.25}
  dev-b: {}
EOF
l4_guard "$AE/dc-8.json" && cat > "$AE/dc-8.json" <<'EOF'
{"case":"DC-8","apportioned":[
 {"person":"dev-a","product":"alpha","category":"Coordination","hours":3.0,"provenance":"self-reported"},
 {"person":"dev-a","product":"beta","category":"Coordination","hours":1.0,"provenance":"self-reported"},
 {"person":"dev-b","product":"portfolio","category":"Coordination","hours":2.0,"provenance":"self-reported"}]}
EOF

l4_guard "$AI/dc-9.yaml" && cat > "$AI/dc-9.yaml" <<'EOF'
case: DC-9
week: 2026-W38
self_reports:
  - person: dev-a
    category: Coordination
    hours: 1.00
    product: null
    provenance: self-reported
    ritual: true      # MUST be rejected: Section 57.2 line 4956, Section 67.2 - never self-reported
EOF

l4_guard "$CP_DIR/metrics/attention/test-derivation.sh" && cat > "$CP_DIR/metrics/attention/test-derivation.sh" <<'EOF'
#!/usr/bin/env bash
# L4 suite 5 - attention-hour derivation. MasterSpec v4.0 Section 97.4 lines 8954-8981.
# Expected values are fixed by L4-07-tests-and-runbook.md task L4-P7-T09. Never edit them
# to make a run pass: a mismatch is a defect in metrics/attention/derive.py, not here.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$CP/tools/records/test/lib.sh"
IN="$CP/tools/records/fixtures/attention/input"
EX="$CP/tools/records/fixtures/attention/expected"
NORM='import sys,json;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True,separators=(",",":")))'

if [ "${1:-}" = "--provenance" ]; then
  out="$(python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-8.yaml" --json 2>/dev/null)"
  n="$(printf '%s' "$out" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(sum(1 for r in d["apportioned"] if r.get("provenance")=="self-reported"))')"
  if [ "$n" = "3" ]; then echo "PROVENANCE OK"; exit 0; else echo "PROVENANCE FAIL labelled=$n expected=3"; exit 1; fi
fi

for c in 1 2 3 4 5 6 7 8; do
  id="DC-$c"
  got="$(python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-$c.yaml" --json 2>/dev/null \
        | python3 -c 'import sys,json;print(json.dumps(json.load(sys.stdin),sort_keys=True,separators=(",",":")))')"
  want="$(python3 -c "$NORM" "$EX/dc-$c.json")"
  assert_eq "$id" "$want" "$got"
done
assert_rejects "DC-9" python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-9.yaml" --json

if [ "$L4_FAIL" -eq 0 ]; then echo "ATTENTION OK"; exit 0; else echo "ATTENTION FAIL $L4_FAIL of 9"; exit 1; fi
EOF
chmod +x "$CP_DIR/metrics/attention/test-derivation.sh"
sh "$CP_DIR/metrics/attention/test-derivation.sh"
sh "$CP_DIR/metrics/attention/test-derivation.sh" --provenance
git -C "$CP_DIR" add tools/records/fixtures/attention metrics/attention/test-derivation.sh
git -C "$CP_DIR" commit -m "L4-P7-T09: suite 5 - attention derivation, nine cases with fixed expected hours (97.4)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Nine input fixtures, eight expected files | `ls "$AI"/dc-*.yaml \| wc -l; ls "$AE"/dc-*.json \| wc -l` | `9` then `8` |
| 2 | Eight derivation cases pass | `sh "$CP_DIR/metrics/attention/test-derivation.sh" \| grep -c '^PASS DC-[1-8]'` | `8` |
| 3 | The ritual negative is rejected | `sh "$CP_DIR/metrics/attention/test-derivation.sh" \| grep -c '^PASS DC-9'` | `1` |
| 4 | Charter string DoD-6 verbatim | `sh "$CP_DIR/metrics/attention/test-derivation.sh" \| tail -1` | `ATTENTION OK` |
| 5 | Charter string DoD-7 verbatim | `sh "$CP_DIR/metrics/attention/test-derivation.sh" --provenance \| tail -1` | `PROVENANCE OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
T="$CP_DIR/metrics/attention/test-derivation.sh"
echo "INPUTS=$(ls "$CP_DIR/tools/records/fixtures/attention/input"/dc-*.yaml | wc -l | tr -d ' ')"
echo "EXPECTED=$(ls "$CP_DIR/tools/records/fixtures/attention/expected"/dc-*.json | wc -l | tr -d ' ')"
echo "CASES=$(sh "$T" | grep -c '^PASS DC-[1-8]')"
echo "RITUAL=$(sh "$T" | grep -c '^PASS DC-9')"
echo "DOD6=$(sh "$T" | tail -1)"
echo "DOD7=$(sh "$T" --provenance | tail -1)"
```

Expected output, exactly:

```
INPUTS=9
EXPECTED=8
CASES=8
RITUAL=1
DOD6=ATTENTION OK
DOD7=PROVENANCE OK
```

**STOP RULE** — the expected JSON files in `fixtures/attention/expected/` are **derived from the spec and frozen by this document**. If a case fails:

- **Never** edit a file under `fixtures/attention/expected/`.
- **Never** edit `metrics/attention/derive.py` — it belongs to the metrics phase, not to this one.
- File a blocker quoting the failing case id, the `expected=` and `actual=` strings verbatim, and the §97.4 line that fixes the rule (idle gap 8971, granularity 8972, precedence 8973, product attribution 8974, reconciliation 8975, instrument defect 8976, self-report 8980).
- If `DC-4` fails with Review non-zero, the precedence order is not implemented and the whole ledger is unsound — mark the blocker `severity: blocks-merge-train`.
- If `DC-6` reports `instrument_defect: false`, the derivation is silently absorbing an over-availability day into a Capacity Profile, which §97.4 line 8976 forbids — same severity.
- If a case fails in a split-versus-round direction, confirm the fixture uses round-then-split (D-L4-P7-03 decided); a mismatch is a defect in `derive.py`, not in the fixture.

---

### TASK `L4-P7-T10` — Suite 6: Ready-queue-miss detector, six cases

**Size:** M **Depends on:** `L4-P7-T04`
**Writes:** `tools/records/fixtures/rqm/*.yaml`, `tools/records/test/suite-06-rqm.sh`, `tools/records/test-rqm-detector.sh`

§97.5, lines 8982–8987, and §29.4. Six cases, matching `L4-00-charter.md` DoD-8 (`RQM OK 6/6`):

| Case | Board transition | Ready queue | Expected | Spec |
|---|---|---|---|---|
| `RQ-1` | Backlog → In Progress | empty | miss recorded, counted in SIG-06 | §97.5 line 8983 |
| `RQ-2` | Backlog → Planned | empty | miss recorded, counted in SIG-06 | §97.5 line 8983 (*"directly to Planned or In Progress"*) |
| `RQ-3` | Ready → Planned → In Progress | non-empty | **no** miss | §97.5 line 8984 (*"The Planned column is the normal assignment step … passing through it is never a miss"*) |
| `RQ-4` | Blocked flag cleared, item resumed | any | **no** miss | §97.5 line 8984 (*"a resumption, not a fresh pickup"*) |
| `RQ-5` | item completed | empty, no suitable item | miss recorded on the **completion** transition | §97.5 line 8986 (*"Completion with an empty Ready queue counts"*) |
| `RQ-6` | Backlog → Planned | suitable Ready items exist | recorded with reason `ready_bypass`, **outside** the SIG-06 count | §97.5 line 8987 (*"A bypass with a full Ready queue does not count"*) |

The §29.4 field set is asserted **without naming a field**, so nothing is invented: run `RQ-1` twice — once with the cause prompt answered, once without — and assert that the unanswered record's key set is a strict subset of the answered one, differing by exactly **three** keys. §97.5 line 8987: *"the last three supplied by the cause prompt, never inferred."*

**Commands**

```bash
set -euo pipefail
RQ="$CP_DIR/tools/records/fixtures/rqm"; mkdir -p "$RQ"

l4_guard "$RQ/rq-1.yaml" && cat > "$RQ/rq-1.yaml" <<'EOF'
case: RQ-1
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Backlog, to: InProgress}
ready_queue: []
blocked_flag_cleared: false
cause_prompt_answered: true
EOF
l4_guard "$RQ/rq-1-unanswered.yaml" && sed 's/^cause_prompt_answered: true/cause_prompt_answered: false/' "$RQ/rq-1.yaml" > "$RQ/rq-1-unanswered.yaml"
l4_guard "$RQ/rq-2.yaml" && sed -e 's/^case: RQ-1/case: RQ-2/' -e 's/to: InProgress/to: Planned/' "$RQ/rq-1.yaml" > "$RQ/rq-2.yaml"
l4_guard "$RQ/rq-3.yaml" && cat > "$RQ/rq-3.yaml" <<'EOF'
case: RQ-3
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Ready, to: Planned, then: InProgress}
ready_queue: [WI-101, WI-102]
blocked_flag_cleared: false
cause_prompt_answered: false
EOF
l4_guard "$RQ/rq-4.yaml" && cat > "$RQ/rq-4.yaml" <<'EOF'
case: RQ-4
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: InProgress, to: InProgress}
ready_queue: []
blocked_flag_cleared: true
cause_prompt_answered: false
EOF
l4_guard "$RQ/rq-5.yaml" && cat > "$RQ/rq-5.yaml" <<'EOF'
case: RQ-5
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: InProgress, to: Done}
ready_queue: []
blocked_flag_cleared: false
cause_prompt_answered: true
EOF
l4_guard "$RQ/rq-6.yaml" && cat > "$RQ/rq-6.yaml" <<'EOF'
case: RQ-6
person: dev-a
date: 2026-09-14
product: alpha
transition: {from: Backlog, to: Planned}
ready_queue: [WI-101, WI-102]
blocked_flag_cleared: false
cause_prompt_answered: true
EOF

l4_guard "$CP_DIR/tools/records/test/suite-06-rqm.sh" && cat > "$CP_DIR/tools/records/test/suite-06-rqm.sh" <<'EOF'
#!/usr/bin/env bash
# L4 suite 6 - Ready-queue-miss detector. Section 97.5 lines 8982-8987; Section 29.4.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
RQ="$CP/tools/records/fixtures/rqm"
DET="$CP/tools/records/rqm-detect"
OUT="${L4_TMP:?}/rqm"; rm -rf "$OUT"; mkdir -p "$OUT"

verdict() { "$DET" --input "$1" --json 2>/dev/null | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("verdict","NONE"),d.get("counts_in_sig06","NONE"))'; }

assert_eq "RQ-1" "miss True"          "$(verdict "$RQ/rq-1.yaml")"
assert_eq "RQ-2" "miss True"          "$(verdict "$RQ/rq-2.yaml")"
assert_eq "RQ-3" "no_miss False"      "$(verdict "$RQ/rq-3.yaml")"
assert_eq "RQ-4" "no_miss False"      "$(verdict "$RQ/rq-4.yaml")"
assert_eq "RQ-5" "miss True"          "$(verdict "$RQ/rq-5.yaml")"
assert_eq "RQ-6" "ready_bypass False" "$(verdict "$RQ/rq-6.yaml")"

# Section 29.4 field set, asserted without naming a field.
"$DET" --input "$RQ/rq-1.yaml"            --json > "$OUT/a.json" 2>/dev/null
"$DET" --input "$RQ/rq-1-unanswered.yaml" --json > "$OUT/b.json" 2>/dev/null
d="$(python3 - "$OUT/a.json" "$OUT/b.json" <<'PY'
import sys,json
a=set(json.load(open(sys.argv[1]))["record"].keys())
b=set(json.load(open(sys.argv[2]))["record"].keys())
print(("SUBSET" if b<a else "NOTSUBSET"), len(a-b))
PY
)"
assert_eq "RQ-FIELDSET" "SUBSET 3" "$d"

summary "06-rqm"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-06-rqm.sh"

l4_guard "$CP_DIR/tools/records/test-rqm-detector.sh" && cat > "$CP_DIR/tools/records/test-rqm-detector.sh" <<'EOF'
#!/usr/bin/env bash
# Charter-named entry point (L4-00-charter.md DoD-8). Delegates to suite 6.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
out="$(sh "$HERE/test/suite-06-rqm.sh")"; rc=$?
echo "$out" | grep -E '^(PASS|FAIL|SKIP) RQ-[1-6] '
n="$(echo "$out" | grep -c '^PASS RQ-[1-6] ')"
if [ "$rc" -eq 0 ] && [ "$n" = "6" ]; then echo "RQM OK 6/6"; exit 0; fi
echo "RQM FAIL $n of 6"; exit 1
EOF
chmod +x "$CP_DIR/tools/records/test-rqm-detector.sh"
sh "$CP_DIR/tools/records/test-rqm-detector.sh"
git -C "$CP_DIR" add tools/records/fixtures/rqm tools/records/test/suite-06-rqm.sh tools/records/test-rqm-detector.sh
git -C "$CP_DIR" commit -m "L4-P7-T10: suite 6 - Ready-queue-miss detector, six cases (97.5, 29.4)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Seven RQ fixtures (six cases + the unanswered variant) | `ls "$RQ"/rq-*.yaml \| wc -l` | `7` |
| 2 | Six behavioural cases pass | `sh "$CP_DIR/tools/records/test/suite-06-rqm.sh" \| grep -c '^PASS RQ-[1-6] '` | `6` |
| 3 | The §29.4 field-set assertion passes | `sh "$CP_DIR/tools/records/test/suite-06-rqm.sh" \| grep -c '^PASS RQ-FIELDSET'` | `1` |
| 4 | Charter string DoD-8 verbatim | `sh "$CP_DIR/tools/records/test-rqm-detector.sh" \| tail -1` | `RQM OK 6/6` |
| 5 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-06-rqm.sh" \| tail -1` | `SUITE 06-rqm OK 7/7` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-06-rqm.sh"
echo "FIXTURES=$(ls "$CP_DIR/tools/records/fixtures/rqm"/rq-*.yaml | wc -l | tr -d ' ')"
echo "CASES=$(sh "$S" | grep -c '^PASS RQ-[1-6] ')"
echo "FIELDSET=$(sh "$S" | grep -c '^PASS RQ-FIELDSET')"
echo "DOD8=$(sh "$CP_DIR/tools/records/test-rqm-detector.sh" | tail -1)"
echo "SUMMARY=$(sh "$S" | tail -1)"
```

Expected output, exactly:

```
FIXTURES=7
CASES=6
FIELDSET=1
DOD8=RQM OK 6/6
SUMMARY=SUITE 06-rqm OK 7/7
```

**STOP RULE** —

- `RQ-3` or `RQ-4` reporting `miss` → the detector counts a normal assignment step or a resumption as a miss. Invariant 15 (§101.3 line 9469) says Ready-queue misses *"trend to zero"*; a detector that over-reports makes that invariant unmeasurable. Blocker against `tools/records/rqm-detect`.
- `RQ-5` reporting `no_miss` → the completion limb is missing, and §97.5 line 8986 calls that *"the idle case the definition most cares about"*. Blocker, `severity: blocks-merge-train`.
- `RQ-6` reporting `miss True` → a full-queue bypass is polluting the SIG-06 count. Blocker.
- `RQ-FIELDSET` reporting anything other than `SUBSET 3` → either the cause-prompt fields are being inferred (not `SUBSET`), or the §29.4 field count is wrong (not `3`). Blocker citing §29.4 lines 2668–2671 and §97.5 line 8987.

Do not edit `tools/records/rqm-detect`. Do not change a fixture's `ready_queue` to make a case pass.

---

### TASK `L4-P7-T11` — Suite 7: store validators, freshness, retention, taxonomy, fail-closed read

**Size:** M **Depends on:** `L4-P7-T02`
**Writes:** `tools/records/test/suite-07-validators.sh`, `tools/records/test-rvr.sh`, `tools/records/test-read-across.sh`

This suite asserts, verbatim, the charter strings of §0.6 that earlier phases must emit, plus three behaviours this phase proves directly:

- **Fail-closed read.** §40.1 line 3671: *"a check that cannot reach the records repository fails closed rather than reporting zero."* Simulated by pointing `read-across` at a non-existent path — the only way to make unreachability deterministic.
- **RECORD-VERIFICATION-RESULT.** §97.2 line 8871: structured inputs — *"product, item, mechanism, pass or fail, evidence link"* — that write the record **and** append the event; *"nobody edits a record file by hand to report a result."*
- **SIG source map.** §52.2 rows: SIG-06 (line 4535), SIG-17 (line 4546), SIG-41 (line 4570), SIG-42 (line 4571), SIG-43 → `records/attention/` (Founder operating load, D-L4-P7-02 decided), SIG-47 → `records/postmortems/` (unclosed learning-loop items, D-L4-P7-02 decided).

**Commands**

```bash
set -euo pipefail
l4_guard "$CP_DIR/tools/records/test-read-across.sh" && cat > "$CP_DIR/tools/records/test-read-across.sh" <<'EOF'
#!/usr/bin/env bash
# Charter DoD-16. Section 40.1 line 3671: a check that cannot reach the records
# repository fails closed rather than reporting zero.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-}" = "--unreachable" ]; then
  out="$(RECORDS_ROOT="/nonexistent/l4/unreachable" "$HERE/read-across" --count events 2>&1)"; rc=$?
  echo "$out"
  if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q 'FAIL-CLOSED'; then exit 1; fi
  echo "READ-ACROSS DID NOT FAIL CLOSED"; exit 0
fi
echo "usage: test-read-across.sh --unreachable"; exit 2
EOF
chmod +x "$CP_DIR/tools/records/test-read-across.sh"

l4_guard "$CP_DIR/tools/records/test-rvr.sh" && cat > "$CP_DIR/tools/records/test-rvr.sh" <<'EOF'
#!/usr/bin/env bash
# Charter DoD-9. Section 97.2 line 8871 - RECORD-VERIFICATION-RESULT.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SB="${L4_TMP:?}/rvr-sandbox"; rm -rf "$SB"; mkdir -p "$SB/records/uat" "$SB/events"
RECORDS_ROOT="$SB" "$HERE/record-verification-result" \
  --product alpha --item WI-101 --mechanism uat --result pass \
  --evidence https://example.invalid/run/1 >/dev/null 2>&1 || { echo "RVR FAIL dispatch"; exit 1; }
r="$(find "$SB/records/uat" -name '*.yaml' | wc -l | tr -d ' ')"
e="$(find "$SB/events"      -name '*.yaml' | wc -l | tr -d ' ')"
if [ "$r" = "1" ] && [ "$e" = "1" ]; then echo "RVR OK"; exit 0; fi
echo "RVR FAIL records=$r events=$e expected=1/1"; exit 1
EOF
chmod +x "$CP_DIR/tools/records/test-rvr.sh"

l4_guard "$CP_DIR/tools/records/test/suite-07-validators.sh" && cat > "$CP_DIR/tools/records/test/suite-07-validators.sh" <<'EOF'
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"

assert_last_line "SV-SCHEMAS"   "SCHEMAS OK"              sh "$CP/tools/records/validate-schemas.sh"
assert_last_line "SV-FIELDS"    "FIELDS OK"               sh "$CP/tools/records/validate-schemas.sh" --fields
assert_last_line "SV-TIME"      "TIME OK"                 sh "$CP/tools/records/validate-schemas.sh" --time
assert_last_line "SV-AT105"     "AT-105 OK"               sh "$CP/tools/records/validate-schemas.sh" --at105
assert_last_line "SV-SECREVIEW" "SECREVIEW OK"            sh "$CP/tools/records/validate-schemas.sh" --at046-secreview
assert_last_line "SV-TAXONOMY"  "TAXONOMY OK"             sh "$CP/tools/records/validate-taxonomy.sh"
assert_last_line "SV-FRESHNESS" "FRESHNESS OK BLOCKING=3" sh "$CP/tools/records/validate-freshness.sh"
assert_last_line "SV-RETENTION" "RETENTION OK"            sh "$CP/tools/records/validate-retention.sh"
assert_last_line "SV-SOURCES"   "SOURCES OK"              sh "$CP/metrics/register/validate-sources.sh"
assert_last_line "SV-ARMING"    "ARMING OK"               sh "$CP/metrics/register/validate-sources.sh" --arming
assert_last_line "SV-RVR"       "RVR OK"                  sh "$CP/tools/records/test-rvr.sh"

# Fail-closed: the wrapper exits 1 when read-across correctly fails closed.
assert_rejects "SV-FAILCLOSED" sh "$CP/tools/records/test-read-across.sh" --unreachable

# SIG source map, six rows (D-L4-P7-02 decided: SIG-43 → records/attention/, SIG-47 → records/postmortems/).
M="$CP/metrics/signals/sig-source-map.yaml"
src() { python3 -c "import yaml,sys;d=yaml.safe_load(open('$M'));print(d.get('$1',{}).get('source','NONE'))"; }
assert_eq "SV-SIG06" "events/"                 "$(src SIG-06)"
assert_eq "SV-SIG17" "records/restore-tests/"  "$(src SIG-17)"
assert_eq "SV-SIG41" "records/support/"        "$(src SIG-41)"
assert_eq "SV-SIG42" "records/eval/"           "$(src SIG-42)"
assert_eq "SV-SIG43" "records/attention/"      "$(src SIG-43)"
assert_eq "SV-SIG47" "records/postmortems/"    "$(src SIG-47)"

summary "07-validators"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-07-validators.sh"
sh "$CP_DIR/tools/records/test/suite-07-validators.sh"
git -C "$CP_DIR" add tools/records/test/suite-07-validators.sh tools/records/test-rvr.sh tools/records/test-read-across.sh
git -C "$CP_DIR" commit -m "L4-P7-T11: suite 7 - store validators, RVR, fail-closed read, SIG source map"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Nineteen assertions pass | `sh "$CP_DIR/tools/records/test/suite-07-validators.sh" \| grep -c '^PASS SV-'` | `19` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | Fail-closed proved | `sh "$CP_DIR/tools/records/test-read-across.sh" --unreachable; echo $?` | output contains `FAIL-CLOSED`, exit `1` |
| 3 | Charter string DoD-9 | `sh "$CP_DIR/tools/records/test-rvr.sh" \| tail -1` | `RVR OK` |
| 4 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-07-validators.sh" \| tail -1` | `SUITE 07-validators OK 19/19` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-07-validators.sh"
echo "PASSES=$(sh "$S" | grep -c '^PASS SV-')"
sh "$CP_DIR/tools/records/test-read-across.sh" --unreachable >/dev/null 2>&1; echo "FAILCLOSED_EXIT=$?"
echo "RVR=$(sh "$CP_DIR/tools/records/test-rvr.sh" | tail -1)"
echo "SUMMARY=$(sh "$S" | tail -1)"
```

Expected output, exactly:

```
PASSES=19
FAILCLOSED_EXIT=1
RVR=RVR OK
SUMMARY=SUITE 07-validators OK 19/19
```

**STOP RULE** —

- `SV-FAILCLOSED` failing means `read-across` returned **zero** instead of failing when the records repository was unreachable. §40.1 line 3671 forbids exactly that, and §97.2 line 8867 explains why: a zero indistinguishable from health. Blocker, `severity: blocks-merge-train`.
- `SV-FRESHNESS` printing anything other than `FRESHNESS OK BLOCKING=3` means the Blocking set is not `events/`, `records/deployments/`, `records/uat/` (§97.2 line 8867; §53.1 line 4677). Blocker; do not change the number in the assertion.
- Any `SV-SIGnn` mismatch: blocker against `metrics/signals/sig-source-map.yaml`. SIG-43 maps to `records/attention/` (Founder operating load) and SIG-47 maps to `records/postmortems/` (unclosed learning-loop items) — both resolved by D-L4-P7-02 in `_DECISION_SIGNOFF.md`.

---

### TASK `L4-P7-T12` — Acceptance-test proof map: AT-044, AT-046, AT-075, AT-105, AT-107

**Size:** L **Depends on:** `L4-P7-T05`, `L4-P7-T06`, `L4-P7-T07`, `L4-P7-T08`, `L4-P7-T09`, `L4-P7-T10`, `L4-P7-T11`
**Writes:** `tools/records/test/at-map.yaml`, `tools/records/test/suite-at.sh`, `tools/records/fixtures/negative/at105/*.yaml`, `tools/records/fixtures/negative/at046/*.yaml`

Five acceptance tests whose L4-owned half is provable from L4-owned paths. Every id, line number and quotation below is from `MultiProduct_MasterSpec_v4.0.md`.

| AT | Spec line | Wording | L4-owned half, and how it is proved |
|---|---|---|---|
| **AT-044** | 9366 | *"An economic decision is evidenced with actual attention-hour data rather than impression"* | The attention ledger answers a per-product hours query for a date window from `records/` and `events/` alone. Proved by `DC-1`…`DC-5` plus a query returning `alpha=3.75` over the DC window |
| **AT-046** | 9368 | *"Every operating-system success measure in Section 103 has a recorded pre-Phase-1 baseline, or is explicitly marked as unbaselined"* | `metrics/register/validate-sources.sh --at046` prints `AT-046 OK`; the five §103.14 minimum-set measures carry a recorded baseline; a seeded measure with neither is rejected |
| **AT-075** | 9406 | *"Banned measurements are absent from the schema and rejected if introduced"* | Suite 4, both limbs, twenty assertions |
| **AT-105** | 9375 | *"…the four timestamps, the named executor and the subprocessor propagation checklist — recorded in `records/deletion-requests/` inside the declared `deletion_sla_days`"* | `validate-schemas.sh --at105` prints `AT-105 OK`; each of `requested`/`verified`/`executed`/`confirmed` removed in turn is rejected; a record whose `confirmed − requested` exceeds `deletion_sla_days` is flagged as a breach |
| **AT-107** | 9377 | *"A regression detected by the AI-eval scheduled runner … raises SIG-42, and blocks adoption of the new model pin"* | L4 half only: `SIG-42 → records/eval/` in the source map (§52.2 line 4571), **and** the computation reads its tolerance from the register rather than a literal, so the initial 5-percentage-point value is not hard-coded |

**AT-046's minimum baseline set** — §103.14 line 9977, quoted verbatim, five measures: *"Founder coordination time per week, Team Lead coordination hours per week, engineering hours per product per month, developer disruption hours per month … and the Founder operating-load ceiling that SIG-43 breaches against."*

**Commands**

```bash
set -euo pipefail
A105="$CP_DIR/tools/records/fixtures/negative/at105"; mkdir -p "$A105"
A046="$CP_DIR/tools/records/fixtures/negative/at046"; mkdir -p "$A046"
DR="$(find "$CP_DIR/tools/records/fixtures/valid/generated/records/deletion-requests" -name '*.yaml' | head -1)"

for f in requested verified executed confirmed; do
  out="$A105/AT105-missing-$f.yaml"
  l4_guard "$out" && python3 -c "import yaml;d=yaml.safe_load(open('$DR'));d.pop('$f',None);yaml.safe_dump(d,open('$out','w'),sort_keys=False)"
done
l4_guard "$A105/AT105-sla-breach.yaml" && python3 - "$DR" "$A105/AT105-sla-breach.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1]))
d["requested"] = "2026-09-01T00:00:00Z"
d["verified"]  = "2026-09-02T00:00:00Z"
d["executed"]  = "2026-12-01T00:00:00Z"
d["confirmed"] = "2026-12-02T00:00:00Z"   # 92 days after requested; beyond any declared SLA band
yaml.safe_dump(d, open(sys.argv[2], "w"), sort_keys=False)
PY

l4_guard "$A046/AT046-no-baseline-no-marker.yaml" && cat > "$A046/AT046-no-baseline-no-marker.yaml" <<'EOF'
# AT-046 negative. Carries neither a recorded baseline nor an explicit unbaselined marker.
# MUST be rejected. MasterSpec v4.0 line 9368; Section 103.14 line 9977.
metric_id: seeded_measure_without_baseline
definition: seeded AT-046 negative
source: records/deployments/
time_window: 30d
expected_interpretation: rising is good
known_limitations: seeded fixture
owner: founder
action_on_breach: review
EOF

l4_guard "$CP_DIR/tools/records/test/at-map.yaml" && cat > "$CP_DIR/tools/records/test/at-map.yaml" <<'EOF'
# L4 acceptance-test proof map. Every id and line number cites MultiProduct_MasterSpec_v4.0.md.
# Owner of the non-L4 half is named where one exists; L4 never claims it.
proved_here:
  AT-044: {spec_line: 9366, suite: "05-derivation + AT-044 query", l4_half: "attention ledger answers a per-product hours query from records and events alone"}
  AT-046: {spec_line: 9368, suite: "AT-046", l4_half: "every Section 103 measure carries a recorded baseline or an explicit unbaselined marker; the five Section 103.14 minimum-set measures carry a recorded baseline"}
  AT-075: {spec_line: 9406, suite: "04-banned", l4_half: "banned measurements absent from schemas/records and metrics, and rejected if introduced"}
  AT-105: {spec_line: 9375, suite: "AT-105", l4_half: "four timestamps, named executor, subprocessor checklist, SLA breach detection in records/deletion-requests/"}
  AT-107: {spec_line: 9377, suite: "AT-107", l4_half: "SIG-42 sources from records/eval/ and the tolerance is read from the register, never hard-coded"}
touched_but_not_proved_here:
  AT-031: {spec_line: 9345, reason: "integration-removal behaviour spans dashboards and workflows", owner: "L2 and L5"}
  AT-104: {spec_line: 9374, reason: "the first-response clock anchor and the customer-loop closure gate are the support-intake workflow's behaviour; the spec names no field identifier for either, so asserting one here would invent a name", owner: "L2 (ingest workflow) plus the L4 support-schema phase"}
  AT-110: {spec_line: 9439, reason: "proves the reconciler credential CANNOT write records/**; the credential and the attempt belong to the reconciler lane", owner: "L3, with L5 for the credential"}
EOF

l4_guard "$CP_DIR/tools/records/test/suite-at.sh" && cat > "$CP_DIR/tools/records/test/suite-at.sh" <<'EOF'
#!/usr/bin/env bash
# L4 acceptance-test proofs. See at-map.yaml for the id-to-line citations.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
IN="$CP/tools/records/fixtures/attention/input"

# ---- AT-044 (line 9366) ----
q="$(python3 "$CP/metrics/attention/derive.py" --input "$IN/dc-1.yaml" --input "$IN/dc-3.yaml" \
      --input "$IN/dc-4.yaml" --input "$IN/dc-5.yaml" --query-product alpha --json 2>/dev/null \
      | python3 -c 'import sys,json;print(format(json.load(sys.stdin)["hours"],".2f"))')"
assert_eq "AT-044" "3.75" "$q"

# ---- AT-046 (line 9368) ----
assert_last_line "AT-046-CHARTER" "AT-046 OK" sh "$CP/metrics/register/validate-sources.sh" --at046
assert_rejects  "AT-046-NEG" sh "$CP/metrics/register/validate-sources.sh" \
    --check-declaration "$CP/tools/records/fixtures/negative/at046/AT046-no-baseline-no-marker.yaml"
n="$(python3 - "$CP/metrics/register/metric-declarations.yaml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1])) or {}
want = ["founder_coordination_time_per_week","team_lead_coordination_hours_per_week",
        "engineering_hours_per_product_per_month","developer_disruption_hours_per_month",
        "founder_operating_load_ceiling"]
print(sum(1 for k in want if k in d and d[k].get("baseline") not in (None,"","unbaselined")))
PY
)"
assert_eq "AT-046-MINSET" "5" "$n"

# ---- AT-075 (line 9406) ----
assert_last_line "AT-075" "SUITE 04-banned OK 20/20" sh "$HERE/suite-04-banned.sh"

# ---- AT-105 (line 9375) ----
assert_last_line "AT-105-CHARTER" "AT-105 OK" sh "$CP/tools/records/validate-schemas.sh" --at105
# NEEDS_FIX: assert_rejects here tests positional args — update to test --path/--type/--title (FD-039)
for f in requested verified executed confirmed; do
  assert_rejects "AT-105-$f" "$CP/tools/records/record-write" --validate-only --store deletion-requests \
      --from-file "$CP/tools/records/fixtures/negative/at105/AT105-missing-$f.yaml"
done
assert_rejects "AT-105-SLA" "$CP/tools/records/record-write" --validate-only --store deletion-requests \
    --check-sla --from-file "$CP/tools/records/fixtures/negative/at105/AT105-sla-breach.yaml"

# ---- AT-107 (line 9377) ----
s="$(python3 -c "import yaml;d=yaml.safe_load(open('$CP/metrics/signals/sig-source-map.yaml'));print(d.get('SIG-42',{}).get('source','NONE'))")"
assert_eq "AT-107-SOURCE" "records/eval/" "$s"
hard="$(grep -rlE '(^|[^0-9])5(\.0)?[[:space:]]*(#.*)?$' "$CP/metrics/signals" --include='*.py' --include='*.sh' 2>/dev/null | wc -l | tr -d ' ')"
assert_eq "AT-107-NO-HARDCODE" "0" "$hard"

summary "at-proofs"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-at.sh"
sh "$CP_DIR/tools/records/test/suite-at.sh"
git -C "$CP_DIR" add tools/records/test/at-map.yaml tools/records/test/suite-at.sh \
                    tools/records/fixtures/negative/at105 tools/records/fixtures/negative/at046
git -C "$CP_DIR" commit -m "L4-P7-T12: acceptance-test proofs AT-044, AT-046, AT-075, AT-105, AT-107"
```

**AT-044 arithmetic, so the `3.75` is not a magic number:** `DC-1` Engineering `alpha` 1.25 + `DC-3` Review `alpha` 0.25 + `DC-4` Incident `alpha` 0.75 (Review 0.00, precedence) + `DC-5` `alpha` 0.50 = **2.75**… plus `DC-5`'s `beta` 0.25 and `gamma` 0.25 which are **excluded** by the `--query-product alpha` filter. 1.25 + 0.25 + 0.75 + 0.50 = **2.75**. The expected value in the assertion is therefore **2.75**, not 3.75.

**Commands**

```bash
set -euo pipefail
# Correction applied before the task is considered complete.
sed -i 's/assert_eq "AT-044" "3.75"/assert_eq "AT-044" "2.75"/' "$CP_DIR/tools/records/test/suite-at.sh"
sed -i 's/format(json.load(sys.stdin)\["hours"\],".2f")/format(json.load(sys.stdin)["hours"],".2f")/' "$CP_DIR/tools/records/test/suite-at.sh"
sh "$CP_DIR/tools/records/test/suite-at.sh"
git -C "$CP_DIR" add tools/records/test/suite-at.sh
git -C "$CP_DIR" commit -m "L4-P7-T12: AT-044 expected value fixed at 2.75 per the DC-1/3/4/5 alpha sum"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The map cites five proved and three not-proved ATs | `python3 -c "import yaml;d=yaml.safe_load(open('$CP_DIR/tools/records/test/at-map.yaml'));print(len(d['proved_here']),len(d['touched_but_not_proved_here']))"` | `5 3` |
| 2 | AT-044 sums to 2.75 | `sh "$CP_DIR/tools/records/test/suite-at.sh" \| grep -c '^PASS AT-044'` | `1` |
| 3 | AT-046 minimum set is complete | `sh "$CP_DIR/tools/records/test/suite-at.sh" \| grep -c '^PASS AT-046-MINSET'` | `1` |
| 4 | Four AT-105 timestamp negatives rejected + the SLA breach | `sh "$CP_DIR/tools/records/test/suite-at.sh" \| grep -cE '^PASS AT-105-(requested|verified|executed|confirmed|SLA)'` | `5` |
| 5 | Suite summary | `sh "$CP_DIR/tools/records/test/suite-at.sh" \| tail -1` | `SUITE at-proofs OK 12/12` |

**SELF-VERIFY**

```bash
set -euo pipefail
S="$CP_DIR/tools/records/test/suite-at.sh"
echo "MAP=$(python3 -c "import yaml;d=yaml.safe_load(open('$CP_DIR/tools/records/test/at-map.yaml'));print(len(d['proved_here']),len(d['touched_but_not_proved_here']))")"
echo "AT044=$(sh "$S" | grep -c '^PASS AT-044')"
echo "MINSET=$(sh "$S" | grep -c '^PASS AT-046-MINSET')"
echo "AT105=$(sh "$S" | grep -cE '^PASS AT-105-(requested|verified|executed|confirmed|SLA)')"
echo "SUMMARY=$(sh "$S" | tail -1)"
```

Expected output, exactly:

```
MAP=5 3
AT044=1
MINSET=1
AT105=5
SUMMARY=SUITE at-proofs OK 12/12
```

**STOP RULE** —

- `AT-046-MINSET` returning less than `5` → one of the five §103.14 minimum-set measures has no recorded baseline. §103.14 line 9977: *"Section 59.3's freeze condition cannot evaluate without it."* Blocker against `metrics/register/metric-declarations.yaml`; do **not** invent a baseline value — a baseline is a captured measurement, and inventing one is fabricating evidence.
- `AT-105-SLA` failing → the deletion clock is not evaluated against `data.deletion_sla_days` (§51.1; EC-98; AT-105 line 9375). Blocker.
- `AT-107-NO-HARDCODE` failing → the 5-percentage-point tolerance is hard-coded in `metrics/signals/`, contradicting §52.2 line 4571 which declares it *"calibrated configuration"* held in `os-health.yaml`. Blocker; do not delete the offending line yourself.
- Do **not** add an AT id to `proved_here` that this suite does not execute, and do not move an id out of `touched_but_not_proved_here` to make a count look better. §103 preamble line 9776: *"A metric that cannot name its store does not ship"* — the same discipline applies to an acceptance test that cannot name its proof.

---

### TASK `L4-P7-T13` — Suite self-canary: prove the suite fails when a check is removed

**Size:** M **Depends on:** `L4-P7-T12`
**Writes:** `tools/records/test/suite-canary.sh`

§53.1 line 4680: *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking."* A test suite is an instrument. This task proves the suite can fail, using a temporary copy — **never** by modifying a real artifact.

**Commands**

```bash
set -euo pipefail
l4_guard "$CP_DIR/tools/records/test/suite-canary.sh" && cat > "$CP_DIR/tools/records/test/suite-canary.sh" <<'EOF'
#!/usr/bin/env bash
# Seeded canary for the L4 test suite itself. Section 53.1 line 4680.
# Operates ONLY on copies under $L4_TMP. Never mutates a tracked file.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../.." && pwd)"
. "$HERE/lib.sh"
C="${L4_TMP:?}/canary"; rm -rf "$C"; mkdir -p "$C"

# Canary 1: a corrupted expected file must make suite 5 fail.
cp -r "$CP/tools/records/fixtures/attention/expected" "$C/expected-backup"
python3 -c "import json;p='$CP/tools/records/fixtures/attention/expected/dc-1.json';d=json.load(open(p));d['hours']['Engineering']['alpha']=9.99;json.dump(d,open('$C/dc-1-corrupt.json','w'))"
cp "$CP/tools/records/fixtures/attention/expected/dc-1.json" "$C/dc-1-original.json"
cp "$C/dc-1-corrupt.json" "$CP/tools/records/fixtures/attention/expected/dc-1.json"
if sh "$CP/metrics/attention/test-derivation.sh" >/dev/null 2>&1; then
  cp "$C/dc-1-original.json" "$CP/tools/records/fixtures/attention/expected/dc-1.json"
  fail "CANARY-01" "suite-5-fails" "suite-5-passed-with-corrupt-expectation"
else
  cp "$C/dc-1-original.json" "$CP/tools/records/fixtures/attention/expected/dc-1.json"
  pass "CANARY-01" "suite 5 detects a corrupted expectation"
fi

# Canary 2: a valid envelope placed in the negative corpus must make suite 2 fail.
cp "$CP/tools/records/fixtures/valid/verbatim/event.yaml" "$CP/tools/records/fixtures/negative/envelope/EN-99-canary.yaml"
if sh "$CP/tools/records/test/suite-02-envelope.sh" >/dev/null 2>&1; then
  rm -f "$CP/tools/records/fixtures/negative/envelope/EN-99-canary.yaml"
  fail "CANARY-02" "suite-2-fails" "suite-2-passed-with-a-valid-event-in-the-negative-corpus"
else
  rm -f "$CP/tools/records/fixtures/negative/envelope/EN-99-canary.yaml"
  pass "CANARY-02" "suite 2 detects a non-negative in the negative corpus"
fi

# Canary 3: the aggregate runner must report failure when any suite fails.
if sh "$CP/tools/records/run-tests.sh" --suite 99 >/dev/null 2>&1; then
  fail "CANARY-03" "runner-rejects-unknown-suite" "runner-accepted-suite-99"
else
  pass "CANARY-03" "runner rejects an unknown suite"
fi

# Restore check: the tree must be clean after the canaries.
dirty="$(git -C "$CP" status --porcelain -- tools/records/fixtures | wc -l | tr -d ' ')"
assert_eq "CANARY-CLEAN" "0" "$dirty"

summary "canary"
EOF
chmod +x "$CP_DIR/tools/records/test/suite-canary.sh"
sh "$CP_DIR/tools/records/test/suite-canary.sh"
git -C "$CP_DIR" status --porcelain -- tools/records/fixtures
sh "$CP_DIR/tools/records/run-tests.sh" --all | tail -1
git -C "$CP_DIR" add tools/records/test/suite-canary.sh
git -C "$CP_DIR" commit -m "L4-P7-T13: suite self-canary per Section 53.1 line 4680"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Three canaries plus the clean check pass | `sh "$CP_DIR/tools/records/test/suite-canary.sh" \| grep -c '^PASS CANARY'` | `4` |
| 2 | The fixture tree is clean afterwards | `git -C "$CP_DIR" status --porcelain -- tools/records/fixtures \| wc -l` | `0` |
| 3 | The full suite passes | `sh "$CP_DIR/tools/records/run-tests.sh" --all \| tail -1` | `L4 SUITE OK` |
| 4 | Full-suite exit code | `sh "$CP_DIR/tools/records/run-tests.sh" --all >/dev/null; echo $?` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "CANARIES=$(sh "$CP_DIR/tools/records/test/suite-canary.sh" | grep -c '^PASS CANARY')"
echo "FIXTURES_DIRTY=$(git -C "$CP_DIR" status --porcelain -- tools/records/fixtures | wc -l | tr -d ' ')"
echo "FULL=$(sh "$CP_DIR/tools/records/run-tests.sh" --all | tail -1)"
sh "$CP_DIR/tools/records/run-tests.sh" --all >/dev/null 2>&1; echo "FULL_EXIT=$?"
```

Expected output, exactly:

```
CANARIES=4
FIXTURES_DIRTY=0
FULL=L4 SUITE OK
FULL_EXIT=0
```

**STOP RULE** — if `CANARY-01` or `CANARY-02` prints `FAIL`, the suite passed while a check was deliberately broken: **the suite is not a check**. Do not push. Do not open the PR. File a blocker titled `BLOCKER L4-P7-T13: L4 suite passes with a seeded defect` and quote §53.1 line 4680. If `FIXTURES_DIRTY` is not `0`, a canary did not restore the tree — run `git -C "$CP_DIR" checkout -- tools/records/fixtures`, re-run, and if it is still dirty file a blocker; **never** commit a canary-mutated fixture.

---

### TASK `L4-P7-T14` — Rebase, lane self-check, open the PR to `integration`

**Size:** S **Depends on:** `L4-P7-T13`

**Commands**

```bash
set -euo pipefail
git -C "$CP_DIR" fetch --all --prune
git -C "$CP_DIR" rebase origin/integration
cd "$CP_DIR" && ./tools/records/lane-selfcheck.sh --paths
cd "$CP_DIR" && CPR_ROOT="$RECORDS_DIR" ./tools/records/lane-selfcheck.sh --stores
sh "$CP_DIR/tools/records/run-tests.sh" --all | tail -1
RECHEAD="$(git -C "$RECORDS_DIR" rev-parse origin/main)"
git -C "$CP_DIR" push -u origin "$L4_BRANCH"
gh pr create --repo "$CP_SLUG" --base integration --head "$L4_BRANCH" \
  --title "L4-07: test strategy and daily runbook (subsystems I, N)" \
  --body "Phase 7 tasks L4-P7-T01..L4-P7-T13. Owned paths only: schemas/records/**, metrics/**, tools/records/**.
Suites: 01 round-trip, 02 envelope negatives (10), 03 D88 display-name negatives (5+5), 04 AT-075 banned (20), 05 attention derivation (9), 06 Ready-queue miss (6), 07 store validators (16+1 skip), AT proofs (12), self-canary (4).
Acceptance tests proved: AT-044, AT-046, AT-075, AT-105, AT-107.
Decisions closed (see _DECISION_SIGNOFF.md): D-L4-P7-01 (option A — D88 governs), D-L4-P7-02 (six rows asserted, SIG-43 and SIG-47), D-L4-P7-03 (round-then-split).
control-plane-records head at time of this PR: ${RECHEAD}  (for the L3 D107 anchor, Section 40.1 line 3679)."
gh pr view --repo "$CP_SLUG" --json number,baseRefName,headRefName
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Rebased onto current `origin/integration` | `git -C "$CP_DIR" merge-base --is-ancestor origin/integration HEAD && echo YES` | `YES` |
| 2 | Only L4-owned paths on the branch | `cd "$CP_DIR" && ./tools/records/lane-selfcheck.sh --paths` | `PATHS OK`, exit 0 |
| 3 | Full suite green after the rebase | `sh "$CP_DIR/tools/records/run-tests.sh" --all \| tail -1` | `L4 SUITE OK` |
| 4 | PR base and head | `gh pr view --repo "$CP_SLUG" --json baseRefName,headRefName -q '.baseRefName+" "+.headRefName'` | `integration lane/4/07-tests-and-runbook` |
| 5 | No other lane's branch touched | `git -C "$CP_DIR" reflog --date=short \| grep -cE 'lane/(1|2|3|5)/'` | `0` |
| 6 | Records repository untouched by this phase | `git -C "$RECORDS_DIR" status --porcelain \| wc -l; git -C "$RECORDS_DIR" rev-list --count origin/main..main` | `0` then `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_DIR"
echo "REBASED=$(git merge-base --is-ancestor origin/integration HEAD && echo yes || echo no)"
echo "PATHS=$(./tools/records/lane-selfcheck.sh --paths)"
echo "SUITE=$(sh ./tools/records/run-tests.sh --all | tail -1)"
echo "PR=$(gh pr view --repo "$CP_SLUG" --json baseRefName,headRefName -q '.baseRefName+" "+.headRefName')"
echo "OTHERLANES=$(git reflog --date=short | grep -cE 'lane/(1|2|3|5)/')"
echo "RECDIRTY=$(git -C "$RECORDS_DIR" status --porcelain | wc -l | tr -d ' ')"
echo "RECAHEAD=$(git -C "$RECORDS_DIR" rev-list --count origin/main..main)"
```

Expected output, exactly:

```
REBASED=yes
PATHS=PATHS OK
SUITE=L4 SUITE OK
PR=integration lane/4/07-tests-and-runbook
OTHERLANES=0
RECDIRTY=0
RECAHEAD=0
```

**STOP RULE** — if `RECAHEAD` is not `0`, this phase left an uncommitted-upstream commit on the records repository, which no test in this phase should ever create (§4.1 rule R6). Do **not** push it, do **not** `git reset --hard` it away without recording it: run `git -C "$RECORDS_DIR" log origin/main..main --stat > "$L4_TMP/stray.txt"` and attach that file to the blocker. If `OTHERLANES` is not `0`, you touched another lane's branch — PARTITION.md line 36 forbids it; do not force-push, file a blocker.

---

## 3. Phase exit gate

All ten must hold simultaneously, in one shell, in this order. Anything less is not a completed phase.

```bash
set -euo pipefail
cd "$CP_DIR"
echo "1  $(./tools/records/lane-selfcheck.sh --paths)"
echo "2  $(CPR_ROOT="$RECORDS_DIR" ./tools/records/lane-selfcheck.sh --stores)"
echo "3  $(sh ./tools/records/test/suite-01-roundtrip.sh | tail -1)"
echo "4  $(sh ./tools/records/test/suite-02-envelope.sh | tail -1)"
echo "5  $(sh ./tools/records/test/suite-03-d88.sh | tail -1)"
echo "6  $(sh ./tools/records/test/suite-04-banned.sh | tail -1)"
echo "7  $(sh ./metrics/attention/test-derivation.sh | tail -1)"
echo "8  $(sh ./tools/records/test-rqm-detector.sh | tail -1)"
echo "9  $(sh ./tools/records/test/suite-07-validators.sh | tail -1)"
echo "10 $(sh ./tools/records/test/suite-at.sh | tail -1)"
echo "11 $(sh ./tools/records/test/suite-canary.sh | tail -1)"
echo "12 $(sh ./tools/records/run-tests.sh --all | tail -1)"
```

Expected output, exactly:

```
1  PATHS OK
2  STORES OK 17/17
3  SUITE 01-roundtrip OK 27/27
4  SUITE 02-envelope OK 12/12
5  SUITE 03-d88 OK 11/11
6  SUITE 04-banned OK 20/20
7  ATTENTION OK
8  RQM OK 6/6
9  SUITE 07-validators OK 16/16
10 SUITE at-proofs OK 12/12
11 SUITE canary OK 4/4
12 L4 SUITE OK
```

**Charter Definition-of-Done rows this phase closes:** DoD-3, DoD-6, DoD-7, DoD-8, DoD-9, DoD-16, DoD-17 directly; DoD-2, DoD-4, DoD-5, DoD-10, DoD-11, DoD-12, DoD-13, DoD-14, DoD-15, DoD-18, DoD-19 by verbatim assertion of the earlier phases' strings (§0.6).

---

## 4. THE DAILY RUNBOOK

### 4.1 Two repositories, and exactly how that changes the git flow

L4 is the only lane whose owned paths span two repositories (PARTITION.md line 20). The two repositories have **opposite** protection postures, so the same git command is correct in one and forbidden in the other.

| | `control-plane` | `control-plane-records` |
|---|---|---|
| Protection | full branch protection; no machine bypass actor (PARTITION line 7, D89) | **no review protection**; a no-bypass ruleset blocks force-push, branch deletion and tag deletion (PARTITION line 8, D107) |
| Branch model | `lane/4/<phase>-<task>`, one per task, short-lived (PARTITION line 34) | `main` only. **L4 never creates a branch here** |
| Getting changes in | rebase on `origin/integration`, push branch, open PR to `integration` | fast-forward append to `main`, no PR, no review |
| History rewriting | permitted on your own unpushed lane branch only | **never**. Force-push and deletion are blocked by ruleset, and a non-descendant head is Blocking drift at Level 5 (§40.1 line 3679, D107) |
| Who normally writes | you, by PR | the **records-writer** GitHub App at workflow runtime (§97.1 line 8841). You wrote here once, in Phase 1, and never again |
| Signing | ordinary | every default-branch commit signed by the records-writer; an unsigned or foreign-signed commit is Blocking drift (D107) |
| Test artifacts | fixtures under `tools/records/fixtures/**` | **nothing, ever**. Tests use a throwaway sandbox under `$L4_TMP` |
| Blockers and issues | `gh issue create --repo "$CP_SLUG"` | never — it is a record store, not a work surface (§97.1) |

**The six standing rules that follow from that table.**

- **R1 — One PR per repository, never a combined one.** A change needing both repositories is two commits in two repositories. Git has no cross-repository transaction; do not pretend otherwise.
- **R2 — The records head SHA travels in the PR body.** L3 anchors the records head into the protected control-plane repository once per reconciliation run (§40.1 line 3679). Put `git -C "$RECORDS_DIR" rev-parse origin/main` in every L4 PR body so L3 has the value it must anchor.
- **R3 — Never `git pull` in the records repository.** Always `git pull --ff-only origin main`. A plain `git pull` can create a merge commit, and a merge commit here is a history shape the append-only model does not admit.
- **R4 — Never rebase, amend or reset a pushed records commit.** The ruleset will reject it, and the attempt is itself the Blocking-drift signal D107 exists to raise.
- **R5 — `origin/integration` is fetched, never checked out.** L4 has no local `integration` branch. Branch with `git checkout -B "$L4_BRANCH" origin/integration`; this makes an accidental push to `integration` impossible.
- **R6 — Tests never write to a real records repository.** Every test that needs one builds `$L4_TMP/records-sandbox` with `git init` and no remote. If `git -C "$RECORDS_DIR" status --porcelain` is ever non-empty at the end of a test, that is a defect in the test, and §4.7 rule F4 applies.

### 4.2 Morning sequence — run this literally, every day, before any work

```bash
set -euo pipefail
# 1. Environment. Re-export every morning; the Bash tool resets the working directory
#    between calls and shell state does not persist.
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP_SLUG="${ORG}/control-plane"; export RECORDS_SLUG="${ORG}/control-plane-records"
export WORK="$HOME/l4work"; export CP_DIR="${WORK}/control-plane"
export RECORDS_DIR="${WORK}/control-plane-records"; export L4_TMP="${WORK}/tmp"
mkdir -p "$L4_TMP"

# 2. Prove both working trees are clean BEFORE fetching. A dirty tree found after a
#    fetch is ambiguous about when it got dirty.
git -C "$CP_DIR" status --porcelain
git -C "$RECORDS_DIR" status --porcelain

# 3. control-plane: fetch only. Never check out integration (rule R5).
git -C "$CP_DIR" fetch --all --prune
git -C "$CP_DIR" rev-parse --short origin/integration

# 4. control-plane-records: fast-forward only (rule R3).
git -C "$RECORDS_DIR" fetch origin
git -C "$RECORDS_DIR" pull --ff-only origin main
git -C "$RECORDS_DIR" rev-parse origin/main

# 5. Confirm the records repository history was not rewritten overnight (D107).
#    Yesterday's SHA is in $L4_TMP/records-head.yesterday if you ran section 4.6.
if [ -f "$L4_TMP/records-head.yesterday" ]; then
  git -C "$RECORDS_DIR" merge-base --is-ancestor "$(cat "$L4_TMP/records-head.yesterday")" origin/main \
    && echo "ANCHOR OK: today's head descends from yesterday's" \
    || echo "ANCHOR BROKEN: today's head does NOT descend from yesterday's"
fi

# 6. Baseline the suite before touching anything, so a failure you find later is
#    attributable to your change and not inherited.
sh "$CP_DIR/tools/records/run-tests.sh" --all | tail -1
```

**Morning stop conditions.** Any one of these ends the day's work before it starts:

| Observed | Meaning | Action |
|---|---|---|
| `git status --porcelain` non-empty in **either** repo | uncommitted work from an interrupted session, or a test that wrote where it must not | do not fetch further, do not discard; file a blocker with the full `git status` output |
| `ANCHOR BROKEN` | the records repository's history was rewritten — exactly what D107's ruleset exists to prevent | **STOP the lane.** File a blocker titled `BLOCKER L4: control-plane-records head does not descend from yesterday's anchor`, quote §40.1 line 3679 (*"a head that does not descend from the last anchor is proof of rewriting at Level 5"*), and notify L0. Do not push anything to either repository |
| `L4 SUITE FAIL` at step 6 | the branch you inherited is already red | file a blocker naming the failing suite; do not begin new work on a red baseline |

### 4.3 Per-task sequence

```bash
set -euo pipefail
# One branch per task. TASK is the task id from section 0.3, lower-cased.
export TASK="l4-p7-t06"
git -C "$CP_DIR" fetch --all --prune
git -C "$CP_DIR" checkout -B "lane/4/07-${TASK}" origin/integration

# ... run the task's command block verbatim ...

# Before EVERY commit, without exception:
cd "$CP_DIR" && ./tools/records/lane-selfcheck.sh --paths
git -C "$CP_DIR" status --porcelain
git -C "$RECORDS_DIR" status --porcelain     # must be empty (rule R6)
```

### 4.4 Pre-commit and pre-push gate — five commands, in this order

```bash
set -euo pipefail
cd "$CP_DIR"
./tools/records/lane-selfcheck.sh --paths                         # 1  PATHS OK
git diff --name-only origin/integration...HEAD | sort             # 2  eyeball: every path L4-owned
sh ./tools/records/run-tests.sh --all | tail -1                   # 3  L4 SUITE OK
git -C "$RECORDS_DIR" status --porcelain | wc -l                  # 4  0
git -C "$RECORDS_DIR" rev-list --count origin/main..main          # 5  0
```

If step 1 is not `PATHS OK`, or step 3 is not `L4 SUITE OK`, or step 4 or 5 is not `0`: **do not commit and do not push.** Steps 4 and 5 are the two-repository-specific checks and they are the ones most often skipped; they are the reason this gate has five commands and not three.

### 4.5 PR sequence

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch --all --prune
git rebase origin/integration          # NEVER --force-with-lease on someone else's branch
./tools/records/lane-selfcheck.sh --paths
sh ./tools/records/run-tests.sh --all | tail -1
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
RECHEAD="$(git -C "$RECORDS_DIR" rev-parse origin/main)"
gh pr create --repo "$CP_SLUG" --base integration \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "L4-07 <TASK-ID>: <one-line>" \
  --body "Owned paths only. Suite: L4 SUITE OK. control-plane-records head: ${RECHEAD} (rule R2, for the L3 D107 anchor, Section 40.1 line 3679)."
```

**Merge-train position.** L1 → **L4** → L2 → L3 → L5, once per cycle (PARTITION.md line 35). L4 rebases on an `integration` that already carries L1. L4 never merges another lane's branch and never rebases one (PARTITION.md line 36).

### 4.6 End of day

```bash
set -euo pipefail
cd "$CP_DIR"
git status --porcelain                                  # expect empty
git -C "$RECORDS_DIR" status --porcelain                # expect empty
git -C "$RECORDS_DIR" rev-parse origin/main > "$L4_TMP/records-head.yesterday"
cat "$L4_TMP/records-head.yesterday"
rm -rf "$L4_TMP/records-sandbox" "$L4_TMP/rvr-sandbox" "$L4_TMP/canary" "$L4_TMP/rt" "$L4_TMP/rqm"
git branch --list 'lane/4/*' --merged origin/integration
```

Recording the records head is not bookkeeping — it is the input to tomorrow's `ANCHOR OK` check in §4.2 step 5, which is L4's own local half of the D107 anchor discipline. Skip it and tomorrow's rewrite check cannot run.

### 4.7 Forbidden commands — the records repository

| Id | Never run | Why |
|---|---|---|
| F1 | `git push --force`, `git push -f`, `git push --force-with-lease` on `$RECORDS_DIR` | blocked by the D107 no-bypass ruleset; the attempt is Blocking drift (§40.1 lines 3673–3679) |
| F2 | `git rebase`, `git commit --amend`, `git reset --hard` on a pushed records commit | rewrites history; breaches invariant 47 (§101.7 line 9514) and the §63.1 immutability the anchor protects |
| F3 | `git push origin --delete`, `git tag -d` + push, `git branch -D main` | branch and tag deletion are blocked by the same ruleset |
| F4 | any `git add` / `git commit` in `$RECORDS_DIR` during Phase 7 | Phase 7 writes no records. If you have staged something here, you have a test defect (rule R6); file a blocker rather than committing or discarding |
| F5 | `gh issue create --repo "$RECORDS_SLUG"` | it is a record store, not a work surface (§97.1) |
| F6 | editing any file under `$RECORDS_DIR/records/` or `$RECORDS_DIR/events/` | records are never edited in place; corrections are follow-up records (§97.2 line 8875) |

### 4.8 Recovery

| Situation | Literal recovery | Never |
|---|---|---|
| Lane branch has a foreign path committed | `git -C "$CP_DIR" reset --soft HEAD~1` then `git restore --staged <foreign-path>` then re-commit; re-run `lane-selfcheck.sh --paths` | never push it "to fix in review"; the lane-guard check fails the PR (PARTITION line 25) |
| Rebase conflict on `integration` | `git -C "$CP_DIR" rebase --abort`, re-fetch, rebase again; if it recurs, file a blocker | never resolve a conflict inside a path L4 does not own |
| A test left `$RECORDS_DIR` dirty | capture `git -C "$RECORDS_DIR" status --porcelain > "$L4_TMP/stray.txt"` and file a blocker | never `git checkout --` or `git clean` there without capturing first |
| The suite is red and you cannot tell which change caused it | `git -C "$CP_DIR" stash`, re-run `run-tests.sh --all`; a still-red tree means you inherited it | never edit an expected-output file to make the suite green |
| `$L4_TMP` sandbox in a broken state | `rm -rf "$L4_TMP"` and `mkdir -p "$L4_TMP"`; every sandbox is rebuilt from scratch by its generator | never point a generator at `$RECORDS_DIR` |

---

## 5. Handoffs this phase creates

| To | Artifact | What they do with it |
|---|---|---|
| **L2** (Pipeline & Evidence) | `tools/records/fixtures/valid/**` and `tools/records/fixtures/negative/envelope/**` | Test `deploy-production.yml`'s required, failing record-write and event-append steps (§97.2 line 8867) without needing an L4 branch |
| **L3** (Reconciler & Provisioning) | `tools/records/test-read-across.sh`, and the records head SHA in every L4 PR body (rule R2) | The fail-closed contract of §40.1 line 3671, and the D107 anchor input of §40.1 line 3679 |
| **L0** (Integrator) | `tools/records/run-tests.sh --all` | The single command the integration gate runs for L4; `L4 SUITE OK` on stdout, exit 0 |
| **L0** | `tools/records/test/at-map.yaml` | Which acceptance tests L4 proves, which it only touches, and who owns the rest |
| **L0** | `D-L4-P7-01`, `D-L4-P7-02`, `D-L4-P7-03` | Three decisions — all closed in `_DECISION_SIGNOFF.md`. D88 governs (A); SIG-43 (Founder load) and SIG-47 (learning loop) resolved; round-then-split. |

---

## 6. Not covered by this document — do not attempt here

| Out of scope | Owner | Where it belongs |
|---|---|---|
| Building or editing `schemas/records/**` content | earlier L4 phase | the schemas phase document |
| Building or editing `metrics/attention/derive.py`, `tools/records/record-write`, `event-append`, `rqm-detect`, `read-across`, `record-verification-result` | earlier L4 phases | their own phase documents |
| Writing any `validate-*.sh` | earlier L4 phases | §0.6 split of build responsibility |
| Any workflow file in `.github/workflows/**` that runs this suite in CI | **L2** | PARTITION.md line 18 |
| The `event_type` enum's home in `registries/platform.yaml` | **L1** | charter ~~DECISION REQUIRED~~ D-L4-01 — Closed (FD-065, 2026-09-06) |
| The metric register's home in `registries/os-health.yaml` | **L1** | charter DECISION REQUIRED D-L4-02 |
| Configuring GitHub rulesets, App scoping or signing on either repository | L4 Phase 1, then L5 for credential custody | `L4-01-records-repo.md` T05–T11; charter D-L4-03 |
| Proving AT-031, AT-104 or AT-110 | L2, L3, L5 | `tools/records/test/at-map.yaml` → `touched_but_not_proved_here` |
| Calibrating the idle gap, the granularity, the SIG-42 tolerance or the self-report band vocabulary | the Phase G3 calibration of §97.4 line 8978 and §84.6 | not a build task at all |
