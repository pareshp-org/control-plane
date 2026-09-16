# 00 — TEST STRATEGY

# The verification pyramid for the five-lane parallel build
# Authoritative for WHAT is tested, WHERE it runs, WHEN it runs, WHO owns it, and WHAT it blocks.
# Conforms to `Code/implementation/PARTITION.md` (FROZEN). Does not redesign the partition.

---

## 0. The one idea this document exists to enforce

> **A check that can only pass is not a check.**

Five low-cost AI developers build in parallel on five branches. None of them has full context. None of
them has judgment authority. The likeliest failure of this programme is not a merge conflict — the
partition makes those nearly impossible. The likeliest failure is that **a lane quietly builds the wrong
thing, ships a suite that asserts nothing, and every light stays green.**

The specification already names this failure three times and refuses it three times:

| Where the spec says it | What it says |
|---|---|
| §53.1, the seeded-canary rule | A permanent seeded drift record exists at all times and every reconciliation run MUST find it. *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking."* |
| AT-102 | *"A reconciler that finds nothing is assumed broken, never assumed clean."* A zero-finding run raises SIG-13 and triggers the gap procedure. |
| §31.2, the seeded-defect case | *"A verification contract that cannot fail is not a contract."* Every `verification/contract.yaml` declares a seeded-defect case the contract MUST fail; a run in which it passes is a FAILED run and raises SIG-18. |
| §95.4, the activation checklist | Each gate arms *"executed for real — including the negative tests — at each threshold, not assumed."* |
| §98.2, Phase 1 completion check | Machine-account approval, the non-default-branch production-secret attempt, and the malformed-exception rejection are each *"executed negatively"*. |
| §103 (metrics), review rejection rate | *"Very low may mean rubber-stamping; very high may mean weak plans."* |
| §99.6, risk 5 | *"An unavailable protection feature reproduces the silent-gate failure."* |

This document generalises those from features of the product into **the operating rule of the build
itself**. Every gate at every level of this pyramid carries a paired negative test that proves the gate
can fail. A level that runs with zero assertions is not clean — it is broken. A gate whose negative
fixture passes is not a gate — it is decoration, and it blocks the merge train until it discriminates
again.

---

## 1. The pyramid

Five levels. Each is narrower in scope and cheaper than the one above it, and each is a **precondition**
for the one above it, never a substitute.

```
                       ┌───────────────────────────────────┐
      T4               │  SPEC ACCEPTANCE  AT-001..AT-110   │  phase boundary → main
                       │  + 111 invariant classifications   │  owner: L0
                       ├───────────────────────────────────┤
      T3               │  INTEGRATION GATE                  │  end of each merge-train cycle
                       │  whole `integration` branch        │  owner: L0
                       ├───────────────────────────────────┤
      T2               │  CROSS-LANE CONTRACT TESTS         │  every lane PR + every train step
                       │  provider half + consumer half     │  owner: L0 owns fixtures; lanes own halves
                       ├───────────────────────────────────┤
      T1               │  LANE SUITE                        │  every push to lane/N/*
                       │  one lane's owned paths only       │  owner: the lane
                       ├───────────────────────────────────┤
      T0               │  TASK SELF-VERIFY                  │  every commit, on the dev's machine
                       │  one task                          │  owner: the lane AI developer
                       └───────────────────────────────────┘
      Tn (paired)      EVERY level above has a mandatory negative twin. See §4.
```

### 1.1 The level table — binding

| Level | Name | Scope | Runs where | Runs when | Owner | Blocks |
|---|---|---|---|---|---|---|
| **T0** | Task self-verify | Exactly one task's acceptance criteria | Developer machine, then GitHub Actions on push to `lane/N/*` | Every commit pushed to a lane branch | The lane AI developer who wrote the task's code | The developer's own claim of "done". A red T0 is a STOP rule: do not open a PR, open a blocker issue |
| **T1** | Lane suite | All of that lane's owned paths, per PARTITION §"The five build lanes" | GitHub Actions, on the lane PR into `integration` | On PR open and on every push to the PR head | The lane; reviewed by L0 | Merge of that lane's PR into `integration` |
| **T2** | Cross-lane contract tests | Every provider/consumer pair declared in `contracts/**` | GitHub Actions, on the lane PR **and** re-run on `integration` after each merge-train step | Every lane PR; every merge-train step | L0 owns the fixtures under `contracts/**`; each lane owns its own half of each pair | Merge into `integration`; a post-merge failure **halts the train** |
| **T3** | Integration gate | The whole `integration` branch as one system | GitHub Actions on `integration` | After the last merge of a train cycle (L1→L4→L2→L3→L5), and on a daily schedule | L0 Integrator | `integration` → `main` |
| **T4** | Spec acceptance | AT-001..AT-110 scheduled at or before the current Section 98 phase, plus the 111 invariant classifications of §101 | GitHub Actions on `integration`; the real-execution subset on the live estate | At each Section 98 phase completion check, and before every `main` merge that closes a phase | L0 Integrator, with a **named owner lane per AT** (§6) | Phase sign-off and the `main` merge for that phase |

