# 99 — PROTOCOL WALKTHROUGH

**Status:** diagnostic, not normative. This file changes nothing. It walks the protocol of files
`00`–`11` end to end on paper, once for a task that goes right and three times for tasks that go
wrong, and records where the walk falls through.

**Owner:** L0 Integrator.
**Method:** every step names the check that runs, what that check would catch, and what it would
miss. A step with nothing in the *misses* column is a step nobody has thought about hard enough.
**Conforms to:** `Code/implementation/PARTITION.md` (FROZEN). Nothing here redesigns the partition
or any sibling protocol file. Where this file finds a contradiction between two protocol files, it
records it as a gap and routes it to L0 — it does not pick a winner.

---

## 0. The verdict, before the evidence

The protocol holds along its main axis. A lane that builds the wrong thing inside its own tree,
that ships a suite asserting nothing, that edits a path it does not own, or that fabricates a
result CI can independently re-run, is caught — usually within two steps, always before `main`.
That is the failure the corpus was written against and it is closed.

It falls through in three places, and they are all the same shape:

> **Every control that is a *re-execution* holds. Every control that is a *record* is
> unfalsifiable.**

A `GATE-RESULT` line is re-derived by CI, so lying about it is pointless. A drill record, an
`executed_for_real: true` field, a `PASS-BOOTSTRAP` verdict, a human-judgment line on a cycle
report and an `H`-class acceptance-test result are all files that assert their own truth. The
gates check that those files *exist* and are *well-formed*. Nothing checks that the event they
describe happened.

The second cluster is wiring. Four instruments the corpus calls mandatory — `--fixture-parity`,
`--mutation-drill`, the AT harness at PR time, and the post-merge integration run as a blocking
condition — are specified in one file and invoked by no job in `10-ci-pipeline.md`. They are not
weak controls; they are absent controls with documentation.

The third cluster is arithmetic and precedence: three different train-halt rules, three different
promotion commands, two different contract registers, and a merge-train clock that does not close
against its own stated GATE A budget.

Fifteen gaps, §5. Each names the specific additional control it needs.

---

## 1. TRACE A — one task, from pickup to `main`

Subject: **L1**, task `L1-03-08`, cycle `2026-09-14`. The task adds a rule file plus an invalid
fixture for each of the eleven rules of §15.5 to `validators/registry/**`, declares
`enumerates: 11`, claims **AT-047** and invariants **31** and **77**, and carries the STOP rule
"if the 24x7-without-rota blocker cannot be made to reject `NEG-CONTRACT-012`, do not proceed."

Branch: `lane/1/f3-08-registry-rules`.

---

### A-0 — Pickup (C1, 09:30)

| | |
|---|---|
| **Who** | L0 issues; the L1 agent reads |
| **Named checks** | `make train-open CYCLE=` publishes the task list (`06` §5 C1). Ledger schema lint — no `status:`, no `percent:`, no `updated_by:` (`11` DT-01). `enumerates: 11` written by L0 at issuance (`11` §2.4). AT/INV ids must exist in §100/§101 (`06` §13 rule 2) |
| **Catches** | A task with no self-verify command, no STOP rule, or an invented AT id. A lane setting its own status later — the field does not exist |
| **Misses** | That the task is the *right* task. `06` §5 C1 says "a lane that receives no task list does not invent one," and there is no detector for a lane that invents one anyway; the invention surfaces only as `at_claimed_unreproduced` (TRAIN-10) or as a `DL-03 orphan_files` finding at LANE DoD, both cycles later. It also misses a task that names a **real but wrong** AT id — G-4 checks the id exists, not that the work moves it |

---

### A-1 — Build and self-verify (C2, 09:40–13:00, developer machine)

| | |
|---|---|
| **Who** | the L1 agent, alone |
| **Named checks** | `make selfverify LANE=1 TASK=f3-08-registry-rules` → `validators/registry/lane-verify.sh --task …` must exit `0` and `lane-negative.sh --task …` must exit `1` (`00` §5 T0). The exit-code contract: `2` = VACUOUS, `3` = NON-DISCRIMINATING (`00` §3). `make dod-task TASK=L1-03-08` → **DT-01 … DT-10**, one line `DOD-VERDICT=MET LEVEL=task` (`11` §2.2). `make dod-negative LEVEL=task` → `proven=10/10 unproven=0`. Anti-hallucination **V1–V6** with every claim pasted from `$EV` (`manual/04`) |
| **Catches** | A suite that asserts nothing (exit `2`). A negative fixture the gate now accepts (exit `3`). `TODO`/`NotImplementedError`/`example.com` in a written file (DT-04). A file that does not parse (DT-05). A foreign path (DT-07). **Eleven declared, three delivered** (DT-08 `declared≠delivered` — the single most characteristic failure of a low-context model, and the only place the number eleven is held). A silently dropped acceptance criterion (DT-02 `exact=`) |
| **Misses** | Everything, in the sense that matters: **no step of T0 is independently observed.** The agent runs the commands, reads the output, and pastes it. `manual/04`'s Prime Directive — "if you did not run a command and read its output, you do not know it" — is an instruction to the agent, enforced by nothing at this step. `$EV` lives outside the repository *by design* (so it fails no lane-guard) and therefore leaves no artifact anyone else can read. DT-09 requires the self-verify output "pasted verbatim from this session"; there is no session to check it against. It also misses a stub that parses, carries no banned token, delivers eleven files and asserts nothing meaningful — DT-04 and DT-05 are lexical, and DT-03/DT-06 only require *a* negative to fire, not the right one |

**Verdict at A-1:** T0 is a discipline, not a control. Its value is that it makes the agent stop
early and cheaply; its value as evidence is zero, and the protocol is right not to treat it as
evidence (`11` §2.5: `accepted` is derived by L0 at integration head, never by the lane).

---

### A-2 — First push to `lane/1/*`

