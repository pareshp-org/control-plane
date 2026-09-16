# 05 — THE MERGE GATE

**Status:** authoritative for the two gates named below. Conforms to the FROZEN PARTITION (`C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md`). Do not redesign.
**Spec basis:** `MultiProduct_MasterSpec_v4.0.md` — Section 26 (gates), Section 27 (four distinct events), Section 31 (verification contract), Section 33 (CI), Section 53 (reconciliation and the seeded canary), Section 95 (bootstrap and the activation checklist), Section 100 (AT-001 … AT-110), Section 101 (invariants 1 … 111), Section 102 (edge case catalogue, incl. EC-109), Section 103 (success metrics).

There are exactly **two** gates. A lane PR passes **GATE A** to enter `integration`. `integration` passes **GATE B** to enter `main`. Nothing else merges anywhere.

| | GATE A — LANE GATE | GATE B — INTEGRATION GATE |
|---|---|---|
| Direction | `lane/N/<phase>-<task>` → `integration` | `integration` → `main` |
| Frequency | Per lane PR, many per day | Once per merge cycle, after L1 → L4 → L2 → L3 → L5 |
| Question it answers | "Did this lane build its own thing correctly, inside its own boundary?" | "Do the five lanes compose into one system that matches the spec?" |
| Checks | 12 (`LG-01` … `LG-12`) | 12 (`IG-01` … `IG-12`) |
| Evaluated by | `make gate-lane LANE=<N> PR=<n>` | `make gate-integration CYCLE=<id>` |
| Pass output | `VERDICT=PASS GATE=lane …` | `VERDICT=PASS GATE=integration …` |
| Human requirement | One non-author Write-holding reviewer (`LG-09`) | L0 integrator sign-off as a decision record (`IG-11`) |
| On any FAIL | STOP. Do not merge. Open a blocker issue. Never re-run to get a different answer. | STOP. `main` does not move. The cycle is re-opened, not waived. |

---

## 1. Rule Zero — a check that can only pass is not a check

This is the load-bearing rule of the whole protocol, and the specification states it in five places:

| Where | What it says |
|---|---|
| §53.1, the seeded-canary rule | A permanent seeded drift record exists at all times and every reconciliation run MUST find it. "A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking." |
| AT-102 | The seeded reconciliation canary. A run reporting zero findings is a **failed** run, raises SIG-13, and triggers the gap procedure. "A reconciler that finds nothing is assumed broken, never assumed clean." |
| EC-109 | A silently-vacuous reconciliation run — a clean run that checked nothing. The canary is the only thing that exposes it. "Silence is never taken as health." |
| §31.2 | "A verification contract that cannot fail is not a contract." Every `verification/contract.yaml` declares a seeded-defect case the contract MUST fail; a run in which the seeded defect passes is a FAILED run. This is what stops `verify: exit 0` from satisfying coverage mapping. |
| §103 (plan-checker row) and §103 (review row) | "Zero rejections means the gates are not working." And: review rejection rate — "Very low may mean rubber-stamping." |

Carried into this protocol as three binding rules:

1. **Every gate check has a paired negative test** that mutates a known input and asserts the check flips to FAIL. A check with no passing negative test is treated as **not present** — the gate fails closed (invariant 80: every control is explicitly classified fail-closed or fail-open; this one is fail-closed).
2. **No output is a FAIL.** An empty result, a crashed script, a timed-out job, a `skipped` or `neutral` conclusion on a required context (§33.2 — such a conclusion on a merged PR is Blocking drift) all read as FAIL. Green is only ever an explicit, exact verdict line.
3. **Zero findings over a window is itself a finding.** A lane whose PRs have never been rejected, and an integration cycle whose negative battery has never caught anything, are reported on the gate record as suspect. `IG-11` makes this mechanical.

---

## 2. Where the gate lives, and why it lives there