### 1.2 What each level may NOT do

* **T0 may not import another lane's source.** PARTITION rule 4. A T0 that needs another lane's output consumes a fixture under `contracts/fixtures/**` or a published artifact.
* **T1 may not assert anything outside its lane's owned paths.** If a lane's suite fails because of another lane's file, the suite is wrong, not the other lane.
* **T2 may not be edited by a lane on both sides.** A lane owns exactly one half of any pair. Both halves in one lane means the contract is not a contract.
* **T3 may not be a re-run of T1.** T3 asserts properties that only exist when all five lanes are present.
* **T4 may not be reinterpreted to make it pass.** AT-090 states the rule for the whole catalogue: *"A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes."* An AT that cannot pass is a **defect report against the build**, escalated to L0 — never a wording change.

---

## 2. Where the tests live — the ownership rule that makes this mergeable

PARTITION rule 1 (one owner per path) and rule 3 (no shared mutable file) apply to test code exactly as
they apply to production code. Therefore:

**Every test lives inside the owned path of the lane that owns the thing under test.** There is no
top-level `tests/` directory. There is no shared test index, manifest, or registry-of-suites.

| Lane | Test root (inside its own owned tree) | Positive entry point | Negative entry point |
|---|---|---|---|
| L1 | `validators/registry/tests/` | `validators/registry/lane-verify.sh` | `validators/registry/lane-negative.sh` |
| L2 | `tools/evidence/tests/` | `tools/evidence/lane-verify.sh` | `tools/evidence/lane-negative.sh` |
| L3 | `reconciler/tests/` | `reconciler/lane-verify.sh` | `reconciler/lane-negative.sh` |
| L4 | `tools/records/tests/` | `tools/records/lane-verify.sh` | `tools/records/lane-negative.sh` |
| L5 | `ops-vm/tests/` | `ops-vm/lane-verify.sh` | `ops-vm/lane-negative.sh` |

The five entry-point paths above are **fixed by this document and never change**. They are the only
names L0's `Makefile` knows. A lane may organise everything beneath them freely.

**Cross-lane fixtures live under `contracts/fixtures/**`, which is L0-owned and FROZEN** (PARTITION
rule 2). This is deliberate and load-bearing: a lane cannot make a contract test pass by editing the
fixture. A lane that believes a fixture is wrong files a Contract Change Request. That single property
is what makes T2 capable of catching a lane that built the wrong thing.

**The runner is the L0 `Makefile`**, which PARTITION assigns to L0. It shells out to the five fixed
entry points. `.github/workflows/**` belongs to L2, so the workflows that invoke `make` are L2
deliverables built to the target names below; L0 owns the target names, L2 owns the triggers.

**Gate-run records are written by machines, not lanes.** `control-plane-records` is L4-owned for
*source* purposes. Record *instances* written at runtime by a workflow under the records-writer
credential (§97.1, D89) are not lane edits and do not violate path ownership. Gate runs land at
`records/gate-runs/<cycle>/<level>-<lane>.yaml`, one file per run, directory-per-item, never appended
to an index.

---

## 3. Exit codes — the vacuity rule

Every entry point at every level uses this exit-code contract. It is not advisory.

| Exit | Meaning | Treated as | Why it exists |
|---|---|---|---|
| `0` | PASS, with at least one assertion executed | Pass | — |
| `1` | FAIL — an assertion failed | Fail | Ordinary red |
| `2` | **VACUOUS** — the suite ran but executed zero assertions | **Fail**, distinct signal | §53.1: every reconciliation run records its per-registry comparison counts *"so that a silently narrowed comparison is itself visible drift"*. A suite that asserts nothing is the same failure. EC-109 names it: a run that completes "clean" while actually checking nothing. |
| `3` | **NON-DISCRIMINATING** — a negative fixture passed the gate | **Fail**, highest severity | AT-102 and §31.2 applied to the build. The instrument stopped discriminating. Blocks the lane from the merge train until fixed. |

Every entry point MUST print, as its last line on stdout, a machine-readable count:

```
GATE-RESULT gate=<GATE-ID> level=<T0|T1|T2|T3|T4> assertions=<n> failures=<n> negatives_run=<n> negatives_that_failed_correctly=<n>
```

The runner fails the level when `assertions == 0`, when `negatives_run == 0`, or when
`negatives_that_failed_correctly != negatives_run`. **Silence is never taken as health.**

---

## 4. THE NEGATIVE-TEST DOCTRINE — binding

### 4.1 The doctrine

