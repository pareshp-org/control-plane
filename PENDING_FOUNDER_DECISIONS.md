# Pending Founder Decisions

> Last updated: 2026-09-08
> These decisions require bendrohit-eng to choose one option. Agents cannot resolve them.
> Choosing one cascades to resolve multiple blockers per decision.
>
> Source documents: `lanes/L1-99-review.md` (D2, D3, D5), `lanes/L2-99-review.md` (B1-L2),
> `lanes/L3-99-review.md` (B1-L3).

---

## PFD-001 — L1 Validator Engine Design (D2)

> **RESOLVED 2026-09-08** — FD-094: L1 validator = Option B (L1-03 design, cli.py, R01-R18)

**Source:** `lanes/L1-99-review.md` §D2
**Status:** BLOCKING — do not dispatch L1 until resolved
**Blocks:** L1-D6 (test phase deadlocks on T01), L1 Phase 1 dispatch, L2 CI wiring (L2 wires its workflow to whichever entrypoint L1 freezes)

**Background.** Five L1 documents each independently designed and froze the validator that L2's CI pipeline must call. They are incompatible at every level: entry point path, invocation grammar, exit-code meanings, rule-identifier scheme, and rule storage layout. `validators/registry/cli.py` is authored twice (by L1-03 and L1-05) with explicitly frozen but different argument grammars. Exit code `3` means GATE CANARY FAILURE in Option C but internal error in Option D — an L2 workflow keyed to one silently mis-gates the other.

**Options (pick exactly one):**

- **A (L1-02 design)** — Standalone schema-check driver at `validators/registry/schema-check/check.py`, invoked with `python check.py`. No rule-ID system; validates schema structure only against `schemas/**`. Exit codes not defined. Simplest surface; does not cover the referential-integrity and date rules that subsystem B requires.

- **B (L1-03 design)** — CLI at `validators/registry/cli.py`, invoked as
  `python -m validators.registry.cli --root <p> --as-of <d> --records-root <p> --format json --rule Rxx`.
  Exit codes 0/1/2. Rules named `R01`–`R18` with sub-codes (e.g., `R07.1`). Stored as flat Python files `rules/r07_coverage_rota.py`. Includes rota-coverage rules (AT-047). Ships a literal baseline fixture and `make-fixture.sh`; the fixture pattern is the one the review calls best.

