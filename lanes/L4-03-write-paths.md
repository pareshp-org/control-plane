# L4 — PHASE 3 — HOW RECORDS GET WRITTEN

**Lane:** L4 Records, Events & Metrics (subsystems I, N)
**Phase:** 3 — write paths
**Phase branch:** `lane/4/03-write-paths` (one branch for the phase, one commit per task, one PR at the end — the convention the lane charter established for `lane/4/00-charter-preflight`)
**Authority:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` is FROZEN and wins over this file. `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L4-00-charter.md` is the lane charter; its §3 owned-path list, §9 decisions and §12 standing rules bind every task here.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines). Every line number below was located with `grep`/`sed` and is cited, not inferred.

---

## 1. The one rule this phase implements

Master Spec §97.2, line 8871:

> **RECORD-VERIFICATION-RESULT** is the single pattern by which a human manual result reaches the machine: a `workflow_dispatch` with structured inputs — product, item, mechanism, pass or fail, evidence link — that writes the corresponding record and appends the event. Manual UAT and verification results (Section 31), restore-test confirmations (Section 44) and support-loop closures (Section 22) all reach their stores through this dispatch; **nobody edits a record file by hand to report a result.**

Phase 1 built the stores. Phase 2 built the shapes. **Phase 3 builds the doors.** After Phase 3 there is exactly one door per store, it is named in a machine-readable register, and a guard fails any pull request that walks past it.

Three further spec facts make this phase load-bearing:

| Fact | Spec anchor |
|---|---|
| Records are *generated from* the workflow surface; nobody transcribes | §97.1, line 8838 |
| The deployment-record and event writes are **required, failing steps** of `deploy-production.yml`, not trailing best-effort ones | §97.2, line 8867 |
| A record is never edited in place; corrections are follow-up records. Historical records are never silently overwritten (invariant 48) | §97.2, line 8890; §101.7, line 9516 |

---

## 2. Fixed workspace convention (binding for every task in this file)

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
```

Re-export these at the start of **every** task. The Bash tool resets the working directory between calls; always use absolute paths.

**Paths this phase writes — nothing else:**

| Repository | Path |
|---|---|
| `control-plane` | `tools/records/**` |
| `control-plane-records` | `CONTRIBUTING.md` |

`schemas/records/**` and `metrics/**` are L4-owned but are **not** written by Phase 3. `.github/workflows/**` in `control-plane` is L2's (PARTITION.md line 18) — Phase 3 publishes the *handler* and the *input contract*; L2 writes the workflow file that calls it. `control-plane-records/.github/` is untouched until charter decision **D-L4-03** resolves.

---

## 3. THE WRITE-PATH TABLE — normative

Every canonical record store of §97.2 (lines 8845–8866), the actor that writes it, and the path by which that actor writes it. This table is the human-readable face of `tools/records/write-paths.yaml`, built in task **L4-T302**. Where the two differ, the YAML file is authoritative and the difference is a blocker for L0.

| # | Store | Writer actor (spec wording) | Write path class | Second path | Hand-authored? | Spec line |
|---|---|---|---|---|---|---|
| 1 | `records/incidents/` | Incident workflow, from the incident issue template | `machine-workflow` | — | No | 8847 |
| 2 | `records/postmortems/` | Human, from template; closure tracked | `human-review-lane` | — | **Yes** | 8848 |
| 3 | `records/uat/` | CI job on UAT completion, from `verification/uat.md` execution | `machine-workflow` | `rvr-dispatch` (manual UAT, §31.2 line 2790) | No | 8849 |
| 4 | `records/estimates/` | Board automation at item close | `machine-board` | — | No | 8850 |
| 5 | `records/deployments/` | Deploy workflow | `machine-deploy` | — | No | 8851 |
| 6 | `records/restore-tests/` | The restore-test workflow, plus the human integrity confirmation through the RECORD-VERIFICATION-RESULT dispatch | `machine-workflow` | `rvr-dispatch` (§44.3 line 4008) | No | 8851 |
| 7 | `records/decisions/` | Human, at the moment of decision | `cli-record-decision` | `human-review-lane` | **Yes** | 8852 |
| 8 | `records/decisions/pending/` | The record-decision CLI when a decision prompt is opened | `cli-record-decision` | — | No | 8853 |
| 9 | `records/breaches/` | Security-incident workflow, when an incident is classified as a breach | `machine-workflow` | — | No | 8854 |
| 10 | `records/deletion-requests/` | Deletion runbook via the RECORD-VERIFICATION-RESULT dispatch | `rvr-dispatch` | — | No | 8855 |
| 11 | `records/security-reviews/` | Security reviewer, from template | `human-review-lane` | — | **Yes** | 8856 |
| 12 | `records/eval/` | The scheduled eval runner and pin-change CI | `machine-workflow` | — | No | 8857 |
| 13 | `records/launches/` | The launch-pack generator at launch-readiness sign-off | `machine-workflow` | — | No | 8858 |
| 14 | `records/demos/` | Human, brief, after each client demo or UAT walkthrough | `human-review-lane` | — | **Yes** | 8859 |
| 15 | `records/support/` | Support intake workflow | `machine-workflow` | `rvr-dispatch` (loop closure, §22.5 line 2256); `machine-workflow` again for the one-tap Founder log entry, §22.8 line 2286 | No | 8860 |
| 16 | `records/onboarding/` | Onboarding workflow at phase completion; human for judgment steps | `machine-workflow` | `human-review-lane` (judgment steps only) | **Yes**, judgment steps only | 8861 |
| 17 | `records/leave/` | Founder or delegate on approval | `human-review-lane` | — | **Yes** | 8862 |
| 18 | `events/` | Every workflow | `machine-workflow` | — | No | 8866 |

`exceptions.yaml`, `policies.yaml` and `patterns.yaml` also appear in the §97.2 table (lines 8863–8865). They live in the **control-plane** repository under `registries/**`, which PARTITION.md line 17 gives to **L1**. They are out of scope for this phase and appear in no L4 file.

### 3.1 The six write-path classes — closed set

| Class | Actor identity | Credential | Mechanism |
|---|---|---|---|
| `machine-workflow` | A control-plane or product GitHub Actions workflow | records-writer GitHub App installation token (§40.1, line 3667) | Calls `tools/records/lib/emit.sh` through a Phase-3 emitter or through the RVR handler |
| `machine-board` | Board automation on the designated work-management system | records-writer | Calls `tools/records/board-emit` or `tools/records/rqm-emit` |
| `machine-deploy` | `deploy-production.yml` / `deploy-staging.yml` | records-writer | Calls `tools/records/deploy-emit` as a **required, failing step** (§97.2, line 8867) |
| `rvr-dispatch` | A human, through `workflow_dispatch` with structured inputs | records-writer (the workflow's, not the human's) | Calls `tools/records/record-verification-result` |
| `cli-record-decision` | The record-decision CLI (§99.2 tool table, line 9217 — subsystems A, O; **not an L4 tool**) | records-writer | Calls `tools/records/record-write` / `event-append`, which delegate to `emit.sh` |
| `human-review-lane` | A named person | The person's own GitHub identity | A pull request on `control-plane-records`, subject to `tools/records/validate-human-record.sh` |

**Result-reporting stores.** Every store whose `hand_authored` flag is `No` is a **result-reporting store**: a hand-authored file appearing there in a pull request is rejected by the guard built in **L4-T314**. This is line 8871's last clause made mechanical.

---

## 4. Phase entry conditions

Task **L4-T301** proves every row. If any row fails, no other task in this phase starts.

| # | Condition | Why | Proof |
|---|---|---|---|
| E1 | `control-plane` and `control-plane-records` are git repositories with the Phase 1 skeleton (19 `.gitkeep` store markers) | Charter L4-T002 | `git -C "$CPR_ROOT" ls-files \| grep -c '/\.gitkeep$'` = `19` |
| E2 | `$CP_ROOT/contracts/registry/event-types.v1.yaml` exists | §97.3, line 8959 — no workflow ever writes an untyped event | `test -f` |
| E3 | `$CP_ROOT/schemas/records/` exists and holds at least `event.envelope.schema.json` | Charter DoD-2, DoD-3 | `test -f` |
| E4 | `python3` is on PATH and can `import yaml` | Every L4 validator reads YAML records | exit 0 |
| E5 | `$CP_ROOT/tools/records/lane-selfcheck.sh` exists and is executable | Charter L4-T005 | `test -x` |

If E2 or E3 fail, the phase that owns them has not merged. **Do not create them here.** Open the blocker in L4-T301.

---

## 5. DECISION REQUIRED — hand to L0

Three questions. **No L4 executor may answer them.** Each blocks only the task named; everything else in the phase proceeds. Charter decisions **D-L4-01**, **D-L4-02** and **D-L4-03** remain open and are not restated here.

### DECISION REQUIRED D-L4-P3-01 — the §18.4 sunset-runbook RVR rows name no target store

- **Fact:** §18.4, line 1798, routes manual sunset-runbook items through RECORD-VERIFICATION-RESULT. Rows 3, 5, 8, 9 and 10 (lines 1804, 1806, 1809, 1810, 1811) each say "RECORD-VERIFICATION-RESULT with … evidence" and name **no record store**. Row 6 (line 1807) is the only one that names one (`records/deletion-requests/`). `grep -n "records/" MultiProduct_MasterSpec_v4.0.md` over lines 1796–1822 returns exactly one store path.
- **Question:** Which store do sunset-runbook RVR results land in — an existing §97.2 store, or a new store requiring a §97.2 table amendment?
- **Blocks:** the sunset mechanisms only. The four armed mechanisms of L4-T304 are unaffected.
- **L4 default until answered:** `tools/records/dispatch/rvr-inputs.yaml` declares exactly four mechanisms. It declares **no** sunset mechanism and **no** placeholder store.
- **L4 must not:** invent a store directory, and must not route a sunset result into an existing store by resemblance.

### DECISION REQUIRED D-L4-P3-02 — "branch protection" on a repository that has none

- **Fact:** §97.1, line 8841: *"Human edits to records travel the normal review lane, as pull requests **under branch protection** like any other change."* §40.1, line 3667 (D89): the Records repository has *"**No protection rules** — the store is append-only by convention and by the write path, not by review."* PARTITION.md line 8 restates D107: no review protection; a no-bypass ruleset blocking force-push and deletion only.
- **Question:** For the `human-review-lane` stores (postmortems, decisions, security-reviews, demos, leave, onboarding judgment steps), what enforces the review that line 8841 requires, given that line 3667 forbids the branch protection line 8841 names? Options as stated in the spec, not invented: (a) a required status check that is not review protection; (b) review protection on `control-plane-records` overriding D107; (c) convention only, with `validate-human-record.sh` as the sole mechanical control.
- **Blocks:** the enforcement half of L4-T313 and L4-T314 only.
- **L4 default until answered:** `validate-human-record.sh` is built and is runnable as a status check. **L4 requests no branch protection and no ruleset change on `control-plane-records`** (charter §3 forbids it), and `CONTRIBUTING.md` records the open question verbatim for L0.

### DECISION REQUIRED D-L4-P3-03 — three write paths have no `event_type` identifier in the §97.3 taxonomy

> **Provenance note (D114-D / REG-021, 2026-09-02):** the decisions register (`lanes/L0-04-decisions-register.md` line 2290) now shows **REG-021 closed**, and all three identifiers — `support_loop_closure`, `deletion_request_recorded`, `work_item_closed` — exist in the corrected 89-identifier enum (`run-phase-0.sh` L0-P0-011; `tests/integration/test_event_type_enum.py`). This section, the `L4-T304` mechanism table below (the `support_loop_closure` and `deletion_provider_confirmation` rows, still `event_type: unarmed` / `armed: false`), and `L4-T307`'s `test-rvr.sh` negative fixture (`unarmed-mechanism ... support_loop_closure ... exit 3`) have **not** been re-armed for that closure. Doing so requires deciding the exact event_type mapping for each mechanism — `deletion_provider_confirmation` is not textually named `deletion_request_recorded` anywhere in this file, so that mapping needs stating, not assuming — and reworking the test harness's case count and record/event-count assertions accordingly. That is a design decision for whoever arms these mechanisms, not a mechanical edit, and has deliberately been left undone here.

- **Fact:** §97.3, line 8959: *"A new event type is a governed addition to the enum and to this taxonomy."* The tracked-events list (line 8963) contains `support item ingested` and `support first-touch breach` but **no** support-loop-closure entry; contains no deletion-request entry at all; and contains no work-item-closed entry, although §97.2 line 8850 writes `records/estimates/` "at item close". Verified by `sed -n '8963p' MultiProduct_MasterSpec_v4.0.md | grep -c "loop clos\|deletion\|item closed"` → `0`. **CAUTION:** `sed -n '8951p'` was the pre-D113 command; after D113 renumbering use `sed -n '8963p'` instead.
- **Question:** L0 to obtain the governed addition of the three identifiers, or to name the existing identifiers these three writes must reuse.
- **Blocks:** the `support_loop_closure` and `deletion_provider_confirmation` mechanisms of L4-T305, and the estimate-at-close emission of L4-T308.
- **L4 default until answered:** those rows carry `event_type: unarmed` in their contract file. The emitter **fails closed** with `EMIT FAIL unknown-event-type` rather than writing an untyped event (§97.3, line 8947). A record without its event is never written: `emit_pair` rolls the record back.
- **L4 must not:** invent an identifier, write to `registries/platform.yaml`, or fall back to free text.

---

## 6. Tasks

Sixteen tasks, L4-T301 through L4-T316. Each is mechanical. None requires designing, choosing or interpreting.

---

### L4-T301 — Phase-3 preflight and phase branch

**Size:** S
**Depends on:** none (phase entry)

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" checkout -B lane/4/03-write-paths origin/integration
git -C "$CP_ROOT" status --porcelain
git -C "$CPR_ROOT" fetch --all --prune
git -C "$CPR_ROOT" checkout -B lane/4/03-write-paths origin/main
echo "E1=$(git -C "$CPR_ROOT" ls-files | grep -c '/\.gitkeep$')"
test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo "E2=yes" || echo "E2=no"
test -f "$CP_ROOT/schemas/records/event.envelope.schema.json" && echo "E3=yes" || echo "E3=no"
python3 -c "import yaml; print('E4=yes')" 2>/dev/null || echo "E4=no"
test -x "$CP_ROOT/tools/records/lane-selfcheck.sh" && echo "E5=yes" || echo "E5=no"
mkdir -p "$CP_ROOT/tools/records/lib" "$CP_ROOT/tools/records/dispatch" "$CP_ROOT/tools/records/fixtures"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Phase branch created off `origin/integration` | `git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD` | `lane/4/03-write-paths` |
| 2 | Working tree clean before any write | `git -C "$CP_ROOT" status --porcelain \| wc -l` | `0` |
| 3 | Phase 1 store skeleton present | `git -C "$CPR_ROOT" ls-files \| grep -c '/\.gitkeep$'` | `19` |
| 4 | Event taxonomy present (E2) | `test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo YES` | `YES` |
| 5 | Event envelope schema present (E3) | `test -f "$CP_ROOT/schemas/records/event.envelope.schema.json" && echo YES` | `YES` |
| 6 | `python3` + PyYAML usable (E4) | `python3 -c "import yaml"; echo $?` | `0` |
| 7 | Three working directories created | `ls -d "$CP_ROOT"/tools/records/{lib,dispatch,fixtures} \| wc -l` | `3` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
echo "BRANCH=$(git -C "$CP_ROOT" rev-parse --abbrev-ref HEAD)"
echo "CPRBRANCH=$(git -C "$CPR_ROOT" rev-parse --abbrev-ref HEAD)"
echo "DIRTY=$(git -C "$CP_ROOT" status --porcelain | wc -l | tr -d ' ')"
echo "STORES=$(git -C "$CPR_ROOT" ls-files | grep -c '/\.gitkeep$')"
echo "TAXONOMY=$(test -f "$CP_ROOT/contracts/registry/event-types.v1.yaml" && echo yes || echo no)"
echo "ENVELOPE=$(test -f "$CP_ROOT/schemas/records/event.envelope.schema.json" && echo yes || echo no)"
echo "PYYAML=$(python3 -c 'import yaml' 2>/dev/null && echo yes || echo no)"
echo "DIRS=$(ls -d "$CP_ROOT"/tools/records/lib "$CP_ROOT"/tools/records/dispatch "$CP_ROOT"/tools/records/fixtures 2>/dev/null | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
BRANCH=lane/4/03-write-paths
CPRBRANCH=lane/4/03-write-paths
DIRTY=0
STORES=19
TAXONOMY=yes
ENVELOPE=yes
PYYAML=yes
DIRS=3
```

**STOP rule** — if any value differs from the expected block above: **do not create the missing artifact yourself.** `TAXONOMY=no` and `ENVELOPE=no` mean an earlier L4 phase has not merged to `integration`; creating them here duplicates another phase's authorship and will conflict at merge. `PYYAML=no` is a runner-image matter for L0. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T301 Phase 3 entry condition failed"
lane: L4
phase: 3
task_id: L4-T301
blocked_by: "<taxonomy absent | envelope schema absent | store skeleton incomplete | pyyaml absent | tree dirty>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "BRANCH=lane/4/03-write-paths / DIRTY=0 / STORES=19 / TAXONOMY=yes / ENVELOPE=yes / PYYAML=yes / DIRS=3"
spec_ref: "Master Spec v4.0 Section 97.3 line 8947; Section 97.2 lines 8843-8926; L4-00-charter.md section 7 DoD-1, DoD-3"
needs: "L0"
action_taken: "nothing created, nothing pushed"
```