| | |
|---|---|
| **Who** | GitHub Actions, `selfci-lane.yml`, self-hosted `[self-hosted, linux, build-ci]` |
| **Named checks** | Branch-name check (warn-only, not reject): `^(lane/[1-5]/(f[0-7]\|g[1-8]\|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}\|l0/.+\|integration\|main)$` — a non-matching name emits `BRANCH-NAME-WARN` in the log and does not fail or block the push. `ci-cache.sh warm` (inputs only). `make lane LANE=1` = `lane-verify.sh --all` + `lane-negative.sh --all` + `make negative-audit LANE=1` + `make lane-guard LANE=1` (`00` §5 T1). Then the vacuity assertion on the last `GATE-RESULT` line: `assertions>0`, `failures=0`, `negatives_run>0`, `negatives_that_failed_correctly==negatives_run` (`10` §7.1) |
| **Catches** | **This is the first independent re-execution in the whole protocol.** Any claim the agent made about its own suite is re-derived here, on a machine the agent does not control. Also: a gate declared with no `negative:` block, a duplicated `proves:` string, a negative fixture byte-identical to its positive (`00` §4.1 rule 5, via `negative-audit`) |
| **Misses** | It blocks nothing. `selfci-lane` **emits no required context and writes no record** (`10` §3), and carries `cancel-in-progress: true`. A red `selfci-lane` is advice. A *cancelled* `selfci-lane` leaves no trace at all — and per `10` §4.2 that cancellation is deliberate and correct, because the workflow gates nothing. It also cannot see outside `validators/registry/**`: `00` §1.2 forbids T1 from asserting anything outside the lane's owned paths, so a correct-but-wrong-shaped output is invisible here by construction |

---

### A-3 — PR opened into `integration`

Three required contexts, and they are the first things in this trace that can stop a merge.

| Context | What runs | Catches | Misses |
|---|---|---|---|
| `lane-guard` | `contracts/gate/lane-guard.sh`, standalone, **no `concurrency:` block** so it always runs to completion (`10` §4.2) | Any changed path whose `owner-of.sh` result ≠ the branch's lane number; and `unowned>0`, which `05` §6 correctly makes a failure and not a warning | See **G-01** (the lane number comes from the branch name) and **G-02** (`ownership.tsv` is unreconciled) |
| `selfci-meta` | `pipeline-gates.sh --all` then `--negative`; must print `PIPELINE-GATES PASS proven=11/11 unproven=0` | **GATE-L0-010** a verdict written inside an L2-owned workflow; **-012** an `if:`/path filter on a required-context job; **-013** an unpinned action; **-014** wrong concurrency polarity; **-016** a result-shaped entry in the cache; **-017** a missing `timeout-minutes`; **-018** a deleted calendar gate; **-019** a credentialed job on a persistent runner; **-020** a run 40% faster with flat assertions | It gates the *pipeline*, not the *content*. And `GATE-L0-020`'s cold-start branch prints `SKIP-IMPOSSIBLE` and exits `0` — named out loud in `10` §8.2, which is the right handling, but it means the speed-honesty gate is inert for the first ten runs of every workflow, i.e. for the whole of BT-0 |
| `selfci-gate-a` | mirror of `make gate-lane LANE=1 PR=<n>` | **LG-01 … LG-12**, below | — |

**GATE A, check by check** (`05` §3):

| # | What it proves here | What it would catch | What it would miss |
|---|---|---|---|
| LG-01 | `behind=0` against `origin/integration` | The gate judging a tree that will not be the tree that lands | Nothing much — but see **G-11**: with `strict_required_status_checks_policy: true`, satisfying LG-01 for five lanes serially is the whole cost of the merge train |
| LG-02 | `foreign=0 unowned=0` | The foreign-path case (Trace B-1) | **G-01**, **G-02** |
| LG-03 | `l0_paths_touched=0` | A lane editing `contracts/**`, `CODEOWNERS`, `Makefile`, `docs/**` — i.e. a lane rewriting the thing that judges it | Nothing detects **L0** widening those files wrongly. `contracts/gate/**`, `contracts/dod/**`, `COUNTS.tsv` and `ownership.tsv` are protected *from lanes* and from nobody else |
| LG-04 | `modified_aggregates=0` | A lane appending to a shared index — PARTITION rule 3, the reason five lanes' merges cannot conflict | It reads `contracts/gate/aggregates.txt`, an L0-authored enumeration. A shared mutable file nobody thought to list is invisible |
| LG-05 | `tests=<n> failed=0 seeded_defect=DETECTED` | **The fabricated-pass case (Trace B-2).** Re-runs the lane suite from a clean checkout of the PR head. Also catches a repaired seeded-defect case — §31.2 applied to the build | Only what the suite covers. A lane whose suite is genuinely green against a stale contract passes here (Trace B-3) |
| LG-06 | `fixtures_sha=<…> fixtures_match=1` | A lane that edited a frozen fixture to go green — `AP-16`, the single most likely wrong move an unsupervised lane makes | **It proves the fixture is unmodified, not that it is current.** This is precisely Trace B-3's blind spot |
| LG-07 | `proven=12/12 unproven=0` | A gate check that cannot be shown to fail. `05` §5 runs one mutation per check in a throwaway worktree | The battery is L0-authored and enumerates twelve mutations; a thirteenth thing LG-01…12 should catch and does not is not detectable by mutating the twelve |
| LG-08 | `at=110/110/110 inv=111/111 ec=112/112 checks=24/24 narrowed=0` | A lane that quietly enumerates less than it declares. The three-way agreement is the check `05` §8 uses to detect any future regression in §100's own table | See **G-13**: the 24 counted checks are LG-01…12 + IG-01…12. T3's own numbered checks and the fourteen `CAN-*` canaries are in no `COUNTS.tsv` row |
| LG-09 | `approver=<login> author_distinct=1 stale_approvals=0 machine_approvals=0 codeowner=1` | A self-approval; a machine approval; an approval of a superseded push; a Read-only approval that does not satisfy (NT-01, NT-02, NT-03) | See **G-10**. With L0 as the only human, this check is satisfied by the same person for all five lanes, every cycle, and the anti-rubber-stamp reading of it lives ten cycles downstream at IG-11 |
| LG-10 | `required=<n> skipped=0 neutral=0 missing=0` | The §33.2 failure — a job skipped by an `if:` reporting a conclusion branch protection counts as satisfied | It reads the PR's own check runs. It cannot see a required context that was never registered at all; that is `DP-04`, a phase-level check |
| LG-11 | `foreign_refs=0` | A cross-lane import — PARTITION rule 4 | A lane that copies another lane's *content* rather than importing it. `AP-25` names the behaviour; `DI-03 stubbed>0` is the detector, and it is at INTEGRATION, four steps later |
| LG-12 | `ci=PASS local=PASS delta=0` | **The shim problem, closed.** L2 owns the workflow that judges L2; a gutted invocation shows up as disagreement between CI and L0's local `make` run. Reinforced by `CAN-SHIM` and by `GATE-L0-010`'s thin-workflow rule | It compares two verdicts. It cannot see that both are wrong for the same reason — a defect in the L0 `Makefile` itself produces `delta=0` |

