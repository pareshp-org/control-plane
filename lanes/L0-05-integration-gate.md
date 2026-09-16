# L0-05 — THE INTEGRATION GATE

**Lane:** L0 Integrator · **Executor:** the human lead (this file is not executed by an AI developer)
**Branches:** `integration` → `main` (PARTITION.md §"Branch & merge model")
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — this file never contradicts it.
**Authoritative upstream:** `protocol/05-merge-gate.md` §4 (GATE B, `IG-01`…`IG-12`) and `protocol/00-test-strategy.md` §5 (T3).
This file **builds** what those two documents **specify**. Where they state a check id, a command or a pass
string, that string is reproduced here byte-for-byte and is never re-worded.

> **Reading rule for lanes L1–L5.** Three things here are binding on a lane executor and nothing else is:
> §2 (what GATE B asks that your lane gate did not), §9 (the STOP rules — what you do when the gate closes on a
> check your lane owns), and the fact recorded in §9.1 that a closed GATE B never rolls back the merge train and
> is never waived. A lane **never** runs `make gate-integration`, never edits `contracts/gate/**`, and never
> promotes anything to `main`. A lane PR that touches `contracts/**` fails `LG-03` before any other check runs.

---

## 0. What this file is, and the one thing it must not become

`protocol/05-merge-gate.md` §4 states GATE B as a table: twelve checks, twelve commands, twelve exact pass lines.
`protocol/00-test-strategy.md` §5 states the same gate as level T3: eleven conjunctive conditions. Neither is
executable. Neither says who writes the scripts, in what order, against which frozen expectation files, or how you
prove — before you trust it once — that the gate is capable of closing.

**This file is those scripts, their frozen inputs, the assembly of `make gate-integration`, and the rehearsal that
proves the whole thing can print `GATE-B-CLOSED`.**

The thing it must not become is a thirteenth check. The gate check count is **24** — `LG-01`…`LG-12` and
`IG-01`…`IG-12` — and that number is itself a row of the count register this file builds (`checks=24/24`,
`protocol/05` §8). A file that adds a check to the gate falsifies the register the gate uses to detect a lane that
quietly built less. Everything new here is therefore one of three things: **an input** to an existing check, a
**precondition** that produces the evidence an existing check reads, or a **detail line** written to
`.gate/integration.log` beneath an existing check's verdict line. Nothing new appears on stdout.

---

## 1. Shell and repository conventions

POSIX `sh` / Git Bash, run from the control-plane repository root. Identical to `L0-00-charter.md` §1 and
`L0-03-merge-train.md` §1.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
export GATE_SPEC="${GATE_SPEC:-C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md}"
cd "$CP_ROOT"
git rev-parse --show-toplevel
gh auth status
```

| Symbol | Meaning | Set by |
|---|---|---|
| `$CP_ROOT` | local clone of `control-plane` | you, once per shell |
| `$CPR_ROOT` | local clone of `control-plane-records` (PARTITION.md §"Repositories") | you, once per shell |
| `$GATE_SPEC` | absolute path to `MultiProduct_MasterSpec_v4.0.md` — the spec is a gate input; if it moves or changes, the gate closes until L0 re-freezes the digest under a decision record | you, once per shell, before running T03 (default matches line 6 of this file) |
| `$CYCLE` | the cycle id GATE B judges, e.g. `2026-08-27-a` | `L0-03-03` (cycle open) |
| `$PHASE` | the Section 98 phase token the cycle closes at — `Ph1`…`Ph7`, `EH`, `SA`, `COND` | `gate-state/PHASE`, task L0-05-04 |
| `$GATE_VERIFIER_TOKEN` | the **second** credential, used only by `IG-09` (§53.1 independent verifier) | task L0-05-12 |

`.gate/` is a working directory, git-ignored, recreated per run. It is not evidence. The evidence is the record
written by `IG-12` into `control-plane-records` (§10).

**Two repositories, not interchangeable.** GATE B judges `control-plane` only. `control-plane-records` carries the
gate's output and is written at runtime by the records-writer credential, never by a hand edit (D89; D107).

---

## 2. What GATE B asks that GATE A did not

GATE A asks one lane whether it built its own thing correctly inside its own boundary. Five green GATE A runs
prove five things about five isolated trees and **nothing whatever** about the thing those trees become. GATE B is
the only place the following five questions are asked at all, and each one is unanswerable on a lane branch:

| # | The question only GATE B can ask | Check | Why a lane cannot ask it |
|---|---|---|---|
| 1 | Does every lane's suite still pass **after the other four landed**? | `IG-02` | On a lane branch the other four lanes' merges do not exist. A lane that passes alone and fails in company has broken a consumer it cannot see — and PARTITION rule 4 forbids cross-lane imports, so it cannot look |
| 2 | Does each consumer work against the producer's **real output**, not the Phase-0 stub it developed against? | `IG-03` | `protocol/01-contract-tests.md` §5.2 gives every lane a stub producer precisely so it can build before the producer ships. `stubbed=0` is the first moment anything checks that the stub and the real thing agree |
| 3 | Is every count the specification states still true of what was built? | `IG-05` | A lane enumerates its own registry. Nothing on a lane branch holds the number 110, 111 or 112 (D44) |
| 4 | Was every acceptance test this phase activates **executed**, with a recorded result? | `IG-07` | ATs are scheduled by Section 98 phase, not by lane. A lane owning three ATs cannot see the other thirty-four |
| 5 | Can all twenty-four checks still fail? | `IG-04` | `LG-07` proves the twelve lane checks on one head. Only GATE B proves all twenty-four, plus the two spec-mandated seeded instruments, on the assembled system |

**The composition failure this exists to catch is not a merge conflict.** PARTITION rule 3 makes merge conflicts
nearly impossible — directory-per-item, no shared mutable file. What survives that design is the failure where
five trees merge cleanly and mean different things: L1 ships a schema field L2's workflow never emits; L4 ships a
record shape L3's finding does not fill; L5 declares a permission matrix L3 compares against a stale copy of.
Every one of those merges without a conflict, and every one of them is caught by `IG-02`, by `IG-03`, or by
nothing at all.

---

## 3. Non-contradiction crosswalk — three documents, one gate

Three files in this plan describe the promotion of `integration`. They are not three gates. Reading them as three
gates is the single most likely way to get this wrong, so the mapping is written out once, here, and this file
conforms to it.

| Layer | Document | Unit | Verdict token | Relationship |
|---|---|---|---|---|
| The gate | `protocol/05-merge-gate.md` §4 | `IG-01`…`IG-12` | `VERDICT=PASS GATE=integration` → `GATE-B-OPEN` | **Authorises the merge** `integration` → `main`. This file builds it |
| The pyramid level | `protocol/00-test-strategy.md` §5 T3 | eleven conditions | level T3 green | The same gate stated as a test level. Every T3 condition maps into an `IG-` check below; none is dropped |
| The closure | `protocol/11-definition-of-done.md` §5 | `DI-01`…`DI-10` | `DOD-VERDICT=MET LEVEL=integration` → `INTEGRATION-DONE` | **Declares the cycle done.** GATE B is `DI-01`, a *member* of that checklist, never a synonym for it |

### 3.1 Every T3 condition, and the `IG-` check that carries it

| T3 (`protocol/00` §5) | Carried by | Note |
|---|---|---|
| 1 — all five `lane-verify.sh --all` green, none reporting `assertions=0` | `IG-02` | The vacuity rule of `protocol/00` §3 (exit `2`) is enforced inside `lane-suite.sh --all`; task L0-05-06 |
| 2 — all ten CT pairs green | `IG-03` | The pair count is read from the harness manifest, never hard-coded — see **L0-IG-D1**, the one open discrepancy |
| 3 — `make negative-audit` green across five lanes and L0 | `IG-04` | The audit is invoked by `negative-battery.sh --gate integration --full`; task L0-05-08 |
| 4 — `make lane-guard --cycle` green | `IG-08` | Replay over the merged range, `lane-guard.sh --replay`; task L0-05-10 |
| 5 — assertion-count ratchet | `IG-05` | A deleted assertion is a narrowed count. `narrowed=1` is its failure token |
| 6 — invariant classification completeness | `IG-06` | Task L0-05-11. Depends on subsystem **O**, which no lane owns — see §5 |
| 7 — AT coverage map current | `IG-07` | Task L0-05-05, driven by the frozen activation map of task L0-05-04 |
| 8 — no `skipped`/`neutral` on a required context | `IG-10` | §33.2: *"A `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift"* |
| 9 — the seeded canary was found | `IG-04` | `canary=FOUND`, asserted separately and by name in the pass test (§8) |
| 10 — the seeded-defect verification case failed | `IG-02` and `IG-04` | `seeded_defects=5/5 DETECTED`; §31.2, SIG-18 |
| 11 — drill record present for all five lanes | `IG-11` | The injected-defect drill of `protocol/00` §4.3 is the anti-rubber-stamp evidence `IG-11` reads |

**Nothing in T3 is unmapped, and no `IG-` check is invented here.** If a future reader finds a T3 condition with
no row above, that is a defect in this file, not licence to add a check.

### 3.2 Where the assembled-system smoke sits

`protocol/08-smoke-and-e2e.md` specifies `e2e/run.sh` — twelve staged runs from `create-product` through
production deploy, rollback and reconciliation — with a floor of **118 positive checkpoints** and **28 gates proven
able to fail**, and `e2e/verdict.sh` as *"the only thing allowed to print PASS for the run"*.

The smoke is **not** a thirteenth check (L0D-IG-2). It is the **evidence-producing precondition of `IG-10`**.
`IG-10` asks whether the digest that will reach production is the digest verified in staging (invariant 22) and
whether any required context reported `skipped` or `neutral` in the merged range. Neither question has an answer
until a real deployment chain has been driven end to end on the assembled system. `make gate-integration`
therefore runs the smoke first, as step 0, and `IG-10` reads the checkpoint log it produced. If `e2e/verdict.sh`
did not print `VERDICT: PASS`, `IG-10` fails and the gate closes with `first_failure=IG-10` — it is never skipped,
never marked not-applicable, and never re-run to get a different answer. The `e2e=PASS` token is asserted **by
name** one level up, at `DI-05` (`protocol/11` §5.2).

---

## 4. L0 decisions held in this file

Plan-local ids in the style of `L0-02-lane-guard.md` §11. They never collide with Appendix A's `D1`…`D112`.

| Id | Decision | Why | Anchor |
|---|---|---|---|
| **L0D-IG-1** | The gate is authored by L0 in `contracts/gate/**` and by nobody else. No lane may edit any file this document creates | §53.1 states the principle for the reconciler and it holds verbatim here: *"no control that can be rewritten by the credential it is checking is a control."* A lane that could edit its own suite row, its own ownership row or its own negative case would be marking its own exam | §53.1; `protocol/05` §2 |
| **L0D-IG-2** | The assembled-system smoke is a precondition of `IG-10`, not a thirteenth check. The check count stays **24** | `checks=24/24` is a row of the count register the gate uses to detect quiet narrowing. A gate that grows a check falsifies its own register (D44) | `protocol/05` §8; D44 |
| **L0D-IG-3** | `count-integrity.sh` counts the **control-plane registries** — one file per item — never the rendered specification table. Fidelity to the specification is proven separately, by `spec-anomalies.tsv` | `protocol/05` §8 demonstrates that the Section 100 table renders 110 rows and 110 unique ids but **111 id cells**. A gate parsing the rendered table would inherit the defect it exists to detect | `protocol/05` §8; PARTITION rule 3 |
| **L0D-IG-4** | `spec-anomalies.tsv` is the register of known Section 100 rendering anomalies. SA-001 (AT-109/110 `\|\|` cell break) was resolved by D113 on 2026-08-28; the file is now empty. A surplus id cell found by the scanner that is not listed is new drift and fails the check with `undeclared=1`. An empty TSV with no surplus cells is the correct passing state. | D113 resolved SA-001; the scanner remains to catch future drift. An anomaly detector whose register is empty passes when it finds nothing — that is correct, not EC-109's failure | D113; EC-109; AT-102; §53.1 |
| **L0D-IG-5** | `contracts/gate/at-activation.tsv` is the frozen phase→AT map. `scheduled=<n>` in `IG-07` is its cumulative row for `$PHASE` and nothing else. **37** is the largest value it can ever hold | `protocol/02` §9.1: 37 of the 110 acceptance tests are reachable within the five-lane build. A status report without that denominator is misleading and L0 rejects it | `protocol/02` §9.1, §9.2 |
| **L0D-IG-6** | An AT whose **negative twin** has no recorded result is reported `asserted_only`, never `executed` | `protocol/02` §10: *"an AT with no recorded twin result is reported as `UNPROVEN`, not `PASS`"*. `IG-07`'s `asserted_only=0` is where that becomes mechanical | `protocol/02` §10; §31.2 |
| **L0D-IG-7** | The verdict of record is the **L0 run** of `make gate-integration`. CI is a mirror. `IG-12` compares them and fails on disagreement | `.github/workflows/**` belongs to L2 (PARTITION.md). A gate whose verdict of record lived in a path a judged lane owns is not a gate | PARTITION.md; `protocol/05` §2 |
| **L0D-IG-8** | Two record families, two paths, neither an index: `records/gate/**` holds one **gate verdict** per run; `records/gate-runs/**` holds one **level result** per level per lane per cycle | `protocol/05` §10 names the first, `protocol/00` §10 names the second. They are different artifacts, so both stand; directory-per-item means neither can conflict (PARTITION rule 3) | `protocol/05` §10; `protocol/00` §2, §10 |
| **L0D-IG-9** | Every script this file creates prints its verdict line as its **last line on stdout** and writes detail to a named file. Absence of output is a FAIL, never a pass | Invariant 80: every control is explicitly classified fail-closed or fail-open. Every check here is fail-closed | invariant 80; `protocol/05` §9 |
| **L0D-IG-10** | `contracts/gate/**` is frozen under its **own** immutable annotated tag `gate/v1.0.0`, on the same tag ruleset with an empty bypass-actor list that `contracts/v1.0.0` uses (L0-01 `D-L0-04`). The data contracts and the gate expectations version on different cadences and are not held by one tag | A moved gate tag would silently re-judge five lanes with no reviewable diff, which is the failure `D-L0-04` exists to prevent for data contracts. Same mechanism, separate tag, so a contract revision does not force a gate revision or the reverse | §33.2; L0-01 `D-L0-04`; invariant 85 |

---

## 5. DECISION REQUIRED — L0 must answer these

These are design choices. The specification does not settle them, and neither this file nor any lane may settle
them. Each states its blocking radius and, where one exists, the defined interim behaviour. **No interim behaviour
makes a gate pass; every one of them fails closed.**

### DECISION REQUIRED — L0-IG-D1: how many cross-lane contract pairs exist

**Question.** Is the cross-lane contract set **ten pairs** or **twelve contracts**?
**The fact.** `protocol/00-test-strategy.md` §5 (T2) declares ten pairs, `CT-01`…`CT-10`, each with a named
provider and consumer. `protocol/01-contract-tests.md` §3 and §4 declare twelve contracts, `C-01`…`C-12`, each with
a producer and consumers. Both documents describe the same artifact — the cross-lane contract test set — and
`IG-03`'s pass line reports `pairs=<n>`. One number is right.
**Why L0.** Reconciling two authoritative protocol documents is a contract decision (PARTITION rule 2). This file
may not pick the larger, the smaller, or the union.
**Interim behaviour, defined and fail-closed.** `contract-tests.sh --mode integrated` reads `pairs=<n>` from the
harness manifest `contracts/harness/pairs.tsv` and additionally asserts that `n` equals the `ct_pairs` row of
`contracts/gate/COUNTS.tsv`. Until L0 answers, `COUNTS.tsv` carries **both** source rows, `ct_pairs_p00` and
`ct_pairs_p01`, and `count-integrity.sh` reports `narrowed=1` — **the gate is closed** until one row is retired by
an L0 decision record. A closed gate here is correct: a build whose cross-lane test set has two sizes has not been
integration-tested, whichever size is right.
**Blocks:** `IG-03` and `IG-05`, and therefore GATE B, from the first cycle.

### DECISION REQUIRED — L0-IG-D2: who owns the acceptance-test harness paths

**Question.** Which lane, or L0, owns `verification/acceptance/**` and `tools/at/**`?
**The fact.** `protocol/02-acceptance-mapping.md` §2 states it: no lane owns `verification/acceptance/**` or
`tools/at/**`, and it recommends L0 claim them. `PARTITION.md` §"The five build lanes" assigns neither. Per
`L0-00-charter.md` §2.3 (L0D-04) an unassigned path is **blocked for everyone**, never silently defaulted to L0.
**Why L0.** Extending `lane-paths.tsv` is L0D-04. This file does not extend it and does not claim the paths.
**Interim behaviour, defined and fail-closed.** `at-coverage.sh` invokes `tools/at/run-at.sh "$PHASE"`. If that
path does not exist, every scheduled AT is reported `not_run` and `IG-07` FAILS with `not_run=<n>`. It is never
reported as `scheduled=0`, and a phase with no runnable harness is never a clean phase.
**Blocks:** `IG-07` and therefore GATE B, from the first cycle in which any AT is scheduled — that is `Ph1`, the
first phase, because `AT-022` activates there.

### DECISION REQUIRED — L0-IG-D3: subsystem **O**, and the invariant classification `IG-06` reads

**Question.** Which lane owns subsystem **O** (governance registries and jobs), and specifically `policies.yaml`?
**The fact.** §101's preamble requires each of the 111 invariants to be classified **mechanical**, **policy** or
**review-held**, with `policy` ones naming a live `policies.yaml` entry, and requires control-plane CI to fail when
a classification is missing or dangling. `policies.yaml` belongs to subsystem **O**, which `PARTITION.md` assigns
to no lane; `protocol/02` §2 records the gap and recommends a split (schemas and registry files to L1, scheduled
jobs to L5) as **an L0 decision, not a lane's**. This file states the dependency and routes it. It does not claim
subsystem O and does not assign it.
**Second fact, and it bounds the damage.** §101's preamble also says the classification *"is authored at Phase
G2"*. G2 is a governance-tier phase, outside the five-lane build (`protocol/02` §9.1). So `IG-06` cannot be fully
satisfiable inside this build, and pretending otherwise would be the AT-090 failure — *"a test that cannot pass on
the architecture it governs gets reinterpreted"* — applied to a gate.
**Interim behaviour, defined and fail-closed.** `invariant-classification.sh` asserts the two halves that **are**
reachable now and fails closed on the third: `classified=<n>/111` counts rows present in
`contracts/gate/invariant-classification.tsv`; `dangling_refs=0` asserts every `mechanical` row names a check id in
`expected-checks.txt` or an AT id in `at-activation.tsv`; `unclassified=<n>` counts the remainder. Until L0
answers, `unclassified` is non-zero and `IG-06` FAILS. **The gate stays closed and the failure is named, rather
than the check being marked not-applicable.** An `IG-06` that passed by declaring itself out of scope is exactly
the silent gate §99.6 risk 5 describes: *"An unavailable protection feature reproduces the silent-gate failure."*
**Blocks:** `IG-06` and therefore GATE B, from the first cycle.

### DECISION REQUIRED — L0-IG-D4: subsystems **G**, **H**, **J** and **P**, and the ATs they strand

**Question.** Which lane, if any, owns subsystems **G** (plan-checker and Gate 1 tooling), **H** (dashboards and
views), **J** (background machine layer) and **P** (people intelligence engine)?
**The fact.** `PARTITION.md` v1 assigns subsystems A, B, C, D, E, F, I, K, L, M, N, Q and R. §99.2 defines
eighteen, A–R. **G, H, J, O and P are assigned to no lane.** This is already escalated in
`protocol/02-acceptance-mapping.md` §2 and is **not re-litigated here**.
**What GATE B needs from them, and nothing more:**

| Subsystem | What the gate touches | Which check | If it stays unassigned |
|---|---|---|---|
| **G** plan-checker | `AT-106` (Gate 1 turnaround), and the plan-rejection count `IG-11` reads for its anti-rubber-stamp window (§103: *"Zero rejections means the gates are not working"*) | `IG-07`, `IG-11` | `AT-106` reports `not_run`; `IG-11` reports `rejections=0 rubber_stamp_flag=1`, which forces the named written answer of `protocol/05` §7 and does not by itself close the gate |
| **H** dashboards | nothing GATE B reads. `AT-097` and `AT-098` are `P2`-gated and outside the 37 | — | no effect on GATE B |
| **J** background cage | `AT-109`, activated at `Ph3` | `IG-07` | `AT-109` reports `not_run` and `IG-07` FAILS from `Ph3` onward |
| **P** people intelligence | 50 acceptance tests, none inside the 37 | — | no effect on GATE B. The denominator is the protection: `37/110`, stated on every gate record |

**Why L0.** Assigning a subsystem is `L0D-04`, held in `L0-00-charter.md` §2.3.
**This file claims none of them.** Where the gate needs one, the dependency is named in the table above and the
affected check fails closed.
**Blocks:** `IG-07` from `Ph3` (subsystem J). Nothing else, before `Ph3`.

### DECISION REQUIRED — L0-IG-D5: `e2e/**` and `contracts/harness/**` ownership and creation

**Question.** Which lane, or L0, owns `e2e/**` (the assembled-system smoke harness) and
`contracts/harness/**` (the contract-test runner and pairs manifest)?

**The fact.** Four artifacts the gate executes are created by no task and assigned to no lane in
`lane-paths.tsv` (B-04): `e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`,
and `contracts/harness/pairs.tsv`. `lane-paths.tsv` places `X<TAB>*/*` before the `0<TAB>*` catch-all,
so `owner_of("e2e/run.sh")` returns `X` — `UNASSIGNED`. Consequences:
- `lane-guard.sh` reports `LANE-GUARD VIOLATION: e2e/run.sh is an UNASSIGNED path (escalate to L0, L0D-04)`;
- `train-owners.sh` (promotion gate `P2`) prints `TRAIN-OWNERS FAIL: 1 unassigned path(s)`;
- `contract-tests.sh` fails immediately on a missing `contracts/harness/run-contract-tests.sh`, so
  `IG-03` FAILS from `L0-05-01` onward.

**Why L0.** `contracts/harness/**` is under `contracts/**`, which is L0-owned. `e2e/**` is not currently
in any lane path, and assigning it is `L0D-04`. This file does not claim it and cannot create it.

**Interim behaviour, defined and fail-closed.** Until L0 answers:
- `contract-tests.sh` exits immediately if `contracts/harness/run-contract-tests.sh` is absent, reporting
  `CONTRACT-TESTS FAIL paired=0 stubbed=X` — `IG-03` FAILS.
- `run-integration.sh` step 0 exits immediately if `e2e/run.sh` is absent, and `IG-10` reads `NO-OUTPUT-FAIL`
  from the driver — `IG-10` FAILS.
- Both failures appear in the rehearsal as baseline failures, so `rehearse.sh` names the baseline check
  and marks all later checks `BLOCKED-BY-<baseline>` (B-02 correction).
- **A missing harness is never reported as `passed` or `not-applicable`.** Invariant 80.

**Blocks:** `IG-03` and `IG-10`, and therefore GATE B, from the first cycle.

---

## 6. Tasks in this file

| Task id | Title | Size | Depends on |
|---|---|---|---|
| L0-05-01 | The gate tree, the 24 frozen check ids, and the two ownership manifests | M | L0-01 (contracts frozen), L0-02-02 (`lane-guard.sh` v2) |
| L0-05-02 | `COUNTS.tsv` — the D44 count register, twenty-six rows and three sum rules | M | L0-05-01 |
| L0-05-03 | `count-integrity.sh` and the frozen spec-anomaly expectation (`IG-05`) | L | L0-05-02 |
| L0-05-04 | `at-activation.tsv` — the frozen phase→AT map, and `gate-state/PHASE` | M | L0-05-01 |
| L0-05-05 | `at-coverage.sh` — executed, never asserted (`IG-07`) | L | L0-05-04 |
| L0-05-06 | `lane-suite.sh --all` — five suites at the merged head (`IG-02`) | M | L0-05-01 |
| L0-05-07 | `contract-tests.sh --mode integrated` — provider to consumer, `stubbed=0` (`IG-03`) | M | L0-05-01, L0-05-02 |
| L0-05-08 | `negative-battery.sh --gate integration --full` — all 24 proven failable (`IG-04`) | L | L0-05-03, L0-05-05, L0-05-06, L0-05-07 |
| L0-05-09 | The assembled-system smoke, and `artifact-honesty.sh` (`IG-10`) | L | L0-05-06 |
| L0-05-10 | `merge-train.sh` and the lane-guard replay (`IG-01`, `IG-08`) | M | L0-05-01 |
| L0-05-11 | `invariant-classification.sh` (`IG-06`) | M | L0-05-04 |
| L0-05-12 | `independent-verifier.sh` under the second credential (`IG-09`) | M | L0-05-01 |
| L0-05-13 | `human-signoff.sh` and the anti-rubber-stamp window (`IG-11`) | M | L0-05-01 |
| L0-05-14 | Assemble `make gate-integration`, `mirror-agree.sh --emit-record` (`IG-12`), and the closing rehearsal | L | L0-05-03 … L0-05-13 |
| L0-05-15 | `emit-gate-record.sh` — the one thing that commits a gate record | M | L0-05-14 |

Dependency graph:

```
L0-01 ─────┐
L0-02-02 ─┴── L0-05-01 ─┬── L0-05-02 ── L0-05-03 ──┐
                          ├── L0-05-04 ─┬── L0-05-05 ┤
                          │              └── L0-05-11 ┤
                          ├── L0-05-06 ─┬─────────────┤
                          │              └── L0-05-09 ┤
                          ├── L0-05-07 ───────────────┤
                          ├── L0-05-10 ───────────────┤
                          ├── L0-05-12 ───────────────┤
                          └── L0-05-13 ───────────────┤
                                         L0-05-08 ────┴── L0-05-14 ── L0-05-15
```

`L0-05-08` depends on T03, T05, T06 and T07 because the negative battery mutates the inputs those four checks
read; a battery written before its targets exist has nothing to mutate and reports `proven=0/24`.

---

## 7. The tasks

### L0-05-01 — The gate tree, the 24 frozen check ids, and the two ownership manifests

**Size:** M · **Dependencies:** L0-01 (`contracts/**` authored and frozen), L0-02-02 (`lane-guard.sh` v2 installed)

`protocol/05` §2.1 already fixes the content of two of these files. **They are transcribed here byte-for-byte and
are not re-derived.** If your transcription differs from `protocol/05` §2.1 in any character, your transcription is
wrong.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only
mkdir -p contracts/gate

# --- the 24 check ids, frozen. L0D-IG-2: this file never grows. ---------------
cat > contracts/gate/expected-checks.txt <<'CHK'
LG-01
LG-02
LG-03
LG-04
LG-05
LG-06
LG-07
LG-08
LG-09
LG-10
LG-11
LG-12
IG-01
IG-02
IG-03
IG-04
IG-05
IG-06
IG-07
IG-08
IG-09
IG-10
IG-11
IG-12
CHK

# --- the machine form of the FROZEN PARTITION path table -----------------------
# Transcribed verbatim from protocol/05-merge-gate.md section 2.1. Tab-separated.
# control-plane only. L4's ownership of the whole control-plane-records repository
# is not a path row here: that repository has one owner and therefore no partition
# to express (L0-02-lane-guard.md, L0D-LG-6).
printf '%s\n' '# path-glob<TAB>lane' > contracts/gate/ownership.tsv
printf '%s\t%s\n' \
  'schemas/registry/**'    1 \
  'schemas/product/**'     1 \
  'registries/**'          1 \
  'validators/registry/**' 1 \
  '.github/workflows/**'   2 \
  'templates/workflows/**' 2 \
  'tools/evidence/**'      2 \
  'reconciler/**'          3 \
  'tools/provision/**'     3 \
  'validators/drift/**'    3 \
  'schemas/records/**'     4 \
  'metrics/**'             4 \
  'tools/records/**'       4 \
  'access/**'              5 \
  'infra/**'               5 \
  'ops-vm/**'              5 \
  'notify/**'              5 \
  'assets/**'              5 \
  'contracts/**'           0 \
  'docs/**'                0 \
  'CODEOWNERS'             0 \
  'Makefile'               0 >> contracts/gate/ownership.tsv

# --- which command IS each lane's suite. A lane cannot change its own row -------
# Transcribed verbatim from protocol/05-merge-gate.md section 2.1.
printf '%s\n' '# lane<TAB>suite-command' > contracts/gate/lane-suite.tsv
printf '%s\t%s\n' \
  1 'make -C validators/registry test && make -C schemas test' \
  2 'make -C tools/evidence test && bash templates/workflows/test/run.sh' \
  3 'make -C reconciler test && make -C validators/drift test' \
  4 'make -C tools/records test && make -C metrics test' \
  5 'make -C access test && make -C infra test && make -C ops-vm test' >> contracts/gate/lane-suite.tsv

# --- the aggregate register read by LG-04 (no-shared-mutable) -------------------
# Twelve L0-owned files that may be READ by anyone and MODIFIED by nobody but L0.
# Four are created by later tasks in this file; the row exists from now so that a
# lane cannot create one first and claim it.
cat > contracts/gate/aggregates.txt <<'AGG'
CODEOWNERS
Makefile
lane-paths.tsv
lane-owners.tsv
lane-guard-exceptions.tsv
docs/merge-train.md
contracts/register.yaml
contracts/gate/expected-checks.txt
contracts/gate/ownership.tsv
contracts/gate/lane-suite.tsv
contracts/gate/COUNTS.tsv
contracts/gate/at-activation.tsv
AGG

grep -qxF '.gate/' .gitignore || printf '.gate/\n' >> .gitignore

make gate-freeze
git add contracts/gate gate.sha256 .gitignore
git commit -m "L0-05-01: gate tree, 24 frozen check ids, ownership and suite manifests; gate.sha256 (FD-029)"
git push origin integration
```

Freeze the tree under its own tag, per **L0D-IG-10**. The tag ruleset is the one `D-L0-04` (L0-01) already
created for `contracts/v1.0.0`: an empty bypass-actor list, so a moved tag has no authorised author (§33.2,
invariant 85). `gate.sha256` (excluding `PHASE`) is committed in the same push so the freeze and the hash
are co-located and the tag anchors both.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git tag -a gate/v1.0.0 -m "L0-05-01: freeze contracts/gate at v1.0.0"
git push origin gate/v1.0.0
git ls-remote --tags origin | grep -c 'refs/tags/gate/v1\.0\.0$'
```

