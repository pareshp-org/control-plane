# L0-99 — COHERENCE REVIEW OF LANE L0

> **SUPERSEDED — 2026-09-02**  
> H-05 correction column verified wrong in all nine rows. 20 of 25 cited anchors drift.  
> **Do not act on H-05 corrections.** Re-derive all findings against current files.

**Reviewed:** `L0-00-charter.md`, `L0-01-phase-0-contracts.md`, `L0-02-lane-guard.md`, `L0-03-merge-train.md`,
`L0-04-decisions-register.md`, `L0-05-integration-gate.md`, `L0-06-bootstrap-mode.md`, `L0-07-onboarding-track.md`
(19,450 lines), plus `PARTITION.md`.
**Verified against:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).
**Tasks in scope:** 103 (9 + 23 + 9 + 12 + 8 + 15 + 12 + 15).

---

## VERDICT

# BLOCKED

Seven defects prevent dispatch. Five of them are **mechanical dead ends** — a task whose stated expected output
cannot be produced by the commands the task itself gives — and two are **cross-file contradictions** where one L0
file executes as settled a decision another L0 file records as `P0 open`.

The lane's controls are complete (103/103 tasks carry acceptance criteria, a SELF-VERIFY block and a STOP rule) and
its citation integrity is unusually good (see §6). The blockers are arithmetic, sequencing and ownership, not
substance.

---

## 1. BLOCKING DEFECTS — worst first

---

### B-01 · `L0-05-integration-gate.md`, ALL FIFTEEN TASKS · the gate writes into the frozen contract tree and never re-freezes

**Problem.** `L0-05-01` declares its dependency as *"L0-01 (`contracts/**` authored and frozen)"* and then writes
`contracts/gate/expected-checks.txt`, `ownership.tsv`, `lane-suite.tsv`, `aggregates.txt`. `T02`–`T15` add
`COUNTS.tsv`, `COUNTS.rules.tsv`, three id-index files, `SPEC_PATH`, `SPEC.sha256`, `spec-anomalies.tsv`,
`at-activation.tsv`, `phase-order.tsv`, `PHASE`, `invariant-classification.tsv` and fourteen `.sh` files.

`L0-00-04` defines the freeze as:

```
find contracts -type f | LC_ALL=C sort | xargs sha256sum | sha256sum
```

— **every file under `contracts/`, without exception.** `L0-P0-023` records that hash into `contracts.sha256`.
No task in `L0-05` runs `make freeze`, and `L0-05-14` states explicitly *"freeze, promote-check and merge-train
targets stay exactly as authored."*

**Consequences, all of them mechanical:**

| Caller | Where | What it prints from `L0-05-01` onward |
|---|---|---|
| `make train-preflight` | `L0-03-01` | `CONTRACTS-DRIFT` → `PREFLIGHT FAIL` → **no cycle can be opened** |
| merge-train step 5 | `L0-03-06` crit 3 | `CONTRACTS-DRIFT` after every lane merge |
| promotion gate `P1` | `L0-03-09` | `GATE-FAIL P1 contracts not frozen` → **no promotion, ever** |
| `make guard-verify` | `L0-02-09` crit 5 | last line is not `CONTRACTS-FROZEN OK` |
| daily 10:30 integrity check | `L0-00` §8.1 | fails every day |

**`contracts/gate/PHASE` makes it permanent.** `L0-05-04` writes `Ph1` into it and `L0-05` §12 states *"L0, at each
§98 phase completion check"* advances it. A **mutable file inside the tree whose hash is asserted to be immutable**
guarantees `CONTRACTS-DRIFT` at every phase boundary even if the initial creation were re-frozen.

**Second-order.** `L0-01` §6.1 makes the permitted list of post-freeze operations exhaustive: change is *"L0 only,
in the 17:00 window, under an approved CCR, a decision record, a green harness, a re-freeze, and a new tag."*
`L0-05` performs none of the six. `L0-01` §8.6's re-freeze recipe is never invoked.

**Correction.** One of:
(a) move the gate tree out of `contracts/` to an L0-owned root path (`gate/**` added to `lane-paths.tsv` under
L0D-04) and keep `gate/v1.0.0` as its tag; **or**
(b) redefine `make freeze` / `make promote-check` in `L0-00-04` to hash `contracts/` **excluding** `contracts/gate/`
and `contracts/ci/`, and freeze the gate tree under its own `gate.sha256` + `gate/v1.0.0` (which `L0D-IG-10` already
half-designs); **or**
(c) keep the tree where it is, run `make freeze` as the last step of `L0-05-15`, and move `PHASE` out of
`contracts/` entirely.
In every case `contracts/gate/PHASE` must not live inside any hashed tree. Record the choice as an L0 decision and
add a row to `L0-04` `register.tsv`.

---

### B-02 · `L0-05-14` · the closing rehearsal can never pass, and §11 makes the whole gate untrusted until it does

**Problem.** `L0-05-14` acceptance criterion 6 and its SELF-VERIFY require, *exactly*:

```
rehearsal=[REHEARSAL PASS closed=12/12]
```

`rehearse.sh` obtains that only if, for each of twelve iterations, every check **except the one deliberately broken**
passes. Three checks are designed by this same file to fail unconditionally until L0 answers open decisions:

| Check | Why it always FAILs | Stated where |
|---|---|---|
| `IG-05` | `COUNTS.tsv` carries **both** `ct_pairs_p00` and `ct_pairs_p01`, and `count-integrity.sh` increments `NARROW` whenever both are present | `L0-IG-D1`; `L0-05-03` crit 7: *"`narrowed=1` or higher — never `narrowed=0`"* |
| `IG-06` | `unclassified` is non-zero until subsystem **O** is assigned; §101 also authors the classification at phase **G2**, outside the five-lane build | `L0-IG-D3`; `L0-05` §5 |
| `IG-07` | `tools/at/run-at.sh` is owned by no lane, so every scheduled AT reports `not_run` | `L0-IG-D2`; `L0-05-05` crit 5 |

Plus `IG-03`, which fail-closes on a missing `contracts/harness/**` (see **B-04**), and `IG-10`, which fail-closes on a
missing `e2e/run.sh` (also **B-04**).

So `first_failure` is `IG-03` or `IG-05` on **every** iteration, `OK` never exceeds 0, and `closed=12/12` is
unreachable. `L0-05` §11 then binds: *"Nothing here is trusted until `rehearse.sh` prints `REHEARSAL PASS
closed=12/12`."* `L0-05-14`'s STOP rule says *"do not promote anything."*

**This is not the intended fail-closed behaviour.** The gate is correctly designed to close on an unanswered
decision; the **rehearsal** is a different instrument, and it has been written so that it inherits those closures and
can therefore never certify the gate. There is no route out named in `T14`.

**Correction.** `rehearse.sh` must assert *"breaking check X moves `first_failure` to X"* against a **baseline
first_failure**, not against a green run — i.e. record the baseline `first_failure` with nothing broken, then for each
`IG-nn` at or before the baseline, break it and assert `first_failure` moves to it; for checks after the baseline,
record `BLOCKED-BY-<baseline>` rather than `NOT-CLOSED`. State the expected output as
`REHEARSAL PASS closed=<n>/<n> blocked_by=IG-nn`. Alternatively, gate `T14` on the closure of `L0-IG-D1`, `-D2` and
`-D3` and say so in its Dependencies row.

---

### B-03 · `L0-04-decisions-register.md` **REG-002** vs `L0-02-lane-guard.md` §4 · the same decision is `P0 open` and `resolved` in two L0 files

**Problem.** `REG-002` is `P0`, `state=open`, and its `blocks` field names **`L0-02-05,L0-02-06,L0-02-07`**. Its
body records four incompatible answers, three claiming to be in force:

| Document | Claim | Status per REG-002 |
|---|---|---|
| `master/07` §7 DEC-02 | *"option 3 is in force as the interim control"* | claimed in force |
| `lanes/L0-02` §4 | `L0D-LG-1/-2/-3` — content frozen in `contracts/ci/`, location stays L2's, placed once in Phase 0 | **claimed resolved** |
| `protocol/10` §2.1 | *"D-L2-06 is resolved here — option (b) … **Resolution, binding.**"* | claimed binding, **incompatible with `L0-02` §4** |
| `master/01` §9 `LA-02` | forbids creating the guard workflow file until L0 decides | open |

`REG-002` concludes: *"Nothing is in force, and that is the finding."* Yet `L0-02-05/T06/T07` execute
`L0D-LG-1..3` with no reference to `REG-002` and no gate on it.

**A fifth disagreement rides along, inside L0.** `REG-002` records that `protocol/10` routes `.github/workflows/**`
to L0 in CODEOWNERS while `L0-00-01`'s CODEOWNERS body routes `/.github/workflows/` to `@LANE2_REVIEWER`. Both
cannot be true of one file.

**The gate this creates.** `L0-04-07` wires `make decisions-gate PHASE=$(cat contracts/gate/PHASE)` as the **first**
step of `promote-check`, and its own criterion 5 states the expected output:

```
DECISIONS-GATE FAIL: 14 P0/P1 entries still open at Ph0 (overdue=16)
```

(Verified: 2 `P0` + 12 `P1` = 14; 16 rows gate at `Ph0`.) So from `L0-04-07` onward **`make promote-check` fails**,
which fails `train-preflight`, promotion `P1` and `guard-verify` — independently of **B-01**, and by design.

**Correction.** Either (i) close `REG-002` and `REG-001` by decision record before any lane branch is created, and
add `REG-002` to `L0-02-05/T06/T07`'s Dependencies rows so the ordering is visible; or (ii) if `L0D-LG-1..3` *is*
the answer, say so: mark `REG-002` `closed` with `record=` pointing at the decision file, retire the three superseded
claims by name, and reconcile `L0-00-01`'s CODEOWNERS line with it. `L0-02` §4 must cite `REG-002` either way.

---

### B-04 · `L0-05-09`, `L0-05-07`, `L0-05-14` · four artifacts the gate executes are created by no task and owned by no lane

| Artifact | Read/executed by | Created by | Owner under `lane-paths.tsv` |
|---|---|---|---|
| `e2e/run.sh` | `run-integration.sh` step 0 (`L0-05-14`) | **nothing** | `X */*` → **UNASSIGNED** |
| `e2e/verdict.sh` | precondition of `IG-10` (`L0-05` §3.2, §7.9.1) | **nothing** | **UNASSIGNED** |
| `contracts/harness/run-contract-tests.sh` | `contract-tests.sh` (`L0-05-07`, line 1404) | **nothing** — `L0-P0-001` creates nine `contracts/` subdirectories and `harness` is not among them | L0 (`contracts/*`) |
| `contracts/harness/pairs.tsv` | `contract-tests.sh` (line 1405), `L0-IG-D1` | **nothing** | L0 |

**And `L0-05-09` line 1790 asserts a false ownership fact:**

> *"it lives at `e2e/` in `control-plane`, is **L0-owned in CODEOWNERS**, is not a lane path, and creates no
> lane-guard conflict."*

`lane-paths.tsv` (`L0-00-03`) places `X<TAB>*/*` before the `0<TAB>*` catch-all precisely so that a nested path no
rule claims resolves to `X`. `owner_of("e2e/run.sh")` therefore returns `X`, and:

* `lane-guard.sh` reports `LANE-GUARD VIOLATION: e2e/run.sh is an UNASSIGNED path (escalate to L0, L0D-04)`;
* `train-owners.sh` — the promotion gate's `P2` — prints `TRAIN-OWNERS FAIL: 1 unassigned path(s)`;
* `L0-00` §2.3 is explicit: *"A path that `lane-paths.tsv` assigns to no lane is **blocked for everyone**."*

`L0-05` correctly routes `tools/at/**` through `L0-IG-D2` and `verification/acceptance/**` likewise. `e2e/**` and
`contracts/harness/**` get no such treatment — they are simply assumed to exist and to be owned.

**Correction.** Add a `DECISION REQUIRED — L0-IG-D5` covering `e2e/**` and `contracts/harness/**` on the same
pattern as `L0-IG-D2`, with the fail-closed interim behaviour stated; or extend `lane-paths.tsv` under L0D-04 and
add a task that authors both harnesses. Delete the "creates no lane-guard conflict" sentence at line 1790 — it is
false as `lane-paths.tsv` is written.

---

### B-05 · `L0-02-07` · L0 commits into `.github/workflows/**`, which `PARTITION.md` gives to L2 exclusively

**Problem.** `L0-02-07` runs:

```bash
cp contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml
git add .github/workflows/lane-guard.yml
git commit -m "L0-02-07: place the frozen lane-guard workflow (one-time, L0D-LG-3)"
```

`PARTITION.md` §"The five build lanes" gives `.github/workflows/**` to **L2, exclusively**; L0's OWNS column is
`contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile`. Rule 1: *"A lane PR touching a foreign path FAILS
the lane-guard check. No exceptions."*

Run the lane's own guard on it: `owner_of(".github/workflows/lane-guard.yml")` matches `2<TAB>.github/workflows/*`
→ owner `2`. For `LANE=0` the `GUARD-CRITICAL` branch is skipped (`if [ "$LANE" != "0" ]`), so the path falls
through to the ownership test and reports `FOREIGN-PATH`. **`make lane-guard LANE=0 BASE=... HEAD=integration` fails
on L0's own commit.** It is latent today only because L0 pushes directly to `integration` and the workflow triggers
on `pull_request`.

`L0-02` §4 argues the case honestly (`L0D-LG-1..3`) and says *"Nothing in PARTITION.md is contradicted."* That is not
accurate: PARTITION's OWNS column is a set, not a set-with-exceptions, and `L0-04` `REG-002` option **A** exists
precisely to add the missing exact-file rule.

**Correction.** This is `REG-002` option A or D. If D (`L0-02`'s answer) is chosen, `lane-paths.tsv` still needs the
exact-file row `0<TAB>.github/workflows/lane-guard.yml` **ordered before** `2<TAB>.github/workflows/*`, plus the
matching CODEOWNERS line, plus a note in `L0-00-03` that the manifest now has one more rule. Until then, no L0 task
may commit that path.

---

### B-06 · `L0-00-03` · the partition manifest has 22 rules; the acceptance criterion and SELF-VERIFY assert 21

**Problem.** The `printf` block writes:

| Group | Rules |
|---|---|
| lane 1 | `schemas/registry/*`, `schemas/product/*`, `registries/*`, `validators/registry/*` = 4 |
| lane 2 | `.github/workflows/*`, `templates/workflows/*`, `tools/evidence/*` = 3 |
| lane 3 | `reconciler/*`, `tools/provision/*`, `validators/drift/*` = 3 |
| lane 4 | `schemas/records/*`, `metrics/*`, `tools/records/*` = 3 |
| lane 5 | `access/*`, `infra/*`, `ops-vm/*`, `notify/*`, `assets/*` = 5 |
| lane 0 | `contracts/*`, `docs/*` = 2 |
| residual | `X */*` = 1 |
| catch-all | `0 *` = 1 |
| **total** | **22** |

Acceptance criterion 1: `grep -vc '^#' lane-paths.tsv` → **`21`**. SELF-VERIFY expects `rules=21`. Both are wrong by
one. The SELF-VERIFY's *"Expected output, exactly"* block therefore cannot be produced, and `L0-00-03`'s STOP rule
is the gate on `L0-00-04` and `L0-00-09`, which is the gate on every lane branch.

**Propagated.** `L0-02` §5 reproduces the manifest and asserts *"the manifest keeps exactly **twenty-one** rules and
L0-00-03's acceptance criteria remain true"*; `L0-02` §8's worked error message prints `manifest … — 21 rules`.

**Correction.** Change `21` → `22` in `L0-00-03` criterion 1 and its SELF-VERIFY; change both statements in
`L0-02` §5 and the sample output in `L0-02` §8. If **B-05** is fixed by adding the exact-file rule, the number
becomes `23` and all four places move again — fix them together.

---

### B-07 · `L0-P0-008` · register row count off by one, and §7.2's whole column is wrong from task 008 to 017

**Problem.** Registration order and cumulative totals:

| Task | Registers | Actual total | §7.2 / criterion says |
|---|---|---|---|
| L0-P0-003 | 1 | 1 | 1 ✓ |
| L0-P0-004 | 1 | 2 | 2 ✓ |
| L0-P0-005 | 1 | 3 | 3 ✓ |
| L0-P0-006 | 1 | 4 | 4 ✓ |
| L0-P0-007 | 1 | 5 | 5 ✓ |
| **L0-P0-008** | **3** | **8** | **7 ✗** |
| L0-P0-009 … L0-P0-017 | 1 each | 9 … 17 | 8 … 16 ✗ |
| L0-P0-018 | 2 | 19 | 19 ✓ (a `+3` jump from a `16` that should be `17`) |
| L0-P0-019 | 1 | 20 | 20 ✓ |
| L0-P0-020 | 3 | 23 | 23 ✓ |

`L0-P0-008` acceptance criterion 6 — *"Register now holds seven rows … `7`"* — fails on a correctly executed task.
Its STOP-rule discipline then halts Phase 0 at task 8 of 23.

The grand total is right: 5+3+1+1+1+1+1+1+1+1+1+2+1+3 = **23**, matching §2's twenty-three contracts. Only the
cumulative column is wrong.

**Correction.** `L0-P0-008` criterion 6 → `8`. §7.2 "Register rows after" column: `008=8, 009=9, 010=10, 011=11,
012=12, 013=13, 014=14, 015=15, 016=16, 017=17`. Leave 018–020 unchanged.

---

## 2. HIGH — a stated expected output that cannot be produced

---

### H-01 · `L0-02-02` criterion 3 and SELF-VERIFY `ok_str` · returns 2, expects 1

`grep -c 'LANE-GUARD OK' lane-guard.sh` matches **two** lines of the §6 script:

* line 189 — `#   0  no violations                       (last line: "LANE-GUARD OK")`
* line 451 — `  printf 'LANE-GUARD OK\n'`