| Path | Owner per FROZEN PARTITION | Holds |
|---|---|---|
| `Makefile` | **L0** (root files) | `gate-lane`, `gate-integration`, and nothing a lane can reach |
| `contracts/gate/**` | **L0** (`contracts/**`, frozen in Phase 0) | every gate script, every frozen expectation file, the ownership map, the suite map, the negative battery |
| `records/gate/**` | **L4** (`control-plane-records`) | append-only gate result records, one file per run (invariant 47) |

The gate is deliberately **not** written by any lane it judges. §53.1 states the principle for the reconciler and it applies here verbatim: "no control that can be rewritten by the credential it is checking is a control." A lane that could edit its own suite manifest, its own ownership row, or its own negative battery would be marking its own exam.

Two consequences, both enforced:

- `.github/workflows/**` belongs to **L2**. Therefore the CI job that runs the gate is a **mirror, never the verdict of record**. The verdict of record is the L0 run of `make gate-lane` / `make gate-integration`. `LG-12` and `IG-12` compare the two and fail on disagreement, which is how a lane quietly weakening the CI invocation is caught.
- The gate's reusable workflow is consumed **by pinned tag** under the `workflows/*` tag ruleset with an empty bypass-actor list (§33.2, invariant 85). A moved tag is Blocking drift.

### 2.1 Frozen expectation files (authored by L0 in Phase 0, never edited by a lane)

`contracts/gate/ownership.tsv` — the machine form of the FROZEN PARTITION path table:

```
# path-glob<TAB>lane
schemas/registry/**	1
schemas/product/**	1
registries/**	1
validators/registry/**	1
.github/workflows/**	2
templates/workflows/**	2
tools/evidence/**	2
reconciler/**	3
tools/provision/**	3
validators/drift/**	3
schemas/records/**	4
metrics/**	4
tools/records/**	4
access/**	5
infra/**	5
ops-vm/**	5
notify/**	5
assets/**	5
contracts/**	0
docs/**	0
CODEOWNERS	0
Makefile	0
```

`contracts/gate/lane-suite.tsv` — which command *is* each lane's suite. A lane cannot change its own row:

```
# lane<TAB>suite-command
1	make -C validators/registry test && make -C schemas test
2	make -C tools/evidence test && bash templates/workflows/test/run.sh
3	make -C reconciler test && make -C validators/drift test
4	make -C tools/records test && make -C metrics test
5	make -C access test && make -C infra test && make -C ops-vm test
```

`contracts/gate/expected-checks.txt` — the 24 check ids, 12 per gate. `contracts/gate/COUNTS.tsv` — the declared spec counts (Section 8 below). `contracts/gate/FIXTURES.sha256` — the digest of the frozen contract fixture tree.

---

## 3. GATE A — LANE PR → `integration`

Run from a clean checkout of the PR head, by L0 or by any agent, with the same result. All twelve are blocking; there is no advisory row.