**Output of record:** one line, `VERDICT=PASS GATE=lane LANE=1 PR=417 …`, and the shell test in
`05` §3.1 must print `GATE-A-OPEN`. Nothing else authorises the merge. `10` §7.2 asserts the same
single line and `wc -l == 1` — a gate that starts printing two lines is closed, which is the right
polarity.

---

### A-4 — Freeze and rebase (C3 13:00, C4 13:00–13:20)

| | |
|---|---|
| **Named checks** | `make train-freeze CYCLE=` — eligibility is four conditions: exactly one open PR from that lane, `lane-guard` green, `lane-verify` green on the PR head, and the PR body declaring its claimed AT ids and invariant numbers (`06` §5 C3). Then `git rebase origin/integration`, `make lane-verify LANE=1` again, `git push --force-with-lease` |
| **Catches** | Two PRs from one lane in one cycle — `06` is explicit that this is how merge order stops meaning anything. A rebase conflict, which `06` §5 C4 correctly reads as a *suspected PARTITION rule-3 breach* rather than as ordinary git friction, because clean lane work cannot conflict |
| **Misses** | Nothing at this step, but see **G-11**: the twenty-minute rebase window and the seventy-minute train window are computed independently of `10` §4.1's train-floor arithmetic, and the two do not agree |

---

### A-5 — Merge train step L1 (C5, 13:20)