---

### L4-T302 — The write-path register

**Size:** M
**Depends on:** L4-T301

Transcribe §3 of this file into `tools/records/write-paths.yaml`. Copy the block below **verbatim**. Do not add rows, do not omit rows, do not change a `spec_line`, do not rename a `schema`.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/write-paths.yaml" <<'WP_EOF'
# tools/records/write-paths.yaml
# The write-path register for lane L4, Phase 3.
# One row per canonical record store of Master Spec v4.0 Section 97.2 (lines 8845-8866).
# Section 97.2 line 8871, binding: nobody edits a record file by hand to report a result.
# id_prefix_source "spec" means the prefix is copied from the representative schema at the
# cited line. id_prefix_source "phase3" means Section 97.2 states no prefix for that store
# and this register declares one; the declaration is the authority, not an executor choice.
register_version: 1
write_path_classes: [machine-workflow, machine-board, machine-deploy, rvr-dispatch, cli-record-decision, human-review-lane]
stores:
  - store: incidents
    path: records/incidents/
    writer_actor: "Incident workflow, from the incident issue template"
    write_path: machine-workflow
    secondary_write_path: null
    hand_authored: false
    id_prefix: INC
    id_prefix_source: "spec line 8879"
    schema: incident.schema.json
    freshness_class: amber
    spec_line: 8847
  - store: postmortems
    path: records/postmortems/
    writer_actor: "Human, from template; closure tracked"
    write_path: human-review-lane
    secondary_write_path: null
    hand_authored: true
    id_prefix: PM
    id_prefix_source: phase3
    schema: postmortem.schema.json
    freshness_class: amber
    spec_line: 8848
  - store: uat
    path: records/uat/
    writer_actor: "CI job on UAT completion, from verification/uat.md execution"
    write_path: machine-workflow
    secondary_write_path: rvr-dispatch
    hand_authored: false
    id_prefix: UAT
    id_prefix_source: phase3
    schema: uat.schema.json
    freshness_class: blocking
    spec_line: 8849
  - store: estimates
    path: records/estimates/
    writer_actor: "Board automation at item close"
    write_path: machine-board
    secondary_write_path: null
    hand_authored: false
    id_prefix: EST
    id_prefix_source: phase3
    schema: estimate.schema.json
    freshness_class: amber
    spec_line: 8850
  - store: deployments
    path: records/deployments/
    writer_actor: "Deploy workflow"
    write_path: machine-deploy
    secondary_write_path: null
    hand_authored: false
    id_prefix: DEP
    id_prefix_source: "spec line 8895"
    schema: deployment.schema.json
    freshness_class: blocking
    spec_line: 8851
  - store: restore-tests
    path: records/restore-tests/
    writer_actor: "The restore-test workflow, plus the human integrity confirmation through the RECORD-VERIFICATION-RESULT dispatch"
    write_path: machine-workflow
    secondary_write_path: rvr-dispatch
    hand_authored: false
    id_prefix: RST
    id_prefix_source: phase3
    schema: restore-test.schema.json
    freshness_class: amber
    spec_line: 8851
  - store: decisions
    path: records/decisions/
    writer_actor: "Human, at the moment of decision"
    write_path: cli-record-decision
    secondary_write_path: human-review-lane
    hand_authored: true
    id_prefix: DEC
    id_prefix_source: "spec line 8907"
    schema: decision.schema.json
    freshness_class: amber
    spec_line: 8852
  - store: decisions/pending
    path: records/decisions/pending/
    writer_actor: "The record-decision CLI when a decision prompt is opened"
    write_path: cli-record-decision
    secondary_write_path: null
    hand_authored: false
    id_prefix: DECP
    id_prefix_source: phase3
    schema: decision-pending.schema.json
    freshness_class: amber
    spec_line: 8853
  - store: breaches
    path: records/breaches/
    writer_actor: "Security-incident workflow, when an incident is classified as a breach"
    write_path: machine-workflow
    secondary_write_path: null
    hand_authored: false
    id_prefix: BRC
    id_prefix_source: phase3
    schema: breach.schema.json
    freshness_class: amber
    spec_line: 8854
  - store: deletion-requests
    path: records/deletion-requests/
    writer_actor: "Deletion runbook via the RECORD-VERIFICATION-RESULT dispatch"
    write_path: rvr-dispatch
    secondary_write_path: null
    hand_authored: false
    id_prefix: DEL
    id_prefix_source: phase3
    schema: deletion-request.schema.json
    freshness_class: amber
    spec_line: 8855
  - store: security-reviews
    path: records/security-reviews/
    writer_actor: "Security reviewer, from template"
    write_path: human-review-lane
    secondary_write_path: null
    hand_authored: true
    id_prefix: SEC
    id_prefix_source: phase3
    schema: security-review.schema.json
    freshness_class: amber
    spec_line: 8856
  - store: eval
    path: records/eval/
    writer_actor: "The scheduled eval runner and pin-change CI"
    write_path: machine-workflow
    secondary_write_path: null
    hand_authored: false
    id_prefix: EVAL
    id_prefix_source: phase3
    schema: eval.schema.json
    freshness_class: amber
    spec_line: 8857
  - store: launches
    path: records/launches/
    writer_actor: "The launch-pack generator at launch-readiness sign-off"
    write_path: machine-workflow
    secondary_write_path: null
    hand_authored: false
    id_prefix: LAU
    id_prefix_source: phase3
    schema: launch.schema.json
    freshness_class: amber
    spec_line: 8858
  - store: demos
    path: records/demos/
    writer_actor: "Human, brief, after each client demo or UAT walkthrough"
    write_path: human-review-lane
    secondary_write_path: null
    hand_authored: true
    id_prefix: DEMO
    id_prefix_source: "spec line 8919"
    schema: demo.schema.json
    freshness_class: amber
    spec_line: 8859
  - store: support
    path: records/support/
    writer_actor: "Support intake workflow; the one-tap Founder log entry (section 22.8 line 2286) uses the same path"
    write_path: machine-workflow
    secondary_write_path: rvr-dispatch
    hand_authored: false
    id_prefix: SUP
    id_prefix_source: phase3
    schema: support.schema.json
    freshness_class: amber
    spec_line: 8860
  - store: onboarding
    path: records/onboarding/
    writer_actor: "Onboarding workflow at phase completion; human for judgment steps"
    write_path: machine-workflow
    secondary_write_path: human-review-lane
    hand_authored: true
    id_prefix: ONB
    id_prefix_source: phase3
    schema: onboarding.schema.json
    freshness_class: amber
    spec_line: 8861
  - store: leave
    path: records/leave/
    writer_actor: "Founder or delegate on approval"
    write_path: human-review-lane
    secondary_write_path: null
    hand_authored: true
    id_prefix: LV
    id_prefix_source: phase3
    schema: leave.schema.json
    freshness_class: amber
    spec_line: 8862
  - store: events
    path: events/
    writer_actor: "Every workflow"
    write_path: machine-workflow
    secondary_write_path: null
    hand_authored: false
    id_prefix: EVT
    id_prefix_source: "spec line 8938"
    schema: event.envelope.schema.json
    freshness_class: blocking
    spec_line: 8866
WP_EOF
git -C "$CP_ROOT" add tools/records/write-paths.yaml
git -C "$CP_ROOT" commit -m "L4-T302: write-path register - one declared writer and path per Section 97.2 store"
python3 -c "import yaml,sys; d=yaml.safe_load(open(r'$CP_ROOT/tools/records/write-paths.yaml')); print('ROWS=%d' % len(d['stores']))"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly 19 store rows | `python3 -c "import yaml;print(len(yaml.safe_load(open(r'$CP_ROOT/tools/records/write-paths.yaml'))['stores']))"` | `19` | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | Every `write_path` is in the closed class list | see SELF-VERIFY `BADCLASS` | `0` |
| 3 | Exactly 3 stores are `freshness_class: blocking` (§53.1 line 4671) | see SELF-VERIFY `BLOCKING` | `3` |
| 4 | Exactly 6 stores are `hand_authored: true` | see SELF-VERIFY `HANDAUTH` | `6` |
| 5 | Every declared `store` directory exists in the records repository | see SELF-VERIFY `MISSINGDIR` | `0` |
| 6 | Every `spec_line` lies inside §97.2's table (8845–8866) | see SELF-VERIFY `BADLINE` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
python3 - <<'PY'
import os, yaml
cp, cpr = os.environ["CP_ROOT"], os.environ["CPR_ROOT"]
d = yaml.safe_load(open(os.path.join(cp, "tools", "records", "write-paths.yaml")))
s, classes = d["stores"], set(d["write_path_classes"])
print("ROWS=%d" % len(s))
print("BADCLASS=%d" % sum(1 for r in s if r["write_path"] not in classes
                          or (r["secondary_write_path"] and r["secondary_write_path"] not in classes)))
print("BLOCKING=%d" % sum(1 for r in s if r["freshness_class"] == "blocking"))
print("HANDAUTH=%d" % sum(1 for r in s if r["hand_authored"]))
print("MISSINGDIR=%d" % sum(1 for r in s if not os.path.isdir(os.path.join(cpr, r["path"].rstrip("/")))))
print("BADLINE=%d" % sum(1 for r in s if not 8845 <= r["spec_line"] <= 8866))
PY
```

Expected output, exactly:

```
ROWS=19
BADCLASS=0
BLOCKING=3
HANDAUTH=6
MISSINGDIR=0
BADLINE=0
```

**STOP rule** — if `ROWS` is not `19`, or any other value is not as shown: the register does not match §3 of this file. **Do not edit a `spec_line`, a `store` name or a `freshness_class` to make it pass.** `MISSINGDIR` above `0` means the Phase 1 skeleton and this register disagree about a directory name — that is a real defect, not a typo to smooth over. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T302 write-path register does not match Section 97.2"
lane: L4
phase: 3
task_id: L4-T302
blocked_by: "<row count | class enum | freshness count | hand-authored count | missing store directory | spec line out of range>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "ROWS=19 / BADCLASS=0 / BLOCKING=3 / HANDAUTH=6 / MISSINGDIR=0 / BADLINE=0" # 19 per FD-059 (bootstrap/ counts as a store)
spec_ref: "Master Spec v4.0 Section 97.2 lines 8845-8866; Section 53.1 line 4671"
needs: "L0"
action_taken: "register committed unmodified; no row altered"
```

---

### L4-T303 — Write-path register validator, with its negative test

**Size:** M
**Depends on:** L4-T302

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
[ -n "$CPR_ROOT" ] || { echo "ERROR: CPR_ROOT is not set"; exit 1; }
cat > "$CP_ROOT/tools/records/validate-write-paths.sh" <<'VWP_EOF'
#!/usr/bin/env bash
# tools/records/validate-write-paths.sh
# Validates tools/records/write-paths.yaml against the records repository and schemas.
# Master Spec v4.0 Section 97.2 lines 8845-8871; Section 53.1 line 4671.
# Usage: validate-write-paths.sh [--schemas]
set -u
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
MODE="${1:---all}"
python3 - "$MODE" <<'PY'
import os, sys, yaml
mode = sys.argv[1]
cp, cpr = os.environ["CP_ROOT"], os.environ["CPR_ROOT"]
reg = yaml.safe_load(open(os.path.join(cp, "tools", "records", "write-paths.yaml")))
stores, classes = reg["stores"], set(reg["write_path_classes"])
errs = []
seen = set()
for r in stores:
    n = r["store"]
    if n in seen: errs.append("duplicate-store %s" % n)
    seen.add(n)
    if r["write_path"] not in classes: errs.append("bad-class %s %s" % (n, r["write_path"]))
    sec = r["secondary_write_path"]
    if sec and sec not in classes: errs.append("bad-secondary-class %s %s" % (n, sec))
    if not os.path.isdir(os.path.join(cpr, r["path"].rstrip("/"))): errs.append("missing-store-dir %s" % n)
    if r["freshness_class"] not in ("amber", "blocking"): errs.append("bad-freshness %s" % n)
    if r["hand_authored"] and r["write_path"] not in ("human-review-lane", "cli-record-decision") \
       and r["secondary_write_path"] != "human-review-lane":
        errs.append("hand-authored-without-human-lane %s" % n)
    if not r["hand_authored"] and "human-review-lane" in (r["write_path"], r["secondary_write_path"]):
        errs.append("result-store-with-human-lane %s" % n)
blocking = sorted(r["store"] for r in stores if r["freshness_class"] == "blocking")
if blocking != ["deployments", "events", "uat"]:
    errs.append("blocking-set %s expected ['deployments','events','uat']" % blocking)
if len(stores) != 19: errs.append("row-count %d expected 19" % len(stores))  # 19 per FD-059 (bootstrap/ counts as a store)
if mode == "--schemas":
    for r in stores:
        p = os.path.join(cp, "schemas", "records", r["schema"])
        if not os.path.exists(p): errs.append("schema-absent %s %s" % (r["store"], r["schema"]))
    if errs:
        for e in errs: print("SCHEMAS FAIL " + e)
        sys.exit(1)
    print("SCHEMAS PRESENT %d/19" % len(stores)); sys.exit(0)
if errs:
    for e in errs: print("WRITE-PATHS FAIL " + e)
    sys.exit(1)
print("WRITE-PATHS OK 19/19")  # 19 per FD-059 (bootstrap/ counts as a store)
PY
VWP_EOF
chmod +x "$CP_ROOT/tools/records/validate-write-paths.sh"
git -C "$CP_ROOT" add tools/records/validate-write-paths.sh
git -C "$CP_ROOT" commit -m "L4-T303: write-path register validator with negative test"
"$CP_ROOT/tools/records/validate-write-paths.sh"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x "$CP_ROOT/tools/records/validate-write-paths.sh" && echo YES` | `YES` |
| 2 | Passes on the committed register | `"$CP_ROOT/tools/records/validate-write-paths.sh"` | `WRITE-PATHS OK 19/19`, exit 0 | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 3 | Fails on a seeded bad class (§53.1 seeded-canary rule, line 4685) | see SELF-VERIFY `NEG1` | starts `WRITE-PATHS FAIL bad-class`, exit 1 |
| 4 | Fails when a result store is given the human lane | see SELF-VERIFY `NEG2` | starts `WRITE-PATHS FAIL result-store-with-human-lane`, exit 1 |
| 5 | The register is byte-identical after both negative tests | see SELF-VERIFY `RESTORED` | `restored` |

**SELF-VERIFY** (includes the two mandatory negative tests — charter §12 rule 10)

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
V="$CP_ROOT/tools/records/validate-write-paths.sh"
W="$CP_ROOT/tools/records/write-paths.yaml"
BEFORE="$(git -C "$CP_ROOT" hash-object "$W")"
echo "POSITIVE=$("$V" | head -1)"
sed -i 's/    write_path: machine-workflow$/    write_path: carrier-pigeon/' "$W"
echo "NEG1=$("$V" | head -1)"
git -C "$CP_ROOT" checkout -- tools/records/write-paths.yaml
sed -i '0,/^    write_path: machine-deploy$/s//    write_path: human-review-lane/' "$W"
echo "NEG2=$("$V" | grep -m1 result-store-with-human-lane)"
git -C "$CP_ROOT" checkout -- tools/records/write-paths.yaml
AFTER="$(git -C "$CP_ROOT" hash-object "$W")"
echo "RESTORED=$([ "$BEFORE" = "$AFTER" ] && echo restored || echo CORRUPT)"
```

Expected output, exactly:

```
POSITIVE=WRITE-PATHS OK 19/19
NEG1=WRITE-PATHS FAIL bad-class incidents carrier-pigeon
NEG2=WRITE-PATHS FAIL result-store-with-human-lane deployments
RESTORED=restored
```

**STOP rule** — if `NEG1` or `NEG2` does not begin `WRITE-PATHS FAIL`, the validator cannot detect a violation and is worthless (charter §12 rule 10). If `RESTORED=CORRUPT`, the register has been damaged: run `git -C "$CP_ROOT" checkout -- tools/records/write-paths.yaml` once more and re-check. Do not push in either case. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T303 write-path validator negative test did not fail"
lane: L4
phase: 3
task_id: L4-T303
blocked_by: "<negative test passed when it must fail | register left corrupt>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "POSITIVE=WRITE-PATHS OK 19/19 / NEG1 and NEG2 both begin WRITE-PATHS FAIL / RESTORED=restored" # 19 per FD-059 (bootstrap/ counts as a store)
spec_ref: "Master Spec v4.0 Section 53.1 line 4685; L4-00-charter.md section 12 rule 10"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T304 — The RECORD-VERIFICATION-RESULT input contract

**Size:** M
**Depends on:** L4-T302
**Partially blocked by:** D-L4-P3-01 (sunset mechanisms) and D-L4-P3-03 (two `event_type` identifiers). Write the file below exactly as given; both defaults are already encoded in it.

