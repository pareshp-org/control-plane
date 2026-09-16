# L0-00 — INTEGRATOR CHARTER

**Lane:** L0 Integrator (human/lead) · **Branches:** `main`, `integration` (PARTITION.md §"Branch & merge model")
**Executor:** the human lead. This is the ONE file in the plan whose executor is not an AI developer.
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — this charter never contradicts it.

> **Reading rule for lanes L1–L5.** This file is normative for you in exactly one way: it tells you what you are
> forbidden to decide and how to escalate. Sections 5, 6 and 7 below are the binding parts for a lane executor.
> Everything else describes work the human lead performs.

---

## 1. Shell and repository conventions used by every command in this file

All commands are POSIX `sh` / Git Bash. Run them from the control-plane repository root.

**Commands**

```bash
set -euo pipefail
# Set once per shell session. Adjust the path to the local clone if it differs.
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
cd "$CP_ROOT"
git rev-parse --show-toplevel
```

Two repositories exist at build time and they are not interchangeable (PARTITION.md §"Repositories"):

| Repo | Holds | Protection posture |
|---|---|---|
| `control-plane` | registries, contracts, schemas, validators, reconciler, provisioning, reusable workflows, access/infra config | Full branch protection. **No machine bypass actor** (D89) |
| `control-plane-records` | `records/**`, `events/**` | No review protection; a no-bypass ruleset blocks force-push and delete (D107) |

L0 opens pull requests from `l0/<task>` branches into `integration` in `control-plane` and promotes to `main` only by pull request. Under the `L0D-07` exception (FD-012), L0 merges its own `l0/<task>` PRs outside the lane merge train. Phase 1's completion check requires that no direct human push to a **default** branch succeeds (§98.2, Phase 1); `integration` is not the default branch, so this is satisfied.

---

## 2. What the integrator owns

### 2.1 Owned paths — the exclusive set

| Path | What lives there | Frozen? |
|---|---|---|
| `contracts/**` | The frozen data contracts every lane codes against — registry schemas, record schemas, event envelope, stub and fixture definitions | **Yes, from Phase 0.** Changed only by an approved Contract Change Request (§6.2) |
| `CODEOWNERS` (repo root) | Path→owner enforcement, generated to contain **human identities only** (§98.2, Phase 1 completion check) | No, but every edit is an L0 decision (L0D-05) |
| `docs/**` | Charter, cadence, merge-train runbook, escalation templates, decision register, transition notes (§95.4) | No |
| `Makefile` | `lane-guard`, `train`, `promote-check` — the local, authoritative gates | No |
| Root files | `lane-paths.tsv`, `lane-guard.sh`, `contracts.sha256`, `README.md`, `.gitignore`, `.editorconfig` | No |

`CODEOWNERS` is placed at the repository **root**, not under `.github/`, so that no L0 artifact sits inside a
directory tree another lane owns. `.github/workflows/**` belongs to L2 with one exception: `.github/workflows/lane-guard.yml` is owned by L0 (FD-003, carve-out).

### 2.2 Owned processes

1. **The Phase 0 contract freeze.** L0 authors `contracts/**` before any lane starts, and freezes it.
2. **The partition.** L0 maintains `lane-paths.tsv` and `lane-guard.sh`; L0 is the residual owner of every path.
3. **The merge train.** L0 runs it in the fixed order `L1 → L4 → L2 → L3 → L5`, once per cycle.
4. **Promotion.** `integration → main` only when the full gate passes.
5. **The decision register.** Every reserved decision is closed by L0 and written as a decision record.
6. **Escalation intake.** Blocker issues and Contract Change Requests, answered on the cadence of §8.
7. **The bootstrap log.** The weekly three-field entry under `records/bootstrap-log/` (§95.4).

### 2.3 The residual-ownership rule (L0D-04)

A path that `lane-paths.tsv` assigns to no lane is **blocked for everyone** and escalates to L0, which either
assigns it to a lane by extending the map or claims it for L0. Silently defaulting unassigned paths to L0 would
let the partition erode without anyone noticing; blocking them keeps the map honest. Root-level files are the one
exception and belong to L0 by the catch-all rule, matching PARTITION.md.

---

## 3. The authority boundary

L0 holds four things absolutely. Nothing in a lane file, a lane branch, a lane PR description or a lane blocker
issue moves any of them.

| # | Pillar | Statement |
|---|---|---|
| 1 | **Contracts** | `contracts/**` is written by L0 in Phase 0 and FROZEN. A lane codes against it and against the generated stubs and fixtures. A lane needing a change files a Contract Change Request; it never edits `contracts/**` (PARTITION.md rule 2) |
| 2 | **The partition** | One owner per path. A lane PR touching a foreign path FAILS `lane-guard`. No exceptions, no overrides, no "just this once" (PARTITION.md rule 1) |
| 3 | **The merge train** | Order, cadence, conflict resolution, revert-versus-roll-forward, and promotion to `main` are L0's alone. A lane never merges or rebases another lane's branch (PARTITION.md §"Branch & merge model") |
| 4 | **Every design-open item of §99.3** | All seven are L0 decisions. A lane that finds itself inventing one has hit a STOP condition (§4 below) |

**Corollary, binding.** If a lane task cannot be executed without designing, choosing or interpreting, the task is
defective and the decision belongs to L0 (PARTITION.md §"AI developer profile"). The lane stops and escalates. It
does not guess, does not pick "the obvious option", and does not leave a `TODO` in code.

---

## 4. The seven design-open items — reserved to L0, all of them

§99.3 names exactly seven matters the implementer must still invent. Each is assigned a plan-local decision id
below. These ids are **plan-local, not Appendix A Decision Register ids** — they never collide with `D1…D112`.

| Plan id | §99.3 item | The open matter | Closed no later than |
|---|---|---|---|
| **L0D-10** | 1 | The attention classifier and constraint diagnosis algorithm — Healthy / Watch / Action Required with the reason on the same line, and "which constraint binds" | Phase G3 (§98.5) |
| **L0D-11** | 2 | The `make parity` declaration format — the environment-schema format compared across local, staging and production, defined once and reused | Phase 4 (§98.2), because Phase 4's completion check runs `make parity` |
| **L0D-12** | 3 | Plan-checker internals — every assumed capability verified against the exact pinned GSD release, and the in-house build budgeted if verification fails | Phase 7 (§98.2); the verification itself is a Phase 1 item (§99.6 risk 4) |
| **L0D-13** | 4 | DevLake field coverage — which metrics need bespoke computation beyond DevLake's models (routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread) | Before Phase G3 (§98.5 states G3 depends on confirmed coverage) |
| **L0D-14** | 5 | Machine sources for context checks — where the computable boundary is drawn across the fifteen systemic context checks of §80, with the humans named in §80.2 classifying the rest | Phase P4 (§98.6) |
| **L0D-15** | 6 | KPI instrumentation projects — scoping each §79 row marked "available after instrumentation" as its own mini-project | Phase P2 (§98.6) |
| **L0D-16** | 7 | Calibration methods — PLU fit, forecast scoring, sustainable-utilisation bands, the §97.4 attention-session parameters, the §72.3 confidence table | Quarterly refits; first method recorded at Phase G5 (§98.5) |

Until an item is closed, **no lane may build anything whose behaviour depends on it.** A lane that reaches such a
dependency files a blocker (§7.1) naming the L0D id.

---

## 5. The L0-only decision register — what only L0 may decide

Plan-local ids. Every closure is written as a decision record under `records/decisions/` using the §97.2 schema,
and every open prompt as a record under `records/decisions/pending/` via the record-decision CLI (§97.2).

### 5.1 Contracts and schemas

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-01 | The shape of every registry, product, record and event schema, and its direct transcription to JSON Schema | §7, §8, §15, §97.2 |
| L0D-02 | `contract_version` policy: what constitutes a breaking change, the supported-version window, deprecation deadlines | §60, invariant 73 |
| L0D-03 | `record_schema_version` and `event_schema_version` handling; the binding event envelope field list | §97.2, §97.3 |
| L0D-17 | Every value marked **calibrated configuration** and its stated initial value — including "sustained" (initial 6 consecutive weeks, SIG-07/SIG-08/SIG-30), the bootstrap-log staleness window (initial 7 days, §95.4), the triage budget (initial 5 minutes per product per pass, §94.3), the AI-eval triage block (initial 30 minutes, §94.3), the SIG-42 regression tolerance (initial 5 percentage points, §52.2), the §29.5 scope-growth threshold | §84.6, AT-074, D102 |

### 5.2 Partition, ownership and access

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-04 | The path→lane map and residual ownership; any extension of `lane-paths.tsv` | PARTITION.md rule 1 |
| L0D-05 | Any `CODEOWNERS` edit; the rule that CODEOWNERS carries human identities only | §98.2 Phase 1 completion check |
| L0D-18 | Fail-closed versus fail-open classification of every control | §64, invariant 80 |
| L0D-25 | Secrets-tier assignment and credential scope, including the records-writer's `contents: write` scope and the reconciler's declared repair scope | §40.1, §26.4, D89, invariant 25 |
| L0D-26 | Anything touching subsystem L / Layer B datasource separation — the second Founder-only Grafana instance, the separately-credentialed people datasource | §90.3, §92.8, D75, invariants 106 and 109 |

