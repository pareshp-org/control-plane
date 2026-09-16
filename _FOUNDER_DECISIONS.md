# FOUNDER DECISIONS â€” the closed register

Decisions the founder has answered directly. This file is **additive and authoritative**: where a plan
document disagrees with a row here, the row here wins and the document is to be corrected in the next
reconciliation sweep.

Format follows `lanes/L0-04-decisions-register.md` Â§4: a decision is closed by a dated record, and the
register row then points at it. Until `records/decisions/` exists (it requires the control-plane repo,
which does not yet exist), this file is that record.

---

## FD-001 â€” The identity of L0

**Decided:** 2026-09-02
**Question:** Is L0, the Integrator, the Founder or Nimesh (Team Lead)?
**Answer:** **The Founder is L0.**

**Why this needed deciding.** L0 is the one role in the plan whose executor is a human rather than an AI
developer (`lanes/L0-00-charter.md` Â§"Executor"). It holds four absolute authorities â€” `contracts/**`,
the partition, the merge train, and every design-open item of spec Â§99.3 â€” and it is the sole closer of
all 60 entries in the decision register. `PARTITION.md` says only "L0 Integrator (human/lead)"; elsewhere
L0 decisions are called "decisions the user must make". **Nothing in the 172,259-line plan decided it**,
and it is not a registered `REG-` entry â€” the gap was found by the fresh-reader dry-run, not by the plan
itself. It determines who sits on the critical path for every contract, every merge and every decision.

**Consequences that follow from this answer, and must be reflected in the plan:**

1. Every `DECISION REQUIRED`, `ASSISTED` task and merge-train step resolves to the Founder. There are
   508 occurrences of `DECISION REQUIRED` / `L0 decides` / `L0 must decide` across the corpus, 29 files
   containing ASSISTED tasks, and 23 Phase-0 tasks (`L0-P0-001`â€¦`023`) that gate all five lanes.
2. `master/04-phase-map.md` records that **all five lanes are idle by construction until `L0-P0-023`
   completes**. That serialisation now sits on the Founder's calendar.
3. Nimesh (Team Lead) is therefore **not** the integrator. Any plan text implying the Team Lead performs
   L0 duties is a defect to be corrected.
4. `cross/10-l0-load.md` â€” the L0 critical-path sweep, running at the time of this decision â€” must be
   read against this answer: its hour estimates are estimates of **the Founder's** hours.

**Open follow-on, not decided here:** whether any L0 duty may be delegated, and to whom. Spec **D108**
(the founder-decision delegate cannot carry a formal people decision) and **D109** (Layer B access is
not delegable) already constrain this. Raise as a new register entry if delegation is wanted.

---

## FD-002 â€” REG-001 Â· Subsystems G, H, J, O and P

**Decided:** 2026-09-02 Â· **Band:** P0 Â· **Gates:** Ph0
**Answer:** **Option B â€” extend existing lanes by path.** Specifically:

| Subsystem | Assignment | Reason |
|---|---|---|
| **H** dashboards and views | **L5** | Grafana runs on the ops VM, which L5 owns (`ops-vm/**`, `infra/**`). D75 and Â§99.5's Layer B split require the Founder-only instance's provisioning to live in a path that lane owns, with `AT-097` executable against it â€” `AT-097` verifies the people datasource is absent from the shared instance's *provisioned configuration*. That is L5 work. |
| **O** governance registries | **L1** | Registry-shaped. L1 already owns `registries/**`. Covers `policies.yaml`, `exceptions.yaml` and the other registry files. |
| **O** governance jobs | **L3** | Reconciliation-shaped. Exception expiry, the pattern detector, the learning-loop tracker and the change-budget counters are reconciler work, and L3 owns `reconciler/**`. Splitting O by shape is legal because the two halves are different paths â€” PARTITION rule 1 forbids one *path* having two owners, not one subsystem. |
| **J** background machine layer | **Deferred** | Already hard-gated behind Phase 3's own CPU benchmark (Â§98.2). A failed benchmark parks the subsystem; deferring changes nothing that was not already gated. |
| **G** plan-checker, Gate 1 tooling | **L0 (the Founder)** | Forced. Â§99.3 item 3 makes plan-checker internals design-open in the specification, and the AI-developer profile forbids a task requiring design. Not delegable to any lane under any option. |
| **P** people intelligence engine | **L0 (the Founder)** | Forced. Â§99.3 item 1 (the attention classifier) is design-open. Â§99.4 item 9 defers P from V1 outright. |

**Chosen over Option A** (hold all five with L0) because the Founder is L0 (FD-001), and A would make the Founder
the critical path from mid-programme â€” the single largest structural risk in the plan, and the one
`cross/10-l0-load.md` is measuring. B moves the two subsystems that *cannot* wait (H, because Â§99.4 item 7 puts
Founder view v0 inside V1; O, because the exception registry with auto-expiry is a Phase 1 completion-check
artifact) onto lanes that are already building adjacent things.

**Cost of this answer.** One explicit, versioned re-freeze of `PARTITION.md`, applied in a single commit together
with `lane-paths.tsv` and `CODEOWNERS`. `master/04` is explicit that this change *"must be made once, explicitly,
and versioned â€” not drifted into"*.

**Settles the raiser disagreements** recorded in the register: O â†’ L1 **not** L3 for the registry half
(`DEC-01` 2 wins over `LA-01` a, which is instead applied to the jobs half); H â†’ L5 **not** L4
(`D-PLAN-01` B and `V1-D2` a win over `D-PLAN-01` A and `DEC-01` 2).

**Supersedes:** `D-PLAN-01`, `D-PLAN-02`, `LA-01`, `D-REQ-4`, `DECISION 1`, `D-EE-2`, `V1-D1`, `V1-D2`, `DEC-01`,
`L1-00` DR #2, `L0-IG-D3`, `L0-IG-D4`, `D-L2-12`, `D-L4-P4-04`, `D-L4-P5-03`, `DR-L0-07-F`, `protocol/02` Â§2.

---

## FD-003 â€” REG-002 Â· The lane-guard circularity

> ## âš ï¸ SUPERSEDED â€” RE-DECISION REQUIRED. Do not execute the answer below.
>
> **Recorded 2026-09-02, withdrawn the same day.** The recommendation that produced this record rested on
> a premise that two plan documents falsify. Option D requires L0 to place the frozen workflow file into
> `.github/workflows/` once, in Phase 0. **L0 may not write to that path at all:**
>
> - `lanes/L0-00-charter.md:53` â€” *"`.github/workflows/**` belongs to L2 and **L0 never writes there**."*
> - `lanes/L0-01-phase-0-contracts.md:31`, **D-L0-05** â€” *"The **lane-guard CI check is not an L0 artifact.**
>   `.github/workflows/**` belongs to L2 (PARTITION.md, line 18) and **L0 may not write there.**"*
>
> Option D is therefore **not executable under the frozen partition**, and the byte-compare it depends on
> has no way to be placed. The register's own conflict table also understates the problem: **six**
> documents state binding positions on this, not four â€” `L0-00` Â§2.1 and `L0-01` D-L0-05 are the two it
> omits, and they are the two that decide it.
>
> **The corrected option set is A + E** (see the analysis below the withdrawn text). Option A â€” a named-file
> carve-out moving exactly one file to L0 â€” works precisely *because* it amends the ownership that D-L0-05
> assumes, rather than trying to act inside it.
>
> **A further fact this surfaced, which changes what Phase 0 delivers.** D-L0-05 records that Phase 0 as
> written enforces the partition with only two mechanisms L0 actually owns â€” **CODEOWNERS review on
> `contracts/**`, and the immutable freeze tag** â€” and that the lane-guard workflow is **L2's first
> obligation in cycle 1**. Until it exists, *"the merge train is guarded by Code Owner review alone, and
> that is a recorded, dated gap"* (`L0-P0-022`). So the plan already ships a deliberate, documented window
> in which the control behind PARTITION rule 1 is not running. Whichever option is chosen must say how long
> that window is and what closes it.

### âœ… RE-DECIDED 2026-09-02 â€” **Options A + E**

**A â€” named-file carve-out.** One exact rule in `lane-paths.tsv` giving **L0** ownership of
`.github/workflows/lane-guard.yml`, ordered **before** L2's prefix rule (exact rules beat prefix rules),
plus the matching `CODEOWNERS` line. This removes L2's write on the guard file outright, rather than
freezing bytes L2 can still reach. It works *because* it amends the ownership `D-L0-05` assumes, instead of
trying to act inside it. Already accepted by `master/03` Â§9, whose rule count reads *"25 if D-REQ-3 Option A"*.

**E â€” cycle-1 replay,** unchanged and still correct. The lane-guard *check* is `contracts/gate/lane-guard.sh`
(L0-owned, present at BT-0). Cycle 1's L1 and L4 merges are gated by L0's local `make gate-lane` run, and
`IG-08` replays the guard over the whole merged range at the first integration gate. Unguarded merges are
**re-checked, not forgiven**.

**Cost of being wrong: two lines, reverted in two lines.**

**Consequential edits.**
1. `lane-paths.tsv`: add `0<TAB>.github/workflows/lane-guard.yml` **above** `2<TAB>.github/workflows/*`.
2. `CODEOWNERS`: add the matching exact-file line above `/.github/workflows/`, which currently routes to
   `@LANE2_REVIEWER` at `lanes/L0-00-charter.md:390`.
3. Every ownership-matching command in the set must honour exact-before-prefix precedence. `L0-00-T03`'s
   `lane-paths.tsv` generator and the guard's `R0c` lane derivation both need checking for this.
4. Correct `lanes/L0-00-charter.md:53` (*"L0 never writes there"*) and `lanes/L0-01` `D-L0-05`
   (*"the lane-guard CI check is not an L0 artifact"*) â€” both are now false for exactly one file, and both
   are cited elsewhere as authority.
5. Correct the register's conflict table: **six** documents state binding positions on REG-002, not four.
   The two it omits â€” `L0-00` Â§2.1 and `L0-01` `D-L0-05` â€” are the two that decide it.

**Superseded by this record:** `master/07` Â§7 `DEC-02`'s *"option 3 in force"*; `lanes/L0-02` Â§4
`L0D-LG-1..3`'s content-freeze resolution; `protocol/10` Â§2.1's *"binding option (b)"* as to **ownership**
(its replay mechanism survives as E). `protocol/10` Â§2 mechanism 2's blanket claim that CODEOWNERS routes
all of `.github/workflows/**` to L0 remains **wrong** â€” it routes exactly one file.

**Still to be answered inside this decision** (`D-L0-05`, `L0-P0-022`): the plan ships a deliberate,
documented window in which the guard does not run â€” *"the merge train is guarded by Code Owner review alone,
and that is a recorded, dated gap"*. Under A + E that window shrinks to cycle 1 only, and E's local run plus
the `IG-08` replay is what closes it. State the window's length explicitly in the decision record.

---

**Withdrawn answer (retained for the record):** Options D + E together.

- **D â€” content freeze.** The workflow body is an L0 contract at `contracts/ci/lane-guard.yml.frozen`. The
  location stays L2-owned, but the file is classified `GUARD-CRITICAL` and byte-compared against the contract
  **before every other check** on every pull request. L0 places it once, on `integration`, in Phase 0, before any
  lane branch exists.
- **E â€” cycle-1 replay.** The lane-guard *check* is `contracts/gate/lane-guard.sh`, L0-owned and present at BT-0.
  Cycle 1's L1 and L4 merges are gated by L0's local `make gate-lane` run, and `IG-08` replays the guard over the
  whole merged range at the first integration gate. Unguarded merges are **re-checked, not forgiven**.

**Why both.** D answers *who owns the bytes*; E answers *what gates cycle 1*, which D does not touch. The register
states E is compatible with A, C or D. Together they answer all four things the register requires a complete
answer to state.

**Why not B** (a separate L0-controlled guard repository), which is the most literal reading of Â§53.1
(*"no control that can be rewritten by the credential it is checking is a control"*): D satisfies Â§53.1 in
substance â€” L2 may edit the file, but an L0-owned byte-compare running first rejects the edit â€” while B adds a
repository `PARTITION.md` does not list (`L0D-24`) and a second credential surface. Reversible to B later if the
byte-compare proves unreliable.

**Preserves the frozen partition unamended.** L2 still owns `.github/workflows/**` and simply may not edit one
file inside it, exactly as it may not edit `contracts/**`.

**This decision record explicitly supersedes three documents that each claim to be binding today:**

| Document | Claim | Status after this record |
|---|---|---|
| `master/07` Â§7 `DEC-02` | *"option 3 is in force as the interim control"* | **Superseded** |
| `protocol/10` Â§2.1 | *"D-L2-06 is resolved here â€” option (b) â€¦ Resolution, binding"* | **Superseded as to ownership; its replay mechanism is adopted as E** |
| `lanes/L0-02` Â§4 `L0D-LG-1..3` | *"claimed resolved"* | **Ratified** â€” this is option D |

**Also settles the fifth disagreement:** `protocol/10` Â§2 mechanism 2 asserts CODEOWNERS routes
`.github/workflows/**` to L0, while the CODEOWNERS body written by `L0-00-T01` routes it to `@LANE2_REVIEWER`.
**The CODEOWNERS body is correct** â€” L2 owns the path; the byte-compare, not CODEOWNERS, is what protects the
guard. `protocol/10` Â§2 mechanism 2 is to be corrected.

---

## FD-004 â€” The index-vs-phase-file task-id namespace fork (unregistered)

**Decided:** 2026-09-02 Â· **Band:** effectively P0 â€” all six lane coherence reviews return `BLOCKED â€” DO NOT DISPATCH` on it
**Answer:** **Publish a concordance.** One mapping file per lane: index id â†’ body-bearing phase-file id.

**The problem.** Every lane except L0 carries two peer decompositions of itself, with disjoint id namespaces and
no concordance in either direction: L1-05 (61 index ids vs 67 phase ids across 5 schemes), L3-06 (78 vs 115),
L4-06 (117 vs 91), L5-06 (59 vs 97). `L4-06-tasks.md` is the acute case â€” 674 lines of index and acceptance
criteria with **zero** task bodies, while ~91 bodies live in L4-02/03/04/05/07 under at least eight disjoint
namespaces (`L4-T`, `L4-P1-T`, `L4-P5-`, `L4-P7-T`, â€¦).

**Why a concordance rather than reissuing the indexes.** It is additive: it edits no existing task file, leaves
both decompositions valid, and preserves every citation to the index ids that already exists across 91 files.
Reissuing would rewrite the four most-reviewed artifacts in the plan and invalidate every such citation â€” a large
re-verification pass stacked on top of 1,037 already-open defects.

**Generate it mechanically, then check it by hand.** The honest residue is the point: for L4, roughly 26 of the
117 index ids are expected to map to nothing. **That residue is the true list of unbuilt L4 work** â€” which is
what the earlier "write 94 missing bodies" instruction got wrong, and would have caused ~91 duplicate bodies.

> **Standing instruction: do NOT write task bodies into `L4-06-tasks.md`.** The bodies mostly exist elsewhere
> under other names. Only the residue the concordance exposes may be authored, and only after it is confirmed.

---