This file is the contract **L2 transcribes into the `workflow_dispatch` `inputs:` block** of the workflow it owns. Phase 3 declares the inputs; L2 declares the workflow. The five inputs are §97.2 line 8871 verbatim: product, item, mechanism, pass or fail, evidence link.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/dispatch/rvr-inputs.yaml" <<'RVR_EOF'
# tools/records/dispatch/rvr-inputs.yaml
# The structured input set of RECORD-VERIFICATION-RESULT.
# Master Spec v4.0 Section 97.2 line 8871; Section 18.4 line 1798.
# L2 transcribes `inputs` into the workflow_dispatch inputs block of the workflow it owns
# under .github/workflows/ (PARTITION.md line 18). L4 owns this contract and the handler
# tools/records/record-verification-result that the workflow calls.
contract_version: 1
inputs:
  - name: product
    required: true
    description: "Product identity key from the L1 product registry."
  - name: item
    required: true
    description: "The thing verified: a work-item reference, a runbook row, a support record id, or a restore-test run id."
  - name: mechanism
    required: true
    type: choice
    description: "One of the mechanisms below. Free text is rejected."
  - name: result
    required: true
    type: choice
    choices: [pass, fail]
    description: "Section 97.2 line 8871: pass or fail."
  - name: evidence_link
    required: true
    description: "A URL. The handler rejects an empty or non-URL value."
mechanisms:
  - mechanism: manual_verification
    target_store: uat
    schema: uat.schema.json
    event_type: uat_executed
    armed: true
    spec_ref: "Section 31.2 line 2790; Section 97.2 line 8871; event in the Section 97.3 tracked list line 8951 as 'UAT executed with result'"
  - mechanism: restore_test_confirmation
    target_store: restore-tests
    schema: restore-test.schema.json
    event_type: restore_test_executed
    armed: true
    spec_ref: "Section 44.3 line 4008; Section 97.2 line 8851; event in the Section 97.3 tracked list line 8951 as 'restore test executed with result'"
  - mechanism: support_loop_closure
    target_store: support
    schema: support.schema.json
    event_type: unarmed
    armed: false
    spec_ref: "Section 22.5 line 2256; Section 97.2 line 8871. BLOCKED by D-L4-P3-03: the Section 97.3 tracked-events list (line 8951) contains no support-loop-closure identifier."
  - mechanism: deletion_provider_confirmation
    target_store: deletion-requests
    schema: deletion-request.schema.json
    event_type: unarmed
    armed: false
    spec_ref: "Section 97.2 line 8855; Section 18.4 line 1807; AT-105 line 9375. BLOCKED by D-L4-P3-03: the Section 97.3 tracked-events list (line 8951) contains no deletion identifier."
# NO sunset-runbook mechanism is declared. Section 18.4 rows 3, 5, 8, 9 and 10
# (lines 1804, 1806, 1809, 1810, 1811) route through this dispatch and name no target
# store. See DECISION REQUIRED D-L4-P3-01 in L4-03-write-paths.md. Do not invent a store.
RVR_EOF
git -C "$CP_ROOT" add tools/records/dispatch/rvr-inputs.yaml
git -C "$CP_ROOT" commit -m "L4-T304: RECORD-VERIFICATION-RESULT structured input contract (Section 97.2 line 8871)"
python3 -c "import yaml;d=yaml.safe_load(open(r'$CP_ROOT/tools/records/dispatch/rvr-inputs.yaml'));print('INPUTS=%d MECH=%d ARMED=%d'%(len(d['inputs']),len(d['mechanisms']),sum(1 for m in d['mechanisms'] if m['armed'])))"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Exactly the five inputs of line 8871 | see SELF-VERIFY `INPUTS` | `5` |
| 2 | Input names are exactly `product,item,mechanism,result,evidence_link` | see SELF-VERIFY `NAMES` | `product,item,mechanism,result,evidence_link` |
| 3 | Exactly four mechanisms declared | see SELF-VERIFY `MECH` | `4` |
| 4 | Exactly two mechanisms armed (D-L4-P3-03 holds the other two closed) | see SELF-VERIFY `ARMED` | `2` |
| 5 | Every `target_store` is a store in the register | see SELF-VERIFY `BADSTORE` | `0` |
| 6 | No sunset mechanism was invented | `grep -ci "sunset\|decommission\|archived" "$CP_ROOT/tools/records/dispatch/rvr-inputs.yaml"` | `1` (the closing comment only) |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, yaml
cp = os.environ["CP_ROOT"]
d = yaml.safe_load(open(os.path.join(cp, "tools", "records", "dispatch", "rvr-inputs.yaml")))
reg = yaml.safe_load(open(os.path.join(cp, "tools", "records", "write-paths.yaml")))
known = {r["store"] for r in reg["stores"]}
print("INPUTS=%d" % len(d["inputs"]))
print("NAMES=%s" % ",".join(i["name"] for i in d["inputs"]))
print("MECH=%d" % len(d["mechanisms"]))
print("ARMED=%d" % sum(1 for m in d["mechanisms"] if m["armed"]))
print("BADSTORE=%d" % sum(1 for m in d["mechanisms"] if m["target_store"] not in known))
PY
```

Expected output, exactly:

```
INPUTS=5
NAMES=product,item,mechanism,result,evidence_link
MECH=4
ARMED=2
BADSTORE=0
```

**STOP rule** — if `ARMED` is not `2`: someone has armed a mechanism whose `event_type` does not exist in the §97.3 taxonomy. **Revert it.** §97.3 line 8947 requires a governed addition to the enum before an identifier may be emitted; arming it here writes an untyped event, which control-plane CI rejects. If `BADSTORE` is not `0`, a mechanism targets a store the register does not know. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T304 RVR mechanism armed or targeted without authority"
lane: L4
phase: 3
task_id: L4-T304
blocked_by: "<mechanism armed without a taxonomy identifier | unknown target store | sunset mechanism invented>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "INPUTS=5 / NAMES=product,item,mechanism,result,evidence_link / MECH=4 / ARMED=2 / BADSTORE=0"
spec_ref: "Master Spec v4.0 Section 97.2 line 8871; Section 97.3 lines 8947, 8951; Section 18.4 line 1798"
needs: "L0 - decisions D-L4-P3-01 and D-L4-P3-03"
action_taken: "no store invented, no identifier invented"
```

---

### L4-T305 — The emission library `tools/records/lib/emit.sh`

**Size:** L
**Depends on:** L4-T301

This is the **only** code in the estate that writes a record file or an event file. Every emitter in this phase calls it. It enforces four spec rules mechanically: UTC-with-offset timestamps (§97.1, line 8839), the record envelope (§97.2, line 8890), the closed `event_type` enum (§97.3, line 8947), and no silent overwrite (invariant 48, line 9516). It writes the record and its event as **one commit**, and rolls the record back if the event cannot be written — §97.2 line 8871's "writes the corresponding record **and** appends the event" is a pair, never a half.

The final block is **guarded**: if `record-write` / `event-append` already exist (delivered by another L4 phase), it verifies they delegate here and creates nothing. If they do not exist, it creates them as thin front-ends. Do not remove the guard.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/lib/validate_instance.py" <<'VI_EOF'
#!/usr/bin/env python3
"""tools/records/lib/validate_instance.py
Write-time instance check. Master Spec v4.0 Section 97.1 line 8839 (UTC with offset),
Section 97.2 line 8890 (record envelope), Section 97.3 lines 8933-8945 (event envelope).
Usage: validate_instance.py <record|event> <schema-path-or-dash> <instance-file>
Full JSON Schema validation is the schema phase's job; this is the write-time gate."""
import json, os, re, sys
import yaml

KIND, SCHEMA, PATH = sys.argv[1], sys.argv[2], sys.argv[3]
RECORD_ENVELOPE = ["record_schema_version", "id", "product", "timestamp"]
EVENT_ENVELOPE = ["event_schema_version", "event_id", "event_type", "occurred_at",
                  "recorded_at", "actor", "product", "subject_ref", "payload"]
TS = re.compile(r"^\s*[A-Za-z0-9_]+:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\S*)\s*$")
OFFSET = re.compile(r"(Z|[+-]\d{2}:\d{2})$")

def fail(msg):
    print("VALIDATE FAIL %s %s" % (msg, PATH))
    sys.exit(1)

text = open(PATH, encoding="utf-8").read()
try:
    doc = yaml.safe_load(text)
except Exception as exc:
    fail("unparseable %s" % exc)
if not isinstance(doc, dict):
    fail("not-a-mapping")
for key in (EVENT_ENVELOPE if KIND == "event" else RECORD_ENVELOPE):
    if key not in doc:
        fail("missing-envelope-field:%s" % key)
for line in text.splitlines():
    m = TS.match(line)
    if m and not OFFSET.search(m.group(1)):
        fail("timestamp-without-utc-offset:%s" % m.group(1))
if SCHEMA != "-" and os.path.exists(SCHEMA):
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    for key in schema.get("required", []):
        if key not in doc:
            fail("missing-schema-required-field:%s" % key)
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        try:
            jsonschema.validate(json.loads(json.dumps(doc, default=str)), schema)
        except jsonschema.ValidationError as exc:
            fail("schema:%s" % exc.message)
print("VALIDATE OK")
VI_EOF
cat > "$CP_ROOT/tools/records/lib/emit.sh" <<'EMIT_EOF'
#!/usr/bin/env bash
# tools/records/lib/emit.sh — the single record/event emission primitive of lane L4.
# Master Spec v4.0: 97.1 line 8839, 97.2 lines 8867/8871/8890, 97.3 lines 8929-8947,
# invariant 48 line 9516. Source this file; do not execute it.
# Optional: EMIT_SCHEMA=<file in schemas/records/>, EMIT_OCCURRED_AT=<UTC with offset>.
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
EMIT_TAXONOMY="$CP_ROOT/metrics/taxonomy/event-types.yaml"
EMIT_VALIDATOR="$CP_ROOT/tools/records/lib/validate_instance.py"

emit_now() { date -u +%Y-%m-%dT%H:%M:%S+00:00; }
emit_day() { date -u +%Y-%m-%d; }

emit_schema_path() {
  if [ -n "${EMIT_SCHEMA:-}" ]; then echo "$CP_ROOT/schemas/records/$EMIT_SCHEMA"; else echo "-"; fi
}

# emit_type_known <event_type> -- shape-independent token search of the taxonomy artifact.
emit_type_known() {
  if [ ! -f "$EMIT_TAXONOMY" ]; then
    echo "EMIT FAIL taxonomy-absent $EMIT_TAXONOMY" >&2; return 1
  fi
  if grep -qE "(^|[^A-Za-z0-9_])$1([^A-Za-z0-9_]|\$)" "$EMIT_TAXONOMY"; then return 0; fi
  echo "EMIT FAIL unknown-event-type $1" >&2; return 1
}

# emit_record <store> <id> <body-file>   -> prints the written path
emit_record() {
  emit_store="$1"; emit_id="$2"; emit_body="$3"
  emit_dir="$CPR_ROOT/records/$emit_store"
  if [ ! -d "$emit_dir" ]; then echo "EMIT FAIL no-store $emit_store" >&2; return 1; fi
  emit_out="$emit_dir/$emit_id.yaml"
  if [ -e "$emit_out" ]; then echo "EMIT FAIL overwrite-refused $emit_out" >&2; return 1; fi
  if ! python3 "$EMIT_VALIDATOR" record "$(emit_schema_path)" "$emit_body" >&2; then
    echo "EMIT FAIL invalid-record $emit_body" >&2; return 1
  fi
  cp "$emit_body" "$emit_out" || return 1
  echo "$emit_out"
}

# emit_event <event_type> <actor> <product> <subject_ref> <payload-file|-> -> prints the path
emit_event() {
  emit_et="$1"; emit_actor="$2"; emit_product="$3"; emit_subject="$4"; emit_payload="$5"
  emit_type_known "$emit_et" || return 1
  emit_d="$(emit_day)"; emit_edir="$CPR_ROOT/events/$emit_d"
  mkdir -p "$emit_edir"
  emit_seq="$(printf '%06d' "$(( $(find "$emit_edir" -maxdepth 1 -name 'EVT-*.yaml' | wc -l) + 1 ))")"
  emit_eid="EVT-$emit_d-$emit_seq"; emit_eout="$emit_edir/$emit_eid.yaml"
  if [ -e "$emit_eout" ]; then echo "EMIT FAIL overwrite-refused $emit_eout" >&2; return 1; fi
  {
    printf 'event_schema_version: 1\n'
    printf 'event_id: %s\n' "$emit_eid"
    printf 'event_type: %s\n' "$emit_et"
    printf 'occurred_at: %s\n' "${EMIT_OCCURRED_AT:-$(emit_now)}"
    printf 'recorded_at: %s\n' "$(emit_now)"
    printf 'actor: %s\n' "$emit_actor"
    printf 'product: %s\n' "$emit_product"
    printf 'subject_ref: %s\n' "$emit_subject"
    printf 'payload:\n'
    if [ "$emit_payload" = "-" ]; then printf '  {}\n'; else sed 's/^/  /' "$emit_payload"; fi
  } > "$emit_eout"
  if ! EMIT_SCHEMA="event.envelope.schema.json" python3 "$EMIT_VALIDATOR" event \
        "$CP_ROOT/schemas/records/event.envelope.schema.json" "$emit_eout" >&2; then
    rm -f "$emit_eout"; echo "EMIT FAIL invalid-event $emit_eid" >&2; return 1
  fi
  echo "$emit_eout"
}

emit_commit() { git -C "$CPR_ROOT" add -A && git -C "$CPR_ROOT" commit -q -m "$1"; }

# emit_pair <store> <id> <body-file> <event_type> <actor> <product> <payload-file|->
# Section 97.2 line 8871: writes the record AND appends the event. Never one without the other.
emit_pair() {
  emit_p_store="$1"; emit_p_id="$2"; emit_p_body="$3"; emit_p_et="$4"
  emit_p_actor="$5"; emit_p_product="$6"; emit_p_payload="$7"
  emit_p_rec="$(emit_record "$emit_p_store" "$emit_p_id" "$emit_p_body")" || return 1
  emit_p_ev="$(emit_event "$emit_p_et" "$emit_p_actor" "$emit_p_product" \
                "records/$emit_p_store/$emit_p_id.yaml" "$emit_p_payload")" || {
    rm -f "$emit_p_rec"
    echo "EMIT FAIL pair-rolled-back $emit_p_id" >&2; return 1; }
  emit_commit "records: $emit_p_id ($emit_p_store) + $(basename "$emit_p_ev" .yaml) [$emit_p_et]" || return 1
  echo "RECORD=$emit_p_rec"
  echo "EVENT=$emit_p_ev"
}
EMIT_EOF
chmod +x "$CP_ROOT/tools/records/lib/validate_instance.py"
if [ -e "$CP_ROOT/tools/records/record-write" ]; then
  grep -q 'lib/emit.sh' "$CP_ROOT/tools/records/record-write" \
    && echo "RECORD-WRITE PRE-EXISTS OK" \
    || echo "RECORD-WRITE CONFLICT does-not-delegate"
else
  cat > "$CP_ROOT/tools/records/record-write" <<'RW_EOF'
#!/usr/bin/env bash
# tools/records/record-write — L2-facing front-end. Delegates to lib/emit.sh.
# Usage: record-write <store> <id> <body-file> [schema-file]
# canonical form (FD-039): --path <path> --type <type> --title <title>
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/lib/emit.sh"
EMIT_SCHEMA="${4:-}" emit_record "$1" "$2" "$3"
RW_EOF
  cat > "$CP_ROOT/tools/records/event-append" <<'EA_EOF'
#!/usr/bin/env bash
# tools/records/event-append — L2-facing front-end. Delegates to lib/emit.sh.
# Usage: event-append <event_type> <actor> <product> <subject_ref> [payload-file]
# canonical form (FD-039): --path <path> --type <type> --title <title>
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/lib/emit.sh"
emit_event "$1" "$2" "$3" "$4" "${5:--}"
EA_EOF
  chmod +x "$CP_ROOT/tools/records/record-write" "$CP_ROOT/tools/records/event-append"
  echo "RECORD-WRITE CREATED"
