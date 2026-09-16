# L0-04 — THE DECISION REGISTER

**Lane:** L0 Integrator · **Executor:** the human lead (this file is not executed by an AI developer)
**Branches:** `integration` (PARTITION.md §"Branch & merge model")
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — this file never contradicts it.
**Closes:** `master/INDEX.md` OPEN ITEM **G-3** (*"No single decision log … L0 cannot answer 'what is still open?' from the set"*) and conflict **C-24** (*"Five parallel decision registers with overlapping content and no cross-references"*).

> **Reading rule for lanes L1–L5.** Two things here are binding on a lane executor and nothing else is:
> §3 — the register itself, which is where you look up the `REG-` id for the decision your task is blocked on — and
> §4.2's rule that **you cite the `REG-` id in the blocker, never only the source id you found in your own lane
> file**. A lane never edits `docs/decisions/**`, never adds a register row, never closes one, and never treats an
> entry's "in force until answered" line as permission to choose something else. Waiting is correct behaviour;
> guessing is not (`L0-00-charter.md` §7.3).

---

## 0. What this file is, and the one thing it must not become

Fifty-seven plan documents raise open decisions. They do it in **more than twenty incompatible id spaces** —
`D-PLAN-nn`, `LA-nn`, `D-REQ-n`, `DECISION n`, `D-EE-n`, `V1-Dn`, `DEC-nn`, `D-08-n` in `master/`; `L1-Dnn`,
`DR-L1-06-x`, `DECISION-L1-02-x`, `D-L2-nn`, `L2/P1/DEC-x`, `D-L3-nn`, `DEC-L3-02-nn`, `DR-L3-05-x`, `DR-3.n`,
`L3-Dn`, `DR-L3-07-x`, `D-L4-nn`, `D-L4-Pn-nn`, `D-L4-TL-n`, `DR-L0-07-x`, `L0-IG-Dn` in `lanes/`. Several ids
collide outright: `D-L2-07`, `D-L2-08` and `D-L2-09` each name **three different decisions** across three Lane 2
files, and `D-L4-01`/`D-L4-02`/`D-L4-03` each name **two** — a collision Lane 4 recorded against itself as
`D-L4-TL-2` and could not fix, because renumbering another document is a foreign-path act. Several decisions are
raised **thirteen times** under thirteen ids: "who owns subsystems G, H, J, O and P" is `D-PLAN-01`+`D-PLAN-02`,
`LA-01`, `D-REQ-4`, `DECISION 1`, `D-EE-2`, `V1-D1`+`V1-D2`, `DEC-01`, `L1-00` DR #2, `L0-IG-D3`+`L0-IG-D4`,
`D-L2-12`, `D-L4-P4-04`, `D-L4-P5-03` and `protocol/02` §2.

**This file is the one register.** It assigns every real open decision a single stable `REG-` id, records who
decides it, what it blocks by lane and task id, the options with their trade-offs, and the phase it gates. §5 is
the concordance: every source id in every plan file mapped to its `REG-` id, so a lane that finds `DR-L3-05-C` in
its own file can resolve it here without knowing this file existed.

**The thing it must not become is a decision-maker.** This file records prompts and their option sets. It closes
nothing. Closure is a dated decision record under `records/decisions/` written by L0 through the `record-decision`
CLI (§97.2); the register row then points at it. A register that closed its own entries would be the failure
`L0-00-charter.md` §3 reserves against: the party bound by a decision writing the decision.

**Two entries outrank everything else in this file and are stated first, at §3.1:**
**REG-001**, the partition gap — subsystems **G**, **H**, **J**, **O** and **P** are assigned to no lane in
PARTITION v1 — and **REG-002**, the lane-guard circularity — the CI check that enforces the partition lives under
`.github/workflows/**`, which the partition gives exclusively to **L2**, one of the five lanes it judges. Neither
is re-litigated here. Both are recorded with every option their raisers stated, and both are `P0`.

---

## 1. Shell and repository conventions