## FD-005 â€” REG-003 Â· The implementation toolchain

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0
**Answer:** **Option A â€” Python 3.12**, with `jsonschema`, `check-jsonschema`, `PyYAML` and `pytest`, pinned by
exact `==`, no lockfile generator. Recorded once in `contracts/**` before the freeze.

**Why.** Already the recommendation of `master/05`. Four lane files assume 3.12 (`L2-05`, `L3-04`, `L3-06`,
`L4-06`) against two assuming 3.11 (`L1-05`, `L1-03`), so it reissues the fewest documents. One runtime serves
validators, reconciler, provisioning CLI and metrics jobs, and matches the ops-VM job substrate (Â§99.2 subsystem
M). Node would put a second runtime on the operations VM. Â§101 invariant 85 requires third-party dependencies
pinned; exact `==` satisfies it without a lockfile generator the plan does not otherwise use.

**Consequence.** `lanes/L1-05-tasks.md` and `lanes/L1-03-validators.md` must be reissued from 3.11 to 3.12, and
`master/08` Â§2.3's worked ledger entry (`npx --yes ajv-cli@5.0.0`) corrected off Node. Each of those files
carries a STOP rule naming exactly this; the reissue is expected, not an error.

**Verify before the freeze:** confirm nothing on the intended operations VM or in a product toolchain pins Python
3.11. If something does, this answer flips to 3.11 at a cost of reissuing two L1 files instead of four.

---

## FD-006 â€” REG-009 Â· The GitHub organisation login

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0 (an entry criterion, not a phase deliverable)
**Answer:** **The Founder will supply the literal login.** It is a fact to be recorded, not a choice â€”
the register lists exactly one option: record it in `contracts/estate.yaml`, key `org`.

**Status: AWAITING VALUE.** Until supplied, every task named below STOPs. There is no safe default
(`lanes/L4-01`).

**Verified facts that bear on the value.** The `gh` CLI is authenticated as `PerpetualSolution` and
`pbhayashri`; `gh api user/orgs` returns nothing â€” **no organisation exists yet**, so this login must be
created, not selected. `manual/05-git-workflow.md` hard-codes `lumiverse-ops` in 8 places (lines 19, 66, 91,
95, 252, 634, 649, 656); the founder has **not** adopted it, so those 8 references are a defect to be
corrected to whatever value is recorded here. `L0-P0-001`'s STOP rule forbids creating the repositories
under a personal account.

**Blocks.** L4 every task in `L4-01-records-repo.md`; L5 `access/**` and `infra/**`; L3 `tools/provision/**`
live runs; L0 `L0-00-T01`.

**Two adjacent facts must be recorded in the same decision** (`master/04` DECISION 5), and are also awaited:
the **BT-0 duration** â€” the one phase with zero parallelism, so its length adds directly to wall-clock â€” and
the **Build-track start date**, from which bootstrap-exception `start`/`expiry` dates, the 90-day restore
rotation and the "roughly month 3" asset gate are all measured.

---

## FD-007 â€” REG-004 Â· The JSON Schema `$id` host

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0
**Answer:** **Option A â€” the company's own domain**, as `https://schemas.<company-domain>/<family>/<entity>/v<N>.schema.json`,
recorded once in `contracts/schema-ids.yaml`.

**Status: AWAITING VALUE** â€” the domain itself.

**Why.** Recommended by `master/09`. `$id` values are baked into every schema file and every cross-file
`$ref` in `contracts/**`; changing them later rewrites every schema across three lanes at once, which is
precisely the class of change the partition exists to prevent. Durability is therefore the property that
decides this, and a domain the company owns outlives any repository or branch layout. Option B
(`raw.githubusercontent.com/<org>/control-plane/main/...`) couples every `$id` to a branch name and to
GitHub; option C (a URN) is never resolvable and is handled poorly by some tooling â€” a real risk given
`check-jsonschema` is the validator chosen in FD-005.

**Note.** No DNS record needs to exist for the `$id` to be valid; `$id` is an identifier, not a fetch target.
The domain must simply be one the company controls and will keep.

**Blocks.** L1 `schemas/registry/**`, `schemas/product/**`; L4 `schemas/records/**`. A schema cannot be
written without an `$id`, so the blocked tasks STOP outright â€” there is no interim behaviour.

---

## FD-008 â€” REG-014 Â· `CODEOWNERS` content

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0
**Answer:** **Option A â€” per-lane human reviewers**, generated from `lane-owners.tsv` by `L0-02-T05`.

**Status: AWAITING VALUES** â€” the real GitHub logins replacing `@LEAD_GITHUB_LOGIN` and `@LANE1_REVIEWER`
â€¦ `@LANE5_REVIEWER`.

**Why.** It is the only option that satisfies both constraints at once: Â§98.2's Phase 1 completion check and
`master/00` EC-14 require **human identities only**, and `master/05` `L0P0-E3` requires a lane team for every
prefix â€” which `master/03` Â§1.6's single `* @<l0-login>` line does not. Generating the file from the same
source as `lane-paths.tsv` makes divergence between ownership and review structurally impossible. Option C
(lane teams) fails EC-14 the moment a team contains a machine account, and the check is executed negatively,
so the failure surfaces as a blocked merge rather than a clear error.

**Consequence.** Five named humans among the nine are needed as lane reviewers. This deliberately spreads
review load off the Founder, who is already L0 (FD-001).

**Binding regardless of option, `L0D-LG-5`.** `L0-00-T01` criterion 4 greps whole lines for
`bot|\[bot\]|records-writer|reconciler` and requires 0 â€” but a correct `CODEOWNERS` contains the path
`/reconciler/`, so **the v1 check can never pass on a correct file**. The check must be reissued to test the
**owner column** only. This is a defect in `L0-00-T01`, not a reason to change the answer.

**Also settled:** `master/03` Â§1.6's single-line form and `master/01` Â§3's team form are both superseded.

---

## FD-009 â€” PREREQUISITE Â· GitHub plan tier

**Decided:** 2026-09-02 Â· **Band:** prerequisite (not a `REG-` entry)
**Answer:** **GitHub Team, to be purchased.** Not yet bought.

**Why it matters.** Spec **D73** and Â§99.5 fix GitHub Team as the minimum, and Â§11.4 calls it
*"non-negotiable, the one item that forces a paid plan"*, because branch protection on private repositories
requires it. Branch protection is the mechanical basis of PARTITION rule 1 â€” the reason merges cannot
conflict.

**Consequence: this is now on the critical path, ahead of `L0-P0-001`.** Nothing in Phase 0 that depends on
branch protection can be verified until the plan is active, and **REG-013** (branch-protection mechanism and
the Phase-0 required-check list) cannot be closed. Purchase it **before** the organisation is created, so
rulesets and App scopes attach to a correctly-tiered object from the start rather than being re-applied.

---

## FD-010 â€” The integration cadence is CONFIGURATION, not a constant

**Decided:** 2026-09-02 Â· **Band:** decisive â€” governs all 873 lane tasks and every schedule in the set
**Answer:** **The cadence is a declared, calibrated configuration value with an enum of states, not a
hard-coded constant.** States: `daily | weekly | monthly | paused | stopped`.

**Why this is the right shape, and not an evasion.** The founder's own specification already carries both
halves of this pattern, and the plan simply failed to use them:

| Spec mechanism | Where it already exists | What it gives us here |
|---|---|---|
| *"Calibrated configuration, initial value X"* | Used throughout â€” verification-contract execution cadence, `cost.usage_reconciliation` (hourly), suspension review-by (10 working days), founder-unreachable delegation (5 working days), credential rotation (quarterly), audit-log review (weekly), export-key rotation (annually) | The cadence carries a declared initial value that is **recalibrated from measurement**, rather than being a number one agent typed into one file |
| `lifecycle: active \| maintenance \| paused` | Already in `product.yaml` (spec Â§15) | `paused` is a first-class, legal state â€” and the spec already makes windows scale with it: *"for products in `maintenance` or `paused`, staleness is measured relative to the product's last activity â€¦ a deliberately parked product does not go structurally Red"* |

This is spec Â§1.2's second load-bearing idea â€” *configuration, not architecture* â€” applied to the one place
the plan hard-coded a constant. It also dissolves the defect directly: **three mutually exclusive clocks
exist because three documents each hard-coded a different constant.** A single declared field with one
authority makes all three readings of it derived rather than competing.

**The shape to build.**

```yaml
# contracts/integration.yaml â€” L0-owned, frozen at Phase 0
integration:
  cadence: daily            # daily | weekly | monthly | paused | stopped
  prs_per_lane_per_cycle: 3 # calibrated configuration
  # both recalibrated from measured train throughput, per the spec's calibration discipline
```

Per-product delivery cadence is a **separate** field on `product.yaml`, keyed off the existing
`lifecycle` enum. Do not conflate the two: the build train is a one-off Track-B activity that merges lane
branches into `integration`; per-product cadence governs the ongoing operating system.

**âš ï¸ What this answer does NOT settle, and must not be allowed to hide.** Making the cadence configurable
does not change the arithmetic â€” it relocates it. At `weekly` Ã— 1 the projection is still **175 weeks
against a published 8â€“22 week band**. Two things are therefore required in the same decision record:

1. **A declared initial value.** Recommended: `cadence: daily`, `prs_per_lane_per_cycle: 3` â€” the only one
   of the four configurations that lands inside the published band (873 Ã· 75/week â‰ˆ 12 weeks).
2. **A validator that makes an unmeetable configuration fail loudly.** `make cadence-check` recomputes
   projected weeks from the open task count and the declared cadence, and FAILS when the projection falls
   outside the declared Track-B band. Without it, the 175-week defect simply moves from a hard-coded line
   into a config file where nobody reads it â€” and a check that cannot fail is not a check (spec Â§53.1).

**Consequential edits.** Amend the `L0-03-T03`/`T04` jq selector to read the quota from configuration rather
than `.[0]`; delete the hard-coded *"One cycle per week, Wednesday"* from `lanes/L0-03:64` and the Wednesday
`MERGE TRAIN` row from `lanes/L0-00` Â§8.2; make `master/02` Â§5 and `protocol/06` Â§2 both derive their tables
from `contracts/integration.yaml` instead of stating competing constants. Also fixes a starvation bug:
`L0-03-T12` and `protocol/06` Â§7 call a lane skipped for 2 cycles a constraint diagnosis and 4 a TRAIN HALT
â€” under weekly Ã— 1, L3 with 194 ready tasks is skipped 193 times by construction.

**Note:** `stopped` is not currently a value of the spec's `lifecycle` enum (`active | maintenance | paused`).
For the train it is a new field and costs nothing. If `stopped` is later wanted on `product.yaml`, that is a
spec amendment (D114) and should be raised as one, not drifted into.

---

## FD-011 â€” The L0 seat: automate the review, split the mechanics

**Decided:** 2026-09-02
**Answer:** **Both moves.**

**Move 1 â€” the review becomes mechanical.** The 873 human PR reviews the plan requires check *"partition
compliance and contract conformance"*. Both are already machine-checkable: partition compliance by the
lane-guard, contract conformance by the `contracts/**` byte-compare adopted in FD-003. Those checks become
the **verdict of record**; the Founder reviews only PRs a check flags, plus a declared sample. This converts
roughly **145 unallocated hours** into a sampling budget.

> The sample rate is itself calibrated configuration, and it must not be zero: a review path that never
> looks at a passing PR is the silent-gate failure spec Â§99.6 risk 5 describes.

**Move 2 â€” the seat splits.** The Founder keeps what is genuinely the Founder's: the 60 `REG-` decisions,
`contracts/**` authorship, and the seven Â§99.3 design-open items. **Nimesh (Team Lead) runs the mechanics:**
the guard, the merge train, and promotion to `main`.

**Authority check â€” this delegation is legal.** Spec **D108** bars a founder-decision delegate from carrying
a formal *people* decision, and **D109** makes Layer B access non-delegable. Train mechanics are neither.
The plan already anticipates a second holder: `REG-046` asks how many context-holding humans hold Write
during V1, and `EXC-BOOT-001` exists for exactly this.

**Consequence.** `REG-046` is effectively answered at **two**. This also makes FD-008's per-lane human
reviewers materially easier to staff, since the Founder is no longer the default reviewer of everything.

