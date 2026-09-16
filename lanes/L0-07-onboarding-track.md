# L0-07 — THE ONBOARDING TRACK (per-product, relative, serialised)

**Lane:** L0 Integrator · **Branches:** `l0/<phase>-<seq>-<slug>` → `integration` (`master/09-glossary-and-conventions.md` §4)
**Owns exclusively (and this file writes nothing else):** `docs/onboarding/**`, the `onboard-*.sh` root scripts, and appended `Makefile` targets — all inside L0's `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Executor:** an AI developer (Sonnet-4.6-class) for every task below. Steps that must happen inside a product repository or on a live system are marked **HUMAN STEP** and the executor's obligation is to record and verify the evidence, never to perform the step.
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — nothing here contradicts it.
**Upstream:** `master/04-phase-map.md` §2 (track vocabulary, `OT-*`), §4.3 (sync points `S0`–`S3`), §5 (calendar-gated items), §6.2 (what only *appears* concurrent). `master/00-MASTER-PLAN.md` §4.3 (Track O). This file is the executable half of both.

> **Why this file exists.** `master/INDEX.md` OPEN ITEM **G-9** states the gap in one sentence: *the onboarding track has no owner in the lane model* — `04` calls it "not a lane deliverable", `01` assigns the eight product repositories to "no lane", and yet `00` §6.2's Foundation definition-of-done requires every live product fully onboarded. Roughly two quarters of work sits in that hole. This file does not close G-9 by inventing a sixth lane. It closes it by putting the **track's control-plane machinery** — the floor checklist, the intake taxonomy, the sequencing computation, the relative-date resolver, the DevOps serialiser, the QA clock, the interim-rule gate — inside L0's own owned paths, where an AI developer can build it, and by routing every step that touches a product repository to a named human executor whose evidence this machinery then verifies.

---

## 0. Conventions every task in this file obeys

### 0.1 Shell and repository

POSIX `sh` / Git Bash, run from the control-plane repository root. Identical to `L0-03-merge-train.md` §1.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cd "$CP_ROOT"
git rev-parse --show-toplevel
gh auth status
```

| Symbol | Meaning | Set by |
|---|---|---|
| `$CP_ROOT` | local clone of `control-plane` | you, once per shell |
| `$OB_ROOT` | onboarding-track store root. **Unset in normal use** (defaults to `docs/onboarding`). Set only to point a checker at a fixture | per command |
| `<slot>` | a two-digit intake slot, `01`…`08` — see §2.3 | fixed by task L0-07-01 |

**GNU `date` is required.** Every relative-date resolution uses `date -u -d`. Prove it once, before L0-07-04:

**Commands**

```bash
date -u -d "2026-01-01 +2 weeks" +%Y-%m-%d      # expected: 2026-01-15
```

If that prints anything else, **STOP** and open `BLOCKER L0-07-04: GNU date unavailable` from `docs/escalation/BLOCKER.md`. Do not substitute another date tool; the resolver's output is an acceptance criterion in four tasks.

### 0.2 GIT PREAMBLE — run before the body of every task

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune
git checkout integration
git pull --ff-only
git status --porcelain          # expected: empty
```

If `git status --porcelain` prints anything, **STOP**. A dirty tree means a previous task did not finish. Do not stash, do not commit foreign changes.

### 0.3 GIT POSTAMBLE — run after the body of every task

Substitute the task's own branch, scope, subject and trailers. `<scope>` is one of `docs`, `root`, `makefile` and nothing else (`master/09-glossary-and-conventions.md` §5.3 — L0's row).

**Commands**

```bash
cd "$CP_ROOT"
git add -A
git status --porcelain          # review: every path must start docs/onboarding/, onboard-, or be Makefile
git commit -F- <<'MSG'
<type>(<scope>): <subject>

<body>

Task-Id: <task-id>
Lane: L0
Phase: <phase-token>
Spec: <citations>
AT: <at-ids or none>
Invariant: <invariant numbers or none>
Agent-Authored: true
Self-Verify: <command>
MSG
git push -u origin HEAD
gh pr create --base integration --title "<task-id>: <subject>" --body "See lanes/L0-07-onboarding-track.md <task-id>."
```

**Path assertion, mandatory before every commit.** This file may write only three path shapes. Run it and read it:

**Commands**

```bash
git diff --cached --name-only | grep -vE '^(docs/onboarding/|onboard-[a-z-]+\.sh$|Makefile$)' && echo "FOREIGN PATH - STOP" || echo "PATHS OK"
```

Anything other than `PATHS OK` is a **STOP**. Do not open the PR. Open a blocker naming the file and the owning lane from PARTITION.md.

### 0.4 The blocker template

Copy verbatim from `docs/escalation/BLOCKER.md` (created by task `L0-00-05`); the canonical text is `L0-00-charter.md` §7.1. Title `BLOCKER <task-id>: <one line>`, labels `blocker`, `lane-0`.

```text
TASK ID:        <e.g. L0-07-05>
LANE:           0
BRANCH:         l0/<phase>-<seq>-<slug>
STOPPED AT:     <the exact command or step number in the task that could not complete>

WHAT I WAS ASKED TO DO
<verbatim quote of the task step>

WHY I CANNOT PROCEED
<one of: forbidden action F-01..F-18 | undecided item C-01..C-12 | contract does not cover the case
 | acceptance criterion is not provable by any command | spec sentence reads two ways>

FORBIDDEN/UNDECIDED ID:   <F-nn or C-nn or L0D-nn or DR-L0-07-x, or NONE>
SPEC SENTENCE QUOTED:     <verbatim, with section number; or NONE>

EXACT OUTPUT OBSERVED
<paste the literal command and its literal output>

WHAT I DID NOT DO
I made no choice, wrote no default, left no TODO, and pushed no code past this point.

FILES TOUCHED SO FAR
<git status --porcelain output>
```

### 0.5 What the executor is forbidden to do in this file

| # | Forbidden | Route to |
|---|---|---|
| OB-F1 | Naming a product, guessing a product id, or filling any field of a `facts.tsv` | **DR-L0-07-D** |
| OB-F2 | Writing a calendar date into any onboarding **phase** or **deadline** field | **DR-L0-07-G**; the resolver of L0-07-04 is the only writer of resolved dates |
| OB-F3 | Reordering `OT-P4` … `OT-P7` for any product | §96.5 makes sequencing a recorded L0 decision; file the note, stop |
| OB-F4 | Deciding whether a product is "worth onboarding at full standard" (state S13) | L0; Spec §18 lifecycle |
| OB-F5 | Performing, or asserting the result of, any step inside a product repository | The named executor of that floor row; you record the evidence |
| OB-F6 | Editing `exceptions.yaml`, `templates/**`, `registries/**`, or any product repository | **DR-L0-07-A**, **DR-L0-07-B**; PARTITION rule 1 |
| OB-F7 | Changing a calibrated value — the 14-day QA SLA, the 90-day restore window, any threshold | `L0-00-charter.md` §6.2 item **L0D-17** |
| OB-F8 | Declaring the floor, an assessment, a phase or the track "done" on any evidence other than the gate command's own output | Spec §96.6: *"a floor declared done on paper is exactly the invisible half-adoption 96.4 exists to catch"* |

---

## 1. Vocabulary — and the label collision, stated once

`master/INDEX.md` OPEN ITEM **C-18** records three competing label schemes for the same four onboarding phases. This file uses **exactly one**: the `OT-*` scheme of `master/04-phase-map.md` §2, because that is the file this track was told to inherit its vocabulary from. Every other scheme appears here only in this cross-map, and never again.

| This file (`04` §2) | `master/00-MASTER-PLAN.md` §4.3 | Spec §98.2 | What it is |
|---|---|---|---|
| `OT-FLOOR` | Track M item **M-7** | §96.6 universal floor | Nine items × every live product. Starts at `BT-0`. Waits for nothing |
| `OT-INTAKE` | "Intake gap assessment (precedes everything)" | §96.6 | One recorded assessment per product, written by a human assessor (**D72**) |
| `OT-P4` | `O-4` | Phase 4 — Environments | Local contract, staging with parity, environments with scoped secrets, parity job |
| `OT-P5` | `O-5` | Phase 5 — Verification | AI drafts the suite; QA reviews, corrects and takes ownership; `uat.md`; smoke; CI runs the contract |
| `OT-P6` | `O-6` | Phase 6 — Delivery Pipeline | Immutable artifact + digest + SBOM; staging deploy + smoke; production approval gate; rollback exercised; restore test recorded |
| `OT-P7` | `O-7` | Phase 7 — GSD Activation | GSD Core at a pinned tag; `.planning/`; constitution in `CONTEXT.md`; model routing |

Build-track milestones this track depends on are the **sync points** of `04` §4.3 — `S0`, `S1`, `S2`, `S3` — not `00`'s `B0`…`B7`. Where `00` §4.3 names finer-grained consumption (`O-4` consumes `B2`, `B3`, `B6`), those all land inside `S3` in `04`'s grid, so `S3` is the conservative gate and the one this file resolves against.

> **`O-4` means two different things in the document set.** In `master/02-branch-merge-model.md` §6 the token `O-4` is a lane-developer *command step number* ("rebase onto integration"). That is C-18's second half. Inside this file `O-4` never appears; the phase is `OT-P4`.

---

## 2. The store — what this track writes, and where

### 2.1 Path ownership

Every artifact this file produces lives under **`docs/onboarding/`** or is an **`onboard-*.sh` root script** or an appended **`Makefile`** target. All three are L0-owned (PARTITION.md line 22: *"`contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile`"*).

**No lane's path is touched.** In particular this track never writes `registries/**` (L1), `.github/workflows/**` (L2), `reconciler/**` or `tools/provision/**` (L3), `records/**` or `metrics/**` (L4), or `access/**` (L5). Where the onboarding track needs one of those surfaces it consumes it, and where the surface has no owner it stops — see §12.

### 2.2 Directory-per-item, because PARTITION rule 3 says so

PARTITION rule 3: *"No shared mutable file, ever. No lane appends to a shared index, list, or registry-of-everything. Directory-per-item only."* The floor is 72 obligations and the taxonomy is 19 states; both are the exact shape that tempts a single big table. Neither gets one. The human-readable tables in `docs/onboarding/README.md` are **generated** from the per-item files by `make onboard-report` and are never hand-edited — Spec §101 #46: *"Derived data is computed, never hand-maintained."*

```
docs/onboarding/
  README.md                              GENERATED between markers by onboard-report.sh
  floor/items/F1.tsv … F9.tsv            the nine universal-floor items (Spec §96.6), transcribed once
  taxonomy/states/S01.tsv … S19.tsv      the nineteen starting states, transcribed once
  taxonomy/notes/N1.tsv N2.tsv           the two intake notes that travel with the taxonomy
  anchors/S0.tsv S1.tsv S2.tsv S3.tsv    build-track milestone anchor dates — L0 input, initially UNSET
  anchors/OT-P4-01.tsv …                 per-product phase anchors, written as each phase actually starts
  rank/01.tsv … 08.tsv                   GENERATED sequence (Spec §96.5 ordering)
  stream/claims/001-*.tsv …              append-only DevOps-stream claim log (Spec §73.1)
  products/<slot>/facts.tsv              L0 input: identity, both criticalities, cost band, profile
  products/<slot>/states.tsv             which S-ids the recorded assessment found
  products/<slot>/floor/F1.tsv … F9.tsv  this product's nine floor rows: executor, date, status, evidence
  products/<slot>/gates.tsv              the S10 and S19 AI-safety gates
  products/<slot>/assessment.tsv         the intake gap assessment register row
  products/<slot>/interim.tsv            pre-onboarding block presence; accepted risks; contract presence
  products/<slot>/qa.tsv                 the QA-takeover SLA clock
  products/<slot>/cd-gate.tsv            only for a product carrying state S3
  products/<slot>/deadline.tsv           source expression and resolved deadline
  products/<slot>/plan.tsv               GENERATED per-product phase plan
  fixtures/<case>/…                      golden fixtures the SELF-VERIFY blocks run against
```

**File format, everywhere:** UTF-8, LF endings, one `key<TAB>value` pair per line, no quoting, no comments except a leading `#` line in generated tables. Every unsupplied value is the literal token `UNSET` — never blank, never a guess. `UNSET` is what makes "L0 has not answered yet" mechanically distinguishable from "the answer is empty", and every checker in this file counts it.

### 2.3 The eight intake slots

There are eight live products (`master/00-MASTER-PLAN.md` §1: *"approximately eight products today"*; Spec §96.6: *"at eight products seventy-two tracked obligations"*). **This file does not know their names and must never invent one.** The store therefore fixes eight numbered slots — `01` … `08` — and the real product identity arrives as the `product_id` field of `facts.tsv`, authored by L0 under **DR-L0-07-D**.

A slot is not a rank. Slot numbers are arbitrary and stable; **rank** is computed from the slot's facts by the §96.5 ordering in L0-07-09, and lives in `docs/onboarding/rank/`.

---

## 3. The relative clock — D99, made mechanical

**D99, binding:** *"The phases split into a Build track dated by subsystem with its complexity band, and an Onboarding track whose per-product phases are relative to the subsystems they consume. Pre-onboarding deadlines are set from the Onboarding track, not from the labels."*

`master/00-MASTER-PLAN.md` §4.3 states the operative consequence: *"Every `deadline` field in a product's pre-onboarding block (Section 96.2) is derived from that product's position in the Track O sequence and the Track B milestones it consumes — never from 'Weeks 4–5'. A deadline set from a label is a deadline that will breach, and a breached deadline is Red under Section 96.4."*

So this track stores **expressions**, not dates. An expression is:

```
<TOKEN>[+<N>w]
```

| Token family | Examples | Anchored by |
|---|---|---|
| Build-track sync point | `S0`, `S1`, `S2`, `S3` | L0, when the sync point is declared passed (`04` §4.3) |
| Per-product phase start | `OT-P4-03`, `OT-P6-07` | This track, when that phase actually begins for that slot |
| Floor | `OT-FLOOR` | L0, at `BT-0` |

`onboard-when.sh` (L0-07-04) is the **only** writer of a resolved date. Until L0 publishes an anchor, every expression resolves to the literal string `UNANCHORED`, and `UNANCHORED` propagates: an unanchored phase produces an unanchored deadline, and the track report renders the expression rather than a number. **That is the correct behaviour, not a defect.** A resolved date that nothing anchored is exactly the failure D99 exists to prevent.

`onboard-when.sh --lint` is the enforcement: it fails any store file containing an absolute week label (`Week 4`, `weeks 4-5`, `week-7`). It runs in the track gate of L0-07-14.

### 3.1 The one place absolute dates are correct

**Floor rows carry real calendar dates.** Spec §96.6: the floor is *"a checklist artifact with one row per item per product, each row carrying a named executor drawn from the product's existing team (Section 95.4) and a date"*, and *"Nothing on the floor waits for onboarding."* The floor consumes no build-track subsystem, so it has nothing to be relative to. `OT-FLOOR` starts at `BT-0` (`04` §2) and its 72 rows are dated in the ordinary way.

The distinction is the whole of D99 in one line: **floor rows are dated; onboarding phases and pre-onboarding deadlines are expressed.**

---

## 4. The DevOps serialiser — Spec §73.1

Spec §73.1, in the staffing-diagnosis chain, and binding on this track:

> *"Brownfield onboarding and platform work serialise on DevOps capacity — only one such stream can proceed at a time — and the staffing diagnosis treats this serialisation as its own constraint shape, distinct from aggregate engineering demand."*

This is not advice. It is a capacity fact with a mechanical consequence: **at most one stream holds the DevOps capacity at any moment**, where a stream is either one product's onboarding phase or one platform-work item. `onboard-stream.sh` (L0-07-10) implements it as an append-only claim log with a single-holder rule, and refuses a second concurrent claim.

### 4.1 Which onboarding phases occupy the stream

| Phase | Occupies the DevOps stream? | Why |
|---|---|---|
| `OT-FLOOR` | **No** | Nine items executed by each product's own named executor (Spec §95.4). It runs alongside `BT-0`/`BT-1` and consumes L0 and per-product-team attention, not DevOps capacity (`04` §6.2) |
| `OT-INTAKE` | **No** | An assessment written by a human assessor against the template (**D72**) |
| `OT-P4` Environments | **Yes** | Provisioning staging with parity, GitHub Environments with scoped secrets, the parity job — Spec §98.2 Phase 4 |
| `OT-P5` Verification | **No — QA instead** | The suite is AI-drafted; the constraint is the QA takeover, §8 below |
| `OT-P6` Delivery Pipeline | **Yes** | Artifact build, deploy workflows, approval gate, rollback exercise, restore test — Spec §98.2 Phase 6 |
| `OT-P7` GSD Activation | **No** | Pinned-tag install and configuration, days (Spec §98.2 Phase 7) |
| Platform work | **Yes** | Spec §73.1 names it in the same breath as brownfield onboarding |

### 4.2 The consequence, computed

Two stream occupancies per product. At eight products that is **sixteen serialised stream occupancies**, and platform work queues in the same line.

| Quantity | Source | Value |
|---|---|---|
| `OT-P4` duration, per product | `00` §4.3 ("1–2 weeks"), from Spec §98.2 Phase 4 | 1–2 weeks |
| `OT-P6` duration, per product | `00` §4.3 ("~1 week"), from Spec §98.2 Phase 6 | ~1 week |
| Stream occupancy, per product | sum of the two | **2–3 weeks** |
| Stream occupancy, eight products | × 8 | **16–24 weeks** |
| QA occupancy, per product | Spec §96.6 QA-takeover SLA | ≤ 2 weeks from suite landing |
| QA occupancy, eight products | × 8, QA is one person (Spec §99.6) | **≤ 16 weeks** + drafting |

`OT-P5` for rank *k* runs while the stream serves rank *k+1*'s `OT-P4`, so the two constraints pipeline rather than add. Track wall-clock is therefore **`max(stream total, QA total)` plus the tail**, and at eight products the stream total is the larger of the two.

> **This refines `04` §6.2, it does not contradict it.** `04` §6.2 says onboarding wall-clock is *"bounded by QA"* and cites Spec §99.6 naming QA *"the most acute single-person dependency in the model"*. Both statements hold: QA is the most acute **single-person** dependency, and the DevOps stream is the **binding serial constraint** at eight products because each product occupies it twice. Where the two disagree numerically, the larger governs, and any platform work admitted to the stream moves the stream total up and never down. The published point estimate is L0's, under **D-PLAN-03** (`master/00-MASTER-PLAN.md` §12). No task in this file publishes one.

---

## 5. The universal floor — nine items, seventy-two obligations

Spec §96.6: *"It is the six §96.2 items verbatim … plus the portfolio-wide Phase 1 actions … The floor is **nine items across every live product**, which at eight products is seventy-two tracked obligations."*

| Id | Item | Source | Meaning (Spec §96.2 / §98.2 Phase 1) |
|---|---|---|---|
| `F1` | Backups verified | §96.2 | A backup exists, and one restore has been performed and recorded, even if the full rotation cadence is not yet running. Before Phase 3 there is no Primary Owner, so the block's named `maintainer` and `escalation` pair confirm instead. This recorded restore is the one the `OT-P6` rotation entry cites, not a second restore six weeks later |
| `F2` | Access inventoried | §96.2 | Every credential, admin account and deploy path is listed; no unknown access remains |
| `F3` | Alerting attached | §96.2 | At minimum an uptime check and an error-rate alert route to the standard alert channel |
| `F4` | Accepted risks recorded | §96.2 | Every rule not yet met is written down as an accepted risk with an owner, and mirrored into the exception registry (**DR-L0-07-B**) |
| `F5` | Named deadline | §96.2 | A dated onboarding completion target; missing it is a Red signal, not a silent slip — `SIG-38` |
| `F6` | Interim response authored | §96.2 | The required `interim_response:` stanza: how to redeploy today, where the last known-good build lives, which parts of the Spec §42.3 response flow are waived under which accepted risk |

> **HUMAN STEP** — Items F7–F9 are repository actions (§5.1). The named executor drawn from the product's existing team (Spec §95.4) must complete these steps inside the product repository or on live GitHub. The AI executor's obligation is to record and verify the evidence, never to perform the step (OB-F5).

| Id | Item | Source | Meaning (Spec §96.2 / §98.2 Phase 1) |
|---|---|---|---|
| `F7` | Repository moved into the organisation | §98.2 Phase 1 | The portfolio-wide consolidation action. This is state **S9**'s entire onboarding path |
| `F8` | Branch protection applied | §98.2 Phase 1 | From the template, required review and approval of the most recent reviewable push. **The required-status-check list starts empty per repository** and is populated as each check comes into existence |
| `F9` | Secrets out of the repository and inventoried | §98.2 Phase 1 | The S10 remedy: rotation of every exposed credential is mandatory and sufficient; a minimal Spec §43 incident record is always filed; purging history is optional and only via an authorised, recorded history-rewrite exception |

### 5.1 The estate is on the floor too

Spec §96.6, and **D69**: *"the hosts running Hermes Agent instances — the background worker harness, the PR-review engine and the founder ops console — are estate machines and meet the same six items from the day they exist … their `HERMES_HOME` directories are sensitive-at-rest and covered by the backup and access-inventory items like any other estate data."*

**Six items, not nine** — the §96.2 six (`F1`–`F6`), because `F7`–`F9` are repository actions and an estate host is not a repository. Estate hosts are not intake slots and do not enter the 72. They are tracked where the estate is tracked: `tools.yaml`, registered before first use (**D69**), which has no owning lane — see **DR-L0-07-E**.

### 5.2 The two hard AI-safety gates

Two taxonomy rows are not merely floor items; they are gates that make a repository **unavailable to any AI-assisted work at all**, onboarding included.

| Gate | Spec sentence | Consequence |
|---|---|---|
| **S10** | *"No AI-assisted session opens the repository until the S10 check passes — universal floor"* (§96.6, S10) | Every AI-assisted session on that repository is blocked. Spec §33 restates it for the packaging path: *"no AI-assisted session opens a repository until that repository's S10 committed-secrets check (Section 96.6) has passed"* |
| **S19** | *"No AI-assisted session opens the repository until the S19 check passes — universal floor"* (§96.6, S19) | Same rule, and Spec §101 #111 names the S19 intake gate as one of the three detectors that enforce *"No customer data in repositories"* |

`04` §8 DECISION 3 already says this out loud: *"A product failing either is unavailable to any AI-assisted work, including onboarding, until it passes."* `onboard-aigate.sh` (L0-07-06) is the mechanical form, and `onboard-interim.sh` (L0-07-13) consumes it.

**S10 and S19 are not symmetric, and the taxonomy is explicit about why.** For S10 rotation is the control and history-purging is optional. For S19 *"there is no rotation-equivalent remedy here, which is exactly why this check is mandatory and not deferred"* — the data must be removed from the working tree immediately, notification runs under the product's `data.regulatory_notification_hours` where the classification requires it, and purging history requires the authorised, recorded history-rewrite exception. Any deletion obligation for the exposed records is recorded in `records/deletion-requests/` (Spec §97.2) — which is L4's repository, not this track's; this track records only that the obligation exists and where.

