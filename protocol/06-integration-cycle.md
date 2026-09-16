# 06 — The Integration Cycle

**Owner: L0 Integrator. Binding on all five lanes.**
Conforms to `Code/implementation/PARTITION.md` (FROZEN). Nothing here redesigns the partition.
Spec anchor: `Research/MultiProduct_MasterSpec_v4.0.md` — Section 100 (110 acceptance tests, AT-001…AT-110), Section 101 (111 invariants), Section 53 (reconciliation and the seeded canary), Section 31.2 (the seeded-defect case), Section 30.2 (plan-checker hard rejects), Section 52 (SIG-01…SIG-46), Section 94 (operating rhythm), Section 46.1 (degraded mode).

---

## 1. Why this file exists

Five low-cost AI developers build in parallel. None of them holds full context. None of them has judgment authority (PARTITION, *AI developer profile*). The consequence is stated plainly so nobody has to infer it:

> **The merge protocol is the only instrument that can detect a lane that quietly built the wrong thing.** No human is reading five branches daily. If the gate does not catch it, nothing catches it.

And therefore the load-bearing rule of this whole document, carried directly from the specification:

> **A check that can only pass is not a check.**
> Section 53.1: a reconciliation run that reports zero findings — the deliberately seeded canary included — is a **FAILED** run, not a clean one. AT-102 makes this an acceptance test.
> Section 31.2: "A verification contract that cannot fail is not a contract." A run in which the seeded defect passes is a **FAILED** run.
> Section 103.9: a review rejection rate that is very low "may mean rubber-stamping."
> Section 30.2: the plan-checker exists to reject; a checker that has never rejected has not been shown to work.

Every gate in the cycle below is therefore paired with a **planted defect that the gate must reject**. A gate with no such pairing is not armed, and this document treats it as absent.

---

## 2. The cycle clock

One cycle = one working day. Times are the estate's local working clock, anchored to the machine/human day of Section 94.2. The five lanes and L0 run to this clock; nothing in the train is "when it's ready."

| Slot | Window | Duration | Owner | Step |
| --- | --- | --- | --- | --- |
| Nightly re-verify | 02:00 | ~25 min | CI | **C0** — full gate re-run on unchanged `integration` HEAD |
| Cycle open | 09:30 | 10 min | L0 | **C1** — publish cycle id, post previous cycle's report, publish blocker verdicts |
| Build window | 09:40–13:00 | 3h 20m | L1–L5 | **C2** — lanes build on `lane/N/*`, self-verify locally |
| Freeze | 13:00 | instant | L0 | **C3** — PR-open cutoff; anything not open and green rides the next cycle |
| Rebase window | 13:00–13:20 | 20 min | L1–L5 | **C4** — each lane rebases its own branch on `integration` HEAD |
| Merge train | 13:20–14:30 | 5 × 12 min + buffer | L0 | **C5** — merge in fixed order **L1 → L4 → L2 → L3 → L5** |
| Integration gate | 14:30–15:05 | 35 min | CI | **C6** — full positive suite on merged HEAD |
| Negative gate | 15:05–15:15 | 10 min | CI (from `main`) | **C7** — the canary run; every gate must reject its planted defect |
| Report | 15:15–15:30 | 15 min | L0 (generated) | **C8** — the daily integration report |
| Promotion | 15:30–15:45 | 15 min | L0 | **C9** — `integration` → `main`, or a recorded refusal |
| Triage | 15:45–16:15 | 30 min | L0 | **C10** — blocker triage, deadlock arbitration |
| Seeding | 16:15–16:30 | 15 min | L0 | **C11** — next cycle's tasks written and assigned |

The 13:00 freeze is deliberately the same cutoff Section 26.1 gives Gate 1 ("a plan submitted before 13:00 is decided the same working day"). Friday inherits the Section 94.8 **15:00 deployment freeze**: on Friday, C9 runs at 14:30 or `main` is not touched that week.

**Wall-clock budget for a healthy cycle: 2 hours 15 minutes of train time (C3→C11).** A cycle whose train time exceeds 4 hours is a sick cycle by definition (§7).

---

## 3. The cast

| Actor | Type | Authority in the cycle | Never does |
| --- | --- | --- | --- |
| **L0 Integrator** | Human | Merges the train, arbitrates blockers and deadlocks, plants and verifies canaries, promotes to `main`, amends tasks | Writes lane code |
| **L1–L5** | AI developer | Builds inside owned paths, opens one PR per cycle, files blockers with reproducing commands | Merges anything; rebases another lane; edits `contracts/**`; edits a foreign path; plants or removes a canary |
| **lane-guard** | CI check | Fails any lane PR touching a foreign path | — |
| **integration-gate** | CI job | Runs the positive suite on merged HEAD | — |
| **canary-run** | CI job, executed from `main`'s copy of the tooling | Proves every gate can fail | — |
| **train-report** | Generator | Writes the machine record; humans write only the judgment lines | Invents a number |

Roles, not people (Section 94.1). "Machines write measurable state; humans write meaning" — invariant 40, Section 94.9. The report generator fills every derivable field; L0 writes only the verdict and the reasons.

---

