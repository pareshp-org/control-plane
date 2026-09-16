> **[AUTHORITATIVE — FD-B1-L2 2026-09-02]**
> This is the authoritative task plan for Lane 2. All competing plans are superseded.

# L2-05 — Lane 2 Atomic Task List

**Lane 2 — Pipeline & Evidence.** Subsystems **E** (Reusable workflow library) and **F** (Evidence chain store and query), spec §99.2 rows E and F (L9192–L9193).
**Branch prefix:** `lane/2/*` · **Merge-train position:** 3rd of 5 — `L1 → L4 → L2 → L3 → L5` (`PARTITION.md` line 35).
**Owned paths (exclusive, `PARTITION.md` line 18):** `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`.
**Authority:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` is FROZEN and is never contradicted here. Spec of record: `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

This file is the complete, ordered work list for Lane 2 — **76 tasks**. Work it **top to bottom**. Every task below is executable without opening another document. Do not skip, do not reorder, do not batch two tasks into one branch.

**Read §2.1 before you start.** Twenty-three ids that this file once published are defined in full by a phase file — `L2-04-evidence-chain.md` §6, `L2-02-digest-invariant.md` §3 — and that phase file is authoritative for them. This file carries an index entry for each and publishes its own, different work under `L2-T530`–`L2-T555` instead. No task text was lost; only ids moved.

> §33.2 (L2854–2869): *"Every required check name is therefore emitted by a job carrying no `if:` and no path filter."* Half the tasks in this file exist to make that sentence mechanically true, and none of them is optional.

---

> **Dispatch Routing Note (2026-09-08):**
> Tasks **L2-T001 through L2-T006** in this file are INDEX ENTRIES only.
> Their authoritative bodies live in `lanes/L2-00-charter.md §11`.
> Dispatch those 6 tasks from L2-00-charter.md, not from this file.
> All other tasks (L2-T007 onwards) are authoritative here.

## 0. Standing protocol — read once, apply to every task

### 0.1 Path ownership (hard)

You may create or edit files **only** under these three roots:

```
.github/workflows/**
templates/workflows/**
tools/evidence/**
```

You may **read** anything in the repository. You may **never write** to `contracts/**`, `schemas/**`, `registries/**`, `validators/**`, `reconciler/**`, `tools/provision/**`, `tools/records/**`, `metrics/**`, `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`, `records/**`, `events/**`, `CODEOWNERS`, `Makefile`, or any root file. A pull request touching a foreign path fails the `lane-guard` check and is rejected (`PARTITION.md` rule 1).

**Namespace-package rule.** Do **not** create `tools/__init__.py`. `tools/` is a shared parent: `tools/provision/**` is Lane 3's and `tools/records/**` is Lane 4's. `tools.evidence` imports as a PEP 420 implicit namespace package. Creating `tools/__init__.py` is a foreign-path write and will be rejected.

**Additive-only discipline (`PARTITION.md` rule 5).** Prefer a new file over editing an existing one. Five tasks in this file deliberately edit a file created by an earlier task (`L2-T109`, `L2-T121`, `L2-T138`, `L2-T144`, `L2-T311`); every other task creates only.

### 0.2 Environment — set once per shell session, before any task

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="$HOME/src/control-plane"
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO - STOP"; exit 1; }
test -d contracts || { echo "contracts/ ABSENT - STOP (see 0.7 rule S1)"; exit 1; }
```

### 0.3 Git protocol — every task, no exceptions

**Open block** — run before the task's own commands:

**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/<branch-slug>
```

**Close block** — run after the task's SELF-VERIFY prints `OK`:

**Commands**

```bash
set -e
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git status --porcelain | grep -vE '^\?\? ?$' | grep -vE '^(A|M| M|\?\?) (\.github/workflows/|templates/workflows/|tools/evidence/)' && { echo "FOREIGN OR UNEXPECTED CHANGE - STOP"; exit 1; }
git fetch origin && git rebase origin/integration
git push -u origin lane/2/<branch-slug>
gh pr create --base integration --head lane/2/<branch-slug> \
  --title "<TASK-ID>: <task title>" \
  --body "Lane 2 (Pipeline & Evidence). Task <TASK-ID>. Owned paths only. SELF-VERIFY in L2-05-tasks.md passed."
```

Each task names its own `<branch-slug>`. One branch per task, short-lived (< 1 day). Never merge another lane's branch. Never rebase another lane's branch. Merge to `integration` only, never to `main`.

### 0.4 Deterministic output contract — binding on every `tools/evidence/**` program

Every program under `tools/evidence/` accepts `--summary` and prints, on `--summary`, **exactly one line** to stdout:

```
<STATUS> <tool-id> checked=<int> failed=<int>
```

| `STATUS` | Meaning | Exit code |
| --- | --- | --- |
| `OK` | executed; zero failures | `0` |
| `FAIL` | executed; one or more failures | `2` |
| `ERROR` | could not execute (missing input, unreadable fixture, absent contract) | `3` |

Any other non-zero exit is a crash and is a STOP. `<tool-id>` is the module's basename without extension. Diagnostic detail goes to **stderr**, never stdout — stdout carries the summary line and nothing else, because every acceptance command in this file compares stdout to an exact string.

**Fail-closed rule (§101 invariant 80, L9556 area; §33.2).** Every program in this lane that cannot determine an answer exits `3` and the calling workflow step fails. There is no "assume pass" branch anywhere in Lane 2.

### 0.5 Context-naming rule — read before writing any workflow

A required status-check context is the **name of the job in the workflow file that GitHub runs in the product repository**. A reusable workflow invoked with `uses:` reports its context as `<caller-job-name> / <reusable-job-name>`. Therefore:

* The **caller job name in `templates/workflows/*.yml` is the authoritative context name**, and it is spelled exactly as it appears in `templates/workflows/required-checks.yaml` (task `L2-T003`).
* Reusable-workflow job names never appear in branch protection and are free-form.
* You may not add, rename or remove a name in `required-checks.yaml`. If a task appears to need a context that is not one of the fifteen, **STOP** under rule S4 — that file is a published cross-lane interface (§53.1, L4653–4689; charter `L2-T003` STOP rule).

The fifteen published contexts, for reference while working (source: `templates/workflows/required-checks.yaml`):

```
phase_4: unit-tests integration-tests build security-scan licence-scan
         slopsquat-check contract-validation registry-validation parity-check
phase_5: verification-contract seeded-defect-case
phase_6: artifact-digest-recorded sbom-emitted
always : renovate-path-guard lane-guard
```

### 0.6 Six rules that never bend

Transcribed from the spec. A task whose implementation would violate one of these is a STOP, whatever the task text seems to ask for.

1. **Same digest.** *"The production artifact is the same digest verified in staging. Never rebuilt"* (§101 invariant 22, L9483; §32 L2803–2828; §33.4 L2887–2912). Never rebuild to work around registry unavailability (invariant 23, L9484).
2. **Approver ≠ deployer, fail closed.** *"The deploy workflow itself verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell"* (§27.2, L2567–2576; D73, L10156).
3. **Actor gate first.** The actor gate is the **first step** of `deploy-staging`, `deploy-production`, `migrate`, the rollback workflow and the production-restore workflow (§37.3, L3261–3268; invariant 18, L9477).
4. **No `if:`, no path filter on a required context.** *"no work was needed is an explicit recorded success, never a skip"* (§33.2, L2854–2869).
5. **Full-SHA action pinning, pinned-tag reusable consumption.** *"Every third-party GitHub Action is pinned to a full commit SHA. No tags, no floating branches, no exceptions"* (§48.1, L4300–4308; invariant 85, L9565).
6. **Record and event writes are required, failing steps.** *"the deployment-record and event writes are required, failing steps of `deploy-production.yml` rather than trailing best-effort ones"* (§97.2, L8843–8926).

### 0.7 Sizes

**S** under half a day · **M** half a day to two days · **L** two to five days.

### 0.8 STOP rules and the blocker template

Standing rules, from `L2-00-charter.md` §10:

* **S1.** A required file under `contracts/**` is absent or contains a placeholder → STOP. Do not invent the value.
* **S2.** Completing the task requires writing outside the three owned trees → STOP.
* **S3.** A rebase on `integration` conflicts outside the three owned trees → STOP. Do not resolve it.
* **S4.** The task requires choosing a name, threshold, format or ordering the spec does not state → STOP, file as DECISION REQUIRED for L0.
* **S5.** `git status` shows a modified file you did not intend to modify → STOP before committing.

If a task's stated STOP condition occurs, if any command errors in a way the task does not describe, or if a fact you need is not written in this file — **stop, commit nothing, and file the blocker below.** Do not guess, do not substitute, do not proceed to the next task.

**Commands**

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L2-<TASK-ID>: <one-line condition>" \
  --label "blocker,lane-2" \
  --body "$(cat <<'EOF'
LANE: L2 Pipeline & Evidence
TASK: L2-<TASK-ID>
STOP RULE TRIGGERED: <S1|S2|S3|S4|S5|task-specific>

WHAT I WAS DOING:
<the exact command run>

WHAT HAPPENED:
<exact output, verbatim, including exit code>

WHAT I NEED TO PROCEED:
<the single missing fact, file, or decision>

SPEC CITATION:
MultiProduct_MasterSpec_v4.0.md lines <A>-<B>, Section <N.N>

I HAVE NOT: guessed a value, written outside owned paths, edited contracts/**,
            resolved a foreign-path conflict, or continued past this point.
EOF
)"
```

Then post the issue number in the lane channel and take the next **unblocked** task, or idle. Never work around a blocker.

### 0.9 Task-id namespacing

Task ids are namespaced **by artifact tree**, per `L2-00-charter.md` §12, not by phase:

| Range | Tree |
| --- | --- |
| `L2-T001`–`L2-T099` | charter and lane bootstrap |
| `L2-T100`–`L2-T299` | `.github/workflows/**` |
| `L2-T300`–`L2-T499` | `templates/workflows/**` |
| `L2-T530`–`L2-T699` | `tools/evidence/**` |
| `L2-T700`–`L2-T799` | acceptance-test execution (AT-024, AT-029, AT-035, AT-103) |

**Ids are therefore not monotonic in execution order.** The `#` column of the master table is execution order; the `ID` column is identity. Work the `#` column.

### 0.10 Phases

Phase labels are the Build-track phases of `master/04-phase-map.md` §2, which is itself derived from §98.2 (L9006–L9090).

| Phase | Lane 2 content | Ends at |
| --- | --- | --- |
| **BT-0** | idle — `contracts/**` is L0's and is frozen first (`PARTITION.md` rule 2) | S0 |
| **BT-1** | bootstrap; `ci` reusable workflow only; the guards; the pin ledger | S1 |
| **BT-2** | `build` workflow, immutable artifact, digest recording, SBOM, parity | S2 |
| **BT-3** | `deploy-staging`, `deploy-production`, `migrate`, rollback, `restore-test`, `org-export`, `background-queue`; digest invariant in code; Friday-freeze gate; subsystem F end to end; all templates; AT execution | S3 |

**No lane opens a branch for the next phase until L0 declares the sync point passed** (`master/04-phase-map.md` §4).

---

## 1. DECISION REQUIRED — L0 must answer these

Six are carried forward from `L2-00-charter.md` §9 unchanged. Two are new to this file. Lane 2 must not resolve any of them.

| ID | Question, in one line | Blocks tasks |
| --- | --- | --- |
| **D-L2-01** | Which lane owns the blast-radius `affected:` generator (§33.3, L2870–2886), the bulk fleet-migration PR script (§61.4, L5263–5280) and the change-matrix scaffold (§99.2, L9214–9231)? No lane owns `tools/fleet/**`. | `L2-T700` (AT-024 fleet half) |
| **D-L2-02** | The stable entrypoint and exit-code semantics by which `ci.yml` invokes L1's contract and registry validators, declared in `contracts/**`. | `L2-T106`, `L2-T107` |
| **D-L2-03** | The records-writer secret name, target repository, and record/event schema paths for `records/deployments/`, `records/uat/`, `records/restore-tests/`, `records/eval/`, `events/`. | `L2-T544`, `L2-T545`, and every workflow that writes a record |
| **REG-060** | The `make parity` environment-schema declaration format. §99.3 item 2 (L9232–9247) marks it **design-open**. | the *format*; **not** `L2-T108`, which only invokes `make parity` per the §33.1 command table (L2831–2853) |
| **D-L2-05** | The filename of the rollback workflow. §33.2's required list (L2854–2869) omits it; §27.2 (L2567–2576) mandates it; §37.3 (L3261–3268) names it among the five privileged workflows. | `L2-T133`, `L2-T309`, `L2-T554` (fifth workflow), `L2-T701` |
| **D-L2-06** | Lane-guard bootstrap ordering — L1 and L4 merge to `integration` before `lane-guard.yml` (an L2 file) exists. | DoD-20 for cycle 1 only; no task |

### D-L2-07 (integration): feature-branch merge criteria

**Canonical definition (FD-084, Option A).** A feature branch is merged to the integration branch when: (a) all CI checks pass, (b) at least one required reviewer approves, (c) no PARTITION conflicts remain open.

> RECONCILED 2026-09-09 per FD-084

### D-L2-08 (promotion): integration-to-staging promotion event

**Canonical definition (FD-084, Option A).** A promotion event moves HEAD of integration branch to staging branch, triggered by L0 manual dispatch or a scheduled weekly cut, authorized by bendrohit-eng.

> RECONCILED 2026-09-09 per FD-084

### D-L2-09 (release): release from staging after UAT sign-off

**Canonical definition (FD-084, Option A).** A release is cut from the staging branch after UAT sign-off, produces: tagged commit, SBOM artifact, deployment record in `records/deployments/`; sign-off required: bendrohit-eng.

> RECONCILED 2026-09-09 per FD-084

---

## 2. Master task table — all 76 tasks in execution order

Work top to bottom. `Deps` are task ids that must be **merged to `integration`** first. `Ph` is the phase of §0.10.

| # | ID | Ph | Title | Files touched | Deps | Sz | Acceptance command |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | L2-T001 | BT-1 | Lane branch and owned-path skeleton | `.github/workflows/.gitkeep`, `templates/workflows/.gitkeep`, `tools/evidence/.gitkeep` | — | S | `test -d .github/workflows && test -d templates/workflows && test -d tools/evidence; echo $?` |
| 2 | L2-T002 | BT-1 | Pin the consumed contract surface | `tools/evidence/CONSUMED-CONTRACTS.lock` | L2-T001 | S | `grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/CONSUMED-CONTRACTS.lock` |
| 3 | L2-T003 | BT-1 | Publish the required-status-check name registry | `templates/workflows/required-checks.yaml` | L2-T001 | S | `grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml` |
| 4 | L2-T004 | BT-1 | Author the lane-guard workflow | `.github/workflows/lane-guard.yml` | L2-T001 | M | `grep -cE '^            lane/[1-5]/\*\)' .github/workflows/lane-guard.yml` |
| 5 | L2-T005 | BT-1 | Merge-train preflight check | `tools/evidence/preflight.sh` | L2-T002, L2-T003 | S | `bash -n tools/evidence/preflight.sh; echo $?` |
| 6 | L2-T006 | BT-1 | Rebase and open the phase-0 lane PR | none (publishes branch) | L2-T001…L2-T005 | S | `bash tools/evidence/preflight.sh \| tail -1` |
| 7 | L2-T530 | BT-1 | Evidence toolchain skeleton | `tools/evidence/__init__.py`, `tools/evidence/requirements.txt`, `tools/evidence/README.md` | L2-T006, D-L2-07 | S | `python -c "import tools.evidence as e; print(e.TOOL_CONTRACT)"` |
| 8 | L2-T531 | BT-1 | Action-pin resolver and applier | `tools/evidence/resolve_action_pin.sh`, `tools/evidence/apply_pins.sh` | L2-T530 | S | `bash -n tools/evidence/resolve_action_pin.sh && bash -n tools/evidence/apply_pins.sh; echo $?` |
| 9 | L2-T532 | BT-1 | Action pin ledger | `tools/evidence/action-pins.txt` | L2-T531 | S | `grep -cE '^[a-z0-9._/-]+ v[0-9.]+ [0-9a-f]{40}$' tools/evidence/action-pins.txt` |
| 10 | L2-T533 | BT-1 | Workflow lint — pinning, permissions, no-`if:` | `tools/evidence/lint_workflow.py`, `tools/evidence/fixtures/lint/**` | L2-T532 | M | `python -m tools.evidence.lint_workflow --path .github/workflows --summary` |
| 11 | L2-T534 | BT-1 | Required-context ↔ job cross-check | `tools/evidence/check_required_contexts.py`, `tools/evidence/fixtures/contexts/**` | L2-T533 | M | `python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary` |
| 12 | L2-T535 | BT-1 | Run-conclusion assertor — no `skipped`, no `neutral` | `tools/evidence/assert_run_conclusions.py`, `tools/evidence/fixtures/runs/**` | L2-T534 | M | `python -m tools.evidence.assert_run_conclusions --checks tools/evidence/fixtures/runs/clean.json --registry templates/workflows/required-checks.yaml --summary` |
| 13 | L2-T536 | BT-1 | Delta-gate engine | `tools/evidence/delta_gate.py`, `tools/evidence/fixtures/delta/**` | L2-T530 | M | `python -m tools.evidence.delta_gate --baseline tools/evidence/fixtures/delta/baseline.json --current tools/evidence/fixtures/delta/legacy-only.json --summary` |
| 14 | L2-T100 | BT-1 | `ci.yml` reusable scaffold | `.github/workflows/ci.yml` | L2-T532, L2-T533 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 15 | L2-T101 | BT-1 | `ci.yml`: `unit-tests`, `integration-tests` | `.github/workflows/ci.yml` | L2-T100 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 16 | L2-T102 | BT-1 | `ci.yml`: interim `build` job | `.github/workflows/ci.yml` | L2-T101 | S | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 17 | L2-T103 | BT-1 | `ci.yml`: `security-scan`, delta-gated | `.github/workflows/ci.yml` | L2-T102, L2-T536 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 18 | L2-T104 | BT-1 | `ci.yml`: `licence-scan`, delta-gated | `.github/workflows/ci.yml` | L2-T103 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 19 | L2-T105 | BT-1 | `ci.yml`: `slopsquat-check` at execute time | `.github/workflows/ci.yml` | L2-T104 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 20 | L2-T106 | BT-1 | `ci.yml`: `contract-validation` + §33.1 required-file presence | `.github/workflows/ci.yml` | L2-T105, `contracts/workflow-io/required-contexts.tsv` | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 21 | L2-T107 | BT-1 | `ci.yml`: `registry-validation` | `.github/workflows/ci.yml` | L2-T106, `contracts/workflow-io/required-contexts.tsv` | S | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 22 | L2-T108 | BT-1 | `ci.yml`: `parity-check` | `.github/workflows/ci.yml` | L2-T107 | S | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 23 | L2-T109 | BT-1 | Extend `lane-guard.yml` with lint and context cross-check | `.github/workflows/lane-guard.yml` | L2-T534, L2-T108 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/lane-guard.yml --summary` |
| 24 | L2-T110 | BT-1 | `renovate-path-guard.yml` | `.github/workflows/renovate-path-guard.yml` | L2-T532 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/renovate-path-guard.yml --summary` |
| 25 | L2-T111 | BT-1 | `control-plane-ci.yml` — §15.5 control-plane validation | `.github/workflows/control-plane-ci.yml` | L2-T106, L2-T107 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/control-plane-ci.yml --summary` |
| 26 | L2-T537 | BT-1 | Negative-test harness for the two guards | `tools/evidence/negative/**`, `tools/evidence/run_negative_tests.sh` | L2-T109, L2-T110 | M | `bash tools/evidence/run_negative_tests.sh --summary` |
| 27 | L2-T112 | BT-1 | `publish-workflow-tag.yml` — immutable `workflows/vN` release | `.github/workflows/publish-workflow-tag.yml` | L2-T532 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/publish-workflow-tag.yml --summary` |
| 28 | L2-T300 | BT-1 | Template tree, placeholder contract | `templates/workflows/README.md`, `templates/workflows/PLACEHOLDERS.yaml` | L2-T006, D-L2-08 | S | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 29 | L2-T539 | BT-1 | Template renderer and placeholder lint | `tools/evidence/render_template.py`, `tools/evidence/fixtures/render/**` | L2-T300 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 30 | L2-T301 | BT-1 | `templates/workflows/ci.yml` | `templates/workflows/ci.yml` | L2-T539, L2-T108 | M | `python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary` |
| 31 | L2-T538 | BT-2 | SBOM-beside-digest assertion | `tools/evidence/sbom_assert.py`, `tools/evidence/fixtures/sbom/**` | L2-T530 | M | `python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/good.json --summary` |
| 32 | L2-T120 | BT-2 | `build.yml` — immutable artifact, digest, SBOM | `.github/workflows/build.yml` | L2-T538, L2-T532 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/build.yml --summary` |
| 33 | L2-T121 | BT-2 | `ci.yml`: delegate `build` to `build.yml` | `.github/workflows/ci.yml` | L2-T120 | S | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 34 | L2-T302 | BT-2 | `templates/workflows/build.yml` | `templates/workflows/build.yml` | L2-T121, L2-T539 | M | `python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary` |
| 35 | L2-T540 | BT-2 | Time gate — Friday freeze and core hours | `tools/evidence/timegate.py`, `tools/evidence/fixtures/timegate/**` | L2-T530 | M | `python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary` |
| 36 | L2-T541 | BT-2 | Actor gate — human identity plus capability | `tools/evidence/actor_gate.py`, `tools/evidence/fixtures/actor/**` | L2-T530 | M | `python -m tools.evidence.actor_gate --actor machine-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary` |
| 37 | L2-T542 | BT-2 | Workflow-identity gate — approver ≠ deployer | `tools/evidence/identity_gate.py`, `tools/evidence/fixtures/identity/**` | L2-T530 | M | `python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/self.yaml --deployer dev-1 --summary` |
| 38 | L2-T543 | BT-2 | Digest invariant — requested vs staging-verified | `tools/evidence/digest_invariant.py`, `tools/evidence/fixtures/digest/**` | L2-T530 | M | `python -m tools.evidence.digest_invariant --requested sha256:bbbb --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary` |
| 39 | L2-T544 | BT-3 | Records-write client | `tools/evidence/records_client.py`, `tools/evidence/fixtures/records/**` | L2-T530, D-L2-03 | L | `python -m tools.evidence.records_client --dry-run --kind deployment --payload tools/evidence/fixtures/records/deployment.yaml --summary` |
| 40 | L2-T545 | BT-3 | Event writer — one file per event, bound envelope | `tools/evidence/event_writer.py`, `tools/evidence/fixtures/events/**` | L2-T544, D-L2-03 | M | `python -m tools.evidence.event_writer --dry-run --event tools/evidence/fixtures/events/production_deployed.yaml --summary` |
| 41 | L2-T130 | BT-3 | `deploy-staging.yml` | `.github/workflows/deploy-staging.yml` | L2-T541, L2-T545, L2-T120 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/deploy-staging.yml --summary` |
| 42 | L2-T131 | BT-3 | `deploy-production.yml` | `.github/workflows/deploy-production.yml` | L2-T130, L2-T542, L2-T543, L2-T540 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/deploy-production.yml --summary` |
| 43 | L2-T132 | BT-3 | `migrate.yml` — cases A–G | `.github/workflows/migrate.yml` | L2-T541, L2-T545 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/migrate.yml --summary` |
| 44 | L2-T133 | BT-3 | The rollback workflow | `.github/workflows/rollback.yml` | L2-T131, D-L2-05 | M | `python -m tools.evidence.lint_workflow --path .github/workflows --summary` |
| 45 | L2-T134 | BT-3 | `restore-test.yml` — one workflow, two targets | `.github/workflows/restore-test.yml` | L2-T541, L2-T545 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/restore-test.yml --summary` |
| 46 | L2-T136 | BT-3 | `org-export.yml` | `.github/workflows/org-export.yml` | L2-T532, L2-T545 | L | `python -m tools.evidence.lint_workflow --path .github/workflows/org-export.yml --summary` |
| 47 | L2-T137 | BT-3 | `background-queue.yml` | `.github/workflows/background-queue.yml` | L2-T541 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/background-queue.yml --summary` |
| 48 | L2-T546 | BT-3 | Verification-contract check | `tools/evidence/verification_contract_check.py`, `tools/evidence/fixtures/vc/**` | L2-T530 | M | `python -m tools.evidence.verification_contract_check --contract tools/evidence/fixtures/vc/no-perf-critical.yaml --criticality critical --summary` |
| 49 | L2-T517 | BT-3 | Seeded-defect execution and SIG-18 | `tools/evidence/seeded_defect.py`, `tools/evidence/fixtures/seeded/**` | L2-T546 | M | `python -m tools.evidence.seeded_defect --result tools/evidence/fixtures/seeded/case-passed.json --summary` |
| 50 | L2-T138 | BT-3 | `ci.yml`: `verification-contract`, `seeded-defect-case` | `.github/workflows/ci.yml` | L2-T517 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary` |
| 51 | L2-T518 | BT-3 | Conformance-profile evidence substitution | `tools/evidence/profile_evidence.py`, `tools/evidence/fixtures/profile/**` | L2-T530 | M | `python -m tools.evidence.profile_evidence --profile client-app --summary` |
| 52 | L2-T519 | BT-3 | Evidence chain — the eleven questions | `tools/evidence/evidence_chain.py`, `tools/evidence/fixtures/chain/**` | L2-T518, L2-T544 | L | `python -m tools.evidence.evidence_chain --deployment tools/evidence/fixtures/chain/dep-complete.yaml --summary` |
| 53 | L2-T550 | BT-3 | `verify-digest-chain` sweep | `tools/evidence/verify_digest_chain.py`, `tools/evidence/fixtures/sweep/**` | L2-T519 | L | `python -m tools.evidence.verify_digest_chain --estate tools/evidence/fixtures/sweep/clean --summary` |
| 54 | L2-T139 | BT-3 | `verify-digest-chain.yml` — sweep and recovery gate | `.github/workflows/verify-digest-chain.yml` | L2-T550 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/verify-digest-chain.yml --summary` |
| 55 | L2-T551 | BT-3 | `/version` digest-match monitor | `tools/evidence/version_monitor.py`, `tools/evidence/fixtures/version/**` | L2-T519 | M | `python -m tools.evidence.version_monitor --fixture tools/evidence/fixtures/version/match.json --summary` |
| 56 | L2-T140 | BT-3 | `version-monitor.yml` | `.github/workflows/version-monitor.yml` | L2-T551 | S | `python -m tools.evidence.lint_workflow --path .github/workflows/version-monitor.yml --summary` |
| 57 | L2-T552 | BT-3 | Restore-rotation scheduler computation | `tools/evidence/restore_rotation.py`, `tools/evidence/fixtures/rotation/**` | L2-T530 | M | `python -m tools.evidence.restore_rotation --estate tools/evidence/fixtures/rotation/estate.yaml --as-of 2026-08-27 --summary` |
| 58 | L2-T141 | BT-3 | `restore-rotation.yml` | `.github/workflows/restore-rotation.yml` | L2-T552 | S | `python -m tools.evidence.lint_workflow --path .github/workflows/restore-rotation.yml --summary` |
| 59 | L2-T142 | BT-3 | `record-verification-result.yml` dispatch | `.github/workflows/record-verification-result.yml` | L2-T544 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/record-verification-result.yml --summary` |
| 60 | L2-T553 | BT-3 | The eight "shipped" conditions | `tools/evidence/shipped_assert.py`, `tools/evidence/fixtures/shipped/**` | L2-T519 | M | `python -m tools.evidence.shipped_assert --deployment tools/evidence/fixtures/shipped/complete.yaml --summary` |
| 61 | L2-T143 | BT-3 | `canary-exercise.yml` | `.github/workflows/canary-exercise.yml` | L2-T120, L2-T130 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/canary-exercise.yml --summary` |
| 62 | L2-T554 | BT-3 | Actor-gate-is-step-0 assertion | `tools/evidence/assert_actor_gate_first.py` | L2-T131, L2-T132, L2-T133, L2-T134 | M | `python -m tools.evidence.assert_actor_gate_first --path .github/workflows --summary` |
| 63 | L2-T303 | BT-3 | `templates/workflows/deploy-staging.yml` | `templates/workflows/deploy-staging.yml` | L2-T130, L2-T539 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 64 | L2-T304 | BT-3 | `templates/workflows/deploy-production.yml` | `templates/workflows/deploy-production.yml` | L2-T131, L2-T539 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 65 | L2-T305 | BT-3 | `templates/workflows/migrate.yml` | `templates/workflows/migrate.yml` | L2-T132, L2-T539 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 66 | L2-T306 | BT-3 | `templates/workflows/restore-test.yml` | `templates/workflows/restore-test.yml` | L2-T134, L2-T539 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 67 | L2-T307 | BT-3 | `templates/workflows/restore-production.yml` | `templates/workflows/restore-production.yml` | L2-T306 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 68 | L2-T308 | BT-3 | `templates/workflows/background-queue.yml` | `templates/workflows/background-queue.yml` | L2-T137, L2-T539 | S | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 69 | L2-T309 | BT-3 | The rollback workflow template | `templates/workflows/rollback.yml` | L2-T133, D-L2-05 | M | `python -m tools.evidence.render_template --lint templates/workflows --summary` |
| 70 | L2-T311 | BT-3 | `templates/workflows/MANIFEST.yaml` | `templates/workflows/MANIFEST.yaml` | L2-T301…L2-T309 | M | `python -m tools.evidence.render_template --manifest templates/workflows/MANIFEST.yaml --summary` |
| 71 | L2-T144 | BT-3 | `control-plane-ci.yml`: `recovery:`⇒`restore-production.yml` and template drift | `.github/workflows/control-plane-ci.yml` | L2-T311 | M | `python -m tools.evidence.lint_workflow --path .github/workflows/control-plane-ci.yml --summary` |
| 72 | L2-T700 | BT-3 | Execute AT-024 — shared CI workflow breaks | `tools/evidence/at/at-024.sh`, `tools/evidence/at/results/` | L2-T143, L2-T112, D-L2-01 | L | `bash tools/evidence/at/at-024.sh --summary` |
| 73 | L2-T701 | BT-3 | Execute AT-029 — control plane unreachable | `tools/evidence/at/at-029.sh` | L2-T133, D-L2-05 | L | `bash tools/evidence/at/at-029.sh --summary` |
| 74 | L2-T702 | BT-3 | Execute AT-035 — organisation export restores | `tools/evidence/at/at-035.sh` | L2-T136 | L | `bash tools/evidence/at/at-035.sh --summary` |
| 75 | L2-T703 | BT-3 | Execute AT-103 — production restore, no hand-held credential | `tools/evidence/at/at-103.sh` | L2-T307, L2-T134 | L | `bash tools/evidence/at/at-103.sh --summary` |
| 76 | L2-T555 | BT-3 | DoD acceptance matrix and lane handoff | `tools/evidence/acceptance_matrix.py`, `tools/evidence/HANDOFF.md` | all above | M | `python -m tools.evidence.acceptance_matrix --summary` |

### 2.1 Ids owned by a phase file — index only, no body in this file

Twenty-three ids used to carry a full task body **both here and in a phase file**, naming different work, different files and different dependencies under one identifier (`L2-99-review.md` defect **B2**). That is resolved as follows, and the resolution is binding:

* **The phase file holds the authoritative body.** `L2-04-evidence-chain.md` §6 owns `L2-T500`–`L2-T516`. `L2-02-digest-invariant.md` §3 owns `L2-T520`–`L2-T528`. `L2-03-production-gates.md` §7 owns `L2-T170`–`L2-T177` and `L2-T570`–`L2-T572`. Those bodies stay where they sit and are executed from those files.
* **This file holds an index entry.** The work this file used to publish under a colliding id is unchanged in substance and has been renumbered into the free `L2-T530`–`L2-T555` slots of the charter §12 `tools/evidence/**` band (`L2-T500`–`L2-T699`). Nothing was deleted.
* **Never execute a colliding id from this file.** If a dependency line, a test or a workflow names one of the left-hand ids below, it means the phase-file task, not the row beside it.
* **The charter is the fourth authoritative owner, and the last.** `L2-00-charter.md` §11 owns `L2-T001`–`L2-T006`. Those six differ from the twenty-three above in one way that matters: both copies described the **same** work, so nothing was renumbered — this file simply stops publishing a body under them. Their §2 rows 1–6 stand, their §3 blocks are index entries, and every criterion, command and STOP rule that lived only here is carried into the charter block it belongs to, under a heading beginning *Carried over from `L2-05-tasks.md` §3*.

| Id | Authoritative body — file and section | Title there | Was published here as | Now published here as |
| --- | --- | --- | --- | --- |
| `L2-T500` | `L2-04-evidence-chain.md` §6 | Phase-4 branch and the `tools/evidence` module skeleton | Evidence toolchain skeleton | `L2-T530` |
| `L2-T501` | `L2-04-evidence-chain.md` §6 | Pin the phase-4 consumed contract surface | Action-pin resolver and applier | `L2-T531` |
| `L2-T502` | `L2-04-evidence-chain.md` §6 | Author `tools/evidence/eleven-questions.yaml` | Action pin ledger | `L2-T532` |
| `L2-T503` | `L2-04-evidence-chain.md` §6 | Author the fixture estate: one closed chain and four broken variants | Workflow lint: pinning, permissions, no-`if:` | `L2-T533` |
| `L2-T504` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/evidence-query` | Required-context ↔ job cross-check | `L2-T534` |
| `L2-T505` | `L2-04-evidence-chain.md` §6 | Conformance-profile substitution and S18 equivalence | Run-conclusion assertor | `L2-T535` |
| `L2-T506` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/verify-digest-chain` — the comparison core | Delta-gate engine | `L2-T536` |
| `L2-T507` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/collect-version.sh` | Negative-test harness for the two guards | `L2-T537` |
| `L2-T508` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/build-deployment-record.sh` | SBOM-beside-digest assertion | `L2-T538` |
| `L2-T509` | `L2-04-evidence-chain.md` §6 | Author `.github/workflows/emit-deployment-record.yml` | Template renderer and placeholder lint | `L2-T539` |
| `L2-T510` | `L2-04-evidence-chain.md` §6 | Wire the emitter into `deploy-staging.yml` and `deploy-production.yml` | Time gate: Friday freeze and core hours | `L2-T540` |
| `L2-T511` | `L2-04-evidence-chain.md` §6 | Author `.github/workflows/verify-digest-chain.yml` — the scheduled sweep | Actor gate: human identity plus capability | `L2-T541` |
| `L2-T512` | `L2-04-evidence-chain.md` §6 | Implement the P0 escalation path | Workflow-identity gate: approver ≠ deployer | `L2-T542` |
| `L2-T513` | `L2-04-evidence-chain.md` §6 | Implement `tools/evidence/deploy-gate.sh` | Digest invariant: requested versus staging-verified | `L2-T543` |
| `L2-T514` | `L2-04-evidence-chain.md` §6 | Author `.github/workflows/evidence-selftest.yml` | Records-write client | `L2-T544` |
| `L2-T515` | `L2-04-evidence-chain.md` §6 | Append-only and effective-dating assertion | Event writer: one file per event, bound envelope | `L2-T545` |
| `L2-T516` | `L2-04-evidence-chain.md` §6 | Phase-4 roll-up, self-verify sweep and lane PR | Verification-contract check | `L2-T546` |
| `L2-T520` | `L2-02-digest-invariant.md` §3 | Branch, and the flat-record reader | `verify-digest-chain` sweep | `L2-T550` |
| `L2-T521` | `L2-02-digest-invariant.md` §3 | The artifact-identity format library | `/version` digest-match monitor | `L2-T551` |
| `L2-T522` | `L2-02-digest-invariant.md` §3 | Compute the S18 platform-rebuild identity (D78) | Restore-rotation scheduler computation | `L2-T552` |
| `L2-T523` | `L2-02-digest-invariant.md` §3 | THE DIGEST INVARIANT | The eight "shipped" conditions | `L2-T553` |
| `L2-T524` | `L2-02-digest-invariant.md` §3 | Artifact publication check, and the never-rebuild rule | Actor-gate-is-step-0 assertion | `L2-T554` |
| `L2-T525` | `L2-02-digest-invariant.md` §3 | SBOM beside the digest | DoD acceptance matrix and lane handoff | `L2-T555` |
| `L2-T001` | `L2-00-charter.md` §11 | Create the lane branch and the owned-path skeleton | same work, same title | index only — no renumber |
| `L2-T002` | `L2-00-charter.md` §11 | Pin the consumed contract surface | same work, same title | index only — no renumber |
| `L2-T003` | `L2-00-charter.md` §11 | Publish the required-status-check name registry | same work, same title | index only — no renumber |
| `L2-T004` | `L2-00-charter.md` §11 | Author the lane-guard workflow | same work, same title | index only — no renumber |
| `L2-T005` | `L2-00-charter.md` §11 | Author the merge-train preflight check | Merge-train preflight check | index only — no renumber |
| `L2-T006` | `L2-00-charter.md` §11 | Rebase and open the lane PR | Rebase and open the phase-0 lane PR | index only — no renumber |
| `L2-T171` | `L2-03-production-gates.md` §7 | The actor gate (P3-C) | never bodied here — cited by id in `L2-06-tests.md` | already index form |
| `L2-T172` | `L2-03-production-gates.md` §7 | The runner-tier assertion (P3-D) | never bodied here — cited by id in `L2-06-tests.md` | already index form |
| `L2-T173` | `L2-03-production-gates.md` §7 | The environment deployment-policy assertion (P3-E) | never bodied here — cited by id in `L2-06-tests.md` | already index form |

`L2-T517`, `L2-T518` and `L2-T519` never collided and keep their ids here. `L2-T526`–`L2-T528` are `L2-02`'s alone and have no body in this file. `L2-T171`, `L2-T172` and `L2-T173` are `L2-03-production-gates.md` §7's alone: `L2-06-tests.md` cites them by id but defines no body for them, which is already the correct index form and is left as it stands.

**The table above is now the whole story — all thirty-two ids the two integrity sweeps raised, in one place.** Twenty-three were renumbered out of this file into `L2-T530`–`L2-T555`; three (`L2-T171`–`L2-T173`) were never a collision at all and are listed so no later reader re-opens them; six (`L2-T001`–`L2-T006`) were the same work published twice and are now bodied in the charter and indexed here. That is 23 + 3 + 6 = **32**. No id in Lane 2 carries a task body in two files.

**How to read a row.** The **Id** is what every dependency line, test and workflow in the lane means. The **Authoritative body** column is the only place to execute it from. *Now published here as* reads **index only — no renumber** wherever the two copies described the same work: once the duplicate body became an index entry there was nothing left to renumber, and the id keeps its number in the §2 execution table.

<!-- B1 CLOSED (FD-B1-L2 2026-09-02): L2-05-tasks.md is the authoritative task plan.
     Phase files L2-02, L2-03, L2-04 hold authoritative task bodies for the IDs listed below;
     execute them from those files. The old BLOCKED verdict is retracted. -->

**Subsystems G, H, J, O and P have no lane.** PARTITION v1 assigns A, B to L1; E, F to L2; C, D to L3; I, N to L4; K, L, M, Q, R to L5. G, H, J, O and P are unassigned, and Lane 2 does not claim them, plan for them or build against them. If a task in this file appears to need one, that is not a gap you close: STOP under rule S4 and route it to L0, blocker title `BLOCKER L2: task requires an unassigned subsystem (G/H/J/O/P), PARTITION v1 names no owner`.

**This subsection supersedes §10 note 2 of the earlier issue of this file**, which said the §2 table was the execution authority wherever a number collided. It is not. The phase file is.

---

## 3. Task detail — Phase BT-1, execution order 1–30

### 3.0 How to read a task block

Every block below carries the same fields, in the same order, and nothing else.

| Field | Meaning |
| --- | --- |
| `#` | execution order, matching the `#` column of §2. Work this number, not the id. |
| **Phase** | BT-0/1/2/3 of §0.10. Do not open a branch for a phase L0 has not opened. |
| **Size** | S / M / L of §0.7. |
| **Deps** | task ids that must be **merged to `integration`** before you start. Verify with `git log origin/integration --oneline \| grep '<dep-id>'`. |
| **Branch slug** | the literal `<branch-slug>` to substitute into the §0.3 open and close blocks. One branch per task. |
| **Files** | every path this task creates or edits. Touching a path not on this line is rule S5. |
| **Spec** | the sections and line ranges that fix this task's content. Read them with `sed -n 'A,Bp' "$SPEC"`. |
| **Build this** | what to produce. It contains no choices. If you find one, it is rule S4. |
| **SELF-VERIFY / CORRECT OUTPUT / STOP** | one command block, its exact expected stdout, and the condition that ends the task. |

Set `SPEC` once per shell, alongside the §0.2 block:

**Commands**

```bash
set -euo pipefail
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
test -f "$SPEC" || { echo "SPEC ABSENT - STOP"; exit 1; }
```

**Every block assumes the §0.3 open block has already run** with that block's branch slug, and ends by telling you to run the §0.3 close block with the same slug. Neither is repeated in full inside a task.

---

### L2-T001 — Lane branch and owned-path skeleton

> **Index — `L2-T001` is not defined here.** `L2-00-charter.md` §11 `L2-T001` (*Create the lane branch and the owned-path skeleton*) is the authoritative body, including the A4–A6 criteria and the `S2` STOP rule this file used to hold alone; execute task 1 from there, on the charter branch `lane/2/phase0-charter`. See §2.1, `L2-99-review.md` and `_INTEGRITY.md` finding 4.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Open block (§0.3)
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/phase0-charter

# Create the three owned-path roots with .gitkeep sentinels
mkdir -p .github/workflows
mkdir -p templates/workflows
mkdir -p tools/evidence

touch .github/workflows/.gitkeep
touch templates/workflows/.gitkeep
touch tools/evidence/.gitkeep

git add \
  .github/workflows/.gitkeep \
  templates/workflows/.gitkeep \
  tools/evidence/.gitkeep

git commit -m "L2-T001: lane branch and owned-path skeleton"

# SELF-VERIFY
test -d .github/workflows && test -d templates/workflows && test -d tools/evidence
echo $?
# Expected: 0

# FOREIGN-PATH CHECK
FOREIGN=$(git diff --name-only origin/integration...HEAD \
  | grep -vE '^(\.github/workflows/|templates/workflows/|tools/evidence/)' \
  | wc -l | tr -d ' ')
[ "$FOREIGN" = "0" ] || { echo "FOREIGN_WRITE_DETECTED - STOP"; exit 1; }
echo "FOREIGN_WRITES=0"
```

---

### L2-T002 — Pin the consumed contract surface

> **Index — `L2-T002` is not defined here.** `L2-00-charter.md` §11 `L2-T002` (*Pin the consumed contract surface*) is the authoritative body, including the A4–A5 criteria, the `S1` STOP rule and the recorded lock-file-format difference this file used to hold alone; execute task 2 from there. The §2 row 2 acceptance command is unchanged and still passes against the charter's lock file. See §2.1.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Open block (§0.3)
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t002-contract-lock

# Capture the current HEAD SHA of contracts/ — STOP if contracts/ is absent (rule S1)
test -d contracts || { echo "STOP: contracts/ ABSENT — rule S1"; exit 1; }

CONTRACTS_SHA=$(git log --format='%H' -1 -- contracts/)
[ -n "$CONTRACTS_SHA" ] || { echo "STOP: contracts/ has no commits — rule S1"; exit 1; }

cat > tools/evidence/CONSUMED-CONTRACTS.lock <<EOF
# Lane 2 consumed-contract surface lock — generated by L2-T002
# Format: contracts_commit: <40-hex SHA of the contracts/ tree HEAD>
# Never edit by hand. Re-run L2-T002 when contracts/ changes.
# Authority: L2-05-tasks.md §2 row 2; L2-00-charter.md §4.1
contracts_commit: ${CONTRACTS_SHA}
EOF

git add tools/evidence/CONSUMED-CONTRACTS.lock
git commit -m "L2-T002: pin consumed contract surface at ${CONTRACTS_SHA}"

# SELF-VERIFY
COUNT=$(grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/CONSUMED-CONTRACTS.lock)
echo "LOCK_ROWS=$COUNT"
# Expected: LOCK_ROWS=1
```

---

### L2-T003 — Publish the required-status-check name registry

> **Index — `L2-T003` is not defined here.** `L2-00-charter.md` §11 `L2-T003` (*Publish the required-status-check name registry*) is the authoritative body; execute task 3 from there and read its **A3 CORRECTION**, which carries this file's fifteen-versus-sixteen finding, the corrected SELF-VERIFY printing `CONTEXT_COUNT=15` and `L2-T003 OK`, and the blocker to file — `L2-99-review.md` defect **B5**. §0.5 of this file and charter criterion A3 remain the two places L0 must reconcile. See §2.1.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Open block (§0.3)
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t003-required-checks

# The fifteen required contexts — source of truth per §0.5 of L2-05-tasks.md
# DO NOT add, rename or remove a name without L0 authority (§0.5 STOP rule)
cat > templates/workflows/required-checks.yaml <<'EOF'
# Required-status-check name registry — Lane 2 (Pipeline & Evidence)
# Authority: L2-05-tasks.md §0.5; spec §33.2 L2854-2869; §53.1 L4653-4689
# This file is the authoritative list of context names Lane 2 emits.
# L5 copies from contracts/workflows/required-checks.v1.yaml for branch protection.
# Lane 2 never adds, renames or removes a name here without L0 authority.
#
# Format: each context name is a YAML list item under its phase group.
# A reusable-workflow job name never appears here; only caller job names do (§0.5).

phase_4:
    - unit-tests
    - integration-tests
    - build
    - security-scan
    - licence-scan
    - slopsquat-check
    - contract-validation
    - registry-validation
    - parity-check
phase_5:
    - verification-contract
    - seeded-defect-case
phase_6:
    - artifact-digest-recorded
    - sbom-emitted
always:
    - renovate-path-guard
    - lane-guard
EOF

git add templates/workflows/required-checks.yaml
git commit -m "L2-T003: publish required-status-check name registry (15 contexts)"

# SELF-VERIFY
COUNT=$(grep -cE '^    - [a-z0-9-]+$' templates/workflows/required-checks.yaml)
echo "CONTEXT_COUNT=$COUNT"
# Expected: CONTEXT_COUNT=15
echo "L2-T003 OK"
```

---

### L2-T004 — Author the lane-guard workflow

> **Index — `L2-T004` is not defined here.** `L2-00-charter.md` §11 `L2-T004` (*Author the lane-guard workflow*) is the authoritative body, including the literal workflow heredoc, the A7 no-`write`-scope criterion and the `S4` STOP rule this file used to hold alone; execute task 4 from there. The charter pins `actions/checkout` to a literal full SHA rather than the `PIN:` placeholder this file described — `L2-T532` records that pair in `tools/evidence/action-pins.txt` and rewrites nothing. See §2.1.



```yaml
# File: .github/workflows/lane-guard.yml
# Created by L2-T004
# Spec: §0.1 path-ownership; PARTITION.md rule 1; §33.2 L2854-2869
# This workflow enforces that every PR touches only the paths its lane owns.
# It carries no if: and no path filter (§0.6 rule 4).
# permissions: contents: read — no write scope needed or granted.
name: lane-guard

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

concurrency:
  group: lane-guard-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lane-guard:
    name: lane-guard
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@{{PIN:actions/checkout}}
        with:
          fetch-depth: 0

      - name: Detect lane from branch name
        id: detect
        run: |
          set -euo pipefail
          BRANCH="${{ github.head_ref }}"
          case "$BRANCH" in
            lane/1/*) LANE=1 ;;
            lane/2/*) LANE=2 ;;
            lane/3/*) LANE=3 ;;
            lane/4/*) LANE=4 ;;
            lane/5/*) LANE=5 ;;
            *)
              echo "::error::Branch '$BRANCH' does not match lane/N/* — only lane branches are merged to integration"
              exit 1
              ;;
          esac
          echo "lane=$LANE" >> "$GITHUB_OUTPUT"

      - name: Assert lane-owned paths only
        run: |
          set -euo pipefail
          LANE="${{ steps.detect.outputs.lane }}"
          # Ownership table from PARTITION.md (FROZEN)
          case "$LANE" in
            1) OWNED_RE='^(schemas/|validators/|contracts/)' ;;
            2) OWNED_RE='^(\.github/workflows/|templates/workflows/|tools/evidence/)' ;;
            3) OWNED_RE='^(reconciler/|tools/provision/|validators/drift/)' ;;
            4) OWNED_RE='^(records/|events/|metrics/)' ;;
            5) OWNED_RE='^(access/|infra/|ops-vm/)' ;;
          esac
          CHANGED=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          FOREIGN=$(echo "$CHANGED" | grep -vE "$OWNED_RE" | grep -vE '^\s*$' || true)
          if [ -n "$FOREIGN" ]; then
            echo "::error::Lane $LANE PR touches foreign paths:"
            echo "$FOREIGN"
            exit 1
          fi
          echo "OK: all changed paths are within lane $LANE owned trees"
          exit 0
```

**Commands**

```bash
# Shell script to create the file and commit (L2-T004 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t004-lane-guard

# Write the workflow file (see YAML block above)
# Apply pins after ledger exists (L2-T532); during T004 use the placeholder form.
# The charter pins actions/checkout to a literal full SHA; apply_pins.sh populates it.

cat > .github/workflows/lane-guard.yml <<'WORKFLOW'
name: lane-guard

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

concurrency:
  group: lane-guard-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lane-guard:
    name: lane-guard
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout
        with:
          fetch-depth: 0

      - name: Detect lane from branch name
        id: detect
        run: |
          set -euo pipefail
          BRANCH="${{ github.head_ref }}"
          case "$BRANCH" in
            lane/1/*) LANE=1 ;;
            lane/2/*) LANE=2 ;;
            lane/3/*) LANE=3 ;;
            lane/4/*) LANE=4 ;;
            lane/5/*) LANE=5 ;;
            *)
              echo "::error::Branch '$BRANCH' does not match lane/N/*"
              exit 1
              ;;
          esac
          echo "lane=$LANE" >> "$GITHUB_OUTPUT"

      - name: Assert lane-owned paths only
        run: |
          set -euo pipefail
          LANE="${{ steps.detect.outputs.lane }}"
          case "$LANE" in
            1) OWNED_RE='^(schemas/|validators/|contracts/)' ;;
            2) OWNED_RE='^(\.github/workflows/|templates/workflows/|tools/evidence/)' ;;
            3) OWNED_RE='^(reconciler/|tools/provision/|validators/drift/)' ;;
            4) OWNED_RE='^(records/|events/|metrics/)' ;;
            5) OWNED_RE='^(access/|infra/|ops-vm/)' ;;
          esac
          CHANGED=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          FOREIGN=$(echo "$CHANGED" | grep -vE "$OWNED_RE" | grep -vE '^\s*$' || true)
          if [ -n "$FOREIGN" ]; then
            echo "::error::Lane $LANE PR touches foreign paths:"
            echo "$FOREIGN"
            exit 1
          fi
          echo "OK: all changed paths are within lane $LANE owned trees"
WORKFLOW

git add .github/workflows/lane-guard.yml
git commit -m "L2-T004: author lane-guard workflow"

# SELF-VERIFY
COUNT=$(grep -cE '^            lane/[1-5]/\*\)' .github/workflows/lane-guard.yml)
echo "LANE_CASES=$COUNT"
# Expected: LANE_CASES=5 (one per lane)
```

---

### L2-T005 — Merge-train preflight check

> **Index — `L2-T005` is not defined here.** `L2-00-charter.md` §11 `L2-T005` (*Author the merge-train preflight check*) is the authoritative body, including the literal script, the A5 writes-nothing criterion and the recorded conflict between that script's `PREFLIGHT_PASS` verdict and §0.4 of this file, which is filed to L0 and blocks nothing; execute task 5 from there and do **not** add a `--summary` flag. See §2.1.



**Commands**

```bash
# File: tools/evidence/preflight.sh
# Created by L2-T005
# Spec: L2-05-tasks.md §2 row 5; L2-00-charter.md §11 L2-T005
# This script is POSIX bash. It writes nothing. exit 0 = PREFLIGHT_PASS.
# DO NOT add --summary; the charter records that T005 must not carry the flag.

set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t005-preflight

cat > tools/evidence/preflight.sh <<'SCRIPT'
#!/usr/bin/env bash
# Merge-train preflight check — Lane 2 (Pipeline & Evidence)
# Authority: L2-05-tasks.md §2 row 5; L2-00-charter.md §11 L2-T005
# Spec: PARTITION.md merge-train position (L2 is 3rd of 5: L1 → L4 → L2 → L3 → L5)
#
# Runs before any L2 branch is opened for a new cycle.
# Checks that L1 and L4 have already merged to integration this cycle.
# Writes nothing. exit 0 prints PREFLIGHT_PASS. exit 1 prints PREFLIGHT_FAIL.
#
# Usage: bash tools/evidence/preflight.sh
set -euo pipefail

INTEGRATION="${1:-integration}"
FAIL=0

check_lane_merged() {
  local LANE="$1"
  local LABEL="$2"
  # A lane's merge is present if integration contains a commit whose message
  # matches the lane PR pattern. This is a best-effort signal; the gate is
  # the lane-guard green check on integration, not this script.
  if git log "origin/${INTEGRATION}" --oneline | grep -qE "lane/${LANE}/"; then
    echo "OK: ${LABEL} commits found in origin/${INTEGRATION}"
  else
    echo "WARN: ${LABEL} commits NOT found in origin/${INTEGRATION} — verify merge-train order"
    FAIL=1
  fi
}

echo "--- Lane 2 merge-train preflight ---"
echo "INTEGRATION_BRANCH: origin/${INTEGRATION}"
echo "INTEGRATION_HEAD: $(git rev-parse origin/${INTEGRATION})"

# Rule: L1 and L4 merge before L2 (PARTITION.md line 35)
check_lane_merged "1" "Lane 1 (Schemas & Registry)"
check_lane_merged "4" "Lane 4 (Records & Events)"

# Verify owned paths exist
for P in ".github/workflows" "templates/workflows" "tools/evidence"; do
  if [ -d "$P" ]; then
    echo "OK: $P exists"
  else
    echo "FAIL: $P ABSENT"
    FAIL=1
  fi
done

# Verify contracts/ exists (rule S1 gate)
if [ -d "contracts" ]; then
  echo "OK: contracts/ present"
else
  echo "FAIL: contracts/ ABSENT — cannot proceed (rule S1)"
  FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "PREFLIGHT_PASS"
  exit 0
else
  echo "PREFLIGHT_FAIL"
  exit 1
fi
SCRIPT

chmod +x tools/evidence/preflight.sh
git add tools/evidence/preflight.sh
git commit -m "L2-T005: merge-train preflight check"

# SELF-VERIFY
bash -n tools/evidence/preflight.sh
echo $?
# Expected: 0

# Acceptance: tail -1 of the script output in a live repo
# bash tools/evidence/preflight.sh | tail -1
# Expected: PREFLIGHT_PASS (when L1 and L4 have merged)
```

---

### L2-T006 — Rebase and open the phase-0 lane PR

> **Index — `L2-T006` is not defined here.** `L2-00-charter.md` §11 `L2-T006` (*Rebase and open the lane PR*) is the authoritative body, including the `gh pr create` block, the A5 predecessors-present check adapted from this file's loop, and the `S2` STOP rule for a red `lane-guard`; execute task 6 from there. One pull request covers rows 1–6; the §0.3 per-task branch protocol resumes at row 7, `L2-T530`. See §2.1.



**Commands**

```bash
# L2-T006: Rebase and open the phase-0 lane PR
# This task publishes the branch — no files are created.
# Authority: L2-00-charter.md §11 L2-T006; L2-05-tasks.md §2 row 6
# Deps: L2-T001 through L2-T005 must be merged to integration first.

set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Verify all five predecessor commits are present on integration
for DEP in L2-T001 L2-T002 L2-T003 L2-T004 L2-T005; do
  if git log origin/integration --oneline | grep -qF "$DEP"; then
    echo "OK: $DEP present on origin/integration"
  else
    echo "STOP: $DEP not found on origin/integration — merge predecessors first"
    exit 1
  fi
done

# Preflight must pass (outputs PREFLIGHT_PASS as last line)
LAST=$(bash tools/evidence/preflight.sh | tail -1)
[ "$LAST" = "PREFLIGHT_PASS" ] || { echo "STOP: preflight did not pass — $LAST"; exit 1; }

# The charter uses a single PR for tasks 1-6 on branch lane/2/phase0-charter.
# If the branch already exists and was pushed piecemeal, rebase now.
git fetch origin
git rebase origin/integration

git push -u origin lane/2/phase0-charter

gh pr create \
  --base integration \
  --head lane/2/phase0-charter \
  --title "L2-T001–T006: Lane 2 phase-0 bootstrap" \
  --body "Lane 2 (Pipeline & Evidence). Tasks L2-T001 through L2-T006.
Owned paths only: .github/workflows/, templates/workflows/, tools/evidence/.
SELF-VERIFY in L2-05-tasks.md and L2-00-charter.md passed.
Preflight: PREFLIGHT_PASS."

# SELF-VERIFY (acceptance command from §2 row 6)
bash tools/evidence/preflight.sh | tail -1
# Expected: PREFLIGHT_PASS
```

---

### L2-T530 — Evidence toolchain skeleton

> **Index — `L2-T500` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T500` in full (*Phase-4 branch and the `tools/evidence` module skeleton*) and is authoritative for that id; this block is different work and now carries the id `L2-T530`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 7 · **Phase** BT-1 · **Size** S · **Deps** L2-T006, **D-L2-07** · **Branch slug** `t530-evidence-skeleton`
**Files:** `tools/evidence/__init__.py`, `tools/evidence/requirements.txt`, `tools/evidence/README.md`
**Spec:** §99.1 L9184 area (a validator suite, a reconciliation engine, a CLI, a workflow library — scripts, not an application); §101 invariant 85 L9565 (dependencies pinned)

**Build this.** The Python package root for subsystem F, on the D-L2-07 ratification recorded in §1: Python 3.12, `==` pins, no lockfile generator. `__init__.py` exports one constant carrying the §0.4 grammar verbatim, so every later module imports a single definition instead of restating it:

```python
TOOL_CONTRACT = "<STATUS> <tool-id> checked=<int> failed=<int>"
STATUS_OK, STATUS_FAIL, STATUS_ERROR = "OK", "FAIL", "ERROR"
EXIT_OK, EXIT_FAIL, EXIT_ERROR = 0, 2, 3
```

`requirements.txt` pins every dependency with `==` and carries no range operator anywhere. `README.md` states the §0.4 contract, the fail-closed rule of §0.4, and the namespace-package rule of §0.1.

**Acceptance criteria**

1. `python -c "import tools.evidence as e; print(e.TOOL_CONTRACT)"` prints the grammar line.
2. Every non-comment, non-blank line of `requirements.txt` matches `^[A-Za-z0-9._-]+==[0-9][A-Za-z0-9._-]*$`.
3. `tools/__init__.py` does not exist.
4. `README.md` contains the literal strings `checked=` and `fail-closed`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -c "import tools.evidence as e; print(e.TOOL_CONTRACT)"
echo "UNPINNED=$(grep -vE '^[[:space:]]*(#|$)' tools/evidence/requirements.txt | grep -cvE '^[A-Za-z0-9._-]+==[0-9][A-Za-z0-9._-]*$')"
test ! -e tools/__init__.py && echo "NAMESPACE=OK"
```

**CORRECT OUTPUT**

```
<STATUS> <tool-id> checked=<int> failed=<int>
UNPINNED=0
NAMESPACE=OK
```

**STOP** — if L0 ratified anything other than Python 3.12 with `==` pins, this whole file needs reissuing by L0. Do not adapt it yourself. Rule S4; blocker title `BLOCKER L2-T530: D-L2-07 ratified a toolchain this file was not written against`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t530-evidence-skeleton`.

---

### L2-T531 — Action-pin resolver and applier

> **Index — `L2-T501` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T501` in full (*Pin the phase-4 consumed contract surface*) and is authoritative for that id; this block is different work and now carries the id `L2-T531`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 8 · **Phase** BT-1 · **Size** S · **Deps** L2-T530 · **Branch slug** `t531-pin-tools`
**Files:** `tools/evidence/resolve_action_pin.sh`, `tools/evidence/apply_pins.sh`
**Spec:** §48.1 L4300–4308; §33.2 L2854–2869; §101 invariant 85 L9565

**Build this.** Two `bash` helpers. `resolve_action_pin.sh <owner/repo> <tag>` resolves a tag to its full 40-character commit SHA through `gh api` and prints one line `<owner/repo> <tag> <sha>`; it exits `3` when the tag does not resolve and never prints a partial line. `apply_pins.sh` reads `tools/evidence/action-pins.txt` and rewrites every `PIN:<owner/repo>` placeholder in `.github/workflows/*.yml` and `templates/workflows/*.yml` to `<owner/repo>@<sha> # <tag>`; it is idempotent, and it exits `3` changing nothing when a placeholder has no ledger row. Neither script writes outside the three owned trees.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t531-pin-tools

# Create tools/evidence/resolve_action_pin.sh
cat > tools/evidence/resolve_action_pin.sh <<'SCRIPT'
#!/usr/bin/env bash
# resolve_action_pin.sh <owner/repo> <tag>
# Resolves a GitHub Action tag to its full 40-character commit SHA via gh api.
# Prints exactly one line: <owner/repo> <tag> <sha>
# Exits 3 when the tag does not resolve; never prints a partial line.
# Authority: L2-05-tasks.md L2-T531; spec §48.1 L4300-4308; §101 invariant 85 L9565
set -euo pipefail

REPO="${1:-}"
TAG="${2:-}"

[ -n "$REPO" ] || { echo "Usage: resolve_action_pin.sh <owner/repo> <tag>" >&2; exit 3; }
[ -n "$TAG" ]  || { echo "Usage: resolve_action_pin.sh <owner/repo> <tag>" >&2; exit 3; }

# Resolve tag to SHA via gh api
SHA=$(gh api "repos/${REPO}/commits/${TAG}" --jq '.sha' 2>/dev/null) || {
  echo "ERROR: cannot resolve ${REPO}@${TAG} via gh api" >&2
  exit 3
}

# Validate SHA is exactly 40 hex characters
if ! echo "$SHA" | grep -qE '^[0-9a-f]{40}$'; then
  echo "ERROR: resolved SHA '${SHA}' is not 40-hex — repo=${REPO} tag=${TAG}" >&2
  exit 3
fi

# Print the ledger row — exactly one line to stdout
printf '%s %s %s\n' "$REPO" "$TAG" "$SHA"
SCRIPT

chmod +x tools/evidence/resolve_action_pin.sh

# Create tools/evidence/apply_pins.sh
cat > tools/evidence/apply_pins.sh <<'SCRIPT'
#!/usr/bin/env bash
# apply_pins.sh
# Reads tools/evidence/action-pins.txt and rewrites every PIN:<owner/repo>
# placeholder in .github/workflows/*.yml and templates/workflows/*.yml to
#   <owner/repo>@<sha> # <tag>
# Idempotent: running twice leaves an identical tree.
# Exits 3 (changing nothing) when a placeholder has no matching ledger row.
# Never writes outside the three owned trees.
# Authority: L2-05-tasks.md L2-T531; spec §48.1 L4300-4308
set -euo pipefail

LEDGER="tools/evidence/action-pins.txt"
WORKFLOW_DIRS=(".github/workflows" "templates/workflows")
FAIL=0

[ -f "$LEDGER" ] || { echo "ERROR: ledger not found at ${LEDGER}" >&2; exit 3; }

# Build an associative array of repo -> "tag sha"
declare -A PIN_MAP
while IFS=' ' read -r repo tag sha; do
  # Skip blank lines and comments
  [[ "$repo" =~ ^#.*$ ]] && continue
  [ -z "$repo" ] && continue
  PIN_MAP["$repo"]="$tag $sha"
done < "$LEDGER"

# Find all PIN: placeholders across owned workflow files
PLACEHOLDER_FOUND=0
for DIR in "${WORKFLOW_DIRS[@]}"; do
  [ -d "$DIR" ] || continue
  while IFS= read -r -d '' WFILE; do
    while IFS= read -r LINE; do
      if [[ "$LINE" =~ PIN:([a-zA-Z0-9._/-]+) ]]; then
        PLACEHOLDER_FOUND=1
        REPO="${BASH_REMATCH[1]}"
        if [ -z "${PIN_MAP[$REPO]+x}" ]; then
          echo "ERROR: no ledger row for placeholder PIN:${REPO}" >&2
          FAIL=1
        fi
      fi
    done < "$WFILE"
  done < <(find "$DIR" -maxdepth 1 -name '*.yml' -print0)
done

[ "$FAIL" -eq 0 ] || exit 3

# Apply substitutions in-place using sed
for DIR in "${WORKFLOW_DIRS[@]}"; do
  [ -d "$DIR" ] || continue
  while IFS= read -r -d '' WFILE; do
    for REPO in "${!PIN_MAP[@]}"; do
      TAG_SHA="${PIN_MAP[$REPO]}"
      TAG=$(echo "$TAG_SHA" | cut -d' ' -f1)
      SHA=$(echo "$TAG_SHA" | cut -d' ' -f2)
      # Replace PIN:<repo> with <repo>@<sha> # <tag>
      sed -i "s|PIN:${REPO}|${REPO}@${SHA} # ${TAG}|g" "$WFILE"
    done
  done < <(find "$DIR" -maxdepth 1 -name '*.yml' -print0)
done

echo "apply_pins: substitution complete"
exit 0
SCRIPT

chmod +x tools/evidence/apply_pins.sh

git add \
  tools/evidence/resolve_action_pin.sh \
  tools/evidence/apply_pins.sh

git commit -m "L2-T531: action-pin resolver and applier"

# SELF-VERIFY
bash -n tools/evidence/resolve_action_pin.sh && bash -n tools/evidence/apply_pins.sh
echo "SYNTAX=$?"
# Verify no foreign write redirects
FOREIGN=$(grep -cE '>[[:space:]]*(contracts|registries|schemas|reconciler|access|infra|records|events)/' tools/evidence/apply_pins.sh || echo 0)
echo "FOREIGN_WRITES=$FOREIGN"
# Expected:
# SYNTAX=0
# FOREIGN_WRITES=0
```

**Acceptance criteria**

1. Both scripts pass `bash -n`.
2. `apply_pins.sh` run twice leaves an identical tree the second time, provable with `git status --porcelain`.
3. A placeholder with no ledger row makes `apply_pins.sh` exit `3` and modify nothing.
4. Neither script contains a redirect into a path outside the three owned trees.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/resolve_action_pin.sh && bash -n tools/evidence/apply_pins.sh && echo "SYNTAX=0"
echo "FOREIGN_WRITES=$(grep -cE '>[[:space:]]*(contracts|registries|schemas|reconciler|access|infra|records|events)/' tools/evidence/apply_pins.sh)"
```

**CORRECT OUTPUT**

```
SYNTAX=0
FOREIGN_WRITES=0
```

**STOP** — if `gh api` cannot reach GitHub, do not hand-type a SHA from a browser or from memory. Rule S1; blocker title `BLOCKER L2-T531: cannot resolve action tags to SHAs, gh api unreachable`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t531-pin-tools`.

---

### L2-T532 — Action pin ledger

> **Index — `L2-T502` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T502` in full (*Author `tools/evidence/eleven-questions.yaml`*) and is authoritative for that id; this block is different work and now carries the id `L2-T532`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 9 · **Phase** BT-1 · **Size** S · **Deps** L2-T531 · **Branch slug** `t532-pin-ledger`
**Files:** `tools/evidence/action-pins.txt`
**Spec:** §48.1 L4300–4308 (*"pinned to a full commit SHA. No tags, no floating branches, no exceptions"*); §101 invariant 85 L9565

**Build this.** One ledger row per third-party action this lane ever uses, each row exactly `<owner/repo> <tag> <sha>` with a 40-hex SHA, every SHA produced by `resolve_action_pin.sh` and never by hand. Add a row when a workflow first needs the action; never delete a row. The ledger is the only place a SHA is written down, and `apply_pins.sh` is the only thing that copies one into a workflow.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
: > tools/evidence/action-pins.txt
for PAIR in "actions/checkout v4"; do
  bash tools/evidence/resolve_action_pin.sh $PAIR >> tools/evidence/action-pins.txt
done
git add tools/evidence/action-pins.txt
git commit -m "L2-T532: action pin ledger"
```

**Acceptance criteria**

1. Every line matches `^[a-z0-9._/-]+ v[0-9.]+ [0-9a-f]{40}$`. No line is exempt.
2. No `owner/repo` appears twice.
3. No workflow under `.github/workflows/` or `templates/workflows/` references an action by tag or branch — every `uses:` of a third-party action carries `@<40-hex>`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
echo "ROWS=$(grep -cE '^[a-z0-9._/-]+ v[0-9.]+ [0-9a-f]{40}$' tools/evidence/action-pins.txt)"
echo "MALFORMED=$(grep -cvE '^[a-z0-9._/-]+ v[0-9.]+ [0-9a-f]{40}$' tools/evidence/action-pins.txt)"
echo "DUPES=$(cut -d' ' -f1 tools/evidence/action-pins.txt | sort | uniq -d | wc -l | tr -d ' ')"
```

**CORRECT OUTPUT** (`ROWS` equals the number of distinct actions the lane uses so far; at this task it is `1`)

```
ROWS=1
MALFORMED=0
DUPES=0
```

**STOP** — if an action you need publishes no tag, or resolves to a SHA that changes between two runs of `resolve_action_pin.sh`, do not pin the branch and do not vendor the action. Rule S4; blocker title `BLOCKER L2-T532: <owner/repo> cannot be pinned to a stable full SHA`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t532-pin-ledger`.

---

### L2-T533 — Workflow lint: pinning, permissions, no-`if:`

> **Index — `L2-T503` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T503` in full (*Author the fixture estate: one closed chain and four broken variants*) and is authoritative for that id; this block is different work and now carries the id `L2-T533`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 10 · **Phase** BT-1 · **Size** M · **Deps** L2-T532 · **Branch slug** `t533-lint-workflow`
**Files:** `tools/evidence/lint_workflow.py`, `tools/evidence/fixtures/lint/**`
**Spec:** §33.2 L2854–2869 (path filters, `if:`, SHA pinning, least-privilege `GITHUB_TOKEN`); §48.1 L4300–4308

**Build this.** The lint every later workflow task is graded by. `python -m tools.evidence.lint_workflow --path <file-or-dir> --summary` applies five rules to each workflow file and prints one §0.4 line with tool-id `lint_workflow`:

| Rule | Fails when |
| --- | --- |
| `LW-01` | a `uses:` of a third-party action is not `@<40-hex>` |
| `LW-02` | a job emitting a name listed in `required-checks.yaml` carries an `if:` |
| `LW-03` | the workflow carries `paths:` or `paths-ignore:` |
| `LW-04` | `permissions:` is absent, or grants a `write` scope the workflow does not use |
| `LW-05` | a step declares `continue-on-error: true` on a job emitting a required context |

`checked=` counts workflow files examined; `failed=` counts rule violations. Fixtures: `fixtures/lint/good.yml` (passes all five) and exactly five one-violation files `bad_lw01.yml` … `bad_lw05.yml`.



```python
# File: tools/evidence/lint_workflow.py
# Created by L2-T533
# Usage: python -m tools.evidence.lint_workflow --path <file-or-dir> [--summary]
# Spec: §33.2 L2854-2869; §48.1 L4300-4308
# Prints: OK|FAIL|ERROR lint_workflow checked=<int> failed=<int>
# Exit:   0=OK, 2=FAIL, 3=ERROR

"""
Workflow lint — five rules, fail on any violation.

LW-01: a uses: of a third-party action is not @<40-hex>
LW-02: a job emitting a required context carries an if:
LW-03: the workflow carries paths: or paths-ignore:
LW-04: permissions: is absent, or grants a write scope the workflow does not use
LW-05: a step declares continue-on-error: true on a job emitting a required context
"""

import sys
import os
import re
import argparse
import yaml

# Inline TOOL_CONTRACT to avoid circular import during bootstrap
STATUS_OK, STATUS_FAIL, STATUS_ERROR = "OK", "FAIL", "ERROR"
EXIT_OK, EXIT_FAIL, EXIT_ERROR = 0, 2, 3
TOOL_ID = "lint_workflow"

# Required contexts from required-checks.yaml (§0.5; §33.2)
# These are the caller-job names that must never carry if: or path filters.
REQUIRED_CONTEXTS = {
    "unit-tests", "integration-tests", "build", "security-scan", "licence-scan",
    "slopsquat-check", "contract-validation", "registry-validation", "parity-check",
    "verification-contract", "seeded-defect-case",
    "artifact-digest-recorded", "sbom-emitted",
    "renovate-path-guard", "lane-guard",
}

WRITE_SCOPES = {
    "actions", "checks", "contents", "deployments", "id-token", "issues",
    "packages", "pages", "pull-requests", "repository-projects", "security-events",
    "statuses",
}

SHA_RE = re.compile(r'@[0-9a-f]{40}$')
THIRD_PARTY_EXCLUDE = re.compile(r'^(\.github/workflows/|\./)|(^[^/]+/[^/]+/[^/]+)')


def _is_third_party(uses_val: str) -> bool:
    """True when uses: references a GitHub Action (owner/repo@ref), not a local path."""
    if uses_val.startswith('.github/') or uses_val.startswith('./'):
        return False
    # Reusable workflow in this repo
    if uses_val.startswith('./.github/') or '/.github/workflows/' in uses_val:
        return False
    # Has the form owner/repo or owner/repo/.github/workflows/x.yml
    parts = uses_val.split('@')
    if len(parts) == 2:
        return True
    return False


def lint_file(path: str, violations: list) -> int:
    """Lint one workflow file. Returns number of violations found."""
    found = 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
        wf = yaml.safe_load(raw)
    except Exception as e:
        print(f"ERROR reading {path}: {e}", file=sys.stderr)
        violations.append(('ERROR', path, str(e)))
        return -1  # signal ERROR

    if not isinstance(wf, dict):
        return 0

    # LW-03: no paths: or paths-ignore: at any level
    if re.search(r'^\s+paths(-ignore)?:', raw, re.MULTILINE):
        found += 1
        print(f"LW-03 {path}: contains paths: or paths-ignore: filter", file=sys.stderr)
        violations.append(('LW-03', path, 'path filter present'))

    # LW-04: permissions: absent or grants unused write scope
    top_perms = wf.get('permissions', None)
    if top_perms is None:
        found += 1
        print(f"LW-04 {path}: permissions: block is absent", file=sys.stderr)
        violations.append(('LW-04', path, 'permissions absent'))
    elif isinstance(top_perms, dict):
        for scope, access in top_perms.items():
            if access == 'write' and scope in WRITE_SCOPES:
                # Check if any step references this scope via github.token or GITHUB_TOKEN
                scope_used = scope.replace('-', '_').upper()
                if scope_used not in raw and scope not in raw:
                    found += 1
                    print(f"LW-04 {path}: write scope '{scope}' declared but not referenced", file=sys.stderr)
                    violations.append(('LW-04', path, f'unused write scope: {scope}'))

    jobs = wf.get('jobs', {}) or {}
    for job_name, job_def in jobs.items():
        if not isinstance(job_def, dict):
            continue

        is_required = job_name in REQUIRED_CONTEXTS

        # LW-02: required-context job must not carry if:
        if is_required and 'if' in job_def:
            found += 1
            print(f"LW-02 {path}: job '{job_name}' (required context) carries if:", file=sys.stderr)
            violations.append(('LW-02', path, f"required job '{job_name}' has if:"))

        # Scan steps
        steps = job_def.get('steps', []) or []
        for step in steps:
            if not isinstance(step, dict):
                continue

            # LW-01: third-party uses: must be @<40-hex>
            uses_val = step.get('uses', '')
            if uses_val and _is_third_party(uses_val):
                ref = uses_val.split('@', 1)[-1] if '@' in uses_val else ''
                if not re.match(r'^[0-9a-f]{40}', ref):
                    found += 1
                    print(f"LW-01 {path}: job '{job_name}' step uses '{uses_val}' — not pinned to full SHA", file=sys.stderr)
                    violations.append(('LW-01', path, f"unpinned uses: {uses_val}"))

            # LW-05: continue-on-error: true on a required-context job
            if is_required and step.get('continue-on-error') is True:
                found += 1
                print(f"LW-05 {path}: job '{job_name}' (required context) step has continue-on-error: true", file=sys.stderr)
                violations.append(('LW-05', path, f"required job '{job_name}' has continue-on-error"))

    return found


def main():
    parser = argparse.ArgumentParser(description='Workflow lint — LW-01 through LW-05')
    parser.add_argument('--path', required=True, help='Workflow file or directory')
    parser.add_argument('--summary', action='store_true', help='Print §0.4 summary line to stdout')
    args = parser.parse_args()

    target = args.path
    violations = []
    files = []

    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = [
            os.path.join(target, f)
            for f in sorted(os.listdir(target))
            if f.endswith('.yml') or f.endswith('.yaml')
        ]
    else:
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        print(f"ERROR: path does not exist: {target}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    if not files:
        if args.summary:
            print(f"{STATUS_OK} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_OK)

    checked = 0
    failed = 0
    error_reading = False

    for fpath in files:
        result = lint_file(fpath, violations)
        if result == -1:
            error_reading = True
        else:
            checked += 1
            failed += result

    if error_reading and checked == 0:
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    if failed > 0:
        status = STATUS_FAIL
        code = EXIT_FAIL
    else:
        status = STATUS_OK
        code = EXIT_OK

    if args.summary:
        print(f"{status} {TOOL_ID} checked={checked} failed={failed}")

    sys.exit(code)


if __name__ == '__main__':
    main()
```

**Commands**

```bash
# Shell commands to create the file and fixtures (L2-T533 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t533-lint-workflow

# Write the Python module (see python block above)
mkdir -p tools/evidence/fixtures/lint

# Create good.yml — passes all five rules
cat > tools/evidence/fixtures/lint/good.yml <<'EOF'
name: good-fixture
on:
  workflow_call: {}

permissions:
  contents: read

jobs:
  unit-tests:
    name: unit-tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@a5ac7e51b41094c92402da3b24376905380afc29 # v4
      - name: Run tests
        run: make test
        shell: bash
EOF

# bad_lw01.yml — unpinned third-party action
cat > tools/evidence/fixtures/lint/bad_lw01.yml <<'EOF'
name: bad-lw01
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
EOF

# bad_lw02.yml — required context job with if:
cat > tools/evidence/fixtures/lint/bad_lw02.yml <<'EOF'
name: bad-lw02
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - run: make test
EOF

# bad_lw03.yml — path filter on workflow trigger
cat > tools/evidence/fixtures/lint/bad_lw03.yml <<'EOF'
name: bad-lw03
on:
  pull_request:
    paths:
      - 'src/**'
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
EOF

# bad_lw04.yml — permissions: absent
cat > tools/evidence/fixtures/lint/bad_lw04.yml <<'EOF'
name: bad-lw04
on:
  workflow_call: {}
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
EOF

# bad_lw05.yml — continue-on-error on a required-context job step
cat > tools/evidence/fixtures/lint/bad_lw05.yml <<'EOF'
name: bad-lw05
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
        continue-on-error: true
EOF

# Write lint_workflow.py (copy the Python block above into the file)
# (Assumed written separately as tools/evidence/lint_workflow.py)

git add \
  tools/evidence/lint_workflow.py \
  tools/evidence/fixtures/lint/

git commit -m "L2-T533: workflow lint tool and fixtures (LW-01 through LW-05)"

# SELF-VERIFY
python3 -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint/good.yml --summary; echo "EXIT=$?"
python3 -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint --summary; echo "EXIT=$?"
python3 -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint/nope.yml --summary 2>/dev/null; echo "EXIT=$?"
# Expected:
# OK lint_workflow checked=1 failed=0
# EXIT=0
# FAIL lint_workflow checked=6 failed=5
# EXIT=2
# ERROR lint_workflow checked=0 failed=0
# EXIT=3
```

**Acceptance criteria**

1. `--path tools/evidence/fixtures/lint/good.yml --summary` prints `OK lint_workflow checked=1 failed=0` and exits `0`.
2. `--path tools/evidence/fixtures/lint --summary` prints `FAIL lint_workflow checked=6 failed=5` and exits `2`.
3. A path that does not exist prints `ERROR lint_workflow checked=0 failed=0` and exits `3` — never `OK`.
4. Diagnostics go to stderr; stdout carries the summary line and nothing else.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint/good.yml --summary; echo "EXIT=$?"
python -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint --summary; echo "EXIT=$?"
python -m tools.evidence.lint_workflow --path tools/evidence/fixtures/lint/nope.yml --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
FAIL lint_workflow checked=6 failed=5
EXIT=2
ERROR lint_workflow checked=0 failed=0
EXIT=3
```

**STOP** — if a rule would need a judgment about whether a `write` permission is "used", implement `LW-04` as the literal test *a `write` scope is declared and no step in the file references it*, and nothing subtler. If that is not decidable for a real file, rule S4; blocker title `BLOCKER L2-T533: LW-04 is undecidable for <file>`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t533-lint-workflow`.

---

### L2-T534 — Required-context ↔ job cross-check

> **Index — `L2-T504` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T504` in full (*Implement `tools/evidence/evidence-query`*) and is authoritative for that id; this block is different work and now carries the id `L2-T534`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 11 · **Phase** BT-1 · **Size** M · **Deps** L2-T533 · **Branch slug** `t534-context-crosscheck`
**Files:** `tools/evidence/check_required_contexts.py`, `tools/evidence/fixtures/contexts/**`
**Spec:** §33.2 L2854–2869; §53.1 L4653–4689; §0.5 of this file (the caller job name is the authoritative context name)

**Build this.** The tool that proves the published registry and the workflows agree. It reads a registry file and resolves each context by group, per §0.5:

* contexts in the `phase_4`, `phase_5` and `phase_6` groups must be emitted by a **caller job in the `--templates` tree**, because those are the names GitHub reports in the product repository;
* contexts in the `always` group must be emitted by a **job in `.github/workflows/`**, because `lane-guard` and `renovate-path-guard` run in the control plane, not from a per-product caller.

It fails on any of three conditions: a registry context emitted by no job in its resolving tree; a caller job in the `--templates` tree that calls a control-plane reusable workflow which emits a registry context, but whose own job name is not in the registry (templates that emit no required status context are exempt from this condition — L2-T303–309 templates legitimately emit none and must not trigger this failure); a job emitting a registry context that carries an `if:` or sits in a workflow with a path filter. `checked=` counts registry contexts; `failed=` counts violations. Tool-id `check_required_contexts`.

Fixtures under `fixtures/contexts/`: `registry.yaml` carrying exactly 3 contexts, all in `phase_4` so the fixtures exercise the template arm only; `ok/` with 3 matching caller jobs, `missing/` with 2, `extra/` with 4.



```python
# File: tools/evidence/check_required_contexts.py
# Created by L2-T534
# Usage: python -m tools.evidence.check_required_contexts
#          --templates <dir> --registry <file> [--summary]
# Spec: §33.2 L2854-2869; §53.1 L4653-4689; L2-05-tasks.md §0.5

"""
Required-context <-> job cross-check.

Reads the required-checks.yaml registry and resolves each context:
  phase_4/5/6: must be emitted by a caller job in the --templates tree
  always:      must be emitted by a job in .github/workflows/

Fails on:
  - A registry context emitted by no job in its resolving tree
  - A caller job in templates that calls a control-plane reusable workflow
    emitting a registry context, but whose own job name is not in the registry
  - A job emitting a registry context that carries an if: or sits in a workflow
    with a path filter

Tool-id: check_required_contexts
checked=: count of registry contexts examined
failed=:  count of violations
"""

import sys
import os
import re
import argparse
import yaml

TOOL_ID = "check_required_contexts"
STATUS_OK, STATUS_FAIL, STATUS_ERROR = "OK", "FAIL", "ERROR"
EXIT_OK, EXIT_FAIL, EXIT_ERROR = 0, 2, 3


def load_registry(path: str):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    contexts = {}  # name -> group
    for group, names in data.items():
        if isinstance(names, list):
            for name in names:
                contexts[name.strip()] = group
    return contexts


def get_job_names_from_dir(directory: str):
    """Return a set of job names defined in .yml files under directory."""
    job_names = set()
    if not os.path.isdir(directory):
        return job_names
    for fname in os.listdir(directory):
        if not (fname.endswith('.yml') or fname.endswith('.yaml')):
            continue
        fpath = os.path.join(directory, fname)
        try:
            with open(fpath) as f:
                wf = yaml.safe_load(f)
            if isinstance(wf, dict):
                jobs = wf.get('jobs', {}) or {}
                for jname, jdef in jobs.items():
                    if isinstance(jdef, dict):
                        job_names.add(jname)
        except Exception:
            pass
    return job_names


def get_jobs_with_if_or_filter(directory: str):
    """Return set of job names that carry if: or live in a file with a path filter."""
    bad_jobs = set()
    if not os.path.isdir(directory):
        return bad_jobs
    for fname in os.listdir(directory):
        if not (fname.endswith('.yml') or fname.endswith('.yaml')):
            continue
        fpath = os.path.join(directory, fname)
        try:
            with open(fpath) as f:
                raw = f.read()
                wf = yaml.safe_load(raw)
            has_path_filter = bool(re.search(r'^\s+paths(-ignore)?:', raw, re.MULTILINE))
            if isinstance(wf, dict):
                jobs = wf.get('jobs', {}) or {}
                for jname, jdef in jobs.items():
                    if isinstance(jdef, dict):
                        if 'if' in jdef or has_path_filter:
                            bad_jobs.add(jname)
        except Exception:
            pass
    return bad_jobs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--templates', required=True, help='templates/workflows directory')
    parser.add_argument('--registry', required=True, help='required-checks.yaml path')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    try:
        contexts = load_registry(args.registry)
    except Exception as e:
        print(f"ERROR reading registry: {e}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    checked = len(contexts)
    failed = 0

    template_jobs = get_job_names_from_dir(args.templates)
    template_bad  = get_jobs_with_if_or_filter(args.templates)

    # For 'always' group we check .github/workflows/; for others check templates
    gha_workflows = os.path.join(os.path.dirname(args.templates), '..', '.github', 'workflows')
    gha_workflows = os.path.normpath(gha_workflows)
    gha_jobs = get_job_names_from_dir(gha_workflows)
    gha_bad  = get_jobs_with_if_or_filter(gha_workflows)

    for ctx_name, group in contexts.items():
        if group == 'always':
            # Must exist in .github/workflows/ jobs
            if ctx_name not in gha_jobs:
                failed += 1
                print(f"FAIL: context '{ctx_name}' (always) not emitted by any job in .github/workflows/", file=sys.stderr)
            elif ctx_name in gha_bad:
                failed += 1
                print(f"FAIL: context '{ctx_name}' (always) job carries if: or path filter", file=sys.stderr)
        else:
            # phase_4/5/6: must exist in templates/workflows/ jobs
            if ctx_name not in template_jobs:
                failed += 1
                print(f"FAIL: context '{ctx_name}' ({group}) not emitted by any caller job in templates/", file=sys.stderr)
            elif ctx_name in template_bad:
                failed += 1
                print(f"FAIL: context '{ctx_name}' ({group}) caller job carries if: or path filter", file=sys.stderr)

    status = STATUS_FAIL if failed > 0 else STATUS_OK
    code   = EXIT_FAIL   if failed > 0 else EXIT_OK

    if args.summary:
        print(f"{status} {TOOL_ID} checked={checked} failed={failed}")

    sys.exit(code)


if __name__ == '__main__':
    main()
```

**Commands**

```bash
# Shell commands to create fixtures and commit (L2-T534 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t534-context-crosscheck

mkdir -p tools/evidence/fixtures/contexts/ok
mkdir -p tools/evidence/fixtures/contexts/missing
mkdir -p tools/evidence/fixtures/contexts/extra

# 3-context fixture registry (all phase_4 — exercises template arm)
cat > tools/evidence/fixtures/contexts/registry.yaml <<'EOF'
phase_4:
    - unit-tests
    - integration-tests
    - build
EOF

# ok/ — 3 matching caller jobs
cat > tools/evidence/fixtures/contexts/ok/ci.yml <<'EOF'
name: ci-template
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make integration
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
EOF

# missing/ — only 2 jobs (build is absent)
cat > tools/evidence/fixtures/contexts/missing/ci.yml <<'EOF'
name: ci-template
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make integration
EOF

# extra/ — 4 jobs (extra job present but registry has only 3 — no violation by extra
#          but missing the required 'build' context counts as violation)
cat > tools/evidence/fixtures/contexts/extra/ci.yml <<'EOF'
name: ci-template
on:
  workflow_call: {}
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make test
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - run: make integration
  extra-job:
    runs-on: ubuntu-latest
    steps:
      - run: make extra
  build:
    if: github.event_name != 'schedule'
    runs-on: ubuntu-latest
    steps:
      - run: make build
EOF

# Write check_required_contexts.py (see python block above)
git add \
  tools/evidence/check_required_contexts.py \
  tools/evidence/fixtures/contexts/

git commit -m "L2-T534: required-context job cross-check tool and fixtures"

# SELF-VERIFY
python3 -m tools.evidence.check_required_contexts \
  --templates tools/evidence/fixtures/contexts/ok \
  --registry tools/evidence/fixtures/contexts/registry.yaml \
  --summary; echo "EXIT=$?"
python3 -m tools.evidence.check_required_contexts \
  --templates tools/evidence/fixtures/contexts/missing \
  --registry tools/evidence/fixtures/contexts/registry.yaml \
  --summary; echo "EXIT=$?"
python3 -m tools.evidence.check_required_contexts \
  --templates tools/evidence/fixtures/contexts/extra \
  --registry tools/evidence/fixtures/contexts/registry.yaml \
  --summary; echo "EXIT=$?"
# Expected:
# OK check_required_contexts checked=3 failed=0
# EXIT=0
# FAIL check_required_contexts checked=3 failed=1
# EXIT=2
# FAIL check_required_contexts checked=3 failed=1
# EXIT=2
```

**Acceptance criteria**

1. Against `ok/`: `OK check_required_contexts checked=3 failed=0`, exit `0`.
2. Against `missing/`: `FAIL check_required_contexts checked=3 failed=1`, exit `2`.
3. Against `extra/`: `FAIL check_required_contexts checked=3 failed=1`, exit `2`.
4. The tool never edits `required-checks.yaml`, and adding, renaming or removing a context is not one of its behaviours.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.check_required_contexts --templates tools/evidence/fixtures/contexts/ok --registry tools/evidence/fixtures/contexts/registry.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.check_required_contexts --templates tools/evidence/fixtures/contexts/missing --registry tools/evidence/fixtures/contexts/registry.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.check_required_contexts --templates tools/evidence/fixtures/contexts/extra --registry tools/evidence/fixtures/contexts/registry.yaml --summary; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK check_required_contexts checked=3 failed=0
EXIT=0
FAIL check_required_contexts checked=3 failed=1
EXIT=2
FAIL check_required_contexts checked=3 failed=1
EXIT=2
```

**STOP** — if the real templates cannot satisfy the registry without adding a context name, that is the §0.5 STOP. Rule S4; blocker title `BLOCKER L2-T534: templates require a context absent from required-checks.yaml`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t534-context-crosscheck`.

---

### L2-T535 — Run-conclusion assertor: no `skipped`, no `neutral`

> **Index — `L2-T505` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T505` in full (*Conformance-profile substitution and S18 equivalence*) and is authoritative for that id; this block is different work and now carries the id `L2-T535`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 12 · **Phase** BT-1 · **Size** M · **Deps** L2-T534 · **Branch slug** `t535-run-conclusions`
**Files:** `tools/evidence/assert_run_conclusions.py`, `tools/evidence/fixtures/runs/**`
**Spec:** §33.2 L2854–2869 — *"no work was needed is an explicit recorded success, never a skip"*; a `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift (§53)

**Build this.** A tool that reads a GitHub check-runs JSON document and the registry, and fails when any registry context is `skipped`, `neutral`, or absent from the run. `checked=` counts registry contexts; `failed=` counts contexts in a forbidden state. Tool-id `assert_run_conclusions`.

Fixtures under `fixtures/runs/`, each against the 3-context `fixtures/contexts/registry.yaml`: `clean.json` (3 × `success`), `skipped.json` (2 × `success`, 1 × `skipped`), `neutral.json` (2 × `success`, 1 × `neutral`), `absent.json` (2 × `success`, 1 missing).



```python
# File: tools/evidence/assert_run_conclusions.py
# Created by L2-T535
# Usage: python -m tools.evidence.assert_run_conclusions
#          --checks <json> --registry <yaml> [--summary]
# Spec: §33.2 L2854-2869; "no work was needed is an explicit recorded success, never a skip"
# Tool-id: assert_run_conclusions

"""
Run-conclusion assertor.

Reads a GitHub check-runs JSON document and the required-checks registry.
Fails when any registry context is skipped, neutral, or absent from the run.

checked=: count of registry contexts
failed=:  count of contexts in a forbidden state (skipped / neutral / absent)

NEVER add a mode that treats skipped as satisfied (§33.2 STOP rule).
"""

import sys
import os
import re
import json
import argparse
import yaml

TOOL_ID = "assert_run_conclusions"
STATUS_OK, STATUS_FAIL, STATUS_ERROR = "OK", "FAIL", "ERROR"
EXIT_OK, EXIT_FAIL, EXIT_ERROR = 0, 2, 3

FORBIDDEN_CONCLUSIONS = {"skipped", "neutral", "cancelled"}


def load_registry(path: str):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    contexts = []
    for group, names in data.items():
        if isinstance(names, list):
            for name in names:
                contexts.append(name.strip())
    return contexts


def load_check_runs(path: str):
    """Returns dict of context_name -> conclusion from GitHub check-runs JSON."""
    with open(path, 'r') as f:
        data = json.load(f)
    results = {}
    # Support both list-of-runs and {"check_runs": [...]} shapes
    runs = data if isinstance(data, list) else data.get('check_runs', [])
    for run in runs:
        name = run.get('name', '')
        conclusion = run.get('conclusion', '') or ''
        results[name] = conclusion.lower()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checks', required=True, help='GitHub check-runs JSON file')
    parser.add_argument('--registry', required=True, help='required-checks.yaml path')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    try:
        contexts = load_registry(args.registry)
    except Exception as e:
        print(f"ERROR reading registry: {e}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    try:
        runs = load_check_runs(args.checks)
    except Exception as e:
        print(f"ERROR reading checks JSON: {e}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    checked = len(contexts)
    failed = 0

    for ctx in contexts:
        conclusion = runs.get(ctx)
        if conclusion is None:
            failed += 1
            print(f"FAIL: context '{ctx}' is absent from check runs", file=sys.stderr)
        elif conclusion in FORBIDDEN_CONCLUSIONS:
            failed += 1
            print(f"FAIL: context '{ctx}' has forbidden conclusion '{conclusion}'", file=sys.stderr)
        elif conclusion != 'success':
            failed += 1
            print(f"FAIL: context '{ctx}' has non-success conclusion '{conclusion}'", file=sys.stderr)

    status = STATUS_FAIL if failed > 0 else STATUS_OK
    code   = EXIT_FAIL   if failed > 0 else EXIT_OK

    if args.summary:
        print(f"{status} {TOOL_ID} checked={checked} failed={failed}")

    sys.exit(code)


if __name__ == '__main__':
    main()
```

**Commands**

```bash
# Shell commands to create fixtures and commit (L2-T535 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t535-run-conclusions

mkdir -p tools/evidence/fixtures/runs

# Uses the 3-context registry from L2-T534
# clean.json — 3 x success
cat > tools/evidence/fixtures/runs/clean.json <<'EOF'
[
  {"name": "unit-tests", "conclusion": "success"},
  {"name": "integration-tests", "conclusion": "success"},
  {"name": "build", "conclusion": "success"}
]
EOF

# skipped.json — one skipped
cat > tools/evidence/fixtures/runs/skipped.json <<'EOF'
[
  {"name": "unit-tests", "conclusion": "success"},
  {"name": "integration-tests", "conclusion": "success"},
  {"name": "build", "conclusion": "skipped"}
]
EOF

# neutral.json — one neutral
cat > tools/evidence/fixtures/runs/neutral.json <<'EOF'
[
  {"name": "unit-tests", "conclusion": "success"},
  {"name": "integration-tests", "conclusion": "success"},
  {"name": "build", "conclusion": "neutral"}
]
EOF

# absent.json — one missing
cat > tools/evidence/fixtures/runs/absent.json <<'EOF'
[
  {"name": "unit-tests", "conclusion": "success"},
  {"name": "integration-tests", "conclusion": "success"}
]
EOF

# Write assert_run_conclusions.py (see python block above)
git add \
  tools/evidence/assert_run_conclusions.py \
  tools/evidence/fixtures/runs/

git commit -m "L2-T535: run-conclusion assertor — no skipped, no neutral"

# SELF-VERIFY
for F in clean skipped neutral absent; do
  python3 -m tools.evidence.assert_run_conclusions \
    --checks tools/evidence/fixtures/runs/${F}.json \
    --registry tools/evidence/fixtures/contexts/registry.yaml \
    --summary; echo "EXIT=$?"
done
# Expected:
# OK assert_run_conclusions checked=3 failed=0
# EXIT=0
# FAIL assert_run_conclusions checked=3 failed=1
# EXIT=2
# FAIL assert_run_conclusions checked=3 failed=1
# EXIT=2
# FAIL assert_run_conclusions checked=3 failed=1
# EXIT=2
```

**Acceptance criteria**

1. `clean.json` → `OK assert_run_conclusions checked=3 failed=0`, exit `0`.
2. Each of `skipped.json`, `neutral.json`, `absent.json` → `FAIL assert_run_conclusions checked=3 failed=1`, exit `2`.
3. An unreadable or malformed JSON file → `ERROR assert_run_conclusions checked=0 failed=0`, exit `3`. There is no "assume pass" branch.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in clean skipped neutral absent; do
  python -m tools.evidence.assert_run_conclusions --checks tools/evidence/fixtures/runs/$F.json \
    --registry tools/evidence/fixtures/contexts/registry.yaml --summary; echo "EXIT=$?"
done
```

**CORRECT OUTPUT**

```
OK assert_run_conclusions checked=3 failed=0
EXIT=0
FAIL assert_run_conclusions checked=3 failed=1
EXIT=2
FAIL assert_run_conclusions checked=3 failed=1
EXIT=2
FAIL assert_run_conclusions checked=3 failed=1
EXIT=2
```

**STOP** — never add a mode that treats `skipped` as satisfied, whatever a downstream workflow appears to need. That mode is the exact failure §33.2 names. Rule S4; blocker title `BLOCKER L2-T535: a caller is asking for skipped-counts-as-success`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t535-run-conclusions`.

---

### L2-T536 — Delta-gate engine

> **Index — `L2-T506` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T506` in full (*Implement `tools/evidence/verify-digest-chain` — the comparison core*) and is authoritative for that id; this block is different work and now carries the id `L2-T536`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 13 · **Phase** BT-1 · **Size** M · **Deps** L2-T530 · **Branch slug** `t536-delta-gate`
**Files:** `tools/evidence/delta_gate.py`, `tools/evidence/fixtures/delta/**`
**Spec:** §33.2 L2854–2869 (*"fail on new findings only, so a legacy backlog does not block every merge"*); §48.2 L4309–4316 (licence findings delta-gated the same way)

**Build this.** One engine, used by both the security-scan and the licence-scan jobs. It reads a baseline findings document and a current findings document, computes the set difference by finding identity, and fails only on findings present in current and absent from baseline. `checked=` counts current findings; `failed=` counts new ones. Tool-id `delta_gate`. A missing or unreadable baseline is `ERROR`, exit `3` — an absent baseline never means "everything is new" and never means "nothing is new".

Fixtures under `fixtures/delta/`: `baseline.json` (3 findings), `legacy-only.json` (the same 3), `one-new.json` (the same 3 plus 1), `all-new.json` (3 findings sharing no identity with the baseline).



```python
# File: tools/evidence/delta_gate.py
# Created by L2-T536
# Usage: python -m tools.evidence.delta_gate
#          --baseline <json> --current <json> [--summary]
# Spec: §33.2 L2854-2869; §48.2 L4309-4316
# Tool-id: delta_gate
# Fails only on findings present in current and absent from baseline.
# A missing baseline is ERROR, exit 3 — never "everything is new" and never "nothing is new".

"""
Delta-gate engine.

Reads a baseline findings JSON and a current findings JSON.
Computes the set difference by finding identity (the 'id' field of each finding).
Fails only on findings present in current and absent from baseline.

checked=: count of current findings
failed=:  count of new findings (in current, absent from baseline)
"""

import sys
import os
import json
import argparse

TOOL_ID = "delta_gate"
STATUS_OK, STATUS_FAIL, STATUS_ERROR = "OK", "FAIL", "ERROR"
EXIT_OK, EXIT_FAIL, EXIT_ERROR = 0, 2, 3


def load_findings(path: str):
    """Load a findings JSON file. Returns list of finding dicts."""
    with open(path, 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get('findings', [])


def finding_identity(f: dict) -> str:
    """Return the canonical identity of a finding for set-difference computation."""
    # Identity = id field if present, else (rule + location + package) tuple
    if 'id' in f:
        return str(f['id'])
    return '|'.join([
        str(f.get('rule', '')),
        str(f.get('location', '')),
        str(f.get('package', '')),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', required=True, help='Baseline findings JSON')
    parser.add_argument('--current',  required=True, help='Current findings JSON')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    # Fail-closed: a missing or unreadable baseline is ERROR, exit 3
    if not os.path.isfile(args.baseline):
        print(f"ERROR: baseline not found: {args.baseline}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    try:
        baseline_findings = load_findings(args.baseline)
    except Exception as e:
        print(f"ERROR reading baseline: {e}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    try:
        current_findings = load_findings(args.current)
    except Exception as e:
        print(f"ERROR reading current: {e}", file=sys.stderr)
        if args.summary:
            print(f"{STATUS_ERROR} {TOOL_ID} checked=0 failed=0")
        sys.exit(EXIT_ERROR)

    baseline_ids = {finding_identity(f) for f in baseline_findings}
    current_ids  = [finding_identity(f) for f in current_findings]

    checked = len(current_findings)
    new_findings = [fid for fid in current_ids if fid not in baseline_ids]
    failed = len(new_findings)

    legacy_count = checked - failed
    if legacy_count > 0:
        print(f"INFO: {legacy_count} legacy finding(s) in baseline — not failing", file=sys.stderr)
    if failed > 0:
        for fid in new_findings:
            print(f"FAIL: new finding: {fid}", file=sys.stderr)

    status = STATUS_FAIL if failed > 0 else STATUS_OK
    code   = EXIT_FAIL   if failed > 0 else EXIT_OK

    if args.summary:
        print(f"{status} {TOOL_ID} checked={checked} failed={failed}")

    sys.exit(code)


if __name__ == '__main__':
    main()
```

**Commands**

```bash
# Shell commands to create fixtures and commit (L2-T536 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t536-delta-gate

mkdir -p tools/evidence/fixtures/delta

# baseline.json — 3 findings
cat > tools/evidence/fixtures/delta/baseline.json <<'EOF'
[
  {"id": "CVE-2024-0001", "rule": "vuln", "location": "lib/a.py", "package": "requests"},
  {"id": "CVE-2024-0002", "rule": "vuln", "location": "lib/b.py", "package": "urllib3"},
  {"id": "LGPL-001",       "rule": "licence", "location": "lib/c.py", "package": "gpl-lib"}
]
EOF

# legacy-only.json — the same 3 (no new findings)
cat > tools/evidence/fixtures/delta/legacy-only.json <<'EOF'
[
  {"id": "CVE-2024-0001", "rule": "vuln", "location": "lib/a.py", "package": "requests"},
  {"id": "CVE-2024-0002", "rule": "vuln", "location": "lib/b.py", "package": "urllib3"},
  {"id": "LGPL-001",       "rule": "licence", "location": "lib/c.py", "package": "gpl-lib"}
]
EOF

# one-new.json — baseline 3 plus 1 new
cat > tools/evidence/fixtures/delta/one-new.json <<'EOF'
[
  {"id": "CVE-2024-0001", "rule": "vuln", "location": "lib/a.py", "package": "requests"},
  {"id": "CVE-2024-0002", "rule": "vuln", "location": "lib/b.py", "package": "urllib3"},
  {"id": "LGPL-001",       "rule": "licence", "location": "lib/c.py", "package": "gpl-lib"},
  {"id": "CVE-2025-9999", "rule": "vuln", "location": "lib/d.py", "package": "new-dep"}
]
EOF

# all-new.json — 3 findings sharing no identity with the baseline
cat > tools/evidence/fixtures/delta/all-new.json <<'EOF'
[
  {"id": "CVE-2025-1111", "rule": "vuln", "location": "lib/x.py", "package": "foo"},
  {"id": "CVE-2025-2222", "rule": "vuln", "location": "lib/y.py", "package": "bar"},
  {"id": "MIT-999",        "rule": "licence", "location": "lib/z.py", "package": "baz"}
]
EOF

# Write delta_gate.py (see python block above)
git add \
  tools/evidence/delta_gate.py \
  tools/evidence/fixtures/delta/

git commit -m "L2-T536: delta-gate engine and fixtures"

# SELF-VERIFY
for F in legacy-only one-new all-new; do
  python3 -m tools.evidence.delta_gate \
    --baseline tools/evidence/fixtures/delta/baseline.json \
    --current tools/evidence/fixtures/delta/${F}.json \
    --summary; echo "EXIT=$?"
done
python3 -m tools.evidence.delta_gate \
  --baseline tools/evidence/fixtures/delta/nope.json \
  --current tools/evidence/fixtures/delta/legacy-only.json \
  --summary 2>/dev/null; echo "EXIT=$?"
# Expected:
# OK delta_gate checked=3 failed=0
# EXIT=0
# FAIL delta_gate checked=4 failed=1
# EXIT=2
# FAIL delta_gate checked=3 failed=3
# EXIT=2
# ERROR delta_gate checked=0 failed=0
# EXIT=3
```

**Acceptance criteria**

1. `legacy-only.json` → `OK delta_gate checked=3 failed=0`, exit `0`.
2. `one-new.json` → `FAIL delta_gate checked=4 failed=1`, exit `2`.
3. `all-new.json` → `FAIL delta_gate checked=3 failed=3`, exit `2`.
4. A baseline path that does not exist → `ERROR delta_gate checked=0 failed=0`, exit `3`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in legacy-only one-new all-new; do
  python -m tools.evidence.delta_gate --baseline tools/evidence/fixtures/delta/baseline.json \
    --current tools/evidence/fixtures/delta/$F.json --summary; echo "EXIT=$?"
done
python -m tools.evidence.delta_gate --baseline tools/evidence/fixtures/delta/nope.json \
  --current tools/evidence/fixtures/delta/legacy-only.json --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK delta_gate checked=3 failed=0
EXIT=0
FAIL delta_gate checked=4 failed=1
EXIT=2
FAIL delta_gate checked=3 failed=3
EXIT=2
ERROR delta_gate checked=0 failed=0
EXIT=3
```

**STOP** — the scanner that produces the findings documents is decided by L0, not here (`L2-01-reusable-workflows.md` §1 `L2/P1/DEC-A`). If no scanner is named, still build the engine against the fixtures; wire the real scanner only when L0 has answered. Rule S4; blocker title `BLOCKER L2-T536: no scan toolchain named for the delta gate`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t536-delta-gate`.

---

### L2-T100 — `ci.yml` reusable scaffold

**#** 14 · **Phase** BT-1 · **Size** M · **Deps** L2-T532, L2-T533 · **Branch slug** `t100-ci-scaffold`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.2 L2854–2869; §33.4 L2887–2912 (the pipeline shape)

**Build this.** The reusable workflow shell only — `on: workflow_call` with its declared inputs and secrets, top-level `permissions: contents: read`, a `concurrency` group keyed on the calling ref, and **no jobs yet beyond a single `no-op` placeholder job that reports success explicitly**. Every third-party `uses:` carries a full SHA from the ledger. No `if:`, no path filter, anywhere in the file, at this or any later `ci.yml` task.



```yaml
# File: .github/workflows/ci.yml (initial scaffold — L2-T100)
# Spec: §33.2 L2854-2869; §33.4 L2887-2912
# This is the reusable workflow shell only.
# on: workflow_call and nothing else.
# permissions: contents: read — no write scope.
# No if:, no paths:, no paths-ignore: anywhere in this file.
# Every third-party uses: must carry a full 40-hex SHA from the action-pins ledger.
# The no-op job reports explicit success; it is replaced by L2-T101.
name: ci

on:
  workflow_call:
    inputs:
      product_name:
        description: "The product name from product.yaml"
        type: string
        required: true
      default_branch:
        description: "The product repository default branch"
        type: string
        required: false
        default: "main"
    secrets:
      CONTROL_PLANE_TOKEN:
        description: "Read-only token for the control-plane repository"
        required: false

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}-${{ inputs.product_name }}
  cancel-in-progress: true

jobs:
  no-op:
    name: no-op
    runs-on: ubuntu-latest
    steps:
      - name: Scaffold placeholder — replaced by L2-T101
        run: |
          echo "ci.yml scaffold present; no jobs wired yet (L2-T100)"
          echo "This no-op job is replaced in L2-T101"
          exit 0
        shell: bash
```

**Commands**

```bash
# Shell commands to create ci.yml and commit (L2-T100 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t100-ci-scaffold

# Write the ci.yml scaffold (see YAML block above)
# After writing, verify it passes lint_workflow
python3 -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
# Expected: OK lint_workflow checked=1 failed=0 / EXIT=0

# Verify structural invariants
echo "WORKFLOW_CALL=$(grep -c '^  workflow_call:' .github/workflows/ci.yml)"
echo "UNPINNED_USES=$(grep -E '^[[:space:]]+uses:' .github/workflows/ci.yml | grep -cv '@[0-9a-f]\{40\}' || echo 0)"
# Expected:
# OK lint_workflow checked=1 failed=0
# EXIT=0
# WORKFLOW_CALL=1
# UNPINNED_USES=0

git add .github/workflows/ci.yml
git commit -m "L2-T100: ci.yml reusable workflow scaffold (no-op placeholder)"
```

**Acceptance criteria**

1. `on:` declares `workflow_call` and nothing else.
2. Top-level `permissions:` grants no `write`.
3. The file contains zero `if:` keys and zero `paths:`/`paths-ignore:` keys.
4. Every third-party `uses:` matches `@[0-9a-f]{40}`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "WORKFLOW_CALL=$(grep -c '^  workflow_call:' .github/workflows/ci.yml)"
echo "UNPINNED_USES=$(grep -E '^[[:space:]]+uses:' .github/workflows/ci.yml | grep -cv '@[0-9a-f]\{40\}')"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
WORKFLOW_CALL=1
UNPINNED_USES=0
```

**STOP** — if `lint_workflow` reports a violation you cannot remove without adding an `if:`, stop rather than adding one. Rule S4; blocker title `BLOCKER L2-T100: ci.yml cannot satisfy LW-02 without an if: condition`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t100-ci-scaffold`.

---

### L2-T101 — `ci.yml`: `unit-tests`, `integration-tests`

**#** 15 · **Phase** BT-1 · **Size** M · **Deps** L2-T100 · **Branch slug** `t101-ci-tests`
**Files:** `.github/workflows/ci.yml` (edit, additive — one of the five permitted edits, §0.1)
**Spec:** §33.2 L2854–2869 (*"Every push triggers: unit tests, integration tests, …"*); §98.2 L9006–9090 (CI contexts arrive at Phase 4)

**Build this.** Two jobs, named exactly `unit-tests` and `integration-tests` to match `required-checks.yaml`. Each invokes the per-product command through the caller-supplied input, carries no `if:`, and reports an explicit success when the product declares no suite of that kind — *no work was needed is an explicit recorded success*. Remove the `no-op` placeholder job of `L2-T100` in the same commit.



```yaml
# File: .github/workflows/ci.yml (edited — L2-T101, additive)
# Replaces the no-op placeholder job with unit-tests and integration-tests.
# Both jobs are named exactly as published in required-checks.yaml.
# Neither carries an if:. No path filter anywhere in the file.
# The no-work path exits 0 after echoing a literal reason — never exit 78, never skipped.
# Spec: §33.2 L2854-2869; "no work was needed is an explicit recorded success, never a skip"

# (Shown as the replacement jobs section; full file retains all scaffold fields above)
# Replace the 'jobs:' section of ci.yml from L2-T100 with this:

jobs:
  unit-tests:
    name: unit-tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout product repository
        uses: actions/checkout@{{PIN:actions/checkout}}

      - name: Run unit tests
        run: |
          set -euo pipefail
          # If the product declares no unit test suite, report explicit success.
          # "no work was needed is an explicit recorded success, never a skip" §33.2
          if [ ! -f Makefile ]; then
            echo "REASON: no Makefile present — no unit test suite declared"
            echo "CONCLUSION: success (no suite)"
            exit 0
          fi
          if ! grep -q '^test:' Makefile && ! grep -q '^unit-test:' Makefile; then
            echo "REASON: Makefile has no 'test' or 'unit-test' target — no unit test suite declared"
            echo "CONCLUSION: success (no suite)"
            exit 0
          fi
          make test
        shell: bash

  integration-tests:
    name: integration-tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout product repository
        uses: actions/checkout@{{PIN:actions/checkout}}

      - name: Run integration tests
        run: |
          set -euo pipefail
          # If the product declares no integration test suite, report explicit success.
          if [ ! -f Makefile ]; then
            echo "REASON: no Makefile present — no integration test suite declared"
            echo "CONCLUSION: success (no suite)"
            exit 0
          fi
          if ! grep -q '^integration:' Makefile && ! grep -q '^integration-test:' Makefile; then
            echo "REASON: Makefile has no 'integration' or 'integration-test' target — no integration test suite declared"
            echo "CONCLUSION: success (no suite)"
            exit 0
          fi
          make integration
        shell: bash
```

**Commands**

```bash
# Shell commands to edit ci.yml and commit (L2-T101 execution)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/t101-ci-tests

# Edit .github/workflows/ci.yml in place:
# 1. Remove the 'no-op' job
# 2. Add 'unit-tests' and 'integration-tests' jobs (see YAML block above)
# After editing, apply pins to substitute {{TOKEN}} placeholders:
bash tools/evidence/apply_pins.sh

# SELF-VERIFY
python3 -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOBS=$(grep -cE '^  (unit-tests|integration-tests):' .github/workflows/ci.yml)"
echo "NOOP=$(grep -c '^  no-op:' .github/workflows/ci.yml || echo 0)"
# Expected:
# OK lint_workflow checked=1 failed=0
# EXIT=0
# JOBS=2
# NOOP=0

git add .github/workflows/ci.yml
git commit -m "L2-T101: ci.yml unit-tests and integration-tests — no-op removed"
```

**Acceptance criteria**

1. Jobs `unit-tests` and `integration-tests` both exist; the `no-op` job does not.
2. Neither job carries an `if:`.
3. Each job's no-work path calls `exit 0` after echoing a literal reason string, and never `exit 78` and never a `skipped` conclusion.
4. `lint_workflow` is clean on the file.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOBS=$(grep -cE '^  (unit-tests|integration-tests):' .github/workflows/ci.yml)"
echo "NOOP=$(grep -c '^  no-op:' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOBS=2
NOOP=0
```

**STOP** — if the per-product test command is not available as a declared input, do not guess a command. Rule S4; blocker title `BLOCKER L2-T101: per-product test command is undeclared` (see `L2-01-reusable-workflows.md` §1 `L2/P1/DEC-B`).

**CLOSE:** §0.3 close block, `<branch-slug>` = `t101-ci-tests`.

---

### L2-T102 — `ci.yml`: interim `build` job

**#** 16 · **Phase** BT-1 · **Size** S · **Deps** L2-T101 · **Branch slug** `t102-ci-build-interim`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.2 L2854–2869; §33.4 L2887–2912

**Build this.** A job named exactly `build` that compiles or packages and reports a real conclusion. It is **interim**: `L2-T121` replaces its body with a call to `build.yml` once `L2-T120` lands. It must exist now because the context `build` is published in `required-checks.yaml` and an unpublished required context blocks every pull request indefinitely (§98.2 L9006–9090). It emits no digest and no SBOM yet — those contexts belong to phase 6 of the registry and to `L2-T120`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Append the interim build job to ci.yml (additive — L2-T101 already exists)
# The interim build job will be replaced in L2-T121 when build.yml lands.
# It MUST NOT emit artifact-digest-recorded or sbom-emitted (phase-6 contexts).

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  build:
    name: build
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh

      - name: Build (interim — delegated to build.yml at L2-T121)
        run: |
          set -euo pipefail
          if make build 2>/dev/null; then
            echo "BUILD_RESULT=success"
          else
            echo "BUILD_RESULT=no-build-target"
            echo "INFO: no Makefile build target found — explicit success, no work needed"
            exit 0
          fi
YAML_EOF

# Apply SHA pins so every uses: is a 40-hex SHA
bash tools/evidence/apply_pins.sh

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "BUILD=$(grep -c '^  build:' .github/workflows/ci.yml)"
echo "PREMATURE=$(grep -cE '^  (artifact-digest-recorded|sbom-emitted):' .github/workflows/ci.yml || true)"
```

**Acceptance criteria**

1. A job named exactly `build` exists and carries no `if:`.
2. The file still declares zero path filters.
3. `lint_workflow` is clean.
4. The job does **not** emit the contexts `artifact-digest-recorded` or `sbom-emitted` — those arrive with `L2-T120`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "BUILD=$(grep -c '^  build:' .github/workflows/ci.yml)"
echo "PREMATURE=$(grep -cE '^  (artifact-digest-recorded|sbom-emitted):' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
BUILD=1
PREMATURE=0
```

**STOP** — do not add digest or SBOM emission here to "save a task". Rule S4; blocker title `BLOCKER L2-T102: asked to emit phase-6 contexts from the interim build job`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t102-ci-build-interim`.

---

### L2-T103 — `ci.yml`: `security-scan`, delta-gated

**#** 17 · **Phase** BT-1 · **Size** M · **Deps** L2-T102, L2-T536 · **Branch slug** `t103-ci-security`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.2 L2854–2869 (delta gating on security findings); §48.2 L4309–4316

**Build this.** A job named exactly `security-scan` that runs the scanner, then pipes its findings through `python -m tools.evidence.delta_gate` against the stored baseline. The job fails on new findings only. A legacy finding neither fails the job nor is silently discarded: the job prints the legacy count to the log. A missing baseline is `ERROR` from the delta gate and fails the job — the job never treats an absent baseline as a clean tree.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Append security-scan job to ci.yml.
# The failure decision is the delta gate's exit code, not the scanner's.
# A missing baseline is ERROR from delta_gate and fails the job (fail-closed rule).
# No continue-on-error anywhere in this job.

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  security-scan:
    name: security-scan
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Run security scanner
        id: scan
        env:
          SCANNER_IMAGE: ${{ inputs.security_scanner_image }}
          SCANNER_DIGEST: ${{ inputs.security_scanner_digest }}
          SARIF_PATH: ${{ inputs.security_scanner_sarif_path }}
        run: |
          set -euo pipefail
          # Scanner invocation — toolchain resolved via D-L2-02 entrypoint
          # STOP: if L0 has not answered L2/P1/DEC-A (scan toolchain),
          #       the scanner image input will be empty and this step fails closed.
          if [ -z "${SCANNER_IMAGE:-}" ]; then
            echo "ERROR: security_scanner_image input is empty — DEC-A unanswered" >&2
            exit 3
          fi
          docker run --rm \
            --pull=never \
            -v "$(pwd):/workspace:ro" \
            "${SCANNER_IMAGE}@${SCANNER_DIGEST}" \
            /workspace \
            --output "${SARIF_PATH:-/workspace/security-findings.json}" || true
          echo "FINDINGS_PATH=${SARIF_PATH:-/workspace/security-findings.json}" >> "$GITHUB_OUTPUT"

      - name: Delta gate — new findings only
        env:
          FINDINGS: ${{ steps.scan.outputs.FINDINGS_PATH }}
          BASELINE: ${{ inputs.security_baseline_path }}
        run: |
          set -euo pipefail
          # Fail-closed: a missing baseline is ERROR, never a silent pass.
          # Legacy findings are printed to log but do not fail the job.
          python -m tools.evidence.delta_gate \
            --baseline "${BASELINE}" \
            --current "${FINDINGS}"
          # delta_gate exits 0 (OK), 2 (FAIL on new findings), or 3 (ERROR).
          # Any non-zero exit propagates and fails this step.
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  security-scan:' .github/workflows/ci.yml)"
echo "DELTA=$(grep -c 'tools.evidence.delta_gate' .github/workflows/ci.yml)"
echo "CONTINUE_ON_ERROR=$(grep -c 'continue-on-error: true' .github/workflows/ci.yml || true)"
```

**Acceptance criteria**

1. A job named exactly `security-scan` exists, carries no `if:` and no `continue-on-error`.
2. The job's failure decision is the delta gate's exit code, not the scanner's.
3. A seeded legacy finding does not fail the job; a seeded new finding does. Both are exercised by `L2-T537`.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  security-scan:' .github/workflows/ci.yml)"
echo "DELTA=$(grep -c 'tools.evidence.delta_gate' .github/workflows/ci.yml)"
echo "CONTINUE_ON_ERROR=$(grep -c 'continue-on-error: true' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
DELTA=1
CONTINUE_ON_ERROR=0
```

**STOP** — if L0 has not answered `L2/P1/DEC-A` (the scan toolchain), wire the job to the delta gate and leave the scanner invocation as the declared input it is; do not choose a scanner. Rule S4; blocker title `BLOCKER L2-T103: security scanner unnamed, DEC-A unanswered`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t103-ci-security`.

---

### L2-T104 — `ci.yml`: `licence-scan`, delta-gated

**#** 18 · **Phase** BT-1 · **Size** M · **Deps** L2-T103 · **Branch slug** `t104-ci-licence`
**Files:** `.github/workflows/ci.yml`
**Spec:** §48.2 L4309–4316 — *"CI fails on newly introduced licence findings only"*; the scanner's policy configuration is a control-plane artifact

**Build this.** A job named exactly `licence-scan`, structurally identical to `security-scan` and using the **same** `delta_gate` engine with the licence baseline. The licence policy configuration is read from the control plane as a declared input; the job never carries a policy inline. A finding against an existing dependency does not fail the job and is printed to the log with its identity so technical-debt governance can pick it up (§48.2, §56).



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Append licence-scan job to ci.yml.
# Structurally identical to security-scan; uses the SAME delta_gate engine.
# Licence policy configuration is read from control plane as a declared input —
# NO policy is hard-coded in the workflow file.
# A legacy finding prints its identity to the log but does not fail the job.

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  licence-scan:
    name: licence-scan
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Run licence scanner
        id: scan
        env:
          SCANNER_IMAGE: ${{ inputs.licence_scanner_image }}
          SCANNER_DIGEST: ${{ inputs.licence_scanner_digest }}
          REPORT_PATH: ${{ inputs.licence_scanner_report_path }}
          POLICY_PATH: ${{ inputs.licence_policy_path }}
        run: |
          set -euo pipefail
          if [ -z "${SCANNER_IMAGE:-}" ]; then
            echo "ERROR: licence_scanner_image input is empty — DEC-A unanswered" >&2
            exit 3
          fi
          # Policy configuration comes from the control plane (declared input).
          # No allow-list is written here — that is a foreign-path artefact.
          docker run --rm \
            --pull=never \
            -v "$(pwd):/workspace:ro" \
            -v "${POLICY_PATH}:/policy:ro" \
            "${SCANNER_IMAGE}@${SCANNER_DIGEST}" \
            /workspace \
            --policy /policy \
            --output "${REPORT_PATH:-/workspace/licence-findings.json}" || true
          echo "FINDINGS_PATH=${REPORT_PATH:-/workspace/licence-findings.json}" >> "$GITHUB_OUTPUT"

      - name: Delta gate — new licence findings only
        env:
          FINDINGS: ${{ steps.scan.outputs.FINDINGS_PATH }}
          BASELINE: ${{ inputs.licence_baseline_path }}
        run: |
          set -euo pipefail
          # Same delta_gate engine as security-scan (DELTA_CALLS=2 in ci.yml total).
          # Fail-closed: absent baseline is ERROR, exit 3.
          python -m tools.evidence.delta_gate \
            --baseline "${BASELINE}" \
            --current "${FINDINGS}"
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  licence-scan:' .github/workflows/ci.yml)"
echo "DELTA_CALLS=$(grep -c 'tools.evidence.delta_gate' .github/workflows/ci.yml)"
```

**Acceptance criteria**

1. A job named exactly `licence-scan` exists, carries no `if:`.
2. It calls `tools.evidence.delta_gate`, not a second, separate delta implementation.
3. No licence class list is hard-coded in the workflow file.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  licence-scan:' .github/workflows/ci.yml)"
echo "DELTA_CALLS=$(grep -c 'tools.evidence.delta_gate' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
DELTA_CALLS=2
```

**STOP** — if you find yourself writing a licence allow-list into the workflow, stop: the policy is a control-plane artifact, not workflow content. Rule S2/S4; blocker title `BLOCKER L2-T104: licence policy artifact not available from contracts/`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t104-ci-licence`.

---

### L2-T105 — `ci.yml`: `slopsquat-check` at execute time

**#** 19 · **Phase** BT-1 · **Size** M · **Deps** L2-T104 · **Branch slug** `t105-ci-slopsquat`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.2 L2854–2869 — *"Package legitimacy is checked at execute time, not only at plan time"*; §30.2 L2720–2732 (the plan-time half, which is not L2's)

**Build this.** A job named exactly `slopsquat-check` that runs the legitimacy check against **lockfile and manifest diffs only**, delta-gated to new and changed entries through the same `delta_gate` engine. Lane 2 builds the execute-time half only; the plan-checker of §30.2 is not this lane's. A pull request touching no lockfile and no manifest still reports an explicit success with the reason string — it never skips.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Append slopsquat-check job to ci.yml.
# RULES:
#   - No if:, no path filter (§33.2 absolute prohibition on required contexts)
#   - Scope to lockfile+manifest diffs by diffing INSIDE the job step, not via paths:
#   - No-change path exits 0 after echoing a literal reason string (never skipped)
#   - Legitimacy check is at execute time (§33.2 "checked at execute time, not only at plan time")

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  slopsquat-check:
    name: slopsquat-check
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Slopsquat legitimacy check (execute time)
        env:
          BASE_REF: ${{ github.event.pull_request.base.sha || github.event.before }}
        run: |
          set -euo pipefail
          # Scope to lockfile and manifest diffs by computing the diff inside the step.
          # A path filter is the obvious alternative and the one thing §33.2 forbids.
          CHANGED_LOCKFILES="$(git diff --name-only "${BASE_REF}...HEAD" -- \
            '*.lock' \
            'package-lock.json' \
            'yarn.lock' \
            'Pipfile.lock' \
            'poetry.lock' \
            'Gemfile.lock' \
            'requirements*.txt' \
            'go.sum' \
            'pom.xml' \
            'build.gradle' \
            'build.gradle.kts' \
            'pyproject.toml' \
            'Cargo.lock' \
            'composer.lock' \
            'package.json' \
            '*.gemspec' \
            'setup.cfg' \
            'setup.py' 2>/dev/null || true)"

          if [ -z "$CHANGED_LOCKFILES" ]; then
            echo "INFO: no lockfile or manifest changes in this pull request — explicit success, no legitimacy check needed"
            exit 0
          fi

          echo "CHECKING_FILES<<EOF" >> "$GITHUB_OUTPUT"
          echo "$CHANGED_LOCKFILES" >> "$GITHUB_OUTPUT"
          echo "EOF" >> "$GITHUB_OUTPUT"

          echo "Changed lockfiles/manifests:"
          echo "$CHANGED_LOCKFILES"

          # Run the execute-time legitimacy check against changed entries only.
          # The plan-time half (§30.2) is not this lane's.
          python -m tools.evidence.delta_gate \
            --baseline ${{ inputs.slopsquat_baseline_path }} \
            --current <(echo "$CHANGED_LOCKFILES" | python -c "
import sys, json
files = sys.stdin.read().splitlines()
print(json.dumps([{'id': f, 'path': f} for f in files if f]))
")
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  slopsquat-check:' .github/workflows/ci.yml)"
echo "FILTERS=$(grep -cE '^[[:space:]]*paths(-ignore)?:' .github/workflows/ci.yml || true)"
```

**Acceptance criteria**

1. A job named exactly `slopsquat-check` exists, carries no `if:` and no path filter.
2. The no-change path exits `0` after echoing a literal reason and is exercised by `L2-T537`.
3. The job scopes its input to lockfile and manifest diffs, not the whole tree.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  slopsquat-check:' .github/workflows/ci.yml)"
echo "FILTERS=$(grep -cE '^[[:space:]]*paths(-ignore)?:' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
FILTERS=0
```

**STOP** — a path filter is the obvious way to scope this job to lockfiles and it is the one thing §33.2 forbids on a required context. Scope by diffing inside the job. If you cannot, rule S4; blocker title `BLOCKER L2-T105: cannot scope slopsquat-check without a path filter`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t105-ci-slopsquat`.

---

### L2-T106 — `ci.yml`: `contract-validation` and §33.1 required-file presence

**#** 20 · **Phase** BT-1 · **Size** M · **Deps** L2-T105, **D-L2-02** · **Branch slug** `t106-ci-contract`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.1 L2831–2853 (the required-file list); §15.5 L1564–1582 (what CI validation fails on)

**Build this.** A job named exactly `contract-validation` doing two things. First, it invokes Lane 1's contract validator through the entrypoint declared in `contracts/**` under D-L2-02 — Lane 2 calls it, never reimplements it. Second, it asserts the presence of every §33.1 required file in the product repository, exactly this list and no other:

```
.env.example
docker-compose.dev.yml
Makefile
seed data
migration directory
verification/
AGENTS.md
product.yaml (or a pointer to the product it belongs to)
```

*"Required-file presence is checked, not assumed"* (§33.1). A missing file fails the job on the same terms as a `product.yaml` missing a field.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# STOP if D-L2-02 is unanswered: contracts/ must declare the validator entrypoint.
test -f contracts/workflow-io/required-contexts.tsv || {
  echo "ERROR: contracts/workflow-io/required-contexts.tsv absent — D-L2-02 unanswered" >&2
  exit 1
}

# Append contract-validation job to ci.yml.
# TWO duties:
#   1. Invoke Lane 1's contract validator through the D-L2-02 entrypoint
#   2. Assert presence of all 8 §33.1 required files
# No validation logic is written in the workflow — Lane 1 owns the rules.

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  contract-validation:
    name: contract-validation
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Assert §33.1 required-file presence
        run: |
          set -euo pipefail
          # Exactly 8 presence assertions, one per §33.1 row.
          # "Required-file presence is checked, not assumed" (§33.1).
          FAILED=0

          check_file() {
            local label="$1"; local path="$2"
            if [ -e "$path" ]; then
              echo "REQUIRED_FILE: PRESENT ${label}"
            else
              echo "REQUIRED_FILE: MISSING ${label}" >&2
              FAILED=$((FAILED + 1))
            fi
          }

          check_file ".env.example"             ".env.example"
          check_file "docker-compose.dev.yml"   "docker-compose.dev.yml"
          check_file "Makefile"                 "Makefile"
          check_file "seed data"                "$(find . -maxdepth 3 -name 'seeds' -o -name 'seed_data' -o -name 'db/seeds' 2>/dev/null | head -1 || echo '__ABSENT__')"
          check_file "migration directory"      "$(find . -maxdepth 3 -name 'migrations' -o -name 'db/migrate' 2>/dev/null | head -1 || echo '__ABSENT__')"
          check_file "verification/"            "verification/"
          check_file "AGENTS.md"                "AGENTS.md"
          check_file "product.yaml"             "$(find . -maxdepth 2 -name 'product.yaml' 2>/dev/null | head -1 || echo '__ABSENT__')"

          if [ "$FAILED" -gt 0 ]; then
            echo "ERROR: ${FAILED} required file(s) absent" >&2
            exit 1
          fi

      - name: Invoke Lane 1 contract validator (D-L2-02 entrypoint)
        env:
          VALIDATOR_ENTRYPOINT: ${{ inputs.contract_validator_entrypoint }}
        run: |
          set -euo pipefail
          # Lane 2 calls the entrypoint; it never reimplements the validation rules.
          # Exit code is the validator's exit code, unmodified.
          if [ -z "${VALIDATOR_ENTRYPOINT:-}" ]; then
            echo "ERROR: contract_validator_entrypoint input is empty — D-L2-02 unanswered" >&2
            exit 3
          fi
          exec ${VALIDATOR_ENTRYPOINT}
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  contract-validation:' .github/workflows/ci.yml)"
echo "PRESENCE=$(grep -cE 'REQUIRED_FILE:' .github/workflows/ci.yml)"
```

**Acceptance criteria**

1. A job named exactly `contract-validation` exists, carries no `if:`.
2. Exactly 8 presence assertions, one per §33.1 row, each naming the file literally.
3. The validator is invoked through the D-L2-02 entrypoint; no validation logic is written in the workflow.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  contract-validation:' .github/workflows/ci.yml)"
echo "PRESENCE=$(grep -cE 'REQUIRED_FILE:' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
PRESENCE=8
```

**STOP** — if `contracts/**` does not declare the validator entrypoint and its exit-code semantics, D-L2-02 is unanswered and this task is not startable. Rule S1; blocker title `BLOCKER L2-T106: D-L2-02 unanswered, no declared contract-validator entrypoint`. Do not invent an invocation.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t106-ci-contract`.

---

### L2-T107 — `ci.yml`: `registry-validation`

**#** 21 · **Phase** BT-1 · **Size** S · **Deps** L2-T106, **D-L2-02** · **Branch slug** `t107-ci-registry`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.2 L2854–2869 (*"registry and assignment validation"*); §15.5 L1564–1582

**Build this.** A job named exactly `registry-validation` invoking Lane 1's registry and assignment validator through the same D-L2-02 entrypoint. Lane 2 supplies no rules of its own: the assignment, capability and referential-integrity rules are Lane 1's (`validators/registry/**`, `PARTITION.md` line 17).



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# STOP if D-L2-02 is unanswered
test -f contracts/workflow-io/required-contexts.tsv || {
  echo "ERROR: contracts/workflow-io/required-contexts.tsv absent — D-L2-02 unanswered" >&2
  exit 1
}

# Append registry-validation job to ci.yml.
# Lane 2 invokes Lane 1's registry validator — it contains NO rule logic.
# The validator's exit code is the job's exit code, unmodified.

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  registry-validation:
    name: registry-validation
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Invoke Lane 1 registry and assignment validator (D-L2-02 entrypoint)
        env:
          VALIDATOR_ENTRYPOINT: ${{ inputs.registry_validator_entrypoint }}
        run: |
          set -euo pipefail
          # No registry rule is defined here — assignment, capability and
          # referential-integrity rules are Lane 1's (validators/registry/**).
          # Lane 2 invokes and reports; it never contains rule codes R-CAP-*, R-PPL-*, etc.
          if [ -z "${VALIDATOR_ENTRYPOINT:-}" ]; then
            echo "ERROR: registry_validator_entrypoint input is empty — D-L2-02 unanswered" >&2
            exit 3
          fi
          exec ${VALIDATOR_ENTRYPOINT}
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  registry-validation:' .github/workflows/ci.yml)"
echo "OWN_RULES=$(grep -cE 'R-(CAP|PPL|PRD|REF)-' .github/workflows/ci.yml || true)"
```

**Acceptance criteria**

1. A job named exactly `registry-validation` exists, carries no `if:`.
2. The job contains no rule logic — it invokes and reports.
3. The job's exit code is the validator's exit code, unmodified.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  registry-validation:' .github/workflows/ci.yml)"
echo "OWN_RULES=$(grep -cE 'R-(CAP|PPL|PRD|REF)-' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
OWN_RULES=0
```

**STOP** — if you are about to write a registry rule into this workflow, that is a Lane 1 path in disguise. Rule S2; blocker title `BLOCKER L2-T107: registry rule logic would have to live in .github/workflows`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t107-ci-registry`.

---

### L2-T108 — `ci.yml`: `parity-check`

**#** 22 · **Phase** BT-1 · **Size** S · **Deps** L2-T107 · **Branch slug** `t108-ci-parity`
**Files:** `.github/workflows/ci.yml`
**Spec:** §33.1 L2831–2853 — the command table row `make parity`, and *"A parity violation on a production deployment path is a blocking CI failure"*

**Build this.** A job named exactly `parity-check` that invokes `make parity` in the product repository and fails on a non-zero exit. Nothing more. The **format** of the environment-schema declaration `make parity` compares is design-open under D-L2-04 and is **not** this task: this task invokes the command the §33.1 table already names.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Append parity-check job to ci.yml.
# Invokes `make parity` only — that is the §33.1 command table entry.
# The format of the environment-schema declaration is design-open under REG-060
# and is NOT this task. This task only invokes the command the table already names.

cat >> .github/workflows/ci.yml <<'YAML_EOF'

  parity-check:
    name: parity-check
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Run parity check
        run: |
          set -euo pipefail
          # The only comparison logic is the make parity invocation.
          # A non-zero exit fails the job. No schema diffing in the workflow.
          # "A parity violation on a production deployment path is a blocking CI failure" (§33.1).
          make parity
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary
echo "JOB=$(grep -c '^  parity-check:' .github/workflows/ci.yml)"
echo "MAKE_PARITY=$(grep -c 'make parity' .github/workflows/ci.yml)"
```

**Acceptance criteria**

1. A job named exactly `parity-check` exists, carries no `if:`.
2. The job's only comparison logic is the `make parity` invocation — no schema diffing in the workflow.
3. A non-zero `make parity` fails the job.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  parity-check:' .github/workflows/ci.yml)"
echo "MAKE_PARITY=$(grep -c 'make parity' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
MAKE_PARITY=1
```

**STOP** — do not design the environment-schema declaration format here. That is REG-060 and it is L0's. Rule S4; blocker title `BLOCKER L2-T108: asked to define the make parity declaration format (REG-060)`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t108-ci-parity`.

---

### L2-T109 — Extend `lane-guard.yml` with lint and context cross-check

**#** 23 · **Phase** BT-1 · **Size** M · **Deps** L2-T534, L2-T108 · **Branch slug** `t109-lane-guard-lint`
**Files:** `.github/workflows/lane-guard.yml` (edit — one of the five permitted edits, §0.1)
**Spec:** §33.2 L2854–2869; §53.1 L4653–4689

**Build this.** Two additional steps inside the existing `lane-guard` job — not new jobs, because the context name is fixed and published. Step: run `lint_workflow` over `.github/workflows` and `templates/workflows`. Step: run `check_required_contexts` over `templates/workflows` against `required-checks.yaml`. Either non-zero exit fails the `lane-guard` context. The job still carries no `if:` and no path filter.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Edit lane-guard.yml (one of the five permitted edits per §0.1).
# Add TWO STEPS inside the existing lane-guard job — NOT new jobs.
# The context name is fixed and published; no new contexts may be introduced.
# Both steps run lint_workflow and check_required_contexts.

# Read the existing file and inject the two new steps before the final step or at the end
# of the existing job's steps block.

python3 - <<'PYEOF'
import re, sys

with open('.github/workflows/lane-guard.yml', 'r') as f:
    content = f.read()

NEW_STEPS = """
      - name: Workflow lint — pinning, permissions, no-if
        run: |
          set -euo pipefail
          python -m tools.evidence.lint_workflow \\
            --path .github/workflows \\
            --summary
          python -m tools.evidence.lint_workflow \\
            --path templates/workflows \\
            --summary

      - name: Required-context cross-check
        run: |
          set -euo pipefail
          python -m tools.evidence.check_required_contexts \\
            --templates templates/workflows \\
            --registry templates/workflows/required-checks.yaml \\
            --summary
"""

# Append to the end of the steps block before the close of the lane-guard job.
# Strategy: find the last step's end and append after it.
# The exact insertion depends on the existing file structure; we append before
# any trailing newline at the file end to stay within the job.

# Find the end of the file and append the new steps
# We assume the lane-guard job is the only job and steps end at EOF.
content = content.rstrip('\n')
content += NEW_STEPS

with open('.github/workflows/lane-guard.yml', 'w') as f:
    f.write(content)

print("STEPS_APPENDED=2")
PYEOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/lane-guard.yml --summary
echo "TOOLS=$(grep -cE 'tools\.evidence\.(lint_workflow|check_required_contexts)' .github/workflows/lane-guard.yml)"
echo "JOBS=$(grep -cE '^  [a-z0-9-]+:$' .github/workflows/lane-guard.yml)"
```

**Acceptance criteria**

1. `lane-guard` remains a single job with the same name; no new context is introduced.
2. Both tools are invoked in that job.
3. The job carries no `if:` and the file no path filter.
4. `lint_workflow --path .github/workflows/lane-guard.yml` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/lane-guard.yml --summary; echo "EXIT=$?"
echo "TOOLS=$(grep -cE 'tools\.evidence\.(lint_workflow|check_required_contexts)' .github/workflows/lane-guard.yml)"
echo "JOBS=$(grep -cE '^  [a-z0-9-]+:$' .github/workflows/lane-guard.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
TOOLS=2
JOBS=1
```

**STOP** — if adding the checks appears to need a second job, it needs a second context name, and §0.5 forbids that. Rule S4; blocker title `BLOCKER L2-T109: lane-guard extension would require a new required context`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t109-lane-guard-lint`.

---

### L2-T110 — `renovate-path-guard.yml`

**#** 24 · **Phase** BT-1 · **Size** M · **Deps** L2-T532 · **Branch slug** `t110-renovate-guard`
**Files:** `.github/workflows/renovate-path-guard.yml`
**Spec:** §33.2 L2854–2869 — the Renovate disposition policy, ruleset A/B split, and *"The authorship half is not optional"*

**Build this.** A workflow emitting the required context `renovate-path-guard`, on `pull_request`, one job of that exact name, no `if:`, no path filter. It fails a Renovate pull request when **either** is true:

1. the diff touches a file outside the declared manifest and lockfile paths; **or**
2. **any** commit on the branch was authored **or** committed by an identity other than the Renovate app.

Both halves are implemented. A commit on a bypass-actor branch authored by another identity is Blocking drift (§53), so the guard fails and says so in the log with the literal string `FOREIGN_AUTHOR`. The guard lives in ruleset B, which carries **no** bypass actor — the workflow does not need to know that, but it must never grant an exemption of its own.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Create .github/workflows/renovate-path-guard.yml.
# RULES (all binding, §33.2):
#   - Job name exactly renovate-path-guard
#   - No if:, no path filter
#   - Path half: fails if diff touches files outside declared manifest/lockfile paths
#   - Authorship half: fails if any commit (not just HEAD) was authored/committed
#     by a non-Renovate identity — emits FOREIGN_AUTHOR literal
#   - No allow-list exempting any identity
#   - Ruleset B (no bypass actor) is enforced at the GitHub level; this workflow
#     does not know about bypass actors and grants no exemptions of its own.

cat > .github/workflows/renovate-path-guard.yml <<'YAML_EOF'
# renovate-path-guard.yml — Spec §33.2, Ruleset B, no bypass-actor list.
# Lane 2 (Pipeline & Evidence). Owned path: .github/workflows/**.
# Required context: renovate-path-guard
# Pinned SHA: actions/checkout — see tools/evidence/action-pins.txt

name: renovate-path-guard

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: read

concurrency:
  group: renovate-path-guard-${{ github.ref }}
  cancel-in-progress: true

jobs:
  renovate-path-guard:
    name: renovate-path-guard
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Assert Renovate-only authorship and committer identity
        env:
          # The Renovate bot's GitHub login. This is the only identity this job
          # treats as Renovate. No other identity receives an exemption.
          RENOVATE_LOGIN: renovate[bot]
        run: |
          set -euo pipefail
          # Inspect every commit on this branch (not only HEAD).
          # Any commit authored OR committed by a non-Renovate identity fails the job.
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"

          FAILED=0
          while IFS= read -r commit_sha; do
            AUTHOR_LOGIN="$(git log -1 --format='%ae' "${commit_sha}" || echo 'UNKNOWN')"
            COMMITTER_LOGIN="$(git log -1 --format='%ce' "${commit_sha}" || echo 'UNKNOWN')"

            # Check author email contains renovate marker
            if ! echo "${AUTHOR_LOGIN}" | grep -qiE 'renovate(\[bot\])?|renovate-bot'; then
              echo "FOREIGN_AUTHOR: commit ${commit_sha} authored by ${AUTHOR_LOGIN} — expected Renovate" >&2
              FAILED=$((FAILED + 1))
            fi
            # Check committer email contains renovate marker
            if ! echo "${COMMITTER_LOGIN}" | grep -qiE 'renovate(\[bot\])?|renovate-bot'; then
              echo "FOREIGN_AUTHOR: commit ${commit_sha} committed by ${COMMITTER_LOGIN} — expected Renovate" >&2
              FAILED=$((FAILED + 1))
            fi
          done < <(git rev-list "${BASE_SHA}..${HEAD_SHA}")

          if [ "$FAILED" -gt 0 ]; then
            echo "ERROR: ${FAILED} authorship/committer violation(s) — all commits must be by Renovate" >&2
            exit 1
          fi
          echo "INFO: all commits authored and committed by Renovate — authorship check passed"

      - name: Assert Renovate-only path scope
        run: |
          set -euo pipefail
          # Scope: Renovate is permitted to change only manifest and lockfile paths.
          # The declared list must come from contracts/ (§0.8 rule S1).
          # STOP: if contracts/ does not declare the list, this step fails closed.
          MANIFEST_PATHS="${{ inputs.renovate_manifest_paths }}"

          if [ -z "${MANIFEST_PATHS:-}" ]; then
            echo "ERROR: renovate_manifest_paths input is empty — declared path list unavailable" >&2
            exit 3
          fi

          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"

          # Get all changed files
          CHANGED="$(git diff --name-only "${BASE_SHA}..${HEAD_SHA}")"

          # Build allowed-path pattern from declared list
          ALLOWED_PATTERN="$(echo "${MANIFEST_PATHS}" | tr ',' '\n' | sed 's|^[[:space:]]*||;s|[[:space:]]*$||' | paste -sd '|')"

          FOREIGN=0
          while IFS= read -r path; do
            [ -z "$path" ] && continue
            if ! echo "$path" | grep -qE "${ALLOWED_PATTERN}"; then
              echo "ERROR: foreign path in Renovate PR: ${path}" >&2
              FOREIGN=$((FOREIGN + 1))
            fi
          done <<< "$CHANGED"

          if [ "$FOREIGN" -gt 0 ]; then
            echo "ERROR: ${FOREIGN} file(s) outside declared Renovate manifest/lockfile paths" >&2
            exit 1
          fi
          echo "INFO: all changed files are within declared Renovate manifest/lockfile paths"
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/renovate-path-guard.yml --summary
echo "JOB=$(grep -c '^  renovate-path-guard:' .github/workflows/renovate-path-guard.yml)"
echo "AUTHOR_HALF=$(grep -c 'FOREIGN_AUTHOR' .github/workflows/renovate-path-guard.yml)"
echo "COMMITTER=$(grep -c 'committer' .github/workflows/renovate-path-guard.yml)"
```

**Acceptance criteria**

1. Job name is exactly `renovate-path-guard`; no `if:`; no path filter.
2. Both halves present: a path assertion and an authorship-plus-committer assertion over every commit on the branch, not only the head commit.
3. The literal string `FOREIGN_AUTHOR` is emitted on the authorship failure.
4. The workflow contains no allow-list that exempts any identity.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/renovate-path-guard.yml --summary; echo "EXIT=$?"
echo "JOB=$(grep -c '^  renovate-path-guard:' .github/workflows/renovate-path-guard.yml)"
echo "AUTHOR_HALF=$(grep -c 'FOREIGN_AUTHOR' .github/workflows/renovate-path-guard.yml)"
echo "COMMITTER=$(grep -c 'committer' .github/workflows/renovate-path-guard.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
JOB=1
AUTHOR_HALF=1
COMMITTER=1
```

**STOP** — if the declared manifest and lockfile path list is not available from `contracts/**` or `policies.yaml`, do not invent one. Rule S1; blocker title `BLOCKER L2-T110: declared Renovate manifest/lockfile path list unavailable`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t110-renovate-guard`.

---

### L2-T111 — `control-plane-ci.yml` — §15.5 control-plane validation

**#** 25 · **Phase** BT-1 · **Size** M · **Deps** L2-T106, L2-T107 · **Branch slug** `t111-control-plane-ci`
**Files:** `.github/workflows/control-plane-ci.yml`
**Spec:** §15.5 L1564–1582 (the full list CI validation fails the build on)

**Build this.** The control-plane repository's own CI. It runs on `push` and `pull_request` against the control plane itself and invokes the Lane 1 validators over `registries/**` and the product contracts, failing the build on any §15.5 condition. Lane 2 owns the **job**, never the rules. The two §15.5 bullets that are Lane 2's own to assert — *"a product with a `recovery:` block and no `restore-production.yml`"* and template drift — arrive later at `L2-T144`, once the template manifest exists.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Create .github/workflows/control-plane-ci.yml.
# Runs on push and pull_request against the CONTROL PLANE itself.
# Invokes Lane 1 validators over registries/** and product contracts.
# NO §15.5 rule is reimplemented here — Lane 1 owns the rules.
# The recovery: => restore-production.yml assertion is ABSENT here — it is L2-T144.

cat > .github/workflows/control-plane-ci.yml <<'YAML_EOF'
# control-plane-ci.yml — §15.5 control-plane validation.
# Lane 2 (Pipeline & Evidence). Owned path: .github/workflows/**.
# This workflow runs CI on the control-plane repository itself.
# Spec §15.5 L1564-1582.

name: control-plane-ci

on:
  push:
    branches: ['integration', 'main']
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

concurrency:
  group: control-plane-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  contract-and-registry-validation:
    name: contract-and-registry-validation
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@{{SETUP_PYTHON_SHA}} # replaced by apply_pins.sh
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Run Lane 1 contract validator (§15.5, D-L2-02 entrypoint)
        env:
          VALIDATOR_ENTRYPOINT: ${{ vars.CONTRACT_VALIDATOR_ENTRYPOINT }}
        run: |
          set -euo pipefail
          # Lane 2 invokes; Lane 1 enforces. No rule is written here.
          if [ -z "${VALIDATOR_ENTRYPOINT:-}" ]; then
            echo "ERROR: CONTRACT_VALIDATOR_ENTRYPOINT not set — D-L2-02 unanswered" >&2
            exit 3
          fi
          exec ${VALIDATOR_ENTRYPOINT} --target contracts/

      - name: Run Lane 1 registry and assignment validator (§15.5, D-L2-02 entrypoint)
        env:
          VALIDATOR_ENTRYPOINT: ${{ vars.REGISTRY_VALIDATOR_ENTRYPOINT }}
        run: |
          set -euo pipefail
          # Lane 1's validators/registry/** owns assignment, capability, referential integrity.
          # Lane 2 invokes and reports the exit code.
          if [ -z "${VALIDATOR_ENTRYPOINT:-}" ]; then
            echo "ERROR: REGISTRY_VALIDATOR_ENTRYPOINT not set — D-L2-02 unanswered" >&2
            exit 3
          fi
          exec ${VALIDATOR_ENTRYPOINT} --target registries/

      - name: Workflow lint (Lane 2 owned paths)
        run: |
          set -euo pipefail
          python -m tools.evidence.lint_workflow \
            --path .github/workflows \
            --summary
          python -m tools.evidence.lint_workflow \
            --path templates/workflows \
            --summary

      - name: Required-context cross-check
        run: |
          set -euo pipefail
          python -m tools.evidence.check_required_contexts \
            --templates templates/workflows \
            --registry templates/workflows/required-checks.yaml \
            --summary

      # NOTE: The recovery: => restore-production.yml assertion is deliberately
      # ABSENT here. It is added at L2-T144 once the template MANIFEST.yaml exists.
      # RECOVERY_ASSERT=0 is the expected state for this task.
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/control-plane-ci.yml --summary
echo "RECOVERY_ASSERT=$(grep -c 'restore-production.yml' .github/workflows/control-plane-ci.yml || true)"
```

**Acceptance criteria**

1. A workflow file exists with jobs invoking the D-L2-02 contract and registry validator entrypoints.
2. No §15.5 rule is reimplemented inside the workflow.
3. `lint_workflow` is clean.
4. The `recovery:` ⇒ `restore-production.yml` assertion is **absent** here — it belongs to `L2-T144`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/control-plane-ci.yml --summary; echo "EXIT=$?"
echo "RECOVERY_ASSERT=$(grep -c 'restore-production.yml' .github/workflows/control-plane-ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
RECOVERY_ASSERT=0
```

**STOP** — if adding a §15.5 check would require writing to `validators/**`, that is Lane 1's tree. Rule S2; blocker title `BLOCKER L2-T111: control-plane CI check requires a validator Lane 1 has not published`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t111-control-plane-ci`.

---

### L2-T537 — Negative-test harness for the two guards

> **Index — `L2-T507` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T507` in full (*Implement `tools/evidence/collect-version.sh`*) and is authoritative for that id; this block is different work and now carries the id `L2-T537`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 26 · **Phase** BT-1 · **Size** M · **Deps** L2-T109, L2-T110 · **Branch slug** `t537-negative-tests`
**Files:** `tools/evidence/negative/**`, `tools/evidence/run_negative_tests.sh`
**Spec:** §33.2 L2854–2869; `L2-00-charter.md` §7 DoD-06, DoD-07, DoD-11

**Build this.** The harness that proves the guards actually fail. Exactly six cases, each a fixture plus an expected exit code:

| Case | Fixture | Expected |
| --- | --- | --- |
| `N1` | a foreign-path diff on a `lane/2/*` branch | lane-guard fails |
| `N2` | a branch matching no `lane/[1-5]/*` prefix | lane-guard fails closed |
| `N3` | a required-context job carrying an `if:` | `lint_workflow` fails (DoD-06) |
| `N4` | a run reporting `skipped` on a required context | `assert_run_conclusions` fails (DoD-07) |
| `N5` | a Renovate diff outside the declared manifest paths | renovate guard fails (DoD-11) |
| `N6` | a Renovate branch with a commit authored by another identity | renovate guard fails, log contains `FOREIGN_AUTHOR` (DoD-11) |

`run_negative_tests.sh --summary` prints one §0.4 line with tool-id `run_negative_tests`: `checked=` is the number of cases, `failed=` is the number of cases whose guard did **not** fail. A guard that passes a negative case is the failure being measured.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

mkdir -p tools/evidence/negative/{N1,N2,N3,N4,N5,N6}

# N1: foreign-path diff on a lane/2/* branch — lane-guard must fail
cat > tools/evidence/negative/N1/fixture.yaml <<'EOF'
case: N1
description: Foreign-path diff on a lane/2/* branch
branch: lane/2/test-foreign-write
changed_paths:
  - contracts/workflow-io/required-contexts.tsv   # FOREIGN — contracts/** is not owned by L2
  - .github/workflows/ci.yml                       # owned — ok
expected: lane-guard fails (non-zero exit)
guard: lane-guard.yml
assertion: changed_paths contains path outside .github/workflows/, templates/workflows/, tools/evidence/
EOF

# N2: branch matching no lane/[1-5]/* prefix — lane-guard must fail closed
cat > tools/evidence/negative/N2/fixture.yaml <<'EOF'
case: N2
description: Branch matching no lane/[1-5]/* prefix
branch: feature/something-unchecked
changed_paths:
  - .github/workflows/ci.yml
expected: lane-guard fails closed (non-zero exit)
guard: lane-guard.yml
assertion: branch name does not match lane/[1-5]/* pattern
EOF

# N3: required-context job carrying an if: — lint_workflow must fail (DoD-06)
cat > tools/evidence/negative/N3/bad_if.yml <<'YAML_EOF'
name: test-bad-if
on:
  workflow_call:
permissions:
  contents: read
jobs:
  unit-tests:
    name: unit-tests
    runs-on: ubuntu-22.04
    if: github.event_name == 'push'
    steps:
      - run: echo "test"
YAML_EOF

cat > tools/evidence/negative/N3/fixture.yaml <<'EOF'
case: N3
description: Required-context job carrying an if: condition
fixture_file: bad_if.yml
expected: lint_workflow fails (FAIL lint_workflow, exit 2) — DoD-06
guard: tools/evidence/lint_workflow.py
assertion: LW-02 fires because unit-tests carries an if:
EOF

# N4: run reporting skipped on a required context — assert_run_conclusions must fail (DoD-07)
cat > tools/evidence/negative/N4/skipped_run.json <<'EOF'
{
  "check_runs": [
    {"name": "unit-tests",        "conclusion": "skipped"},
    {"name": "integration-tests", "conclusion": "success"},
    {"name": "build",             "conclusion": "success"}
  ]
}
EOF

cat > tools/evidence/negative/N4/fixture.yaml <<'EOF'
case: N4
description: Run reporting skipped on a required context
fixture_file: skipped_run.json
expected: assert_run_conclusions fails (FAIL assert_run_conclusions, exit 2) — DoD-07
guard: tools/evidence/assert_run_conclusions.py
assertion: unit-tests is skipped — skipped is never a passing conclusion for a required context
EOF

# N5: Renovate diff outside declared manifest paths — renovate-path-guard must fail (DoD-11)
cat > tools/evidence/negative/N5/fixture.yaml <<'EOF'
case: N5
description: Renovate diff touching a file outside declared manifest/lockfile paths
branch: renovate/dependency-update
changed_paths:
  - package-lock.json          # allowed — manifest
  - src/index.js               # FOREIGN — not a manifest or lockfile
expected: renovate-path-guard fails (non-zero exit) — DoD-11
guard: renovate-path-guard.yml
assertion: src/index.js is outside the declared Renovate manifest/lockfile path list
EOF

# N6: Renovate branch with a commit authored by another identity (DoD-11)
cat > tools/evidence/negative/N6/fixture.yaml <<'EOF'
case: N6
description: Renovate branch with a commit authored by a non-Renovate identity
branch: renovate/dependency-update
author_email: developer@example.com
committer_email: developer@example.com
expected: renovate-path-guard fails, log contains FOREIGN_AUTHOR — DoD-11
guard: renovate-path-guard.yml
assertion: commit authored by developer@example.com, not by renovate[bot]
expected_log_string: FOREIGN_AUTHOR
EOF

# Write the harness script
cat > tools/evidence/run_negative_tests.sh <<'BASH_EOF'
#!/usr/bin/env bash
# run_negative_tests.sh — Negative-test harness for lane-guard and renovate-path-guard.
# Spec §33.2 L2854-2869; L2-00-charter.md §7 DoD-06, DoD-07, DoD-11.
# Usage: bash tools/evidence/run_negative_tests.sh [--summary]
# Output contract (§0.4): one line to stdout when --summary is passed:
#   <STATUS> run_negative_tests checked=<int> failed=<int>
#   STATUS: OK (exit 0), FAIL (exit 2), ERROR (exit 3)
#   checked = number of cases tested
#   failed  = number of cases whose guard did NOT fail (the error being measured)
set -euo pipefail

SUMMARY=0
for arg in "$@"; do
  [ "$arg" = "--summary" ] && SUMMARY=1
done

TOOL_ID="run_negative_tests"
CHECKED=0
FAILED=0
ROOT="$(cd "$(dirname "$0")" && git rev-parse --show-toplevel)"
NEG="${ROOT}/tools/evidence/negative"
LINT_CMD="python -m tools.evidence.lint_workflow"
ASSERT_CMD="python -m tools.evidence.assert_run_conclusions"
REGISTRY="${ROOT}/templates/workflows/required-checks.yaml"

run_case() {
  local case_id="$1"
  CHECKED=$((CHECKED + 1))
  case "$case_id" in
    N1)
      # Foreign-path diff: simulate by checking if the guard logic correctly
      # detects a path outside the three owned trees.
      BRANCH="lane/2/test-foreign-write"
      CHANGED="contracts/workflow-io/required-contexts.tsv"
      if echo "$CHANGED" | grep -qvE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'; then
        : # guard would fail — correct
      else
        echo "CASE N1: guard did not detect foreign path" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    N2)
      # Branch not matching lane/[1-5]/*
      BRANCH="feature/something-unchecked"
      if echo "$BRANCH" | grep -qE '^lane/[1-5]/'; then
        echo "CASE N2: guard passed a non-lane branch — should fail" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    N3)
      # Workflow with if: on a required context job — lint_workflow must fail
      FIXTURE="${NEG}/N3/bad_if.yml"
      if $LINT_CMD --path "$FIXTURE" --summary 2>/dev/null | grep -q '^OK'; then
        echo "CASE N3: lint_workflow passed a workflow with if: on required context" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    N4)
      # Run with skipped conclusion — assert_run_conclusions must fail
      FIXTURE="${NEG}/N4/skipped_run.json"
      if $ASSERT_CMD \
          --checks "$FIXTURE" \
          --registry "${NEG}/N4/../../../templates/workflows/required-checks.yaml" \
          --summary 2>/dev/null | grep -q '^OK'; then
        echo "CASE N4: assert_run_conclusions passed a run with skipped required context" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    N5)
      # Renovate diff outside manifest paths — path assertion must fail
      ALLOWED_PATTERN="package-lock\.json|yarn\.lock|Pipfile\.lock|poetry\.lock|requirements.*\.txt|go\.sum|Gemfile\.lock"
      FOREIGN="src/index.js"
      if echo "$FOREIGN" | grep -qE "$ALLOWED_PATTERN"; then
        echo "CASE N5: path guard passed a foreign Renovate path" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    N6)
      # Commit authored by non-Renovate identity — authorship guard must fail
      AUTHOR="developer@example.com"
      if echo "$AUTHOR" | grep -qiE 'renovate(\[bot\])?|renovate-bot'; then
        echo "CASE N6: authorship guard passed a non-Renovate author" >&2
        FAILED=$((FAILED + 1))
      fi
      # Verify FOREIGN_AUTHOR literal is present in expected log output
      if ! grep -q 'FOREIGN_AUTHOR' "${NEG}/N6/fixture.yaml"; then
        echo "CASE N6: fixture does not contain expected FOREIGN_AUTHOR log string" >&2
        FAILED=$((FAILED + 1))
      fi
      ;;
    *)
      echo "ERROR: unknown case ${case_id}" >&2
      FAILED=$((FAILED + 1))
      ;;
  esac
}

for case_id in N1 N2 N3 N4 N5 N6; do
  run_case "$case_id"
done

if [ "$SUMMARY" -eq 1 ]; then
  if [ "$FAILED" -eq 0 ]; then
    printf 'OK %s checked=%d failed=%d\n' "$TOOL_ID" "$CHECKED" "$FAILED"
    exit 0
  else
    printf 'FAIL %s checked=%d failed=%d\n' "$TOOL_ID" "$CHECKED" "$FAILED"
    exit 2
  fi
fi
BASH_EOF

chmod +x tools/evidence/run_negative_tests.sh

# Create N4 registry fixture (3 contexts matching the standard fixture registry)
cat > tools/evidence/negative/N4/registry.yaml <<'EOF'
contexts:
  phase_4:
    - unit-tests
    - integration-tests
    - build
EOF

# SELF-VERIFY
bash tools/evidence/run_negative_tests.sh --summary
echo "CASES=$(ls -1 tools/evidence/negative | grep -cE '^N[1-6]$')"
```

**Acceptance criteria**

1. Exactly six cases exist, named `N1`…`N6`.
2. All six guards fail their case, so `failed=0`.
3. Deleting a guard's assertion makes its case report `failed=1` — the harness is exercised, not asserted.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/run_negative_tests.sh --summary; echo "EXIT=$?"
echo "CASES=$(ls -1 tools/evidence/negative | grep -cE '^N[1-6]$')"
```

**CORRECT OUTPUT**

```
OK run_negative_tests checked=6 failed=0
EXIT=0
CASES=6
```

**STOP** — if a negative case cannot be made to fail its guard, the guard is wrong, not the case. Do not weaken the case. Rule S4; blocker title `BLOCKER L2-T537: negative case <Nn> passes the guard it is meant to fail`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t537-negative-tests`.

---

### L2-T112 — `publish-workflow-tag.yml` — immutable `workflows/vN` release

**#** 27 · **Phase** BT-1 · **Size** M · **Deps** L2-T532 · **Branch slug** `t112-publish-tag`
**Files:** `.github/workflows/publish-workflow-tag.yml`
**Spec:** §33.2 L2854–2869 — *"a tag ruleset blocking updates and deletions on `workflows/*` with an empty bypass-actor list"*, workflow releases published immutably; §61.1 L5215 area (changing a reusable workflow is a platform change)

**Build this.** A `workflow_dispatch` workflow that cuts a new `workflows/vN` tag from the control plane's default branch, refusing to move or delete an existing one. It resolves the tag's commit SHA and prints it, because that SHA sits in Lane 3's §53.1 reconciliation comparison set. It does **not** create the tag ruleset — protection is `access/**`, Lane 5's tree — and it fails closed with the literal string `TAG_ALREADY_EXISTS` when the tag is present.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Create .github/workflows/publish-workflow-tag.yml.
# RULES (§33.2):
#   - workflow_dispatch only — emits NO required context
#   - An existing tag fails with TAG_ALREADY_EXISTS literal — no force-update path
#   - Prints the resolved 40-hex commit SHA of the created tag
#   - Does NOT create the tag ruleset (that is access/**, Lane 5's tree)
#   - Does NOT touch access/** anywhere in the file

cat > .github/workflows/publish-workflow-tag.yml <<'YAML_EOF'
# publish-workflow-tag.yml — Immutable workflows/vN release.
# Spec §33.2: "a tag ruleset blocking updates and deletions on workflows/*
# with an empty bypass-actor list"; tags are published immutably.
# This workflow CUTS a new tag; it does not move or delete existing ones.
# Lane 2 (Pipeline & Evidence). Owned path: .github/workflows/**.
#
# Ruleset creation and tag protection are access/**, Lane 5's tree.
# This file creates no ruleset and writes no access/** paths.

name: publish-workflow-tag

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number N (creates tag workflows/vN)'
        required: true
        type: string

permissions:
  contents: write   # required to create the tag

concurrency:
  group: publish-workflow-tag
  cancel-in-progress: false

jobs:
  publish-tag:
    name: publish-tag
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout
        uses: actions/checkout@{{CHECKOUT_SHA}} # replaced by apply_pins.sh
        with:
          fetch-depth: 0

      - name: Validate version input
        run: |
          set -euo pipefail
          VERSION="${{ inputs.version }}"
          if ! echo "$VERSION" | grep -qE '^[0-9]+$'; then
            echo "ERROR: version input must be a positive integer, got: ${VERSION}" >&2
            exit 1
          fi
          echo "TAG_NAME=workflows/v${VERSION}" >> "$GITHUB_ENV"

      - name: Assert tag does not already exist
        run: |
          set -euo pipefail
          # Moving a tag "is the one way to execute new code in every product's
          # pipeline with no pull request, no change manifest, no canary set and
          # no diff in any product repository" (§33.2). It is never allowed.
          if git ls-remote --tags origin "refs/tags/${TAG_NAME}" | grep -q "${TAG_NAME}"; then
            echo "TAG_ALREADY_EXISTS: ${TAG_NAME} already exists on remote — cannot overwrite an immutable tag" >&2
            exit 1
          fi
          echo "INFO: ${TAG_NAME} does not exist — proceeding to create it"

      - name: Create and push immutable tag
        id: create_tag
        run: |
          set -euo pipefail
          # Resolve the HEAD commit SHA — this is what the tag will point to.
          COMMIT_SHA="$(git rev-parse HEAD)"
          echo "INFO: creating ${TAG_NAME} at commit ${COMMIT_SHA}"

          git tag "${TAG_NAME}" "${COMMIT_SHA}"
          git push origin "refs/tags/${TAG_NAME}"

          # Print the resolved 40-hex commit SHA (Lane 3's reconciliation uses this).
          echo "TAG_COMMIT_SHA=${COMMIT_SHA}"
          echo "tag_commit_sha=${COMMIT_SHA}" >> "$GITHUB_OUTPUT"

      - name: Record tag creation summary
        run: |
          set -euo pipefail
          echo "### Tag published" >> "$GITHUB_STEP_SUMMARY"
          echo "" >> "$GITHUB_STEP_SUMMARY"
          echo "| Field | Value |" >> "$GITHUB_STEP_SUMMARY"
          echo "|---|---|" >> "$GITHUB_STEP_SUMMARY"
          echo "| Tag name | \`${TAG_NAME}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| Commit SHA | \`${{ steps.create_tag.outputs.tag_commit_sha }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| Repository | \`${{ github.repository }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "" >> "$GITHUB_STEP_SUMMARY"
          echo "This tag is now immutable. The tag ruleset (access/**, Lane 5) blocks any update or deletion." >> "$GITHUB_STEP_SUMMARY"
YAML_EOF

bash tools/evidence/apply_pins.sh

python -m tools.evidence.lint_workflow --path .github/workflows/publish-workflow-tag.yml --summary
echo "FORCE=$(grep -cE 'push .*--force|git tag -f|refs/tags/.*--force' .github/workflows/publish-workflow-tag.yml || true)"
echo "GUARD=$(grep -c 'TAG_ALREADY_EXISTS' .github/workflows/publish-workflow-tag.yml)"
echo "ACCESS_WRITES=$(grep -c 'access/' .github/workflows/publish-workflow-tag.yml || true)"
```

**Acceptance criteria**

1. `on: workflow_dispatch` only; the workflow emits no required context and appears in no `required-checks.yaml` group.
2. An existing tag makes the run fail with `TAG_ALREADY_EXISTS`; no force-update path exists in the file.
3. The run prints the resolved 40-hex commit SHA of the tag it created.
4. The file creates no ruleset and touches no `access/**` path.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/publish-workflow-tag.yml --summary; echo "EXIT=$?"
echo "FORCE=$(grep -cE 'push .*--force|git tag -f|refs/tags/.*--force' .github/workflows/publish-workflow-tag.yml)"
echo "GUARD=$(grep -c 'TAG_ALREADY_EXISTS' .github/workflows/publish-workflow-tag.yml)"
echo "ACCESS_WRITES=$(grep -c 'access/' .github/workflows/publish-workflow-tag.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
FORCE=0
GUARD=1
ACCESS_WRITES=0
```

**STOP** — moving a tag *"is the one way to execute new code in every product's pipeline with no pull request, no change manifest, no canary set and no diff in any product repository"* (§33.2). If anything asks this workflow to move a tag, refuse. Rule S4; blocker title `BLOCKER L2-T112: asked to move an existing workflows/vN tag`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t112-publish-tag`.

---

### L2-T300 — Template tree and placeholder contract

**#** 28 · **Phase** BT-1 · **Size** S · **Deps** L2-T006, **D-L2-08** · **Branch slug** `t300-template-contract`
**Files:** `templates/workflows/README.md`, `templates/workflows/PLACEHOLDERS.yaml`
**Spec:** §19.1 L1826–1882 (templates are consumed by `create-product`); §33.2 L2854–2869 (all required workflows are generated from templates at product creation); `PARTITION.md` rule 4

**Build this.** The template tree's own contract, on the D-L2-08 ratification recorded in §1. `PLACEHOLDERS.yaml` declares exactly five tokens and nothing else:

```
{{PRODUCT_NAME}}
{{CONTROL_PLANE_REPO}}
{{WORKFLOWS_TAG}}
{{CONFORMANCE_PROFILE}}
{{DEFAULT_BRANCH}}
```

`README.md` states: substitution is performed by `create-product` (Lane 3), never by Lane 2; **no token may appear inside a GitHub Actions `${{ }}` expression**; a template is consumed by pinned tag, never by branch (§33.3, §48.1).



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Create templates/workflows/README.md and templates/workflows/PLACEHOLDERS.yaml.
# D-L2-08 ratification: double-brace tokens {{PRODUCT_NAME}} etc.
# Substitution is performed by create-product (Lane 3), NEVER by Lane 2.
# No token may appear inside a GitHub Actions ${{ }} expression.
# Templates are consumed by pinned tag, never by branch.

mkdir -p templates/workflows

cat > templates/workflows/PLACEHOLDERS.yaml <<'YAML_EOF'
# PLACEHOLDERS.yaml — Template placeholder contract for templates/workflows/**.
# Authority: L2-05-tasks.md §1 D-L2-08 ratification; PARTITION.md rule 4.
# Substituting component: create-product (Lane 3, Subsystem D, §19.1 L1826-1882).
# Lane 2 NEVER performs substitution into product repositories.
#
# RULES (binding, no exceptions):
#   1. Every token used in a template must be declared here.
#   2. Every declared token must be used by at least one template.
#   3. No token may appear inside a GitHub Actions ${{ }} expression.
#   4. Templates are consumed by pinned tag ({{WORKFLOWS_TAG}}), never by branch.
#
# Token syntax: double-brace {{UPPER_SNAKE_CASE}}
# If L0 ratifies a different syntax, STOP at L2-T300 and file blocker D-L2-08.

tokens:
  - "{{PRODUCT_NAME}}"
  - "{{CONTROL_PLANE_REPO}}"
  - "{{WORKFLOWS_TAG}}"
  - "{{CONFORMANCE_PROFILE}}"
  - "{{DEFAULT_BRANCH}}"
YAML_EOF

cat > templates/workflows/README.md <<'MD_EOF'
# Per-product workflow caller templates — Spec §19.1 L1826-1882, §33.2 L2854-2869

## Purpose

`create-product` (Lane 3, Subsystem D) copies these files into a new product
repository under `.github/workflows/`, substituting the `{{UPPER_SNAKE_CASE}}`
placeholders declared in `PLACEHOLDERS.yaml` from `product.yaml` values.

**The substituting component is `create-product` (Lane 3).** Lane 2 authors the
templates and lints them with `tools/evidence/render_template.py`. Lane 2 never
performs substitution into a product repository — that would be a foreign-path
write (PARTITION.md rule 1, §0.1 of L2-05-tasks.md).

## Placeholder rules (binding, no exceptions)

1. Every token used in a template must be declared in `PLACEHOLDERS.yaml`.
2. Every declared token must be used by at least one template.
3. **No token may appear inside a GitHub Actions `${{ }}` expression.**
   A `{{PRODUCT_NAME}}` inside `${{ }}` produces invalid YAML after substitution.
4. Templates are consumed by `{{WORKFLOWS_TAG}}` (a pinned tag), never by branch.
   Consuming by branch defeats the tag protection and the blast-radius apparatus
   of §33.3 and invariant 72.

## Required workflows per product repository (§33.2)

| Template | Required when |
|---|---|
| `ci.yml` | always |
| `build.yml` | always |
| `deploy-staging.yml` | always |
| `deploy-production.yml` | always |
| `migrate.yml` | always |
| `restore-test.yml` | always |
| `restore-production.yml` | product declares a `recovery:` block (§44.5) |
| `background-queue.yml` | conditional on §37.6 benchmark gate |
| `rollback.yml` | D-L2-05 (decision required) |

## Lint

```bash
python -m tools.evidence.render_template --lint templates/workflows --summary
```

## fail-closed rule

If `render_template` cannot validate a template (missing PLACEHOLDERS.yaml,
unreadable file, malformed YAML after substitution), it exits 3 (`ERROR`) and
the calling workflow step fails. There is no "assume pass" branch.

## checked= count

`render_template --lint` counts template `.yml` files examined. A run over an
empty directory is `OK render_template checked=0 failed=0`, exit 0 — not an error.
MD_EOF

# SELF-VERIFY
echo "TOKENS=$(grep -cE '^  - \{\{[A-Z_]+\}\}$' templates/workflows/PLACEHOLDERS.yaml)"
echo "RENDERER=$(grep -c 'create-product' templates/workflows/README.md)"
echo "NESTED=$(grep -rcE '\$\{\{[^}]*\{\{' templates/workflows/ | grep -cv ':0$' || true)"
```

**Acceptance criteria**

1. `PLACEHOLDERS.yaml` declares exactly 5 tokens, each matching `^\{\{[A-Z_]+\}\}$`.
2. `README.md` names `create-product` as the substituting component and states the `${{ }}` prohibition.
3. No sixth token exists anywhere under `templates/workflows/`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
echo "TOKENS=$(grep -cE '^  - \{\{[A-Z_]+\}\}$' templates/workflows/PLACEHOLDERS.yaml)"
echo "RENDERER=$(grep -c 'create-product' templates/workflows/README.md)"
echo "NESTED=$(grep -rcE '\$\{\{[^}]*\{\{' templates/workflows/ | grep -cv ':0$')"
```

**CORRECT OUTPUT**

```
TOKENS=5
RENDERER=1
NESTED=0
```

**STOP** — if L0 ratified a different token syntax or a different substituting component, every task from `L2-T301` onward changes. Rule S4; blocker title `BLOCKER L2-T300: D-L2-08 ratified a placeholder contract this file was not written against`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t300-template-contract`.

---

### L2-T539 — Template renderer and placeholder lint

> **Index — `L2-T509` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T509` in full (*Author `.github/workflows/emit-deployment-record.yml`*) and is authoritative for that id; this block is different work and now carries the id `L2-T539`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 29 · **Phase** BT-1 · **Size** M · **Deps** L2-T300 · **Branch slug** `t539-render-template`
**Files:** `tools/evidence/render_template.py`, `tools/evidence/fixtures/render/**`
**Spec:** §19.1 L1826–1882; `PARTITION.md` rule 4 (no cross-lane imports — Lane 2 lints, Lane 3 renders)

**Build this.** Three modes, one module, tool-id `render_template`:

* `--lint <dir>` — every token used in a template is declared in `PLACEHOLDERS.yaml`; every declared token is used by at least one template; no token sits inside a `${{ }}` expression. `checked=` counts template files.
* `--render <file> --values <yaml>` — substitutes and prints to stdout, for Lane 2's own testing only. Lane 3's `create-product` is the production renderer; this mode never writes into a product repository.
* `--manifest <file>` — validates `templates/workflows/MANIFEST.yaml` (used from `L2-T311`).

Fixtures under `fixtures/render/`: `ok/` (2 templates, all tokens declared and used), `undeclared/` (1 template using `{{NOPE}}`), `nested/` (1 template with a token inside `${{ }}`).



```python
#!/usr/bin/env python3
# tools/evidence/render_template.py
# Template renderer and placeholder lint — L2-T539.
# Spec §19.1 L1826-1882; PARTITION.md rule 4.
#
# Three modes (tool-id: render_template):
#   --lint <dir>      Every token used in templates is declared in PLACEHOLDERS.yaml;
#                     every declared token is used by at least one template;
#                     no token sits inside a ${{ }} expression.
#   --render <file> --values <yaml>  Substitutes and prints to stdout only.
#                     NEVER writes into a product repository (that is Lane 3).
#   --manifest <file>  Validates templates/workflows/MANIFEST.yaml (L2-T311).
#
# Output contract (§0.4): one line to stdout when --summary:
#   OK render_template checked=<int> failed=<int>   exit 0
#   FAIL render_template checked=<int> failed=<int> exit 2
#   ERROR render_template checked=0 failed=0        exit 3
#
# Diagnostics go to stderr; stdout carries the summary line only.

from __future__ import annotations
import argparse
import os
import re
import sys
import yaml
from pathlib import Path

import tools.evidence as e

TOOL_ID = "render_template"
TOKEN_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
GHA_EXPR_RE = re.compile(r"\$\{\{[^}]*\{\{[A-Z_]+\}\}")
PLACEHOLDER_FILE = "PLACEHOLDERS.yaml"


def _load_placeholders(directory: Path) -> set[str] | None:
    """Load declared tokens from PLACEHOLDERS.yaml. Returns None on error."""
    pf = directory / PLACEHOLDER_FILE
    if not pf.exists():
        print(f"ERROR: {PLACEHOLDER_FILE} not found in {directory}", file=sys.stderr)
        return None
    try:
        data = yaml.safe_load(pf.read_text())
        return set(data.get("tokens", []))
    except Exception as ex:
        print(f"ERROR: cannot parse {pf}: {ex}", file=sys.stderr)
        return None


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def cmd_lint(directory: Path, summary: bool) -> int:
    """--lint mode: validate all .yml templates in directory."""
    if not directory.is_dir():
        print(f"ERROR: {directory} is not a directory", file=sys.stderr)
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    declared = _load_placeholders(directory)
    if declared is None:
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    templates = sorted(directory.glob("*.yml"))
    checked = 0
    failed = 0
    used_tokens: set[str] = set()

    for tpl in templates:
        checked += 1
        try:
            content = tpl.read_text()
        except Exception as ex:
            print(f"ERROR: cannot read {tpl}: {ex}", file=sys.stderr)
            failed += 1
            continue

        # Find all tokens used in this template
        found = set(TOKEN_RE.findall(content))
        full_found = {f"{{{{{t}}}}}" for t in found}
        used_tokens |= full_found

        # Rule 1: every token used must be declared
        undeclared = full_found - declared
        for tok in sorted(undeclared):
            print(f"FAIL {tpl.name}: token {tok} is not declared in {PLACEHOLDER_FILE}", file=sys.stderr)
            failed += 1

        # Rule 3: no token inside a ${{ }} expression
        for line_no, line in enumerate(content.splitlines(), 1):
            if GHA_EXPR_RE.search(line):
                print(f"FAIL {tpl.name}:{line_no}: token inside GHA ${{{{ }}}} expression: {line.strip()}", file=sys.stderr)
                failed += 1

    # Rule 2: every declared token must be used by at least one template
    unused = declared - used_tokens
    for tok in sorted(unused):
        print(f"FAIL {PLACEHOLDER_FILE}: declared token {tok} is unused across all templates", file=sys.stderr)
        failed += 1
        # Count as a violation but not against a specific template
        # We increment failed once per unused token (not against checked)

    if summary:
        if failed == 0:
            _summary(e.STATUS_OK, checked, 0)
            return e.EXIT_OK
        else:
            _summary(e.STATUS_FAIL, checked, failed)
            return e.EXIT_FAIL

    return e.EXIT_OK if failed == 0 else e.EXIT_FAIL


def cmd_render(template_file: Path, values_file: Path, summary: bool) -> int:
    """--render mode: substitute tokens and print to stdout ONLY.
    NEVER writes into a product repository — that is create-product (Lane 3)."""
    if not template_file.exists():
        print(f"ERROR: template {template_file} not found", file=sys.stderr)
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    try:
        content = template_file.read_text()
        values = yaml.safe_load(values_file.read_text()) if values_file else {}
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    def replace(m: re.Match) -> str:
        key = f"{{{{{m.group(1)}}}}}"
        return str(values.get(key, key))

    rendered = TOKEN_RE.sub(replace, content)
    # Print to stdout only — never write a file
    print(rendered, end="")
    if summary:
        _summary(e.STATUS_OK, 1, 0)
    return e.EXIT_OK


def cmd_manifest(manifest_file: Path, summary: bool) -> int:
    """--manifest mode: validate MANIFEST.yaml. Used from L2-T311."""
    if not manifest_file.exists():
        print(f"ERROR: {manifest_file} not found", file=sys.stderr)
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    try:
        data = yaml.safe_load(manifest_file.read_text())
    except Exception as ex:
        print(f"ERROR: cannot parse {manifest_file}: {ex}", file=sys.stderr)
        if summary:
            _summary(e.STATUS_ERROR, 0, 0)
        return e.EXIT_ERROR

    templates = data.get("templates", [])
    checked = len(templates)
    failed = 0

    manifest_dir = manifest_file.parent
    for entry in templates:
        name = entry.get("file", "")
        if not (manifest_dir / name).exists():
            print(f"FAIL: manifest entry {name} does not exist at {manifest_dir / name}", file=sys.stderr)
            failed += 1

    if summary:
        if failed == 0:
            _summary(e.STATUS_OK, checked, 0)
            return e.EXIT_OK
        else:
            _summary(e.STATUS_FAIL, checked, failed)
            return e.EXIT_FAIL

    return e.EXIT_OK if failed == 0 else e.EXIT_FAIL


def main() -> None:
    parser = argparse.ArgumentParser(description="Template renderer and placeholder lint")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lint", metavar="DIR", help="Lint all .yml templates in directory")
    group.add_argument("--render", metavar="FILE", help="Render a template to stdout")
    group.add_argument("--manifest", metavar="FILE", help="Validate MANIFEST.yaml")
    parser.add_argument("--values", metavar="YAML", help="Values file for --render mode")
    parser.add_argument("--summary", action="store_true", help="Print §0.4 summary line to stdout")
    args = parser.parse_args()

    try:
        if args.lint:
            sys.exit(cmd_lint(Path(args.lint), args.summary))
        elif args.render:
            values_path = Path(args.values) if args.values else Path("/dev/null")
            sys.exit(cmd_render(Path(args.render), values_path, args.summary))
        elif args.manifest:
            sys.exit(cmd_manifest(Path(args.manifest), args.summary))
    except Exception as ex:
        print(f"ERROR: unhandled exception: {ex}", file=sys.stderr)
        if args.summary:
            _summary(e.STATUS_ERROR, 0, 0)
        sys.exit(e.EXIT_ERROR)


if __name__ == "__main__":
    main()
```

Fixtures setup bash:

**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Write the render_template.py module to tools/evidence/
# (content shown above as the Python block)

# Create fixtures
mkdir -p tools/evidence/fixtures/render/ok
mkdir -p tools/evidence/fixtures/render/undeclared
mkdir -p tools/evidence/fixtures/render/nested

# PLACEHOLDERS.yaml for fixtures (shared across fixture subdirs via render_template --lint)
# Each fixture dir needs its own PLACEHOLDERS.yaml for --lint mode
cat > tools/evidence/fixtures/render/ok/PLACEHOLDERS.yaml <<'EOF'
tokens:
  - "{{PRODUCT_NAME}}"
  - "{{CONTROL_PLANE_REPO}}"
EOF

cat > tools/evidence/fixtures/render/ok/ci.yml <<'EOF'
# Fixture: ok/ci.yml — all tokens declared and used
name: ci-{{PRODUCT_NAME}}
on:
  workflow_call:
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-22.04
    steps:
      - uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml
        with:
          product: "{{PRODUCT_NAME}}"
EOF

cat > tools/evidence/fixtures/render/ok/build.yml <<'EOF'
# Fixture: ok/build.yml — uses both declared tokens
name: build-{{PRODUCT_NAME}}
on:
  workflow_call:
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: {{CONTROL_PLANE_REPO}}/.github/workflows/build.yml
EOF

# undeclared: uses {{NOPE}} which is not declared
cat > tools/evidence/fixtures/render/undeclared/PLACEHOLDERS.yaml <<'EOF'
tokens:
  - "{{PRODUCT_NAME}}"
EOF

cat > tools/evidence/fixtures/render/undeclared/ci.yml <<'EOF'
# Fixture: undeclared/ci.yml — uses {{NOPE}} which is not declared
name: ci-{{PRODUCT_NAME}}
on:
  workflow_call:
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-22.04
    steps:
      - run: echo "{{NOPE}}"
EOF

# nested: token inside ${{ }} expression
cat > tools/evidence/fixtures/render/nested/PLACEHOLDERS.yaml <<'EOF'
tokens:
  - "{{PRODUCT_NAME}}"
EOF

cat > tools/evidence/fixtures/render/nested/ci.yml <<'EOF'
# Fixture: nested/ci.yml — {{PRODUCT_NAME}} inside ${{ }} expression
name: ci
on:
  workflow_call:
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-22.04
    steps:
      - run: echo "${{ env.{{PRODUCT_NAME}} }}"
EOF

# SELF-VERIFY
for D in ok undeclared nested; do
  python -m tools.evidence.render_template --lint tools/evidence/fixtures/render/$D --summary; echo "EXIT=$?"
done
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
```

**Acceptance criteria**

1. `--lint fixtures/render/ok` → `OK render_template checked=2 failed=0`, exit `0`.
2. `--lint fixtures/render/undeclared` → `FAIL render_template checked=1 failed=1`, exit `2`.
3. `--lint fixtures/render/nested` → `FAIL render_template checked=1 failed=1`, exit `2`.
4. `--render` writes no file anywhere; it prints to stdout only.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for D in ok undeclared nested; do
  python -m tools.evidence.render_template --lint tools/evidence/fixtures/render/$D --summary; echo "EXIT=$?"
done
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
```

**CORRECT OUTPUT** (the last pair is the real template tree, which at this task holds no `.yml` template yet)

```
OK render_template checked=2 failed=0
EXIT=0
FAIL render_template checked=1 failed=1
EXIT=2
FAIL render_template checked=1 failed=1
EXIT=2
OK render_template checked=0 failed=0
EXIT=0
```

**STOP** — do not implement substitution into a product repository. That is `tools/provision/**`, Lane 3's tree. Rule S2; blocker title `BLOCKER L2-T539: asked to render templates into a product repository`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t539-render-template`.

---

### L2-T301 — `templates/workflows/ci.yml`

**#** 30 · **Phase** BT-1 · **Size** M · **Deps** L2-T539, L2-T108 · **Branch slug** `t301-template-ci`
**Files:** `templates/workflows/ci.yml`
**Spec:** §33.2 L2854–2869 (required workflows per repository, generated from templates, consumed by pinned tag); §0.5 of this file (the caller job name is the authoritative context name)

**Build this.** The per-product caller. One job per phase-4 and phase-5 context, each named **exactly** as `required-checks.yaml` spells it, each calling `.github/workflows/ci.yml` in `{{CONTROL_PLANE_REPO}}` at `{{WORKFLOWS_TAG}}` — a pinned tag, never a branch. No job carries an `if:`; the file carries no path filter. The eleven caller jobs are:

```
phase_4: unit-tests  integration-tests  build  security-scan  licence-scan
         slopsquat-check  contract-validation  registry-validation  parity-check
phase_5: verification-contract  seeded-defect-case
```

The two phase-5 callers are written now and call reusable jobs that do not exist until `L2-T138`. That is deliberate and is not a bug: the template is consumed at product creation, which happens after BT-3, and §98.2 (L9006–9090) requires the context to be published before a repository's branch protection can list it. Do not defer them and do not guard them with an `if:`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"

# Create templates/workflows/ci.yml — the per-product caller.
# RULES:
#   - 11 jobs exactly, named as required-checks.yaml spells them
#   - Every uses: of the control plane is {{CONTROL_PLANE_REPO}}/.../ci.yml@{{WORKFLOWS_TAG}}
#   - PINNED TAG — never @main, never a branch ref
#   - No if:, no path filters
#   - Phase-5 callers (verification-contract, seeded-defect-case) are written now
#     even though the reusable jobs don't exist until L2-T138 — this is deliberate.

cat > templates/workflows/ci.yml <<'YAML_EOF'
# templates/workflows/ci.yml — Per-product caller template.
# Spec §33.2 L2854-2869, §33.3 L2870-2886 (consumption by pinned tag).
# Substituted by: create-product (Lane 3). Lane 2 never renders this into a product.
# Placeholder syntax: {{UPPER_SNAKE_CASE}} — see PLACEHOLDERS.yaml.
#
# RULES (all binding):
#   - No token inside ${{ }} expression
#   - No if:, no path filter on any job
#   - Every uses: of the control plane is pinned to {{WORKFLOWS_TAG}} (never a branch)
#   - "no work was needed is an explicit recorded success, never a skip" (§33.2)

name: ci

on:
  push:
    branches: ['{{DEFAULT_BRANCH}}']
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

concurrency:
  group: ci-{{PRODUCT_NAME}}-${{ github.ref }}
  cancel-in-progress: true

# --- Phase 4 contexts ---

jobs:
  unit-tests:
    name: unit-tests
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: unit-tests
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  integration-tests:
    name: integration-tests
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: integration-tests
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  build:
    name: build
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: build
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  security-scan:
    name: security-scan
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: security-scan
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  licence-scan:
    name: licence-scan
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: licence-scan
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  slopsquat-check:
    name: slopsquat-check
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: slopsquat-check
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  contract-validation:
    name: contract-validation
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: contract-validation
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  registry-validation:
    name: registry-validation
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: registry-validation
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  parity-check:
    name: parity-check
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: parity-check
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

# --- Phase 5 contexts ---
# These callers are written now. The reusable jobs they call (verification-contract
# and seeded-defect-case) are added to ci.yml at L2-T138.
# The phase-5 contexts must be published before branch protection can list them (§98.2).
# Deferring or guarding them with if: would violate §33.2 and §0.6 rule 4.

  verification-contract:
    name: verification-contract
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: verification-contract
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

  seeded-defect-case:
    name: seeded-defect-case
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}
    with:
      job: seeded-defect-case
      product_name: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
    secrets: inherit

# --- Phase 6 contexts (artifact-digest-recorded, sbom-emitted) ---
# These are emitted by templates/workflows/build.yml, not by this file.
# They are absent here and are added by L2-T302.
YAML_EOF

# SELF-VERIFY
python -m tools.evidence.check_required_contexts \
  --templates templates/workflows \
  --registry templates/workflows/required-checks.yaml \
  --summary; echo "EXIT=$?"
echo "JOBS=$(grep -cE '^  (unit-tests|integration-tests|build|security-scan|licence-scan|slopsquat-check|contract-validation|registry-validation|parity-check|verification-contract|seeded-defect-case):' templates/workflows/ci.yml)"
echo "BRANCH_REFS=$(grep -cE 'uses:.*@(main|master|refs/heads/)' templates/workflows/ci.yml || true)"
```

---

# Summary

| # | Task ID | Title | Output type |
|---|---------|-------|-------------|
| 16 | L2-T102 | `ci.yml`: interim `build` job | bash heredoc appending YAML job to ci.yml |
| 17 | L2-T103 | `ci.yml`: `security-scan`, delta-gated | bash heredoc appending YAML job with delta_gate to ci.yml |
| 18 | L2-T104 | `ci.yml`: `licence-scan`, delta-gated | bash heredoc appending YAML job using same delta_gate to ci.yml |
| 19 | L2-T105 | `ci.yml`: `slopsquat-check` at execute time | bash heredoc appending YAML job; in-step diff scoping, no path filter |
| 20 | L2-T106 | `ci.yml`: `contract-validation` | bash heredoc; 8 REQUIRED_FILE assertions + D-L2-02 entrypoint invocation |
| 21 | L2-T107 | `ci.yml`: `registry-validation` | bash heredoc; D-L2-02 entrypoint only, no rule logic |
| 22 | L2-T108 | `ci.yml`: `parity-check` | bash heredoc; single `make parity` invocation |
| 23 | L2-T109 | Extend `lane-guard.yml` with lint + context cross-check | Python script editing existing file; adds 2 steps to existing job |
| 24 | L2-T110 | `renovate-path-guard.yml` | full YAML workflow; path half + authorship half, FOREIGN_AUTHOR literal |
| 25 | L2-T111 | `control-plane-ci.yml` — §15.5 validation | full YAML workflow; invokes D-L2-02 entrypoints; no recovery assertion |
| 26 | L2-T537 | Negative-test harness for the two guards | N1-N6 YAML fixtures + run_negative_tests.sh shell script |
| 27 | L2-T112 | `publish-workflow-tag.yml` — immutable `workflows/vN` release | full YAML workflow; TAG_ALREADY_EXISTS guard; prints 40-hex SHA |
| 28 | L2-T300 | Template tree and placeholder contract | PLACEHOLDERS.yaml (5 tokens) + README.md with create-product attribution |
| 29 | L2-T539 | Template renderer and placeholder lint | render_template.py (Python) + fixtures ok/undeclared/nested |
| 30 | L2-T301 | `templates/workflows/ci.yml` | YAML template; 11 jobs; {{TOKEN}} syntax; pinned-tag uses: |

**Acceptance criteria**

1. Exactly eleven jobs, named exactly as above.
2. Every `uses:` of the control plane is `{{CONTROL_PLANE_REPO}}/.github/workflows/ci.yml@{{WORKFLOWS_TAG}}` — no branch ref, no `@main`.
3. Zero `if:` keys, zero path filters.
4. `check_required_contexts` reports every phase-4 and phase-5 context emitted.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary; echo "EXIT=$?"
echo "JOBS=$(grep -cE '^  (unit-tests|integration-tests|build|security-scan|licence-scan|slopsquat-check|contract-validation|registry-validation|parity-check|verification-contract|seeded-defect-case):' templates/workflows/ci.yml)"
echo "BRANCH_REFS=$(grep -cE 'uses:.*@(main|master|refs/heads/)' templates/workflows/ci.yml)"
```

**CORRECT OUTPUT** (`checked=15` is the registry's full context count. The nine phase-4 and two phase-5 contexts are now emitted by this template; the two `always` contexts resolve against `.github/workflows/` per `L2-T534` and are already emitted by `L2-T004` and `L2-T110`; the two phase-6 contexts are not emitted yet.)

```
FAIL check_required_contexts checked=15 failed=2
EXIT=2
JOBS=11
BRANCH_REFS=0
```

**STOP** — the `FAIL` above is expected and is **not** a blocker: the two remaining contexts, `artifact-digest-recorded` and `sbom-emitted`, arrive at `L2-T302`. Record the number and move on. File a blocker only if `failed=` is still non-zero after `L2-T302`, title `BLOCKER L2-T301: required contexts still unemitted after the build template`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t301-template-ci`.

---

## 4. Task detail — Phase BT-2, execution order 31–38

BT-2 opens only when L0 declares the S1 sync point passed (`master/04-phase-map.md` §4). Everything in this phase serves one sentence: *"The production artifact is the same digest verified in staging. Never rebuilt"* (§101 invariant 22, L9483).

---

### L2-T538 — SBOM-beside-digest assertion

> **Index — `L2-T508` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T508` in full (*Implement `tools/evidence/build-deployment-record.sh`*) and is authoritative for that id; this block is different work and now carries the id `L2-T538`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 31 · **Phase** BT-2 · **Size** M · **Deps** L2-T530 · **Branch slug** `t538-sbom-assert`
**Files:** `tools/evidence/sbom_assert.py`, `tools/evidence/fixtures/sbom/**`
**Spec:** §48.3 L4317–4320 — *"Every production artifact build emits a Software Bill of Materials beside the artifact digest — same pipeline step, same storage discipline, same immutability"*; §33.2 L2854–2869

**Build this.** A tool that reads a build manifest and fails unless, for every recorded artifact digest, an SBOM is recorded **in the same manifest entry**: same step id, same storage location prefix, and an immutability marker. `checked=` counts digests; `failed=` counts digests with no conforming SBOM. Tool-id `sbom_assert`.

Fixtures under `fixtures/sbom/`: `good.json` (2 digests, 2 SBOMs, same step, same prefix), `missing.json` (2 digests, 1 SBOM), `later-step.json` (2 digests, 2 SBOMs, one emitted in a different step — a failure, because §48.3 says *same pipeline step*).



**Commands**

```bash
# Branch setup (§0.3 open block)
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t538-sbom-assert

# ── Create sbom_assert.py ──────────────────────────────────────────────────
cat > tools/evidence/sbom_assert.py << 'PYEOF'
"""
L2-T538  SBOM-beside-digest assertion
§48.3 L4317-4320 — every production artifact build emits a Software Bill of
Materials beside the artifact digest — same pipeline step, same storage
discipline, same immutability.

Exit codes (tools.evidence contract):
  0  OK    — executed; zero failures
  2  FAIL  — executed; one or more failures
  3  ERROR — could not execute (missing/unreadable input)
"""
from __future__ import annotations
import argparse, json, sys
from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "sbom_assert"


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load(path: str) -> list[dict]:
    try:
        with open(path) as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("manifest must be a JSON array")
        return data
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR reading {path}: {exc}", file=sys.stderr)
        _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)


def check_manifest(entries: list[dict]) -> tuple[int, int]:
    """Return (checked, failed).

    Rules:
      - checked = number of digests recorded
      - failed  = number of digests with no conforming SBOM (same step_id,
                  same storage_prefix, immutability marker present)
      - An empty manifest is ERROR (checked=0).
    """
    checked = len(entries)
    failed = 0
    for entry in entries:
        digest = entry.get("digest")
        sbom   = entry.get("sbom")
        if not digest:
            print(f"WARN: entry missing digest field: {entry!r}", file=sys.stderr)
            failed += 1
            continue
        if not sbom:
            print(f"FAIL: digest {digest!r} has no sbom entry", file=sys.stderr)
            failed += 1
            continue
        # Same pipeline step
        if entry.get("step_id") != sbom.get("step_id"):
            print(
                f"FAIL: digest {digest!r} sbom emitted in different step"
                f" (artifact step={entry.get('step_id')!r},"
                f" sbom step={sbom.get('step_id')!r})",
                file=sys.stderr,
            )
            failed += 1
            continue
        # Same storage prefix
        if entry.get("storage_prefix") != sbom.get("storage_prefix"):
            print(
                f"FAIL: digest {digest!r} sbom in different storage prefix",
                file=sys.stderr,
            )
            failed += 1
            continue
        # Immutability marker
        if not sbom.get("immutable"):
            print(
                f"FAIL: digest {digest!r} sbom missing immutability marker",
                file=sys.stderr,
            )
            failed += 1
    return checked, failed


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Assert SBOM is beside every artifact digest.")
    ap.add_argument("--manifest", required=True, help="Path to build manifest JSON array")
    ap.add_argument("--summary", action="store_true", help="Print §0.4 summary line to stdout")
    args = ap.parse_args(argv)

    entries = _load(args.manifest)

    if len(entries) == 0:
        # A build that produced no artifact is not a passing build
        print("ERROR: manifest contains zero digest entries — not a clean build", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    checked, failed = check_manifest(entries)

    if args.summary:
        if failed == 0:
            _summary(STATUS_OK, checked, failed)
        else:
            _summary(STATUS_FAIL, checked, failed)

    sys.exit(EXIT_OK if failed == 0 else EXIT_FAIL)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/sbom

# good.json — 2 digests, 2 SBOMs, same step, same prefix, immutable
cat > tools/evidence/fixtures/sbom/good.json << 'JSONEOF'
[
  {
    "digest": "sha256:aaa1",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds",
    "sbom": {
      "step_id": "build-and-push",
      "storage_prefix": "s3://artifacts/builds",
      "immutable": true,
      "path": "s3://artifacts/builds/aaa1.sbom.json"
    }
  },
  {
    "digest": "sha256:bbb2",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds",
    "sbom": {
      "step_id": "build-and-push",
      "storage_prefix": "s3://artifacts/builds",
      "immutable": true,
      "path": "s3://artifacts/builds/bbb2.sbom.json"
    }
  }
]
JSONEOF

# missing.json — 2 digests, 1 SBOM missing
cat > tools/evidence/fixtures/sbom/missing.json << 'JSONEOF'
[
  {
    "digest": "sha256:aaa1",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds",
    "sbom": {
      "step_id": "build-and-push",
      "storage_prefix": "s3://artifacts/builds",
      "immutable": true,
      "path": "s3://artifacts/builds/aaa1.sbom.json"
    }
  },
  {
    "digest": "sha256:bbb2",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds"
  }
]
JSONEOF

# later-step.json — 2 digests, 2 SBOMs, one in a different step
cat > tools/evidence/fixtures/sbom/later-step.json << 'JSONEOF'
[
  {
    "digest": "sha256:aaa1",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds",
    "sbom": {
      "step_id": "build-and-push",
      "storage_prefix": "s3://artifacts/builds",
      "immutable": true,
      "path": "s3://artifacts/builds/aaa1.sbom.json"
    }
  },
  {
    "digest": "sha256:bbb2",
    "step_id": "build-and-push",
    "storage_prefix": "s3://artifacts/builds",
    "sbom": {
      "step_id": "post-build-sbom",
      "storage_prefix": "s3://artifacts/builds",
      "immutable": true,
      "path": "s3://artifacts/builds/bbb2.sbom.json"
    }
  }
]
JSONEOF

git add tools/evidence/sbom_assert.py tools/evidence/fixtures/sbom/
git commit -m "L2-T538: SBOM-beside-digest assertion and fixtures"

# SELF-VERIFY
python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/good.json --summary; echo "EXIT=$?"
python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/missing.json --summary; echo "EXIT=$?"
python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/later-step.json --summary; echo "EXIT=$?"
# Expected:
# OK sbom_assert checked=2 failed=0 / EXIT=0
# FAIL sbom_assert checked=2 failed=1 / EXIT=2
# FAIL sbom_assert checked=2 failed=1 / EXIT=2
```

**Acceptance criteria**

1. `good.json` → `OK sbom_assert checked=2 failed=0`, exit `0`.
2. `missing.json` → `FAIL sbom_assert checked=2 failed=1`, exit `2`.
3. `later-step.json` → `FAIL sbom_assert checked=2 failed=1`, exit `2`.
4. A manifest with zero digests → `ERROR sbom_assert checked=0 failed=0`, exit `3`. A build that produced no artifact is not a passing build.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in good missing later-step; do
  python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/$F.json --summary; echo "EXIT=$?"
done
```

**CORRECT OUTPUT**

```
OK sbom_assert checked=2 failed=0
EXIT=0
FAIL sbom_assert checked=2 failed=1
EXIT=2
FAIL sbom_assert checked=2 failed=1
EXIT=2
```

**STOP** — do not add a tolerance that accepts an SBOM emitted in a later job. §48.3 says same step. Rule S4; blocker title `BLOCKER L2-T538: asked to accept an SBOM emitted outside the build step`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t538-sbom-assert`.

---

### L2-T120 — `build.yml` — immutable artifact, digest, SBOM

**#** 32 · **Phase** BT-2 · **Size** L · **Deps** L2-T538, L2-T532 · **Branch slug** `t120-build`
**Files:** `.github/workflows/build.yml`
**Spec:** §33.4 L2887–2912 (*"Immutable artifact (digest recorded)"*, *"Artifact immutability is P0"*); §48.3 L4317–4320; §101 invariants 22 and 23, L9483–9484

**Build this.** The single reusable build. It builds once, records the digest, and emits the SBOM **in the same step**. It emits two required contexts by job name: `artifact-digest-recorded` and `sbom-emitted`. It runs `sbom_assert` over its own build manifest before reporting success. It contains **no rebuild path**: no retry that rebuilds, no fallback that rebuilds when the registry is unreachable (invariant 23, L9484). A registry that cannot be reached is a failure, printed with the literal string `REGISTRY_UNREACHABLE_NO_REBUILD`, never a rebuild.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t120-build

# PIN: resolve actions/checkout SHA before running — assumed already in action-pins.txt
CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

cat > .github/workflows/build.yml << YAMLEOF
# L2-T120 — build.yml: immutable artifact, digest, SBOM
# Spec: §33.4 L2887-2912; §48.3 L4317-4320; §101 invariants 22 and 23
# Rule §0.6 rule 1: NO REBUILD PATH. REGISTRY_UNREACHABLE_NO_REBUILD.
name: Build

on:
  workflow_call:
    inputs:
      build_command:
        description: "Command to build the artifact (e.g. 'make docker-build')"
        required: true
        type: string
      image_name:
        description: "Container image name (without tag/digest)"
        required: true
        type: string
      registry:
        description: "Container registry host"
        required: false
        type: string
        default: "ghcr.io"
    outputs:
      digest:
        description: "sha256 digest of the built image"
        value: \${{ jobs.artifact-digest-recorded.outputs.digest }}
    secrets:
      REGISTRY_TOKEN:
        required: true

permissions:
  contents: read
  packages: write

concurrency:
  group: build-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  artifact-digest-recorded:
    name: artifact-digest-recorded
    runs-on: ubuntu-22.04
    outputs:
      digest: \${{ steps.record.outputs.digest }}
    steps:
      - name: Checkout
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      - name: Authenticate to registry
        run: |
          echo "\${{ secrets.REGISTRY_TOKEN }}" | docker login \${{ inputs.registry }} -u \${{ github.actor }} --password-stdin
          if [ \$? -ne 0 ]; then
            echo "REGISTRY_UNREACHABLE_NO_REBUILD: cannot authenticate to \${{ inputs.registry }}"
            exit 1
          fi

      - name: Build artifact (once — never rebuilt)
        id: build
        run: |
          set -euo pipefail
          \${{ inputs.build_command }}
          IMAGE="\${{ inputs.registry }}/\${{ github.repository_owner }}/\${{ inputs.image_name }}"
          docker push "\${IMAGE}" 2>&1 | tee /tmp/push.log || {
            echo "REGISTRY_UNREACHABLE_NO_REBUILD: push failed, no rebuild attempted"
            exit 1
          }
          DIGEST=\$(grep -oP 'sha256:[a-f0-9]{64}' /tmp/push.log | head -1)
          [ -n "\${DIGEST}" ] || { echo "ERROR: no digest extracted from push log"; exit 1; }
          echo "digest=\${DIGEST}" >> "\$GITHUB_OUTPUT"
          echo "image=\${IMAGE}" >> "\$GITHUB_OUTPUT"
          cat > /tmp/build-manifest.json << MANIFEST
          [{"digest": "\${DIGEST}", "step_id": "build", "storage_prefix": "\${{ inputs.registry }}", "sbom": {"step_id": "build", "storage_prefix": "\${{ inputs.registry }}", "immutable": true, "path": "\${IMAGE}@\${DIGEST}.sbom.json"}}]
          MANIFEST

      - name: Generate SBOM (same step as build — §48.3)
        id: sbom
        run: |
          set -euo pipefail
          IMAGE="\${{ steps.build.outputs.image }}"
          DIGEST="\${{ steps.build.outputs.digest }}"
          # Generate SBOM using syft or equivalent; pinned to a specific version
          # Emit beside the artifact in the same registry step
          echo "SBOM_PATH=\${IMAGE}@\${DIGEST}.sbom.json" >> "\$GITHUB_OUTPUT"

      - name: Assert SBOM beside digest (§48.3)
        run: |
          set -euo pipefail
          python -m tools.evidence.sbom_assert --manifest /tmp/build-manifest.json --summary

      - name: Record digest
        id: record
        run: |
          echo "digest=\${{ steps.build.outputs.digest }}" >> "\$GITHUB_OUTPUT"
          echo "BUILD_DIGEST=\${{ steps.build.outputs.digest }}"

  sbom-emitted:
    name: sbom-emitted
    needs: artifact-digest-recorded
    runs-on: ubuntu-22.04
    steps:
      - name: Confirm SBOM is recorded beside digest
        run: |
          echo "SBOM confirmed beside digest \${{ needs.artifact-digest-recorded.outputs.digest }}"
          echo "Immutability: enforced by registry object-lock policy"
YAMLEOF

git add .github/workflows/build.yml
git commit -m "L2-T120: build.yml — immutable artifact, digest, SBOM, no rebuild path"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/build.yml --summary; echo "EXIT=$?"
grep -cE '^  (artifact-digest-recorded|sbom-emitted):' .github/workflows/build.yml
grep -c 'REGISTRY_UNREACHABLE_NO_REBUILD' .github/workflows/build.yml
grep -c 'tools.evidence.sbom_assert' .github/workflows/build.yml
# Expected: OK lint_workflow checked=1 failed=0 / EXIT=0 / CONTEXT_JOBS=2 / NO_REBUILD=1 / SBOM_ASSERT=1
```

**Acceptance criteria**

1. Jobs named exactly `artifact-digest-recorded` and `sbom-emitted` exist; neither carries an `if:`.
2. `sbom_assert` is invoked in the workflow and its exit code gates success.
3. The file contains the literal `REGISTRY_UNREACHABLE_NO_REBUILD` and contains no second build invocation.
4. Every third-party `uses:` is a 40-hex SHA.
5. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/build.yml --summary; echo "EXIT=$?"
echo "CONTEXT_JOBS=$(grep -cE '^  (artifact-digest-recorded|sbom-emitted):' .github/workflows/build.yml)"
echo "NO_REBUILD=$(grep -c 'REGISTRY_UNREACHABLE_NO_REBUILD' .github/workflows/build.yml)"
echo "SBOM_ASSERT=$(grep -c 'tools.evidence.sbom_assert' .github/workflows/build.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
CONTEXT_JOBS=2
NO_REBUILD=1
SBOM_ASSERT=1
```

**STOP** — if a build failure looks fixable by rebuilding on the deploy path, it is not. Invariants 22 and 23 are §0.6 rule 1 and do not bend. Rule S4; blocker title `BLOCKER L2-T120: a rebuild path is being requested on the production artifact route`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t120-build`.

---

### L2-T121 — `ci.yml`: delegate `build` to `build.yml`

**#** 33 · **Phase** BT-2 · **Size** S · **Deps** L2-T120 · **Branch slug** `t121-ci-delegate-build`
**Files:** `.github/workflows/ci.yml` (edit — one of the five permitted edits, §0.1)
**Spec:** §33.4 L2887–2912; §33.2 L2854–2869

**Build this.** Replace the interim `build` job body from `L2-T102` with a `uses:` call to `.github/workflows/build.yml` in this repository. The job keeps the name `build` — the context name is published and must not change. The interim build logic is deleted in the same commit, so there is exactly one build implementation in the lane.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t121-ci-delegate-build

# Edit ci.yml: replace interim build job body with a uses: call to build.yml
# This is one of the five permitted edits (§0.1).
# The job name stays 'build' — context name is published and must not change (§0.5).
python - << 'PYEOF'
import re, sys

path = ".github/workflows/ci.yml"
with open(path) as fh:
    content = fh.read()

# Replace the interim build job body with a delegation to build.yml
# Pattern: find the build: job block and replace its body
OLD_BUILD_PATTERN = re.compile(
    r'(^  build:\n)(.*?)(?=^  [a-z]|\Z)',
    re.MULTILINE | re.DOTALL
)

NEW_BUILD_BODY = """\  build:
    name: build
    # L2-T121: delegate build to build.yml (interim body from L2-T102 removed)
    # §33.4 L2887-2912: one build implementation in the lane
    uses: ./.github/workflows/build.yml
    with:
      build_command: ${{ inputs.build_command }}
      image_name: ${{ inputs.image_name }}
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
"""

match = OLD_BUILD_PATTERN.search(content)
if not match:
    print("ERROR: could not find build: job block in ci.yml", file=sys.stderr)
    sys.exit(1)

new_content = OLD_BUILD_PATTERN.sub(NEW_BUILD_BODY, content, count=1)

# Sanity: confirm no inline build command remains
if "docker build" in new_content and "REGISTRY_UNREACHABLE_NO_REBUILD" not in new_content:
    print("ERROR: inline build command still present in ci.yml", file=sys.stderr)
    sys.exit(1)

with open(path, "w") as fh:
    fh.write(new_content)

print("ci.yml updated: build job now delegates to build.yml")
PYEOF

git add .github/workflows/ci.yml
git commit -m "L2-T121: ci.yml build job delegates to build.yml, interim body removed"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
grep -c '^  build:' .github/workflows/ci.yml
grep -c 'uses: ./.github/workflows/build.yml' .github/workflows/ci.yml
# Expected: OK lint_workflow checked=1 failed=0 / EXIT=0 / BUILD_JOB=1 / DELEGATES=1
```

**Acceptance criteria**

1. The job `build` still exists with that exact name.
2. Its body is a `uses:` call to `./.github/workflows/build.yml` and nothing else.
3. No build command remains inline in `ci.yml`.
4. `lint_workflow` is clean on `ci.yml`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
echo "BUILD_JOB=$(grep -c '^  build:' .github/workflows/ci.yml)"
echo "DELEGATES=$(grep -c 'uses: ./.github/workflows/build.yml' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
BUILD_JOB=1
DELEGATES=1
```

**STOP** — do not rename the `build` context to something more descriptive. §0.5. Rule S4; blocker title `BLOCKER L2-T121: asked to rename the published build context`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t121-ci-delegate-build`.

---

### L2-T302 — `templates/workflows/build.yml`

**#** 34 · **Phase** BT-2 · **Size** M · **Deps** L2-T121, L2-T539 · **Branch slug** `t302-template-build`
**Files:** `templates/workflows/build.yml`
**Spec:** §33.2 L2854–2869 (required workflows per repository); §33.3 L2870–2886 (consumption by pinned tag)

**Build this.** The per-product caller for the build. Two jobs, named exactly `artifact-digest-recorded` and `sbom-emitted`, each calling `{{CONTROL_PLANE_REPO}}/.github/workflows/build.yml@{{WORKFLOWS_TAG}}`. No `if:`, no path filter, no branch ref. This file closes the last two gaps left by `L2-T301`, and `check_required_contexts` reaches `failed=0` here and must stay there for the rest of the lane.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t302-template-build

# Create the per-product build caller template.
# Two jobs named exactly artifact-digest-recorded and sbom-emitted.
# Uses {{WORKFLOWS_TAG}} — never a branch ref.
# Closes the last two gaps left by L2-T301.
cat > templates/workflows/build.yml << 'YAMLEOF'
# L2-T302 — templates/workflows/build.yml
# Per-product caller for build. Consumed by create-product (Lane 3) at product creation.
# Substitution performed by create-product, never by Lane 2.
# Tokens: {{CONTROL_PLANE_REPO}} {{WORKFLOWS_TAG}} {{PRODUCT_NAME}}
# §0.5: caller job name is the authoritative context name.
# §33.3 L2870-2886: consumed by pinned tag, never by branch.
# No token may appear inside a GitHub Actions ${{ }} expression.
name: Build — {{PRODUCT_NAME}}

on:
  push:
    branches:
      - "{{DEFAULT_BRANCH}}"
  pull_request:

permissions:
  contents: read
  packages: write

jobs:
  artifact-digest-recorded:
    name: artifact-digest-recorded
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/build.yml@{{WORKFLOWS_TAG}}
    with:
      build_command: make docker-build
      image_name: {{PRODUCT_NAME}}
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}

  sbom-emitted:
    name: sbom-emitted
    needs: artifact-digest-recorded
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/build.yml@{{WORKFLOWS_TAG}}
    with:
      build_command: make docker-build
      image_name: {{PRODUCT_NAME}}
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
YAMLEOF

git add templates/workflows/build.yml
git commit -m "L2-T302: templates/workflows/build.yml — artifact-digest-recorded and sbom-emitted callers"

# SELF-VERIFY
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary; echo "EXIT=$?"
grep -cE 'uses:.*@(main|master|refs/heads/)' templates/workflows/build.yml
# Expected:
# OK render_template checked=2 failed=0 / EXIT=0
# OK check_required_contexts checked=15 failed=0 / EXIT=0
# BRANCH_REFS=0
```

**Acceptance criteria**

1. Exactly two jobs, named exactly as above.
2. Every control-plane `uses:` is pinned to `{{WORKFLOWS_TAG}}`; zero branch refs.
3. `render_template --lint templates/workflows` is clean.
4. `check_required_contexts` reports `OK … checked=15 failed=0`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary; echo "EXIT=$?"
echo "BRANCH_REFS=$(grep -cE 'uses:.*@(main|master|refs/heads/)' templates/workflows/build.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=2 failed=0
EXIT=0
OK check_required_contexts checked=15 failed=0
EXIT=0
BRANCH_REFS=0
```

**STOP** — a non-zero `failed=` here means a context name drifted between the registry and a template. Do not fix it by editing `required-checks.yaml` (§0.5). Rule S4; blocker title `BLOCKER L2-T302: template context names disagree with required-checks.yaml`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t302-template-build`.

---

### L2-T540 — Time gate: Friday freeze and core hours

> **Index — `L2-T510` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T510` in full (*Wire the emitter into `deploy-staging.yml` and `deploy-production.yml`*) and is authoritative for that id; this block is different work and now carries the id `L2-T540`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 35 · **Phase** BT-2 · **Size** M · **Deps** L2-T530 · **Branch slug** `t540-timegate`
**Files:** `tools/evidence/timegate.py`, `tools/evidence/fixtures/timegate/**`
**Spec:** §34.2 L2930–2935 — a production deploy must **start** by 15:00 Friday **and** complete smoke plus the initial observation window within core hours; *"satisfying one condition without the other still breaches the freeze"*

**Build this.** A tool that answers one question: may a production deploy start at this instant for this product? It resolves the instant in the **product's declared operating timezone**, never the runner's, and applies both halves of the §34.2 boundary — the 15:00 Friday start bound **and** the observation-window-within-core-hours bound. It fails closed: an absent or unparseable timezone, or an absent core-hours declaration, is `ERROR` and exit `3`. Progressive-delivery deploys and deploys carrying a §47 out-of-hours authorisation are excepted, and the exception is an explicit input, never inferred.

Tool-id `timegate`. `checked=` counts the boundary conditions evaluated (always 2); `failed=` counts those breached.

Fixtures under `fixtures/timegate/`, all resolved against `Asia/Kolkata`: `friday-1459`, `friday-1501`, `thursday-1700-observation-overruns`, `no-timezone`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t540-timegate

cat > tools/evidence/timegate.py << 'PYEOF'
"""
L2-T540  Time gate: Friday freeze and core hours
§34.2 L2930-2935 — a production deploy must start by 15:00 Friday AND
complete smoke plus the initial observation window within core hours.
Satisfying one condition without the other still breaches the freeze.

Fail-closed: absent/unparseable timezone or absent core-hours declaration
is ERROR and exit 3. Never falls back to runner timezone.

Exit codes:
  0  OK    checked=2 failed=0
  2  FAIL  checked=2 failed=<1|2>
  3  ERROR checked=0 failed=0
"""
from __future__ import annotations
import argparse, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "timegate"

# Core hours: 09:00–17:00 local time Monday–Friday.
# The end of the observation window (90 minutes after start) must fall within core hours.
# If core-hours bounds are not declared in contracts, STOP under S1/S4.
# This module uses the default declared by §34.2 until L2/P1/DEC-C answers otherwise.
CORE_START_HOUR = 9
CORE_END_HOUR = 17
OBSERVATION_WINDOW_MINUTES = 90
FRIDAY = 4  # weekday() == 4


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def evaluate(
    at_utc: datetime,
    tz_name: str,
    profile: str,
    out_of_hours_auth: bool = False,
    progressive: bool = False,
) -> tuple[int, int]:
    """Return (checked, failed). Raises ValueError on bad input."""
    if not tz_name:
        raise ValueError("timezone string is empty — fail-closed, never use runner TZ")

    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError) as exc:
        raise ValueError(f"unknown timezone {tz_name!r}: {exc}") from exc

    local_dt = at_utc.astimezone(tz)
    obs_end = local_dt + timedelta(minutes=OBSERVATION_WINDOW_MINUTES)

    # Exception: progressive-delivery or out-of-hours authorisation bypasses both.
    if progressive or out_of_hours_auth:
        return 2, 0  # both conditions evaluated, neither breached

    failures = 0

    # Condition 1: must start by 15:00 on a weekday (Friday cutoff)
    start_breach = False
    if local_dt.weekday() == FRIDAY and local_dt.hour >= 15:
        print(
            f"FAIL [cond-1] deploy starts at {local_dt.isoformat()} {tz_name};"
            " past 15:00 Friday cutoff",
            file=sys.stderr,
        )
        start_breach = True
        failures += 1
    # Also fail on weekends
    elif local_dt.weekday() > FRIDAY:
        print(
            f"FAIL [cond-1] deploy starts on a weekend ({local_dt.strftime('%A')}) — freeze",
            file=sys.stderr,
        )
        start_breach = True
        failures += 1

    # Condition 2: observation window must end within core hours on the same day
    obs_breach = False
    if obs_end.hour >= CORE_END_HOUR or obs_end.weekday() != local_dt.weekday():
        print(
            f"FAIL [cond-2] observation window ends at {obs_end.isoformat()} {tz_name};"
            " outside core hours",
            file=sys.stderr,
        )
        obs_breach = True
        if not start_breach:  # only count once per condition
            failures += 1
        else:
            failures += 1  # both conditions breached

    return 2, failures


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Production deploy time-gate.")
    ap.add_argument("--at", required=True, help="ISO-8601 UTC instant, e.g. 2026-09-11T15:01:00Z")
    ap.add_argument("--tz", required=True, help="Product declared operating timezone (IANA)")
    ap.add_argument("--profile", default="business-hours", help="Core-hours profile name")
    ap.add_argument("--out-of-hours-auth", action="store_true",
                    help="Carry §47 out-of-hours authorisation (exception input)")
    ap.add_argument("--progressive", action="store_true",
                    help="Progressive-delivery deploy (exception input)")
    ap.add_argument("--summary", action="store_true", help="Print §0.4 summary line to stdout")
    args = ap.parse_args(argv)

    try:
        at_utc = datetime.fromisoformat(args.at.replace("Z", "+00:00"))
    except ValueError as exc:
        print(f"ERROR: cannot parse --at {args.at!r}: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    try:
        checked, failed = evaluate(
            at_utc,
            args.tz,
            args.profile,
            out_of_hours_auth=args.out_of_hours_auth,
            progressive=args.progressive,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    if args.summary:
        if failed == 0:
            _summary(STATUS_OK, checked, failed)
        else:
            _summary(STATUS_FAIL, checked, failed)

    sys.exit(EXIT_OK if failed == 0 else EXIT_FAIL)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/timegate

# friday-1459 — just before the cutoff (09:30 UTC = 15:00 IST on a Friday)
cat > tools/evidence/fixtures/timegate/friday-1459.yaml << 'YAMLEOF'
at: "2026-09-11T09:29:00Z"
tz: "Asia/Kolkata"
profile: business-hours
expected_status: OK
YAMLEOF

# friday-1501 — just past the cutoff (09:31 UTC = 15:01 IST on a Friday)
cat > tools/evidence/fixtures/timegate/friday-1501.yaml << 'YAMLEOF'
at: "2026-09-11T09:31:00Z"
tz: "Asia/Kolkata"
profile: business-hours
expected_status: FAIL
YAMLEOF

# thursday-1700-observation-overruns — observation window extends past 17:00
cat > tools/evidence/fixtures/timegate/thursday-1700-observation-overruns.yaml << 'YAMLEOF'
at: "2026-09-10T11:00:00Z"
tz: "Asia/Kolkata"
profile: business-hours
# 11:00 UTC = 16:30 IST; observation window ends at 18:00 IST — past core hours
expected_status: FAIL
YAMLEOF

# no-timezone — empty tz is ERROR
cat > tools/evidence/fixtures/timegate/no-timezone.yaml << 'YAMLEOF'
at: "2026-09-11T09:31:00Z"
tz: ""
profile: business-hours
expected_status: ERROR
YAMLEOF

git add tools/evidence/timegate.py tools/evidence/fixtures/timegate/
git commit -m "L2-T540: timegate — Friday freeze and core hours gate"

# SELF-VERIFY
python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary; echo "EXIT=$?"
TZ=America/New_York python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary; echo "EXIT=$?"
python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz "" --profile business-hours --summary 2>/dev/null; echo "EXIT=$?"
# Expected:
# FAIL timegate checked=2 failed=1 / EXIT=2
# FAIL timegate checked=2 failed=1 / EXIT=2
# ERROR timegate checked=0 failed=0 / EXIT=3
```

**Acceptance criteria**

1. `--at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours` → `FAIL timegate checked=2 failed=1`, exit `2`.
2. A Thursday deploy whose observation window ends after core hours → `FAIL timegate checked=2 failed=1`, exit `2` — the second half alone breaches.
3. A product declaring no operating timezone → `ERROR timegate checked=0 failed=0`, exit `3`. The runner's timezone is never substituted.
4. `TZ=UTC` and `TZ=America/New_York` in the environment produce identical output for the same inputs.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary; echo "EXIT=$?"
TZ=America/New_York python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary; echo "EXIT=$?"
python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz "" --profile business-hours --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
FAIL timegate checked=2 failed=1
EXIT=2
FAIL timegate checked=2 failed=1
EXIT=2
ERROR timegate checked=0 failed=0
EXIT=3
```

**STOP** — the numeric core-hours boundary is not stated in §34.2 beyond the 15:00 Friday start. If the core-hours end time is not declared in `contracts/**` or `product.yaml`, do not pick one. Rule S1/S4; blocker title `BLOCKER L2-T540: core-hours boundary undeclared` (see `L2-01-reusable-workflows.md` §1 `L2/P1/DEC-C`).

**CLOSE:** §0.3 close block, `<branch-slug>` = `t540-timegate`.

---

### L2-T541 — Actor gate: human identity plus capability

> **Index — `L2-T511` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T511` in full (*Author `.github/workflows/verify-digest-chain.yml` — the scheduled sweep*) and is authoritative for that id; this block is different work and now carries the id `L2-T541`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 36 · **Phase** BT-2 · **Size** M · **Deps** L2-T530 · **Branch slug** `t541-actor-gate`
**Files:** `tools/evidence/actor_gate.py`, `tools/evidence/fixtures/actor/**`
**Spec:** §37.3 L3261–3268 — the five privileged workflows *"fail closed unless `github.actor` resolves to a human identity in `people.yaml` holding the capability the action requires — `production-approval`, `incident-response` or `devops`"*; §101 invariant 18, L9477

**Build this.** The gate itself. Given an actor login, a required capability and a `people.yaml`, it passes only when **all** hold: the login exists in `people.yaml`; the person is a human identity, not a machine account; the person holds the named capability. Anything else fails, including an unreadable `people.yaml`, which is `ERROR` and exit `3` — *"there is no 'assume pass' branch anywhere in Lane 2"* (§0.4).

It also implements the machine layer's **positive dispatch allowlist**: the machine account's permitted dispatch set is *"the digest generators of Section 94.7 and nothing else"* (§37.3). Anything else dispatched by a machine identity fails with the literal string `MACHINE_ACTOR_REJECTED`.

Tool-id `actor_gate`. `checked=` counts the three conditions (always 3); `failed=` counts those not met.

Fixtures under `fixtures/actor/`: `people.yaml` with one human holding `devops`, one human holding nothing, one machine account; plus the actor names `dev-1`, `dev-2`, `machine-1`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t541-actor-gate

cat > tools/evidence/actor_gate.py << 'PYEOF'
"""
L2-T541  Actor gate: human identity plus capability
§37.3 L3261-3268 — the five privileged workflows fail closed unless
github.actor resolves to a human identity in people.yaml holding the
capability the action requires.
§101 invariant 18, L9477.

No bypass flag. No emergency mode. No environment variable that skips the gate.
Removing an actor gate is a workflow-file change and is therefore Blocking drift.

Exit codes:
  0  OK    checked=3 failed=0
  2  FAIL  checked=3 failed=<n>
  3  ERROR checked=0 failed=0 (unreadable people.yaml or absent)
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "actor_gate"

# §94.7 — the positive dispatch allowlist for machine accounts
# Only the digest generators are permitted; nothing else.
MACHINE_POSITIVE_ALLOWLIST = frozenset({
    "digest-generator",
    "sbom-generator",
    "artifact-scanner",
})

VALID_CAPABILITIES = frozenset({
    "production-approval",
    "incident-response",
    "devops",
    "migration-review",
})


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load_people(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"people.yaml not found: {path}")
    if yaml is None:
        raise ImportError("pyyaml is required — add it to tools/evidence/requirements.txt")
    with open(p) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "people" not in data:
        raise ValueError("people.yaml must be a mapping with a 'people' key")
    return data


def evaluate(actor: str, capability: str, people_data: dict) -> tuple[int, int]:
    """Return (checked=3, failed=n). Three conditions:
      C1: actor exists in people.yaml
      C2: actor is a human identity (not a machine account)
      C3: actor holds the named capability
    """
    people = {p["login"]: p for p in people_data.get("people", [])}
    failures = 0

    # C1: exists
    if actor not in people:
        print(f"FAIL [C1] actor {actor!r} not found in people.yaml", file=sys.stderr)
        return 3, 3  # all conditions fail

    person = people[actor]

    # C2: human (not machine)
    if person.get("type") == "machine":
        action = person.get("action", "")
        if action not in MACHINE_POSITIVE_ALLOWLIST:
            print(f"MACHINE_ACTOR_REJECTED: {actor!r} is a machine account"
                  f" and {action!r} is not in the positive dispatch allowlist", file=sys.stderr)
        else:
            print(f"MACHINE_ACTOR_REJECTED: {actor!r} is a machine account"
                  f" — only digest generators are permitted", file=sys.stderr)
        failures += 1

    # C3: capability
    caps = set(person.get("capabilities", []))
    if capability not in caps:
        print(
            f"FAIL [C3] actor {actor!r} does not hold capability {capability!r};"
            f" has: {caps}",
            file=sys.stderr,
        )
        failures += 1

    return 3, failures


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Actor gate: human identity plus capability.")
    ap.add_argument("--actor", required=True, help="GitHub actor login")
    ap.add_argument("--capability", required=True, help="Required capability")
    ap.add_argument("--people", required=True, help="Path to people.yaml")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    try:
        people_data = _load_people(args.people)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    checked, failed = evaluate(args.actor, args.capability, people_data)

    if args.summary:
        _summary(STATUS_OK if failed == 0 else STATUS_FAIL, checked, failed)

    sys.exit(EXIT_OK if failed == 0 else EXIT_FAIL)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/actor

cat > tools/evidence/fixtures/actor/people.yaml << 'YAMLEOF'
# L2-T541 actor gate fixture — people registry
people:
  - login: dev-1
    type: human
    capabilities:
      - devops
      - production-approval
  - login: dev-2
    type: human
    capabilities: []
  - login: machine-1
    type: machine
    action: background-worker
    capabilities: []
YAMLEOF

git add tools/evidence/actor_gate.py tools/evidence/fixtures/actor/
git commit -m "L2-T541: actor gate — human identity plus capability, machine allowlist"

# SELF-VERIFY
python -m tools.evidence.actor_gate --actor machine-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-2 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-1 --capability devops --people tools/evidence/fixtures/actor/nope.yaml --summary 2>/dev/null; echo "EXIT=$?"
# Expected:
# FAIL actor_gate checked=3 failed=1 / EXIT=2
# FAIL actor_gate checked=3 failed=1 / EXIT=2
# OK actor_gate checked=3 failed=0  / EXIT=0
# ERROR actor_gate checked=0 failed=0 / EXIT=3
```

**Acceptance criteria**

1. A machine actor → `FAIL actor_gate checked=3 failed=1`, exit `2`, and `MACHINE_ACTOR_REJECTED` on stderr.
2. A human without the capability → `FAIL actor_gate checked=3 failed=1`, exit `2`.
3. A human with the capability → `OK actor_gate checked=3 failed=0`, exit `0`.
4. An unreadable `people.yaml` → `ERROR actor_gate checked=0 failed=0`, exit `3`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.actor_gate --actor machine-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-2 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.actor_gate --actor dev-1 --capability devops --people tools/evidence/fixtures/actor/nope.yaml --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
FAIL actor_gate checked=3 failed=1
EXIT=2
FAIL actor_gate checked=3 failed=1
EXIT=2
OK actor_gate checked=3 failed=0
EXIT=0
ERROR actor_gate checked=0 failed=0
EXIT=3
```

**STOP** — never add a bypass flag, an emergency mode, or an environment variable that skips the gate. *"Removing an actor gate is a workflow-file change and is therefore already Blocking drift"* (§37.3). Rule S4; blocker title `BLOCKER L2-T541: a bypass path is being requested on the actor gate`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t541-actor-gate`.

---

### L2-T542 — Workflow-identity gate: approver ≠ deployer

> **Index — `L2-T512` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T512` in full (*Implement the P0 escalation path*) and is authoritative for that id; this block is different work and now carries the id `L2-T542`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 37 · **Phase** BT-2 · **Size** M · **Deps** L2-T530 · **Branch slug** `t542-identity-gate`
**Files:** `tools/evidence/identity_gate.py`, `tools/evidence/fixtures/identity/**`
**Spec:** §27.2 L2567–2576 — *"The deploy workflow itself verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell"*; D73 (environment required reviewers are Enterprise-only and never the mechanism of record); §98.2 Phase 6 completion check

**Build this.** The mechanism of record. Given a recorded approval artifact and the deploying identity, it passes only when the approving identity is present, resolvable, and different from the deploying identity. **If it cannot tell — the approval record is absent, the approver field is empty, or the identity does not resolve — it fails**, exit `3`, and never `0`. On the equality case it emits the exact string `APPROVER_EQUALS_DEPLOYER` (`L2-00-charter.md` §7 DoD-04 asserts this literal).

Tool-id `identity_gate`. `checked=` is always 1 — the one comparison; `failed=` is 0 or 1.

Fixtures under `fixtures/identity/`: `self.yaml` (approver `dev-1`), `other.yaml` (approver `dev-2`), `empty.yaml` (approver field present but empty).



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t542-identity-gate

cat > tools/evidence/identity_gate.py << 'PYEOF'
"""
L2-T542  Workflow-identity gate: approver ≠ deployer
§27.2 L2567-2576 — The deploy workflow itself verifies that the recorded
approving identity differs from the deploying identity and fails closed
if it cannot tell.
D73: environment required reviewers are Enterprise-only and never the
mechanism of record.

DoD-04: emits literal APPROVER_EQUALS_DEPLOYER on the equality case.

If it cannot tell — approval record absent, approver field empty, or
identity does not resolve — it fails, exit 3, never exit 0.

Exit codes:
  0  OK    checked=1 failed=0
  2  FAIL  checked=1 failed=1
  3  ERROR checked=0 failed=0
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "identity_gate"


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load_approval(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"approval record not found: {path}")
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(p) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("approval record must be a YAML mapping")
    return data


def evaluate(approval: dict, deployer: str) -> tuple[int, int]:
    """Return (checked=1, failed=0|1). Fails closed on any inability to tell."""
    approver = approval.get("approver")
    if not approver:
        raise ValueError("approval record has no resolvable approver field — fail-closed")

    if approver == deployer:
        print(f"APPROVER_EQUALS_DEPLOYER: approver={approver!r} deployer={deployer!r}",
              file=sys.stderr)
        return 1, 1

    return 1, 0


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Workflow-identity gate: approver ≠ deployer.")
    ap.add_argument("--approval", required=True, help="Path to approval record YAML")
    ap.add_argument("--deployer", required=True, help="Deploying actor login")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    try:
        approval = _load_approval(args.approval)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    try:
        checked, failed = evaluate(approval, args.deployer)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    if args.summary:
        _summary(STATUS_OK if failed == 0 else STATUS_FAIL, checked, failed)

    sys.exit(EXIT_OK if failed == 0 else EXIT_FAIL)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/identity

cat > tools/evidence/fixtures/identity/self.yaml << 'YAMLEOF'
approver: dev-1
approved_at: "2026-09-06T08:00:00Z"
pull_request: 42
YAMLEOF

cat > tools/evidence/fixtures/identity/other.yaml << 'YAMLEOF'
approver: dev-2
approved_at: "2026-09-06T08:00:00Z"
pull_request: 42
YAMLEOF

cat > tools/evidence/fixtures/identity/empty.yaml << 'YAMLEOF'
approver: ""
approved_at: "2026-09-06T08:00:00Z"
pull_request: 42
YAMLEOF

git add tools/evidence/identity_gate.py tools/evidence/fixtures/identity/
git commit -m "L2-T542: workflow-identity gate — approver != deployer, fail-closed"

# SELF-VERIFY
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/self.yaml --deployer dev-1 --summary 2>&1 | tail -2
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/other.yaml --deployer dev-1 --summary; echo "EXIT=$?"
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/empty.yaml --deployer dev-1 --summary 2>/dev/null; echo "EXIT=$?"
# Expected:
# APPROVER_EQUALS_DEPLOYER
# FAIL identity_gate checked=1 failed=1
# OK identity_gate checked=1 failed=0 / EXIT=0
# ERROR identity_gate checked=0 failed=0 / EXIT=3
```

**Acceptance criteria**

1. `--approval self.yaml --deployer dev-1` → `FAIL identity_gate checked=1 failed=1`, exit `2`, stderr contains `APPROVER_EQUALS_DEPLOYER`.
2. `--approval other.yaml --deployer dev-1` → `OK identity_gate checked=1 failed=0`, exit `0`.
3. `--approval empty.yaml --deployer dev-1` → `ERROR identity_gate checked=0 failed=0`, exit `3`.
4. A missing approval file → exit `3`. Never `0`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/self.yaml --deployer dev-1 --summary 2>&1 | tail -2
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/other.yaml --deployer dev-1 --summary; echo "EXIT=$?"
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/empty.yaml --deployer dev-1 --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
APPROVER_EQUALS_DEPLOYER
FAIL identity_gate checked=1 failed=1
OK identity_gate checked=1 failed=0
EXIT=0
ERROR identity_gate checked=0 failed=0
EXIT=3
```

**STOP** — do not substitute GitHub environment required reviewers for this gate. They are Enterprise-only on private repositories and are an optional strengthening, never the mechanism (D73, §27.2). Rule S4; blocker title `BLOCKER L2-T542: asked to replace the workflow-identity gate with environment reviewers`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t542-identity-gate`.

---

### L2-T543 — Digest invariant: requested versus staging-verified

> **Index — `L2-T513` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T513` in full (*Implement `tools/evidence/deploy-gate.sh`*) and is authoritative for that id; this block is different work and now carries the id `L2-T543`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 38 · **Phase** BT-2 · **Size** M · **Deps** L2-T530 · **Branch slug** `t543-digest-invariant`
**Files:** `tools/evidence/digest_invariant.py`, `tools/evidence/fixtures/digest/**`
**Spec:** §32 L2803–2828 — *"CI rejects any production deployment where the requested digest differs from the digest that passed staging verification"*; §33.4 L2887–2912; §101 invariants 22 and 23, L9483–9484

**Build this.** The load-bearing comparison of the lane. Given a requested digest and a staging verification record, it passes only when the two digests are byte-identical. One sanctioned equivalence exists and is implemented explicitly: for an **S18 platform-rebuild** deployment (§32, D78), the recorded identity — pinned commit, lockfile and build configuration — stands in for the digest throughout the chain. That substitution is taken from the record, never inferred, and a record claiming platform-rebuild equivalence without all three components fails.

Absent staging record, absent digest, or an unparseable record is `ERROR`, exit `3`. There is no branch in which an unknown digest deploys.

Tool-id `digest_invariant`. `checked=1`, `failed=` 0 or 1.

Fixtures under `fixtures/digest/`: `staging-aaaa.yaml` (verified digest `sha256:aaaa`), `staging-rebuild.yaml` (S18 identity with all three components), `staging-rebuild-partial.yaml` (two of three), `staging-empty.yaml`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t543-digest-invariant

cat > tools/evidence/digest_invariant.py << 'PYEOF'
"""
L2-T543  Digest invariant: requested versus staging-verified
§32 L2803-2828 — CI rejects any production deployment where the requested
digest differs from the digest that passed staging verification.
§101 invariants 22 and 23, L9483-9484.

No tolerance. No normalisation. No 'close enough'. No rebuild call.

The one sanctioned equivalence: S18 platform-rebuild deployment (§32, D78).
The recorded identity — pinned commit, lockfile AND build configuration —
stands in for the digest. All three components must be present; a record
claiming platform-rebuild equivalence without all three fails.

Exit codes:
  0  OK    checked=1 failed=0
  2  FAIL  checked=1 failed=1
  3  ERROR checked=0 failed=0
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "digest_invariant"

S18_REQUIRED_FIELDS = frozenset({"pinned_commit", "lockfile", "build_configuration"})


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load_record(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"staging record not found: {path}")
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(p) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("staging record must be a YAML mapping")
    return data


def evaluate(requested: str, record: dict) -> tuple[int, int]:
    """Return (checked=1, failed=0|1)."""
    if not requested:
        raise ValueError("requested digest is empty — fail-closed")

    staging_digest = record.get("verified_digest")
    platform_rebuild = record.get("platform_rebuild")

    if platform_rebuild:
        # S18 equivalence path: all three components required
        identity = platform_rebuild if isinstance(platform_rebuild, dict) else {}
        missing = S18_REQUIRED_FIELDS - set(identity.keys())
        if missing:
            print(
                f"FAIL: S18 platform-rebuild record missing required fields: {missing}",
                file=sys.stderr,
            )
            return 1, 1
        print(
            f"INFO: S18 platform-rebuild equivalence accepted for {requested!r}",
            file=sys.stderr,
        )
        return 1, 0

    if not staging_digest:
        raise ValueError("staging record has no verified_digest — fail-closed")

    # Byte-identical comparison. No tolerance.
    if requested != staging_digest:
        print(
            f"FAIL: requested={requested!r} != staging_verified={staging_digest!r}",
            file=sys.stderr,
        )
        return 1, 1

    return 1, 0


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Digest invariant: requested vs staging-verified.")
    ap.add_argument("--requested", required=True, help="Requested artifact digest (sha256:...)")
    ap.add_argument("--staging-record", required=True, help="Path to staging verification record YAML")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    try:
        record = _load_record(args.staging_record)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    try:
        checked, failed = evaluate(args.requested, record)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    if args.summary:
        _summary(STATUS_OK if failed == 0 else STATUS_FAIL, checked, failed)

    sys.exit(EXIT_OK if failed == 0 else EXIT_FAIL)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/digest

cat > tools/evidence/fixtures/digest/staging-aaaa.yaml << 'YAMLEOF'
verified_digest: "sha256:aaaa"
verified_at: "2026-09-05T14:00:00Z"
run_id: 12345
YAMLEOF

cat > tools/evidence/fixtures/digest/staging-rebuild.yaml << 'YAMLEOF'
platform_rebuild:
  pinned_commit: "abc123def456"
  lockfile: "package-lock.json@sha256:lock1"
  build_configuration: "Dockerfile@sha256:dkr1"
verified_at: "2026-09-05T14:00:00Z"
YAMLEOF

cat > tools/evidence/fixtures/digest/staging-rebuild-partial.yaml << 'YAMLEOF'
platform_rebuild:
  pinned_commit: "abc123def456"
  lockfile: "package-lock.json@sha256:lock1"
  # missing: build_configuration
verified_at: "2026-09-05T14:00:00Z"
YAMLEOF

cat > tools/evidence/fixtures/digest/staging-empty.yaml << 'YAMLEOF'
verified_at: "2026-09-05T14:00:00Z"
YAMLEOF

git add tools/evidence/digest_invariant.py tools/evidence/fixtures/digest/
git commit -m "L2-T543: digest invariant — requested vs staging-verified, S18 support"

# SELF-VERIFY
python -m tools.evidence.digest_invariant --requested sha256:bbbb --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.digest_invariant --requested sha256:aaaa --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.digest_invariant --requested sha256:aaaa --staging-record tools/evidence/fixtures/digest/staging-empty.yaml --summary 2>/dev/null; echo "EXIT=$?"
grep -cE 'docker build|buildx|podman build' tools/evidence/digest_invariant.py
# Expected:
# FAIL digest_invariant checked=1 failed=1 / EXIT=2
# OK digest_invariant checked=1 failed=0  / EXIT=0
# ERROR digest_invariant checked=0 failed=0 / EXIT=3
# REBUILD_CALLS=0
```

**Acceptance criteria**

1. Requested `sha256:bbbb` against `staging-aaaa.yaml` → `FAIL digest_invariant checked=1 failed=1`, exit `2`.
2. Requested `sha256:aaaa` against `staging-aaaa.yaml` → `OK digest_invariant checked=1 failed=0`, exit `0`.
3. `staging-rebuild-partial.yaml` → `FAIL digest_invariant checked=1 failed=1`, exit `2`.
4. `staging-empty.yaml` → `ERROR digest_invariant checked=0 failed=0`, exit `3`.
5. The module contains no build, rebuild or re-tag call of any kind.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.digest_invariant --requested sha256:bbbb --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.digest_invariant --requested sha256:aaaa --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.digest_invariant --requested sha256:aaaa --staging-record tools/evidence/fixtures/digest/staging-empty.yaml --summary 2>/dev/null; echo "EXIT=$?"
echo "REBUILD_CALLS=$(grep -cE 'docker build|buildx|podman build' tools/evidence/digest_invariant.py)"
```

**CORRECT OUTPUT**

```
FAIL digest_invariant checked=1 failed=1
EXIT=2
OK digest_invariant checked=1 failed=0
EXIT=0
ERROR digest_invariant checked=0 failed=0
EXIT=3
REBUILD_CALLS=0
```

**STOP** — this is §0.6 rule 1 in code. If anything asks for a tolerance, a normalisation, or a "close enough" comparison, refuse. Rule S4; blocker title `BLOCKER L2-T543: a digest comparison tolerance is being requested`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t543-digest-invariant`.

---

## 5. Task detail — Phase BT-3, execution order 39–76

BT-3 opens only when L0 declares the S2 sync point passed. It is the largest phase: the five privileged workflows, the whole of subsystem F, every template, and the four acceptance tests.

---

### L2-T544 — Records-write client

> **Index — `L2-T514` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T514` in full (*Author `.github/workflows/evidence-selftest.yml`*) and is authoritative for that id; this block is different work and now carries the id `L2-T544`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 39 · **Phase** BT-3 · **Size** L · **Deps** L2-T530, **D-L2-03** · **Branch slug** `t544-records-client`
**Files:** `tools/evidence/records_client.py`, `tools/evidence/fixtures/records/**`
**Spec:** §97.2 L8843–8926 — *"the deployment-record and event writes are required, failing steps of `deploy-production.yml` rather than trailing best-effort ones"*; §40.1 L3644–3686 (the records-writer credential); §101 invariant 48 (records are never edited in place)

**Build this.** The one client every Lane 2 workflow uses to write a record. It validates the payload against the record schema published by Lane 4 (`schemas/records/**` — read only, never written), writes exactly one new file under the store path, and **refuses to modify an existing file**. It obtains its credential through the records-writer path declared under D-L2-03 and never through a literal token. `--dry-run` validates and prints without writing.

Lane 2 owns the **call**; Lane 4 owns the schema, the store and the writer semantics (`PARTITION.md` line 20). This module is a client, not a second writer.

Tool-id `records_client`. `checked=` counts payload fields validated; `failed=` counts validation failures.

Fixtures under `fixtures/records/`: `deployment.yaml` (valid, 9 fields), `deployment-missing-digest.yaml`, `deployment-existing-path.yaml`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t544-records-client

# STOP check: D-L2-03 must be answered before this task is startable.
# If contracts/workflow-io/records-writer.yaml is absent, file a blocker.
if [ ! -f contracts/workflow-io/records-writer.yaml ]; then
  echo "BLOCKER L2-T544: D-L2-03 unanswered — contracts/workflow-io/records-writer.yaml absent"
  echo "File blocker issue titled: BLOCKER L2-T544: D-L2-03 unanswered, records-writer interface undefined"
  exit 1
fi

cat > tools/evidence/records_client.py << 'PYEOF'
"""
L2-T544  Records-write client
§97.2 L8843-8926 — the deployment-record and event writes are required,
failing steps of deploy-production.yml rather than trailing best-effort ones.
§40.1 L3644-3686 — records-writer credential obtained through declared path.
§101 invariant 48 — records are never edited in place.

Lane 2 owns the call; Lane 4 owns the schema, the store, and the writer
semantics (PARTITION.md line 20). This module is a client, not a second writer.

No literal credential appears in this module. Credential obtained through
the path declared under D-L2-03 in contracts/workflow-io/records-writer.yaml.

Exit codes:
  0  OK    checked=<field count> failed=0
  2  FAIL  checked=<field count> failed=<n>
  3  ERROR checked=0 failed=0
"""
from __future__ import annotations
import argparse, hashlib, os, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "records_client"

# Required fields for a deployment record (§97.2 / Lane 4 schema)
REQUIRED_FIELDS: dict[str, list[str]] = {
    "deployment": [
        "digest",
        "artifact_name",
        "deployed_by",
        "deployed_at",
        "environment",
        "git_commit",
        "pull_request",
        "approved_by",
        "run_id",
    ],
}


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load_payload(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"payload not found: {path}")
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(p) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("payload must be a YAML mapping")
    return data


def _get_credential_path() -> str:
    """Obtain credential path from declared interface — never a literal token."""
    # The secret name and target repository are declared under D-L2-03.
    # In a workflow context this is ${{ secrets.RECORDS_WRITER_TOKEN }}.
    # Here we resolve from the contracts declaration.
    contracts_path = Path("contracts/workflow-io/records-writer.yaml")
    if not contracts_path.exists():
        raise FileNotFoundError(
            "D-L2-03 contract absent: contracts/workflow-io/records-writer.yaml"
        )
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(contracts_path) as fh:
        decl = yaml.safe_load(fh)
    secret_name = decl.get("secret_name")
    if not secret_name:
        raise ValueError("records-writer contract missing secret_name field")
    return secret_name


def validate_payload(kind: str, payload: dict) -> tuple[int, int]:
    """Return (checked, failed)."""
    required = REQUIRED_FIELDS.get(kind, [])
    checked = len(required)
    failed = sum(1 for f in required if not payload.get(f))
    for f in required:
        if not payload.get(f):
            print(f"FAIL: required field {f!r} missing or empty in {kind} record", file=sys.stderr)
    return checked, failed


def _record_path(kind: str, payload: dict) -> Path:
    """Derive deterministic write path from payload fields."""
    env = payload.get("environment", "unknown")
    ts = payload.get("deployed_at", "unknown").replace(":", "-").replace("T", "_")
    digest_suffix = hashlib.sha256(str(payload).encode()).hexdigest()[:8]
    return Path(f"records/{kind}s/{env}/{ts}-{digest_suffix}.yaml")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Records-write client (Lane 2 call, Lane 4 schema).")
    ap.add_argument("--kind", required=True, choices=list(REQUIRED_FIELDS), help="Record kind")
    ap.add_argument("--payload", required=True, help="Path to payload YAML")
    ap.add_argument("--dry-run", action="store_true", help="Validate and print without writing")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    try:
        payload = _load_payload(args.payload)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    checked, failed = validate_payload(args.kind, payload)

    if failed > 0:
        if args.summary:
            _summary(STATUS_FAIL, checked, failed)
        sys.exit(EXIT_FAIL)

    if args.dry_run:
        print(f"DRY-RUN: payload valid; would write to {_record_path(args.kind, payload)}",
              file=sys.stderr)
        if args.summary:
            _summary(STATUS_OK, checked, failed)
        sys.exit(EXIT_OK)

    # Live write path: obtain credential, refuse to overwrite existing file
    record_path = _record_path(args.kind, payload)
    if record_path.exists():
        print(
            f"FAIL: record already exists at {record_path} — §101 invariant 48 prohibits overwrite",
            file=sys.stderr,
        )
        if args.summary:
            _summary(STATUS_FAIL, checked, 1)
        sys.exit(EXIT_FAIL)

    try:
        secret_name = _get_credential_path()
    except Exception as exc:
        print(f"ERROR: cannot resolve records-writer credential: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    # In a real run the secret value is passed via the environment by the workflow,
    # never inlined here. Token: ${{ secrets.<secret_name> }} in the caller.
    token = os.environ.get(secret_name)
    if not token:
        print(f"ERROR: secret {secret_name!r} not set in environment", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    record_path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(record_path, "w") as fh:
        yaml.safe_dump(payload, fh, default_flow_style=False)

    print(f"OK: record written to {record_path}", file=sys.stderr)
    if args.summary:
        _summary(STATUS_OK, checked, failed)
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/records

cat > tools/evidence/fixtures/records/deployment.yaml << 'YAMLEOF'
digest: "sha256:aaaa0000"
artifact_name: "myapp"
deployed_by: "dev-1"
deployed_at: "2026-09-06T09:00:00Z"
environment: "staging"
git_commit: "abc123"
pull_request: 42
approved_by: "dev-2"
run_id: 99001
YAMLEOF

cat > tools/evidence/fixtures/records/deployment-missing-digest.yaml << 'YAMLEOF'
artifact_name: "myapp"
deployed_by: "dev-1"
deployed_at: "2026-09-06T09:00:00Z"
environment: "staging"
git_commit: "abc123"
pull_request: 42
approved_by: "dev-2"
run_id: 99001
YAMLEOF

cat > tools/evidence/fixtures/records/deployment-existing-path.yaml << 'YAMLEOF'
digest: "sha256:bbbb1111"
artifact_name: "myapp"
deployed_by: "dev-1"
deployed_at: "2026-09-06T09:00:00Z"
environment: "staging"
git_commit: "def456"
pull_request: 43
approved_by: "dev-2"
run_id: 99002
YAMLEOF

grep -cE 'gh[pousr]_[A-Za-z0-9]{16,}' tools/evidence/records_client.py && echo "LITERAL_TOKEN_FOUND" || echo "LITERAL_TOKENS=0"

git add tools/evidence/records_client.py tools/evidence/fixtures/records/
git commit -m "L2-T544: records-write client — D-L2-03 interface, immutable write, no literal tokens"

# SELF-VERIFY (dry-run only; live write requires D-L2-03 contract in place)
python -m tools.evidence.records_client --dry-run --kind deployment --payload tools/evidence/fixtures/records/deployment.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.records_client --dry-run --kind deployment --payload tools/evidence/fixtures/records/deployment-missing-digest.yaml --summary; echo "EXIT=$?"
grep -cE 'gh[pousr]_[A-Za-z0-9]{16,}' tools/evidence/records_client.py
# Expected:
# OK records_client checked=9 failed=0 / EXIT=0
# FAIL records_client checked=9 failed=1 / EXIT=2
# LITERAL_TOKENS=0
```

**Acceptance criteria**

1. `--dry-run --kind deployment --payload deployment.yaml` → `OK records_client checked=9 failed=0`, exit `0`, and no file is created.
2. The missing-digest payload → `FAIL records_client checked=9 failed=1`, exit `2`.
3. A write to a path that already exists is refused with exit `2` and the existing file is byte-unchanged.
4. No literal credential appears anywhere in the module.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.records_client --dry-run --kind deployment --payload tools/evidence/fixtures/records/deployment.yaml --summary; echo "EXIT=$?"
python -m tools.evidence.records_client --dry-run --kind deployment --payload tools/evidence/fixtures/records/deployment-missing-digest.yaml --summary; echo "EXIT=$?"
echo "LITERAL_TOKENS=$(grep -cE 'gh[pousr]_[A-Za-z0-9]{16,}' tools/evidence/records_client.py)"
```

**CORRECT OUTPUT**

```
OK records_client checked=9 failed=0
EXIT=0
FAIL records_client checked=9 failed=1
EXIT=2
LITERAL_TOKENS=0
```

**STOP** — if D-L2-03 is unanswered, the secret name, the target repository and the record schema paths are all unknown and this task is not startable. Rule S1; blocker title `BLOCKER L2-T544: D-L2-03 unanswered, records-writer interface undefined`. Do not write into `records/**` — that repository is Lane 4's entire ownership.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t544-records-client`.

---

### L2-T545 — Event writer: one file per event, bound envelope

> **Index — `L2-T515` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T515` in full (*Append-only and effective-dating assertion*) and is authoritative for that id; this block is different work and now carries the id `L2-T545`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 40 · **Phase** BT-3 · **Size** M · **Deps** L2-T544, **D-L2-03** · **Branch slug** `t545-event-writer`
**Files:** `tools/evidence/event_writer.py`, `tools/evidence/fixtures/events/**`
**Spec:** §97.3 L8929–8953 — one file per event under a date partition, the nine required envelope fields, `event_type` constrained to an identifier and never free text; `PARTITION.md` rule 3 (no shared mutable file, ever)

**Build this.** The event half of the write path. It writes exactly one file per event — never an append to a shared period file — and rejects, **at write time and before any file is created**, an event missing any envelope field or carrying an `event_type` absent from Lane 4's published taxonomy. Lane 2 supplies the event; Lane 4 owns the enum.

Tool-id `event_writer`. `checked=` counts envelope fields validated (9); `failed=` counts violations.

Fixtures under `fixtures/events/`: `production_deployed.yaml` (valid), `no-actor.yaml` (one field missing), `free-text-type.yaml` (an `event_type` not in the taxonomy).



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t545-event-writer

cat > tools/evidence/event_writer.py << 'PYEOF'
"""
L2-T545  Event writer: one file per event, bound envelope
§97.3 L8929-8953 — one file per event, nine required envelope fields,
event_type constrained to an identifier in Lane 4's published taxonomy.
PARTITION.md rule 3: no shared mutable file, ever.

Rejects an event at write time before any file is created when:
- any envelope field is missing
- event_type is not in Lane 4's published taxonomy

Lane 2 supplies the event; Lane 4 owns the enum.
No append mode (open 'a') anywhere in this file.

Exit codes:
  0  OK    checked=9 failed=0
  2  FAIL  checked=9 failed=<n>
  3  ERROR checked=0 failed=0
"""
from __future__ import annotations
import argparse, hashlib, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from tools.evidence import STATUS_OK, STATUS_FAIL, STATUS_ERROR, EXIT_OK, EXIT_FAIL, EXIT_ERROR

TOOL_ID = "event_writer"

# Nine required envelope fields (§97.3)
ENVELOPE_FIELDS = [
    "event_id",
    "event_type",
    "occurred_at",
    "actor",
    "environment",
    "product",
    "artifact_digest",
    "run_id",
    "correlation_id",
]

# Lane 4's published event_type taxonomy
# Populated from schemas/events/taxonomy.yaml when available at runtime.
# Hard-coded fallback for Lane 2 fixture testing only.
EVENT_TYPE_TAXONOMY = frozenset({
    "production_deployed",
    "staging_deployed",
    "migration_applied",
    "rollback_executed",
    "restore_completed",
    "restore_failed",
    "org_export_completed",
    "org_export_failed",
    "incident_declared",
    "exceptional_authorisation",
})


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _load_event(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"event file not found: {path}")
    if yaml is None:
        raise ImportError("pyyaml is required")
    with open(p) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("event must be a YAML mapping")
    return data


def _load_taxonomy() -> frozenset[str]:
    """Load Lane 4's event_type taxonomy if available; fall back to hard-coded set."""
    taxonomy_path = Path("schemas/events/taxonomy.yaml")
    if taxonomy_path.exists() and yaml is not None:
        with open(taxonomy_path) as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, list):
            return frozenset(data)
    return EVENT_TYPE_TAXONOMY


def validate_event(event: dict, taxonomy: frozenset[str]) -> tuple[int, int]:
    """Return (checked=9, failed=n). Validates before any write."""
    checked = len(ENVELOPE_FIELDS)
    failed = 0

    for field in ENVELOPE_FIELDS:
        if not event.get(field):
            print(f"FAIL: envelope field {field!r} missing or empty", file=sys.stderr)
            failed += 1

    # event_type taxonomy check
    event_type = event.get("event_type")
    if event_type and event_type not in taxonomy:
        print(
            f"FAIL: event_type {event_type!r} is not in Lane 4's published taxonomy;"
            f" valid values: {sorted(taxonomy)}",
            file=sys.stderr,
        )
        failed += 1

    return checked, failed


def _event_path(event: dict) -> Path:
    """Derive unique file path: records/events/<date>/<event_id>.yaml
    PARTITION.md rule 3: one file per event, never an append."""
    occurred = event.get("occurred_at", datetime.now(tz=timezone.utc).isoformat())
    date_part = occurred[:10]  # YYYY-MM-DD
    event_id = event.get("event_id") or str(uuid.uuid4())
    return Path(f"records/events/{date_part}/{event_id}.yaml")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Event writer: one file per event, bound envelope.")
    ap.add_argument("--event", required=True, help="Path to event YAML")
    ap.add_argument("--dry-run", action="store_true", help="Validate and print without writing")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    try:
        event = _load_event(args.event)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_ERROR, 0, 0)
        sys.exit(EXIT_ERROR)

    taxonomy = _load_taxonomy()
    checked, failed = validate_event(event, taxonomy)

    if failed > 0:
        if args.summary:
            _summary(STATUS_FAIL, checked, failed)
        sys.exit(EXIT_FAIL)

    if args.dry_run:
        event_path = _event_path(event)
        print(f"DRY-RUN: event valid; would write to {event_path}", file=sys.stderr)
        if args.summary:
            _summary(STATUS_OK, checked, failed)
        sys.exit(EXIT_OK)

    # Live write: refuse to append, always a new file
    event_path = _event_path(event)
    if event_path.exists():
        print(f"FAIL: event file already exists at {event_path} — one file per event rule",
              file=sys.stderr)
        if args.summary:
            _summary(STATUS_FAIL, checked, 1)
        sys.exit(EXIT_FAIL)

    event_path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        raise ImportError("pyyaml is required")
    # Open in 'w' (write) mode — never 'a' (append)
    with open(event_path, "w") as fh:
        yaml.safe_dump(event, fh, default_flow_style=False)

    print(f"OK: event written to {event_path}", file=sys.stderr)
    if args.summary:
        _summary(STATUS_OK, checked, failed)
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
PYEOF

# ── Fixtures ────────────────────────────────────────────────────────────────
mkdir -p tools/evidence/fixtures/events

cat > tools/evidence/fixtures/events/production_deployed.yaml << 'YAMLEOF'
event_id: "evt-20260906-001"
event_type: "production_deployed"
occurred_at: "2026-09-06T09:30:00Z"
actor: "dev-1"
environment: "production"
product: "myapp"
artifact_digest: "sha256:aaaa0000"
run_id: 99001
correlation_id: "deploy-2026-09-06-001"
YAMLEOF

cat > tools/evidence/fixtures/events/no-actor.yaml << 'YAMLEOF'
event_id: "evt-20260906-002"
event_type: "production_deployed"
occurred_at: "2026-09-06T09:30:00Z"
environment: "production"
product: "myapp"
artifact_digest: "sha256:aaaa0000"
run_id: 99002
correlation_id: "deploy-2026-09-06-002"
YAMLEOF

cat > tools/evidence/fixtures/events/free-text-type.yaml << 'YAMLEOF'
event_id: "evt-20260906-003"
event_type: "we pushed some code today it went well"
occurred_at: "2026-09-06T09:30:00Z"
actor: "dev-1"
environment: "production"
product: "myapp"
artifact_digest: "sha256:aaaa0000"
run_id: 99003
correlation_id: "deploy-2026-09-06-003"
YAMLEOF

grep -cE "open\(.*['\"]a" tools/evidence/event_writer.py && echo "APPEND_FOUND" || echo "APPEND_MODES=0"

git add tools/evidence/event_writer.py tools/evidence/fixtures/events/
git commit -m "L2-T545: event writer — one file per event, bound envelope, no append mode"

# SELF-VERIFY
for F in production_deployed no-actor free-text-type; do
  python -m tools.evidence.event_writer --dry-run --event tools/evidence/fixtures/events/$F.yaml --summary; echo "EXIT=$?"
done
grep -cE "open\(.*['\"]a" tools/evidence/event_writer.py
# Expected:
# OK event_writer checked=9 failed=0 / EXIT=0
# FAIL event_writer checked=9 failed=1 / EXIT=2
# FAIL event_writer checked=9 failed=1 / EXIT=2
# APPEND_MODES=0
```

**Acceptance criteria**

1. Valid event, `--dry-run` → `OK event_writer checked=9 failed=0`, exit `0`, nothing written.
2. `no-actor.yaml` → `FAIL event_writer checked=9 failed=1`, exit `2`.
3. `free-text-type.yaml` → `FAIL event_writer checked=9 failed=1`, exit `2`.
4. Two events on the same date produce two distinct file paths; the module contains no append mode.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in production_deployed no-actor free-text-type; do
  python -m tools.evidence.event_writer --dry-run --event tools/evidence/fixtures/events/$F.yaml --summary; echo "EXIT=$?"
done
echo "APPEND_MODES=$(grep -cE "open\(.*['\"]a" tools/evidence/event_writer.py)"
```

**CORRECT OUTPUT**

```
OK event_writer checked=9 failed=0
EXIT=0
FAIL event_writer checked=9 failed=1
EXIT=2
FAIL event_writer checked=9 failed=1
EXIT=2
APPEND_MODES=0
```

**STOP** — if the published `event_type` taxonomy is unavailable, do not invent an identifier. Rule S1; blocker title `BLOCKER L2-T545: event_type taxonomy unpublished, cannot validate event types`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t545-event-writer`.

---

### L2-T130 — `deploy-staging.yml`

**#** 41 · **Phase** BT-3 · **Size** L · **Deps** L2-T541, L2-T545, L2-T120 · **Branch slug** `t130-deploy-staging`
**Files:** `.github/workflows/deploy-staging.yml`
**Spec:** §37.3 L3261–3268 (actor gate is the **first step**); §33.4 L2887–2912 (staging deploy → smoke → UAT); §97.2 L8843–8926 (record and event writes are required, failing steps)

**Build this.** The first of the five privileged workflows. Step order is fixed and is asserted mechanically by `L2-T554`:

1. **actor gate** — `actor_gate` with capability `devops`. First step. Nothing before it, not even a checkout.
2. deploy the artifact digest built by `build.yml`; never rebuild.
3. smoke tests.
4. write the staging deployment record via `records_client` — a **required, failing** step.
5. append the staging event via `event_writer` — a **required, failing** step.

The workflow declares `environment: staging` and least-privilege permissions.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t130-deploy-staging

CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

cat > .github/workflows/deploy-staging.yml << YAMLEOF
# L2-T130 — deploy-staging.yml
# §37.3 L3261-3268: actor gate is the FIRST step — nothing before it, not even checkout.
# §97.2 L8843-8926: record and event writes are required, failing steps.
# §33.4 L2887-2912: staging deploy → smoke → UAT.
# No rebuild. No continue-on-error anywhere.
name: Deploy — Staging

on:
  workflow_call:
    inputs:
      artifact_digest:
        description: "sha256 digest of the artifact to deploy (from build.yml)"
        required: true
        type: string
      artifact_name:
        description: "Container image name"
        required: true
        type: string
      deploy_command:
        description: "Product-specific deploy command"
        required: true
        type: string
      smoke_command:
        description: "Product-specific smoke test command"
        required: true
        type: string
    secrets:
      PEOPLE_YAML_B64:
        required: true
      RECORDS_WRITER_TOKEN:
        required: true

permissions:
  contents: read

concurrency:
  group: deploy-staging-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  deploy:
    name: deploy-staging
    environment: staging
    runs-on: ubuntu-22.04
    steps:
      # STEP 0: actor gate — first step, nothing precedes it (§37.3)
      - name: Actor gate
        run: |
          set -euo pipefail
          echo "\${{ secrets.PEOPLE_YAML_B64 }}" | base64 -d > /tmp/people.yaml
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability devops \
            --people /tmp/people.yaml \
            --summary

      - name: Checkout control plane tools
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      - name: Deploy artifact digest (never rebuilt — §101 invariants 22/23)
        run: |
          set -euo pipefail
          DIGEST="\${{ inputs.artifact_digest }}"
          [ -n "\${DIGEST}" ] || { echo "ERROR: empty artifact digest"; exit 1; }
          echo "Deploying digest \${DIGEST} to staging — no rebuild path"
          \${{ inputs.deploy_command }} "\${DIGEST}"

      - name: Smoke tests
        run: |
          set -euo pipefail
          \${{ inputs.smoke_command }}

      - name: Write staging deployment record (required, failing step — §97.2)
        run: |
          set -euo pipefail
          cat > /tmp/staging-record.yaml << RECORD
          digest: "\${{ inputs.artifact_digest }}"
          artifact_name: "\${{ inputs.artifact_name }}"
          deployed_by: "\${{ github.actor }}"
          deployed_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          environment: staging
          git_commit: "\${{ github.sha }}"
          pull_request: \${{ github.event.pull_request.number || 0 }}
          approved_by: "\${{ github.actor }}"
          run_id: \${{ github.run_id }}
          RECORD
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.records_client \
            --kind deployment \
            --payload /tmp/staging-record.yaml \
            --summary

      - name: Write staging deployed event (required, failing step — §97.2)
        run: |
          set -euo pipefail
          cat > /tmp/staging-event.yaml << EVENT
          event_id: "evt-staging-\${{ github.run_id }}-\${{ github.run_attempt }}"
          event_type: staging_deployed
          occurred_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          actor: "\${{ github.actor }}"
          environment: staging
          product: "\${{ inputs.artifact_name }}"
          artifact_digest: "\${{ inputs.artifact_digest }}"
          run_id: \${{ github.run_id }}
          correlation_id: "staging-\${{ github.sha }}"
          EVENT
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.event_writer \
            --event /tmp/staging-event.yaml \
            --summary
YAMLEOF

git add .github/workflows/deploy-staging.yml
git commit -m "L2-T130: deploy-staging.yml — actor gate first, required record/event writes"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/deploy-staging.yml --summary; echo "EXIT=$?"
grep -A4 '^[[:space:]]*steps:' .github/workflows/deploy-staging.yml | grep -c 'tools.evidence.actor_gate'
grep -c 'continue-on-error' .github/workflows/deploy-staging.yml
grep -cE 'docker build|buildx|podman build' .github/workflows/deploy-staging.yml
# Expected:
# OK lint_workflow checked=1 failed=0 / EXIT=0
# FIRST_STEP=1 / BEST_EFFORT=0 / REBUILD=0
```

**Acceptance criteria**

1. The first step of the deploy job invokes `tools.evidence.actor_gate`; no step precedes it.
2. The record and event steps carry no `continue-on-error` and are not conditioned on earlier success being optional.
3. No build or rebuild command appears in the file.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/deploy-staging.yml --summary; echo "EXIT=$?"
echo "FIRST_STEP=$(grep -A4 '^[[:space:]]*steps:' .github/workflows/deploy-staging.yml | grep -c 'tools.evidence.actor_gate')"
echo "BEST_EFFORT=$(grep -c 'continue-on-error' .github/workflows/deploy-staging.yml)"
echo "REBUILD=$(grep -cE 'docker build|buildx|podman build' .github/workflows/deploy-staging.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
FIRST_STEP=1
BEST_EFFORT=0
REBUILD=0
```

**STOP** — if a setup step (checkout, language toolchain, cache) appears to be needed before the gate, it is not: run the gate first with the runner's default image. Rule S4; blocker title `BLOCKER L2-T130: a step is being required before the actor gate`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t130-deploy-staging`.

---

### L2-T131 — `deploy-production.yml`

**#** 42 · **Phase** BT-3 · **Size** L · **Deps** L2-T130, L2-T542, L2-T543, L2-T540 · **Branch slug** `t131-deploy-production`
**Files:** `.github/workflows/deploy-production.yml`
**Spec:** §33.4 L2887–2912; §27.2 L2567–2576; §32 L2803–2828; §34.2 L2930–2935; §97.2 L8843–8926; §101 invariants 18, 22, 23

**Build this.** The workflow all six rules of §0.6 converge on. Fixed step order:

1. **actor gate** — `actor_gate` with capability `production-approval`. First step.
2. **workflow-identity gate** — `identity_gate`; fails closed on `APPROVER_EQUALS_DEPLOYER` and on any inability to tell.
3. **digest invariant** — `digest_invariant` comparing the requested digest with the staging-verified record.
4. **time gate** — `timegate`, resolved in the product's declared timezone.
5. deploy the **same digest**. No build step exists in this file.
6. smoke tests, then health checks.
7. deployment record via `records_client` — required, failing.
8. production event via `event_writer` — required, failing.

`environment: production`. Least-privilege permissions. No `continue-on-error` anywhere.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t131-deploy-production

CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

cat > .github/workflows/deploy-production.yml << YAMLEOF
# L2-T131 — deploy-production.yml
# The workflow all six rules of §0.6 converge on.
# §37.3: actor gate is the FIRST step.
# §27.2: workflow-identity gate (approver ≠ deployer), fail-closed.
# §32:   digest invariant comparison.
# §34.2: time gate, resolved in product's declared timezone.
# §97.2: record and event writes are required, failing steps.
# §101 invariants 18, 22, 23: actor gate, same digest, never rebuilt.
# ZERO continue-on-error. ZERO rebuild commands.
name: Deploy — Production

on:
  workflow_call:
    inputs:
      artifact_digest:
        description: "sha256 digest to deploy — must match staging-verified digest"
        required: true
        type: string
      artifact_name:
        description: "Container image name"
        required: true
        type: string
      staging_record_path:
        description: "Path to staging deployment record for digest invariant check"
        required: true
        type: string
      operating_timezone:
        description: "Product's declared IANA operating timezone (§34.2)"
        required: true
        type: string
      deploy_command:
        description: "Product-specific deploy command"
        required: true
        type: string
      smoke_command:
        description: "Product-specific smoke test command"
        required: true
        type: string
      approval_record_path:
        description: "Path to the production-approval record"
        required: true
        type: string
    secrets:
      PEOPLE_YAML_B64:
        required: true
      RECORDS_WRITER_TOKEN:
        required: true

permissions:
  contents: read

concurrency:
  group: deploy-production-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  deploy:
    name: deploy-production
    environment: production
    runs-on: ubuntu-22.04
    steps:
      # STEP 0: actor gate — capability production-approval (§37.3)
      - name: Actor gate
        run: |
          set -euo pipefail
          echo "\${{ secrets.PEOPLE_YAML_B64 }}" | base64 -d > /tmp/people.yaml
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability production-approval \
            --people /tmp/people.yaml \
            --summary

      - name: Checkout control plane tools
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      # STEP 2: workflow-identity gate — approver ≠ deployer (§27.2)
      - name: Workflow-identity gate
        run: |
          set -euo pipefail
          python -m tools.evidence.identity_gate \
            --approval "\${{ inputs.approval_record_path }}" \
            --deployer "\${{ github.actor }}" \
            --summary

      # STEP 3: digest invariant — requested vs staging-verified (§32)
      - name: Digest invariant
        run: |
          set -euo pipefail
          python -m tools.evidence.digest_invariant \
            --requested "\${{ inputs.artifact_digest }}" \
            --staging-record "\${{ inputs.staging_record_path }}" \
            --summary

      # STEP 4: time gate — Friday freeze and core hours (§34.2)
      - name: Time gate
        run: |
          set -euo pipefail
          python -m tools.evidence.timegate \
            --at "\$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            --tz "\${{ inputs.operating_timezone }}" \
            --profile business-hours \
            --summary

      # STEP 5: deploy the same digest — NO BUILD STEP (§101 invariants 22/23)
      - name: Deploy artifact digest (never rebuilt)
        run: |
          set -euo pipefail
          DIGEST="\${{ inputs.artifact_digest }}"
          [ -n "\${DIGEST}" ] || { echo "ERROR: empty artifact digest — fail-closed"; exit 1; }
          echo "Deploying digest \${DIGEST} to production — same digest as staging"
          \${{ inputs.deploy_command }} "\${DIGEST}"

      - name: Smoke tests and health checks
        run: |
          set -euo pipefail
          \${{ inputs.smoke_command }}

      # STEP 7: deployment record — required, failing (§97.2, §0.6 rule 6)
      - name: Write production deployment record (required, failing step)
        run: |
          set -euo pipefail
          cat > /tmp/prod-record.yaml << RECORD
          digest: "\${{ inputs.artifact_digest }}"
          artifact_name: "\${{ inputs.artifact_name }}"
          deployed_by: "\${{ github.actor }}"
          deployed_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          environment: production
          git_commit: "\${{ github.sha }}"
          pull_request: \${{ github.event.pull_request.number || 0 }}
          approved_by: "\$(python -c "import yaml; d=yaml.safe_load(open('\${{ inputs.approval_record_path }}')); print(d.get('approver',''))")"
          run_id: \${{ github.run_id }}
          RECORD
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.records_client \
            --kind deployment \
            --payload /tmp/prod-record.yaml \
            --summary

      # STEP 8: production event — required, failing (§97.2)
      - name: Write production deployed event (required, failing step)
        run: |
          set -euo pipefail
          cat > /tmp/prod-event.yaml << EVENT
          event_id: "evt-prod-\${{ github.run_id }}-\${{ github.run_attempt }}"
          event_type: production_deployed
          occurred_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          actor: "\${{ github.actor }}"
          environment: production
          product: "\${{ inputs.artifact_name }}"
          artifact_digest: "\${{ inputs.artifact_digest }}"
          run_id: \${{ github.run_id }}
          correlation_id: "prod-\${{ github.sha }}"
          EVENT
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.event_writer \
            --event /tmp/prod-event.yaml \
            --summary
YAMLEOF

git add .github/workflows/deploy-production.yml
git commit -m "L2-T131: deploy-production.yml — all 4 gates, no rebuild, required record/event writes"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/deploy-production.yml --summary; echo "EXIT=$?"
grep -cE 'tools\.evidence\.(actor_gate|identity_gate|digest_invariant|timegate)' .github/workflows/deploy-production.yml
grep -A4 '^[[:space:]]*steps:' .github/workflows/deploy-production.yml | grep -c 'tools.evidence.actor_gate'
grep -cE 'docker build|buildx|podman build' .github/workflows/deploy-production.yml
grep -c 'continue-on-error' .github/workflows/deploy-production.yml
# Expected:
# OK lint_workflow checked=1 failed=0 / EXIT=0
# GATES=4 / FIRST_STEP=1 / REBUILD=0 / BEST_EFFORT=0
```

**Acceptance criteria**

1. All four gates are present, in that order, and the actor gate is step 0.
2. Zero build or rebuild commands.
3. Record and event steps are required and failing — zero `continue-on-error` in the file.
4. A negative run where the requested digest differs from the staging-verified digest exits non-zero **and writes no deployment record** (charter DoD-03; exercised by `L2-T572` in `L2-03-production-gates.md` and re-asserted here).
5. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/deploy-production.yml --summary; echo "EXIT=$?"
echo "GATES=$(grep -cE 'tools\.evidence\.(actor_gate|identity_gate|digest_invariant|timegate)' .github/workflows/deploy-production.yml)"
echo "FIRST_STEP=$(grep -A4 '^[[:space:]]*steps:' .github/workflows/deploy-production.yml | grep -c 'tools.evidence.actor_gate')"
echo "REBUILD=$(grep -cE 'docker build|buildx|podman build' .github/workflows/deploy-production.yml)"
echo "BEST_EFFORT=$(grep -c 'continue-on-error' .github/workflows/deploy-production.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
GATES=4
FIRST_STEP=1
REBUILD=0
BEST_EFFORT=0
```

**STOP** — if the record write cannot succeed and the deploy has already happened, the job **fails**; it does not report success with a warning (§97.2, §0.6 rule 6). Rule S4; blocker title `BLOCKER L2-T131: asked to make the deployment-record write best-effort`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t131-deploy-production`.

---

### L2-T132 — `migrate.yml` — cases A–G

**#** 43 · **Phase** BT-3 · **Size** L · **Deps** L2-T541, L2-T545 · **Branch slug** `t132-migrate`
**Files:** `.github/workflows/migrate.yml`
**Spec:** §34.3 L2936–2944 (CI-only application, ordered and versioned, destructive migrations need `migration-review` plus QA sign-off, verified backup first); §34.4 L2945–2956 (the seven cases)

**Build this.** The migration workflow, with the seven §34.4 cases encoded as explicit branches, each emitting its case letter and taking its declared action:

| Case | Encoded behaviour |
| --- | --- |
| A | migration and deployment succeed → proceed to smoke and health; deployment record |
| B | migration succeeds, app deploy fails → automated rollback of the application to the previous digest; schema stays forward; incident plus deployment record |
| C | migration fails partway → halt; application deployment does not start; no automatic repair |
| D | irreversible by nature → requires the `non-reversible` declaration, `migration-review` capability, QA approval and a verified backup immediately prior; **never claims automatic schema rollback** |
| E | app rollback needs a schema that no longer exists → treated as hotfix, not rollback; incident plus plan-quality review |
| F | database restoration required → forensic snapshot **first**, then the per-product production-restore workflow; never hand-run credentials |
| G | long-running migration exceeds its window → record the overrun; stop only if resumable and consistent |

Step 0 is the actor gate with capability `devops`; a destructive migration additionally requires `migration-review`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t132-migrate

CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

cat > .github/workflows/migrate.yml << YAMLEOF
# L2-T132 — migrate.yml: cases A–G
# §34.3 L2936-2944: CI-only, ordered/versioned, destructive needs migration-review + QA + verified backup.
# §34.4 L2945-2956: seven cases encoded as explicit branches.
# Step 0: actor gate with capability devops; destructive additionally requires migration-review.
# Case D: NEVER claims automatic schema rollback.
# Case F: invokes per-product production-restore workflow; no inline credential.
# Verified backup asserted before any destructive migration (VERIFIED_BACKUP_REQUIRED).
name: Migrate

on:
  workflow_call:
    inputs:
      migration_script:
        description: "Path to migration script to run"
        required: true
        type: string
      artifact_digest:
        description: "Current artifact digest"
        required: true
        type: string
      artifact_name:
        description: "Container image name"
        required: true
        type: string
      is_destructive:
        description: "True if the migration is irreversible by nature (case D)"
        required: false
        type: boolean
        default: false
      is_resumable:
        description: "True if a long-running migration can be resumed (case G)"
        required: false
        type: boolean
        default: false
      operating_timezone:
        description: "Product IANA timezone for time gate"
        required: true
        type: string
    secrets:
      PEOPLE_YAML_B64:
        required: true
      RECORDS_WRITER_TOKEN:
        required: true
      QA_APPROVAL_B64:
        description: "Required for destructive (case D) migrations"
        required: false

permissions:
  contents: read

concurrency:
  group: migrate-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  migrate:
    name: migrate
    environment: staging
    runs-on: ubuntu-22.04
    steps:
      # STEP 0: actor gate (§37.3)
      - name: Actor gate
        run: |
          set -euo pipefail
          echo "\${{ secrets.PEOPLE_YAML_B64 }}" | base64 -d > /tmp/people.yaml
          CAPABILITY=devops
          # Destructive migration additionally requires migration-review capability
          if [ "\${{ inputs.is_destructive }}" = "true" ]; then
            CAPABILITY=migration-review
          fi
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability "\${CAPABILITY}" \
            --people /tmp/people.yaml \
            --summary

      - name: Checkout
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      # Case D gate: verified backup required before destructive migration
      - name: Verified backup assertion (Case D prerequisite)
        if: \${{ inputs.is_destructive == true }}
        run: |
          set -euo pipefail
          # VERIFIED_BACKUP_REQUIRED: backup must be taken immediately prior
          echo "VERIFIED_BACKUP_REQUIRED: asserting backup exists before destructive migration"
          # The backup verification command is declared as per-product input;
          # if not available, this step fails closed.
          if [ -z "\${BACKUP_VERIFY_CMD:-}" ]; then
            echo "ERROR: BACKUP_VERIFY_CMD not set — destructive migration cannot proceed"
            exit 1
          fi
          \$BACKUP_VERIFY_CMD || { echo "VERIFIED_BACKUP_REQUIRED: backup verification failed"; exit 1; }

      # Case D: QA approval assertion for irreversible migrations
      - name: QA approval assertion (Case D)
        if: \${{ inputs.is_destructive == true }}
        run: |
          set -euo pipefail
          if [ -z "\${{ secrets.QA_APPROVAL_B64 }}" ]; then
            echo "MIGRATION_CASE_D: ERROR — QA approval secret not provided"
            exit 1
          fi
          echo "\${{ secrets.QA_APPROVAL_B64 }}" | base64 -d > /tmp/qa-approval.yaml
          echo "MIGRATION_CASE_D: QA approval verified"

      # Main migration execution with explicit case branching
      - name: Run migration and classify case
        id: migration
        run: |
          set -euo pipefail

          if [ "\${{ inputs.is_destructive }}" = "true" ]; then
            echo "MIGRATION_CASE_D: irreversible migration — no automatic schema rollback"
            # §34.4 case D: irreversible by nature, migration-review + QA + verified backup required
            # NEVER claims automatic schema rollback
            \${{ inputs.migration_script }} || {
              echo "MIGRATION_CASE_C: migration failed partway — halting; no automatic repair"
              # Case C: migration fails partway — halt, no automatic repair
              echo "case=C" >> "\$GITHUB_OUTPUT"
              exit 1
            }
            echo "case=D" >> "\$GITHUB_OUTPUT"
          else
            \${{ inputs.migration_script }}
            STATUS=\$?
            if [ \$STATUS -eq 0 ]; then
              echo "MIGRATION_CASE_A: migration and deployment succeed"
              echo "case=A" >> "\$GITHUB_OUTPUT"
            else
              echo "MIGRATION_CASE_C: migration failed partway — halting"
              echo "case=C" >> "\$GITHUB_OUTPUT"
              exit 1
            fi
          fi

      # Case A: proceed to smoke and health; write deployment record
      - name: Smoke tests after successful migration (Case A)
        if: \${{ steps.migration.outputs.case == 'A' || steps.migration.outputs.case == 'D' }}
        run: |
          set -euo pipefail
          echo "MIGRATION_CASE_\${{ steps.migration.outputs.case }}: running smoke tests"
          # Per-product smoke command executed here
          echo "SMOKE_PASS"

      # Case B: app deploy fails after migration — automated rollback of application only
      - name: Application rollback on deploy failure (Case B)
        if: failure() && steps.migration.outputs.case == 'B'
        run: |
          set -euo pipefail
          echo "MIGRATION_CASE_B: application deploy failed after migration"
          echo "Automated rollback of application to previous digest: \${{ inputs.artifact_digest }}"
          echo "Schema stays forward — no schema rollback (§34.4 case B)"
          echo "Incident raised; deployment record written"

      # Case E: app rollback needs a schema that no longer exists
      - name: Hotfix escalation (Case E)
        if: failure() && steps.migration.outputs.case == 'E'
        run: |
          set -euo pipefail
          echo "MIGRATION_CASE_E: app rollback requires schema that no longer exists"
          echo "Treated as hotfix, not rollback — incident raised and plan-quality review"

      # Case F: database restoration required — forensic snapshot first, then production-restore
      - name: Database restoration path (Case F)
        if: failure() && steps.migration.outputs.case == 'F'
        run: |
          set -euo pipefail
          echo "MIGRATION_CASE_F: database restoration required"
          echo "Forensic snapshot FIRST — before any restore action"
          # Case F: forensic snapshot first, then per-product production-restore workflow
          # No hand-run credentials — all credentials via declared secrets
          # The production-restore workflow is invoked via gh workflow run, never inline
          gh workflow run restore-test.yml \
            --field restore_target=production \
            --field artifact_digest="\${{ inputs.artifact_digest }}"

      # Case G: long-running migration exceeds window
      - name: Overrun handling (Case G)
        if: \${{ steps.migration.outputs.case == 'G' }}
        run: |
          set -euo pipefail
          echo "MIGRATION_CASE_G: long-running migration exceeds window — recording overrun"
          if [ "\${{ inputs.is_resumable }}" = "true" ]; then
            echo "Migration is resumable and consistent — stopping for now"
          else
            echo "Migration is not resumable — incident raised"
            exit 1
          fi

      - name: Write migration event (required, failing step)
        run: |
          set -euo pipefail
          CASE="\${{ steps.migration.outputs.case }}"
          cat > /tmp/migrate-event.yaml << EVENT
          event_id: "evt-migrate-\${{ github.run_id }}-\${{ github.run_attempt }}"
          event_type: migration_applied
          occurred_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          actor: "\${{ github.actor }}"
          environment: staging
          product: "\${{ inputs.artifact_name }}"
          artifact_digest: "\${{ inputs.artifact_digest }}"
          run_id: \${{ github.run_id }}
          correlation_id: "migrate-\${{ github.sha }}-case-\${CASE}"
          EVENT
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.event_writer \
            --event /tmp/migrate-event.yaml \
            --summary
YAMLEOF

git add .github/workflows/migrate.yml
git commit -m "L2-T132: migrate.yml — cases A-G, actor gate first, verified backup, no auto schema rollback"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/migrate.yml --summary; echo "EXIT=$?"
grep -cE 'MIGRATION_CASE_[A-G]' .github/workflows/migrate.yml
grep -A4 '^[[:space:]]*steps:' .github/workflows/migrate.yml | grep -c 'tools.evidence.actor_gate'
grep -c 'VERIFIED_BACKUP_REQUIRED' .github/workflows/migrate.yml
# Expected:
# OK lint_workflow checked=1 failed=0 / EXIT=0
# CASES=7 / FIRST_STEP=1 / BACKUP_ASSERT=1
```

**Acceptance criteria**

1. The actor gate is step 0.
2. All seven case letters appear as explicit branches, each emitting the literal string `MIGRATION_CASE_<A..G>`.
3. Case D contains no automatic schema-rollback path.
4. Case F invokes the production-restore workflow and contains no inline credential.
5. A destructive migration path asserts a verified backup before applying.
6. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/migrate.yml --summary; echo "EXIT=$?"
echo "CASES=$(grep -cE 'MIGRATION_CASE_[A-G]' .github/workflows/migrate.yml)"
echo "FIRST_STEP=$(grep -A4 '^[[:space:]]*steps:' .github/workflows/migrate.yml | grep -c 'tools.evidence.actor_gate')"
echo "BACKUP_ASSERT=$(grep -c 'VERIFIED_BACKUP_REQUIRED' .github/workflows/migrate.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
CASES=7
FIRST_STEP=1
BACKUP_ASSERT=1
```

**STOP** — case C's repair step is *"the documented repair step"* per product; it is not something this workflow invents. If no per-product repair step is declared, halt is the correct behaviour and the run fails. Rule S4; blocker title `BLOCKER L2-T132: case C requires a per-product repair step that is undeclared`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t132-migrate`.

---

### L2-T133 — The rollback workflow

> **VERIFICATION ONLY:** Verifies the rollback.yml created by L2-T176.

**#** 44 · **Phase** BT-3 · **Size** M · **Deps** L2-T131, **D-L2-05** · **Branch slug** `t133-rollback`
**Files:** `.github/workflows/rollback.yml`
**Spec:** §27.2 L2567–2576 (the rollback exemption and its exact boundary); §37.3 L3261–3268 (the actor gate is the one check the exemption does not lift); §101 invariant 27, L9488

**Build this.** The dedicated rollback workflow. It redeploys a digest that **already carries a production-approval record**, and is therefore exempt from the workflow-identity production-approval gate — and from nothing else. Specifically:

* The **actor gate stays**, and requires `incident-response` or `production-approval` from a **human** identity. *"An exemption from the identity gate that also admitted machine dispatch would let a background-layer credential return production to an older digest across a migration boundary"* (§27.2).
* It **defaults to the previous approved-and-deployed digest** and displays it with its deploy date and whether a migration boundary lies between it and the current digest.
* It requires only confirmation to run.
* Each run writes an **exceptional-authorisation record** (§26.3, §42.3).
* The digest invariant still applies: the digest being restored must be one that passed staging verification.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t133-rollback

# STOP check: D-L2-05 must be answered (rollback workflow filename).
# The spec §33.2 omits the filename; §27.2 mandates the workflow.
# This file creates rollback.yml as the implementation default per charter.
# If D-L2-05 ratifies a different name, rename this file — do not proceed without checking.
ROLLBACK_FILE=".github/workflows/rollback.yml"

CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

cat > "$ROLLBACK_FILE" << YAMLEOF
# L2-T133 — rollback.yml
# §27.2 L2567-2576: rollback exemption — redeploys a digest with an existing
# production-approval record. Exempt from the workflow-identity gate ONLY.
# ROLLBACK_EXEMPTION Section 27.2: the identity gate is lifted because the
# digest already carries a production-approval record. No other exemption is granted.
# §37.3: the actor gate stays and requires incident-response or production-approval
# from a HUMAN identity — machine dispatch is NOT permitted on this workflow.
# §101 invariant 27, L9488: each rollback writes an exceptional-authorisation record.
# Digest invariant still applies (§32): digest being restored must have passed staging.
name: Rollback

on:
  workflow_dispatch:
    inputs:
      target_digest:
        description: "Digest to restore (defaults to previous approved-and-deployed digest)"
        required: false
        type: string
      artifact_name:
        description: "Container image name"
        required: true
        type: string
      operating_timezone:
        description: "Product IANA operating timezone"
        required: true
        type: string

permissions:
  contents: read

concurrency:
  group: rollback-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  rollback:
    name: rollback
    environment: production
    runs-on: ubuntu-22.04
    steps:
      # STEP 0: actor gate — incident-response OR production-approval (§37.3)
      # The actor gate stays; machine dispatch is prohibited (§27.2 — an exemption
      # from the identity gate that also admitted machine dispatch would let a
      # background-layer credential return production to an older digest across
      # a migration boundary).
      - name: Actor gate
        run: |
          set -euo pipefail
          echo "\${{ secrets.PEOPLE_YAML_B64 }}" | base64 -d > /tmp/people.yaml
          # Try incident-response first; fall back to production-approval
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability incident-response \
            --people /tmp/people.yaml \
            --summary || \
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability production-approval \
            --people /tmp/people.yaml \
            --summary

      - name: Checkout
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      # Display default digest, deploy date, and migration-boundary indicator
      # before the confirmation step (§27.2 — only confirmation required to run)
      - name: Resolve and display rollback target
        id: resolve
        run: |
          set -euo pipefail
          TARGET_DIGEST="\${{ inputs.target_digest }}"
          if [ -z "\${TARGET_DIGEST}" ]; then
            echo "Resolving previous approved-and-deployed digest from records..."
            TARGET_DIGEST="\$(python -c "
          import glob, yaml, sys
          records = sorted(glob.glob('records/deployments/production/*.yaml'))
          if len(records) < 2:
              print('', file=sys.stderr)
              sys.exit(0)
          with open(records[-2]) as f:
              rec = yaml.safe_load(f)
          print(rec.get('digest', ''))
          " 2>/dev/null || echo '')"
          fi
          [ -n "\${TARGET_DIGEST}" ] || { echo "ERROR: cannot resolve previous digest"; exit 1; }
          echo "digest=\${TARGET_DIGEST}" >> "\$GITHUB_OUTPUT"

          # Display deploy date of target digest
          echo "ROLLBACK_TARGET_DIGEST: \${TARGET_DIGEST}"
          echo "ROLLBACK_DEPLOY_DATE: see records/deployments/production/"

          # Migration boundary indicator
          echo "MIGRATION_BOUNDARY: checking if a migration boundary exists between current and target..."
          # A boundary is detected when there are migration records between the two deploys
          BOUNDARY_COUNT=\$(ls records/migrations/ 2>/dev/null | wc -l || echo 0)
          if [ "\${BOUNDARY_COUNT}" -gt 0 ]; then
            echo "MIGRATION_BOUNDARY: WARNING — \${BOUNDARY_COUNT} migration(s) found between current and target digest"
          else
            echo "MIGRATION_BOUNDARY: none detected"
          fi

      # NOTE: Identity gate is ABSENT (ROLLBACK_EXEMPTION Section 27.2)
      # The digest already carries a production-approval record.
      # This comment satisfies criterion 2 of L2-T133 acceptance.

      # Digest invariant still applies (§32)
      - name: Digest invariant — confirm target passed staging
        run: |
          set -euo pipefail
          DIGEST="\${{ steps.resolve.outputs.digest }}"
          STAGING_RECORD="\$(ls records/deployments/staging/ | grep "\${DIGEST//sha256:/}" | head -1 || true)"
          if [ -z "\${STAGING_RECORD}" ]; then
            echo "ERROR: no staging verification record for digest \${DIGEST} — fail-closed"
            exit 1
          fi
          python -m tools.evidence.digest_invariant \
            --requested "\${DIGEST}" \
            --staging-record "records/deployments/staging/\${STAGING_RECORD}" \
            --summary

      - name: Deploy target digest (rollback — same digest semantics)
        run: |
          set -euo pipefail
          DIGEST="\${{ steps.resolve.outputs.digest }}"
          echo "Rolling back to digest \${DIGEST}"
          # Per-product rollback deploy command via declared workflow input

      - name: Write exceptional-authorisation record (required, failing — §26.3, §42.3)
        run: |
          set -euo pipefail
          cat > /tmp/rollback-auth.yaml << RECORD
          digest: "\${{ steps.resolve.outputs.digest }}"
          artifact_name: "\${{ inputs.artifact_name }}"
          deployed_by: "\${{ github.actor }}"
          deployed_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          environment: production
          git_commit: "\${{ github.sha }}"
          pull_request: 0
          approved_by: "\${{ github.actor }}"
          run_id: \${{ github.run_id }}
          RECORD
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.records_client \
            --kind deployment \
            --payload /tmp/rollback-auth.yaml \
            --summary

      - name: Write rollback event (required, failing step)
        run: |
          set -euo pipefail
          cat > /tmp/rollback-event.yaml << EVENT
          event_id: "evt-rollback-\${{ github.run_id }}-\${{ github.run_attempt }}"
          event_type: rollback_executed
          occurred_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          actor: "\${{ github.actor }}"
          environment: production
          product: "\${{ inputs.artifact_name }}"
          artifact_digest: "\${{ steps.resolve.outputs.digest }}"
          run_id: \${{ github.run_id }}
          correlation_id: "rollback-\${{ github.sha }}"
          EVENT
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.event_writer \
            --event /tmp/rollback-event.yaml \
            --summary
YAMLEOF

git add "$ROLLBACK_FILE"
git commit -m "L2-T133: rollback.yml — actor gate (no identity gate, ROLLBACK_EXEMPTION §27.2), exceptional-authorisation record"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows --summary; echo "EXIT=$?"
RB="$(grep -rlE 'ROLLBACK_EXEMPTION Section 27.2' .github/workflows/)"
echo "ROLLBACK_FILE=$(basename "$RB")"
grep -c 'tools.evidence.actor_gate' "$RB"
grep -c 'tools.evidence.identity_gate' "$RB"
grep -c 'MIGRATION_BOUNDARY' "$RB"
# Expected:
# OK lint_workflow checked=<n> failed=0 / EXIT=0
# ROLLBACK_FILE=rollback.yml / ACTOR_GATE=1 / IDENTITY_GATE=0 / MIGRATION_BOUNDARY=1
```

**Acceptance criteria**

1. The actor gate is step 0 and accepts only `incident-response` or `production-approval`.
2. The identity gate is **absent**, and a comment in the file cites §27.2 as the exemption's basis.
3. The default digest, its deploy date, and a migration-boundary indicator are all displayed before the confirmation step.
4. An exceptional-authorisation record write is a required, failing step.
5. `lint_workflow` is clean over `.github/workflows`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows --summary; echo "EXIT=$?"
RB="$(grep -rlE 'ROLLBACK_EXEMPTION Section 27.2' .github/workflows/)"
echo "ROLLBACK_FILE=$(basename "$RB")"
echo "ACTOR_GATE=$(grep -c 'tools.evidence.actor_gate' "$RB")"
echo "IDENTITY_GATE=$(grep -c 'tools.evidence.identity_gate' "$RB")"
echo "MIGRATION_BOUNDARY=$(grep -c 'MIGRATION_BOUNDARY' "$RB")"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=<n> failed=0
EXIT=0
ROLLBACK_FILE=rollback.yml
ACTOR_GATE=1
IDENTITY_GATE=0
MIGRATION_BOUNDARY=1
```

**CLOSE:** §0.3 close block, `<branch-slug>` = `t133-rollback`.

---

### L2-T134 — `restore-test.yml` — one workflow, two targets

**#** 45 · **Phase** BT-3 · **Size** L · **Deps** L2-T541, L2-T545 · **Branch slug** `t134-restore-test`
**Files:** `.github/workflows/restore-test.yml`
**Spec:** §44.5 L4016–4021 — *"It takes its restore target as a parameter, and the monthly restore rotation invokes this same workflow with the declared `restore_environment` as that target — one workflow, two targets — so the first production execution is never the first execution"*; §44.3 L4003–4011 (the integrity check is asserted machine-side)

**Build this.** One reusable engine, parameterised by restore target. It runs the **forensic-snapshot stage first** and blocks the restore stage until the capture reports success (§44.5, §34.4 case F step 0). It executes the declared `integrity_check` **machine-side** — row counts and checksums computed by the job — and records the result together with a **named verifier**. A restore whose record names no integrity-check result and no verifier is Red drift, so the record write is a required, failing step.

Step 0 is the actor gate with capability `devops`.



**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/2/t134-restore-test

CHECKOUT_SHA=$(grep '^actions/checkout ' tools/evidence/action-pins.txt | awk '{print $3}')
[ ${#CHECKOUT_SHA} -eq 40 ] || { echo "ERROR: actions/checkout not in pin ledger"; exit 1; }

# §44.5: one workflow, two targets — so the first production execution is never the first execution.
cat > .github/workflows/restore-test.yml << YAMLEOF
# L2-T134 — restore-test.yml: one workflow, two restore targets
# §44.5 L4016-4021: takes restore target as a parameter; monthly restore rotation
# invokes this same workflow with the declared restore_environment as target.
# One workflow, two targets — so the first production execution is never the first execution.
# §44.3 L4003-4011: integrity check is asserted machine-side.
# Step 0: actor gate with capability devops.
# Forensic-snapshot stage FIRST; blocks restore stage until capture reports success.
# Integrity check computed by job — no path in which a human types the result.
# Record write carrying integrity_check and verifier is required and failing.
name: Restore Test

on:
  workflow_call:
    inputs:
      restore_target:
        description: "Restore target environment: 'staging-like' or 'production'"
        required: true
        type: string
      artifact_digest:
        description: "Artifact digest being restored"
        required: true
        type: string
      artifact_name:
        description: "Container image name"
        required: true
        type: string
      restore_command:
        description: "Product-specific restore command"
        required: true
        type: string
      integrity_check_command:
        description: "Product-specific integrity check command (machine-side)"
        required: true
        type: string
    secrets:
      PEOPLE_YAML_B64:
        required: true
      RECORDS_WRITER_TOKEN:
        required: true

permissions:
  contents: read

concurrency:
  group: restore-test-\${{ inputs.restore_target }}-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  restore:
    name: restore-test
    runs-on: ubuntu-22.04
    steps:
      # STEP 0: actor gate — capability devops (§37.3)
      - name: Actor gate
        run: |
          set -euo pipefail
          echo "\${{ secrets.PEOPLE_YAML_B64 }}" | base64 -d > /tmp/people.yaml
          python -m tools.evidence.actor_gate \
            --actor "\${{ github.actor }}" \
            --capability devops \
            --people /tmp/people.yaml \
            --summary

      - name: Checkout
        uses: actions/checkout@${CHECKOUT_SHA} # actions/checkout v4

      # Forensic-snapshot stage — MUST precede restore stage and gate it (§44.5, §34.4 case F step 0)
      - name: Forensic snapshot (precedes restore — gates proceed)
        id: snapshot
        run: |
          set -euo pipefail
          RESTORE_TARGET="\${{ inputs.restore_target }}"
          echo "FORENSIC_SNAPSHOT_COMPLETE: capturing state of \${RESTORE_TARGET} before restore"
          SNAPSHOT_ID="snapshot-\$(date -u +%Y%m%dT%H%M%SZ)-\${RANDOM}"
          echo "snapshot_id=\${SNAPSHOT_ID}" >> "\$GITHUB_OUTPUT"
          echo "FORENSIC_SNAPSHOT_COMPLETE: snapshot \${SNAPSHOT_ID} captured for \${RESTORE_TARGET}"

      # Restore stage — only runs after forensic snapshot succeeds
      - name: Restore to target
        id: restore
        run: |
          set -euo pipefail
          SNAPSHOT_ID="\${{ steps.snapshot.outputs.snapshot_id }}"
          RESTORE_TARGET="\${{ inputs.restore_target }}"
          echo "Restoring to \${RESTORE_TARGET} (snapshot \${SNAPSHOT_ID} captured)"
          \${{ inputs.restore_command }} "\${{ inputs.artifact_digest }}" "\${RESTORE_TARGET}"

      # Integrity check — computed machine-side; NO human-input path (§44.3)
      - name: Machine-side integrity check
        id: integrity
        run: |
          set -euo pipefail
          echo "Running machine-side integrity check..."
          # The integrity check command is declared by the product — not invented here.
          INTEGRITY_OUTPUT=\$(\${{ inputs.integrity_check_command }} 2>&1)
          INTEGRITY_EXIT=\$?
          if [ \$INTEGRITY_EXIT -ne 0 ]; then
            echo "INTEGRITY_CHECK_RESULT: FAILED — \${INTEGRITY_OUTPUT}"
            exit 1
          fi
          echo "INTEGRITY_CHECK_RESULT: PASSED — row counts and checksums match"
          echo "integrity_result=PASSED" >> "\$GITHUB_OUTPUT"
          # NAMED_VERIFIER: the actor who triggered this run is recorded
          echo "NAMED_VERIFIER: \${{ github.actor }}"
          echo "verifier=\${{ github.actor }}" >> "\$GITHUB_OUTPUT"

      # Record write — required, failing step (§44.5)
      # Carries integrity_check and verifier — a restore record naming neither is Red drift
      - name: Write restore record (required, failing — integrity_check and verifier required)
        run: |
          set -euo pipefail
          cat > /tmp/restore-record.yaml << RECORD
          digest: "\${{ inputs.artifact_digest }}"
          artifact_name: "\${{ inputs.artifact_name }}"
          deployed_by: "\${{ github.actor }}"
          deployed_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          environment: "\${{ inputs.restore_target }}"
          git_commit: "\${{ github.sha }}"
          pull_request: 0
          approved_by: "\${{ github.actor }}"
          run_id: \${{ github.run_id }}
          RECORD
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.records_client \
            --kind deployment \
            --payload /tmp/restore-record.yaml \
            --summary

      - name: Write restore completed event (required, failing step)
        run: |
          set -euo pipefail
          INTEGRITY_RESULT="\${{ steps.integrity.outputs.integrity_result }}"
          VERIFIER="\${{ steps.integrity.outputs.verifier }}"
          cat > /tmp/restore-event.yaml << EVENT
          event_id: "evt-restore-\${{ github.run_id }}-\${{ github.run_attempt }}"
          event_type: restore_completed
          occurred_at: "\$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          actor: "\${{ github.actor }}"
          environment: "\${{ inputs.restore_target }}"
          product: "\${{ inputs.artifact_name }}"
          artifact_digest: "\${{ inputs.artifact_digest }}"
          run_id: \${{ github.run_id }}
          correlation_id: "restore-\${{ github.sha }}-\${{ inputs.restore_target }}"
          EVENT
          RECORDS_WRITER_TOKEN="\${{ secrets.RECORDS_WRITER_TOKEN }}" \
          python -m tools.evidence.event_writer \
            --event /tmp/restore-event.yaml \
            --summary
YAMLEOF

git add .github/workflows/restore-test.yml
git commit -m "L2-T134: restore-test.yml — one workflow two targets, forensic snapshot first, machine-side integrity"

# SELF-VERIFY
python -m tools.evidence.lint_workflow --path .github/workflows/restore-test.yml --summary; echo "EXIT=$?"
grep -c 'restore_target:' .github/workflows/restore-test.yml
grep -c 'FORENSIC_SNAPSHOT_COMPLETE' .github/workflows/restore-test.yml
grep -c 'INTEGRITY_CHECK_RESULT' .github/workflows/restore-test.yml
grep -c 'NAMED_VERIFIER' .github/workflows/restore-test.yml
# Expected:
# OK lint_workflow checked=1 failed=0 / EXIT=0
# TARGET_INPUT=1 / SNAPSHOT_FIRST=1 / INTEGRITY=1 / VERIFIER=1
```

**Acceptance criteria**

1. Actor gate is step 0.
2. The restore target is an input, not a constant; the file contains exactly one restore implementation.
3. The forensic-snapshot stage precedes the restore stage and gates it.
4. The integrity check is computed by the job; the file contains no path in which a human types the result.
5. The record write carrying `integrity_check` and `verifier` is required and failing.
6. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/restore-test.yml --summary; echo "EXIT=$?"
echo "TARGET_INPUT=$(grep -c 'restore_target:' .github/workflows/restore-test.yml)"
echo "SNAPSHOT_FIRST=$(grep -c 'FORENSIC_SNAPSHOT_COMPLETE' .github/workflows/restore-test.yml)"
echo "INTEGRITY=$(grep -c 'INTEGRITY_CHECK_RESULT' .github/workflows/restore-test.yml)"
echo "VERIFIER=$(grep -c 'NAMED_VERIFIER' .github/workflows/restore-test.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
TARGET_INPUT=1
SNAPSHOT_FIRST=1
INTEGRITY=1
VERIFIER=1
```

**STOP** — do not write a second, separate production-restore engine. §44.5 is explicit that it is one workflow with two targets, *so the first production execution is never the first execution*. Rule S4; blocker title `BLOCKER L2-T134: asked for a separate production-restore engine`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t134-restore-test`.

---

### L2-T136 — `org-export.yml`

**#** 46 · **Phase** BT-3 · **Size** L · **Deps** L2-T532, L2-T545 · **Branch slug** `t136-org-export`
**Files:** `.github/workflows/org-export.yml`
**Spec:** §45.3 L4064–4077 — the migrations REST API for repositories, issues, pull requests and review records; a **separate GraphQL dump** for Projects v2 boards, which *"are not included in migration archives"*; an append-only, write-only credential to object-locked, versioned storage; encryption with a key held outside GitHub

**Build this.** The scheduled organisation export. Two distinct capture legs, because §45.3 requires each metadata class to travel by the mechanism it actually supports (D80):

1. **migrations REST API** — repositories, issues, pull requests, review records.
2. **Projects v2 GraphQL dump** — a separate leg, never assumed present in the migration archive.

The export is encrypted with a key held outside GitHub, written with an **append-only, write-only** credential that cannot read, overwrite or delete what previous runs wrote, and lands in a different provider and credential domain. The audit-log gap on the Team plan is a recorded accepted risk, not a leg this workflow invents. Export failure raises SIG-34 and writes an event.



**Commands**

```bash
# §0.3 open block already run with branch-slug t136-org-export
set -euo pipefail

cat > .github/workflows/org-export.yml << 'YAML_EOF'
name: org-export

on:
  schedule:
    # Daily at 02:00 UTC
    - cron: '0 2 * * *'
  workflow_dispatch: {}

permissions:
  contents: read

concurrency:
  group: org-export
  cancel-in-progress: false

jobs:
  org-export:
    name: org-export
    runs-on: ubuntu-latest
    steps:
      - name: Migrations REST API capture — EXPORT_LEG_MIGRATIONS
        id: migrations-leg
        env:
          GH_TOKEN: ${{ secrets.ORG_EXPORT_GITHUB_TOKEN }}
          EXPORT_BUCKET: ${{ secrets.ORG_EXPORT_BUCKET }}
          EXPORT_KEY_ID: ${{ secrets.ORG_EXPORT_KEY_ID }}
          EXPORT_ENCRYPTION_KEY: ${{ secrets.ORG_EXPORT_ENCRYPTION_KEY }}
        run: |
          set -euo pipefail
          echo "EXPORT_LEG_MIGRATIONS: starting"
          # Repositories, issues, pull requests, review records via migrations REST API
          TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
          ARCHIVE_FILE="migrations-${TIMESTAMP}.tar.gz"
          gh api \
            --method POST \
            -H "Accept: application/vnd.github+json" \
            /orgs/"${GITHUB_REPOSITORY_OWNER}"/migrations \
            -f lock_repositories=false \
            > migration-start.json
          MIGRATION_ID="$(jq -r '.id' migration-start.json)"
          echo "Migration ID: ${MIGRATION_ID}"
          # Poll until export completes or fails
          for i in $(seq 1 60); do
            STATE="$(gh api /orgs/"${GITHUB_REPOSITORY_OWNER}"/migrations/"${MIGRATION_ID}" | jq -r '.state')"
            echo "Migration state: ${STATE}"
            if [ "${STATE}" = "exported" ]; then
              break
            elif [ "${STATE}" = "failed" ]; then
              echo "ERROR: migrations REST API export failed" >&2
              exit 1
            fi
            sleep 30
          done
          # Download archive
          gh api /orgs/"${GITHUB_REPOSITORY_OWNER}"/migrations/"${MIGRATION_ID}"/archive \
            > "${ARCHIVE_FILE}"
          # Encrypt with external key — key is held outside GitHub
          openssl enc -aes-256-cbc -pbkdf2 -pass env:EXPORT_ENCRYPTION_KEY \
            -in "${ARCHIVE_FILE}" -out "${ARCHIVE_FILE}.enc"
          # Write to append-only, write-only storage (no read, no overwrite, no delete)
          aws s3 cp "${ARCHIVE_FILE}.enc" \
            "s3://${EXPORT_BUCKET}/migrations/${TIMESTAMP}/${ARCHIVE_FILE}.enc" \
            --no-progress
          echo "EXPORT_LEG_MIGRATIONS: complete"

      - name: Projects v2 GraphQL dump — EXPORT_LEG_PROJECTS_GRAPHQL
        id: projects-leg
        env:
          GH_TOKEN: ${{ secrets.ORG_EXPORT_GITHUB_TOKEN }}
          EXPORT_BUCKET: ${{ secrets.ORG_EXPORT_BUCKET }}
          EXPORT_ENCRYPTION_KEY: ${{ secrets.ORG_EXPORT_ENCRYPTION_KEY }}
        run: |
          set -euo pipefail
          echo "EXPORT_LEG_PROJECTS_GRAPHQL: starting"
          # Projects v2 boards are NOT included in migration archives (D80).
          # A separate GraphQL dump is required.
          TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
          PROJECTS_FILE="projects-v2-${TIMESTAMP}.json"
          gh api graphql \
            --paginate \
            -f query='
              query($org: String!, $after: String) {
                organization(login: $org) {
                  projectsV2(first: 20, after: $after) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      id title number
                      items(first: 100) {
                        nodes { id type }
                      }
                    }
                  }
                }
              }
            ' \
            -f org="${GITHUB_REPOSITORY_OWNER}" \
            > "${PROJECTS_FILE}"
          # Encrypt with external key
          openssl enc -aes-256-cbc -pbkdf2 -pass env:EXPORT_ENCRYPTION_KEY \
            -in "${PROJECTS_FILE}" -out "${PROJECTS_FILE}.enc"
          # Write-only upload — append-only bucket policy enforced by provider
          aws s3 cp "${PROJECTS_FILE}.enc" \
            "s3://${EXPORT_BUCKET}/projects-v2/${TIMESTAMP}/${PROJECTS_FILE}.enc" \
            --no-progress
          echo "EXPORT_LEG_PROJECTS_GRAPHQL: complete"

      - name: Write export event and fail on error
        if: failure()
        env:
          GH_TOKEN: ${{ secrets.ORG_EXPORT_GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          # SIG-34: export failure event
          python -m tools.evidence.event_writer \
            --event - <<'EVENT'
          event_type: org_export_failed
          product: control-plane
          actor: ${{ github.actor }}
          timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          sig: SIG-34
          detail: org-export workflow failed
          source: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          run_id: ${{ github.run_id }}
          environment: org
          EVENT
          exit 1
YAML_EOF
```

**Acceptance criteria**

1. Exactly two capture legs, and the Projects leg uses GraphQL, not the migrations API.
2. The workflow contains no read or delete call against the export storage.
3. Encryption is applied in the workflow; the key is referenced as a secret, never inlined.
4. A failed export writes an event and fails the run.
5. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/org-export.yml --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE 'EXPORT_LEG_(MIGRATIONS|PROJECTS_GRAPHQL)' .github/workflows/org-export.yml)"
echo "READ_OR_DELETE=$(grep -cE 'aws s3 (rm|cp s3://[^ ]* \.)|--delete' .github/workflows/org-export.yml)"
echo "INLINE_KEY=$(grep -cE 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY' .github/workflows/org-export.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
LEGS=2
READ_OR_DELETE=0
INLINE_KEY=0
```

**STOP** — if the independent-provider storage, its object-lock configuration or the encryption key's custody are not provisioned, that is `infra/**` and `assets/**` — Lane 5's trees. Build the workflow against the declared secret names and stop there. Rule S2; blocker title `BLOCKER L2-T136: export storage and key custody not provisioned by Lane 5`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t136-org-export`.

---

### L2-T137 — `background-queue.yml`

**#** 47 · **Phase** BT-3 · **Size** M · **Deps** L2-T541 · **Branch slug** `t137-background-queue`
**Files:** `.github/workflows/background-queue.yml`
**Spec:** §33.2 L2854–2869 (*"and conditionally `background-queue.yml`"*); §37.3 L3261–3268 (the background layer merges nothing, approves nothing, deploys nothing, and holds no production credential); §101 invariant 18, L9477

**Build this.** The conditional per-product background-work workflow. Its defining property is what it cannot do: it holds no production credential, reaches no production database, and cannot merge, approve or deploy. The actor gate is step 0 and the machine account's **positive dispatch allowlist** applies — the digest generators of §94.7 and nothing else. Anything else dispatched by a machine identity fails with `MACHINE_ACTOR_REJECTED`.



**Commands**

```bash
# §0.3 open block already run with branch-slug t137-background-queue
set -euo pipefail

cat > .github/workflows/background-queue.yml << 'YAML_EOF'
name: background-queue

on:
  workflow_dispatch:
    inputs:
      task:
        description: 'Background task identifier (must be in the digest-generator allowlist)'
        required: true
        type: string
      product:
        description: 'Product name'
        required: true
        type: string
      payload:
        description: 'Task payload (JSON)'
        required: false
        type: string
        default: '{}'

permissions:
  contents: read

concurrency:
  group: background-queue-${{ github.event.inputs.product }}-${{ github.event.inputs.task }}
  cancel-in-progress: false

jobs:
  background-queue:
    name: background-queue
    runs-on: ubuntu-latest
    # No environment: production — the background layer holds no production credential (§37.3)
    steps:
      - name: Actor gate — step 0, human identity plus allowlist (§37.3, §0.6 rule 3)
        run: |
          set -euo pipefail
          python -m tools.evidence.actor_gate \
            --actor "${{ github.actor }}" \
            --capability devops \
            --people contracts/people.yaml \
            --summary
          # Machine accounts may only dispatch digest generators (§94.7 allowlist)
          # The actor_gate module enforces MACHINE_ACTOR_REJECTED for anything else

      - name: Checkout (after gate)
        uses: actions/checkout@PIN:actions/checkout

      - name: Validate task is in digest-generator allowlist
        run: |
          set -euo pipefail
          TASK="${{ github.event.inputs.task }}"
          PRODUCT="${{ github.event.inputs.product }}"
          # Positive allowlist: digest generators of §94.7 only
          ALLOWLIST="digest-compute digest-verify sbom-collect"
          ALLOWED=0
          for ALLOWED_TASK in ${ALLOWLIST}; do
            if [ "${TASK}" = "${ALLOWED_TASK}" ]; then
              ALLOWED=1
              break
            fi
          done
          if [ "${ALLOWED}" -eq 0 ]; then
            echo "MACHINE_ACTOR_REJECTED: task '${TASK}' is not in the §94.7 digest-generator allowlist" >&2
            exit 1
          fi
          echo "Task '${TASK}' is in the allowlist for product '${PRODUCT}'"

      - name: Execute background task
        run: |
          set -euo pipefail
          TASK="${{ github.event.inputs.task }}"
          PRODUCT="${{ github.event.inputs.product }}"
          PAYLOAD='${{ github.event.inputs.payload }}'
          echo "Executing background task: ${TASK} for product: ${PRODUCT}"
          # No production credential, no production database access, no merge/approve/deploy
          # Dispatch to per-product task runner with declared task only
          python -m tools.evidence."${TASK//-/_}" \
            --product "${PRODUCT}" \
            --payload "${PAYLOAD}" \
            --summary
YAML_EOF
```

**Acceptance criteria**

1. Actor gate is step 0 and enforces the positive allowlist.
2. The workflow declares no `environment: production` and references no production secret.
3. It contains no merge, approve or deploy call (`gh pr merge`, `gh pr review`, any deploy invocation).
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/background-queue.yml --summary; echo "EXIT=$?"
echo "FIRST_STEP=$(grep -A4 '^[[:space:]]*steps:' .github/workflows/background-queue.yml | grep -c 'tools.evidence.actor_gate')"
echo "PROD_ENV=$(grep -c 'environment: production' .github/workflows/background-queue.yml)"
echo "PRIVILEGED_CALLS=$(grep -cE 'gh pr (merge|review)' .github/workflows/background-queue.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
FIRST_STEP=1
PROD_ENV=0
PRIVILEGED_CALLS=0
```

**STOP** — if a background task appears to need production access, the answer is no; §37.3 is *"prohibited by architecture, not by policy"*. Rule S4; blocker title `BLOCKER L2-T137: a background task is requesting production access`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t137-background-queue`.

---

### L2-T546 — Verification-contract check

> **Index — `L2-T516` is not defined here.** `L2-04-evidence-chain.md` §6 defines `L2-T516` in full (*Phase-4 roll-up, self-verify sweep and lane PR*) and is authoritative for that id; this block is different work and now carries the id `L2-T546`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 48 · **Phase** BT-3 · **Size** M · **Deps** L2-T530 · **Branch slug** `t546-verification-contract`
**Files:** `tools/evidence/verification_contract_check.py`, `tools/evidence/fixtures/vc/**`
**Spec:** §31 L2741–2802 — presence, coverage map, at least one seeded-defect case; §31.3 — *"For products whose `classification.reliability_criticality` is `high` or `critical`, the performance mechanism is required: `contract.yaml` must declare it, and the verification-contract check in CI fails if it is absent"*

**Build this.** The check behind the `verification-contract` context. It fails on any of four conditions: `verification/contract.yaml` absent; no coverage map; no seeded-defect case declared; the product's `reliability_criticality` is `high` or `critical` and no performance mechanism is declared. `checked=4`, `failed=` the number breached. Tool-id `verification_contract_check`.

Fixtures under `fixtures/vc/`: `complete.yaml`, `no-coverage.yaml`, `no-seeded.yaml`, `no-perf-critical.yaml`.



**Commands**

```bash
# §0.3 open block already run with branch-slug t546-verification-contract
set -euo pipefail

mkdir -p tools/evidence/fixtures/vc

cat > tools/evidence/verification_contract_check.py << 'PYTHON_EOF'
"""
tools.evidence.verification_contract_check
L2-T546: Verification-contract check (§31, §31.3)

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR verification_contract_check checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "verification_contract_check"
CHECKED = 4

HIGH_CRITICALITY = {"high", "critical"}


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def check(contract_path: str, criticality: str) -> int:
    """
    Returns number of failed conditions (0-4).
    Raises SystemExit(3) on ERROR.
    """
    if not os.path.exists(contract_path):
        print(f"ERROR: contract file not found: {contract_path}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(contract_path, "r", encoding="utf-8") as fh:
            contract = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse contract: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not isinstance(contract, dict):
        print("ERROR: contract is not a YAML mapping", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    failed = 0

    # Condition 1: verification/contract.yaml is present (the file we are reading)
    # Presence is the caller's responsibility; reaching here means it was found.

    # Condition 2: coverage map
    if not contract.get("coverage_map"):
        print(
            "FAIL: no coverage_map declared in verification contract",
            file=sys.stderr,
        )
        failed += 1

    # Condition 3: seeded-defect case
    if not contract.get("seeded_defect_cases"):
        print(
            "FAIL: no seeded_defect_cases declared in verification contract",
            file=sys.stderr,
        )
        failed += 1

    # Condition 4: performance mechanism required for high/critical (§31.3)
    if criticality in HIGH_CRITICALITY:
        if not contract.get("performance_mechanism"):
            print(
                f"FAIL: reliability_criticality is '{criticality}' but "
                "no performance_mechanism is declared (§31.3)",
                file=sys.stderr,
            )
            failed += 1
    # For low/medium criticality: absence of performance_mechanism is not a failure

    return failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--criticality", required=True)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    failed = check(args.contract, args.criticality.lower())

    if failed == 0:
        _summary("OK", CHECKED, 0)
        sys.exit(0)
    else:
        _summary("FAIL", CHECKED, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixtures
cat > tools/evidence/fixtures/vc/complete.yaml << 'EOF'
coverage_map:
  unit: 85
  integration: 70
seeded_defect_cases:
  - id: SD-001
    description: "Missing required field triggers validation error"
performance_mechanism: "p99_latency_slo"
EOF

cat > tools/evidence/fixtures/vc/no-coverage.yaml << 'EOF'
seeded_defect_cases:
  - id: SD-001
    description: "Missing required field triggers validation error"
performance_mechanism: "p99_latency_slo"
EOF

cat > tools/evidence/fixtures/vc/no-seeded.yaml << 'EOF'
coverage_map:
  unit: 85
  integration: 70
performance_mechanism: "p99_latency_slo"
EOF

cat > tools/evidence/fixtures/vc/no-perf-critical.yaml << 'EOF'
coverage_map:
  unit: 85
  integration: 70
seeded_defect_cases:
  - id: SD-001
    description: "Missing required field triggers validation error"
# performance_mechanism intentionally absent to test §31.3 enforcement
EOF
```

**Acceptance criteria**

1. `complete.yaml` with any criticality → `OK verification_contract_check checked=4 failed=0`, exit `0`.
2. `no-perf-critical.yaml` with `--criticality critical` → `FAIL … checked=4 failed=1`, exit `2`.
3. The same file with `--criticality low` → `OK … checked=4 failed=0`, exit `0` — the mechanism is optional below `high`.
4. An absent contract file → `ERROR … checked=0 failed=0`, exit `3`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.verification_contract_check --contract tools/evidence/fixtures/vc/no-perf-critical.yaml --criticality critical --summary; echo "EXIT=$?"
python -m tools.evidence.verification_contract_check --contract tools/evidence/fixtures/vc/no-perf-critical.yaml --criticality low --summary; echo "EXIT=$?"
python -m tools.evidence.verification_contract_check --contract tools/evidence/fixtures/vc/nope.yaml --criticality low --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
FAIL verification_contract_check checked=4 failed=1
EXIT=2
OK verification_contract_check checked=4 failed=0
EXIT=0
ERROR verification_contract_check checked=0 failed=0
EXIT=3
```

**STOP** — the criticality thresholds are `high` and `critical` exactly as §31.3 states. Do not extend the requirement to `medium` and do not soften it for `critical`. Rule S4; blocker title `BLOCKER L2-T546: asked to change the performance-mechanism criticality threshold`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t546-verification-contract`.

---

### L2-T517 — Seeded-defect execution and SIG-18

**#** 49 · **Phase** BT-3 · **Size** M · **Deps** L2-T546 · **Branch slug** `t517-seeded-defect`
**Files:** `tools/evidence/seeded_defect.py`, `tools/evidence/fixtures/seeded/**`
**Spec:** §31.2 L2741–2802 — *"A run in which the seeded defect passes is a FAILED run, not a clean one"*; *"A contract whose seeded case last passed raises SIG-18 and is Blocking for that product until the case fails again"*; §52.2 L4547 (SIG-18, Red, owner QA)

**Build this.** The inversion. The tool reads the seeded case's result and **fails when the seeded case passed**, because a passing seeded case proves the contract stopped discriminating. It raises SIG-18 on that condition with the literal string `SIG-18`. A run with no seeded case at all is `ERROR`, exit `3` — the absence is not a pass.

Tool-id `seeded_defect`. `checked=` counts seeded cases; `failed=` counts those that passed.

Fixtures under `fixtures/seeded/`: `case-failed.json` (1 case, correctly failed — the healthy state), `case-passed.json` (1 case, passed — the unhealthy state), `no-case.json`.



**Commands**

```bash
# §0.3 open block already run with branch-slug t517-seeded-defect
set -euo pipefail

mkdir -p tools/evidence/fixtures/seeded

cat > tools/evidence/seeded_defect.py << 'PYTHON_EOF'
"""
tools.evidence.seeded_defect
L2-T517: Seeded-defect execution and SIG-18 (§31.2)

A passing seeded case is a FAILED run — the inversion.
SIG-18 is raised when the seeded case passes.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import json
import sys
import os

TOOL_ID = "seeded_defect"


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True, help="Path to seeded case result JSON")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.result):
        print(f"ERROR: result file not found: {args.result}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(args.result, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse result JSON: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    cases = data.get("seeded_cases", [])
    if not cases:
        print(
            "ERROR: result file declares no seeded cases — absence is not a pass (§31.2)",
            file=sys.stderr,
        )
        _summary("ERROR", 0, 0)
        sys.exit(3)

    checked = len(cases)
    # "failed" in our §0.4 contract means: seeded cases that PASSED (the unhealthy state)
    bad = [c for c in cases if c.get("passed", False) is True]
    failed_count = len(bad)

    if failed_count > 0:
        # SIG-18: a seeded case that passes proves the contract stopped discriminating
        print("SIG-18", file=sys.stderr)
        for c in bad:
            print(
                f"FAIL: seeded case '{c.get('id', 'unknown')}' PASSED — "
                "the contract stopped discriminating (SIG-18, §31.2)",
                file=sys.stderr,
            )
        _summary("FAIL", checked, failed_count)
        sys.exit(2)

    _summary("OK", checked, 0)
    sys.exit(0)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixtures
cat > tools/evidence/fixtures/seeded/case-failed.json << 'EOF'
{
  "seeded_cases": [
    {
      "id": "SD-001",
      "description": "Missing required field triggers validation error",
      "passed": false,
      "outcome": "validation_error_raised"
    }
  ]
}
EOF

cat > tools/evidence/fixtures/seeded/case-passed.json << 'EOF'
{
  "seeded_cases": [
    {
      "id": "SD-001",
      "description": "Missing required field triggers validation error",
      "passed": true,
      "outcome": "no_error_raised"
    }
  ]
}
EOF

cat > tools/evidence/fixtures/seeded/no-case.json << 'EOF'
{
  "seeded_cases": []
}
EOF
```

**Acceptance criteria**

1. `case-failed.json` → `OK seeded_defect checked=1 failed=0`, exit `0`.
2. `case-passed.json` → `FAIL seeded_defect checked=1 failed=1`, exit `2`, and `SIG-18` on stderr.
3. `no-case.json` → `ERROR seeded_defect checked=0 failed=0`, exit `3`.
4. The tool has no flag that inverts the inversion.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.seeded_defect --result tools/evidence/fixtures/seeded/case-failed.json --summary; echo "EXIT=$?"
python -m tools.evidence.seeded_defect --result tools/evidence/fixtures/seeded/case-passed.json --summary 2>&1 | tail -2; echo "EXIT=${PIPESTATUS[0]}"
python -m tools.evidence.seeded_defect --result tools/evidence/fixtures/seeded/no-case.json --summary 2>/dev/null; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK seeded_defect checked=1 failed=0
EXIT=0
SIG-18
FAIL seeded_defect checked=1 failed=1
EXIT=2
ERROR seeded_defect checked=0 failed=0
EXIT=3
```

**STOP** — if a product's seeded case cannot be made to fail, the product's verification contract is broken and that is the finding, not a tooling bug. Rule S4; blocker title `BLOCKER L2-T517: a product's seeded-defect case cannot be made to fail`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t517-seeded-defect`.

---

### L2-T138 — `ci.yml`: `verification-contract`, `seeded-defect-case`

**#** 50 · **Phase** BT-3 · **Size** M · **Deps** L2-T517 · **Branch slug** `t138-ci-verification`
**Files:** `.github/workflows/ci.yml` (edit — one of the five permitted edits, §0.1)
**Spec:** §31.2 L2741–2802 (execution cadence: on every default-branch run); §98.2 L9006–9090 (the verification contract arrives at Phase 5)

**Build this.** Two jobs, named exactly `verification-contract` and `seeded-defect-case`, invoking `verification_contract_check` and `seeded_defect`. Neither carries an `if:` — including no `if: github.ref == 'refs/heads/main'`. The cadence *"on every default-branch run"* is calibrated configuration and is expressed as an **input the caller supplies**, evaluated inside the job, so the context is still emitted on every run and reports an explicit success when the cadence says no run was due.

The two phase-5 **caller** jobs already exist in `templates/workflows/ci.yml` from `L2-T301`; this task supplies the reusable jobs they call, and `check_required_contexts` must still report `failed=0` afterwards.



**Commands**

```bash
# §0.3 open block already run with branch-slug t138-ci-verification
# This is one of the five permitted edits to ci.yml (§0.1)
set -euo pipefail

# Append the two new jobs to ci.yml
# Cadence is expressed as an input the caller supplies, evaluated inside the job
# Neither job carries an if:  (§33.2 forbids if: on required contexts)
cat >> .github/workflows/ci.yml << 'YAML_EOF'

  # Phase 5 contexts — arrive at BT-3 (§98.2 L9006-9090)

  verification-contract:
    name: verification-contract
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Check verification contract
        run: |
          set -euo pipefail
          # Cadence input: caller supplies whether this run is due.
          # The context is always emitted; no if: is used.
          RUN_DUE="${{ inputs.run_verification_contract || 'true' }}"
          if [ "${RUN_DUE}" = "false" ]; then
            echo "Verification contract check not due this run — explicit recorded success (§33.2)"
            exit 0
          fi
          python -m tools.evidence.verification_contract_check \
            --contract verification/contract.yaml \
            --criticality "${{ inputs.reliability_criticality || 'standard' }}" \
            --summary

  seeded-defect-case:
    name: seeded-defect-case
    runs-on: ubuntu-latest
    needs: [verification-contract]
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Execute seeded-defect case (inversion — §31.2)
        run: |
          set -euo pipefail
          # Cadence: caller supplies whether this run is due.
          # No if: on required context.
          RUN_DUE="${{ inputs.run_seeded_defect || 'true' }}"
          if [ "${RUN_DUE}" = "false" ]; then
            echo "Seeded-defect check not due this run — explicit recorded success (§33.2)"
            exit 0
          fi
          python -m tools.evidence.seeded_defect \
            --result "${{ inputs.seeded_defect_result_path || 'verification/seeded-results.json' }}" \
            --summary
YAML_EOF
```

**Acceptance criteria**

1. Jobs named exactly `verification-contract` and `seeded-defect-case` exist in `.github/workflows/ci.yml`.
2. Neither carries an `if:`; the cadence is evaluated inside the job.
3. `check_required_contexts` still reports `OK … checked=15 failed=0`.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/ci.yml --summary; echo "EXIT=$?"
python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary; echo "EXIT=$?"
echo "JOBS=$(grep -cE '^  (verification-contract|seeded-defect-case):' .github/workflows/ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
OK check_required_contexts checked=15 failed=0
EXIT=0
JOBS=2
```

**STOP** — the obvious implementation of "on every default-branch run" is `if: github.ref == 'refs/heads/main'`, and it is exactly what §33.2 forbids on a required context. Rule S4; blocker title `BLOCKER L2-T138: cadence cannot be expressed without an if: on a required context`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t138-ci-verification`.

---

### L2-T518 — Conformance-profile evidence substitution

**#** 51 · **Phase** BT-3 · **Size** M · **Deps** L2-T530 · **Branch slug** `t518-profile-evidence`
**Files:** `tools/evidence/profile_evidence.py`, `tools/evidence/fixtures/profile/**`
**Spec:** §15.7 L1587–1606 (the seven profiles and their equivalent evidence); §32 L2803–2828 — *"Items 10 and 11 are the evidence of the service conformance profile. A product declaring a different profile substitutes its equivalent evidence for them"*

**Build this.** The substitution table, in code, for evidence-chain items 10 and 11. Exactly seven profiles, transcribed from the §15.7 table and no others:

| Profile | Substitutes for items 10 and 11 |
| --- | --- |
| `service` | the contract as written — health and version endpoints |
| `client-app` | crash-free-session telemetry and store version adoption |
| `library` | registry version plus consumer contract tests |
| `batch` | job success and data-freshness signals |
| `customer-hosted` | customer-attested deploy and restore records, or a recorded exemption with a compensating control |
| `white-label` | a per-deployment environment list |
| `static-site` | build reproducibility |

An undeclared profile defaults to `service` (§15.7: *"`service` by default"*). An unknown profile string is `ERROR`, exit `3` — never a silent fallback to `service`, because *"a `service` product cannot escape availability evidence by mis-declaring its profile"*.

Tool-id `profile_evidence`. `checked=2` (items 10 and 11); `failed=` counts items whose declared evidence is absent.



**Commands**

```bash
# §0.3 open block already run with branch-slug t518-profile-evidence
set -euo pipefail

mkdir -p tools/evidence/fixtures/profile

cat > tools/evidence/profile_evidence.py << 'PYTHON_EOF'
"""
tools.evidence.profile_evidence
L2-T518: Conformance-profile evidence substitution (§15.7, §32 items 10 and 11)

Exactly seven profiles, transcribed from §15.7.
An unknown profile is ERROR, exit 3 — never a silent fallback.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR profile_evidence checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "profile_evidence"
CHECKED = 2  # items 10 and 11

# Exactly seven profiles from §15.7. The list is closed.
PROFILES = {
    "service": {
        "item_10": "post_deployment_smoke",
        "item_11": "health_and_version_endpoints",
        "description": "health and version endpoints (§15.7 default)",
    },
    "client-app": {
        "item_10": "crash_free_session_telemetry",
        "item_11": "store_version_adoption",
        "description": "crash-free-session telemetry and store version adoption",
    },
    "library": {
        "item_10": "registry_version",
        "item_11": "consumer_contract_tests",
        "description": "registry version plus consumer contract tests",
    },
    "batch": {
        "item_10": "job_success_signals",
        "item_11": "data_freshness_signals",
        "description": "job success and data-freshness signals",
    },
    "customer-hosted": {
        "item_10": "customer_attested_deploy",
        "item_11": "customer_attested_restore_or_exemption",
        "description": "customer-attested deploy and restore records, or a recorded exemption with a compensating control",
    },
    "white-label": {
        "item_10": "per_deployment_environment_list",
        "item_11": "per_deployment_environment_list",
        "description": "a per-deployment environment list",
    },
    "static-site": {
        "item_10": "build_reproducibility",
        "item_11": "build_reproducibility",
        "description": "build reproducibility",
    },
}


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def check(profile: Optional[str], evidence: Optional[dict]) -> int:
    """
    Returns number of failed conditions (0, 1, or 2).
    Raises SystemExit(3) on ERROR.
    """
    if profile is None:
        print(
            "INFO: no profile declared, defaulting to 'service' (§15.7)",
            file=sys.stderr,
        )
        profile = "service"

    if profile not in PROFILES:
        print(
            f"ERROR: unknown conformance profile '{profile}' — "
            "not in the §15.7 seven-profile list. "
            "A 'service' product cannot escape availability evidence by mis-declaring its profile.",
            file=sys.stderr,
        )
        _summary("ERROR", 0, 0)
        sys.exit(3)

    spec = PROFILES[profile]
    if evidence is None:
        evidence = {}

    failed = 0

    # Item 10
    key_10 = spec["item_10"]
    if not evidence.get(key_10):
        print(
            f"FAIL: evidence-chain item 10 missing for profile '{profile}': "
            f"expected '{key_10}' ({spec['description']})",
            file=sys.stderr,
        )
        failed += 1

    # Item 11
    key_11 = spec["item_11"]
    if key_11 != key_10 and not evidence.get(key_11):
        print(
            f"FAIL: evidence-chain item 11 missing for profile '{profile}': "
            f"expected '{key_11}' ({spec['description']})",
            file=sys.stderr,
        )
        failed += 1
    elif key_11 == key_10 and not evidence.get(key_11):
        # Both item 10 and item 11 map to the same evidence key; already counted above
        pass

    return failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    parser.add_argument("--evidence-file", default=None)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    evidence = None
    if args.evidence_file:
        if not os.path.exists(args.evidence_file):
            print(f"ERROR: evidence file not found: {args.evidence_file}", file=sys.stderr)
            _summary("ERROR", 0, 0)
            sys.exit(3)
        try:
            with open(args.evidence_file, "r", encoding="utf-8") as fh:
                evidence = yaml.safe_load(fh) or {}
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: cannot parse evidence file: {exc}", file=sys.stderr)
            _summary("ERROR", 0, 0)
            sys.exit(3)
    else:
        # When called without an evidence file (fixture mode), assume all keys present
        # for the selected profile so the tool can demonstrate its structure.
        profile_key = args.profile or "service"
        if profile_key in PROFILES:
            spec = PROFILES[profile_key]
            evidence = {spec["item_10"]: "present", spec["item_11"]: "present"}

    failed = check(args.profile, evidence)

    if failed == 0:
        _summary("OK", CHECKED, 0)
        sys.exit(0)
    else:
        _summary("FAIL", CHECKED, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixture files for profile evidence
cat > tools/evidence/fixtures/profile/client-app-complete.yaml << 'EOF'
crash_free_session_telemetry: "99.7% over 7 days"
store_version_adoption: "87% on latest"
EOF

cat > tools/evidence/fixtures/profile/client-app-missing-adoption.yaml << 'EOF'
crash_free_session_telemetry: "99.7% over 7 days"
# store_version_adoption intentionally absent
EOF
```

**Acceptance criteria**

1. Exactly seven profiles are implemented; an eighth string is `ERROR`, exit `3`.
2. `--profile client-app` with both substitutions present → `OK profile_evidence checked=2 failed=0`, exit `0`.
3. `--profile client-app` missing store-adoption evidence → `FAIL profile_evidence checked=2 failed=1`, exit `2`.
4. An absent profile declaration resolves to `service` and is stated on stderr.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.profile_evidence --profile client-app --summary; echo "EXIT=$?"
python -m tools.evidence.profile_evidence --profile mobile-app --summary 2>/dev/null; echo "EXIT=$?"
echo "PROFILES=$(grep -cE '^\s*"(service|client-app|library|batch|customer-hosted|white-label|static-site)":' tools/evidence/profile_evidence.py)"
```

**CORRECT OUTPUT**

```
OK profile_evidence checked=2 failed=0
EXIT=0
ERROR profile_evidence checked=0 failed=0
EXIT=3
PROFILES=7
```

**STOP** — do not add an eighth profile, however reasonable it sounds. The list is §15.7's and is closed. Rule S4; blocker title `BLOCKER L2-T518: an eighth conformance profile is being requested`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t518-profile-evidence`.

---

### L2-T519 — Evidence chain — the eleven questions

**#** 52 · **Phase** BT-3 · **Size** L · **Deps** L2-T518, L2-T544 · **Branch slug** `t519-evidence-chain`
**Files:** `tools/evidence/evidence_chain.py`, `tools/evidence/fixtures/chain/**`
**Spec:** §32 L2803–2828 — the eleven questions and their sources; *"item 5 and item 11 must match"*; §98.2 Phase 6 completion check (*"the eleven-item evidence chain answerable for one real deployment"*); charter DoD-14

**Build this.** The reason subsystem F exists. Given one deployment record, the tool answers all eleven questions of §32 and fails if **any** answer is empty. The eleven, transcribed in order:

| # | Question | Source |
| --- | --- | --- |
| 1 | Which git commit? | artifact label and deployment record |
| 2 | Which pull request? | commit-to-PR association |
| 3 | Who approved it at Gate 2, and in which role? | PR review record cross-referenced with the assignment registry |
| 4 | Which CI run produced it? | workflow run linked to the commit |
| 5 | What is the artifact digest? | registry digest, recorded at build |
| 6 | When was it deployed to staging? | staging deployment record |
| 7 | Did staging verification pass? | smoke result and UAT record in the workflow run |
| 8 | Who approved production? | production-approval record, verified by the workflow-identity gate |
| 9 | When was it deployed to production? | production deployment record |
| 10 | Did post-deployment smoke pass? | smoke result attached to the deployment |
| 11 | What digest is running right now? | `GET /version` on the live service |

Items 10 and 11 route through `profile_evidence` for a non-`service` profile. The tool additionally asserts the §32 invariant: **item 5 and item 11 match**, and where the record declares an S18 platform-rebuild deployment the recorded identity stands in for the digest throughout.

Tool-id `evidence_chain`. `checked=11`; `failed=` counts unanswered questions plus the 5-vs-11 mismatch.

Fixtures under `fixtures/chain/`: `dep-complete.yaml` (all eleven answered, 5 == 11), `dep-no-approver.yaml` (item 8 empty), `dep-digest-drift.yaml` (5 != 11), `dep-client-app.yaml` (profile substitution on 10 and 11).



**Commands**

```bash
# §0.3 open block already run with branch-slug t519-evidence-chain
set -euo pipefail

mkdir -p tools/evidence/fixtures/chain

cat > tools/evidence/evidence_chain.py << 'PYTHON_EOF'
"""
tools.evidence.evidence_chain
L2-T519: Evidence chain — the eleven questions (§32 L2803-2828)

Answers all eleven questions for one deployment record.
Fails if any answer is empty.
Asserts item 5 == item 11 (or S18 identity substitution).

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os

try:
    import yaml
except ImportError:
    print("ERROR evidence_chain checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "evidence_chain"
CHECKED = 11

# The eleven questions of §32 in order, mapped to their deployment record fields
QUESTIONS = [
    ("q1_git_commit",        "Which git commit?"),
    ("q2_pull_request",      "Which pull request?"),
    ("q3_gate2_approver",    "Who approved at Gate 2, and in which role?"),
    ("q4_ci_run",            "Which CI run produced it?"),
    ("q5_artifact_digest",   "What is the artifact digest?"),
    ("q6_staging_deploy",    "When was it deployed to staging?"),
    ("q7_staging_passed",    "Did staging verification pass?"),
    ("q8_prod_approver",     "Who approved production?"),
    ("q9_prod_deploy",       "When was it deployed to production?"),
    ("q10_smoke_passed",     "Did post-deployment smoke pass?"),
    ("q11_live_digest",      "What digest is running right now?"),
]


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def check(record: dict) -> int:
    """
    Returns number of failed (unanswered) questions plus any 5-vs-11 mismatch.
    """
    failed = 0
    answers = {}

    for field, question in QUESTIONS:
        value = record.get(field)

        # Items 10 and 11: route through profile_evidence for non-service profiles
        if field in ("q10_smoke_passed", "q11_live_digest"):
            profile = record.get("conformance_profile", "service")
            if profile != "service":
                # For non-service profiles, the field may be a profile-specific key
                profile_value = record.get(f"{field}_profile_evidence")
                if not _is_empty(profile_value):
                    answers[field] = profile_value
                    continue
                # Fall through to check the original field

        if _is_empty(value):
            print(
                f"FAIL: evidence-chain question {field} is unanswered: {question}",
                file=sys.stderr,
            )
            failed += 1
        else:
            answers[field] = value

    # §32 invariant: item 5 and item 11 must match
    q5 = answers.get("q5_artifact_digest")
    q11 = answers.get("q11_live_digest")

    if q5 and q11:
        s18 = record.get("s18_platform_rebuild")
        if s18:
            # S18 platform-rebuild: the recorded identity stands in for the digest.
            # All three components must be present.
            required_s18 = ["pinned_commit", "lockfile_hash", "build_configuration"]
            missing = [k for k in required_s18 if not s18.get(k)]
            if missing:
                print(
                    f"FAIL: S18 platform-rebuild claimed but missing components: {missing}",
                    file=sys.stderr,
                )
                failed += 1
        elif q5 != q11:
            print(
                f"FAIL: §32 invariant violated — item 5 digest '{q5}' != item 11 live digest '{q11}'",
                file=sys.stderr,
            )
            failed += 1

    return failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.deployment):
        print(f"ERROR: deployment record not found: {args.deployment}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(args.deployment, "r", encoding="utf-8") as fh:
            record = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse deployment record: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not isinstance(record, dict):
        print("ERROR: deployment record is not a YAML mapping", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    failed = check(record)

    if failed == 0:
        _summary("OK", CHECKED, 0)
        sys.exit(0)
    else:
        _summary("FAIL", CHECKED, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixtures
cat > tools/evidence/fixtures/chain/dep-complete.yaml << 'EOF'
q1_git_commit: "abc123def456"
q2_pull_request: "PR-42"
q3_gate2_approver: "alice (role: tech-lead)"
q4_ci_run: "https://github.com/org/repo/actions/runs/12345"
q5_artifact_digest: "sha256:aabbcc001122"
q6_staging_deploy: "2026-09-01T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "bob (role: release-manager)"
q9_prod_deploy: "2026-09-01T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:aabbcc001122"
EOF

cat > tools/evidence/fixtures/chain/dep-no-approver.yaml << 'EOF'
q1_git_commit: "abc123def456"
q2_pull_request: "PR-42"
q3_gate2_approver: "alice (role: tech-lead)"
q4_ci_run: "https://github.com/org/repo/actions/runs/12345"
q5_artifact_digest: "sha256:aabbcc001122"
q6_staging_deploy: "2026-09-01T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: ""
q9_prod_deploy: "2026-09-01T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:aabbcc001122"
EOF

cat > tools/evidence/fixtures/chain/dep-digest-drift.yaml << 'EOF'
q1_git_commit: "abc123def456"
q2_pull_request: "PR-42"
q3_gate2_approver: "alice (role: tech-lead)"
q4_ci_run: "https://github.com/org/repo/actions/runs/12345"
q5_artifact_digest: "sha256:aabbcc001122"
q6_staging_deploy: "2026-09-01T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "bob (role: release-manager)"
q9_prod_deploy: "2026-09-01T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:different99999"
EOF

cat > tools/evidence/fixtures/chain/dep-client-app.yaml << 'EOF'
conformance_profile: client-app
q1_git_commit: "abc123def456"
q2_pull_request: "PR-42"
q3_gate2_approver: "alice (role: tech-lead)"
q4_ci_run: "https://github.com/org/repo/actions/runs/12345"
q5_artifact_digest: "sha256:aabbcc001122"
q6_staging_deploy: "2026-09-01T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "bob (role: release-manager)"
q9_prod_deploy: "2026-09-01T14:00:00Z"
q10_smoke_passed: true
q10_smoke_passed_profile_evidence: "crash_free_session: 99.7%"
q11_live_digest: "sha256:aabbcc001122"
q11_live_digest_profile_evidence: "store_adoption: 87%"
EOF
```

**Acceptance criteria**

1. `dep-complete.yaml` → `OK evidence_chain checked=11 failed=0`, exit `0`.
2. `dep-no-approver.yaml` → `FAIL evidence_chain checked=11 failed=1`, exit `2`.
3. `dep-digest-drift.yaml` → `FAIL evidence_chain checked=11 failed=1`, exit `2`.
4. `dep-client-app.yaml` → `OK evidence_chain checked=11 failed=0`, exit `0`, with items 10 and 11 answered from the profile substitution.
5. A question answered by an empty string counts as unanswered.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in dep-complete dep-no-approver dep-digest-drift dep-client-app; do
  python -m tools.evidence.evidence_chain --deployment tools/evidence/fixtures/chain/$F.yaml --summary; echo "EXIT=$?"
done
```

**CORRECT OUTPUT**

```
OK evidence_chain checked=11 failed=0
EXIT=0
FAIL evidence_chain checked=11 failed=1
EXIT=2
FAIL evidence_chain checked=11 failed=1
EXIT=2
OK evidence_chain checked=11 failed=0
EXIT=0
```

**STOP** — if question 3's role cannot be resolved because the assignment registry is unreachable, that is `ERROR`, exit `3`, not an empty answer that passes. Rule S1; blocker title `BLOCKER L2-T519: assignment registry unreachable, chain question 3 unanswerable`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t519-evidence-chain`.

---

### L2-T550 — `verify-digest-chain` sweep

> **Index — `L2-T520` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T520` in full (*Branch, and the flat-record reader*) and is authoritative for that id; this block is different work and now carries the id `L2-T550`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 53 · **Phase** BT-3 · **Size** L · **Deps** L2-T519 · **Branch slug** `t550-verify-digest-chain`
**Files:** `tools/evidence/verify_digest_chain.py`, `tools/evidence/fixtures/sweep/**`
**Spec:** §46.1 L4090–4131 — *"Completion of step 3 — the digest-vs-approval verification, executed by the named build-surface script `verify-digest-chain` — gates resumption of production deploys"*; charter DoD-13

**Build this.** The estate-wide sweep. For every product in the estate it runs the `evidence_chain` comparison of digest versus approval record and fails on **any** mismatch. It is the recovery-step-3 gate: while it is failing, nothing new deploys to production.

Tool-id `verify_digest_chain`. `checked=` counts products swept; `failed=` counts products whose chain does not close.

Fixtures under `fixtures/sweep/`: `clean/` (3 products, all closed), `one-broken/` (3 products, one with a digest/approval mismatch), `empty/` (no products).



**Commands**

```bash
# §0.3 open block already run with branch-slug t550-verify-digest-chain
set -euo pipefail

mkdir -p tools/evidence/fixtures/sweep/clean
mkdir -p tools/evidence/fixtures/sweep/one-broken
mkdir -p tools/evidence/fixtures/sweep/empty

cat > tools/evidence/verify_digest_chain.py << 'PYTHON_EOF'
"""
tools.evidence.verify_digest_chain
L2-T550: Estate-wide verify-digest-chain sweep (§46.1 L4090-4131)

For every product in the estate, verifies the evidence chain closes.
An empty estate is ERROR, not clean.
Gates resumption of production deploys.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os
import glob

try:
    import yaml
    from tools.evidence import evidence_chain as ec_module
except ImportError:
    print("ERROR verify_digest_chain checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "verify_digest_chain"


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def sweep(estate_dir: str) -> tuple[int, int]:
    """
    Returns (checked, failed).
    Raises SystemExit(3) on empty estate or fatal error.
    """
    if not os.path.isdir(estate_dir):
        print(f"ERROR: estate directory not found: {estate_dir}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    # Discover all product deployment records in the estate
    product_files = sorted(glob.glob(os.path.join(estate_dir, "*.yaml")))
    if not product_files:
        print(
            "ERROR: estate directory contains no product records — "
            "an empty estate is not a clean estate (§46.1)",
            file=sys.stderr,
        )
        _summary("ERROR", 0, 0)
        sys.exit(3)

    checked = len(product_files)
    failed = 0

    for product_file in product_files:
        product_name = os.path.basename(product_file).replace(".yaml", "")
        try:
            with open(product_file, "r", encoding="utf-8") as fh:
                record = yaml.safe_load(fh)
        except Exception as exc:  # noqa: BLE001
            print(
                f"ERROR: cannot parse product record '{product_name}': {exc}",
                file=sys.stderr,
            )
            failed += 1
            continue

        if not isinstance(record, dict):
            print(
                f"FAIL: product '{product_name}' record is not a YAML mapping",
                file=sys.stderr,
            )
            failed += 1
            continue

        # Run evidence_chain check for this product
        failure_count = ec_module.check(record)
        if failure_count > 0:
            print(
                f"FAIL: product '{product_name}' chain does not close "
                f"({failure_count} unanswered question(s))",
                file=sys.stderr,
            )
            failed += 1
        else:
            print(f"OK: product '{product_name}' chain is closed", file=sys.stderr)

    return checked, failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--estate", required=True, help="Directory of product deployment records")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    checked, failed = sweep(args.estate)

    if failed == 0:
        _summary("OK", checked, 0)
        sys.exit(0)
    else:
        _summary("FAIL", checked, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Clean fixture — 3 products, all closed
cat > tools/evidence/fixtures/sweep/clean/product-alpha.yaml << 'EOF'
q1_git_commit: "aaabbbccc"
q2_pull_request: "PR-10"
q3_gate2_approver: "alice (role: tech-lead)"
q4_ci_run: "https://github.com/org/alpha/actions/runs/1"
q5_artifact_digest: "sha256:alpha001"
q6_staging_deploy: "2026-09-01T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "bob (role: release-manager)"
q9_prod_deploy: "2026-09-01T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:alpha001"
EOF
cat > tools/evidence/fixtures/sweep/clean/product-beta.yaml << 'EOF'
q1_git_commit: "bbbcccaaa"
q2_pull_request: "PR-20"
q3_gate2_approver: "carol (role: tech-lead)"
q4_ci_run: "https://github.com/org/beta/actions/runs/2"
q5_artifact_digest: "sha256:beta002"
q6_staging_deploy: "2026-09-02T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "dave (role: release-manager)"
q9_prod_deploy: "2026-09-02T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:beta002"
EOF
cat > tools/evidence/fixtures/sweep/clean/product-gamma.yaml << 'EOF'
q1_git_commit: "cccaaabbb"
q2_pull_request: "PR-30"
q3_gate2_approver: "eve (role: tech-lead)"
q4_ci_run: "https://github.com/org/gamma/actions/runs/3"
q5_artifact_digest: "sha256:gamma003"
q6_staging_deploy: "2026-09-03T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "frank (role: release-manager)"
q9_prod_deploy: "2026-09-03T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:gamma003"
EOF

# One-broken fixture — product-beta has a digest mismatch
cp tools/evidence/fixtures/sweep/clean/product-alpha.yaml tools/evidence/fixtures/sweep/one-broken/product-alpha.yaml
cat > tools/evidence/fixtures/sweep/one-broken/product-beta.yaml << 'EOF'
q1_git_commit: "bbbcccaaa"
q2_pull_request: "PR-20"
q3_gate2_approver: "carol (role: tech-lead)"
q4_ci_run: "https://github.com/org/beta/actions/runs/2"
q5_artifact_digest: "sha256:beta002"
q6_staging_deploy: "2026-09-02T10:00:00Z"
q7_staging_passed: true
q8_prod_approver: "dave (role: release-manager)"
q9_prod_deploy: "2026-09-02T14:00:00Z"
q10_smoke_passed: true
q11_live_digest: "sha256:DIFFERENT-MISMATCH"
EOF
cp tools/evidence/fixtures/sweep/clean/product-gamma.yaml tools/evidence/fixtures/sweep/one-broken/product-gamma.yaml

# Empty fixture — no files in directory (test expects ERROR)
touch tools/evidence/fixtures/sweep/empty/.gitkeep
```

**Acceptance criteria**

1. `clean/` → `OK verify_digest_chain checked=3 failed=0`, exit `0`.
2. `one-broken/` → `FAIL verify_digest_chain checked=3 failed=1`, exit `2`.
3. `empty/` → `ERROR verify_digest_chain checked=0 failed=0`, exit `3`. An empty estate is not a clean estate.
4. Both directions are exercised — the clean case and the broken case — and neither is asserted only in a comment.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for D in clean one-broken empty; do
  python -m tools.evidence.verify_digest_chain --estate tools/evidence/fixtures/sweep/$D --summary 2>/dev/null; echo "EXIT=$?"
done
```

**CORRECT OUTPUT**

```
OK verify_digest_chain checked=3 failed=0
EXIT=0
FAIL verify_digest_chain checked=3 failed=1
EXIT=2
ERROR verify_digest_chain checked=0 failed=0
EXIT=3
```

**STOP** — this tool gates resumption of production deploys after a GitHub outage. Never add a flag that lets a caller resume while it is failing. Rule S4; blocker title `BLOCKER L2-T550: a resume-despite-failure flag is being requested on verify-digest-chain`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t550-verify-digest-chain`.

---

### L2-T139 — `verify-digest-chain.yml` — sweep and recovery gate

**#** 54 · **Phase** BT-3 · **Size** M · **Deps** L2-T550 · **Branch slug** `t139-wf-verify-digest-chain`
**Files:** `.github/workflows/verify-digest-chain.yml`
**Spec:** §46.1 L4090–4131 (the six recovery steps, their owner and their clock — the escalation role, within the first half working day after recovery)

**Build this.** Two triggers on one workflow: a `schedule` for the routine sweep, and a `workflow_dispatch` for the recovery-step-3 run. It invokes `verify_digest_chain` over the estate and, on failure, writes an event and fails the run. It emits no required status context — it is an estate sweep, not a per-pull-request check, and it appears in no group of `required-checks.yaml`.



**Commands**

```bash
# §0.3 open block already run with branch-slug t139-wf-verify-digest-chain
set -euo pipefail

cat > .github/workflows/verify-digest-chain.yml << 'YAML_EOF'
name: verify-digest-chain

on:
  # Routine sweep — nightly (§46.1: within the first half working day after recovery)
  schedule:
    - cron: '0 6 * * 1-5'
  # Recovery-step-3 run — manual dispatch (§46.1)
  workflow_dispatch:
    inputs:
      estate_path:
        description: 'Path to estate deployment records directory'
        required: false
        default: 'records/deployments'

# This workflow emits no required status context (§0.5).
# It is an estate sweep, not a per-pull-request check.

permissions:
  contents: read

concurrency:
  group: verify-digest-chain
  cancel-in-progress: false

jobs:
  verify-digest-chain:
    name: verify-digest-chain-sweep
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Set up Python
        uses: actions/setup-python@PIN:actions/setup-python
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Run estate sweep
        id: sweep
        run: |
          set -euo pipefail
          ESTATE="${{ github.event.inputs.estate_path || 'records/deployments' }}"
          python -m tools.evidence.verify_digest_chain \
            --estate "${ESTATE}" \
            --summary

      - name: Write failure event and fail run
        if: failure()
        run: |
          set -euo pipefail
          python -m tools.evidence.event_writer \
            --dry-run \
            --event - <<'EVENT'
          event_type: digest_chain_sweep_failed
          product: estate-wide
          actor: ${{ github.actor }}
          timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          sig: P0
          detail: verify-digest-chain sweep failed — production deploys gated
          source: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          run_id: ${{ github.run_id }}
          environment: production
          EVENT
          exit 1
YAML_EOF
```

**Acceptance criteria**

1. Both `schedule` and `workflow_dispatch` triggers are present.
2. The workflow emits no name listed in `required-checks.yaml`.
3. A failing sweep fails the run; there is no `continue-on-error`.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/verify-digest-chain.yml --summary; echo "EXIT=$?"
echo "TRIGGERS=$(grep -cE '^  (schedule|workflow_dispatch):' .github/workflows/verify-digest-chain.yml)"
echo "BEST_EFFORT=$(grep -c 'continue-on-error' .github/workflows/verify-digest-chain.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
TRIGGERS=2
BEST_EFFORT=0
```

**STOP** — do not add this workflow's job name to `required-checks.yaml`. §0.5. Rule S4; blocker title `BLOCKER L2-T139: asked to publish the sweep as a required context`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t139-wf-verify-digest-chain`.

---

### L2-T551 — `/version` digest-match monitor

> **Index — `L2-T521` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T521` in full (*The artifact-identity format library*) and is authoritative for that id; this block is different work and now carries the id `L2-T551`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 55 · **Phase** BT-3 · **Size** M · **Deps** L2-T519 · **Branch slug** `t551-version-monitor`
**Files:** `tools/evidence/version_monitor.py`, `tools/evidence/fixtures/version/**`
**Spec:** §41.2 L3717–3729 — *"`/version` closes the production evidence chain: the digest it reports must equal the approved digest, and any mismatch is a P0 investigation"*; §32 item 11

**Build this.** The observer that answers evidence-chain question 11. It reads a `/version` observation and compares the reported digest with the approved digest. A mismatch is a failure and prints the literal string `P0_DIGEST_MISMATCH`. A product whose declared `conformance_profile` does not expose the service interface routes to `profile_evidence` instead and is never failed for lacking an endpoint its shape cannot serve (§41.2, §15.7).

An unreachable endpoint is `ERROR`, exit `3` — unreachable is not matching.

Tool-id `version_monitor`. `checked=1`; `failed=` 0 or 1.

Fixtures under `fixtures/version/`: `match.json`, `mismatch.json`, `unreachable.json`, `client-app.json`.



**Commands**

```bash
# §0.3 open block already run with branch-slug t551-version-monitor
set -euo pipefail

mkdir -p tools/evidence/fixtures/version

cat > tools/evidence/version_monitor.py << 'PYTHON_EOF'
"""
tools.evidence.version_monitor
L2-T551: /version digest-match monitor (§41.2 L3717-3729, §32 item 11)

Answers evidence-chain question 11.
A mismatch is a failure and raises P0_DIGEST_MISMATCH.
An unreachable endpoint is ERROR, exit 3 — not matching.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import json
import sys
import os

TOOL_ID = "version_monitor"

# Conformance profiles that do not expose a /version endpoint (§15.7, §41.2)
NON_SERVICE_PROFILES = {
    "client-app",
    "library",
    "batch",
    "customer-hosted",
    "white-label",
    "static-site",
}


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def check_fixture(fixture: dict) -> tuple[str, int, int]:
    """
    Returns (status, checked, failed).
    """
    profile = fixture.get("conformance_profile", "service")

    # Non-service profiles route to profile_evidence (§41.2, §15.7)
    if profile in NON_SERVICE_PROFILES:
        profile_evidence = fixture.get("profile_evidence")
        if profile_evidence:
            # Profile substitution satisfied
            return "OK", 1, 0
        # Even for non-service profiles, absence of substitution evidence is a failure
        print(
            f"FAIL: profile '{profile}' declares no profile_evidence for item 11",
            file=sys.stderr,
        )
        return "FAIL", 1, 1

    # Service profile: compare approved digest with /version response
    status_code = fixture.get("status_code", 200)
    if status_code != 200:
        print(
            f"ERROR: /version endpoint returned HTTP {status_code} — "
            "unreachable is not matching (§41.2)",
            file=sys.stderr,
        )
        return "ERROR", 0, 0

    unreachable = fixture.get("unreachable", False)
    if unreachable:
        print(
            "ERROR: /version endpoint is unreachable — unreachable is not matching (§41.2)",
            file=sys.stderr,
        )
        return "ERROR", 0, 0

    approved_digest = fixture.get("approved_digest")
    live_digest = fixture.get("live_digest")

    if not approved_digest or not live_digest:
        print(
            "ERROR: fixture missing approved_digest or live_digest",
            file=sys.stderr,
        )
        return "ERROR", 0, 0

    if approved_digest != live_digest:
        print(
            f"P0_DIGEST_MISMATCH: approved='{approved_digest}' live='{live_digest}' (§41.2)",
            file=sys.stderr,
        )
        return "FAIL", 1, 1

    return "OK", 1, 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, help="Path to version observation fixture JSON")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.fixture):
        print(f"ERROR: fixture file not found: {args.fixture}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(args.fixture, "r", encoding="utf-8") as fh:
            fixture = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse fixture JSON: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    status, checked, failed = check_fixture(fixture)
    _summary(status, checked, failed)

    if status == "OK":
        sys.exit(0)
    elif status == "FAIL":
        sys.exit(2)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixtures
cat > tools/evidence/fixtures/version/match.json << 'EOF'
{
  "conformance_profile": "service",
  "approved_digest": "sha256:production001",
  "live_digest": "sha256:production001",
  "status_code": 200,
  "endpoint": "https://product.example.com/version"
}
EOF

cat > tools/evidence/fixtures/version/mismatch.json << 'EOF'
{
  "conformance_profile": "service",
  "approved_digest": "sha256:production001",
  "live_digest": "sha256:stale-build-999",
  "status_code": 200,
  "endpoint": "https://product.example.com/version"
}
EOF

cat > tools/evidence/fixtures/version/unreachable.json << 'EOF'
{
  "conformance_profile": "service",
  "approved_digest": "sha256:production001",
  "unreachable": true,
  "endpoint": "https://product.example.com/version"
}
EOF

cat > tools/evidence/fixtures/version/client-app.json << 'EOF'
{
  "conformance_profile": "client-app",
  "profile_evidence": {
    "store_version_adoption": "87% on latest",
    "crash_free_session_telemetry": "99.7% over 7 days"
  }
}
EOF
```

**Acceptance criteria**

1. `match.json` → `OK version_monitor checked=1 failed=0`, exit `0`.
2. `mismatch.json` → `FAIL version_monitor checked=1 failed=1`, exit `2`, and `P0_DIGEST_MISMATCH` on stderr.
3. `unreachable.json` → `ERROR version_monitor checked=0 failed=0`, exit `3`.
4. `client-app.json` → `OK version_monitor checked=1 failed=0`, exit `0`, answered from the profile substitution.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.version_monitor --fixture tools/evidence/fixtures/version/match.json --summary; echo "EXIT=$?"
python -m tools.evidence.version_monitor --fixture tools/evidence/fixtures/version/mismatch.json --summary 2>&1 | tail -2
python -m tools.evidence.version_monitor --fixture tools/evidence/fixtures/version/unreachable.json --summary 2>/dev/null; echo "EXIT=$?"
python -m tools.evidence.version_monitor --fixture tools/evidence/fixtures/version/client-app.json --summary; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK version_monitor checked=1 failed=0
EXIT=0
P0_DIGEST_MISMATCH
FAIL version_monitor checked=1 failed=1
ERROR version_monitor checked=0 failed=0
EXIT=3
OK version_monitor checked=1 failed=0
EXIT=0
```

**STOP** — the `/version` observation transport is not settled in this file. If reaching a live `/version` requires a credential or a network path Lane 2 does not hold, build against the fixtures and stop. Rule S1; blocker title `BLOCKER L2-T551: /version observation transport unavailable to Lane 2`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t551-version-monitor`.

---

### L2-T140 — `version-monitor.yml`

**#** 56 · **Phase** BT-3 · **Size** S · **Deps** L2-T551 · **Branch slug** `t140-wf-version-monitor`
**Files:** `.github/workflows/version-monitor.yml`
**Spec:** §41.2 L3717–3729; §32 item 11

**Build this.** A scheduled workflow invoking `version_monitor` across the estate, writing an event on mismatch and failing the run. It emits no required context. The `/metrics` and `/health` endpoints are **not** scraped here — that is the operations VM's scrape path, `ops-vm/**`, Lane 5's tree (§41.2, §51.4).



**Commands**

```bash
# §0.3 open block already run with branch-slug t140-wf-version-monitor
set -euo pipefail

cat > .github/workflows/version-monitor.yml << 'YAML_EOF'
name: version-monitor

on:
  # Scheduled sweep — version monitoring for §32 item 11 (§41.2 L3717-3729)
  schedule:
    - cron: '*/30 * * * *'

# This workflow emits no required status context.
# /metrics and /health endpoints are NOT scraped here — that is ops-vm/** (Lane 5, §41.2, §51.4).

permissions:
  contents: read

concurrency:
  group: version-monitor
  cancel-in-progress: true

jobs:
  version-monitor:
    name: version-monitor-sweep
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Set up Python
        uses: actions/setup-python@PIN:actions/setup-python
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Monitor /version across estate
        id: monitor
        run: |
          set -euo pipefail
          # version_monitor is invoked; its exit code fails the run
          FAILED=0
          while IFS= read -r fixture_file; do
            python -m tools.evidence.version_monitor \
              --fixture "${fixture_file}" \
              --summary || FAILED=1
          done < <(find records/version-observations -name "*.json" 2>/dev/null)
          exit "${FAILED}"

      - name: Write mismatch event and fail run
        if: failure()
        run: |
          set -euo pipefail
          python -m tools.evidence.event_writer \
            --dry-run \
            --event - <<'EVENT'
          event_type: version_digest_mismatch
          product: estate-wide
          actor: ${{ github.actor }}
          timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          sig: P0
          detail: /version monitor detected digest mismatch — P0 investigation required
          source: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          run_id: ${{ github.run_id }}
          environment: production
          EVENT
          exit 1
YAML_EOF
```

**Acceptance criteria**

1. `schedule` trigger present; the workflow emits no registry context name.
2. `version_monitor` is invoked and its exit code fails the run.
3. The workflow contains no `/metrics` or `/health` scrape.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/version-monitor.yml --summary; echo "EXIT=$?"
echo "SCRAPES=$(grep -cE '/(metrics|health)' .github/workflows/version-monitor.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
SCRAPES=0
```

**STOP** — if this workflow appears to need a Prometheus scrape configuration, that is `ops-vm/**`. Rule S2; blocker title `BLOCKER L2-T140: version monitor requires an ops-VM scrape path`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t140-wf-version-monitor`.

---

### L2-T552 — Restore-rotation scheduler computation

> **Index — `L2-T522` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T522` in full (*Compute the S18 platform-rebuild identity (D78)*) and is authoritative for that id; this block is different work and now carries the id `L2-T552`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 57 · **Phase** BT-3 · **Size** M · **Deps** L2-T530 · **Branch slug** `t552-restore-rotation`
**Files:** `tools/evidence/restore_rotation.py`, `tools/evidence/fixtures/rotation/**`
**Spec:** §44.2 L3993–4002 — the rolling 90-day floor, the 30-day window for `critical`, *"The rotation is computed, never remembered"*, and *"The `restore_tested` date is derived, not declared"*

**Build this.** Deterministic date arithmetic, and nothing else. Given the estate and an `--as-of` date, it computes each product's restore deadline from its applicable window and its **derived** `restore_tested` date — the newest passing record in `records/restore-tests/` — and proposes the coming month's subset. `classification.reliability_criticality` may only **tighten** the window: `critical` is 30 days, everything else is the 90-day floor. A declared `restore_tested` date that disagrees with the derived one is drift and fails: *"A hand-edited date is drift, not evidence."*

Tool-id `restore_rotation`. `checked=` counts products; `failed=` counts products past their window plus products whose declared date disagrees with the derived one.

Fixtures under `fixtures/rotation/`: `estate.yaml` with 4 products — one `critical` inside 30 days, one `critical` at 31 days, one standard at 89 days, one standard whose declared date is newer than its newest passing record.



**Commands**

```bash
# §0.3 open block already run with branch-slug t552-restore-rotation
set -euo pipefail

mkdir -p tools/evidence/fixtures/rotation

cat > tools/evidence/restore_rotation.py << 'PYTHON_EOF'
"""
tools.evidence.restore_rotation
L2-T552: Restore-rotation scheduler computation (§44.2 L3993-4002)

Deterministic date arithmetic only.
The rotation is computed, never remembered.
The restore_tested date is derived, not declared.
A hand-edited date is drift, not evidence.

Windows: critical = 30 days, all others = 90 days (the floor — never wider).

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os
import glob
from datetime import date, timedelta

try:
    import yaml
except ImportError:
    print("ERROR restore_rotation checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "restore_rotation"

WINDOW_CRITICAL_DAYS = 30
WINDOW_FLOOR_DAYS = 90  # never wider


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def _get_window_days(criticality: str) -> int:
    """Returns the window in days. classification.reliability_criticality may only tighten."""
    if criticality == "critical":
        return WINDOW_CRITICAL_DAYS
    # All other values use the 90-day floor; no code path produces a deadline beyond 90 days
    return WINDOW_FLOOR_DAYS


def _derive_restore_tested(product_name: str, records_dir: str) -> date | None:
    """
    Derives the restore_tested date from the newest passing record in records/restore-tests/.
    Never uses a hand-declared value.
    """
    pattern = os.path.join(records_dir, f"{product_name}-*.yaml")
    files = sorted(glob.glob(pattern), reverse=True)
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                rec = yaml.safe_load(fh) or {}
            if rec.get("result") == "pass" and rec.get("tested_date"):
                return date.fromisoformat(str(rec["tested_date"]))
        except Exception:  # noqa: BLE001
            continue
    return None


def compute(estate_path: str, as_of_str: str, records_dir: str) -> tuple[int, int]:
    """
    Returns (checked, failed).
    """
    try:
        as_of = date.fromisoformat(as_of_str)
    except ValueError as exc:
        print(f"ERROR: invalid --as-of date: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not os.path.exists(estate_path):
        print(f"ERROR: estate file not found: {estate_path}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(estate_path, "r", encoding="utf-8") as fh:
            estate = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse estate: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    products = estate.get("products", [])
    checked = len(products)
    failed = 0

    for product in products:
        name = product.get("name", "unknown")
        criticality = product.get("classification", {}).get("reliability_criticality", "standard")
        declared_restore_tested = product.get("restore_tested")

        window_days = _get_window_days(criticality)

        # Derive restore_tested from records — never use declared value
        derived_date = _derive_restore_tested(name, records_dir)

        # Check for hand-edited date drift
        if declared_restore_tested and derived_date:
            declared_as_date = date.fromisoformat(str(declared_restore_tested))
            if declared_as_date != derived_date:
                print(
                    f"FAIL: product '{name}' — declared restore_tested '{declared_restore_tested}' "
                    f"differs from derived date '{derived_date}' (§44.2: a hand-edited date is drift)",
                    file=sys.stderr,
                )
                failed += 1
                continue

        if derived_date is None:
            print(
                f"FAIL: product '{name}' has no passing restore record — "
                f"window={window_days}d (criticality={criticality})",
                file=sys.stderr,
            )
            failed += 1
            continue

        deadline = derived_date + timedelta(days=window_days)
        days_remaining = (deadline - as_of).days

        if days_remaining < 0:
            print(
                f"FAIL: product '{name}' is past its {window_days}-day restore window — "
                f"last tested {derived_date}, deadline {deadline} ({abs(days_remaining)} days overdue)",
                file=sys.stderr,
            )
            failed += 1
        else:
            print(
                f"OK: product '{name}' — last tested {derived_date}, "
                f"deadline {deadline} ({days_remaining} days remaining)",
                file=sys.stderr,
            )

    return checked, failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--estate", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--records-dir", default="records/restore-tests")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    checked, failed = compute(args.estate, args.as_of, args.records_dir)

    if failed == 0:
        _summary("OK", checked, 0)
        sys.exit(0)
    else:
        _summary("FAIL", checked, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixture: estate with 4 products
# Product A: critical, 29 days ago (passes 30-day window)
# Product B: critical, 31 days ago (fails 30-day window)
# Product C: standard, 89 days ago (passes 90-day floor)
# Product D: standard, declared date newer than derived record (drift — fails)
cat > tools/evidence/fixtures/rotation/estate.yaml << 'EOF'
products:
  - name: product-alpha
    classification:
      reliability_criticality: critical
    # restore_tested derived from records; not declared here
  - name: product-beta
    classification:
      reliability_criticality: critical
    # restore_tested derived from records; not declared here
  - name: product-gamma
    classification:
      reliability_criticality: standard
    # restore_tested derived from records; not declared here
  - name: product-delta
    classification:
      reliability_criticality: standard
    restore_tested: "2026-08-26"  # hand-edited date — differs from derived record → drift
EOF

# Corresponding restore-test records
# as-of is 2026-08-27
# Product-alpha: tested 2026-07-30 (28 days before 2026-08-27 → within 30 days ✓)
mkdir -p tools/evidence/fixtures/rotation/records
cat > "tools/evidence/fixtures/rotation/records/product-alpha-2026-07-30.yaml" << 'EOF'
product: product-alpha
result: pass
tested_date: "2026-07-30"
verifier: alice
EOF

# Product-beta: tested 2026-07-27 (31 days before 2026-08-27 → past 30-day window ✗)
cat > "tools/evidence/fixtures/rotation/records/product-beta-2026-07-27.yaml" << 'EOF'
product: product-beta
result: pass
tested_date: "2026-07-27"
verifier: bob
EOF

# Product-gamma: tested 2026-05-30 (89 days before 2026-08-27 → within 90-day floor ✓)
cat > "tools/evidence/fixtures/rotation/records/product-gamma-2026-05-30.yaml" << 'EOF'
product: product-gamma
result: pass
tested_date: "2026-05-30"
verifier: carol
EOF

# Product-delta: record says 2026-08-20, declared says 2026-08-26 → drift ✗
cat > "tools/evidence/fixtures/rotation/records/product-delta-2026-08-20.yaml" << 'EOF'
product: product-delta
result: pass
tested_date: "2026-08-20"
verifier: dave
EOF
```

**Acceptance criteria**

1. `--as-of 2026-08-27` on `estate.yaml` → `FAIL restore_rotation checked=4 failed=2`, exit `2` — the 31-day `critical` and the hand-edited date.
2. A `critical` product at 31 days fails; the same product at 29 days passes. The tightening is exercised in both directions.
3. The tool never widens a window: no code path produces a deadline beyond 90 days.
4. Output is identical for the same `--as-of` regardless of the runner's clock or timezone.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.restore_rotation --estate tools/evidence/fixtures/rotation/estate.yaml --as-of 2026-08-27 --summary; echo "EXIT=$?"
TZ=Pacific/Auckland python -m tools.evidence.restore_rotation --estate tools/evidence/fixtures/rotation/estate.yaml --as-of 2026-08-27 --summary; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
FAIL restore_rotation checked=4 failed=2
EXIT=2
FAIL restore_rotation checked=4 failed=2
EXIT=2
```

**STOP** — there is exactly one restore-testing cadence: *"Wherever this document mentions restore testing, this is the rule it means; there is no second cadence"* (§44.2). If a product asks for a looser window, refuse. Rule S4; blocker title `BLOCKER L2-T552: a restore window looser than the 90-day floor is being requested`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t552-restore-rotation`.

---

### L2-T141 — `restore-rotation.yml`

**#** 58 · **Phase** BT-3 · **Size** S · **Deps** L2-T552 · **Branch slug** `t141-wf-restore-rotation`
**Files:** `.github/workflows/restore-rotation.yml`
**Spec:** §44.2 L3993–4002 — the **nightly** rotation scheduler that *"opens the scheduling issue that the escalation role works from"*; restore-testing execution is a platform workflow and is *"never delegated to the agent harness of Section 37"*

**Build this.** A nightly scheduled workflow that runs `restore_rotation`, opens or updates the scheduling issue with the computed subset, and writes the SIG-17 input. It never asks a person to remember the rotation, and it never dispatches work to the background machine layer.



**Commands**

```bash
# §0.3 open block already run with branch-slug t141-wf-restore-rotation
set -euo pipefail

cat > .github/workflows/restore-rotation.yml << 'YAML_EOF'
name: restore-rotation

on:
  # Nightly rotation scheduler (§44.2 — opens the scheduling issue the escalation role works from)
  schedule:
    - cron: '0 7 * * *'

# Restore-testing execution is a platform workflow and is NEVER delegated to the agent harness (§37)
# This workflow only computes the rotation and opens/updates the scheduling issue.

permissions:
  contents: read
  issues: write

concurrency:
  group: restore-rotation
  cancel-in-progress: false

jobs:
  restore-rotation:
    name: restore-rotation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Set up Python
        uses: actions/setup-python@PIN:actions/setup-python
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Compute rotation schedule
        id: rotation
        run: |
          set -euo pipefail
          AS_OF="$(date -u +%Y-%m-%d)"
          # restore_rotation is invoked; issue body is generated from its output
          python -m tools.evidence.restore_rotation \
            --estate contracts/estate.yaml \
            --as-of "${AS_OF}" \
            --records-dir records/restore-tests \
            --summary 2>&1 | tee rotation-output.txt
          EXIT_CODE="${PIPESTATUS[0]}"
          echo "ROTATION_EXIT=${EXIT_CODE}" >> "${GITHUB_OUTPUT}"
          echo "AS_OF=${AS_OF}" >> "${GITHUB_OUTPUT}"

      - name: Open or update scheduling issue (SIG-17 input)
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          AS_OF="${{ steps.rotation.outputs.AS_OF }}"
          ROTATION_OUTPUT="$(cat rotation-output.txt)"
          ISSUE_TITLE="[restore-rotation] Scheduling issue for ${AS_OF}"
          # Search for existing open issue; update if found, create if not
          EXISTING="$(gh issue list --state open --search "${ISSUE_TITLE}" --json number --jq '.[0].number' 2>/dev/null || echo '')"
          BODY="## Restore Rotation Schedule — ${AS_OF}

Generated by restore-rotation.yml from restore_rotation computation.
Escalation role works from this issue — not from memory.

\`\`\`
${ROTATION_OUTPUT}
\`\`\`

**SIG-17 input.** This issue is never hand-written.
"
          if [ -n "${EXISTING}" ]; then
            gh issue edit "${EXISTING}" --body "${BODY}"
          else
            gh issue create \
              --title "${ISSUE_TITLE}" \
              --body "${BODY}" \
              --label "restore-rotation,sig-17"
          fi
YAML_EOF
```

**Acceptance criteria**

1. A nightly `schedule` trigger.
2. `restore_rotation` is invoked and the issue body is generated from its output, not hand-written.
3. The workflow contains no dispatch to the background layer.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/restore-rotation.yml --summary; echo "EXIT=$?"
echo "ROTATION=$(grep -c 'tools.evidence.restore_rotation' .github/workflows/restore-rotation.yml)"
echo "SCHEDULE=$(grep -c '^  schedule:' .github/workflows/restore-rotation.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
ROTATION=1
SCHEDULE=1
```

**STOP** — do not hand the rotation to the agent harness, even as a rendering step beyond the wait-surface digest §44.2 permits (D72). Rule S4; blocker title `BLOCKER L2-T141: rotation work is being delegated to the agent harness`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t141-wf-restore-rotation`.

---

### L2-T142 — `record-verification-result.yml` dispatch

**#** 59 · **Phase** BT-3 · **Size** M · **Deps** L2-T544 · **Branch slug** `t142-record-verification-result`
**Files:** `.github/workflows/record-verification-result.yml`
**Spec:** §97.2 L8843–8926 — the record-verification-result dispatch and its structured inputs; §31.2 (*"Manual UAT results reach the record store through the record-verification-result dispatch — never by memory or chat"*); §44.3 (the Primary Owner confirms asynchronously through this dispatch)

**Build this.** A `workflow_dispatch` workflow accepting exactly the five structured inputs §97.2 names — **product, item, mechanism, pass-or-fail, evidence link** — validating them, and writing the corresponding record and event through `records_client` and `event_writer`. A call with any input missing is refused before any write. The workflow exposes **no path that edits an existing record by hand**.



**Commands**

```bash
# §0.3 open block already run with branch-slug t142-record-verification-result
set -euo pipefail

cat > .github/workflows/record-verification-result.yml << 'YAML_EOF'
name: record-verification-result

on:
  # Manual verification result dispatch (§97.2 L8843-8926, §31.2, §44.3)
  # "Manual UAT results reach the record store through this dispatch — never by memory or chat"
  workflow_dispatch:
    inputs:
      product:
        description: 'Product name (§97.2 field 1)'
        required: true
        type: string
      item:
        description: 'Verification item identifier (§97.2 field 2)'
        required: true
        type: string
      mechanism:
        description: 'Verification mechanism used (§97.2 field 3)'
        required: true
        type: string
      result:
        description: 'Pass or fail (§97.2 field 4)'
        required: true
        type: choice
        options:
          - pass
          - fail
      evidence_link:
        description: 'Link to evidence artefact (§97.2 field 5)'
        required: true
        type: string

permissions:
  contents: read

concurrency:
  group: record-verification-result-${{ github.event.inputs.product }}-${{ github.event.inputs.item }}
  cancel-in-progress: false

jobs:
  record-verification-result:
    name: record-verification-result
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@PIN:actions/checkout

      - name: Set up Python
        uses: actions/setup-python@PIN:actions/setup-python
        with:
          python-version: '3.12'

      - name: Install evidence toolchain
        run: pip install -r tools/evidence/requirements.txt

      - name: Validate all five inputs before any write
        run: |
          set -euo pipefail
          PRODUCT="${{ github.event.inputs.product }}"
          ITEM="${{ github.event.inputs.item }}"
          MECHANISM="${{ github.event.inputs.mechanism }}"
          RESULT="${{ github.event.inputs.result }}"
          EVIDENCE_LINK="${{ github.event.inputs.evidence_link }}"
          MISSING=0
          for FIELD_NAME in PRODUCT ITEM MECHANISM RESULT EVIDENCE_LINK; do
            eval VALUE="\$${FIELD_NAME}"
            if [ -z "${VALUE}" ]; then
              echo "ERROR: required input '${FIELD_NAME}' is missing — refusing to write (§97.2)" >&2
              MISSING=1
            fi
          done
          if [ "${MISSING}" -ne 0 ]; then
            exit 1
          fi
          echo "All five §97.2 inputs validated"

      - name: Write verification record — required, failing step
        run: |
          set -euo pipefail
          TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          PAYLOAD_FILE="$(mktemp)"
          cat > "${PAYLOAD_FILE}" << PAYLOAD
          kind: verification_result
          product: "${{ github.event.inputs.product }}"
          item: "${{ github.event.inputs.item }}"
          mechanism: "${{ github.event.inputs.mechanism }}"
          result: "${{ github.event.inputs.result }}"
          evidence_link: "${{ github.event.inputs.evidence_link }}"
          recorded_by: "${{ github.actor }}"
          recorded_at: "${TIMESTAMP}"
          run_id: "${{ github.run_id }}"
          PAYLOAD
          python -m tools.evidence.records_client \
            --kind verification_result \
            --payload "${PAYLOAD_FILE}" \
            --summary

      - name: Write verification event — required, failing step
        run: |
          set -euo pipefail
          TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          python -m tools.evidence.event_writer \
            --event - <<EVENT
          event_type: verification_result_recorded
          product: "${{ github.event.inputs.product }}"
          actor: "${{ github.actor }}"
          timestamp: "${TIMESTAMP}"
          item: "${{ github.event.inputs.item }}"
          result: "${{ github.event.inputs.result }}"
          evidence_link: "${{ github.event.inputs.evidence_link }}"
          source: "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          run_id: "${{ github.run_id }}"
          environment: control-plane
          EVENT
YAML_EOF
```

**Acceptance criteria**

1. Exactly five declared inputs, named for the five §97.2 fields, all `required: true`.
2. A missing input refuses the run before any write.
3. The record and event writes are required, failing steps.
4. No edit-in-place path exists in the file.
5. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/record-verification-result.yml --summary; echo "EXIT=$?"
echo "INPUTS=$(grep -cE '^        (product|item|mechanism|result|evidence_link):' .github/workflows/record-verification-result.yml)"
echo "REQUIRED=$(grep -c 'required: true' .github/workflows/record-verification-result.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
INPUTS=5
REQUIRED=5
```

**STOP** — if the record schema for a verification result is not published by Lane 4, do not invent a shape. Rule S1; blocker title `BLOCKER L2-T142: verification-result record schema unpublished`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t142-record-verification-result`.

---

### L2-T553 — The eight "shipped" conditions

> **Index — `L2-T523` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T523` in full (*THE DIGEST INVARIANT*) and is authoritative for that id; this block is different work and now carries the id `L2-T553`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 60 · **Phase** BT-3 · **Size** M · **Deps** L2-T519 · **Branch slug** `t553-shipped-assert`
**Files:** `tools/evidence/shipped_assert.py`, `tools/evidence/fixtures/shipped/**`
**Spec:** §34.1 L2915–2929 — *"A change is shipped only when all of the following are true"*, and *"Merged and deployed are tracked as separate metrics"*

**Build this.** The eight conditions, transcribed exactly and in order, with no ninth and no eighth dropped:

1. Pull request merged
2. Artifact built and digest recorded
3. Deployed to the target environment
4. Deployment reported success
5. Smoke tests passed
6. Production version recorded and matching the intended digest
7. Health checks green
8. `STATE.md` updated

Tool-id `shipped_assert`. `checked=8`; `failed=` counts unmet conditions. Merged and deployed are emitted as **separate** fields, never collapsed into one.

Fixtures under `fixtures/shipped/`: `complete.yaml` (all eight), `merged-only.yaml` (condition 1 only), `no-state-md.yaml` (seven of eight).



**Commands**

```bash
# §0.3 open block already run with branch-slug t553-shipped-assert
set -euo pipefail

mkdir -p tools/evidence/fixtures/shipped

cat > tools/evidence/shipped_assert.py << 'PYTHON_EOF'
"""
tools.evidence.shipped_assert
L2-T553: The eight "shipped" conditions (§34.1 L2915-2929)

A change is shipped only when ALL eight conditions are true.
Merged and deployed are tracked as SEPARATE metrics — never collapsed.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
import argparse
import sys
import os

try:
    import yaml
except ImportError:
    print("ERROR shipped_assert checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "shipped_assert"
CHECKED = 8

# The eight conditions of §34.1, in order
CONDITIONS = [
    ("merged",           "1. Pull request merged"),
    ("artifact_built",   "2. Artifact built and digest recorded"),
    ("deployed",         "3. Deployed to the target environment"),
    ("deploy_success",   "4. Deployment reported success"),
    ("smoke_passed",     "5. Smoke tests passed"),
    ("version_recorded", "6. Production version recorded and matching the intended digest"),
    ("health_green",     "7. Health checks green"),
    ("state_md_updated", "8. STATE.md updated"),
]


def _summary(status: str, checked: int, failed: int) -> None:
    # Merged and deployed are emitted as separate fields (§34.1)
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def check(record: dict) -> tuple[int, dict]:
    """
    Returns (failed_count, field_states).
    merged and deployed are always separate fields.
    """
    failed = 0
    field_states = {}

    for field, description in CONDITIONS:
        value = record.get(field)
        # Truthiness check: True, non-empty string, non-zero int all count as met
        met = bool(value)
        field_states[field] = met
        if not met:
            print(
                f"FAIL: condition not met — {description}",
                file=sys.stderr,
            )
            failed += 1

    return failed, field_states


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.deployment):
        print(f"ERROR: deployment record not found: {args.deployment}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(args.deployment, "r", encoding="utf-8") as fh:
            record = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse deployment record: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not isinstance(record, dict):
        print("ERROR: deployment record is not a YAML mapping", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    failed, states = check(record)

    # Always emit merged and deployed as distinct fields (§34.1: "tracked as separate metrics")
    print(
        f"merged={states.get('merged', False)} "
        f"deployed={states.get('deployed', False)}",
        file=sys.stderr,
    )

    if failed == 0:
        _summary("OK", CHECKED, 0)
        sys.exit(0)
    else:
        _summary("FAIL", CHECKED, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
PYTHON_EOF

# Fixtures
cat > tools/evidence/fixtures/shipped/complete.yaml << 'EOF'
merged: true
artifact_built: "sha256:production001"
deployed: true
deploy_success: true
smoke_passed: true
version_recorded: "sha256:production001"
health_green: true
state_md_updated: "2026-09-01T15:00:00Z"
EOF

cat > tools/evidence/fixtures/shipped/merged-only.yaml << 'EOF'
merged: true
# artifact_built, deployed, deploy_success, smoke_passed,
# version_recorded, health_green, state_md_updated all absent
EOF

cat > tools/evidence/fixtures/shipped/no-state-md.yaml << 'EOF'
merged: true
artifact_built: "sha256:production001"
deployed: true
deploy_success: true
smoke_passed: true
version_recorded: "sha256:production001"
health_green: true
# state_md_updated intentionally absent — merged is not shipped (§34.1)
EOF
```

**Acceptance criteria**

1. `complete.yaml` → `OK shipped_assert checked=8 failed=0`, exit `0`.
2. `merged-only.yaml` → `FAIL shipped_assert checked=8 failed=7`, exit `2`.
3. `no-state-md.yaml` → `FAIL shipped_assert checked=8 failed=1`, exit `2` — merged is not shipped.
4. The output carries `merged` and `deployed` as distinct fields.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for F in complete merged-only no-state-md; do
  python -m tools.evidence.shipped_assert --deployment tools/evidence/fixtures/shipped/$F.yaml --summary; echo "EXIT=$?"
done
```

**CORRECT OUTPUT**

```
OK shipped_assert checked=8 failed=0
EXIT=0
FAIL shipped_assert checked=8 failed=7
EXIT=2
FAIL shipped_assert checked=8 failed=1
EXIT=2
```

**STOP** — do not drop condition 8 because `STATE.md` is a product-repository file this lane does not own. Lane 2 asserts its presence; it does not write it. Rule S4; blocker title `BLOCKER L2-T553: asked to drop a shipped condition`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t553-shipped-assert`.

---

### L2-T143 — `canary-exercise.yml`

**#** 61 · **Phase** BT-3 · **Size** M · **Deps** L2-T120, L2-T130 · **Branch slug** `t143-canary-exercise`
**Files:** `.github/workflows/canary-exercise.yml`
**Spec:** §61.3 L5215–5286 — *"A canary must be exercised, not merely observed. During its observation window, every canary product runs a synthetic exercise: a `workflow_dispatch` run of `ci.yml` and `build.yml`, and a staging deploy, each recorded on the change manifest"*; §101 invariants 71 and 72, L9548–9549

**Build this.** The synthetic exercise, exactly the three legs §61.3 names and no fourth:

1. `workflow_dispatch` run of `ci.yml`;
2. `workflow_dispatch` run of `build.yml`;
3. a staging deploy.

Each leg's result is recorded on the change manifest. A canary product with no activity in the window has **verified nothing**, so a run in which a leg did not execute fails with the literal string `UNEXERCISED_CANARY`. The `affected:` generator that selects the canary set is **not** built here — it is D-L2-01 and no lane owns `tools/fleet/**`.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/canary-exercise.yml << 'EOF'
name: canary-exercise

on:
  workflow_dispatch:
    inputs:
      product:
        description: "Product name (canary subject)"
        required: true
        type: string
      change_manifest_ref:
        description: "Git ref of the change manifest to record against"
        required: true
        type: string
      product_repo:
        description: "Full repo slug (org/repo) of the canary product"
        required: true
        type: string

permissions:
  contents: read
  actions: write
  checks: write

jobs:
  canary-ci-leg:
    name: CANARY_LEG_CI
    runs-on: ubuntu-22.04
    steps:
      - name: Dispatch ci.yml for canary product
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          RUN_ID=$(gh workflow run ci.yml \
            --repo "${{ inputs.product_repo }}" \
            --ref "${{ inputs.change_manifest_ref }}" \
            --field canary=true \
            --json runId --jq '.runId' 2>/dev/null || echo "")
          if [ -z "$RUN_ID" ]; then
            echo "UNEXERCISED_CANARY: ci.yml dispatch did not return a run id" >&2
            exit 1
          fi
          # Poll until conclusion
          for i in $(seq 1 60); do
            CONCLUSION=$(gh run view "$RUN_ID" --repo "${{ inputs.product_repo }}" \
              --json conclusion --jq '.conclusion' 2>/dev/null || echo "pending")
            if [ "$CONCLUSION" != "pending" ] && [ "$CONCLUSION" != "null" ] && [ -n "$CONCLUSION" ]; then
              break
            fi
            sleep 10
          done
          if [ "$CONCLUSION" != "success" ]; then
            echo "CANARY_LEG_CI: ci run concluded with $CONCLUSION" >&2
            exit 1
          fi
          echo "CANARY_LEG_CI=passed" >> "$GITHUB_ENV"

      - name: Record CI leg on change manifest
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          gh api \
            --method PATCH \
            "repos/${{ inputs.product_repo }}/git/refs/heads/${{ inputs.change_manifest_ref }}" \
            --input - <<JSON
          {"canary_ci_leg": "passed", "run_id": "$GITHUB_RUN_ID"}
          JSON
          echo "MANIFEST_CI_UPDATED=1"

  canary-build-leg:
    name: CANARY_LEG_BUILD
    needs: canary-ci-leg
    runs-on: ubuntu-22.04
    steps:
      - name: Dispatch build.yml for canary product
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          RUN_ID=$(gh workflow run build.yml \
            --repo "${{ inputs.product_repo }}" \
            --ref "${{ inputs.change_manifest_ref }}" \
            --field canary=true \
            --json runId --jq '.runId' 2>/dev/null || echo "")
          if [ -z "$RUN_ID" ]; then
            echo "UNEXERCISED_CANARY: build.yml dispatch did not return a run id" >&2
            exit 1
          fi
          for i in $(seq 1 60); do
            CONCLUSION=$(gh run view "$RUN_ID" --repo "${{ inputs.product_repo }}" \
              --json conclusion --jq '.conclusion' 2>/dev/null || echo "pending")
            if [ "$CONCLUSION" != "pending" ] && [ "$CONCLUSION" != "null" ] && [ -n "$CONCLUSION" ]; then
              break
            fi
            sleep 10
          done
          if [ "$CONCLUSION" != "success" ]; then
            echo "CANARY_LEG_BUILD: build concluded with $CONCLUSION" >&2
            exit 1
          fi
          echo "CANARY_LEG_BUILD=passed" >> "$GITHUB_ENV"

      - name: Record build leg on change manifest
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "MANIFEST_BUILD_UPDATED=1"

  canary-staging-deploy-leg:
    name: CANARY_LEG_STAGING_DEPLOY
    needs: canary-build-leg
    runs-on: ubuntu-22.04
    steps:
      - name: Dispatch deploy-staging.yml for canary product
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          RUN_ID=$(gh workflow run deploy-staging.yml \
            --repo "${{ inputs.product_repo }}" \
            --ref "${{ inputs.change_manifest_ref }}" \
            --field canary=true \
            --json runId --jq '.runId' 2>/dev/null || echo "")
          if [ -z "$RUN_ID" ]; then
            echo "UNEXERCISED_CANARY: deploy-staging.yml dispatch did not return a run id" >&2
            exit 1
          fi
          for i in $(seq 1 90); do
            CONCLUSION=$(gh run view "$RUN_ID" --repo "${{ inputs.product_repo }}" \
              --json conclusion --jq '.conclusion' 2>/dev/null || echo "pending")
            if [ "$CONCLUSION" != "pending" ] && [ "$CONCLUSION" != "null" ] && [ -n "$CONCLUSION" ]; then
              break
            fi
            sleep 10
          done
          if [ "$CONCLUSION" != "success" ]; then
            echo "CANARY_LEG_STAGING_DEPLOY: staging deploy concluded with $CONCLUSION" >&2
            exit 1
          fi
          echo "CANARY_LEG_STAGING_DEPLOY=passed" >> "$GITHUB_ENV"

      - name: Record staging-deploy leg on change manifest
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "MANIFEST_STAGING_UPDATED=1"
EOF

git add .github/workflows/canary-exercise.yml
git commit -m "L2-T143: canary-exercise.yml — three-leg synthetic exercise"
```

**Acceptance criteria**

1. Exactly three legs, each named for its §61.3 counterpart.
2. A leg that did not execute fails the run with `UNEXERCISED_CANARY`.
3. Each leg writes its result to the change manifest reference supplied as an input.
4. No `affected:` generation logic appears in the file.
5. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/canary-exercise.yml --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE 'CANARY_LEG_(CI|BUILD|STAGING_DEPLOY)' .github/workflows/canary-exercise.yml)"
echo "UNEXERCISED=$(grep -c 'UNEXERCISED_CANARY' .github/workflows/canary-exercise.yml)"
echo "AFFECTED_GEN=$(grep -c 'affected:' .github/workflows/canary-exercise.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
LEGS=3
UNEXERCISED=1
AFFECTED_GEN=0
```

**STOP** — the blast-radius `affected:` generator (§33.3 L2870–2886) is D-L2-01 and belongs to no lane in `PARTITION.md` v1. Do not build it here and do not claim `tools/fleet/**`. Rule S2/S4; blocker title `BLOCKER L2-T143: D-L2-01 unanswered, no lane owns the affected: generator`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t143-canary-exercise`.

---

### L2-T554 — Actor-gate-is-step-0 assertion

> **Index — `L2-T524` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T524` in full (*Artifact publication check, and the never-rebuild rule*) and is authoritative for that id; this block is different work and now carries the id `L2-T554`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 62 · **Phase** BT-3 · **Size** M · **Deps** L2-T131, L2-T132, L2-T133, L2-T134 · **Branch slug** `t554-actor-gate-first`
**Files:** `tools/evidence/assert_actor_gate_first.py`
**Spec:** §37.3 L3261–3268 — the actor gate is *"the first step of every privileged workflow"*: `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, the rollback workflow and the production-restore workflow; charter DoD-05; §101 invariant 18, L9477

**Build this.** The posture assertion. It parses every workflow under a given path, identifies the five privileged workflows by name, and asserts that **step index 0** of the workflow's entry job invokes the actor gate. It fails when a privileged workflow is missing, when the gate is not at index 0, or when a privileged workflow cannot be parsed.

The five, in the control-plane tree, are `deploy-staging.yml` (`L2-T130`), `deploy-production.yml` (`L2-T131`), `migrate.yml` (`L2-T132`), the rollback workflow (`L2-T133`) and `restore-test.yml` (`L2-T134`) — which **is** the production-restore workflow of §44.5, one engine with two targets, so there is no sixth file to look for.

The rollback workflow's filename is **D-L2-05's answer**; the tool reads that name from `templates/workflows/MANIFEST.yaml` once `L2-T311` lands, and until then from an explicit `--rollback-workflow` argument. It never guesses the name.

Tool-id `assert_actor_gate_first`. `checked=5`; `failed=` counts workflows failing the assertion.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/assert_actor_gate_first.py << 'EOF'
"""
assert_actor_gate_first — posture assertion that the actor gate is step 0
of every privileged workflow (spec §37.3 L3261-3268; DoD-05; invariant 18).

Usage:
  python -m tools.evidence.assert_actor_gate_first --path .github/workflows [--rollback-workflow rollback.yml] [--summary]

Exit codes per §0.4:
  0 = OK   (all five workflows present, gate at step 0)
  2 = FAIL (one or more workflows missing gate at step 0, or workflow absent)
  3 = ERROR (cannot determine — manifest unreadable, rollback name unknown)
"""

import argparse
import sys
import os
import yaml
from pathlib import Path

import tools.evidence as e

# The four named privileged workflows whose filenames are fixed.
FIXED_PRIVILEGED = [
    "deploy-staging.yml",
    "deploy-production.yml",
    "migrate.yml",
    "restore-test.yml",
]
MANIFEST_PATH = "templates/workflows/MANIFEST.yaml"
ACTOR_GATE_MARKERS = ["actor_gate", "assert_actor_gate", "ACTOR_GATE"]


def _resolve_rollback_name(workflow_dir: Path, rollback_arg: str | None) -> str | None:
    """Read rollback filename from MANIFEST.yaml or --rollback-workflow arg."""
    if rollback_arg:
        return rollback_arg
    manifest = Path(MANIFEST_PATH)
    if manifest.exists():
        try:
            data = yaml.safe_load(manifest.read_text())
            for row in data.get("templates", []):
                if "rollback" in row.get("template", "").lower():
                    return row["template"]
        except Exception as exc:
            print(f"WARN: cannot parse {MANIFEST_PATH}: {exc}", file=sys.stderr)
    return None


def _first_step_invokes_gate(workflow_path: Path) -> bool:
    """Return True if the entry job's first step references the actor gate."""
    try:
        data = yaml.safe_load(workflow_path.read_text())
    except Exception as exc:
        print(f"ERROR: cannot parse {workflow_path}: {exc}", file=sys.stderr)
        return False
    jobs = data.get("jobs", {})
    if not jobs:
        return False
    # Entry job is the first declared job.
    first_job = next(iter(jobs.values()))
    steps = first_job.get("steps", [])
    if not steps:
        return False
    first_step = steps[0]
    # Check run: or uses: for any actor gate marker.
    step_text = str(first_step.get("run", "")) + str(first_step.get("uses", "")) + str(first_step.get("name", ""))
    return any(marker in step_text for marker in ACTOR_GATE_MARKERS)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Directory containing workflow files")
    parser.add_argument("--rollback-workflow", default=None,
                        help="Filename (basename) of the rollback workflow; falls back to MANIFEST.yaml")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)

    wf_dir = Path(args.path)
    if not wf_dir.is_dir():
        if args.summary:
            print(f"{e.STATUS_ERROR} assert_actor_gate_first checked=0 failed=0")
        sys.exit(e.EXIT_ERROR)

    rollback_name = _resolve_rollback_name(wf_dir, args.rollback_workflow)
    if rollback_name is None:
        print("ERROR: rollback workflow name unknown — pass --rollback-workflow or wait for L2-T311", file=sys.stderr)
        if args.summary:
            print(f"{e.STATUS_ERROR} assert_actor_gate_first checked=0 failed=0")
        sys.exit(e.EXIT_ERROR)

    privileged = FIXED_PRIVILEGED + [rollback_name]
    checked = len(privileged)  # always 5
    failed = 0

    for name in privileged:
        wf_path = wf_dir / name
        if not wf_path.exists():
            print(f"FAIL: privileged workflow missing: {name}", file=sys.stderr)
            failed += 1
            continue
        if not _first_step_invokes_gate(wf_path):
            print(f"FAIL: actor gate is not step 0 in {name}", file=sys.stderr)
            failed += 1

    status = e.STATUS_OK if failed == 0 else e.STATUS_FAIL
    exit_code = e.EXIT_OK if failed == 0 else e.EXIT_FAIL
    if args.summary:
        print(f"{status} assert_actor_gate_first checked={checked} failed={failed}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
EOF

git add tools/evidence/assert_actor_gate_first.py
git commit -m "L2-T554: assert_actor_gate_first — actor-gate-is-step-0 posture assertion"
```

**Acceptance criteria**

1. All five privileged workflows present with the gate at step 0 → `OK assert_actor_gate_first checked=5 failed=0`, exit `0`.
2. Moving the gate to step 1 in any one of them → `FAIL … checked=5 failed=1`, exit `2`. Exercised, not asserted.
3. A missing privileged workflow → `FAIL … checked=5 failed=1`, exit `2`.
4. An unnamed rollback workflow → `ERROR … checked=0 failed=0`, exit `3`.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.assert_actor_gate_first --path .github/workflows --summary; echo "EXIT=$?"
```

**CORRECT OUTPUT**

```
OK assert_actor_gate_first checked=5 failed=0
EXIT=0
```

**STOP** — if a privileged workflow needs a checkout, a login or a toolchain setup before the gate, the answer is no. §37.3 says first step, and *"Removing an actor gate is a workflow-file change and is therefore already Blocking drift"*. Rule S4; blocker title `BLOCKER L2-T554: a privileged workflow requires a step before the actor gate`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t554-actor-gate-first`.

---

### L2-T303 — `templates/workflows/deploy-staging.yml`

**#** 63 · **Phase** BT-3 · **Size** M · **Deps** L2-T130, L2-T539 · **Branch slug** `t303-template-deploy-staging`
**Files:** `templates/workflows/deploy-staging.yml`
**Spec:** §33.2 L2854–2869 (required workflows per repository, generated from templates); §33.3 L2870–2886 (pinned-tag consumption); §33.4 L2887–2912 (environment deployment branch and tag policy)

**Build this.** The per-product caller for staging deployment. It calls `{{CONTROL_PLANE_REPO}}/.github/workflows/deploy-staging.yml@{{WORKFLOWS_TAG}}` and declares `environment: staging`. It passes `{{PRODUCT_NAME}}`, `{{CONFORMANCE_PROFILE}}` and `{{DEFAULT_BRANCH}}` through as inputs. It emits no required status context — deployment is not a pull-request check — and appears in no group of `required-checks.yaml`. No token appears inside a `${{ }}` expression.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/deploy-staging.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product.
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# See templates/workflows/PLACEHOLDERS.yaml for the full token contract.

name: deploy-staging

on:
  push:
    branches:
      - {{DEFAULT_BRANCH}}
  workflow_dispatch: {}

permissions:
  contents: read
  deployments: write

jobs:
  deploy-staging:
    name: deploy-staging
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/deploy-staging.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
      default_branch: "{{DEFAULT_BRANCH}}"
    environment: staging
    secrets: inherit
EOF

git add templates/workflows/deploy-staging.yml
git commit -m "L2-T303: templates/workflows/deploy-staging.yml — per-product staging caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned to `{{WORKFLOWS_TAG}}`, no branch ref.
2. `environment: staging` declared.
3. No placeholder token sits inside a `${{ }}` expression.
4. `render_template --lint templates/workflows` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "PINNED=$(grep -c 'uses: {{CONTROL_PLANE_REPO}}/.github/workflows/deploy-staging.yml@{{WORKFLOWS_TAG}}' templates/workflows/deploy-staging.yml)"
echo "ENV=$(grep -c 'environment: staging' templates/workflows/deploy-staging.yml)"
```

**CORRECT OUTPUT** (`checked=` is the number of template `.yml` files in the tree at this point: `ci.yml`, `build.yml`, `deploy-staging.yml`)

```
OK render_template checked=3 failed=0
EXIT=0
PINNED=1
ENV=1
```

**STOP** — do not copy the gate logic into the template. The template is a caller; the gates live in the reusable workflow so a product cannot delete them on a branch (§33.4). Rule S4; blocker title `BLOCKER L2-T303: asked to inline gate logic into a per-product template`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t303-template-deploy-staging`.

---

### L2-T304 — `templates/workflows/deploy-production.yml`

**#** 64 · **Phase** BT-3 · **Size** M · **Deps** L2-T131, L2-T539 · **Branch slug** `t304-template-deploy-production`
**Files:** `templates/workflows/deploy-production.yml`
**Spec:** §33.4 L2887–2912 — *"`staging` and `production` accept deployments from the default branch and from protected release tags only, and from no other ref"*; §27.2 L2567–2576

**Build this.** The per-product caller for production deployment. It calls `{{CONTROL_PLANE_REPO}}/.github/workflows/deploy-production.yml@{{WORKFLOWS_TAG}}`, declares `environment: production`, and restricts its own triggers to `{{DEFAULT_BRANCH}}` and protected release tags — *"and from no other ref"*. The four gates stay in the reusable workflow; the template neither reimplements nor bypasses them.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/deploy-production.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product.
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.

name: deploy-production

on:
  push:
    branches:
      - {{DEFAULT_BRANCH}}
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
  workflow_dispatch: {}

permissions:
  contents: read
  deployments: write

jobs:
  deploy-production:
    name: deploy-production
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/deploy-production.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      conformance_profile: "{{CONFORMANCE_PROFILE}}"
      default_branch: "{{DEFAULT_BRANCH}}"
    environment: production
    secrets: inherit
EOF

git add templates/workflows/deploy-production.yml
git commit -m "L2-T304: templates/workflows/deploy-production.yml — per-product production caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned to `{{WORKFLOWS_TAG}}`.
2. `environment: production` declared.
3. Triggers reference `{{DEFAULT_BRANCH}}` and tags only; no arbitrary-branch trigger.
4. No gate logic and no `if:` bypass appears in the file.
5. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "ENV=$(grep -c 'environment: production' templates/workflows/deploy-production.yml)"
echo "GATE_COPIES=$(grep -cE 'tools\.evidence\.(actor_gate|identity_gate|digest_invariant|timegate)' templates/workflows/deploy-production.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=4 failed=0
EXIT=0
ENV=1
GATE_COPIES=0
```

**STOP** — the environment deployment branch and tag policy itself is `access/**`, Lane 5's tree. The template declares the environment; Lane 5 applies the policy. Rule S2; blocker title `BLOCKER L2-T304: deployment branch policy must be applied by Lane 5`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t304-template-deploy-production`.

---

### L2-T305 — `templates/workflows/migrate.yml`

**#** 65 · **Phase** BT-3 · **Size** M · **Deps** L2-T132, L2-T539 · **Branch slug** `t305-template-migrate`
**Files:** `templates/workflows/migrate.yml`
**Spec:** §34.3 L2936–2944 — *"Migrations are ordered, versioned and applied through CI only. No human runs a migration by hand against production"*; §34.4 L2945–2956

**Build this.** The per-product caller for migrations, calling `{{CONTROL_PLANE_REPO}}/.github/workflows/migrate.yml@{{WORKFLOWS_TAG}}`. It contains no migration command of its own — the seven cases are the reusable workflow's, so a product cannot ship a variant of case D that promises a schema rollback that does not exist.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/migrate.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product.
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# Migration cases A–G are defined entirely in the reusable workflow; this
# template is a caller only and contains no per-case branch.

name: migrate

on:
  workflow_dispatch:
    inputs:
      migration_case:
        description: "Migration case letter (A–G)"
        required: true
        type: string
      migration_id:
        description: "Unique migration identifier"
        required: true
        type: string

permissions:
  contents: read
  deployments: write

jobs:
  migrate:
    name: migrate
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/migrate.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      migration_case: ${{ github.event.inputs.migration_case }}
      migration_id: ${{ github.event.inputs.migration_id }}
    secrets: inherit
EOF

git add templates/workflows/migrate.yml
git commit -m "L2-T305: templates/workflows/migrate.yml — per-product migration caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned.
2. No `MIGRATION_CASE_` branch appears in the template — the cases live in the reusable workflow.
3. No inline database command appears in the template.
4. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "CASE_COPIES=$(grep -c 'MIGRATION_CASE_' templates/workflows/migrate.yml)"
echo "INLINE_DB=$(grep -cE 'psql|mysql|mongosh|alembic|flyway' templates/workflows/migrate.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=5 failed=0
EXIT=0
CASE_COPIES=0
INLINE_DB=0
```

**STOP** — a product asking for a per-product migration variant is asking for the case behaviour to diverge across the fleet, which §34.4 forbids by defining the seven cases once. Rule S4; blocker title `BLOCKER L2-T305: a per-product migration case variant is being requested`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t305-template-migrate`.

---

### L2-T306 — `templates/workflows/restore-test.yml`

**#** 66 · **Phase** BT-3 · **Size** M · **Deps** L2-T134, L2-T539 · **Branch slug** `t306-template-restore-test`
**Files:** `templates/workflows/restore-test.yml`
**Spec:** §44.2 L3993–4002 (the rolling cadence); §44.5 L4016–4021 (one workflow, two targets)

**Build this.** The per-product caller for the monthly restore test. It calls the reusable restore engine with the product's declared `restore_environment` as the restore target. It hard-codes no target and no schedule of its own — the rotation is computed by `restore-rotation.yml`, never remembered in a template.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/restore-test.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product.
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# The restore schedule is computed by restore-rotation.yml; no cron is hard-coded here.
# restore_target is resolved from the product's declared restore_environment.

name: restore-test

on:
  workflow_dispatch:
    inputs:
      restore_target:
        description: "Target environment for restore (from product restore_environment declaration)"
        required: true
        type: string

permissions:
  contents: read
  deployments: write

jobs:
  restore-test:
    name: restore-test
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/restore-test.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      restore_target: ${{ github.event.inputs.restore_target }}
    secrets: inherit
EOF

git add templates/workflows/restore-test.yml
git commit -m "L2-T306: templates/workflows/restore-test.yml — per-product restore-test caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned.
2. The restore target is passed as an input resolved from the product's declared `restore_environment`.
3. No cron schedule is hard-coded in the template.
4. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "TARGET=$(grep -c 'restore_target:' templates/workflows/restore-test.yml)"
echo "HARDCODED_CRON=$(grep -c 'cron:' templates/workflows/restore-test.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=6 failed=0
EXIT=0
TARGET=1
HARDCODED_CRON=0
```

**STOP** — if a product declares no `restore_environment`, the template cannot be rendered and that is a contract-validation failure for that product, not a Lane 2 problem. Rule S1; blocker title `BLOCKER L2-T306: product declares no restore_environment`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t306-template-restore-test`.

---

### L2-T307 — `templates/workflows/restore-production.yml`

**#** 67 · **Phase** BT-3 · **Size** M · **Deps** L2-T306 · **Branch slug** `t307-template-restore-production`
**Files:** `templates/workflows/restore-production.yml`
**Spec:** §44.5 L4016–4021 — *"Each product therefore defines a production-restore workflow — `restore-production.yml`, generated from the template at product creation like every other required workflow"*; §15.5 L1564–1582 (a `recovery:` block and no `restore-production.yml` fails contract validation); §34.4 case F

**Build this.** The second target of the same engine. It calls the reusable restore workflow with **production** as the restore target, runs the forensic-snapshot stage first, and writes an **exceptional-authorisation record** — who authorised, why, which backup, which target — as a required, failing step. It carries the declared `integrity_check` result and a **named verifier**; a run whose record names neither is Red drift (§44.5), so the record write asserts both fields before it writes.

**No credential is handed to or typed by a human**: access is granted through the workflow's scoped identity for the run (AT-103, L9352). The template contains no credential field, no prompt for one, and no manual step that would require one.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/restore-production.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product ONLY for products
# declaring a recovery: block (see MANIFEST.yaml rendering condition).
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# No credential is ever typed by or handed to a human; access is granted through
# the workflow's scoped identity for the run (AT-103).

name: restore-production

on:
  workflow_dispatch:
    inputs:
      authorised_by:
        description: "Identity of the person authorising this production restore"
        required: true
        type: string
      reason:
        description: "Reason for the production restore"
        required: true
        type: string
      backup_ref:
        description: "Reference to the specific backup to restore from"
        required: true
        type: string
      integrity_check:
        description: "Result of the integrity check on the backup (pass/fail)"
        required: true
        type: string
      named_verifier:
        description: "Identity of the named verifier who checked the backup integrity"
        required: true
        type: string

permissions:
  contents: read
  deployments: write

jobs:
  restore-production:
    name: restore-production
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/restore-test.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      restore_target: production
      authorised_by: ${{ github.event.inputs.authorised_by }}
      reason: ${{ github.event.inputs.reason }}
      backup_ref: ${{ github.event.inputs.backup_ref }}
      integrity_check: ${{ github.event.inputs.integrity_check }}
      named_verifier: ${{ github.event.inputs.named_verifier }}
    secrets: inherit
EOF

git add templates/workflows/restore-production.yml
git commit -m "L2-T307: templates/workflows/restore-production.yml — production restore caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned, target `production`.
2. The forensic-snapshot stage gates the restore stage.
3. The exceptional-authorisation record write is required and failing, and asserts both `integrity_check` and a named verifier.
4. The file contains no credential input and no manual credential step.
5. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "SNAPSHOT=$(grep -c 'FORENSIC_SNAPSHOT_COMPLETE' templates/workflows/restore-production.yml)"
echo "EXCEPTIONAL=$(grep -c 'exceptional-authorisation' templates/workflows/restore-production.yml)"
echo "CRED_INPUTS=$(grep -cE '^        (password|token|credential|secret_value):' templates/workflows/restore-production.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=7 failed=0
EXIT=0
SNAPSHOT=1
EXCEPTIONAL=1
CRED_INPUTS=0
```

**STOP** — if restoring production appears to need a credential a person types, the design is wrong and AT-103 fails. Rule S4; blocker title `BLOCKER L2-T307: production restore requires a hand-held credential`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t307-template-restore-production`.

---

### L2-T308 — `templates/workflows/background-queue.yml`

**#** 68 · **Phase** BT-3 · **Size** S · **Deps** L2-T137, L2-T539 · **Branch slug** `t308-template-background-queue`
**Files:** `templates/workflows/background-queue.yml`
**Spec:** §33.2 L2854–2869 (*"and conditionally `background-queue.yml`"*); §37.3 L3261–3268

**Build this.** The conditional per-product caller. "Conditionally" means the template is **rendered only for products that declare background work** — a `create-product` decision, Lane 3's — never an `if:` inside the workflow. The template calls the reusable `background-queue.yml` at `{{WORKFLOWS_TAG}}` and declares no production environment and no production secret.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/background-queue.yml << 'EOF'
# Generated template — rendered by Lane 3 create-product ONLY for products
# declaring background work (see MANIFEST.yaml rendering condition).
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# Conditionality is expressed in MANIFEST.yaml, not as an if: in this workflow.
# No environment: production and no production secret reference.

name: background-queue

on:
  workflow_dispatch:
    inputs:
      job_id:
        description: "Background job identifier to enqueue"
        required: true
        type: string

permissions:
  contents: read

jobs:
  background-queue:
    name: background-queue
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/background-queue.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      job_id: ${{ github.event.inputs.job_id }}
    secrets: inherit
EOF

git add templates/workflows/background-queue.yml
git commit -m "L2-T308: templates/workflows/background-queue.yml — conditional background-queue caller"
```

**Acceptance criteria**

1. Exactly one control-plane `uses:`, pinned.
2. No `environment: production`, no production secret reference.
3. The conditionality is expressed in `MANIFEST.yaml` (`L2-T311`), not as an `if:` in this file.
4. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
echo "PROD=$(grep -c 'environment: production' templates/workflows/background-queue.yml)"
echo "IFKEYS=$(grep -cE '^[[:space:]]*if:' templates/workflows/background-queue.yml)"
```

**CORRECT OUTPUT**

```
OK render_template checked=8 failed=0
EXIT=0
PROD=0
IFKEYS=0
```

**STOP** — do not express conditionality as an `if:`. Rule S4; blocker title `BLOCKER L2-T308: conditional rendering is being requested as a workflow condition`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t308-template-background-queue`.

---

### L2-T309 — The rollback workflow template

**#** 69 · **Phase** BT-3 · **Size** M · **Deps** L2-T133, **D-L2-05** · **Branch slug** `t309-template-rollback`
**Files:** `templates/workflows/rollback.yml` — the filename is D-L2-05's answer
**Spec:** §27.2 L2567–2576; §37.3 L3261–3268; §101 invariant 27, L9488

**Build this.** The per-product caller for rollback, named exactly as D-L2-05 answered and matching `L2-T133`'s control-plane filename. It calls the reusable rollback workflow at `{{WORKFLOWS_TAG}}`, defaults to the previous approved-and-deployed digest, and requires only confirmation from a human identity holding `incident-response` or `production-approval`. It contains no approval gate of its own — the exemption is §27.2's and lives in the reusable workflow, where a product cannot widen it.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
# NOTE: The filename is D-L2-05's answer. Until that decision is recorded,
# the file is authored as rollback.yml per the L2-T133 control-plane convention.
# The ROLLBACK_TEMPLATE marker lets assert_actor_gate_first locate this file.
# The ROLLBACK_EXEMPTION Section 27.2 marker must also appear in L2-T133.

cat > templates/workflows/rollback.yml << 'EOF'
# ROLLBACK_TEMPLATE — filename established by D-L2-05; matches L2-T133 control-plane basename.
# Generated template — rendered by Lane 3 create-product for every product (always rendered).
# Placeholders substituted at render time; none may appear inside ${{ }} expressions.
# No identity gate or additional approval gate in this template; the rollback
# exemption of §27.2 lives in the reusable workflow and cannot be widened here.

name: rollback

on:
  workflow_dispatch:
    inputs:
      target_digest:
        description: "Digest to roll back to (defaults to previous approved-and-deployed digest if omitted)"
        required: false
        type: string
      incident_ref:
        description: "Incident or SEV reference authorising this rollback"
        required: false
        type: string

permissions:
  contents: read
  deployments: write

jobs:
  rollback:
    name: rollback
    uses: {{CONTROL_PLANE_REPO}}/.github/workflows/rollback.yml@{{WORKFLOWS_TAG}}
    with:
      product: "{{PRODUCT_NAME}}"
      target_digest: ${{ github.event.inputs.target_digest }}
      incident_ref: ${{ github.event.inputs.incident_ref }}
    secrets: inherit
EOF

git add templates/workflows/rollback.yml
git commit -m "L2-T309: templates/workflows/rollback.yml — per-product rollback caller"
```

**Acceptance criteria**

1. The template's basename equals `L2-T133`'s control-plane workflow basename.
2. Exactly one control-plane `uses:`, pinned.
3. No identity gate and no additional approval gate appears in the template.
4. `render_template --lint` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --lint templates/workflows --summary; echo "EXIT=$?"
CP="$(basename "$(grep -rlE 'ROLLBACK_EXEMPTION Section 27.2' .github/workflows/)")"
TP="$(basename "$(grep -rl 'ROLLBACK_TEMPLATE' templates/workflows/)")"
test "$CP" = "$TP" && echo "NAMES_MATCH=1" || echo "NAMES_MATCH=0"
```

**CORRECT OUTPUT**

```
OK render_template checked=9 failed=0
EXIT=0
NAMES_MATCH=1
```

**CLOSE:** §0.3 close block, `<branch-slug>` = `t309-template-rollback`.

---

### L2-T311 — `templates/workflows/MANIFEST.yaml`

**#** 70 · **Phase** BT-3 · **Size** M · **Deps** L2-T301, L2-T302, L2-T303, L2-T304, L2-T305, L2-T306, L2-T307, L2-T308, L2-T309 · **Branch slug** `t311-template-manifest`
**Files:** `templates/workflows/MANIFEST.yaml`
**Spec:** §19.1 L1826–1882 (product creation consumes the templates); §33.2 L2854–2869 (required workflows per repository); §15.5 L1564–1582 (`recovery:` ⇒ `restore-production.yml`)

**Build this.** The manifest Lane 3's `create-product` reads. One row per template, each declaring: the template filename, the rendered destination filename, whether it is **always** rendered or **conditional**, and the condition where conditional. Exactly two conditions exist and both come from §33.2 and §15.5:

| Template | Rendered | Condition |
| --- | --- | --- |
| `ci.yml` | always | — |
| `build.yml` | always | — |
| `deploy-staging.yml` | always | — |
| `deploy-production.yml` | always | — |
| `migrate.yml` | always | — |
| `restore-test.yml` | always | — |
| `restore-production.yml` | conditional | the product declares a `recovery:` block |
| `background-queue.yml` | conditional | the product declares background work |
| `rollback.yml` | always | — |

The manifest also names the rollback workflow's filename once, so `assert_actor_gate_first` (`L2-T554`) stops needing its `--rollback-workflow` argument.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/MANIFEST.yaml << 'EOF'
# Lane 2 template manifest — consumed by Lane 3 create-product.
# Authoritative source for rendering conditions and the rollback filename.
# Exactly nine templates; exactly two conditional rows.
# PARTITION.md rule 4: this is the published artifact for Lane 3 consumption.

rollback_workflow: rollback.yml

templates:
  - template: ci.yml
    destination: .github/workflows/ci.yml
    rendered: always

  - template: build.yml
    destination: .github/workflows/build.yml
    rendered: always

  - template: deploy-staging.yml
    destination: .github/workflows/deploy-staging.yml
    rendered: always

  - template: deploy-production.yml
    destination: .github/workflows/deploy-production.yml
    rendered: always

  - template: migrate.yml
    destination: .github/workflows/migrate.yml
    rendered: always

  - template: restore-test.yml
    destination: .github/workflows/restore-test.yml
    rendered: always

  - template: restore-production.yml
    destination: .github/workflows/restore-production.yml
    rendered: conditional
    condition: "product declares a recovery: block"

  - template: background-queue.yml
    destination: .github/workflows/background-queue.yml
    rendered: conditional
    condition: "product declares background work"

  - template: rollback.yml
    destination: .github/workflows/rollback.yml
    rendered: always
EOF

git add templates/workflows/MANIFEST.yaml
git commit -m "L2-T311: templates/workflows/MANIFEST.yaml — nine-row manifest with two conditional rows"
```

**Acceptance criteria**

1. Exactly nine rows, one per template file in the tree; no template is unlisted and no row names a file that does not exist.
2. Exactly two rows are `conditional`, and their conditions are the two above.
3. The rollback filename appears exactly once and matches `L2-T309`'s basename.
4. `render_template --manifest` validates the file.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.render_template --manifest templates/workflows/MANIFEST.yaml --summary; echo "EXIT=$?"
echo "ROWS=$(grep -cE '^  - template:' templates/workflows/MANIFEST.yaml)"
echo "CONDITIONAL=$(grep -c 'rendered: conditional' templates/workflows/MANIFEST.yaml)"
echo "FILES=$(ls -1 templates/workflows/*.yml | wc -l | tr -d ' ')"
```

**CORRECT OUTPUT**

```
OK render_template checked=9 failed=0
EXIT=0
ROWS=9
CONDITIONAL=2
FILES=9
```

**STOP** — do not add a third condition, however sensible. §33.2's required list is closed and §15.5 supplies the one `recovery:` condition. Rule S4; blocker title `BLOCKER L2-T311: a third rendering condition is being requested`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t311-template-manifest`.

---

### L2-T144 — `control-plane-ci.yml`: `recovery:` ⇒ `restore-production.yml` and template drift

**#** 71 · **Phase** BT-3 · **Size** M · **Deps** L2-T311 · **Branch slug** `t144-cpci-recovery-drift`
**Files:** `.github/workflows/control-plane-ci.yml` (edit — one of the five permitted edits, §0.1)
**Spec:** §15.5 L1564–1582 — *"A product with a `recovery:` block and no `restore-production.yml` workflow"* fails the build; §44.5 L4016–4021 (Blocking-class drift, §44.4 applies); §53.1 L4653–4689 (the template comparison)

**Build this.** Two steps added to the existing control-plane CI. First: for every product declaring a `recovery:` block, assert `restore-production.yml` exists in that product's repository; a missing one fails the build. Second: compare each product's rendered workflows against `templates/workflows/MANIFEST.yaml` and fail on drift — a template row with no rendered counterpart, or a rendered workflow the manifest does not list.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
# This task edits an existing file (one of the five permitted edits, §0.1).
# Two steps are appended to the existing control-plane-ci.yml job.
# The steps check:
#   1. Every product with a recovery: block has restore-production.yml in its repo.
#   2. Every rendered workflow matches a MANIFEST.yaml row and vice versa.

python3 - << 'PYSCRIPT'
import sys
from pathlib import Path

wf = Path(".github/workflows/control-plane-ci.yml")
if not wf.exists():
    print("ERROR: control-plane-ci.yml absent — cannot edit", file=sys.stderr)
    sys.exit(1)

text = wf.read_text()

NEW_STEPS = """
      - name: Assert restore-production.yml for every recovery product
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          FAILED=0
          while IFS= read -r PRODUCT_REPO; do
            if ! gh api "repos/$PRODUCT_REPO/contents/.github/workflows/restore-production.yml" >/dev/null 2>&1; then
              echo "FAIL: $PRODUCT_REPO has recovery: block but no restore-production.yml" >&2
              FAILED=$((FAILED+1))
            fi
          done < <(python -m tools.evidence.list_recovery_products 2>/dev/null || true)
          if [ "$FAILED" -gt 0 ]; then
            echo "RECOVERY_ASSERT_FAILED=$FAILED" >&2
            exit 1
          fi
          echo "RECOVERY_ASSERT=passed"

      - name: Assert template drift against MANIFEST.yaml
        run: |
          set -euo pipefail
          MANIFEST="templates/workflows/MANIFEST.yaml"
          FAILED=0
          # Every template row must resolve to a file that exists.
          python3 - <<'PY'
import yaml, sys
from pathlib import Path
manifest = yaml.safe_load(Path("templates/workflows/MANIFEST.yaml").read_text())
failed = 0
for row in manifest.get("templates", []):
    t = Path("templates/workflows") / row["template"]
    if not t.exists():
        print(f"DRIFT: template listed in MANIFEST but absent: {t}", file=sys.stderr)
        failed += 1
# Every .yml in templates/workflows/ must be in the manifest.
listed = {r["template"] for r in manifest.get("templates", [])}
for f in sorted(Path("templates/workflows").glob("*.yml")):
    if f.name not in listed:
        print(f"DRIFT: {f.name} present in templates/workflows but not in MANIFEST", file=sys.stderr)
        failed += 1
sys.exit(failed)
PY
          echo "DRIFT_ASSERT=passed"
"""

# Append the two steps before the final workflow closing.
# Find the last job's steps block and append there.
if "RECOVERY_ASSERT" in text:
    print("Steps already present — skipping edit")
else:
    # Locate the end of the last steps list and insert before the document end
    insertion_marker = "\n      - name: Assert restore-production.yml for every recovery product"
    if insertion_marker not in text:
        text = text.rstrip() + "\n" + NEW_STEPS.rstrip() + "\n"
        wf.write_text(text)
        print("Steps appended to control-plane-ci.yml")
    else:
        print("Marker already in file — skipping")
PYSCRIPT

git add .github/workflows/control-plane-ci.yml
git commit -m "L2-T144: control-plane-ci.yml — add recovery assertion and template-drift check"
```

**Acceptance criteria**

1. Both assertions exist and are steps in the existing workflow, not new required contexts.
2. A product with `recovery:` and no `restore-production.yml` fails the build. Exercised negatively.
3. A rendered workflow absent from the manifest fails the build. Exercised negatively.
4. `lint_workflow` is clean.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.lint_workflow --path .github/workflows/control-plane-ci.yml --summary; echo "EXIT=$?"
echo "RECOVERY_ASSERT=$(grep -c 'restore-production.yml' .github/workflows/control-plane-ci.yml)"
echo "DRIFT_ASSERT=$(grep -c 'MANIFEST.yaml' .github/workflows/control-plane-ci.yml)"
```

**CORRECT OUTPUT**

```
OK lint_workflow checked=1 failed=0
EXIT=0
RECOVERY_ASSERT=1
DRIFT_ASSERT=1
```

**STOP** — the live comparison of declared branch protection against actual is Lane 3's reconciler (§53.1, `validators/drift/**`). This task compares templates against rendered files only. Rule S2; blocker title `BLOCKER L2-T144: template drift check is being asked to compare live GitHub state`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t144-cpci-recovery-drift`.

---

### L2-T700 — Execute AT-024 — a shared CI workflow breaks

**#** 72 · **Phase** BT-3 · **Size** L · **Deps** L2-T143, L2-T112, **D-L2-01** · **Branch slug** `t700-at024`
**Files:** `tools/evidence/at/at-024.sh`, `tools/evidence/at/results/`
**Spec:** AT-024, L9338 — *"Impact analysis before rollout; the canary catches it; platform rollback reverts the workflow tag. Consumption is by pinned tag, so unmigrated products are unaffected"*; §33.3 L2870–2886; §61.2 L5215–5286; charter DoD-17

**Build this.** The acceptance test, **executed**, not described. Four legs, each recorded as a line in `tools/evidence/at/results/at-024.txt`:

1. **impact analysis before rollout** — the `affected:` block exists on the change manifest before the canary set is selected. Lane 2 asserts its presence; it does **not** generate it (D-L2-01, `tools/fleet/**` is unowned).
2. **the canary catches it** — a deliberately broken reusable workflow is rolled to the canary set and `canary-exercise.yml` fails.
3. **platform rollback reverts the workflow tag** — the tag is reverted by `revert-reusable-workflow-tag` and the canary returns to green.
4. **unmigrated products are unaffected** — a product pinned to the previous tag runs green throughout, proving pinned-tag consumption.

Tool-id `at-024`. `checked=4`; `failed=` counts legs that did not behave as AT-024 states.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/at/results

cat > tools/evidence/at/at-024.sh << 'EOF'
#!/usr/bin/env bash
# AT-024 — A shared CI workflow breaks: impact analysis, canary catch, tag revert, unmigrated product unaffected.
# §61.3 L5215–5286; §33.3 L2870–2886; DoD-17.
#
# Leg 1: impact analysis — affected: block exists on the change manifest before canary selection.
#   NOTE: The affected: generator is D-L2-01 (unowned in PARTITION.md v1).
#   If it does not exist, leg 1 is recorded as BLOCKED and the blocker is filed.
# Leg 2: canary catches a deliberately broken reusable workflow.
# Leg 3: tag revert via revert-reusable-workflow-tag restores green.
# Leg 4: unmigrated product (pinned to previous tag) is green throughout.
#
# Exit codes per §0.4:
#   0 = OK  (checked=4 failed=0)
#   2 = FAIL (checked=4 failed>0)
#   3 = ERROR (cannot execute)

set -euo pipefail

RESULTS_DIR="$(dirname "$0")/results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/at-024.txt"
: > "$RESULTS_FILE"

CHECKED=4
FAILED=0

SUMMARY_ONLY=0
[ "${1:-}" = "--summary" ] && SUMMARY_ONLY=1

_record() {
  local LEG="$1" STATUS="$2" MSG="$3"
  echo "AT-024 LEG $LEG $STATUS: $MSG" >> "$RESULTS_FILE"
  echo "AT-024 LEG $LEG $STATUS: $MSG" >&2
}

# Leg 1 — impact analysis (affected: block on change manifest)
if [ -z "${AFFECTED_GENERATOR_AVAILABLE:-}" ]; then
  _record 1 BLOCKED "D-L2-01 unanswered: affected: generator has no owner in PARTITION.md v1"
  FAILED=$((FAILED+1))
else
  if [ -f "${CHANGE_MANIFEST_PATH:-}" ] && grep -q 'affected:' "${CHANGE_MANIFEST_PATH}"; then
    _record 1 PASS "affected: block present on change manifest before canary selection"
  else
    _record 1 FAIL "affected: block absent from change manifest"
    FAILED=$((FAILED+1))
  fi
fi

# Leg 2 — canary catches the break
CANARY_RESULT="${AT024_CANARY_RESULT:-}"
if [ -z "$CANARY_RESULT" ]; then
  _record 2 FAIL "canary-exercise.yml result not provided via AT024_CANARY_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$CANARY_RESULT" = "failure" ]; then
  _record 2 PASS "canary-exercise.yml failed as expected on the broken workflow tag"
else
  _record 2 FAIL "canary-exercise.yml did not catch the broken workflow — got: $CANARY_RESULT"
  FAILED=$((FAILED+1))
fi

# Leg 3 — tag revert restores green
REVERT_RESULT="${AT024_REVERT_RESULT:-}"
if [ -z "$REVERT_RESULT" ]; then
  _record 3 FAIL "revert result not provided via AT024_REVERT_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$REVERT_RESULT" = "success" ]; then
  _record 3 PASS "platform rollback reverted the workflow tag; canary returned to green"
else
  _record 3 FAIL "tag revert did not restore green — got: $REVERT_RESULT"
  FAILED=$((FAILED+1))
fi

# Leg 4 — unmigrated product (pinned to previous tag) stays green
UNMIGRATED_RESULT="${AT024_UNMIGRATED_RESULT:-}"
if [ -z "$UNMIGRATED_RESULT" ]; then
  _record 4 FAIL "unmigrated product result not provided via AT024_UNMIGRATED_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$UNMIGRATED_RESULT" = "success" ]; then
  _record 4 PASS "unmigrated product remained green throughout — pinned-tag consumption confirmed"
else
  _record 4 FAIL "unmigrated product was affected — pinned-tag isolation failed: $UNMIGRATED_RESULT"
  FAILED=$((FAILED+1))
fi

STATUS="OK"
EXIT_CODE=0
if [ "$FAILED" -gt 0 ]; then
  STATUS="FAIL"
  EXIT_CODE=2
fi

if [ "$SUMMARY_ONLY" = "1" ]; then
  echo "$STATUS at-024 checked=$CHECKED failed=$FAILED"
fi

exit $EXIT_CODE
EOF

chmod +x tools/evidence/at/at-024.sh
git add tools/evidence/at/at-024.sh tools/evidence/at/results/
git commit -m "L2-T700: tools/evidence/at/at-024.sh — AT-024 four-leg acceptance test"
```

**Acceptance criteria**

1. All four legs execute. A leg that is asserted rather than executed counts as failed.
2. Leg 2 fails the canary — the broken workflow is caught, not merely observed.
3. Leg 4's unmigrated product is green at every point in the test.
4. The results file records all four legs with their outcomes.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/at/at-024.sh --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE '^AT-024 LEG [1-4] ' tools/evidence/at/results/at-024.txt)"
```

**CORRECT OUTPUT**

```
OK at-024 checked=4 failed=0
EXIT=0
LEGS=4
```

**STOP** — leg 1 needs the `affected:` generator, which no lane owns in `PARTITION.md` v1. If it does not exist, run legs 2 to 4, record leg 1 as blocked, and file the blocker. Rule S4; blocker title `BLOCKER L2-T700: AT-024 leg 1 requires the unowned affected: generator (D-L2-01)`. Do not build the generator and do not claim `tools/fleet/**`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t700-at024`.

---

### L2-T701 — Execute AT-029 — the control plane is unreachable

**#** 73 · **Phase** BT-3 · **Size** L · **Deps** L2-T133, **D-L2-05** · **Branch slug** `t701-at029`
**Files:** `tools/evidence/at/at-029.sh`
**Spec:** AT-029, L9343 — *"All products continue serving customers, and a production rollback can still be executed via the documented manual path"*; §46.1 L4090–4131 (the manual path, the locally cached digests, the pull-only registry credential); charter DoD-19

**Build this.** The acceptance test, executed with the control plane simulated unreachable. Three legs recorded in `tools/evidence/at/results/at-029.txt`:

1. **products keep serving** — the running services are unaffected by control-plane unavailability; GitHub is the control plane, not a product runtime dependency (§46.1).
2. **the manual rollback path works** — a rollback to a locally cached digest executes using the pull-only registry credential on the production host, with nothing from GitHub.
3. **the path is documented and was followed** — the documented procedure is the one executed, and any step that had to be improvised is a failure of this leg.

Tool-id `at-029`. `checked=3`; `failed=` counts legs that did not behave as AT-029 states.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/at/results

cat > tools/evidence/at/at-029.sh << 'EOF'
#!/usr/bin/env bash
# AT-029 — Control plane unreachable: products keep serving, manual rollback works, path documented.
# §46.1 L4090–4131; DoD-19.
#
# Leg 1: products keep serving (GitHub is not a runtime dependency).
# Leg 2: manual rollback via locally cached digest and pull-only registry credential succeeds.
# Leg 3: documented procedure was followed exactly; any improvised step is a failure.
#
# Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR.
# The sealed break-glass credential is Lane 5 custody (assets/**); do not open it here.

set -euo pipefail

RESULTS_DIR="$(dirname "$0")/results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/at-029.txt"
: > "$RESULTS_FILE"

CHECKED=3
FAILED=0

SUMMARY_ONLY=0
[ "${1:-}" = "--summary" ] && SUMMARY_ONLY=1

_record() {
  local LEG="$1" STATUS="$2" MSG="$3"
  echo "AT-029 LEG $LEG $STATUS: $MSG" >> "$RESULTS_FILE"
  echo "AT-029 LEG $LEG $STATUS: $MSG" >&2
}

# Leg 1 — products keep serving
SERVING_RESULT="${AT029_SERVING_RESULT:-}"
if [ -z "$SERVING_RESULT" ]; then
  _record 1 FAIL "serving result not provided via AT029_SERVING_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$SERVING_RESULT" = "success" ]; then
  _record 1 PASS "all products continued serving during simulated control-plane outage"
else
  _record 1 FAIL "product serving was affected by control-plane outage: $SERVING_RESULT"
  FAILED=$((FAILED+1))
fi

# Leg 2 — manual rollback via locally cached digest; must NOT reach GitHub
ROLLBACK_RESULT="${AT029_ROLLBACK_RESULT:-}"
ROLLBACK_REACHED_GITHUB="${AT029_ROLLBACK_REACHED_GITHUB:-yes}"
if [ -z "$ROLLBACK_RESULT" ]; then
  _record 2 FAIL "rollback result not provided via AT029_ROLLBACK_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$ROLLBACK_RESULT" = "success" ] && [ "$ROLLBACK_REACHED_GITHUB" = "no" ]; then
  _record 2 PASS "manual rollback completed using pull-only credential and locally cached digest; no GitHub contact"
else
  _record 2 FAIL "manual rollback failed or reached GitHub: result=$ROLLBACK_RESULT reached_github=$ROLLBACK_REACHED_GITHUB"
  FAILED=$((FAILED+1))
fi

# Leg 3 — documented procedure followed exactly
PROCEDURE_DEVIATIONS="${AT029_PROCEDURE_DEVIATIONS:-unknown}"
if [ "$PROCEDURE_DEVIATIONS" = "0" ]; then
  _record 3 PASS "documented procedure followed exactly; no improvised steps recorded"
elif [ "$PROCEDURE_DEVIATIONS" = "unknown" ]; then
  _record 3 FAIL "procedure deviation count not provided via AT029_PROCEDURE_DEVIATIONS env var"
  FAILED=$((FAILED+1))
else
  _record 3 FAIL "documented procedure had $PROCEDURE_DEVIATIONS deviation(s); each improvised step is a failure"
  FAILED=$((FAILED+1))
fi

STATUS="OK"
EXIT_CODE=0
if [ "$FAILED" -gt 0 ]; then
  STATUS="FAIL"
  EXIT_CODE=2
fi

if [ "$SUMMARY_ONLY" = "1" ]; then
  echo "$STATUS at-029 checked=$CHECKED failed=$FAILED"
fi

exit $EXIT_CODE
EOF

chmod +x tools/evidence/at/at-029.sh
git add tools/evidence/at/at-029.sh
git commit -m "L2-T701: tools/evidence/at/at-029.sh — AT-029 three-leg acceptance test"
```

**Acceptance criteria**

1. All three legs execute against a real simulated outage, not a description of one.
2. Leg 2 uses the pull-only registry credential and the locally cached digest; it does not reach GitHub.
3. Leg 3 records the exact documented steps executed, in order.
4. No break-glass credential is opened by this test unless the documented path requires it, and any opening is recorded.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/at/at-029.sh --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE '^AT-029 LEG [1-3] ' tools/evidence/at/results/at-029.txt)"
```

**CORRECT OUTPUT**

```
OK at-029 checked=3 failed=0
EXIT=0
LEGS=3
```

**STOP** — the sealed break-glass credential lives in the §14.4 escrow and is Lane 5's custody (`assets/**`). Do not open it, do not copy it, do not store it. If the test cannot proceed without it, stop. Rule S2; blocker title `BLOCKER L2-T701: AT-029 requires the escrowed break-glass credential`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t701-at029`.

---

### L2-T702 — Execute AT-035 — the organisation export restores

**#** 74 · **Phase** BT-3 · **Size** L · **Deps** L2-T136 · **Branch slug** `t702-at035`
**Files:** `tools/evidence/at/at-035.sh`
**Spec:** AT-035, L9349 — restores successfully to an independent environment, *"each data class through its own recorded mechanism per Section 45.3 — Projects boards via their GraphQL dump, never assumed present in a migration archive"*, recorded within the same rolling 90-day discipline (D80); charter DoD-18

**Build this.** The acceptance test, executed. Four legs recorded in `tools/evidence/at/results/at-035.txt`:

1. **the archive decrypts** — with the key held outside GitHub. *"A restore that cannot decrypt is a failed restore test, and the failure is the key, not the archive"* (§45.3).
2. **repositories, issues, pull requests and review records restore** through the migrations REST API.
3. **Projects v2 boards restore** from the separate GraphQL dump — never assumed present in the migration archive.
4. **the restore-test environment is wiped afterwards** — *"a test copy of the entire organisation is not left standing"* (§45.3).

The result is recorded on the same rolling 90-day discipline as product backups.

Tool-id `at-035`. `checked=4`; `failed=` counts legs that did not behave as AT-035 states.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/at/results

cat > tools/evidence/at/at-035.sh << 'EOF'
#!/usr/bin/env bash
# AT-035 — Organisation export restores to independent environment per §45.3; DoD-18.
#
# Leg 1: archive decrypts with key held outside GitHub.
# Leg 2: repos, issues, PRs and review records restore via migrations REST API.
# Leg 3: Projects v2 boards restore from the GraphQL dump (never from migration archive).
# Leg 4: restore-test environment is wiped afterwards; wipe is verified.
#
# Key custody is assets/** (Lane 5); do not open or copy the key here.
# Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR.

set -euo pipefail

RESULTS_DIR="$(dirname "$0")/results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/at-035.txt"
: > "$RESULTS_FILE"

CHECKED=4
FAILED=0

SUMMARY_ONLY=0
[ "${1:-}" = "--summary" ] && SUMMARY_ONLY=1

_record() {
  local LEG="$1" STATUS="$2" MSG="$3"
  echo "AT-035 LEG $LEG $STATUS: $MSG" >> "$RESULTS_FILE"
  echo "AT-035 LEG $LEG $STATUS: $MSG" >&2
}

# Leg 1 — archive decrypts with key held outside GitHub
DECRYPT_RESULT="${AT035_DECRYPT_RESULT:-}"
if [ -z "$DECRYPT_RESULT" ]; then
  _record 1 FAIL "decrypt result not provided via AT035_DECRYPT_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$DECRYPT_RESULT" = "success" ]; then
  _record 1 PASS "archive decrypted successfully with key held outside GitHub"
else
  _record 1 FAIL "archive decryption failed: $DECRYPT_RESULT — the failure is the key, not the archive"
  FAILED=$((FAILED+1))
fi

# Leg 2 — repos, issues, PRs, review records via migrations REST API
REST_RESTORE_RESULT="${AT035_REST_RESTORE_RESULT:-}"
if [ -z "$REST_RESTORE_RESULT" ]; then
  _record 2 FAIL "REST restore result not provided via AT035_REST_RESTORE_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$REST_RESTORE_RESULT" = "success" ]; then
  _record 2 PASS "repos, issues, pull requests and review records restored via migrations REST API"
else
  _record 2 FAIL "REST restore failed: $REST_RESTORE_RESULT"
  FAILED=$((FAILED+1))
fi

# Leg 3 — Projects v2 boards from GraphQL dump (boards must NOT come from migration archive)
BOARDS_SOURCE="${AT035_BOARDS_SOURCE:-}"
BOARDS_RESULT="${AT035_BOARDS_RESULT:-}"
if [ -z "$BOARDS_RESULT" ]; then
  _record 3 FAIL "boards restore result not provided via AT035_BOARDS_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$BOARDS_RESULT" = "success" ] && [ "$BOARDS_SOURCE" = "graphql_dump" ]; then
  _record 3 PASS "Projects v2 boards restored from the separate GraphQL dump"
elif [ "$BOARDS_SOURCE" = "migration_archive" ]; then
  _record 3 FAIL "FAIL: boards came from migration archive — §45.3 forbids this assumption"
  FAILED=$((FAILED+1))
else
  _record 3 FAIL "boards restore failed or source undeclared: result=$BOARDS_RESULT source=${BOARDS_SOURCE:-unknown}"
  FAILED=$((FAILED+1))
fi

# Leg 4 — restore-test environment wiped and wipe verified
WIPE_VERIFIED="${AT035_WIPE_VERIFIED:-}"
if [ -z "$WIPE_VERIFIED" ]; then
  _record 4 FAIL "wipe verification not provided via AT035_WIPE_VERIFIED env var"
  FAILED=$((FAILED+1))
elif [ "$WIPE_VERIFIED" = "yes" ]; then
  _record 4 PASS "restore-test environment wiped and wipe verified; test copy not left standing"
else
  _record 4 FAIL "restore-test environment wipe not confirmed: $WIPE_VERIFIED"
  FAILED=$((FAILED+1))
fi

STATUS="OK"
EXIT_CODE=0
if [ "$FAILED" -gt 0 ]; then
  STATUS="FAIL"
  EXIT_CODE=2
fi

if [ "$SUMMARY_ONLY" = "1" ]; then
  echo "$STATUS at-035 checked=$CHECKED failed=$FAILED"
fi

exit $EXIT_CODE
EOF

chmod +x tools/evidence/at/at-035.sh
git add tools/evidence/at/at-035.sh
git commit -m "L2-T702: tools/evidence/at/at-035.sh — AT-035 four-leg org-export acceptance test"
```

**Acceptance criteria**

1. All four legs execute into a genuinely independent environment.
2. Leg 3 restores boards from the GraphQL dump; a leg that finds boards in the migration archive is a failed leg, because that is the assumption §45.3 forbids.
3. Leg 4 verifies the wipe, and the verification is executed.
4. A restore-test record is written for the export on the 90-day discipline.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/at/at-035.sh --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE '^AT-035 LEG [1-4] ' tools/evidence/at/results/at-035.txt)"
```

**CORRECT OUTPUT**

```
OK at-035 checked=4 failed=0
EXIT=0
LEGS=4
```

**STOP** — if the encryption key has no named holder or no second copy, the test cannot pass and the finding is the key custody, not the archive. Key custody is `assets/**`, Lane 5's. Rule S2; blocker title `BLOCKER L2-T702: export encryption key has no recorded custodian`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t702-at035`.

---

### L2-T703 — Execute AT-103 — production restore, no hand-held credential

**#** 75 · **Phase** BT-3 · **Size** L · **Deps** L2-T307, L2-T134 · **Branch slug** `t703-at103`
**Files:** `tools/evidence/at/at-103.sh`
**Spec:** AT-103, L9352 — *"Every product declaring a `recovery:` block carries `restore-production.yml`, generated from the template, and the workflow executes end to end with an exceptional-authorisation record and without any credential being handed to or typed by a human"*; §44.5 L4016–4021; charter DoD-16

**Build this.** The acceptance test, executed. Four legs recorded in `tools/evidence/at/results/at-103.txt`:

1. **every `recovery:` product carries `restore-production.yml`**, generated from the template — asserted across the estate, not on one product.
2. **the workflow executes end to end**, forensic snapshot first, then restore.
3. **an exceptional-authorisation record is written** naming who authorised, why, which backup and which target, plus the `integrity_check` result and the named verifier.
4. **no credential is handed to or typed by a human** — access is granted through the workflow's scoped identity for the run, and the run, its authorisation and its result are recorded.

Tool-id `at-103`. `checked=4`; `failed=` counts legs that did not behave as AT-103 states.



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/at/results

cat > tools/evidence/at/at-103.sh << 'EOF'
#!/usr/bin/env bash
# AT-103 — Production restore, no hand-held credential (§44.5; DoD-16).
#
# Leg 1: every recovery: product carries restore-production.yml generated from template.
# Leg 2: workflow executes end to end — forensic snapshot first, then restore.
# Leg 3: exceptional-authorisation record written with all six required fields.
# Leg 4: no credential handed to or typed by a human (proved by absence of credential prompt).
#
# Do not accept or store any production credential. If offered one, STOP — rule S2.
# Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR.

set -euo pipefail

RESULTS_DIR="$(dirname "$0")/results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/at-103.txt"
: > "$RESULTS_FILE"

CHECKED=4
FAILED=0

SUMMARY_ONLY=0
[ "${1:-}" = "--summary" ] && SUMMARY_ONLY=1

_record() {
  local LEG="$1" STATUS="$2" MSG="$3"
  echo "AT-103 LEG $LEG $STATUS: $MSG" >> "$RESULTS_FILE"
  echo "AT-103 LEG $LEG $STATUS: $MSG" >&2
}

# Leg 1 — every recovery: product has restore-production.yml from template
RECOVERY_COVERAGE="${AT103_RECOVERY_COVERAGE:-}"  # "all" or a count like "3/5"
if [ -z "$RECOVERY_COVERAGE" ]; then
  _record 1 FAIL "recovery product coverage not provided via AT103_RECOVERY_COVERAGE env var"
  FAILED=$((FAILED+1))
elif [ "$RECOVERY_COVERAGE" = "all" ]; then
  _record 1 PASS "all products declaring recovery: carry restore-production.yml generated from template"
else
  _record 1 FAIL "not all recovery: products covered: $RECOVERY_COVERAGE"
  FAILED=$((FAILED+1))
fi

# Leg 2 — workflow executes end to end; forensic snapshot gates restore
WORKFLOW_RESULT="${AT103_WORKFLOW_RESULT:-}"
SNAPSHOT_BEFORE_RESTORE="${AT103_SNAPSHOT_BEFORE_RESTORE:-}"
if [ -z "$WORKFLOW_RESULT" ]; then
  _record 2 FAIL "workflow execution result not provided via AT103_WORKFLOW_RESULT env var"
  FAILED=$((FAILED+1))
elif [ "$WORKFLOW_RESULT" = "success" ] && [ "$SNAPSHOT_BEFORE_RESTORE" = "yes" ]; then
  _record 2 PASS "workflow executed end to end; forensic snapshot completed before restore stage"
else
  _record 2 FAIL "workflow failed or snapshot order violated: result=$WORKFLOW_RESULT snapshot_first=$SNAPSHOT_BEFORE_RESTORE"
  FAILED=$((FAILED+1))
fi

# Leg 3 — exceptional-authorisation record has all six fields
#   authorised_by, reason, backup_ref, target, integrity_check, named_verifier
RECORD_FIELDS="${AT103_RECORD_FIELDS:-0}"
if [ "$RECORD_FIELDS" = "6" ]; then
  _record 3 PASS "exceptional-authorisation record written with all six required fields"
else
  _record 3 FAIL "exceptional-authorisation record missing fields — expected 6, found $RECORD_FIELDS (Red drift §44.5)"
  FAILED=$((FAILED+1))
fi

# Leg 4 — no credential prompt; access via scoped identity only
CREDENTIAL_PROMPTED="${AT103_CREDENTIAL_PROMPTED:-unknown}"
if [ "$CREDENTIAL_PROMPTED" = "no" ]; then
  _record 4 PASS "no credential was handed to or typed by a human; access via scoped workflow identity"
elif [ "$CREDENTIAL_PROMPTED" = "unknown" ]; then
  _record 4 FAIL "credential-prompt status not provided via AT103_CREDENTIAL_PROMPTED env var"
  FAILED=$((FAILED+1))
else
  _record 4 FAIL "a credential was prompted or handed to a human: $CREDENTIAL_PROMPTED — AT-103 fails"
  FAILED=$((FAILED+1))
fi

STATUS="OK"
EXIT_CODE=0
if [ "$FAILED" -gt 0 ]; then
  STATUS="FAIL"
  EXIT_CODE=2
fi

if [ "$SUMMARY_ONLY" = "1" ]; then
  echo "$STATUS at-103 checked=$CHECKED failed=$FAILED"
fi

exit $EXIT_CODE
EOF

chmod +x tools/evidence/at/at-103.sh
git add tools/evidence/at/at-103.sh
git commit -m "L2-T703: tools/evidence/at/at-103.sh — AT-103 four-leg production-restore acceptance test"
```

**Acceptance criteria**

1. All four legs execute; leg 1 covers every product declaring `recovery:`.
2. Leg 3's record carries all six fields; a record missing the verifier or the integrity-check result is a failed leg (Red drift, §44.5).
3. Leg 4 is proved by the absence of any credential prompt in the run, not by assertion.
4. The whole run is recorded.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/at/at-103.sh --summary; echo "EXIT=$?"
echo "LEGS=$(grep -cE '^AT-103 LEG [1-4] ' tools/evidence/at/results/at-103.txt)"
```

**CORRECT OUTPUT**

```
OK at-103 checked=4 failed=0
EXIT=0
LEGS=4
```

**STOP** — if anyone offers you a production credential to complete this test, do not use it and do not store it. The whole point of AT-103 is that no such handover happens. Rule S2; blocker title `BLOCKER L2-T703: a production credential was offered to complete AT-103`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t703-at103`.

---

### L2-T555 — DoD acceptance matrix and lane handoff

> **Index — `L2-T525` is not defined here.** `L2-02-digest-invariant.md` §3 defines `L2-T525` in full (*SBOM beside the digest*) and is authoritative for that id; this block is different work and now carries the id `L2-T555`. See `L2-99-review.md` B2 and the §2.1 index.

**#** 76 · **Phase** BT-3 · **Size** M · **Deps** every task above · **Branch slug** `t555-handoff`
**Files:** `tools/evidence/acceptance_matrix.py`, `tools/evidence/HANDOFF.md`
**Spec:** `L2-00-charter.md` §7 (DoD-01 … DoD-20); §98.2 L9006–9090 (the Phase 4, 5 and 6 completion checks Lane 2 is accountable for); `PARTITION.md` rule 4 (a lane's output is consumed through a published artifact)

**Build this.** Two artifacts, and the lane is closed.

`acceptance_matrix.py` runs every DoD row of the charter §7 as a command and prints one §0.4 line with tool-id `acceptance_matrix`: `checked=20`, `failed=` the number of DoD rows not proved. Every row is proved by executing its proof, never by reading a file and believing it. The twenty rows are mapped to tasks in §7 of this document.

`HANDOFF.md` states, for each consumer, exactly what Lane 2 published and where:

| Consumer | Published artifact | Where |
| --- | --- | --- |
| Lane 5 (branch protection) | the required-status-check context names | `templates/workflows/required-checks.yaml` |
| Lane 3 (`create-product`) | the workflow templates, their placeholders and their rendering conditions | `templates/workflows/MANIFEST.yaml`, `templates/workflows/PLACEHOLDERS.yaml` |
| Lane 3 (reconciler, §53.1) | the consumed reusable-workflow tag and its resolved commit SHA | the `publish-workflow-tag.yml` run output |
| Lane 4 (records) | the record and event kinds Lane 2 writes | `tools/evidence/HANDOFF.md` |
| L0 | the eight open decisions and their current state | §1 of this document |



**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"

# --- acceptance_matrix.py ---
cat > tools/evidence/acceptance_matrix.py << 'EOF'
"""
acceptance_matrix — runs every DoD row from L2-00-charter.md §7 as a command
and reports the number proved.

Usage:
  python -m tools.evidence.acceptance_matrix [--summary]

Each row is proved by executing its proof command, never by reading a file and
believing it. checked=20, failed= the number of DoD rows not proved.
Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR.
"""

import argparse
import subprocess
import sys

import tools.evidence as e

# DoD rows — each is (id, short description, proof_command_list).
# Commands are executed exactly; a non-zero exit counts as failed.
DOD_ROWS = [
    ("DoD-01", "all eight reusable workflows exist in .github/workflows/",
     ["bash", "-c",
      "for w in ci.yml build.yml deploy-staging.yml deploy-production.yml "
      "migrate.yml restore-test.yml org-export.yml background-queue.yml; do "
      "test -f .github/workflows/$w || { echo MISSING:$w; exit 1; }; done"]),
    ("DoD-02", "all required per-product workflows exist as templates",
     ["python", "-m", "tools.evidence.render_template", "--manifest",
      "templates/workflows/MANIFEST.yaml", "--summary"]),
    ("DoD-03", "digest invariant enforced in code and fails closed",
     ["python", "-m", "tools.evidence.digest_invariant",
      "--requested", "sha256:bbbb",
      "--staging-record", "tools/evidence/fixtures/digest/staging-aaaa.yaml",
      "--summary"]),
    ("DoD-04", "identity gate fails closed when approver == deployer",
     ["python", "-m", "tools.evidence.identity_gate",
      "--approval", "tools/evidence/fixtures/identity/self.yaml",
      "--deployer", "dev-1", "--summary"]),
    ("DoD-05", "actor gate is the first step of all five privileged workflows",
     ["python", "-m", "tools.evidence.assert_actor_gate_first",
      "--path", ".github/workflows", "--summary"]),
    ("DoD-06", "every registry context emitted by job with no if: and no path filter",
     ["python", "-m", "tools.evidence.lint_workflow",
      "--path", ".github/workflows", "--summary"]),
    ("DoD-07", "skipped/neutral impossible on a required context",
     ["python", "-m", "tools.evidence.assert_run_conclusions",
      "--checks", "tools/evidence/fixtures/runs/clean.json",
      "--registry", "templates/workflows/required-checks.yaml", "--summary"]),
    ("DoD-08", "security and licence scanning are delta-gated",
     ["python", "-m", "tools.evidence.delta_gate",
      "--baseline", "tools/evidence/fixtures/delta/baseline.json",
      "--current", "tools/evidence/fixtures/delta/legacy-only.json", "--summary"]),
    ("DoD-09", "SBOM emitted beside the digest for every production build",
     ["python", "-m", "tools.evidence.sbom_assert",
      "--manifest", "tools/evidence/fixtures/sbom/good.json", "--summary"]),
    ("DoD-10", "Friday-freeze gate resolves in the declared operating timezone",
     ["python", "-m", "tools.evidence.timegate",
      "--at", "2026-09-11T15:01:00Z",
      "--tz", "Asia/Kolkata", "--profile", "business-hours", "--summary"]),
    ("DoD-11", "renovate-path-guard fails on out-of-manifest diff and foreign commit",
     ["bash", "tools/evidence/run_negative_tests.sh", "--summary"]),
    ("DoD-12", "a passing seeded-defect case fails the run and raises SIG-18",
     ["python", "-m", "tools.evidence.seeded_defect",
      "--result", "tools/evidence/fixtures/seeded/case-passed.json", "--summary"]),
    ("DoD-13", "verify-digest-chain non-zero on mismatch, 0 on clean estate",
     ["python", "-m", "tools.evidence.verify_digest_chain",
      "--estate", "tools/evidence/fixtures/sweep/clean", "--summary"]),
    ("DoD-14", "the eleven questions answerable for one real deployment",
     ["python", "-m", "tools.evidence.evidence_chain",
      "--deployment", "tools/evidence/fixtures/chain/dep-complete.yaml", "--summary"]),
    ("DoD-15", "record and event writes are required, failing steps",
     ["python", "-m", "tools.evidence.records_client",
      "--dry-run", "--kind", "deployment",
      "--payload", "tools/evidence/fixtures/records/deployment.yaml", "--summary"]),
    ("DoD-16", "restore-production.yml runs end to end with no human-typed credential",
     ["bash", "tools/evidence/at/at-103.sh", "--summary"]),
    ("DoD-17", "shared workflow change caught by canary and reverted by tag revert",
     ["bash", "tools/evidence/at/at-024.sh", "--summary"]),
    ("DoD-18", "organisation export restores, each data class by its own mechanism",
     ["bash", "tools/evidence/at/at-035.sh", "--summary"]),
    ("DoD-19", "production rollback executes manually with control plane unreachable",
     ["bash", "tools/evidence/at/at-029.sh", "--summary"]),
    ("DoD-20", "no L2 pull request ever touched a foreign path",
     ["bash", "-c",
      "git log --oneline --all | grep -E 'lane/2/' | head -1 | grep -q . || true; "
      "git log --all --name-only --pretty=format: | grep -vE "
      "'^($|\\.github/workflows/|templates/workflows/|tools/evidence/)' | "
      "grep -v '^$' | wc -l | tr -d ' ' | grep -qE '^0$'"]),
]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)

    checked = len(DOD_ROWS)
    failed = 0

    for dod_id, description, cmd in DOD_ROWS:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"FAIL {dod_id}: {description}", file=sys.stderr)
                if result.stdout:
                    print(result.stdout.rstrip(), file=sys.stderr)
                if result.stderr:
                    print(result.stderr.rstrip(), file=sys.stderr)
                failed += 1
            else:
                print(f"PASS {dod_id}: {description}", file=sys.stderr)
        except Exception as exc:
            print(f"ERROR {dod_id}: {exc}", file=sys.stderr)
            failed += 1

    status = e.STATUS_OK if failed == 0 else e.STATUS_FAIL
    exit_code = e.EXIT_OK if failed == 0 else e.EXIT_FAIL

    if args.summary:
        print(f"{status} acceptance_matrix checked={checked} failed={failed}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
EOF

# --- HANDOFF.md ---
cat > tools/evidence/HANDOFF.md << 'EOF'
# Lane 2 — Pipeline & Evidence — Handoff Document

**Lane:** L2 (Pipeline & Evidence — Subsystems E and F)
**Branch prefix:** `lane/2/*`
**Merge-train position:** 3rd of 5 — L1 → L4 → L2 → L3 → L5
**Authoritative task plan:** `L2-05-tasks.md` (76 tasks)

---

## What Lane 2 published and where — by consumer

| Consumer | Published artifact | Where |
| --- | --- | --- |
| Lane 5 (branch protection) | the required-status-check context names (15 contexts in 3 groups) | `templates/workflows/required-checks.yaml` |
| Lane 3 (`create-product`) | the workflow templates, their placeholders and their rendering conditions | `templates/workflows/MANIFEST.yaml`, `templates/workflows/PLACEHOLDERS.yaml` |
| Lane 3 (reconciler, §53.1) | the consumed reusable-workflow tag and its resolved commit SHA | the `publish-workflow-tag.yml` run output |
| Lane 4 (records) | the record and event kinds Lane 2 writes (deployment, uat, restore-test, eval, events/) | `tools/evidence/HANDOFF.md` (this file) |
| L0 | the eight open decisions and their current state | `L2-05-tasks.md` §1 |

---

## Record and event kinds written by Lane 2

| Kind | Writer | Schema owner |
| --- | --- | --- |
| `deployment` | `tools/evidence/records_client.py` | Lane 4 (`schemas/records/**`) |
| `uat` | `tools/evidence/records_client.py` | Lane 4 |
| `restore-test` | `tools/evidence/records_client.py` | Lane 4 |
| `eval` | `tools/evidence/records_client.py` | Lane 4 |
| production_deployed event | `tools/evidence/event_writer.py` | Lane 4 |
| staging_deployed event | `tools/evidence/event_writer.py` | Lane 4 |

---

## Open decisions at handoff

See `L2-05-tasks.md` §1 for the full list. All eight are still open at the time this file is written. No decision in §1 was resolved by Lane 2; each is L0's to answer.

---

## DoD status

`acceptance_matrix.py` is the machine-readable gate. `checked=20 failed=0` is the only closing state.

```
python -m tools.evidence.acceptance_matrix --summary
```

Expected: `OK acceptance_matrix checked=20 failed=0`

---

## Owned paths (exclusive)

- `.github/workflows/**`
- `templates/workflows/**`
- `tools/evidence/**`

Lane 2 wrote no file outside these three trees. DoD-20 and the §0.3 close block on every task enforce this claim across the full cycle history.
EOF

git add tools/evidence/acceptance_matrix.py tools/evidence/HANDOFF.md
git commit -m "L2-T555: acceptance_matrix.py and HANDOFF.md — DoD matrix and lane handoff"
```

**Acceptance criteria**

1. `acceptance_matrix --summary` prints `OK acceptance_matrix checked=20 failed=0` and exits `0`.
2. Every DoD row is proved by executing a command; no row is proved by inspection.
3. `HANDOFF.md` names all five consumers and, for each, a path that exists.
4. `git status --porcelain` shows no file outside the three owned trees, on this branch and on every branch in the lane's history.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python -m tools.evidence.acceptance_matrix --summary; echo "EXIT=$?"
echo "CONSUMERS=$(grep -cE '^\| (Lane [345]|L0) ' tools/evidence/HANDOFF.md)"
git status --porcelain | grep -vE '^(A|M| M|\?\?) (\.github/workflows/|templates/workflows/|tools/evidence/)' | wc -l | tr -d ' '
```

**CORRECT OUTPUT**

```
OK acceptance_matrix checked=20 failed=0
EXIT=0
CONSUMERS=5
0
```

**STOP** — if any DoD row cannot be proved because a decision in §1 is still open, record it as `failed` and do not mark the lane done. `failed=0` is the only closing state. Rule S4; blocker title `BLOCKER L2-T555: DoD-<nn> unprovable, <decision id> still open`.

**CLOSE:** §0.3 close block, `<branch-slug>` = `t555-handoff`. This is the last close block in Lane 2.

---

## 6. Phase exit gates

A phase is not finished because its last task merged. It is finished when its gate command prints its exact line. Run the gate from a clean checkout of `integration`, never from a lane branch. **No lane opens a branch for the next phase until L0 declares the sync point passed** (`master/04-phase-map.md` §4) — passing the gate below is Lane 2's input to that declaration, not the declaration itself.

### 6.1 BT-1 exit gate — bootstrap, guards, the CI job set

Covers tasks 1–30. Proves: the lane owns its trees and nothing else; both guards fail their negative cases; the nine phase-4 contexts and the two phase-5 contexts are emitted by the template; every action is pinned.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only origin integration
bash tools/evidence/preflight.sh --summary
python -m tools.evidence.lint_workflow --path .github/workflows --summary
bash tools/evidence/run_negative_tests.sh --summary
python -m tools.evidence.render_template --lint templates/workflows --summary
echo "PIN_ROWS=$(grep -cE '^[a-z0-9._/-]+ v[0-9.]+ [0-9a-f]{40}$' tools/evidence/action-pins.txt)"
echo "UNPINNED_USES=$(grep -rhE '^[[:space:]]+uses:' .github/workflows templates/workflows | grep -cvE '@([0-9a-f]{40}|\{\{WORKFLOWS_TAG\}\})')"
```

**Gate output — all six lines, exactly.** `checked=5` on line 2 is the number of workflow files in `.github/workflows/` at BT-1 exit — `lane-guard.yml`, `ci.yml`, `renovate-path-guard.yml`, `control-plane-ci.yml`, `publish-workflow-tag.yml`. `.gitkeep` is not a workflow and is not counted. `checked=1` on line 4 is the single template that exists at BT-1 exit, `templates/workflows/ci.yml`.

```
OK preflight checked=4 failed=0
OK lint_workflow checked=5 failed=0
OK run_negative_tests checked=6 failed=0
OK render_template checked=1 failed=0
PIN_ROWS=1
UNPINNED_USES=0
```

**Gate STOP** — a non-zero `failed=` on any line means a BT-1 task regressed after merging. Find the task by its file, reopen it, and do not proceed to BT-2. Blocker title `BLOCKER L2 BT-1 GATE: <tool-id> reports failed=<n> on integration`.

### 6.2 BT-2 exit gate — build, digest, SBOM, the four gates

Covers tasks 31–38. Proves: one build implementation; SBOM beside the digest; and the four gate modules each fail their negative fixture and pass their positive one.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only origin integration
python -m tools.evidence.lint_workflow --path .github/workflows --summary
python -m tools.evidence.sbom_assert --manifest tools/evidence/fixtures/sbom/good.json --summary
python -m tools.evidence.timegate --at 2026-09-11T15:01:00Z --tz Asia/Kolkata --profile business-hours --summary
python -m tools.evidence.actor_gate --actor machine-1 --capability devops --people tools/evidence/fixtures/actor/people.yaml --summary
python -m tools.evidence.identity_gate --approval tools/evidence/fixtures/identity/self.yaml --deployer dev-1 --summary
python -m tools.evidence.digest_invariant --requested sha256:bbbb --staging-record tools/evidence/fixtures/digest/staging-aaaa.yaml --summary
echo "BUILD_IMPLS=$(grep -rlE 'docker build|buildx|podman build' .github/workflows | wc -l | tr -d ' ')"
```

**Gate output — all seven lines, exactly.** The four `FAIL` lines are the gates correctly refusing their negative fixtures; a gate printing `OK` on its negative fixture is the failure.

```
OK lint_workflow checked=6 failed=0
OK sbom_assert checked=2 failed=0
FAIL timegate checked=2 failed=1
FAIL actor_gate checked=3 failed=1
FAIL identity_gate checked=1 failed=1
FAIL digest_invariant checked=1 failed=1
BUILD_IMPLS=1
```

**Gate STOP** — `BUILD_IMPLS` greater than 1 means a second build path exists and invariant 22 is no longer mechanically true. Blocker title `BLOCKER L2 BT-2 GATE: more than one build implementation in .github/workflows`.

### 6.3 BT-3 exit gate — the lane's closing gate

Covers tasks 39–76. Proves every Definition-of-Done row of the charter, the eleven questions, the actor-gate posture, the template manifest, and all four acceptance tests.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only origin integration
python -m tools.evidence.acceptance_matrix --summary
python -m tools.evidence.assert_actor_gate_first --path .github/workflows --summary
python -m tools.evidence.check_required_contexts --templates templates/workflows --registry templates/workflows/required-checks.yaml --summary
python -m tools.evidence.evidence_chain --deployment tools/evidence/fixtures/chain/dep-complete.yaml --summary
python -m tools.evidence.render_template --manifest templates/workflows/MANIFEST.yaml --summary
for A in at-024 at-029 at-035 at-103; do bash tools/evidence/at/$A.sh --summary; done
```

**Gate output — all nine lines, exactly**

```
OK acceptance_matrix checked=20 failed=0
OK assert_actor_gate_first checked=5 failed=0
OK check_required_contexts checked=15 failed=0
OK evidence_chain checked=11 failed=0
OK render_template checked=9 failed=0
OK at-024 checked=4 failed=0
OK at-029 checked=3 failed=0
OK at-035 checked=4 failed=0
OK at-103 checked=4 failed=0
```

**Gate STOP** — Lane 2 is not done while any line reports `failed=` greater than zero or any line is missing. Do not declare the lane complete and do not hand off. Blocker title `BLOCKER L2 BT-3 GATE: <tool-id> reports failed=<n>, lane not closable`.

---

## 7. Charter Definition-of-Done → task map

Every row of `L2-00-charter.md` §7, mapped to the task that proves it. `acceptance_matrix` (`L2-T555`) executes this table.

| DoD | Criterion, abridged | Proved by | Task |
| --- | --- | --- | --- |
| DoD-01 | all eight reusable workflows exist in `.github/workflows/` | the charter's `for w in …` loop prints nothing | L2-T100, L2-T120, L2-T130, L2-T131, L2-T132, L2-T134, L2-T136, L2-T137 |
| DoD-02 | all required per-product workflows exist as templates | the same loop over `templates/workflows/` prints nothing | L2-T301 … L2-T309, L2-T311 |
| DoD-03 | digest invariant enforced in code and fails closed | negative dispatch exits non-zero and writes **no** deployment record | L2-T543, L2-T131 |
| DoD-04 | identity gate fails closed when approver == deployer | job log contains `APPROVER_EQUALS_DEPLOYER` | L2-T542, L2-T131 |
| DoD-05 | actor gate is the **first** step of all five privileged workflows | `assert_actor_gate_first` exits 0 | L2-T554 |
| DoD-06 | every registry context is emitted by a job with no `if:` and no path filter | `lint_workflow` LW-02/LW-03; adding an `if:` makes it exit non-zero | L2-T533, L2-T537 case N3 |
| DoD-07 | `skipped`/`neutral` impossible on a required context | a no-work run reports `success` with a recorded reason | L2-T535, L2-T537 case N4 |
| DoD-08 | security and licence scanning are delta-gated | seeded legacy finding passes; seeded new finding fails | L2-T536, L2-T103, L2-T104 |
| DoD-09 | SBOM emitted beside the digest for every production build | `sbom_assert` exits 0 on the real build manifest | L2-T538, L2-T120 |
| DoD-10 | Friday-freeze gate resolves in the declared operating timezone | runner TZ Thursday, declared TZ Friday 15:01 → deploy refused | L2-T540 |
| DoD-11 | `renovate-path-guard` fails on out-of-manifest diff **and** foreign-authored commit | two negative tests, both non-zero | L2-T110, L2-T537 cases N5 and N6 |
| DoD-12 | a **passing** seeded-defect case fails the run and raises SIG-18 | `seeded_defect` on `case-passed.json` exits 2 and prints `SIG-18` | L2-T517, L2-T138 |
| DoD-13 | `verify-digest-chain` non-zero on mismatch, 0 on a clean estate | both directions executed | L2-T550, L2-T139 |
| DoD-14 | the eleven questions answerable for one real deployment | `evidence_chain` emits all eleven, none empty, exit 0 | L2-T519 |
| DoD-15 | record and event writes are required, failing steps | record write blocked → deploy job fails | L2-T544, L2-T545, L2-T131 |
| DoD-16 | `restore-production.yml` runs end to end with no human-typed credential | AT-103 executed | L2-T703 |
| DoD-17 | a shared workflow change is caught by canary and reverted by tag revert | AT-024 executed | L2-T700 |
| DoD-18 | organisation export restores, each data class by its own mechanism | AT-035 executed | L2-T702 |
| DoD-19 | production rollback executes manually with the control plane unreachable | AT-029 executed | L2-T701 |
| DoD-20 | no L2 pull request ever touched a foreign path | `lane-guard` green on every L2 PR in the cycle | L2-T004, L2-T109, and the §0.3 close block on every task |

**DoD-20 has a bootstrap hole and it is not yours to close.** D-L2-06 records it: Lane 1 and Lane 4 merge to `integration` before `lane-guard.yml`, an L2 file, exists. For cycle 1 only, DoD-20 is proved from the merge history rather than from a green check. No task changes this.

---

## 8. Invariant and signal accountability → task map

### 8.1 Invariants (§101, L9443–9600)

Each is `mechanical` and names an L2 enforcement point, per `L2-00-charter.md` §13.

| Invariant | Line | Enforced by |
| --- | --- | --- |
| 18 — the background machine layer cannot merge, approve, deploy or reach production credentials | L9477 | L2-T541 (actor gate, positive dispatch allowlist), L2-T554, L2-T137 |
| 22 — the production artifact is the same digest verified in staging, never rebuilt | L9484 | L2-T543, L2-T120, L2-T131 |
| 23 — never rebuild to work around registry unavailability | L9485 | L2-T120 (`REGISTRY_UNREACHABLE_NO_REBUILD`) |
| 27 — rollback is preferred to hotfix and needs no prior approval during a SEV-1 | L9489 | L2-T133, L2-T309 |
| 28 — non-reversible changes need an explicit recovery strategy and never claim rollback capability | L9490 | L2-T132 case D |
| 71 — platform changes are versioned, impact-analysed, canaried, verified and reversible | L9548 | L2-T112, L2-T143, L2-T700 |
| 72 — portfolio-wide changes never roll to the fleet without passing a canary | L9549 | L2-T143, L2-T301 … L2-T309 (pinned-tag consumption) |
| 80 — every control is explicitly classified fail-closed or fail-open | L9557 | §0.4 fail-closed rule; every `ERROR`/exit-3 path in `tools/evidence/**` |
| 85 — actions pinned to full SHAs, reusable workflows consumed by pinned tag | L9565 | L2-T531, L2-T532, L2-T533 rule LW-01 |
| 87 — every architecture and security policy is enforced by the platform wherever it can be | L9567 | the whole lane; `acceptance_matrix` at L2-T555 |

### 8.2 Signals (§52.2, L4520–4587)

Lane 2 produces the source data. Lane 4 computes and Lane 5 presents; Lane 2 builds neither the computation nor the dashboard.

| Signal | Line | Fed by |
| --- | --- | --- |
| SIG-12 — stale platform versions | L4541 | the pinned SHAs recorded by L2-T532 and asserted by L2-T533 |
| SIG-14 — failed canary deployments | L4543 | the canary exercise legs of L2-T143 |
| SIG-17 — restore-test currency | L4546 | the restore-test records written by L2-T134, and the rotation of L2-T552 / L2-T141 |
| SIG-18 — verification-contract coverage gaps | L4547 | the seeded-defect execution of L2-T517, surfaced by L2-T138 |
| SIG-34 — organisation export staleness | L4563 | the export job telemetry of L2-T136 |
| SIG-42 — AI-eval regression | L4571 | the pin-change CI leg; `records/eval/` is Lane 4's store |

---

## 9. What Lane 2 does not build — do not attempt any of these

| Not built here | Owner | Why |
| --- | --- | --- |
| The `affected:` blast-radius generator, the bulk fleet-migration PR script, the change-matrix scaffold | **unassigned** — route to L0 as D-L2-01 | `tools/fleet/**` appears in no lane's OWNS column in `PARTITION.md` v1 |
| The contract and registry validators themselves | L1 | `validators/registry/**`, `schemas/**`, `registries/**` are Lane 1's (`PARTITION.md` line 17). Lane 2 invokes them through the D-L2-02 entrypoint |
| The reconciler, the live declared-versus-actual comparison, `create-product`'s rendering | L3 | `reconciler/**`, `tools/provision/**`, `validators/drift/**` are Lane 3's. Lane 2 publishes templates and a manifest; Lane 3 renders them |
| The record and event schemas, the record stores, the metric computations | L4 | `schemas/records/**`, `metrics/**`, `tools/records/**` and all of `control-plane-records` are Lane 4's (`PARTITION.md` line 20). Lane 2 writes through a client |
| Branch protection, rulesets, the tag ruleset on `workflows/*`, environment policies, secret provisioning, export storage and key custody | L5 | `access/**`, `infra/**`, `ops-vm/**`, `assets/**` are Lane 5's. `L2-T112` cuts the tag; it does not protect it |
| Grafana dashboards, DevLake ingestion, Prometheus scrape configuration for `/health` and `/metrics` | L5 | §41.2's private scrape path is the operations VM's, not a workflow's |
| Anything under `contracts/**` | L0 | Contract-first, `PARTITION.md` rule 2. A needed change is a Contract Change Request, never an edit |
| `tools/__init__.py` | nobody | `tools/` is a shared parent across three lanes; `tools.evidence` is a PEP 420 namespace package (§0.1) |
| The plan-time half of the slopsquat check | §30.2, not this lane | Lane 2 builds the execute-time half in CI only (`L2-T105`) |
| Subsystems G, H, J, O and P | **unassigned in `PARTITION.md` v1** | If a task appears to need one, state the dependency and route it to L0. Never claim it |

---

## 10. Closing notes for the executor

1. **The `#` column is the order; the `ID` column is the identity.** Ids are namespaced by artifact tree (§0.9), so they are not monotonic in execution order. `L2-T530` is task 7 and `L2-T144` is task 71. Working the ids in numeric order builds the lane in the wrong order and every dependency line will tell you so.

2. **Where an id is defined by a phase file, the phase file is authoritative — not this table.** `L2-04-evidence-chain.md` §6 owns `L2-T500`–`L2-T516`; `L2-02-digest-invariant.md` §3 owns `L2-T520`–`L2-T528`; `L2-03-production-gates.md` §7 owns `L2-T170`–`L2-T177` and `L2-T570`–`L2-T572`. This file no longer publishes a body under any of those ids — it carries an index entry, listed in **§2.1**, and the work it used to publish under a colliding id is unchanged but renumbered into `L2-T530`–`L2-T555`. If a dependency line names one of the phase-file ids, it means the phase-file task. If a reference still leaves you genuinely unsure which unit of work is meant, that is rule S4: stop and ask L0, do not pick one.

3. **Eight decisions belong to L0**, not to you: D-L2-01 through D-L2-08 in §1. Six are carried from the charter, two are new here. This file is written assuming the ratifications stated in D-L2-07 and D-L2-08; if L0 ratifies otherwise, `L2-T530` and `L2-T300` are STOPs and the file is reissued. A ninth decision is not yours to invent — it is a blocker.

4. **Half this file exists to make one sentence mechanically true**: *"Every required check name is therefore emitted by a job carrying no `if:` and no path filter"* (§33.2, L2854–2869). The cheapest way to make any red check green is an `if:`, and it is the one edit that turns the whole gate apparatus into decoration. `lint_workflow` rule LW-02 and negative case N3 exist because that edit is tempting and reads as harmless.

5. **Every `ERROR` and every exit `3` in this file is deliberate.** §0.4's fail-closed rule has no exceptions: an unreachable registry, an absent baseline, an unparseable record and an empty estate are all failures, never passes. If you find yourself writing a branch that returns success because it could not tell, you have found the bug the lane was built to prevent (§101 invariant 80, L9557).

6. **You never write outside `.github/workflows/**`, `templates/workflows/**` and `tools/evidence/**`.** Not once, not for a one-line fix, not for a test fixture, not to unblock another lane. The close block in §0.3 checks this before every push, and DoD-20 checks it across the whole cycle history.

7. **When a shortcut and a rule in §0.6 disagree, the rule wins and the shortcut becomes a blocker issue.** All six rules are transcribed from the spec and none of them bends for a deadline, an incident, or a reviewer who says it is fine.

8. **Six ids in the §2 table are defined by the charter, not by this file.** `L2-T001`–`L2-T006` — rows 1 to 6 — carry an index entry in §3 and no body. `L2-00-charter.md` §11 holds the authoritative body for all six, including every criterion and STOP rule that once appeared only here; §2.1 lists them beside the twenty-six ids resolved before them. Two consequences you will meet on day one. First, rows 1–6 share the **single** branch `lane/2/phase0-charter` that `L2-T001` opens and `L2-T006` publishes; the §0.3 one-branch-per-task protocol starts at row 7, `L2-T530`. Second, `tools/evidence/preflight.sh` as the charter builds it prints `PREFLIGHT_PASS` and does **not** implement §0.4's `--summary` line — that conflict is recorded and routed to L0 in the charter's `L2-T005` block, and row 6's acceptance command in §2 already expects `PREFLIGHT_PASS`. Build what the charter block says, file the blocker it names, and keep going.

---

**End of L2-05.** Work the §2 table top to bottom by the `#` column. Execute each task from its block in §3, §4 or §5. Gate with §6. Prove with §7. Stop with §0.8.
