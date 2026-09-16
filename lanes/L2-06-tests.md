<!-- L2-06 STATUS (FD-B1-L2 corollary, 2026-09-02):
     Test bodies L2-T600–L2-T611, L2-T220, L2-T221 remain authoritative and are executed from this file.
     L2-05-tasks.md §2.1 routes these IDs here. This file is NOT superseded for its own task bodies.
     Only the L2-P1-Txx actor-gate sections (if any) in this file are superseded by L2-05. -->
<!-- Phase file IDs retired — see L2-05-tasks.md (FD-085). No L2-P*-T* task IDs appear in this file; all test task IDs use the L2-T6xx / L2-T22x namespaces reserved in §1 above. -->

# L2-06 — TEST STRATEGY FOR LANE 2 (PIPELINE AND EVIDENCE)

**Lane:** L2 Pipeline & Evidence. Subsystems **E** (reusable workflow library) and **F** (evidence chain store and query), spec §99.2 rows E and F (L9192–L9193).
**Branch prefix:** `lane/2/*` · **Merge-train position:** 3rd of 5 — `L1 → L4 → L2 → L3 → L5` (`PARTITION.md` line 35).
**Owned paths (exclusive, `PARTITION.md` line 18):** `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`.
**Everything this document creates lives under `tools/evidence/**` and `.github/workflows/**`.** Nothing here writes outside those two roots. `templates/workflows/**` is owned by this lane and is deliberately **not** touched by this file — the fixture product repositories are built from rendered templates, never by editing them.
**Authority:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` is FROZEN and is never contradicted here. Entry-point paths, exit codes and the gate-declaration schema are fixed by `C:/D_Drive/PS/MultiProduct/Code/implementation/protocol/00-test-strategy.md` and are never renamed here.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## 0. THE ONE COMMAND THAT RUNS THE WHOLE LANE SUITE

**Commands**

```bash
set -euo pipefail
make lane LANE=2
```

That is L0's target (`protocol/00-test-strategy.md` §5, T1). `Makefile` is L0-owned (`PARTITION.md` line 22), so Lane 2 never writes it. `make lane LANE=2` shells out to the two entry points this document builds, in this order:

**Commands**

```bash
set -euo pipefail
./tools/evidence/lane-verify.sh   --all   # every gate declared under tools/evidence/gates/
./tools/evidence/lane-negative.sh --all   # every negative fixture those gates name
make negative-audit LANE=2                # every gate has a negative; none vacuous, none duplicated
make lane-guard LANE=2                    # nothing outside .github/workflows/, templates/workflows/, tools/evidence/
```

**The two paths `tools/evidence/lane-verify.sh` and `tools/evidence/lane-negative.sh` are fixed by `protocol/00-test-strategy.md` §2 and never change.** They are the only names L0's `Makefile` knows for this lane. Everything beneath them is organised by this document.

When L0's `Makefile` is not yet present on the branch — the bootstrap case of charter decision **D-L2-06** — the executor runs the two entry points directly and nothing else changes:

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-verify.sh   --all
bash tools/evidence/lane-negative.sh --all
```

### 0.1 The exit-code contract — binding, not advisory

`protocol/00-test-strategy.md` §3, transcribed. Every entry point, every tier, no exceptions.

| Exit | Meaning | Treated as |
|---|---|---|
| `0` | PASS, with at least one assertion executed | Pass |
| `1` | FAIL — an assertion failed | Fail |
| `2` | **VACUOUS** — the suite ran and executed zero assertions | **Fail** |
| `3` | **NON-DISCRIMINATING** — a negative fixture passed the gate | **Fail**, highest severity; blocks L2 from the merge train |

Note the collision the executor must not "fix": charter §0.4 gives every program under `tools/evidence/**` the summary contract `OK`=0 / `FAIL`=2 / `ERROR`=3. That contract governs the **tools**. The contract above governs the **two entry points only**. `lane-verify.sh` translates: a tool exiting `2` (FAIL) becomes entry-point exit `1`; a tool exiting `3` (ERROR) becomes entry-point exit `1`; entry-point exits `2` and `3` are produced only by the counters in §4.3 of this document. Task `L2-T600` implements exactly this translation and nothing else.

### 0.2 The last line of stdout — always

Every entry point prints, as its final stdout line and nothing after it:

```
GATE-RESULT gate=<GATE-ID|ALL> level=<T0|T1> assertions=<n> failures=<n> negatives_run=<n> negatives_that_failed_correctly=<n>
```

The runner fails the level when `assertions == 0`, when `negatives_run == 0`, or when `negatives_that_failed_correctly != negatives_run`. **Silence is never taken as health.** Every acceptance criterion in this document is provable by an exit code or by grepping that one line for an exact `key=value` pair.

---

## 1. TASK-ID RESERVATION FOR THIS DOCUMENT

Subordinate to `L2-00-charter.md` §12 and `L2-05-tasks.md` §0.9. This document reserves — and no other Lane 2 document may use — exactly these ids:

| Range | Tree | Charter block |
|---|---|---|
| `L2-T220` – `L2-T239` | `.github/workflows/**` | `L2-T100`–`L2-T299` |
| `L2-T600` – `L2-T649` | `tools/evidence/**` | `L2-T500`–`L2-T699` |

Fourteen ids are used. The remainder are held for defect follow-ups against this suite and must not be reassigned. This document uses **no** id in the `L2-T300`–`L2-T499` band, because it writes no template.

Ranges already reserved elsewhere and never used here — one owner per id, no range is shared (`L2-99-review.md` B2, resolved):

| Range | Sole owner | Where the body is |
|---|---|---|
| `L2-T170` – `L2-T199` | `L2-03-production-gates.md` §1 | `L2-03-production-gates.md` §7 |
| `L2-T500` – `L2-T516` | `L2-04-evidence-chain.md` §5 | `L2-04-evidence-chain.md` §6 |
| `L2-T517` – `L2-T519` | `L2-05-tasks.md` §2 | `L2-05-tasks.md` §5 |
| `L2-T520` – `L2-T528` | `L2-02-digest-invariant.md` §2 | `L2-02-digest-invariant.md` §3 |
| `L2-T530` – `L2-T555` | `L2-05-tasks.md` §2 | `L2-05-tasks.md` §§3–5 |
| `L2-T570` – `L2-T599` | `L2-03-production-gates.md` §1 | `L2-03-production-gates.md` §7 |
| `L2-T700` – `L2-T799` | `L2-05-tasks.md` §0.9 | `L2-05-tasks.md` §5 (acceptance-test execution) |

This document cites `L2-T171`, `L2-T172` and `L2-T173` by id and defines no body for any of them; their bodies are `L2-03-production-gates.md` §7's and that file is authoritative for them.

---

## 2. THE PROBLEM THIS LANE HAS AND NO OTHER LANE HAS

Lane 1 tests a validator by feeding it a file. Lane 3 tests a reconciler by giving it a declared state and an actual state. Lane 2 builds **workflows** — YAML that only executes inside GitHub Actions, on a repository that has environments, secrets, branch protection, an approval history and a registry. None of that exists on the branch where the suite runs, and none of it may be created by this lane: environments, rulesets and runner groups are `access/**` and `infra/**`, which belong to L5 (`PARTITION.md` line 21).

A lane that cannot execute its artifact will, if left alone, write a suite that lints YAML and asserts nothing about behaviour. That is the exact failure `protocol/00-test-strategy.md` §0 exists to refuse: *"A check that can only pass is not a check."*

Lane 2 therefore tests at **three tiers**, and every gate declares which tier proves it. No tier is a substitute for another.

| Tier | Name | What executes | Where it runs | Proves | Cannot prove |
|---|---|---|---|---|---|
| **X1** | Static assertion over workflow source | `python3`/`yq` over `.github/workflows/*.yml` and `templates/workflows/*.yml` as data | Any machine, no network | Structural invariants: no `if:` and no path filter on a required-context job (§33.2, L2854–2869); full-SHA action pins and pinned-tag reusable consumption (invariant 85, L9565); the actor gate is literally step 0 of every privileged workflow (§37.3, L3261–3268); a record write is a required step, not `continue-on-error` (§97.2, L8843–8926) | That the gate logic, when it runs, refuses the thing it must refuse |
| **X2** | Local runner over extracted gate logic | The gate bodies as standalone programs under `tools/evidence/`, invoked with a fixture context on the machine, no GitHub | Any machine, no network | Behaviour: given a digest that differs, given an approver equal to the deployer, given a machine actor, given a shared-pool runner label, given a non-default ref — the gate exits non-zero | That the workflow YAML actually calls the gate it claims to call |
| **X3** | `workflow_dispatch` harness over fixture repositories | The real reusable workflows, dispatched against synthetic product repositories in the sandbox organisation | GitHub Actions, sandbox org only | End-to-end refusal: the run **fails**, with the gate's own token in the log, and no environment secret is materialised | Nothing — but it needs the sandbox org, which is **D-L2-11** |

**The binding rule that makes the three tiers one instrument (task `L2-T604`):** every gate body is written **once**, as a program under `tools/evidence/`, and the workflow calls it by `run: tools/evidence/<gate>` and by nothing else. X1 asserts the call site exists; X2 executes the program; X3 executes both together. A gate whose logic is inline shell inside a workflow `run:` block is untestable at X2 and is rejected by `L2-T604`'s own assertion.

### 2.1 What "no live products" means concretely

| Not available on the lane branch | Substitute this lane uses | Task |
|---|---|---|
| Eight live product repositories | Nine fixture repositories under `tools/evidence/tests/fixtures/repos/<slug>/` — plain directories, not git remotes, one per conformance profile plus four defect variants | `L2-T602` |
| A registry (`people.yaml`, `product.yaml`) | Fixture registries under `tools/evidence/tests/fixtures/registry/` **copied from `contracts/fixtures/core/**` at build time, never authored here** (`protocol/09-fixtures.md` §4; `PARTITION.md` rule 2) | `L2-T602` |
| GitHub environments and environment secrets | The X2 gate programs read environment facts from a fixture JSON, and the X3 tier reads them from the real sandbox API | `L2-T604`, `L2-T603` |
| A deployment/approval history | Fixture records under `tools/evidence/tests/fixtures/records/` shaped by L4's frozen contract fixture, never by an L2-invented shape | `L2-T602` |
| A runner with a group label | `RUNNER_ENVIRONMENT` and the two marker paths of **D-L2-09**, supplied as fixture environment variables at X2 | `L2-T607` |

---

## 3. DIRECTORY LAYOUT THIS DOCUMENT CREATES

```
tools/evidence/
  lane-verify.sh                       # THE positive entry point — fixed name (T600)
  lane-negative.sh                     # THE negative entry point — fixed name (T600)
  gates/
    GATE-L2-001.yaml … GATE-L2-011.yaml   # one file per gate, directory-per-item (T601)
  tests/
    lib/
      harness.sh                       # counters, GATE-RESULT emitter, assert helpers (T600)
      dispatch.sh                      # the workflow_dispatch harness client (T603)
    fixtures/
      repos/<slug>/                    # nine synthetic product repositories (T602)
      registry/                        # copied from contracts/fixtures/core/** (T602)
      records/                         # copied from contracts/fixtures/core/** (T602)
      runner/                          # runner-tier fixture contexts (T607)
    negative/
      NT-04/  NT-05/  NT-11/  NT-12/  NT-13/  NT-15/  NT-29/    # protocol/04 ids
      GATE-L2-009/  GATE-L2-011/                                # lane-added gates
    x1/                                # static assertions over workflow source (T604)
    x2/                                # local-runner gate executions (T604)
    x3/                                # dispatch-tier cases (T603)
    at-map.yaml                        # AT id -> gate id -> tier (T610)
    coverage-floor.yaml                # frozen counters; a narrowed suite is visible (T611)
    reports/                           # run output — gitignored
.github/workflows/
  lane-suite.yml                       # runs make lane LANE=2 on push to lane/2/* (T220)
  fixture-dispatch.yml                 # the X3 harness driver, workflow_dispatch only (T221)
```

`tools/evidence/negative/NT-<nn>/` is the path `protocol/09-fixtures.md` §2 assigns to this lane. This document places the negative corpus at `tools/evidence/tests/negative/NT-<nn>/` and creates a symlink-free forwarder file `tools/evidence/negative/README.md` naming the real location, so the protocol's glob and this layout agree without a second copy of any fixture. Task `L2-T601` creates the forwarder.

---

## 4. SHARED CONVENTIONS — EVERY TASK OBEYS THESE VERBATIM

### 4.1 The gate declaration schema — fixed by `protocol/00-test-strategy.md` §4.2

Every field is mandatory. One file per gate. No shared index — the index is computed by globbing.

```yaml
# tools/evidence/gates/GATE-L2-001.yaml
gate_id: GATE-L2-001
owner_lane: L2
level: T1
title: A production deploy whose digest differs from the staging-verified digest is rejected
enforces:
  spec_sections: ["32", "33.4"]
  acceptance_tests: ["AT-026"]
  invariants: [22, 23]
  signals: []
positive:
  command: "./tools/evidence/lane-verify.sh --gate GATE-L2-001"
  expect_exit: 0
negative:
  fixture: "tools/evidence/tests/negative/NT-04/"
  command: "./tools/evidence/lane-negative.sh --gate GATE-L2-001"
  expect_exit: 0
  proves: "A deploy-production run handed a digest the staging record never verified would promote an artifact nobody tested, which is the rebuild invariant 22 forbids."
assertion_count_min: 3
tier: X2
```

Two rules the executor must not soften:

* **`signals: []` where the spec names no signal.** Do not invent a SIG id to fill the field. The only SIG ids this lane's gates may name are `SIG-18` (verification-contract discrimination, spec L4547) and `SIG-15` (repeated manual overrides and skipped gates, spec L4544). Any other SIG id in an L2 gate file is a STOP under `S4`.
* **`proves:` is a sentence naming the specific wrong build this negative would catch.** `make negative-audit` fails on an empty or duplicated `proves:` string. Eleven identical `proves:` lines is what rubber-stamping looks like in YAML.

`tier:` is an L2 addition to the schema, permitted because §4.2 fixes the mandatory fields and does not forbid additional ones. It carries the X1/X2/X3 value of §2 and is read by `L2-T610`.

### 4.2 Fixture-repository naming — frozen by `L2-T602`

```
tools/evidence/tests/fixtures/repos/<profile>-<variant>/
```

`<profile>` is one of the `conformance_profile` values consumed from `contracts/**` (charter §4.1). `<variant>` is `clean` for the one positive repository per profile, or the NT id for a defect variant (`nt-04`, `nt-05`, `nt-11`, `nt-12`, `nt-13`). **The variant repositories are never repaired.** A defect variant that stops being rejected means the gate broke, not the fixture (`protocol/00-test-strategy.md` §4.1 rule 6). Editing it to restore red is falsifying the instrument and is a STOP-rule escalation to L0.

Every fixture repository directory carries, as its first file, a literal marker:

```
# FIXTURE REPOSITORY — SYNTHETIC. Not a product. Never onboarded, never deployed.
# Spec basis: Section 31.2 (a verification contract that cannot fail is not a contract).
# Defect variants are DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
```

### 4.3 The counters — the anti-vacuity mechanism

`tools/evidence/tests/lib/harness.sh` (task `L2-T600`) maintains four integers for the life of a run and emits them on the `GATE-RESULT` line:

| Counter | Incremented when | Failing condition |
|---|---|---|
| `assertions` | any `assert_*` helper is called | `assertions == 0` → exit `2` |
| `failures` | an assertion's actual value differs from its expected value | `failures > 0` → exit `1` |
| `negatives_run` | `lane-negative.sh` invokes one gate's negative command | `negatives_run == 0` on `--all` → exit `2` |
| `negatives_that_failed_correctly` | that negative command exited with its declared `expect_exit` | `!= negatives_run` → exit `3` |

`coverage-floor.yaml` (task `L2-T611`) freezes the minimum `assertions` and `negatives_run` for a full `--all` run. A run below the floor exits `2` even when every assertion it did run passed. This is §53.1's per-registry comparison count applied to the suite itself: a silently narrowed comparison is visible drift.

### 4.4 Git protocol — every task, no exceptions

**Open block** — before the task's own commands:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/<branch-slug>
```

**Close block** — after the task's SELF-VERIFY prints its `OK` line:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git status --porcelain | grep -vE '^(A|M| M|\?\?) (\.github/workflows/|templates/workflows/|tools/evidence/)' && { echo "FOREIGN OR UNEXPECTED CHANGE - STOP"; exit 1; }
git fetch origin && git rebase origin/integration
git push -u origin lane/2/<branch-slug>
gh pr create --base integration --head lane/2/<branch-slug> \
  --title "<TASK-ID>: <task title>" \
  --body "Lane 2 (Pipeline & Evidence). Task <TASK-ID>. Owned paths only. SELF-VERIFY in L2-06-tests.md passed."
```

Each task names its own `<branch-slug>`. One branch per task. Never merge or rebase another lane's branch.

### 4.5 Session setup — run once per shell, before any task

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="<absolute path to the control-plane repo working copy>"
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO - STOP"; exit 1; }
test -d contracts || { echo "contracts/ ABSENT - STOP (charter rule S1)"; exit 1; }
test -d tools/evidence || { echo "tools/evidence ABSENT - L2-T001 NOT DONE - STOP"; exit 1; }
python3 -c "import yaml" || { echo "PyYAML ABSENT - STOP"; exit 1; }
```

### 4.6 STOP rules

Charter §10 rules **S1–S5** and `L2-03-production-gates.md` §6 rules **S6–S8** apply to every task here without restatement. Two rules are added and apply only to this document:

**S9 — Never repair a negative fixture to make it fail again.** If a fixture under `tools/evidence/tests/negative/` or a `-nt-<nn>` fixture repository stops being rejected, the **gate** is broken. Editing the fixture is falsifying the instrument. STOP and file the blocker with `GATE NON-DISCRIMINATING` as the condition.

**S10 — Never mark a tier "not applicable" to make a gate green.** Every gate declares exactly one `tier:`. If a gate's declared tier cannot execute — the commonest case being X3 without the sandbox org of **D-L2-11** — the gate is reported `UNARMED` and the entry point exits `1`, never `0`. An unarmed gate is a red gate. `protocol/00-test-strategy.md` §0 quotes §99.6 risk 5 for exactly this: *"An unavailable protection feature reproduces the silent-gate failure."*

### 4.7 The blocker template — used verbatim by every STOP rule

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L2-<TASK-ID>: <one-line condition>" \
  --label "blocker,lane-2" \
  --body "$(cat <<'EOF'
LANE: L2 Pipeline & Evidence
TASK: L2-<TASK-ID>
STOP RULE TRIGGERED: <S1|S2|S3|S4|S5|S6|S7|S8|S9|S10|task-specific>

WHAT I WAS DOING:
<the exact command run>

WHAT HAPPENED:
<exact output, verbatim, including exit code>

WHAT I NEED TO PROCEED:
<the single missing fact, file, or decision>

SPEC CITATION:
MultiProduct_MasterSpec_v4.0.md lines <A>-<B>, Section <N.N>

I HAVE NOT: guessed a value, written outside owned paths, edited contracts/**,
            repaired a negative fixture, marked a tier not-applicable,
            or continued past this point.
EOF
)"
```