Whether S19 is a **tenth** floor obligation or rides `F9` is genuinely ambiguous in the source and changes the denominator of the floor burn-down. It is **DR-L0-07-C**. Until L0 answers, the checklist is nine rows (Spec §96.6's own arithmetic: 9 × 8 = 72) and the S19 gate is tracked in `gates.tsv`, counted separately.

---

## 6. The intake taxonomy — nineteen states, and the path from each

Spec §96.6: *"States compose — a real product is usually in several at once; the assessment records all that apply."* So `states.tsv` holds a set, never a single value, and nothing in this track assumes one state per product.

| Id | Starting state | Immediate action (pre-onboarding) | Onboarding path | Prereq token |
|---|---|---|---|---|
| S1 | No CI and no CD — manual everything | Universal floor; releases recorded by hand as accepted risk | Full Phases 4–6: environments → verification → pipeline. The reusable workflow library means this is instantiation, not invention | — |
| S2 | CI only — tests run, deployment manual | Keep the existing CI; record manual deployment as accepted risk | Migrate CI onto the pinned reusable workflows; add artifact build with digest, environments, deploy workflows (Phase 6). Existing tests seed the verification contract. Phase 6 completion check includes: legacy deploy path disabled and its credentials revoked | — |

> **HUMAN STEP** — S3's immediate action requires the product team to gate the live production CD pipeline (disable auto-deploy, insert an approval webhook, or freeze it entirely). This must be done on the live system before any onboarding work proceeds. The AI executor records the chosen pattern and named approver in `cd-gate.tsv` (OB-F5).

| Id | Starting state | Immediate action (pre-onboarding) | Onboarding path | Prereq token |
|---|---|---|---|---|
| S3 | CD only — auto-deploy with no meaningful tests | **The most dangerous state.** Gate the existing CD immediately using one of the three named patterns of the interim-CD gating pattern library — (1) disable auto-deploy and name a manual deployer; (2) insert an approval webhook in front of the existing CD; (3) freeze CD entirely and deploy from artifact by hand — with the interim approver named in the onboarding block. Where none of the three can be applied at once, record continued operation as a Red accepted risk with the shortest deadline in the portfolio | Verification contract FIRST (Phase 5, out of normal order), then rebuild CD as the governed pipeline (Phase 6) | `cd-gate` |
| S4 | Local development only — nothing deployed, or deployed ad hoc | Universal floor; if something *is* serving users ad hoc, inventory how | Phase 4 creates staging and production as governed environments from the start — greenfield-like, often the cheapest onboarding | — |
| S5 | Local + production, no staging | Every change is currently verified in production or not at all — record as accepted risk; restore target is a throwaway environment, recorded in the block | Provision staging with parity (Phase 4); until parity passes, changes are treated as high-risk (progressive delivery preferred). Phase 6 completion check includes: legacy deploy path disabled and its credentials revoked | `restore-target` |
| S6 | A "UAT" environment only, or odd environment names | Map the existing environment to its true role — a UAT box that behaves like staging IS staging; rename in configuration, not in infrastructure | Fill the missing environments per Phase 4; the parity check tells the truth about whether the mapped environment actually matches production | `environment-mapping` |
| S7 | No tests at all | Accepted risk; no AI-assisted feature work on this product until a contract exists (the portfolio invariant) | Phase 5: AI drafts the automated suite during working hours, QA reviews, corrects and takes ownership; `uat.md` authored from how the product is actually exercised today | — |
| S8 | Not containerised / no reproducible build | Record build steps as they exist | Containerise during Phase 4 where practical; where genuinely impractical, the product must still produce an immutable, digest-identified artifact of some form — the digest invariant is not waivable, the packaging format is | — |

> **HUMAN STEP** — S9 requires a GitHub organisation administrator to transfer the product repository into the company org (live GitHub). S10 requires the product team to rotate every exposed credential in the live system and file the §43 incident record. Both must happen immediately on discovery. The AI executor records the evidence in `floor/F7.tsv` (for S9) and `gates.tsv` (for S10) — it never performs these steps (OB-F5).

| Id | Starting state | Immediate action (pre-onboarding) | Onboarding path | Prereq token |
|---|---|---|---|---|
| S9 | Repository on a personal account or outside host | Move into the organisation immediately — this is universal-floor, week 1, for every product at once | — (the floor is the whole path) | `repo-in-org` |
| S10 | Secrets committed in the repository or `.env` files | Treat as a live credential exposure. Rotation of every exposed credential is mandatory and sufficient; a minimal Spec §43 incident record is always filed. Purging the secret from history is optional and happens only via an authorised, recorded history-rewrite exception. **No AI-assisted session opens the repository until the S10 check passes** | Secret tiers applied at Phase 4 | `s10-gate` |
| S11 | No monitoring, no health endpoints | Universal-floor uptime check externally; endpoints come later | The three endpoints added during Phase 4 — deliberately trivial to implement in any stack | — |
| S12 | Mobile / store-delivered product | Nothing special pre-onboarding | Declare `conformance_profile: client-app` (Spec §15.7); standard path otherwise — store submission is the deploy step, release latency declared, heavier UAT mix declared in the contract | `profile-client-app` |
| S13 | Heavy tech debt / legacy stack nobody wants to touch | Assess honestly: is this product worth onboarding at full standard? | The lifecycle answer may be Maintenance (Spec §18) — reduced obligations, but the universal floor and restore testing still apply. Not every product must reach Level 3+; an internal tool held at Level 2 deliberately is a valid, *recorded* outcome (Spec §65) | `lifecycle-decision` |
| S14 | Already meeting most of the standard | Fast-track: intake assessment, contract authored, gaps closed | Days, not weeks — the assessment exists precisely so these products do not pay the full onboarding tax | — |
| S15 | Multi-product monorepo | Universal floor on the shared repository | Either split into per-product repositories, or declare a shared-repo product set: path-scoped branch protection and CI, and a per-product contract for each product in the repository. Product and Repository remain separate concepts either way | `shared-repo-decl` |
| S16 | Customer-hosted / on-premises production | Universal floor on what the company controls; record what it does not | Declare `conformance_profile: customer-hosted` (Spec §15.7): customer-attested deploy and restore records, or a recorded exemption with a compensating control | `profile-customer-hosted` |
| S17 | Library/SDK or batch pipeline — no serving interface | Universal floor | Declare `conformance_profile: library` or `batch` (Spec §15.7) and meet its equivalent evidence: registry version plus consumer contract tests, or job success and data-freshness signals | `profile-library-or-batch` |
| S18 | Platform-rebuild deployment — git-push to a PaaS that rebuilds per environment, so staging and production are separate platform builds and the byte-identical-digest invariant is structurally unsatisfiable there | Record the equivalent evidence as the product's immutable identity: the pinned commit SHA plus lockfile plus recorded build configuration (**D78**) | Replatforming to the container pipeline is the onboarding step wherever the product's `classification.reliability_criticality` demands the true digest chain; until then the recorded equivalent evidence is the identity the evidence chain cites | `equivalent-identity` |

> **HUMAN STEP** — S19 requires the product team to act inside the product repository immediately: remove the committed customer data from the working tree, trigger the regulatory notification process under `data.regulatory_notification_hours`, and (where required) authorise and record the history-rewrite exception. There is no rotation-equivalent remedy (§5.2). The AI executor records the evidence in `gates.tsv` and the deletion obligation reference — it never performs these steps (OB-F5).

| Id | Starting state | Immediate action (pre-onboarding) | Onboarding path | Prereq token |
|---|---|---|---|---|
| S19 | Customer data committed in the repository — production dumps, real call recordings, exported spreadsheets, support transcripts, or test fixtures built from live customer records | Treat as a live disclosure of customer data, not untidiness. Inventory what is present and where; notify under the product's `data.regulatory_notification_hours` where the classification requires it; remove the data from the working tree immediately. History is append-only, so purging it requires the authorised, recorded history-rewrite exception — there is no rotation-equivalent remedy. **No AI-assisted session opens the repository until the S19 check passes** | Fixtures replaced with declared-provenance fixtures (Spec §38.3); the `data:` block completed at Phase 4; any deletion obligation for the exposed records recorded in `records/deletion-requests/` (Spec §97.2) | `s19-gate` |

**The `Prereq token` column is authored here, not in the spec.** Each token exists only where the spec's immediate-action text names a specific artifact, record or declaration that must exist before the product's phases begin. The producing sentence is quoted in the row. Nothing is inferred from a row whose action is "universal floor plus an accepted risk" — those rows carry `—`, and the plan generator emits no prereq for them. This mapping is data, transcribed once in L0-07-03; the executor never derives a token.

### 6.1 The out-of-order note, and who may act on it

S3's onboarding path says *"Verification contract FIRST (Phase 5, out of normal order)"*. `master/00-MASTER-PLAN.md` §4.3 reads that as *"a product in starting state S3 takes O-5 before O-6, out of normal order"* — and the standard order `OT-P4 → OT-P5 → OT-P6 → OT-P7` already satisfies it. **So the plan generator never reorders anything.** It emits the standard order, plus a literal `NOTE` row carrying the spec sentence, and the real urgency of S3 lives where the spec puts it: in the *immediate* CD gating, which is a pre-onboarding action and is enforced by the `cd-gate` prereq, not by phase order. Reordering phases for any product is **OB-F3** and belongs to L0's §96.5 sequencing decision.

### 6.2 The two intake notes that travel with the taxonomy

Spec §96.6, final paragraph — recorded as `taxonomy/notes/N1.tsv` and `N2.tsv`, applicable to any slot regardless of state:

| Id | Note | Prereq token |
|---|---|---|
| `N1` | *"A store account owned by a personal Google or Apple account is the mobile-store analogue of the personal-hosting state (S9): transfer to the company account is scheduled at intake, or its absence is a dated accepted risk."* | `store-account-transfer` |
| `N2` | *"A production database shared between two products is declared at intake, and backup and restore ownership is assigned to a named product then — never left implicit between the two."* | `shared-db-ownership` |

### 6.3 A rendering artifact in the source table, recorded so nobody re-derives it

At spec line 8825 the S18 and S19 rows are emitted on a single physical line and the S19 row text then repeats. The taxonomy is **nineteen states, S1 through S19**, each appearing once. If a later reader counts twenty rows in the raw markdown, this is why. Nothing in this track derives a state id from row position; ids are transcribed literally.

---

## 7. The intake gap assessment

Spec §96.6: *"Onboarding therefore begins with a recorded **intake gap assessment** per product, authored from the named template artifact in the control plane (`templates/intake-gap-assessment.md`) so every assessment covers the same ground: current state measured against the target standard, every gap becoming either a scheduled onboarding step or an accepted risk with an owner and the named deadline."*

Four properties this track enforces mechanically:

1. **One recorded assessment per product**, stored beside the pre-onboarding block, and *"the input to the Section 98 per-product phase plan"* — so `onboard-plan.sh` refuses to generate a plan for a slot whose `assessment.tsv` is not `recorded`.
2. **The recorded assessment is always written by the human assessor** (**D72**). A machine draft is permitted — *"draft-only, on local inference, permitted only where the product's S10 gate allows machine processing of its metadata and `ai_processing_permitted` is set"* — and `assessment.tsv` distinguishes `machine_drafted` from `recorded_by`. A machine draft with no human `recorded_by` is not an assessment.
3. **Intake places each product at its honest maturity level** — Spec §65, *"usually 0 or 1"*, and *"onboarding is the climb"*. `assessment.tsv` carries `maturity_level_at_intake` from the closed set `0`–`7` (Spec §65).
4. **Regression-test follow-ups from a pre-onboarding incident land here** — Spec §96.3: they *"are routed into the product's intake gap assessment (Section 96.6) as scheduled onboarding steps, so the incident's lessons arrive with the product rather than evaporating."*

**The template has no owning path.** `templates/intake-gap-assessment.md` is named by the spec and appears in no lane's OWNS column — this is `04` §8 DECISION 2, already escalated. It is **DR-L0-07-A** here. This track consumes the template; it never writes it.

### 7.1 The target standard the assessment measures against

Spec §96.6's target-standard table, transcribed into `docs/onboarding/taxonomy/standard/T1.tsv` … `T10.tsv` by L0-07-07 so that an assessment can be checked for coverage:

| Id | Standard | Defined in |
|---|---|---|
| `T1` | Repository in the company organisation, branch protection from template | Spec §11 |
| `T2` | Valid `product.yaml` with ownership, criticality, support model | Spec §15 |
| `T3` | The eight make commands and required files | Spec §33.1 |
| `T4` | The three HTTP endpoints (`/health`, `/version`, `/metrics`) | Spec §41.2 |
| `T5` | Three environments (local, staging, production) with parity checked | Spec §33 |
| `T6` | Verification contract (automated, UAT, smoke; AI eval where declared) | Spec §31 |
| `T7` | Immutable-artifact pipeline, same digest staging → production | Spec §32–§34 |
| `T8` | CI-only migrations, backward-compatible one cycle | Spec §34.3 |
| `T9` | Backups with one verified restore; then the rolling cadence | Spec §44 |
| `T10` | Boards as execution truth; work through the gates | Spec §23–§29 |

Spec §96.6: *"The table states the standard for the default `service` profile; a product declaring a different `conformance_profile` (Section 15.7) meets the equivalent evidence its profile defines wherever the service interface does not apply."* The checker therefore reads `conformance_profile` from `facts.tsv` and, for a non-`service` profile, requires the row to be answered `equivalent` with the equivalent evidence named — never silently skipped.

---

## 8. The QA-takeover SLA — the `OT-P5` serialiser

Spec §96.6, the Phase-5 QA queue rule:

> *"Each product carries a **QA-takeover SLA** — initial calibrated value: two weeks from the AI-drafted suite landing to QA having reviewed, corrected and taken ownership — and a breached SLA is a QA-capacity signal at the weekly review, never a personal one."*

Spec §98.2 Phase 5's completion check repeats it, and §98.2's closing paragraph adds: *"Across Phases 5–7 the QA-takeover SLA (Section 96.6) paces the verification queue product by product."*

| Property | Value | Source |
|---|---|---|
| Clock starts | The AI-drafted suite **landing** for that product — not the phase start | Spec §96.6 |
| Duration | 14 days, the initial calibrated value of "two weeks" | Spec §96.6; changing it is **L0D-17** |
| Clock stops | QA has *reviewed, corrected and taken ownership* | Spec §96.6 |
| On breach | A **QA-capacity signal at the weekly review** — `SIG-08` (QA bottleneck: verification demand above sustainable capacity; Amber, Red on sustained breach) | Spec §52.2 |
| Never | A personal signal, and never an individual-performance input | Spec §96.6 |

`onboard-qa.sh` takes `--asof <YYYY-MM-DD>` so its verdict is deterministic and testable. A breach prints the signal id; it never prints a person.

---

## 9. The interim rule — what continues, and what waits

Spec §96.6, the sentence this track exists to keep honest:

> *"During Phases 4–5, **manual feature work on the product is permitted** under the recorded accepted risks of the pre-onboarding block; only AI-assisted feature work waits for the verification contract (the portfolio invariant). Onboarding does not freeze a live product's roadmap — it governs how the roadmap ships in the interim."*

Spec §98.2 restates it as applying *throughout* Phases 5–7. Spec §101 #1 is the portfolio invariant it names: *"No product completes onboarding without a verification contract; a live product not yet onboarded operates only under the declared pre-onboarding pathway of Section 96, with its absence recorded as an accepted risk with a named deadline."*

`onboard-interim.sh` (L0-07-13) answers two questions per slot, in this fixed order, and prints the first failing reason:

| Question | PERMITTED when | Otherwise |
|---|---|---|
| **Manual feature work?** | the pre-onboarding block is present **and** its accepted risks are recorded (`F4` closed) | `BLOCKED reason=no-recorded-accepted-risks` — not because onboarding forbids the work, but because §96.2's declared state does not yet exist, and Spec §96.2 admits no undeclared gap |
| **AI-assisted feature work?** | S10 gate passes **and** S19 gate passes **and** the verification contract is present | `BLOCKED reason=s10-gate` / `s19-gate` / `no-verification-contract`, in that order |

The order matters. S10 and S19 are checked **first** because they block *any* AI-assisted session on the repository, not merely feature work (§5.2). A product that has a verification contract but a failing S19 gate is still closed to AI-assisted work.

---

## 10. The per-product sequencing plan for eight products

### 10.1 The ordering function — Spec §96.5, transcribed

> *"Sequencing rule: highest `classification.reliability_criticality` first — the products where an ungoverned incident hurts most spend the least time in pre-onboarding mode. Within equal criticality, sequence by business.criticality, then by expected onboarding cost, cheapest first. The sequence and its deadlines are recorded as a decision and reviewed at the quarterly operating-system review."*

Three keys, in order, then a deterministic tie-break:

| Key | Field | Ordering | Vocabulary source |
|---|---|---|---|
| 1 | `reliability_criticality` | `critical` → `high` → `medium` → `low` | Spec §15.1 (`low \| medium \| high \| critical`) |
| 2 | `business_criticality` | `high` → `medium` → `low` | Spec §15.1 (`high \| medium \| low`) |
| 3 | `onboarding_cost_band` | `S` → `M` → `L` → `XL`, cheapest first | Spec §99.2 complexity bands (`S` under a week, `M` one to three weeks, `L` three to eight weeks, `XL` multi-month) |
| 4 | slot number ascending | — | **This file**, so the computation is total and reproducible. A tie-break is not a decision; it is the absence of one |

L0 authors the three field values per slot (**DR-L0-07-D**). The executor computes rank and **never estimates a cost band**.

### 10.2 The per-rank schedule, as expressions

This is the sequencing plan. It is parameterised on rank, not on product identity, which is why it can be written before **DR-L0-07-D** is answered. `k` is rank, `1`…`8`; `slot(k)` is the slot at rank `k`.

| Phase | Earliest expression | Gate | Serialiser | Duration |
|---|---|---|---|---|
| `OT-FLOOR` | `OT-FLOOR+0w` | none — starts at `BT-0` | product team attention, criticality order | its own declared duration; *"several weeks"* (Spec §96.6), **DECISION 3** in `04` §8 |
| `OT-INTAKE` | `OT-FLOOR+0w` | `templates/intake-gap-assessment.md` exists (**DR-L0-07-A**) | human assessor | 0.5–2 days per product (`00` §4.3) |
| `OT-P4` | `max(S3, OT-P6-slot(k-1))` | `S3` passed **and** `OT-INTAKE` recorded for this slot | **DevOps stream** | 1–2 weeks |
| `OT-P5` | `OT-P4-slot(k)+0w` | that slot's `OT-P4` complete | **QA takeover, ≤ 14 days from suite landing** | drafting + ≤ 2 weeks |
| `OT-P6` | `max(OT-P5-slot(k), S3)` | that slot's `OT-P5` complete | **DevOps stream** | ~1 week |
| `OT-P7` | `OT-P6-slot(k)+0w` | that slot's `OT-P6` complete **and** plan-checker available (**DR-L0-07-F**) | none | days |

**Why `OT-P4` for rank `k` waits on `OT-P6` for rank `k-1`:** because §4.1 puts both on the DevOps stream and Spec §73.1 permits one stream at a time. Rank `k`'s environments work cannot begin while rank `k-1`'s pipeline work still holds the stream. That single row is the whole reason eight products take roughly two quarters (Spec §96.1) rather than 3–4 weeks.

### 10.3 The wave picture

```
stream:  [P4 r1][P6 r1][P4 r2][P6 r2][P4 r3][P6 r3] … [P4 r8][P6 r8]   16 occupancies, strictly serial
QA:            [------P5 r1------][------P5 r2------] …                 ≤14d each, pipelined behind P4
P7:                     [r1]              [r2]        …                 days, off both constraints
floor:   [========= OT-FLOOR, all 8 products, criticality order =========]   parallel with BT-0/BT-1
```

Read three things off it, and say them out loud to anyone who asks why the track is not shorter:

1. **The floor is not inside the track's serial part.** It runs beside `BT-0`/`BT-1` and is finished, or explicitly carrying dated accepted risks, before any product's `OT-P4` starts.
2. **`OT-P5` never lengthens the track unless QA breaches.** It pipelines behind the stream. When it does lengthen the track, the cause is `SIG-08` and the remedy ladder is Spec §73.2's Verification row — *"verification automation and background-drafted suites; shift authoring to developers with QA reviewing; then hire QA"* — never "QA works faster".
3. **Any platform work admitted to the stream displaces a product.** That is Spec §73.1's serialisation, and it is why `onboard-stream.sh` takes `kind=platform` as a first-class claim rather than pretending platform work happens elsewhere.

### 10.4 Where each starting state changes the plan

Composition means a slot's plan is the standard six rows plus one prereq row per applicable state. Nothing is removed.

| If `states.tsv` contains | The plan gains | Enforced by |
|---|---|---|
| `S3` | prereq `cd-gate` — one of the three named patterns recorded, with the interim approver named in the onboarding block; or `pattern=none` and a Red accepted risk carrying **the shortest deadline in the portfolio** | `onboard-plan.sh` refuses to emit; `onboard-deadline.sh` checks the minimum |
| `S5` | prereq `restore-target` — the throwaway environment named in the block; **never production** | `onboard-plan.sh` |
| `S9` | prereq `repo-in-org` — satisfied by floor row `F7` and by nothing else | `onboard-floor.sh` |
| `S10` | prereq `s10-gate` — and the repository is closed to AI-assisted work until it passes | `onboard-aigate.sh`, `onboard-interim.sh` |
| `S12` / `S16` / `S17` | prereq `profile-*` — `conformance_profile` in `facts.tsv` matches the state's declared profile | `onboard-plan.sh` |
| `S13` | prereq `lifecycle-decision` — recorded, and **OB-F4**: the executor never makes it | `onboard-plan.sh` |
| `S15` | prereq `shared-repo-decl` — split, or a declared shared-repo product set | `onboard-plan.sh` |
| `S18` | prereq `equivalent-identity` — pinned commit SHA + lockfile + recorded build configuration (**D78**) | `onboard-plan.sh` |
| `S19` | prereq `s19-gate` — and the repository is closed to AI-assisted work until it passes | `onboard-aigate.sh`, `onboard-interim.sh` |
| `S6` | prereq `environment-mapping` — the existing environment mapped to its true role in configuration | `onboard-plan.sh` |
| `N1` / `N2` | prereq `store-account-transfer` / `shared-db-ownership` | `onboard-plan.sh` |

---

## 11. Tasks in this file

Fifteen tasks. Six transcribe a spec table into per-item files; nine build a checker. **Not one of them requires a
judgment**, because every judgment this track contains has been lifted out into §12 as a `DECISION REQUIRED` block.
The store is seeded entirely with the literal token `UNSET`, every checker fails closed on `UNSET`, and the burn-down
from "72 obligations open" to "72 obligations closed with evidence" is therefore a measurable quantity from the first
commit rather than a paragraph anyone can declare complete (Spec §96.6, L8802).

| Task id | Title | Size | Depends on |
|---|---|---|---|
| L0-07-01 | The onboarding store, the eight intake slots, and the `UNSET` discipline | M | L0-00-02 |
| L0-07-02 | The nine universal-floor items, and the seventy-two seeded obligation rows | M | L0-07-01 |
| L0-07-03 | The nineteen-state taxonomy, the two intake notes, and the prereq-token map | M | L0-07-01 |
| L0-07-04 | `onboard-when.sh` — the relative-date resolver and the absolute-label lint (D99) | L | L0-07-01 |
| L0-07-05 | `onboard-floor.sh` — the floor checker and the paper-floor detector | M | L0-07-02, L0-07-04 |
| L0-07-06 | `onboard-aigate.sh` — the S10 and S19 AI-safety gates, fail-closed and asymmetric | M | L0-07-03 |
| L0-07-07 | The ten-row target standard, and the per-slot coverage sheet | S | L0-07-01 |
| L0-07-08 | `onboard-assess.sh` — the intake gap assessment, and what is not an assessment | M | L0-07-07 |
| L0-07-09 | `onboard-rank.sh` — the §96.5 ordering function, total and reproducible | M | L0-07-01 |
| L0-07-10 | `onboard-stream.sh` — the single-holder DevOps serialiser (§73.1) | L | L0-07-01 |
| L0-07-11 | `onboard-plan.sh` — the per-product phase plan, composed from the states | L | T03, T04, T09, T10 |
| L0-07-12 | `onboard-qa.sh` — the QA-takeover SLA clock, and the signal that is never a person | M | L0-07-01, L0-07-04 |
| L0-07-13 | `onboard-interim.sh` — manual work continues; AI-assisted work waits | M | L0-07-06, L0-07-11 |
| L0-07-14 | `onboard-deadline.sh`, `onboard-gate.sh` and the `make onboard-*` targets — the track gate | L | T05, T06, T08, T11, T12, T13 |
| L0-07-15 | `onboard-report.sh` — the generated README, and the weekly track ritual | M | L0-07-14 |

Dependency graph:

```
L0-00-02 ── L0-07-01 ─┬── L0-07-02 ───────────────────┐
                        ├── L0-07-03 ─┬── L0-07-06 ────┤
                        ├── L0-07-07 ─── L0-07-08 ─────┤
                        ├── L0-07-09 ───────────────────┤
                        ├── L0-07-10 ───────────────────┤
                        └── L0-07-04 ─┬── L0-07-05 ────┤
                                       ├── L0-07-12 ────┤
                                       └── L0-07-11 ─┬──┴── L0-07-14 ── L0-07-15
                                                      └── L0-07-13 ─────┘
```

**Ordering note.** T01–T10 are independent of every Build-track milestone and of **DR-L0-07-D**: they build machinery
parameterised on rank and slot, never on product identity. That is deliberate. The track's control-plane half can be
finished during `BT-0`/`BT-1`, so that on the day L0 answers **DR-L0-07-D** the eight `facts.tsv` files are the only
thing anybody has to write.

---

### L0-07-01 — The onboarding store, the eight intake slots, and the `UNSET` discipline

**Size:** M · **Dependencies:** L0-00-02

The store is TSV, not YAML, for the reason `L0-02-lane-guard.md` §5 gives for `lane-paths.tsv` and `L0-06-01` gives
for `repo-scope.tsv`: the checkers that read it need no parser and no dependency, so they cannot fail for a reason
unrelated to what they are checking.

Two conventions this task establishes and every later task obeys:

* **Authored files are `key<TAB>value`, one pair per line.** **Generated tables** — `plan.tsv`, `rank/NN.tsv`, the
  per-slot `standard.tsv`, the stream claim log — are row-oriented under a single leading `#` header line. That is the
  carve-out §2.2 names, and nothing else is row-oriented.
* **Every unsupplied value is the literal token `UNSET`.** Never blank, never `-`, never a plausible default. Every
  checker in this file treats `UNSET` as **fail**, never as "not applicable". A store seeded by this task therefore
  fails every gate in the track, which is the correct reading of eight live products on day zero.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty; if not, STOP (§0.2)
git checkout -b l0/onboarding-01-store

mkdir -p docs/onboarding/floor/items \
         docs/onboarding/taxonomy/states docs/onboarding/taxonomy/notes docs/onboarding/taxonomy/standard \
         docs/onboarding/anchors docs/onboarding/rank \
         docs/onboarding/stream/claims docs/onboarding/stream/releases \
         docs/onboarding/fixtures

for s in 01 02 03 04 05 06 07 08; do
  mkdir -p "docs/onboarding/products/$s/floor"
  p="docs/onboarding/products/$s"
  printf 'product_id\tUNSET\nrepository\tUNSET\nreliability_criticality\tUNSET\nbusiness_criticality\tUNSET\nonboarding_cost_band\tUNSET\nconformance_profile\tUNSET\nteam\tUNSET\n' > "$p/facts.tsv"
  printf 'states\tUNSET\nnotes\tUNSET\nassessed_on\tUNSET\n' > "$p/states.tsv"
  printf 's10_status\tUNSET\ns10_rotation\tUNSET\ns10_incident_record\tUNSET\ns10_checked_on\tUNSET\ns19_status\tUNSET\ns19_removed_on\tUNSET\ns19_notification\tUNSET\ns19_deletion_obligation\tUNSET\ns19_checked_on\tUNSET\n' > "$p/gates.tsv"
  printf 'status\tUNSET\nmachine_drafted\tUNSET\nrecorded_by\tUNSET\nrecorded_on\tUNSET\ntemplate_version\tUNSET\nmaturity_level_at_intake\tUNSET\nincident_followups\tUNSET\n' > "$p/assessment.tsv"
  printf 'block_present\tUNSET\naccepted_risks_recorded\tUNSET\ninterim_response_authored\tUNSET\nverification_contract\tUNSET\n' > "$p/interim.tsv"
  printf 'suite_landed_on\tUNSET\nsla_days\t14\ntaken_over_on\tUNSET\ntaken_over_by\tUNSET\nstatus\tUNSET\n' > "$p/qa.tsv"
  printf 'source_expr\tUNSET\nresolved\tUNSET\nentered\tUNSET\nstatus\tUNSET\n' > "$p/deadline.tsv"
done

for a in S0 S1 S2 S3 OT-FLOOR; do
  printf 'token\t%s\ndate\tUNSET\ndeclared_by\tUNSET\n' "$a" > "docs/onboarding/anchors/$a.tsv"
done

cat > docs/onboarding/CONVENTIONS.md <<'CONV'
# Onboarding-track store — conventions

Authority: MasterSpec v4.0 Section 96 (spec L8714-L8834); decisions D99 (L10192), D72 (L10150), D78 (L10161);
Section 73.1 DevOps serialisation (spec L6005). Plan: implementation/lanes/L0-07-onboarding-track.md.
Owner: L0. Paths: docs/onboarding/** plus the root onboard-*.sh scripts plus Makefile targets, and nothing else.

## Four rules

1. Authored files are key<TAB>value, one pair per line, UTF-8, LF. Generated tables are row-oriented under one
   leading '#' header line and are NEVER hand-edited (invariant 46, spec L9514: derived data is computed).
2. Every unsupplied value is the literal token UNSET. Every checker treats UNSET as FAIL, never as not-applicable.
3. Slots 01..08 are arbitrary and stable. A slot is NOT a rank. Rank is computed into docs/onboarding/rank/.
   No product name, repository name or person's name is written by any executor: that is forbidden action OB-F1.
4. Onboarding PHASES and pre-onboarding DEADLINES are expressions, never dates (D99, spec L10192).
   FLOOR rows carry real calendar dates, because the floor consumes no Build-track subsystem (Section 96.6 L8802).

## The eight slots and what lives under each

facts.tsv      identity and the three Section 96.5 ordering keys   (L0 input)
states.tsv     the S-ids the recorded assessment found             (assessor input)
gates.tsv      the S10 and S19 AI-safety gates                     (checker input)
assessment.tsv the intake gap assessment register row              (assessor input)
standard.tsv   the ten-row target-standard coverage sheet          (assessor input, generated shell)
interim.tsv    pre-onboarding block presence and accepted risks    (L0 input)
qa.tsv         the QA-takeover SLA clock                           (QA input)
deadline.tsv   deadline expression and its resolution              (expression authored; resolution generated)
cd-gate.tsv    ONLY for a slot carrying state S3                   (L0 input)
floor/F1..F9   the nine floor rows for this product                (named executor input)
plan.tsv       the per-product phase plan                          (GENERATED by onboard-plan.sh)
CONV

cat > docs/onboarding/README.md <<'RM'
# Onboarding track — status

This file is GENERATED between the markers by `onboard-report.sh` (L0-07-15). Do not hand-edit inside them.
Conventions: docs/onboarding/CONVENTIONS.md. Plan: implementation/lanes/L0-07-onboarding-track.md.

<!-- BEGIN GENERATED -->
<!-- END GENERATED -->
RM
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Eight slots, no more, no fewer | `ls docs/onboarding/products \| tr '\n' ' '` | `01 02 03 04 05 06 07 08 ` |
| 2 | Seven authored files per slot, 56 in all | `find docs/onboarding/products -name '*.tsv' \| wc -l` | `56` |
| 3 | Every authored line is exactly two tab-separated fields | `find docs/onboarding -name '*.tsv' -exec awk -F'\t' 'NF!=2{print FILENAME}' {} + \| wc -l` | `0` |
| 4 | Every value is `UNSET`, except the calibrated `sla_days` | `find docs/onboarding/products -name '*.tsv' -exec awk -F'\t' '$2!="UNSET"{print $1}' {} + \| sort -u \| tr '\n' ' '` | `sla_days ` |
| 5 | Five anchors, all unanchored | `awk -F'\t' '$1=="date"{print $2}' docs/onboarding/anchors/*.tsv \| sort -u` | `UNSET` |
| 6 | The README carries both markers and nothing between them | `sed -n '/BEGIN GENERATED/,/END GENERATED/p' docs/onboarding/README.md \| wc -l` | `2` |
| 7 | No product identity was invented anywhere (OB-F1) | `awk -F'\t' '$1=="product_id"{print $2}' docs/onboarding/products/*/facts.tsv \| sort -u` | `UNSET` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'slots=%s files=%s malformed=%s nonunset=[%s] anchors=%s markers=%s\n' \
  "$(ls docs/onboarding/products | wc -l | tr -d ' ')" \
  "$(find docs/onboarding/products -name '*.tsv' | wc -l | tr -d ' ')" \
  "$(find docs/onboarding -name '*.tsv' -exec awk -F'\t' 'NF!=2{print FILENAME}' {} + | wc -l | tr -d ' ')" \
  "$(find docs/onboarding/products -name '*.tsv' -exec awk -F'\t' '$2!="UNSET"{print $1}' {} + | sort -u | tr '\n' ' ' | sed 's/ $//')" \
  "$(awk -F'\t' '$1=="date"{print $2}' docs/onboarding/anchors/*.tsv | sort -u)" \
  "$(sed -n '/BEGIN GENERATED/,/END GENERATED/p' docs/onboarding/README.md | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
slots=8 files=56 malformed=0 nonunset=[sla_days] anchors=UNSET markers=2
```

**Commit**

```bash
cd "$CP_ROOT"
git add -A
git diff --cached --name-only | grep -vE '^(docs/onboarding/|onboard-[a-z-]+\.sh$|Makefile$)' && echo "FOREIGN PATH - STOP" || echo "PATHS OK"
git commit -F- <<'MSG'
feat(docs): onboarding store, eight intake slots, UNSET discipline

Seeds docs/onboarding/ per PARTITION rule 3 (directory-per-item). Every value is
UNSET, so every checker in the track fails closed on a day-zero store.

Task-Id: L0-07-01
Lane: L0
Phase: OT-FLOOR
Spec: Section 96.6 L8802; Section 96.2 L8722-8733; D99 L10192; invariant 46 L9514
AT: none
Invariant: 46
Agent-Authored: true
Self-Verify: see L0-07-01 SELF-VERIFY
MSG
git push -u origin HEAD
gh pr create --base integration --title "L0-07-01: onboarding store and the eight intake slots" --body "See lanes/L0-07-onboarding-track.md L0-07-01."
```

**STOP rule** — if `nonunset` prints anything other than `[sla_days]`, a value has been invented. Do not "fix" it by
editing the value to something more plausible; delete `docs/onboarding/products/`, re-run the loop, and if the second
run still shows it, open `BLOCKER L0-07-01: seeded store carries a value no task supplied`. If you were tempted to
fill `product_id` with a real product name because you happen to know one, that is exactly **OB-F1** and
**DR-L0-07-D**: the eight identities and their three ordering keys are L0's to author, and an executor who guesses one
silently corrupts the §96.5 sequence from which every deadline in the portfolio is derived.

---

### L0-07-02 — The nine universal-floor items, and the seventy-two seeded obligation rows

**Size:** M · **Dependencies:** L0-07-01

Spec §96.6 (L8802) is unusually specific about the artifact, and the specificity is the point: *"it is a checklist
artifact with one row per item per product, each row carrying a named executor drawn from the product's existing team
(Section 95.4) and a date, not a paragraph anyone can declare complete."* Nine item definitions, transcribed once;
seventy-two rows, seeded open.

`estate` marks the six items that also bind the operating system's own machine estate (§5.1). Estate hosts are **not**
slots and are **not** in the 72 — the column exists so the fact survives in the store rather than only in this plan,
and so that **DR-L0-07-E** has something to point at.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-02-floor

while IFS='|' read -r id item src estate meaning; do
  [ -n "$id" ] || continue
  printf 'id\t%s\nitem\t%s\nsource\t%s\nestate\t%s\nmeaning\t%s\n' "$id" "$item" "$src" "$estate" "$meaning" \
    > "docs/onboarding/floor/items/$id.tsv"
done <<'ITEMS'
F1|backups-verified|Section 96.2 L8726|yes|A backup exists and one restore has been performed and recorded even if the full rotation cadence is not running; before Phase 3 the block maintainer and escalation pair confirm; this recorded restore is the one the OT-P6 rotation entry cites
F2|access-inventoried|Section 96.2 L8727|yes|Every credential admin account and deploy path is listed; no unknown access remains
F3|alerting-attached|Section 96.2 L8728|yes|At minimum an uptime check and an error-rate alert route to the standard alert channel
F4|accepted-risks-recorded|Section 96.2 L8729|yes|Every rule not yet met is written down as an accepted risk with an owner and mirrored into the exception registry (Section 54)
F5|named-deadline|Section 96.2 L8730|yes|A dated onboarding completion target; missing it is a Red signal not a silent slip (SIG-38 L4567)
F6|interim-response-authored|Section 96.2 L8731|yes|The required interim_response stanza: how to redeploy today where the last known-good build lives and which parts of the Section 42.3 response flow are waived under which accepted risk
F7|repository-in-organisation|Section 98.2 Phase 1 L9010|no|The portfolio-wide consolidation action; this is starting state S9 entire onboarding path
F8|branch-protection-applied|Section 98.2 Phase 1 L9010|no|From the template with required review and approval of the most recent reviewable push; the required-status-check list starts empty per repository and grows per phase
F9|secrets-out-and-inventoried|Section 98.2 Phase 1 L9010|no|The S10 remedy: rotation of every exposed credential is mandatory and sufficient; a minimal Section 43 incident record is always filed; purging history is optional and only via an authorised recorded history-rewrite exception
ITEMS

for s in 01 02 03 04 05 06 07 08; do
  for f in F1 F2 F3 F4 F5 F6 F7 F8 F9; do
    printf 'item\t%s\nexecutor\tUNSET\ndate\tUNSET\nstatus\tUNSET\nevidence\tUNSET\naccepted_risk\tUNSET\n' \
      "$f" > "docs/onboarding/products/$s/floor/$f.tsv"
  done
done
```

Six keys per row, and the meaning of each, because a checker is only as honest as the field it reads:

> **HUMAN STEP** — Filling the `executor`, `date`, `evidence`, and `status` fields for floor items F7 (move the product repository into the organisation), F8 (apply branch protection from the GitHub template on the product repository), and F9 (rotate every exposed credential and file the §43 incident record) must be done by the named executor inside the product repository or on live GitHub. The AI executor running this task seeds these rows as `UNSET`; it records and verifies the evidence supplied by the named executor, and never performs the step itself (OB-F5).

| Key | Values | Read by |
|---|---|---|
| `item` | `F1`…`F9` | join key back to `floor/items/` |
| `executor` | a named person **drawn from the product's existing team** (Spec §95.4). Never a role, never a team | `onboard-floor.sh` |
| `date` | `YYYY-MM-DD` — a real calendar date. Floor rows are dated; phases are expressed (§3.1) | `onboard-floor.sh`; the `--lint` of L0-07-04 does not scan this file |
| `status` | `UNSET` (= open) or the literal `closed`. Nothing else closes a row | `onboard-floor.sh` |
| `evidence` | what proves it. Non-`UNSET` is mandatory on any `closed` row | `onboard-floor.sh` paper-floor detector |
| `accepted_risk` | the dated accepted-risk id, required for any row still open past its date (§96.6 L8802) | `onboard-floor.sh` |

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Nine item definitions | `ls docs/onboarding/floor/items \| tr '\n' ' '` | `F1.tsv F2.tsv F3.tsv F4.tsv F5.tsv F6.tsv F7.tsv F8.tsv F9.tsv ` |
| 2 | Exactly seventy-two obligation rows | `find docs/onboarding/products -path '*/floor/*.tsv' \| wc -l` | `72` |
| 3 | Six of the nine items bind the estate (§5.1) | `awk -F'\t' '$1=="estate" && $2=="yes"' docs/onboarding/floor/items/*.tsv \| wc -l` | `6` |
| 4 | Every row has all six keys | `for f in docs/onboarding/products/*/floor/*.tsv; do wc -l < "$f"; done \| sort -u` | `6` |
| 5 | Nothing is closed yet | `awk -F'\t' '$1=="status" && $2=="closed"' docs/onboarding/products/*/floor/*.tsv \| wc -l` | `0` |
| 6 | Every item id appears in every slot | `awk -F'\t' '$1=="item"{print $2}' docs/onboarding/products/*/floor/*.tsv \| sort \| uniq -c \| awk '{print $1}' \| sort -u` | `8` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'items=%s rows=%s estate=%s keys=%s closed=%s peritem=%s\n' \
  "$(ls docs/onboarding/floor/items | wc -l | tr -d ' ')" \
  "$(find docs/onboarding/products -path '*/floor/*.tsv' | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="estate" && $2=="yes"' docs/onboarding/floor/items/*.tsv | wc -l | tr -d ' ')" \
  "$(for f in docs/onboarding/products/*/floor/*.tsv; do wc -l < "$f"; done | sort -u | tr '\n' ',' | sed 's/,$//' | tr -d ' ')" \
  "$(awk -F'\t' '$1=="status" && $2=="closed"' docs/onboarding/products/*/floor/*.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="item"{print $2}' docs/onboarding/products/*/floor/*.tsv | sort | uniq -c | awk '{print $1}' | sort -u | tr '\n' ',' | sed 's/,$//')"
```

Expected output, exactly:

```
items=9 rows=72 estate=6 keys=6 closed=0 peritem=8
```

**Commit**

```bash
cd "$CP_ROOT"
git add -A
git diff --cached --name-only | grep -vE '^(docs/onboarding/|onboard-[a-z-]+\.sh$|Makefile$)' && echo "FOREIGN PATH - STOP" || echo "PATHS OK"
git commit -F- <<'MSG'
feat(docs): nine universal-floor items and seventy-two seeded obligations

Transcribes the Section 96.6 floor (the six Section 96.2 items plus the three
portfolio-wide Phase 1 actions) and seeds one row per item per slot, each open,
each carrying a named-executor and date slot. 9 x 8 = 72 (spec L8802).

Task-Id: L0-07-02
Lane: L0
Phase: OT-FLOOR
Spec: Section 96.6 L8802; Section 96.2 L8726-8731; Section 98.2 Phase 1 L9010; D69 L10147
AT: AT-051
Invariant: none
Agent-Authored: true
Self-Verify: see L0-07-02 SELF-VERIFY
MSG
git push -u origin HEAD
gh pr create --base integration --title "L0-07-02: the nine floor items and the 72 obligations" --body "See lanes/L0-07-onboarding-track.md L0-07-02."
```

**STOP rule** — if `rows` is anything other than `72`, stop before committing. The number is the spec's own arithmetic
at L8802 (*"nine items across every live product, which at eight products is seventy-two tracked obligations"*) and it
is the denominator of the burn-down `SIG-38` is computed against. If you believe there is a **tenth** floor item — the
S19 customer-data check is the candidate, and the ambiguity is real — do **not** add it. It is **DR-L0-07-C**, and the
S19 gate is tracked in `gates.tsv` and counted separately until L0 answers. If you believe an estate host should be a
ninth or tenth slot, that is **DR-L0-07-E**: an estate host is not a repository and meets six items, not nine.

---

### L0-07-03 — The nineteen-state taxonomy, the two intake notes, and the prereq-token map

**Size:** M · **Dependencies:** L0-07-01

Nineteen states, one file each, transcribed from the §96.6 table (spec L8808–L8826). Two things travel with them: the
`ai_gate` flag, which is `yes` for exactly S10 and S19 and `no` for the other seventeen; and the `prereq` token of §6,
which is authored in this plan, is data here, and is never derived by an executor.

Read §6.3 before you count rows in the spec: at L8825 the S18 and S19 rows are emitted on one physical line and the
S19 text then repeats at L8826. The taxonomy is **nineteen** states. Ids are transcribed literally and are never
derived from row position.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-03-taxonomy

while IFS='|' read -r id line gate prereq state; do
  [ -n "$id" ] || continue
  printf 'id\t%s\nstate\t%s\nspec_line\t%s\nai_gate\t%s\nprereq\t%s\n' "$id" "$state" "$line" "$gate" "$prereq" \
    > "docs/onboarding/taxonomy/states/$id.tsv"
done <<'STATES'
S1|L8808|no|-|No CI and no CD - manual everything
S2|L8809|no|-|CI only - tests run deployment manual
S3|L8810|no|cd-gate|CD only - auto-deploy with no meaningful tests
S4|L8811|no|-|Local development only - nothing deployed or deployed ad hoc
S5|L8812|no|restore-target|Local plus production no staging
S6|L8813|no|environment-mapping|A UAT environment only or odd environment names
S7|L8814|no|-|No tests at all
S8|L8815|no|-|Not containerised or no reproducible build
S9|L8816|no|repo-in-org|Repository on a personal account or outside host
S10|L8817|yes|s10-gate|Secrets committed in the repository or dotenv files
S11|L8818|no|-|No monitoring no health endpoints
S12|L8819|no|profile-client-app|Mobile or store-delivered product
S13|L8820|no|lifecycle-decision|Heavy tech debt or legacy stack nobody wants to touch
S14|L8821|no|-|Already meeting most of the standard
S15|L8822|no|shared-repo-decl|Multi-product monorepo
S16|L8823|no|profile-customer-hosted|Customer-hosted or on-premises production
S17|L8824|no|profile-library-or-batch|Library SDK or batch pipeline - no serving interface
S18|L8825|no|equivalent-identity|Platform-rebuild deployment - git-push PaaS rebuilding per environment
S19|L8825-8826|yes|s19-gate|Customer data committed in the repository
STATES

printf 'id\tN1\nnote\tA store account owned by a personal Google or Apple account is the mobile-store analogue of S9: transfer to the company account is scheduled at intake or its absence is a dated accepted risk\nspec_line\tL8828\nprereq\tstore-account-transfer\n' > docs/onboarding/taxonomy/notes/N1.tsv
printf 'id\tN2\nnote\tA production database shared between two products is declared at intake and backup and restore ownership is assigned to a named product then - never left implicit between the two\nspec_line\tL8828\nprereq\tshared-db-ownership\n' > docs/onboarding/taxonomy/notes/N2.tsv
```

The full immediate-action and onboarding-path prose for every state is the §6 table of this plan and stays there. The
store carries the id, the state name, the spec line, the gate flag and the prereq token — which is everything a
checker reads. A checker that had to parse an English paragraph would be a checker that fails for a reason unrelated
to what it is checking.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Nineteen states, each exactly once | `ls docs/onboarding/taxonomy/states \| sed 's/\.tsv//' \| sort -V \| tr '\n' ' '` | `S1 S2 S3 S4 S5 S6 S7 S8 S9 S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 ` |
| 2 | Exactly two states are AI-safety gates | `awk -F'\t' '$1=="ai_gate" && $2=="yes"{print FILENAME}' docs/onboarding/taxonomy/states/*.tsv \| xargs -n1 basename \| sort \| tr '\n' ' '` | `S10.tsv S19.tsv ` |
| 3 | Twelve states carry a prereq token | `awk -F'\t' '$1=="prereq" && $2!="-"' docs/onboarding/taxonomy/states/*.tsv \| wc -l` | `12` |
| 4 | Every prereq token is unique | `awk -F'\t' '$1=="prereq" && $2!="-"{print $2}' docs/onboarding/taxonomy/states/*.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 5 | Two intake notes, each with its own token | `awk -F'\t' '$1=="prereq"{print $2}' docs/onboarding/taxonomy/notes/*.tsv \| sort \| tr '\n' ' '` | `shared-db-ownership store-account-transfer ` |
| 6 | Every state file has five keys | `for f in docs/onboarding/taxonomy/states/*.tsv; do wc -l < "$f"; done \| sort -u` | `5` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'states=%s gates=[%s] prereqs=%s dupes=%s notes=%s keys=%s\n' \
  "$(ls docs/onboarding/taxonomy/states | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="ai_gate" && $2=="yes"{print FILENAME}' docs/onboarding/taxonomy/states/*.tsv | xargs -n1 basename | sed 's/\.tsv//' | sort | tr '\n' ' ' | sed 's/ $//')" \
  "$(awk -F'\t' '$1=="prereq" && $2!="-"' docs/onboarding/taxonomy/states/*.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="prereq" && $2!="-"{print $2}' docs/onboarding/taxonomy/states/*.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(ls docs/onboarding/taxonomy/notes | wc -l | tr -d ' ')" \
  "$(for f in docs/onboarding/taxonomy/states/*.tsv; do wc -l < "$f"; done | sort -u | tr '\n' ',' | sed 's/,$//' | tr -d ' ')"
```

Expected output, exactly:

```
states=19 gates=[S10 S19] prereqs=12 dupes=0 notes=2 keys=5
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-03`, branch `l0/onboarding-03-taxonomy`, subject
`feat(docs): nineteen-state intake taxonomy, two intake notes, prereq tokens`,
`Spec: Section 96.6 L8806-L8828; D78 L10161`, `Invariant: 111`.

**STOP rule** — if `states` is `20`, you have transcribed the L8825 rendering artifact as a twentieth state: delete
`docs/onboarding/taxonomy/states/`, read §6.3, and re-run the loop. If `gates` is anything other than `[S10 S19]`,
stop — that flag decides which repositories are closed to *every* AI-assisted session, and adding a third or dropping
one of the two is a policy change, not a transcription. §96.6's closing paragraph (L8832) does say the taxonomy *"is
configuration, not a closed list — a starting state not listed here is added to the table when first encountered, with
its path, rather than handled silently"*; adding an S20 is therefore legitimate **and is L0's**, under the same
authority as **DR-L0-07-D**. An executor who meets an unlisted starting state opens
`BLOCKER L0-07-03: unlisted starting state <description>` and adds nothing.

---

### L0-07-04 — `onboard-when.sh` — the relative-date resolver and the absolute-label lint (D99)

**Size:** L · **Dependencies:** L0-07-01

This script is the mechanical form of D99 (spec L10192) and it is the **only writer of a resolved date** in the whole
track. Four subcommands, and nothing else:

| Subcommand | Does | Refuses |
|---|---|---|
| `resolve <expr>` | prints the resolved `YYYY-MM-DD`, or `UNANCHORED`, or `UNKNOWN-TOKEN` | an expression that is not `TOKEN[+Nw]` or `max(e1,e2)` |
| `set <token> <YYYY-MM-DD> <declared_by>` | writes an anchor file | a date that is not `YYYY-MM-DD`; a token whose anchor file does not already exist |
| `lint` | scans every expression-bearing file for an absolute week label | nothing — it reports, and exits 1 on any hit |
| `check` | recomputes every `deadline.tsv` `resolved` from its `source_expr` and compares | nothing — exits 1 on any divergence |

`UNANCHORED` is a **result, not an error**. A phase whose Build-track sync point has not been declared passed has no
date, and printing one would be the precise failure D99 exists to prevent.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-04-when
date -u -d "2026-01-01 +2 weeks" +%Y-%m-%d      # expected: 2026-01-15 ; if not, STOP (§0.1)

cat > onboard-when.sh <<'WHEN'
#!/usr/bin/env sh
# =============================================================================
# onboard-when.sh — L0-owned. The ONLY writer of a resolved date in the
# onboarding track. Mechanical form of D99 (MasterSpec v4.0 L10192):
# "an Onboarding track whose per-product phases are relative to the subsystems
# they consume. Pre-onboarding deadlines are set from the Onboarding track,
# not from the labels."
# Store: docs/onboarding (override with OB_ROOT for fixtures).
# Plan: implementation/lanes/L0-07-onboarding-track.md L0-07-04.
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"

usage() {
  echo "usage: onboard-when.sh resolve <expr> | set <token> <YYYY-MM-DD> <who> | lint | check" >&2
  exit 2
}

is_date() {
  case "$1" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;;
    *) return 1 ;;
  esac
}

anchor_date() {                       # $1 = token
  f="$OB/anchors/$1.tsv"
  if [ ! -f "$f" ]; then echo "MISSING"; return; fi
  v=$(awk -F'\t' '$1=="date"{print $2}' "$f")
  if [ -z "$v" ]; then echo "UNSET"; else echo "$v"; fi
}

resolve_one() {                       # $1 = TOKEN[+Nw]
  e="$1"
  case "$e" in
    *+*w) tok=$(printf '%s' "$e" | sed 's/+.*$//')
          off=$(printf '%s' "$e" | sed 's/^.*+//; s/w$//') ;;
    *)    tok="$e"; off=0 ;;
  esac
  case "$off" in ''|*[!0-9]*) echo "BAD-EXPRESSION"; return ;; esac
  d=$(anchor_date "$tok")
  case "$d" in
    MISSING) echo "UNKNOWN-TOKEN"; return ;;
    UNSET)   echo "UNANCHORED";   return ;;
  esac
  if is_date "$d"; then
    date -u -d "$d +$off weeks" +%Y-%m-%d
  else
    echo "BAD-ANCHOR"
  fi
}

resolve() {                           # $1 = expr, possibly max(e1,e2)
  e="$1"
  case "$e" in
    max\(*\))
      inner=$(printf '%s' "$e" | sed 's/^max(//; s/)$//')
      a=$(printf '%s' "$inner" | sed 's/,.*$//')
      b=$(printf '%s' "$inner" | sed 's/^[^,]*,//')
      ra=$(resolve_one "$a"); rb=$(resolve_one "$b")
      for r in "$ra" "$rb"; do
        case "$r" in UNANCHORED|UNKNOWN-TOKEN|BAD-EXPRESSION|BAD-ANCHOR) echo "$r"; return ;; esac
      done
      printf '%s\n%s\n' "$ra" "$rb" | sort | tail -1
      ;;
    *) resolve_one "$e" ;;
  esac
}

lint() {
  # An absolute week label in an expression-bearing file is the exact failure D99
  # forbids. Floor rows are NOT scanned: floor rows are dated (Section 96.6 L8802,
  # this plan section 3.1). Only plan.tsv and deadline.tsv carry expressions.
  hits=0
  for f in "$OB"/products/*/plan.tsv "$OB"/products/*/deadline.tsv; do
    [ -f "$f" ] || continue
    if grep -nEi 'week[s]?[ _-]?[0-9]' "$f" >/dev/null 2>&1; then
      grep -nEi 'week[s]?[ _-]?[0-9]' "$f" | sed "s|^|ABSOLUTE-LABEL $f:|"
      hits=$((hits+1))
    fi
  done
  echo "WHEN-LINT files_with_labels=$hits"
  [ "$hits" -eq 0 ] || return 1
  return 0
}

check() {
  bad=0; n=0
  for f in "$OB"/products/*/deadline.tsv; do
    [ -f "$f" ] || continue
    slot=$(basename "$(dirname "$f")")
    src=$(awk -F'\t' '$1=="source_expr"{print $2}' "$f")
    got=$(awk -F'\t' '$1=="resolved"{print $2}' "$f")
    [ "$src" = "UNSET" ] && continue
    n=$((n+1))
    want=$(resolve "$src")
    if [ "$want" != "$got" ]; then
      echo "STALE-RESOLUTION slot=$slot expr=$src recorded=$got recomputed=$want"
      bad=$((bad+1))
    fi
  done
  echo "WHEN-CHECK resolved=$n stale=$bad"
  [ "$bad" -eq 0 ] || return 1
  return 0
}