1. **Every gate has an ID.** Format `GATE-L<n>-<nnn>`, e.g. `GATE-L3-001`. L0's gates use `GATE-L0-<nnn>`.
2. **Every gate has a declaration file** at `<owning-lane-path>/gates/<GATE-ID>.yaml`. One file per gate. Directory-per-item. No shared index — the index is computed by globbing.
3. **Every gate declaration MUST carry a `negative:` block** naming a fixture that the gate is required to reject, and the exit code the rejection produces.
4. **A gate whose negative fixture passes is a FAILED gate**, not a clean one, and is reported as exit `3`. The owning lane is blocked from the merge train until the negative fixture fails again.
5. **A gate with no negative block does not exist.** `make negative-audit` fails the build if any `gates/*.yaml` lacks one, if any named fixture directory is missing or empty, or if any negative fixture is byte-identical to its positive fixture.
6. **Negative fixtures are never repaired to make them fail.** If a fixture stops being rejected, the *gate* is broken. Editing the fixture to restore red is falsifying the instrument and is a STOP-rule escalation to L0.
7. **The doctrine is recursive.** `make negative-audit` itself has a negative test: `GATE-L0-001` plants a declaration file with a missing `negative:` block and asserts that the audit rejects it.
8. **`GATE-L<n>-<nnn>` is the only negative-test namespace** (FD-098, A3). `01-contract-tests.md`'s `N-<nn>`, `03-invariant-tests.md`'s `IT-<nnn>`, `04-negative-tests.md`'s `NT-<nn>`, `08-smoke-and-e2e.md`'s `NEG-<nn>`, `09-fixtures.md`'s `NEG-<DOMAIN>-<nnn>` fixture ids, and `11-definition-of-done.md`'s `DT`/`DP`/`DL`/`DI`/`DV`/`DG` checklist ids are non-canonical. `NEGATIVE-TEST-CONCORDANCE.md` maps every one of them onto its `GATE-L<n>-<nnn>` equivalent (or states why it has none) and cites exactly where each lives today.

### 4.2 The gate declaration schema

```yaml
# reconciler/gates/GATE-L3-001.yaml
gate_id: GATE-L3-001
owner_lane: L3
level: T1
title: Reconciliation run finds the seeded canary
enforces:
  spec_sections: ["53.1", "53.2"]
  acceptance_tests: ["AT-102", "AT-032"]
  invariants: [44]
  signals: ["SIG-13"]
positive:
  command: "./reconciler/lane-verify.sh --gate GATE-L3-001"
  expect_exit: 0
negative:
  fixture: "reconciler/tests/negative/GATE-L3-001/"
  command: "./reconciler/lane-negative.sh --gate GATE-L3-001"
  expect_exit: 1
  proves: "A reconciliation run whose comparison set has been narrowed so the canary is not compared reports zero findings and MUST be reported as a FAILED run, not a clean one."
assertion_count_min: 3
```

Every field is mandatory. `proves:` is a sentence, not a label: it states the specific wrong-build the
negative test would catch. `make negative-audit` fails on an empty or duplicated `proves:` string,
because five identical `proves:` lines is what rubber-stamping looks like in YAML.

### 4.3 The injected-defect drill — the anti-rubber-stamp control

The spec refuses to read a quiet gate as a healthy gate: *"zero rejections means the gates are not
working"* for the plan-checker, *"very low may mean rubber-stamping"* for review rejection rate. The
same reading applies to a lane whose PRs are never rejected.

**Once per merge-train cycle, L0 injects one known-bad change per lane** onto a throwaway branch
`drill/<cycle>/L<n>`, never onto the lane's own branch. The change is drawn from the lane's own
`gates/*.yaml` `proves:` statements. The lane's T1 suite MUST reject it.

| Outcome | Meaning | Action |
|---|---|---|
| T1 rejects the drill | The lane's suite discriminates | Record `pass` in `records/gate-runs/<cycle>/drill-L<n>.yaml`; no further action |
| T1 accepts the drill | The lane's suite does not discriminate | Exit `3`. The lane is **BLOCKED from the train** for this cycle. L0 opens a blocker issue naming the gate. The lane's next task is repairing the gate, not new feature work |
| No drill was run this cycle | The control itself was skipped | T3 fails. A cycle with no drill record is not a clean cycle |

**Standing rejection-rate reading, recorded per cycle, never punitive and never personal:**

| Observation over a full cycle | Reading | Response |
|---|---|---|
| A lane's PRs were rejected by no gate at any level | The gates are presumed non-discriminating, not the lane presumed perfect | Mandatory drill escalation: three injected defects next cycle instead of one |
| The plan-checker rejected zero plans | Per §30.2 and the spec's own reading, the checker is presumed broken | L0 runs the plan-checker's own negative fixtures before the next cycle |
| Code review produced zero findings across all five lanes | Rubber-stamping, per §103 | Recorded as an instrument signal on the cycle record; reviewer rotation for the next cycle |

---