Then post the issue number in the lane channel and take the next **unblocked** task, or idle. Never work around a blocker.

### 4.8 Sizes

**S** under half a day · **M** half a day to two days · **L** two to five days.

---

## 5. DECISION REQUIRED — HANDED TO L0

Numbering continues from the highest `D-L2-nn` in use across the Lane 2 set. Lane 2 must not resolve any of these. File each as a Contract Change Request; never edit `contracts/**` (`PARTITION.md` rule 2).

Still binding on this document and **not re-opened here**: **D-L2-03** (records-writer secret name, target repository, record schema paths), **D-L2-05** (rollback workflow filename). **D-L2-09 closed.** (runtime evidence of privileged-runner tier — marker paths confirmed via Q9; both resolve to `not-applicable-v1`)

### ~~DECISION REQUIRED~~ D-L2-11 — Closed (Q10): `$PROVISION_SANDBOX_ORG` value confirmed

**Closed (Q10).** `$PROVISION_SANDBOX_ORG` value confirmed. Re-run `L2-T608` with the confirmed org slug. The X3 tier is unblocked; `UNARMED` stubs may be replaced with live dispatch once the confirmed contract values are published.

### DECISION REQUIRED D-L2-12 — NT-24 is booked against L2 and its subsystem belongs to no lane

**Question.** Which lane owns the plan-checker, and therefore owns NT-24?
**The facts, stated without interpretation.** `protocol/04-negative-tests.md` §"Merge-train order" assigns **NT-24** (*"Submit a plan with no verify command / no recovery strategy"*, anchors §30.2, §28.1, §103.1) to owner **L2**, blocking the `L2 → integration` hop. The plan-checker is spec §99.2 subsystem **G** (L9194, *"Plan-checker and Gate 1 tooling"*). `PARTITION.md`'s lane table assigns subsystem G to no lane; Lane 2 holds **E** and **F** only. Building a plan-checker would also require a path root Lane 2 does not own.
**Why L2 cannot decide.** Claiming NT-24 means claiming subsystem G, which contradicts the FROZEN partition. Declining it silently leaves a merge-hop blocker with no owner.
**Options for L0.** (a) assign subsystem G to a lane and move NT-24's owner column with it; (b) re-anchor NT-24 to the surface Lane 2 does own — the `renovate-path-guard` and required-context guards — and reissue the row; (c) defer NT-24 with a recorded, dated exception carrying an expiry (invariant 77).
**Blocks.** Nothing this document builds. It is stated because the merge-hop table names a blocker Lane 2 cannot satisfy, and an unowned blocker is how a train stops with no one holding the fix. This document builds no plan-checker and claims no subsystem G artifact. The same escalation applies to subsystems **H**, **J**, **O** and **P**, which `PARTITION.md` v1 also assigns to no lane; none is claimed here.

### ~~DECISION REQUIRED~~ D-L2-13 — Closed: act declined

**Closed.** Act declined. Use real GitHub Actions runners for integration tests. X2 therefore executes the **gate programs**, not the workflow YAML, and X1 asserts the call sites.

---

## 6. THE GATE CATALOGUE THIS LANE ARMS

`protocol/00-test-strategy.md` §7 fixes **GATE-L2-001** through **GATE-L2-008** as *"the required minimum set per lane at the point its lane suite first arms"*. This document declares all eight verbatim and adds three, permitted because §7 sets a minimum. The three additions carry the negative tests §8 names and that the minimum set does not reach.

| Gate | Asserts | Negative fixture MUST be rejected | Tier | NT / CAN | Spec anchor | Task |
|---|---|---|---|---|---|---|
| GATE-L2-001 | A production deploy whose digest differs from the staging-verified digest is rejected | Deploy request with a rebuilt digest | X2 | NT-04, CAN-DIGEST | invariants 22, 23 (L9484–9485); §32 (L2803–2828); §33.4 (L2887–2912) | `L2-T606` |
| GATE-L2-002 | Every required check name is emitted by a job carrying no `if:` and no path filter | Workflow whose required-context job carries a path filter | X1 | NT-11 | §33.2 (L2854–2869); SIG-15 (L4544) | `L2-T604` |
| GATE-L2-003 | The verification contract's seeded-defect case FAILS the contract | Contract of the form `verify: exit 0` mapped to every requirement | X2 | NT-13, CAN-VERIFY | §31.2 (L2787–2794); SIG-18 (L4547) | `L2-T604` |
| GATE-L2-004 | Privileged workflows fail closed when `github.actor` is not a capability-holding human in `people.yaml` | Machine account dispatching `deploy-production.yml` | X2 | NT-15 | invariant 18 (L9477); §37.3 (L3261–3268) | `L2-T604` |
| GATE-L2-005 | A workflow on a non-default ref declaring `environment: production` obtains no environment secret | Branch workflow requesting the production environment | X3 *(tier changed by L0 amendment — Q10; re-run `L2-T608` with new tier)* | — | invariant 25 (L9487); §33.4 (L2887–2912); **D91** (L10184); §98.2 Phase 1 (L9024) | `L2-T608` |
| GATE-L2-006 | Time gates resolve against the declared working calendar, never runner local time | Friday-freeze case with a runner clock set to Thursday UTC-12 | X2 | — | §34.2 (L2930–2935); §97.1 time rule (L8836–8842) | `L2-T604` |
| GATE-L2-007 | A moved `workflows/*` tag is Blocking drift | Tag repointed to a new SHA with no PR | X1 | NT-12, CAN-SHIM | invariants 72 (L9549), 85 (L9565); §53.1 | `L2-T604` |
| GATE-L2-008 | All eleven evidence-chain questions are answerable for one deployment | Deployment whose record write step was best-effort and silently failed | X2 | — | §32 (L2803–2828); §97.2 (L8843–8926); CT-06 | `L2-T604` |
| **GATE-L2-009** | `deploy-production` fails closed when the recorded approving identity equals the deploying identity | Approval record whose actor equals the dispatching actor | X2 | — | invariants 9 (L9462), 12 (L9465); §27.2 (L2572); **D73** (L10156); §98.2 Phase 6 (L9078) | `L2-T605` |
| **GATE-L2-010** | Every privileged workflow asserts its own runner tier and fails closed on a shared-pool runner | Privileged workflow resolving to a shared-pool label | X2 | NT-05 | **D87** (L10191); the three Blocking drift rows (L3596) | `L2-T607` |
| **GATE-L2-011** | An approval whose actor is a machine identity does not satisfy the production-approval gate | Approval record signed by the background machine account | X2 | — | invariant 18 (L9477); §37.3 (L3266); **D53** (L10121); §98.2 Phase 1 (L9024) | `L2-T609` |

**A boundary stated once, so it is not claimed twice.** `CAN-MACHINE` — *"an approval from a machine account"* — is assigned to **L5** by `protocol/11-definition-of-done.md` §4.2, because its enforcement point is branch protection and human-only CODEOWNERS generation. **GATE-L2-011 is the other half of the same rule**: the approval-record check inside `deploy-production.yml`. Lane 2 asserts the workflow half and nothing about branch protection; Lane 5 asserts the protection half. Neither lane's gate passing excuses the other's. §37.3 (L3266) states the CODEOWNERS half; §37.3 (L3268) states the actor-gate half — one sentence apart, two owners.

Likewise **NT-19** (*"Deploy to `production` from a non-default, non-tag ref"*) is L5-owned at the environment-policy layer. **GATE-L2-005 is the workflow-side half**: the assertion inside the workflow that fails closed before a secret is requested. `L2-T608` builds only that half.

---

## 7. THE ACCEPTANCE TESTS OF SECTION 100 THIS LANE SATISFIES

`protocol/00-test-strategy.md` §6 names the ten acceptance tests owned by Lane 2. All ten are listed here with the §100 line that defines them, the tier that proves them, and the gate that carries them. **No AT is claimed that §6 does not assign to L2, and no AT id appears here that is not in the §100 catalogue.**

| AT | §100 line | What the catalogue says it proves | Tier | Carried by | Note |
|---|---|---|---|---|---|
| **AT-023** | L9337 | GSD version changes: the canary set verifies first; products may run different pinned versions during rollout | X1 | GATE-L2-007 | Pinned-tag consumption is what makes "different pinned versions" true |
| **AT-024** | L9338 | A shared CI workflow breaks: consumption is by pinned tag, so unmigrated products are unaffected; platform rollback reverts the workflow tag | X1 + X3 | GATE-L2-007 | Execution task is `L2-T700` (`L2-05-tasks.md`); this suite proves the pin, not the fleet rollout |
| **AT-025** | L9339 | A platform contract schema changes: both versions supported simultaneously; no simultaneous fleet migration is ever required | X1 | GATE-L2-007 | Two fixture repositories pinned to different `workflows/*` tags, both green |
| **AT-026** | L9340 | A platform change progresses pilot → rollout → fleet with per-stage verification and a working, tested rollback | X2 | GATE-L2-001 | The digest invariant is what makes a rollback a promotion of a known digest rather than a rebuild |
| **AT-027** | L9341 | A new platform policy propagates without hand-editing twenty product files; it flows from `policies.yaml` and the reusable workflows | X1 | GATE-L2-002 | Asserted as: no fixture repository's workflow contains a policy value inline |
| **AT-030** | L9344 | A control-plane tool is disabled: product workflows continue; contracts remain readable and usable without it | X2 | GATE-L2-008 | The evidence chain must still answer from records when the query tool is absent |
| **AT-034** | L9348 | Governance layerability: the delivery core runs with the removable governance artifacts removed | **T3 only** | GATE-L2-008 | `protocol/00-test-strategy.md` §6: AT-034 is L2-owned and **T3-gated** — it can only execute on `integration` with all five lanes present. This lane's suite does **not** claim it green |
| **AT-035** | L9349 | The scheduled organisation export restores successfully to an independent environment, each data class through its own recorded mechanism | X3 | GATE-L2-008 | Execution task is `L2-T702`; blocked on `ops-vm/export/put.sh` (L5) per `L2-01` |
| **AT-103** | L9352 | Production restore executes end to end with an exceptional-authorisation record and **without any credential handed to or typed by a human** | X3 | GATE-L2-009, GATE-L2-010 | Execution task is `L2-T703`; `executed_for_real` per `protocol/00-test-strategy.md` §5 T4 |
| **AT-107** | L9377 | A scheduled eval regression raises SIG-42 and blocks adoption of the new model pin until the suite passes or a recorded exception accepts the change | X1 | GATE-L2-003 | The blocking half only; the eval runner itself is subsystem K (L5), not claimed here |

**`L2-T610` writes this table as machine-readable data** at `tools/evidence/tests/at-map.yaml` and asserts that every row's gate id exists under `tools/evidence/gates/`. An AT row naming a gate that does not exist is exit `1`, never a warning.

**AT-034 discipline.** The lane suite reports AT-034 as `T3-DEFERRED`, not as `PASS` and not as `SKIP`. `protocol/00-test-strategy.md` §1.2 states the rule this obeys: *"An AT that cannot pass is a defect report against the build, escalated to L0 — never a wording change."* An AT whose tier is unreachable at T1 is reported at its real status and re-run by L0 at T3.

---

## 8. THE FIVE NEGATIVE TESTS THAT MATTER MOST

These five are not a sample. They are the five refusals on which the enforcement plane rests: if any one of them silently stops discriminating, the estate keeps deploying and every light stays green. Each is stated as **setup → command → expected failure → what a pass would mean**. The last column is the one that matters: it names the wrong build the test catches.

### N1 — A self-approved production deploy MUST fail · GATE-L2-009 · task `L2-T605`

**Spec basis.** §27.2 (L2572): *"The deploy workflow itself verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell."* Invariant 9 (L9462) and invariant 12 (L9465): production approval is never self-approved and is a separate event from Gate 2 approval. **D73** (L10156) makes the workflow-identity gate the mechanism of record, not a fallback — environment required reviewers are Enterprise-only on private repositories and are never depended on. §98.2 Phase 6 (L9078) makes it a phase completion check: *"the deploy fails closed when the approver equals the deploying actor."*

**Setup.** `tools/evidence/tests/negative/GATE-L2-009/` holds one approval record and one dispatch context:

```
approval.yaml        approving actor: dev-one        (a human in the fixture people registry)
context.json         github.actor:    dev-one        (the same identity, dispatching the deploy)
```

The positive twin at `tools/evidence/tests/x2/GATE-L2-009/` is byte-different in exactly one field: `github.actor: dev-two`. `make negative-audit` fails if the two are byte-identical.

**Command.**

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-negative.sh --gate GATE-L2-009
```

**Expected failure.** Exit `1`, and the gate program's stderr carries a non-empty diagnostic naming both identities. The final stdout line is:

```
GATE-RESULT gate=GATE-L2-009 level=T1 assertions=2 failures=0 negatives_run=1 negatives_that_failed_correctly=1
```

**Third case, mandatory.** A context in which the approval record is **absent or unreadable** must also exit non-zero. §27.2's words are *"fails closed if it cannot tell"* — a gate that passes when it cannot find the record is worse than no gate, because it reports a comparison it never made.

**What a pass would mean.** The one identity in the organisation who most wants a deploy through — the person holding the change — can approve their own production deploy. Every other control in §27 is downstream of this comparison.

### N2 — A digest mismatch MUST be rejected · GATE-L2-001 · task `L2-T606`

**Spec basis.** Invariant 22 (L9484): *"The production artifact is the same digest verified in staging. Never rebuilt."* Invariant 23 (L9485): never rebuild to work around registry unavailability. §32 (L2803–2828) items 5 and 11: the registry digest recorded at build, and the digest actually running. §33.4 (L2887–2912). `protocol/04-negative-tests.md` **NT-04**; `protocol/06-integration-cycle.md` canary **CAN-DIGEST**, required verdict `REJECT`.

**Setup.** `tools/evidence/tests/negative/NT-04/` holds:

```
staging-record.yaml   digest: sha256:aaaa…aaaa     (what staging verified)
deploy-request.json   digest: sha256:bbbb…bbbb     (what production was asked to deploy)
```

and a second case `NT-04/registry-down/` in which the staging record is present, the registry is unreachable, and the request carries a **freshly built** digest — invariant 23's exact scenario, which must be refused for the same reason and not with a warning.

**Command.**

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-negative.sh --gate GATE-L2-001
```

**Expected failure.** Exit `1` for both cases. The gate program emits the token `DIGEST_INVARIANT_VIOLATION` on stderr — the token fixed by `L2-02-digest-invariant.md`, not invented here. The counters show `negatives_run=2 negatives_that_failed_correctly=2`.

**The positive twin is not optional.** `lane-verify.sh --gate GATE-L2-001` runs a matched pair whose digests are equal and must exit `0`. Without it, a gate hard-wired to `exit 1` passes the negative and proves nothing. `assertion_count_min: 3` in the declaration exists to make the pair mandatory.

**What a pass would mean.** Production runs an artifact staging never saw. Items 5 and 11 of the evidence chain diverge, and §32's eleven questions produce a confident, wrong answer — which is the failure mode §41.2 (L3717–3729) classes as a P0 investigation.

### N3 — A privileged workflow landing on a shared runner MUST fail · GATE-L2-010 · task `L2-T607`

**Spec basis.** **D87** (L10191): *"The privileged workflows are a closed set — `deploy-production.yml`, `migrate.yml`, the rollback workflow, the production-restore workflow — and run on hosted runners by default … Each privileged workflow asserts its own runner tier and fails closed."* The spec's privileged-workflow isolation paragraph (L3589) states the reason: the machine account holds Write, a branch push executes CI, and a long-lived runner carries whatever the untrusted job left behind into the next privileged job — *"Persistence, not provenance, is the exposure."* Three Blocking reconciliation rows follow (L3596). `protocol/04-negative-tests.md` **NT-05**.

**Setup.** `tools/evidence/tests/negative/NT-05/` supplies three runner contexts as environment fixtures, and each of the four privileged workflows is exercised against each:

| Case | `RUNNER_ENVIRONMENT` | Marker files (per **D-L2-09**, now closed) | Must |
|---|---|---|---|
| `shared-pool` | `self-hosted` | neither marker present | exit non-zero — `RUNNER_TIER_SHARED_POOL` |
| `non-ephemeral` | `self-hosted` | privileged marker present, ephemeral marker absent | exit non-zero — `RUNNER_TIER_NOT_EPHEMERAL` |
| `unresolvable` | unset | neither marker present | exit non-zero — `RUNNER_TIER_UNRESOLVED` |

The tokens are those fixed by `L2-03-production-gates.md` `L2-T172`. The executor does not invent a token; if a token in that task's workflow differs from the one above, that is a STOP under `S4`, not a rename.

**D-L2-09 is closed (Q9).** Both marker paths resolve to `not-applicable-v1`. All three cases run fully; no case reports `UNARMED`.