| # | Check | What it proves | Command | Pass output (exact) |
|---|---|---|---|---|
| LG-01 | Rebase currency | The PR was rebased on current `integration`; the gate judged the code that will actually land | `bash contracts/gate/rebase-currency.sh --base origin/integration` | `LG-01 rebase PASS base=<sha7> behind=0` |
| LG-02 | **Lane-guard** | Every changed path belongs to this lane (PARTITION rule 1) | `bash contracts/gate/lane-guard.sh --lane <N> --base origin/integration --head HEAD` | `LG-02 lane-guard PASS lane=<N> changed=<n> foreign=0 unowned=0` |
| LG-03 | Contract immunity | `contracts/**`, `CODEOWNERS`, `Makefile`, `docs/**` untouched; a contract change came as a CCR, not a diff (PARTITION rule 2) | `bash contracts/gate/contract-immunity.sh --base origin/integration --head HEAD` | `LG-03 contract-immunity PASS l0_paths_touched=0` |
| LG-04 | No shared mutable file | Directory-per-item only; no lane appended to a shared index (PARTITION rule 3) | `bash contracts/gate/no-shared-mutable.sh --base origin/integration --head HEAD` | `LG-04 no-shared-mutable PASS modified_aggregates=0 added=<n>` |
| LG-05 | **Lane suite** | The lane's own suite, as L0 declared it, is green — including its seeded defect (§31.2) | `bash contracts/gate/lane-suite.sh --lane <N>` | `LG-05 lane-suite PASS lane=<N> tests=<n> failed=0 seeded_defect=DETECTED` |
| LG-06 | **Contract tests** | The lane's output satisfies the frozen contract, tested against the frozen fixtures — not against a locally edited copy | `bash contracts/gate/contract-tests.sh --lane <N>` | `LG-06 contract-tests PASS cases=<n> failed=0 fixtures_sha=<sha256-first12> fixtures_match=1` |
| LG-07 | **Negative tests** | Every one of LG-01 … LG-12 was proven able to fail on this head (Rule Zero) | `bash contracts/gate/negative-battery.sh --gate lane --lane <N>` | `LG-07 negatives PASS proven=12/12 unproven=0` |
| LG-08 | **Count integrity** | The lane did not silently narrow what it enumerates; declared counts equal actual counts | `bash contracts/gate/count-integrity.sh --scope lane --lane <N>` | `LG-08 counts PASS at=110/110/110 inv=111/111 ec=112/112 checks=24/24 narrowed=0` |
| LG-09 | **Human review** | A Write-holding human who is not the author approved the most recent reviewable push (invariants 8, 9) and no machine identity approved anything (invariant 18, D53) | `bash contracts/gate/human-review.sh --pr <n>` | `LG-09 human-review PASS approver=<login> author_distinct=1 stale_approvals=0 machine_approvals=0 codeowner=1` |
| LG-10 | Required-check honesty | No required context reported `skipped` or `neutral`; every required check ran for real (§33.2) | `bash contracts/gate/check-conclusions.sh --pr <n>` | `LG-10 check-conclusions PASS required=<n> skipped=0 neutral=0 missing=0` |
| LG-11 | No cross-lane import | The lane consumed other lanes only through `contracts/**` or a published artifact (PARTITION rule 4) | `bash contracts/gate/no-cross-import.sh --lane <N>` | `LG-11 no-cross-import PASS foreign_refs=0` |
| LG-12 | Mirror agreement | The CI mirror and the L0 run reached the same verdict | `bash contracts/gate/mirror-agree.sh --pr <n> --local .gate/lane.verdict` | `LG-12 mirror-agree PASS ci=PASS local=PASS delta=0` |

### 3.1 The one command that evaluates GATE A

```bash
# From a clean checkout of the PR head. LANE and PR are the only inputs.
git fetch origin integration
make gate-lane LANE=3 PR=417
```

`make gate-lane` runs LG-01 … LG-12 in order, writes every per-check line to `.gate/lane.log`, writes the aggregate to `.gate/lane.verdict`, and prints **exactly one line** on stdout:

```
VERDICT=PASS GATE=lane LANE=3 PR=417 HEAD=9f2c1ab checks=12/12 negatives=12/12 counts=OK canary=n/a ts=2026-08-27T11:04:19Z
```

**The unambiguous pass test — this and nothing else:**

```bash
mkdir -p .gate
make gate-lane LANE=3 PR=417 | tee .gate/lane.stdout
grep -Fq 'VERDICT=PASS GATE=lane' .gate/lane.stdout && test "$(wc -l < .gate/lane.stdout)" -eq 1 && echo GATE-A-OPEN || echo GATE-A-CLOSED
```

`GATE-A-OPEN` is the only string that authorises the merge. Anything else — `GATE-A-CLOSED`, no output, a non-zero exit, more than one line, a `VERDICT=FAIL`, a truncated log — is a closed gate. **STOP rule:** if the gate is closed, do not merge, do not re-run hoping for a different result, do not edit `contracts/gate/**` (you do not own it). Open a blocker issue naming the failing check id and paste the failing line from `.gate/lane.log`.

### 3.2 What a failure looks like

Failures are as literal as passes. Example, LG-02:

```
LG-02 lane-guard FAIL lane=3 changed=14 foreign=2 unowned=0
LG-02 foreign: schemas/registry/product.schema.json owner=lane1
LG-02 foreign: metrics/drift.rules.yaml owner=lane4
VERDICT=FAIL GATE=lane LANE=3 PR=417 HEAD=9f2c1ab checks=11/12 first_failure=LG-02
```

The lane's fix is always the same shape: remove the foreign path from the PR and file a Contract Change Request or a cross-lane request. It is never to widen `ownership.tsv`.

---

## 4. GATE B — `integration` → `main`

`main` is protected and releasable (PARTITION, Branch & merge model). GATE B runs once per cycle, after the full merge train L1 → L4 → L2 → L3 → L5 has landed. GATE B is not GATE A repeated: GATE A asks whether a lane is internally correct; GATE B asks whether the five lanes are the same system.

| # | Check | What it proves | Command | Pass output (exact) |
|---|---|---|---|---|
| IG-01 | Merge-train completeness and order | All five lanes landed this cycle in dependency order; no lane merged another lane's branch (PARTITION) | `bash contracts/gate/merge-train.sh --cycle <id> --base origin/main` | `IG-01 merge-train PASS lanes=5/5 order=1,4,2,3,5 out_of_order=0 cross_lane_merges=0` |
| IG-02 | **Full lane suites at merged head** | Every lane's suite still passes *after* the other four landed — the check a lane cannot run alone | `bash contracts/gate/lane-suite.sh --all` | `IG-02 lane-suites PASS lanes=5/5 tests=<n> failed=0 seeded_defects=5/5 DETECTED` |
| IG-03 | **Contract tests, provider-to-consumer** | Each consumer runs against the other lane's *real* output, not against the Phase-0 stub | `bash contracts/gate/contract-tests.sh --mode integrated` | `IG-03 contract-tests PASS pairs=<n> cases=<n> failed=0 stubbed=0 fixtures_match=1` |
| IG-04 | **Negative tests, full battery** | All 24 checks proven failable, plus the two spec-mandated seeded instruments | `bash contracts/gate/negative-battery.sh --gate integration --full` | `IG-04 negatives PASS proven=24/24 unproven=0 canary=FOUND seeded_defects=DETECTED` |
| IG-05 | **Count integrity, full scope** | Declared counts equal actual counts everywhere, and the reconciler recorded its per-registry comparison counts (§53.1) | `bash contracts/gate/count-integrity.sh --scope integration` | `IG-05 counts PASS at=110/110/110 inv=111/111 ec=112/112 checks=24/24 registries=<n>/<n> narrowed=0` |
| IG-06 | Invariant classification | Every one of the 111 invariants carries `mechanical` / `policy` / `review-held`, and every `mechanical` one names a live check or a real AT id (§101 preamble) | `bash contracts/gate/invariant-classification.sh` | `IG-06 invariant-classification PASS classified=111/111 mechanical=<n> dangling_refs=0 unclassified=0` |
| IG-07 | AT coverage and execution | Every AT this phase activates was **executed**, with a recorded result — never asserted (§100; AT-108, AT-109, AT-110 are executed, not claimed) | `bash contracts/gate/at-coverage.sh --phase <p>` | `IG-07 at-coverage PASS scheduled=<n> executed=<n> not_run=0 asserted_only=0` |
| IG-08 | Lane-guard replay | Replays LG-02 over the entire merged range, catching a foreign path that entered inside a merge commit | `bash contracts/gate/lane-guard.sh --replay --base origin/main --head origin/integration` | `IG-08 lane-guard-replay PASS commits=<n> foreign=0 unowned=0` |
| IG-09 | Independent control verifier | No machine identity in any CODEOWNERS; branch-protection and ruleset JSON match the committed template; the bypass-actor list is exactly what §40.1 and §33.2 declare — run under a **different credential** from the reconciler (§53.1) | `bash contracts/gate/independent-verifier.sh --credential $GATE_VERIFIER_TOKEN` | `IG-09 independent-verifier PASS repos=<n> machine_codeowners=0 template_diff=0 bypass_actors_exact=1 credential=verifier` |
| IG-10 | Artifact and check honesty | The digest that will reach production is the digest verified in staging (invariant 22); no required context is `skipped`/`neutral` anywhere in the range (§33.2) | `bash contracts/gate/artifact-honesty.sh --range origin/main..origin/integration` | `IG-10 artifact-honesty PASS digest_mismatches=0 rebuilt=0 skipped=0 neutral=0` |
| IG-11 | **Human sign-off + anti-rubber-stamp** | An L0 integrator signed off as a decision record, and the trailing-window rejection rate is non-zero (§103: "Zero rejections means the gates are not working") | `bash contracts/gate/human-signoff.sh --cycle <id> --window 10` | `IG-11 human-signoff PASS signer=<login> decision_record=<id> machine_approvals=0 window_cycles=10 rejections=<n>0 rubber_stamp_flag=0` |
| IG-12 | Mirror agreement + evidence | CI mirror agrees, and the gate wrote its own append-only record (invariant 47) | `bash contracts/gate/mirror-agree.sh --cycle <id> --local .gate/integration.verdict --emit-record` | `IG-12 mirror-agree PASS ci=PASS local=PASS delta=0 record=records/gate/<cycle>.yaml` |