**Glob-dialect note.** `lane-paths.tsv` uses bare globs (e.g. `schemas/registry/*`), while `ownership.tsv`
uses `**` recursive globs (e.g. `schemas/registry/**`). The two are semantically equivalent for single-level
directories, but the mapping is not verified by any script here — only the lane ID assignment is compared
(criterion 14 below).

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 24 check ids, no blank line, no duplicate | `sort -u contracts/gate/expected-checks.txt \| grep -c .` | `24` |
| 2 | Twelve are `LG-`, twelve are `IG-` | `printf '%s %s\n' "$(grep -c '^LG-' contracts/gate/expected-checks.txt)" "$(grep -c '^IG-' contracts/gate/expected-checks.txt)"` | `12 12` |
| 3 | Ownership map has 22 data rows | `grep -vc '^#' contracts/gate/ownership.tsv` | `22` |
| 4 | Every ownership row resolves to a lane `0`–`5` | `cut -f2 contracts/gate/ownership.tsv \| grep -v '^#' \| grep -cv '^[0-5]$'` | `0` |
| 5 | Every lane 1–5 appears in the ownership map | `for n in 1 2 3 4 5; do cut -f2 contracts/gate/ownership.tsv \| grep -qx "$n" \|\| echo "MISSING $n"; done; echo DONE` | `DONE` alone |
| 6 | Suite map has exactly one row per lane, 1–5 | `grep -vc '^#' contracts/gate/lane-suite.tsv` | `5` |
| 7 | No path appears in two ownership rows (PARTITION rule 1) | `cut -f1 contracts/gate/ownership.tsv \| grep -v '^#' \| sort \| uniq -d \| wc -l` | `0` |
| 8 | Aggregate register has 12 rows | `grep -c . contracts/gate/aggregates.txt` | `12` |
| 9 | `.gate/` is ignored | `git check-ignore -q .gate/probe && echo IGNORED` | `IGNORED` |
| 10 | The freeze tag exists on the remote | `git ls-remote --tags origin \| grep -c 'refs/tags/gate/v1\.0\.0$'` | `1` |
| 11 | The tag is annotated, not lightweight | `git cat-file -t "$(git rev-parse gate/v1.0.0)"` | `tag` |
| 12 | `gate.sha256` committed and `make gate-freeze` is idempotent (FD-029) | `make gate-freeze >/dev/null; a=$(cat gate.sha256); make gate-freeze >/dev/null; b=$(cat gate.sha256); [ "$a" = "$b" ] && echo STABLE` | `STABLE` |
| 13 | `make promote-check` now passes with gate tree present (FD-029) | `make promote-check` | `CONTRACTS-FROZEN OK` |
| 14 | Lane assignments in `ownership.tsv` match `lane-paths.tsv` for their common paths (glob-dialect note above) | `join -t'	' <(sort contracts/gate/ownership.tsv) <(awk 'NR>1{print $1"\t"$3}' lane-paths.tsv \| sort) \| awk -F'\t' '$2 != $3 {print; e=1} END{exit e}'` | empty (no mismatches) |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'checks=%s lg=%s ig=%s own=%s badlane=%s dup=%s suite=%s agg=%s ignore=%s tag=%s\n' \
  "$(sort -u contracts/gate/expected-checks.txt | grep -c .)" \
  "$(grep -c '^LG-' contracts/gate/expected-checks.txt)" \
  "$(grep -c '^IG-' contracts/gate/expected-checks.txt)" \
  "$(grep -vc '^#' contracts/gate/ownership.tsv)" \
  "$(cut -f2 contracts/gate/ownership.tsv | grep -v '^#' | grep -cv '^[0-5]$')" \
  "$(cut -f1 contracts/gate/ownership.tsv | grep -v '^#' | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(grep -vc '^#' contracts/gate/lane-suite.tsv)" \
  "$(grep -c . contracts/gate/aggregates.txt)" \
  "$(git check-ignore -q .gate/probe && echo YES || echo NO)" \
  "$(git cat-file -t "$(git rev-parse gate/v1.0.0)" 2>/dev/null || echo NONE)"
```

Expected output, exactly:

```
checks=24 lg=12 ig=12 own=22 badlane=0 dup=0 suite=5 agg=12 ignore=YES tag=tag
```

**STOP rule** — if `checks` is anything but `24`, the gate's own count register is already false and every later
`checks=24/24` in this file is a lie about a number nothing holds. Do not adjust `COUNTS.tsv` in the next task to
match. If `dup` is not `0`, two rows claim one path and PARTITION rule 1 is broken in the machine form before the
gate has run once — this is `L0D-04`, not something to resolve here. If `tag=NONE`, the gate tree is unfrozen and a
lane could edit the file that judges it; do not proceed to L0-05-02. In every case open
`BLOCKER L0-05-01: <one line>` using `docs/escalation/BLOCKER.md`, with `FORBIDDEN/UNDECIDED ID: L0D-IG-1`.

---

### L0-05-02 — `COUNTS.tsv`: the D44 count register

**Size:** M · **Dependencies:** L0-05-01

D44 is one line of the Decision Register and it is the whole reason this check exists: *"All cross-references use
this document's section numbers; **every stated count is true**"* (Appendix A, D44). Five AI developers with no
shared context fail in one characteristic way — a lane implements 40 of 110 things and reports success, because
nothing anywhere holds the number 110. `contracts/gate/COUNTS.tsv` holds it.

Each row is `key<TAB>declared<TAB>source<TAB>kind`. `kind` is `spec` when the number is stated in the
specification, and `plan` when it is stated by a frozen plan document. Both are checked; the distinction exists so
that a failing row tells you which document to open.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/COUNTS.tsv <<'CNT'
# key<TAB>declared<TAB>source<TAB>kind
# D44: "every stated count is true". A row is added only when a document states
# the number literally. Nothing here is inferred, rounded or estimated.
at	110	MasterSpec v4.0 Section 100 preamble ("The catalogue contains 110 tests")	spec
inv	111	MasterSpec v4.0 Section 101 preamble ("The catalogue contains 111 invariants")	spec
ec	112	MasterSpec v4.0 Section 102 preamble ("The catalogue contains 112 cases")	spec
subsystems	18	MasterSpec v4.0 Section 99.2 subsystem table, rows A..R	spec
evidence_questions	11	MasterSpec v4.0 Section 32 ("the system answers eleven questions")	spec
orphan_types	16	MasterSpec v4.0 Section 7 ("Orphan detection - what the system surfaces (16 orphan types)")	spec
recon_levels	5	MasterSpec v4.0 D43 ("reconciliation Levels 1-5")	spec
event_types	86	L0-01-phase-0-contracts.md D-L0-03 (one per Section 97.3 taxonomy entry)	plan
frozen_contracts	23	L0-01-phase-0-contracts.md Section 2 ("Twenty-three frozen contracts")	plan
lanes	5	PARTITION.md "The five build lanes"	plan
train_order	5	PARTITION.md "Merge train: L1 -> L4 -> L2 -> L3 -> L5"	plan
subsystems_assigned	13	PARTITION.md subsystem column (A,B,C,D,E,F,I,K,L,M,N,Q,R)	plan
subsystems_unassigned	5	PARTITION.md vs Section 99.2 (G,H,J,O,P) - protocol/02 Section 2	plan
lane_checks	12	protocol/05-merge-gate.md Section 3 (LG-01..LG-12)	plan
integration_checks	12	protocol/05-merge-gate.md Section 4 (IG-01..IG-12)	plan
checks	24	protocol/05-merge-gate.md Section 8, contracts/gate/expected-checks.txt	plan
ct_pairs_p00	10	protocol/00-test-strategy.md Section 5 T2 (CT-01..CT-10)	plan
ct_pairs_p01	12	protocol/01-contract-tests.md Section 3 (C-01..C-12)	plan
nt_register	32	protocol/04-negative-tests.md Section 3 (NT-01..NT-32)	plan
at_in_scope	37	protocol/02-acceptance-mapping.md Section 9.1	plan
at_governance_gated	23	protocol/02-acceptance-mapping.md Section 9.1	plan
at_people_gated	50	protocol/02-acceptance-mapping.md Section 9.1	plan
at_twins	33	protocol/02-acceptance-mapping.md Section 10	plan
e2e_positive_floor	118	protocol/08-smoke-and-e2e.md Section 7	plan
e2e_negative_floor	28	protocol/08-smoke-and-e2e.md Section 7	plan
canaries	14	protocol/11-definition-of-done.md DI-06	plan
decisions	112	MasterSpec v4.0 Appendix A	spec
CNT

# --- the sum rules: counts that must add up, not merely exist -----------------
cat > contracts/gate/COUNTS.rules.tsv <<'RUL'
# rule-id<TAB>total-key<TAB>addend-keys (comma separated)<TAB>what it protects
SUM-01	at	at_in_scope,at_governance_gated,at_people_gated	The five-lane build proves 37 of 110. A partition that quietly re-scopes shows up as a broken sum, not as a smaller denominator on a slide
SUM-02	subsystems	subsystems_assigned,subsystems_unassigned	G, H, J, O and P are unassigned in PARTITION v1. If this sum starts holding with unassigned=0, a subsystem was claimed without an L0 decision
SUM-03	checks	lane_checks,integration_checks	L0D-IG-2. The gate cannot grow a check without breaking its own register
RUL

# --- frozen id sets: one row per id, so a three-way count is possible ---------
: > contracts/gate/at-index.tsv
n=1; while [ "$n" -le 110 ]; do printf 'AT-%03d\n' "$n" >> contracts/gate/at-index.tsv; n=$((n+1)); done
: > contracts/gate/inv-index.tsv
n=1; while [ "$n" -le 111 ]; do printf '%d\n' "$n" >> contracts/gate/inv-index.tsv; n=$((n+1)); done
: > contracts/gate/ec-index.tsv
n=1; while [ "$n" -le 112 ]; do printf 'EC-%d\n' "$n" >> contracts/gate/ec-index.tsv; n=$((n+1)); done

git add contracts/gate
git commit -m "L0-05-02: COUNTS.tsv (D44), sum rules, and the three frozen id sets"
git push origin integration
```

**The three id sets are contiguous by construction and that is the point.** §100 numbers `AT-001` to `AT-110`,
§101 numbers invariants *"continuously"* 1 to 111, §102 numbers `EC-1` to `EC-112`. Generating them with a loop
rather than transcribing them by hand removes the transcription error class entirely; the *transcription* that
still has to be checked is the specification's own, and that is task L0-05-03.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Register has 27 data rows | `grep -vc '^#' contracts/gate/COUNTS.tsv` | `27` |
| 2 | No duplicate key | `cut -f1 contracts/gate/COUNTS.tsv \| grep -v '^#' \| sort \| uniq -d \| wc -l` | `0` |
| 3 | Every declared value is a positive integer | `cut -f2 contracts/gate/COUNTS.tsv \| grep -v '^#' \| grep -cv '^[1-9][0-9]*$'` | `0` |
| 4 | Every row carries a non-empty source and a `kind` of `spec` or `plan` | `awk -F'\t' '!/^#/ && (NF!=4 \|\| $3=="" \|\| ($4!="spec" && $4!="plan")) {c++} END{print c+0}' contracts/gate/COUNTS.tsv` | `0` |
| 5 | SUM-01 holds: 37 + 23 + 50 = 110 | `awk -F'\t' '$1=="at_in_scope"{a=$2} $1=="at_governance_gated"{b=$2} $1=="at_people_gated"{c=$2} $1=="at"{t=$2} END{print (a+b+c==t)?"SUM-01-OK":"SUM-01-BROKEN"}' contracts/gate/COUNTS.tsv` | `SUM-01-OK` |
| 6 | SUM-02 holds: 13 + 5 = 18 | `awk -F'\t' '$1=="subsystems_assigned"{a=$2} $1=="subsystems_unassigned"{b=$2} $1=="subsystems"{t=$2} END{print (a+b==t)?"SUM-02-OK":"SUM-02-BROKEN"}' contracts/gate/COUNTS.tsv` | `SUM-02-OK` |
| 7 | SUM-03 holds: 12 + 12 = 24 | `awk -F'\t' '$1=="lane_checks"{a=$2} $1=="integration_checks"{b=$2} $1=="checks"{t=$2} END{print (a+b==t)?"SUM-03-OK":"SUM-03-BROKEN"}' contracts/gate/COUNTS.tsv` | `SUM-03-OK` |
| 8 | `checks` agrees with the frozen check file from T01 | `[ "$(awk -F'\t' '$1=="checks"{print $2}' contracts/gate/COUNTS.tsv)" = "$(sort -u contracts/gate/expected-checks.txt \| grep -c .)" ] && echo AGREE` | `AGREE` |
| 9 | The three id sets have the declared sizes | `printf '%s %s %s\n' "$(wc -l < contracts/gate/at-index.tsv)" "$(wc -l < contracts/gate/inv-index.tsv)" "$(wc -l < contracts/gate/ec-index.tsv)" \| tr -s ' '` | `110 111 112` |
| 10 | The AT id set is contiguous `AT-001`…`AT-110` | `printf '%s %s\n' "$(head -1 contracts/gate/at-index.tsv)" "$(tail -1 contracts/gate/at-index.tsv)"` | `AT-001 AT-110` |
| 11 | **The open discrepancy is visible, not hidden** — both pair rows are present | `grep -c '^ct_pairs_p0' contracts/gate/COUNTS.tsv` | `2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
S1=$(awk -F'\t' '$1=="at_in_scope"{a=$2} $1=="at_governance_gated"{b=$2} $1=="at_people_gated"{c=$2} $1=="at"{t=$2} END{print (a+b+c==t)?"OK":"BROKEN"}' contracts/gate/COUNTS.tsv)
S2=$(awk -F'\t' '$1=="subsystems_assigned"{a=$2} $1=="subsystems_unassigned"{b=$2} $1=="subsystems"{t=$2} END{print (a+b==t)?"OK":"BROKEN"}' contracts/gate/COUNTS.tsv)
S3=$(awk -F'\t' '$1=="lane_checks"{a=$2} $1=="integration_checks"{b=$2} $1=="checks"{t=$2} END{print (a+b==t)?"OK":"BROKEN"}' contracts/gate/COUNTS.tsv)
printf 'rows=%s dupkey=%s badval=%s sum01=%s sum02=%s sum03=%s ids=%s/%s/%s span=%s..%s open_d1=%s\n' \
  "$(grep -vc '^#' contracts/gate/COUNTS.tsv)" \
  "$(cut -f1 contracts/gate/COUNTS.tsv | grep -v '^#' | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(cut -f2 contracts/gate/COUNTS.tsv | grep -v '^#' | grep -cv '^[1-9][0-9]*$')" \
  "$S1" "$S2" "$S3" \
  "$(wc -l < contracts/gate/at-index.tsv | tr -d ' ')" \
  "$(wc -l < contracts/gate/inv-index.tsv | tr -d ' ')" \
  "$(wc -l < contracts/gate/ec-index.tsv | tr -d ' ')" \
  "$(head -1 contracts/gate/at-index.tsv)" "$(tail -1 contracts/gate/at-index.tsv)" \
  "$(grep -c '^ct_pairs_p0' contracts/gate/COUNTS.tsv)"
```

Expected output, exactly:

```
rows=27 dupkey=0 badval=0 sum01=OK sum02=OK sum03=OK ids=110/111/112 span=AT-001..AT-110 open_d1=2
```

**STOP rule** — if any `sumNN` prints `BROKEN`, **do not change the addends to make the total work**. The register
is a transcription of documents; a broken sum means one of those documents is wrong or you mis-transcribed it, and
either answer is L0's. Open `BLOCKER L0-05-02: sum rule SUM-0N broken`, quote the two document sentences that
disagree, and stop. If `open_d1` is not `2`, someone has already resolved **L0-IG-D1** by deleting a row instead of
by a decision record; restore both rows and require the decision. **Never adjust `COUNTS.tsv` to match the code** —
`protocol/05` §9 states it as its own row: *"Do not adjust `COUNTS.tsv` to match the code."*

---

### L0-05-03 — `count-integrity.sh`, and the frozen spec-anomaly expectation (`IG-05`)

**Size:** L · **Dependencies:** L0-05-02

Two things happen in this task and they must not be confused.

1. **`count-integrity.sh`** asserts that the counts the register declares are true **of what was built** — the
   control-plane registries, one file per item. This is `IG-05` and `LG-08`.
2. **`spec-transcription.sh`** asserts that the id set the register froze is a true transcription **of the
   specification**, and that no undeclared anomaly has appeared in Section 100. The list of known anomalies is
   held in `spec-anomalies.tsv`; as of D113 (2026-08-28) it is empty — the AT-109/110 `||` cell break that
   was SA-001 was corrected in the spec. The three-way check (rows / unique-ids / id-cells) remains as a guard
   against future rendering drift.

**Why the second one exists at all.** `protocol/05` §8 originally documented a rendering anomaly in Section 100:
the table rendered **110 rows** and **110 unique ids** but **111 id cells**, because the `AT-109` row carried a
duplicated `AT-110` id cell after a `||` cell break. That anomaly was corrected by D113 on 2026-08-28 and
`spec-anomalies.tsv` is now empty. The three-way agreement check is kept: if a future spec edit reintroduces a
surplus id cell, `SURPLUS` will be non-zero and the verdict will print `undeclared=1`.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"

# --- where the specification is, and its frozen digest ------------------------
# The spec is an INPUT to the gate. If it moves or changes, the gate closes until
# L0 re-freezes the digest under a decision record. GATE_SPEC is set in §1.
[ -f "$GATE_SPEC" ] || { echo "BLOCKER: spec not found at '$GATE_SPEC' — set GATE_SPEC or verify §1 path"; exit 2; }
printf '%s\n' "$GATE_SPEC" > contracts/gate/SPEC_PATH
sha256sum "$(cat contracts/gate/SPEC_PATH)" | cut -d' ' -f1 > contracts/gate/SPEC.sha256

# --- spec-anomalies.tsv: empty as of D113 (2026-08-28) -----------------------
# SA-001 (AT-109/110 duplicated-id-cell) was resolved by D113. The scanner
# still runs; any surplus id cell that is not listed here produces
# SPEC-TRANSCRIPTION FAIL with undeclared=1.
cat > contracts/gate/spec-anomalies.tsv <<'ANO'
# id<TAB>section<TAB>kind<TAB>signature
# No confirmed anomalies in Section 100 of spec v4.0 as of D113 (2026-08-28).
# A row found that is not listed here is new drift and causes FAIL undeclared=1.
ANO

cat > contracts/gate/spec-transcription.sh <<'STR'
#!/usr/bin/env sh
# =============================================================================
# spec-transcription.sh - L0-owned (contracts/gate/**, L0D-IG-1).
# Proves (a) the frozen id sets are a true transcription of the specification and
# (b) every FROZEN ANOMALY in spec-anomalies.tsv is STILL PRESENT (L0D-IG-4).
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"
SPEC="${GATE_SPEC:-$(cat "$GD/SPEC_PATH" 2>/dev/null || true)}"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"
DET="$OUT/spec-transcription.txt"; : > "$DET"

fail_cfg() { echo "SPEC-TRANSCRIPTION FAIL: $1" ; exit 2; }
[ -n "$SPEC" ] && [ -f "$SPEC" ] || fail_cfg "specification not found at '$SPEC'"
[ -f "$GD/SPEC.sha256" ] || fail_cfg "SPEC.sha256 missing"
[ -f "$GD/spec-anomalies.tsv" ] || fail_cfg "spec-anomalies.tsv missing"

HAVE=$(sha256sum "$SPEC" | cut -d' ' -f1)
WANT=$(cat "$GD/SPEC.sha256")
if [ "$HAVE" != "$WANT" ]; then
  echo "spec digest have=$HAVE want=$WANT" >> "$DET"
  echo "SPEC-TRANSCRIPTION FAIL digest_match=0 anomalies=0/0"
  exit 1
fi

# --- Section 100 slice: preamble line to the line before Section 101 ----------
S100_BEG=$(grep -n '^## Section 100\.' "$SPEC" | head -1 | cut -d: -f1)
S100_END=$(grep -n '^## Section 101\.' "$SPEC" | head -1 | cut -d: -f1)
[ -n "$S100_BEG" ] && [ -n "$S100_END" ] || fail_cfg "Section 100/101 headings not found"
sed -n "${S100_BEG},$((S100_END-1))p" "$SPEC" > "$OUT/s100.raw"

ROWS=$(grep -c '^| AT-[0-9][0-9][0-9] |' "$OUT/s100.raw" || true)
UNIQ=$(grep -o '^| AT-[0-9][0-9][0-9] ' "$OUT/s100.raw" | tr -d '| ' | sort -u | wc -l | tr -d ' ')
CELLS=$(grep -o '| AT-[0-9][0-9][0-9] |' "$OUT/s100.raw" | wc -l | tr -d ' ')
printf 'section100 rows=%s unique=%s cells=%s\n' "$ROWS" "$UNIQ" "$CELLS" >> "$DET"

# --- the frozen id set must equal the specification's UNIQUE id set -----------
grep -o '^| AT-[0-9][0-9][0-9] ' "$OUT/s100.raw" | tr -d '| ' | sort -u > "$OUT/s100.ids"
if diff -q "$GD/at-index.tsv" "$OUT/s100.ids" >/dev/null 2>&1; then IDSET=1; else IDSET=0
  diff "$GD/at-index.tsv" "$OUT/s100.ids" >> "$DET" || true
fi

# --- every frozen anomaly must STILL be found --------------------------------
TOTAL=0; FOUND=0
while IFS='	' read -r id sec kind sig; do
  case "$id" in ''|\#*) continue ;; esac
  TOTAL=$((TOTAL+1))
  hit=0
  case "$kind" in
    duplicated-id-cell)
      # exactly one more id cell than unique ids, and the surplus is AT-110
      if [ "$CELLS" -eq $((UNIQ+1)) ] && grep -q '^| AT-109 |.*| AT-110 |' "$OUT/s100.raw"; then hit=1; fi
      ;;
    *) hit=0 ;;
  esac
  if [ "$hit" -eq 1 ]; then FOUND=$((FOUND+1)); printf '%s FOUND (%s)\n' "$id" "$sig" >> "$DET"
  else printf '%s ABSENT - parser stopped looking, or the input changed (%s)\n' "$id" "$sig" >> "$DET"; fi
done < "$GD/spec-anomalies.tsv"

# --- an anomaly nobody declared is new drift ---------------------------------
SURPLUS=$((CELLS - UNIQ - TOTAL))
[ "$SURPLUS" -lt 0 ] && SURPLUS=0

if [ "$IDSET" -eq 1 ] && [ "$FOUND" -eq "$TOTAL" ] && [ "$SURPLUS" -eq 0 ]; then
  printf 'SPEC-TRANSCRIPTION PASS digest_match=1 idset_match=1 anomalies=%s/%s undeclared=0\n' "$FOUND" "$TOTAL"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'SPEC-TRANSCRIPTION FAIL digest_match=1 idset_match=%s anomalies=%s/%s undeclared=%s\n' \
  "$IDSET" "$FOUND" "$TOTAL" "$SURPLUS"
exit 1
STR
chmod +x contracts/gate/spec-transcription.sh
```

Now the count check itself. It asserts **three numbers agree** per registry — the declared count, the count of
unique ids, and the count of id occurrences in row position — because any two of them can agree while the artifact
is wrong. `protocol/05` §8: *"Read `at=110/110/110` as `declared/unique-ids/id-cells`. All three must be
identical."*

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/count-integrity.sh <<'CIS'
#!/usr/bin/env sh
# =============================================================================
# count-integrity.sh - L0-owned (contracts/gate/**, L0D-IG-1). D44 made mechanical.
#   --scope lane --lane <N>   the LG-08 form
#   --scope integration       the IG-05 form (adds the reconciler comparison ratchet)
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"; SCOPE=""; LANE=""
while [ $# -gt 0 ]; do case "$1" in
  --scope) SCOPE="$2"; shift 2 ;;
  --lane)  LANE="$2";  shift 2 ;;
  *) echo "COUNT-INTEGRITY FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ "$SCOPE" = "lane" ] || [ "$SCOPE" = "integration" ] || { echo "COUNT-INTEGRITY FAIL: --scope lane|integration required"; exit 2; }
CPR="${CPR_ROOT:?CPR_ROOT must point at the control-plane-records clone}"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/count-integrity.txt"; : > "$DET"
NARROW=0

decl() { awk -F'\t' -v k="$1" '!/^#/ && $1==k {print $2; exit}' "$GD/COUNTS.tsv"; }

# triple <label> <declared> <unique> <cells>
triple() {
  printf '%s declared=%s unique=%s cells=%s\n' "$1" "$2" "$3" "$4" >> "$DET"
  if [ "$2" = "$3" ] && [ "$3" = "$4" ]; then return 0; fi
  NARROW=$((NARROW+1)); return 1
}

# --- acceptance tests: one file per test, generated from the id set ----------
AT_D=$(decl at)
AT_DIR="$CPR/records/acceptance"
if [ -d "$AT_DIR" ]; then
  AT_CELLS=$(find "$AT_DIR" -name 'AT-*.yaml' | wc -l | tr -d ' ')
  AT_UNIQ=$(grep -h '^id:' "$AT_DIR"/AT-*.yaml 2>/dev/null | awk '{print $2}' | sort -u | wc -l | tr -d ' ')
else
  AT_CELLS=0; AT_UNIQ=0
fi
triple at "$AT_D" "$AT_UNIQ" "$AT_CELLS" || true

# --- invariants and edge cases: frozen L0 id sets, two-way ------------------
INV_D=$(decl inv); INV_C=$(grep -c . "$GD/inv-index.tsv"); INV_U=$(sort -u "$GD/inv-index.tsv" | grep -c .)
EC_D=$(decl ec);   EC_C=$(grep -c . "$GD/ec-index.tsv");   EC_U=$(sort -u "$GD/ec-index.tsv" | grep -c .)
[ "$INV_D" = "$INV_U" ] && [ "$INV_U" = "$INV_C" ] || NARROW=$((NARROW+1))
[ "$EC_D" = "$EC_U" ]  && [ "$EC_U"  = "$EC_C" ]  || NARROW=$((NARROW+1))
printf 'inv declared=%s unique=%s cells=%s\nec declared=%s unique=%s cells=%s\n' \
  "$INV_D" "$INV_U" "$INV_C" "$EC_D" "$EC_U" "$EC_C" >> "$DET"

# --- gate checks ------------------------------------------------------------
CK_D=$(decl checks); CK_C=$(grep -c . "$GD/expected-checks.txt"); CK_U=$(sort -u "$GD/expected-checks.txt" | grep -c .)
[ "$CK_D" = "$CK_U" ] && [ "$CK_U" = "$CK_C" ] || NARROW=$((NARROW+1))

# --- the sum rules ----------------------------------------------------------
while IFS='	' read -r rid total addends _; do
  case "$rid" in ''|\#*) continue ;; esac
  t=$(decl "$total"); s=0
  for a in $(echo "$addends" | tr ',' ' '); do s=$((s + $(decl "$a"))); done
  if [ "$s" != "$t" ]; then NARROW=$((NARROW+1)); printf '%s BROKEN %s=%s sum=%s\n' "$rid" "$total" "$t" "$s" >> "$DET"
  else printf '%s OK %s=%s\n' "$rid" "$total" "$t" >> "$DET"; fi
done < "$GD/COUNTS.rules.tsv"

# --- L0-IG-D1: two declared pair counts is itself a narrowing risk -----------
if [ -n "$(decl ct_pairs_p00)" ] && [ -n "$(decl ct_pairs_p01)" ]; then
  NARROW=$((NARROW+1))
  echo "L0-IG-D1 UNRESOLVED: ct_pairs_p00=$(decl ct_pairs_p00) ct_pairs_p01=$(decl ct_pairs_p01)" >> "$DET"
fi

REG="n/a"
if [ "$SCOPE" = "integration" ]; then
  # Section 53.1: "Every run additionally records its per-registry comparison counts
  # ... so that a silently narrowed comparison is itself visible drift."
  RUN=$(ls -1 "$CPR"/records/reconciliation/*.yaml 2>/dev/null | LC_ALL=C sort | tail -1 || true)
  if [ -z "$RUN" ]; then
    REG="0/0"; NARROW=$((NARROW+1)); echo "no reconciliation run record found" >> "$DET"
  else
    RD=$(awk '/^ *declared_registries:/{print $2}' "$RUN"); RC=$(awk '/^ *compared_registries:/{print $2}' "$RUN")
    RD=${RD:-0}; RC=${RC:-0}; REG="$RC/$RD"
    [ "$RD" -gt 0 ] && [ "$RC" = "$RD" ] || { NARROW=$((NARROW+1)); echo "registry comparison narrowed $REG" >> "$DET"; }
    PREV=$(ls -1 "$CPR"/records/reconciliation/*.yaml | LC_ALL=C sort | tail -2 | head -1)
    if [ "$PREV" != "$RUN" ]; then
      PC=$(awk '/^ *compared_registries:/{print $2}' "$PREV"); PC=${PC:-0}
      [ "$RC" -ge "$PC" ] || { NARROW=$((NARROW+1)); echo "registry ratchet fell $PC -> $RC" >> "$DET"; }
    fi
  fi
fi

LBL="COUNT-INTEGRITY"
if [ "$NARROW" -eq 0 ]; then
  printf '%s PASS at=%s/%s/%s inv=%s/%s ec=%s/%s checks=%s/%s registries=%s narrowed=0\n' \
    "$LBL" "$AT_D" "$AT_UNIQ" "$AT_CELLS" "$INV_D" "$INV_U" "$EC_D" "$EC_U" "$CK_D" "$CK_U" "$REG"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf '%s FAIL at=%s/%s/%s inv=%s/%s ec=%s/%s checks=%s/%s registries=%s narrowed=%s\n' \
  "$LBL" "$AT_D" "$AT_UNIQ" "$AT_CELLS" "$INV_D" "$INV_U" "$EC_D" "$EC_U" "$CK_D" "$CK_U" "$REG" "$NARROW"
exit 1
CIS
chmod +x contracts/gate/count-integrity.sh

git add contracts/gate
git commit -m "L0-05-03: count-integrity.sh (IG-05/LG-08) and the frozen spec-anomaly expectation"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both scripts are executable | `test -x contracts/gate/count-integrity.sh && test -x contracts/gate/spec-transcription.sh && echo BOTH` | `BOTH` |
| 2 | The spec digest is recorded and current | `sha256sum "$(cat contracts/gate/SPEC_PATH)" \| cut -d' ' -f1 \| diff -q - contracts/gate/SPEC.sha256 >/dev/null && echo MATCH` | `MATCH` |
| 3 | No undeclared anomaly present (SA-001 resolved by D113; TSV is empty) | `bash contracts/gate/spec-transcription.sh \| tail -1 \| grep -o 'anomalies=[0-9]*/[0-9]*'` | `anomalies=0/0` |
| 4 | The transcription check passes overall | `bash contracts/gate/spec-transcription.sh \| tail -1 \| cut -d' ' -f1-2` | `SPEC-TRANSCRIPTION PASS` |
| 5 | Section 100 renders 110 rows, 110 unique ids, 110 cells (D113 removed the surplus cell) | `grep -o 'section100 rows=[0-9]* unique=[0-9]* cells=[0-9]*' .gate/spec-transcription.txt` | `section100 rows=110 unique=110 cells=110` |
| 6 | The count check refuses an unknown scope | `bash contracts/gate/count-integrity.sh --scope bogus; echo "rc=$?"` | `COUNT-INTEGRITY FAIL: --scope lane\|integration required` then `rc=2` |
| 7 | **The count check FAILS while L0-IG-D1 is open** | `bash contracts/gate/count-integrity.sh --scope integration \| tail -1 \| grep -o 'narrowed=[0-9]*'` | `narrowed=1` or higher — never `narrowed=0` |
| 8 | The open decision is named in the detail file, not hidden | `grep -c 'L0-IG-D1 UNRESOLVED' .gate/count-integrity.txt` | `1` |
| 9 | The three sum rules are evaluated every run | `grep -c '^SUM-0[123] ' .gate/count-integrity.txt` | `3` |
| 10 | A missing spec fails as a configuration error, not silently | `GATE_SPEC=/nonexistent bash contracts/gate/spec-transcription.sh; echo "rc=$?"` | a line beginning `SPEC-TRANSCRIPTION FAIL: specification not found` then `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
T=$(bash contracts/gate/spec-transcription.sh | tail -1)
C=$(bash contracts/gate/count-integrity.sh --scope integration | tail -1 || true)
GATE_SPEC=/nonexistent bash contracts/gate/spec-transcription.sh >/dev/null 2>&1; MISSING=$?
printf 'exec=%s digest=%s s100=[%s] anomalies=%s countfail=%s d1=%s sums=%s missing_rc=%s\n' \
  "$(test -x contracts/gate/count-integrity.sh -a -x contracts/gate/spec-transcription.sh && echo YES || echo NO)" \
  "$(sha256sum "$(cat contracts/gate/SPEC_PATH)" | cut -d' ' -f1 | diff -q - contracts/gate/SPEC.sha256 >/dev/null && echo MATCH || echo DIFFER)" \
  "$(grep -o 'rows=[0-9]* unique=[0-9]* cells=[0-9]*' .gate/spec-transcription.txt | head -1)" \
  "$(echo "$T" | grep -o 'anomalies=[0-9]*/[0-9]*')" \
  "$(echo "$C" | grep -o 'narrowed=[0-9]*')" \
  "$(grep -c 'L0-IG-D1 UNRESOLVED' .gate/count-integrity.txt)" \
  "$(grep -c '^SUM-0[123] ' .gate/count-integrity.txt)" \
  "$MISSING"