## 4. Where the train's own machinery lives

The partition is frozen, so the train tooling is placed where it collides with nothing.

| Path | Owner | Contents |
| --- | --- | --- |
| `Makefile` | L0 (PARTITION: root files, `Makefile`) | `train-*` targets — the entry points |
| `tools/train/**` | **L0** | Gate logic, canary fixtures, deadlock detector, report generator |
| `docs/train/**` | L0 (PARTITION: `docs/**`) | The human-readable daily reports |
| `.github/workflows/integration-gate.yml` | **L2** (PARTITION: `.github/workflows/**`) | A shim, six lines, that does nothing but `make train-gate` |

`tools/train/**` appears in no lane's row in the frozen table. Under PARTITION rule 1 ("one owner per path") an unclaimed path falls to L0 as integrator. This adds nothing to any lane's ownership and removes nothing from it. The lane-guard configuration must list `tools/train/**` as L0-owned so that a lane PR touching it fails.

**The shim problem, stated because it is exactly the failure this document exists to prevent.** L2 owns `.github/workflows/**`, so L2 authors the workflow file that invokes the gate that judges L2. A shim quietly rewritten to `exit 0` is a check that can only pass. Mitigations, both required:

1. The shim carries no logic. All gate logic lives in L0's `Makefile` and `tools/train/**`.
2. **CAN-SHIM** (§6) is a commit that MUST fail the gate. If the shim was gutted, CAN-SHIM passes, and a passing CAN-SHIM freezes the train. This is Section 53.1's independent-control-verifier reasoning transposed: *no control that can be rewritten by the party it checks is a control.*

The canary job runs `tools/train/` **as checked out from `main`**, not from the branch under test — the same separation Section 53.1 requires of the second verifier ("off the operations VM and under a different credential").

The daily report is written to `docs/train/` and `tools/train/state/`, **not** to `records/**`. `records/**` is L4's deliverable. An instrument that records its own health inside the artefact it is measuring cannot report that artefact's absence. Once L4's record stores pass their acceptance tests and `integration` has promoted to `main` three cycles running, L0 may mirror the reports into `records/` — mirror, never move.

---

## 5. The cycle, step by step

### C0 — Nightly re-verify (02:00, ~25 min, CI)

Runs the full positive suite against **unchanged** `integration` HEAD. Nothing merged since the last run; the tree is byte-identical. A failure therefore means the environment rotted, not that a lane broke something — a pinned action moved, a registry went away, a fixture expired.

```bash
set -uo pipefail
git fetch origin
git checkout --detach origin/integration
make train-verify-full 2>&1 | tee tools/train/state/nightly-$(date -u +%F).log
nightly_exit="${PIPESTATUS[0]}"
echo "nightly_exit=${nightly_exit}"
exit "$nightly_exit"
```

A red C0 freezes the cycle at C1: no lane merges until L0 records the cause. Pins are invariant 85 (GSD by tag, actions by full commit SHA, reusable workflows by pinned tag); a green tree that goes red overnight usually means a pin was not a pin.

### C1 — Cycle open (09:30, 10 min, L0)

```bash
make train-open CYCLE="$(date -u +%F)"
```

Emits, to the channel every lane reads:

* the cycle id;
* yesterday's report (`docs/train/CYCLE-<prev>.md`);
* the verdict on every blocker filed yesterday — **every blocker gets a written verdict inside one cycle**, including "not a blocker, here is why";
* the task list per lane, from C11 of the previous cycle.

A lane that receives no task list does not invent one. It re-runs its self-verify, posts the result, and waits. Inventing work is how a lane quietly builds the wrong thing.

### C2 — Build window (09:40–13:00, 3h 20m, lanes)

Each lane works on exactly one branch, `lane/N/<phase>-<task>`, short-lived (PARTITION: < 1 day). Before opening a PR, the lane runs its own self-verify — the unambiguous command its task specifies:

```bash
set -euo pipefail
make lane-verify LANE=3          # exits 0 or non-zero; no interpretation required
make lane-guard  LANE=3          # proves this branch touches only lane 3 paths
git diff --name-only origin/integration...HEAD | sort
```

A lane that cannot get `make lane-verify` to exit 0 does **not** open a PR. It files a blocker (§10) and stops. This is the STOP rule the AI developer profile requires.

### C3 — Freeze (13:00, L0)

At 13:00 the train takes what is open and green. Anything else rides tomorrow.

```bash
make train-freeze CYCLE="$(date -u +%F)"   # snapshots eligible PRs, one per lane, into tools/train/state/
```

Eligibility, all four required:

1. exactly one open PR from that lane;
2. `lane-guard` green;
3. `lane-verify` green on the PR head;
4. the PR body declares its **claimed AT ids and invariant numbers** (§8).

A lane with two open PRs is not partly eligible. L0 closes the later one and it rides tomorrow. Two PRs from one lane in one cycle is how merge order stops meaning anything.

### C4 — Rebase window (13:00–13:20, 20 min, lanes)

Each lane rebases **its own** branch. A lane never rebases another lane's branch (PARTITION).