### 4.1 The one command that evaluates GATE B

```bash
git fetch origin main integration
make gate-integration CYCLE=2026-08-27-a
```

Single-line stdout on success:

```
VERDICT=PASS GATE=integration CYCLE=2026-08-27-a HEAD=4bd90fe checks=12/12 negatives=24/24 counts=OK canary=FOUND lanes=5/5 signer=<login> ts=2026-08-27T18:22:07Z
```

**The unambiguous pass test:**

```bash
set -euo pipefail
mkdir -p .gate
make gate-integration CYCLE=2026-08-27-a | tee .gate/integration.stdout || true
grep -Fq 'VERDICT=PASS GATE=integration' .gate/integration.stdout \
  && grep -Fq 'canary=FOUND' .gate/integration.stdout \
  && grep -Fq 'negatives=24/24' .gate/integration.stdout \
  && test "$(wc -l < .gate/integration.stdout)" -eq 1 \
  && echo GATE-B-OPEN || echo GATE-B-CLOSED
```

`GATE-B-OPEN` is the only string that authorises `integration` → `main`. Note that `canary=FOUND` and `negatives=24/24` are asserted **separately and by name**, because those are the two tokens a broken gate is most likely to lose while still printing a verdict — the exact failure EC-109 describes.

**STOP rule:** a closed GATE B does not roll back the merge train and does not waive. The cycle stays open, the failing check id is fixed in the owning lane through a new lane PR at GATE A, and GATE B re-runs whole. There is no partial GATE B and no "merge the other four".

---

## 5. The negative battery — proving every gate can fail

`contracts/gate/negative-battery.sh` runs one mutation per check against a throwaway worktree, asserts the check returns FAIL, and restores. A check that stays PASS under its mutation is reported `unproven`, and an unproven check fails the gate — the gate cannot certify itself with an instrument it has not just seen bite.

