> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3-07 — Test Strategy and Daily Runbook
### Lane 3 — Reconciler & Provisioning (Subsystems C and D, spec §99.2)

**Lane:** L3 · **Branch prefix:** `lane/3/*` · **Owns exclusively:** `reconciler/**`, `tools/provision/**`, `validators/drift/**` (PARTITION.md, "The five build lanes").
**This file owns:** the Lane 3 test harness, the fixture organisation, every Lane 3 test case, the phase-gated live-organisation procedure, and the Lane 3 daily runbook.

**Why this file is written the way it is.** Spec §99.6 risk 6: *"Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system."* Its stated mitigation is *"Detect-only first; repair classes enabled one at a time; stricter-only rule enforced in code and tested."* Every rule below exists to make that mitigation mechanical rather than remembered.

---

## 1. The four safety rules of Lane 3 testing

These are binding on every task in this file and on every future Lane 3 task.

| # | Rule | Source | Mechanically enforced by |
|---|---|---|---|
| SR-1 | **Dry-run (plan) is the default.** Writes happen only when the apply flag is passed explicitly. A test that does not name the apply flag must produce zero mutating calls. | §99.4 item 6 ("detect and block only"); §98.2 Phase 3 | `TC-L3-01` |
| SR-2 | **Every test runs against the fixture organisation in replay mode.** The reconciler reads a recorded snapshot from disk; the network is deliberately unreachable during the suite. | §53.1 (the comparison set is data); risk 6 | `TC-L3-02`, harness proxy trap |
| SR-3 | **No Lane 3 test touches the live organisation until the phase gate opens.** The gate is Phase 3's completion check (§98.2) plus AT-110 executed for real, authorised by L0 in writing. | §98.2 Phase 3 completion check; AT-110 | `TC-L3-03` (apply-allowlist guard) + `reconciler/test/live/GATE.md` |
| SR-4 | **A green suite is not evidence unless the negative tests ran.** The suite fails if any of the four mandatory negative cases (`TC-L3-05`, `TC-L3-06`, `TC-L3-08`, `TC-L3-09`) is skipped or absent. | §95.4 ("executed for real — including the negative tests"); §53.1 seeded-canary rule | `run-tests.sh` mandatory-case check |

**The two negative tests that matter most**, stated plainly so no executor can mistake them for optional:

1. **Auto-repair must refuse to loosen.** §53.3: *"a repair is permitted only when it moves the system toward the declared state **and** the declared state is at least as restrictive as the actual state… Where actual state is stricter than declared state, reconciliation raises Level 2 for human judgment rather than relaxing the control."* Invariant 81 and AT-033. Cases `TC-L3-05` (raises Level 2, repairs nothing) and `TC-L3-06` (a loosening repair plan aborts non-zero).
2. **A run that finds nothing must fail.** §53.1 seeded-canary rule: *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one."* AT-102, EC-109, SIG-13. Cases `TC-L3-08` (canary present → found) and `TC-L3-09` (canary removed from the comparison set → run exits non-zero and raises SIG-13).

---

## 2. DECISION REQUIRED → L0 (blocks T01)

> **DECISION REQUIRED — DR-L3-07-A: the Lane 3 test-harness interface contract.**
>
> Every task in this file invokes the reconciler and the provisioning CLI. Their invocation strings, flag names and run-record location are a cross-task interface, not a Lane 3 test choice, and PARTITION.md rule 2 makes `contracts/**` L0-owned. L0 must publish `contracts/l3-test-harness.env` containing **exactly these keys**, one `KEY=value` per line, no other content:
>
> | Key | Must contain |
> |---|---|
> | `RECONCILE_CMD` | The command that runs one reconciliation, plan-only by default |
> | `RECONCILE_APPLY_FLAG` | The single flag that enables writes (SR-1) |
> | `RECONCILE_SOURCE_FLAG` | The flag whose value is a recorded-snapshot directory (replay mode, SR-2) |
> | `RECONCILE_OUT_FLAG` | The flag whose value is the run-record output directory |
> | `RUN_RECORD_PATH` | Path of the JSON run record relative to the output directory |
> | `PROVISION_CMD` | The command that runs a provisioning operation (`create-product`, `add-person`, `change-role`, `remove-person` — §12.6) |
> | `APPLY_ALLOWLIST_PATH` | Repo-relative path of the file naming the organisations apply mode may target |
> | `FIXTURE_ORG` | The organisation login used by the fixture snapshot |
> | `LIVE_ORG` | The real organisation login, recorded here **only** so `TC-L3-03` can prove the reconciler refuses it |
> | `HARNESS_JQ` | Path to `jq`, or the literal `none` |
>
> The run record must carry the fields §53.1 already mandates — a findings array, per-registry comparison counts, and the canary result — so the assertions in this file read spec-named data, not invented data.
>
> **Until this file exists, T01 STOPs.** No executor invents a value for any key.

**Commands**

```bash
set -euo pipefail
cat > contracts/l3-test-harness.env << 'EOF'
RECONCILE_CMD=
RECONCILE_APPLY_FLAG=
RECONCILE_SOURCE_FLAG=
RECONCILE_OUT_FLAG=
RUN_RECORD_PATH=
PROVISION_CMD=
APPLY_ALLOWLIST_PATH=
FIXTURE_ORG=
LIVE_ORG=
HARNESS_JQ=
EOF
```

> **DECISION REQUIRED — DR-L3-07-B: authorisation to touch the live organisation.**
>
> SR-3 forbids any live-organisation execution until the gate opens. The gate cannot be judged by the executor. L0 must publish `contracts/l3-live-org-gate.md` stating: (a) Phase 3's completion check has passed (*"contracts validate; registries, contracts and Team membership agree, machine-verified"*, §98.2); (b) the named human who will supervise the AT-110 six-attempt run; (c) the date authorised. **T10 STOPs until that file exists**, and T10 never runs unsupervised.

---

## 3. The fixture organisation

A **fixture organisation** is a recorded, on-disk snapshot of an organisation's GitHub-side state plus the declared registries that describe it. It is the only target the suite ever compares against (SR-2). It lives at `reconciler/test/fixtures/org/` and has three parts:

| Part | Path | Contents |
|---|---|---|
| Declared | `fixtures/org/declared/` | The registry side of every §53.1 comparison row this lane implements: people, assignments, product contracts, branch-protection template, environment template |
| Actual | `fixtures/org/actual/` | Recorded GitHub-side responses, one JSON file per endpoint, keyed by a flattened path |
| Canary | `fixtures/org/canary/` | The permanent seeded drift record of §53.1, and the `no-canary/` variant used by `TC-L3-09` |

The fixture organisation is **lane-local test data**. It is never validated by L1's registry validators (PARTITION rule 4, no cross-lane imports) and it is never pushed to any GitHub organisation.

---

## 4. Test case catalogue