### 5.3 Merge train and release

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-06 | Approving or denying a Contract Change Request | PARTITION.md rule 2 |
| L0D-07 | Any deviation from the fixed merge order `L1 → L4 → L2 → L3 → L5` | PARTITION.md §"Branch & merge model" |
| L0D-08 | Revert versus roll-forward when `integration` breaks | §28, invariant 27 |
| L0D-09 | Promotion `integration → main` | PARTITION.md §"Branch & merge model" |

### 5.4 Programme governance

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-19 | Opening and closing every bootstrap exception, with expiry, owner and deactivation trigger | §95, §54.2, invariant 77, SIG-39 |
| L0D-20 | Declaring a phase `declined` — a recorded decision carrying the gate answers, the forgone capabilities and a review date | §98.1 |
| L0D-21 | Releasing the P0-before-P2 lock (only a `declined` P0 releases it; an unbuilt P0 holds it) | §98.1 |
| L0D-22 | The drift-budget tolerances and headline thresholds in `os-health.yaml`, and each signal's `activation_dependency` and `lookback_window` | §52.1, §52.2 (D77), §53.4 |
| L0D-23 | The enforcement classification — mechanical / policy / review-held — of each of the 111 invariants | §101 preamble, authored at Phase G2 |
| L0D-24 | Accepting a risk or recording a plan-tier fallback (branch protection on private repos requires the Team plan; environment required reviewers are Enterprise-only and are not depended on) | §99.5, §99.6 risk 5, D73, D80 |

---

## 6. Decisions the lanes are FORBIDDEN to make

This is the operative list for an AI lane executor. **If a task requires any of the following, STOP and escalate.**
It is never a judgment call whether an item is on the list — if the action appears below, it is forbidden.

### 6.1 Absolutely forbidden — no lane, ever

| # | Forbidden action | Why | Escalate as |
|---|---|---|---|
| F-01 | Editing any file under `contracts/**` | Contracts are frozen in Phase 0 (PARTITION.md rule 2) | CCR |
| F-02 | Editing `CODEOWNERS`, `Makefile`, `lane-paths.tsv`, `lane-guard.sh`, or any repository-root file | L0-owned | Blocker |
| F-03 | Editing any path the lane does not own | PARTITION.md rule 1 | Blocker |
| F-04 | Creating or appending to a shared index, list, manifest or registry-of-everything | PARTITION.md rule 3 — directory-per-item only | Blocker |
| F-05 | Importing from, referencing, or reading another lane's source tree | PARTITION.md rule 4 | CCR |
| F-06 | Merging, rebasing, force-pushing or deleting another lane's branch | PARTITION.md §"Branch & merge model" | Blocker |
| F-07 | Adding a required status check to branch protection | The list starts empty per repository and is populated only as each check comes into existence, named by its phase (§98.2 Phase 1) | Blocker |
| F-08 | Granting, widening or bypassing any permission, secret scope or ruleset bypass actor | Invariants 25, 79, 87; D89 forbids a machine bypass actor on `control-plane` | Blocker |
| F-09 | Introducing a metered LLM API or a free cloud LLM tier into engineering tooling, or setting an API key anywhere | Invariants 83 and 84; §98.2 Phase 1 verifies `env \| grep -i api_key` returns empty | Blocker |
| F-10 | Consuming a third-party GitHub Action by tag, branch or floating ref | Invariant 85 — third-party actions are pinned to full commit SHAs; reusable workflows by pinned tag | Blocker |
| F-11 | Writing a record or event by hand-editing a file, or having any machine identity approve anything | §97.1 — the credential writes records, it approves nothing (D76 as amended by D89) | Blocker |
| F-12 | Rebuilding an artifact, or writing any code path that could rebuild for production | Invariants 22 and 23 | Blocker |
| F-13 | Writing code that could auto-repair toward a looser state | Invariant 81; AT-033; §99.6 risk 6 | Blocker |
| F-14 | Placing any customer data — fixtures, support records, incident evidence included — in git | Invariant 111 | Blocker |
| F-15 | Creating any code path to an automated improvement plan, termination, promotion, compensation change or formal warning | Invariant 37; AT-071 | Blocker |
| F-16 | Adding a per-person raw-activity drill-down or any per-person value to a general engineering surface | Invariants 98, 99, 109; AT-089 | Blocker |
| F-17 | Generating any Layer B evidence before the datasource separation is verified | §98.6 sequencing rule: P4 must not begin before AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds | Blocker |
| F-18 | Inventing a spec section number, AT id, invariant number, SIG id or D id | The catalogues are closed: 110 acceptance tests (§100), 111 invariants (§101), 47 signals (§52.2) | Blocker |

### 6.2 Forbidden without an L0 ruling — the "do not choose" list

| # | The lane must not choose | The L0 decision that covers it |
|---|---|---|
| C-01 | A field name, type, enum value, or required/optional status in any schema | L0D-01 |
| C-02 | A threshold, window, tolerance, band, cadence or any number described as "calibrated" | L0D-17, L0D-22 |
| C-03 | Whether a schema change is breaking, and what version it becomes | L0D-02 |
| C-04 | Whether a control fails closed or fails open | L0D-18 |
| C-05 | A retention or diagnostic window for telemetry | Invariant 47 — retention classes are declared in the control plane and Founder-owned; L0D-22 |
| C-06 | The severity, drift class or response time of any finding | L0D-22, §53 |
| C-07 | Which of the 111 invariants a check enforces, or its enforcement classification | L0D-23 |
| C-08 | A default when the spec is silent or ambiguous | L0D-01 through L0D-26 as applicable; if none fits, L0 rules on it fresh |
| C-09 | Anything in the seven §99.3 design-open items | L0D-10 … L0D-16 |
| C-10 | A tool, library, service or vendor not already named in the spec | §62 tool register; invariant 83; L0D-24 |
| C-11 | Accepting a risk, or deferring a requirement | L0D-19, L0D-24 — a deferral is only ever a dated `exceptions.yaml` entry with owner and deactivation trigger (§54.2, §98.2 Phase 2) |
| C-12 | Reinterpreting a spec sentence that reads two ways | L0 rules; the lane quotes the sentence verbatim in the blocker |

### 6.3 The one thing a lane may always do without asking

Add a **new file inside a path it owns**, conforming to a frozen contract, with a test. Additive-only within the
lane is the default working mode (PARTITION.md rule 5).

---

## 7. Escalation protocol

Two channels, and only two. Choosing between them is mechanical: if the fix requires a change to `contracts/**`,
it is a CCR; otherwise it is a Blocker.

### 7.1 Blocker issue template

Copy verbatim into a GitHub issue titled `BLOCKER <task-id>: <one line>`, label `blocker`, `lane-<N>`.
The canonical copy lives at `docs/escalation/BLOCKER.md` (created by task **L0-00-05**).

```text
TASK ID:        <e.g. L1-03-07>
LANE:           <1|2|3|4|5>
BRANCH:         lane/<N>/<phase>-<task>
STOPPED AT:     <the exact command or step number in the task that could not complete>

WHAT I WAS ASKED TO DO
<verbatim quote of the task step>

WHY I CANNOT PROCEED
<one of: forbidden action F-01..F-18 | undecided item C-01..C-12 | contract does not cover the case
 | acceptance criterion is not provable by any command | spec sentence reads two ways>

FORBIDDEN/UNDECIDED ID:   <F-nn or C-nn or L0D-nn, or NONE>
SPEC SENTENCE QUOTED:     <verbatim, with section number; or NONE>

EXACT OUTPUT OBSERVED
<paste the literal command and its literal output>

WHAT I DID NOT DO
I made no choice, wrote no default, left no TODO, and pushed no code past this point.

FILES TOUCHED SO FAR
<git status --porcelain output>
```

### 7.2 Contract Change Request template

Titled `CCR <task-id>: <contract path>`, label `ccr`, `lane-<N>`. Canonical copy at `docs/escalation/CCR.md`.

```text
TASK ID:            <e.g. L4-02-03>
CONTRACT FILE:      contracts/<path>
CONTRACT VERSION:   <value of contract_version / record_schema_version in that file>

WHAT THE CONTRACT SAYS NOW
<verbatim excerpt>

WHAT THE TASK REQUIRES
<verbatim quote of the task step>

THE GAP, STATED AS A FACT
<one sentence; no proposed wording, no suggested field names — proposing the fix is L0D-01/L0D-06>

BLAST RADIUS I CAN OBSERVE
<grep output showing every file in MY lane that reads this contract>

I HAVE NOT EDITED contracts/**.
```

### 7.3 Response commitment

| Channel | L0 reads at | Answer by |
|---|---|---|
| Blocker | 09:30 and 16:30 sweeps (§8.1) | Same working day |
| CCR | 17:00 contract window (§8.1) | Next working day; a CCR that changes a frozen contract also produces a decision record and a `contracts.sha256` re-freeze |