## 5. Level detail — what runs, and what it blocks

### T0 — Task self-verify

**Owner:** the lane AI developer. **Blocks:** the developer's own "done", and PR creation.

Every task issued to a lane carries, per PARTITION §"AI developer profile", a self-verify command whose
output is unambiguous. T0 is the execution of exactly that command, plus the task's own negative case.

```bash
# run from the repository root, on the lane branch, before every commit
make selfverify LANE=3 TASK=phase3-reconciler-canary
```

Which resolves to, literally:

```bash
./reconciler/lane-verify.sh  --task phase3-reconciler-canary   # must exit 0
./reconciler/lane-negative.sh --task phase3-reconciler-canary  # must exit 1
```

**STOP rule for the lane developer.** If `lane-verify.sh` exits `2` (vacuous) or `lane-negative.sh`
exits `0` (non-discriminating), **do not commit, do not open a PR, do not "fix" the negative fixture**.
Open a blocker issue titled `BLOCKER L<n> <GATE-ID> non-discriminating` and stop work on the task.

### T1 — Lane suite

**Owner:** the lane, reviewed by L0. **Blocks:** the lane PR merging into `integration`.

```bash
make lane LANE=3
```

Runs, in order:

```bash
./reconciler/lane-verify.sh   --all || exit 1   # every gate declared under reconciler/gates/; must exit 0
./reconciler/lane-negative.sh --all; neg=$?; [ "$neg" -eq 1 ] || exit 3   # every negative fixture named by those gates; a healthy, discriminating run exits 1
make negative-audit LANE=3 || exit 1            # every gate has a negative; none is vacuous or duplicated
make lane-guard LANE=3 || exit 1                # no file outside reconciler/**, tools/provision/**, validators/drift/**
```

T1 passes only when all four pass, `assertions > 0`, and `negatives_that_failed_correctly == negatives_run`.

`make lane-guard` is the mechanical form of PARTITION rule 1. It has its own negative test
(`GATE-L0-002`): a fixture branch touching a foreign path that the guard MUST reject.

### T2 — Cross-lane contract tests

**Owner:** L0 owns `contracts/fixtures/**`; each lane owns its own half. **Blocks:** merge into
`integration`; a failure after a train step halts the train.

```bash
make contract-tests             # all pairs
make contract-tests PAIR=CT-03  # one pair
```

| Pair | Provider (writes the shape) | Consumer (reads the shape) | What the fixture proves | Spec anchor |
|---|---|---|---|---|
| CT-01 | L1 `schemas/product/**` | L2 workflow contract validation | A `product.yaml` valid against the frozen fixture validates in CI, and a fixture violating `contract_version` is rejected | §15.5, §98.2 Phase 3 |
| CT-02 | L1 `registries/**` schemas | L3 reconciler comparison set | Every registry row the reconciler claims to compare is present in the schema, and the run reports its per-registry comparison count | §53.1 |
| CT-03 | L4 `schemas/records/deployments` | L2 `deploy-production.yml` | The deploy workflow writes a record that validates, and a deploy whose record write fails is a FAILED deploy, not a warning | §97.2 |
| CT-04 | L4 event envelope (`events/`, one file per event) | L2 every workflow | Every workflow emits an event that validates; an event write is a required, failing step | §97.1, §97.2 |
| CT-05 | L5 `access/**` permission model | L3 reconciler | The declared permission matrix is exactly what the reconciler compares against; a stricter-than-declared production control is raised, never relaxed | AT-033, invariant 81 |
| CT-06 | L2 evidence chain | L4 record stores | All eleven questions of §32 are answerable from records alone, with items 5 and 11 matching | §32, invariant 22 |
| CT-07 | L1 capability list | L5 access provisioning | `people-intelligence` is present and marked non-delegable; an assignment granting it fails validation | AT-090, AT-091, invariant 106 |
| CT-08 | L3 drift-finding shape | L4 record store | Every finding carries `acknowledged_by` and `acknowledged_at`; a finding without them is rejected | §53.1 |
| CT-09 | L2 required-status-check context names | L3 branch-protection template | Every context named in the template is emitted by a real job carrying no `if:` and no path filter; a `skipped` or `neutral` conclusion on a required context is Blocking | §33.2 |
| CT-10 | L1 invariant classification map | L4 `policies.yaml` / gate index | Each of the 111 invariants is exactly one of mechanical / policy / review-held; a `mechanical` one naming no live gate id and no AT id fails CI | §101 preamble |

**Every pair carries its own negative fixture** as `contracts/fixtures/<CT-ID>/invalid-NNN.yaml`,
owned by L0 and frozen — the flat layout `lanes/L0-01-phase-0-contracts.md` actually builds, with no
`negative/` subdirectory. CT-10's negative fixture is an invariant carrying no classification at all —
the exact omission §101 says nothing would otherwise detect.

### T3 — Integration gate