[ $# -ge 1 ] || usage
cmd="$1"; shift
case "$cmd" in
  resolve) [ $# -eq 1 ] || usage; resolve "$1" ;;
  set)
    [ $# -eq 3 ] || usage
    tok="$1"; d="$2"; who="$3"
    f="$OB/anchors/$tok.tsv"
    [ -f "$f" ] || { echo "NO-SUCH-ANCHOR $tok — create the anchor file first (L0-07-01/T11)" >&2; exit 1; }
    is_date "$d" || { echo "NOT-A-DATE $d" >&2; exit 1; }
    printf 'token\t%s\ndate\t%s\ndeclared_by\t%s\n' "$tok" "$d" "$who" > "$f"
    echo "ANCHORED $tok=$d by=$who"
    ;;
  lint|--lint)   lint ;;
  check|--check) check ;;
  *) usage ;;
esac
WHEN
chmod +x onboard-when.sh

mkdir -p docs/onboarding/fixtures/when/anchors docs/onboarding/fixtures/when/products/01 \
         docs/onboarding/fixtures/when-bad/products/01
printf 'token\tS3\ndate\t2026-01-05\ndeclared_by\tL0\n'          > docs/onboarding/fixtures/when/anchors/S3.tsv
printf 'token\tS0\ndate\tUNSET\ndeclared_by\tUNSET\n'            > docs/onboarding/fixtures/when/anchors/S0.tsv
printf 'token\tOT-P6-01\ndate\t2026-02-02\ndeclared_by\tL0\n'    > docs/onboarding/fixtures/when/anchors/OT-P6-01.tsv
printf 'source_expr\tS3+2w\nresolved\t2026-01-19\nentered\t2026-01-05\nstatus\tpre_onboarding\n' \
  > docs/onboarding/fixtures/when/products/01/deadline.tsv