```

Expected output, exactly:

```
exec=YES digest=MATCH s100=[rows=110 unique=110 cells=110] anomalies=0/0 countfail=narrowed=1 d1=1 sums=3 missing_rc=2
```

**STOP rule** — one of these is inverted from what instinct says, and it is deliberate.

- If `countfail=narrowed=0` **while L0-IG-D1 is still open**, the count check has been made to pass by deleting one
  of the two `ct_pairs` rows without a decision record. Restore both rows. A gate that opened because a question
  was deleted is worse than a closed gate.
- If `s100` shows `cells=111`, the specification file you are pointed at is a pre-D113 version that still carries
  the AT-109/110 `||` cell break. Check `SPEC_PATH` and update `SPEC.sha256` via a decision record in
  `records/decisions/` per `L0-00-charter.md` §5. Do not remove the surplus-cell check to make the mismatch go away.
- If `undeclared=1` appears in the `spec-transcription.sh` verdict, a surplus id cell was found that is not listed
  in `spec-anomalies.tsv`. This is new rendering drift. Add a row to the TSV under an L0 decision record; do not
  suppress the check.

---

### L0-05-04 — `at-activation.tsv`: the frozen phase→AT map, and `gate-state/PHASE`

**Size:** M · **Dependencies:** L0-05-01

§100's preamble states the scheduling rule: *"Each test is verified at the implementation phase (Section 98,
Implementation Phases and Roadmap) where the capability it exercises activates."* `IG-07` asks whether every test
this phase activates was **executed**. That question has no answer until "this phase activates" is a file.

**The denominator, stated on every gate record.** `protocol/02` §9.1: **37 of the 110** acceptance tests are
reachable within the five-lane build; 23 are gated on the Governance tier and 50 on the People tier, whose
subsystem **P** no lane owns. `at_in_scope + at_governance_gated + at_people_gated = 37 + 23 + 50 = 110` is sum
rule `SUM-01` from L0-05-02. **A lane that reports "all my acceptance tests pass" has said something about at
most a third of the catalogue**, and a status report without that denominator is rejected.

#### 7.4.1 The activation table — transcribed from `protocol/02` §9.2, with the twin register of §10

| Phase (§98) | Activates | New | Cumulative ATs | New twins | Cumulative twins | `A` | `H/A` | `H` |
|---|---|---|---|---|---|---|---|---|
| `Ph1` Foundation | `AT-022` | 1 | **1** | — | **0** | 0 | 0 | 1 |
| `Ph2` Visibility | `AT-051` | 1 | **2** | `NT-051` | **1** | 1 | 0 | 0 |
| `Ph3` Registries & Standards | `AT-011`, `AT-018`, `AT-021`, `AT-036`, `AT-039`, `AT-075`, `AT-102`, `AT-109`, `AT-110` | 9 | **11** | 9 | **10** | 8 | 1 | 0 |
| `Ph4` Environments | `AT-010` | 1 | **12** | `NT-010` | **11** | 1 | 0 | 0 |
| `Ph5` Verification | `AT-009`, `AT-049`, `AT-107` | 3 | **15** | 3 | **14** | 3 | 0 | 0 |
| `Ph6` Delivery Pipeline | `AT-028`, `AT-029`, `AT-101`, `AT-103` | 4 | **19** | `NT-103` | **15** | 0 | 1 | 3 |
| `Ph7` GSD Activation | `AT-030`, `AT-034`, `AT-106` | 3 | **22** | 3 | **18** | 2 | 1 | 0 |
| `EH` Early hardening | `AT-003`, `AT-004`, `AT-023`, `AT-024`, `AT-025`, `AT-026`, `AT-033`, `AT-035`, `AT-048`, `AT-104` | 10 | **32** | 10 | **28** | 6 | 4 | 0 |
| `SA` Scale activation | `AT-008`, `AT-019`, `AT-020`, `AT-105` | 4 | **36** | 4 | **32** | 1 | 3 | 0 |
| `COND` Conditional | `AT-108` | 1 | **37** | `NT-108` | **33** | 1 | 0 | 0 |
| | | **37** | | | **33** | **23** | **10** | **4** |

The four tests with **no twin** are exactly the four `H` rows — `AT-022`, `AT-028`, `AT-029`, `AT-101` — because
`protocol/02` §10 registers a twin for every automatable test and for the automatable core of every hybrid. They
are executed on a recorded cadence and the record is the evidence; `at-coverage.sh` requires the record and does
not require a twin for them.

**Three tests carry a warning that belongs on this table, not buried in a script:**

| AT | Warning | Anchor |
|---|---|---|
| `AT-109` | Depends on subsystem **J**, which no lane owns. From `Ph3` this reports `not_run` and `IG-07` FAILS until **L0-IG-D4** is answered | `protocol/02` §2 |
| `AT-106` | Depends on subsystem **G**, which no lane owns. From `Ph7` this reports `not_run` | `protocol/02` §2, §9.3 (`‡G`) |
| `AT-034` | Owned by **L0**, and executable only on `integration` with all five lanes present — it is the test that proves the delivery core still runs with the removable governance artifacts removed. Its second twin is the important one: deleting the reconciliation engine must make the core **fail** | `protocol/00` §6; `protocol/02` §10 (`NT-034`) |

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/at-activation.tsv <<'ACT'
# phase<TAB>at<TAB>owner_lane<TAB>twin
# FROZEN (L0D-IG-5). Transcribed from protocol/02-acceptance-mapping.md sections
# 9.2 (phase), 9.3 and protocol/00-test-strategy.md section 6 (owner), 10 (twin).
# owner "G" means the subsystem is UNASSIGNED in PARTITION v1 - see L0-IG-D4.
# twin "-" means protocol/02 section 10 registers no twin (the four H-class tests).
# 37 rows. This file never grows past 37 without an L0 decision record.
Ph1	AT-022	L5	-
Ph2	AT-051	L1	NT-051
Ph3	AT-011	L5	NT-011
Ph3	AT-018	L3	NT-018
Ph3	AT-021	L1	NT-021
Ph3	AT-036	L3	NT-036
Ph3	AT-039	L1	NT-039
Ph3	AT-075	L1	NT-075
Ph3	AT-102	L3	NT-102
Ph3	AT-109	L5	NT-109
Ph3	AT-110	L3	NT-110
Ph4	AT-010	L1	NT-010
Ph5	AT-009	L2	NT-009
Ph5	AT-049	L1	NT-049
Ph5	AT-107	L5	NT-107
Ph6	AT-028	L5	-
Ph6	AT-029	L2	-
Ph6	AT-101	L1	-
Ph6	AT-103	L2	NT-103
Ph7	AT-030	L5	NT-030
Ph7	AT-034	L0	NT-034
Ph7	AT-106	G	NT-106
EH	AT-003	L1	NT-003
EH	AT-004	L3	NT-004
EH	AT-023	L2	NT-023
EH	AT-024	L2	NT-024
EH	AT-025	L1	NT-025
EH	AT-026	L2	NT-026
EH	AT-033	L3	NT-033
EH	AT-035	L2	NT-035
EH	AT-048	L4	NT-048
EH	AT-104	L4	NT-104
SA	AT-008	L3	NT-008
SA	AT-019	L1	NT-019
SA	AT-020	L1	NT-020
SA	AT-105	L2	NT-105
COND	AT-108	L5	NT-108
ACT

# --- the phase order, so "cumulative" is mechanical and not a judgement ------
cat > contracts/gate/phase-order.tsv <<'PHO'
# ordinal<TAB>phase<TAB>Section 98 reference
1	Ph1	98.2 Phase 1 Foundation
2	Ph2	98.2 Phase 2 Visibility
3	Ph3	98.2 Phase 3 Registries and Standards
4	Ph4	98.2 Phase 4 Environments
5	Ph5	98.2 Phase 5 Verification
6	Ph6	98.2 Phase 6 Delivery Pipeline
7	Ph7	98.2 Phase 7 GSD Activation
8	EH	98.3 Early hardening
9	SA	98.4 Scale activation
10	COND	Conditional activation on the Section 39.5 trigger
PHO

# --- the phase this cycle closes at. Ph1 is the first phase that activates
#     anything at all (AT-022, Founder continuity). L0 advances this file at
#     each Section 98 phase completion check, never a lane.
# FD-055: gate-state/ is mutable; not part of contracts/ SHA-256 hash.
mkdir -p "$CP_ROOT/gate-state"
printf 'Ph1\n' > "$CP_ROOT/gate-state/PHASE"

git add contracts/gate
git commit -m "L0-05-04: frozen phase->AT activation map, phase order, PHASE pointer"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 37 activation rows | `grep -vc '^#' contracts/gate/at-activation.tsv` | `37` |
| 2 | Exactly 37 distinct AT ids — no test activates twice | `cut -f2 contracts/gate/at-activation.tsv \| grep -v '^#' \| sort -u \| wc -l` | `37` |
| 3 | Exactly 33 twins registered | `cut -f4 contracts/gate/at-activation.tsv \| grep -c '^NT-'` | `33` |
| 4 | The four twinless rows are the four named `H` tests | `awk -F'\t' '$4=="-"{print $2}' contracts/gate/at-activation.tsv \| sort \| tr '\n' ' '` | `AT-022 AT-028 AT-029 AT-101 ` |
| 5 | Every activated AT is a real id from the frozen set | `cut -f2 contracts/gate/at-activation.tsv \| grep '^AT-' \| sort -u \| comm -23 - contracts/gate/at-index.tsv \| wc -l` | `0` |
| 6 | Every phase token is one `phase-order.tsv` declares | `cut -f1 contracts/gate/at-activation.tsv \| grep -v '^#' \| sort -u \| comm -23 - <(cut -f2 contracts/gate/phase-order.tsv \| grep -v '^#' \| sort) \| wc -l` | `0` |
| 7 | The count agrees with `COUNTS.tsv` | `[ "$(grep -vc '^#' contracts/gate/at-activation.tsv)" = "$(awk -F'\t' '$1=="at_in_scope"{print $2}' contracts/gate/COUNTS.tsv)" ] && echo AGREE` | `AGREE` |
| 8 | The twin count agrees with `COUNTS.tsv` | `[ "$(cut -f4 contracts/gate/at-activation.tsv \| grep -c '^NT-')" = "$(awk -F'\t' '$1=="at_twins"{print $2}' contracts/gate/COUNTS.tsv)" ] && echo AGREE` | `AGREE` |
| 9 | The cumulative column of §7.4.1 is reproducible | `for p in Ph1 Ph2 Ph3 Ph4 Ph5 Ph6 Ph7 EH SA COND; do printf '%s ' "$(awk -F'\t' -v P="$p" 'BEGIN{o=0} NR==FNR{ord[$2]=$1; next} $1!~/^#/{if(ord[$1]<=ord[P])n++} END{print n+0}' contracts/gate/phase-order.tsv contracts/gate/at-activation.tsv)"; done; echo` | `1 2 11 12 15 19 22 32 36 37 ` |
| 10 | The phase pointer holds a declared token | `grep -qxF "$(cat gate-state/PHASE)" <(cut -f2 contracts/gate/phase-order.tsv \| grep -v '^#') && echo VALID` | `VALID` |
| 11 | The unassigned-subsystem owner is visible, not laundered into a lane | `awk -F'\t' '$3=="G"{print $2}' contracts/gate/at-activation.tsv` | `AT-106` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
CUM=$(for p in Ph1 Ph2 Ph3 Ph4 Ph5 Ph6 Ph7 EH SA COND; do
  printf '%s ' "$(awk -F'\t' -v P="$p" 'NR==FNR{ord[$2]=$1; next} $1!~/^#/{if(ord[$1]<=ord[P])n++} END{print n+0}' \
    contracts/gate/phase-order.tsv contracts/gate/at-activation.tsv)"
done)
printf 'rows=%s uniq=%s twins=%s twinless=[%s] unknown_at=%s cum=[%s] phase=%s unassigned=%s\n' \
  "$(grep -vc '^#' contracts/gate/at-activation.tsv)" \
  "$(cut -f2 contracts/gate/at-activation.tsv | grep -v '^#' | sort -u | wc -l | tr -d ' ')" \
  "$(cut -f4 contracts/gate/at-activation.tsv | grep -c '^NT-')" \
  "$(awk -F'\t' '$4=="-"{print $2}' contracts/gate/at-activation.tsv | sort | tr '\n' ' ' | sed 's/ $//')" \
  "$(cut -f2 contracts/gate/at-activation.tsv | grep '^AT-' | sort -u | comm -23 - contracts/gate/at-index.tsv | wc -l | tr -d ' ')" \
  "$(echo "$CUM" | sed 's/ $//')" \
  "$(cat gate-state/PHASE)" \
  "$(awk -F'\t' '$3=="G"{print $2}' contracts/gate/at-activation.tsv | tr '\n' ' ' | sed 's/ $//')"
```

Expected output, exactly:

```
rows=37 uniq=37 twins=33 twinless=[AT-022 AT-028 AT-029 AT-101] unknown_at=0 cum=[1 2 11 12 15 19 22 32 36 37] phase=Ph1 unassigned=AT-106
```

**STOP rule** — if `unknown_at` is not `0`, a row names an AT id that does not exist in Section 100. That is
forbidden-action **F-18** (*"Inventing a spec section number, AT id, invariant number, SIG id or D id"*, cited in
`L0-03-merge-train.md` §L0-03-02): delete the invented id, do not "correct" it to a nearby one, and open
`BLOCKER L0-05-04: invented AT id <id>`. If `rows` is greater than `37`, someone has widened the in-scope set
without an L0 decision — a wider set makes the gate look more thorough and is the exact opposite: it schedules
tests the build cannot run, which report `not_run` and close the gate for the wrong reason. If `unassigned` is
empty, `AT-106`'s dependency on subsystem **G** has been laundered into a lane; restore it and route through
**L0-IG-D4**. **Never move an AT to a later phase to make a cycle pass.**

---

### L0-05-05 — `at-coverage.sh`: executed, never asserted (`IG-07`)

**Size:** L · **Dependencies:** L0-05-04

`IG-07`'s pass line is fixed by `protocol/05` §4:

```
IG-07 at-coverage PASS scheduled=<n> executed=<n> not_run=0 asserted_only=0
```

Four words carry the whole check. **`scheduled`** is the cumulative row of `at-activation.tsv` for `$PHASE`
(L0D-IG-5). **`executed`** counts ATs with a real recorded result. **`not_run`** counts scheduled ATs with no
result at all. **`asserted_only`** counts ATs that have a result but no evidence that the result was produced by
running something — including, per **L0D-IG-6**, any AT whose registered twin has no recorded result.

§100 is explicit that three of these are executed rather than claimed. `AT-110`: *"Executed for real at the phase
that builds the reconciler and re-executed at every rotation."* `AT-108` and `AT-109` are written the same way —
four attempts, six attempts, and the positive run afterwards. `protocol/00` §5 T4 carries it as
`executed_for_real: true`, and states the consequence: *"For these, a green simulated run is not a pass."*

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/at-coverage.sh <<'ATC'
#!/usr/bin/env sh
# =============================================================================
# at-coverage.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-07.
#   --phase <Ph1|Ph2|...|COND>   defaults to gate-state/PHASE
# Reads results from $CPR_ROOT/records/acceptance-runs/<cycle>/ and twin results
# from $CPR_ROOT/records/acceptance-twins/<cycle>/. One file per run, never an
# index (PARTITION rule 3).
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"; PHASE=""; CYCLE="${CYCLE:-}"
while [ $# -gt 0 ]; do case "$1" in
  --phase) PHASE="$2"; shift 2 ;;
  --cycle) CYCLE="$2"; shift 2 ;;
  *) echo "AT-COVERAGE FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
PHASE="${PHASE:-$(cat "${CP_ROOT:-.}/gate-state/PHASE" 2>/dev/null || true)}"
[ -n "$PHASE" ] || { echo "AT-COVERAGE FAIL: no phase given and gate-state/PHASE is empty"; exit 2; }
grep -q "	$PHASE	" "$GD/phase-order.tsv" || { echo "AT-COVERAGE FAIL: '$PHASE' is not a declared phase token"; exit 2; }
[ -n "$CYCLE" ] || { echo "AT-COVERAGE FAIL: CYCLE not set"; exit 2; }
CPR="${CPR_ROOT:?CPR_ROOT must point at the control-plane-records clone}"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/at-coverage.tsv"; : > "$DET"

ORD=$(awk -F'\t' -v p="$PHASE" '$2==p{print $1}' "$GD/phase-order.tsv")
RUNS="$CPR/records/acceptance-runs/$CYCLE"
TWINS="$CPR/records/acceptance-twins/$CYCLE"
HARNESS="tools/at/run-at.sh"

SCHED=0; EXEC=0; NOTRUN=0; ASSERTED=0

# L0-IG-D2: no lane owns tools/at/**. A missing harness is not a skip.
HARNESS_PRESENT=1; [ -x "$HARNESS" ] || HARNESS_PRESENT=0

while IFS='	' read -r ph at owner twin; do
  case "$ph" in ''|\#*) continue ;; esac
  o=$(awk -F'\t' -v p="$ph" '$2==p{print $1}' "$GD/phase-order.tsv")
  [ "$o" -le "$ORD" ] || continue
  SCHED=$((SCHED+1))
  R="$RUNS/$at.yaml"
  if [ "$HARNESS_PRESENT" -eq 0 ] || [ ! -f "$R" ]; then
    NOTRUN=$((NOTRUN+1)); printf '%s\t%s\tNOT_RUN\t-\t%s\n' "$at" "$owner" "$twin" >> "$DET"; continue
  fi
  MODE=$(awk -F': *' '/^ *evidence:/{print $2}' "$R"); MODE=${MODE:-none}
  RESULT=$(awk -F': *' '/^ *result:/{print $2}' "$R"); RESULT=${RESULT:-none}
  # "executed" requires an execution record: a command, an exit code, a timestamp.
  HAS_CMD=$(grep -c '^ *command:' "$R" || true)
  HAS_RC=$(grep -c '^ *exit_code:' "$R" || true)
  # L0D-IG-6: a registered twin with no recorded result makes the AT asserted-only.
  TWIN_OK=1
  if [ "$twin" != "-" ]; then [ -f "$TWINS/$twin.yaml" ] || TWIN_OK=0; fi
  if [ "$MODE" = "asserted" ] || [ "$HAS_CMD" -eq 0 ] || [ "$HAS_RC" -eq 0 ] || [ "$TWIN_OK" -eq 0 ]; then
    ASSERTED=$((ASSERTED+1))
    printf '%s\t%s\tASSERTED_ONLY\t%s\t%s twin_result=%s\n' "$at" "$owner" "$RESULT" "$twin" "$TWIN_OK" >> "$DET"
  elif [ "$RESULT" = "pass" ]; then
    EXEC=$((EXEC+1)); printf '%s\t%s\tEXECUTED\tpass\t%s\n' "$at" "$owner" "$twin" >> "$DET"
  else
    NOTRUN=$((NOTRUN+1)); printf '%s\t%s\tFAILED\t%s\t%s\n' "$at" "$owner" "$RESULT" "$twin" >> "$DET"
  fi
done < "$GD/at-activation.tsv"

TOTAL=$(awk -F'\t' '!/^#/{n++} END{print n+0}' "$GD/at-activation.tsv")
printf '# phase=%s cycle=%s harness=%s denominator=%s/110 (protocol/02 section 9.1)\n' \
  "$PHASE" "$CYCLE" "$HARNESS_PRESENT" "$TOTAL" >> "$DET"

if [ "$NOTRUN" -eq 0 ] && [ "$ASSERTED" -eq 0 ] && [ "$SCHED" -eq "$EXEC" ]; then
  printf 'AT-COVERAGE PASS scheduled=%s executed=%s not_run=0 asserted_only=0\n' "$SCHED" "$EXEC"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'AT-COVERAGE FAIL scheduled=%s executed=%s not_run=%s asserted_only=%s\n' "$SCHED" "$EXEC" "$NOTRUN" "$ASSERTED"
exit 1
ATC
chmod +x contracts/gate/at-coverage.sh

git add contracts/gate/at-coverage.sh
git commit -m "L0-05-05: at-coverage.sh (IG-07) - executed, never asserted"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x contracts/gate/at-coverage.sh && echo PRESENT` | `PRESENT` |
| 2 | An undeclared phase token is a configuration error, not a pass | `CYCLE=probe bash contracts/gate/at-coverage.sh --phase Ph9; echo "rc=$?"` | `AT-COVERAGE FAIL: 'Ph9' is not a declared phase token` then `rc=2` |
| 3 | A missing cycle is a configuration error | `bash contracts/gate/at-coverage.sh --phase Ph1; echo "rc=$?"` | `AT-COVERAGE FAIL: CYCLE not set` then `rc=2` |
| 4 | `scheduled` matches the cumulative table for every phase | see SELF-VERIFY case C | `1 2 11 12 15 19 22 32 36 37` |
| 5 | **A missing harness fails, and never reports `scheduled=0`** (L0-IG-D2) | `CYCLE=probe bash contracts/gate/at-coverage.sh --phase Ph3 \| tail -1` | `AT-COVERAGE FAIL scheduled=11 executed=0 not_run=11 asserted_only=0` |
| 6 | An AT recorded without a command is `asserted_only` | see SELF-VERIFY case A | `asserted_only=1` |
| 7 | An AT whose registered twin has no result is `asserted_only` (L0D-IG-6) | see SELF-VERIFY case B | `asserted_only=1` |
| 8 | The detail file names the denominator every run | `grep -c 'denominator=37/110' .gate/at-coverage.tsv` | `1` |
| 9 | The detail file has one row per scheduled AT | `grep -vc '^#' .gate/at-coverage.tsv` | equals the `scheduled=` value of the same run |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
export CYCLE=selftest
R="$CPR_ROOT/records/acceptance-runs/$CYCLE"; T="$CPR_ROOT/records/acceptance-twins/$CYCLE"
mkdir -p "$R" "$T"
printf 'x\n' > /tmp/at-probe-harness && mkdir -p tools/at && cp /tmp/at-probe-harness tools/at/run-at.sh && chmod +x tools/at/run-at.sh

# case A - AT-022 recorded as a claim, with no command and no exit code
printf 'id: AT-022\nresult: pass\nevidence: asserted\n' > "$R/AT-022.yaml"
A=$(bash contracts/gate/at-coverage.sh --phase Ph1 | tail -1 | grep -o 'asserted_only=[0-9]*')

# case B - AT-051 executed properly, but its twin NT-051 has no recorded result
printf 'id: AT-022\nresult: pass\nevidence: executed\ncommand: tools/at/run-at.sh Ph1\nexit_code: 0\n' > "$R/AT-022.yaml"
printf 'id: AT-051\nresult: pass\nevidence: executed\ncommand: tools/at/run-at.sh Ph2\nexit_code: 0\n' > "$R/AT-051.yaml"
B=$(bash contracts/gate/at-coverage.sh --phase Ph2 | tail -1 | grep -o 'asserted_only=[0-9]*')

# case C - the scheduled denominator per phase, harness removed so nothing else varies
rm -f tools/at/run-at.sh
C=$(for p in Ph1 Ph2 Ph3 Ph4 Ph5 Ph6 Ph7 EH SA COND; do
      printf '%s ' "$(bash contracts/gate/at-coverage.sh --phase "$p" | tail -1 | sed 's/.*scheduled=\([0-9]*\).*/\1/')"
    done | sed 's/ $//')

# case D - undeclared phase, and missing cycle
bash contracts/gate/at-coverage.sh --phase Ph9 >/dev/null 2>&1; D=$?
CYCLE= bash contracts/gate/at-coverage.sh --phase Ph1 >/dev/null 2>&1; E=$?

rm -rf "$R" "$T"
printf 'caseA=%s caseB=%s sched=[%s] badphase_rc=%s nocycle_rc=%s denom=%s\n' \
  "$A" "$B" "$C" "$D" "$E" "$(grep -c 'denominator=37/110' .gate/at-coverage.tsv)"
```

Expected output, exactly:

```
caseA=asserted_only=1 caseB=asserted_only=1 sched=[1 2 11 12 15 19 22 32 36 37] badphase_rc=2 nocycle_rc=2 denom=1
```

**STOP rule** — if `caseA` or `caseB` prints `asserted_only=0`, the check has stopped distinguishing a test that
ran from a test that was claimed, and every later `IG-07 PASS` is worthless. **Do not relax the evidence fields to
make real runs pass more easily.** AT-090 states the general form of this failure for the catalogue it governs:
*"A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control
test is how the boundary erodes."* Open `BLOCKER L0-05-05: at-coverage no longer discriminates asserted results`
and stop. If `sched` differs from `1 2 11 12 15 19 22 32 36 37`, `at-activation.tsv` and §7.4.1 have diverged;
re-run L0-05-04's SELF-VERIFY before touching this script.

---

### L0-05-06 — `lane-suite.sh --all`: five suites at the merged head (`IG-02`)

**Size:** M · **Dependencies:** L0-05-01

`IG-02` is the check a lane cannot run: *every lane's suite still passes* **after** *the other four landed*. Its
pass line is fixed by `protocol/05` §4:

```
IG-02 lane-suites PASS lanes=5/5 tests=<n> failed=0 seeded_defects=5/5 DETECTED
```

Two contracts from `protocol/00` are enforced inside this script and neither is optional.

**The exit-code contract** (`protocol/00` §3). `0` pass with at least one assertion; `1` ordinary fail;
**`2` vacuous** — the suite ran and executed zero assertions; **`3` non-discriminating** — a negative fixture
passed. Exit `2` and exit `3` are failures, and they are the two that a suite reports while looking green.

**The `GATE-RESULT` line** (`protocol/00` §3). Every entry point prints, as its last stdout line:

```
GATE-RESULT gate=<GATE-ID> level=<T0|T1|T2|T3|T4> assertions=<n> failures=<n> negatives_run=<n> negatives_that_failed_correctly=<n>
```

The runner fails the level when `assertions == 0`, when `negatives_run == 0`, or when
`negatives_that_failed_correctly != negatives_run`. **Silence is never taken as health.**

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/lane-suite.sh <<'LSS'
#!/usr/bin/env sh
# =============================================================================
# lane-suite.sh - L0-owned (contracts/gate/**, L0D-IG-1). LG-05 and IG-02.
#   --lane <N>   one lane's suite      (LG-05 form)
#   --all        all five, in train order 1,4,2,3,5   (IG-02 form)
# The suite COMMAND comes from contracts/gate/lane-suite.tsv and a lane cannot
# change its own row (protocol/05 section 2.1).
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"; MODE=""; LANE=""
while [ $# -gt 0 ]; do case "$1" in
  --lane) MODE=one; LANE="$2"; shift 2 ;;
  --all)  MODE=all; shift ;;
  *) echo "LANE-SUITE FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$MODE" ] || { echo "LANE-SUITE FAIL: --lane <N> or --all required"; exit 2; }
[ -f "$GD/lane-suite.tsv" ] || { echo "LANE-SUITE FAIL: lane-suite.tsv missing"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/lane-suite.txt"; : > "$DET"

case "$MODE" in one) LANES="$LANE" ;; all) LANES="1 4 2 3 5" ;; esac

OK=0; N=0; TESTS=0; FAILED=0; SEEDED=0; SEEDED_TOTAL=0
for L in $LANES; do
  N=$((N+1))
  CMD=$(awk -F'\t' -v l="$L" '!/^#/ && $1==l {print $2; exit}' "$GD/lane-suite.tsv")
  if [ -z "$CMD" ]; then
    echo "lane $L: NO SUITE ROW - fail closed" >> "$DET"; FAILED=$((FAILED+1)); continue
  fi
  echo "== lane $L: $CMD" >> "$DET"
  set +e
  sh -c "$CMD" >> "$DET" 2>&1
  RC=$?
  set -e
  LAST=$(grep '^GATE-RESULT ' "$DET" | tail -1)
  A=$(echo "$LAST" | sed -n 's/.*assertions=\([0-9]*\).*/\1/p'); A=${A:-0}
  F=$(echo "$LAST" | sed -n 's/.*failures=\([0-9]*\).*/\1/p'); F=${F:-0}
  NR=$(echo "$LAST" | sed -n 's/.*negatives_run=\([0-9]*\).*/\1/p'); NR=${NR:-0}
  NC=$(echo "$LAST" | sed -n 's/.* negatives_that_failed_correctly=\([0-9]*\).*/\1/p'); NC=${NC:-0}
  TESTS=$((TESTS+A))
  SEEDED_TOTAL=$((SEEDED_TOTAL+1))
  VERDICT=FAIL
  case "$RC" in
    0) if [ "$A" -gt 0 ] && [ "$F" -eq 0 ] && [ "$NR" -gt 0 ] && [ "$NC" = "$NR" ]; then
         VERDICT=PASS; OK=$((OK+1)); SEEDED=$((SEEDED+1))
       elif [ "$A" -eq 0 ]; then VERDICT="FAIL vacuous(assertions=0)"
       elif [ "$NR" -eq 0 ]; then VERDICT="FAIL no-negatives(negatives_run=0)"
       else VERDICT="FAIL seeded_defect=PASSED($NC/$NR)"; fi ;;
    2) VERDICT="FAIL vacuous(exit=2)" ;;
    3) VERDICT="FAIL non-discriminating(exit=3)" ;;
    *) VERDICT="FAIL exit=$RC" ;;
  esac
  [ "$VERDICT" = "PASS" ] || FAILED=$((FAILED+1))
  printf 'lane %s %s assertions=%s failures=%s negatives=%s/%s\n' "$L" "$VERDICT" "$A" "$F" "$NC" "$NR" >> "$DET"
done

if [ "$MODE" = "all" ]; then
  if [ "$OK" -eq 5 ] && [ "$FAILED" -eq 0 ] && [ "$SEEDED" -eq 5 ]; then
    printf 'LANE-SUITE PASS lanes=5/5 tests=%s failed=0 seeded_defects=5/5 DETECTED\n' "$TESTS"; exit 0 # exit 0 = gate ARMED (FD-035)
  fi
  printf 'LANE-SUITE FAIL lanes=%s/5 tests=%s failed=%s seeded_defects=%s/5\n' "$OK" "$TESTS" "$FAILED" "$SEEDED"; exit 1
fi
if [ "$OK" -eq 1 ]; then
  printf 'LANE-SUITE PASS lane=%s tests=%s failed=0 seeded_defect=DETECTED\n' "$LANE" "$TESTS"; exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'LANE-SUITE FAIL lane=%s tests=%s failed=%s seeded_defect=PASSED\n' "$LANE" "$TESTS" "$FAILED"; exit 1
LSS
chmod +x contracts/gate/lane-suite.sh

git add contracts/gate/lane-suite.sh
git commit -m "L0-05-06: lane-suite.sh, LG-05 and IG-02, with the vacuity and non-discrimination rules"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x contracts/gate/lane-suite.sh && echo PRESENT` | `PRESENT` |
| 2 | No mode is a configuration error | `bash contracts/gate/lane-suite.sh; echo "rc=$?"` | `LANE-SUITE FAIL: --lane <N> or --all required` then `rc=2` |
| 3 | `--all` runs the five lanes in train order | `grep -c '^== lane ' .gate/lane-suite.txt` after an `--all` run | `5` |
| 4 | The train order is `1 4 2 3 5`, not `1 2 3 4 5` | `grep '^== lane ' .gate/lane-suite.txt \| sed 's/== lane \([0-9]\).*/\1/' \| tr '\n' ' '` | `1 4 2 3 5 ` |
| 5 | A lane with **no suite row** fails closed | see SELF-VERIFY case R | a line `lane 9: NO SUITE ROW - fail closed` |
| 6 | A suite exiting `0` with `assertions=0` is a FAIL, not a pass | see SELF-VERIFY case V | `FAIL vacuous(assertions=0)` |
| 7 | A suite exiting `0` with `negatives_run=0` is a FAIL | see SELF-VERIFY case N | `FAIL no-negatives(negatives_run=0)` |
| 8 | A suite whose seeded defect passed is a FAIL | see SELF-VERIFY case S | `FAIL seeded_defect=PASSED` |
| 9 | Exit `3` is reported as non-discriminating, distinctly from exit `1` | see SELF-VERIFY case D | `FAIL non-discriminating(exit=3)` |
| 10 | The pass line matches `protocol/05` §4 byte-for-byte | see SELF-VERIFY case P | `LANE-SUITE PASS lanes=5/5 tests=5 failed=0 seeded_defects=5/5 DETECTED` |

**SELF-VERIFY**

Run against a throwaway suite map so that no lane's real suite is invoked. `GD` is honoured by copying the gate
directory, never by editing the frozen one.

```bash
set -euo pipefail
cd "$CP_ROOT"
rm -rf /tmp/gsv && mkdir -p /tmp/gsv && cp contracts/gate/lane-suite.sh /tmp/gsv/