| Check | Mutation injected | Required result |
|---|---|---|
| LG-01 | Reset the worktree one commit behind `origin/integration` | `LG-01 … FAIL behind=1` |
| LG-02 / IG-08 | Touch `schemas/registry/.negative-probe` from a lane-3 context | `LG-02 … FAIL foreign=1` |
| LG-03 | Append a comment line to `contracts/.negative-probe` | `LG-03 … FAIL l0_paths_touched=1` |
| LG-04 | Modify (not add) a file listed in `contracts/gate/aggregates.txt` | `LG-04 … FAIL modified_aggregates=1` |
| LG-05 / IG-02 | Un-break the lane's declared seeded-defect case so the suite goes green on broken input (§31.2) | `LG-05 … FAIL seeded_defect=PASSED` |
| LG-06 / IG-03 | Edit one frozen fixture byte | `LG-06 … FAIL fixtures_match=0` |
| LG-07 / IG-04 | Delete one negative case from the battery manifest | `LG-07 … FAIL unproven=1` |
| LG-08 / IG-05 | Drop one row from a registry the lane enumerates | `LG-08 … FAIL narrowed=1` |
| LG-09 | Replay an approval by the PR author; then an approval by the machine account | `LG-09 … FAIL author_distinct=0` then `… FAIL machine_approvals=1` |
| LG-10 / IG-10 | Add an `if: false` to a job emitting a required check name | `LG-10 … FAIL skipped=1` |
| LG-11 | Add an import of `reconciler/` into a lane-1 file | `LG-11 … FAIL foreign_refs=1` |
| LG-12 / IG-12 | Flip the local verdict file to `FAIL` while CI says `PASS` | `LG-12 … FAIL delta=1` |
| IG-01 | Re-order the cycle's merges to L3 before L1 | `IG-01 … FAIL out_of_order=1` |
| IG-06 | Point one `mechanical` invariant at a non-existent check name | `IG-06 … FAIL dangling_refs=1` |
| IG-07 | Mark one scheduled AT `asserted` instead of `executed` | `IG-07 … FAIL asserted_only=1` |
| IG-09 | Add the machine account to a scratch CODEOWNERS in the verifier's sandbox | `IG-09 … FAIL machine_codeowners=1` |
| IG-11 | Present a sign-off by the author of the cycle's largest diff | `IG-11 … FAIL machine_approvals=0 self_signoff=1` |
| **AT-102** | Remove the seeded canary drift record from the comparison set, then run reconciliation | run reports `canary=MISSING` → **FAILED run**, SIG-13 raised, gap procedure (§53.7) |

Run standalone at any time:

```bash
bash contracts/gate/negative-battery.sh --gate integration --full
# NEGATIVE-BATTERY PASS proven=24/24 unproven=0 canary=FOUND seeded_defects=DETECTED
```

Any line containing `unproven=` with a value other than `0` closes both gates.

---

## 6. The lane-guard result, stated exactly

`LG-02` is the single mechanical expression of PARTITION rule 1. Its logic is three lines and admits no judgment:

```bash
set -euo pipefail
git diff --name-only "origin/integration...HEAD" | while read -r p; do
  owner="$(bash contracts/gate/owner-of.sh "$p")"     # returns 0..5, or "none"
  [ "$owner" = "$LANE" ] || echo "foreign: $p owner=lane$owner"
done
```

| Result | Meaning | Gate |
|---|---|---|
| `foreign=0 unowned=0` | every changed path is owned by this lane | PASS |
| `foreign>0` | the lane touched another lane's or L0's path | FAIL — remove the path; file a CCR |
| `unowned>0` | the lane created a path no row in `ownership.tsv` claims | FAIL — an unowned path is a future merge conflict; L0 assigns ownership first |

`unowned>0` is a failure, not a warning. PARTITION rule 1 is "one owner per path", and a path with zero owners violates it in the direction nobody notices until two lanes both create it.

---

## 7. Human review — what "reviewed" has to mean

The human requirement is different at each gate and neither is satisfiable by a machine.

**GATE A (`LG-09`).** One approval from a Write-holding human who is not the PR author, on the **most recent reviewable push** (invariant 9: no self-approval, enforced mechanically by requiring approval of the most recent reviewable push). CODEOWNERS review satisfied. Zero approvals from any machine identity — invariant 18 puts merge and approve outside machine authority entirely, and D53's no-machine-approval-of-gates rule stands. Invariant 8: every normal change receives independent review from someone other than its author.

**GATE B (`IG-11`).** The L0 integrator signs the cycle off, and the sign-off is a decision record in `records/decisions/` (§97), not a chat message. The signer must not be the author of the cycle's largest diff. Gate 2 approval and production approval are separate events (§27, invariant 12); GATE B is the merge-authorising one and confers nothing about production.

