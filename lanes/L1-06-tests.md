# L1-06 — Test Strategy for Lane 1 (Registries & Contracts)

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 Registries & Contracts — Subsystems A (control-plane repository) and B (schema validation and CI gate engine), spec Section 99.2.
**Branch prefix:** `lane/1/*` (PARTITION.md, "The five build lanes").
**Paths this lane owns exclusively:** `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`.
**Every file created by this document lives under `validators/registry/tests/**`.** Nothing here writes outside the four owned prefixes.
**Merge position:** L1 merges FIRST in the train (PARTITION.md, "Merge train: L1 → L4 → L2 → L3 → L5").

---

## 0. The one command that runs the whole lane suite

```bash
bash validators/registry/tests/run.sh --all
```

Exit code `0` = lane suite green. Any non-zero = red. The final line of stdout is always exactly one of:

```
LANE1 SUITE: PASS fixtures=<N> valid=<V> invalid=<I> canaries=<C> rules=<R>
LANE1 SUITE: FAIL fixtures=<N> valid=<V> invalid=<I> canaries=<C> rules=<R>
```

Every acceptance criterion in this document is provable by an exit code or by grepping for one of those two literal prefixes, or by a literal string named in the task.

**This lane cannot wire its own CI.** `.github/workflows/**` belongs to L2 and `Makefile` belongs to L0 (PARTITION.md lane table). L1 publishes the invocation contract as an owned artifact at `validators/registry/tests/ci-contract.md` (task **L1-06-15**) and L2 consumes it. A lane never edits a foreign path — PARTITION.md rule 1. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

---

## 1. Why the corpus is built this way

Section 31.2 states the rule this lane applies to itself: *"A verification contract that cannot fail is not a contract."* Section 53.1 states the same rule for the reconciler as the seeded-canary rule, and AT-102 makes it an acceptance test: *"A run reporting zero findings — the canary included — is a **failed** run."* Section 95.4 requires the activation checklist be *"executed for real — including the negative tests."*

Subsystem B is a validator. A validator that has silently stopped validating reports the same green as a validator that is working. The corpus below is therefore built so that **the failure mode of the instrument is louder than the failure mode of the data**. Four independent layers, each of which alone would catch a dead validator:

| Layer | Mechanism | Fails loudly when | Grounded in |
|---|---|---|---|
| **L-A Negative corpus** | Every deliberately-invalid fixture has a frozen `*.expect.yaml` naming the expected non-zero exit and a frozen `must_contain` substring of the validator's diagnostic | A rule stops firing, or a different rule fires than the one the fixture targets | §31.2 seeded-defect rule |
| **L-B Seeded canary** | One permanently-present, clearly-labelled invalid fixture **per schema id**, named `CANARY-DO-NOT-FIX.yaml`, which every run MUST reject | The validator stops loading a schema entirely; a run that rejects zero canaries is a FAILED run, never a clean one | §53.1 seeded-canary rule; AT-102 |
| **L-C Coverage counters** | The runner records, per run, how many fixtures and how many distinct frozen `must_contain` strings it actually exercised, and fails if either drops below the floor frozen in `coverage-floor.yaml` | The corpus is silently narrowed — a fixture directory stops being discovered, a glob stops matching | §53.1 *"records its per-registry comparison counts … a silently narrowed comparison is itself visible drift"* |
| **L-D Schema mutation** | A harness deletes one constraint at a time from a **copy** of each schema and asserts at least one previously-valid fixture now fails | A schema constraint exists but no fixture exercises it — an uncovered rule that could be deleted without any test noticing | §95.4 negative-test philosophy, executed rather than assumed |

**The discriminating property, stated as a single sentence the executor can check:** an invalid fixture that exits `0` is a suite FAILURE, and a run in which the canary count rejected is less than the canary count present is a suite FAILURE regardless of every other result.

---

## 2. The schema id set this lane tests

Derived from the control-plane inventory of spec §52.6 ("twenty-nine entries"), minus the rows other lanes own. `records/**` and `events/**` are L4 (PARTITION.md). `templates/`, `workflows/`, `runbooks/` and provisioned dashboards are L2/L5. Layer B stores and the conduct-records store are never in an org-readable repository (§52.6) and are out of every lane's schema surface. The Constitution file and the compliance-artifact register are prose, not schema-validated YAML.

### 2.1 `schemas/registry/**` — 15 ids

| # | Schema id | Live artifact (§52.6) | Spec anchor |
|---|---|---|---|
| 1 | `people` | `people.yaml` | §7, §7.1, §7.3 |
| 2 | `roles` | `roles.yaml` | §8 |
| 3 | `topology` | `topology.yaml` | §13.1, §66.2 |
| 4 | `platform` | `platform.yaml` | §60.1 |
| 5 | `os-health` | `os-health.yaml` | §52.2, §52.4, §52.6 |
| 6 | `policies` | `policies.yaml` | §55.1, §55.2, §55.3 |
| 7 | `exceptions` | `exceptions.yaml` | §54.1, §54.2 |
| 8 | `patterns` | `patterns.yaml` | §58.2 |
| 9 | `economics` | `economics.yaml` | §68.1, §57.1 |
| 10 | `platform-roadmap` | `platform-roadmap.yaml` | §59.3 |
| 11 | `tools` | `tools.yaml` | §62.1 |
| 12 | `ai-toolchain` | `ai-toolchain.yaml` | §36.3 |
| 13 | `change-manifest` | `changes/*.yaml` | §25 |
| 14 | `scenario` | `scenarios/*.yaml` | §52.6 |

<!-- NOT ENFORCED (FD-058): These artifacts are not authored by L1 per charter decision. Schema ids 12 (ai-toolchain), 13 (change-manifest), 14 (scenario) are preserved in this table for reference only. Any test assertion derived from their presence in the schema set or fixture corpus is not enforced. -->

### 2.2 `schemas/product/**` — 3 ids

| # | Schema id | Live artifact | Spec anchor |
|---|---|---|---|
| 16 | `product-contract` | `product.yaml` | §15.1, §15.5, §15.7 |
| 17 | `verification-contract` | `verification/contract.yaml` | §31.1, §31.2, §31.3 |
| 18 | `shared-service` | `service.yaml` | §20.1 |

**17 schema ids total.** Task **L1-06-01** proves the set present on disk is exactly this set and STOPS otherwise. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

---

## 3. Directory layout this document creates

```
validators/registry/tests/
  run.sh                              # the single entrypoint (T02)
  lib/
    adapter.sh                        # invokes the validator per validator.cmd (T02)
    assert.sh                         # exit-code and substring assertions (T02)
  validator.cmd                       # ONE line, frozen by T01
  schema-ids.txt                      # 18 lines, frozen by T01
  coverage-floor.yaml                 # frozen counters (T10)
  at-map.yaml                         # AT id -> fixture map (T14)
  ci-contract.md                      # the invocation contract handed to L2 (T15)
  fixtures/
    valid/<schema-id>/<case>.yaml                       # T03, T04, T12
    invalid/<schema-id>/<case>.yaml                     # T05..T08
    invalid/<schema-id>/<case>.expect.yaml              # T05..T08
    canary/<schema-id>/CANARY-DO-NOT-FIX.yaml           # T09
    layerability/                                       # T13
  mutation/
    mutate.sh                         # T11
    mutation-floor.yaml               # T11
  reports/                            # gitignored run output
```

---

## 4. Shared conventions — every task obeys these verbatim

### 4.1 Fixture expectation file format (`*.expect.yaml`)

```yaml
schema_id: product-contract
spec_clause: "15.5 / assignment referencing a person who does not exist or is departed"
at_ids: [AT-008]
expect_exit: nonzero
must_contain: "<frozen substring of validator diagnostic — recorded once by T05..T08>"
frozen_on: "<YYYY-MM-DD the substring was recorded>"
```

`must_contain` is recorded once, from the real validator output, at the moment the fixture is authored, and then committed. It is never regenerated in bulk. Any later change to a frozen `must_contain` is a reviewable one-line diff in the PR — which is the whole point.

### 4.2 Canary fixture header — literal, first three lines of every canary file

```yaml
# CANARY — DELIBERATELY INVALID — DO NOT FIX, DO NOT DELETE.
# Spec basis: Section 53.1 seeded-canary rule; AT-102.
# A suite run that does not reject this file is a FAILED run.
```

### 4.3 Git flow — identical for every task

```bash
cd "$REPO_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/1/06-<taskid>
# ... do the work ...
git add validators/registry/tests
git status --porcelain | grep -v '^A  validators/registry/tests/' && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-<taskid>: <one line>"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-<taskid>
gh pr create --base integration --head lane/1/06-<taskid> \
  --title "L1-06-<taskid>: <one line>" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

The `git status --porcelain | grep -v ...` line is the lane-guard pre-check. If it prints anything, the agent has staged a foreign path and MUST NOT push.

### 4.4 The blocker-issue template — used by every STOP rule

```bash
gh issue create \
  --title "BLOCKER L1-06-<taskid>: <one-line condition>" \
  --label "blocker,lane-1,needs-L0" \
  --body "$(cat <<'EOF'