Criterion 3 and the *"Expected output, exactly"* block both say `1`.
**Correction:** `grep -c "^  printf 'LANE-GUARD OK" lane-guard.sh` → `1`, or change the expected value to `2`.
(The companion `fail_str` check is correct: the comment says `N violation(s)`, the printf says `%s violation(s)`.)

### H-02 · `L0-02-02` criterion 7 · guard-critical count returns 12, expects 13

```
grep -A3 "^CRITICAL=" lane-guard.sh | tr " " "\n" | grep -c "[a-z]"
```

The first token is `CRITICAL="CODEOWNERS` — entirely upper-case, so `grep "[a-z]"` does not count it. The twelve
counted are `Makefile`, `contracts.sha256`, `lane-paths.tsv`, `lane-owners.tsv`, `lane-guard.sh`,
`lane-guard-exceptions.tsv`, `lane-guard-selftest.sh`, `codeowners-gen.sh`, `lane-guard-ruleset.json`,
`.github/workflows/lane-guard.yml`, `contracts/ci/lane-guard.yml.frozen`, `contracts/ci/lane-guard.contract.md`.
The list genuinely has 13 entries; the *command* returns 12.
**Correction:** `grep -A3 '^CRITICAL=' lane-guard.sh | sed 's/^CRITICAL="//' | tr ' ' '\n' | grep -c .` → `13`.