```bash
set -euo pipefail
git fetch origin
git rebase origin/integration          # on your own lane/N/* branch only
make lane-verify LANE=N                # must still exit 0 after the rebase
git push --force-with-lease
```

`--force-with-lease`, never `--force`. A rebase that produces a conflict is a partition violation until proven otherwise: PARTITION rule 3 ("no shared mutable file, ever") means clean lane work *cannot* conflict. A conflict in this window is reported to L0 immediately and is triaged at C10 as a suspected rule-3 breach — not resolved by the lane.

### C5 — Merge train (13:20–14:30, 12 min per lane, L0)

Fixed order, dependency order, no exceptions: **L1 → L4 → L2 → L3 → L5**.

```bash
set -euo pipefail
for LANE in 1 4 2 3 5; do
  make train-merge LANE="$LANE" CYCLE="$(date -u +%F)" || echo "L$LANE reverted, train continues"
done
```

`train-merge` performs, per lane, in this order:

1. re-assert `lane-guard` on the merge result, not only on the branch;
2. merge to `integration` with `--no-ff` (every lane merge stays visible in history — invariant 47, append-only);
3. run the **smoke tier** of the gate (≤ 3 min): schema validation, contract stub compile, the lane's own claimed ATs;
4. on failure: `git revert -m 1 <merge>` immediately, and the train **continues to the next lane**.

**The train does not stop for one lane.** A lane whose merge is reverted is out for that cycle and its blocker is triaged at C10. Halting the whole train on one lane's failure is how four healthy lanes get punished for one sick one — and it is how a stalling lane becomes invisible, because the cycle stops producing evidence.

### C6 — Integration gate (14:30–15:05, 35 min, CI)

The full positive suite on merged HEAD.

```bash
make train-gate CYCLE="$(date -u +%F)"
```

| Tier | What runs | Budget | Fail-mode |
| --- | --- | --- | --- |
| G-1 Structure | lane-guard over the whole diff; no foreign-path write survived the train | 1 min | fail-closed |
| G-2 Schema | every registry and contract fixture validated against every supported schema version (subsystem B) | 4 min | fail-closed |
| G-3 Contract | `contracts/**` stubs and fixtures still satisfied by every consumer | 5 min | fail-closed |
| G-4 Acceptance | the AT harness — every AT id any lane has ever claimed, re-run from L0's harness | 15 min | fail-closed |
| G-5 Invariant | the invariant assertions for every invariant classified `mechanical` (Section 101 preamble) | 6 min | fail-closed |
| G-6 Provenance | no customer-shaped data in any fixture (invariant 111); no API key anywhere (invariant 84); no machine identity in CODEOWNERS | 4 min | fail-closed |

Every tier is **fail-closed**, and that classification is written down because invariant 80 requires every control to be explicitly classified fail-closed or fail-open. There is no fail-open tier in this gate.

### C7 — Negative gate (15:05–15:15, 10 min, CI from `main`)

The canary run. See §6. **This is the step that makes the other steps mean something.**

```bash
set -euo pipefail
git fetch origin main
git worktree add /tmp/train-verifier origin/main        # tooling from main, target is integration
/tmp/train-verifier/tools/train/run-canaries.sh --target origin/integration \
  --out tools/train/state/canaries-$(date -u +%F).json
git worktree remove /tmp/train-verifier
```

### C8 — Report (15:15–15:30, 15 min, generated + L0)

```bash
make train-report CYCLE="$(date -u +%F)"
```

See §8. The generator fills every derivable field. L0 writes the three judgment lines and nothing else.

### C9 — Promotion (15:30–15:45, 15 min, L0)

`integration` → `main` requires **all** of:

| # | Condition |
| --- | --- |
| 1 | C6 green in every tier |
| 2 | C7: every planted canary **rejected by its gate** |
| 3 | Zero open Blocking-class findings against `integration` |
| 4 | The AT/INV ledger (§8) shows no id claimed by two lanes and no id claimed-but-unreproduced |
| 5 | The cycle report exists and is signed by L0 |

```bash
make train-promote CYCLE="$(date -u +%F)"   # refuses unless 1-5 hold; prints which one failed
```

A refusal is recorded with its reason in the report. Refusing to promote is a normal outcome; refusing **silently** is not. Promotion drought is a stall signal (TRAIN-08, §7).

### C10 — Triage (15:45–16:15, 30 min, L0)

Every blocker filed since the last C10 gets a verdict this cycle. Deadlocks are arbitrated per §10. Reverted merges are diagnosed and become tomorrow's first task for their lane.

### C11 — Seeding (16:15–16:30, 15 min, L0)

L0 writes tomorrow's task per lane. Each task carries what the AI developer profile mandates: exact paths, literal commands, complete acceptance criteria, an unambiguous self-verify command, a STOP rule, and — added here — **the AT ids and invariant numbers the task is expected to move**. A task that moves no id is allowed, but it must say so explicitly. Silence is how coverage flatlines (TRAIN-06).

---

## 6. The negative gate — every gate must be proven able to fail

Fourteen canaries. L0 plants them; L0 verifies them; **no lane may create, edit, or delete one**. A lane that can remove the canary judging it is Section 53.1's instrument rewriting the wall it inspects.