LANE: L1 (Registries & Contracts)
TASK: L1-06-<taskid>
FILE OWNED: validators/registry/tests/**

STOP CONDITION HIT:
<paste the exact literal condition text from the task's STOP rule>

COMMAND RUN:
<paste the exact command>

OBSERVED OUTPUT:
<paste stdout and stderr verbatim, unedited>

EXPECTED OUTPUT:
<paste the task's SELF-VERIFY "correct output looks like" block verbatim>

WHAT I DID NOT DO:
I did not modify any file outside validators/registry/tests/**.
I did not guess, choose, or design a substitute.

DECISION REQUIRED FROM L0:
<paste the DECISION REQUIRED block id, if the task names one; otherwise "none named">
EOF
)"
```

After filing, the agent stops work on that task and moves to the next task whose dependencies are all satisfied. It does not proceed on the blocked task.

---

## 5. Tasks

### L1-06-01 — Preflight: freeze the lane surface and the validator invocation <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** none (first task in this file)

**Creates:**
- `validators/registry/tests/schema-ids.txt`
- `validators/registry/tests/validator.cmd`

> **NOT ENFORCED (FD-058):** The schema-ids.txt written below includes `ai-toolchain`, `change-manifest`, and `scenario`. These artifacts are not authored by L1 per charter decision (DECISION REQUIRED #1 and #3). The schema-set freeze check (step 2) and the count assertion (criterion 1, prints `17`) derived from including these ids are not enforced. These entries are preserved for reference.

**Commands**

```bash
set -euo pipefail
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t01
mkdir -p validators/registry/tests

# 1. Write the expected schema id set (17 ids, Section 2 of L1-06-tests.md)
cat > validators/registry/tests/schema-ids.txt <<'EOF'
people
roles
topology
platform
os-health
policies
exceptions
patterns
economics
platform-roadmap
tools
ai-toolchain
change-manifest
scenario
product-contract
verification-contract
shared-service
EOF

# 2. Schema-set diff — freeze-file pattern
# D2-L1: jsonschema (Python) is the canonical validator.
# D5-L1: schemas/registry/<id>.json is the canonical layout (single flat file per id).
# Guard: fail immediately if the canonical schema path holds no schemas.
SCHEMA_COUNT=$(find schemas/registry -maxdepth 1 -name '*.json' -not -name '_*.json' 2>/dev/null | wc -l)
if [ "$SCHEMA_COUNT" -eq 0 ]; then
  echo "SCHEMA-SET-EMPTY: no schemas found at schemas/registry/"; exit 1
fi
# Initialize the freeze file if absent (first run); this is not an error.
[ -f schemas/registry/.schema-freeze.sha256 ] || \
  find schemas/registry -maxdepth 1 -name '*.json' -not -name '_*.json' | sort | xargs sha256sum > schemas/registry/.schema-freeze.sha256
# Compare current state against the frozen snapshot.
find schemas/registry -maxdepth 1 -name '*.json' -not -name '_*.json' | sort | xargs sha256sum > /tmp/current.sha256
diff /tmp/current.sha256 schemas/registry/.schema-freeze.sha256 || { echo "SCHEMA SET CHANGED"; exit 1; }
echo "SCHEMA_SET_DIFF_EXIT=$?"

# 3. Discover the validator entrypoint — exact-match discovery, no interpretation
find validators/registry -maxdepth 2 -type f \
  \( -name 'validate' -o -name 'validate.sh' -o -name 'validate.py' -o -name 'validate.js' \) \
  | sort > /tmp/l1_validator_candidates.txt
wc -l < /tmp/l1_validator_candidates.txt
```

Then, and only if `/tmp/l1_validator_candidates.txt` contains **exactly one** line:

```bash
CAND="$(cat /tmp/l1_validator_candidates.txt)"
case "$CAND" in
  *.py) printf 'python %s --schema {SCHEMA_ID} --file {FILE}\n' "$CAND" > validators/registry/tests/validator.cmd ;;
  *.js) echo "STOP: .js validator not permitted (FD-005); found $CAND"; exit 1 ;;
  *)    printf 'bash %s --schema {SCHEMA_ID} --file {FILE}\n'   "$CAND" > validators/registry/tests/validator.cmd ;;
esac
cat validators/registry/tests/validator.cmd
```

Then smoke the contract against one live registry file:

```bash
CMD="$(cat validators/registry/tests/validator.cmd)"
RUN="${CMD//\{SCHEMA_ID\}/people}"
RUN="${RUN//\{FILE\}/registries/people.yaml}"
echo "RUN: $RUN"
eval "$RUN"; echo "VALIDATOR_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `wc -l < validators/registry/tests/schema-ids.txt` | prints `17` |
| 2 | `diff /tmp/current.sha256 schemas/registry/.schema-freeze.sha256` | exit code `0`, no output (schemas/registry/*.json set unchanged since freeze) |
| 3 | `wc -l < validators/registry/tests/validator.cmd` | prints `1` |

> **NOTE:** The freeze file `schemas/registry/.schema-freeze.sha256` is created on first run (D5-L1 canonical layout). Once committed, any change to the file set in `schemas/registry/` causes the diff to be non-empty and T01 stops. Do not add `*.sha256` to any `.gitignore` pattern — the freeze file must be committed and tracked.
| 4 | `grep -c '{SCHEMA_ID}' validators/registry/tests/validator.cmd` and `grep -c '{FILE}'` | each prints `1` |
| 5 | The smoke run above | `VALIDATOR_EXIT=0` |

**SELF-VERIFY**

```bash
test "$(wc -l < validators/registry/tests/schema-ids.txt)" = "17" \
 && { find schemas/registry -maxdepth 1 -name '*.json' -not -name '_*.json' | sort | xargs sha256sum > /tmp/current.sha256; \
      diff -q /tmp/current.sha256 schemas/registry/.schema-freeze.sha256; } \
 && grep -q '{SCHEMA_ID}' validators/registry/tests/validator.cmd \
 && grep -q '{FILE}' validators/registry/tests/validator.cmd \
 && echo "T01 OK"
```

Correct output: the single line `T01 OK`, exit code `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if ANY of:
- the diff in step 2 exits non-zero printing `SCHEMA SET CHANGED` (the schema set in `schemas/registry/` has drifted from the frozen snapshot) — cite **DECISION REQUIRED DR-L1-06-A**;
- `/tmp/l1_validator_candidates.txt` has `0` or more than `1` line — cite **DR-L1-06-B**;
- the smoke run prints `VALIDATOR_EXIT=` anything other than `0` — cite **DR-L1-06-B**;
- `registries/people.yaml` does not exist — cite **DR-L1-06-A**.

> **DECISION REQUIRED — DR-L1-06-A (to L0)**
> The 17 schema ids in §2 are derived from spec §52.6, minus rows PARTITION.md assigns to other lanes. If the schemas actually authored by L1-01..L1-05 differ in count, name or file extension, that is a lane-internal naming decision this test file may not make. L0 must publish the authoritative schema-id list and file-naming convention (a `contracts/**` entry per PARTITION.md rule 2), after which T01 is re-run unchanged against the corrected `schema-ids.txt`. The executor must not rename schemas, invent ids, or drop ids to make the diff pass.

> **DECISION REQUIRED — DR-L1-06-B (to L0)**
> This test strategy assumes a single validator entrypoint invoked as `<runner> <path> --schema <id> --file <path>`, exit `0` on valid, non-zero on invalid, with a diagnostic on stdout or stderr that contains a stable, greppable identifier for the rule that fired. If zero or several entrypoints exist, or if the exit-code convention differs, or if diagnostics carry no stable rule identifier, L0 must publish the validator CLI contract (including the rule-identifier format) as a `contracts/**` entry. Everything from T02 onward reads `validator.cmd` and the frozen `must_contain` strings; without a stable diagnostic, layer L-A degrades to exit-code-only and the corpus can no longer prove which rule fired. The executor must not patch the validator — `validators/registry/` outside `tests/` is authored by other L1 tasks.
>
> **NOTE — Reissued per REG-018 Option A:** validator.cmd must invoke `ci-preflight.sh` (not `gate.py`); must_contain matches the JSON `rule` field in the findings report.

---

### L1-06-02 — Build the harness: runner, adapter, assertions <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-01 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `validators/registry/tests/run.sh`
- `validators/registry/tests/lib/adapter.sh`
- `validators/registry/tests/lib/assert.sh`
- `validators/registry/tests/.gitignore`

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t02
mkdir -p validators/registry/tests/lib validators/registry/tests/reports

printf 'reports/\n' > validators/registry/tests/.gitignore

cat > validators/registry/tests/lib/adapter.sh <<'EOF'
#!/usr/bin/env bash
# Invokes the frozen validator command for one (schema_id, file) pair.
# Prints combined stdout+stderr. Returns the validator's exit code.
l1_validate() {
  local schema_id="$1" file="$2" tmpl run
  tmpl="$(cat "${L1_TESTS_DIR}/validator.cmd")"
  run="${tmpl//\{SCHEMA_ID\}/$schema_id}"
  run="${run//\{FILE\}/$file}"
  eval "$run" 2>&1
  return "${PIPESTATUS[0]:-$?}"
}
EOF

cat > validators/registry/tests/lib/assert.sh <<'EOF'
#!/usr/bin/env bash
L1_FAILS=0
l1_fail() { echo "FAIL: $*"; L1_FAILS=$((L1_FAILS+1)); }
l1_pass() { echo "ok: $*"; }
EOF

cat > validators/registry/tests/run.sh <<'EOF'
#!/usr/bin/env bash
# Lane 1 test suite. Single entrypoint.
# Usage: run.sh --all | --valid | --invalid | --canary | --coverage | --mutation | --layerability
set -euo pipefail
L1_TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export L1_TESTS_DIR
cd "${L1_TESTS_DIR}/../../.." || exit 90
. "${L1_TESTS_DIR}/lib/adapter.sh"
. "${L1_TESTS_DIR}/lib/assert.sh"

MODE="${1:---all}"
N_FIX=0; N_VALID=0; N_INVALID=0; N_CANARY_PRESENT=0; N_CANARY_REJECTED=0
declare -A RULES_SEEN

run_valid() {
  local f id
  while IFS= read -r f; do
    id="$(basename "$(dirname "$f")")"
    out="$(l1_validate "$id" "$f")"; rc=$?
    N_FIX=$((N_FIX+1)); N_VALID=$((N_VALID+1))
    if [ "$rc" -ne 0 ]; then l1_fail "valid fixture rejected: $f (exit $rc) :: $out"
    else l1_pass "valid $f"; fi
  done < <(find "${L1_TESTS_DIR}/fixtures/valid" -type f -name '*.yaml' | sort)
}

run_invalid() {
  local f e id want
  while IFS= read -r f; do
    case "$f" in *.expect.yaml) continue;; esac
    e="${f%.yaml}.expect.yaml"
    id="$(basename "$(dirname "$f")")"
    N_FIX=$((N_FIX+1)); N_INVALID=$((N_INVALID+1))
    if [ ! -f "$e" ]; then l1_fail "invalid fixture has no .expect.yaml: $f"; continue; fi
    want="$(sed -n 's/^must_contain: *"\(.*\)"$/\1/p' "$e")"
    out="$(l1_validate "$id" "$f")"; rc=$?
    if [ "$rc" -eq 0 ]; then
      l1_fail "INVALID FIXTURE ACCEPTED (validator stopped validating): $f"
    elif [ -n "$want" ] && ! printf '%s' "$out" | grep -qF -- "$want"; then
      l1_fail "wrong rule fired for $f :: expected substring [$want] :: got [$out]"
    else
      RULES_SEEN["$want"]=1
      l1_pass "invalid $f"
    fi
  done < <(find "${L1_TESTS_DIR}/fixtures/invalid" -type f -name '*.yaml' | sort)
}

run_canary() {
  local f id
  while IFS= read -r f; do
    id="$(basename "$(dirname "$f")")"
    N_CANARY_PRESENT=$((N_CANARY_PRESENT+1)); N_FIX=$((N_FIX+1))
    out="$(l1_validate "$id" "$f")"; rc=$?
    if [ "$rc" -ne 0 ]; then N_CANARY_REJECTED=$((N_CANARY_REJECTED+1)); l1_pass "canary rejected $f"
    else l1_fail "CANARY ACCEPTED — THIS RUN IS FAILED, NOT CLEAN: $f"; fi
  done < <(find "${L1_TESTS_DIR}/fixtures/canary" -type f -name 'CANARY-DO-NOT-FIX.yaml' | sort)
  if [ "$N_CANARY_PRESENT" -eq 0 ]; then l1_fail "ZERO CANARIES PRESENT — corpus narrowed"; fi
  if [ "$N_CANARY_REJECTED" -ne "$N_CANARY_PRESENT" ]; then
    l1_fail "canary rejection $N_CANARY_REJECTED != canary present $N_CANARY_PRESENT"
  fi
}

case "$MODE" in
  --valid) run_valid;;
  --invalid) run_invalid;;
  --canary) run_canary;;
  --coverage) . "${L1_TESTS_DIR}/lib/coverage.sh" 2>/dev/null || l1_fail "coverage not built (T10)";;
  --mutation) bash "${L1_TESTS_DIR}/mutation/mutate.sh" || l1_fail "mutation harness failed (T11)";;
  --layerability) bash "${L1_TESTS_DIR}/fixtures/layerability/run.sh" || l1_fail "layerability failed (T13)";;
  --all)
    run_valid; run_invalid; run_canary
    [ -f "${L1_TESTS_DIR}/lib/coverage.sh" ] && { . "${L1_TESTS_DIR}/lib/coverage.sh"; }
    [ -f "${L1_TESTS_DIR}/mutation/mutate.sh" ] && { bash "${L1_TESTS_DIR}/mutation/mutate.sh" || l1_fail "mutation"; }
    [ -f "${L1_TESTS_DIR}/fixtures/layerability/run.sh" ] && { bash "${L1_TESTS_DIR}/fixtures/layerability/run.sh" || l1_fail "layerability"; }
    ;;
  *) echo "unknown mode: $MODE"; exit 91;;
esac

R=${#RULES_SEEN[@]}
if [ "$L1_FAILS" -eq 0 ]; then
  echo "LANE1 SUITE: PASS fixtures=$N_FIX valid=$N_VALID invalid=$N_INVALID canaries=$N_CANARY_PRESENT rules=$R"; exit 0
else
  echo "LANE1 SUITE: FAIL fixtures=$N_FIX valid=$N_VALID invalid=$N_INVALID canaries=$N_CANARY_PRESENT rules=$R"; exit 1
fi
EOF

chmod +x validators/registry/tests/run.sh
# canonical path (FD-036): tests/fixtures/invalid/<schema-id>/
mkdir -p validators/registry/tests/fixtures/valid validators/registry/tests/fixtures/invalid validators/registry/tests/fixtures/canary
bash -n validators/registry/tests/run.sh; echo "SYNTAX_EXIT=$?"
bash validators/registry/tests/run.sh --all; echo "RUN_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `bash -n validators/registry/tests/run.sh` | exit `0` |
| 2 | `bash validators/registry/tests/run.sh --all \| tail -1` | matches `^LANE1 SUITE: FAIL ` — **FAIL is correct here**, because zero canaries exist yet and `ZERO CANARIES PRESENT` must fire |
| 3 | `bash validators/registry/tests/run.sh --all 2>&1 \| grep -c 'ZERO CANARIES PRESENT'` | prints `1` |
| 4 | `bash validators/registry/tests/run.sh --nonsense; echo $?` | prints `91` |
| 5 | `cat validators/registry/tests/.gitignore` | exactly `reports/` |

**SELF-VERIFY**

```bash
bash -n validators/registry/tests/run.sh \
 && bash validators/registry/tests/run.sh --all 2>&1 | grep -q 'ZERO CANARIES PRESENT' \
 && bash validators/registry/tests/run.sh --all 2>&1 | tail -1 | grep -q '^LANE1 SUITE: FAIL ' \
 && echo "T02 OK"
```

Correct output: `T02 OK`, exit `0`. An empty corpus **must** report FAIL — this is the harness proving its own loudness before any fixture exists.

**STOP rule** — do not proceed, file the §4.4 blocker, if:
- `bash -n` on `run.sh` exits non-zero after copying the block above verbatim (do not "fix" the script — copy it again exactly, then STOP);
- the empty-corpus run reports `PASS` (a harness that is green with no fixtures is the exact defect this lane exists to prevent) — cite **DR-L1-06-B**.

---

### L1-06-03 — Valid fixture corpus: the 15 registry schemas <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** `validators/registry/tests/fixtures/valid/<id>/minimal.yaml` and `.../typical.yaml` for each of the 15 registry ids in §2.1 (30 files).

Content rules, non-negotiable and mechanical:
- `minimal.yaml` contains **only** the fields the schema marks required, nothing more.
- `typical.yaml` is a verbatim transcription of the spec's own worked example for that file: `people` from §7 (both people entries, including the `work_arrangement` block of §7.3), `roles` from §8, `topology` from §13.1 and §66.2, `platform` from §60.1, `policies` from §55.1, `exceptions` from §54.1 (the full `EXC-2026-041` entry), `economics` from §68.1, `platform-roadmap` from §59.3, `tools` from §62.1, `ai-toolchain` from §36.3. <!-- NOT ENFORCED (FD-058): These artifacts are not authored by L1 per charter decision. The ai-toolchain, change-manifest, and scenario fixtures in this list are not created by T03. -->
- Placeholder identity values only. `people` fixtures use `dev-a`, `dev-b`, `sec-1`, `lead-1` — the spec's own placeholders. No real person, no real customer name (§15.1 uses `customer-ref-017`, "reference, not the customer's legal name").
- Every fixture with an `os-health` shape assigns every SIG identifier present to exactly one priority tier (§52.4: *"A CI check validates that every SIG identifier in the signal table appears in exactly one priority tier"*), and every signal row carries `activation_dependency` and `lookback_window` (§52.2, D77).

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t03
for id in people roles topology platform os-health policies exceptions patterns \
          economics platform-roadmap tools ai-toolchain change-manifest scenario; do
  mkdir -p "validators/registry/tests/fixtures/valid/$id"
done
# author minimal.yaml and typical.yaml per the content rules above, then:
bash validators/registry/tests/run.sh --valid; echo "VALID_EXIT=$?"
find validators/registry/tests/fixtures/valid -name '*.yaml' | wc -l
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/valid -name '*.yaml' \| wc -l` | prints `30` |
| 2 | `for id in $(head -15 validators/registry/tests/schema-ids.txt); do test -f validators/registry/tests/fixtures/valid/$id/minimal.yaml && test -f validators/registry/tests/fixtures/valid/$id/typical.yaml \|\| echo "MISSING $id"; done` | prints nothing |
| 3 | `bash validators/registry/tests/run.sh --valid 2>&1 \| grep -c '^FAIL: '` | prints `0` |
| 4 | `grep -rIl 'TODO\|TBD\|FIXME\|lorem' validators/registry/tests/fixtures/valid \| wc -l` | prints `0` |

**SELF-VERIFY**

```bash
test "$(find validators/registry/tests/fixtures/valid -name '*.yaml' | wc -l)" = "30" \
 && [ "$(bash validators/registry/tests/run.sh --valid 2>&1 | grep -c '^FAIL: ')" = "0" ] \
 && [ "$(grep -rIl 'TODO\|TBD\|FIXME' validators/registry/tests/fixtures/valid | wc -l)" = "0" ] \
 && echo "T03 OK"
```

Correct output: `T03 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if a fixture transcribed verbatim from the spec section named above is **rejected** by the validator. That is a schema/spec disagreement, not a fixture defect. Paste the fixture, the spec line range (`sed -n 'A,Bp'`), and the validator diagnostic into the blocker. **Do not edit the fixture to make it pass** — the fixture is the spec.

---

### L1-06-04 — Valid fixture corpus: the 3 product schemas <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-06-02 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 8 files under `validators/registry/tests/fixtures/valid/product-contract/`, `.../verification-contract/`, `.../shared-service/`.

| File | Content, literally |
|---|---|
| `product-contract/minimal.yaml` | required fields only |
| `product-contract/typical-service.yaml` | the complete §15.1 contract block, verbatim, `conformance_profile: service` |
| `product-contract/profile-client-app.yaml` | §15.7 `client-app`: no `observability.health_endpoint`, with `deployment.staged_rollout` present including `crash_free_sessions.sev2_below_pct` and `sev1_below_pct` (§15.1) |
| `product-contract/profile-static-site.yaml` | §15.7 `static-site` with `recovery: not-applicable` — explicitly permitted |
| `product-contract/three-repositories.yaml` | one product, three entries under `code.repositories` (§16; AT-010) |
| `verification-contract/minimal.yaml` | required fields only, including the mandatory seeded-defect case (§31.2) |
| `verification-contract/typical.yaml` | full contract with `performance` mechanism declared, matching a product at `reliability_criticality: high` (§31.3) |
| `shared-service/typical.yaml` | the §20.1 `service.yaml` example verbatim |

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t04
mkdir -p validators/registry/tests/fixtures/valid/{product-contract,verification-contract,shared-service}
cat > validators/registry/tests/fixtures/valid/product-contract/minimal.yaml <<'EOF'
---
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  id: product-min
  display_name: Minimal Product
  lifecycle: active
  launch_status: pre-launch
  created: "2026-01-01"
classification:
  class: internal
  reliability_criticality: low
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2026-01-01"
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-min
      role: primary
      deploys: true
  default_branch: main
  gsd_version: v3.1.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: not-applicable
  smoke_tests: not-applicable
  performance: not-applicable
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.product-min.internal
  production: https://product-min.example.com
deployment:
  build: docker
  artifact_type: container-image
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: Redeploy previous container tag
  progressive_delivery: none
reversibility_default: fully-reversible
infrastructure:
  runtime: Node.js 22
  database: PostgreSQL
  cache: Redis
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 100
    ceiling: 200
dependencies:
  internal: []
  external: []
  infrastructure: []
security:
  secrets_location: AWS Secrets Manager
  scorecard_minimum: 6
  production_db_access: via bastion host only
data:
  classification: internal
  retention_days: 365
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: false
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors: []
observability:
  health_endpoint: /health
  version_endpoint: /version
  metrics: Prometheus /metrics
  telemetry_exposure: private-authenticated
  alert_channel: "#alerts-product-min"
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  weekend_exception_eligible: false
  primary_responder: dev-a
  backup_responder: dev-b
  critical_incident_response: Page primary responder
commitments: []
business:
  criticality: low
EOF

cat > validators/registry/tests/fixtures/valid/product-contract/typical-service.yaml <<'EOF'
---
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  id: product-1
  display_name: Example Product 1
  lifecycle: active
  launch_status: launched
  created: "2024-01-15"
classification:
  class: commercial
  reliability_criticality: high
  domain: core-platform
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2024-01-15"
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-1-api
      role: primary
      deploys: true
  default_branch: main
  gsd_version: v3.1.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: required
  smoke_tests: required
  performance: optional
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.product-1.internal
  production: https://product-1.company.com
deployment:
  build: docker
  artifact_type: container-image
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: Redeploy previous container tag
  progressive_delivery: none
reversibility_default: fully-reversible
infrastructure:
  runtime: Node.js 22
  database: PostgreSQL
  cache: Redis
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 450
    ceiling: 600
dependencies:
  internal: []
  external:
    - stripe.com/v2
  infrastructure:
    - postgres-primary
ai_runtime_dependency:
  evaluation:
    suite: evals/product-1/suite.yaml
security:
  secrets_location: AWS Secrets Manager
  scorecard_minimum: 7
  production_db_access: via bastion host only
ai_restrictions:
  ai_processing_permitted: true
  restricted_paths: []
  basis: Section 36.4 default
data:
  classification: customer-data
  retention_days: 2555
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: true
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors:
    - stripe.com
observability:
  health_endpoint: /health
  version_endpoint: /version
  metrics: Prometheus /metrics
  telemetry_exposure: private-authenticated
  alert_channel: "#alerts-product-1"
recovery:
  backup_frequency: daily
  point_in_time_recovery:
    enabled: false
    window_minutes: null
  backup_retention_days: 30
  encrypted: true
  storage_location: AWS S3 ap-south-1 (separate account)
  restore_procedure: Run ops/restore.sh with backup ID
  restore_environment: staging-restore.product-1.internal
  integrity_check: SHA-256 checksum on backup file
  restore_tested: "2026-07-01"
  rpo_minutes: 1440
  rto_minutes: 240
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  intake_channel: "#support-product-1"
  triager: dev-a
  weekend_exception_eligible: false
  primary_responder: dev-a
  backup_responder: sec-1
  critical_incident_response: Page primary responder immediately
commitments:
  - sla: "99.9% uptime"
    scope: paying customers
    conflict_check: passed
business:
  criticality: high
  active_customers: 42
  revenue_importance: high
EOF

cat > validators/registry/tests/fixtures/valid/product-contract/profile-client-app.yaml <<'EOF'
---
contract_version: 2
platform_compatibility: supported
conformance_profile: client-app
identity:
  id: product-app
  display_name: Client App Product
  lifecycle: active
  launch_status: launched
  created: "2025-01-01"
classification:
  class: commercial
  reliability_criticality: medium
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2025-01-01"
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-app
      role: primary
      deploys: true
  default_branch: main
  gsd_version: v3.1.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: required
  smoke_tests: required
  performance: not-applicable
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.product-app.internal
  production: https://product-app.example.com
deployment:
  build: docker
  artifact_type: container-image
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: Redeploy previous container tag
  progressive_delivery: staged-rollout
  staged_rollout:
    stages_pct:
      - 10
      - 30
      - 100
    observation_window_hours: 24
    advancer: primary_owner
    crash_free_sessions:
      sev2_below_pct: 99.5
      sev1_below_pct: 99.9
reversibility_default: fully-reversible
infrastructure:
  runtime: React Native
  database: PostgreSQL
  cache: Redis
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 200
    ceiling: 350
dependencies:
  internal: []
  external: []
  infrastructure: []
security:
  secrets_location: AWS Secrets Manager
  scorecard_minimum: 7
  production_db_access: via bastion host only
data:
  classification: customer-data
  retention_days: 365
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: true
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors: []
observability:
  version_endpoint: /version
  metrics: Prometheus /metrics
  telemetry_exposure: private-authenticated
  alert_channel: "#alerts-product-app"
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  intake_channel: "#support-product-app"
  triager: dev-a
  weekend_exception_eligible: false
  primary_responder: dev-a
  backup_responder: dev-b
  critical_incident_response: Page primary responder
commitments: []
business:
  criticality: medium
EOF

cat > validators/registry/tests/fixtures/valid/product-contract/profile-static-site.yaml <<'EOF'
---
contract_version: 2
platform_compatibility: supported
conformance_profile: static-site
identity:
  id: product-site
  display_name: Static Site Product
  lifecycle: active
  launch_status: launched
  created: "2025-01-01"
classification:
  class: commercial
  reliability_criticality: low
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2025-01-01"
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-site
      role: primary
      deploys: true
  default_branch: main
  gsd_version: v3.1.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: not-applicable
  smoke_tests: not-applicable
  performance: not-applicable
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.product-site.internal
  production: https://product-site.example.com
deployment:
  build: static
  artifact_type: static-files
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: Redeploy previous build artifact
  progressive_delivery: none
reversibility_default: fully-reversible
infrastructure:
  runtime: CDN
  database: none
  cache: CDN edge
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 50
    ceiling: 100
dependencies:
  internal: []
  external: []
  infrastructure: []
security:
  secrets_location: GitHub Actions secrets
  scorecard_minimum: 6
  production_db_access: not-applicable
data:
  classification: public
  retention_days: 365
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: false
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors: []
observability:
  health_endpoint: /index.html
  version_endpoint: /version.json
  metrics: CloudFront metrics
  telemetry_exposure: public
  alert_channel: "#alerts-product-site"
recovery: not-applicable
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  intake_channel: "#support-product-site"
  triager: dev-a
  weekend_exception_eligible: false
  primary_responder: dev-a
  backup_responder: dev-b
  critical_incident_response: Page primary responder
commitments: []
business:
  criticality: low
EOF

cat > validators/registry/tests/fixtures/valid/product-contract/three-repositories.yaml <<'EOF'
---
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  id: product-multi-repo
  display_name: Multi-Repository Product
  lifecycle: active
  launch_status: launched
  created: "2025-01-01"
classification:
  class: commercial
  reliability_criticality: medium
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2025-01-01"
    end_date: null
escalation: team_lead
code:
  repositories:
    - name: org/product-multi-api
      role: primary
      deploys: true
    - name: org/product-multi-frontend
      role: frontend
      deploys: true
    - name: org/product-multi-mobile
      role: mobile
      deploys: false
  default_branch: main
  gsd_version: v3.1.0
  accepts_external_contributions: false
verification:
  automated: required
  manual_uat: required
  smoke_tests: required
  performance: not-applicable
  contract_path: verification/contract.yaml
environments:
  local: http://localhost:3000
  staging: https://staging.product-multi-repo.internal
  production: https://product-multi-repo.example.com
deployment:
  build: docker
  artifact_type: container-image
  artifact_registry: ghcr.io/org
  rollback_supported: true
  rollback_method: Redeploy previous container tag
  progressive_delivery: none
reversibility_default: fully-reversible
infrastructure:
  runtime: Node.js 22
  database: PostgreSQL
  cache: Redis
  provider: AWS
  region: ap-south-1
  provider_outage_behaviour: degraded-mode
  monthly_budget_band:
    currency: USD
    expected: 300
    ceiling: 500
dependencies:
  internal: []
  external: []
  infrastructure: []
security:
  secrets_location: AWS Secrets Manager
  scorecard_minimum: 7
  production_db_access: via bastion host only
data:
  classification: internal
  retention_days: 365
  residency: ap-south-1
  isolation: shared-tenant
  deletion_supported: false
  deletion_sla_days: 30
  regulatory_notification_hours: 72
  subprocessors: []
observability:
  health_endpoint: /health
  version_endpoint: /version
  metrics: Prometheus /metrics
  telemetry_exposure: private-authenticated
  alert_channel: "#alerts-product-multi-repo"
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  intake_channel: "#support-product-multi-repo"
  triager: dev-a
  weekend_exception_eligible: false
  primary_responder: dev-a
  backup_responder: dev-b
  critical_incident_response: Page primary responder
commitments: []
business:
  criticality: medium
EOF

cat > validators/registry/tests/fixtures/valid/verification-contract/minimal.yaml <<'EOF'
---
contract_version: 1
mechanisms:
  - automated
coverage_map:
  - requirement: REQ-001
    check: ci/unit-tests
auto_pass:
  scope: documentation-only-changes
required_paths:
  - verification/contract.yaml
  - automated/
  - uat.md
  - smoke/
seeded_defect_cases:
  - id: SD-001
    path: automated/test_example.py
    mechanism: automated
    last_run: "2026-09-01"
    last_result: failed_as_expected
EOF

cat > validators/registry/tests/fixtures/valid/verification-contract/typical.yaml <<'EOF'
---
contract_version: 1
mechanisms:
  - automated
  - manual_uat
  - smoke
  - performance
coverage_map:
  - requirement: REQ-001
    check: ci/unit-tests
  - requirement: REQ-002
    check: ci/integration-tests
  - requirement: REQ-003
    check: uat/manual-test-plan
  - requirement: REQ-004
    check: ci/smoke-tests
  - requirement: REQ-005
    check: ci/performance-suite
auto_pass:
  scope: documentation-only-changes
required_paths:
  - verification/contract.yaml
  - automated/
  - uat.md
  - smoke/
seeded_defect_cases:
  - id: SD-001
    path: automated/test_example.py
    mechanism: automated
    last_run: "2026-09-01"
    last_result: failed_as_expected
  - id: SD-002
    path: automated/test_performance.py
    mechanism: performance
    last_run: "2026-09-01"
    last_result: failed_as_expected
EOF

cat > validators/registry/tests/fixtures/valid/shared-service/typical.yaml <<'EOF'
---
service_version: 1
identity:
  id: auth-service
  repository: org/auth-service
  type: internal-api
assignments:
  - person: dev-a
    type: primary_owner
    start_date: "2025-06-01"
    end_date: null
  - person: dev-b
    type: backup_owner
    start_date: "2025-06-01"
    end_date: null
escalation: team_lead
consumers:
  - product-1
  - product-3
  - product-7
compatibility:
  versioning: semver
  supported_versions:
    - 2.x
    - 3.x
  deprecation_notice_days: 90
  breaking_change_policy: major-version-with-migration-guide
verification:
  automated: required
  consumer_contract_tests: required
  smoke_tests: required
operations:
  primary_responder: dev-a
  backup_responder: dev-b
  incident_severity_inheritance: highest-consumer
EOF

bash validators/registry/tests/run.sh --valid; echo "VALID_EXIT=$?"
git add \
  validators/registry/tests/fixtures/valid/product-contract/minimal.yaml \
  validators/registry/tests/fixtures/valid/product-contract/typical-service.yaml \
  validators/registry/tests/fixtures/valid/product-contract/profile-client-app.yaml \
  validators/registry/tests/fixtures/valid/product-contract/profile-static-site.yaml \
  validators/registry/tests/fixtures/valid/product-contract/three-repositories.yaml \
  validators/registry/tests/fixtures/valid/verification-contract/minimal.yaml \
  validators/registry/tests/fixtures/valid/verification-contract/typical.yaml \
  validators/registry/tests/fixtures/valid/shared-service/typical.yaml
git status --porcelain | grep -v '^A  validators/registry/tests/' && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-04: valid fixture corpus — 3 product schemas (product-contract, verification-contract, shared-service)"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-t04
gh pr create --base integration --head lane/1/06-t04 \
  --title "L1-06-04: valid fixture corpus — 3 product schemas" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/valid/product-contract -name '*.yaml' \| wc -l` | prints `5` |
| 2 | `find validators/registry/tests/fixtures/valid/verification-contract -name '*.yaml' \| wc -l` | prints `2` |
| 3 | `find validators/registry/tests/fixtures/valid/shared-service -name '*.yaml' \| wc -l` | prints `1` |
| 4 | `grep -c 'name:' validators/registry/tests/fixtures/valid/product-contract/three-repositories.yaml` | prints `3` or more, and `grep -A20 'repositories:' ... \| grep -c '  - name:'` prints `3` |
| 5 | `bash validators/registry/tests/run.sh --valid 2>&1 \| grep -c '^FAIL: '` | prints `0` |

**SELF-VERIFY**

```bash
test "$(find validators/registry/tests/fixtures/valid/product-contract -name '*.yaml' | wc -l)" = "5" \
 && [ "$(bash validators/registry/tests/run.sh --valid 2>&1 | grep -c '^FAIL: ')" = "0" ] \
 && grep -q 'conformance_profile: client-app' validators/registry/tests/fixtures/valid/product-contract/profile-client-app.yaml \
 && grep -q 'conformance_profile: static-site' validators/registry/tests/fixtures/valid/product-contract/profile-static-site.yaml \
 && echo "T04 OK"
```

Correct output: `T04 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if `profile-client-app.yaml` is rejected for a missing health endpoint. §15.7 is explicit: *"a `client-app` product is not failed for lacking a health endpoint."* That rejection is a schema defect owned by another L1 task, not a fixture defect. Do not add a health endpoint to the fixture.

---

### L1-06-05 — Negative corpus: people, roles, topology <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-03 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 12 fixture/expect pairs (24 files) under `validators/registry/tests/fixtures/invalid/{people,roles,topology}/`.
<!-- # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/ -->

| Fixture basename | Defect it plants | Spec clause | AT ids |
|---|---|---|---|
| `contractor-null-end-date` | `employment_type: contractor`, `end_date: null` | §7.1 *"`end_date` is mandatory for every non-employee"* | AT-008 |
| `temp-specialist-null-end-date` | `employment_type: temporary_specialist`, `end_date: null` | §7.1 | AT-008 |
| `departed-not-revoked` | `availability: departed`, `access_status: provisioned` | §7.1 *"`departed` implies `revoked`"* | AT-017 |
| `revoked-still-active` | `access_status: revoked`, `availability: active`, employee | §7.1 *"`revoked` implies `departed` or a non-employee past `end_date`"* | AT-017 |
| `suspended-with-departed` | `access_status: suspended`, `availability: departed` | §7.1 *"`suspended` is valid only with `active` or `on_leave`"* | — |
| `reused-person-id` | two entries sharing `id: dev-a` | §7.1 *"Their identifier is never reused"* | AT-017 |
| `timezone-as-utc-offset` | `work_arrangement.timezone: "+05:30"` | §7.3 *"IANA identifier, never a UTC offset"* | AT-047 |
| `fte-out-of-range` | `fte: 1.4` | §7.1 sample: `0 < fte <= 1` | — |
| `rota-member-no-accepted-window` | rota member with `accepted_coverage_window: null` on a product declaring `24x7` | §7.3 *"fails closed where a member has no work arrangement, no accepted window"* | AT-047 |
| `unknown-capability` | a capability not present in the capability model | §9.1 | AT-002 |
| `role-without-performance-mapping` | a `roles.yaml` entry with no performance-framework mapping | §100.1 AT-007 pass condition | AT-007 |
| `topology-escalation-unresolvable` | `escalation: team_lead` with no domain lead and no portfolio Team Lead in `topology.yaml` | §66.2, D3 | AT-016 |

Procedure per fixture — this is the freeze step and must be followed exactly:

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t05
mkdir -p validators/registry/tests/fixtures/invalid/{people,roles,topology}

# 1. Copy the matching valid fixture, then introduce EXACTLY ONE defect from the table.
cp validators/registry/tests/fixtures/valid/people/typical.yaml \
   validators/registry/tests/fixtures/invalid/people/contractor-null-end-date.yaml
# ...edit that one field...

# 2. Record the diagnostic ONCE and freeze it.
export L1_TESTS_DIR="$PWD/validators/registry/tests"
. validators/registry/tests/lib/adapter.sh
OUT="$(l1_validate people validators/registry/tests/fixtures/invalid/people/contractor-null-end-date.yaml)"; RC=$?
echo "EXIT=$RC"; echo "$OUT"
# 3. Choose the single longest line of $OUT that names the rule, and freeze it verbatim:
cat > validators/registry/tests/fixtures/invalid/people/contractor-null-end-date.expect.yaml <<EOF
schema_id: people
spec_clause: "7.1 / end_date is mandatory for every non-employee"
at_ids: [AT-008]
expect_exit: nonzero
must_contain: "<paste the frozen line verbatim>"
frozen_on: "$(date -u +%Y-%m-%d)"
EOF
```

Repeat for all 12. Then:

```bash
bash validators/registry/tests/run.sh --invalid; echo "INVALID_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/invalid/{people,roles,topology} -name '*.yaml' ! -name '*.expect.yaml' \| wc -l` | prints `12` |
| 2 | `for f in $(find validators/registry/tests/fixtures/invalid -name '*.yaml' ! -name '*.expect.yaml'); do test -f "${f%.yaml}.expect.yaml" \|\| echo "NOEXPECT $f"; done` | prints nothing |
| 3 | `grep -rh 'must_contain:' validators/registry/tests/fixtures/invalid \| grep -c '""'` | prints `0` (no empty frozen strings) |
| 4 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c 'INVALID FIXTURE ACCEPTED'` | prints `0` |
| 5 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c '^FAIL: '` | prints `0` |
| 6 | Each fixture differs from its valid parent by exactly one defect: `diff <(valid parent) <(fixture) \| grep -c '^[<>]'` | prints `2` or less per fixture |

**SELF-VERIFY**

```bash
N=$(find validators/registry/tests/fixtures/invalid/people validators/registry/tests/fixtures/invalid/roles validators/registry/tests/fixtures/invalid/topology -name '*.yaml' ! -name '*.expect.yaml' | wc -l)
test "$N" = "12" \
 && [ "$(bash validators/registry/tests/run.sh --invalid 2>&1 | grep -c '^FAIL: ')" = "0" ] \
 && [ "$(grep -rh 'must_contain:' validators/registry/tests/fixtures/invalid | grep -c '""')" = "0" ] \
 && echo "T05 OK"
```

Correct output: `T05 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if any fixture in the table above validates **clean** (exit `0`). That means the rule named in its Spec clause column is not implemented in the schema or validator. Do NOT delete the fixture, do NOT weaken it, do NOT mark it valid. File the blocker naming the fixture, the spec clause and the AT ids, and move to the next task. A missing rule is L1-0x work; suppressing the fixture would hide exactly the gap this corpus exists to expose.

---

### L1-06-06 — Negative corpus: the product contract, one fixture per §15.5 bullet <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** L **Depends on:** L1-06-04 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 17 fixture/expect pairs (34 files) under `validators/registry/tests/fixtures/invalid/product-contract/`.

§15.5 enumerates the conditions on which *"CI validation fails the build"*. One fixture per bullet, plus the §15.7 mis-declaration case:

| # | Fixture basename | §15.5 bullet | AT ids |
|---|---|---|---|
| 1 | `missing-required-field` | malformed contract or missing required field | AT-001 |
| 2 | `restore-tested-stale` | `restore_tested` older than required cadence (90-day floor) | — (invariant 4) |
| 3 | `recovery-without-restore-workflow` | `recovery:` block and no `restore-production.yml` | AT-103 |
| 4 | `assignment-nonexistent-person` | assignment references a person who does not exist | AT-008 |
| 5 | `assignment-departed-person` | assignment references a `departed` person | AT-017 |
| 6 | `assignment-end-date-past` | assignment whose `end_date` has passed | AT-018 |
| 7 | `reviewer-set-team-mismatch` | reviewer set not matching Team membership (declared side only) | AT-002 |
| 8 | `dependency-unknown-service` | declared dependency on a shared service absent from the registry | — (invariant 64) |
| 9 | `contract-version-unsupported` | `contract_version` the platform version does not support | AT-025 |
| 10 | `residency-region-conflict` | `data.residency: eu` vs `infrastructure.region: us-east-1`, no recorded resolution | AT-105 |
| 11 | `commitment-no-conflict-check` | `commitments` entry with neither `passed` nor `waived-with-decision` | — (§21.4) |
| 12 | `ai-dependency-no-eval-suite` | `ai_runtime_dependency` with no suite at `verification/ai-eval/` | **AT-049** |
| 13 | `launched-no-intake-channel` | `launch_status: launched`, no `intake_channel` / no `triager` | AT-048 |
| 14 | `classification-missing-reliability` | `classification` without `reliability_criticality` | — (D4) |
| 15 | `business-missing-criticality` | `business:` without `criticality` | — (D4) |
| 16 | `24x7-no-coverage-window` | `support_model: 24x7`, `coverage_window: null` | **AT-047**, §15.6 |
| 17 | `coverage-window-not-covered-by-rota` | `coverage_window` not fully covered by active rota members' accepted windows | **AT-047** |
| 18 | `profile-service-missing-health-endpoint` | `conformance_profile: service` escaping availability evidence (§15.7 *"a `service` product cannot escape availability evidence by mis-declaring its profile"*) | AT-009 |
| 19 | `detection-expectation-mismatch` | declared `detection_expectation` differing from the value `support_model` derives (§15.1: *"A declared value differing from the derived value fails CI"*) | AT-047 |

(19 rows; the table header count of 17 in the Creates line is superseded by this table — author **19** pairs, 38 files.)

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t06
mkdir -p validators/registry/tests/fixtures/invalid/product-contract
# For each row: cp the valid parent, plant exactly one defect, run l1_validate, freeze must_contain.
# Parent for rows 1-17,19: fixtures/valid/product-contract/typical-service.yaml
# Parent for row 18:       fixtures/valid/product-contract/typical-service.yaml with observability removed
export L1_TESTS_DIR="$PWD/validators/registry/tests"
. validators/registry/tests/lib/adapter.sh
bash validators/registry/tests/run.sh --invalid; echo "INVALID_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/invalid/product-contract -name '*.yaml' ! -name '*.expect.yaml' \| wc -l` | prints `19` |
| 2 | `grep -rl 'AT-047' validators/registry/tests/fixtures/invalid/product-contract \| wc -l` | prints `3` |
| 3 | `grep -rl 'AT-049' validators/registry/tests/fixtures/invalid/product-contract \| wc -l` | prints `1` |
| 4 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c 'INVALID FIXTURE ACCEPTED'` | prints `0` |
| 5 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c 'wrong rule fired'` | prints `0` |
| 6 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` only once T09 has landed; before T09 it prints `1` with `ZERO CANARIES PRESENT` |

**SELF-VERIFY**

```bash
test "$(find validators/registry/tests/fixtures/invalid/product-contract -name '*.yaml' ! -name '*.expect.yaml' | wc -l)" = "19" \
 && [ "$(bash validators/registry/tests/run.sh --invalid 2>&1 | grep -c 'INVALID FIXTURE ACCEPTED')" = "0" ] \
 && [ "$(bash validators/registry/tests/run.sh --invalid 2>&1 | grep -c 'wrong rule fired')" = "0" ] \
 && echo "T06 OK"
```

Correct output: `T06 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if:
- any of rows 1–19 validates clean (rule not implemented — same handling as T05: file, do not delete the fixture).

> **DECISION REQUIRED — DR-L1-06-C (to L0)**
> Rows 7 and 17 assert cross-file referential rules: a reviewer set against GitHub Team membership (§15.5, §53.1) and a product `coverage_window` against rota members' `accepted_coverage_window` in `people.yaml` (§7.3, §47.9). Row 7's *actual* side is GitHub state and belongs to L3's reconciler (`validators/drift/**`, PARTITION.md). L0 must state which half L1's validator owns: the **declared-side consistency check** (the product's named reviewers exist and are active in `people.yaml`) versus the **declared-vs-actual comparison** (L3). This document assumes L1 owns the declared side only and row 7's fixture asserts a declared-side inconsistency. If L0 rules otherwise, row 7 moves to L3 and the fixture is deleted with the decision cited in the commit message.

---

### L1-06-07 — Negative corpus: exceptions and policies <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-03 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 10 fixture/expect pairs (20 files) under `validators/registry/tests/fixtures/invalid/{exceptions,policies}/`.

| Fixture basename | Defect | Spec clause | AT ids |
|---|---|---|---|
| `exception-no-expiry` | `expiry: null` | §54.2 *"CI rejects any exception without one"*; **invariant 77** | AT-036, AT-037 |
| `exception-no-owner` | `owner: null` with a `compensating_control` declared | §54.2 *"names the store its execution lands in and the cadence"* | AT-037 |
| `exception-no-compensating-control-field` | `compensating_control` key absent entirely | §54.2 *"If the honest answer is 'none', that must be written"* | — |
| `exception-trigger-satisfied-wrong-type` | `closure: trigger_satisfied` on `type: temporary_access` | §54.2 *"available only to types that declare a `deactivation_trigger` — `bootstrap` and `founder_standing_delegation_activation`"* | AT-039 |
| `exception-bootstrap-no-deactivation-trigger` | `type: bootstrap`, `deactivation_trigger: null` | §54.5, §95.2 | **AT-039** |
| `exception-authority-lacks-capability` | `type: break_glass`, `authority` a person without `platform-admin` | §54.3 authority mapping | AT-036 |
| `policy-no-review-date` | `review_date` absent | §55.2 *"Every policy has a review date"* | AT-045 |
| `policy-review-date-beyond-12-months` | review date 400 days out | §55.2 *"at most 12 months out"* | AT-045 |
| `policy-starts-at-enforce` | `status: enforce` on first entry, not a critical security control, no `entered_at_enforce_directly` + `justification` | §55.3; **invariant 78** | AT-027 |
| `policy-stage-transition-before-dwell` | transition recorded before `min_dwell` elapsed | §55.3 *"A stage transition recorded before its dwell has elapsed fails CI"* | AT-027 |

Same copy → plant one defect → record → freeze procedure as T05.

**Commands**

```bash
set -euo pipefail
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t07
mkdir -p validators/registry/tests/fixtures/invalid/{exceptions,policies}

export L1_TESTS_DIR="$PWD/validators/registry/tests"
. validators/registry/tests/lib/adapter.sh

# For each fixture: copy the matching valid parent, introduce EXACTLY ONE defect
# per the table, run l1_validate, record the diagnostic, and freeze must_contain.
# Parent for all exception rows: fixtures/valid/exceptions/typical.yaml
# Parent for all policy rows:    fixtures/valid/policies/typical.yaml

for basename in \
    exception-no-expiry \
    exception-no-owner \
    exception-no-compensating-control-field \
    exception-trigger-satisfied-wrong-type \
    exception-bootstrap-no-deactivation-trigger \
    exception-authority-lacks-capability; do
  cp validators/registry/tests/fixtures/valid/exceptions/typical.yaml \
     "validators/registry/tests/fixtures/invalid/exceptions/${basename}.yaml"
  # Edit exactly one defect per the table, then record the diagnostic once and freeze it.
  OUT="$(l1_validate exceptions \
    "validators/registry/tests/fixtures/invalid/exceptions/${basename}.yaml")"; RC=$?
  echo "EXIT=$RC :: $basename"; echo "$OUT"
done

for basename in \
    policy-no-review-date \
    policy-review-date-beyond-12-months \
    policy-starts-at-enforce \
    policy-stage-transition-before-dwell; do
  cp validators/registry/tests/fixtures/valid/policies/typical.yaml \
     "validators/registry/tests/fixtures/invalid/policies/${basename}.yaml"
  OUT="$(l1_validate policies \
    "validators/registry/tests/fixtures/invalid/policies/${basename}.yaml")"; RC=$?
  echo "EXIT=$RC :: $basename"; echo "$OUT"
done

bash validators/registry/tests/run.sh --invalid; echo "INVALID_EXIT=$?"
git add validators/registry/tests/fixtures/invalid/exceptions \
        validators/registry/tests/fixtures/invalid/policies
git status --porcelain | grep -v '^A  validators/registry/tests/' \
  && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-07: negative corpus exceptions and policies (10 fixture/expect pairs)"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-t07
gh pr create --base integration --head lane/1/06-t07 \
  --title "L1-06-07: negative corpus exceptions and policies" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/invalid/exceptions -name '*.yaml' ! -name '*.expect.yaml' \| wc -l` | prints `6` |
| 2 | `find validators/registry/tests/fixtures/invalid/policies -name '*.yaml' ! -name '*.expect.yaml' \| wc -l` | prints `4` |
| 3 | `grep -rl 'AT-039' validators/registry/tests/fixtures/invalid/exceptions \| wc -l` | prints `2` |
| 4 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c '^FAIL: '` | prints `0` |

**SELF-VERIFY**

```bash
test "$(find validators/registry/tests/fixtures/invalid/exceptions -name '*.yaml' ! -name '*.expect.yaml' | wc -l)" = "6" \
 && test "$(find validators/registry/tests/fixtures/invalid/policies -name '*.yaml' ! -name '*.expect.yaml' | wc -l)" = "4" \
 && [ "$(bash validators/registry/tests/run.sh --invalid 2>&1 | grep -c '^FAIL: ')" = "0" ] \
 && echo "T07 OK"
```

Correct output: `T07 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if `exception-no-expiry` validates clean. Invariant 77 is non-negotiable (*"an exception without one is invalid and fails CI"*) and §98.2 Phase 1's completion check requires *"the minimal `exceptions.yaml` schema validator (expiry, owner, deactivation trigger present) is active in control-plane CI and rejects a deliberately malformed exception"*. A clean result here means the Phase 1 completion check is unmet. File the blocker with `severity: phase-1-completion-check` in the title.

---

### L1-06-08 — Negative corpus: os-health and the people-boundary denials <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-03 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 8 fixture/expect pairs (16 files) under `validators/registry/tests/fixtures/invalid/{os-health,people,product-contract}/`.

| Fixture basename | Directory | Defect | Spec clause | AT ids |
|---|---|---|---|---|
| `sig-in-no-priority-tier` | `os-health` | a SIG id present in the signal table and in no P0/P1/P2 tier | §52.4 *"an unassigned or doubly assigned signal fails validation of `os-health.yaml`"* | AT-032 |
| `sig-in-two-priority-tiers` | `os-health` | a SIG id listed in both P1 and P2 | §52.4 | AT-032 |
| `signal-no-activation-dependency` | `os-health` | a signal row without `activation_dependency` | §52.2, **D77** | AT-046 |
| `signal-no-lookback-window` | `os-health` | a signal row without `lookback_window` | §52.2 *"Every `os-health.yaml` row therefore declares a `lookback_window`"* | AT-046 |
| `metric-no-owner-no-response` | `os-health` | a metric with neither owner nor defined action on breach | **invariant 49** *"or it is deleted"* | AT-045 |
| `banned-surveillance-metric` | `os-health` | a metric measuring presence/keystrokes/hours-at-desk | §91.2; **AT-075** *"Banned measurements are absent from the schema and rejected if introduced"* | **AT-075** |
| `assignment-grants-people-intelligence` | `product-contract` | an assignment granting the `people-intelligence` capability | **AT-090** *"an attempt to create an assignment granting `people-intelligence` fails validation"*; D9/D109 | **AT-090**, AT-091 |
| `automated-personnel-action` | `people` | a configured automatic improvement-plan / termination / promotion trigger | **AT-071** *"attempted configuration of one fails validation"*; **invariant 37** | **AT-071** |

**Commands**

```bash
set -euo pipefail
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t08
mkdir -p validators/registry/tests/fixtures/invalid/os-health

export L1_TESTS_DIR="$PWD/validators/registry/tests"
. validators/registry/tests/lib/adapter.sh

# os-health fixtures (6): parent = fixtures/valid/os-health/typical.yaml
for basename in \
    sig-in-no-priority-tier \
    sig-in-two-priority-tiers \
    signal-no-activation-dependency \
    signal-no-lookback-window \
    metric-no-owner-no-response \
    banned-surveillance-metric; do
  cp validators/registry/tests/fixtures/valid/os-health/typical.yaml \
     "validators/registry/tests/fixtures/invalid/os-health/${basename}.yaml"
  # Edit exactly one defect per the table, then record the diagnostic once and freeze it.
  OUT="$(l1_validate os-health \
    "validators/registry/tests/fixtures/invalid/os-health/${basename}.yaml")"; RC=$?
  echo "EXIT=$RC :: $basename"; echo "$OUT"
done

# people-boundary denial — product-contract: parent = typical-service.yaml
cp validators/registry/tests/fixtures/valid/product-contract/typical-service.yaml \
   validators/registry/tests/fixtures/invalid/product-contract/assignment-grants-people-intelligence.yaml
# Edit: add an assignment granting the people-intelligence capability.
OUT="$(l1_validate product-contract \
  validators/registry/tests/fixtures/invalid/product-contract/assignment-grants-people-intelligence.yaml)"; RC=$?
echo "EXIT=$RC :: assignment-grants-people-intelligence"; echo "$OUT"

# people-boundary denial — people: parent = typical.yaml
cp validators/registry/tests/fixtures/valid/people/typical.yaml \
   validators/registry/tests/fixtures/invalid/people/automated-personnel-action.yaml
# Edit: add a configured automatic improvement-plan or termination trigger.
OUT="$(l1_validate people \
  validators/registry/tests/fixtures/invalid/people/automated-personnel-action.yaml)"; RC=$?
echo "EXIT=$RC :: automated-personnel-action"; echo "$OUT"

bash validators/registry/tests/run.sh --invalid; echo "INVALID_EXIT=$?"
git add validators/registry/tests/fixtures/invalid/os-health \
        validators/registry/tests/fixtures/invalid/product-contract/assignment-grants-people-intelligence.yaml \
        validators/registry/tests/fixtures/invalid/product-contract/assignment-grants-people-intelligence.expect.yaml \
        validators/registry/tests/fixtures/invalid/people/automated-personnel-action.yaml \
        validators/registry/tests/fixtures/invalid/people/automated-personnel-action.expect.yaml
git status --porcelain | grep -v '^A  validators/registry/tests/' \
  && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-08: negative corpus os-health and people-boundary denials (8 fixture/expect pairs)"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-t08
gh pr create --base integration --head lane/1/06-t08 \
  --title "L1-06-08: negative corpus os-health and people-boundary denials" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `grep -rl 'AT-075' validators/registry/tests/fixtures/invalid \| wc -l` | prints `1` |
| 2 | `grep -rl 'AT-090' validators/registry/tests/fixtures/invalid \| wc -l` | prints `1` |
| 3 | `grep -rl 'AT-071' validators/registry/tests/fixtures/invalid \| wc -l` | prints `1` |
| 4 | `find validators/registry/tests/fixtures/invalid/os-health -name '*.yaml' ! -name '*.expect.yaml' \| wc -l` | prints `6` |
| 5 | `bash validators/registry/tests/run.sh --invalid 2>&1 \| grep -c 'INVALID FIXTURE ACCEPTED'` | prints `0` |

**SELF-VERIFY**

```bash
for at in AT-071 AT-075 AT-090; do
  [ "$(grep -rl "$at" validators/registry/tests/fixtures/invalid | wc -l)" = "1" ] || { echo "MISSING $at"; exit 1; }
done
[ "$(bash validators/registry/tests/run.sh --invalid 2>&1 | grep -c 'INVALID FIXTURE ACCEPTED')" = "0" ] && echo "T08 OK"
```

Correct output: `T08 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if `assignment-grants-people-intelligence`, `automated-personnel-action` or `banned-surveillance-metric` validates clean. These three are the schema-level enforcement of AT-090, AT-071 and AT-075 respectively, and each is a P0 access or people-trust boundary (§99.6 risk 8). Title the blocker `BLOCKER L1-06-08: people-boundary rule not enforced by schema` and label it `blocker,lane-1,needs-L0,p0`. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

---

### L1-06-09 — Seeded canaries: one per schema id <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-06-05, L1-06-06, L1-06-07, L1-06-08 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** `validators/registry/tests/fixtures/canary/<id>/CANARY-DO-NOT-FIX.yaml` for all 17 ids (17 files).

Each canary is the schema's `minimal.yaml` with **one required field deleted**, prefixed by the literal three-line header of §4.2. No `.expect.yaml` — canaries are exit-code-only by design, because their job is to prove the schema still loads at all.

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t09
while read -r id; do
  mkdir -p "validators/registry/tests/fixtures/canary/$id"
  { printf '# CANARY — DELIBERATELY INVALID — DO NOT FIX, DO NOT DELETE.\n';
    printf '# Spec basis: Section 53.1 seeded-canary rule; AT-102.\n';
    printf '# A suite run that does not reject this file is a FAILED run.\n';
    cat "validators/registry/tests/fixtures/valid/$id/minimal.yaml"; } \
    > "validators/registry/tests/fixtures/canary/$id/CANARY-DO-NOT-FIX.yaml"
  # then delete exactly one required field from the copied body
done < validators/registry/tests/schema-ids.txt
bash validators/registry/tests/run.sh --canary; echo "CANARY_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `find validators/registry/tests/fixtures/canary -name 'CANARY-DO-NOT-FIX.yaml' \| wc -l` | prints `17` |
| 2 | `grep -L 'DO NOT FIX, DO NOT DELETE' $(find validators/registry/tests/fixtures/canary -name 'CANARY-DO-NOT-FIX.yaml') \| wc -l` | prints `0` |
| 3 | `bash validators/registry/tests/run.sh --canary 2>&1 \| grep -c 'CANARY ACCEPTED'` | prints `0` |
| 4 | `bash validators/registry/tests/run.sh --canary 2>&1 \| tail -1` | starts `LANE1 SUITE: PASS ` and contains `canaries=17` |
| 5 | Negative meta-check: `mv validators/registry/tests/fixtures/canary /tmp/cx && bash validators/registry/tests/run.sh --canary 2>&1 \| grep -c 'ZERO CANARIES PRESENT'; mv /tmp/cx validators/registry/tests/fixtures/canary` | prints `1` |
| 6 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` |

**SELF-VERIFY**

```bash
bash validators/registry/tests/run.sh --canary 2>&1 | tail -1 | grep -q 'canaries=17' \
 && [ "$(bash validators/registry/tests/run.sh --canary 2>&1 | grep -c 'CANARY ACCEPTED')" = "0" ] \
 && bash validators/registry/tests/run.sh --all >/dev/null 2>&1 \
 && echo "T09 OK"
```

Correct output: `T09 OK`, exit `0`. This is the first task at which `run.sh --all` is expected to exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if any canary is accepted (exit `0`). Per §53.1 and AT-102, an instrument that reports zero findings including the canary is failed, not clean. Title the blocker `BLOCKER L1-06-09: canary accepted for schema <id> — validator not loading schema`. Never delete or repair a canary to clear the failure. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

---

### L1-06-10 — Coverage counters and the frozen floor <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-09 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `validators/registry/tests/lib/coverage.sh`
- `validators/registry/tests/coverage-floor.yaml`

`coverage.sh` recomputes, from the filesystem, four counts and compares each against `coverage-floor.yaml`, failing if any is **below** the floor. This is §53.1's per-registry comparison count applied to the corpus: *"a silently narrowed comparison is itself visible drift."*

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t10

cat > validators/registry/tests/lib/coverage.sh <<'EOF'
#!/usr/bin/env bash
# Corpus-narrowing detector. Sourced by run.sh.
_c_valid=$(find "${L1_TESTS_DIR}/fixtures/valid"   -name '*.yaml' | wc -l | tr -d ' ')
_c_inval=$(find "${L1_TESTS_DIR}/fixtures/invalid" -name '*.yaml' ! -name '*.expect.yaml' | wc -l | tr -d ' ')
_c_canary=$(find "${L1_TESTS_DIR}/fixtures/canary" -name 'CANARY-DO-NOT-FIX.yaml' | wc -l | tr -d ' ')
_c_rules=$(grep -rh '^must_contain:' "${L1_TESTS_DIR}/fixtures/invalid" | sort -u | wc -l | tr -d ' ')
_f() { sed -n "s/^$1: *\([0-9][0-9]*\).*/\1/p" "${L1_TESTS_DIR}/coverage-floor.yaml"; }
for k in valid invalid canary rules; do
  case $k in valid) a=$_c_valid;; invalid) a=$_c_inval;; canary) a=$_c_canary;; rules) a=$_c_rules;; esac
  b=$(_f "min_$k")
  if [ -z "$b" ]; then l1_fail "coverage-floor.yaml missing min_$k"; continue; fi
  if [ "$a" -lt "$b" ]; then l1_fail "COVERAGE NARROWED: $k=$a below frozen floor $b"; else l1_pass "coverage $k=$a >= $b"; fi