### H-03 · `L0-02-05` criterion 1 and SELF-VERIFY · generator emits 34 rules, expects 33

`codeowners-gen.sh` emits: 1 default + 18 lane trees (4+3+3+3+5) + 2 L0 trees + 13 guard-critical = **34**, and
`grep -vc '^#\|^$' "$OUT"` counts exactly those. The document's own parenthetical —
*"(33 = 1 default + 18 lane trees + 2 L0 trees + 13 guard-critical files…)"* — sums to 34.
**Correction:** `CODEOWNERS-GEN OK 34 rules` in criterion 1, in the SELF-VERIFY expected block, and in the
parenthetical. Criterion 7 (`tail -13`) is unaffected and correct.

### H-04 · `L0-03-01` · the cycle-log header ends up twice; three criteria assert it appears once

The prose says the markers *"immediately **replac[e]** the hand-written cycle-log table that L0-00-08 placed
there"*, but the Python only **inserts** `BEGIN\nEND\n` *before* the header it finds:

```python
s = s[:i] + "<!-- CYCLE-LOG:BEGIN -->\n<!-- CYCLE-LOG:END -->\n" + s[i:]
```

`make train-log` then emits a fresh header between the markers while the original survives after `END`. Result:

* `L0-03-01` criterion 9 (`grep -c 'cycle | date | L1 | L4 | L2 | L3 | L5'` → `1`) returns `2`;
* `L0-03-01` SELF-VERIFY prints `header=2` against an expected `header=1`;
* `L0-00-08` criterion 5 (`… | 1`) also becomes `2`.