A lane **does not poll and does not proceed** while a blocker is open. It moves to the next task whose dependencies
are satisfied, or it stops. Waiting is correct behaviour; guessing is not.

---

## 8. Cadence

### 8.1 Daily — the integrator's day

Grounded in the day model of §94.2 and the Team Lead priority model of §94.5. During the build the human lead
holds both the Founder and Team Lead surfaces (§98.7: "the Founder solo under Bootstrap Mode").

| Time | L0 activity | Output |
|---|---|---|
| 09:30 | Blocker sweep. Read every open `blocker` issue opened since the last sweep | Each answered, or converted to an L0D decision and dated |
| 09:45 | `integration` health: `make lane-guard` across every lane branch pushed overnight | Green list; any red branch is told to stop |
| 10:00 | Drift and orphan alerts on the control-plane repository itself — SIG-03 permission drift, SIG-05 orphan risk, SIG-13 failed reconciliations | Blocking-class items actioned before anything else |
| 10:30 | **Contract-freeze integrity check**: `make promote-check` sub-step verifying `contracts.sha256` still matches | `CONTRACTS-FROZEN OK` |
| 10:30–13:00 | Heavy block (§94.2). L0 authoring: contracts, docs, decision records | The day's L0 deliverable |
| 14:00 | Window-tight block: lane PR review — partition compliance and contract conformance only, never style | Approvals or change requests |
| 16:30 | Second blocker sweep | Same-day close on everything opened before 16:00 |
| 17:00 | **Contract window** — the only time `contracts/**` is edited, and only under an approved CCR | Re-freeze + decision record |
| 17:30 | End-of-day readiness check (§94.5 priority 10), adapted to the build: every lane has an unblocked next task; no unactioned Blocking-class drift; no blocker older than one working day; no lane branch older than one day unrebased | Actioned or explicitly carried over with a recorded reason |

**Only these interrupt L0** (§94.5, adapted): a blocker issue, a CCR, Blocking-class drift, a red `integration`,
and a lane branch that has touched a foreign path. Routine lane PR notifications do not.

### 8.2 Weekly — the integrator's week

| When | L0 activity | Anchor |
|---|---|---|
| Monday 09:30 | Portfolio review of the build: phase position per lane, P0-before-P2 lock status, every open L0D | §94.8 |
| Monday 10:00 | Which constraint binds this week — which lane is the bottleneck, and whether it is a contract gap or a capacity gap | §94.6 |
| Monday 14:00 | Verification sequence for the week — which acceptance tests of §100 become provable this week | §94.8 |
| **Wednesday** | **MERGE TRAIN** — the weekly cycle, run in the fixed order (§9) | PARTITION.md |
| Midweek, default Thursday | Standing decision window, thirty minutes: every open L0D prompt actioned, deferred with a date, or explicitly declined | §94.6, D79 |
| Friday 15:00 | Freeze: no promotion `integration → main` after this point in the week | §94.8 |
| Friday 16:30 | Weekly banded attention self-report, five minutes | §94.8, §97.4 |
| Friday 17:00 | **Weekly bootstrap log entry** under `records/bootstrap-log/` — the fixed three-field template: gates stubbed and armed; bootstrap exceptions opened and closed; phase completion checks run and their results. Two of the three fields are generator-filled; L0 writes the judgment lines | §95.4, §94.8 |
| Friday 17:15 | Next week's lane queue refilled — every lane has a Ready task with satisfied dependencies | §94.5 priority 6 |

The bootstrap-log entry is not optional and has a detector: control-plane CI raises **Blocking** drift when the
newest entry is older than the calibrated staleness window, initial value 7 days (§95.4, L0D-17).

### 8.3 Monthly and quarterly

| Cadence | L0 activity | Anchor |
|---|---|---|
| Monthly | Dependency, Scorecard, cost-band and asset-expiry sweep across the two repositories | §94.8 |
| Monthly | Judgment-capture ritual, 15 minutes: the month's classification and routing judgment calls recorded so they feed Coordination attention and calibration | §94.8 |
| Quarterly, month 1 | Operating-system review from the generated review pack — retires at least one policy, one metric or one automation, or records why nothing warranted retirement (AT-045) | §94.8, §98.5 G8 |
| Quarterly, month 2 | Escrow seal audit and its functional verification | §94.8, §14.4 |
| Quarterly, month 3 | Control-plane disaster-recovery drill | §94.8 |

Quarterly rituals are staggered, not stacked; the month assignments above are the spec's stated initial values and
are recalibrated only by the ritual attention-hours budget line of §57.2 (L0D-17).

---

## 9. The merge train