done
EOF

cat > validators/registry/tests/coverage-floor.yaml <<EOF
# Frozen corpus floor. Lowering any number here is a reviewable diff and
# requires a recorded decision. Spec basis: Section 53.1 comparison counts.
min_valid:   $(find validators/registry/tests/fixtures/valid -name '*.yaml' | wc -l | tr -d ' ')
min_invalid: $(find validators/registry/tests/fixtures/invalid -name '*.yaml' ! -name '*.expect.yaml' | wc -l | tr -d ' ')
min_canary:  18
min_rules:   $(grep -rh '^must_contain:' validators/registry/tests/fixtures/invalid | sort -u | wc -l | tr -d ' ')
EOF

bash validators/registry/tests/run.sh --coverage; echo "COV_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `grep -c '^min_' validators/registry/tests/coverage-floor.yaml` | prints `4` |
| 2 | `grep '^min_canary:' validators/registry/tests/coverage-floor.yaml` | prints `min_canary:  18` |
| 3 | `grep '^min_valid:' validators/registry/tests/coverage-floor.yaml` | the number equals `38` (30 from T03 + 8 from T04) |
| 4 | `grep '^min_invalid:' validators/registry/tests/coverage-floor.yaml` | the number equals `50` (12 T05 + 19 T06 + 10 T07 + 9 T08) |
| 5 | `bash validators/registry/tests/run.sh --coverage; echo $?` | prints `0` |
| 6 | Narrowing meta-check: `mv validators/registry/tests/fixtures/invalid/policies /tmp/px && bash validators/registry/tests/run.sh --coverage 2>&1 \| grep -c 'COVERAGE NARROWED'; mv /tmp/px validators/registry/tests/fixtures/invalid/policies` | prints `1` or more |