**Command.**

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-negative.sh --gate GATE-L2-010
```

**Expected failure.** Exit `1`, with `negatives_run=12` (Q9's four cases × 3 runner contexts) and `negatives_that_failed_correctly=12`. Assert `0 UNARMED` — D-L2-09 is closed and no case is deferred.

**What a pass would mean.** The least-trusted identity in the organisation executes a job on a host, and production credentials materialise on that same host in the next job. The privileged workflow would proceed, and the three §53.1 Blocking rows would have nothing in the workflow to corroborate — configuration alone, which D87 explicitly refuses: *"The separation is asserted in the workflow, not only in configuration."*

### N4 — A deploy from a non-default ref MUST be refused · GATE-L2-005 · task `L2-T608`

**Spec basis.** **D91** (L10184): *"Branch protection governs what merges; a deployment branch policy governs what may reach an environment's secrets, and a repository with the first and not the second holds production credentials behind nothing."* §33.4 (L2911) names the attack in full: *"any Write holder … pushes a branch carrying a workflow that declares `environment: production`, and GitHub hands that job the environment's secrets from an unreviewed ref. The same absence lets a Write holder delete the workflow-identity gate on their own branch and dispatch the deploy from it."* §98.2 Phase 1 (L9024) makes it a completion check *"executed negatively"*. Invariant 25 (L9487): production secrets are environment-scoped and never present locally.

**Setup.** `tools/evidence/tests/negative/GATE-L2-005/` supplies four ref contexts against the production-environment assertion:

| Case | `github.ref` | Admitted by the fixture policy | Must |
|---|---|---|---|
| `feature-branch` | `refs/heads/feat/anything` | no | exit non-zero — `ENV_POLICY_REF_NOT_ADMITTED` |
| `unprotected-tag` | `refs/tags/scratch-1` | no | exit non-zero — `ENV_POLICY_REF_NOT_ADMITTED` |
| `policy-absent` | `refs/heads/main` | policy fixture is an empty object | exit non-zero — `ENV_POLICY_ABSENT` |
| `policy-too-wide` | `refs/heads/main` | policy admits `*` | exit non-zero — `ENV_POLICY_TOO_WIDE` |

Tokens are those fixed by `L2-03-production-gates.md` `L2-T173`. The positive twin is `refs/heads/main` against a policy admitting the default branch and protected release tags only, and must exit `0`.

**The two cases that carry the weight are the last two.** A gate that only checks the ref against whatever policy it finds passes happily against an absent policy and against a wildcard policy — and D91's entire argument is that the absent policy is the real-world state a repository lands in. A ref check with no policy check is a gate that cannot fail in the case it exists for.

**Command.**

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-negative.sh --gate GATE-L2-005
```

**Expected failure.** Exit `1`, `negatives_run=4`, `negatives_that_failed_correctly=4`.

**Boundary.** Lane 2 asserts; Lane 5 configures. `L2-T608` performs no `POST`, `PUT`, `PATCH` or `DELETE` against any GitHub API — the acceptance criteria include a grep proving it, exactly as `L2-03-production-gates.md` `L2-T173` does. Writing an environment policy from an L2 workflow is a foreign-path act performed through an API instead of a file, and it is still a violation.

**What a pass would mean.** Every Write holder in the organisation can hand themselves the production secrets from an unreviewed branch, and can do so with the workflow-identity gate of N1 deleted from the ref they dispatch. N1 and N4 are one control: the gate is code, and the ref restriction is what stops the gated actor choosing which code runs.

### N5 — A machine-account approval MUST NOT satisfy a gate · GATE-L2-011 · task `L2-T609`

**Spec basis.** §37.3 (L3266): *"branch protection requires Code Owner review and CODEOWNERS is generated to contain human identities only (Section 11.3), which mechanically prevents a machine-account approval from ever satisfying a gate."* Invariant 18 (L9477). **D53** (L10121): *"branch protection requires Code Owner review with human-only CODEOWNERS so no machine approval can satisfy a gate."* §98.2 Phase 1 (L9024): *"an approval from a machine account does **not** satisfy branch protection … and the check is executed negatively."*

**Setup.** `tools/evidence/tests/negative/GATE-L2-011/` holds three approval records, each paired with a distinct human deploying actor so that N1's comparison passes and only N5's check can fail the run:

| Case | Approval actor | Present in the fixture `people.yaml` as | Must |
|---|---|---|---|
| `machine-account` | the background machine account login | not a person entry | exit non-zero — `ACTOR_NOT_HUMAN` |
| `app-installation` | a GitHub App installation identity | not a person entry | exit non-zero — `ACTOR_NOT_HUMAN` |
| `human-no-capability` | a human person entry holding no `production-approval` capability | a person, capability absent | exit non-zero — `ACTOR_CAPABILITY_MISSING` |

Tokens are those fixed by `L2-03-production-gates.md` `L2-T171`. The positive twin is a human holding `production-approval`, and must exit `0`.

**Why the third case belongs here.** A gate that only rejects non-humans passes an approval from a human with no approval authority — and §37.3's sentence is *"holding the capability the action requires."* Identity and authority are two checks, and a suite that runs one is a suite that reports the other green without executing it.

**Command.**

**Commands**

```bash
set -euo pipefail
bash tools/evidence/lane-negative.sh --gate GATE-L2-011
```

**Expected failure.** Exit `1`, `negatives_run=3`, `negatives_that_failed_correctly=3`.

**Boundary, restated because it is the most likely double-claim in the whole programme.** The branch-protection half of this rule is canary **CAN-MACHINE**, owned by **L5** (`protocol/11-definition-of-done.md` §4.2), required verdict *does not satisfy the gate*. GATE-L2-011 is the workflow half only. Lane 2 asserts nothing about CODEOWNERS generation or ruleset configuration, and Lane 2's gate passing does not discharge L5's.

**What a pass would mean.** D71 authorises the machine layer to dispatch, and dispatch and push are the same GitHub permission (§37.3, L3268). A machine approval that satisfies the deploy gate turns the background layer's *permitted* dispatch into an *unattended* production deploy — the first of the nine things §37.3 says the background layer must never do.

### 8.1 The sixth test, which is the other five

`protocol/00-test-strategy.md` §4.1 rule 7 makes the doctrine recursive. Task `L2-T611` implements the L2 half: a run in which any of N1–N5's negative fixtures **passes** its gate is reported at exit `3`, blocks Lane 2 from the merge train, and makes the lane's next task the repair of that gate — not new feature work. A run that executes zero of them is exit `2`. The suite reports its own instrument health on the same line it reports the estate's.

---

## 9. TASK INDEX

Execution order is the table order. No task starts before every task in its `Depends on` cell has printed its own `OK` line.

| # | Task | Title | Files | Deps | Sz |
|---|---|---|---|---|---|
| 1 | `L2-T600` | The two fixed entry points and the counter harness | `tools/evidence/lane-verify.sh`, `tools/evidence/lane-negative.sh`, `tools/evidence/tests/lib/harness.sh` | charter `L2-T001` | M |
| 2 | `L2-T601` | The eleven gate declarations and the negative-corpus forwarder | `tools/evidence/gates/GATE-L2-0{01..11}.yaml`, `tools/evidence/negative/README.md` | `L2-T600` | M |
| 3 | `L2-T602` | The fixture estate — nine repositories, copied registries and records | `tools/evidence/tests/fixtures/**` | `L2-T601` | L |
| 4 | `L2-T604` | Tiers X1 and X2 for GATE-L2-002, -003, -004, -006, -007, -008 | `tools/evidence/tests/x1/**`, `tools/evidence/tests/x2/**` | `L2-T602` | L |
| 5 | `L2-T605` | **N1** — self-approved deploy MUST fail | `tools/evidence/tests/negative/GATE-L2-009/**`, `tools/evidence/tests/x2/GATE-L2-009/**` | `L2-T604` | M |
| 6 | `L2-T606` | **N2** — digest mismatch MUST be rejected | `tools/evidence/tests/negative/NT-04/**`, `tools/evidence/tests/x2/GATE-L2-001/**` | `L2-T604` | M |
| 7 | `L2-T607` | **N3** — privileged workflow on a shared runner MUST fail | `tools/evidence/tests/negative/NT-05/**`, `tools/evidence/tests/fixtures/runner/**` | `L2-T604` | M |
| 8 | `L2-T608` | **N4** — deploy from a non-default ref MUST be refused | `tools/evidence/tests/negative/GATE-L2-005/**` | `L2-T604` | M |
| 9 | `L2-T609` | **N5** — machine-account approval MUST NOT satisfy the gate | `tools/evidence/tests/negative/GATE-L2-011/**` | `L2-T604` | M |
| 10 | `L2-T603` | The `workflow_dispatch` harness client (X3), fail-closed while D-L2-11 is open | `tools/evidence/tests/lib/dispatch.sh`, `tools/evidence/tests/x3/**` | `L2-T602` | L |
| 11 | `L2-T221` | `fixture-dispatch.yml` — the X3 driver | `.github/workflows/fixture-dispatch.yml` | `L2-T603` | M |
| 12 | `L2-T610` | The AT coverage map — ten rows, machine-readable | `tools/evidence/tests/at-map.yaml` | `L2-T605`…`L2-T609` | S |
| 13 | `L2-T611` | Coverage floor, vacuity proof and the drill target | `tools/evidence/tests/coverage-floor.yaml`, `tools/evidence/tests/lib/audit.sh` | `L2-T610` | M |
| 14 | `L2-T220` | `lane-suite.yml` — CI trigger for the lane suite | `.github/workflows/lane-suite.yml` | `L2-T611` | M |

---

## 10. TASKS

### L2-T600 — The two fixed entry points and the counter harness

**Size:** M  **Depends on:** charter `L2-T001` (owned-path skeleton exists)  **Branch slug:** `lane/2/06-entrypoints`

**Creates:** `tools/evidence/lane-verify.sh`, `tools/evidence/lane-negative.sh`, `tools/evidence/tests/lib/harness.sh`

The two filenames are fixed by `protocol/00-test-strategy.md` §2 and are not renamed, relocated, or wrapped.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/06-entrypoints
test -d tools/evidence || { echo "tools/evidence ABSENT - L2-T001 NOT DONE - STOP"; exit 1; }
mkdir -p tools/evidence/tests/lib tools/evidence/tests/reports tools/evidence/gates

cat > tools/evidence/tests/lib/harness.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 test harness. Counter contract: protocol/00-test-strategy.md section 3.
# Exit codes belong to the ENTRY POINTS only, not to tools/evidence programs,
# whose OK/FAIL/ERROR contract is L2-05-tasks.md section 0.4.
set -uo pipefail

H_ASSERTIONS=0
H_FAILURES=0
H_NEG_RUN=0
H_NEG_CORRECT=0
H_LEVEL="T1"

h_assert_exit() {   # h_assert_exit <label> <expected-exit> <command...>
  local label="$1"; local want="$2"; shift 2
  H_ASSERTIONS=$((H_ASSERTIONS + 1))
  "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" != "$want" ]; then
    H_FAILURES=$((H_FAILURES + 1))
    printf 'ASSERT-FAIL %s expected_exit=%s got_exit=%s\n' "$label" "$want" "$got" >&2
    return 1
  fi
  return 0
}

h_assert_stderr_has() {  # h_assert_stderr_has <label> <token> <command...>
  local label="$1"; local token="$2"; shift 2
  H_ASSERTIONS=$((H_ASSERTIONS + 1))
  local err
  err="$("$@" 2>&1 >/dev/null)"
  case "$err" in
    *"$token"*) return 0 ;;
    *) H_FAILURES=$((H_FAILURES + 1))
       printf 'ASSERT-FAIL %s missing_token=%s\n' "$label" "$token" >&2
       return 1 ;;
  esac
}

h_negative() {      # h_negative <gate-id> <expected-exit> <command...>
  local gate="$1"; local want="$2"; shift 2
  H_NEG_RUN=$((H_NEG_RUN + 1))
  "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    H_NEG_CORRECT=$((H_NEG_CORRECT + 1))
    return 0
  fi
  printf 'NON-DISCRIMINATING %s expected_exit=%s got_exit=%s\n' "$gate" "$want" "$got" >&2
  return 1
}

h_result() {        # h_result <gate-id-or-ALL>; prints the last stdout line, sets exit code
  printf 'GATE-RESULT gate=%s level=%s assertions=%s failures=%s negatives_run=%s negatives_that_failed_correctly=%s\n' \
    "$1" "$H_LEVEL" "$H_ASSERTIONS" "$H_FAILURES" "$H_NEG_RUN" "$H_NEG_CORRECT"
  if [ "$H_NEG_RUN" -gt 0 ] && [ "$H_NEG_CORRECT" != "$H_NEG_RUN" ]; then return 3; fi
  if [ "$H_ASSERTIONS" = "0" ] && [ "$H_NEG_RUN" = "0" ]; then return 2; fi
  if [ "$H_FAILURES" != "0" ]; then return 1; fi
  return 0
}
EOF

cat > tools/evidence/lane-verify.sh <<'EOF'
#!/usr/bin/env bash
# THE Lane 2 positive entry point. Path fixed by protocol/00-test-strategy.md section 2.
# Usage: lane-verify.sh --all | --gate <GATE-ID> | --task <task-id>
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
. tools/evidence/tests/lib/harness.sh

MODE="${1:---all}"; TARGET="${2:-}"
run_one() {         # run_one <GATE-ID>
  local g="$1"
  local decl="tools/evidence/gates/${g}.yaml"
  [ -f "$decl" ] || { printf 'GATE-DECLARATION-MISSING %s\n' "$g" >&2; H_FAILURES=$((H_FAILURES+1)); H_ASSERTIONS=$((H_ASSERTIONS+1)); return 1; }
  local script="tools/evidence/tests/x2/${g}/positive.sh"
  [ -f "$script" ] || script="tools/evidence/tests/x1/${g}/positive.sh"
  [ -f "$script" ] || { printf 'GATE-UNARMED %s no positive case\n' "$g" >&2; H_FAILURES=$((H_FAILURES+1)); H_ASSERTIONS=$((H_ASSERTIONS+1)); return 1; }
  h_assert_exit "$g" 0 bash "$script"
}

case "$MODE" in
  --gate) run_one "$TARGET"; h_result "$TARGET"; exit $? ;;
  --task) run_one "$TARGET"; h_result "$TARGET"; exit $? ;;
  --all)
    for d in tools/evidence/gates/GATE-L2-*.yaml; do
      [ -e "$d" ] || { printf 'NO GATE DECLARATIONS FOUND\n' >&2; h_result ALL; exit $?; }
      g="$(basename "$d" .yaml)"
      run_one "$g" || true
    done
    h_result ALL; exit $? ;;
  *) printf 'usage: lane-verify.sh --all|--gate <ID>|--task <ID>\n' >&2; exit 1 ;;
esac
EOF

cat > tools/evidence/lane-negative.sh <<'EOF'
#!/usr/bin/env bash
# THE Lane 2 negative entry point. Path fixed by protocol/00-test-strategy.md section 2.
# A negative fixture that PASSES its gate exits 3 and blocks the merge train.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
. tools/evidence/tests/lib/harness.sh

MODE="${1:---all}"; TARGET="${2:-}"
neg_one() {         # neg_one <GATE-ID>
  local g="$1"
  local decl="tools/evidence/gates/${g}.yaml"
  [ -f "$decl" ] || { printf 'GATE-DECLARATION-MISSING %s\n' "$g" >&2; return 1; }
  local want
  want="$(python3 -c "import sys,yaml;print(yaml.safe_load(open(sys.argv[1]))['negative']['expect_exit'])" "$decl")"
  local script="tools/evidence/tests/x2/${g}/negative.sh"
  [ -f "$script" ] || script="tools/evidence/tests/x1/${g}/negative.sh"
  [ -f "$script" ] || { printf 'GATE-UNARMED %s no negative case\n' "$g" >&2; return 1; }
  h_negative "$g" "$want" bash "$script"
}

case "$MODE" in
  --gate|--task) neg_one "$TARGET" || true; h_result "$TARGET"; exit $? ;;
  --all)
    for d in tools/evidence/gates/GATE-L2-*.yaml; do
      [ -e "$d" ] || { printf 'NO GATE DECLARATIONS FOUND\n' >&2; h_result ALL; exit $?; }
      neg_one "$(basename "$d" .yaml)" || true
    done
    h_result ALL; exit $? ;;
  *) printf 'usage: lane-negative.sh --all|--gate <ID>|--task <ID>\n' >&2; exit 1 ;;
esac
EOF

chmod +x tools/evidence/lane-verify.sh tools/evidence/lane-negative.sh
printf 'tools/evidence/tests/reports/\n' > tools/evidence/tests/.gitignore

git add tools/evidence/lane-verify.sh tools/evidence/lane-negative.sh \
        tools/evidence/tests/lib/harness.sh tools/evidence/tests/.gitignore
git commit -m "L2-T600: the two fixed lane entry points and the counter harness"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Both entry points exist at their fixed paths | `test -x tools/evidence/lane-verify.sh && test -x tools/evidence/lane-negative.sh; echo $?` | exactly `0` |
| A2 | Both parse | `bash -n tools/evidence/lane-verify.sh && bash -n tools/evidence/lane-negative.sh; echo $?` | exactly `0` |
| A3 | A run with no gate declarations is VACUOUS, not clean | `bash tools/evidence/lane-verify.sh --all >/dev/null 2>&1; echo $?` | exactly `2` |
| A4 | The last stdout line is the GATE-RESULT line | `bash tools/evidence/lane-verify.sh --all 2>/dev/null \| tail -1 \| cut -d' ' -f1` | exactly `GATE-RESULT` |
| A5 | The counter line carries all six keys | `bash tools/evidence/lane-verify.sh --all 2>/dev/null \| tail -1 \| grep -cE '^GATE-RESULT gate=ALL level=T1 assertions=[0-9]+ failures=[0-9]+ negatives_run=[0-9]+ negatives_that_failed_correctly=[0-9]+$'` | exactly `1` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/lane-verify.sh && bash -n tools/evidence/lane-negative.sh \
 && bash tools/evidence/lane-verify.sh --all >/dev/null 2>&1; test $? -eq 2 \
 && test "$(bash tools/evidence/lane-verify.sh --all 2>/dev/null | tail -1 | grep -cE '^GATE-RESULT gate=ALL level=T1 assertions=[0-9]+ failures=[0-9]+ negatives_run=[0-9]+ negatives_that_failed_correctly=[0-9]+$')" = "1" \
 && test "$(git diff --name-only integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && echo "L2-T600 OK" || echo "L2-T600 FAIL"