printf 'source_expr\tWeek 4\nresolved\tUNSET\nentered\tUNSET\nstatus\tUNSET\n' \
  > docs/onboarding/fixtures/when-bad/products/01/deadline.tsv
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | An anchored expression resolves | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve S3+2w` | `2026-01-19` |
| 2 | A zero offset is the anchor itself | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve OT-P6-01+0w` | `2026-02-02` |
| 3 | `max()` takes the later of the two | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve 'max(S3+2w,OT-P6-01+0w)'` | `2026-02-02` |
| 4 | An undeclared anchor propagates, it does not guess | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve S0+1w` | `UNANCHORED` |
| 5 | `max()` with one unanchored side is unanchored | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve 'max(S0+0w,S3+0w)'` | `UNANCHORED` |
| 6 | An unknown token is named, not defaulted | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh resolve BT-9+0w` | `UNKNOWN-TOKEN` |
| 7 | The real store is clean of absolute labels | `./onboard-when.sh lint` | `WHEN-LINT files_with_labels=0` |
| 8 | The lint actually fails on a week label | `OB_ROOT=docs/onboarding/fixtures/when-bad ./onboard-when.sh lint >/dev/null; echo $?` | `1` |
| 9 | A recorded resolution that matches passes `check` | `OB_ROOT=docs/onboarding/fixtures/when ./onboard-when.sh check` | `WHEN-CHECK resolved=1 stale=0` |
| 10 | `set` refuses a non-date | `./onboard-when.sh set S0 "Week 4" L0 >/dev/null 2>&1; echo $?` | `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
F=docs/onboarding/fixtures/when
printf 'a=%s b=%s max=%s unanch=%s maxunanch=%s unk=%s lint=%s badlint=%s check=[%s] setrefuse=%s\n' \
  "$(OB_ROOT=$F ./onboard-when.sh resolve S3+2w)" \
  "$(OB_ROOT=$F ./onboard-when.sh resolve OT-P6-01+0w)" \
  "$(OB_ROOT=$F ./onboard-when.sh resolve 'max(S3+2w,OT-P6-01+0w)')" \
  "$(OB_ROOT=$F ./onboard-when.sh resolve S0+1w)" \
  "$(OB_ROOT=$F ./onboard-when.sh resolve 'max(S0+0w,S3+0w)')" \
  "$(OB_ROOT=$F ./onboard-when.sh resolve BT-9+0w)" \
  "$(./onboard-when.sh lint | awk '{print $2}')" \
  "$(OB_ROOT=docs/onboarding/fixtures/when-bad ./onboard-when.sh lint >/dev/null 2>&1; echo $?)" \
  "$(OB_ROOT=$F ./onboard-when.sh check)" \
  "$(./onboard-when.sh set S0 'Week 4' L0 >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
a=2026-01-19 b=2026-02-02 max=2026-02-02 unanch=UNANCHORED maxunanch=UNANCHORED unk=UNKNOWN-TOKEN lint=files_with_labels=0 badlint=1 check=[WHEN-CHECK resolved=1 stale=0] setrefuse=1
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-04`, branch `l0/onboarding-04-when`, subject
`feat(root): onboard-when.sh, the relative-date resolver and absolute-label lint`,
`Spec: D99 L10192; Section 96.2 L8730; Section 98.2 L9050-L9080`, `Invariant: none`.

**STOP rule** — if criterion 8 prints `0`, the lint does not fail on `Week 4` and **must not be committed**: a lint
that passes everything is worse than no lint, because the track gate of L0-07-14 will then certify a store full of
label-derived deadlines as D99-clean. Do not relax the regex to make criterion 7 pass either — if criterion 7 fails on
the real store, a week label has been written into a `plan.tsv` or a `deadline.tsv`, and the fix is to replace that
value with an expression, never to narrow the pattern. If you cannot express a date any other way because no anchor
token fits, open `BLOCKER L0-07-04: no anchor token expresses <case>`; inventing a token is **OB-F2**.

---

### L0-07-05 — `onboard-floor.sh` — the floor checker and the paper-floor detector

**Size:** M · **Dependencies:** L0-07-02, L0-07-04

The floor's failure mode is named in the spec, in the same sentence that defines the artifact: *"a floor declared done
on paper is exactly the invisible half-adoption 96.4 exists to catch, occurring in the one week 96.4 cannot see,
because the health report carrying its signals is a G1 deliverable"* (§96.6, L8802). So this checker's central rule is
not "count the closed rows". It is: **a row closed without evidence is a violation, and the run fails.**

Two failure classes, and one measurement:

| Class | Definition | Exit |
|---|---|---|
| `PAPER-FLOOR` | `status=closed` with `evidence=UNSET` | **1** — the §96.6 L8802 failure, verbatim |
| `RED-FLOOR` | open, with a `date` in the past relative to `--asof`, and `accepted_risk=UNSET` | **1** — §96.6 L8802: an outstanding floor item *"carries a dated accepted risk for it, mirrored into the exception registry like any other"* |
| `unexecuted` | `executor=UNSET` | **0** — measured, not failed. §95.4 requires a named executor before the row can be worked, and `onboard-plan.sh` blocks the slot's `OT-P4` on it |

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-05-floor

cat > onboard-floor.sh <<'FLOOR'
#!/usr/bin/env sh
# =============================================================================
# onboard-floor.sh — L0-owned. The universal-floor burn-down and the
# paper-floor detector. MasterSpec v4.0 Section 96.6 (spec L8802):
# nine items x every live product = seventy-two tracked obligations, each row
# carrying a named executor (Section 95.4) and a date.
# usage: onboard-floor.sh [--asof YYYY-MM-DD] [--slot NN]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ASOF=$(date -u +%Y-%m-%d)
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --asof) ASOF="$2"; shift 2 ;;
    --slot) ONLY="$2"; shift 2 ;;
    *) echo "usage: onboard-floor.sh [--asof YYYY-MM-DD] [--slot NN]" >&2; exit 2 ;;
  esac
done

# older <a> <b> — true when ISO date a is strictly earlier than ISO date b.
# Uses sort, not test '<', because POSIX test has no string-ordering operator.
older() {
  [ "$1" != "$2" ] || return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort | head -1)" = "$1" ]
}

