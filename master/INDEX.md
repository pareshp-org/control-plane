# INDEX — the implementation document set

**What this is.** The navigational map of `Code/implementation/`. It names every file in the set, states what each is for and who reads it, gives the reading order for each of the three audiences, and lists the items that are unresolved.

**What this is not.** Authority. This file settles nothing. Where it disagrees with `PARTITION.md`, `PARTITION.md` wins; where it disagrees with a document it indexes, that document wins on its own subject and this index is defective.

**Authority order** (from `master/00-MASTER-PLAN.md` §0, restated so it is visible from the front door):

| Rank | Document | Settles |
|---|---|---|
| 1 | `Research/MultiProduct_MasterSpec_v4.0.md` | What the system must be and do. All `§`, `AT-`, invariant, `SIG-` and `D` identifiers are cited from here and nowhere else |
| 2 | `Code/implementation/PARTITION.md` | Path ownership, branch model, merge train, AI-developer profile. **FROZEN** |
| 3 | `master/00-MASTER-PLAN.md` | Scope, tiers, calendar, entry criteria, definition of done |
| 4 | `master/`, `protocol/`, `manual/` | Process detail |
| 5 | `lanes/*` | Task-level instructions for one lane |

**Binding rule for every lane developer:** you may not resolve a conflict between two of these documents yourself. Stop, open a blocker issue titled `BLOCKER: authority conflict <doc-A> vs <doc-B>`, and wait for L0. Every item in **§7 OPEN ITEMS** is already known to L0 and is not yours to resolve.

**Scale, as counted.** **111 files (94 markdown plan files + 17 Session 15 implementation artifacts), 172,259 lines** in the four core directories, per the most recent integrity sweep. Current file counts run higher — verified against `ls lanes/*.md protocol/*.md manual/*.md master/*.md` on 2026-09-09:

| Directory | Files | Lines |
|---|---|---|
| `master/` | 11 (incl. this file) | 9,798 |
| `lanes/` | 66 — 54 core plan files + 12 post-freeze additions (6 `CONCORDANCE.md`, 4 `_98-DEEP-REVIEW.md`, 2 L4 metric-register files; see §5.1, §5.5) | 138,026 (core sweep total; the 12 additions are not yet folded in) |
| `manual/` | 14 (the §4 preamble already said fourteen; this row was stale and is now corrected to match) | 13,262 |
| `protocol/` | 16 — 13 numbered `00`–`11`/`99` + `_98-DEEP-REVIEW.md` + two new files, `00-dispatch-model.md` and `README.md` (see §3) | 11,173 (+88 lines across the two new files, not yet folded in) |

Line counts above are from the most recent integrity sweep (`_INTEGRITY.md` §A). Files added after that sweep — the `CONCORDANCE`, `_98-DEEP-REVIEW`, `cross/` and `review-harvest/` sets, plus `protocol/00-dispatch-model.md`, `protocol/README.md`, `lanes/L0-CONCORDANCE.md`, `lanes/L4-03-metric-register.md` and `lanes/L4-04-metric-register.md` — are catalogued in §3, §5.1, §5.5 and §§5.7–5.8 without measured line counts folded into the sweep total; re-derive with `wc -l`.

**Git state, as counted.** 161 commits on `master` (`git log --oneline | wc -l`, run 2026-09-15), HEAD `fb21ed7` — "fix(protocol/05-merge-gate): repair mechanical defects in merge gate doc". (This set is under active parallel edit; re-run the command before trusting this figure.)

No one reads all of it. The reading orders in §6 are the whole point of this file.

---

## 1. Root — outside the four indexed directories

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `PARTITION.md` | 47 | The FROZEN partition contract: two repositories, the five lanes' exclusive path ownership, the five anti-conflict rules, the branch and merge model, the AI-developer profile. Every other file in the set conforms to it and none redesigns it | **Everyone, first, always** |
| `_INTEGRITY.md` | — | The current integrity sweep of the whole set. Verdict per directory, open-item audit, and the §B refutation of the former INDEX O-1…O-6 false-blocker set. Supersedes `_INTEGRITY.superseded-2026-09-02.md` | L0 |
| `_DECISION_DOCKET.md` | — | The decision docket: all 60 `REG-` entries analysed, options evaluated, and recommendations for each. Includes §3C register-wide defects and §4 consequential edit list. Input to `_DECISION_SIGNOFF.md` | L0 |
| `_DECISION_SIGNOFF.md` | — | The Founder's decision signoff: options chosen for every `REG-` entry, including FD-001–FD-015. Supersedes pending status in `lanes/L0-04-decisions-register.md` for every closed entry. The record of closed decisions | L0 |
| `_FOUNDER_DECISIONS.md` | — | FD-001 through FD-015, as individually signed records with rationale. FD-013 froze the `contracts/**` surface (see §7.2 G-5, G-10 and §7.3 R-9) | L0; a lane reads its FD references |
| `_RESIDUE.md` | — | Roll-up of the five lane concordances, produced under FD-004. Measures how many planned task ids are unbuilt as of 2026-09-02. Read §4 before citing §1 or §2 figures | L0 |
| `RESUME.md` | — | The L0 session resume document: current state of Phase 0 work, last-touched task, and the first command to run on return. Dated Session 14 (2026-09-08); `SESSION-15-STATUS.md` below is a day newer and may now supersede it — not reconciled here | L0 |
| `_DAMAGE.md` | 13 | Historical truncation report from an earlier sweep. All nine files it names have since been repaired; kept as a record, not a work list | L0 |
| `_STATUS.txt` | 3 | Stale one-line counter. Superseded by `_INTEGRITY.md` and by this file | — |
| `RESUME.superseded-2026-09-02.md` | — | Superseded RESUME; kept as a historical record | — |
| `_INTEGRITY.superseded-2026-09-02.md` | — | Integrity sweep 3 report; superseded by `_INTEGRITY.md` | — |
| `.github/CODEOWNERS` | 42 | GitHub code ownership — maps lane paths to lane-team reviewers; generated by L0 from `lane-paths.tsv` (FD-109). Lives under `.github/`, not at the repository root | L0; GitHub |
| `facts.tsv` | — | Product facts table — eight products, build date, criticality order, floor obligation; placeholder names to be replaced by Founder (FD-030) | L0 |
| `README.md` | 21 | Repo-root orientation: quick start, directory structure, pointer to this file for the full inventory | Everyone, first |
| `CONTRIBUTING.md` | 44 | The 5-lane model at a glance — lane names, owners, responsibilities — and where to find every architectural decision | Everyone |
| `FOUNDER-DECISION-PACKET.md` | 195 | Compressed pointer packet into the `protocol/_98-DEEP-REVIEW.md` defects still needing a Founder judgment call, one sitting's worth of open picks | Founder (L0) |
| `PENDING_FOUNDER_DECISIONS.md` | 660 | The open-PFD tracker: decisions the Founder alone can choose among, sourced from the lane coherence reviews; each closed PFD records which FD resolved it | Founder (L0) |
| `PHASE-0-EXECUTION.md` | 95 | The literal Phase 0 run guide: prerequisites, GitHub PAT scopes, org and repo names, the step-by-step commands | L0 |
| `SESSION-15-STATUS.md` | 168 | Session 15 status snapshot (2026-09-09): current-state summary for whoever picks the session up next, with live-verified numbers and the commands to re-run them | L0 |

**Note on `O-0…O-12` in `master/02`.** That document's §6 uses `O-0` through `O-12` as numbered command steps for lane developers (e.g., "Run O-1 to clone"). That step-numbering space is entirely distinct from the C-/G-/R- open-item ids in this file's §7. `cross/03-id-collisions.md` documents the naming collision.

---

## 2. `master/` — programme level, L0-owned

Eleven files. L0 reads all of them; a lane reads the four marked.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `master/00-MASTER-PLAN.md` | 719 | The front door. Authority order, scope, the three tiers, the honest calendar, entry criteria EC-1…EC-15, definition of done, and a document map | L0; every reader second |
| `master/01-lane-architecture.md` | 705 | Why each lane boundary sits where it does: the lane map, subsystem letters A–R, exclusive path ownership row by row, contract consumption and publication, inter-lane dependencies, and the `C1`–`C18` contract surfaces | L0; a lane before its first task |
| `master/02-branch-merge-model.md` | 1,062 | Git topology, branch lifetimes, the ordered merge train, rebase discipline, merge authority, the daily cycle, behind-lane recovery, and the literal ruleset/branch-protection configuration. Its §6 contains steps `O-0`…`O-12` — numbered command steps, distinct from this file's C-/G-/R- open-item ids | L0 executes; **lane reads §6** |
| `master/03-conflict-prevention.md` | 1,276 | The repository machinery that makes five simultaneous lane branches structurally unable to collide: ownership map, longest-match resolution, the append-only map, the guard rules R1–R5, the CCR procedure | L0 installs; a lane reads §1 before its first branch |
| `master/04-phase-map.md` | 410 | One timeline for the whole build. The two clocks (Build track `BT-0`…`BT-4`, Onboarding track `OT-P4`…`OT-P7`), sync points `S0`–`S4`, what genuinely parallelises and what only appears to | L0 sequences; **a lane reads only to know its phase and its gate** |
| `master/05-entry-exit-criteria.md` | 1,622 | For every phase in every lane: what must be true to start, what must be true to finish, and the exact command that proves it. Every exit criterion is a command printing `PASS <id>` or `FAIL <id>` | L0 for `L0-P0`/`G-INT`/`G-F*`; **a lane for its own phase section** |
| `master/06-v1-scope.md` | 572 | What the first release contains and what it does not, with the trigger that moves each deferred item into a later release. Every scope question is a table lookup | L0 and all five lanes |
| `master/07-risk-register.md` | 691 | Risks to *building* the system with five parallel agents (not risks to the running system). Two registers, scored, each row with a detection command and a lane duty | L0 owns every row; **a lane runs only its "lane duty" column and §6 STOP rules** |
| `master/08-progress-tracking.md` | 1,325 | Status derived from git, never self-reported. The ledger L0 authors, the burn-down, and the report generator | **L0 first**; a lane reads §11 only |
| `master/09-glossary-and-conventions.md` | 1,470 | The prescriptive style contract: identifiers, branch naming, commit format, PR format, blockers and CCRs, file/schema naming, YAML, JSON Schema, tests and fixtures | Every lane developer and L0 |
| `master/INDEX.md` | *this file* | The navigational map and the open-items list | Everyone |