fi
git -C "$CP_ROOT" add tools/records/lib tools/records/record-write tools/records/event-append
git -C "$CP_ROOT" commit -m "L4-T305: emission library - record+event pair, UTC offset, no silent overwrite"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Library and validator exist | `ls "$CP_ROOT"/tools/records/lib/emit.sh "$CP_ROOT"/tools/records/lib/validate_instance.py \| wc -l` | `2` |
| 2 | `record-write` and `event-append` both delegate to `lib/emit.sh` | `grep -lc 'lib/emit.sh' "$CP_ROOT"/tools/records/record-write "$CP_ROOT"/tools/records/event-append \| wc -l` | `2` |
| 3 | An event with an unknown type is refused | see SELF-VERIFY `T_UNKNOWN` | `EMIT FAIL unknown-event-type not_a_real_event_type` |
| 4 | A record write over an existing file is refused (invariant 48) | see SELF-VERIFY `T_OVERWRITE` | starts `EMIT FAIL overwrite-refused` |
| 5 | A timestamp without a UTC offset is refused (§97.1 line 8839) | see SELF-VERIFY `T_NOOFFSET` | starts `VALIDATE FAIL timestamp-without-utc-offset` |
| 6 | A record missing an envelope field is refused (§97.2 line 8890) | see SELF-VERIFY `T_ENVELOPE` | `VALIDATE FAIL missing-envelope-field:product` |
| 7 | No file was written outside `tools/records/` | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^tools/records/'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
V="$CP_ROOT/tools/records/lib/validate_instance.py"
T="$(mktemp -d)"
echo "FILES=$(ls "$CP_ROOT"/tools/records/lib/emit.sh "$CP_ROOT"/tools/records/lib/validate_instance.py 2>/dev/null | wc -l | tr -d ' ')"
echo "DELEGATES=$(grep -l 'lib/emit.sh' "$CP_ROOT"/tools/records/record-write "$CP_ROOT"/tools/records/event-append 2>/dev/null | wc -l | tr -d ' ')"
printf 'record_schema_version: 1\nid: SELFTEST-1\nproduct: selftest\ntimestamp: 2026-08-27T10:00:00+00:00\n' > "$T/good.yaml"
printf 'record_schema_version: 1\nid: SELFTEST-2\ntimestamp: 2026-08-27T10:00:00+00:00\n' > "$T/noenv.yaml"
printf 'record_schema_version: 1\nid: SELFTEST-3\nproduct: selftest\ntimestamp: 2026-08-27T10:00:00\n' > "$T/nooff.yaml"
( set +e; . "$CP_ROOT/tools/records/lib/emit.sh"
  echo "T_UNKNOWN=$(emit_event not_a_real_event_type selftest selftest ref - 2>&1 >/dev/null | head -1)"
  emit_record uat SELFTEST-OVERWRITE "$T/good.yaml" >/dev/null 2>&1
  echo "T_OVERWRITE=$(emit_record uat SELFTEST-OVERWRITE "$T/good.yaml" 2>&1 >/dev/null | head -1)"
  rm -f "$CPR_ROOT/records/uat/SELFTEST-OVERWRITE.yaml" )
echo "T_NOOFFSET=$(python3 "$V" record - "$T/nooff.yaml" 2>&1 | head -1)"
echo "T_ENVELOPE=$(python3 "$V" record - "$T/noenv.yaml" 2>&1 | head -1)"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^tools/records/')"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
rm -rf "$T"
```

Expected output, exactly:

```
FILES=2
DELEGATES=2
T_UNKNOWN=EMIT FAIL unknown-event-type not_a_real_event_type
T_OVERWRITE=EMIT FAIL overwrite-refused $HOME/src/control-plane-records/records/uat/SELFTEST-OVERWRITE.yaml
T_NOOFFSET=VALIDATE FAIL timestamp-without-utc-offset:2026-08-27T10:00:00 <path>
T_ENVELOPE=VALIDATE FAIL missing-envelope-field:product <path>
FOREIGN=0
CPRCLEAN=0
```

`<path>` is the temporary file path and varies; every other token is exact.

**STOP rule** — if `DELEGATES` is not `2`, or the guard printed `RECORD-WRITE CONFLICT does-not-delegate`: a second implementation of the record write already exists in the tree. **Do not overwrite it and do not delete it** — two writers for one store is exactly the divergence §97.1 line 8838 forbids. If `CPRCLEAN` is not `0`, the self-test left a file in the records repository: remove it with the `rm -f` line above and re-run. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T305 second record-write implementation, or emit guard failed"
lane: L4
phase: 3
task_id: L4-T305
blocked_by: "<record-write does not delegate to lib/emit.sh | negative test passed | records repo left dirty>"
observed: "<paste the exact SELF-VERIFY output and the guard line from the task commands>"
expected: "FILES=2 / DELEGATES=2 / all four negative tests fail / FOREIGN=0 / CPRCLEAN=0"
spec_ref: "Master Spec v4.0 Section 97.1 lines 8838-8839; Section 97.2 lines 8871, 8890; Section 97.3 line 8947; invariant 48 line 9516"
needs: "L0"
action_taken: "nothing overwritten, nothing deleted, nothing pushed"
```

---

### L4-T306 — The RECORD-VERIFICATION-RESULT handler

**Size:** L
**Depends on:** L4-T304, L4-T305

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/record-verification-result" <<'RVRH_EOF'
#!/usr/bin/env bash
# tools/records/record-verification-result
# The single pattern by which a human manual result reaches the machine.
# Master Spec v4.0 Section 97.2 line 8871; Section 18.4 line 1798; Section 31.2 line 2790;
# Section 44.3 line 4008; Section 22.5 line 2256.
# Called by the workflow_dispatch workflow L2 owns under .github/workflows/.
# Usage: record-verification-result <product> <item> <mechanism> <pass|fail> <evidence_link> <actor>
# canonical form (FD-039): --path <path> --type <type> --title <title>
set -euo pipefail
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/emit.sh"

if [ "$#" -ne 6 ]; then
  echo "RVR FAIL wrong-arity expected 6 got $#" >&2; exit 2
fi
PRODUCT="$1"; ITEM="$2"; MECHANISM="$3"; RESULT="$4"; EVIDENCE="$5"; ACTOR="$6"

for v in PRODUCT ITEM MECHANISM RESULT EVIDENCE ACTOR; do
  eval "val=\${$v}"
  if [ -z "$val" ]; then echo "RVR FAIL empty-input $v" >&2; exit 2; fi
done
case "$RESULT" in pass|fail) ;; *) echo "RVR FAIL bad-result $RESULT" >&2; exit 2 ;; esac
case "$EVIDENCE" in http://*|https://*) ;; *) echo "RVR FAIL bad-evidence-link $EVIDENCE" >&2; exit 2 ;; esac

LOOKUP="$(python3 - "$CP_ROOT/tools/records/dispatch/rvr-inputs.yaml" "$MECHANISM" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for m in d["mechanisms"]:
    if m["mechanism"] == sys.argv[2]:
        if not m["armed"]:
            print("UNARMED %s" % m["spec_ref"]); sys.exit(0)
        print("OK %s %s %s" % (m["target_store"], m["schema"], m["event_type"])); sys.exit(0)
print("UNKNOWN")
PY
)"
case "$LOOKUP" in
  UNKNOWN) echo "RVR FAIL unknown-mechanism $MECHANISM" >&2; exit 2 ;;
  UNARMED*) echo "RVR FAIL unarmed-mechanism $MECHANISM - $LOOKUP" >&2; exit 3 ;;
esac
STORE="$(echo "$LOOKUP" | cut -d' ' -f2)"
SCHEMA="$(echo "$LOOKUP" | cut -d' ' -f3)"
EVENT_TYPE="$(echo "$LOOKUP" | cut -d' ' -f4)"
PREFIX="$(python3 - "$CP_ROOT/tools/records/write-paths.yaml" "$STORE" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print(next(r["id_prefix"] for r in d["stores"] if r["store"] == sys.argv[2]))
PY
)"
DAY="$(emit_day)"
DIR="$CPR_ROOT/records/$STORE"
SEQ="$(printf '%03d' "$(( $(find "$DIR" -maxdepth 1 -name "$PREFIX-$DAY-*.yaml" | wc -l) + 1 ))")"
ID="$PREFIX-$DAY-$SEQ"
BODY="$(mktemp)"
trap 'rm -f "$BODY" "$BODY.payload"' EXIT
{
  printf 'record_schema_version: 1\n'
  printf 'id: %s\n' "$ID"
  printf 'product: %s\n' "$PRODUCT"
  printf 'timestamp: %s\n' "$(emit_now)"
  printf 'mechanism: %s\n' "$MECHANISM"
  printf 'item: %s\n' "$ITEM"
  printf 'result: %s\n' "$RESULT"
  printf 'evidence_link: %s\n' "$EVIDENCE"
  printf 'reported_by: %s\n' "$ACTOR"
  printf 'write_path: rvr-dispatch\n'
} > "$BODY"
{
  printf 'mechanism: %s\n' "$MECHANISM"
  printf 'result: %s\n' "$RESULT"
  printf 'item: %s\n' "$ITEM"
  printf 'evidence_link: %s\n' "$EVIDENCE"
} > "$BODY.payload"
EMIT_SCHEMA="$SCHEMA" emit_pair "$STORE" "$ID" "$BODY" "$EVENT_TYPE" "$ACTOR" "$PRODUCT" "$BODY.payload"
echo "RVR OK $ID $STORE $EVENT_TYPE"
RVRH_EOF
chmod +x "$CP_ROOT/tools/records/record-verification-result"
git -C "$CP_ROOT" add tools/records/record-verification-result
git -C "$CP_ROOT" commit -m "L4-T306: RECORD-VERIFICATION-RESULT handler - writes the record, appends the event"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Handler is executable | `test -x "$CP_ROOT/tools/records/record-verification-result" && echo YES` | `YES` |
| 2 | Handler takes exactly the six positional arguments (five inputs + actor) | `grep -c 'wrong-arity expected 6' "$CP_ROOT/tools/records/record-verification-result"` | `1` |
| 3 | Handler contains no hand-edit or in-place-edit path | `grep -cE '\bsed -i\b|>>' "$CP_ROOT/tools/records/record-verification-result"` | `0` |
| 4 | Handler resolves store, schema and event type from the contract, never from a literal | `grep -c 'rvr-inputs.yaml' "$CP_ROOT/tools/records/record-verification-result"` | `1` |
| 5 | Only `tools/records/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^tools/records/'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
H="$CP_ROOT/tools/records/record-verification-result"
echo "EXEC=$(test -x "$H" && echo yes || echo no)"
echo "ARITY=$(grep -c 'wrong-arity expected 6' "$H")"
echo "INPLACE=$(grep -cE '\bsed -i\b|>>' "$H")"
echo "CONTRACTDRIVEN=$(grep -c 'rvr-inputs.yaml' "$H")"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^tools/records/')"
```

Expected output, exactly:

```
EXEC=yes
ARITY=1
INPLACE=0
CONTRACTDRIVEN=1
FOREIGN=0
```

**STOP rule** — if `INPLACE` is not `0`, the handler contains an append or in-place edit: §97.2 line 8890 forbids editing a record in place, and `emit_pair` is the only write. If `CONTRACTDRIVEN` is not `1`, the handler has a hard-coded store or event type, which drifts from `rvr-inputs.yaml` the moment D-L4-P3-03 resolves. Do not push. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T306 RVR handler edits in place or hard-codes its routing"
lane: L4
phase: 3
task_id: L4-T306
blocked_by: "<in-place edit path present | routing hard-coded | wrong arity>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "EXEC=yes / ARITY=1 / INPLACE=0 / CONTRACTDRIVEN=1 / FOREIGN=0"
spec_ref: "Master Spec v4.0 Section 97.2 lines 8871, 8890"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T307 — RVR test harness (charter DoD-9)

**Size:** M
**Depends on:** L4-T306

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
[ -n "$CPR_ROOT" ] || { echo "ERROR: CPR_ROOT is not set"; exit 1; }
cat > "$CP_ROOT/tools/records/test-rvr.sh" <<'TRVR_EOF'
#!/usr/bin/env bash
# tools/records/test-rvr.sh — proves charter DoD-9.
# Master Spec v4.0 Section 97.2 line 8871.
# Runs against a throwaway clone of the records repository; the real store is untouched.
set -u
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
SANDBOX="$(mktemp -d)"
cp -R "$CPR_ROOT/." "$SANDBOX/"
export CPR_ROOT="$SANDBOX"
git -C "$SANDBOX" config user.email "records-writer@test.invalid"
git -C "$SANDBOX" config user.name "records-writer-test"
H="$CP_ROOT/tools/records/record-verification-result"
PASSED=0; FAILED=0
t() { # t <label> <expect-exit> <command...>
  label="$1"; want="$2"; shift 2
  "$@" >/dev/null 2>&1; got=$?
  if [ "$got" = "$want" ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); echo "RVR CASE FAIL $label want-exit=$want got-exit=$got"; fi
}
t armed-pass            0 "$H" demoprod ITEM-1 manual_verification pass https://example.invalid/run/1 lead-1
t armed-fail            0 "$H" demoprod ITEM-2 restore_test_confirmation fail https://example.invalid/run/2 qa-1
t unknown-mechanism     2 "$H" demoprod ITEM-3 not_a_mechanism pass https://example.invalid/run/3 lead-1
t unarmed-mechanism     3 "$H" demoprod ITEM-4 support_loop_closure pass https://example.invalid/run/4 lead-1
t bad-result            2 "$H" demoprod ITEM-5 manual_verification maybe https://example.invalid/run/5 lead-1
t bad-evidence-link     2 "$H" demoprod ITEM-6 manual_verification pass not-a-url lead-1
t empty-product         2 "$H" "" ITEM-7 manual_verification pass https://example.invalid/run/7 lead-1
t wrong-arity           2 "$H" demoprod ITEM-8 manual_verification pass
RECS=$(find "$SANDBOX/records/uat" "$SANDBOX/records/restore-tests" -name '*.yaml' | wc -l | tr -d ' ')
EVTS=$(find "$SANDBOX/events" -name 'EVT-*.yaml' | wc -l | tr -d ' ')
if [ "$RECS" != "2" ]; then echo "RVR CASE FAIL record-count want=2 got=$RECS"; FAILED=$((FAILED+1)); else PASSED=$((PASSED+1)); fi
if [ "$EVTS" != "2" ]; then echo "RVR CASE FAIL event-count want=2 got=$EVTS"; FAILED=$((FAILED+1)); else PASSED=$((PASSED+1)); fi
rm -rf "$SANDBOX"
if [ "$FAILED" != "0" ]; then echo "RVR FAIL $PASSED passed $FAILED failed"; exit 1; fi
echo "RVR OK"
TRVR_EOF
chmod +x "$CP_ROOT/tools/records/test-rvr.sh"
git -C "$CP_ROOT" add tools/records/test-rvr.sh
git -C "$CP_ROOT" commit -m "L4-T307: RVR test harness - 10 cases including 6 negatives (DoD-9)"
"$CP_ROOT/tools/records/test-rvr.sh"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Harness passes | `"$CP_ROOT/tools/records/test-rvr.sh"` | `RVR OK`, exit 0 |
| 2 | Exactly one record **and** one event per accepted dispatch | the `record-count` / `event-count` cases inside the harness | no `RVR CASE FAIL` line |
| 3 | Six negative cases are present | `grep -c '^t .* [23] ' "$CP_ROOT/tools/records/test-rvr.sh"` | `6` |
| 4 | The real records repository is untouched by the test | `git -C "$CPR_ROOT" status --porcelain \| wc -l` | `0` |
| 5 | An unarmed mechanism is refused, not written (D-L4-P3-03) | `. ; "$CP_ROOT/tools/records/record-verification-result" p i support_loop_closure pass https://x.invalid a; echo $?` | exit `3` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
echo "RESULT=$("$CP_ROOT/tools/records/test-rvr.sh" | tail -1)"
echo "NEGCASES=$(grep -c '^t .* [23] ' "$CP_ROOT/tools/records/test-rvr.sh")"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
"$CP_ROOT/tools/records/record-verification-result" p i support_loop_closure pass https://x.invalid a >/dev/null 2>&1
echo "UNARMEDEXIT=$?"
```

Expected output, exactly:

```
RESULT=RVR OK
NEGCASES=6
CPRCLEAN=0
UNARMEDEXIT=3
```

**STOP rule** — if `RESULT` is not `RVR OK`, read the `RVR CASE FAIL` lines the harness printed and fix **the handler**, never the test's expectations. If `CPRCLEAN` is not `0`, the harness wrote into the real store instead of its sandbox — `git -C "$CPR_ROOT" checkout -- .` and `git -C "$CPR_ROOT" clean -fd`, then stop. If `UNARMEDEXIT` is not `3`, an unarmed mechanism was accepted and an untyped event may have been written. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T307 RVR harness failed or wrote into the real store"
lane: L4
phase: 3
task_id: L4-T307
blocked_by: "<case failure | real store written | unarmed mechanism accepted>"
observed: "<paste the exact SELF-VERIFY output and every RVR CASE FAIL line>"
expected: "RESULT=RVR OK / NEGCASES=6 / CPRCLEAN=0 / UNARMEDEXIT=3"
spec_ref: "Master Spec v4.0 Section 97.2 line 8871; Section 97.3 line 8947; L4-00-charter.md DoD-9"
needs: "L0"
action_taken: "test expectations unmodified; nothing pushed"
```

---

### L4-T308 — The board-event emission contract

**Size:** M
**Depends on:** L4-T302

