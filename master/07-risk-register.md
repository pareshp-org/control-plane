# 07 — Risk Register (the implementation programme)

**Scope:** risks to *building* the operating system with five parallel AI developers plus one integrator (L0).
**Not in scope:** risks to the operating system once it runs. Those are the forty-seven health signals of spec Section 52.2 (SIG-01 … SIG-47), the drift classes of Section 53.4, and the edge-case catalogue of Section 102. This file never duplicates them; where a build risk maps onto a live SIG identifier the mapping is named, and the SIG stays the authority.

**Authority order.** `Code/implementation/PARTITION.md` (frozen) > the spec (`Research/MultiProduct_MasterSpec_v4.0.md`) > the protocol files under `Code/implementation/protocol/` > this file. This file never redesigns the partition; where it identifies a gap in coverage it raises an `L0 DECISION REQUIRED` block and stops.

**Owner:** L0. Every row in both registers is owned by L0. The five lanes own no risk — a lane's only duties are the *lane duty* column (a command it runs before opening its PR) and the STOP rules in §6. A lane that hits a STOP rule opens a blocker issue and stops; it never improvises a fix.

---

## 1. Scales

These are the only three scales used in this file. They are countable, so two people scoring the same row get the same answer.

### 1.1 Likelihood

| Code | Meaning — stated as a frequency, not a feeling |
| --- | --- |
| **H** | Expected at least once per merge cycle. With five lanes running, assume it happens this week. |
| **M** | Expected at least once per phase, not every cycle. |
| **L** | Expected at most once across the whole programme, or requires a second independent failure first. |

### 1.2 Impact