total=0; closed=0; paper=0; red=0; unexec=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  for f in "$d"floor/*.tsv; do
    [ -f "$f" ] || continue
    item=$(awk -F'\t'     '$1=="item"{print $2}'          "$f")
    st=$(awk -F'\t'       '$1=="status"{print $2}'        "$f")
    ev=$(awk -F'\t'       '$1=="evidence"{print $2}'      "$f")
    dt=$(awk -F'\t'       '$1=="date"{print $2}'          "$f")
    ex=$(awk -F'\t'       '$1=="executor"{print $2}'      "$f")
    ar=$(awk -F'\t'       '$1=="accepted_risk"{print $2}' "$f")
    total=$((total+1))
    [ "$ex" = "UNSET" ] && unexec=$((unexec+1))
    if [ "$st" = "closed" ]; then
      closed=$((closed+1))
      if [ "$ev" = "UNSET" ]; then
        echo "PAPER-FLOOR slot=$slot item=$item — closed with no evidence (Section 96.6 L8802)"
        paper=$((paper+1))
      fi
    else
      if [ "$dt" != "UNSET" ] && older "$dt" "$ASOF" && [ "$ar" = "UNSET" ]; then
        echo "RED-FLOOR slot=$slot item=$item date=$dt — outstanding past its date with no dated accepted risk"
        red=$((red+1))
      fi
    fi
  done
done

open=$((total-closed))
echo "FLOOR total=$total closed=$closed open=$open paper=$paper red=$red unexecuted=$unexec asof=$ASOF"
[ "$paper" -eq 0 ] && [ "$red" -eq 0 ] || exit 1
exit 0
FLOOR
chmod +x onboard-floor.sh

mkdir -p docs/onboarding/fixtures/floor-bad/products/01/floor
printf 'item\tF1\nexecutor\tperson-a\ndate\t2026-01-05\nstatus\tclosed\nevidence\tUNSET\naccepted_risk\tUNSET\n' \
  > docs/onboarding/fixtures/floor-bad/products/01/floor/F1.tsv
printf 'item\tF3\nexecutor\tperson-a\ndate\t2026-01-05\nstatus\tUNSET\nevidence\tUNSET\naccepted_risk\tUNSET\n' \
  > docs/onboarding/fixtures/floor-bad/products/01/floor/F3.tsv
```

`older()` compares two ISO-8601 dates by sorting them, because POSIX `test` has no string-ordering operator and
`[ "$a" \< "$b" ]` is a bashism that fails silently under `dash`. ISO-8601 sorts lexically, so no `date` call is
needed anywhere in this checker — which means it cannot fail for a reason unrelated to what it is checking.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The seeded store is 72 open, and passes | `./onboard-floor.sh --asof 2026-03-01` | `FLOOR total=72 closed=0 open=72 paper=0 red=0 unexecuted=72 asof=2026-03-01` |
| 2 | The seeded store exits 0 | `./onboard-floor.sh --asof 2026-03-01 >/dev/null; echo $?` | `0` |
| 3 | A closed row with no evidence is caught | `OB_ROOT=docs/onboarding/fixtures/floor-bad ./onboard-floor.sh --asof 2026-03-01 \| grep -c PAPER-FLOOR` | `1` |
| 4 | An open row past its date with no accepted risk is caught | `OB_ROOT=docs/onboarding/fixtures/floor-bad ./onboard-floor.sh --asof 2026-03-01 \| grep -c RED-FLOOR` | `1` |
| 5 | Either failure class fails the run | `OB_ROOT=docs/onboarding/fixtures/floor-bad ./onboard-floor.sh --asof 2026-03-01 >/dev/null 2>&1; echo $?` | `1` |
| 6 | Before its date, the open row is not Red | `OB_ROOT=docs/onboarding/fixtures/floor-bad ./onboard-floor.sh --asof 2026-01-01 \| grep -c RED-FLOOR` | `0` |
| 7 | One slot can be inspected alone | `./onboard-floor.sh --slot 03 --asof 2026-03-01 \| awk '{print $2}'` | `total=9` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
B=docs/onboarding/fixtures/floor-bad
printf 'seeded=[%s] rc=%s paper=%s red=%s badrc=%s early=%s slot=%s\n' \
  "$(./onboard-floor.sh --asof 2026-03-01)" \
  "$(./onboard-floor.sh --asof 2026-03-01 >/dev/null; echo $?)" \
  "$(OB_ROOT=$B ./onboard-floor.sh --asof 2026-03-01 | grep -c PAPER-FLOOR)" \
  "$(OB_ROOT=$B ./onboard-floor.sh --asof 2026-03-01 | grep -c RED-FLOOR)" \
  "$(OB_ROOT=$B ./onboard-floor.sh --asof 2026-03-01 >/dev/null 2>&1; echo $?)" \
  "$(OB_ROOT=$B ./onboard-floor.sh --asof 2026-01-01 | grep -c RED-FLOOR)" \
  "$(./onboard-floor.sh --slot 03 --asof 2026-03-01 | awk '{print $2}')"
```

Expected output, exactly:

```
seeded=[FLOOR total=72 closed=0 open=72 paper=0 red=0 unexecuted=72 asof=2026-03-01] rc=0 paper=1 red=1 badrc=1 early=0 slot=total=9
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-05`, branch `l0/onboarding-05-floor`, subject
`feat(root): onboard-floor.sh, the 72-obligation burn-down and paper-floor detector`,
`Spec: Section 96.6 L8802; Section 96.2 L8722-8733; Section 95.4`, `AT: AT-051`, `Invariant: none`.

**STOP rule** — if `paper` prints `0` against the `floor-bad` fixture, the detector is not detecting and must not be
committed. Do not weaken the rule to `status=closed` alone: the whole point of L8802 is that closure is a claim and
evidence is the thing that makes the claim checkable. If a real row is genuinely closed and you cannot find evidence
to name, the row is **not closed** — set `status` back to `UNSET` and record the reason as an accepted risk. Declaring
a floor row done on any evidence other than this command's own output is forbidden action **OB-F8**.

---

### L0-07-06 — `onboard-aigate.sh` — the S10 and S19 AI-safety gates, fail-closed and asymmetric

**Size:** M · **Dependencies:** L0-07-03

Two taxonomy rows carry the same sentence — *"No AI-assisted session opens the repository until the S10 check passes —
universal floor"* (L8817) and the same for S19 (L8825) — and Spec §33 restates the S10 half for the packaging path.
`04` §8 DECISION 3 already draws the consequence: a product failing either *"is unavailable to any AI-assisted work,
including onboarding, until it passes."*

**The two gates are not symmetric, and the script must not treat them as if they were.** For S10, rotation is the
control and history-purging is optional. For S19 there is *"no rotation-equivalent remedy here, which is exactly why
this check is mandatory and not deferred"* — the removal itself is the control. The pass conditions therefore differ,
and the script names the missing field rather than printing a bare `BLOCKED`.

| Gate | Passes only when |
|---|---|
| **S10** | `s10_status=pass` **and** `s10_checked_on` is a date **and** `s10_rotation` ∈ {`done`, `not-applicable`} **and** `s10_incident_record` is `none` exactly when `s10_rotation=not-applicable`, and a record id otherwise (§96.6 L8817: *"a minimal Section 43 incident record is always filed"*) |
| **S19** | `s19_status=pass` **and** `s19_checked_on` is a date **and** `s19_removed_on` is a date or `not-applicable` **and** `s19_notification` ∈ {`done`, `not-required-by-classification`, `not-applicable`} **and** `s19_deletion_obligation` is not `UNSET` (`none`, or a `records/deletion-requests/` reference — Spec §97.2) |

A gate row claiming `pass` while missing any of its own evidence is `INVALID`, not `BLOCKED`, and **exits 1**: it is a
mis-stated fact in the store, not a legitimate state of a product.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-06-aigate

cat > onboard-aigate.sh <<'AIGATE'
#!/usr/bin/env sh
# =============================================================================
# onboard-aigate.sh — L0-owned. The S10 and S19 AI-safety gates.
# MasterSpec v4.0 Section 96.6 L8817 (S10) and L8825 (S19), both verbatim:
# "No AI-assisted session opens the repository until the S<n> check passes —
# universal floor". Section 33 restates the S10 half; invariant 111 (L9597)
# names the S19 intake gate as one of the three no-customer-data detectors.
# FAIL-CLOSED: UNSET is BLOCKED, never "not applicable".
# usage: onboard-aigate.sh [--slot NN] [--verdict NN]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ONLY=""; VERDICT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --slot)    ONLY="$2";    shift 2 ;;
    --verdict) VERDICT="$2"; shift 2 ;;
    *) echo "usage: onboard-aigate.sh [--slot NN] [--verdict NN]" >&2; exit 2 ;;
  esac
done

is_date() { case "$1" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;; *) return 1 ;; esac; }
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }

invalid=0; blocked=0; permitted=0
[ -n "$VERDICT" ] && ONLY="$VERDICT"

for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  g="$d/gates.tsv"
  [ -f "$g" ] || { echo "AIGATE slot=$slot verdict=INVALID reason=no-gates-file"; invalid=$((invalid+1)); continue; }

  s10s=$(kv "$g" s10_status);   s10r=$(kv "$g" s10_rotation)
  s10i=$(kv "$g" s10_incident_record); s10c=$(kv "$g" s10_checked_on)
  s19s=$(kv "$g" s19_status);   s19rm=$(kv "$g" s19_removed_on)
  s19n=$(kv "$g" s19_notification); s19o=$(kv "$g" s19_deletion_obligation); s19c=$(kv "$g" s19_checked_on)

  s10="BLOCKED"; s10why="s10-gate"
  if [ "$s10s" = "pass" ]; then
    if ! is_date "$s10c"; then s10="INVALID"; s10why="s10-pass-without-check-date"
    elif [ "$s10r" = "not-applicable" ] && [ "$s10i" != "none" ]; then s10="INVALID"; s10why="s10-no-exposure-but-incident-record-claimed"
    elif [ "$s10r" = "done" ] && { [ "$s10i" = "none" ] || [ "$s10i" = "UNSET" ]; }; then s10="INVALID"; s10why="s10-rotation-without-incident-record"
    elif [ "$s10r" != "done" ] && [ "$s10r" != "not-applicable" ]; then s10="INVALID"; s10why="s10-pass-without-rotation-disposition"
    else s10="PASS"; s10why="-"; fi
  elif [ "$s10s" = "fail" ]; then s10why="s10-gate-failed"
  fi

  s19="BLOCKED"; s19why="s19-gate"
  if [ "$s19s" = "pass" ]; then
    if ! is_date "$s19c"; then s19="INVALID"; s19why="s19-pass-without-check-date"
    elif ! is_date "$s19rm" && [ "$s19rm" != "not-applicable" ]; then s19="INVALID"; s19why="s19-no-removal-there-is-no-rotation-equivalent-remedy"
    elif [ "$s19n" != "done" ] && [ "$s19n" != "not-required-by-classification" ] && [ "$s19n" != "not-applicable" ]; then s19="INVALID"; s19why="s19-notification-disposition-missing"
    elif [ "$s19o" = "UNSET" ]; then s19="INVALID"; s19why="s19-deletion-obligation-not-recorded"
    else s19="PASS"; s19why="-"; fi
  elif [ "$s19s" = "fail" ]; then s19why="s19-gate-failed"
  fi

  if [ "$s10" = "INVALID" ] || [ "$s19" = "INVALID" ]; then
    v="INVALID"; why=$([ "$s10" = "INVALID" ] && echo "$s10why" || echo "$s19why"); invalid=$((invalid+1))
  elif [ "$s10" = "PASS" ] && [ "$s19" = "PASS" ]; then
    v="PERMITTED"; why="-"; permitted=$((permitted+1))
  else
    v="BLOCKED"; why=$([ "$s10" != "PASS" ] && echo "$s10why" || echo "$s19why"); blocked=$((blocked+1))
  fi
  echo "AIGATE slot=$slot s10=$s10 s19=$s19 verdict=$v reason=$why"
done

echo "AIGATE-SUMMARY permitted=$permitted blocked=$blocked invalid=$invalid"
[ "$invalid" -eq 0 ] || exit 1
exit 0
AIGATE
chmod +x onboard-aigate.sh

mkdir -p docs/onboarding/fixtures/aigate-pass/products/01 docs/onboarding/fixtures/aigate-invalid/products/01
printf 's10_status\tpass\ns10_rotation\tdone\ns10_incident_record\tINC-2026-0007\ns10_checked_on\t2026-01-06\ns19_status\tpass\ns19_removed_on\t2026-01-06\ns19_notification\tnot-required-by-classification\ns19_deletion_obligation\tnone\ns19_checked_on\t2026-01-06\n' \
  > docs/onboarding/fixtures/aigate-pass/products/01/gates.tsv
printf 's10_status\tpass\ns10_rotation\tdone\ns10_incident_record\tINC-2026-0007\ns10_checked_on\t2026-01-06\ns19_status\tpass\ns19_removed_on\tUNSET\ns19_notification\tdone\ns19_deletion_obligation\tnone\ns19_checked_on\t2026-01-06\n' \
  > docs/onboarding/fixtures/aigate-invalid/products/01/gates.tsv
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | A day-zero store is closed to AI-assisted work on all eight slots | `./onboard-aigate.sh \| tail -1` | `AIGATE-SUMMARY permitted=0 blocked=8 invalid=0` |
| 2 | The first blocking reason is S10, not S19 | `./onboard-aigate.sh --slot 01 \| head -1` | `AIGATE slot=01 s10=BLOCKED s19=BLOCKED verdict=BLOCKED reason=s10-gate` |
| 3 | A day-zero store is a legitimate state, not an error | `./onboard-aigate.sh >/dev/null; echo $?` | `0` |
| 4 | A fully evidenced pair permits | `OB_ROOT=docs/onboarding/fixtures/aigate-pass ./onboard-aigate.sh \| tail -1` | `AIGATE-SUMMARY permitted=1 blocked=0 invalid=0` |
| 5 | S19 claiming pass with no removal is INVALID, not BLOCKED | `OB_ROOT=docs/onboarding/fixtures/aigate-invalid ./onboard-aigate.sh \| head -1 \| awk '{print $4, $5}'` | `verdict=INVALID reason=s19-no-removal-there-is-no-rotation-equivalent-remedy` |
| 6 | A mis-stated gate fails the run | `OB_ROOT=docs/onboarding/fixtures/aigate-invalid ./onboard-aigate.sh >/dev/null 2>&1; echo $?` | `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'zero=[%s] first=[%s] rc=%s pass=[%s] invalid=[%s] invrc=%s\n' \
  "$(./onboard-aigate.sh | tail -1)" \
  "$(./onboard-aigate.sh --slot 01 | head -1)" \
  "$(./onboard-aigate.sh >/dev/null; echo $?)" \
  "$(OB_ROOT=docs/onboarding/fixtures/aigate-pass ./onboard-aigate.sh | tail -1)" \
  "$(OB_ROOT=docs/onboarding/fixtures/aigate-invalid ./onboard-aigate.sh | head -1 | awk '{print $4, $5}')" \
  "$(OB_ROOT=docs/onboarding/fixtures/aigate-invalid ./onboard-aigate.sh >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
zero=[AIGATE-SUMMARY permitted=0 blocked=8 invalid=0] first=[AIGATE slot=01 s10=BLOCKED s19=BLOCKED verdict=BLOCKED reason=s10-gate] rc=0 pass=[AIGATE-SUMMARY permitted=1 blocked=0 invalid=0] invalid=[verdict=INVALID reason=s19-no-removal-there-is-no-rotation-equivalent-remedy] invrc=1
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-06`, branch `l0/onboarding-06-aigate`, subject
`feat(root): onboard-aigate.sh, the fail-closed S10 and S19 AI-safety gates`,
`Spec: Section 96.6 L8817 L8825; Section 33; Section 97.2`, `Invariant: 111`, `AT: none`.

**STOP rule** — if criterion 1 prints anything other than `permitted=0 blocked=8`, the gate is not failing closed and
must not be committed: a gate that defaults to permitted is a gate that opens eight live repositories to AI-assisted
sessions on the strength of an empty file. Never add a code path that treats a slot whose `states.tsv` does not list
S10 or S19 as exempt — **both checks are universal floor** and run against every repository regardless of what the
assessment found; the states record what was *found*, the gates record whether the check *ran and passed*. If a real
product needs a disposition none of the listed values expresses, open
`BLOCKER L0-07-06: gate disposition <value> is not in the closed set` — widening either value set is L0's, because
it changes which repositories AI may open.

---

### L0-07-07 — The ten-row target standard, and the per-slot coverage sheet

**Size:** S · **Dependencies:** L0-07-01

The §7.1 table, transcribed into ten files, plus one coverage sheet per slot so that an assessment can be *checked*
for coverage rather than read for reassurance. The sheet is a generated shell: ten rows, every verdict `UNSET`, filled
in by the human assessor.

**No row is marked "does not apply to this profile" anywhere in this task.** Spec §96.6 (L8800) says a product on a
non-`service` `conformance_profile` *"meets the equivalent evidence its profile defines wherever the service interface
does not apply"* — which is a rule about the **answer**, not about the question. Every product answers all ten rows;
a non-`service` profile may answer `equivalent` and must then name the equivalent evidence. Deciding in advance which
rows a profile is excused from would be exactly the silent skip §96.6's honesty paragraph (L8832) warns about.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-07-standard

while IFS='|' read -r id std def; do
  [ -n "$id" ] || continue
  printf 'id\t%s\nstandard\t%s\ndefined_in\t%s\nspec_line\tL8785-L8798\n' "$id" "$std" "$def" \
    > "docs/onboarding/taxonomy/standard/$id.tsv"
done <<'STD'
T1|Repository in the company organisation branch protection from template|Section 11
T2|Valid product.yaml with ownership criticality support model|Section 15
T3|The eight make commands and required files|Section 33.1
T4|The three HTTP endpoints health version metrics|Section 41.2
T5|Three environments local staging production with parity checked|Section 33
T6|Verification contract automated UAT smoke AI eval where declared|Section 31
T7|Immutable-artifact pipeline same digest staging to production|Sections 32-34
T8|CI-only migrations backward-compatible one cycle|Section 34.3
T9|Backups with one verified restore then the rolling cadence|Section 44
T10|Boards as execution truth work through the gates|Sections 23-29
STD

for s in 01 02 03 04 05 06 07 08; do
  {
    printf '# standard.tsv — Section 96.6 target-standard coverage. Assessor input.\n'
    printf '# id\tverdict\tevidence_or_gap\tdisposition\n'
    printf '# verdict: met | gap | equivalent      disposition: scheduled-step | accepted-risk | -\n'
    for t in T1 T2 T3 T4 T5 T6 T7 T8 T9 T10; do
      printf '%s\tUNSET\tUNSET\tUNSET\n' "$t"
    done
  } > "docs/onboarding/products/$s/standard.tsv"
done
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Ten standard rows | `ls docs/onboarding/taxonomy/standard \| wc -l` | `10` |
| 2 | Ids are `T1`…`T10`, each once | `ls docs/onboarding/taxonomy/standard \| sed 's/\.tsv//' \| sort -V \| tr '\n' ' '` | `T1 T2 T3 T4 T5 T6 T7 T8 T9 T10 ` |
| 3 | Every slot has a ten-row sheet | `for f in docs/onboarding/products/*/standard.tsv; do grep -vc '^#' "$f"; done \| sort -u` | `10` |
| 4 | Every sheet row is four fields | `awk -F'\t' '!/^#/ && NF!=4' docs/onboarding/products/*/standard.tsv \| wc -l` | `0` |
| 5 | Nothing is answered yet | `awk -F'\t' '!/^#/ && $2!="UNSET"' docs/onboarding/products/*/standard.tsv \| wc -l` | `0` |
| 6 | No row was pre-excused for a profile | `grep -c 'not-applicable' docs/onboarding/products/*/standard.tsv \| awk -F: '{s+=$2} END{print s}'` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'std=%s ids=[%s] rows=%s fields=%s answered=%s excused=%s\n' \
  "$(ls docs/onboarding/taxonomy/standard | wc -l | tr -d ' ')" \
  "$(ls docs/onboarding/taxonomy/standard | sed 's/\.tsv//' | sort -V | tr '\n' ' ' | sed 's/ $//')" \
  "$(for f in docs/onboarding/products/*/standard.tsv; do grep -vc '^#' "$f"; done | sort -u | tr '\n' ',' | sed 's/,$//')" \
  "$(awk -F'\t' '!/^#/ && NF!=4' docs/onboarding/products/*/standard.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && $2!="UNSET"' docs/onboarding/products/*/standard.tsv | wc -l | tr -d ' ')" \
  "$(grep -c 'not-applicable' docs/onboarding/products/*/standard.tsv | awk -F: '{s+=$2} END{print s+0}')"
```

Expected output, exactly:

```
std=10 ids=[T1 T2 T3 T4 T5 T6 T7 T8 T9 T10] rows=10 fields=4 answered=0 excused=0
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-07`, branch `l0/onboarding-07-standard`, subject
`feat(docs): the ten-row target standard and the per-slot coverage sheet`,
`Spec: Section 96.6 L8785-L8800; Section 15.7`, `Invariant: none`.

**STOP rule** — if you find yourself wanting an eleventh row because some other section of the spec states a further
obligation, stop: the target standard is the ten rows of the L8785 table and nothing else, and extending it changes
what "onboarded" means for eight live products. Open `BLOCKER L0-07-07: target standard row <n> proposed`. Equally,
do not delete a row because a profile looks exempt — see the paragraph above; the exemption lives in the *answer*.

---

### L0-07-08 — `onboard-assess.sh` — the intake gap assessment, and what is not an assessment

**Size:** M · **Dependencies:** L0-07-07

Four properties from §7, enforced in order. The fourth is the one that matters most and is the easiest to lose:

> **A machine draft with no human `recorded_by` is not an assessment.** D72 (spec L10150) puts intake-assessment
> drafts in the closed list of machine-drafted aids that are *"wait-surface conveniences, never surfaces of record …
> confirmed by a human before any routing effect"*, and §96.6 (L8783) says plainly: *"the recorded assessment is
> always written by the human assessor (D72)."*

| Verdict | Meaning | Exit |
|---|---|---|
| `NOT-RECORDED` | `status` is `UNSET` or `machine-drafted`; no plan may be generated for this slot | 0 — a legitimate day-zero state |
| `INVALID` | the row claims `recorded` while missing `recorded_by`, `recorded_on`, `template_version`, an in-range maturity level, or a complete coverage sheet | **1** — a mis-stated fact |
| `RECORDED` | all of the above present, every one of the ten rows answered, every `gap` dispositioned, every `equivalent` evidenced | 0 |

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-08-assess

cat > onboard-assess.sh <<'ASSESS'
#!/usr/bin/env sh
# =============================================================================
# onboard-assess.sh — L0-owned. The Section 96.6 intake gap assessment checker.
# "Onboarding therefore begins with a recorded intake gap assessment per
# product, authored from the named template artifact in the control plane
# (templates/intake-gap-assessment.md) ... the recorded assessment is always
# written by the human assessor (D72)." (spec L8783)
# The template itself has NO owning lane — DR-L0-07-A. This script consumes it
# by version string only and never writes it.
# usage: onboard-assess.sh [--slot NN]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ONLY=""
[ $# -ge 2 ] && [ "$1" = "--slot" ] && ONLY="$2"

kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }
is_date() { case "$1" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;; *) return 1 ;; esac; }

recorded=0; notrec=0; invalid=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  a="$d/assessment.tsv"; sh_="$d/standard.tsv"; fa="$d/facts.tsv"
  st=$(kv "$a" status); by=$(kv "$a" recorded_by); on=$(kv "$a" recorded_on)
  tv=$(kv "$a" template_version); ml=$(kv "$a" maturity_level_at_intake)
  md=$(kv "$a" machine_drafted)
  prof=$(kv "$fa" conformance_profile)

  if [ "$st" != "recorded" ]; then
    r="no-recorded-assessment"
    [ "$st" = "machine-drafted" ] && r="machine-draft-is-not-an-assessment-D72"
    echo "ASSESS slot=$slot verdict=NOT-RECORDED reason=$r"; notrec=$((notrec+1)); continue
  fi

  why=""
  [ "$by" = "UNSET" ]                 && why="recorded-without-a-human-assessor-D72"
  [ -z "$why" ] && ! is_date "$on"    && why="recorded-without-a-date"
  [ -z "$why" ] && [ "$tv" = "UNSET" ] && why="no-template-version-DR-L0-07-A"
  if [ -z "$why" ]; then
    case "$ml" in 0|1|2|3|4|5|6|7) : ;; *) why="maturity-level-outside-0-7-Section-65" ;; esac
  fi
  if [ -z "$why" ] && [ ! -f "$sh_" ]; then why="no-coverage-sheet"; fi

  gaps=0; equivs=0
  if [ -z "$why" ]; then
    n=$(awk -F'\t' '!/^#/' "$sh_" | wc -l | tr -d ' ')
    [ "$n" -eq 10 ] || why="coverage-sheet-is-$n-rows-not-10"
  fi
  if [ -z "$why" ]; then
    OIFS=$IFS; IFS=$(printf '\t')
    while read -r id v ev disp; do
      case "$id" in \#*|'') continue ;; esac
      case "$v" in
        met) : ;;
        gap) gaps=$((gaps+1))
             case "$disp" in scheduled-step|accepted-risk) : ;;
               *) why="gap-$id-has-no-disposition"; break ;; esac ;;
        equivalent) equivs=$((equivs+1))
             [ "$ev" != "UNSET" ] || { why="equivalent-$id-names-no-evidence"; break; }
             [ "$prof" != "service" ] || { why="equivalent-$id-on-a-service-profile"; break; } ;;
        *) why="row-$id-unanswered"; break ;;
      esac
    done < "$sh_"
    IFS=$OIFS
  fi

  if [ -n "$why" ]; then
    echo "ASSESS slot=$slot verdict=INVALID reason=$why"; invalid=$((invalid+1))
  else
    echo "ASSESS slot=$slot verdict=RECORDED by=$by maturity=$ml gaps=$gaps equivalents=$equivs drafted=$md"
    recorded=$((recorded+1))
  fi
done

echo "ASSESS-SUMMARY recorded=$recorded not_recorded=$notrec invalid=$invalid"
[ "$invalid" -eq 0 ] || exit 1
exit 0
ASSESS
chmod +x onboard-assess.sh

for c in assess-ok assess-draft assess-nohuman; do
  mkdir -p "docs/onboarding/fixtures/$c/products/01"
  printf 'product_id\tUNSET\nrepository\tUNSET\nreliability_criticality\tUNSET\nbusiness_criticality\tUNSET\nonboarding_cost_band\tUNSET\nconformance_profile\tservice\nteam\tUNSET\n' \
    > "docs/onboarding/fixtures/$c/products/01/facts.tsv"
  {
    printf '# id\tverdict\tevidence_or_gap\tdisposition\n'
    printf 'T1\tmet\tbranch protection from template\t-\n'
    printf 'T2\tmet\tproduct.yaml valid\t-\n'
    printf 'T3\tgap\tfour of eight make targets missing\tscheduled-step\n'
    printf 'T4\tgap\tno /metrics endpoint\tscheduled-step\n'
    printf 'T5\tgap\tno staging\taccepted-risk\n'
    printf 'T6\tgap\tno automated suite\tscheduled-step\n'
    printf 'T7\tgap\tno digest chain\tscheduled-step\n'
    printf 'T8\tmet\tmigrations run in CI\t-\n'
    printf 'T9\tmet\trestore recorded 2026-01-04\t-\n'
    printf 'T10\tgap\tboard not the execution surface\tscheduled-step\n'
  } > "docs/onboarding/fixtures/$c/products/01/standard.tsv"
done
printf 'status\trecorded\nmachine_drafted\tyes\nrecorded_by\tassessor-1\nrecorded_on\t2026-01-08\ntemplate_version\tv1\nmaturity_level_at_intake\t1\nincident_followups\tnone\n' \
  > docs/onboarding/fixtures/assess-ok/products/01/assessment.tsv
printf 'status\tmachine-drafted\nmachine_drafted\tyes\nrecorded_by\tUNSET\nrecorded_on\tUNSET\ntemplate_version\tv1\nmaturity_level_at_intake\t1\nincident_followups\tnone\n' \
  > docs/onboarding/fixtures/assess-draft/products/01/assessment.tsv
printf 'status\trecorded\nmachine_drafted\tyes\nrecorded_by\tUNSET\nrecorded_on\t2026-01-08\ntemplate_version\tv1\nmaturity_level_at_intake\t1\nincident_followups\tnone\n' \
  > docs/onboarding/fixtures/assess-nohuman/products/01/assessment.tsv
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | A day-zero store has no assessments and is not an error | `./onboard-assess.sh \| tail -1` | `ASSESS-SUMMARY recorded=0 not_recorded=8 invalid=0` |
| 2 | Day zero exits 0 | `./onboard-assess.sh >/dev/null; echo $?` | `0` |
| 3 | A complete human-recorded assessment is accepted, gaps counted | `OB_ROOT=docs/onboarding/fixtures/assess-ok ./onboard-assess.sh \| head -1` | `ASSESS slot=01 verdict=RECORDED by=assessor-1 maturity=1 gaps=6 equivalents=0 drafted=yes` |
| 4 | A machine draft is not an assessment (D72) | `OB_ROOT=docs/onboarding/fixtures/assess-draft ./onboard-assess.sh \| head -1 \| awk '{print $3, $4}'` | `verdict=NOT-RECORDED reason=machine-draft-is-not-an-assessment-D72` |
| 5 | A machine draft does not fail the run — it is a normal waiting state | `OB_ROOT=docs/onboarding/fixtures/assess-draft ./onboard-assess.sh >/dev/null; echo $?` | `0` |
| 6 | Claiming `recorded` with no human assessor is INVALID | `OB_ROOT=docs/onboarding/fixtures/assess-nohuman ./onboard-assess.sh \| head -1 \| awk '{print $3, $4}'` | `verdict=INVALID reason=recorded-without-a-human-assessor-D72` |
| 7 | That mis-statement fails the run | `OB_ROOT=docs/onboarding/fixtures/assess-nohuman ./onboard-assess.sh >/dev/null 2>&1; echo $?` | `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'zero=[%s] rc=%s ok=[%s] draft=[%s] draftrc=%s nohuman=[%s] nhrc=%s\n' \
  "$(./onboard-assess.sh | tail -1)" \
  "$(./onboard-assess.sh >/dev/null; echo $?)" \
  "$(OB_ROOT=docs/onboarding/fixtures/assess-ok ./onboard-assess.sh | head -1)" \
  "$(OB_ROOT=docs/onboarding/fixtures/assess-draft ./onboard-assess.sh | head -1 | awk '{print $3, $4}')" \
  "$(OB_ROOT=docs/onboarding/fixtures/assess-draft ./onboard-assess.sh >/dev/null; echo $?)" \
  "$(OB_ROOT=docs/onboarding/fixtures/assess-nohuman ./onboard-assess.sh | head -1 | awk '{print $3, $4}')" \
  "$(OB_ROOT=docs/onboarding/fixtures/assess-nohuman ./onboard-assess.sh >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
zero=[ASSESS-SUMMARY recorded=0 not_recorded=8 invalid=0] rc=0 ok=[ASSESS slot=01 verdict=RECORDED by=assessor-1 maturity=1 gaps=6 equivalents=0 drafted=yes] draft=[verdict=NOT-RECORDED reason=machine-draft-is-not-an-assessment-D72] draftrc=0 nohuman=[verdict=INVALID reason=recorded-without-a-human-assessor-D72] nhrc=1
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-08`, branch `l0/onboarding-08-assess`, subject
`feat(root): onboard-assess.sh, the intake gap assessment checker`,
`Spec: Section 96.6 L8783; Section 65; Section 96.3 L8765; D72 L10150`, `Invariant: none`.

**STOP rule** — if criterion 4 prints `RECORDED`, the script is treating a machine draft as a surface of record and
must not be committed; that is the precise prohibition D72 (L10150) exists to state. Do not add a mode that lets a
draft satisfy `onboard-plan.sh` "temporarily". If `templates/intake-gap-assessment.md` does not exist anywhere in the
repository, do **not** create it — it belongs to no lane, that is `04` §8 DECISION 2 and **DR-L0-07-A** here, and this
task deliberately consumes only the `template_version` string so the checker works before the template lands.

---

### L0-07-09 — `onboard-rank.sh` — the §96.5 ordering function, total and reproducible

**Size:** M · **Dependencies:** L0-07-01

§96.5 (spec L8779), transcribed in §10.1: three keys, then the slot-number tie-break this plan adds so the computation
is total. The script computes; it never estimates. If any slot is missing any of the three keys the run **refuses**,
naming the slot and the field, because a rank computed over a guessed criticality is worse than no rank: every
deadline in the portfolio is derived from it.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-09-rank

cat > onboard-rank.sh <<'RANK'
#!/usr/bin/env sh
# =============================================================================
# onboard-rank.sh — L0-owned. The Section 96.5 sequencing rule (spec L8779):
# "highest classification.reliability_criticality first ... Within equal
# criticality, sequence by business.criticality, then by expected onboarding
# cost, cheapest first."
# Key 4 (slot ascending) is this plan's tie-break, so the order is total.
# Writes docs/onboarding/rank/NN.tsv. GENERATED — never hand-edited.
# usage: onboard-rank.sh [--check]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
CHECK=0
[ $# -ge 1 ] && [ "$1" = "--check" ] && CHECK=1

kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }
relk() { case "$1" in critical) echo 1;; high) echo 2;; medium) echo 3;; low) echo 4;; *) echo 9;; esac; }
busk() { case "$1" in high) echo 1;; medium) echo 2;; low) echo 3;; *) echo 9;; esac; }
cstk() { case "$1" in S) echo 1;; M) echo 2;; L) echo 3;; XL) echo 4;; *) echo 9;; esac; }

blocked=0
lines=""
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  f="$d/facts.tsv"
  r=$(kv "$f" reliability_criticality); b=$(kv "$f" business_criticality); c=$(kv "$f" onboarding_cost_band)
  for pair in "reliability_criticality=$r" "business_criticality=$b" "onboarding_cost_band=$c"; do
    case "$pair" in *=UNSET) echo "RANK-BLOCKED slot=$slot field=${pair%%=*} — DR-L0-07-D"; blocked=$((blocked+1)) ;; esac
  done
  rk=$(relk "$r"); bk=$(busk "$b"); ck=$(cstk "$c")
  for pair in "reliability_criticality=$r:$rk" "business_criticality=$b:$bk" "onboarding_cost_band=$c:$ck"; do
    case "$pair" in *:9)
      v=${pair%%=*}; val=${pair#*=}; val=${val%:9}
      case "$val" in UNSET) : ;; *) echo "RANK-INVALID slot=$slot field=$v value=$val"; blocked=$((blocked+1)) ;; esac ;;
    esac
  done
  lines="$lines$rk $bk $ck $slot
"
done

if [ "$blocked" -gt 0 ]; then
  echo "RANK-SUMMARY blocked=$blocked — no rank written"
  exit 1
fi

order=""
k=0
printf '%s' "$lines" | sort -k1,1n -k2,2n -k3,3n -k4,4 | while read -r rk bk ck slot; do
  [ -n "$slot" ] || continue
  k=$((k+1)); kk=$(printf '%02d' "$k")
  if [ "$CHECK" -eq 0 ]; then
    printf 'rank\t%s\nslot\t%s\nreliability_key\t%s\nbusiness_key\t%s\ncost_key\t%s\n' "$kk" "$slot" "$rk" "$bk" "$ck" \
      > "$OB/rank/$kk.tsv"
  fi
  echo "$slot" >> "$OB/rank/.order.$$"
done
order=$(tr '\n' ',' < "$OB/rank/.order.$$" | sed 's/,$//')
rm -f "$OB/rank/.order.$$"
echo "RANK order=$order"
exit 0
RANK
chmod +x onboard-rank.sh

mkdir -p docs/onboarding/fixtures/rank/rank
for s in 01 02 03 04 05 06 07 08; do mkdir -p "docs/onboarding/fixtures/rank/products/$s"; done
while IFS='|' read -r slot r b c; do
  [ -n "$slot" ] || continue
  printf 'product_id\tUNSET\nrepository\tUNSET\nreliability_criticality\t%s\nbusiness_criticality\t%s\nonboarding_cost_band\t%s\nconformance_profile\tservice\nteam\tUNSET\n' \
    "$r" "$b" "$c" > "docs/onboarding/fixtures/rank/products/$slot/facts.tsv"
done <<'FX'
01|high|high|M
02|critical|low|L
03|high|high|S
04|medium|high|S
05|critical|low|S
06|low|low|XL
07|high|medium|S
08|medium|high|S
FX
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The day-zero store refuses to rank | `./onboard-rank.sh \| tail -1` | `RANK-SUMMARY blocked=24 — no rank written` |
| 2 | Refusal is a failure, not a silent skip | `./onboard-rank.sh >/dev/null 2>&1; echo $?` | `1` |
| 3 | It names the slot and the field | `./onboard-rank.sh \| head -1` | `RANK-BLOCKED slot=01 field=reliability_criticality — DR-L0-07-D` |
| 4 | A filled fixture ranks in §96.5 order | `OB_ROOT=docs/onboarding/fixtures/rank ./onboard-rank.sh \| tail -1` | `RANK order=05,02,03,01,07,04,08,06` |
| 5 | Eight rank files are written | `ls docs/onboarding/fixtures/rank/rank/*.tsv \| wc -l` | `8` |
| 6 | Rank 01 is the cheapest of the two `critical` slots | `awk -F'\t' '$1=="slot"{print $2}' docs/onboarding/fixtures/rank/rank/01.tsv` | `05` |
| 7 | The tie between slots 04 and 08 breaks on slot number | `awk -F'\t' '$1=="slot"{print $2}' docs/onboarding/fixtures/rank/rank/06.tsv docs/onboarding/fixtures/rank/rank/07.tsv \| tr '\n' ' '` | `04 08 ` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
R=docs/onboarding/fixtures/rank
OB_ROOT=$R ./onboard-rank.sh >/dev/null
printf 'zero=[%s] rc=%s first=[%s] order=[%s] files=%s r1=%s tie=[%s]\n' \
  "$(./onboard-rank.sh | tail -1)" \
  "$(./onboard-rank.sh >/dev/null 2>&1; echo $?)" \
  "$(./onboard-rank.sh | head -1)" \
  "$(OB_ROOT=$R ./onboard-rank.sh | tail -1)" \
  "$(ls $R/rank/*.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="slot"{print $2}' $R/rank/01.tsv)" \
  "$(awk -F'\t' '$1=="slot"{print $2}' $R/rank/06.tsv $R/rank/07.tsv | tr '\n' ' ' | sed 's/ $//')"
```

Expected output, exactly:

```
zero=[RANK-SUMMARY blocked=24 — no rank written] rc=1 first=[RANK-BLOCKED slot=01 field=reliability_criticality — DR-L0-07-D] order=[RANK order=05,02,03,01,07,04,08,06] files=8 r1=05 tie=[04 08]
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-09`, branch `l0/onboarding-09-rank`, subject
`feat(root): onboard-rank.sh, the Section 96.5 ordering function`,
`Spec: Section 96.5 L8779; Section 15.1; Section 99.2`, `Invariant: none`.

**STOP rule** — if the day-zero run prints an order instead of `blocked=24`, the script has defaulted a missing
criticality and must not be committed. **Never** infer a criticality from a product's name, its traffic, its
repository size or anything else: the three values are L0's under **DR-L0-07-D**, and a wrong `reliability_criticality`
moves a product's whole onboarding — and therefore its Red-signal deadline — to the wrong end of a two-quarter queue.
Estimating an `onboarding_cost_band` is the same prohibition; the bands are §99.2's complexity bands and belong to
whoever prices the work. If a real product's criticality is genuinely one the §15.1 vocabulary does not contain, open
`BLOCKER L0-07-09: criticality value <v> is outside the Section 15.1 vocabulary`.

---

### L0-07-10 — `onboard-stream.sh` — the single-holder DevOps serialiser (§73.1)

**Size:** L · **Dependencies:** L0-07-01

Spec §73.1 (L6005) is a capacity fact with a mechanical consequence: *"Brownfield onboarding and platform work
serialise on DevOps capacity — only one such stream can proceed at a time."* This script is that sentence, enforced.
It is an append-only claim log with a single-holder rule; §4.1 fixes which phases occupy the stream, and platform work
is a first-class claim rather than something that happens invisibly somewhere else.

**Directory-per-item, both directions.** A claim writes one file under `stream/claims/`; a release writes one file
under `stream/releases/`. A release never edits the claim it releases, so the log is append-only in the strict sense
and two people working from two clones cannot conflict (PARTITION rule 3).

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-10-stream

cat > onboard-stream.sh <<'STREAM'
#!/usr/bin/env sh
# =============================================================================
# onboard-stream.sh — L0-owned. The DevOps-capacity serialiser.
# MasterSpec v4.0 Section 73.1 (spec L6005): "Brownfield onboarding and platform
# work serialise on DevOps capacity — only one such stream can proceed at a
# time — and the staffing diagnosis treats this serialisation as its own
# constraint shape, distinct from aggregate engineering demand."
# Occupying phases (this plan section 4.1): OT-P4, OT-P6, platform.
# Append-only: a claim writes one file; a release writes another. Nothing edits.
# usage: onboard-stream.sh holder | check
#        onboard-stream.sh claim <product|platform> <ref> <OT-P4|OT-P6|platform> <YYYY-MM-DD>
#        onboard-stream.sh release <seq> <YYYY-MM-DD>
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
C="$OB/stream/claims"; R="$OB/stream/releases"
is_date() { case "$1" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;; *) return 1 ;; esac; }
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }

held() {                       # prints the seq of every unreleased claim
  for f in "$C"/*.tsv; do
    [ -f "$f" ] || continue
    s=$(kv "$f" seq)
    [ -f "$R/$s.tsv" ] || echo "$s"
  done
}

case "${1:-}" in
  holder)
    n=0
    for s in $(held); do
      n=$((n+1))
      f=$(ls "$C"/"$s"-*.tsv 2>/dev/null | head -1)
      echo "STREAM HOLDER seq=$s kind=$(kv "$f" kind) ref=$(kv "$f" ref) phase=$(kv "$f" phase) since=$(kv "$f" claimed_on)"
    done
    [ "$n" -eq 0 ] && echo "STREAM FREE"
    exit 0 ;;
  check)
    n=$(held | wc -l | tr -d ' ')
    bad=0
    for f in "$C"/*.tsv; do
      [ -f "$f" ] || continue
      p=$(kv "$f" phase); k=$(kv "$f" kind)
      case "$p" in OT-P4|OT-P6|platform) : ;; *) echo "STREAM-INVALID seq=$(kv "$f" seq) phase=$p does not occupy the stream (section 4.1)"; bad=$((bad+1)) ;; esac
      case "$k" in product|platform) : ;; *) echo "STREAM-INVALID seq=$(kv "$f" seq) kind=$k"; bad=$((bad+1)) ;; esac
    done
    echo "STREAM-CHECK claims=$(ls "$C" 2>/dev/null | wc -l | tr -d ' ') open=$n invalid=$bad"
    { [ "$n" -le 1 ] && [ "$bad" -eq 0 ]; } || exit 1
    exit 0 ;;
  claim)
    [ $# -eq 5 ] || { echo "usage: onboard-stream.sh claim <kind> <ref> <phase> <date>" >&2; exit 2; }
    kind="$2"; ref="$3"; phase="$4"; when="$5"
    case "$kind"  in product|platform) : ;; *) echo "BAD-KIND $kind" >&2; exit 2 ;; esac
    case "$phase" in OT-P4|OT-P6|platform) : ;; *) echo "PHASE-DOES-NOT-OCCUPY-THE-STREAM $phase (section 4.1)" >&2; exit 2 ;; esac
    is_date "$when" || { echo "NOT-A-DATE $when" >&2; exit 2; }
    h=$(held | head -1)
    if [ -n "$h" ]; then
      hf=$(ls "$C"/"$h"-*.tsv 2>/dev/null | head -1)
      echo "STREAM BUSY holder=$h ref=$(kv "$hf" ref) phase=$(kv "$hf" phase) — Section 73.1 permits one stream at a time"
      exit 1
    fi
    n=$(ls "$C" 2>/dev/null | wc -l | tr -d ' '); n=$((n+1)); seq=$(printf '%03d' "$n")
    printf 'seq\t%s\nkind\t%s\nref\t%s\nphase\t%s\nclaimed_on\t%s\n' "$seq" "$kind" "$ref" "$phase" "$when" \
      > "$C/$seq-$kind-$ref.tsv"
    echo "STREAM CLAIMED seq=$seq kind=$kind ref=$ref phase=$phase on=$when"
    exit 0 ;;
  release)
    [ $# -eq 3 ] || { echo "usage: onboard-stream.sh release <seq> <date>" >&2; exit 2; }
    seq="$2"; when="$3"
    is_date "$when" || { echo "NOT-A-DATE $when" >&2; exit 2; }
    ls "$C"/"$seq"-*.tsv >/dev/null 2>&1 || { echo "NO-SUCH-CLAIM $seq" >&2; exit 1; }
    [ -f "$R/$seq.tsv" ] && { echo "ALREADY-RELEASED $seq" >&2; exit 1; }
    printf 'seq\t%s\nreleased_on\t%s\n' "$seq" "$when" > "$R/$seq.tsv"
    echo "STREAM RELEASED seq=$seq on=$when"
    exit 0 ;;
  *) echo "usage: onboard-stream.sh holder|check|claim|release" >&2; exit 2 ;;
esac
STREAM
chmod +x onboard-stream.sh

mkdir -p docs/onboarding/fixtures/stream-double/stream/claims docs/onboarding/fixtures/stream-double/stream/releases
printf 'seq\t001\nkind\tproduct\nref\tslot-05\nphase\tOT-P4\nclaimed_on\t2026-02-02\n' \
  > docs/onboarding/fixtures/stream-double/stream/claims/001-product-slot-05.tsv
printf 'seq\t002\nkind\tplatform\nref\tplatform-a\nphase\tplatform\nclaimed_on\t2026-02-03\n' \
  > docs/onboarding/fixtures/stream-double/stream/claims/002-platform-platform-a.tsv
```

**Acceptance criteria**

Every command below runs against the scratch fixture, **never against the real store**: a claim written while testing
would otherwise be committed as a real occupancy of the DevOps stream. Reset it first, and the sequence is then
deterministic and repeatable:

**Commands**

```bash
cd "$CP_ROOT"
export S=docs/onboarding/fixtures/stream-scratch
rm -rf "$S"; mkdir -p "$S/stream/claims" "$S/stream/releases"
```

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | An empty log is free | `OB_ROOT=$S ./onboard-stream.sh holder` | `STREAM FREE` |
| 2 | A first claim succeeds | `OB_ROOT=$S ./onboard-stream.sh claim product slot-05 OT-P4 2026-02-02` | `STREAM CLAIMED seq=001 kind=product ref=slot-05 phase=OT-P4 on=2026-02-02` |
| 3 | **A second concurrent claim is refused** | `OB_ROOT=$S ./onboard-stream.sh claim platform platform-a platform 2026-02-03` | `STREAM BUSY holder=001 ref=slot-05 phase=OT-P4 — Section 73.1 permits one stream at a time` |
| 4 | …and the refusal is a non-zero exit | `OB_ROOT=$S ./onboard-stream.sh claim platform platform-a platform 2026-02-03 >/dev/null 2>&1; echo $?` | `1` |
| 5 | After release the stream is free again | `OB_ROOT=$S ./onboard-stream.sh release 001 2026-02-16 >/dev/null; OB_ROOT=$S ./onboard-stream.sh holder` | `STREAM FREE` |
| 6 | Releasing edited nothing — the claim still reads as claimed | `awk -F'\t' '$1=="claimed_on"{print $2}' $S/stream/claims/001-product-slot-05.tsv` | `2026-02-02` |
| 7 | A phase that does not occupy the stream is refused (§4.1) | `OB_ROOT=$S ./onboard-stream.sh claim product slot-05 OT-P5 2026-02-17 >/dev/null 2>&1; echo $?` | `2` |
| 8 | Two open claims fail `check` | `OB_ROOT=docs/onboarding/fixtures/stream-double ./onboard-stream.sh check \| tail -1` | `STREAM-CHECK claims=2 open=2 invalid=0` |
| 9 | …with a non-zero exit | `OB_ROOT=docs/onboarding/fixtures/stream-double ./onboard-stream.sh check >/dev/null 2>&1; echo $?` | `1` |
| 10 | A double release is refused | `OB_ROOT=$S ./onboard-stream.sh release 001 2026-02-17 >/dev/null 2>&1; echo $?` | `1` |
| 11 | The real store carries no test claim | `ls docs/onboarding/stream/claims \| wc -l` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
S=docs/onboarding/fixtures/stream-scratch
rm -rf "$S"; mkdir -p "$S/stream/claims" "$S/stream/releases"
a=$(OB_ROOT=$S ./onboard-stream.sh holder)
b=$(OB_ROOT=$S ./onboard-stream.sh claim product slot-05 OT-P4 2026-02-02)
c=$(OB_ROOT=$S ./onboard-stream.sh claim platform platform-a platform 2026-02-03 2>&1)
crc=$(OB_ROOT=$S ./onboard-stream.sh claim platform platform-a platform 2026-02-03 >/dev/null 2>&1; echo $?)
OB_ROOT=$S ./onboard-stream.sh release 001 2026-02-16 >/dev/null
d=$(OB_ROOT=$S ./onboard-stream.sh holder)
e=$(OB_ROOT=$S ./onboard-stream.sh claim product slot-05 OT-P5 2026-02-17 >/dev/null 2>&1; echo $?)
f=$(OB_ROOT=docs/onboarding/fixtures/stream-double ./onboard-stream.sh check | tail -1)
g=$(OB_ROOT=$S ./onboard-stream.sh release 001 2026-02-17 >/dev/null 2>&1; echo $?)
printf 'free=[%s] claim=[%s] busy=[%s] busyrc=%s after=[%s] wrongphase=%s double=[%s] rerelease=%s real=%s\n' \
  "$a" "$b" "$c" "$crc" "$d" "$e" "$f" "$g" "$(ls docs/onboarding/stream/claims | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
free=[STREAM FREE] claim=[STREAM CLAIMED seq=001 kind=product ref=slot-05 phase=OT-P4 on=2026-02-02] busy=[STREAM BUSY holder=001 ref=slot-05 phase=OT-P4 — Section 73.1 permits one stream at a time] busyrc=1 after=[STREAM FREE] wrongphase=2 double=[STREAM-CHECK claims=2 open=2 invalid=0] rerelease=1 real=0
```

The two `claim platform …` calls are deliberate: the first captures the message, the second captures the exit code.
If you collapse them, one of the two halves of criterion 3–4 silently stops being tested. `real=0` is the guard that
the whole exercise ran in the fixture: a test claim committed into `docs/onboarding/stream/claims/` would read, to
every later run of `holder`, as a product genuinely holding the DevOps stream.

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-10`, branch `l0/onboarding-10-stream`, subject
`feat(root): onboard-stream.sh, the single-holder DevOps serialiser`,
`Spec: Section 73.1 L6005; Section 98.2 Phase 4 L9050 and Phase 6 L9070`, `Invariant: none`.

**STOP rule** — if criterion 3 succeeds instead of printing `STREAM BUSY`, the serialiser does not serialise and must
not be committed: the entire §10.3 wave picture, and with it the honest two-quarter estimate of Spec §96.1, rests on
this one refusal. Do not add a `--force` flag, and do not add a second stream "for platform work" — §73.1 puts
brownfield onboarding and platform work on the *same* capacity, which is why platform work is a claim here rather than
an exemption. If real work genuinely needs the stream while it is held, that is a **sequencing decision** and belongs
to L0 under §96.5: open `BLOCKER L0-07-10: stream contention between <a> and <b>` and let L0 order them. Deciding
which of two waiting streams goes first is forbidden action **OB-F3**.

---

### L0-07-11 — `onboard-plan.sh` — the per-product phase plan, composed from the states

**Size:** L · **Dependencies:** L0-07-03, L0-07-04, L0-07-09, L0-07-10

This is §10.2 and §10.4 turned into a generator. It emits, per slot, the **standard six phase rows in the standard
order**, preceded by one prereq row per applicable starting state and, for a slot carrying S3, the literal `NOTE` row
of §6.1. It composes; it never removes and it never reorders — reordering `OT-P4`…`OT-P7` for any product is
forbidden action **OB-F3** and belongs to L0's §96.5 sequencing decision.

It also creates the four per-slot phase anchors (`OT-P4-NN` … `OT-P7-NN`), unset, so that `onboard-when.sh` has
something to resolve against the day a phase actually starts. **An expression is written; a date is never written**
(D99, and **OB-F2**).

Four refusals, each naming the missing input rather than proceeding on a default:

| Refusal | Because |
|---|---|
| `no-rank` | §96.5 sequencing is the input to every `OT-P4` expression; without it the serialisation row cannot be written. **DR-L0-07-D** |
| `no-recorded-assessment` | §96.6 L8783: the assessment *"is the input to the Section 98 per-product phase plan"* |
| `no-states-recorded` | a plan whose prereqs were composed from an empty state set is a plan that silently drops the S3 CD gate |
| `prereq-<token>-unrecorded` | §10.4 — an applicable state's prereq artifact does not exist yet |

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-11-plan

cat > onboard-plan.sh <<'PLAN'
#!/usr/bin/env sh
# =============================================================================
# onboard-plan.sh — L0-owned. Generates docs/onboarding/products/NN/plan.tsv.
# Section 10.2 of implementation/lanes/L0-07-onboarding-track.md, which is
# MasterSpec v4.0 Section 98.2 Phases 4-7 sequenced under Section 96.5 and
# serialised under Section 73.1 (spec L6005).
# GENERATED — never hand-edited (invariant 46, spec L9514).
# Writes EXPRESSIONS, never dates (D99, spec L10192).
# usage: onboard-plan.sh [--slot NN] [--check]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ONLY=""; CHECK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --slot)  ONLY="$2"; shift 2 ;;
    --check) CHECK=1;   shift ;;
    *) echo "usage: onboard-plan.sh [--slot NN] [--check]" >&2; exit 2 ;;
  esac
done

kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }

rank_of()  { awk -F'\t' -v s="$1" 'FNR==1{r=""} $1=="rank"{r=$2} $1=="slot" && $2==s{print r}' "$OB"/rank/*.tsv 2>/dev/null; }
slot_at()  { f="$OB/rank/$1.tsv"; [ -f "$f" ] && awk -F'\t' '$1=="slot"{print $2}' "$f"; }
prereq_of(){ f="$OB/taxonomy/states/$1.tsv"; [ -f "$f" ] && awk -F'\t' '$1=="prereq"{print $2}' "$f"; }

# The prereq token -> artifact that satisfies it (this plan, section 10.4).
prereq_file() {
  case "$1" in
    cd-gate)                 echo "cd-gate.tsv" ;;
    s10-gate|s19-gate)       echo "gates.tsv" ;;
    repo-in-org)             echo "floor/F7.tsv" ;;   # section 10.4: satisfied by floor row F7 and by nothing else
    restore-target|environment-mapping|lifecycle-decision|shared-repo-decl|equivalent-identity) echo "interim.tsv" ;;
    profile-client-app|profile-customer-hosted|profile-library-or-batch) echo "facts.tsv" ;;
    store-account-transfer|shared-db-ownership) echo "interim.tsv" ;;
    *) echo "" ;;
  esac
}

blocked=0; written=0; stale=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue

  k=$(rank_of "$slot")
  if [ -z "$k" ]; then echo "PLAN-BLOCKED slot=$slot reason=no-rank — DR-L0-07-D"; blocked=$((blocked+1)); continue; fi
  if [ "$(kv "$d/assessment.tsv" status)" != "recorded" ]; then
    echo "PLAN-BLOCKED slot=$slot reason=no-recorded-assessment — Section 96.6 L8783"; blocked=$((blocked+1)); continue
  fi
  states=$(kv "$d/states.tsv" states)
  if [ "$states" = "UNSET" ] || [ -z "$states" ]; then
    echo "PLAN-BLOCKED slot=$slot reason=no-states-recorded"; blocked=$((blocked+1)); continue
  fi

  # ---- prereq rows, composed from the recorded states and notes (section 10.4)
  rows=""; bad=""; has_s3=no
  for sid in $(printf '%s' "$states" | tr ',' ' ') $(printf '%s' "$(kv "$d/states.tsv" notes)" | tr ',' ' '); do
    [ "$sid" = "UNSET" ] && continue
    case "$sid" in N1) t="store-account-transfer" ;; N2) t="shared-db-ownership" ;; *) t=$(prereq_of "$sid") ;; esac
    [ "$sid" = "S3" ] && has_s3=yes
    [ -z "$t" ] && { echo "PLAN-BLOCKED slot=$slot reason=unknown-state-$sid"; bad="x"; break; }
    [ "$t" = "-" ] && continue
    pf=$(prereq_file "$t")
    if [ -n "$pf" ] && [ ! -f "$d/$pf" ]; then bad="prereq-$t-unrecorded"; break; fi
    # section 10.4: a prereq is satisfied by the RECORDED VALUE, not by the file existing.
    # Gates must carry the specific status field; floor rows must show the gating action closed.
    # Negative test: file present but field value wrong → expect prereq-<token>-unrecorded.
    case "$t" in
      s10-gate)    grep -q 's10_status=pass' "$d/gates.tsv"    2>/dev/null || { bad="prereq-s10-gate-unrecorded";   break; } ;;
      repo-in-org) grep -q 'status=closed'   "$d/floor/F7.tsv" 2>/dev/null || { bad="prereq-repo-in-org-unrecorded"; break; } ;;
      profile-client-app)       [ "$(kv "$d/facts.tsv" conformance_profile)" = "client-app" ]      || { bad="prereq-$t-unrecorded"; break; } ;;
      profile-customer-hosted)  [ "$(kv "$d/facts.tsv" conformance_profile)" = "customer-hosted" ] || { bad="prereq-$t-unrecorded"; break; } ;;
      profile-library-or-batch) case "$(kv "$d/facts.tsv" conformance_profile)" in library|batch) : ;; *) bad="prereq-$t-unrecorded"; break ;; esac ;;
    esac
    r=$(printf 'PREREQ:%s\t-\t%s\t-\tUNSET' "$t" "$sid")
    rows="$rows$r
"
  done
  if [ -n "$bad" ]; then
    [ "$bad" = "x" ] || echo "PLAN-BLOCKED slot=$slot reason=$bad"
    blocked=$((blocked+1)); continue
  fi
  if [ "$has_s3" = yes ]; then
    r=$(printf 'NOTE:S3-verification-contract-first\t-\tS3\t-\tspec-L8810-standard-order-already-satisfies-it')
    rows="$rows$r
"
  fi

  # ---- the six phase rows, in the standard order, always (OB-F3)
  prev=""
  if [ "$k" != "01" ]; then
    pk=$(printf '%02d' $(( ${k#0} - 1 )))
    prev=$(slot_at "$pk")
  fi
  if [ -n "$prev" ]; then p4="max(S3+0w,OT-P6-$prev+0w)"; else p4="S3+0w"; fi

  tmp="$d/.plan.$$"
  {
    printf '# plan.tsv — GENERATED by onboard-plan.sh. Never hand-edited. rank=%s\n' "$k"
    printf '# phase\tearliest_expr\tgate\tserialiser\tstatus\n'
    printf '%s' "$rows"
    printf 'OT-FLOOR\tOT-FLOOR+0w\tnone\tproduct-team\tUNSET\n'
    printf 'OT-INTAKE\tOT-FLOOR+0w\tintake-template\thuman-assessor\tUNSET\n'
    printf 'OT-P4\t%s\tintake-recorded\tdevops-stream\tUNSET\n' "$p4"
    printf 'OT-P5\tOT-P4-%s+0w\tOT-P4-complete\tqa-takeover\tUNSET\n' "$slot"
    printf 'OT-P6\tmax(OT-P5-%s+0w,S3+0w)\tOT-P5-complete\tdevops-stream\tUNSET\n' "$slot"
    printf 'OT-P7\tOT-P6-%s+0w\tplan-checker\tnone\tUNSET\n' "$slot"
  } > "$tmp"

  if [ "$CHECK" -eq 1 ]; then
    if [ ! -f "$d/plan.tsv" ] || ! cmp -s "$tmp" "$d/plan.tsv"; then
      echo "PLAN-STALE slot=$slot — regenerate with onboard-plan.sh"; stale=$((stale+1))
    fi
    rm -f "$tmp"
  else
    mv "$tmp" "$d/plan.tsv"
    for ph in OT-P4 OT-P5 OT-P6 OT-P7; do
      a="$OB/anchors/$ph-$slot.tsv"
      [ -f "$a" ] || printf 'token\t%s\ndate\tUNSET\ndeclared_by\tUNSET\n' "$ph-$slot" > "$a"
    done
    echo "PLAN-WRITTEN slot=$slot rank=$k prereqs=$(printf '%s' "$rows" | grep -c '^PREREQ:') phases=6"
  fi
  written=$((written+1))
done

echo "PLAN-SUMMARY planned=$written blocked=$blocked stale=$stale"
{ [ "$blocked" -eq 0 ] && [ "$stale" -eq 0 ]; } || exit 1
exit 0
PLAN
chmod +x onboard-plan.sh

# ---- fixture: two slots, ranked, one of them carrying S3 and S7
P=docs/onboarding/fixtures/plan
rm -rf "$P"; mkdir -p "$P/rank" "$P/anchors" "$P/products/01" "$P/products/02"
printf 'rank\t01\nslot\t02\nreliability_key\t1\nbusiness_key\t1\ncost_key\t1\n' > "$P/rank/01.tsv"
printf 'rank\t02\nslot\t01\nreliability_key\t2\nbusiness_key\t1\ncost_key\t1\n' > "$P/rank/02.tsv"
for s in 01 02; do
  printf 'product_id\tUNSET\nrepository\tUNSET\nreliability_criticality\thigh\nbusiness_criticality\thigh\nonboarding_cost_band\tS\nconformance_profile\tservice\nteam\tUNSET\n' > "$P/products/$s/facts.tsv"
  printf 'status\trecorded\nmachine_drafted\tno\nrecorded_by\tassessor-1\nrecorded_on\t2026-01-08\ntemplate_version\tv1\nmaturity_level_at_intake\t1\nincident_followups\tnone\n' > "$P/products/$s/assessment.tsv"
  printf 'block_present\tyes\naccepted_risks_recorded\tyes\ninterim_response_authored\tyes\nverification_contract\tabsent\n' > "$P/products/$s/interim.tsv"
done
printf 'states\tS3,S7\nnotes\tUNSET\nassessed_on\t2026-01-08\n' > "$P/products/01/states.tsv"
printf 'states\tS1\nnotes\tUNSET\nassessed_on\t2026-01-08\n'    > "$P/products/02/states.tsv"
printf 'pattern\tapproval-webhook\napprover\tapprover-1\nrecorded_on\t2026-01-08\naccepted_risk\tAR-2026-0011\n' > "$P/products/01/cd-gate.tsv"
cp -r docs/onboarding/taxonomy "$P/taxonomy"
OB_ROOT=$P ./onboard-plan.sh >/dev/null
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The day-zero store plans nothing and says why | `./onboard-plan.sh \| tail -1` | `PLAN-SUMMARY planned=0 blocked=8 stale=0` |
| 2 | The first reason is the missing rank | `./onboard-plan.sh \| head -1` | `PLAN-BLOCKED slot=01 reason=no-rank — DR-L0-07-D` |
| 3 | The fixture plans both slots | `OB_ROOT=docs/onboarding/fixtures/plan ./onboard-plan.sh \| tail -1` | `PLAN-SUMMARY planned=2 blocked=0 stale=0` |
| 4 | **Rank 2's `OT-P4` waits on rank 1's `OT-P6`** (§73.1) | `awk -F'\t' '$1=="OT-P4"{print $2}' docs/onboarding/fixtures/plan/products/01/plan.tsv` | `max(S3+0w,OT-P6-02+0w)` |
| 5 | Rank 1's `OT-P4` waits only on the sync point | `awk -F'\t' '$1=="OT-P4"{print $2}' docs/onboarding/fixtures/plan/products/02/plan.tsv` | `S3+0w` |
| 6 | The S3 slot gains the `cd-gate` prereq and the note | `grep -c '^PREREQ:cd-gate\|^NOTE:S3' docs/onboarding/fixtures/plan/products/01/plan.tsv` | `2` |
| 7 | The order is the standard order for both slots | `awk -F'\t' '/^OT-/{printf "%s ", $1}' docs/onboarding/fixtures/plan/products/01/plan.tsv` | `OT-FLOOR OT-INTAKE OT-P4 OT-P5 OT-P6 OT-P7 ` |
| 8 | Four phase anchors were created per slot, all unset | `awk -F'\t' '$1=="date"{print $2}' docs/onboarding/fixtures/plan/anchors/OT-P*-01.tsv \| sort -u` | `UNSET` |
| 9 | No plan contains an absolute week label | `OB_ROOT=docs/onboarding/fixtures/plan ./onboard-when.sh lint` | `WHEN-LINT files_with_labels=0` |
| 10 | A regenerated plan is byte-identical (`--check` is stable) | `OB_ROOT=docs/onboarding/fixtures/plan ./onboard-plan.sh --check \| tail -1` | `PLAN-SUMMARY planned=2 blocked=0 stale=0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
P=docs/onboarding/fixtures/plan
printf 'zero=[%s] first=[%s] fixture=[%s] p4rank2=%s p4rank1=%s s3rows=%s order=[%s] anchors=%s lint=[%s] check=[%s]\n' \
  "$(./onboard-plan.sh | tail -1)" \
  "$(./onboard-plan.sh | head -1)" \
  "$(OB_ROOT=$P ./onboard-plan.sh | tail -1)" \
  "$(awk -F'\t' '$1=="OT-P4"{print $2}' $P/products/01/plan.tsv)" \
  "$(awk -F'\t' '$1=="OT-P4"{print $2}' $P/products/02/plan.tsv)" \
  "$(grep -c '^PREREQ:cd-gate\|^NOTE:S3' $P/products/01/plan.tsv)" \
  "$(awk -F'\t' '/^OT-/{printf "%s ", $1}' $P/products/01/plan.tsv | sed 's/ $//')" \
  "$(awk -F'\t' '$1=="date"{print $2}' $P/anchors/OT-P*-01.tsv | sort -u)" \
  "$(OB_ROOT=$P ./onboard-when.sh lint)" \
  "$(OB_ROOT=$P ./onboard-plan.sh --check | tail -1)"
```

Expected output, exactly:

```
zero=[PLAN-SUMMARY planned=0 blocked=8 stale=0] first=[PLAN-BLOCKED slot=01 reason=no-rank — DR-L0-07-D] fixture=[PLAN-SUMMARY planned=2 blocked=0 stale=0] p4rank2=max(S3+0w,OT-P6-02+0w) p4rank1=S3+0w s3rows=2 order=[OT-FLOOR OT-INTAKE OT-P4 OT-P5 OT-P6 OT-P7] anchors=UNSET lint=[WHEN-LINT files_with_labels=0] check=[PLAN-SUMMARY planned=2 blocked=0 stale=0]
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-11`, branch `l0/onboarding-11-plan`, subject
`feat(root): onboard-plan.sh, the per-product phase plan composed from the states`,
`Spec: Section 98.2 L9050-L9089; Section 96.5 L8779; Section 96.6 L8783 L8810; Section 73.1 L6005; D99 L10192`,
`Invariant: 46`.

**STOP rule** — if criterion 4 prints `S3+0w` for slot 01, the serialisation row has been lost and the plan must not be
committed: without it every product's `OT-P4` looks startable at once, the §10.3 wave picture collapses, and the plan
promises a portfolio onboarded in three weeks that Spec §96.1 says takes *"roughly two quarters"*. If you believe a
particular product should take `OT-P5` before `OT-P4`, or `OT-P6` before `OT-P5`, do **not** reorder — read §6.1: the
standard order already satisfies S3's out-of-order sentence, and reordering is **OB-F3**. If a recorded state has no
prereq mapping in `prereq_file()`, the script blocks rather than skipping the prereq; open
`BLOCKER L0-07-11: prereq token <t> has no satisfying artifact` and let L0 name it.

---

### L0-07-12 — `onboard-qa.sh` — the QA-takeover SLA clock, and the signal that is never a person

**Size:** M · **Dependencies:** L0-07-01, L0-07-04

§8, mechanised. The clock starts at the **AI-drafted suite landing**, not at the phase start; it runs 14 days, the
initial calibrated value of "two weeks"; it stops when QA *"has reviewed, corrected and taken ownership"*. A breach is
`SIG-08` (QA bottleneck, spec L4537) *"at the weekly review, never a personal one"*.

**The script never prints `taken_over_by` on a breach line.** That is not decoration: Spec §96.6 (L8830) says the
breach is a capacity signal and not a personal one, and a breach line carrying a person's name is a personal one no
matter what the surrounding prose claims.

**Three exit codes**, because a breach and a corrupt record are not the same event:

| Exit | Meaning | What the track gate of L0-07-14 does with it |
|---|---|---|
| `0` | no breach | passes |
| `3` | one or more breaches | **reports** the signal; does not fail the gate. A breach is a true fact about capacity, not a defect in the store |
| `1` | the clock itself is mis-stated — ownership before landing, ownership with no owner, a non-numeric SLA | **fails** the gate |

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-12-qa

cat > onboard-qa.sh <<'QA'
#!/usr/bin/env sh
# =============================================================================
# onboard-qa.sh — L0-owned. The Section 96.6 QA-takeover SLA clock (spec L8830):
# "initial calibrated value: two weeks from the AI-drafted suite landing to QA
# having reviewed, corrected and taken ownership - and a breached SLA is a
# QA-capacity signal at the weekly review, never a personal one."
# Signal on breach: SIG-08 (spec L4537). NEVER prints a person on a breach line.
# The 14 is calibrated configuration: changing it is L0D-17, not an edit here.
# usage: onboard-qa.sh [--asof YYYY-MM-DD] [--slot NN]
# exit: 0 clean | 3 breach present (a signal, not a defect) | 1 invalid clock
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ASOF=$(date -u +%Y-%m-%d); ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --asof) ASOF="$2"; shift 2 ;;
    --slot) ONLY="$2"; shift 2 ;;
    *) echo "usage: onboard-qa.sh [--asof YYYY-MM-DD] [--slot NN]" >&2; exit 2 ;;
  esac
done
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }
is_date() { case "$1" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;; *) return 1 ;; esac; }
days_between() { a=$(date -u -d "$1" +%s); b=$(date -u -d "$2" +%s); echo $(( (b - a) / 86400 )); }

breach=0; invalid=0; landed=0; owned=0; waiting=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  f="$d/qa.tsv"
  ld=$(kv "$f" suite_landed_on); to=$(kv "$f" taken_over_on)
  by=$(kv "$f" taken_over_by);   sla=$(kv "$f" sla_days)

  case "$sla" in ''|*[!0-9]*) echo "QA-INVALID slot=$slot reason=sla_days-not-a-number"; invalid=$((invalid+1)); continue ;; esac

  if [ "$ld" = "UNSET" ]; then
    if [ "$to" != "UNSET" ]; then
      echo "QA-INVALID slot=$slot reason=ownership-recorded-before-any-suite-landed"; invalid=$((invalid+1))
    else
      echo "QA slot=$slot state=not-landed"
    fi
    continue
  fi
  is_date "$ld" || { echo "QA-INVALID slot=$slot reason=suite_landed_on-not-a-date"; invalid=$((invalid+1)); continue; }
  landed=$((landed+1))

  if [ "$to" != "UNSET" ]; then
    is_date "$to" || { echo "QA-INVALID slot=$slot reason=taken_over_on-not-a-date"; invalid=$((invalid+1)); continue; }
    [ "$by" != "UNSET" ] || { echo "QA-INVALID slot=$slot reason=ownership-without-an-owner"; invalid=$((invalid+1)); continue; }
    n=$(days_between "$ld" "$to")
    [ "$n" -ge 0 ] || { echo "QA-INVALID slot=$slot reason=taken-over-before-the-suite-landed"; invalid=$((invalid+1)); continue; }
    owned=$((owned+1))
    if [ "$n" -gt "$sla" ]; then
      echo "QA-SLA BREACH slot=$slot days=$n sla=$sla signal=SIG-08 state=owned-late"
      breach=$((breach+1))
    else
      echo "QA slot=$slot state=owned days=$n sla=$sla"
    fi
  else
    n=$(days_between "$ld" "$ASOF")
    waiting=$((waiting+1))
    if [ "$n" -gt "$sla" ]; then
      echo "QA-SLA BREACH slot=$slot days=$n sla=$sla signal=SIG-08 state=awaiting-takeover"
      breach=$((breach+1))
    else
      echo "QA slot=$slot state=awaiting-takeover days=$n sla=$sla"
    fi
  fi
done

echo "QA-SUMMARY landed=$landed owned=$owned awaiting=$waiting breaches=$breach invalid=$invalid asof=$ASOF"
[ "$invalid" -eq 0 ] || exit 1
[ "$breach"  -eq 0 ] || exit 3
exit 0
QA
chmod +x onboard-qa.sh

Q=docs/onboarding/fixtures/qa
rm -rf "$Q"; mkdir -p "$Q/products/01" "$Q/products/02" "$Q/products/03"
printf 'suite_landed_on\t2026-02-02\nsla_days\t14\ntaken_over_on\tUNSET\ntaken_over_by\tUNSET\nstatus\tawaiting\n'          > "$Q/products/01/qa.tsv"
printf 'suite_landed_on\t2026-02-02\nsla_days\t14\ntaken_over_on\t2026-02-10\ntaken_over_by\tqa-1\nstatus\towned\n'        > "$Q/products/02/qa.tsv"
printf 'suite_landed_on\tUNSET\nsla_days\t14\ntaken_over_on\t2026-02-10\ntaken_over_by\tqa-1\nstatus\towned\n'             > "$Q/products/03/qa.tsv"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Day zero: nothing has landed, nothing is late | `./onboard-qa.sh --asof 2026-03-01 \| tail -1` | `QA-SUMMARY landed=0 owned=0 awaiting=0 breaches=0 invalid=0 asof=2026-03-01` |
| 2 | Day zero exits clean | `./onboard-qa.sh --asof 2026-03-01 >/dev/null; echo $?` | `0` |
| 3 | Inside the window, no breach | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-02-10 --slot 01` | `QA slot=01 state=awaiting-takeover days=8 sla=14` |
| 4 | On day 14 exactly, still no breach | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-02-16 --slot 01 \| awk '{print $3}'` | `state=awaiting-takeover` |
| 5 | On day 15, `SIG-08` | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-02-17 --slot 01 \| head -1` | `QA-SLA BREACH slot=01 days=15 sla=14 signal=SIG-08 state=awaiting-takeover` |
| 6 | A breach exits 3 — a signal, not a defect | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-02-17 --slot 01 >/dev/null; echo $?` | `3` |
| 7 | **No breach line names a person** | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-02-17 \| grep BREACH \| grep -c 'qa-1'` | `0` |
| 8 | A completed takeover records its duration | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-03-01 --slot 02` | `QA slot=02 state=owned days=8 sla=14` |
| 9 | Ownership with no landed suite is invalid, and fails | `OB_ROOT=docs/onboarding/fixtures/qa ./onboard-qa.sh --asof 2026-03-01 --slot 03 >/dev/null 2>&1; echo $?` | `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
Q=docs/onboarding/fixtures/qa
printf 'zero=[%s] zrc=%s in=[%s] day14=%s day15=[%s] brc=%s person=%s owned=[%s] invrc=%s\n' \
  "$(./onboard-qa.sh --asof 2026-03-01 | tail -1)" \
  "$(./onboard-qa.sh --asof 2026-03-01 >/dev/null; echo $?)" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-02-10 --slot 01)" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-02-16 --slot 01 | awk '{print $3}')" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-02-17 --slot 01 | head -1)" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-02-17 --slot 01 >/dev/null; echo $?)" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-02-17 | grep BREACH | grep -c 'qa-1')" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-03-01 --slot 02)" \
  "$(OB_ROOT=$Q ./onboard-qa.sh --asof 2026-03-01 --slot 03 >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
zero=[QA-SUMMARY landed=0 owned=0 awaiting=0 breaches=0 invalid=0 asof=2026-03-01] zrc=0 in=[QA slot=01 state=awaiting-takeover days=8 sla=14] day14=state=awaiting-takeover day15=[QA-SLA BREACH slot=01 days=15 sla=14 signal=SIG-08 state=awaiting-takeover] brc=3 person=0 owned=[QA slot=02 state=owned days=8 sla=14] invrc=1
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-12`, branch `l0/onboarding-12-qa`, subject
`feat(root): onboard-qa.sh, the QA-takeover SLA clock and the SIG-08 verdict`,
`Spec: Section 96.6 L8830; Section 98.2 Phase 5 L9068; SIG-08 L4537`, `Invariant: none`.

**STOP rule** — if criterion 7 prints anything other than `0`, a person's name is reaching a breach line and the script
must not be committed: Spec §96.6 (L8830) makes the breach a capacity signal *"never a personal one"*, and §79/§83's
whole separation between capacity evidence and individual evidence rests on lines like this one not carrying a name.
Do **not** change the `14` to make a real breach disappear — that number is calibrated configuration, forbidden action
**OB-F7**, and belongs to L0 under **L0D-17** (`L0-00-charter.md` §5.1). The remedy ladder for a sustained breach is
Spec §73.2's Verification row — *"verification automation and background-drafted suites; shift authoring to developers
with QA reviewing; then hire QA"* — and none of its rungs is an executor's to pull.

---

### L0-07-13 — `onboard-interim.sh` — manual work continues; AI-assisted work waits

**Size:** M · **Dependencies:** L0-07-06, L0-07-11

§9, mechanised: two questions per slot, in a fixed order, each answering with the **first** failing reason so the
answer is a single actionable sentence rather than a list.

> *"During Phases 4–5, manual feature work on the product is permitted under the recorded accepted risks of the
> pre-onboarding block; only AI-assisted feature work waits for the verification contract (the portfolio invariant).
> Onboarding does not freeze a live product's roadmap — it governs how the roadmap ships in the interim."*
> — Spec §96.6, L8830. §98.2 (L9089) applies it throughout Phases 5–7.

The AI question consults `onboard-aigate.sh` **first**, before the contract, because S10 and S19 close a repository to
*every* AI-assisted session and not merely to feature work (§5.2). A product with a verification contract and a
failing S19 gate is still closed.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-13-interim

cat > onboard-interim.sh <<'INTERIM'
#!/usr/bin/env sh
# =============================================================================
# onboard-interim.sh — L0-owned. The Section 96.6 interim rule (spec L8830).
# Manual feature work continues under the recorded accepted risks of the
# pre-onboarding block; only AI-assisted feature work waits for the
# verification contract (portfolio invariant 1, spec L9451).
# S10/S19 are consulted FIRST: they close the repository to every AI-assisted
# session, not merely to feature work (Section 96.6 L8817, L8825).
# usage: onboard-interim.sh [--slot NN]
# exit: 0 (BLOCKED is a legitimate state) | 1 if a gate row is INVALID
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
HERE=$(dirname "$0")
ONLY=""
[ $# -ge 2 ] && [ "$1" = "--slot" ] && ONLY="$2"
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }

manual_ok=0; ai_ok=0; invalid=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  i="$d/interim.tsv"
  bp=$(kv "$i" block_present); ar=$(kv "$i" accepted_risks_recorded); vc=$(kv "$i" verification_contract)

  # ---- question 1: manual feature work
  if [ "$bp" != "yes" ]; then m="BLOCKED"; mr="no-pre-onboarding-block"
  elif [ "$ar" != "yes" ]; then m="BLOCKED"; mr="no-recorded-accepted-risks"
  else m="PERMITTED"; mr="-"; manual_ok=$((manual_ok+1)); fi

  # ---- question 2: AI-assisted feature work
  g=$(OB_ROOT="$OB" "$HERE/onboard-aigate.sh" --slot "$slot" | head -1)
  s10=$(printf '%s' "$g" | awk '{print $3}'); s19=$(printf '%s' "$g" | awk '{print $4}')
  case "$g" in *" s10="*) : ;; *) s10="s10=INVALID" ;; esac    # e.g. no gates.tsv at all
  if [ "$s10" = "s10=INVALID" ] || [ "$s19" = "s19=INVALID" ]; then
    a="INVALID"; ar2="gate-row-invalid-see-onboard-aigate"; invalid=$((invalid+1))
  elif [ "$s10" != "s10=PASS" ]; then a="BLOCKED"; ar2="s10-gate"
  elif [ "$s19" != "s19=PASS" ]; then a="BLOCKED"; ar2="s19-gate"
  elif [ "$vc" != "present" ]; then a="BLOCKED"; ar2="no-verification-contract"
  else a="PERMITTED"; ar2="-"; ai_ok=$((ai_ok+1)); fi

  echo "INTERIM slot=$slot manual=$m reason=$mr ai=$a reason=$ar2"
done

echo "INTERIM-SUMMARY manual_permitted=$manual_ok ai_permitted=$ai_ok invalid=$invalid"
[ "$invalid" -eq 0 ] || exit 1
exit 0
INTERIM
chmod +x onboard-interim.sh

I=docs/onboarding/fixtures/interim
rm -rf "$I"; mkdir -p "$I/products/01" "$I/products/02" "$I/products/03"
# 01: block and risks recorded, both gates pass, contract absent -> manual yes, ai no
printf 'block_present\tyes\naccepted_risks_recorded\tyes\ninterim_response_authored\tyes\nverification_contract\tabsent\n' > "$I/products/01/interim.tsv"
printf 's10_status\tpass\ns10_rotation\tdone\ns10_incident_record\tINC-2026-0007\ns10_checked_on\t2026-01-06\ns19_status\tpass\ns19_removed_on\t2026-01-06\ns19_notification\tnot-required-by-classification\ns19_deletion_obligation\tnone\ns19_checked_on\t2026-01-06\n' > "$I/products/01/gates.tsv"
# 02: contract present but S19 not checked -> ai still blocked on the gate
printf 'block_present\tyes\naccepted_risks_recorded\tyes\ninterim_response_authored\tyes\nverification_contract\tpresent\n' > "$I/products/02/interim.tsv"
printf 's10_status\tpass\ns10_rotation\tdone\ns10_incident_record\tINC-2026-0008\ns10_checked_on\t2026-01-06\ns19_status\tUNSET\ns19_removed_on\tUNSET\ns19_notification\tUNSET\ns19_deletion_obligation\tUNSET\ns19_checked_on\tUNSET\n' > "$I/products/02/gates.tsv"
# 03: everything in place -> both permitted
printf 'block_present\tyes\naccepted_risks_recorded\tyes\ninterim_response_authored\tyes\nverification_contract\tpresent\n' > "$I/products/03/interim.tsv"
cp "$I/products/01/gates.tsv" "$I/products/03/gates.tsv"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Day zero: no block yet, so neither is permitted | `./onboard-interim.sh --slot 01` | `INTERIM slot=01 manual=BLOCKED reason=no-pre-onboarding-block ai=BLOCKED reason=s10-gate` |
| 2 | Day zero is a legitimate state | `./onboard-interim.sh >/dev/null; echo $?` | `0` |
| 3 | **Manual work continues without a contract** | `OB_ROOT=docs/onboarding/fixtures/interim ./onboard-interim.sh --slot 01` | `INTERIM slot=01 manual=PERMITTED reason=- ai=BLOCKED reason=no-verification-contract` |
| 4 | **A contract does not open a repository whose S19 gate has not passed** | `OB_ROOT=docs/onboarding/fixtures/interim ./onboard-interim.sh --slot 02 \| awk '{print $5, $6}'` | `ai=BLOCKED reason=s19-gate` |
| 5 | Gates plus contract permits AI-assisted work | `OB_ROOT=docs/onboarding/fixtures/interim ./onboard-interim.sh --slot 03 \| awk '{print $5, $6}'` | `ai=PERMITTED reason=-` |
| 6 | The summary counts both questions separately | `OB_ROOT=docs/onboarding/fixtures/interim ./onboard-interim.sh \| tail -1` | `INTERIM-SUMMARY manual_permitted=3 ai_permitted=1 invalid=0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
I=docs/onboarding/fixtures/interim
printf 'zero=[%s] zrc=%s manual=[%s] s19=[%s] both=[%s] sum=[%s]\n' \
  "$(./onboard-interim.sh --slot 01)" \
  "$(./onboard-interim.sh >/dev/null; echo $?)" \
  "$(OB_ROOT=$I ./onboard-interim.sh --slot 01)" \
  "$(OB_ROOT=$I ./onboard-interim.sh --slot 02 | awk '{print $5, $6}')" \
  "$(OB_ROOT=$I ./onboard-interim.sh --slot 03 | awk '{print $5, $6}')" \
  "$(OB_ROOT=$I ./onboard-interim.sh | tail -1)"
```

Expected output, exactly:

```
zero=[INTERIM slot=01 manual=BLOCKED reason=no-pre-onboarding-block ai=BLOCKED reason=s10-gate] zrc=0 manual=[INTERIM slot=01 manual=PERMITTED reason=- ai=BLOCKED reason=no-verification-contract] s19=[ai=BLOCKED reason=s19-gate] both=[ai=PERMITTED reason=-] sum=[INTERIM-SUMMARY manual_permitted=3 ai_permitted=1 invalid=0]
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-13`, branch `l0/onboarding-13-interim`, subject
`feat(root): onboard-interim.sh, the Section 96.6 interim rule`,
`Spec: Section 96.6 L8830; Section 98.2 L9089; invariant 1 L9451; invariant 111 L9597`, `Invariant: 1, 111`.

**STOP rule** — if criterion 3 prints `manual=BLOCKED`, the script has turned onboarding into a roadmap freeze, which
is the opposite of what §96.6 L8830 says, and it must not be committed: *"Onboarding does not freeze a live product's
roadmap — it governs how the roadmap ships in the interim."* If criterion 4 prints `ai=PERMITTED`, the script is
letting a verification contract override an AI-safety gate, and eight live repositories are one merge away from
AI-assisted sessions opening a repository holding committed customer data — invariant 111 (L9597). Neither answer may
be "softened" for a product under delivery pressure; a product that needs AI-assisted work sooner needs its **gate**
to pass sooner, and that is floor work under `onboard-floor.sh`, not a flag here.

---

### L0-07-14 — `onboard-deadline.sh`, `onboard-gate.sh` and the `make onboard-*` targets — the track gate

**Size:** L · **Dependencies:** L0-07-05, L0-07-06, L0-07-08, L0-07-11, L0-07-12, L0-07-13

Two scripts and one Makefile block. `onboard-deadline.sh` resolves the `F5` named deadline from its expression and
grades it against `SIG-38` (*"A product in pre-onboarding mode past its deadline… Amber; Red past deadline"*, spec
L4567). `onboard-gate.sh` runs the whole track in one command and returns **one** verdict.

**The gate has three outcomes per check, not two**, because "not yet answerable" and "wrong" are different facts:

| Outcome | Meaning | Effect on the gate |
|---|---|---|
| `OK` | the check passed | — |
| `PENDING` | the check cannot run yet because an input only L0 or a human assessor may supply is absent (`DR-L0-07-D`, an unrecorded assessment) | reported, does not fail |
| `SIGNAL` | a true fact about the world that the operating system wants surfaced — a QA breach, a passed deadline | reported, does not fail |
| `FAIL` | the store contradicts itself, or a generated file diverged from its generator | **fails the gate** |

A gate that failed on `PENDING` would be red from the first commit until **DR-L0-07-D** is answered, and a permanently
red gate teaches everyone to ignore it. A gate that passed on `FAIL` would certify a paper floor. The distinction is
the whole design.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-14-gate

cat > onboard-deadline.sh <<'DL'
#!/usr/bin/env sh
# =============================================================================
# onboard-deadline.sh — L0-owned. The Section 96.2 named deadline (floor item
# F5, spec L8730: "A dated onboarding completion target; missing it is a Red
# signal, not a silent slip"), resolved from its EXPRESSION (D99, L10192) and
# graded against SIG-38 (spec L4567: Amber; Red past deadline).
# Section 10.4: a slot carrying S3 with cd-gate pattern=none must carry the
# SHORTEST deadline in the portfolio (Section 96.6 L8810).
# usage: onboard-deadline.sh [--asof YYYY-MM-DD] [--write]
# exit: 0 clean | 3 signal present (missing or breached) | 1 store contradiction
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
HERE=$(dirname "$0")
ASOF=$(date -u +%Y-%m-%d); WRITE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --asof)  ASOF="$2"; shift 2 ;;
    --write) WRITE=1;   shift ;;
    *) echo "usage: onboard-deadline.sh [--asof YYYY-MM-DD] [--write]" >&2; exit 2 ;;
  esac
done
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }
is_date() { case "$1" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;; *) return 1 ;; esac; }

missing=0; breached=0; invalid=0; resolved_n=0; minres=""
for d in "$OB"/products/*/; do
  slot=$(basename "$d"); f="$d/deadline.tsv"
  ex=$(kv "$f" source_expr)
  if [ "$ex" = "UNSET" ]; then
    echo "DEADLINE MISSING slot=$slot — floor item F5 is open (Section 96.2 L8730)"; missing=$((missing+1)); continue
  fi
  r=$(OB_ROOT="$OB" "$HERE/onboard-when.sh" resolve "$ex")
  if [ "$WRITE" -eq 1 ]; then
    printf 'source_expr\t%s\nresolved\t%s\nentered\t%s\nstatus\t%s\n' \
      "$ex" "$r" "$(kv "$f" entered)" "$(kv "$f" status)" > "$f"
  fi
  case "$r" in
    UNANCHORED) echo "DEADLINE UNANCHORED slot=$slot expr=$ex — correct until L0 declares the anchor (D99)"; continue ;;
    UNKNOWN-TOKEN|BAD-EXPRESSION|BAD-ANCHOR)
      echo "DEADLINE-INVALID slot=$slot expr=$ex reason=$r"; invalid=$((invalid+1)); continue ;;
  esac
  is_date "$r" || { echo "DEADLINE-INVALID slot=$slot expr=$ex reason=not-a-date"; invalid=$((invalid+1)); continue; }
  resolved_n=$((resolved_n+1))
  if [ -z "$minres" ]; then minres="$r"; else minres=$(printf '%s\n%s\n' "$minres" "$r" | sort | head -1); fi
  st=$(kv "$f" status)
  if [ "$st" != "complete" ] && [ "$r" != "$ASOF" ] && [ "$(printf '%s\n%s\n' "$r" "$ASOF" | sort | head -1)" = "$r" ]; then
    echo "DEADLINE BREACH slot=$slot resolved=$r asof=$ASOF signal=SIG-38 grade=Red"; breached=$((breached+1))
  fi