Declares which board transition emits which `event_type`, and what the board automation writes. The identifiers are the lower-case underscore-separated forms of the §97.3 tracked-events list (line 8951), which line 8947 requires. **Phase 3 does not create identifiers** — `validate-board-events` (task L4-T310) proves each one exists in `metrics/taxonomy/event-types.yaml`, and a miss is a blocker, never a taxonomy edit.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/dispatch/board-events.yaml" <<'BE_EOF'
# tools/records/dispatch/board-events.yaml
# Board automation emission contract. Master Spec v4.0 Section 29.1 lines 2625-2640
# (the seven flow columns; Blocked is a flag, not a column; Deploy is rendered from
# deployment records and nobody moves a card into it by hand), Section 29.5 lines 2672-2702,
# Section 97.2 line 8850, Section 97.5 lines 8983-8987.
# Every event_type below is the transliteration of an entry in the Section 97.3
# tracked-events list (line 8951). Phase 3 creates no identifier: validate-board-events.sh
# proves each is already in metrics/taxonomy/event-types.yaml.
contract_version: 1
flow_columns: [Backlog, Ready, Planned, "In Progress", "In Review", Verify, Done]
flags: [Blocked]
rendered_not_moved: [Deploy]      # Section 29.1 line 2628
transitions:
  - transition: created
    from: null
    to: Backlog
    event_type: work_item_created
    record: null
    spec_ref: "Section 97.3 line 8951 'Work item created'"
  - transition: to_ready
    from: Backlog
    to: Ready
    event_type: moved_to_ready
    record: null
    spec_ref: "Section 97.3 line 8951 'moved to Ready'; Section 29.3 line 2653"
  - transition: assigned
    from: Ready
    to: Planned
    event_type: assigned
    record: null
    spec_ref: "Section 97.3 line 8951 'assigned'; Section 29.3 line 2657 Ready -> Planned -> In Progress"
  - transition: execute_started
    from: Planned
    to: "In Progress"
    event_type: execute_started
    record: null
    spec_ref: "Section 97.3 line 8951 'execute started'"
  - transition: requirement_changed
    from: any
    to: same
    event_type: requirement_changed_materially
    record: null
    spec_ref: "Section 29.5 line 2672; Section 97.3 line 8951 'requirement changed materially'"
  - transition: re_plan
    from: any
    to: Planned
    event_type: re_plan_triggered
    record: null
    spec_ref: "Section 29.5 line 2700 (Blocked flag with reason re-plan); Section 97.3 line 8951 're-plan triggered'"
  - transition: item_closed
    from: Verify
    to: Done
    event_type: unarmed
    record: estimates
    spec_ref: "Section 97.2 line 8850 (estimate-vs-actual written by board automation at item close). BLOCKED by D-L4-P3-03: the Section 97.3 tracked-events list (line 8951) contains no item-closed identifier."
estimate_capture:
  # Section 29.3 line 2663: the record carries the band label AND the point value in force,
  # and both elapsed and elapsed net of recorded Blocked time, so the two are never confused.
  store: estimates
  schema: estimate.schema.json
  required_fields: [band, point_value, elapsed_hours, elapsed_net_of_blocked_hours, band_vocabulary_version]
  vocabulary_source: "registries/economics.yaml (L1-owned; Section 29.3 line 2663)"
  exempt_item_classes: [spike, incident, debt-remediation]   # Section 29.3 line 2663
BE_EOF
git -C "$CP_ROOT" add tools/records/dispatch/board-events.yaml
git -C "$CP_ROOT" commit -m "L4-T308: board-automation emission contract (Sections 29.1, 29.5, 97.2, 97.5)"
python3 -c "import yaml;d=yaml.safe_load(open(r'$CP_ROOT/tools/records/dispatch/board-events.yaml'));print('TRANS=%d COLS=%d'%(len(d['transitions']),len(d['flow_columns'])))"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Seven flow columns exactly as §29.1 line 2627 | see SELF-VERIFY `COLUMNS` | `Backlog,Ready,Planned,In Progress,In Review,Verify,Done` |
| 2 | `Blocked` is a flag, `Deploy` is rendered — neither is a flow column | see SELF-VERIFY `FLAGDEPLOY` | `flag=Blocked rendered=Deploy` |
| 3 | Seven transitions declared | see SELF-VERIFY `TRANS` | `7` |
| 4 | Exactly one transition is `unarmed` (D-L4-P3-03) | see SELF-VERIFY `UNARMED` | `1` |
| 5 | Estimate capture requires both elapsed figures (§29.3 line 2663) | see SELF-VERIFY `ESTFIELDS` | `band,point_value,elapsed_hours,elapsed_net_of_blocked_hours,band_vocabulary_version` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, yaml
d = yaml.safe_load(open(os.path.join(os.environ["CP_ROOT"], "tools", "records", "dispatch", "board-events.yaml")))
print("COLUMNS=%s" % ",".join(d["flow_columns"]))
print("FLAGDEPLOY=flag=%s rendered=%s" % (",".join(d["flags"]), ",".join(d["rendered_not_moved"])))
print("TRANS=%d" % len(d["transitions"]))
print("UNARMED=%d" % sum(1 for t in d["transitions"] if t["event_type"] == "unarmed"))
print("ESTFIELDS=%s" % ",".join(d["estimate_capture"]["required_fields"]))
PY
```

Expected output, exactly:

```
COLUMNS=Backlog,Ready,Planned,In Progress,In Review,Verify,Done
FLAGDEPLOY=flag=Blocked rendered=Deploy
TRANS=7
UNARMED=1
ESTFIELDS=band,point_value,elapsed_hours,elapsed_net_of_blocked_hours,band_vocabulary_version
```

**STOP rule** — if `COLUMNS` differs, the contract disagrees with §29.1 line 2627: re-copy the block, do not adjust it. If `UNARMED` is `0`, someone armed `item_closed` with an invented identifier — revert. If `FLAGDEPLOY` shows `Blocked` or `Deploy` inside `flow_columns`, §29.1 line 2628 is violated. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T308 board-event contract disagrees with Section 29.1"
lane: L4
phase: 3
task_id: L4-T308
blocked_by: "<column set wrong | Blocked or Deploy treated as a column | item_closed armed without a taxonomy identifier>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "COLUMNS=Backlog,Ready,Planned,In Progress,In Review,Verify,Done / FLAGDEPLOY=flag=Blocked rendered=Deploy / TRANS=7 / UNARMED=1"
spec_ref: "Master Spec v4.0 Section 29.1 lines 2627-2628; Section 29.3 line 2663; Section 97.2 line 8850; Section 97.3 line 8951"
needs: "L0 - decision D-L4-P3-03"
action_taken: "no identifier invented"
```

---

### L4-T309 — The board emitter and the Ready-queue-miss emitter

**Size:** L
**Depends on:** L4-T305, L4-T308

Two front-ends the board automation calls. `board-emit` emits a transition event (and, when the contract names a record, that record). `rqm-emit` emits the Ready-queue-miss event carrying the **full §29.4 field set**.

**Scope boundary, binding:** `rqm-emit` **emits**; it does not decide. It consumes a verdict document produced by the detector (charter DoD-8, another phase's task) and refuses to run without one. It never infers `team_lead_blocked` or `priority_changed_recently` — §97.5 line 8987: *"the last three supplied by the cause prompt, never inferred."*

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/board-emit" <<'BEM_EOF'
#!/usr/bin/env bash
# tools/records/board-emit — board-automation event emitter.
# Master Spec v4.0 Section 29.1 lines 2625-2640; Section 97.2 line 8850; Section 97.3 line 8929.
# Usage: board-emit <transition> <product> <actor> <subject_ref> [key=value ...]
set -euo pipefail
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/emit.sh"
if [ "$#" -lt 4 ]; then echo "BOARD FAIL wrong-arity expected at least 4 got $#" >&2; exit 2; fi
TRANSITION="$1"; PRODUCT="$2"; ACTOR="$3"; SUBJECT="$4"; shift 4
LOOKUP="$(python3 - "$CP_ROOT/tools/records/dispatch/board-events.yaml" "$TRANSITION" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for t in d["transitions"]:
    if t["transition"] == sys.argv[2]:
        if t["event_type"] == "unarmed":
            print("UNARMED %s" % t["spec_ref"]); sys.exit(0)
        print("OK %s %s" % (t["event_type"], t["record"] or "-")); sys.exit(0)
print("UNKNOWN")
PY
)"
case "$LOOKUP" in
  UNKNOWN) echo "BOARD FAIL unknown-transition $TRANSITION" >&2; exit 2 ;;
  UNARMED*) echo "BOARD FAIL unarmed-transition $TRANSITION - $LOOKUP" >&2; exit 3 ;;
esac
EVENT_TYPE="$(echo "$LOOKUP" | cut -d' ' -f2)"
PAYLOAD="$(mktemp)"; trap 'rm -f "$PAYLOAD"' EXIT
printf 'transition: %s\n' "$TRANSITION" > "$PAYLOAD"
printf 'write_path: machine-board\n' >> "$PAYLOAD"
for kv in "$@"; do printf '%s: %s\n' "${kv%%=*}" "${kv#*=}" >> "$PAYLOAD"; done
emit_event "$EVENT_TYPE" "$ACTOR" "$PRODUCT" "$SUBJECT" "$PAYLOAD" >/dev/null
emit_commit "events: $TRANSITION [$EVENT_TYPE] $PRODUCT"
echo "BOARD OK $TRANSITION $EVENT_TYPE"
BEM_EOF
cat > "$CP_ROOT/tools/records/rqm-emit" <<'RQM_EOF'
#!/usr/bin/env bash
# tools/records/rqm-emit — Ready-queue-miss event emitter.
# Master Spec v4.0 Section 29.4 lines 2668-2671 (the recorded field set) and
# Section 97.5 lines 8983-8987 (both detector limbs; the ready_bypass carve-out;
# the last three fields supplied by the cause prompt, never inferred).
# THIS SCRIPT EMITS; IT DOES NOT DETECT. It consumes the detector's verdict document.
# Usage: rqm-emit <verdict-file.yaml>
# Verdict document, all keys required:
#   limb: pickup_without_ready | completion_with_empty_ready | ready_bypass
#   person: <registry identity>      date: <YYYY-MM-DD>      product: <product key>
#   queue_empty_reason: <text from the cause prompt>
#   team_lead_blocked: true|false    priority_changed_recently: true|false
#   subject_ref: <work item reference>
set -euo pipefail
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/emit.sh"
if [ "$#" -ne 1 ]; then echo "RQM FAIL wrong-arity expected 1 got $#" >&2; exit 2; fi
VERDICT="$1"
if [ ! -f "$VERDICT" ]; then echo "RQM FAIL no-verdict-file $VERDICT" >&2; exit 2; fi
python3 - "$VERDICT" <<'PY' || exit 2
import sys, yaml
req = ["limb", "person", "date", "product", "queue_empty_reason",
       "team_lead_blocked", "priority_changed_recently", "subject_ref"]
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
missing = [k for k in req if k not in d or d[k] in (None, "")]
if missing:
    print("RQM FAIL missing-field:%s" % ",".join(missing)); sys.exit(1)
if d["limb"] not in ("pickup_without_ready", "completion_with_empty_ready", "ready_bypass"):
    print("RQM FAIL bad-limb:%s" % d["limb"]); sys.exit(1)
PY
LIMB="$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['limb'])" "$VERDICT")"
PRODUCT="$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['product'])" "$VERDICT")"
ACTOR="$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['person'])" "$VERDICT")"
SUBJECT="$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['subject_ref'])" "$VERDICT")"
PAYLOAD="$(mktemp)"; trap 'rm -f "$PAYLOAD"' EXIT
cat "$VERDICT" > "$PAYLOAD"
# Section 97.5 line 8986: a full-Ready bypass is recorded with reason ready_bypass as a
# board-hygiene finding and never enters the SIG-06 count (Section 52.2 line 4535).
if [ "$LIMB" = "ready_bypass" ]; then
  printf 'reason: ready_bypass\nsig06_counted: false\n' >> "$PAYLOAD"
else
  printf 'sig06_counted: true\n' >> "$PAYLOAD"
fi
printf 'write_path: machine-board\n' >> "$PAYLOAD"
emit_event ready_queue_miss_recorded "$ACTOR" "$PRODUCT" "$SUBJECT" "$PAYLOAD" >/dev/null
emit_commit "events: ready_queue_miss_recorded [$LIMB] $PRODUCT"
echo "RQM OK $LIMB $PRODUCT"
RQM_EOF
chmod +x "$CP_ROOT/tools/records/board-emit" "$CP_ROOT/tools/records/rqm-emit"
git -C "$CP_ROOT" add tools/records/board-emit tools/records/rqm-emit
git -C "$CP_ROOT" commit -m "L4-T309: board-automation and Ready-queue-miss emitters (Sections 29.4, 97.5)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Both emitters executable | `ls -l "$CP_ROOT"/tools/records/board-emit "$CP_ROOT"/tools/records/rqm-emit \| grep -c '^-..x' ` | `2` |
| 2 | `rqm-emit` requires all six §29.4 fields plus limb and subject | `grep -c 'queue_empty_reason", *$\|"queue_empty_reason"' "$CP_ROOT/tools/records/rqm-emit"` | `1` or greater |
| 3 | `rqm-emit` carries the `ready_bypass` carve-out with `sig06_counted: false` | `grep -c 'sig06_counted: false' "$CP_ROOT/tools/records/rqm-emit"` | `1` |
| 4 | `rqm-emit` contains no detection logic (it consumes a verdict) | `grep -ci 'backlog\|in progress\|queue depth' "$CP_ROOT/tools/records/rqm-emit"` | `0` |
| 5 | `board-emit` refuses the unarmed `item_closed` transition | see SELF-VERIFY `ITEMCLOSED` | exit `3` |
| 6 | Only `tools/records/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^tools/records/'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
echo "EXEC=$(ls -l "$CP_ROOT"/tools/records/board-emit "$CP_ROOT"/tools/records/rqm-emit | grep -c '^-..x')"
echo "BYPASS=$(grep -c 'sig06_counted: false' "$CP_ROOT/tools/records/rqm-emit")"
echo "NODETECT=$(grep -ci 'backlog\|in progress\|queue depth' "$CP_ROOT/tools/records/rqm-emit")"
"$CP_ROOT/tools/records/board-emit" item_closed demoprod lead-1 ref >/dev/null 2>&1
echo "ITEMCLOSED=$?"
"$CP_ROOT/tools/records/rqm-emit" /nonexistent.yaml >/dev/null 2>&1
echo "NOVERDICT=$?"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^tools/records/')"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
EXEC=2
BYPASS=1
NODETECT=0
ITEMCLOSED=3
NOVERDICT=2
FOREIGN=0
CPRCLEAN=0
```

**STOP rule** — if `NODETECT` is not `0`, detection logic has leaked into the emitter; the detector is a different task in a different phase and two implementations will diverge. If `ITEMCLOSED` is not `3`, the unarmed transition was accepted and an untyped or invented event may exist — inspect `git -C "$CPR_ROOT" log -1 --stat` and stop. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T309 emitter contains detection logic or accepted an unarmed transition"
lane: L4
phase: 3
task_id: L4-T309
blocked_by: "<detection logic in rqm-emit | unarmed transition accepted | records repo dirty>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "EXEC=2 / BYPASS=1 / NODETECT=0 / ITEMCLOSED=3 / NOVERDICT=2 / FOREIGN=0 / CPRCLEAN=0"
spec_ref: "Master Spec v4.0 Section 29.4 lines 2668-2671; Section 97.5 lines 8983-8987; Section 97.3 line 8947"
needs: "L0 - decision D-L4-P3-03"
action_taken: "nothing pushed"
```

---

### L4-T310 — Taxonomy conformance check for both emission contracts

**Size:** M
**Depends on:** L4-T304, L4-T308

Proves that every armed `event_type` in `rvr-inputs.yaml` and `board-events.yaml` already exists in `metrics/taxonomy/event-types.yaml`. **This check never edits the taxonomy.** §97.3 line 8947: a new event type is a governed addition to the enum, and the enum lives in `registries/platform.yaml`, which L4 must never write (charter §3.1).

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/validate-board-events.sh" <<'VBE_EOF'
#!/usr/bin/env bash
# tools/records/validate-board-events.sh
# Every armed event_type in the Phase 3 emission contracts must already exist in the
# Section 97.3 taxonomy artifact. Master Spec v4.0 Section 97.3 line 8947.
# THIS SCRIPT NEVER WRITES THE TAXONOMY.
set -u
: "${CP_ROOT:?CP_ROOT not set}"
TAX="$CP_ROOT/metrics/taxonomy/event-types.yaml"
if [ ! -f "$TAX" ]; then echo "TAXONOMY-CONFORMANCE FAIL taxonomy-absent $TAX"; exit 1; fi
TYPES="$(python3 - "$CP_ROOT" <<'PY'
import os, sys, yaml
cp = sys.argv[1]
out = []
r = yaml.safe_load(open(os.path.join(cp, "tools", "records", "dispatch", "rvr-inputs.yaml"), encoding="utf-8"))
out += [m["event_type"] for m in r["mechanisms"] if m["armed"]]
b = yaml.safe_load(open(os.path.join(cp, "tools", "records", "dispatch", "board-events.yaml"), encoding="utf-8"))
out += [t["event_type"] for t in b["transitions"] if t["event_type"] != "unarmed"]
out += ["ready_queue_miss_recorded"]
print("\n".join(sorted(set(out))))
PY
)"
MISSING=0; TOTAL=0
for t in $TYPES; do
  TOTAL=$((TOTAL+1))
  if ! grep -qE "(^|[^A-Za-z0-9_])$t([^A-Za-z0-9_]|\$)" "$TAX"; then
    echo "TAXONOMY-CONFORMANCE FAIL absent-from-taxonomy $t"; MISSING=$((MISSING+1))
  fi
done
if [ "$MISSING" != "0" ]; then echo "TAXONOMY-CONFORMANCE FAIL $MISSING/$TOTAL absent"; exit 1; fi
echo "TAXONOMY-CONFORMANCE OK $TOTAL/$TOTAL"
VBE_EOF
chmod +x "$CP_ROOT/tools/records/validate-board-events.sh"
git -C "$CP_ROOT" add tools/records/validate-board-events.sh
git -C "$CP_ROOT" commit -m "L4-T310: taxonomy conformance check for the Phase 3 emission contracts"
"$CP_ROOT/tools/records/validate-board-events.sh"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script is executable | `test -x "$CP_ROOT/tools/records/validate-board-events.sh" && echo YES` | `YES` |
| 2 | Every armed identifier is in the taxonomy | `"$CP_ROOT/tools/records/validate-board-events.sh"` | `TAXONOMY-CONFORMANCE OK 9/9`, exit 0 |
| 3 | The script writes nothing | `grep -cE '>\s*"?\$TAX|sed -i' "$CP_ROOT/tools/records/validate-board-events.sh"` | `0` |
| 4 | The taxonomy file is byte-identical after the run | see SELF-VERIFY `TAXUNCHANGED` | `unchanged` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
TAX="$CP_ROOT/metrics/taxonomy/event-types.yaml"
BEFORE="$(git -C "$CP_ROOT" hash-object "$TAX")"
echo "RESULT=$("$CP_ROOT/tools/records/validate-board-events.sh" | tail -1)"
AFTER="$(git -C "$CP_ROOT" hash-object "$TAX")"
echo "TAXUNCHANGED=$([ "$BEFORE" = "$AFTER" ] && echo unchanged || echo MODIFIED)"
echo "NOWRITE=$(grep -cE '> *"?\$TAX|sed -i' "$CP_ROOT/tools/records/validate-board-events.sh")"
```