Fixtures live in `tools/train/canaries/`. The runner executes from `main`'s checkout against `integration`.

| ID | Planted defect | Gate that must reject it | Required verdict | Spec anchor |
| --- | --- | --- | --- | --- |
| CAN-LANE | A commit on `lane/3/*` touching `schemas/registry/` | lane-guard | REJECT | PARTITION rule 1 |
| CAN-SHIM | A commit that must fail G-2 | the L2 workflow shim actually invoking `make train-gate` | REJECT | §4 of this file |
| CAN-SCHEMA | A non-employee assignment with no `end_date` | G-2 schema validation | REJECT | inv 58; AT-008; AT-018 |
| CAN-EXPIRY | An `exceptions.yaml` entry with no expiry | G-2 (week-one exception validator, Section 98.2 Phase 1) | REJECT | inv 77; AT-039 |
| CAN-UNCLASSIFIED | A control with no fail-closed/fail-open classification | G-2 | REJECT | inv 80 |
| CAN-DRIFT | The permanent seeded drift record in the reconciler's comparison set | reconciler run | **FIND** it | §53.1; AT-102; SIG-13 |
| CAN-NARROW | A reconciler config that silently drops a registry from the comparison set | per-registry comparison counts | REJECT | §53.1 |
| CAN-LOOSEN | Actual platform state stricter than declared | reconciler auto-repair | RAISE Level 2, **never relax** | §53.3; inv 81; AT-033 |
| CAN-VERIFY | The seeded-defect case in a `verification/contract.yaml` | verification contract run | **FAIL** the run | §31.2; SIG-18 |
| CAN-PLAN | A plan whose task has no automated verify command | plan-checker | REJECT | §30.2 |
| CAN-DIGEST | A production deploy request whose digest ≠ the staging-verified digest | pipeline digest invariant | REJECT | §32; inv 22 |
| CAN-MACHINE | An approval from a machine account | branch protection / CODEOWNERS human-only generation | NOT satisfy the gate | §98.2 Phase 1 completion check; inv 18 |
| CAN-PEOPLE | An assignment granting `people-intelligence` | G-2 validation | REJECT | AT-090; inv 106 |
| CAN-SURVEIL | A banned surveillance measurement added to a schema | G-2 validation | REJECT | AT-075; inv 96 |

**Verdict semantics, stated once so the report is unambiguous:**

| Field value | Meaning | Cycle effect |
| --- | --- | --- |
| `rejected` | The gate caught the planted defect | canary PASSES; gate is armed |
| `accepted` | The gate let the planted defect through | canary **FAILS**; **the gate is dead** |
| `absent` | The canary fixture was missing at run time | canary **FAILS**; treated as `accepted` |

**Any `accepted` or `absent` freezes the train.** No promotion to `main`, no merges next cycle, until L0 records what broke the gate and CAN-* returns `rejected`. This is AT-102's rule generalised: *a run that finds nothing, including the canary, is a failed run.*

Ownership of each canary's target gate, so a freeze routes to someone:

| Lane | Canaries whose gate that lane builds |
| --- | --- |
| L1 | CAN-SCHEMA, CAN-EXPIRY, CAN-UNCLASSIFIED, CAN-PEOPLE, CAN-SURVEIL |
| L2 | CAN-SHIM, CAN-DIGEST, CAN-VERIFY |
| L3 | CAN-DRIFT, CAN-NARROW, CAN-LOOSEN |
| L4 | (records/metrics side of CAN-DRIFT evidence) |
| L5 | CAN-MACHINE |
| L0 | CAN-LANE, CAN-PLAN |

**Adding a gate adds a canary in the same PR.** A gate merged without its paired canary fails G-1 and is reverted at C5. There is no cycle in which a gate exists unproven.

---

## 7. Healthy cycle versus sick cycle

Read across. These are thresholds, not impressions.

| Dimension | Healthy | Sick |
| --- | --- | --- |
| Lanes shipping | 5 of 5 opened an eligible PR | ≤ 3 of 5, or the same lane silent 2 cycles running |
| Train wall time (C3→C11) | ≤ 2h 15m | > 4h |
| Branch age at merge | < 1 working day (PARTITION) | any branch surviving 2 freezes |
| Rebase conflicts | 0 | ≥ 1 — a suspected rule-3 breach |
| lane-guard violations | 0, or 1 caught and fixed same cycle | same lane violating in ≥ 2 cycles — it does not understand its partition |
| Canary verdicts | 14 of 14 `rejected` | any `accepted` or `absent` |
| Real rejections (non-canary) | ≥ 1 per lane per rolling 5 cycles | **0 across all lanes in 5 cycles** |
| Reverted merges | ≤ 1 per cycle, diagnosed by C10 | ≥ 2 in a cycle, or the same lane reverted twice in 5 cycles |
| AT ledger movement | verified count strictly increasing over any 3 cycles | flat for 3 cycles while lane commits > 0 |
| Claim integrity | every claimed AT id independently reproduced by L0's harness | any id claimed-but-unreproduced, or claimed by two lanes |
| Promotion to `main` | ≥ 1 per 3 cycles | none in 5 cycles |
| Blocker verdicts | 100% answered within one cycle | any blocker unanswered across 2 cycles |
| Report | present, signed, all fields derived | missing or stale > 1 cycle |