---

## 3. `protocol/` — how the five lanes coexist and how the work is proven

Sixteen files (thirteen numbered `00`–`11` and `99`, plus `_98-DEEP-REVIEW.md`, `00-dispatch-model.md`, and `README.md`). L0-owned; every lane reads the ones its gates run. Note: `00-dispatch-model.md` shares the numeric slot `00` with `00-test-strategy.md` — both exist as of 2026-09-09; the collision is unresolved (same shape of defect as the L4 slot collisions in §5.5).

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `protocol/00-test-strategy.md` | 532 | The T0–T4 verification pyramid: what is tested, where, when, who owns it and what it blocks. Fixes the exit-code contract and the negative-test doctrine | L0 and all five lanes |
| `protocol/00-dispatch-model.md` | 81 | Canonical answers to the dispatch-gate Q1–Q3 (task delivery format, task-id/branch grammar, execution model) per FD-071–073. Also flags an open discrepancy (FD-073 note): the canonical task-id grammar `L<N>-<FF>-<NN>` does not match `L0-00-charter.md`'s existing `L<N>-<FF>-T<NN>` usage, and no id-format check may run in CI until L0 resolves it | L0; every lane before its first task |
| `protocol/README.md` | 7 | One-paragraph orientation for the directory: what `protocol/` is for, and the rule not to duplicate its content in lane files | Anyone new to the directory |
| `protocol/01-contract-tests.md` | 658 | The cross-lane tests that catch two lanes diverging. Governs `contracts/**`, `contracts/fixtures/**` and `contracts/harness/**` — written by L0 in Phase 0 and frozen | L0 authors; lanes run |
| `protocol/02-acceptance-mapping.md` | 590 | Maps all 110 spec acceptance tests AT-001…AT-110 to the lane that implements them, the phase each can first run, and whether it is automatable | L0; a lane checks the AT ids it owns |
| `protocol/03-invariant-tests.md` | 1,331 | The enforcement suite for the 111 spec invariants: mechanical/policy classification, the live check or AT id behind each, and CI that fails when an invariant carries neither | L0; lanes implementing an enforcing check |
| `protocol/04-negative-tests.md` | 1,595 | The negative-test catalogue. Every test performs a forbidden action and asserts the system refused. Built from AT-, invariant and EC- identifiers | L0; every lane, per gate |
| `protocol/05-merge-gate.md` | 347 | The two gates. GATE A (`LG-01`…`LG-12`) admits a lane PR into `integration`; GATE B (`IG-01`…`IG-12`) admits `integration` into `main` | L0 runs both; a lane must pass GATE A |
| `protocol/06-integration-cycle.md` | 651 | The daily cycle: how the merge train is opened, run in order, gated and closed | **L0**; a lane reads what a rebase directive obliges |
| `protocol/07-rollback.md` | 1,164 | Recovery of the *build* — not production rollback. Includes the proof requirement that an unexecuted rollback procedure is a hypothesis | L0 for anything touching `integration`/`main`; **a lane only for §R3 and §R5.3** |
| `protocol/08-smoke-and-e2e.md` | 1,206 | The end-to-end run that proves the five lanes built the *same* system: one pilot product from nothing through Gate 1, Gate 2, a real digest, staging, verification, production approval and deploy | L0, at every `integration` → `main` promotion and once as the V1 exit gate |
| `protocol/09-fixtures.md` | 701 | The shared test corpus, deliberately containing wrong data that gates are required to report. Defines `make fixtures-all` and the `FG-1`…`FG-5` meta-gates | L0 authors; every lane's gate runs against it |
| `protocol/10-ci-pipeline.md` | 1,072 | The workflows that run on `lane/N/*`, `integration` and `main` **during the build** — explicitly distinguished from Lane 2's reusable workflow library for the product estate | L0; L2 must not conflate the two |
| `protocol/11-definition-of-done.md` | 1,113 | Done at every level: task, phase, lane, V1, Foundation, programme. Each level's proof is a command | L0 and every lane |
| `protocol/99-WALKTHROUGH.md` | 643 | Diagnostic, not normative. Walks files `00`–`11` end to end on paper and records where the protocol falls through | L0 only |
| `protocol/_98-DEEP-REVIEW.md` | — | Deep adversarial review of the protocol files (wave 2). Findings, not normative | L0 |

---

## 4. `manual/` — the AI developer's operating manual

Fourteen files — `00`–`11`, all present, plus the `99` hardening review and `_98-DEEP-REVIEW.md`. This is what a lane agent is actually given.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `manual/00-README-FOR-AI-DEVELOPERS.md` | 283 | The two-minute front card: five lanes, your lane owns fixed paths, you decide nothing, every task ends in a self-verify command you must actually run | **Every lane agent, before its first action** |
| `manual/01-lane-system-prompts.md` | 1,988 | Five complete, verbatim copy-pasteable system prompts — one per lane. A production artefact, not examples | **The operator** who starts a lane session |
| `manual/02-task-execution-protocol.md` | 1,127 | The twelve-step loop, run once per task, in order, without skipping. Opens with the six ways agents fail it | Every lane agent, per task |
| `manual/03-guardrails-and-stop-rules.md` | 739 | The STOP conditions and the five things you do when one fires. Binding, and it overrides your task card | Every lane agent |
| `manual/04-anti-hallucination.md` | 905 | Six named failure modes (invented path, invented citation, unrun test, …) and the verification gates `V1`…`V6` that block each | Every lane agent |
| `manual/05-git-workflow.md` | 1,291 | Every git command you will ever run here, in order, with expected output — plus §14, the forbidden commands | Every lane agent |
| `manual/06-pr-and-review.md` | 927 | How a PR is opened and what the body must contain; the four distinct events (Approve / Merge / Approve-for-production / Deploy); why you never merge and never approve | Lane agent and reviewer |
| `manual/07-worked-example.md` | 1,528 | One real Lane 1 task end to end — the `people.yaml` schema — nothing elided, every command literal, every captured output real | A lane agent facing its first task of that shape |
| `manual/08-failure-playbook.md` | 826 | What to do when something went wrong: orient, diagnose, and the STOP-AND-REPLAN signals. Three laws — do not fix what you do not own, do not guess, do not report what you did not run | A lane agent, only once something broke |
| `manual/09-cost-and-context-discipline.md` | 530 | What you may read, and when to stop reading | Every lane agent |
| `manual/10-quality-bar.md` | 829 | The eight gates of `DONE`, each with the output you must paste. `BLOCKED` is the only alternative | Every lane agent, before reporting |
| `manual/11-onboarding-a-new-agent.md` | 1,204 | The lane-handover procedure: incoming agent, outgoing agent, and L0 running the swap. Also the standing refusal of a sixth agent | Incoming/outgoing agents and L0 |
| `manual/99-HARDENING.md` | 1,438 | Adversarial hardening review of `manual/00`–`manual/11` and `PARTITION.md`: `A1`–`A20` on the five lane system prompts, `B1`–`B15` cross-file contradictions, `C1`–`C13` broken commands, red-team walkthrough, `M1`–`M18` missing controls. **Findings, not normative** | L0 |
| `manual/_98-DEEP-REVIEW.md` | — | Deep adversarial review of the manual files (wave 2). Findings, not normative | L0 |

---

## 5. `lanes/` — the task packs

**Core task packs: fifty-four files** — L0 has nine, each of L1–L5 has nine (`00` charter → `07` runbook, plus `99` coherence review). **A lane developer opens exactly one lane's files and never another's.** The `99` reviews are audit artifacts for L0, not plan documents.