Expected output, exactly:

```
RESULT=TAXONOMY-CONFORMANCE OK 9/9
TAXUNCHANGED=unchanged
NOWRITE=0
```

The nine identifiers are: `uat_executed`, `restore_test_executed`, `work_item_created`, `moved_to_ready`, `assigned`, `execute_started`, `requirement_changed_materially`, `re_plan_triggered`, `ready_queue_miss_recorded`.

**STOP rule** — if any `absent-from-taxonomy` line appears, **do not add the identifier to `metrics/taxonomy/event-types.yaml` and do not change the contract file to a name that happens to be present.** §97.3 line 8947 makes a new event type a governed addition; either the taxonomy is incomplete or the transliteration is wrong, and both are L0's call. If `TAXUNCHANGED=MODIFIED`, the check wrote to a file it must only read. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T310 armed event_type absent from the Section 97.3 taxonomy"
lane: L4
phase: 3
task_id: L4-T310
blocked_by: "<identifier absent from taxonomy | taxonomy modified by the check>"
observed: "<paste every 'absent-from-taxonomy' line and the SELF-VERIFY output>"
expected: "RESULT=TAXONOMY-CONFORMANCE OK 9/9 / TAXUNCHANGED=unchanged / NOWRITE=0"
spec_ref: "Master Spec v4.0 Section 97.3 lines 8947, 8951; L4-00-charter.md section 3.1 (registries are L1's)"
needs: "L0 - decisions D-L4-01 and D-L4-P3-03"
action_taken: "taxonomy not modified; no identifier invented"
```

---

### L4-T311 — The deploy required-step contract

**Size:** M
**Depends on:** L4-T302

§97.2 line 8867 makes the deployment-record and event writes **required, failing steps** of `deploy-production.yml`. L2 owns that workflow file. Phase 3 publishes the contract L2 transcribes, and the emitter L2 calls. The contract states explicitly that no step may carry `continue-on-error: true`.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/dispatch/deploy-steps.yaml" <<'DS_EOF'
# tools/records/dispatch/deploy-steps.yaml
# The record and event writes deploy-production.yml must run as REQUIRED, FAILING steps.
# Master Spec v4.0 Section 97.2 line 8867: "the deployment-record and event writes are
# required, failing steps of deploy-production.yml rather than trailing best-effort ones:
# a deploy whose record cannot be written is a deploy whose evidence chain does not close,
# and the eleven questions of Section 32 are unanswerable for it afterwards."
# L2 owns .github/workflows/deploy-production.yml (PARTITION.md line 18) and transcribes
# this contract into it. L4 owns tools/records/deploy-emit, which the workflow calls.
contract_version: 1
binding_rules:
  - "No step below may carry continue-on-error: true."
  - "No step below may be guarded by if: always() in a way that lets the job succeed after it fails."
  - "The deployment record and its event are one commit; a record without its event is never written."
  - "Section 32 line 2827: the chain is assembled from these records, never from hand-maintained state."
steps:
  - step: record_artifact_built
    event_type: artifact_built
    record: null
    required_failing: true
    payload_fields: [digest]
    spec_ref: "Section 32 line 2812 question 5; Section 97.3 line 8951 'artifact built with digest'"
  - step: record_staging_deployed
    event_type: staging_deployed
    record: null
    required_failing: true
    payload_fields: [digest, environment]
    spec_ref: "Section 32 line 2813 question 6; Section 97.3 line 8951 'staging deployed'"
  - step: record_staging_smoke
    event_type: staging_smoke_result
    record: null
    required_failing: true
    payload_fields: [smoke_result]
    spec_ref: "Section 32 line 2814 question 7; Section 97.3 line 8951 'staging smoke result'"
  - step: record_production_approval
    event_type: production_approval_granted
    record: null
    required_failing: true
    payload_fields: [approved_by, approval_event]
    spec_ref: "Section 32 line 2815 question 8; Section 97.3 line 8951 'production approval granted with approver'"
  - step: record_production_deployed
    event_type: production_deployed
    record: deployments
    required_failing: true
    payload_fields: [digest]
    spec_ref: "Section 97.2 lines 8851, 8867; Section 32 line 2816 question 9; Section 97.3 line 8951 'production deployed with digest'"
  - step: record_production_smoke
    event_type: production_smoke_result
    record: null
    required_failing: true
    payload_fields: [smoke_result]
    spec_ref: "Section 32 line 2817 question 10; Section 97.3 line 8951 'production smoke result'"
  - step: record_version_digest_confirmed
    event_type: version_digest_confirmed
    record: null
    required_failing: true
    payload_fields: [digest]
    spec_ref: "Section 32 line 2818 question 11; Section 97.3 line 8951 '/version digest confirmed'"
  - step: record_rollback_initiated
    event_type: rollback_initiated
    record: deployments
    required_failing: true
    payload_fields: [from_digest, to_digest, rollback_of]
    spec_ref: "Section 97.3 line 8951 'rollback initiated with from-digest and to-digest'"
deployment_record_fields:
  # Section 97.2 lines 8894-8902, the representative deployment schema, copied field for field.
  required: [id, product, digest, approved_by, approval_event, staging_verified, uat_record, smoke_result, rollback_of]
  schema: deployment.schema.json
DS_EOF
git -C "$CP_ROOT" add tools/records/dispatch/deploy-steps.yaml
git -C "$CP_ROOT" commit -m "L4-T311: deploy required-failing-step contract (Section 97.2 line 8867, Section 32)"
python3 -c "import yaml;d=yaml.safe_load(open(r'$CP_ROOT/tools/records/dispatch/deploy-steps.yaml'));print('STEPS=%d REQ=%d'%(len(d['steps']),sum(1 for s in d['steps'] if s['required_failing'])))"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Eight steps declared | see SELF-VERIFY `STEPS` | `8` |
| 2 | **Every** step is `required_failing: true` | see SELF-VERIFY `REQUIRED` | `8` |
| 3 | Exactly two steps write the `deployments` record | see SELF-VERIFY `RECORDSTEPS` | `2` |
| 4 | The deployment record fields are §97.2 lines 8894–8902 verbatim | see SELF-VERIFY `DEPFIELDS` | `id,product,digest,approved_by,approval_event,staging_verified,uat_record,smoke_result,rollback_of` |
| 5 | The file forbids `continue-on-error` in writing | `grep -c 'continue-on-error' "$CP_ROOT/tools/records/dispatch/deploy-steps.yaml"` | `1` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
python3 - <<'PY'
import os, yaml
d = yaml.safe_load(open(os.path.join(os.environ["CP_ROOT"], "tools", "records", "dispatch", "deploy-steps.yaml")))
print("STEPS=%d" % len(d["steps"]))
print("REQUIRED=%d" % sum(1 for s in d["steps"] if s["required_failing"]))
print("RECORDSTEPS=%d" % sum(1 for s in d["steps"] if s["record"] == "deployments"))
print("DEPFIELDS=%s" % ",".join(d["deployment_record_fields"]["required"]))
PY
```

Expected output, exactly:

```
STEPS=8
REQUIRED=8
RECORDSTEPS=2
DEPFIELDS=id,product,digest,approved_by,approval_event,staging_verified,uat_record,smoke_result,rollback_of
```

**STOP rule** — if `REQUIRED` is not `8`, a step has been marked optional: §97.2 line 8867 admits no best-effort deploy record. If `DEPFIELDS` differs from the string above, the contract no longer matches §97.2 lines 8894–8902 and the §32 evidence chain will not close. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T311 deploy contract weakened a required step or changed the record shape"
lane: L4
phase: 3
task_id: L4-T311
blocked_by: "<step marked optional | deployment record fields altered>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "STEPS=8 / REQUIRED=8 / RECORDSTEPS=2 / DEPFIELDS as printed in L4-03-write-paths.md"
spec_ref: "Master Spec v4.0 Section 97.2 lines 8867, 8894-8902; Section 32 lines 2807-2827"
needs: "L0"
action_taken: "nothing weakened; nothing pushed"
```

---

### L4-T312 — The deploy emitter

**Size:** L
**Depends on:** L4-T305, L4-T311

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/deploy-emit" <<'DE_EOF'
#!/usr/bin/env bash
# tools/records/deploy-emit — the deploy workflow's record and event writer.
# Master Spec v4.0 Section 97.2 lines 8851, 8867, 8894-8902; Section 32 lines 2807-2827.
# Called by deploy-production.yml / deploy-staging.yml (L2-owned) as a REQUIRED, FAILING step.
# Non-zero exit is the contract: a deploy whose record cannot be written must fail the deploy.
# Usage: deploy-emit <step> <product> <actor> <subject_ref> [key=value ...]
# For the two record-writing steps, these key=value pairs are required:
#   digest= approved_by= approval_event= staging_verified= uat_record= smoke_result= rollback_of=
set -euo pipefail
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/emit.sh"
if [ "$#" -lt 4 ]; then echo "DEPLOY FAIL wrong-arity expected at least 4 got $#" >&2; exit 2; fi
STEP="$1"; PRODUCT="$2"; ACTOR="$3"; SUBJECT="$4"; shift 4
LOOKUP="$(python3 - "$CP_ROOT/tools/records/dispatch/deploy-steps.yaml" "$STEP" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for s in d["steps"]:
    if s["step"] == sys.argv[2]:
        print("OK %s %s" % (s["event_type"], s["record"] or "-")); sys.exit(0)
print("UNKNOWN")
PY
)"
if [ "$LOOKUP" = "UNKNOWN" ]; then echo "DEPLOY FAIL unknown-step $STEP" >&2; exit 2; fi
EVENT_TYPE="$(echo "$LOOKUP" | cut -d' ' -f2)"
RECORD="$(echo "$LOOKUP" | cut -d' ' -f3)"
KV="$(mktemp)"; BODY="$(mktemp)"; trap 'rm -f "$KV" "$BODY"' EXIT
printf 'step: %s\nwrite_path: machine-deploy\n' "$STEP" > "$KV"
for kv in "$@"; do printf '%s: %s\n' "${kv%%=*}" "${kv#*=}" >> "$KV"; done
if [ "$RECORD" = "-" ]; then
  emit_event "$EVENT_TYPE" "$ACTOR" "$PRODUCT" "$SUBJECT" "$KV" >/dev/null
  emit_commit "events: $STEP [$EVENT_TYPE] $PRODUCT"
  echo "DEPLOY OK $STEP $EVENT_TYPE"
  exit 0
fi
REQ="$(python3 -c "import yaml,sys;print(' '.join(yaml.safe_load(open(sys.argv[1],encoding='utf-8'))['deployment_record_fields']['required']))" "$CP_ROOT/tools/records/dispatch/deploy-steps.yaml")"
DAY="$(emit_day)"
DIR="$CPR_ROOT/records/$RECORD"
SEQ="$(printf '%03d' "$(( $(find "$DIR" -maxdepth 1 -name "DEP-$DAY-*.yaml" | wc -l) + 1 ))")"
ID="DEP-$DAY-$SEQ"
{
  printf 'record_schema_version: 1\n'
  printf 'id: %s\n' "$ID"
  printf 'product: %s\n' "$PRODUCT"
  printf 'timestamp: %s\n' "$(emit_now)"
  printf 'write_path: machine-deploy\n'
  printf 'deployed_by: %s\n' "$ACTOR"
} > "$BODY"
for f in $REQ; do
  case "$f" in id|product) continue ;; esac
  val=""
  for kv in "$@"; do case "$kv" in "$f="*) val="${kv#*=}" ;; esac; done
  if [ -z "$val" ]; then echo "DEPLOY FAIL missing-required-field $f" >&2; exit 1; fi
  printf '%s: %s\n' "$f" "$val" >> "$BODY"
done
EMIT_SCHEMA="deployment.schema.json" emit_pair "$RECORD" "$ID" "$BODY" "$EVENT_TYPE" "$ACTOR" "$PRODUCT" "$KV"
echo "DEPLOY OK $STEP $EVENT_TYPE $ID"
DE_EOF
chmod +x "$CP_ROOT/tools/records/deploy-emit"
git -C "$CP_ROOT" add tools/records/deploy-emit
git -C "$CP_ROOT" commit -m "L4-T312: deploy emitter - record and event as a required failing step"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Emitter executable | `test -x "$CP_ROOT/tools/records/deploy-emit" && echo YES` | `YES` |
| 2 | A missing required deployment field fails the step non-zero | see SELF-VERIFY `MISSINGFIELD` | exit `1`, message `DEPLOY FAIL missing-required-field approved_by` |
| 3 | An unknown step fails non-zero | see SELF-VERIFY `UNKNOWNSTEP` | exit `2` |
| 4 | The required field list is read from the contract, never hard-coded | `grep -c "deployment_record_fields" "$CP_ROOT/tools/records/deploy-emit"` | `1` |
| 5 | No `continue-on-error`, no `\|\| true`, no `set +e` anywhere | `grep -cE '\|\| true|set \+e|continue-on-error' "$CP_ROOT/tools/records/deploy-emit"` | `0` |
| 6 | Only `tools/records/` changed | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^tools/records/'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
D="$CP_ROOT/tools/records/deploy-emit"
OUT="$("$D" record_production_deployed demoprod dev-1 ref digest=sha256:abc 2>&1)"; RC=$?
echo "MISSINGFIELD=$RC:$(echo "$OUT" | grep -o 'DEPLOY FAIL missing-required-field [a-z_]*' | head -1)"
"$D" not_a_step demoprod dev-1 ref >/dev/null 2>&1
echo "UNKNOWNSTEP=$?"
echo "CONTRACTDRIVEN=$(grep -c 'deployment_record_fields' "$D")"
echo "BESTEFFORT=$(grep -cE '\|\| true|set \+e|continue-on-error' "$D")"
echo "FOREIGN=$(git -C "$CP_ROOT" diff --name-only origin/integration...HEAD | grep -vc '^tools/records/')"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
MISSINGFIELD=1:DEPLOY FAIL missing-required-field approved_by
UNKNOWNSTEP=2
CONTRACTDRIVEN=1
BESTEFFORT=0
FOREIGN=0
CPRCLEAN=0
```

