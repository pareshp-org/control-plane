# 11 — DEFINITION OF DONE

**Status:** binding at every level named below. Conforms to the FROZEN PARTITION
(`C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md`). Does not redesign it.

**Spec basis:** `Research/MultiProduct_MasterSpec_v4.0.md` — §31.2 (a verification contract that cannot fail
is not a contract), §53.1 (the seeded-canary rule and the independent control verifier), §53.7 (the
control-loop gap procedure), §95.3 (what remains binding even in bootstrap), §95.4 (the activation
checklist, executed for real including the negative tests), §96.2/§96.4/§96.6 (pre-onboarding, adoption
health, the universal floor), §98.2 (Foundation Phases 1–7 and their completion checks), §99.4 (the minimal
honest V1), §100 (AT-001 … AT-110), §101 (invariants 1 … 111), §102 (EC-1 … EC-112), §103.13 (operating
system success criteria), §103.14 (baselines before Phase 1).

**Reads with, and never contradicts:**

| File | What it owns that this file only cites |
|---|---|
| `protocol/00-test-strategy.md` | The T0–T4 pyramid, the exit-code vacuity contract, the `GATE-RESULT` line, the five fixed lane entry points |
| `protocol/01-contract-tests.md` | The contract register C-01…, `make contract-test`, the negative-proof suite |
| `protocol/05-merge-gate.md` | GATE A (`LG-01`…`LG-12`), GATE B (`IG-01`…`IG-12`), the 24-check negative battery, `COUNTS.tsv` |
| `protocol/06-integration-cycle.md` | The cycle clock, `make train-*`, the fourteen `CAN-*` canaries |
| `protocol/07-rollback.md` | R1–R4 — what happens when a DoD claim is withdrawn after the fact |
| `protocol/08-smoke-and-e2e.md` | `e2e/run.sh`, `e2e/verdict.sh`, the 118 positive / 28 negative checkpoint floors |
| `protocol/09-fixtures.md` | `make fixtures-all`, the fixture canary, the four meta-gates |
| `manual/10-quality-bar.md` | The AI developer's own eight-gate task bar (G1–G8) and the completion report shape |
| `master/00-MASTER-PLAN.md` §5 EC-16 | `make decisions-gate` — all Phase 0-gated `REG-` entries must be closed before B-Day; cited here so this DoD file is not the only document that omits it (cross-reference: `master/05-entry-exit-criteria.md` L0P0-E6, `lanes/L0-04-decisions-register.md` §3) |
| `master/00-MASTER-PLAN.md` §6 | `make dod-v1`, `make dod-foundation` — this file is the superset those two targets live inside |
| `master/08-progress-tracking.md` | The task ledger schema, the nine-value derived status enum, `verify-task.sh` |

**This file adds nothing new to those. It states, for each of six levels, the checklist that closes the
level, the one command that proves it, and the one command that proves the checklist could have failed.**

---

## 0. The one rule

> **Nothing is done because someone says it is done.**
> §96.6: *"a floor declared done on paper is exactly the invisible half-adoption 96.4 exists to catch."*
> §95.4: *"The checklist is executed for real — including the negative tests — at each threshold, not assumed."*