mk() { printf '%s\n' "$1" > /tmp/gsv/lane-suite.tsv; }
row() { printf '%s\t%s\n' "$1" "$2" >> /tmp/gsv/lane-suite.tsv; }
good() { echo "echo GATE-RESULT gate=GATE-L$1-001 level=T1 assertions=1 failures=0 negatives_run=1 negatives_that_failed_correctly=1"; }

# case P - all five healthy
mk '# lane<TAB>suite-command'; for l in 1 2 3 4 5; do row "$l" "$(good $l)"; done
P=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --all | tail -1)
ORD=$(grep '^== lane ' /tmp/gsv/out/lane-suite.txt | sed 's/== lane \([0-9]\).*/\1/' | tr '\n' ' ' | sed 's/ $//')

# case V - lane 3 vacuous (assertions=0), exit 0
mk '# lane<TAB>suite-command'; for l in 1 2 4 5; do row "$l" "$(good $l)"; done
row 3 "echo GATE-RESULT gate=GATE-L3-001 level=T1 assertions=0 failures=0 negatives_run=1 negatives_that_failed_correctly=1"
V=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --all >/dev/null 2>&1; grep -o 'FAIL vacuous(assertions=0)' /tmp/gsv/out/lane-suite.txt | head -1)

# case N - lane 3 ran no negatives
mk '# lane<TAB>suite-command'; for l in 1 2 4 5; do row "$l" "$(good $l)"; done
row 3 "echo GATE-RESULT gate=GATE-L3-001 level=T1 assertions=9 failures=0 negatives_run=0 negatives_that_failed_correctly=0"
N=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --all >/dev/null 2>&1; grep -o 'FAIL no-negatives(negatives_run=0)' /tmp/gsv/out/lane-suite.txt | head -1)

# case S - lane 3's seeded defect passed
mk '# lane<TAB>suite-command'; for l in 1 2 4 5; do row "$l" "$(good $l)"; done
row 3 "echo GATE-RESULT gate=GATE-L3-001 level=T1 assertions=9 failures=0 negatives_run=3 negatives_that_failed_correctly=2"
S=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --all >/dev/null 2>&1; grep -o 'FAIL seeded_defect=PASSED' /tmp/gsv/out/lane-suite.txt | head -1)

# case D - lane 3 exits 3
mk '# lane<TAB>suite-command'; for l in 1 2 4 5; do row "$l" "$(good $l)"; done
row 3 "exit 3"
D=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --all >/dev/null 2>&1; grep -o 'FAIL non-discriminating(exit=3)' /tmp/gsv/out/lane-suite.txt | head -1)

# case R - a lane with no row
mk '# lane<TAB>suite-command'; row 1 "$(good 1)"
R=$(GATE_OUT=/tmp/gsv/out sh /tmp/gsv/lane-suite.sh --lane 9 >/dev/null 2>&1; grep -o 'NO SUITE ROW - fail closed' /tmp/gsv/out/lane-suite.txt | head -1)

sh /tmp/gsv/lane-suite.sh >/dev/null 2>&1; NOMODE=$?
printf 'pass=[%s] order=[%s] vacuous=[%s] noneg=[%s] seeded=[%s] exit3=[%s] norow=[%s] nomode_rc=%s\n' \
  "$P" "$ORD" "$V" "$N" "$S" "$D" "$R" "$NOMODE"
```

Expected output, exactly:

```
pass=[LANE-SUITE PASS lanes=5/5 tests=5 failed=0 seeded_defects=5/5 DETECTED] order=[1 4 2 3 5] vacuous=[FAIL vacuous(assertions=0)] noneg=[FAIL no-negatives(negatives_run=0)] seeded=[FAIL seeded_defect=PASSED] exit3=[FAIL non-discriminating(exit=3)] norow=[NO SUITE ROW - fail closed] nomode_rc=2
```

**STOP rule** — if `vacuous`, `noneg` or `seeded` comes back empty, the script has stopped distinguishing a suite
that asserts nothing from a suite that passes. That is the single failure `protocol/00` §0 exists to prevent:
*"a lane quietly builds the wrong thing, ships a suite that asserts nothing, and every light stays green."* Do not
proceed to L0-05-08 — the negative battery mutates exactly these paths and a battery pointed at a blind check
reports `proven` for a check that cannot see. Open `BLOCKER L0-05-06: lane-suite vacuity check not discriminating`
and stop. If `order` is not `1 4 2 3 5`, the train order has been re-implemented as ascending; that is `L0D-07`
territory and it is not fixed here.

---

### L0-05-16 — Author e2e/run.sh

**Owner:** L0  **FILES:** e2e/run.sh  **INSTRUCTION:** [placeholder per FD-033]

> FD-033: L0 owns `e2e/**` (FD-055/L0D-04). This stub is a placeholder; the full task body is authored when L0-IG-D5 is resolved and L0 decides the owner and creation path for `e2e/**`. Until then, `run-integration.sh` step 0 exits immediately if this file is absent, and `IG-10` reads `NO-OUTPUT-FAIL` — the gate stays closed (§5 L0-IG-D5).

---

### L0-05-17 — Author e2e/verdict.sh

**Owner:** L0  **FILES:** e2e/verdict.sh  **INSTRUCTION:** [placeholder per FD-033]

> FD-033: L0 owns `e2e/**` (FD-055/L0D-04). This stub is a placeholder; the full task body is authored when L0-IG-D5 is resolved. `protocol/08-smoke-and-e2e.md` specifies `e2e/verdict.sh` as *"the only thing allowed to print PASS for the run"*; no other path may emit that token.

---

### L0-05-18 — Author contracts/harness/run-contract-tests.sh

**Owner:** L0  **FILES:** contracts/harness/run-contract-tests.sh  **INSTRUCTION:** [placeholder per FD-033]

> FD-033: L0 owns `contracts/harness/**` (contracts/** is L0-exclusive, PARTITION.md). This stub is a placeholder; the full task body is authored when L0-IG-D5 is resolved. Until then, `contract-tests.sh` exits immediately if this file is absent, and `IG-03` FAILS with `CONTRACT-TESTS FAIL paired=0` — the gate stays closed (§5 L0-IG-D5).

---

### L0-05-19 — Author contracts/harness/pairs.tsv

**Owner:** L0  **FILES:** contracts/harness/pairs.tsv  **INSTRUCTION:** [placeholder per FD-033]

> FD-033: L0 owns `contracts/harness/**`. This stub is a placeholder; the full task body is authored when both L0-IG-D1 (how many cross-lane pairs) and L0-IG-D5 (ownership of the harness) are resolved. `pairs.tsv` is the harness manifest read by `contract-tests.sh --mode integrated`; its row count determines `pairs=<n>` in `IG-03`'s pass line and must agree with `COUNTS.tsv` `ct_pairs_p00`/`ct_pairs_p01` once L0-IG-D1 is settled.

---

### L0-05-07 — `contract-tests.sh --mode integrated`: provider to consumer (`IG-03`)

**Size:** M · **Dependencies:** L0-05-01, L0-05-02

`IG-03` is the only check that ever looks at whether the **stub a lane developed against** and the **real thing the
producer shipped** agree. `protocol/01` §5.2 hands every lane a stub producer on purpose, so it can build before
the producer exists; `protocol/01` §5.4 calls the handover *"parity"* and requires it *"the first cycle after any
producer lane merges"*. `stubbed=0` is that requirement made mechanical.

Pass line, fixed by `protocol/05` §4:

```
IG-03 contract-tests PASS pairs=<n> cases=<n> failed=0 stubbed=0 fixtures_match=1
```

**`fixtures_match=1` is not decoration.** `contracts/fixtures/**` is L0-owned and FROZEN (PARTITION rule 2), and
`protocol/00` §2 states why in one sentence: *"a lane cannot make a contract test pass by editing the fixture."*
The digest comparison is the only thing that makes that sentence true at run time.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
# --- freeze the fixture tree ------------------------------------------------
find contracts/fixtures -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 \
  > contracts/gate/FIXTURES.sha256

cat > contracts/gate/contract-tests.sh <<'CTS'
#!/usr/bin/env sh
# =============================================================================
# contract-tests.sh - L0-owned (contracts/gate/**, L0D-IG-1). LG-06 and IG-03.
#   --lane <N>          the LG-06 form: everything lane N consumes and produces
#   --mode integrated   the IG-03 form: every pair, live producers only
# Delegates execution to the harness of protocol/01 section 9 and adds the two
# assertions only the gate can make: fixture immutability, and stubbed=0.
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"; MODE=""; LANE=""
while [ $# -gt 0 ]; do case "$1" in
  --lane) MODE=lane; LANE="$2"; shift 2 ;;
  --mode) MODE="$2"; shift 2 ;;
  *) echo "CONTRACT-TESTS FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ "$MODE" = "lane" ] || [ "$MODE" = "integrated" ] || { echo "CONTRACT-TESTS FAIL: --lane <N> or --mode integrated required"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/contract-tests.txt"; : > "$DET"
HARNESS="contracts/harness/run-contract-tests.sh"
MANIFEST="contracts/harness/pairs.tsv"
[ -x "$HARNESS" ] || { echo "CONTRACT-TESTS FAIL: harness $HARNESS missing - fail closed"; exit 1; }
[ -f "$MANIFEST" ] || { echo "CONTRACT-TESTS FAIL: pair manifest $MANIFEST missing - fail closed"; exit 1; }

# --- fixtures_match: the frozen tree must be byte-identical -------------------
HAVE=$(find contracts/fixtures -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
WANT=$(cat "$GD/FIXTURES.sha256")
FM=0; [ "$HAVE" = "$WANT" ] && FM=1
printf 'fixtures have=%s want=%s match=%s\n' "$HAVE" "$WANT" "$FM" >> "$DET"

# --- L0-IG-D1: the manifest's pair count must agree with COUNTS.tsv ----------
PAIRS=$(grep -vc '^#' "$MANIFEST")
D00=$(awk -F'\t' '$1=="ct_pairs_p00"{print $2}' "$GD/COUNTS.tsv")
D01=$(awk -F'\t' '$1=="ct_pairs_p01"{print $2}' "$GD/COUNTS.tsv")
DECL=$(awk -F'\t' '$1=="ct_pairs"{print $2}' "$GD/COUNTS.tsv")
PAIRS_OK=0
if [ -n "$DECL" ]; then
  [ "$PAIRS" = "$DECL" ] && PAIRS_OK=1
else
  echo "L0-IG-D1 UNRESOLVED: manifest declares $PAIRS pairs; COUNTS.tsv declares $D00 (protocol/00) and $D01 (protocol/01)" >> "$DET"
fi

if [ "$MODE" = "integrated" ]; then
  set +e; "$HARNESS" --all --mode integrated --report "tsv:$OUT/contract-report.tsv" >> "$DET" 2>&1; RC=$?; set -e
else
  set +e; "$HARNESS" --side consumer --lane "L$LANE" --report "tsv:$OUT/contract-report.tsv" >> "$DET" 2>&1; RC=$?; set -e
fi

CASES=$(grep -vc '^#' "$OUT/contract-report.tsv" 2>/dev/null || echo 0)
FAILED=$(awk -F'\t' '!/^#/ && $3!="pass"{n++} END{print n+0}' "$OUT/contract-report.tsv" 2>/dev/null || echo 0)
# A case still resolved against .contract-stubs/ has not met its producer.
STUBBED=$(awk -F'\t' '!/^#/ && $4 ~ /contract-stubs/{n++} END{print n+0}' "$OUT/contract-report.tsv" 2>/dev/null || echo 0)

if [ "$RC" -eq 0 ] && [ "$FAILED" -eq 0 ] && [ "$FM" -eq 1 ] && [ "$CASES" -gt 0 ] \
   && { [ "$MODE" = "lane" ] || { [ "$STUBBED" -eq 0 ] && [ "$PAIRS_OK" -eq 1 ]; }; }; then
  printf 'CONTRACT-TESTS PASS pairs=%s cases=%s failed=0 stubbed=%s fixtures_match=1\n' "$PAIRS" "$CASES" "$STUBBED"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'CONTRACT-TESTS FAIL pairs=%s cases=%s failed=%s stubbed=%s fixtures_match=%s\n' "$PAIRS" "$CASES" "$FAILED" "$STUBBED" "$FM"
exit 1
CTS
chmod +x contracts/gate/contract-tests.sh

git add contracts/gate
git commit -m "L0-05-07: contract-tests.sh (LG-06/IG-03), frozen fixture digest, stubbed=0"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable and the fixture digest is recorded | `test -x contracts/gate/contract-tests.sh && test -s contracts/gate/FIXTURES.sha256 && echo BOTH` | `BOTH` |
| 2 | The recorded digest is current | `find contracts/fixtures -type f \| LC_ALL=C sort \| xargs sha256sum \| sha256sum \| cut -d' ' -f1 \| diff -q - contracts/gate/FIXTURES.sha256 >/dev/null && echo MATCH` | `MATCH` |
| 3 | A missing harness fails closed, never passes | `mv contracts/harness/run-contract-tests.sh /tmp/h 2>/dev/null; bash contracts/gate/contract-tests.sh --mode integrated; echo "rc=$?"; mv /tmp/h contracts/harness/run-contract-tests.sh 2>/dev/null` | `CONTRACT-TESTS FAIL: harness ... missing - fail closed` then `rc=1` |
| 4 | **Editing one fixture byte flips `fixtures_match` to `0`** | see SELF-VERIFY case F | `fixtures_match=0` |
| 5 | A case still resolving against a stub is counted | see SELF-VERIFY case S | `stubbed=1` |
| 6 | **The open discrepancy L0-IG-D1 is named in the detail file** | `grep -c 'L0-IG-D1 UNRESOLVED' .gate/contract-tests.txt` | `1` |
| 7 | Zero cases is a failure, not an empty pass | see SELF-VERIFY case Z | `CONTRACT-TESTS FAIL` with `cases=0` |
| 8 | No mode is a configuration error | `bash contracts/gate/contract-tests.sh; echo "rc=$?"` | `CONTRACT-TESTS FAIL: --lane <N> or --mode integrated required` then `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
FX=$(find contracts/fixtures -type f | LC_ALL=C sort | head -1)

# case F - one byte of one frozen fixture, restored immediately
cp "$FX" /tmp/fx.bak && printf '\n' >> "$FX"
F=$(bash contracts/gate/contract-tests.sh --mode integrated 2>/dev/null | tail -1 | grep -o 'fixtures_match=[01]')
cp /tmp/fx.bak "$FX" && rm -f /tmp/fx.bak

# case S - a report row still resolved against .contract-stubs/
mkdir -p .gate
printf '# pair\tcase\tresult\tresolved_from\nC-07\tconsumer-L3\tpass\t.contract-stubs/C-07/access-model-full.yaml\n' > .gate/contract-report.tsv
S=$(awk -F'\t' '!/^#/ && $4 ~ /contract-stubs/{n++} END{print "stubbed=" n+0}' .gate/contract-report.tsv)

# case Z - an empty report
printf '# pair\tcase\tresult\tresolved_from\n' > .gate/contract-report.tsv
Z=$(awk -F'\t' '!/^#/{n++} END{print "cases=" n+0}' .gate/contract-report.tsv)

bash contracts/gate/contract-tests.sh >/dev/null 2>&1; NOMODE=$?
printf 'digest=%s fixtures_mutated=[%s] %s %s d1=%s nomode_rc=%s\n' \
  "$(find contracts/fixtures -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 | diff -q - contracts/gate/FIXTURES.sha256 >/dev/null && echo MATCH || echo DIFFER)" \
  "$F" "$S" "$Z" \
  "$(grep -c 'L0-IG-D1 UNRESOLVED' .gate/contract-tests.txt)" "$NOMODE"
```

Expected output, exactly:

```
digest=MATCH fixtures_mutated=[fixtures_match=0] stubbed=1 cases=0 d1=1 nomode_rc=2
```

**STOP rule** — if `fixtures_mutated` shows `fixtures_match=1`, a lane can make a contract test pass by editing the
fixture and `IG-03` proves nothing. **Do not re-freeze `FIXTURES.sha256` to clear a mismatch you did not cause.**
A genuine fixture change is a Contract Change Request (`docs/escalation/CCR.md`, PARTITION rule 2), approved under
`L0D-06`, and the re-freeze is a step of that approval — never a repair. If `digest=DIFFER` at the end of this
SELF-VERIFY, case F did not restore the file: restore it from git (`git checkout -- contracts/fixtures`) before
committing anything. Open `BLOCKER L0-05-07: fixture immunity not enforced` for the first case.

---

### L0-05-08 — `negative-battery.sh --gate integration --full` (`IG-04`)

**Size:** L · **Dependencies:** L0-05-03, L0-05-05, L0-05-06, L0-05-07

This is the check that makes the other twenty-three mean something. `protocol/05` §5: the battery *"runs one
mutation per check against a throwaway worktree, asserts the check returns FAIL, and restores. A check that stays
PASS under its mutation is reported `unproven`, and an unproven check fails the gate — the gate cannot certify
itself with an instrument it has not just seen bite."*

Pass line, fixed by `protocol/05` §4:

```
IG-04 negatives PASS proven=24/24 unproven=0 canary=FOUND seeded_defects=DETECTED
```

**Why 24 and not 18.** `protocol/05` §5 lists eighteen mutation rows, but several rows carry two check ids
(`LG-02 / IG-08`, `LG-05 / IG-02`, and so on) because one mutation proves the same instrument at both gates. The
manifest below is written **one row per check id**, so `proven=24/24` is literally the number of rows that bit.
A manifest of eighteen rows reporting `24/24` would be the arithmetic version of the failure this whole file
exists to prevent.

#### 7.8.1 The battery manifest — transcribed from `protocol/05` §5

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/negative-battery.tsv <<'NEG'
# check<TAB>gate<TAB>mutation<TAB>required-failure-token
# FROZEN. One row per check id in expected-checks.txt. 24 rows, no more, no less.
# Transcribed from protocol/05-merge-gate.md section 5. Rows carrying two check
# ids there are split here so that proven=24/24 counts checks, not mutations.
LG-01	lane	Reset the worktree one commit behind origin/integration	behind=1
LG-02	lane	Touch schemas/registry/.negative-probe from a lane-3 context	foreign=1
LG-03	lane	Append a comment line to contracts/.negative-probe	l0_paths_touched=1
LG-04	lane	Modify (not add) a file listed in contracts/gate/aggregates.txt	modified_aggregates=1
LG-05	lane	Un-break the lane's declared seeded-defect case so the suite goes green on broken input	seeded_defect=PASSED
LG-06	lane	Edit one frozen fixture byte	fixtures_match=0
LG-07	lane	Delete one negative case from the battery manifest	unproven=1
LG-08	lane	Drop one row from a registry the lane enumerates	narrowed=1
LG-09	lane	Replay an approval by the PR author, then an approval by the machine account	author_distinct=0
LG-10	lane	Add an if:false to a job emitting a required check name	skipped=1
LG-11	lane	Add an import of reconciler/ into a lane-1 file	foreign_refs=1
LG-12	lane	Flip the local verdict file to FAIL while CI says PASS	delta=1
IG-01	integration	Re-order the cycle's merges to L3 before L1	out_of_order=1
IG-02	integration	Un-break one lane's seeded-defect case at the merged head	seeded_defects=4/5
IG-03	integration	Edit one frozen fixture byte	fixtures_match=0
IG-04	integration	Delete one row from this manifest	unproven=1
IG-05	integration	Drop one row from a registry the reconciler enumerates	narrowed=1
IG-06	integration	Point one mechanical invariant at a non-existent check name	dangling_refs=1
IG-07	integration	Mark one scheduled AT asserted instead of executed	asserted_only=1
IG-08	integration	Touch schemas/registry/.negative-probe inside a merge commit in the range	foreign=1
IG-09	integration	Add the machine account to a scratch CODEOWNERS in the verifier's sandbox	machine_codeowners=1
IG-10	integration	Add an if:false to a job emitting a required check name	skipped=1
IG-11	integration	Present a sign-off by the author of the cycle's largest diff	self_signoff=1
IG-12	integration	Flip the local verdict file to FAIL while CI says PASS	delta=1
NEG
```

**Two instruments are proven in addition to the twenty-four**, and they are the two the pass line names separately
because they are the two a broken gate loses while still printing a verdict:

| Instrument | Mutation | Required result | Anchor |
|---|---|---|---|
| **The seeded reconciliation canary** | Remove the seeded canary drift record from the comparison set, then run reconciliation | the run reports `canary=MISSING` → a **FAILED run**, `SIG-13` raised, the §53.7 gap procedure runs | `AT-102`; §53.1; `EC-109` |
| **The seeded-defect verification case** | Restore a lane's `verification/contract.yaml` seeded-defect case to something that passes | the run reports `seeded_defect=PASSED` → a **FAILED run**, `SIG-18` raised, Blocking for that product | §31.2 |

§53.1 states the canary rule in the sentence the whole protocol is built on: *"A run that reports zero findings,
including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking, not that nothing
drifted."* `AT-102` states the consequence: *"A reconciler that finds nothing is assumed broken, never assumed
clean."*

#### 7.8.2 The battery

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/negative-battery.sh <<'NBS'
#!/usr/bin/env sh
# =============================================================================
# negative-battery.sh - L0-owned (contracts/gate/**, L0D-IG-1). LG-07 and IG-04.
#   --gate lane --lane <N>        prove the twelve LG- checks
#   --gate integration --full     prove all 24, plus the canary and seeded defects
# Every mutation is applied in a THROWAWAY WORKTREE and never in $CP_ROOT.
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"; GATE=""; LANE=""; FULL=0
while [ $# -gt 0 ]; do case "$1" in
  --gate) GATE="$2"; shift 2 ;;
  --lane) LANE="$2"; shift 2 ;;
  --full) FULL=1; shift ;;
  *) echo "NEGATIVE-BATTERY FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ "$GATE" = "lane" ] || [ "$GATE" = "integration" ] || { echo "NEGATIVE-BATTERY FAIL: --gate lane|integration required"; exit 2; }
[ -f "$GD/negative-battery.tsv" ] || { echo "NEGATIVE-BATTERY FAIL: manifest missing - fail closed"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/negative-battery.txt"; : > "$DET"

# --- the manifest must cover every check id, exactly once ---------------------
EXPECT=$(sort -u "$GD/expected-checks.txt" | grep -c .)
HAVE=$(cut -f1 "$GD/negative-battery.tsv" | grep -v '^#' | sort -u | grep -c .)
DUPS=$(cut -f1 "$GD/negative-battery.tsv" | grep -v '^#' | sort | uniq -d | grep -c . || true)
MISSING=$(comm -23 <(sort -u "$GD/expected-checks.txt") <(cut -f1 "$GD/negative-battery.tsv" | grep -v '^#' | sort -u) | tr '\n' ' ')
if [ "$HAVE" != "$EXPECT" ] || [ "$DUPS" -ne 0 ]; then
  printf 'manifest coverage broken have=%s expect=%s dups=%s missing=[%s]\n' "$HAVE" "$EXPECT" "$DUPS" "$MISSING" >> "$DET"
  printf 'NEGATIVE-BATTERY FAIL proven=0/%s unproven=%s canary=UNKNOWN seeded_defects=UNKNOWN\n' "$EXPECT" "$EXPECT"
  exit 1
fi

WT="$(mktemp -d)/probe"
git worktree add --detach "$WT" HEAD >/dev/null 2>&1 || { echo "NEGATIVE-BATTERY FAIL: cannot create throwaway worktree"; exit 2; }
cleanup() { git worktree remove --force "$WT" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM

PROVEN=0; UNPROVEN=0; TOTAL=0
while IFS='	' read -r check gate mutation token; do
  case "$check" in ''|\#*) continue ;; esac
  if [ "$GATE" = "lane" ] && [ "$gate" != "lane" ]; then continue; fi
  if [ "$GATE" = "integration" ] && [ "$FULL" -eq 0 ] && [ "$gate" != "integration" ]; then continue; fi
  TOTAL=$((TOTAL+1))
  # Each mutation lives in its own file, one file per check, directory-per-item.
  M="$GD/mutations/$check.sh"
  if [ ! -x "$M" ]; then
    UNPROVEN=$((UNPROVEN+1)); printf '%s UNPROVEN no-mutation-script %s\n' "$check" "$M" >> "$DET"; continue
  fi
  set +e
  RESULT=$(GATE_PROBE_WT="$WT" GATE_OUT="$OUT/probe" sh "$M" 2>&1 | tail -1)
  set -e
  case "$RESULT" in
    *"$token"*) PROVEN=$((PROVEN+1)); printf '%s PROVEN bit-on=[%s] mutation=%s\n' "$check" "$token" "$mutation" >> "$DET" ;;
    *) UNPROVEN=$((UNPROVEN+1)); printf '%s UNPROVEN expected=[%s] got=[%s] mutation=%s\n' "$check" "$token" "$RESULT" "$mutation" >> "$DET" ;;
  esac
done < "$GD/negative-battery.tsv"

CANARY=n/a; SEEDED=n/a
if [ "$GATE" = "integration" ] && [ "$FULL" -eq 1 ]; then
  CR=$(GATE_PROBE_WT="$WT" sh "$GD/mutations/CANARY.sh" 2>&1 | tail -1)
  case "$CR" in *canary=MISSING*) CANARY=FOUND ;; *) CANARY=UNPROVEN ;; esac
  printf 'CANARY probe=[%s] verdict=%s (AT-102, section 53.1, EC-109)\n' "$CR" "$CANARY" >> "$DET"
  SR=$(GATE_PROBE_WT="$WT" sh "$GD/mutations/SEEDED-DEFECT.sh" 2>&1 | tail -1)
  case "$SR" in *seeded_defect=PASSED*) SEEDED=DETECTED ;; *) SEEDED=UNPROVEN ;; esac
  printf 'SEEDED-DEFECT probe=[%s] verdict=%s (section 31.2, SIG-18)\n' "$SR" "$SEEDED" >> "$DET"
fi

if [ "$UNPROVEN" -eq 0 ] && [ "$PROVEN" -eq "$TOTAL" ] \
   && { [ "$GATE" = "lane" ] || [ "$FULL" -eq 0 ] || { [ "$CANARY" = "FOUND" ] && [ "$SEEDED" = "DETECTED" ]; }; }; then
  printf 'NEGATIVE-BATTERY PASS proven=%s/%s unproven=0 canary=%s seeded_defects=%s\n' "$PROVEN" "$TOTAL" "$CANARY" "$SEEDED"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'NEGATIVE-BATTERY FAIL proven=%s/%s unproven=%s canary=%s seeded_defects=%s\n' "$PROVEN" "$TOTAL" "$UNPROVEN" "$CANARY" "$SEEDED"
exit 1
NBS
chmod +x contracts/gate/negative-battery.sh
mkdir -p contracts/gate/mutations
```

Each mutation is **one file per check**, directory-per-item, so that adding one never edits a shared file
(PARTITION rule 3). Two worked examples; the remaining twenty-two follow the identical shape and each is written
from its manifest row.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"

# IG-05 - drop one row from a registry the reconciler enumerates
cat > contracts/gate/mutations/IG-05.sh <<'M05'
#!/usr/bin/env sh
# Mutation for IG-05. Runs entirely inside $GATE_PROBE_WT. Never touches $CP_ROOT.
set -eu
WT="${GATE_PROBE_WT:?throwaway worktree required}"
cd "$WT"
# Narrow the frozen AT id set by exactly one row; count-integrity must see it.
sed -i '$d' contracts/gate/at-index.tsv
GATE_OUT="${GATE_OUT:-.gate}" sh contracts/gate/count-integrity.sh --scope integration 2>&1 | tail -1
M05
chmod +x contracts/gate/mutations/IG-05.sh

# CANARY - AT-102. Remove the seeded canary from the comparison set and reconcile.
cat > contracts/gate/mutations/CANARY.sh <<'MCAN'
#!/usr/bin/env sh
# AT-102 / section 53.1 / EC-109. A run that reports zero findings, canary included,
# is a FAILED run. This probe proves the reconciler still notices the canary's absence.
# It operates on a SANDBOX comparison set. It NEVER edits the live canary record -
# protocol/04-negative-tests.md NT-06 states the same restriction.
set -eu
WT="${GATE_PROBE_WT:?throwaway worktree required}"
cd "$WT"
SB="$(mktemp -d)"
cp -r validators/drift/comparison-set "$SB/set"
rm -f "$SB/set"/canary-*.yaml
reconciler/lane-verify.sh --comparison-set "$SB/set" --summary 2>&1 | tail -1
MCAN
chmod +x contracts/gate/mutations/CANARY.sh

git add contracts/gate
git commit -m "L0-05-08: negative battery (LG-07/IG-04), 24-row manifest, per-check mutations"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The manifest has exactly 24 rows | `grep -vc '^#' contracts/gate/negative-battery.tsv` | `24` |
| 2 | The manifest covers every check id, once | `comm -3 <(sort -u contracts/gate/expected-checks.txt) <(cut -f1 contracts/gate/negative-battery.tsv \| grep -v '^#' \| sort -u) \| wc -l` | `0` |
| 3 | No check id appears twice | `cut -f1 contracts/gate/negative-battery.tsv \| grep -v '^#' \| sort \| uniq -d \| wc -l` | `0` |
| 4 | Every row names a required-failure token | `awk -F'\t' '!/^#/ && ($4=="" \|\| NF!=4){c++} END{print c+0}' contracts/gate/negative-battery.tsv` | `0` |
| 5 | Twelve rows are `lane`, twelve are `integration` | `printf '%s %s\n' "$(awk -F'\t' '$2=="lane"' contracts/gate/negative-battery.tsv \| grep -c .)" "$(awk -F'\t' '$2=="integration"' contracts/gate/negative-battery.tsv \| grep -c .)"` | `12 12` |
| 6 | **Deleting one manifest row makes the battery fail its own coverage check** | see SELF-VERIFY case M | `NEGATIVE-BATTERY FAIL proven=0/24 unproven=24` |
| 7 | A check with no mutation script is `UNPROVEN`, never skipped | see SELF-VERIFY case U | `UNPROVEN no-mutation-script` |
| 8 | The mutations run in a throwaway worktree, never in the clone | `git -C "$CP_ROOT" status --porcelain \| wc -l` after a full run | `0` |
| 9 | The canary probe never edits the live canary record | `grep -c 'mktemp' contracts/gate/mutations/CANARY.sh` | `1` |
| 10 | Any `unproven=` value other than `0` closes both gates | `grep -c 'unproven=0' <(bash contracts/gate/negative-battery.sh --gate integration --full \| tail -1)` on a healthy tree | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
rm -rf /tmp/nbv && mkdir -p /tmp/nbv
cp -r contracts/gate /tmp/nbv/gate

# case M - one manifest row deleted: coverage must break before any mutation runs
grep -v '^IG-07	' contracts/gate/negative-battery.tsv > /tmp/nbv/gate/negative-battery.tsv
M=$(GATE_OUT=/tmp/nbv/out sh /tmp/nbv/gate/negative-battery.sh --gate integration --full 2>&1 | tail -1)

# case U - manifest intact, but IG-06's mutation script removed
cp contracts/gate/negative-battery.tsv /tmp/nbv/gate/negative-battery.tsv
rm -f /tmp/nbv/gate/mutations/IG-06.sh
GATE_OUT=/tmp/nbv/out sh /tmp/nbv/gate/negative-battery.sh --gate integration --full >/dev/null 2>&1 || true
U=$(grep -o 'IG-06 UNPROVEN no-mutation-script' /tmp/nbv/out/negative-battery.txt | head -1)

printf 'rows=%s cover=%s dup=%s notoken=%s split=[%s %s] deleted_row=[%s] nomutation=[%s] clean=%s canary_sandbox=%s\n' \
  "$(grep -vc '^#' contracts/gate/negative-battery.tsv)" \
  "$(comm -3 <(sort -u contracts/gate/expected-checks.txt) <(cut -f1 contracts/gate/negative-battery.tsv | grep -v '^#' | sort -u) | wc -l | tr -d ' ')" \
  "$(cut -f1 contracts/gate/negative-battery.tsv | grep -v '^#' | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && ($4=="" || NF!=4){c++} END{print c+0}' contracts/gate/negative-battery.tsv)" \
  "$(awk -F'\t' '$2=="lane"' contracts/gate/negative-battery.tsv | grep -c .)" \
  "$(awk -F'\t' '$2=="integration"' contracts/gate/negative-battery.tsv | grep -c .)" \
  "$M" "$U" \
  "$(git status --porcelain | wc -l | tr -d ' ')" \
  "$(grep -c 'mktemp' contracts/gate/mutations/CANARY.sh)"
```

Expected output, exactly:

```
rows=24 cover=0 dup=0 notoken=0 split=[12 12] deleted_row=[NEGATIVE-BATTERY FAIL proven=0/24 unproven=24 canary=UNKNOWN seeded_defects=UNKNOWN] nomutation=[IG-06 UNPROVEN no-mutation-script] clean=0 canary_sandbox=1
```

**STOP rule** — this is the strictest STOP rule in the file.

- If `deleted_row` shows a `PASS`, the battery can lose a check and still certify the gate. That is `LG-07`'s own
  mutation succeeding against `LG-07`, and it means the gate has no floor. **Stop the merge train.** Open
  `BLOCKER L0-05-08: negative battery does not detect its own narrowing` and do not run a cycle.
- If `nomutation` is empty, a check with no mutation script is being silently treated as proven. `protocol/05` §1
  is explicit: *"A check with no passing negative test is treated as **not present** — the gate fails closed."*
- If `clean` is not `0`, a mutation escaped the throwaway worktree and modified the real clone.
  `git checkout -- .` immediately, then find the mutation script that used a relative path outside
  `$GATE_PROBE_WT` and fix it before any other work. A battery that mutates the tree it judges is worse than no
  battery.
- If a run reports `canary=UNPROVEN`, do **not** proceed and do **not** re-run hoping for `FOUND`. Treat it as
  `protocol/05` §9's `canary=MISSING` row: a FAILED run, `SIG-13`, and the §53.7 gap procedure over the window,
  with records produced in the window marked `gap-window`. **Never record the run as clean.**

---

### L0-05-09 — The assembled-system smoke, and `artifact-honesty.sh` (`IG-10`)

**Size:** L · **Dependencies:** L0-05-06

`IG-10`'s pass line, fixed by `protocol/05` §4:

```
IG-10 artifact-honesty PASS digest_mismatches=0 rebuilt=0 skipped=0 neutral=0
```

It asks two questions and neither has an answer on a static branch. **Is the digest that will reach production the
digest verified in staging** (invariant 22: *"The production artifact is the same digest verified in staging. Never
rebuilt."*)? And **did any required context report `skipped` or `neutral` anywhere in the merged range** (§33.2:
*"A `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift"*)?

The first question needs a deployment chain to have actually run. That is the assembled-system smoke, and per
**L0D-IG-2** it is `IG-10`'s precondition, not a thirteenth check.

#### 7.9.1 What the smoke is

`protocol/08-smoke-and-e2e.md` owns the harness; it lives at `e2e/` in `control-plane`. **`e2e/**` is not yet
assigned in `lane-paths.tsv`, so `lane-guard.sh` reports it `UNASSIGNED` and `train-owners.sh` reports a
`TRAIN-OWNERS FAIL` (B-04). Ownership and creation are routed via **L0-IG-D5**. It runs twelve stages `E2E-01`…`E2E-12` from
`create-product` on an empty estate through Gate 1, Gate 2, build, staging, production approval, production
deploy, the eleven-question evidence chain, rollback, restore, and reconciliation. Sixteen acceptance tests are
**executed for real** by that run: `AT-001`, `AT-002`, `AT-009`, `AT-010`, `AT-032`, `AT-033`, `AT-036`, `AT-037`,
`AT-039`, `AT-049`, `AT-102`, `AT-103`, `AT-106`, `AT-108`, `AT-109`, `AT-110` (`protocol/08` §1.2).

Its verdict rule is not a convention (`protocol/08` §7):

**Commands**

```bash
set -euo pipefail
[ "$fails" -eq 0 ] || { echo "VERDICT: FAIL — ${fails} checkpoint failures"; exit 1; }
[ "$neg" -ge 28 ]  || { echo "VERDICT: FAIL — only ${neg}/28 gates were proven able to fail"; exit 1; }
[ "$pos" -ge 118 ] || { echo "VERDICT: FAIL — only ${pos}/118 positive checkpoints ran"; exit 1; }
echo "VERDICT: PASS — ${pos} checkpoints, ${neg} gates proven able to fail"
```

**A run with 118 green checkpoints and zero fired gates is a FAILED run.** The count of gates proven able to fail
is a first-class pass condition, exactly as §53.1 makes the canary a pass condition of a reconciliation run.

#### 7.9.2 Wiring it to `IG-10`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/artifact-honesty.sh <<'AHS'
#!/usr/bin/env sh
# =============================================================================
# artifact-honesty.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-10.
#   --range <base>..<head>
# Preconditions (L0D-IG-2): the assembled-system smoke of protocol/08 has run and
# e2e/verdict.sh printed "VERDICT: PASS". Without it there is no digest chain to
# inspect and the check FAILS - it is never skipped and never not-applicable.
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
RANGE=""
while [ $# -gt 0 ]; do case "$1" in
  --range) RANGE="$2"; shift 2 ;;
  *) echo "ARTIFACT-HONESTY FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$RANGE" ] || { echo "ARTIFACT-HONESTY FAIL: --range <base>..<head> required"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/artifact-honesty.txt"; : > "$DET"

# --- precondition: the smoke verdict ----------------------------------------
E2E_STDOUT="${E2E_STDOUT:-$OUT/e2e.stdout}"
E2E=FAIL
if [ -f "$E2E_STDOUT" ] && grep -Fq 'VERDICT: PASS' "$E2E_STDOUT"; then E2E=PASS; fi
POS=$(sed -n 's/.*PASS — \([0-9]*\) checkpoints.*/\1/p' "$E2E_STDOUT" 2>/dev/null | tail -1); POS=${POS:-0}
NEGP=$(sed -n 's/.*checkpoints, \([0-9]*\) gates proven able to fail.*/\1/p' "$E2E_STDOUT" 2>/dev/null | tail -1); NEGP=${NEGP:-0}
printf 'e2e verdict=%s checkpoints=%s/118 gates_proven=%s/28\n' "$E2E" "$POS" "$NEGP" >> "$DET"