POSIX `sh` / Git Bash, run from the control-plane repository root. Identical to `L0-00-charter.md` §1,
`L0-03-merge-train.md` §1 and `L0-05-integration-gate.md` §1.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
cd "$CP_ROOT"
git rev-parse --show-toplevel
```

| Symbol | Meaning | Set by |
|---|---|---|
| `$CP_ROOT` | local clone of `control-plane` | you, once per shell |
| `$CPR_ROOT` | local clone of `control-plane-records` (PARTITION.md §"Repositories") | you, once per shell |
| `$PHASE` | the Section 98 phase token the programme currently stands at — `Ph0`…`Ph7`, `EH`, `G1`…`G8`, `P1`…`P8` | `contracts/gate/PHASE`, task `L0-05-04` |

Every path this file writes is inside `docs/decisions/`, which is inside `docs/**`, which PARTITION.md gives to L0
exclusively. **This file writes nothing anywhere else.** It does not extend `lane-paths.tsv` (that is `L0D-04`), it
does not edit `contracts/**` (that is the Phase-0 freeze and `L0D-06`), and it creates no workflow.

---

## 2. L0 decisions held in this file

Plan-local ids in the style of `L0-02-lane-guard.md` §11 and `L0-05-integration-gate.md` §4. They never collide
with Appendix A's `D1`…`D112`.

| Id | Decision | Why | Anchor |
|---|---|---|---|
| **L0D-DR-1** | The register's stable id space is `REG-001`…`REG-060`, allocated **once** and never reused, renumbered or reordered. A retired entry keeps its id and takes state `withdrawn` | §97.3's rule for the event enum applied to decision ids: *"never renamed once shipped"*. Every lane file, blocker issue and decision record citing a `REG-` id must still resolve years later | §97.3; §97.2 |
| **L0D-DR-2** | The **source of truth is one L0-owned TSV**, `docs/decisions/register.tsv`; the per-entry markdown under `docs/decisions/open/` is **rendered** from it and never hand-edited | The pattern `L0-06-bootstrap-mode.md` §7 already uses for `docs/bootstrap/gate-register.tsv`. PARTITION rule 3 forbids a **shared** mutable file; this file has exactly one writer, L0, and no lane may open it | PARTITION rule 3; `L0-06` §7 |
| **L0D-DR-3** | The **open prompt** lives in `docs/decisions/` (control-plane, L0-owned). The **closure** lives in `records/decisions/` (control-plane-records) and is written by the `record-decision` CLI, never by hand | `L0-00-charter.md` §5 states it: *"every closure is written as a decision record under `records/decisions/` using the §97.2 schema, and every open prompt as a record under `records/decisions/pending/`"*. F-11 forbids hand-editing any record | §97.2; F-11 |
| **L0D-DR-4** | A row's `state` is one of exactly four: `open`, `closed`, `declined`, `withdrawn`. `declined` carries the gate answers, the forgone capabilities and a review date | §98.1: *"Declined is a state, not an absence."* An entry that is neither answered nor declined is `open` and stays visible; there is no "assumed" state and no "probably fine" state | §98.1; L0D-20 |
| **L0D-DR-5** | Every entry carries a **gating phase token** and a **priority band** `P0`…`P3` | `L0-00-charter.md` §8.2's midweek standing decision window (§94.6, D79) needs an ordering to work through; without one the register is a list, not a queue | §94.6; D79 |
| **L0D-DR-6** | An entry's **"in force until answered"** line is transcribed from the raising document in substance and is **never invented here**. Where the raiser stated no interim behaviour the line reads `none — the blocked task STOPs` | A file that invented interim behaviours would be choosing on five lanes' behalf, which `L0-00-charter.md` §6.2 `C-08` forbids a lane from doing and which L0 must not do informally either | C-08; PARTITION §"AI developer profile" |
| **L0D-DR-7** | The register is **not** a required status check and is **not** added to branch protection. Its gate is the local `make decisions-gate`, run inside `make promote-check` | F-07: the required-check list starts empty per repository and grows only as each check comes into existence, named by its phase (§98.2 Phase 1). L0 does not exempt itself from its own rule | F-07; §98.2 Phase 1 |
| **L0D-DR-8** | Where two plan documents state **different resolutions of the same decision**, the register records **both, as a conflict**, and the entry stays `open`. It never picks the later file, the longer argument or the more specific one | `master/INDEX.md`'s binding rule: *"you may not resolve a conflict between two of these documents yourself."* That rule binds L0's register exactly as it binds a lane; L0 resolves by deciding and recording, not by indexing | `master/INDEX.md` preamble |

---

## 3. THE REGISTER

**How to read an entry.** The decider is always L0 — the `Input needed from` row names whose fact or judgment L0
must obtain first, because an entry L0 cannot answer alone stalls twice if that is discovered at the decision
window. `Blocks` names lanes and task ids exactly as the raising document wrote them; where a raiser named no task,
the row names the artifact instead. `Gates` is the phase token by which the answer must exist, derived from the
raising document's own stated blocking radius — a deadline, not an estimate. `Raised as` is the dedup evidence; the
full mapping is §5.

**Priority bands.** `P0` — work stops now, across lanes. `P1` — Phase 0 exit is unreachable without it. `P2` — a
named lane task STOPs at it. `P3` — nothing stops; recorded so it is not re-derived, re-argued or silently
defaulted.

**Count.** Sixty entries: 2 × `P0`, 13 × `P1`, 38 × `P2`, 7 × `P3`. That arithmetic is a row of
`docs/decisions/register.tsv` and is asserted by `reg-lint.sh` (task `L0-04-03`).
<!-- Count changed from prior snapshot (2×P0, 14×P1, 34×P2, 12×P3) to reflect REG-001/REG-002 closure and priority reclassification, Session 12, 2026-09-08 -->

---

### 3.1 Band P0 — the two entries that outrank everything

---

#### REG-001 — Subsystems G, H, J, O and P are assigned to no lane

| | |
|---|---|
| **Priority** | **P0** |
| **Decided by** | L0. Assigning a subsystem is `L0D-04` (`L0-00-charter.md` §2.3) and, on options B and C below, also a versioned amendment to the FROZEN partition |
| **Input needed from** | Nobody. Every fact needed is already on the page; this is a scope judgment L0 holds alone |
| **State** | Closed — Resolved by FD-002 (2026-09-02): Subsystems G→L0, H→L5, J deferred, O→L1(registries)/L3(jobs), P→L0. Preamble X-rule lifted. |
| **Gates** | Split by subsystem — see the sub-rows. Earliest is **Ph0** (contract freeze) for **O**'s registry half; latest is **Ph7** for **G** |
| **Raised as** | `D-PLAN-01`, `D-PLAN-02` (`master/00` §2.3) · `LA-01` (`master/01` §9) · `D-REQ-4` (`master/03` §8) · `DECISION 1` (`master/04` §8) · `D-EE-2` (`master/05` §1) · `V1-D1`, `V1-D2` (`master/06` §12) · `DEC-01` (`master/07` §7) · `DECISION REQUIRED #2` (`lanes/L1-00` §12) · `L0-IG-D3`, `L0-IG-D4` (`lanes/L0-05` §5) · `D-L2-12` (`lanes/L2-06` §5) · `D-L4-P4-04` (`lanes/L4-04` §5) · `D-L4-P5-03` (`lanes/L4-05` §6) · `DR-L0-07-F` (`lanes/L0-07` §10.2) · `protocol/02` §2 · `master/INDEX.md` C-21, C-24 |

**What must be decided.** Spec §99.2 defines eighteen lettered subsystems, **A** through **R**. PARTITION.md
assigns thirteen: A, B → L1; E, F → L2; C, D → L3; I, N → L4; K, L, M, Q, R → L5. **G** (plan-checker and Gate 1
tooling), **H** (dashboards and views), **J** (background machine layer), **O** (governance registries and jobs)
and **P** (people intelligence engine) are assigned to nothing. The lane guard is fail-closed: `lane-paths.tsv`
carries `X<TAB>*/*` before its catch-all (`L0-00-03`), so the first pull request touching a path any of the five
would need resolves to `UNOWNED` and fails. **That is the guard working correctly, and it stalls the work
invisibly.** L0 must state, per subsystem, which lane owns it or that it is out of the five-lane build.

**Blocks, by lane and task id.**

| Subsystem | Blocks | Gates |
|---|---|---|
| **G** plan-checker, Gate 1 tooling | L2 `L2-T700` (NT-24, booked against L2 by `protocol/04` but requiring subsystem G); `IG-07` for `AT-106` and `IG-11`'s rejection count (`lanes/L0-05` §5); onboarding `OT-P7` for every product (`lanes/L0-07` §10.2, `DR-L0-07-F`); `master/04` BT-4 | **Ph7**; the capability-verification run against the pinned GSD release is an **entry-criterion** task (`master/00` §5 EC-9) and cannot wait |
| **H** dashboards and views | Founder view v0, which §99.4 item 7 places **inside V1**; L4's `metrics/ingest/README.md` handoff (`D-L4-P5-03`); `AT-097`, `AT-098` — both `P2`-gated, so outside GATE B's 37 (`lanes/L0-05` §5) | **Ph2** — `master/06` §12 `V1-D2`: *"Do not start one until this is answered"* |
| **J** background machine layer | `AT-109`, activated at `Ph3`; `IG-07` FAILS from `Ph3` onward if it stays unassigned (`lanes/L0-05` §5); the Hermes cage, egress override and systemd stop unit | **Ph3**, and gated behind Phase 3's own CPU benchmark (§98.2) — a failed benchmark parks the subsystem, it does not assign it |
| **O** governance registries and jobs | `policies.yaml`, which `IG-06` reads for the §101 `policy`-class invariant classification (`lanes/L0-05` §5); the exception-expiry counter, pattern detector, learning-loop tracker, change-budget counters, exit checklists, tool register; `L1-00` §12 DR #2's "name the lane that owns the O jobs"; `AT-031`, `AT-038`, `AT-040`, `AT-045` (`protocol/02` §2) | **Ph0** for the registry-file half — the minimal `exceptions.yaml` is a named Phase 1 completion-check artifact (§98.2) and `master/04` DECISION 2 records that the **file** has no declared owner |
| **P** people intelligence engine | The Capacity Profile, workload states and Founder view that must honour L4's `capacity_profile_eligible`, `workload_state_eligible` and `founder_view_eligible` outputs (`D-L4-P4-04`); the Performance Framework Registry (`LA-03`); 50 acceptance tests, none inside GATE B's 37 (`lanes/L0-05` §5) | **P1** at the earliest; §98.6 hard-gates P4 on the Layer B datasource separation, itself a P2 deliverable. §99.4 item 9 defers P from V1 outright |

**Options.**

| # | Option | Trade-off |
|---|---|---|
| **A** | **Hold all five with L0**, executed serially outside the five parallel branches (`master/03` `D-REQ-4` A; `master/04` DECISION 1 (a); `master/07` DEC-01 (1); `master/01` `LA-01` (c)) | Consistent with §98.7 (*"no dedicated platform team"*) and with the fact that G, H, J, O and P each require judgment the AI-developer profile excludes. **No partition change.** Cost: L0 becomes the critical path from mid-programme, and BT-4 is not a parallel phase at all — the §99.4 item 7 Founder view slips behind S3 |
| **B** | **Extend existing lanes by path**, no new lane. Candidate mapping, stated by three raisers with two disagreements: O → L3 (`LA-01` a, exception expiry is already reconciliation) **or** O → L1 (`DEC-01` 2, registry-shaped) — the raisers disagree; H → L4 (`D-PLAN-01` A, `DEC-01` 2) **or** H → L5 (`D-PLAN-01` B, `V1-D2` a, Grafana runs on the ops VM) — the raisers disagree; J → L5; G → L2 (`LA-01` a, CI-adjacent) **or** G → L0 (`DEC-01` 2, design-open); P → deferred | Adds the paths to the §2 manifest, `CODEOWNERS` and `lane-paths.tsv` in **one commit** with a decision record. Requires an explicit, versioned re-freeze of PARTITION.md — *"which must be made once, explicitly, and versioned — not drifted into"* (`master/04`). **The two disagreements above are themselves part of the decision** and must be settled in the same record |
| **C** | **Open a sixth lane** `lane/6/*` with its own path set (`LA-01` b; `master/05` Option 2) | Contradicts nothing PARTITION states — it fixes five *build* lanes — but changes the merge train order, adds a CODEOWNERS block, a lane-owner row and a guard arm. `master/04` DECISION 1 (c) recommends against it |
| **D** | **Leave them `UNOWNED` deliberately**, so any attempt to build one fails loudly (`D-REQ-4` C) | Zero work now; **this is the current state by default**. `master/03` is explicit that the resulting failure is *"a correct fail-closed stop, not a bug to be worked around by adding a map rule locally"*. Guarantees a mid-build stall at the first attempt, at a time L0 does not choose |
| **E** | **Declined**, per §98.1 — for **G** specifically, `master/00` `D-PLAN-02` option C: Phase 7 recorded as `declined` with gate answers, forgone capabilities and a review date, planning artifacts staying plain markdown and YAML | Loses tooling, not truth. Applies to a subsystem, not to the set. `L0D-20` governs the recording; `L0D-21` governs the P0-before-P2 lock that a `declined` phase releases |

**Constraint binding on every option** (`master/07` DEC-01, `master/00` `D-PLAN-01`, `master/01` `LA-01`):
§99.3 item 3 (plan-checker internals, → **G**) and item 1 (the attention classifier, feeding **P**) are
**design-open in the specification**. Neither may be assigned to a lane in any form, because PARTITION's
AI-developer profile forbids a task that requires designing. They are L0 work under every option. Separately, on
whichever lane receives **H**, the Layer B split of §99.5 and **D75** require the Founder-only instance's
provisioning to live in a path that lane owns **and** `AT-097` to be executable against it — `AT-097` verifies the
people datasource is absent from the shared instance's *provisioned configuration*, not inferred from panel
visibility. `C` (a sixth lane) additionally forces a merge-train amendment, which is `L0D-07`.

**In force until answered.** The guard's `X` rule. Every path the five subsystems would need resolves `UNOWNED`
and every pull request touching one FAILS. No lane creates a plan-checker, a dashboard JSON file, a Hermes cage
configuration, a governance job or any people-intelligence artifact. A lane asked to do so files a blocker naming
**REG-001** and stops (`L0-00-charter.md` §7.1). `IG-06` and `IG-07` fail closed and GATE B stays closed rather
than reporting the affected acceptance tests as not-applicable — an `IG-06` that passed by declaring itself out of
scope is the silent gate §99.6 risk 5 describes.

---

#### REG-002 — The lane guard sits inside the exclusive path of a lane it judges

| | |
|---|---|
| **Priority** | **P0** |
| **Decided by** | L0. On options A and E this is `L0D-04` (extending `lane-paths.tsv`) plus `L0D-05` (`CODEOWNERS`); on option B it is `L0D-24` (a repository PARTITION does not list) |
| **Input needed from** | Nobody |
| **State** | Closed — Resolved by FD-003 (2026-09-02): Named-file carve-out option A + cycle-1 replay option E. `.github/workflows/lane-guard.yml` exclusively L0-owned per lane-paths.tsv. Guard circularity resolved. |
| **Gates** | **Ph0**, before any lane branch exists. `L0D-LG-3` turns on this being true: the workflow is placed *"before `.github/workflows/**` has an L2 branch to be taken from"* |
| **Raised as** | `LA-02` (`master/01` §4, §9) · `D-REQ-3` (`master/03` §8) · `DEC-02` (`master/07` §7) · `D-L2-06` (`lanes/L2-00` §9, `lanes/L2-05` §1) · `DR-L1-06-D` (`lanes/L1-06` §5) · `L0D-LG-1`…`L0D-LG-3` (`lanes/L0-02` §4, stated as a resolution) · `protocol/10` §2.1 (stated as a *different* resolution) · `master/INDEX.md` C-9, C-14, R-11 |

**What must be decided.** PARTITION.md states that the partition is enforced by *"CODEOWNERS + the lane-guard CI
check"*. `CODEOWNERS` is L0's. GitHub will only run a workflow that lives in `.github/workflows/`, and PARTITION.md
gives `.github/workflows/**` to **L2, exclusively, without carve-out**. As frozen, L2 owns the workflow that
polices all five lanes, and an L2 pull request editing it touches no foreign path — so the guard raises no
violation about itself. L0 must decide **who owns that file's bytes** and **how the cycle-1 ordering works**, since
the merge train runs `L1 → L4 → L2 → L3 → L5` and L1 and L4 therefore merge before any L2 file exists.

**Why it is P0 and not P1.** `master/07` DEC-02: *"The lane-guard check is the single mechanical control behind
PARTITION rule 1, which is the reason merges cannot conflict. If it is weakened, AX-10, AX-11 and AX-16 all lose
their detection at once, and the loss is silent."* §53.1 states the general principle this instance violates:
*"no control that can be rewritten by the credential it is checking is a control."*

**The live conflict this entry must resolve, recorded under L0D-DR-8.** Four plan documents already state four
different answers, three of them as *binding*:

| Document | What it states | Status |
|---|---|---|
| `master/01` §9 `LA-02` | Options only; and **forbids creating the guard workflow file until L0 decides** — which makes `master/01` §4 and §11's own self-verify block unrunnable (`INDEX` R-11) | open |
| `master/03` §8 `D-REQ-3` | Recommends **A** (an exact-file rule `L0 .github/workflows/lane-guard.yml`), and keep `pull_request_target` regardless | recommendation |
| `master/07` §7 `DEC-02` | *"Until answered: **option 3** is in force as the interim control"* — L0 pins the guard's blob SHA at Phase 0 and runs `B17` at every train slot | **claimed in force** |
| `lanes/L0-02` §4 | `L0D-LG-1`/`-2`/`-3`: the *content* is an L0 contract at `contracts/ci/lane-guard.yml.frozen`, the *location* stays L2-owned but byte-frozen and classified `GUARD-CRITICAL`, and L0 places the file once on `integration` in Phase 0 | **claimed resolved** |
| `protocol/10` §2.1 | *"D-L2-06 is resolved here — option (b), retroactive replay. **Resolution, binding.** No partition exception is created"* — L0 runs the verdict of record locally for cycle 1, and `IG-08` replays the guard over the merged range | **claimed binding, and incompatible with `L0-02` §4** |

A fifth disagreement rides along: `protocol/10` §2 mechanism 2 asserts *"`CODEOWNERS` … routes `.github/workflows/**` to L0, so L2 authors and L0 approves"*, while the `CODEOWNERS` body written by `L0-00-01` routes `/.github/workflows/` to `@LANE2_REVIEWER`. Both cannot be true of one file.

**Blocks, by lane and task id.**

| Lane | Blocks | Detail |
|---|---|---|
| **L0** | `L0-02-05` (generate `CODEOWNERS`), `L0-02-06` (freeze the workflow contract), `L0-02-07` (place the workflow) | `LA-02` forbids creating the file until this is decided; `L0-02` proceeds as though it is decided |
| **L2** | `L2-T004` (`lane-guard.yml`); charter `DoD-20` for cycle 1 | `D-L2-06` |
| **L1, L4** | Cycle-1 merges to `integration` run before any guard workflow exists | `D-L2-06`; `DR-L1-06-D` asks the adjacent question — whether L1 PRs before L2's check lands are gated manually |
| **all** | `IG-08` (lane-guard replay), `LG-01`…`LG-12` mirroring | `protocol/10` §2.1; `lanes/L0-05` §4 `L0D-IG-7` |

**Options** (union of the four raisers' sets; no new option is invented here).

| # | Option | Trade-off |
|---|---|---|
| **A** | **Named-file carve-out.** One exact-file rule `0<TAB>.github/workflows/lane-guard.yml` in `lane-paths.tsv`, ordered before L2's prefix rule, plus the matching `CODEOWNERS` line. Exact rules beat prefix rules (`D-REQ-3` A; `DEC-02` 1) | Smallest change. Narrows L2's stated ownership by exactly one file and makes the OWNS column a glob-with-one-exception, which every ownership-matching command must then honour. Does **not** by itself answer the cycle-1 ordering |
| **B** | **Move the guard out of the repository under test.** A separate L0-controlled repository, consumed as a reusable workflow by pinned tag — the mechanism §99.5 already uses for the reusable workflow library; the file in `control-plane` becomes a two-line pinned caller and moving the pin is itself a detectable change (`DEC-02` 2; `LA-02` b; `D-REQ-3` C) | Strongest separation. Adds a repository PARTITION.md does not list, which is `L0D-24`, and a second credential surface |
| **C** | **Accept and detect.** Ownership unchanged; L0 pins the guard's blob SHA at Phase 0 and runs `B17` at every train slot, treating any difference as Red and Blocking on `lane/2/*` (`DEC-02` 3; `LA-02` c) | Zero structural change. Detection is L0-manual and depends on `B17` actually being run every cycle — the same class of dependency `master/07` BR-03 calls out. **`master/07` claims this is in force today** |
| **D** | **Content-freeze in `contracts/**`.** The workflow body is an L0 contract at `contracts/ci/lane-guard.yml.frozen`; the location stays L2-owned but is classified `GUARD-CRITICAL` and byte-compared against the contract on every PR; L0 places it once, on `integration`, in Phase 0, before any lane branch exists (`lanes/L0-02` §4) | Preserves the frozen partition **unamended** — L2 still owns the path and simply may not edit one file in it, exactly as it may not edit `contracts/**`. Depends on the Phase-0 placement being genuinely one-time and on the byte-compare running before every other check |
| **E** | **Cycle-1 replay only.** No ownership change at all: the lane-guard *check* is `contracts/gate/lane-guard.sh` (L0-owned, exists at BT-0); cycle 1's L1 and L4 merges are gated by L0's local `make gate-lane` run, and `IG-08` replays the guard over the whole merged range at the first integration gate, so unguarded merges are *re-checked, not forgiven* (`protocol/10` §2.1) | Answers the **ordering** half completely and the **ownership** half not at all — it moves the verdict of record out of CI but leaves `.github/workflows/lane-guard.yml` editable by L2. Compatible with A, C or D; **incompatible with treating `L0-02` §4 as already settled** |

**A complete answer must state four things**, because the raisers each answer a different subset: (1) who owns the
bytes of `.github/workflows/lane-guard.yml`; (2) what `lane-paths.tsv` and `CODEOWNERS` say about
`.github/workflows/**`, in agreement with each other; (3) what gates L1's and L4's cycle-1 merges; (4) which of
`master/07` DEC-02's "option 3 in force", `lanes/L0-02` §4's `L0D-LG-1..3` and `protocol/10` §2.1's "binding
option (b)" survives, and which are superseded by the decision record.

**In force until answered.** Nothing is in force, and that is the finding: three documents each claim a different
interim control is running. Until L0 records one answer, treat the guard as **unarmed** — L0 runs
`make lane-guard LANE=<n> BASE=integration HEAD=<branch>` locally for every lane branch at the 09:45 sweep
(`L0-00-charter.md` §8.1) and that local run is the verdict of record. No lane opens `.github/workflows/`.

---

### 3.2 Band P1 — Phase 0 exit is unreachable without these

Thirteen entries. Every one of them must be recorded in `contracts/**` **before the contract freeze**, because a
lane's first task reads it. `L0-00-charter.md` §8.1's 17:00 contract window is the only time they may be written.

---

#### REG-003 — The implementation toolchain: language, runtime version, dependency pinning

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-24`, a tool not already named in the spec — `C-10`) |
| **Input needed from** | Nobody. §99.5 fixes the substrate and is silent on implementation language; this is L0's alone |
| **State** | Closed — Forced by prior decision |
| **Raised as** | `D-EE-1` (`master/05` §1) · `L1-D01` (`lanes/L1-05` §1) · `validator_runtime` (`lanes/L1-03` §1) · `D-3` (`lanes/L1-04` §4) · `D-L2-07` (`lanes/L2-05` §1) · `L3-D1` (`lanes/L3-06` §1) · `D-L3-01` (`lanes/L3-01` §1) · `D-L3-04-01` (`lanes/L3-04` §1) · `D-L4-TL-1` (`lanes/L4-06` §1) · `L5-T02` (`lanes/L5-06` §4) · `master/INDEX.md` C-23 |

**What must be decided.** §99.5 fixes the git host, CI, dashboards, boards, records substrate and identity bridge.
It names **no implementation language** for subsystems B, C, D, F, I or N. §99.1 fixes the *shape* — *"a
schema-and-validator suite, a reconciliation engine, a provisioning and scaffolding CLI, a reusable CI/CD workflow
library"* — scripts and CLIs, never an application. §101 invariant 85 requires third-party dependencies pinned. One
runtime, one pinning mechanism, recorded once.

**Why this is P1 and not P3.** The five lanes have already written against **three different answers**: `L1-05`
and `L1-03` assume **Python 3.11**; `L2-05`, `L3-04`, `L3-06` and `L4-06` assume **Python 3.12**; `master/08` §2.3's
worked ledger entry uses `npx --yes ajv-cli@5.0.0`, i.e. Node. Four lane files each say *"if L0 ratifies anything
else, STOP and this whole file needs reissuing by L0."* A late answer reissues four lane documents.

**Blocks.** L1 `L1-001` and `L1-03-00`; L2 `L2-T500`; L3 `L3-P0-02` *"and therefore everything"*; L4 `L4-P2-02`
*"and every task after it"*; L5 `L5-T02`.

| # | Option | Trade-off |
|---|---|---|
| **A** (`T-A`, recommended by `master/05`) | Python 3.12, `jsonschema`, `check-jsonschema`, `PyYAML`, `pytest`, pinned by exact `==`, no lockfile generator | One runtime for validators, reconciler, provisioning CLI and metrics jobs; matches the ops-VM job substrate (§99.2 subsystem M). Requires the 3.11/3.12 split above to be settled explicitly, not left to whichever file the executor opens first |
| **B** (`T-B`) | Node 20, `ajv-cli`, `js-yaml`, `vitest` | Closer to Actions-native tooling; puts a second runtime on the operations VM |
| **C** (`T-C`) | Go, single static binaries | Best for the reconciler's privileged credential; slowest to author with AI assistance |

**In force until answered.** `master/05` §1 publishes a substitution table so every command in that file is
mechanically portable across the three. Each lane file names its assumption in its own DECISION REQUIRED block and
STOPs at the task named above if `contracts/**` says otherwise.

---

#### REG-004 — The JSON Schema `$id` host

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-01`) |
| **Input needed from** | The Founder — the company domain or the GitHub organisation login (interacts with **REG-009**) |
| **Raised as** | `L0 DECISION REQUIRED 1` (`master/09` §19) |
| **State** | Closed — Resolved by FD-007-R (2026-09-02) + FD-050 (2026-09-06): Option C (URN); namespace `urn:multiproduct:schemas:<type>:<version>`. |

**What must be decided.** The `<SCHEMA_HOST>` token in `https://schemas.<SCHEMA_HOST>/<family>/<entity>/v<N>.schema.json`
(§11.1). `$id` values are baked into every schema file and every cross-file `$ref` from `contracts/**`; changing
them later rewrites every schema in three lanes at once, which the partition exists to prevent.
**Blocks.** L1 `schemas/registry/**`, `schemas/product/**`; L4 `schemas/records/**`.

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended by `master/09`) | The company's own domain, `schemas.<company>.com`, recorded once in `contracts/schema-ids.yaml` | Stable, readable, resolvable if ever published; requires L0 to name the domain |
| **B** | `https://raw.githubusercontent.com/<org>/control-plane/main/schemas/…` | Resolvable today with no DNS work; couples `$id` to a branch name and to GitHub |
| **C** | A URN, `urn:controlplane:registry:people:v1` | No host needed, never resolvable; some tooling handles URNs poorly |

**In force until answered.** None — the blocked task STOPs. A schema cannot be written without an `$id`.

---

#### REG-005 — The JSON Schema validator implementation and dialect

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-01`, `L0D-24`) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by prior decision |
| **Raised as** | `L0 DECISION REQUIRED 2` (`master/09` §19) · `DR-L1-06-B` half (`lanes/L1-06` §5) |

**What must be decided.** §99.2 subsystem B requires *"multi-version schema validators"* and names no
implementation; §99.5 names no schema tooling. The choice fixes the dialect actually supported, whether `format`
asserts or only annotates, and the exact text of validation errors — which `master/09` §13.2 verdict lines and every
`rejects` test compare against. Distinct from **REG-003**: a Python build can still run `ajv`, and a Go binary
forces the dialect down.
**Blocks.** L1 (every rule module); L2 (the CI gate); L4 (record schema validation).

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended) | Python `jsonschema` + `check-jsonschema` CLI, `format` assertion **explicitly enabled** | Full 2020-12; same language as the reconciler and provisioning tools; one toolchain to install. `master/09` §11.2 rule 10 additionally requires a `pattern` on every date field, which is what makes A safe |
| **B** | `ajv-cli` (Node) | Fast, excellent 2020-12 support; adds a Node toolchain to a Python-shaped build surface |
| **C** | `yajsv` (Go, draft-07 only) | Single static binary, no runtime; **forces the dialect down to draft-07**, losing `$defs`/`prefixItems` semantics assumed throughout §11 |

**In force until answered.** None — L1 `L1-03-00` fails closed if `contracts/decisions/L1-03.yaml` is absent or
carries a `null` key.

---

#### REG-006 — Commit-signing scope on `control-plane` lane branches

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-18`, fail-closed classification; `L0D-25`, key custody) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by spec |
| **Raised as** | `L0 DECISION REQUIRED 4` (`master/09` §19) · `UXG-4` (`master/05` §0.5) · `master/02` §10.5, §O-11 · `master/INDEX.md` C-16 |

**What must be decided.** **D107** requires signing on the **records** repository — *"commits are signed by the
writing identity and an unsigned or foreign-signed commit is Blocking drift"* — and the specification is silent for
`control-plane` lane branches. Three plan documents disagree: `master/02` §10.5 puts `required_signatures` only on
the records ruleset; `master/05` `UXG-4` makes *every commit on every lane branch* signature-verified an exit
condition; `master/09` §15 offers signing on `main`/`integration` as an option.
**Blocks.** Every lane's first task (the setup step changes); L5 `L5-T07` (`access/model/branch-protection.yaml`);
`master/05` `UXG-4` as an exit criterion.

| # | Option | Trade-off |
|---|---|---|
| **A** | Signed commits required on all branches of both repositories | Uniform and strongest; every AI developer needs a key provisioned before its first commit, which is a fifth-tier credential per lane (§40.1) |
| **B** (recommended by `master/09`) | Signed on `main` and `integration` only | Lane branches stay frictionless; every commit reaching a protected branch is attested. `UXG-4` must then be rewritten by L0, because it asserts the opposite |
| **C** | Signed on `control-plane-records` only, per D107 | The minimum the spec demands; leaves `control-plane` authorship unattested |

**In force until answered.** None — a lane's first task cannot be written until the setup step is fixed. `UXG-4`
as written fails every lane on day one.

---

#### REG-007 — The `contracts/**` surface list, filenames and directory layout

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` — this entry *is* the freeze · **Decided by** L0 (`L0D-01`, `L0D-06`) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by prior decision |
| **Raised as** | `L3-D2` (`lanes/L3-06` §1) · `DR-L3-07-A` (`lanes/L3-07` §2) · `D-1` (`lanes/L1-04` §4) · `D-L4-TL-5` (`lanes/L4-06` §1) · `D-L2-02` (`lanes/L2-00` §9) · `master/01` §5 (`C1`–`C18`) · `master/03` §3.1 · `master/05` `L0P0-E1` · `master/06` §11 · `master/INDEX.md` G-5, G-10 |

**What must be decided.** `contracts/**` is specified three times in the plan set and fixed once nowhere.
`master/01` §5 lists eighteen surfaces `C1`–`C18` and says *"the exact filenames are L0's to fix"*; `master/03`
§3.1 gives a directory layout (`contracts/schemas/`, `contracts/event-types/`, `contracts/records/`,
`contracts/workflow-io/`, `contracts/cli/`, `contracts/fixtures/`, `CONTRACTS.lock`); `master/05` `L0P0-E1`
requires seven specific files (`estate.yaml`, `lane-paths.yaml`, `l1-schemas.yaml`, `l2-workflows.yaml`,
`l3-reconciler.yaml`, `l4-records.yaml`, `l5-access.yaml`); `master/06` §11 adds `contracts/v1-scope.yaml`;
`master/03` §4.2 references `contracts/CONSUMERS.md`. Phase 0 is the one unparallelisable step in the plan and its
output is unspecified.

**A second half, `master/INDEX.md` G-10.** `master/01` §5 names **L4** as the producer of surfaces `C1`/`C2`/`C3`,
**L2** of `C7`/`C12`, **L3** of `C9`–`C11`, **L5** of `C13`–`C15`/`C17` — but PARTITION rule 2 forbids a lane from
editing `contracts/**` and `master/01` §6.1 puts Phase 0 authorship entirely with L0, before any lane exists. Either
L0 authors nine surfaces it has no domain knowledge of, or a lane writes into a path it may not touch. `LA-05`
raises this for `C2` only; it applies to nine.
**Blocks.** L3 `L3-P0-03` *"and every task depending on it"*, `L3-07-01`; L1 `L1-03-00`, `L1-04-08`; L2 standing
STOP rule `S1`; L4 `L4-P2-02`. Also `master/04` §7's `contracts/v1` tag check and `master/03` §3.2's
`contracts/CONTRACTS.lock` — two independent freeze mechanisms, neither protected by any ruleset (`INDEX` R-9).

| # | Option | Trade-off |
|---|---|---|
| **A** | Adopt `master/03` §3.1's layout, extend it with `master/05`'s seven per-lane files, and publish `contracts/CONSUMERS.md` naming which lane reads which surface | One layout; the per-lane file gives each lane exactly one path to read. Requires L0 to author all eighteen surfaces including the nine it has no domain knowledge of |
| **B** | Same layout, but each lane's surface is authored as a **draft** in the lane's own tree and L0 transcribes it into `contracts/**` verbatim under a CCR before the freeze | Keeps domain knowledge with the lane and authorship with L0; costs one transcription round per surface and needs the draft path named in the same decision |
| **C** | Freeze only the surfaces Phase-0 lanes actually read, and version the rest as they are needed | Shortest Phase 0. Breaks the "frozen from Phase 0" property PARTITION rule 2 rests on, and turns every later addition into a CCR against a moving baseline |

**In force until answered.** None. Every lane's Phase-0 preflight task fails closed on a missing contract, by
design (L1 `L1-001`, L2 `S1`, L3 `L3-P0-03`, L4 `L4-P2-02`).

---

#### REG-008 — Where the spec's root-named registry files physically live

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-04`) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by PARTITION.md |
| **Raised as** | `D-REQ-2` (`master/03` §8) · `DECISION 2` (`master/04` §8) · `LA-04` (`master/01` §9) · `master/INDEX.md` C-11, C-12 |

**What must be decided.** The spec writes `people.yaml`, `roles.yaml`, `platform.yaml`, `topology.yaml`,
`exceptions.yaml`, `policies.yaml`, `tools.yaml` and `economics.yaml` as repository-root files (§7, §8, §54, §55,
§60, §62, §66, §68). PARTITION gives **root files to L0** and **`registries/**` to L1**. Taken literally, L1 — the
Registries & Contracts lane — owns no registry file at all and every registry change becomes an L0 CCR. Three plan
documents place them in three mutually exclusive locations: `master/03` §2.5 makes them uncommitted build outputs
(acceptance criterion 8 requires `git ls-files | grep '^people\.yaml$'` to be `0`); `master/06` §13's V1 exit gate
requires `test -f people.yaml` **at the repository root**; `master/00` EC-11, `master/02` §13, `master/05` §3 and
`master/07` §5.3 all read them at `registries/<name>.yaml`.
**Blocks.** The `L1 registries/` line of the ownership map, the whole of `master/03` §2.5, and **L1's first task**.
Also `master/06` §13's V1 exit gate, which is written against the opposite answer.

| # | Option | Trade-off |
|---|---|---|
| **A** (assumed by `master/03`) | Registries live under `registries/` as directory-per-item trees (`registries/people/<login>.yaml`, `registries/platform/event-types/<id>.yaml`); the root-named files are **build outputs**, assembled by `make`, never committed. L1 owns the source, L0 owns the assembler | Consistent with invariant 46 (*derived data is computed, never hand-maintained*) and with §97.3's one-file-per-item rule. `master/06` §13's exit gate must then be rewritten by L0. Note `INDEX` C-12: `master/03`'s `lane-generated.map` compares by exact path and can never match a bare name under this option — the rule is inert as written and must be fixed in the same decision |
| **B** | Root-named files hand-maintained at the root, owned by L0 | Every new person, tool, policy and event type becomes an L0 serialisation point; L1's lane has almost no content; reintroduces exactly the shared-mutable-file conflict class PARTITION rule 3 removes |
| **C** | Root-named files at the root, each assigned individually to L1 by exact-file rule | Preserves the spec's literal layout and keeps L1 productive; keeps the shared-list conflict class alive **inside** L1 and forces every L1 task to serialise |

**In force until answered.** `master/03` is written throughout against **A**; if L0 chooses B or C the only edits
are to the two ownership maps. L1 does not create a registry file at either location until this is recorded.

---

#### REG-009 — The GitHub organisation login

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` — it is an entry criterion, not a phase deliverable · **Decided by** L0 |
| **Input needed from** | The Founder |
| **State** | Closed — Resolved by FD-068 |
| **Raised as** | `D-L4-01` (`lanes/L4-01` §"DECISION REQUIRED") · `DECISION 5` (`master/04` §8) · `D-L4-TL-5` (`lanes/L4-06` §1) |

**What must be decided.** §98.2 Phase 1 requires *"Consolidate all products into one company-owned GitHub
organisation"* and never names it. `$ORG` is substituted into every `gh` command in the plan set. A wrong value
creates repositories in the wrong account and attaches every ruleset and App scope to the wrong object.
**Blocks.** L4 **every task** in `L4-01-records-repo.md`; L5 `access/**` and `infra/**`; L3 `tools/provision/**`
live runs; L0 `L0-00-01`.

| # | Option | Trade-off |
|---|---|---|
| **A** | Record the literal login in `contracts/estate.yaml`, key `org` | The only option. It is a fact, not a choice |

**In force until answered.** *"None — there is no safe default"* (`lanes/L4-01`). Every task STOPs.
Two adjacent facts must be recorded in the same decision, per `master/04` DECISION 5: the **BT-0 duration** (the
one phase with zero parallelism, so its length adds directly to wall-clock) and the **Build-track start date**,
from which bootstrap-exception `start`/`expiry` dates, the 90-day restore rotation and the "roughly month 3" asset
gate are all measured.

---

#### REG-010 — L0's own branch prefix

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-04`) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by prior decision |
| **Raised as** | `D-REQ-1` (`master/03` §8) |

**What must be decided.** The guard derives the lane from the head branch name. PARTITION defines `lane/N/*` for
lanes and names `main` and `integration` for L0, but does not name the branch L0 opens its **own** pull requests
from — and L0 must open them, because branch protection forbids direct pushes to `main`.
**Blocks.** `R0c derive the lane from the head branch` in `master/03`'s guard; `lane-guard.sh`'s lane argument for
every L0 PR.

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended, and what `master/03`'s workflow already implements) | `l0/<task>`, e.g. `l0/ccr-14`, `l0/freeze-contracts` | One line in the `case` statement, already present; costs nothing; keeps every change to `integration` reviewable |
| **B** | L0 pushes directly to `integration` with `enforce_admins: false` | Costs the audit trail and contradicts §98.2 Phase 1's completion check (*"no direct human push to any default branch succeeds"*) |
| **C** | `lane/0/*` for symmetry | Requires the `case` arm and the L0 rules in the ownership map to be re-keyed to `L0`; cosmetic only |

**In force until answered.** `L0-00-charter.md` §1 has L0 working **directly on `integration`**, which is
permitted only because `integration` is not the default branch. That is option B's posture for L0's own commits and
must be reconciled with whichever option is recorded.

---

#### REG-011 — Branch-name grammar, task-id grammar, and the phase-vocabulary crosswalk

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0`, before the first lane branch exists · **Decided by** L0 (`L0D-04`) |
| **Input needed from** | Nobody |
| **State** | Closed — Forced by prior decision |
| **Raised as** | `master/INDEX.md` C-1, C-2, C-18, C-19, C-20, G-2 |

**What must be decided.** Three grammars, all load-bearing, none agreed.
**(a) Branch names.** `master/02` §2 fixes `^lane/[1-5]/(p[0-7]|g[1-8]|pp[1-8])-[a-z0-9-]{3,40}$`; `master/09` §4
fixes `^lane/[1-5]/(f[0-7]|g[1-8]|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}$` and explicitly declares `master/02`'s
convention wrong; `master/05` §0.4 and `master/08` §2.2 use two further schemes. **Every live branch name in the
set passes neither regex** — `lane/1/01-repo-skeleton`, `lane/2/phase0-charter`, `lane/4/00-charter-preflight`,
`lane/3/05-loader`, `lane/1/canary-do-not-merge`, `lane/1/s0-guard-test`, `lane/2/phase1-ci`.
**(b) Task ids.** `master/09` §3 fixes `L<lane>-<PHASE>-<2-digit>`; `master/08` §2.2 fixes a three-digit lower-case
form; `master/05` §0.2 uses `L<lane>-P<n>` for *lane build* phases, which parses under `master/09` as People-tier.
In use across the set: `L1-RB-088`, `L1-04-017`, `L3-P1-006`, `L5-P3-011`, `L0-P0-023`, `L1-F3-04`, `L1-p0-003`.
**(c) Phase vocabulary.** Four schemes — `B0`–`B7`, `BT-0`–`BT-4`/`S0`–`S4`, `L<n>-P<k>`, `F0`–`F7`/`G1`–`G8`/`P1`–`P8` —
with no crosswalk, plus three onboarding schemes (`O-4`…`O-7`, `OT-P4`…`OT-P7`, `O-1`…`O-4`) and `S<n>` meaning four
unrelated things.
**Why P1.** The lane guard derives the lane from the branch name, so (a) is mechanical, not cosmetic. Branch names,
task ids and gate ids all encode a phase, so a lane cannot determine which phase it is in.
**Blocks.** Every lane's first branch; `master/03`'s `R0c`; `L0-03-merge-train.md`'s per-lane branch checks; every
`Depends on <task-id>` line in every lane file.

| # | Option | Trade-off |
|---|---|---|
| **A** | Adopt `master/09` §3–§4 as authoritative for all three, and L0 reissues the non-conforming branch and task ids in `master/02`, `master/05`, `master/08` and every lane file in one commit | `master/09` is the conventions document and is the only one that states the `P3` ambiguity explicitly. Costs a sweep of the whole set |
| **B** | Adopt a deliberately loose grammar — `^lane/[1-5]/[a-z0-9][a-z0-9-]{2,48}$` — and derive the lane from the second segment only, dropping the phase from the branch name entirely | The guard needs only the lane. Every existing branch name passes. Loses the phase signal from branch names, which `master/08`'s burn-down reads |
| **C** | Keep every existing name and publish `master/09` §"crosswalk" — one table mapping each scheme onto each other | Zero renaming. The crosswalk becomes a permanent piece of load-bearing translation that nothing mechanically validates |

**In force until answered.** None. `master/INDEX.md` G-2 records this as the root cause of C-1, C-2 and C-19 and
recommends it be *"fixed once, in `09`, before anything else"*.

---

#### REG-012 — Git conventions: merge method, staging, branch creation, commit message, and the canonical templates

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-04`, `L0D-07`) |
| **Input needed from** | Nobody |
| **State** | Closed — D113 or forced by arithmetic |
| **Raised as** | `master/INDEX.md` C-3, C-4, C-5, C-6, R-6 |

**What must be decided.** Five conventions, each stated twice or three times, incompatibly.
**Merge method** — `master/02` §5.3 mandates `gh pr merge --merge`, *"never squash, never rebase"*, and §10.1 sets
`allow_squash_merge=false` at repository level; `master/09` §6.4 mandates *"Merge method is **squash**"*. If
`master/02`'s repository setting is applied, `master/09`'s instruction cannot execute.
**Staging** — `master/02` §O-2: *"Never `git add .`, never `git add -A`"*; `manual/00` §7 step 7 instructs
`git add -A`.
**Branch creation** — `master/02` §O-1 mandates `git switch --no-track -c <branch> origin/integration` and states
`--no-track` is *required* so `git push` can never target `integration`; `manual/00` §7 step 3 creates exactly the
tracking relationship §O-1 forbids.
**Commit message** — three formats; `master/09` §5.1's `commit-msg` hook rejects the other two.
**Blocker template** — `master/08` points lane developers at `docs/plan/BLOCKER.md`, which no file authors; two
templates exist, in `master/09` §7.1 and `master/02` §6 `O-10`, in different formats; `L0-00-charter.md` §7.1 names
a third canonical copy at `docs/escalation/BLOCKER.md`.
**Blocks.** Every lane's git preamble and postamble; `L0-03-merge-train.md` step 4 (`--no-ff`); every STOP rule in
every lane file, which resolves to filing a blocker in a template that must exist.

| # | Option | Trade-off |
|---|---|---|
| **A** | Adopt `master/02` for merge, staging and branch creation (they are the stricter forms and one is enforced at repository level), `master/09` §5.1 for the commit message and its hook, and `docs/escalation/BLOCKER.md` + `docs/escalation/CCR.md` as the single canonical templates. Reissue `manual/00` §7 | One answer per convention, each taken from the document that enforces it mechanically. Costs a rewrite of `manual/00` §7 and of `master/09` §6.4–§6.5 |
| **B** | Adopt `master/09` throughout and set `allow_squash_merge=true`, `allow_merge_commit=false` | Squash gives one commit per task on `integration`, which suits the ledger; contradicts `L0-03-merge-train.md`'s `--no-ff` merges and loses the per-lane commit history the replay in `IG-08` reads |
| **C** | Record each convention separately, taking the stricter of each pair | No single document survives intact; every lane file must then be checked against five separate rulings rather than one |

**In force until answered.** `L0-00-charter.md` §7.1's `docs/escalation/BLOCKER.md` is the template every L0 file
already cites; treat the other two as superseded on sight. The merge, staging and branch-creation conflicts have no
interim answer and a lane hitting one files a blocker naming **REG-012**.

---

#### REG-013 — Branch-protection mechanism, and the required-check list at Phase 0

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-18`, `L0D-24`; F-07 binds every lane) |
| **Input needed from** | Nobody — but see the plan-tier constraint below |
| **State** | Closed — Forced by spec |
| **Raised as** | `master/INDEX.md` C-13, C-14 · `master/02` §10 · `master/03` §1.5 · `master/00` EC-3, EC-13 · `master/05` `L0P0-E4` |

**What must be decided.** **(a) Mechanism.** `master/02` §10 chooses **repository rulesets, not classic branch
protection**, with reasoning, and defines `CP-2` for `integration` with `required_approving_review_count: 0` and
`require_last_push_approval: false`. `master/03` §1.5 applies **classic** protection via
`PUT /branches/integration/protection` with `required_approving_review_count: 1`,
`require_last_push_approval: true`, `enforce_admins: false`. `master/00` EC-3 and `master/05` `L0P0-E4` read the
classic endpoint. Applying both leaves two overlapping controls with different values on one branch.
**(b) The Phase-0 required-check list.** `master/02` §10.1 `CP-1` **unarmed** includes `{"context": "lane-guard"}`
on `main` from day one; `master/03` §1.5 requires `["lane-guard"]` on `integration`; `master/00` EC-3 requires
`main`'s check list to be `[]` to PASS and `master/05` `L0P0-E4` requires length `0`; `master/00` EC-13
simultaneously requires the guard live before B-Day. **The four cannot all hold**, and §98.2 Phase 1 warns that a
required check no workflow emits blocks every pull request indefinitely.
**Blocks.** L5 `L5-T07` (`access/model/branch-protection.yaml`); L0 `L0-00-01` criterion on `main`; `master/00`
EC-3, EC-13; `master/05` `L0P0-E4`; L3's §53.1 branch-protection template comparison. Interacts with **REG-002**
(the guard's own context) and **REG-025** (the blocking check-run name).

| # | Option | Trade-off |
|---|---|---|
| **A** | Rulesets only, per `master/02` §10; reissue `master/03` §1.5 and the two EC commands to read the ruleset API | One mechanism, one set of values, and rulesets are what §40.1's D107 no-bypass posture needs on the records repository anyway. Costs three command rewrites |
| **B** | Classic protection only, per `master/03` §1.5 | The EC commands already read it; loses the empty-bypass-actor ruleset property `D89` relies on for `control-plane` |
| **C** | Both, with an explicit statement of which value wins per parameter | Reproduces the silent-gate class §99.6 risk 5 warns about — two controls, one surface, no visible precedence |

**Binding constraint on (b) under every option.** The list starts **empty per repository** and grows only as each
check comes into existence, **named by its phase** (§98.2 Phase 1). F-07 forbids any lane adding a context.
**Plan-tier note, `L0D-24`.** Branch protection on private repositories requires the Team plan and environment
required reviewers are Enterprise-only and are not depended on (§99.5, §99.6 risk 5, D73, D80). If a control is
unavailable, it is recorded as an accepted risk with an owner and a date — never stubbed silently.

**In force until answered.** `L0-00-01`'s STOP rule: if branch protection on `main` cannot be confirmed as
requiring a pull request, do not proceed and **do not weaken protection to make the push succeed**.

---

#### REG-014 — `CODEOWNERS` content: human identities, lane teams, or both

| | |
|---|---|
| **Priority** | **P1** · **Gates** `Ph0` · **Decided by** L0 (`L0D-05`) |
| **Input needed from** | The Founder — the real GitHub logins that replace `@LEAD_GITHUB_LOGIN` and `@LANEn_REVIEWER` |
| **State** | Closed — Resolved by FD-067 |
| **Raised as** | `master/INDEX.md` C-15 · `master/01` §3 · `master/03` §1.6 · `master/00` EC-14 · `master/05` `L0P0-E3` · `L0D-LG-5` (`lanes/L0-02` §11) |

**What must be decided.** `master/01` §3 gives a per-lane `CODEOWNERS` with `@ORG/lane-1-registries` …
`@ORG/lane-5-access` as code owners. `master/03` §1.6 gives a single line, `* @<l0-github-login>`, on the ground
that *"the five lane agents are machine actors: they author, they never approve"*. `master/00` EC-14 and §98.2's
Phase 1 completion check require CODEOWNERS to contain **human identities only**, verified negatively.
`master/05` `L0P0-E3` requires a lane team for **every** prefix, which `master/03`'s single line does not satisfy.
`L0-00-01` writes a third form: per-lane human reviewers.
**Blocks.** `L0-00-01` acceptance criteria 3 and 4; `L0-02-05` (generate `CODEOWNERS` from `lane-paths.tsv`);
`master/05` `L0P0-E3`; `master/00` EC-14. Interacts with **REG-002** (which owner the workflows tree carries) and
**REG-046** (how many humans exist to name).

| # | Option | Trade-off |
|---|---|---|
| **A** | Per-lane **human** reviewers, generated from `lane-owners.tsv` by `L0-02-05` | Satisfies EC-14 and `L0P0-E3` together, and the generation makes divergence from `lane-paths.tsv` impossible. Requires as many named humans as lanes, which **REG-046** may show do not exist |
| **B** | Single line `* @<l0-login>` | Honest under Bootstrap Mode with one human; fails `L0P0-E3`'s per-prefix requirement, which L0 must then reissue |
| **C** | Lane **teams** as owners | Fails EC-14 the moment a team contains a machine account, and §98.2's check is executed **negatively** — an approval from a machine account does not satisfy branch protection |

**Binding regardless of option, `L0D-LG-5`.** `L0-00-01`'s criterion 4
(`grep -ci 'bot\|\[bot\]\|records-writer\|reconciler' CODEOWNERS` must be `0`) greps whole lines, and a correct
CODEOWNERS contains the path `/reconciler/` — so the v1 check can never pass on a correct file. The rule it
protects is preserved and tested where it lives: the **owner column**.

**In force until answered.** `L0-00-01`'s criterion 3 (`placeholders=0`) blocks the commit: placeholders left in
place are a defect, and the file cannot be committed with them.

---

### 3.3 Band P2 — a named lane task STOPs at these

Thirty-eight entries. Each names the exact task that stops. Where the raising document defined a fail-closed interim
stub, that stub is transcribed under **in force**; a stub that *permits* is never an interim behaviour here
(`L0-00-charter.md` §6.2 `C-11`).

---

#### REG-015 — Owner and path of the acceptance-test harness

**Gates** `Ph0` for the path claim, `Ph1` for the harness itself · **Decided by** L0 (`L0D-04`) · **Input from** nobody
**Raised as** `D-EE-3` (`master/05` §1) · `L0-IG-D2` (`lanes/L0-05` §5) · `protocol/02` §2 · `master/INDEX.md` G-6, R-12
**State:** Closed — Forced by PARTITION.md

**What must be decided.** No lane owns `verification/acceptance/**` or `tools/at/**`. `protocol/02` §2 records it
and recommends L0 claim them; PARTITION assigns neither; and per `L0-00-charter.md` §2.3 an unassigned path is
**blocked for everyone**, never silently defaulted to L0. Thirteen `make` targets that `master/00` §6 makes
normative — `make dod-v1`, `make dod-foundation`, `make dod-programme`, `make at AT=<id>`, `make at-suite TIER=<t>`,
`make founder-view-v0`, `make evidence-chain`, `make phase1-completion-check`, `make check-append-only`,
`make invariant-classification`, `make codeowners-human-only`, `make validate-exceptions`, `make lane-guard` — have
no owner, no file and no harness (`INDEX` R-12).
**Blocks.** `IG-07` and therefore **GATE B**, from the first cycle in which any AT is scheduled — that is `Ph1`,
because `AT-022` activates there (`lanes/L0-05` §5). Every AT-citing exit criterion in `master/05`. Every tier gate
in `master/00` §6.4.

| # | Option | Trade-off |
|---|---|---|
| **A** (`O-3A`, recommended by `master/05`) | L0 owns `tests/acceptance/**` as a root path, one file per AT named `AT-0NN_<slug>`; each lane delivers its AT checks as a CLI subcommand in its own tree and L0's harness only invokes CLIs | Adds one L0 path; keeps PARTITION rule 4 intact — L0 never reaches into a lane's tree, it calls a published entry point |
| **B** (`O-3B`) | Each lane owns `tests/acceptance/lane-<N>/**` under its own tree; L0's `Makefile` aggregates | No new shared path; AT ids are then split across five trees and **no single command runs the catalogue** |
| **C** (`O-3C`) | The harness is a workflow only, `.github/workflows/acceptance.yml` (L2) | Puts every lane's AT logic in L2's tree — violates rule 4 in spirit, and re-creates **REG-002**'s problem on a second control |

**In force.** `at-coverage.sh` invokes `tools/at/run-at.sh "$PHASE"`; if that path does not exist every scheduled
AT is reported `not_run` and `IG-07` **FAILS** with `not_run=<n>`. It is never reported as `scheduled=0`, and a
phase with no runnable harness is never a clean phase. `master/05` writes every AT-citing criterion as the
underlying literal check so the criterion is executable without the harness.

---

#### REG-016 — The AT → phase map

**Gates** `Ph1`, before the first weekly review · **Decided by** L0 · **Input from** nobody
**Raised as** `D-08-6` (`master/08` §10) · partially discharged by `L0D-IG-5` (`lanes/L0-05` §4)
**State:** Closed — Forced by spec

**What must be decided.** §100 states each test *"is verified at the implementation phase where the capability it
exercises activates"* and publishes **no** AT→phase table. `master/08`'s `B2` therefore has a programme-wide
denominator of 110 and no per-phase denominator, so *"are we done with Phase 1?"* cannot be answered from AT
coverage. `lanes/L0-05` `L0D-IG-5` already freezes a **build-scope** map at `contracts/gate/at-activation.tsv`,
whose largest cumulative value is **37** (`protocol/02` §9.1). The programme-wide map is still missing.
**Blocks.** `master/08` `B2` per-phase coverage; every phase gate stated as AT coverage rather than as §98
completion-check prose.

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended) | L0 authors `docs/plan/at-phase-map.yaml`, one row per AT id naming its §98 phase — ~110 rows, a few hours | Every phase gate becomes checkable. Must agree with `contracts/gate/at-activation.tsv` or the gate and the ledger disagree |
| **B** | Carry only the programme-wide denominator; phase gates use §98's completion checks verbatim | Zero work; the completion checks are prose and are checked by hand |
| **C** | Derive the map from `at_ids` on issued task packets | **Rejected by its raiser** — it makes the denominator a function of what was already planned, so coverage can never read below 100% of what was thought of |

**In force.** The build-scope map only. Every gate record states the denominator `37/110` (`L0D-IG-5`), which is
what stops a status report from being misleading.

---

#### REG-017 — The unowned-path schedule

**Gates** rolling — each row gates the first task that needs it · **Decided by** L0 (`L0D-04`) · **Input from** nobody
**Raised as** `LA-03` (`master/01` §9) · `DECISION 2` (`master/04` §8) · plus the per-path raisers named in the table
· `master/INDEX.md` G-7
**State:** Closed — Forced by PARTITION.md

**What must be decided.** Fourteen named artifacts fall outside every lane's OWNS list. The guard is fail-closed,
so the first pull request touching any of them fails as `UNOWNED` — correct behaviour that stalls the work
invisibly. Each must be assigned **before the first lane task that needs it**, or a lane will create it in whatever
directory seems reasonable and two lanes will create it twice.

| # | Path or artifact | Raised as | Blocks | Gates |
|---|---|---|---|---|
| a | `changes/*.yaml` (change manifests, §25) | `LA-03`; `L1-00` DR #3 | L1 governance-registry schema work | `Ph2` |
| b | `scenarios/*.yaml` (§72.5) | `LA-03`; `L1-00` DR #3 | same | `G3` |
| c | Leave records (§7.2, source of truth for leave and the company working calendar) | `L1-00` DR #3; `D-L4-P4-03` | L1's `availability` transition rule; L4 `L4-T406` rule R4 | `Ph2` |
| d | `registries/ai-toolchain.yaml` (§52.6; §99.2 subsystem K → L5, but L5 owns no `registries/**`) | `L1-00` DR #1 | any L1 file that would create it | `Ph2` |
| e | Non-workflow `templates/**`, incl. `templates/intake-gap-assessment.md` (§96.6) | `LA-03`; `DECISION 2`; `DR-L0-07-A` | onboarding `OT-INTAKE` for every product | `Ph2` |
| f | `runbooks/**` | `LA-03` | L5 and L3 runbook tasks | `Ph3` |
| g | The Constitution file — L0's "root files" cover it **only if** placed at repository depth 0 | `LA-03` | onboarding `OT-P4` (`CONTEXT.md` reference) | `Ph4` |
| h | Provisioned dashboard JSON | `LA-03`; belongs to whoever gets **H** — see **REG-001** | Founder view v0 | `Ph2` |
| i | The compliance-artifact register | `LA-03` | governance-tier work | `G2` |
| j | The Performance Framework Registry (§77.1) | `LA-03`; `framework_registry_path` (`lanes/L1-03` §1) | L1 `R14` (§77.5 revision integrity audit) | `P2` |
| k | `.github/` **non-workflow** files in `control-plane` | `LA-03`; `master/03` §1.2 assigns them to L0 as though frozen; `INDEX` C-9 | any PR adding a `.github/` non-workflow file | `Ph0` |
| l | `derived/**` — the D107 records-head anchor destination and the D93 reconciler write-scope allowlist | `DR-3.1` (`lanes/L3-03` §2) | L3 `T06`, `T10` | `Ph3` |
| m | `tools/fleet/**` — the §33.3 blast-radius generator, the §61.4 fleet-migration PR script, the change-matrix scaffold | `D-L2-01` (`lanes/L2-00` §9) | L2 `L2-T700` (AT-024 fleet half); every §33.3 and §61.4 task | `Ph4` |
| n | The programme ledger and generators — `docs/plan/**` vs an unclaimed `tools/ledger/**` | `D-08-1` (`master/08` §2) | `master/08`'s whole generator set | `Ph0` |
| o | `tools.yaml` estate-host registration (D69, "registered before first use") | `DR-L0-07-E` (`lanes/L0-07` §5.1) | onboarding floor tracking for estate hosts | `Ph1` |
| p | The `product-template` repository and the eight live product repositories | `LA-03`; `master/01` §2.1 | the whole Onboarding track — see **REG-057** | `Ph2` |

**Options, applying uniformly to every row.**

| # | Option | Trade-off |
|---|---|---|
| **A** | Assign each to the nearest lane by dependency and add every path to `lane-paths.tsv`, `CODEOWNERS` and the §2 manifest **in one commit** with one decision record | One commit, one re-freeze, one review. `master/01` §9 states this requirement explicitly for `LA-01`/`LA-03` |
| **B** | Claim each for L0 under `docs/**` or a new L0 root path | No lane change; L0 becomes the author of fourteen artifacts, several of which are domain content L0 does not hold |
| **C** | Leave unassigned; each stays fail-closed until its first PR | Zero work now; guarantees fourteen separate mid-build stalls, each at a time L0 did not choose |

**In force.** The guard's `X` rule — `UNOWNED`, blocked for everyone, escalates to L0 (`L0D-04`). Rows **h**, **j**
and **b** additionally depend on **REG-001**: dashboard JSON belongs to whoever gets **H**, the framework registry
to whoever gets **P**, and `changes/`+`scenarios/` to whoever gets **O**.

---

#### REG-018 — The L1 validator invocation contract

**Gates** `Ph1` · **Decided by** L0 (`L0D-01`) · **Input from** L1 (the entry point it is building)
**Raised as** `DECISION REQUIRED #4` (`lanes/L1-00` §12) · `D-L2-02` (`lanes/L2-00` §9, `lanes/L2-05` §1) ·
`DR-L1-06-B` (`lanes/L1-06` §5) · `D-2` (`lanes/L1-04` §4)
**State:** Closed — Forced by PARTITION.md

**What must be decided.** §99.2 names subsystem B *"Schema validation and CI gate engine"* and assigns it to L1;
PARTITION gives `.github/workflows/**` to L2. **L1 owns the engine and L2 owns the trigger.** §98.2 Phase 1's
completion check requires the minimal `exceptions.yaml` validator to be *"active in control-plane CI"* — an L1 DoD
item that only an L2-owned file can make true. `contracts/**` must therefore publish the stable entry point: the
command line, the exit-code semantics, and the machine-readable output shape including **a stable, greppable rule
identifier** in every diagnostic.
**Blocks.** L2 `L2-T106`, `L2-T107` (charter DoD-06 partial); L1 `DoD-8` and `DoD-9`, which L1 cannot mark done
alone; L1 `L1-06-02` onward — without a stable diagnostic, layer L-A degrades to exit-code-only and the negative
corpus can no longer prove **which** rule fired.

| # | Option | Trade-off |
|---|---|---|
| **A** | Publish `contracts/cli/registry-validate.yaml`: one entry point, exit `0` valid / non-zero invalid, one JSON object per finding on stdout carrying `rule_id`, `severity`, `file`, `pointer` | L1 and L2 both build to it without either touching the other's tree; the rule id is what makes `L1-06`'s `must_contain` assertions stable across refactors |
| **B** | Publish only the command line and exit codes; diagnostics remain free text | Cheaper to freeze; `L1-06`'s corpus can then prove only that *something* was rejected, not which rule fired |
| **C** | Each validator is a standalone executable under `validators/registry/bin/` with documented exit codes and no unified interface | L1's stated fallback. L2 must then hard-code a list of executables, which breaks on L1's first addition |

**In force.** `lanes/L1-00` §12: *"Build every validator as a standalone executable under `validators/registry/bin/`
with documented exit codes. Do not create, edit or propose any file under `.github/`."*

---

#### REG-019 — The record write interface, and what "signed by the writing identity" means

**Gates** `Ph1` · **Decided by** L0 (`L0D-25`, `L0D-03`) · **Input from** L5 (the credential) and L4 (the schemas)
**Raised as** `D-L2-03` (`lanes/L2-00` §9, `lanes/L2-05` §1) · `D-L4-02` (`lanes/L4-01` §"DECISION REQUIRED") ·
`D-L4-P3-02` (`lanes/L4-03` §5)
**State:** Closed — Forced by spec

**What must be decided.** Three things in one contract. **(a)** The records-writer secret name, the target
repository, and the record and event schema paths for `records/deployments/`, `records/uat/`,
`records/restore-tests/`, `records/eval/` and `events/`. **(b)** Which mechanism satisfies **D107**'s *"the
records-writer signs every commit, and a commit on the default branch that is unsigned, or signed by any other
identity, is Blocking drift"*. **(c)** What enforces the review §97.1 line 8841 requires — *"human edits to records
travel the normal review lane, as pull requests **under branch protection**"* — given that §40.1 (D89) gives the
records repository *"no protection rules"* and PARTITION restates D107 as a no-bypass ruleset only.
**Blocks.** L2 `L2-T544`, `L2-T545` and **every workflow that writes a record** (charter DoD-14, DoD-15) —
§97.2 makes the deployment-record and event writes **required, failing** steps, so a guessed interface makes every
deploy fail; L4 `L4-T313`, `L4-T314` enforcement half.

| # | Option (for **b**) | Trade-off |
|---|---|---|
| **A** | REST **Contents API** with the installation token; GitHub signs with its own web-flow key, the commit shows **Verified**, author and committer are the App's bot identity | Satisfies a `required_signatures` ruleset rule with no key distribution. The signing *key* is GitHub's; the *identity* is the App's |
| **B** | A dedicated GPG or SSH signing key in the fifth secrets tier (§40.1), pushed with `git push` + `commit -S` | The signing key is the writer's own. Adds a key to rotate on the quarterly fifth-tier cadence and a key-distribution problem on every runner |

| # | Option (for **c**) | Trade-off |
|---|---|---|
| **A** | A required status check that is **not** review protection — `validate-human-record.sh` | Honours D89 and D107 unchanged; the "review" is mechanical validation, not human review, which line 8841 may not have meant |
| **B** | Review protection on `control-plane-records`, overriding D107 | Satisfies line 8841 literally; contradicts an Appendix A decision, which is `L0D-06`-class |
| **C** | Convention only, with `validate-human-record.sh` as the sole mechanical control | Cheapest; leaves line 8841 unenforced and must be recorded as an accepted risk (`L0D-24`) |

**In force.** L4 builds `validate-human-record.sh` and makes it runnable as a status check; **L4 requests no branch
protection and no ruleset change on `control-plane-records`** and records the open question verbatim in
`CONTRIBUTING.md`.

---

#### REG-020 — The record stores §97.2 does not list

**Gates** rolling, per row · **Decided by** L0 (`L0D-03`; a §97.2 table amendment is `L0D-06`) · **Input from** L4
**Raised as** the eight raisers named per row
**State:** Closed — Resolved by FD-022 (2026-09-02): Option A (§97.2 amendments) for rows a–g, Option B (route to existing store) for row h. FD-053 (2026-09-06) supplements row a with path `records/verification-blocks/`.

**What must be decided.** §97.2's canonical record-store table is the closed list every metric derives from
(invariant 46, §103 preamble). Eight write paths in the plan have no store in it. Each row is either a §97.2 table
amendment or a routing to an existing store — **never a resemblance match**.

| # | Store needed | Raised as | Blocks | In force |
|---|---|---|---|---|
| a | Verification-block record (§23.1, §27) | `D-L2-08` (`lanes/L2-03` §5) | L2 `L2-T174` step `verification-block` | step present, **exits non-zero** with `VERIFICATION_BLOCK_STORE_UNRESOLVED` |
| b | Exceptional-authorisation record for each rollback run (§27.2, §42.3) | `D-L2-10` (`lanes/L2-03` §5) | L2 `L2-T176` step `exceptional-authorisation-record` | step present, **exits non-zero** with `EXCEPTIONAL_AUTH_STORE_UNRESOLVED` |
| c | Provider-side attestation record (§40.2, §53.1) | `D-L3-02` (`lanes/L3-01` §1) | L3 `L3-01-11` (CMP-09) | none — the task STOPs |
| d | Production-restore record (§44.5, §53.1) | `D-L3-03` (`lanes/L3-01` §1) | L3 `L3-01-18` (CMP-16) | none — the task STOPs |
| e | Reconciliation-run record and repair record (§53.1, §26.4) | `DEC-L3-02-03` (`lanes/L3-02` §2) | L3 `T03`, `T04`, `T08`, `T13` | none — *"There is no default and no placeholder"* |
| f | Sunset-runbook RVR results (§18.4 rows 3, 5, 8, 9, 10) | `D-L4-P3-01` (`lanes/L4-03` §5) | the sunset mechanisms of `L4-T304` | `rvr-inputs.yaml` declares **four** mechanisms, no sunset mechanism and no placeholder store |
| g | Scorecard scan results (§92.3, §19.2) | `D-L4-P5-01` (`lanes/L4-05` §6) | nothing | `metrics/ingest/scorecard.yaml` carries `source_store: PENDING-D-L4-P5-01`; the drop measure renders `unarmed — not yet instrumented` under D77 and **cannot render as a miss** |
| h | `records/verification/gsd-pin` — read by `master/07` §5.3 `A4`, placed by `master/00` EC-9 at `records/decisions/plan-checker-capability-verification.yaml`, and absent from `master/01` §6.3's sixteen-store list | `master/INDEX.md` R-7 | `master/07` `A4` | the check tests for a store that does not exist and can never pass |

**Options, applying per row.** **A** — amend the §97.2 store table and publish the path, the id prefix and the
schema id (this is a contract change and a `record_schema_version` decision). **B** — route to an existing store
and publish the query. **C** — declare the surface collector-only and exempt from invariant 46, recorded as an
accepted risk. Trade-off is uniform: **A** costs a schema and a store; **B** costs the ability to query that class
separately for ever; **C** costs a metric that can never be derived from a canonical record.

**Binding on every row.** *"L4 must not invent a store directory, and must not route a result into an existing
store by resemblance"* (`lanes/L4-03` §5). The same rule binds L2 and L3.

---

#### REG-021 — The closed `event_type` enum: publication mechanism and identifier list

**Gates** `Ph1` — §97.3: *"the enum ships populated in Phase 1 so no workflow ever writes an untyped event"* ·
**Decided by** L0 (`L0D-03`) · **Input from** L4 (the taxonomy), L1 (the carrier file)
**Raised as** `LA-05` (`master/01` §9) · `D-L4-01` (`lanes/L4-00` §9) · `DECISION-L1-02-B` (`lanes/L1-02` §3) ·
`L1-D05` (`lanes/L1-05` §1) · `D-L2-08` (`lanes/L2-04` §4) · `D-L4-P3-03` (`lanes/L4-03` §5)
**State:** Closed — Forced by spec

**What must be decided.** §97.3 is explicit: the enum is declared in `platform.yaml`, control-plane CI rejects any
event whose `event_type` is absent from it, identifiers are *"lower-case, underscore-separated, never renamed once
shipped"*, and a new type is *"a governed addition to the enum and to this taxonomy"*. `platform.yaml` is under
`registries/**` (**L1**); the taxonomy content is **L4**'s domain; every workflow that emits an event (**L2**,
**L3**, **L5**) depends on it. §97.3 supplies the taxonomy as roughly 110 **prose phrases**, not identifiers —
turning *"plan approved (Gate 1) with `agent_authored` flag"* into `plan_approved` is a naming act. Three write
paths have **no** taxonomy entry at all: support-loop closure, deletion request, work-item closed
(`D-L4-P3-03`).
**Blocks.** L1 `L1-107` (seeding `platform.yaml`); L2 `L2-T509`, `L2-T512`; L4 `L4-T305` (`support_loop_closure`,
`deletion_provider_confirmation`) and `L4-T308` (estimate-at-close emission).

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended by `master/01`) | L1 owns `platform.yaml` and transcribes L4's taxonomy **verbatim** from the frozen contract surface `C2` — a one-way copy, so no lane authors into another lane's file. Adding an event type is a **CCR against C2**, never a direct edit by the emitting lane | Preserves the glob and PARTITION rule 4; every addition is reviewable in one place. Costs a CCR round for each new event type |
| **B** | The enum is a separate file under `schemas/records/**` (L4) that `platform.yaml` references | Puts the taxonomy with its author; requires a §52.6 amendment — a twenty-ninth-entry change, which §52.6 itself governs (*"any proposal for a new control-plane artifact must state which existing file cannot hold the content"*) |
| **C** | L4 publishes `metrics/taxonomy/event-types.yaml` for L1 to embed | L4's own stated alternative. Same effect as A with the source outside `contracts/**`, so nothing freezes it |

**In force.** L1's `platform.v1` schema declares the field and validates its **shape**; `L1-107` seeds it from
`contracts/` if a file there defines it and otherwise seeds it **empty** (`event_type: []`), with the schema
permitting empty. **L1 never invents an event-type token.** L4's three unmapped rows carry `event_type: unarmed`
and the emitter **fails closed** with `EMIT FAIL unknown-event-type` rather than writing an untyped event; a record
without its event is never written — `emit_pair` rolls the record back.
**L4 must not** write to `registries/platform.yaml` under any circumstance.

---

#### REG-022 — The metric register content boundary (`os-health.yaml`)

**Gates** `G1` for the computation job; `Ph2` for the schema · **Decided by** L0 (`L0D-22`) · **Input from** the Team Lead (§52.6 names them the owner of the file's content)
**Raised as** `LA-04` (`master/01` §9) · `D-L4-02` (`lanes/L4-00` §9) · `L1-D04` (`lanes/L1-05` §1)
**State:** Closed — Forced by spec

**What must be decided.** §52.6 places `os-health.yaml` in the control-plane repository as the metric register —
*"definitions, sources, thresholds, time windows, baselines, drift classes, tolerances, expected interpretations,
known limitations, owners, activation dependencies, defined action on breach"*. Its **path** is `registries/**`,
which is **L1**'s; its **content** is the Team Lead's; its **consumers** are L4's metrics and L3's drift
classification; and the health-computation job that reads it is a `G1` deliverable under unassigned subsystem
**O** or **H** — see **REG-001**. §84.6 requires eight attributes on each of the 46 signals, `known_limitations`
*"is never empty"* and where genuinely absent must read exactly `none-known` — *"a claim a named owner made"*.
**Blocks.** L1 `L1-605` population (not the schema); L4 `DoD-13`, `DoD-14`, `DoD-15` integration.

| # | Option | Trade-off |
|---|---|---|
| **A** (recommended by `master/01`) | Leave the file with L1 — **schema only** — and route the computation job by **REG-001** | Preserves the glob; §52.6 already separates file ownership from schema ownership. The 46 rows stay unauthored until the Team Lead writes them |
| **B** | Carve `registries/os-health.yaml` to L4 as a named exception to the `registries/**` rule | Breaks "one owner per path" at **file** granularity, not glob granularity. Puts the register with its computation |
| **C** | L4 publishes `metrics/register/metric-declarations.yaml` for L1 to embed | Same shape as **REG-021** option C; nothing freezes the source |

**In force.** L1 builds the schema and the validator (`L1-605`), enforcing the ten required attributes, the
`SIG-NN` id pattern and the closed drift-class enum; `registries/os-health.yaml` ships with `signals: []`.
**L4 must not** write to `registries/os-health.yaml` under any circumstance.

---

#### REG-023 — The calibrated values, and their stated initial numbers

**Gates** rolling, per row · **Decided by** L0 (`L0D-17`, `L0D-22`) · **Input from** nobody
**Raised as** `L0D-17` (`L0-00-charter.md` §5.1) · `L2/P1/DEC-C` (`lanes/L2-01` §1) · `DECISION REQUIRED #3`
(`lanes/L0-06` §5) · `D-EE-5` (`master/05` §1)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** §84.6 and **D102** establish the convention: a calibrated value is configuration with a
**stated initial value**, changed only by a recorded decision. `C-02` forbids any lane choosing one. These are the
values the plan set actually consumes and has not recorded.

| # | Value | Stated initial | Raised as | Blocks | Gates |
|---|---|---|---|---|---|
| a | "Sustained", for SIG-07 / SIG-08 / SIG-30 | 6 consecutive weeks | `L0D-17` | L4 signal computation | `G1` |
| b | Bootstrap-log staleness window (§95.4) | 7 days | `L0D-17`; `L0-06` DR #3 | L0 `L0-06-12`; the SIG-39 detector | `Ph1` |
| c | Bootstrap exception lifetime and review offset (§95.2 exhibit, spec L8666–L8668) | 91 days / 30 days | `L0-06` DR #3 | nothing — `L0-06-03` transcribes the exhibit | `Ph1` |
| d | Triage budget per product per pass (§94.3) | 5 minutes | `L0D-17` | attention-ledger derivation | `P1` |
| e | AI-eval triage block (§94.3) | 30 minutes | `L0D-17` | same | `P1` |
| f | SIG-42 regression tolerance (§52.2) | 5 percentage points | `L0D-17` | L4 signal computation | `G1` |
| g | Scope-growth threshold (§29.5) | as §29.5 states | `L0D-17` | board automation | `G3` |
| h | `FREEZE_TZ`, `CORE_HOURS_END`, `OBSERVATION_WINDOW_MINUTES` (§34.2's *"15:00 Friday"* has no timezone and "core hours" has no numeric end) | **none stated anywhere** | `L2/P1/DEC-C` | L2 `L2-P1-T04`; `.github/workflows/gate-freeze.yml` | `Ph4` |
| i | "Detection has run clean for weeks" before auto-repair (§98.3, §99.4 item 6) | **none stated** | `D-EE-5` | L3 `L3-P4` entry criterion `L3P4-N2` | `Ph5` |
| j | Per-product provider attestation window (§40.2, *"calibrated configuration; initial value monthly"*) | monthly | `D-L3-02` | L3 `L3-01-11` | `Ph3` |

**Options for row (i)**, the only row whose raiser published a real option set: **O-5A** 14 consecutive days, zero
unexplained findings, canary found on every run — fastest, thinnest evidence; **O-5B** (recommended) 28 days plus
**≥1 real Blocking finding correctly raised and closed** — matches "weeks" plural and proves the detector fires,
not merely runs; **O-5C** 42 days plus a full restore-test rotation cycle — safest, delays the highest-value repair
classes. `master/05` writes `L3P4-N2` against O-5B and carries the number in **one variable**.
**Options for row (h).** No option set exists, because the spec supplies no candidate values. L0 states four
literals into `templates/workflows/freeze-policy.env`.

**In force.** Rows (a)–(g) and (j): the stated initial value, recorded as a transcription with its spec line
cited, never as a choice. Row (h): tasks `L2-P1-T05`/`T06` and the freeze gate **fail closed** with
`DECISION REQUIRED L2/P1/DEC-C unanswered`. Row (i): `L3-P4` does not begin.

---

#### REG-024 — Drift classes the spec assigns to nothing

**Gates** `Ph3` · **Decided by** L0 (`L0D-22`; §53.5 reserves class assignment to the exception-approval authority) · **Input from** nobody
**Raised as** `DEC-L3-02-01`, `DEC-L3-02-04` (`lanes/L3-02` §2) · `L3-D4` (`lanes/L3-06` §5) · `DR-3.2` (`lanes/L3-03` §2) · `D-L3-04` part (b) (`lanes/L3-01` §1)
**State:** Closed — Forced by spec

**What must be decided.** §53.4 states there is exactly one drift severity scale — Green / Amber / Red / Blocking —
that *"class assignment lives in configuration and is reviewable; it is not decided ad hoc during an incident"*,
and that *"security drift and production environment drift are never classified below Red"*. Five findings have no
class.

| # | Finding | The gap | Blocks |
|---|---|---|---|
| a | **Red-class response level** | §53.2's five levels declare an "Applies to" scope for Green (L1), Amber (L2) and Blocking (L4). **No level names Red** | L3 `T02`, `T04`, `T14` |
| b | **Orphan severities `High` and `Medium`** | §12.2 grades the sixteen orphan types `Blocking`/`High`/`Medium`; §53.4 retires older vocabulary *"exactly once, here"* and does not cover `High` or `Medium`. SIG-05 is fixed at `Blocking` | nothing — interim defined |
| c | **The permanent seeded canary finding** | A permanent finding consuming budget would exhaust §53.4's hard portfolio budgets by construction (*"up to 2 open Amber per product … Red is deliberately held flat at 3 portfolio-wide"*); excluding it in code would violate the same paragraph | L3 `T01` config |
| d | **Comparison-count shortfall** (`rows_compared < rows_declared`) | §53.1 requires per-registry comparison counts *"so that a silently narrowed comparison is itself visible drift"* and assigns the finding no class | L3 `L3-01-20` |
| e | **A sixth repair class?** | §53.2 Level 3 enumerates five permitted repairs as a closed list; §53.1 carries a separate row — *"`product.yaml` lifecycle \| Renovate, monitoring and CI configuration \| Auto-repair where safe; alert otherwise"* — which is not one of the five | L3 `T06` |

**Options.** (a): **A** Red behaves as Level 2 **plus** Founder-view surfacing; **B** Red is its own response level.
A is cheaper and changes no notification code; B changes the §53.4 drift-budget arithmetic and the §93 Founder view,
which L3 does not own. (b): **A** map `High`→Amber, `Medium`→Green; **B** leave both outside the scale and count
them separately for ever. (c): **A** `green`, `counts_against_budget: false` — the only class whose semantics do
not change the budget arithmetic, since §53.4 gives Green no budget; **B** a named exclusion at any class, which
requires the exclusion to be configuration, not code. (d): any of the four classes; §53.1's own framing (*"itself
visible drift"*) argues against Green. (e): **A** `not-a-repair-class` — the §53.1 row raises Level 2 and stops;
**B** a sixth class id with its own stricter-only predicate, which widens the highest-privilege automation in the
system and §99.6 risk 6 makes that an explicit governance act.

**In force.** (b): every orphan finding carries `orphan_severity` verbatim from §12.2; `Blocking` also carries
`drift_class=BLOCKING`; `High` and `Medium` carry `drift_class=None`, are reported, and are **excluded from every
drift-budget count** — the D77 arming discipline applied to a class with no declared home. (c):
`validators/drift/canary/canary.yaml` carries `drift_class: green`, `counts_against_budget: false`, in
**configuration** so a change is a config edit and never a code edit. (a), (d), (e): none — the named tasks STOP.

---

#### REG-025 — The blocking check-run name, and required-context composition

**Gates** `Ph1` · **Decided by** L0 (`L0D-01`) · **Input from** nobody
**Raised as** `DEC-L3-02-02` (`lanes/L3-02` §2) · `DR-L3-01` (`lanes/L3-00` §10) · `D-1` (`lanes/L1-04` §4) ·
`D-L2-07` (`lanes/L2-02` §4)
**State:** Closed — Forced by spec

**What must be decided.** Three names that three lanes must match exactly. **(a)** §11.3 names
`control-plane/blocking-drift` as a required status check and §40.1 grants the reconciler check-run write for
*"exactly one named check"*, adding that *"a check run published under that name by any identity other than the
reconciler is Blocking drift"* — but the specification never writes the string, nor the App slug that alone may
publish it. **(b)** §11.3 lists *"contract validation"* in prose; branch protection needs a literal context string,
identical in the branch-protection template, in the workflow job name, and in §53.1's template comparison.
**(c)** GitHub composes a reusable-workflow call's check-run name as `<caller job id> / <called job id>`, so the
templates emit `build / artifact` and nothing named `build`, while `templates/workflows/required-checks.yaml`
(frozen by `L2-T003`) lists the plain names `build`, `artifact-digest-recorded`, `sbom-emitted`.
**Why it must be one decision.** §98.2 Phase 1 warns that a required check name no workflow emits blocks every pull
request indefinitely; L5 copies these names into branch protection and L3 compares them in the §53.1 template
comparison. Changing either side unilaterally desynchronises three lanes.
**Blocks.** L3 **every** `reconciler/levels/` Level-4 task, `T11`, `T12`, `T14`; L1 `L1-04-08`; L2 the phase-4
and phase-6 pipeline contexts, charter `DoD-06` and `DoD-09` for three contexts; L5 `L5-T07`.

| # | Option | Trade-off |
|---|---|---|
| **A** | Publish `contracts/reconciler/checkrun.yaml` (`blocking_check_name`, `expected_app_slug`) and `contracts/ci/required-contexts.tsv` carrying the **composed** names, and amend `required-checks.yaml` to match, recording the composition rule | One source, three consumers, and the composition rule is written down rather than rediscovered. Costs one amendment to a file `L2-T003` already froze — which is a CCR, not an L2 edit |
| **B** | Direct that required-context jobs be **normal jobs** in the product workflow rather than reusable-workflow calls | Plain names work unchanged; L0 must then state how such a job obtains the control-plane build surface without a reusable-workflow call |

**In force.** None — L3's Level-4 tasks STOP. L2's artifacts are correct under either resolution and are built
regardless; the blocker is filed by `L2-T404`.

---

#### REG-026 — Reconciler identity, write scope and the records-head anchor

**Gates** `Ph3` · **Decided by** L0 (`L0D-25`, `L0D-04`) · **Input from** L5 (the asset-inventory entry)
**Raised as** `L3-D3` (`lanes/L3-06` §1) · `DR-3.1` (`lanes/L3-03` §2) · `D-L3-04-02` (`lanes/L3-04` §1)
**State:** Closed — Forced by spec

**What must be decided.** **(a)** Is the reconciler credential a **GitHub App installation token** or a
**fine-grained PAT**? §40.1 allows either; **D80** states a preference (*"machine identities prefer GitHub Apps
over seat accounts where the mechanism allows"*) without deciding. The choice changes the auth code path and the
`AT-110` probe shape. **(b)** Which organisation login do `--live` smoke runs target? **(c)** **D107** requires the
reconciler to write the records-repository head SHA *"into the control-plane repository, which is fully
protected"*, and **D93** narrows *"the reconciler's own write scope … to generated `derived/**` files"* — but
`derived/**` is assigned to no lane (**REG-017** row l). L0 must state the anchor destination path, who owns
`derived/**`, and the **literal contents** of the write-scope allowlist. **(d)** §40.1 requires each credential's
exact permission set published in its inventory entry, and §49.1 requires that entry to carry rotation cadence, a
named rotator holding `devops`, a runbook link and an out-of-window alert-config owner — and `assets/**` is **L5**'s.
**Blocks.** L3 `L3-P5-06` (`AT-110` probe), `L3-P5-07` (behavioural envelope), `T06`, `T10`; L3 `L3-04-02`
(`provision verify-credential-envelope`).

| # | Option (for **a**) | Trade-off |
|---|---|---|
| **A** | GitHub App installation token | Matches D80's stated preference; no seat consumed; installation scoping is per-repository and reviewable |
| **B** | Fine-grained PAT | Simpler to issue and rotate; a PAT is bound to a human account, which is exactly what D80 steers away from |

**In force.** `reconciler/config/anchoring.yaml` (L3-owned, created by `T10`) carries
`anchor_path: derived/anchors/records-head.yaml` and `write_scope_allowlist: [derived/**]` — *"the narrowest
reading of D93 and D107 together, one line to change"*, with `T06` enforcing the allowlist **as data, never as
code**. For (d), the CLI declares and self-tests the **minimum** set the tasks actually need in
`tools/provision/provision/security/envelope.yaml`, which is L3-owned and is the input L5 transcribes into the
inventory. Everything else is fixture-backed and proceeds.

---

#### REG-027 — Which repair class is enabled first, and in what order

**Gates** `Ph5` · **Decided by** L0 · **Input from** nobody
**Raised as** `DR-L3-02` (`lanes/L3-00` §10)
**State:** Closed — Forced by spec

**What must be decided.** §99.6 risk 6 requires *"repair classes enabled one at a time"*. §53.2 Level 3 lists six
candidates: Team membership sync, CODEOWNERS regeneration, label and board field sync, re-applying declared branch
protection, removing expired assignments, removing expired access. The order is a risk judgment, not a spec fact,
and choosing which org-admin write goes live first is exactly the judgment the partition reserves to L0.
**Blocks.** Every `reconciler/repair/` task after the stricter-only guard.
**Options.** **A** — publish an ordered list of the six with the gate each must pass before the next is enabled
(the raiser's requested output). **B** — enable none in V1 and run detect-only through Foundation, recorded as a
scope decision. A costs six gates; B costs the §99.4 item 6 auto-repair capability and must be a recorded decision,
not a slip.
**In force.** None — the repair tasks after the stricter-only guard do not start. **F-13** binds regardless: no
code path may auto-repair toward a looser state (invariant 81, `AT-033`, §99.6 risk 6).

---

#### REG-028 — The seeded canary: what is planted, where, and how it is labelled

**Gates** `Ph3` · **Decided by** L0 · **Input from** L1 or L5 (whichever registry or access artifact carries it)
**Raised as** `DR-L3-03` (`lanes/L3-00` §10) · `D-L3-04` part (a) (`lanes/L3-01` §1) · `DR-3.2` (`lanes/L3-03` §2, the class half — see **REG-024** c)
**State:** Closed — Forced by spec

**What must be decided.** §53.1 requires *"a permanent seeded drift record — a deliberately planted, clearly
labelled mismatch in the comparison set — exists at all times, and every reconciliation run MUST find it."* Which
comparator carries it, where the mismatch lives, and how it is labelled so no operator mistakes it for real drift,
is a design choice with a security constraint: it **must not** be planted in a real security control, because
§53.4 holds that *"security drift and production environment drift are never classified below Red"*.
**Why L0.** The canary must be planted in a registry (**L1**) or an access artifact (**L5**) and read by **L3** —
a three-lane contract, and a governance placement decision rather than an implementation one.
**Blocks.** L3 `reconciler/canary/**` and `L3-01-20`, and therefore `AT-102`; `IG-04`'s canary assertion.
**Options.** **A** — plant it in a purpose-built, clearly-labelled row of a low-consequence registry (candidate:
a reserved `topology.yaml` entry), so no real control is falsified. **B** — plant it in the branch-protection
template comparison, where the mismatch is visible but the artifact is a real security control — **excluded by
§53.4** and listed only so it is visibly excluded. **C** — synthesise the canary inside the comparison set at run
time rather than planting it in data, which makes it a code path the credential being checked can rewrite and
therefore not a control (§53.1).
**In force.** None for placement. The canary's *absence* is already handled: `T03` treats it as a **FAILED run at
Level 5**, a different finding with a different class, so a missing canary is never silently a clean run.

---

#### REG-029 — The `gap-window` mark's carrier

**Gates** `Ph3` · **Decided by** L0 (`L0D-03`) · **Input from** L4
**Raised as** `DR-L3-04` (`lanes/L3-00` §10)
**State:** Closed — Forced by spec

**What must be decided.** §53.7 requires every record produced during a gap window to carry the `gap-window` mark
until re-verified. Records are **L4**'s; the mark is set by **L3**'s gap procedure. The field lives in a record
schema L3 does not own and must not edit.
**Blocks.** L3's gap-window procedure; L4's record schemas that must carry the field.
**Options.** **A** — a common field on the shared record envelope in `contracts/`, so every store carries it
uniformly. **B** — a per-store field on only the stores a gap window can affect, which is smaller but requires the
affected set to be enumerated and re-enumerated as stores are added. **C** — a separate `records/gap-windows/`
store that names the affected id ranges, which keeps record schemas untouched at the cost of a join on every read.
**In force.** None — L3 does not set a field that does not exist and does not edit `schemas/records/**`.

---

#### REG-030 — The scan toolchain: security scanner, licence scanner, SBOM generator

**Gates** `Ph2` · **Decided by** L0 (`L0D-24`; `C-10`, a tool not already named in the spec) · **Input from** nobody
**Raised as** `L2/P1/DEC-A` (`lanes/L2-01` §1)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** §33.2 requires *"unit tests, integration tests, build, security scan, licence scan,
contract validation, registry and assignment validation, environment parity check, and the verification contract
check"*; §48.2 requires a licence scanner with delta gating; §48.3 requires an SBOM *"beside the artifact digest —
same pipeline step, same storage discipline, same immutability"*. **No section of the specification names which
scanner, which licence scanner or which SBOM generator**, and §99.5's technology-shape decisions are silent on all
three. L0 must return exactly nine values for `templates/workflows/scan-tools.env`:
`SECURITY_SCANNER_IMAGE`, `SECURITY_SCANNER_DIGEST` (`sha256:` + 64 hex), `SECURITY_SCANNER_SARIF_PATH`,
`LICENCE_SCANNER_IMAGE`, `LICENCE_SCANNER_DIGEST`, `LICENCE_SCANNER_REPORT_PATH`, `SBOM_GENERATOR_IMAGE`,
`SBOM_GENERATOR_DIGEST`, `SBOM_FORMAT` (`spdx-json` or `cyclonedx-json`).
**Why L0 and not L2.** §48.2 makes the scanner's *"policy configuration a control-plane artifact, versioned like
every other reusable configuration"*, which makes the choice a platform change under §61 with a canary set.
**Blocks.** L2 `L2-P1-T01` (writing the file), and therefore `L2-P1-T05` (`ci.yml`) and `L2-P1-T06` (`build.yml`).
**Options.** No option set exists in the plan, because no candidate tool is named anywhere in the specification.
The **shape** of the answer is fixed: three images, each **pinned by digest** (invariant 85), and one SBOM format.
The trade-off is uniform — any tool chosen becomes a control-plane artifact under §61's platform-change discipline,
so the cost of changing it later is a canary rollout, not an edit.
**In force.** Tasks `L2-P1-T05` and `L2-P1-T06` STOP at their stated STOP rule, and the workflow bodies fail closed
with `DECISION REQUIRED L2/P1/DEC-A unanswered`.

---

#### REG-031 — Per-product deploy and restore command fields on `product.yaml` (a CCR)

**Gates** `Ph4` · **Decided by** L0 (`L0D-06`, approving or denying a Contract Change Request) · **Input from** nobody
**Raised as** `L2/P1/DEC-B` (`lanes/L2-01` §1)
**State:** Closed — Resolved by FD-020 (2026-09-02): Option B — deny CCR; extend §33.1 standard command table with `make deploy` and `make restore`.

**What must be decided.** The reusable `deploy-staging`, `deploy-production`, `migrate`, `restore-production` and
`restore-test` workflows must invoke *something* in the product repository. §15.1's `deployment:` block declares
`build`, `artifact_type`, `artifact_registry`, `rollback_supported`, `rollback_method`, `progressive_delivery` —
and **no command, entry point or script path**. §33.1 fixes eight standard commands
(`make setup|dev|test|uat-local|migrate|reset|health|parity`); `make migrate` is among them, and there is **no**
standard command for deploy or for restore. L0 rules on a CCR against `product.yaml` naming whether `deployment:`
gains `deploy_command:` and `restore_command:`, and confirming that `make migrate` is the entry point `migrate.yml`
invokes.
**Blocks.** Not the workflows — see **in force** — but **L3's substitution table** in `create-product`.
**Options.** **A** — grant the CCR: two new fields on `product.yaml`, validated by L1's schema, substituted by L3.
**B** — deny it and extend §33.1's standard command table with `make deploy` and `make restore`, which keeps
`product.yaml` unchanged and moves the variation into the product's own `Makefile`. A costs a contract version; B
costs every product a `Makefile` change and makes the eight-command table nine or ten.
**In force, and this is not a workaround.** Every reusable workflow declares these as **required `workflow_call`
inputs with no default**, and the caller templates carry the literal placeholders `__DEPLOY_COMMAND__` /
`__RESTORE_COMMAND__` for L3's `create-product` to substitute. A required input with no default **fails closed**
if a caller omits it, satisfying invariant 80 and §64.2. The workflows are therefore buildable and testable now.

---

#### REG-032 — The filename of the rollback workflow

**Gates** `Ph4` · **Decided by** L0 (`L0D-01`) · **Input from** nobody
**Raised as** `D-L2-05` (`lanes/L2-00` §9, `lanes/L2-05` §1)
**State:** Closed — Forced by spec

**What must be decided.** §33.2's required-workflow list does **not** include a rollback workflow, yet §27.2
mandates *"a dedicated rollback workflow"* and §37.3 names *"the rollback workflow"* among the five privileged
workflows requiring the actor gate. The filename becomes a required-workflow name checked by §15.5 contract
validation and by reconciliation's §53.1 template comparison, so choosing it unilaterally desynchronises L1, L3
and L5.
**Blocks.** L2 `L2-T133`, `L2-T309`, `L2-T554` (the fifth privileged workflow), `L2-T701`; charter `DoD-05`; L1's
required-file validation; L3's template comparison.
**Options.** **A** — `rollback.yml`, added to §33.2's required list by amendment, so all three consumers read one
name from `contracts/`. **B** — fold rollback into `deploy-production.yml` behind an input, so no new required
name exists; §37.3's five-privileged-workflow count then reads four, which contradicts the section. **C** — name
it and mark it **not** required, so §15.5 does not check for it; the actor gate then guards a file nothing asserts
exists.
**In force.** None — the named tasks STOP.

---

#### REG-033 — The template placeholder syntax

**Gates** `Ph2` · **Decided by** L0 (`L0D-01`) · **Input from** L3 (which performs the substitution)
**Raised as** `D-L2-08` (`lanes/L2-05` §1)
**State:** Closed — Resolved by FD-019 (2026-09-02): `{{TOKEN}}` double-brace syntax; L2's renderer published as contract artifact under `contracts/`. Confirmed by FD-054 (2026-09-06).

**What must be decided.** `templates/workflows/**` is consumed by L3's `create-product` (§19.1). The token syntax
is a **cross-lane interface**; L2 inventing it produces templates L3 cannot render (PARTITION rule 4).
**Blocks.** L2 `L2-T300` and **every task from `L2-T301` onward** in the `templates/workflows/**` tree.
**Options.** **A** — double-brace tokens `{{PRODUCT_NAME}}`, `{{CONTROL_PLANE_REPO}}`, `{{WORKFLOWS_TAG}}`,
`{{CONFORMANCE_PROFILE}}`, `{{DEFAULT_BRANCH}}`, substituted by `create-product`, with the binding rule that **no
token may appear inside a GitHub Actions `${{ }}` expression**. **B** — `envsubst`-style `${NAME}` tokens, which
collide with Actions expression syntax and with shell expansion in every `run:` block. **C** — a full template
engine, which adds a dependency to L3's CLI for a substitution of five values.
**In force.** L2 is written assuming **A**; if L0 ratifies anything else, `L2-T300` STOPs.

---

#### REG-034 — The `/version` observation transport

**Gates** `Ph4` · **Decided by** L0 (`L0D-25`) · **Input from** L5 (a runner label) or L4 (a scrape read interface)
**Raised as** `D-L2-09` (`lanes/L2-04` §4)
**State:** Closed — Forced by spec

**What must be decided.** From which runner, under which credential, does the scheduled sweep perform
`GET /version`? §41.2 declares the estate's posture `private-authenticated` — *"the endpoints are reachable only
over the private path from the operations VM, with a per-product scrape credential"* — so a GitHub-hosted runner
cannot reach `/version`. The two candidate transports are both **foreign paths** to L2.
**Blocks.** Live scheduling of L2 `L2-T511`. It does **not** block `L2-T506`: the comparison core reads an
observations file and is fully testable offline.
**Options.** **A** — a self-hosted runner on the operations VM (`ops-vm/**`, **L5**); L0 publishes the runner label
and the scrape-credential secret name. Puts the sweep where the network path already exists; adds a self-hosted
runner to the privileged-tier question of **REG-037**. **B** — read the observation from subsystem I's Prometheus
scrape (`metrics/**`, **L4**); L0 publishes the read interface. No new runner and no new credential; the sweep then
depends on the scrape's freshness rather than on a live probe, which weakens what §32's digest chain is asserting.
**In force.** `L2-T511`'s workflow reads the transport values at run time and **fails closed** with
`VERSION_OBSERVATION_TRANSPORT_UNRESOLVED` if they are absent. If the canary sweep ever exits `0` while
unresolved, that is itself a STOP.

---

#### REG-035 — The eleven-question field binding

**Gates** `Ph4` · **Decided by** L0 (`L0D-01`) · **Input from** L4 (the record schemas)
**Raised as** `D-L2-07` (`lanes/L2-04` §4)
**State:** Closed — Forced by spec

**What must be decided.** `contracts/` must publish, for each of §32's eleven evidence questions, the **record
field name** that answers it on L4's deployment and UAT record schemas. §97.2 labels its deployment record
*representative*: it names `id`, `product`, `digest`, `approved_by`, `approval_event`, `staging_verified`,
`uat_record`, `smoke_result`, `rollback_of` — and names **no** field for the git commit (Q1), the pull request
(Q2), the CI run (Q4), the environment discriminator (Q6, Q9) or the deploy timestamps (Q6, Q9). Those names are
L4's to define; L2 inventing them is a cross-lane import that breaks silently on L4's first schema revision.
**What the answer looks like.** `contracts/evidence/eleven-question-map.yaml`, one entry per question 1–11, each
carrying `store`, `record_field` (or `source: github-api` with the API path), and `required: true|false`.
**Blocks.** Live wiring of L2 `L2-T504`. It does **not** block building it — `L2-T503` ships a lane-owned fixture
map of identical shape, so the engine is built and tested now.
**Options.** **A** — extend the deployment record schema with the five missing fields and map every question to a
record field. **B** — map the five to `source: github-api`, so the chain reads live platform state for them.
A makes the chain reconstructible from records alone after any dashboard failure, which is what §97.3 says the log
is for; B avoids five schema fields at the cost of a chain that cannot be replayed offline.
**In force.** The lane fixture map. `L2-T504`'s wiring task files the blocker; nothing else stops.

---

#### REG-036 — The record field carrying an S18 platform-rebuild identity

**Gates** `Ph6` · **Decided by** L0 (`L0D-01`) · **Input from** L4 (the deployment-record schema)
**Raised as** `D-L2-09` (`lanes/L2-02` §4)
**State:** Closed — Forced by spec

**What must be decided.** §32 says the S18 recorded identity *"stands in for the digest throughout this chain"*.
L2 writes it into the deployment record's `digest:` field as `platform-rebuild:v1:<64 hex>` (fixed by `L2-T521`,
published in `templates/workflows/artifact-conventions.yaml`). §97.2 prints `digest: sha256:…` and shows no S18
variant. **If L4's schema constrains `digest` to `^sha256:`, every S18 deployment record fails validation and the
evidence chain does not close for that product.**
**Blocks.** Validation of S18 deployment records; charter `DoD-14` for any S18 product. Nothing in L2's phase.
**Options.** **A** — confirm `digest:` accepts both value forms and record the regex union in L4's schema; one
field, one query, and the two forms are distinguishable by prefix. **B** — a distinct field, in which case
`tools/evidence/assert-staging-verified-identity.sh` reads that field in `platform-rebuild` mode — a one-line change
to a task already written, at the cost of every reader learning two fields.
**In force.** L2 writes the composed value; the failure, if it comes, is a schema rejection at write time, which is
fail-closed and visible.

---

#### REG-037 — Runtime evidence of privileged-runner tier

**Priority** P1 · **Gates** `Ph6` · **Decided by** L0 (`L0D-25`) · **Input from** L5 (`infra/**` marker paths)
**Raised as** `D-L2-09` (`lanes/L2-03` §5)
**State:** Closed — Resolved by FD-018 (2026-09-02): Option B — no product takes the D87 exception in V1; both marker keys published with literal value `not-applicable-v1`.

**What must be decided.** **D87** requires each privileged workflow to assert its own runner tier and fail closed,
with the declared exception being an `--ephemeral` self-hosted runner in a runner group labelled `privileged`.
GitHub exposes **neither** the runner group nor the `--ephemeral` registration flag to the running job. The only
runtime-checkable evidence is a host-side marker placed by L5 at runner provisioning time, and the marker paths are
an `infra/**` interface L2 may not invent.
**Blocks.** The **self-hosted branch** of L2 `L2-T172` only, and the X2 runner-tier negative test that reads the
markers (`D-L2-09` is restated as still binding in `lanes/L2-06` §5). The **hosted default** — which is D87's own
stated default — is unblocked and is built regardless.
**Options.** **A** — publish `privileged_runner_marker_path` and `ephemeral_runner_marker_path` as an
L5-implemented contract, written at runner registration. Makes the assertion testable and makes the three §53.1
Blocking drift rows checkable. **B** — declare that **no product takes the D87 exception in V1**, in which case the
self-hosted branch is unreachable by construction and the hosted branch is the whole control. B is smaller and must
be recorded as a scope decision, because it forecloses self-hosted privileged runners for V1.
**In force.** The hosted branch is built and armed; the self-hosted branch is present and fails closed.

---

#### REG-038 — The sandbox organisation and fixture-repository slugs for the X3 harness

**Gates** `Ph2` · **Decided by** L0 (`L0D-24`, `L0D-25`) · **Input from** L5 (`infra/**` provisioning, `access/**`)
**Raised as** `D-L2-11` (`lanes/L2-06` §5)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** Under which GitHub organisation do the X3 fixture repositories live, what are their
slugs, and which credential dispatches into them? A sandbox organisation is `infra/**` and its access model is
`access/**`, both **L5**; the org slug and the dispatch credential must arrive through `contracts/**`. L2 inventing
them produces a harness that dispatches nowhere and **reports green**.
**Blocks.** The X3 tier only: L2 `L2-T603`, `L2-T221`, and the X3 half of `L2-T607` and `L2-T608`. X1 and X2 are
unblocked and are built regardless.
**Options.** **A** — publish `sandbox_org_slug`, `sandbox_dispatch_secret_name` and `fixture_repo_prefix` in
`contracts/**`, with L5 provisioning the org. Buys the only tier that can prove **D91** negatively, since §33.4
requires every environment to carry a deployment branch and tag policy from the template at creation. **B** —
declare X3 out of scope for V1, in which case every X3 gate is re-declared at X2 **by an L0-issued amendment to
`lanes/L2-06`, never by the executor**.
**In force.** `L2-T603` ships the harness with the dispatch step present and **exiting non-zero** with
`SANDBOX_ORG_UNRESOLVED` — a fail-closed stub, never a skipped one — and every X3 gate reports `UNARMED` under
`lanes/L2-06`'s STOP rule `S10`.

---

#### REG-039 — The five orphan-detection input surfaces

**Gates** `Ph3` · **Decided by** L0 · **Input from** L5 (the asset inventory), and whichever lane produces each snapshot
**Raised as** `DR-L3-05-A` … `DR-L3-05-E` (`lanes/L3-05` §5)
**State:** Closed — Forced by spec

**What must be decided.** §12.2's sixteen orphan types are detected from five input surfaces the specification
names by role and not by path. `lanes/L3-05` §5 fixes the answer's shape: `L3-05-02` creates
`reconciler/orphans/decisions.py` with **every constant set to `None`** and a docstring naming the five decisions,
and the executor pastes L0's literal answer into it — it invents nothing.

| # | Surface | The gap | Constants | Blocks |
|---|---|---|---|---|
| a | **Operational asset inventory** location and type vocabulary | §49.1 and §52.6 name the artifact and its per-entry fields (expiry, owner, ≥30-day alert threshold) and state **no filename, no schema, no type vocabulary**. Orphan types 6–9 must tell a certificate from a domain from a vendor relationship, a distinction with no spec-given field | `ASSET_INVENTORY_PATHS`, `ASSET_ENTRIES_KEY`, `ASSET_ID_KEY`, `ASSET_OWNER_KEY`, `ASSET_TYPE_KEY`, `ASSET_TYPE_CERTIFICATE`, `ASSET_TYPE_DOMAIN`, `ASSET_TYPE_VENDOR` | `L3-05-10`…`T13` |
| b | **Which assignment types are "delegation-type"** | §10.1 requires *"Every delegation-type assignment receives a 14-day advance expiry warning"*; the seventeen-row table above it never labels a row "delegation-type", and candidate rows carry four different expiry phrasings | `DELEGATION_WARNING_TYPES` | `L3-05-26` |
| c | **Board snapshot** source and shape for H1 items | §12.2's Detection column is *"Board"*; boards live in the designated work-management system (§29.1), not in a control-plane YAML; §99.5 leaves the board shape open | `BOARD_SNAPSHOT_PATH`, `BOARD_SNAPSHOT_FORMAT`, `BOARD_ITEMS_KEY`, `BOARD_ITEM_ID_KEY`, `BOARD_ASSIGNEE_KEY`, `BOARD_COLUMN_KEY`, `BOARD_BLOCKED_KEY`, `BOARD_H1_COLUMNS` | `L3-05-17` |
| d | **"Open gate-relevant work"** input surface | §12.2, EC-111 and §12.4 all describe live GitHub state, and this phase is forbidden from making network calls. A snapshot file is required and the spec names none | `OPEN_WORK_SNAPSHOT_PATH`, `OPEN_WORK_SNAPSHOT_FORMAT`, `OPEN_WORK_ITEMS_KEY`, `OPEN_WORK_ID_KEY`, `OPEN_WORK_HOLDER_KEY`, `OPEN_WORK_KIND_KEY`, `OPEN_WORK_PRODUCT_KEY`, `OPEN_WORK_GATE_RELEVANT_KINDS` | `L3-05-18`, `L3-05-27` |
| e | **How a customer commitment's owner resolves** | §12.2 gives the Detection source as *"Contract operations block"*; the commitments schema (§21.1, §15.1) contains **no `owner:` field**, and the operations block carries `triager`, `primary_responder`, `backup_responder`, `intake_channel`. Selecting which one carries commitment ownership is interpretation | `COMMITMENT_OWNER_RESOLUTION` (an ordered tuple of dotted key paths) | `L3-05-14` |

**Options, uniform across the five rows.** **A** — L0 publishes each path, key and literal value set as a
`contracts/` entry and the executor transcribes it into `decisions.py`. **B** — the surface is declared not
detectable in this build and the affected orphan type is recorded as `unarmed — not yet instrumented` under D77.
A costs a snapshot producer per surface (rows c and d need a lane named to produce them); B costs the orphan type,
and §12.2's sixteen become fewer, which is a scope decision and must be recorded as one.
**Binding note for row (a).** The asset inventory is **L5** data (`assets/**`). L3 reads it **by path**; L3 must
not import L5 source (PARTITION rule 4).
**In force.** Every constant is `None`; the affected task STOPs and opens the blocker naming the `DR-L3-05-x` id
and **REG-039**. The executor does not create the file, invent a path, or proceed.

---

#### REG-040 — `product-template`'s seed-data and migration-directory paths

**Gates** `Ph2` · **Decided by** L0 · **Input from** whoever owns `product-template` (see **REG-017** row p)
**Raised as** `D-L3-04-03` (`lanes/L3-04` §1)
**State:** Closed — D113 or forced by arithmetic

**What must be decided.** §33.1 makes the required-file list binding — *"Required-file presence is checked, not
assumed"* — and names `.env.example`, `docker-compose.dev.yml`, `Makefile`, **seed data**, **migration directory**,
`verification/`, `AGENTS.md`, and either `product.yaml` or a pointer. Two of the eight are described **by role, not
by path**, and `product-template` is not an L3-owned repository, so L3 cannot define them there.
**Blocks.** L3 `L3-04-10` (the scaffold verifier) as a live check; nothing else.
**Options.** **A** — fix `seed/` and `migrations/` as the canonical paths in `product-template` and in the
conformance profile; simplest, and the verifier fails a repository with neither. **B** — declare them per-product
by a `product.yaml` field, which suits a heterogeneous estate and turns a presence check into a declared-path
check. A costs uniformity across eight existing products; B costs a contract field and a second failure mode
(declared path absent).
**In force.** `tools/provision/provision/conformance/required_files.yaml` (L3-owned) fixes them as `seed/` and
`migrations/`, and the scaffold verifier fails a repository that has neither. If L0 settles differently, **only
that file changes** and `L3-04-10` is re-run.

---

#### REG-041 — The L3 test-harness interface contract, and authorisation to touch the live organisation

**Gates** `Ph3` · **Decided by** L0 (`L0D-01`; the live-org gate is `L0D-24`) · **Input from** L3 (its own CLI shape)
**Raised as** `DR-L3-07-A`, `DR-L3-07-B` (`lanes/L3-07` §2)
**State:** Closed — Resolved by FD-023 (2026-09-02): Option A for both parts — ten-key contract in `contracts/l3-test-harness.env`; Nimesh named as AT-110 live-probe supervisor.

**What must be decided.** **(a)** Every task in `lanes/L3-07` invokes the reconciler and the provisioning CLI.
Their invocation strings, flag names and run-record location are a **cross-task interface**, not a test choice, so
under PARTITION rule 2 they are L0's. L0 publishes `contracts/l3-test-harness.env` containing exactly these keys,
one `KEY=value` per line, no other content: `RECONCILE_CMD`, `RECONCILE_APPLY_FLAG`, `RECONCILE_SOURCE_FLAG`,
`RECONCILE_OUT_FLAG`, `RUN_RECORD_PATH`, `PROVISION_CMD`, `APPLY_ALLOWLIST_PATH`, `FIXTURE_ORG`, `LIVE_ORG`,
`HARNESS_JQ`. The run record must carry the fields §53.1 already mandates — a findings array, per-registry
comparison counts, and the canary result — so the assertions read spec-named data, not invented data.
**(b)** `SR-3` forbids any live-organisation execution until a gate opens, and the gate cannot be judged by the
executor. L0 publishes `contracts/l3-live-org-gate.md` stating: Phase 3's completion check has passed (*"contracts
validate; registries, contracts and Team membership agree, machine-verified"*, §98.2); the named human who will
supervise the `AT-110` six-attempt run; and the date authorised.
**Blocks.** (a) L3 `T01` and therefore the whole suite. (b) L3 `T10`, which **never runs unsupervised**.
**Options.** (a) **A** — publish the ten keys as stated; **B** — publish a single `RECONCILE_CMD` and let flags be
discovered from `--help`, which makes the suite depend on help text and breaks silently on a rename. (b) **A** —
authorise with a named supervisor and a date; **B** — decline live-org execution for V1, in which case `AT-110` is
recorded as `not_run` with a dated trigger, never as passed.
**In force.** *"Until this file exists, `T01` STOPs. No executor invents a value for any key."* `LIVE_ORG` is
recorded in the harness file **only** so `TC-L3-03` can prove the reconciler **refuses** it.

---

#### REG-042 — The per-product rota shape in `people.yaml` — a hard block

**Gates** `Ph2` · **Decided by** L0 (`L0D-01`) · **Input from** nobody
**Raised as** `L1-D03` (`lanes/L1-05` §1)
**State:** Closed — Forced by spec

**What must be decided.** §7.1's `people.yaml` example places a **single** `work_arrangement.accepted_coverage_window`
on the person — one window, person-wide, `null` when not on a rota. §47.9 requires that *"`people.yaml` carries,
**per product**, the named rota members, each member's accepted window, the paging-path identifier and the funding
decision record."* These are two different shapes, and the spec gives field names for the first only. Choosing
between them, and **naming the two fields §47.9 describes but does not name** (paging path, funding decision
record), is schema design.
**Why it cannot be defaulted.** §15.5 and `AT-047` both hang a CI failure on the result, so guessing produces a
validator that fails the acceptance test.
**Blocks.** L1 `L1-311` — the only **hard block** in Lane 1. Every other L1 task proceeds.
**What L0 must return.** The exact YAML shape with field names for the per-product rota block, **and**
confirmation of whether `work_arrangement.accepted_coverage_window` is retained, removed, or becomes a derived
value.
**Options.** **A** — per-product rota block on the person, `accepted_coverage_window` retained as the person-wide
default; two shapes, one overriding the other, and the validator must state precedence. **B** — per-product rota
block only, `accepted_coverage_window` **derived** from it; one source of truth, and §7.1's example must be
reissued as superseded narrative. **C** — the rota lives on `product.yaml` and `people.yaml` carries only the
window; puts the per-product data with the product, and §47.9 says `people.yaml`, so this needs an explicit
override of the section.
**In force.** None. `L1-311` files the blocker with `DECIDER: L0 Integrator` and both spec citations.

---

#### REG-043 — The L1 schema-shape rulings

**Gates** `Ph2` for rows a–f, `Ph1` for row g · **Decided by** L0 (`L0D-01`, `L0D-18`) · **Input from** nobody
**Raised as** the raisers named per row
**State:** Closed — D113 or forced by arithmetic

Eight rulings L1 needs before it can freeze a schema. Each has a stated default that ships; none is a hard block
except where noted.

| # | Ruling needed | Raised as | Default that ships | Blocks |
|---|---|---|---|---|
| a | Is a `product.yaml` **v1** schema required? §60.1's `platform.yaml` declares `supported_contract_versions.product: [1, 2]`; §15.1 exhibits only v2; **no v1 shape appears anywhere in the specification** | `DECISION-L1-02-A` | v2-only; `schemas/registry/index.json` lists v2. The §60.1 literal `[1, 2]` then fails the cross-file residual check once that validator exists | authoring `schemas/product/product/v1/` |
| b | The carrier for the 24-token capability vocabulary — §9.1 requires CI to fail any capability without a row in the §9 table, and §52.6's 29-entry inventory contains no `capabilities.yaml` and forbids a thirtieth artifact | `L1-D02` | a **closed `enum`** in `schemas/registry/common/defs.v1.schema.json` (`$defs.capability`); no registry file is created | `L1-101`, `L1-201` if overturned |
| c | Ratification of the planner-fixed field names for the four prose-only registries — `patterns.yaml` (§58.2), the automation-ledger and standing-entry blocks of `economics.yaml` (§57.1, §57.2), the tolerance block of `os-health.yaml` (§53.4), the investment-gate block of `platform-roadmap.yaml` (§59.2). Semantics fully specified; field names not | `DECISION-L1-02-C` | the names fixed literally in `L1-02` `T09`, `T12`, `T13`, `T14` so the executor never chooses | nothing — but a rename after population is a §60.2 **v2 schema**, not an in-place edit |
| d | Which control-plane file carries the fail-closed / fail-open classification of every control (§64.2, invariant 80)? §52.6 freezes the inventory at 29 artifacts and §64.2 names no file | `control_classification_home` (`lanes/L1-03` §1) | `registries/policies.yaml`, extended with a required `failure_mode:` per entry (`fail-closed` \| `fail-open` \| `graded`) | `L1-03` `T11` (rule R10) |
| e | How does a control-plane CI run read `records/restore-tests/` to check that `restore_tested` is **derived, not declared** (§44.2), when those records live in the **records repository** L1 does not own? | `records_snapshot_mode` (`lanes/L1-03` §1) | `optional-path`: the CLI accepts `--records-root`; when absent, `R06.3 severity=info skipped-no-records-root` and age only. **L2 supplies the path in CI** | `L1-03` `T07` (rule R06) live half |
| f | Which half of the cross-file referential rules L1 owns — the **declared-side** consistency check (named reviewers exist and are active in `people.yaml`) versus the **declared-vs-actual** comparison (GitHub state, which is L3's `validators/drift/**`) | `DR-L1-06-C` | L1 owns the **declared side only**; `L1-06` row 7's fixture asserts a declared-side inconsistency | `L1-06` rows 7 and 17 |
| g | The authoritative schema-id list and file-naming convention — the 18 ids in `lanes/L1-06` §2 are derived from §52.6 minus rows PARTITION assigns elsewhere, and may not match what `L1-01`…`L1-05` actually author | `DR-L1-06-A` | none — `L1-06-01`'s `diff` must be empty | `L1-06-01` STOPs |
| h | `platform.yaml` carries two values L1 does not produce — `reusable_workflow_versions` (L2 owns the workflow tags) and the closed `event_type` enum (L4) | `L1-D05` | L1's `platform.v1` schema declares both and validates their **shape**; `L1-107` seeds from `contracts/` if defined there, otherwise empty (`current: null`, `supported: []`, `event_type: []`). **L1 never invents a workflow tag or an event-type token** | see **REG-021** |

**Options, uniform.** **A** — ratify the stated default and record it, which costs one decision record per row and
nothing else. **B** — replace it, which costs the named task's re-run. Row (c) carries the asymmetry that matters:
ratification is free **before** population and a §60.2 v2 schema **after** it, *"which is exactly the cost this
decision exists to pay once"*.

---

#### REG-044 — The bootstrap exception write path, and Gate 1's compensating control during bootstrap

**Gates** `Ph1` · **Decided by** L0 (`L0D-19`, `L0D-04`) · **Input from** nobody
**Raised as** `DECISION REQUIRED #1`, `#2` (`lanes/L0-06` §5) · `DR-L0-07-B` (`lanes/L0-07`)
**State:** Closed — Forced by PARTITION.md

**What must be decided.** **(a)** §95.2 and §54.5 place bootstrap exceptions in `exceptions.yaml`, the unified
exception registry. PARTITION assigns `registries/**` to **L1, exclusively**, and L1's `L1-108` creates
`registries/exceptions.yaml` containing `exceptions: []` with the comment *"entries are authored by their owner,
not by Lane 1"*. The owner of a bootstrap exception is the Founder (§54.3: `bootstrap` → `exceptional-approval`),
which in this programme is **L0**. So the authoring party and the path owner are different lanes, and PARTITION
rule 3 forbids two writers on one file.
**(b)** §26.1 states Gate 1's bootstrap handling verbatim: *"Where neither exists — the bootstrap case — the
self-approval runs under a recorded bootstrap exception (Section 95), with Gate 2 independent review as the
compensating control."* But **Gate 2 independent review is itself relaxed in bootstrap**, under the §95.2 exhibit's
own `EXC-BOOT-001` (`scope: gate-2-independent-review`). During the solo build both exceptions are open at once, so
Gate 1's named compensating control **is not in force**. §54.2: *"the compensating control is the entire reason an
exception is acceptable."*
**Blocks.** Nothing in `lanes/L0-06`. (a) changes only where the rendered YAML finally lands; (b) leaves one line
of `EXC-BOOT-012` provisional.

| # | Option (for **a**) | Trade-off |
|---|---|---|
| **A** | L1 lands the rendered block in one L1 task, taking `docs/bootstrap/exceptions/` as its input | No partition change; L0 authors, L1 transcribes, one writer per file |
| **B** | L0 is granted `registries/exceptions.yaml` by an `L0D-04` extension of `lane-paths.tsv` | Author and owner become the same party; breaks the `registries/**` glob at file granularity |
| **C** | The entries move to a directory-per-item store that L1 assembles | Matches PARTITION rule 3 exactly; needs the store path and the assembler, and interacts with **REG-008** |

**Option for (b).** L0 states the compensating control `EXC-BOOT-012` (`gate-1-plan-approval`) carries while
`EXC-BOOT-001` is open. There is no candidate set in the source; a bootstrap exception without a real compensating
control is a silent policy breach.
**In force.** `docs/bootstrap/exceptions/EXC-BOOT-NNN.yaml` — one file per exception, inside L0's exclusively-owned
`docs/**`, directory-per-item — is the authored form. `EXC-BOOT-012` carries the common compensating-control set
plus **the literal sentence naming this gap**, so the record states the fact rather than implying a control that is
not running, and the gap is a standing line in the weekly bootstrap log until L0 answers.

---

#### REG-045 — How many cross-lane contract pairs exist

**Gates** `Ph1` · **Decided by** L0 (`L0D-06`; reconciling two protocol documents is a contract decision) · **Input from** nobody
**Raised as** `L0-IG-D1` (`lanes/L0-05` §5)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** Is the cross-lane contract set **ten pairs** or **twelve contracts**?
`protocol/00-test-strategy.md` §5 (T2) declares ten pairs, `CT-01`…`CT-10`, each with a named provider and
consumer. `protocol/01-contract-tests.md` §3 and §4 declare twelve contracts, `C-01`…`C-12`, each with a producer
and consumers. Both describe the same artifact, and `IG-03`'s pass line reports `pairs=<n>`. **One number is
right.** This file may not pick the larger, the smaller, or the union.
**Blocks.** `IG-03` and `IG-05`, and therefore **GATE B**, from the first cycle.
**Options.** **A** — ten pairs, retiring `protocol/01`'s two extras with a reason. **B** — twelve, reissuing
`protocol/00` §5. **C** — the union, which is the one answer forbidden: a set assembled from two documents that
disagree is a set neither document specified.
**In force.** `contracts/gate/COUNTS.tsv` carries **both** source rows, `ct_pairs_p00` and `ct_pairs_p01`, and
`count-integrity.sh` reports `narrowed=1` — **the gate is closed** until one row is retired by an L0 decision
record. A closed gate here is correct: a build whose cross-lane test set has two sizes has not been
integration-tested, whichever size is right.

---

#### REG-046 — How many context-holding humans hold Write during V1

**Gates** `Ph1` · **Decided by** L0 (`L0D-19`, `L0D-24`) · **Input from** the Founder (headcount)
**Raised as** `V1-D6` (`master/06` §12)
**State:** Closed — Resolved by FD-017 (2026-09-02): Two context-holding humans — the Founder (bendrohit-eng, L0) and Nimesh (Team Lead) — on `control-plane` and `product-template`.

**What must be decided.** §95.1 scopes Bootstrap Mode **per repository, never per company**: the shortfall exists
only where no second context-holding human exists. §98.7 assumes *"the Founder solo under Bootstrap Mode"* for
Foundation. PARTITION describes a different reality: five parallel AI developers plus one human integrator — and
AI developers are **not** context-holding humans for gate-independence purposes, because §98.2's Phase 1 completion
check is explicit that an approval from a machine account does not satisfy branch protection. For each repository
in scope, L0 must state how many context-holding humans hold Write at V1.
**Blocks.** Which rows of the §95.4 activation checklist arm for real and which run under a recorded bootstrap
exception; which of invariants 9, 12 and 57 arm mechanically at V1; how many bootstrap exceptions L1 must author
into `exceptions.yaml`; whether §98.2's Phase 1 completion check *"executed for real once headcount permits"* is
executed at V1 or deferred with its trigger recorded. Also **REG-014** (how many humans there are to name in
`CODEOWNERS`).
**The thresholds are fixed by §95.4 and are not negotiable.** **2 humans** arms no-self-approval, Gate 2
independent review and most-recent-push approval. **3 humans** arms production-approver ≠ deploying-actor and the
real cross-review matrix. **QA role filled** arms independent verification authority and release sign-off.
**4+ humans** arms Backup Owner coverage, the knowledge-redundancy floor and responder rotation.
**Options.** There is no option set — the answer is a headcount. What L0 chooses is which repositories to
prioritise for the second human, since §95.1 is per-repository.
**Binding regardless of the answer.** Every relaxed gate gets one exception naming the gate, the repositories, the
compensating controls, an owner, an expiry and a deactivation trigger, with the **armed configuration recorded
beside the unarmed one** (§95.2). An exception whose expiry passes with its gate still unarmed is **SIG-39**, Red,
routed to the Founder. Stubbed gates have a habit of staying stubbed (§99.6 risk 3).

---

#### REG-047 — Which products are the pilots, and are there two or three

**Gates** `Ph2` · **Decided by** L0 / the Founder (product criticality is a Founder judgment) · **Input from** the Founder
**Raised as** `V1-D4` (`master/06` §12) · `DECISION 4` (`master/04` §8)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** §99.4 fixes the count as *"2–3 pilot products"*; §96.5 fixes the ordering — sequenced
highest `classification.reliability_criticality` first. Neither names products, correctly, because product identity
is configuration, not architecture (invariant 52). L0 supplies the **ordered list**, written into
`contracts/v1-scope.yaml` under `pilot_products`. Every other live product then gets a stub `product.yaml` with an
onboarding block and a deadline set from the Onboarding track, **not** from a §98.2 week label (**D99**).
**Blocks.** All Onboarding-track work `OT-P4`…`OT-P7`; the Phase 2 pre-onboarding stubs; `master/06` §13's V1 exit
gate, which is evaluated against this set and no other. Interacts with **REG-048** (`DR-L0-07-D`: the eight product
identities behind the numbered slots).
**Options.** **A** — two pilots; smallest surface, and every V1 exit criterion is proven twice. **B** — three;
proves the fleet mechanisms against more variety, at one more product's onboarding cost inside V1.
**Note for L0, from the raiser.** The choice interacts with §95.1 — a product repository whose existing team
already holds Write **satisfies gate independence immediately and never enters bootstrap**. Choosing such a product
as pilot one arms more of the invariant floor for real rather than under exception.
**In force.** None — a lane cannot pick a pilot, and `lanes/L0-07` fixes eight numbered slots `01`…`08` precisely
so the track can be built before the identities exist.

---

#### REG-048 — The universal floor: duration, sequence, the tenth item, and the calendar anchors

**Gates** `Ph1` · **Decided by** L0 · **Input from** the Founder (product identity, criticality order) and the intake assessors (starting states)
**Raised as** `DECISION 3` (`master/04` §8) · `DR-L0-07-C`, `DR-L0-07-D`, `DR-L0-07-G` (`lanes/L0-07`)
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

**What must be decided.** Four things the onboarding track cannot compute for itself.
**(a) The 72-row floor checklist.** §96.6 states the floor *"carries its own duration in the roadmap"* and that
*"costed honestly against the portfolio's starting states it is several weeks"* — deliberately no number, because
it depends on the eight products' actual starting states, which only the intake gap assessments reveal. L0 produces
the 9 × 8 checklist with a named executor and a date per row, sequenced by `classification.reliability_criticality`
(§96.5), each lower-criticality product still outstanding on a floor item carrying a **dated accepted risk mirrored
into the exception registry**.
**(b) Is S19 a tenth floor obligation, or does it ride `F9`?** Genuinely ambiguous in the source, and it changes
the denominator of the floor burn-down (`DR-L0-07-C`).
**(c) The eight product identities** — the `product_id` field of each slot's `facts.tsv` (`DR-L0-07-D`). `lanes/L0-07`
*"does not know their names and must never invent one."*
**(d) The absolute-date anchor** the relative clock resolves against (`DR-L0-07-G`), which is the same anchor
**REG-009** needs for the Build track.
**Blocks.** Every onboarding phase's dated deadline; the floor burn-down denominator; `lanes/L0-07` `T04` (the
resolver) and the per-slot `facts.tsv`. `master/04` DECISION 3 states it cannot wait, because two floor items are
**hard AI-safety gates**: **S10** (secrets committed) and **S19** (customer data committed) — *"No AI-assisted
session opens the repository until the S10 check passes"*, and invariant 111 for S19. A product failing either is
unavailable to any AI-assisted work, **including onboarding**, until it passes.
**Options for (b).** **A** — S19 is a tenth obligation; the denominator becomes 80 and §96.6's own arithmetic
(9 × 8 = 72) must be reissued. **B** — S19 rides `F9`; the denominator stays 72 and the S19 gate is tracked
separately in `gates.tsv`, counted on its own.
**In force.** **B** — nine rows, 72 obligations, S19 tracked separately in `gates.tsv`. The eight slots are
numbered `01`…`08` and carry no product name. Every phase and deadline field holds a **relative expression**, never
a calendar date; the resolver of `L0-07-04` is the only writer of resolved dates (`OB-F2`).

---

### 3.4 Band P3 — recorded, with a defined default; no task stops today

Seven entries. Each ships a stated default or a fail-closed placeholder, so nothing waits. They are here because a
default that is never ratified becomes a decision nobody made, and because several become `P2` at a later tier —
the `Escalates at` line says when.

---

#### REG-049 — Required-check status of `digest-invariant-selftest`

**Gates** `Ph6` · **Escalates at** the first product reaching §98.2 Phase 6 · **Decided by** L0 (`L0D-18`)
**Raised as** `D-L2-08` (`lanes/L2-02` §4)
**State:** Closed — Forced by prior decision

`L2-T202` creates `.github/workflows/digest-invariant-selftest.yml`, which runs the negative-test harness proving
the §32 gate still refuses. Should its context be a **required** status check on the control-plane repository?
L2 may not decide: `L2-T003`'s STOP rule forbids Lane 2 adding a context to the frozen registry, and §98.2 Phase 1
makes the required-check list a per-phase, explicitly named addition.
**Options.** **A** — required; a pull request weakening `assert-staging-verified-identity.sh` then fails the merge
gate, not merely the run. **B** — advisory; leaves the estate's **only mechanical proof of the digest invariant**
(§32; invariant 22) as a run that can be ignored. `lanes/L2-02` names B a material posture decision and routes it
to L0 for that reason. **Blocks** nothing in Lane 2's phase.
**In force.** Not required. The workflow runs and reports.

---

#### REG-050 — Whether a local GitHub Actions runner is admitted to the toolchain

**Gates** `Ph2` · **Escalates at** never, unless a lane proposes one · **Decided by** L0 (`L0D-24`; `C-10`)
**Raised as** `D-L2-13` (`lanes/L2-06` §5)
**State:** Closed — Forced by prior decision

May the X2 tier use a local Actions runner (`act` or equivalent) to execute a workflow file off-platform, and if so
at which pinned version and by which pinning mechanism? **No section of the specification names a local Actions
runner.** §48.1 and invariant 85 require every third-party dependency pinned; admitting an unpinned binary that
executes workflow YAML on a developer machine is a toolchain decision with a supply-chain surface, and §99.5's
technology-shape decisions are silent on it. **L3 will face the identical question for `reconciler/**`; the two
lanes must not diverge** — which is why this is one register entry and not two.
**Options.** **A** — decline. X2 executes the **gate programs**, not the workflow YAML, and X1 asserts the call
sites; this is why `lanes/L2-06` §2's binding rule exists — one gate body, called from the workflow by path,
executable standalone. **B** — admit at a pinned version, which gains a fourth execution path and adds a
supply-chain surface to every developer machine.
**In force.** **A**. `lanes/L2-06` is written assuming L0 declines. **An executor who finds `act` on the PATH does
not use it and does not call the suite stronger for it.** If L0 admits one, X1 is unchanged, X2 gains a path, and
**no gate is re-declared and no negative fixture is retired.**

---

#### REG-051 — The four L4 record vocabularies the specification does not enumerate

**Gates** `Ph2` · **Escalates at** first population of the affected store · **Decided by** L0 (`L0D-01`)
**Raised as** `D-L4-04` … `D-L4-07` (`lanes/L4-02` §4)
**State:** Closed — Forced by spec

| # | Ruling | The gap | Default that ships |
|---|---|---|---|
| a | Per-store **record-id prefix** | §97.2 gives literal prefixes for four stores only — `INC-`, `DEP-`, `DEC-`, `DEMO-`. The other thirteen have none stated anywhere | the generic `record_id` pattern accepts any 2–10-character upper-case prefix; the four spec'd stores pin their literal prefix with `"pattern"` |
| b | **State vocabularies** for the eight compound event entries — §97.3 states *"exactly one stable `event_type` identifier"* per entry, and eight entries name two or more states in one entry | one identifier per `·`-separated entry — the literal reading — with `payload_required: [state]` and `state` an unconstrained non-empty string |
| c | **Security-review finding severity and disposition** — §97.2 says a security-review record *"carries findings with severity and disposition"* and no vocabulary for either is stated. The `SEV-1`…`SEV-4` ladder is the **incident** ladder and is not stated to apply | both required non-empty strings with **no enum**: the field is mandatory, the vocabulary is not invented |
| d | **Launch-readiness checklist rows** — §19.2 requires *"every checklist row rendered green or red with a link to its evidence record"*; the row identifiers are spread across §19.2, §22.2 and §22.6 and are enumerated as a closed list nowhere | `checklist` is a required non-empty array of `{row, status, evidence}`; `row` unconstrained non-empty string, `status` the closed enum `green|red` (literal from §19.2) |

**Options, uniform.** **A** — ratify the default. **B** — narrow it to a closed enum. The asymmetry is the whole
reason none of these blocks: **narrowing a pattern later is a §60.2 v2 schema, not a rewrite**, and adding an
identifier later is a governed enum addition — retiring is marked, never removed (§97.3).
**Blocks.** Nothing.

---

#### REG-052 — The four L4 derivation rulings

**Gates** `P1` for rows a and c; `G3` for row b; `P1` for row d · **Decided by** L0 (`L0D-17`, `L0D-01`)
**Raised as** `D-L4-P4-01` … `D-L4-P4-03` (`lanes/L4-04` §5) · `D-L4-P7-03` (`lanes/L4-07` §"DECISION REQUIRED")
**State:** Closed — Forced by spec

| # | Ruling | The gap | Default that ships | Blocks |
|---|---|---|---|---|
| a | Does `fte` **multiply** the declared schedule, or is it already in it? | §7.3: *"`fte` is a capacity multiplier, not a status"*; §7 on the same block: `fte: 1.0 # 0 < fte <= 1; part-time is configuration`, beside a per-weekday `schedule` with explicit `start`/`end`. Applying both **halves a half-day twice** | `calibration.yaml` declares `fte_application: none` with `pending: D-L4-P4-01`; the declared `schedule` span is authoritative, grounded in *"part-time is configuration"* | rule **R6** of `scheduled-availability.py` (`L4-T406`) only |
| b | Is the Ready-queue-miss event appended at detection, or after the cause prompt? | §97.5 says the automation *"appends a Ready-queue-miss event with who, which date, and which product, **and opens a one-line cause prompt**"*, and that the event *"carries the full §29.4 field set … the last three supplied by the cause prompt, never inferred."* An event cannot be appended before three of its six fields exist | `rqm-detect --emit` writes the verdict **only** when `cause_prompt_answered` is true; otherwise it prints `RQM-DETECT PENDING-CAUSE <case>`, exits `0`, **writes no verdict and appends no event**. It never fabricates a cause | the `--emit` path of `L4-T417` only |
| c | Which leave record carries the company working calendar? | §6.4 and §52.6 place the calendar in the leave records; neither the spec nor Phase 2 states **which** record is current, or how a reader selects it | `scheduled-availability.py` takes `--calendar <path>` as a **required explicit argument**; it never searches `records/leave/`, never picks by resemblance, and exits `3` with `SCHEDAVAIL ERROR no-calendar` when absent | rule **R4** of `L4-T406`, production wiring only |
| d | Round-then-split, or split-then-round, for product attribution? | §97.4 fixes granularity at 0.25 h *"rounded to nearest, never to zero"* and attribution as *"a session touching several splits across them by event count"* — and does not say which comes first | every attention fixture is constructed so **both orders yield the identical value** (case DC-5 splits 60 minutes 2:1:1 → 0.50/0.25/0.25 either way) | nothing today |

**Options.** Each row is a binary and the trade-off is the same in every case: the default is the **literal reading
of the cited line** and the alternative is the **other** literal reading; whichever L0 records becomes
configuration, not code, in `calibration.yaml`.
**Binding.** **No fixture, in this phase or any other, may be added that distinguishes the two orders of row (d)
until L0 answers** — adding one would be a design decision. L4 must not hard-code either behaviour, write to
`registries/people.yaml`, or infer a schedule from activity (§7.2: leave *"is never inferred from activity"*).

---

#### REG-053 — Does D88 govern the §97.2 decision-record comment?

**Gates** `Ph2` · **Escalates at** the first real decision record naming a person · **Decided by** L0 (`L0D-01`)
**Raised as** `D-L4-P7-01` (`lanes/L4-07` §"DECISION REQUIRED")
**State:** Closed — Forced by spec

Both sides, quoted. **D88**: *"Records carry stable person IDs, never names — that rule is real, it is enforced at
schema validation, and it is what keeps the record stores de-identified"*, with the consequence that *"names in
record bodies fail schema validation."* **§97.2**, inside the decision-record example:
`decider: founder  # role, not name, in rules; names appear in real records`.
**These cannot both be executed.** A validator cannot both reject and accept a name in `decider`.
**Options.** **A** — D88 governs and §97.2's trailing comment is superseded narrative; the record stores stay
de-identified and every person-valued field is an id. **B** — a stated carve-out naming **which stores and which
fields** admit a name; buys human-readable decision records at the cost of a de-identification property that then
holds only per-store.
**Blocks.** `L4-P7-T07` only.
**In force.** **A**. `L4-P7-T07` asserts rejection in all five person-valued fields. If L0 rules the other way,
`L4-P7-T07` is **re-issued by L0**; the executor must not adapt it.

---

#### REG-054 — `SIG-43` is used twice, and the signal denominator is 46 or 47

**Priority** P2 · **Gates** `Ph2` · **Escalates at** the §52.4 tier check coming online · **Decided by** L0 (`L0D-22`)
**Raised as** `D-L4-P7-02` (`lanes/L4-07`) · `D-L4-TL-4` (`lanes/L4-06` §1) · `D-08-2` (`master/08` §10) ·
`master/INDEX.md` C-26
**State:** Closed — D113 or forced by arithmetic

§52.2 states there are *exactly forty-six signals* and its table contains 46 distinct identifiers across **47
rows**: `SIG-43` labels both *"Unclosed learning-loop items"* (source `records/postmortems/` plus
`records/incidents/`, Amber, QA) and *"Founder operating load"* (source the attention ledger, Amber; Red on
sustained breach, Team Lead). Reproduce it:

**Commands**

```bash
grep -oE '\| SIG-[0-9]{2} \|' "$SPEC" | sort | uniq -c | awk '$1>1'   # -> 2 | SIG-43 |
```

§52.2's own list, §52.4's tiering, §103.14 and **D104** all read `SIG-43` as **Founder operating load** — so the
learning-loop row is the one carrying a borrowed identifier. It matters because §52.4 mandates a CI check that
*"every SIG identifier in the signal table appears in exactly one priority tier"*, so one row would be **untiered
for ever**, and because `metrics/signals/sig-source-map.yaml` maps one id to one store and cannot carry one id
twice. It also decides whether the denominator used as authoritative in `master/07` and `master/08` §5.2 is **46**
or **47**.
**Options.** **A** — Founder operating load keeps `SIG-43`; the learning-loop row takes a new id and the
denominator becomes 47. **B** — the reverse, contradicting four other spec locations. **C** — retire the
learning-loop row, keeping 46; loses a signal §52.2 declared.
**Blocks.** L4 `L4-P3-06` (the SIG source map) and `L4-P7-14` (learning-loop measures) — *"both unblocked the
moment L0 records an id"*.
**In force.** The Founder-operating-load signal maps to `SIG-43`; the learning-loop row emits
`signal_id: PENDING-D-L4-TL-4`, and `L4-P3-06`'s check asserts the placeholder is **present**, not that it is
resolved. `L4-P7-T11` asserts only the four unambiguous rows — SIG-06, SIG-17, SIG-41, SIG-42 — and reports the
SIG-43 row as `DEFERRED-D-L4-P7-02`, counted neither pass nor fail. **Do not invent a replacement id** (F-18).

---

#### REG-055 — `.github/**` and the repository root inside `control-plane-records`

**Gates** `Ph1` · **Escalates at** the first `.github/` file needed in the records repository · **Decided by** L0 (`L0D-04`)
**Raised as** `D-L4-03` (`lanes/L4-00` §9) · `master/INDEX.md` C-10
**State:** Closed — Forced by PARTITION.md

PARTITION gives **L4** *"ALL of `control-plane-records`"* and gives **L2** `.github/workflows/**`. Does the
repo-level grant to L4 cover `.github/**` inside that repository — including a committed ruleset JSON — or does
L2's path pattern reach **across repositories**? Independently, `master/03` §1.2's records-repo ownership map
assigns `:root:` and `.github/` in that repository to **L0**, which `master/01` §2 row 26 contradicts (*"Stated as
ALL. No exception."*).
**Options.** **A** — the repo-level grant wins; L2's pattern is scoped to `control-plane`, and `lane-paths.tsv`
becomes per-repository. **B** — path patterns are global; L2 owns `.github/workflows/**` in both repositories,
which puts an L2 file in a repository L2 has no other reason to clone. **C** — L0 holds `:root:` and `.github/` in
the records repository per `master/03`, narrowing "ALL" by two rules that PARTITION does not state.
**Blocks.** L4 `L4-T003` only.
**In force.** L4 creates **no file** under `control-plane-records/.github/` and records the D107 ruleset
requirement as a note in the repository README for L0.

---

#### REG-056 — Boards, the Scorecard drop magnitude, and the estimate exemption

**Gates** `G3` · **Escalates at** the first board automation write · **Decided by** L0 (`L0D-22`, `L0D-24`)
**Raised as** `D-L4-P5-02`, `D-L4-P5-04`, `D-L4-P5-05` (`lanes/L4-05` §6)
**State:** Closed — Forced by spec

| # | Ruling | The gap | Default that ships |
|---|---|---|---|
| a | The **designated work-management system**, its plan tier, and which board mode is selected | §29.1 says boards live *"in the designated work-management system"* and never names it; §99.5 names GitHub Projects among the verified-semantics surfaces. §29.1 states the dependency verbatim: *"confirm aggregation and filtering capability at the plan tier in use before Phase 1 of implementation … If aggregation is unavailable, the fallback is a single organisation-level project containing all items with a product field, and per-product filtered views."* **That confirmation is a console action against a live plan tier and no executor can perform it from a lane branch** | `board-conventions.yaml` declares **both** modes in full, `selected_mode: PENDING-D-L4-P5-04`, `aggregation_confirmed: false`. Nothing downstream branches on the mode |
| b | What magnitude and window define a reportable Scorecard **drop** | §92.3 says *"A Scorecard score drop"* and §17.3 *"Expect a Scorecard drop to remediate"*; neither states a size or a window. `security.scorecard_minimum` (initial `7.0`) is a **floor**, a different condition from a decrease | two separately named conditions, both literal readings: `decrease` (any strictly negative delta against the previous scan) and `below_minimum`. **Neither carries a routing threshold**; `routing_threshold: PENDING-D-L4-P5-02` |
| c | What field on a board item carries the item class, for the §29.3 estimate exemption | **D79**: *"Normal planned work records an estimate band … spikes, incidents and debt-remediation items are exempt."* The three classes are named in prose; no field on any board item, in any registry schema, or in §97.2 carries them | `ready-definition.yaml` declares `estimate_exempt_classes: [spike, incident, debt-remediation]` — the three literal §29.3 words — and `estimate_capture.py` **requires** `--item-class`; a call without it exits `3` (`ERROR missing-item-class`), never `0` |

**Options.** (a) **A** confirm aggregation and select `aggregated`; **B** select `single_project_fallback` without
confirming, which §29.1 permits only as the fallback. (b) **A** set a magnitude and window; **B** route on any
decrease, which is noisier but has no invented number. (c) **A** name the field and its closed vocabulary;
**B** keep `--item-class` mandatory on the caller for ever, which pushes the classification onto whoever calls.
**Binding.** **L4 must not** pick a mode, name a vendor, create a board, or **infer** an item class from a title, a
label, a linked incident record or a column.
**Blocks.** Nothing in Lane 4's phase. Row (b)'s drop measure renders `unarmed — not yet instrumented` under D77
and **cannot render as a miss**.

---

#### REG-057 — Phase 0 / Phase 1 overlap on the records-repository skeleton

**Priority** P2 · **Gates** `Ph1` · **Escalates at** immediately, if `L4-T002` is started · **Decided by** L0
**Raised as** `D-L4-TL-3` (`lanes/L4-06` §1)
**State:** Closed — Forced by PARTITION.md

`lanes/L4-00` §11 defines `L4-T002` *"Records repository skeleton"* and `L4-T003` *"Protection requirement declared
for L0"*. `lanes/L4-01` §0.3 defines `L4-P1-T02` (create the repository), `L4-P1-T03` (directory-per-item
skeleton), `L4-P1-T04` (root documents) and `L4-P1-T05`/`L4-P1-T06` (the two rulesets). **These overlap in scope and
would create the same platform objects twice.** Deleting or superseding a task defined in another lane document is
a judgment about document authority, which is L0's.
**Options.** **A** — `lanes/L4-01` is authoritative and `L4-T002`/`L4-T003` are withdrawn. **B** — `lanes/L4-00` is
authoritative and `L4-01`'s five rows are re-scoped to "verify, do not create". A leaves the charter with a hole in
its task list; B leaves the detailed file unable to bootstrap from nothing.
**Blocks.** `L4-T002`, `L4-T003`. Everything else proceeds; `L4-T004` onward do not depend on them.
**In force.** Run `L4-T001` and `L4-T004`–`L4-T007`, then **stop and wait**. Do not create `control-plane-records`
twice.

---

#### REG-058 — Is DevLake installed in V1?

**Priority** P2 · **Gates** `Ph2` · **Escalates at** `G3` — §99.3 item 4 requires DevLake field coverage confirmed **before G3**
**Decided by** L0 (`L0D-24`) · **Raised as** `V1-D3` (`master/06` §12)
**State:** Closed — Forced by spec

The two sides, verbatim. §98.2 Phase 2, bullet one: *"DevLake and Grafana on the operations VM, connected to the
organisation."* §99.4 item 7: *"Founder view v0 from GitHub API and reconciliation output plus Scorecard —
**DevLake is heavy and safely deferrable a few weeks in a solo build**; review and cycle-time metrics need team
activity to be meaningful anyway."*
**Bearing on the decision.** Phase 2's completion check reads *"every product visible in Grafana with a Scorecard
score"*, which **does not require DevLake**. §99.5 warns: *"Confirm DevLake's required database engine and version
for the pinned release before install — it determines the compose file and the control-plane backup procedure."*
Ten V1-adjacent signals name DevLake as their source (SIG-04, SIG-07, SIG-08, SIG-40 among them) and would render
**unarmed — not yet instrumented** under **D77** if it is deferred, which is a legitimate state, not a failure.
**Options.** **A** (recommended by its raiser) — deferred out of V1; V1 ships Grafana + Prometheus + Scorecard, and
DevLake installs when team activity makes review and cycle-time metrics meaningful, and in any case before `G3`.
**B** — in V1 as Phase 2 states, buying the DevLake-sourced signals earlier at the cost of the database-engine
decision, the compose file and the control-plane backup procedure landing inside V1.
**Blocks.** L5's `ops-vm/**` compose file and the control-plane backup procedure; whether L4's `metrics/**` targets
DevLake models or the GitHub API directly.
**In force.** None recorded. §99.4 is the section that defines V1 membership; §98.2's bullet is a phase inventory
which **D99** has already established is not a schedule. **Record the answer either way, so it is not
re-litigated.**

---

#### REG-059 — Does the operational asset inventory ship a V1 sliver?

**Priority** P2 · **Gates** `Ph2` · **Escalates at** the first machine-credential expiry · **Decided by** L0 (`L0D-24`)
**Raised as** `V1-D5` (`master/06` §12)
**State:** Closed — Forced by spec

§98.3 defers the operational asset inventory and vendor deadline watch to Early hardening: *"Needed before the
first certificate expiry, roughly month 3."* §97.2 states the opposite for one class of asset: *"Each control-plane
machine credential carries its **expiry date**, not only its rotation cadence, in the operational asset inventory,
so the 30-day expiry alert fires on it like any other asset (Section 49)."* V1 creates exactly two such
credentials — the **reconciler** credential and the **records-writer** GitHub App token (§40.1, D89) — and §99.6
risk 6 makes the reconciler's the highest-privilege identity in the estate.
**Options.** **A** (recommended) — a minimal sliver in V1: `assets/**` holds **machine-credential rows only**
(owner, expiry date, rotation cadence, 30-day lead alert). Certificates, domains, OAuth, signing and vendor
deprecations wait for Early hardening; band impact is within the **S** end of subsystem Q's S–M range. **B** —
nothing in V1: the two expiries live only in the runbook and the 30-day alert does not fire on them, which must be
recorded as a **dated accepted risk with an owner**, since §97.2 states the requirement in the present tense.
**Blocks.** L5's `assets/**` tasks, and whether the 30-day expiry alert exists at V1 exit. Interacts with
**REG-026** (d) and **REG-039** (a).
**In force.** None recorded. Note that two rows and one alert is smaller than the accepted-risk record option B
would require, and that an unwatched expiry on the reconciler credential is the failure §99.6 risk 6 is written
about.

---

#### REG-060 — The seven design-open items of §99.3

**Priority** P2 · **Gates** per item — see the table · **Decided by** L0, all seven, absolutely (`L0-00-charter.md` §3 pillar 4)
**Raised as** `L0D-10` … `L0D-16` (`L0-00-charter.md` §4) · `D-EE-4` (`master/05` §1) · `master/01` §10
> *Cross-reference: See `PENDING_FOUNDER_DECISIONS.md` — no dedicated PFD yet; L0 must supply literal values directly.*

§99.3 names exactly seven matters the implementer must still invent, *"each logged as such at build time"*. This is
that log. **No lane invents any of them.** A lane whose task appears to require one files a blocker naming the
`L0D-` id and **REG-060** — that is forbidden action `C-09`.

| `L0D-` | §99.3 item | The open matter | Gates | Which lane would otherwise invent it |
|---|---|---|---|---|
| **L0D-10** | 1 | The **attention classifier and constraint diagnosis algorithm** — Healthy / Watch / Action Required with the reason on the same line, and *"which constraint binds"* | `G3` | L4 (metrics) |
| **L0D-11** | 2 | The **`make parity` declaration format** — the environment-schema format compared across local, staging and production, defined once and reused | `Ph4`, because Phase 4's completion check runs `make parity` | L2 (the parity job) and L1 (the schema) |
| **L0D-12** | 3 | **Plan-checker internals** — verify every assumed capability against the exact pinned GSD release before configuring it; budget the in-house build if verification fails | `Ph7`; the verification itself is a `Ph1` item (§99.6 risk 4) and an entry criterion (`master/00` EC-9) | unassigned subsystem **G** — see **REG-001** |
| **L0D-13** | 4 | **DevLake field coverage** — which metrics need bespoke computation beyond DevLake's models (routine reviews absorbed cross-checked against the routing table, reviewer familiarity, reviewer-spread) | before `G3`, which §98.5 makes conditional on confirmed coverage | L4 — see **REG-058** |
| **L0D-14** | 5 | **Machine sources for context checks** — where the computable boundary is drawn across the fifteen systemic context checks of §80, with the humans named in §80.2 classifying the rest | `P4` | subsystem **P** — see **REG-001** |
| **L0D-15** | 6 | **KPI instrumentation projects** — scoping each §79 row marked *"available after instrumentation"* as its own mini-project with its own owner | `P2` | subsystem **P** |
| **L0D-16** | 7 | **Calibration methods** — PLU fit, forecast scoring, sustainable-utilisation bands, the §97.4 attention-session parameters, the §72.3 confidence table | quarterly refits; the first method recorded at `G5` | L4 — and the **initial values** are **REG-023** |

**Item 2 has a stated sequence and it is not a free choice**: L0 defines the format, **then** L1 schematises it,
**then** L2 consumes it, in that order (`master/01` §10). Doing it in any other order produces a schema for a
format that does not exist yet.
**Constraint binding on **REG-001****: items 1 and 3 are design-open, so subsystems **G** and **P** may not be
assigned to a lane in any form under any option — PARTITION's AI-developer profile forbids a task that requires
designing. They are L0 work under every option.
**Options.** Per item, the options are **A** invent and record it, **B** declare the dependent phase `declined`
under §98.1 with gate answers, forgone capabilities and a review date (`L0D-20`). There is no third option: an item
left open past its gating phase is a phase that neither completed nor declined, which §98.1 has no state for.
**In force.** Until an item is closed, **no lane may build anything whose behaviour depends on it.**
Item 7's *initial* values must still be recorded as configuration so the exit command has something to assert
against (`D-EE-4`) — that is **REG-023**, which is `P2` and does not wait for the method.

---

#### REG-061 — The `contracts/gate/**` freeze scope

**Band:** P0 · **Gates:** Ph0 · **Decided by** L0 · **Closed:** 2026-09-02

`L0-00-04` defined `make freeze` / `make promote-check` as hashing every file under `contracts/`. `L0-05-01`–`T13`
write `contracts/gate/**`, and `contracts/gate/PHASE` is advanced by L0 at each §98 phase boundary — a mutable
file inside a tree whose hash is asserted immutable, causing `CONTRACTS-DRIFT` on every `make train-preflight`.

**Chosen option (b):** redefine `freeze` and `promote-check` to exclude `contracts/gate/` and `contracts/ci/`;
add `gate-freeze` target hashing `contracts/gate/` excluding `PHASE`; `gate/v1.0.0` anchors the gate tree.
Record: **FD-029** (`Code/implementation/_FOUNDER_DECISIONS.md`).

---

#### REG-062 — The git identity a lane developer commits under

**Band:** P1 · **Gates:** Ph0, O-0 and every commit thereafter · **Decided by** L0 (Founder-ratified) · **Closed:** 2026-09-16

`master/02-branch-merge-model.md` §12 raises this as **DECISION D-BMM-01** (previously colliding with the
unrelated `D-L0-01` in `lanes/L0-01-phase-0-contracts.md` — the JSON Schema dialect ruling, closed separately
at **REG-005**; see the collision row added to §5.2 below) and leaves it formally open, with three options and a
recommendation. It blocks the first command (`git config user.name/user.email`) of every one of the five lanes.

| Option | Mechanism |
|---|---|
| **A** (ratified) | Five GitHub machine accounts, `lane-1`…`lane-5`, each with Write on `control-plane`. Never appear in `CODEOWNERS`; their approvals never satisfy a gate. |
| B | All lanes commit as L0's human identity, with `Co-authored-by: lane-N` / `Lane: N` trailers |
| C | One shared machine account `lane-bot`, lanes distinguished only by branch prefix |

**Chosen option (A).** `manual/05-git-workflow.md` §5 already operationalises this exact choice — `AGENT_NAME`
(`lane1-bot`) and `AGENT_EMAIL` (`lane1-bot@users.noreply.github.com`), set `--local` per clone (never `--global`)
— across all five lane packs; this entry ratifies that operational fact as the L0 decision rather than leaving
it standing on an unresolved `DECISION D-BMM-01` while every lane pack already assumes option A. This closes
`master/02`'s D-BMM-01 with no further action needed from any lane: mirror the five accounts into `people.yaml`
under the machine-account class of Section 11.2, per `master/02`'s own recommendation, as part of Phase-0 bootstrap
(no lane task changes as a result of this ratification — the mechanism was already in force).

---

## 4. How a lane uses this register

### 4.1 The lookup, in three commands

A lane executor reaching a DECISION REQUIRED block in its own file does exactly this and nothing else.

**Commands**

```bash
cd "$CP_ROOT"
git checkout integration && git pull --ff-only

# 1. Resolve the source id you found in your lane file to its REG id.
grep -P '^DR-L3-05-C\t' docs/decisions/concordance.tsv

# 2. Read the entry.
cat docs/decisions/open/REG-039.md

# 3. Confirm it is still open.
awk -F'\t' '$1=="REG-039"{print $1, $3, $6}' docs/decisions/register.tsv
```

If field 6 (`state`) reads `open`, the decision is not made and **the task STOPs**. If it reads `closed`, field 9
names the decision record in `records/decisions/` that carries the answer; read that record, not this register.

### 4.2 The blocker addendum

`L0-00-charter.md` §7.1's template is unchanged. One line is **added** to it, and the canonical copy at
`docs/escalation/BLOCKER.md` is updated by task `L0-04-06`:

```text
FORBIDDEN/UNDECIDED ID:   <F-nn or C-nn or L0D-nn, or NONE>
REGISTER ID:              <REG-nnn, or NONE>          <-- added by L0-04-06
SPEC SENTENCE QUOTED:     <verbatim, with section number; or NONE>
```

**The rule.** Cite the `REG-` id. Citing only the source id you found in your own lane file is what produced eight
parallel registers, and a blocker that names `D-L2-08` does not tell L0 which of the **three different decisions**
carrying that id is meant.

### 4.3 What a lane may never do with this register

| # | Forbidden | Why |
|---|---|---|
| 1 | Edit any file under `docs/decisions/**` | `docs/**` is L0's exclusively; `F-02` and `F-03` |
| 2 | Add a register row, or a concordance row for an id it invented | The id space is allocated once, by L0 (`L0D-DR-1`) |
| 3 | Treat an "in force until answered" line as permission to choose something else | Those lines are transcribed from the raising document; they are the **only** permitted interim behaviour and they are all fail-closed |
| 4 | Close an entry, mark one `declined`, or act on an entry whose `state` is `open` | Closure is a dated decision record written by L0 (`L0D-DR-3`); `C-08` and `C-11` |
| 5 | Proceed because an entry is `P3` | `P3` means nothing stops **today**; the `Escalates at` line says when that changes |

---

## 5. The concordance — every source id, mapped

This is the dedup evidence and the lookup table `4.1` reads. It is **generated** into
`docs/decisions/concordance.tsv` by task `L0-04-02`, from the register's own `sources` field, so a source id can
never map to two entries by transcription error. **One hundred and eighty-eight source tokens map to sixty entries.** Nine source ids are used for more than one
decision and are disambiguated by the file that raised them.

Read it as: *the id in column 1, raised in the file in column 2, is entry `REG-nnn`.* Where several source ids map
to one `REG-`, they are the same decision and only the `REG-` id is used from here on.

| Source id | Raised in | → |
|---|---|---|
| `D-PLAN-01`, `D-PLAN-02` | `master/00-MASTER-PLAN.md` §2.3 | **REG-001** |
| `LA-01` | `master/01-lane-architecture.md` §9 | **REG-001** |
| `D-REQ-4` | `master/03-conflict-prevention.md` §8 | **REG-001** |
| `DECISION 1` | `master/04-phase-map.md` §8 | **REG-001** |
| `D-EE-2` | `master/05-entry-exit-criteria.md` §1 | **REG-001** |
| `V1-D1`, `V1-D2` | `master/06-v1-scope.md` §12 | **REG-001** |
| `DEC-01` | `master/07-risk-register.md` §7 | **REG-001** |
| `DECISION REQUIRED #2` | `lanes/L1-00-charter.md` §12 | **REG-001** |
| `L0-IG-D3`, `L0-IG-D4` | `lanes/L0-05-integration-gate.md` §5 | **REG-001** |
| `D-L2-12` | `lanes/L2-06-tests.md` §5 | **REG-001** |
| `D-L4-P4-04` | `lanes/L4-04-attention-ledger.md` §5 | **REG-001** |
| `D-L4-P5-03` | `lanes/L4-05-pipeline-and-boards.md` §6 | **REG-001** |
| `DR-L0-07-F` | `lanes/L0-07-onboarding-track.md` §10.2 | **REG-001** |
| `LA-02` | `master/01` §4, §9 | **REG-002** |
| `D-REQ-3` | `master/03` §8 | **REG-002** |
| `DEC-02` | `master/07` §7 | **REG-002** |
| `D-L2-06` | `lanes/L2-00-charter.md` §9; `lanes/L2-05-tasks.md` §1 | **REG-002** |
| `DR-L1-06-D` | `lanes/L1-06-tests.md` §5 | **REG-002** |
| `L0D-LG-1`, `L0D-LG-2`, `L0D-LG-3` | `lanes/L0-02-lane-guard.md` §4, §11 | **REG-002** |
| `D-EE-1` | `master/05` §1 | **REG-003** |
| `L1-D01` | `lanes/L1-05-tasks.md` §1 | **REG-003** |
| `validator_runtime` | `lanes/L1-03-validators.md` §1 | **REG-003** |
| `D-3` | `lanes/L1-04-ci-gate-engine.md` §4 | **REG-003** |
| `D-L2-07` (`L2-05` sense) | `lanes/L2-05-tasks.md` §1 | **REG-003** |
| `L3-D1` | `lanes/L3-06-tasks.md` §1 | **REG-003** |
| `D-L3-01` | `lanes/L3-01-diff-engine.md` §1 | **REG-003** |
| `D-L3-04-01` | `lanes/L3-04-provisioning.md` §1 | **REG-003** |
| `D-L4-TL-1` | `lanes/L4-06-tasks.md` §1 | **REG-003** |
| `DECISION REQUIRED 1` | `master/09-glossary-and-conventions.md` §19 | **REG-004** |
| `DECISION REQUIRED 2` | `master/09` §19 | **REG-005** |
| `DECISION REQUIRED 3` | `master/09` §19 | **REG-060** (§99.3 item 2, `L0D-11`) |
| `DR-L1-06-B` | `lanes/L1-06` §5 | **REG-018** · also bears on **REG-005** |
| `DECISION REQUIRED 4` | `master/09` §19 | **REG-006** |
| `L3-D2` | `lanes/L3-06` §1 | **REG-007** |
| `DR-L3-07-A` | `lanes/L3-07-tests-and-runbook.md` §2 | **REG-041** · also bears on **REG-007** |
| `D-1` | `lanes/L1-04` §4 | **REG-025** · also bears on **REG-007** |
| `D-L4-TL-5` | `lanes/L4-06` §1 | **REG-009** · also bears on **REG-007** |
| `D-L2-02` | `lanes/L2-00` §9 | **REG-018** · also bears on **REG-007** |
| `D-REQ-2` | `master/03` §8 | **REG-008** |
| `DECISION 2` | `master/04` §8 | **REG-017** · also bears on **REG-008** |
| `LA-04` | `master/01` §9 | **REG-022** · also bears on **REG-008** |
| `D-L4-01` (`L4-01` sense: org login) | `lanes/L4-01-records-repo.md` | **REG-009** |
| `DECISION 5` | `master/04` §8 | **REG-009** · also bears on **REG-048** |
| `D-REQ-1` | `master/03` §8 | **REG-010** |
| `C-1`, `C-2`, `C-18`, `C-19`, `C-20`, `G-2` | `master/INDEX.md` §7 | **REG-011** |
| `C-3`, `C-4`, `C-5`, `C-6`, `R-6` | `master/INDEX.md` §7 | **REG-012** |
| `C-13`, `C-14` | `master/INDEX.md` §7 | **REG-013** |
| `C-15` | `master/INDEX.md` §7 | **REG-014** |
| `L0D-LG-5` | `lanes/L0-02` §11 | **REG-014** |
| `D-EE-3` | `master/05` §1 | **REG-015** |
| `L0-IG-D2` | `lanes/L0-05` §5 | **REG-015** |
| `G-6`, `R-12` | `master/INDEX.md` §7 | **REG-015** |
| `D-08-6` | `master/08-progress-tracking.md` §10 | **REG-016** |
| `LA-03` | `master/01` §9 | **REG-017** |
| `DECISION REQUIRED #1`, `#3` | `lanes/L1-00` §12 | **REG-017** |
| `DR-L0-07-A`, `DR-L0-07-E` | `lanes/L0-07` §7, §5.1 | **REG-017** |
| `DR-3.1` | `lanes/L3-03-canary-and-integrity.md` §2 | **REG-026** · also bears on **REG-017** |
| `D-L2-01` | `lanes/L2-00` §9 | **REG-017** |
| `D-08-1` | `master/08` §2 | **REG-017** n |
| `framework_registry_path` | `lanes/L1-03` §1 | **REG-017** |
| `G-7` | `master/INDEX.md` §7 | **REG-017** |
| `DECISION REQUIRED #4` | `lanes/L1-00` §12 | **REG-018** |
| `D-2` | `lanes/L1-04` §4 | **REG-018** |
| `D-L2-03` | `lanes/L2-00` §9 | **REG-019** |
| `D-L4-02` (`L4-01` sense: signing) | `lanes/L4-01` | **REG-019** |
| `D-L4-P3-02` | `lanes/L4-03-write-paths.md` §5 | **REG-019** |
| `D-L2-08` (`L2-03` sense), `D-L2-10` | `lanes/L2-03-production-gates.md` §5 | **REG-020** |
| `D-L3-02`, `D-L3-03` | `lanes/L3-01` §1 | **REG-020** |
| `DEC-L3-02-03` | `lanes/L3-02-levels-and-repair.md` §2 | **REG-020** |
| `D-L4-P3-01` | `lanes/L4-03` §5 | **REG-020** |
| `D-L4-P5-01` | `lanes/L4-05` §6 | **REG-020** |
| `R-7` | `master/INDEX.md` §7 | **REG-020** |
| `LA-05` | `master/01` §9 | **REG-021** |
| `D-L4-01` (`L4-00` sense: enum mechanism) | `lanes/L4-00-charter.md` §9 | **REG-021** |
| `DECISION-L1-02-B` | `lanes/L1-02-schemas.md` §3 | **REG-021** |
| `L1-D05` | `lanes/L1-05` §1 | **REG-021** · also bears on **REG-043** h |
| `D-L2-08` (`L2-04` sense) | `lanes/L2-04-evidence-chain.md` §4 | **REG-021** |
| `D-L4-P3-03` | `lanes/L4-03` §5 | **REG-021** |
| `D-L4-02` (`L4-00` sense: metric register) | `lanes/L4-00` §9 | **REG-022** |
| `L1-D04` | `lanes/L1-05` §1 | **REG-022** |
| `L0D-17` | `L0-00-charter.md` §5.1 | **REG-023** |
| `L2/P1/DEC-C` | `lanes/L2-01-reusable-workflows.md` §1 | **REG-023** |
| `DECISION REQUIRED #3` | `lanes/L0-06-bootstrap-mode.md` §5 | **REG-023** |
| `D-EE-5` | `master/05` §1 | **REG-023** |
| `DEC-L3-02-01`, `DEC-L3-02-04` | `lanes/L3-02` §2 | **REG-024** |
| `L3-D4` | `lanes/L3-06-tasks.md` §5 | **REG-024** |
| `DR-3.2` | `lanes/L3-03` §2 | **REG-024** · also bears on **REG-028** |
| `D-L3-04` (b) | `lanes/L3-01` §1 | **REG-024** |
| `DEC-L3-02-02` | `lanes/L3-02` §2 | **REG-025** |
| `DR-L3-01` | `lanes/L3-00-charter.md` §10 | **REG-025** |
| `D-L2-07` (`L2-02` sense) | `lanes/L2-02-digest-invariant.md` §4 | **REG-025** |
| `L3-D3` | `lanes/L3-06` §1 | **REG-026** |
| `D-L3-04-02` | `lanes/L3-04` §1 | **REG-026** |
| `DR-L3-02` | `lanes/L3-00` §10 | **REG-027** |
| `DR-L3-03` | `lanes/L3-00` §10 | **REG-028** |
| `D-L3-04` (a) | `lanes/L3-01` §1 | **REG-028** |
| `DR-L3-04` | `lanes/L3-00` §10 | **REG-029** |
| `L2/P1/DEC-A` | `lanes/L2-01` §1 | **REG-030** |
| `L2/P1/DEC-B` | `lanes/L2-01` §1 | **REG-031** |
| `D-L2-05` | `lanes/L2-00` §9 | **REG-032** |
| `D-L2-08` (`L2-05` sense) | `lanes/L2-05` §1 | **REG-033** |
| `D-L2-09` (`L2-04` sense) | `lanes/L2-04` §4 | **REG-034** |
| `D-L2-07` (`L2-04` sense) | `lanes/L2-04` §4 | **REG-035** |
| `D-L2-09` (`L2-02` sense) | `lanes/L2-02` §4 | **REG-036** |
| `D-L2-09` (`L2-03` sense) | `lanes/L2-03` §5 | **REG-037** |
| `D-L2-11` | `lanes/L2-06` §5 | **REG-038** |
| `DR-L3-05-A` … `DR-L3-05-E` | `lanes/L3-05-orphans.md` §5 | **REG-039** |
| `D-L3-04-03` | `lanes/L3-04` §1 | **REG-040** |
| `DR-L3-07-A`, `DR-L3-07-B` | `lanes/L3-07` §2 | **REG-041** |
| `L1-D03` | `lanes/L1-05` §1 | **REG-042** |
| `DECISION-L1-02-A`, `DECISION-L1-02-C` | `lanes/L1-02` §3 | **REG-043** a, c |
| `L1-D02` | `lanes/L1-05` §1 | **REG-043** b |
| `control_classification_home`, `records_snapshot_mode` | `lanes/L1-03` §1 | **REG-043** d, e |
| `DR-L1-06-C`, `DR-L1-06-A` | `lanes/L1-06` §5 | **REG-043** f, g |
| `DECISION REQUIRED #1`, `#2` | `lanes/L0-06` §5 | **REG-044** |
| `L0-IG-D1` | `lanes/L0-05` §5 | **REG-045** |
| `V1-D6` | `master/06` §12 | **REG-046** |
| `V1-D4`, `DECISION 4` | `master/06` §12; `master/04` §8 | **REG-047** |
| `DECISION 3` | `master/04` §8 | **REG-048** |
| `DR-L0-07-B` | `lanes/L0-07` §5 | **REG-044** |
| `DR-L0-07-C`, `DR-L0-07-D`, `DR-L0-07-G` | `lanes/L0-07` §5.2, §2.3, §3 | **REG-048** |
| `D-L2-08` (`L2-02` sense) | `lanes/L2-02` §4 | **REG-049** |
| `D-L2-13` | `lanes/L2-06` §5 | **REG-050** |
| `D-L4-04` … `D-L4-07` | `lanes/L4-02-record-schemas.md` §4 | **REG-051** |
| `D-L4-P4-01`, `-02`, `-03` | `lanes/L4-04` §5 | **REG-052** a, b, c |
| `D-L4-P7-03` | `lanes/L4-07-tests-and-runbook.md` | **REG-052** d |
| `D-L4-P7-01` | `lanes/L4-07` | **REG-053** |
| `D-L4-P7-02`, `D-L4-TL-4`, `D-08-2`, `C-26` | `lanes/L4-07`; `lanes/L4-06` §1; `master/08` §10; `master/INDEX.md` | **REG-054** |
| `D-L4-03`, `C-10` | `lanes/L4-00` §9; `master/INDEX.md` | **REG-055** |
| `D-L4-P5-02`, `D-L4-P5-04`, `D-L4-P5-05` | `lanes/L4-05` §6 | **REG-056** |
| `D-L4-TL-3` | `lanes/L4-06` §1 | **REG-057** |
| `V1-D3` | `master/06` §12 | **REG-058** |
| `V1-D5` | `master/06` §12 | **REG-059** |
| `L0D-10` … `L0D-16`, `D-EE-4` | `L0-00-charter.md` §4; `master/05` §1 | **REG-060** |
| `D-08-3` | `master/08` §10 | **REG-017** n · see §5.1 |
| `D-08-5` | `master/08` §10 | **REG-011** · see §5.1 |
| `D-L4-TL-2` | `lanes/L4-06` §1 | **resolved by this file — see §5.2** |

### 5.1 Two `master/08` items that are process, not decisions, and where they went

`D-08-3` (*who runs the daily report*) and `D-08-5` (*what the phase burn-down is denominated in*) are recorded in
`docs/decisions/register.tsv` as rows **REG-017 n** and a note on **REG-011** respectively, because each collapses
into a question already open:

- **`D-08-3`** — its two options are (A) L0 runs `daily-report.sh` from a workstation each morning, or (B) L0 issues
  an L2 task packet whose deliverable is `.github/workflows/plan-daily-report.yml`. The obstacle is that
  `.github/workflows/` is L2's, which is **REG-002**'s obstacle; the home for the scripts is **REG-017** row n.
  Trade-off, recorded: A costs nothing and *"does not run when L0 does not"*; B makes the programme's own
  instrument a lane deliverable with a lane's lead time.
- **`D-08-5`** — its two options are (A) denominate in §99.2 subsystem complexity bands per **D99** and treat
  §98.2's week labels as configuration-elapsed ordering, or (B) denominate in the week labels, *"simple, and known
  to be wrong by D99's own reasoning"*. This is the same vocabulary problem as **REG-011** (c) and must be settled
  in the same record. `master/08` §10: *"Take it at the first weekly review, record it, and never revisit it
  mid-programme."*

### 5.2 The id collision this file resolves, and what happens to the colliding ids

`D-L4-TL-2` asks: *"Renumber which set, to what."* This file answers it **without renumbering anything**, which is
the point of `L0D-DR-1`.

| Colliding id | Sense 1 | Sense 2 | Sense 3 |
|---|---|---|---|
| `D-L2-07` | required-context name composition (`L2-02`) → **REG-025** | the eleven-question field binding (`L2-04`) → **REG-035** | implementation language for `tools/evidence/**` (`L2-05`) → **REG-003** |
| `D-L2-08` | `digest-invariant-selftest` required status (`L2-02`) → **REG-049** | verification-block store path (`L2-03`) → **REG-020** a | template placeholder syntax (`L2-05`) → **REG-033**; *and* the two `event_type` identifiers (`L2-04`) → **REG-021** |
| `D-L2-09` | the S18 digest carrier (`L2-02`) → **REG-036** | privileged-runner tier evidence (`L2-03`) → **REG-037** | the `/version` transport (`L2-04`) → **REG-034** |
| `D-L4-01` | the `event_type` enum mechanism (`L4-00`) → **REG-021** | the GitHub organisation login (`L4-01`) → **REG-009** | — |
| `D-L4-02` | the metric register boundary (`L4-00`) → **REG-022** | records-writer commit signing (`L4-01`) → **REG-019** | — |
| `D-L4-03` | `.github/**` in the records repo (`L4-00`) → **REG-055** | records-writer key custody (`L4-01`) → **REG-019** | — |
| `DECISION REQUIRED #1` | `master/09` §19 → **REG-004** | `lanes/L1-00` §12 → **REG-017** | `lanes/L0-06` §5 → **REG-044** |
| `DECISION REQUIRED #2` | `master/09` §19 → **REG-005** | `lanes/L1-00` §12 → **REG-001** | `lanes/L0-06` §5 → **REG-044** |
| `DECISION REQUIRED #3` | `master/09` §19 → **REG-060** | `lanes/L1-00` §12 → **REG-017** | `lanes/L0-06` §5 → **REG-023** |
| `DECISION REQUIRED #4` | `master/09` §19 → **REG-006** | `lanes/L1-00` §12 → **REG-018** | — |
| `D-L0-01` | contract shapes: JSON Schema draft 2020-12 for validators, declarative YAML for fact tables (`lanes/L0-01-phase-0-contracts.md` §1) → **REG-005** | the lane-developer git identity, raised in `master/02-branch-merge-model.md` §12 under the collision-avoiding id **D-BMM-01** → **REG-062** | — |

The last four rows are the worst case in the set: four documents number their blocks `#1`…`#4` with no prefix at
all, so the bare label carries **no** information across files. A blocker citing *"DECISION REQUIRED #2"* is
unroutable on its face, which is why §4.2 makes the `REG-` id mandatory rather than merely helpful.

**No lane document is renumbered.** Every lane file keeps the id it already carries; the concordance disambiguates
by **file**, and §4.2's blocker line makes the `REG-` id the thing L0 actually reads. Renumbering a lane document
would be a foreign-path write by whoever did it, which is exactly why `D-L4-TL-2` could not fix itself.

---

## 6. DECISION REQUIRED — items this file cannot close by itself

Written in the house form of `lanes/L0-05-integration-gate.md` §5 and `lanes/L1-00-charter.md` §12. Neither blocks
a task below; each states what this file does in the meantime, and each is itself a register row.

### DECISION REQUIRED — L0-DR-D1: may L0 write into `records/decisions/` at all?

**The fact.** `L0-00-charter.md` §5 requires every closure to be *"written as a decision record under
`records/decisions/` using the §97.2 schema, and every open prompt as a record under `records/decisions/pending/`
via the record-decision CLI (§97.2)"*. PARTITION.md gives **ALL of `control-plane-records`** to **L4**, and
`master/01` §2 row 26 restates it as *"Stated as ALL. No exception."* So the party writing every decision record is
not the party that owns the repository it lands in.
**Why it is not a contradiction on its face.** §97.1 distinguishes the **write path** from **path ownership**:
records are written through the records-writer credential by a mechanism L4 builds, and a human record travels the
review lane. L0 writing a decision record through L4's CLI is a **use** of L4's mechanism, not an edit of L4's
tree — the same relationship every lane has with every other lane's published artifact (PARTITION rule 4).
**Why L0 must still state it.** The `record-decision` CLI is an L4 deliverable that does not exist at Phase 0, and
`L0-04-08` needs somewhere to put a closure on day one.
**Interim behaviour, defined.** `L0-04-08` writes the closure to `docs/decisions/closed/REG-nnn.yaml` — L0-owned,
directory-per-item, carrying the exact §97.2 field set (`id`, `decider`, `prompt_received`, `decided`, `subject`,
`options_considered`, `evidence`, `review_date`) — and the register row's `record` field names that path. At
cutover, `L0-04-08` re-emits every closed row through the `record-decision` CLI and rewrites the `record` field to
the `records/decisions/` path. **Nothing is hand-edited into `records/**` at any point** (`F-11`).
**Blocks.** Nothing.

### DECISION REQUIRED — L0-DR-D2: which `record_schema_version` does a Phase-0 closure carry?

**The fact.** §97.2 requires every record to carry `record_schema_version`. The decision-record schema is **L4**'s
(`schemas/records/**`) and lands in Lane 4's Phase 2; `L0-04-08` closes register rows from Phase 0 onward.
**Why L0.** `record_schema_version` handling is `L0D-03`, reserved in the charter. Stamping a version that no
schema defines yet, and stamping none, are both choices.
**Interim behaviour, defined.** `docs/decisions/closed/REG-nnn.yaml` omits `record_schema_version` entirely and
carries `pending_schema: L0-DR-D2` instead. `reg-lint.sh` **FAILS** if a closure file carries a
`record_schema_version` value before L4 has published the schema — a fabricated version is worse than an absent
one, because a validator would accept it. At cutover the CLI stamps the real value.
**Blocks.** Nothing. `L0-04-08` runs and produces a file that is deliberately not yet a record.

---

## 7. The register file format

Four files and one directory, all under `docs/decisions/`, all L0-owned.

| Path | What it is | Written by |
|---|---|---|
| `docs/decisions/register.tsv` | **The source of truth.** One row per entry, 10 tab-separated fields | `L0-04-01`, then `L0-04-08` on each closure |
| `docs/decisions/concordance.tsv` | Source id → `REG-` id, 3 fields | `L0-04-02` |
| `docs/decisions/gates.tsv` | `REG-` id → gating phase → blocked task ids, 3 fields | `L0-04-03` |
| `docs/decisions/open/REG-nnn.md` | One rendered file per **open** entry | `L0-04-06`, rendered — never hand-edited |
| `docs/decisions/closed/REG-nnn.yaml` | One closure per closed entry, §97.2 field set | `L0-04-08` |
| `docs/decisions/L0-decision-register.md` | The human index `docs/README.md` already names (`L0-00-02`) | `L0-04-06`, rendered |
| `docs/decisions/bin/reg-status.sh`, `reg-lint.sh`, `reg-close.sh` | The three scripts | `L0-04-04`, `T05`, `T08` |

**`register.tsv` — ten fields, in this order, tab-separated, no field ever empty:**

| # | Field | Values |
|---|---|---|
| 1 | `id` | `REG-001` … `REG-060` |
| 2 | `priority` | `P0` \| `P1` \| `P2` \| `P3` |
| 3 | `gates` | a phase token: `Ph0`…`Ph7`, `EH`, `G1`…`G8`, `P1`…`P8` |
| 4 | `title` | one line, no tabs |
| 5 | `decider` | `L0` for every row; the column exists so a future delegation is visible |
| 6 | `state` | `open` \| `closed` \| `declined` \| `withdrawn` (`L0D-DR-4`) |
| 7 | `blocks` | comma-separated task ids, or `none` |
| 8 | `sources` | comma-separated source ids from the concordance |
| 9 | `record` | path of the closure file, or `-` while `open` |
| 10 | `opened` | ISO date the prompt was raised |

**Why TSV and not YAML.** Same reason `lane-paths.tsv` is TSV (`L0D-04`): the scripts need no parser and no
dependency, so the register is readable and checkable before **REG-003** picks a language.

**Why `open/` is rendered and never authored.** Two writable copies of one fact drift. The render is idempotent and
`reg-lint.sh` proves it: re-rendering into a scratch directory and diffing must produce no output.

---

## 8. Tasks in this file

Eight tasks. Executor: the human lead. All paths exact, all commands literal, all inside `docs/decisions/`.

| Task id | Title | Size | Depends on |
|---|---|---|---|
| `L0-04-01` | The register tree and `register.tsv` — all sixty-one rows | L | `L0-00-02` |
| `L0-04-02` | `concordance.tsv`, generated from the register and checked for uniqueness | S | `L0-04-01` |
| `L0-04-03` | `reg-lint.sh` — the eight integrity checks | M | `L0-04-02` |
| `L0-04-04` | `reg-status.sh` — the queue, by band and by gating phase | M | `L0-04-03` |
| `L0-04-05` | `reg-close.sh` — the closure procedure, and `closed/` | M | `L0-04-03` |
| `L0-04-06` | Render `open/`, the index, and add `REGISTER ID` to the blocker template | M | `L0-04-03` |
| `L0-04-07` | `make decisions`, `make decisions-gate`, and the `promote-check` hook | M | `L0-04-04`, `L0-04-06` |
| `L0-04-08` | The standing decision window, and the first sweep | S | `L0-04-07` |

---

## 9. The tasks

---

### L0-04-01 — The register tree and `register.tsv`

**Size:** L · **Dependencies:** `L0-00-02`

The register is authored as pipe-delimited text and converted to TSV in one step, so the file below is
copy-pasteable without preserving tab characters. The `opened` date is stamped by `awk`, never typed.

**Commands**

```bash
cd "$CP_ROOT"
git checkout integration && git pull --ff-only
mkdir -p docs/decisions/open docs/decisions/closed docs/decisions/bin

printf '%s\n' \
'# register.tsv — L0-owned (L0D-DR-2). THE source of truth for every open decision.' \
'# docs/decisions/open/*.md are RENDERED from this file; never hand-edit them.' \
'# 10 tab-separated fields: id  priority  gates  title  decider  state  blocks  sources  record  opened' \
'# state is one of: open | closed | declined | withdrawn  (L0D-DR-4)' \
'# A source token is <source-id>@<file>. The @ makes a colliding id unique by file.' \
> docs/decisions/register.tsv

awk -v d="$(date -u +%F)" 'BEGIN{FS="|";OFS="\t"} {$1=$1; $10=d; print}' >> docs/decisions/register.tsv <<'EOF'
REG-001|P0|Ph0|Subsystems G H J O and P are assigned to no lane|L0|open|L2-T700,L3-05-10,IG-06,IG-07,OT-P7|D-PLAN-01@master/00,D-PLAN-02@master/00,LA-01@master/01,D-REQ-4@master/03,DECISION-1@master/04,D-EE-2@master/05,V1-D1@master/06,V1-D2@master/06,DEC-01@master/07,DECISION-REQUIRED-2@lanes/L1-00,L0-IG-D3@lanes/L0-05,L0-IG-D4@lanes/L0-05,D-L2-12@lanes/L2-06,D-L4-P4-04@lanes/L4-04,D-L4-P5-03@lanes/L4-05,DR-L0-07-F@lanes/L0-07|-
REG-002|P0|Ph0|The lane guard sits inside the exclusive path of a lane it judges|L0|closed|L0-02-05,L0-02-06,L0-02-07,L2-T004,IG-08|LA-02@master/01,D-REQ-3@master/03,DEC-02@master/07,D-L2-06@lanes/L2-00,DR-L1-06-D@lanes/L1-06,L0D-LG-1@lanes/L0-02,L0D-LG-2@lanes/L0-02,L0D-LG-3@lanes/L0-02|FD-003@Code/implementation/_FOUNDER_DECISIONS.md
REG-003|P1|Ph0|Implementation toolchain language runtime and dependency pinning|L0|closed|L1-001,L1-03-00,L2-T500,L3-P0-02,L4-P2-02,L5-T02|D-EE-1@master/05,L1-D01@lanes/L1-05,validator-runtime@lanes/L1-03,D-3@lanes/L1-04,D-L2-07@lanes/L2-05,L3-D1@lanes/L3-06,D-L3-01@lanes/L3-01,D-L3-04-01@lanes/L3-04,D-L4-TL-1@lanes/L4-06|-
REG-004|P1|Ph0|The JSON Schema id host|L0|open|L1-02-05,L4-P2-02|DECISION-REQUIRED-1@master/09|-
REG-005|P1|Ph0|The JSON Schema validator implementation and dialect|L0|closed|L1-03-00,L2-T106,L4-P2-02|DECISION-REQUIRED-2@master/09|-
REG-006|P1|Ph0|Commit-signing scope on control-plane lane branches|L0|closed|L1-001,L2-T500,L3-P0-02,L4-P2-02,L5-T01,L5-T07|DECISION-REQUIRED-4@master/09|-
REG-007|P1|Ph0|The contracts surface list filenames and directory layout|L0|closed|L1-001,L1-03-00,L2-T500,L3-P0-03,L4-P2-02|G-5@master/INDEX,G-10@master/INDEX,R-9@master/INDEX|-
REG-008|P1|Ph0|Where the spec root-named registry files physically live|L0|closed|L1-001,L1-107|D-REQ-2@master/03|-
REG-009|P1|Ph0|The GitHub organisation login and the two calendar anchors|L0|open|L0-00-01,L4-P1-T02,L5-T05,L3-04-01|D-L4-01@lanes/L4-01,DECISION-5@master/04,D-L4-TL-5@lanes/L4-06|-
REG-010|P1|Ph0|L0 own branch prefix|L0|closed|L0-02-04|D-REQ-1@master/03|-
REG-011|P1|Ph0|Branch-name grammar task-id grammar and the phase crosswalk|L0|closed|L0-02-04,L0-03-03,L1-001,L2-T500,L3-P0-02,L4-P2-02,L5-T01|C-1@master/INDEX,C-2@master/INDEX,C-18@master/INDEX,C-19@master/INDEX,C-20@master/INDEX,G-2@master/INDEX,D-08-5@master/08|-
REG-012|P1|Ph0|Git conventions merge method staging branch creation message and templates|L0|closed|L0-03-05,L1-001,L2-T500,L3-P0-02,L4-P2-02,L5-T01|C-3@master/INDEX,C-4@master/INDEX,C-5@master/INDEX,C-6@master/INDEX,R-6@master/INDEX|-
REG-013|P1|Ph0|Branch-protection mechanism and the Phase 0 required-check list|L0|closed|L0-00-01,L5-T07|C-13@master/INDEX,C-14@master/INDEX|-
REG-014|P1|Ph0|CODEOWNERS content human identities lane teams or both|L0|open|L0-00-01,L0-02-05|C-15@master/INDEX,L0D-LG-5@lanes/L0-02|-
REG-015|P2|Ph0|Owner and path of the acceptance-test harness|L0|closed|L0-05-05,IG-07|D-EE-3@master/05,L0-IG-D2@lanes/L0-05,G-6@master/INDEX,R-12@master/INDEX|-
REG-016|P2|Ph1|The AT to phase map|L0|closed|B2@master/08|D-08-6@master/08|-
REG-017|P2|Ph0|The unowned-path schedule sixteen artifacts|L0|closed|L1-101,L2-T700,L3-03-10,L0-07-06|LA-03@master/01,DECISION-2@master/04,DECISION-REQUIRED-1@lanes/L1-00,DECISION-REQUIRED-3@lanes/L1-00,DR-L0-07-A@lanes/L0-07,DR-L0-07-E@lanes/L0-07,D-L2-01@lanes/L2-00,D-08-1@master/08,D-08-3@master/08,framework-registry-path@lanes/L1-03,G-7@master/INDEX|-
REG-018|P2|Ph1|The L1 validator invocation contract|L0|closed|L2-T106,L2-T107,L1-06-02|DECISION-REQUIRED-4@lanes/L1-00,D-2@lanes/L1-04,D-L2-02@lanes/L2-00,DR-L1-06-B@lanes/L1-06|-
REG-019|P2|Ph1|The record write interface and records-writer commit signing|L0|closed|L2-T544,L2-T545,L4-T313,L4-T314|D-L2-03@lanes/L2-00,D-L4-02@lanes/L4-01,D-L4-P3-02@lanes/L4-03|-
REG-020|P2|Ph2|The record stores section 97.2 does not list|L0|open|L2-T174,L2-T176,L3-01-11,L3-01-18,L4-T304|D-L2-08@lanes/L2-03,D-L2-10@lanes/L2-03,D-L3-02@lanes/L3-01,D-L3-03@lanes/L3-01,DEC-L3-02-03@lanes/L3-02,D-L4-P3-01@lanes/L4-03,D-L4-P5-01@lanes/L4-05,R-7@master/INDEX|-
REG-021|P2|Ph1|The closed event_type enum mechanism and identifier list|L0|closed|L1-107,L2-T509,L2-T512,L4-T305,L4-T308|LA-05@master/01,D-L4-01@lanes/L4-00,DECISION-L1-02-B@lanes/L1-02,L1-D05@lanes/L1-05,D-L2-08@lanes/L2-04,D-L4-P3-03@lanes/L4-03|-
REG-022|P2|Ph2|The metric register content boundary os-health.yaml|L0|closed|L1-605|LA-04@master/01,D-L4-02@lanes/L4-00,L1-D04@lanes/L1-05|-
REG-023|P2|Ph1|The calibrated values and their stated initial numbers|L0|open|L2-P1-T04,L2-P1-T05,L2-P1-T06,L3-P4,L0-06-03,L0-06-12,L3-01-11|L0D-17@lanes/L0-00,L2-P1-DEC-C@lanes/L2-01,DECISION-REQUIRED-3@lanes/L0-06,D-EE-5@master/05|-
REG-024|P2|Ph3|Drift classes the spec assigns to nothing|L0|closed|L3-02-02,L3-02-04,L3-02-06,L3-02-14,L3-01-20|DEC-L3-02-01@lanes/L3-02,DEC-L3-02-04@lanes/L3-02,L3-D4@lanes/L3-06,DR-3.2@lanes/L3-03,D-L3-04b@lanes/L3-01|-
REG-025|P2|Ph1|The blocking check-run name and required-context composition|L0|closed|L3-02-11,L3-02-12,L3-02-14,L1-04-08,L2-T404|DEC-L3-02-02@lanes/L3-02,DR-L3-01@lanes/L3-00,D-1@lanes/L1-04,D-L2-07@lanes/L2-02|-
REG-026|P2|Ph3|Reconciler identity write scope and the records-head anchor|L0|closed|L3-P5-06,L3-P5-07,L3-03-06,L3-03-10,L3-04-02|L3-D3@lanes/L3-06,DR-3.1@lanes/L3-03,D-L3-04-02@lanes/L3-04|-
REG-027|P2|Ph5|Which repair class is enabled first and in what order|L0|closed|L3-repair-all|DR-L3-02@lanes/L3-00|-
REG-028|P2|Ph3|The seeded canary content location and label|L0|closed|L3-01-20,L3-03-01|DR-L3-03@lanes/L3-00,D-L3-04a@lanes/L3-01|-
REG-029|P2|Ph3|The gap-window mark carrier|L0|closed|L3-gap-window|DR-L3-04@lanes/L3-00|-
REG-030|P2|Ph2|The scan toolchain security licence and SBOM|L0|open|L2-P1-T01,L2-P1-T05,L2-P1-T06|L2-P1-DEC-A@lanes/L2-01|-
REG-031|P2|Ph4|Per-product deploy and restore command fields on product.yaml|L0|open|L3-04-10|L2-P1-DEC-B@lanes/L2-01|-
REG-032|P2|Ph4|The filename of the rollback workflow|L0|closed|L2-T133,L2-T309,L2-T554,L2-T701|D-L2-05@lanes/L2-00|-
REG-033|P2|Ph2|The template placeholder syntax|L0|open|L2-T300,L2-T301|D-L2-08@lanes/L2-05|-
REG-034|P2|Ph4|The version observation transport|L0|closed|L2-T511|D-L2-09@lanes/L2-04|-
REG-035|P2|Ph4|The eleven-question field binding|L0|closed|L2-T504|D-L2-07@lanes/L2-04|-
REG-036|P2|Ph6|The record field carrying an S18 platform-rebuild identity|L0|closed|L4-deployment-schema|D-L2-09@lanes/L2-02|-
REG-037|P1|Ph6|Runtime evidence of privileged-runner tier|L0|open|L2-T172|D-L2-09@lanes/L2-03|-
REG-038|P2|Ph2|The sandbox organisation and fixture-repository slugs for X3|L0|open|L2-T603,L2-T221,L2-T607,L2-T608|D-L2-11@lanes/L2-06|-
REG-039|P2|Ph3|The five orphan-detection input surfaces|L0|closed|L3-05-10,L3-05-11,L3-05-12,L3-05-13,L3-05-14,L3-05-17,L3-05-18,L3-05-26,L3-05-27|DR-L3-05-A@lanes/L3-05,DR-L3-05-B@lanes/L3-05,DR-L3-05-C@lanes/L3-05,DR-L3-05-D@lanes/L3-05,DR-L3-05-E@lanes/L3-05|-
REG-040|P2|Ph2|product-template seed-data and migration-directory paths|L0|closed|L3-04-10|D-L3-04-03@lanes/L3-04|-
REG-041|P2|Ph3|The L3 test-harness contract and live-organisation authorisation|L0|open|L3-07-01,L3-07-10|DR-L3-07-A@lanes/L3-07,DR-L3-07-B@lanes/L3-07|-
REG-042|P2|Ph2|The per-product rota shape in people.yaml|L0|closed|L1-311|L1-D03@lanes/L1-05|-
REG-043|P2|Ph1|The eight L1 schema-shape rulings|L0|closed|L1-101,L1-107,L1-201,L1-02-09,L1-03-07,L1-03-11,L1-06-01|DECISION-L1-02-A@lanes/L1-02,DECISION-L1-02-C@lanes/L1-02,L1-D02@lanes/L1-05,control-classification-home@lanes/L1-03,records-snapshot-mode@lanes/L1-03,DR-L1-06-A@lanes/L1-06,DR-L1-06-C@lanes/L1-06|-
REG-044|P2|Ph1|The bootstrap write path and Gate 1 compensating control|L0|closed|L0-06-03,L1-108|DECISION-REQUIRED-1@lanes/L0-06,DECISION-REQUIRED-2@lanes/L0-06,DR-L0-07-B@lanes/L0-07|-
REG-045|P2|Ph1|How many cross-lane contract pairs exist|L0|open|L0-05-07,IG-03,IG-05|L0-IG-D1@lanes/L0-05|-
REG-046|P2|Ph1|How many context-holding humans hold Write during V1|L0|open|L0-06-03,L1-108,L0-00-01|V1-D6@master/06|-
REG-047|P2|Ph2|Which products are the pilots and are there two or three|L0|open|OT-P4,OT-P5,OT-P6,OT-P7,L0-07-02|V1-D4@master/06,DECISION-4@master/04|-
REG-048|P2|Ph1|The universal floor duration sequence tenth item and product identity|L0|open|L0-07-02,L0-07-04,L0-07-09|DECISION-3@master/04,DR-L0-07-C@lanes/L0-07,DR-L0-07-D@lanes/L0-07,DR-L0-07-G@lanes/L0-07|-
REG-049|P3|Ph6|Required-check status of digest-invariant-selftest|L0|closed|none|D-L2-08@lanes/L2-02|-
REG-050|P3|Ph2|Whether a local GitHub Actions runner is admitted|L0|closed|none|D-L2-13@lanes/L2-06|-
REG-051|P3|Ph2|The four L4 record vocabularies|L0|closed|none|D-L4-04@lanes/L4-02,D-L4-05@lanes/L4-02,D-L4-06@lanes/L4-02,D-L4-07@lanes/L4-02|-
REG-052|P3|P1|The four L4 derivation rulings|L0|closed|L4-T406,L4-T417|D-L4-P4-01@lanes/L4-04,D-L4-P4-02@lanes/L4-04,D-L4-P4-03@lanes/L4-04,D-L4-P7-03@lanes/L4-07|-
REG-053|P3|Ph2|Does D88 govern the section 97.2 decision-record comment|L0|closed|L4-P7-T07|D-L4-P7-01@lanes/L4-07|-
REG-054|P2|Ph2|SIG-43 is used twice and the denominator is 46 or 47|L0|closed|L4-P3-06,L4-P7-14|D-L4-P7-02@lanes/L4-07,D-L4-TL-4@lanes/L4-06,D-08-2@master/08,C-26@master/INDEX|-
REG-055|P3|Ph1|dot-github and root inside control-plane-records|L0|closed|L4-T003|D-L4-03@lanes/L4-00,C-10@master/INDEX|-
REG-056|P3|G3|Boards the Scorecard drop magnitude and the estimate exemption|L0|closed|none|D-L4-P5-02@lanes/L4-05,D-L4-P5-04@lanes/L4-05,D-L4-P5-05@lanes/L4-05|-
REG-057|P2|Ph1|Phase 0 and Phase 1 overlap on the records-repository skeleton|L0|closed|L4-T002,L4-T003|D-L4-TL-3@lanes/L4-06|-
REG-058|P2|Ph2|Is DevLake installed in V1|L0|closed|L5-ops-vm-compose|V1-D3@master/06|-
REG-059|P2|Ph2|Does the operational asset inventory ship a V1 sliver|L0|closed|L5-assets|V1-D5@master/06|-
REG-060|P2|Ph4|The seven design-open items of section 99.3|L0|open|none|L0D-10@lanes/L0-00,L0D-11@lanes/L0-00,L0D-12@lanes/L0-00,L0D-13@lanes/L0-00,L0D-14@lanes/L0-00,L0D-15@lanes/L0-00,L0D-16@lanes/L0-00,D-EE-4@master/05,DECISION-REQUIRED-3@master/09|-
REG-061|P0|Ph0|The contracts/gate freeze scope — gate tree excluded from main hash (B-01 correction)|L0|closed|L0-03-03,L0-03-06,L0-03-09,L0-02-09|B-01@lanes/L0-99-review.md|FD-029@Code/implementation/_FOUNDER_DECISIONS.md
EOF

git add docs/decisions/register.tsv
git commit -m "L0-04-01: the decision register, sixty-one rows (L0D-DR-1, L0D-DR-2; REG-061 added 2026-09-02)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 61 data rows | `grep -vc '^#' docs/decisions/register.tsv` | `61` |
| 2 | Every row has exactly 10 tab-separated fields | `awk -F'\t' '!/^#/ && NF!=10' docs/decisions/register.tsv \| wc -l` | `0` |
| 3 | No field is empty | `awk -F'\t' '!/^#/{for(i=1;i<=10;i++) if($i=="") print}' docs/decisions/register.tsv \| wc -l` | `0` |
| 4 | Ids are unique | `awk -F'\t' '!/^#/{print $1}' docs/decisions/register.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 5 | Ids are contiguous `REG-001`…`REG-060` | `awk -F'\t' '!/^#/{print $1}' docs/decisions/register.tsv \| sort > /tmp/have.txt; seq -f 'REG-%03g' 1 60 \| sort > /tmp/want.txt; diff /tmp/have.txt /tmp/want.txt \| wc -l` | `0` |
| 6 | Band counts are 2 / 13 / 38 / 7 | `awk -F'\t' '!/^#/{print $2}' docs/decisions/register.tsv \| sort \| uniq -c \| awk '{printf "%s=%s ", $2, $1}'; echo` | `P0=2 P1=13 P2=38 P3=7 ` |
| 7 | Every row is `open` at authoring time | `awk -F'\t' '!/^#/ && $6!="open"' docs/decisions/register.tsv \| wc -l` | `0` |
| 8 | Every decider is `L0` | `awk -F'\t' '!/^#/ && $5!="L0"' docs/decisions/register.tsv \| wc -l` | `0` |
| 9 | Every `record` field is `-` while open | `awk -F'\t' '!/^#/ && $6=="open" && $9!="-"' docs/decisions/register.tsv \| wc -l` | `0` |
| 10 | The two `P0` rows are `REG-001` and `REG-002` | `awk -F'\t' '$2=="P0"{printf "%s ", $1}' docs/decisions/register.tsv; echo` | `REG-001 REG-002 ` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
awk -F'\t' '!/^#/{print $1}' docs/decisions/register.tsv | sort > /tmp/have.txt
seq -f 'REG-%03g' 1 60 | sort > /tmp/want.txt
printf 'rows=%s fields=%s empty=%s dupes=%s contiguous=%s bands=%s open=%s p0=%s\n' \
  "$(grep -vc '^#' docs/decisions/register.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=10' docs/decisions/register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{for(i=1;i<=10;i++) if($i=="") print}' docs/decisions/register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $1}' docs/decisions/register.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(diff -q /tmp/have.txt /tmp/want.txt >/dev/null 2>&1 && echo YES || echo NO)" \
  "$(awk -F'\t' '!/^#/{c[$2]++} END{printf "%d/%d/%d/%d", c["P0"], c["P1"], c["P2"], c["P3"]}' docs/decisions/register.tsv)" \
  "$(awk -F'\t' '!/^#/ && $6=="open"' docs/decisions/register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$2=="P0"{printf "%s;", $1}' docs/decisions/register.tsv)"
```

Expected output, exactly:

```
rows=60 fields=0 empty=0 dupes=0 contiguous=YES bands=2/13/38/7 open=17 p0=REG-001;REG-002;
```

**STOP rule** — if `rows` is not `60`, the heredoc was truncated on paste; **do not add rows from memory and do not
renumber to close the gap** — re-paste the block whole. If `contiguous=NO`, an id is missing or duplicated and the
id space is no longer allocated-once (`L0D-DR-1`); every later citation of a `REG-` id would be ambiguous. If
`bands` is not `2/13/38/7`, a row's priority was altered, which changes what `make decisions-gate` blocks on. In
every case open `BLOCKER L0-04-01: register integrity` using `docs/escalation/BLOCKER.md`, with
`FORBIDDEN/UNDECIDED ID: L0D-DR-1` and `REGISTER ID: NONE`.

---

### L0-04-02 — `concordance.tsv`, generated and checked for uniqueness

**Size:** S · **Dependencies:** `L0-04-01`

The concordance is **derived** from `register.tsv` field 8, never authored, so a source id can never map to two
entries by transcription error. The `@` in each source token splits into the id and the file.

**Commands**

```bash
cd "$CP_ROOT"

printf '%s\n' \
'# concordance.tsv — GENERATED from register.tsv field 8 by L0-04-02. Do not hand-edit.' \
'# 3 tab-separated fields: source_id  raised_in_file  reg_id' \
> docs/decisions/concordance.tsv

awk -F'\t' '!/^#/ {
  n = split($8, s, ",")
  for (i = 1; i <= n; i++) {
    p = index(s[i], "@")
    if (p == 0) { print "MALFORMED " s[i] > "/dev/stderr"; continue }
    printf "%s\t%s\t%s\n", substr(s[i], 1, p-1), substr(s[i], p+1), $1
  }
}' docs/decisions/register.tsv | sort >> docs/decisions/concordance.tsv

git add docs/decisions/concordance.tsv
git commit -m "L0-04-02: concordance generated from the register"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | 188 source tokens mapped | `grep -vc '^#' docs/decisions/concordance.tsv` | `188` |
| 2 | Every row has 3 fields | `awk -F'\t' '!/^#/ && NF!=3' docs/decisions/concordance.tsv \| wc -l` | `0` |
| 3 | No `(source_id, file)` pair maps to two entries | `awk -F'\t' '!/^#/{print $1 "@" $2}' docs/decisions/concordance.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 4 | Every `reg_id` exists in the register | `awk -F'\t' '!/^#/{print $3}' docs/decisions/concordance.tsv \| sort -u \| while read r; do grep -q "^$r	" docs/decisions/register.tsv \|\| echo "MISSING $r"; done; echo DONE` | `DONE` alone |
| 5 | No source token was malformed | `awk -F'\t' '!/^#/{print $8}' docs/decisions/register.tsv \| tr ',' '\n' \| grep -cv '@'` | `0` |
| 6 | The colliding ids each appear more than once, disambiguated by file | `for i in D-L2-07 D-L2-08 D-L2-09 D-L4-01; do printf '%s=%s ' "$i" "$(awk -F'\t' -v x="$i" '$1==x' docs/decisions/concordance.tsv \| wc -l \| tr -d ' ')"; done; echo` | `D-L2-07=3 D-L2-08=4 D-L2-09=3 D-L4-01=2 ` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'tokens=%s fields=%s dupes=%s dangling=%s malformed=%s collisions=%s\n' \
  "$(grep -vc '^#' docs/decisions/concordance.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=3' docs/decisions/concordance.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $1 "@" $2}' docs/decisions/concordance.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $3}' docs/decisions/concordance.tsv | sort -u | while read -r r; do grep -q "^$r	" docs/decisions/register.tsv || echo x; done | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $8}' docs/decisions/register.tsv | tr ',' '\n' | grep -cv '@')" \
  "$(awk -F'\t' '!/^#/{c[$1]++} END{n=0; for(k in c) if(c[k]>1) n++; print n}' docs/decisions/concordance.tsv)"
```

Expected output, exactly:

```
tokens=188 fields=0 dupes=0 dangling=0 malformed=0 collisions=9
```

**STOP rule** — if `dupes` is not `0`, one `(source id, file)` pair maps to two entries, which means the same
sentence in the same file was filed as two decisions; **do not delete a row to make it unique** — the duplicate is
evidence that §3 merged two things that are not the same, or split one thing that is. If `collisions` is not `9`,
the nine colliding source ids catalogued in §5.2 are not all present, and a lane citing one of them cannot be
routed. If `dangling` is not `0`, `register.tsv` was edited after `L0-04-01`. Open
`BLOCKER L0-04-02: concordance integrity`, `REGISTER ID: NONE`.

---

### L0-04-03 — `reg-lint.sh`, the eight integrity checks

**Size:** M · **Dependencies:** `L0-04-02`

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/decisions/bin/reg-lint.sh <<'LINT'
#!/usr/bin/env sh
# reg-lint.sh — L0-owned. Integrity of the decision register.
# Usage: ./docs/decisions/bin/reg-lint.sh
# Last line is one of:
#   REG-LINT OK checks=8
#   REG-LINT FAIL <check-id>
# Exit 0 on pass, 1 on any failure. Fail-closed: a missing input is a FAIL, never a skip.
set -eu
D="$(dirname "$0")/.."
R="$D/register.tsv"; C="$D/concordance.tsv"
fail() { echo "REG-LINT FAIL $1"; exit 1; }

[ -f "$R" ] || fail L1-register-missing
[ -f "$C" ] || fail L3-concordance-missing

# L1 shape: 60 rows, 10 fields, no empty field
[ "$(grep -vc '^#' "$R")" = "60" ] || fail L1-row-count
[ "$(awk -F'\t' '!/^#/ && NF!=10' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L1-field-count
[ "$(awk -F'\t' '!/^#/{for(i=1;i<=10;i++) if($i=="") print}' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L1-empty-field

# L2 id space: unique and contiguous REG-001..REG-060 (L0D-DR-1).
# Runs BEFORE L3 because a broken id space also breaks the derived concordance,
# and the root cause must be the reported one.
awk -F'\t' '!/^#/{print $1}' "$R" | sort > /tmp/reg_have.txt
seq -f 'REG-%03g' 1 60 | sort > /tmp/reg_want.txt
diff -q /tmp/reg_have.txt /tmp/reg_want.txt >/dev/null 2>&1 || fail L2-id-space

# L3 concordance is a pure function of the register
awk -F'\t' '!/^#/{n=split($8,s,","); for(i=1;i<=n;i++){p=index(s[i],"@");
  printf "%s\t%s\t%s\n", substr(s[i],1,p-1), substr(s[i],p+1), $1}}' "$R" | sort > /tmp/reg_expect.tsv
grep -v '^#' "$C" | sort > /tmp/reg_actual.tsv
diff -q /tmp/reg_expect.tsv /tmp/reg_actual.tsv >/dev/null 2>&1 || fail L3-concordance-stale

# L4 vocabulary: priority, state, decider (L0D-DR-4, L0D-DR-5)
[ "$(awk -F'\t' '!/^#/ && $2 !~ /^P[0-3]$/' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L4-priority
[ "$(awk -F'\t' '!/^#/ && $6 !~ /^(open|closed|declined|withdrawn)$/' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L4-state
[ "$(awk -F'\t' '!/^#/ && $5!="L0"' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L4-decider

# L5 phase tokens are from the closed set
[ "$(awk -F'\t' '!/^#/ && $3 !~ /^(Ph[0-7]|EH|G[1-8]|P[1-8])$/' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L5-phase-token

# L6 record field agrees with state (L0D-DR-3)
[ "$(awk -F'\t' '!/^#/ && $6=="open" && $9!="-"' "$R" | wc -l | tr -d ' ')" = "0" ] || fail L6-open-has-record
MISSING=$(awk -F'\t' '!/^#/ && $6!="open" && $9!="-"{print $9}' "$R" \
  | while read -r f; do [ -f "$f" ] || echo x; done | wc -l | tr -d ' ')
[ "$MISSING" = "0" ] || fail L6-record-missing

# L7 no closure carries a fabricated record_schema_version (L0-DR-D2)
if [ -d "$D/closed" ]; then
  [ "$(grep -rl 'record_schema_version' "$D/closed" 2>/dev/null | wc -l | tr -d ' ')" = "0" ] || fail L7-fabricated-schema-version
fi

# L8 the rendered open/ files are exactly what the register renders
[ -x "$D/bin/reg-render.sh" ] || fail L8-renderer-missing
rm -rf /tmp/reg_render && mkdir -p /tmp/reg_render
"$D/bin/reg-render.sh" /tmp/reg_render >/dev/null
diff -rq "$D/open" /tmp/reg_render >/dev/null 2>&1 || fail L8-render-drift

echo "REG-LINT OK checks=8"
LINT
chmod +x docs/decisions/bin/reg-lint.sh

git add docs/decisions/bin/reg-lint.sh
git commit -m "L0-04-03: register integrity checks (L0D-DR-1, L0D-DR-2, L0D-DR-4)"
git push origin integration
```

`L8` fails until `L0-04-06` creates the renderer. That is correct and deliberate: a lint that passed while the
rendered copies did not exist would be asserting nothing about them.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The script exists and is executable | `test -x docs/decisions/bin/reg-lint.sh && echo EXEC` | `EXEC` |
| 2 | It fails closed on a missing renderer, naming the check | `docs/decisions/bin/reg-lint.sh; echo "rc=$?"` | `REG-LINT FAIL L8-renderer-missing` then `rc=1` |
| 3 | Every earlier check passed before `L8` was reached | `docs/decisions/bin/reg-lint.sh 2>&1 \| grep -c 'FAIL L[1-7]'` | `0` |
| 4 | It detects a stale concordance | `cp docs/decisions/concordance.tsv /tmp/c.bak; echo "X	Y	REG-001" >> docs/decisions/concordance.tsv; docs/decisions/bin/reg-lint.sh; cp /tmp/c.bak docs/decisions/concordance.tsv` | `REG-LINT FAIL L3-concordance-stale` |
| 5 | It detects a broken id space | `cp docs/decisions/register.tsv /tmp/r.bak; sed -i 's/^REG-060	/REG-061	/' docs/decisions/register.tsv; docs/decisions/bin/reg-lint.sh; cp /tmp/r.bak docs/decisions/register.tsv` | `REG-LINT FAIL L2-id-space` |
| 6 | It detects an invalid state | `cp docs/decisions/register.tsv /tmp/r.bak; awk -F'\t' 'BEGIN{OFS="\t"} NR==7{$6="probably"} {print}' /tmp/r.bak > docs/decisions/register.tsv; docs/decisions/bin/reg-lint.sh; cp /tmp/r.bak docs/decisions/register.tsv` | `REG-LINT FAIL L4-state` |
| 7 | The register is byte-identical after every negative test | `diff -q /tmp/r.bak docs/decisions/register.tsv && echo RESTORED` | `RESTORED` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
cp docs/decisions/register.tsv /tmp/r.bak
cp docs/decisions/concordance.tsv /tmp/c.bak
n1=$(docs/decisions/bin/reg-lint.sh 2>&1 | tail -1)
printf 'X\tY\tREG-001\n' >> docs/decisions/concordance.tsv
n2=$(docs/decisions/bin/reg-lint.sh 2>&1 | tail -1); cp /tmp/c.bak docs/decisions/concordance.tsv
sed 's/^REG-060\t/REG-061\t/' /tmp/r.bak > docs/decisions/register.tsv
n3=$(docs/decisions/bin/reg-lint.sh 2>&1 | tail -1); cp /tmp/r.bak docs/decisions/register.tsv
printf 'exec=%s base=%s stale=%s idspace=%s restored=%s\n' \
  "$(test -x docs/decisions/bin/reg-lint.sh && echo YES || echo NO)" \
  "$n1" "$n2" "$n3" \
  "$(diff -q /tmp/r.bak docs/decisions/register.tsv >/dev/null 2>&1 && echo YES || echo NO)"
```

Expected output, exactly:

```
exec=YES base=REG-LINT FAIL L8-renderer-missing stale=REG-LINT FAIL L3-concordance-stale idspace=REG-LINT FAIL L2-id-space restored=YES
```

**STOP rule** — if `base` is `REG-LINT OK checks=8` before `L0-04-06` has run, `L8` is not testing anything and
the lint is reporting a pass it did not earn. If either negative test prints `REG-LINT OK`, the check it targets is
inert — **do not proceed to `L0-04-04` and do not weaken a check to make a later task pass**; a register whose
integrity check does not fire is the silent-gate failure §99.6 risk 5 describes, applied to L0's own instrument.
If `restored=NO`, the negative tests mutated the register: restore from `/tmp/r.bak` and re-run before anything
else. Open `BLOCKER L0-04-03: reg-lint inert`, `REGISTER ID: NONE`.

---

### L0-04-04 — `reg-status.sh`, the queue by band and by gating phase

**Size:** M · **Dependencies:** `L0-04-03`

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/decisions/bin/reg-status.sh <<'STATUS'
#!/usr/bin/env sh
# reg-status.sh — L0-owned. The decision queue, ordered for the standing decision window.
# Usage: ./docs/decisions/bin/reg-status.sh [<phase-token>]
#   With no argument: the whole queue.
#   With a phase token: only entries gating at or before that phase, which is what
#   `make decisions-gate` asks before a promotion (L0D-DR-7).
# Last line: REG-STATUS open=<n> p0=<n> p1=<n> p2=<n> p3=<n> overdue=<n>
set -eu
D="$(dirname "$0")/.."
R="$D/register.tsv"
PH="${1:-}"
[ -f "$R" ] || { echo "REG-STATUS FAIL: register.tsv missing"; exit 2; }

# Phase ordinal. Foundation Ph0..Ph7 = 0..7, EH = 8, G1..G8 = 10..17, P1..P8 = 20..27.
ord() {
  case "$1" in
    Ph[0-7]) echo $(( $(printf '%s' "$1" | cut -c3-) )) ;;
    EH)      echo 8 ;;
    G[1-8])  echo $(( 9  + $(printf '%s' "$1" | cut -c2-) )) ;;
    P[1-8])  echo $(( 19 + $(printf '%s' "$1" | cut -c2-) )) ;;
    *)       echo 99 ;;
  esac
}

CUT=99
[ -n "$PH" ] && CUT="$(ord "$PH")"

echo "id       band gates state    title"
awk -F'\t' '!/^#/ && $6=="open"' "$R" | sort -t'	' -k2,2 -k3,3 | while IFS='	' read -r id band gates title decider state blocks sources record opened; do
  printf '%-8s %-4s %-5s %-8s %s\n' "$id" "$band" "$gates" "$state" "$title"
done

OPEN=$(awk -F'\t' '!/^#/ && $6=="open"' "$R" | wc -l | tr -d ' ')
P0=$(awk -F'\t' '!/^#/ && $6=="open" && $2=="P0"' "$R" | wc -l | tr -d ' ')
P1=$(awk -F'\t' '!/^#/ && $6=="open" && $2=="P1"' "$R" | wc -l | tr -d ' ')
P2=$(awk -F'\t' '!/^#/ && $6=="open" && $2=="P2"' "$R" | wc -l | tr -d ' ')
P3=$(awk -F'\t' '!/^#/ && $6=="open" && $2=="P3"' "$R" | wc -l | tr -d ' ')

OVERDUE=0
for g in $(awk -F'\t' '!/^#/ && $6=="open"{print $3}' "$R"); do
  [ "$(ord "$g")" -le "$CUT" ] && OVERDUE=$((OVERDUE+1))
done

echo "REG-STATUS open=$OPEN p0=$P0 p1=$P1 p2=$P2 p3=$P3 overdue=$OVERDUE"
STATUS
chmod +x docs/decisions/bin/reg-status.sh

git add docs/decisions/bin/reg-status.sh
git commit -m "L0-04-04: the decision queue report (L0D-DR-5)"
git push origin integration
```

`overdue` counts entries still `open` whose gating phase is **at or before** the phase argument. With no argument
the cut is `99`, so `overdue` equals `open` — that is intentional: with no phase asserted, every open entry is
overdue against *some* phase and the number is not a verdict. The verdict is `make decisions-gate` (`L0-04-07`),
which always passes a phase.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Executable | `test -x docs/decisions/bin/reg-status.sh && echo EXEC` | `EXEC` |
| 2 | Reports current open queue | `docs/decisions/bin/reg-status.sh \| tail -1` | `REG-STATUS open=17 p0=2 p1=13 p2=38 p3=7 overdue=17` |
| 3 | `Ph0` narrows the overdue count to the `Ph0`-gated entries | `docs/decisions/bin/reg-status.sh Ph0 \| tail -1 \| grep -o 'overdue=[0-9]*'` | `overdue=16` |
| 4 | The two `P0` rows print first under band ordering | `docs/decisions/bin/reg-status.sh \| sed -n '2,3p' \| cut -d' ' -f1 \| tr '\n' ' '` | `REG-001 REG-002 ` |
| 5 | It fails closed with no register | `mv docs/decisions/register.tsv /tmp/r2.bak; docs/decisions/bin/reg-status.sh; echo "rc=$?"; mv /tmp/r2.bak docs/decisions/register.tsv` | `REG-STATUS FAIL: register.tsv missing` then `rc=2` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'exec=%s all=[%s] ph0=%s first=%s\n' \
  "$(test -x docs/decisions/bin/reg-status.sh && echo YES || echo NO)" \
  "$(docs/decisions/bin/reg-status.sh | tail -1)" \
  "$(docs/decisions/bin/reg-status.sh Ph0 | tail -1 | grep -o 'overdue=[0-9]*')" \
  "$(docs/decisions/bin/reg-status.sh | sed -n '2p' | cut -d' ' -f1)"
```

Expected output, exactly:

```
exec=YES all=[REG-STATUS open=17 p0=2 p1=13 p2=38 p3=7 overdue=17] ph0=overdue=16 first=REG-001
```

**STOP rule** — if `ph0` is not `overdue=16`, either a gating phase token was altered in `register.tsv` or the
`ord()` ladder does not cover a token the register uses; **do not adjust the expected number to match the output**.
The sixteen `Ph0`-gated entries are the Phase-0 exit condition and are counted in three places in this file. If
`all` reports fewer than 17 open, an entry was closed without a decision record. Open
`BLOCKER L0-04-04: status arithmetic`, `REGISTER ID: NONE`.

---

### L0-04-05 — `reg-close.sh`, the closure procedure

**Size:** M · **Dependencies:** `L0-04-03`

Closure is the only operation that edits `register.tsv` after `L0-04-01`, and it is scripted so that the three
things a closure must do together — write the record, flip the state, point the row at the record — cannot happen
one without the others.

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/decisions/bin/reg-close.sh <<'CLOSE'
#!/usr/bin/env sh
# reg-close.sh — L0-owned. Close one register entry. L0 ONLY (L0D-DR-3).
# Usage: ./docs/decisions/bin/reg-close.sh <REG-nnn> <closed|declined|withdrawn> <subject-file>
#   <subject-file> is a plain-text file whose lines become options_considered and evidence.
# Last line: REG-CLOSE OK <REG-nnn> -> <state> <record-path>
set -eu
D="$(dirname "$0")/.."
R="$D/register.tsv"
ID="${1:?REG id required}"; STATE="${2:?state required}"; SUBJ="${3:?subject file required}"
TODAY="$(date -u +%F)"

case "$STATE" in closed|declined|withdrawn) ;; *) echo "REG-CLOSE FAIL: bad state $STATE"; exit 2 ;; esac
grep -q "^$ID	" "$R" || { echo "REG-CLOSE FAIL: $ID not in register"; exit 2; }
[ "$(awk -F'\t' -v i="$ID" '$1==i{print $6}' "$R")" = "open" ] || { echo "REG-CLOSE FAIL: $ID is not open"; exit 2; }
[ -f "$SUBJ" ] || { echo "REG-CLOSE FAIL: subject file $SUBJ missing"; exit 2; }

TITLE="$(awk -F'\t' -v i="$ID" '$1==i{print $4}' "$R")"
OPENED="$(awk -F'\t' -v i="$ID" '$1==i{print $10}' "$R")"
REC="docs/decisions/closed/$ID.yaml"

# The Section 97.2 decision-record field set, exactly. record_schema_version is
# deliberately absent until L0-DR-D2 is answered; pending_schema stands in its place.
{
  printf 'id: %s\n' "$ID"
  printf 'decider: founder\n'
  printf 'prompt_received: %s\n' "$OPENED"
  printf 'decided: %s\n' "$TODAY"
  printf 'subject: %s\n' "$TITLE"
  printf 'state: %s\n' "$STATE"
  printf 'options_considered:\n'
  sed -n 's/^option: /  - /p' "$SUBJ"
  printf 'evidence:\n'
  sed -n 's/^evidence: /  - /p' "$SUBJ"
  printf 'review_date: %s\n' "$(sed -n 's/^review_date: //p' "$SUBJ")"
  printf 'pending_schema: L0-DR-D2\n'
} > "$REC"

grep -c '^  - ' "$REC" >/dev/null
[ "$(sed -n 's/^review_date: //p' "$REC" | grep -c '^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$')" = "1" ] \
  || { rm -f "$REC"; echo "REG-CLOSE FAIL: review_date must be an ISO date (Section 97.2)"; exit 2; }
[ "$(sed -n '/^options_considered:/,/^evidence:/p' "$REC" | grep -c '^  - ')" -ge 2 ] \
  || { rm -f "$REC"; echo "REG-CLOSE FAIL: at least two options_considered are required"; exit 2; }

awk -F'\t' -v OFS='\t' -v i="$ID" -v st="$STATE" -v rec="$REC" \
  '$1==i{$6=st; $9=rec} {print}' "$R" > "$R.new" && mv "$R.new" "$R"

echo "REG-CLOSE OK $ID -> $STATE $REC"
CLOSE
chmod +x docs/decisions/bin/reg-close.sh

git add docs/decisions/bin/reg-close.sh
git commit -m "L0-04-05: the closure procedure (L0D-DR-3, L0D-DR-4, L0-DR-D2)"
git push origin integration
```

**Why `options_considered` is required to have at least two.** §97.2's decision record carries
`options_considered`, and a closure listing one option is not a decision — it is a description of what happened.
Every entry in §3 publishes an option set precisely so this check can be met from the register itself.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Executable | `test -x docs/decisions/bin/reg-close.sh && echo EXEC` | `EXEC` |
| 2 | It refuses an unknown id | `docs/decisions/bin/reg-close.sh REG-999 closed /dev/null; echo "rc=$?"` | `REG-CLOSE FAIL: REG-999 not in register` then `rc=2` |
| 3 | It refuses a bad state | `docs/decisions/bin/reg-close.sh REG-001 maybe /dev/null; echo "rc=$?"` | `REG-CLOSE FAIL: bad state maybe` then `rc=2` |
| 4 | It refuses a closure with fewer than two options | `printf 'option: A\nevidence: x\nreview_date: 2027-01-01\n' > /tmp/s1.txt; docs/decisions/bin/reg-close.sh REG-049 closed /tmp/s1.txt; echo "rc=$?"` | `REG-CLOSE FAIL: at least two options_considered are required` then `rc=2` |
| 5 | It refuses a closure with no ISO review date | `printf 'option: A\noption: B\nevidence: x\nreview_date: soon\n' > /tmp/s2.txt; docs/decisions/bin/reg-close.sh REG-049 closed /tmp/s2.txt; echo "rc=$?"` | `REG-CLOSE FAIL: review_date must be an ISO date (Section 97.2)` then `rc=2` |
| 6 | A refused closure leaves no record file behind | `test ! -f docs/decisions/closed/REG-049.yaml && echo CLEAN` | `CLEAN` |
| 7 | The register is unchanged after every refusal | `git diff --name-only docs/decisions/register.tsv \| wc -l` | `0` |
| 8 | No closure carries `record_schema_version` (`L0-DR-D2`) | `grep -rc 'record_schema_version' docs/decisions/closed/ 2>/dev/null \| wc -l` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'option: A\noption: B\nevidence: x\nreview_date: soon\n' > /tmp/s2.txt
printf 'option: A\nevidence: x\nreview_date: 2027-01-01\n'      > /tmp/s1.txt
printf 'exec=%s unknown=[%s] badstate=[%s] oneopt=[%s] baddate=[%s] clean=%s dirty=%s\n' \
  "$(test -x docs/decisions/bin/reg-close.sh && echo YES || echo NO)" \
  "$(docs/decisions/bin/reg-close.sh REG-999 closed /dev/null 2>&1 | tail -1)" \
  "$(docs/decisions/bin/reg-close.sh REG-001 maybe /dev/null 2>&1 | tail -1)" \
  "$(docs/decisions/bin/reg-close.sh REG-049 closed /tmp/s1.txt 2>&1 | tail -1)" \
  "$(docs/decisions/bin/reg-close.sh REG-049 closed /tmp/s2.txt 2>&1 | tail -1)" \
  "$(test ! -f docs/decisions/closed/REG-049.yaml && echo YES || echo NO)" \
  "$(git diff --name-only docs/decisions/register.tsv | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
exec=YES unknown=[REG-CLOSE FAIL: REG-999 not in register] badstate=[REG-CLOSE FAIL: bad state maybe] oneopt=[REG-CLOSE FAIL: at least two options_considered are required] baddate=[REG-CLOSE FAIL: review_date must be an ISO date (Section 97.2)] clean=YES dirty=0
```

**STOP rule** — if `dirty` is not `0`, a **refused** closure mutated the register: the state flip is happening
before the record is validated, and a row could then read `closed` with no record behind it, which is exactly the
condition `reg-lint.sh` check `L6` exists to catch and which `L0D-DR-3` forbids. Restore with
`git checkout -- docs/decisions/register.tsv` and do not proceed. If any of the four refusals prints
`REG-CLOSE OK`, the guard is inert. Open `BLOCKER L0-04-05: closure guard inert`, `REGISTER ID: NONE`.

---

### L0-04-06 — Render `open/`, the index, and add `REGISTER ID` to the blocker template

**Size:** M · **Dependencies:** `L0-04-03`

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/decisions/bin/reg-render.sh <<'RENDER'
#!/usr/bin/env sh
# reg-render.sh — L0-owned. Render one markdown file per OPEN entry.
# Usage: ./docs/decisions/bin/reg-render.sh [<output-dir>]   default: docs/decisions/open
# Idempotent by construction: the output is a pure function of register.tsv.
# Last line: REG-RENDER OK files=<n>
set -eu
D="$(dirname "$0")/.."
R="$D/register.tsv"
OUT="${1:-$D/open}"
[ -f "$R" ] || { echo "REG-RENDER FAIL: register.tsv missing"; exit 2; }
rm -f "$OUT"/REG-*.md 2>/dev/null || true
mkdir -p "$OUT"

awk -F'\t' '!/^#/ && $6=="open"' "$R" | while IFS='	' read -r id band gates title decider state blocks sources record opened; do
  {
    printf '# %s — %s\n\n' "$id" "$title"
    printf '| | |\n|---|---|\n'
    printf '| Priority | %s |\n' "$band"
    printf '| Gates | %s |\n' "$gates"
    printf '| Decided by | %s |\n' "$decider"
    printf '| State | %s |\n' "$state"
    printf '| Opened | %s |\n\n' "$opened"
    printf '**Blocks.** %s\n\n' "$(printf '%s' "$blocks" | tr ',' ' ')"
    printf '**Raised as.** %s\n\n' "$(printf '%s' "$sources" | tr ',' ' ')"
    printf '**Full statement, with the option set and the interim behaviour in force:**\n'
    printf 'implementation/lanes/L0-04-decisions-register.md, section 3, entry %s.\n\n' "$id"
    printf 'RENDERED FILE — do not edit. Edit docs/decisions/register.tsv (L0D-DR-2).\n'
  } > "$OUT/$id.md"
done

echo "REG-RENDER OK files=$(ls -1 "$OUT"/REG-*.md 2>/dev/null | wc -l | tr -d ' ')"
RENDER
chmod +x docs/decisions/bin/reg-render.sh
docs/decisions/bin/reg-render.sh

# The human index docs/README.md already names (L0-00-02).
{
  printf '# The L0 decision register — index\n\n'
  printf 'Source of truth: `docs/decisions/register.tsv` (L0D-DR-2). This index is RENDERED.\n'
  printf 'Full statements, option sets and interim behaviours: `implementation/lanes/L0-04-decisions-register.md` section 3.\n\n'
  printf '| id | band | gates | state | title |\n|---|---|---|---|---|\n'
  awk -F'\t' '!/^#/{printf "| %s | %s | %s | %s | %s |\n", $1, $2, $3, $6, $4}' docs/decisions/register.tsv
} >> docs/decisions/L0-decision-register.md

# Add the REGISTER ID line to the canonical blocker template (section 4.2).
grep -q '^REGISTER ID:' docs/escalation/BLOCKER.md || \
  sed -i 's|^FORBIDDEN/UNDECIDED ID:.*|&\nREGISTER ID:              <REG-nnn, or NONE>|' docs/escalation/BLOCKER.md

git add docs/decisions/bin/reg-render.sh docs/decisions/open docs/decisions/L0-decision-register.md docs/escalation/BLOCKER.md
git commit -m "L0-04-06: render the register, publish the index, extend the blocker template"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Sixty rendered files | `ls -1 docs/decisions/open/REG-*.md \| wc -l` | `60` |
| 2 | Rendering is idempotent | `rm -rf /tmp/rr && mkdir -p /tmp/rr && docs/decisions/bin/reg-render.sh /tmp/rr >/dev/null && diff -rq docs/decisions/open /tmp/rr && echo IDENTICAL` | `IDENTICAL` |
| 3 | Every rendered file carries the do-not-edit line | `grep -Lc 'RENDERED FILE' docs/decisions/open/REG-*.md \| wc -l` | `0` |
| 4 | The index lists all sixty | `grep -c '^| REG-' docs/decisions/L0-decision-register.md` | `60` |
| 5 | The index is at the path `docs/README.md` names | `grep -c 'decisions/L0-decision-register.md' docs/README.md` | `1` |
| 6 | The blocker template carries the register line, exactly once | `grep -c '^REGISTER ID:' docs/escalation/BLOCKER.md` | `1` |
| 7 | `reg-lint.sh` now passes all eight checks | `docs/decisions/bin/reg-lint.sh \| tail -1` | `REG-LINT OK checks=8` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
rm -rf /tmp/rr && mkdir -p /tmp/rr && docs/decisions/bin/reg-render.sh /tmp/rr >/dev/null
printf 'files=%s idempotent=%s marked=%s index=%s readme=%s blocker=%s lint=%s\n' \
  "$(ls -1 docs/decisions/open/REG-*.md | wc -l | tr -d ' ')" \
  "$(diff -rq docs/decisions/open /tmp/rr >/dev/null 2>&1 && echo YES || echo NO)" \
  "$(grep -L 'RENDERED FILE' docs/decisions/open/REG-*.md | wc -l | tr -d ' ')" \
  "$(grep -c '^| REG-' docs/decisions/L0-decision-register.md)" \
  "$(grep -c 'decisions/L0-decision-register.md' docs/README.md)" \
  "$(grep -c '^REGISTER ID:' docs/escalation/BLOCKER.md)" \
  "$(docs/decisions/bin/reg-lint.sh | tail -1)"
```

Expected output, exactly:

```
files=60 idempotent=YES marked=0 index=60 readme=1 blocker=1 lint=REG-LINT OK checks=8
```

**STOP rule** — if `idempotent=NO`, the renderer is not a pure function of `register.tsv` and there are now two
writable copies of one fact, which is the condition `L0D-DR-2` exists to prevent; **do not reconcile the two by
editing a file under `open/`** — fix the renderer. If `blocker` is `0`, the `sed` did not match, and every lane
blocker from this point carries no `REG-` id, so L0 cannot route a citation of `D-L2-08` to one of its four
meanings (§5.2); add the line by hand to `docs/escalation/BLOCKER.md` only — never to a lane's copy. If `lint` is
not `REG-LINT OK checks=8`, do not proceed to `L0-04-07`. Open `BLOCKER L0-04-06: render drift`,
`REGISTER ID: NONE`.

---

### L0-04-07 — `make decisions`, `make decisions-gate`, and the `promote-check` hook

**Size:** M · **Dependencies:** `L0-04-04`, `L0-04-06`

The register becomes a gate here, and only a **local** one. It is not a required status check and is not added to
branch protection (`L0D-DR-7`, `F-07`).

**Commands**

```bash
cd "$CP_ROOT"
cat >> Makefile <<'MK'

# --- L0-04: the decision register -------------------------------------------
# `decisions`      the queue, for the standing decision window (charter 8.2)
# `decisions-lint` integrity of the register itself
# `decisions-gate` PHASE=<token>: fails if any P0 or P1 entry gating at or
#                  before PHASE is still open. Local only (L0D-DR-7).
.PHONY: decisions decisions-lint decisions-gate

decisions:
	@docs/decisions/bin/reg-status.sh

decisions-lint:
	@docs/decisions/bin/reg-lint.sh

decisions-gate:
	@test -n "$(PHASE)" || { echo "DECISIONS-GATE FAIL: PHASE is required"; exit 2; }
	@docs/decisions/bin/reg-lint.sh >/dev/null || { echo "DECISIONS-GATE FAIL: register integrity"; exit 1; }
	@n=$$(docs/decisions/bin/reg-status.sh "$(PHASE)" | tail -1 | sed 's/.*overdue=//'); \
	 b=$$(awk -F'\t' '!/^#/ && $$6=="open" && ($$2=="P0" || $$2=="P1")' docs/decisions/register.tsv | wc -l | tr -d ' '); \
	 if [ "$$b" -gt 0 ]; then \
	   echo "DECISIONS-GATE FAIL: $$b P0/P1 entries still open at $(PHASE) (overdue=$$n)"; \
	   docs/decisions/bin/reg-status.sh "$(PHASE)" | awk '$$2=="P0" || $$2=="P1"'; \
	   exit 1; \
	 fi; \
	 echo "DECISIONS-GATE OK phase=$(PHASE) overdue=$$n blocking=0"
MK

# Wire it into promote-check. The register gate runs FIRST, because a promotion
# taken while a P0 decision is open is a promotion nobody decided to make.
python - <<'PY'
import re, pathlib
f = pathlib.Path('Makefile')
s = f.read_text()
# Insert decisions-gate as first indented command in promote-check recipe
s = re.sub(
    r'^(promote-check:\n)',
    r'\g<1>\t$(MAKE) decisions-gate\n',
    s,
    flags=re.MULTILINE
)
f.write_text(s)
PY
# Verify the insertion landed
sed -n '/^promote-check:/,/^$/p' Makefile | sed -n '2p'
# Expected output: a line containing decisions-gate

git add Makefile
git commit -m "L0-04-07: make decisions, decisions-lint, decisions-gate (L0D-DR-7)"
git push origin integration
```

Add one line to the existing `promote-check` recipe, at its top, so the register is checked before anything else:

```make
promote-check:
	@$(MAKE) decisions-gate PHASE=$$(cat contracts/gate/PHASE)
	@# ... every existing promote-check step follows, unchanged ...
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The three targets exist | `make -np 2>/dev/null \| grep -c '^\(decisions\|decisions-lint\|decisions-gate\):'` | `3` |
| 2 | `make decisions` prints the queue verdict | `make decisions \| tail -1` | `REG-STATUS open=17 p0=2 p1=13 p2=38 p3=7 overdue=17` |
| 3 | `make decisions-lint` passes | `make decisions-lint \| tail -1` | `REG-LINT OK checks=8` |
| 4 | `decisions-gate` refuses without `PHASE` | `make decisions-gate; echo "rc=$?"` | `DECISIONS-GATE FAIL: PHASE is required` then `rc=2` |
| 5 | `decisions-gate` FAILS at `Ph0` while the fourteen `P0`/`P1` entries are open | `make decisions-gate PHASE=Ph0 \| head -1` | `DECISIONS-GATE FAIL: 14 P0/P1 entries still open at Ph0 (overdue=16)` |
| 6 | `promote-check` invokes it first | `sed -n '/^promote-check:/,/^$/p' Makefile \| sed -n '2p'` | a line containing `decisions-gate` |
| 7 | No workflow file was created or edited | `git status --porcelain .github/ \| wc -l` | `0` |
| 8 | No required status check was added | `git diff --name-only \| grep -c 'access/'` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'targets=%s queue=[%s] lint=[%s] nophase=[%s] gate=[%s] hooked=%s workflows=%s\n' \
  "$(make -np 2>/dev/null | grep -c '^\(decisions\|decisions-lint\|decisions-gate\):')" \
  "$(make decisions 2>/dev/null | tail -1)" \
  "$(make decisions-lint 2>/dev/null | tail -1)" \
  "$(make decisions-gate 2>&1 | head -1)" \
  "$(make decisions-gate PHASE=Ph0 2>&1 | head -1)" \
  "$(sed -n '/^promote-check:/,/^$/p' Makefile | grep -c 'decisions-gate')" \
  "$(git status --porcelain .github/ | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
targets=3 queue=[REG-STATUS open=17 p0=2 p1=13 p2=38 p3=7 overdue=17] lint=[REG-LINT OK checks=8] nophase=[DECISIONS-GATE FAIL: PHASE is required] gate=[DECISIONS-GATE FAIL: 14 P0/P1 entries still open at Ph0 (overdue=16)] hooked=1 workflows=0
```

**STOP rule** — if `gate` prints `DECISIONS-GATE OK` while seventeen entries are open, the gate is inert and
`promote-check` would now pass a promotion taken with **REG-001** and **REG-002** unanswered; **do not proceed and
do not lower the gate to `P0` only to make a later promotion succeed.** If `workflows` is not `0`, this task wrote
into `.github/`, which is L2's exclusive path — revert immediately; that is `F-03` and it fails `lane-guard`. If
`hooked` is `0`, the `promote-check` edit was not applied and the gate exists but never runs, which is worse than
no gate because it reads as coverage. Open `BLOCKER L0-04-07: decisions-gate inert`, `REGISTER ID: NONE`.

---

### L0-04-08 — The standing decision window, and the first sweep

**Size:** S · **Dependencies:** `L0-04-07`

`L0-00-charter.md` §8.2 already schedules the window — *"Midweek, default Thursday · Standing decision window,
thirty minutes: every open L0D prompt actioned, deferred with a date, or explicitly declined"* (§94.6, **D79**).
This task gives it its input and its record.

**Commands**

```bash
cd "$CP_ROOT"
mkdir -p docs/cadence
cat > docs/cadence/decision-window.md <<'WIN'
# The standing decision window — thirty minutes, midweek, default Thursday

Anchors: MasterSpec v4.0 Section 94.6; decision D79; L0-00-charter.md Section 8.2.
Input:   make decisions
Rule:    every entry actioned, deferred with a date, or explicitly declined (Section 98.1).
         "Deferred" is not a state. A deferral is a review_date on a closure, or the entry stays open.

## The order of work, fixed

1. `make decisions-lint`            — if this is not OK, stop; the queue is not trustworthy.
2. `make decisions | head -20`      — P0 first, then P1, then by gating phase.
3. For each entry actioned:
     a. read the full statement:  implementation/lanes/L0-04-decisions-register.md section 3
     b. write the subject file:   docs/decisions/subjects/<REG-nnn>.txt
        one `option: ` line per option considered (at least two)
        one `evidence: ` line per piece of evidence
        one `review_date: YYYY-MM-DD` line
     c. `docs/decisions/bin/reg-close.sh <REG-nnn> <closed|declined|withdrawn> \
           docs/decisions/subjects/<REG-nnn>.txt`
     d. `docs/decisions/bin/reg-render.sh`
     e. `make decisions-lint`       — must print REG-LINT OK checks=8
4. One commit per window, message: `L0 decision window <YYYY-MM-DD>: closed <ids>`.

## What is never done here

- No entry is closed without at least two options_considered and an ISO review_date.
- No entry is marked closed to clear the queue. An entry with no answer stays open;
  an entry that will not be answered is `declined` and carries the Section 98.1 fields.
- No lane file is edited. A closure that changes what a lane must build is followed by an
  L0-issued reissue of that lane file, never by the lane adapting on its own.
WIN

mkdir -p docs/decisions/subjects
printf '%s\n' '# One subject file per closed entry. Input to reg-close.sh. L0-owned.' \
  > docs/decisions/subjects/README.md

git add docs/cadence/decision-window.md docs/decisions/subjects
git commit -m "L0-04-08: the standing decision window and its input store (D79)"
git push origin integration

# The first sweep: report the queue and prove the two P0 entries are the head of it.
make decisions | head -5
make decisions-gate PHASE=Ph0 || true
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The window procedure is published | `test -f docs/cadence/decision-window.md && echo PRESENT` | `PRESENT` |
| 2 | It cites §94.6 and D79 | `grep -c 'Section 94.6\|D79' docs/cadence/decision-window.md` | a number `>= 2` |
| 3 | The subject store exists | `test -d docs/decisions/subjects && echo PRESENT` | `PRESENT` |
| 4 | The queue's first two entries are the two `P0` rows | `make decisions 2>/dev/null \| sed -n '2,3p' \| cut -d' ' -f1 \| tr '\n' ' '` | `REG-001 REG-002 ` |
| 5 | Nothing was closed by this task | `awk -F'\t' '!/^#/ && $6!="open"' docs/decisions/register.tsv \| wc -l` | `0` |
| 6 | The docs index names the register | `grep -c 'L0-decision-register.md' docs/README.md` | `1` |
| 7 | Nothing outside `docs/**` and `Makefile` was touched by tasks T01–T08 | `git diff --name-only "$(git rev-parse HEAD~8)" HEAD \| grep -cv '^\(docs/\|Makefile$\)'` | `0` |

*(Criterion 4 checks both the first and second data rows; SELF-VERIFY's `head=` field checks only the first row as a quick smoke test — the two are complementary, not redundant.)*

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'window=%s cites=%s subjects=%s head=%s closed=%s foreign=%s\n' \
  "$(test -f docs/cadence/decision-window.md && echo PRESENT || echo MISSING)" \
  "$(grep -c 'Section 94.6\|D79' docs/cadence/decision-window.md)" \
  "$(test -d docs/decisions/subjects && echo PRESENT || echo MISSING)" \
  "$(make decisions 2>/dev/null | sed -n '2p' | cut -d' ' -f1)" \
  "$(awk -F'\t' '!/^#/ && $6!="open"' docs/decisions/register.tsv | wc -l | tr -d ' ')" \
  "$(git diff --name-only "$(git rev-parse HEAD~8)" HEAD | grep -cv '^\(docs/\|Makefile$\)')"
```

Expected output, exactly:

```
window=PRESENT cites=2 subjects=PRESENT head=REG-001 closed=0 foreign=0
```

**STOP rule** — if `foreign` is not `0`, one of tasks `T01`–`T08` wrote outside `docs/**` and `Makefile`, which are
the only paths this file is permitted to touch; identify the file with
`git diff --name-only "$(git rev-parse HEAD~8)" HEAD | grep -v '^\(docs/\|Makefile$\)'` and revert that hunk — do
not leave it and do not extend `lane-paths.tsv` to cover it, which is `L0D-04` and a separate decision. If `closed`
is not `0`, an entry was closed during setup, before any decision window ran; **a closure with no decision behind
it is worse than an open entry**, because the register then reports coverage it does not have. Revert it with
`git checkout -- docs/decisions/register.tsv docs/decisions/closed` and open
`BLOCKER L0-04-08: premature closure`, `REGISTER ID: NONE`.

---

## 10. The one command, and the one string that says the register is honest

**Commands**

```bash
cd "$CP_ROOT"
make decisions-lint && make decisions | tail -1
```

Two lines, and both must appear:

```
REG-LINT OK checks=8
REG-STATUS open=<n> p0=<n> p1=<n> p2=<n> p3=<n> overdue=<n>
```

`REG-LINT OK checks=8` is the only statement in this file that the register is internally consistent: sixty-one rows,
one id space, a concordance that is a pure function of the register, no closure without a record, no record without
a closure, and no rendered file that disagrees with the source. It says nothing whatever about whether the
decisions are **right** — that is what the sixty `records/decisions/` entries eventually say, one at a time.

`REG-STATUS … p0=0 p1=0` is the string that says Phase 0 can end.

---

## 11. What this file does not do

| # | Not done here | Where it is done |
|---|---|---|
| 1 | Deciding anything | The standing decision window (§94.6, D79); `docs/cadence/decision-window.md`; `L0-00-charter.md` §8.2 |
| 2 | Extending `lane-paths.tsv` or `CODEOWNERS` for any of the paths **REG-001** or **REG-017** name | `L0D-04`, `L0D-05`; `lanes/L0-02-lane-guard.md` §5, `L0-02-05` |
| 3 | Writing anything under `contracts/**` | The Phase 0 freeze; `lanes/L0-01-phase-0-contracts.md`; `L0D-06` |
| 4 | Writing a record into `records/decisions/` | The `record-decision` CLI (§97.2), an L4 deliverable; `L0-DR-D1` states the interim path |
| 5 | Adding any required status check | `F-07`; `L0D-DR-7`; the required-check list grows per phase, named by its phase (§98.2 Phase 1) |
| 6 | Renumbering any lane document's decision ids | `L0D-DR-1`; §5.2. The concordance disambiguates instead |
| 7 | Reissuing a lane file after a closure changes what it must build | L0, in the same window; §4.3 rule 5 and the decision-window procedure forbid a lane adapting on its own |
| 8 | Asserting the register in CI | Nothing does. `make decisions-gate` is local and runs inside `make promote-check`, which is the verdict of record (`lanes/L0-05-integration-gate.md` `L0D-IG-7`) |