**SELF-VERIFY**

```bash
bash validators/registry/tests/run.sh --coverage >/dev/null 2>&1 \
 && [ "$(grep -c '^min_' validators/registry/tests/coverage-floor.yaml)" = "4" ] \
 && mv validators/registry/tests/fixtures/invalid/policies /tmp/px \
 && bash validators/registry/tests/run.sh --coverage 2>&1 | grep -q 'COVERAGE NARROWED' \
 && mv /tmp/px validators/registry/tests/fixtures/invalid/policies \
 && echo "T10 OK"
```

Correct output: `T10 OK`, exit `0`. If the meta-check fails, restore the directory before doing anything else: `mv /tmp/px validators/registry/tests/fixtures/invalid/policies`.

**STOP rule** — do not proceed, file the §4.4 blocker, if the narrowing meta-check (criterion 6) does not fire. A floor that does not detect a removed directory is not a floor. Do not adjust the numbers downward to make the suite green — lowering a floor is a recorded L0 decision, never an executor action.

---

### L1-06-11 — Schema-mutation meta-test <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** L **Depends on:** L1-06-10 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `validators/registry/tests/mutation/mutate.sh`
- `validators/registry/tests/mutation/mutation-floor.yaml`

For each schema, the harness copies the schema to a temp directory, removes one entry from its `required` array, points the validator at the mutated copy, and asserts that **at least one previously-valid fixture now fails**. A mutation no fixture detects is an uncovered constraint. This executes §95.4's *"including the negative tests"* against the schema surface rather than assuming coverage.

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t11
mkdir -p validators/registry/tests/mutation