Fixed order, once per cycle: **L1 → L4 → L2 → L3 → L5.** The order is dependency order (PARTITION.md §"Dependency
order"): L1 schemas and L4 record schemas produce what everything validates against; L2 workflows consume L1
schemas; L3 consumes L1 plus the L5 access model; L5 integrates last.

Per lane, in order:

1. Confirm the lane branch is rebased on `integration` and is less than one day old.
2. Run `make lane-guard LANE=<n> BASE=integration HEAD=<branch>` — must print `LANE-GUARD OK`.
3. Run the lane's own SELF-VERIFY block from its plan file — must produce its stated expected output.
4. Merge to `integration` with `--no-ff`.
5. Re-run steps 2–3 for the merged result before starting the next lane.

If any step fails, that lane is **skipped for the cycle** — the train does not stop for it, and the remaining lanes
merge in order behind it. Skipping is L0's call and is recorded; a lane never negotiates its own skip. Revert versus
roll-forward on a broken `integration` is L0D-08.

Promotion `integration → main` (L0D-09) happens only when `make promote-check` passes, and never after Friday 15:00.

---

## 10. L0 TASKS

Nine tasks. Executor: the human lead. All paths are exact; all commands are literal.

---

### L0-00-01 — Establish branch topology and the root CODEOWNERS

**Size:** S · **Dependencies:** none

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch --all --prune
git checkout main
git pull --ff-only
git checkout -b integration 2>/dev/null || git checkout integration
git push -u origin integration

cat > CODEOWNERS <<'EOF'
# CODEOWNERS — owned by L0 (integrator). Human identities only.
# Machine accounts must never appear here: an approval from a machine account
# does not satisfy branch protection, and the check is executed negatively.
# Reference: MasterSpec v4.0 Section 98.2, Phase 1 completion check.
#
# Default owner: the integrator.
*                       @bendrohit-eng

# --- Lane-owned trees (PARTITION.md, FROZEN) ---
/schemas/registry/      @LANE1_REVIEWER
/schemas/product/       @LANE1_REVIEWER
/registries/            @LANE1_REVIEWER
/validators/registry/   @LANE1_REVIEWER
/.github/workflows/     @LANE2_REVIEWER
/templates/workflows/   @LANE2_REVIEWER
/tools/evidence/        @LANE2_REVIEWER
/reconciler/            @LANE3_REVIEWER
/tools/provision/       @LANE3_REVIEWER
/validators/drift/      @LANE3_REVIEWER
/schemas/records/       @LANE4_REVIEWER
/metrics/               @LANE4_REVIEWER
/tools/records/         @LANE4_REVIEWER
/access/                @LANE5_REVIEWER
/infra/                 @LANE5_REVIEWER
/ops-vm/                @LANE5_REVIEWER
/notify/                @LANE5_REVIEWER
/assets/                @LANE5_REVIEWER

# --- L0-exclusive (last match wins in CODEOWNERS) ---
/contracts/             @bendrohit-eng
/docs/                  @bendrohit-eng
/CODEOWNERS             @bendrohit-eng
/Makefile               @bendrohit-eng
/lane-paths.tsv         @bendrohit-eng
/lane-guard.sh          @bendrohit-eng
/contracts.sha256       @bendrohit-eng
EOF

git add CODEOWNERS
git commit -m "L0-00-01: branch topology and root CODEOWNERS"
git push origin integration
```

Replace every `@LANEn_REVIEWER` placeholder with real GitHub logins before committing.
Placeholders left in place are a defect: CODEOWNERS carries human identities only.

Bootstrap the GitHub issue labels that every STOP rule and escalation template uses. Lane agents are forbidden
from creating labels (`L0D-04`); this task is the only place they are created (Step 4 blocker — ~60
`SAFE_TO_DISPATCH` verdicts in `_DISPATCH_GATE.md` depend on the `blocker` label existing).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
gh label create blocker  --color "#B60205" --description "Blocks forward progress; escalate to L0" --force
gh label create lane-1   --color "#0075CA" --description "Owned by Lane 1 (registries/schemas)" --force
gh label create lane-2   --color "#0075CA" --description "Owned by Lane 2 (CI/workflows)" --force
gh label create lane-3   --color "#0075CA" --description "Owned by Lane 3 (reconciler)" --force
gh label create lane-4   --color "#0075CA" --description "Owned by Lane 4 (metrics/records)" --force
gh label create lane-5   --color "#0075CA" --description "Owned by Lane 5 (access/infra)" --force
gh label create lane-0   --color "#6E5494" --description "Owned by Lane 0 (integrator/L0)" --force
gh label list --limit 20
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | `integration` exists on the remote | `git ls-remote --heads origin integration \| wc -l` | `1` |
| 2 | Root `CODEOWNERS` exists | `test -f CODEOWNERS && echo PRESENT` | `PRESENT` |
| 3 | No placeholder logins remain | `grep -c 'LANE[0-9]*_REVIEWER' CODEOWNERS` | `0` |
| 4 | No machine account listed | `grep -ci 'bot\|\[bot\]\|records-writer\|reconciler' CODEOWNERS` | `0` |
| 5 | No `CODEOWNERS` under `.github/` | `test ! -f .github/CODEOWNERS && echo CLEAN` | `CLEAN` |
| 6 | `blocker` label exists (Step 4) | `gh label list \| grep -c '^blocker'` | `1` |
| 7 | All seven lane labels exist | `gh label list \| grep -c '^lane-[0-5]'` | `7` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'branch=%s codeowners=%s placeholders=%s machines=%s dotgithub=%s blocker=%s lanes=%s\n' \
  "$(git ls-remote --heads origin integration | wc -l | tr -d ' ')" \
  "$(test -f CODEOWNERS && echo PRESENT || echo MISSING)" \
  "$(grep -c 'LANE[0-9]*_REVIEWER' CODEOWNERS)" \
  "$(grep -ci 'bot\|\[bot\]\|records-writer\|reconciler' CODEOWNERS)" \
  "$(test ! -f .github/CODEOWNERS && echo CLEAN || echo DIRTY)" \
  "$(gh label list | grep -c '^blocker')" \
  "$(gh label list | grep -c '^lane-[0-5]')"
```

Expected output, exactly:

```
branch=1 codeowners=PRESENT placeholders=0 machines=0 dotgithub=CLEAN blocker=1 lanes=7
```

**STOP rule** — if `git push -u origin integration` is rejected, or if branch protection on `main` cannot be
confirmed as requiring a pull request, do not proceed and do not weaken protection to make the push succeed.
Open a blocker titled `BLOCKER L0-00-01: branch topology` using `docs/escalation/BLOCKER.md`. Loosening
protection to unblock is exactly the failure invariant 81 and §99.6 risk 6 exist to prevent.

---

### L0-00-02 — Publish this charter into the repository

**Size:** S · **Dependencies:** L0-00-01

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p docs/charter
cp "C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L0-00-charter.md" docs/charter/L0-charter.md
cp "C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md"          docs/charter/PARTITION.md

cat > docs/README.md <<'EOF'
# control-plane documentation

| Document | What it governs |
|---|---|
| `charter/L0-charter.md` | The integrator charter: ownership, reserved decisions, cadence, merge train |
| `charter/PARTITION.md`  | The FROZEN lane partition. Authoritative. Never edited by a lane |
| `escalation/BLOCKER.md` | Blocker issue template |
| `escalation/CCR.md`     | Contract Change Request template |
| `decisions/L0-decision-register.md` | The L0-only decision register, L0D-01 .. L0D-26 |
| `cadence/L0-cadence.md` | The daily and weekly checklist the integrator runs |
| `merge-train.md`        | The merge-train runbook |
EOF

git add docs
git commit -m "L0-00-02: publish integrator charter and frozen partition"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Charter published | `test -f docs/charter/L0-charter.md && echo PRESENT` | `PRESENT` |
| 2 | Partition published byte-identical | `diff -q docs/charter/PARTITION.md "C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md" && echo IDENTICAL` | `IDENTICAL` |
| 3 | Docs index present | `test -f docs/README.md && echo PRESENT` | `PRESENT` |
| 4 | Charter names all five lanes | `grep -c 'L1\|L2\|L3\|L4\|L5' docs/charter/L0-charter.md` | a number `> 0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'charter=%s partition=%s index=%s\n' \
  "$(test -f docs/charter/L0-charter.md && echo PRESENT || echo MISSING)" \
  "$(diff -q docs/charter/PARTITION.md "C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md" >/dev/null 2>&1 && echo IDENTICAL || echo DIVERGED)" \
  "$(test -f docs/README.md && echo PRESENT || echo MISSING)"
```

Expected output, exactly:

```
charter=PRESENT partition=IDENTICAL index=PRESENT
```

**STOP rule** — if `diff` reports `DIVERGED`, the published partition is not the frozen one. Do not edit either
file to make them match. Open `BLOCKER L0-00-02: partition divergence` and resolve which copy is authoritative
before any lane starts. A divergent partition is an unenforceable partition.

---

### L0-00-03 — Author the machine-readable partition map

**Size:** M · **Dependencies:** L0-00-02

The map is TSV, not YAML, so `lane-guard.sh` needs no parser and no dependency. That choice is L0D-04.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf '%s\n' \
'# lane-paths.tsv — machine-readable form of PARTITION.md. L0-owned (L0D-04).' \
'# Describes control-plane only; control-plane-records has no lane guard (L0D-LG-6, REG-055).' \
'# Format: <lane><TAB><sh glob>. First match wins, so order is significant.' \
'# Lane X = unassigned nested path: blocked for everyone, escalates to L0.' \
'# Lane 0 = L0 (integrator). The final catch-all covers repository-root files.' > lane-paths.tsv
printf '0\tcontracts/\n0\t.github/workflows/\n2\t.github/workflows/build.yml\n0\tlane-paths.tsv\n0\tMakefile\n0\tcontracts/event-types.yaml\n0\tcontracts/tag-ruleset.json\n0\tcontracts/lane-paths.yaml\n0\tcontracts/harness/\n0\te2e/\n' >> lane-paths.tsv
printf '1\tschemas/registry/*\n1\tschemas/product/*\n1\tregistries/*\n1\tvalidators/registry/*\n' >> lane-paths.tsv
printf '0\t.github/workflows/lane-guard.yml\n'                                                   >> lane-paths.tsv
printf '2\t.github/workflows/*\n2\ttemplates/workflows/*\n2\ttools/evidence/*\n'                 >> lane-paths.tsv
printf '3\treconciler/*\n3\ttools/provision/*\n3\tvalidators/drift/*\n'                          >> lane-paths.tsv
printf '4\tschemas/records/*\n4\tmetrics/*\n4\ttools/records/*\n'                                >> lane-paths.tsv
printf '5\taccess/*\n5\tinfra/*\n5\tops-vm/*\n5\tnotify/*\n5\tassets/*\n'                        >> lane-paths.tsv
printf '0\tcontracts/*\n0\tdocs/*\n'                                                             >> lane-paths.tsv
printf '0\tplan-checker/*\n'                                                                     >> lane-paths.tsv
printf '0\tverification/acceptance/**\n'                                                         >> lane-paths.tsv
printf '0\ttools/at/**\n'                                                                        >> lane-paths.tsv
printf '0\ttools/train/**\n'                                                                     >> lane-paths.tsv
printf '0\te2e/*\n'                                                                              >> lane-paths.tsv
printf '0\ttools/lane-guard/*\n'                                                                 >> lane-paths.tsv
printf '0\tderived/**\n'                                                                         >> lane-paths.tsv
printf '0\tgate-state/**\n'                                                                      >> lane-paths.tsv
printf 'X\t*/*\n'                                                                                >> lane-paths.tsv
printf '0\t*\n'                                                                                  >> lane-paths.tsv

# Emit contracts/lane-paths.yaml — mirror of lane-paths.tsv for UEG-2 (master/05).
# Describes control-plane only; control-plane-records has no lane guard (L0D-LG-6, REG-055)
mkdir -p contracts
cat > contracts/lane-paths.yaml <<'LPYAML'
# Generated by L0-00-03 from the same source as lane-paths.tsv
# For use by UEG-2 (master/05) — describes control-plane only
# Describes control-plane only; control-plane-records has no lane guard (L0D-LG-6, REG-055)
entries:
  - path: "contracts/"
    owner: L0
    rule: exclusive
  - path: ".github/workflows/"
    owner: L0
    rule: exclusive
  - path: ".github/workflows/build.yml"
    owner: L2
    rule: exclusive
  - path: "lane-paths.tsv"
    owner: L0
    rule: exclusive
  - path: "Makefile"
    owner: L0
    rule: exclusive
  - path: "contracts/event-types.yaml"
    owner: L0
    rule: exclusive
  - path: "contracts/tag-ruleset.json"
    owner: L0
    rule: exclusive
  - path: "contracts/lane-paths.yaml"
    owner: L0
    rule: exclusive
  - path: "contracts/harness/"
    owner: L0
    rule: exclusive
  - path: "e2e/"
    owner: L0
    rule: exclusive
  - lane: "1"
    path: "schemas/registry/*"
  - lane: "1"
    path: "schemas/product/*"
  - lane: "1"
    path: "registries/*"
  - lane: "1"
    path: "validators/registry/*"
  - lane: "0"
    path: ".github/workflows/lane-guard.yml"
  - lane: "2"
    path: ".github/workflows/*"
  - lane: "2"
    path: "templates/workflows/*"
  - lane: "2"
    path: "tools/evidence/*"
  - lane: "3"
    path: "reconciler/*"
  - lane: "3"
    path: "tools/provision/*"
  - lane: "3"
    path: "validators/drift/*"
  - lane: "4"
    path: "schemas/records/*"
  - lane: "4"
    path: "metrics/*"
  - lane: "4"
    path: "tools/records/*"
  - lane: "5"
    path: "access/*"
  - lane: "5"
    path: "infra/*"
  - lane: "5"
    path: "ops-vm/*"
  - lane: "5"
    path: "notify/*"
  - lane: "5"
    path: "assets/*"
  - lane: "0"
    path: "contracts/*"
  - lane: "0"
    path: "docs/*"
  - lane: "0"
    path: "plan-checker/*"
  - lane: "0"
    path: "verification/acceptance/**"
  - lane: "0"
    path: "tools/at/**"
  - lane: "0"
    path: "tools/train/**"
  - lane: "0"
    path: "e2e/*"
  - lane: "0"
    path: "tools/lane-guard/*"
  - lane: "0"
    path: "derived/**"
  - lane: "0"
    path: "gate-state/**"
  - lane: "X"
    path: "*/*"
  - lane: "0"
    path: "*"
LPYAML

git add lane-paths.tsv contracts/lane-paths.yaml
git commit -m "L0-00-03: machine-readable partition map (L0D-04)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 41 rules, comments excluded | `grep -vc '^#' lane-paths.tsv` | `41` |
| 2 | Every rule is tab-separated with two fields | `awk -F'\t' '!/^#/ && NF!=2' lane-paths.tsv \| wc -l` | `0` |
| 3 | Every PARTITION lane tree appears | `for p in schemas/registry schemas/product registries validators/registry .github/workflows templates/workflows tools/evidence reconciler tools/provision validators/drift schemas/records metrics tools/records access infra ops-vm notify assets contracts docs; do grep -q "	$p/\*$" lane-paths.tsv \|\| echo "MISSING $p"; done` | no output |
| 4 | No lane tree assigned twice | `awk -F'\t' '!/^#/{print $2}' lane-paths.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 5 | The `X` residual rule precedes the catch-all | `grep -n '^X\|^0	\*$' lane-paths.tsv \| tail -2 \| cut -d: -f1 \| tr '\n' ' '` | two ascending numbers |
| 6 | Symmetric difference between `lane-paths.tsv` and `contracts/lane-paths.yaml` is empty — both carry identical prefix sets | `diff <(awk -F'\t' '!/^#/{print $2}' lane-paths.tsv \| sort) <(grep '^ *path:' contracts/lane-paths.yaml \| sed 's/.*path: "//;s/"$//' \| sort) && echo IDENTICAL` | `IDENTICAL` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
miss=$(for p in schemas/registry schemas/product registries validators/registry .github/workflows \
  templates/workflows tools/evidence reconciler tools/provision validators/drift schemas/records \
  metrics tools/records access infra ops-vm notify assets contracts docs; do
  grep -q "	$p/\*$" lane-paths.tsv || echo x; done | wc -l | tr -d ' ')
symdiff=$(diff \
  <(awk -F'\t' '!/^#/{print $2}' lane-paths.tsv | sort) \
  <(grep '^ *path:' contracts/lane-paths.yaml | sed 's/.*path: "//;s/"$//' | sort) \
  | wc -l | tr -d ' ')
printf 'rules=%s malformed=%s missing=%s dupes=%s symdiff=%s\n' \
  "$(grep -vc '^#' lane-paths.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=2' lane-paths.tsv | wc -l | tr -d ' ')" \
  "$miss" \
  "$(awk -F'\t' '!/^#/{print $2}' lane-paths.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$symdiff"
```

Expected output, exactly:

```
rules=41 malformed=0 missing=0 dupes=0 symdiff=0
```

**STOP rule** — if `missing` is non-zero, the map does not cover the frozen partition. Do not add the missing
tree from memory and do not guess its lane. Re-read `docs/charter/PARTITION.md` and copy the row verbatim. If the
tree genuinely is not in PARTITION.md, open `BLOCKER L0-00-03: unassigned tree <path>` — assigning it is L0D-04.

---

### L0-00-04 — Author the lane guard and the Makefile gates

**Size:** M · **Dependencies:** L0-00-03

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > lane-guard.sh <<'GUARD'
#!/usr/bin/env sh
# lane-guard.sh — L0-owned. Enforces PARTITION.md rule 1: one owner per path.
# Usage: ./lane-guard.sh <lane 0..5> <base-ref> <head-ref>
set -eu
LANE="${1:?lane required}"; BASE="${2:?base ref required}"; HEAD="${3:?head ref required}"
MAP="$(dirname "$0")/lane-paths.tsv"
[ -f "$MAP" ] || { echo "LANE-GUARD FAIL: lane-paths.tsv missing"; exit 2; }

owner_of() {
  _f="$1"; _own=""
  while IFS='	' read -r _lane _pat; do
    case "$_lane" in ''|\#*) continue ;; esac
    # shellcheck disable=SC2254
    case "$_f" in $_pat) _own="$_lane"; break ;; esac
  done < "$MAP"
  echo "${_own:-X}"
}