**Owner:** L0 Integrator. **Blocks:** `integration` → `main`.

```bash
make gate-integration CYCLE=2026-W36
```

The gate is the literal conjunction of these ten checks. All ten must pass. There is no partial pass and
no override that is not a recorded exception with an expiry (invariant 77).

| # | Check | Fails when | Anchor |
|---|---|---|---|
| 1 | All five `lane-verify.sh --all` green | Any exits non-zero, or any reports `assertions=0` | §3 |
| 2 | All ten CT pairs green | Any pair fails, either half | §5 T2 |
| 3 | `make negative-audit` green across all five lanes and L0 | Any gate lacks a negative, any negative fixture is empty, duplicated, or passes | §4 |
| 4 | `make lane-guard --cycle` green | Any PR merged this cycle touched a foreign path | PARTITION rule 1 |
| 5 | Assertion-count ratchet | Total `assertions` across all levels is lower than the previous `integration` tag's total | Prevents quiet deletion of tests |
| 6 | Invariant classification completeness | Fewer than 111 invariants classified, or a `mechanical` one names no live gate/AT | §101 preamble |
| 7 | AT coverage map current | Any AT scheduled at or before the current Section 98 phase has no runnable command or no last-run result | §100 preamble |
| 8 | No `skipped` / `neutral` on any required context of any merged PR | Any occurs | §33.2 |
| 9 | **The seeded canary was found** | The reconciler's run reported zero findings, canary included | AT-102, §53.1 |
| 10 | **The seeded-defect verification case failed** | Any `verification/contract.yaml` seeded-defect case passed on its last run | §31.2, SIG-18 |
| 11 | Drill record present for all five lanes this cycle | Any lane has no `drill-L<n>.yaml` for the cycle | §4.3 |

Checks 9, 10 and 11 are the negative-test doctrine expressed as the release gate: they are the three
checks that fail when everything else looks green.

**On T3 failure:** the train stops where it is. `integration` is not merged to `main`. The failing
check names one lane; that lane's next task is the fix. No lane merges ahead of a stopped train — the
merge order L1 → L4 → L2 → L3 → L5 exists because of dependency order (PARTITION §"Dependency order"),
and reordering around a failure ships the dependency inversion the order exists to prevent.

### T4 — Spec acceptance tests

**Owner:** L0 Integrator, with a named owner lane per AT. **Blocks:** phase sign-off and the `main`
merge closing that phase.

```bash
set -euo pipefail
make acceptance PHASE=3            # every AT whose phase <= 3
make acceptance AT=AT-102          # one test
make acceptance PHASE=3 NEGATIVE=1 # the paired negative for every AT in scope
```

Per §100: *"Each test is verified at the implementation phase where the capability it exercises
activates."* The AT coverage map at `contracts/acceptance/AT-<nnn>.yaml` (L0-owned, frozen) carries for
each of the 110 tests: `phase`, `owner_lane`, `command`, `negative_command`, `executed_for_real`.