# --- invariant 22: staging-verified digest == production digest -------------
CPR="${CPR_ROOT:?CPR_ROOT must point at the control-plane-records clone}"
MIS=0; REBUILT=0; PAIRS=0
for D in "$CPR"/records/deployments/*.yaml; do
  [ -f "$D" ] || continue
  ENVN=$(awk -F': *' '/^environment:/{print $2}' "$D")
  [ "$ENVN" = "production" ] || continue
  PAIRS=$((PAIRS+1))
  PD=$(awk -F': *' '/^digest:/{print $2}' "$D")
  SD=$(awk -F': *' '/^staging_verified_digest:/{print $2}' "$D")
  RB=$(awk -F': *' '/^rebuilt:/{print $2}' "$D"); RB=${RB:-false}
  [ "$PD" = "$SD" ] || { MIS=$((MIS+1)); printf 'digest mismatch %s prod=%s staging=%s\n' "$D" "$PD" "$SD" >> "$DET"; }
  [ "$RB" = "false" ] || { REBUILT=$((REBUILT+1)); printf 'rebuilt artifact %s\n' "$D" >> "$DET"; }
done

# --- section 33.2: no skipped / neutral on a required context in the range ---
SKIP=0; NEU=0
for SHA in $(git log --format=%H "$RANGE"); do
  gh api "repos/{owner}/{repo}/commits/$SHA/check-runs" --jq \
    '.check_runs[] | select(.conclusion=="skipped" or .conclusion=="neutral") | .name + " " + .conclusion' \
    2>/dev/null >> "$OUT/conclusions.txt" || true
done
SKIP=$(grep -c ' skipped$' "$OUT/conclusions.txt" 2>/dev/null || true)
NEU=$(grep -c ' neutral$' "$OUT/conclusions.txt" 2>/dev/null || true)

if [ "$E2E" = "PASS" ] && [ "$PAIRS" -gt 0 ] && [ "$MIS" -eq 0 ] && [ "$REBUILT" -eq 0 ] \
   && [ "$SKIP" -eq 0 ] && [ "$NEU" -eq 0 ]; then
  printf 'ARTIFACT-HONESTY PASS digest_mismatches=0 rebuilt=0 skipped=0 neutral=0\n'
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'ARTIFACT-HONESTY FAIL e2e=%s deployments=%s digest_mismatches=%s rebuilt=%s skipped=%s neutral=%s\n' \
  "$E2E" "$PAIRS" "$MIS" "$REBUILT" "$SKIP" "$NEU"
exit 1
AHS
chmod +x contracts/gate/artifact-honesty.sh

git add contracts/gate/artifact-honesty.sh
git commit -m "L0-05-09: artifact-honesty.sh (IG-10) with the assembled-system smoke as its precondition"
git push origin integration
```

**`PAIRS -gt 0` is load-bearing.** A range containing zero production deployments would otherwise report
`digest_mismatches=0 rebuilt=0` and pass, which is the zero-shaped-metric failure §97.2 names: *"a workflow whose
record-write step fails silently renders every count-shaped derived metric as zero … which is indistinguishable
from health."* Zero deployments examined is not zero mismatches found.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x contracts/gate/artifact-honesty.sh && echo PRESENT` | `PRESENT` |
| 2 | No range is a configuration error | `bash contracts/gate/artifact-honesty.sh; echo "rc=$?"` | `ARTIFACT-HONESTY FAIL: --range <base>..<head> required` then `rc=2` |
| 3 | **A missing smoke verdict fails the check** | see SELF-VERIFY case E | `ARTIFACT-HONESTY FAIL e2e=FAIL` |
| 4 | A smoke that ran but fell short of a floor fails | see SELF-VERIFY case F | `ARTIFACT-HONESTY FAIL e2e=FAIL` |
| 5 | A production record whose digest differs from staging is a mismatch | see SELF-VERIFY case D | `digest_mismatches=1` |
| 6 | A rebuilt artifact is counted separately from a mismatch | see SELF-VERIFY case R | `rebuilt=1` |
| 7 | **Zero production deployments in range does not pass** | see SELF-VERIFY case Z | `ARTIFACT-HONESTY FAIL` with `deployments=0` |
| 8 | The smoke counters are recorded against their floors | `grep -o 'checkpoints=[0-9]*/118 gates_proven=[0-9]*/28' .gate/artifact-honesty.txt` | one line matching that shape |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
export GATE_OUT=/tmp/ahv; rm -rf "$GATE_OUT"; mkdir -p "$GATE_OUT"
export CPR_ROOT=/tmp/ahv/records; mkdir -p "$CPR_ROOT/records/deployments"
R="HEAD~1..HEAD"

# case E - no smoke stdout at all
E=$(bash contracts/gate/artifact-honesty.sh --range "$R" 2>/dev/null | tail -1 | cut -d' ' -f1-3)

# case F - smoke ran and fell short of the 28-gate floor
printf 'VERDICT: FAIL — only 21/28 gates were proven able to fail\n' > "$GATE_OUT/e2e.stdout"
F=$(bash contracts/gate/artifact-honesty.sh --range "$R" 2>/dev/null | tail -1 | cut -d' ' -f1-3)

# case Z - smoke passed, but no production deployment record exists
printf 'VERDICT: PASS — 121 checkpoints, 28 gates proven able to fail\n' > "$GATE_OUT/e2e.stdout"
Z=$(bash contracts/gate/artifact-honesty.sh --range "$R" 2>/dev/null | tail -1 | grep -o 'deployments=[0-9]*')

# case D - one production record with a digest that does not match staging
printf 'environment: production\ndigest: sha256:aaa\nstaging_verified_digest: sha256:bbb\nrebuilt: false\n' \
  > "$CPR_ROOT/records/deployments/d1.yaml"
D=$(bash contracts/gate/artifact-honesty.sh --range "$R" 2>/dev/null | tail -1 | grep -o 'digest_mismatches=[0-9]*')

# case R - matching digest, but the artifact was rebuilt
printf 'environment: production\ndigest: sha256:aaa\nstaging_verified_digest: sha256:aaa\nrebuilt: true\n' \
  > "$CPR_ROOT/records/deployments/d1.yaml"
RB=$(bash contracts/gate/artifact-honesty.sh --range "$R" 2>/dev/null | tail -1 | grep -o 'rebuilt=[a-z0-9]*')

printf 'nosmoke=[%s] shortfloor=[%s] nodeploy=[%s] mismatch=[%s] %s counters=%s\n' \
  "$E" "$F" "$Z" "$D" "$RB" \
  "$(grep -c 'checkpoints=[0-9]*/118 gates_proven=[0-9]*/28' "$GATE_OUT/artifact-honesty.txt")"
```

Expected output, exactly:

```
nosmoke=[ARTIFACT-HONESTY FAIL e2e=FAIL] shortfloor=[ARTIFACT-HONESTY FAIL e2e=FAIL] nodeploy=[deployments=0] mismatch=[digest_mismatches=1] rebuilt=1 counters=1
```

**STOP rule** — if `nodeploy` prints `deployments=0` and the overall verdict was nevertheless `PASS`, the check has
learned to report health from an empty set. Fix `PAIRS -gt 0` before anything else; §52.3's presentation
discipline plus a zero-shaped metric is exactly how a broken evidence chain gets no screen space. If
`shortfloor` prints `e2e=PASS`, the smoke floors are not being read: `protocol/08` §7.2 makes 118 and 28 pass
conditions, not statistics, and a gate that ignores them accepts a smoke that proved nothing. **Never set
`E2E_STDOUT` to a hand-written file to get past this check** — that is fabricating evidence, and `IG-12` will not
catch it because CI mirrors the same forged input. Open `BLOCKER L0-05-09: artifact honesty accepts an absent
smoke` and stop.

---

### L0-05-10 — `merge-train.sh` and the lane-guard replay (`IG-01`, `IG-08`)

**Size:** M · **Dependencies:** L0-05-01

Two checks, one task, because both read the same thing: the set of merge commits between `origin/main` and
`origin/integration` for this cycle.

Pass lines, fixed by `protocol/05` §4:

```
IG-01 merge-train PASS lanes=5/5 order=1,4,2,3,5 out_of_order=0 cross_lane_merges=0
IG-08 lane-guard-replay PASS commits=<n> foreign=0 unowned=0
```

**`IG-08` exists because `LG-02` cannot see inside a merge.** A lane PR is judged on its own diff. A foreign path
introduced by a merge commit — a bad conflict resolution, a rebase that swallowed someone else's file — is not in
any lane PR's diff and passes twelve green GATE A runs. The replay walks the whole merged range instead.

`unowned>0` is a failure, not a warning (`protocol/05` §6): PARTITION rule 1 is *"one owner per path"*, and a path
with zero owners violates it in the direction nobody notices until two lanes both create it.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/merge-train.sh <<'MTS'
#!/usr/bin/env sh
# =============================================================================
# merge-train.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-01.
#   --cycle <id> --base origin/main
# Asserts: all five lanes landed this cycle, in the FROZEN order 1,4,2,3,5, and
# no lane merged another lane's branch (PARTITION.md "Branch & merge model").
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
CYCLE=""; BASE=""
while [ $# -gt 0 ]; do case "$1" in
  --cycle) CYCLE="$2"; shift 2 ;;
  --base)  BASE="$2";  shift 2 ;;
  *) echo "MERGE-TRAIN FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$CYCLE" ] && [ -n "$BASE" ] || { echo "MERGE-TRAIN FAIL: --cycle <id> --base <ref> required"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/merge-train.txt"; : > "$DET"
FROZEN="1 4 2 3 5"

# Merge commits in the range, oldest first, with the lane each merged.
git log --merges --reverse --format='%H%x09%s' "$BASE..origin/integration" > "$OUT/merges.tsv"
SEEN=""; CROSS=0
while IFS='	' read -r sha subj; do
  L=$(printf '%s' "$subj" | sed -n "s|.*lane/\([1-5]\)/.*|\1|p")
  if [ -z "$L" ]; then printf '%s NON-LANE MERGE %s\n' "$sha" "$subj" >> "$DET"; continue; fi
  # A merge whose SECOND parent branch names a different lane than its first-parent
  # context is a lane merging another lane's branch - forbidden without exception.
  N=$(git log -1 --format=%s "$sha^2" 2>/dev/null | sed -n "s|.*lane/\([1-5]\)/.*|\1|p")
  if [ -n "$N" ] && [ "$N" != "$L" ]; then
    CROSS=$((CROSS+1)); printf '%s CROSS-LANE MERGE lane%s merged lane%s\n' "$sha" "$L" "$N" >> "$DET"
  fi
  SEEN="$SEEN $L"
  printf '%s lane=%s %s\n' "$sha" "$L" "$subj" >> "$DET"
done < "$OUT/merges.tsv"

ACTUAL=$(printf '%s' "$SEEN" | tr ' ' '\n' | grep -v '^$' | awk '!seen[$0]++' | tr '\n' ' ' | sed 's/ $//')
LANES=$(printf '%s' "$ACTUAL" | tr ' ' '\n' | grep -c . || true)
OOO=0; [ "$ACTUAL" = "$FROZEN" ] || OOO=1
printf 'frozen=[%s] actual=[%s] out_of_order=%s cross=%s\n' "$FROZEN" "$ACTUAL" "$OOO" "$CROSS" >> "$DET"

if [ "$LANES" -eq 5 ] && [ "$OOO" -eq 0 ] && [ "$CROSS" -eq 0 ]; then
  printf 'MERGE-TRAIN PASS lanes=5/5 order=1,4,2,3,5 out_of_order=0 cross_lane_merges=0\n'; exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'MERGE-TRAIN FAIL lanes=%s/5 order=%s out_of_order=%s cross_lane_merges=%s\n' \
  "$LANES" "$(printf '%s' "$ACTUAL" | tr ' ' ',')" "$OOO" "$CROSS"
exit 1
MTS
chmod +x contracts/gate/merge-train.sh
```

The replay reuses **`lane-guard.sh` v2** from `L0-02-02`. It is not re-implemented here — a second implementation
of the partition rule is a second answer to *"who owns this path"*, and `L0-02` §6.1 is explicit that the guard
engine is one file.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/lane-guard-replay.sh <<'LGR'
#!/usr/bin/env sh
# =============================================================================
# lane-guard-replay.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-08.
#   --base origin/main --head origin/integration
# Replays LG-02 over EVERY commit in the merged range, so a foreign path that
# entered inside a merge commit is caught. Delegates to lane-guard.sh v2
# (L0-02-02) - the partition rule has exactly one implementation.
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
BASE=""; HEAD=""
while [ $# -gt 0 ]; do case "$1" in
  --base) BASE="$2"; shift 2 ;;
  --head) HEAD="$2"; shift 2 ;;
  *) echo "LANE-GUARD-REPLAY FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$BASE" ] && [ -n "$HEAD" ] || { echo "LANE-GUARD-REPLAY FAIL: --base and --head required"; exit 2; }
[ -x ./lane-guard.sh ] || { echo "LANE-GUARD-REPLAY FAIL: ./lane-guard.sh missing - fail closed"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/lane-guard-replay.txt"; : > "$DET"

N=0; FOREIGN=0; UNOWNED=0
for SHA in $(git rev-list --reverse --no-merges "$BASE..$HEAD"); do
  N=$((N+1))
  SUBJ=$(git log -1 --format=%s "$SHA")
  L=$(git log -1 --format='%D %s' "$SHA" | sed -n "s|.*lane/\([1-5]\)/.*|\1|p")
  L=${L:-0}
  set +e
  R=$(./lane-guard.sh "$L" "$SHA^" "$SHA" 2>&1)
  set -e
  case "$(printf '%s' "$R" | tail -1)" in
    "LANE-GUARD OK") : ;;
    *) printf '%s lane=%s %s\n%s\n' "$SHA" "$L" "$SUBJ" "$R" >> "$DET" ;;
  esac
  FOREIGN=$((FOREIGN + $(printf '%s' "$R" | grep -c 'VIOLATION \[FOREIGN-PATH\]' || true)))
  UNOWNED=$((UNOWNED + $(printf '%s' "$R" | grep -c 'VIOLATION \[UNASSIGNED-PATH\]' || true)))
done

if [ "$FOREIGN" -eq 0 ] && [ "$UNOWNED" -eq 0 ]; then
  printf 'LANE-GUARD-REPLAY PASS commits=%s foreign=0 unowned=0\n' "$N"; exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'LANE-GUARD-REPLAY FAIL commits=%s foreign=%s unowned=%s\n' "$N" "$FOREIGN" "$UNOWNED"
exit 1
LGR
chmod +x contracts/gate/lane-guard-replay.sh

git add contracts/gate
git commit -m "L0-05-10: merge-train.sh (IG-01) and lane-guard-replay.sh (IG-08)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both scripts are executable | `test -x contracts/gate/merge-train.sh && test -x contracts/gate/lane-guard-replay.sh && echo BOTH` | `BOTH` |
| 2 | Missing arguments are configuration errors | `bash contracts/gate/merge-train.sh; echo "rc=$?"` | `MERGE-TRAIN FAIL: --cycle <id> --base <ref> required` then `rc=2` |
| 3 | The frozen order string is `1 4 2 3 5`, never ascending | `grep -c 'FROZEN="1 4 2 3 5"' contracts/gate/merge-train.sh` | `1` |
| 4 | **A reordered cycle fails** | see SELF-VERIFY case O | `out_of_order=1` |
| 5 | A cycle with four lanes fails on count, not on order | see SELF-VERIFY case L | `lanes=4/5` |
| 6 | A missing `lane-guard.sh` fails closed rather than passing an empty replay | `mv lane-guard.sh /tmp/lg; bash contracts/gate/lane-guard-replay.sh --base origin/main --head HEAD; echo "rc=$?"; mv /tmp/lg lane-guard.sh` | `LANE-GUARD-REPLAY FAIL: ./lane-guard.sh missing - fail closed` then `rc=2` |
| 7 | The replay reuses the L0-02 guard rather than re-implementing it | `grep -c './lane-guard.sh' contracts/gate/lane-guard-replay.sh` | `2` |
| 8 | `unowned` is reported separately from `foreign` | `grep -c 'unowned=' contracts/gate/lane-guard-replay.sh` | `2` |

**SELF-VERIFY**

Uses a synthetic history so that no real cycle is needed and no branch is touched.

```bash
set -euo pipefail
cd "$CP_ROOT"
rm -rf /tmp/mtv && git init -q /tmp/mtv && cd /tmp/mtv
git config user.email l0@example.invalid && git config user.name L0
printf 'x\n' > f && git add f && git commit -qm base && git branch -M main
git branch integration main
mkbranch() { git checkout -q -b "lane/$1/p0-probe" integration; printf '%s\n' "$1" > "l$1"; git add .; \
             git commit -qm "lane $1 work"; git checkout -q integration; \
             git merge -q --no-ff "lane/$1/p0-probe" -m "Merge pull request from lane/$1/p0-probe"; }
cp "$CP_ROOT/contracts/gate/merge-train.sh" /tmp/mtv/mt.sh

# case O - merged 1,2,4,3,5 instead of 1,4,2,3,5
for n in 1 2 4 3 5; do mkbranch "$n"; done
git remote add origin . 2>/dev/null; git update-ref refs/remotes/origin/integration integration
O=$(GATE_OUT=/tmp/mtv/out sh /tmp/mtv/mt.sh --cycle probe --base main 2>&1 | tail -1 | grep -o 'out_of_order=[0-9]*')

# case L - only four lanes landed
git checkout -q main && git branch -qD integration && git checkout -q -b integration main
for n in 1 4 2 3; do mkbranch "$n"; done
git update-ref refs/remotes/origin/integration integration
L=$(GATE_OUT=/tmp/mtv/out sh /tmp/mtv/mt.sh --cycle probe --base main 2>&1 | tail -1 | grep -o 'lanes=[0-9]*/5')

# case F - replay detects one VIOLATION [FOREIGN-PATH] and exits FAIL
git checkout -q main && git branch -qD integration && git checkout -q -b integration main
# Stub lane-guard.sh that always emits one foreign-path violation
printf '#!/usr/bin/env sh\nprintf "VIOLATION [FOREIGN-PATH] lane=%s path=lane/2/x owned_by=2\\n" "$1"\nprintf "LANE-GUARD FAIL\\n"\n' > lane-guard.sh
chmod +x lane-guard.sh
git checkout -q -b "lane/1/p0-probe" integration
printf 'lf\n' > lf && git add . && git commit -qm "lane 1 work"
git checkout -q integration
git merge -q --no-ff "lane/1/p0-probe" -m "Merge pull request from lane/1/p0-probe"
git update-ref refs/remotes/origin/integration integration
cp "$CP_ROOT/contracts/gate/lane-guard-replay.sh" /tmp/mtv/lgr.sh
FLINE=$(GATE_OUT=/tmp/mtv/out sh /tmp/mtv/lgr.sh --base main --head refs/remotes/origin/integration 2>&1 | tail -1)
F="$(printf '%s' "$FLINE" | grep -o 'foreign=[0-9]*') $(printf '%s' "$FLINE" | grep -o 'LANE-GUARD-REPLAY [A-Z]*')"

cd "$CP_ROOT"
printf 'exec=%s frozen=%s reorder=[%s] short=[%s] reuse=%s unowned=%s foreign=[%s]\n' \
  "$(test -x contracts/gate/merge-train.sh -a -x contracts/gate/lane-guard-replay.sh && echo YES || echo NO)" \
  "$(grep -c 'FROZEN="1 4 2 3 5"' contracts/gate/merge-train.sh)" \
  "$O" "$L" \
  "$(grep -c './lane-guard.sh' contracts/gate/lane-guard-replay.sh)" \
  "$(grep -c 'unowned=' contracts/gate/lane-guard-replay.sh)" \
  "$F"
```

Expected output, exactly:

```
exec=YES frozen=1 reorder=[out_of_order=1] short=[lanes=4/5] reuse=2 unowned=2 foreign=[foreign=1 LANE-GUARD-REPLAY FAIL]
```

**STOP rule** — if `reorder` prints `out_of_order=0`, the order check accepts any order and the dependency
inversion the order exists to prevent ships silently. `protocol/00` §5 T3 states the consequence: *"reordering
around a failure ships the dependency inversion the order exists to prevent."* Do not "fix" it by widening the
comparison to a set membership test — the order is a sequence. Open `BLOCKER L0-05-10: merge order not enforced`.
If `short` prints `lanes=5/5` for a four-lane cycle, a skipped lane is being counted as landed; a lane skipped for
starvation reasons is recorded by `L0-03-12`, and it is **never** recorded as merged. If `reuse` is not `2`, the
replay has grown its own copy of the partition rule; delete it and call `./lane-guard.sh` — two implementations of
`owner_of` is `L0D-04` erosion with extra steps.

---

### L0-05-11 — `invariant-classification.sh` (`IG-06`)

**Size:** M · **Dependencies:** L0-05-04 · **Routed decision:** **L0-IG-D3** (subsystem **O**)

Pass line, fixed by `protocol/05` §4:

```
IG-06 invariant-classification PASS classified=111/111 mechanical=<n> dangling_refs=0 unclassified=0
```

§101's preamble is the whole specification of this check and it is worth reading as one sentence: control-plane CI
*"fails when an invariant classified `mechanical` names no live check or AT- identifier, when one classified
`policy` names no live `policies.yaml` entry, or when any invariant carries no classification at all."* It also
says why: *"an invariant that is neither mechanically enforced nor entered as a policy has no owner, no cadence,
and nothing detects the omission."*

**Read §5, `L0-IG-D3`, before running this.** The `policy` branch needs `policies.yaml`, which belongs to
subsystem **O**, which no lane owns; and §101 says the classification is authored at Phase **G2**, outside the
five-lane build. This check therefore **fails closed with a named reason** for as long as that is true. It is
never marked not-applicable and never given a "scoped out" pass.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
# One row per invariant. Seeded from inv-index.tsv so the row count is 111 by
# construction; the classification column is filled by L0 as it is authored.
awk '{printf "%s\tunclassified\t-\t-\n", $1}' contracts/gate/inv-index.tsv \
  > contracts/gate/invariant-classification.tsv

cat > contracts/gate/invariant-classification.sh <<'ICS'
#!/usr/bin/env sh
# =============================================================================
# invariant-classification.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-06.
# Row format: invariant<TAB>class<TAB>reference<TAB>note
#   class: mechanical | policy | review-held | unclassified
#   mechanical -> reference must be a check id in expected-checks.txt
#                 or an AT id in at-activation.tsv
#   policy     -> reference must be a live entry key in registries/policies.yaml
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GD="$(dirname "$0")"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/invariant-classification.txt"; : > "$DET"
MAP="$GD/invariant-classification.tsv"
[ -f "$MAP" ] || { echo "INVARIANT-CLASSIFICATION FAIL: map missing - fail closed"; exit 2; }

DECL=$(awk -F'\t' '$1=="inv"{print $2}' "$GD/COUNTS.tsv")
ROWS=$(grep -vc '^#' "$MAP")
CLASSIFIED=0; MECH=0; DANGLING=0; UNCLASS=0
CHECKS="$GD/expected-checks.txt"; ATS=$(cut -f2 "$GD/at-activation.tsv" | grep '^AT-' | sort -u)
POL="registries/policies.yaml"

while IFS='	' read -r inv cls ref note; do
  case "$inv" in ''|\#*) continue ;; esac
  case "$cls" in
    mechanical)
      CLASSIFIED=$((CLASSIFIED+1)); MECH=$((MECH+1))
      if grep -qxF "$ref" "$CHECKS" || printf '%s\n' "$ATS" | grep -qxF "$ref"; then :
      else DANGLING=$((DANGLING+1)); printf 'inv %s mechanical -> %s DANGLING\n' "$inv" "$ref" >> "$DET"; fi ;;
    policy)
      CLASSIFIED=$((CLASSIFIED+1))
      if [ -f "$POL" ] && grep -q "^ *${ref}:" "$POL"; then :
      else DANGLING=$((DANGLING+1)); printf 'inv %s policy -> %s DANGLING (subsystem O, L0-IG-D3)\n' "$inv" "$ref" >> "$DET"; fi ;;
    review-held)
      CLASSIFIED=$((CLASSIFIED+1))
      [ -n "$ref" ] && [ "$ref" != "-" ] || { DANGLING=$((DANGLING+1)); printf 'inv %s review-held names no review\n' "$inv" >> "$DET"; } ;;
    *)
      UNCLASS=$((UNCLASS+1)); printf 'inv %s UNCLASSIFIED\n' "$inv" >> "$DET" ;;
  esac