| Case | Name | Proves | Spec / AT / invariant | Task |
|---|---|---|---|---|
| TC-L3-01 | Plan is the default | No apply flag ⇒ zero mutating calls recorded | SR-1; §99.4 item 6 | T03 |
| TC-L3-02 | Replay is hermetic | A suite run makes no network call at all | SR-2 | T03 |
| TC-L3-03 | Apply-allowlist guard | Apply mode against `LIVE_ORG` exits non-zero and writes nothing | SR-3; §99.6 risk 6 | T03 |
| TC-L3-04 | Repair classes are individually gated | A disabled repair class produces a finding, never a repair | §99.6 risk 6 ("repair classes enabled one at a time") | T04 |
| **TC-L3-05** | **Stricter actual is not relaxed** | Actual stricter than declared ⇒ Level 2 finding, zero repairs | §53.3; AT-033; invariant 81 | T04 |
| **TC-L3-06** | **A loosening repair aborts** | A repair plan that would loosen a control exits non-zero before any write | §53.3; invariant 81 | T04 |
| TC-L3-07 | Comparison counts are recorded | Run record carries per-registry comparison counts | §53.1 | T05 |
| **TC-L3-08** | **The canary is found** | Every run reports the seeded canary drift | §53.1; AT-102 | T05 |
| **TC-L3-09** | **A run that finds nothing FAILS** | Canary removed ⇒ non-zero exit, SIG-13 raised, not "clean" | §53.1; AT-102; EC-109; SIG-13 | T05 |
| TC-L3-10 | Expiry revokes without a human | An assignment past `end_date` is revoked by the run | §53.1 row "Assignment `end_date`"; AT-018; AT-008; AT-036 | T06 |
| TC-L3-11 | A failed revoke becomes Blocking | An un-revocable expired grant is Blocking drift on its expiry date | AT-037; §53.2 Level 4 | T06 |
| TC-L3-12 | Orphans are Blocking and undismissable | No Primary Owner / no Cross-Reviewer / no Primary Responder ⇒ Blocking, dismissal refused | §12.1 orphan table; AT-017; invariant 57; SIG-05 | T06 |
| TC-L3-13 | CODEOWNERS is human-only | Generated CODEOWNERS contains no machine identity | §98.2 Phase 1 completion check; §53.1 independent verifier | T07 |
| TC-L3-14 | Machine workflow edit is Blocking | A workflow-file change by a machine identity is Blocking regardless of content | §53.1; §53.2 Level 4 | T07 |
| TC-L3-15 | Records head is anchored | Run records the records-repo head SHA and commit count; a non-descendant head is Blocking Level 5 | §40.1 (D107) | T07 |
| TC-L3-16 | create-product enumerates | A 21st product appears with no hard-coded product list anywhere in the lane's output | AT-001; §19.1 | T08 |
| TC-L3-17 | add-person is complete | Registry entry, team membership, capability grant; reconciliation grants access | AT-002; §12.6 | T08 |
| TC-L3-18 | Templates are safe by default | Provisioning templates are minimum-privilege and fail-closed | invariants 79, 80; §98.5 G2 | T08 |
| TC-L3-19 | Registry edits stage before the fleet | A merged registry change reaches the canary set only, fleet held one cycle | §26.4 | T09 |
| TC-L3-20 | External cause is annotated | A vendor-outage failure is annotated `external-cause`, not raised as raw Red | §53.1 | T09 |
| TC-L3-21 | AT-110 six-attempt boundary | Reconciler credential fails all six writes, then completes a normal run | AT-110; §40.3 | T10 (gated) |

Mandatory negative cases (SR-4): `TC-L3-05`, `TC-L3-06`, `TC-L3-08`, `TC-L3-09`.

---

## 5. Tasks

Size key: **S** ≤ 1 hour · **M** ≤ half a day · **L** ≤ one day. Every command below runs from the root of your `control-plane` clone. Start every task from a clean `integration` (Runbook §6.1).

---

### T01 — Bootstrap the harness · size S · depends: DR-L3-07-A

**Files created (all Lane-3 owned):**
`reconciler/test/harness.env`, `reconciler/test/run-tests.sh`, `reconciler/test/lib/assert.sh`, `reconciler/test/README.md`, `reconciler/test/cases/.keep`, `tools/provision/test/cases/.keep`, `validators/drift/test/cases/.keep`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t01

test -f contracts/l3-test-harness.env || { echo "STOP: DR-L3-07-A unresolved"; exit 1; }
command -v jq >/dev/null || { echo "STOP: jq missing"; exit 1; }

mkdir -p reconciler/test/lib reconciler/test/cases reconciler/test/bin \
         reconciler/test/fixtures/org reconciler/test/live \
         tools/provision/test/cases validators/drift/test/cases
cp contracts/l3-test-harness.env reconciler/test/harness.env
touch reconciler/test/cases/.keep tools/provision/test/cases/.keep validators/drift/test/cases/.keep

cat > reconciler/test/lib/assert.sh <<'EOF'
# Lane 3 assertions. Every function exits 1 on failure with a one-line reason.
fail() { echo "ASSERT-FAIL: $*" >&2; exit 1; }
assert_eq()       { [ "$1" = "$2" ] || fail "expected [$2] got [$1] ($3)"; }
assert_ne()       { [ "$1" != "$2" ] || fail "expected NOT [$2] ($3)"; }
assert_nonzero()  { [ "$1" -ne 0 ] || fail "expected non-zero exit ($2)"; }
assert_zero()     { [ "$1" -eq 0 ] || fail "expected zero exit, got $1 ($2)"; }
assert_file()     { [ -f "$1" ] || fail "missing file $1"; }
assert_empty()    { [ ! -s "$1" ] || fail "expected empty file $1, contents: $(cat "$1")"; }
assert_jq()       { local got; got="$(jq -r "$2" "$1")"; assert_eq "$got" "$3" "$1 $2"; }
EOF

cat > reconciler/test/run-tests.sh <<'EOF'
#!/usr/bin/env bash
# Lane 3 test runner. Usage: bash reconciler/test/run-tests.sh [case-id]
set -u
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 2
export L3_ROOT="$ROOT"
export L3_TEST="$ROOT/reconciler/test"
set -a; . "$L3_TEST/harness.env"; set +a

MANDATORY="TC-L3-05 TC-L3-06 TC-L3-08 TC-L3-09"
DIRS="reconciler/test/cases tools/provision/test/cases validators/drift/test/cases"
FILTER="${1:-}"

# SR-2: the network is unreachable for the whole suite.
export HTTPS_PROXY="http://127.0.0.1:1" HTTP_PROXY="http://127.0.0.1:1" ALL_PROXY="http://127.0.0.1:1"
export PATH="$L3_TEST/bin:$PATH"

pass=0; failn=0; total=0; present=""
for d in $DIRS; do
  [ -d "$d" ] || continue
  for c in $(ls "$d"/TC-L3-*.sh 2>/dev/null | sort); do
    id="$(basename "$c" .sh)"; present="$present $id"
    [ -n "$FILTER" ] && [ "$FILTER" != "$id" ] && continue
    total=$((total+1))
    if out="$(bash "$c" 2>&1)"; then echo "PASS $id"; pass=$((pass+1))
    else echo "FAIL $id"; echo "$out" | sed 's/^/    /'; failn=$((failn+1)); fi
  done
done
# SR-4: a suite missing a mandatory negative case is not a green suite.
if [ -z "$FILTER" ]; then
  for m in $MANDATORY; do
    case " $present " in *" $m "*) ;; *) echo "FAIL $m MISSING-MANDATORY-NEGATIVE-CASE"; failn=$((failn+1)); total=$((total+1));; esac
  done
fi
echo "SUMMARY total=$total pass=$pass fail=$failn"
[ "$failn" -eq 0 ]
EOF
chmod +x reconciler/test/run-tests.sh

cat > reconciler/test/README.md <<'EOF'
# Lane 3 test harness
Run everything:  bash reconciler/test/run-tests.sh
Run one case:    bash reconciler/test/run-tests.sh TC-L3-05
Safety rules SR-1..SR-4 are documented in implementation/lanes/L3-07-tests-and-runbook.md.
The suite never contacts a network and never targets a live organisation.
EOF