| | |
|---|---|
| **Named checks** | `make train-merge LANE=1` → re-assert `lane-guard` **on the merge result**, not only on the branch; `git merge --no-ff`; the smoke tier ≤ 3 min (schema validation, contract stub compile, the lane's own claimed ATs); on failure `git revert -m 1 <merge>` (`06` §5 C5) |
| **Catches** | A foreign path that appears only in the merge resolution — the case LG-02 on the branch cannot see |
| **Misses** | **G-03.** What happens next on failure has three different documented answers: `06` reverts and *continues to the next lane*; `00` §8 halts the train and freezes `integration`; `01` §8.1 freezes `integration` and restarts the whole order next cycle. The smoke tier includes "contract stub compile", so a contract failure at this step is simultaneously in scope for all three rules |

---

### A-6 — Post-merge on `integration`

| | |
|---|---|
| **Named checks** | `selfci-integration.yml`, singleton, `cancel-in-progress: false`. Ten CT pairs as a job matrix, each asserting a `GATE-RESULT … level=T2` line. `lane-guard.sh --replay --base origin/main --head $GITHUB_SHA` (IG-08). `make fixtures-all` (FG-1…FG-5). `make negative-audit`. `ci-cache.sh audit` (GATE-L0-016). `assertion-ratchet.sh` (T3 check 5). Then a **hosted** `record` job that fails closed if `RECORDS_WRITER_TOKEN` is absent |
| **Catches** | Two lanes diverging at a boundary — the `plan-approved` vs `plan_approved` failure `01` §0 is written against. A foreign path smuggled inside a merge commit. A quietly deleted test (the ratchet). A narrowed fixture corpus (FG-4's evaluation counts). A cached result masquerading as a run |
| **Misses** | **G-07: this entire job emits no required status context.** Everything above blocks nothing mechanically; the halt is a procedure L0 performs after reading a result. **G-05:** the matrix is hard-coded `[CT-01 … CT-10]`, so `C-11` (secret tiers) and `C-12` (version floor / multi-version) from `01`'s twelve-contract register have no CI job — and `N-12`, the canary for "a lane quietly dropped v1 while `platform.yaml` still declares it supported", never executes. **G-06:** neither `--fixture-parity` nor `--mutation-drill` runs here, though `01` §5.4 and §7.2 make both mandatory |

---

### A-7 — Remaining train steps L4 → L2 → L3 → L5

Each repeats A-3 … A-6 for its lane. The order is fixed and is a dependency order
(PARTITION §"Dependency order"); `00` §5 T3 is explicit that reordering around a failure ships the
dependency inversion the order exists to prevent.

**Catches:** consumers meeting real producer output, in order.
**Misses:** the three inversions of `01` §3 — **C-07, C-10, C-11 are produced by L5 and consumed by
L3**, and L3 merges *before* L5. At L3's step, L5's real output does not exist in this cycle, so
L3 is measured against stubs. This is legal and deliberate (`01` §5), and it is exactly the
mechanism Trace B-3 rides.

---

### A-8 — Integration gate (C6, 14:30) and negative gate (C7, 15:05)

| | |
|---|---|
| **Named checks** | `make train-gate CYCLE=` → tiers **G-1** structure, **G-2** schema, **G-3** contract, **G-4** acceptance, **G-5** invariant, **G-6** provenance, every one fail-closed (`06` §5 C6). Then, from a worktree of `origin/main`, `tools/train/run-canaries.sh --target origin/integration` → the fourteen `CAN-*` canaries, each of which must be `rejected` (`CAN-DRIFT`: **found**; `CAN-LOOSEN`: raise Level 2; `CAN-VERIFY`: the run **fails**; `CAN-MACHINE`: does not satisfy). **NOT ARMED — excluded from counts, Phase 1+:** `tools/train/**` is an unbuilt path (Founder decision A7, 2026-09-16; `_98-DEEP-REVIEW.md` B-06); the fourteen-canary count does not run |
| **Catches** | The three failures that fire when everything else looks green: a reconciliation run that found nothing, a verification contract whose seeded defect passed, a lane whose gates stopped discriminating. `absent` counts as `accepted` (`11` §4.2) — a missing canary fixture is a dead gate, not a skipped test, which is the correct polarity |
| **Misses** | **G-14.** The canary runner executes from `main`, which is the right separation — but `tools/train/**` reached `main` through this same train. A defective runner promoted once verifies every subsequent cycle with a compromised instrument, and the only detector is the deadlock detector's own planted pair (`06` §10 step 1), which tests a different code path |

---

### A-9 — Nightly drills

`selfci-nightly.yml` injects one known-bad change per lane onto `drill/<cycle>/L<n>`, never onto the
lane's branch, on a **hosted** runner, and requires `DRILL L<n> rejected=1`.

**Catches:** a lane whose suite has stopped discriminating but whose PRs happen not to trip it —
the anti-rubber-stamp control of `00` §4.3.
**Misses:** **G-08.** GATE B verifies the drill by `record-exists.sh records/gate-runs/<cycle>/drill-L<n>.yaml`.
Existence, not occurrence.

---

### A-10 — GATE B, the E2E, and the integration DoD

| | |
|---|---|
| **Named checks** | `make gate-integration CYCLE=` → **IG-01 … IG-12**; the pass test asserts `VERDICT=PASS GATE=integration`, **`canary=FOUND`** and **`negatives=24/24`** *separately and by name*, and `wc -l == 1` → `GATE-B-OPEN`. `e2e/run.sh` then `e2e/verdict.sh` → `VERDICT: PASS` with both floors, 118 positive checkpoints and 28 gates proven able to fail. `make dod-integration CYCLE=` → **DI-01 … DI-10**, asserting `canary=FOUND`, `canaries=14/14` and `e2e=PASS` separately. **NOT ARMED — excluded from counts, Phase 1+:** `make dod-integration` and `tools/train/**` (which the canary count depends on) are unbuilt paths (Founder decision A7, 2026-09-16; `_98-DEEP-REVIEW.md` B-06); the DI-01…DI-10 and canaries=14/14 counts do not run |
| **Catches** | The composition failures no lane can see: IG-02 every lane's suite green *after the other four landed*; IG-03 `stubbed=0`; IG-06 `classified=111/111 dangling_refs=0`; IG-07 `asserted_only=0`; IG-09 the independent verifier under a **different credential**; IG-10 `digest_mismatches=0 rebuilt=0`; IG-11 the ten-cycle rejection count. And `08` §7.2's rule, which is the sharpest sentence in the corpus: *a run with 118 green checkpoints and zero fired gates is a FAILED run* |
| **Misses** | **G-04** (three promotion commands, no precedence — `make train-promote`'s five conditions omit the 24-check battery, count integrity, the ratchet, the fixture gate and the E2E). **G-09** (`asserted_only=0` reads a field, not an observation). **G-15** (the full E2E cannot run at the cadence it is required at). **G-13** (`00` §5 T3 says "these ten checks" and lists eleven) |

---

### A-11 — Promotion to `main` (C9, 15:30)

`integration → main` is a pull request. `selfci-gate-b` is a required context. `main` carries full
branch protection with **no machine bypass actor** (PARTITION line 7, D89), so the merge needs a
human approval that, by invariant 9, cannot be the person who opened it.

**Catches:** a promotion of a SHA whose GATE B is closed; a machine attempting the merge.
**Misses:** **G-10.** The build has one human. `05` §7 handles the shortfall correctly in principle
— a declared, expiring bootstrap exception naming the gate, the compensating control, an owner and
a deactivation trigger — but nothing in the trace makes that exception *visible on the gate record
of every cycle it covers*, so a later reader sees `VERDICT=PASS GATE=integration … signer=paresh`
and has no way to know the independent-review clause was never armed.

**Task status finally becomes `accepted`** when `make dod-task TASK=L1-03-08` is re-run by L0
against `integration` head after the merge (`11` §2.5). A task MET on its branch and NOT-MET at
integration head is an **escape**, recorded under `11` §1.2 and routed as a new task. This is the
best-designed loop in the corpus: it is the only place where the level below is graded by the level
above with a record of the disagreement.

---

## 2. TRACE B-1 — an agent edits a foreign path

**Scenario.** The L3 agent, building the reconciler, finds that `schemas/registry/product.schema.json`
is missing a field its comparison set needs. The fix is obvious and two lines. It makes the fix.

| Step | Control | Result |
|---|---|---|
| 0 | `make dod-task` **DT-07** `changed=<n> foreign=0 outside_owns=0`; and `06` §5 C2's local `make lane-guard LANE=3` | Caught — on the agent's own machine, unobserved. If the agent ignores it, nothing is recorded |
| **+1** | `selfci-lane.yml` runs `make lane LANE=3`, which includes `make lane-guard LANE=3` | **First independent detection.** Blocks nothing: `selfci-lane` emits no required context |
| **+2** | PR opened. `lane-guard` (required context) **and** `LG-02` inside `make gate-lane` | **First blocking detection.** `LG-02 lane-guard FAIL lane=3 changed=14 foreign=1 unowned=0` / `foreign: schemas/registry/product.schema.json owner=lane1`. `05` §9 routes it: remove the path, file a Contract Change Request, and **do not edit `ownership.tsv`** |
| +2 | CODEOWNERS routes the foreign path to L1 — the second independent mechanism `04` NT-30 requires, so the gate is not a single point of failure | Redundant catch |
| +4 | `IG-08` lane-guard replay over `origin/main..origin/integration` | Catches a foreign path that entered inside a *merge commit* rather than in the diff |
| end of lane | `DL-10 boundary PASS commits=<n> foreign=0 contract_edits=0` over the lane's whole history | Catches a foreign-path commit cherry-picked in during an `R3` rebuild |
| every cycle | T3 check 4, `make lane-guard --cycle` | Catches a foreign path merged this cycle by any route |

**Caught: two steps later, blocking.** Five independent layers, three of them mechanical and
mutually redundant. This is the best-covered failure in the protocol, and `07` §8.3 even drills it
weekly against a throwaway branch, treating a *passing* lane-guard as the finding.

**What it still misses — and both are real:**

**G-01. The lane number comes from the branch name, not from the actor.**
`05` §6 compares each changed path's owner against `$LANE`; `10` §7.2 derives `$LANE` from
`GITHUB_HEAD_REF` with `cut -d/ -f2`. Nothing in the corpus binds an agent to a lane number. An
L3 agent that names its branch `lane/1/p1-schema-fix` is judged as L1, and `LG-02` passes on the
edit above. Every other control in the stack — CODEOWNERS, `DL-10`, `IG-08` — inherits the same
branch-derived lane. `06` §14 rule 3 states the prohibition; no check enforces the identity half
of it.

**G-02. `ownership.tsv` is reconciled against nothing.**
`05` §2.1 gives it twenty rows, L0-authored, protected from lanes by `LG-03` and from nobody else.
Meanwhile `06` §4 asserts `tools/train/**` is L0-owned "and the lane-guard configuration must list
it"; `08` §3.1 asserts `e2e/**` is L0-owned "in CODEOWNERS"; `02` §2 states that
`verification/acceptance/**` and `tools/at/**` are owned by nobody and that L0 must claim them;
`11` §0.2 adds `contracts/dod/**`. Four files assert ownership of paths that appear in no frozen
table. `owner-of.sh` returns `none` for all of them, which `LG-02` correctly fails as `unowned>0`
— so the *lane* is stopped, and the *protocol* is broken, and the error surfaces as a lane's
blocker rather than as L0's defect.

---

## 3. TRACE B-2 — an agent reports a passing test it never ran

**Scenario.** The L4 agent cannot get `tools/records/lane-negative.sh` to reject
`NEG-REC-003` (three stores past their write-freshness interval). Rather than open the blocker its
STOP rule requires, it writes the PR body from `manual/04` §10's template with a plausible
`GATE-RESULT` line: `assertions=87 failures=0 negatives_run=11 negatives_that_failed_correctly=11`.

| Step | Control | Result |
|---|---|---|
| 0 | `manual/04` V3 and the Prime Directive; DT-09 "output pasted verbatim from this session" | **Not a control.** There is no session artifact. `$EV` is deliberately outside the repository so it fails no lane-guard, which also means it is deliberately outside the evidence chain |
| **+1** | `selfci-lane.yml` re-runs `make lane LANE=4` on a runner and parses the *real* last `GATE-RESULT` line | **Caught.** The fabricated line never enters CI; the workflow reads `.gate/lane.log`, which it produced. `SELFCI FAIL non-discriminating 10/11` |
| **+2** | `LG-05 lane-suite` re-runs the suite from a clean checkout of the PR head; `LG-12` compares the CI conclusion with L0's local `make gate-lane` verdict | **Caught and blocking.** A doctored `.gate/lane.verdict` produces `delta=1`, and `05` §9 is explicit: never take the greener of the two verdicts |
| +4 | `11` §2.5 re-derivation at integration head turns `integrated` into `accepted`; an escape is recorded | Third catch |
| +5 | `06` §8: `at_reproduced` is computed by re-running L0's harness. Invariant 20 — "a lane's claim is an input to the check, never the result of it". TRAIN-10 fires on `at_claimed_unreproduced` | Fourth catch |

**Caught: one step later, blocking at two.** For anything CI can re-execute, this failure is
closed by construction — the fabrication has no surface to live on, because every consumer of the
claim recomputes it.

**What it misses is the largest gap in the corpus.** The re-execution defence covers exactly the
claims that are re-executable. It does not cover:

| Claim class | Where it is recorded | What checks it | Why the check is not a check |
|---|---|---|---|
| The nightly drill rejected the planted defect | `records/gate-runs/<cycle>/drill-L<n>.yaml` | GATE B step "Assert the drill records exist", `record-exists.sh` (`10` §7.4); T3 check 11 | Existence of a file. **G-08** |
| `AT-108`, `AT-109`, `AT-110`, `AT-022`, `AT-103` were **executed for real** on the live estate | `contracts/acceptance/AT-<nnn>.yaml` field `executed_for_real` | `IG-07 asserted_only=0`; `DP-06`; `DV-06` | Reads the same field the claim is written into. **G-09** |
| The four `H`-class drills of `02` §9.2 happened | `records/build-drills/`, `records/e2e/` | `07` §8 ("a drill with no record did not happen") | A record with no drill also passes |
| The rollback and restore of `R1`/`R2` were proven by a red-then-green pair | Revert PR body carrying two run URLs (`07` §R1.5) | Human reading of the PR body | The URLs are not machine-resolved; `07` §R1.5's STOP rule is stated to the operator, not to a gate |
| `PASS-BOOTSTRAP` skipped exactly the four independence gates | `records/e2e/<run-id>.yaml` `unproven_gates:` | `08` §8.4 requires a matching `exceptions.yaml` entry | The list of what was skipped is written by the thing that skipped it |
| The judgment lines on the cycle report | `docs/train/CYCLE-<date>.md` | `06` §8 marks three fields `# HUMAN`; `11` §9 requires `suspect_answer` non-null when a flag is 1 | Presence, never content |

Every row is a place where a claim reaches `main` on the strength of a file that asserts itself.

---

## 4. TRACE B-3 — a lane ships against a stale contract

**Scenario.** L3 builds `tools/provision/gen-codeowners` against `contracts/fixtures/C-07/stub/`
and `contracts/fixtures/C-07/expected/CODEOWNERS`, per `01` §5.2's stub strategy — which is correct
and mandated, because L5 does not merge until the end of the train. Three cycles later L5 lands its
real `access/model.yaml`, whose team-name resolution differs from the stub in one field.

| Step | Control | Result |
|---|---|---|
| 0–2 | T0, T1, `LG-05` | **Green, correctly.** The lane conforms to the frozen contract. `01` §5.2 is explicit that this is a real signal and explicitly *not* a claim that the producer has shipped |
| +2 | `LG-06 contract-tests PASS … fixtures_sha=<…> fixtures_match=1` | **Green.** `fixtures_match=1` proves the fixture tree is unmodified. It says nothing about currency. This is the load-bearing miss |
| +2 | `LG-01 rebase PASS behind=0` | Catches the *other* staleness — a contract change already merged to `integration`. An open Contract Change Request is invisible |
| +2 | `01` §5.2's reporting distinction, `C-07.L3 PASS (against stub)` vs `(against live producer)`, with stub-only cycles listed at the bottom of every run | The right instrument — **and it is a report line, not a gate** |
| **+4 (earliest)** | Post-merge CT on `integration` after **L5's** step, i.e. the last step of the cycle, four train steps after L3 merged | First point at which the divergence can be observed at all |
| +4 | `--fixture-parity` (`01` §5.4): re-validates every fixture against the real producer and compares field by field; divergence is **Blocking** and triaged by the four-row table, never patched at the fixture | **No job runs it.** `10` §7.3 runs the CT matrix, the replay, `fixtures-all`, `negative-audit`, the cache audit and the ratchet. Parity is absent |
| +5 | `IG-03 contract-tests PASS pairs=<n> … stubbed=0` and `DI-03 stubbed=0` | The correct gate, at promotion. But nothing in the corpus says **how `stubbed` is computed** — if it is a flag the harness sets rather than a fact derived from which implementation was on `PATH`, it is a self-assertion of the `B-2` class |
| +5 | `--mutation-drill` (`01` §7.2), mandatory "at every `integration → main` promotion" | **No job runs it** |

**Caught: four train steps later at the earliest, and only if `--fixture-parity` is run — which no
job does. Otherwise: at promotion, by `IG-03 stubbed=0`, or not at all.**

Three distinct misses sit inside this trace:

1. **The stub-to-live handoff is unwired.** The one instrument designed for exactly this failure
   is specified in `01` and invoked nowhere in `10`. (**G-06**)
2. **Two contract registers.** `00` §5 T2 defines ten pairs `CT-01…CT-10`; `01` §3 defines twelve
   contracts `C-01…C-12` with a different runner and a different id scheme. `C-02` (validator CLI
   exit codes), `C-11` (secret tiers) and `C-12` (version floor) have no CT counterpart and no CI
   job; `CT-06` (evidence chain) and `CT-10` (invariant classification map) have no C counterpart
   and therefore no stub, no negative proof, no comparison-count baseline and no mutation. The
   union is larger than either register and nothing reconciles them. (**G-05**)
3. **Nothing tests a contract against the specification.** `01` §5.3 rule 2 is right that the
   fixture is the contract and code moves to the fixture — but if L0 writes a fixture that is wrong
   relative to §90 or §40.1, both sides conform to it, every gate is green, and the error is
   structurally undetectable until a human reads the spec. `TRAIN-13` (three CCRs in five cycles
   for one area) is the only instrument, and it detects *pressure*, not *error*.

---

## 5. GAP LIST — where a failure reaches `main` uncaught

Ordered by consequence. Each row states the gap, the trace that exposes it, and the **specific
additional control** it needs. Every proposed control carries its own negative fixture, because a
control added to this protocol without one is subject to the protocol's own Rule Zero.

---

### G-01 — Lane identity is derived from a branch name

**Exposed by:** B-1. **Reaches `main`:** yes — a mislabelled branch passes `LG-02`, `IG-08`,
`DL-10` and CODEOWNERS routing, all of which read the same branch-derived lane number.

**Control needed.** An L0-owned `contracts/gate/lane-actors.tsv` mapping each lane to its declared
GitHub identity. `LG-02` gains two assertions: the PR author, and the author *and* committer of
every commit in `origin/integration...HEAD`, must equal the declared actor for the branch's lane.
Output line gains `actor_match=1`. Negative fixture: a PR opened by L3's actor from a `lane/1/*`
branch, which `negative-battery.sh` must flip to `LG-02 … FAIL actor_match=0`.

---

### G-02 — `ownership.tsv` is reconciled against neither PARTITION nor the tree

**Exposed by:** B-1. **Reaches `main`:** yes — a widened glob or a path claimed in prose by four
files and by no row.

**Control needed.** `GATE-L0-003 ownership-coverage`, run in `selfci-meta` (so it is a required
context) with three assertions: (a) the eighteen lane rows of `ownership.tsv` are byte-identical to
a machine extract of PARTITION's path table; (b) `git ls-files | owner-of.sh` returns a lane for
**100%** of tracked paths — `unowned=0` over the whole tree, not only over a diff; (c) every path
asserted L0-owned in prose (`tools/train/**`, `e2e/**`, `verification/acceptance/**`, `tools/at/**`,
`contracts/dod/**`) carries a row. Negative fixtures: one glob widening L3 into
`schemas/registry/**`, and one new untracked-owner directory; both must fail.

---

### G-03 — Three incompatible train-halt rules

**Exposed by:** A-5. **Reaches `main`:** yes, by the worse route — the wrong halt semantics either
freeze a healthy train or continue a poisoned one, and both are defensible by citation.

**Control needed.** One authoritative halt table in a single file, plus a mechanical
`tools/train/state/TRAIN-STATE` token (`RUNNING` | `HALTED` | `FROZEN`) that `make train-merge`,
`make train-promote` and `make gate-integration` all read and refuse to run against. The table must
resolve, by name, at minimum: smoke-tier failure at a train step; T2 failure pre-merge; T2 failure
post-merge; canary `accepted`/`absent`; contract-suite exit 3. Negative fixture: set `FROZEN` and
assert the next `train-merge` refuses rather than proceeding.

---

### G-04 — Three promotion commands, no precedence

**Exposed by:** A-10. **Reaches `main`:** yes. `make train-promote`'s five conditions (`06` §5 C9)
omit the 24-check negative battery, count integrity, the assertion ratchet, the fixture gate, the
lane suites at merged head, and the E2E. It is the command the cycle checklist in `06` §15 actually
runs.

**Control needed.** Redefine `train-promote` as a thin wrapper that refuses unless
`.dod/integration.stdout` carries `DOD-VERDICT=MET LEVEL=integration` **for this exact HEAD sha**,
and `DI-01` already carries GATE B. Print the resolved chain on refusal. Negative fixture: a
`GATE-B-CLOSED` verdict on file with all five `06` conditions satisfied; `train-promote` must
refuse.

---

### G-05 — Two contract registers with no reconciliation

**Exposed by:** B-3. **Reaches `main`:** yes. `C-02`, `C-11` and `C-12` have no CI job; `N-12` —
the canary for a lane silently dropping v1 support — never executes.

**Control needed.** One register, `contracts/register.yaml`, as the single source. The
`selfci-integration.yml` matrix is **generated** from it at run time via a step output rather than
hard-coded. Add `GATE-L0-021 register-parity` to `selfci-meta`: the matrix cardinality, the
`expected-counts.tsv` row count and the register row count must be three equal numbers — the
three-way agreement discipline of `05` §8 applied to the register itself. Negative fixture: delete
one row from the matrix and require `narrowed=1`.

---

### G-06 — Four mandated instruments are invoked by no job

**Exposed by:** B-3, and A-6. **Reaches `main`:** yes. Specified as mandatory, wired nowhere:

| Instrument | Mandated in | Invoked in `10` |
|---|---|---|
| `run-contract-tests.sh --fixture-parity` | `01` §5.4, "required the first cycle after any producer lane merges" | no |
| `run-contract-tests.sh --mutation-drill` | `01` §7.2, "at every `integration → main` promotion" | no |
| `tools/at/run-at.sh` at PR time + `prove-twin.sh` on touched `implements:` paths | `02` §11.5 | no |
| `--negative-proof` as part of the full run | `01` §7.1 | no |

**Control needed.** Wire all four: parity into `selfci-integration.yml` after each train step;
mutation drill and negative-proof into `selfci-gate-b.yml`; the AT harness and twin runner into
`selfci-gate-a.yml`. Then make **`stubbed` a derived fact, not a flag** — the harness records, per
consumer run, which producer implementation was on `PATH`, and `IG-03` computes `stubbed` from that
record. Assign `verification/acceptance/**` and `tools/at/**` to L0 in `ownership.tsv` in the same
change (`02` §2 has been asking). Negative fixture: force one consumer onto its stub and require
`IG-03 … FAIL stubbed=1` and GATE B closed.

---

### G-07 — The post-merge integration run blocks nothing

**Exposed by:** A-6. **Reaches `main`:** yes. Ten CT pairs, the lane-guard replay, the fixture
gate, the negative audit, the cache audit and the assertion ratchet all run on `push: integration`
and emit no required context.

**Control needed.** A required context on the `integration → main` PR that reads the **latest
`selfci-integration` conclusion for the exact SHA being promoted** and fails on anything other than
`success` — and fails when no such run exists for that SHA, because absence of a run is a FAIL
under Rule Zero, never an absence of a problem. Negative fixture: promote a SHA carrying no
post-merge run and require the gate to close.

---

### G-08 — Drill records are checked for existence, not occurrence

**Exposed by:** A-9, B-2. **Reaches `main`:** yes. The anti-rubber-stamp control of the whole
protocol is satisfied by a well-formed file.

**Control needed.** Every drill record must carry `run_id`, `runner_class: github-hosted`, the
injected defect's id drawn from that lane's own `gates/*.yaml` `proves:` set, the id of the gate
that rejected it, and that gate's verbatim FAIL line. GATE B must resolve the `run_id` to a real
workflow run whose head SHA belongs to this cycle, and must assert the defect id exists in that
lane's gate declarations. Apply the same shape to `records/build-drills/` (`07` §8) and
`records/dod/drills/` (`11` §1.4). Negative fixture: a hand-written drill record with a valid shape
and no resolvable `run_id`; GATE B must close.

---

### G-09 — `executed_for_real` is a field, not an observation

**Exposed by:** B-2. **Reaches `main`:** yes, and this is the highest-consequence row in the list,
because the tests it covers are the ones that prove boundaries rather than assert them: **AT-110**
(the reconciler credential, the system's most privileged identity, §99.6 risk 6), **AT-108**,
**AT-109**, **AT-103**, **AT-022**. `IG-07 asserted_only=0` reads the field the claim is written
into. `00` §5 T4 states the rule — "a green simulated run is not a pass" — and provides no
mechanism to tell the two apart.

**Control needed.** An execution attestation per `executed_for_real` AT, carrying (a) the run id of
a job on the privileged **hosted** runner, (b) the target host or credential identity the attempt
used, and (c) the refusal text captured from the **target system**, not from the harness — the same
distinction `02` STOP rule 9 already draws for AT-109's host egress wall versus its harness
allowlist. `IG-07` must fail when the run id does not resolve or its head SHA is not an ancestor of
the cycle. For the four genuinely-`H` tests, the record names the human and a decision-record id,
and GATE B fails on a self-attested `H` result whose named human is the cycle signer. Negative
fixture: mark AT-110 executed with a fabricated run id; `IG-07` must fail.

---

### G-10 — The independent-review clause is unarmed and invisible

**Exposed by:** A-3 (LG-09), A-11. **Reaches `main`:** yes, permanently. `LG-09` needs a non-author
Write-holding human on five PRs a day; `IG-11` needs a signer who is not the author of the cycle's
largest diff; `07` §R2 needs a second approver before any `main` revert can be executed at all.
With L0 as the only human, all three run under `05` §7's bootstrap exception for the whole build,
and the anti-rubber-stamp instruments then measure one person approving their own train.

**Control needed.** Two parts. (1) Name the second human in `exceptions.yaml` before BT-0 with the
expiry, owner, deactivation trigger and compensating control that `05` §7 already requires — and
treat "no second human" as a **build-blocking** condition for the `R2` path specifically, since a
red `main` at 02:00 is otherwise unrecoverable by design. (2) Until then, make the exception
mechanically visible on every gate record: GATE A prints `human_review=BOOTSTRAP-EXC-<id>` in place
of a clean pass token, so no cycle can later be read as having had independent review. Negative
fixture: let the exception pass its expiry and require GATE A to close — AT-039's own mechanism,
pointed at the build.

---

### G-11 — The merge-train clock does not close

**Exposed by:** A-4, A-5. **Reaches `main`:** indirectly, and this is how a protocol dies. `06` §2
allocates 13:20–14:30, seventy minutes, for five lanes. `10` §4.1 computes the floor as
`5 × (rebase + GATE_A + merge) + integration_gate` under `strict_required_status_checks_policy: true`,
where every merge invalidates the four PRs behind it. At GATE A's 5-minute p50 that is ≈35 minutes;
at its own 12-minute `timeout-minutes` it exceeds the window before the integration gate starts,
and `06` allots C6 a further 35 minutes inside 14:30–15:05. One GATE A timeout consumes the cycle.
A protocol that cannot finish inside its own clock is abandoned in practice, one shortcut at a time.

**Control needed.** `make train-freeze` refuses to open a train whose trailing-median GATE A
duration × 5, plus the C6 budget, exceeds the remaining window, and records the refusal with its
arithmetic. A cycle that cannot complete is refused at 13:00 rather than abandoned at 14:30 —
`06` §5 C9 already establishes that a recorded refusal is a normal outcome and a silent one is not.
Negative fixture: set the trailing median to 15 minutes and require the freeze to refuse.

---

### G-12 — No per-lane wrong-thing detector, and L4 has almost none

**Exposed by:** A-0, and by `02` §9.3 saying it outright. **Reaches `main`:** yes. TRAIN-06
(coverage flatline) evaluates `at_verified_delta` across all lanes at a three-cycle latency. L4 is
primary on **two** in-scope acceptance tests out of 37, so L4 can ship a whole build's worth of
green with essentially no AT movement while TRAIN-06 reads as normal. `02` §9.3 states the
consequence precisely: *"L4 could ship a records schema nothing validates against and no acceptance
test would notice until G1."*

**Control needed.** Evaluate TRAIN-06 **per lane** against that lane's own in-scope denominator
(L1:9, L2:8, L3:7, L4:2, L5:7 per `02` §9.3), never against the portfolio total. For L4
specifically, name the substitute instrument and gate it: the contract halves of `C-03`, `C-04` and
`C-09`, plus the `STATIC-F3` checks of AT-071/075/083/085, each carrying its own assertion
ratchet. And require every status report to carry `02` §9.1's denominator — 37 of 110 — because a
percentage computed over "the tests I wrote" is not a coverage figure. Negative fixture: hold L4's
assertion count flat across three cycles and require the flatline to fire for L4 alone.

---

### G-13 — The gate-check count registry does not cover the gates

**Exposed by:** A-3 (LG-08), A-10. **Reaches `main`:** yes, quietly. `00` §5 T3 introduces "the
literal conjunction of these **ten** checks" and then lists **eleven** rows — and row 11 is the
drill-record check, the anti-rubber-stamp control. `05` §8 freezes `checks=24/24` for LG-01…12 and
IG-01…12 only; T3's numbered checks, the fourteen `CAN-*` canaries, the eleven `GATE-L0-0xx`
pipeline gates, the five `FG-x` fixture meta-gates and the 32 `NT-xx` are in no `COUNTS.tsv` row.
The three-way count agreement — the corpus's own best idea, built to catch any future regression in
§100's table — does not cover the corpus's own gates.

**Control needed.** Fix the ten/eleven discrepancy, and extend `COUNTS.tsv` to hold a declared
count for every gate family: `checks=24`, `t3=11`, `canaries=14`, `pipeline_gates=11`, `fixture_gates=5`,
`negative_tests=32`, each verified by the same declared / unique-ids / id-cells triple. Negative
fixture: delete T3 check 11 from its manifest and require `LG-08 … FAIL narrowed=1`.

---

### G-14 — The canary runner is promoted by the train it verifies

**Exposed by:** A-8. **Reaches `main`:** yes, once, and then permanently. `06` §5 C7 runs
`tools/train/run-canaries.sh` from a worktree of `origin/main` — the correct separation, and the
same reasoning §53.1 applies to the independent control verifier. But `tools/train/**` reached
`main` through this train. A defective runner promoted once verifies every subsequent cycle with a
compromised instrument, and reports fourteen armed gates while arming none.

**Control needed.** Pin the runner by tag under the `workflows/*`-class ruleset — updates and
deletions blocked, empty bypass-actor list — and have GATE B assert that the runner's tree SHA
equals the SHA recorded on the last green cycle record, so any change to the instrument is a
reviewed, visible event rather than a side effect of promotion. Negative fixture: move the tag and
require GATE B to close, which is `NT-12` pointed at the build's own tooling.

---

### G-15 — The E2E cannot run at the cadence it is required at

**Exposed by:** A-10. **Reaches `main`:** yes. `08` §8.1 requires a full run at **every**
`integration → main` promotion and nightly. `08` `CP-0003` asserts the pilot product **does not
exist** before the run, but only on the first run (`E2E_FIRST_RUN=1` / `--first-run`) — on every
subsequent run the pilot is the estate's permanent canary product and its presence is expected —
and `08` §2.1 says the product is never torn down. The full run is therefore a once-only artifact
by construction, while `DI-05` demands `e2e=PASS checkpoints=118/118 gates_proven=28/28` every
cycle. In practice `DI-05` will be satisfied by the first run's record, forever, and the 28-gate
floor — the strongest single assertion in the corpus — becomes a stored constant.

**Control needed.** Split it. A once-only `e2e-create` variant (E2E-01/02 with `CP-0003` intact),
recorded as the V1 exit artifact. A per-promotion `e2e-cycle` variant against a fresh per-cycle
product id (`pilot-<cycle>`), keeping stages E2E-03…E2E-13 and the whole 28-test negative suite.
State the checkpoint floors per variant, and make the gate fail when the variant named in the
record does not match the trigger that demanded it. Negative fixture: present the once-only
variant's record at a promotion and require refusal.

---

## 6. What holds — recorded so the gap list is not read as a verdict on the whole

Six things in this corpus are better than they need to be, and a later reader should not weaken them
while fixing the fifteen above.

1. **The vacuity exit code.** `00` §3's `2` = VACUOUS and `3` = NON-DISCRIMINATING, propagated
   through `DL-06`, `selfci-lane`'s parse step and the merge gate. Most protocols have no way to
   distinguish "nothing failed" from "nothing ran".
2. **Separating the verdict of record from CI.** `05` §2 and `10` §2: L2 owns the workflow that
   judges L2, and `LG-12`/`IG-12` catch the resulting conflict of interest by *disagreement* rather
   than by reading the diff. `CAN-SHIM` closes the same hole from the other side.
3. **Asserting losable tokens by name.** `05` §4.1 greps `canary=FOUND` and `negatives=24/24`
   separately from the verdict line, on the explicit reasoning that those are the two tokens a
   broken gate is most likely to lose while still printing a verdict. `11` §5.2 does the same for
   three tokens. This is a genuinely unusual piece of design.
4. **The escape ledger.** `11` §1.2: a level is graded by the level above it, and the disagreement
   is a record, not a silent fix. `accepted` derived at integration head is the only status in the
   build that means anything.
5. **`cp_refute`'s reason regex.** `08` §3.2: a negative test that fails for the wrong reason is
   reported as `WRONG REASON — the gate may be broken rather than working`. Almost every
   negative-test framework in existence accepts any non-zero exit.
6. **Positive controls paired to every negative.** `04` §6 and `03` §1.1: six refusals from a
   revoked token look identical to six refusals from a bounded one. The corpus never forgets the
   positive leg, and AT-110's own wording is quoted to justify it.

---

## 7. Summary

| Trace | First independent detection | First blocking detection | Reaches `main`? |
|---|---|---|---|
| A — a task that goes right | +1 (`selfci-lane`) | +2 (GATE A) | yes, correctly |
| B-1 — foreign path | +1 (`selfci-lane` → `lane-guard`) | +2 (`lane-guard` context, `LG-02`) | **no** — five redundant layers, unless the branch is mislabelled (**G-01**) |
| B-2 — fabricated pass | +1 (`selfci-lane` re-executes) | +2 (`LG-05`, `LG-12`) | **no** for re-executable claims; **yes** for drills, `executed_for_real`, `H`-class results and every human-judgment field (**G-08**, **G-09**) |
| B-3 — stale contract | +4 at the earliest, and only if `--fixture-parity` runs | +5 (`IG-03 stubbed=0`), if `stubbed` is derived rather than declared | **yes**, today — the instrument for this exact failure is specified and wired to nothing (**G-06**, **G-05**) |

Fifteen gaps. Twelve are wiring, precedence or arithmetic and are cheap to close. Three — **G-08**,
**G-09**, **G-10** — are the same defect wearing three costumes, and closing them means accepting
one uncomfortable sentence:

> **A record written by the party whose work it describes is a claim, not evidence — and this
> protocol currently promotes to `main` on five classes of such claim.**

The corpus already knows the sentence. `06` §8 states it exactly once, about acceptance-test
counts: *"a lane's claim is an input to the check, never the result of it."* Gaps G-08, G-09 and
G-10 are the places where that rule was written down and then not applied.