VIOL=0
for f in $(git diff --name-only "$BASE"..."$HEAD"); do
  o=$(owner_of "$f")
  if [ "$o" = "X" ]; then
    echo "LANE-GUARD VIOLATION: $f is an UNASSIGNED path (escalate to L0, L0D-04)"; VIOL=$((VIOL+1))
  elif [ "$o" != "$LANE" ]; then
    echo "LANE-GUARD VIOLATION: $f is owned by lane $o, not lane $LANE"; VIOL=$((VIOL+1))
  fi
done

if [ "$VIOL" -eq 0 ]; then echo "LANE-GUARD OK"; exit 0; fi
echo "LANE-GUARD FAIL: $VIOL violation(s)"; exit 1
GUARD
chmod +x lane-guard.sh

cat > Makefile <<'MK'
# Makefile — L0-owned. The local, authoritative gates.
SHELL := /bin/sh
LANE ?= 0
BASE ?= integration
HEAD ?= HEAD

.PHONY: lane-guard train freeze gate-freeze promote-check

lane-guard:
	@./lane-guard.sh $(LANE) $(BASE) $(HEAD)

train:
	@echo "MERGE TRAIN ORDER (FROZEN): L1 -> L4 -> L2 -> L3 -> L5"
	@echo "Per lane: rebase -> lane-guard -> lane SELF-VERIFY -> merge --no-ff -> re-verify"

freeze:
	@test -d contracts || { echo "CONTRACTS-NOT-FROZEN: contracts/ does not exist"; exit 1; }
	@find contracts -type f -not -path 'contracts/gate/*' -not -path 'contracts/ci/*' \
	  | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 > contracts.sha256
	@echo "CONTRACTS-FROZEN $$(cat contracts.sha256)"

gate-freeze:
	@test -d contracts/gate || { echo "GATE-NOT-FROZEN: contracts/gate/ does not exist"; exit 1; }
	@find contracts/gate -type f -not -name PHASE \
	  | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 > gate.sha256
	@echo "GATE-FROZEN $$(cat gate.sha256)"

promote-check:
	@test -d contracts || { echo "CONTRACTS-NOT-FROZEN: contracts/ does not exist"; exit 1; }
	@test -f contracts.sha256 || { echo "CONTRACTS-NOT-FROZEN: no freeze hash recorded"; exit 1; }
	@now=$$(find contracts -type f -not -path 'contracts/gate/*' -not -path 'contracts/ci/*' \
	  | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1); \
	 was=$$(cat contracts.sha256); \
	 if [ "$$now" = "$$was" ]; then echo "CONTRACTS-FROZEN OK"; \
	 else echo "CONTRACTS-DRIFT: frozen=$$was actual=$$now"; exit 1; fi
MK

git add lane-guard.sh Makefile
git commit -m "L0-00-04: lane guard and Makefile gates"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Guard is executable | `test -x lane-guard.sh && echo EXEC` | `EXEC` |
| 2 | Guard passes a clean same-lane diff | see SELF-VERIFY case A | `LANE-GUARD OK` |
| 3 | Guard fails a foreign-path diff | see SELF-VERIFY case B | `LANE-GUARD FAIL: 1 violation(s)` |
| 4 | Guard fails an unassigned nested path | see SELF-VERIFY case C | line containing `UNASSIGNED path` |
| 5 | `make train` prints the frozen order | `make train \| head -1` | `MERGE TRAIN ORDER (FROZEN): L1 -> L4 -> L2 -> L3 -> L5` |
| 6 | `promote-check` refuses before the freeze | `make promote-check; echo "rc=$?"` | `rc=1` while `contracts/` is absent |
| 7 | `freeze` and `promote-check` exclude the gate and CI trees (FD-029/B-01) | `make freeze 2>&1 \| grep -c 'gate\|ci'` | `0` (the exclusion is in the `find` filter, not in output) |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout -b tmp/guard-selftest integration