**STOP rule** — if `BESTEFFORT` is not `0`, the emitter can swallow its own failure and §97.2 line 8867 is defeated at the only place it can be defeated. If `MISSINGFIELD` does not begin `1:`, an incomplete deployment record was accepted and the §32 evidence chain cannot close for that deploy. Do not push. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T312 deploy emitter can succeed without a complete record"
lane: L4
phase: 3
task_id: L4-T312
blocked_by: "<failure swallowed | incomplete deployment record accepted | unknown step accepted>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "MISSINGFIELD=1:DEPLOY FAIL missing-required-field approved_by / UNKNOWNSTEP=2 / CONTRACTDRIVEN=1 / BESTEFFORT=0 / FOREIGN=0 / CPRCLEAN=0"
spec_ref: "Master Spec v4.0 Section 97.2 lines 8867, 8894-8902; Section 32 lines 2807-2827"
needs: "L0"
action_taken: "nothing pushed"
```

---

### L4-T313 — The deploy emitter failure test

**Size:** M
**Depends on:** L4-T312

Proves the required-failing-step property directly: when the records repository is unwritable, `deploy-emit` exits non-zero and leaves **nothing** behind. This is §97.2 line 8867 turned into a test rather than an assertion.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
[ -n "$CPR_ROOT" ] || { echo "ERROR: CPR_ROOT is not set"; exit 1; }
cat > "$CP_ROOT/tools/records/test-deploy-emit.sh" <<'TDE_EOF'
#!/usr/bin/env bash
# tools/records/test-deploy-emit.sh
# Master Spec v4.0 Section 97.2 line 8867 - required, failing steps, proved.
set -u
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
SANDBOX="$(mktemp -d)"
cp -R "$CPR_ROOT/." "$SANDBOX/"
export CPR_ROOT="$SANDBOX"
git -C "$SANDBOX" config user.email "records-writer@test.invalid"
git -C "$SANDBOX" config user.name "records-writer-test"
D="$CP_ROOT/tools/records/deploy-emit"
FAILED=0
FULL="digest=sha256:deadbeef approved_by=lead-1 approval_event=https://example.invalid/run/9 staging_verified=true uat_record=records/uat/UAT-x.yaml smoke_result=pass rollback_of=null"
# 1. Happy path writes exactly one record and one event, in one commit.
BEFORE_COMMITS=$(git -C "$SANDBOX" rev-list --count HEAD)
if ! $D record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1; then
  echo "DEPLOY CASE FAIL happy-path-nonzero"; FAILED=$((FAILED+1)); fi
RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
EVTS=$(find "$SANDBOX/events" -name 'EVT-*.yaml' | wc -l | tr -d ' ')
AFTER_COMMITS=$(git -C "$SANDBOX" rev-list --count HEAD)
[ "$RECS" = "1" ] || { echo "DEPLOY CASE FAIL record-count want=1 got=$RECS"; FAILED=$((FAILED+1)); }
[ "$EVTS" = "1" ] || { echo "DEPLOY CASE FAIL event-count want=1 got=$EVTS"; FAILED=$((FAILED+1)); }
[ "$((AFTER_COMMITS-BEFORE_COMMITS))" = "1" ] || { echo "DEPLOY CASE FAIL commit-count want=1 got=$((AFTER_COMMITS-BEFORE_COMMITS))"; FAILED=$((FAILED+1)); }
# 2. Store removed: the step must fail non-zero and write nothing.
mv "$SANDBOX/records/deployments" "$SANDBOX/records/deployments.hidden"
$D record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1
[ "$?" != "0" ] || { echo "DEPLOY CASE FAIL unwritable-store-returned-zero"; FAILED=$((FAILED+1)); }
mv "$SANDBOX/records/deployments.hidden" "$SANDBOX/records/deployments"
STRAY=$(git -C "$SANDBOX" status --porcelain | wc -l | tr -d ' ')
[ "$STRAY" = "0" ] || { echo "DEPLOY CASE FAIL residue-after-failure count=$STRAY"; FAILED=$((FAILED+1)); }
# 3. Unknown event type in the taxonomy path: the pair must roll back, no orphan record.
BEFORE_RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
CP_ROOT_SAVED="$CP_ROOT"
( export CP_ROOT="$(mktemp -d)"; mkdir -p "$CP_ROOT/metrics/taxonomy" "$CP_ROOT/schemas/records" "$CP_ROOT/tools/records"
  cp -R "$CP_ROOT_SAVED/tools/records/." "$CP_ROOT/tools/records/"
  cp -R "$CP_ROOT_SAVED/schemas/records/." "$CP_ROOT/schemas/records/" 2>/dev/null
  printf 'event_types: []\n' > "$CP_ROOT/metrics/taxonomy/event-types.yaml"
  "$CP_ROOT/tools/records/deploy-emit" record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1 ) 
AFTER_RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
[ "$BEFORE_RECS" = "$AFTER_RECS" ] || { echo "DEPLOY CASE FAIL orphan-record-after-event-failure"; FAILED=$((FAILED+1)); }
rm -rf "$SANDBOX"
if [ "$FAILED" != "0" ]; then echo "DEPLOY-EMIT FAIL $FAILED"; exit 1; fi
echo "DEPLOY-EMIT OK 6/6"
TDE_EOF
chmod +x "$CP_ROOT/tools/records/test-deploy-emit.sh"
git -C "$CP_ROOT" add tools/records/test-deploy-emit.sh
git -C "$CP_ROOT" commit -m "L4-T313: deploy emitter failure test - required failing step proved, pair rollback proved"
"$CP_ROOT/tools/records/test-deploy-emit.sh"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Test passes | `"$CP_ROOT/tools/records/test-deploy-emit.sh"` | `DEPLOY-EMIT OK 6/6`, exit 0 |
| 2 | The happy path produces exactly one record, one event, one commit | the three counts inside the test | no `DEPLOY CASE FAIL` line |
| 3 | An unwritable store makes the step exit non-zero | case 2 inside the test | no `unwritable-store-returned-zero` line |
| 4 | A failed event write leaves no orphan record (`emit_pair` rollback) | case 3 inside the test | no `orphan-record-after-event-failure` line |
| 5 | The real records repository is untouched | `git -C "$CPR_ROOT" status --porcelain \| wc -l` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
echo "RESULT=$("$CP_ROOT/tools/records/test-deploy-emit.sh" | tail -1)"
echo "CPRCLEAN=$(git -C "$CPR_ROOT" status --porcelain | wc -l | tr -d ' ')"
echo "CPRCOMMITS_STABLE=$(git -C "$CPR_ROOT" rev-list --count HEAD)"
```

Expected output, exactly:

```
RESULT=DEPLOY-EMIT OK 6/6
CPRCLEAN=0
CPRCOMMITS_STABLE=<the same number as before this task ran>
```

Record the commit count before running and compare; it must not change.

**STOP rule** — if `RESULT` is not `DEPLOY-EMIT OK 6/6`, fix `deploy-emit` or `lib/emit.sh`, never the test. In particular: if `orphan-record-after-event-failure` appears, `emit_pair`'s rollback is broken and a record can exist with no event, which is exactly the half-write §97.2 line 8871 forbids. If `CPRCLEAN` is not `0` or the commit count moved, the test escaped its sandbox. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T313 deploy emitter failure test failed or escaped its sandbox"
lane: L4
phase: 3
task_id: L4-T313
blocked_by: "<case failure | orphan record after event failure | real store written>"
observed: "<paste the exact SELF-VERIFY output and every DEPLOY CASE FAIL line>"
expected: "RESULT=DEPLOY-EMIT OK 6/6 / CPRCLEAN=0 / records-repo commit count unchanged"
spec_ref: "Master Spec v4.0 Section 97.2 lines 8867, 8871; Section 32 line 2827"
needs: "L0"
action_taken: "test expectations unmodified; nothing pushed"
```

---

### L4-T314 — The human review lane, declared

**Size:** M
**Depends on:** L4-T302
**Partially blocked by:** D-L4-P3-02. The document below states the open question verbatim and requests no protection change; write it exactly as given.

**Commands**

```bash
export CPR_ROOT="$HOME/src/control-plane-records"
cat > "$CPR_ROOT/CONTRIBUTING.md" <<'CONTRIB_EOF'
# Contributing to control-plane-records

This repository holds `records/**` and `events/**` and nothing else.
Master Spec v4.0 Section 97 (lines 8834-8991) and Section 40.1 (lines 3644-3686) govern it.

## The one rule

**Nobody edits a record file by hand to report a result.** (Section 97.2, line 8871.)

A manual result reaches this repository through **RECORD-VERIFICATION-RESULT** — a
`workflow_dispatch` with five structured inputs (product, item, mechanism, pass or fail,
evidence link) that writes the record and appends the event in one commit. Manual UAT and
verification results (Section 31.2, line 2790), restore-test confirmations (Section 44.3,
line 4008) and support-loop closures (Section 22.5, line 2256) all arrive this way.

If you find yourself opening a text editor on a file under `records/` to say that something
passed, failed, completed or was confirmed: stop. Use the dispatch.

## Records are never edited in place

Section 97.2, line 8890: a record never edits in place; **corrections are follow-up records**.
Invariant 48 (line 9516): historical records are never silently overwritten.
A pull request that modifies or deletes an existing file under `records/` or `events/` is
rejected by `tools/records/validate-human-record.sh` in the control-plane repository.

## Which stores accept a hand-authored record

Six stores accept hand-authored records, and only these six. Every other store is written by
a machine path and a hand-authored file there is rejected.

| Store | Who authors | Spec line |
| --- | --- | --- |
| `records/postmortems/` | Human, from template; closure tracked | 8848 |
| `records/decisions/` | Human, at the moment of decision (normally through the record-decision CLI) | 8852 |
| `records/security-reviews/` | Security reviewer, from template | 8856 |
| `records/demos/` | Human, brief, after each client demo or UAT walkthrough | 8859 |
| `records/onboarding/` | Onboarding workflow at phase completion; **human for judgment steps only** | 8861 |
| `records/leave/` | Founder or delegate on approval | 8862 |

Machine-written stores, for reference: incidents, uat, estimates, deployments, restore-tests,
decisions/pending, breaches, deletion-requests, eval, launches, support, and `events/`.
The full register with the writing actor and the write path for every store is
`tools/records/write-paths.yaml` in the control-plane repository.

## How to add a hand-authored record

1. Branch from the default branch.
2. Add **one new file** under the store's directory. Do not touch any existing file.
3. Every record carries `record_schema_version`, `id`, `product` and `timestamp`
   (Section 97.2, line 8890). Every timestamp is UTC **with its offset**
   (Section 97.1, line 8839) — for example `2026-08-27T09:31:04+00:00`.
4. Open a pull request. `validate-human-record.sh` runs against the diff.
5. A reviewer merges. Merges are fast-forward appends; the repository ruleset blocks
   force pushes, branch deletion and tag deletion, with no bypass actor (Section 40.1,
   line 3675, D107).

## Deployment operations

Accepted deviation: this repository uses `make deploy` and `make restore` for deployment operations (Q14=B). See `docs/decisions/D-L4-P3-03.md`.

## What lane L4 does not configure

L4 declares; it does not configure GitHub. The protection posture this repository requires is
recorded in `PROTECTION-REQUEST.md` for L0. No file exists under `.github/` here until charter
decision **D-L4-03** resolves.

## Commit signing

The records-writer signs every commit it makes on the default branch, and a default-branch
commit that is unsigned or signed by another identity is Blocking drift (Section 40.1,
line 3676). Configuring that identity is a credential matter, not something this file or any
L4 script performs.
CONTRIB_EOF
git -C "$CPR_ROOT" add CONTRIBUTING.md
git -C "$CPR_ROOT" commit -m "L4-T314: human review lane declared - six hand-authored stores, no hand-edited results"
git -C "$CPR_ROOT" log --oneline -1
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The file exists and states the one rule | `grep -c "Nobody edits a record file by hand to report a result" "$CPR_ROOT/CONTRIBUTING.md"` | `1` |
| 2 | Exactly six hand-authored stores listed | see SELF-VERIFY `HANDSTORES` | `6` |
| 3 | The six match the register's `hand_authored: true` rows | see SELF-VERIFY `MATCH` | `match` |
| 4 | The D-L4-P3-02 open question is recorded verbatim with both spec lines | `grep -c "8841" "$CPR_ROOT/CONTRIBUTING.md"; grep -c "3667" "$CPR_ROOT/CONTRIBUTING.md"` | `1` and `1` |
| 5 | The file requests no branch protection | `grep -c "requests no branch protection" "$CPR_ROOT/CONTRIBUTING.md"` | `1` |
| 6 | Nothing was created under `.github/` | `test -d "$CPR_ROOT/.github" && echo PRESENT \|\| echo ABSENT` | `ABSENT` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
C="$CPR_ROOT/CONTRIBUTING.md"
echo "ONERULE=$(grep -c 'Nobody edits a record file by hand to report a result' "$C")"
echo "HANDSTORES=$(grep -c '^| \`records/' "$C")"
python3 - <<'PY'
import os, re, yaml
cpr, cp = os.environ["CPR_ROOT"], os.environ["CP_ROOT"]
doc = open(os.path.join(cpr, "CONTRIBUTING.md"), encoding="utf-8").read()
listed = set(re.findall(r"^\| `records/([a-z/-]+)/`", doc, re.M))
reg = yaml.safe_load(open(os.path.join(cp, "tools", "records", "write-paths.yaml"), encoding="utf-8"))
declared = {r["store"] for r in reg["stores"] if r["hand_authored"]}
print("MATCH=%s" % ("match" if listed == declared else "MISMATCH listed=%s declared=%s" % (sorted(listed), sorted(declared))))
PY
echo "LINE8841=$(grep -c '8841' "$C")"
echo "LINE3667=$(grep -c '3667' "$C")"
echo "NOPROT=$(grep -c 'requests no branch protection' "$C")"
echo "DOTGITHUB=$(test -d "$CPR_ROOT/.github" && echo present || echo absent)"
```

Expected output, exactly:

```
ONERULE=1
HANDSTORES=6
MATCH=match
LINE8841=1
LINE3667=1
NOPROT=1
DOTGITHUB=absent
```

**STOP rule** — if `MATCH` is not `match`, `CONTRIBUTING.md` and `write-paths.yaml` disagree about which stores accept a hand-authored record. **Do not resolve it by editing whichever file is easier**; both were transcribed from §97.2 lines 8845–8866 and a divergence means one transcription is wrong. If `DOTGITHUB=present`, charter decision D-L4-03 has been pre-empted. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T314 human-lane store list disagrees with the write-path register"
lane: L4
phase: 3
task_id: L4-T314
blocked_by: "<store list mismatch | .github created | protection requested>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "ONERULE=1 / HANDSTORES=6 / MATCH=match / LINE8841=1 / LINE3667=1 / NOPROT=1 / DOTGITHUB=absent"
spec_ref: "Master Spec v4.0 Section 97.1 line 8841; Section 40.1 line 3667; Section 97.2 lines 8845-8866; PARTITION.md line 8"
needs: "L0 - decisions D-L4-P3-02 and D-L4-03"
action_taken: "neither file edited to force agreement; nothing pushed"
```

---

### L4-T315 — The no-hand-edit guard

**Size:** L
**Depends on:** L4-T302, L4-T314

The mechanical form of §97.2 line 8871's last clause. Runs against a pull-request diff on `control-plane-records` and rejects three things: a hand-authored file in a machine-written store, any modification of an existing record or event, and any deletion.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
cat > "$CP_ROOT/tools/records/validate-human-record.sh" <<'VHR_EOF'
#!/usr/bin/env bash
# tools/records/validate-human-record.sh
# The human review lane guard for control-plane-records.
# Master Spec v4.0 Section 97.2 line 8871 (nobody edits a record file by hand to report a
# result), line 8890 (never edits in place; corrections are follow-up records),
# invariant 47 line 9515 (append-only), invariant 48 line 9516 (no silent overwrite).
# Usage: validate-human-record.sh [<base-ref>]   default base-ref: origin/HEAD
set -u
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
BASE="${1:-origin/HEAD}"
DIFF="$(git -C "$CPR_ROOT" diff --name-status "$BASE"...HEAD)"
if [ -z "$DIFF" ]; then echo "HUMAN-RECORD OK 0 files"; exit 0; fi
# DF-0614 fix: `python3 - <<'PY'` makes the heredoc win on fd 0, so python3 reads the script
# from the heredoc but sys.stdin.read() inside the script returns empty — the piped DIFF is
# discarded. Fix: write the checker to a temp file and pipe DIFF into a named python3 call.
_VHR_PY="$(mktemp --suffix=.py)"
cat > "$_VHR_PY" <<'PY'
import sys, yaml
reg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
hand = {r["path"].rstrip("/") for r in reg["stores"] if r["hand_authored"]}
machine = {r["path"].rstrip("/") for r in reg["stores"] if not r["hand_authored"]}
errs, n = [], 0
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    parts = line.split("\t")
    status, path = parts[0][0], parts[-1]
    n += 1
    if not (path.startswith("records/") or path.startswith("events/")):
        continue
    if status in ("M", "R"):
        errs.append("in-place-edit %s (Section 97.2 line 8890: corrections are follow-up records)" % path)
        continue
    if status == "D":
        errs.append("deletion %s (invariant 47 line 9515: history is append-only)" % path)
        continue
    if status == "A":
        owner = None
        for d in sorted(hand | machine, key=len, reverse=True):
            if path.startswith(d + "/"):
                owner = d
                break
        if owner is None:
            errs.append("unknown-store %s" % path)
        elif owner in machine:
            errs.append("hand-authored-in-machine-store %s (Section 97.2 line 8871)" % path)
if errs:
    for e in errs:
        print("HUMAN-RECORD FAIL " + e)
    sys.exit(1)