**Zero real rejections is a sick cycle, not a healthy one.** Five AI developers with no repo context, building a 10,000-line specification, producing five consecutive days of work that no gate objected to, means the gates are asleep — the plan-checker reading of Section 30.2 and the rubber-stamping reading of Section 103.9, applied to the train itself. Treat it exactly as AT-102 treats a reconciliation run that found nothing.

**The wrong-thing detector is the AT ledger, not the diff.** A lane can produce a large, clean, green diff every day for a week and move zero acceptance tests. Commit volume is not evidence — invariant 17 (machine output volume is not throttled) and invariant 90/AT-085 (volume is never counted) both point the same way. What counts is: *which of the 110 tests moved, and did L0's harness reproduce it?*

---

## 8. The daily integration report

Machine record: `tools/train/state/CYCLE-<YYYY-MM-DD>.yaml`. Human render: `docs/train/CYCLE-<YYYY-MM-DD>.md`.

Every field below is derived by the generator except the three marked `# HUMAN`. Invariant 40 and invariant 46: machines write measurable state, derived data is computed and never hand-maintained.

```yaml
cycle_id: "2026-09-14"
integration_sha_before: "a1b2c3d"
integration_sha_after:  "e4f5a6b"
train_wall_minutes: 128

lanes:
  - lane: L1
    branch: "lane/1/f3-04-registry-schemas"
    eligible_at_freeze: true
    lane_guard: green
    rebase_conflicts: 0
    merged: true
    reverted: false
    files_changed: 11
    at_claimed:   [AT-001, AT-002, AT-006]
    at_reproduced: [AT-001, AT-002, AT-006]   # re-run from L0's harness, not the lane's
    at_unreproduced: []
    inv_claimed:  [50, 51, 52, 58]
    real_rejections_this_cycle: 1              # gate said no to something the lane meant to ship
  - lane: L4
    # ... one block per lane, all five present even when a lane shipped nothing

gates:
  G1_structure: pass
  G2_schema:    pass
  G3_contract:  pass
  G4_acceptance: pass
  G5_invariant: pass
  G6_provenance: pass

canaries:                                      # rejected = the gate caught it = PASS
  CAN-LANE:         rejected
  CAN-SHIM:         rejected
  CAN-SCHEMA:       rejected
  CAN-EXPIRY:       rejected
  CAN-UNCLASSIFIED: rejected
  CAN-DRIFT:        found
  CAN-NARROW:       rejected
  CAN-LOOSEN:       raised_level_2
  CAN-VERIFY:       failed_run
  CAN-PLAN:         rejected
  CAN-DIGEST:       rejected
  CAN-MACHINE:      not_satisfied
  CAN-PEOPLE:       rejected
  CAN-SURVEIL:      rejected
canary_verdict: all_armed                      # all_armed | DEAD_GATE

ledger:
  at_total: 110
  at_verified_cumulative: 41
  at_verified_delta_this_cycle: 3
  at_claimed_by_two_lanes: []
  at_claimed_unreproduced: []
  inv_total: 111
  inv_mechanical_asserted: 29
  inv_unclassified: 0                          # Section 101 preamble: unclassified fails CI

signals_open: [TRAIN-05]
blockers_open: 2
blockers_answered_this_cycle: 3
deadlocks_open: 0

promotion:
  promoted_to_main: false
  refusal_reason: "TRAIN-05 open: zero real rejections across 5 cycles"   # HUMAN
cycle_verdict: "amber"                                                    # HUMAN
next_cycle_correction: "L0 to hand-audit L2's last three merges"          # HUMAN
signed_by: "L0"
```

### The report's own canary

A report is an instrument, and instruments get graded here like every other one.

* A report in which **every gate passed, every canary passed, and `real_rejections` summed to zero across all five lanes for five consecutive cycles** is not a clean report. The generator sets `cycle_verdict: sick` and opens **TRAIN-05** automatically. L0 cannot close TRAIN-05 by asserting things are fine; it closes when a real rejection occurs, or when L0 hand-audits three merges and records what it found.
* A **missing or stale report is Blocking**, on the same reasoning and the same 7-day-class discipline the weekly bootstrap log carries in Section 95.4: an evidence base nothing makes happen gets reconstructed from memory at exactly the moment you needed it to be real. Here the window is one cycle, not seven days, because the cycle is daily.
* `at_verified_cumulative` is computed by re-running the AT harness from L0's checkout. It is never incremented by a lane's assertion. A lane's claim is an input to the check, never the result of it — invariant 20: repository-provided text is data, not authority.

---

## 9. Stall signals

The train stalls quietly. These make it loud. Each is fail-closed unless stated (invariant 80).