mkdir -p registries && echo "a: 1" > registries/probe.yaml
git add -A && git commit -q -m "probe A"
A=$(./lane-guard.sh 1 integration HEAD | tail -1)

mkdir -p reconciler && echo "b" > reconciler/probe.txt
git add -A && git commit -q -m "probe B"
B=$(./lane-guard.sh 1 integration HEAD | tail -1)

mkdir -p unassigned/tree && echo "c" > unassigned/tree/probe.txt
git add -A && git commit -q -m "probe C"
C=$(./lane-guard.sh 1 integration HEAD | grep -c 'UNASSIGNED path')

printf 'A=[%s] B=[%s] C=%s\n' "$A" "$B" "$C"

git checkout integration && git branch -D tmp/guard-selftest
```

Expected output, exactly:

```
A=[LANE-GUARD OK] B=[LANE-GUARD FAIL: 2 violation(s)] C=1
```

(Case B reports 2 because the probe branch still carries case A's file relative to `integration`; the relevant
fact is that it is non-zero and names `reconciler/probe.txt` as owned by lane 3.)

**STOP rule** — if case B prints `LANE-GUARD OK`, the guard does not enforce the partition and **no lane may
start**. Do not adjust the expected output to match. Open `BLOCKER L0-00-04: lane guard does not fail foreign
paths` and fix the guard before any lane branch is created. An unenforced partition produces exactly the merge
conflicts PARTITION.md rule 1 exists to make impossible.

---

### L0-00-05 — Author the escalation templates

**Size:** S · **Dependencies:** L0-00-02

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p docs/escalation
```

Copy the block in **§7.1** of this charter verbatim into `docs/escalation/BLOCKER.md`, and the block in **§7.2**
verbatim into `docs/escalation/CCR.md`, each preceded by a one-line title and the response commitment table of §7.3.

**Commands**

```bash
set -euo pipefail
git add docs/escalation
git commit -m "L0-00-05: blocker and CCR escalation templates"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both templates exist | `ls docs/escalation \| sort \| tr '\n' ' '` | `BLOCKER.md CCR.md ` |
| 2 | Blocker template carries every required field | `for k in 'TASK ID' 'LANE' 'STOPPED AT' 'FORBIDDEN/UNDECIDED ID' 'SPEC SENTENCE QUOTED' 'EXACT OUTPUT OBSERVED' 'WHAT I DID NOT DO'; do grep -q "$k" docs/escalation/BLOCKER.md \|\| echo "MISSING $k"; done` | no output |
| 3 | CCR template forbids proposing wording | `grep -c 'no proposed wording' docs/escalation/CCR.md` | `1` |
| 4 | CCR template asserts contracts untouched | `grep -c 'I HAVE NOT EDITED contracts' docs/escalation/CCR.md` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
miss=$(for k in 'TASK ID' 'LANE' 'STOPPED AT' 'FORBIDDEN/UNDECIDED ID' 'SPEC SENTENCE QUOTED' \
  'EXACT OUTPUT OBSERVED' 'WHAT I DID NOT DO'; do
  grep -q "$k" docs/escalation/BLOCKER.md || echo x; done | wc -l | tr -d ' ')
printf 'files=[%s] blocker_missing=%s ccr_nowording=%s ccr_untouched=%s\n' \
  "$(ls docs/escalation | sort | tr '\n' ' ')" "$miss" \
  "$(grep -c 'no proposed wording' docs/escalation/CCR.md)" \
  "$(grep -c 'I HAVE NOT EDITED contracts' docs/escalation/CCR.md)"
```

Expected output, exactly:

```
files=[BLOCKER.md CCR.md ] blocker_missing=0 ccr_nowording=1 ccr_untouched=1
```

**STOP rule** — if a required field is missing, do not invent a replacement field name. The field list is fixed
because L0 triages on it. Re-copy §7.1 verbatim from `docs/charter/L0-charter.md`.

---

### L0-00-06 — Publish the L0 decision register

**Size:** M · **Dependencies:** L0-00-02

Create `docs/decisions/L0-decision-register.md` containing, verbatim, §4 and §5 of this charter — the seven
design-open items **L0D-10 … L0D-16** and the reserved decisions **L0D-01 … L0D-26** with their spec anchors — plus
this header:

```text
# L0 DECISION REGISTER

These identifiers are PLAN-LOCAL. They are not Appendix A Decision Register ids (D1..D112) and never will be.
Every closure is written as a decision record under records/decisions/ using the Section 97.2 schema
(id, decider, prompt_received, decided, subject, options_considered, evidence, review_date).
Every open prompt lives under records/decisions/pending/ and is drained at the midweek decision window (D79).
Status values: OPEN | CLOSED | DECLINED. DECLINED carries the gate answers and a review date (Section 98.1).
```

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p docs/decisions
cat > docs/decisions/L0-decision-register.md << 'EOF'
# L0 DECISION REGISTER

These identifiers are PLAN-LOCAL. They are not Appendix A Decision Register ids (D1..D112) and never will be.
Every closure is written as a decision record under records/decisions/ using the Section 97.2 schema
(id, decider, prompt_received, decided, subject, options_considered, evidence, review_date).
Every open prompt lives under records/decisions/pending/ and is drained at the midweek decision window (D79).
Status values: OPEN | CLOSED | DECLINED. DECLINED carries the gate answers and a review date (Section 98.1).

## 4. The seven design-open items — reserved to L0, all of them

§99.3 names exactly seven matters the implementer must still invent. Each is assigned a plan-local decision id
below. These ids are **plan-local, not Appendix A Decision Register ids** — they never collide with `D1…D112`.

| Plan id | §99.3 item | The open matter | Closed no later than |
|---|---|---|---|
| **L0D-10** | 1 | The attention classifier and constraint diagnosis algorithm — Healthy / Watch / Action Required with the reason on the same line, and "which constraint binds" | Phase G3 (§98.5) |
| **L0D-11** | 2 | The `make parity` declaration format — the environment-schema format compared across local, staging and production, defined once and reused | Phase 4 (§98.2), because Phase 4's completion check runs `make parity` |
| **L0D-12** | 3 | Plan-checker internals — every assumed capability verified against the exact pinned GSD release, and the in-house build budgeted if verification fails | Phase 7 (§98.2); the verification itself is a Phase 1 item (§99.6 risk 4) |
| **L0D-13** | 4 | DevLake field coverage — which metrics need bespoke computation beyond DevLake's models (routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread) | Before Phase G3 (§98.5 states G3 depends on confirmed coverage) |
| **L0D-14** | 5 | Machine sources for context checks — where the computable boundary is drawn across the fifteen systemic context checks of §80, with the humans named in §80.2 classifying the rest | Phase P4 (§98.6) |
| **L0D-15** | 6 | KPI instrumentation projects — scoping each §79 row marked "available after instrumentation" as its own mini-project | Phase P2 (§98.6) |
| **L0D-16** | 7 | Calibration methods — PLU fit, forecast scoring, sustainable-utilisation bands, the §97.4 attention-session parameters, the §72.3 confidence table | Quarterly refits; first method recorded at Phase G5 (§98.5) |

Until an item is closed, **no lane may build anything whose behaviour depends on it.** A lane that reaches such a
dependency files a blocker (§7.1) naming the L0D id.

## 5. The L0-only decision register — what only L0 may decide

Plan-local ids. Every closure is written as a decision record under `records/decisions/` using the §97.2 schema,
and every open prompt as a record under `records/decisions/pending/` via the record-decision CLI (§97.2).

### 5.1 Contracts and schemas

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-01 | The shape of every registry, product, record and event schema, and its direct transcription to JSON Schema | §7, §8, §15, §97.2 |
| L0D-02 | `contract_version` policy: what constitutes a breaking change, the supported-version window, deprecation deadlines | §60, invariant 73 |
| L0D-03 | `record_schema_version` and `event_schema_version` handling; the binding event envelope field list | §97.2, §97.3 |
| L0D-17 | Every value marked **calibrated configuration** and its stated initial value — including "sustained" (initial 6 consecutive weeks, SIG-07/SIG-08/SIG-30), the bootstrap-log staleness window (initial 7 days, §95.4), the triage budget (initial 5 minutes per product per pass, §94.3), the AI-eval triage block (initial 30 minutes, §94.3), the SIG-42 regression tolerance (initial 5 percentage points, §52.2), the §29.5 scope-growth threshold | §84.6, AT-074, D102 |

### 5.2 Partition, ownership and access

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-04 | The path→lane map and residual ownership; any extension of `lane-paths.tsv` | PARTITION.md rule 1 |
| L0D-05 | Any `CODEOWNERS` edit; the rule that CODEOWNERS carries human identities only | §98.2 Phase 1 completion check |
| L0D-18 | Fail-closed versus fail-open classification of every control | §64, invariant 80 |
| L0D-25 | Secrets-tier assignment and credential scope, including the records-writer's `contents: write` scope and the reconciler's declared repair scope | §40.1, §26.4, D89, invariant 25 |
| L0D-26 | Anything touching subsystem L / Layer B datasource separation — the second Founder-only Grafana instance, the separately-credentialed people datasource | §90.3, §92.8, D75, invariants 106 and 109 |