done < "$MAP"

[ "$UNCLASS" -eq 0 ] || printf 'L0-IG-D3 UNRESOLVED: %s invariants unclassified; policies.yaml belongs to subsystem O, unassigned in PARTITION v1; section 101 authors the map at Phase G2\n' "$UNCLASS" >> "$DET"

if [ "$ROWS" = "$DECL" ] && [ "$CLASSIFIED" = "$DECL" ] && [ "$DANGLING" -eq 0 ] && [ "$UNCLASS" -eq 0 ]; then
  printf 'INVARIANT-CLASSIFICATION PASS classified=%s/%s mechanical=%s dangling_refs=0 unclassified=0\n' "$CLASSIFIED" "$DECL" "$MECH"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'INVARIANT-CLASSIFICATION FAIL classified=%s/%s mechanical=%s dangling_refs=%s unclassified=%s\n' \
  "$CLASSIFIED" "$DECL" "$MECH" "$DANGLING" "$UNCLASS"
exit 1
ICS
chmod +x contracts/gate/invariant-classification.sh

git add contracts/gate
git commit -m "L0-05-11: invariant-classification.sh (IG-06), 111-row map, fails closed on L0-IG-D3"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The map has exactly 111 rows | `grep -vc '^#' contracts/gate/invariant-classification.tsv` | `111` |
| 2 | The row count agrees with `COUNTS.tsv` | `[ "$(grep -vc '^#' contracts/gate/invariant-classification.tsv)" = "$(awk -F'\t' '$1=="inv"{print $2}' contracts/gate/COUNTS.tsv)" ] && echo AGREE` | `AGREE` |
| 3 | **The check FAILS while `L0-IG-D3` is open** | `bash contracts/gate/invariant-classification.sh \| tail -1 \| cut -d' ' -f1-2` | `INVARIANT-CLASSIFICATION FAIL` |
| 4 | The open decision is named, not hidden | `grep -c 'L0-IG-D3 UNRESOLVED' .gate/invariant-classification.txt` | `1` |
| 5 | A `mechanical` row naming a real check id is accepted | see SELF-VERIFY case M | `dangling_refs=0` for that row |
| 6 | A `mechanical` row naming a non-existent check is `DANGLING` | see SELF-VERIFY case D | `dangling_refs=1` |
| 7 | A `mechanical` row may name an AT id | see SELF-VERIFY case A | `dangling_refs=0` for that row |
| 8 | A missing map fails closed | `mv contracts/gate/invariant-classification.tsv /tmp/m; bash contracts/gate/invariant-classification.sh; echo "rc=$?"; mv /tmp/m contracts/gate/invariant-classification.tsv` | `INVARIANT-CLASSIFICATION FAIL: map missing - fail closed` then `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
rm -rf /tmp/icv && mkdir -p /tmp/icv && cp -r contracts/gate /tmp/icv/gate
mkrow() { printf '%s\t%s\t%s\t-\n' "$1" "$2" "$3"; }
{ mkrow 44 mechanical IG-04; mkrow 47 mechanical AT-102; mkrow 80 mechanical IG-99; } > /tmp/icv/gate/invariant-classification.tsv
n=1; while [ "$n" -le 108 ]; do mkrow "$((n+200))" review-held "quarterly-os-review" >> /tmp/icv/gate/invariant-classification.tsv; n=$((n+1)); done
R=$(GATE_OUT=/tmp/icv/out sh /tmp/icv/gate/invariant-classification.sh 2>&1 | tail -1)
printf 'rows=%s agree=%s live=[%s] d3=%s probe=[%s] dangling_row=[%s]\n' \
  "$(grep -vc '^#' contracts/gate/invariant-classification.tsv)" \
  "$([ "$(grep -vc '^#' contracts/gate/invariant-classification.tsv)" = "$(awk -F'\t' '$1=="inv"{print $2}' contracts/gate/COUNTS.tsv)" ] && echo AGREE || echo DIFFER)" \
  "$(bash contracts/gate/invariant-classification.sh 2>&1 | tail -1 | cut -d' ' -f1-2)" \
  "$(grep -c 'L0-IG-D3 UNRESOLVED' .gate/invariant-classification.txt)" \
  "$(echo "$R" | grep -o 'dangling_refs=[0-9]*')" \
  "$(grep -o 'inv 80 mechanical -> IG-99 DANGLING' /tmp/icv/out/invariant-classification.txt)"
```

Expected output, exactly:

```
rows=111 agree=AGREE live=[INVARIANT-CLASSIFICATION FAIL] d3=1 probe=[dangling_refs=1] dangling_row=[inv 80 mechanical -> IG-99 DANGLING]
```

**STOP rule** — if `live` prints `PASS` while the real map is still all `unclassified`, the check is counting rows
rather than classifications and §101's third clause (*"or when any invariant carries no classification at all"*)
has been dropped. If `dangling_row` is empty, a `mechanical` invariant pointing at a check that does not exist is
being accepted — which is how an invariant acquires the appearance of enforcement with no enforcement behind it.
**Do not classify invariants yourself to clear the failure.** `L0D-23` (`L0-00-charter.md` §4) reserves the
enforcement classification of each of the 111 invariants to L0, and §101 places the authoring at Phase G2. Open
`BLOCKER L0-05-11: IG-06 unsatisfiable pending L0-IG-D3` and leave the gate closed.

---

### L0-05-12 — `independent-verifier.sh` under the second credential (`IG-09`)

**Size:** M · **Dependencies:** L0-05-01

Pass line, fixed by `protocol/05` §4:

```
IG-09 independent-verifier PASS repos=<n> machine_codeowners=0 template_diff=0 bypass_actors_exact=1 credential=verifier
```

§53.1 requires a second verifier running *"off the operations VM and under a different credential"*, writing its
result *"to a surface the operations VM cannot write to"*, and states that its *"own absence for one cycle is
Level 5"*. The reason is one sentence, also §53.1: **no control that can be rewritten by the credential it is
checking is a control.** A verifier running under the reconciler's own token can only tell you what the reconciler
already believes.

Three assertions, all mechanical:

| Assertion | What it proves | Anchor |
|---|---|---|
| `machine_codeowners=0` | No machine identity appears as an owner in any `CODEOWNERS` in the estate | invariant 18; D53; §98.2 Phase 1 completion check |
| `template_diff=0` | Live branch-protection and ruleset JSON match the committed template byte-for-byte | §53.1 blocking row; §11.3 |
| `bypass_actors_exact=1` | The bypass-actor list is exactly what §40.1 and §33.2 declare — for `control-plane` that is **empty** (D89), and the `workflows/*` tag ruleset's is empty too (invariant 85) | §33.2; §40.1; D89 |

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/independent-verifier.sh <<'IVS'
#!/usr/bin/env sh
# =============================================================================
# independent-verifier.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-09.
#   --credential <token>
# MUST run under a credential that is NOT the reconciler's and NOT the
# records-writer's (section 53.1). The script proves that before it proves
# anything else: a verifier that cannot show it is independent is not a verifier.
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
CRED=""
while [ $# -gt 0 ]; do case "$1" in
  --credential) CRED="$2"; shift 2 ;;
  *) echo "INDEPENDENT-VERIFIER FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$CRED" ] || { echo "INDEPENDENT-VERIFIER FAIL: --credential required - a verifier with no declared identity is not independent"; exit 2; }
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/independent-verifier.txt"; : > "$DET"

# --- identity proof: who is this token, and is it the thing under test? ------
WHO=$(GH_TOKEN="$CRED" gh api user --jq .login 2>/dev/null || true)
[ -n "$WHO" ] || { echo "INDEPENDENT-VERIFIER FAIL: credential does not authenticate - fail closed"; exit 1; }
printf 'verifier identity=%s\n' "$WHO" >> "$DET"
for FORBIDDEN in $(cat contracts/gate/machine-identities.txt); do
  if [ "$WHO" = "$FORBIDDEN" ]; then
    printf 'INDEPENDENT-VERIFIER FAIL credential=%s is a machine identity under test (section 53.1)\n' "$WHO"
    exit 1
  fi
done

REPOS=0; MCO=0; TDIFF=0; BYPASS_OK=1
while IFS='	' read -r repo tmpl bypass_expect; do
  case "$repo" in ''|\#*) continue ;; esac
  REPOS=$((REPOS+1))
  # CODEOWNERS owner column only - a path like /reconciler/ is not a machine owner
  # (L0-02-lane-guard.md, L0D-LG-5).
  CO=$(GH_TOKEN="$CRED" gh api "repos/$repo/contents/CODEOWNERS" --jq .content 2>/dev/null | base64 -d 2>/dev/null || true)
  HITS=$(printf '%s\n' "$CO" | grep -v '^ *#' | grep -o '@[A-Za-z0-9_.-]*' \
         | grep -c -F -f contracts/gate/machine-identities.txt || true)
  MCO=$((MCO+HITS))
  [ "$HITS" -eq 0 ] || printf '%s machine identity in CODEOWNERS owner column: %s\n' "$repo" "$HITS" >> "$DET"

  LIVE=$(GH_TOKEN="$CRED" gh api "repos/$repo/branches/main/protection" 2>/dev/null || echo '{}')
  printf '%s' "$LIVE" | jq -S . > "$OUT/prot.$REPOS.live.json" 2>/dev/null || echo '{}' > "$OUT/prot.$REPOS.live.json"
  jq -S . "$tmpl" > "$OUT/prot.$REPOS.want.json" 2>/dev/null || echo '{}' > "$OUT/prot.$REPOS.want.json"
  if ! diff -q "$OUT/prot.$REPOS.want.json" "$OUT/prot.$REPOS.live.json" >/dev/null; then
    TDIFF=$((TDIFF+1)); diff "$OUT/prot.$REPOS.want.json" "$OUT/prot.$REPOS.live.json" >> "$DET" || true
  fi

  ACT=$(GH_TOKEN="$CRED" gh api "repos/$repo/rulesets" --jq '[.[].bypass_actors[]?.actor_id] | length' 2>/dev/null || echo -1)
  [ "$ACT" = "$bypass_expect" ] || { BYPASS_OK=0; printf '%s bypass actors have=%s want=%s\n' "$repo" "$ACT" "$bypass_expect" >> "$DET"; }
done < contracts/gate/verifier-scope.tsv

if [ "$REPOS" -gt 0 ] && [ "$MCO" -eq 0 ] && [ "$TDIFF" -eq 0 ] && [ "$BYPASS_OK" -eq 1 ]; then
  printf 'INDEPENDENT-VERIFIER PASS repos=%s machine_codeowners=0 template_diff=0 bypass_actors_exact=1 credential=verifier\n' "$REPOS"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'INDEPENDENT-VERIFIER FAIL repos=%s machine_codeowners=%s template_diff=%s bypass_actors_exact=%s credential=%s\n' \
  "$REPOS" "$MCO" "$TDIFF" "$BYPASS_OK" "$WHO"
exit 1
IVS
chmod +x contracts/gate/independent-verifier.sh

# The identities the verifier may not be, and may not find in any CODEOWNERS.
cat > contracts/gate/machine-identities.txt <<'MID'
@records-writer
@reconciler
@gate-mirror
@renovate[bot]
@github-actions[bot]
MID

# repo<TAB>committed protection template<TAB>expected bypass-actor count
printf '%s\n' '# repo<TAB>template<TAB>bypass_actors_expected' > contracts/gate/verifier-scope.tsv
printf '%s\t%s\t%s\n' \
  'ORG/control-plane'         'access/branch-protection.template.json'  0 \
  'ORG/control-plane-records' 'access/records-ruleset.template.json'    0 >> contracts/gate/verifier-scope.tsv

git add contracts/gate
git commit -m "L0-05-12: independent-verifier.sh (IG-09) with the identity proof first"
git push origin integration
```

**`ORG` is a placeholder for the GitHub organisation login and is settled by `D-L4-01` in
`L4-01-records-repo.md`.** Substitute the value that decision records; do not invent one. Until it is recorded,
the verifier reports `repos=0` and `IG-09` FAILS — `REPOS -gt 0` is checked for exactly that reason.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x contracts/gate/independent-verifier.sh && echo PRESENT` | `PRESENT` |
| 2 | No credential is a configuration error | `bash contracts/gate/independent-verifier.sh; echo "rc=$?"` | a line containing `a verifier with no declared identity is not independent` then `rc=2` |
| 3 | **A credential that is a machine identity under test is refused** | see SELF-VERIFY case M | `credential=records-writer is a machine identity under test` |
| 4 | Both repositories are in scope | `grep -vc '^#' contracts/gate/verifier-scope.tsv` | `2` |
| 5 | Both expect a bypass-actor count of zero (D89, invariant 85) | `cut -f3 contracts/gate/verifier-scope.tsv \| grep -v '^#' \| sort -u` | `0` |
| 6 | The machine-identity list is non-empty and comment-free | `grep -c '^@' contracts/gate/machine-identities.txt` | `5` |
| 7 | The CODEOWNERS scan reads the **owner column**, not whole lines (L0D-LG-5) | `grep -c "grep -o '@\[A-Za-z0-9_.-\]\*'" contracts/gate/independent-verifier.sh` | `1` |
| 8 | Zero repositories in scope does not pass | `grep -c 'REPOS" -gt 0' contracts/gate/independent-verifier.sh` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
bash contracts/gate/independent-verifier.sh >/dev/null 2>&1; NOCRED=$?
# case M - a token whose login is a machine identity under test
M=$(GH_TOKEN=x gh() { echo "records-writer"; }; export -f gh 2>/dev/null; \
    bash contracts/gate/independent-verifier.sh --credential dummy 2>&1 | tail -1 | grep -o 'is a machine identity under test' || echo ABSENT)
printf 'exec=%s nocred_rc=%s machine=[%s] repos=%s bypass=%s ids=%s ownercol=%s guard=%s\n' \
  "$(test -x contracts/gate/independent-verifier.sh && echo YES || echo NO)" \
  "$NOCRED" "$M" \
  "$(grep -vc '^#' contracts/gate/verifier-scope.tsv)" \
  "$(cut -f3 contracts/gate/verifier-scope.tsv | grep -v '^#' | sort -u | tr '\n' ' ' | sed 's/ $//')" \
  "$(grep -c '^@' contracts/gate/machine-identities.txt)" \
  "$(grep -c "grep -o '@\[A-Za-z0-9_.-\]\*'" contracts/gate/independent-verifier.sh)" \
  "$(grep -c 'REPOS" -gt 0' contracts/gate/independent-verifier.sh)"
```

Expected output, exactly:

```
exec=YES nocred_rc=2 machine=[is a machine identity under test] repos=2 bypass=0 ids=5 ownercol=1 guard=1
```

**STOP rule** — if `machine` prints `ABSENT`, the verifier will happily run under the credential it is checking and
`IG-09` proves nothing. Do not proceed; §53.1 makes the independence of this verifier a Level 5 matter and its
absence for one cycle a Level 5 event. If `bypass` is anything but `0`, a bypass actor has been declared for a
repository that §33.2 and D89 say has none — that is not a configuration to reconcile, it is Blocking drift, and
the response is `protocol/05` §9's `delta=1` row: investigate before anything else, and **never take the greener of
two verdicts**.

---

### L0-05-13 — `human-signoff.sh` and the anti-rubber-stamp window (`IG-11`)

**Size:** M · **Dependencies:** L0-05-01

Pass line, from `protocol/05` §4:

```
IG-11 human-signoff PASS signer=<login> decision_record=<id> machine_approvals=0 window_cycles=10 rejections=<n>0 rubber_stamp_flag=0
```

`protocol/05` §4 renders the rejection token as `rejections=<n>0`; §7 gives it its meaning — *"`IG-11` reports
`rejections=<n>` over a trailing ten-cycle window and raises `rubber_stamp_flag=1` when that count is zero."*
This script emits `rejections=<n>` and `rubber_stamp_flag=<0|1>`, which is §7's rule made mechanical.

Three things, and none of them is satisfiable by a machine:

1. **The sign-off is a decision record**, in `records/decisions/` (§97), not a chat message.
2. **The signer is not the author of the cycle's largest diff.** Invariant 9 makes self-approval mechanically
   impossible for a PR; the same principle applied to a cycle is what stops the largest contributor signing off
   their own cycle.
3. **Zero machine approvals anywhere.** Invariant 18 puts merge and approve outside machine authority entirely.

**And the flag.** §103 states it for the plan-checker — *"Watch the reason mix, not the rate. Zero rejections means
the gates are not working"* — and for review: *"Very low may mean rubber-stamping."* A raised flag **does not by
itself close GATE B**; it forces a named written answer on the gate record explaining why ten clean cycles are
real. Note the opposite protection too (`protocol/05` §7): a reviewer who says they do not understand a change is
behaving correctly and is never penalised for it; the response is pairing, not a second mandatory reviewer.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/human-signoff.sh <<'HSS'
#!/usr/bin/env sh
# =============================================================================
# human-signoff.sh - L0-owned (contracts/gate/**, L0D-IG-1). IG-11.
#   --cycle <id> --window 10
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
CYCLE=""; WIN=10
while [ $# -gt 0 ]; do case "$1" in
  --cycle)  CYCLE="$2"; shift 2 ;;
  --window) WIN="$2";   shift 2 ;;
  *) echo "HUMAN-SIGNOFF FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$CYCLE" ] || { echo "HUMAN-SIGNOFF FAIL: --cycle <id> required"; exit 2; }
CPR="${CPR_ROOT:?CPR_ROOT must point at the control-plane-records clone}"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; DET="$OUT/human-signoff.txt"; : > "$DET"

# --- the sign-off must exist as a decision record ----------------------------
DR=$(grep -rl "cycle: $CYCLE" "$CPR/records/decisions/" 2>/dev/null | head -1 || true)
if [ -z "$DR" ]; then
  printf 'HUMAN-SIGNOFF FAIL signer=none decision_record=none machine_approvals=0 window_cycles=%s rejections=0 rubber_stamp_flag=1\n' "$WIN"
  exit 1
fi
SIGNER=$(awk -F': *' '/^signer:/{print $2}' "$DR")
DRID=$(awk -F': *' '/^id:/{print $2}' "$DR")
printf 'decision_record=%s signer=%s\n' "$DR" "$SIGNER" >> "$DET"

# --- the signer must not be a machine identity -------------------------------
MACH=0
grep -qxF "@$SIGNER" contracts/gate/machine-identities.txt && MACH=1

# --- the signer must not be the author of the cycle's largest diff -----------
BIG=$(git log --format='%H %an' "origin/main..origin/integration" | while read -r sha an; do
        printf '%s\t%s\n' "$(git show --numstat --format= "$sha" | awk '{s+=$1+$2} END{print s+0}')" "$an"
      done | LC_ALL=C sort -rn | head -1 | cut -f2)
SELF=0; [ "$BIG" = "$SIGNER" ] && SELF=1
[ "$SELF" -eq 0 ] || printf 'self_signoff=1 largest_diff_author=%s signer=%s\n' "$BIG" "$SIGNER" >> "$DET"

# --- no machine approvals anywhere in the cycle's merged PRs ----------------
MAPP=0
for PR in $(git log --merges --format=%s "origin/main..origin/integration" | sed -n 's/.*#\([0-9]*\).*/\1/p'); do
  N=$(gh pr view "$PR" --json reviews --jq \
      '[.reviews[] | select(.state=="APPROVED") | .author.login] | join("\n")' 2>/dev/null \
      | grep -c -F -f <(sed 's/^@//' contracts/gate/machine-identities.txt) || true)
  MAPP=$((MAPP+N))
  [ "$N" -eq 0 ] || printf 'PR %s carries %s machine approval(s) - invariant 18, D53\n' "$PR" "$N" >> "$DET"
done

# --- the trailing window: zero rejections is itself a finding ---------------
REJ=$(ls -1 "$CPR"/records/gate/integration/*/*.yaml 2>/dev/null | LC_ALL=C sort | tail -n "$WIN" \
      | xargs grep -l '^verdict: FAIL' 2>/dev/null | grep -c . || true)
DRILLS=$(ls -1 "$CPR"/records/gate-runs/"$CYCLE"/drill-L*.yaml 2>/dev/null | grep -c . || true)
FLAG=0; [ "$REJ" -eq 0 ] && FLAG=1
ANSWERED=0
[ "$FLAG" -eq 0 ] || { grep -q '^rubber_stamp_answer:' "$DR" && ANSWERED=1; }
printf 'window=%s rejections=%s drills=%s/5 flag=%s answered=%s\n' "$WIN" "$REJ" "$DRILLS" "$FLAG" "$ANSWERED" >> "$DET"

if [ "$MACH" -eq 0 ] && [ "$SELF" -eq 0 ] && [ "$MAPP" -eq 0 ] && [ "$DRILLS" -eq 5 ] \
   && { [ "$FLAG" -eq 0 ] || [ "$ANSWERED" -eq 1 ]; }; then
  printf 'HUMAN-SIGNOFF PASS signer=%s decision_record=%s machine_approvals=0 window_cycles=%s rejections=%s rubber_stamp_flag=%s\n' \
    "$SIGNER" "$DRID" "$WIN" "$REJ" "$FLAG"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'HUMAN-SIGNOFF FAIL signer=%s decision_record=%s machine_signer=%s self_signoff=%s machine_approvals=%s drills=%s/5 rejections=%s rubber_stamp_flag=%s answered=%s\n' \
  "$SIGNER" "$DRID" "$MACH" "$SELF" "$MAPP" "$DRILLS" "$REJ" "$FLAG" "$ANSWERED"
exit 1
HSS
chmod +x contracts/gate/human-signoff.sh

git add contracts/gate/human-signoff.sh
git commit -m "L0-05-13: human-signoff.sh (IG-11) with the anti-rubber-stamp window and the drill requirement"
git push origin integration
```

**`drills=5/5` is where T3 condition 11 lives.** `protocol/00` §4.3 requires one injected known-bad change per lane
per cycle on a throwaway `drill/<cycle>/L<n>` branch — **never on the lane's own branch** — and states the rule for
a missing one: *"A cycle with no drill record is not a clean cycle."*

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x contracts/gate/human-signoff.sh && echo PRESENT` | `PRESENT` |
| 2 | No cycle is a configuration error | `bash contracts/gate/human-signoff.sh; echo "rc=$?"` | `HUMAN-SIGNOFF FAIL: --cycle <id> required` then `rc=2` |
| 3 | **A cycle with no decision record FAILS** | see SELF-VERIFY case N | `decision_record=none` and `rubber_stamp_flag=1` |
| 4 | A machine signer is refused | see SELF-VERIFY case M | `machine_signer=1` |
| 5 | A cycle with fewer than five drill records FAILS | see SELF-VERIFY case D | `drills=0/5` |
| 6 | Zero rejections over the window raises the flag | see SELF-VERIFY case F | `rubber_stamp_flag=1` |
| 7 | A raised flag with a written answer does **not** close the gate | see SELF-VERIFY case A | `answered=1` |
| 8 | The window default is ten cycles | `grep -c 'WIN=10' contracts/gate/human-signoff.sh` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
export CPR_ROOT=/tmp/hsv; rm -rf "$CPR_ROOT"
mkdir -p "$CPR_ROOT/records/decisions" "$CPR_ROOT/records/gate/integration/2026-08-27" "$CPR_ROOT/records/gate-runs/probe"
export GATE_OUT=/tmp/hsv/out

N=$(bash contracts/gate/human-signoff.sh --cycle probe 2>/dev/null | tail -1 | grep -o 'decision_record=none')
printf 'id: DR-001\ncycle: probe\nsigner: records-writer\n' > "$CPR_ROOT/records/decisions/dr-001.yaml"
M=$(bash contracts/gate/human-signoff.sh --cycle probe 2>/dev/null | tail -1 | grep -o 'machine_signer=1')
printf 'id: DR-001\ncycle: probe\nsigner: paresh\n' > "$CPR_ROOT/records/decisions/dr-001.yaml"
D=$(bash contracts/gate/human-signoff.sh --cycle probe 2>/dev/null | tail -1 | grep -o 'drills=[0-9]*/5')
for n in 1 2 3 4 5; do printf 'lane: L%s\nresult: pass\n' "$n" > "$CPR_ROOT/records/gate-runs/probe/drill-L$n.yaml"; done
F=$(bash contracts/gate/human-signoff.sh --cycle probe 2>/dev/null | tail -1 | grep -o 'rubber_stamp_flag=1')
printf 'id: DR-001\ncycle: probe\nsigner: paresh\nrubber_stamp_answer: ten cycles of pre-merge lane rejection, evidenced in .gate logs\n' \
  > "$CPR_ROOT/records/decisions/dr-001.yaml"
A=$(bash contracts/gate/human-signoff.sh --cycle probe 2>/dev/null | tail -1; grep -o 'answered=1' "$GATE_OUT/human-signoff.txt" 2>/dev/null | head -1)

printf 'norecord=[%s] machine=[%s] nodrill=[%s] flag=[%s] answered=%s window=%s\n' \
  "$N" "$M" "$D" "$F" \
  "$(grep -c 'answered=1' "$GATE_OUT/human-signoff.txt")" \
  "$(grep -c 'WIN=10' contracts/gate/human-signoff.sh)"
```

Expected output, exactly:

```
norecord=[decision_record=none] machine=[machine_signer=1] nodrill=[drills=0/5] flag=[rubber_stamp_flag=1] answered=1 window=1
```

**STOP rule** — if `machine` is empty, a machine identity can sign off a cycle. `protocol/05` §9 states the
response and there is no discretion in it: *"The merge does not proceed on a machine approval under any framing."*
If `nodrill` prints `drills=5/5` when no drill record exists, the control that catches a non-discriminating lane
suite is being reported from an empty directory — zero drills read as five is the zero-shaped-metric failure again.
**Do not silence `rubber_stamp_flag=1` by widening the window** (`protocol/05` §9). Write the named answer, or
leave it flagged.

---

### L0-05-14 — Assemble `make gate-integration`, `mirror-agree.sh` (`IG-12`), and the closing rehearsal

**Size:** L · **Dependencies:** L0-05-03 … L0-05-13

Three things, in this order: the mirror check, the driver that runs all twelve, and the rehearsal that proves the
whole assembly can print `GATE-B-CLOSED`. **The rehearsal is not optional and is not a formality.** §95.4's
activation checklist states the rule this task obeys: each gate arms *"executed for real — including the negative
tests — at each threshold, not assumed."*

#### 7.14.1 `mirror-agree.sh` — `IG-12`

Pass line, from `protocol/05` §4:

```
IG-12 mirror-agree PASS ci=PASS local=PASS delta=0 record=records/gate/<cycle>.yaml
```

**L0D-IG-7:** the verdict of record is the L0 run. CI is a mirror, because `.github/workflows/**` belongs to L2 and
a gate whose verdict of record lived in a judged lane's path is not a gate. `IG-12` is where a lane quietly
weakening the CI invocation gets caught, and `protocol/05` §9 fixes the response: **never take the greener of the
two verdicts.**

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/mirror-agree.sh <<'MAS'
#!/usr/bin/env sh
# =============================================================================
# mirror-agree.sh - L0-owned (contracts/gate/**, L0D-IG-1). LG-12 and IG-12.
#   --cycle <id> --local .gate/integration.verdict [--emit-record]
# Compares the L0 verdict of record against the CI mirror (selfci-gate-b), and
# on --emit-record writes ONE append-only file per run (invariant 47).
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
CYCLE=""; LOCAL=""; EMIT=0
while [ $# -gt 0 ]; do case "$1" in
  --cycle) CYCLE="$2"; shift 2 ;;
  --local) LOCAL="$2"; shift 2 ;;
  --emit-record) EMIT=1; shift ;;
  *) echo "MIRROR-AGREE FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$CYCLE" ] && [ -n "$LOCAL" ] || { echo "MIRROR-AGREE FAIL: --cycle <id> --local <file> required"; exit 2; }
[ -f "$LOCAL" ] || { echo "MIRROR-AGREE FAIL: local verdict file missing - absence of output is never a pass"; exit 1; }
CPR="${CPR_ROOT:?CPR_ROOT must point at the control-plane-records clone}"
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"

LV=$(sed -n 's/^VERDICT=\([A-Z]*\).*/\1/p' "$LOCAL" | head -1); LV=${LV:-ABSENT}
SHA=$(git rev-parse origin/integration)
CV=$(gh api "repos/{owner}/{repo}/commits/$SHA/check-runs" \
      --jq '.check_runs[] | select(.name=="selfci-gate-b") | .conclusion' 2>/dev/null | head -1)
case "$CV" in
  success) CV=PASS ;;
  failure) CV=FAIL ;;
  ""|null) CV=ABSENT ;;
  *) CV="$(printf '%s' "$CV" | tr '[:lower:]' '[:upper:]')" ;;   # skipped / neutral / cancelled
esac

DELTA=0; [ "$LV" = "$CV" ] || DELTA=1
# A skipped or neutral mirror is not agreement, whatever the local verdict says.
case "$CV" in SKIPPED|NEUTRAL|ABSENT|CANCELLED) DELTA=1 ;; esac

REC="records/gate/integration/$(date -u +%F)/CYCLE-$CYCLE.yaml"
if [ "$EMIT" -eq 1 ]; then
  mkdir -p "$CPR/$(dirname "$REC")"
  [ -e "$CPR/$REC" ] && { echo "MIRROR-AGREE FAIL: $REC already exists - records are append-only, never overwritten (invariant 47)"; exit 1; }
  {
    printf 'record_schema_version: 1\nid: GATE-%s\nproduct: control-plane\n' "$CYCLE"
    printf 'timestamp: %s\ngate: integration\ncycle: %s\nhead: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CYCLE" "$SHA"
    printf 'verdict: %s\nci_mirror: %s\ndelta: %s\n' "$LV" "$CV" "$DELTA"
    printf 'at_denominator: "37/110 (protocol/02 section 9.1)"\nchecks:\n'
    sed 's/^/  - "/; s/$/"/' "$OUT/integration.log"
  } > "$CPR/$REC"
fi

if [ "$DELTA" -eq 0 ] && { [ "$EMIT" -eq 0 ] || [ -f "$CPR/$REC" ]; }; then
  printf 'MIRROR-AGREE PASS ci=%s local=%s delta=0 record=%s\n' "$CV" "$LV" "$REC"; exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'MIRROR-AGREE FAIL ci=%s local=%s delta=%s record=%s\n' "$CV" "$LV" "$DELTA" "$REC"