done

# Section 10.4 — the S3-without-a-CD-gate rule.
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  case ",$(kv "$d/states.tsv" states)," in *,S3,*) : ;; *) continue ;; esac
  pat="none"; [ -f "$d/cd-gate.tsv" ] && pat=$(kv "$d/cd-gate.tsv" pattern)
  [ "$pat" = "none" ] || continue
  r=$(kv "$d/deadline.tsv" resolved)
  is_date "$r" || continue
  if [ "$r" != "$minres" ]; then
    echo "DEADLINE-INVALID slot=$slot reason=s3-with-no-cd-gate-must-carry-the-shortest-deadline-in-the-portfolio min=$minres has=$r"
    invalid=$((invalid+1))
  fi
done

echo "DEADLINE-SUMMARY resolved=$resolved_n missing=$missing breached=$breached invalid=$invalid earliest=${minres:-none} asof=$ASOF"
[ "$invalid" -eq 0 ] || exit 1
{ [ "$missing" -eq 0 ] && [ "$breached" -eq 0 ]; } || exit 3
exit 0
DL
chmod +x onboard-deadline.sh

cat > onboard-gate.sh <<'GATE'
#!/usr/bin/env sh
# =============================================================================
# onboard-gate.sh — L0-owned. The onboarding-track gate: one command, one
# verdict. Plan: implementation/lanes/L0-07-onboarding-track.md L0-07-14.
# OK | PENDING (an L0 or assessor input is absent) | SIGNAL (a true fact worth
# surfacing) | FAIL (the store contradicts itself, or a generated file diverged).
# usage: onboard-gate.sh [--asof YYYY-MM-DD]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
HERE=$(dirname "$0")
ASOF=$(date -u +%Y-%m-%d)
[ $# -ge 2 ] && [ "$1" = "--asof" ] && ASOF="$2"
export OB_ROOT="$OB"
fails=0; pend=0; sig=0
row() { printf '  %-10s %s\n' "$1" "$2"; }

out=$("$HERE/onboard-when.sh" lint 2>&1);        rc=$?
if [ $rc -eq 0 ]; then row when-lint OK; else row when-lint "FAIL — $(printf '%s' "$out" | head -1)"; fails=$((fails+1)); fi

out=$("$HERE/onboard-floor.sh" --asof "$ASOF" 2>&1); rc=$?
if [ $rc -eq 0 ]; then row floor "OK — $(printf '%s' "$out" | tail -1)"
else row floor "FAIL — $(printf '%s' "$out" | head -1)"; fails=$((fails+1)); fi

out=$("$HERE/onboard-aigate.sh" 2>&1); rc=$?
if [ $rc -eq 0 ]; then row aigate "OK — $(printf '%s' "$out" | tail -1)"
else row aigate "FAIL — $(printf '%s' "$out" | grep INVALID | head -1)"; fails=$((fails+1)); fi

out=$("$HERE/onboard-assess.sh" 2>&1); rc=$?
if [ $rc -eq 0 ]; then row assess "OK — $(printf '%s' "$out" | tail -1)"
else row assess "FAIL — $(printf '%s' "$out" | grep INVALID | head -1)"; fails=$((fails+1)); fi

out=$("$HERE/onboard-rank.sh" 2>&1); rc=$?
if [ $rc -eq 0 ]; then row rank "OK — $(printf '%s' "$out" | tail -1)"
elif printf '%s' "$out" | grep -q 'RANK-INVALID'; then row rank "FAIL — $(printf '%s' "$out" | grep RANK-INVALID | head -1)"; fails=$((fails+1))
else row rank "PENDING — DR-L0-07-D (the eight facts.tsv are unwritten)"; pend=$((pend+1)); fi

out=$("$HERE/onboard-stream.sh" check 2>&1); rc=$?
if [ $rc -eq 0 ]; then row stream "OK — $(printf '%s' "$out" | tail -1)"
else row stream "FAIL — $(printf '%s' "$out" | tail -1) (Section 73.1 permits one stream)"; fails=$((fails+1)); fi

out=$("$HERE/onboard-plan.sh" --check 2>&1); rc=$?
if [ $rc -eq 0 ]; then row plan "OK — $(printf '%s' "$out" | tail -1)"
elif printf '%s' "$out" | grep -q 'PLAN-STALE'; then row plan "FAIL — a generated plan diverged from its generator (invariant 46)"; fails=$((fails+1))
else row plan "PENDING — $(printf '%s' "$out" | head -1)"; pend=$((pend+1)); fi

out=$("$HERE/onboard-qa.sh" --asof "$ASOF" 2>&1); rc=$?
case $rc in
  0) row qa "OK — $(printf '%s' "$out" | tail -1)" ;;
  3) row qa "SIGNAL — $(printf '%s' "$out" | grep BREACH | head -1)"; sig=$((sig+1)) ;;
  *) row qa "FAIL — $(printf '%s' "$out" | grep INVALID | head -1)"; fails=$((fails+1)) ;;