cat > validators/registry/tests/mutation/mutate.sh <<'EOF'
#!/usr/bin/env bash
# Deletes one `required` entry at a time from a COPY of each schema and asserts
# at least one valid fixture then fails. Never writes to schemas/ .
set -u
D="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; export L1_TESTS_DIR="$D"
ROOT="$(cd "$D/../../.." && pwd)"; cd "$ROOT" || exit 90
. "$D/lib/adapter.sh"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
TOTAL=0; KILLED=0; SURVIVORS=""
while read -r id; do
  for src in schemas/registry/$id.schema.json schemas/product/$id.schema.json; do
    [ -f "$src" ] || continue
    n=$(python -c "import json,sys;d=json.load(open('$src'));print(len(d.get('required',[])))")
    i=0
    while [ "$i" -lt "$n" ]; do
      cp -r schemas "$WORK/schemas.$id.$i"
      m="$WORK/schemas.$id.$i/${src#schemas/}"
      python - "$m" "$i" <<'PY'
import json,sys
p,i=sys.argv[1],int(sys.argv[2]); d=json.load(open(p)); r=d.get('required',[]); r.pop(i)
d['required']=r; json.dump(d,open(p,'w'),indent=2)
PY
      TOTAL=$((TOTAL+1)); detected=0
      for f in "$D"/fixtures/valid/"$id"/*.yaml; do
        case "$f" in *.expect.yaml|*'*'*) continue;; esac
        L1_SCHEMA_ROOT="$WORK/schemas.$id.$i" l1_validate "$id" "$f" >/dev/null 2>&1 || { detected=1; break; }
      done
      if [ "$detected" -eq 1 ]; then KILLED=$((KILLED+1)); else SURVIVORS="$SURVIVORS $id#$i"; fi
      i=$((i+1))
    done
  done
done < "$D/schema-ids.txt"
FLOOR=$(sed -n 's/^min_kill_pct: *\([0-9][0-9]*\).*/\1/p' "$D/mutation/mutation-floor.yaml")
PCT=0; [ "$TOTAL" -gt 0 ] && PCT=$(( KILLED * 100 / TOTAL ))
echo "MUTATION: total=$TOTAL killed=$KILLED pct=$PCT floor=$FLOOR"
[ -n "$SURVIVORS" ] && echo "MUTATION SURVIVORS:$SURVIVORS"
[ "$PCT" -ge "${FLOOR:-100}" ] || { echo "MUTATION FLOOR BREACHED"; exit 1; }
exit 0
EOF
chmod +x validators/registry/tests/mutation/mutate.sh