Idempotence (`stable=YES`) is unaffected.
**Correction:** delete the header and its separator line during marker insertion (`s[:i] + markers + s[j:]` where
`j` skips the two table lines), or relax the three criteria to `>= 1`.

### H-05 · all four files that state it · *"Appendix A's `D1`…`D109`"* is false — the register runs `D1`…`D112`

Verified: `Appendix A — Consolidation Decision Register` contains **112** rows, `D1` … `D112`; `D110`, `D111` and
`D112` are real entries (Layer B surface naming, the declared working calendar, the coverage validator's input).

Stated as `D1…D109` in:
`L0-00-charter.md` §4 · `L0-02-lane-guard.md` §11 · `L0-04-decisions-register.md` §2 · `L0-05-integration-gate.md` §4.

This is a stated count that is not true, which is the exact thing **D44** (*"every stated count is true"*) and
`L0-05-02`'s `COUNTS.tsv` exist to prevent — and `COUNTS.tsv` has no `decisions` row to catch it.
**Correction:** `D1…D112` in all four places. Consider adding `decisions<TAB>112<TAB>MasterSpec v4.0 Appendix A<TAB>spec`
to `COUNTS.tsv` (this changes `L0-05-02` criterion 1 from `26` to `27` and the SELF-VERIFY's `rows=`).

### H-06 · `L0-P0-020` `PROT-R2` · invariant 101 is misattributed

`PROT-R2` reads: *"Require approval of the most recent reviewable push… This is the enforcement behind the
no-self-approval invariant | 11.3, **invariant 101**"*, and the task's **Spec** row lists `invariant 101`.

Spec §101 #101 is: *"Under-utilisation is diagnosed, and is never presented as underperformance."*
The no-self-approval invariant is **#9**: *"No self-approval, enforced mechanically by requiring approval of the most
recent reviewable push."* (§11.3 L865 states the mechanism.)

`L0-05` §11 gets this right ("invariant 9"), so the two L0 files disagree.
**Correction:** `invariant 9` in `PROT-R2` and in `L0-P0-020`'s Spec row. This is F-18 territory —
*"Inventing … an invariant number"* — applied to a misattribution rather than an invention, and it reaches L5's
`access/**` implementation through a frozen contract.

### H-07 · `L0-01-phase-0-contracts.md`, nine tasks · *"Author X to the shape above"* with no authorable material

`L0-P0-006`, `-007`, `-008`, `-013`, `-014`, `-015`, `-016`, `-017`, `-020` replace the file body with a comment:

```bash
# Author contracts/registry/product.contract.v2.json to the shape above.
```

while their acceptance criteria assert precise internal structure of the file that comment stands in for. Worked
example, `L0-P0-006` (the contract all five lanes consume):

* The "shape" is one paragraph naming ~23 top-level blocks by name, with field lists for none of them.
* Criterion 6 requires `grep -o 'PROD-R[0-9]'` to return `PROD-R1 … PROD-R6` from the JSON — so the rule ids must be
  embedded as `description` strings. Nothing says so.
* The SELF-VERIFY reads `contracts/stubs/product.yaml` and dereferences `["assignments"]`,
  `["classification"]["reliability_criticality"]`, `["verification"]["performance"]`. That stub is listed under
  **Writes** and is authored by **no command and no content block**.
* `invalid-001..005` are described in five comment lines and written by nothing.

The same pattern applies to `stubs/verification-contract.yaml`, `stubs/service.yaml`, `stubs/topology.yaml`,
`stubs/platform.yaml`, `stubs/required-checks.yaml`, `stubs/secret-tiers.yaml`,
`stubs/evidence-chain-answers.yaml`, `stubs/comparison-set.yaml`, `stubs/permission-model.yaml`,
`stubs/branch-protection.yaml`, `stubs/layer-split.yaml` — every one dereferenced by a SELF-VERIFY, none authored.

`L0-P0-003`, `-004`, `-005`, `-018`, `-019`, `-021` show the standard the file sets for itself: complete, literal,
copy-pasteable content. Nine tasks fall short of it.

**Why this blocks in practice.** `L0-P0-023`'s SELF-VERIFY is the start signal for all five lanes, and it depends on
`verify_contracts.py` printing `CONTRACTS-VERIFY OK 23/23`, which depends on `H3` (every stub exists and is
non-empty) and `H6` (every stub validates). Neither can hold for eleven stubs nobody wrote.

**Correction.** For each of the nine, transcribe the field set literally from the cited spec section into the task
body (as `L0-P0-004` does for `C-REG-PEOPLE-1`), and author each named stub and each named invalid fixture with a
literal content block. At minimum, `L0-P0-006` must carry the §15.1 block list with field names, types and enums,
since five lanes block on it and its STOP rule calls it *"the most expensive block in the programme."*

---

## 3. MEDIUM

| # | File · task | Problem | Correction |
|---|---|---|---|
| M-01 | `L0-05-01` | `contracts/gate/ownership.tsv` is a **second copy** of the partition map, in a different glob dialect (`schemas/registry/**` vs `lane-paths.tsv`'s `schemas/registry/*`), with 22 rows against the manifest's 22 (different rows: it adds `CODEOWNERS`/`Makefile`, drops the `X` and catch-all). Nothing compares the two. `L0-P0-020`'s own STOP rule states the principle being broken: *"a check name written down twice is a check name that will differ once"* | Derive `ownership.tsv` from `lane-paths.tsv` in the task body, or add an `IG`-detail assertion that the two agree; state the glob-dialect mapping explicitly |
| M-02 | `L0-06` §3 | *"**Eight items**, transcribed from spec L8689–L8695"*. §95.3 lists **seven** bullets (L8689–L8695). `BIND-08` is imported from §26.4 L2533 and its spec-line cite `L8695` belongs to `BIND-07` | *"Seven items from §95.3, plus one carried from §26.4"*; change `BIND-08`'s spec-line cell to `§26.4 L2533` only |
| M-03 | four files | Line-number drift: `§54.2 (spec L4798)` → actual **L4797**; `§28.1 (spec L2588)` → actual **L2587**; `§98.2 Phase 1 (spec L9019)` for the machine-approval negative check → **L9024** (and §11.3 **L864**); `§11 (spec L810)` for hard-coded repository names → **L813** | Re-anchor. Line numbers are load-bearing here because `spec-transcription.sh` pins `SPEC.sha256`, so a spec edit already closes the gate — but a wrong line makes a citation unverifiable by hand |
| M-04 | `L0-04` §3 line 106 | *"asserted by `reg-lint.sh` (task `L0-04-05`)"*. `reg-lint.sh` is **`L0-04-03`**; `L0-04-05` is `reg-close.sh` | `L0-04-03` |
| M-05 | `L0-07` header | The `HUMAN STEP` convention is declared — *"Steps that must happen inside a product repository or on a live system are marked **HUMAN STEP**"* — and the marker appears **exactly once in 3,131 lines: in the declaration itself.** Zero steps carry it. The executor is an AI developer whose `OB-F5` forbids *"Performing, or asserting the result of, any step inside a product repository"*, with no mechanical way to tell which step that is | Mark every such step, or delete the convention and rely on `OB-F5` plus the `§12.1` consumed-surfaces table. Since `L0-07` is the one L0 file with an AI executor, this is the file where an unapplied marking convention costs most |
| M-06 | `L0-04-07` | The `promote-check` hook is prose only — *"Add one line to the existing `promote-check` recipe, at its top"* — with no command, while criterion 6 asserts `sed -n '/^promote-check:/,/^$/p' Makefile \| sed -n '2p'` contains `decisions-gate`. It also reads `contracts/gate/PHASE`, which does not exist until `L0-05-04` and mutates thereafter (**B-01**) | Give the literal edit (a `python`/`sed` in-place insertion, as `L0-03-01` does for the markers), and resolve the `PHASE` location with **B-01** |
| M-07 | `L0-P0-019` | Spec row cites `invariant 33`, which is *"The founder does not review routine code and does not dispatch incident responders."* The task is about the four scaffolding operations and their safe defaults; the applicable invariants are **79** (minimum privilege / draft state) and **80** (fail-closed classification), both already cited elsewhere in the file | `invariants 79, 80` |
| M-08 | `L0-05` §8.3, §11 | `make dod-integration` is invoked twice as part of the closure sequence and is created by no L0 task (it belongs to `protocol/11`). `L0-05` §3 correctly frames `DI-01`…`DI-10` as a different layer, but the quick-reference reads as if the target exists here | Name `protocol/11` as the owner at the point of invocation, or add the target with a fail-closed stub |

---

## 4. LOW

| # | Where | Problem |
|---|---|---|
| L-01 | all eight files | `§N.M` denotes both a MasterSpec section and the plan file's own section. Usually disambiguated by an adjacent filename, but not always (`L0-05` §3.2 mixes `protocol/08 §7` and bare `§53.1` in one paragraph). Suggest reserving `§` for the spec and `Sec.` or `this file §` for self-references |
| L-02 | `L0-04-08` | Criterion 4 uses `sed -n '2,3p'` and expects `REG-001 REG-002 `; the SELF-VERIFY uses `sed -n '2p'` and expects `head=REG-001`. Not contradictory, but the two disagree about what is being asserted |
| L-03 | `L0-03-01` | The appended `Makefile` adds a `promote-gate` target invoking `./train-promote-gate.sh`, which `L0-03-09` creates. `make promote-gate` between T01 and T09 fails with a missing-file error rather than a named verdict. Add the forward-reference note the file uses elsewhere (`L0-P0-021` handles the same situation explicitly and well) |
| L-04 | `L0-05-03` | `contracts/gate/SPEC_PATH` is written as `$HOME/src/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md`; the spec in this environment is at `C:/D_Drive/PS/MultiProduct/Research/`. Criterion 2's digest match depends on it. Make the path an explicit variable set in §1 alongside `$CP_ROOT` |
| L-05 | `L0-06-06` | Depends on `L1-108` (an L1 task) but the §7 dependency graph shows only L0 predecessors, so the cross-lane wait is invisible in the graph |

---

## 5. CHECKS THAT PASSED

Recorded because a review that reports only defects hides what is already sound.

**Controls — complete.** All **103** tasks across the eight files carry an **Acceptance criteria** table, a
**SELF-VERIFY** block with a stated expected output, and a **STOP rule**. No exceptions.

**Dependencies — no dangling ids.** 103 L0 task ids declared; every `L0-*` task id referenced anywhere in the eight
files resolves to a declared task. Every cross-lane id L0 depends on resolves in the owning lane's files:
`L1-001`, `L1-107`, `L1-108` → `L1-05-tasks.md`; `L2-T004`, `L2-T500`, `L2-T700` → L2 files;
`L5-01-03/T05/T07/T10/T13/T14` → `L5-01-org-and-access.md`.

**Register arithmetic — verified by re-computation from the source rows.**
60 rows · bands `P0=2 P1=12 P2=34 P3=12` · ids contiguous `REG-001`…`REG-060` · **188** source tokens, all unique ·
**9** colliding source ids (`D-L2-07`=3, `D-L2-08`=4, `D-L2-09`=3, `D-L4-01`=2, `D-L4-02`=2, `DECISION-REQUIRED-1`=3,
`-2`=3, `-3`=3, `-4`=2) · **16** `Ph0`-gated rows · **14** `P0`+`P1`. Every acceptance criterion in `L0-04-01`,
`T02`, `T04` and `T07` matches.

**Activation map arithmetic — verified.** `at-activation.tsv`: 37 rows, 37 distinct ATs, 33 twins, 4 twinless
(`AT-022`, `AT-028`, `AT-029`, `AT-101`), cumulative `1 2 11 12 15 19 22 32 36 37`. §7.4.1's `A`/`H/A`/`H` columns
sum to 23/10/4 = 37 and the four `H` rows are exactly the four twinless ATs.

**Citation integrity — sampled hard, and it holds.**

| Claim | Source | Verified |
|---|---|---|
| 110 acceptance tests | §100 preamble | ✓ |
| 111 invariants | §101 preamble; 111 numbered items counted | ✓ |
| 112 edge cases | §102 preamble; 112 `EC-` rows counted | ✓ |
| 18 subsystems A–R | §99.2 | ✓ |
| 46 signals | §52.2 | ✓ |
| **86 event types** (`D-L0-03`) | §97.3 taxonomy line split on `·` → **86** parts | ✓ |
| 27 capabilities (`L0-P0-003`) | §9 table, counting grouped cells: 4 + 19 + 4 | ✓ |
| 8 dangerous, explicit-grant-only | §8 / D106 — list matches **verbatim, in order** | ✓ |
| **17 rows in §53.1** (`L0-P0-017`) | the table renders 16 physical lines; line 20 carries **two** rows split by `\|\|` | ✓ — correctly counted |
| 27-row permission matrix | §90.2 | ✓ |
| **SA-001 spec anomaly is real** | §100 renders `rows=110 unique=110 cells=111`; the `AT-109` row carries a second `AT-110` id cell after `\|\|`, and `AT-110` repeats as its own row | ✓ exactly as `spec-anomalies.tsv` describes; `grep '^\| AT-109 \|.*\| AT-110 \|'` matches |
| D ids `D43 D44 D53 D69 D73 D75 D76 D77 D78 D79 D80 D87 D88 D89 D91 D93 D95 D99 D101 D102 D104 D106 D107 D109 D110` | Appendix A | all present, all semantically correct |
| AT ids `AT-001 002 017 031 033 034 039 045 047 050 071 074 089 090 095 097 098 102 103 105 106 110` | §100 | all present, all semantically correct |
| SIG ids `03 05 07 08 13 18 30 39 42 43` | §52.2 | all present, all semantically correct |
| Invariants `1 4 11 12 20 21 22 23 25 26 27 35 37 40 44 46 47 50 51 52 58 63 73 77 79 80 81 83 84 85 87 88 98 99 106 109 111` | §101 | all correct in context |
| Spec line anchors `L8642 L8678 L8687 L8689 L8695 L8703 L8708 L9017 L9018 L10125 L10182 L10194 L10205 L9554 L4568 L9361 L2533 L2497 L8652 L2571 L8680 L9010 L6009 L8586 L9508 L9514 L9515 L9489 L864 L865 L869 L870 L2866 L4697 L9012` | | all land on the quoted sentence |

Two invariant misattributions (**H-06**, **M-07**) and four line-anchor slips (**M-03**) are the only citation
defects in a sample of roughly 120 — a low rate for a document set this size, and no invented id was found.

**Judgment leakage — none found in the L0 body.** Seven of the eight files declare a human executor. `L0-07`, the
one file with an AI executor, carries an eight-row forbidden-actions table (`OB-F1`…`OB-F8`), seven
`DECISION REQUIRED` blocks each with fail-closed interim behaviour, and an `UNSET`-everywhere discipline that makes
"not yet answered" mechanically distinct from "empty". Its only gap is the unapplied `HUMAN STEP` marker
(**M-05**). The `L5`-specific `ASSISTED` requirement in the review brief does not apply to this lane; the
equivalent obligation here — routing credential and console work to a named human — is met in `L0-01`, `L0-02-08`,
`L0-03-09`, `L0-05-12` and `L0-07` §0.5.

---

## 6. WHAT MUST HAPPEN BEFORE DISPATCH

Ordered. Items 1–3 are ordering and decision problems; 4–7 are one-line arithmetic fixes.

1. **Resolve where `contracts/gate/**` lives and how it is frozen (B-01).** Nothing in `L0-02`, `L0-03` or `L0-05`
   can be run green until `make promote-check` can pass. Decide it, record it, and correct `L0-00-04`,
   `L0-05-01` and `L0-05-04` together.
2. **Close `REG-001` and `REG-002` (B-03), or gate `L0-02-05/T06/T07` on them.** `make decisions-gate PHASE=Ph0`
   is designed to fail while they are open, and `promote-check` now calls it first. `L0-02` must stop presenting
   `L0D-LG-1..3` as settled while `L0-04` records it as `P0 open` with three rival claims.
3. **Give `e2e/**` and `contracts/harness/**` an owner and an author (B-04), and delete the false ownership
   sentence at `L0-05` line 1790.** Then rewrite `rehearse.sh`'s pass condition against a baseline `first_failure`
   (B-02), or gate `L0-05-14` on `L0-IG-D1/-D2/-D3`.
4. **`lane-paths.tsv` is 22 rules, not 21** — `L0-00-03` ×2, `L0-02` §5 ×2, `L0-02` §8 (B-06).
5. **`L0-P0-008` register total is 8**, and §7.2's column is wrong for tasks 008–017 (B-07).
6. **Four command/expectation mismatches:** `L0-02-02` crit 3 and crit 7, `L0-02-05` crit 1, `L0-03-01` crit 9
   (H-01 … H-04).
7. **`D1…D112`, not `D1…D109`** in four files; **invariant 9, not 101** in `L0-P0-020` (H-05, H-06).

**Then** `L0-P0-006`, `-007`, `-008`, `-013`, `-014`, `-015`, `-016`, `-017` and `-020` need their file bodies and
their eleven missing stubs written out literally (H-07), because `L0-P0-023` — the signal that starts all five
lanes — cannot print `PHASE-0-COMPLETE` without them.

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

### Changes landed in Session 12

- **L0-P0-025 complete** — 86 `event_type` entries verified and present.
- **L0-P0-026 added** — e2e/harness task bodies authored and committed.
- **REG-001 closed** — open decision resolved; `L0-04` and `L0-02` now consistent.
- **REG-002 closed** — rival claims reconciled; `L0D-LG-1..3` no longer marked `P0 open`.
- **Phase 0 `# Author` comments** — all converted to heredocs across every Phase 0 task.
- **Phase 0 task count: 26** (was 24 before Session 12; two net-new tasks: L0-P0-025 and L0-P0-026).

### Effect on BLOCKED verdict

B-03 (REG-001/REG-002) is now **closed**. B-02, B-04, B-06, B-07 and H-01..H-07 status unchanged from the original review — those require separate L0 decisions and are tracked in the structural-blockers memory entry.