| ID | Signal | Detector | Threshold | Owner | Action | Analogue |
| --- | --- | --- | --- | --- | --- | --- |
| TRAIN-01 | Lane silence | No eligible PR at freeze | 2 consecutive cycles | L0 | L0 reads that lane's branch itself; task may be unbuildable as written | SIG-06 |
| TRAIN-02 | Stale branch | Branch behind `integration` | > 1 cycle | Lane | Rebase or abandon; PARTITION caps branch life at < 1 day | PARTITION |
| TRAIN-03 | Partition violation | lane-guard fail | Same lane, 2 cycles in 5 | L0 | Rewrite that lane's task with explicit path list; do not warn twice | PARTITION rule 1 |
| TRAIN-04 | **Dead gate** | Any canary `accepted` or `absent` | 1 | L0 | **Freeze the train.** No merges, no promotion, until `rejected` returns | §53.1; AT-102; §31.2 |
| TRAIN-05 | Rubber-stamp suspicion | Sum of real rejections | 0 across 5 cycles | L0 | Hand-audit 3 merges; record findings | §103.9; §30.2 |
| TRAIN-06 | **Coverage flatline** | `at_verified_delta` | 0 for 3 cycles while commits > 0 | L0 | Stop feature tasks; next task per lane must move a named AT id | §100 |
| TRAIN-07 | Deadlock | Cycle in the blocker graph | 1 | L0 | Run §10 | this file |
| TRAIN-08 | Promotion drought | Cycles since `main` moved | 5 | L0 | `integration` is diverging from releasable; cut scope until it promotes | §32 |
| TRAIN-09 | Revert churn | Reverts of one lane's merges | 2 in 5 cycles | L0 | That lane's tasks are too large or too vague; halve them | — |
| TRAIN-10 | Claim collision | `at_claimed_by_two_lanes` or `at_claimed_unreproduced` non-empty | 1 | L0 | Two lanes building the same thing, or one lane claiming what it did not build — the wrong-thing signature | §100 |
| TRAIN-11 | Report gap | Newest report age | > 1 cycle | L0 | Blocking; no promotion | §95.4 |
| TRAIN-12 | Unproven blocker | Blocker with no reproducing command | 1 | L0 | Close as unproven, with the reason written (§10 step 0) | this file |
| TRAIN-13 | Contract pressure | Contract Change Requests filed | 3 in 5 cycles for one area | L0 | The frozen contract is wrong in that area; fix `contracts/**` once rather than routing five workarounds | PARTITION rule 2 |

**The three that mean "a lane quietly built the wrong thing"** are TRAIN-06, TRAIN-10 and TRAIN-13. They are the ones to read first, before any green gate.

---

## 10. Mutual block — two lanes each believing the other blocks them