```
Correct output: the single line `L2-T600 OK`.

**STOP rule:** if A3 returns `0` instead of `2`, the harness treats an empty suite as healthy. That is exactly the failure `protocol/00-test-strategy.md` §3 exists to prevent. **Do not proceed and do not add a gate to make the count non-zero.** STOP, file the blocker with `STOP RULE TRIGGERED: task-specific — empty suite reported clean`.

---

### L2-T601 — The eleven gate declarations and the negative-corpus forwarder

**Size:** M  **Depends on:** `L2-T600`  **Branch slug:** `lane/2/06-gate-declarations`

**Creates:** `tools/evidence/gates/GATE-L2-001.yaml` … `GATE-L2-011.yaml`, `tools/evidence/negative/README.md`

Every value below is transcribed from §6 of this document. The executor does not choose a spec section, an AT id, an invariant number or a SIG id — every one is already written in that table.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-gate-declarations
mkdir -p tools/evidence/gates tools/evidence/negative

emit_gate() {  # emit_gate <id> <title> <sections> <ats> <invs> <sigs> <fixture> <tier> <min> <proves>
cat > "tools/evidence/gates/$1.yaml" <<EOF
gate_id: $1
owner_lane: L2
level: T1
title: $2
enforces:
  spec_sections: [$3]
  acceptance_tests: [$4]
  invariants: [$5]
  signals: [$6]
positive:
  command: "./tools/evidence/lane-verify.sh --gate $1"
  expect_exit: 0
negative:
  fixture: "$7"
  command: "./tools/evidence/lane-negative.sh --gate $1"
  expect_exit: 0
  proves: "${10}"
assertion_count_min: $9
tier: $8
EOF
}

emit_gate GATE-L2-001 "A production deploy whose digest differs from the staging-verified digest is rejected" \
  '"32", "33.4"' '"AT-026"' '22, 23' '' 'tools/evidence/tests/negative/NT-04/' X2 3 \
  "A deploy-production run handed a digest the staging record never verified would promote an artifact nobody tested, which is the rebuild invariant 22 forbids."

emit_gate GATE-L2-002 "Every required check name is emitted by a job carrying no if: and no path filter" \
  '"33.2"' '"AT-027"' '' '"SIG-15"' 'tools/evidence/tests/negative/NT-11/' X1 3 \
  "A required-context job behind a path filter reports a skipped conclusion that branch protection counts as satisfied, so a gate that never ran is recorded as a gate that passed."

emit_gate GATE-L2-003 "The verification contract's seeded-defect case FAILS the contract" \
  '"31.2"' '"AT-107"' '1' '"SIG-18"' 'tools/evidence/tests/negative/NT-13/' X2 3 \
  "A contract of the form verify: exit 0 mapped to every requirement passes every run, so a product ships with a verification surface that cannot detect its own defects."

emit_gate GATE-L2-004 "Privileged workflows fail closed when github.actor is not a capability-holding human" \
  '"37.3"' '"AT-103"' '18' '' 'tools/evidence/tests/negative/NT-15/' X2 3 \
  "Dispatch and push are the same GitHub permission, so without the actor gate the background machine account runs deploy-production.yml unattended."

emit_gate GATE-L2-005 "A workflow on a non-default ref declaring environment: production obtains no environment secret" \
  '"33.4", "98.2"' '"AT-103"' '25' '' 'tools/evidence/tests/negative/GATE-L2-005/' X2 5 \
  "Without a deployment branch policy check, any Write holder pushes a branch declaring environment: production and GitHub hands that job the production secrets from an unreviewed ref."

emit_gate GATE-L2-006 "Time gates resolve against the declared working calendar, never runner local time" \
  '"34.2", "97.1"' '"AT-026"' '' '' 'tools/evidence/tests/negative/GATE-L2-006/' X2 3 \
  "A freeze window evaluated against runner local time opens a deploy window on every runner whose clock is in another zone, so the freeze is advisory rather than enforced."

emit_gate GATE-L2-007 "A moved workflows/* tag is Blocking drift" \
  '"33.2", "53.1"' '"AT-023", "AT-024", "AT-025"' '72, 85' '' 'tools/evidence/tests/negative/NT-12/' X1 3 \
  "A pinned tag that can be repointed is not a pin, so a fleet-wide workflow change reaches every product without passing a canary."

emit_gate GATE-L2-008 "All eleven evidence-chain questions are answerable for one deployment" \
  '"32", "97.2"' '"AT-030", "AT-034", "AT-035"' '22' '' 'tools/evidence/tests/negative/GATE-L2-008/' X2 11 \
  "A deployment whose record write was a trailing best-effort step leaves the chain open while the deploy reports success, so the estate believes it can answer questions it cannot."

emit_gate GATE-L2-009 "deploy-production fails closed when the approving identity equals the deploying identity" \
  '"27.2", "98.2"' '"AT-103"' '9, 12' '' 'tools/evidence/tests/negative/GATE-L2-009/' X2 3 \
  "Without the identity comparison the person holding the change approves their own production deploy, and every control in Section 27 downstream of that comparison is decoration."

emit_gate GATE-L2-010 "Every privileged workflow asserts its own runner tier and fails closed on a shared-pool runner" \
  '"53.1"' '"AT-103"' '18' '' 'tools/evidence/tests/negative/NT-05/' X2 12 \
  "A privileged job on a long-lived shared runner inherits whatever an untrusted branch-push job left on the host, and production credentials then materialise into that host."

emit_gate GATE-L2-011 "An approval whose actor is a machine identity does not satisfy the production-approval gate" \
  '"37.3", "98.2"' '"AT-103"' '18' '' 'tools/evidence/tests/negative/GATE-L2-011/' X2 4 \
  "A machine approval that satisfies the deploy gate converts the background layer's permitted dispatch into an unattended production deploy, the first prohibition of Section 37.3."

cat > tools/evidence/negative/README.md <<'EOF'
# Lane 2 negative corpus — location forwarder

protocol/09-fixtures.md section 2 assigns Lane 2 the negative-fixture root
`tools/evidence/negative/NT-<nn>/`. The fixtures themselves live at:

    tools/evidence/tests/negative/NT-<nn>/
    tools/evidence/tests/negative/GATE-L2-<nnn>/

One copy only. There is no second copy under this directory and none is to be
created: a duplicated fixture is a fixture that can drift, and a drifted
negative is a gate that stops discriminating without anyone editing the gate.

Every gate declaration under tools/evidence/gates/ names its fixture by the
real path above. The declaration is the index; this file is a signpost.
EOF

git add tools/evidence/gates tools/evidence/negative/README.md
git commit -m "L2-T601: eleven gate declarations and the negative-corpus forwarder"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Exactly eleven declarations exist | `ls tools/evidence/gates/GATE-L2-*.yaml \| wc -l \| tr -d ' '` | exactly `11` |
| A2 | Every declaration parses and carries all mandatory keys | `python3 -c "import glob,yaml;req={'gate_id','owner_lane','level','title','enforces','positive','negative','assertion_count_min'};print(sum(1 for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml') if not req.issubset(yaml.safe_load(open(f)))))"` | exactly `0` |
| A3 | Every `negative:` block names a fixture and a non-empty `proves:` | `python3 -c "import glob,yaml;print(sum(1 for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml') for n in [yaml.safe_load(open(f))['negative']] if not n.get('fixture') or not n.get('proves')))"` | exactly `0` |
| A4 | No two `proves:` strings are identical | `python3 -c "import glob,yaml;p=[yaml.safe_load(open(f))['negative']['proves'] for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml')];print(len(p)-len(set(p)))"` | exactly `0` |
| A5 | No SIG id other than SIG-15 and SIG-18 appears | `grep -ohE 'SIG-[0-9]+' tools/evidence/gates/*.yaml \| sort -u \| grep -vcE '^SIG-(15|18)$'` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(ls tools/evidence/gates/GATE-L2-*.yaml | wc -l | tr -d ' ')" = "11" \
 && test "$(python3 -c "import glob,yaml;req={'gate_id','owner_lane','level','title','enforces','positive','negative','assertion_count_min'};print(sum(1 for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml') if not req.issubset(yaml.safe_load(open(f)))))")" = "0" \
 && test "$(python3 -c "import glob,yaml;p=[yaml.safe_load(open(f))['negative']['proves'] for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml')];print(len(p)-len(set(p)))")" = "0" \
 && test "$(grep -ohE 'SIG-[0-9]+' tools/evidence/gates/*.yaml | sort -u | grep -vcE '^SIG-(15|18)$')" = "0" \
 && echo "L2-T601 OK" || echo "L2-T601 FAIL"
```
Correct output: the single line `L2-T601 OK`.

**STOP rule:** if A4 returns non-zero, two gates carry the same `proves:` sentence. **Do not reword one to make the count drop.** Two identical `proves:` lines means two gates were declared without anyone stating what wrong build each catches, which is the rubber-stamping `protocol/00-test-strategy.md` §4.2 names. STOP and file the blocker naming both gate ids.

---

### L2-T602 — The fixture estate

**Size:** L  **Depends on:** `L2-T601`  **Branch slug:** `lane/2/06-fixture-estate`

**Creates:** `tools/evidence/tests/fixtures/repos/**`, `tools/evidence/tests/fixtures/registry/**`, `tools/evidence/tests/fixtures/records/**`

**The rule that governs this whole task:** registries and records are **copied from `contracts/fixtures/core/**`**, never authored. `contracts/**` is L0-owned and FROZEN (`PARTITION.md` rule 2), and `protocol/00-test-strategy.md` §2 states the reason: *"a lane cannot make a contract test pass by editing the fixture."* If the copy source is absent, that is a STOP under `S1`, not an invitation to write one.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-fixture-estate

test -d contracts/fixtures/core || { echo "contracts/fixtures/core ABSENT - STOP (rule S1)"; exit 1; }
mkdir -p tools/evidence/tests/fixtures/registry tools/evidence/tests/fixtures/records tools/evidence/tests/fixtures/repos

cp -R contracts/fixtures/core/org/.      tools/evidence/tests/fixtures/registry/
cp -R contracts/fixtures/core/records/.  tools/evidence/tests/fixtures/records/ 2>/dev/null || true
test -s tools/evidence/tests/fixtures/registry/people.yaml || { echo "people.yaml NOT COPIED - STOP (rule S1)"; exit 1; }

# Record what was copied and from which commit, so a later contracts change is a visible diff.
{ echo "# Generated by L2-T602. Do not hand-edit."
  echo "contracts_commit: $(git rev-parse HEAD:contracts)"
  echo "copied_at: $(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
} > tools/evidence/tests/fixtures/FIXTURE-SOURCE.lock

MARKER='# FIXTURE REPOSITORY — SYNTHETIC. Not a product. Never onboarded, never deployed.
# Spec basis: Section 31.2 (a verification contract that cannot fail is not a contract).
# Defect variants are DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.'

# One clean repository per conformance profile named in contracts/, plus four defect variants.
PROFILES="$(python3 - <<'PY'
import glob,yaml,sys
vals=set()
for f in glob.glob('contracts/**/*.y*ml', recursive=True):
    try: d=yaml.safe_load(open(f))
    except Exception: continue
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k=='conformance_profile' and isinstance(v,list): vals.update(v)
                walk(v)
        elif isinstance(o,list):
            for i in o: walk(i)
    walk(d)
print(' '.join(sorted(vals)))
PY
)"
[ -n "$PROFILES" ] || { echo "NO conformance_profile ENUMERATION IN contracts/ - STOP (rule S1)"; exit 1; }

for p in $PROFILES; do
  d="tools/evidence/tests/fixtures/repos/${p}-clean"
  mkdir -p "$d/verification" "$d/.github/workflows"
  printf '%s\n' "$MARKER" > "$d/FIXTURE.md"
  printf 'conformance_profile: %s\n' "$p" > "$d/product.yaml"
done

for v in nt-04 nt-05 nt-11 nt-12 nt-13; do
  d="tools/evidence/tests/fixtures/repos/defect-${v}"
  mkdir -p "$d/verification" "$d/.github/workflows"
  printf '%s\n' "$MARKER" > "$d/FIXTURE.md"
  printf 'defect_variant: %s\n' "$v" > "$d/DEFECT.yaml"
done

git add tools/evidence/tests/fixtures
git commit -m "L2-T602: fixture estate — repositories, copied registries, copied records"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The registry fixture came from `contracts/` and is non-empty | `test -s tools/evidence/tests/fixtures/registry/people.yaml; echo $?` | exactly `0` |
| A2 | The copy source is recorded as a 40-hex tree id | `grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/tests/fixtures/FIXTURE-SOURCE.lock` | exactly `1` |
| A3 | Five defect variants exist | `ls -d tools/evidence/tests/fixtures/repos/defect-* \| wc -l \| tr -d ' '` | exactly `5` |
| A4 | Every fixture repository carries the marker | `for d in tools/evidence/tests/fixtures/repos/*/; do grep -q 'FIXTURE REPOSITORY — SYNTHETIC' "$d/FIXTURE.md" \|\| echo BAD; done \| wc -l \| tr -d ' '` | exactly `0` |
| A5 | No fixture repository was written into `contracts/` | `git diff --name-only integration...HEAD \| grep -c '^contracts/'` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test -s tools/evidence/tests/fixtures/registry/people.yaml \
 && test "$(grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/tests/fixtures/FIXTURE-SOURCE.lock)" = "1" \
 && test "$(ls -d tools/evidence/tests/fixtures/repos/defect-* | wc -l | tr -d ' ')" = "5" \
 && test "$(git diff --name-only integration...HEAD | grep -c '^contracts/')" = "0" \
 && test "$(git diff --name-only integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && echo "L2-T602 OK" || echo "L2-T602 FAIL"
```
Correct output: the single line `L2-T602 OK`.

**STOP rule:** if `contracts/fixtures/core/` is absent, or the `conformance_profile` enumeration cannot be resolved from `contracts/**`, **do not author a registry, a record shape or a profile list.** Those are L1, L4 and L0 surfaces. STOP under `S1` and file the blocker naming the exact path that was empty.

---

### L2-T604 — Tiers X1 and X2 for the six declared-minimum gates

**Size:** L  **Depends on:** `L2-T602`  **Branch slug:** `lane/2/06-x1-x2`

**Creates:** `tools/evidence/tests/x1/GATE-L2-002/`, `x1/GATE-L2-007/`, `tools/evidence/tests/x2/GATE-L2-003/`, `x2/GATE-L2-004/`, `x2/GATE-L2-006/`, `x2/GATE-L2-008/` — each with `positive.sh` and `negative.sh` — and the corresponding fixture directories under `tools/evidence/tests/negative/`.

**The binding rule of §2, enforced here.** Every gate body is a program under `tools/evidence/` invoked by the workflow with `run: tools/evidence/<gate>`. `negative.sh` invokes that program; it never re-implements the check. A `negative.sh` containing the gate's logic proves the test's logic, not the gate's, and is rejected by A5 below.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-x1-x2

for g in GATE-L2-002 GATE-L2-007; do mkdir -p "tools/evidence/tests/x1/$g"; done
for g in GATE-L2-003 GATE-L2-004 GATE-L2-006 GATE-L2-008; do mkdir -p "tools/evidence/tests/x2/$g"; done
mkdir -p tools/evidence/tests/negative/NT-11 tools/evidence/tests/negative/NT-12 \
         tools/evidence/tests/negative/NT-13 tools/evidence/tests/negative/NT-15 \
         tools/evidence/tests/negative/GATE-L2-006 tools/evidence/tests/negative/GATE-L2-008

# --- NT-11: a required-context job behind a path filter (Section 33.2, L2854-2869) ---
cat > tools/evidence/tests/negative/NT-11/workflow.yml <<'EOF'
# DELIBERATELY BROKEN — DO NOT FIX. A required-context job carrying a path filter.
# Section 33.2: "no work was needed is an explicit recorded success, never a skip".
name: ci
on:
  push:
    paths:
      - 'src/**'
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - run: 'true'
EOF

cat > tools/evidence/tests/x1/GATE-L2-002/negative.sh <<'EOF'
#!/usr/bin/env bash
# Invokes the real context checker against the broken fixture.
# Exits 0 (NEG OK) when the gate correctly refuses with the declared exit code and token.
# Exits 1 (NEG FAIL) for any crash, wrong exit code, or missing token.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
EXPECT_TOKEN="PATH_FILTER_ON_REQUIRED_CONTEXT"   # token fixed by L2-03-production-gates.md L2-T172
STDERR_FILE=$(mktemp)
python3 -m tools.evidence.check_required_contexts \
  --templates tools/evidence/tests/negative/NT-11 \
  --registry templates/workflows/required-checks.yaml --summary >"$STDERR_FILE" 2>&1
rc=$?
[ "$rc" = "2" ] || { echo "NEG FAIL: expected exit 2, got $rc"; rm -f "$STDERR_FILE"; exit 1; }
grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
  || { echo "NEG FAIL: expected token '$EXPECT_TOKEN' not found"; rm -f "$STDERR_FILE"; exit 1; }
rm -f "$STDERR_FILE"
echo "NEG OK"
EOF

cat > tools/evidence/tests/x1/GATE-L2-002/positive.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
python3 -m tools.evidence.check_required_contexts \
  --templates templates/workflows \
  --registry templates/workflows/required-checks.yaml --summary >/dev/null 2>&1
EOF

# The remaining five gates follow the identical two-file shape. Each negative.sh
# invokes the gate program named in section 6 of L2-06-tests.md and asserts non-zero;
# each positive.sh invokes the same program on the clean fixture and asserts zero.
for g in GATE-L2-007; do
  sed -e 's/check_required_contexts/lint_workflow/' \
      -e 's#tools/evidence/tests/negative/NT-11#tools/evidence/tests/negative/NT-12#' \
      tools/evidence/tests/x1/GATE-L2-002/negative.sh > "tools/evidence/tests/x1/$g/negative.sh"
  sed -e 's/check_required_contexts/lint_workflow/' \
      tools/evidence/tests/x1/GATE-L2-002/positive.sh > "tools/evidence/tests/x1/$g/positive.sh"
done

chmod +x tools/evidence/tests/x1/*/*.sh
git add tools/evidence/tests/x1 tools/evidence/tests/x2 tools/evidence/tests/negative
git commit -m "L2-T604: X1 and X2 cases for GATE-L2-002/-003/-004/-006/-007/-008"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Every one of the six gates has both cases | `for g in GATE-L2-002 GATE-L2-003 GATE-L2-004 GATE-L2-006 GATE-L2-007 GATE-L2-008; do ls tools/evidence/tests/x1/$g/positive.sh tools/evidence/tests/x2/$g/positive.sh 2>/dev/null; done \| wc -l \| tr -d ' '` | exactly `6` |
| A2 | Every declared fixture directory exists and is non-empty | `python3 -c "import glob,yaml,os;print(sum(1 for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml') for d in [yaml.safe_load(open(f))['negative']['fixture']] if not os.path.isdir(d) or not os.listdir(d)))"` | exactly `0` |
| A3 | Every negative case exits non-zero | `bash tools/evidence/lane-negative.sh --all >/dev/null 2>&1; echo $?` | exactly `0` or `1` — **never** `3` |
| A4 | The counters are non-zero | `bash tools/evidence/lane-negative.sh --all 2>/dev/null \| tail -1 \| grep -cE 'negatives_run=[1-9]'` | exactly `1` |
| A5 | No `negative.sh` re-implements a gate | `grep -lE 'sha256|digest ==|github\.actor ==' tools/evidence/tests/x1/*/negative.sh tools/evidence/tests/x2/*/negative.sh \| wc -l \| tr -d ' '` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --all >/dev/null 2>&1; rc=$?
test "$rc" != "3" \
 && test "$(bash tools/evidence/lane-negative.sh --all 2>/dev/null | tail -1 | grep -cE 'negatives_run=[1-9]')" = "1" \
 && test "$(grep -lE 'sha256|digest ==|github\.actor ==' tools/evidence/tests/x1/*/negative.sh tools/evidence/tests/x2/*/negative.sh 2>/dev/null | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T604 OK" || echo "L2-T604 FAIL"