Done is a **verdict line printed by a command**, on a named revision, recorded in an append-only file
(Spec §101 #47). It is never a status field a lane sets, never a percentage, never a report paragraph, never
the absence of a red mark. The task ledger has no `status:` key for exactly this reason
(`master/08-progress-tracking.md` §2.3), and this file extends that discipline upward through five more
levels.

### 0.1 The six levels

| # | Level | Unit | Closed by | Verdict token | Proving command | Negative proof |
|---|---|---|---|---|---|---|
| 1 | **TASK** | one ledger task, one branch | the lane AI developer, then re-derived by L0 | `DOD-VERDICT=MET LEVEL=task` | `make dod-task TASK=<id>` | `make dod-negative LEVEL=task TASK=<id>` |
| 2 | **PHASE** | one build-track phase `BT-0`…`BT-4` for one lane | L0 at the sync point | `DOD-VERDICT=MET LEVEL=phase` | `make dod-phase PHASE=<BT-n> LANE=<N>` | `make dod-negative LEVEL=phase PHASE=<BT-n>` |
| 3 | **LANE** | all of one lane's owned paths, all phases | L0 | `DOD-VERDICT=MET LEVEL=lane` | `make dod-lane LANE=<N>` | `make dod-negative LEVEL=lane LANE=<N>` |
| 4 | **INTEGRATION** | one merge-train cycle on `integration` | L0 integrator | `DOD-VERDICT=MET LEVEL=integration` | `make dod-integration CYCLE=<id>` | `make dod-negative LEVEL=integration CYCLE=<id>` |
| 5 | **V1** | the nine §99.4 items on `main` | L0 integrator + Founder | `DOD-VERDICT=MET LEVEL=v1` | `make dod-v1` | `make dod-negative LEVEL=v1` |
| 6 | **PROGRAMME** | Foundation tier complete across the live portfolio | Founder, as a decision record | `DOD-VERDICT=MET LEVEL=programme` | `make dod-programme` | `make dod-negative LEVEL=programme` |

**Levels are preconditions, never substitutes.** A phase is not done because its tasks are; a lane is not
done because its phases are; V1 is not done because the lanes are. Each level asserts something that only
exists at that level, and §1.3 names it for each.

### 0.2 Where `make` lives, and why no lane can move it

`Makefile` is an L0 root file (PARTITION line 22). Every `dod-*` target is authored by L0 at BT-0 and is
outside every lane's owned paths. A lane cannot change what "done" means for its own work — the same
property §53.1 requires of the reconciler: *"no control that can be rewritten by the credential it is
checking is a control."*

`contracts/dod/**` holds the checklists, the frozen expectation files and the negative mutations. It is
inside `contracts/**`, which PARTITION rule 2 freezes at Phase 0. A PR from any lane touching it fails
`LG-03` (contract immunity) before any other check runs.

---

## 1. The doctrine — a DoD that can only be met is not a DoD

This is Rule Zero of `protocol/05-merge-gate.md` §1, applied to completion rather than to merging. The
specification states the principle in five places and every one of them is load-bearing here:

| Where | What it says | What it forces on this file |
|---|---|---|
| §53.1, the seeded-canary rule | *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking."* | Every DoD level has a planted thing it must find. A level that finds nothing has not been checked. |
| **AT-102** | *"A reconciler that finds nothing is assumed broken, never assumed clean."* | `DI-06` and `DV-08` assert `canary=FOUND` **by name**, separately from the verdict. |
| §31.2 | *"A verification contract that cannot fail is not a contract."* Every `verification/contract.yaml` declares a seeded-defect case the contract MUST fail; a run in which the seeded defect passes is a FAILED run and raises **SIG-18**. | `DT-06`, `DL-05` and `DV-05` require the seeded defect to be **DETECTED**, not merely for the suite to be green. |
| §103.13 / §103.1 (plan-checker row) | *"Watch the reason mix, not the rate. Zero rejections means the gates are not working."* | `DL-09`, `DI-09` and `DG-08` are escape and rejection instruments: a level with no rejections over its window is flagged, not congratulated. |
| §103.9 (review row) | *"Very low may mean rubber-stamping; very high may mean weak plans."* | The same flag applies to human review at every level, and a flagged window forces a written named answer on the record. |
| **EC-109** | A silently-vacuous run — *"Silence is never taken as health."* | Exit code `2` (VACUOUS) from any DoD check is a FAIL, not a pass. `protocol/00-test-strategy.md` §3 owns the code table. |

### 1.1 The three binding rules

1. **Every DoD check has a paired negative mutation** that makes it flip to NOT-MET. A check whose
   mutation does not flip it is reported `unproven`, and an unproven check is treated as **absent** — the
   level fails closed (Spec §101 #80: every control is explicitly classified fail-closed or fail-open; every
   check in this file is fail-closed).
2. **No output is NOT-MET.** An empty result, a crashed script, a timeout, a `skipped` or `neutral`
   conclusion on a required context, exit code `2` or `3` — all read as NOT-MET. MET is only ever an exact
   verdict line.
3. **Zero escapes over a window is itself a finding.** A level that has never rejected anything, and a
   level whose downstream has never caught anything it declared done, are reported `suspect=1` on the
   record. The flag does not by itself close the level; it forces a named written answer.

### 1.2 The escape ledger — the instrument that catches a level marking its own exam

An **escape** is a thing declared MET at level *n* that a check at level *n+1* subsequently rejected. Every
level records its escapes into `records/dod/escapes/<level>/<date>-<id>.yaml` (directory-per-item,
PARTITION rule 3, so five lanes never conflict).

```bash
set -euo pipefail
# contracts/dod/escape-rate.sh — read-only. Prints one line. Run by any level's DoD target.
# Usage: bash contracts/dod/escape-rate.sh --level lane --window 10
set -uo pipefail
LEVEL="$2"; WINDOW="$4"
# §9 layout: records/dod/closures/<level>/<date>/<file>.yaml — extra glob star for date subdirectory.
mapfile -t _wf < <(ls -1 "records/dod/closures/${LEVEL}"/*/*.yaml 2>/dev/null | sort | tail -n "$WINDOW")
closed=${#_wf[@]}
# §9 layout: records/dod/escapes/<level>/<date>/<file>.yaml — extra glob star for date subdirectory
# (see §9's own worked example, records/dod/escapes/lane/2026-09-02/L3-DL-04-esc-011.yaml).
esc=$(ls -1 "records/dod/escapes/${LEVEL}"/*/*.yaml 2>/dev/null | wc -l | tr -d ' ')
# Rejections counted only within the window (last $WINDOW closures by date-sort, not all-time).
rej=0
[ "$closed" -gt 0 ] && rej=$(grep -l 'verdict: NOT-MET' "${_wf[@]}" 2>/dev/null | wc -l | tr -d ' ')
flag=0
[ "$closed" -ge "$WINDOW" ] && [ "$rej" -eq 0 ] && flag=1
echo "ESCAPE-RATE level=${LEVEL} window=${WINDOW} closures=${closed} rejections=${rej} escapes=${esc} suspect=${flag}"
```

**Paired negative** — a rejection record older than the window is not counted as a rejection:

```bash
# Seed: window=2, three closure records, oldest carries verdict: NOT-MET.
# Directory layout follows §9: records/dod/closures/<level>/<date>/<file>.yaml
mkdir -p records/dod/closures/lane/2026-01-01 records/dod/closures/lane/2026-06-01 records/dod/closures/lane/2026-09-01
printf 'verdict: NOT-MET\n' > records/dod/closures/lane/2026-01-01/r1.yaml   # OLD — outside window
printf 'verdict: MET\n'     > records/dod/closures/lane/2026-06-01/r2.yaml
printf 'verdict: MET\n'     > records/dod/closures/lane/2026-09-01/r3.yaml
bash contracts/dod/escape-rate.sh --level lane --window 2
# Expected: closures=2 rejections=0 (2026-01-01 record excluded by tail -n 2)
# Bug (pre-fix): glob *.yaml matched nothing; all-time grep counted the old rejection.
```

| Reading | Meaning | Action |
|---|---|---|
| `rejections=0` over a full window | Nothing was ever refused at this level | `suspect=1`. Write the named explanation on the closure record. §103.13, plan-checker row. |
| `escapes=0` **and** `rejections=0` | The level neither refuses nor is ever caught refusing wrongly | Same flag, higher severity: the level may be decorative. L0 runs one deliberate escape drill (§1.4). |
| `escapes` rising | The level is passing broken work downstream | The level's checklist is missing a check. Add the check **and its negative mutation in the same PR** (`protocol/06-integration-cycle.md` §6: *"Adding a gate adds a canary in the same PR."*). |
| `escapes=0`, `rejections>0` | Healthy | None. |

### 1.3 What each level asserts that no other level can

Stated once, so nobody argues that a higher level "already covers" a lower one.

| Level | The property only this level can observe |
|---|---|
| TASK | The task's own acceptance commands produce their **exact** declared stdout on this working tree |
| PHASE | The §98.2 completion check for the phase passes **as written**, including its negative clauses, on the sync-point tip |
| LANE | The lane's whole owned tree is internally consistent and complete against its charter DoD table — the check that no single task can make true |
| INTEGRATION | The five lanes compose: contract tests run provider-to-consumer against **real** output, not stubs; the canaries fire from `main`'s checkout against `integration` |
| V1 | The nine §99.4 items do the four things V1 claims end to end on one pilot product — declared state enforced, drift visible, orphans impossible to miss, every production artifact traceable |
| PROGRAMME | Every live product is at the §96.6 target standard, and the operating system's own success measures have baselines (§103.14, AT-046) |

### 1.4 The deliberate escape drill

Once per phase L0 injects one defect that **should** be caught at a named level, allows it through the level
below, and records whether the level catches it. This is §95.4's discipline — *executed for real, not
assumed* — applied to the DoD itself.

```bash
# L0 only. Never run by a lane. Writes records/dod/drills/<date>-<level>.yaml
make dod-drill LEVEL=integration DEFECT=CAN-NARROW
# DOD-DRILL level=integration defect=CAN-NARROW injected=1 caught=1 caught_by=DI-06 latency_checks=1
```

`caught=0` closes the level until the missing check exists. A drill that is never run leaves the level's
`suspect` flag permanently raised.

---

## 2. LEVEL 1 — TASK DONE

**Unit:** one ledger file under the task-ledger schema of `master/08-progress-tracking.md` §2.3.
**Owner:** the lane AI developer.
**Re-derived by:** L0, after merge, which is what turns ledger status `integrated` into `accepted`.

### 2.1 The checklist

| # | Check | What it proves | Pass output (exact) |
|---|---|---|---|
| DT-01 | Ledger conformance | The task was issued under a lint-clean ledger file; no `status:`/`percent:`/`updated_by:` key exists | `DT-01 ledger PASS task=<id> lint=OK forbidden_keys=0` |
| DT-02 | **Every** acceptance criterion MET | Each `acceptance[].command` produced its exact `expect` string — all of them, not a subset | `DT-02 acceptance PASS criteria=<n>/<n> exact=<n> partial=0` |
| DT-03 | **Negative criterion fired** | At least one acceptance criterion is a negative test and it produced `REJECTED`, not `UNEXPECTED-PASS` (ledger rule 2, §95.4) | `DT-03 negative PASS negatives=<n> fired=<n> unexpected_pass=0` |
| DT-04 | Completeness | No banned token in any file the task wrote: `TODO`, `FIXME`, `CHANGEME`, `NotImplementedError`, `pass  # `, `...`, `your-org`, `example.com`, `0.0.0` | `DT-04 complete PASS files=<n> banned_tokens=0` |
| DT-05 | Runnable / parseable | Every file the task wrote parses or executes under its own toolchain, named in `toolchain:` | `DT-05 runnable PASS files=<n> unparseable=0 toolchain=<binary>` |
| DT-06 | Seeded-defect discrimination | Where the task ships a suite or a validator, its seeded-defect case still **fails** (§31.2) | `DT-06 seeded PASS cases=<n> detected=<n> passed_wrongly=0` |
| DT-07 | Path ownership | Every changed path is in `owns_paths:` and inside the lane's PARTITION prefix | `DT-07 paths PASS changed=<n> foreign=0 outside_owns=0` |
| DT-08 | No narrowing | The count of things the criterion enumerates equals the count of things delivered | `DT-08 narrowing PASS declared=<n> delivered=<n> ratio=1.00` |
| DT-09 | Self-verify | `self_verify:` ran and exited 0, with output pasted verbatim from this session | `DT-09 self-verify PASS exit=0 command=<path>` |
| DT-10 | Blocker honesty | Every item the task could not do is an open blocker issue titled `<task-id> …`, not a silent omission | `DT-10 blockers PASS unreported_gaps=0 open_blockers=<n>` |

`DT-01`…`DT-10` are the mechanical form of the eight gates in `manual/10-quality-bar.md` §10.1. That file
is what the developer reads; this table is what the machine runs. They do not disagree: G1→DT-02, G2→DT-04,
G3→DT-05, G4→DT-01, G5→DT-08, G6→DT-09, G7→DT-07, G8→DT-10, with DT-03 and DT-06 added because a checklist
with no negative limb is exactly what this protocol exists to forbid.

### 2.2 The proving command

```bash
set -euo pipefail
# From the control-plane repository root, on the task's branch, after rebasing on integration.
export CP="$PWD"
git fetch origin integration
git rebase origin/integration

make dod-task TASK=L1-F0-003
```

`make dod-task` runs `DT-01` … `DT-10` in order, writes every per-check line to `.dod/task.log`, and prints
**exactly one line** on stdout:

```
DOD-VERDICT=MET LEVEL=task ID=L1-F0-003 LANE=1 HEAD=9f2c1ab checks=10/10 negatives=10/10 criteria=7/7 escapes=0 ts=2026-08-27T11:04:19Z
```

**The unambiguous test — this and nothing else:**

```bash
set -euo pipefail
mkdir -p .dod
make dod-task TASK=L1-F0-003 | tee .dod/task.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=task' .dod/task.stdout \
  && grep -Fq 'negatives=10/10' .dod/task.stdout \
  && test "$(wc -l < .dod/task.stdout)" -eq 1 \
  && echo TASK-DONE || echo TASK-NOT-DONE
```

`TASK-DONE` is the only string that authorises opening a PR. Anything else — including no output at all —
means the task is `BLOCKED`, which is a legitimate, cheap, correct outcome.

### 2.3 The negative proof — proving DT-01…DT-10 can fail

```bash
make dod-negative LEVEL=task TASK=L1-F0-003
# DOD-NEGATIVE level=task proven=10/10 unproven=0
```

Each mutation runs in a throwaway worktree and is restored. Any `unproven` value other than `0` means the
task is NOT done regardless of how green the positives are.

| Check | Mutation injected | Required result |
|---|---|---|
| DT-01 | Add `status: done` to a copy of the ledger file | `DT-01 … FAIL forbidden_keys=1` |
| DT-02 | Change one `expect:` string by one character | `DT-02 … FAIL criteria=6/7 exact=6` |
| DT-03 | Make the negative fixture valid so the validator accepts it | `DT-03 … FAIL unexpected_pass=1` |
| DT-04 | Append `# TODO: wire this up` to one written file | `DT-04 … FAIL banned_tokens=1` |
| DT-05 | Truncate one written file mid-token | `DT-05 … FAIL unparseable=1` |
| DT-06 | Repair the seeded-defect case so the suite goes green on broken input | `DT-06 … FAIL passed_wrongly=1` |
| DT-07 | `touch` one path outside `owns_paths:` | `DT-07 … FAIL outside_owns=1` |
| DT-08 | Delete one of the enumerated deliverables | `DT-08 … FAIL declared=7 delivered=6 ratio=0.86` |
| DT-09 | Point `self_verify:` at a script that exits 1 | `DT-09 … FAIL exit=1` |
| DT-10 | Close the blocker issue for an item the task did not deliver | `DT-10 … FAIL unreported_gaps=1` |

### 2.4 DT-08 stated exactly — the anti-narrowing check

Five AI developers with no shared context fail in one characteristic way: the task says *"a rule file plus
an invalid fixture for each of the eleven rules in §15.5"* and the lane ships three, because nothing anywhere
holds the number eleven. The ledger holds it, in the criterion text, and `DT-08` extracts it:

```bash
set -euo pipefail
# contracts/dod/narrowing.sh --task <id>
# Every acceptance criterion whose text contains a cardinal ("eleven", "each of the", "every")
# must declare an explicit count in the ledger as `enumerates: <n>`. L0 rejects at issuance otherwise.
declared=$(yq -r '.acceptance[].enumerates // 0' "docs/plan/ledger/${TASK}.yaml" | awk '{s+=$1} END{print s+0}')
delivered=$(bash "docs/plan/bin/count-deliverables.sh" "${TASK}")
[ "$declared" -eq "$delivered" ] \
  && echo "DT-08 narrowing PASS declared=${declared} delivered=${delivered} ratio=1.00" \
  || echo "DT-08 narrowing FAIL declared=${declared} delivered=${delivered}"
```

**STOP rule.** If `declared` and `delivered` disagree, the fix is to deliver the missing items or open a
blocker naming them. The fix is never to lower `enumerates:` — that field is L0's, written at issuance, and
editing it is a foreign-path change that fails `LG-03`.

### 2.5 Task done is not task accepted

| Ledger status | What it means | Who derives it |
|---|---|---|
| `in-review` | `TASK-DONE` printed; PR open | lane |
| `integrated` | PR merged to `integration` | merge train |
| **`accepted`** | `make dod-task` re-run against `integration` **head after the merge** exits MET | derived, by L0 |
| `released` | the merge commit is an ancestor of `origin/main` | L0 |

`master/08-progress-tracking.md` §3.1 is explicit: *"`accepted` is the only status that means anything."*
A task that is MET on its own branch and NOT-MET on `integration` head is an **escape** — recorded under
§1.2, counted against the TASK level, and routed to the lane as a new task, never as a silent fix.

---

## 3. LEVEL 2 — PHASE DONE

**Unit:** one build-track phase (`BT-0` … `BT-4`, `master/04-phase-map.md` §2) for one lane.
**Owner:** L0, at the sync point (`S0` … `S4`).
**Rule:** *no lane opens a branch for the next phase until L0 declares the sync point passed.*

### 3.1 The checklist

| # | Check | What it proves | Pass output (exact) |
|---|---|---|---|
| DP-01 | Every issued task `accepted` | No task of this phase for this lane sits at any status below `accepted` | `DP-01 tasks PASS phase=<BT-n> lane=<N> issued=<n> accepted=<n> below=0` |
| DP-02 | **Spec completion check executed as written** | The §98.2 completion check for the mapped spec phase ran, including every negative clause, with its result recorded | `DP-02 completion-check PASS spec_phase=<n> clauses=<n> executed=<n> asserted_only=0` |
| DP-03 | Sync-point cleanliness | The five lines of `master/04-phase-map.md` §4.1 each produced their exact expected output | `DP-03 sync PASS open_prs=0 ci=success ff=FF-OK unmerged=0 required_reported=0-missing` |
| DP-04 | Required-check honesty | Every status-check context this phase added is in branch protection **and** was actually reported by a run | `DP-04 required-checks PASS added=<n> in_protection=<n> reported=<n> missing=0` |
| DP-05 | **Sync-point negative executed** | The negative column of `master/04-phase-map.md` §4.3 for this sync ran for real and failed as required | `DP-05 sync-negative PASS cases=<n> failed_correctly=<n> unexpected_pass=0` |
| DP-06 | Phase AT set executed | Every AT scheduled at or before this phase was executed with a recorded result, never asserted | `DP-06 at PASS scheduled=<n> executed=<n> not_run=0 asserted_only=0` |
| DP-07 | Phase invariant set armed | Every invariant this phase arms names a live check or a real AT id, or is explicitly recorded as unarmed (D77) | `DP-07 invariants PASS armed=<n> dangling=0 unrecorded=0` |
| DP-08 | Blocker ledger clear | No open blocker issue names this phase for this lane, or each one carries an L0 decision record deferring it | `DP-08 blockers PASS open=0 deferred_with_record=<n> undecided=0` |
| DP-09 | Escape rate | The phase level has refused something over its trailing window | `DP-09 escape-rate PASS window=5 rejections=<n> escapes=0 suspect=0` |

### 3.2 The spec completion checks, quoted — never paraphrased

`DP-02` compares against `contracts/dod/completion-checks/<spec-phase>.txt`, which L0 transcribes verbatim
at BT-0 from the spec lines below. A lane may not edit those files.

| Phase | Spec | Line | Completion check (the clause set `DP-02` enumerates) |
|---|---|---|---|
| `BT-1` | §98.2 Phase 1 | 9037 | no direct human push to any default branch succeeds; a Read-only approval does **not** satisfy protection while a Write-holding Cross-Reviewer approval does; an approval from a machine account does **not** satisfy it and CODEOWNERS is generated to contain human identities only, *"and the check is executed negatively"*; 2FA active with hardware keys/passkeys; **no API key present anywhere**; the minimal `exceptions.yaml` validator active in control-plane CI and *"rejects a deliberately malformed exception"*; Teams granting Write exist **before** protection is armed; a workflow on a non-default branch declaring `environment: production` obtains no environment secret, *"executed negatively"*; a second Owner or escrowed break-glass credential with a named escrow custodian; the org export's first run scheduled or recorded as a dated accepted risk |
| `BT-1` | §98.2 Phase 2 | 9048 | every product visible in Grafana with a Scorecard score; control-plane surfaces reachable only over the §51.4 private path, or carried as a dated `policy_waiver`; every live product either onboarding or in declared pre-onboarding mode with a deadline |
| `BT-2` | §98.2 Phase 3 | 9061 | *"contracts validate; registries, contracts and Team membership agree, machine-verified"* |
| `OT-P4` | §98.2 Phase 4 | 9070 | `make setup && make dev && make test` succeeds for someone unfamiliar with the product; `make parity` reports no divergence; every required file of §33.1 present, `AGENTS.md` included; the contexts this phase adds are in branch protection **and actually reported by a run** |
| `OT-P5` | §98.2 Phase 5 | 9081 | verification contract present and passing; QA signed off, under the §96.6 QA-takeover SLA — a breach is a QA-capacity signal, never a personal one |
| `BT-3` / `OT-P6` | §98.2 Phase 6 | 9091 | a deliberate rollback succeeded in staging; restore test recorded; the eleven-item evidence chain answerable for one real deployment; the production-approval test verifies the workflow-identity gate and *"the deploy fails closed when the approver equals the deploying actor"* |
| `OT-P7` | §98.2 Phase 7 | 9100 | a first plan passes the plan-checker and is approved at Gate 1 |

**`DP-02` counts clauses, not sentences.** A completion check with nine clauses and eight recorded results
is NOT-MET at `executed=8`, and the missing clause is named on the record. This is the count-integrity
discipline of `protocol/05-merge-gate.md` §8 applied to prose.

### 3.3 The proving command

```bash
set -euo pipefail
git fetch origin --prune
git checkout integration && git reset --hard origin/integration

make dod-phase PHASE=BT-2 LANE=3
```

```
DOD-VERDICT=MET LEVEL=phase PHASE=BT-2 LANE=3 SYNC=S2 HEAD=4bd90fe checks=9/9 negatives=9/9 tasks=14/14 clauses=3/3 escapes=0 ts=2026-08-27T16:40:02Z
```

```bash
set -euo pipefail
mkdir -p .dod
make dod-phase PHASE=BT-2 LANE=3 | tee .dod/phase.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=phase' .dod/phase.stdout \
  && grep -Fq 'negatives=9/9' .dod/phase.stdout \
  && grep -Fq 'asserted_only=0' .dod/phase.log \
  && test "$(wc -l < .dod/phase.stdout)" -eq 1 \
  && echo PHASE-DONE || echo PHASE-NOT-DONE
```

### 3.4 The negative proof

```bash
make dod-negative LEVEL=phase PHASE=BT-2
# DOD-NEGATIVE level=phase proven=9/9 unproven=0
```

| Check | Mutation | Required result |
|---|---|---|
| DP-01 | Move one task's PR back to `CLOSED` unmerged in the drill fixture | `DP-01 … FAIL below=1` |
| DP-02 | Remove one clause's result from the completion-check record | `DP-02 … FAIL executed=<n-1>` |
| DP-03 | Leave one lane PR open against `integration` | `DP-03 … FAIL open_prs=1` |
| DP-04 | Add a required context no workflow emits | `DP-04 … FAIL missing=1` |
| DP-05 | Mark a sync negative `asserted` rather than executed | `DP-05 … FAIL unexpected_pass=1` |
| DP-06 | Record one scheduled AT as `asserted` | `DP-06 … FAIL asserted_only=1` |
| DP-07 | Point one `mechanical` invariant at a check name that does not exist | `DP-07 … FAIL dangling=1` |
| DP-08 | Open a blocker naming the phase with no decision record | `DP-08 … FAIL undecided=1` |
| DP-09 | Present five consecutive closures with zero rejections | `DP-09 … FAIL suspect=1` |

### 3.5 `BT-4` — the phase whose ownership gap is now resolved

`master/04-phase-map.md` §2/§8 DECISION 1 no longer records `BT-4` as **BLOCKED**. The subsystem-ownership
gap is now **Resolved: FD-002** (2026-09-02; `lanes/L0-04-decisions-register.md` REG-001, "State: Closed"):
subsystems **G** (plan-checker) and **P** (people intelligence) are assigned to **L0**; **H** (dashboards)
to **L5**; **O** (governance registries and jobs) splits **L1** (registries) / **L3** (jobs); **J**
(background layer) is recorded **deferred** — no lane builds it in this build track. Every subsystem `BT-4`
needs either has an owning lane or is explicitly out of scope; nothing is unowned any more.
`master/04-phase-map.md` §4.3's `S4` row and its §9 one-page summary both read `RESOLVED (FD-002)`, not
`BLOCKED`.

`make dod-phase PHASE=BT-4` therefore no longer refuses to run **for lack of an owning lane** — that reason
is closed. See §11, decision 2, closed to match.

---

## 4. LEVEL 3 — LANE DONE

**Unit:** all of one lane's owned paths, across every phase it has deliverables in.
**Owner:** L0. A lane never declares itself done.

### 4.1 The checklist

| # | Check | What it proves | Pass output (exact) |
|---|---|---|---|
| DL-01 | Charter DoD table green | Every `DoD-n` row in that lane's `lanes/L<N>-00-charter.md` produced its stated proof | `DL-01 charter PASS lane=<N> rows=<n>/<n> failed=0` |
| DL-02 | All phases MET | Every `BT-n` in which the lane has a deliverable is `DOD-VERDICT=MET LEVEL=phase` | `DL-02 phases PASS phases=<n>/<n> undefined=0` |
| DL-03 | Owned tree complete | Every path the lane's charter names exists, and nothing exists in the lane's tree that no charter row claims | `DL-03 tree PASS declared=<n> present=<n> orphan_files=0` |
| DL-04 | **Lane suite green at `integration` head** | The suite passes after the other four lanes landed — the check the lane cannot run alone | `DL-04 lane-suite PASS lane=<N> tests=<n> failed=0` |
| DL-05 | **Seeded defect detected** | The lane's suite still fails its seeded-defect case (§31.2) | `DL-05 seeded PASS seeded_defect=DETECTED` |
| DL-06 | **Negative entry point non-vacuous** | `<lane-root>/lane-negative.sh` ran, executed ≥1 negative, and every one failed correctly | `DL-06 negatives PASS negatives_run=<n> failed_correctly=<n> vacuous=0` |
| DL-07 | Canary gates armed | Every `CAN-*` canary whose gate this lane builds returned `rejected` (or `FIND` for `CAN-DRIFT`) | `DL-07 canaries PASS owned=<n> rejected=<n> accepted=0 absent=0` |
| DL-08 | Contract halves | Every contract in the register where this lane is producer or consumer passes, against frozen fixtures | `DL-08 contracts PASS as_producer=<n> as_consumer=<n> failed=0 fixtures_match=1` |
| DL-09 | Escape rate | The lane has had work rejected over its trailing ten-PR window | `DL-09 escape-rate PASS window=10 rejections=<n> escapes=<n> suspect=0` |
| DL-10 | Boundary integrity over history | No commit in the lane's whole history touched a foreign path or `contracts/**` | `DL-10 boundary PASS commits=<n> foreign=0 contract_edits=0` |

### 4.2 The canaries each lane owns

From `protocol/06-integration-cycle.md` §6. `DL-07` asserts only the lane's own rows; `DI-06` asserts all
fourteen.

| Lane | Canaries whose gate that lane builds | Required verdict |
|---|---|---|
| L1 | `CAN-SCHEMA`, `CAN-EXPIRY`, `CAN-UNCLASSIFIED`, `CAN-PEOPLE`, `CAN-SURVEIL` | `rejected` |
| L2 | `CAN-SHIM`, `CAN-DIGEST`, `CAN-VERIFY` | `rejected` (`CAN-VERIFY`: the contract run **fails**) |
| L3 | `CAN-DRIFT`, `CAN-NARROW`, `CAN-LOOSEN` | `CAN-DRIFT`: **FIND**; `CAN-NARROW`: `rejected`; `CAN-LOOSEN`: raise Level 2, never relax |
| L4 | records/metrics side of `CAN-DRIFT` evidence | `rejected` |
| L5 | `CAN-MACHINE` | does **not** satisfy the gate |
| L0 | `CAN-LANE`, `CAN-PLAN` | `rejected` |

`absent` counts as `accepted` — a missing canary fixture is a dead gate, not a skipped test.

### 4.3 The proving command

```bash
git checkout integration && git reset --hard origin/integration
make dod-lane LANE=3
```

```
DOD-VERDICT=MET LEVEL=lane LANE=3 HEAD=4bd90fe checks=10/10 negatives=10/10 charter_rows=11/11 canaries=3/3 seeded=DETECTED escapes=0 ts=2026-08-27T17:11:44Z
```

```bash
set -euo pipefail
mkdir -p .dod
make dod-lane LANE=3 | tee .dod/lane.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=lane' .dod/lane.stdout \
  && grep -Fq 'seeded=DETECTED' .dod/lane.stdout \
  && grep -Fq 'negatives=10/10' .dod/lane.stdout \
  && test "$(wc -l < .dod/lane.stdout)" -eq 1 \
  && echo LANE-DONE || echo LANE-NOT-DONE
```

### 4.4 The negative proof

```bash
make dod-negative LEVEL=lane LANE=3
# DOD-NEGATIVE level=lane proven=10/10 unproven=0
```

| Check | Mutation | Required result |
|---|---|---|
| DL-01 | Delete one file a charter DoD row names | `DL-01 … FAIL failed=1` |
| DL-02 | Set one phase record to `NOT-MET` | `DL-02 … FAIL phases=<n-1>/<n>` |
| DL-03 | Add a file under the lane root that no charter row claims | `DL-03 … FAIL orphan_files=1` |
| DL-04 | Revert one other lane's merge in the drill worktree | `DL-04 … FAIL failed=<n>` |
| DL-05 | Repair the seeded defect | `DL-05 … FAIL seeded_defect=PASSED` |
| DL-06 | Empty `lane-negative.sh` of assertions | `DL-06 … FAIL vacuous=1` (exit `2`) |
| DL-07 | Delete one owned canary fixture | `DL-07 … FAIL absent=1` |
| DL-08 | Edit one frozen fixture byte | `DL-08 … FAIL fixtures_match=0` |
| DL-09 | Present ten PRs with zero rejections | `DL-09 … FAIL suspect=1` |
| DL-10 | Cherry-pick a foreign-path commit into the lane history | `DL-10 … FAIL foreign=1` |

### 4.5 `DL-06` and the vacuity rule, stated once

`protocol/00-test-strategy.md` §3 fixes the exit-code contract. `DL-06` is where it bites hardest, because
a negative entry point that asserts nothing is the single easiest way for a lane to look finished:

| Exit | Meaning | DL-06 result |
|---|---|---|
| `0` with `negatives_run=0` | The script ran and asserted nothing | **NOT-MET**, `vacuous=1` |
| `2` | VACUOUS, declared by the script itself | **NOT-MET** |
| `3` | NON-DISCRIMINATING — a negative fixture passed the gate | **NOT-MET**, highest severity; blocks the lane from the merge train |
| `0` with `negatives_run=n` and `failed_correctly=n` | Healthy | MET |

§53.1 is the authority: *"Every run additionally records its per-registry comparison counts … so that a
silently narrowed comparison is itself visible drift."* A suite that asserts nothing is the same failure.

---

## 5. LEVEL 4 — INTEGRATION DONE

**Unit:** one merge-train cycle on `integration`, after L1 → L4 → L2 → L3 → L5 have landed.
**Owner:** the L0 integrator.
**Relationship to GATE B:** GATE B (`IG-01`…`IG-12`) authorises the **merge** `integration` → `main`.
`DOD-VERDICT=MET LEVEL=integration` says the **cycle** is done. GATE B is a member of this checklist
(`DI-01`), not a synonym for it.

### 5.1 The checklist

| # | Check | What it proves | Pass output (exact) |
|---|---|---|---|
| DI-01 | GATE B open | `make gate-integration CYCLE=<id>` printed `GATE-B-OPEN` | `DI-01 gate-b PASS checks=12/12 negatives=24/24 canary=FOUND` |
| DI-02 | All five lanes landed, in order | `lanes=5/5 order=1,4,2,3,5 out_of_order=0 cross_lane_merges=0` | `DI-02 train PASS lanes=5/5 order=1,4,2,3,5` |
| DI-03 | **Contract tests integrated** | Each consumer ran against the producer's **real** output, not the Phase-0 stub | `DI-03 contracts PASS pairs=<n> cases=<n> failed=0 stubbed=0` |
| DI-04 | Fixture gate | `make fixtures-all` green: structure, positives, negatives, the fixture canary rejected, counts recorded | `DI-04 fixtures PASS gates=6/6 canary=REJECTED narrowed=0` |
| DI-05 | **E2E verdict** | `e2e/verdict.sh` printed `VERDICT: PASS` with both floors met | `DI-05 e2e PASS checkpoints=<n>/118 gates_proven=<n>/28` |
| DI-06 | **Fourteen canaries armed** | Run from `main`'s checkout against `integration`; every `CAN-*` returned its required verdict | `DI-06 canaries PASS armed=14/14 accepted=0 absent=0 CAN-DRIFT=FOUND` |
| DI-07 | Count integrity, full scope | Declared counts equal actual counts everywhere; per-registry comparison counts recorded | `DI-07 counts PASS at=110/110/110 inv=111/111 ec=112/112 checks=24/24 registries=<n>/<n> narrowed=0` |
| DI-08 | All five lanes MET at this head | `make dod-lane LANE=<N>` is MET for every lane at the cycle tip | `DI-08 lanes PASS lanes=5/5 not_met=0` |
| DI-09 | **Anti-rubber-stamp** | Trailing ten-cycle rejection count is non-zero, or a named written answer exists on the record | `DI-09 signoff PASS signer=<login> window_cycles=10 rejections=<n> rubber_stamp_flag=0` |
| DI-10 | Record written | The cycle wrote its own append-only record and the record names an existing path | `DI-10 record PASS path=records/dod/closures/integration/<cycle>.yaml` |

### 5.2 The proving command

```bash
set -euo pipefail
git fetch origin main integration
CYCLE=2026-08-27-a

make dod-integration CYCLE="$CYCLE"
```

```
DOD-VERDICT=MET LEVEL=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=10/10 negatives=10/10 lanes=5/5 canaries=14/14 canary=FOUND e2e=PASS counts=OK escapes=0 signer=paresh ts=2026-08-27T18:22:07Z
```

```bash
set -euo pipefail
mkdir -p .dod
make dod-integration CYCLE="$CYCLE" | tee .dod/integration.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=integration' .dod/integration.stdout \
  && grep -Fq 'canary=FOUND'   .dod/integration.stdout \
  && grep -Fq 'canaries=14/14' .dod/integration.stdout \
  && grep -Fq 'e2e=PASS'       .dod/integration.stdout \
  && test "$(wc -l < .dod/integration.stdout)" -eq 1 \
  && echo INTEGRATION-DONE || echo INTEGRATION-NOT-DONE
```

`canary=FOUND`, `canaries=14/14` and `e2e=PASS` are asserted **separately and by name**. They are the three
tokens a broken instrument is most likely to lose while still printing a verdict — the exact failure EC-109
describes and `protocol/05-merge-gate.md` §4.1 guards the same way.

### 5.3 The independent verifier — the check that cannot be run by the thing it checks

§53.1 requires a second verifier *"off the operations VM and under a different credential"*, writing its
result *"to a surface the operations VM cannot write to"*, whose *"own absence for one cycle is Level 5"*.
`DI-06` inherits that property: the canary runner executes from a worktree of `main`, not from
`integration`, and not from any lane's tree.

```bash
set -euo pipefail
# From protocol/06-integration-cycle.md §15 — the shape is fixed, do not vary it.
git worktree add /tmp/train-verifier origin/main
/tmp/train-verifier/tools/train/run-canaries.sh \
  --target origin/integration --out tools/train/state/canaries-"$CYCLE".json
git worktree remove /tmp/train-verifier
```

**If `run-canaries.sh` reports anything other than fourteen armed gates, stop at that line. Everything after
it is a check that could only pass.**

Absence of the verifier's own result for one cycle is treated as **Level 5 — Escalate** (§53.2): an
incident, notified to the escalation role. It is never treated as a clean cycle.

### 5.4 The negative proof

```bash
make dod-negative LEVEL=integration CYCLE=2026-08-27-a
# DOD-NEGATIVE level=integration proven=10/10 unproven=0
```

| Check | Mutation | Required result |
|---|---|---|
| DI-01 | Flip one `IG-*` line to FAIL in the drill verdict file | `DI-01 … FAIL checks=11/12` |
| DI-02 | Re-order the cycle's merges to L3 before L1 | `DI-02 … FAIL out_of_order=1` |
| DI-03 | Force one consumer back onto its Phase-0 stub | `DI-03 … FAIL stubbed=1` |
| DI-04 | Make the fixture canary acceptable to its gate | `DI-04 … FAIL canary=ACCEPTED` |
| DI-05 | Delete one negative stage from `e2e/negative/` | `DI-05 … FAIL gates_proven=27/28` |
| DI-06 | Remove the `CAN-DRIFT` seeded record from the comparison set | `DI-06 … FAIL CAN-DRIFT=MISSING` → run is FAILED, **SIG-13**, §53.7 gap procedure |
| DI-07 | Drop one row from a registry a lane enumerates | `DI-07 … FAIL narrowed=1` |
| DI-08 | Set one lane's DoD record to `NOT-MET` | `DI-08 … FAIL not_met=1` |
| DI-09 | Present a sign-off by the author of the cycle's largest diff | `DI-09 … FAIL self_signoff=1` |
| DI-10 | Delete the closure record after writing the verdict | `DI-10 … FAIL path=missing` |

### 5.5 STOP rules at this level

| Symptom | Action | STOP rule |
|---|---|---|
| `canary=MISSING` / `CAN-DRIFT=MISSING` | Treat the run as **FAILED**; raise **SIG-13**; run the §53.7 gap procedure over the window; mark records produced in the window `gap-window` | Never record the run as clean. A `gap-window` record is not evidence for any level until re-verified. |
| `accepted` or `absent` on any canary | **The train freezes.** No promotion, no merges next cycle | The freeze lifts only when L0 records what broke the gate and the canary returns `rejected`. |
| `gates_proven` below 28 on the E2E | A gate permitted what it exists to forbid | More serious than a failed positive: the happy path may be entirely green while the system has no gate at all. |
| `seeded_defect=PASSED` anywhere | The instrument stopped discriminating (§31.2) | Raise **SIG-18**; Blocking for that product until the case fails again. Never delete the seeded case to go green. |
| `rubber_stamp_flag=1` | Ten cycles with zero rejections | Write the named explanation on the closure record. Do not silence the flag by widening the window. |
| Any DoD script crashes, times out, or prints nothing | Fail closed; the level is NOT-MET | Absence of output is never a pass (Spec §101 #80). |

---

## 6. LEVEL 5 — V1 DONE

**Unit:** the nine items of §99.4, on `main`, for the declared pilot product set.
**Owner:** L0 integrator, countersigned by the Founder as a decision record.
**Authority for scope:** `master/06-v1-scope.md`. Its §8.3 list of **acceptance tests V1 must not claim** is
part of the scope contract: *"a lane that 'makes a test pass' from this list has built out of scope."*

### 6.1 The checklist

| # | Check | Covers §99.4 item | What it proves | Pass output (exact) |
|---|---|---|---|---|
| DV-01 | Registries and schemas | 1 | `make validate` exits 0; `make check-append-only` exits 0; effective dating present in every registry and record schema | `DV-01 registries PASS files=<n> invalid=0 append_only=OK effective_dating=<n>/<n>` |
| DV-02 | GitHub enforcement, negatives executed | 2 | `make phase1-completion-check` exits 0 and prints each §98.2 Phase 1 negative test with its result | `DV-02 enforcement PASS clauses=<n> executed=<n> asserted_only=0` |
| DV-03 | Scaffolding v0 | 3 | `create-product` and `add-person` complete with **zero hand-editing**; generated CODEOWNERS contains human identities only | `DV-03 scaffolding PASS hand_edits=0 machine_codeowners=0` |
| DV-04 | Delivery pipeline and evidence chain | 4 | `make at AT=AT-103` exits 0; `make evidence-chain PRODUCT=<p>` answers all eleven questions; one deliberate rollback in staging; one recorded restore test | `DV-04 pipeline PASS chain=11/11 rollback=RECORDED restore_test=RECORDED digest_rebuilds=0` |
| DV-05 | Verification contract + seeded defect | 5 | `make validate` rejects a fixture product with no verification contract (Spec §101 #1); the seeded-defect case **fails** (§31.2, D97) | `DV-05 verification PASS missing_contract=REJECTED seeded_defect=DETECTED` |
| DV-06 | Reconciliation v0, detect and block | 6 | `make at AT=AT-102`, `AT=AT-033`, `AT=AT-110` all exit 0; the block is a **named required check** posted per affected repository, not "fails CI" | `DV-06 reconciler PASS at=AT-102,AT-033,AT-110 required_check=POSTED level3_shipped=0` |
| DV-07 | Founder view v0 | 7 | `make founder-view-v0` renders with **zero hand-maintained numbers** (Spec §101 #46); every panel names its record store | `DV-07 founder-view PASS panels=<n> hand_maintained=0 unnamed_source=0` |
| DV-08 | Governance sliver + CP/DP invariant | 8 | `make at AT=AT-036`, `AT=AT-037`, `AT=AT-039`, `AT=AT-029`, `AT=AT-030` all exit 0; every control classified fail-closed or fail-open | `DV-08 governance PASS at=5/5 unclassified_controls=0` |
| DV-09 | People tier: **nothing but schemas** | 9 | People schemas validate, and **no Layer B artefact exists** | `DV-09 people PASS schemas=<n> layer_b_artifacts=0` |
| DV-10 | The six residuals | R-1…R-6 | Each residual of `master/06-v1-scope.md` §4 meets its stated acceptance | `DV-10 residuals PASS residuals=6/6 unmet=0` |
| DV-11 | **Out-of-scope negative** | §8.3 | No AT on the "must not claim" list is recorded as passing | `DV-11 scope PASS must_not_claim=<n> wrongly_claimed=0` |
| DV-12 | **V1 negative battery** | — | Every DV check proven able to fail on this head | `DV-12 negatives PASS proven=12/12 unproven=0` |

### 6.2 The V1 acceptance-test set — every id real, every id executed

From `master/06-v1-scope.md` §8.2. `DV-06` and `DV-08` execute these; none is asserted.

| AT | What it proves at V1 |
|---|---|
| **AT-102** | The seeded reconciliation canary: every run must find the seeded drift; a zero-finding run is a **failed** run, raises **SIG-13** and triggers the gap procedure |
| **AT-110** | The reconciler credential is provably bounded: six attempts, all six fail, and the credential then still completes a normal reconciliation run — *"executed for real at the phase that builds the reconciler"* |
| **AT-103** | Production restore with no credential handed to or typed by a human, with an exceptional-authorisation record |
| **AT-033** | No auto-loosening: a stricter-than-declared production control is raised for human review, never relaxed |
| **AT-029** | All products keep serving customers with the control plane unreachable, and a production rollback still executes via the documented manual path |
| **AT-030** | A control-plane tool is disabled; `.planning/`, verification contracts and product contracts remain readable and usable without it |
| **AT-036** | A temporary access exception expires and reconciliation revokes it with no human action |
| **AT-037** | An exception that cannot be auto-revoked becomes Blocking drift on its expiry date |
| **AT-039** | A bootstrap exception carries an expiry and an activation checklist; it *"cannot lapse silently"* |
| **AT-051** | Brownfield pre-onboarding mode: minimal ruleset, accepted-risk record, named deadline; a breached deadline surfaces as drift |
| **AT-009** | Conditional on the pilot's declared conformance profile — for the default `service` profile, the eight commands, the three endpoints and the verification contract |
| **AT-047** *(contract-validation half only)* | A declared `coverage_window` not fully covered by active rota members **fails contract validation** |
| **AT-049** | Conditional on a pilot declaring an `ai_runtime_dependency`: no eval suite under `verification/` → CI fails |

### 6.3 The V1 invariant floor

Invariants V1 arms, each with a mechanism (`master/06-v1-scope.md` §8.1). An invariant not on this list is
armed later **or explicitly rendered unarmed** — never quietly assumed.

`1` · `3` · `4` · `9` · `12` · `20` · `22` · `23` · `44` · `46` · `47` · `57` · `75` · `76` · `77` · `79` ·
`80` · `81` · `84` · `85` · `111` *(partial — state it as partial; do not claim it fully mechanical)*.

Plus everything §95.3 declares binding **even in bootstrap**: digest immutability (22), verification
contracts (1), secret tiers and the API-key-free environment (25, 84), append-only history and effective
dating (47), the constitution and the untrusted-input rule (20), safe defaults and fail-closed
classification (79, 80), and the explicit production-approval event (12).

### 6.4 The proving command

```bash
git checkout main && git reset --hard origin/main
make dod-v1
```

```
DOD-VERDICT=MET LEVEL=v1 HEAD=1c77e30 checks=12/12 negatives=12/12 items=9/9 residuals=6/6 at=13/13 invariants=21/21 wrongly_claimed=0 canary=FOUND ts=2026-09-30T10:02:55Z
```

```bash
set -euo pipefail
mkdir -p .dod
make dod-v1 | tee .dod/v1.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=v1' .dod/v1.stdout \
  && grep -Fq 'items=9/9'          .dod/v1.stdout \
  && grep -Fq 'wrongly_claimed=0'  .dod/v1.stdout \
  && grep -Fq 'canary=FOUND'       .dod/v1.stdout \
  && grep -Fq 'negatives=12/12'    .dod/v1.stdout \
  && test "$(wc -l < .dod/v1.stdout)" -eq 1 \
  && echo V1-DONE || echo V1-NOT-DONE
```

`make dod-v1` calls `implementation/master/v1-exit-gate.sh` (`master/06-v1-scope.md` §13) and then adds
`DV-11` and `DV-12`, which that script does not carry. Both are required: the exit gate proves the nine
items exist; `DV-11` proves nothing beyond them was built, and `DV-12` proves the whole set could have
failed.

### 6.5 The negative proof

```bash
make dod-negative LEVEL=v1
# DOD-NEGATIVE level=v1 proven=12/12 unproven=0
```

| Check | Mutation | Required result |
|---|---|---|
| DV-01 | Remove `effective_from` from one registry schema | `DV-01 … FAIL effective_dating=<n-1>/<n>` |
| DV-02 | Record one Phase 1 negative clause as asserted | `DV-02 … FAIL asserted_only=1` |
| DV-03 | Hand-edit one file `create-product` should have generated | `DV-03 … FAIL hand_edits=1` |
| DV-04 | Rebuild the production artifact instead of promoting the staging digest | `DV-04 … FAIL digest_rebuilds=1` |
| DV-05 | Repair the seeded-defect case in `verification/contract.yaml` | `DV-05 … FAIL seeded_defect=PASSED` → **SIG-18** |
| DV-06 | Remove the seeded canary from the comparison set | `DV-06 … FAIL AT-102=FAILED-RUN` → **SIG-13** |
| DV-07 | Hand-enter one number into a Grafana panel | `DV-07 … FAIL hand_maintained=1` |
| DV-08 | Remove one control's fail-closed/fail-open classification | `DV-08 … FAIL unclassified_controls=1` |
| DV-09 | Create one Layer B artefact | `DV-09 … FAIL layer_b_artifacts=1` |
| DV-10 | Delete the newest `records/bootstrap-log/` entry (R-6) | `DV-10 … FAIL unmet=1` (control-plane CI Blocking past 7 days) |
| DV-11 | Record `AT-001` as passing | `DV-11 … FAIL wrongly_claimed=1` |
| DV-12 | Delete one mutation from the V1 battery manifest | `DV-12 … FAIL unproven=1` |

**`DV-11` deserves its own paragraph.** A cheap model that has just made the nine items work will reach for
the next plausible test and try to make it pass too. `master/06-v1-scope.md` §8.3 lists, by id, everything
V1 must **not** claim — `AT-001`, `AT-002`, `AT-003`–`AT-008`, `AT-017`, `AT-018`, `AT-019`–`AT-022`,
`AT-023`–`AT-027`, `AT-031`, `AT-032`, `AT-034`, `AT-035`, `AT-038`, `AT-040`–`AT-046`, `AT-048`, `AT-050`,
`AT-052`–`AT-088`, `AT-089`–`AT-100`, `AT-101`, `AT-104`–`AT-109`. A recorded pass for any of them is
**out-of-scope work**, and `DV-11` fails V1 for it. Building more is not finishing sooner.

---

## 7. LEVEL 6 — PROGRAMME DONE

**Unit:** the Foundation tier, complete across the live portfolio.
**Owner:** the Founder, as a decision record. This is the only level a human closes rather than a machine,
and even here the human is countersigning a machine verdict, not replacing it.

### 7.1 The checklist

| # | Check | Authority | Pass output (exact) |
|---|---|---|---|
| DG-01 | V1 MET on `main` | §99.4 | `DG-01 v1 PASS verdict=MET head=<sha7>` |
| DG-02 | Every live product onboarded, or in declared pre-onboarding with an unbreached deadline | §96.2, §96.4 | `DG-02 onboarding PASS products=<n> complete=<n> pre_onboarding=<n> breached=0` |
| DG-03 | Portfolio adoption ratio reaches 100% by the last named deadline | §96.4 | `DG-03 adoption PASS ratio=1.00 last_deadline=<date> late=0` |
| DG-04 | **Universal floor closed** — 9 items × every live product, each with a named executor and a date, or a dated accepted risk mirrored into the exception registry | §96.6 | `DG-04 floor PASS rows=<n>/<n> unexecuted=0 unmirrored_risks=0` |
| DG-05 | Zero Blocking drift open | §53, §98.5 G1 exit | `DG-05 drift PASS blocking_open=0 acknowledged=<n>` |
| DG-06 | **Every reconciliation run in the window found the canary** | AT-102 | `DG-06 canary PASS runs=<n> found=<n> zero_finding_runs=0` |
| DG-07 | Per product: eleven-item evidence chain answerable for one real deployment; one deliberate rollback succeeded in staging; one restore test recorded and in the rolling 90-day rotation | §98.2 Phase 6; invariants 3, 4 | `DG-07 per-product PASS products=<n> chain=<n>/<n> rollbacks=<n>/<n> restores=<n>/<n> stale_restore=0` |
| DG-08 | **Anti-rubber-stamp across the programme** | §103.13 | `DG-08 instruments PASS plan_rejections=<n> review_change_requested=<n> zero_rate_flags=0` |
| DG-09 | **Baselines recorded before Phase 1** | §103.14, AT-046 | `DG-09 baselines PASS measures=<n> baselined=<n> unbaselined_marked=<n> silently_absent=0` |
| DG-10 | Programme negative battery | this file | `DG-10 negatives PASS proven=10/10 unproven=0` |

### 7.2 `DG-08` — the four standing zero-rate instruments

From `protocol/08-smoke-and-e2e.md` §7.3 and §103.13. Each reads the event log; each has a reading that
means the gate is **not** working.

| Instrument | Source | Reading that means the gate is not working |
|---|---|---|
| Plan-checker rejections | `plan_rejected` events | **Zero over a review period.** §103.1: *"Zero rejections means the gates are not working"* |
| Gate 2 change-requested rate | Review records | **Very low may mean rubber-stamping** (§103.9) |
| Reconciliation findings | Reconciler run records | **Zero including the canary → failed run**, SIG-13, gap procedure (AT-102) |
| Verification-contract seeded case | Contract run records | **Last run passed → SIG-18**, Blocking for that product (§31.2) |

Plus the write-freshness limb (§97.2): past interval on `events/`, `records/deployments/` or `records/uat/`
is **Blocking**, because zero-shaped metrics are indistinguishable from health.

**A `zero_rate_flag` does not by itself close the programme level.** It forces a named written answer on the
closure record, signed by the metric's owner — Team Lead for §103.1/§103.2/§103.9, QA and Team Lead for
§103.3, Founder for §103.13. An unanswered flag holds the level at NOT-MET.

### 7.3 The proving command

```bash
git checkout main && git reset --hard origin/main
make dod-programme
```

`make dod-programme` runs `make dod-v1`, then `make dod-foundation` (`master/00-MASTER-PLAN.md` §6.2), then
`DG-03`…`DG-10`, and prints one line:

```
DOD-VERDICT=MET LEVEL=programme HEAD=1c77e30 checks=10/10 negatives=10/10 products=8/8 floor=72/72 blocking_drift=0 canary_runs=63/63 baselines=OK zero_rate_flags=0 decision_record=DEC-2026-11-14-3 ts=2026-11-14T09:15:00Z
```

```bash
set -euo pipefail
mkdir -p .dod
make dod-programme | tee .dod/programme.stdout
grep -Fq 'DOD-VERDICT=MET LEVEL=programme' .dod/programme.stdout \
  && grep -Fq 'blocking_drift=0'   .dod/programme.stdout \
  && grep -Fq 'zero_rate_flags=0'  .dod/programme.stdout \
  && grep -Fq 'baselines=OK'       .dod/programme.stdout \
  && grep -Eq 'canary_runs=([0-9]+)/\1' .dod/programme.stdout \
  && grep -Fq 'decision_record=DEC-' .dod/programme.stdout \
  && test "$(wc -l < .dod/programme.stdout)" -eq 1 \
  && echo PROGRAMME-DONE || echo PROGRAMME-NOT-DONE
```

The `canary_runs=n/n` regex asserts that **every** run in the window found the canary — not that most did.
One zero-finding run is one failed run, and AT-102 admits no rounding.

### 7.4 The negative proof

```bash
make dod-negative LEVEL=programme
# DOD-NEGATIVE level=programme proven=10/10 unproven=0
```

| Check | Mutation | Required result |
|---|---|---|
| DG-01 | Set the V1 record to `NOT-MET` | `DG-01 … FAIL verdict=NOT-MET` |
| DG-02 | Backdate one pre-onboarding `deadline:` past today | `DG-02 … FAIL breached=1` |
| DG-03 | Remove one product from the adoption denominator | `DG-03 … FAIL ratio<1.00` **and** `DI-07`-class narrowing flagged |
| DG-04 | Mark one floor row done with no named executor | `DG-04 … FAIL unexecuted=1` |
| DG-05 | Open one Blocking drift finding | `DG-05 … FAIL blocking_open=1` |
| DG-06 | Insert one zero-finding reconciliation run into the window | `DG-06 … FAIL zero_finding_runs=1` |
| DG-07 | Age one `restore_tested` date past 90 days | `DG-07 … FAIL stale_restore=1` (Spec §101 #4: an older date fails CI) |
| DG-08 | Present a review period with zero plan rejections | `DG-08 … FAIL zero_rate_flags=1` |
| DG-09 | Remove one §103.13 measure's baseline without marking it `unbaselined` | `DG-09 … FAIL silently_absent=1` (AT-046) |
| DG-10 | Delete one mutation from the programme battery | `DG-10 … FAIL unproven=1` |

### 7.5 `DG-04` — why the floor is the row, not the paragraph

§96.6 is explicit and this check refuses to soften it: the universal floor is **nine items across every live
product**, *"which at eight products is seventy-two tracked obligations: it is a checklist artifact with one
row per item per product, each row carrying a named executor drawn from the product's existing team and a
date, not a paragraph anyone can declare complete."*

```bash
set -euo pipefail
# contracts/dod/floor.sh — one row per item per product, directory-per-item (PARTITION rule 3)
products=$(yq -r '.products[].id' registries/portfolio.yaml 2>/dev/null | wc -l)
[ "$products" -gt 0 ] || { echo "DG-04 floor FAIL products=0 portfolio_empty_or_missing=1"; exit 1; }
items=9
expected=$(( products * items ))
rows=$(ls -1 records/floor/*/*.yaml 2>/dev/null | wc -l)
named=$(grep -l '^executor: [a-z]' records/floor/*/*.yaml 2>/dev/null | wc -l)
dated=$(grep -l '^completed: 20' records/floor/*/*.yaml 2>/dev/null | wc -l)
risks=$(grep -l '^accepted_risk_id: EXC-' records/floor/*/*.yaml 2>/dev/null | wc -l)
unmirrored_risks=0
for f in $(grep -l '^accepted_risk_id: EXC-' records/floor/*/*.yaml 2>/dev/null); do
  rid=$(grep '^accepted_risk_id:' "$f" | awk '{print $2}')
  grep -q "^- id: ${rid}\$" registries/exceptions.yaml 2>/dev/null || unmirrored_risks=$(( unmirrored_risks + 1 ))
done
unexecuted=$(( rows - named ))
echo "DG-04 floor rows=${rows}/${expected} named=${named} dated=${dated} accepted_risks=${risks} unmirrored_risks=${unmirrored_risks}"
[ "$rows" -eq "$expected" ] && [ "$unexecuted" -eq 0 ] && [ "$unmirrored_risks" -eq 0 ] \
  && echo "DG-04 floor PASS rows=${rows}/${expected} unexecuted=0 unmirrored_risks=0" \
  || echo "DG-04 floor FAIL rows=${rows}/${expected} unexecuted=${unexecuted} unmirrored_risks=${unmirrored_risks}"
```

A floor row closed by an accepted risk must carry `accepted_risk_id:` pointing at a live `exceptions.yaml`
entry — §96.6 requires the risk *"mirrored into the exception registry like any other"*, which means it
inherits Spec §101 #77 (every exception has an expiry) and **SIG-39** (bootstrap exception past expiry with
its gate still unarmed). A floor row cannot be closed by a promise with no clock.

---

## 8. THE ANTI-PATTERN LIST — what "done" is NOT

Written because a low-cost model with no repo context will otherwise declare victory at the first plausible
stopping point. Each row is a real failure mode, its detector, and the level that catches it. **If your
completion claim matches a row in this table, your claim is false and the correct output is `BLOCKED`.**

### 8.1 Claim-shaped anti-patterns

| # | "Done" is NOT… | Why it is not done | Detector | Caught at |
|---|---|---|---|---|
| AP-01 | …a status you set. | The ledger has no `status:` field precisely so this cannot happen. Status is derived from git and GitHub facts only. | `DT-01` forbidden-key scan | TASK |
| AP-02 | …a percentage. There is no 90% done. | `master/08-progress-tracking.md` §0 forbids `percent:` and `progress:` keys. A task is `accepted` or it is not. | `DT-01` | TASK |
| AP-03 | …"done with caveats" or "done, minor item remaining". | `manual/10-quality-bar.md` §10.1: there is no third status. A remaining item is a `BLOCKED` task or an open blocker issue. | `DT-10` `unreported_gaps` | TASK |
| AP-04 | …a summary paragraph describing what you built. | Prose is not a verdict line. Only the exact `DOD-VERDICT=MET` string closes a level. | `wc -l` = 1 on the stdout file | every level |
| AP-05 | …a plan for finishing. | §95.4: *"stubbed gates have a habit of staying stubbed."* An intention to finish is empirically a stub that ships. | `DT-04` banned tokens | TASK |
| AP-06 | …someone else's sign-off in chat. | GATE B sign-off is a decision record in `records/decisions/`, not a message. | `DI-09` `decision_record=` | INTEGRATION |
| AP-07 | …the absence of a red mark. | Silence is never health (EC-109). MET is an explicit exact string; nothing else is. | Rule 2 of §1.1 | every level |

### 8.2 Instrument-shaped anti-patterns — the ones this protocol exists for

| # | "Done" is NOT… | Why it is not done | Detector | Caught at |
|---|---|---|---|---|
| AP-08 | …a green suite that contains no negative test. | A check that can only pass is not a check. §95.4 executes negatives *for real*. | `DT-03`, `DL-06` `vacuous=1`, exit code `2` | TASK, LANE |
| AP-09 | …a suite whose seeded defect now passes. | §31.2: *"A verification contract that cannot fail is not a contract."* A run in which the seeded defect passes is a **FAILED** run. | `DT-06`, `DL-05`, `DV-05` `seeded_defect=PASSED` → **SIG-18** | TASK, LANE, V1 |
| AP-10 | …a reconciliation run that reported zero findings. | §53.1 / AT-102: *"A reconciler that finds nothing is assumed broken, never assumed clean."* | `DI-06 CAN-DRIFT=MISSING`, `DG-06 zero_finding_runs` → **SIG-13** | INTEGRATION, PROGRAMME |
| AP-11 | …a gate with no paired canary. | `protocol/06-integration-cycle.md` §6: *"Adding a gate adds a canary in the same PR."* A gate merged without one is reverted. | `DL-07`, `DI-06` `absent=1` | LANE, INTEGRATION |
| AP-12 | …a required status check that reported `skipped` or `neutral`. | §33.2: such a conclusion on a merged PR is **Blocking drift**. The check that appears green never ran. | `DP-04` `missing`, `LG-10`/`IG-10` | PHASE |
| AP-13 | …a required check nothing emits. | §98.2 Phase 1: *"a list that silently stays empty is a gate that reads armed and is not."* | `DP-03` line 5, `DP-04` | PHASE |
| AP-14 | …ten cycles with zero rejections. | §103.13: *"Zero rejections means the gates are not working."* §103.9: *"Very low may mean rubber-stamping."* | `DL-09`, `DI-09` `rubber_stamp_flag=1`, `DG-08` | LANE → PROGRAMME |
| AP-15 | …a level whose downstream has never caught it wrong. | A level nothing has ever refused may be decorative. | `bash contracts/dod/escape-rate.sh` `suspect=1`; `make dod-drill` `caught=0` | every level |
| AP-16 | …a passing test that was fixed by editing the fixture. | `contracts/fixtures/**` is L0-owned and FROZEN. A lane that believes a fixture is wrong files a Contract Change Request. | `DL-08` `fixtures_match=0`, `LG-03` | LANE |
| AP-17 | …an acceptance test recorded as `asserted` rather than executed. | §100 requires AT-108, AT-109 and AT-110 to be **executed for real**. AT-090: *"A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes."* | `DP-06`, `IG-07` `asserted_only=1` | PHASE |
| AP-18 | …a completion check you read and agreed with. | §98.2's checks are *"executed as written"*. `DP-02` counts clauses with recorded results, not sentences you have read. | `DP-02` `executed<clauses` | PHASE |

### 8.3 Scope-shaped anti-patterns — the quiet-wrong-thing failures

| # | "Done" is NOT… | Why it is not done | Detector | Caught at |
|---|---|---|---|---|
| AP-19 | …a smaller task that resembles the task. Three of eleven rules is not eleven rules. | Five developers with no shared context fail exactly this way; nothing local holds the number. | `DT-08` `declared≠delivered`, `DV-11`/`IG-05` count integrity | TASK, V1 |
| AP-20 | …lowering the declared count to match what you built. | `COUNTS.tsv` and `enumerates:` are L0-frozen. `protocol/05-merge-gate.md` §9: *"Do not adjust `COUNTS.tsv` to match the code."* | `LG-03` contract immunity; `DI-07` `narrowed=1` | TASK → INTEGRATION |
| AP-21 | …an enumeration you silently narrowed. | §53.1 requires per-registry comparison counts *"so that a silently narrowed comparison is itself visible drift"*. | `CAN-NARROW`; `DI-07 registries=<n>/<n>` | INTEGRATION |
| AP-22 | …building something not in V1 because it looked adjacent. | `master/06-v1-scope.md` §8.3: *"a lane that 'makes a test pass' from this list has built out of scope."* | `DV-11` `wrongly_claimed>0` | V1 |
| AP-23 | …work in another lane's paths, however obviously correct the fix. | PARTITION rule 1, no exceptions. The fix is a blocker issue or a Contract Change Request, never an edit. | `DT-07`, `DL-10`, `LG-02` `foreign>0` | TASK, LANE |
| AP-24 | …a path no `ownership.tsv` row claims. | *"An unowned path is a future merge conflict"* — a path with zero owners violates rule 1 in the direction nobody notices. | `LG-02` `unowned>0`; `DL-03 orphan_files` | TASK, LANE |
| AP-25 | …stubbing another lane's output into your own tree so your tests go green. | PARTITION rule 4. A consumer develops against `make stub-env` materialised from `contracts/**`, never against a hand-written copy of a producer. | `LG-11` `foreign_refs>0`; `DI-03` `stubbed>0` | TASK, INTEGRATION |
| AP-26 | …a contract change you made yourself. | PARTITION rule 2: `contracts/**` is FROZEN. A lane files a CCR and **stops work on the affected task**. | `LG-03` `l0_paths_touched>0` | TASK |

### 8.4 Artifact-shaped anti-patterns

| # | "Done" is NOT… | Why it is not done | Detector | Caught at |
|---|---|---|---|---|
| AP-27 | …a file with the right name, the right imports and an empty body. | `manual/10-quality-bar.md` §10.2: a plausible-looking stub *"passes a glance. It fails a run."* | `DT-04` banned tokens; `DT-05` `unparseable` | TASK |
| AP-28 | …`properties: {}` or `required: []` where the task named fields. | Half a schema validates as a schema and rejects nothing. | `DT-03` — the negative fixture must be `REJECTED` | TASK |
| AP-29 | …a test that asserts `True`, or that would pass against an empty implementation. | The suite must fail on broken input, which is what the seeded-defect case proves. | `DT-06`, `DL-05` | TASK, LANE |
| AP-30 | …a dashboard panel with a hand-entered number. | Invariant 46: derived data is computed, never hand-maintained; metrics derive from the §97 stores. | `DV-07` `hand_maintained>0` | V1 |
| AP-31 | …a record store that exists but has never been written to. | §97.2 write-freshness is **Blocking** for `events/`, `records/deployments/` and `records/uat/`. Zero-shaped metrics are indistinguishable from health. | `DV-10` (R-1); `DG-08` freshness limb | V1, PROGRAMME |
| AP-32 | …a gate run with no record. | `protocol/05-merge-gate.md` §10 and §95.4: *"An evidence base that nothing makes happen is reconstructed from memory."* | `DI-10` `path=missing` | INTEGRATION |
| AP-33 | …a production artifact rebuilt for `main`. | Invariants 22 and 23: the production artifact is the same digest verified in staging. Never rebuilt, not even around registry unavailability. | `DV-04` `digest_rebuilds>0`; `CAN-DIGEST` | V1 |
| AP-34 | …a floor item declared complete in a paragraph. | §96.6: one row per item per product, each with a named executor and a date. | `DG-04` `unexecuted>0` | PROGRAMME |

### 8.5 Authority-shaped anti-patterns

| # | "Done" is NOT… | Why it is not done | Detector | Caught at |
|---|---|---|---|---|
| AP-35 | …a merge approved by a machine account. | Invariant 18 puts merge and approve outside machine authority entirely; §98.2 Phase 1 executes it negatively. | `LG-09` `machine_approvals>0`; `CAN-MACHINE` | TASK |
| AP-36 | …a self-approved change. | Invariants 8 and 9: independent review, and approval of the **most recent reviewable push**. | `LG-09` `author_distinct=0`, `stale_approvals>0` | TASK |
| AP-37 | …a deploy approved by the actor deploying it. | Invariant 12 and §98.2 Phase 6: the deploy *"fails closed when the approver equals the deploying actor"*. | `DV-02`/`DP-02` Phase 6 clause | PHASE, V1 |
| AP-38 | …a gate relaxed because headcount is short. | The gate runs under a declared **expiring** bootstrap exception in `exceptions.yaml` with owner, expiry and deactivation trigger. Invariant 77 rejects one without an expiry. | `DV-08`; **SIG-39** | V1 |
| AP-39 | …a lane grading its own exam. | §53.1: *"no control that can be rewritten by the credential it is checking is a control."* `contracts/dod/**`, `contracts/gate/**` and the canaries are L0's. | `LG-03`; `DL-10` `contract_edits>0` | TASK, LANE |
| AP-40 | …a re-run until it goes green. | `protocol/05-merge-gate.md` §3.1: *"do not re-run hoping for a different result."* A flaky gate is a defect in the gate, recorded as one. | Closure records are append-only; every run is kept (Spec §101 #47) | every level |

### 8.6 The one-line test

```bash
# If you cannot answer YES to all five, you are not done.
# 1. Did a command print the exact DOD-VERDICT=MET line for this level, on this revision?
# 2. Did the paired negative run print proven=<n>/<n> unproven=0?
# 3. Did every planted thing get found — canary=FOUND, seeded_defect=DETECTED, canaries=14/14?
# 4. Does the count you delivered equal the count that was declared?
# 5. Is there an append-only record file naming this revision and this verdict?
```

---

## 9. What each level writes

Every closure — MET or NOT-MET — writes exactly one file. One run per file, append-only, never overwritten
(Spec §101 #47; §97 directory-per-item; PARTITION rule 3, which is why five lanes' records never conflict).

```
records/dod/closures/task/2026-08-27/L1-F0-003-9f2c1ab.yaml
records/dod/closures/phase/2026-08-27/BT-2-L3-4bd90fe.yaml
records/dod/closures/lane/2026-08-27/L3-4bd90fe.yaml
records/dod/closures/integration/2026-08-27/CYCLE-2026-08-27-a.yaml
records/dod/closures/v1/2026-09-30/V1-1c77e30.yaml
records/dod/closures/programme/2026-11-14/FOUNDATION-1c77e30.yaml
records/dod/escapes/lane/2026-09-02/L3-DL-04-esc-011.yaml
records/dod/drills/2026-09-02-integration.yaml
```

The record shape is fixed:

```yaml
dod_record_schema_version: 1
level: integration                 # task | phase | lane | integration | v1 | programme
id: CYCLE-2026-08-27-a
revision: 4bd90fe                  # the exact SHA the verdict is about
verdict: MET                       # MET | NOT-MET | UNDEFINED
checks:                            # every per-check line, verbatim, in order
  - "DI-01 gate-b PASS checks=12/12 negatives=24/24 canary=FOUND"
  - "DI-02 train PASS lanes=5/5 order=1,4,2,3,5"
negatives: "DOD-NEGATIVE level=integration proven=10/10 unproven=0"
counts: "at=110/110/110 inv=111/111 ec=112/112 checks=24/24 registries=9/9 narrowed=0"
canaries: "armed=14/14 accepted=0 absent=0 CAN-DRIFT=FOUND"
escape_rate: "window=10 closures=10 rejections=3 escapes=0 suspect=0"
human: { signer: paresh, decision_record: DEC-2026-08-27-2, self_signoff: false }
suspect_answer: null               # required non-null whenever any suspect/flag field is 1
verdict_line: "DOD-VERDICT=MET LEVEL=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=10/10 …"
```

**A closure with no record is itself a failure.** `DI-10` requires `path=` to name an existing file, and the
same rule applies at every level: `make dod-*` refuses to print MET if it could not write its record.

---

## 10. When a level is NOT-MET — the routing table

Find the row, do the thing, stop. No judgment is required at any row.

| Level | Symptom | Action | STOP rule |
|---|---|---|---|
| TASK | any `DT-*` FAIL | Fix it, or report `BLOCKED` with the failing line pasted. `BLOCKED` is cheap; a false `DONE` costs five lanes a merge train. | Do not open the PR. Do not fix by editing a foreign path or a fixture. |
| TASK | MET on branch, NOT-MET on `integration` head | Record an **escape** (§1.2). L0 issues a new task. | Never fix it inside another lane's PR. |
| PHASE | `DP-02 executed<clauses` | Execute the missing completion-check clause and record its result | Never mark a clause satisfied by reading it. |
| PHASE | `DP-05 unexpected_pass=1` | The sync-point negative did not fire; the gate is dead. Repair the gate before anything else. | The sync point does not pass. No lane opens the next phase. |
| PHASE | `BT-4` returns `UNDEFINED` | Escalate to L0: DECISION 1 of `master/04-phase-map.md` | No lane may build H, O, G, J or P. Those paths are unowned. |
| LANE | `DL-05 seeded_defect=PASSED` | Restore the seeded case; raise **SIG-18**; Blocking until the case fails again | Never delete the seeded case to make the suite green. |
| LANE | `DL-06 vacuous=1` (exit `2`) | The negative entry point asserts nothing. Write real negatives. | A vacuous suite is a FAIL, not a pass. |
| LANE | `DL-07 absent=1` | A canary fixture is missing. Treated as `accepted` — the gate is dead. | The train freezes until the canary returns `rejected`. |
| INTEGRATION | `CAN-DRIFT=MISSING` / `canary=MISSING` | **FAILED** run. Raise **SIG-13**. Run the §53.7 gap procedure over the window. Mark the window's records `gap-window`. | Never record the run as clean. A `gap-window` record is not evidence for any level until re-verified. |
| INTEGRATION | any canary `accepted`/`absent` | The train freezes: no promotion, no merges next cycle | Lifts only when L0 records what broke the gate and the canary returns `rejected`. |
| INTEGRATION | `DI-05 gates_proven<28` | A negative E2E stage did not fire | More serious than a failing positive: the system may have no gate at all. |
| INTEGRATION | GATE B closed | The cycle stays open; the failing check is fixed in the **owning lane** through a new lane PR at GATE A; GATE B re-runs whole | There is no partial GATE B and no "merge the other four". |
| INTEGRATION | a merge is wrong after the fact | `protocol/07-rollback.md` R1 (revert to `integration`) or R2 (revert a promotion to `main`) | The revert must itself pass the canary and boundary assertions of R1. |
| V1 | `DV-11 wrongly_claimed>0` | Out-of-scope work. Record it, revert it or defer it under `master/06-v1-scope.md` §9 | Building more is not finishing sooner. |
| V1 | `DV-09 layer_b_artifacts>0` | Layer B is a P2 deliverable. Remove the artefact. | Invariant 106 is absolute at the application and datasource layers. |
| PROGRAMME | `DG-06 zero_finding_runs>0` | Each such run is a failed run: SIG-13 and the gap procedure, per run | One failed run in the window holds the level. AT-102 admits no rounding. |
| PROGRAMME | `DG-08 zero_rate_flags=1` | The metric's owner writes the named answer on the closure record | An unanswered flag holds the level at NOT-MET. Do not widen the window. |
| PROGRAMME | `DG-09 silently_absent=1` | Mark the measure `unbaselined` **or** record its baseline. AT-046 permits the marker, never the silence. | A baseline cannot be captured retroactively (`master/06-v1-scope.md` R-5). |
| any | script crashes / times out / prints nothing | Fail closed. The level is NOT-MET. | Absence of output is never a pass (Spec §101 #80). |
| any | `unproven>0` on the negative battery | Repair the negative case before anything else | The check is treated as **absent**. Fail closed. |

---

## 11. L0 DECISIONS REQUIRED

Five items this file cannot resolve without inventing something the specification does not state. Each names
exactly what is missing and what is blocked until it is supplied. **No lane may resolve any of these.**

### DECISION 1 — The non-zero rejection floor, per level and per window

§103.13 and §103.9 state that zero rejections means the gates are not working, and that a very low rate may
mean rubber-stamping. Neither names a floor or a window. This file uses `window=10` for LANE and
INTEGRATION and `window=5` for PHASE as **placeholders that L0 must confirm or replace**, and treats the
floor as *strictly greater than zero* rather than a rate.

**Blocked until decided:** `DL-09`, `DI-09`, `DG-08` can flag but cannot calibrate. Record the chosen values
in `contracts/dod/windows.tsv` as **calibrated configuration** on the §95.4 pattern — the bootstrap log's
staleness window is *"the calibrated staleness window, initial value 7 days, changed only by a recorded
decision"* — so the numbers are refittable without a code change and every refit leaves a decision record.

### DECISION 2 — `BT-4` has no owning lane, so it has no Definition of Done — **Resolved: FD-002**

`master/04-phase-map.md` §2/§8 DECISION 1 recorded subsystems **H**, **O**, **G**, **J** and **P** as having
no owning lane in the frozen partition. That gap is now **Resolved: FD-002** (2026-09-02;
`lanes/L0-04-decisions-register.md` REG-001): **G** and **P** → **L0**; **H** → **L5**; **O** splits
**L1** (registries) / **L3** (jobs); **J** stays **deferred** — no lane builds it in this build track.
`make dod-phase PHASE=BT-4` no longer returns `UNDEFINED` for lack of an owning lane, and sync point `S4`
is no longer blocked on that ground.

### DECISION 3 — The universal floor's duration and per-product sequence

§96.6 says the floor *"is several weeks"* and gives no number, and `master/04-phase-map.md` DECISION 3
already raises it. `DG-04` can count 72 rows but cannot say when they are due.

**Blocked until decided:** `DG-03`'s `last_deadline`, and therefore `DOD-VERDICT` for the PROGRAMME level.
L0 must publish the per-product sequence in §96.5 criticality order with a date per row.

### DECISION 4 — Calendar anchors for `DG-02` and `DG-03`

Pre-onboarding deadlines are set from the Onboarding track, not from §98.2's week labels (D99). No absolute
dates exist anywhere in the plan; `master/04-phase-map.md` DECISION 5 names the same gap.

**Blocked until decided:** `DG-02 breached=` and `DG-03 late=` are uncomputable without a dated deadline per
product. L0 fixes the anchors once, in `registries/portfolio.yaml`, and never again.

### DECISION 5 — The status value for a revoked closure

`master/08-progress-tracking.md` §3.1 fixes a **closed nine-value enum** with no value meaning "was
`accepted`, later found wrong". §53.6's closure-quality rule — a finding closed without evidence of
remediation is reopened, not counted — has no expression in the enum, and this file's escape ledger (§1.2)
needs one.

**Blocked until decided:** escapes are recorded as files under `records/dod/escapes/**` but cannot change a
task's derived status. L0 either adds a tenth value (`reopened`) with its derivation rule, or rules that an
escape is always a **new** task with a new ledger file linking the old one. Either is fine; the ambiguity is
not. **No lane may pick.**

---

## 12. Citation self-verification

Every identifier in this file resolves in the specification. Run these from the repository root that holds
`Research/MultiProduct_MasterSpec_v4.0.md`; each prints only found ids, and the counts must match.

```bash
set -euo pipefail
SPEC="Research/MultiProduct_MasterSpec_v4.0.md"

# Acceptance tests cited here — expect 20 lines, one per id, none missing.
for id in AT-001 AT-002 AT-009 AT-029 AT-030 AT-033 AT-036 AT-037 AT-039 AT-046 \
          AT-047 AT-049 AT-051 AT-075 AT-090 AT-102 AT-103 AT-108 AT-109 AT-110; do
  grep -q "| $id |" "$SPEC" && echo "OK  $id" || echo "MISSING  $id"
done | grep -c '^OK' # expect: 20

# Edge case cited — expect 1
grep -c '| EC-109 |' "$SPEC"

# Signals cited — expect one line each
for s in SIG-13 SIG-18 SIG-39; do
  grep -q "$s" "$SPEC" && echo "OK  $s" || echo "MISSING  $s"
done | grep -c '^OK' # expect: 3   (SIG-13 failed reconciliations, SIG-18 verification-contract
                     #              coverage gaps, SIG-39 bootstrap exception unclosed)

# Sections cited — expect one hit each
for s in "### 31.2" "### 53.1" "### 53.7" "### 95.4" "### 96.4" "### 96.6" \
         "### 98.2" "### 99.4" "### 103.13" "### 103.14" \
         "## Section 100" "## Section 101" "## Section 102"; do
  printf '%-18s %s\n' "$s" "$(grep -c "^$s" "$SPEC")"
done

# The three declared counts this file asserts, read from the spec's own words.
grep -o 'contains \*\*110 tests\*\*\|contains \*\*111 invariants\*\*\|contains \*\*112 cases\*\*' "$SPEC" | sort -u

# The four load-bearing quotations. Note the regex on the first: §53.1 writes it plain and §31.2
# writes it bold (`**FAILED run**`), so a fixed-string grep finds only one of the two.
grep -cE 'FAILED run\*{0,2},? not a clean one' "$SPEC"              # expect: 2 (§53.1 and §31.2)
grep -c 'reconciler that finds nothing is assumed broken, never assumed clean' "$SPEC"  # expect: 1
grep -c 'Zero rejections means the gates are not working' "$SPEC"   # expect: 1
grep -c 'Very low may mean rubber-stamping' "$SPEC"                 # expect: 1
```

**Invariant numbers** cited in this file — `1, 3, 4, 8, 9, 12, 18, 20, 22, 23, 25, 44, 46, 47, 57, 75,
76, 77, 79, 80, 81, 84, 85, 106, 111` — are ordinal positions in §101's continuously numbered catalogue of
111. Verify any one of them by number:

```bash
awk '/^## Section 101\./,/^## Section 102\./' "$SPEC" | grep -E '^[0-9]+\. ' | sed -n '102p'
# expect the text of Spec §101 #102 (rebalance before permanent hiring)
awk '/^## Section 101\./,/^## Section 102\./' "$SPEC" | grep -cE '^[0-9]+\. '
# expect: 111
```

**`DI-07`'s three-way count agreement (`declared / unique-ids / id-cells`) is the discriminating check** for Section 100, because any two of the three can agree while the table contains a duplication or a narrowing. In `MultiProduct_MasterSpec_v4.0.md` at Phase 0 freeze all three agree at 110/110/110. The acceptance registry is generated from the **id set**, one file per test under `records/acceptance/AT-###.yaml` — never from the rendered table.

---

## 13. The whole file, for a lane developer, in one paragraph

You are done with a task when `make dod-task TASK=<id>` prints one line beginning
`DOD-VERDICT=MET LEVEL=task` and `make dod-negative LEVEL=task TASK=<id>` prints `unproven=0` — not before,
and not because the code looks right. Every acceptance criterion, not a subset. At least one negative test,
and it fired. No `TODO`, no empty body, no placeholder value. The count you delivered equals the count that
was declared. Nothing outside your `owns_paths:`. If any of that is false, the answer is `BLOCKED` with the
failing line pasted, and `BLOCKED` is a correct, cheap, respected outcome — a false `DONE` costs five lanes
a merge train. You do not declare your phase, your lane, the integration cycle, V1 or the programme done;
L0 does, with the commands in §3 through §7, and each of those levels re-runs your task's acceptance
criteria against the merged head, which is the only place `accepted` is earned. You may not edit
`contracts/dod/**`, `contracts/gate/**`, `contracts/fixtures/**`, `COUNTS.tsv`, `ownership.tsv`, any
canary fixture, or any other lane's path — a lane that can rewrite the thing judging it is not being judged.
And if your suite, your validator or your reconciler ever reports that it found nothing, that is not a clean
result: it is a failed one, and this whole protocol exists because of that single sentence.