printf '# Frozen mutation floor. Raising it is free; lowering it is a recorded decision.\nmin_kill_pct: 100\n' \
  > validators/registry/tests/mutation/mutation-floor.yaml

bash validators/registry/tests/mutation/mutate.sh; echo "MUT_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `bash validators/registry/tests/mutation/mutate.sh 2>&1 \| grep -c '^MUTATION: total='` | prints `1` |
| 2 | `bash validators/registry/tests/mutation/mutate.sh 2>&1 \| grep '^MUTATION: ' \| grep -o 'total=[0-9]*'` | `total=` a number greater than `0` |
| 3 | `bash validators/registry/tests/mutation/mutate.sh 2>&1 \| grep -c 'MUTATION FLOOR BREACHED'` | prints `0` |
| 4 | `git status --porcelain schemas/ \| wc -l` after the run | prints `0` — the harness must never mutate the real schemas |
| 5 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` |

**SELF-VERIFY**

```bash
bash validators/registry/tests/mutation/mutate.sh > /tmp/mut.txt 2>&1; echo "exit=$?"
grep '^MUTATION: ' /tmp/mut.txt
[ "$(git status --porcelain schemas/ | wc -l)" = "0" ] && echo "SCHEMAS UNTOUCHED"
```

Correct output: a line `MUTATION: total=<n>` with `pct=100 floor=100`, `exit=0`, and `SCHEMAS UNTOUCHED`.

**Paired negative — revert mutation re-accepts valid fixture:**

```bash
# Take the first schema ID, pop one required field into a temp copy, confirm a
# valid fixture is rejected by the mutated schema, then validate the same fixture
# against the unmodified schemas/ tree and confirm it is accepted.
# This proves it is the mutation — not a pre-existing defect — causing rejection.
(
  set -u
  D="validators/registry/tests"
  . "$D/lib/adapter.sh"
  SVID="$(head -1 "$D/schema-ids.txt")"
  SVSRC="$(ls schemas/registry/$SVID.schema.json schemas/product/$SVID.schema.json 2>/dev/null | head -1)"
  SVF="$(ls "$D/fixtures/valid/$SVID/"*.yaml 2>/dev/null | grep -v '\.expect\.yaml' | head -1)"
  SVWORK="$(mktemp -d)"; trap 'rm -rf "$SVWORK"' EXIT
  cp -r schemas "$SVWORK/schemas.sv"
  python - "$SVWORK/schemas.sv/${SVSRC#schemas/}" 0 <<'PY'
import json,sys; p,i=sys.argv[1],int(sys.argv[2])
d=json.load(open(p)); r=d.get('required',[]); r.pop(i)
d['required']=r; json.dump(d,open(p,'w'),indent=2)
PY
  L1_SCHEMA_ROOT="$SVWORK/schemas.sv" l1_validate "$SVID" "$SVF" >/dev/null 2>&1 \
    && { echo "SV_NEG_FAIL: mutated schema accepted $SVF — mutation not detected"; exit 1; } \
    || echo "SV_NEG_STEP1 OK: mutated schema correctly rejected valid fixture"
  L1_SCHEMA_ROOT="schemas" l1_validate "$SVID" "$SVF" >/dev/null 2>&1 \
    && echo "SV_NEG_STEP2 OK: original schema accepted fixture after revert" \
    || { echo "SV_NEG_FAIL: validator rejected valid fixture with unmodified schema"; exit 1; }
) && echo "SV_REVERT_NEG OK" || echo "SV_REVERT_NEG FAIL"
```

Expected output: `SV_NEG_STEP1 OK: mutated schema correctly rejected valid fixture`, `SV_NEG_STEP2 OK: original schema accepted fixture after revert`, `SV_REVERT_NEG OK`.

**STOP rule** — do not proceed, file the §4.4 blocker, if:
- `MUTATION SURVIVORS:` is non-empty — each survivor names a schema constraint no fixture exercises. List every survivor in the blocker; the fix is a new negative fixture, which is a new task L0 assigns, not an edit to the floor;
- `git status --porcelain schemas/` is non-empty after the run — the harness wrote to a real schema. Immediately run `git checkout -- schemas/` and file the blocker before any commit;
- `python` is not on PATH — cite **DR-L1-06-B** (the mutation harness needs a JSON editor and the lane's language runtime is not this document's to choose).

---

### L1-06-12 — Multi-version corpus (AT-025) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-04 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** 4 files under `validators/registry/tests/fixtures/valid/product-contract/` and `.../invalid/product-contract/`.

§60.2 requires *"Validator supports BOTH v1 and v2"* and *"No simultaneous fleet migration is ever required"*. AT-025's pass condition: *"Versioned contracts. Both versions supported simultaneously."*

| File | Content |
|---|---|
| `valid/product-contract/v1-supported.yaml` | `contract_version: 1`, valid under the v1 schema |
| `valid/product-contract/v2-supported.yaml` | `contract_version: 2`, valid under the v2 schema (the §15.1 shape) |
| `valid/product-contract/v1-transitional.yaml` | `contract_version: 1` with `platform_compatibility: transitional` plus the full §60.3 `platform_migration` block (`target_contract_version`, `owner`, `deadline`, `reason`) |
| `invalid/product-contract/transitional-no-owner-no-deadline.yaml` + `.expect.yaml` | `platform_compatibility: transitional` with `platform_migration.owner: null` and no `deadline` — §60.3 *"Requires a named migration owner, a target version and a deadline"*; feeds SIG-10 |

**Commands**

```bash
set -euo pipefail
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t12

export L1_TESTS_DIR="$PWD/validators/registry/tests"
. validators/registry/tests/lib/adapter.sh