| Code | Meaning |
| --- | --- |
| **I1** | Programme-stopping. `main` becomes unreleasable, or a spec invariant (Section 101, #1–#111) ships violated, or work already merged must be discarded. |
| **I2** | Phase-slipping. One or more lane-days lost, or a merge cycle skipped, or rework spanning more than one lane. |
| **I3** | Task-local. Rework confined to one lane branch, under one lane-day, nothing merged. |

### 1.3 Response class

Borrowed verbatim from the spec's single drift severity scale (Section 6.7, tabulated at Section 53.4) so the programme uses no second severity vocabulary. Response times below are the *build-programme* readings of that table.

| Class | Response time in this programme | Blocks work |
| --- | --- | --- |
| Green | Recorded at the cycle review only | No |
| Amber | Fixed by the end of the next merge cycle | No |
| Red | Fixed within 2 business days; named on the L0 cycle report | No, but no new lane task starts in the affected lane |
| Blocking | Immediate. The merge train halts for the affected lane | Yes |

**Class assignment matrix** (applied mechanically; no ad-hoc classing):

| | I1 | I2 | I3 |
| --- | --- | --- | --- |
| **H** | Blocking | Red | Amber |
| **M** | Blocking | Amber | Green |
| **L** | Red | Green | Green |

---

## 2. Register A — spec-derived build risks

Rows BR-01 … BR-10 are spec Section 99.6 rows 1 … 10, transcribed without alteration of the risk or its mitigation. Rows BR-11 … BR-13 are the three secondary risks logged in the closing paragraph of Section 99.6. The likelihood, impact, class, lane and detection columns are this register's contribution — the spec states the risk and the mitigation, not a score.

| ID | Spec 99.6 row | Risk | L | I | Class | Mitigation the spec already mandates | Lane most exposed | Detection signal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BR-01 | 1 | Scope drift toward productisation — installer, tenancy, upgrade machinery for third parties | M | I1 | Blocking | Build the internal distribution for this company only; revisit only after it has run in anger (contradicts non-goal, Section 2.3; D1) | L3 (provisioning), L5 (infra) | Any added path matching `install*`, `tenant*`, `upgrade*`, `multi-tenan*`; see §5.3 cmd `A1` |
| BR-02 | 2 | Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance because the record stores were not built early | M | I1 | Blocking | Section 97 is built in Foundation, before any dashboard that reads from it | L4 (owns `schemas/records/**`, `metrics/**`, records repo) | Any dashboard/metric artifact merged while `records/**` schemas are absent; cmd `A2` |
| BR-03 | 3 | Bootstrap gates staying stubbed — relaxed gates have a habit of remaining relaxed | H | I2 | Red | Expiring exceptions with deactivation triggers; unclosed expiry escalates Red (Section 95); invariant #77; SIG-39 | L1 (exception schema), L5 (access) | An `exceptions.yaml` entry with no `expiry`, no owner or no deactivation trigger; cmd `A3` |
| BR-04 | 4 | Plan-checker dependency volatility — Gate 1 load-bears on a third-party tool in a high-mortality category | M | I2 | Amber | Verify every capability against the pinned release immediately; budget the in-house build as fallback; planning artifacts stay plain markdown and YAML | **No lane owns subsystem G** — see §7, DEC-01 | Verification record for the pinned GSD release missing at Phase 7; cmd `A4` |
| BR-05 | 5 | GitHub tier or behaviour dependencies failing silently — an unavailable protection feature reproduces the silent-gate failure | M | I1 | Blocking | Verify-before-Phase-1 checklist; fallbacks recorded as accepted risks, never assumed (Section 11.4; D73; D91) | L5 (access/infra) | A branch-protection or environment feature configured but never executed negatively; cmd `A5` |
| BR-06 | 6 | Reconciliation auto-repair — the highest-privilege identity in the system; a bug loosens security or locks everyone out | M | I1 | Blocking | Detect-only first; repair classes enabled one at a time; stricter-only rule enforced in code and tested; the reconciler credential in the top secrets tier (Section 40.1); bounded by AT-110; invariant #81 | L3 (owns `reconciler/**`) | Any repair/write code path merged before AT-110 and AT-102 pass; cmd `A6` |
| BR-07 | 7 | Instrument-before-operate — dozens of signals built ahead of real rhythm become alert fatigue | M | I2 | Amber | P0-before-P2 (Section 98.1, binding); data-before-forecasts; presentation discipline (52.3); the D77 arming discipline; the quarterly forced retirement (AT-045) | L4 (metrics), L5 (notify) | A signal row in `os-health.yaml` with no `activation_dependency` or no `lookback_window`; cmd `A7` |
| BR-08 | 8 | People-layer trust failure — Layer B leakage or a leaderboard-shaped view poisons adoption | L | I1 | Red | Datasource-level separation tested (D75); the self-view document (D110); the no-surveillance invariants (#96–#99); the P4 gate blocking evidence generation until access control exists | L5 (owns `access/**`) | A people datasource referenced in the shared Grafana provisioning; AT-097, AT-098; cmd `A8` |
| BR-09 | 9 | Data quality riding on human discipline — predictive layers compute confidently on garbage | M | I2 | Amber | Machines write state wherever plumbing exists (invariant #40, #46); roll out per product; prove one product's loop end to end before scaling | L4 (records/events) | A metric whose source is a hand-maintained file rather than `records/**`; cmd `A9` |
| BR-10 | 10 | The control plane becoming an unowned product — one VM carrying DevLake, Grafana and every job, maintained by nobody | L | I2 | Green | The ops VM has a named owner, an SLO, a declared patch cadence, a `tools.yaml` entry and a non-optional quarterly restore drill under four hours (Section 51.5; SIG-36) | L5 (owns `ops-vm/**`) | `ops-vm` artifacts merged with no `tools.yaml` entry and no named owner; cmd `A10` |
| BR-11 | secondary | A cross-reviewer implemented with Read-only permission fails silently | M | I2 | Amber | The Phase 1 completion checks catch it, executed negatively (Section 98.2) | L5 (access) | Phase 1 completion check not executed *negatively* — only the positive case recorded; cmd `A5` |
| BR-12 | secondary | QA remains the most acute single-person dependency in the model | H | I3 | Amber | Governed where QA capacity is defined; the people plan matters as much as the build plan; SIG-08, AT-082 | Not a lane risk — L0/Founder | Verification-contract work queued behind one person; visible on the L0 cycle report only |
| BR-13 | secondary | Current-configuration snapshots (roster, KRA/KPI content) go stale — they are configuration captured from source, never inferred from the spec | H | I2 | Red | Captured from their source and maintained as such; never inferred from the specification document | L1 (owns `registries/**`) | Any registry value that appears verbatim in the spec text and nowhere in a capture record; cmd `A11` |

**Reading BR-04 and BR-06 together:** they are the two rows where the spec's own mitigation is a *sequencing* rule, not a check. Sequencing is exactly what parallel execution breaks. Both therefore also appear as gate conditions in §4.

---

## 3. Register B — five-parallel-agent execution risks

These do not appear in the spec. They exist because the spec is being executed by five branches at once, by a reader profile PARTITION.md defines as "Sonnet-4.6-class, low cost, no repo context, no judgment authority".

Every row below states: how it happens, the **mechanical** mitigation already frozen into the plan (with the PARTITION rule number), the **detection signal** (an observable, not a hope), and the response.

---

### AX-01 — Silent divergence between lanes
**L** H · **I** I2 · **Class** Red · **Owner** L0

**Mechanism.** Two lanes independently need the same concept — a date-window rule, a `severity` enum, a path convention for per-item files — and each implements it plausibly and differently. Both lanes' self-verify commands pass, because each verifies its own branch. Nothing fails until integration, or later, until the reconciler and the validator disagree about the same YAML file.

**Mechanical mitigation already in the plan.** PARTITION rule 2 (contract-first): shared concepts live in `contracts/**`, are authored by L0 in Phase 0 and are FROZEN; lanes code against it and against generated stubs and fixtures. PARTITION rule 4: no cross-lane imports, so a lane cannot silently couple to another lane's private choice. A lane that needs a shared concept that `contracts/**` does not carry files a Contract Change Request — it does not invent one.

**Detection signal.** A concept name that appears in two lanes' added files but in no file under `contracts/`. Run `B1` nightly.

**Threshold.** One duplicated concept token across two lanes = Red. Two or more, or any duplication in an enum or a schema `$id` = Blocking.

**Response.** L0 halts both lanes on that concept, authors the contract entry, reissues both tasks against it. Neither lane picks a winner.

---

### AX-02 — Contract drift
**L** M · **I** I1 · **Class** Blocking · **Owner** L0

**Mechanism.** Two shapes. (a) A lane edits `contracts/**` directly — usually with a one-line "fix" that looks harmless. (b) A lane branched before a legitimate L0 contract change and codes for a week against a stale copy; its PR merges and quietly reintroduces the old shape.

**Mechanical mitigation already in the plan.** PARTITION rule 2: `contracts/**` is L0-owned and frozen; a lane never edits it, it files a Contract Change Request. PARTITION §"Branch & merge model": lane branches are short-lived (< 1 day) and **rebased on `integration` before PR**, which is precisely the control against shape (b). PARTITION rule 1 plus the lane-guard CI check reject shape (a) at PR time.

**Detection signal.** The `contracts/` tree SHA on the lane branch differs from the frozen value. This is a single value with a single correct answer — run `B2` on every lane branch, every cycle.

**Threshold.** Any difference = Blocking, without exception, including a whitespace-only difference.

**Response.** PR closed, not fixed in place. If the lane genuinely needs the change, it files a Contract Change Request; L0 makes the change on `integration`, all five lanes rebase, and only then does work resume.

---

### AX-03 — An agent inventing scope
**L** H · **I** I2 · **Class** Red · **Owner** L0 · **Lane duty: yes**

**Mechanism.** The single most common low-cost-model failure on a well-specified task: the task says "create these four files", the model creates them plus a README, a helper module, a `utils/` directory and a test harness nobody asked for. Each addition is defensible in isolation. Together they are unreviewed surface that L0 must now own forever, and they are frequently where AX-01 divergence enters.

**Mechanical mitigation already in the plan.** PARTITION's AI-developer profile: every task carries **exact file paths** and **complete acceptance criteria**. That makes the declared output set a closed list, so an addition is detectable by set difference rather than by judgment. PARTITION rule 5 (additive-only within a lane, prefer new files over editing existing ones) constrains *where* additions may land but never authorises undeclared ones.

**Detection signal.** `git diff --diff-filter=A` on the branch returns a path not on the task's declared file list. Run `B3` — the lane runs it too, as its lane duty, before opening the PR.

**Threshold.** One undeclared file = Red. Any undeclared *directory* = Blocking (a directory is a structure decision, and structure decisions belong to L0).

**Response.** L0 deletes the undeclared paths from the branch, or accepts them explicitly by amending the task file first. Silent acceptance is prohibited — it converts an invented scope into a precedent.

---

### AX-04 — Hallucinated file paths
**L** H · **I** I3 · **Class** Amber · **Owner** L0 · **Lane duty: yes**

**Mechanism.** The model writes `schemas/registry/person.schema.json` when the contract says `schemas/registry/people.schema.json`; or references `tools/records/emit.py` from a workflow when the file is `tools/records/emit-event.py`; or cites a path from a *different* repository. YAML and Markdown do not resolve references, so nothing errors. The workflow fails months later, in CI, on someone else's branch.

**Mechanical mitigation already in the plan.** PARTITION's AI-developer profile requires a **self-verify command whose output is unambiguous** on every task. A self-verify that only checks "did I write a file" does not catch this; the self-verify must resolve every path the new files *reference*. That resolution is command `B4` and it belongs in every lane task's verify step.

**Detection signal.** `B4` prints one line per unresolvable path reference and exits non-zero. Expected output on a clean branch is exactly `OK 0 unresolved`.

**Threshold.** Any unresolved reference = Amber and the PR does not merge. It is I3 rather than I2 only because it is cheap to fix *if* detected before merge; undetected it becomes AX-06.

**Response.** Lane fixes on its own branch. No L0 involvement unless the correct path is in another lane's tree, which is AX-12.

---

### AX-05 — Plausible-but-wrong commands
**L** H · **I** I2 · **Class** Red · **Owner** L0 · **Lane duty: yes**

**Mechanism.** The model writes a command that reads correctly and is wrong: a `gh api` call against an endpoint that does not exist on the plan tier (Section 11.4, D73), a `jq` filter that silently yields `null` instead of failing, a `yq` invocation with v3 syntax against v4, a `find -exec` that succeeds while matching nothing. Then it writes, in the PR body, that the command was run and passed. Nothing in the repository distinguishes a command that was executed from a command that was composed.

**Mechanical mitigation already in the plan.** Two, jointly: (i) PARTITION's requirement that every task carry a *self-verify command whose output is unambiguous* — "unambiguous" means it prints a value that cannot be produced by a no-op, not merely exit 0; and (ii) the acceptance criterion must be checked **by CI on the branch tip**, not by the agent's report. A claim is not evidence; a workflow run against the tip SHA is.

**Detection signal.** The most recent CI run's `headSha` does not equal the branch tip SHA, or no run exists. Command `B5` prints exactly `VERIFIED-AT-TIP` or `STALE-OR-UNVERIFIED`.

**Threshold.** `STALE-OR-UNVERIFIED` = Red, PR not merged. A `jq`/`yq` command in a merged file that can return `null` without non-zero exit = Amber, fixed next cycle.

**Response.** L0 re-runs the verify in CI. If it fails, the task is reissued with the failing command replaced by an explicit one; the agent is never asked to "check again", because the same model composes the same plausible command.

---

### AX-06 — Silent partial completion
**L** H · **I** I1 · **Class** Blocking · **Owner** L0 · **Lane duty: yes**

**Mechanism.** The task has six acceptance criteria. The agent satisfies four, produces stub or empty files for the remaining two, and reports the task complete — often with an entirely sincere summary that lists all six. This is the failure mode that survives review, because the file *exists* and the diff *looks* like work. It is the direct parent of BR-02 (dashboards ship empty) and BR-03 (gates read armed and are not) at build scale.

**Mechanical mitigation already in the plan.** PARTITION's AI-developer profile: **complete acceptance criteria** plus a self-verify command. Made mechanical here: each task's acceptance criteria are numbered, and the self-verify prints a count line of the form `PASS n/N`. `n<N` is a failed task regardless of what the agent's summary says. This is the same philosophy the spec applies to reconciliation (AT-102, the seeded canary — a run reporting nothing is assumed broken) and to verification contracts (D97, the seeded-defect case).

**Detection signal.** Three, run together as `B6`: (a) the `PASS n/N` line, (b) added files under a plausibility floor in line count, (c) any `TODO`/`TBD`/`FIXME`/`placeholder`/`lorem` token in the added files.

**Threshold.** `n<N`, or any file added with 0 lines, or any placeholder token = Blocking. Expected `B6` output on a clean branch is exactly `PASS N/N` followed by `0 stubs 0 placeholders`.

**Response.** The task is reissued *whole*, not patched. A partially-completed task handed back for completion is where the four passing criteria silently regress.

---

### AX-07 — Merge-train starvation
**L** M · **I** I2 · **Class** Amber (Red at threshold 2) · **Owner** L0

**Mechanism.** PARTITION fixes the train order L1 → L4 → L2 → L3 → L5, in dependency order. If L1 misses its slot, everything behind it either waits or merges out of order. Out-of-order merging is the more dangerous outcome: L2 merges workflows that consume L1 schemas that are not on `integration` yet, and `integration` goes red for reasons no single lane can diagnose.

**Mechanical mitigation already in the plan.** PARTITION's fixed train order, once per cycle, and the rule that lanes merge to `integration` only via PR. The order is the mitigation; it holds only if a missed slot is *visible* rather than silently skipped.

**Detection signal.** Cycles elapsed since each lane last merged into `integration`. Command `B7` prints one line per lane.

**Threshold.** A lane with no merge for 1 cycle = Amber. 2 cycles = Red; that lane's tasks are re-scoped smaller before the next cycle, because the usual cause is a task too large for a < 1-day branch. A lane merging out of the declared order = Blocking.

**Response.** L0 does not reorder the train. L0 shrinks the starving lane's next task until it fits one slot.

---

### AX-08 — A lane blocking on another lane
**L** H · **I** I2 · **Class** Red · **Owner** L0

**Mechanism.** L3's reconciler needs the shape of L5's access model; L2's workflows need L1's schema `$id`s. The lane cannot proceed, and — this is the failure, not the waiting — an agent with no judgment authority does not wait. It invents the missing shape (AX-01), or reaches into the other lane's tree (AX-12), because inventing produces a completed task and waiting does not.

**Mechanical mitigation already in the plan.** PARTITION rule 2 and rule 4 together: a lane consumes another lane's output **only** through `contracts/**` or a published artifact. Everything one lane needs from another exists in `contracts/**` in Phase 0, *before* any lane starts, precisely so that no lane is ever blocked on another lane's source tree. The dependency order in the train exists to keep that true over time. The STOP rule ("if X, do not proceed — open a blocker issue") is the lane's only legal response.

**Detection signal.** Open blocker issues, and their age. Command `B8`.

**Threshold.** Any blocker issue open > 1 cycle = Red. A blocker issue whose text names another lane's *source path* rather than a contract gap = Blocking, because it means the lane was about to reach across.

**Response.** L0 resolves it in `contracts/**`, never by telling the blocked lane to read the other lane's branch. If the contract genuinely cannot be authored yet, L0 re-sequences the lane's tasks; the lane is never left to improvise.

---

### AX-09 — Integration debt accumulating on `integration`
**L** H · **I** I1 · **Class** Blocking · **Owner** L0

**Mechanism.** `integration` is the daily merge target; `main` takes `integration` only when the full gate passes. Small unresolved failures accumulate on `integration` — a validator that fails on one fixture, a workflow that lints dirty — and each new merge lands on top. After a week, `integration` is far from `main`, nobody knows which merge introduced which failure, and no lane can reproduce the failure because no lane owns the combination. This is the parallel-execution analogue of BR-10: `integration` becomes the unowned product.

**Mechanical mitigation already in the plan.** PARTITION's branch model: `main` is protected and releasable, only `integration` merges into it, and `integration` → `main` happens when the full gate passes. The mitigation is the *cadence* — the gate must run every cycle, on `integration`, whether or not anyone intends to promote.

**Detection signal.** Two numbers: commits on `integration` not on `main`, and the age of the oldest such commit. Command `B9`.

**Threshold.** > 2 cycles of unpromoted commits, **or** oldest unpromoted commit > 5 calendar days, **or** the full gate red on `integration` for 2 consecutive cycles = Blocking. The merge train halts for all five lanes until `integration` is green and promoted.

**Response.** Halting the train is the response; there is no partial version. Lanes continue working on their branches and do not merge. This is deliberately expensive so that the debt is paid at one cycle rather than at five.

---

### AX-10 — Foreign-path edit (lane-guard evasion)
**L** M · **I** I1 · **Class** Blocking · **Owner** L0 · **Lane duty: yes**

**Mechanism.** A lane edits a path it does not own — usually while "fixing" something adjacent, occasionally because the task file's path list was ambiguous. PARTITION rule 1 makes this a hard failure with no exceptions, because one-owner-per-path is the entire reason merges cannot conflict.

**Mechanical mitigation already in the plan.** PARTITION rule 1, enforced by CODEOWNERS **plus** the lane-guard CI check. Both, not either: CODEOWNERS routes review, the lane-guard check fails the PR.

**Detection signal.** Command `B10` classifies every changed path on a branch against the frozen ownership table and prints `OK` or one `FOREIGN <path>` line per violation. The lane runs it before opening the PR; L0 runs it again at the train.

**Threshold.** Any `FOREIGN` line = Blocking. No exceptions, per PARTITION rule 1.

**Response.** PR closed. The change, if wanted, is filed as a request to the owning lane or to L0.

---

### AX-11 — A shared mutable file reintroduced
**L** M · **I** I1 · **Class** Blocking · **Owner** L0

**Mechanism.** An agent, reasonably, adds an `index.yaml`, a `README` table listing every product, a `signals.md` catalogue, or appends to a shared list — because that is how humans normally organise things. PARTITION rule 3 forbids it absolutely: directory-per-item only, one file per event, per record, per schema. A shared mutable file is the one construct that makes five-way merges conflict, and it also violates the spec's own "no artifact becomes a dumping ground" (invariant #45) and "derived data is computed, never hand-maintained" (invariant #46).

**Mechanical mitigation already in the plan.** PARTITION rule 3, plus rule 5 (prefer new files over editing existing ones).

**Detection signal.** Any file modified — not added — by two or more lane branches in the same cycle. Command `B11`.

**Threshold.** Any file appearing in two lanes' modified sets = Blocking.

**Response.** L0 converts the shared file into a directory-per-item structure before either PR merges, and reissues both tasks.

---

### AX-12 — Cross-lane import
**L** M · **I** I2 · **Class** Amber · **Owner** L0 · **Lane duty: yes**

**Mechanism.** L3's reconciler imports `validators/registry/...` directly instead of consuming the published validator artifact; L2's workflow `include`s a path under `reconciler/`. Nothing breaks on the branch, because both trees are present in the same checkout. It breaks the moment either lane refactors inside its own owned path — which PARTITION rule 5 explicitly permits.

**Mechanical mitigation already in the plan.** PARTITION rule 4: a lane consumes another lane's output only through `contracts/**` or a published artifact, never by reaching into its source tree.

**Detection signal.** Command `B12`: grep the branch's added files for any literal path prefix owned by a different lane.

**Threshold.** Any hit = Amber and the PR does not merge. Escalates to Blocking if the importing file is a CI workflow, because that couples the pipeline to a private layout.

**Response.** Replace with a `contracts/**` reference or an artifact consumption. If neither exists, this is AX-08 and becomes a Contract Change Request.

---

### AX-13 — Fabricated spec citation
**L** H · **I** I2 · **Class** Red · **Owner** L0 · **Lane duty: yes**

**Mechanism.** The agent writes `# enforces AT-118` or `# see SIG-51` or `# per D120` in a comment, a schema `description`, or a task-completion note. These identifiers do not exist. The spec has exactly **110** acceptance tests (AT-001 … AT-100 plus AT-101 … AT-110), exactly **47** signals (SIG-01 … SIG-47), exactly **111** invariants (numbered 1 … 111), and decision records D1 … D114. A fabricated identifier is worse than no identifier: it manufactures false traceability, and Section 101's own enforcement-classification CI check exists precisely because an invariant that names no live check has no owner.

**Mechanical mitigation already in the plan.** PARTITION's AI-developer profile: no task may require designing, choosing or interpreting. Citing a spec identifier is interpretation. Therefore **the lane never authors a citation** — every identifier a lane writes is copied verbatim from the identifier list supplied in its own task file. Anything else is fabrication by construction.

**Detection signal.** Command `B13` extracts every `AT-nnn`, `SIG-nn` and `Dnnn` token from the branch's added files and range-checks it. Expected output is exactly `0 fabricated`.

**Threshold.** Any out-of-range identifier = Red, PR not merged. An out-of-range identifier inside a schema, a validator or a workflow = Blocking, because it will be read as machine-checkable traceability.

**Response.** L0 supplies the correct identifier, or the citation is deleted. The lane never picks a replacement.

---

### AX-14 — Long-lived lane branch / rebase collision
**L** M · **I** I2 · **Class** Amber · **Owner** L0

**Mechanism.** PARTITION requires lane branches to be short-lived (< 1 day) and rebased on `integration` before PR. A branch that lives four days accumulates a large rebase against four cycles of contract and fixture change; the agent, asked to rebase, resolves conflicts by judgment it does not have — and the most common resolution is to keep its own side, which silently reverts the other lanes' work.

**Mechanical mitigation already in the plan.** The < 1 day branch rule and the rebase-before-PR rule, both in PARTITION's branch and merge model. Plus the rule that a lane never rebases another lane's branch.

**Detection signal.** Command `B14`: for each lane branch, its age in hours and its distance behind `integration`.

**Threshold.** Age > 24h = Amber. Age > 48h, or > 20 commits behind `integration` = Red; the branch is abandoned and the task reissued from a fresh branch rather than rebased.

**Response.** Reissue, do not rebase. A reissued task on current `integration` costs one lane-day; a bad conflict resolution costs a cycle and is invisible.

---

### AX-15 — The records repository's history is rewritten
**L** L · **I** I1 · **Class** Red · **Owner** L0

**Mechanism.** L4 owns all of `control-plane-records`, which per PARTITION has **no review protection** — a no-bypass ruleset blocks force-push and delete (D89, D107). An agent resolving a messy state with `git push --force` is a normal reflex. The ruleset should refuse it; if the ruleset was configured wrong, nothing else notices, and invariant #47 (history is append-only) is violated in the one store where the violation is unrecoverable.

**Mechanical mitigation already in the plan.** PARTITION's repository table: the no-bypass ruleset on `control-plane-records` (D107). The spec adds the second fence: the reconciler anchors the records head SHA into the protected control-plane repository each run, so a head that does not descend from the last anchor is proof of rewriting, at reconciliation Level 5 (D107).

**Detection signal.** Command `B15`: `git merge-base --is-ancestor <last-anchor> <current-head>`. Output is exactly `APPEND-ONLY-OK` or `HISTORY-REWRITTEN`.

**Threshold.** `HISTORY-REWRITTEN` = Red immediately and Blocking if any record referenced by a merged artifact is affected. During the build, before the reconciler exists, L0 records the anchor manually every cycle (`B15` prints the value to record).

**Response.** Restore from the last anchor. Do not attempt to reconstruct; the anchor exists so that reconstruction is never a judgment call.

---

### AX-16 — Unowned build surface
**L** H · **I** I1 · **Class** Blocking · **Owner** L0

**Mechanism.** PARTITION assigns thirteen of the spec's eighteen subsystems (Section 99.2): A, B → L1; E, F → L2; C, D → L3; I, N → L4; K, L, M, Q, R → L5. **G** (plan-checker and Gate 1 tooling), **H** (dashboards and views), **J** (background machine layer, conditional), **O** (governance registries and jobs) and **P** (people intelligence engine) are assigned to no lane. This is not a defect in PARTITION — PARTITION freezes what the five lanes own, and does not claim to enumerate the whole build surface — but at execution time an unassigned subsystem is a subsystem that either never gets built or gets built by whichever lane touches its edge first, which is AX-03 and AX-10 arriving together. Two of the five are load-bearing on Register A: G carries BR-04, and O carries the exception lifecycle behind BR-03.

**Mechanical mitigation already in the plan.** PARTITION rule 1 prevents an unassigned subsystem being *absorbed* silently — a lane touching it fails the lane-guard check, because the paths are in no lane's owned set. The gap is therefore detectable rather than silent. It is not, on its own, resolved.

**Detection signal.** Command `B16`: any changed path on any lane branch that matches none of the five ownership globs and is not an L0 path.

**Threshold.** Any such path = Blocking until DEC-01 (§7) is answered.

**Response.** See **DEC-01**. Until L0 answers it, no lane task may name a path under an unassigned subsystem.

---

### AX-17 — The lane-guard check lives in a path a lane owns
**L** M · **I** I1 · **Class** Blocking · **Owner** L0

**Mechanism.** PARTITION states the lane partition is enforced by CODEOWNERS plus the lane-guard CI check. `CODEOWNERS` is L0-owned. But CI checks live in `.github/workflows/**`, which PARTITION assigns exclusively to **L2**. As frozen, L2 owns the file that polices L2 — and polices the other four lanes. An L2 agent doing routine work in its own owned path can weaken or disable the guard without touching a foreign path, so the lane-guard check itself raises no violation.

**Mechanical mitigation already in the plan.** None specific — this is a structural consequence of the frozen path assignment, and the register's job is to surface it, not to redesign the partition. What the plan does give is the general detection: any change to the guard workflow is a change to a file whose content L0 can pin by hash.

**Detection signal.** Command `B17`: the blob SHA of the lane-guard workflow file on every lane branch, compared against the value L0 froze at Phase 0. One value per branch, unambiguous.

**Threshold.** Any lane branch whose lane-guard blob SHA differs from the frozen value = Blocking, regardless of which branch it is — the matrix gives M×I1 no lower class, and an L2 branch is not the only one that can carry a stale or altered guard file forward.

**Response.** See **DEC-02**. Until answered, `B17` runs at every train slot and the frozen hash is the control.

---

## 4. Gate conditions carried from Register A into the merge train

Three Register A rows are sequencing rules, and sequencing is what parallel execution breaks. They are therefore also hard gates on the train, checked by L0 at every promotion of `integration` → `main`:

| Gate | Condition | Blocks | Source |
| --- | --- | --- | --- |
| G-A | No dashboard or metric artifact is promoted while `schemas/records/**` is absent from `integration` | BR-02 | Spec 99.6 row 2; Section 97 built in Foundation |
| G-B | No `reconciler/**` write or repair code path is promoted before AT-102 (seeded canary) and AT-110 (bounded reconciler credential) both execute for real and pass | BR-06 | Spec 99.6 row 6; AT-102; AT-110; invariant #81 |
| G-C | No P2 or P3 capability is promoted while a P0 capability is unbuilt | BR-07 | Spec Section 98.1, the P0-before-P2 rule, stated binding |

A promotion attempt that fails G-A, G-B or G-C is Blocking. These are not lane-visible; L0 checks them.

---

## 5. Detection commands

All commands are POSIX shell, runnable in Git Bash on the integrator's workstation. They read only — none mutates a branch. Run them from a clone of `control-plane` unless stated otherwise.

### 5.1 One-time setup (L0, at Phase 0 close)

Commands below expect these to exist. Keep the audit directory **outside** the repository so it collides with no lane's owned path.

```bash
set -euo pipefail
export AUDIT="$HOME/.mp-audit"
export SPEC="/c/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
mkdir -p "$AUDIT"

# Freeze the contracts tree SHA the moment Phase 0 closes.
git fetch origin
git rev-parse origin/integration:contracts > "$AUDIT/contracts.frozen"
cat "$AUDIT/contracts.frozen"    # record this value in the cycle report

# Freeze the lane-guard workflow blob SHA (see AX-17 / DEC-02).
git rev-parse "origin/integration:.github/workflows/lane-guard.yml" > "$AUDIT/laneguard.frozen"

# The frozen ownership table, transcribed from PARTITION.md. Do not edit.
cat > "$AUDIT/ownership.txt" <<'EOF'
1 schemas/registry/
1 schemas/product/
1 registries/
1 validators/registry/
2 .github/workflows/
2 templates/workflows/
2 tools/evidence/
3 reconciler/
3 tools/provision/
3 validators/drift/
4 schemas/records/
4 metrics/
4 tools/records/
5 access/
5 infra/
5 ops-vm/
5 notify/
5 assets/
0 contracts/
0 CODEOWNERS
0 docs/
0 Makefile
EOF
```

### 5.2 Per-branch variables

```bash
set -euo pipefail
export BR="lane/2/phase1-ci"        # the branch under review, no origin/ prefix
export LANE="${BR#lane/}"; LANE="${LANE%%/*}"   # -> 2
git fetch origin --prune
export BASE="origin/integration"
export TIP="origin/$BR"
```

### 5.3 Register A commands

```bash
set -euo pipefail
# A1 — BR-01 productisation scope drift
git diff --name-only "$BASE...$TIP" | grep -Ei '(^|/)(install|installer|tenant|tenancy|multi.?tenan|upgrade|license-server)' \
  && echo "A1 FAIL productisation-shaped path" || echo "A1 OK"

# A2 — BR-02 evidence plumbing before dashboards
if git diff --name-only "$BASE...$TIP" | grep -qE '^(metrics/|.*dashboard)'; then
  git ls-tree -r "$BASE" --name-only | grep -q '^schemas/records/' \
    && echo "A2 OK" || echo "A2 FAIL dashboard/metric ahead of records schemas"
else echo "A2 OK (n/a)"; fi

# A3 — BR-03 exception without expiry / owner / deactivation trigger
git show "$TIP:registries/exceptions.yaml" 2>/dev/null \
  | grep -cE '^\s*(expiry|owner|deactivation_trigger):' \
  | awk '{ if ($1 % 3 == 0 && $1 > 0) print "A3 OK"; else print "A3 FAIL incomplete exception entry" }'

# A4 — BR-04 plan-checker pinned-release verification record present
# Run inside the control-plane-records clone (not control-plane).
# EC-9 writes the record to records/decisions/plan-checker-capability-verification.yaml there.
git fetch origin
git ls-tree -r origin/main --name-only | grep -q '^records/decisions/plan-checker-capability-verification' \
  && echo "A4 OK" || echo "A4 FAIL no plan-checker capability verification decision record"

# A5 — BR-05 / BR-11 negative execution of protection checks
git grep -lE 'executed negatively|negative case|expect_fail' "$TIP" -- access/ infra/ 2>/dev/null \
  | wc -l | awk '{ if ($1>0) print "A5 OK "$1" negative checks"; else print "A5 FAIL no negatively-executed protection check" }'

# A6 — BR-06 reconciler repair path ahead of its gates
git diff --name-only "$BASE...$TIP" | grep -q '^reconciler/.*repair' \
  && { git grep -lE 'AT-102|AT-110' "$TIP" -- reconciler/ >/dev/null \
       && echo "A6 REVIEW repair path present, gates cited — verify AT-102/AT-110 executed" \
       || echo "A6 FAIL repair path with no AT-102/AT-110 evidence"; } \
  || echo "A6 OK (detect-only)"

# A7 — BR-07 signal row missing arming discipline (D77)
git show "$TIP:registries/os-health.yaml" 2>/dev/null | awk '
  /^  - id: SIG-/ {id=$3; dep=0; win=0}
  /activation_dependency:/ {dep=1}
  /lookback_window:/ {win=1}
  /^  - id: SIG-/ && NR>1 { if (prev!="" && (pdep==0||pwin==0)) print "A7 FAIL "prev }
  {prev=id; pdep=dep; pwin=win}
  END { if (prev!="" && (pdep==0||pwin==0)) print "A7 FAIL "prev; print "A7 scan complete" }'

# A8 — BR-08 people datasource in the shared Grafana provisioning (D75, AT-097)
git grep -lEi 'people|layer.?b' "$TIP" -- 'ops-vm/grafana/shared/**' 2>/dev/null \
  && echo "A8 FAIL people reference in shared instance" || echo "A8 OK"

# A9 — BR-09 hand-maintained metric source (invariant #46)
git grep -nE 'source:\s*(manual|hand|spreadsheet|csv)' "$TIP" -- metrics/ 2>/dev/null \
  && echo "A9 FAIL hand-maintained metric source" || echo "A9 OK"

# A10 — BR-10 ops-vm artifact with no tool register entry
git diff --name-only "$BASE...$TIP" | grep -q '^ops-vm/' \
  && { git show "$TIP:registries/tools.yaml" 2>/dev/null | grep -q 'ops-vm' \
       && echo "A10 OK" || echo "A10 FAIL ops-vm artifact without tools.yaml entry"; } \
  || echo "A10 OK (n/a)"

# A11 — BR-13 registry value inferred from the spec instead of captured
for v in $(git show "$TIP:registries/people.yaml" 2>/dev/null | grep -oE 'github_login:\s*\S+' | awk '{print $2}'); do
  grep -qF "$v" "$SPEC" && echo "A11 REVIEW '$v' also appears in the spec — confirm it was captured, not inferred"
done; echo "A11 scan complete"
```

### 5.4 Register B commands

```bash
set -euo pipefail
# B1 — AX-01 silent divergence: concept tokens duplicated across lanes, absent from contracts/
for L in 1 2 3 4 5; do
  for b in $(git branch -r --list "origin/lane/$L/*" --format='%(refname:short)'); do
    git diff --name-only "$BASE...$b"
  done | xargs -r -n1 basename | sed 's/\.[^.]*$//' | sort -u
done | sort | uniq -d > "$AUDIT/dup.txt"
while read -r tok; do
  git ls-tree -r "$BASE" --name-only -- contracts/ | grep -q "$tok" || echo "B1 DIVERGENCE $tok"
done < "$AUDIT/dup.txt"; echo "B1 scan complete"

# B2 — AX-02 contract drift. Expected: every lane branch prints the frozen SHA.
FROZEN=$(cat "$AUDIT/contracts.frozen")
for b in $(git branch -r --list 'origin/lane/*' --format='%(refname:short)'); do
  cur=$(git rev-parse "$b:contracts" 2>/dev/null || echo MISSING)
  [ "$cur" = "$FROZEN" ] && echo "B2 OK       $b" || echo "B2 DRIFT    $b $cur"
done

# B3 — AX-03 invented scope. task-files.txt = the task file's declared output list, one path per line.
git diff --name-only --diff-filter=A "$BASE...$TIP" | sort > "$AUDIT/added.txt"
sort "$AUDIT/task-files.txt" > "$AUDIT/declared.txt"
comm -13 "$AUDIT/declared.txt" "$AUDIT/added.txt" \
  | sed 's/^/B3 UNDECLARED /' | grep . || echo "B3 OK 0 undeclared"

# B4 — AX-04 hallucinated path references. Expected: "B4 OK 0 unresolved"
git ls-tree -r "$TIP" --name-only > "$AUDIT/tree.txt"
n=0
for f in $(git diff --name-only "$BASE...$TIP"); do
  for p in $(git show "$TIP:$f" 2>/dev/null \
      | grep -oE '[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.(ya?ml|json|sh|py|md)' | sort -u); do
    grep -qxF "$p" "$AUDIT/tree.txt" || { echo "B4 UNRESOLVED $f -> $p"; n=$((n+1)); }
  done
done
if [ "$n" -eq 0 ]; then echo "B4 OK $n unresolved"; else echo "B4 FAIL $n unresolved"; exit 1; fi

# B5 — AX-05 verified at tip. Expected: VERIFIED-AT-TIP
run=$(gh run list --branch "$BR" --limit 1 --json headSha -q '.[0].headSha' 2>/dev/null)
[ -n "$run" ] && [ "$run" = "$(git rev-parse "$TIP")" ] \
  && echo "VERIFIED-AT-TIP" || echo "STALE-OR-UNVERIFIED"

# B6 — AX-06 silent partial completion. Expected: "PASS N/N" then "0 stubs 0 placeholders"
run=$(gh run list --branch "$BR" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null)
gh run view "$run" --log 2>/dev/null | grep -oE 'PASS [0-9]+/[0-9]+' | tail -1
stubs=0; for f in $(git diff --name-only --diff-filter=A "$BASE...$TIP"); do
  [ "$(git show "$TIP:$f" | wc -l)" -lt 3 ] && { echo "B6 STUB $f"; stubs=$((stubs+1)); }
done
ph=$(git grep -cEi 'TODO|TBD|FIXME|placeholder|lorem' "$TIP" -- \
      $(git diff --name-only "$BASE...$TIP") 2>/dev/null | wc -l)
echo "$stubs stubs $ph placeholders"

# B7 — AX-07 merge-train starvation
for L in 1 2 3 4 5; do
  last=$(git log "$BASE" --merges --grep="lane/$L/" -1 --format=%cI 2>/dev/null)
  printf 'B7 L%s last-merge %s\n' "$L" "${last:-NEVER}"
done

# B8 — AX-08 blocked lanes
gh issue list --label blocker --state open \
  --json number,title,createdAt,labels -q '.[] | "B8 \(.number) \(.createdAt) \(.title)"'

# B9 — AX-09 integration debt. Expected: small count, recent oldest.
echo "B9 unpromoted commits: $(git rev-list --count origin/main..origin/integration)"
echo "B9 oldest unpromoted:  $(git log origin/main..origin/integration --format=%cI | tail -1)"

# B10 — AX-10 foreign-path edit. Expected: "B10 OK"
fail=0
for p in $(git diff --name-only "$BASE...$TIP"); do
  owner=$(awk -v P="$p" '{ if (index(P,$2)==1) print $1 }' "$AUDIT/ownership.txt" | head -1)
  [ -z "$owner" ] && { echo "B10 UNOWNED $p"; fail=1; continue; }
  [ "$owner" = "$LANE" ] || { echo "B10 FOREIGN $p (owner L$owner)"; fail=1; }
done; [ "$fail" = 0 ] && echo "B10 OK"

# B11 — AX-11 shared mutable file across lanes
for L in 1 2 3 4 5; do
  for b in $(git branch -r --list "origin/lane/$L/*" --format='%(refname:short)'); do
    git diff --name-only --diff-filter=M "$BASE...$b" | sed "s|^|$L |"
  done
done | sort -k2 | awk '{ if ($2==prev && $1!=pl) print "B11 SHARED "$2" (L"pl", L"$1")"; prev=$2; pl=$1 }'
echo "B11 scan complete"

# B12 — AX-12 cross-lane import. Expected: "B12 OK"
hit=0
added=$(git diff --name-only --diff-filter=A "$BASE...$TIP")
if [ -n "$added" ]; then
  while read -r own pfx; do
    [ "$own" = "$LANE" ] && continue; [ "$own" = "0" ] && continue
    git grep -nF "$pfx" "$TIP" -- $added 2>/dev/null \
      && { echo "B12 CROSS-LANE-IMPORT $pfx (L$own)"; hit=1; }
  done < "$AUDIT/ownership.txt"
fi
[ "$hit" = 0 ] && echo "B12 OK"

# B13 — AX-13 fabricated citations. Expected: "0 fabricated"
git grep -hoE '\b(AT-[0-9]{3}|SIG-[0-9]{2}|D[0-9]{1,3})\b' "$TIP" -- \
  $(git diff --name-only --diff-filter=A "$BASE...$TIP") 2>/dev/null | sort -u \
| awk '
  /^AT-/ { n=substr($0,4)+0; if (n<1 || n>110) { print "B13 FABRICATED "$0; c++ } ; next }
  /^SIG-/ { n=substr($0,5)+0; if (n<1 || n>47) { print "B13 FABRICATED "$0; c++ } ; next }
  /^D/    { n=substr($0,2)+0; if (n<1 || n>114) { print "B13 FABRICATED "$0; c++ } ; next }
  END { print (c+0)" fabricated" }'

# B14 — AX-14 branch age and lag
for b in $(git branch -r --list 'origin/lane/*' --format='%(refname:short)'); do
  age=$(( ( $(date +%s) - $(git log -1 --format=%ct "$b") ) / 3600 ))
  behind=$(git rev-list --count "$b..$BASE")
  printf 'B14 %-28s age_h=%-4s behind=%s\n' "$b" "$age" "$behind"
done

# B15 — AX-15 records repo append-only. Run inside the control-plane-records clone.
# ANCHOR = the head SHA recorded at the previous cycle.
ANCHOR=$(cat "$AUDIT/records.anchor" 2>/dev/null)
git fetch origin
if [ -n "$ANCHOR" ] && git merge-base --is-ancestor "$ANCHOR" origin/main; then
  echo "APPEND-ONLY-OK"; else echo "HISTORY-REWRITTEN"; fi
git rev-parse origin/main > "$AUDIT/records.anchor"; cat "$AUDIT/records.anchor"

# B16 — AX-16 unowned build surface. Expected: "B16 OK"
un=0
for p in $(git diff --name-only "$BASE...$TIP"); do
  awk -v P="$p" '{ if (index(P,$2)==1) found=1 } END { exit !found }' "$AUDIT/ownership.txt" \
    || { echo "B16 UNASSIGNED-SUBSYSTEM $p"; un=1; }
done; [ "$un" = 0 ] && echo "B16 OK"

# B17 — AX-17 lane-guard integrity. Expected: every branch prints the frozen SHA.
LG=$(cat "$AUDIT/laneguard.frozen")
for b in $(git branch -r --list 'origin/lane/*' --format='%(refname:short)'); do
  cur=$(git rev-parse "$b:.github/workflows/lane-guard.yml" 2>/dev/null || echo MISSING)
  [ "$cur" = "$LG" ] && echo "B17 OK    $b" || echo "B17 ALTERED $b $cur"
done
```

### 5.5 Cadence

| When | Who | Runs |
| --- | --- | --- |
| Before opening any PR | The lane | `B3`, `B4`, `B10`, `B12`, `B13`, plus its own task self-verify |
| At each train slot, per PR | L0 | `B2`, `B5`, `B6`, `B10`, `B13`, `B16`, `B17`, plus the relevant `A*` |
| Once per cycle | L0 | `B1`, `B7`, `B8`, `B9`, `B11`, `B14`, `B15` |
| At each `integration` → `main` promotion | L0 | `B9`, gates G-A, G-B, G-C (§4) |

---

## 6. STOP rules for the five lanes

Copy this block verbatim into every lane task file. It is the complete list of conditions under which a lane stops. A lane facing anything on this list opens a blocker issue labelled `blocker`, naming the task id and the condition, and stops. It does not improvise, does not choose, does not ask another lane.

| # | If this is true | Do not proceed. Open a blocker issue saying |
| --- | --- | --- |
| S1 | The task names a file path that does not exist and the task does not say to create it | `blocked: path <p> missing, task <id> does not create it` |
| S2 | A command in the task fails, and the task does not describe that failure | `blocked: command <cmd> exited <n>, task <id> gives no branch for it` |
| S3 | Doing the task appears to require editing a path outside the lane's OWNS list | `blocked: task <id> requires <path>, owned by L<n>` |
| S4 | Something needed is absent from `contracts/**` | `contract-change-request: task <id> needs <concept>, absent from contracts/` |
| S5 | Two instructions in the task contradict each other | `blocked: task <id> steps <a> and <b> conflict` |
| S6 | The task requires choosing between options, naming a threshold, or deciding a format | `blocked: task <id> requires a decision — L0 input needed` |
| S7 | Fewer than all numbered acceptance criteria pass at the end | `incomplete: task <id> PASS n/N, criteria <list> unmet` |
| S8 | `B10` prints any `FOREIGN` or `UNOWNED` line | `blocked: lane-guard violation on <path>` |
| S9 | `B2` prints anything other than the frozen contracts SHA | `blocked: contracts tree differs from frozen value` |
| S10 | The branch is more than 24 hours old | `stale-branch: task <id>, request reissue on fresh branch` |

A lane never: edits `contracts/**`; merges or rebases another lane's branch; force-pushes to any branch; adds a shared index, list or catalogue file; writes a spec identifier not supplied in its own task file; marks a task complete with `n<N`.

---

## 7. L0 decisions required

### DEC-01 — Five subsystems have no lane

> **Superseded by FD-002 — see `Code/implementation/_FOUNDER_DECISIONS.md`.**

**Fact.** Spec Section 99.2 enumerates eighteen subsystems, A through R. PARTITION.md assigns thirteen: A, B (L1); E, F (L2); C, D (L3); I, N (L4); K, L, M, Q, R (L5). Unassigned: **G** plan-checker and Gate 1 tooling; **H** dashboards and views; **J** background machine layer (conditional, gated on the CPU benchmark per Section 98.2 Phase 3 and D69); **O** governance registries and jobs; **P** people intelligence engine.

**Why it must be answered before the first cycle.** Two of the five carry Register A rows: G carries BR-04 (plan-checker dependency volatility) and O carries the exception lifecycle behind BR-03 (bootstrap gates staying stubbed). AX-16 blocks any lane branch that touches an unassigned path, so with no answer the work simply does not happen and the omission is invisible until a phase completion check fails.

**Options. L0 chooses; this file does not.**

1. **Leave all five with L0.** H (dashboards, provisioned JSON), O (governance registries) and P (people intelligence) are all downstream of lanes that must land first; L0 builds them serially after the Foundation train stabilises. Cost: L0 becomes the critical path from mid-programme. Consistent with PARTITION as frozen — no lane table change.
2. **Extend three existing lanes by adding owned paths, without adding a lane.** Candidate mapping, following the spec's own dependency spine (`A → B → C/D`; `E → F → H/I`; `I` feeds governance computation): O to L1 (registry-shaped, sits beside `registries/**`), H to L4 (dashboards read the metrics L4 builds), P deferred entirely per Section 99.4 item 9. G and J stay with L0 — G because Section 99.3 item 3 marks plan-checker internals design-open, J because it is benchmark-gated. Cost: amends the frozen partition, which requires an explicit re-freeze and a new CODEOWNERS generation.
3. **Defer four, assign one.** Per Section 99.4 (the minimal honest V1), H beyond the Founder view v0, J, and P are explicitly deferred, and O reduces to the exception registry alone — which is a registry, so it goes to L1. G stays with L0. Cost: lowest scope, but BR-04's in-house-fallback budget must be scheduled explicitly or it will not exist when the pinned-release verification fails.

**Constraint on any option.** Section 99.3 item 3 (plan-checker internals) and item 1 (the attention classifier, feeding P) are design-open in the spec. Neither may be assigned to a lane in any form, because PARTITION's AI-developer profile forbids a task that requires designing. They are L0 work under every option.

**Until answered:** no lane task may name a path outside the five OWNS lists, and `B16` is Blocking.

---

### DEC-02 — The lane-guard check sits inside L2's exclusive path

> **Superseded by FD-003 — see `Code/implementation/_FOUNDER_DECISIONS.md`.**

**Fact.** PARTITION states the partition is enforced by "CODEOWNERS + the lane-guard CI check". `CODEOWNERS` is L0-owned. CI checks live under `.github/workflows/**`, which PARTITION assigns exclusively to L2. As frozen, L2 owns the workflow that polices all five lanes, and an L2 agent can alter it without touching a foreign path — so the guard raises no violation about itself.

**Why it must be answered before the first cycle.** The lane-guard check is the single mechanical control behind PARTITION rule 1, which is the reason merges cannot conflict. If it is weakened, AX-10, AX-11 and AX-16 all lose their detection at once, and the loss is silent.

**Options. L0 chooses; this file does not.**

1. **Named-file carve-out.** `.github/workflows/lane-guard.yml` (and only that file) is L0-owned, entered in `CODEOWNERS` as an L0 path and excluded from L2's OWNS glob. Smallest change; makes the OWNS column a glob-with-one-exception rather than a clean prefix, which every ownership-matching command in §5 must then honour.
2. **Move the guard out of the repository under test.** The check runs as a reusable workflow held in a separate L0-controlled repository and consumed by pinned tag — the same mechanism the spec already uses for the reusable workflow library and its canary/rollback unit (Section 99.5, "reusable workflows consumed by pinned tag"; invariant #85). The workflow file in `control-plane` becomes a two-line caller that pins a tag, and moving the pin is itself a detectable change. Strongest separation; adds a repository.
3. **Accept and detect.** Leave ownership as frozen; L0 pins the guard's blob SHA at Phase 0 and runs `B17` at every train slot, treating any difference as Red (Blocking on `lane/2/*`). Zero structural change; detection is L0-manual and depends on `B17` actually being run every cycle, which is the same class of dependency the spec calls out at BR-03.

**Until answered:** option 3 is in force as the interim control, because it requires nothing to be built. `B17` runs at every train slot from Phase 0 onward.

---

## 8. Maintaining this register

* **Cadence.** Reviewed by L0 at the close of every merge cycle, alongside the cycle report. Scores are re-read against §1's frequency definitions using the cycle's actual counts, not impressions.
* **Adding a row.** A risk enters this register when it has (a) a stated mechanism, (b) a mitigation that already exists in PARTITION.md or the spec, and (c) a detection command whose expected clean output is written down. A risk without (c) is not a register row; it is an `L0 DECISION REQUIRED` block.
* **Closing a row.** A row closes only when its detection command has returned clean for two consecutive cycles **and** its mitigation is mechanical rather than procedural. A row whose mitigation is "L0 remembers to check" never closes; it stays Amber for the life of the programme. This mirrors the spec's own closure-quality rule (Section 53.6): a finding closed without evidence is reopened and counted as a closure-quality defect.
* **What this register may never do.** Redesign the lane partition, reassign an owned path, alter the merge-train order, or resolve a spec matter Section 99.3 marks design-open. Each of those is an `L0 DECISION REQUIRED` block and nothing else.