### 5.3 Merge train and release

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-06 | Approving or denying a Contract Change Request | PARTITION.md rule 2 |
| L0D-07 | Any deviation from the fixed merge order `L1 → L4 → L2 → L3 → L5` | PARTITION.md §"Branch & merge model" |
| L0D-08 | Revert versus roll-forward when `integration` breaks | §28, invariant 27 |
| L0D-09 | Promotion `integration → main` | PARTITION.md §"Branch & merge model" |

### 5.4 Programme governance

| Plan id | Reserved decision | Spec anchor |
|---|---|---|
| L0D-19 | Opening and closing every bootstrap exception, with expiry, owner and deactivation trigger | §95, §54.2, invariant 77, SIG-39 |
| L0D-20 | Declaring a phase `declined` — a recorded decision carrying the gate answers, the forgone capabilities and a review date | §98.1 |
| L0D-21 | Releasing the P0-before-P2 lock (only a `declined` P0 releases it; an unbuilt P0 holds it) | §98.1 |
| L0D-22 | The drift-budget tolerances and headline thresholds in `os-health.yaml`, and each signal's `activation_dependency` and `lookback_window` | §52.1, §52.2 (D77), §53.4 |
| L0D-23 | The enforcement classification — mechanical / policy / review-held — of each of the 111 invariants | §101 preamble, authored at Phase G2 |
| L0D-24 | Accepting a risk or recording a plan-tier fallback (branch protection on private repos requires the Team plan; environment required reviewers are Enterprise-only and are not depended on) | §99.5, §99.6 risk 5, D73, D80 |
EOF
git add docs/decisions
git commit -m "L0-00-06: L0 decision register L0D-01..L0D-26"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | All 26 ids present | `for n in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26; do grep -q "L0D-$n" docs/decisions/L0-decision-register.md \|\| echo "MISSING L0D-$n"; done` | no output |
| 2 | All seven §99.3 items mapped to L0D-10..L0D-16 | `grep -c 'L0D-1[0-6]' docs/decisions/L0-decision-register.md` | a number `>= 7` |
| 3 | The plan-local disclaimer is present | `grep -c 'PLAN-LOCAL' docs/decisions/L0-decision-register.md` | `1` |
| 4 | No invented spec id | `grep -oE '\bD[0-9]{1,3}\b' docs/decisions/L0-decision-register.md \| sort -u \| tr '\n' ' '` | only ids that appear in the spec's Appendix A |
| 5 | Every entry names a spec anchor | `awk -F'\|' '/L0D-/ && $0 ~ /^\|/ && $NF !~ /§|Section|invariant|PARTITION/' docs/decisions/L0-decision-register.md \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
miss=$(for n in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26; do
  grep -q "L0D-$n" docs/decisions/L0-decision-register.md || echo x; done | wc -l | tr -d ' ')
printf 'missing=%s designopen=%s disclaimer=%s\n' "$miss" \
  "$(grep -c 'L0D-1[0-6]' docs/decisions/L0-decision-register.md)" \
  "$(grep -c 'PLAN-LOCAL' docs/decisions/L0-decision-register.md)"
```

Expected output:

```
missing=0 designopen=7 disclaimer=1
```

(`designopen` may exceed 7 if the ids are cross-referenced elsewhere in the file; it must never be below 7.)

**STOP rule** — if criterion 4 surfaces a `Dnn` that does not appear in the spec's Appendix A, an id has been
invented. Delete it. Do not "correct" it to a nearby number: cite the real decision or cite none.

---

### L0-00-07 — Publish the cadence checklist

**Size:** S · **Dependencies:** L0-00-02

Create `docs/cadence/L0-cadence.md` containing §8.1, §8.2 and §8.3 of this charter verbatim.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p docs/cadence
cat > docs/cadence/L0-cadence.md << 'EOF'
# L0 CADENCE

## 8.1 Daily — the integrator's day

Grounded in the day model of §94.2 and the Team Lead priority model of §94.5. During the build the human lead
holds both the Founder and Team Lead surfaces (§98.7: "the Founder solo under Bootstrap Mode").

| Time | L0 activity | Output |
|---|---|---|
| 09:30 | Blocker sweep. Read every open `blocker` issue opened since the last sweep | Each answered, or converted to an L0D decision and dated |
| 09:45 | `integration` health: `make lane-guard` across every lane branch pushed overnight | Green list; any red branch is told to stop |
| 10:00 | Drift and orphan alerts on the control-plane repository itself — SIG-03 permission drift, SIG-05 orphan risk, SIG-13 failed reconciliations | Blocking-class items actioned before anything else |
| 10:30 | **Contract-freeze integrity check**: `make promote-check` sub-step verifying `contracts.sha256` still matches | `CONTRACTS-FROZEN OK` |
| 10:30–13:00 | Heavy block (§94.2). L0 authoring: contracts, docs, decision records | The day's L0 deliverable |
| 14:00 | Window-tight block: lane PR review — partition compliance and contract conformance only, never style | Approvals or change requests |
| 16:30 | Second blocker sweep | Same-day close on everything opened before 16:00 |
| 17:00 | **Contract window** — the only time `contracts/**` is edited, and only under an approved CCR | Re-freeze + decision record |
| 17:30 | End-of-day readiness check (§94.5 priority 10), adapted to the build: every lane has an unblocked next task; no unactioned Blocking-class drift; no blocker older than one working day; no lane branch older than one day unrebased | Actioned or explicitly carried over with a recorded reason |

**Only these interrupt L0** (§94.5, adapted): a blocker issue, a CCR, Blocking-class drift, a red `integration`,
and a lane branch that has touched a foreign path. Routine lane PR notifications do not.

## 8.2 Weekly — the integrator's week

| When | L0 activity | Anchor |
|---|---|---|
| Monday 09:30 | Portfolio review of the build: phase position per lane, P0-before-P2 lock status, every open L0D | §94.8 |
| Monday 10:00 | Which constraint binds this week — which lane is the bottleneck, and whether it is a contract gap or a capacity gap | §94.6 |
| Monday 14:00 | Verification sequence for the week — which acceptance tests of §100 become provable this week | §94.8 |
| **Wednesday** | **MERGE TRAIN** — the weekly cycle, run in the fixed order (§9) | PARTITION.md |
| Midweek, default Thursday | Standing decision window, thirty minutes: every open L0D prompt actioned, deferred with a date, or explicitly declined | §94.6, D79 |
| Friday 15:00 | Freeze: no promotion `integration → main` after this point in the week | §94.8 |
| Friday 16:30 | Weekly banded attention self-report, five minutes | §94.8, §97.4 |
| Friday 17:00 | **Weekly bootstrap log entry** under `records/bootstrap-log/` — the fixed three-field template: gates stubbed and armed; bootstrap exceptions opened and closed; phase completion checks run and their results. Two of the three fields are generator-filled; L0 writes the judgment lines | §95.4, §94.8 |
| Friday 17:15 | Next week's lane queue refilled — every lane has a Ready task with satisfied dependencies | §94.5 priority 6 |

The bootstrap-log entry is not optional and has a detector: control-plane CI raises **Blocking** drift when the
newest entry is older than the calibrated staleness window, initial value 7 days (§95.4, L0D-17).

## 8.3 Monthly and quarterly

| Cadence | L0 activity | Anchor |
|---|---|---|
| Monthly | Dependency, Scorecard, cost-band and asset-expiry sweep across the two repositories | §94.8 |
| Monthly | Judgment-capture ritual, 15 minutes: the month's classification and routing judgment calls recorded so they feed Coordination attention and calibration | §94.8 |
| Quarterly, month 1 | Operating-system review from the generated review pack — retires at least one policy, one metric or one automation, or records why nothing warranted retirement (AT-045) | §94.8, §98.5 G8 |
| Quarterly, month 2 | Escrow seal audit and its functional verification | §94.8, §14.4 |
| Quarterly, month 3 | Control-plane disaster-recovery drill | §94.8 |

Quarterly rituals are staggered, not stacked; the month assignments above are the spec's stated initial values and
are recalibrated only by the ritual attention-hours budget line of §57.2 (L0D-17).
EOF
git add docs/cadence
git commit -m "L0-00-07: integrator daily and weekly cadence"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | File exists | `test -f docs/cadence/L0-cadence.md && echo PRESENT` | `PRESENT` |
| 2 | Both blocker sweeps named | `grep -c '09:30\|16:30' docs/cadence/L0-cadence.md` | a number `>= 2` |
| 3 | The Friday bootstrap-log entry is named with its path | `grep -c 'records/bootstrap-log/' docs/cadence/L0-cadence.md` | `1` |
| 4 | The merge-train day is named | `grep -c 'MERGE TRAIN' docs/cadence/L0-cadence.md` | `1` |
| 5 | The midweek decision window is named | `grep -c 'Thursday' docs/cadence/L0-cadence.md` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'file=%s sweeps=%s bootstraplog=%s train=%s window=%s\n' \
  "$(test -f docs/cadence/L0-cadence.md && echo PRESENT || echo MISSING)" \
  "$(grep -c '09:30\|16:30' docs/cadence/L0-cadence.md)" \
  "$(grep -c 'records/bootstrap-log/' docs/cadence/L0-cadence.md)" \
  "$(grep -c 'MERGE TRAIN' docs/cadence/L0-cadence.md)" \
  "$(grep -c 'Thursday' docs/cadence/L0-cadence.md)"