**Post-FD-004 additions:** every lane, L0 included, now has one `CONCORDANCE.md` (tracking bodied vs. missing task ids; L0's own was added Session 13 — see §5.1); L1, L2, L4 and L5 each also have one `_98-DEEP-REVIEW.md` (a second adversarial review wave; L3 does not). These are L0 reference documents; a lane developer does not read them. **Sixty-six files total in `lanes/` as of 2026-09-09** (`ls lanes/*.md | wc -l`): the 54 core packs, 6 `CONCORDANCE.md`, 4 `_98-DEEP-REVIEW.md`, and two further L4 metric-register files that postdate the original 54 (§5.5).

**Lane coherence review status:** all six `L*-99-review.md` files formally return BLOCKED. However, `L1-99` and `L5-99` block on body-count measurements that `_INTEGRITY.md` §B refutes as false (all bodies are present). The authoritative residue count is in `_RESIDUE.md` §1.

### 5.1 L0 — Integrator (executed by the human lead, except `L0-07`)

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L0-00-charter.md` | 1,352 | The integrator's standing charter: what L0 owns, what L0 alone decides (`L0D-*`), the daily rhythm, the freeze definition. 9 tasks | L0; **lanes read §5–§7 only** |
| `lanes/L0-01-phase-0-contracts.md` | 7,426 | Phase 0, which runs before any lane starts: authoring and freezing `contracts/**`, the stubs and fixtures each lane codes against, and the CCR SLA. 23 tasks, ending at `PHASE-0-COMPLETE` | L0 only |
| `lanes/L0-02-lane-guard.md` | 1,794 | The production lane guard: machine-readable ownership manifest, guard engine, the Actions workflow that makes it binding on every lane PR, the CODEOWNERS generator, the exact error text an agent sees, the override procedure. 9 tasks | L0 builds; lanes see only its output |
| `lanes/L0-03-merge-train.md` | 1,685 | The merge train as an operational procedure: literal commands, failure branches, records. 12 tasks | L0 runs it; **lanes read §4, §6, §7, §10** |
| `lanes/L0-04-decisions-register.md` | 3,162 | The single decision register: 62 `REG-` ids consolidating every `L0 DECISION REQUIRED` block raised anywhere in the set, with options, status and resolution. 8 tasks | L0 maintains; **a lane looks up the `REG-` id its blocker cites** |
| `lanes/L0-05-integration-gate.md` | 3,781 | GATE B built: the executable form of `protocol/05` §4 (`IG-01`…`IG-12`) and `protocol/00` §5 (T3). 15 tasks | L0 only; a lane reads §2 and §9 |
| `lanes/L0-06-bootstrap-mode.md` | 1,959 | Operating while the org is one person: opening and closing bootstrap exceptions with expiry, owner and deactivation trigger. 12 tasks | L0 as Founder; **a lane reads §3** |
| `lanes/L0-07-onboarding-track.md` | 3,201 | The onboarding track's control-plane machinery inside L0's own paths — floor checklist, intake taxonomy, sequencing, relative-date resolver, DevOps serialiser, QA clock. The one L0 file executed by an AI developer. 15 tasks | An AI developer; human steps are marked |
| `lanes/L0-99-review.md` | 516 | Coherence review of L0's eight plan files (19,450 lines, 103 tasks). Verdict **BLOCKED** — seven defects, five mechanical dead ends | L0 |
| `lanes/L0-CONCORDANCE.md` | 41 | Session 13 concordance/log — L0 has no single tasks file, so this tracks protocol-file additions, FD-071–081 closure, Phase 0 completion status and file-count housekeeping rather than a task-id mapping | L0 |

### 5.2 L1 — Registries & Contracts · subsystems A, B · branch `lane/1/*` · merge train **1st**

Owns `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L1-00-charter.md` | 851 | Lane mandate, path ownership, subsystem mapping, consumption/publication contracts, lane DoD, DECISION REQUIRED block | The L1 agent, in full |
| `lanes/L1-01-repo-skeleton.md` | 2,004 | Phase 1 — the `control-plane` repository skeleton, effective dating and append-only discipline from day one. 13 tasks | The L1 agent |
| `lanes/L1-02-schemas.md` | 4,968 | Phase 2 — one JSON Schema per registry or contract, plus fixture pairs and the schema-check harness. No business logic. 19 tasks | The L1 agent |
| `lanes/L1-03-validators.md` | 2,177 | Phase 3 — the validator suite: referential integrity, date arithmetic, the rule manifest and the CLI. 21 tasks | The L1 agent |
| `lanes/L1-04-ci-gate-engine.md` | 1,788 | Phase 4 — the CI gate engine (subsystem B), the gate-rule schema and the canary registry. 9 tasks | The L1 agent |
| `lanes/L1-05-tasks.md` | 20,001 | The lane's complete ordered atomic task list — **157 tasks, all bodied** (`L1-001`…`L1-1001`: the original 61 core tasks plus 96 absorbed tasks). File is 20,001 lines and ends `**END OF LANE 1 TASK LIST — 157 tasks, L1-001 through L1-1001.**` (grew from 6,132 lines/61 tasks after commit `7679902` reconstructed 69 previously-truncated task bodies — see §7.5 and the dated note below) | The L1 agent |
| `lanes/L1-06-tests.md` | 2,303 | The lane test strategy; everything it creates lives under `validators/registry/tests/**`. 15 tasks | The L1 agent |
| `lanes/L1-07-runbook.md` | 1,172 | The daily runbook — a script, not advice; every branch point ends in a command or a STOP. 14 `L1-RB-*` procedures | The L1 agent, daily |
| `lanes/L1-99-review.md` | 558 | Coherence review. Verdict **BLOCKED** — five mutually exclusive plans for one subsystem. **Its body-count finding is false** (see §7.5; all 61 bodies present) | L0 |
| `lanes/L1-CONCORDANCE.md` | — | Post-FD-004 concordance: planned ids vs. bodied ids. Authoritative residue count for L1 | L0 |
| `lanes/L1-98-DEEP-REVIEW.md` | — | Wave-2 adversarial review of L1 files. Findings, not normative | L0 |

### 5.3 L2 — Pipeline & Evidence · subsystems E, F · branch `lane/2/*` · merge train **3rd**

Owns `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L2-00-charter.md` | 1,001 | Lane mandate, scope, STOP rules `S1`–`S5`, blocker template, task-id ranges | The L2 agent, in full |
| `lanes/L2-01-reusable-workflows.md` | 2,537 | Phase 1 — the reusable workflow library and the per-product caller stubs `create-product` scaffolds. 16 tasks | The L2 agent |
| `lanes/L2-02-digest-invariant.md` | 2,359 | Phase 2 — the digest invariant and artifact chain (spec §32), the load-bearing phase of the lane. 18 tasks | The L2 agent |
| `lanes/L2-03-production-gates.md` | 3,268 | Phase 3 — production approval and isolation: workflow-identity gate, runner isolation (D87), environment policy. 13 tasks | The L2 agent |
| `lanes/L2-04-evidence-chain.md` | 3,500 | Phase 4 — subsystem F, the evidence chain store and query; the eleven-question chain. 17 tasks (`L2-T500`–`T516`) | The L2 agent |
| `lanes/L2-05-tasks.md` | 13,526 | The lane's atomic task list — 76 rows, **all 76 bodied**; 23 of its ids are also defined in `L2-02`/`L2-04` (see C-7) | The L2 agent |
| `lanes/L2-06-tests.md` | 2,448 | The lane test strategy; everything it creates lives under `tools/evidence/**` and `.github/workflows/**`. 14 tasks | The L2 agent |
| `lanes/L2-07-runbook.md` | 1,775 | The daily runbook. 15 `L2-RB-*` procedures | The L2 agent, daily |
| `lanes/L2-99-review.md` | 358 | Coherence review. Verdict **BLOCKED** — two peer task decompositions sharing 23 ids (see C-7) | L0 |
| `lanes/L2-CONCORDANCE.md` | — | Post-FD-004 concordance: planned ids vs. bodied ids | L0 |
| `lanes/L2-98-DEEP-REVIEW.md` | — | Wave-2 adversarial review of L2 files. Findings, not normative | L0 |

### 5.4 L3 — Reconciler & Provisioning · subsystems C, D · branch `lane/3/*` · merge train **4th**

Owns `reconciler/**`, `tools/provision/**`, `validators/drift/**`. The highest-privilege code in the system; every phase file restates the detect-only-first mitigation.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L3-00-charter.md` | 1,207 | Lane mandate and the paragraph that governs every task: detect first, repair one class at a time. 6 tasks | The L3 agent, in full |
| `lanes/L3-01-diff-engine.md` | 7,850 | Phase 1 — the read-only declared-versus-actual diff engine: nineteen comparators, the finding envelope, the run record. 22 tasks. Largest file in `lanes/L3-*` (`lanes/L1-05-tasks.md` and `lanes/L2-05-tasks.md` are both larger set-wide) | The L3 agent |
| `lanes/L3-02-levels-and-repair.md` | 3,678 | Phase 2 — the five response levels and the first auto-repair classes, with the stricter-only rule enforced in code. 14 tasks | The L3 agent |
| `lanes/L3-03-canary-and-integrity.md` | 6,264 | Phase 3 — instrument integrity: the seeded canary, narrowing detection, history-rewrite detection, unscheduled-run refusal. Nothing here repairs anything. 15 tasks | The L3 agent |
| `lanes/L3-04-provisioning.md` | 2,104 | Phase 4 — subsystem D, provisioning and scaffolding (`create-product`). 18 tasks | The L3 agent |
| `lanes/L3-05-orphans.md` | 2,088 | Phase 5 — orphan and expiry detection; writes nothing outside `reconciler/`. 30 tasks | The L3 agent |
| `lanes/L3-06-tasks.md` | 4,991 | Declares itself the lane's complete ordered work list — 78 rows, all bodied, in an id scheme disjoint from every phase file (see C-8) | The L3 agent |
| `lanes/L3-07-tests-and-runbook.md` | 1,466 | The lane test harness, fixture organisation, the phase-gated live-organisation procedure, and the daily runbook. 11 tasks | The L3 agent |
| `lanes/L3-99-review.md` | 752 | Coherence review. Verdict **BLOCKED** — two complete mutually exclusive plans for the same subsystems (see C-8) | L0 |
| `lanes/L3-CONCORDANCE.md` | — | Post-FD-004 concordance: planned ids vs. bodied ids | L0 |

### 5.5 L4 — Records, Events & Metrics · subsystems I, N · branch `lane/4/*` · merge train **2nd**

Owns all of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` in `control-plane`. The only lane working across two repositories.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L4-00-charter.md` | 668 | Lane mandate, two-repo path ownership, standing rules, decisions, lane DoD. 7 tasks | The L4 agent, in full |
| `lanes/L4-01-records-repo.md` | 1,580 | Phase 1 — standing up `control-plane-records`: directory-per-item, the no-bypass ruleset (D107), commit signing, the `records-writer` App (D89). 12 tasks | The L4 agent |
| `lanes/L4-02-record-schemas.md` | 4,072 | Phase 2 — the record and event schemas and the event envelope. 25 tasks | The L4 agent |
| `lanes/L4-03-write-paths.md` | 2,489 | Phase 3 — how records get written: never edited in place, corrections are follow-up records. 16 tasks | The L4 agent |
| `lanes/L4-03-metric-register.md` | 1,131 | A second file also numbered `03` (unresolved slot collision, added Session 13, 2026-09-08): the authoritative Phase 3 (register bootstrap) and Phase 7 (declarations/§103 computations) metric-register task bodies — 21 bodies for `L4-06-tasks.md` index rows `L4-P3-06` and `L4-P7-01..20` | The L4 agent |
| `lanes/L4-04-attention-ledger.md` | 3,727 | Phase 4 — the attention ledger, its duration rule, and the metrics derived from it. 19 tasks | The L4 agent |
| `lanes/L4-04-metric-register.md` | 2,638 | A second file also numbered `04`: an earlier metric-register draft (authored 2026-09-06, task ids `L4-04-M01..M15`), marked **SUPERSEDED DRAFT** by its own header in favour of `L4-03-metric-register.md`. Kept as a historical record | L0 only |
| `lanes/L4-05-pipeline-and-boards.md` | 3,783 | Phase 5 — the ingest half of subsystem I and the board/horizon/Ready half of subsystem N. 17 tasks | The L4 agent |
| `lanes/L4-06-tasks.md` | 850 | A 117-row index-style task list: 23 rows resolve to a body in the phase files; 94 rows have no body anywhere (see C-17). Complete as an acceptance-criteria index; not executable alone | The L4 agent |
| `lanes/L4-07-tests-and-runbook.md` | 2,285 | Phase 7 — test strategy (fixture corpora, round-trip, negative, derivation tests) and the two-repository daily runbook. Each L4 instrument must prove it can fail. 14 tasks | The L4 agent |
| `lanes/L4-99-review.md` | 462 | Coherence review. Verdict **BLOCKED** — three incompatible id namespaces; the damage is in the two coordinating documents, while `L4-02`–`L4-05` are sound (see C-17) | L0 |
| `lanes/L4-CONCORDANCE.md` | — | Post-FD-004 concordance: planned ids vs. bodied ids | L0 |
| `lanes/L4-98-DEEP-REVIEW.md` | — | Wave-2 adversarial review of L4 files. Findings, not normative | L0 |

### 5.6 L5 — Access, Infra & Ops · subsystems K, L, M, Q, R · branch `lane/5/*` · merge train **5th**

Owns `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`. The widest lane.

| File | Lines | Purpose | Audience |
|---|---|---|---|
| `lanes/L5-00-charter.md` | 877 | Lane mandate, path ownership, subsystem/spec coverage map, merge-train obligations, lane DoD, and the task-authoring contract. 1 task | The L5 agent, in full |
| `lanes/L5-01-org-and-access.md` | 5,689 | Phase 1 — the GitHub organisation and access model (spec §11): org settings, Teams, branch protection, deployment branch policy, the bootstrap arming pattern. 15 tasks | The L5 agent |
| `lanes/L5-02-secrets-and-boundaries.md` | 5,323 | Phase 2 — the five secret tiers and trust boundaries (D95); every judgement value is read from a frozen L0 input or the task STOPs. 14 tasks | The L5 agent |
| `lanes/L5-03-layer-b.md` | 3,949 | Phase 3 — the Layer B split that hard-gates the People tier (spec §90.3). **13 tasks, all bodied** | The L5 agent |
| `lanes/L5-04-ops-vm.md` | 5,252 | Phase 4 — the operations VM and estate: deliberately disposable, rebuilt under four hours, never in a product's runtime path. **19 tasks, all bodied** | The L5 agent |
| `lanes/L5-05-assets-ai-notify.md` | 4,605 | Phase 5 — asset inventory and deadline watch (Q), AI runtime contract enforcement (K), notification routing (R). **17 tasks, all bodied** (K01–K04 and R01–R04 confirmed present) | The L5 agent |
| `lanes/L5-06-tasks.md` | 5,725 | The lane's complete atomic task list — **74 tasks, all bodied** (`L5-T01`…`L5-T74`; corrected 2026-09-09 from a stale 59-task/1,126-line count that predates this session — the file itself has not changed since the initial bootstrap commit `7780141`; the 2026-09-09 correction's own figure of 5,622 lines has since drifted too, corrected again here 2026-09-15). Its `L5-T*` id namespace shares no id with any L5 phase file (see C-21) | The L5 agent |
| `lanes/L5-07-tests-and-runbook.md` | 2,715 | The lane test strategy — access configuration tested negatively, Phase 1 completion checks executed for real — plus the daily runbook and the ASSISTED/HUMAN-GATED rule. **14 tasks, all bodied** | The L5 agent |
| `lanes/L5-99-review.md` | 94 | Coherence review. Verdict **BLOCKED** — five id schemes. **Its body-count finding is false** (see §7.5; all 153 L5 body ids present) | L0 |
| `lanes/L5-CONCORDANCE.md` | — | Post-FD-004 concordance: planned ids vs. bodied ids | L0 |
| `lanes/L5-98-DEEP-REVIEW.md` | — | Wave-2 adversarial review of L5 files. Findings, not normative | L0 |

### 5.7 `cross/` — cross-cutting analysis

Twelve analysis files produced by the review wave. **Findings documents, not normative plan files** — they describe defects but do not define tasks or contract surfaces. L0 reads them; lanes do not.

| File | Purpose |
|---|---|
| `cross/01-path-ownership.md` | Path-ownership audit: gaps and overlaps in `lane-paths.tsv` vs. what the plan documents claim each lane owns |
| `cross/02-task-graph.md` | Task dependency graph: unreachable tasks, dependency cycles, and phases where a required predecessor has no body |
| `cross/03-id-collisions.md` | Id-collision join: every `O-*`, `C-*`, `G-*`, `R-*`, `REG-*`, `L<n>-T*` namespace collision across the whole set. Documents the naming collision between `master/02` §6 step-numbers (`O-0`…`O-12`) and this file's open-item space |
| `cross/04-contract-coherence.md` | Contract-coherence check: whether each `contracts/**` surface cited by a lane matches what `master/01` §5 and FD-013 froze |
| `cross/05-command-integrity.md` | Command-integrity audit: commands in task bodies that reference paths, executables or environment variables that do not exist |
| `cross/06-convention-conflicts.md` | Convention-conflict inventory: all five pairs from REG-012 (merge method, staging, branch creation, commit message, templates), plus branch grammar (C-1/C-2/C-18) and phase vocabulary (C-19) |
| `cross/07-spec-coverage.md` | Spec-coverage matrix: which spec sections and AT-ids each lane covers, gaps in AT-002…AT-110 coverage, and unassigned subsystem surface |
| `cross/08-acceptance-coverage.md` | Acceptance-coverage drill: AT-ids that appear in gate files but have no implementing task body anywhere |
| `cross/09-gate-failability.md` | Gate-failability audit: gates that can only pass, per the negative-test doctrine (`protocol/00` §5) |
| `cross/10-l0-load.md` | L0-load analysis: tasks whose ASSISTED or HUMAN-GATED label makes them serial L0 work, with total-hour estimate |
| `cross/11-first-hour.md` | First-hour audit: the first command of each lane's entry document, and whether it can actually run in a clean environment |
| `cross/12-redteam.md` | Red-team walkthrough: adversarial scenario tracing an agent through one full task that silently builds the wrong thing |

### 5.8 `review-harvest/` — review harvest artifacts

Produced by the cross-cutting and wave-2 review passes. **Findings, not normative.** L0 uses these to triage and dispatch fixes; no lane reads them. Thirty-eight files total (`ls review-harvest/ | wc -l`, verified 2026-09-15) — the sixteen markdown findings documents below, plus the twenty-two JSON/script/text working files of the harvest pipeline that produced them, added here for completeness:

| File | Purpose |
|---|---|
| `review-harvest/_BLOCKERS.md` | Consolidated blocker list (severity: BLOCKING) from all review passes, sorted by lane and phase |
| `review-harvest/_FIX_AGENDA.md` | Prioritised fix agenda: which blockers to resolve before dispatch, which the merge train handles, which are false |
| `review-harvest/_DEDUP_REPORT.md` | Deduplication report: findings that appear in more than one review file, with canonical source |
| `review-harvest/_DISPATCH_GATE.md` | Dispatch-gate checklist: the two named conditions from FD-014 and the current triage status of each |
| `review-harvest/_QUARANTINE.md` | Quarantined findings: findings whose premises were later found false (including stale body-count claims from superseded file snapshots) |
| `review-harvest/_CLASS_citation.md` | Class: citation defects — dangling references, stale line numbers, wrong file paths |
| `review-harvest/_CLASS_command-error.md` | Class: command errors — commands that will fail, wrong flags, missing executables |
| `review-harvest/_CLASS_completeness.md` | Class: completeness defects — missing task bodies, missing SELF-VERIFY blocks |
| `review-harvest/_CLASS_contradiction.md` | Class: contradictions — two documents stating opposite rules |
| `review-harvest/_CLASS_cross-cutting.md` | Class: cross-cutting defects — defects spanning multiple lanes or files |
| `review-harvest/_CLASS_executability.md` | Class: executability defects — tasks whose SELF-VERIFY cannot produce the required output |
| `review-harvest/_CLASS_judgment-required.md` | Class: judgment-required items — defects that require an L0 decision before they can be fixed |
| `review-harvest/_CLASS_missing-control.md` | Class: missing controls — enforcement mechanisms described in prose but not wired into CI or a gate |
| `review-harvest/_CLASS_path-ownership.md` | Class: path-ownership defects — tasks that write to paths a different lane owns |
| `review-harvest/_CLASS_task-id.md` | Class: task-id defects — collisions, orphaned ids, dual-defined bodies |
| `review-harvest/_CLASS_style.md` | Class: style defects — identifier format, commit message format, file naming |
| `review-harvest/review-A-L0L1L2.json` | Raw per-file review findings, harvest batch A (lanes L0, L1, L2) |
| `review-harvest/review-B-L3L4L5.json` | Raw per-file review findings, harvest batch B (lanes L3, L4, L5) |
| `review-harvest/review-C-shared.json` | Raw per-file review findings, harvest batch C (`master/`, `protocol/`, `manual/`) |
| `review-harvest/cross-cutting.json` | Raw output of the cross-cutting review sweep (spec coverage, id collisions, command integrity, etc.), pre-harvest |
| `review-harvest/cross-final-3.json` | Raw output of the cross-cutting review sweep, round 3 |
| `review-harvest/round2-lanes.json` | Wave-2 adversarial review findings, lane files |
| `review-harvest/round2-shared.json` | Wave-2 adversarial review findings, shared files (`master/`, `protocol/`, `manual/`) |
| `review-harvest/_harvest.py` | Script that pulls per-reviewer findings out of the workflow journals into `_ALL_DEFECTS.json`, excluding roll-up double-counts |
| `review-harvest/_dedupe.py` | Script that collapses `_ALL_DEFECTS.json` into `_DEFECTS_DEDUPED.json` / `_DEDUP_REPORT.md` by rare-identifier overlap |
| `review-harvest/_ALL_DEFECTS.json` | Consolidated raw findings from every review pass above, pre-dedup; input to `_dedupe.py` |
| `review-harvest/_ALL_DEFECTS.round1-backup.json` | Snapshot of `_ALL_DEFECTS.json` taken before the round-2 review passes were folded in |
| `review-harvest/_DEFECTS_DEDUPED.json` | Deduplicated defect set, output of `_dedupe.py` |
| `review-harvest/_DEFECTS_SYSTEMIC.json` | Defects classified as systemic rather than local; currently empty (`[]`) |
| `review-harvest/_DUPLICATE_PAIRS.json` | Candidate duplicate-finding pairs and the shared identifiers linking them, input to `_dedupe.py` |
| `review-harvest/_BLOCKERS_INDEXED.json` | `_BLOCKERS.md`'s findings as structured JSON (src/reviewer/target/severity/category), for tooling |
| `review-harvest/_VERDICTS.json` | Per-file verdict (e.g. MAJOR-ISSUES) from each review pass, keyed by run and reviewer |
| `review-harvest/_batch120.txt` | Raw text output of an early review batch (`DF-` numbered findings), predating the JSON harvest pipeline |
| `review-harvest/_B3_L2_DECISION_BRIEF.md` | Decision brief for blocker B3 — L2's three-way `D-L2-07`/`D-L2-08`/`D-L2-09` id collision — mapping each sense to its `REG-` entry |
| `review-harvest/_D_L4_01_02_BRIEF.md` | Decision brief for `D-L4-01`/`D-L4-02`, the event-type-enum and metric-declarations questions raised by `L4-04-M15` |
| `review-harvest/_GATE_EVAL_2026-09-06.md` | FD-014 dispatch-gate evaluation snapshot, 2026-09-06, checking the six `L*-99-review.md` verdicts against FD-030–052 |
| `review-harvest/_FOUNDER_DECISIONS.md` | Session 9 (2026-09-02) FD additions extending the root `_FOUNDER_DECISIONS.md`; a same-named but distinct file from the one at the repository root |
| `review-harvest/fix-last-blockers.json` | Working record of the final blocker-fix pass — files edited, line deltas, summaries |

### 5.9 `contracts/` — the frozen contract surface (Phase 0 output)

`contracts/**` is written by L0 in Phase 0 and FROZEN under PARTITION.md rule 2. FD-013 settled the exact layout. No file in `contracts/` is a markdown plan document; the surface consists of YAML schemas, a lock file, and a consumer manifest. The directory is populated during Phase 0 execution; it is listed here so every lane can locate the surface it reads.

**FD-013 frozen surface** (from `_FOUNDER_DECISIONS.md` FD-013):

| Path | Consumer(s) |
|---|---|
| `contracts/schemas/` | L1 |
| `contracts/event-types/event-type.enum.v1.yaml` | L2, L4 |
| `contracts/records/` | L4 |
| `contracts/workflow-io/` | L2, L3 |
| `contracts/cli/` | L1, L3 |
| `contracts/fixtures/` | All lanes |
| `contracts/CONTRACTS.lock` | Gate B (`IG-05`) |
| `contracts/estate.yaml` | L1, L3, L5 |
| `contracts/lane-paths.yaml` | `master/05` `UEG-2` |
| `contracts/l1-schemas.yaml` | L1 |
| `contracts/l2-workflows.yaml` | L2 |
| `contracts/l3-reconciler.yaml` | L3 |
| `contracts/l4-records.yaml` | L4 |
| `contracts/l5-access.yaml` | L5 |
| `contracts/v1-scope.yaml` | `master/06` §11 |
| `contracts/environment-schema.yaml` | All lanes (FD-013 amendment) |
| `contracts/CONSUMERS.md` | Everyone |
| `contracts/validator-contract.md` | L1 (frozen interface for Option B validator CLI — FD-094) |
| `contracts/orphans/decisions.yaml` | L0, L3 (orphan detection input surfaces — FD-108) |
| `contracts/v1-scope.yaml` | `master/06` §11 (V1 scope contract — FD-112) |

**Unresolved split (C-9, C-14):** `master/05` `UEG-2` reads `contracts/lane-paths.yaml`; the lane guard reads the root `lane-paths.tsv`; `master/03` names a third path. As shipped, `UEG-2` fails for every lane at every phase entry, permanently.

### 5.10 Session 15 implementation artifacts (2026-09-09)

Concrete implementation files placed in Phase 0 as L1 lane deliverables. These are not plan documents; they are the artifacts the plan files describe and that the lane agents will extend in Phase 1.

**Update, 2026-09-09 (later the same day):** the validator CLI's 18 rules, stubbed when this section was first written, were completed in commit `9e1fb49` — "feat(validators): implement all 18 rules R01-R18 with full YAML parsing". `cli.py` and the `rules/` row below reflect that; Phase 1 now extends/hardens the rules rather than filling empty bodies.

| File | Purpose | FD |
|---|---|---|
| `schemas/registry/people.v1.schema.json` | People registry JSON Schema — validates `registries/people/*.yaml` entries | FD-096 |
| `schemas/registry/capabilities.v1.schema.json` | Capabilities registry JSON Schema | FD-096 |
| `schemas/registry/roles.v1.schema.json` | Roles registry JSON Schema | FD-096 |
| `schemas/registry/platform.v1.schema.json` | Platform registry JSON Schema | FD-096 |
| `schemas/registry/exceptions.v1.schema.json` | Bootstrap exceptions registry JSON Schema | FD-096 |
| `schemas/registry/policies.v1.schema.json` | Policies registry JSON Schema | FD-096 |
| `schemas/product/service.v1.schema.json` | Service product contract JSON Schema | FD-096 |
| `validators/registry/cli.py` | Option B validator CLI entry point — dynamically loads and runs all 18 rules (single `--rule Rnn` or the full suite via `run_all`); exit 0/1/2 per the frozen interface | FD-094 |
| `validators/registry/rules/r01..r18_*.py` (18 files) + `registry.py` | All 18 validator rules (R01–R18) fully implemented with real YAML parsing — id-uniqueness, reference validity, date/expiry checks, schema-version match, canary integrity, etc. **Not stubs** (no `NotImplementedError`/`TODO`/bare `pass` in any rule body — the sole `pass` left, in `r14_schema_version_match.py`, is inside a `try/except`, re-verified 2026-09-09); two correctness fixes have landed since this row was first written — `94bde1e` (R10/R12/R14 empty-registry short-circuit bug; CLI `--root` hardening) and `9891290` (R01/R08 fallback-directory bug, which always resolved to the registry root); 799 lines total, up from 706 | FD-094 |
| `validators/registry/make-fixture.sh` | Fixture generator for validator test harness | FD-094 |
| `registries/people/_canary.yaml` | Canary seed entry — seeded registry for instrument integrity checks | FD-106 |
| `.github/workflows/lane-guard.yml` | Lane guard CI workflow — enforces branch protection on every lane PR | FD-102 |
| `scripts/actor-gate.sh` | Actor gate enforcement script — validates actor identity on write paths | FD-086 |

---

## 6. Reading orders

### 6.1 The L0 integrator — the human lead

You are the only reader who reads the whole set. Read in this order before B-Day.

| # | File | Why here |
|---|---|---|
| 1 | `PARTITION.md` | The frozen contract you are enforcing |
| 2 | `master/00-MASTER-PLAN.md` | Scope, tiers, calendar, entry criteria, DoD |
| 3 | `master/01-lane-architecture.md` | Path ownership row by row and the `C1`–`C18` surfaces you must freeze |
| 4 | `master/06-v1-scope.md` | What you are actually shipping first |
| 5 | `master/04-phase-map.md` | The two clocks, the sequence, and the sync points you declare passed |
| 6 | `master/02-branch-merge-model.md` | The git topology and the rulesets you apply at Phase 0 |
| 7 | `master/03-conflict-prevention.md` | The guard you install and the CCR procedure you operate |
| 8 | `lanes/L0-00-charter.md` | Your standing charter — keep it open |
| 9 | `lanes/L0-01-phase-0-contracts.md` | Your Phase 0 task list. Execute it; nothing else starts until it prints `PHASE-0-COMPLETE` |
| 10 | `lanes/L0-02-lane-guard.md` | Build the guard before any lane opens a branch |
| 11 | `lanes/L0-04-decisions-register.md` | The 62 `REG-` ids. Answer the P0 ones before dispatch |
| 12 | `master/05-entry-exit-criteria.md` §0, §2 | Your own gates: `L0-P0`, `G-INT`, `G-F*` |
| 13 | `protocol/00`, `05`, `06` | Test strategy, the two gates, the daily cycle |
| 14 | `lanes/L0-03-merge-train.md`, `lanes/L0-05-integration-gate.md` | The train and GATE B, as operational procedure |
| 15 | `master/08-progress-tracking.md` | The ledger you author and the report you generate |
| 16 | `master/07-risk-register.md` | The detection commands you run at each slot and cycle |
| 17 | `protocol/07-rollback.md` | Before you need it, not after |
| 18 | `_INTEGRITY.md` + the five `lanes/L*-99-review.md` | Current dispatch verdict — read `_INTEGRITY.md` §B before treating L1-99 or L5-99 as blocking |
| — | `_DECISION_SIGNOFF.md`, `_FOUNDER_DECISIONS.md` | On demand for any closed `REG-` or `FD-` entry |
| — | Everything else | On demand |

**Before B-Day you must also resolve, or explicitly defer with a dated record, every item in §7.** The contradictions C-1/C-3/C-4/C-13/C-14/C-18 and gaps G-2/G-6/G-7 block dispatch directly; the register cites each by its C-/G- id.

### 6.2 A lane developer being dispatched — an AI agent working one task

Short and fixed. Do not read outside it; `manual/09-cost-and-context-discipline.md` is binding on how much you read.

| # | File | Read |
|---|---|---|
| 1 | `manual/00-README-FOR-AI-DEVELOPERS.md` | In full. Two minutes. |
| 2 | `PARTITION.md` | In full. It is 47 lines. |
| 3 | `manual/03-guardrails-and-stop-rules.md` | In full. It overrides your task card. |
| 4 | `manual/04-anti-hallucination.md` | In full. |
| 5 | `manual/02-task-execution-protocol.md` | In full — this is your loop, steps 1–12. |
| 6 | `manual/05-git-workflow.md` | In full, including §14 forbidden commands. |
| 7 | `manual/09-cost-and-context-discipline.md` | In full, before you read anything not on this list. |
| 8 | `master/09-glossary-and-conventions.md` | §2 identifiers, §4 branch naming, §5 commits, §6 PRs, §7 blockers and CCRs. |
| 9 | `lanes/L<your-lane>-00-charter.md` | In full. |
| 10 | `lanes/L<your-lane>-<your-phase>-*.md` | **Your phase file only.** |
| 11 | `master/05-entry-exit-criteria.md` §0 + your lane's section | Your entry and exit gates. |
| 12 | `manual/07-worked-example.md` | Once, if this is your first task of that shape. |
| 13 | `manual/06-pr-and-review.md`, `manual/10-quality-bar.md` | Before you open the PR. |
| 14 | `manual/08-failure-playbook.md` | Only when something has already gone wrong. |

**Never read:** another lane's files, any `lanes/L*-99-review.md`, `lanes/L*-CONCORDANCE.md`, `lanes/L*-98-DEEP-REVIEW.md`, `cross/`, or `review-harvest/`. The interface to another lane is `contracts/**` and nothing else.

**If your task card cites a `REG-` id:** look it up in `lanes/L0-04-decisions-register.md`. Do not infer the answer.

### 6.3 A reviewer

| Reviewing | Read, in order |
|---|---|
| **One lane PR** | `PARTITION.md` → `master/09` §5–§6 (commit and PR format) → `master/03` §1 (what the guard proves and what it does not) → the task's own file in `lanes/` → `manual/10-quality-bar.md` → `master/07` §5.4 detection commands |
| **A phase exit** | `master/04-phase-map.md` §4, §7 → `master/05-entry-exit-criteria.md` for that phase → `protocol/04-negative-tests.md` for the gates that must be executed negatively → `protocol/05-merge-gate.md` |
| **An integration cycle or a promotion** | `protocol/06-integration-cycle.md` → `protocol/05-merge-gate.md` §4 (GATE B) → `lanes/L0-05-integration-gate.md` → `protocol/08-smoke-and-e2e.md` |
| **An acceptance-test claim** | `protocol/02-acceptance-mapping.md` → `protocol/03-invariant-tests.md` → `master/06-v1-scope.md` §8 → `protocol/11-definition-of-done.md` |
| **A whole lane, for dispatch readiness** | that lane's `L<n>-99-review.md` → `_INTEGRITY.md` per-file rows → `_RESIDUE.md` §1 → the lane's `00` charter and its tasks file → §7 below |
| **The plan itself** | `PARTITION.md` → `master/00` → `master/01` → §7 below → `protocol/99-WALKTHROUGH.md` → `master/07-risk-register.md` |

---

## 7. OPEN ITEMS

Every item below is known to L0 and is not yours to resolve as a lane developer. The id space uses three prefixes: **C-** (contradictions — two documents state opposite rules), **G-** (gaps — something required does not exist), **R-** (risks — build risk from an unresolved question). These ids are the ones cited in `lanes/L0-04-decisions-register.md` and `_FOUNDER_DECISIONS.md`; an entry of the form "Raised as: master/INDEX.md C-14" resolves to the row below labelled C-14.

---

### 7.1 Contradictions

Two documents stating opposite rules for the same situation.

| ID | Summary | Documents in conflict | Register |
|---|---|---|---|
| **C-1** | Branch-name grammar — `master/02` §2 enforces `^lane/[1-5]/(p[0-7]\|g[1-8]\|pp[1-8])-[a-z0-9-]{3,40}$` as the required branch shape | `master/02` L54 | REG-011 |
| **C-2** | Branch-name grammar — `master/09` §4 enforces `^lane/[1-5]/(f[0-7]\|g[1-8]\|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}$` and explicitly declares `master/02`'s convention wrong; yet `master/02`'s pattern is the one `protocol/10` L377 enforces in CI (`exit 1`) | `master/09` L244; `protocol/10` L377 | REG-011 |
| **C-3** | Merge method — `master/02` §5.3 mandates `gh pr merge --merge` ("never squash, never rebase") and §10.1 sets `allow_squash_merge=false` at repository level; `master/09` §6.4 mandates squash and specifies the squash commit message | `master/02` L161, L611; `master/09` L516 | REG-012 |
| **C-4** | `git add` — `master/02` §O-2 forbids `git add .` and `git add -A` ("stage explicit paths"); `manual/00` §7 Step 7 instructs `git add -A` — and `manual/00` is the first file every agent reads | `master/02` L234; `manual/00` L151 | REG-012 |
| **C-5** | Branch creation convention — `master/02` and `master/09` each state a different branch-creation flow; agents following one violate the other | `master/02`; `master/09` §4 | REG-012 |
| **C-6** | Canonical blocker/PR templates — `docs/plan/BLOCKER.md` is the path cited in `master/02` §6.1; `docs/escalation/BLOCKER.md` is the path cited in `L0-00-T05` and DoD proofs. One must not exist or one must be an alias | `master/02` §6.1; `lanes/L0-00-charter.md` T05 | REG-012 |
| **C-7** | Lane 2 dual task ids — `L2-T500`–`T516` carry a full body in both `L2-04-evidence-chain.md` and `L2-05-tasks.md`; `L2-T520`–`T525` carry a full body in both `L2-02-digest-invariant.md` and `L2-05-tasks.md`. 32 ids are dual-defined; two agents given Lane 2 will write different files under one id | `lanes/L2-04`, `lanes/L2-02`, `lanes/L2-05` | — |
| **C-8** | Lane 3 two complete plans — `L3-06-tasks.md` (78 tasks, `L3-P<phase>-<nn>` scheme) vs. the seven phase files (116 tasks, five other schemes). Not one id is shared in either direction; both plans build the same artifacts. L0 must designate one and demote the other | `lanes/L3-06` vs `lanes/L3-01`…`L3-05` | — |
| **C-9** | `.github/` non-workflow path ownership — `master/03` §1.2 assigns these paths to L0 as though frozen, but no rule in `lane-paths.tsv` covers them; a PR adding any `.github/` non-workflow file resolves `UNOWNED` and the lane guard refuses it | `master/03` §1.2; `lanes/L0-02` | REG-002, REG-017 |
| **C-10** | `.github/**` and repository root inside `control-plane-records` — path ownership in the records repo is unresolved; `lanes/L4-00` §9 raises the question without answering it | `lanes/L4-00` §9 | REG-055 |
| **C-11** | Registry file location — the spec requires `test -f people.yaml` at the repository root; `master/00` EC-11, `master/02` §13, `master/05` §3 and `master/09` §8.1 reference conflicting paths for the same registry file | `master/00`, `master/02`, `master/05`, `master/09` | REG-008 |
| **C-12** | Registry file location (second file) — a second spec-named registry file is referenced at inconsistent paths across the plan documents | `master/00`, `master/02` | REG-008 |
| **C-13** | Branch-protection mechanism — `master/02` §10 and `master/03` §1.5 state different requirements for `integration`'s required-check list at Phase 0 | `master/02` §10; `master/03` §1.5 | REG-013 |
| **C-14** | Required-check list at Phase 0 — `master/00` EC-3 requires `main`'s check list to be `[]` to PASS; `master/00` EC-13 requires it populated; `master/05` `L0P0-E4` requires length 0. These are mutually exclusive | `master/00` EC-3 vs EC-13; `master/05` L0P0-E4 | REG-013, REG-002 |
| **C-15** | CODEOWNERS content — `master/01` §3 specifies lane teams as owners; `master/03` §1.6 and `master/00` EC-14 require human reviewers. A team containing a machine account fails EC-14; the §98.2 check is executed negatively | `master/01` §3; `master/03` §1.6; `master/00` EC-14 | REG-014 |
| **C-16** | Commit-signing scope — `master/02` §10.5 and `master/09`'s recommendation conflict on which branches require signed commits; `master/05` `UXG-4` makes every commit on every lane branch signature-verified as a universal exit criterion | `master/02` §10.5; `master/09`; `master/05` UXG-4 | REG-006 |
| **C-17** | Lane 4 incompatible id namespaces — of 117 rows in `L4-06-tasks.md` (which calls itself "the complete ordered work list executable from this file alone"), 94 have no body in any L4 document; 84 tasks that do have bodies appear in no row of that table. Six charter DoD proof commands invoke executables no task builds | `lanes/L4-06`; `lanes/L4-02`…`L4-05` | — |
| **C-18** | Branch-name grammar (live names) — the branch names actually in use across the lane files (`lane/1/01-repo-skeleton`, `lane/2/phase0-charter`, `lane/4/00-charter-preflight`, `lane/3/05-loader`) pass neither `master/02`'s nor `master/09`'s grammar. The lane guard derives the lane number from the branch name, so a non-conforming name misidentifies or orphans the PR | All lane phase files; `master/02` L54; `master/09` L244 | REG-011 |
| **C-19** | Phase vocabulary — no crosswalk between the four phase vocabularies: `B0`–`B7` (`master/00` §4.2), `BT-0`–`BT-4`/`S0`–`S4` (`master/04` §2), `L<n>-P<k>` (`master/05` §0.2), `F0`–`F7`/`G1`–`G8`/`P1`–`P8` (`master/09` §3.2). Branch names, task ids and gate ids all encode a phase; a lane cannot mechanically determine which phase it is in | `master/00`, `master/04`, `master/05`, `master/09` | REG-011 |
| **C-20** | Subsystem count — `master/04` §8 states *"seventeen lettered subsystems A–R"*; `master/07` states eighteen twice and enumerates five unassigned ones. A–R is eighteen letters; `master/04` is wrong, and it is the file L0 sequences from | `master/04` L323; `master/07` L313, L637 | REG-011 |
| **C-21** | Lane 5 five id schemes — the phase files use five mutually exclusive id schemes (`L5-01-T*`, `L5-P2-T*`, `L5-P3-*`, `L5-04-T*`, `L5-05-{K,Q,R}*`); `L5-06-tasks.md`'s `L5-T*` namespace shares no id with any of them; no cross-reference exists in either direction. An agent handed `L5-T17` cannot locate it under any name | `lanes/L5-06`; `lanes/L5-01`…`L5-05` | — |
| **C-23** | Implementation toolchain — language, runtime version, and dependency pinning are not specified in the spec; every lane's Phase 0/1 opens a `L0 DECISION REQUIRED` block on this point | All lane charters | REG-003 |
| **C-24** | ~~Five parallel decision registers with overlapping content and no cross-references~~ — **CLOSED** by `lanes/L0-04-decisions-register.md` (62 `REG-` ids, 3,044 lines) | — | — |
| **C-26** | Signal denominator — SIG-43 appears twice in the spec, assigned to two different signals; the stated signal denominator is 46 in some places and 47 in others | `Research/MultiProduct_MasterSpec_v4.0.md` | REG-054 |

---

### 7.2 Gaps

Something that the plan requires to exist but does not.

| ID | Summary | Where it is missing | Register |
|---|---|---|---|
| **G-2** | No phase-vocabulary crosswalk — the root cause of C-1, C-2 and C-19. Until a single vocabulary is designated and a crosswalk published in `master/09`, branch names, task ids and gate ids are ambiguous to any mechanical tool | `master/09` | REG-011 |
| **G-3** | ~~No single decision log~~ — **CLOSED** by `lanes/L0-04-decisions-register.md` | — | — |
| **G-4** | `master/00` §7 is the authoritative index of a document architecture that was never built. It declares *"Twenty documents…"* and names 19 specific paths (`master/01-CONTRACT-SURFACE.md`, `protocol/10-LANE-OPERATING-PROTOCOL.md` through `protocol/16-ACCEPTANCE-TEST-HARNESS.md`, `manual/20`–`manual/23`, `lanes/L1-REGISTRIES-AND-CONTRACTS.md` through `lanes/L5-ACCESS-INFRA-AND-OPS.md`) — not one of which exists. By §7's own rule, every file that does exist is *"not part of the plan"*, and §0/§9's escalation paths terminate nowhere | `master/00` L486–520 | — |
| **G-5** | `contracts/**` surface list — exact filenames and directory layout were unspecified in any frozen document. **Resolved by FD-013** (§5.9 lists the frozen surface). Residual gap: the `contracts/lane-paths.yaml` vs `lane-paths.tsv` split (C-9, C-14) | `master/01` §5; `master/03` §3.1 | REG-007 |
| **G-6** | No acceptance-test harness file — no harness exists at any path; every AT that `IG-07` depends on is unexecutable. `IG-07` fails closed and GATE B stays closed until REG-015 is resolved | `protocol/02`; `lanes/L0-05` §5 | REG-015 |
| **G-7** | Five subsystems assigned to no lane — G (plan-checker and Gate 1 tooling), H (dashboards and views), J (background machine layer), O (governance registries and jobs) and P (people intelligence engine) appear in no lane's OWNS column. G carries a load-bearing risk row; O carries the exception lifecycle | `master/04` §8; PARTITION.md | REG-017 |
| **G-8** | `master/02` sends every lane developer to its task card in `implementation/lanes/L<N>.md` — a path that has never existed; the packs are `L<N>-<nn>-<slug>.md`. `manual/02-task-execution-protocol.md` names a third layout, `implementation/lanes/L<N>/tasks/<TASK_ID>.md`. `manual/11` now uses the correct `lanes/L<N>-*.md` glob | `master/02` L5, L287, L319; `manual/02` L1044 | — |
| **G-9** | `manual/06` line 701 PR-body template cites task card `implementation/lanes/L1-05-tasks.md#L1-P2-T07`. The path is correct; the anchor does not resolve — Lane 1's ids are `L1-001`…`L1-905`. An agent that copies this template produces an unresolvable link. Renumbering the worked example is a rewrite of `manual/06` §11, not a path repair, so it was not made here; L0 decides which id grammar is normative | `manual/06` L701 | — |
| **G-10** | Contracts surface producer — `master/01` §5 names L4 as the producer of surfaces C1/C2/C3; `master/03` §3.1 places authorship with L0; under PARTITION rule 2, L0 authors all contracts at Phase 0 before any lane exists. **Resolved by FD-013** (L0 transcribes from published lane plans; neither horn of the dilemma is real) | `master/01` §5; `master/03` §3.1 | REG-007, FD-013 |
| **G-11** | Two invoked scripts never authored — `docs/plan/bin/r5b-collisions.sh` is invoked three times in `master/08`, including as the evidence command for STOP signal `S1`; `docs/plan/bin/p0-before-p2.sh` is invoked once for `S7`. Neither script exists anywhere in the set. The `S1` and `S7` detectors cannot run | `master/08` L594, L976, L979, L1000 | — |
| **G-12** | `master/06` presents its V1 exit gate as `implementation/master/v1-exit-gate.sh`. No such file exists; the script lives only inside a markdown fence | `master/06` L409 | — |

---

### 7.3 Risks

Build risk from an unresolved question or a missing mechanism.

| ID | Summary | Impact | Register |
|---|---|---|---|
| **R-6** | Git convention uncertainty — until C-3/C-4/C-5/C-6 are resolved, every lane developer hitting a conflicting rule must file a blocker naming REG-012; the conflict is present in every lane's git preamble and postamble across all 54 lane files | Every lane's first commit and every PR | REG-012 |
| **R-7** | `records/verification/gsd-pin` absent — `master/07` §5.3 check `A4` tests for this store and is the detection command for `S1`; the store is absent from `master/01` §6.3's sixteen-store list and will never be created unless it is added; the check can never pass | `master/07` §5.3 A4 | REG-020 |
| **R-9** | Two independent freeze mechanisms — `master/04` §7's `contracts/v1` tag check and `master/03` §3.2's `contracts/CONTRACTS.lock` are two independent freeze mechanisms, neither protected by any ruleset. **Addressed in FD-013's answer**: name one as normative and protect it with a new ruleset CP-4 for `refs/tags/contracts/*` | `master/04` §7; `master/03` §3.2 | REG-007, FD-013 |
| **R-11** | `master/01` §4 and §11 self-verify unrunnable — `master/01` forbids creating the guard workflow file until REG-002 is resolved; therefore `master/01`'s own self-verify block, which validates the guard, cannot be executed; those sections are untested hypotheses | `master/01` §4, §11 | REG-002 |
| **R-12** | No AT harness file — `IG-07` and therefore GATE B fail permanently until REG-015 is answered and the harness file is physically authored. It is reported as `not_run`, not `scheduled=0`; the gate never silently passes | `lanes/L0-05` §5; IG-07 | REG-015 |

---

### 7.4 Housekeeping

| ID | Item |
|---|---|
| **H-1** | `lanes/l1all.tmp` (764 KB) is a stray concatenation left in the lanes directory. It is not a plan document and should be deleted before dispatch |
| **H-2** | `_STATUS.txt` reports a stale line count and is superseded by `_INTEGRITY.md` and by this file |

---

### 7.5 Closed since the previous index — recorded so they are not re-raised

| Was | Status now |
|---|---|
| **O-1 through O-6** — former "dispatch blockers — missing task bodies" asserting 116 bodies absent across L1 and L5 | **FALSE — do not action.** All bodies confirmed present by `_INTEGRITY.md` §B. Verification commands, re-run 2026-09-09: `grep -cE '^#{2,4} +L1-[0-9]{3,4} ' lanes/L1-05-tasks.md` → **157** (was 61 before commit `7679902` reconstructed 69 truncated bodies and the file absorbed 96 more tasks; the old 3-digit-only pattern now undercounts by 2 because it misses `L1-1000`/`L1-1001`); `grep -cE '^#{2,4} +L5-T[0-9]{2} ' lanes/L5-06-tasks.md` → **74** (the file itself is unchanged this session — 59 was already an undercount when first recorded, not new drift); heading checks for `L5-03`, `L5-04`, `L5-05`, `L5-07` all clear. **Any plan, issue or review that asserts these as blockers is citing a superseded snapshot.** `L1-99` and `L5-99` block on the same false counts; their BLOCKED verdicts are weakened on those points |
| **C-24** — five parallel decision registers | **Closed** by `lanes/L0-04-decisions-register.md` (62 `REG-` ids) |
| **G-3** — no single decision log | **Closed** by `lanes/L0-04-decisions-register.md` |
| *Several numbered slots absent* — L2 had 2 of 8 files, L4 had 2 of 8, L5 was missing `01`/`05`/`06`, L3 was missing `03`, `manual/` skipped `07` | **Closed.** All 94 core plan files exist. `L3-03` is 6,023 lines, `L5-01` is 5,635, `L5-06` is 1,126, `manual/07` is 1,518 |
| *No onboarding track owner* | **Closed** by `lanes/L0-07-onboarding-track.md` (3,131 lines, 15 tasks) |
| The `_DAMAGE.md` truncation cohort — `L0-01`, `L2-03`, `L2-04`, `L2-05`, `L3-01`, `L3-03`, `L5-01`, `L5-02` | **Repaired.** Every continuation marker is gone and each file ends on a complete closing passage |
| *"57 markdown files, ~55,600 lines"* | **Superseded.** 94 core plan files, 172,259 lines |

---

*Regenerated 2026-09-09. Full directory walk of `master/`, `lanes/`, `protocol/`, `manual/`, `cross/`, and `review-harvest/`. Line counts for the four core directories are from `_INTEGRITY.md` §A (the authoritative sweep). The former O-1…O-23 open-item space is retired: O-1…O-6 were false (§7.5); the remaining substance is assigned to C-/G-/R- ids above, making every id cited in `lanes/L0-04-decisions-register.md` and `_FOUNDER_DECISIONS.md` resolvable to an entry in §7. Nothing in §7 is resolved by this regeneration — resolution requires L0.*

---

*Targeted update, 2026-09-09 (later same-day pass, not a full directory walk). Three things verified and corrected: (1) the validator CLI's 18 rules (R01–R18) are fully implemented, not stubs — confirmed by reading every rule file and grepping for `NotImplementedError`/`TODO`/bare `pass` (none found), commit `9e1fb49`; (2) git commit count is 9 on `master` (`git log --oneline | wc -l`), HEAD `c0ddb6e`; (3) `lanes/*.md` and `protocol/*.md` file counts were reconciled against `ls` — 66 and 16 files respectively, up from the 54/14 this file previously recorded, with the new files (`protocol/00-dispatch-model.md`, `protocol/README.md`, `lanes/L0-CONCORDANCE.md`, `lanes/L4-03-metric-register.md`, `lanes/L4-04-metric-register.md`) now catalogued in §3, §5.1 and §5.5. This pass did not touch `_FOUNDER_DECISIONS.md` or `decisions/open-decisions.yaml` — those are owned elsewhere. It did not re-run the full integrity sweep, so directory line-count totals in the Scale table above still reflect the prior sweep plus the individually-noted new files; it did not resolve the `protocol/00` or `lanes/L4-03`/`L4-04` slot collisions it surfaced, only recorded them.*

---

*Targeted update, 2026-09-09 (third pass, same day — 15 more commits landed on `master` since the previous note, none of them touching this file's own content until now). (1) **Git commit count** is now **24** on `master` (`git log --oneline | wc -l`, live), HEAD `5c86521` — "fix(phase0): L0-P0-012 never created CPR content before committing — crashed at task 12". (2) **Validator rule status** (§5.10): still all 18 rules implemented, still no stub bodies (re-verified live); two correctness fixes landed since the last note — `94bde1e` (R10/R12/R14 empty-registry short-circuit bug; CLI `--root` hardening) and `9891290` (R01/R08 fallback-directory bug, which always resolved to the registry root) — combined `rules/` + `registry.py` line count is now **799**, up from 706. (3) **Test count**, run live: `python -m pytest --collect-only -q` collects **104 tests**, all under `tests/` at the repository root (`tests/integration/*.py` plus `tests/test_phase0_lib_sync.py`) — note this is a different location from the `validators/registry/tests/**` path `lanes/L1-06-tests.md` describes; that discrepancy is not reconciled here. (4) **`lanes/L1-05-tasks.md`** grew from 6,132 to **20,001 lines** and from 61 to **157 tasks** (`L1-001`…`L1-1001`) — commit `7679902` reconstructed 69 previously-truncated task bodies and the file absorbed 96 additional tasks; §5.2 and the O-1…O-6 verification note in §7.5 are corrected above. (5) **`lanes/L5-06-tasks.md`** was found, incidentally, already miscounted at 59 tasks/1,126 lines while re-verifying (4)'s grep pattern; live count is **74 tasks / 5,622 lines** (`L5-T01`…`L5-T74`). This file has not been touched by any commit this session (last touched in the initial bootstrap commit `7780141`), so the error predates this session and every prior pass of this index — it is corrected above, not because it drifted today. This pass touched only `master/INDEX.md` and did not touch `_FOUNDER_DECISIONS.md` or `decisions/open-decisions.yaml`. It did not re-run the full integrity sweep or refresh the Scale table's per-directory line-count totals in §0 — those still reflect the prior sweep. Spot checks taken during this pass (the two corrections above, plus `ls`-based file counts per directory, unchanged at 66/16/14/11) indicate those aggregate totals have drifted further and are due a full re-derivation; none was performed here.*