print("HUMAN-RECORD OK %d files" % n)
PY
printf '%s\n' "$DIFF" | python3 "$_VHR_PY" "$CP_ROOT/tools/records/write-paths.yaml"
_VHR_RC=$?
rm -f "$_VHR_PY"
exit "$_VHR_RC"
VHR_EOF
chmod +x "$CP_ROOT/tools/records/validate-human-record.sh"
git -C "$CP_ROOT" add tools/records/validate-human-record.sh
git -C "$CP_ROOT" commit -m "L4-T315: no-hand-edit guard for the human review lane (Section 97.2 lines 8871, 8890)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Guard is executable | `test -x "$CP_ROOT/tools/records/validate-human-record.sh" && echo YES` | `YES` |
| 2 | A new file in a hand-authored store passes | see SELF-VERIFY `CASE_OK` | `HUMAN-RECORD OK 1 files` |
| 3 | A new file in a machine store is rejected | see SELF-VERIFY `CASE_MACHINE` | `HUMAN-RECORD FAIL hand-authored-in-machine-store records/uat/HANDMADE.yaml (Section 97.2 line 8871)` |
| 4 | An in-place edit of an existing record is rejected | see SELF-VERIFY `CASE_EDIT` | starts `HUMAN-RECORD FAIL in-place-edit` |
| 5 | A deletion is rejected | see SELF-VERIFY `CASE_DELETE` | starts `HUMAN-RECORD FAIL deletion` |
| 6 | The sandbox is removed and the real store is untouched | see SELF-VERIFY `CPRCLEAN` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT_REAL="$HOME/src/control-plane-records"
S="$(mktemp -d)"; cp -R "$CPR_ROOT_REAL/." "$S/"
export CPR_ROOT="$S"
git -C "$S" config user.email "t@test.invalid"; git -C "$S" config user.name "t"
G="$CP_ROOT/tools/records/validate-human-record.sh"
BASE="$(git -C "$S" rev-parse HEAD)"
printf 'record_schema_version: 1\nid: PM-2026-08-27-001\nproduct: demoprod\ntimestamp: 2026-08-27T09:00:00+00:00\n' > "$S/records/postmortems/PM-2026-08-27-001.yaml"
git -C "$S" add -A && git -C "$S" commit -q -m c1
echo "CASE_OK=$("$G" "$BASE" | tail -1)"
BASE2="$(git -C "$S" rev-parse HEAD)"
printf 'record_schema_version: 1\nid: HANDMADE\nproduct: demoprod\ntimestamp: 2026-08-27T09:00:00+00:00\n' > "$S/records/uat/HANDMADE.yaml"
git -C "$S" add -A && git -C "$S" commit -q -m c2
echo "CASE_MACHINE=$("$G" "$BASE2" | head -1)"
BASE3="$(git -C "$S" rev-parse HEAD)"
printf 'edited: true\n' >> "$S/records/postmortems/PM-2026-08-27-001.yaml"
git -C "$S" add -A && git -C "$S" commit -q -m c3
echo "CASE_EDIT=$("$G" "$BASE3" | head -1 | cut -d' ' -f1-3)"
BASE4="$(git -C "$S" rev-parse HEAD)"
git -C "$S" rm -q "records/uat/HANDMADE.yaml" && git -C "$S" commit -q -m c4
echo "CASE_DELETE=$("$G" "$BASE4" | head -1 | cut -d' ' -f1-3)"
rm -rf "$S"
echo "CPRCLEAN=$(git -C "$CPR_ROOT_REAL" status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
CASE_OK=HUMAN-RECORD OK 1 files
CASE_MACHINE=HUMAN-RECORD FAIL hand-authored-in-machine-store records/uat/HANDMADE.yaml (Section 97.2 line 8871)
CASE_EDIT=HUMAN-RECORD FAIL in-place-edit
CASE_DELETE=HUMAN-RECORD FAIL deletion
CPRCLEAN=0
```

**STOP rule** — if `CASE_MACHINE`, `CASE_EDIT` or `CASE_DELETE` does not begin `HUMAN-RECORD FAIL`, the guard cannot detect the violation it exists to detect, and §97.2 line 8871 has no mechanical enforcement anywhere in the estate. Do not relax any expectation. If `CPRCLEAN` is not `0`, the sandbox leaked into the real repository. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T315 no-hand-edit guard failed to reject a violation"
lane: L4
phase: 3
task_id: L4-T315
blocked_by: "<hand-authored machine-store file accepted | in-place edit accepted | deletion accepted | sandbox leaked>"
observed: "<paste the exact SELF-VERIFY output>"
expected: "CASE_OK=HUMAN-RECORD OK 1 files / CASE_MACHINE, CASE_EDIT and CASE_DELETE all begin HUMAN-RECORD FAIL / CPRCLEAN=0"
spec_ref: "Master Spec v4.0 Section 97.2 lines 8871, 8890; invariants 47 and 48, lines 9515-9516"
needs: "L0"
action_taken: "no expectation relaxed; nothing pushed"
```

---

### L4-T316 — Phase-3 coverage proof, rebase and lane PR

**Size:** M
**Depends on:** L4-T303, L4-T307, L4-T309, L4-T310, L4-T313, L4-T315

Proves the phase's central claim before it merges: **every store in the register has a declared writer, and every write path class has at least one working implementation or is explicitly delegated outside L4.**

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
[ -n "$CPR_ROOT" ] || { echo "ERROR: CPR_ROOT is not set"; exit 1; }
cat > "$CP_ROOT/tools/records/test-write-paths.sh" <<'TWP_EOF'
#!/usr/bin/env bash
# tools/records/test-write-paths.sh — Phase 3 coverage proof.
# Every Section 97.2 store has a declared writer and a reachable write path.
set -u
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
FAILED=0
run() { label="$1"; shift; if "$@" >/dev/null 2>&1; then :; else echo "COVERAGE FAIL $label"; FAILED=$((FAILED+1)); fi; }
run register     "$CP_ROOT/tools/records/validate-write-paths.sh"
run taxonomy     "$CP_ROOT/tools/records/validate-board-events.sh"
run rvr          "$CP_ROOT/tools/records/test-rvr.sh"
run deploy       "$CP_ROOT/tools/records/test-deploy-emit.sh"
IMPL_MISSING=$(python3 - "$CP_ROOT" <<'PY'
import os, sys, yaml
cp = sys.argv[1]
impl = {
    "machine-workflow":    ["tools/records/record-write", "tools/records/event-append"],
    "machine-board":       ["tools/records/board-emit", "tools/records/rqm-emit"],
    "machine-deploy":      ["tools/records/deploy-emit"],
    "rvr-dispatch":        ["tools/records/record-verification-result"],
    "human-review-lane":   ["tools/records/validate-human-record.sh"],
    "cli-record-decision": [],   # tool of subsystems A/O (Section 99.2 line 9217); not an L4 tool
}
reg = yaml.safe_load(open(os.path.join(cp, "tools", "records", "write-paths.yaml"), encoding="utf-8"))
missing = 0
for r in reg["stores"]:
    for cls in (r["write_path"], r["secondary_write_path"]):
        if not cls:
            continue
        if cls not in impl:
            print("no-implementation-map %s %s" % (r["store"], cls)); missing += 1; continue
        for f in impl[cls]:
            if not os.path.exists(os.path.join(cp, f)):
                print("missing-implementation %s %s %s" % (r["store"], cls, f)); missing += 1
print("MISSING=%d" % missing)
PY
)
echo "$IMPL_MISSING" | grep -v '^MISSING=' || true
N=$(echo "$IMPL_MISSING" | sed -n 's/^MISSING=//p')
if [ "$N" != "0" ]; then echo "COVERAGE FAIL implementations=$N"; FAILED=$((FAILED+1)); fi
if [ "$FAILED" != "0" ]; then echo "WRITE-PATH COVERAGE FAIL $FAILED"; exit 1; fi
echo "WRITE-PATH COVERAGE OK 19/19"  # 19 per FD-059 (bootstrap/ counts as a store)
TWP_EOF
chmod +x "$CP_ROOT/tools/records/test-write-paths.sh"
git -C "$CP_ROOT" add tools/records/test-write-paths.sh
git -C "$CP_ROOT" commit -m "L4-T316: Phase 3 write-path coverage proof"
"$CP_ROOT/tools/records/test-write-paths.sh"
git -C "$CP_ROOT" fetch --all --prune
git -C "$CP_ROOT" rebase origin/integration
[ -n "$CP_ROOT" ] || { echo "ERROR: CP_ROOT is not set"; exit 1; }
cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths
[ -n "$CP_ROOT" ] || { echo "ERROR: CP_ROOT is not set"; exit 1; }
cd "$CP_ROOT" && ./tools/records/test-write-paths.sh
git -C "$CP_ROOT" push -u origin lane/4/03-write-paths
[ -n "$CPR_ROOT" ] || { echo "ERROR: CPR_ROOT is not set"; exit 1; }
git -C "$CPR_ROOT" push -u origin lane/4/03-write-paths
gh pr create --base integration --head lane/4/03-write-paths \
  --title "L4-03: how records get written (Section 97.2 write paths)" \
  --body "L4 Phase 3, tasks L4-T301..L4-T316. Owned paths only: tools/records/** in control-plane, CONTRIBUTING.md in control-plane-records. Declares one writer and one write path per Section 97.2 store; implements the RECORD-VERIFICATION-RESULT dispatch handler, the board-automation emitters, the deploy required-failing-step emitter and the no-hand-edit guard. Open decisions for L0: D-L4-P3-01, D-L4-P3-02, D-L4-P3-03 (see Code/implementation/lanes/L4-03-write-paths.md section 5), plus charter decisions D-L4-01, D-L4-02, D-L4-03."
gh pr create --repo "$(basename "$CPR_ROOT")" --base main --head lane/4/03-write-paths \
  --title "L4-03: records CONTRIBUTING.md (Section 97.2 no-hand-edit guard)" \
  --body "L4 Phase 3 records repository change: adds CONTRIBUTING.md no-hand-edit guard to control-plane-records. Companion to control-plane PR lane/4/03-write-paths. Closes D-L4-03."
gh pr view --json number,baseRefName,headRefName
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Coverage proof passes | `"$CP_ROOT/tools/records/test-write-paths.sh"` | `WRITE-PATH COVERAGE OK 19/19`, exit 0 | <!-- 19 per FD-059 (bootstrap/ counts as a store) -->
| 2 | Lane path guard passes after rebase | `cd "$CP_ROOT" && ./tools/records/lane-selfcheck.sh --paths` | `PATHS OK` |
| 3 | Only `tools/records/` changed in `control-plane` | `git -C "$CP_ROOT" diff --name-only origin/integration...HEAD \| grep -vc '^tools/records/'` | `0` |
| 4 | Only `CONTRIBUTING.md` was added in `control-plane-records` this phase | see SELF-VERIFY `CPRADDED` | `CONTRIBUTING.md` |
| 5 | PR base is `integration`, head is the phase branch | `gh pr view --json baseRefName,headRefName` | `integration`, `lane/4/03-write-paths` |
| 6 | No other lane's branch was touched | `git -C "$CP_ROOT" reflog --date=short \| grep -cE 'lane/(1|2|3|5)/'` | `0` |

**SELF-VERIFY**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
[ -n "$CP_ROOT" ] || { echo "ERROR: CP_ROOT is not set"; exit 1; }
cd "$CP_ROOT"
echo "COVERAGE=$(./tools/records/test-write-paths.sh | tail -1)"
echo "PATHS=$(./tools/records/lane-selfcheck.sh --paths)"
echo "FOREIGN=$(git diff --name-only origin/integration...HEAD | grep -vc '^tools/records/')"
echo "CPRADDED=$(git -C "$CPR_ROOT" show --name-only --format= HEAD | tr -d '\r' | tr '\n' ',' | sed 's/,$//')"
echo "BASE=$(gh pr view --json baseRefName -q .baseRefName)"
echo "HEAD=$(gh pr view --json headRefName -q .headRefName)"
echo "OTHERLANES=$(git reflog --date=short | grep -cE 'lane/(1|2|3|5)/')"
```

Expected output, exactly:

```
COVERAGE=WRITE-PATH COVERAGE OK 19/19
PATHS=PATHS OK
FOREIGN=0
CPRADDED=CONTRIBUTING.md
BASE=integration
HEAD=lane/4/03-write-paths
OTHERLANES=0
```

**STOP rule** — if `COVERAGE` is not `WRITE-PATH COVERAGE OK 19/19`, read the `COVERAGE FAIL` and `missing-implementation` lines; a store with no reachable writer is precisely the evidence-plumbing gap of §99.6 risk 2 (lines 9276–9294) and must not merge. If `FOREIGN` is not `0` or `OTHERLANES` is not `0`, the lane-guard check will fail the PR — do not force-push and do not resolve another lane's conflict. Open a blocker issue:

```yaml
title: "[L4-BLOCKER] L4-T316 Phase 3 coverage or lane-guard preconditions failed"
lane: L4
phase: 3
task_id: L4-T316
blocked_by: "<store with no reachable writer | foreign path | another lane's branch touched | rebase failed>"
observed: "<paste the exact SELF-VERIFY output and every COVERAGE FAIL line>"
expected: "COVERAGE=WRITE-PATH COVERAGE OK 19/19 / PATHS=PATHS OK / FOREIGN=0 / CPRADDED=CONTRIBUTING.md / BASE=integration / HEAD=lane/4/03-write-paths / OTHERLANES=0" # 19 per FD-059 (bootstrap/ counts as a store)
spec_ref: "Master Spec v4.0 Section 99.6 risk 2 lines 9276-9294; Section 97.2 lines 8845-8871; PARTITION.md lines 25, 32-36"
needs: "L0"
action_taken: "no force-push, no merge, no other-lane branch modified"
```

---

## 7. Task summary

| Task ID | Title | Size | Depends on | Files written |
|---|---|---|---|---|
| L4-T301 | Phase-3 preflight and phase branch | S | — | none (branch + directories) |
| L4-T302 | The write-path register | M | L4-T301 | `tools/records/write-paths.yaml` |
| L4-T303 | Write-path register validator | M | L4-T302 | `tools/records/validate-write-paths.sh` |
| L4-T304 | RVR input contract | M | L4-T302 | `tools/records/dispatch/rvr-inputs.yaml` |
| L4-T305 | Emission library | L | L4-T301 | `tools/records/lib/emit.sh`, `tools/records/lib/validate_instance.py`, guarded `record-write`, `event-append` |
| L4-T306 | RVR handler | L | L4-T304, L4-T305 | `tools/records/record-verification-result` |
| L4-T307 | RVR test harness (DoD-9) | M | L4-T306 | `tools/records/test-rvr.sh` |
| L4-T308 | Board-event emission contract | M | L4-T302 | `tools/records/dispatch/board-events.yaml` |
| L4-T309 | Board and Ready-queue-miss emitters | L | L4-T305, L4-T308 | `tools/records/board-emit`, `tools/records/rqm-emit` |
| L4-T310 | Taxonomy conformance check | M | L4-T304, L4-T308 | `tools/records/validate-board-events.sh` |
| L4-T311 | Deploy required-step contract | M | L4-T302 | `tools/records/dispatch/deploy-steps.yaml` |
| L4-T312 | Deploy emitter | L | L4-T305, L4-T311 | `tools/records/deploy-emit` |
| L4-T313 | Deploy emitter failure test | M | L4-T312 | `tools/records/test-deploy-emit.sh` |
| L4-T314 | Human review lane declared | M | L4-T302 | `control-plane-records/CONTRIBUTING.md` |
| L4-T315 | No-hand-edit guard | L | L4-T302, L4-T314 | `tools/records/validate-human-record.sh` |
| L4-T316 | Coverage proof, rebase, lane PR | M | T303, T307, T309, T310, T313, T315 | `tools/records/test-write-paths.sh` |

**Sizes:** 1 × S, 9 × M, 6 × L.

---

## 8. What Phase 3 hands to the other lanes

| Artifact | Consumer | Consumed as |
|---|---|---|
| `tools/records/dispatch/rvr-inputs.yaml` | **L2** | The `workflow_dispatch` `inputs:` block of the RECORD-VERIFICATION-RESULT workflow L2 owns under `.github/workflows/` |
| `tools/records/record-verification-result` | **L2** | The handler that workflow calls |
| `tools/records/dispatch/deploy-steps.yaml` | **L2** | The eight required, failing steps `deploy-production.yml` must run (§97.2, line 8867) |
| `tools/records/deploy-emit` | **L2** | The emitter those steps call |
| `tools/records/dispatch/board-events.yaml`, `board-emit`, `rqm-emit` | **L2** | The board-automation emission surface |
| `tools/records/write-paths.yaml` | **L3** | The declared writer per store, beside the write-freshness windows the §53.1 drift row (line 4671) compares against |
| `tools/records/validate-human-record.sh`, `validate-write-paths.sh`, `validate-board-events.sh` | **L0** | Status checks for the gate |
| `control-plane-records/CONTRIBUTING.md` | everyone | The human lane, and the D-L4-P3-02 open question |

---

## 9. Standing rules — this phase only

The lane charter's §12 applies in full. Four rules bind this phase in particular:

1. **`emit.sh` is the only writer.** No task in this phase, and no later task, writes a file under `records/` or `events/` by any other means. Two writers for one store is the divergence §97.1 line 8838 exists to prevent.
2. **A record and its event are one commit.** `emit_pair` writes both or neither (§97.2, line 8871). Never call `emit_record` alone from an emitter.
3. **Never invent an `event_type`.** §97.3 line 8947 makes a new identifier a governed addition to the enum in `registries/platform.yaml`, which is L1's file (charter §3.1). An identifier that fails `validate-board-events.sh` is a blocker for L0, never a taxonomy edit.
4. **Never weaken a required failing step.** `continue-on-error`, `|| true` and `set +e` are absent from every emitter by design (§97.2, line 8867). Restoring a green build by adding one converts a Blocking evidence failure into an invisible one — the exact failure mode §99.6 risk 2 (lines 9276–9294) names.