esac

out=$("$HERE/onboard-interim.sh" 2>&1); rc=$?
if [ $rc -eq 0 ]; then row interim "OK — $(printf '%s' "$out" | tail -1)"
else row interim "FAIL — a gate row is invalid"; fails=$((fails+1)); fi

out=$("$HERE/onboard-deadline.sh" --asof "$ASOF" 2>&1); rc=$?
case $rc in
  0) row deadline "OK — $(printf '%s' "$out" | tail -1)" ;;
  3) row deadline "SIGNAL — $(printf '%s' "$out" | tail -1)"; sig=$((sig+1)) ;;
  *) row deadline "FAIL — $(printf '%s' "$out" | grep INVALID | head -1)"; fails=$((fails+1)) ;;
esac

if [ "$fails" -eq 0 ]; then
  echo "ONBOARDING-TRACK GATE OK fails=0 pending=$pend signals=$sig asof=$ASOF"; exit 0
else
  echo "ONBOARDING-TRACK GATE FAIL fails=$fails pending=$pend signals=$sig asof=$ASOF"; exit 1
fi
GATE
chmod +x onboard-gate.sh

# ---- Makefile block, appended once. Recipe lines need REAL tabs, so they are
# written with printf '\t' rather than typed, which is what makes this block
# survive being copied out of a plan document.
if grep -q '^# BEGIN onboarding-track targets' Makefile 2>/dev/null; then
  echo "Makefile block already present — nothing appended"
else
  {
    printf '\n# BEGIN onboarding-track targets (L0-07-14) — do not hand-edit between the markers\n'
    printf '.PHONY: onboard-gate onboard-floor onboard-aigate onboard-plan onboard-qa onboard-interim onboard-stream onboard-deadline onboard-report\n'
    printf 'onboard-gate:\n';     printf '\t@./onboard-gate.sh\n'
    printf 'onboard-floor:\n';    printf '\t@./onboard-floor.sh\n'
    printf 'onboard-aigate:\n';   printf '\t@./onboard-aigate.sh\n'
    printf 'onboard-plan:\n';     printf '\t@./onboard-plan.sh\n'
    printf 'onboard-qa:\n';       printf '\t@./onboard-qa.sh\n'
    printf 'onboard-interim:\n';  printf '\t@./onboard-interim.sh\n'
    printf 'onboard-stream:\n';   printf '\t@./onboard-stream.sh holder\n'
    printf 'onboard-deadline:\n'; printf '\t@./onboard-deadline.sh\n'
    printf '# END onboarding-track targets\n'
  } >> Makefile
fi

D=docs/onboarding/fixtures/deadline
rm -rf "$D"; mkdir -p "$D/products/01" "$D/products/02" "$D/anchors"
printf 'token\tS3\ndate\t2026-01-05\ndeclared_by\tL0\n' > "$D/anchors/S3.tsv"
printf 'token\tS0\ndate\tUNSET\ndeclared_by\tUNSET\n'   > "$D/anchors/S0.tsv"
printf 'source_expr\tS3+4w\nresolved\t2026-02-02\nentered\t2026-01-05\nstatus\tpre_onboarding\n' > "$D/products/01/deadline.tsv"
printf 'states\tS3\nnotes\tUNSET\nassessed_on\t2026-01-08\n'   > "$D/products/01/states.tsv"
printf 'source_expr\tS3+2w\nresolved\t2026-01-19\nentered\t2026-01-05\nstatus\tpre_onboarding\n' > "$D/products/02/deadline.tsv"
printf 'states\tS1\nnotes\tUNSET\nassessed_on\t2026-01-08\n'   > "$D/products/02/states.tsv"
mkdir -p "$D/products/03"
printf 'source_expr\tS0+1w\nresolved\tUNANCHORED\nentered\tUNSET\nstatus\tpre_onboarding\n' > "$D/products/03/deadline.tsv"
printf 'states\tS1\nnotes\tUNSET\nassessed_on\t2026-01-08\n'   > "$D/products/03/states.tsv"
```

The `deadline` fixture is deliberately wrong in exactly one way: slot 01 carries **S3** with no `cd-gate.tsv`, and its
deadline is **later** than slot 02's. §10.4 says that slot must carry *"the shortest deadline in the portfolio"*, so
the checker must reject it. A checker that accepts this fixture would let the most dangerous starting state in the
taxonomy — auto-deploy with no meaningful tests — sit at the back of the queue.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Day zero: eight products with no named deadline is `F5` open, a signal | `./onboard-deadline.sh --asof 2026-03-01 \| tail -1` | `DEADLINE-SUMMARY resolved=0 missing=8 breached=0 invalid=0 earliest=none asof=2026-03-01` |
| 2 | …and a signal exits 3, not 1 | `./onboard-deadline.sh --asof 2026-03-01 >/dev/null; echo $?` | `3` |
| 3 | A passed deadline is `SIG-38`, Red | `OB_ROOT=docs/onboarding/fixtures/deadline ./onboard-deadline.sh --asof 2026-03-01 \| grep -c 'signal=SIG-38 grade=Red'` | `2` |
| 4 | **An ungated S3 product must hold the shortest deadline** | `OB_ROOT=docs/onboarding/fixtures/deadline ./onboard-deadline.sh --asof 2026-01-10 \| grep -c 's3-with-no-cd-gate-must-carry-the-shortest-deadline-in-the-portfolio'` | `1` |
| 5 | …and that contradiction fails, it does not merely signal | `OB_ROOT=docs/onboarding/fixtures/deadline ./onboard-deadline.sh --asof 2026-01-10 >/dev/null 2>&1; echo $?` | `1` |
| 6 | An unanchored expression is reported, never guessed (D99) | `OB_ROOT=docs/onboarding/fixtures/deadline ./onboard-deadline.sh --asof 2026-03-01 \| grep -c 'DEADLINE UNANCHORED'` | `1` |
| 7 | The gate runs every check and returns one verdict | `./onboard-gate.sh --asof 2026-03-01 \| tail -1` | `ONBOARDING-TRACK GATE OK fails=0 pending=2 signals=1 asof=2026-03-01` |
| 8 | A day-zero gate is green, and says what it is waiting for | `./onboard-gate.sh --asof 2026-03-01 \| grep -c PENDING` | `2` |
| 9 | The Makefile block is present exactly once | `grep -c '^# BEGIN onboarding-track targets' Makefile` | `1` |
| 10 | Recipe lines are real tabs, so `make` parses | `make -n onboard-gate` | `./onboard-gate.sh` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
D=docs/onboarding/fixtures/deadline
printf 'zero=[%s] zrc=%s red=%s unanch=%s s3=%s s3rc=%s gate=[%s] pending=%s mk=%s make=[%s]\n' \
  "$(./onboard-deadline.sh --asof 2026-03-01 | tail -1)" \
  "$(./onboard-deadline.sh --asof 2026-03-01 >/dev/null; echo $?)" \
  "$(OB_ROOT=$D ./onboard-deadline.sh --asof 2026-03-01 | grep -c 'signal=SIG-38 grade=Red')" \
  "$(OB_ROOT=$D ./onboard-deadline.sh --asof 2026-03-01 | grep -c 'DEADLINE UNANCHORED')" \
  "$(OB_ROOT=$D ./onboard-deadline.sh --asof 2026-01-10 | grep -c 's3-with-no-cd-gate-must-carry-the-shortest-deadline-in-the-portfolio')" \
  "$(OB_ROOT=$D ./onboard-deadline.sh --asof 2026-01-10 >/dev/null 2>&1; echo $?)" \
  "$(./onboard-gate.sh --asof 2026-03-01 | tail -1)" \
  "$(./onboard-gate.sh --asof 2026-03-01 | grep -c PENDING)" \
  "$(grep -c '^# BEGIN onboarding-track targets' Makefile)" \
  "$(make -n onboard-gate)"
```

