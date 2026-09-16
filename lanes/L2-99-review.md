# L2-99 — COHERENCE REVIEW OF LANE 2 (PIPELINE & EVIDENCE)

> **SUPERSEDED — 2026-09-02**  
> This review was produced against an earlier copy of the L2 lane files.  
> **Do not act on any finding in this document** without re-deriving it against the current files.

**Reviewed:** `L2-00-charter.md`, `L2-01-reusable-workflows.md`, `L2-02-digest-invariant.md`, `L2-03-production-gates.md`, `L2-04-evidence-chain.md`, `L2-05-tasks.md`, `L2-06-tests.md`, `L2-07-runbook.md` (19,918 lines) against `PARTITION.md` and `MultiProduct_MasterSpec_v4.0.md` (10,214 lines).
**Reviewer scope:** path ownership, dangling dependencies, missing controls, internal agreement, judgment leakage, citation integrity, executability.

---

## VERDICT

# 🔴 BLOCKED — DO NOT DISPATCH

Lane 2 contains **two mutually incompatible task decompositions of the same subsystem**, published as peers, sharing 23 task identifiers that name different work. A low-cost agent handed this lane cannot determine which document is authoritative, and any two agents working concurrently from `L2-04` and `L2-05` will both believe they own `L2-T500`–`L2-T516` and will write different files under the same ids.

Six defects are blocking. Ten more are correctness defects that must be fixed before dispatch but do not by themselves stop the lane.

**What is genuinely good, and should not be re-cut:** every one of the 161 task blocks across all eight files carries a SELF-VERIFY block, a STOP rule and an acceptance-criteria table — zero exceptions. No task writes outside the three owned trees. No dependency points at a task id that does not exist. Section line-range citations are accurate in eleven of twelve samples. `L2-01`, `L2-02`, `L2-03`, `L2-04` and `L2-06` are each internally consistent and densely executable. The defect is *between* documents, not inside them.

---

## BLOCKING DEFECTS

### B1 — Two incompatible task decompositions of the same lane
**Files:** `L2-05-tasks.md` §2 vs `L2-01`, `L2-02`, `L2-03`, `L2-04`, `L2-06`
**Task ids:** whole-lane

`L2-05-tasks.md` line 8 declares itself *"the complete, ordered work list for Lane 2 — **76 tasks** … Every task below is executable without opening another document."* Its master table is a self-consistent 76-row decomposition.

The five phase files define a **different** 78-task decomposition of the same subsystem:

| File | Ids defined | Count | Present in L2-05's 76? |
|---|---|---|---|
| `L2-01` | `L2-P1-T00`–`L2-P1-T15` | 16 | none |
| `L2-02` | `L2-T200`–`202`, `L2-T400`–`405`, `L2-T520`–`528` | 18 | none as the same task |
| `L2-03` | `L2-T170`–`177`, `L2-T370`–`371`, `L2-T570`–`572` | 13 | none |
| `L2-04` | `L2-T500`–`L2-T516` | 17 | none as the same task |
| `L2-06` | `L2-T600`–`611`, `L2-T220`–`221` | 14 | none |

Not one of `L2-T170`–`177`, `L2-T200`–`202`, `L2-T220`–`221`, `L2-T370`–`371`, `L2-T400`–`405`, `L2-T526`–`528`, `L2-T570`–`572`, `L2-T600`–`611` appears anywhere in `L2-05`'s master table. Conversely `L2-05` invents `L2-T517`–`519`, `L2-T521`–`525` bodies that no phase file knows about.

**Correction.** L0 must declare exactly one of the two decompositions normative and reduce the other to a pointer. If the phase files win, `L2-05` §2 must be regenerated as an execution-order index over the phase-file ids and nothing else. If `L2-05` wins, the phase files must be re-issued against its ids. Half-merging them will reproduce B2.

---

### B2 — 23 task ids bound to two different tasks
**Files:** `L2-04-evidence-chain.md` + `L2-05-tasks.md`; `L2-02-digest-invariant.md` + `L2-05-tasks.md`
**Task ids:** `L2-T500`–`L2-T516`, `L2-T520`–`L2-T525`

The same identifier names different work, different files, and different dependencies in two documents:

| Id | `L2-05` | `L2-04` |
|---|---|---|
| `L2-T502` | Action pin ledger → `tools/evidence/action-pins.txt` | Author `tools/evidence/eleven-questions.yaml` |
| `L2-T504` | Required-context ↔ job cross-check | Implement `tools/evidence/evidence-query` |
| `L2-T509` | Template renderer and placeholder lint | Author `.github/workflows/emit-deployment-record.yml` |
| `L2-T512` | Workflow-identity gate → `identity_gate.py` | Implement the P0 escalation path |
| `L2-T513` | Digest invariant → `digest_invariant.py` | Implement `tools/evidence/deploy-gate.sh` |

| Id | `L2-05` | `L2-02` |
|---|---|---|
| `L2-T520` | `verify-digest-chain` sweep | Branch, and the flat-record reader |
| `L2-T523` | The eight "shipped" conditions | **THE DIGEST INVARIANT** |
| `L2-T525` | DoD acceptance matrix and lane handoff | SBOM beside the digest |

`L2-04`'s `L2-T500` depends on `L2-T001`; `L2-05`'s `L2-T500` depends on `L2-T006` and `D-L2-07`. Same id, two dependency graphs.

This is already load-bearing in a third document: `L2-06-tests.md:1140` resolves `L2-T512` to `tools.evidence.identity_gate` (the `L2-05` binding) and `L2-06-tests.md:1738` resolves `L2-T502` to `tools/evidence/action-pins.txt` (also `L2-05`) — while `L2-06-tests.md:72` simultaneously asserts that `L2-T500`–`L2-T528` is *"already reserved elsewhere"* by **both** `L2-04-evidence-chain.md` **and** `L2-05-tasks.md`, without noticing that two documents cannot reserve the same range.

**Correction.** Re-number one side. The charter §12 band `L2-T500`–`L2-T699` has 200 slots and only ~40 are used; move `L2-04`'s seventeen to `L2-T530`–`L2-T546` and `L2-02`'s nine to `L2-T550`–`L2-T558`, or apply the inverse if `L2-05` is the document that gets regenerated. Then re-point `L2-06-tests.md` lines 72, 1140, 1246, 1738.

---

### B3 — `D-L2-07`, `D-L2-08` and `D-L2-09` each define three or four different questions
**Files:** `L2-02` §4, `L2-03` §5, `L2-04` §4, `L2-05` §1
**Task ids:** every task that names one of these as a blocker

| Id | `L2-02` | `L2-03` | `L2-04` | `L2-05` |
|---|---|---|---|---|
| `D-L2-07` | Required-context name composition for reusable-workflow calls | — | The eleven-question field binding | Implementation language and runtime for `tools/evidence/**` |
| `D-L2-08` | Required-check status of `digest-invariant-selftest` | Path of the verification-block store | The two `event_type` identifiers this phase writes | Template placeholder syntax |
| `D-L2-09` | The record field carrying an S18 platform-rebuild identity | Runtime evidence of privileged-runner tier | The `/version` observation transport | — |