```

Expected output:

```
file=PRESENT sweeps=2 bootstraplog=1 train=1 window=1
```

(`sweeps` may be higher than 2 if a time appears in more than one row; it must never be below 2.)

**STOP rule** — if the bootstrap-log row is absent, stop. §95.4 gives that entry a Blocking-drift detector at a
7-day staleness window; a cadence that does not schedule it guarantees the detector fires. Re-copy §8.2 verbatim.

---

### L0-00-08 — Publish the merge-train runbook

**Size:** M · **Dependencies:** L0-00-04, L0-00-07

Create `docs/merge-train.md` containing §9 of this charter verbatim, plus a cycle log table with the columns
`cycle | date | L1 | L4 | L2 | L3 | L5 | promoted | notes`, where each lane cell is `MERGED`, `SKIPPED` or `NONE`.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
# author docs/merge-train.md as described above, then:
git add docs/merge-train.md
git commit -m "L0-00-08: merge-train runbook and cycle log"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Runbook exists | `test -f docs/merge-train.md && echo PRESENT` | `PRESENT` |
| 2 | The frozen order appears exactly as PARTITION.md states it | `grep -c 'L1 → L4 → L2 → L3 → L5\|L1 -> L4 -> L2 -> L3 -> L5' docs/merge-train.md` | a number `>= 1` |
| 3 | The five per-lane steps are enumerated | `grep -c 'lane-guard\|SELF-VERIFY\|--no-ff\|rebased' docs/merge-train.md` | a number `>= 4` |
| 4 | The Friday 15:00 promotion cut-off is stated | `grep -c 'Friday 15:00' docs/merge-train.md` | `1` |
| 5 | Cycle log header present | `grep -c 'cycle | date | L1 | L4 | L2 | L3 | L5' docs/merge-train.md` | `1` |
| 6 | `make train` agrees with the runbook | `make train \| head -1 \| grep -c 'L1 -> L4 -> L2 -> L3 -> L5'` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'file=%s order=%s cutoff=%s maketrain=%s\n' \
  "$(test -f docs/merge-train.md && echo PRESENT || echo MISSING)" \
  "$(grep -c 'L1 → L4 → L2 → L3 → L5\|L1 -> L4 -> L2 -> L3 -> L5' docs/merge-train.md)" \
  "$(grep -c 'Friday 15:00' docs/merge-train.md)" \
  "$(make train | head -1 | grep -c 'L1 -> L4 -> L2 -> L3 -> L5')"
```

Expected output:

```
file=PRESENT order=1 cutoff=1 maketrain=1
```

**STOP rule** — if the order in the runbook differs from PARTITION.md in any respect, stop and correct the
runbook, never the partition. The order is dependency order and reordering it silently reintroduces the
cross-lane build failures the partition removes.

---

### L0-00-09 — Rehearse the merge train on empty lane branches

**Size:** M · **Dependencies:** L0-00-04, L0-00-08

The rehearsal proves the gate before any lane has produced anything worth losing.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only

for n in 1 4 2 3 5; do
  git checkout -B "lane/$n/rehearsal" integration
  case "$n" in
    1) d=registries ;;
    2) d=templates/workflows ;;
    3) d=reconciler ;;
    4) d=metrics ;;
    5) d=notify ;;
  esac
  mkdir -p "$d" && printf 'rehearsal: lane-%s\n' "$n" > "$d/.rehearsal.yaml"
  git add -A && git commit -q -m "lane $n rehearsal"
  echo "--- lane $n ---"
  ./lane-guard.sh "$n" integration "lane/$n/rehearsal" | tail -1
done

git checkout integration
for n in 1 4 2 3 5; do
  git merge --no-ff -m "merge-train rehearsal: lane/$n" "lane/$n/rehearsal"
done
git log --oneline --merges -5
```

Cleanup after the rehearsal passes:

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration
git reset --hard origin/integration
for n in 1 2 3 4 5; do git branch -D "lane/$n/rehearsal"; done
git status --porcelain | wc -l
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Every lane branch passes its own guard | the loop above | five lines, each `LANE-GUARD OK` |
| 2 | All five merges apply with zero conflicts | `git log --oneline --merges \| head -5 \| wc -l` | `5` |
| 3 | No merge conflict occurred | `git ls-files -u \| wc -l` | `0` |
| 4 | A cross-lane guard call still fails | `./lane-guard.sh 1 integration lane/3/rehearsal \| tail -1` | `LANE-GUARD FAIL: 1 violation(s)` |
| 5 | Working tree clean after cleanup | `git status --porcelain \| wc -l` | `0` |

**SELF-VERIFY** (run before cleanup)

```bash
set -euo pipefail
cd "$CP_ROOT"
ok=$(for n in 1 4 2 3 5; do ./lane-guard.sh "$n" integration "lane/$n/rehearsal" | tail -1; done | grep -c 'LANE-GUARD OK')
printf 'guards_ok=%s merges=%s conflicts=%s cross_lane=[%s]\n' \
  "$ok" \
  "$(git log --oneline --merges | head -5 | wc -l | tr -d ' ')" \
  "$(git ls-files -u | wc -l | tr -d ' ')" \
  "$(./lane-guard.sh 1 integration lane/3/rehearsal | tail -1)"
```

Expected output, exactly:

```
guards_ok=5 merges=5 conflicts=0 cross_lane=[LANE-GUARD FAIL: 1 violation(s)]
```

**STOP rule** — if `conflicts` is non-zero, two lanes have written the same path and the partition is violated
somewhere the map does not see. **Do not resolve the conflict.** Resolving it hides the violation and normalises
exactly the shared-mutable-file pattern PARTITION.md rule 3 forbids. Open
`BLOCKER L0-00-09: rehearsal merge conflict on <path>` and fix `lane-paths.tsv` under L0D-04 first.
If `cross_lane` prints `LANE-GUARD OK`, the guard is broken and no lane may start (same STOP as L0-00-04).

---

## 11. Dependency graph of this file's tasks

```
L0-00-01  (branches + CODEOWNERS)
   └── L0-00-02  (publish charter + partition)
          ├── L0-00-03  (lane-paths.tsv)
          │      └── L0-00-04  (lane-guard.sh + Makefile)
          │             ├── L0-00-08  (merge-train runbook)   ← also needs T07
          │             └── L0-00-09  (rehearsal)             ← also needs T08
          ├── L0-00-05  (escalation templates)
          ├── L0-00-06  (decision register)
          └── L0-00-07  (cadence checklist)
```

**Gate:** no lane branch is created until L0-00-09 passes its SELF-VERIFY, and no lane task is dispatched until
the Phase 0 contract freeze has recorded `contracts.sha256` (`make freeze`).

---

## 12. Standing reminders the integrator does not get to forget

1. **A contract change is never a code change.** It is a CCR, a decision record, a re-freeze, and a re-run of every
   lane's SELF-VERIFY. Contracts are frozen for a reason (PARTITION.md rule 2).
2. **Detect before repair.** Auto-repair is the riskiest code in the system; it ships only after detection has run
   clean for weeks, one repair class at a time, stricter-only, enforced in code and tested (§98.3, §99.6 risk 6,
   invariant 81, AT-033, AT-102).
3. **A required check that nothing emits blocks every pull request indefinitely; an empty list is a gate that
   reads armed and is not.** The required-status-check list starts empty per repository and each phase names the
   contexts it adds (§98.2, Phase 1).
4. **Stubbed gates stay stubbed.** Every relaxation is an `exceptions.yaml` entry with expiry, owner and
   deactivation trigger, or it does not exist (§95, §54.2, invariant 77, SIG-39, AT-039).
5. **Declined is a state, not an absence.** A phase that fails its gate is recorded `declined` with the gate
   answers, the forgone capabilities and a review date — and only a declined P0 releases the P0-before-P2 lock
   (§98.1, L0D-20, L0D-21).
6. **The record stores live in their own repository, and no machine bypass actor exists on `control-plane`**
   (D89, D107, §40.1). Nothing a lane asks for changes that.
7. **Extensibility is the acceptance criterion.** No dashboard, workflow or script contains a product list, and no
   person is hard-coded into architecture logic (AT-001, AT-002, invariants 51 and 52). Reject any lane PR that
   introduces one, regardless of how convenient it is.
8. **The layered removal test is real.** The delivery core runs with the governance artifacts removed, and removing
   any named external tool changes nothing in the operating model (AT-031, AT-034). Build so this stays true.