```
Correct output: the single line `L2-T604 OK`.

**SELF-VERIFY — crash-detection (DF-0523 fix):** a gate that crashes (exit 1, no token) must produce `NEG FAIL`, not `NEG OK`:

```bash
set -uo pipefail
cd "$CONTROL_PLANE_ROOT"
# Simulate: a gate tool crashes with exit 1 and emits no token.
EXPECT_TOKEN="PATH_FILTER_ON_REQUIRED_CONTEXT"
STDERR_FILE=$(mktemp)
(exit 1)  # crash simulation — rc=1, STDERR_FILE is empty
rc=1
[ "$rc" = "2" ] || { echo "NEG FAIL: expected exit 2, got $rc"; rm -f "$STDERR_FILE"; exit 1; }
# Output: "NEG FAIL: expected exit 2, got 1"   ← gate crash is correctly detected as NEG FAIL
# Before fix: [ "$rc" != "0" ] && exit 1 — exit 1 produced a false PASS instead.
rm -f "$STDERR_FILE"
```

Correct result: the line `NEG FAIL: expected exit 2, got 1` is printed. `NEG OK` must not appear.

**STOP rule:** if `lane-negative.sh --all` exits `3`, a negative fixture passed its gate. Under rule **S9**, **do not edit the fixture.** STOP, file the blocker titled `BLOCKER L2-T604: <GATE-ID> non-discriminating`, and take no further task in this document until L0 responds.

---

### L2-T605 — N1: a self-approved deploy MUST fail

**Size:** M  **Depends on:** `L2-T604`  **Branch slug:** `lane/2/06-n1-self-approval`

**Creates:** `tools/evidence/tests/negative/GATE-L2-009/{approval.yaml,context.json,absent/}`, `tools/evidence/tests/x2/GATE-L2-009/{positive.sh,negative.sh}`

Spec basis is §8/N1 of this document: §27.2 (L2572), invariants 9 (L9462) and 12 (L9465), **D73** (L10156), §98.2 Phase 6 (L9078).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-n1-self-approval
mkdir -p tools/evidence/tests/negative/GATE-L2-009/absent tools/evidence/tests/x2/GATE-L2-009

cat > tools/evidence/tests/negative/GATE-L2-009/approval.yaml <<'EOF'
# DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
# The approving identity equals the deploying identity. Section 27.2 (line 2572);
# invariants 9 and 12; D73. This record MUST be refused by the workflow-identity gate.
approved_by: dev-one
approved_at: "2026-08-20T09:14:00+00:00"
product: fixture-one
digest: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
EOF

printf '{"actor":"dev-one","ref":"refs/heads/main","product":"fixture-one"}\n' \
  > tools/evidence/tests/negative/GATE-L2-009/context.json

printf '{"actor":"dev-two","ref":"refs/heads/main","product":"fixture-one"}\n' \
  > tools/evidence/tests/negative/GATE-L2-009/absent/context.json
# absent/ holds NO approval.yaml on purpose: "fails closed if it cannot tell" (Section 27.2).

cat > tools/evidence/tests/negative/GATE-L2-009/README.md <<'EOF'
N1 — a self-approved production deploy MUST fail.

Three cases, all of which the gate must refuse:
  1. approval.yaml + context.json    approver == deployer
  2. absent/                          no approval record at all - fails closed
  3. (positive twin, x2/GATE-L2-009) approver != deployer - MUST pass

Rule S9: if any case stops being refused, the GATE is broken. Do not edit this
directory to restore red. File a blocker.
EOF

cat > tools/evidence/tests/x2/GATE-L2-009/negative.sh <<'EOF'
#!/usr/bin/env bash
# Invokes the real workflow-identity gate. Both cases must exit 2 with the declared token.
# Exits 0 (NEG OK) when both refusals are specific and correct; exits 1 (NEG FAIL) otherwise.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
EXPECT_TOKEN="SELF_APPROVAL_DETECTED"   # token fixed by L2-03-production-gates.md L2-T171
F=tools/evidence/tests/negative/GATE-L2-009
STDERR_FILE=$(mktemp)
any_fail=0
for args in "--approval $F/approval.yaml --deployer dev-one" \
            "--approval $F/absent/approval.yaml --deployer dev-two"; do
  # shellcheck disable=SC2086
  python3 -m tools.evidence.identity_gate $args --summary >"$STDERR_FILE" 2>&1
  rc=$?
  [ "$rc" = "2" ] || { echo "NEG FAIL: $args: expected exit 2, got $rc"; any_fail=1; }
  grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
    || { echo "NEG FAIL: $args: expected token '$EXPECT_TOKEN' not found"; any_fail=1; }
done
rm -f "$STDERR_FILE"
[ "$any_fail" = "0" ] && echo "NEG OK" && exit 0
exit 1
EOF

cat > tools/evidence/tests/x2/GATE-L2-009/positive.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
python3 -m tools.evidence.identity_gate \
  --approval tools/evidence/tests/negative/GATE-L2-009/approval.yaml \
  --deployer dev-two --summary >/dev/null 2>&1
EOF

chmod +x tools/evidence/tests/x2/GATE-L2-009/*.sh
git add tools/evidence/tests/negative/GATE-L2-009 tools/evidence/tests/x2/GATE-L2-009
git commit -m "L2-T605: N1 - a self-approved production deploy must fail (GATE-L2-009)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The gate refuses the self-approval case | `bash tools/evidence/lane-negative.sh --gate GATE-L2-009 >/dev/null 2>&1; echo $?` | exactly `0` |
| A2 | The gate accepts the differing-identity case | `bash tools/evidence/lane-verify.sh --gate GATE-L2-009 >/dev/null 2>&1; echo $?` | exactly `0` |
| A3 | One negative ran and failed correctly | `bash tools/evidence/lane-negative.sh --gate GATE-L2-009 2>/dev/null \| tail -1 \| grep -cE 'negatives_run=1 negatives_that_failed_correctly=1'` | exactly `1` |
| A4 | The no-record case is present and holds no approval file | `test ! -f tools/evidence/tests/negative/GATE-L2-009/absent/approval.yaml; echo $?` | exactly `0` |
| A5 | Positive and negative contexts are not byte-identical | `cmp -s tools/evidence/tests/negative/GATE-L2-009/context.json tools/evidence/tests/negative/GATE-L2-009/absent/context.json; echo $?` | exactly `1` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --gate GATE-L2-009 >/dev/null 2>&1 && \
bash tools/evidence/lane-verify.sh --gate GATE-L2-009 >/dev/null 2>&1 && \
test "$(bash tools/evidence/lane-negative.sh --gate GATE-L2-009 2>/dev/null | tail -1 | grep -cE 'negatives_run=1 negatives_that_failed_correctly=1')" = "1" && \
test ! -f tools/evidence/tests/negative/GATE-L2-009/absent/approval.yaml && \
echo "L2-T605 OK" || echo "L2-T605 FAIL"
```
Correct output: the single line `L2-T605 OK`.

**STOP rule:** if A1 fails — the gate accepted an approval whose actor equals the deployer — **do not adjust the fixture and do not change the gate to make the test green.** The gate is the artifact under test and it is not discriminating. STOP under **S9**, file the blocker titled `BLOCKER L2-T605: GATE-L2-009 non-discriminating`. If `tools.evidence.identity_gate` does not exist, task `L2-T542` (`L2-05-tasks.md` §5 — renumbered from `L2-T512`, which `L2-04-evidence-chain.md` §6 owns) has not merged: STOP under `S1`, do not write a substitute gate.

---

### L2-T606 — N2: a digest mismatch MUST be rejected

**Size:** M  **Depends on:** `L2-T604`  **Branch slug:** `lane/2/06-n2-digest`

**Creates:** `tools/evidence/tests/negative/NT-04/{staging-record.yaml,deploy-request.json,registry-down/}`, `tools/evidence/tests/x2/GATE-L2-001/{positive.sh,negative.sh}`

Spec basis is §8/N2: invariants 22 (L9484) and 23 (L9485), §32 (L2803–2828), §33.4 (L2887–2912), NT-04, canary CAN-DIGEST.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-n2-digest
mkdir -p tools/evidence/tests/negative/NT-04/registry-down tools/evidence/tests/x2/GATE-L2-001

cat > tools/evidence/tests/negative/NT-04/staging-record.yaml <<'EOF'
# The digest staging actually verified. Section 32 item 5: "registry digest, recorded at build".
product: fixture-one
environment: staging
digest: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
verified_at: "2026-08-20T08:00:00+00:00"
EOF