# Author the three valid versioned fixtures (§60.2, AT-025):
#   v1-supported.yaml     — contract_version: 1, valid under the v1 schema
#   v2-supported.yaml     — contract_version: 2, valid under the v2 schema (§15.1 shape)
#   v1-transitional.yaml  — contract_version: 1 with full §60.3 platform_migration block
# After authoring each file, verify both versions validate in the same run — that is AT-025:
bash validators/registry/tests/run.sh --valid; echo "VALID_EXIT=$?"

# Author the invalid fixture — transitional with null owner and no deadline (§60.3):
cp validators/registry/tests/fixtures/valid/product-contract/v1-transitional.yaml \
   validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.yaml
# Edit: set platform_migration.owner: null and remove the deadline field.
OUT="$(l1_validate product-contract \
  validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.yaml)"; RC=$?
echo "EXIT=$RC"; echo "$OUT"
# Freeze must_contain from the diagnostic line that names the rule:
cat > validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.expect.yaml <<EOF
schema_id: product-contract
spec_clause: "60.3 / Requires a named migration owner, a target version and a deadline"
at_ids: [AT-025]
expect_exit: nonzero
must_contain: "<paste the frozen diagnostic line verbatim>"
frozen_on: "$(date -u +%Y-%m-%d)"
EOF

bash validators/registry/tests/run.sh --all; echo "SUITE_EXIT=$?"
git add validators/registry/tests/fixtures/valid/product-contract/v1-supported.yaml \
        validators/registry/tests/fixtures/valid/product-contract/v2-supported.yaml \
        validators/registry/tests/fixtures/valid/product-contract/v1-transitional.yaml \
        validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.yaml \
        validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.expect.yaml
git status --porcelain | grep -v '^A  validators/registry/tests/' \
  && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-12: multi-version corpus v1/v2 simultaneous support (AT-025)"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-t12
gh pr create --base integration --head lane/1/06-t12 \
  --title "L1-06-12: multi-version product-contract corpus (AT-025)" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `grep -l 'contract_version: 1' validators/registry/tests/fixtures/valid/product-contract/*.yaml \| wc -l` | prints `2` |
| 2 | `grep -l 'contract_version: 2' validators/registry/tests/fixtures/valid/product-contract/*.yaml \| wc -l` | prints `2` or more |
| 3 | `bash validators/registry/tests/run.sh --valid 2>&1 \| grep -c '^FAIL: '` | prints `0` — **both** versions validate in the same run, which is AT-025 |
| 4 | `grep 'at_ids' validators/registry/tests/fixtures/invalid/product-contract/transitional-no-owner-no-deadline.expect.yaml` | contains `AT-025` |
| 5 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` |

**SELF-VERIFY**

```bash
[ "$(grep -l 'contract_version: 1' validators/registry/tests/fixtures/valid/product-contract/*.yaml | wc -l)" = "2" ] \
 && [ "$(bash validators/registry/tests/run.sh --valid 2>&1 | grep -c '^FAIL: ')" = "0" ] \
 && echo "T12 OK"
```

Correct output: `T12 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if `schemas/product/product-contract.schema.json` carries only one version and there is no v1 artifact to validate against. AT-025 and invariant 73 both require simultaneous support; a single-version schema is a lane gap owned by an L1-0x task. Do not author a v1 schema — `schemas/product/**` is edited by other L1 tasks and this document creates nothing outside `validators/registry/tests/**`.

---

### L1-06-13 — Governance layerability (AT-034) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-06-03 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:**
- `validators/registry/tests/fixtures/layerability/run.sh`
- `validators/registry/tests/fixtures/layerability/core-only/` — a copy of the valid registry corpus with the five removable governance artifacts absent

AT-034: *"The delivery core (Parts I–VI) runs correctly with the removable governance artifacts removed — `os-health.yaml`, `policies.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml` … The reconciliation engine and the exception registry are core-resident machinery and are never removed."*

The test therefore has two halves, both mechanical:
1. With `os-health`, `policies`, `patterns`, `economics`, `platform-roadmap` fixtures absent, every remaining valid fixture still validates and the suite exits `0`.
2. With `exceptions` **also** absent, the run MUST fail — the exception registry is core-resident and its absence is not layerability.

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t13
mkdir -p validators/registry/tests/fixtures/layerability/core-only

cat > validators/registry/tests/fixtures/layerability/run.sh <<'EOF'
#!/usr/bin/env bash
# AT-034 governance layerability. Operates on a COPY; never touches fixtures/valid.
set -u
D="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; export L1_TESTS_DIR="$D"
ROOT="$(cd "$D/../../.." && pwd)"; cd "$ROOT" || exit 90
. "$D/lib/adapter.sh"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
cp -r "$D/fixtures/valid" "$W/valid"
REMOVABLE="os-health policies patterns economics platform-roadmap"
for r in $REMOVABLE; do rm -rf "$W/valid/$r"; done
rc=0
for f in "$W"/valid/*/*.yaml; do
  id="$(basename "$(dirname "$f")")"
  l1_validate "$id" "$f" >/dev/null 2>&1 || { echo "LAYERABILITY FAIL: core rejected $f"; rc=1; }
done
[ "$rc" -eq 0 ] && echo "LAYERABILITY: core-only PASS (removed:$REMOVABLE)"
# Half 2 — the core-resident negative: exceptions must NOT be removable.
# Remove exceptions from the working corpus FIRST, then re-run the validator.
# The validator must exit non-zero: absence of a core-resident schema/fixture is an error.
rm -rf "$W/valid/exceptions"
rc2=0
for f in "$W"/valid/*/*.yaml; do
  id2="$(basename "$(dirname "$f")")"
  l1_validate "$id2" "$f" >/dev/null 2>&1 || { rc2=1; break; }
done
if [ "$rc2" -eq 1 ]; then
  echo "LAYERABILITY: half-2 PASS — exceptions absence correctly rejected by validator (AT-034)"
else
  echo "LAYERABILITY FAIL: half-2 — validator accepted corpus after exceptions removal"; rc=1
