# L3-99 — COHERENCE REVIEW: Lane 3 (Reconciler & Provisioning)

**Reviewer:** L3 coherence reviewer
**Date:** 2026-08-27
**Scope reviewed, in full:**

| File | Lines | Tasks declared |
| --- | --- | --- |
| `L3-00-charter.md` | 1,103 | `L3-00-01` … `L3-00-06` (6) |
| `L3-01-diff-engine.md` | 7,574 | `L3-01-01` … `L3-01-22` (22) |
| `L3-02-levels-and-repair.md` | 3,557 | `L3-02-01` … `L3-02-14` (14) |
| `L3-03-canary-and-integrity.md` | 6,023 | `L3-P3-T00` … `L3-P3-T14` (15) |
| `L3-04-provisioning.md` | 1,938 | `L3-04-01` … `L3-04-18` (18) |
| `L3-05-orphans.md` | 2,034 | `L3-05-01` … `L3-05-30` (30) |
| `L3-06-tasks.md` | 3,285 | `L3-P0-01` … `L3-P8-06` (78) |
| `L3-07-tests-and-runbook.md` | 1,361 | `T01` … `T11` (11) |

Plus `Code/implementation/PARTITION.md` (47 lines, FROZEN) and citation sampling against
`Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## VERDICT

> ## **BLOCKED — do not dispatch.**
>
> The lane contains **two complete, mutually exclusive implementation plans for the same
> subsystems**, in two id schemes, on two phase numberings, against two runtimes, in two package
> layouts. 194 task definitions exist for a body of work that should have roughly 78–116. An
> executor handed this lane cannot determine which file is authoritative, and executing both
> builds subsystems C and D twice into colliding paths.
>
> Defects **B1 – B10** below are dispatch-blocking. **H11 – H17** must be resolved before the
> affected tasks run. **M18 – M25** and **L26 – L29** are correctable in place.
>
> What is *good* here should be said plainly, because it is unusual: **every one of the 194 tasks
> in all eight files carries both a SELF-VERIFY block and a STOP rule** (defect class 3: clean).
> **No task references a task id that does not exist** (defect class 2: clean). **No task writes a
> path outside `reconciler/**`, `tools/provision/**`, `validators/drift/**`** (defect class 1:
> clean). **Citation integrity is high** — every sampled AT id, invariant number, SIG id, D id,
> section header and line anchor resolves exactly, including the charter's line-level anchors
> (invariant 81 → 9558, AT-102 → 9351, AT-110 → 9439, SIG-13 → 4542, §52.6 → 29 entries). The four
> citation defects found (B10, H11, H12, M22, M23) are misreadings, not inventions.
>
> The lane is not broken because it is careless. It is blocked because it was written twice.

---

## BLOCKING DEFECTS

### B1 — Two complete, competing task plans for the same lane

| | |
| --- | --- |
| **Files** | `L3-06-tasks.md` §2 vs `L3-00`, `L3-01`, `L3-02`, `L3-03`, `L3-04`, `L3-05`, `L3-07` |
| **Task ids** | all 78 of `L3-P0-01`…`L3-P8-06` vs all 116 of `L3-00-01`…, `L3-01-01`…, `L3-02-01`…, `L3-P3-T00`…, `L3-04-01`…, `L3-05-01`…, `T01`… |

**Problem.** `L3-06-tasks.md` opens: *"This file is the complete, ordered work list for Lane 3.
Work it top to bottom. Every task below is executable without opening another document."* Its
master table is 78 tasks in the `L3-P<phase>-<nn>` scheme. The six phase files declare a separate,
equally complete 116-task plan in five *other* schemes. **Not one id from any phase file appears in
`L3-06`, and not one `L3-P*` id appears in any phase file.** Both plans build the same artifacts:
two comparator registries, two canary implementations, two stricter-only predicates, two AT-110
probes, two CODEOWNERS generators, two orphan detector sets, two `create-product` orchestrators.

**Correction.** L0 must designate exactly one plan as authoritative and delete or demote the other
to a non-executable design note with its task ids stripped. If `L3-06` is chosen, the phase files
lose their task bodies and keep only their spec-transcription and DECISION REQUIRED sections. If
the phase files are chosen, `L3-06` must be reissued as an index over their ids. Do not attempt to
merge them — B3 and B5 make merger impossible without re-deciding the runtime and the layout.

---

### B2 — "Phase N" denotes a different body of work in each file

| | |
| --- | --- |
| **Files** | all seven plan files |
| **Task ids** | every task, via its `Phase` field |

**Problem.**

| Phase | `L3-06` says | The phase file says |
| --- | --- | --- |
| 1 | comparators only (`L3-P1-01`…`20`) | the whole diff engine incl. run record and schemas (`L3-01`) |
| 2 | orphan detection (`L3-P2-01`…`06`) | the five response levels and auto-repair (`L3-02`) |
| 3 | the Level-4 block surface (`L3-P3-01`…`06`) | instrument integrity: canary, D93, gap procedure, D107, D96 (`L3-03`) |
| 5 | independent verifier + credential bound (`L3-P5-01`…`08`) | orphan and expiry detection (`L3-05`) |
| 6 | auto-repair (`L3-P6-01`…`10`) | — (`L3-06` only) |

`L3-06` §12.1 states *"Order is not advisory. Phase 6 exists after Phase 5 because §99.6 risk 6
requires detect-only first."* Under the phase files, "Phase 5" is orphan detection and auto-repair
is "Phase 2" — the opposite ordering, and the one §99.6 risk 6 forbids. The branch names collide
too: `lane/3/p3-t01` (L3-03) vs `lane/3/p3-01-*` (L3-06).

**Correction.** Once B1 is settled, renumber the surviving plan so that phase number → deliverable
is one-to-one lane-wide, and restate the detect → block → repair ordering rule against the
surviving numbers.

---

### B3 — Three binding, contradictory runtime decisions; two tasks write the same file

| | |
| --- | --- |
| **Files** | `L3-01-diff-engine.md` §1 D-L3-01 + `L3-01-01`; `L3-06-tasks.md` §1 L3-D1 + `L3-P0-02`; `L3-04-provisioning.md` §0.3 + §1 D-L3-04-01; `L3-03-canary-and-integrity.md` §3 |
| **Task ids** | `L3-01-01`, `L3-P0-02`, `L3-04-01` |

**Problem.**

| Source | Runtime | `reconciler/requirements.txt` |
| --- | --- | --- |
| `L3-01` D-L3-01 | `python-3.11` exactly; `L3-01-01` A4 asserts `requires-python = "==3.11` in `reconciler/pyproject.toml` | hash-pinned via `pip-compile --generate-hashes`; A3 asserts ≥3 `hash=sha256:` lines |
| `L3-06` L3-D1 | Python 3.12; STOP: *"If L0 ratified any runtime other than Python 3.12, STOP: every command in this file assumes Python 3.12"* | *exactly two* `==`-pinned lines, *"no lockfile generator"*; SELF-VERIFY runs `! grep -Eq '(>=|~=|\*)'` |
| `L3-04` D-L3-04-01 | Python 3.12; §0.3 gate `sys.version_info[:2]>=(3,12)` else MISSING | `tools/provision/requirements.txt`, PyYAML pinned by hash |
| `L3-03` §3 | "Python 3.11 or newer" | — |

`L3-01-01` and `L3-P0-02` both create `reconciler/requirements.txt`, with incompatible content
rules: a `pip-compile --generate-hashes` file is dozens of lines with `--hash=sha256:` continuations
and environment markers containing `>=`, so it fails `L3-P0-02`'s SELF-VERIFY by construction; a
two-line `==` file fails `L3-01-01`'s A3 by construction. Each task's STOP rule fires on the
other's answer.

**Correction.** L0 records one runtime and one pinning mechanism in `docs/decisions/`. The losing
file is reissued in full — both files say so themselves, and both are right.

---

### B4 — `L3-06` forbids the live-organisation dependency that `L3-04` requires, and `L3-04` is not gated

| | |
| --- | --- |
| **Files** | `L3-06-tasks.md` §0.4; `L3-04-provisioning.md` §0.3, §0.7, `L3-04-02` … `L3-04-18` |
| **Task ids** | all of `L3-04-02`…`T18`; contrast `L3-07` `T10` |

**Problem.** `L3-06` §0.4 is binding on the lane: *"every acceptance command and every SELF-VERIFY
command must run locally, offline, against a fixture. No task's acceptance may depend on a live
GitHub organisation, a running CI job, or another lane's merged branch."* `L3-04` §0.3 gates the
entire phase on `PROVISION_SANDBOX_ORG`, `gh auth status = OK`, and a real sandbox GitHub
organisation, and every create-product/add-person task executes `gh` subprocess calls against it.

The asymmetry matters for dispatch safety: `L3-07` `T10` (the AT-110 six-attempt run against the
fifth-tier reconciler credential) **is** correctly gated — SR-3, `DR-L3-07-B`, a published
`contracts/l3-live-org-gate.md`, a named human supervisor, and *"never run by a schedule"*.
`L3-04` needs comparable credential and console access for eighteen tasks and carries no such
marking, no supervisor requirement, and no ASSISTED flag.

**Correction.** Either (a) rewrite `L3-04` fixture-backed with a `--live` flag never exercised in
acceptance, matching `L3-06` §0.4 and §0.5's own posture; or (b) mark every `L3-04` task **ASSISTED**
and gate the phase behind the same published live-org gate `L3-07` `T10` uses. Do not dispatch
`L3-04` to an unsupervised low-cost agent as written.

---

### B5 — Mutually exclusive package layouts for the same artifacts

| | |
| --- | --- |
| **Files** | `L3-06-tasks.md` §0.1, `L3-P4-02`, `L3-P6-01`, `L3-P3-03`, `L3-P5-06`; `L3-04-provisioning.md` §0.6, `L3-04-07`; `L3-02-levels-and-repair.md` `T05`, `T10`, `T12`; `L3-00-charter.md` §2.1 |

**Problem.** The same artifact is assigned to different files, packages and import paths:

| Artifact | `L3-06` | Phase file |
| --- | --- | --- |
| CODEOWNERS generator | `tools/provision/codeowners.py`, imported `from tools.provision.codeowners import generate` from repo root | `L3-04-07`: `tools/provision/provision/codeowners/render.py`, run as `python -m provision` from `$CP/tools/provision` |
| Stricter-only predicate | `L3-P6-01`: `reconciler/repair/stricter.py` | `L3-02-05`: `validators/drift/stricter_only.py` |
| Check-run identity check | `L3-P3-03`: `reconciler/comparators/checkrun_identity.py` | `L3-02-12`: `validators/drift/checkrun_identity_guard.py` |
| AT-110 probe | `L3-P5-06`: `validators/drift/credential_bounds.py` | `L3-02-10`: `reconciler/credential/bound_check.py` |
| Response levels 1–5 | *no `reconciler/levels/` created by any task* | `L3-02-03/04/08/11/13`: `reconciler/levels/level1..5_*.py` |
| Test directory | `reconciler/tests/`, `tools/provision/tests/` | `reconciler/comparators/tests/` + `reconciler/api/tests/` (L3-01); `reconciler/test/` (L3-07) |

`L3-06` §0.1's namespace rule (*"Do not create `tools/__init__.py`… `tools.provision` imports as a
PEP 420 implicit namespace package"*) requires the repo root on `sys.path`. `L3-04` requires a
nested `tools/provision/provision/` package, a `.venv` inside `tools/provision`, and `cd
"$CP/tools/provision"` before every command. Both cannot be true of one repository.

**Correction.** Publish one internal layout table for the lane — the charter §2.1 table is the
natural home — and make every task's file paths conform to it. Note that charter §2.1 currently
matches *neither* plan (see B7).

---

### B6 — The comparison set has three incompatible cardinalities

| | |
| --- | --- |
| **Files** | `L3-00-charter.md` §1.1, §7.1, §8 D1, `L3-00-05`; `L3-01-diff-engine.md` §4, exit E3; `L3-06-tasks.md` `L3-P1-02`…`P1-16` |

**Problem.**

| Source | Count | Ids | Location |
| --- | --- | --- | --- |
| Charter | ~~**23**~~ → **19** per FD-061 | `C01`–`C19` <!-- was C01–C23; 4 §40.1/D107 rows removed per FD-061 --> | one file per entry under `reconciler/comparators/cmp_*.py` |
| `L3-01` | **19** | `CMP-01`–`CMP-19` | `reconciler/comparators/cmp_*.py` |
| `L3-06` | ~~**16**~~ → **19** per FD-061 (14 + `display_name` + `checkrun_identity` + 3 TBD from L3-01 reconciliation) | comparator string ids | `reconciler/comparators/*.py` |

<!-- FD-061 (2026-09-06): L3-01 is authoritative at 19. Charter updated from 23 to 19 (§40.1/D107 rows excluded). L3-06 updated from 16 to 19 (3 additional comparators needed per L3-01 reconciliation). -->

All three were defensible decompositions of §53.1 — the spec's table has 17 logical rows (verified:
lines 4655–4671, with rows 16 and 17 sharing one physical line) plus 2 prose Blocking paragraphs.
The charter folded four §40.1/D107 conditions into the same set; `L3-06` merges the two authorship
paragraphs into one comparator and hard-coded `EXPECTED_MINIMUM_COUNTS` with exactly fourteen keys
(`L3-P1-16` SELF-VERIFY expected `counts 14`; updated to 19 per FD-061). **No task in any file creates `reconciler/checks/`.**

**Correction.** Fix the decomposition once, in the charter, with each entry's spec anchor; derive
`L3-01`'s manifest and `L3-06`'s count table from it. The charter's `ls reconciler/checks | wc -l`
proof must then name the directory that is actually built. <!-- Partially addressed by FD-061: count corrected to 19; directory path still needs reconciliation with L3-01's `reconciler/comparators/` path. -->

---

### B7 — The charter's Definition of Done cannot be satisfied by any task in the lane

| | |
| --- | --- |
| **File** | `L3-00-charter.md` §8, rows D1, D2, D3, D5, D7, D9, D10, D11 |
| **Task ids** | none — that is the defect |

**Problem.** Eight of fourteen DoD rows assert against artifacts or literal strings no task produces:

| Row | Proof command | Why it fails |
| --- | --- | --- |
| D1 | `ls reconciler/checks \| wc -l` → ~~`23`~~ `19` per FD-061 | `reconciler/checks/` is created by no task (B6); count updated from 23 to 19 per FD-061 <!-- 19 per FD-061 --> |
| D2 | `ls reconciler/levels \| wc -l` → `5` | created only by `L3-02`, absent from `L3-06` (B5) |
| D3 | output contains `LOOSENING-REPAIR-REFUSED` | no task emits this literal |
| D5 | output contains `ZERO-FINDINGS-RUN-FAILED` | no task emits this literal |
| D7 | output contains `ORPHAN-TYPES=16` | `L3-P2-01` prints `types 16 blocking 7`; `L3-05-21` prints neither |
| D9 | output contains `MACHINE-IDENTITY-REJECTED` | no task emits this literal |
| D10 | `ls validators/drift/verifier \| wc -l` ≥ 1 | `L3-P5-01` makes `verifier.py` a **module**; `ls` on it returns the file, not a directory listing, and the `-d` semantics differ |
| D11 | `grep -c '^- \[ \] attempt' reconciler/CREDENTIAL-ENVELOPE.md` → `6` | **self-contradiction**: `L3-00-06`, which writes that file, asserts `ATTEMPTS=7` (six MUST FAIL + one MUST SUCCEED). D11 prints `7`. |

D11 is the sharpest: the charter's own task guarantees the charter's own DoD row fails.

**Correction.** Rewrite §8 so each row's proof command names an artifact a named task creates and a
literal a named task emits. Cite the task id in a new column. Fix D11 to `7`, or change its grep to
`'MUST FAIL'`.

---

### B8 — `L3-06`'s fixture silently pre-resolves five L0 decisions by inventing registry schema

| | |
| --- | --- |
| **Files** | `L3-06-tasks.md` `L3-P0-04` (files 6, 7, 8, 9, 10; file 2 `commitments`) driving `L3-P2-01`…`P2-05`; vs `L3-05-orphans.md` §5 `DR-L3-05-A` … `DR-L3-05-E` |
| **Task ids** | `L3-P0-04`, `L3-P2-01`, `L3-P2-02`, `L3-P2-03`, `L3-P2-04`, `L3-P2-05` |

**Problem.** `L3-05` §5 establishes, with spec citations, that five inputs the orphan detectors need
**do not exist in the spec** and are L0's to settle:

* `DR-L3-05-A` — the operational asset inventory has no spec-given filename, schema or type
  vocabulary (§49.1, §52.6 name the artifact only). Blocks orphan types 6, 7, 8, 9.
* `DR-L3-05-B` — §10.1 line 787 requires a 14-day warning for *"delegation-type"* assignments but
  no row in its table is labelled delegation-type.
* `DR-L3-05-C` — §12.2's Detection column for orphan type 13 is *"Board"*; boards live outside the
  control plane and no snapshot file is named.
* `DR-L3-05-D` — *"open gate-relevant work"* has no declared input surface.
* `DR-L3-05-E` — the commitments schema (§21.1, §15.1) **contains no `owner:` field**.

`L3-P0-04` invents all five: `assets.yaml` with `kind: certificate|domain|vendor|operational`,
`board.yaml` with `items[].horizon`, `open_gate_items[].kind`, `migrations[]`, and — directly
contradicting `DR-L3-05-E` — `commitments: [{id: COM-alpha-001, owner: ""}]`. `L3-P2-02`…`P2-04`
then assert exact finding counts against the invention, and `L3-05` §5 notes the asset inventory is
**L5-owned data** (`assets/**`, PARTITION.md line 21).

This is the judgment leakage PARTITION.md line 47 reserves for L0 — *"No task may require designing,
choosing, or interpreting"* — laundered through a fixture so it reads as fact.

**Correction.** Strip the invented keys from `fixture-a`, mark `L3-P2-01`…`P2-05` blocked on
`DR-L3-05-A`…`E`, and adopt `L3-05`'s `input_unavailable` posture: a detector whose declared input
is absent returns `input_unavailable` with a non-empty `missing_inputs`, never an empty clean result.

---

### B9 — Twenty-eight decision items in eight numbering schemes, several restating the same question

| | |
| --- | --- |
| **Files** | `L3-00` §10 (`DR-L3-01`…`05`); `L3-01` §1 (`D-L3-01`…`04`, `CCR-L3-01`); `L3-02` §2 (`DEC-L3-02-01`…`04`); `L3-03` §2 (`DR-3.1`, `DR-3.2`); `L3-04` §1 (`D-L3-04-01`…`03`); `L3-05` §5 (`DR-L3-05-A`…`E`); `L3-06` §1 (`L3-D1`…`D4`); `L3-07` §2 (`DR-L3-07-A`, `B`) |

**Problem.** The same question is asked under different ids, with different scope and different
interim defaults:

| Question | Asked as |
| --- | --- |
| Implementation runtime | `D-L3-01` (3.11), `L3-D1` (3.12), `D-L3-04-01` (3.12) |
| Seeded-canary placement and class | `DR-L3-03`, `D-L3-04(a)`, `DR-3.2` |
| Record-store paths for run/repair records | `DR-L3-04`, `L3-D2`, `DEC-L3-02-03`, `D-L3-02`, `D-L3-03` |
| Repair-class enabling order | `DR-L3-02` (six classes), `DEC-L3-02-04` (is there a sixth?) |
| Blocking check-run name | `DR-L3-01`, `DEC-L3-02-02` — **and the spec already answers it** (see B10) |

`L3-06` compounds it: §1 says *"the four decisions L0 owns"*; §12.3 says *"Five decisions belong to
L0"*.

**Correction.** One decision register for the lane, one id scheme, one row per distinct question,
each naming every task it blocks across every file. Reconcile the interim defaults — three files
currently proceed against three different provisional runtimes.

---

### B10 — `DEC-L3-02-02` blocks three tasks on a question the spec answers

| | |
| --- | --- |
| **File** | `L3-02-levels-and-repair.md` §2, `DEC-L3-02-02` |
| **Task ids blocked** | `L3-02-11`, `L3-02-12`, `L3-02-14` |

**Problem.** `DEC-L3-02-02` asserts: *"D92 says 'posts a named required check on every affected
repository' … The spec never writes the name string."*

**It does.** MasterSpec §11.3, **line 867**:

> *"Require status checks to pass: tests, build, security scan, contract validation, reviewer matrix
> validation, parity check, verification contract, and `control-plane/blocking-drift` — the check the
> reconciler holds at failure while Blocking-class drift is open against the product (Section 53.2)."*

`L3-01-08`'s STOP rule and `L3-06` `L3-P3-02` both use the spec-given literal correctly.
`DEC-L3-02-02` blocks `L3-02-11`, `T12` and `T14` on an L0 answer already in the spec of record,
and its own exit criterion E1 (14 merged `L3-02-T` branches) cannot be met while it stands.

**Correction.** Retire `DEC-L3-02-02`. Replace it with a note that the string is `control-plane/
blocking-drift` per §11.3 line 867, and narrow the residual question to *when* the context is added
to each repository's required-check list (§98.2 Phase 1: *"a required check no workflow emits blocks
every pull request indefinitely"*) — which genuinely is L5's and L2's. Apply the same narrowing to
charter `DR-L3-01`.

---

## HIGH DEFECTS

### H11 — The charter misstates §53.2 and would authorise a repair class the spec does not

| | |
| --- | --- |
| **File** | `L3-00-charter.md` §10, `DR-L3-02` |

**Problem.** `DR-L3-02` states: *"Section 53.2 Level 3 lists six candidate repair classes (Team
membership sync, CODEOWNERS regeneration, label and board field sync, re-applying declared branch
protection, removing expired assignments, removing expired access)"*, and asks L0 for *"An ordered
list of the six classes."*

§53.2's Level 3 "Applies to" cell (line 4696) reads: *"Safe, idempotent, reversible repairs only:
Team membership sync from registries, CODEOWNERS regeneration, label and board field sync,
re-applying declared branch protection, removing expired assignments and expired access."* That is
**five** classes; the charter splits the last phrase into two. `L3-02-06` (*"closed list of five"*,
*"THE LIST IS CLOSED. Adding a class is a governance act"*) and `L3-06` `L3-P6-02`
(`REPAIR_CLASSES total=5`, `L3-P6-09` asserts `modules 5`) both transcribe five correctly.

Under §99.6 risk 6 an extra repair class is an extra org-admin write path. Asking L0 to order six
invites one into existence by clerical error.

**Correction.** `DR-L3-02` → five classes, quoting the §53.2 cell verbatim. Cross-reference
`DEC-L3-02-04`, which asks the *right* version of the sixth-class question (does §53.1's
*"Auto-repair where safe"* lifecycle row create one?).

---

### H12 — The charter attributes four §40.1 conditions to §53.1

| | |
| --- | --- |
| **File** | `L3-00-charter.md` §1.1 item 1, §7.1 row "53.1" |
| **Task id** | `L3-00-05` |

**Problem.** §1.1 and §7.1 both read *"53.1 Declared versus actual | 4653–4689 | 17 table rows + 6
prose Blocking rows = 23 comparison entries."* §53.1 declares exactly **two** prose Blocking
paragraphs (machine-identity workflow-file push; non-bypass-actor authorship on a bypass branch).
Entries `C20`–`C23` — unsigned records-repo commit, non-descendant head, foreign check-run publisher,
out-of-envelope credential run — come from **§40.1 / D107**, as `L3-00-05`'s own generated
`COMPARISON-SET.md` body correctly says (*"plus the Blocking rows declared in prose in Sections 53.1
and 40.1"*).

**Correction.** Split the §7.1 row: `53.1 → 17 table rows + 2 prose rows`; add a `40.1 / D107 → 4
prose rows` row. The task body is already right; only the charter's summary tables are wrong.

> **RESOLVED by FD-061 (2026-09-06).** Comparison-set cardinality updated to 19 per FD-061 (L3-01 authoritative). The charter's §1.1 item 1, §7.1, and L3-00-05 have been updated; the §40.1/D107 rows (C20–C23) are no longer counted in the 19-entry comparison set. <!-- 19 per FD-061 -->

---

### H13 — `L3-06` §0.5's exit-code contract contradicts sixteen task expectations

| | |
| --- | --- |
| **File** | `L3-06-tasks.md` §0.5 vs `L3-P1-02`…`P1-15`, `L3-P3-03` |

**Problem.** §0.5 fixes: *"`3` = run FAILED (instrument failure, canary missing)."* `L3-P1-17`
implements it: *"a run whose findings list is empty, **or which does not contain the canary**, sets
`status="FAILED"` and exits `3`."*

Every Phase-1 comparator SELF-VERIFY prints `CANARY missing` and expects exit `0` or `2`:

```
OK org_membership findings=1 compared=5
CANARY missing
exit=2
```

Sequentially this holds only while `L3-P1-17` is unmerged. The moment it merges, all sixteen of
those acceptance commands return `3`, and each task's STOP rule (*"if `exit` is `0`, the Blocking
class is not reaching the exit code"*) fires on correct code. `L3-P8-05`'s regression matrix and any
re-run of a Phase-1 task hit this immediately.

**Correction.** State in §0.5 that `--only` suppresses the canary rule and prints `CANARY n/a`, or
require every `--only` invocation to include the canary comparator once `L3-P1-17` exists, and
update the sixteen expected-output blocks accordingly.

---

### H14 — `L3-01`'s universal lane-guard omits an owned root and fails two of its own tasks

| | |
| --- | --- |
| **File** | `L3-01-diff-engine.md` §2, line 98 |
| **Task ids** | `L3-01-08`, `L3-01-10` |

**Problem.** §2's *"Universal path rule … run before every commit"*:

**Commands**

```bash
set -euo pipefail
git diff --cached --name-only | grep -vE '^(reconciler/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
```

`tools/provision/` is missing. `L3-01-08` creates `tools/provision/templates/branch-protection.yaml`
and `L3-01-10` creates `tools/provision/templates/environment.yaml` — both legitimately owned, both
flagged by §3 of the same file as *"created by this phase … PARTITION.md line 19 gives
`tools/provision/**` to this lane."* An executor obeying §2 gets `LANE-GUARD FAIL` on a correct
commit and, per §2, *"Unstage it. Do not push."* Every per-task SELF-VERIFY (lines 643, 1098, 1655,
2001, 2381, 2634, 2864, 3202…) uses the correct three-root regex, so §2 is a stale duplicate.

**Correction.** `grep -vE '^(reconciler/|tools/provision/|validators/drift/)'` in §2, matching the
task bodies and charter §11.

---

### H15 — Three conflicting declared branch-protection templates; eight required checks never compared

| | |
| --- | --- |
| **Files** | `L3-01-diff-engine.md` `L3-01-08`; `L3-06-tasks.md` `L3-P0-04` file 11, `L3-P1-06`, `L3-P4-03` |

**Problem.**

| Artifact | `required_status_checks.contexts` |
| --- | --- |
| `L3-01-08` → `tools/provision/templates/branch-protection.yaml` | **8 entries** — SELF-VERIFY asserts `8`, transcribing §11.3 line 867's eight named checks |
| `L3-P0-04` file 11 → `.../fixture-a/declared/templates/branch-protection.json` | **1 entry** — `["control-plane/blocking-drift"]` |
| `L3-P4-03` (applied at creation) | **0 entries** — *"applied empty at creation"*, citing §98.2 Phase 1 |

The declared/applied split in `L3-P4-03` is a legitimate reading of §98.2. The **declared template**
disagreeing with itself is not: `L3-P1-06` deep-compares actual protection against the one-context
JSON, so seven of §11.3's eight required checks are outside the comparison set entirely, and a
repository that dropped `contract validation` or `parity check` produces no finding.

**Correction.** One declared template file for the lane, carrying all eight §11.3 contexts. Model
the creation-time empty list as a documented *applied* deviation with the manual step `L3-P4-03`
already emits, not as a second template.

---

### H16 — Three acceptance tests the charter obligates the lane to pass have no implementing task

| | |
| --- | --- |
| **Files** | `L3-00-charter.md` §7.3 (14 ATs) vs `L3-06-tasks.md` `L3-P8-05` (11 ATs) |
| **Task ids** | AT-021, AT-034, AT-051 — unassigned in all eight files |

**Problem.** Charter §7.3 lists fourteen ATs as *"this lane's obligation"*. `L3-P8-05`'s traceability
matrix runs eleven and asserts `MATRIX passed=11 total=11`. Missing, and absent from every task in
every L3 file:

* **AT-021** (line 9330) — permanent ownership change recorded as a decision, Founder-view
  notification generated automatically. Charter maps it to L3; nothing implements it.
* **AT-034** (line 9348) — *"The reconciliation engine and the exception registry are core-resident
  machinery and are never removed."* Charter maps it to L3; no task asserts core-residency.
* **AT-051** (line 9373) — a breached pre-onboarding deadline surfaces as drift. Charter §7.2 cites
  §96.2 (*"a stub `product.yaml` is a legitimate declared state"*); no comparator handles the
  pre-onboarding state, and `L3-P0-04`'s fixture has no pre-onboarding product.

**Correction.** Either add tasks for the three, or move them out of charter §7.3 with the owning
lane named. Silence is the one option §101 invariant 44 does not allow.

---

### H17 — `L3-P8-05` and `L3-P8-06` are transitively blocked by `L3-D3`, unmarked

| | |
| --- | --- |
| **File** | `L3-06-tasks.md` §1 (L3-D3 Blocks column), `L3-P8-05`, `L3-P8-06` |

**Problem.** §1: *"**L3-D3** … **Blocks:** L3-P5-06 (AT-110 probe) and L3-P5-07 (behavioural
envelope). Everything else in this file is fixture-backed and proceeds without it."* But `L3-P8-05`
requires `MATRIX passed=11 total=11`, and its own table maps **AT-110 → L3-P5-06**. `L3-P8-06`
depends on `L3-P8-05` and its STOP rule is *"if any consumer's entry point does not yet exist, stop
… Do not write a placeholder."* Both are unreachable until L3-D3 is answered, and the lane's final
two tasks are therefore blocked by a decision the table says blocks only two Phase-5 tasks.

**Correction.** Add `L3-P8-05`, `L3-P8-06` to L3-D3's Blocks column, and delete the *"Everything
else … proceeds without it"* clause.

---

## MEDIUM DEFECTS

### M18 — `L3-P5-01`'s SELF-VERIFY expects a value the command cannot return

**File** `L3-06-tasks.md` · **Task** `L3-P5-01`

**Commands**

```bash
set -euo pipefail
grep -rc "import reconciler" validators/drift/ | grep -c ":0"
```
Expected: `3`. At `L3-P5-01`, `validators/drift/` contains **five** files: `README.md` (`L3-P0-01`),
`tests/__init__.py` (`L3-P0-02`), `__init__.py`, `verifier.py`, `tests/test_verifier.py`. The command
returns `5` — or `4`, because `test_verifier.py` must plausibly contain the literal string
`import reconciler` in order to assert its absence. Expected `3` is unreachable, and the STOP rule
fires on a correct implementation.
**Correction.** `grep -rL "import reconciler" validators/drift/ --include='*.py' | wc -l` against a
count the task states, or assert the negative directly: `! grep -rq "^\(from\|import\) reconciler"
validators/drift/ && echo NO-RECONCILER-IMPORT`.

---

### M19 — Three Phase-4 SELF-VERIFYs call undeclared signatures and an undefined attribute

**File** `L3-06-tasks.md` · **Tasks** `L3-P4-02`, `L3-P4-03`, `L3-P4-05`

| Task | Declared signature | SELF-VERIFY call |
| --- | --- | --- |
| `L3-P4-02` | `generate(product, registries) -> str` | `generate('alpha', 'fixture-a')` |
| `L3-P4-03` | `plan_protection(repo, template)` | `plan_protection('gamma','fixture-a')`, then prints `p.contexts` |
| `L3-P4-05` | `plan_teams(registries)` | `plan_teams('fixture-a')` |

A fixture *name* is passed where a registries object or a template belongs. Worse, `L3-P4-03` prints
`p.contexts` — `Plan` is defined in `L3-P4-01` as *"an ordered list of steps with
`summary_line(operation)`"*; no `contexts` attribute is specified in any task. An executor must
invent the object model to make its own SELF-VERIFY run.
**Correction.** State one signature per function and use it identically in the body, acceptance table
and SELF-VERIFY. Add `contexts` to `Plan` in `L3-P4-01` or read it off the protection step.

---

### M20 — `L3-P4-07` plans a product that does not exist in the fixture

**File** `L3-06-tasks.md` · **Task** `L3-P4-07`

```
python -m tools.provision.cli create-product --fixture fixture-a --product gamma --dry-run --summary
→ PLAN create-product steps=13 writes=0 manual=2
```
`fixture-a` declares only `alpha` and `beta`. Steps 3–5 (`team`, `codeowners`, `branch_protection`)
consume assignments; `gamma` has none, and `L3-P4-05` makes membership *derived* — *"a
caller-supplied member list raises."* The task never says whether to add `gamma` to the fixture, and
doing so breaks `L3-P0-04`'s `files=16` **and** `L3-P4-07`'s own `hardcoded=0` grep. The executor
must decide. `L3-P4-01`'s `--fixture` / `--live` mutual requirement forecloses the obvious escape.
**Correction.** Either add a 17th fixture file `declared/products/gamma.request.yaml` (and update
`files=17` in `L3-P0-04`), or state that `create-product` for an undeclared product plans from a
request payload passed on the command line, and give that payload literally.

---

### M21 — `L3-P2-01` contradicts itself inside one sentence

**File** `L3-06-tasks.md` · **Task** `L3-P2-01`

> *"Tests assert: exactly sixteen entries; **the six `Blocking` rows** are exactly indices 1, 2, 4, 5,
> 7, 10, 15 — count them: **seven**."*

Seven is correct — verified against §12.2 lines 993–1008 (rows 1, 2, 4, 5, 7, 10, 15 are Blocking).
Acceptance criterion 2 and the SELF-VERIFY (`blocking 7`) both say seven. An executor writing the
test from the first clause asserts `6` and fails its own SELF-VERIFY, then hits a STOP rule telling
it to re-read §12.2 rather than fix the sentence.
**Correction.** *"the seven `Blocking` rows are exactly indices 1, 2, 4, 5, 7, 10, 15."*

---

### M22 — `L3-P3-04` attributes a figure to §53.4 that §53.4 does not state

**File** `L3-06-tasks.md` · **Task** `L3-P3-04`

> *"with `amber_per_product: 2` and 2 products, the Amber ceiling computes as 4; with 8 products, 16;
> with 20 products, 40 (**the three figures §53.4 states**)."*

§53.4 (line 4715) states two: *"up to 2 open Amber per product, so the ceiling reads **16** at eight
products and **40** at twenty."* `4` is derived. The arithmetic is right; the attribution is not, and
this lane's own standing rule is that a transcribed number is never adjusted to fit.
**Correction.** *"…16 and 40 are the two figures §53.4 states; 4 follows from the same rule at two
products."*

---

### M23 — `L3-P0-02` cites invariant 85 for a requirement invariant 85 does not make

**File** `L3-06-tasks.md` · **Task** `L3-P0-02`, acceptance criterion 2

Invariant 85 (line 9565) reads: *"GSD Core is pinned to a tagged release; third-party GitHub Actions
are pinned to full commit SHAs; reusable workflows are consumed by pinned tag."* It says nothing
about Python package pinning. `==`-pinning is sound, but the cited authority does not require it —
and `L3-01-01`'s hash-pinning is the stricter reading of the same (absent) requirement. This is the
citation half of B3.
**Correction.** Cite the L0 runtime decision as the authority, and cite invariant 85 only where the
lane consumes reusable workflows by tag (`L3-P1-07`, `L3-P1-10`), where it genuinely applies.

---

### M24 — `L3-06`'s master table and task bodies disagree on files created

**File** `L3-06-tasks.md` · **Tasks** `L3-P4-01` (row 40), `L3-P5-01` (row 50), `L3-P1-17` (row 24)

| Row | Table says | Body also creates |
| --- | --- | --- |
| 40 | `tools/provision/cli.py`, `tools/provision/tests/test_cli.py` | `tools/provision/plan.py` |
| 50 | `validators/drift/verifier.py` (+test) | `validators/drift/__init__.py` |
| 24 | `reconciler/canary.py`, `reconciler/tests/test_canary.py` | `reconciler/comparators/display_name.py` |

§0.2's close-out instruction is `git add <the exact files named in the task>` — ambiguous where the
two disagree, and an omitted `__init__.py` breaks the next task's import.
**Correction.** Make the master table's Files column authoritative and complete, or drop the column
and point at the body.

---

### M25 — `derived/**` is owned by no lane; two tasks target it, only one raises it

**Files** `L3-02-levels-and-repair.md` `T09` + exit E4; `L3-03-canary-and-integrity.md` `DR-3.1`,
`L3-P3-T06`, `L3-P3-T10`

D93 narrows the reconciler credential's control-plane write scope to `derived/**`; D107 requires the
records head-SHA anchor written *into the control-plane repository*. **PARTITION.md assigns
`derived/**` to no lane.** `L3-03` raises this correctly as `DR-3.1` with an interim default
(`anchor_path: derived/anchors/records-head.yaml`) and enforces the allowlist as data. `L3-02-09`
does not raise it at all and hard-codes the outcome in exit criterion E4
(`['derived/']`). The charter's DECISION REQUIRED section does not mention `derived/**` at all.
**Correction.** Promote `DR-3.1` to a charter-level decision, since its answer changes PARTITION.md —
a frozen document only L0 may amend. Add the cross-reference to `L3-02-09`.

---

## LOW DEFECTS

### L26 — Five homes for one seeded canary
`L3-00` §2.1 `reconciler/canary/**` · `L3-01` `reconciler/canary-binding.yaml` · `L3-P3-T01`
`validators/drift/canary/canary.yaml` · `L3-P0-04` `reconciler/fixtures/fixture-a/canary.yaml` ·
`L3-07` §3 `reconciler/test/fixtures/org/canary/`. §53.1 requires *"a permanent seeded drift
record … exists at all times"*; five candidate locations is how one ends up existing nowhere.
**Correction.** One path, named in the charter §2.1 table, referenced by the other four.

### L27 — Charter `DR-L3-01` asks L0 for a string §11.3 already supplies
Same root as B10. Narrow to the registration phase.
**Correction.** *"Needed in `contracts/**`: the phase at which `control-plane/blocking-drift`
(§11.3, line 867) is added to each repository's required-status-check list."*

### L28 — `L3-04`'s package root is never stated
`L3-04-07` names `tools/provision/provision/codeowners/render.py`; §0.6 shows `python -m provision`
with no working directory; §0.4 implies `$CP/tools/provision`. The doubled `provision/provision/` is
deliberate but reads as a typo.
**Correction.** State the package root and the `PYTHONPATH`/`cd` contract once in §0.1.

### L29 — `L3-04` task bodies elide file contents
Every `Commands` block contains `# ... write the files ...` where `L3-06` and `L3-01` give literal
heredocs. `L3-04-07` compensates with exact rendering rules and negative-check semantics; `T03`,
`T04`, `T11` and `T12` do not, leaving a one-line "Contract" column per file while acceptance
criteria assert exact pytest node ids (`test_direct_machine_fails`, `test_machine_in_team_fails`)
the executor must invent to make its own acceptance pass.
**Correction.** For the reader PARTITION.md line 45 names, give the module skeleton and the test
names literally, as `L3-06` does throughout.

---

## Executability assessment — the two most complex tasks

### `L3-P4-07` — `create-product` orchestrator (size L, 5 merged dependencies)

**Verdict: NOT executable by an agent with no context.**

What is good: the thirteen step ids are given literally, in §19.1's own order, each with its spec
line; the two manual steps are named; the anti-hard-coding rule is proven negatively
(`grep -rc 'alpha\|beta' … → 0`); the expected summary line is byte-exact; the STOP rule quotes
§19.1's *"If a human must edit a dashboard to add a product, that is a defect."*

What defeats it:

1. **M20** — it plans `--product gamma`, which does not exist in `fixture-a`, and never says where
   gamma's assignments come from. Steps 3–5 cannot execute; adding gamma to the fixture breaks two
   other assertions. The agent must decide.
2. **M19** — its three merged dependencies (`L3-P4-02`, `P4-03`, `P4-05`) expose signatures the
   orchestrator must call, and each is documented with two different signatures.
3. **B5** — if `L3-04-13` (the same orchestrator, different plan) has also been dispatched, the
   agent writes into a package layout that the other task's `lane_guard` rejects.
4. The §19.1 decomposition disagrees with `L3-00-04`'s `OPERATIONS.md`, which the same lane tells
   the agent to treat as the enumeration of record: `OPERATIONS.md` gives 13 outputs with
   registration as **one** item plus an alert-channel item plus a CONFIGURE item; `L3-P4-07` gives 13
   with registration split into **three** and the other two moved to manual steps and to `L3-P4-08`.
   Both say "13"; they are not the same 13.

### `L3-P8-05` — Lane acceptance-matrix runner (size M, depends on all 77 preceding tasks)

**Verdict: NOT executable — blocked, and its blocker is undeclared.**

What is good: the AT→task mapping table is explicit and every AT id in it verifies against §100
(AT-001 → 9305, AT-002 → 9306, AT-008 → 9312, AT-017 → 9326, AT-018 → 9327, AT-032 → 9346,
AT-033 → 9347, AT-036 → 9358, AT-037 → 9359, AT-102 → 9351, AT-110 → 9439). The STOP rule is exactly
right: *"do not adjust the test to match the code."*

What defeats it:

1. **H17** — AT-110 maps to `L3-P5-06`, which §1 declares blocked on `L3-D3`. `MATRIX passed=11
   total=11` is unreachable until L0 rules on GitHub App vs fine-grained PAT, and the decision table
   does not say so.
2. **H13** — the matrix re-runs Phase-1 acceptance paths after `L3-P1-17` has merged, so the
   comparator runs it invokes return exit `3` where their tasks expect `0`/`2`.
3. **H16** — the charter obligates fourteen ATs; the matrix knows eleven. An agent that reads the
   charter first will conclude the runner is incomplete and, per acceptance criterion 2 (*"an unmapped
   AT id fails the runner"*), cannot tell whether to add AT-021, AT-034 and AT-051 or leave them out.
4. AT-002 and AT-001 are asserted against **dry-run plans** (`writes=0`). §100's AT-002 requires
   *"Reconciliation grants access"* — an applied outcome. The task does not say how a plan-only run
   discharges an AT whose text describes an effect, and the agent has no authority to decide that it
   does.

---

## What is clean

Recorded so the rework does not damage it.

| Check | Result |
| --- | --- |
| **1. Path-ownership violations** | **None.** Every `git add`, `cat >`, `mkdir -p` and file-table entry across all eight files lands under `reconciler/**`, `tools/provision/**` or `validators/drift/**`. Foreign paths appear only as read-only inputs, correctly disclaimed (`L3-01` §3, `L3-06` §0.1, `L3-03` §3, `L3-04` closing table, `L3-05` §5). The `reconciler/fixtures/declared/registries/**` mirrors are lane-local test data, not writes to L1. |
| **2. Dangling dependencies** | **None.** Every `L3-0N-Tnn`, `L3-Pn-nn`, `L3-P3-Tnn`, `L3-Dn`, `DR-*`, `DEC-*`, `D-L3-*` reference resolves to a definition in the same corpus. |
| **3. Missing controls** | **None.** All 194 tasks carry a SELF-VERIFY block and a STOP rule. `L3-05-05`…`T20` inherit theirs from the *"Detector tasks — common shape"* section, which is explicit and complete. Blocker-issue templates are present in all seven plan files. |
| **6. Citation integrity (sampled)** | **High.** Verified present and at the cited lines: AT-001/002/005/008/017/018/021/032/033/034/036/037/051/071/102/110, EC-109, EC-111; invariants 3, 4, 7, 24, 26, 36–38, 44, 47, 52, 53, 55, 56, 57, 58, 72, 77, 79, 80, 81, 85; SIG-02/03/05/13 at 4531/4532/4534/4542; D53, D63, D69, D73, D77, D80, D87, D89, D91, D92, D93, D95, D96, D101, D107; sections 6.7, 10.1, 10.2, 11.2, 11.3, 11.4, 12.1–12.7, 15.1, 15.7, 17.3, 18.1, 19.1, 20.1, 21.1, 21.4, 26.4, 27.2, 28.1, 29.1, 29.2, 33.1, 33.2, 33.4, 36.4, 37.3, 40.1–40.3, 41.2, 43, 44.2, 44.5, 46.1, 49.1, 51.2, 52.2, 52.4, 52.6, 53.1–53.7, 54.3, 55, 58.4, 60.2, 60.3, 61.3, 61.5, 63.1, 64.1, 64.2, 74, 90.6, 91.8, 94.7, 95.4, 96.2, 97.1, 97.2, 98.2, 98.3, 99.1, 99.2, 99.4, 99.5, 99.6, 100, 101. §52.6's "twenty-nine entries" and §12.2's sixteen orphan rows with seven Blocking both check out exactly. **No invented identifier was found.** The five citation defects are misreadings (B10, H11, H12, M22, M23), not fabrications. |
| **Fixture arithmetic** | `L3-06`'s `fixture-a` is internally consistent: every finding count and `compared` value in `L3-P1-02`…`P2-05` was recomputed by hand against the sixteen fixture files and matches, including the 4/3/5/2 orphan splits and the `departing`-is-still-active predicate. |
| **Truncation** | All eight files terminate on complete content. The `_DAMAGE.md` truncations of `L3-01` (197 lines) and `L3-03` (332 lines) have been repaired — now 7,574 and 6,023 lines with intact exit-criteria tables. |

---

## Dispatch gate

Do not dispatch Lane 3 until, at minimum:

1. **B1** — one plan designated authoritative; the other stripped of executable task ids.
2. **B2** — phase numbers made one-to-one with deliverables lane-wide.
3. **B3** — one runtime and one pinning mechanism recorded; the losing file reissued.
4. **B4** — `L3-04` either made fixture-backed or marked ASSISTED behind a live-org gate.
5. **B5** — one internal layout table published and conformed to.
6. **B6 / B7** — comparison-set cardinality fixed once, and the charter's DoD made satisfiable.
7. **B8** — invented registry schema removed from `fixture-a`; `DR-L3-05-A`…`E` honoured.
8. **B9** — one decision register, one id scheme.
9. **B10** — `DEC-L3-02-02` retired against §11.3 line 867.

`H11`–`H17` are then resolvable inside the surviving plan without further L0 arbitration.