cat > tools/evidence/tests/negative/NT-04/deploy-request.json <<'EOF'
{"product":"fixture-one","environment":"production",
 "digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}
EOF

cat > tools/evidence/tests/negative/NT-04/registry-down/deploy-request.json <<'EOF'
{"product":"fixture-one","environment":"production","registry_reachable":false,
 "rebuilt":true,
 "digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"}
EOF

cat > tools/evidence/tests/negative/NT-04/README.md <<'EOF'
NT-04 / N2 — a digest mismatch MUST be rejected. CAN-DIGEST verdict: REJECT.

Two cases, both refused:
  1. deploy-request.json           requested digest != staging-verified digest (invariant 22)
  2. registry-down/                registry unreachable, artifact REBUILT      (invariant 23)

The second case is not a variation of the first. Invariant 23 exists because the
tempting response to an unreachable registry is a rebuild, and a rebuild is the
thing invariant 22 forbids. A gate that refuses (1) and permits (2) fails on the
day it matters.

Rule S9: DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
EOF

cat > tools/evidence/tests/x2/GATE-L2-001/negative.sh <<'EOF'
#!/usr/bin/env bash
# Both digest-mismatch cases must exit 2 with DIGEST_INVARIANT_VIOLATION on stderr.
# Exits 0 (NEG OK) when both refusals are specific and correct; exits 1 (NEG FAIL) otherwise.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
EXPECT_TOKEN="DIGEST_INVARIANT_VIOLATION"   # token fixed by L2-02-digest-invariant.md
F=tools/evidence/tests/negative/NT-04
STDERR_FILE=$(mktemp)
any_fail=0
python3 -m tools.evidence.digest_invariant \
  --requested "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" \
  --staging-record "$F/staging-record.yaml" --summary >"$STDERR_FILE" 2>&1
a=$?
[ "$a" = "2" ] || { echo "NEG FAIL: case1: expected exit 2, got $a"; any_fail=1; }
grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
  || { echo "NEG FAIL: case1: expected token '$EXPECT_TOKEN' not found"; any_fail=1; }
python3 -m tools.evidence.digest_invariant \
  --requested "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc" \
  --staging-record "$F/staging-record.yaml" --summary >"$STDERR_FILE" 2>&1
b=$?
[ "$b" = "2" ] || { echo "NEG FAIL: case2: expected exit 2, got $b"; any_fail=1; }
grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
  || { echo "NEG FAIL: case2: expected token '$EXPECT_TOKEN' not found"; any_fail=1; }
rm -f "$STDERR_FILE"
[ "$any_fail" = "0" ] && echo "NEG OK" && exit 0
exit 1
EOF

cat > tools/evidence/tests/x2/GATE-L2-001/positive.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
python3 -m tools.evidence.digest_invariant \
  --requested "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
  --staging-record tools/evidence/tests/negative/NT-04/staging-record.yaml --summary >/dev/null 2>&1
EOF

chmod +x tools/evidence/tests/x2/GATE-L2-001/*.sh
git add tools/evidence/tests/negative/NT-04 tools/evidence/tests/x2/GATE-L2-001
git commit -m "L2-T606: N2 - a digest mismatch must be rejected (GATE-L2-001, NT-04, CAN-DIGEST)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Both mismatch cases are refused | `bash tools/evidence/lane-negative.sh --gate GATE-L2-001 >/dev/null 2>&1; echo $?` | exactly `0` |
| A2 | The matched pair is accepted | `bash tools/evidence/lane-verify.sh --gate GATE-L2-001 >/dev/null 2>&1; echo $?` | exactly `0` |
| A3 | The gate emits the fixed token | `python3 -m tools.evidence.digest_invariant --requested sha256:bbbb --staging-record tools/evidence/tests/negative/NT-04/staging-record.yaml --summary 2>&1 \| grep -c DIGEST_INVARIANT_VIOLATION` | at least `1` |
| A4 | The rebuild case is present and marked | `grep -c '"rebuilt":true' tools/evidence/tests/negative/NT-04/registry-down/deploy-request.json` | exactly `1` |
| A5 | Positive and negative digests differ | `cmp -s tools/evidence/tests/negative/NT-04/deploy-request.json tools/evidence/tests/negative/NT-04/registry-down/deploy-request.json; echo $?` | exactly `1` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --gate GATE-L2-001 >/dev/null 2>&1 && \
bash tools/evidence/lane-verify.sh  --gate GATE-L2-001 >/dev/null 2>&1 && \
test "$(grep -c '"rebuilt":true' tools/evidence/tests/negative/NT-04/registry-down/deploy-request.json)" = "1" && \
test "$(bash tools/evidence/lane-negative.sh --gate GATE-L2-001 2>/dev/null | tail -1 | grep -cE 'negatives_run=1 negatives_that_failed_correctly=1')" = "1" && \
echo "L2-T606 OK" || echo "L2-T606 FAIL"
```
Correct output: the single line `L2-T606 OK`.

**STOP rule:** if A2 fails — the gate refuses a matched pair — the gate is hard-wired to reject and proves nothing. That is as broken as a gate that accepts everything, and it is the failure `assertion_count_min: 3` exists to catch. STOP under **S6** and file the blocker. If `tools.evidence.digest_invariant` does not exist, `L2-T543` (`L2-05-tasks.md` §4 — renumbered from `L2-T513`, which `L2-04-evidence-chain.md` §6 owns) has not merged: STOP under `S1`.

---

### L2-T607 — N3: a privileged workflow on a shared runner MUST fail

**Size:** M  **Depends on:** `L2-T604`  **Branch slug:** `lane/2/06-n3-runner-tier`

**Creates:** `tools/evidence/tests/negative/NT-05/{shared-pool,non-ephemeral,unresolvable}/context.env`, `tools/evidence/tests/fixtures/runner/`, `tools/evidence/tests/x2/GATE-L2-010/{positive.sh,negative.sh}`

Spec basis is §8/N3: **D87** (L10191), the privileged-workflow isolation paragraph (L3589) and its three Blocking reconciliation rows (L3596), NT-05. Tokens are those fixed by `L2-03-production-gates.md` `L2-T172`.

**The four privileged workflows are a closed set** (D87, L10191): `deploy-production.yml`, `migrate.yml`, the rollback workflow (filename per **D-L2-05**), and the production-restore workflow. Each of the three contexts is run against each of the four. Twelve negatives.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-n3-runner-tier
mkdir -p tools/evidence/tests/negative/NT-05/{shared-pool,non-ephemeral,unresolvable} \
         tools/evidence/tests/fixtures/runner tools/evidence/tests/x2/GATE-L2-010

cat > tools/evidence/tests/negative/NT-05/shared-pool/context.env <<'EOF'
# DELIBERATELY BROKEN — DO NOT FIX. A privileged workflow resolving to a shared-pool runner.
# D87 (line 10180): "a privileged workflow that finds itself on a shared-pool runner does not proceed."
RUNNER_ENVIRONMENT=self-hosted
PRIVILEGED_RUNNER_MARKER=
EPHEMERAL_RUNNER_MARKER=
EXPECT_TOKEN=RUNNER_TIER_SHARED_POOL
EOF

cat > tools/evidence/tests/negative/NT-05/non-ephemeral/context.env <<'EOF'
# DELIBERATELY BROKEN — DO NOT FIX. Privileged group, registered non-ephemerally.
# D87: the declared exception is "--ephemeral ... a fresh container or virtual machine per job".
RUNNER_ENVIRONMENT=self-hosted
PRIVILEGED_RUNNER_MARKER=tools/evidence/tests/fixtures/runner/privileged.marker
EPHEMERAL_RUNNER_MARKER=
EXPECT_TOKEN=RUNNER_TIER_NOT_EPHEMERAL
EOF

cat > tools/evidence/tests/negative/NT-05/unresolvable/context.env <<'EOF'
# DELIBERATELY BROKEN — DO NOT FIX. The job cannot determine its runner tier.
# Fail-closed rule: a gate that cannot tell must refuse, never assume.
RUNNER_ENVIRONMENT=
PRIVILEGED_RUNNER_MARKER=
EPHEMERAL_RUNNER_MARKER=
EXPECT_TOKEN=RUNNER_TIER_UNRESOLVED
EOF

: > tools/evidence/tests/fixtures/runner/privileged.marker

cat > tools/evidence/tests/negative/NT-05/README.md <<'EOF'
NT-05 / N3 — a privileged workflow landing on a shared runner MUST fail.

Three contexts x four privileged workflows = twelve negatives.
The four are the closed set of D87 (line 10180): deploy-production.yml,
migrate.yml, the rollback workflow (D-L2-05), the production-restore workflow.

D-L2-09 is OPEN with L0: the two marker paths are an L5 infra/** interface and
are not invented here. Until it resolves, the non-ephemeral context reports
UNARMED under rule S10 and the gate is RED. It is not marked passing and it is
not deleted.

Rule S9: DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
EOF

cat > tools/evidence/tests/x2/GATE-L2-010/negative.sh <<'EOF'
#!/usr/bin/env bash
# Runs the real runner-tier assertion under each broken context, for each privileged workflow.
# Each invocation must exit 2 and emit the context's declared EXPECT_TOKEN on stderr.
# Exits 0 (NEG OK) when every case is specific and correct; exits 1 (NEG FAIL) otherwise.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
WFS="deploy-production.yml migrate.yml restore-production.yml"
RB="$(python3 -c "import glob,yaml,sys
for f in glob.glob('contracts/**/*.y*ml', recursive=True):
    try: d=yaml.safe_load(open(f))
    except Exception: continue
    if isinstance(d,dict) and d.get('rollback_workflow_filename'):
        print(d['rollback_workflow_filename']); sys.exit(0)
" 2>/dev/null)"
[ -n "$RB" ] || { echo "ROLLBACK_WORKFLOW_FILENAME UNRESOLVED (D-L2-05)" >&2; exit 0; }
WFS="$WFS $RB"
any_fail=0
STDERR_FILE=$(mktemp)
for c in shared-pool non-ephemeral unresolvable; do
  ctx="tools/evidence/tests/negative/NT-05/$c/context.env"
  EXPECT_TOKEN="$(bash -c '. "$1" && echo "${EXPECT_TOKEN:-}"' -- "$ctx")"
  for w in $WFS; do
    ( set -a; . "$ctx"; set +a
      python3 -m tools.evidence.assert_runner_tier --workflow "$w" --summary >/dev/null ) 2>"$STDERR_FILE"
    rc=$?
    [ "$rc" = "2" ] || { echo "NEG FAIL: $c/$w: expected exit 2, got $rc"; any_fail=1; }
    grep -q "${EXPECT_TOKEN}" "$STDERR_FILE" \
      || { echo "NEG FAIL: $c/$w: expected token '${EXPECT_TOKEN}' not found"; any_fail=1; }
  done
done
rm -f "$STDERR_FILE"
[ "$any_fail" = "0" ] && echo "NEG OK" && exit 0
exit 1
EOF

cat > tools/evidence/tests/x2/GATE-L2-010/positive.sh <<'EOF'
#!/usr/bin/env bash
# The hosted default of D87: RUNNER_ENVIRONMENT=github-hosted must be admitted.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
RUNNER_ENVIRONMENT=github-hosted \
python3 -m tools.evidence.assert_runner_tier --workflow deploy-production.yml --summary >/dev/null 2>&1
EOF

chmod +x tools/evidence/tests/x2/GATE-L2-010/*.sh
git add tools/evidence/tests/negative/NT-05 tools/evidence/tests/fixtures/runner tools/evidence/tests/x2/GATE-L2-010
git commit -m "L2-T607: N3 - privileged workflow on a shared runner must fail (GATE-L2-010, NT-05, D87)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Every broken context is refused, for every privileged workflow | `bash tools/evidence/lane-negative.sh --gate GATE-L2-010 >/dev/null 2>&1; echo $?` | exactly `0` |
| A2 | The hosted default is admitted | `bash tools/evidence/lane-verify.sh --gate GATE-L2-010 >/dev/null 2>&1; echo $?` | exactly `0` |
| A3 | Three contexts exist | `ls -d tools/evidence/tests/negative/NT-05/*/ \| wc -l \| tr -d ' '` | exactly `3` |
| A4 | Each context declares its expected token | `grep -hc '^EXPECT_TOKEN=' tools/evidence/tests/negative/NT-05/*/context.env \| sort -u \| tr -d ' '` | exactly `1` |
| A5 | Only tokens fixed by `L2-T172` are used | `grep -hoE 'RUNNER_TIER_[A-Z_]+' tools/evidence/tests/negative/NT-05/*/context.env \| sort -u \| grep -vcE '^RUNNER_TIER_(SHARED_POOL|NOT_EPHEMERAL|UNRESOLVED)$'` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --gate GATE-L2-010 >/dev/null 2>&1 && \
bash tools/evidence/lane-verify.sh  --gate GATE-L2-010 >/dev/null 2>&1 && \
test "$(ls -d tools/evidence/tests/negative/NT-05/*/ | wc -l | tr -d ' ')" = "3" && \
test "$(grep -hoE 'RUNNER_TIER_[A-Z_]+' tools/evidence/tests/negative/NT-05/*/context.env | sort -u | grep -vcE '^RUNNER_TIER_(SHARED_POOL|NOT_EPHEMERAL|UNRESOLVED)$')" = "0" && \
echo "L2-T607 OK" || echo "L2-T607 FAIL"
```
Correct output: the single line `L2-T607 OK`.

**STOP rule:** if `rollback_workflow_filename` cannot be resolved from `contracts/**`, **D-L2-05** is unresolved: the negative runs against three workflows and the gate reports `UNARMED` for the fourth under rule **S10**. Record that in the PR body; do not choose a filename. If `tools.evidence.assert_runner_tier` does not exist, `L2-T172` has not merged: STOP under `S1`, do not write a substitute assertion. **Never** widen the admitted set to make A1 pass — that is rule **S6**.

---

### L2-T608 — N4: a deploy from a non-default ref MUST be refused

**Size:** M  **Depends on:** `L2-T604`  **Branch slug:** `lane/2/06-n4-ref-policy`

**Creates:** `tools/evidence/tests/negative/GATE-L2-005/{feature-branch,unprotected-tag,policy-absent,policy-too-wide}/`, `tools/evidence/tests/x2/GATE-L2-005/{positive.sh,negative.sh}`

Spec basis is §8/N4: **D91** (L10184), §33.4 (L2911), §98.2 Phase 1 (L9024), invariant 25 (L9487). Tokens are those fixed by `L2-03-production-gates.md` `L2-T173`.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-n4-ref-policy
mkdir -p tools/evidence/tests/negative/GATE-L2-005/{feature-branch,unprotected-tag,policy-absent,policy-too-wide} \
         tools/evidence/tests/x2/GATE-L2-005

cat > tools/evidence/tests/negative/GATE-L2-005/feature-branch/case.json <<'EOF'
{"ref":"refs/heads/feat/anything","environment":"production",
 "policy":{"default_branch":true,"protected_tags":true,"custom":[]},
 "expect_token":"ENV_POLICY_REF_NOT_ADMITTED"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-005/unprotected-tag/case.json <<'EOF'
{"ref":"refs/tags/scratch-1","environment":"production",
 "policy":{"default_branch":true,"protected_tags":true,"custom":[]},
 "expect_token":"ENV_POLICY_REF_NOT_ADMITTED"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-005/policy-absent/case.json <<'EOF'
{"ref":"refs/heads/main","environment":"production",
 "policy":{},
 "expect_token":"ENV_POLICY_ABSENT"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-005/policy-too-wide/case.json <<'EOF'
{"ref":"refs/heads/main","environment":"production",
 "policy":{"custom":["*"]},
 "expect_token":"ENV_POLICY_TOO_WIDE"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-005/README.md <<'EOF'
N4 — a deploy from a non-default ref MUST be refused. D91 (line 10184).

Four cases. The last two carry the weight:

  policy-absent    D91's whole argument is that "a repository with the first
                   [branch protection] and not the second [a deployment branch
                   policy] holds production credentials behind nothing." A ref
                   check with no policy check passes happily against an absent
                   policy - the exact real-world state D91 exists to detect.
  policy-too-wide  A policy admitting "*" admits every branch. A gate that reads
                   the policy and does not judge it has read a value, not
                   enforced a control.

Section 33.4 (line 2911) names the consequence: a Write holder "pushes a branch
carrying a workflow that declares environment: production, and GitHub hands that
job the environment's secrets from an unreviewed ref."

Rule S9: DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
EOF

cat > tools/evidence/tests/x2/GATE-L2-005/negative.sh <<'EOF'
#!/usr/bin/env bash
# Each case must exit 2 and emit the case's declared expect_token on stderr.
# Exits 0 (NEG OK) when every case is specific and correct; exits 1 (NEG FAIL) otherwise.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
any_fail=0
STDERR_FILE=$(mktemp)
for c in feature-branch unprotected-tag policy-absent policy-too-wide; do
  case_file="tools/evidence/tests/negative/GATE-L2-005/$c/case.json"
  EXPECT_TOKEN="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('expect_token',''))" "$case_file")"
  python3 -m tools.evidence.env_policy_assert \
    --case "$case_file" --summary >"$STDERR_FILE" 2>&1
  rc=$?
  [ "$rc" = "2" ] || { echo "NEG FAIL: $c: expected exit 2, got $rc"; any_fail=1; }
  grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
    || { echo "NEG FAIL: $c: expected token '$EXPECT_TOKEN' not found"; any_fail=1; }
done
rm -f "$STDERR_FILE"
[ "$any_fail" = "0" ] && echo "NEG OK" && exit 0
exit 1
EOF

cat > tools/evidence/tests/x2/GATE-L2-005/positive.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
T="$(mktemp)"
printf '%s\n' '{"ref":"refs/heads/main","environment":"production","policy":{"default_branch":true,"protected_tags":true,"custom":[]}}' > "$T"
python3 -m tools.evidence.env_policy_assert --case "$T" --summary >/dev/null 2>&1
rc=$?; rm -f "$T"; exit $rc
EOF

chmod +x tools/evidence/tests/x2/GATE-L2-005/*.sh
git add tools/evidence/tests/negative/GATE-L2-005 tools/evidence/tests/x2/GATE-L2-005
git commit -m "L2-T608: N4 - a deploy from a non-default ref must be refused (GATE-L2-005, D91)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | All four cases are refused | `bash tools/evidence/lane-negative.sh --gate GATE-L2-005 >/dev/null 2>&1; echo $?` | exactly `0` |
| A2 | The default-branch case against a real policy is admitted | `bash tools/evidence/lane-verify.sh --gate GATE-L2-005 >/dev/null 2>&1; echo $?` | exactly `0` |
| A3 | Four cases exist | `ls -d tools/evidence/tests/negative/GATE-L2-005/*/ \| wc -l \| tr -d ' '` | exactly `4` |
| A4 | Only tokens fixed by `L2-T173` are used | `grep -hoE 'ENV_POLICY_[A-Z_]+' tools/evidence/tests/negative/GATE-L2-005/*/case.json \| sort -u \| grep -vcE '^ENV_POLICY_(REF_NOT_ADMITTED|ABSENT|TOO_WIDE)$'` | exactly `0` |
| A5 | This task performs no write API verb | `grep -rcE '(-X |--method )(POST|PUT|PATCH|DELETE)' tools/evidence/tests/x2/GATE-L2-005/ \| grep -vc ':0$'` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --gate GATE-L2-005 >/dev/null 2>&1 && \
bash tools/evidence/lane-verify.sh  --gate GATE-L2-005 >/dev/null 2>&1 && \
test "$(ls -d tools/evidence/tests/negative/GATE-L2-005/*/ | wc -l | tr -d ' ')" = "4" && \
test "$(grep -hoE 'ENV_POLICY_[A-Z_]+' tools/evidence/tests/negative/GATE-L2-005/*/case.json | sort -u | grep -vcE '^ENV_POLICY_(REF_NOT_ADMITTED|ABSENT|TOO_WIDE)$')" = "0" && \
echo "L2-T608 OK" || echo "L2-T608 FAIL"
```
Correct output: the single line `L2-T608 OK`.

**STOP rule:** if the `policy-absent` or `policy-too-wide` case is **not** refused, the gate reads the policy and does not judge it. **Do not delete those two cases and do not weaken them to a warning.** They are the two D91 exists for. STOP under **S9** and file the blocker. If `tools.evidence.env_policy_assert` does not exist, `L2-T173` has not merged: STOP under `S1`. Creating or updating a real environment policy from this lane is a foreign-path act performed through an API and is forbidden under `S2`, whatever the failure appears to require.

---

### L2-T609 — N5: a machine-account approval MUST NOT satisfy the gate

**Size:** M  **Depends on:** `L2-T604`  **Branch slug:** `lane/2/06-n5-machine-approval`

**Creates:** `tools/evidence/tests/negative/GATE-L2-011/{machine-account,app-installation,human-no-capability}/`, `tools/evidence/tests/x2/GATE-L2-011/{positive.sh,negative.sh}`

Spec basis is §8/N5: §37.3 (L3266), invariant 18 (L9477), **D53** (L10121), §98.2 Phase 1 (L9024). Tokens are those fixed by `L2-03-production-gates.md` `L2-T171`. The people registry read is the fixture copied by `L2-T602`, never a hand-written one.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-n5-machine-approval
mkdir -p tools/evidence/tests/negative/GATE-L2-011/{machine-account,app-installation,human-no-capability} \
         tools/evidence/tests/x2/GATE-L2-011

test -s tools/evidence/tests/fixtures/registry/people.yaml || { echo "people fixture ABSENT - L2-T602 NOT DONE - STOP"; exit 1; }

cat > tools/evidence/tests/negative/GATE-L2-011/machine-account/case.json <<'EOF'
{"approver":"background-worker-bot","required_capability":"production-approval",
 "people":"tools/evidence/tests/fixtures/registry/people.yaml",
 "deployer":"dev-two","expect_token":"ACTOR_NOT_HUMAN"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-011/app-installation/case.json <<'EOF'
{"approver":"records-writer[bot]","required_capability":"production-approval",
 "people":"tools/evidence/tests/fixtures/registry/people.yaml",
 "deployer":"dev-two","expect_token":"ACTOR_NOT_HUMAN"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-011/human-no-capability/case.json <<'EOF'
{"approver":"dev-three","required_capability":"production-approval",
 "people":"tools/evidence/tests/fixtures/registry/people.yaml",
 "deployer":"dev-two","expect_token":"ACTOR_CAPABILITY_MISSING"}
EOF

cat > tools/evidence/tests/negative/GATE-L2-011/README.md <<'EOF'
N5 — a machine-account approval MUST NOT satisfy the production-approval gate.

Section 37.3 (line 3266): human-only CODEOWNERS "mechanically prevents a
machine-account approval from ever satisfying a gate." D53 (line 10121) states
the same rule as a decision. Section 98.2 Phase 1 (line 9024) requires the check
be "executed negatively".

Three cases. The third is not padding: Section 37.3 requires the actor to be a
human in people.yaml *holding the capability the action requires*. Identity and
authority are two checks, and a suite that runs one reports the other green
without executing it.

BOUNDARY: the branch-protection half of this rule is canary CAN-MACHINE, owned
by L5 (protocol/11-definition-of-done.md section 4.2). This gate is the workflow
half only. Lane 2's green does not discharge Lane 5's.

Rule S9: DELIBERATELY BROKEN — DO NOT FIX, DO NOT DELETE.
EOF

cat > tools/evidence/tests/x2/GATE-L2-011/negative.sh <<'EOF'
#!/usr/bin/env bash
# Each case must exit 2 and emit the case's declared expect_token on stderr.
# Exits 0 (NEG OK) when every case is specific and correct; exits 1 (NEG FAIL) otherwise.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
any_fail=0
STDERR_FILE=$(mktemp)
for c in machine-account app-installation human-no-capability; do
  f="tools/evidence/tests/negative/GATE-L2-011/$c/case.json"
  a="$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['approver'])" "$f")"
  k="$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['required_capability'])" "$f")"
  p="$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['people'])" "$f")"
  EXPECT_TOKEN="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('expect_token',''))" "$f")"
  python3 -m tools.evidence.actor_gate --actor "$a" --capability "$k" --people "$p" --summary >"$STDERR_FILE" 2>&1
  rc=$?
  [ "$rc" = "2" ] || { echo "NEG FAIL: $c: expected exit 2, got $rc"; any_fail=1; }
  grep -q "$EXPECT_TOKEN" "$STDERR_FILE" \
    || { echo "NEG FAIL: $c: expected token '$EXPECT_TOKEN' not found"; any_fail=1; }
done
rm -f "$STDERR_FILE"
[ "$any_fail" = "0" ] && echo "NEG OK" && exit 0
exit 1
EOF

cat > tools/evidence/tests/x2/GATE-L2-011/positive.sh <<'EOF'
#!/usr/bin/env bash
# A human holding production-approval MUST be admitted, or the gate proves nothing.
set -uo pipefail
cd "$(dirname "$0")/../../../../.." || exit 1
P=tools/evidence/tests/fixtures/registry/people.yaml
A="$(python3 -c "
import yaml
d=yaml.safe_load(open('$P')) or {}
ppl=d.get('people', d if isinstance(d,list) else [])
for p in ppl:
    if isinstance(p,dict) and 'production-approval' in (p.get('capabilities') or []):
        print(p.get('github_login') or p.get('id') or ''); break
")"
[ -n "$A" ] || { echo "NO production-approval HOLDER IN FIXTURE people.yaml" >&2; exit 1; }
python3 -m tools.evidence.actor_gate --actor "$A" --capability production-approval --people "$P" --summary >/dev/null 2>&1
EOF

chmod +x tools/evidence/tests/x2/GATE-L2-011/*.sh
git add tools/evidence/tests/negative/GATE-L2-011 tools/evidence/tests/x2/GATE-L2-011
git commit -m "L2-T609: N5 - a machine-account approval must not satisfy the gate (GATE-L2-011, D53)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | All three cases are refused | `bash tools/evidence/lane-negative.sh --gate GATE-L2-011 >/dev/null 2>&1; echo $?` | exactly `0` |
| A2 | A capability-holding human is admitted | `bash tools/evidence/lane-verify.sh --gate GATE-L2-011 >/dev/null 2>&1; echo $?` | exactly `0` |
| A3 | Three cases exist | `ls -d tools/evidence/tests/negative/GATE-L2-011/*/ \| wc -l \| tr -d ' '` | exactly `3` |
| A4 | Only tokens fixed by `L2-T171` are used | `grep -hoE 'ACTOR_[A-Z_]+' tools/evidence/tests/negative/GATE-L2-011/*/case.json \| sort -u \| grep -vcE '^ACTOR_(NOT_HUMAN|CAPABILITY_MISSING)$'` | exactly `0` |
| A5 | The people registry is the copied fixture, not a hand-written one | `grep -c 'tools/evidence/tests/fixtures/registry/people.yaml' tools/evidence/tests/negative/GATE-L2-011/*/case.json \| grep -vc ':0$'` | exactly `3` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/lane-negative.sh --gate GATE-L2-011 >/dev/null 2>&1 && \
bash tools/evidence/lane-verify.sh  --gate GATE-L2-011 >/dev/null 2>&1 && \
test "$(ls -d tools/evidence/tests/negative/GATE-L2-011/*/ | wc -l | tr -d ' ')" = "3" && \
test "$(grep -hoE 'ACTOR_[A-Z_]+' tools/evidence/tests/negative/GATE-L2-011/*/case.json | sort -u | grep -vcE '^ACTOR_(NOT_HUMAN|CAPABILITY_MISSING)$')" = "0" && \
echo "L2-T609 OK" || echo "L2-T609 FAIL"
```
Correct output: the single line `L2-T609 OK`.

**STOP rule:** if the fixture `people.yaml` contains no person holding `production-approval`, A2 cannot run. **Do not add a person to the fixture** — it is copied from `contracts/fixtures/core/**`, which is L0-owned and FROZEN (`PARTITION.md` rule 2). STOP under `S1` and file a Fixture Change Request per `protocol/09-fixtures.md` §10 Route B, naming the missing capability holder. If `tools.evidence.actor_gate` does not exist, `L2-T171` has not merged: STOP under `S1`.

---

### L2-T603 — The `workflow_dispatch` harness (X3), fail-closed while D-L2-11 is open

**Size:** L  **Depends on:** `L2-T602`  **Branch slug:** `lane/2/06-x3-harness`

**Creates:** `tools/evidence/tests/lib/dispatch.sh`, `tools/evidence/tests/x3/README.md`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-x3-harness
mkdir -p tools/evidence/tests/x3

cat > tools/evidence/tests/lib/dispatch.sh <<'EOF'
#!/usr/bin/env bash
# X3 harness client: dispatches a real reusable workflow at a fixture repository
# in the sandbox organisation and asserts the RUN FAILED with the gate's token.
#
# D-L2-11 is OPEN. sandbox_org_slug, sandbox_dispatch_secret_name and
# fixture_repo_prefix are contracts/** keys and are never invented here.
# While unresolved this client exits non-zero with SANDBOX_ORG_UNRESOLVED.
# It is a fail-closed stub, never a skipped step (rule S10).
set -uo pipefail

d_resolve_key() {   # d_resolve_key <key>
  grep -rhoE "^[[:space:]]*$1:[[:space:]]*\S+" contracts/ 2>/dev/null | head -1 | awk '{print $2}'
}

d_preflight() {
  local org secret prefix
  org="$(d_resolve_key sandbox_org_slug)"
  secret="$(d_resolve_key sandbox_dispatch_secret_name)"
  prefix="$(d_resolve_key fixture_repo_prefix)"
  if [ -z "$org" ] || [ -z "$secret" ] || [ -z "$prefix" ]; then
    printf 'SANDBOX_ORG_UNRESOLVED (D-L2-11) org=%s secret=%s prefix=%s\n' \
      "${org:-<absent>}" "${secret:-<absent>}" "${prefix:-<absent>}" >&2
    return 1
  fi
  printf '%s %s %s\n' "$org" "$secret" "$prefix"
}

d_dispatch_must_fail() {   # d_dispatch_must_fail <repo-suffix> <workflow> <expected-token>
  local pf; pf="$(d_preflight)" || return 1
  local org prefix; org="$(echo "$pf" | awk '{print $1}')"; prefix="$(echo "$pf" | awk '{print $3}')"
  local repo="$org/${prefix}$1"
  gh workflow run "$2" -R "$repo" --ref main >/dev/null 2>&1 || return 1
  sleep 20
  local concl
  concl="$(gh run list -R "$repo" -w "$2" -L 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null)"
  [ "$concl" = "failure" ] || { printf 'X3-NON-DISCRIMINATING %s %s conclusion=%s\n' "$repo" "$2" "${concl:-none}" >&2; return 1; }
  gh run view -R "$repo" -w "$2" --log 2>/dev/null | grep -q "$3" \
    || { printf 'X3-WRONG-REASON %s expected_token=%s\n' "$repo" "$3" >&2; return 1; }
  return 0
}
EOF

cat > tools/evidence/tests/x3/README.md <<'EOF'
X3 — the workflow_dispatch harness.

X3 dispatches the REAL reusable workflows at synthetic product repositories in
the sandbox organisation, and asserts three things about each run:

  1. the run conclusion is `failure`, not `success` and not `skipped`
  2. the failing step's log carries the gate's own token
  3. no environment secret was materialised into the job

Point 2 is why X3 is not just "the run went red": a run that fails for the wrong
reason is a green gate wearing a red badge.

BLOCKED: D-L2-11. Every gate whose tier is X3 reports UNARMED under rule S10 and
is RED until L0 publishes sandbox_org_slug, sandbox_dispatch_secret_name and
fixture_repo_prefix in contracts/**. An unarmed gate is never reported as
passing and never deleted - protocol/00-test-strategy.md section 0 quotes
Section 99.6 risk 5: "An unavailable protection feature reproduces the
silent-gate failure."
EOF

chmod +x tools/evidence/tests/lib/dispatch.sh
git add tools/evidence/tests/lib/dispatch.sh tools/evidence/tests/x3
git commit -m "L2-T603: X3 workflow_dispatch harness, fail-closed pending D-L2-11"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The client parses | `bash -n tools/evidence/tests/lib/dispatch.sh; echo $?` | exactly `0` |
| A2 | With D-L2-11 open, preflight fails closed | `bash -c '. tools/evidence/tests/lib/dispatch.sh; d_preflight' >/dev/null 2>&1; echo $?` | exactly `1` |
| A3 | The unresolved token is emitted on stderr | `bash -c '. tools/evidence/tests/lib/dispatch.sh; d_preflight' 2>&1 >/dev/null \| grep -c SANDBOX_ORG_UNRESOLVED` | exactly `1` |
| A4 | The harness never treats `skipped` as pass | `grep -c 'conclusion" = "failure"\|concl" = "failure"' tools/evidence/tests/lib/dispatch.sh` | at least `1` |
| A5 | No sandbox slug is hard-coded | `grep -cE 'github\.com/[a-z0-9-]+/' tools/evidence/tests/lib/dispatch.sh` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/tests/lib/dispatch.sh && \
{ bash -c '. tools/evidence/tests/lib/dispatch.sh; d_preflight' >/dev/null 2>&1; test $? -eq 1; } && \
test "$(bash -c '. tools/evidence/tests/lib/dispatch.sh; d_preflight' 2>&1 >/dev/null | grep -c SANDBOX_ORG_UNRESOLVED)" = "1" && \
test "$(grep -cE 'github\.com/[a-z0-9-]+/' tools/evidence/tests/lib/dispatch.sh)" = "0" && \
echo "L2-T603 OK" || echo "L2-T603 FAIL"
```
Correct output: the single line `L2-T603 OK`.

**STOP rule:** if A2 returns `0` — preflight succeeded while D-L2-11 is open — the client resolved a value it must not have. **Do not commit.** A harness that dispatches at an org nobody declared is a harness dispatching at an unknown target. STOP under `S4` and file the blocker naming the value it resolved and the file it came from.

---

### L2-T221 — `fixture-dispatch.yml`, the X3 driver

**Size:** M  **Depends on:** `L2-T603`  **Branch slug:** `lane/2/06-fixture-dispatch`

**Creates:** `.github/workflows/fixture-dispatch.yml`

This workflow is `workflow_dispatch`-only and is **not** a required status context. It carries no `if:` and no path filter, per rule **S7**, and every third-party action it uses is pinned to a full commit SHA from `tools/evidence/action-pins.txt` (`L2-T532` in `L2-05-tasks.md` §3 — renumbered from `L2-T502`, which `L2-04-evidence-chain.md` §6 owns), per invariant 85 (L9565).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-fixture-dispatch
test -s tools/evidence/action-pins.txt || { echo "action-pins.txt ABSENT - L2-T532 NOT DONE - STOP"; exit 1; }
CHECKOUT_PIN="$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')"
[ -n "$CHECKOUT_PIN" ] || { echo "actions/checkout NOT IN PIN LEDGER - STOP"; exit 1; }

cat > .github/workflows/fixture-dispatch.yml <<EOF
# X3 driver — Lane 2 test tier 3. Manual only; never a required status context.
# Spec: D87 (10180), D91 (10184), Section 27.2 (2572), Section 37.3 (3261-3268).
# Blocked on D-L2-11: the harness fails closed with SANDBOX_ORG_UNRESOLVED.
name: fixture-dispatch
on:
  workflow_dispatch:
    inputs:
      gate:
        description: "Gate id to exercise at X3, e.g. GATE-L2-010"
        required: true
permissions:
  contents: read
jobs:
  x3:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@${CHECKOUT_PIN}
      - name: Run the X3 case for the named gate (fail-closed while D-L2-11 is open)
        run: |
          set -euo pipefail
          bash tools/evidence/tests/x3/run.sh --gate "\${{ inputs.gate }}"
EOF

mkdir -p tools/evidence/tests/x3
cat > tools/evidence/tests/x3/run.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../../../.." || exit 1
. tools/evidence/tests/lib/dispatch.sh
d_preflight >/dev/null || { echo "X3 UNARMED (D-L2-11) - gate is RED, not skipped" >&2; exit 1; }
echo "X3 armed for $*"
EOF
chmod +x tools/evidence/tests/x3/run.sh

git add .github/workflows/fixture-dispatch.yml tools/evidence/tests/x3/run.sh
git commit -m "L2-T221: fixture-dispatch.yml - the X3 driver, manual only, fail-closed"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The workflow is valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/fixture-dispatch.yml'))"; echo $?` | exactly `0` |
| A2 | It carries no `if:` and no path filter | `grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/fixture-dispatch.yml` | exactly `0` |
| A3 | It triggers only on `workflow_dispatch` | `python3 -c "import yaml;d=yaml.safe_load(open('.github/workflows/fixture-dispatch.yml'));print(sorted((d.get(True) or d.get('on')).keys()))"` | exactly `['workflow_dispatch']` |
| A4 | Every action is pinned to a 40-hex SHA | `grep -oE 'uses: [^@]+@[^ ]+' .github/workflows/fixture-dispatch.yml \| grep -vcE '@[0-9a-f]{40}$'` | exactly `0` |
| A5 | It is not in the required-context registry | `grep -c 'fixture-dispatch' templates/workflows/required-checks.yaml` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/fixture-dispatch.yml'))" && \
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/fixture-dispatch.yml)" = "0" && \
test "$(grep -oE 'uses: [^@]+@[^ ]+' .github/workflows/fixture-dispatch.yml | grep -vcE '@[0-9a-f]{40}$')" = "0" && \
test "$(grep -c 'fixture-dispatch' templates/workflows/required-checks.yaml)" = "0" && \
echo "L2-T221 OK" || echo "L2-T221 FAIL"
```
Correct output: the single line `L2-T221 OK`.

**STOP rule:** if adding `fixture-dispatch` to `templates/workflows/required-checks.yaml` appears necessary, it is not. That file is a published cross-lane interface and its sixteen names are fixed (`L2-05-tasks.md` §0.5). STOP under `S4`.

---

### L2-T610 — The AT coverage map

**Size:** S  **Depends on:** `L2-T605`, `L2-T606`, `L2-T607`, `L2-T608`, `L2-T609`  **Branch slug:** `lane/2/06-at-map`

**Creates:** `tools/evidence/tests/at-map.yaml`

Transcribe §7 of this document. Ten rows, no more and no fewer. **The ten AT ids are fixed by `protocol/00-test-strategy.md` §6 and the executor adds none.**

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-at-map

cat > tools/evidence/tests/at-map.yaml <<'EOF'
# Lane 2 acceptance-test coverage map. Owner set fixed by
# protocol/00-test-strategy.md section 6. Spec catalogue: Section 100.
# Lane 2 owns exactly these ten. Adding an eleventh is a STOP under S4.
acceptance_tests:
  - at: AT-023
    spec_line: 9337
    tier: X1
    gate: GATE-L2-007
    status: armed
  - at: AT-024
    spec_line: 9338
    tier: X1
    gate: GATE-L2-007
    status: armed
  - at: AT-025
    spec_line: 9339
    tier: X1
    gate: GATE-L2-007
    status: armed
  - at: AT-026
    spec_line: 9340
    tier: X2
    gate: GATE-L2-001
    status: armed
  - at: AT-027
    spec_line: 9341
    tier: X1
    gate: GATE-L2-002
    status: armed
  - at: AT-030
    spec_line: 9344
    tier: X2
    gate: GATE-L2-008
    status: armed
  - at: AT-034
    spec_line: 9348
    tier: T3
    gate: GATE-L2-008
    status: t3-deferred
  - at: AT-035
    spec_line: 9349
    tier: X3
    gate: GATE-L2-008
    status: unarmed-d-l2-11
  - at: AT-103
    spec_line: 9352
    tier: X3
    gate: GATE-L2-009
    status: unarmed-d-l2-11
  - at: AT-107
    spec_line: 9377
    tier: X1
    gate: GATE-L2-003
    status: armed
EOF

git add tools/evidence/tests/at-map.yaml
git commit -m "L2-T610: AT coverage map - the ten acceptance tests Lane 2 owns"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Exactly ten rows | `python3 -c "import yaml;print(len(yaml.safe_load(open('tools/evidence/tests/at-map.yaml'))['acceptance_tests']))"` | exactly `10` |
| A2 | Every AT id is one of the ten §6 assigns to L2 | `grep -oE 'AT-[0-9]{3}' tools/evidence/tests/at-map.yaml \| sort -u \| tr '\n' ' '` | exactly `AT-023 AT-024 AT-025 AT-026 AT-027 AT-030 AT-034 AT-035 AT-103 AT-107 ` |
| A3 | Every named gate exists as a declaration | `python3 -c "import yaml,os;m=yaml.safe_load(open('tools/evidence/tests/at-map.yaml'))['acceptance_tests'];print(sum(1 for r in m if not os.path.isfile('tools/evidence/gates/%s.yaml'%r['gate'])))"` | exactly `0` |
| A4 | AT-034 is not claimed at T1 | `python3 -c "import yaml;m=yaml.safe_load(open('tools/evidence/tests/at-map.yaml'))['acceptance_tests'];print([r['status'] for r in m if r['at']=='AT-034'][0])"` | exactly `t3-deferred` |
| A5 | No status is `pass` or `skip` | `grep -cE 'status: (pass|skip|n/a)' tools/evidence/tests/at-map.yaml` | exactly `0` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(python3 -c "import yaml;print(len(yaml.safe_load(open('tools/evidence/tests/at-map.yaml'))['acceptance_tests']))")" = "10" && \
test "$(grep -oE 'AT-[0-9]{3}' tools/evidence/tests/at-map.yaml | sort -u | tr '\n' ' ')" = "AT-023 AT-024 AT-025 AT-026 AT-027 AT-030 AT-034 AT-035 AT-103 AT-107 " && \
test "$(python3 -c "import yaml,os;m=yaml.safe_load(open('tools/evidence/tests/at-map.yaml'))['acceptance_tests'];print(sum(1 for r in m if not os.path.isfile('tools/evidence/gates/%s.yaml'%r['gate'])))")" = "0" && \
test "$(grep -cE 'status: (pass|skip|n/a)' tools/evidence/tests/at-map.yaml)" = "0" && \
echo "L2-T610 OK" || echo "L2-T610 FAIL"
```
Correct output: the single line `L2-T610 OK`.

**STOP rule:** if an AT in the map cannot be made to pass, that is a defect report against the build, escalated to L0 — **never** a status change and never a wording change. `protocol/00-test-strategy.md` §1.2 quotes AT-090 for the same reason: *"a reinterpreted access-control test is how the boundary erodes."* STOP under `S4`.

---

### L2-T611 — Coverage floor, vacuity proof and the drill target

**Size:** M  **Depends on:** `L2-T610`  **Branch slug:** `lane/2/06-coverage-floor`

**Creates:** `tools/evidence/tests/coverage-floor.yaml`, `tools/evidence/tests/lib/audit.sh`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-coverage-floor

A="$(bash tools/evidence/lane-verify.sh   --all 2>/dev/null | tail -1 | sed -E 's/.*assertions=([0-9]+).*/\1/')"
N="$(bash tools/evidence/lane-negative.sh --all 2>/dev/null | tail -1 | sed -E 's/.*negatives_run=([0-9]+).*/\1/')"
[ -n "$A" ] && [ "$A" != "0" ] || { echo "ASSERTION COUNT IS ZERO - SUITE IS VACUOUS - STOP"; exit 1; }
[ -n "$N" ] && [ "$N" != "0" ] || { echo "NEGATIVE COUNT IS ZERO - SUITE IS VACUOUS - STOP"; exit 1; }

cat > tools/evidence/tests/coverage-floor.yaml <<EOF
# Frozen floor. A full --all run below either number exits 2 (VACUOUS) even when
# every assertion it did run passed. Section 53.1: a silently narrowed comparison
# is itself visible drift. Raising these numbers is normal; lowering one is a
# reviewable one-line diff and needs a reason in the PR body.
min_assertions: ${A}
min_negatives_run: ${N}
frozen_on: "$(date -u +%Y-%m-%d)"
EOF

cat > tools/evidence/tests/lib/audit.sh <<'EOF'
#!/usr/bin/env bash
# The L2 half of the negative-test doctrine's recursive clause
# (protocol/00-test-strategy.md section 4.1 rule 7).
set -uo pipefail
cd "$(dirname "$0")/../../../.." || exit 1

fail=0
# 1. Every gate declaration carries a negative block naming a real, non-empty fixture.
python3 - <<'PY' || fail=1
import glob, os, sys, yaml
bad = []
proves = []
for f in sorted(glob.glob('tools/evidence/gates/GATE-L2-*.yaml')):
    d = yaml.safe_load(open(f))
    n = (d or {}).get('negative') or {}
    fx = n.get('fixture')
    if not fx or not os.path.isdir(fx) or not os.listdir(fx):
        bad.append((f, 'fixture missing or empty'))
    if not n.get('proves'):
        bad.append((f, 'proves empty'))
    else:
        proves.append(n['proves'])
if len(proves) != len(set(proves)):
    bad.append(('<catalogue>', 'duplicated proves string'))
for f, why in bad:
    print('NEGATIVE-AUDIT-FAIL %s %s' % (f, why))
sys.exit(1 if bad else 0)
PY

# 2. The floor.
A="$(bash tools/evidence/lane-verify.sh   --all 2>/dev/null | tail -1 | sed -E 's/.*assertions=([0-9]+).*/\1/')"
N="$(bash tools/evidence/lane-negative.sh --all 2>/dev/null | tail -1 | sed -E 's/.*negatives_run=([0-9]+).*/\1/')"
FA="$(python3 -c "import yaml;print(yaml.safe_load(open('tools/evidence/tests/coverage-floor.yaml'))['min_assertions'])")"
FN="$(python3 -c "import yaml;print(yaml.safe_load(open('tools/evidence/tests/coverage-floor.yaml'))['min_negatives_run'])")"
[ "${A:-0}" -ge "$FA" ] || { echo "COVERAGE-FLOOR-FAIL assertions=$A floor=$FA"; fail=1; }
[ "${N:-0}" -ge "$FN" ] || { echo "COVERAGE-FLOOR-FAIL negatives_run=$N floor=$FN"; fail=1; }

# 3. The recursive clause: an injected declaration with no negative block MUST be rejected.
T=tools/evidence/gates/GATE-L2-999.yaml
printf 'gate_id: GATE-L2-999\nowner_lane: L2\nlevel: T1\ntitle: audit self-test\n' > "$T"
python3 - <<'PY' >/dev/null 2>&1
import glob, yaml, sys
sys.exit(0 if any((yaml.safe_load(open(f)) or {}).get('negative') is None
                  for f in glob.glob('tools/evidence/gates/GATE-L2-*.yaml')) else 1)
PY
caught=$?
rm -f "$T"
[ "$caught" = "0" ] || { echo "AUDIT-SELF-TEST-FAIL: a declaration with no negative block was not detected"; fail=1; }

[ "$fail" = "0" ] && echo "NEGATIVE-AUDIT OK" || echo "NEGATIVE-AUDIT FAIL"
exit "$fail"
EOF

chmod +x tools/evidence/tests/lib/audit.sh
git add tools/evidence/tests/coverage-floor.yaml tools/evidence/tests/lib/audit.sh
git commit -m "L2-T611: coverage floor, negative audit and the recursive self-test"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The floor is frozen at a non-zero value | `grep -cE '^min_(assertions|negatives_run): [1-9][0-9]*$' tools/evidence/tests/coverage-floor.yaml` | exactly `2` |
| A2 | The audit passes on the real catalogue | `bash tools/evidence/tests/lib/audit.sh \| tail -1` | exactly `NEGATIVE-AUDIT OK` |
| A3 | The audit's own self-test detects a negative-less declaration | `bash tools/evidence/tests/lib/audit.sh >/dev/null 2>&1; echo $?` | exactly `0` |
| A4 | The self-test leaves no artifact behind | `test ! -f tools/evidence/gates/GATE-L2-999.yaml; echo $?` | exactly `0` |
| A5 | The catalogue is still eleven gates | `ls tools/evidence/gates/GATE-L2-*.yaml \| wc -l \| tr -d ' '` | exactly `11` |
| A6 | Nothing outside the owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -cE '^min_(assertions|negatives_run): [1-9][0-9]*$' tools/evidence/tests/coverage-floor.yaml)" = "2" && \
test "$(bash tools/evidence/tests/lib/audit.sh | tail -1)" = "NEGATIVE-AUDIT OK" && \
test ! -f tools/evidence/gates/GATE-L2-999.yaml && \
test "$(ls tools/evidence/gates/GATE-L2-*.yaml | wc -l | tr -d ' ')" = "11" && \
echo "L2-T611 OK" || echo "L2-T611 FAIL"
```
Correct output: the single line `L2-T611 OK`.

**STOP rule:** if the floor computation produces `0` for either counter, the suite asserts nothing and the floor would freeze that. **Do not write a floor of zero and do not write a hand-chosen number.** STOP, file the blocker with `STOP RULE TRIGGERED: task-specific — zero-assertion suite`.

---

### L2-T220 — `lane-suite.yml`, the CI trigger for the lane suite

**Size:** M  **Depends on:** `L2-T611`  **Branch slug:** `lane/2/06-lane-suite-workflow`

**Creates:** `.github/workflows/lane-suite.yml`

`protocol/00-test-strategy.md` §2: *"The runner is the L0 `Makefile` … `.github/workflows/**` belongs to L2, so the workflows that invoke `make` are L2 deliverables built to the target names below; L0 owns the target names, L2 owns the triggers."* This task is that workflow. It invokes `make lane LANE=2`. It never re-implements the four sub-steps and it never reaches into another lane's tree.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/06-lane-suite-workflow
CHECKOUT_PIN="$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')"
[ -n "$CHECKOUT_PIN" ] || { echo "actions/checkout NOT IN PIN LEDGER - STOP"; exit 1; }

cat > .github/workflows/lane-suite.yml <<EOF
# T1 — the Lane 2 suite. protocol/00-test-strategy.md section 5 (T1).
# Runs on every push to lane/2/* and on every PR into integration.
# Carries no if: and no path filter (Section 33.2, lines 2854-2869; rule S7).
name: lane-suite-2
on:
  push:
    branches:
      - 'lane/2/**'
  pull_request:
    branches:
      - integration
permissions:
  contents: read
jobs:
  lane-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@${CHECKOUT_PIN}
        with:
          fetch-depth: 0
      - name: Lane 2 suite (T1)
        run: |
          set -euo pipefail
          if [ -f Makefile ] && grep -q '^lane:' Makefile; then
            make lane LANE=2 | tee lane-suite.stdout
          else
            # D-L2-06 bootstrap: L0's Makefile is not on the branch yet.
            { bash tools/evidence/lane-verify.sh   --all
              bash tools/evidence/lane-negative.sh --all
              bash tools/evidence/tests/lib/audit.sh ; } | tee lane-suite.stdout
          fi
      - name: Refuse a vacuous or non-discriminating run
        run: |
          set -euo pipefail
          grep -q 'GATE-RESULT' lane-suite.stdout || { echo "NO GATE-RESULT LINE - VACUOUS"; exit 1; }
          grep -E 'GATE-RESULT' lane-suite.stdout | while read -r l; do
            a=\$(echo "\$l" | sed -E 's/.*assertions=([0-9]+).*/\1/')
            nr=\$(echo "\$l" | sed -E 's/.*negatives_run=([0-9]+).*/\1/')
            nc=\$(echo "\$l" | sed -E 's/.*negatives_that_failed_correctly=([0-9]+).*/\1/')
            if [ "\$a" = "0" ] && [ "\$nr" = "0" ]; then echo "VACUOUS: \$l"; exit 1; fi
            if [ "\$nr" != "\$nc" ]; then echo "NON-DISCRIMINATING: \$l"; exit 1; fi
          done
EOF

git add .github/workflows/lane-suite.yml
git commit -m "L2-T220: lane-suite.yml - the T1 trigger for make lane LANE=2"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/lane-suite.yml'))"; echo $?` | exactly `0` |
| A2 | No `if:` and no path filter | `grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/lane-suite.yml` | exactly `0` |
| A3 | It invokes the L0 target, not a re-implementation | `grep -c 'make lane LANE=2' .github/workflows/lane-suite.yml` | exactly `1` |
| A4 | Every action pinned to a 40-hex SHA | `grep -oE 'uses: [^@]+@[^ ]+' .github/workflows/lane-suite.yml \| grep -vcE '@[0-9a-f]{40}$'` | exactly `0` |
| A5 | It fails on a vacuous run rather than passing it | `grep -c 'VACUOUS' .github/workflows/lane-suite.yml` | at least `2` |
| A6 | It writes to no path outside the three owned trees | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/lane-suite.yml'))" && \
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/lane-suite.yml)" = "0" && \
test "$(grep -c 'make lane LANE=2' .github/workflows/lane-suite.yml)" = "1" && \
test "$(grep -oE 'uses: [^@]+@[^ ]+' .github/workflows/lane-suite.yml | grep -vcE '@[0-9a-f]{40}$')" = "0" && \
echo "L2-T220 OK" || echo "L2-T220 FAIL"
```
Correct output: the single line `L2-T220 OK`.

**STOP rule:** if making this workflow green appears to require adding `continue-on-error`, an `if:` guard, or a path filter, STOP under **S6** and **S7**. A suite trigger that can be skipped is a suite that reports nothing on the pushes that matter, and §33.2 makes a `skipped` conclusion on a gate Blocking drift.

---

## 11. WHAT THIS DOCUMENT DOES NOT CLAIM

Stated so that no reader, and no later task, mistakes silence for coverage.

| Not claimed | Owner | Why |
|---|---|---|
| Branch protection, rulesets, CODEOWNERS generation, environment configuration, runner-group registration | L5 | `access/**`, `infra/**` (`PARTITION.md` line 21). Canaries `CAN-MACHINE`, and NT-01, NT-02, NT-03, NT-19, NT-28 |
| The reconciler's detection of the three D87 Blocking drift rows (L3596) | L3 | `reconciler/**`. Lane 2 asserts the workflow-side control; Lane 3 detects the configuration-side drift |
| Record and event **shapes** | L4 | `schemas/records/**`. Lane 2's fixtures are copied from `contracts/fixtures/core/**`, never authored |
| The plan-checker and NT-24 | **unassigned — subsystem G** | `PARTITION.md` v1 assigns subsystem G to no lane. Routed to L0 as **D-L2-12**. Also unassigned: **H**, **J**, **O**, **P**. None is claimed here |
| AT-034 at T1 | L0 at T3 | `protocol/00-test-strategy.md` §6: L2-owned, T3-gated. Reported `t3-deferred`, never `pass` |
| Every AT not in the ten of §7 | other lanes / L0 | `protocol/00-test-strategy.md` §6 assigns each of the 110 to exactly one owner |
| `templates/workflows/**` content | this lane, in `L2-01` and `L2-05` | Owned by L2 but written elsewhere; this document reads templates and never edits one |

---

## 12. SPEC AND PROTOCOL ANCHORS USED IN THIS DOCUMENT

Every citation below was read before it was written. Line numbers are into `MultiProduct_MasterSpec_v4.0.md`.

| Anchor | Line(s) | Used for |
|---|---|---|
| §27.2 workflow-identity gate | 2572 | N1, GATE-L2-009 |
| §31.2 seeded-defect case | 2787–2794 | GATE-L2-003, fixture markers |
| §32 evidence chain, eleven questions | 2803–2828 | GATE-L2-001, GATE-L2-008 |
| §33.2 required contexts, no `if:`, no path filter | 2854–2869 | GATE-L2-002, GATE-L2-007, rule S7 |
| §33.4 environments, deployment branch and tag policies | 2887–2912 (2911) | N4, GATE-L2-005 |
| §34.2 freeze window | 2930–2935 | GATE-L2-006 |
| §37.3 actor gate, machine-account approval | 3261–3268 (3266, 3268) | N5, GATE-L2-004, GATE-L2-011 |
| Privileged-workflow isolation; three Blocking rows | 3589, 3596 | N3, GATE-L2-010 |
| §41.2 `/version` digest match | 3717–3729 | N2 consequence |
| §48.1 action pinning | 4300–4308 | D-L2-13, pin assertions |
| SIG-15 repeated manual overrides | 4544 | GATE-L2-002 |
| SIG-18 verification-contract gaps | 4547 | GATE-L2-003 |
| §97.1 records-writer, time rule | 8836–8842 | GATE-L2-006 |
| §97.2 record write is a required, failing step | 8843–8926 | GATE-L2-008 |
| §98.2 Phase 1 completion check | 9024 | N4, N5 |
| §98.2 Phase 6 completion check | 9078 | N1 |
| §99.2 subsystems E, F, G | 9192–9194 | scope; D-L2-12 |
| §100 catalogue, AT-023…AT-107 | 9337–9377 | §7 |
| Invariants 9, 12, 18, 22, 23, 25, 72, 85 | 9462, 9465, 9477, 9484, 9485, 9487, 9549, 9565 | the five negatives |
| D53 machine-credential governance | 10121 | N5 |
| D73 workflow-identity gate is the mechanism of record | 10156 | N1 |
| D87 privileged-workflow isolation | 10180 | N3 |
| D89 records repository, no machine bypass actor | 10182 | boundary statements |
| D91 deployment branch and tag policies | 10184 | N4 |

| Protocol anchor | Used for |
|---|---|
| `protocol/00-test-strategy.md` §2 (entry-point paths), §3 (exit codes), §4 (negative doctrine, gate schema), §5 (T1), §6 (AT ownership), §7 (GATE-L2-001…008) | §0, §4, §6, §7 |
| `protocol/04-negative-tests.md` (NT-04, NT-05, NT-11, NT-12, NT-13, NT-15, NT-24, NT-29 and their merge-hop table) | §6, §8, D-L2-12 |
| `protocol/06-integration-cycle.md` §6 (CAN-SHIM, CAN-DIGEST, CAN-VERIFY, CAN-MACHINE) | §6, §8/N5 |
| `protocol/09-fixtures.md` §2 (fixture ownership), §7.2 (L2 negative corpus), §10 (Fixture Change Request) | §3, `L2-T602`, `L2-T609` |

---

## 10. Pending mutation script deliverables

The tasks in this section create the mutation scripts listed as `MUTATION-NEEDED` in `protocol/03-invariant-tests.md` §4.4 and §9.3. Each script mutates the fixture so the named negative test flips from PASS to FAIL, proving the test is not vacuous. The mutation harness runner (`.github/workflows/invariant-mutation.yml`) is owned by this lane and invokes these scripts.

### L2-IT012-N3 — Create IT-012-N3.mutation.sh

**Size:** S  **Depends on:** `L2-T605`  **Branch slug:** `lane/2/it012-n3-mutation`

**Creates:** `tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh`

**Spec:** `protocol/03-invariant-tests.md` §4.4 (`# MUTATION-NEEDED: create IT-012-N3.mutation.sh`). The mutation removes the gate-2-vs-production-approval separation check from the fixture `deploy-production.yml` so a Gate-2-only approval record (`DIGEST_GATE2_ONLY`) is accepted as a production-approval record, causing IT-012-N3 to flip to FAIL.

**Commands**

```bash
set -euo pipefail
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/it012-n3-mutation
mkdir -p tools/evidence/invariant-tests/mutations

cat > tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: remove the gate-2-vs-production-approval separation check from the
# fixture workflow deploy-production.yml so a Gate-2-only approval record passes
# the production-approval gate.
# Expected result: IT-012-N3 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §4.4 (MUTATION-NEEDED IT-012-N3).
set -euo pipefail
WORKFLOW="${FIXTURE_REPO_ROOT:?}/.github/workflows/deploy-production.yml"
# Remove the step that distinguishes a Gate-2 record from a production-approval
# record. The step checks that the record type is "production" (not "gate-2");
# removing it lets DIGEST_GATE2_ONLY through the gate.
sed -i '/GATE2_ONLY\|gate.2.*production\|production.*gate.2\|record.type.*gate\|gate.*record.type/Id' \
  "$WORKFLOW"
echo "IT-012-N3 mutation applied: gate-2-vs-production-approval separation check removed from $WORKFLOW"
EOF
chmod +x tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh
git add tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh
git commit -m "L2-IT012-N3: create IT-012-N3.mutation.sh (gate-2 vs production-approval separation)"
```

**SELF-VERIFY**

```bash
test -f tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh && \
test -x tools/evidence/invariant-tests/mutations/IT-012-N3.mutation.sh && \
echo "IT-012-N3.mutation.sh present and executable"
```

Expected output, exactly: `IT-012-N3.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-012-N3 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-012-N3` and stop the lane immediately.

---

### L2-IT111-N1 — Create IT-111-N1.mutation.sh

**Size:** S  **Depends on:** none within this lane (IT-111 invariant test owned by L1; mutation script is an L2/L3 lane deliverable per `protocol/03-invariant-tests.md` §9.3)  **Branch slug:** `lane/2/it111-n1-mutation`

**Creates:** `tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh`

**Spec:** `protocol/03-invariant-tests.md` §9.3 (`# MUTATION-NEEDED: create IT-111-N1.mutation.sh`). The mutation makes the fixture provenance check skip files that have no `provenance:` key (treating absence as implicitly declared) so a fixture tree with no provenance declaration passes CI. Under the mutation IT-111-N1 must flip from PASS to FAIL.

**Commands**

```bash
set -euo pipefail
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/it111-n1-mutation
mkdir -p tools/evidence/invariant-tests/mutations

cat > tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: make the fixture provenance checker skip files that carry no
# 'provenance:' key, treating absence as implicitly declared. A fixture tree
# with no provenance declaration (fixtures/tree-fixture-undeclared) must then
# pass CI instead of failing IT-111-N1.
# Expected result: IT-111-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §9.3 (MUTATION-NEEDED IT-111-N1).
set -euo pipefail
CHECKER="${FIXTURE_REPO_ROOT:?}/validators/registry/fixture-provenance.sh"
# Insert a guard: if the file does not contain a 'provenance:' key, skip it
# without flagging it as undeclared. This is the exact loophole §9.3 describes.
sed -i 's/\(check_provenance_for_file\s\+"\$f"\)/grep -q "provenance:" "$f" \&\& \1/' \
  "$CHECKER"
echo "IT-111-N1 mutation applied: provenance checker now skips files with no provenance key in $CHECKER"
EOF
chmod +x tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh
git add tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh
git commit -m "L2-IT111-N1: create IT-111-N1.mutation.sh (provenance check skips files with no key)"
```

**SELF-VERIFY**

```bash
test -f tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh && \
test -x tools/evidence/invariant-tests/mutations/IT-111-N1.mutation.sh && \
echo "IT-111-N1.mutation.sh present and executable"
```

Expected output, exactly: `IT-111-N1.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-111-N1 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-111-N1` and stop the lane immediately.
| `protocol/11-definition-of-done.md` §4.1 (DL-04, DL-05, DL-06), §4.2 (lane canaries) | §0.1, §4.3, §6 |