git add reconciler/test tools/provision/test validators/drift/test
git commit -m "L3-07-01: Lane 3 test harness skeleton and runner"
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | Harness env copied verbatim from contracts | `diff contracts/l3-test-harness.env reconciler/test/harness.env; echo rc=$?` | `rc=0` |
| 2 | Runner exists and is executable | `test -x reconciler/test/run-tests.sh && echo OK` | `OK` |
| 3 | Runner fails an empty suite on the mandatory-case rule | `bash reconciler/test/run-tests.sh >/dev/null 2>&1; echo rc=$?` | `rc=1` |
| 4 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(reconciler/|tools/provision/|validators/drift/)' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh; echo "rc=$?"
```
Expected, exactly:
```
FAIL TC-L3-05 MISSING-MANDATORY-NEGATIVE-CASE
FAIL TC-L3-06 MISSING-MANDATORY-NEGATIVE-CASE
FAIL TC-L3-08 MISSING-MANDATORY-NEGATIVE-CASE
FAIL TC-L3-09 MISSING-MANDATORY-NEGATIVE-CASE
SUMMARY total=4 pass=0 fail=4
rc=1
```

**STOP rule** — If `contracts/l3-test-harness.env` is absent, or `jq` is absent, or any key listed in DR-L3-07-A is missing from the file: do not proceed, do not invent a value, file a blocker with template B-1 (§7) naming `DR-L3-07-A`.

---

### T02 — Build the fixture organisation · size M · depends: T01

**Files created:** `reconciler/test/fixtures/org/declared/*.yaml`, `reconciler/test/fixtures/org/actual/*.json`, `reconciler/test/fixtures/org/canary/canary.yaml`, `reconciler/test/fixtures/org/canary/no-canary/.keep`, `reconciler/test/fixtures/org/README.md`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t02
set -a; . reconciler/test/harness.env; set +a
mkdir -p reconciler/test/fixtures/org/declared reconciler/test/fixtures/org/actual \
         reconciler/test/fixtures/org/canary/no-canary
touch reconciler/test/fixtures/org/canary/no-canary/.keep

cat > reconciler/test/fixtures/org/declared/people.yaml <<'EOF'
people:
  - github: fx-owner
    availability: active
    capabilities: [code-review, production-approval]
  - github: fx-reviewer
    availability: active
    capabilities: [code-review]
  - github: fx-contractor
    availability: active
    employment_type: contractor
    capabilities: [code-review]
    end_date: "2000-01-01"     # deliberately past: drives TC-L3-10
  - github: fx-departed
    availability: departed
    capabilities: []
EOF

cat > reconciler/test/fixtures/org/declared/product-fx-alpha.yaml <<'EOF'
product: fx-alpha
assignments:
  primary_owner: fx-owner
  cross_reviewer: fx-reviewer
  backup_owner: fx-owner
  primary_responder: fx-owner
branch_protection:
  required_approving_review_count: 2
  require_code_owner_reviews: true
  allow_force_pushes: false
EOF

cat > reconciler/test/fixtures/org/declared/product-fx-orphan.yaml <<'EOF'
product: fx-orphan
assignments:
  primary_owner: fx-departed     # drives TC-L3-12 (Blocking orphan)
  cross_reviewer: null           # drives TC-L3-12 (Blocking orphan)
  backup_owner: fx-owner
  primary_responder: null        # drives TC-L3-12 (Blocking orphan)
branch_protection:
  required_approving_review_count: 2
  require_code_owner_reviews: true
  allow_force_pushes: false
EOF

cat > reconciler/test/fixtures/org/declared/product-fx-strict.yaml <<'EOF'
product: fx-strict
assignments:
  primary_owner: fx-owner
  cross_reviewer: fx-reviewer
  backup_owner: fx-owner
  primary_responder: fx-owner
branch_protection:
  required_approving_review_count: 1   # actual is 2 — stricter. Drives TC-L3-05.
  require_code_owner_reviews: true
  allow_force_pushes: false
EOF

cat > reconciler/test/fixtures/org/actual/teams.json <<'EOF'
{"org":"FIXTURE_ORG_PLACEHOLDER","teams":[
 {"slug":"fx-alpha","members":["fx-owner","fx-reviewer","fx-contractor"]},
 {"slug":"fx-orphan","members":["fx-owner"]},
 {"slug":"fx-strict","members":["fx-owner","fx-reviewer"]}]}
EOF

cat > reconciler/test/fixtures/org/actual/branch-protection.json <<'EOF'
{"fx-alpha":{"required_approving_review_count":2,"require_code_owner_reviews":true,"allow_force_pushes":false},
 "fx-orphan":{"required_approving_review_count":2,"require_code_owner_reviews":true,"allow_force_pushes":false},
 "fx-strict":{"required_approving_review_count":2,"require_code_owner_reviews":true,"allow_force_pushes":false}}
EOF

cat > reconciler/test/fixtures/org/actual/codeowners.json <<'EOF'
{"fx-alpha":["@fx-owner","@fx-reviewer"],
 "fx-orphan":["@fx-owner"],
 "fx-strict":["@fx-owner","@fx-reviewer"]}
EOF

cat > reconciler/test/fixtures/org/canary/canary.yaml <<'EOF'
# The permanent seeded drift of spec §53.1. Every reconciliation run MUST report it.
# A run that does not report this record is a FAILED run (AT-102, EC-109, SIG-13).
canary:
  id: CANARY-001
  label: "seeded-canary — deliberate, permanent, never repair"
  registry: branch_protection
  scope: fx-canary
  declared: {required_approving_review_count: 2}
  actual:   {required_approving_review_count: 2, allow_force_pushes: true}
  expected_class: Blocking
  repairable: false
EOF

sed -i "s/FIXTURE_ORG_PLACEHOLDER/${FIXTURE_ORG}/" reconciler/test/fixtures/org/actual/teams.json

cat > reconciler/test/fixtures/org/README.md <<'EOF'
# The Lane 3 fixture organisation
Lane-local test data. Never pushed to any GitHub organisation, never validated by L1 validators.
declared/  the registry side of the §53.1 comparison rows
actual/    recorded GitHub-side state, one JSON per surface
canary/    the permanent seeded drift (§53.1); no-canary/ is the deliberately-blind variant for TC-L3-09
EOF

git add reconciler/test/fixtures
git commit -m "L3-07-02: fixture organisation with seeded canary"
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | Nine fixture files present | `find reconciler/test/fixtures/org -type f ! -name .keep \| wc -l` | `9` |
| 2 | Fixture org substituted, no placeholder left | `grep -rc PLACEHOLDER reconciler/test/fixtures \| grep -v ':0' \| wc -l` | `0` |
| 3 | Canary declares itself unrepairable | `grep -c 'repairable: false' reconciler/test/fixtures/org/canary/canary.yaml` | `1` |
| 4 | Blind variant exists and is empty of canary records | `ls reconciler/test/fixtures/org/canary/no-canary/ \| grep -v '^.keep$' \| wc -l` | `0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
find reconciler/test/fixtures/org -type f ! -name .keep | wc -l
grep -c 'repairable: false' reconciler/test/fixtures/org/canary/canary.yaml
```
Expected, exactly:
```
9
1
```

**STOP rule** — If `FIXTURE_ORG` is empty or equal to `LIVE_ORG`: stop immediately, do not commit, file blocker template B-1 naming SR-3. A fixture organisation that is the live organisation is the exact failure §99.6 risk 6 describes.

---

### T03 — Dry-run, hermeticity and the apply guard (TC-L3-01/02/03) · size M · depends: T02

**Files created:** `reconciler/test/bin/gh`, `reconciler/test/bin/curl`, `reconciler/test/cases/TC-L3-01.sh`, `TC-L3-02.sh`, `TC-L3-03.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t03

cat > reconciler/test/bin/gh <<'EOF'
#!/usr/bin/env bash
# PATH shim: records every gh invocation; refuses every mutating call.
echo "gh $*" >> "${L3_CALL_LOG:-/dev/null}"
case " $* " in
  *" --method POST "*|*" --method PATCH "*|*" --method PUT "*|*" --method DELETE "*|*" api "*" -X "*)
     echo "MUTATING-CALL: gh $*" >&2; exit 97;;
esac
exit 0
EOF
cat > reconciler/test/bin/curl <<'EOF'
#!/usr/bin/env bash
echo "curl $*" >> "${L3_CALL_LOG:-/dev/null}"
case " $* " in *" -X "*|*" --request "*) echo "MUTATING-CALL: curl $*" >&2; exit 97;; esac
exit 0
EOF
chmod +x reconciler/test/bin/gh reconciler/test/bin/curl

cat > reconciler/test/cases/TC-L3-01.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-01 — SR-1: plan is the default. No apply flag ⇒ zero mutating calls.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >"$out/stdout" 2>"$out/stderr"
assert_file "$out/$RUN_RECORD_PATH"
grep -c 'MUTATING-CALL' "$out/stderr" > "$out/mut" || true
assert_eq "$(grep -c 'MUTATING-CALL' "$out/stderr" || true)" "0" "plan mode must issue no mutating call"
assert_eq "$(jq -r '.mode' "$out/$RUN_RECORD_PATH")" "plan" "run record must declare plan mode"
assert_eq "$(jq -r '.repairs | length' "$out/$RUN_RECORD_PATH")" "0" "plan mode must record zero repairs"
EOF

cat > reconciler/test/cases/TC-L3-02.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-02 — SR-2: replay is hermetic. The suite exports an unreachable proxy;
# a run that still succeeds proves it read the recorded snapshot, not the network.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
rc=$?; assert_zero "$rc" "replay run must succeed with the network unreachable"
assert_eq "$(jq -r '.source' "$out/$RUN_RECORD_PATH")" "replay" "run record must declare replay source"
EOF

cat > reconciler/test/cases/TC-L3-03.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-03 — SR-3: apply mode refuses any organisation absent from the allowlist,
# and refuses LIVE_ORG outright before the phase gate (§99.6 risk 6).
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
set +e
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$LIVE_ORG" \
  $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >"$out/stdout" 2>"$out/stderr"
rc=$?
set -e
assert_nonzero "$rc" "apply against LIVE_ORG must be refused"
assert_empty "$L3_CALL_LOG"
grep -qi 'allowlist' "$out/stderr" || fail "refusal must name the allowlist ($APPLY_ALLOWLIST_PATH)"
EOF

git add reconciler/test/bin reconciler/test/cases
git commit -m "L3-07-03: dry-run default, hermetic replay and apply-allowlist guard"
bash reconciler/test/run-tests.sh TC-L3-01
bash reconciler/test/run-tests.sh TC-L3-02
bash reconciler/test/run-tests.sh TC-L3-03
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-01 passes | `bash reconciler/test/run-tests.sh TC-L3-01` | `PASS TC-L3-01` then `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-02 passes | `bash reconciler/test/run-tests.sh TC-L3-02` | `PASS TC-L3-02` then `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-03 passes | `bash reconciler/test/run-tests.sh TC-L3-03` | `PASS TC-L3-03` then `SUMMARY total=1 pass=1 fail=0` |
| 4 | Shims are executable | `test -x reconciler/test/bin/gh && test -x reconciler/test/bin/curl && echo OK` | `OK` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
for c in TC-L3-01 TC-L3-02 TC-L3-03; do bash reconciler/test/run-tests.sh $c | head -1; done
```
Expected, exactly:
```
PASS TC-L3-01
PASS TC-L3-02
PASS TC-L3-03
```

**STOP rule** — If `TC-L3-03` fails because apply mode **succeeded** against `LIVE_ORG`: stop all Lane 3 work immediately, push nothing further, and file blocker template B-2 (security-class) citing §99.6 risk 6 and SR-3. This is not a test defect to work around.

---

### T04 — The stricter-only negative tests (TC-L3-04/05/06) · size M · depends: T03

**Files created:** `reconciler/test/cases/TC-L3-04.sh`, `TC-L3-05.sh`, `TC-L3-06.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t04

cat > reconciler/test/cases/TC-L3-04.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-04 — repair classes are enabled one at a time (§99.6 risk 6).
# With the branch-protection repair class disabled, drift must produce a finding and no repair.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" \
  --repair-class-disabled branch_protection >/dev/null 2>&1
assert_eq "$(jq -r '[.repairs[]? | select(.registry=="branch_protection")] | length' "$out/$RUN_RECORD_PATH")" "0" \
  "a disabled repair class must never repair"
assert_ne "$(jq -r '[.findings[]? | select(.registry=="branch_protection")] | length' "$out/$RUN_RECORD_PATH")" "0" \
  "a disabled repair class must still find"
EOF

cat > reconciler/test/cases/TC-L3-05.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-05 — MANDATORY NEGATIVE. §53.3 / invariant 81 / AT-033.
# fx-strict: actual (2 approvals) is STRICTER than declared (1). Reconciliation must
# raise Level 2 for human judgment and must NOT relax the control.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$FIXTURE_ORG" \
  $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
f='[.findings[]? | select(.scope=="fx-strict" and .registry=="branch_protection")]'
assert_eq "$(jq -r "$f | length" "$out/$RUN_RECORD_PATH")" "1" "stricter-than-declared must produce exactly one finding"
assert_eq "$(jq -r "$f | .[0].level" "$out/$RUN_RECORD_PATH")" "2" "stricter-than-declared is Level 2 (§53.3)"
assert_eq "$(jq -r '[.repairs[]? | select(.scope=="fx-strict")] | length' "$out/$RUN_RECORD_PATH")" "0" \
  "reconciliation must never relax a stricter actual control"
grep -c 'MUTATING-CALL' "$out/calls.log" >/dev/null 2>&1 || true
assert_eq "$(grep -c 'fx-strict' "$L3_CALL_LOG" || true)" "0" "no write may be issued against fx-strict"
EOF

cat > reconciler/test/cases/TC-L3-06.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-06 — MANDATORY NEGATIVE. A repair plan that would LOOSEN a control must abort
# non-zero before any write (§53.3, invariant 81). Injected via a loosening declared state.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/declared/product-fx-alpha.yaml" <<'YAML'
product: fx-alpha
assignments:
  primary_owner: fx-owner
  cross_reviewer: fx-reviewer
  backup_owner: fx-owner
  primary_responder: fx-owner
branch_protection:
  required_approving_review_count: 0
  require_code_owner_reviews: false
  allow_force_pushes: true
YAML
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
set +e
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$FIXTURE_ORG" \
  $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >"$out/stdout" 2>"$out/stderr"
rc=$?
set -e
assert_nonzero "$rc" "a loosening repair plan must abort"
assert_empty "$L3_CALL_LOG"
grep -qiE 'loosen|stricter' "$out/stderr" || fail "abort must name the stricter-only rule (§53.3)"
EOF

git add reconciler/test/cases
git commit -m "L3-07-04: auto-repair must refuse to loosen (TC-L3-04/05/06)"
bash reconciler/test/run-tests.sh TC-L3-05
bash reconciler/test/run-tests.sh TC-L3-06
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-04 passes | `bash reconciler/test/run-tests.sh TC-L3-04 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-05 passes | `bash reconciler/test/run-tests.sh TC-L3-05 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-06 passes | `bash reconciler/test/run-tests.sh TC-L3-06 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 4 | Both mandatory cases exist on disk | `ls reconciler/test/cases/TC-L3-05.sh reconciler/test/cases/TC-L3-06.sh \| wc -l` | `2` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
for c in TC-L3-04 TC-L3-05 TC-L3-06; do bash reconciler/test/run-tests.sh $c | head -1; done
```
Expected, exactly:
```
PASS TC-L3-04
PASS TC-L3-05
PASS TC-L3-06
```

**STOP rule** — If `TC-L3-05` or `TC-L3-06` fails because the reconciler **did** relax a control or **did** issue a write: stop Lane 3 work, file blocker template B-2 citing §53.3, invariant 81 and AT-033. Do not weaken the test to make it pass; the test is the invariant.

---

### T05 — The seeded canary: a run that finds nothing must fail (TC-L3-07/08/09) · size M · depends: T04

**Files created:** `reconciler/test/cases/TC-L3-07.sh`, `TC-L3-08.sh`, `TC-L3-09.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t05

cat > reconciler/test/cases/TC-L3-07.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-07 — §53.1: every run records per-registry comparison counts, so a silently
# narrowed comparison is itself visible drift.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
assert_ne "$(jq -r '.comparison_counts | length' "$out/$RUN_RECORD_PATH")" "0" "run record must carry comparison counts"
assert_ne "$(jq -r '.comparison_counts.branch_protection // 0' "$out/$RUN_RECORD_PATH")" "0" \
  "branch_protection rows compared must be non-zero"
assert_ne "$(jq -r '.comparison_counts.assignments // 0' "$out/$RUN_RECORD_PATH")" "0" \
  "assignment rows compared must be non-zero"
EOF

cat > reconciler/test/cases/TC-L3-08.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-08 — MANDATORY NEGATIVE. AT-102 / §53.1: every run MUST find the seeded canary.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
assert_eq "$(jq -r '.canary.found' "$out/$RUN_RECORD_PATH")" "true" "the seeded canary must be found"
assert_eq "$(jq -r '.canary.id' "$out/$RUN_RECORD_PATH")" "CANARY-001" "the canary id must be reported"
assert_eq "$(jq -r '[.repairs[]? | select(.scope=="fx-canary")] | length' "$out/$RUN_RECORD_PATH")" "0" \
  "the canary is never repaired"
EOF

cat > reconciler/test/cases/TC-L3-09.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-09 — MANDATORY NEGATIVE. AT-102 / EC-109 / SIG-13:
# a run reporting zero findings, canary included, is a FAILED run, never a clean one.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"
mkdir -p "$src/declared" "$src/actual" "$src/canary"
cp "$L3_TEST"/fixtures/org/declared/product-fx-alpha.yaml "$src/declared/"
cp "$L3_TEST"/fixtures/org/actual/*.json "$src/actual/"
# canary/ deliberately empty: the instrument has stopped looking.
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
set +e
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >"$out/stdout" 2>"$out/stderr"
rc=$?
set -e
assert_nonzero "$rc" "a run that finds nothing must exit non-zero"
assert_file "$out/$RUN_RECORD_PATH"
assert_eq "$(jq -r '.status' "$out/$RUN_RECORD_PATH")" "failed" "the run must be recorded FAILED, not clean"
assert_eq "$(jq -r '.canary.found' "$out/$RUN_RECORD_PATH")" "false" "canary absence must be reported"
assert_eq "$(jq -r '[.signals[]? | select(.==\"SIG-13\")] | length' "$out/$RUN_RECORD_PATH")" "1" \
  "a failed run raises SIG-13 (failed reconciliations)"
EOF

git add reconciler/test/cases
git commit -m "L3-07-05: seeded canary; a run that finds nothing is a failed run"
bash reconciler/test/run-tests.sh TC-L3-08
bash reconciler/test/run-tests.sh TC-L3-09
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-07 passes | `bash reconciler/test/run-tests.sh TC-L3-07 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-08 passes | `bash reconciler/test/run-tests.sh TC-L3-08 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-09 passes | `bash reconciler/test/run-tests.sh TC-L3-09 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 4 | Suite no longer fails the mandatory-case rule | `bash reconciler/test/run-tests.sh \| grep -c MISSING-MANDATORY` | `0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
SUMMARY total=9 pass=9 fail=0
```

**STOP rule** — If `TC-L3-09` fails because the reconciler reported the empty comparison set as **clean** and exited zero: stop Lane 3 work and file blocker template B-2 citing AT-102, EC-109 and SIG-13. A reconciler that reports clean while checking nothing is the exact failure §53.1 names; it is never fixed by relaxing the test.

---

### T06 — Expiry revocation and orphan detection (TC-L3-10/11/12) · size M · depends: T05

**Files created:** `reconciler/test/cases/TC-L3-10.sh`, `TC-L3-11.sh`, `validators/drift/test/cases/TC-L3-12.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t06

cat > reconciler/test/cases/TC-L3-10.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-10 — §53.1 row "Assignment end_date" / AT-018 / AT-008 / AT-036:
# an assignment past its end_date is auto-revoked, with no human action.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$FIXTURE_ORG" \
  $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
r='[.repairs[]? | select(.subject=="fx-contractor" and .action=="revoke")]'
assert_eq "$(jq -r "$r | length" "$out/$RUN_RECORD_PATH")" "1" "expired assignment must be revoked"
assert_eq "$(jq -r "$r | .[0].human_action_required" "$out/$RUN_RECORD_PATH")" "false" \
  "expiry revocation requires no human action (AT-018)"
assert_eq "$(jq -r "$r | .[0].level" "$out/$RUN_RECORD_PATH")" "3" "expiry revocation is a Level 3 repair (§53.2)"
EOF

cat > reconciler/test/cases/TC-L3-11.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-11 — AT-037: an expired grant that cannot be auto-revoked becomes Blocking drift
# on its expiry date rather than disappearing.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
# Make the revoke impossible: the shim refuses the write for this subject.
export L3_REVOKE_FAILS="fx-contractor"
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$FIXTURE_ORG" \
  $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 || true
f='[.findings[]? | select(.subject=="fx-contractor")]'
assert_ne "$(jq -r "$f | length" "$out/$RUN_RECORD_PATH")" "0" "a failed revoke must leave a finding"
assert_eq "$(jq -r "$f | .[0].class" "$out/$RUN_RECORD_PATH")" "Blocking" \
  "a failed auto-revoke is Blocking drift (AT-037)"
EOF

cat > validators/drift/test/cases/TC-L3-12.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-12 — §12.1 orphan table / AT-017 / invariant 57 / SIG-05:
# fx-orphan has a departed Primary Owner, no Cross-Reviewer and no Primary Responder.
# All three are Blocking, and a Blocking orphan cannot be dismissed unresolved.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$L3_TEST/fixtures/org" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
o='[.findings[]? | select(.type=="orphan" and .scope=="fx-orphan")]'
assert_eq "$(jq -r "$o | length" "$out/$RUN_RECORD_PATH")" "3" "three Blocking orphan types on fx-orphan"
assert_eq "$(jq -r "$o | map(select(.class==\"Blocking\")) | length" "$out/$RUN_RECORD_PATH")" "3" \
  "all three orphans are Blocking severity"
assert_eq "$(jq -r "$o | map(select(.dismissible==true)) | length" "$out/$RUN_RECORD_PATH")" "0" \
  "Blocking orphans cannot be dismissed unresolved (invariant 57)"
assert_eq "$(jq -r '[.signals[]? | select(.=="SIG-05")] | length' "$out/$RUN_RECORD_PATH")" "1" \
  "orphan risk raises SIG-05"
EOF

git add reconciler/test/cases validators/drift/test/cases
git commit -m "L3-07-06: expiry revocation and Blocking orphan detection"
bash reconciler/test/run-tests.sh TC-L3-12
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-10 passes | `bash reconciler/test/run-tests.sh TC-L3-10 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-11 passes | `bash reconciler/test/run-tests.sh TC-L3-11 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-12 passes | `bash reconciler/test/run-tests.sh TC-L3-12 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 4 | The drift-validator case dir is populated | `ls validators/drift/test/cases/TC-L3-12.sh \| wc -l` | `1` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(reconciler/|validators/drift/)' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
SUMMARY total=12 pass=12 fail=0
```

**STOP rule** — If `TC-L3-12` reports any orphan as `dismissible: true`: stop and file blocker template B-2 citing invariant 57 and AT-017. If `TC-L3-10` shows `human_action_required: true`, file blocker template B-1 citing AT-018 — the guarantee §12.4 makes is that expiry needs no human.

---

### T07 — The machine-authority wall (TC-L3-13/14/15) · size M · depends: T06

**Files created:** `validators/drift/test/cases/TC-L3-13.sh`, `TC-L3-14.sh`, `TC-L3-15.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t07

cat > validators/drift/test/cases/TC-L3-13.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-13 — §98.2 Phase 1 completion check / §53.1 independent verifier:
# generated CODEOWNERS contains human identities only; a machine identity is Blocking drift.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/actual/codeowners.json" <<'JSON'
{"fx-alpha":["@fx-owner","@fx-reconciler[bot]"],"fx-orphan":["@fx-owner"],"fx-strict":["@fx-owner"]}
JSON
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 || true
f='[.findings[]? | select(.type=="codeowners_machine_identity")]'
assert_eq "$(jq -r "$f | length" "$out/$RUN_RECORD_PATH")" "1" "a machine identity in CODEOWNERS must be found"
assert_eq "$(jq -r "$f | .[0].class" "$out/$RUN_RECORD_PATH")" "Blocking" "it is Blocking drift"
EOF

cat > validators/drift/test/cases/TC-L3-14.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-14 — §53.1: "A workflow-file change pushed by a machine identity is Blocking-class
# drift, regardless of the change's content."
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/actual/workflow-commits.json" <<'JSON'
{"fx-alpha":[{"path":".github/workflows/ci.yml","author":"fx-reconciler[bot]","change":"whitespace only"}]}
JSON
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 || true
f='[.findings[]? | select(.type=="workflow_change_by_machine")]'
assert_eq "$(jq -r "$f | .[0].class" "$out/$RUN_RECORD_PATH")" "Blocking" \
  "machine workflow edit is Blocking regardless of content"
assert_eq "$(jq -r "$f | .[0].content_evaluated" "$out/$RUN_RECORD_PATH")" "false" \
  "the finding must not depend on the change's content"
EOF

cat > validators/drift/test/cases/TC-L3-15.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-15 — §40.1 (D107): once per run the reconciler anchors the records repository's
# head SHA and commit count into the control plane; a non-descendant head is Blocking, Level 5.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/actual/records-anchor.json" <<'JSON'
{"last_anchored_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","last_commit_count":100,
 "current_head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","current_commit_count":98,
 "head_descends_from_anchor":false}
JSON
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 || true
f='[.findings[]? | select(.type=="records_head_not_descendant")]'
assert_eq "$(jq -r "$f | .[0].class" "$out/$RUN_RECORD_PATH")" "Blocking" "a rewritten records history is Blocking"
assert_eq "$(jq -r "$f | .[0].level" "$out/$RUN_RECORD_PATH")" "5" "it escalates at Level 5 (§53.2)"
assert_ne "$(jq -r '.records_anchor.current_head_sha // ""' "$out/$RUN_RECORD_PATH")" "" \
  "every run records the records-repo head SHA"
EOF

git add validators/drift/test/cases
git commit -m "L3-07-07: machine-authority wall — CODEOWNERS, workflow edits, records anchor"
bash reconciler/test/run-tests.sh | tail -1
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-13 passes | `bash reconciler/test/run-tests.sh TC-L3-13 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-14 passes | `bash reconciler/test/run-tests.sh TC-L3-14 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-15 passes | `bash reconciler/test/run-tests.sh TC-L3-15 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 4 | Full suite green | `bash reconciler/test/run-tests.sh \| tail -1` | `SUMMARY total=15 pass=15 fail=0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^validators/drift/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
SUMMARY total=15 pass=15 fail=0
```

**STOP rule** — If `TC-L3-14` passes only when the change content is non-trivial (i.e. the reconciler evaluates content before classifying): file blocker template B-1 citing §53.1. Content-sensitivity here is a design defect, not a test-tuning question, and the decision belongs to L0.

---

### T08 — Provisioning tests (TC-L3-16/17/18) · size M · depends: T02

**Files created:** `tools/provision/test/cases/TC-L3-16.sh`, `TC-L3-17.sh`, `TC-L3-18.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t08

cat > tools/provision/test/cases/TC-L3-16.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-16 — AT-001 / §19.1: adding a product is configuration. The scaffold emits the
# full create-product set, and no hard-coded product list exists anywhere in this lane.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$PROVISION_CMD create-product --name fx-product-21 --dry-run --out "$out" >/dev/null 2>&1
assert_zero "$?" "create-product dry-run must succeed"
for item in product_yaml github_team codeowners branch_protection environments ci_workflows \
            verification_skeleton local_env_contract endpoints registrations; do
  assert_eq "$(jq -r ".emitted.$item // \"missing\"" "$out/plan.json")" "true" "create-product must emit $item (§19.1)"
done
# AT-001: "No dashboard, workflow or script contains a product list."
hits="$(grep -rInE 'fx-alpha[",: ].*fx-orphan|PRODUCTS=\(' reconciler tools/provision validators/drift \
        --include='*.sh' --include='*.yml' --include='*.yaml' --exclude-dir=test | wc -l)"
assert_eq "$hits" "0" "no product list may be hard-coded outside test fixtures (AT-001)"
EOF

cat > tools/provision/test/cases/TC-L3-17.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-17 — AT-002 / §12.6: add-person produces the registry entry, invitation, Team
# membership per assignments and capability grants; reconciliation then grants access.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$PROVISION_CMD add-person --github fx-newjoiner --role developer --dry-run --out "$out" >/dev/null 2>&1
for item in people_entry org_invitation team_membership capability_grants ai_runtime_assignment \
            onboarding_checklist_issue review_network_registration; do
  assert_eq "$(jq -r ".emitted.$item // \"missing\"" "$out/plan.json")" "true" "add-person must emit $item (§12.6)"
done
assert_eq "$(jq -r '.emitted.workflow_edits // 0' "$out/plan.json")" "0" \
  "adding a person changes no workflow, architecture or dashboard (AT-002)"
EOF

cat > tools/provision/test/cases/TC-L3-18.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-18 — invariants 79 and 80: new people, products and tools default to minimum
# privilege and draft state; every control is explicitly classified fail-closed or fail-open.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$PROVISION_CMD create-product --name fx-product-22 --dry-run --out "$out" >/dev/null 2>&1
assert_eq "$(jq -r '.defaults.org_base_permission' "$out/plan.json")" "read" "org base permission defaults to Read"
assert_eq "$(jq -r '.defaults.launch_status' "$out/plan.json")" "draft" "new products default to draft (invariant 79)"
assert_eq "$(jq -r '.defaults.branch_protection.allow_force_pushes' "$out/plan.json")" "false" "force pushes off by default"
assert_eq "$(jq -r '[.controls[]? | select(.fail_mode==null)] | length' "$out/plan.json")" "0" \
  "every control carries an explicit fail-closed/fail-open classification (invariant 80)"
EOF

git add tools/provision/test/cases
git commit -m "L3-07-08: provisioning tests for AT-001, AT-002 and safe defaults"
bash reconciler/test/run-tests.sh | tail -1
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-16 passes | `bash reconciler/test/run-tests.sh TC-L3-16 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-17 passes | `bash reconciler/test/run-tests.sh TC-L3-17 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | TC-L3-18 passes | `bash reconciler/test/run-tests.sh TC-L3-18 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 4 | No mutating call from a dry-run provisioning plan | `bash reconciler/test/run-tests.sh TC-L3-16 >/dev/null; echo rc=$?` | `rc=0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^tools/provision/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
SUMMARY total=18 pass=18 fail=0
```

**STOP rule** — If the AT-001 hard-coded-product-list grep in `TC-L3-16` returns a hit outside `test/`: do not delete the hit and do not add an exclusion. File blocker template B-1 citing AT-001 and §19.1 ("Every one of those surfaces enumerates from the product registry").

---

### T09 — Registry-change staging and external cause (TC-L3-19/20) · size M · depends: T05

**Files created:** `reconciler/test/cases/TC-L3-19.sh`, `TC-L3-20.sh`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t09

cat > reconciler/test/cases/TC-L3-19.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-19 — §26.4: "a merged registry change is applied by the next reconciliation run to
# the declared canary set only; the remainder of the fleet is held for one reconciliation
# cycle and applied only after the canary cycle records a clean run."
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/declared/canary-set.yaml" <<'YAML'
canary_set: [fx-alpha]
YAML
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_APPLY_FLAG --org "$FIXTURE_ORG" --registry-change-pending \
  $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1
assert_eq "$(jq -r '[.repairs[]? | select(.scope!="fx-alpha" and .origin=="registry-change")] | length' "$out/$RUN_RECORD_PATH")" "0" \
  "only the canary set is applied in the first cycle"
assert_eq "$(jq -r '.fleet_hold.reason' "$out/$RUN_RECORD_PATH")" "awaiting-clean-canary-cycle" \
  "the fleet is explicitly held for one cycle (§26.4)"
EOF

cat > reconciler/test/cases/TC-L3-20.sh <<'EOF'
#!/usr/bin/env bash
# TC-L3-20 — §53.1: a failure caused by an acknowledged vendor outage is annotated
# external-cause on the run record rather than raised as raw Red, and is re-executed later.
set -u; . "$L3_TEST/lib/assert.sh"
out="$(mktemp -d)"; src="$out/src"; cp -r "$L3_TEST/fixtures/org" "$src"
cat > "$src/actual/vendor-status.json" <<'JSON'
{"github":{"status":"incident","confirmed":true,"incident":"fixture vendor outage"}}
JSON
export L3_CALL_LOG="$out/calls.log"; : > "$L3_CALL_LOG"
$RECONCILE_CMD $RECONCILE_SOURCE_FLAG "$src" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 || true
assert_eq "$(jq -r '.annotation' "$out/$RUN_RECORD_PATH")" "external-cause" "the run is annotated external-cause"
assert_ne "$(jq -r '.annotation_names_outage // ""' "$out/$RUN_RECORD_PATH")" "" "the annotation names the outage"
assert_eq "$(jq -r '.reexecute_on_recovery' "$out/$RUN_RECORD_PATH")" "true" "the run re-executes once the dependency recovers"
EOF

git add reconciler/test/cases
git commit -m "L3-07-09: registry-change canary staging and external-cause annotation"
bash reconciler/test/run-tests.sh | tail -1
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | TC-L3-19 passes | `bash reconciler/test/run-tests.sh TC-L3-19 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 2 | TC-L3-20 passes | `bash reconciler/test/run-tests.sh TC-L3-20 \| tail -1` | `SUMMARY total=1 pass=1 fail=0` |
| 3 | Full suite green | `bash reconciler/test/run-tests.sh \| tail -1` | `SUMMARY total=20 pass=20 fail=0` |
| 4 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
SUMMARY total=20 pass=20 fail=0
```

**STOP rule** — If `TC-L3-20` shows a run annotated `external-cause` **without** a confirmed vendor incident in the fixture: file blocker template B-2 citing §53.1. A self-granted outage excuse turns every failed run into a clean one.

---

### T10 — The live-organisation procedure and AT-110 (TC-L3-21) · size L · depends: T09, DR-L3-07-B

This is the only task that touches the live organisation, and it runs **once, supervised, at the phase gate**.

**Files created:** `reconciler/test/live/GATE.md`, `reconciler/test/live/AT-110.sh`, `reconciler/test/live/RESULT.template.md`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t10

test -f contracts/l3-live-org-gate.md || { echo "STOP: DR-L3-07-B unresolved"; exit 1; }

cat > reconciler/test/live/GATE.md <<'EOF'
# The Lane 3 live-organisation gate (SR-3)

No Lane 3 command runs against the live organisation until ALL of the following are true:

1. `contracts/l3-live-org-gate.md` exists and names the supervising human and the authorised date.
2. Phase 3's completion check has passed: "contracts validate; registries, contracts and Team
   membership agree, machine-verified" (spec §98.2, Phase 3).
3. `bash reconciler/test/run-tests.sh` is green against the fixture organisation on the same commit.
4. The run is executed with a human watching the terminal, in plan mode first.

Order of first contact with the live organisation, never varied:
  a. plan-only run (no apply flag)          -> inspect the findings by hand
  b. AT-110 six-attempt boundary test        -> reconciler/test/live/AT-110.sh
  c. plan-only run again                     -> confirm the credential still reconciles (§40.1)
  d. apply mode, ONE repair class enabled    -> §99.6 risk 6, "repair classes enabled one at a time"
EOF

cat > reconciler/test/live/AT-110.sh <<'EOF'
#!/usr/bin/env bash
# AT-110 — "The reconciler credential is provably bounded". Six attempts must FAIL,
# then a normal reconciliation must still complete. Supervised; never run by a schedule.
# Re-executed at every credential rotation, on the same gate as §40.1's clean-run condition.
# NOTE: The six refusal attempts are read from `contracts/workflows/secret-tiers.v1.yaml`
# `must_fail` list, not hard-coded here. The reconciler credential is used to run them.
set -u
ROOT="$(git rev-parse --show-toplevel)"; export L3_TEST="$ROOT/reconciler/test"
set -a; . "$L3_TEST/harness.env"; set +a
[ -f "$ROOT/contracts/l3-live-org-gate.md" ] || { echo "STOP: gate file absent"; exit 1; }
pass=0
try_must_fail() { # $1 = label, rest = command
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "AT-110 FAIL: $label SUCCEEDED — the credential is not bounded"; exit 1
  else echo "AT-110 ok: $label refused"; pass=$((pass+1)); fi
}
try_must_fail "write a GitHub Actions secret"   gh api -X PUT  "/repos/$LIVE_ORG/control-plane/actions/secrets/AT110"
try_must_fail "write an environment"            gh api -X PUT  "/repos/$LIVE_ORG/control-plane/environments/at110"
try_must_fail "change a workflow file"          gh api -X PUT  "/repos/$LIVE_ORG/control-plane/contents/.github/workflows/at110.yml"
try_must_fail "change organisation settings"    gh api -X PATCH "/orgs/$LIVE_ORG"
try_must_fail "write to records/**"             gh api -X PUT  "/repos/$LIVE_ORG/control-plane-records/contents/records/at110.yaml"
try_must_fail "reach Layer B"                   gh api         "/orgs/$LIVE_ORG/teams/layer-b-people/members"
[ "$pass" -eq 6 ] || { echo "AT-110 FAIL: expected 6 refusals, got $pass"; exit 1; }
out="$(mktemp -d)"
$RECONCILE_CMD --org "$LIVE_ORG" $RECONCILE_OUT_FLAG "$out" >/dev/null 2>&1 \
  || { echo "AT-110 FAIL: bounded credential can no longer reconcile"; exit 1; }
echo "AT-110 PASS: 6 refusals, normal run completed"
EOF
chmod +x reconciler/test/live/AT-110.sh

cat > reconciler/test/live/RESULT.template.md <<'EOF'
# AT-110 execution record
date:
supervising human (from contracts/l3-live-org-gate.md):
commit sha:
six refusals observed: yes / no
normal reconciliation completed after the six attempts: yes / no
next re-execution due: at the next reconciler-credential rotation (§40.1, quarterly initial value)
EOF

git add reconciler/test/live
git commit -m "L3-07-10: live-organisation gate and the AT-110 bounded-credential procedure"
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | Gate file present and executable procedure staged | `test -x reconciler/test/live/AT-110.sh && echo OK` | `OK` |
| 2 | The procedure refuses to run without L0's gate file | `mv contracts/l3-live-org-gate.md /tmp/g && bash reconciler/test/live/AT-110.sh; echo rc=$? && mv /tmp/g contracts/l3-live-org-gate.md` | `STOP: gate file absent` then `rc=1` |
| 3 | Exactly six attempts are coded | `grep -c '^try_must_fail' reconciler/test/live/AT-110.sh` | `7` |
| 4 | The live procedure is not in the automatic suite | `bash reconciler/test/run-tests.sh \| grep -c 'AT-110'` | `0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
grep -c '^try_must_fail' reconciler/test/live/AT-110.sh
bash reconciler/test/run-tests.sh | tail -1
```
Expected, exactly:
```
7
SUMMARY total=20 pass=20 fail=0
```

**STOP rule** — If any of the six attempts **succeeds** during the supervised run: stop, do not retry, do not proceed to apply mode, and file blocker template B-2 as a security-class blocker citing AT-110, §40.1 and §40.3. A successful write from the reconciler credential in any of those six positions is treated as the compromise of the system's highest-privilege identity (§99.6 risk 6), which §40.1 handles as a security incident, not a build defect.

---

### T11 — Acceptance-test traceability matrix · size S · depends: T09

**Files created:** `reconciler/test/AT-TRACEABILITY.md`

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git switch integration && git pull --ff-only
git switch -c lane/3/07-t11

cat > reconciler/test/AT-TRACEABILITY.md <<'EOF'
# Lane 3 acceptance-test traceability (spec §100)

| AT | Test | Lane 3 case | Status |
| --- | --- | --- | --- |
| AT-001 | Add product 21 | TC-L3-16 | owned by L3 |
| AT-002 | Add a person | TC-L3-17 | owned by L3 |
| AT-008 | Temporary specialist / contractor joins | TC-L3-10 | reconciliation half owned by L3 |
| AT-017 | A person leaves | TC-L3-12 | orphan-detection half owned by L3 |
| AT-018 | A temporary assignment expires | TC-L3-10 | owned by L3 |
| AT-033 | No auto-loosening | TC-L3-05, TC-L3-06 | owned by L3 |
| AT-036 | A temporary access exception expires | TC-L3-10 | revocation half owned by L3 |
| AT-037 | A failed exception is visible | TC-L3-11 | drift half owned by L3 |
| AT-102 | The seeded reconciliation canary | TC-L3-08, TC-L3-09 | owned by L3 |
| AT-110 | The reconciler credential is provably bounded | TC-L3-21 (reconciler/test/live/AT-110.sh) | owned by L3, phase-gated |

Adjacent, NOT owned by Lane 3 — do not write tests for these here:
| AT-021 ownership change (record + Founder notification halves) · AT-032 self-observability
| AT-091 Layer B capability gating (datasource half) · AT-103 restore-production workflow
EOF

git add reconciler/test/AT-TRACEABILITY.md
git commit -m "L3-07-11: AT traceability matrix for Lane 3"
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
|---|---|---|---|
| 1 | Ten owned AT rows recorded | `grep -c '^| AT-' reconciler/test/AT-TRACEABILITY.md` | `10` |
| 2 | Every named case file exists | `for c in 05 06 08 09 10 11 12 16 17; do ls reconciler/test/cases/TC-L3-$c.sh tools/provision/test/cases/TC-L3-$c.sh validators/drift/test/cases/TC-L3-$c.sh 2>/dev/null; done \| wc -l` | `9` |
| 3 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^reconciler/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
grep -c '^| AT-' reconciler/test/AT-TRACEABILITY.md
```
Expected, exactly:
```
10
```

**STOP rule** — If any AT id in the matrix does not appear verbatim in spec §100: do not edit the id and do not remove the row. File blocker template B-1 quoting the mismatch. Inventing an AT id is worse than an incomplete matrix.

---

## 6. The daily runbook

Everything below is literal. Run it from the root of your `control-plane` clone. `<TASK>` is a task id from §5 lowercased with the `L3-07-` prefix dropped, e.g. `T04` → `07-t04`.

### 6.1 Start a task

**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin
git switch integration
git pull --ff-only
git switch -c lane/3/07-t04            # branch name: lane/3/<phase>-<task>
git status --short                      # expect: no output
```

If `git pull --ff-only` fails, your `integration` has local commits. Do not merge and do not force. Run `git log --oneline origin/integration..integration` and file blocker template B-1 — a lane never rewrites `integration` (PARTITION, branch & merge model).

### 6.2 Verify before you commit

**Commands**

```bash
set -euo pipefail
# 1. The suite
bash reconciler/test/run-tests.sh | tail -1

# 2. The lane-guard pre-check — run this EVERY time, before every commit
git add -A
git diff --cached --name-only \
  | grep -Ev '^(reconciler/|tools/provision/|validators/drift/)' \
  | tee /tmp/foreign-paths.txt
wc -l < /tmp/foreign-paths.txt          # expect: 0
```

`0` means every staged path is Lane 3's. Any other number means the PR will fail the lane-guard check (PARTITION rule 1) — fix it now, per §6.5, not after the PR opens.

**Commands**

```bash
set -euo pipefail
# 3. Commit
git commit -m "L3-07-04: auto-repair must refuse to loosen (TC-L3-04/05/06)"
```

### 6.3 Open the PR

**Commands**

```bash
set -euo pipefail
git push -u origin HEAD
gh pr create \
  --base integration \
  --title "L3-07-04 — auto-repair must refuse to loosen" \
  --body "Lane: L3 (Reconciler & Provisioning)
Task: L3-07-04
Paths touched: reconciler/** only
Suite: SUMMARY total=15 pass=15 fail=0
Spec: §53.3, invariant 81, AT-033
Self-verify output pasted below."
gh pr checks --watch
```

Then **stop**. Do not run `gh pr merge`. `integration` is merged by L0 in the fixed train order L1 → L4 → L2 → L3 → L5 (PARTITION, merge train). A lane never merges its own PR into the train and never merges or rebases another lane's branch.

### 6.4 Rebase on integration

Do this whenever `gh pr checks` reports the branch is behind, and once at the start of any day the branch survives.

**Commands**

```bash
set -euo pipefail
git fetch origin
git rebase origin/integration
# resolve conflicts ONLY inside reconciler/**, tools/provision/**, validators/drift/**
bash reconciler/test/run-tests.sh | tail -1
git push --force-with-lease
```

If a conflict lands in a path outside those three prefixes, abort and escalate — you are not the owner of that file:

**Commands**

```bash
set -euo pipefail
git rebase --abort
```
Then file blocker template B-1 with the conflicting path. PARTITION rule 1 has no exceptions.

### 6.5 A failing lane-guard check

**Commands**

```bash
set -euo pipefail
gh pr checks | grep -i lane-guard
gh pr diff --name-only \
  | grep -Ev '^(reconciler/|tools/provision/|validators/drift/)'
```

The second command prints the offending paths. Then, for each one:

| Situation | Action |
|---|---|
| The file was touched by accident (formatter, editor, stray `git add -A`) | `git restore --source=origin/integration --staged --worktree <path>` then re-run §6.2 and `git push --force-with-lease` |
| The file is new and should never have been created | `git rm --cached <path> && rm <path>` then re-run §6.2 |
| The change is genuinely needed in another lane's path | **Do not edit it.** File blocker template B-3 (Contract Change Request) and continue the task without that change |
| The file is under `contracts/**` | **Never.** PARTITION rule 2: `contracts/**` is frozen and L0-owned. File blocker template B-3 |

Re-verify after any of the above:

**Commands**

```bash
set -euo pipefail
git diff --name-only origin/integration...HEAD \
  | grep -Ev '^(reconciler/|tools/provision/|validators/drift/)' | wc -l   # expect: 0
git push --force-with-lease
gh pr checks --watch
```

### 6.6 End of day

**Commands**

```bash
set -euo pipefail
git push -u origin HEAD                 # never leave work only on the local machine
gh pr view --json number,statusCheckRollup -q '.number, (.statusCheckRollup[].conclusion)'
```

A Lane 3 branch is short-lived — under one day (PARTITION, branch & merge model). A branch older than one working day is itself a blocker: file template B-1 saying so rather than carrying it.

---

## 7. Blocker templates

File blockers in the `control-plane` repository, from inside the clone so `gh` infers the repo. Never continue a task past its STOP rule.

### B-1 — Standard blocker

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L3-07-04: <one line, no speculation>" \
  --label blocker --label lane-3 \
  --body "Lane: L3 (Reconciler & Provisioning)
Task: L3-07-04
Branch: $(git rev-parse --abbrev-ref HEAD)
Commit: $(git rev-parse --short HEAD)

Command run (verbatim):
<paste>

Observed output (verbatim):
<paste>

Expected output (from the task's SELF-VERIFY block):
<paste>

Files touched so far:
$(git diff --name-only origin/integration...HEAD | tr '\n' ' ')

What is blocked: <the specific acceptance criterion number>
Spec citation: <section / AT id / invariant number — quote it, never paraphrase>
Decision needed from: L0 Integrator
I have NOT: edited any path outside reconciler/**, tools/provision/**, validators/drift/**;
            weakened any test to make it pass; invented any value."
```

### B-2 — Security-class blocker (reconciler boundary or auto-repair)

Use this for any failure of `TC-L3-03`, `TC-L3-05`, `TC-L3-06`, `TC-L3-09`, `TC-L3-12` or the AT-110 procedure. Stop all Lane 3 work first.

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "SECURITY BLOCKER L3-07: reconciler boundary failure — <one line>" \
  --label blocker --label lane-3 --label security \
  --body "Class: reconciler boundary / auto-repair. Spec §99.6 risk 6: the reconciler is the
highest-privilege identity in the system.

Failing case: <TC id>
Command run (verbatim):
<paste>
Observed (verbatim):
<paste>
Expected:
<paste>

Spec citation: <§53.3 / invariant 81 / AT-033 / AT-102 / AT-110 — quote it>
Action taken: all Lane 3 work stopped at commit $(git rev-parse --short HEAD).
Nothing was retried, no test was modified, no live-organisation command was issued.
Decision needed from: L0 Integrator. §40.1 treats compromise of this credential as a
security incident under §43, not as a build defect."
```

### B-3 — Contract Change Request (a foreign path is genuinely needed)

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "CCR from L3-07: <the change needed in a path Lane 3 does not own>" \
  --label contract-change-request --label lane-3 \
  --body "Requesting lane: L3
Task: L3-07-T<nn>
Path needed (owned by another lane or by L0): <path>
Owning lane per PARTITION.md: <L0 / L1 / L2 / L4 / L5>
Why Lane 3 needs it: <one paragraph, factual>
Proposed content: <exact text or diff>
Lane 3 has NOT edited the path. PARTITION rule 2: a lane needing a contract change files a
Contract Change Request; it never edits contracts/**."
```

---

## 8. Dependency graph and sizes

| Task | Title | Size | Depends on |
|---|---|---|---|
| L3-07-01 | Bootstrap the harness | S | DR-L3-07-A (L0) |
| L3-07-02 | Build the fixture organisation | M | T01 |
| L3-07-03 | Dry-run, hermeticity, apply guard | M | T02 |
| L3-07-04 | Stricter-only negative tests | M | T03 |
| L3-07-05 | Seeded canary tests | M | T04 |
| L3-07-06 | Expiry revocation and orphans | M | T05 |
| L3-07-07 | Machine-authority wall | M | T06 |
| L3-07-08 | Provisioning tests | M | T02 |
| L3-07-09 | Registry staging, external cause | M | T05 |
| L3-07-10 | Live-org gate and AT-110 | L | T09, DR-L3-07-B (L0) |
| L3-07-11 | AT traceability matrix | S | T09 |

T08 is independent of T03–T07 and may run in parallel on its own branch. T10 never runs before the phase gate opens (SR-3).

---

## 9. Standing rules for anyone extending this file's suite

1. A new Lane 3 test case goes in `reconciler/test/cases/`, `tools/provision/test/cases/` or `validators/drift/test/cases/` — nowhere else (PARTITION rule 1).
2. A test is never weakened to make a build pass. §53.3 and §53.1 are invariants (81, 44); the test is the enforcement, and AT-033 and AT-102 are the acceptance conditions.
3. A new repair class ships with its own negative test proving it cannot loosen, and it is enabled alone (§99.6 risk 6).
4. The seeded canary is never removed, never repaired, and never excluded from a comparison set (§53.1).
5. Nothing in this lane runs against the live organisation without `contracts/l3-live-org-gate.md` and a human watching (SR-3).
6. **STOP: do not use `act` for local workflow testing.** This mirrors the `L2-06` ruling (D-L2-13). Use real GitHub Actions runners.