The charter §9 defines only `D-L2-01`–`06`; every id from `07` upward was allocated independently by four documents. A blocker issue filed with `STOP RULE: D-L2-08` — which the blocker template requires — is unresolvable, because L0 cannot tell which of four questions is being asked. `L2-06` additionally allocates `D-L2-11`, `D-L2-12`, `D-L2-13` with no `D-L2-10` in its own file (`D-L2-10` is `L2-03`'s).

**Correction.** L0 assigns a single monotonic register. Suggested: keep `D-L2-01`–`06` (charter), then `07`–`09` = `L2-02`'s, `10`–`12` = `L2-03`'s, `13`–`15` = `L2-04`'s, `16`–`17` = `L2-05`'s, `18`–`20` = `L2-06`'s, `21`–`23` = `L2-01`'s DEC-A/B/C. Rewrite every in-text reference.

---

### B4 — `L2-01` uses an identifier namespace no other document recognises
**File:** `L2-01-reusable-workflows.md`
**Task ids:** `L2-P1-T00` … `L2-P1-T15` (all 16)

Every other L2 document uses `L2-TNNN`, governed by the charter §12 reservation table. `L2-01` uses `L2-P1-TNN`, which falls in no reserved band and is referenced by **zero** other files — `L2-05`, `L2-06` and `L2-07` cite `L2-01` only by document name and section (`L2-01-reusable-workflows.md §1 L2/P1/DEC-A`), never by task id. Its three decisions likewise use a private `L2/P1/DEC-A|B|C` namespace outside the `D-L2-nn` register.

The consequence is not cosmetic: `L2-01` builds `.github/workflows/ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-production.yml` and `restore-test.yml` — the same seven artifacts `L2-05` builds under `L2-T100`, `L2-T120`, `L2-T130`–`134`. Two agents, two documents, two ids, one file.

**Correction.** Re-number `L2-P1-T00`–`T15` into the charter §12 `L2-T100`–`L2-T299` band, or delete `L2-01`'s task bodies and make it the design rationale for `L2-05`'s `L2-T100`-series. Do not ship both as executable.

---

### B5 — Charter `L2-T003` SELF-VERIFY can never print OK
**File:** `L2-00-charter.md` lines 424–491
**Task id:** `L2-T003`

The heredoc writes `templates/workflows/required-checks.yaml` with **15** context names (verified by running the task's own regex over the task's own heredoc: `grep -cE '^    - [a-z0-9-]+$'` → `15`). Acceptance criterion A3 demands *"exactly `16`"* and the SELF-VERIFY asserts `test "$(...)" = "16"`. A correct transcription therefore prints `L2-T003 FAIL`, and the task's STOP rule forbids adding a sixteenth name. The task is unexecutable as written and dead-ends the executor at task 3 of 6.

`L2-05-tasks.md:72` already caught this and handles it correctly — it prints `CONTEXT_COUNT=15`, tells the executor `15` is the *correct* output of a correct transcription, forbids editing either side, and routes the arithmetic to L0 under S4. The charter was never updated to match.

**Correction.** In `L2-00-charter.md`, change A3 to `exactly 15` and the SELF-VERIFY comparison to `"15"`, or add the missing sixteenth context — and reconcile with `L2-05` §0.5, which also says "sixteen" (see M1).

---

### B6 — Three competing actor-gate implementations at three paths
**Files:** `L2-01`, `L2-03`, `L2-05`
**Task ids:** `L2-P1-T03`, `L2-T171`, `L2-T511`

| Task | File | Artifact |
|---|---|---|
| `L2-P1-T03` (`L2-01:531`) | `L2-01` | `.github/workflows/gate-actor.yml` — reusable workflow |
| `L2-T171` (`L2-03:257`) | `L2-03` | `.github/workflows/actor-gate.yml` — reusable workflow |
| `L2-T511` (`L2-05:264`) | `L2-05` | `tools/evidence/actor_gate.py` — Python module |

All three implement §37.3 (L3261–3268) and invariant 18 (L9477). The same split exists for the workflow-identity gate (`L2-T174` in `L2-03` vs `L2-T512` in `L2-05`) and the digest invariant (`L2-T523` in `L2-02`, `L2-T513` in `L2-05`, `L2-T506`/`L2-T513` in `L2-04`). Whichever merges second either overwrites the first or leaves the estate with two gates and no rule about which one `deploy-production.yml` calls.

`L2-06-tests.md` compounds this by testing **both** bindings: line 1614 resolves the actor gate to `tools.evidence.actor_gate` (`L2-05`'s) while line 1502 says its tokens are *"those fixed by `L2-03-production-gates.md` `L2-T171`"* (`L2-03`'s workflow).

**Correction.** L0 picks one implementation form per gate — reusable workflow or Python module — and deletes the other two tasks. §37.3 requires the gate be *"the first step of every privileged workflow"*, which favours the reusable-workflow form; `L2-06`'s negative tests invoke it as a Python module. One of those must change.

---

## HIGH DEFECTS

### H1 — `L2-05`, the designated executable list, is prose, not executable
**File:** `L2-05-tasks.md`
**Task ids:** 75 of 76

`L2-05` claims each task is *"executable without opening another document."* It contains **one** heredoc across 3,970 lines — the `required-checks.yaml` in `L2-T003`. All 76 task blocks specify their artifact through a prose `**Build this.**` paragraph. Compare the phase files, which supply literal content:

| File | Heredocs | Tasks | Lines/task |
|---|---|---|---|
| `L2-06` | 46 | 14 | 155 |
| `L2-04` | 41 | 17 | 200 |
| `L2-03` | 19 | 13 | 246 |
| `L2-02` | 17 | 18 | 126 |
| `L2-01` | 15 | 16 | 155 |
| **`L2-05`** | **1** | **76** | **52** |

**Two most complex tasks, checked directly (review item 7):**

**`L2-T519` — Evidence chain, the eleven questions (Size L, `L2-05:3xxx`). NOT EXECUTABLE.** The task's substance is four fixture files — `dep-complete.yaml`, `dep-no-approver.yaml`, `dep-digest-drift.yaml`, `dep-client-app.yaml` — described only by parenthetical ("all eleven answered, 5 == 11"). No schema, no field names, no example. The agent must design the deployment-record YAML shape, which is precisely what `D-L2-03` declares undecided and L4-owned. It must also route items 10 and 11 "through `profile_evidence`" with no call signature given, and handle "where the record declares an S18 platform-rebuild deployment" with no field name for that declaration. The STOP rule anticipates the assignment registry being "unreachable" but the task never says how to reach it.

**`L2-T131` — `deploy-production.yml` (Size L, `L2-05:2190`). NOT EXECUTABLE.** The most gated workflow in the estate is specified as an eight-item prose list with no YAML. Undefined: the reusable-workflow `inputs:`/`secrets:` contract, how the staging-verified record is located, how `records_client` is invoked from an Actions step, how the product's declared timezone is obtained, the deploy/smoke/health commands, and the runner tier (see H2). Separately, its SELF-VERIFY **does not prove its own acceptance criteria**: criterion 1 requires the four gates "in that order, and the actor gate is step 0", but `GATES=4` is an unordered whole-file `grep -c`, and `FIRST_STEP` uses `grep -A4 '^[[:space:]]*steps:'` — a four-line window that assumes a YAML layout the task never fixes. A file with the gates in reverse order passes.

**Correction.** Either promote the phase files to normative (B1) — they carry the literal content — or back-fill every `L2-05` task with the heredoc its phase-file twin already has.

---

### H2 — D87 runner-tier assertion absent from `L2-05` entirely
**File:** `L2-05-tasks.md`
**Task ids:** `L2-T131`, `L2-T132`, `L2-T133`, and the missing `restore-production` task

D87 (spec L10180) requires: *"Each privileged workflow asserts its own runner tier and fails closed; three Blocking drift rows detect the rest."* `grep -c 'D87\|runner.tier\|runner_tier\|ephemeral' L2-05-tasks.md` returns **0**. `L2-01` cites D87 seventeen times; `L2-03` implements the assertion as `L2-T172`.

An agent executing `L2-05` alone — which the document instructs — produces four privileged workflows with no runner-tier assertion, silently violating D87 and the charter's own §8.1 mapping of §39.5.

**Correction.** Add a runner-tier task to `L2-05` (or adopt `L2-T172`) and make it a dependency of `L2-T131`, `L2-T132`, `L2-T133` and the restore-production task.

---

### H3 — The `restore-production.yml` reusable workflow is built by no `L2-05` task
**File:** `L2-05-tasks.md` §2
**Task ids:** missing at the `L2-T135` slot

The master table runs `L2-T134` (`restore-test.yml`) → `L2-T136` (`org-export.yml`). `L2-T135` is an unexplained hole exactly where `.github/workflows/restore-production.yml` belongs. `L2-T307` builds only the *template*. `L2-01`'s `L2-P1-T10` builds the reusable engine.

Charter DoD-16 requires `restore-production.yml` to run end to end (AT-103, spec L9352, verified present), and `L2-T703` executes AT-103 with deps `L2-T307, L2-T134` — neither of which is the engine. `L2-T144` asserts `recovery:` ⇒ `restore-production.yml` exists, for an engine no task creates.

**Correction.** Add `L2-T135` (`restore-production.yml` reusable engine, §44.5 L4016–4021 verified), or make `L2-T703`/`L2-T144` depend on `L2-01`'s `L2-P1-T10`. Also fill or document the `L2-T310` hole between `L2-T309` and `L2-T311`.

---

### H4 — `L2-01` stages every commit with `git add -A`, which `L2-07` forbids
**File:** `L2-01-reusable-workflows.md` lines 233, 389, 501, 615, 772, 983, 1120, 1237, 1439, 1608, 1793, 1903, 2028, 2161, 2289
**Task ids:** all 15 committing tasks (`L2-P1-T00`–`T14`)

Every `L2-01` task commits with `git add -A`. `L2-07-runbook.md:657` states the opposite rule verbatim: *"Stage ONLY owned paths. Never `git add -A`, never `git add .`, never `git commit -a`."* `L2-05` §0.3's close block likewise greps `git status --porcelain` for foreign paths before committing.

`git add -A` stages every untracked file in the working tree — including any stray artifact under `contracts/`, `schemas/` or `access/` — which is the exact failure mode `lane-guard` (`L2-T004`) exists to catch, and which the charter's STOP rule S5 forbids.

**Correction.** Replace all 15 occurrences with explicit `git add -- <path>` naming only the files the task creates, as `L2-00` and `L2-05` already do.

---

### H5 — Citation integrity: §99.2 subsystem rows E and F cited 12 lines off, landing on Lane 5's rows
**Files:** `L2-00-charter.md` §1.1, §3, §8.1; `L2-05-tasks.md` line 3
**Task ids:** lane-wide reading instruction

Cited throughout as *"§99.2 row E (L9204)"* and *"row F (L9205)"*. Verified against the spec:

- **L9192** = `| E | Reusable workflow library | ci, build, deploy-staging, … |` ✅ actual row E
- **L9193** = `| F | Evidence chain store and query | The eleven-question answerability … |` ✅ actual row F
- **L9204** = `| Q | Asset inventory and deadline watch | …` ❌ Lane 5's subsystem
- **L9205** = `| R | Notification routing | …` ❌ Lane 5's subsystem

The charter §15 instructs executors to read cited ranges with `sed -n 'A,Bp'`. An executor following the lane's own definition-of-surface citation reads Lane 5's asset-inventory and notification rows.

**Correction.** Global replace `L9204` → `L9192` and `L9205` → `L9193` in `L2-00` and `L2-05`.

---

### H6 — Citation integrity: seven of nine invariant line numbers in the charter are wrong
**File:** `L2-00-charter.md` §13 (and inherited by `L2-05` §0.6)
**Task ids:** every task citing an invariant

Invariant **text** is transcribed correctly everywhere. The **line numbers** are not:

| Invariant | Cited | Actual | Line cited actually holds |
|---|---|---|---|
| 18 | L9477 | L9477 | ✅ correct |
| 22 | L9483 | **L9484** | blank line |
| 23 | L9484 | **L9485** | invariant 22 |
| 27 | L9488 | **L9489** | invariant 26 |
| 28 | L9489 | **L9490** | invariant 27 |
| 71 | L9539 | **L9548** | invariant 65 (product split and merge) |
| 72 | L9540 | **L9549** | invariant 66 (product transfer) |
| 85 | L9558 | **L9565** | invariant 81 (auto-repair) |
| 87 | L9560 | **L9567** | blank line |

Invariants 71 and 72 are off by nine and point at entirely unrelated invariants. `L2-05` §0.6 inherits the wrong L9483/L9484 for invariants 22/23 but independently cites invariant 85 at **L9565, which is correct** — so the two documents disagree with each other as well as with the spec. `L2-06` cites invariant 25 at L9487 ✅ and invariant 18 at L9477 ✅.

**Correction.** Apply the Actual column to `L2-00` §13 and `L2-05` §0.6.

---

## MEDIUM DEFECTS

### M1 — "Sixteen published contexts" listed as fifteen
**File:** `L2-05-tasks.md` §0.5 (twice), `L2-00-charter.md` §11 A3
**Task id:** `L2-T003`
§0.5 says *"it is spelled exactly as it appears in … required-checks.yaml"*, *"If a task appears to need a context that is not one of the sixteen"*, then prints a block of **15** names. Same arithmetic error as B5. **Correction:** say fifteen, or add the sixteenth and update B5's assertions in lockstep.

### M2 — `L2-05` §0.1 undercounts its own editing tasks by half
**File:** `L2-05-tasks.md` §0.1
**Task ids:** `L2-T101`–`L2-T108`
§0.1 states *"Five tasks in this file deliberately edit a file created by an earlier task (`L2-T109`, `L2-T121`, `L2-T138`, `L2-T144`, `L2-T311`); every other task creates only."* The master table shows **eleven** tasks whose sole file is `.github/workflows/ci.yml`: `L2-T100` creates it and `L2-T101`–`T108`, `L2-T121`, `L2-T138` edit it — ten editing tasks, of which eight are unlisted. **Correction:** restate as ten and name them; this also serialises nine PRs through one file, which the merge-train section should acknowledge.

### M3 — Invariant 80 cited at the wrong line
**File:** `L2-05-tasks.md` §0.4
Cites the fail-closed rule as *"§101 invariant 80, L9556 area"*. L9556 is invariant **79** (minimum privilege); invariant 80 (*"Every control is explicitly classified fail-closed or fail-open"*) is at **L9557**. **Correction:** cite L9557 and drop "area".

### M4 — §15.7 range overshoots the section
**Files:** `L2-00-charter.md` §1.1 F-4, §8.2; `L2-05`
Cited as L1587–1606. §15.7 starts at L1587 ✅ but ends at **L1602**. **Correction:** cite L1587–1602.

### M5 — `L2-05` pre-ratifies two open L0 decisions and is written against them
**File:** `L2-05-tasks.md` §1
**Task ids:** `L2-T500` and every `tools/evidence/**` task; `L2-T300` and every template task
`D-L2-07` states *"This file is written assuming L0 ratifies: Python 3.12 …"* and `D-L2-08` *"assuming L0 ratifies: double-brace tokens `{{PRODUCT_NAME}}` …"*, with `L2-T500`'s STOP noting *"this whole file needs reissuing by L0"* if not. The STOP rules are correctly placed, but the entire 76-task list is conditional on two unmade decisions — which is a lane-level risk L0 must accept explicitly, not a defect the executor can absorb. **Correction:** obtain both rulings before dispatch.

### M6 — `L2-T131` acceptance criteria are not provable by its SELF-VERIFY
**File:** `L2-05-tasks.md`, task `L2-T131` — detailed under H1. **Correction:** replace the `grep -A4` heuristic with an ordered assertion (`assert_actor_gate_first`, `L2-T524`, already exists) and make criterion 1's ordering claim mechanically checkable.

---

## CHECKS THAT PASSED

| # | Check | Result |
|---|---|---|
| 1 | **Path-ownership violations** | ✅ **CLEAN.** Every `cat >`, `mkdir`, `touch` and `git add` target across all eight files lands in `.github/workflows/**`, `templates/workflows/**` or `tools/evidence/**`. The only foreign-path reference is `L2-06:863` `cp -R contracts/fixtures/core/. tools/evidence/tests/fixtures/` — a read of `contracts/**` copying *into* an owned tree, which PARTITION.md permits. `L2-05` §0.1 additionally forbids creating `tools/__init__.py`, correctly protecting Lane 3's and Lane 4's `tools/` siblings. Caveat: H4's `git add -A` weakens this in practice. |
| 2 | **Dangling dependencies** | ✅ **CLEAN.** Every id in a `Deps`/`Depends on` field resolves to a defined task block. Cross-file deps (`L2-02:113`→`L2-T006`, `L2-03:155`→`L2-T001/T002`, `L2-04:156`→`L2-T001`, `L2-06:539`→`L2-T001`) all resolve. Ids `L2-T099/199/239/299/399/499/599/649/699/799` appear only as range boundaries in reservation tables, not as dependencies. |
| 3 | **Missing controls** | ✅ **CLEAN.** All **161** task blocks across all eight files carry a SELF-VERIFY block, a STOP rule and an acceptance-criteria table. Zero exceptions. |
| 6 | **Citation integrity — sections, ATs, SIGs, Ds** | ✅ **MOSTLY CLEAN.** Section ranges verified exact for §32 (2803–2828), §33.2 (2854–2869), §33.4 (2887–2912), §27.2 (2567–2576), §34.2 (2930–2935), §31.2 (2787–2794), §37.3 (3261–3268), §46.1 (4090–4131), §48.1 (4300–4308), §53.1 (4653–4689), §97.2 (8843–8926) — 11 of 12, with §15.7 off (M4). **AT-024** (L9338), **AT-029** (L9343), **AT-035** (L9349), **AT-103** (L9352) all exist with matching text. **SIG-12/14/17/18/34/42** all exist inside the §52.2 table (L4530–4576, within the cited 4520–4587). **D5, D53, D69, D71, D73, D74, D78, D80, D87, D89, D91, D95, D97, D101, D107** all exist in Appendix A with matching subject matter. `L2-03`'s verbatim §37.3 quote at L3267 is exact. **Nothing invented** — the failures (H5, H6, M3, M4) are all line-number drift, not fabricated identifiers. |
| 5 | **Judgment leakage** | ⚠️ **PARTIAL.** No task asks the executor to *choose* a name, threshold or format without a STOP — the S1–S5 discipline is applied consistently and the open decisions are correctly routed to L0. But `L2-05` requires the executor to *author* 75 artifacts from prose (H1), which is design work in all but name. Not applicable: the ASSISTED-marking rule is L5-specific; Lane 2 requires no credentials or console access, and `L2-06`'s `D-L2-11` correctly fails closed with `SANDBOX_ORG_UNRESOLVED` rather than asking the executor to obtain an org. |

---

## MINIMUM SET TO UNBLOCK

1. **B1** — L0 declares one decomposition normative; the other becomes an index.
2. **B2** — Re-number the 23 colliding ids; re-point `L2-06` lines 72, 1140, 1246, 1738.
3. **B3** — Single `D-L2-nn` register; rewrite all references.
4. **B4** — Fold `L2-P1-T00`–`T15` into the charter §12 bands, or demote `L2-01` to rationale.
5. **B5** — Fix the 15/16 arithmetic in `L2-00` §11 and `L2-05` §0.5.
6. **B6** — One implementation form per gate; delete the losing tasks.
7. **H1–H4** — Back-fill literal content, add the D87 runner-tier task, add `L2-T135`, replace 15× `git add -A`.
8. **H5, H6, M1–M6** — Mechanical citation and arithmetic corrections.

Items 1–6 are the dispatch gate. Until they close, two agents given this lane will write different files under the same task id.

---

# RESOLUTION LOG — B2, TASK-ID COLLISIONS

**Applied:** 2026-08-27 · **Scope:** defect **B2** only (23 ids bound to two different tasks). B1, B3, B4, B5, B6 and H1–H6 are untouched and still gate dispatch.

## The rule applied

**The phase file holds the authoritative body; the tasks file holds an index entry that points at it.** This is the pattern Lane 4 already uses (`L4-06-tasks.md` §2 is a master table over `L4-P1-*`/`L4-P2-*` ids whose bodies live in the phase files) and it is now Lane 2's rule too.

For each colliding id the phase-file definition was kept **where it sits** — it carries the literal heredoc content, which the `L2-05` twin does not (review H1: `L2-04` 41 heredocs / 17 tasks, `L2-02` 17 / 18, `L2-05` **1** / 76). The `L2-05` body under that id names *different* work, so it was **not deleted**: it was renumbered, unchanged in substance, into free slots of the charter §12 `tools/evidence/**` band (`L2-T500`–`L2-T699`, ~40 of 200 slots used). Every renumbered block now opens with a one-line index entry naming the file and section that owns the old id, and `L2-05-tasks.md` §2.1 carries the full index table.

## Ownership after the change — one owner per id

| Id | Owner (authoritative body) | Title there | `L2-05`'s different work, renumbered to |
|---|---|---|---|
| `L2-T500` | `L2-04-evidence-chain.md` §6 | Phase-4 branch and the `tools/evidence` module skeleton | `L2-T530` Evidence toolchain skeleton |
| `L2-T501` | `L2-04-evidence-chain.md` §6 | Pin the phase-4 consumed contract surface | `L2-T531` Action-pin resolver and applier |
| `L2-T502` | `L2-04-evidence-chain.md` §6 | Author `tools/evidence/eleven-questions.yaml` | `L2-T532` Action pin ledger |
| `L2-T503` | `L2-04-evidence-chain.md` §6 | Author the fixture estate | `L2-T533` Workflow lint |
| `L2-T504` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/evidence-query` | `L2-T534` Required-context ↔ job cross-check |
| `L2-T505` | `L2-04-evidence-chain.md` §6 | Conformance-profile substitution, S18 equivalence | `L2-T535` Run-conclusion assertor |
| `L2-T506` | `L2-04-evidence-chain.md` §6 | `verify-digest-chain` comparison core | `L2-T536` Delta-gate engine |
| `L2-T507` | `L2-04-evidence-chain.md` §6 | `tools/evidence/collect-version.sh` | `L2-T537` Negative-test harness for the two guards |
| `L2-T508` | `L2-04-evidence-chain.md` §6 | `tools/evidence/build-deployment-record.sh` | `L2-T538` SBOM-beside-digest assertion |
| `L2-T509` | `L2-04-evidence-chain.md` §6 | `.github/workflows/emit-deployment-record.yml` | `L2-T539` Template renderer and placeholder lint |
| `L2-T510` | `L2-04-evidence-chain.md` §6 | Wire the emitter into the two deploy workflows | `L2-T540` Time gate |
| `L2-T511` | `L2-04-evidence-chain.md` §6 | `.github/workflows/verify-digest-chain.yml` sweep | `L2-T541` Actor gate |
| `L2-T512` | `L2-04-evidence-chain.md` §6 | The P0 escalation path | `L2-T542` Workflow-identity gate |
| `L2-T513` | `L2-04-evidence-chain.md` §6 | `tools/evidence/deploy-gate.sh` | `L2-T543` Digest invariant |
| `L2-T514` | `L2-04-evidence-chain.md` §6 | `.github/workflows/evidence-selftest.yml` | `L2-T544` Records-write client |
| `L2-T515` | `L2-04-evidence-chain.md` §6 | Append-only and effective-dating assertion | `L2-T545` Event writer |
| `L2-T516` | `L2-04-evidence-chain.md` §6 | Phase-4 roll-up and lane PR | `L2-T546` Verification-contract check |
| `L2-T520` | `L2-02-digest-invariant.md` §3 | Branch, and the flat-record reader | `L2-T550` `verify-digest-chain` sweep |
| `L2-T521` | `L2-02-digest-invariant.md` §3 | The artifact-identity format library | `L2-T551` `/version` digest-match monitor |
| `L2-T522` | `L2-02-digest-invariant.md` §3 | Compute the S18 platform-rebuild identity (D78) | `L2-T552` Restore-rotation scheduler |
| `L2-T523` | `L2-02-digest-invariant.md` §3 | THE DIGEST INVARIANT | `L2-T553` The eight "shipped" conditions |
| `L2-T524` | `L2-02-digest-invariant.md` §3 | Artifact publication check, never-rebuild rule | `L2-T554` Actor-gate-is-step-0 assertion |
| `L2-T525` | `L2-02-digest-invariant.md` §3 | SBOM beside the digest | `L2-T555` DoD acceptance matrix and lane handoff |

Unchanged and uncontested: `L2-T517`–`L2-T519` are `L2-05`'s alone; `L2-T526`–`L2-T528` are `L2-02`'s alone.

## `L2-T171`–`L2-T173` — no collision existed

The brief listed these as defined in both `L2-03-production-gates.md` and `L2-06-tests.md`. **They are not.** `L2-03` §7 defines all three (lines 257, 477, 643). `L2-06` defines **no** task body for any of them — it cites them by id in §8 N3/N4/N5 and in the `L2-T607`/`L2-T608`/`L2-T609` STOP rules ("Tokens are those fixed by `L2-03-production-gates.md` `L2-T172`"), which is already the index form this resolution installs everywhere else. No body was moved. `L2-03` §1 now states the ownership explicitly so the next reader does not re-open the question.

This also revises the headline count: the collision set is **23 ids, not 32** — matching B2's own tally, not the brief's.

## Files changed

| File | Change |
|---|---|
| `L2-05-tasks.md` | **Primary.** 23 ids renumbered (`L2-T500`–`516` → `530`–`546`; `L2-T520`–`525` → `550`–`555`) across 208 occurrences plus branch slugs; new §2.1 index table; one-line index entry inserted at the head of each of the 23 renumbered blocks; §10 note 2 rewritten (it asserted the opposite rule — that §2 was the execution authority over a colliding phase-file id); intro paragraph points at §2.1. |
| `L2-06-tests.md` | §1 reservation rewritten as a one-owner-per-range table (it had claimed `L2-T500`–`528` was reserved by two documents at once); stale bindings re-pointed — `L2-T512`→`L2-T542`, `L2-T513`→`L2-T543`, `L2-T502`→`L2-T532` (×2, including the `action-pins.txt ABSENT` STOP string); the `L2-T171`–`173` citations left as they stand and documented as correct. |
| `L2-04-evidence-chain.md` | §5 opens with an authority note for `L2-T500`–`L2-T516`. No task body touched. |
| `L2-02-digest-invariant.md` | §0.2 gains an authority note for `L2-T520`–`L2-T528`. No task body touched. |
| `L2-03-production-gates.md` | §1 gains an authority note covering `L2-T171`–`L2-T173`. No task body touched. |

## Verification

A heading-level scan of all eight `L2-*.md` files finds **154 task bodies and no id defined in more than one file** within the B2 set. Nothing was deleted: `L2-05`'s task count is still 76 and every block it previously held is present under its new id.

## Still open — not resolved here, and one new finding

- **B1, B3, B4, B5, B6, H1–H6, M1–M6** are untouched. B2 closing does not unblock dispatch on its own.
- **Six further duplicate bodies, outside the brief:** `L2-T001`–`L2-T006` carry a full body in **both** `L2-00-charter.md` §11 and `L2-05-tasks.md` §3 — and unlike the 23 above, these are the *same* work in both files. They were deliberately left alone. Choosing an owner here is not a mechanical de-duplication: it is B1 (which decomposition is normative for the lane) and it is entangled with B5 (the charter's `L2-T003` SELF-VERIFY can never print OK, while `L2-05`'s copy of the same task is correct). Picking a winner silently would be the judgment leakage rule S4 exists to prevent. **L0 decides**, then the losing side becomes six index rows by the same pattern used above.