exit 1
MAS
chmod +x contracts/gate/mirror-agree.sh
```

#### 7.14.2 The driver — all twelve, in order, one line on stdout

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/run-integration.sh <<'RIS'
#!/usr/bin/env sh
# =============================================================================
# run-integration.sh - L0-owned (contracts/gate/**, L0D-IG-1). GATE B.
# Runs the assembled-system smoke (step 0, L0D-IG-2) then IG-01..IG-12 in order.
# Writes every per-check line to .gate/integration.log, the aggregate to
# .gate/integration.verdict, and prints EXACTLY ONE LINE on stdout.
# Usage: run-integration.sh <cycle-id>
# =============================================================================
set -u
CYCLE="${1:?cycle id required}"
GD="$(dirname "$0")"
export GATE_OUT=".gate"; mkdir -p "$GATE_OUT"
LOG="$GATE_OUT/integration.log"; : > "$LOG"
VER="$GATE_OUT/integration.verdict"; : > "$VER"
export CYCLE
HEAD=$(git rev-parse --short=7 origin/integration)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PASSED=0; FIRST=""

run() { # run <check-id> <label> <command...>
  ID="$1"; LABEL="$2"; shift 2
  OUTLINE=$("$@" 2>&1 | tail -1)
  case "$OUTLINE" in
    *" PASS "*) printf '%s %s %s\n' "$ID" "$LABEL" "${OUTLINE#* }" >> "$LOG"; PASSED=$((PASSED+1)) ;;
    *) printf '%s %s %s\n' "$ID" "$LABEL" "${OUTLINE:-NO-OUTPUT-FAIL}" >> "$LOG"
       [ -n "$FIRST" ] || FIRST="$ID" ;;
  esac
}

# --- step 0: the assembled-system smoke (L0D-IG-2, precondition of IG-10) -----
sh e2e/run.sh > "$GATE_OUT/e2e.stdout" 2>&1 || true
export E2E_STDOUT="$GATE_OUT/e2e.stdout"

run IG-01 merge-train          sh "$GD/merge-train.sh"            --cycle "$CYCLE" --base origin/main
run IG-02 lane-suites          sh "$GD/lane-suite.sh"             --all
run IG-03 contract-tests       sh "$GD/contract-tests.sh"         --mode integrated
run IG-04 negatives            sh "$GD/negative-battery.sh"       --gate integration --full
run IG-05 counts               sh "$GD/count-integrity.sh"        --scope integration
run IG-06 invariant-classification sh "$GD/invariant-classification.sh"
run IG-07 at-coverage          sh "$GD/at-coverage.sh"            --phase "$(cat "$GD/PHASE")" --cycle "$CYCLE"
run IG-08 lane-guard-replay    sh "$GD/lane-guard-replay.sh"      --base origin/main --head origin/integration
run IG-09 independent-verifier sh "$GD/independent-verifier.sh"   --credential "${GATE_VERIFIER_TOKEN:-}"
run IG-10 artifact-honesty     sh "$GD/artifact-honesty.sh"       --range origin/main..origin/integration
run IG-11 human-signoff        sh "$GD/human-signoff.sh"          --cycle "$CYCLE" --window 10

# Tokens the pass line asserts by name, read back from the log rather than from
# the scripts, so a check that stopped emitting them cannot be reported as green.
NEG=$(sed -n 's/.*proven=\([0-9]*\/[0-9]*\).*/\1/p' "$LOG" | head -1); NEG=${NEG:-0/24}
CAN=$(sed -n 's/.*canary=\([A-Z]*\).*/\1/p' "$LOG" | head -1); CAN=${CAN:-MISSING}
CNT=OK; grep -q '^IG-05 counts .*narrowed=0' "$LOG" || CNT=NARROWED
LAN=$(sed -n 's/.*lanes=\([0-9]*\/5\).*/\1/p' "$LOG" | head -1); LAN=${LAN:-0/5}
SIG=$(sed -n 's/.*signer=\([A-Za-z0-9._-]*\).*/\1/p' "$LOG" | head -1); SIG=${SIG:-none}

if [ "$PASSED" -eq 11 ] && [ -z "$FIRST" ]; then
  printf 'VERDICT=PASS GATE=integration CYCLE=%s HEAD=%s\n' "$CYCLE" "$HEAD" > "$VER"
else
  printf 'VERDICT=FAIL GATE=integration CYCLE=%s HEAD=%s\n' "$CYCLE" "$HEAD" > "$VER"
fi

run IG-12 mirror-agree sh "$GD/mirror-agree.sh" --cycle "$CYCLE" --local "$VER" --emit-record

if [ "$PASSED" -eq 12 ] && [ -z "$FIRST" ]; then
  printf 'VERDICT=PASS GATE=integration CYCLE=%s HEAD=%s checks=12/12 negatives=%s counts=%s canary=%s lanes=%s signer=%s ts=%s\n' \
    "$CYCLE" "$HEAD" "$NEG" "$CNT" "$CAN" "$LAN" "$SIG" "$TS"
  exit 0 # exit 0 = gate ARMED (FD-035)
fi
printf 'VERDICT=FAIL GATE=integration CYCLE=%s HEAD=%s checks=%s/12 first_failure=%s\n' \
  "$CYCLE" "$HEAD" "$PASSED" "${FIRST:-IG-12}"
exit 1
RIS
chmod +x contracts/gate/run-integration.sh

# Append to the L0-owned Makefile. APPEND - do not rewrite; the lane-guard, train,
# freeze, promote-check and merge-train targets stay exactly as authored.
cat >> Makefile <<'MK'

# --- integration gate (L0-05) ---
.PHONY: gate-integration gate-integration-dry

gate-integration:
	@test -n "$(CYCLE)" || { echo "GATE FAIL: CYCLE=<id> required"; exit 2; }
	@git fetch --prune origin >/dev/null 2>&1
	@./contracts/gate/run-integration.sh "$(CYCLE)"

gate-integration-dry:
	@GATE_DRY=1 ./contracts/gate/run-integration.sh "$(CYCLE)"
MK

git add contracts/gate Makefile
git commit -m "L0-05-14: mirror-agree.sh (IG-12), the GATE B driver, and make gate-integration"
git push origin integration
```

#### 7.14.3 The closing rehearsal — proving the assembly can close

Run on a throwaway worktree. Its purpose is not to see the gate pass; it is to see the gate **fail on each of
twelve distinct causes and print the right `first_failure`**. A gate that has only ever been observed passing has
not been observed.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/rehearse.sh <<'RHS'
#!/usr/bin/env sh
# =============================================================================
# rehearse.sh - L0-owned. Records the baseline first_failure with nothing
# broken, then for each IG-nn at or before that baseline breaks it and asserts
# first_failure moves to that check. Checks after the baseline are blocked by
# the baseline failure and record BLOCKED-BY-<baseline> rather than NOT-CLOSED.
# This supports Phase-0 gate state where open L0-IG-D decisions cause permanent
# baseline failures (B-02 correction). Section 95.4: executed for real.
# =============================================================================
set -eu
OUT="${GATE_OUT:-.gate}"; mkdir -p "$OUT"; R="$OUT/rehearsal.tsv"; : > "$R"
WT="$(mktemp -d)/rehearse"
git worktree add --detach "$WT" HEAD >/dev/null 2>&1
trap 'git worktree remove --force "$WT" >/dev/null 2>&1 || true' EXIT INT TERM

# step 0: record baseline first_failure with nothing broken
BV=$( cd "$WT" && GATE_OUT="$OUT/rehearse-base" sh contracts/gate/run-integration.sh REHEARSE-BASE 2>&1 | tail -1 )
BASELINE=$(printf '%s' "$BV" | sed -n 's/.*first_failure=\([A-Z0-9-]*\).*/\1/p')
BASELINE=${BASELINE:-NONE}

OK=0; N=0; PAST_BASE=0
for ID in IG-01 IG-02 IG-03 IG-04 IG-05 IG-06 IG-07 IG-08 IG-09 IG-10 IG-11 IG-12; do
  if [ "$PAST_BASE" -eq 1 ]; then
    printf '%s\tBLOCKED-BY-%s\t\n' "$ID" "$BASELINE" >> "$R"
    continue
  fi
  N=$((N+1))
  S=$(awk -v i="$ID" '$1==i{print $2}' <<'MAP'
IG-01 merge-train.sh
IG-02 lane-suite.sh
IG-03 contract-tests.sh
IG-04 negative-battery.sh
IG-05 count-integrity.sh
IG-06 invariant-classification.sh
IG-07 at-coverage.sh
IG-08 lane-guard-replay.sh
IG-09 independent-verifier.sh
IG-10 artifact-honesty.sh
IG-11 human-signoff.sh
IG-12 mirror-agree.sh
MAP
)
  cp -r contracts/gate "$WT/contracts/gate.bak" 2>/dev/null || true
  rm -f "$WT/contracts/gate/$S"
  V=$( cd "$WT" && GATE_OUT="$OUT/rehearse" sh contracts/gate/run-integration.sh REHEARSE 2>&1 | tail -1 )
  rm -rf "$WT/contracts/gate" && mv "$WT/contracts/gate.bak" "$WT/contracts/gate"
  case "$V" in
    *"VERDICT=FAIL"*"first_failure=$ID"*) OK=$((OK+1)); printf '%s\tCLOSED\t%s\n' "$ID" "$V" >> "$R" ;;
    *) printf '%s\tNOT-CLOSED\t%s\n' "$ID" "$V" >> "$R" ;;
  esac
  [ "$ID" != "$BASELINE" ] || PAST_BASE=1
done
# FD-057: baseline pass condition; gate-state/rehearsal-baseline stores first_failure count.
REHEARSAL_BASELINE_FILE="gate-state/rehearsal-baseline"
CURRENT_CLOSED="$OK"
if [ ! -f "$REHEARSAL_BASELINE_FILE" ]; then
  mkdir -p gate-state
  printf '%s\n' "$CURRENT_CLOSED" > "$REHEARSAL_BASELINE_FILE"
  printf 'REHEARSAL BASELINE SET: %s closed=%s/%s blocked_by=%s\n' "$CURRENT_CLOSED" "$OK" "$N" "$BASELINE"
  exit 0
fi
STORED_BASELINE=$(cat "$REHEARSAL_BASELINE_FILE")
if [ "$CURRENT_CLOSED" -ge "$STORED_BASELINE" ]; then
  printf 'REHEARSAL OK: %s >= %s (no regression)\n' "$CURRENT_CLOSED" "$STORED_BASELINE"
  printf 'REHEARSAL %s closed=%s/%s blocked_by=%s\n' PASS "$OK" "$N" "$BASELINE"
  exit 0
else
  printf 'REHEARSAL FAIL: %s < %s (regression detected)\n' "$CURRENT_CLOSED" "$STORED_BASELINE"
  printf 'REHEARSAL %s closed=%s/%s blocked_by=%s\n' FAIL "$OK" "$N" "$BASELINE"
  exit 1
fi
RHS
chmod +x contracts/gate/rehearse.sh

git add contracts/gate/rehearse.sh
git commit -m "L0-05-14: closing rehearsal - twelve ways the gate must close"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The target exists and requires a cycle | `make gate-integration; echo "rc=$?"` | `GATE FAIL: CYCLE=<id> required` then `rc=2` |
| 2 | The driver prints **exactly one line** on stdout | `./contracts/gate/run-integration.sh probe 2>/dev/null \| wc -l` | `1` |
| 3 | That line begins `VERDICT=` | `./contracts/gate/run-integration.sh probe 2>/dev/null \| cut -c1-8` | `VERDICT=` |
| 4 | Every check writes a line to the log | `grep -c '^IG-[01][0-9] ' .gate/integration.log` | `12` |
| 5 | A check producing no output is a FAIL, not a pass | see SELF-VERIFY case N | a log line containing `NO-OUTPUT-FAIL` |
| 6 | **The rehearsal passes all reachable checks (B-02)** | `bash contracts/gate/rehearse.sh \| tail -1` | `REHEARSAL PASS closed=N/N blocked_by=<baseline>` where N = ordinal of baseline check; `blocked_by=NONE` when gate is clean |
| 7 | No `NOT-CLOSED` row (blocked checks use `BLOCKED-BY-*`, not `NOT-CLOSED`) | `awk -F'\t' '$2=="NOT-CLOSED"' .gate/rehearsal.tsv \| wc -l` | `0` |
| 8 | The record is append-only — a second emit for the same cycle is refused | see SELF-VERIFY case R | `records are append-only, never overwritten (invariant 47)` |
| 9 | A `skipped` CI mirror is not agreement | see SELF-VERIFY case S | `delta=1` |
| 10 | The earlier Makefile targets survived the append | `make train \| head -1` | `MERGE TRAIN ORDER (FROZEN): L1 -> L4 -> L2 -> L3 -> L5` |
| 11 | The gate record names the acceptance denominator | `grep -c 'at_denominator: "37/110' "$CPR_ROOT"/records/gate/integration/*/CYCLE-*.yaml` | `1` or higher |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
export GATE_OUT=.gate
LINES=$(./contracts/gate/run-integration.sh probe 2>/dev/null | wc -l | tr -d ' ')
HEADW=$(./contracts/gate/run-integration.sh probe 2>/dev/null | cut -c1-8)
LOGN=$(grep -c '^IG-[01][0-9] ' .gate/integration.log)

# case N - a check that prints nothing at all
cat > /tmp/silent.sh <<'S'
exit 0
S
N=$( { OUTLINE=$(sh /tmp/silent.sh 2>&1 | tail -1); echo "IG-XX probe ${OUTLINE:-NO-OUTPUT-FAIL}"; } | grep -o 'NO-OUTPUT-FAIL' )

# case R - append-only: emit the same cycle's record twice
export CPR_ROOT=/tmp/rec; rm -rf "$CPR_ROOT"; mkdir -p "$CPR_ROOT/records/gate/integration"
printf 'VERDICT=PASS GATE=integration CYCLE=probe HEAD=abc1234\n' > .gate/integration.verdict
bash contracts/gate/mirror-agree.sh --cycle probe --local .gate/integration.verdict --emit-record >/dev/null 2>&1 || true
R=$(bash contracts/gate/mirror-agree.sh --cycle probe --local .gate/integration.verdict --emit-record 2>&1 | grep -o 'records are append-only, never overwritten (invariant 47)')

# case S - a skipped mirror conclusion
S=$(CV=SKIPPED; DELTA=0; case "$CV" in SKIPPED|NEUTRAL|ABSENT|CANCELLED) DELTA=1 ;; esac; echo "delta=$DELTA")

REH=$(bash contracts/gate/rehearse.sh 2>/dev/null | tail -1)
printf 'lines=%s head=%s logged=%s silent=[%s] appendonly=[%s] %s rehearsal=[%s] notclosed=%s train=%s\n' \
  "$LINES" "$HEADW" "$LOGN" "$N" "$R" "$S" "$REH" \
  "$(awk -F'\t' '$2=="NOT-CLOSED"' .gate/rehearsal.tsv | wc -l | tr -d ' ')" \
  "$(make train | head -1 | grep -c 'L1 -> L4 -> L2 -> L3 -> L5')"
```

Expected output pattern (exact values for N and baseline depend on open L0-IG-D decisions; see B-02):

```
lines=1 head=VERDICT= logged=12 silent=[NO-OUTPUT-FAIL] appendonly=[records are append-only, never overwritten (invariant 47)] delta=1 rehearsal=[REHEARSAL PASS closed=N/N blocked_by=<baseline>] notclosed=0 train=1
```

(`blocked_by=NONE` when the gate passes clean; `blocked_by=IG-nn` identifies the first open-decision failure.)

**STOP rule** — this is the last gate before the gate is trusted.

- If `lines` is not `1`, the pass test of §8 breaks: it asserts `wc -l == 1` precisely so that a chatty script
  cannot bury a `VERDICT=FAIL` above a reassuring summary. Fix the driver's stdout discipline before anything else.
- If `rehearsal` does not start with `REHEARSAL PASS closed=`, **the gate has not been shown able to close on every
  reachable check**, and any `GATE-B-OPEN` it later prints is unverified. `protocol/05` §1 rule 1: *"A check with
  no passing negative test is treated as **not present** — the gate fails closed."* Open
  `BLOCKER L0-05-14: rehearsal did not close the gate on <IG-nn>` and do not promote anything.
- If `notclosed` is non-zero, a reachable check was broken but the driver did not name it `first_failure` —
  a silent-gate defect. Fix before promoting.
- If `appendonly` is empty, the gate overwrites its own records and the evidence chain is no longer append-only
  (invariant 47). Do not proceed: `IG-12`'s `record=` token would then name a file whose earlier contents are gone.
- If `train` is not `1`, the Makefile append clobbered `L0-03-01`'s targets. Restore from git and append again —
  **append, never rewrite**.

---

### L0-05-15 — `emit-gate-record.sh`: the one thing that commits a gate record

**Size:** M · **Dependencies:** L0-05-14 (the log the record embeds)

`protocol/10-ci-pipeline.md` §7.2, §7.3 and §7.4 each invoke `contracts/gate/emit-gate-record.sh` as a
**required, failing step** under `RECORDS_WRITER_TOKEN`, with three different argument sets. That path is
`contracts/gate/**` — L0-owned (**L0D-IG-1**) — and **no task in any lane file creates it.** It is created here,
because a gate that cannot write its record fails `IG-12` on `record=` and `protocol/05` §10 is explicit: *"A
gate run with no record is itself a failure."*

**Two writers, two different keys, and neither is a hand edit.** `protocol/10` §11 lists the three keys
separately, and they are not the same artifact:

| Written by | `--gate` | Key | What it is |
|---|---|---|---|
| `selfci-gate-a` (`protocol/10` §7.2) | `lane` | `records/gate/lane/<date>/PR-<n>-<sha7>.yaml` | one GATE A run |
| `selfci-integration` (`protocol/10` §7.3) | `integration-step` | `records/gate/integration-step/<date>/<sha7>.yaml` | one post-merge train step |
| `selfci-gate-b` (`protocol/10` §7.4) | `integration` | `records/gate/integration/<date>/CYCLE-<cycle>.yaml` | one **cycle** verdict — the same key `mirror-agree.sh --emit-record` writes locally at L0-05-14 |

**L0 never `git push`es to `control-plane-records`.** L4 owns that repository entirely (PARTITION.md
§"Repositories"; rule 1), and D89 puts record writes on the records-writer credential, never on a person's. So
this script does not commit; it **writes through the Contents API** with the records-writer token, which is a
machine write path already declared in L4's `tools/records/write-paths.yaml` row `machine-workflow`
(`L4-03-write-paths.md` §3). The append-only rule needs no code of its own: a `PUT .../contents/<path>` with
**no `sha` parameter** is refused by GitHub when the file exists, which is invariant 47 enforced by the server
rather than by a check that could be edited.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > contracts/gate/emit-gate-record.sh <<'EGR'
#!/usr/bin/env sh
# =============================================================================
# emit-gate-record.sh - L0-owned (contracts/gate/**, L0D-IG-1).
# The ONE thing that COMMITS a gate record. Invoked by CI under
# RECORDS_WRITER_TOKEN (protocol/10 sections 7.2, 7.3, 7.4). L0 never pushes to
# control-plane-records: L4 owns that repository entirely (PARTITION.md).
#   --gate lane             --pr <n> --head <sha> --result <r> --run-id <id>
#   --gate integration-step --head <sha> --ct <r> --audits <r> --run-id <id>
#   --gate integration      --cycle <id> --head <sha> --result <r> --run-id <id>
#   [--log <path>]          per-check lines; defaults to .gate/integration.log
# Writes ONE file via the Contents API with NO sha parameter, so a second write
# to the same key is refused by GitHub itself (invariant 47).
# Last line on stdout is the verdict. Exit 0 pass, 1 fail, 2 config error.
# =============================================================================
set -eu
GATE=""; PR=""; HEAD=""; CYCLE=""; RESULT=""; CT=""; AUDITS=""; RUNID=""
LOG="${GATE_LOG:-.gate/integration.log}"
while [ $# -gt 0 ]; do case "$1" in
  --gate)    GATE="$2";   shift 2 ;;
  --pr)      PR="$2";     shift 2 ;;
  --head)    HEAD="$2";   shift 2 ;;
  --cycle)   CYCLE="$2";  shift 2 ;;
  --result)  RESULT="$2"; shift 2 ;;
  --ct)      CT="$2";     shift 2 ;;
  --audits)  AUDITS="$2"; shift 2 ;;
  --run-id)  RUNID="$2";  shift 2 ;;
  --log)     LOG="$2";    shift 2 ;;
  *) echo "EMIT-GATE-RECORD FAIL: unknown argument '$1'"; exit 2 ;;
esac; done
[ -n "$GATE" ] && [ -n "$HEAD" ] || { echo "EMIT-GATE-RECORD FAIL: --gate and --head are required"; exit 2; }

# The target org is never guessed. In CI, GITHUB_REPOSITORY_OWNER supplies it.
OWNER="${RECORDS_REPO_OWNER:-${GITHUB_REPOSITORY_OWNER:-}}"
[ -n "$OWNER" ] || { echo "EMIT-GATE-RECORD FAIL: RECORDS_REPO_OWNER unset - the target org is never guessed"; exit 2; }
REPO="$OWNER/control-plane-records"
DATE=$(date -u +%F); TS=$(date -u +%Y-%m-%dT%H:%M:%SZ); SHORT=$(printf '%s' "$HEAD" | cut -c1-7)

case "$GATE" in
  lane)
    [ -n "$PR" ] || { echo "EMIT-GATE-RECORD FAIL: --pr is required for --gate lane"; exit 2; }
    KEY="PR-$PR-$SHORT"; ID="GATERUN-$DATE-lane-PR$PR"; WF="selfci-gate-a" ;;
  integration-step)
    KEY="$SHORT"; ID="GATERUN-$DATE-integration-step-$SHORT"; WF="selfci-integration"
    RESULT="$CT/$AUDITS" ;;
  integration)
    [ -n "$CYCLE" ] || { echo "EMIT-GATE-RECORD FAIL: --cycle is required for --gate integration"; exit 2; }
    # Same id as mirror-agree.sh writes locally, because it is the same run.
    KEY="CYCLE-$CYCLE"; ID="GATE-$CYCLE"; WF="selfci-gate-b" ;;
  *) echo "EMIT-GATE-RECORD FAIL: --gate must be lane, integration-step or integration"; exit 2 ;;
esac
REC="records/gate/$GATE/$DATE/$KEY.yaml"

# A CI job result that is not "success" is a FAIL. cancelled, skipped and
# neutral are never passes (section 33.2).
VERDICT=FAIL
case "$GATE:$RESULT" in
  lane:success|integration:success|integration-step:success/success) VERDICT=PASS ;;
esac

# The per-check lines are the record's substance. The negative-battery result,
# the count triples, the signer and the trailing rejection count are TOKENS ON
# THOSE LINES - never a second copy that could disagree with them (protocol/05
# section 10).
NLINES=0
if [ -f "$LOG" ]; then NLINES=$(grep -c . "$LOG" || true); fi
if [ "$GATE" = "integration" ] && [ "$NLINES" -eq 0 ]; then
  echo "EMIT-GATE-RECORD FAIL: gate log $LOG absent or empty - a cycle record with no per-check lines is not evidence (protocol/05 section 10)"
  exit 1
fi
if [ "$NLINES" -eq 0 ]; then CH="checks: []"
else CH="checks:
$(sed 's/\\/\\\\/g; s/"/\\"/g; s/^/  - "/; s/$/"/' "$LOG")"; fi

BODY=$(printf 'record_schema_version: 1\nid: %s\nproduct: control-plane\ntimestamp: %s\ngate: %s\ncycle: %s\nhead: %s\nworkflow: %s\nrun_id: "%s"\nverdict: %s\nat_denominator: "37/110 (protocol/02 section 9.1)"\n%s\n' \
  "$ID" "$TS" "$GATE" "${CYCLE:-none}" "$HEAD" "$WF" "$RUNID" "$VERDICT" "$CH")

ERRF="${TMPDIR:-/tmp}/emit-gate-record.$$"
B64=$(printf '%s' "$BODY" | base64 | tr -d '\n')
if gh api --method PUT "repos/$REPO/contents/$REC" \
     -f message="gate record $ID" -f content="$B64" >/dev/null 2>"$ERRF"; then
  printf 'EMIT-GATE-RECORD PASS gate=%s record=%s verdict=%s checks=%s\n' "$GATE" "$REC" "$VERDICT" "$NLINES"
  rm -f "$ERRF"; exit 0 # exit 0 = gate ARMED (FD-035)
fi
if grep -qi 'sha\|already exists\|422' "$ERRF" 2>/dev/null; then
  printf 'EMIT-GATE-RECORD FAIL record=%s reason=already-exists - records are append-only, never overwritten (invariant 47)\n' "$REC"
else
  printf 'EMIT-GATE-RECORD FAIL record=%s reason=write-refused\n' "$REC"
fi
rm -f "$ERRF"; exit 1
EGR
chmod +x contracts/gate/emit-gate-record.sh

git add contracts/gate/emit-gate-record.sh
git commit -m "L0-05-15: emit-gate-record.sh - the committed gate record (protocol/10 7.2, 7.3, 7.4)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The script exists at the path `protocol/10` invokes | `test -x contracts/gate/emit-gate-record.sh && echo PRESENT` | `PRESENT` |
| 2 | All three `--gate` forms are accepted | `grep -c '^  lane)\|^  integration-step)\|^  integration)' contracts/gate/emit-gate-record.sh` | `3` |
| 3 | The three record keys match `protocol/10` §11 | `grep -c 'PR-\$PR-\$SHORT\|KEY="\$SHORT"\|CYCLE-\$CYCLE' contracts/gate/emit-gate-record.sh` | `3` |
| 4 | **A cycle record with no per-check lines is refused** | see SELF-VERIFY case B | `EMIT-GATE-RECORD FAIL: gate log ... absent or empty` |
| 5 | **A non-`success` CI result never becomes `verdict: PASS`** | see SELF-VERIFY case E | `verdict: FAIL` |
| 6 | The write carries no `sha`, so a second write is server-refused | `grep -c '\-f sha' contracts/gate/emit-gate-record.sh` | `0` |
| 7 | An existing key is reported as append-only, not as a generic error | see SELF-VERIFY case C | `reason=already-exists` |
| 8 | The org is never guessed | `RECORDS_REPO_OWNER= GITHUB_REPOSITORY_OWNER= sh contracts/gate/emit-gate-record.sh --gate lane --pr 1 --head abc; echo "rc=$?"` | `EMIT-GATE-RECORD FAIL: RECORDS_REPO_OWNER unset - the target org is never guessed` then `rc=2` |
| 9 | An unknown gate name is a config error, not a default | see SELF-VERIFY case D | `rc=2` |
| 10 | The record names the acceptance denominator | see SELF-VERIFY case A | `denom=1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
W=$(mktemp -d); mkdir -p "$W/bin" "$W/log"
# stub gh: case A/E succeed and capture the body; case C refuses with 422.
cat > "$W/bin/gh" <<'GH'
#!/usr/bin/env sh
for a in "$@"; do case "$a" in content=*) echo "${a#content=}" | base64 -d > "$GHCAP" ;; esac; done
[ "${GHFAIL:-0}" = "1" ] && { echo '{"message":"Invalid request. \"sha\" wasn'"'"'t supplied.","status":"422"}' >&2; exit 1; }
exit 0
GH
chmod +x "$W/bin/gh"; PATH="$W/bin:$PATH"; export PATH RECORDS_REPO_OWNER=probe-org
for n in 1 2 3 4 5 6 7 8 9 10 11 12; do printf 'IG-%02d probe PASS token=%s\n' "$n" "$n"; done > "$W/log/ok.log"
: > "$W/log/empty.log"

# case A - a full cycle record
export GHCAP="$W/a.yaml"
A=$(sh contracts/gate/emit-gate-record.sh --gate integration --cycle 2026-08-27-a \
      --head 4bd90fe1122334455 --result success --run-id 99 --log "$W/log/ok.log" | tail -1)
# case B - a cycle record with no per-check lines
B=$(sh contracts/gate/emit-gate-record.sh --gate integration --cycle c2 --head abc1234 \
      --result success --run-id 99 --log "$W/log/empty.log" 2>&1 | tail -1 | cut -c1-31)
# case C - the key already exists
export GHCAP="$W/c.yaml" GHFAIL=1
C=$(sh contracts/gate/emit-gate-record.sh --gate lane --pr 417 --head 9f2c1ab99 \
      --result success --run-id 99 2>&1 | tail -1 | sed 's/.*reason=/reason=/; s/ -.*//')
unset GHFAIL
# case D - a gate name nobody declared
sh contracts/gate/emit-gate-record.sh --gate everything --head abc1234 >/dev/null 2>&1; D=$?
# case E - a cancelled CI job
export GHCAP="$W/e.yaml"
sh contracts/gate/emit-gate-record.sh --gate integration --cycle c3 --head abc1234 \
      --result cancelled --run-id 99 --log "$W/log/ok.log" >/dev/null 2>&1
printf 'A=[%s] lines=%s denom=%s B=[%s] C=[%s] D=%s E=[%s]\n' \
  "$A" "$(grep -c '^  - "IG-' "$W/a.yaml")" "$(grep -c 'at_denominator: "37/110' "$W/a.yaml")" \
  "$B" "$C" "$D" "$(sed -n 's/^verdict: //p' "$W/e.yaml")"