`executed_for_real: true` marks the ATs the spec requires to be executed on the live estate rather than
simulated — AT-108, AT-109 and AT-110 say so explicitly (AT-110: *"Executed for real at the phase that
builds the reconciler and re-executed at every rotation"*), as does §95.4's activation checklist. For
these, a green simulated run is not a pass.

---

## 6. Ownership map — which lane owns which acceptance tests

A lane owns an AT when the AT's pass condition is satisfied inside that lane's owned paths. L0 owns
every AT that spans lanes. No AT is unowned.

<!-- AUTHORITY NOTE (FD-037): protocol/02-acceptance-mapping.md is the authoritative AT→owner map. Rows here that conflict with protocol/02 are superseded. -->
| Owner | Acceptance tests owned | Representative |
|---|---|---|
| **L1** Registries & Contracts | AT-001, AT-002, AT-005, AT-007, AT-008, AT-009, AT-010, AT-013, AT-015, AT-016, AT-019, AT-020, AT-021, AT-036, AT-037, AT-038, AT-047, AT-049, AT-051, AT-071, AT-074, AT-075, AT-077, AT-078, AT-087 | AT-049 — a product declaring `ai_runtime_dependency` without an evaluation suite fails CI |
| **L2** Pipeline & Evidence | AT-023, AT-024, AT-025, AT-026, AT-027, AT-030, AT-034, AT-035, AT-103, AT-107 | AT-103 — production restore executes end to end with no credential typed by a human |
| **L3** Reconciler & Provisioning | AT-017, AT-018, AT-022, AT-032, AT-033, AT-102, AT-110 | AT-102 — the seeded reconciliation canary |
| **L4** Records, Events & Metrics | AT-040, AT-044, AT-046, AT-048, AT-050, AT-052, AT-053, AT-054, AT-059, AT-073, AT-084, AT-085, AT-086, AT-088, AT-104, AT-105 | AT-088 — source re-read failure never downgrades verified content |
| **L5** Access, Infra & Ops | AT-028, AT-029, AT-031, AT-089, AT-090, AT-091, AT-092, AT-093, AT-094, AT-095, AT-096, AT-097, AT-098, AT-099, AT-100, AT-108, AT-109 | AT-097 — no people datasource in the shared Grafana provisioning, verified in the provisioned configuration, not inferred from panel visibility |
| **L0** Integrator (cross-lane) | AT-003, AT-004, AT-006, AT-011, AT-012, AT-014, AT-039, AT-041, AT-042, AT-043, AT-045, AT-055, AT-056, AT-057, AT-058, AT-060, AT-061, AT-062, AT-063, AT-064, AT-065, AT-066, AT-067, AT-068, AT-069, AT-070, AT-072, AT-076, AT-079, AT-080, AT-081, AT-082, AT-083, AT-101, AT-106 | AT-101 — three simultaneous SEV-1s; spans people, incident and topology surfaces |

**AT-034 (governance layerability) is L2-owned and T3-gated**, because it is the test that proves the
delivery core still runs with the removable governance artifacts removed — it can only be executed on
`integration`, with all five lanes present.

---

## 7. Representative gate catalogue

Each lane declares its own gates. This is the required minimum set per lane at the point its lane suite
first arms. Each row becomes a `gates/<GATE-ID>.yaml` file with a mandatory negative fixture.

### L1 — Registries & Contracts

| Gate | Asserts | Negative fixture MUST be rejected | Anchor |
|---|---|---|---|
| GATE-L1-001 | An exception without an expiry fails CI | `exceptions.yaml` entry with owner and trigger but no `expiry` | invariant 77, AT-036, AT-037, §98.2 Phase 1 |
| GATE-L1-002 | An assignment naming a departed or nonexistent person fails CI | Assignment referencing a `departed` person | invariant 7, AT-017 |
| GATE-L1-003 | A `restore_tested` date older than the rolling 90-day window fails CI | Contract with a 100-day-old date | invariant 4, invariant 3 |
| GATE-L1-004 | A 24x7 `coverage_window` not covered by active rota members fails contract validation | Contract declaring 24x7 with a two-person weekday rota | invariant 31, AT-047 |
| GATE-L1-005 | An invariant carrying no enforcement classification fails CI | Classification map with invariant 44 unclassified | §101 preamble, CT-10 |
| GATE-L1-006 | `ai_runtime_dependency` without an evaluation suite under `verification/` fails CI | Product declaring the block with an empty `verification/` | AT-049 |
| GATE-L1-007 | An authority delta with no linked decision-record ID in the same commit fails CI | Commit adding a Write-conferring assignment, no decision ID | §26.4 |
| GATE-L1-008 | No product list appears in any schema, validator or dashboard source | Validator with a hard-coded eight-product array | AT-001, AT-013, invariants 51, 52 |
| GATE-L1-009 | An assignment granting `people-intelligence` fails validation | Delegate assignment granting it | AT-090, invariant 106 |
| GATE-L1-010 | Banned surveillance measurements are absent from the schema and rejected if introduced | Schema adding a keystroke-count field | AT-075, invariants 96, 97 |

### L2 — Pipeline & Evidence

| Gate | Asserts | Negative fixture MUST be rejected | Anchor |
|---|---|---|---|
| GATE-L2-001 | A production deploy whose digest differs from the staging-verified digest is rejected | Deploy request with a rebuilt digest | invariant 22, invariant 23, §32 |
| GATE-L2-002 | Every required check name is emitted by a job carrying no `if:` and no path filter | Workflow whose required-context job carries a path filter | §33.2, CT-09 |
| GATE-L2-003 | The verification contract's seeded-defect case FAILS the contract | Contract of the form `verify: exit 0` mapped to every requirement | §31.2, SIG-18 |
| GATE-L2-004 | Privileged workflows fail closed when `github.actor` is not a capability-holding human in `people.yaml` | Machine account dispatching `deploy-production.yml` | invariant 18, §37.3 |
| GATE-L2-005 | A workflow on a non-default branch declaring `environment: production` obtains no environment secret | Branch workflow requesting the production environment | invariant 25, §98.2 Phase 1 |
| GATE-L2-006 | Time gates resolve against the declared working calendar, never runner local time | Friday-freeze test with a runner clock set to Thursday UTC-12 | §97.1, §34.2 |
| GATE-L2-007 | A moved `workflows/*` tag is Blocking drift | Tag repointed to a new SHA with no PR | invariant 72, invariant 85, §53.1 |
| GATE-L2-008 | All eleven evidence-chain questions are answerable for one real deployment | Deployment whose record write step was best-effort and silently failed | §32, §98.2 Phase 6, CT-06 |

### L3 — Reconciler & Provisioning

| Gate | Asserts | Negative fixture MUST be rejected | Anchor |
|---|---|---|---|
| GATE-L3-001 | Every reconciliation run finds the seeded canary; zero findings is a FAILED run raising SIG-13 | Run whose comparison set excludes the canary and reports clean | **AT-102**, §53.1, EC-109 |
| GATE-L3-002 | Every run records its per-registry comparison counts | Run emitting findings but no counts | §53.1 |
| GATE-L3-003 | Auto-repair moves only toward the declared, stricter state | Repair class that relaxes a stricter-than-declared production control | AT-033, invariant 81 |
| GATE-L3-004 | The reconciler credential is bounded: six named write attempts all fail, then a normal run still completes | Credential that can write a `records/**` file | **AT-110**, §99.6 risk 6 |
| GATE-L3-005 | An expired assignment is revoked with no human action | Expired assignment still holding Team membership after a run | AT-018, AT-036, invariant 58 |
| GATE-L3-006 | Blocking orphans cannot be dismissed unresolved | Dismissal of a product with no active Primary Owner | AT-017, invariant 57, SIG-05 |
| GATE-L3-007 | The independent control verifier runs off the operations VM under a different credential; its absence for one cycle is Level 5 | Verifier configured to run on the ops VM under the reconciler credential | §53.1 |
| GATE-L3-008 | `create-product` and `add-person` complete with zero hand-editing | Scaffold run leaving a CODEOWNERS file requiring manual edit | AT-001, AT-002, invariants 53, 54, 79 |
| GATE-L3-009 | A merged registry change reaches the declared canary set only, for one cycle | Registry edit applied fleet-wide on the first run | §26.4, invariant 72 |

### L4 — Records, Events & Metrics

| Gate | Asserts | Negative fixture MUST be rejected | Anchor |
|---|---|---|---|
| GATE-L4-001 | A store past its declared write-freshness interval is Amber, and Blocking for `events/`, `records/deployments/`, `records/uat/` | `events/` with no write for twice its interval, reported green | §97.2, §53.1 |
| GATE-L4-002 | A count-shaped metric reading zero against a stale store is a failure, not health | Zero ready-queue misses derived from a store that has not been written | §97.2, §52.3 |
| GATE-L4-003 | The records-writer credential is scoped to the records repository alone and reaches no registry | Token with `contents: write` on `control-plane` | §97.1 D89, invariant 18 |
| GATE-L4-004 | Records are append-only; corrections are follow-up records, never in-place edits | Commit editing an existing incident record in place | invariant 47, invariant 48, AT-088 |
| GATE-L4-005 | Every dashboard metric names the record store it derives from | Panel deriving from a hand-maintained number | §97.1, invariants 46, 49 |
| GATE-L4-006 | No customer data in records; references are by identifier only | Support record embedding a customer email body | invariant 111, §22.2, §96.6 |
| GATE-L4-007 | Every record carries `record_schema_version`, `id`, `product`, `timestamp` | Record missing `record_schema_version` written from Phase 1 onward | §97.2 |
| GATE-L4-008 | Manual results reach stores only through RECORD-VERIFICATION-RESULT | A hand-edited `records/uat/` file reporting a pass | §97.2 |

### L5 — Access, Infra & Ops

| Gate | Asserts | Negative fixture MUST be rejected | Anchor |
|---|---|---|---|
| GATE-L5-001 | Layer B is unreachable from general surfaces by any path | Shared-instance query path resolving to Layer B data | AT-089, invariant 109 |
| GATE-L5-002 | No people datasource entry and no dashboard reference exists in the shared Grafana provisioning | Provisioned config carrying a hidden people datasource | AT-097, D75 |
| GATE-L5-003 | The Founder-only instance requires its own credential; a shared login grants nothing | Shared-instance session reaching the Founder instance | AT-098 |
| GATE-L5-004 | `people-intelligence` gates Layer B; grant opens and expiry closes access through reconciliation | Expired delegate assignment retaining access | AT-091, invariant 106 |
| GATE-L5-005 | The Team Lead is denied at both the dashboard and the datasource layer | Team Lead reaching a Founder people view at the datasource | AT-092, AT-093 |
| GATE-L5-006 | The founder ops console is provably read-only: four attempts fail, then a read query still answers | Console able to mutate a board | AT-108, D69, D71 |
| GATE-L5-007 | The background cage egress wall holds at the host layer, and the systemd wall-clock stop terminates the process at the window boundary | Egress blocked only by harness configuration | AT-109 |
| GATE-L5-008 | `env \| grep -i api_key` returns empty on every machine, including shell profiles and repository `.env` files | Machine with a key in a shell profile | invariant 84, §36.6, §98.2 Phase 1 |
| GATE-L5-009 | The operations VM rebuilds from GitHub in under 4 hours | Rebuild depending on an unbacked-up local file | §99.6 risk 10, invariants 75, 76 |
| GATE-L5-010 | Every expiry-tracked asset carries an owner, an expiry and a configurable-lead alert; owners appear in orphan detection | Certificate entry with an expiry and no owner | §49.1, SIG-05 |

---

## 8. Merge-train interaction — what blocks what, in order

The train order is fixed by PARTITION: **L1 → L4 → L2 → L3 → L5**, once per cycle.

```bash
set -euo pipefail
# L0 runs this at each train step, in order. It is the whole protocol.
make gate-step CYCLE=2026-W36 LANE=1
make gate-step CYCLE=2026-W36 LANE=4
make gate-step CYCLE=2026-W36 LANE=2
make gate-step CYCLE=2026-W36 LANE=3
make gate-step CYCLE=2026-W36 LANE=5
make gate-integration CYCLE=2026-W36
```

Each `make gate-step` is:

```bash
set -euo pipefail
make lane LANE=$LANE                      # T1 + negative audit + lane guard
make contract-tests                       # T2, all pairs, both halves
git -C . merge --no-ff "lane/$LANE/<descriptive-slug>"   # only if the two above are green
make contract-tests                       # T2 again, post-merge, on integration
```

| Failure point | Blocks | Who fixes | Train state |
|---|---|---|---|
| T0 red | The task | The lane developer | Not started |
| T1 red | That lane's PR | The lane | Train waits at this lane |
| T1 exit `3` | That lane, for the whole cycle | The lane, gate repair first | Lane skipped; cycle continues without it |
| T2 red pre-merge | That lane's PR | The lane that owns the failing half | Train waits |
| T2 red post-merge | **The train** | L0 decides which half is wrong; only the owning lane edits | Train halted, `integration` frozen |
| T3 red | `integration` → `main` | The lane the failing check names | Train complete, release blocked |
| T4 red | Phase sign-off | The AT's owner lane, per §6 | Phase not closed |
| Missing drill record | T3 check 11 | L0 | Release blocked |

**A lane never merges another lane's branch and never rebases another lane's branch** (PARTITION
§"Branch & merge model"). A T2 post-merge failure is resolved by the owning lane on its own branch and
re-entered at the next train step, never by an integrator editing lane source.

---

## 9. STOP rules — for the lane AI developer

These are absolute. They require no judgment, which is the point.

| If | Then |
|---|---|
| `lane-verify.sh` exits `2` (vacuous) | Do not commit. Open `BLOCKER L<n> vacuous-suite`. Stop. |
| `lane-negative.sh` exits `0` (a negative fixture passed) | Do not commit. Do not edit the fixture. Open `BLOCKER L<n> <GATE-ID> non-discriminating`. Stop. |
| A gate you were asked to build has no obvious way to fail | Do not build it. Open `BLOCKER L<n> gate-cannot-fail <description>`. Stop. A gate with no failure mode is not a gate. |
| A test requires touching a path your lane does not own | Do not touch it. Open a Contract Change Request. Stop. |
| A contract fixture under `contracts/fixtures/**` appears wrong | Do not edit it. Open a Contract Change Request. Stop. |
| An acceptance test AT-xxx cannot pass on what you built | Do not reinterpret the test. Open `BLOCKER L<n> AT-xxx unsatisfiable`. Stop. (AT-090 states why.) |
| Making a test pass would require deleting or weakening another test | Stop. The assertion ratchet (T3 check 5) will reject it anyway. |

---

## 10. Recording — what every run writes

One file per run. Directory-per-item. No shared index. Written by the workflow under the records-writer
credential, never hand-edited (§97.1, §97.2).

```yaml
# records/gate-runs/2026-W36/T1-L3.yaml
record_schema_version: 1
id: GATERUN-2026-W36-T1-L3
product: control-plane
timestamp: 2026-09-03T09:14:22+00:00
cycle: 2026-W36
level: T1
lane: L3
result: pass                 # pass | fail | vacuous | non-discriminating
assertions: 214
failures: 0
negatives_run: 9
negatives_that_failed_correctly: 9
gates_executed: [GATE-L3-001, GATE-L3-002, GATE-L3-003, GATE-L3-004, GATE-L3-005,
                 GATE-L3-006, GATE-L3-007, GATE-L3-008, GATE-L3-009]
canary_found: true
drill: records/gate-runs/2026-W36/drill-L3.yaml
```

`canary_found: false` on any run is a FAILED run under AT-102, raises SIG-13, and triggers the gap
procedure — it is never recorded as clean, and never recorded as a skipped check.

---

## 11. The closing rule

Everything above reduces to one sentence, and every lane developer is expected to be able to recite it:

> **A green run with zero assertions, a gate with no negative fixture, a reconciliation that found
> nothing, a verification contract whose seeded defect passed, a lane whose PRs were never rejected,
> and a review with no findings are all the same event: the instrument stopped looking.**
>
> **None of them is a pass.**