fi
exit "$rc"
EOF
chmod +x validators/registry/tests/fixtures/layerability/run.sh
bash validators/registry/tests/run.sh --layerability; echo "LAYER_EXIT=$?"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `bash validators/registry/tests/fixtures/layerability/run.sh 2>&1 \| grep -c 'LAYERABILITY: core-only PASS'` | prints `1` |
| 2 | `bash validators/registry/tests/fixtures/layerability/run.sh 2>&1 \| grep -c 'LAYERABILITY FAIL'` | prints `0` |
| 3 | `bash validators/registry/tests/fixtures/layerability/run.sh; echo $?` | prints `0` |
| 4 | `git status --porcelain validators/registry/tests/fixtures/valid \| wc -l` after the run | prints `0` — the harness copies, never mutates |
| 5 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` |

**SELF-VERIFY**

```bash
bash validators/registry/tests/fixtures/layerability/run.sh > /tmp/lay.txt 2>&1; echo "exit=$?"
grep 'LAYERABILITY' /tmp/lay.txt
[ "$(git status --porcelain validators/registry/tests/fixtures/valid | wc -l)" = "0" ] && echo "VALID CORPUS UNTOUCHED"
```

Correct output: `LAYERABILITY: core-only PASS (removed:os-health policies patterns economics platform-roadmap)`, `LAYERABILITY: half-2 PASS — exceptions absence correctly rejected by validator (AT-034)`, `exit=0`, `VALID CORPUS UNTOUCHED`.

**Paired negative — exceptions present during re-run means validator accepts:**

```bash
# Run a variant of half 2 with exceptions still present (only the five governance
# artifacts removed). The validator must accept the corpus. This proves it is
# exceptions' *absence* — not a pre-existing defect — that causes the rejection.
(
  set -u
  D="validators/registry/tests"
  . "$D/lib/adapter.sh"
  W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
  cp -r "$D/fixtures/valid" "$W/valid"
  REMOVABLE="os-health policies patterns economics platform-roadmap"
  for r in $REMOVABLE; do rm -rf "$W/valid/$r"; done
  # exceptions dir intentionally left present
  rc_neg=0
  for f in "$W"/valid/*/*.yaml; do
    id2="$(basename "$(dirname "$f")")"
    l1_validate "$id2" "$f" >/dev/null 2>&1 || { rc_neg=1; break; }
  done
  [ "$rc_neg" -eq 0 ] \
    && echo "SV_LAY_NEG OK: exceptions present — validator accepted corpus (as expected)" \
    || echo "SV_LAY_NEG FAIL: exceptions present but validator rejected corpus"
) && echo "SV_LAY_REVERT OK" || echo "SV_LAY_REVERT FAIL"
```

Expected output: `SV_LAY_NEG OK: exceptions present — validator accepted corpus (as expected)`, `SV_LAY_REVERT OK`.

**STOP rule** — do not proceed, file the §4.4 blocker, if a non-governance fixture is rejected once the five governance artifacts are removed. That means a core schema has a hard reference into a removable governance file, which contradicts AT-034 and is a schema defect owned by an L1-0x task. Name the rejecting fixture and the diagnostic in the blocker.

---

### L1-06-14 — Acceptance-test traceability map <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** L1-06-06, L1-06-07, L1-06-08, L1-06-09, L1-06-12, L1-06-13 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** `validators/registry/tests/at-map.yaml`

One entry per AT id claimed in §6 below, naming the fixtures that exercise it and whether Lane 1 satisfies it in full or in part. The runner does not need to parse it; the acceptance criteria below check it mechanically.

**Commands**

```bash
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t14
# Write validators/registry/tests/at-map.yaml with one block per AT id listed in §6 of this file.
# Each block must have: at, scope (full|partial), pass_condition (verbatim from spec §100), fixtures list.
# The file must contain exactly 24 blocks — one per AT id claimed in §6.
git add validators/registry/tests/at-map.yaml
# Then verify every listed fixture path exists and every claimed AT appears in some .expect.yaml:
grep -c '^  - at: ' validators/registry/tests/at-map.yaml
for p in $(sed -n 's|^      - \(validators/.*\)$|\1|p' validators/registry/tests/at-map.yaml); do
  test -f "$p" || echo "MISSING FIXTURE $p"
done
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `grep -c '^  - at: ' validators/registry/tests/at-map.yaml` | prints `24` (the count of AT ids in §6) |
| 2 | `for p in $(sed -n 's\|^      - \(validators/.*\)$\|\1\|p' validators/registry/tests/at-map.yaml); do test -f "$p" \|\| echo "MISSING $p"; done` | prints nothing |
| 3 | `grep -o 'AT-[0-9]\{3\}' validators/registry/tests/at-map.yaml \| sort -u \| wc -l` | prints `24` |
| 4 | Every `scope:` value is `full` or `partial`: `grep '^    scope: ' validators/registry/tests/at-map.yaml \| grep -vc 'full\|partial'` | prints `0` |
| 5 | Every AT with `scope: full` has at least one fixture path listed | `python -c` check below exits `0` |

```bash
python - <<'PY'
import re,sys
t=open('validators/registry/tests/at-map.yaml').read()
blocks=re.split(r'^  - at: ', t, flags=re.M)[1:]
bad=[b.split()[0] for b in blocks if 'scope: full' in b and 'validators/' not in b]
print("EMPTY_FULL:", bad); sys.exit(1 if bad else 0)
PY
```

**SELF-VERIFY**

```bash
[ "$(grep -c '^  - at: ' validators/registry/tests/at-map.yaml)" = "24" ] \
 && [ "$(grep -o 'AT-[0-9]\{3\}' validators/registry/tests/at-map.yaml | sort -u | wc -l)" = "24" ] \
 && echo "T14 OK"
```

Correct output: `T14 OK`, exit `0`.

**STOP rule** — do not proceed, file the §4.4 blocker, if any AT id in §6 has **no** fixture and cannot be given one from the corpus already built. Do not invent an AT id, do not renumber, do not mark an unfixtured AT as `full`. Section 100 is the authority and this document cites only ids that exist there.

---

### L1-06-15 — Publish the CI invocation contract to L2 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** L1-06-14 <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Creates:** `validators/registry/tests/ci-contract.md`

L1 owns no workflow file. PARTITION.md rule 4: *"A lane consumes another lane's output only through `contracts/**` or a published artifact — never by reaching into its source tree."* This file is that published artifact.

Content, exactly these six sections:

1. **Invocation.** `bash validators/registry/tests/run.sh --all`, run from the repository root, on every push and every pull request touching `schemas/**`, `registries/**` or `validators/**`.
2. **Success contract.** Exit `0` and a final stdout line matching `^LANE1 SUITE: PASS `. Any other exit code, or a final line matching `^LANE1 SUITE: FAIL `, fails the check.
3. **Required-status-check context name.** `lane1-registry-suite` — to be added to branch protection per §98.2 Phase 1 (*"The required-status-check list starts empty per repository and is populated as each check comes into existence … Each phase's completion check names the contexts it adds"*).
4. **Runtime dependencies.** `bash`, `find`, `grep`, `sed`, plus the runtime named on line 1 of `validators/registry/tests/validator.cmd`, plus `python` for the mutation harness.
5. **Non-negotiable.** The check may never be made `continue-on-error`, and its failure may never be downgraded to a warning. A green suite with zero canaries rejected is a failed run (§53.1, AT-102), and the runner already enforces that; a workflow that swallows the exit code defeats it.
6. **Change control.** Changes to this contract are a Contract Change Request to L0 (PARTITION.md rule 2), never a direct edit by L2 or L1.

**Commands**

```bash
set -euo pipefail
cd "$REPO_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/1/06-t15

VALIDATOR_RUNTIME="$(head -1 validators/registry/tests/validator.cmd | awk '{print $1}')"

cat > validators/registry/tests/ci-contract.md <<EOF
# Lane 1 CI Invocation Contract

Published by Lane 1 (Registries & Contracts) for consumption by Lane 2.
PARTITION.md rule 4: a lane consumes another lane's output only through
\`contracts/**\` or a published artifact — this file is that published artifact.

## 1. Invocation

\`bash validators/registry/tests/run.sh --all\`

Run from the repository root on every push and every pull request touching
\`schemas/**\`, \`registries/**\`, or \`validators/**\`.

## 2. Success contract

- Exit code **0** and a final stdout line matching \`^LANE1 SUITE: PASS \` — the check passes.
- Any other exit code, or a final stdout line matching \`^LANE1 SUITE: FAIL \` — the check fails.
- A run that rejects zero canaries is a **FAILED** run even if every other fixture
  passes (§53.1, AT-102). The runner enforces this; no wrapper may override it.

## 3. Required-status-check context name

\`lane1-registry-suite\`

Add to branch protection per §98.2 Phase 1. Until the L2 workflow is active,
the reviewer runs \`bash validators/registry/tests/run.sh --all\` locally and
pastes the final PASS/FAIL line into the PR description before approving.

## 4. Runtime dependencies

- \`bash\`, \`find\`, \`grep\`, \`sed\` (standard POSIX tools)
- \`${VALIDATOR_RUNTIME}\` — runtime named on line 1 of \`validators/registry/tests/validator.cmd\`
- \`python\` — required by the schema-mutation harness (T11)

## 5. Non-negotiable

- This check **may never** be made \`continue-on-error: true\`.
- Its failure **may never** be downgraded to a warning or non-blocking annotation.
- A green suite with zero canaries rejected is a failed run (§53.1, AT-102);
  a workflow that swallows the exit code defeats the instrument.

## 6. Change control

Changes to this contract require a Contract Change Request to L0 (PARTITION.md
rule 2). Lane 2 and Lane 1 may not edit this file unilaterally.
EOF

grep -c 'bash validators/registry/tests/run.sh --all' validators/registry/tests/ci-contract.md
grep -c 'lane1-registry-suite' validators/registry/tests/ci-contract.md
grep -c 'continue-on-error' validators/registry/tests/ci-contract.md
git status --porcelain | grep -c '\.github/' || true
bash validators/registry/tests/run.sh --all; echo "SUITE_EXIT=$?"
git add validators/registry/tests/ci-contract.md
git status --porcelain | grep -v '^A  validators/registry/tests/' \
  && echo "FOREIGN PATH STAGED — ABORT" && exit 1
git commit -m "L1-06-15: publish CI invocation contract for L2 (ci-contract.md)"
git fetch origin && git rebase origin/integration
git push -u origin lane/1/06-t15
gh pr create --base integration --head lane/1/06-t15 \
  --title "L1-06-15: CI invocation contract for L2" \
  --body "Lane 1. Owned paths only: validators/registry/tests/**. Suite: bash validators/registry/tests/run.sh --all"
```

**Acceptance criteria**

| # | Provable by | Unambiguous pass |
|---|---|---|
| 1 | `grep -c 'bash validators/registry/tests/run.sh --all' validators/registry/tests/ci-contract.md` | `1` or more |
| 2 | `grep -c 'lane1-registry-suite' validators/registry/tests/ci-contract.md` | `1` or more |
| 3 | `grep -c 'continue-on-error' validators/registry/tests/ci-contract.md` | `1` or more |
| 4 | `git status --porcelain \| grep -c '\.github/'` | prints `0` — L1 wrote no workflow |
| 5 | `bash validators/registry/tests/run.sh --all; echo $?` | prints `0` |

**SELF-VERIFY**

```bash
grep -q 'lane1-registry-suite' validators/registry/tests/ci-contract.md \
 && [ "$(git status --porcelain | grep -c '\.github/')" = "0" ] \
 && bash validators/registry/tests/run.sh --all >/dev/null 2>&1 \
 && echo "T15 OK — lane suite green, no foreign path touched"
```

Correct output: `T15 OK — lane suite green, no foreign path touched`, exit `0`.

**STOP rule** — do not proceed, and file the §4.4 blocker citing **DR-L1-06-D**, if the executor is tempted to add a workflow file to make the check "live". It must not. `.github/workflows/**` is L2's exclusive path (PARTITION.md) and touching it fails the lane-guard check.

> **DECISION REQUIRED — DR-L1-06-D (to L0)**
> The lane suite is inert until a workflow calls it, and that workflow is L2's. L0 must sequence the handoff: L1 merges first in the train, so `ci-contract.md` exists before L2's workflow task runs, but L1's own PRs are not gated by the suite until L2 lands the check. L0 decides whether L1 PRs before that point are gated manually (the reviewer runs `run.sh --all` and pastes the final line into the PR) or whether the L2 workflow task is pulled forward. This document assumes the manual interim gate and states it in `ci-contract.md`; the decision is L0's.

---

## 6. Acceptance tests from spec Section 100 that Lane 1 satisfies

`full` = Lane 1's fixtures alone prove the pass condition. `partial` = Lane 1 proves the schema/registry half; another lane proves the platform half (reconciliation is L3, workflows are L2, records are L4). Every id below appears verbatim in spec §100.

| AT id | Pass-condition fragment (spec §100) | L1 scope | Proving fixtures / task |
|---|---|---|---|
| **AT-001** | *"Every surface enumerates from the registry … No dashboard, workflow or script contains a product list"* | partial | `valid/product-contract/*` validate with zero edits to `schemas/**` or `validators/**`; T03, T04 |
| **AT-002** | *"People Registry entry, role assignment, capability grant … No workflow, architecture or dashboard change"* | partial | `valid/people/*`, `invalid/people/unknown-capability`; T03, T05 |
| **AT-007** | *"Role profile plus performance-framework mapping added; no architecture change"* | partial | `invalid/roles/role-without-performance-mapping`; T05 |
| **AT-008** | *"Scoped, dated, capability-limited entry … Employment type supported; capacity and expiry handled"* | full (declared side) | `invalid/people/contractor-null-end-date`, `.../temp-specialist-null-end-date`, `invalid/product-contract/assignment-nonexistent-person`; T05, T06 |
| **AT-009** | *"The product conforms to the operating interface for its declared conformance profile (Section 15.7)"* | full | `valid/product-contract/profile-client-app`, `.../profile-static-site`, `invalid/product-contract/profile-service-missing-health-endpoint`; T04, T06 |
| **AT-010** | *"Product and Repository are separate concepts. One contract, one owner set"* | full | `valid/product-contract/three-repositories`; T04 |
| **AT-011** | *"The approved runtime list is configuration"* | partial | `valid/ai-toolchain/typical`; T03 |
| **AT-016** | *"Only `topology.yaml` changes … Escalation resolves through topology"* | full (declared side) | `invalid/topology/topology-escalation-unresolvable`; T05 |
| **AT-017** | *"orphan detection surfaces every unowned responsibility"* (declared side) | partial | `invalid/people/departed-not-revoked`, `.../revoked-still-active`, `.../reused-person-id`; T05 |
| **AT-018** | *"Reconciliation removes it without human action"* (CI half: expired assignment fails validation, §15.5) | partial | `invalid/product-contract/assignment-end-date-past`; T06 |
| **AT-025** | *"Versioned contracts. Both versions supported simultaneously"* | full | `valid/product-contract/v1-supported`, `.../v2-supported`, `.../v1-transitional`, `invalid/product-contract/transitional-no-owner-no-deadline`; T12 |
| **AT-027** | *"it flows from `policies.yaml` and the reusable workflows"* | partial | `invalid/policies/policy-starts-at-enforce`, `.../policy-stage-transition-before-dwell`; T07 |
| **AT-032** | *"detects and reports a failure in its own reconciliation, health job or dashboard freshness"* | partial | `invalid/os-health/sig-in-no-priority-tier`, `.../sig-in-two-priority-tiers`; T08 |
| **AT-034** | *"The delivery core … runs correctly with the removable governance artifacts removed … The reconciliation engine and the exception registry are core-resident machinery and are never removed"* | full | `fixtures/layerability/run.sh`; T13 |
| **AT-036** | *"Reconciliation revokes it with no human action"* (CI half: the exception is well-formed and dated) | partial | `invalid/exceptions/exception-no-expiry`, `.../exception-authority-lacks-capability`; T07 |
| **AT-037** | *"An exception that cannot be auto-revoked becomes Blocking drift on its expiry date"* | partial | `invalid/exceptions/exception-no-expiry`, `.../exception-no-owner`; T07 |
| **AT-039** | *"A bootstrap-mode gate exception carries an expiry and an activation checklist … it cannot lapse silently"* | full (declared side) | `invalid/exceptions/exception-bootstrap-no-deactivation-trigger`, `.../exception-trigger-satisfied-wrong-type`; T07 |
| **AT-045** | *"retires at least one policy, one metric or one automation, or explicitly records why"* | partial | `invalid/policies/policy-no-review-date`, `.../policy-review-date-beyond-12-months`, `invalid/os-health/metric-no-owner-no-response`; T07, T08 |
| **AT-046** | *"has a recorded pre-Phase-1 baseline, or is explicitly marked as unbaselined"* | partial | `invalid/os-health/signal-no-activation-dependency`, `.../signal-no-lookback-window`; T08 |
| **AT-047** | *"a product declaring an extended or 24x7 support model whose declared `coverage_window` is not fully covered by the accepted windows of active rota members … **fails contract validation**"* | full | `invalid/product-contract/24x7-no-coverage-window`, `.../coverage-window-not-covered-by-rota`, `.../detection-expectation-mismatch`, `invalid/people/rota-member-no-accepted-window`, `.../timezone-as-utc-offset`; T05, T06 |
| **AT-049** | *"A product declaring an `ai_runtime_dependency` block without an evaluation suite under `verification/` fails CI"* | full | `invalid/product-contract/ai-dependency-no-eval-suite`; T06 |
| **AT-071** | *"attempted configuration of one fails validation"* | full | `invalid/people/automated-personnel-action`; T08 |
| **AT-075** | *"Banned measurements are absent from the schema and rejected if introduced"* | full | `invalid/os-health/banned-surveillance-metric`; T08 |
| **AT-090** | *"an attempt to create an assignment granting `people-intelligence` fails validation"* | full | `invalid/product-contract/assignment-grants-people-intelligence`; T08 |

**24 AT ids.** T14 freezes this count into `at-map.yaml`.

**Deliberately not claimed by Lane 1**, and why:
- **AT-102** (seeded reconciliation canary) is L3's — it tests the reconciler's run, not the validator's. Lane 1 borrows its *principle* for the canary corpus (§1, layer L-B) and cites it as the design basis, not as an AT this lane satisfies.
- **AT-103**, **AT-105** are exercised in part by fixtures 3 and 10 of T06, but their pass conditions require an executed workflow and a recorded evidence bundle — L2 and L4. Lane 1 claims neither.
- **AT-033**, **AT-081**, **AT-091**, **AT-097**, **AT-098** all require live platform state or a provisioned Grafana instance; no schema fixture can satisfy them.

---

## 7. Invariants this corpus mechanically enforces

Cited from spec §101; each names the fixture that proves it. §101's own rule applies: an invariant classified `mechanical` must name the CI check or AT id that enforces it.

| Invariant # | Text fragment | Fixture |
|---|---|---|
| **4** | *"A `restore_tested` date older than the window fails CI"* | `invalid/product-contract/restore-tested-stale` |
| **37** | *"No automatic formal improvement plan … Automation never makes personnel decisions"* | `invalid/people/automated-personnel-action` |
| **49** | *"Every operating-system metric has an owner and a defined response, or it is deleted"* | `invalid/os-health/metric-no-owner-no-response` |
| **58** | *"Temporary assignments carry a mandatory end date and expire without human action"* | `invalid/product-contract/assignment-end-date-past` |
| **64** | *"Cross-product dependencies are declared and discoverable"* | `invalid/product-contract/dependency-unknown-service` |
| **73** | *"Contract schemas are versioned, and simultaneous fleet migration is never required"* | `valid/product-contract/v1-supported` + `v2-supported` in one run |
| **77** | *"Every exception has an expiry; an exception without one is invalid and fails CI"* | `invalid/exceptions/exception-no-expiry` |
| **78** | *"A new policy may not begin at Enforce unless it is a critical security control"* | `invalid/policies/policy-starts-at-enforce` |

---

## 8. Task graph and sizes

| Task | Size | Depends on | Creates (count) |
|---|---|---|---|
| L1-06-01 | S | — | 2 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-02 | M | T01 | 4 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-03 | M | T02 | 30 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-04 | S | T02 | 8 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-05 | M | T03 | 24 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-06 | L | T04 | 38 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-07 | M | T03 | 20 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-08 | M | T03 | 18 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-09 | S | T05, T06, T07, T08 | 18 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-10 | M | T09 | 2 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-11 | L | T10 | 2 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-12 | M | T04 | 4 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-13 | S | T03 | 2 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-14 | M | T06, T07, T08, T09, T12, T13 | 1 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-06-15 | S | T14 | 1 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**15 tasks. 174 files, all under `validators/registry/tests/**`.**

Serial critical path: T01 → T02 → T03 → T05/T07/T08 → T09 → T10 → T11 → T14 → T15. T04, T06, T12, T13 run off the same T02/T03/T04 shoulder and can be interleaved by a single agent in any order that respects the table.

---

## 9. Standing rules for whoever runs these tasks

1. **Never make a failing negative fixture pass by editing the fixture.** A negative fixture that validates clean is the discovery this corpus exists to make. File the blocker; leave the fixture in place; move on.
2. **Never delete or repair a canary.** §4.2's header says so on the file's first line.
3. **Never lower a floor.** `coverage-floor.yaml` and `mutation-floor.yaml` go up freely and down only by recorded L0 decision.
4. **Never write outside `validators/registry/tests/**`.** The §4.3 `git status --porcelain` pre-check is the guard; if it prints anything, stop.
5. **Never edit `schemas/**` or `registries/**` from these tasks.** They are owned by other L1 tasks. A schema gap is a blocker, not a fix.
6. **Every `must_contain` is recorded from a real run, once, and then frozen.** Never regenerate the whole set in bulk — that would launder exactly the regression the frozen strings exist to catch.