**Record honestly, per the sweep's item 10:** B0 is **~24 working days, not the 3â€“5 the plan budgets**, and
per-cycle L0 load is 3â€“4 h/day. `master/04` Â§3.4's wall-clock formula `max(critical path, longest off-path
lane)` **has no L0 term** and must be reissued to include one. Until the seat is priced in the schedule,
every schedule in the set is a schedule for five agents and no integrator.

---

## FD-012 â€” REG-010 Â· L0's own branch prefix

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0
**Answer:** **Option A â€” `l0/<task>`** (e.g. `l0/freeze-contracts`, `l0/ccr-14`).

**And the correction that makes it real.** `REG-010` asserts this `case` arm *"already exists"*. It does
**not**. It is present in `master/03-conflict-prevention.md` at lines 241 and 409 (`l0/*|integration) LANE=L0`)
and **absent from `lanes/L0-02-lane-guard.md`, the file that actually ships the guard**, whose `case`
statement falls through to `die "LANE-GUARD REFUSED: branch names no lane"`.

**Severity.** Twenty sites across four L0 files open PRs from `l0/*` â€” including `l0/phase-0-contracts`
(**the contract freeze itself**), `l0/revert-promo-$CYCLE` (the promotion-rollback path),
`l0/t2w-negative-selfapprove` (the Phase-1 self-approval negative test) and all fifteen
`l0/onboarding-NN-*` branches. **All 23 Phase-0 tasks and all 15 L0-07 tasks are unmergeable as shipped.**
This is a day-one, first-command blocker.

**Required edits:** add `l0/*) LANE=0 ;;` to `lanes/L0-02-lane-guard.md` at ~line 548, and correct
`REG-010`'s false "already present" claim so it is not trusted again.

**Second half, settled in the same record.** The train enumerates candidates as
`startswith("lane/$n/")` inside `for n in 1 4 2 3 5`, so an `l0/*` PR is **never a train candidate** even
once the guard passes it. **Decision: L0 merges its own branches outside the train**, recorded as the
`L0D-07` exception. Adding an L0 slot to the train would put the integrator's own changes behind the queue
it operates, which is the wrong dependency direction.

---

## FD-013 â€” REG-007 Â· The `contracts/**` surface list

**Decided:** 2026-09-02 Â· **Band:** P1 Â· **Gates:** Ph0 â€” *this entry is the freeze*
**Answer:** **Option A.** Adopt `master/03` Â§3.1's directory layout (`contracts/schemas/`,
`contracts/event-types/`, `contracts/records/`, `contracts/workflow-io/`, `contracts/cli/`,
`contracts/fixtures/`, `CONTRACTS.lock`), extend it with `master/05` `L0P0-E1`'s seven per-lane files
(`estate.yaml`, `lane-paths.yaml`, `l1-schemas.yaml`, `l2-workflows.yaml`, `l3-reconciler.yaml`,
`l4-records.yaml`, `l5-access.yaml`) plus `master/06` Â§11's `contracts/v1-scope.yaml`, and publish
`contracts/CONSUMERS.md` naming which lane reads which surface. One layout; each lane gets exactly one path
to read.

**The register's stated cost is a false problem, and this record says so.** `REG-007` frames option A as
*"requires L0 to author all eighteen surfaces including the nine it has no domain knowledge of"*, and
`master/INDEX.md` G-10 poses it as a dilemma: either L0 authors nine surfaces blind, or a lane writes into a
path PARTITION rule 2 forbids it to touch. **Neither horn is real.** The domain knowledge is already
written down, in plan documents that exist today â€” `lanes/L4-02-record-schemas.md`,
`lanes/L2-01-reusable-workflows.md`, `lanes/L3-01-diff-engine.md`, `lanes/L5-01-org-and-access.md`. L0 is
**transcribing from documents**, not inventing nine specifications. Option B (lanes draft, L0 transcribes)
is additionally impossible as stated, because `master/01` Â§6.1 puts Phase 0 authorship entirely with L0
**before any lane exists**.

**Rejected: option C** (freeze only what Phase-0 lanes read). It would shorten the ~190-hour pre-B-Day
estimate, which is tempting given FD-011 â€” but it breaks the *frozen-from-Phase-0* property PARTITION rule 2
rests on and turns every later addition into a CCR against a moving baseline, which is the exact failure
contract-first design exists to prevent.

**Also settle in the same record** (`master/INDEX.md` R-9): `master/04` Â§7's `contracts/v1` tag check and
`master/03` Â§3.2's `contracts/CONTRACTS.lock` are **two independent freeze mechanisms, neither protected by
any ruleset**. Name one as normative and protect it.

---

## FD-014 â€” The dispatch gate (unregistered)

**Decided:** 2026-09-02 Â· **Band:** effectively P0 â€” nothing in the register asks this question at all
**Answer:** **Dispatch waits for the 270 blocking defects to be TRIAGED â€” not fixed â€” and for the six lane
coherence reviews to stop returning `BLOCKED`. It does not wait for the other 767.**

**The two conditions, stated so they can be checked.**

1. **All blocking defects triaged.** Every one sorted into exactly one of: *fix before dispatch*, *safe to
   dispatch against* (the merge train or integration gate will catch it), or *false â€” does not reproduce*.
   The third bucket is not hypothetical: the triage analysts were told to spot-check, and review findings
   that are themselves wrong are the most expensive kind, because a fix pass acts on them. Note the count
   will exceed 270 â€” a second review wave covering the 55 never-reviewed files is landing now.
2. **The six lane coherence reviews no longer return `BLOCKED â€” DO NOT DISPATCH`.** They all block on one
   thing: the index-vs-phase-file namespace fork. **FD-004's concordance is what clears it.**

**Why triage and not fix.** The five AI developers have no judgment authority and no repo context. A
blocking defect inside a task body does not become a raised blocker â€” it becomes a wrong artifact quietly
merged. That is the specific failure the pre-dispatch review exists to prevent. The 767 non-blocking
defects are precisely what the merge train and the integration gate are built to catch; holding dispatch for
them spends the Founder's serial time doing what an automated gate would do for free.

**Cost of being wrong is high in both directions**, which is why the gate is two named conditions rather
than a judgment call: dispatching early costs rework across five branches; waiting for all 1,037 costs weeks
of L0 time on top of the ~24 working days Phase 0 already carries (FD-011).

**This gate is independent of Phase 0.** Phase 0 (`L0-P0-001`â€¦`023`) may proceed in parallel with triage â€”
it is blocked only by the P0/P1 decisions, most of which are now closed. Do not serialise them.

---

## FD-015 â€” Q4 Â· REG-001 residual Â· Subsystem G: build or decline

**Decided:** 2026-09-02 Â· **P0**
**Answer:** **Neither yet â€” run the GSD capability verification FIRST, then decide.** Do not decide blind.

`master/00` EC-9 already requires a capability-verification run against the exact pinned GSD release, and it
is a **pre-B-Day entry criterion**, so it happens either way. Its result is the only fact that makes this
answerable: if the pinned release already does the job, G collapses from 3â€“8 founder-weeks to configuration.
G's internals are Â§99.3 design-open, so no lane may build it under any option â€” this is the Founder's
calendar, on top of Phase 0.

**Two literal edits that must ship with the eventual answer, which FD-002 omitted:**
1. **`G` assigned to L0 does not resolve to L0 under the guard.** L0 owns only `contracts/*`, `docs/*` and a
   root catch-all, and the `X<TAB>*/*` residual rule sits **above** it â€” so `plan-checker/anything` resolves
   `UNOWNED` and fails. Insert `printf '0\tplan-checker/*\n'` before the `X` line in `L0-00-T03`.
2. **The O-registry half of FD-002 cannot execute until REG-008 closes** (where the spec's root-named
   registry files physically live).

---

## FD-016 â€” Q6 Â· REG-047 Â· The pilots

**Decided:** 2026-09-02 Â· **Answer: TWO pilots.**

Ordered highest `reliability_criticality` first, then `business.criticality`, then cheapest onboarding cost
(Â§96.5). **Pilot one must be a repository whose team already holds Write** â€” that satisfies gate independence
immediately and never enters Bootstrap Mode (Â§95.1, Â§95.2).

Risk is asymmetric and that is why two: adding a third later is one list edit in an L0-owned contract;
withdrawing one mid-onboarding requires a fresh dated decision and full re-sequencing under Â§96.5. A third
pilot would also land on the Founder personally â€” `OT-P7`'s completion check is *"a first plan passes the
plan-checker"*, and the plan-checker is subsystem G (FD-015).

**Unblocks** `OT-P4`â€¦`OT-P7` for every product, `L0-07-T02`, the Phase-2 pre-onboarding stubs, and
`master/06` Â§13's **V1 exit gate, which today has no set to evaluate and cannot be run at all**.
**Awaiting: which two.**

---

## FD-017 â€” Q12 Â· REG-046 Â· Context-holding humans with Write during V1

**Decided:** 2026-09-02 Â· **Answer: TWO** â€” the Founder (L0, FD-001) and **Nimesh** (Team Lead), on
`control-plane` and `product-template`.

This is the headcount FD-011's split already implies. Two is also the minimum that makes FD-008's per-lane
human reviewers meaningful: with one Write holder every CODEOWNERS route collapses back to the Founder and
the review is self-approval in all but name. `EXC-BOOT-001` covers the gap until Nimesh is onboarded.
Each Write holder needs an operational-asset-inventory entry with a named rotation and a Â§62 trust-boundary
statement.

---

## FD-018 â€” Q9 Â· REG-037 Â· Self-hosted runner exception in V1

**Decided:** 2026-09-02 Â· **Answer: Option B â€” declare it not applicable for V1.**

Publish **both** runner-marker keys with the literal value `not-applicable-v1`, so `L2-T170`'s eleven-key
gate can **evaluate** rather than hang. Leaving the keys unpublished is what blocks **all of L2 Phase 3**
today.

Consistent with D87: the attack depends on shared persistence, hosted runners are ephemeral by construction,
and the privileged tail is ~500 min/month against 3,000 included â€” cost is not a reason to self-host.
Reversible: a product that later needs a fixed egress address or a private network files the exception then.

---

## FD-019 â€” Q15 Â· REG-033 Â· Template placeholder syntax **and the renderer's owner**

**Decided:** 2026-09-02 Â· **Answer: `{{TOKEN}}` syntax, and publish L2's renderer as a contract.**

- **Syntax â€” forced.** `${NAME}` collides with GitHub Actions `${{ }}` and with shell expansion in every
  `run:` block; a template engine adds a runtime dependency for a five-value substitution.
- **Owner â€” option (b).** Publish L2's `tools.evidence.render_template` as a contract artifact under
  `contracts/`, which L3 consumes. One renderer, placed by name, no PARTITION rule-4 violation.

**Why this was urgent, and the register did not say so.** Two L2 documents already write **incompatible
vocabularies into the same directory**: `L2-T300` writes `PLACEHOLDERS.yaml` with *"exactly five tokens and
nothing else"* plus an acceptance criterion that no sixth token exists anywhere under `templates/workflows/`,
while `L2-P1-T14` writes `PLACEHOLDERS.md` with **sixteen** tokens into that same tree. Dispatching Lane 2
without this ruling produces two branches whose acceptance criteria mechanically contradict each other â€”
visible only after both are written.

**Fold into the same ruling:** the vocabulary is incomplete. `ci.yml`'s required `base_ref` and
`restore-production.yml`'s `authorised_by` / `reason` / `backup_id` / `verifier` have no token and no
`product.yaml` source, so **three of eight templates cannot be written under a closed vocabulary**. Also, per
FD-020, drop `{{DEPLOY_COMMAND}}` and `{{RESTORE_COMMAND}}` before publishing.

---

## FD-020 â€” Q14 Â· REG-031 Â· Per-product deploy and restore commands

**Decided:** 2026-09-02 Â· **Answer: Option B â€” DENY the CCR.**

`product.yaml` does **not** gain `deploy_command:` / `restore_command:`. Extend Â§33.1's standard to
`make deploy` and `make restore`; the variation moves into each product's Makefile, where it belongs, rather
than into the control-plane schema governing all eight.

**The security reason, which the CCR does not state.** Two arbitrary command strings in `product.yaml` are
executed by the control plane against production. That is an unbounded command-injection surface â€” nothing
constrains what the string contains. A fixed target name is checkable; an arbitrary string is not.

---

## FD-021 â€” Q10 Â· REG-038 Â· The sandbox GitHub organisation

**Decided:** 2026-09-02 Â· **Answer: Option A â€” ONE sandbox organisation, on the Team tier.**

**It has to exist regardless**: `lanes/L3-04` Â§0.3 makes *every* task in L3's provisioning phase target
`$PROVISION_SANDBOX_ORG` and refuse to run against anything else (lines 48, 65, 608, 1324, 1553), and
`L3-07-T01` STOPs without `FIXTURE_ORG`. The decision is money, not scope.

**Team tier, not free.** Environment protection and Â§33.4's deployment branch-and-tag policy on private
repositories require Team â€” and their absence is exactly what `L2-T608` exists to prove. A free sandbox
silently makes the X3 test meaningless.

**This record declares them one organisation.** L2's `sandbox_org_slug`, `lanes/L3-04` Â§0.3's
`$PROVISION_SANDBOX_ORG` and REG-041(a)'s `FIXTURE_ORG` are the **same** org. No document currently says so.
**Sequenced:** FD-009 (Team plan) â†’ the production org â†’ this. **Add an acceptance criterion asserting
`FIXTURE_ORG != LIVE_ORG`**, or `TC-L3-03` â€” which proves the reconciler *refuses* the live org â€” proves
nothing.

**Unblocks** `L2-T603`, `L2-T221`, `GATE-L2-005`, and all of L3's provisioning phase including the AT-001
add-product-21 rehearsal at `L3-04-T14`.

---

## FD-022 â€” Q8 Â· REG-020 Â· The eight record stores Â§97.2 does not list

**Decided:** 2026-09-02 Â· **Answer: Option A for rows aâ€“g, Option B for row h.**

Amend Â§97.2 for the seven rows that are genuinely their own record kind, publishing **path, id prefix and
schema id** for each; route row h into an existing store. **Note the count: rows aâ€“g yield EIGHT stores, not
seven â€” row e is two.**

**Why it needs a spec amendment.** D103 requires records, events and states to carry schemas, so a record
kind with no declared store and no schema id is unenforceable by construction. Â§97.2 is a table, so **D113's
rule governs the edit: one row per line, verified against parsed rows, never against line counts.**

---

## FD-023 â€” Q11 Â· REG-041 Â· The AT-110 live probe

**Decided:** 2026-09-02 Â· **Answer: authorise it, with Nimesh as the named supervisor** â€” and publish
`contracts/l3-test-harness.env` with its ten keys rather than discovering flags from `--help`
(help-text discovery **fails open** on a rename, the wrong failure direction for a privileged-credential test).

AT-110 is the one test Â§100.6 says must be *"executed rather than asserted"*, because it bounds the most
privileged credential in the estate (Â§99.6 risk 6). The gate is self-enforcing:
`contracts/l3-live-org-gate.md` cannot honestly be published until Â§98.2's Phase-3 completion check passes.

**Two defects that must be fixed in the same ruling:**
1. **A second, ungated live probe exists**, named by neither the register nor the docket. `lanes/L3-07` T10
   gates AT-110 on `contracts/l3-live-org-gate.md`; `lanes/L3-06` `L3-P5-06` builds
   `validators/drift/credential_bounds.py --mode live` gated only on `L3-D3`. **Two agents on parallel
   branches could both fire a live probe at the highest-privilege identity under gates neither knows about.**
   Record them as the same gate and delete the duplicate.
2. **`AT-110.sh` proves nothing as written.** It issues six bare `gh api` calls, which run as whoever ran
   `gh auth login` â€” **not as the reconciler**. Under a low-privilege login all six refuse and AT-110
   "passes". It must assume the reconciler identity explicitly.

**Unblocks** `L3-07-T01` and therefore the entire eleven-task L3 suite (T02â€¦T11 all chain off T01).

---

## FD-024 â€” Q16 Â· REG-060 Â· The seven design-open items of Â§99.3

**Decided:** 2026-09-02 Â· **Answer: close items 2 and 3 now; items 1, 4, 5, 6, 7 stay open under their
gating phases; declare none declined today.**

- **Item 2 (`L0D-11`, the `make parity` format).** Adopt `master/09` Â§19 option A: a per-environment
  `env.<environment>.yaml` declaring variable names, types and required/optional, validated by a JSON Schema
  like every other control-plane artifact. **Home it at `contracts/environment-schema.yaml`, L0-owned** â€”
  *not* L5 `infra/**` as `master/09:1412` recommends.
- **Item 3 (`L0D-12`, plan-checker internals).** This is FD-015's input: run the capability verification now;
  the build budget follows the result.

**The register records `blocks | none` against this entry. That is false.** `L2P2-N2` (`master/05:738`) tests
`test -f contracts/environment-schema.yaml` and `master/05:775` STOPs on its absence â€” so **L2 Phase 2, L4
Phase 4 and L4 Phase 5 cannot be entered** without item 2. Three lane phases.

> **âš ï¸ This amends FD-013.** `contracts/environment-schema.yaml` is **absent from FD-013's frozen
> `contracts/**` surface** â€” not in `master/03` Â§3.1's layout, not among `master/05`'s seven per-lane files,
> not `v1-scope.yaml`, not `CONSUMERS.md` â€” while `master/05:738` tests for it by exact path. **Add it to the
> frozen list in the same commit**, or `L2P2-N2` can never pass.

---

## FD-025 â€” The authority-delta detector (unregistered)

**Decided:** 2026-09-02 Â· **Answer: L3 owns it.**

An authority delta is a difference between declared state and actual platform state â€” that is the definition
of drift, and L3 owns `validators/drift/**` and the reconciler. One lane then owns the whole
compare-declared-to-actual surface, and no path changes: `L3-06` already places it where L3 may write.

**Consequential edit:** `lanes/L3-03-canary-and-integrity.md:1764` explicitly refuses the work and routes it
to L1. That refusal is now incorrect and is a one-line correction â€” chosen over the alternative, which would
have required a partition amendment, since `L3-06` Â§0.1 forbids L3 writing to `validators/registry/**`.

**Surfaced by the concordance work, not by any register entry or review.**

---

## FD-026 â€” Q13 Â· REG-023 Â· Arming the auto-repair class

**Decided:** 2026-09-02 Â· **Answer: O-5B â€” arm auto-repair only after 28 consecutive days with zero
incorrect repair proposals.**

The reconciler applying a fix automatically is a change to production made by a machine on the strength of
its own judgement, so the evidence bar is **behavioural and measured**, not a date someone picked. 28 days
covers a full monthly cycle including a restore-test rotation. Consistent with Â§53.1: a control needs
demonstrated discriminating power before it is trusted.

**Still awaiting:** the operating **timezone** and **core-hours end**. Nothing can derive them, and they set
the out-of-hours escalation thresholds (D85) and the whole Â§94.8 cadence table.

---

## FD-007-R â€” REG-004 RE-DECIDED Â· The JSON Schema `$id` host

**Re-decided:** 2026-09-02, superseding FD-007's Option A.
**Answer:** **Option C â€” a URN.** Scheme: `urn:controlplane:<family>:<entity>:v<N>`, e.g.
`urn:controlplane:registry:people:v1`. Recorded once in `contracts/schema-ids.yaml`.

**Why the original answer was wrong.** FD-007 chose the company domain on the grounds that it is *durable*.
The founder's challenge inverted that argument correctly: an `$id` is baked into every schema and every
cross-file `$ref`, and changing it rewrites every schema across three lanes â€” so the property that actually
matters is **"can never need to change."** A domain is an **external fact that can change**: a rebrand, an
acquisition, a lapsed renewal. A URN depends on nothing outside the repository. For the one field in the
design that is most expensive to change, the right choice is the one with no external dependency at all.

**The objection that blocked C did not survive testing.** FD-007 rejected URNs because *"some tooling handles
URNs poorly"* â€” an assertion made without testing, against the validator chosen in FD-005. Tested directly:

```
jsonschema 4.23.0, Draft202012Validator, two schemas linked by
$ref: "urn:controlplane:registry:_common:v1#/$defs/effective_date"
  â†’ cross-file $ref by URN resolved: OK
  â†’ valid document   â†’ passes
  â†’ invalid document â†’ caught: "'effective_from' is a required property"
```

Draft 2020-12 permits any absolute URI as an `$id`, and `check-jsonschema` resolves `$ref`s through its own
registry rather than by fetching. **Verify once more against the pinned `check-jsonschema` version before the
freeze**, then sign.

**Consequence:** the company domain is no longer needed for schemas at all. It is removed from the awaited
values.

---

## FD-027 â€” Configuration, not frozen literals (a design amendment)

**Decided:** 2026-09-02 Â· **Origin:** the founder's question â€” *"can't we build it so a UI updates these, and
it works from an ENV?"*

**Answer:** **Yes, and the specification already requires it. The plan contradicts the spec here, and the
spec wins.** These values are **registry data or calibrated configuration**, never literals frozen into
Phase-0 contracts.

**Spec authority, verified:**

| Spec | Text |
|---|---|
| Â§872 | *"**CODEOWNERS** routes review requests automatically and is **generated from the registries rather than hand-maintained**; the generator emits human identities only."* |
| Â§858 | *"Team membership is **derived from the registries and reconciled continuously** â€” a mismatch between `people.yaml`, `product.yaml` and actual GitHub Team membership **fails CI and raises a drift finding**."* |
| Â§4526 | *"values are **derived, never hand-maintained**."* |

**The class, and where each value actually lives:**

| Value | Home | Changing it later |
|---|---|---|
| GitHub org login | `contracts/estate.yaml['org']` | one field |
| Human GitHub logins | `people.yaml` â†’ CODEOWNERS **regenerates** | one field |
| The eight products, 24 fields | `product.yaml`, one per product | one field |
| Which products are pilots | a registry field | re-sortable |
| Security / licence / SBOM scanners | `tools.yaml` | one field |
| Operating timezone, core-hours end | calibrated configuration | one field |
| BT-0 duration, `build_track_start_date` | calibrated configuration, declared initial value | one field |

**What changes in the plan.** Every Phase-0 task carrying a `placeholders=0` acceptance gate on one of these
is rewritten to **read the value from its registry or from `contracts/estate.yaml`**, with a validator that
**fails closed** when a required value is absent. A missing value must stop the run loudly â€” the point is to
remove the hard-coding, not the check.

**The two values that remain genuinely irreducible**, because no amount of configuration removes a
chicken-and-egg:

1. **The GitHub organisation login.** `gh repo create "$ORG/control-plane"` cannot run inside an organisation
   that has no name, and the name must be registered with GitHub before it exists.
2. **One human GitHub login â€” the Founder's.** Branch protection needs at least one human it can require a
   review from, and `L0-00-T01` cannot commit a CODEOWNERS containing only placeholders.

Everything else is entered once as data and changed freely thereafter.

**On the UI.** What the founder described *is* in the plan: subsystem **H** (dashboards and views), assigned
to L5 by FD-002, with Founder view v0 inside V1 per Â§99.4. The ordering constraint is unavoidable â€” the UI is
built *by* the system, so it cannot precede it. The two bootstrap values create the repository that holds the
registries that the UI later edits.

**Effect.** Roughly **25 blockers** move from *"awaiting a founder value"* to *"reads its value from a file."*
Same shape as FD-010, and for the same reason: an agent hard-coded a constant where the specification wanted
configuration.

**This amends FD-006 and FD-008** â€” both remain correct in form; only the org login and one human login are
still awaited, not the full set of values they listed.

---

## FD-028 â€” The Acting Team Lead designate (unregistered)

**Decided:** 2026-09-02 Â· **Band:** effectively P0 for continuity Â· **Cost:** none
**Answer:** **Bhushan is the Acting Team Lead designate.**

**What this closes â€” the largest structural fragility found in the design phase.** `Design/ROLES.md` Â§5.0
states it: *"Every single-holder mitigation in this specification terminates in the same place."* Â§54.4
routes reviewer unavailability to the escalation role; EC-7 routes QA verification authority to the Team
Lead; Â§44.2 gives restore-rotation scheduling to the escalation role; Â§37.5 gives background-layer class
restoration to the Team Lead. **The escalation role is Nimesh, and his Acting designate slot was empty** â€”
with Â§98.3 scheduling the designation as *early hardening*, i.e. after Phases 1 through 7.

> *"The four single-holder risks are not four independent risks. They are four tributaries into one."*

Naming a designate converts four single points of failure into three, and it costs nothing.

**Why Bhushan, and why he is the only candidate.** Â§13.1 requires the designate to hold `plan-approval`
and `architecture` **continuously but dormant**, so that activation is a configuration change rather than
a competence question decided under pressure. Bhushan holds `architecture` already as a
`senior_developer` default. Every other person is disqualified:

| Person | Why not |
|---|---|
| Saumit, Prathamesh, Mansi, Harshal | Each is the **sole holder** of their own capability. Promoting any of them relocates the fragility rather than removing it |
| Swati, Aarti, Unmesh | Hold `code-review` only; no `architecture` |
| The Founder | Creates a loop â€” Â§14.3 already grants the Founder's emergency founder-class scope **to the Team Lead**, so the two seats would cover each other with no outside fallback. Also adds to a seat already carrying 23 Phase-0 tasks |

**The caveat, recorded rather than buried.** `Design/ROLES.md` ranks Bhushan **6th** on fragility as *"the
holder of two independent safeguards that fail together"* â€” he is the only legal Gate 1 approver for
Nimesh's own plans **and** the compensating control for that same gate. This decision adds a third
dependency to one person. It is still correct: **a designated understudy who is slightly overloaded beats
an empty slot entirely.** But it should not be mistaken for a complete fix.

**Required edits.**
1. `topology.yaml` succession block: set `succession.team_lead.acting` to Bhushan. Â§13.1 places the
   designation here, alongside the other rules mapping roles to people â€” **not** in `roles.yaml`, which
   Â§8 forbids from naming a person.
2. `people.yaml`: grant Bhushan `plan-approval` as a **dormant** capability, held continuously. It is not
   a `senior_developer` default, so it must be an explicit grant.
3. On activation, the **full `team_lead` capability set** â€” including `platform-change-approval` â€” is
   granted for the recorded activation period and **expires with it** (Â§13.1). Activation and
   deactivation are both recorded events.
4. Note Â§13.1's dormancy rule: *"the dormant Acting designate may approve Team-Lead-authored plans
   without activation"* â€” that is precisely what the continuously-held dormant `plan-approval` is for.
   Activation is required only to assume the wider Team Lead authority set.

**Open follow-on, not decided here.** Â§68.4 records that only **two to three of the nine** are independent
multi-product owners today. The real structural fix is a fourth, and **Aarti** is the Foundational
Developer already on that path. Recommend recording a capability-development plan with a review date, so
the Acting designate is eventually a choice rather than the only eligible name. Raise as a register entry.

---

## FD-029 â€” REG-061 Â· The `contracts/gate/**` freeze scope (B-01 correction)

**Decided:** 2026-09-02 Â· **Band:** P0 Â· **Gates:** Ph0
**Question:** `L0-00-T04` defines `make freeze` / `make promote-check` as hashing every file under
`contracts/`. `L0-05-T01`â€“`T13` write `contracts/gate/**`, and `L0-05-T04` introduces `contracts/gate/PHASE`,
which L0 advances at each Â§98 phase boundary. This makes a mutable file live inside a tree whose hash is
asserted immutable, guaranteeing `CONTRACTS-DRIFT` on every `make train-preflight`. Which of three correction
options should be implemented?

**Answer:** **Option (b)** â€” redefine `make freeze` and `make promote-check` in `L0-00-T04` to hash
`contracts/` **excluding** `contracts/gate/` and `contracts/ci/`; freeze the gate tree separately under
`gate.sha256` + `gate/v1.0.0`, where `gate.sha256` excludes `PHASE` (which is mutable by design and
anchored by the Â§98 phase-completion protocol, not by hash).

**Why (b) over (a) and (c):**
- **(a)** (move gate tree to `gate/**`) requires renaming paths throughout `L0-05`, `L0-02`, `L0-03`,
  `PARTITION.md`, `CODEOWNERS`, and `lane-paths.tsv` â€” significant blast radius for a naming change.
- **(c)** (re-run `make freeze` in `L0-05-T15` + move PHASE) re-freezes all of `contracts/` on every
  cycle, coupling the gate-record workflow to the Phase-0 contract freeze. Any post-Phase-0 CCR on a
  contract would then require running T15 again. Also doesn't fix the PHASE mutable-file problem unless
  PHASE is moved to a non-hashed location.
- **(b)** is surgical: it separates the two freezes at the boundary that is already semantically meaningful
  (`contracts/gate/` is gated by `L0D-IG-10` and `gate/v1.0.0`; `contracts/ci/` is gated by the CCR
  process), leaves all path names unchanged, and makes PHASE's mutability explicit by excluding it from
  both hashes.

**Implementation recorded in:**
- `lanes/L0-00-charter.md` `L0-00-T04`: `freeze` and `promote-check` updated with `-not -path` exclusions;
  `gate-freeze` target added.
- `lanes/L0-05-integration-gate.md` `L0-05-T01`: `make gate-freeze` + `git add gate.sha256` inserted before
  the `gate/v1.0.0` tag push.
- `lanes/L0-04-decisions-register.md`: REG-061 row added (state: closed).

---

---

## FD-030 â€” Q1 (dispatch gate Â§5.1) Â· Task delivery mechanism

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** all lanes
**Question:** How is a task delivered to an agent? Task card vs tasks/<ID>.md vs lane pack Â§9.
**Answer:** Lane file + task ID â€” the agent receives the lane file path and the task ID; the task card
model (G3) is enabled by this answer and can now be completed.

---

## FD-031 â€” Q2 (dispatch gate Â§5.1) Â· Task-id grammar

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** all lanes
**Question:** One task-id grammar + one branch grammar â€” 6 live id schemes across 845 ids.
**Answer:** Two-part `L1-001` grammar is canonical. Corollaries: D3-L1 (task-id scheme), D1-L4
(task-id namespace) follow this grammar.

---

## FD-032 â€” Q3 (dispatch gate Â§5.1) Â· Execution model

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** all lanes
**Question:** One execution model â€” one task per session vs continuous executor.
**Answer:** One session per task.

---

## FD-033 â€” Q4 (dispatch gate Â§5.1) Â· AT/e2e ownership

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** REG-015
**Question:** Who owns `verification/acceptance/**`, `tools/at/**`, `e2e/**`, `contracts/harness/**`?
**Answer:** Split ownership â€” L0 owns `e2e/**` and `contracts/harness/**`; each lane owns
`tools/at/<lane>/`. This closes REG-015.

---

## FD-034 â€” Q5 (dispatch gate Â§5.1) Â· Residual-ownership rule

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** lane-paths.tsv
**Question:** `lane-paths.tsv` makes L0 UNASSIGNED for its own Phase-0 work.
**Answer:** Add L0 carve-out rows to `lane-paths.tsv` so L0's Phase-0 paths are explicitly assigned.

---

## FD-035 â€” Q6 (dispatch gate Â§5.1) Â· Exit-code contract

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** all gate scripts
**Question:** Exit 1 inversion â€” breached gate currently scores as armed in several scripts.
**Answer:** `exit 0` = gate **ARMED** (clean). `exit 1` = gate breached. All gate scripts must follow
this convention consistently.

---

## FD-036 â€” Q7 (dispatch gate Â§5.1) Â· Negative-test apparatus

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** L1, L4
**Question:** One negative-test apparatus â€” 4 namespaces, 4 fixture layouts, no concordance.
**Answer:** Canonical layout: `tests/fixtures/invalid/<schema-id>/`. All negative fixtures migrate to
this namespace.

---

## FD-037 â€” Q8 (dispatch gate Â§5.1) Â· ATâ†’owner map authority

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** all lanes
**Question:** AT â†’ owner-lane map: `protocol/00` vs `protocol/02` disagree on 16 of 37 rows.
**Answer:** `protocol/02` is the authoritative AT-ownership authority. `protocol/00` rows deferred to it.

---

## FD-038 â€” Q9 (dispatch gate Â§5.1) Â· access-inputs.yaml shape

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** L5-02, L5-03
**Question:** `contracts/access/access-inputs.yaml` shape â€” L5-02 publishes 5 keys, L5-03 reads 6.
**Answer:** L5-02 adds `layer_b_admin_group` as the 6th key. L5-03's read is correct; L5-02's publish
must be extended.

---

## FD-039 â€” Q10 (dispatch gate Â§5.1) Â· Writer CLI canonical form

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** L1, L4
**Question:** Which writer CLI is canonical â€” positional or long-option? (`assert_rejects` currently
vacuously green.)
**Answer:** Long-option CLI: `--path --type --title`. All invocations must use long options.

---

## FD-040 â€” Q11 (dispatch gate Â§5.1) Â· build.yml owner

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** CODEOWNERS
**Question:** Who owns `.github/workflows/build.yml`? 3 mutually exclusive contracts claim ownership.
**Answer:** L2 owns `.github/workflows/build.yml`. The other two claims are superseded.

---

## FD-041 â€” Q12 (dispatch gate Â§5.1) Â· event-types.yaml authorship

**Decided:** 2026-09-03 Â· **Band:** design Â· **Gates:** contracts/
**Question:** 86-entry `event_type` enum â€” L0 must publish in `contracts/`.
**Answer:** L0-P0 authors `contracts/event-types.yaml`. This is a Phase-0 task.

---

## FD-042 â€” D2-L1 Â· L1 validator implementation

**Decided:** 2026-09-03 Â· **Band:** L1 Â· **Gates:** L1-02
**Question:** Five mutually exclusive validator implementations (D2-L1).
**Answer:** Python `jsonschema` library. AJV and all Node.js validator paths removed. (FD-005 corollary
â€” Python wins; this decides the specific library.)

---

## FD-043 â€” D5-L1 Â· L1 schema file layout

**Decided:** 2026-09-03 Â· **Band:** L1 Â· **Gates:** L1-02, L1-06
**Question:** Three incompatible schema file layouts (D5-L1).
**Answer:** Single-file schema per contract type at `schemas/registry/<id>.json`.

---

## FD-044 â€” B1-L2 Â· L2 authoritative decomposition

**Decided:** 2026-09-03 Â· **Band:** L2 Â· **Gates:** L2 lane
**Question:** Two complete incompatible plans â€” `L2-05-tasks.md` (76 tasks) vs five phase files (78
tasks).
**Answer:** `L2-05-tasks.md` is canonical (76-task plan). Phase files are superseded. Corollaries B4
and B6 follow from this choice â€” B4 namespace and B6 actor-gate form both derive from L2-05.

---

## FD-045 â€” B1-L3 Â· L3 authoritative plan

**Decided:** 2026-09-06 Â· **Band:** L3 Â· **Gates:** L3 lane
**Question:** Two complete incompatible plans â€” 78-task plan vs 116-task plan (phase files).
**Answer:** **116-task plan â€” phase files are authoritative.** The 78-task figure that appeared in the
last-session summary was a transcription error from a stale snapshot. Session 9 ledger was correct.
Corollaries: B5 package layout follows the phase-file structure; B8 (L3-06 pre-resolving DR-L3-05-A
through E) must be unwound â€” those fields are not yet decided.

---

## FD-046 â€” B4-L3 Â· L3 fixture/mock approach

**Decided:** 2026-09-03 Â· **Band:** L3 Â· **Gates:** L3-06
**Question:** L3-06 Â§0.4 forbids live GitHub org; L3-04 requires one. Contradiction.
**Answer:** Mocked stub â€” L3 tests use a mocked GitHub org stub, not a live org.

---

## FD-047 â€” B1-L5 Â· L5 task system

**Decided:** 2026-09-03 Â· **Band:** L5 Â· **Gates:** L5 lane
**Question:** Two parallel mutually contradictory task systems â€” L5-06-tasks.md ("ATOMIC TASK LIST",
L5-T01..T59) vs L5-01..L5-05 phase files.
**Answer:** Phase files (L5-01..L5-05) are authoritative. L5-06-tasks.md becomes a concordance index
only; its task bodies do not execute.

---

## FD-048 â€” D2-L4 Â· L4 metric-register phase

**Decided:** 2026-09-03 Â· **Band:** L4 Â· **Gates:** L4-04, DoD-5/13/14/15/19
**Question:** Entire metric-register phase absent (15 modules, five DoD items undischargeable).
**Answer:** Add metric-register as a separate phase under L4-04 with 15 modules authored as separate
tasks. DoD items 5, 13, 14, 15, 19 become dischargeable once these tasks are written.

---

## FD-049 â€” D8-L4 Â· L4 attention-ledger model

**Decided:** 2026-09-03 Â· **Band:** L4 Â· **Gates:** L4-03, L4-05
**Question:** Two incompatible attention-ledger designs â€” dual implementation conflict.
**Answer:** Event-log model: append-only JSONL per product. L4-05 implementation is authoritative;
L4-03 cross-reference removed.

---

## FD-050 â€” Schema URN namespace

**Decided:** 2026-09-06 Â· **Band:** design Â· **Gates:** L1, all schema $id fields
**Question:** FD-007-R chose URNs for schema `$id`. What is the canonical URN namespace prefix?
**Answer:** `urn:multiproduct:schemas`. Full `$id` format: `urn:multiproduct:schemas:<type>:<version>`
(e.g., `urn:multiproduct:schemas:product:v2`). This prefix is stable by design â€” it references the
system, not the company name or any external DNS name.

---

## FD-051 â€” GitHub organisation login

**Decided:** 2026-09-06 Â· **Band:** infra Â· **Gates:** Phase 0 (L0-P0-001)
**Question:** Which GitHub org login will hold the `control-plane` and `control-plane-records` repos?
**Answer:** `paresh-org`. All `gh` CLI calls, `ORG` env var, and CODEOWNERS references use this login.
**Pre-condition:** The org must be created and upgraded to GitHub Team tier (FD-009) before L0-P0-001
runs. The `gh` CLI is authenticated as `PerpetualSolution` / `pbhayashri`; verify that account has
authority to create the `paresh-org` org before Phase 0 begins.

---

## FD-052 â€” Lane reviewer CODEOWNERS strategy

**Decided:** 2026-09-06 Â· **Band:** infra Â· **Gates:** L0-P0-002 (CODEOWNERS authoring)
**Question:** Five lane reviewer GitHub logins needed for CODEOWNERS and branch protection.
**Answer:** Defer â€” write CODEOWNERS with `@paresh-org/lane-1-reviewers` through
`@paresh-org/lane-5-reviewers` team handles. Replace with real logins before Phase 1 dispatch.
Phase 0 operates with L0 alone; branch protection teams are not exercised until lanes open.

---

## FD-067 â€” Founder's GitHub login

**Decided:** 2026-09-08 Â· **Session:** 12 Â· **Band:** infra
**Question:** What is the Founder's personal GitHub login (needed for CODEOWNERS L0 paths and L0-P0-001 commit attribution)?
**Answer:** `bendrohit-eng`. Account created 2026-07-24; confirmed active via `gh auth status`.

**Corollaries:**
- Replace every `@LEAD_GITHUB_LOGIN` in CODEOWNERS blocks with `@bendrohit-eng`
- Replace `L0_LOGIN` variable references with `bendrohit-eng`
- `bendrohit-eng` is the account that will create the GitHub org and run Phase 0
- Previous references to `PerpetualSolution` / `pbhayashri` in FD-051 describe a different account and are superseded for this purpose

---

## FD-068 â€” Org name is a single config value, not a hardcoded literal

**Decided:** 2026-09-08 Â· **Session:** 12 Â· **Band:** infra
**Question:** How should the GitHub org login be distributed across the 92 plan files?
**Answer:** One canonical config file (`contracts/project-config.sh`), all scripts source it. No org literal is hardcoded in any script. The placeholder token `<ORG>` marks every remaining injection point. When the org is created, one edit to `project-config.sh` propagates to all scripts.

**Corollaries:**
- `contracts/project-config.sh` exports: `ORG` (org login), `L0_LOGIN` (bendrohit-eng), `SCHEMA_URN` (urn:multiproduct:schemas), `CP` (control-plane), `CPR` (control-plane-records)
- Every script that sets `export ORG="<github-org-login>"` is rewritten to `source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"`
- FD-051 (`paresh-org`) is SUSPENDED â€” user does not recognise or control that org. Real org name TBD; user creates org at github.com/organizations/new as `bendrohit-eng` and reports the name.
- Until org is created, `ORG` value in `project-config.sh` is `""`; all Phase 0 scripts already check `${ORG:?ERROR: set ORG in contracts/project-config.sh}` and stop cleanly if unset.

---

## Recording rule

When the control-plane repository exists, each row above becomes a dated decision record under
`records/decisions/` written through the `record-decision` CLI (spec Â§97.2), and the corresponding
register row points at it. This file is then superseded, not deleted.

---

## FD-053 â€” REG-020: Verification-block store path

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** REG-020 (blocked L2-T174 and L2 dispatch)

**Decision:** Verification-block records are stored at `records/verification-blocks/`

**Rationale:** Consistent with the records/ tree layout; parallel to other record stores managed by L4.

**Corollaries:**
- L2-T174 acceptance criterion referencing the store path uses `records/verification-blocks/`
- Any L2 template or workflow that writes verification blocks targets this path
- L4 must treat this store in its freshness/retention configuration

---

## FD-054 â€” REG-033: Template placeholder token syntax

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** REG-033 (blocked all L2 template and workflow tasks)

**Decision:** Canonical template placeholder syntax is `{{TOKEN}}` (double-brace)

**Rationale:** L2-05 is already written using {{TOKEN}} throughout; this is a ratification requiring zero rework.

**Corollaries:**
- All L2 template files use `{{TOKEN}}` for placeholder values
- No `%TOKEN%` or `${TOKEN}` forms are used in template heredocs
- Any new template tasks added to L2 follow this convention

---

## FD-055 â€” L0-B01: contracts/gate/ freeze conflict fix

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L0-B01 (CONTRACTS-DRIFT on every make promote-check)

**Decision:** Move `contracts/gate/**` out of `contracts/` into a new `gate-state/` directory at repo root

**Rationale:** Cleanest separation â€” mutable gate state (PHASE file) is physically separated from the hashed contract tree. No hash exclusion lists needed; gate-state/ is simply not included in the SHA-256 hash.

**Corollaries:**
- `gate-state/` directory created at repo root (not inside `contracts/`)
- `gate-state/PHASE` replaces `contracts/gate/PHASE`
- All L0-05 gate scripts that read/write PHASE are updated to reference `gate-state/PHASE`
- L0-00-T03 partition manifest adds `gate-state/` to the directory layout
- `lane-paths.tsv` gets a row `0	gate-state/**` (L0 owns gate-state)

---

## FD-056 â€” L3-B03: Python version for L3 reconciler

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L3-B03 (FD-005 vs L3-01 phase file contradiction)

**Decision:** Python 3.12 for the L3 reconciler â€” follow FD-005 system-wide mandate

**Rationale:** Consistent with the system-wide Python 3.12 mandate from FD-005. L3-01 phase file's 3.11 requirement was an oversight.

**Corollaries:**
- L3-01-diff-engine.md updated: all `python3.11`, `==3.11`, `python_requires=">=3.11"` changed to 3.12
- No FD-005 exception for L3
- `reconciler/pyproject.toml` heredoc in L3-01 uses `python_requires = ">=3.12"`

---

## FD-057 â€” L0-B02: rehearse.sh pass condition redesign

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L0-B02 (L0-05-T14 closing rehearsal permanently returns closed=0/12)

**Decision:** Baseline pass condition â€” T14 passes when the closure count does not regress from a stored first_failure baseline.

**Rationale:** A fresh repo starts at 0/12; T14 passes if count stays the same or improves. This makes the rehearsal meaningfully testable without requiring L0-IG-D1/D2/D3 to be closed first.

**Corollaries:**
- L0-05-T14 `rehearse.sh` script reads a stored baseline from `gate-state/rehearsal-baseline` (or equivalent)
- On first run: baseline is set to current closure count
- On subsequent runs: PASS if count >= baseline, FAIL if count < baseline (regression)
- The `first_failure` store lives in `gate-state/` (not `contracts/gate/` per FD-055)

---

## FD-058 â€” L1-D08: ai-toolchain.yaml and changes/*/scenarios/* ownership

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L1-D08 (charter says "Do not create"; L1-02-T16/T17/T18 build them)

**Decision:** Charter wins â€” L1 does NOT create ai-toolchain.yaml, changes/*, or scenarios/*

**Rationale:** Avoids scope creep; keeps L1 focused on schema validation.

**Corollaries:**
- L1-02-T16, L1-02-T17, L1-02-T18 are marked OUT-OF-SCOPE with comment referencing FD-058
- L1-06 does NOT assert STOP if these files are absent
- ai-toolchain.yaml, changes/*, scenarios/* remain outside L1's lane boundary
- If these artifacts are needed, a future FD designates a different owner

---

## FD-059 â€” L4-D05: bootstrap/ store count

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L4-D05 (lane-selfcheck.sh says 18 stores; L4-01-T03 creates 19)

**Decision:** bootstrap/ IS a store â€” 19 stores total

**Rationale:** bootstrap/ is a real data store created by L4-01-T03; excluding it from the count is arbitrary.

**Corollaries:**
- lane-selfcheck.sh --stores assertion updated: 18 â†’ 19
- L4-06 Â§2, L4-07, and all other documents that state the store count updated to 19
- DoD-1, P2 exit gate, L4-03-T301-E1 all updated to reference 19

---

## FD-060 â€” L5-B03: DoD validator approach

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L5-B03 (only 1 of 16 l5-validate.sh modes implemented)

**Decision:** Redesign DoD-01..16 proof commands to use the phase-file toolchain already built

**Rationale:** The phase-file toolchain (lane_tree_check.sh, validate_handoff.py, pytest) is already implemented. Redesigning proof commands to use it is lower effort than implementing 15 new l5-validate.sh modes.

**Corollaries:**
- L5-00-charter.md DoD-01..DoD-16 proof commands rewritten to use lane_tree_check.sh / validate_handoff.py / pytest
- l5-validate.sh remains with only --layout implemented (no new modes added)
- Each DoD row maps to a specific tool invocation from the phase-file toolchain

---

## FD-061 â€” L3-B06: Comparison-set cardinality

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L3-B06 (23/19/16 cardinality mismatch across charter/L3-01/L3-06)

**Decision:** 19 comparators â€” L3-01 phase file is authoritative (per FD-045)

**Rationale:** FD-045 already established phase files as canonical. L3-01 specifies 19 comparators. Charter and L3-06 counts are superseded.

**Corollaries:**
- L3-00-charter.md Â§7.1: change 23 â†’ 19 comparators
- L3-06: change 16 (or any other count) â†’ 19 comparators
- reconciler/checks/ directory holds exactly 19 check files
- All acceptance criteria asserting cardinality reference 19

---

## FD-062 â€” L5-H04-E05: Messaging channel for L5 routing integration tests

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L5-H04 E-05 (blocks L5-T41 routing integration test)

**Decision:** Default channel = `engineering-alerts`; channel is configurable via environment variable `L5_ROUTING_CHANNEL`

**Rationale:** `engineering-alerts` is a sensible default for a multi-product engineering platform. Making it configurable avoids hardcoding org-specific values into the lane files.

**Corollaries:**
- L5-T41 test uses: channel="${L5_ROUTING_CHANNEL:-engineering-alerts}"
- Channel name is documented in L5 charter Â§1.1 prerequisites (env var table)
- Escalation E-05 is resolved; L5-T41 unblocks

---

## FD-063 â€” L5-H04-E08: Private-path for L5-04-T02

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L5-H04 E-08 (blocks L5-04-T02 with no fallback)

**Decision:** Defer to Phase 1 â€” L5-04-T02 is marked BLOCKED-PENDING-E-08

**Rationale:** Private-path value depends on deployment configuration not yet established. Will be set during Phase 1 infrastructure setup.

**Corollaries:**
- L5-04-T02 is annotated: BLOCKED-PENDING-E-08 â€” private-path value set at Phase 1 deployment
- No placeholder path is hardcoded
- E-08 escalation is recorded as deferred; not an open decision requiring further input before Phase 1

---

## FD-064 â€” L3-B08: Pre-invented fixture data approach

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** L3-B08 annotation approach decision

**Decision:** Keep pre-invented content as DRAFT â€” annotate, do not delete

**Rationale:** Preserves draft work as a starting point. When DR-L3-05-A..E are answered, the draft becomes the basis for the final content.

**Corollaries:**
- CONTESTED sections in L3-06/L3-05 retain their content
- Each contested section has: <!-- DRAFT (DR-L3-05-X): content is invented; pending Founder decision -->
- DR-L3-05-A..E remain open L0 decisions (not answered in this session)
- The L3 mechanical fix agent annotates assertions that depend on this data as BLOCKED

---

## FD-065 â€” D-L4-01: L4 event-type identifiers vs L1 registry

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** D-L4-01 (blocks L4-04 merge, DoD-13)

**Decision:** Remap L4 source identifiers to existing L1 event types (option b)

**Rationale:** L4's source fields (`l4/event-log-records`, `l4/ci-run-records`, etc.) are internal aliases, not formal event-type identifiers. At implementation time, verify the 5 SIG store paths map to existing L1 event categories. No new registry entries needed.

**Corollaries:**
- `metrics/signals/sig-source-map.yaml` is updated at implementation time to map each SIG row to the corresponding existing L1 event-type identifier
- The 5 store paths (events/, records/deployments/, records/uat/, records/eval/, records/security-reviews/) are confirmed against L1 categories before merge
- If any store path genuinely has no L1 equivalent: escalate to option (a) for only that specific type
- `decisions/open-decisions.yaml` D-L4-01 marked RESOLVED with this decision recorded

---

## FD-066 â€” D-L4-02: Metric declarations publication path

**Date:** 2026-09-06  
**Session:** 11  
**Blocker resolved:** D-L4-02 (blocks L4-04 merge, DoD-13, DoD-20)

**Decision:** L4-scoped; L1 carries stable references only (option c)

**Rationale:** Most architecturally consistent with charter Â§3 prohibition on L4 writing to registries/**. Avoids two-source-of-truth problem; preserves L4 autonomy over metric evolution. The L4 metric-declarations.yaml is the authoritative register.

**Corollaries:**
- `registries/os-health.yaml` holds references (path/ID pointers) to `metrics/register/metric-declarations.yaml` â€” no L4 metric text is copied into L1
- The CCR diff script (`metric-declarations-diff.sh`) is a review artifact only â€” never a data-migration tool
- DoD-13 and DoD-20 clear when both `decisions/open-decisions.yaml` stubs show `status: RESOLVED`
- `decisions/open-decisions.yaml` D-L4-02 marked RESOLVED with this decision recorded

---

## FD-069 â€” GitHub org login confirmed: pareshp-org

**Date:** 2026-09-08  
**Session:** 12  
**Blocker resolved:** FD-068 ORG placeholder (ORG="" â†’ "pareshp-org"); FD-051 fully closed

**Decision:** The GitHub organization login is `pareshp-org`.

**Evidence:** Founder provided URL `https://github.com/pareshp-org` directly in session.

**Corollaries:**
- `contracts/project-config.sh`: `export ORG="pareshp-org"` â€” set immediately upon this decision
- FD-051 (paresh-org) closed: `pareshp-org` is the correct org; `paresh-org` is an unrelated org not controlled by `bendrohit-eng`
- All gh CLI calls that reference `$ORG` now resolve to `pareshp-org` at runtime via `project-config.sh`
- Phase 0 can proceed once `bendrohit-eng` confirms owner-level access to `pareshp-org` and purchases GitHub Team tier
- No files need editing for the org name â€” only `contracts/project-config.sh` holds the literal; everything else sources it

---

## FD-070 — bendrohit-eng confirmed owner of pareshp-org

**Date:** 2026-09-08  
**Session:** 12  
**Blocker resolved:** Phase 0 execution requirement (L0 must be org owner to run gh CLI org-setup commands)

**Decision:** `bendrohit-eng` is the owner of the `pareshp-org` GitHub organization.

**Evidence:** Founder confirmed directly in Session 12 chat.

**Corollaries:**
- Phase 0 can proceed: all gh CLI calls referencing `$ORG` and using `$GITHUB_TOKEN` (authenticated as bendrohit-eng) have full org-owner permissions
- No org transfer or invitation needed
- GitHub Team tier still needs to be purchased at github.com/organizations/pareshp-org/billing
- After Team tier: branch protection rulesets and CODEOWNERS enforcement become available (required by L0-P0-004, L0-P0-007)

---

## FD-071 — Q1: Task delivery to agent

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q1

**Decision:** A task is delivered to an agent by passing the lane file path together with the task ID. The task body lives at `tasks/<LANE>-<ID>.md` and is the detailed instruction carrier. The agent receives both; the lane file is the primary specification, and the task body path resolves deterministically from the ID. This is the task card format per `protocol/00`, and it is consistent with the L0-01 preamble dispatch model established in FD-030 (2026-09-03). No alternative delivery mechanism — inline task text, G3-style task cards as standalone files, or lane-pack §9 bundles — is valid.

**Corollaries:**
- All lane task bodies follow the `tasks/<LANE>-<ID>.md` naming pattern; no other path is used
- The Founder's dispatch loop always supplies: (1) the lane file path, (2) the task ID, and (3) optionally the resolved `tasks/<LANE>-<ID>.md` path as a convenience pointer
- Agents must not infer which task to run from context — the ID must be given explicitly
- FD-030 is confirmed and extended by this record; no revision to that decision is required

---

## FD-072 — Q2: Task-id grammar and branch grammar

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q2

**Decision:** The canonical task-id grammar is the two-part form `L<N>-<NNN>` (e.g., `L1-001`, `L0-P0-026`). This was established by FD-031 (2026-09-03) and remains canonical across all 845 plan IDs. The branch grammar is `lane/<N>/<descriptive-slug>` (e.g., `lane/1/repo-skeleton`, `lane/3/reconciler-core`). These two grammars together constitute the complete identifier space for the build; all six previously live ID schemes have been collapsed into this pair.

**Corollaries:**
- All task IDs across L1–L5 and L0 follow the two-part grammar; non-conforming IDs in existing documents are defects corrected during reconciliation
- D3-L1 (task-id scheme) and D1-L4 (task-id namespace) are superseded by and comply with this grammar
- Branch names take the form `lane/<N>/<slug>` with no other prefix; the integration branch is `integration` and the trunk is `main` (PARTITION.md §"Branch & merge model")
- FD-031 is confirmed; no change to that decision is required

---

## FD-073 — Q3: Execution model

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q3

**Decision:** The execution model is one session per task (session-per-task), as established by FD-032 (2026-09-03) and specified in `protocol/00-test-strategy.md` §3. A continuous executor is not used. Each agent invocation handles exactly one task ID and returns; the Founder's dispatch loop then opens a new session for the next task. This is the only execution model compatible with the AI-developer profile (PARTITION.md §"AI-developer profile"), which prohibits design decisions and cross-task state accumulation inside a single session.

**Corollaries:**
- Agents must treat each session as stateless with respect to prior sessions; no session may depend on in-memory state from a previous session
- Session outputs (files committed to the lane branch) are the only permitted state carrier between sessions
- The Founder is the dispatch loop; the Founder opens and closes each session
- FD-032 is confirmed; no change to that decision is required

---

## FD-074 — Q4: Ownership of verification/acceptance/**, tools/at/**, e2e/**, contracts/harness/**

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q4

**Decision:** Ownership is split as follows. L0 owns `e2e/**` and `contracts/harness/**`; this was established by FD-033 (2026-09-03) and is now implemented by task L0-P0-026, which authors `e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`, and `contracts/harness/pairs.tsv`. Each lane owns its own `tools/at/<lane-id>/` subtree — the lane that builds the artifact under test is the lane that owns the AT tooling for it. L0 owns `verification/acceptance/**` as a gate-artifact path; no lane may write to it without an L0 PR.

**Corollaries:**
- `lane-paths.tsv` carries explicit L0 rows for `e2e/**` and `contracts/harness/**`; neither resolves to `X` (UNASSIGNED) after L0-P0-026
- `tools/at/<lane-id>/` ownership rows appear in `lane-paths.tsv` under each lane's prefix; lane-guard enforces this per-lane boundary
- `verification/acceptance/**` is an L0-owned gate-artifact path; `at-coverage.sh` (L0-05-T05) reads from it and L0 is the sole writer
- REG-015 is closed by this ownership split (per FD-033); L0-IG-D2 and L0-IG-D5 are resolved by L0-P0-026
- FD-033 is confirmed and extended by this record

---

## FD-075 — Q5: Residual-ownership rule

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q5

**Decision:** L0 owns its own Phase-0 work. `lane-paths.tsv` is updated with explicit L0 carve-out rows so that every path L0 authors in Phase 0 resolves to lane `0` and not to `X` (UNASSIGNED). The lane-guard carve-out for `.github/workflows/lane-guard.yml` (one exact-file rule ordered before L2's prefix rule) was established by FD-003 and remains in force. The L0-P0-026 additions (`e2e/**`, `contracts/harness/**`) are covered by FD-074 above. After all carve-outs are applied, no L0-authored file may produce a lane-guard `UNASSIGNED` report.

**Corollaries:**
- `lane-paths.tsv` carries `0<TAB>.github/workflows/lane-guard.yml` above `2<TAB>.github/workflows/*` (FD-003 exact-file rule)
- `lane-paths.tsv` carries `0<TAB>e2e/**` and `0<TAB>contracts/harness/**` (L0-P0-026)
- `lane-paths.tsv` carries `0<TAB>contracts/**`, `0<TAB>docs/**`, `0<TAB>CODEOWNERS`, `0<TAB>Makefile` (existing L0 roots from PARTITION.md)
- `lane-guard.sh` must check that every file written in a lane PR resolves to a non-`X` owner before the PR is admitted; `UNASSIGNED` in any lane PR is a blocker
- FD-034 is confirmed; the L0-P0-026 additions extend but do not revise that decision

---

## FD-076 — Q6: Exit-code contract

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q6

**Decision:** The universal exit-code contract for all gate scripts is: `exit 0` = gate ARMED / check passed (green); `exit 1` = gate breached / check failed (red); `exit 2` = configuration error or unimplemented mode (the check did not run). This was established by FD-035 (2026-09-03). All scripts authored by L0-P0-026 (`e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`) and all scripts in `contracts/gate/**` follow this contract. The `exit 2` code is reserved exclusively for configuration errors — missing required inputs, unrecognised flags, or modes the script explicitly declines to implement — and is never used for logic failures, which must exit `1`.

**Corollaries:**
- Every gate script must emit its verdict as the last line on stdout and then exit with the appropriate code; absence of any stdout output is itself a failure (invariant 80)
- Scripts that previously inverted exit 0 and exit 1 are defects; all were corrected in Session 5 (mechanical bug fixes) and are not reintroduced
- Callers that check `$?` must distinguish `2` (configuration error — re-check inputs) from `1` (logic failure — re-run is not the fix)
- The `exit 0 = ARMED` convention is annotated in every script as `# exit 0 = gate ARMED (FD-035)` to make the inversion explicit to future readers
- FD-035 is confirmed; no change to that decision is required

---

## FD-077 — Q7: Negative-test apparatus

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q7

**Decision:** The canonical fixture layout for negative tests is `fixtures/invalid/<pair-id>/` where `<pair-id>` matches the contract-pair identifier (e.g., `CT-01`). The runner is `contract-tests.sh --negative-proof` mode, authored as part of L0-P0-026. This supersedes the `tests/fixtures/invalid/<schema-id>/` layout recorded in FD-036 (2026-09-03): the schema-id namespace was a preliminary form; the pair-id namespace is the form that aligns with the harness manifest `contracts/harness/pairs.tsv` and the `IG-04` battery. All four prior namespace variants in use across lanes must migrate to `fixtures/invalid/<pair-id>/` before the negative battery can produce `proven=24/24`.

**Corollaries:**
- `fixtures/invalid/<pair-id>/` is the sole valid path for negative-test fixtures; lane-guard rejects fixtures at any other path under `fixtures/invalid/`
- `contract-tests.sh --negative-proof` is the single negative-proof runner; no per-lane equivalent is created or permitted
- The `negative-battery.sh --gate integration --full` runner (L0-05-T08) reads from this canonical layout; `proven=0/24` is the expected baseline until lane fixtures are migrated
- FD-036 is superseded by this record on the fixture layout; the conclusion that exactly one apparatus exists is unchanged

---

## FD-078 — Q8: AT → owner-lane map authority

**Date:** 2026-09-08  
**Session:** 12  
**Gate:** Dispatch gate §5.1 Q8

**Decision:** `protocol/02-acceptance-mapping.md` is the authoritative AT-to-owner-lane map for all 37 in-scope acceptance tests. This was established by FD-037 (2026-09-03). Session 12 resolves the specific point of contention: L3 owns the `authority_delta` acceptance tests because L3 owns `validators/drift/**`, and `authority_delta` tests exercise the drift-detection validators that L3 builds. The 16-row disagreement between `protocol/00` and `protocol/02` is resolved in favour of `protocol/02` on all 16 rows. The `owner_lane` column of `contracts/gate/at-activation.tsv` is frozen from `protocol/02` §9.2 exclusively.

**Corollaries:**
- `contracts/gate/at-activation.tsv` (authored in L0-05-T04) sources its `owner_lane` column from `protocol/02` §9.2; no row may deviate from that source without an L0 decision record
- `authority_delta`-class ATs are assigned to L3 in `at-activation.tsv`; L3's lane suite must include the tooling to run them
- `protocol/00` AT-ownership rows are not authoritative; where they agree with `protocol/02` the agreement is coincidence, not dual authority
- FD-037 is confirmed and extended by this record; the Session 12 resolution of the `authority_delta` ownership is the net-new content

---

## FD-079 — Q9 (dispatch gate §5.1) · access-inputs.yaml shape — RE-DECIDED

**Decided:** 2026-09-08 · **Session:** 13 · **Band:** design · **Gates:** L5-02, L5-03
**Supersedes:** FD-038 (same question, opposite resolution)
**Question:** `contracts/access/access-inputs.yaml` shape — L5-02 publishes 5 keys, L5-03 reads 6.
**Answer:** L5-02's published shape is authoritative. The 6th key (`layer_b_admin_group`) that L5-03 reads is derived from context, not from the YAML contract. L5-03 must treat this key as optional with a documented default; L5-02 does not add a 6th key.

**Why this overturns FD-038.** FD-038 said "L5-02 adds `layer_b_admin_group` as the 6th key." That answer extends a frozen contract (`contracts/access/access-inputs.yaml` is frozen at Phase 0 under FD-013); extending it post-freeze is a CCR, not a task-level edit. The correct resolution is to keep the contract at 5 keys and have the consumer derive the missing value from a declared default — the same pattern used by every other L5 task that reads optional fields.

**Corollaries:**
- `contracts/access/access-inputs.yaml` retains exactly 5 top-level keys; no 6th key is added
- L5-03 task `L5-03-09` reads `access-inputs.yaml.layer_b_admin_group` as optional; if absent, falls back to `"${ORG}/layer-b-admins"` (the declared default, documented in L5-03's frozen inputs section)
- The comment in `L5-02` at lines 77-80 referencing FD-038's "6th key" is corrected: the key is not in the YAML; the default lives in L5-03 instead
- FD-038's corollary "L5-02's publish must be extended" is withdrawn by this record

---

## FD-080 — Q10 (dispatch gate §5.1) · Writer CLI canonical form — SUPPLEMENTED

**Decided:** 2026-09-08 · **Session:** 13 · **Band:** design · **Gates:** L1, L4
**Supplements:** FD-039 (same canonical form; this record adds the assert_rejects fix)
**Question:** Which writer CLI is canonical — positional or long-option? (`assert_rejects` currently vacuously green.)
**Answer:** Long-option is canonical per FD-031's two-part `L1-001` grammar: flags such as `--product`, `--type`, `--event` (L1) and `--store`, `--validate-only`, `--from-file` (L4). Positional arguments are rejected with a non-zero exit code. `assert_rejects` must assert a **concrete non-zero exit code value** — a bare `[ $? -ne 0 ]` is insufficient because any usage error (including an unrelated crash) satisfies it vacuously.

**Why the assert_rejects fix is required.** `protocol/04` §3 states: "a check that can only pass is not a check." `assert_rejects "positional-invocation"` currently passes on `exit 1` from a segfault or missing binary, not just from an intentional rejection. The paired negative must seed the exact refusal and confirm the exact exit code the CLI documents for bad-argument rejection (typically `exit 2`).

**Corollaries:**
- Every `assert_rejects` call in L1 and L4 suites is updated to assert the **documented rejection exit code** (e.g., `assert_exits_with 2 "record-write store id body"`) not merely any non-zero exit
- Positional invocations (`record-write <store> <id> <body>`) are removed from all task bodies, fixtures, and test harnesses
- L4-07's long-option form (`--store/--validate-only/--from-file`) is the canonical records-writer CLI shape
- L4-03's positional form is superseded by this ruling; any task body using it is a FIX_NOW item

---

## FD-081 — Q11 (dispatch gate §5.1) · `.github/workflows/build.yml` owner

**Decided:** 2026-09-08 · **Session:** 13 · **Band:** design · **Gates:** CODEOWNERS, L2
**Confirms:** FD-040 (same answer; this record adds the content-authority ruling)
**Question:** Who owns `.github/workflows/build.yml`? Three mutually exclusive contracts (`L2-01` job `build` + 5 actions; `L2-02` job `artifact` + 1; `L2-05` two jobs). Both writers use truncating `cat >`; the second merge silently wins.
**Answer:** **L2 owns `.github/workflows/build.yml`.** The canonical content is the `L2-05` two-job definition (FD-044: `L2-05-tasks.md` is the canonical L2 plan). `L2-01` and `L2-02` describe jobs that must be folded into `L2-05`'s single authoritative file; they do not independently author `build.yml`. L0's carve-out (FD-003) covers only `lane-guard.yml`; `build.yml` has no L0 ownership and no carve-out.

**Why three contracts conflicted.** `L2-01` and `L2-02` each contain a `cat > .github/workflows/build.yml` heredoc that overwrites whatever came before. Under a `cat >` write, the last task to run wins silently. FD-044 resolves the L2 plan conflict by making `L2-05` canonical; as a corollary, `L2-01` and `L2-02` must remove their `build.yml` writes and instead describe the job requirements that `L2-05` implements.

**Corollaries:**
- `CODEOWNERS`: `/.github/workflows/build.yml` is covered by the existing `/.github/workflows/**  @<lane2-reviewer>` line; no separate entry is needed
- `ownership.tsv` row `.github/workflows/**  2` already covers `build.yml`; no new row needed
- `L2-01` and `L2-02` heredocs that write `build.yml` are removed; replaced with prose specifications that `L2-05` implements
- The L1-claims on build.yml (if any) are likewise withdrawn — L1 does not own any `.github/workflows/` file

---

## FD-082 — Task-ID Grammar: No T Infix (PFD-008)

**Decided:** 2026-09-08 · **PFD:** PFD-008 · **Band:** design · **Gates:** all lane documents, CI task-id checks
**Status:** DECIDED

**Answer:** **Option A** — `L<N>-<FF>-<NN>` (no `T` infix). Effective immediately.

FD-072's ruling is confirmed and extended. The charter format (`L0-00-T01`, with `T` infix between file-number and task-number) and the lane-file prefix format (`T-L1-04-01`) are both retired. A single sed pass normalises all ~845 task-ID instances across charter and plan files; this action is required before Phase 1 dispatch.

**Actions required:**
- Run one sed pass across all lane documents to normalise `T`-infix and `T-` prefix occurrences to the `L<N>-<FF>-<NN>` form
- Update format-validation regexes and CI task-id checks to accept only `L<N>-<FF>-<NN>`
- Concordance tooling updated to the single canonical grammar

---

## FD-083 — Five Lane Reviewer GitHub Logins (PFD-009)

**Decided:** 2026-09-08 · **PFD:** PFD-009 · **Band:** infra · **Gates:** CODEOWNERS finalisation, branch-protection reviewer assignment
**Status:** DECIDED

**Answer:** All five lane reviewer slots are assigned to **`bendrohit-eng`** for bootstrap. Replace `@LANE1_REVIEWER` through `@LANE5_REVIEWER` in `CODEOWNERS` with `@bendrohit-eng`. Swap to individual logins before Phase 1 dispatch when team members are onboarded to `pareshp-org`.

**Actions required:**
- Replace `@LANE1_REVIEWER` through `@LANE5_REVIEWER` in CODEOWNERS with `@bendrohit-eng`
- Record the swap-out trigger: before Phase 1 dispatch, each reviewer slot is updated to the named team-member login

---

## FD-084 — L2 Branch-Model Definitions: Integration, Promotion, Release (PFD-010)

**Decided:** 2026-09-08 · **PFD:** PFD-010 · **Band:** L2 design · **Gates:** L2 merge-criteria automation, L2-05 task reconciliation
**Status:** DECIDED

**Answer:** **Option A** — `L2-05-tasks.md` definitions are canonical for integration, promotion, and release. Rewrite conflicting definitions in L2-01, L2-03, and L2-04 phase files to match `L2-05`. No new contracts file is introduced. Consistent with FD-044 (L2-05 is the authoritative L2 plan).

**Actions required:**
- Rewrite D-L2-07, D-L2-08, and D-L2-09 definitions in L2-01/L2-03/L2-04 to match L2-05-tasks.md
- Phase files become reference/design-note files; their definition text is replaced with a pointer to L2-05

---

## FD-085 — L2 Task-ID Namespace: Retire L2-P*-T* IDs (PFD-011)

**Decided:** 2026-09-08 · **PFD:** PFD-011 · **Band:** L2 design · **Gates:** L2 executor routing, concordance tooling
**Status:** DECIDED

**Answer:** **Option A** — retire all `L2-P*-T*` IDs from phase files entirely. Replace each with a `[retired — see L2-T<nnn>]` stub. Only `L2-T*` IDs (from `L2-05-tasks.md`) constitute the live executable namespace. Downstream of FD-044.

**Actions required:**
- Replace every `L2-P*-T*` heading in phase files with a `[retired]` stub referencing the corresponding `L2-T*` ID
- Verify that concordance tooling, task-lookup tooling, and executor routing exclude the retired namespace

---

## FD-086 — L2 Actor-Gate Canonical Form (PFD-012)

**Decided:** 2026-09-08 · **PFD:** PFD-012 · **Band:** L2 CI · **Gates:** L2 CI workflow wiring, L2 gate-check automation
**Status:** DECIDED

**Answer:** **Option A** — shell script `scripts/actor-gate.sh` per L2-05. L2-06 tests are unchanged and continue to assert the shell-script form. The branch-protection rule form (L2-01) and YAML workflow-step form (L2-03) are superseded. Consistent with FD-044 (L2-05 authoritative).

**Actions required:**
- L2-01 and L2-03 actor-gate definitions annotated as superseded; L2-05 form is the implementation target
- L2-06 acceptance tests left as-is (they already test the shell-script form)

---

## FD-087 — L3 Bootstrap: Split L3-04 into Dry-Run + Live Tasks (PFD-013)

**Decided:** 2026-09-08 · **PFD:** PFD-013 · **Band:** L3 bootstrap · **Gates:** L3-04 executability, L3 Phase 0 dispatch
**Status:** DECIDED

**Answer:** **Option C** — split L3-04 into two tasks. Task 1 (dry-run) runs during bootstrap and exercises all provisioning logic against a mock or sandbox; Task 2 (live) runs after the bootstrap constraint lifts and performs actual GitHub org API calls against `pareshp-org`. The §0.4 prohibition in L3-06 remains in force for the bootstrap phase; it is satisfied by the split rather than removed.

**Actions required:**
- L3-04 is split: the dry-run task executes during bootstrap; the live task is gated on the bootstrap-constraint-lifted signal
- Task IDs for both parts follow the `L3-<FF>-<NN>` grammar (FD-082)
- L3-06 §0.4 annotation updated to note that the live-org task is explicitly post-bootstrap

---

## FD-088 — L3 tools/provision Package Layout (PFD-014)

**Decided:** 2026-09-08 · **PFD:** PFD-014 · **Band:** L3 package · **Gates:** L3 package authoring
**Status:** DECIDED

**Answer:** **Option A** — L3-06 layout: one subdirectory per tool under `tools/provision/` (`tools/provision/{comparator,canary,orphan,create-product}/`). The phase-file `lib/` + `bin/` split is retired. Consistent with FD-045 (L3-06-tasks.md authoritative) and FD-098 below.

**Actions required:**
- All L3 provisioning tooling authored under `tools/provision/<tool>/` (one subdirectory per tool)
- Phase-file `lib/` and `bin/` path references rewritten to the L3-06 subdirectory layout
- `pyproject.toml` package names and test fixture paths follow the subdirectory layout

---

## FD-089 — L3-06 Fixture-A: Reject Invented Schema Fields (PFD-015)

**Decided:** 2026-09-08 · **PFD:** PFD-015 · **Band:** L3 test validity · **Gates:** L3 test suite trustworthiness
**Status:** DECIDED

**Answer:** **Option B** — reject all five invented fields. Rewrite `fixture-a` to use only currently ratified schema fields. DR-L3-05-A through DR-L3-05-E are explicitly deferred; the five fields (`capability.scope`, `capability.ttl`, `person.lane_assignments[]`, `product.phase_gate`, `registry.version_policy`) are not added to any L1 schema. Tests built against the rewritten fixture will be trustworthy.

**Actions required:**
- Rewrite `fixture-a` in L3-06 to use only fields present in ratified `schemas/registry/*.v1.schema.json`
- DR-L3-05-A through DR-L3-05-E marked explicitly deferred in `PENDING_FOUNDER_DECISIONS.md` with reference to FD-089
- Any test assertion that depended on the five invented fields is rewritten or removed

---

## FD-090 — L4 FTE Not Re-Applied at Day Level (PFD-016)

**Decided:** 2026-09-08 · **PFD:** PFD-016 · **Band:** L4 capacity · **Gates:** Rule R6 of scheduled-availability.py (L4-T406)
**Status:** DECIDED

**Answer:** **Option B** — the declared schedule span is the full per-day availability; `fte` is not re-applied at the day level. Record `fte_application: none` in `calibration.yaml`. The scheduled-availability derivation is: `scheduled_hours = (end − start)` with no `fte` multiplier applied inside the day calculation.

**Actions required:**
- `calibration.yaml` gains key `fte_application: none`
- Rule R6 of `scheduled-availability.py` (L4-T406) implements Option B semantics
- Comments in the rule document Option B and reference FD-090

---

## FD-091 — L4 Ready-Queue-Miss Event: Hold Until Cause Fields Answered (PFD-017)

**Decided:** 2026-09-08 · **PFD:** PFD-017 · **Band:** L4 events · **Gates:** --emit path of rqm-detect (L4-T417)
**Status:** DECIDED

**Answer:** **Option A** — hold the event until all cause-prompt fields are answered. Never fabricate cause fields. The event is not appended until `queue_empty_reason`, `team_lead_blocked`, and `priority_changed_recently` are supplied by the Team Lead through the cause prompt. This preserves the integrity of the §97.5 field set.

**Actions required:**
- `rqm-detect --emit` blocks until all eight §29.4 fields are present; it does not emit a partial record
- No null/empty placeholder values are written into the event store for cause fields
- Documentation in L4-T417 updated to state the hold-until-complete behaviour explicitly

---

## FD-092 — L4 Working Calendar: Fixed Filename (PFD-018)

**Decided:** 2026-09-08 · **PFD:** PFD-018 · **Band:** L4 capacity · **Gates:** Rule R4 of scheduled-availability.py (L4-T406)
**Status:** DECIDED

**Answer:** **Option A** — fixed filename convention. The canonical company working calendar is `records/leave/company-calendar.yaml`. Readers select it by that exact path; no version-comparison or date-comparison logic is required.

**Actions required:**
- Rule R4 of `scheduled-availability.py` reads the calendar from `records/leave/company-calendar.yaml`
- `leave.schema.json` documents that `company-calendar.yaml` is the well-known calendar record
- Any future calendar update replaces the file at that fixed path (no version suffixes)

---

## FD-093 — L4 Owns Subsystem P: Capacity Profile (PFD-019)

**Decided:** 2026-09-08 · **PFD:** PFD-019 · **Band:** partition · **Gates:** PARTITION.md, capacity_profile_eligible consumer
**Status:** DECIDED

**Answer:** **Option A** — L4 owns subsystem P. Capacity planning is a metric aggregate, and L4 is the metrics lane. L4 is the consumer that must honour the `capacity_profile_eligible`, `workload_state_eligible`, and `founder_view_eligible` flags emitted by `derive.py`.

**Actions required:**
- `PARTITION.md` updated: subsystem P assigned to L4
- `lane-paths.tsv` gains an L4 row covering the Capacity Profile path
- `metrics/attention/HANDOFF-P.md` (L4-T413) updated to name L4 as the subsystem P owner
- CODEOWNERS updated accordingly

---

## FD-094 — L1 Validator Engine: Option B CLI Design (PFD-001)

**Decided:** 2026-09-08 · **PFD:** PFD-001 · **Band:** L1 · **Gates:** L1-02, L1-04, L1-05, L1-07
**Status:** DECIDED

**Answer:** **Option B** — L1-03 design. Entry point: `validators/registry/cli.py`, invoked as:

```
python -m validators.registry.cli --root <path> --as-of <date> --records-root <path> --format json --rule Rxx
```

Exit codes: `0` = all rules pass; `1` = one or more rules fail; `2` = configuration / invocation error. Rules R01–R18. Option D is superseded.

**Actions required:**
- Write `contracts/validator-contract.md` documenting the CLI grammar, exit codes, and rule registry
- Rewrite all validator references in L1-02, L1-04, L1-05, and L1-07 against the Option B grammar
- Option D forms (if present in any task body) are replaced with Option B forms

---

## FD-095 — L1 Dispatch Surface: L1-05-tasks.md Sole Dispatch (PFD-002)

**Decided:** 2026-09-08 · **PFD:** PFD-002 · **Band:** L1 · **Gates:** L1 executor routing
**Status:** DECIDED

**Answer:** **Option A** — `L1-05-tasks.md` is the sole dispatch surface. All 127 task bodies are absorbed under the `L1-{nnn}` scheme. Phase documents (`L1-01`, `L1-02`, `L1-03`, `L1-04`, `L1-06`, `L1-07`) become reference and design-note files; their task bodies do not execute.

**Actions required:**
- Every L1 phase-file task body is either (a) already present in L1-05-tasks.md under an `L1-{nnn}` ID, or (b) added to L1-05 before Phase 1 dispatch
- Phase files annotated as reference/design-note only; executor routing ignores them

---

## FD-096 — L1 Schema Layout: Flat schemas/registry/ (PFD-003)

**Decided:** 2026-09-08 · **PFD:** PFD-003 · **Band:** L1 · **Gates:** L1-02 §0.1, L1-05 FILES fields, L1-03-T08 STOP rule
**Status:** DECIDED

**Answer:** **Option A** — flat layout: `schemas/registry/<name>.v1.schema.json`. One file per schema entity; no subdirectory nesting within `schemas/registry/`.

**Actions required:**
- Fix L1-02 §0.1 path references to the flat layout
- Fix all L1-05 FILES fields that reference a nested layout
- Fix L1-03-T08 STOP rule to test against the flat layout
- All schema `$id` URNs (per FD-050) remain unchanged; only the file-system path changes to flat

---

## FD-097 — L2 Canonical Plan Confirmed: L2-05-tasks.md (PFD-004)

**Decided:** 2026-09-08 · **PFD:** PFD-004 · **Band:** L2 · **Gates:** L2-06, D-L2-07/08/09 reconciliation
**Status:** DECIDED

**Answer:** **Option A confirmed** — `L2-05-tasks.md` is authoritative. FD-044 is confirmed. Authorise the id-renumbering cleanup: resolve the L2-T500–T525 collision, re-point L2-06 against the renumbered IDs, and reconcile D-L2-07, D-L2-08, D-L2-09.

**Actions required:**
- Resolve L2-T500–T525 collision (renumber or retire conflicting IDs)
- Re-point L2-06 acceptance tests against the post-renumbering L2-05 IDs
- D-L2-07, D-L2-08, D-L2-09 reconciliation completed per FD-084

---

## FD-098 — L3 Canonical Plan Confirmed: L3-06-tasks.md (PFD-005)

**Decided:** 2026-09-08 · **PFD:** PFD-005 · **Band:** L3 · **Gates:** L3 phase-file task-body removal
**Status:** DECIDED

**Answer:** **Option A confirmed** — `L3-06-tasks.md` is authoritative. FD-045 is confirmed. Ratify the additions L3-P0-CMP10, L3-P0-CMP12, L3-P0-AT001, and L3-P0-DEL14. Authorise removal of superseded task bodies from phase files (they become reference/design-note files).

**Actions required:**
- L3-P0-CMP10, CMP12, AT001, DEL14 additions ratified and retained in L3-06
- Phase-file task bodies that duplicate L3-06 entries are removed; phase files become reference/design-note files
- Phase-file task bodies not yet in L3-06 are assessed for inclusion before Phase 1 dispatch

---

## FD-099 — L5 Drills Executor and Window (PFD-007)

**Decided:** 2026-09-08 · **PFD:** PFD-007 · **Band:** L5 · **Gates:** L5 drill scheduling
**Status:** DECIDED

**Answer:** `bendrohit-eng` is the executor for all L5 drills. Drill window is unrestricted (no blackout period for bootstrap). The first product executed in criticality order runs the disruption drill. PFD-006 (break-glass second owner for drills) remains DEFERRED — it is not answered by this record.

**Actions required:**
- L5 drill task bodies updated to name `bendrohit-eng` as executor
- Drill scheduling documentation updated: no window restriction during bootstrap
- PFD-006 remains in PENDING_FOUNDER_DECISIONS.md as a separate open item

---

## FD-100 — Registry File Location: Directory-Per-Item under registries/ (PFD-020)

**Decided:** 2026-09-08 · **PFD:** PFD-020 · **Band:** L1 · **Gates:** L1 registry authoring, make build outputs
**Status:** DECIDED

**Answer:** **Option A** — directory-per-item under `registries/`. Each registry item lives at `registries/<entity>/<id>/`. Root-named flat files (e.g., `registries/people.yaml`) are `make` build outputs assembled from the directory tree; they are never committed to the repository. L1 owns the source directory trees.

**Actions required:**
- `lane-paths.tsv`: L1 owns `registries/**` source trees
- `Makefile` build targets produce root-named assembled files as outputs only; no root-named file is committed
- CODEOWNERS updated: `registries/**` routes to L1 reviewer

---

## FD-101 — Git Conventions: master/02 and master/09 (PFD-021)

**Decided:** 2026-09-08 · **PFD:** PFD-021 · **Band:** all lanes · **Gates:** commit-msg hook, BLOCKER template
**Status:** DECIDED

**Answer:** **Option A**. Merge method, staging, and branch creation follow `master/02`. Commit message format follows `master/09` §5.1. Canonical blocker escalation template is `docs/escalation/BLOCKER.md`. The commit-msg hook moves from L0's local toolchain to lane-guard CI.

**Actions required:**
- All lane task bodies reference `master/02` for branch/merge conventions and `master/09` §5.1 for commit message format
- `docs/escalation/BLOCKER.md` authored as the canonical blocker template (L0-owned path)
- Commit-msg hook wired into lane-guard CI (not run locally as a git hook)

---

## FD-102 — Branch Protection: Rulesets-Only, Empty Phase-0 Check List (PFD-022)

**Decided:** 2026-09-08 · **PFD:** PFD-022 · **Band:** infra · **Gates:** L0-P0-004, L0-P0-007
**Status:** DECIDED

**Answer:** **Option A** — rulesets-only (no legacy branch protection rules). The Phase-0 required-check list on every repository is empty at creation time. The `lane-guard` required check is added on first-run day only (not at repo creation).

**Actions required:**
- Repository creation scripts configure rulesets only; no legacy branch-protection API calls
- Phase-0 ruleset: required-status-checks list = `[]`
- `lane-guard` required check added to the ruleset on the first day `lane-guard.yml` fires (post-L2 Phase 1)

---

## FD-103 — Unowned Paths: Assign All 16 to Nearest Lane (PFD-023)

**Decided:** 2026-09-08 · **PFD:** PFD-023 · **Band:** partition · **Gates:** PARTITION.md freeze, CODEOWNERS
**Status:** DECIDED

**Answer:** **Option A** — all 16 previously unowned paths are assigned to the nearest lane in one versioned re-freeze commit. Rows b, h, and j are transcribed from FD-002 (the subsystem assignments recorded there). The commit touches `PARTITION.md`, `lane-paths.tsv`, and `CODEOWNERS` atomically.

**Actions required:**
- One versioned re-freeze commit assigns all 16 paths; no path remains with `X` (UNASSIGNED) after the commit
- Rows b/h/j assignments follow FD-002 (H→L5, O-registry→L1, O-jobs→L3)
- Lane-guard validates zero UNASSIGNED rows after the freeze commit

---

## FD-104 — Record Write Interface: REST Contents API with GitHub App Token (PFD-024)

**Decided:** 2026-09-08 · **PFD:** PFD-024 · **Band:** L4 · **Gates:** records/deployments/, records/uat/, records/restore-tests/, records/eval/, events/
**Status:** DECIDED

**Answer:** **Option A** — REST Contents API (GitHub's `/repos/{owner}/{repo}/contents/{path}` endpoint) with GitHub App installation token. Hand-edit control: `validate-human-record.sh` is a required status check on any PR touching the record paths listed below. Automated writes use the App token; human writes must pass the validation check.

**Record paths covered:** `records/deployments/`, `records/uat/`, `records/restore-tests/`, `records/eval/`, `events/`

**Actions required:**
- Record-writer CLI (L4) uses the REST Contents API with a GitHub App installation token
- `validate-human-record.sh` added as a required status check on the five record paths
- No direct git push to record paths is permitted outside the CLI

---

## FD-105 — Reconciler Identity: GitHub App Installation Token (PFD-025)

**Decided:** 2026-09-08 · **PFD:** PFD-025 · **Band:** L3 · **Gates:** reconciler identity, derived/ allowlist
**Status:** DECIDED

**Answer:** **Option A** — GitHub App installation token is the reconciler's identity. Ratify anchor `derived/anchors/records-head.yaml`. The reconciler's write allowlist is `[derived/**]`; it may not write outside this path.

**Actions required:**
- L3 reconciler task bodies specify GitHub App installation token as the runtime identity
- `derived/anchors/records-head.yaml` is authored and committed as the reconciler's state anchor
- `contracts/` (or equivalent) documents the allowlist `[derived/**]` as the reconciler write boundary

---

## FD-106 — Seeded Canary: people.yaml _canary Field (PFD-026)

**Decided:** 2026-09-08 · **PFD:** PFD-026 · **Band:** L3 · **Gates:** CMP-01, CMP-03 canary detection
**Status:** DECIDED

**Answer:** The seeded canary lives in `people.yaml`, field `_canary`, with label value `__CANARY__`. CMP-01 and CMP-03 both read `people.yaml`; the canary row will be detected by both comparators as part of their normal operation.

**Actions required:**
- `people.yaml` gains a `_canary: __CANARY__` field in the bootstrap fixture
- CMP-01 and CMP-03 acceptance criteria assert that the canary row is detected and reported
- Canary detection is a required assertion in the L3 comparator test suite

---

## FD-107 — Security/SBOM Tools: Trivy + Syft (PFD-027)

**Decided:** 2026-09-08 · **PFD:** PFD-027 · **Band:** L2/L5 · **Gates:** CI security scan jobs, SBOM generation
**Status:** DECIDED

**Answer:** **Trivy** for security scanning (two jobs: image scan + dependency scan). **Syft** for SBOM generation, `spdx-json` output format. Both tools pinned by sha256 digest to the latest stable release at implementation time.

**Actions required:**
- Two Trivy jobs added to the CI workflow (image scan + dependency scan)
- One Syft job added for SBOM generation, outputting `spdx-json`
- Both tool invocations pin the container/binary sha256 digest at implementation time; the digest is recorded in `contracts/` or a pinning manifest

---

## FD-108 — Orphan Detection Surfaces: 5 Accepted Defaults (PFD-028)

**Decided:** 2026-09-08 · **PFD:** PFD-028 · **Band:** L1/L3 · **Gates:** orphan detection tooling
**Status:** DECIDED

**Answer:** Five orphan detection surfaces are accepted as the V1 defaults:

| Surface | Path | Field |
|---|---|---|
| (a) Asset inventory | `docs/assets/asset-list.yaml` | `asset_id` |
| (b) Delegation records | All delegation types where "Expires cleanly" ≠ "Only by reassignment" | expiry field |
| (c) Board snapshot | `records/board/snapshot.yaml` | — |
| (d) Open work | `records/work/open.yaml` | — |
| (e) Commitments | (any record with `commitments[]`) | `commitments[].owner` |

Publish the accepted set as `contracts/orphans/decisions.yaml`.

**Actions required:**
- `contracts/orphans/decisions.yaml` authored listing the five surfaces with their paths and fields
- Orphan-detection tooling (L1/L3) targets exactly these five surfaces in V1
- Additional surfaces require a new FD to add them

---

## FD-109 — Bootstrap Exception Path: registries/exceptions/<id>/exception.yaml (PFD-029)

**Decided:** 2026-09-08 · **PFD:** PFD-029 · **Band:** L1 · **Gates:** §95.3 Gate 1, bootstrap exception workflow
**Status:** DECIDED

**Answer:** **Option A**. Path is forced by FD-100 (directory-per-item): `registries/exceptions/<id>/exception.yaml`. §95.3 Gate 1 compensating controls: `validate-human-record.sh` (required status check) plus CODEOWNERS approval by `bendrohit-eng`.

**Actions required:**
- Bootstrap exception records written to `registries/exceptions/<id>/exception.yaml`
- `validate-human-record.sh` is a required check on `registries/exceptions/**` PRs
- CODEOWNERS: `registries/exceptions/**` requires approval from `bendrohit-eng`

---

## FD-110 — Build Start Date and Product Placeholders (PFD-030)

**Decided:** 2026-09-08 · **PFD:** PFD-030 · **Band:** all lanes · **Gates:** bootstrap-exception dates, restore rotation, asset gate
**Status:** DECIDED

**Answer:** Build-track start date is **2026-09-08**. Eight products are named `Product-1` through `Product-8` as placeholders; replace with real product names before Phase 1 dispatch in criticality order. S19 rides F9; the denominator stays 72.

**Corollaries:**
- Bootstrap-exception `start` and `expiry` dates are measured from 2026-09-08
- The 90-day restore rotation and "roughly month 3" asset gate are measured from 2026-09-08
- `Product-1` through `Product-8` are the dispatch names until replaced by the Founder

---

## FD-111 — Board Layout and Scorecard (PFD-031)

**Decided:** 2026-09-08 · **PFD:** PFD-031 · **Band:** L4/L5 · **Gates:** §99.5 board automation, scorecard alert
**Status:** DECIDED

**Answer:** **Option A** — one org-level GitHub Project with a product field (forced by §99.5). Scorecard drop alert threshold: a drop of ≥ 0.5 versus the previous scan over a 30-day rolling window. Estimate-exempt task classes: `[normal, spike, incident, debt-remediation]`.

**Actions required:**
- GitHub Project created at org level with a `product` single-select field
- Scorecard alert job fires when the score drops ≥ 0.5 vs the previous scan in the 30-day window
- `calibration.yaml` or equivalent records the threshold and exempt classes

---

## FD-112 — DevLake V1: Deferred (PFD-032)

**Decided:** 2026-09-08 · **PFD:** PFD-032 · **Band:** L5 · **Gates:** SIG-04, SIG-07, SIG-08, SIG-40
**Status:** DECIDED

**Answer:** DevLake is **deferred** from V1 scope. Write `contracts/v1-scope.yaml` with an explicit deferral entry. Direct L5 to revert the DevLake stack entry in `ops-vm/stack/compose.shared.yml`. Signals SIG-04, SIG-07, SIG-08, and SIG-40 are recorded as deferred with trigger date TBD by L0.

**Actions required:**
- `contracts/v1-scope.yaml` gains a deferral entry for DevLake with reference to FD-112
- L5 reverts any DevLake service definition from `ops-vm/stack/compose.shared.yml`
- SIG-04, SIG-07, SIG-08, SIG-40 entries in the signal register updated: `status: deferred`, `trigger_date: TBD (L0 decision)`