**The anti-rubber-stamp clause.** `IG-11` reports `rejections=<n>` over a trailing ten-cycle window and raises `rubber_stamp_flag=1` when that count is zero. §103 states it for the plan-checker — "Watch the reason mix, not the rate. Zero rejections means the gates are not working" — and for review: "Very low may mean rubber-stamping." A flagged window does not by itself close GATE B; it forces a named written answer on the gate record explaining why ten clean cycles are real. Note the opposite protection too (§17, restated §103): a reviewer who says they do not understand a change is behaving correctly and is never penalised for it; the response is pairing, not a second mandatory reviewer.

**Where headcount cannot supply a second human**, the gate is not silently relaxed. It runs under a declared, expiring bootstrap exception in `exceptions.yaml` (§95.2) naming the gate, the repositories, the compensating control, an owner, an expiry and a deactivation trigger. An exception without an expiry is rejected by CI (invariant 77). The activation checklist of §95.4 is executed for real — including its negative tests — when the headcount threshold arrives: "A self-approved PR fails branch protection; a Read-only approval does not satisfy it; a Write-holding cross-reviewer approval does."

---

## 8. Count integrity — the check against a lane that quietly built less

Five AI developers with no shared context fail in one characteristic way: a lane implements 40 of 110 things and reports success, because nothing anywhere holds the number 110. `contracts/gate/COUNTS.tsv` holds it, frozen, transcribed from the specification:

| Registry | Declared count | Spec statement |
|---|---|---|
| Acceptance tests | **110**, AT-001 … AT-110, no gaps, no duplicates | §100: "The catalogue contains **110 tests**, numbered AT-001 to AT-100 plus AT-101 to AT-103 … AT-104 to AT-107 … and AT-108 to AT-110" |
| Invariants | **111**, numbered continuously 1 … 111 | §101: "The catalogue contains **111 invariants**, numbered continuously and grouped by theme" |
| Edge cases | **112**, EC-1 … EC-112 | §102: "The catalogue contains **112 cases**, numbered EC-1 to EC-112 and grouped into eleven domains" |
| Gate checks | **24**, LG-01 … LG-12 and IG-01 … IG-12 | this document, `contracts/gate/expected-checks.txt` |
| Reconciler comparison rows | per-registry, recorded each run | §53.1: "Every run additionally records its per-registry comparison counts … so that a silently narrowed comparison is itself visible drift" |

The check asserts **three numbers agree** for each registry — the declared count, the count of unique ids, and the count of id occurrences in row position — because any two of them can agree while the artifact is wrong:

```bash
bash contracts/gate/count-integrity.sh --scope integration
# COUNT-INTEGRITY PASS at=110/110/110 inv=111/111 ec=112/112 checks=24/24 registries=9/9 narrowed=0
```

Read `at=110/110/110` as `declared/unique-ids/id-cells`. All three must be identical.

**The three-way count is the only discriminating check.** A table with a duplicated row passes a unique-id count and passes a row count, but any downstream system that machine-parses it into a keyed store silently miskeys the duplicate. In `MultiProduct_MasterSpec_v4.0.md` at Phase 0 freeze all three counts agree at 110/110/110 — the spec is clean, and the three-way check is the control that detects any future regression introduced during a spec amendment:

```bash
awk '/^## Section 100\./{found=1} found{print} /^## Section 101\./{if(found && NR>1)exit}' Research/MultiProduct_MasterSpec_v4.0.md > /tmp/s100.txt
echo "rows=$(grep -c '^| AT-' /tmp/s100.txt) unique=$(grep -o '^| AT-[0-9]\{3\}' /tmp/s100.txt | sort -u | wc -l) cells=$(grep -o '| AT-[0-9]\{3\} |' /tmp/s100.txt | wc -l)"
# rows=110 unique=110 cells=110
```

The operational consequence for the build: the control-plane acceptance-test registry is generated from the **id set**, one file per test (`records/acceptance/AT-###.yaml`), never from the rendered table — directory-per-item, per PARTITION rule 3 — and `IG-05` verifies the directory holds exactly 110 files whose ids are exactly `AT-001` … `AT-110`.