- **C (L1-04 design)** — Gate script at `validators/registry/gate.py`, invoked as
  `python3 validators/registry/gate.py --root . --mode all --report <p>`.
  Exit codes 0/1/2/**3** (3 = GATE CANARY FAILURE). Rules identified by directory name, stored as `rules/<id>/rule.yaml` + `check.py`. Canary-seeding built in. The negative-test discipline (universal must-fail recipe using `INVALID: [`) is called the strongest pattern in the review.

- **D (L1-05 design)** — CLI at `validators/registry/cli.py` (same path as B, different grammar), invoked as
  `python -m validators.registry.cli validate --file <p> --dir <p> --today <d> --format text`.
  Exit codes 0/1/2/**3** (3 = internal error; conflicts with C's meaning). Rules named `R-CAP-01`, `R-PPL-02`, `R-REF-01`. Stored as `rules/r_cap_01.py`. This is the design L1-05-tasks.md freezes as "the only interface Lane 2 may call."

- **E (L1-07 design)** — Shell orchestrator at `validators/registry/run-all.sh`, invoked as `bash validators/registry/run-all.sh`. No exit codes or rule IDs defined. Thin wrapper only; delegates to other validators. Suitable only as a convenience runner, not as the frozen L2 contract surface.

**Recommendation:** Option B or C. Option B ships the most complete executable baseline and the review judges its fixture pattern best. Option C has the strongest CI-integration story (canary and gate built in, directory-per-rule avoids shared mutable files). Option D cannot be chosen alongside B because they both write `validators/registry/cli.py` with incompatible grammars. Option A is incomplete. Option E is a wrapper, not a design.

**To decide:** In next L0 session say: "PFD-001: L1 validator engine = Option B" (or C, or D). Then write the chosen invocation contract to `contracts/validator-contract.md` and rewrite all five L1 documents against it.

---

## PFD-002 — L1 Task-ID Grammar and Dispatch Surface (D3)

> **RESOLVED 2026-09-08** — FD-095: L1 dispatch surface = Option A (L1-05-tasks.md sole dispatch)

**Source:** `lanes/L1-99-review.md` §D3
**Status:** BLOCKING — do not dispatch L1 until resolved
**Blocks:** L1 executability (an executor handed L1-05 re-authors from scratch work that five other documents already specify, and vice versa); D20 (four repo-root conventions); D22 (three AT lists)

**Background.** Lane 1 contains 127 task bodies across 8 files, each using its own id scheme. `L1-05-tasks.md` §0 tells the executor "do not open another document to decide what to do next — everything you need is here" but delivers only 31 of its 61 declared bodies (after D1 resolution verified all 61 are present, the 127 bodies exist but are spread across documents, not consolidated in L1-05). `L1-05-tasks.md` contains not one reference to any `L1-01-T*`, `L1-02-T*`, `L1-03-T*`, `T-L1-04-*`, or `L1-06-T*` id.

The five schemes in use:
1. `L1-{doc}-T{nn}` — used by L1-00, L1-01, L1-02, L1-03, L1-06 (five files, same pattern)
2. `T-L1-04-{nn}` — reversed prefix, used by L1-04 only
3. `L1-{nnn}` — numeric, no document prefix, used by L1-05
4. `L1-RB-{nn}` — runbook prefix, used by L1-07
5. (L1-05 also mixes in its own `L1-D01`–`L1-D03` decision ids)

**Options (pick exactly one):**

- **A — L1-05-tasks.md becomes the sole dispatch surface.** Phase documents (L1-00 through L1-04, L1-06, L1-07) are rewritten as reference/design-note files with no executable task bodies. All 127 task bodies are absorbed into L1-05-tasks.md under a single `L1-{nnn}` scheme. The phase documents retain their spec-transcription sections and DECISION REQUIRED items. Executors open only L1-05-tasks.md.

- **B — Phase documents are the dispatch surface; L1-05-tasks.md is replaced by an index.** L1-05-tasks.md is deleted and replaced with a single ordering-index file that lists phase-document tasks in execution order. All ids are renumbered to one scheme (`L1-{doc}-T{nn}` across all files). Executors follow the index, open each phase document for the task body.

**Recommendation:** Option A, because L1-05's existing `L1-{nnn}` scheme is already partially built and because concentrating all task bodies in one file reduces executor navigation overhead. The review notes that L1-03's literal baseline fixture and `make-fixture.sh` pattern is the one worth preserving, but the fixture approach can be ported into L1-05's structure.

**To decide:** In next L0 session say: "PFD-002: L1 dispatch surface = Option A" (or B). Then renumber all tasks to one scheme and publish the mapping in charter §14.

---

## PFD-003 — L1 Schema File Layout (D5)

> **RESOLVED 2026-09-08** — FD-096: L1 schema layout = Option A (flat schemas/registry/<name>.v1.schema.json)

**Source:** `lanes/L1-99-review.md` §D5
**Status:** BLOCKING — do not dispatch L1 until resolved
**Blocks:** D6 (test phase T01 deadlocks because schema-set diff depends on filenames), L1-03-T08 STOP rule (references a path no task ever creates), L3/L5 cross-lane artifact promised but non-existent under two of the three conventions

**Background.** Three L1 documents each fix a different directory layout for the schema files. `L1-03-T08`'s STOP rule reads for `schemas/registry/people.v1.schema.json` — a path that neither L1-02 nor L1-05 ever creates. `L1-06-tests.md` T01 uses `-maxdepth 1` to find schemas, which returns zero files under Option B (schemas are at depth 3). `L1-05`'s `L1-D02` decides that `schemas/registry/capabilities.v1.schema.json` will never exist, while `L1-00-charter.md` §6 promises that exact file to L3 and L5.

**Options (pick exactly one):**

- **A (Charter §3.1)** — Flat file, version in filename only:
  `schemas/registry/<name>.v1.schema.json`
  Example: `schemas/registry/people.v1.schema.json`
  Discovery at gate time: `find schemas/registry schemas/product -maxdepth 1 -name '*.schema.json'` — works without version subdirectory indirection.

- **B (L1-02 design)** — Versioned subdirectory:
  `schemas/registry/<name>/v<N>/<name>.schema.json`
  Example: `schemas/registry/people/v1/people.schema.json`
  Supports adding v2 alongside v1 without renaming. The L1-06-tests.md `-maxdepth 1` discovery must be changed to `-maxdepth 3`. Any flat STOP rule that names a depth-1 path fails silently.

- **C (L1-05 design)** — Flat file with type suffix:
  `schemas/registry/<name>.registry.v1.schema.json` (for registry schemas)
  `schemas/product/<name>.contract.v<N>.schema.json` (for product schemas)
  Example: `schemas/registry/people.registry.v1.schema.json`
  Also moves the service schema to the registry tree: `schemas/registry/service.v1.schema.json` (differs from Charter's `schemas/product/service.v1.schema.json`). The suffix makes type explicit but makes all cross-lane path references wrong.

**Recommendation:** Option A. It matches the charter (the lane's constitution), it is what all cross-lane artifact promises are written against (L3, L5 both expect flat paths), and it is the only layout where the existing STOP rules and the `-maxdepth 1` test gate work without modification.

**To decide:** In next L0 session say: "PFD-003: L1 schema layout = Option A" (or B or C). Then fix `L1-02` §0.1 and all `L1-05` FILES fields against the chosen layout, and re-point `L1-03-T08`'s STOP rule at a real path.

---

## PFD-004 — L2 Canonical Plan (B1)

> **RESOLVED 2026-09-08** — FD-097: L2 canonical plan = Option A confirmed (L2-05 authoritative)

**Source:** `lanes/L2-99-review.md` §B1
**Status:** Decision asserted by FD-B1-L2 (2026-09-02) — confirm and authorize cleanup
**Blocks:** L2 dispatch; B2 (23 task ids bound to two different tasks); B3 (decision questions defined differently in each file)

**Background.** Lane 2 contains two mutually incompatible task decompositions. `L2-05-tasks.md` declares itself "the complete, ordered work list for Lane 2 — 76 tasks." The five phase files (L2-01, L2-02, L2-03, L2-04, L2-06) define a different 78-task decomposition. Not one id from any phase file appears in L2-05's master table, and not one L2-05 id appears in any phase file. Both L2-05-tasks.md (via its header) and each phase file (via "SUPERSEDED" banners) assert the same decision (L2-05 wins) was made as FD-B1-L2 on 2026-09-02. However, the downstream cleanup — renumbering the 23 colliding ids, re-pointing L2-06-tests.md, and re-expressing the phase file content as reference-only — has not been done.

**Options:**

- **A — L2-05-tasks.md (76 tasks) is authoritative.** Phase files are reference-only design notes. The 23 colliding ids (L2-T500–L2-T516 and L2-T520–L2-T525) are renumbered in L2-04 and L2-02 to avoid the L2-05 range. L2-06-tests.md is re-pointed. Decision questions D-L2-07, D-L2-08, D-L2-09 (currently defined differently in each file) are reconciled into a single definition in L2-05.
  *Note: This is what the FD-B1-L2 banner asserts.*

- **B — Five phase files (78 tasks) are authoritative.** L2-05-tasks.md §2 master table is regenerated as an execution-order index over the phase-file ids. Phase-file ids are preserved. L2-05 body tasks that have no phase-file counterpart (L2-T517–519, L2-T521–525) are either absorbed into phase files or explicitly dropped.

**Recommendation:** Option A is already asserted (FD-B1-L2 banner in L2-05-tasks.md; "SUPERSEDED" banners in all five phase files). Confirm Option A and authorize agents to execute the cleanup: renumber L2-04's L2-T530–L2-T546 and L2-02's L2-T550–L2-T558, re-point L2-06-tests.md lines 72/1140/1246/1738, and reconcile the D-L2-07/08/09 definitions.

**To decide:** In next L0 session say: "PFD-004: L2 canonical plan = Option A confirmed" (or choose B). If A: authorize the id-renumbering cleanup described above.

---

## PFD-005 — L3 Canonical Plan (B1)

> **RESOLVED 2026-09-08** — FD-098: L3 canonical plan = Option A confirmed (L3-06 authoritative, 4 additions ratified)

**Source:** `lanes/L3-99-review.md` §B1
**Status:** Decision asserted by FD-B1-L3 (2026-09-02) — 4 work items still need L0 ruling
**Blocks:** L3 dispatch; B2–B10 cascade from the dual-plan conflict; 4 items from superseded phase files have no L3-06 equivalents

**Background.** Lane 3 contains two complete, mutually exclusive implementation plans. `L3-06-tasks.md` opens with "This file is the complete, ordered work list for Lane 3 — 78 tasks." The six phase files (L3-00 through L3-05) plus the test/runbook file (L3-07) define a separate 116-task plan across five other id schemes. Not one id from any phase file appears in L3-06, and not one `L3-P*` id appears in any phase file. Both plans build the same artifacts: two comparator registries, two canary implementations, two orphan detectors, two `create-product` orchestrators. L3-06-tasks.md bears an "[AUTHORITATIVE — FD-B1-L3 2026-09-02]" banner, but the L3-99 review was never superseded. Additionally, four work items from the phase files were found to have no L3-06 equivalents (Session 12, 2026-09-08); they were added as L3-P0-CMP10, L3-P0-CMP12, L3-P0-AT001, L3-P0-DEL14 — but these additions themselves need L0 sign-off.

**Options:**

- **A — L3-06-tasks.md (78 + 4 additions = 82 tasks) is authoritative.** Phase files become non-executable design notes (task bodies stripped, spec-transcription and DECISION REQUIRED sections kept). The four Session-12 additions (CMP10, CMP12, AT001, DEL14) are ratified as part of the plan. Runtime, package layout, and phase numbering follow L3-06 conventions.
  *Note: This is what the FD-B1-L3 banner asserts.*

- **B — Seven phase files (116 tasks) are authoritative.** L3-06-tasks.md is reissued as an execution-order index over the phase-file ids. Phase-file ids and phase numbering are preserved. The B3 runtime conflict (Python multiprocessing in L3-06 vs single-threaded in phase files) and B5 package layout conflict must be resolved against phase-file conventions.

**Key difference beyond task count:** B3 in L3-99 identifies an incompatible runtime model — L3-06 uses Python `multiprocessing` and a batch comparator loop; the phase files use a single-threaded sequential runner. B5 identifies two different package layout schemes. These mean Options A and B are not mergeable without re-deciding both.

**Recommendation:** Option A. The FD-B1-L3 decision is already asserted, L3-06 has the newer Session-12 additions, and the phase files are substantially larger and harder to audit. Ratify Option A, strip phase-file task bodies, and formally close the four CMP10/CMP12/AT001/DEL14 additions as part of the plan.

**To decide:** In next L0 session say: "PFD-005: L3 canonical plan = Option A confirmed" (or choose B). If A: ratify the four Session-12 task additions and authorize phase-file task-body removal.

---

## Decision Session Template

Copy into the next L0 session log and fill in:

```
## L0 Decision Session — [DATE]

PFD-001: L1 validator engine         = Option __   (A / B / C / D / E)
PFD-002: L1 dispatch surface         = Option __   (A / B)
PFD-003: L1 schema file layout       = Option __   (A / B / C)
PFD-004: L2 canonical plan           = Option A confirmed  (or B)
PFD-005: L3 canonical plan           = Option A confirmed  (or B)
PFD-008: Task-ID grammar             = Option __   (A / B / C)
PFD-009: Lane reviewer logins        = L1:__ L2:__ L3:__ L4:__ L5:__
PFD-010: L2 branch-model definitions = Option __   (A / B / C)
PFD-011: L2 namespace collision      = Option __   (A / B)
PFD-012: L2 actor-gate form          = Option __   (A / B / C)
PFD-013: L3 bootstrap live-org       = Option __   (A / B / C)
PFD-014: L3 provision layout         = Option __   (A / B)  [after PFD-005]
PFD-015: L3 fixture-a schema fields  = Option __   (A / B / C)
PFD-016: FTE application in per-day scheduled availability (L4-P4-01) = Option __   (A / B)
PFD-017: Ready-queue-miss event emit timing (L4-P4-02)                = Option __   (A / B)
PFD-018: Working calendar selection rule (L4-P4-03)                   = Option __   (A / B)
PFD-019: Capacity Profile lane ownership (L4-P4-04)                   = Option __   (A / B)
```

Once all five core PFDs are filled in, agents can write the chosen contracts to `contracts/**` and
rewrite the affected lane documents against them. FD-014 gate clears after PFD-001, PFD-002,
and PFD-003 are answered and written to contracts. PFD-008 unblocks format-validation tooling;
PFD-009 unblocks CODEOWNERS finalization.


---

## PFD-006 — L5 AT-022 Break-Glass Owner Decision (DR-L5-07-A)

> **RESOLVED 2026-09-08** — DEFERRED (no FD yet — second break-glass owner TBD)

**Blocks:** L5-07-T09/AT-022 past INCOMPLETE state  
**What L0 must supply:**
- A. The second Owner GitHub login (who can break glass if bendrohit-eng is unavailable)
- B. The escrow custodian (who holds the break-glass credentials)
- C. The drill schedule (how often to run the continuity drill)

**File:** `lanes/L5-07-tests-and-runbook.md:1347`

---

## PFD-007 — L5 AT-029/AT-035 Drill Names (DR-L5-07-D)

> **RESOLVED 2026-09-08** — FD-099: L5 drills = bendrohit-eng executor, unrestricted window

**Blocks:** L5-07-T14 AT-029 legs 2-3 past INCOMPLETE state  
**What L0 must supply:**
- A. The drill product name (which product runs the disruption drill)
- B. The DevOps executor GitHub login (who runs the drill)
- C. The authorised drill window (when drills are permitted)

**File:** `lanes/L5-07-tests-and-runbook.md:2212`

---

## PFD-008 — Task-ID Grammar `T` Infix (protocol/00 Q2 discrepancy)

> **RESOLVED 2026-09-08** — FD-082: Task-ID grammar = Option A (L<N>-<FF>-<NN>, no T infix)

**Blocks:** Format-validation regexes, concordance tooling, CI task-id checks  
**Context:** Three live formats in the codebase:
- Charter format: `L0-00-T01` (with `T` infix between FF and NN)
- Lane-file format: `T-L1-04-01` (with `T-` prefix before lane)
- FD-072 ruling: `L<N>-<FF>-<NN>` (no `T` at all, e.g. `L1-04-02`)

**Options:**
- **A** — Keep `L<N>-<FF>-<NN>` (no `T`): most compact, requires updating ~845 IDs in charter and plan files
- **B** — Keep `L<N>-<FF>-T<NN>` (charter format): preserves charter headers, requires updating lane-file prefix `T-` style
- **C** — Keep `T-L<N>-<FF>-<NN>` (lane-file prefix format): requires updating charter headers

**Recommendation:** Option A (`L<N>-<FF>-<NN>`) — already the ruling in FD-072; most parseable by regex; bulk update is one sed pass.  
**To decide:** Add to next L0 session, say "FD-082: Task-ID grammar = Option A/B/C"

---

## PFD-009 — Five Lane Reviewer GitHub Logins

> **RESOLVED 2026-09-08** — FD-083: Lane reviewers = all 5 = bendrohit-eng (bootstrap)

**Blocks:** CODEOWNERS finalization, branch protection reviewer assignment, PR review routing  
**Context:** `CODEOWNERS` has `@LANEn_REVIEWER` placeholders (n=1..5). These are the people who will review PRs touching each lane's paths. They must be members of `pareshp-org`.

**What L0 must supply:**
- L1 reviewer GitHub login: `_________________`
- L2 reviewer GitHub login: `_________________`
- L3 reviewer GitHub login: `_________________`
- L4 reviewer GitHub login: `_________________`
- L5 reviewer GitHub login: `_________________`

**Note:** Each reviewer must already have a GitHub account and must be invited to `pareshp-org`. L0 can assign themselves (`bendrohit-eng`) to all 5 initially — that is a valid bootstrap option.  
**To decide:** Add to next L0 session, say "FD-083: Lane reviewers = ..." or "all lanes: bendrohit-eng for bootstrap"

---

## PFD-010 — L2 Decision Definitions: Integration, Promotion, Release (B3)

> **RESOLVED 2026-09-08** — FD-084: L2 branch-model = Option A (L2-05 definitions canonical)

**Blocks:** L2 merge-criteria automation, L2-05 task reconciliation; downstream of PFD-004  
**Context:** Three decision questions (D-L2-07, D-L2-08, D-L2-09) each have 3–4 contradictory definitions spread across L2-01, L2-03, L2-04, and L2-05. L2-05 is asserted authoritative (PFD-004 / FD-B1-L2) but its definitions conflict with the phase-file definitions that were written first.

- **D-L2-07** — "integration" (branch merge criteria): What conditions must be met before a feature branch is merged to the integration branch?
- **D-L2-08** — "promotion" (inter-branch move): What is the exact definition of a promotion event — which branches are involved, what triggers it, and who authorises it?
- **D-L2-09** — "release" (final delivery): What constitutes a release — cut from which branch, what artefacts are produced, what sign-off is required?

**Options:**
- **A** — Accept L2-05-tasks.md's definitions as canonical for all three terms; rewrite conflicting phase-file definitions to match.
- **B** — Accept L2-01's definitions (the first to be written) as canonical; update L2-05 to match.
- **C** — Define each term fresh in a new `contracts/l2-branch-model.md` and rewrite all files against it.

**Recommendation:** Option A — consistent with PFD-004 Option A (L2-05 is authoritative). Avoids introducing a new contract file before the canonical plan is stable.  
**To decide:** Add to next L0 session, say "FD-084: L2 branch-model definitions = Option A/B/C"

---

## PFD-011 — L2 Task-ID Namespace Collision (B4)

> **RESOLVED 2026-09-08** — FD-085: L2 namespace = Option A (retire L2-P*-T* IDs)

**Blocks:** L2 executor routing, automated task-lookup tooling, concordance checks  
**Context:** L2-01 (phase file) uses task IDs `L2-P1-T00` through `L2-P1-T15`. L2-05-tasks.md uses the same numeric range (`L2-T00`–`L2-T15`) under a different prefix scheme. After PFD-004 Option A is confirmed (L2-05 wins), the phase-file IDs become non-executable but still appear in search results and tooling, causing routing errors. Both namespaces must be made distinct, or the phase-file IDs must be fully retired.

**Options:**
- **A** — Retire all `L2-P*-T*` IDs from phase files entirely; replace with `[retired]` stubs. L2-05 IDs (`L2-T*`) are the only live namespace.
- **B** — Rename phase-file IDs to `L2-REF-P1-T*` to make them clearly non-executable; tooling excludes the `REF` prefix from dispatch.

**Recommendation:** Option A — cleaner; fewer live namespaces reduce regex complexity and false concordance hits.  
**To decide:** Add to next L0 session, say "FD-085: L2 namespace collision = Option A/B"

---

## PFD-012 — L2 Actor-Gate Canonical Form (B6)

> **RESOLVED 2026-09-08** — FD-086: L2 actor-gate = Option A (scripts/actor-gate.sh)

**Blocks:** L2 CI workflow wiring; L2 gate-check automation  
**Context:** Three L2 documents each define `actor-gate` differently and incompatibly:
- L2-01 defines it as a branch-protection rule (GitHub branch settings).
- L2-03 defines it as a YAML workflow step (`actor-gate:` job in the CI pipeline).
- L2-05 defines it as a shell script (`scripts/actor-gate.sh`) called by the workflow.

All three definitions produce different observable behaviour at gate-check time. L2-06-tests.md currently tests for the L2-05 shell-script form.

**Options:**
- **A** — Shell script (`scripts/actor-gate.sh`) per L2-05; L2-06 tests unchanged.
- **B** — YAML workflow step per L2-03; rewrite L2-06 tests to assert the workflow-step form.
- **C** — Branch-protection rule per L2-01; drop actor-gate from the CI workflow entirely.

**Recommendation:** Option A — consistent with PFD-004 Option A (L2-05 authoritative); L2-06 tests already cover it.  
**To decide:** Add to next L0 session, say "FD-086: L2 actor-gate form = Option A/B/C"

---

## PFD-013 — L3 Live GitHub Org vs Bootstrap Prohibition (B4)

> **RESOLVED 2026-09-08** — FD-087: L3 bootstrap = Option C (split L3-04 dry-run + live)

**Blocks:** L3-04 executability; L3 Phase 0 dispatch  
**Context:** A direct contradiction exists between two L3 documents:
- L3-04 requires live GitHub org API calls to function (it provisions repos, teams, and webhooks in `pareshp-org`).
- L3-06 §0.4 explicitly states "no live org calls during bootstrap phase."

Running L3-04 as written violates L3-06's bootstrap constraint. Deferring L3-04 blocks the org-provisioning tasks that several later L3 tasks depend on.

**Options:**
- **A** — Permit live org calls from L3-04 during bootstrap; remove or scope the §0.4 prohibition to cover only product-facing calls, not provisioning calls.
- **B** — Rewrite L3-04 to operate in dry-run / mock mode during bootstrap; live org provisioning deferred to a post-bootstrap L3 phase.
- **C** — Split L3-04 into two tasks: one dry-run task (runs during bootstrap) and one live task (runs after the bootstrap constraint lifts).

**Recommendation:** Option C — preserves the bootstrap safety constraint while unblocking progress; gives L0 a clear phase boundary.  
**To decide:** Add to next L0 session, say "FD-087: L3 bootstrap live-org = Option A/B/C"

---

## PFD-014 — L3 tools/provision Package Layout (B5)

> **RESOLVED 2026-09-08** — FD-088: L3 package layout = Option A (one-subdir-per-tool)

**Blocks:** L3 package authoring; downstream of PFD-005  
**Context:** Two L3 plans produce incompatible directory structures under `tools/provision/`:
- L3-06 layout: `tools/provision/{comparator,canary,orphan,create-product}/` — one subdirectory per tool, flat module files inside.
- Phase-file layout: `tools/provision/lib/{comparator.py,canary.py,orphan.py}` with a separate `tools/provision/bin/` for entry-point scripts.

Import paths, `pyproject.toml` package names, and test fixture paths differ between the two layouts. Choosing the wrong layout causes tests written against one layout to fail silently under the other.

**Options:**
- **A** — L3-06 layout (one subdirectory per tool); consistent with PFD-005 Option A.
- **B** — Phase-file layout (`lib/` + `bin/` split); consistent with PFD-005 Option B.

**Recommendation:** Option A — consistent with PFD-005 Option A (L3-06 authoritative). Resolve PFD-005 first.  
**To decide:** Add to next L0 session, say "FD-088: L3 tools/provision layout = Option A/B" (after deciding PFD-005)

---

## PFD-015 — L3-06 Fixture-A Invented Schema Fields (B8)

> **RESOLVED 2026-09-08** — FD-089: L3 fixture-a = Option B (reject invented fields)

**Blocks:** L3 test validity; DR-L3-05-A through DR-L3-05-E must be formally resolved before tests are trusted  
**Context:** L3-06's `fixture-a` pre-resolves five open decisions (DR-L3-05-A through DR-L3-05-E) by inventing schema fields that do not appear in any ratified L1 schema: `capability.scope`, `capability.ttl`, `person.lane_assignments[]`, `product.phase_gate`, and `registry.version_policy`. Tests built against these fixtures will return green even if the invented fields are later rejected, masking real failures.

**Options:**
- **A** — Ratify all five invented fields as valid additions to the L1 schema; add them to `schemas/registry/*.v1.schema.json` under PFD-003's chosen layout.
- **B** — Reject the invented fields; rewrite fixture-a to use only currently ratified schema fields; mark DR-L3-05-A through DR-L3-05-E as explicitly deferred.
- **C** — Ratify some, reject others — L0 reviews each of the five fields individually and decides per field.

**Recommendation:** Option C for correctness; Option B if bootstrap speed is the priority. Option A risks ratifying fields that conflict with L2/L4/L5 schemas not yet reviewed.  
**To decide:** Add to next L0 session, say "FD-089: L3 fixture-a schema fields = Option A/B/C" — if C, decide each of DR-L3-05-A through DR-L3-05-E individually.

---

## PFD-016 — L4 FTE Application in Scheduled Availability (D-L4-P4-01)

> **RESOLVED 2026-09-08** — FD-090: L4 FTE = Option B (fte not re-applied at day level)

**Blocks:** Rule R6 of `scheduled-availability.py` (L4-T406) only. Every attention fixture supplies `scheduled_availability_hours` directly, so no derivation and no test is blocked.  
**Context:** §7.3 line 629 states "`fte` is a capacity multiplier, not a status." §7 line 577 shows a part-time person can be expressed either as a short schedule with `fte: 1.0`, or a full schedule with `fte: 0.5`. Applying both to a single day halves a half-day twice. The question is which form is canonical for per-day computation.  
**Question:** In computing scheduled availability for one day, is the declared `schedule` span multiplied by `fte`, or is `fte` an aggregate-period multiplier that the per-day figure must not apply?  
**L4 default until answered:** `calibration.yaml` declares `fte_application: none`; the declared `schedule` span is authoritative and `fte` is not applied a second time, grounded in line 577's "part-time is configuration."  
**Options:**
- **A** — Apply `fte` as a multiplier to the per-day schedule span (`scheduled_hours = (end − start) × fte`)
- **B** — The declared schedule span is the full per-day availability; `fte` is not re-applied at the day level (current default, `fte_application: none`)

**To decide:** Add to next L0 session, say "FD-090: L4 fte_application = Option A or B"

---

## PFD-017 — L4 Ready-Queue-Miss Event Emit Timing (D-L4-P4-02)

> **RESOLVED 2026-09-08** — FD-091: L4 RQM emit = Option A (hold until cause-prompt answered)

**Blocks:** The `--emit` path of `rqm-detect` (L4-T417) only. Classification, the `--json` verdict, and the whole of `L4-P7-T10`'s suite are unaffected — that suite never calls `--emit`.  
**Context:** §97.5 line 8984 states the board automation "appends a Ready-queue-miss event with who, which date, and which product, and opens a one-line cause prompt for the Team Lead." §97.5 line 8986 states the event "carries the full Section 29.4 field set … the last three supplied by the cause prompt, never inferred." Phase 3's `rqm-emit` (L4-T309) refuses a verdict document missing any of the eight keys (`queue_empty_reason`, `team_lead_blocked`, `priority_changed_recently` included). An event cannot be appended at detection time and also carry fields that do not exist yet.  
**Question:** Does the event wait for the cause prompt to be answered, or is it appended immediately and completed by a follow-up record (§97.2 line 8890: "corrections are follow-up records")? If the second, which store carries the follow-up?  
**L4 default until answered:** `rqm-detect --emit` writes the verdict document only when `cause_prompt_answered` is true. When false it prints `RQM-DETECT PENDING-CAUSE <case>` on stdout, exits `0`, writes no verdict file and appends no event. It never fabricates a cause or infers any of the three cause fields.  
**Options:**
- **A** — Hold the event until all cause-prompt fields are answered (current default)
- **B** — Emit immediately with null/empty values for the 3 late fields; complete via a follow-up record in the store L0 names

**To decide:** Add to next L0 session, say "FD-091: ready-queue-miss emit = Option A or B"

---

## PFD-018 — L4 Working Calendar Selection Rule (D-L4-P4-03)

> **RESOLVED 2026-09-08** — FD-092: L4 calendar = Option A (fixed filename records/leave/company-calendar.yaml)

**Blocks:** Rule R4 of `scheduled-availability.py` (L4-T406) only, and only in production wiring. No fixture and no test is blocked.  
**Context:** §6.4 line 451 and §52.6 line 4641 both place the company working calendar — operating timezone, standard working days, core-hours window, and the public-holiday list per location — in the leave records. `work_arrangement.public_holiday_set` is a reference to this calendar, not a second independent list. `L4-02-record-schemas.md` gives `leave.schema.json` those fields plus a calendar `version`. Neither the spec nor Phase 2 states which record in `records/leave/` is the current calendar, or how a reader selects it.  
**Question:** By what rule does a reader select the calendar-carrying leave record — a fixed filename, the highest calendar `version`, the latest effective date, or another rule L0 names?  
**L4 default until answered:** `scheduled-availability.py` takes the calendar document as a required explicit argument `--calendar <path>`. It never searches `records/leave/`, never picks a record by resemblance, and exits `3` with `SCHEDAVAIL ERROR no-calendar` when the argument is absent.  
**Options:**
- **A** — Fixed filename convention (e.g., `records/leave/company-calendar.yaml`)
- **B** — Highest calendar `version` field among records in `records/leave/`
- **C** — Latest effective date among leave records that carry a calendar body
- **D** — Another selection rule L0 names

**To decide:** Add to next L0 session, say "FD-092: working calendar selection = Option A/B/C/D"

---

## PFD-019 — L4 Capacity Profile Lane Assignment (D-L4-P4-04)

> **RESOLVED 2026-09-08** — FD-093: L4 Capacity Profile owner = Option A (L4 owns subsystem P)

**Blocks:** Nothing in this phase. This phase emits `capacity_profile_eligible`, `workload_state_eligible`, and `founder_view_eligible` as declared output fields and records truncations; it builds no Capacity Profile, no workload state, and no Founder view.  
**Context:** §97.4 line 8975 caps derived hours against "that person's scheduled availability for that day in the Capacity Profile (Section 69.2)," and line 8976 says an instrument-defect day "never enters a Capacity Profile, a workload state (Section 83) or the Founder view." The Capacity Profile, workload states, and the whole people-intelligence surface are §99.2 subsystem P (line 9203), which PARTITION.md v1 assigns to no lane — the known partition gap already escalated by other authors, alongside G, H, J, and O.  
**Question:** Which lane owns subsystem P, and therefore owns the consumer that must honour `capacity_profile_eligible`, `workload_state_eligible` and `founder_view_eligible`?  
**L4 default until answered:** `derive.py` emits the three eligibility flags as declared output fields, and `metrics/attention/HANDOFF-P.md` (L4-T413) names them for whoever receives subsystem P. L4 writes no file under any path subsystem P would own.  
**Options:**
- **A** — L4 owns Capacity Profile (it is a metric aggregate)
- **B** — L3 owns Capacity Profile (it is derived from records)
- **C** — New L6 lane for cross-cutting concerns (not in current 5-lane model)

**Recommendation:** Option A (L4) — capacity planning is closest to the metrics layer.  
**To decide:** Add to next L0 session, say "FD-093: Capacity Profile owner = Option A/B/C"

---

## PFD-020 — Registry File Physical Location (Directory-per-item vs Root-named)

> **RESOLVED 2026-09-08** — FD-100: Registry location = Option A (directory-per-item under registries/)

**Source:** REG-008 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** L1's first task and the `L1 registries/` line of `lane-paths.tsv`; the whole of `master/03` §2.5; also prerequisite of REG-044(a) / PFD-029 — that entry cannot be answered before this one

**Question:** Are `people.yaml`, `roles.yaml`, `platform.yaml`, `topology.yaml`, `exceptions.yaml`, `policies.yaml`, `tools.yaml`, and `economics.yaml` built from one-file-per-item directory trees that L1 owns (with root-named files as uncommitted build outputs), or hand-kept single files at the repo root that L0 owns? Three plan documents place them in three mutually exclusive locations.

**Option A:** Commit to directory-per-item under `registries/` (L1-owned source files; root-named files are `make` build outputs, never committed). Supply the decision in the same record that rewrites `master/06` §13's V1 exit gate to match.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply the layout ruling now so lane dispatch is unblocked.

---

## PFD-021 — Git Conventions (Merge Method, Staging, Branch Creation, Commit Message, Templates)

> **RESOLVED 2026-09-08** — FD-101: Git conventions = Option A (master/02 + master/09 §5.1)

**Source:** REG-012 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** Every lane's git preamble and postamble across all 54 lane files; `L0-03-merge-train.md` step 4 (`--no-ff`); every STOP rule in every lane file (each resolves to a blocker template that must exist); `manual/00` §7 (the first file every AI developer reads)

**Question:** For the five git conventions each stated two or three incompatible ways — merge method, staging command, branch creation, commit message format, and blocker template location — which document is authoritative for each? `master/02` and `master/09` contradict each other on all five; `manual/00` §7 contradicts `master/02` on two.

**Option A:** State the five rulings explicitly: merge method and staging and branch creation follow `master/02`; commit message follows `master/09` §5.1; canonical template is `docs/escalation/BLOCKER.md`. Reissue `manual/00` §7 in the same record. Also confirm that `master/09` §5.1's commit-msg hook must be moved into lane-guard CI (it is currently local and uncommitted — not a control).
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal rulings now so lane dispatch is unblocked.

---

## PFD-022 — Branch-Protection Mechanism and Phase-0 Required-Check List

> **RESOLVED 2026-09-08** — FD-102: Branch protection = Option A (rulesets-only, empty Phase-0 check list)

**Source:** REG-013 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** Phase 0 exit: `L0-00-T01`'s STOP criterion on `main`, `master/00` EC-3, `master/05` `L0P0-E4` and E5, `L5-T07`; without the empty-list ruling the first L2 pull request cannot merge and the build deadlocks at cycle 1

**Question:** Rulesets, classic branch protection, or both — and is the Phase-0 required-check list on every repository empty? `master/02` §10 chooses rulesets with `required_approving_review_count: 0`; `master/03` §1.5 chooses classic protection with `required_approving_review_count: 1`. `master/02` §10.1 seeds `{"context": "lane-guard"}` from day one; `master/00` EC-3 and `master/05` `L0P0-E4` require the list to be length 0. The four cannot all hold.

**Option A:** State the mechanism choice (rulesets-only is the only option that satisfies D89 and D107's empty-bypass-actor property) and confirm the Phase-0 required-check list on every repository is empty — `lane-guard` is added only on the day that check first reports a run.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-023 — Unowned-Path Lane Assignment (Sixteen Paths, Fail-Closed)

> **RESOLVED 2026-09-08** — FD-103: Unowned paths = Option A (all 16 assigned in one commit)

**Source:** REG-017 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `L1-101`; `L2-T700`/AT-024 fleet half; `L3-P3-T06` and `T10`; `L0-07` `OT-INTAKE` and `OT-P4` for all eight products; `master/08`'s entire generator set; gates Ph0 through Ph4 plus G2 and G3. Sixteen unscheduled mid-build stalls at times L0 did not choose if left unresolved.

**Question:** Sixteen named files and directories fall outside every lane's OWNS list (the guard is fail-closed — any PR touching them resolves `UNOWNED` and fails). Each must be assigned before the first lane task that needs it. Assign them all now in one commit, park them on L0, or let each stall a lane mid-build?

**Option A:** Assign each of the 16 paths to its nearest lane by dependency and add all paths to `lane-paths.tsv`, CODEOWNERS, and the manifest in one versioned re-freeze commit with one decision record. (Rows b, h, and j follow from REG-001 / FD-002 and should be transcribed from it rather than re-decided.)
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal lane assignments now so lane dispatch is unblocked.

---

## PFD-024 — Record Write Interface, Signing Identity, and Hand-Edit Control

> **RESOLVED 2026-09-08** — FD-104: Record write = Option A (REST API + installation token)

**Source:** REG-019 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** Phase 1; `L2-T514`, `L2-T515`, and every workflow that writes a record (charter DoD-14, DoD-15); `L4-T313`, `L4-T314`; §97.2 makes the deployment-record and event writes required, failing steps — a guessed interface makes every deploy fail

**Question:** Which credential writes records (REST Contents API with installation token, or a dedicated GPG/SSH key), how are those commits signed to satisfy D107, and what stops a person hand-editing a record without review given that §40.1/D89 gives the records repository no protection rules? Feeds REG-026/PFD-025 and REG-044/PFD-029.

**Option A:** Commit to (b) REST Contents API with installation token (GitHub signs with web-flow key; commit shows Verified as the App's bot identity) and (c) a required status check `validate-human-record.sh` as the hand-edit control. Supply the records-writer App slug, target repository slug, and the record/event schema paths for `records/deployments/`, `records/uat/`, `records/restore-tests/`, `records/eval/`, and `events/`.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-025 — Reconciler Identity: GitHub App vs Fine-Grained PAT

> **RESOLVED 2026-09-08** — FD-105: Reconciler = Option A (GitHub App installation token)

**Source:** REG-026 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `L3-P5-06` (AT-110 credential-bounds probe), `L3-P5-07`, `L3-03-T06` and `T10`, `L3-04-T02`. Also settles the `expected_app_slug` key REG-025 needs — REG-025 cannot be fully closed before this one. Reverse cost: EXPENSIVE (credential change rewrites token acquisition in all affected L3 tasks).

**Question:** Does the most powerful automated identity in the estate run as a GitHub App installation token, or as a fine-grained PAT bound to a human account? §40.1 permits either, but D80 prefers Apps and a PAT bound to a human Code Owner collapses both §40.1 and §11.3 at once.

**Option A:** Commit to a GitHub App installation token. Ratify the interim anchor (`derived/anchors/records-head.yaml`, allowlist `[derived/**]`) and name the org login for `--live` runs. Supply the App name and slug.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-026 — Seeded Canary: Registry, Location, and Label

> **RESOLVED 2026-09-08** — FD-106: Seeded canary = people.yaml/_canary/__CANARY__

**Source:** REG-028 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** AT-102 (canary detection); drift-check gate arming; pairs with REG-024(c)/PFD-024 (one decides the canary's drift class, this decides what the canary is). Note: `topology.yaml` was the prior candidate but appears in no CMP-01…CMP-19 comparator row — a canary there is never found and AT-102 silently fails.

**Question:** The canary must be a labelled row in a low-consequence registry that a frozen comparator actually reads. Which registry file does a CMP-01…CMP-19 comparator read, which field within it carries the canary row, and what is the exact label value to seed there?

**Option A:** Name the specific registry file (from the set that CMP-01…CMP-19 comparators actually read), the field name, and the exact canary label value. The recommendation shape is one labelled row in a low-consequence registry — only L0 can name the exact registry and label.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-027 — Security, Licence, and SBOM Scanner Tool Selection

> **RESOLVED 2026-09-08** — FD-107: Security/SBOM = Trivy + Syft + spdx-json

**Source:** REG-030 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `L2-T600`-series security-scan tasks; the SBOM generation step; every gate that reads the SBOM output. Binding constraint is invariant 83 (free, self-hosted, or flat per-person; no metered tooling) — commercial scanners are ruled out. SBOM format is already fixed: `protocol/08` CP-0603 hard-codes `--require-format spdx-json`.

**Question:** Which specific free, open-source scanner tools satisfy invariant 83 for security scanning, licence checking, and SBOM generation in V1 — and what are their pinned sha256 image digests? No document names any tool; this is a genuine spend and toolchain decision only L0 can make.

**Option A:** Confirm the tool selection (recommended: Trivy for security ×2 jobs, Syft for SBOM, `spdx-json` output format) and supply the three sha256 digests for the pinned container images so invariant 85 is satisfied.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-028 — Five Orphan-Detection Input Surfaces

> **RESOLVED 2026-09-08** — FD-108: Orphan surfaces = 5 defaults accepted (see contracts/orphans/decisions.yaml)

**Source:** REG-039 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** Nine L3 tasks at Ph3: `L3-05-T10`…`T13`, `T14`, `T17`, `T18`, `T27`, `T26`. Answering fewer than all five surfaces unblocks nothing — each blocked task depends on a different row. Note: this is five decisions under one REG id; consider splitting into REG-039a…e before the sitting.

**Question:** The orphan detector needs five things named: (a) the asset list path and its field names, (b) which delegation types from §10.1's 17-row table get the 14-day expiry warning, (c) where the board snapshot lives, (d) where the open-work snapshot lives, and (e) which field in §21.1's commitments block says who owns a customer commitment. Name all five, or drop the checks that need them (which kills two Blocking orphan types)?

**Option A:** Name each of the five surfaces and publish them as `contracts/orphans/decisions.yaml`. Row (b)'s defensible default: every §10.1 type whose "Expires cleanly" column is not "Only by reassignment". Rows (c) and (d) need no new lane assignment — PARTITION v1 already assigns N and I to L4 and Q to L5.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-029 — Bootstrap Exception Write Path and Gate 1 Compensating Control

> **RESOLVED 2026-09-08** — FD-109: Bootstrap exception path = registries/exceptions/<id>/exception.yaml

**Source:** REG-044 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** Gate 1 compensating-control authoring in `exceptions.yaml`; L1 bootstrap-exception tasks. Downstream of PFD-020 (REG-008) — cannot be fully answered before REG-008 is decided. If REG-008 lands on A (directory-per-item), then REG-044(a) = C; if REG-008 lands on B or C, then REG-044(a) = A. Option B is never correct (B alone amends the frozen partition).

**Question:** Which path and format does L1 use to write bootstrap exceptions (the answer is forced by PFD-020/REG-008), and which §95.3 binding-in-bootstrap controls are in force for Gate 1 led by the §26.4 authority-delta gate?

**Option A:** Confirm the bootstrap exception write path (after answering PFD-020) and name the §95.3 Gate 1 compensating controls in the same decision record. Supply these literals after REG-008 is closed.
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — answer REG-008/PFD-020 first, then supply the forced exception-path and the §95.3 control list in the same sitting so lane dispatch is unblocked.

---

## PFD-030 — Build Start Date, Eight Product Names, and Floor Obligation

> **RESOLVED 2026-09-08** — FD-110: Build start = 2026-09-08; products = Product-1..8; S19 rides F9

**Source:** REG-048 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `L0-07-T02`, `T04` (the date resolver — the only writer of resolved dates), `T09`; every onboarding deadline; the floor burn-down denominator; the eight `facts.tsv` files — 24 blocking fields (8 slots × 3 ordering keys) that today emit `RANK-BLOCKED`. Two floor rows are hard AI-safety gates: no AI session opens a repository until S10 and S19 pass. Reverse cost: MODERATE — being wrong on the date re-dates every bootstrap expiry in the estate.

**Question:** What calendar date does everything count from? What are your eight products called and in what criticality order (reliability criticality, then business criticality, then cheapest onboarding)? Is the customer-data check S19 a tenth universal-floor obligation or does it ride F9? (§96.6 enumerates the nine floor items literally; S19 is not among them — the ambiguity traces to a D113-removed duplicate row.)

**Option A:** Supply three literal values: (a) the build start date, (b) the eight product names in criticality order, (c) explicit statement on S19 — recommended B (S19 rides F9; denominator stays 72).
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-031 — Board Layout, Scorecard Drop Magnitude, and Estimate Exemption

> **RESOLVED 2026-09-08** — FD-111: Board = org-level Project; scorecard ≥0.5/30d; exempt=[normal,spike,incident,debt-remediation]

**Source:** REG-056 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `L4-T500`-series board-configuration tasks; Scorecard alert threshold wiring; the estimate-gate CI check. Note: §99.5's Boards bullet already makes the single org-level Project the default, so no vendor choice remains for item (a) — only items (b) and (c) require a literal value from L0.

**Question:** Three rulings in one entry: (a) one org-level Project with a product field, or per-product boards? (b) What minimum Scorecard drop magnitude (vs previous scan, over what window) triggers an alert? (c) Which item classes are exempt from estimate requirements? Item (b) is a calibrated number only L0 can set — no document states it.

**Option A:** State the three literal values: (a) one org-level Project with a product field (forced by §99.5); (b) supply the Scorecard drop threshold and window (recommended: ≥ 0.5 vs previous scan, 30-day window — this is a calibrated number L0 must supply); (c) exempt item classes list (recommended: `[normal, spike, incident, debt-remediation]`).
**Option B:** Defer until first execution sprint begins.

**Recommendation:** A — supply literal values now so lane dispatch is unblocked.

---

## PFD-032 — DevLake V1 Inclusion Decision

> **RESOLVED 2026-09-08** — FD-112: DevLake deferred; L5 to revert compose.shared.yml

**Source:** REG-058 (from `_DECISION_DOCKET.md`)
**Raised:** Session 13 audit
**Blocks:** `contracts/v1-scope.yaml` (the V1 scope boundary record); four signals (SIG-04, SIG-07, SIG-08, SIG-40) that name DevLake as their source; `L5-04-T03` has already written DevLake into `ops-vm/stack/compose.shared.yml` — L5 has built the deferred option while the decision was open. An explicit ruling is needed to either ratify or revert that implementation.

**Question:** Is DevLake installed and connected in V1, or deferred? D77's arming discipline warns that the day DevLake connects it produces "a wall of amber, produced by the instrument rather than by the system." Four (not ten) V1-adjacent signals name DevLake as their source. L5 has already partially implemented it without a decision record.

**Option A:** State the V1 scope ruling explicitly — defer DevLake and record it in `contracts/v1-scope.yaml`; simultaneously direct L5 to revert `ops-vm/stack/compose.shared.yml` to remove the premature inclusion. The four affected signals (SIG-04, SIG-07, SIG-08, SIG-40) are recorded as deferred with a dated trigger.
**Option B:** Defer the decision itself until first execution sprint begins (note: L5 has already shipped a partial implementation that will conflict with a later deferral ruling).

**Recommendation:** A — supply the explicit V1 scope ruling now so lane dispatch is unblocked and the L5 partial implementation is either ratified or cleanly reverted.