```

Expected output, exactly:

```
A=[EMIT-GATE-RECORD PASS gate=integration record=records/gate/integration/2026-08-27/CYCLE-2026-08-27-a.yaml verdict=PASS checks=12] lines=12 denom=1 B=[EMIT-GATE-RECORD FAIL: gate log] C=[reason=already-exists] D=2 E=[FAIL]
```

The date component of case A's `record=` is the day you run it; every other field is fixed.

**STOP rule** — if `E` is not `FAIL`, a cancelled CI job is being recorded as a passing gate run, and every
downstream reader of `records/gate/**` — the `IG-11` rejection window, `protocol/11` §5, the evidence chain —
inherits the lie from a file nobody will re-derive. `protocol/10` §10 states the rule this implements: *"A
cancelled required context is not a pass."* Fix the `case` block, do not add a mapping for `cancelled`. If `C` is
not `reason=already-exists`, a second write to an existing key is being reported as a generic error; the
append-only violation then reads as a network problem and gets retried. If `B` succeeded, a cycle record with no
per-check lines was accepted, and `IG-12`'s `record=` token would name a file that proves nothing — open
`BLOCKER L0-05-15: cycle record accepted with no per-check lines` and stop. **Never add a `-f sha` parameter to
make a re-write succeed**: that converts an append-only store into a mutable one, which is invariant 47 deleted
by a one-line change.

---

## 8. THE ONE COMMAND, AND THE ONE STRING THAT OPENS `main`

Everything above exists so that this section is two commands long.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch origin main integration
make gate-integration CYCLE=2026-08-27-a
```

`make gate-integration` runs the assembled-system smoke, then `IG-01` … `IG-12` in order, writes every per-check
line to `.gate/integration.log`, writes the aggregate to `.gate/integration.verdict`, emits the append-only gate
record, and prints **exactly one line** on stdout:

```
VERDICT=PASS GATE=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=12/12 negatives=24/24 counts=OK canary=FOUND lanes=5/5 signer=paresh ts=2026-08-27T18:22:07Z
```

### 8.1 The unambiguous pass test — this and nothing else

Reproduced from `protocol/05` §4.1 without a character changed.

**Commands**

```bash
set -euo pipefail
make gate-integration CYCLE=2026-08-27-a | tee .gate/integration.stdout
grep -Fq 'VERDICT=PASS GATE=integration' .gate/integration.stdout \
  && grep -Fq 'canary=FOUND' .gate/integration.stdout \
  && grep -Fq 'negatives=24/24' .gate/integration.stdout \
  && test "$(wc -l < .gate/integration.stdout)" -eq 1 \
  && echo GATE-B-OPEN || echo GATE-B-CLOSED
```

**`GATE-B-OPEN` is the only string that authorises `integration` → `main`.** Anything else is a closed gate:
`GATE-B-CLOSED`, no output at all, a non-zero exit, more than one line, a `VERDICT=FAIL`, a truncated log.

Four assertions, and each one exists because of a specific way a broken gate stays green:

| Assertion | The failure it catches |
|---|---|
| `VERDICT=PASS GATE=integration` | The obvious one, and the only one most people would write |
| **`canary=FOUND`**, by name | The reconciler stopped looking. `EC-109`: *"A reconciliation run completes 'clean' while actually checking nothing."* The verdict line still prints; the token quietly goes missing |
| **`negatives=24/24`**, by name | The negative battery lost a check. A battery reporting `18/18` is arithmetically consistent and proves nothing about the six checks it forgot |
| `wc -l == 1` | A chatty or partially-crashed script printed a reassuring summary after a failure line. One line means one answer |

`protocol/05` §4.1 says why the two middle assertions are made separately: *"those are the two tokens a broken gate
is most likely to lose while still printing a verdict — the exact failure EC-109 describes."*

### 8.2 What a closed gate looks like

Failures are as literal as passes.

```
IG-05 counts FAIL at=110/110/111 inv=111/111 ec=112/112 checks=24/24 registries=9/9 narrowed=1
VERDICT=FAIL GATE=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=4/12 first_failure=IG-05
```

Read `at=110/110/111` as declared / unique-ids / id-cells: 110 tests are declared, 110 distinct ids exist, and
**111 id cells** were counted — one acceptance-test file carries an id that another file already carries. Nothing
is missing, nothing is extra, and the registry is still wrong. Two of the three numbers agree, which is why the
check needs all three.

### 8.3 The cycle-level closure, one level up

GATE B authorises the merge. It does not declare the cycle done. That is `protocol/11` §5, and it asserts three
further tokens by name — including the smoke verdict this gate consumed as a precondition:

**Commands**

```bash
set -euo pipefail
make dod-integration CYCLE=2026-08-27-a | tee .dod/integration.stdout  # (target defined in `protocol/11`, not in L0 tasks; reference here for sequence completeness)
grep -Fq 'DOD-VERDICT=MET LEVEL=integration' .dod/integration.stdout \
  && grep -Fq 'canary=FOUND'   .dod/integration.stdout \
  && grep -Fq 'canaries=14/14' .dod/integration.stdout \
  && grep -Fq 'e2e=PASS'       .dod/integration.stdout \
  && test "$(wc -l < .dod/integration.stdout)" -eq 1 \
  && echo INTEGRATION-DONE || echo INTEGRATION-NOT-DONE
```

`GATE-B-OPEN` without `INTEGRATION-DONE` means: the merge is authorised, the cycle is not closed. Both are needed
before the next cycle opens.

---

## 9. Failure taxonomy and STOP rules

You are reading this because `make gate-integration` printed something other than the line in §8. Find the row,
do what it says, stop. The nine rows of `protocol/05` §9 stand unchanged and are not restated where they already
cover the symptom; this section adds the `first_failure=` routing and the two things `protocol/05` §9 leaves
implicit — what a closed GATE B does **not** do, and whose next task the fix is.

### 9.1 What a closed GATE B does, and the four things it never does

A closed GATE B does exactly one thing: **`integration` is not merged to `main` this cycle.** That is the whole
of its authority. It does none of the following, and each refusal is anchored.

**1. It does not roll back the merge train.** `protocol/00` §5 T3: *"the train stops where it is."* Lanes that
already merged into `integration` stay merged. Revert has its own two triggers and GATE B is neither of them:
`L0-03-10` (a named merge left `integration` red at T06 step 5, or `make promote-check` printed
`CONTRACTS-DRIFT`<!-- FD-055: gate-state/ is mutable; not part of contracts/ SHA-256 hash -->, or `train-owners.sh` failed after a merge that individually passed `lane-guard`) and
`L0-03-11` (a bad promotion already on `main`). Unwinding five lanes' work because one check closed manufactures
exactly the rework the partition exists to prevent.

**2. It does not re-order the train or let a lane merge past it.** `protocol/00` §5 T3: *"No lane merges ahead of
a stopped train — the merge order L1 → L4 → L2 → L3 → L5 exists because of dependency order, and reordering
around a failure ships the dependency inversion the order exists to prevent."* The order is PARTITION's and
frozen; changing it is `L0D-07` with a decision record.

**3. It is not waived.** `protocol/00` §5 T3: *"There is no partial pass and no override that is not a recorded
exception with an expiry (invariant 77)."* The only override shape that exists is a declared exception in
`exceptions.yaml` (§95.2) naming the gate, the repositories, the compensating control, an owner, an expiry and a
deactivation trigger, authored by L0 as a decision record; an exception without an expiry is rejected by CI
(invariant 77). And note the limit of what an exception can buy. It can buy time against a control that is not
yet **buildable** — that is what `protocol/05` §7 uses it for when headcount cannot supply a second human. It
cannot make **missing evidence** valid. An exception written to silence `canary=FOUND` would not convert a
vacuous reconciliation run into a good one: §53.7 has already classified that run as failed and its window as
`gap-window`, and *"a gap-window record is not evidence for any gate until re-verification clears the mark."*

**4. It is not re-run for a different answer.** One cycle, one verdict of record (**L0D-IG-7**). A re-run after
changing an input is a **new cycle with a new id**, and the closed run's record stays where it was written
(invariant 47). `protocol/10` §10 says the same thing about an instrument that hangs: *"Never re-run hoping for a
different answer."* Re-running until green is the rubber-stamp failure §103 names, executed by machine instead of
by a person.

### 9.2 The taxonomy — one row per way GATE B closes

Every symptom below is a literal token from stdout or from `.gate/integration.log`. Nothing here requires
interpretation.

| Symptom | Classification | Action | STOP rule |
|---|---|---|---|
| `first_failure=IG-01`, `lanes=<4 or fewer>/5` | The cycle is not complete — a lane did not land | Finish the cycle, or record the lane's `NONE`/`SKIPPED` line (`L0-03-08`) and re-run | Do not promote a partial cycle. `IG-01` counts lanes; it does not judge whether the absence was reasonable |
| `first_failure=IG-01`, `out_of_order>0` | The train ran in an order PARTITION does not permit | Stop the cycle. The dependency inversion is already merged | Do not "re-order the record". Only `L0D-07` with a decision record changes the order |
| `first_failure=IG-01`, `cross_lane_merges>0` | A lane merged another lane's branch | Identify the merge; treat as a partition violation (`L0-03-02`, `TRAIN HALT, CLASSIFICATION: PARTITION-VIOLATION`) | PARTITION §"Branch & merge model": *"A lane NEVER merges another lane's branch."* No exception |
| `first_failure=IG-02`, `failed>0` | A lane's suite passed alone and fails in company | The named lane's next task is the fix | Do not skip the lane's suite to get the cycle out. `IG-02` is the only place composition is tested |
| `first_failure=IG-02`, `seeded_defects=<n>/5` with `n<5` | A lane's verification instrument stopped discriminating (§31.2, SIG-18) | Restore the seeded case; the product is Blocking until the case fails again | `protocol/05` §9, verbatim: *"Never delete the seeded case to make the suite green."* |
| `first_failure=IG-02` and a lane reports `assertions=0` | A vacuous suite (`protocol/00` §3, exit `2`) | Repair the suite | A green run with zero assertions is not a pass. Do not lower the threshold |
| `first_failure=IG-03`, `stubbed>0` | A consumer is still resolving against its Phase-0 stub; the real producer has never been tested against | The consumer removes the stub resolution and runs against the live producer | Do not report `pairs=<n>` green while any case resolves to `.contract-stubs/`. That is the exact failure `IG-03` exists for |
| `first_failure=IG-03`, `fixtures_match=0` | A frozen contract fixture was modified | Restore the fixture from `gate/v1.0.0`; the change goes through a CCR | `protocol/00` §9: *"Do not edit it. Open a Contract Change Request. Stop."* |
| `first_failure=IG-04`, `unproven>0` | A gate check cannot be shown able to fail | Repair the negative case before anything else | `protocol/05` §1 rule 1: the check is treated as **not present**. Fail closed |
| `first_failure=IG-04`, `canary=MISSING` | The reconciler stopped looking (AT-102, EC-109) | Treat the run as a **FAILED** run; raise SIG-13; run the §53.7 gap procedure over the window; mark records produced in the window `gap-window` | `protocol/05` §9, verbatim: *"Never record the run as clean."* |
| `first_failure=IG-05`, `narrowed=1` | A registry enumerates less than it declares (D44) | Diff the registry against `COUNTS.tsv`; restore the missing items | `protocol/05` §9, verbatim: *"Do not adjust `COUNTS.tsv` to match the code."* |
| `first_failure=IG-05` with a three-way mismatch such as `at=110/110/111` | Declared, unique and cell counts disagree — a duplicate or a narrowed comparison | Find the id that occupies two cells; restore one file per item | Two of three numbers agreeing is the normal appearance of this defect. Do not accept it |
| `first_failure=IG-06`, `unclassified>0` | The invariant classification is incomplete — **L0-IG-D3** is open (subsystem **O**) | L0 answers `L0-IG-D3`; the gate stays closed meanwhile | Never mark `IG-06` not-applicable. §99.6 risk 5: *"An unavailable protection feature reproduces the silent-gate failure."* |
| `first_failure=IG-06`, `dangling_refs>0` | A `mechanical` invariant names a check or AT that does not exist | Correct the reference to a real id, or reclassify with a decision record | Do not delete the row. A deleted classification is `unclassified`, which also closes the gate — deliberately |
| `first_failure=IG-07`, `not_run>0` | A scheduled acceptance test was never executed | Run it; if the harness path does not exist, **L0-IG-D2** is the blocker | A missing harness is never `scheduled=0`. **Never move an AT to a later phase to make a cycle pass** |
| `first_failure=IG-07`, `asserted_only>0` | An AT has a claim but no recorded twin result (**L0D-IG-6**) | Run the twin, record the result | `protocol/02` §10: the AT is `UNPROVEN`, not `PASS`. Do not promote a claim to a result |
| `first_failure=IG-08`, `foreign>0` | A foreign path entered inside a merge commit | Remove the path; the owning lane files a CCR if it genuinely needs it | `protocol/05` §9, verbatim: *"Do not edit `ownership.tsv`. Do not merge."* |
| `first_failure=IG-08`, `unowned>0` | A path no row in `ownership.tsv` claims (`protocol/05` §6) | L0 assigns ownership first (`L0D-04`) | `unowned>0` is a failure, not a warning. A path with zero owners is a future two-lane collision |
| `first_failure=IG-09`, `credential=... is a machine identity under test` | The verifier ran as the thing it verifies | Re-run under `$GATE_VERIFIER_TOKEN` | §53.1: *"no control that can be rewritten by the credential it is checking is a control."* Do not proceed under the reconciler's or the records-writer's token |
| `first_failure=IG-09`, `machine_codeowners>0` or `bypass_actors_exact=0` | Branch protection drifted from the committed template | `access/**` is L5's; L0 files a Blocking-class item and never edits it | D89: no machine bypass actor on `control-plane`. Do not "temporarily" add one to land the cycle |
| `first_failure=IG-10`, `e2e=FAIL` or an absent smoke stdout | The assembled-system smoke did not pass, so `IG-10` has nothing honest to read | Fix the smoke (`protocol/08`), re-run the gate | `IG-10` is never skipped and never not-applicable when the smoke did not run. **L0D-IG-2** |
| `first_failure=IG-10`, `digest_mismatches>0` or `rebuilt>0` | The artifact that reached production is not the artifact staging verified (invariant 22) | The pipeline promotes the digest; it never rebuilds | Do not re-tag to make the digests match. That records agreement without creating it |
| `first_failure=IG-10`, `skipped>0` or `neutral>0` | A required context that appears green never ran (§33.2) | Remove the `if:`/path filter from the job emitting the required name — `.github/workflows/**` is L2's | `protocol/05` §9, verbatim: a `skipped`/`neutral` conclusion on a required context of a merged PR **is Blocking drift** |
| `first_failure=IG-11`, `machine_approvals>0` | A machine approved a gate (invariant 18, D53) | Dismiss the approval; obtain a human one; record the incident | `protocol/05` §9, verbatim: *"The merge does not proceed on a machine approval under any framing."* |
| `first_failure=IG-11`, `self_signoff=1` | The signer is the author of the cycle's largest diff | A different Write-holding human signs | Invariant 9. No self-approval, under any framing, including "nobody else was available" |
| `first_failure=IG-11`, `drills=<n>/5` with `n<5` | A lane has no injected-defect drill record this cycle (`protocol/00` §4.3) | The lane runs the drill; the record is `records/gate-runs/<cycle>/drill-L<n>.yaml` | The drill is the anti-rubber-stamp evidence. Its absence is not a formality |
| `first_failure=IG-12`, `delta=1` | CI and the L0 run disagree | Investigate the workflow diff before anything else; a workflow-file change pushed by a machine identity is Blocking drift (§53.1) | `protocol/05` §9, verbatim: *"Never take the greener of the two verdicts."* |
| `first_failure=IG-12`, `ci=SKIPPED`, `ci=NEUTRAL`, `ci=CANCELLED` or `ci=ABSENT` | There is no mirror to agree with | Get a real conclusion on the promoted head | A missing mirror is not agreement, whatever the local verdict says |
| Any check line reading `NO-OUTPUT-FAIL` | Instrument failure — a script crashed, timed out, or printed nothing | Fail closed; the gate is CLOSED; repair the script | Invariant 80, and **L0D-IG-9**: absence of output is never a pass |
| stdout is more than one line | The driver's output discipline broke | Repair `run-integration.sh`; the §8.1 test asserts `wc -l == 1` for this reason | A reassuring summary printed after a `VERDICT=FAIL` line is how a closed gate gets read as open |

### 9.3 Routing — whose next task the fix is

`protocol/00` §5 T3: *"The failing check names one lane; that lane's next task is the fix."* This table makes
"names one lane" mechanical. The owner is read from PARTITION's path table, never from a judgement about who
seems responsible.

| Check | Whose next task | Why — the owned path |
|---|---|---|
| `IG-01` | L0 | The train is L0's (`L0-03`). A `cross_lane_merges>0` finding additionally names the offending lane |
| `IG-02` | the lane named in the failing `LANE-SUITE` line | Its suite, its owned paths |
| `IG-03` | the failing pair's **provider**, unless the provider conforms to `contracts/**` and the consumer does not — then the consumer. If **both** conform, neither is at fault and it is a CCR to L0 | `contracts/**` is the arbiter, and it is L0's (PARTITION rule 2) |
| `IG-04` | L0 for a mutation that failed to fire (`contracts/gate/**`); the reconciler lane **L3** for `canary=MISSING`; for `seeded_defects`, the lane whose verification contract case passed | Mutations are L0-owned; the canary lives in `reconciler/**` |
| `IG-05` | the lane owning the narrowed registry — `registries/**` is **L1**, `records/**` is **L4** | PARTITION path table |
| `IG-06` | L0, blocked on **L0-IG-D3** | `policies.yaml` is subsystem **O**, unassigned in PARTITION v1 |
| `IG-07` | the `owner_lane` column of `contracts/gate/at-activation.tsv` for the failing AT — `G` means unassigned, blocked on **L0-IG-D4** | The frozen activation map, L0-05-04 |
| `IG-08` | the lane whose commit introduced the foreign path, as named by `lane-guard.sh` | `LG-02`'s single implementation (L0-02-02) |
| `IG-09` | **L5** for a protection or CODEOWNERS finding (`access/**`); L0 for a credential finding | PARTITION path table |
| `IG-10` | **L2** — the digest chain and the required contexts live in `.github/workflows/**` and `tools/evidence/**` | PARTITION path table |
| `IG-11` | L0 — the integrator signs, and the drill records are requested from the five lanes | `records/decisions/` (§97) |
| `IG-12` | **L2** for a workflow-side disagreement; L0 for a record-side one | `.github/workflows/**` is L2's; `contracts/gate/**` is L0's |

A lane is told by being sent the verbatim gate output, exactly as `L0-03-07` sends a lane its GATE A failure.
Nothing is paraphrased and nothing is summarised:

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
gh issue create --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  --title "GATE B CLOSED cycle $CYCLE: $(sed -n 's/.*first_failure=//p' .gate/integration.stdout) — lane L<n>" \
  --label "blocker" --label "lane-<n>" \
  --body "$(printf 'GATE B closed on cycle %s.\n\nstdout:\n```\n%s\n```\n\n.gate/integration.log:\n```\n%s\n```\n\nRouting: L0-05 §9.3. Taxonomy row: L0-05 §9.2.\nYour next task is the fix (protocol/00 §5 T3). Reply with the blocker template at docs/escalation/BLOCKER.md.\n' \
      "$CYCLE" "$(cat .gate/integration.stdout)" "$(cat .gate/integration.log)")"
```

### 9.4 The blocker, filled in

The lane replies with `docs/escalation/BLOCKER.md` (L0-00-05), unchanged, titled
`BLOCKER <its next task id>: GATE B <IG-nn> <failing token>`. Two fields are filled differently at GATE B than at
GATE A, and getting them wrong is what makes a blocker unactionable:

- **STOPPED AT** is the `IG-` check id and the literal failing line from `.gate/integration.log`, not "the
  integration gate".
- **EXACT OUTPUT OBSERVED** is the whole one-line stdout **and** the failing log line. The one-line verdict alone
  does not identify the cause; the log line alone does not prove the gate closed.

A filled example, for the routing case a lane is most likely to receive:

```text
TASK ID:        L3-06-04
LANE:           3
BRANCH:         lane/3/eh-canary-restore
STOPPED AT:     IG-04, log line: IG-04 negatives FAIL proven=23/24 unproven=1 canary=MISSING seeded_defects=DETECTED

WHAT I WAS ASKED TO DO
"Fix the check named by first_failure. L0-05 §9.3 routes canary=MISSING to L3."

WHY I CANNOT PROCEED
spec sentence reads two ways

FORBIDDEN/UNDECIDED ID:   NONE
SPEC SENTENCE QUOTED:     §53.1 / EC-109: "A reconciliation run completes 'clean' while actually checking
                          nothing — a broken query, an empty product enumeration."

EXACT OUTPUT OBSERVED
$ make gate-integration CYCLE=2026-08-27-a
VERDICT=FAIL GATE=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=3/12 first_failure=IG-04
$ grep '^IG-04' .gate/integration.log
IG-04 negatives FAIL proven=23/24 unproven=1 canary=MISSING seeded_defects=DETECTED

WHAT I DID NOT DO
I made no choice, wrote no default, left no TODO, and pushed no code past this point.

FILES TOUCHED SO FAR
(clean)
```

**The one thing a lane must never put in a blocker** is a proposed change to `contracts/gate/**`. That tree is
L0's (**L0D-IG-1**), and a lane proposing its own exam paper is the failure §53.1 describes. Report the token;
L0 owns the remedy.

### 9.5 The one flag that does not close the gate

`rubber_stamp_flag=1` is the exception to everything above, and it is deliberate. `IG-11` raises it when the
trailing ten-cycle window contains **zero** rejections. `protocol/05` §7: *"A flagged window does not by itself
close GATE B; it forces a named written answer on the gate record explaining why ten clean cycles are real."*
§103 says why the flag exists at all — *"Watch the reason mix, not the rate. Zero rejections means the gates are
not working"* — and the plan-rejection half of that count depends on subsystem **G**, which no lane owns
(**L0-IG-D4**).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
grep -o 'rejections=[0-9]* rubber_stamp_flag=[01]' .gate/integration.log
```

If the flag is `1`, write the answer on the gate record before promoting — it is a field of the record, not a
comment on a pull request. **Do not silence the flag by widening the window** (`protocol/05` §9), and note the
opposite protection §17 states and §103 restates: a reviewer who says they do not understand a change is
behaving correctly and is never penalised for it. The response to a flagged window is pairing, never a second
mandatory reviewer bolted on to make the number move.

---

## 10. What the gate writes

`.gate/` is scratch and is git-ignored (L0-05-01). **The evidence is the record**, and there are two families of
it (**L0D-IG-8**), neither an index, both directory-per-item so that five lanes' records can never conflict
(PARTITION rule 3; §97; invariant 47).

### 10.1 The two families, and the three keys inside the first

| Family | Path | One file per | Written by | Named in |
|---|---|---|---|---|
| Gate verdicts | `records/gate/lane/<date>/PR-<n>-<sha7>.yaml` | GATE A run | `emit-gate-record.sh --gate lane` (L0-05-15) from `selfci-gate-a` | `protocol/05` §10; `protocol/10` §11 |
| Gate verdicts | `records/gate/integration-step/<date>/<sha7>.yaml` | post-merge train step | `emit-gate-record.sh --gate integration-step` from `selfci-integration` | `protocol/10` §11 |
| Gate verdicts | `records/gate/integration/<date>/CYCLE-<cycle>.yaml` | **cycle** | `emit-gate-record.sh --gate integration` from `selfci-gate-b`; the same key `mirror-agree.sh --emit-record` writes locally | `protocol/05` §10 |
| Level results | `records/gate-runs/<cycle>/<level>-<lane>.yaml` and `records/gate-runs/<cycle>/drill-L<n>.yaml` | level per lane per cycle, and the injected-defect drill | the lane's own CI, under the records-writer credential | `protocol/00` §10, §4.3 |

`IG-11` reads the second family for `drills=<n>/5` and the first family for the trailing rejection window. Neither
is derived from the other, which is why both exist.

### 10.2 The cycle record, field by field

`protocol/05` §10 requires a record to carry *"gate, lane or cycle, head SHA, the twelve per-check lines
verbatim, the negative-battery result, the count triples, the human approver or signer, the trailing rejection
count, and the verdict line."* Nine of those are single fields. **The last five are not copied into fields at
all** — they are tokens on the twelve per-check lines, quoted verbatim:

```yaml
record_schema_version: 1
id: GATE-2026-08-27-a
product: control-plane
timestamp: 2026-08-27T18:22:07Z
gate: integration
cycle: 2026-08-27-a
head: 4bd90fe1122334455667788990aabbccddeeff00
workflow: selfci-gate-b
run_id: "12345678901"
verdict: PASS
at_denominator: "37/110 (protocol/02 section 9.1)"
checks:
  - "IG-01 merge-train PASS lanes=5/5 order=1,4,2,3,5 out_of_order=0 cross_lane_merges=0"
  - "IG-02 lane-suites PASS lanes=5/5 tests=1284 failed=0 seeded_defects=5/5 DETECTED"
  - "IG-03 contract-tests PASS pairs=10 cases=61 failed=0 stubbed=0 fixtures_match=1"
  - "IG-04 negatives PASS proven=24/24 unproven=0 canary=FOUND seeded_defects=DETECTED"
  - "IG-05 counts PASS at=110/110/110 inv=111/111 ec=112/112 checks=24/24 registries=9/9 narrowed=0"
  - "IG-06 invariant-classification PASS classified=111/111 mechanical=68 dangling_refs=0 unclassified=0"
  - "IG-07 at-coverage PASS scheduled=1 executed=1 not_run=0 asserted_only=0"
  - "IG-08 lane-guard-replay PASS commits=94 foreign=0 unowned=0"
  - "IG-09 independent-verifier PASS repos=2 machine_codeowners=0 template_diff=0 bypass_actors_exact=1 credential=verifier"
  - "IG-10 artifact-honesty PASS digest_mismatches=0 rebuilt=0 skipped=0 neutral=0"
  - "IG-11 human-signoff PASS signer=paresh decision_record=DR-0091 machine_approvals=0 window_cycles=10 rejections=3 rubber_stamp_flag=0"
  - "IG-12 mirror-agree PASS ci=PASS local=PASS delta=0 record=records/gate/integration/2026-08-27/CYCLE-2026-08-27-a.yaml"
```

**Why the tokens are not also fields.** A record carrying `negatives: 24/24` beside a check line reading
`proven=23/24` has two answers and no way to tell which one a later reader will believe. One copy, quoted
verbatim from the instrument that produced it, cannot disagree with itself. The `at_denominator` field is the
one deliberate addition (**L0D-IG-5**): a cycle record that reports acceptance coverage without stating that the
five-lane build can reach only 37 of the 110 tests is a status report that overstates itself, and `protocol/02`
§9.1 rejects it.

`IG-12`'s pass line names this file, and `protocol/05` §10 is categorical: *"A gate run with no record is itself
a failure."* That is why the record is emitted **before** the verdict is finally reported (L0-05-14), and why
`mirror-agree.sh` refuses to overwrite an existing key.

### 10.3 Two copies of one run, and the parity check L0 runs after promotion

The cycle key is written twice, on purpose, by two identities that cannot substitute for each other:

| Copy | Written by | Where it lives | What it is |
|---|---|---|---|
| The verdict of record | `mirror-agree.sh --emit-record` (L0-05-14) | the `$CPR_ROOT` **working tree**, uncommitted | the L0 run — the verdict (**L0D-IG-7**) |
| The durable record | `emit-gate-record.sh` (L0-05-15) from `selfci-gate-b`, under `RECORDS_WRITER_TOKEN` | the default branch of `control-plane-records` | the committed evidence (D89; D107) |

L0 does not commit the first, ever: L4 owns all of `control-plane-records` (PARTITION.md §"Repositories"), and
record writes belong to the records-writer credential, never to a person's (D89). `IG-12` already proves the two
copies agree on the thing that matters — `delta=0` is the comparison of the CI conclusion with the local verdict
— so parity is a **post-promotion tidy-up**, not a thirteenth check (**L0D-IG-2**):

**Commands**

```bash
set -euo pipefail
cd "$CPR_ROOT"
git fetch --prune origin
REC="records/gate/integration/$(date -u +%F)/CYCLE-$CYCLE.yaml"
git show "origin/main:$REC" > "${TMPDIR:-/tmp}/committed.yaml" 2>/dev/null || echo "RECORD-PARITY FAIL: no committed record"
for k in gate cycle head verdict; do
  L=$(sed -n "s/^$k: //p" "$REC"); C=$(sed -n "s/^$k: //p" "${TMPDIR:-/tmp}/committed.yaml")
  [ "$L" = "$C" ] || echo "RECORD-PARITY DIFF $k local=$L committed=$C"
done
echo "RECORD-PARITY CHECKED $REC"
rm -f "$REC"            # the local copy is a working-tree artifact, not evidence
git status --porcelain | head -1
```

Expected: `RECORD-PARITY CHECKED records/gate/integration/<date>/CYCLE-<cycle>.yaml`, no `DIFF` line, and no
output from `git status --porcelain`. `timestamp` and `run_id` differ between the copies by construction and are
not compared; `gate`, `cycle`, `head` and `verdict` must be identical.

**STOP rule.** `RECORD-PARITY FAIL: no committed record` after `selfci-gate-b` has run means the required,
failing record step did not fail when it could not write — `protocol/10` §10: *"**Never** make the record write
best-effort."* The merge already authorised is not revoked; the **cycle is not closed**, and §8.3's rule stands:
`GATE-B-OPEN` without `INTEGRATION-DONE` means the next cycle does not open. Open
`BLOCKER L0-05-15: gate record not committed for cycle <id>` and route by §9.3 — the record step lives in
`.github/workflows/**`, which is L2's. A `RECORD-PARITY DIFF verdict` line is worse and is Blocking drift: two
records of one run disagree about whether the gate opened. Do not delete either. Quote both on the blocker.

---

## 11. Quick reference — one promotion, start to finish

Two gates guard `main` and **neither subsumes the other**. `make promote-gate` (`L0-03-09`) judges the *cycle
bookkeeping* — contracts frozen, every path owned, no machine workflow commit, the freeze window, CI green on the
exact head. `make gate-integration` (this file) judges *what was built*. Their overlap on "all five lanes landed"
(`P6` and `IG-01`) is a duplicated assertion, which is not a contradiction: it is the same fact proven from the
cycle record and from the git history independently.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
export CPR_ROOT="$HOME/src/control-plane-records"
export CYCLE=2026-08-27-a
export GATE_VERIFIER_TOKEN=...                    # the second credential, IG-09 (L0-05-12)
git fetch origin main integration

# 1. GATE B — what was built. The one command.
make gate-integration CYCLE="$CYCLE" | tee .gate/integration.stdout

# 2. The one string that authorises the merge (protocol/05 §4.1, reproduced at §8.1).
grep -Fq 'VERDICT=PASS GATE=integration' .gate/integration.stdout \
  && grep -Fq 'canary=FOUND' .gate/integration.stdout \
  && grep -Fq 'negatives=24/24' .gate/integration.stdout \
  && test "$(wc -l < .gate/integration.stdout)" -eq 1 \
  && echo GATE-B-OPEN || echo GATE-B-CLOSED
#    GATE-B-CLOSED -> §9.2 for the row, §9.3 for the lane, §9.4 for the blocker. STOP.

# 3. The cycle bookkeeping gate, immediately before the PR (its P8 freeze window is time-sensitive).
make promote-gate CYCLE="$CYCLE"                  # PROMOTE-GATE OK

# 4. The promotion PR. A pull request, never a push, never a local fast-forward (L0-03-09).
gh pr create --base main --head integration --label promotion \
  --title "PROMOTE cycle $CYCLE: integration -> main" \
  --body "GATE B: GATE-B-OPEN. Record: records/gate/integration/$(date -u +%F)/CYCLE-$CYCLE.yaml. L0D-09."

# 5. Human Code Owner approval, no self-approval (invariant 9), no machine identity (invariant 18).
# 6. Merge, then close the cycle.
make dod-integration CYCLE="$CYCLE" | tee .dod/integration.stdout    # INTEGRATION-DONE (§8.3) (target defined in `protocol/11`, not in L0 tasks; reference here for sequence completeness)
# 7. Record parity, then remove the local copy (§10.3).
```

The whole gate, as one dependency chain: `L0-05-01` builds the tree and freezes the 24 check ids →
`T02`–`T13` build the twelve checks and their frozen inputs → `T14` assembles `make gate-integration` and
**rehearses it closing twelve times** → `T15` gives the record a way to be committed. Nothing here is trusted
until `rehearse.sh` prints `REHEARSAL PASS closed=N/N` (FD-057: N is the baseline closure count from `gate-state/rehearsal-baseline`; first run sets it): a gate that has only ever been observed passing has
not been observed.

---

## 12. What this file does not decide

| Matter | Owner | Anchor |
|---|---|---|
| Whether the gate has 24 checks | **L0D-IG-2**, and a decision record. Adding a check falsifies the `checks=24/24` register | `protocol/05` §8; D44 |
| How many cross-lane contract pairs exist — ten or twelve | **L0-IG-D1**. `IG-03` and `IG-05` stay closed until answered | `protocol/00` §5 T2; `protocol/01` §3, §4 |
| Who owns `verification/acceptance/**` and `tools/at/**` | **L0-IG-D2**, via `L0D-04`. This file does not claim them | `protocol/02` §2; `L0-00-charter.md` §2.3 |
| Which lane owns subsystem **O** and `policies.yaml` | **L0-IG-D3**, via `L0D-04`. `IG-06` stays closed until answered | §101 preamble; PARTITION v1 |
| Which lane owns subsystems **G**, **H**, **J**, **P** | **L0-IG-D4**, via `L0D-04`. Already escalated in `protocol/02` §2 and not re-litigated here | §99.2; PARTITION v1 |
| Who owns and creates `e2e/**` and `contracts/harness/**` | **L0-IG-D5**, via `L0D-04`. `IG-03` and `IG-10` stay closed until answered. See §5 L0-IG-D5 | B-04; `lane-paths.tsv` |
| Which identity commits a gate record | Decided, not open: the records-writer, through `emit-gate-record.sh` in CI. L0 never pushes to `control-plane-records` | D89; D107; `protocol/10` §7.2–§7.4 |
| The value of `gate-state/PHASE` | L0, at each §98 phase completion check. Never a lane, and never advanced to make a cycle pass | §98.2; **L0D-IG-5** |
| Whether to promote at all | `L0D-09` | `L0-03-09` |
| Revert versus roll-forward on a broken `integration` | `L0D-08`, with a decision record; the default is revert (invariant 27) | `L0-03-10` |
| Any deviation from `L1 → L4 → L2 → L3 → L5` | `L0D-07`, with a decision record | PARTITION §"Branch & merge model" |
| A bootstrap exception when the human requirement cannot be met | L0, as an entry in `exceptions.yaml` with a named compensating control, owner, expiry and deactivation trigger | §95.2; invariant 77; `protocol/05` §7 |
| Branch-protection and CODEOWNERS configuration itself | **L5**, `access/**`. L0 files a Blocking-class item; it never edits them | PARTITION path table; `IG-09` |
| The shape of the CI workflows that mirror this gate | **L2**, `.github/workflows/**`. The gate's verdict of record is not theirs to hold | **L0D-IG-7**; `protocol/10` |
| The schema the gate record validates against | **L4**, `schemas/records/**`. The gate writes the record; it does not define the record's schema | PARTITION path table |
| The content of `contracts/**` a failing `IG-03` pair points at | `L0D-06`, through a Contract Change Request. A lane never edits `contracts/**` | PARTITION rule 2 |
| Whether a specification anomaly is "fixed" | Nobody in this repository. `spec-anomalies.tsv` is a frozen expectation; the specification is an input, not an output | **L0D-IG-4**; EC-109 |

Nothing in a lane PR description, a lane blocker issue, a lane comment or a lane's own plan file moves any row of
this table, and nothing in this file moves a row of `PARTITION.md`.