Expected output, exactly:

```
zero=[DEADLINE-SUMMARY resolved=0 missing=8 breached=0 invalid=0 earliest=none asof=2026-03-01] zrc=3 red=2 unanch=1 s3=1 s3rc=1 gate=[ONBOARDING-TRACK GATE OK fails=0 pending=2 signals=1 asof=2026-03-01] pending=2 mk=1 make=[./onboard-gate.sh]
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-14`, branch `l0/onboarding-14-gate`, subject
`feat(root): onboard-deadline.sh, onboard-gate.sh and the make onboard-* targets`,
`Spec: Section 96.2 L8730; Section 96.4 L8769-L8775; Section 96.6 L8810; SIG-38 L4567; D99 L10192`, `AT: AT-051`,
`Invariant: 46`. The commit touches `Makefile`, so re-read the path assertion output before pushing: `Makefile` is in
the allowed set, every other root file is not.

**STOP rule** — if criterion 4 prints `0`, the shortest-deadline rule is not enforced and the gate must not be
committed: §96.6 (L8810) calls S3 *"the most dangerous state"* precisely because an unverified change reaches
production automatically, and a portfolio that sequences it last has inverted §96.5. If criterion 7 prints `FAIL` on
a freshly seeded store, do **not** relax a checker to make the gate green — find which row says `FAIL`, and if the
cause is a real store contradiction, fix the store; if the cause is a check that should have been `PENDING`, fix the
mapping in `onboard-gate.sh` only, and never the checker's own exit code. If `make -n onboard-gate` prints
`*** missing separator`, the recipe lines lost their tabs in transit: delete the appended block, re-run the `printf`
sequence, and do not retype the tabs by hand.

---

### L0-07-15 — `onboard-report.sh` — the generated README, and the weekly track ritual

**Size:** M · **Dependencies:** L0-07-14

Invariant 46 (spec L9514): *"Derived data is computed, never hand-maintained."* The human-readable state of the
onboarding track is derived from 100-odd small files, so it is generated between the markers of
`docs/onboarding/README.md` and never typed. `--check` re-renders into a temporary file and compares, so a hand-edit
inside the markers is a **failure** rather than a silent divergence — the same technique `L0-06-04` uses for the
rendered bootstrap exceptions.

**Commands**

```bash
cd "$CP_ROOT"
git fetch origin --prune && git checkout integration && git pull --ff-only
git status --porcelain          # expected: empty
git checkout -b l0/onboarding-15-report

cat > onboard-report.sh <<'REP'
#!/usr/bin/env sh
# =============================================================================
# onboard-report.sh — L0-owned. Renders docs/onboarding/README.md between the
# markers from the per-item store. GENERATED — invariant 46 (spec L9514).
# usage: onboard-report.sh [--check] [--asof YYYY-MM-DD]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
HERE=$(dirname "$0")
CHECK=0; ASOF=$(date -u +%Y-%m-%d)
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1; shift ;;
    --asof)  ASOF="$2"; shift 2 ;;
    *) echo "usage: onboard-report.sh [--check] [--asof YYYY-MM-DD]" >&2; exit 2 ;;
  esac
done
export OB_ROOT="$OB"
kv() { awk -F'\t' -v k="$2" '$1==k{print $2; f=1} END{if(!f) print "UNSET"}' "$1"; }

body=$(
  echo "<!-- BEGIN GENERATED -->"
  echo "Generated by onboard-report.sh on $ASOF. Do not hand-edit inside these markers (invariant 46)."
  echo
  echo '## Portfolio'
  echo
  echo '| Check | Result |'
  echo '|---|---|'
  printf '| Universal floor | %s |\n'   "$("$HERE/onboard-floor.sh"    --asof "$ASOF" 2>/dev/null | tail -1)"
  printf '| AI-safety gates | %s |\n'   "$("$HERE/onboard-aigate.sh"                   2>/dev/null | tail -1)"
  printf '| Intake assessments | %s |\n' "$("$HERE/onboard-assess.sh"                  2>/dev/null | tail -1)"
  printf '| Sequence (96.5) | %s |\n'   "$("$HERE/onboard-rank.sh"                     2>/dev/null | tail -1)"
  printf '| DevOps stream (73.1) | %s |\n' "$("$HERE/onboard-stream.sh" holder         2>/dev/null | head -1)"
  printf '| QA-takeover SLA | %s |\n'   "$("$HERE/onboard-qa.sh"       --asof "$ASOF" 2>/dev/null | tail -1)"
  printf '| Interim rule | %s |\n'      "$("$HERE/onboard-interim.sh"                  2>/dev/null | tail -1)"
  printf '| Named deadlines | %s |\n'   "$("$HERE/onboard-deadline.sh" --asof "$ASOF" 2>/dev/null | tail -1)"
  echo
  echo '## Per product'
  echo
  echo '| Slot | Rank | States | Floor closed | AI gates | Assessment | Deadline |'
  echo '|---|---|---|---|---|---|---|'
  for d in "$OB"/products/*/; do
    slot=$(basename "$d")
    rk=$(awk -F'\t' -v s="$slot" 'FNR==1{r=""} $1=="rank"{r=$2} $1=="slot" && $2==s{print r}' "$OB"/rank/*.tsv 2>/dev/null)
    fl=$("$HERE/onboard-floor.sh" --slot "$slot" --asof "$ASOF" 2>/dev/null | tail -1 | awk '{print $3}')
    ag=$("$HERE/onboard-aigate.sh" --slot "$slot" 2>/dev/null | head -1 | awk '{print $4}')
    as=$("$HERE/onboard-assess.sh" --slot "$slot" 2>/dev/null | head -1 | awk '{print $3}')
    printf '| %s | %s | %s | %s | %s | %s | %s |\n' \
      "$slot" "${rk:-UNRANKED}" "$(kv "$d/states.tsv" states)" "$fl" "$ag" "$as" "$(kv "$d/deadline.tsv" resolved)"
  done
  echo
  echo "Vocabulary: OT-FLOOR, OT-INTAKE, OT-P4..OT-P7 (master/04-phase-map.md section 2)."
  echo "Dates are EXPRESSIONS, not week labels (D99, spec L10192). UNANCHORED is a correct answer."
  echo "<!-- END GENERATED -->"
)

tmp="$OB/.README.$$"
awk -v repl="$body" '
  /<!-- BEGIN GENERATED -->/ {print repl; skip=1; next}
  /<!-- END GENERATED -->/   {skip=0; next}
  !skip {print}
' "$OB/README.md" > "$tmp"

if [ "$CHECK" -eq 1 ]; then
  if cmp -s "$tmp" "$OB/README.md"; then rm -f "$tmp"; echo "REPORT-CHECK OK"; exit 0
  else rm -f "$tmp"; echo "REPORT-CHECK STALE — run 'make onboard-report' and commit the result"; exit 1; fi
fi
mv "$tmp" "$OB/README.md"
echo "REPORT-WRITTEN $OB/README.md asof=$ASOF"
exit 0
REP
chmod +x onboard-report.sh

if grep -q '^onboard-report:' Makefile; then
  echo "report target already present"
else
  { printf 'onboard-report:\n'; printf '\t@./onboard-report.sh\n'; } >> Makefile
fi

./onboard-report.sh --asof 2026-03-01
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The README renders | `./onboard-report.sh --asof 2026-03-01` | `REPORT-WRITTEN docs/onboarding/README.md asof=2026-03-01` |
| 2 | Rendering twice is idempotent | `./onboard-report.sh --asof 2026-03-01 >/dev/null; ./onboard-report.sh --check --asof 2026-03-01` | `REPORT-CHECK OK` |
| 3 | Eight product rows are rendered | `sed -n '/## Per product/,/^$/p' docs/onboarding/README.md \| grep -c '^| 0'` | `8` |
| 4 | A hand-edit inside the markers is caught | `sed -i 's/^| 01 |/| 01 EDITED |/' docs/onboarding/README.md && ./onboard-report.sh --check --asof 2026-03-01; ./onboard-report.sh --asof 2026-03-01 >/dev/null` | `REPORT-CHECK STALE — run 'make onboard-report' and commit the result` |
| 5 | Nothing outside the markers is touched | `head -1 docs/onboarding/README.md` | `# Onboarding track — status` |
| 6 | The report never invents a product name | `grep -c UNSET docs/onboarding/README.md` | `8` |
| 7 | `make onboard-report` is wired | `make -n onboard-report` | `./onboard-report.sh` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
./onboard-report.sh --asof 2026-03-01 >/dev/null
a=$(./onboard-report.sh --check --asof 2026-03-01)
sed -i 's/^| 01 |/| 01 EDITED |/' docs/onboarding/README.md
b=$(./onboard-report.sh --check --asof 2026-03-01)
./onboard-report.sh --asof 2026-03-01 >/dev/null
printf 'idempotent=[%s] handedit=[%s] rows=%s head=[%s] unset=%s make=[%s]\n' \
  "$a" "$b" \
  "$(sed -n '/## Per product/,/^$/p' docs/onboarding/README.md | grep -c '^| 0')" \
  "$(head -1 docs/onboarding/README.md)" \
  "$(grep -c UNSET docs/onboarding/README.md)" \
  "$(make -n onboard-report)"
```

Expected output, exactly:

```
idempotent=[REPORT-CHECK OK] handedit=[REPORT-CHECK STALE — run 'make onboard-report' and commit the result] rows=8 head=[# Onboarding track — status] unset=8 make=[./onboard-report.sh]
```

**Commit** — the block of L0-07-01 with `Task-Id: L0-07-15`, branch `l0/onboarding-15-report`, subject
`feat(root): onboard-report.sh and the generated onboarding-track README`,
`Spec: Section 96.4 L8769; invariant 46 L9514`, `Invariant: 46`.

**STOP rule** — if criterion 4 prints `REPORT-CHECK OK` after the hand-edit, the divergence detector is not detecting
and must not be committed: a README that can be edited by hand is a second source of truth for the onboarding track,
and the first thing anyone will edit is a burn-down number. Never hand-edit inside the markers to "fix a rendering
glitch" — change the generator, or change the store the generator reads.

---

## 12. DECISION REQUIRED — items this file cannot close by itself

Written in the house form of `L0-06-bootstrap-mode.md` §5. **No executor resolves any of them.** Each names what this
file does in the meantime, so no task in §11 is blocked on an answer.

---

> ### DECISION REQUIRED — DR-L0-07-A — `templates/intake-gap-assessment.md` has no owning lane
>
> **Facts.** Spec §96.6 (L8783) names the artifact by path: assessments are *"authored from the named template
> artifact in the control plane (`templates/intake-gap-assessment.md`)"*. `templates/**` appears in no lane's OWNS
> column in PARTITION.md; only `templates/workflows/**` does, and that is L2's. `master/04-phase-map.md` §8
> **DECISION 2** already escalates the general case of unowned named artifacts.
> **Question for L0.** Who authors and owns `templates/intake-gap-assessment.md`: L0 under the residual-ownership
> rule (`L0-00-charter.md` §2.3, **L0D-04**), or L2 as an extension of its `templates/**` prefix, or does the template
> move under `docs/onboarding/` and become this track's?
> **Blocks.** `OT-INTAKE` for every product, in the real world. **Nothing in §11** — L0-07-08 checks the
> `template_version` string, so the checker is complete and testable before the template exists.
> **This file's behaviour pending the answer.** No task writes `templates/**`. An assessment recorded against
> `template_version=UNSET` is `INVALID`, so the gap is visible rather than silently tolerated.

---

> ### DECISION REQUIRED — DR-L0-07-B — mirroring pre-onboarding accepted risks into the exception registry
>
> **Facts.** Spec §96.2 (L8735): *"Pre-onboarding accepted risks are mirrored as entries in the exception registry
> (Section 54), so the single-answer property holds: one registry answers 'what rules are currently relaxed, where,
> and until when'."* PARTITION.md line 17 assigns `registries/**` to **L1, exclusively**. This is structurally the
> same collision `L0-06-bootstrap-mode.md` DECISION REQUIRED #1 raises for bootstrap exceptions, one registry over.
> **Question for L0.** Same three options, and preferably the same answer as the bootstrap case: (a) L1 lands the
> entries from an L0-authored source, (b) L0 is granted the file by an **L0D-04** extension of `lane-paths.tsv`, or
> (c) the registry becomes a directory-per-item store L1 assembles.
> **Blocks.** Nothing in §11. It changes only where floor item `F4`'s mirror finally lands.
> **This file's behaviour pending the answer.** `F4` is closed on evidence naming the accepted-risk id; the mirror is
> tracked as an open item. **L0 does not edit `registries/**`.**

---

> ### DECISION REQUIRED — DR-L0-07-C — is the S19 customer-data check a tenth floor obligation?
>
> **Facts.** Spec §96.6 (L8802) states the floor's arithmetic explicitly: *"nine items across every live product,
> which at eight products is seventy-two tracked obligations"* — and the nine are the six §96.2 items plus three
> Phase 1 actions, of which `F9` is *secrets* out of the repository. The S19 row (L8825) then says its own check is
> *"universal floor"*, and invariant 111 (L9597) names the S19 intake gate as a distinct detector from the
> secret-scanning one.
> **Question for L0.** Is S19 a tenth floor item — making the denominator 80, not 72 — or does it ride `F9`?
> **Blocks.** Nothing in §11. It changes the burn-down denominator and therefore what `SIG-38` is measured against.
> **This file's behaviour pending the answer.** The checklist is **nine** rows, matching the spec's own arithmetic,
> and the S19 gate is tracked separately in `gates.tsv` and enforced by `onboard-aigate.sh` — so the obligation is
> never lost, only counted elsewhere. L0-07-02's STOP rule forbids an executor from adding the tenth row.

---

> ### DECISION REQUIRED — DR-L0-07-D — the eight product identities and their three ordering keys
>
> **Facts.** §96.5 sequences on `classification.reliability_criticality`, then `business.criticality`, then expected
> onboarding cost. §11's machinery computes the order; it cannot supply the inputs. Spec §11 additionally forbids
> hard-coded repository names, and `master/04-phase-map.md` §8 **DECISION 4** separately asks L0 for the pilot set.
> **Question for L0.** For each of the eight slots: `product_id`, `repository`, `reliability_criticality`,
> `business_criticality`, `onboarding_cost_band`, `conformance_profile`, `team` — and the recorded §96.5 sequencing
> decision they produce, *"recorded as a decision and reviewed at the quarterly operating-system review"* (L8779).
> **Blocks.** The **real-world** track: `onboard-rank.sh` refuses, `onboard-plan.sh` refuses, and every deadline stays
> `UNSET`. **Nothing in §11's construction** — every task is written against slots and ranks.
> **This file's behaviour pending the answer.** Eight numbered slots, every field `UNSET`, every checker failing
> closed and naming this decision by id. Filling any field is forbidden action **OB-F1**.

---

> ### DECISION REQUIRED — DR-L0-07-E — the estate's six floor items, and `tools.yaml`
>
> **Facts.** Spec §96.6 (L8802) puts the operating system's own machine estate on the floor: *"the hosts running
> Hermes Agent instances — the background worker harness, the PR-review engine and the founder ops console — are
> estate machines and meet the same six items from the day they exist (D69); their `HERMES_HOME` directories are
> sensitive-at-rest and covered by the backup and access-inventory items."* D69 (L10147) places those instances in
> the **Subsystem J cage**, and `master/04-phase-map.md` §8 **DECISION 1** records that subsystems **G, H, J, O and P
> are assigned to no lane** in PARTITION v1.
> **Question for L0.** Which lane, or which L0 file, owns the estate hosts' six floor rows and the `tools.yaml`
> registration D69 requires *before first use*? This track owns eight product slots and says so; it does not claim J.
> **Blocks.** Nothing in §11.
> **This file's behaviour pending the answer.** `floor/items/FN.tsv` carries the `estate` flag so the six applicable
> items are identified in the store, and **no estate host is created as a slot** — an estate host is not a repository
> and does not enter the 72 (L0-07-02's STOP rule). The obligation is named here and routed, never quietly absorbed.

---

> ### DECISION REQUIRED — DR-L0-07-F — `OT-P7` depends on GSD Core and the plan-checker, which no lane owns
>
> **Facts.** Spec §98.2 Phase 7 (L9080) requires GSD Core installed at a pinned tag, `.planning/` created, the
> constitution referenced in `CONTEXT.md`, model routing configured — and its completion check is *"a first plan
> passes the plan-checker and is approved at Gate 1."* The GSD tier is in the same unowned group as J: **O and P** in
> `04` §8 **DECISION 1**, which also records §99.4 deferring J and P outright.
> **Question for L0.** Who delivers the plan-checker and the GSD Core installation profile that `OT-P7` consumes, and
> is `OT-P7` in V1 scope at all (`master/06-v1-scope.md`)?
> **Blocks.** `OT-P7` in the real world, for every product. **Nothing in §11** — `onboard-plan.sh` emits the `OT-P7`
> row with gate `plan-checker`, which simply stays open until the checker exists.
> **This file's behaviour pending the answer.** The row is emitted and left open. This track does **not** claim O or
> P and writes nothing under any GSD path.

---

> ### DECISION REQUIRED — DR-L0-07-G — the anchor dates for `S0`…`S3` and `OT-FLOOR`
>
> **Facts.** D99 (L10192) makes every onboarding phase relative to the Build-track milestone it consumes; §11's
> resolver is built for exactly that. But an expression resolves to a date only once L0 declares the anchor, and
> `master/04-phase-map.md` §8 **DECISION 5** already records that no spec line supplies a calendar anchor.
> **Question for L0.** When each sync point (`S0`, `S1`, `S2`, `S3`) is declared passed, and the date `OT-FLOOR`
> starts at `BT-0` — each recorded with `onboard-when.sh set <token> <date> <who>`, which is the only writer.
> **Blocks.** Nothing. Every unanchored expression resolves to `UNANCHORED`, which is the correct answer.
> **This file's behaviour pending the answer.** Anchors ship `UNSET`; `UNANCHORED` propagates through plans and
> deadlines; the report renders the expression. Writing a calendar date into a phase or deadline field is forbidden
> action **OB-F2**.

---

### 12.1 Surfaces this track consumes and never writes

| Surface | Owner | This file's relationship to it |
|---|---|---|
| `registries/exceptions.yaml` — the mirror of every pre-onboarding accepted risk (§96.2 L8735) | **L1** (PARTITION.md line 17); `L1-05-tasks.md` **L1-108** | Named in floor row `F4`'s evidence. Never edited here — **DR-L0-07-B** |
| `templates/intake-gap-assessment.md` (§96.6 L8783) | **unassigned** — `04` §8 DECISION 2 | Consumed by version string only — **DR-L0-07-A** |
| `schemas/product/**` and the `product.yaml` Phase-2 stub carrying the `onboarding:` block (§96.2 L8735) | **L1** | This track records *whether* the block is present (`interim.tsv`); L1 owns its schema |
| `records/deletion-requests/`, `records/incidents/` — the S19 deletion obligation and the S10 §43 incident record | **L4** (`control-plane-records` is L4's entirely, PARTITION.md line 20) | `gates.tsv` records the **reference**; the record itself is written in L4's repository |
| `.github/workflows/**` — the parity job, deploy workflows, the production approval gate that `OT-P4` and `OT-P6` instantiate | **L2** | The plan's phase rows depend on them via sync point `S3`; nothing here writes a workflow |
| `access/**` — GitHub Environments, scoped secrets, branch-protection profiles behind floor row `F8` | **L5** | `F8` is closed on evidence produced by L5's apply runbook |
| The `SIG-38` and `SIG-08` detectors, and the §96.4 adoption-health surface | **L3** `validators/drift/**` (detector) and **L4** `metrics/**` (the health report) — the dashboard half is subsystem **H**, unassigned (`04` §8 DECISION 1) | `onboard-deadline.sh` and `onboard-qa.sh` print the signal ids so the manual sweep works before the detectors exist |
| The Hermes estate hosts, `tools.yaml`, subsystem **J** | **unassigned** — `04` §8 DECISION 1 | **DR-L0-07-E** |
| GSD Core, the plan-checker, subsystems **O** and **P** | **unassigned** — `04` §8 DECISION 1 | **DR-L0-07-F** |

---

## 13. Quick reference — one onboarding week

**Commands**

```bash
cd "$CP_ROOT" && git checkout integration && git pull --ff-only

make onboard-gate             # ONBOARDING-TRACK GATE OK fails=0 pending=N signals=M   [T14]
make onboard-floor            # FLOOR total=72 closed=.. paper=0 red=0                 [T05]
make onboard-stream           # STREAM HOLDER seq=.. ref=.. phase=..  |  STREAM FREE   [T10]
make onboard-qa               # QA-SLA BREACH ... signal=SIG-08, if any                [T12]
make onboard-interim          # per slot: manual=… ai=…                                [T13]
make onboard-report && git add docs/onboarding/README.md && git commit -m "onboarding report $(date -u +%F)"

# When a phase actually starts, anchor it — this is the only way a date enters the store:
./onboard-when.sh set OT-P4-03 2026-02-02 L0
./onboard-deadline.sh --write            # re-resolves every deadline from its expression

# When a phase takes or releases the DevOps stream (Section 73.1 — one at a time):
./onboard-stream.sh claim product slot-03 OT-P4 2026-02-02
./onboard-stream.sh release 001 2026-02-16
```

The five sentences worth keeping in the head, each quoted:

1. §96.6 L8802 — the floor is *"nine items across every live product"*, and *"a floor declared done on paper is
   exactly the invisible half-adoption 96.4 exists to catch"*.
2. §96.6 L8830 — *"manual feature work on the product is permitted … only AI-assisted feature work waits for the
   verification contract"*; onboarding *"governs how the roadmap ships in the interim"*.
3. §96.6 L8817 / L8825 — *"No AI-assisted session opens the repository until the S10 check passes"*, and the same for
   S19, where *"there is no rotation-equivalent remedy"*.
4. §73.1 L6005 — brownfield onboarding and platform work *"serialise on DevOps capacity — only one such stream can
   proceed at a time"*.
5. D99 L10192 — the Onboarding track's phases are *"relative to the subsystems they consume. Pre-onboarding deadlines
   are set from the Onboarding track, not from the labels."*

---

## 14. What this file does not decide

| Matter | Owner |
|---|---|
| The eight product identities, their criticalities and cost bands, and the recorded §96.5 sequence | **L0** — **DR-L0-07-D**. Never an executor's reading of a repository |
| Reordering `OT-P4`…`OT-P7` for any product, or admitting platform work ahead of a product in the stream | **L0** under §96.5 — forbidden action **OB-F3** |
| Whether a product is worth onboarding at full standard (state S13), and its lifecycle answer | **L0** — Spec §18; forbidden action **OB-F4** |
| Adding a twentieth starting state, or changing which states are AI-safety gates | **L0** — §96.6 L8832 makes the taxonomy configuration, not an executor's extension |
| Whether S19 is a tenth floor obligation | **L0** — **DR-L0-07-C** |
| The 14-day QA SLA, the 90-day restore rotation, and every other calibrated value | **L0D-17** (`L0-00-charter.md` §5.1) — forbidden action **OB-F7** |
| Sync-point anchor dates, and the date `OT-FLOOR` starts | **L0** — **DR-L0-07-G**; `04` §8 DECISION 5 |
| The floor's declared duration in the roadmap and the published wall-clock estimate | **L0** — `04` §8 DECISION 3 and **D-PLAN-03** (`master/00-MASTER-PLAN.md` §12). §4.2 computes bounds; no task publishes a point estimate |
| Who authors `templates/intake-gap-assessment.md` | **L0** — **DR-L0-07-A**; `04` §8 DECISION 2 |
| Where a pre-onboarding accepted risk lands in `registries/exceptions.yaml` | **L0** — **DR-L0-07-B**. `registries/**` is L1's exclusively |
| The estate hosts' six floor items, `tools.yaml`, subsystem **J** | **L0** — **DR-L0-07-E**; `04` §8 DECISION 1 |
| GSD Core, the plan-checker and `OT-P7`'s real feasibility, subsystems **O** and **P** | **L0** — **DR-L0-07-F**; `04` §8 DECISION 1 |
| Performing any step inside a product repository | The named executor of that floor row (§95.4) — forbidden action **OB-F5**. This track records and verifies the evidence |
| Declaring the floor, an assessment, a phase or the track complete | Nobody, on any evidence other than the gate command's own output — forbidden action **OB-F8** |

Nothing in a PR description, a blocker issue, a comment or a product team's assurance moves any row of this table. The
onboarding track's whole reason for existing is that eight products are live and serving customers while the operating
system is still being built, and Spec §96.1 names both failure modes it exists to prevent: *"Ungoverned interim
operation and invisible half-adoption are both failure modes, and both get explicit machinery."* Every checker in §11
is one half of that machinery; the `UNSET` seeded into every field is the other, because a field that has never been
answered and a field answered "fine" must never look the same.