This is the failure mode with no natural detector: both lanes are idle, both are convinced they are correct, neither can escalate to the other because **lanes have no channel to each other** (PARTITION rule 4: a lane consumes another lane's output only through `contracts/**` or a published artifact). Left alone it burns cycles silently while both lanes report "blocked."

### Step 0 — A blocker that cannot be checked is not a blocker

Every blocker issue MUST carry a **reproducing command and its actual output**. The template:

```
BLOCKER
lane:        L3
task:        p2-reconciler-diff
blocked_by:  lane/1        # a lane id, a contract path, or "unknown" — never a person
repro:       make lane-verify LANE=3
output:      |
             validators/registry/assignment.schema.json: no such file
              -> expected under contracts/registry/v1/ per contracts/README
expected:    contracts/registry/v1/assignment.schema.json to exist and validate the fixture
```

L0's triage at C10 runs `repro` verbatim.

* Command does not reproduce → **not a blocker**. Closed as unproven, TRAIN-12, with the reason written back to the lane. The lane resumes.
* No `repro` field at all → **not a blocker**, same outcome.

This is the same principle as the canaries, pointed at claims instead of gates: a claim that cannot be checked is not a check on anything. Most "mutual blocks" die here, because at least one side is usually mistaken about what it needs.

### Step 1 — Detection is machine, not human

```bash
make train-deadlock CYCLE="$(date -u +%F)"
# builds the directed graph from open blockers' blocked_by fields
# any cycle of length >= 2  ->  DEADLOCK, raises TRAIN-07, exits 2
```

Runs inside C8 every cycle. Neither lane has to notice, and neither lane is trusted to.

**The detector has its own canary.** `tools/train/canaries/deadlock-pair.json` holds a permanent synthetic L-A↔L-B pair that the detector MUST report every run. A run reporting zero deadlocks — the planted pair included — is a **failed detector run**, not a clean one, and freezes the train under TRAIN-04. Section 53.1's seeded-canary rule, applied to the arbitration instrument itself.

### Step 2 — Both lanes stop; neither negotiates

On TRAIN-07, both lanes:

1. stop work on the disputed item **only** — other tasks continue;
2. do **not** contact each other, do not open a PR against the other's paths, do not "temporarily" copy the other lane's file into their tree;
3. wait for L0's verdict, delivered at the next C1.

Rationale: neither lane has judgment authority (PARTITION, *AI developer profile*), and a lane resolving a cross-lane dependency by reaching into another tree is precisely PARTITION rule 4's prohibition. A workaround merged today is a partition breach forever.

### Step 3 — L0 arbitrates within one cycle, using a fixed ladder

L0 applies these in order. **First match wins.** No weighing, no discussion, no "it depends" — the ladder exists so that arbitration is deterministic and reproducible, and so it cannot be gamed by whichever lane argues longest.

| # | Condition | Resolution | Who moves |
| --- | --- | --- | --- |
| **1** | The thing both lanes need lives in `contracts/**` and is missing, ambiguous, or wrong | L0 writes or corrects the contract **and** a compile-against stub/fixture. Both lanes unblock the same cycle | L0 |
| **2** | One lane is attempting to edit or depend on a path it does not own | The non-owning lane is wrong regardless of technical merit. L0 rewrites that lane's task; the owning lane proceeds unchanged | The non-owning lane |
| **3** | The dependency runs **against** the merge-train order L1→L4→L2→L3→L5 | The lane **later** in the train waits. Its item defers one cycle; the earlier lane proceeds. Deterministic tie-break, no debate | The later lane |
| **4** | A genuine mutual dependency, both directions real, both lanes correct | L0 **cuts it with a stub**: a fixture in `contracts/**` that both sides build against. Never by letting either lane read the other's source | L0 |
| **5** | None of 1–4 | L0 **splits the item**: the part buildable against a stub ships now; the residue becomes an L0-owned task | L0 |

Rung 3 is the one that resolves the honest, symmetric case, and it is why the merge train has a fixed order at all. The order is a dependency order (PARTITION, *Dependency order*); when two lanes disagree about who waits, the order already answered.

### Step 4 — The resolution is a recorded decision

```bash
set -euo pipefail
make train-arbitrate CYCLE="$(date -u +%F)" \
  RUNG=3 LANES="L2,L3" ITEM="p2-reconciler-diff" \
  DECISION="L3 defers one cycle; L2 proceeds. Train order L2 precedes L3."
# writes docs/train/decisions/DEC-<cycle>-<n>.md and links both blocker issues
```

Arbitration is judgment, and judgment is written down by a human (invariant 40; Section 94.9). The decision names the rung applied, so a later reader can check the ladder was followed rather than trusting that it was.

### Step 5 — Anti-capture

Two guards, because an arbitration ladder is itself gameable:

* **Repeat-winner guard.** If deadlocks in the same contract area resolve in favour of the same lane **3 times in a rolling 5 cycles**, the partition is wrong, not the lanes. L0 opens a PARTITION amendment — the only path by which the frozen contract changes, and only L0 may open it. This is the same instinct as SIG-32 (a repeatedly overridden signal is a suspect signal) and Section 53.6 (a repeatedly reclassified drift class is a suspect class).
* **Rung-1 counter.** Rung-1 resolutions are counted. Three in five cycles for one area raises **TRAIN-13**: the contract is under-specified there, and L0 fixes `contracts/**` once rather than arbitrating the same gap five times.

### Step 6 — Unblock verification

A deadlock is not closed when L0 writes the decision. It closes when **both** lanes' `repro` commands exit 0 on the next cycle's `integration` HEAD, verified by L0, not reported by the lanes:

```bash
make train-unblock-verify ITEM="p2-reconciler-diff"   # re-runs both stored repro commands; exits 0 only if both do
```

A deadlock closed on a lane's say-so is a deadlock that reopens tomorrow.

---

## 11. When a merge turns out to be wrong after the fact

Discovered at C0, or by a canary going `accepted` two cycles later:

```bash
set -euo pipefail
git checkout integration
git revert -m 1 <merge-sha>          # revert the merge, never rewrite integration's history
make train-verify-full
git push origin integration
```

Then, mandatory and in the same cycle: **the failure becomes a permanent negative test.** Invariant 2 — "every production bug becomes a permanent regression test" — applies to the train's own defects with full force. A revert with no new test added is not a fix; it is the same defect with the evidence deleted. The new test is added to `tools/train/canaries/` if it proves a gate can fail, or to the AT harness if it proves behaviour.

`integration`'s history is never rewritten. Force-push to `integration` or `main` is prohibited (PARTITION: `main` protected; `control-plane-records` carries a no-bypass ruleset per D107).

---

## 12. Degraded cycle — when the platform is unavailable

Mirrors Section 46.1, scoped to the train. Entry and exit are **recorded events** announced by L0; nobody discovers the mode by inference.

```
GIT HOST UNAVAILABLE

CONTINUES:
  ✓ Lanes build locally on their own branches (git is distributed)
  ✓ make lane-verify, make lane-guard  (both run offline)
  ✓ Local canary runs from a local main worktree

PAUSES:
  ✗ The merge train (C5)
  ✗ Integration and negative gates (C6, C7)
  ✗ Promotion to main (C9)

ON RECOVERY — reconcile, do not assume:
  1. Every lane pushes; L0 verifies nothing was lost
  2. Re-run the full gate on integration HEAD (C0, out of band)
  3. Re-run ALL canaries before the first merge — a gate unexercised
     across the outage is an unproven gate
  4. Run the deadlock detector; blockers filed offline enter the graph
  5. Write one catch-up report covering the whole window
  6. Resume the normal clock at the next 09:30
```

Step 3 **gates the resumption of merging**, the same way Section 46.1 makes `verify-digest-chain` gate the resumption of production deploys. Records written out of band during the outage are captured one dated file per record type per day and reconciled on recovery; a record with no dated file is a record that was never made.

---

## 13. The AT and invariant ledger — the anti-wrong-thing instrument

This is the single most important artefact the cycle produces, because it is the only one that answers *did they build the right thing* rather than *did it compile*.

Rules:

1. **Every lane task names the AT ids and invariant numbers it moves.** Named at C11, before the work, never after.
2. **Ids are real or the task fails review.** Section 100 holds AT-001…AT-110; Section 101 holds invariants 1…111. An id outside those ranges fails G-4 at once. Never invent one.
3. **L0 reproduces every claim** from its own harness. A lane's green is an input, not a result (invariant 20).
4. **No id belongs to two lanes.** A collision is TRAIN-10 and is arbitrated at C10 by the §10 ladder.
5. **Every invariant carries its classification** — `mechanical`, `policy`, or `review-held` — per the Section 101 preamble, and an unclassified invariant fails CI. `inv_unclassified: 0` is a promotion precondition.

Indicative lane ownership of the catalogue, set by L0 at Phase 0 and amended only with the partition:

| Lane | Subsystems (PARTITION) | Representative acceptance tests | Representative invariants |
| --- | --- | --- | --- |
| L1 Registries & Contracts | A, B | AT-001, AT-002, AT-006, AT-007, AT-008, AT-009, AT-010, AT-016, AT-047, AT-051 | 1, 7, 11, 50, 51, 52, 53, 54, 58, 62, 77, 80 |
| L2 Pipeline & Evidence | E, F | AT-023, AT-024, AT-025, AT-026, AT-027, AT-030, AT-049, AT-103, AT-107 | 2, 22, 23, 28, 71, 72, 73, 85 |
| L3 Reconciler & Provisioning | C, D | AT-017, AT-018, AT-033, AT-036, AT-037, AT-102, AT-110 | 44, 55, 57, 58, 79, 81 |
| L4 Records, Events & Metrics | I, N | AT-032, AT-040, AT-041, AT-042, AT-043, AT-046, AT-048, AT-088, AT-104, AT-105 | 40, 46, 47, 49, 111 |
| L5 Access, Infra & Ops | K, L, M, Q, R | AT-011, AT-022, AT-028, AT-029, AT-035, AT-050, AT-089, AT-090, AT-097, AT-098, AT-108, AT-109 | 18, 24, 25, 26, 83, 84, 106, 107, 108, 109 |

Several of these acceptance tests are themselves negative by construction, and they are the ones to schedule early rather than late, because they are the tests that prove a boundary rather than assert it: **AT-102** (a reconciliation run finding nothing is a failed run), **AT-108** (four writes from the ops console, all four must fail), **AT-109** (two connections from inside the background cage, both must be refused at the host egress layer), **AT-110** (six attempts from the reconciler credential, all six must fail, and the credential must then still complete a normal run), **AT-071** (no code path to an automated people action exists; attempted configuration fails validation), **AT-075** (banned measurements are absent and rejected if introduced). AT-090 says it outright: *"a test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes."*

---

## 14. What a lane must never do

Short, absolute, and quotable back at a lane in one line.

1. Never merge anything. Only L0 merges.
2. Never rebase, push to, or open a PR against another lane's branch.
3. Never edit a path outside your lane's OWNS column.
4. Never edit `contracts/**`. File a Contract Change Request.
5. Never create, edit, delete, or "fix" a canary in `tools/train/**`.
6. Never claim an AT id or invariant number you did not move.
7. Never invent an id. If it is not in Section 100 or Section 101, it does not exist.
8. Never work around a blocker by copying another lane's file into your tree.
9. Never open a second PR in one cycle.
10. Never file a blocker without a reproducing command and its output.
11. Never force-push anything but your own lane branch, and then only with `--force-with-lease`.
12. Never proceed past your task's STOP rule. Stop, file, wait for C1.

---

## 15. Cycle checklist — L0's literal run

```bash
set -euo pipefail
CYCLE="$(date -u +%F)"

make train-open      CYCLE="$CYCLE"                       # C1   09:30
make train-freeze    CYCLE="$CYCLE"                       # C3   13:00
for LANE in 1 4 2 3 5; do                                 # C5   13:20
  make train-merge LANE="$LANE" CYCLE="$CYCLE" || echo "L$LANE reverted, train continues"
done
make train-gate      CYCLE="$CYCLE"                       # C6   14:30

git worktree add /tmp/train-verifier origin/main          # C7   15:05
/tmp/train-verifier/tools/train/run-canaries.sh \
  --target origin/integration --out tools/train/state/canaries-$CYCLE.json
git worktree remove /tmp/train-verifier

make train-deadlock  CYCLE="$CYCLE"                       # C8   15:15
make train-report    CYCLE="$CYCLE"
make train-promote   CYCLE="$CYCLE"                       # C9   15:30 (refuses, loudly, with a reason)
make train-triage    CYCLE="$CYCLE"                       # C10  15:45
make train-seed      CYCLE="$CYCLE"                       # C11  16:15
```

If `run-canaries.sh` reports anything other than fourteen armed gates, stop at that line. Everything after it is a check that could only pass.