---

## 9. Failure taxonomy and STOP rules

Written for an implementer with no repo context and no judgment authority. Find the row, do the thing, stop.

| Symptom | Classification | Action | STOP rule |
|---|---|---|---|
| `VERDICT=FAIL`, `first_failure=LG-02` or `IG-08` | Boundary violation | Remove the foreign path from the PR; if the lane genuinely needs it, file a Contract Change Request | Do not edit `ownership.tsv`. Do not merge. |
| `seeded_defect=PASSED` | The verification instrument stopped discriminating (§31.2) | Restore the seeded-defect case; raise SIG-18; the product is Blocking until the case fails again | Never delete the seeded case to make the suite green. |
| `canary=MISSING` | The reconciler stopped looking (AT-102, EC-109) | Treat the run as a **FAILED** run; raise SIG-13; run the §53.7 gap procedure over the window; mark records produced in the window `gap-window` | Never record the run as clean. A gap-window record is not evidence for any gate until re-verified. |
| `unproven>0` | A gate check cannot be proven able to fail | Repair the negative case before anything else | The check is treated as absent. Fail closed. |
| `narrowed=1` or a count mismatch | A lane silently enumerates less than it declares | Diff the registry against `COUNTS.tsv`; restore the missing items | Do not adjust `COUNTS.tsv` to match the code. |
| `machine_approvals>0` | A machine approved a gate (invariant 18, D53) | Dismiss the approval; obtain a human one; record the incident | The merge does not proceed on a machine approval under any framing. |
| `skipped=1` / `neutral=1` on a required context | The check that appears green never ran (§33.2) | Remove the `if:`/path filter from the job emitting the required name | A `skipped` or `neutral` conclusion on a required context of a merged PR is Blocking drift. |
| `delta=1` on mirror agreement | CI and the L0 run disagree | Investigate the workflow diff before anything else; a workflow-file change pushed by a machine identity is Blocking drift (§53.1) | Never take the greener of the two verdicts. |
| Gate script crashes, times out, or prints nothing | Instrument failure | Fail closed; the gate is CLOSED | Absence of output is never a pass (Rule Zero, rule 2, §1). |
| `rubber_stamp_flag=1` | Ten cycles with zero rejections | Write the named explanation on the gate record | Do not silence the flag by widening the window. |

---

## 10. What the gate writes

Every run — pass or fail — writes one file, one run per file, append-only, never overwritten (invariant 47; §97 directory-per-item; PARTITION rule 3, which is why five lanes' gate records never conflict):

```
records/gate/lane/2026-08-27/PR-417-9f2c1ab.yaml
records/gate/integration/2026-08-27/CYCLE-2026-08-27-a.yaml
```

Each record carries: gate, lane or cycle, head SHA, the twelve per-check lines verbatim, the negative-battery result, the count triples, the human approver or signer, the trailing rejection count, and the verdict line. A gate run with no record is itself a failure (`IG-12`, `record=` must name an existing path) — the same discipline §95.4 puts on the weekly bootstrap log: "An evidence base that nothing makes happen is reconstructed from memory at exactly the moment the closure discipline exists to prevent that."

---

## 11. The gate in one paragraph, for a lane developer

Rebase on `integration`. Run `make gate-lane LANE=<N> PR=<n>`. If the single output line does not start `VERDICT=PASS GATE=lane`, you do not merge — read `.gate/lane.log`, find the first `FAIL` line, find its row in Section 9, do exactly what that row says, and open a blocker issue if the row tells you to. You may not edit `contracts/gate/**`, `ownership.tsv`, `lane-suite.tsv`, `COUNTS.tsv`, or any other lane's paths; a PR that does fails `LG-02` or `LG-03` before anything else runs. Your suite must contain a seeded defect that it fails, or `LG-05` reports `seeded_defect=PASSED` and the gate closes: a suite that cannot fail is not a suite.
